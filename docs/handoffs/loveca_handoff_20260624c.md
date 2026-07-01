# Loveca handoff 20260624c

## Summary

- Added a generic route for effects that mill cards from deck top, then optionally place a waiting-room LIVE at a fixed deck position.
- Covered `PL!N-bp5-021` 天王寺璃奈.
- Updated the top-k audit to reflect current timing-specific coverage for `PL!-bp6-007` and `PL!S-sd1-009`.

## Runtime Changes

- `llocg_ui/engine.py`
  - BUILD_TAG: `mill_top2_live_deck4th_20260624c`
  - Added `mill_top_k_then_waiting_live_to_deck_nth_optional`.
  - Added `choose_live_from_green_to_deck_nth` pending resolution.
- `llocg_ui/server.py`
  - BUILD_TAG / APP_VERSION: `mill_top2_live_deck4th_20260624c`
  - `choose_live_from_green_to_deck_nth` uses the existing card-selection UI.
- `tools/audit_topk_complex_family_20260604.py`
  - Added the new rule id to focused classifications.
  - Added current-implementation overrides for timing-specific routes not matched by `_match_effect_template`.

## Reports And Debug

- Updated `loveca_reports/loveca_topk_complex_family_audit_20260604a.*`.
  - `PL!N-bp5-021` moved to `implemented_mill_top_then_live_deck_nth`.
  - `PL!-bp6-007` is reflected as `implemented_live_success_reveal_top_no_bladeheart_score`.
  - `PL!S-sd1-009` is reflected as `implemented_live_start_hand_group_top_bottom_blade`.
  - Remaining unmatched top-k-family count is now 20.
- Added the `PL!N-bp5-021` debug command to `docs/debug/loveca_debug_commands_current_updates_20260623.md`.

## Checks

- Internal matcher check for `PL!N-bp5-021`.
- Internal engine smoke for mill 2 -> pending LIVE choice -> selected LIVE inserted as 4th deck card.

## Notes

- No file move, deletion, backup creation, or local cleanup was done in this pass.
- Existing unstaged `llocg_fetch_all_card_images.py` and root untracked markdown files were left untouched.
