# Implementation notes

No additional runtime changes were made in this completion pass. The previous `choose_enter_effect_mode` pending fix remains in `llocg_ui/engine.py` and `llocg_ui/server.py`.

This pass adds audit-only tooling and artifacts:

- Opponent wait count tests now separate `initial_wait_count` from `selected_count`.
- Selected count values `0`, `1`, and `2` are actually sent through `resolve_pending`.
- Cases are unique: `initial0+select1` and `initial1+select2` are no longer treated as the same scenario.
- Undo is checked by normalized recursive state comparison, not by key existence.
- Optional effect non-regression uses real cards:
  - `PL!S-sd1-004` for `してもよい`.
  - `PL!SP-bp2-013` for `1枚まで`.
- Opponent aggregate count input remains the formal current model; individual opponent card state is not required.
