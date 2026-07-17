# Static Evidence PL!N-PR-026#A02

- audit_id: PL!N-PR-026#A02
- cardnumber: PL!N-PR-026
- cardname: 天王寺璃奈
- effect_text: <BODY> / このメンバーは、このメンバーの下に置かれているコスト9以下の『虹ヶ咲』のメンバーカードが持つ / <ライブ成功時> / 能力をすべて得る。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/effects/live_start.py:626:            "text": "【天王寺璃奈】ライブ開始時：自分ステージのコスト合計が相手より低いなら、カードを2枚引き、手札1枚をデッキの一番上に置く",`
- `llocg_ui/effects/live_start.py:634:            gs.log.append(f"[PENDING] 天王寺璃奈: confirm draw2/hand top1 (my_cost={my_cost}, opp unavailable)")`

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
      "effect_template": "このメンバーは、このメンバーの下に置かれているコスト9以下の『虹ヶ咲』のメンバーカードが持つ<ライブ成功時>能力をすべて得る。",
      "cost_op": null,
      "effect_op": null,
      "raw": "このメンバーは、このメンバーの下に置かれているコスト9以下の『虹ヶ咲』のメンバーカードが持つ\n<ライブ成功時>\n能力をすべて得る。"
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
