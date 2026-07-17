# Static Evidence PL!N-PR-010#A01

- audit_id: PL!N-PR-010#A01
- cardnumber: PL!N-PR-010
- cardname: エマ・ヴェルデ
- effect_text: <BODY> / 手札をすべて公開する：自分のステージにほかのメンバーがおり、かつこれにより公開した手札の中にライブカードがない場合、自分のデッキの上からカードを5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- `llocg_ui/engine.py:15918:      PL!N-PR-003 上原歩夢 / PL!N-PR-008 近江彼方 / PL!N-PR-010 エマ・ヴェルデ`

## cardname_search

- `llocg_ui/engine.py:15918:      PL!N-PR-003 上原歩夢 / PL!N-PR-008 近江彼方 / PL!N-PR-010 エマ・ヴェルデ`
- `llocg_ui/effects/registry.py:201:    # Prompt: PL!N-bp3-008 エマ・ヴェルデ (ライブ開始時)`
- `llocg_ui/effects/registry.py:210:            "source_name": "エマ・ヴェルデ",`
- `llocg_ui/effects/registry.py:213:            "no_target_log": "no other wait member on stage (エマ・ヴェルデ)"`

## feature_term_search

- `llocg_ui/engine.py:15920:      自分のステージにほかのメンバーがおり、かつこれにより公開した手札の中にライブカードがない場合、`
- `llocg_ui/engine.py:15921:      自分のデッキの上からカードを5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。`
- `llocg_ui/effects/registry.py:314:        "effect_template": "自分のデッキの上からカードを5枚見る。その中からメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",`
- `llocg_ui/effects/registry.py:320:        "effect_template": "このメンバーがステージから控え室に置かれたとき、自分のデッキの上からカードを5枚見る。その中からメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",`
- `llocg_ui/effects/registry.py:326:        "effect_template": "このメンバーがステージから控え室に置かれたとき、自分のデッキの上からカードを5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",`

## compiled_db_entry

```json
{
  "ability_type": "起動",
  "trigger": "BODY",
  "conditions": "ターン1回",
  "clauses": [
    {
      "optional": false,
      "cost_template": "手札をすべて公開する",
      "effect_template": "自分のステージにほかのメンバーがおり、かつこれにより公開した手札の中にライブカードがない場合、自分のデッキの上からカードを5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",
      "cost_op": {
        "id": "C023",
        "template": "手札をすべて公開する",
        "op": "TODO",
        "params": {},
        "note": "",
        "confidence": 0.0
      },
      "effect_op": null,
      "raw": "手札をすべて公開する：自分のステージにほかのメンバーがおり、かつこれにより公開した手札の中にライブカードがない場合、自分のデッキの上からカードを5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。"
    }
  ]
}
```

## generic_matcher_candidate

- `llocg_ui/engine.py:1916:            # BODY起動効果（手札をすべて公開する）はeffect_templateが_EFFECT_RULESにないためスキップ`
- `llocg_ui/engine.py:1917:            is_body_cost = '手札をすべて公開する' in cost and str(ab.get('trigger', '') or '') == 'BODY'`
- `llocg_ui/engine.py:15907:    # BODY効果（手札をすべて公開する）は起動効果のため cmd_activate_member で処理`
- `llocg_ui/engine.py:22406:            # Cost: 手札をすべて公開する（BODY起動効果）`

## card_specific_route

- `llocg_ui/engine.py:15918:      PL!N-PR-003 上原歩夢 / PL!N-PR-008 近江彼方 / PL!N-PR-010 エマ・ヴェルデ`

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

- `llocg_ui/engine.py:1916:            # BODY起動効果（手札をすべて公開する）はeffect_templateが_EFFECT_RULESにないためスキップ`
- `llocg_ui/engine.py:1917:            is_body_cost = '手札をすべて公開する' in cost and str(ab.get('trigger', '') or '') == 'BODY'`
- `llocg_ui/engine.py:15907:    # BODY効果（手札をすべて公開する）は起動効果のため cmd_activate_member で処理`
- `llocg_ui/engine.py:22406:            # Cost: 手札をすべて公開する（BODY起動効果）`

## ui_route

- not found

## reachable_from_runtime

No previous static matcher/resolve route; no pending/dispatch evidence in mapping

## conflicting_routes

none found in this static pass

- final_classification: IMPLEMENTED_ROUTE_UNVERIFIED
- confidence: low
- reason: Some route/op evidence exists, but this static pass does not prove end-to-end reachability.
