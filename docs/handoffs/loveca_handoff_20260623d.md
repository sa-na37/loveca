# Loveca handoff 20260623d

## Scope

Added a generic reveal-until-live route and consolidated debug commands/checklists.

## Runtime changes

- Updated `BUILD_TAG` to `topk_reveal_until_and_debug_20260623d`.
- Added matcher/resolver:
  - `reveal_until_live_to_hand_rest_waiting`
  - op: `reveal_until_match_to_hand_rest_waiting`
- Behavior:
  - reveal cards from deck top until the first live card is found
  - put that live card into hand
  - put all earlier revealed cards into waiting room
  - use normal deck refresh if the deck runs out during reveal

## Newly covered top-k audit example

- `PL!N-bp1-011` ミア・テイラー — `reveal_until_live_to_hand_rest_waiting`

## Audit updates

- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
  - `implemented_existing_topk_or_deck`: 96 -> 97
  - `needs_audit_unmatched_topk`: 42 -> 41
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
  - updated `PL!N-bp1-011` from `needs_audit_unmatched_topk` to `implemented_existing_topk_or_deck`

## Debug memo

- Added `docs/debug/loveca_debug_commands_20260623.md`
- This file consolidates compile checks, CSV count checks, focused UI debug targets, and a small DB-backed matcher smoke check for the implementation work from 20260622h through 20260623d.

## Checks

- Loaded the actual runtime DB and confirmed `PL!N-bp1-011` matches the new route.
- Engine-only reveal-until-live test moved two non-live cards to waiting room and the first live card to hand.

## Notes

- No file moves, deletions, or new backups were performed in this step.
