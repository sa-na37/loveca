# Static Evidence PL!HS-bp1-003#A01

- audit_id: PL!HS-bp1-003#A01
- cardnumber: PL!HS-bp1-003
- cardname: 乙宗梢
- effect_text: <BODY> / 自分のステージのエリアすべてに『蓮ノ空』のメンバーが登場しており、かつ名前が異なる場合、「<常時>ライブの合計スコアを+1する。」を得る。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/effects/topdeck.py:337:            '乙宗梢 bp2-012' if ext_key == 'body_stage_to_green_top5_member_optional' else`
- `llocg_ui/effects/registry.py:305:        "gd": {"topk": "3", "source_name": "乙宗梢 bp2-003"},`
- `llocg_ui/effects/registry.py:322:        "gd": {"topk": "5", "filter_kind": "MEMBER", "optional": "1", "source_name": "乙宗梢 bp2-012"},`

## feature_term_search

- `llocg_ui/engine.py:13682:                if 'エリアすべてに『' in blob and 'のメンバーが登場しており、かつ名前が異なる場合' in blob and 'ライブの合計スコアを+1する' in blob:`
- `llocg_ui/engine.py:20140:                m = re.match(r'^自分のステージのエリアすべてに『(?P<group>[^』]+)』のメンバーが登場しており、かつ名前が異なる場合、「<ライブ成功時>エールにより公開された自分のカードの中にライブカードが(?P<c1>\d+)枚以上ある場合、ライブの合計スコアを\+(?P<b1>\d+)する。ライブカードが(?P<c2>\d+)枚以上ある場合、代わりに合計スコアを\+(?P<b2>\d+)する。」を得る。?$', eff_norm2)`

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
      "effect_template": "自分のステージのエリアすべてに『蓮ノ空』のメンバーが登場しており、かつ名前が異なる場合、「<常時>ライブの合計スコアを+1する。」を得る。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分のステージのエリアすべてに『蓮ノ空』のメンバーが登場しており、かつ名前が異なる場合、「<常時>ライブの合計スコアを+1する。」を得る。"
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
