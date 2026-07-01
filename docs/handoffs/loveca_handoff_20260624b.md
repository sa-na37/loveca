# Loveca handoff 20260624b

## Summary

- Added a generic live-start route for stage-cost comparison effects that draw cards and then put a hand card on deck top.
- Covered `PL!N-bp4-009` 天王寺璃奈.

## Runtime Changes

- `llocg_ui/engine.py`
  - BUILD_TAG: `stage_cost_lower_draw2_top_20260624b`
  - Added `draw_then_hand_to_deck_top`.
  - Added `hand_to_deck_top` pending resolution.
- `llocg_ui/server.py`
  - BUILD_TAG / APP_VERSION: `stage_cost_lower_draw2_top_20260624b`
  - `hand_to_deck_top` uses the existing card-selection UI.
- `llocg_ui/effects/registry.py`
  - BUILD_TAG: `stage_cost_lower_draw2_top_20260624b`
  - Added `live_start_my_cost_lower_draw2_hand_top1`.
- `llocg_ui/effects/live_start.py`
  - BUILD_TAG: `stage_cost_lower_draw2_top_20260624b`
  - Added stage-cost lower draw2/topdeck handling with manual confirm fallback.

## Reports And Debug

- Updated `loveca_reports/loveca_topk_complex_family_audit_20260604a.*`.
  - `PL!N-bp4-009` moved from `needs_audit_unmatched_topk` to `implemented_stage_cost_lower_draw2_hand_top1`.
  - Remaining unmatched top-k-family count is now 23.
- Added the `PL!N-bp4-009` debug command to `docs/debug/loveca_debug_commands_current_updates_20260623.md`.

## Checks

- Internal matcher check for `PL!N-bp4-009`.
- Internal engine smoke for confirm -> draw 2 -> hand card to deck top.

## Notes

- No file move, deletion, backup creation, or local cleanup was done in this pass.
- Existing unstaged `llocg_fetch_all_card_images.py` and root `loveca_final_application_spec_updated_20260623.md` were left untouched.
