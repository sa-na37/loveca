# Static Evidence PL!HS-bp5-016#A02

- audit_id: PL!HS-bp5-016#A02
- cardnumber: PL!HS-bp5-016
- cardname: 桂城泉
- effect_text: <BODY> / 相手のステージにウェイト状態のメンバーが2人以上いるかぎり、 / <紫> / を得る。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- not found

## feature_term_search

- `llocg_ui/engine.py:121:    {"id": "topdeck_green_live_group_upto1_then_draw_if_opponent_wait_exists", "pattern": r"^自分の控え室から『(?P<group>[^』]+)』のライブカードを1枚までデッキの一番上に置く。その後、相手のステージにウェイト状態のメンバーがいる場合、カードを1枚引く。$", "op": "topdeck_green_live_group_upto1_then_draw_if_opponent_wait_exists"},`
- `llocg_ui/engine.py:415:    {"id": "opponent_wait_exists_reduce_required_any", "pattern": r"^相手のステージにウェイト状態のメンバーがいる場合、このカードを成功させるための必要ハートを(?P<anys>(?:<任意>|<\(任意\)>)+)減らす。$", "op": "opponent_wait_exists_reduce_required_any"},`
- `llocg_ui/engine.py:4536:            'text': f'【{src or "この能力"}】相手のステージにウェイト状態のメンバーがいる場合、カードを1枚引きます。条件を満たすなら Apply、満たさないなら Skip。',`
- `llocg_ui/engine.py:19375:    m = re.match(r'^相手のステージにウェイト状態のメンバーがいる場合、このカードを成功させるための必要ハートを(?P<anys>(?:<\(任意\)>)+)減らす。$', eff_norm)`

## compiled_db_entry

```json
{
  "ability_type": "常時",
  "trigger": "BODY",
  "conditions": "",
  "clauses": [
    {
      "optional": false,
      "cost_template": "",
      "effect_template": "相手のステージにウェイト状態のメンバーが2人以上いるかぎり、<紫>を得る。",
      "cost_op": null,
      "effect_op": null,
      "raw": "相手のステージにウェイト状態のメンバーが2人以上いるかぎり、\n<紫>\nを得る。"
    }
  ]
}
```

## generic_matcher_candidate

- not found

## card_specific_route

- not found

## trigger_collection_route

- `llocg_ui/server.py:418:            #   text="デッキ上2枚から『μ's』・能力なし/常時能力ありを1枚手札へ..."`
- `llocg_ui/server.py:1819:                        # 常時BODYブレード加算（コスト13以上条件）`
- `llocg_ui/server.py:1883:        """常時ブレードボーナスを返す（UI表示専用）。"""`
- `llocg_ui/server.py:1892:        """常時のハート加算を返す（UI表示専用）。"""`
- `llocg_ui/server.py:1912:        """常時のライブ合計スコア加算を返す（UI表示専用）。"""`
- `llocg_ui/server.py:2322:                # BODY trigger with clauses: ability_typeをヘッダに使う（例：常時）`

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
