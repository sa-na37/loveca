# Loveca handoff 20260622g

## Status
- 20260622f is treated as the current passing base.
- User confirmed the duplicate pending effect text fix is OK.
- Debug commands should be provided in chat only, not embedded in this handoff.

## Change
- Added a generic conditional wrapper for live-start effects that grant a temporary bonus to one stage member.
- Changed files:
  - `llocg_ui/effects/registry.py`
  - `llocg_ui/effects/live_start.py`
  - `llocg_ui/effects/helpers.py`

## BUILD_TAG
- `registry.py`: `effect_registry_conditional_stage_bonus_20260622g`
- `live_start.py`: `live_start_conditional_stage_bonus_20260622g`
- `helpers.py`: `helpers_live_in_progress_set_zone_20260622g`

## Implemented generic shape

```text
<condition>場合、ライブ終了時まで、自分のステージにいる<target>メンバー1人は、<icons>を得る。
```

Supported condition fragments:
- `自分の成功ライブカード置き場にカードがN枚以上ある`
- `自分の控え室に『X』のメンバーカードがN枚以上ある`
- `自分のライブ中のライブカードに、<ライブ開始時>能力も<ライブ成功時>能力も持たないカードがある`

Supported target/icon fragments reuse the existing `live_start_pick_stage_member_temp_bonus` route:
- no target restriction
- `このメンバー以外`
- `『X』` group/unit target
- repeated heart/blade icon runs

## Representative newly covered cards
- `PL!S-bp2-025` 青空Jumping Heart
- `PL!HS-pb1-025` 抱きしめる花びら
- `PL!-bp4-014` 星空凛

## Notes
- Complex target predicates such as `ハートを持つメンバー` remain intentionally unsupported in this simple wrapper.
- `set_zone` is now included in `_live_in_progress_cards()` so "ライブ中のカード" conditions can see the currently set live cards.
