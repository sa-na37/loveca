#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llocg_deckcode_to_decklist.py

DeckLog deck code / saved HTML -> deck TSV for simulation.

Key features:
- Parse main deck ONLY (energy deck ignored).
- Robust HTML parsing: image-first -> count (<img ...> ... <span class="num">N</span>).
- For --code:
    1) Try DeckLog API endpoints (fast; may break when schema changes)
    2) Try direct HTML GET (often a JS shell)
    3) Fallback to Playwright-rendered HTML (reliable)
   Rendered HTML is cached to <root>/decklists/<CODE>.html (unless --no-cache-html).
- Writes TSV to <root>/decklists/deck_<CODE>.tsv (default).
- Writes meta JSON (deck name etc.) to <root>/decklists/deck_<CODE>.meta.json
  without changing TSV schema.

Usage:
  python3 llocg_deckcode_to_decklist.py --root ./llocg_db_out_full --code 1RCBL
  python3 llocg_deckcode_to_decklist.py --root ./llocg_db_out_full --html ./llocg_db_out_full/decklists/1RCBL.html
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# -----------------------------
# Data model
# -----------------------------

@dataclass
class DeckEntry:
    count: int
    card_no: str
    rarity: str
    name: str = ""

# -----------------------------
# Helpers
# -----------------------------

def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def write_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def write_deck_tsv(path: Path, cards: List[DeckEntry], with_name: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["count", "card_no", "rarity"] + (["name"] if with_name else [])
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for c in cards:
            row = {"count": c.count, "card_no": c.card_no, "rarity": c.rarity}
            if with_name:
                row["name"] = c.name
            w.writerow(row)

def write_deck_txt(path: Path, cards: List[DeckEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for c in cards:
        if c.name:
            lines.append(f"{c.count}\t{c.card_no}\t{c.rarity}\t{c.name}")
        else:
            lines.append(f"{c.count}\t{c.card_no}\t{c.rarity}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

# -----------------------------
# Deck name extraction & meta JSON
# -----------------------------

def extract_deck_name_from_html(html_text: str) -> str:
    m = re.search(r"<h2>\s*デッキ名「([^」]+)」のデッキ\s*</h2>", html_text)
    if m:
        return m.group(1).strip()
    m = re.search(r"デッキ名「([^」]+)」", html_text)
    if m:
        return m.group(1).strip()
    return ""

def write_deck_meta_json(
    root: Path,
    code: str,
    deck_name: str,
    source_url: str,
    html_path: Optional[Path],
    tsv_path: Path,
) -> Path:
    meta = {
        "deck_code": code,
        "deck_name": deck_name,
        "source_url": source_url,
        "html_path": str(html_path) if html_path else "",
        "tsv_path": str(tsv_path),
        "fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    out = (root / "decklists" / f"deck_{code}.meta.json").resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return out

# -----------------------------
# Card no / rarity split
# -----------------------------

def _norm_plus(s: str) -> str:
    return (s or "").replace("＋", "+").strip()


def split_card_no_and_rarity(s: str) -> Tuple[str, str]:
    if not s:
        return "", ""
    s = s.strip()
    s = s.replace("－", "-").replace("―", "-").replace("—", "-")
    s = _norm_plus(s)

    # DeckLog sometimes exports card IDs like:
    #   PL!N-pb1-005-P+
    #   PL!N-pb1-005-P＋
    #   PL!HS-PR-018-PR
    # Strip the rarity suffix, then trim any separator hyphen left before it.
    tokens = ["SEC2", "SEC+", "SEC", "R2", "R+", "PR", "P2", "P1", "P+", "SD", "L", "N", "R"]
    su = s.upper()
    for t in tokens:
        if su.endswith(t):
            card_no = s[:-len(t)].rstrip("-").strip()
            rarity = t.replace("P1", "P").replace("SEC+", "SEC2").replace("R+", "R2")
            return card_no, rarity

    # Tolerate a trailing hyphen even when no rarity suffix was present.
    return s.rstrip("-").strip(), ""

# -----------------------------
# Parsing: HTML (rendered)
# -----------------------------

IMG_URL_RE = re.compile(r"/cardlist/(?P<fname>[^\"'>]+?\.png)\b", re.IGNORECASE)

def _slice_main_deck_section(html_text: str) -> str:
    m0 = re.search(r"<h3>\s*メインデッキ\s*</h3>", html_text)
    if not m0:
        return html_text
    sub = html_text[m0.end():]
    m1 = re.search(r"<h3>\s*エネルギーデッキ\s*</h3>", sub)
    if m1:
        return html_text[m0.start(): m0.end() + m1.start()]
    return html_text[m0.start():]

def parse_cards_from_html_by_image_urls(html_text: str) -> List[DeckEntry]:
    main_html = _slice_main_deck_section(html_text)

    img_re = re.compile(
        r"<img[^>]+?title=\"(?P<cardid>[^\"]+?)\s*:\s*(?P<name>[^\"]*?)\""  # cardid : name
        r"[^>]+?(?:data-src|src)=\"(?P<imgurl>[^\"]*?/cardlist/[^\"]+?\.png[^\"]*)\"",
        re.IGNORECASE | re.DOTALL,
    )

    rendered_hits: Dict[Tuple[str, str], DeckEntry] = {}
    for m in img_re.finditer(main_html):
        cardid = (m.group("cardid") or "").strip()
        name = (m.group("name") or "").strip()
        imgurl = (m.group("imgurl") or "").strip()

        win_end = min(len(main_html), m.end() + 400)
        window = main_html[m.end():win_end]
        cm = re.search(r"<span\s+class=\"num\">\s*(\d+)\s*</span>", window, re.IGNORECASE)
        if not cm:
            continue
        cnt = int(cm.group(1))

        card_no, rarity = split_card_no_and_rarity(cardid)
        if not rarity:
            fname_m = re.search(r"/cardlist/([^/?#]+)\.png", imgurl, re.IGNORECASE)
            if fname_m:
                stem = fname_m.group(1)
                card_no2, rarity2 = split_card_no_and_rarity(stem)
                if card_no2:
                    card_no, rarity = card_no2, rarity2

        if not card_no:
            continue

        key = (card_no, rarity)
        if key not in rendered_hits:
            rendered_hits[key] = DeckEntry(count=0, card_no=card_no, rarity=rarity, name=name)
        rendered_hits[key].count += cnt

    if rendered_hits:
        out = list(rendered_hits.values())
        out.sort(key=lambda x: (x.card_no, x.rarity))
        return out

    # Fallback: image URLs only
    found: Dict[Tuple[str, str], DeckEntry] = {}
    matches = list(IMG_URL_RE.finditer(main_html))
    if not matches:
        return []
    for m in matches:
        fname = m.group("fname")
        stem = Path(fname).stem
        card_no, rarity = split_card_no_and_rarity(stem)
        if not card_no:
            continue
        key = (card_no, rarity)
        found.setdefault(key, DeckEntry(count=0, card_no=card_no, rarity=rarity))
        found[key].count += 1
    out = list(found.values())
    out.sort(key=lambda x: (x.card_no, x.rarity))
    return out

# -----------------------------
# Fetching
# -----------------------------

def fetch_url_bytes_requests(url: str, *, ua: str, timeout: float, verify_ssl: bool) -> bytes:
    import requests
    headers = {"User-Agent": ua, "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"}
    r = requests.get(url, headers=headers, timeout=timeout, verify=verify_ssl)
    r.raise_for_status()
    return r.content

def fetch_url_bytes_urllib(url: str, *, ua: str, timeout: float, verify_ssl: bool) -> bytes:
    import ssl
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"})
    if verify_ssl:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read()

def fetch_url_bytes(url: str, *, ua: str, timeout: float, insecure_fallback: bool, log: List[str]) -> bytes:
    try:
        return fetch_url_bytes_requests(url, ua=ua, timeout=timeout, verify_ssl=True)
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        if "SSL" in msg or "CERTIFICATE" in msg.upper():
            log.append(f"[WARN] SSL verification failed when fetching {url}; retrying without verification (--insecure).")
            if not insecure_fallback:
                raise
            try:
                return fetch_url_bytes_requests(url, ua=ua, timeout=timeout, verify_ssl=False)
            except Exception:
                return fetch_url_bytes_urllib(url, ua=ua, timeout=timeout, verify_ssl=False)
        try:
            return fetch_url_bytes_urllib(url, ua=ua, timeout=timeout, verify_ssl=True)
        except Exception:
            raise

# -----------------------------
# API parsing
# -----------------------------

def _json_loads_best_effort(text: str) -> Optional[Any]:
    try:
        return json.loads(text)
    except Exception:
        return None

def parse_cards_from_json(obj: Any) -> List[DeckEntry]:
    if not isinstance(obj, dict):
        return []
    candidates = []
    for k in ("mainDeck", "main_deck", "main", "deck", "cards"):
        v = obj.get(k)
        if isinstance(v, list):
            candidates.append(v)
    for k in ("data", "result"):
        v = obj.get(k)
        if isinstance(v, dict):
            for kk in ("mainDeck", "main", "cards"):
                vv = v.get(kk)
                if isinstance(vv, list):
                    candidates.append(vv)
    if not candidates:
        return []
    cards_out: Dict[Tuple[str, str], DeckEntry] = {}
    for arr in candidates:
        for it in arr:
            if not isinstance(it, dict):
                continue
            cid = str(it.get("cardId") or it.get("card_id") or it.get("id") or "").strip()
            if not cid:
                continue
            cnt = it.get("num") if "num" in it else it.get("count")
            try:
                cnt = int(cnt)
            except Exception:
                continue
            name = str(it.get("name") or it.get("cardName") or it.get("card_name") or "").strip()
            card_no, rarity = split_card_no_and_rarity(cid)
            if not card_no:
                continue
            key = (card_no, rarity)
            if key not in cards_out:
                cards_out[key] = DeckEntry(count=0, card_no=card_no, rarity=rarity, name=name)
            cards_out[key].count += cnt
    out = list(cards_out.values())
    out.sort(key=lambda x: (x.card_no, x.rarity))
    return out

def try_fetch_and_parse_by_api(code: str, *, ua: str, timeout: float, insecure_fallback: bool, log: List[str]) -> List[DeckEntry]:
    urls = [
        f"https://decklog.bushiroad.com/system/app/api/view/{code}",
        f"https://decklog.bushiroad.com/system/app/api/view/{code}/",
        f"https://decklog.bushiroad.com/system/app/api/view/{code}?_={int(datetime.datetime.now().timestamp()) % 100000}",
    ]
    for url in urls:
        try:
            data = fetch_url_bytes(url, ua=ua, timeout=timeout, insecure_fallback=insecure_fallback, log=log)
            text = data.decode("utf-8", errors="replace")
            obj = _json_loads_best_effort(text)
            if obj is None:
                continue
            cards = parse_cards_from_json(obj)
            if cards:
                log.append(f"[INFO] Parsed {len(cards)} unique cards from API source: {url}")
                return cards
        except Exception as e:
            log.append(f"[WARN] API fetch failed for {url}: {type(e).__name__}: {e}")
    return []

def try_fetch_and_parse_by_html(code: str, *, ua: str, timeout: float, insecure_fallback: bool, log: List[str]) -> Tuple[List[DeckEntry], str]:
    url = f"https://decklog.bushiroad.com/view/{code}"
    try:
        data = fetch_url_bytes(url, ua=ua, timeout=timeout, insecure_fallback=insecure_fallback, log=log)
        text = data.decode("utf-8", errors="replace")
    except Exception as e:
        log.append(f"[WARN] HTML fetch failed for {url}: {type(e).__name__}: {e}")
        return [], ""
    cards = parse_cards_from_html_by_image_urls(text)
    if cards:
        log.append(f"[INFO] Parsed {len(cards)} unique cards from HTML: {url}")
    return cards, text

def try_fetch_and_parse_by_playwright(code: str, *, timeout: float, log: List[str]) -> Tuple[List[DeckEntry], str]:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as e:
        log.append(f"[WARN] Playwright not available: {type(e).__name__}: {e}")
        return [], ""
    url = f"https://decklog.bushiroad.com/view/{code}"
    html = ""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=DEFAULT_UA, locale="ja-JP")
            page.goto(url, wait_until="networkidle", timeout=int(timeout * 1000))
            try:
                page.wait_for_selector("text=メインデッキ", timeout=8000)
            except Exception:
                pass
            try:
                page.wait_for_selector("img[src*='cardlist'], img[data-src*='cardlist']", timeout=8000)
            except Exception:
                pass
            html = page.content()
            browser.close()
    except Exception as e:
        log.append(f"[WARN] Playwright fetch failed for {url}: {type(e).__name__}: {e}")
        return [], ""
    cards = parse_cards_from_html_by_image_urls(html)
    if cards:
        log.append(f"[INFO] Parsed {len(cards)} unique cards via Playwright: {url}")
    return cards, html

def parse_from_local_html(path: Path, log: List[str]) -> Tuple[List[DeckEntry], str]:
    text = read_text_file(path)
    cards = parse_cards_from_html_by_image_urls(text)
    if cards:
        log.append(f"[INFO] Parsed {len(cards)} unique cards from local HTML: {path}")
    return cards, text

# -----------------------------
# main
# -----------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Project root (e.g., ./llocg_db_out_full)")
    ap.add_argument("--code", default="", help="DeckLog deck code (e.g., 7QEC8)")
    ap.add_argument("--html", default="", help="Saved DeckLog HTML (Save Page As) to parse offline")
    ap.add_argument("--out", default="", help="Output path. Default: <root>/decklists/deck_<code>.tsv")
    ap.add_argument("--format", choices=["tsv", "txt", "both"], default="tsv")
    ap.add_argument("--with-name", action="store_true", help="Include 4th 'name' column (if available)")
    ap.add_argument("--user-agent", default=DEFAULT_UA)
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--no-insecure-fallback", action="store_true")
    ap.add_argument("--no-playwright", action="store_true")
    ap.add_argument("--no-cache-html", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    log: List[str] = []

    if not args.code and not args.html:
        print("[ERR] Provide --code or --html")
        return 2

    insecure_fallback = not args.no_insecure_fallback
    decklists_dir = root / "decklists"
    decklists_dir.mkdir(parents=True, exist_ok=True)

    cache_html_path: Optional[Path] = None
    if args.code:
        cache_html_path = (decklists_dir / f"{args.code}.html").resolve()

    cards: List[DeckEntry] = []
    used_html_text = ""
    used_html_path: Optional[Path] = None

    if args.code and cache_html_path and cache_html_path.exists():
        c, ht = parse_from_local_html(cache_html_path, log=log)
        if c:
            cards = c
            used_html_text = ht
            used_html_path = cache_html_path

    if (not cards) and args.code:
        cards = try_fetch_and_parse_by_api(args.code, ua=args.user_agent, timeout=args.timeout, insecure_fallback=insecure_fallback, log=log)

    if (not cards) and args.code:
        c2, h2 = try_fetch_and_parse_by_html(args.code, ua=args.user_agent, timeout=args.timeout, insecure_fallback=insecure_fallback, log=log)
        if c2:
            cards = c2
            used_html_text = h2
            if cache_html_path and (not args.no_cache_html):
                try:
                    write_text_file(cache_html_path, h2)
                    used_html_path = cache_html_path
                except Exception as e:
                    log.append(f"[WARN] Failed to write cache HTML: {type(e).__name__}: {e}")

    if (not cards) and args.code and (not args.no_playwright):
        c3, h3 = try_fetch_and_parse_by_playwright(args.code, timeout=max(args.timeout, 25.0), log=log)
        if c3:
            cards = c3
            used_html_text = h3
            if cache_html_path and (not args.no_cache_html):
                try:
                    write_text_file(cache_html_path, h3)
                    used_html_path = cache_html_path
                except Exception as e:
                    log.append(f"[WARN] Failed to write cache HTML: {type(e).__name__}: {e}")

    if (not cards) and args.html:
        hp = Path(args.html).expanduser().resolve()
        c4, h4 = parse_from_local_html(hp, log=log)
        if c4:
            cards = c4
            used_html_text = h4
            used_html_path = hp

    if not cards:
        print("[ERR] No cards were parsed from the source.")
        if log:
            print("\n--- debug log ---")
            for ln in log[-20:]:
                print(ln)
        return 1

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
    else:
        tag = args.code if args.code else Path(args.html).stem
        out_path = decklists_dir / f"deck_{tag}.tsv"

    if args.format in ("tsv", "both"):
        write_deck_tsv(out_path, cards, with_name=args.with_name)
    if args.format in ("txt", "both"):
        write_deck_txt(out_path.with_suffix(".txt"), cards)

    deck_name = ""
    meta_json_path: Optional[Path] = None
    if args.code:
        source_url = f"https://decklog.bushiroad.com/view/{args.code}"
        if (not used_html_text) and cache_html_path and cache_html_path.exists():
            try:
                used_html_text = read_text_file(cache_html_path)
                used_html_path = cache_html_path
            except Exception:
                pass
        if used_html_text:
            deck_name = extract_deck_name_from_html(used_html_text)
        try:
            meta_json_path = write_deck_meta_json(root, args.code, deck_name, source_url, used_html_path, out_path)
        except Exception as e:
            log.append(f"[WARN] Failed to write deck meta json: {type(e).__name__}: {e}")

    print("[DONE]")
    print(f"root   : {root}")
    if args.code:
        print(f"code   : {args.code}")
        if deck_name:
            print(f"deck_name: {deck_name}")
        if meta_json_path:
            print(f"meta   : {meta_json_path}")
    if args.html:
        print(f"html   : {Path(args.html).expanduser().resolve()}")
    print(f"cards  : {len(cards)} unique")
    print(f"out    : {out_path}")
    if used_html_path:
        print(f"cache  : {used_html_path}")

    if any(ln.startswith("[WARN] SSL verification failed") for ln in log):
        print("note   : (some warnings occurred; run with --no-insecure-fallback to forbid insecure retry)")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
