#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LL-OCG DB Tool (single-file) v7

Subcommands:
  scrape    : wiki -> cards_min.csv/json  (with normalize columns if enabled)
  normalize : postprocess effect_tokens_json: (E)/(ALL)/(ブレード)/(スコア+N)
              + classify effect text into NO_ABILITY / HAS_TEXT
  mine      : mine frequent effect templates -> CSV + stub YAML
  audit     : audit CSV (missing, json parse, unknown tokens, cardno format)
  all       : scrape -> normalize -> mine -> audit

Deps:
  pip install requests beautifulsoup4 lxml pandas
"""

from __future__ import annotations

BUILD_TAG = "db_tool_cardtype_infer_20260410a"

import argparse
import hashlib
import json
import re
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import Counter

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
from bs4 import XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

CONFIG = {
    "products_url": "https://wikiwiki.jp/llocardgame/%E5%95%86%E5%93%81%E4%B8%80%E8%A6%A7",
    "outdir": "llocg_db_out",
    "cache": ".cache_llocg",
    "delay": 2.5,
    "checkpoint_every": 50,
    "max_fail": 500,
    "user_agent": "LL-OCG-DB-Build/1.0 (polite crawler; contact: your_email@example.com)",
    "normalize_suffix": "_tokv1",
}

# Allow: PL!-xxx-001, PL!HS-xxx-001, PL!SP-..., PL!N-..., etc.
CARDNO_IN_TEXT = re.compile(
    r"\b([A-Z]{1,4}(?:!(?:[A-Z0-9]{0,8})?)?-[A-Za-z0-9]+-\d{3}(?:-[A-Za-z0-9]+)?)\b"
)
AUDIT_CARDNO_RE = re.compile(r"^[A-Z]{1,4}(?:!(?:[A-Z0-9]{0,8})?)?-[A-Za-z0-9]+-\d{3}(?:-[A-Za-z0-9]+)?$")

START_MARKERS = ["▼効果テキスト", "▼カードテキスト", "▼テキスト"]
STOP_HEADINGS = {
    "カード解説", "収録状況", "コメント", "関連カード", "関連", "各種データ", "編集補助", "画像", "テンプレート",
    "カード検索補助", "人気", "今日人気", "最新"
}

KEY_MAP_EXACT = {
    "カードタイプ": "card_type",
    "カード種別": "card_type",
    "種別": "card_type",
    "作品": "work_title",
    "作品名": "work_title",
    "参加グループ": "group",
    "グループ": "group",
    "参加ユニット": "unit",
    "ユニット": "unit",
    "コスト": "cost",
    "ブレード": "blade",
    "ブレードハート": "blade_heart",
    "基本ハート": "base_hearts",
    "必要ハート": "required_hearts",
    "スコア": "score",
}
KEY_MAP_CONTAINS = [
    ("カードタイプ", "card_type"),
    ("カード種別", "card_type"),
    ("種別", "card_type"),
    ("作品名", "work_title"),
    ("作品", "work_title"),
    ("参加グループ", "group"),
    ("グループ", "group"),
    ("参加ユニット", "unit"),
    ("ユニット", "unit"),
    ("コスト", "cost"),
    ("ブレードハート", "blade_heart"),
    ("ブレード", "blade"),
    ("基本ハート", "base_hearts"),
    ("必要ハート", "required_hearts"),
    ("スコア", "score"),
]

COLOR_MAP = {
    "(桃)": "pink",
    "(黄)": "yellow",
    "(紫)": "purple",
    "(青)": "blue",
    "(緑)": "green",
    "(赤)": "red",
    "(白)": "white",
    "(黒)": "black",
    "(任意)": "any",
}

ICON_COUNT_RE = re.compile(r"<\(([^)]+)\)>\s*(?:×|x|X)?\s*(\d+)?")
TOTAL_RE = re.compile(r"\(合計\s*(\d+)\)")
FW_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")

# token postprocess
SCORE_TAG_RE = re.compile(r"^\(\s*(?:スコア|ｽｺｱ|SCORE|Score)\s*([+\-＋－])\s*(\d+)\s*\)$")
PLUS_MINUS_MAP = str.maketrans({"＋": "+", "－": "-"})
KNOWN_SIMPLE = {
    "(ブレード)": "blade_icon_n",
    "(E)": "energy_icon_n",     # Energy
    "(ALL)": "all_heart_n",     # All-heart
}

NO_ABILITY_MARKERS = {"", "(なし)", "(テキストなし)"}


# -------------------------
# official image manifest
# -------------------------
OFFICIAL_BASE_URL = "https://llofficial-cardgame.com"
OFFICIAL_CARDLIST_SEARCH_URL = OFFICIAL_BASE_URL + "/cardlist/searchresults/"
OFFICIAL_CARDLIST_MORE_URL = OFFICIAL_BASE_URL + "/cardlist/cardsearch_ex"

PB_PREFIX_TO_OFFICIAL_EXPANSION = {
    "PL!SP": "PBSP",
    "PL!LS": "PBLS",
    "PL!N": "PBnj",
    "PL!": "PBLL",
    "LL": "PBLL",
}
SD_PREFIX_TO_OFFICIAL_EXPANSION = {
    "PL!SP": "SPSD01",
    "PL!N": "NSD01",
    "PL!HS": "HSSD01",
    "PL!LS": "LSSD01",
    "PL!S": "SSD01",
    "PL!": "PLSD01",
}
OFFICIAL_RARITY_ALIAS = {
    "R＋": "R2", "R+": "R2",
    "L＋": "L2", "L+": "L2",
    "P＋": "P2", "P+": "P2",
    "PE＋": "PE2", "PE+": "PE2",
    "SEC＋": "SEC2", "SEC+": "SEC2",
    "PR＋": "PR2", "PR+": "PR2",
}
OFFICIAL_CARD_RARITY_TAIL_RE = re.compile(r"^(?P<base>.+)-(?P<rarity>[A-Za-z0-9＋\+]{1,8})$")


def _card_prefix_from_cardno(cardno: str) -> str:
    parts = (cardno or "").split("-")
    if not parts:
        return cardno
    head = parts[0]
    if head.startswith("PL!"):
        return head
    return head


def official_expansion_from_cardno(cardno: str) -> Optional[str]:
    c = (cardno or "").strip()
    if not c:
        return None
    m = re.search(r"(?:^|-)bp([1-9][0-9]*)(?:-|$)", c, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        return f"BP{n:02d}"
    m = re.search(r"(?:^|-)pb([1-9][0-9]*)(?:-|$)", c, re.IGNORECASE)
    if m:
        return PB_PREFIX_TO_OFFICIAL_EXPANSION.get(_card_prefix_from_cardno(c))
    m = re.search(r"(?:^|-)sd([1-9][0-9]*)(?:-|$)", c, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        base = SD_PREFIX_TO_OFFICIAL_EXPANSION.get(_card_prefix_from_cardno(c))
        if not base:
            return None
        return re.sub(r"SD\d{2}$", f"SD{n:02d}", base)
    return None


def official_normalize_rarity_token(token: str) -> str:
    t = (token or "").strip().upper().replace("＋", "+")
    return OFFICIAL_RARITY_ALIAS.get(t, t)


def split_display_card_and_rarity(display_card: str) -> Tuple[str, str]:
    s = (display_card or "").strip()
    m = OFFICIAL_CARD_RARITY_TAIL_RE.match(s)
    if not m:
        return s, ""
    base = m.group("base").strip()
    rarity = m.group("rarity").strip()
    return base, rarity


def infer_rarity_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    if "-" not in stem:
        return ""
    tail = stem.rsplit("-", 1)[-1]
    return official_normalize_rarity_token(tail)


def parse_official_cardlist_items(html: str, expansion: str, wanted_cardnos: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    items: List[Dict[str, Any]] = []
    seen: Set[Tuple[str, str, str]] = set()

    for node in soup.select(".cardlist-Result_Item.image-Item[card]"):
        display_card = (node.get("card") or "").strip()
        if not display_card:
            continue
        base_cardno, rarity_display = split_display_card_and_rarity(display_card)
        if wanted_cardnos is not None and base_cardno not in wanted_cardnos:
            continue
        img = node.find("img")
        if not img:
            continue
        src = (img.get("src") or "").strip()
        if not src:
            continue
        parsed = urllib.parse.urlparse(src)
        remote_filename = Path(urllib.parse.unquote(parsed.path)).name
        if not remote_filename:
            continue
        rarity_norm = infer_rarity_from_filename(remote_filename) or official_normalize_rarity_token(rarity_display)
        folder = expansion
        # If the live src already contains the /cardlist/<folder>/ segment, trust it.
        mm = re.search(r"/cardlist/([^/]+)/[^/]+$", parsed.path)
        if mm:
            folder = mm.group(1)
        exact_url = f"{OFFICIAL_BASE_URL}/wordpress/wp-content/images/cardlist/{folder}/{remote_filename}"
        key = (base_cardno, rarity_norm, remote_filename)
        if key in seen:
            continue
        seen.add(key)
        items.append({
            "cardnumber": base_cardno,
            "card_attr": display_card,
            "rarity_display": rarity_display,
            "rarity_norm": rarity_norm,
            "folder": folder,
            "remote_filename": remote_filename,
            "exact_url": exact_url,
        })
    return items


def extract_official_max_page(html: str) -> int:
    m = re.search(r"max_page\s*=\s*([0-9]+)", html)
    if not m:
        return 1
    try:
        return max(1, int(m.group(1)))
    except Exception:
        return 1


def load_cardnumbers_from_db(db_json: Optional[Path], db_csv: Optional[Path]) -> List[str]:
    out: List[str] = []
    if db_json and db_json.exists():
        try:
            data = json.loads(db_json.read_text(encoding="utf-8"))
            rows = data if isinstance(data, list) else data.get("cards", data)
            if isinstance(rows, list):
                for r in rows:
                    if isinstance(r, dict):
                        cn = r.get("cardnumber")
                        if isinstance(cn, str) and cn.strip():
                            out.append(cn.strip())
        except Exception:
            pass
    if (not out) and db_csv and db_csv.exists():
        try:
            df = pd.read_csv(db_csv)
            if "cardnumber" in df.columns:
                out.extend([str(x).strip() for x in df["cardnumber"].dropna().tolist() if str(x).strip()])
        except Exception:
            pass
    # de-dup keep order
    seen = set()
    uniq: List[str] = []
    for cn in out:
        if cn not in seen:
            uniq.append(cn)
            seen.add(cn)
    return uniq


def cmd_official_image_manifest(
    db_json: Optional[Path],
    db_csv: Optional[Path],
    outdir: Path,
    cache_dir: Path,
    delay: float,
    user_agent: str,
    timeout: float = 25.0,
    per_card_fallback: bool = True,
) -> Path:
    wanted_cardnos = load_cardnumbers_from_db(db_json, db_csv)
    if not wanted_cardnos:
        raise SystemExit("[ERROR] no cardnumber rows found for official image manifest generation")

    wanted_set = set(wanted_cardnos)
    expansion_to_cards: Dict[str, Set[str]] = {}
    unmatched: List[str] = []
    for cn in wanted_cardnos:
        exp = official_expansion_from_cardno(cn)
        if exp:
            expansion_to_cards.setdefault(exp, set()).add(cn)
        else:
            unmatched.append(cn)

    cards_map: Dict[str, List[Dict[str, Any]]] = {}
    expansions_summary: Dict[str, Any] = {}

    def push_items(items: List[Dict[str, Any]]) -> None:
        for item in items:
            cn = item["cardnumber"]
            cards_map.setdefault(cn, [])
            key = (item["rarity_norm"], item["remote_filename"], item["folder"])
            seen_keys = {(x["rarity_norm"], x["remote_filename"], x["folder"]) for x in cards_map[cn]}
            if key not in seen_keys:
                cards_map[cn].append(item)

    for expansion in sorted(expansion_to_cards.keys()):
        first_url = f"{OFFICIAL_CARDLIST_SEARCH_URL}?expansion={urllib.parse.quote(expansion)}&view=image&sort=new"
        html = fetch(first_url, cache_dir, delay=delay, user_agent=user_agent, timeout=timeout)
        page_items = parse_official_cardlist_items(html, expansion, wanted_cardnos=expansion_to_cards[expansion])
        push_items(page_items)
        max_page = extract_official_max_page(html)
        pages_done = 1
        if max_page >= 2:
            for page in range(2, max_page + 1):
                more_url = f"{OFFICIAL_CARDLIST_MORE_URL}?expansion={urllib.parse.quote(expansion)}&view=image&page={page}"
                more_html = fetch(more_url, cache_dir, delay=delay, user_agent=user_agent, timeout=timeout)
                push_items(parse_official_cardlist_items(more_html, expansion, wanted_cardnos=expansion_to_cards[expansion]))
                pages_done += 1
        expansions_summary[expansion] = {
            "cards_wanted": len(expansion_to_cards[expansion]),
            "pages_fetched": pages_done,
            "max_page": max_page,
        }

    missing_after_expansion = [cn for cn in wanted_cardnos if cn not in cards_map]
    # per-card fallback is reserved for unmatched prefixes / stubborn misses (PR etc.)
    if per_card_fallback and missing_after_expansion:
        for cn in missing_after_expansion:
            url = f"{OFFICIAL_CARDLIST_SEARCH_URL}?cardno={urllib.parse.quote(cn)}&view=image&sort=new"
            try:
                html = fetch(url, cache_dir, delay=delay, user_agent=user_agent, timeout=timeout)
            except Exception:
                continue
            push_items(parse_official_cardlist_items(html, official_expansion_from_cardno(cn) or "UNKNOWN", wanted_cardnos={cn}))

    manifest = {
        "version": 1,
        "source": "official_cardlist",
        "generated_from": {
            "db_json": str(db_json) if db_json else "",
            "db_csv": str(db_csv) if db_csv else "",
        },
        "base_url": f"{OFFICIAL_BASE_URL}/wordpress/wp-content/images/cardlist",
        "cards_total_in_db": len(wanted_cardnos),
        "cards_with_manifest": len(cards_map),
        "cards_missing_manifest": len([cn for cn in wanted_cardnos if cn not in cards_map]),
        "expansions": expansions_summary,
        "cards": {cn: cards_map.get(cn, []) for cn in wanted_cardnos if cards_map.get(cn)},
    }

    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / "official_image_manifest.json"
    out_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # also emit a compact TSV for quick inspection / grep
    flat_rows: List[Dict[str, Any]] = []
    for cn, entries in manifest["cards"].items():
        for e in entries:
            flat_rows.append({
                "cardnumber": cn,
                "rarity_norm": e.get("rarity_norm", ""),
                "rarity_display": e.get("rarity_display", ""),
                "folder": e.get("folder", ""),
                "remote_filename": e.get("remote_filename", ""),
                "exact_url": e.get("exact_url", ""),
            })
    flat_path = outdir / "official_image_manifest.tsv"
    pd.DataFrame(flat_rows).to_csv(flat_path, index=False, encoding="utf-8-sig", sep="\t")
    print(f"[DONE] official image manifest -> {out_path}")
    print(f"[DONE] official image manifest TSV -> {flat_path}")
    return out_path


def sha_path(cache_dir: Path, url: str) -> Path:
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]
    return cache_dir / f"{h}.html"


def fetch(url: str, cache_dir: Path, delay: float, user_agent: str, timeout: float = 25.0) -> str:
    cache_dir.mkdir(parents=True, exist_ok=True)
    p = sha_path(cache_dir, url)
    if p.exists():
        return p.read_text(encoding="utf-8", errors="ignore")
    time.sleep(delay)
    r = requests.get(url, headers={"User-Agent": user_agent}, timeout=timeout)
    r.raise_for_status()
    html = r.text
    p.write_text(html, encoding="utf-8")
    return html


def norm_url(href: str) -> Optional[str]:
    if not href:
        return None
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/llocardgame/"):
        return "https://wikiwiki.jp" + href
    return None


def cardno_name_from_url(url: str) -> Tuple[str, str]:
    try:
        seg = url.split("/llocardgame/")[-1]
        seg = seg.split("#")[0].split("?")[0]
        seg = urllib.parse.unquote(seg)
        parts = seg.split(" ", 1)
        cardno = parts[0].strip()
        name = parts[1].strip() if len(parts) == 2 else ""
        return cardno, name
    except Exception:
        return "", ""


def replace_icons(node: Tag) -> None:
    for img in list(node.find_all("img")):
        alt = (img.get("alt") or img.get("title") or "").strip()
        if not alt:
            src = (img.get("src") or "").split("/")[-1]
            alt = src or "ICON"
        img.replace_with(f"<{alt}>")


def cell_text(cell: Tag) -> str:
    frag = BeautifulSoup(str(cell), "lxml")
    c = frag.find(["th", "td"]) or frag
    replace_icons(c)
    return c.get_text(" ", strip=True)


def normalize_key(k: str) -> str:
    if not k:
        return ""
    k = k.replace("　", " ")
    k = re.sub(r"\s+", "", k)
    k = k.replace("：", "").replace(":", "").replace("・", "")
    return k.strip()


def map_key(k_norm: str) -> Optional[str]:
    if not k_norm:
        return None
    if k_norm in KEY_MAP_EXACT:
        return KEY_MAP_EXACT[k_norm]
    for needle, col in KEY_MAP_CONTAINS:
        if needle in k_norm:
            return col
    return None


def parse_info_table(soup: BeautifulSoup, key_set: Set[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = tr.find_all(["th", "td"], recursive=True)
            if len(cells) < 2:
                continue
            k_raw = cell_text(cells[0])
            v_raw = cell_text(cells[1])
            k_norm = normalize_key(k_raw)
            if not k_norm:
                continue
            key_set.add(k_norm)

            col = map_key(k_norm)
            if not col:
                continue

            if col in {"cost", "blade", "score"}:
                mm = re.search(r"(\d+)", v_raw.translate(FW_DIGITS))
                out[col] = mm.group(1) if mm else ""
            else:
                out[col] = v_raw

    # guard
    if out.get("blade_heart", "") == "効果テキスト":
        out["blade_heart"] = ""
    return out


def main_container(soup: BeautifulSoup) -> Tag:
    return soup.find(id="content") or soup.find(id="body") or soup


def soup_main_text(soup: BeautifulSoup) -> str:
    main = main_container(soup)
    replace_icons(main)
    return main.get_text("\n", strip=True)


def extract_effect_text(main_text: str) -> str:
    lines = [ln.strip() for ln in main_text.splitlines() if ln.strip()]
    start_idx = None
    for s in START_MARKERS:
        if s in lines:
            start_idx = lines.index(s) + 1
            break
    if start_idx is None:
        return ""
    out: List[str] = []
    for i in range(start_idx, len(lines)):
        ln = lines[i]
        if ln.startswith("▼") and i > start_idx:
            break
        if ln in STOP_HEADINGS:
            break
        if ln.startswith("最終更新") or ln.startswith("広告") or ln.startswith("これらのキーワード"):
            continue
        out.append(ln)
    return "\n".join(out).strip()


def parse_heart_expr(raw: str) -> Tuple[Dict[str, int], Optional[int], List[str]]:
    counts: Dict[str, int] = {}
    tags: List[str] = []
    if not raw or not isinstance(raw, str):
        return counts, None, tags

    s = raw.translate(FW_DIGITS)
    m_total = TOTAL_RE.search(s)
    total = int(m_total.group(1)) if m_total else None

    for m in ICON_COUNT_RE.finditer(s):
        token = f"({m.group(1)})"
        n = int(m.group(2)) if m.group(2) else 1
        if token in COLOR_MAP:
            key = COLOR_MAP[token]
            counts[key] = counts.get(key, 0) + n
        else:
            tags.append(token)
    return counts, total, tags


def _has_text_value(v: Any) -> bool:
    if v is None:
        return False
    try:
        s = str(v).strip()
    except Exception:
        return False
    if not s:
        return False
    return s not in {"nan", "None", "null"}


def _canonical_card_type_raw(norm: str) -> str:
    return {
        "LIVE": "ライブ",
        "MEMBER": "メンバー",
        "EVENT": "イベント",
        "SUPPORT": "サポート",
    }.get((norm or "").strip().upper(), "")


def norm_card_type(raw: str) -> str:
    if not raw:
        return ""
    s = str(raw).strip()
    if "ライブ" in s:
        return "LIVE"
    if "メンバー" in s:
        return "MEMBER"
    if "イベント" in s:
        return "EVENT"
    if "サポート" in s:
        return "SUPPORT"
    return s


def infer_card_type(raw: Any, required_hearts_raw: Any = "", score: Any = "", cost: Any = "", blade: Any = "", base_hearts_raw: Any = "") -> Tuple[str, str]:
    raw_norm = norm_card_type(str(raw or ""))

    # Explicit non-member/live types stay authoritative.
    if raw_norm in {"EVENT", "SUPPORT"}:
        return raw_norm, _canonical_card_type_raw(raw_norm)

    has_live_signals = _has_text_value(required_hearts_raw) or _has_text_value(score)
    has_member_signals = _has_text_value(cost) or _has_text_value(blade) or _has_text_value(base_hearts_raw)

    inferred = raw_norm
    if has_live_signals and not has_member_signals:
        inferred = "LIVE"
    elif has_member_signals and not has_live_signals:
        inferred = "MEMBER"
    elif not inferred:
        if has_live_signals:
            inferred = "LIVE"
        elif has_member_signals:
            inferred = "MEMBER"

    canonical_raw = _canonical_card_type_raw(inferred) if inferred in {"LIVE", "MEMBER", "EVENT", "SUPPORT"} else str(raw or "")
    return inferred, canonical_raw


def normalize_effect_text(effect_text: str) -> str:
    if not effect_text or not isinstance(effect_text, str):
        return ""
    s = effect_text.translate(FW_DIGITS)
    s = s.replace("×", "x").replace("ｘ", "x").replace("Ｘ", "X")
    s = re.sub(r"(<\([^)]+\)>)\s*(?:x|X)\s*(\d+)", r"\1\2", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s).strip()
    return s


def classify_effect_text_status(effect_text_raw: Any, effect_text_norm: Any = "") -> str:
    raw = normalize_effect_text(effect_text_raw) if isinstance(effect_text_raw, str) else ""
    norm = normalize_effect_text(effect_text_norm) if isinstance(effect_text_norm, str) else ""
    s = norm or raw
    return "NO_ABILITY" if s in NO_ABILITY_MARKERS else "HAS_TEXT"


def extract_effect_tokens(effect_text_norm: str) -> Dict[str, Any]:
    tokens: Dict[str, Any] = {"hearts": {}, "blade_mentions": []}
    if not effect_text_norm:
        return tokens
    s = effect_text_norm

    for m in ICON_COUNT_RE.finditer(s):
        token = f"({m.group(1)})"
        n = int(m.group(2)) if m.group(2) else 1
        if token in COLOR_MAP:
            key = COLOR_MAP[token]
            tokens["hearts"][key] = tokens["hearts"].get(key, 0) + n
        else:
            tokens.setdefault("tags", []).append(token)
    return tokens


def extract_product_urls(products_html: str, products_url: str) -> List[str]:
    soup = BeautifulSoup(products_html, "lxml")
    urls: Set[str] = set()
    for a in soup.find_all("a", href=True):
        u = norm_url(a["href"])
        if not u:
            continue
        if "/::cmd/" in u:
            continue
        if "wikiwiki.jp/llocardgame/" in u:
            urls.add(u)
    urls.discard(products_url)
    return sorted(urls)


def extract_card_links_from_product(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    urls: Set[str] = set()
    for a in soup.find_all("a", href=True):
        u = norm_url(a["href"])
        if not u or "/::cmd/" in u:
            continue
        cardno, _ = cardno_name_from_url(u)
        if CARDNO_IN_TEXT.match(cardno):
            urls.add(u)
    return sorted(urls)


def parse_card_page(url: str, html: str, key_set: Set[str], do_normalize: bool) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    title = soup.find("title").get_text(strip=True) if soup.find("title") else ""
    cardno_u, name_u = cardno_name_from_url(url)

    info = parse_info_table(soup, key_set)
    main_text = soup_main_text(soup)
    effect_text = extract_effect_text(main_text)

    card_type_raw = info.get("card_type", "")
    base_raw = info.get("base_hearts", "")
    req_raw = info.get("required_hearts", "")
    bh_raw = info.get("blade_heart", "")

    rec: Dict[str, Any] = {
        "cardnumber": cardno_u,
        "cardname": name_u,
        "page_title": title,
        "card_type_raw": card_type_raw,
        "work_title": info.get("work_title", ""),
        "group": info.get("group", ""),
        "unit": info.get("unit", ""),
        "cost": info.get("cost", ""),
        "blade": info.get("blade", ""),
        "blade_heart_raw": bh_raw,
        "base_hearts_raw": base_raw,
        "required_hearts_raw": req_raw,
        "score": info.get("score", ""),
        "effect_text_raw": effect_text,
        "source_url": url,
    }

    if do_normalize:
        inferred_type, canonical_raw = infer_card_type(
            card_type_raw,
            required_hearts_raw=req_raw,
            score=info.get("score", ""),
            cost=info.get("cost", ""),
            blade=info.get("blade", ""),
            base_hearts_raw=base_raw,
        )
        rec["card_type_raw"] = canonical_raw or card_type_raw
        rec["card_type_norm"] = inferred_type

        base_counts, base_total, base_tags = parse_heart_expr(base_raw)
        req_counts, req_total, req_tags = parse_heart_expr(req_raw)
        bh_counts, bh_total, bh_tags = parse_heart_expr(bh_raw)

        rec["base_hearts_counts_json"] = json.dumps(base_counts, ensure_ascii=False)
        rec["base_hearts_total"] = base_total if base_total is not None else sum(base_counts.values())
        rec["base_hearts_tags_json"] = json.dumps(base_tags, ensure_ascii=False)

        rec["required_hearts_counts_json"] = json.dumps(req_counts, ensure_ascii=False)
        rec["required_hearts_total"] = req_total if req_total is not None else sum(req_counts.values())
        rec["required_hearts_tags_json"] = json.dumps(req_tags, ensure_ascii=False)

        rec["blade_heart_counts_json"] = json.dumps(bh_counts, ensure_ascii=False)
        rec["blade_heart_total"] = bh_total if bh_total is not None else sum(bh_counts.values())
        rec["blade_heart_tags_json"] = json.dumps(bh_tags, ensure_ascii=False)

        eff_norm = normalize_effect_text(effect_text)
        eff_status = classify_effect_text_status(effect_text, eff_norm)
        rec["effect_text_norm"] = eff_norm
        rec["effect_text_status"] = eff_status
        rec["effect_text_is_no_ability"] = 1 if eff_status == "NO_ABILITY" else 0
        rec["effect_tokens_json"] = json.dumps(extract_effect_tokens(eff_norm), ensure_ascii=False)

    return rec


def load_resume_urls(resume_csv: Path, resume_json: Path) -> Set[str]:
    urls: Set[str] = set()
    if resume_csv.exists():
        try:
            df = pd.read_csv(resume_csv)
            if "source_url" in df.columns:
                urls.update([u for u in df["source_url"].dropna().astype(str).tolist() if u])
        except Exception:
            pass
    if resume_json.exists():
        try:
            data = json.loads(resume_json.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for r in data:
                    if isinstance(r, dict) and r.get("source_url"):
                        urls.add(str(r["source_url"]))
        except Exception:
            pass
    return urls


def finalize_outputs(outdir: Path, records: List[Dict[str, Any]], keys_found: Set[str], failed: List[str]) -> Tuple[Path, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    if "source_url" in df.columns:
        df = df.drop_duplicates(subset=["source_url"], keep="last")
    if "cardnumber" in df.columns:
        df = df.drop_duplicates(subset=["cardnumber"], keep="last")

    out_json = outdir / "cards_min.json"
    out_csv = outdir / "cards_min.csv"
    out_json.write_text(json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2), encoding="utf-8")
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    if keys_found:
        (outdir / "keys_found.txt").write_text("\n".join(sorted(keys_found)), encoding="utf-8")
    if failed:
        (outdir / "failed_urls.txt").write_text("\n".join(failed), encoding="utf-8")
    return out_csv, out_json


def cmd_scrape(products_url: str, outdir: Path, cache_dir: Path, delay: float,
              checkpoint_every: int, max_fail: int, user_agent: str,
              limit_products: int = 0, limit_cards: int = 0, no_normalize: bool = False) -> Tuple[Path, Path]:

    outdir.mkdir(parents=True, exist_ok=True)
    resume_csv = outdir / "cards_min.csv"
    resume_json = outdir / "cards_min.json"
    resume_urls = load_resume_urls(resume_csv, resume_json)

    records: List[Dict[str, Any]] = []
    keys_found: Set[str] = set()
    failed: List[str] = []

    prod_html = fetch(products_url, cache_dir, delay=delay, user_agent=user_agent)
    product_urls = extract_product_urls(prod_html, products_url)
    if limit_products:
        product_urls = product_urls[:limit_products]
    print(f"[INFO] product pages: {len(product_urls)}")

    card_urls: Set[str] = set()
    for i, pu in enumerate(product_urls, 1):
        try:
            h = fetch(pu, cache_dir, delay=delay, user_agent=user_agent)
            card_urls.update(extract_card_links_from_product(h))
        except Exception as e:
            failed.append(pu)
            print(f"[WARN] product fetch failed: {pu} ({e})")
            if len(failed) >= max_fail:
                raise SystemExit("[ERROR] too many failures")
        if i % 20 == 0:
            print(f"[INFO] processed products {i}/{len(product_urls)}")

    card_list = sorted(card_urls)
    if limit_cards:
        card_list = card_list[:limit_cards]
    print(f"[INFO] card pages: {len(card_list)}")

    todo = [u for u in card_list if u not in resume_urls]
    print(f"[INFO] to process: {len(todo)}")

    since_ck = 0
    for idx, cu in enumerate(todo, 1):
        try:
            h = fetch(cu, cache_dir, delay=delay, user_agent=user_agent)
            rec = parse_card_page(cu, h, keys_found, do_normalize=(not no_normalize))
            records.append(rec)
        except Exception as e:
            failed.append(cu)
            print(f"[WARN] card fetch failed: {cu} ({e})")
            if len(failed) >= max_fail:
                raise SystemExit("[ERROR] too many failures")

        since_ck += 1
        if checkpoint_every and since_ck >= checkpoint_every:
            pd.DataFrame(records).to_csv(outdir / "cards_min_checkpoint.csv", index=False, encoding="utf-8-sig")
            since_ck = 0
            print(f"[INFO] checkpoint: records={len(records)} failed={len(failed)}")

        if idx % 200 == 0:
            print(f"[INFO] processed cards {idx}/{len(todo)}")

    out_csv, out_json = finalize_outputs(outdir, records, keys_found, failed)
    print("[DONE] records=", len(pd.read_csv(out_csv)))
    print("  CSV :", out_csv)
    print("  JSON:", out_json)
    return out_csv, out_json


# -------------------------
# normalize (postprocess)
# -------------------------
def safe_json_loads(s: Any) -> Tuple[bool, Any]:
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return True, None
    if not isinstance(s, str):
        return False, None
    ss = s.strip()
    if ss == "":
        return True, None
    try:
        return True, json.loads(ss)
    except Exception:
        return False, None


def normalize_tag(tag: str) -> str:
    t = tag.strip()
    t = t.translate(FW_DIGITS).translate(PLUS_MINUS_MAP)
    t = re.sub(r"\s+", "", t)
    return t


def process_tokens(obj: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(obj, dict):
        obj = {}

    tags = obj.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    blade_icon_n = int(obj.get("blade_icon_n", 0) or 0)
    energy_icon_n = int(obj.get("energy_icon_n", 0) or 0)
    all_heart_n = int(obj.get("all_heart_n", 0) or 0)
    score_delta_icon = int(obj.get("score_delta_icon", 0) or 0)

    unknown: List[str] = []
    for raw in tags:
        if not isinstance(raw, str) or not raw.strip():
            continue
        t = normalize_tag(raw)

        if t in KNOWN_SIMPLE:
            key = KNOWN_SIMPLE[t]
            if key == "blade_icon_n":
                blade_icon_n += 1
            elif key == "energy_icon_n":
                energy_icon_n += 1
            elif key == "all_heart_n":
                all_heart_n += 1
            continue

        m = SCORE_TAG_RE.match(t)
        if m:
            sign = m.group(1).translate(PLUS_MINUS_MAP)
            n = int(m.group(2).translate(FW_DIGITS))
            score_delta_icon += (n if sign == "+" else -n)
            continue

        unknown.append(t)

    obj["blade_icon_n"] = blade_icon_n
    obj["energy_icon_n"] = energy_icon_n
    obj["all_heart_n"] = all_heart_n
    obj["score_delta_icon"] = score_delta_icon
    obj["unknown_tags"] = unknown
    obj["tags"] = unknown
    return obj


def cmd_normalize(csv_path: Path, json_path: Optional[Path], outdir: Path, suffix: str) -> Tuple[Path, Optional[Path]]:
    df = pd.read_csv(csv_path)
    if "effect_tokens_json" not in df.columns:
        raise SystemExit("[ERROR] effect_tokens_json not found")

    new_tokens_json = []
    tok_blade, tok_energy, tok_all, tok_score_delta, tok_unknown_n = [], [], [], [], []
    effect_statuses, effect_no_ability_flags = [], []
    repaired_type_norms, repaired_type_raws = [], []
    bad_json = 0

    eff_norm_series = df["effect_text_norm"].tolist() if "effect_text_norm" in df.columns else [""] * len(df)

    req_series = df["required_hearts_raw"].tolist() if "required_hearts_raw" in df.columns else [""] * len(df)
    score_series = df["score"].tolist() if "score" in df.columns else [""] * len(df)
    cost_series = df["cost"].tolist() if "cost" in df.columns else [""] * len(df)
    blade_series = df["blade"].tolist() if "blade" in df.columns else [""] * len(df)
    base_series = df["base_hearts_raw"].tolist() if "base_hearts_raw" in df.columns else [""] * len(df)
    raw_type_series = df["card_type_raw"].tolist() if "card_type_raw" in df.columns else [""] * len(df)

    for s, eff_norm, req_raw, score, cost, blade, base_raw, raw_type in zip(
        df["effect_tokens_json"].tolist(),
        eff_norm_series,
        req_series,
        score_series,
        cost_series,
        blade_series,
        base_series,
        raw_type_series,
    ):
        ok, obj = safe_json_loads(s)
        if (not ok) or (obj is None) or (not isinstance(obj, dict)):
            bad_json += 1
            obj = {}
        obj2 = process_tokens(obj)

        tok_blade.append(int(obj2.get("blade_icon_n", 0) or 0))
        tok_energy.append(int(obj2.get("energy_icon_n", 0) or 0))
        tok_all.append(int(obj2.get("all_heart_n", 0) or 0))
        tok_score_delta.append(int(obj2.get("score_delta_icon", 0) or 0))
        unk = obj2.get("unknown_tags", [])
        tok_unknown_n.append(len(unk) if isinstance(unk, list) else 0)

        new_tokens_json.append(json.dumps(obj2, ensure_ascii=False))
        st = classify_effect_text_status(eff_norm, eff_norm)
        effect_statuses.append(st)
        effect_no_ability_flags.append(1 if st == "NO_ABILITY" else 0)

        inferred_type, canonical_raw = infer_card_type(
            raw_type,
            required_hearts_raw=req_raw,
            score=score,
            cost=cost,
            blade=blade,
            base_hearts_raw=base_raw,
        )
        repaired_type_norms.append(inferred_type)
        repaired_type_raws.append(canonical_raw or str(raw_type or ""))

    df["effect_tokens_json"] = new_tokens_json
    df["effect_text_status"] = effect_statuses
    df["effect_text_is_no_ability"] = effect_no_ability_flags
    df["card_type_norm"] = repaired_type_norms
    df["card_type_raw"] = repaired_type_raws
    df["tok_blade_icon_n"] = tok_blade
    df["tok_energy_icon_n"] = tok_energy
    df["tok_all_heart_n"] = tok_all
    df["tok_score_delta_icon"] = tok_score_delta
    df["tok_unknown_tags_n"] = tok_unknown_n

    outdir.mkdir(parents=True, exist_ok=True)
    out_csv = outdir / f"{csv_path.stem}{suffix}.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"[DONE] wrote: {out_csv} (bad_json={bad_json})")

    out_json = None
    if json_path and json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for r in data:
                    if not isinstance(r, dict):
                        continue
                    ok, obj = safe_json_loads(r.get("effect_tokens_json", ""))
                    if (not ok) or (obj is None) or (not isinstance(obj, dict)):
                        obj = {}
                    r["effect_tokens_json"] = json.dumps(process_tokens(obj), ensure_ascii=False)
                    inferred_type, canonical_raw = infer_card_type(
                        r.get("card_type_raw", ""),
                        required_hearts_raw=r.get("required_hearts_raw", ""),
                        score=r.get("score", ""),
                        cost=r.get("cost", ""),
                        blade=r.get("blade", ""),
                        base_hearts_raw=r.get("base_hearts_raw", ""),
                    )
                    r["card_type_norm"] = inferred_type
                    r["card_type_raw"] = canonical_raw or str(r.get("card_type_raw", "") or "")
                out_json = outdir / f"{json_path.stem}{suffix}.json"
                out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"[DONE] wrote: {out_json}")
        except Exception as e:
            print(f"[WARN] failed to update json: {e}")

    return out_csv, out_json


# -------------------------
# mine templates
# -------------------------
def canonicalize_effect(s: str) -> str:
    if not isinstance(s, str) or not s.strip():
        return ""
    t = s.strip()
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n+", "\n", t)
    t = re.sub(r"<\(([^)]+)\)>\s*(\d+)", r"<(\1)>{n}", t)
    t = re.sub(r"(?<![<{])\b\d+\b", "{n}", t)
    t = re.sub(r"(\D)\d+(\D)", lambda m: f"{m.group(1)}{{n}}{m.group(2)}", t)
    t = t.replace("{n}{n}", "{n}")
    t = t.replace("＋", "+").replace("－", "-")
    return t


def split_trigger_blocks(effect_text_norm: str) -> List[Dict[str, Any]]:
    """
    Robust two-level parsing for abilities.

    Output blocks:
      - ability_type: 自動 / 起動 / 常時 (or UNKNOWN)
      - trigger: 自動の下位カテゴリ（登場時/ライブ開始時/ライブ成功時/…）または "BODY"
      - conditions: センター/ライト/レフト/ターンn回 等の条件ヘッダ（triggerではない）
      - text: ブロック本文

    Key rule (your spec):
      効果カテゴリには「起動」「常時」「自動」「登場時」「ライブ開始時」「ライブ成功時」があり、
      「登場時/ライブ開始時/ライブ成功時」はすべて「自動」に包含される（短縮記法）。
      したがって、イベント系カテゴリ（登場時/ライブ開始時/ライブ成功時/～時）を見たら
      そのブロックは必ず ability_type="自動" として開始する（直前が起動/常時でも上書き）。

    Supported header forms when a line is *only* the header:
      <...> / ＜...＞ / 〈...〉 / 《...》 / 【...】 / [...] / （...）
    """
    if not isinstance(effect_text_norm, str) or not effect_text_norm.strip():
        return []

    # normalize common bracket variants to simplify detection
    t = effect_text_norm
    t = t.replace("＜", "<").replace("＞", ">")
    t = t.replace("〈", "<").replace("〉", ">")
    t = t.replace("《", "<").replace("》", ">")
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]

    ability_headers = {"自動", "起動", "常時"}

    # auto sub-triggers (shorthand categories)
    auto_triggers = {
        "登場時", "登場した時", "登場",
        "ライブ開始時", "ライブ成功時", "ライブ終了時", "ライブ中",
        "ターン開始時", "ターン終了時",
        "アタック時", "アタックした時",
    }

    known_conditions = {"センター", "ライト", "レフト"}
    turn_n_re = re.compile(r"^ターン\s*[0-9０-９]+\s*回$")

    # heuristic for trigger headers
    eventish_re = re.compile(r"(開始時|成功時|終了時|した時|時$)")

    def classify_header(h: str) -> Tuple[str, str]:
        h = h.strip()
        # ability
        if h in ability_headers:
            return ("ability", h)
        if h.startswith("自動"):
            return ("ability", "自動")
        if h.startswith("起動"):
            return ("ability", "起動")
        if h.startswith("常時"):
            return ("ability", "常時")

        # conditions
        if h in known_conditions or turn_n_re.match(h):
            return ("condition", h)

        # triggers (auto shorthand)
        if h in auto_triggers:
            return ("trigger", h)
        if eventish_re.search(h):
            return ("trigger", h)

        return ("condition", h)

    # header line matchers
    header_angle = re.compile(r"^<([^<>]+)>$")
    header_kakko = re.compile(r"^[\[\【\（]([^\]\】\）]+)[\]\】\）]$")

    def parse_header_line(ln: str) -> Optional[str]:
        m = header_angle.match(ln)
        if m and not ln.startswith("<("):  # exclude icons like <(桃)>
            return m.group(1).strip()
        m = header_kakko.match(ln)
        if m:
            return m.group(1).strip()
        return None

    blocks: List[Dict[str, Any]] = []
    cur_ability = "UNKNOWN"
    cur_trigger = "BODY"
    cur_conditions: List[str] = []
    cur_lines: List[str] = []

    def flush():
        nonlocal cur_lines
        if cur_lines:
            inferred = cur_ability
            if inferred == "UNKNOWN" and cur_trigger != "BODY":
                inferred = "自動"
            blocks.append({
                "ability_type": inferred,
                "trigger": cur_trigger,
                "conditions": list(cur_conditions),
                "text": "\n".join(cur_lines).strip(),
            })
        cur_lines = []

    for ln in lines:
        h = parse_header_line(ln)
        if h is not None:
            kind, val = classify_header(h)

            if kind == "ability":
                flush()
                cur_ability = val
                cur_trigger = "BODY"
                cur_conditions = []
                continue

            if kind == "trigger":
                flush()
                # IMPORTANT: triggerカテゴリは自動の短縮記法なので必ず自動にする
                cur_ability = "自動"
                cur_trigger = val
                cur_conditions = []
                continue

            # condition
            flush()
            cur_conditions.append(val)
            continue

        cur_lines.append(ln)

    flush()
    return blocks


def split_cost_effect_clauses(block_text: str) -> List[Dict[str, Any]]:
    """
    Split block text into clauses. A clause may contain cost/effect split by '：' or ':'.

    Why a cost sentence may be split into two:
      The wiki often inserts <br> inside one sentence (visual wrap),
      so our line-based splitter treated it as two separate clauses.

    Fix:
      We do a "soft-wrap merge" pass:
        - If a line does NOT contain a separator and
        - The previous line looks unfinished (ends with particles like 'から','を','に','へ','の','と','して' etc.),
          then we concatenate them.

    Also trims leading punctuation artifacts on clause texts.
    """
    if not isinstance(block_text, str) or not block_text.strip():
        return []

    raw_lines = [ln.strip() for ln in block_text.splitlines() if ln.strip()]

    def clean_leading_punct(s: str) -> str:
        if not s:
            return s
        return s.lstrip("、。,.，・ ")

    merge_tail = ("から", "を", "に", "へ", "の", "と", "して", "または", "および", "及び")
    merged: List[str] = []
    for ln in raw_lines:
        if not merged:
            merged.append(ln)
            continue
        prev = merged[-1]
        has_sep_prev = ("：" in prev) or (":" in prev)
        has_sep_ln = ("：" in ln) or (":" in ln)
        if (not has_sep_prev) and (not has_sep_ln) and any(prev.endswith(t) for t in merge_tail) and not ln.startswith("<"):
            merged[-1] = prev + ln
        else:
            merged.append(ln)

    clauses: List[Dict[str, Any]] = []
    for ln in merged:
        sep = "：" if "：" in ln else (":" if ":" in ln else None)
        if sep:
            left, right = ln.split(sep, 1)
            left = left.strip()
            right = right.strip()
            optional = ("してもよい" in left) or ("してもよい" in ln)
            clauses.append({
                "optional": optional,
                "cost_text": clean_leading_punct(left),
                "effect_text": clean_leading_punct(right),
                "raw": ln,
            })
        else:
            clauses.append({
                "optional": ("してもよい" in ln),
                "cost_text": "",
                "effect_text": clean_leading_punct(ln),
                "raw": ln,
            })
    return clauses


# --- filter extraction: group/unit/work/card_kind/cost constraints ---
GROUP_ALIASES = {
    "Aqours": "Aqours",
    "μ's": "Muse",
    "μｓ": "Muse",
    "ミューズ": "Muse",
    "Liella!": "Liella",
    "Liella": "Liella",
    "虹ヶ咲": "Nijigasaki",
    "虹ヶ咲学園": "Nijigasaki",
    "蓮ノ空": "Hasunosora",
    "蓮ノ空女学院": "Hasunosora",
}

UNIT_ALIASES = {
    # Aqours
    "CYaRon!": "CYaRon",
    "AZALEA": "AZALEA",
    "Guilty Kiss": "GuiltyKiss",
    # μ's
    "Printemps": "Printemps",
    "lily white": "lilywhite",
    "BiBi": "BiBi",
    # Liella!
    "CatChu!": "CatChu",
    "KALEIDOSCORE": "KALEIDOSCORE",
    "5yncri5e!": "5yncri5e",
}

CARD_KIND_ALIASES = {
    "ライブカード": "LIVE",
    "ライブ": "LIVE",
    "メンバーカード": "MEMBER",
    "メンバー": "MEMBER",
    "イベントカード": "EVENT",
    "イベント": "EVENT",
    "サポートカード": "SUPPORT",
    "サポート": "SUPPORT",
}

COST_LE_RE = re.compile(r"コスト\s*([0-9]+)\s*以下")
COST_GE_RE = re.compile(r"コスト\s*([0-9]+)\s*以上")

def extract_filters(text: str) -> Dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        return {}
    f: Dict[str, Any] = {}

    groups = set()
    for k, v in GROUP_ALIASES.items():
        if k in text:
            groups.add(v)
    if groups:
        f["group"] = sorted(groups)

    units = set()
    for k, v in UNIT_ALIASES.items():
        if k in text:
            units.add(v)
    m = re.search(r"ユニット\s*「([^」]+)」", text)
    if m:
        units.add(m.group(1).strip())
    if units:
        f["unit"] = sorted(units)

    kinds = set()
    for k, v in CARD_KIND_ALIASES.items():
        if k in text:
            kinds.add(v)
    if kinds:
        f["card_kind"] = sorted(kinds)

    m = COST_LE_RE.search(text)
    if m:
        f["cost_le"] = int(m.group(1))
    m = COST_GE_RE.search(text)
    if m:
        f["cost_ge"] = int(m.group(1))

    return f


def cmd_mine(csv_path: Path, outdir: Path, top: int = 150) -> Dict[str, Path]:
    """
    Mine:
      - trigger frequency
      - cost clause templates
      - effect clause templates
    Also generates stub YAML for cost/effect clauses.
    """
    df = pd.read_csv(csv_path)
    if "effect_text_norm" not in df.columns:
        raise SystemExit("[ERROR] effect_text_norm not found")

    outdir.mkdir(parents=True, exist_ok=True)

    trigger_rows = []
    cost_rows = []
    eff_rows = []

    for _, r in df.iterrows():
        cardno = str(r.get("cardnumber", "") or "")
        name = str(r.get("cardname", "") or "")
        ctype = str(r.get("card_type_norm", "") or "")
        url = str(r.get("source_url", "") or "")
        et = r.get("effect_text_norm", "")
        blocks = split_trigger_blocks(et)
        for b in blocks:
            ability = b.get("ability_type","UNKNOWN")
            trig = b.get("trigger","BODY")
            conds = b.get("conditions", []) or []
            conds_s = ";".join([c for c in conds if isinstance(c,str) and c.strip()])
            txt = b["text"]
            trigger_rows.append({"ability_type": ability, "ability_type": ability,
                        "trigger": trig,
                        "conditions": conds_s, "cardnumber": cardno, "cardname": name, "card_type": ctype, "source_url": url})

            clauses = split_cost_effect_clauses(txt)
            for cl in clauses:
                optional = bool(cl.get("optional", False))
                cost_text = str(cl.get("cost_text", "") or "")
                eff_text = str(cl.get("effect_text", "") or "")

                cost_tmpl = canonicalize_effect(cost_text) if cost_text else ""
                eff_tmpl = canonicalize_effect(eff_text) if eff_text else ""

                filters = extract_filters(cost_text + " " + eff_text)
                g = ",".join(filters.get("group", [])) if isinstance(filters.get("group"), list) else ""
                u = ",".join(filters.get("unit", [])) if isinstance(filters.get("unit"), list) else ""
                k = ",".join(filters.get("card_kind", [])) if isinstance(filters.get("card_kind"), list) else ""
                cost_le = filters.get("cost_le", "")
                cost_ge = filters.get("cost_ge", "")

                if cost_tmpl:
                    cost_rows.append({
                        "ability_type": ability,
                        "trigger": trig,
                        "conditions": conds_s,
                        "optional": optional,
                        "cost_template": cost_tmpl,
                        "count": 1,
                        "example_cardnumber": cardno,
                        "example_cardname": name,
                        "example_card_type": ctype,
                        "example_cost_text": cost_text,
                        "filters_group": g,
                        "filters_unit": u,
                        "filters_card_kind": k,
                        "filters_cost_le": cost_le,
                        "filters_cost_ge": cost_ge,
                        "example_source_url": url,
                    })

                if eff_tmpl:
                    eff_rows.append({
                        "ability_type": ability,
                        "trigger": trig,
                        "conditions": conds_s,
                        "optional": optional,
                        "effect_template": eff_tmpl,
                        "count": 1,
                        "example_cardnumber": cardno,
                        "example_cardname": name,
                        "example_card_type": ctype,
                        "example_effect_text": eff_text,
                        "filters_group": g,
                        "filters_unit": u,
                        "filters_card_kind": k,
                        "filters_cost_le": cost_le,
                        "filters_cost_ge": cost_ge,
                        "example_source_url": url,
                    })

    trig_df = pd.DataFrame(trigger_rows)
    if len(trig_df):
        trig_counts = trig_df.groupby(["ability_type", "trigger"], dropna=False).size().reset_index(name="count")
        trig_counts = trig_counts.sort_values("count", ascending=False)
    else:
        trig_counts = pd.DataFrame(columns=["ability_type","trigger","count"])
    trig_out = trig_counts.head(top)
    trig_csv = outdir / f"trigger_top{top}.csv"
    trig_out.to_csv(trig_csv, index=False, encoding="utf-8-sig")

    if cost_rows:
        cdf = pd.DataFrame(cost_rows)
        gcols = ["ability_type", "trigger", "conditions", "optional", "cost_template", "filters_group", "filters_unit", "filters_card_kind", "filters_cost_le", "filters_cost_ge"]
        agg = cdf.groupby(gcols, dropna=False).agg(
            count=("count", "sum"),
            example_cardnumber=("example_cardnumber", "first"),
            example_cardname=("example_cardname", "first"),
            example_card_type=("example_card_type", "first"),
            example_cost_text=("example_cost_text", "first"),
            example_source_url=("example_source_url", "first"),
        ).reset_index()
        agg = agg.sort_values("count", ascending=False).head(top)
        cost_csv = outdir / f"cost_clause_template_top{top}.csv"
        agg.to_csv(cost_csv, index=False, encoding="utf-8-sig")
    else:
        cost_csv = outdir / f"cost_clause_template_top{top}.csv"
        pd.DataFrame([]).to_csv(cost_csv, index=False, encoding="utf-8-sig")

    if eff_rows:
        edf = pd.DataFrame(eff_rows)
        gcols = ["ability_type", "trigger", "conditions", "optional", "effect_template", "filters_group", "filters_unit", "filters_card_kind", "filters_cost_le", "filters_cost_ge"]
        agg = edf.groupby(gcols, dropna=False).agg(
            count=("count", "sum"),
            example_cardnumber=("example_cardnumber", "first"),
            example_cardname=("example_cardname", "first"),
            example_card_type=("example_card_type", "first"),
            example_effect_text=("example_effect_text", "first"),
            example_source_url=("example_source_url", "first"),
        ).reset_index()
        agg = agg.sort_values("count", ascending=False).head(top)
        eff_csv = outdir / f"effect_clause_template_top{top}.csv"
        agg.to_csv(eff_csv, index=False, encoding="utf-8-sig")
    else:
        eff_csv = outdir / f"effect_clause_template_top{top}.csv"
        pd.DataFrame([]).to_csv(eff_csv, index=False, encoding="utf-8-sig")

    def write_stub(kind: str, df_top: pd.DataFrame, template_col: str, example_col: str) -> Path:
        stub = []
        stub.append(f"# {kind}_patterns_stub.yaml")
        stub.append("# Auto-generated. Fill `action` and `params` for each template.")
        stub.append("version: 1")
        stub.append("patterns:")
        for i, row in df_top.reset_index(drop=True).iterrows():
            tmpl = str(row[template_col])
            cnt = int(row["count"])
            ability = str(row.get("ability_type","UNKNOWN"))
            trig = str(row.get("trigger",""))
            conds = str(row.get("conditions",""))
            opt = bool(row.get("optional", False))
            ex = str(row.get(example_col, "") or "")
            stub.append(f"  - id: {kind[:1].upper()}{i+1:03d}")
            stub.append(f"    count: {cnt}")
            stub.append(f"    ability_type: {json.dumps(ability, ensure_ascii=False)}")
            stub.append(f"    trigger: {json.dumps(trig, ensure_ascii=False)}")
            stub.append(f"    conditions: {json.dumps(conds, ensure_ascii=False)}")
            stub.append(f"    optional: {str(opt).lower()}")
            stub.append(f"    template: {json.dumps(tmpl, ensure_ascii=False)}")
            stub.append(f"    example: {json.dumps(ex, ensure_ascii=False)}")
            for fk in ["filters_group", "filters_unit", "filters_card_kind", "filters_cost_le", "filters_cost_ge"]:
                val = row.get(fk, "")
                if isinstance(val, float) and pd.isna(val):
                    val = ""
                stub.append(f"    {fk}: {json.dumps(str(val), ensure_ascii=False)}")
            stub.append("    action: TODO")
            stub.append("    params: {}")
            stub.append("")
        p = outdir / f"{kind}_patterns_stub.yaml"
        p.write_text("\n".join(stub), encoding="utf-8")
        return p

    cost_top = pd.read_csv(cost_csv) if cost_csv.exists() else pd.DataFrame([])
    eff_top = pd.read_csv(eff_csv) if eff_csv.exists() else pd.DataFrame([])

    cost_stub = write_stub("cost", cost_top, "cost_template", "example_cost_text") if len(cost_top) else (outdir / "cost_patterns_stub.yaml")
    if not len(cost_top):
        cost_stub.write_text("version: 1\npatterns: []\n", encoding="utf-8")

    eff_stub = write_stub("effect", eff_top, "effect_template", "example_effect_text") if len(eff_top) else (outdir / "effect_patterns_stub.yaml")
    if not len(eff_top):
        eff_stub.write_text("version: 1\npatterns: []\n", encoding="utf-8")

    print(f"[DONE] triggers -> {trig_csv}")
    print(f"[DONE] cost clauses -> {cost_csv}")
    print(f"[DONE] effect clauses -> {eff_csv}")
    print(f"[DONE] stubs -> {cost_stub} , {eff_stub}")

    return {
        "trigger_csv": trig_csv,
        "cost_csv": cost_csv,
        "effect_csv": eff_csv,
        "cost_stub": cost_stub,
        "effect_stub": eff_stub,
    }


# -------------------------
# audit
# -------------------------
def cmd_audit(csv_path: Path, top_unknown: int = 30) -> None:
    df = pd.read_csv(csv_path)
    print("[SUMMARY]")
    print(f"  rows: {len(df)}")
    if "cardnumber" in df.columns:
        print(f"  unique cardnumber: {df['cardnumber'].nunique(dropna=True)}")

    print("\n[MISSING RATE]")
    for col in ["card_type_norm", "cost", "score", "blade", "effect_text_norm", "base_hearts_raw", "required_hearts_raw"]:
        if col in df.columns:
            na = float(df[col].isna().mean())
            empty = float((df[col].astype(str).str.strip() == "").mean())
            print(f"  {col:20s}  na={na:.3f} empty={empty:.3f}")

    if "cardnumber" in df.columns:
        bad = df["cardnumber"].fillna("").astype(str).apply(lambda x: (x.strip() != "" and not AUDIT_CARDNO_RE.match(x.strip())))
        n_bad = int(bad.sum())
        print("\n[CARDNUMBER FORMAT]")
        print(f"  bad format count: {n_bad}")

    if "effect_text_status" in df.columns:
        print("\n[EFFECT TEXT STATUS]")
        vc = df["effect_text_status"].fillna("").astype(str).value_counts(dropna=False)
        for k, v in vc.items():
            print(f"  {k or '(blank)':20s} {int(v)}")
    elif "effect_text_norm" in df.columns:
        print("\n[EFFECT TEXT STATUS]")
        vc = df["effect_text_norm"].fillna("").astype(str).map(lambda s: classify_effect_text_status(s, s)).value_counts(dropna=False)
        for k, v in vc.items():
            print(f"  {k or '(blank)':20s} {int(v)}")

    # unknown tags tally
    if "effect_tokens_json" in df.columns:
        unknown = Counter()
        for s in df["effect_tokens_json"].tolist():
            ok, obj = safe_json_loads(s)
            if not ok or not isinstance(obj, dict):
                continue
            tags = obj.get("unknown_tags", obj.get("tags", []))
            if isinstance(tags, list):
                for t in tags:
                    if isinstance(t, str) and t:
                        unknown[t] += 1
        print("\n[UNKNOWN TOKENS in effect_tokens_json]")
        for k, v in unknown.most_common(top_unknown):
            print(f"  {k:20s} {v}")

    for col in ["tok_energy_icon_n", "tok_all_heart_n", "tok_blade_icon_n", "tok_score_delta_icon"]:
        if col in df.columns:
            print(f"\n[{col}] sum={int(df[col].fillna(0).sum())}")

    print("\n[DONE]")


# -------------------------
# CLI
# -------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llocg_db_tool_v7.py")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("scrape")
    ps.add_argument("--products-url", default=CONFIG["products_url"])
    ps.add_argument("--outdir", default=CONFIG["outdir"])
    ps.add_argument("--cache", default=CONFIG["cache"])
    ps.add_argument("--delay", type=float, default=CONFIG["delay"])
    ps.add_argument("--checkpoint-every", type=int, default=CONFIG["checkpoint_every"])
    ps.add_argument("--max-fail", type=int, default=CONFIG["max_fail"])
    ps.add_argument("--user-agent", default=CONFIG["user_agent"])
    ps.add_argument("--limit-products", type=int, default=0)
    ps.add_argument("--limit-cards", type=int, default=0)
    ps.add_argument("--no-normalize", action="store_true")

    pn = sub.add_parser("normalize")
    pn.add_argument("--csv", required=True)
    pn.add_argument("--json", default="")
    pn.add_argument("--outdir", default="")
    pn.add_argument("--suffix", default=CONFIG["normalize_suffix"])

    pm = sub.add_parser("mine")
    pm.add_argument("--csv", required=True)
    pm.add_argument("--outdir", default="")
    pm.add_argument("--top", type=int, default=120)

    pa = sub.add_parser("audit")
    pa.add_argument("--csv", required=True)
    pa.add_argument("--top-unknown", type=int, default=30)

    pim = sub.add_parser("image-manifest")
    pim.add_argument("--json", default="")
    pim.add_argument("--csv", default="")
    pim.add_argument("--outdir", default=CONFIG["outdir"])
    pim.add_argument("--cache", default=CONFIG["cache"])
    pim.add_argument("--delay", type=float, default=CONFIG["delay"])
    pim.add_argument("--user-agent", default=CONFIG["user_agent"])
    pim.add_argument("--timeout", type=float, default=25.0)
    pim.add_argument("--no-per-card-fallback", action="store_true")

    pall = sub.add_parser("all")
    pall.add_argument("--products-url", default=CONFIG["products_url"])
    pall.add_argument("--outdir", default=CONFIG["outdir"])
    pall.add_argument("--cache", default=CONFIG["cache"])
    pall.add_argument("--delay", type=float, default=CONFIG["delay"])
    pall.add_argument("--checkpoint-every", type=int, default=CONFIG["checkpoint_every"])
    pall.add_argument("--max-fail", type=int, default=CONFIG["max_fail"])
    pall.add_argument("--user-agent", default=CONFIG["user_agent"])
    pall.add_argument("--limit-products", type=int, default=0)
    pall.add_argument("--limit-cards", type=int, default=0)
    pall.add_argument("--no-normalize", action="store_true")
    pall.add_argument("--suffix", default=CONFIG["normalize_suffix"])
    pall.add_argument("--mine-top", type=int, default=120)
    pall.add_argument("--top-unknown", type=int, default=30)
    pall.add_argument("--no-official-image-manifest", action="store_true")
    pall.add_argument("--official-timeout", type=float, default=25.0)
    pall.add_argument("--no-per-card-fallback", action="store_true")

    return p


def main() -> None:
    args = build_parser().parse_args()

    if args.cmd == "scrape":
        cmd_scrape(
            products_url=args.products_url,
            outdir=Path(args.outdir),
            cache_dir=Path(args.cache),
            delay=args.delay,
            checkpoint_every=args.checkpoint_every,
            max_fail=args.max_fail,
            user_agent=args.user_agent,
            limit_products=args.limit_products,
            limit_cards=args.limit_cards,
            no_normalize=args.no_normalize,
        )
        return

    if args.cmd == "normalize":
        csvp = Path(args.csv)
        jsonp = Path(args.json) if args.json else None
        outdir = Path(args.outdir) if args.outdir else csvp.parent
        cmd_normalize(csvp, jsonp, outdir, args.suffix)
        return

    if args.cmd == "mine":
        csvp = Path(args.csv)
        outdir = Path(args.outdir) if args.outdir else csvp.parent
        cmd_mine(csvp, outdir, args.top)
        return

    if args.cmd == "audit":
        cmd_audit(Path(args.csv), args.top_unknown)
        return

    if args.cmd == "image-manifest":
        db_json = Path(args.json) if args.json else None
        db_csv = Path(args.csv) if args.csv else None
        cmd_official_image_manifest(
            db_json=db_json,
            db_csv=db_csv,
            outdir=Path(args.outdir),
            cache_dir=Path(args.cache),
            delay=args.delay,
            user_agent=args.user_agent,
            timeout=args.timeout,
            per_card_fallback=(not args.no_per_card_fallback),
        )
        return

    if args.cmd == "all":
        out_csv, out_json = cmd_scrape(
            products_url=args.products_url,
            outdir=Path(args.outdir),
            cache_dir=Path(args.cache),
            delay=args.delay,
            checkpoint_every=args.checkpoint_every,
            max_fail=args.max_fail,
            user_agent=args.user_agent,
            limit_products=args.limit_products,
            limit_cards=args.limit_cards,
            no_normalize=args.no_normalize,
        )
        norm_csv, norm_json = cmd_normalize(out_csv, out_json, Path(args.outdir), args.suffix)
        cmd_mine(norm_csv, Path(args.outdir), args.mine_top)
        cmd_audit(norm_csv, args.top_unknown)
        if not args.no_official_image_manifest:
            try:
                cmd_official_image_manifest(
                    db_json=norm_json,
                    db_csv=norm_csv,
                    outdir=Path(args.outdir),
                    cache_dir=Path(args.cache),
                    delay=args.delay,
                    user_agent=args.user_agent,
                    timeout=args.official_timeout,
                    per_card_fallback=(not args.no_per_card_fallback),
                )
            except Exception as e:
                print(f"[WARN] official image manifest generation failed: {e}")
        return


if __name__ == "__main__":
    main()
