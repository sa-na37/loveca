# Loveca handoff 20260623i

## Summary

Added a generic top-k route for filtered up-to multi-pick effects and covered `PL!S-bp2-005`.

## Changed runtime files

- `llocg_ui/engine.py`
- `llocg_ui/server.py`

## BUILD_TAG

- `topk_filtered_up_to_multi_pick_20260623i`

## Implemented

- `look_top_k_optional_member_heart_any_color_upto_n`
- Filtered `choose_from_topk` pending now supports min/max pick ranges.
- UI multi-pick selection now allows `0..N` ranges when the pending says `min_pick_count=0`.

## Covered

- `PL!S-bp2-005`: look at top 7 cards, choose up to 3 member cards with red/green/blue hearts, put the rest into waiting room.

## Debug memo

Added a launch command to `docs/debug/loveca_debug_commands_current_updates_20260623.md`.

## Checks

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Matcher check for `PL!S-bp2-005`.
- Internal engine smoke check for selecting two cards and choosing zero cards.

All checks passed.
