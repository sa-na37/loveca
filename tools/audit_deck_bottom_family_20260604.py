#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit Loveca deck-bottom movement family.

BUILD_TAG: audit_deck_bottom_family_20260604a
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

BUILD_TAG = "audit_deck_bottom_family_20260604a"


def iter_clauses(compiled: Dict[str, Any]):
    for c in compiled.get("cards", []) or []:
        for ab in c.get("abilities", []) or []:
            for cl in ab.get("clauses", []) or []:
                yield c, ab, cl


def classify(cost: str, eff: str, raw: str) -> str:
    blob = " ".join([cost or "", eff or "", raw or ""])
    if "デッキの一番下" not in blob and "デッキの下" not in blob and "一番上か一番下" not in blob:
        return "not_deck_bottom"
    if "控え室にある「" in cost and "シャッフルしてデッキの一番下" in cost:
        return "implemented_existing_named_green_cost_to_bottom"
    if "控え室にあるメンバーカード2枚" in cost and "それらのカードのコストの合計" in eff:
        return "implemented_green_member2_costsum_bottom"
    if "手札のライブカード" in cost and "デッキの一番下" in cost:
        return "implemented_hand_live_cost_to_bottom"
    if re.search(r"^自分の控え室から(?:ライブ|メンバー)?カードを\d+枚までデッキの一番下に置く。$", eff or ""):
        return "implemented_green_kind_upto_bottom"
    if re.search(r"^カードを\d+枚引き、手札を\d+枚デッキの一番下に置く。$", eff or ""):
        return "implemented_draw_then_hand_bottom"
    if "エールにより公開された自分のカードの中から" in eff and "デッキの一番下" in eff:
        return "implemented_existing_yell_to_bottom"
    if "自分か相手を選ぶ" in eff and "デッキの一番下" in eff:
        return "needs_opponent_player_choice"
    if "自分と相手" in eff and "デッキの下" in eff:
        return "needs_opponent_mass_bottom"
    if "すべてのメンバーカード" in eff and "デッキの下" in eff:
        return "needs_mass_bottom_threshold"
    if "一番上か一番下" in eff or "一番上か一番下" in cost:
        return "needs_top_or_bottom_choice"
    return "needs_audit_unmatched_deck_bottom"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compiled", default="./llocg_db_out_full/cards_compiled_v7h.json")
    ap.add_argument("--outdir", default="./loveca_reports")
    args = ap.parse_args()
    compiled_path = Path(args.compiled)
    if not compiled_path.exists():
        alt = Path("/mnt/data/cards_compiled_v7h.json")
        if alt.exists():
            compiled_path = alt
    data = json.loads(compiled_path.read_text(encoding="utf-8"))
    rows: List[Dict[str, Any]] = []
    for c, ab, cl in iter_clauses(data):
        cost = str(cl.get("cost_template", "") or "")
        eff = str(cl.get("effect_template", "") or "")
        raw = str(cl.get("raw", "") or "")
        if "デッキの一番下" not in (cost + eff + raw) and "デッキの下" not in (cost + eff + raw) and "一番上か一番下" not in (cost + eff + raw):
            continue
        status = classify(cost, eff, raw)
        rows.append({
            "cardnumber": c.get("cardnumber", ""),
            "cardname": c.get("cardname", ""),
            "card_type": c.get("card_type", ""),
            "ability_type": ab.get("ability_type", ""),
            "trigger": ab.get("trigger", ""),
            "conditions": ab.get("conditions", ""),
            "status": status,
            "cost_template": cost,
            "effect_template": eff,
            "raw": raw.replace("\n", " "),
        })
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "loveca_deck_bottom_family_audit_20260604a.csv"
    md_path = outdir / "loveca_deck_bottom_family_audit_20260604a.md"
    fieldnames = ["cardnumber", "cardname", "card_type", "ability_type", "trigger", "conditions", "status", "cost_template", "effect_template", "raw"]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    cnt = Counter(r["status"] for r in rows)
    lines = [
        "# Loveca deck-bottom family audit 20260604a",
        "",
        f"BUILD_TAG: `{BUILD_TAG}`",
        f"compiled: `{compiled_path}`",
        "",
        "## Summary",
        "",
        f"candidates: {len(rows)}",
    ]
    for k, v in sorted(cnt.items()):
        lines.append(f"- {k}: {v}")
    lines += ["", "## Rows", ""]
    for r in rows:
        lines.append(f"- `{r['cardnumber']}` {r['cardname']} — **{r['status']}**")
        if r["cost_template"]:
            lines.append(f"  - cost: {r['cost_template']}")
        if r["effect_template"]:
            lines.append(f"  - effect: {r['effect_template']}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] wrote {csv_path}")
    print(f"[OK] wrote {md_path}")
    print(f"[OK] candidates={len(rows)}")
    for k, v in sorted(cnt.items()):
        print(f"[OK] {k}: {v}")


if __name__ == "__main__":
    main()
