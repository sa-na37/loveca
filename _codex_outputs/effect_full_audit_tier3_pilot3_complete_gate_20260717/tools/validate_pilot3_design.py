#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: tier3_pilot3_design_validator_20260717a
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "effect_full_audit_tier3_pilot3_complete_gate_20260717"
DB = ROOT / "llocg_db_out_full" / "cards_compiled_v7h.json"
FORBIDDEN = [
    "exact named", "as stated", "depending on text", "appropriate card", "required card",
    "prepare condition", "apply effect", "state change", "route change", "likely",
    "etc.", "TBD", "TODO", "unknown",
]
REQUIRED = [
    "canonical_id", "cardnumber", "cardname", "trigger", "effect_text", "ability_summary",
    "source_zone", "positive_condition", "negative_condition_removed", "required_stage_L",
    "required_stage_C", "required_stage_R", "required_hand", "required_green", "required_deck_order",
    "required_success_zone", "required_live_cards", "required_energy_active", "required_energy_wait",
    "required_opponent_inputs", "required_history", "required_attached_energy", "action_sequence",
    "expected_pending_sequence", "condition_probe", "effect_probe", "expected_positive_delta",
    "expected_negative_delta", "cleanup_applicable", "cleanup_point", "undo_applicable", "ui_required",
    "browser_steps",
]


def concrete_delta(s: str) -> bool:
    if not s or s == "NOT_APPLICABLE":
        return False
    return bool(re.search(r"(=|\+|-|remains|temp_blade|effective_cost|energy_|count)", s))


def main() -> int:
    errors = []
    path = OUT / "pilot3_setup_design.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8"))) if path.exists() else []
    db = {c["cardnumber"] for c in json.loads(DB.read_text(encoding="utf-8")).get("cards", [])}
    if len(rows) != 3:
        errors.append(f"row_count={len(rows)} expected=3")
    if rows:
        missing_cols = [c for c in REQUIRED if c not in rows[0]]
        if missing_cols:
            errors.append(f"missing_columns={missing_cols}")
    triggers = {r.get("trigger", "") for r in rows}
    if not (("常時" in triggers or "BODY" in triggers) and "起動" in triggers and "ライブ開始時" in triggers):
        errors.append(f"trigger_mix_invalid={sorted(triggers)}")
    for idx, r in enumerate(rows, 1):
        for col in REQUIRED:
            if not str(r.get(col, "")).strip():
                errors.append(f"row{idx}:{col}:blank")
        blob = json.dumps(r, ensure_ascii=False)
        for word in FORBIDDEN:
            if word in blob:
                errors.append(f"row{idx}:forbidden:{word}")
        if r.get("cardnumber") not in db:
            errors.append(f"row{idx}:card_missing:{r.get('cardnumber')}")
        if r.get("positive_condition") == r.get("negative_condition_removed"):
            errors.append(f"row{idx}:positive_negative_same")
        if not concrete_delta(r.get("expected_positive_delta", "")):
            errors.append(f"row{idx}:positive_delta_not_concrete")
        if not concrete_delta(r.get("expected_negative_delta", "")):
            errors.append(f"row{idx}:negative_delta_not_concrete")
        if ";" not in r.get("action_sequence", "") and r.get("trigger") != "常時":
            errors.append(f"row{idx}:action_sequence_not_specific")
        if r.get("condition_probe") in {"NOT_APPLICABLE", ""}:
            errors.append(f"row{idx}:condition_probe_missing")
        if r.get("effect_probe") in {"NOT_APPLICABLE", ""}:
            errors.append(f"row{idx}:effect_probe_missing")
    out = OUT / "validation" / "design_validation.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    if errors:
        out.write_text("FAIL\n" + "\n".join(errors) + "\n", encoding="utf-8")
        print(out.read_text(encoding="utf-8"))
        return 1
    out.write_text("PASS\n", encoding="utf-8")
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
