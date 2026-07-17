# Static Evidence PL!SP-bp1-001#A01

- audit_id: PL!SP-bp1-001#A01
- cardnumber: PL!SP-bp1-001
- cardname: 澁谷かのん
- effect_text: <BODY> / 自分のステージにほかのメンバーがいない場合、自分はライブできない。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- not found

## feature_term_search

- `llocg_ui/engine.py:477:    {"id": "body_always_stage_other_member_blades", "pattern": r"^自分のステージにほかのメンバーがいないかぎり、(?P<blades>(?:<\(ブレード\)>)+)を得る。$", "op": "body_always_noop"},`
- `llocg_ui/engine.py:355:    {"id": "draw_then_no_live_until_end_turn", "pattern": r"^カードを(?P<n>\d+)枚引く。ライブ終了時まで、自分はライブできない。$", "op": "draw_then_no_live_until_end_turn"},`
- `llocg_ui/effects/registry.py:367:        "effect_template": "カードを1枚引く。ライブ終了時まで、自分はライブできない。",`

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
      "effect_template": "自分のステージにほかのメンバーがいない場合、自分はライブできない。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分のステージにほかのメンバーがいない場合、自分はライブできない。"
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
