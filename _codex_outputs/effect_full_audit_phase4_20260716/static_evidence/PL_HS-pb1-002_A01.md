# Static Evidence PL!HS-pb1-002#A01

- audit_id: PL!HS-pb1-002#A01
- cardnumber: PL!HS-pb1-002
- cardname: 村野さやか
- effect_text: <BODY> / 手札の「村野さやか」のメンバーカードを1枚公開する：これにより公開したカードをこのメンバーの下に置く。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/effects/stage_triggers.py:31:    # PL!HS-bp2-002 村野さやか (登場)`
- `llocg_ui/effects/stage_triggers.py:32:    # PL!HS-bp2-002 村野さやか (BODY)`
- `llocg_ui/effects/stage_triggers.py:56:            gs.log.append(f"[AUTO_EXT] 村野さやか BODY: my_cost={my_cost} found_higher={found_higher} ({src})")`
- `llocg_ui/effects/stage_triggers.py:217:    # bp2_batch3_local_20260413f: PL!HS-bp2-011 村野さやか (登場)`
- `llocg_ui/effects/registry.py:434:        "gd": {"topk": "5", "source_name": "村野さやか bp2-011"},`

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
      "cost_template": "手札の「村野さやか」のメンバーカードを1枚公開する",
      "effect_template": "これにより公開したカードをこのメンバーの下に置く。",
      "cost_op": null,
      "effect_op": null,
      "raw": "手札の「村野さやか」のメンバーカードを1枚公開する：これにより公開したカードをこのメンバーの下に置く。"
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
