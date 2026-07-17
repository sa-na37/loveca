# Static Evidence PL!SP-bp7-025#A01

- audit_id: PL!SP-bp7-025#A01
- cardnumber: PL!SP-bp7-025
- cardname: Memories
- effect_text: <ライブ開始時> / ライブ終了時まで、自分のステージにいる「嵐千砂都」1人は<(ブレード)>を得る。
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
  "ability_type": "自動",
  "trigger": "ライブ開始時",
  "conditions": "",
  "clauses": [
    {
      "optional": false,
      "cost_template": "",
      "effect_template": "ライブ終了時まで、自分のステージにいる「嵐千砂都」1人は<(ブレード)>を得る。",
      "cost_op": null,
      "effect_op": null,
      "raw": "ライブ終了時まで、自分のステージにいる「嵐千砂都」1人は<(ブレード)>を得る。"
    }
  ]
}
```

## generic_matcher_candidate

- not found

## card_specific_route

- not found

## trigger_collection_route

- `llocg_ui/server.py:3697:    if(kind.startsWith('live_start') || kind === 'enqueue_pending_prompt') return 'ライブ開始時';`
- `llocg_ui/server.py:6075:    // Exact cardnumber only. Labels like "C: PL!N-bp1-003 ライブ開始時" must NOT match.`
- `llocg_ui/effects/stage_triggers.py:124:    # Prompt 22: PL!-bp3-026 Oh,Love&Peace! (ライブ開始時)`
- `llocg_ui/effects/stage_triggers.py:205:    # Prompt 80: PL!HS-bp2-007 百生吟子 (ライブ開始時)`
- `llocg_ui/effects/live_start.py:7:ライブ開始時に解決する ext apply の正本。`
- `llocg_ui/effects/live_start.py:356:            if str(trig or "").strip() in ("ライブ開始時", "ライブ成功時"):`

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
