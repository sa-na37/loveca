# Static Evidence PL!SP-pb2-006#A02

- audit_id: PL!SP-pb2-006#A02
- cardnumber: PL!SP-pb2-006
- cardname: 桜小路きな子
- effect_text: <BODY> / 自分のライブが成功するか、このメンバーがエリアを移動したとき、自分の控室にある『Liella!』のメンバーカードを1枚、このメンバーの下に置く。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- not found

## feature_term_search

- `llocg_ui/engine.py:999:    m_main_phase_stage_moved_event = re.match(r'^自分のメインフェイズの間、このメンバーがエリアを移動したとき、(?P<inner>.+)$', s_stage_cond)`
- `llocg_ui/engine.py:13048:                    m = re.match(r'^自分のメインフェイズの間、このメンバーがエリアを移動したとき、(?P<inner>.+)$', eff_norm)`

## compiled_db_entry

```json
{
  "ability_type": "自動",
  "trigger": "BODY",
  "conditions": "ターン1回",
  "clauses": [
    {
      "optional": false,
      "cost_template": "",
      "effect_template": "自分のライブが成功するか、このメンバーがエリアを移動したとき、自分の控室にある『Liella!』のメンバーカードを1枚、このメンバーの下に置く。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分のライブが成功するか、このメンバーがエリアを移動したとき、自分の控室にある『Liella!』のメンバーカードを1枚、このメンバーの下に置く。"
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
