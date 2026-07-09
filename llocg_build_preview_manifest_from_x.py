#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build official_preview_image_manifest.json from official X card-introduction posts.

Matching contract:
  product code + card name + rarity -> cardnumber

The normalized card DB does not store rarity as a row field. For MEMBER cards,
booster numbering commonly separates the rare/parallel base block from the N
block. This tool intentionally uses only the conservative cases below:
  * one DB candidate for the card name -> match
  * rarity N with 2+ candidates -> highest numeric suffix (late/N block)
  * rare-family rarity with exactly 2 candidates -> lowest numeric suffix
  * rare-family rarity with 3+ candidates -> AMBIGUOUS; require override

This specifically avoids guessing expansions where the same character has two
R-base cards. Ambiguities are written to audit output and are not added to the
preview manifest.

Input modes:
  1) Official X API user timeline (recommended for automatic collection)
     Requires X_BEARER_TOKEN or --x-bearer-token.
  2) Tweet IDs via the public embed/syndication JSON endpoint (manual/probe mode).
  3) Existing tweet-result JSON files (offline/reproducible debug mode).

BUILD_TAG is intentionally visible for delivery verification.
"""

from __future__ import annotations

BUILD_TAG = "x_preview_manifest_db_reverse_match_20260709a"

import argparse
import csv
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_USERNAME = "LL_cardgame"
DEFAULT_KEYWORD = "カード紹介"
KNOWN_RARITIES = (
    "SEC2", "SECE", "SECL", "PR2", "PE2", "P2", "R2", "L2",
    "SRL", "DUO", "LLE", "SEC", "SD", "CL", "PR", "AR", "RM",
    "RE", "PE", "N", "R", "L", "P",
)
RARITY_SUFFIXES = set(KNOWN_RARITIES)
RARE_MEMBER_FAMILY = {
    "R", "R2", "P", "P2", "SEC", "SEC2", "SECL", "SRL", "DUO",
    "AR", "RM", "RE", "PE", "PE2", "SECE", "LLE",
}

SYNDICATION_FEATURES = (
    "tfw_timeline_list:;tfw_follower_count_sunset:true;"
    "tfw_tweet_edit_backend:on;tfw_refsrc_session:on;"
    "tfw_fosnr_soft_interventions_enabled:on;"
    "tfw_show_birdwatch_pivots_enabled:on;"
    "tfw_show_business_verified_badge:on;"
    "tfw_duplicate_scribes_to_settings:on;"
    "tfw_use_profile_image_shape_enabled:on;"
    "tfw_show_blue_verified_badge:on;"
    "tfw_legacy_timeline_sunset:true;"
    "tfw_show_gov_verified_badge:on;"
    "tfw_show_business_affiliate_badge:on;"
    "tfw_tweet_edit_frontend:on"
)


@dataclass(frozen=True)
class CardRow:
    cardnumber: str
    cardname: str
    card_type: str
    number: Optional[int]


@dataclass(frozen=True)
class TweetRecord:
    tweet_id: str
    text: str
    media_urls: Tuple[str, ...]
    created_at: str
    post_url: str
    source: str


@dataclass
class MatchAudit:
    tweet_id: str
    post_url: str
    source: str
    created_at: str
    product_code: str
    keyword_present: bool
    rarity: str
    matched_cardname: str
    cardname_matches: str
    candidate_cardnumbers: str
    selected_cardnumber: str
    media_count: int
    status: str
    reason: str
    text: str


def _http_json(url: str, *, headers: Optional[Dict[str, str]] = None, timeout: float = 30.0) -> Any:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {url}\n{body[:1000]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"network error: {url}: {exc}") from exc


def _canonical_cardnumber(value: str) -> str:
    cardno = str(value or "").strip()
    m = re.match(r"^(.*)-([A-Za-z0-9]+)$", cardno)
    if m and m.group(2).upper() in RARITY_SUFFIXES:
        base = m.group(1)
        if re.search(r"-(?:bp|pb|sd)\d+-\d+$", base, flags=re.IGNORECASE) or re.search(
            r"-PR-\d+$", base, flags=re.IGNORECASE
        ):
            return base
    return cardno


def _product_pattern(product_code: str) -> re.Pattern[str]:
    code = product_code.strip().upper()
    m = re.fullmatch(r"BP0*(\d+)", code)
    if m:
        return re.compile(rf"-bp{int(m.group(1))}-", re.IGNORECASE)
    m = re.fullmatch(r"(?:[A-Z]+)?SD0*(\d+)", code)
    if m:
        return re.compile(rf"-sd{int(m.group(1))}-", re.IGNORECASE)
    m = re.fullmatch(r"(?:[A-Z]+)?PB0*(\d+)", code)
    if m:
        return re.compile(rf"-pb{int(m.group(1))}-", re.IGNORECASE)
    raise ValueError(f"unsupported product code: {product_code!r}")


def load_db(path: Path, product_code: str) -> List[CardRow]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, list):
        raise ValueError(f"expected list JSON: {path}")
    pat = _product_pattern(product_code)
    out: List[CardRow] = []
    seen: set[Tuple[str, str]] = set()
    for raw in obj:
        if not isinstance(raw, dict):
            continue
        cardno = _canonical_cardnumber(str(raw.get("cardnumber", "")))
        cardname = str(raw.get("cardname", "") or "").strip()
        if not cardno or not cardname or not pat.search(cardno):
            continue
        key = (cardno, cardname)
        if key in seen:
            continue
        seen.add(key)
        m = re.search(r"-(\d+)$", cardno)
        out.append(
            CardRow(
                cardnumber=cardno,
                cardname=cardname,
                card_type=str(raw.get("card_type_norm", "") or raw.get("card_type", "")).upper(),
                number=int(m.group(1)) if m else None,
            )
        )
    return out


def _extract_rarity(text: str) -> str:
    # Card-introduction posts normally use full-width angle brackets, e.g. ＜N＞.
    rarity_alt = "|".join(re.escape(x) for x in KNOWN_RARITIES)
    patterns = [
        rf"[＜<]\s*({rarity_alt})\s*[＞>]",
        rf"[【\[]\s*({rarity_alt})\s*[】\]]",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).upper()
    return ""


def _cardname_matches(text: str, rows: Sequence[CardRow]) -> List[str]:
    names = sorted({row.cardname for row in rows if row.cardname}, key=lambda x: (-len(x), x))
    hits = [name for name in names if name in text]
    # If a longer exact DB card name contains shorter DB names, keep only the
    # longest composite name. This handles names such as A＆B＆C.
    kept: List[str] = []
    for name in hits:
        if any(name != longer and name in longer for longer in kept):
            continue
        kept.append(name)
    return kept


def load_overrides(path: Optional[Path]) -> Dict[str, Any]:
    if path is None or not path.exists():
        return {}
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"override JSON must be an object: {path}")
    return obj


def _override_cardnumber(
    overrides: Dict[str, Any], *, tweet_id: str, product_code: str, cardname: str, rarity: str
) -> Tuple[str, str]:
    tweets = overrides.get("tweets", {})
    if isinstance(tweets, dict):
        value = tweets.get(tweet_id)
        if isinstance(value, str) and value.strip():
            return _canonical_cardnumber(value), "OVERRIDE_TWEET"

    products = overrides.get("products", {})
    if isinstance(products, dict):
        product = products.get(product_code.upper(), {})
        if isinstance(product, dict):
            card = product.get(cardname, {})
            if isinstance(card, dict):
                value = card.get(rarity.upper())
                if isinstance(value, str) and value.strip():
                    return _canonical_cardnumber(value), "OVERRIDE_PRODUCT_CARD_RARITY"
    return "", ""


def resolve_cardnumber(
    *,
    tweet_id: str,
    cardname: str,
    rarity: str,
    product_code: str,
    rows: Sequence[CardRow],
    overrides: Dict[str, Any],
) -> Tuple[str, str, List[str], str]:
    candidates = [row for row in rows if row.cardname == cardname]
    candidate_numbers = sorted({row.cardnumber for row in candidates})

    override, override_status = _override_cardnumber(
        overrides,
        tweet_id=tweet_id,
        product_code=product_code,
        cardname=cardname,
        rarity=rarity,
    )
    if override:
        if override not in {row.cardnumber for row in rows}:
            return "", "BAD_OVERRIDE", candidate_numbers, f"override cardnumber not in product DB: {override}"
        return override, override_status, candidate_numbers, "override resolved"

    if not candidates:
        return "", "NO_DB_CANDIDATE", [], "no DB row for product + cardname"

    if len(candidate_numbers) == 1:
        return candidate_numbers[0], "MATCHED_SINGLE", candidate_numbers, "single DB candidate"

    numbered = sorted(
        (row for row in candidates if row.number is not None),
        key=lambda row: (int(row.number or -1), row.cardnumber),
    )
    if len({row.number for row in numbered}) != len(candidate_numbers):
        return "", "AMBIGUOUS_CANDIDATES", candidate_numbers, "candidate suffix numbers are not uniquely sortable"

    if rarity == "N":
        selected = numbered[-1].cardnumber
        return selected, "MATCHED_N_LATE_BLOCK", candidate_numbers, "N rarity -> highest suffix candidate"

    if rarity in RARE_MEMBER_FAMILY:
        member_candidates = [row for row in numbered if row.card_type == "MEMBER"]
        if len(candidate_numbers) == 2 and len(member_candidates) == 2:
            selected = numbered[0].cardnumber
            return selected, "MATCHED_R_EARLY_BLOCK", candidate_numbers, "rare-family rarity + two MEMBER candidates -> lowest suffix candidate"
        if len(candidate_numbers) >= 3:
            return "", "AMBIGUOUS_R_DUPLICATE", candidate_numbers, "3+ same-name candidates; possible two-R expansion; override required"

    return "", "AMBIGUOUS_CANDIDATES", candidate_numbers, f"cannot infer rarity={rarity} among {len(candidate_numbers)} candidates"


def _syndication_token(tweet_id: str) -> str:
    # Mirrors the token computation used by X embed clients closely enough for
    # the tweet-result endpoint. Python float intentionally matches JS Number's
    # binary64 arithmetic here.
    value = (int(tweet_id) / 1e15) * math.pi
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    integer = int(value)
    fraction = value - integer
    encoded = "0" if integer == 0 else ""
    while integer:
        integer, rem = divmod(integer, 36)
        encoded = digits[rem] + encoded
    encoded += "."
    for _ in range(20):
        fraction *= 36
        n = int(fraction)
        encoded += digits[n]
        fraction -= n
    return encoded.replace(".", "").replace("0", "")


def _media_urls_from_syndication(obj: Any) -> List[str]:
    urls: List[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
        elif isinstance(value, str) and "pbs.twimg.com/media/" in value:
            urls.append(value.replace("\\/", "/"))

    walk(obj)
    return list(dict.fromkeys(urls))


def tweet_from_syndication_json(obj: Dict[str, Any], *, username: str, source: str) -> TweetRecord:
    tweet_id = str(obj.get("id_str", "") or obj.get("id", "")).strip()
    text = str(obj.get("text", "") or "")
    return TweetRecord(
        tweet_id=tweet_id,
        text=text,
        media_urls=tuple(_media_urls_from_syndication(obj)),
        created_at=str(obj.get("created_at", "") or ""),
        post_url=f"https://x.com/{username}/status/{tweet_id}" if tweet_id else "",
        source=source,
    )


def fetch_syndication_tweet(tweet_id: str, *, username: str, timeout: float) -> TweetRecord:
    query = urllib.parse.urlencode(
        {
            "id": tweet_id,
            "lang": "ja",
            "features": SYNDICATION_FEATURES,
            "token": _syndication_token(tweet_id),
        }
    )
    url = "https://cdn.syndication.twimg.com/tweet-result?" + query
    obj = _http_json(url, timeout=timeout)
    if not isinstance(obj, dict):
        raise RuntimeError(f"unexpected syndication response for {tweet_id}")
    return tweet_from_syndication_json(obj, username=username, source="x_syndication")


def fetch_x_api_timeline(
    *, bearer_token: str, username: str, max_pages: int, timeout: float
) -> List[TweetRecord]:
    headers = {"Authorization": f"Bearer {bearer_token}"}
    user_url = "https://api.x.com/2/users/by/username/" + urllib.parse.quote(username)
    user_obj = _http_json(user_url, headers=headers, timeout=timeout)
    try:
        user_id = str(user_obj["data"]["id"])
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"X API user lookup did not return data.id: {user_obj}") from exc

    out: List[TweetRecord] = []
    pagination_token = ""
    for _page in range(max_pages):
        params = {
            "max_results": "100",
            "exclude": "retweets,replies",
            "tweet.fields": "created_at,attachments",
            "expansions": "attachments.media_keys",
            "media.fields": "type,url,preview_image_url,alt_text",
        }
        if pagination_token:
            params["pagination_token"] = pagination_token
        url = f"https://api.x.com/2/users/{user_id}/tweets?" + urllib.parse.urlencode(params)
        obj = _http_json(url, headers=headers, timeout=timeout)
        if not isinstance(obj, dict):
            raise RuntimeError("unexpected X API timeline response")

        media_by_key: Dict[str, Dict[str, Any]] = {}
        includes = obj.get("includes", {})
        if isinstance(includes, dict):
            for media in includes.get("media", []) or []:
                if isinstance(media, dict) and media.get("media_key"):
                    media_by_key[str(media["media_key"])] = media

        for tweet in obj.get("data", []) or []:
            if not isinstance(tweet, dict):
                continue
            urls: List[str] = []
            attachments = tweet.get("attachments", {})
            keys = attachments.get("media_keys", []) if isinstance(attachments, dict) else []
            for key in keys or []:
                media = media_by_key.get(str(key), {})
                if str(media.get("type", "")) != "photo":
                    continue
                url_value = str(media.get("url", "") or media.get("preview_image_url", "")).strip()
                if url_value:
                    urls.append(url_value)
            tweet_id = str(tweet.get("id", ""))
            out.append(
                TweetRecord(
                    tweet_id=tweet_id,
                    text=str(tweet.get("text", "") or ""),
                    media_urls=tuple(dict.fromkeys(urls)),
                    created_at=str(tweet.get("created_at", "") or ""),
                    post_url=f"https://x.com/{username}/status/{tweet_id}",
                    source="x_api_timeline",
                )
            )

        meta = obj.get("meta", {})
        pagination_token = str(meta.get("next_token", "")) if isinstance(meta, dict) else ""
        if not pagination_token:
            break
    return out


def load_tweet_ids(args: argparse.Namespace) -> List[str]:
    ids: List[str] = []
    for value in args.tweet_id or []:
        value = value.strip()
        if value:
            ids.append(value)
    if args.tweet_id_file:
        for line in args.tweet_id_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.search(r"status/(\d+)", line)
            ids.append(m.group(1) if m else line)
    return list(dict.fromkeys(ids))


def collect_tweets(args: argparse.Namespace) -> List[TweetRecord]:
    tweets: List[TweetRecord] = []

    if args.tweet_json_dir:
        for path in sorted(args.tweet_json_dir.glob("*.json")):
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                tweets.append(tweet_from_syndication_json(obj, username=args.x_username, source=f"tweet_json:{path.name}"))

    for path in args.tweet_json or []:
        obj = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(obj, dict):
            tweets.append(tweet_from_syndication_json(obj, username=args.x_username, source=f"tweet_json:{path.name}"))

    for tweet_id in load_tweet_ids(args):
        tweets.append(fetch_syndication_tweet(tweet_id, username=args.x_username, timeout=args.timeout))

    bearer = args.x_bearer_token or os.environ.get("X_BEARER_TOKEN", "")
    if args.x_api_timeline:
        if not bearer:
            raise SystemExit("ERROR: --x-api-timeline requires --x-bearer-token or X_BEARER_TOKEN")
        tweets.extend(
            fetch_x_api_timeline(
                bearer_token=bearer,
                username=args.x_username,
                max_pages=args.max_pages,
                timeout=args.timeout,
            )
        )

    dedup: Dict[str, TweetRecord] = {}
    for tweet in tweets:
        key = tweet.tweet_id or tweet.post_url or (tweet.text + "\n" + "\n".join(tweet.media_urls))
        dedup[key] = tweet
    return list(dedup.values())


def load_manifest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"cards": {}}
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"manifest must be object JSON: {path}")
    cards = obj.get("cards")
    if not isinstance(cards, dict):
        obj["cards"] = {}
    return obj


def add_manifest_entry(manifest: Dict[str, Any], cardnumber: str, entry: Dict[str, Any]) -> bool:
    cards = manifest.setdefault("cards", {})
    entries = cards.setdefault(cardnumber, [])
    if not isinstance(entries, list):
        entries = []
        cards[cardnumber] = entries
    signature = (
        str(entry.get("image_url", "")),
        str(entry.get("post_url", "")),
        str(entry.get("rarity_norm", "")),
    )
    for old in entries:
        if not isinstance(old, dict):
            continue
        old_signature = (
            str(old.get("image_url", "")),
            str(old.get("post_url", "")),
            str(old.get("rarity_norm", "")),
        )
        if old_signature == signature:
            return False
    entries.append(entry)
    return True


def process_tweets(
    *,
    tweets: Sequence[TweetRecord],
    rows: Sequence[CardRow],
    product_code: str,
    keyword: str,
    overrides: Dict[str, Any],
    manifest: Dict[str, Any],
) -> Tuple[List[MatchAudit], int]:
    audits: List[MatchAudit] = []
    added = 0
    for tweet in tweets:
        keyword_present = keyword in tweet.text
        rarity = _extract_rarity(tweet.text)
        names = _cardname_matches(tweet.text, rows)
        cardname = names[0] if len(names) == 1 else ""
        candidates: List[str] = []
        selected = ""
        status = ""
        reason = ""

        if not keyword_present:
            status, reason = "SKIP_KEYWORD", f"keyword not found: {keyword}"
        elif not tweet.media_urls:
            status, reason = "NO_MEDIA", "no pbs.twimg.com photo media URL"
        elif len(tweet.media_urls) != 1:
            status, reason = "AMBIGUOUS_MEDIA", f"expected one photo; got {len(tweet.media_urls)}"
        elif not rarity:
            status, reason = "NO_RARITY", "known rarity token not found in angle brackets"
        elif not names:
            status, reason = "NO_CARDNAME", "no product DB cardname found in post text"
        elif len(names) > 1:
            status, reason = "AMBIGUOUS_CARDNAME", "multiple non-substring DB cardnames found in post text"
        else:
            selected, status, candidates, reason = resolve_cardnumber(
                tweet_id=tweet.tweet_id,
                cardname=cardname,
                rarity=rarity,
                product_code=product_code,
                rows=rows,
                overrides=overrides,
            )
            if selected:
                entry = {
                    "folder": product_code.upper(),
                    "rarity_norm": rarity,
                    "image_url": tweet.media_urls[0],
                    "source": "official_x",
                    "post_url": tweet.post_url,
                    "tweet_id": tweet.tweet_id,
                    "posted_at": tweet.created_at,
                    "cardname_from_post": cardname,
                    "match_status": status,
                }
                if add_manifest_entry(manifest, selected, entry):
                    added += 1

        audits.append(
            MatchAudit(
                tweet_id=tweet.tweet_id,
                post_url=tweet.post_url,
                source=tweet.source,
                created_at=tweet.created_at,
                product_code=product_code.upper(),
                keyword_present=keyword_present,
                rarity=rarity,
                matched_cardname=cardname,
                cardname_matches=" | ".join(names),
                candidate_cardnumbers=" | ".join(candidates),
                selected_cardnumber=selected,
                media_count=len(tweet.media_urls),
                status=status,
                reason=reason,
                text=tweet.text.replace("\r", " ").replace("\n", " "),
            )
        )
    return audits, added


def write_audit(audits: Sequence[MatchAudit], tsv_path: Path, json_path: Path) -> None:
    tsv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(MatchAudit.__dataclass_fields__)
    with tsv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for row in audits:
            writer.writerow(asdict(row))
    json_path.write_text(
        json.dumps([asdict(row) for row in audits], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Build Loveca preview image manifest from official X posts")
    ap.add_argument("--root", type=Path, default=Path("./llocg_db_out_full"))
    ap.add_argument("--db", type=Path, default=None, help="Default: <root>/cards_min_tokv1.json")
    ap.add_argument("--manifest", type=Path, default=None, help="Default: <root>/official_preview_image_manifest.json")
    ap.add_argument("--product-code", required=True, help="e.g. BP07")
    ap.add_argument("--keyword", default=DEFAULT_KEYWORD)
    ap.add_argument("--override-json", type=Path, default=None, help="Optional ambiguity override JSON")
    ap.add_argument("--audit-tsv", type=Path, default=None)
    ap.add_argument("--audit-json", type=Path, default=None)
    ap.add_argument("--x-username", default=DEFAULT_USERNAME)
    ap.add_argument("--x-api-timeline", action="store_true", help="Collect official account timeline via X API")
    ap.add_argument("--x-bearer-token", default="", help="Prefer X_BEARER_TOKEN env var instead of CLI")
    ap.add_argument("--max-pages", type=int, default=10)
    ap.add_argument("--tweet-id", action="append", default=[])
    ap.add_argument("--tweet-id-file", type=Path, default=None)
    ap.add_argument("--tweet-json", action="append", type=Path, default=[])
    ap.add_argument("--tweet-json-dir", type=Path, default=None)
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--dry-run", action="store_true", help="Write audit only; do not write manifest")
    ap.add_argument("--strict", action="store_true", help="Exit 2 if a keyword-matching image post is not matched")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    db_path = args.db.resolve() if args.db else root / "cards_min_tokv1.json"
    manifest_path = args.manifest.resolve() if args.manifest else root / "official_preview_image_manifest.json"
    audit_tsv = args.audit_tsv.resolve() if args.audit_tsv else root / "preview_x_match_audit.tsv"
    audit_json = args.audit_json.resolve() if args.audit_json else root / "preview_x_match_audit.json"

    rows = load_db(db_path, args.product_code)
    if not rows:
        raise SystemExit(f"ERROR: no DB rows for product {args.product_code}: {db_path}")
    overrides = load_overrides(args.override_json)
    tweets = collect_tweets(args)
    if not tweets:
        raise SystemExit("ERROR: no tweet input; use --x-api-timeline, --tweet-id, --tweet-id-file, or --tweet-json-dir")

    manifest = load_manifest(manifest_path)
    audits, added = process_tweets(
        tweets=tweets,
        rows=rows,
        product_code=args.product_code,
        keyword=args.keyword,
        overrides=overrides,
        manifest=manifest,
    )
    write_audit(audits, audit_tsv, audit_json)

    if not args.dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts: Dict[str, int] = {}
    for row in audits:
        counts[row.status] = counts.get(row.status, 0) + 1
    print(f"BUILD_TAG={BUILD_TAG}")
    print(f"product={args.product_code.upper()} db_rows={len(rows)} tweets={len(tweets)} manifest_added={added}")
    for status, count in sorted(counts.items()):
        print(f"{status}: {count}")
    print(f"audit_tsv={audit_tsv}")
    print(f"audit_json={audit_json}")
    if args.dry_run:
        print("manifest=DRY_RUN")
    else:
        print(f"manifest={manifest_path}")

    bad_statuses = {
        "NO_MEDIA", "AMBIGUOUS_MEDIA", "NO_RARITY", "NO_CARDNAME",
        "AMBIGUOUS_CARDNAME", "NO_DB_CANDIDATE", "BAD_OVERRIDE",
        "AMBIGUOUS_R_DUPLICATE", "AMBIGUOUS_CANDIDATES",
    }
    unresolved = [row for row in audits if row.keyword_present and row.status in bad_statuses]
    if args.strict and unresolved:
        print(f"[STRICT] unresolved={len(unresolved)}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
