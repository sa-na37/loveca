# Static Evidence PL!SP-bp2-004#A01

- audit_id: PL!SP-bp2-004#A01
- cardnumber: PL!SP-bp2-004
- cardname: 平安名すみれ
- effect_text: <BODY> / 自分のステージにいるメンバーのうち、センターエリアにいるメンバーが最も大きいコストを持つ場合、 / <黄> / を得る。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/engine.py:19665:    # Example: PL!SP-pb2-004 平安名すみれ.`

## feature_term_search

- not found

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
      "effect_template": "自分のステージにいるメンバーのうち、センターエリアにいるメンバーが最も大きいコストを持つ場合、<黄>を得る。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分のステージにいるメンバーのうち、センターエリアにいるメンバーが最も大きいコストを持つ場合、\n<黄>\nを得る。"
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

- final_classification: NOT_IMPLEMENTED_WITH_EVIDENCE
- confidence: medium
- reason: No card-specific route, no compiled op, and feature-term searches found no matching generic route in inspected runtime files.
