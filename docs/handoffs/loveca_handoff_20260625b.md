# Loveca handoff 20260625b

## Summary

- Added generic deck-top reveal and stage-count top-card routes.
- Covered `PL!N-pb1-004` 朝香果林 and `PL!HS-bp6-001` 日野下花帆.
- Reflected existing live-success excess-heart top reorder coverage for `PL!HS-bp6-028`.

## Runtime Changes

- `llocg_ui/engine.py`
  - BUILD_TAG: `reveal_position_stagecount_keep_top_20260625b`
  - Added `reveal_top1_cost_le_member_hand_then_self_position_change`.
  - Added `look_top_stage_member_count_plus_keep_one_top_rest_waiting`.
  - Reused existing `show_revealed_cards_ack`, `position_change`, and `choose_top_keep_one` pending flows.
- `tools/audit_topk_complex_family_20260604.py`
  - Added focused classifications for both new routes.
  - Added current-implementation override for `PL!HS-bp6-028`.

## Reports And Debug

- Updated `loveca_reports/loveca_topk_complex_family_audit_20260604a.*`.
  - `PL!N-pb1-004` moved to `implemented_reveal_top_cost_member_position_change`.
  - `PL!HS-bp6-001` moved to `implemented_stage_count_top_keep_one`.
  - `PL!HS-bp6-028` is reflected as `implemented_live_success_excess_top_reorder`.
  - Remaining unmatched top-k-family count is now 17.
- Added debug commands for `PL!N-pb1-004` and `PL!HS-bp6-001` to `docs/debug/loveca_debug_commands_current_updates_20260623.md`.

## Checks

- Internal matcher check for `PL!N-pb1-004`.
- Internal engine smoke for matching top member -> hand -> revealed ack -> source position change.
- Internal engine smoke for non-matching top card -> waiting room.
- Internal matcher check for `PL!HS-bp6-001`.
- Internal engine smoke for stage member count +2 -> choose one deck top -> rest waiting room.

## Notes

- No file move, deletion, backup creation, or local cleanup was done in this pass.
- Existing unstaged `llocg_fetch_all_card_images.py`, untracked root markdown/handoff files, and `llocg_ui/views.py` were left untouched.
