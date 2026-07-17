# Static Evidence PL!SP-bp4-009#A01

- audit_id: PL!SP-bp4-009#A01
- cardnumber: PL!SP-bp4-009
- cardname: 鬼塚夏美
- effect_text: <BODY> / 自分のステージにいるメンバーのコストが相手より低いかぎり、<(ブレード)><(ブレード)><(ブレード)> / を得る。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- not found

## feature_term_search

- `llocg_ui/engine.py:443:    {"id": "stage_cost_sum_lt_opponent_draw_hand_top", "pattern": r"^自分のステージにいるメンバーのコストの合計が相手より低い場合、カードを(?P<draw_n>\d+)枚引き、自分の手札を(?P<top_n>\d+)枚デッキの一番上に置く。$", "op": "stage_cost_sum_lt_opponent_manual"},`
- `llocg_ui/effects/registry.py:40:        "effect_template": "自分のステージにいるメンバーのコストの合計が相手より低い場合、カードを2枚引き、自分の手札を1枚デッキの一番上に置く。",`

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
      "effect_template": "自分のステージにいるメンバーのコストが相手より低いかぎり、<(ブレード)><(ブレード)><(ブレード)>を得る。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分のステージにいるメンバーのコストが相手より低いかぎり、<(ブレード)><(ブレード)><(ブレード)>\nを得る。"
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
