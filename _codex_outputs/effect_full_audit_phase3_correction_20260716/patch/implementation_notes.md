# Implementation notes

- `choose_enter_effect_mode` pending generated from generic `[登場] 以下から1つを選ぶ` route is now marked `mandatory=True` and `allow_skip=False`.
- `next` now blocks mandatory `choose_enter_effect_mode`, keeps the pending active, and appends a clear required-selection message.
- Invalid/empty `resolve_pending` for mandatory `choose_enter_effect_mode` re-inserts the pending instead of dropping it.
- Optional skip paths remain gated by `optional`, `allow_skip`, or existing optional pending kinds and were regression tested.
- Opponent wait aggregate count input remains the current formal model; no individual opponent card state was introduced or required.
