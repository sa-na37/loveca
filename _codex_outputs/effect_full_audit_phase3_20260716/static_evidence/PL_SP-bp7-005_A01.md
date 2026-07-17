# Static Evidence PL!SP-bp7-005#A01

- audit_id: PL!SP-bp7-005#A01
- cardnumber: PL!SP-bp7-005
- cardname: 葉月恋
- effect_text: <BODY> / このメンバーが登場するか、自分のエネルギーがエネルギー置き場からエネロキーデッキに置かれたとき、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。そのエネルギーカードは、次のターンのアクティブフェイズにアクティブしない。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/effects/registry.py:340:        "gd": {"topk": "5", "filter_group": "Liella!", "optional": "1", "source_name": "葉月恋 bp1-005"},`

## feature_term_search

- `llocg_ui/engine.py:141:    {"id": "energy_put_wait_then_manual_draw_if_no_bladeheart", "pattern": r"^自分のエネルギーデッキから、エネルギーカードを(?P<n>\d+)枚ウェイト状態で置く。これにより控え室に置いたカードがブレードハートを持たない場合、カードを(?P<draw_n>\d+)枚引く。$", "op": "energy_put_wait_then_manual_draw_if_no_bladeheart"},`
- `llocg_ui/engine.py:142:    {"id": "energy_put_active_n", "pattern": r"^自分のエネルギーデッキから、エネルギーカードを(?P<n>\d+)枚アクティブ状態で置く。$", "op": "energy_put_active"},`
- `llocg_ui/engine.py:143:    {"id": "energy_put_wait_n", "pattern": r"^自分のエネルギーデッキから、エネルギーカードを(?P<n>\d+)枚ウェイト状態で置く。$", "op": "energy_put_wait"},`
- `llocg_ui/engine.py:147:    {"id": "energy_put_wait_no_active_next_n", "pattern": r"^自分のエネルギーデッキから、エネルギーカードを(?P<n>\d+)枚ウェイト状態で置く。それらのエネルギーカードは、次のターンのアクティブフェイズにアクティブしない。$", "op": "energy_put_wait_no_active_next"},`

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
      "effect_template": "このメンバーが登場するか、自分のエネルギーがエネルギー置き場からエネロキーデッキに置かれたとき、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。そのエネルギーカードは、次のターンのアクティブフェイズにアクティブしない。",
      "cost_op": null,
      "effect_op": null,
      "raw": "このメンバーが登場するか、自分のエネルギーがエネルギー置き場からエネロキーデッキに置かれたとき、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。そのエネルギーカードは、次のターンのアクティブフェイズにアクティブしない。"
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
