# Static Evidence PL!SP-bp5-005#A01

- audit_id: PL!SP-bp5-005#A01
- cardnumber: PL!SP-bp5-005
- cardname: 葉月恋
- effect_text: <BODY> / デッキの上からカードを3枚控え室に置く：ライブ終了時まで、これにより控え室に置いた『Liella!』のメンバーカード1枚につき、<(ブレード)> / を得る。
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
  "ability_type": "起動",
  "trigger": "BODY",
  "conditions": "ターン1回",
  "clauses": [
    {
      "optional": false,
      "cost_template": "デッキの上からカードを3枚控え室に置く",
      "effect_template": "ライブ終了時まで、これにより控え室に置いた『Liella!』のメンバーカード1枚につき、<(ブレード)>を得る。",
      "cost_op": null,
      "effect_op": null,
      "raw": "デッキの上からカードを3枚控え室に置く：ライブ終了時まで、これにより控え室に置いた『Liella!』のメンバーカード1枚につき、<(ブレード)>\nを得る。"
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

- final_classification: NOT_IMPLEMENTED_WITH_EVIDENCE
- confidence: medium
- reason: No card-specific route, no compiled op, and feature-term searches found no matching generic route in inspected runtime files.
