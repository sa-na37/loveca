# Static Evidence PL!N-PR-024#A01

- audit_id: PL!N-PR-024#A01
- cardnumber: PL!N-PR-024
- cardname: 桜坂しずく
- effect_text: <BODY> / 自分と相手の成功ライブカード置き場にカードが合計4枚以上あるかぎり、<(ブレード)><(ブレード)> / を得る。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/effects/registry.py:191:    # Prompt: PL!N-bp1-003 桜坂しずく (ライブ開始時)`

## feature_term_search

- `llocg_ui/engine.py:278:    {"id": "opponent_success_count_same_gain_icons", "pattern": r"^自分と相手の成功ライブカード置き場にあるカードの枚数が同じ場合、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "opponent_success_count_same_gain_icons"},`
- `llocg_ui/engine.py:13998:                elif '自分と相手の成功ライブカード置き場にカードが合計' in blob and 'ブレード' in blob:`
- `llocg_ui/engine.py:13999:                    m_total_success = re.search(r'自分と相手の成功ライブカード置き場にカードが合計(\d+)枚以上', blob)`

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
      "effect_template": "自分と相手の成功ライブカード置き場にカードが合計4枚以上あるかぎり、<(ブレード)><(ブレード)>を得る。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分と相手の成功ライブカード置き場にカードが合計4枚以上あるかぎり、<(ブレード)><(ブレード)>\nを得る。"
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
