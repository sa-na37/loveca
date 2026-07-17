# Static Evidence PL!N-PR-025#A01

- audit_id: PL!N-PR-025#A01
- cardnumber: PL!N-PR-025
- cardname: 優木せつ菜
- effect_text: <BODY> / 自分のステージに、このメンバーか、ほかのメンバーがバトンタッチして登場したとき、カードを1枚引く。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- not found

## feature_term_search

- `llocg_ui/effects/success_zone.py:259:            "after_effect_template": "ライブの合計スコアが相手より高く、かつ自分のステージに『蓮ノ空』のメンバーがいる場合、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。",`
- `llocg_ui/effects/position.py:158:            "text": f"{src}: 自分のステージにブレード5以上の『μ's』メンバーがいないため、センターエリア以外にポジションチェンジする",`
- `llocg_ui/engine.py:43:    {"id": "draw_then_stage_group_member_temp_cost", "pattern": r"^カードを(?P<draw_n>\d+)枚引き、ライブ終了時まで、自分のステージにいる『(?P<group>[^』]+)』のメンバー1人のコストを\+(?P<cost_n>\d+)する。$", "op": "draw_then_stage_group_member_temp_cost"},`
- `llocg_ui/engine.py:44:    {"id": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte", "pattern": r"^自分のステージにいる『(?P<group>[^』]+)』のメンバー1人を選ぶ。ライブ終了時まで、このメンバーのコストは、選んだメンバーが元々持つコストより(?P<minus_n>\d+)低い値に等しくなる。これによりこのカードのコストが(?P<threshold>\d+)以上になった場合、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte"},`
- `llocg_ui/engine.py:16177:                m_baton_enter = re.match(r'^自分のステージに、このメンバーか、ほかのメンバーがバトンタッチして登場したとき、(?P<inner>.+)$', eff_norm)`
- `llocg_ui/server.py:3439:    if(s.includes('カードを1枚引く')) return 'カードを1枚引きます。';`
- `llocg_ui/engine.py:39:    {"id": "favorite_icecream_answer_draw_fragment", "pattern": r"^回答があなたの場合、自分と相手はカードを1枚引く。$", "op": "answer_fragment_noop"},`
- `llocg_ui/engine.py:48:    {"id": "draw_stage_member_count_then_discard_1", "pattern": r"^自分のステージにいるメンバー1人につき、カードを1枚引く。その後、手札を1枚控え室に置く。$", "op": "draw_stage_member_count_then_discard", "discard_n": 1},`
- `llocg_ui/engine.py:121:    {"id": "topdeck_green_live_group_upto1_then_draw_if_opponent_wait_exists", "pattern": r"^自分の控え室から『(?P<group>[^』]+)』のライブカードを1枚までデッキの一番上に置く。その後、相手のステージにウェイト状態のメンバーがいる場合、カードを1枚引く。$", "op": "topdeck_green_live_group_upto1_then_draw_if_opponent_wait_exists"},`

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
      "effect_template": "自分のステージに、このメンバーか、ほかのメンバーがバトンタッチして登場したとき、カードを1枚引く。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分のステージに、このメンバーか、ほかのメンバーがバトンタッチして登場したとき、カードを1枚引く。"
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
