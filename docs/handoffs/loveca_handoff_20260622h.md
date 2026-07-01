# Loveca handoff 20260622h

## Status
- 20260622g is treated as the current passing base.
- Debug commands should be provided in chat only, not embedded in this handoff.

## Change
- Generalized the live-start yell heart color conversion route.
- Changed file:
  - `llocg_ui/engine.py`

## BUILD_TAG
- `engine.py`: `live_start_yell_color_convert_generic_20260622h`

## Implemented generic shape

```text
ライブ終了時まで、エールによって公開される自分のカードが持つ<source icons...><ALL>は、すべて<target>になる。
```

## Covered examples
- `PL!N-bp4-025` VIVID WORLD
  - converts non-blue / ALL yell hearts to blue.
- `PL!SP-bp4-023` Dazzling Game
  - converts non-purple / ALL yell hearts to purple.

## Notes
- Kept the old `vivid_world_blue_mode_this_live` flag for compatibility.
- Added `yell_heart_convert_target_color_this_live` as the generic target-color state.
- No cardnumber-specific branch was added.

## Confirmed
- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Internal matcher check:
  - `PL!N-bp4-025` maps to target `青`.
  - `PL!SP-bp4-023` maps to target `紫`.
