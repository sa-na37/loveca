#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Loveca prerelease preview-image manifest from the WIKIWIKI aggregate
"公式ポスト" page and public X syndication JSON.

Normal operation deliberately avoids:
  * paid X API / Bearer Token
  * per-card WIKIWIKI page requests
  * WIKIWIKI ::cmd/source requests

The WIKIWIKI aggregate page directly associates cardnumber(+rarity) rows with
X post links.  One aggregate-page request is cached, then only uncached X post
JSON is fetched.  Prerelease product filtering is driven by
product_release_registry.json.

BUILD_TAG is intentionally visible for delivery verification.
"""
from __future__ import annotations

BUILD_TAG = "preview_only_non_energy_official_post_cards_20260803a"

import argparse
import csv
import json
import math
import random
import re
import sys
import time
import urllib.parse
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import requests
from bs4 import BeautifulSoup, Tag

DEFAULT_USERNAME = "LL_cardgame"
DEFAULT_KEYWORD = "カード紹介"
OFFICIAL_POSTS_PAGE_URL = "https://wikiwiki.jp/llocardgame/%E5%85%AC%E5%BC%8F%E3%83%9D%E3%82%B9%E3%83%88"
PRODUCT_RELEASE_REGISTRY_FILENAME = "product_release_registry.json"
TWEET_CACHE_FILENAME = "preview_x_post_cache.json"
OFFICIAL_POSTS_CACHE_FILENAME = "preview_wiki_official_posts_index_cache.json"
PREVIEW_MANIFEST_FILENAME = "official_preview_image_manifest.json"
AUDIT_TSV_FILENAME = "preview_x_match_audit.tsv"
AUDIT_JSON_FILENAME = "preview_x_match_audit.json"

PB_PREFIX_TO_PRODUCT = {
    "PL!HS": "PBHS",
    "PL!SP": "PBSP",
    "PL!S": "PBLS",
    "PL!LS": "PBLS",
    "PL!N": "PBnj",
    "PL!": "PBLL",
    "LL": "PBLL",
}
SD_PREFIX_TO_PRODUCT = {
    "PL!SP": "SPSD01",
    "PL!N": "NSD01",
    "PL!HS": "HSSD01",
    "PL!LS": "LSSD01",
    "PL!S": "SSD01",
    "PL!": "PLSD01",
}
CL_PREFIX_TO_PRODUCT = {"PL!HS": "CLHS01"}

RARITY_ALIAS = {
    "R+": "R2",
    "L+": "L2",
    "P+": "P2",
    "PE+": "PE2",
    "SEC+": "SEC2",
    "PR+": "PR2",
}
KNOWN_RARITY_TOKENS = (
    "SEC+", "SEC2", "SECE", "SECL", "PR+", "PR2", "PE+", "PE2",
    "P+", "P2", "R+", "R2", "L+", "L2", "SRL", "DUO", "LLE",
    "SEC", "SD", "CL", "PR", "AR", "RM", "RE", "PE", "PP",
    "N", "R", "L", "P",
)
KNOWN_RARITIES = tuple(dict.fromkeys(RARITY_ALIAS.get(x, x) for x in KNOWN_RARITY_TOKENS))
RARITY_SUFFIXES = set(KNOWN_RARITIES)
RAW_RARITY_SUFFIXES = set(KNOWN_RARITY_TOKENS)

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
class ProductInfo:
    product_code: str
    release_date: str
    title: str
    source_url: str


@dataclass(frozen=True)
class TweetRecord:
    tweet_id: str
    text: str
    media_urls: Tuple[str, ...]
    created_at: str
    post_url: str
    source: str


@dataclass(frozen=True)
class OfficialPostIndexEntry:
    cardnumber: str
    rarity_raw: str
    rarity_norm: str
    tweet_id: str
    post_url: str
    row_text: str


@dataclass
class MatchAudit:
    tweet_id: str
    post_url: str
    source: str
    created_at: str
    product_code: str
    candidate_products: str
    keyword_present: bool
    product_text_present: bool
    rarity: str
    matched_cardname: str
    cardname_matches: str
    candidate_cardnumbers: str
    selected_cardnumber: str
    media_count: int
    status: str
    reason: str
    text: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json_object(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return obj if isinstance(obj, dict) else {}


def canonical_cardnumber(value: str) -> Tuple[str, str]:
    cardno = str(value or "").strip()
    m = re.match(r"^(.*)-([A-Za-z0-9+]+)$", cardno)
    if not m:
        return cardno, ""
    raw = m.group(2).upper()
    normalized = RARITY_ALIAS.get(raw, raw)
    if raw not in RAW_RARITY_SUFFIXES and normalized not in RARITY_SUFFIXES:
        return cardno, ""
    base = m.group(1)
    if (
        re.search(r"-(?:bp|pb|sd|cl)\d+-(?:\d+|E\d+)$", base, flags=re.IGNORECASE)
        or re.search(r"-PR-\d+$", base, flags=re.IGNORECASE)
    ):
        return base, normalized
    return cardno, ""


def card_prefix(cardno: str) -> str:
    return str(cardno or "").split("-", 1)[0]


def product_code_for_cardnumber(cardno: str) -> str:
    canonical, _rarity = canonical_cardnumber(cardno)
    c = canonical

    m = re.search(r"(?:^|-)bp([1-9][0-9]*)(?:-|$)", c, flags=re.IGNORECASE)
    if m:
        return f"BP{int(m.group(1)):02d}"

    m = re.search(r"(?:^|-)pb([1-9][0-9]*)(?:-|$)", c, flags=re.IGNORECASE)
    if m:
        base = PB_PREFIX_TO_PRODUCT.get(card_prefix(c))
        if not base:
            return ""
        n = int(m.group(1))
        return base if n == 1 else f"{base}{n:02d}"

    m = re.search(r"(?:^|-)sd([1-9][0-9]*)(?:-|$)", c, flags=re.IGNORECASE)
    if m:
        base = SD_PREFIX_TO_PRODUCT.get(card_prefix(c))
        if not base:
            return ""
        return re.sub(r"SD\d{2}$", f"SD{int(m.group(1)):02d}", base)

    m = re.search(r"(?:^|-)cl([1-9][0-9]*)(?:-|$)", c, flags=re.IGNORECASE)
    if m:
        base = CL_PREFIX_TO_PRODUCT.get(card_prefix(c))
        if not base:
            return ""
        return re.sub(r"\d{2}$", f"{int(m.group(1)):02d}", base)

    if re.search(r"-PR-\d+(?:-|$)", c, flags=re.IGNORECASE):
        return "PR"
    return ""


def is_energy_cardnumber(cardno: str) -> bool:
    canonical, _rarity = canonical_cardnumber(cardno)
    return bool(re.search(r"-(?:bp|pb|sd|cl)\d+-E\d+(?:$|-)", canonical, flags=re.IGNORECASE))


def remove_energy_manifest_entries(manifest: Dict[str, Any]) -> int:
    cards = manifest.setdefault("cards", {})
    if not isinstance(cards, dict):
        manifest["cards"] = {}
        return 0
    removed = 0
    for cardno in list(cards.keys()):
        if is_energy_cardnumber(str(cardno)):
            del cards[cardno]
            removed += 1
    return removed


def cardname_from_index_row(row_text: str, cardnumber: str) -> str:
    text = re.sub(r"\s+", " ", str(row_text or "")).strip()
    if not text:
        return ""
    text = re.sub(r"^\d{4}/\d{1,2}/\d{1,2}\s*", "", text)
    text = re.sub(re.escape(cardnumber), "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(?:ポスト|post)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" 　-_/｜|")
    return text[:120]


def load_product_registry(path: Path) -> Dict[str, ProductInfo]:
    obj = load_json_object(path)
    products = obj.get("products", {}) if isinstance(obj, dict) else {}
    if not isinstance(products, dict):
        raise SystemExit(f"ERROR: invalid product release registry: {path}")

    out: Dict[str, ProductInfo] = {}
    for code, raw in products.items():
        if not isinstance(raw, dict):
            continue
        code_norm = str(code or "").strip().upper()
        release_raw = str(raw.get("release_date", "") or "").strip()
        if not code_norm or not release_raw:
            continue
        try:
            date.fromisoformat(release_raw)
        except ValueError:
            continue
        out[code_norm] = ProductInfo(
            product_code=code_norm,
            release_date=release_raw,
            title=str(raw.get("title", "") or "").strip(),
            source_url=str(raw.get("source_url", "") or "").strip(),
        )
    return out


def prerelease_products(products: Dict[str, ProductInfo], *, as_of: date) -> Dict[str, ProductInfo]:
    out: Dict[str, ProductInfo] = {}
    for code, info in products.items():
        try:
            release_day = date.fromisoformat(info.release_date)
        except ValueError:
            continue
        if as_of < release_day:
            out[code] = info
    return out


def load_db_cardnumbers(path: Path) -> set[str]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    rows = obj if isinstance(obj, list) else obj.get("cards", []) if isinstance(obj, dict) else []
    if not isinstance(rows, list):
        raise SystemExit(f"ERROR: invalid DB JSON: {path}")
    out: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        raw = str(row.get("cardnumber", "") or "").strip()
        if not raw:
            continue
        canonical, _rarity = canonical_cardnumber(raw)
        out.add(canonical)
    return out


def retry_after_seconds(response: requests.Response, retry_index: int) -> float:
    raw = str(response.headers.get("Retry-After", "") or "").strip()
    if raw:
        try:
            return max(1.0, float(raw))
        except ValueError:
            pass
    return min(900.0, 300.0 * (2 ** max(0, retry_index))) + random.uniform(0.0, 30.0)


def request_text_once(url: str, *, timeout: float) -> str:
    """Single polite page attempt. Deliberately do not sleep 5+ minutes on 429."""
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=timeout,
    )
    if response.status_code == 429:
        retry_after = retry_after_seconds(response, 0)
        raise RuntimeError(f"HTTP 429 retry_after={retry_after:.1f}s")
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"
    return response.text


def request_json(url: str, *, timeout: float, max_429_retries: int = 3) -> Any:
    rate_retry = 0
    transient_retry = 0
    while True:
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=timeout,
            )
        except (requests.Timeout, requests.ConnectionError) as exc:
            if transient_retry < 2:
                wait_sec = 5.0 * (2 ** transient_retry)
                transient_retry += 1
                print(
                    f"[HTTP][WARN] transient retry={transient_retry}/2 "
                    f"wait={wait_sec:.1f}s url={url} ({exc})",
                    file=sys.stderr,
                )
                time.sleep(wait_sec)
                continue
            raise RuntimeError(f"network error: {url}: {exc}") from exc

        if response.status_code == 429:
            rate_retry += 1
            if rate_retry > max_429_retries:
                raise RuntimeError(f"HTTP 429 repeated {rate_retry} times: {url}")
            wait_sec = retry_after_seconds(response, rate_retry - 1)
            print(
                f"[RATE-LIMIT] 429 retry={rate_retry}/{max_429_retries} "
                f"wait={wait_sec:.1f}s url={url}",
                file=sys.stderr,
            )
            time.sleep(wait_sec)
            continue

        response.raise_for_status()
        try:
            return response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"invalid JSON response: {url}\n{response.text[:1000]}"
            ) from exc


def parse_datetime(value: str) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def cache_is_fresh(cache_obj: Dict[str, Any], *, ttl_minutes: float) -> bool:
    checked = parse_datetime(str(cache_obj.get("checked_at", "") or ""))
    if checked is None:
        return False
    age = datetime.now(timezone.utc) - checked
    return age <= timedelta(minutes=max(0.0, ttl_minutes))


def _x_status_id(href: str) -> str:
    parsed = urllib.parse.urlparse(str(href or ""))
    if parsed.netloc.lower() not in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}:
        return ""
    m = re.search(r"/status(?:es)?/(\d{15,22})(?:/|$)", parsed.path)
    return m.group(1) if m else ""


def _row_text_for_anchor(anchor: Tag) -> str:
    row = anchor.find_parent("tr")
    container: Tag = row if isinstance(row, Tag) else anchor.parent if isinstance(anchor.parent, Tag) else anchor
    return re.sub(r"\s+", " ", container.get_text(" ", strip=True)).strip()


CARD_VARIANT_RE = re.compile(
    r"(?P<value>(?:PL![A-Za-z]*|LL)-(?:(?:bp|pb|sd|cl)\d+|PR)-(?:E\d+|\d{3})(?:-[A-Za-z0-9+]+)?)",
    flags=re.IGNORECASE,
)


def _extract_cardnumber_from_row(row_text: str, known_cardnumbers: Sequence[str]) -> Tuple[str, str, str]:
    """Read the explicit cardnumber(+rarity) printed by the aggregate table.

    This intentionally does not require the card to exist in the current DB so
    the one-page prefetch can run before a clean-install DB build. DB membership
    is validated later when selecting active prerelease entries.
    """
    text = str(row_text or "")
    match = CARD_VARIANT_RE.search(text)
    if not match:
        return "", "", ""
    raw_value = match.group("value")
    canonical, rarity_norm = canonical_cardnumber(raw_value)
    rarity_raw = ""
    if rarity_norm:
        suffix = raw_value[len(canonical) + 1 :]
        rarity_raw = suffix.upper()
    return canonical, rarity_raw, rarity_norm


def parse_official_posts_index_html(
    page_html: str,
    *,
    known_cardnumbers: Iterable[str],
) -> Tuple[List[OfficialPostIndexEntry], Dict[str, int]]:
    known = sorted({str(x).strip() for x in known_cardnumbers if str(x).strip()}, key=len, reverse=True)
    soup = BeautifulSoup(page_html, "lxml")
    entries: List[OfficialPostIndexEntry] = []
    stats = {
        "x_links": 0,
        "mapped": 0,
        "unmapped": 0,
        "duplicate_pairs": 0,
    }
    seen: set[Tuple[str, str]] = set()

    for anchor in soup.find_all("a", href=True):
        if not isinstance(anchor, Tag):
            continue
        href = urllib.parse.urljoin(OFFICIAL_POSTS_PAGE_URL, str(anchor.get("href", "") or ""))
        tweet_id = _x_status_id(href)
        if not tweet_id:
            continue
        stats["x_links"] += 1
        row_text = _row_text_for_anchor(anchor)
        cardno, rarity_raw, rarity_norm = _extract_cardnumber_from_row(row_text, known)
        if not cardno:
            stats["unmapped"] += 1
            continue
        key = (cardno, tweet_id)
        if key in seen:
            stats["duplicate_pairs"] += 1
            continue
        seen.add(key)
        entries.append(
            OfficialPostIndexEntry(
                cardnumber=cardno,
                rarity_raw=rarity_raw,
                rarity_norm=rarity_norm,
                tweet_id=tweet_id,
                post_url=f"https://x.com/{DEFAULT_USERNAME}/status/{tweet_id}",
                row_text=row_text,
            )
        )
        stats["mapped"] += 1
    return entries, stats


def index_entry_to_dict(entry: OfficialPostIndexEntry) -> Dict[str, str]:
    return asdict(entry)


def index_entry_from_dict(raw: Dict[str, Any]) -> OfficialPostIndexEntry:
    return OfficialPostIndexEntry(
        cardnumber=str(raw.get("cardnumber", "") or "").strip(),
        rarity_raw=str(raw.get("rarity_raw", "") or "").strip(),
        rarity_norm=str(raw.get("rarity_norm", "") or "").strip(),
        tweet_id=str(raw.get("tweet_id", "") or "").strip(),
        post_url=str(raw.get("post_url", "") or "").strip(),
        row_text=str(raw.get("row_text", "") or ""),
    )


def load_index_cache(path: Path) -> Dict[str, Any]:
    return load_json_object(path)


def save_index_cache(
    path: Path,
    *,
    entries: Sequence[OfficialPostIndexEntry],
    parse_stats: Dict[str, int],
) -> None:
    payload = {
        "schema_version": 1,
        "source_url": OFFICIAL_POSTS_PAGE_URL,
        "checked_at": utc_now_iso(),
        "entries": [index_entry_to_dict(entry) for entry in entries],
        "parse_stats": dict(parse_stats),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cached_index_entries(cache_obj: Dict[str, Any]) -> List[OfficialPostIndexEntry]:
    rows = cache_obj.get("entries", []) if isinstance(cache_obj, dict) else []
    if not isinstance(rows, list):
        return []
    out: List[OfficialPostIndexEntry] = []
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        entry = index_entry_from_dict(raw)
        if entry.cardnumber and entry.tweet_id:
            out.append(entry)
    return out


def fetch_or_load_official_posts_index(
    *,
    cache_path: Path,
    known_cardnumbers: Iterable[str],
    timeout: float,
    cache_ttl_minutes: float,
    force_refresh: bool,
) -> Tuple[List[OfficialPostIndexEntry], Dict[str, Any]]:
    cache_obj = load_index_cache(cache_path)
    cached_entries = cached_index_entries(cache_obj)
    if cached_entries and not force_refresh and cache_is_fresh(cache_obj, ttl_minutes=cache_ttl_minutes):
        return cached_entries, {
            "source": "cache_fresh",
            "entries": len(cached_entries),
            **{str(k): int(v) for k, v in (cache_obj.get("parse_stats", {}) or {}).items() if isinstance(v, int)},
        }

    try:
        page_html = request_text_once(OFFICIAL_POSTS_PAGE_URL, timeout=timeout)
        entries, parse_stats = parse_official_posts_index_html(
            page_html,
            known_cardnumbers=known_cardnumbers,
        )
        save_index_cache(cache_path, entries=entries, parse_stats=parse_stats)
        return entries, {"source": "network", "entries": len(entries), **parse_stats}
    except Exception as exc:  # noqa: BLE001
        if cached_entries:
            print(
                f"[WIKI-OFFICIAL-POSTS][WARN] refresh failed; using stale cache: {exc}",
                file=sys.stderr,
            )
            return cached_entries, {
                "source": "cache_stale_after_error",
                "entries": len(cached_entries),
                "refresh_error": str(exc),
            }
        raise RuntimeError(
            f"official-post index fetch failed and no cache is available: {exc}"
        ) from exc


def _syndication_token(tweet_id: str) -> str:
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
    return TweetRecord(
        tweet_id=tweet_id,
        text=str(obj.get("text", "") or ""),
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
    obj = request_json(url, timeout=timeout)
    if not isinstance(obj, dict):
        raise RuntimeError(f"unexpected syndication response for {tweet_id}")
    return tweet_from_syndication_json(obj, username=username, source="x_syndication")


def tweet_to_dict(tweet: TweetRecord) -> Dict[str, Any]:
    return {
        "tweet_id": tweet.tweet_id,
        "text": tweet.text,
        "media_urls": list(tweet.media_urls),
        "created_at": tweet.created_at,
        "post_url": tweet.post_url,
        "source": tweet.source,
    }


def tweet_from_dict(raw: Dict[str, Any]) -> TweetRecord:
    return TweetRecord(
        tweet_id=str(raw.get("tweet_id", "") or "").strip(),
        text=str(raw.get("text", "") or ""),
        media_urls=tuple(
            str(x).strip()
            for x in (raw.get("media_urls", []) or [])
            if str(x).strip()
        ),
        created_at=str(raw.get("created_at", "") or ""),
        post_url=str(raw.get("post_url", "") or ""),
        source=str(raw.get("source", "") or "cache"),
    )


def load_tweet_cache(path: Path) -> Dict[str, TweetRecord]:
    obj = load_json_object(path)
    rows = obj.get("tweets", []) if isinstance(obj, dict) else []
    out: Dict[str, TweetRecord] = {}
    if isinstance(rows, list):
        for raw in rows:
            if not isinstance(raw, dict):
                continue
            tweet = tweet_from_dict(raw)
            if tweet.tweet_id:
                out[tweet.tweet_id] = tweet
    return out


def save_tweet_cache(path: Path, tweets: Dict[str, TweetRecord]) -> None:
    payload = {
        "schema_version": 1,
        "updated_at": utc_now_iso(),
        "tweets": [
            tweet_to_dict(tweet)
            for _tweet_id, tweet in sorted(
                tweets.items(),
                key=lambda item: int(item[0]) if item[0].isdigit() else -1,
            )
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> Dict[str, Any]:
    obj = load_json_object(path)
    if not obj:
        return {"cards": {}}
    if not isinstance(obj.get("cards"), dict):
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


def process_direct_index_entries(
    *,
    entries: Sequence[OfficialPostIndexEntry],
    active_products: Dict[str, ProductInfo],
    known_cardnumbers: set[str],
    tweets: Dict[str, TweetRecord],
    manifest: Dict[str, Any],
    keyword: str,
) -> Tuple[List[MatchAudit], int]:
    audits: List[MatchAudit] = []
    added = 0

    for entry in entries:
        product_code = product_code_for_cardnumber(entry.cardnumber)
        if product_code not in active_products:
            continue
        tweet = tweets.get(entry.tweet_id)
        if tweet is None:
            audits.append(
                MatchAudit(
                    tweet_id=entry.tweet_id,
                    post_url=entry.post_url,
                    source="wiki_official_posts_index",
                    created_at="",
                    product_code=product_code,
                    candidate_products=product_code,
                    keyword_present=False,
                    product_text_present=True,
                    rarity=entry.rarity_norm,
                    matched_cardname="",
                    cardname_matches="",
                    candidate_cardnumbers=entry.cardnumber,
                    selected_cardnumber=entry.cardnumber,
                    media_count=0,
                    status="POST_FETCH_FAILED",
                    reason="tweet-result JSON unavailable",
                    text=entry.row_text,
                )
            )
            continue

        keyword_present = keyword in tweet.text or "新カード紹介" in tweet.text
        media_count = len(tweet.media_urls)
        if not keyword_present:
            status = "SKIP_KEYWORD"
            reason = f"card-introduction keyword not found: {keyword}"
        elif media_count == 0:
            status = "NO_MEDIA"
            reason = "no pbs.twimg.com photo media URL"
        elif media_count != 1:
            status = "AMBIGUOUS_MEDIA"
            reason = f"expected one photo; got {media_count}"
        else:
            if entry.cardnumber in known_cardnumbers:
                status = "MATCHED_WIKI_OFFICIAL_POST_INDEX"
                reason = "cardnumber and post URL directly paired by WIKIWIKI 公式ポスト index"
            else:
                status = "MATCHED_WIKI_OFFICIAL_POST_INDEX_PREVIEW_ONLY"
                reason = (
                    "cardnumber and post URL directly paired by WIKIWIKI 公式ポスト index; "
                    "card is not in local DB yet, so only preview image metadata is registered"
                )
            manifest_entry = {
                "folder": product_code,
                "rarity_norm": entry.rarity_norm,
                "image_url": tweet.media_urls[0],
                "source": "official_x_via_wiki_official_posts_index",
                "post_url": entry.post_url,
                "tweet_id": entry.tweet_id,
                "posted_at": tweet.created_at,
                "cardname_from_post": cardname_from_index_row(entry.row_text, entry.cardnumber),
                "match_status": status,
            }
            if add_manifest_entry(manifest, entry.cardnumber, manifest_entry):
                added += 1

        audits.append(
            MatchAudit(
                tweet_id=entry.tweet_id,
                post_url=entry.post_url,
                source="wiki_official_posts_index",
                created_at=tweet.created_at,
                product_code=product_code,
                candidate_products=product_code,
                keyword_present=keyword_present,
                product_text_present=True,
                rarity=entry.rarity_norm,
                matched_cardname="",
                cardname_matches="",
                candidate_cardnumbers=entry.cardnumber,
                selected_cardnumber=entry.cardnumber,
                media_count=media_count,
                status=status,
                reason=reason,
                text=tweet.text,
            )
        )

    return audits, added


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Build Loveca preview image manifest from WIKIWIKI 公式ポスト + public X syndication"
    )
    ap.add_argument("--root", type=Path, default=Path("./llocg_db_out_full"))
    ap.add_argument("--db", type=Path, default=None)
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument("--product-registry", type=Path, default=None)
    ap.add_argument("--product-code", default="")
    ap.add_argument("--as-of", default="")
    ap.add_argument("--keyword", default=DEFAULT_KEYWORD)
    ap.add_argument("--audit-tsv", type=Path, default=None)
    ap.add_argument("--audit-json", type=Path, default=None)
    ap.add_argument("--tweet-cache", type=Path, default=None)
    ap.add_argument("--official-posts-cache", type=Path, default=None)
    ap.add_argument("--official-posts-cache-minutes", type=float, default=30.0)
    ap.add_argument("--refresh-official-posts-cache", action="store_true")
    ap.add_argument("--prefetch-official-posts-only", action="store_true")
    ap.add_argument("--require-discovered-posts", action="store_true")
    ap.add_argument("--x-username", default=DEFAULT_USERNAME)
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--syndication-delay", type=float, default=0.25)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strict", action="store_true")

    # Compatibility options accepted but intentionally unused by the normal path.
    ap.add_argument("--empty-recheck-hours", type=float, default=12.0)
    ap.add_argument("--page-cache-ttl-hours", type=float, default=6.0)
    ap.add_argument("--http-cache", type=Path, default=None)
    ap.add_argument("--wiki-source-cache", type=Path, default=None)
    ap.add_argument("--wiki-source-timeout", type=float, default=30.0)
    ap.add_argument("--wiki-source-delay", type=float, default=5.0)
    ap.add_argument("--no-wiki-source-auto", action="store_true")
    ap.add_argument("--refresh-wiki-source-cache", action="store_true")
    ap.add_argument("--collection-state", type=Path, default=None)
    ap.add_argument("--override-json", type=Path, default=None)
    ap.add_argument("--product-text", default="")
    ap.add_argument("--x-api-timeline", action="store_true")
    ap.add_argument("--x-bearer-token", default="")
    ap.add_argument("--x-start-time", default="")
    ap.add_argument("--initial-lookback-days", type=int, default=120)
    ap.add_argument("--max-pages", type=int, default=10)
    ap.add_argument("--tweet-id", action="append", default=[])
    ap.add_argument("--tweet-id-file", type=Path, default=None)
    ap.add_argument("--tweet-json", action="append", type=Path, default=[])
    ap.add_argument("--tweet-json-dir", type=Path, default=None)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    db_path = args.db.resolve() if args.db else root / "cards_min_tokv1.json"
    manifest_path = args.manifest.resolve() if args.manifest else root / PREVIEW_MANIFEST_FILENAME
    registry_path = (
        args.product_registry.resolve()
        if args.product_registry
        else root / PRODUCT_RELEASE_REGISTRY_FILENAME
    )
    tweet_cache_path = args.tweet_cache.resolve() if args.tweet_cache else root / TWEET_CACHE_FILENAME
    index_cache_path = (
        args.official_posts_cache.resolve()
        if args.official_posts_cache
        else root / OFFICIAL_POSTS_CACHE_FILENAME
    )
    audit_tsv = args.audit_tsv.resolve() if args.audit_tsv else root / AUDIT_TSV_FILENAME
    audit_json = args.audit_json.resolve() if args.audit_json else root / AUDIT_JSON_FILENAME

    try:
        as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    except ValueError as exc:
        raise SystemExit("ERROR: --as-of must be YYYY-MM-DD") from exc

    # Prefetch can run before the DB update. It only refreshes one WIKIWIKI page
    # and stores parsed direct cardnumber->post mappings for the later stage.
    if args.prefetch_official_posts_only:
        known_cardnumbers = load_db_cardnumbers(db_path) if db_path.exists() else set()
        try:
            entries, stats = fetch_or_load_official_posts_index(
                cache_path=index_cache_path,
                known_cardnumbers=known_cardnumbers,
                timeout=args.timeout,
                cache_ttl_minutes=max(0.0, args.official_posts_cache_minutes),
                force_refresh=args.refresh_official_posts_cache,
            )
        except RuntimeError as exc:
            print(f"BUILD_TAG={BUILD_TAG}")
            print("mode=prefetch_official_posts_only")
            print(f"[WIKI-OFFICIAL-POSTS][WARN] {exc}", file=sys.stderr)
            if args.require_discovered_posts:
                raise SystemExit(f"ERROR: {exc}") from exc
            return 0
        print(f"BUILD_TAG={BUILD_TAG}")
        print("mode=prefetch_official_posts_only")
        print(
            "[WIKI-OFFICIAL-POSTS] "
            + " ".join(f"{key}={value}" for key, value in stats.items())
        )
        print(f"cache={index_cache_path}")
        print(f"entries={len(entries)}")
        return 0

    products = load_product_registry(registry_path)
    active_products = prerelease_products(products, as_of=as_of)
    if args.product_code:
        requested = args.product_code.strip().upper()
        active_products = {code: info for code, info in active_products.items() if code == requested}

    print(f"BUILD_TAG={BUILD_TAG}")
    print(f"as_of={as_of.isoformat()}")
    print("collection_default=wiki_official_posts_index_no_paid_x_api")

    if not active_products:
        print("prerelease_products=0")
        print("manifest_added=0")
        return 0

    known_cardnumbers = load_db_cardnumbers(db_path)
    try:
        entries, index_stats = fetch_or_load_official_posts_index(
            cache_path=index_cache_path,
            known_cardnumbers=known_cardnumbers,
            timeout=args.timeout,
            cache_ttl_minutes=max(0.0, args.official_posts_cache_minutes),
            force_refresh=args.refresh_official_posts_cache,
        )
    except RuntimeError as exc:
        print(f"[WIKI-OFFICIAL-POSTS][WARN] {exc}", file=sys.stderr)
        if args.require_discovered_posts:
            raise SystemExit(f"ERROR: {exc}") from exc
        print("manifest_added=0")
        print("reason=official-post index unavailable and no cache exists")
        return 0
    print(
        "[WIKI-OFFICIAL-POSTS] "
        + " ".join(f"{key}={value}" for key, value in index_stats.items())
    )

    active_entries = [
        entry
        for entry in entries
        if product_code_for_cardnumber(entry.cardnumber) in active_products
    ]
    energy_entries = [entry for entry in active_entries if is_energy_cardnumber(entry.cardnumber)]
    relevant_entries = [entry for entry in active_entries if not is_energy_cardnumber(entry.cardnumber)]
    known_relevant = [entry for entry in relevant_entries if entry.cardnumber in known_cardnumbers]
    missing_db = [entry for entry in relevant_entries if entry.cardnumber not in known_cardnumbers]
    print(
        "[PREVIEW-INDEX] "
        f"active_products={len(active_products)} "
        f"relevant_entries={len(relevant_entries)} "
        f"known_db_entries={len(known_relevant)} "
        f"index_cards_not_in_db={len(missing_db)} "
        f"energy_card_entries_skipped={len(energy_entries)}"
    )
    if missing_db:
        sample = ", ".join(
            "{}{}".format(
                entry.cardnumber,
                f"-{entry.rarity_raw}" if entry.rarity_raw else "",
            )
            for entry in missing_db[:30]
        )
        print(
            "[PREVIEW-INDEX-MISSING-DB] "
            f"cards={len(missing_db)} "
            f"sample={sample} "
            "reason=official-post index has prerelease rows that are not in the local DB yet"
        )
    if args.require_discovered_posts and not relevant_entries:
        raise SystemExit(
            "ERROR: no prerelease card/post mappings discovered on WIKIWIKI 公式ポスト index"
        )

    tweets = load_tweet_cache(tweet_cache_path)
    requested_ids = list(dict.fromkeys(entry.tweet_id for entry in relevant_entries))
    new_tweets = 0
    fetch_failures: Dict[str, str] = {}
    for tweet_id in requested_ids:
        if tweet_id in tweets:
            continue
        try:
            tweets[tweet_id] = fetch_syndication_tweet(
                tweet_id,
                username=args.x_username,
                timeout=args.timeout,
            )
            new_tweets += 1
        except Exception as exc:  # noqa: BLE001
            fetch_failures[tweet_id] = str(exc)
            print(f"[X-SYNDICATION][WARN] tweet_id={tweet_id}: {exc}", file=sys.stderr)
        if args.syndication_delay > 0:
            time.sleep(max(0.0, args.syndication_delay))
    save_tweet_cache(tweet_cache_path, tweets)

    manifest = load_manifest(manifest_path)
    removed_energy_manifest = remove_energy_manifest_entries(manifest)
    audits, added = process_direct_index_entries(
        entries=relevant_entries,
        active_products=active_products,
        known_cardnumbers=known_cardnumbers,
        tweets=tweets,
        manifest=manifest,
        keyword=args.keyword,
    )
    write_audit(audits, audit_tsv, audit_json)

    if not args.dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    counts: Dict[str, int] = {}
    for row in audits:
        counts[row.status] = counts.get(row.status, 0) + 1

    print(
        "prerelease_products="
        + ",".join(
            f"{code}:{info.release_date}"
            for code, info in sorted(active_products.items())
        )
    )
    print(
        f"index_entries={len(entries)} relevant_entries={len(relevant_entries)} "
        f"requested_posts={len(requested_ids)} new_tweets={new_tweets} "
        f"tweet_fetch_failures={len(fetch_failures)}"
    )
    print(f"manifest_added={added}")
    print(f"manifest_energy_removed={removed_energy_manifest}")
    for status, count in sorted(counts.items()):
        print(f"{status}: {count}")
    print(f"official_posts_cache={index_cache_path}")
    print(f"tweet_cache={tweet_cache_path}")
    print(f"audit_tsv={audit_tsv}")
    print(f"audit_json={audit_json}")
    print("manifest=DRY_RUN" if args.dry_run else f"manifest={manifest_path}")

    unresolved_statuses = {
        "POST_FETCH_FAILED",
        "NO_MEDIA",
        "AMBIGUOUS_MEDIA",
    }
    unresolved = [row for row in audits if row.status in unresolved_statuses]
    if args.strict and unresolved:
        print(f"[STRICT] unresolved={len(unresolved)}", file=sys.stderr)
        return 2
    if args.require_discovered_posts and not any(
        row.status in {
            "MATCHED_WIKI_OFFICIAL_POST_INDEX",
            "MATCHED_WIKI_OFFICIAL_POST_INDEX_PREVIEW_ONLY",
        }
        for row in audits
    ):
        raise SystemExit("ERROR: prerelease post mappings were found but no usable preview image was matched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
