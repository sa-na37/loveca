# Static Evidence PL!N-PR-026#A03

- audit_id: PL!N-PR-026#A03
- cardnumber: PL!N-PR-026
- cardname: 天王寺璃奈
- effect_text: 
- previous_classification: UNREACHABLE_TRIGGER_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/effects/live_start.py:626:            "text": "【天王寺璃奈】ライブ開始時：自分ステージのコスト合計が相手より低いなら、カードを2枚引き、手札1枚をデッキの一番上に置く",`
- `llocg_ui/effects/live_start.py:634:            gs.log.append(f"[PENDING] 天王寺璃奈: confirm draw2/hand top1 (my_cost={my_cost}, opp unavailable)")`

## feature_term_search

- not found

## compiled_db_entry

```json
{}
```

## generic_matcher_candidate

- not found

## card_specific_route

- not found

## trigger_collection_route

- `llocg_ui/server.py:3462:    if(kind === 'set_opponent_excess_for_live_success') return 'このライブ成功時効果の処理で参照する相手余剰ハート数を選んでください。';`
- `llocg_ui/server.py:3698:    if(kind.includes('success')) return 'ライブ成功時';`
- `llocg_ui/server.py:5556:    note.textContent = 'ライブ成功時効果解決前の判定結果です。';`
- `llocg_ui/server.py:6970:      setRichText(elModalText, pendText || 'このライブ成功時効果の処理で参照する相手余剰ハート数を選んでください。');`
- `manual_overrides/loveca_card_text_overrides.json:9:      "effect_text_raw": "<ライブ成功時>\n自分が余剰ハートを3つ以上持っている場合、それらをすべて失い、このカードのスコアを+1する。",`
- `manual_overrides/loveca_card_text_overrides.json:10:      "effect_text_norm": "<ライブ成功時>\n自分が余剰ハートを3つ以上持っている場合、それらをすべて失い、このカードのスコアを+1する。"`

## pending_creation_route

- not found

## resolver_route

- not found

## ui_route

- not found

## reachable_from_runtime

Route candidate exists or text matched, but previous reachable flag is not YES; trigger collection path is not proven

## conflicting_routes

none found in this static pass

- final_classification: NOT_IMPLEMENTED_WITH_EVIDENCE
- confidence: medium
- reason: No card-specific route, no compiled op, and feature-term searches found no matching generic route in inspected runtime files.
