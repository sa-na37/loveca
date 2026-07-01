# Loveca handoff 20260623j

## Summary

Ran the debug-response workflow: integrated current debug commands, processed user debug comments, fixed runtime issues, and corrected active debug commands.

## Debug response shorthand

When the user says `デバッグ対応`, perform this same workflow:

- integrate `docs/debug/loveca_debug_commands_current_updates_20260623.md` into `docs/debug/loveca_debug_commands_20260623.md`
- move confirmed OK entries to resolved confirmations
- preserve user problem comments while fixing the issue
- update active commands and add `＊修正済み` / `＊再確認待ち`
- clear the current-updates file after integration

## Changed runtime files

- `llocg_ui/engine.py`
- `llocg_ui/server.py`

## BUILD_TAG

- `debug_feedback_integration_fixups_20260623j`

## Fixed

- Waiting-room retrieve filters now use group-or-unit matching.
- `PL!HS-pb1-004` can now find `PL!HS-pb1-027` as a `スリーズブーケ` LIVE candidate.
- Reveal-until result popups now prefer card names, with card numbers in parentheses.

## Debug memo

- Integrated 20260623i `PL!S-bp2-005` command into the main debug memo.
- Cleared the current-updates file.
- Fixed active debug commands for `PL!HS-pb1-004`, `PL!HS-pb1-027`, `PL!-bp6-016`, and `PL!-bp6-002`.
- Repaired the malformed `PL!S-bp6-005` command block.

## Checks

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Internal smoke check for `PL!HS-pb1-004` retrieving `PL!HS-pb1-027`.
- Internal smoke check for card-name-first reveal result text.

All checks passed.
