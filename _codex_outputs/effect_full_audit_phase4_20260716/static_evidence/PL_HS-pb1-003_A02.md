# Static Evidence PL!HS-pb1-003#A02

- audit_id: PL!HS-pb1-003#A02
- cardnumber: PL!HS-pb1-003
- cardname: 大沢瑠璃乃
- effect_text: <BODY> / 自分の手札からカードが1枚以上控え室に置かれるたび、ライブ終了時まで、<桃> / <(ブレード)>を得る。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/effects/stage_triggers.py:107:    # PL!HS-bp2-014 大沢瑠璃乃 (登場)`
- `llocg_ui/effects/stage_triggers.py:115:            gs.log.append(f"[AUTO_EXT] 大沢瑠璃乃 bp2-014: draw {drawn}; cannot live until end of live")`
- `llocg_ui/effects/live_start.py:656:    # Prompt 77: PL!HS-bp2-005 大沢瑠璃乃`
- `llocg_ui/effects/live_start.py:668:                gs.log.append("[AUTO_EXT] all stage filled -> +2blade (大沢瑠璃乃)")`
- `llocg_ui/effects/live_start.py:673:                gs.log.append("[AUTO_EXT] stage not full, no blade (大沢瑠璃乃)")`
- `llocg_ui/effects/live_start.py:943:    # Prompt 76: PL!HS-bp2-005 大沢瑠璃乃 (登場)`

## feature_term_search

- `llocg_ui/engine.py:40:    {"id": "favorite_icecream_answer_blade_fragment", "pattern": r"^回答がそれ以外の場合、ライブ終了時まで、自分と相手のステージにいるメンバーは<\(ブレード\)>を得る。$", "op": "answer_fragment_noop"},`
- `llocg_ui/engine.py:42:    {"id": "draw_n_then_gain_icons_until_end_live", "pattern": r"^カードを(?P<n>\d+)枚引き、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "draw_then_gain_icons_until_end_live"},`
- `llocg_ui/engine.py:43:    {"id": "draw_then_stage_group_member_temp_cost", "pattern": r"^カードを(?P<draw_n>\d+)枚引き、ライブ終了時まで、自分のステージにいる『(?P<group>[^』]+)』のメンバー1人のコストを\+(?P<cost_n>\d+)する。$", "op": "draw_then_stage_group_member_temp_cost"},`
- `llocg_ui/engine.py:44:    {"id": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte", "pattern": r"^自分のステージにいる『(?P<group>[^』]+)』のメンバー1人を選ぶ。ライブ終了時まで、このメンバーのコストは、選んだメンバーが元々持つコストより(?P<minus_n>\d+)低い値に等しくなる。これによりこのカードのコストが(?P<threshold>\d+)以上になった場合、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte"},`

## compiled_db_entry

```json
{
  "ability_type": "自動",
  "trigger": "BODY",
  "conditions": "ターン2回",
  "clauses": [
    {
      "optional": false,
      "cost_template": "",
      "effect_template": "自分の手札からカードが1枚以上控え室に置かれるたび、ライブ終了時まで、<桃><(ブレード)>を得る。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分の手札からカードが1枚以上控え室に置かれるたび、ライブ終了時まで、<桃>\n<(ブレード)>を得る。"
    }
  ]
}
```

## generic_matcher_candidate

- not found

## card_specific_route

- not found

## trigger_collection_route

- `llocg_ui/server.py:3424:    if(kind === 'mass_bottom_auto_ack') return '自動効果確認';`
- `llocg_ui/server.py:3469:    if(kind === 'mass_bottom_auto_ack') return '自動効果を確認してから、後続処理へ進みます。';`
- `llocg_ui/engine.py:2176:        timing = '自動効果'`
- `llocg_ui/engine.py:2188:def _auto_effect_detail_for_condition(ctx: Optional[Dict[str, Any]], effect_text: str, condition_text: str, timing: str = '自動効果') -> str:`
- `llocg_ui/engine.py:2191:    head = f'【{src}】{timing}' if src else str(timing or '自動効果')`
- `llocg_ui/engine.py:2277:        timing0 = str((ctx or {}).get('effect_timing', '') or (ctx or {}).get('timing', '') or '自動効果').strip()`

## pending_creation_route

- not found

## resolver_route

- not found

## ui_route

- not found

## reachable_from_runtime

No previous static matcher/resolve route; no pending/dispatch evidence in mapping

## conflicting_routes

none found in this static pass

- final_classification: STATIC_ANALYSIS_INCONCLUSIVE
- confidence: low
- reason: Search evidence is insufficient to confirm either implementation or absence.
