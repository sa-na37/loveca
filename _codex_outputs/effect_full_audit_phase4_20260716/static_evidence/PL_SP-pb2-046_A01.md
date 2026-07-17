# Static Evidence PL!SP-pb2-046#A01

- audit_id: PL!SP-pb2-046#A01
- cardnumber: PL!SP-pb2-046
- cardname: Butterfly Wing
- effect_text: <BODY> / 自分のステージにいるメンバーが持つ / <ライブ開始時> / 能力は発動しない。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- not found

## feature_term_search

- `llocg_ui/engine.py:208:    {"id": "live_success_score_if_revealed_live_or_stage_heart_kinds_or_moved", "pattern": r"^エールにより公開された自分のカードの中にライブカードが(?P<live_n>\d+)枚以上あるか、自分のステージにいるメンバーが持つハートの中に<(?:\(桃\)|桃)>、<(?:\(赤\)|赤)>、<(?:\(黄\)|黄)>、<(?:\(緑\)|緑)>、<(?:\(青\)|青)>、<(?:\(紫\)|紫)>のうち合計(?P<kind_n>\d+)種類以上あるか、このターンに自分のステージにいるメンバーがエリアを移動している場合、このカードのスコアを\+(?P<delta>\d+)する。$", "op": "live_success_score_if_revealed_live_or_stage_heart_kinds_or_moved"},`
- `llocg_ui/engine.py:212:    {"id": "live_success_score_if_stage_heart_total_gt_opponent", "pattern": r"^自分のステージにいるメンバーが持つハートの総数が、相手のステージにいるメンバーが持つハートの総数より多い場合、このカードのスコアを\+(?P<delta>\d+)する。$", "op": "live_success_score_if_stage_heart_total_gt_opponent"},`
- `llocg_ui/engine.py:351:    {"id": "stage_heart_total_opponent_live_start_required_notice", "pattern": r"^自分のステージにいるメンバーが持つハートに<(?P<color>[^<>]+)>が合計(?P<count>\d+)つ以上ある場合、相手のライブ開始時、相手のライブカード置き場にあるライブカード1枚は、成功させるための必要ハートが<任意>多くなる。$", "op": "stage_heart_total_opponent_live_start_required_notice"},`
- `llocg_ui/engine.py:391:    {"id": "stage_blade_total_gte_reduce_required_any", "pattern": r"^自分のステージにいるメンバーが持つ<\(ブレード\)>の合計が(?P<count>\d+)以上の場合、このカードを成功させるための必要ハートは(?P<anys>(?:<任意>|<\(任意\)>)+)少なくなる。$", "op": "stage_blade_total_gte_reduce_required_any"},`

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
      "effect_template": "自分のステージにいるメンバーが持つ<ライブ開始時>能力は発動しない。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分のステージにいるメンバーが持つ\n<ライブ開始時>\n能力は発動しない。"
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
