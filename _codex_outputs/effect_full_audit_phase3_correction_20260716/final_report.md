PENDING_RESIDUE_FIXED_AND_REGRESSION_PASSED

## Summary

The Phase 3 accounting contradiction for `PL!-PR-005#A01#P3_choice_required` was corrected in the new correction output directory, then the runtime was fixed and regression tested.

## Runtime fix

- Mandatory `choose_enter_effect_mode` can no longer be advanced by NEXT without a branch choice.
- Empty/invalid resolution keeps the pending active and displays a required-selection message.
- A valid branch choice resolves normally and clears pending after the branch completes.
- Optional effects and pay/skip style prompts remain skippable.
- Opponent wait continues to use the aggregate count input model, which is the current formal specification.

## Regression Results

- mandatory_choice_next_and_invalid: PASS {"invalid_kept_pending": true, "next_blocked": true, "undo_ok": true, "valid_choice_resolved": true}
- PL!-PR-005_draw_discard: PASS {"hand_count": 0, "pending_kind": "", "undo_ok": true}
- PL!-PR-006_draw_discard: PASS {"hand_count": 0, "pending_kind": "", "undo_ok": true}
- PL!-PR-008_draw_discard: PASS {"hand_count": 0, "pending_kind": "", "undo_ok": true}
- PL!-PR-005_opponent_wait_count0: PASS {"expected": 2, "got": 2, "initial": 0, "pending_kind": "", "undo_ok": true}
- PL!-PR-005_opponent_wait_count1: PASS {"expected": 3, "got": 3, "initial": 1, "pending_kind": "", "undo_ok": true}
- PL!-PR-005_opponent_wait_existing1_plus2: PASS {"expected": 3, "got": 3, "initial": 1, "pending_kind": "", "undo_ok": true}
- PL!-PR-005_opponent_wait_count2: PASS {"expected": 3, "got": 3, "initial": 2, "pending_kind": "", "undo_ok": true}
- optional_confirm_effect_skip: PASS {"pending_kind": "", "pending_text": "", "undo_ok": true}
- optional_pay_or_skip_next: PASS {"pending_kind": "", "pending_text": "", "undo_ok": true}

## UI Evidence

- `regression/ui/mandatory_choice_next_block.png`: popup remains with required-selection message after NEXT without choice.
- `regression/ui/mandatory_choice_after_valid_resolution.png`: popup is gone after valid branch resolution.

## Outputs

- Corrected Phase 3 files: `corrected_phase3/`
- Runtime patch: `patch/patch.diff`
- Regression CSV: `regression/regression_test_results.csv`
- Before/after evidence: `evidence/`
