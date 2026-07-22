# Loveca handoff 20260721 - runtime reaudit items

## Context

The former implementation/design hold for `PL!SP-bp5-004` energy-placement trigger has been handled in runtime. `energy_placed_auto` already existed, and the missing work was connecting all ordinary energy-zone placement routes that can add cards from the energy deck to the player's active/wait energy zone. This was implemented in `llocg_ui/engine.py` with `BUILD_TAG=energy_placed_auto_hook_20260721g`.

## Implemented before this handoff

- Connected `_enqueue_energy_placed_auto_triggers` after these ordinary energy-zone placement routes:
  - `energy_put_wait_then_manual_draw_if_no_bladeheart`
  - `both_players_energy_put_wait`
  - `energy_gte_put_wait`
  - `energy_put_wait_under_plus_one_self`
  - `baton_from_group_and_energy_gte_put_wait_energy`
- Confirmed simple wait-energy placement and `energy_gte_put_wait` both trigger `PL!SP-bp5-004[エネルギー配置誘発]`.
- Confirmed `add=0` does not create a false trigger.
- Kept member-under-energy placements out of this trigger because they are not the normal energy zone.

## Runtime reaudit status

- Baton-entered member references are no longer a runtime design blocker. On 20260721, normal `cmd_play` baton flow was corrected/confirmed to pass `entry_origin='baton'` into member-enter trigger collection, and direct live-start template resolution for the baton-entered group-count family now produces `message_ack` for both success and unmet-condition cases.
- `PL!N-bp3-005` / `PL!S-bp5-005` were rechecked through normal command paths that create turn-enter history by actual play/baton operations.
- Remaining baton/turn-enter work is visual/browser confirmation only: operation feel, popup source display, and image/list layout. Keep that in the separated Japanese visual checklist.
- Movement BODY effects should use the normal `position_change -> _record_stage_area_movement -> stage_movement_auto` path. Direct `try_apply_effect_template` is not the correct trigger path for movement event wrappers.

## Separated handoff files

- Broad UI/layout work: `docs/handoffs/loveca_handoff_20260721_broad_ui_layout_items.md`
- Japanese visual verification checklist: `docs/handoffs/loveca_handoff_20260721_visual_confirmation_checklist_ja.md`

## Suggested next order

1. Continue residual runtime audit only for items that still lack a normal command path.
2. Keep visual/browser checks in the separated Japanese checklist.
3. Avoid reopening the energy-placement trigger or baton-entered references as design waits unless a concrete route bypassing the generic ledger/hook is found.
