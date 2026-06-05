#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit MIRACLE WAVE style live-success score-set effects."""
from __future__ import annotations

BUILD_TAG = "audit_miracle_wave_family_20260605a"

import argparse
import csv
import json
from pathlib import Path

PATTERN_TERMS = (
    "ブレードハートを持たないカードが0枚",
    "余剰ハートを2つ以上",
    "このカードのスコアは4になる",
)


def iter_cards(payload):
    if isinstance(payload, dict) and isinstance(payload.get("cards"), list):
        return payload["cards"]
    if isinstance(payload, list):
        return payload
    return []


def effect_texts(card):
    for ab in card.get("abilities", []) or []:
        for cl in ab.get("clauses", []) or []:
            raw = str(cl.get("raw") or cl.get("effect_template") or "").strip()
            if raw:
                yield str(ab.get("trigger") or ""), raw


def classify(text: str) -> str:
    if all(t in text for t in PATTERN_TERMS):
        return "implemented_score_set_no_bladeheart_or_excess"
    return "needs_audit_unmatched"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compiled", default="./llocg_db_out_full/cards_compiled_v7h.json")
    ap.add_argument("--outdir", default="./loveca_reports")
    args = ap.parse_args()
    compiled = Path(args.compiled)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    data = json.loads(compiled.read_text(encoding="utf-8"))
    rows = []
    for card in iter_cards(data):
        for trigger, text in effect_texts(card):
            if any(t in text for t in PATTERN_TERMS):
                rows.append({
                    "cardnumber": card.get("cardnumber", ""),
                    "cardname": card.get("cardname", ""),
                    "trigger": trigger,
                    "status": classify(text),
                    "text": text.replace("\n", " "),
                })
    csv_path = outdir / "loveca_miracle_wave_family_audit_20260605a.csv"
    md_path = outdir / "loveca_miracle_wave_family_audit_20260605a.md"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["cardnumber", "cardname", "trigger", "status", "text"])
        w.writeheader(); w.writerows(rows)
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    lines = ["# MIRACLE WAVE family audit 20260605a", "", f"candidates: {len(rows)}"]
    for k in sorted(counts):
        lines.append(f"- {k}: {counts[k]}")
    lines.append("")
    for r in rows:
        lines.append(f"- `{r['cardnumber']}` {r['cardname']} [{r['trigger']}] — {r['status']}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] wrote: {csv_path}")
    print(f"[OK] wrote: {md_path}")


if __name__ == "__main__":
    main()
