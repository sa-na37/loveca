# Static Evidence PL!HS-pb1-001#A01

- audit_id: PL!HS-pb1-001#A01
- cardnumber: PL!HS-pb1-001
- cardname: 日野下花帆
- effect_text: <BODY> / 自分のステージにほかの『スリーズブーケ』のメンバーが登場するたび、<(E)> / を支払ってもよい。そうした場合、エネルギーを2枚アクティブにする。
- previous_classification: NOT_IMPLEMENTED_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- `llocg_ui/effects/topdeck.py:336:            '日野下花帆 bp2-010' if ext_key == 'enter_top5_member_optional_pick' else`
- `llocg_ui/effects/live_start.py:938:    # Prompt 73: PL!HS-bp2-001 日野下花帆 (起動)`
- `llocg_ui/effects/registry.py:226:    # Prompt 73: PL!HS-bp2-001 日野下花帆 (起動)`
- `llocg_ui/effects/registry.py:234:            "source_name": "日野下花帆",`
- `llocg_ui/effects/registry.py:238:            "pending_label": "【日野下花帆】控え室からスコア3以下の蓮ノ空ライブカードを1枚選んでください",`
- `llocg_ui/effects/registry.py:239:            "no_candidates_log": "[AUTO_EXT] no 蓮ノ空 LIVE score<=3 in green_room (日野下花帆)"`

## feature_term_search

- `llocg_ui/engine.py:16472:            'text': f"【{_source_cn_or_default((trig or {}).get('source_cn', ''), 'この能力')}】ライブ開始時：エネルギー2枚を支払ってもよい。自分のステージに『{str((trig or {}).get('condition_group_name', '') or '虹ヶ咲')}』のメンバーがいる場合、このカードのスコアを+1する。",`
- `llocg_ui/engine.py:10376:    #   自分の成功ライブカード置き場にあるカードのスコアの合計が9以上の場合、エネルギーを2枚アクティブにする。`
- `llocg_ui/effects/registry.py:46:        "effect_template": "自分の成功ライブカード置き場にあるカードのスコアの合計が6以上の場合、エネルギーを2枚アクティブにする。",`

## compiled_db_entry

```json
{
  "ability_type": "自動",
  "trigger": "BODY",
  "conditions": "ターン2回",
  "clauses": [
    {
      "optional": false,
      "cost_template": "",
      "effect_template": "自分のステージにほかの『スリーズブーケ』のメンバーが登場するたび、<(E)>を支払ってもよい。そうした場合、エネルギーを2枚アクティブにする。",
      "cost_op": null,
      "effect_op": null,
      "raw": "自分のステージにほかの『スリーズブーケ』のメンバーが登場するたび、<(E)>\nを支払ってもよい。そうした場合、エネルギーを2枚アクティブにする。"
    }
  ]
}
```

## generic_matcher_candidate

- not found

## card_specific_route

- not found

## trigger_collection_route

- `llocg_ui/server.py:3424:    if(kind === 'mass_bottom_auto_ack') return '自動効果確認';`
- `llocg_ui/server.py:3469:    if(kind === 'mass_bottom_auto_ack') return '自動効果を確認してから、後続処理へ進みます。';`
- `llocg_ui/effects/stage_triggers.py:222:    # bp2_batch3_local_20260413f: PL!HS-bp2-015 藤島慈 (自動/BODY)`
- `llocg_ui/effects/helpers.py:908:            auto_detail = f'【{src_label}】自動効果\n効果：{auto_detail}'`
- `llocg_ui/effects/helpers.py:910:            auto_detail = f'【{src_label}】自動効果\n効果：{label_text}'`
- `llocg_ui/engine.py:2176:        timing = '自動効果'`

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
