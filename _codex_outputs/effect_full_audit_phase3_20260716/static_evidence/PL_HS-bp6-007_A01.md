# Static Evidence PL!HS-bp6-007#A01

- audit_id: PL!HS-bp6-007#A01
- cardnumber: PL!HS-bp6-007
- cardname: セラス 柳田 リリエンフェルト
- effect_text: <BODY> / 自分のステージに『Edel Note』のメンバーが登場したとき、相手は、自身のステージにいるアクティブ状態のメンバー1人をウェイトにする。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- not found

## feature_term_search

- `llocg_ui/engine.py:539:    {"id": "set_opponent_wait_self_choice", "pattern": r"^相手は、?自身のステージにいるアクティブ状態のメンバー1人をウェイトにする。$", "op": "set_opponent_wait_self_choice"},`

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
      "effect_template": "自分のステージに『Edel Note』のメンバーが登場したとき、相手は、自身のステージにいるアクティブ状態のメンバー1人をウェイトにする。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分のステージに『Edel Note』のメンバーが登場したとき、相手は、自身のステージにいるアクティブ状態のメンバー1人をウェイトにする。"
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
