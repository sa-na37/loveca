# Loveca handoff 20260623c

## Scope

Added more generic coverage for remaining top-k audit items in `llocg_ui/engine.py`.

## Runtime changes

- Updated `BUILD_TAG` to `topk_mill_retrieve_and_reorder_20260623c`.
- Added generic matcher/resolver support for:
  - mill top K cards, then retrieve one waiting-room card by kind/group
  - look at top K cards, then return all of them to deck top in chosen order
  - if a stage group member exists, optionally mill top K cards
  - direct `手札を1枚控え室に置いてもよい。<effect>` wrapper text
- Added pending resolution kinds:
  - `reorder_topk_all`
  - `confirm_mill_top_to_green`

## Newly covered top-k audit examples

- `PL!-bp5-010` 高坂穂乃果 — `mill_top_k_then_retrieve_waiting_group_type`
- `PL!HS-pb1-004` 百生吟子 — `mill_top_k_then_retrieve_waiting_group_type`
- `PL!N-bp1-009` 天王寺璃奈 — `mill_top_k_then_retrieve_waiting_type`
- `PL!-pb1-006` 西木野真姫 — existing `topdeck_green_live_group_upto1_then_draw_if_opponent_wait_exists`
- `PL!HS-pb1-027` ユメワズライ — `stage_group_optional_mill_top_k`
- `PL!-bp6-016` 東條希 — `look_top_k_reorder_all_on_top`
- `PL!-pb1-016` 東條希 — `optional_discard_one_from_hand_then_effect_direct` + `look_top_k_optional_group`

## Audit updates

- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
  - `implemented_existing_topk_or_deck`: 89 -> 96
  - `needs_audit_unmatched_topk`: 49 -> 42
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
  - updated the seven examples above from `needs_audit_unmatched_topk` to `implemented_existing_topk_or_deck`

## Checks

- Loaded the actual runtime DB and confirmed all seven target card texts match the expected route.
- Engine-only checks confirmed:
  - mill-then-retrieve queues a waiting-room picker after milling
  - reorder-all queues `reorder_topk_all`
  - optional group mill queues `confirm_mill_top_to_green` when the stage condition is met

## Notes

- No file moves, deletions, or new backups were performed in this step.
