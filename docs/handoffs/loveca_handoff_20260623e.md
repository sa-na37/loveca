# Loveca handoff 20260623e

## Scope

Added a small top-k matcher variant and reclassified existing top-k routes that the current runtime already supports.

## Runtime changes

- Updated `BUILD_TAG` to `topk_trailing_punctuation_variants_20260623e`.
- `look_top_k_optional_type`, `look_top_k_optional_group`, and `look_top_k_optional_group_type` now accept DB text where the final Japanese period is missing.
- Top-k filtered group checks now use the existing group-or-unit matcher, so unit labels such as `5yncri5e!` are treated as valid filter labels.

## Newly covered top-k audit example

- `PL!SP-pb1-017` 桜小路きな子 — `look_top_k_optional_group`

## Newly reclassified existing routes

- `PL!N-bp4-002` 中須かすみ — `choose_self_or_opponent_top1_mill_optional`
- `PL!N-bp5-009` 天王寺璃奈 — `look_top_k_optional_cost_ge_group_member`
- `PL!S-bp5-006` 津島善子 — `look_top_k_optional_cost_ge_group_member`
- `PL!S-bp6-012` 松浦果南 — `mill_top_k_to_waiting`
- `PL!S-bp6-017` 小原鞠莉 — `mill_top_k_to_waiting`
- `PL!S-bp6-019` Step! ZERO to ONE — `score_draw_then_hand_top_or_bottom_if_all_stage_group`
- `PL!S-pb1-008` 小原鞠莉 — `choose_self_or_opponent_topk_reorder_keep_any`
- `PL!S-sd1-013` 黒澤ダイヤ — `mill_top_k_to_waiting`
- `PL!SP-bp5-008` 若菜四季 — `look_top_k_optional_cost_ge_group_member`

## Audit updates

- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
  - `implemented_existing_topk_or_deck`: 97 -> 107
  - `needs_audit_unmatched_topk`: 41 -> 31
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
  - updated the ten examples above from `needs_audit_unmatched_topk` to implemented route ids

## Debug memo

- Added a runnable `PL!SP-pb1-017` debug command to `docs/debug/loveca_debug_commands_20260623.md`.
- Updated the debug memo matcher-count expectation to `implemented_existing_topk_or_deck=107` and `needs_audit_unmatched_topk=31`.

## Checks

- Loaded the runtime DB and confirmed `PL!SP-pb1-017` matches `look_top_k_optional_group`.
- Engine-only top-k filtered test showed only a `5yncri5e!` unit card in the top five as a selectable candidate.
- Python compile passed for `llocg_ui/engine.py`, `llocg_ui/server.py`, `llocg_ui/engine_effect.py`, and `llocg_ui/effects/*.py`.

## Notes

- No file moves, deletions, or new backups were performed in this step.
