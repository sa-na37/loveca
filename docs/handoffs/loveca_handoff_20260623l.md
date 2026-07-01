# Loveca handoff 20260623l

## Summary

- Added a generic top-k route for effects that select up to N cards with at most one card per group name.
- Covered `PL!SP-bp5-007` 米女メイ.

## Runtime Changes

- `llocg_ui/engine.py`
  - BUILD_TAG: `distinct_group_topk_pick_20260623l`
  - Added pattern `look_top_k_optional_distinct_group_upto_n`.
  - `choose_from_topk` pending can now carry `unique_by_group`.
  - Multi-pick resolution rejects duplicate group names.
- `llocg_ui/server.py`
  - BUILD_TAG / APP_VERSION: `distinct_group_topk_pick_20260623l`
  - Multi-pick top-k UI disables unselected candidates whose group name is already selected.

## Reports And Debug

- Updated `loveca_reports/loveca_topk_complex_family_audit_20260604a.*`.
  - `PL!SP-bp5-007` moved from `needs_audit_unmatched_topk` to `implemented_distinct_group_upto_n`.
  - Remaining unmatched top-k count is now 25.
- Added the `PL!SP-bp5-007` debug command to `docs/debug/loveca_debug_commands_current_updates_20260623.md`.

## Checks

- Internal matcher check for `PL!SP-bp5-007`.
- Internal engine smoke for valid distinct-group multi-pick.
- Internal engine smoke for invalid duplicate-group multi-pick.

## Notes

- No file move, deletion, backup creation, or local cleanup was done in this pass.
- Existing unstaged `llocg_fetch_all_card_images.py` and root `loveca_final_application_spec_updated_20260623.md` were left untouched.
