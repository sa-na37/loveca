# Static Evidence PL!HS-pb1-028#A03

- audit_id: PL!HS-pb1-028#A03
- cardnumber: PL!HS-pb1-028
- cardname: COMPASS
- effect_text: 
- previous_classification: UNREACHABLE_TRIGGER_CONFIRMED

## cardnumber_search

- not found

## cardname_search

- not found

## feature_term_search

- not found

## compiled_db_entry

```json
{}
```

## generic_matcher_candidate

- not found

## card_specific_route

- not found

## trigger_collection_route

- `llocg_ui/server.py:3697:    if(kind.startsWith('live_start') || kind === 'enqueue_pending_prompt') return 'ライブ開始時';`
- `llocg_ui/server.py:6075:    // Exact cardnumber only. Labels like "C: PL!N-bp1-003 ライブ開始時" must NOT match.`
- `llocg_ui/engine.py:129:    {"id": "live_storage_count_choose_group_live_no_live_start_topdeck_gain_icons", "pattern": r"^自分のライブカード置き場にカードが(?P<count_n>\d+)枚以上ある場合、その中から<ライブ開始時>能力を持たない『(?P<group>[^』]+)』のライブカードを1枚選び、デッキの一番上に置いてもよい。そうした場合、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>と?)+)を得る。$", "op": "live_storage_count_choose_group_live_no_live_start_topdeck_gain_icons"},`
- `llocg_ui/engine.py:260:    {"id": "live_success_stage_live_start_member_score", "pattern": r"^自分のステージに<ライブ開始時>を持つメンバーがいる場合、このカードのスコアを\+(?P<delta>\d+)する。$", "op": "live_success_stage_live_start_member_score"},`
- `llocg_ui/engine.py:341:    {"id": "disable_stage_group_live_start_then_retrieve", "pattern": r"^自分のステージにいる『(?P<group>[^』]+)』メンバー(?P<n>\d+)人のすべての<ライブ開始時>能力を、ライブ終了時まで、無効にしてもよい。これにより無効にした場合、自分の控え室から『(?P=group)』のカードを(?P<retrieve_n>\d+)枚手札に加える。$", "op": "disable_stage_group_live_start_then_retrieve"},`
- `llocg_ui/engine.py:351:    {"id": "stage_heart_total_opponent_live_start_required_notice", "pattern": r"^自分のステージにいるメンバーが持つハートに<(?P<color>[^<>]+)>が合計(?P<count>\d+)つ以上ある場合、相手のライブ開始時、相手のライブカード置き場にあるライブカード1枚は、成功させるための必要ハートが<任意>多くなる。$", "op": "stage_heart_total_opponent_live_start_required_notice"},`

## pending_creation_route

- not found

## resolver_route

- not found

## ui_route

- not found

## reachable_from_runtime

Route candidate exists or text matched, but previous reachable flag is not YES; trigger collection path is not proven

## conflicting_routes

none found in this static pass

- final_classification: NOT_IMPLEMENTED_WITH_EVIDENCE
- confidence: medium
- reason: No card-specific route, no compiled op, and feature-term searches found no matching generic route in inspected runtime files.
