#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llocg_decklist_to_simdeck.py

Convert a scraped DeckLog TSV (deck_<CODE>.tsv) into a simulation-friendly JSON by resolving
each card number against a compiled DB JSON (cards_compiled_*.json).

Key points (project conventions):
- Rarity is NOT required for resolution (and DB may not store it). We still accept it if present.
- We do NOT require a separate "id" field in the DB. If absent, we use cardnumber as the stable key.

Typical usage:
  python3 llocg_decklist_to_simdeck.py --root ./llocg_db_out_full --code 1RCBL
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# -------------------------
# utils
# -------------------------

def _warn(msg: str) -> None:
    print(f"[WARN] {msg}", file=sys.stderr)

def _die(msg: str, code: int = 1) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(code)

def _load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        _die(f"Failed to read JSON: {path} ({e})")

def _norm_plus(s: str) -> str:
    # Fullwidth plus → ASCII plus
    return s.replace("＋", "+").strip()

_CARDNO_SUFFIX_RE = re.compile(r"^(?P<base>.*-\d{3})(?:-(?P<suf>[A-Za-z0-9+＋]+))?$")

def _split_cardno_and_suffix(card_no_raw: str) -> Tuple[str, str]:
    """
    DeckLog export sometimes packs a rarity-like suffix into card_no, e.g.:
      PL!N-pb1-005-P＋
    We want:
      base = PL!N-pb1-005
      suffix = P+
    Also tolerate trailing hyphen:
      PL!-bp3-012-  -> base=PL!-bp3-012, suffix=""
    If it doesn't match the pattern, return (cleaned, "").
    """
    s = card_no_raw.strip()
    # drop any trailing hyphens/spaces
    s = re.sub(r"[-\s]+$", "", s)

    m = _CARDNO_SUFFIX_RE.match(s)
    if not m:
        return s, ""
    base = m.group("base") or s
    suf = m.group("suf") or ""
    return base.strip(), _norm_plus(suf)

def _read_tsv_deck(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        _die(f"TSV not found: {path}")
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for i, r in enumerate(reader, start=2):
            if not r:
                continue
            try:
                cnt = int(str(r.get("count", "")).strip())
            except Exception:
                _die(f"Bad count at line {i}: {r}")
            card_no_raw = str(r.get("card_no", "")).strip()
            rarity_raw = str(r.get("rarity", "")).strip()

            if not card_no_raw:
                _die(f"Empty card_no at line {i}")

            base_no, suf = _split_cardno_and_suffix(card_no_raw)
            rarity = _norm_plus(rarity_raw)

            # If rarity column is empty but card_no had a suffix, treat that as rarity.
            if not rarity and suf:
                rarity = suf
                _warn(f"Rarity inferred from card_no at line {i}: {card_no_raw} -> card_no={base_no}, rarity={rarity}")

            if not rarity:
                _warn(f"Empty rarity at line {i} (will resolve by card_no-only): {base_no}")

            rows.append({"count": cnt, "card_no": base_no, "rarity": rarity})

    return rows

def _guess_code_from_tsv(tsv_path: Path) -> Optional[str]:
    m = re.match(r"deck_([A-Za-z0-9]+)\.tsv$", tsv_path.name)
    return m.group(1) if m else None

def _find_latest_compiled_db(root: Path) -> Path:
    # Prefer explicit v7b if exists, otherwise newest cards_compiled_*.json
    cand = root / "cards_compiled_v7b.json"
    if cand.exists():
        return cand
    cands = sorted(root.glob("cards_compiled_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if cands:
        return cands[0]
    _die(f"No compiled DB found under root: {root} (expected cards_compiled_*.json)")

def _iter_cards(db_obj: Any) -> List[Dict[str, Any]]:
    """
    Accept either:
      - {"cards":[...]}
      - {"data":[...]}
      - [...]
    """
    if isinstance(db_obj, list):
        return [x for x in db_obj if isinstance(x, dict)]
    if isinstance(db_obj, dict):
        for k in ("cards", "data", "items"):
            v = db_obj.get(k)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
    _die("Unknown compiled DB schema: expected list or dict with 'cards' list")

def _get_card_no(card: Dict[str, Any]) -> Optional[str]:
    for k in ("card_no", "cardnumber", "cardnumber_norm", "cardnumber_raw"):
        v = card.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def _get_rarity(card: Dict[str, Any]) -> str:
    for k in ("rarity", "rare", "rar", "r"):
        v = card.get(k)
        if isinstance(v, str) and v.strip():
            return _norm_plus(v)
    return ""  # treat as unknown/unused

def _get_name(card: Dict[str, Any]) -> str:
    for k in ("name", "cardname", "card_name", "title"):
        v = card.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""

def _get_card_id(card: Dict[str, Any]) -> str:
    """
    "id" is optional in our project. If absent, use cardnumber as a stable key.
    """
    for k in ("id", "card_id", "cid", "uuid", "_db_key"):
        v = card.get(k)
        if isinstance(v, (str, int)) and str(v).strip():
            return str(v).strip()
    cno = _get_card_no(card)
    if cno:
        return cno
    return "UNKNOWN_ID"

@dataclass
class Resolved:
    tsv_card_no: str
    tsv_rarity: str
    count: int
    db_id: str
    db_card_no: str
    db_rarity: str
    name: str

def _build_index(cards: List[Dict[str, Any]]) -> Dict[Tuple[str, str], List[Dict[str, Any]]]:
    """
    Index by (card_no, rarity) and also by (card_no, "") to support DBs without rarity.

    IMPORTANT BUGFIX:
    If DB rarity is empty, DO NOT insert twice into the same (card_no,"") bucket.
    (That duplication causes false "ambiguous_card_no".)
    """
    idx: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for c in cards:
        cno = _get_card_no(c)
        if not cno:
            continue
        rar = _get_rarity(c)
        idx.setdefault((cno, rar), []).append(c)
        if rar != "":
            idx.setdefault((cno, ""), []).append(c)
    return idx

def _resolve_one(idx: Dict[Tuple[str, str], List[Dict[str, Any]]], card_no: str, rarity: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Return (card_record, mode).
    """
    # 1) Exact (card_no, rarity)
    cand = idx.get((card_no, rarity), [])
    if len(cand) == 1:
        return cand[0], "exact"
    if len(cand) > 1:
        return None, "ambiguous_exact"

    # 2) Fallback: DB without rarity (card_no,"")
    cand = idx.get((card_no, ""), [])
    if len(cand) == 1:
        return cand[0], "card_no_only"
    if len(cand) > 1:
        return None, "ambiguous_card_no"

    return None, "missing"

def _load_deck_meta(decklists_dir: Path, code: str) -> Dict[str, Any]:
    meta_path = decklists_dir / f"deck_{code}.meta.json"
    if not meta_path.exists():
        return {}
    obj = _load_json(meta_path)
    return obj if isinstance(obj, dict) else {}

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="./llocg_db_out_full", help="Project root (contains decklists/, cards_compiled_*.json)")
    ap.add_argument("--code", default="", help="Deck code (e.g., 1RCBL). If empty, inferred from --tsv filename.")
    ap.add_argument("--tsv", default="", help="Deck TSV path. Default: <root>/decklists/deck_<CODE>.tsv")
    ap.add_argument("--db", default="", help="Compiled DB JSON path. Default: auto-detect under <root>/")
    ap.add_argument("--out", default="", help="Output JSON path. Default: <root>/sim_decks/deck_<CODE>.json")
    ap.add_argument("--flat", action="store_true", help="Also emit flat_db_ids list (length=total_cards)")
    ap.add_argument("--allow-ambiguous", action="store_true", help="If ambiguous, choose the first match (not recommended)")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    decklists_dir = root / "decklists"
    sim_decks_dir = root / "sim_decks"
    decklists_dir.mkdir(parents=True, exist_ok=True)
    sim_decks_dir.mkdir(parents=True, exist_ok=True)

    tsv_path = Path(args.tsv).expanduser().resolve() if args.tsv else None
    if tsv_path is None:
        tsv_path = None  # for type checker

    code = (args.code or "").strip()
    if not code:
        # infer from --tsv if provided
        if args.tsv:
            code = _guess_code_from_tsv(Path(args.tsv)) or ""
        if not code:
            _die("Deck code is required: provide --code <CODE> or --tsv deck_<CODE>.tsv")

    if not args.tsv:
        tsv_path = (decklists_dir / f"deck_{code}.tsv").resolve()
    else:
        tsv_path = Path(args.tsv).expanduser().resolve()

    rows = _read_tsv_deck(tsv_path)

    db_path = Path(args.db).expanduser().resolve() if args.db else _find_latest_compiled_db(root)
    db_obj = _load_json(db_path)
    cards = _iter_cards(db_obj)
    idx = _build_index(cards)

    resolved: List[Resolved] = []
    missing: List[Tuple[str, str]] = []
    ambiguous: List[Tuple[str, str, str]] = []

    for r in rows:
        cno = r["card_no"]
        rar = r["rarity"]
        rec, mode = _resolve_one(idx, cno, rar)
        if rec is None:
            if mode.startswith("ambiguous"):
                ambiguous.append((cno, rar, mode))
            else:
                missing.append((cno, rar))
            continue

        db_id = _get_card_id(rec).strip()
        db_cno = (_get_card_no(rec) or cno).strip()
        if not db_id or db_id == "UNKNOWN_ID":
            # Never fail hard: treat cardnumber as key.
            _warn(f"DB id is missing/unknown for {cno}; using cardnumber as db_id.")
            db_id = db_cno

        resolved.append(
            Resolved(
                tsv_card_no=cno,
                tsv_rarity=rar,
                count=r["count"],
                db_id=db_id,
                db_card_no=db_cno,
                db_rarity=_get_rarity(rec),
                name=_get_name(rec),
            )
        )

    if missing:
        _warn("Missing cards in compiled DB (first 50 shown):")
        for cno, rar in missing[:50]:
            _warn(f"  - {cno}\t{rar}")
    if ambiguous:
        _warn("Ambiguous matches in compiled DB (first 50 shown):")
        for cno, rar, mode in ambiguous[:50]:
            _warn(f"  - {cno}\t{rar}\t({mode})")

    if missing or ambiguous:
        if ambiguous and args.allow_ambiguous:
            _warn("--allow-ambiguous is set, but this script currently does not auto-pick among multiple candidates.")
        _die(f"DB resolution failed: missing={len(missing)}, ambiguous={len(ambiguous)}. Fix normalization/DB, then retry.")

    # meta (deck name etc.)
    meta = _load_deck_meta(decklists_dir, code)

    out_path = Path(args.out).expanduser().resolve() if args.out else (sim_decks_dir / f"deck_{code}.json").resolve()

    payload: Dict[str, Any] = {
        "deck_code": code,
        "deck_name": meta.get("deck_name", ""),
        "tsv_path": str(tsv_path),
        "db_path": str(db_path),
        "total_cards": sum(x.count for x in resolved),
        "unique_cards": len(resolved),
        "cards": [
            {
                "count": x.count,
                "card_no": x.db_card_no,   # preferred stable key
                "db_id": x.db_id,          # for compatibility; same as card_no if DB has no id
                "name": x.name,
            }
            for x in resolved
        ],
        "meta": meta,
    }

    if args.flat:
        flat: List[str] = []
        for x in resolved:
            flat.extend([x.db_id] * x.count)
        payload["flat_db_ids"] = flat

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("[DONE]")
    print(f"root   : {root}")
    print(f"code   : {code}")
    print(f"tsv    : {tsv_path}")
    print(f"db     : {db_path}")
    print(f"cards  : {len(resolved)} unique / {payload['total_cards']} total")
    print(f"out    : {out_path}")

if __name__ == "__main__":
    main()
