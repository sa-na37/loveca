# Loveca handoff 20260622f

## Status
- 20260622e is treated as the current base.
- User confirmed debug case 2 behavior is OK.
- Remaining issue: effect confirmation popup duplicated the same executing effect text in the top prompt and in the lower 「発動する効果」 box.

## Change
- Changed `llocg_ui/server.py` only.
- BUILD_TAG: `pending_modal_no_duplicate_effect_detail_20260622f`

## Intent
- For `confirm_effect` / `pay_or_skip` pending modals, the concrete executing effect is already displayed in the main prompt line.
- Suppress the lower duplicate 「発動する効果」 box for those confirmation modals.
- Also suppress the lower box when the main prompt already contains the same effect text.
- No engine/effect behavior changes.

## Notes
- Debug commands are intentionally not embedded in this handoff file. They should be provided in chat only.
