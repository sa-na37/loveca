# Static Evidence PL!HS-bp6-006#A02

- audit_id: PL!HS-bp6-006#A02
- cardnumber: PL!HS-bp6-006
- cardname: 安養寺姫芽
- effect_text: <BODY> / このメンバーは『みらくらぱーく！』以外のメンバーカードとのバトンタッチで控え室に置けない。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/engine.py:10983:    # hand->set during the current LIVE_SET phase; default 3, may be reduced by effects like 安養寺姫芽`
- `llocg_ui/engine.py:10985:    # one-shot delta reserved for the next LIVE_SET phase (e.g. -1 by 安養寺姫芽)`
- `llocg_ui/effects/live_start.py:950:    # Prompt 80: PL!HS-bp2-018 安養寺姫芽 (登場)`
- `llocg_ui/effects/special.py:28:        src = str((ctx or {}).get("source_cn") or "安養寺姫芽")`

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
      "effect_template": "このメンバーは『みらくらぱーく！』以外のメンバーカードとのバトンタッチで控え室に置けない。",
      "cost_op": null,
      "effect_op": null,
      "raw": "このメンバーは『みらくらぱーく！』以外のメンバーカードとのバトンタッチで控え室に置けない。"
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
