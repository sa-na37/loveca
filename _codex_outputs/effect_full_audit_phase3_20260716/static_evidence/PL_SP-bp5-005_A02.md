# Static Evidence PL!SP-bp5-005#A02

- audit_id: PL!SP-bp5-005#A02
- cardnumber: PL!SP-bp5-005
- cardname: 葉月恋
- effect_text: <BODY> / 自分のメインフェイズの際、自分のカードが1枚以上いずれかの領域から控え室に置かれるたび、<(E)> / 支払ってもよい。そうした場合、それらのカードの中から1枚手札に加える。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/effects/registry.py:340:        "gd": {"topk": "5", "filter_group": "Liella!", "optional": "1", "source_name": "葉月恋 bp1-005"},`

## feature_term_search

- not found

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
      "effect_template": "自分のメインフェイズの際、自分のカードが1枚以上いずれかの領域から控え室に置かれるたび、<(E)>支払ってもよい。そうした場合、それらのカードの中から1枚手札に加える。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分のメインフェイズの際、自分のカードが1枚以上いずれかの領域から控え室に置かれるたび、<(E)>\n支払ってもよい。そうした場合、それらのカードの中から1枚手札に加える。"
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

- final_classification: NOT_IMPLEMENTED_WITH_EVIDENCE
- confidence: medium
- reason: No card-specific route, no compiled op, and feature-term searches found no matching generic route in inspected runtime files.
