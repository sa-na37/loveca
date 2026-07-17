# Static Evidence PL!SP-bp1-003#A01

- audit_id: PL!SP-bp1-003#A01
- cardnumber: PL!SP-bp1-003
- cardname: 嵐千砂都
- effect_text: <BODY> / 手札にあるメンバーカードを好きな枚数公開する：公開したカードのコストの合計が、10、20、30、40、50のいずれかの場合、ライブ終了時まで、「<常時>ライブの合計スコアを+1する。」を得る。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- not found

## feature_term_search

- `llocg_ui/engine.py:40:    {"id": "favorite_icecream_answer_blade_fragment", "pattern": r"^回答がそれ以外の場合、ライブ終了時まで、自分と相手のステージにいるメンバーは<\(ブレード\)>を得る。$", "op": "answer_fragment_noop"},`
- `llocg_ui/engine.py:42:    {"id": "draw_n_then_gain_icons_until_end_live", "pattern": r"^カードを(?P<n>\d+)枚引き、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "draw_then_gain_icons_until_end_live"},`
- `llocg_ui/engine.py:43:    {"id": "draw_then_stage_group_member_temp_cost", "pattern": r"^カードを(?P<draw_n>\d+)枚引き、ライブ終了時まで、自分のステージにいる『(?P<group>[^』]+)』のメンバー1人のコストを\+(?P<cost_n>\d+)する。$", "op": "draw_then_stage_group_member_temp_cost"},`
- `llocg_ui/engine.py:44:    {"id": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte", "pattern": r"^自分のステージにいる『(?P<group>[^』]+)』のメンバー1人を選ぶ。ライブ終了時まで、このメンバーのコストは、選んだメンバーが元々持つコストより(?P<minus_n>\d+)低い値に等しくなる。これによりこのカードのコストが(?P<threshold>\d+)以上になった場合、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte"},`

## compiled_db_entry

```json
{
  "ability_type": "起動",
  "trigger": "BODY",
  "conditions": "ターン1回",
  "clauses": [
    {
      "optional": false,
      "cost_template": "手札にあるメンバーカードを好きな枚数公開する",
      "effect_template": "公開したカードのコストの合計が、10、20、30、40、50のいずれかの場合、ライブ終了時まで、「<常時>ライブの合計スコアを+1する。」を得る。",
      "cost_op": {
        "id": "C058",
        "template": "手札にあるメンバーカードを好きな枚数公開する",
        "op": "TODO",
        "params": {},
        "note": "",
        "confidence": 0.0
      },
      "effect_op": null,
      "raw": "手札にあるメンバーカードを好きな枚数公開する：公開したカードのコストの合計が、10、20、30、40、50のいずれかの場合、ライブ終了時まで、「<常時>ライブの合計スコアを+1する。」を得る。"
    }
  ]
}
```

## generic_matcher_candidate

- not found

## card_specific_route

- not found

## trigger_collection_route

- `llocg_ui/server.py:3700:    if(kind.includes('activate') || kind.includes('body')) return '起動/能力';`
- `llocg_ui/server.py:5151:        b.textContent = '起動';`
- `llocg_ui/server.py:6411:    // BODY起動: デッキ上5枚からライブカードを1枚選択（choose_from_topkと同じ左右分割UI）`
- `llocg_ui/engine.py:957:    if 'この能力を起動するためのコストは' in s:`
- `llocg_ui/engine.py:1916:            # BODY起動効果（手札をすべて公開する）はeffect_templateが_EFFECT_RULESにないためスキップ`
- `llocg_ui/engine.py:6280:        if str((ctx or {}).get('effect_timing', '') or '') != '起動効果':`

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

- final_classification: IMPLEMENTED_ROUTE_UNVERIFIED
- confidence: low
- reason: Some route/op evidence exists, but this static pass does not prove end-to-end reachability.
