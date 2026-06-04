# -*- coding: utf-8 -*-
from __future__ import annotations
# BUILD_TAG: db_parse_raw_heart_icons_20260604a

"""llocg_ui.db

カードDB（compiled/tokv1）読み込みと、カード番号/種別判定ユーティリティ。

- `cards_min_tokv1.csv/json`（スタッツ/必要ハート等）と `cards_compiled_*.json`（種別/能力）をマージ
- decklist/画像ファイル名の揺れ（末尾ハイフン、PR位置入替、0埋め等）を吸収
- `cards_min_tokv1.csv` は UTF-8 BOM あり得るため `utf-8-sig` で読む
"""


import argparse
import csv
import json
import random
import time
import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _safe_int(x, default=0) -> int:
    try:
        if x is None:
            return default
        if isinstance(x, int):
            return x
        s = str(x).strip()
        if s == "" or s.lower() == "nan":
            return default
        return int(float(s))
    except Exception:
        return default


def _read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _write_text(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _hearts_from_counts_json(counts_json: str) -> Dict[str, int]:
    if not counts_json:
        return {}
    try:
        d = json.loads(counts_json)
        if isinstance(d, dict):
            out = {}
            for k, v in d.items():
                try:
                    iv = int(v)
                except Exception:
                    continue
                if iv != 0:
                    out[str(k)] = iv
            return out
    except Exception:
        return {}
    return {}


_COLOR_TOKEN_TO_KEY = {
    "桃": "pink", "赤": "red", "黄": "yellow",
    "緑": "green", "青": "blue", "紫": "purple",
    "任意": "any", "ALL": "all",
    "pink": "pink", "red": "red", "yellow": "yellow",
    "green": "green", "blue": "blue", "purple": "purple",
    "any": "any", "all": "all",
}
_ICON_TOKEN_RE = re.compile(r"<\s*\(?\s*([^<>（）()]+?)\s*\)?\s*>\s*(?:(?:×|x|X)\s*)?([0-9０-９]+)?")
_FW_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")


def _parse_raw_icon_counts(raw: str, *, include_any: bool = True, include_all: bool = True) -> Dict[str, int]:
    """Parse official-style icon text such as '<赤> 2 <任意> 7'.

    The 2026 DB update changed many stat fields from legacy '<(赤)>×2'
    normalized counts to raw official-like '<赤> 2' strings.  Older runtime code
    only trusted *_counts_json, so LIVE required hearts could become req={}.  This
    parser is intentionally local to runtime DB loading so the simulator remains
    usable even before DB regeneration.
    """
    txt = str(raw or "").strip().replace("＋", "+")
    if not txt or txt in {"なし", "-", "nan", "None", "null"}:
        return {}
    out: Dict[str, int] = {}
    for m in _ICON_TOKEN_RE.finditer(txt):
        token = str(m.group(1) or "").strip().replace(" ", "")
        key = _COLOR_TOKEN_TO_KEY.get(token)
        if not key:
            continue
        if key == "any" and not include_any:
            continue
        if key == "all" and not include_all:
            continue
        n_raw = str(m.group(2) or "").strip().translate(_FW_DIGITS)
        n = int(n_raw) if n_raw else 1
        if n > 0:
            out[key] = int(out.get(key, 0) or 0) + n
    return out


def _merge_counts_with_raw(counts: Dict[str, int], raw: str, *, include_any: bool = True, include_all: bool = True) -> Dict[str, int]:
    base = dict(counts or {})
    # Existing normalized columns are authoritative when populated.  Fall back to
    # raw only when the normalized column is blank/broken.
    if any(int(v or 0) > 0 for v in base.values()):
        return {str(k): int(v) for k, v in base.items() if int(v or 0) != 0}
    return _parse_raw_icon_counts(raw, include_any=include_any, include_all=include_all)


def _parse_raw_icon_tags(raw: str) -> List[str]:
    """Return non-count icon tags from raw blade-heart text.

    Examples: '<ALL>' -> '(ALL)', '<ドロー+1>' -> '(ドロー+1)', '<スコア+1>' -> '(スコア+1)'.
    Color icons are not returned here because they are represented in *_hearts.
    """
    txt = str(raw or "").strip().replace("＋", "+")
    if not txt or txt in {"なし", "-", "nan", "None", "null"}:
        return []
    tags: List[str] = []
    for m in _ICON_TOKEN_RE.finditer(txt):
        token = str(m.group(1) or "").strip().replace(" ", "")
        if token in _COLOR_TOKEN_TO_KEY:
            # Keep ALL both as a wildcard heart and as a tag, because some effect
            # filters check for blade-heart payload tags explicitly.
            if token == "ALL":
                tags.append("(ALL)")
            continue
        if token:
            tags.append(f"({token})")
    return list(dict.fromkeys(tags))


def _merge_tags_with_raw(tags_json: str, raw: str) -> str:
    tags = _parse_tags_json(tags_json)
    tags.extend(_parse_raw_icon_tags(raw))
    return json.dumps(list(dict.fromkeys([str(t) for t in tags if str(t).strip()])), ensure_ascii=False)


def _parse_tags_json(tags_json: str) -> List[str]:
    try:
        x = json.loads(tags_json) if tags_json else []
        if isinstance(x, list):
            return [str(t) for t in x]
    except Exception:
        pass
    return []


def _count_draw_icons(tags_json: str) -> int:
    n = 0
    for t in _parse_tags_json(tags_json):
        m = re.search(r"ドロー\+(\d+)", t)
        if m:
            n += int(m.group(1))
    return n


def _norm_type(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().upper()


def is_member_type(card_type_norm: str) -> bool:
    # Robust to DB variants: MEMBER / MEMBER_CARD / "メンバー" / etc.
    raw = card_type_norm or ""
    t = _norm_type(raw)
    if not t and not raw:
        return False
    if "MEMBER" in t:
        return True
    if "メンバー" in raw:
        return True
    return False


def is_live_type(card_type_norm: str) -> bool:
    raw = card_type_norm or ""
    t = _norm_type(raw)
    if not t and not raw:
        return False
    if "LIVE" in t:
        return True
    if "ライブ" in raw:
        return True
    return False


def _looks_like_live_payload(required_hearts: Dict[str, int], score: int, cost: int = 0, blade: int = 0, base_hearts: Optional[Dict[str, int]] = None) -> bool:
    """Heuristic DB repair for obvious LIVE rows mis-exported as MEMBER.

    Prefer explicit required_hearts. As a weaker fallback, accept score>0 only when
    the row has no member-like payload (cost/blade/base_hearts).
    """
    try:
        req = required_hearts or {}
        if isinstance(req, dict) and any(int(v or 0) > 0 for v in req.values()):
            return True
    except Exception:
        pass
    try:
        if int(score or 0) > 0 and int(cost or 0) == 0 and int(blade or 0) == 0 and not (base_hearts or {}):
            return True
    except Exception:
        pass
    return False


def _repair_cardinfo_type(ci: "CardInfo") -> "CardInfo":
    try:
        raw = str(getattr(ci, 'type', '') or '').strip()
        looks_live = _looks_like_live_payload(
            getattr(ci, 'required_hearts', {}) or {},
            getattr(ci, 'score', 0) or 0,
            getattr(ci, 'cost', 0) or 0,
            getattr(ci, 'blade', 0) or 0,
            getattr(ci, 'base_hearts', {}) or {},
        )
        if looks_live and (not raw or is_member_type(raw)):
            ci.type = 'LIVE'
    except Exception:
        pass
    return ci


def _norm_cardno_for_filename(cardno: str) -> str:
    parts = (cardno or "").split("-")
    if not parts:
        return cardno or ""
    last = parts[-1]
    if last.isdigit():
        parts[-1] = last.zfill(3)
        return "-".join(parts)
    return cardno or ""


# ----------------------------
# Card DB
# ----------------------------

@dataclass
class CardInfo:
    cardnumber: str
    name: str = ""
    type: str = ""
    cost: int = 0
    blade: int = 0
    score: int = 0
    base_hearts: Dict[str, int] = field(default_factory=dict)
    required_hearts: Dict[str, int] = field(default_factory=dict)
    blade_hearts: Dict[str, int] = field(default_factory=dict)
    blade_heart_tags_json: str = "[]"
    # Preserve original DB text as a fallback for newly scraped official-style icons
    # such as <ALL>, <スコア+1>, <桃>, when normalized count/tag columns are empty.
    base_hearts_raw: str = ""
    required_hearts_raw: str = ""
    blade_heart_raw: str = ""
    group: str = ""
    unit: str = ""
    abilities: List[Dict[str, Any]] = field(default_factory=list)



# --- Card number normalization & variants (DB lookup + image lookup) ---

RARITY_TOKENS = {
    "N","R","R2","L","L2","SD","PR","SEC","SECL","AR","RM","P","P2","P+","P＋","SP","SP+","SP＋"
}

def _canon_cardno(cn: str) -> str:
    s = (cn or "").strip()
    if not s:
        return ""
    # normalize fullwidth plus
    s = s.replace("＋", "+")
    # strip trailing hyphens/spaces
    s = re.sub(r"[-\s]+$", "", s)
    # HS-018-PR -> HS-PR-018 (common alt form)
    m = re.match(r"^(.*?)-(\d+)-PR$", s, flags=re.IGNORECASE)
    if m:
        s = f"{m.group(1)}-PR-{m.group(2)}"
    # If a rarity token got appended as a suffix (e.g., ...-P+), drop it
    parts = s.split("-")
    if len(parts) >= 2:
        last = parts[-1].upper()
        if last in RARITY_TOKENS and (len(parts) < 3 or not parts[-2].isdigit()):
            parts = parts[:-1]
            s = "-".join(parts)
    return s

def _cardno_variants(cn: str) -> List[str]:
    base = _canon_cardno(cn)
    out: List[str] = []
    for x in [cn, base]:
        x = (x or "").strip()
        if not x:
            continue
        x = re.sub(r"[-\s]+$", "", x)
        out.append(x)
        out.append(_norm_cardno_for_filename(x))
    return list(dict.fromkeys([x for x in out if x]))

def _get_card(cards_db: Dict[str, CardInfo], cn: str) -> Optional[CardInfo]:
    for key in _cardno_variants(cn):
        c = cards_db.get(key)
        if c:
            return c
    return None

def load_tokv1_json(path: Path) -> Dict[str, CardInfo]:
    obj = _read_json(path)
    if isinstance(obj, dict) and "cards" in obj:
        obj = obj.get("cards", [])
    if not isinstance(obj, list):
        return {}
    out: Dict[str, CardInfo] = {}
    for r in obj:
        if not isinstance(r, dict):
            continue
        cn_raw = str(r.get("cardnumber", "") or "").strip()
        cn = _canon_cardno(cn_raw)
        if not cn:
            continue
        ci = _repair_cardinfo_type(CardInfo(
            cardnumber=cn,
            name=str(r.get("cardname", "")).strip(),
            type=str(r.get("card_type_norm", "") or r.get("card_type_raw", "") or "").strip(),
            cost=_safe_int(r.get("cost", 0), 0),
            blade=_safe_int(r.get("blade", 0), 0),
            score=_safe_int(r.get("score", 0), 0),
            base_hearts=_merge_counts_with_raw(
                _hearts_from_counts_json(str(r.get("base_hearts_counts_json", ""))),
                str(r.get("base_hearts_raw", "") or ""),
                include_any=False,
                include_all=True,
            ),
            required_hearts=_merge_counts_with_raw(
                _hearts_from_counts_json(str(r.get("required_hearts_counts_json", ""))),
                str(r.get("required_hearts_raw", "") or ""),
                include_any=True,
                include_all=True,
            ),
            blade_hearts=_merge_counts_with_raw(
                _hearts_from_counts_json(str(r.get("blade_heart_counts_json", ""))),
                str(r.get("blade_heart_raw", "") or ""),
                include_any=False,
                include_all=True,
            ),
            blade_heart_tags_json=_merge_tags_with_raw(
                str(r.get("blade_heart_tags_json", "[]")) or "[]",
                str(r.get("blade_heart_raw", "") or ""),
            ),
            base_hearts_raw=str(r.get("base_hearts_raw", "") or "").strip(),
            required_hearts_raw=str(r.get("required_hearts_raw", "") or "").strip(),
            blade_heart_raw=str(r.get("blade_heart_raw", "") or "").strip(),
            # NOTE: some tokv1.json exports include these columns; keep if present.
            group=str(r.get("group", "") or "").strip(),
            unit=str(r.get("unit", "") or "").strip(),
        ))
        for k in _cardno_variants(cn_raw):
            out[k] = ci
        out[cn] = ci
    return out

def load_compiled_json(path: Path) -> Dict[str, CardInfo]:
    obj = _read_json(path)
    cards = obj.get("cards", []) if isinstance(obj, dict) else []
    out: Dict[str, CardInfo] = {}
    for r in cards:
        if not isinstance(r, dict):
            continue
        cn_raw = str(r.get("cardnumber", "") or "").strip()
        cn = _canon_cardno(cn_raw)
        if not cn:
            continue
        ci = CardInfo(
            cardnumber=cn,
            name=str(r.get("cardname", "")).strip(),
            type=str(r.get("card_type", "") or r.get("type", "") or "").strip(),
            abilities=(r.get("abilities", []) if isinstance(r.get("abilities", []), list) else []),
        )
        for k in _cardno_variants(cn_raw):
            out[k] = ci
        out[cn] = ci
    return out

def _search_roots(root: Path) -> List[Path]:
    roots: List[Path] = []
    db_out = Path(root) / 'llocg_db_out_full'
    if db_out.exists() and db_out.is_dir():
        roots.append(db_out)
    roots.append(Path(root))
    seen: List[Path] = []
    out: List[Path] = []
    for r in roots:
        if r not in seen:
            seen.append(r)
            out.append(r)
    return out


def detect_one_file(root: Path, patterns: List[str]) -> Optional[Path]:
    for base in _search_roots(root):
        hits: List[Path] = []
        for pat in patterns:
            hits.extend([p for p in base.glob(pat) if p.is_file()])
        if hits:
            hits.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return hits[0]
    return None

def load_cards_db(root: Path, compiled_path: Optional[Path] = None, tokv1_path: Optional[Path] = None) -> Dict[str, CardInfo]:
    # tokv1 (stats) first, then compiled (type/abilities) as fill
    if tokv1_path is None:
        tokv1_path = detect_one_file(root, ["cards_min_tokv1.json", "cards_min_tokv1.csv"])
    if compiled_path is None:
        compiled_path = detect_one_file(root, ["cards_compiled_*.json", "cards_compiled*.json"])
    db: Dict[str, CardInfo] = {}
    if tokv1_path and tokv1_path.exists():
        if tokv1_path.suffix.lower() == ".json":
            db.update(load_tokv1_json(tokv1_path))
            # IMPORTANT: cards_min_tokv1.json may omit group/unit columns.
            # If so, fill them from the CSV when available.
            csv_path = detect_one_file(root, ["cards_min_tokv1.csv"])
            if csv_path and csv_path.exists():
                try:
                    csv_db = load_cards_min(root)
                    for cn_csv, ci_csv in csv_db.items():
                        cn_can = _canon_cardno(str(cn_csv))
                        if not cn_can:
                            continue
                        ci = _get_card(db, cn_can)
                        if not ci:
                            continue
                        if (not getattr(ci, "group", "")) and getattr(ci_csv, "group", ""):
                            ci.group = ci_csv.group
                        if (not getattr(ci, "unit", "")) and getattr(ci_csv, "unit", ""):
                            ci.unit = ci_csv.unit
                except Exception:
                    # Never break UI due to metadata fill.
                    pass
        else:
            db.update(load_cards_min(root))
    if compiled_path and compiled_path.exists():
        comp = load_compiled_json(compiled_path)
        for k, ci in comp.items():
            if k not in db:
                db[k] = ci
            else:
                if not db[k].name and ci.name:
                    db[k].name = ci.name
                if not db[k].type and ci.type:
                    db[k].type = ci.type
                # abilities: tokv1 has none; compiled carries them
                if (not getattr(db[k], "abilities", None)) and getattr(ci, "abilities", None):
                    db[k].abilities = ci.abilities
    seen = set()
    for ci in list(db.values()):
        if id(ci) in seen:
            continue
        seen.add(id(ci))
        _repair_cardinfo_type(ci)
    return db
def load_cards_min(root: Path) -> Dict[str, CardInfo]:
    p = detect_one_file(root, ["cards_min_tokv1.csv"])
    if not p or not p.exists():
        return {}
    out: Dict[str, CardInfo] = {}
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cn = str(r.get("cardnumber", "") or r.get("\ufeffcardnumber", "") or "").strip()
            if not cn:
                continue
            out[cn] = _repair_cardinfo_type(CardInfo(
                cardnumber=cn,
                name=str(r.get("cardname", "")).strip(),
                type=str(r.get("card_type_norm", "")).strip(),
                cost=_safe_int(r.get("cost", 0), 0),
                blade=_safe_int(r.get("blade", 0), 0),
                score=_safe_int(r.get("score", 0), 0),
                base_hearts=_merge_counts_with_raw(
                    _hearts_from_counts_json(str(r.get("base_hearts_counts_json", ""))),
                    str(r.get("base_hearts_raw", "") or ""),
                    include_any=False,
                    include_all=True,
                ),
                required_hearts=_merge_counts_with_raw(
                    _hearts_from_counts_json(str(r.get("required_hearts_counts_json", ""))),
                    str(r.get("required_hearts_raw", "") or ""),
                    include_any=True,
                    include_all=True,
                ),
                blade_hearts=_merge_counts_with_raw(
                    _hearts_from_counts_json(str(r.get("blade_heart_counts_json", ""))),
                    str(r.get("blade_heart_raw", "") or ""),
                    include_any=False,
                    include_all=True,
                ),
                blade_heart_tags_json=_merge_tags_with_raw(
                    str(r.get("blade_heart_tags_json", "[]")) or "[]",
                    str(r.get("blade_heart_raw", "") or ""),
                ),
                base_hearts_raw=str(r.get("base_hearts_raw", "") or "").strip(),
                required_hearts_raw=str(r.get("required_hearts_raw", "") or "").strip(),
                blade_heart_raw=str(r.get("blade_heart_raw", "") or "").strip(),
                group=str(r.get("group", "") or "").strip(),
                unit=str(r.get("unit", "") or "").strip(),
            ))
    return out


# ----------------------------
