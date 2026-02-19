#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, json, csv, re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

RARITY_TOKENS = {"N","R","R2","L","L2","SD","PR","SEC","SECL","AR","RM","P","P2","P+"}
TYPE_TOKENS = {"MEMBER","LIVE","ENERGY"}

def canonicalize_card_no(raw: Any) -> str:
    s = "" if raw is None else str(raw)
    s = s.strip().strip('"').strip("'").replace("＋","+")
    s = re.sub(r"\s+","", s).rstrip("-")
    for _ in range(6):
        m = re.match(r"^(.*)-([A-Za-z0-9\+]+)$", s)
        if not m:
            break
        head, tail = m.group(1), m.group(2).upper()
        if tail in RARITY_TOKENS or tail in TYPE_TOKENS:
            s = head.rstrip("-")
        else:
            break
    return s

def pr_reorder(cn: str) -> str:
    cn = canonicalize_card_no(cn)
    m = re.match(r"^(.*)-PR-(\d+)$", cn, flags=re.I)
    if m:
        return f"{m.group(1)}-{m.group(2)}-PR"
    m2 = re.match(r"^(.*)-(\d+)-PR$", cn, flags=re.I)
    if m2:
        return f"{m2.group(1)}-PR-{m2.group(2)}"
    return cn

def read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def normalize_type(x: Any) -> str:
    s = "" if x is None else str(x)
    s = s.strip().upper()
    s = s.replace("メンバー","MEMBER").replace("ライブ","LIVE").replace("エネルギー","ENERGY")
    return s

def compiled_to_map(obj: Any) -> Dict[str, Dict[str, Any]]:
    """
    Accept:
      - { "cards": [...] }
      - { "cards": {cn: {...}} }
      - { cn: {...} }
    Return: cn -> record (dict)
    """
    if not isinstance(obj, dict):
        return {}
    cards = obj.get("cards", obj)
    out: Dict[str, Dict[str, Any]] = {}

    def add(rec: Dict[str, Any], key: str = "") -> None:
        cn = canonicalize_card_no(
            rec.get("cardnumber")
            or rec.get("card_no")
            or rec.get("cardNumber")
            or rec.get("db_card_no")
            or key
            or ""
        )
        if not cn:
            return
        out[cn] = rec

    if isinstance(cards, list):
        for rec in cards:
            if isinstance(rec, dict):
                add(rec)
    elif isinstance(cards, dict):
        for k, rec in cards.items():
            if isinstance(rec, dict):
                add(rec, key=str(k))
    return out

def load_tokv1(root: Path, tokv1_path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}

    p = tokv1_path if tokv1_path else None
    if p and p.exists():
        if p.suffix.lower() == ".csv":
            with p.open("r", encoding="utf-8", newline="") as f:
                rd = csv.DictReader(f)
                for r in rd:
                    cn = canonicalize_card_no(r.get("cardnumber", ""))
                    if cn:
                        out[cn] = r
            return out
        if p.suffix.lower() == ".json":
            obj = read_json(p)
            cards = obj.get("cards", obj) if isinstance(obj, dict) else obj
            if isinstance(cards, list):
                for rec in cards:
                    if isinstance(rec, dict):
                        cn = canonicalize_card_no(rec.get("cardnumber") or rec.get("card_no") or "")
                        if cn:
                            out[cn] = rec
            elif isinstance(cards, dict):
                for k, rec in cards.items():
                    if isinstance(rec, dict):
                        cn = canonicalize_card_no(rec.get("cardnumber") or rec.get("card_no") or k or "")
                        if cn:
                            out[cn] = rec
            return out

    csv_path = root / "cards_min_tokv1.csv"
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            rd = csv.DictReader(f)
            for r in rd:
                cn = canonicalize_card_no(r.get("cardnumber", ""))
                if cn:
                    out[cn] = r
        return out

    json_path = root / "cards_min_tokv1.json"
    if json_path.exists():
        obj = read_json(json_path)
        cards = obj.get("cards", obj) if isinstance(obj, dict) else obj
        if isinstance(cards, list):
            for rec in cards:
                if isinstance(rec, dict):
                    cn = canonicalize_card_no(rec.get("cardnumber") or rec.get("card_no") or "")
                    if cn:
                        out[cn] = rec
        elif isinstance(cards, dict):
            for k, rec in cards.items():
                if isinstance(rec, dict):
                    cn = canonicalize_card_no(rec.get("cardnumber") or rec.get("card_no") or k or "")
                    if cn:
                        out[cn] = rec
    return out

def extract_type_from_record(rec: Optional[Dict[str, Any]]) -> Tuple[str, Dict[str, str]]:
    if not rec:
        return "", {}
    cand = {
        "card_type": normalize_type(rec.get("card_type")),
        "card_type_norm": normalize_type(rec.get("card_type_norm")),
        "type": normalize_type(rec.get("type")),
    }
    chosen = cand["card_type"] or cand["card_type_norm"] or cand["type"] or ""
    return chosen, cand

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--compiled", required=True)
    ap.add_argument("--tokv1", default=None)
    ap.add_argument("--probe-cn", required=True)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    compiled_path = Path(args.compiled).resolve()
    tokv1_path = Path(args.tokv1).resolve() if args.tokv1 else None

    obj = read_json(compiled_path)
    comp_map = compiled_to_map(obj)
    tok_map = load_tokv1(root, tokv1_path)

    print("[INFO] root      =", root)
    print("[INFO] compiled  =", compiled_path)
    print("[INFO] tokv1     =", tokv1_path if tokv1_path else "(root default)")
    print("[INFO] compiled records =", len(comp_map))
    print("[INFO] tokv1 records    =", len(tok_map))
    print()

    raw = args.probe_cn
    v0 = raw
    v1 = canonicalize_card_no(raw)
    v2 = pr_reorder(v1)
    v3 = canonicalize_card_no(raw).rstrip("-")
    variants = []
    for v in [v0, v1, v2, v3, v1 + "-", v2 + "-"]:
        vv = v.replace("＋","+")
        if vv not in variants:
            variants.append(vv)

    print("[PROBE] input =", raw)
    print("[PROBE] variants:")
    for v in variants:
        print("  -", v)
    print()

    def show_hit(label: str, rec: Optional[Dict[str, Any]]) -> None:
        if not rec:
            print(f"    {label}: MISS")
            return
        t, cands = extract_type_from_record(rec)
        keys = list(rec.keys())
        keys_preview = ", ".join(keys[:18]) + (" ..." if len(keys) > 18 else "")
        print(f"    {label}: HIT keys=({keys_preview})")
        print(f"      type chosen='{t}'  cands={cands}")

    for v in variants:
        key = canonicalize_card_no(v)
        print(f"[LOOKUP] key='{key}'")
        comp_rec = comp_map.get(key)
        tok_rec = tok_map.get(key)
        show_hit("compiled", comp_rec)
        show_hit("tokv1   ", tok_rec)

        # simulate typical overlay fill rule: tokv1 first, then compiled fill-if-empty
        tok_type, _ = extract_type_from_record(tok_rec)
        comp_type, _ = extract_type_from_record(comp_rec)
        final = tok_type or comp_type or ""
        print(f"    => final_type (tokv1-first fill) = '{final}'")
        print()

    # extra: show if compiled contains near-miss keys with trailing '-'
    key0 = canonicalize_card_no(raw)
    near = [k for k in comp_map.keys() if k.startswith(key0) and k != key0]
    near2 = [k for k in comp_map.keys() if key0.startswith(k) and k != key0]
    if near or near2:
        print("[NEAR-MISS] compiled similar keys:")
        for k in (near[:10] + near2[:10]):
            print("  -", k)

if __name__ == "__main__":
    main()
