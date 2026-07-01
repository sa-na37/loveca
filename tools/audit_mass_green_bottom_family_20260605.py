#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit mass waiting-room member -> deck bottom family for Loveca."""
from __future__ import annotations

BUILD_TAG = "audit_mass_green_bottom_family_20260605a"

import argparse
import csv
import json
import re
from pathlib import Path

PAT_FANFARE = re.compile(r"自分の控え室にあるすべてのメンバーカードをシャッフルし、デッキの下に置いてもよい。これにより『(?P<group>[^』]+)』のカードを(?P<n>\d+)枚以上デッキの下に置いた場合、ライブ終了時まで、自分のステージにいる「(?P<name>[^」]+)」1人は(?P<blades>(?:<\(ブレード\)>)+)を得る。")
PAT_BOTH = re.compile(r"自分と相手はそれぞれ、自身の控え室にあるすべてのメンバーカードをシャッフルし、自身のデッキの下に置く。これにより自分と相手のカードが合計(?P<n>\d+)枚以上デッキの下に置かれた場合、自分の控え室からライブカードを(?P<retrieve>\d+)枚手札に加え、ライブ終了時まで、(?P<blades>(?:<\(ブレード\)>)+)を得る。")


def iter_clauses(card):
    for ab in card.get("abilities") or []:
        for cl in ab.get("clauses") or []:
            yield ab, cl


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compiled", default="./llocg_db_out_full/cards_compiled_v7h.json")
    ap.add_argument("--outdir", default="./loveca_reports")
    ns = ap.parse_args()
    compiled = Path(ns.compiled)
    outdir = Path(ns.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    data = json.loads(compiled.read_text(encoding="utf-8"))
    cards = data.get("cards") or data
    rows = []
    for card in cards:
        for ab, cl in iter_clauses(card):
            eff = str(cl.get("effect_template") or cl.get("raw") or "").strip()
            if "控え室にあるすべてのメンバーカード" not in eff or "デッキの下" not in eff:
                continue
            status = "needs_audit_unmatched_mass_bottom"
            if PAT_FANFARE.search(eff):
                status = "implemented_optional_own_all_members_group_threshold_stage_named_blade"
            elif PAT_BOTH.search(eff):
                status = "implemented_both_players_all_members_threshold_retrieve_live_blade"
            rows.append({
                "cardnumber": card.get("cardnumber", ""),
                "cardname": card.get("cardname", ""),
                "card_type": card.get("card_type", card.get("card_type_norm", "")),
                "trigger": ab.get("trigger", ""),
                "status": status,
                "effect": eff,
            })
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    csv_path = outdir / "loveca_mass_green_bottom_family_audit_20260605a.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["cardnumber", "cardname", "card_type", "trigger", "status", "effect"])
        w.writeheader(); w.writerows(rows)
    md_path = outdir / "loveca_mass_green_bottom_family_audit_20260605a.md"
    lines = [
        "# Loveca mass waiting-room member bottomdeck family audit 20260605a",
        "",
        f"BUILD_TAG: `{BUILD_TAG}`",
        f"compiled: `{compiled}`",
        "",
        "## Summary",
        "",
        f"candidates: {len(rows)}",
    ]
    for k in sorted(counts):
        lines.append(f"- {k}: {counts[k]}")
    lines += ["", "## Rows", ""]
    for r in rows:
        lines.append(f"- `{r['cardnumber']}` {r['cardname']} — **{r['status']}**")
        lines.append(f"  - trigger: {r['trigger']}")
        lines.append(f"  - effect: {r['effect']}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] wrote {csv_path}")
    print(f"[OK] wrote {md_path}")


if __name__ == "__main__":
    main()
