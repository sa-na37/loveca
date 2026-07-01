#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loveca DB integrity checker for DB update workflow.

Default target:
  /Users/tekitou/Desktop/gsim/loveca/llocg_db_out_full

Checks:
- cards_min_tokv1.csv/json row/card counts
- cards_compiled_v7h.json count and cardnumber set consistency
- duplicate / missing / malformed cardnumbers
- cardname and card_type consistency between min DB and compiled DB
- official_image_manifest consistency, if present
- optional card image count, if --images-dir is supplied
"""
from __future__ import annotations

BUILD_TAG = "db_integrity_checker_pbhs_clhs01_20260603b"

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

CARDNO_RE = re.compile(r"^[A-Z]{1,4}(?:!(?:[A-Z0-9]{0,8})?)?-[A-Za-z0-9]+-\d{3}(?:-[A-Za-z0-9]+)?$")


def load_json_cards(path: Path) -> Tuple[Any, List[Dict[str, Any]]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    cards = obj.get("cards", obj) if isinstance(obj, dict) else obj
    if not isinstance(cards, list):
        raise SystemExit(f"[NG] JSON cards is not a list: {path}")
    return obj, [c for c in cards if isinstance(c, dict)]


def cardno(c: Dict[str, Any]) -> str:
    return str(c.get("cardnumber") or c.get("card_number") or "").strip()


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def product_key(n: str) -> str:
    m = re.search(r"-(bp\d+|sd\d+|pb\d+|cl\d+|PR)-", n, re.I)
    return m.group(1).lower() if m else "other"


def first_last(nums: List[str], k: int = 10) -> str:
    return f"first={nums[:3]} last={nums[-k:]}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dbdir", type=Path, default=Path("/Users/tekitou/Desktop/gsim/loveca/llocg_db_out_full"))
    ap.add_argument("--images-dir", type=Path, default=None)
    ap.add_argument("--expect-min", type=int, default=0, help="Optional expected minimum card count, e.g. 990")
    args = ap.parse_args()

    dbdir = args.dbdir
    csv_path = dbdir / "cards_min_tokv1.csv"
    min_json_path = dbdir / "cards_min_tokv1.json"
    comp_path = dbdir / "cards_compiled_v7h.json"
    manifest_path = dbdir / "official_image_manifest.json"

    problems: List[str] = []
    warnings: List[str] = []

    print("=== Loveca DB integrity check ===")
    print("dbdir:", dbdir)

    required = [csv_path, min_json_path, comp_path]
    for p in required:
        if not p.exists():
            problems.append(f"missing required file: {p}")
    if problems:
        for x in problems:
            print("[NG]", x)
        return 1

    csv_rows = read_csv_rows(csv_path)
    min_obj, min_cards = load_json_cards(min_json_path)
    comp_obj, comp_cards = load_json_cards(comp_path)

    min_nums = [cardno(c) for c in min_cards]
    comp_nums = [cardno(c) for c in comp_cards]
    csv_nums = [str(r.get("cardnumber") or "").strip() for r in csv_rows]

    print("\n[COUNTS]")
    print("csv rows        :", len(csv_rows), first_last(csv_nums))
    print("min json cards  :", len(min_cards), first_last(min_nums))
    print("compiled cards  :", len(comp_cards), first_last(comp_nums))
    print("compiled source :", comp_obj.get("source_csv") if isinstance(comp_obj, dict) else "")

    if args.expect_min and len(min_cards) < args.expect_min:
        problems.append(f"card count below expected minimum: {len(min_cards)} < {args.expect_min}")
    if len(csv_rows) != len(min_cards):
        problems.append(f"csv/json count mismatch: csv={len(csv_rows)} json={len(min_cards)}")
    if len(min_cards) != len(comp_cards):
        problems.append(f"min/compiled count mismatch: min={len(min_cards)} compiled={len(comp_cards)}")

    print("\n[DUPLICATES / FORMAT]")
    for label, nums in [("csv", csv_nums), ("min", min_nums), ("compiled", comp_nums)]:
        dups = [k for k, v in Counter(nums).items() if k and v > 1]
        bad = [n for n in nums if n and not CARDNO_RE.match(n)]
        blank = [n for n in nums if not n]
        print(f"{label:8s} duplicates={len(dups)} bad_format={len(bad)} blank={len(blank)}")
        if dups:
            problems.append(f"{label} duplicate cardnumbers: {dups[:20]}")
        if bad:
            problems.append(f"{label} bad cardnumber format: {bad[:20]}")
        if blank:
            problems.append(f"{label} blank cardnumber count={len(blank)}")

    print("\n[SET CONSISTENCY]")
    min_set, comp_set, csv_set = set(min_nums), set(comp_nums), set(csv_nums)
    print("csv == min      :", csv_set == min_set)
    print("min == compiled :", min_set == comp_set)
    if csv_set != min_set:
        problems.append(f"csv/min cardnumber set mismatch: csv-only={len(csv_set-min_set)} min-only={len(min_set-csv_set)}")
    if min_set != comp_set:
        problems.append(f"min/compiled cardnumber set mismatch: min-only={len(min_set-comp_set)} compiled-only={len(comp_set-min_set)}")

    print("\n[REQUIRED FIELDS]")
    for field in ["cardnumber", "cardname", "source_url", "card_type_norm", "effect_text_norm"]:
        miss = []
        for c in min_cards:
            v = c.get(field)
            if v is None or str(v).strip() == "" or str(v).strip().lower() == "nan":
                miss.append(cardno(c))
        print(f"{field:18s}: missing={len(miss)}", miss[:10] if miss else "")
        if field in {"cardnumber", "cardname", "source_url", "card_type_norm"} and miss:
            problems.append(f"missing {field}: {miss[:20]}")
        elif field == "effect_text_norm" and miss:
            warnings.append(f"missing effect_text_norm: {miss[:20]}")

    print("\n[TYPE / STATUS]")
    print("card_type_norm  :", dict(Counter(str(c.get("card_type_norm") or "").strip() for c in min_cards)))
    print("compiled type   :", dict(Counter(str(c.get("card_type") or "").strip() for c in comp_cards)))
    print("effect status   :", dict(Counter(str(c.get("effect_text_status") or "").strip() for c in min_cards)))
    print("parse status    :", dict(Counter(str(c.get("parse_status") or "").strip() for c in comp_cards)))

    min_by = {cardno(c): c for c in min_cards}
    name_diff = []
    type_diff = []
    for c in comp_cards:
        n = cardno(c)
        m = min_by.get(n)
        if not m:
            continue
        if str(c.get("cardname") or "").strip() != str(m.get("cardname") or "").strip():
            name_diff.append((n, m.get("cardname"), c.get("cardname")))
        if str(c.get("card_type") or "").strip() != str(m.get("card_type_norm") or "").strip():
            type_diff.append((n, m.get("card_type_norm"), c.get("card_type")))
    print("name diff       :", len(name_diff), name_diff[:5])
    print("type diff       :", len(type_diff), type_diff[:5])
    if name_diff:
        problems.append(f"name mismatch min vs compiled: {name_diff[:10]}")
    if type_diff:
        problems.append(f"type mismatch min vs compiled: {type_diff[:10]}")

    print("\n[PRODUCT COUNTS]")
    pc = Counter(product_key(n) for n in min_nums)
    for k, v in sorted(pc.items()):
        print(f"{k:8s} {v}")
    bp6 = [n for n in min_nums if "-bp6-" in n.lower()]
    cl1 = [n for n in min_nums if "-cl1-" in n.lower()]
    pbhs = [n for n in min_nums if n.startswith("PL!HS-") and "-pb" in n.lower()]
    print("bp6 count       :", len(bp6), bp6[:5], bp6[-5:])
    print("cl1 count       :", len(cl1), cl1[:5], cl1[-5:])
    print("PBHS card count :", len(pbhs), pbhs[:5], pbhs[-5:])

    print("\n[COMPILED ABILITIES]")
    ability_count = clause_count = todo_cost = todo_effect = 0
    empty_abilities = []
    unknown_ability = []
    triggers = Counter()
    for c in comp_cards:
        abs_ = c.get("abilities") or []
        if str(c.get("parse_status") or "") == "OK" and not abs_:
            empty_abilities.append(cardno(c))
        ability_count += len(abs_)
        for ab in abs_:
            triggers[(ab.get("ability_type", ""), ab.get("trigger", ""))] += 1
            if ab.get("ability_type") in ("", "UNKNOWN"):
                unknown_ability.append((cardno(c), ab.get("trigger"), ab.get("conditions")))
            for cl in ab.get("clauses") or []:
                clause_count += 1
                cop = cl.get("cost_op") or {}
                eop = cl.get("effect_op") or {}
                if cop.get("op") == "TODO":
                    todo_cost += 1
                if eop.get("op") == "TODO":
                    todo_effect += 1
    print("abilities       :", ability_count)
    print("clauses         :", clause_count)
    print("empty OK cards  :", len(empty_abilities), empty_abilities[:10])
    print("UNKNOWN ability :", len(unknown_ability), unknown_ability[:10])
    print("TODO cost/effect:", todo_cost, todo_effect)
    print("top triggers    :", triggers.most_common(10))
    if empty_abilities:
        warnings.append(f"OK parse_status but empty abilities: {empty_abilities[:20]}")
    if unknown_ability:
        warnings.append(f"UNKNOWN abilities: {unknown_ability[:20]}")

    if manifest_path.exists():
        print("\n[OFFICIAL IMAGE MANIFEST]")
        man = json.loads(manifest_path.read_text(encoding="utf-8"))
        cards_map = man.get("cards") or {}
        print("cards_total_in_db     :", man.get("cards_total_in_db"))
        print("cards_with_manifest   :", man.get("cards_with_manifest"))
        print("cards_missing_manifest:", man.get("cards_missing_manifest"))
        print("manifest card keys    :", len(cards_map))
        print("manifest extra keys   :", len(set(cards_map) - min_set))
        print("db no manifest keys   :", len(min_set - set(cards_map)))
        bad_entries = []
        for cn, entries in cards_map.items():
            if not isinstance(entries, list):
                bad_entries.append((cn, "entries not list"))
                continue
            for e in entries:
                if not isinstance(e, dict) or not e.get("exact_url") or not e.get("remote_filename") or not e.get("folder"):
                    bad_entries.append((cn, e))
        print("bad manifest entries  :", len(bad_entries))
        if man.get("cards_total_in_db") != len(min_cards):
            warnings.append(f"manifest cards_total_in_db differs from min json count: {man.get('cards_total_in_db')} vs {len(min_cards)}")
        if bad_entries:
            problems.append(f"bad manifest entries: {bad_entries[:20]}")
        bp06 = (man.get("expansions") or {}).get("BP06")
        clhs01 = (man.get("expansions") or {}).get("CLHS01")
        pbhs_exp = (man.get("expansions") or {}).get("PBHS")
        cl1_db = [n for n in min_nums if "-cl1-" in n.lower()]
        cl1_manifest = [n for n in cl1_db if n in cards_map]
        pbhs_db = [n for n in min_nums if n.startswith("PL!HS-") and "-pb" in n.lower()]
        pbhs_manifest = [n for n in pbhs_db if n in cards_map]
        print("BP06 manifest summary :", bp06)
        print("CLHS01 manifest summary:", clhs01)
        print("PBHS manifest summary :", pbhs_exp)
        print("CL1 manifest coverage :", len(cl1_manifest), "/", len(cl1_db))
        print("PBHS manifest coverage:", len(pbhs_manifest), "/", len(pbhs_db))
        if cl1_db and len(cl1_manifest) != len(cl1_db):
            warnings.append(f"CL1 manifest coverage incomplete: {len(cl1_manifest)}/{len(cl1_db)}")
        if pbhs_db and len(pbhs_manifest) != len(pbhs_db):
            warnings.append(f"PBHS manifest coverage incomplete: {len(pbhs_manifest)}/{len(pbhs_db)}")
    else:
        warnings.append(f"manifest not found: {manifest_path}")

    if args.images_dir:
        imgdir = args.images_dir
        print("\n[CARD IMAGES]")
        if imgdir.exists():
            imgs = list(imgdir.rglob("*.png"))
            print("image dir:", imgdir)
            print("png files:", len(imgs))
        else:
            warnings.append(f"images-dir not found: {imgdir}")

    print("\n[WARNINGS]")
    if warnings:
        for w in warnings:
            print("[WARN]", w)
    else:
        print("none")

    print("\n[RESULT]")
    if problems:
        for p in problems:
            print("[NG]", p)
        return 1
    print("[OK] no critical DB consistency errors detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
