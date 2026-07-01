# Loveca handoff 20260623g

## Summary

Added four small generic routes for remaining top-k / deck-top text variants and recorded runnable checks in the current-updates debug file.

## Changed runtime files

- `llocg_ui/engine.py`

## BUILD_TAG

- `topk_filter_variants_20260623g`

## Implemented

- `PL!N-bp4-021`: waiting-room card optional topdeck text now maps to the existing `topdeck_from_green` pending.
- `PL!S-bp6-005`: top-k filter for members that have all specified heart colors.
- `PL!-bp6-002`: top-k filter for no-ability group cards or BODY/常時 group cards.
- `PL!SP-bp5-013`: top-k filter for group members or blade-heart members of another group.

## Debug memo

Added individual launch commands to `docs/debug/loveca_debug_commands_current_updates_20260623.md` for:

- `PL!-bp6-002`
- `PL!S-bp6-005`
- `PL!SP-bp5-013`
- `PL!N-bp4-021`

## Checks

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Internal DB-backed matcher and pending smoke checks for all four examples.
- CSV status count check for `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`.

All checks passed.
