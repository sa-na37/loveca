# Static Evidence PL!SP-bp5-011#A03

- audit_id: PL!SP-bp5-011#A03
- cardnumber: PL!SP-bp5-011
- cardname: 鬼塚冬毬
- effect_text: <BODY> / を得る。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- not found

## feature_term_search

- not found

## compiled_db_entry

```json
{
  "ability_type": "常時",
  "trigger": "BODY",
  "conditions": "右サイド;青;青;青",
  "clauses": [
    {
      "optional": false,
      "cost_template": "",
      "effect_template": "を得る。",
      "cost_op": null,
      "effect_op": {
        "id": "E145",
        "template": "を得る。",
        "op": "TODO",
        "params": {},
        "note": "",
        "confidence": 0.0
      },
      "raw": "を得る。"
    }
  ]
}
```

## generic_matcher_candidate

- `llocg_ui/engine.py:40:    {"id": "favorite_icecream_answer_blade_fragment", "pattern": r"^回答がそれ以外の場合、ライブ終了時まで、自分と相手のステージにいるメンバーは<\(ブレード\)>を得る。$", "op": "answer_fragment_noop"},`
- `llocg_ui/engine.py:42:    {"id": "draw_n_then_gain_icons_until_end_live", "pattern": r"^カードを(?P<n>\d+)枚引き、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "draw_then_gain_icons_until_end_live"},`
- `llocg_ui/engine.py:44:    {"id": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte", "pattern": r"^自分のステージにいる『(?P<group>[^』]+)』のメンバー1人を選ぶ。ライブ終了時まで、このメンバーのコストは、選んだメンバーが元々持つコストより(?P<minus_n>\d+)低い値に等しくなる。これによりこのカードのコストが(?P<threshold>\d+)以上になった場合、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte"},`
- `llocg_ui/engine.py:45:    {"id": "self_temp_cost_then_stage_group_cost_sum_gt_opponent_gain_icons", "pattern": r"^ライブ終了時まで、このメンバーのコストを\+(?P<cost_n>\d+)する。その後、自分のステージにいる『(?P<group>[^』]+)』のメンバーのコストの合計が、相手のステージにいるメンバーのコストの合計より高い場合、さらにライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "self_temp_cost_then_stage_group_cost_sum_gt_opponent_gain_icons"},`

## card_specific_route

- not found

## trigger_collection_route

- `llocg_ui/server.py:418:            #   text="デッキ上2枚から『μ's』・能力なし/常時能力ありを1枚手札へ..."`
- `llocg_ui/server.py:1819:                        # 常時BODYブレード加算（コスト13以上条件）`
- `llocg_ui/server.py:1883:        """常時ブレードボーナスを返す（UI表示専用）。"""`
- `llocg_ui/server.py:1892:        """常時のハート加算を返す（UI表示専用）。"""`
- `llocg_ui/server.py:1912:        """常時のライブ合計スコア加算を返す（UI表示専用）。"""`
- `llocg_ui/server.py:2322:                # BODY trigger with clauses: ability_typeをヘッダに使う（例：常時）`

## pending_creation_route

- not found

## resolver_route

- `llocg_ui/engine.py:40:    {"id": "favorite_icecream_answer_blade_fragment", "pattern": r"^回答がそれ以外の場合、ライブ終了時まで、自分と相手のステージにいるメンバーは<\(ブレード\)>を得る。$", "op": "answer_fragment_noop"},`
- `llocg_ui/engine.py:42:    {"id": "draw_n_then_gain_icons_until_end_live", "pattern": r"^カードを(?P<n>\d+)枚引き、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "draw_then_gain_icons_until_end_live"},`
- `llocg_ui/engine.py:44:    {"id": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte", "pattern": r"^自分のステージにいる『(?P<group>[^』]+)』のメンバー1人を選ぶ。ライブ終了時まで、このメンバーのコストは、選んだメンバーが元々持つコストより(?P<minus_n>\d+)低い値に等しくなる。これによりこのカードのコストが(?P<threshold>\d+)以上になった場合、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte"},`
- `llocg_ui/engine.py:45:    {"id": "self_temp_cost_then_stage_group_cost_sum_gt_opponent_gain_icons", "pattern": r"^ライブ終了時まで、このメンバーのコストを\+(?P<cost_n>\d+)する。その後、自分のステージにいる『(?P<group>[^』]+)』のメンバーのコストの合計が、相手のステージにいるメンバーのコストの合計より高い場合、さらにライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "self_temp_cost_then_stage_group_cost_sum_gt_opponent_gain_icons"},`

## ui_route

- not found

## reachable_from_runtime

No previous static matcher/resolve route; no pending/dispatch evidence in mapping

## conflicting_routes

none found in this static pass

- final_classification: IMPLEMENTED_ROUTE_UNVERIFIED
- confidence: low
- reason: Some route/op evidence exists, but this static pass does not prove end-to-end reachability.
