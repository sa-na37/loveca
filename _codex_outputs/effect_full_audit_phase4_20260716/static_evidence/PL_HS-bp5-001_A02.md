# Static Evidence PL!HS-bp5-001#A02

- audit_id: PL!HS-bp5-001#A02
- cardnumber: PL!HS-bp5-001
- cardname: 日野下花帆
- effect_text: <BODY> / <(E)><(E)>手札のライブカードを1枚公開する：自分の控え室から、これにより公開したカードのカード名がすべて含まれるライブカードを1枚手札に加える。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/effects/topdeck.py:336:            '日野下花帆 bp2-010' if ext_key == 'enter_top5_member_optional_pick' else`
- `llocg_ui/effects/registry.py:226:    # Prompt 73: PL!HS-bp2-001 日野下花帆 (起動)`
- `llocg_ui/effects/registry.py:234:            "source_name": "日野下花帆",`
- `llocg_ui/effects/registry.py:238:            "pending_label": "【日野下花帆】控え室からスコア3以下の蓮ノ空ライブカードを1枚選んでください",`
- `llocg_ui/effects/registry.py:239:            "no_candidates_log": "[AUTO_EXT] no 蓮ノ空 LIVE score<=3 in green_room (日野下花帆)"`
- `llocg_ui/effects/registry.py:316:        "gd": {"topk": "5", "filter_kind": "MEMBER", "optional": "1", "source_name": "日野下花帆 bp2-010"},`

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
      "cost_template": "<(E)><(E)>手札のライブカードを1枚公開する",
      "effect_template": "自分の控え室から、これにより公開したカードのカード名がすべて含まれるライブカードを1枚手札に加える。",
      "cost_op": null,
      "effect_op": null,
      "raw": "<(E)><(E)>手札のライブカードを1枚公開する：自分の控え室から、これにより公開したカードのカード名がすべて含まれるライブカードを1枚手札に加える。"
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
