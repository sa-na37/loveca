# Loveca handoff 20260625a

## Summary

- Added a generic live-start route for revealing deck top, checking member cost, and then position-changing the source member.
- Covered `PL!N-pb1-004` 朝香果林.
- Reflected existing live-success excess-heart top reorder coverage for `PL!HS-bp6-028`.

## Runtime Changes

- `llocg_ui/engine.py`
  - BUILD_TAG: `reveal_top_cost_member_position_20260625a`
  - Added `reveal_top1_cost_le_member_hand_then_self_position_change`.
  - The route moves a matching cost-limited member to hand, shows the revealed-card ack, then uses the existing `position_change` pending for the source member.
  - Non-matching revealed cards go to waiting room with a revealed-card ack.
- `tools/audit_topk_complex_family_20260604.py`
  - Added focused classification for the new reveal-top position-change route.
  - Added current-implementation override for `PL!HS-bp6-028`.

## Reports And Debug

- Updated `loveca_reports/loveca_topk_complex_family_audit_20260604a.*`.
  - `PL!N-pb1-004` moved to `implemented_reveal_top_cost_member_position_change`.
  - `PL!HS-bp6-028` is reflected as `implemented_live_success_excess_top_reorder`.
  - Remaining unmatched top-k-family count is now 18.
- Added the `PL!N-pb1-004` debug command to `docs/debug/loveca_debug_commands_current_updates_20260623.md`.

## Checks

- Internal matcher check for `PL!N-pb1-004`.
- Internal engine smoke for matching top member -> hand -> revealed ack -> source position change.
- Internal engine smoke for non-matching top card -> waiting room.

## Notes

- No file move, deletion, backup creation, or local cleanup was done in this pass.
- Existing unstaged `llocg_fetch_all_card_images.py`, untracked root markdown/handoff files, and `llocg_ui/views.py` were left untouched.
