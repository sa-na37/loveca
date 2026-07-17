# Static Evidence PL!HS-bp6-014#A01

- audit_id: PL!HS-bp6-014#A01
- cardnumber: PL!HS-bp6-014
- cardname: 安養寺姫芽
- effect_text: <BODY> / このカードを手札から控え室に置く：カードを1枚引き、ライブ終了時まで、自分のステージにいる「藤島慈」か「大沢瑠璃乃」のうち1人は<(ブレード)> / を得る。この能力は、このカードが手札にある場合のみ起動できる。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/engine.py:10983:    # hand->set during the current LIVE_SET phase; default 3, may be reduced by effects like 安養寺姫芽`
- `llocg_ui/engine.py:10985:    # one-shot delta reserved for the next LIVE_SET phase (e.g. -1 by 安養寺姫芽)`
- `llocg_ui/effects/special.py:28:        src = str((ctx or {}).get("source_cn") or "安養寺姫芽")`
- `llocg_ui/effects/live_start.py:950:    # Prompt 80: PL!HS-bp2-018 安養寺姫芽 (登場)`

## feature_term_search

- `llocg_ui/effects/stage_triggers.py:125:    # ライブ終了時まで、ステージのメンバー1人（選択）に +3ブレード`
- `llocg_ui/effects/live_start.py:128:        text=f"{source_cn}: {pretty}から1つ選ぶ → ライブ終了時まで+1",`
- `llocg_ui/effects/live_start.py:651:    # ライブ終了時まで、ライブ中のカード 1 枚につき +1ブレード`
- `llocg_ui/effects/live_start.py:657:    # ステージ全 3 エリアにメンバーがいる → ライブ終了時まで +2ブレード`

## compiled_db_entry

```json
{
  "ability_type": "起動",
  "trigger": "BODY",
  "conditions": "",
  "clauses": [
    {
      "optional": false,
      "cost_template": "このカードを手札から控え室に置く",
      "effect_template": "カードを1枚引き、ライブ終了時まで、自分のステージにいる「藤島慈」か「大沢瑠璃乃」のうち1人は<(ブレード)>を得る。この能力は、このカードが手札にある場合のみ起動できる。",
      "cost_op": {
        "id": "C038",
        "template": "このカードを手札から控え室に置く",
        "op": "TODO",
        "params": {},
        "note": "",
        "confidence": 0.0
      },
      "effect_op": null,
      "raw": "このカードを手札から控え室に置く：カードを1枚引き、ライブ終了時まで、自分のステージにいる「藤島慈」か「大沢瑠璃乃」のうち1人は<(ブレード)>\nを得る。この能力は、このカードが手札にある場合のみ起動できる。"
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

- final_classification: IMPLEMENTED_ROUTE_UNVERIFIED
- confidence: low
- reason: Some route/op evidence exists, but this static pass does not prove end-to-end reachability.
