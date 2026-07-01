# Loveca handoff 20260623k

## Summary

- Debug-response pass for the user `デバッグ対応` workflow.
- No pending command body existed in `docs/debug/loveca_debug_commands_current_updates_20260623.md`, so the main debug memo was updated from user comments already present in `docs/debug/loveca_debug_commands_20260623.md`.
- User-confirmed OK commands were moved to the resolved list.
- `PL!-bp6-002` remains active for UI recheck after runtime/command correction.

## Runtime Changes

- `llocg_ui/engine.py`
  - BUILD_TAG: `debug_response_filter_reorder_20260623k`
  - `group_no_ability_or_body` now treats only `ability_type` containing `常時` as the <常時> branch.
  - BODY-zone activated abilities such as `PL!-sd1-008` no longer match the <常時> branch.
- `llocg_ui/server.py`
  - BUILD_TAG / APP_VERSION: `debug_response_filter_reorder_20260623k`
  - Reorder popup card drops now insert before/after the target card based on drag direction/card half.

## Debug Memo Changes

- Added Codex-comment rule: use `※` for Codex response comments, keeping user `＊` comments distinct.
- Moved these to resolved confirmations:
  - `PL!HS-pb1-004`
  - `PL!HS-pb1-027`
  - `PL!-bp6-016`
  - `PL!S-bp6-005`
  - `PL!S-bp2-005`
- Updated active `PL!-bp6-002` command:
  - top cards: `PL!-bp3-015`, `PL!-bp3-002`, `PL!HS-PR-001`
  - user `＊挙動問題あり` comment preserved
  - Codex fix/recheck comments use `※`

## Checks

- Python compile
- Internal engine smoke for `PL!-bp6-002` no-ability / activated BODY / always BODY filtering
- Embedded UI script syntax check
- Debug memo bash block syntax check
- Forbidden debug option scan
- `git diff --check`

## Notes

- No file move, deletion, backup creation, or local cleanup was done in this pass.
- Existing unstaged `llocg_fetch_all_card_images.py` was left untouched.
