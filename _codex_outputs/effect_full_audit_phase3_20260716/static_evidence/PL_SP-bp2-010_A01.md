# Static Evidence PL!SP-bp2-010#A01

- audit_id: PL!SP-bp2-010#A01
- cardnumber: PL!SP-bp2-010
- cardname: ウィーン・マルガレーテ
- effect_text: <BODY> / 相手のライブカード置き場にあるすべてのライブカードは、成功させるための必要ハートが / <任意> / 多くなる。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- `llocg_ui/engine.py:1141:    current live (for example PL!SP-bp2-010). Keep the modifier in state so both`
- `llocg_ui/engine.py:18928:    # Generalized from PL!SP-bp2-010 Wien Margarete.`

## cardname_search

- not found

## feature_term_search

- `llocg_ui/engine.py:351:    {"id": "stage_heart_total_opponent_live_start_required_notice", "pattern": r"^自分のステージにいるメンバーが持つハートに<(?P<color>[^<>]+)>が合計(?P<count>\d+)つ以上ある場合、相手のライブ開始時、相手のライブカード置き場にあるライブカード1枚は、成功させるための必要ハートが<任意>多くなる。$", "op": "stage_heart_total_opponent_live_start_required_notice"},`

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
      "effect_template": "相手のライブカード置き場にあるすべてのライブカードは、成功させるための必要ハートが<任意>多くなる。",
      "cost_op": null,
      "effect_op": null,
      "raw": "相手のライブカード置き場にあるすべてのライブカードは、成功させるための必要ハートが\n<任意>\n多くなる。"
    }
  ]
}
```

## generic_matcher_candidate

- not found

## card_specific_route

- `llocg_ui/engine.py:1141:    current live (for example PL!SP-bp2-010). Keep the modifier in state so both`
- `llocg_ui/engine.py:18928:    # Generalized from PL!SP-bp2-010 Wien Margarete.`

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
