#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit Loveca self/opponent waiting-room-to-deck-bottom family."""
from __future__ import annotations

BUILD_TAG = "audit_choose_player_green_bottom_family_20260605a"

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

RE_MEMBER = re.compile(r"自分か相手を選ぶ。自分は、そのプレイヤーの控え室にあるメンバーカードを\d+枚まで、好きな順番でデッキの一番下に置く。")
RE_LIVE_DRAW = re.compile(r"自分か相手を選ぶ。自分は、そのプレイヤーの控え室にあるライブカードを\d+枚、そのプレイヤーのデッキの一番下に置く。そうした場合、自分はカードを\d+枚引く。")

def iter_clauses(cards: Iterable[Dict[str, Any]]):
    for c in cards:
        for ab in c.get("abilities", []) or []:
            for cl in ab.get("clauses", []) or []:
                eff = str(cl.get("effect_template") or cl.get("raw") or "").strip()
                cost = str(cl.get("cost_template") or "").strip()
                raw = str(cl.get("raw") or "").strip()
                if "自分か相手を選ぶ" not in eff and "自分か相手を選ぶ" not in raw:
                    continue
                yield {
                    "cardnumber": c.get("cardnumber", ""),
                    "cardname": c.get("cardname", ""),
                    "card_type": c.get("card_type", ""),
                    "ability_type": ab.get("ability_type", ""),
                    "trigger": ab.get("trigger", ""),
                    "conditions": ab.get("conditions", ""),
                    "cost_template": cost,
                    "effect_template": eff,
                    "raw": raw,
                }

def status_for(row: Dict[str, Any]) -> str:
    eff = row["effect_template"]
    if RE_MEMBER.fullmatch(eff):
        return "implemented_choose_player_member_upto_bottom"
    if RE_LIVE_DRAW.fullmatch(eff):
        return "implemented_choose_player_live_bottom_draw"
    return "needs_audit_unmatched_choose_player"

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compiled", default="./llocg_db_out_full/cards_compiled_v7h.json")
    ap.add_argument("--outdir", default="./loveca_reports")
    ns = ap.parse_args()

    compiled = Path(ns.compiled)
    data = json.loads(compiled.read_text(encoding="utf-8"))
    cards = data.get("cards", data if isinstance(data, list) else [])
    rows: List[Dict[str, Any]] = []
    for row in iter_clauses(cards):
        row["status"] = status_for(row)
        rows.append(row)

    outdir = Path(ns.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "loveca_choose_player_green_bottom_family_audit_20260605a.csv"
    md_path = outdir / "loveca_choose_player_green_bottom_family_audit_20260605a.md"

    fields = ["cardnumber", "cardname", "card_type", "ability_type", "trigger", "conditions", "status", "cost_template", "effect_template", "raw"]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})

    counts: Dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    lines = [
        "# Loveca choose-player green-bottom family audit 20260605a",
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
        if r.get("cost_template"):
            lines.append(f"  - cost: {r['cost_template']}")
        lines.append(f"  - effect: {r['effect_template']}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] wrote {md_path}")
    print(f"[OK] wrote {csv_path}")

if __name__ == "__main__":
    main()
