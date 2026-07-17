# Static Evidence PL!SP-bp2-008#A01

- audit_id: PL!SP-bp2-008#A01
- cardnumber: PL!SP-bp2-008
- cardname: 若菜四季
- effect_text: <BODY> / <(E)>：このメンバーがいるエリアとは別の自分のエリア1つを選ぶ。このメンバーをそのエリアに移動する。選んだエリアにメンバーがいる場合、そのメンバーは、このメンバーがいたエリアに移動させる。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/engine.py:21214:                # Example: PL!SP-pb2-008 若菜四季.`
- `llocg_ui/effects/registry.py:129:    # Prompt 6: PL!SP-bp4-008 若菜四季 (ライブ開始時, no-cost)`

## feature_term_search

- `llocg_ui/engine.py:345:    {"id": "draw_then_move_self_to_other_area_swap", "pattern": r"^カードを(?P<n>\d+)枚引く。その後、登場したエリアとは別の自分のエリア1つを選ぶ。このメンバーをそのエリアに移動する。選んだエリアにメンバーがいる場合、そのメンバーは、このメンバーがいたエリアに移動させる。$", "op": "draw_then_position_change_self"},`
- `llocg_ui/engine.py:345:    {"id": "draw_then_move_self_to_other_area_swap", "pattern": r"^カードを(?P<n>\d+)枚引く。その後、登場したエリアとは別の自分のエリア1つを選ぶ。このメンバーをそのエリアに移動する。選んだエリアにメンバーがいる場合、そのメンバーは、このメンバーがいたエリアに移動させる。$", "op": "draw_then_position_change_self"},`

## compiled_db_entry

```json
{
  "ability_type": "起動",
  "trigger": "BODY",
  "conditions": "ターン1回",
  "clauses": [
    {
      "optional": false,
      "cost_template": "<(E)>",
      "effect_template": "このメンバーがいるエリアとは別の自分のエリア1つを選ぶ。このメンバーをそのエリアに移動する。選んだエリアにメンバーがいる場合、そのメンバーは、このメンバーがいたエリアに移動させる。",
      "cost_op": null,
      "effect_op": null,
      "raw": "<(E)>：このメンバーがいるエリアとは別の自分のエリア1つを選ぶ。このメンバーをそのエリアに移動する。選んだエリアにメンバーがいる場合、そのメンバーは、このメンバーがいたエリアに移動させる。"
    }
  ]
}
```

## generic_matcher_candidate

- `llocg_ui/engine.py:1241:      - Explicit counts like "<(E)> 3" or "[E]3"`
- `llocg_ui/engine.py:1242:      - Repeated icons like "<(E)><(E)><(E)>" (counts as 3)`
- `llocg_ui/engine.py:1255:            total += t.count("<(E)>")`
- `llocg_ui/engine.py:6150:        need_e = int(energy_icons.count('<(E)>') or 0)`

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

- `llocg_ui/engine.py:1241:      - Explicit counts like "<(E)> 3" or "[E]3"`
- `llocg_ui/engine.py:1242:      - Repeated icons like "<(E)><(E)><(E)>" (counts as 3)`
- `llocg_ui/engine.py:1255:            total += t.count("<(E)>")`
- `llocg_ui/engine.py:6150:        need_e = int(energy_icons.count('<(E)>') or 0)`

## ui_route

- not found

## reachable_from_runtime

No previous static matcher/resolve route; no pending/dispatch evidence in mapping

## conflicting_routes

none found in this static pass

- final_classification: STATIC_ANALYSIS_INCONCLUSIVE
- confidence: low
- reason: Search evidence is insufficient to confirm either implementation or absence.
