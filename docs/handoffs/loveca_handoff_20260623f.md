# Loveca handoff 20260623f

## Summary

Processed the user debug comments in `docs/debug/loveca_debug_commands_20260623.md` and implemented the requested generalized UI/cost fixes.

## Changed runtime files

- `llocg_ui/engine.py`
- `llocg_ui/server.py`

## BUILD_TAG

- `debug_feedback_ui_and_costs_20260623f`

## Implemented

- Classified `このメンバーをウェイトにし、手札を1枚控え室に置いてもよい` as self WAIT plus hand discard, not self-to-waiting-room.
- Added a confirmation popup for automatic `mill_top_conditional_followup` resolution, including revealed cards, condition result, and follow-up result.
- Generalized multi-pick top-k UI so cards can be selected with frames/order badges and confirmed once.
- Generalized enter-effect mode UI so choices appear as framed `①` / `②` options below the effect text.
- Added a debug comment handling rule and moved confirmed-ok commands into the resolved list.

## Debug memo status

Resolved entries:

- `LL-bp6-001`
- `PL!HS-cl1-004`
- `PL!-sd1-019`
- `PL!HS-cl1-001`

Still active for re-check after fixes:

- `PL!-bp5-222` / `PL!HS-cl1-007`
- `PL!HS-bp5-008`
- `PL!-sd1-007`

## Checks

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Extracted embedded UI script from `llocg_ui/server.py` and checked it with bundled Node.js `--check`.
- Engine-only WAIT cost regression checks for `PL!-bp5-222` and `PL!HS-bp5-008`.
- Engine-only automatic confirmation popup check for `PL!-sd1-007`.

All checks passed.
