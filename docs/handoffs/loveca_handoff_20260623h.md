# Loveca handoff 20260623h

## Summary

Integrated the current debug-command updates into the main debug memo, processed user debug comments, and fixed the runtime/UI issues called out by those comments.

## Changed runtime files

- `llocg_ui/engine.py`
- `llocg_ui/server.py`

## BUILD_TAG

- `debug_memo_integration_feedback_20260623h`

## Debug memo

- Integrated `docs/debug/loveca_debug_commands_current_updates_20260623.md` into `docs/debug/loveca_debug_commands_20260623.md`.
- Cleared the current-updates file back to its empty pending placeholder.
- Moved confirmed OK commands to the resolved confirmations list.
- Kept active commands that need re-check after command/runtime fixes.
- Ensured user-facing `＊` comments sit outside executable bash command blocks.

## Fixed

- Auto confirmation condition labels now show Japanese text instead of internal keys.
- Heart/blade tokens in confirmation text are normalized for texticon rendering.
- Waiting-room-to-deck-top pending text now includes source and effect text.
- Reveal-until-live effects now show a result popup with revealed cards and destination summary.
- Reorder-all top-k effects now use the selected-frame reorder popup with final confirmation.
- Optional hand-discard cost display no longer repeats the full condition/effect text.
- Debug commands for `PL!HS-bp5-001`, `PL!HS-pb1-004`, `PL!HS-pb1-027`, and `PL!-bp6-016` were corrected for their intended check flow.

## Deferred

- Window-resize-wide layout follow-up was left as a separate UI-wide task.

## Checks

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Parsed all bash blocks in `docs/debug/loveca_debug_commands_20260623.md` with `bash -n`.
- Extracted embedded UI script from `llocg_ui/server.py` and checked it with bundled Node.js `--check`.
- Internal engine-only feedback smoke check for the updated pending/result text and reorder-all flow.

All checks passed.
