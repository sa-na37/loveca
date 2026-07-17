# Static Evidence PL!SP-pb2-041#A01

- audit_id: PL!SP-pb2-041#A01
- cardnumber: PL!SP-pb2-041
- cardname: 若菜四季
- effect_text: <BODY> / <(ブレード)><(ブレード)>を得る。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/engine.py:21214:                # Example: PL!SP-pb2-008 若菜四季.`
- `llocg_ui/effects/registry.py:129:    # Prompt 6: PL!SP-bp4-008 若菜四季 (ライブ開始時, no-cost)`

## feature_term_search

- not found

## compiled_db_entry

```json
{
  "ability_type": "常時",
  "trigger": "BODY",
  "conditions": "右サイド",
  "clauses": [
    {
      "optional": false,
      "cost_template": "",
      "effect_template": "<(ブレード)><(ブレード)>を得る。",
      "cost_op": null,
      "effect_op": null,
      "raw": "<(ブレード)><(ブレード)>を得る。"
    }
  ]
}
```

## generic_matcher_candidate

- `llocg_ui/engine.py:12090:      <常時> 自分か相手のステージにコスト13以上のメンバーがいる場合、<(ブレード)><(ブレード)>を得る。`
- `llocg_ui/effects/registry.py:28:        "effect_template": "ライブ終了時まで、自分の成功ライブカード置き場にあるカード1枚につき、<(ブレード)><(ブレード)>を得る。",`
- `llocg_ui/effects/registry.py:123:        "effect_template": "自分のステージのエリアすべてにメンバーが登場している場合、ライブ終了時まで、<(ブレード)><(ブレード)>を得る。",`
- `llocg_ui/effects/registry.py:298:        "effect_template": "自分のステージに、このメンバーよりコストの大きいメンバーがいる場合、<(ブレード)><(ブレード)><(ブレード)>を得る。",`

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

- `llocg_ui/engine.py:12090:      <常時> 自分か相手のステージにコスト13以上のメンバーがいる場合、<(ブレード)><(ブレード)>を得る。`
- `llocg_ui/effects/registry.py:28:        "effect_template": "ライブ終了時まで、自分の成功ライブカード置き場にあるカード1枚につき、<(ブレード)><(ブレード)>を得る。",`
- `llocg_ui/effects/registry.py:123:        "effect_template": "自分のステージのエリアすべてにメンバーが登場している場合、ライブ終了時まで、<(ブレード)><(ブレード)>を得る。",`
- `llocg_ui/effects/registry.py:298:        "effect_template": "自分のステージに、このメンバーよりコストの大きいメンバーがいる場合、<(ブレード)><(ブレード)><(ブレード)>を得る。",`

## ui_route

- not found

## reachable_from_runtime

No previous static matcher/resolve route; no pending/dispatch evidence in mapping

## conflicting_routes

none found in this static pass

- final_classification: STATIC_ANALYSIS_INCONCLUSIVE
- confidence: low
- reason: Search evidence is insufficient to confirm either implementation or absence.
