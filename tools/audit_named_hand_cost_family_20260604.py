#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit Loveca named-hand discard cost / cost-result family."""
from __future__ import annotations

BUILD_TAG = "audit_named_hand_cost_family_20260604a"

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, List


def load_cards(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return list(data.get("cards", []) or [])
    return list(data or [])


def classify(cost: str, eff: str) -> str:
    t = (cost or "") + "：" + (eff or "")
    if "手札の「" not in t or "控え室に置いてもよい" not in t:
        return "out_of_scope"
    e = re.sub(r"\s+", "", eff or "")
    if "ライブの合計スコアを+" in e:
        return "implemented_exact3_live_total_score_bonus"
    if "控え室に置いた枚数1枚につき" in e and "ブレード" in e:
        return "implemented_count_to_blade_bonus"
    if "置いたそれらのカードが持つハートの色1つにつき" in e:
        return "implemented_discarded_heart_colors"
    return "needs_audit_unmatched"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compiled", default="./llocg_db_out_full/cards_compiled_v7h.json")
    ap.add_argument("--outdir", default="./loveca_reports")
    args = ap.parse_args()
    compiled = Path(args.compiled)
    if not compiled.exists():
        # Container / ad-hoc fallback.
        alt = Path("/mnt/data/cards_compiled_v7h.json")
        if alt.exists():
            compiled = alt
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cards = load_cards(compiled)
    rows: List[Dict[str, Any]] = []
    for c in cards:
        for ab in c.get("abilities", []) or []:
            for cl in ab.get("clauses", []) or []:
                cost = str(cl.get("cost_template", "") or "")
                eff = str(cl.get("effect_template", "") or "")
                raw = str(cl.get("raw", "") or "")
                if "手札の「" not in (cost + eff + raw) or "控え室に置いてもよい" not in (cost + eff + raw):
                    continue
                rows.append({
                    "cardnumber": c.get("cardnumber", ""),
                    "cardname": c.get("cardname", ""),
                    "ability_type": ab.get("ability_type", ""),
                    "trigger": ab.get("trigger", ""),
                    "cost_template": cost,
                    "effect_template": eff,
                    "status": classify(cost, eff),
                })
    csv_path = outdir / "loveca_named_hand_cost_family_audit_20260604a.csv"
    md_path = outdir / "loveca_named_hand_cost_family_audit_20260604a.md"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["cardnumber","cardname","ability_type","trigger","status","cost_template","effect_template"])
        w.writeheader(); w.writerows(rows)
    counts: Dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    lines = [
        "# Loveca named-hand discard cost / cost-result family audit (2026-06-04a)",
        "",
        f"compiled: `{compiled}`",
        f"candidates: {len(rows)}",
        "",
        "## Summary",
        "",
    ]
    for k in sorted(counts):
        lines.append(f"- {k}: {counts[k]}")
    lines += ["", "## Candidates", ""]
    for r in rows:
        lines += [
            f"### {r['cardnumber']} {r['cardname']}",
            f"- status: `{r['status']}`",
            f"- trigger: `{r['ability_type']} / {r['trigger']}`",
            f"- cost: {r['cost_template']}",
            f"- effect: {r['effect_template']}",
            "",
        ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] wrote: {csv_path}")
    print(f"[OK] wrote: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
