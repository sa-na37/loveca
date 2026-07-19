#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: tier3_pilot3_result_validator_20260717a
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "effect_full_audit_tier3_pilot3_complete_gate_20260717"
ALLOWED = {
    "IMPLEMENTED_AND_REACHABLE", "IMPLEMENTED_RUNTIME_UI_PENDING", "TRIGGER_REACHED_RESOLVER_BLOCKED",
    "UI_ROUTE_MISSING", "GENERIC_ROUTE_TEXT_NOT_MATCHED", "NOT_IMPLEMENTED_CONFIRMED",
    "BLOCKED_BY_ENGINE_CAPABILITY", "RULE_INTERPRETATION_REQUIRED", "SETUP_DESIGN_ERROR",
}


def main() -> int:
    errors = []
    rows = list(csv.DictReader((OUT / "pilot3_results.csv").open(encoding="utf-8")))
    if len(rows) != 3:
        errors.append(f"row_count={len(rows)}")
    for r in rows:
        cid = r["canonical_id"]
        if r["final_status"] not in ALLOWED:
            errors.append(f"{cid}:bad_status")
        if r["design_validator_passed"] != "true":
            errors.append(f"{cid}:design_not_passed")
        if not r["condition_positive_observed"] or not r["condition_negative_observed"]:
            errors.append(f"{cid}:condition_missing")
        if r["final_status"] == "IMPLEMENTED_AND_REACHABLE":
            for col in ["effect_completed_positive", "effect_absent_negative", "pending_sequence_completed"]:
                if r[col] != "true":
                    errors.append(f"{cid}:implemented_requires_{col}")
            if r["ui_required"] == "true" and r["browser_passed"] != "true":
                errors.append(f"{cid}:implemented_requires_browser")
            if r["undo_applicable"] == "true" and r["undo_passed"] != "true":
                errors.append(f"{cid}:implemented_requires_undo")
        if r["final_status"] == "TRIGGER_REACHED_RESOLVER_BLOCKED":
            if r["trigger_executed"] != "true" or r["resolver_entered"] != "true":
                errors.append(f"{cid}:blocked_requires_trigger_and_resolver")
            if r["effect_completed_positive"] == "true":
                errors.append(f"{cid}:blocked_but_completed")
            if "not matchable" not in r["reason"] and "absent" not in r["reason"] and "not created" not in r["reason"]:
                errors.append(f"{cid}:blocked_reason_not_specific")
        if not (OUT / r["evidence"]).exists():
            errors.append(f"{cid}:evidence_missing")
    out = OUT / "validation" / "result_validation.txt"
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
