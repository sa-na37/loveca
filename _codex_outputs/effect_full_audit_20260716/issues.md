# Issues

Runtime and DB were not modified during this audit. Each issue includes a reproduction harness, but static findings require follow-up runtime/UI execution before closing.

## ISS-0001 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `LL-bp2-001#A02`
- test_case_id: `LL-bp2-001#A02#T01`
- cardnumber: `LL-bp2-001`
- cardname: `渡辺曜＆鬼塚夏美＆大沢瑠璃乃`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このメンバーはバトンタッチで控え室に置けない。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/LL-bp2-001_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='LL-bp2-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0002 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `LL-bp7-001#A01`
- test_case_id: `LL-bp7-001#A01#T01`
- cardnumber: `LL-bp7-001`
- cardname: `国木田花丸＆優木せつ菜＆嵐千砂都`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このカードのプレイに際し、自分の手札から「国木田花丸」と「優木せつ菜」と「嵐千砂都」のメンバーカードをそれぞれ1枚ずつ控え室に置いてもよい。そうしたとき、このカードのコストは10になる。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/LL-bp7-001_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='LL-bp7-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0003 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!-PR-005#A01`
- test_case_id: `PL!-PR-005#A01#T01`
- cardnumber: `PL!-PR-005`
- cardname: `星空凛`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<登場>
以下から1つを選ぶ。
・カードを1枚引き、手札を1枚控え室に置く。
・相手のステージにいるすべてのコスト2以下のメンバーをウェイトにする。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-PR-005_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-PR-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0004 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!-PR-006#A01`
- test_case_id: `PL!-PR-006#A01#T01`
- cardnumber: `PL!-PR-006`
- cardname: `西木野真姫`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<登場>
以下から1つを選ぶ。
・カードを1枚引き、手札を1枚控え室に置く。
・相手のステージにいるすべてのコスト2以下のメンバーをウェイトにする。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-PR-006_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-PR-006'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0005 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!-PR-008#A01`
- test_case_id: `PL!-PR-008#A01#T01`
- cardnumber: `PL!-PR-008`
- cardname: `小泉花陽`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<登場>
以下から1つを選ぶ。
・カードを1枚引き、手札を1枚控え室に置く。
・相手のステージにいるすべてのコスト2以下のメンバーをウェイトにする。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-PR-008_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-PR-008'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0006 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!-PR-020#A01`
- test_case_id: `PL!-PR-020#A01#T01`
- cardnumber: `PL!-PR-020`
- cardname: `高坂穂乃果`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ開始時>
<センター>
自分のライブカード置き場にあるライブカードのスコアの合計が8以上の場合、『
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-PR-020_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-PR-020'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0007 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!-PR-020#A02`
- test_case_id: `PL!-PR-020#A02#T01`
- cardnumber: `PL!-PR-020`
- cardname: `高坂穂乃果`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
ライブの合計スコアを+1する。』を得る。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-PR-020_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-PR-020'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0008 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp3-002#A02`
- test_case_id: `PL!-bp3-002#A02#T01`
- cardnumber: `PL!-bp3-002`
- cardname: `絢瀬絵里`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
相手のステージにいるウェイト状態のメンバー1人につき、
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp3-002_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp3-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0009 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp4-002#A01`
- test_case_id: `PL!-bp4-002#A01#T01`
- cardnumber: `PL!-bp4-002`
- cardname: `絢瀬絵里`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のライブ中のライブカードに、
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp4-002_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp4-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0010 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp4-002#A02`
- test_case_id: `PL!-bp4-002#A02#T01`
- cardnumber: `PL!-bp4-002`
- cardname: `絢瀬絵里`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ開始時>
能力も
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp4-002_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp4-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0011 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp4-002#A03`
- test_case_id: `PL!-bp4-002#A03#T01`
- cardnumber: `PL!-bp4-002`
- cardname: `絢瀬絵里`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ成功時>
能力も持たないカードがあるかぎり、
<紫>
<紫>
を加える。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp4-002_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp4-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0012 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp4-002#A04`
- test_case_id: `PL!-bp4-002#A04#T01`
- cardnumber: `PL!-bp4-002`
- cardname: `絢瀬絵里`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
手札を2枚控え室に置く：自分の控え室から『μ's』のライブカードを1枚手札に加える。この能力は、自分の成功ライブカード置き場にあるカードのスコアの合計が6以上の場合のみ起動できる。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp4-002_A04_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp4-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0013 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp4-014#A02`
- test_case_id: `PL!-bp4-014#A02#T01`
- cardnumber: `PL!-bp4-014`
- cardname: `星空凛`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ開始時>
能力も
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp4-014_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp4-014'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0014 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp4-014#A03`
- test_case_id: `PL!-bp4-014#A03#T01`
- cardnumber: `PL!-bp4-014`
- cardname: `星空凛`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ成功時>
能力も持たないカードがある場合、ライブ終了時まで、自分のステージにいるこのメンバー以外のメンバー1人は、
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp4-014_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp4-014'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0015 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp4-018#A01`
- test_case_id: `PL!-bp4-018#A01#T01`
- cardnumber: `PL!-bp4-018`
- cardname: `矢澤にこ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分の成功ライブカード置き場にあるカードのスコアの合計が相手より高いかぎり、
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp4-018_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp4-018'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0016 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp5-024#A01`
- test_case_id: `PL!-bp5-024#A01#T01`
- cardnumber: `PL!-bp5-024`
- cardname: `Private Wars`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ開始時>
自分のステージに『A-RISE』のメンバーがいる場合、以下から1つを選ぶ。
・ウェイト状態のメンバー1人をアクティブにし、ライブ終了時まで、そのメンバーは
<(ブレード)>
を得る。
・相手のステージにいる元々持つ
<(ブレード)>
が3つ以下のメンバー1人をウェイトにする。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp5-024_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp5-024'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0017 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp5-111#A02`
- test_case_id: `PL!-bp5-111#A02#T01`
- cardnumber: `PL!-bp5-111`
- cardname: `綺羅ツバサ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
手札を1枚控え室に置く：ウェイト状態のメンバー1人をアクティブにする。これにより相手のステージにいるメンバーをアクティブにした場合、自分の控え室からライブカードを1枚控え室に置く。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp5-111_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp5-111'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0018 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp6-002#A02`
- test_case_id: `PL!-bp6-002#A02#T01`
- cardnumber: `PL!-bp6-002`
- cardname: `絢瀬絵里`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
能力を持つ『μ's』のカードを1枚公開して手札に加えてもよい。残りを控え室に置く。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp6-002_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp6-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0019 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp6-009#A01`
- test_case_id: `PL!-bp6-009#A01#T01`
- cardnumber: `PL!-bp6-009`
- cardname: `矢澤にこ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
<センター>
自分のステージの右サイドエリアと左サイドエリアに、元々持つ
<(ブレード)>
の数が2つのメンバーがいるかぎり、ライブの合計スコアを+1する。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp6-009_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp6-009'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0020 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp6-019#A01`
- test_case_id: `PL!-bp6-019#A01#T01`
- cardnumber: `PL!-bp6-019`
- cardname: `Music S.T.A.R.T!!`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このカードが自分の成功ライブカード置き場にあるかぎり、元々のコストが17以上の『μ's』のメンバーカードを自分の手札から登場させるためのコストは2減る。この効果は重複しない。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp6-019_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp6-019'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0021 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp6-020#A01`
- test_case_id: `PL!-bp6-020#A01#T01`
- cardnumber: `PL!-bp6-020`
- cardname: `Dancing stars on me!`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<自動>
<ターン1回>
自分のステージのセンターエリアにいる『μ's』のメンバーの
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp6-020_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp6-020'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0022 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp6-020#A02`
- test_case_id: `PL!-bp6-020#A02#T01`
- cardnumber: `PL!-bp6-020`
- cardname: `Dancing stars on me!`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ開始時>
能力が解決したとき、そのメンバーをポジションチェンジする。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp6-020_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp6-020'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0023 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp6-020#A03`
- test_case_id: `PL!-bp6-020#A03#T01`
- cardnumber: `PL!-bp6-020`
- cardname: `Dancing stars on me!`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン1回>
自分のステージのセンターエリアにいる『μ's』のメンバーの
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp6-020_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp6-020'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0024 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp6-020#A04`
- test_case_id: `PL!-bp6-020#A04#T01`
- cardnumber: `PL!-bp6-020`
- cardname: `Dancing stars on me!`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ成功時>
能力が解決したとき、そのメンバーがこのターン中に移動している場合、このカードのスコアを+1する。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp6-020_A04_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp6-020'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0025 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp6-022#A01`
- test_case_id: `PL!-bp6-022#A01#T01`
- cardnumber: `PL!-bp6-022`
- cardname: `Dreamin' Go! Go!!`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このカードが自分の成功ライブカード置き場にある限り、自分の元々のスコア5以上の『μ's』のライブカードの必要ハートを
<任意>
<任意>
減らす。この効果は重複しない。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp6-022_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp6-022'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0026 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!-bp6-024#A01`
- test_case_id: `PL!-bp6-024#A01#T01`
- cardnumber: `PL!-bp6-024`
- cardname: `錯覚CROSSROADS`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このカードを成功ライブカード置き場に置く場合、代わりに自分の控え室にある『μ's』のライブカードを1枚置いてもよい。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-bp6-024_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-bp6-024'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0027 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!-pb1-002#A02`
- test_case_id: `PL!-pb1-002#A02#T01`
- cardnumber: `PL!-pb1-002`
- cardname: `絢瀬絵里`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
相手のステージにいるウェイト状態のメンバー1人につき、
<紫>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-pb1-002_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-pb1-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0028 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!-pb1-013#A01`
- test_case_id: `PL!-pb1-013#A01#T01`
- cardnumber: `PL!-pb1-013`
- cardname: `園田海未`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<起動>
<ターン1回>
<(E)>
<(E)>
自分の手札を、相手は見ないで1枚選び公開する。これにより公開されたカードがライブカードの場合、ライブ終了時まで、このメンバーは『
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-pb1-013_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-pb1-013'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0029 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!-pb1-013#A02`
- test_case_id: `PL!-pb1-013#A02#T01`
- cardnumber: `PL!-pb1-013`
- cardname: `園田海未`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
ライブの合計スコアを+1する。』を得る。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-pb1-013_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-pb1-013'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0030 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!-pb1-015#A02`
- test_case_id: `PL!-pb1-015#A02#T01`
- cardnumber: `PL!-pb1-015`
- cardname: `西木野真姫`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン1回>
自分のカードの効果によって、相手のステージにいるアクティブ状態のコスト4以下のメンバーがウェイト状態になったとき、カードを1枚引く。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_-pb1-015_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-pb1-015'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0031 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-bp1-003#A01`
- test_case_id: `PL!HS-bp1-003#A01#T01`
- cardnumber: `PL!HS-bp1-003`
- cardname: `乙宗梢`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のステージのエリアすべてに『蓮ノ空』のメンバーが登場しており、かつ名前が異なる場合、「
<常時>
ライブの合計スコアを+1する。」を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-bp1-003_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-bp1-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0032 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-bp2-020#A01`
- test_case_id: `PL!HS-bp2-020#A01#T01`
- cardnumber: `PL!HS-bp2-020`
- cardname: `Link to the FUTURE`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
すべての領域にあるこのカードは『スリーズブーケ』、『DOLLCHESTRA』、『みらくらぱーく！』として扱う。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-bp2-020_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-bp2-020'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0033 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-bp5-001#A02`
- test_case_id: `PL!HS-bp5-001#A02#T01`
- cardnumber: `PL!HS-bp5-001`
- cardname: `日野下花帆`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
<(E)>
<(E)>
手札のライブカードを1枚公開する：自分の控え室から、これにより公開したカードのカード名がすべて含まれるライブカードを1枚手札に加える。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-bp5-001_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-bp5-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0034 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-bp5-016#A02`
- test_case_id: `PL!HS-bp5-016#A02#T01`
- cardnumber: `PL!HS-bp5-016`
- cardname: `桂城泉`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
相手のステージにウェイト状態のメンバーが2人以上いるかぎり、
<紫>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-bp5-016_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-bp5-016'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0035 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-bp5-018#A01`
- test_case_id: `PL!HS-bp5-018#A01#T01`
- cardnumber: `PL!HS-bp5-018`
- cardname: `AURORA FLOWER`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
すべての領域にあるこのカードは『スリーズブーケ』、『DOLLCHESTRA』、『みらくらぱーく！』として扱う。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-bp5-018_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-bp5-018'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0036 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-bp5-022#A01`
- test_case_id: `PL!HS-bp5-022#A01#T01`
- cardnumber: `PL!HS-bp5-022`
- cardname: `Retrofuture`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ開始時>
<(E)>
<(E)>
支払ってもよい：自分のステージにコスト9以上の『Edel Note』のメンバーがいる場合、以下から1つを選ぶ。
・自分の控え室からコスト4以下の『Edel Note』のメンバーカードを1枚、メンバーのいないエリアに登場させる。
・このカードの必要ハートを
<紫>
減らす。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-bp5-022_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-bp5-022'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0037 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-bp6-006#A02`
- test_case_id: `PL!HS-bp6-006#A02#T01`
- cardnumber: `PL!HS-bp6-006`
- cardname: `安養寺姫芽`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このメンバーは『みらくらぱーく！』以外のメンバーカードとのバトンタッチで控え室に置けない。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-bp6-006_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-bp6-006'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0038 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-bp6-007#A01`
- test_case_id: `PL!HS-bp6-007#A01#T01`
- cardnumber: `PL!HS-bp6-007`
- cardname: `セラス 柳田 リリエンフェルト`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン1回>
自分のステージに『Edel Note』のメンバーが登場したとき、相手は、自身のステージにいるアクティブ状態のメンバー1人をウェイトにする。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-bp6-007_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-bp6-007'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0039 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-bp6-014#A01`
- test_case_id: `PL!HS-bp6-014#A01#T01`
- cardnumber: `PL!HS-bp6-014`
- cardname: `安養寺姫芽`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
このカードを手札から控え室に置く：カードを1枚引き、ライブ終了時まで、自分のステージにいる「藤島慈」か「大沢瑠璃乃」のうち1人は
<(ブレード)>
を得る。この能力は、このカードが手札にある場合のみ起動できる。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-bp6-014_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-bp6-014'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0040 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-cl1-004#A01`
- test_case_id: `PL!HS-cl1-004#A01#T01`
- cardnumber: `PL!HS-cl1-004`
- cardname: `百生吟子`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<登場>
以下から1つを選ぶ。
・自分のデッキの上からカードを3枚控え室に置く。
・相手のステージにいるコスト2以下のメンバー1人をウェイトにする。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-cl1-004_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-cl1-004'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0041 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-cl1-011#A01`
- test_case_id: `PL!HS-cl1-011#A01#T01`
- cardnumber: `PL!HS-cl1-011`
- cardname: `ド！ド！ド！`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ成功時>
<(E)>
支払ってもよい：以下から1つを選ぶ。
・自分の控え室からメンバーカードを1枚手札に加える。
・自分のライブカード置き場にカードが2枚以上ある場合、自分の控え室から『蓮ノ空』のライブカードを1枚手札に加える。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-cl1-011_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-cl1-011'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0042 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-pb1-001#A01`
- test_case_id: `PL!HS-pb1-001#A01#T01`
- cardnumber: `PL!HS-pb1-001`
- cardname: `日野下花帆`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン2回>
自分のステージにほかの『スリーズブーケ』のメンバーが登場するたび、
<(E)>
を支払ってもよい。そうした場合、エネルギーを2枚アクティブにする。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-pb1-001_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-pb1-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0043 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-pb1-002#A01`
- test_case_id: `PL!HS-pb1-002#A01#T01`
- cardnumber: `PL!HS-pb1-002`
- cardname: `村野さやか`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
手札の「村野さやか」のメンバーカードを1枚公開する：これにより公開したカードをこのメンバーの下に置く。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-pb1-002_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-pb1-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0044 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-pb1-003#A02`
- test_case_id: `PL!HS-pb1-003#A02#T01`
- cardnumber: `PL!HS-pb1-003`
- cardname: `大沢瑠璃乃`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン2回>
自分の手札からカードが1枚以上控え室に置かれるたび、ライブ終了時まで、
<桃>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-pb1-003_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-pb1-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0045 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-pb1-007#A02`
- test_case_id: `PL!HS-pb1-007#A02#T01`
- cardnumber: `PL!HS-pb1-007`
- cardname: `セラス 柳田 リリエンフェルト`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のステージにメンバーがちょうど2人おり、かつ相手のステージにメンバーが3人以上いるかぎり、
<紫>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-pb1-007_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-pb1-007'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0046 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-pb1-008#A02`
- test_case_id: `PL!HS-pb1-008#A02#T01`
- cardnumber: `PL!HS-pb1-008`
- cardname: `桂城泉`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
相手のステージにいるメンバーはアクティブフェイズにアクティブにならない。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-pb1-008_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-pb1-008'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0047 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-pb1-009#A01`
- test_case_id: `PL!HS-pb1-009#A01#T01`
- cardnumber: `PL!HS-pb1-009`
- cardname: `日野下花帆`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<センター>
<ターン2回>
自分のステージに『蓮ノ空』のメンバーが登場するたび、ライブ終了時まで、
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-pb1-009_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-pb1-009'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0048 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-pb1-014#A02`
- test_case_id: `PL!HS-pb1-014#A02#T01`
- cardnumber: `PL!HS-pb1-014`
- cardname: `安養寺姫芽`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このメンバーの正面のエリアにいる相手のメンバーのコストが、このメンバーのコストより高いかぎり、
<桃>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-pb1-014_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-pb1-014'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0049 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-pb1-015#A01`
- test_case_id: `PL!HS-pb1-015#A01#T01`
- cardnumber: `PL!HS-pb1-015`
- cardname: `セラス 柳田 リリエンフェルト`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のステージにほかのメンバーがいないかぎり、
<(ブレード)>
<(ブレード)>
<(ブレード)>
を失う。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-pb1-015_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-pb1-015'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0050 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-pb1-028#A02`
- test_case_id: `PL!HS-pb1-028#A02#T01`
- cardnumber: `PL!HS-pb1-028`
- cardname: `COMPASS`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ開始時>
能力1つを発動させてよい。
（
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-pb1-028_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-pb1-028'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0051 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-pb1-028#A03`
- test_case_id: `PL!HS-pb1-028#A03#T01`
- cardnumber: `PL!HS-pb1-028`
- cardname: `COMPASS`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ開始時>
能力がコストを持つ場合、支払って発動させる。）
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-pb1-028_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-pb1-028'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0052 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-sd1-004#A02`
- test_case_id: `PL!HS-sd1-004#A02#T01`
- cardnumber: `PL!HS-sd1-004`
- cardname: `百生吟子`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のステージに「日野下花帆」か「徒町小鈴」か「安養寺姫芽」がいるかぎり、
<緑>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-sd1-004_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-sd1-004'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0053 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-sd1-005#A02`
- test_case_id: `PL!HS-sd1-005#A02#T01`
- cardnumber: `PL!HS-sd1-005`
- cardname: `徒町小鈴`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のステージに「村野さやか」か「百生吟子」か「安養寺姫芽」がいるかぎり、
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-sd1-005_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-sd1-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0054 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!HS-sd1-020#A01`
- test_case_id: `PL!HS-sd1-020#A01#T01`
- cardnumber: `PL!HS-sd1-020`
- cardname: `Link to the FUTURE（104期Ver.）`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
すべての領域にあるこのカードは『スリーズブーケ』、『DOLLCHESTRA』、『みらくらぱーく！』として扱う。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_HS-sd1-020_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!HS-sd1-020'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0055 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-PR-003#A01`
- test_case_id: `PL!N-PR-003#A01#T01`
- cardnumber: `PL!N-PR-003`
- cardname: `上原歩夢`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
手札をすべて公開する：自分のステージにほかのメンバーがおり、かつこれにより公開した手札の中にライブカードがない場合、自分のデッキの上からカードを5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-PR-003_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-PR-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0056 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-PR-008#A01`
- test_case_id: `PL!N-PR-008#A01#T01`
- cardnumber: `PL!N-PR-008`
- cardname: `近江彼方`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
手札をすべて公開する：自分のステージにほかのメンバーがおり、かつこれにより公開した手札の中にライブカードがない場合、自分のデッキの上からカードを5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-PR-008_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-PR-008'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0057 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-PR-010#A01`
- test_case_id: `PL!N-PR-010#A01#T01`
- cardnumber: `PL!N-PR-010`
- cardname: `エマ・ヴェルデ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
手札をすべて公開する：自分のステージにほかのメンバーがおり、かつこれにより公開した手札の中にライブカードがない場合、自分のデッキの上からカードを5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-PR-010_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-PR-010'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0058 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-PR-024#A01`
- test_case_id: `PL!N-PR-024#A01#T01`
- cardnumber: `PL!N-PR-024`
- cardname: `桜坂しずく`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分と相手の成功ライブカード置き場にカードが合計4枚以上あるかぎり、
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-PR-024_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-PR-024'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0059 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-PR-025#A01`
- test_case_id: `PL!N-PR-025#A01#T01`
- cardnumber: `PL!N-PR-025`
- cardname: `優木せつ菜`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン2回>
自分のステージに、このメンバーか、ほかのメンバーがバトンタッチして登場したとき、カードを1枚引く。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-PR-025_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-PR-025'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0060 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-PR-026#A02`
- test_case_id: `PL!N-PR-026#A02#T01`
- cardnumber: `PL!N-PR-026`
- cardname: `天王寺璃奈`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このメンバーは、このメンバーの下に置かれているコスト9以下の『虹ヶ咲』のメンバーカードが持つ
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-PR-026_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-PR-026'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0061 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-PR-026#A03`
- test_case_id: `PL!N-PR-026#A03#T01`
- cardnumber: `PL!N-PR-026`
- cardname: `天王寺璃奈`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ成功時>
能力をすべて得る。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-PR-026_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-PR-026'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0062 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-PR-027#A01`
- test_case_id: `PL!N-PR-027#A01#T01`
- cardnumber: `PL!N-PR-027`
- cardname: `朝香果林`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分と相手のステージにメンバーが合計6人いるかぎり、
<赤>
<青>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-PR-027_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-PR-027'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0063 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp1-002#A02`
- test_case_id: `PL!N-bp1-002#A02#T01`
- cardnumber: `PL!N-bp1-002`
- cardname: `中須かすみ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<(E)>
<(E)>
, 手札を1枚控え室に置く：このカードを控え室からステージに登場させる。この能力は、このカードが控え室にある場合のみ起動できる。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp1-002_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp1-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0064 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp1-008#A01`
- test_case_id: `PL!N-bp1-008#A01#T01`
- cardnumber: `PL!N-bp1-008`
- cardname: `エマ・ヴェルデ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
手札のメンバーカードを1枚控え室に置く：自分の控え室から、これにより控え室に置いたメンバーカードより、コストの低いメンバーカードを1枚手札に加える。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp1-008_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp1-008'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0065 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp3-003#A02`
- test_case_id: `PL!N-bp3-003#A02#T01`
- cardnumber: `PL!N-bp3-003`
- cardname: `桜坂しずく`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<登場>
能力1つを使用する。
（
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp3-003_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp3-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0066 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp3-003#A03`
- test_case_id: `PL!N-bp3-003#A03#T01`
- cardnumber: `PL!N-bp3-003`
- cardname: `桜坂しずく`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<登場>
能力がコストを持つ場合、支払って発動する。）
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp3-003_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp3-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0067 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp3-005#A03`
- test_case_id: `PL!N-bp3-005#A03#T01`
- cardnumber: `PL!N-bp3-005`
- cardname: `宮下愛`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
ライブの合計スコアを+1する。』を得る。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp3-005_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp3-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0068 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp4-007#A02`
- test_case_id: `PL!N-bp4-007#A02#T01`
- cardnumber: `PL!N-bp4-007`
- cardname: `優木せつ菜`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分と相手のエネルギーの合計が15枚以上あるかぎり、
<赤>
<赤>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp4-007_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp4-007'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0069 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp4-008#A01`
- test_case_id: `PL!N-bp4-008#A01#T01`
- cardnumber: `PL!N-bp4-008`
- cardname: `エマ・ヴェルデ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
手札を1枚控え室に置く：エネルギー1枚か『虹ヶ咲』のメンバー1人をアクティブにする。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp4-008_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp4-008'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0070 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp4-012#A01`
- test_case_id: `PL!N-bp4-012#A01#T01`
- cardnumber: `PL!N-bp4-012`
- cardname: `鐘嵐珠`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
相手の成功ライブカード置き場にあるカードのスコアの合計が6以上であるかぎり、ライブの合計スコアを+1する。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp4-012_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp4-012'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0071 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp4-018#A01`
- test_case_id: `PL!N-bp4-018#A01#T01`
- cardnumber: `PL!N-bp4-018`
- cardname: `近江彼方`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン1回>
自分のメインフェイズの間、このメンバーがアクティブ状態からウェイト状態になった時、カードを1枚引き、手札からカードを1枚控え室に置く。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp4-018_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp4-018'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0072 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp4-026#A01`
- test_case_id: `PL!N-bp4-026#A01#T01`
- cardnumber: `PL!N-bp4-026`
- cardname: `DIVE!`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
自分のメインフェイズにこのカードが控え室から手札に加えられたとき、自分の手札からカード名が「DIVE！」のカード1枚を表向きでライブカード置き場に置いてもよい。そうした場合、次のライブカードセットフェイズで自分のライブカード置き場におけるカードの枚数の条件が1枚減る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp4-026_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp4-026'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0073 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp4-026#A02`
- test_case_id: `PL!N-bp4-026#A02#T01`
- cardnumber: `PL!N-bp4-026`
- cardname: `DIVE!`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
このカードが表向きでライブカード置き場に置かれたとき、ライブ終了時まで、自分のステージにいる『虹ヶ咲』のメンバー1人は、
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp4-026_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp4-026'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0074 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp4-030#A01`
- test_case_id: `PL!N-bp4-030#A01#T01`
- cardnumber: `PL!N-bp4-030`
- cardname: `Daydream Mermaid`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ成功時>
以下から1つを選ぶ。自分の成功ライブカード置き場に『虹ヶ咲』のカードがある場合、代わりに1つ以上を選ぶ。
・自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。
・自分の控え室からメンバーカードを1枚手札に加える。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp4-030_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp4-030'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0075 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp5-001#A01`
- test_case_id: `PL!N-bp5-001#A01#T01`
- cardnumber: `PL!N-bp5-001`
- cardname: `上原歩夢`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<自動>
<ターン1回>
自分がエールしたとき、エールにより公開された自分のカードが持つブレードハートの中に
<桃>
、
<赤>
、
<黄>
、
<緑>
、
<青>
、
<紫>
、
<ALL>
のうち、3種類以上ある場合、ライブ終了時まで、
<桃>
を得る。6種類以上ある場合、さらにライブ終了時まで、『
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp5-001_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp5-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0076 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp5-001#A02`
- test_case_id: `PL!N-bp5-001#A02#T01`
- cardnumber: `PL!N-bp5-001`
- cardname: `上原歩夢`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
ライブの合計スコアを+1する。』を得る。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp5-001_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp5-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0077 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp5-002#A01`
- test_case_id: `PL!N-bp5-002#A01#T01`
- cardnumber: `PL!N-bp5-002`
- cardname: `中須かすみ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分と相手のステージの中で、このメンバーがほかのすべてのメンバーより多くのハートを持つかぎり、ライブの合計スコアを+1する。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp5-002_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp5-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0078 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp5-003#A01`
- test_case_id: `PL!N-bp5-003#A01#T01`
- cardnumber: `PL!N-bp5-003`
- cardname: `桜坂しずく`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
手札を1枚控え室に置く：自分の控え室にあるライブカードを1枚選び、そのカードのスコアに等しい数の
<(E)>
を支払ってもよい。そうした場合、そのライブカードを手札に加える。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp5-003_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp5-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0079 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp5-011#A01`
- test_case_id: `PL!N-bp5-011#A01#T01`
- cardnumber: `PL!N-bp5-011`
- cardname: `ミア・テイラー`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<登場>
以下から1つを選ぶ。
・自分の控え室にカード名が異なるライブカードが3枚以上ある場合、自分の控え室からライブカードを1枚手札に加える。
・自分の控え室にグループ名が異なるライブカードが3枚以上ある場合、自分の控え室からライブカードを2枚手札に加える。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp5-011_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp5-011'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0080 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp5-030#A01`
- test_case_id: `PL!N-bp5-030#A01#T01`
- cardnumber: `PL!N-bp5-030`
- cardname: `繚乱！ビクトリーロード`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
自分のステージにいるメンバーの
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp5-030_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp5-030'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0081 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp5-030#A02`
- test_case_id: `PL!N-bp5-030#A02#T01`
- cardnumber: `PL!N-bp5-030`
- cardname: `繚乱！ビクトリーロード`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ開始時>
能力が解決するたび、そのメンバーが
<ALL>
を持たない場合、ライブ終了時まで、そのメンバーは
<ALL>
を得る。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp5-030_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp5-030'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0082 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp5-030#A03`
- test_case_id: `PL!N-bp5-030#A03#T01`
- cardnumber: `PL!N-bp5-030`
- cardname: `繚乱！ビクトリーロード`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
自分のステージにいるメンバーの
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp5-030_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp5-030'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0083 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp5-030#A04`
- test_case_id: `PL!N-bp5-030#A04#T01`
- cardnumber: `PL!N-bp5-030`
- cardname: `繚乱！ビクトリーロード`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ成功時>
能力が解決するたび、カードを1枚引く。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp5-030_A04_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp5-030'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0084 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp7-004#A01`
- test_case_id: `PL!N-bp7-004#A01#T01`
- cardnumber: `PL!N-bp7-004`
- cardname: `朝香果林`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
エネルギー置き場にあるエネルギー1枚をこのメンバーの下に置く：相手のステージにいる、元々持つ
<(ブレード)>
の数がこのメンバーの下にあるエネルギーカードの枚数に1を足した数以下のメンバー1人をウェイトにする。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp7-004_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp7-004'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0085 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-bp7-005#A01`
- test_case_id: `PL!N-bp7-005#A01#T01`
- cardnumber: `PL!N-bp7-005`
- cardname: `宮下愛`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<登場>
自分のステージに名前の異なる『DiverDiva』のメンバーが2人いる場合、以下から1つを選ぶ。
・エネルギーを2枚アクティブにする。
・自分のエネルギーデッキから、エネルギーカード1枚を自分のステージにいる『虹ヶ咲』のメンバーの下に置く。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-bp7-005_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-bp7-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0086 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-pb1-002#A02`
- test_case_id: `PL!N-pb1-002#A02#T01`
- cardnumber: `PL!N-pb1-002`
- cardname: `中須かすみ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このメンバーの下にエネルギーカードが2枚以上置かれているかぎり、ライブの合計スコアを+1する。
（メンバーがステージから離れたとき、下に置かれているエネルギーカードはエネルギーデッキに戻す。）
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-pb1-002_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-pb1-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0087 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-pb1-003#A01`
- test_case_id: `PL!N-pb1-003#A01#T01`
- cardnumber: `PL!N-pb1-003`
- cardname: `桜坂しずく`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<(E)>
<(E)>
このカードを手札から控え室に置く：カードを1枚引き、ライブ終了時まで、自分のステージにいる『虹ヶ咲』のメンバー1人は
<(ブレード)>
を得る。この能力は、このカードが手札にある場合のみ起動できる。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-pb1-003_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-pb1-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0088 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-pb1-004#A01`
- test_case_id: `PL!N-pb1-004#A01#T01`
- cardnumber: `PL!N-pb1-004`
- cardname: `朝香果林`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このターンにこのメンバーが移動していない限り、
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-pb1-004_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-pb1-004'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0089 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-pb1-005#A01`
- test_case_id: `PL!N-pb1-005#A01#T01`
- cardnumber: `PL!N-pb1-005`
- cardname: `宮下愛`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン1回>
自分のステージにコスト10のメンバーが登場したとき、カードを1枚引く。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-pb1-005_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-pb1-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0090 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-pb1-007#A01`
- test_case_id: `PL!N-pb1-007#A01#T01`
- cardnumber: `PL!N-pb1-007`
- cardname: `優木せつ菜`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のライブ中のカードの必要ハートの中に
<桃>
、
<赤>
、
<黄>
、
<緑>
、
<青>
、
<紫>
がそれぞれ1以上含まれるかぎり、
<ALL>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-pb1-007_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-pb1-007'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0091 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-pb1-010#A01`
- test_case_id: `PL!N-pb1-010#A01#T01`
- cardnumber: `PL!N-pb1-010`
- cardname: `三船栞子`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<登場>
以下から1つを選ぶ。
・エネルギーを1枚アクティブにする。
・自分の控え室にある『虹ヶ咲』のライブカードを2枚まで好きな順番でデッキの上に置く。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-pb1-010_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-pb1-010'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0092 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!N-pb1-012#A01`
- test_case_id: `PL!N-pb1-012#A01#T01`
- cardnumber: `PL!N-pb1-012`
- cardname: `鐘嵐珠`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン1回>
自分のステージにこのメンバー以外のコスト11のメンバーが登場した時、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_N-pb1-012_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!N-pb1-012'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0093 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-PR-029#A01`
- test_case_id: `PL!S-PR-029#A01#T01`
- cardnumber: `PL!S-PR-029`
- cardname: `渡辺曜`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分か相手のステージにコスト13以上のメンバーがいる場合、
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-PR-029_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-PR-029'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0094 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-PR-030#A01`
- test_case_id: `PL!S-PR-030#A01#T01`
- cardnumber: `PL!S-PR-030`
- cardname: `津島善子`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分か相手のステージにコスト13以上のメンバーがいる場合、
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-PR-030_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-PR-030'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0095 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-PR-031#A01`
- test_case_id: `PL!S-PR-031#A01#T01`
- cardnumber: `PL!S-PR-031`
- cardname: `国木田花丸`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分か相手のステージにコスト13以上のメンバーがいる場合、
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-PR-031_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-PR-031'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0096 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-PR-039#A01`
- test_case_id: `PL!S-PR-039#A01#T01`
- cardnumber: `PL!S-PR-039`
- cardname: `渡辺曜`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分と相手の成功ライブカード置き場にカードが合計4枚以上あるかぎり、
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-PR-039_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-PR-039'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0097 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-PR-042#A01`
- test_case_id: `PL!S-PR-042#A01#T01`
- cardnumber: `PL!S-PR-042`
- cardname: `小原鞠莉`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分と相手のステージにメンバーが合計6人いるかぎり、
<赤>
<緑>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-PR-042_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-PR-042'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0098 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp2-001#A01`
- test_case_id: `PL!S-bp2-001#A01#T01`
- cardnumber: `PL!S-bp2-001`
- cardname: `高海千歌`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分の成功ライブカード置き場のカードが0枚で、かつ相手の成功ライブカード置き場にカードが1枚以上ある場合、
<(ブレード)>
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp2-001_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp2-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0099 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp2-024#A01`
- test_case_id: `PL!S-bp2-024#A01#T01`
- cardnumber: `PL!S-bp2-024`
- cardname: `君のこころは輝いてるかい？`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このカードは成功ライブカード置き場に置くことができない。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp2-024_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp2-024'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0100 [S2] PARTIAL: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp3-001#A01`
- test_case_id: `PL!S-bp3-001#A01#T01`
- cardnumber: `PL!S-bp3-001`
- cardname: `高海千歌`
- result_type: `PARTIAL`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<センター>
<ターン1回>
メンバー1人をウェイトにする：ライブ終了時まで、これによってウェイト状態になったメンバーは、「
<常時>
ライブの合計スコアを+1する。」を得る。
(この能力はセンターエリアに登場している場合のみ起動できる。)
```

Expected: Runtime route reachable and testable

Actual: PARTIAL

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp3-001_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: `llocg_ui/engine.py`

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp3-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0101 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp3-006#A01`
- test_case_id: `PL!S-bp3-006#A01#T01`
- cardnumber: `PL!S-bp3-006`
- cardname: `津島善子`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<センター>
<ターン1回>
このメンバーをウェイトにし、手札を1枚控え室に置く：このメンバー以外の『Aqours』のメンバー1人を自分のステージから控え室に置く。そうした場合、自分の控え室から、そのメンバーのコストに2を足した数に等しいコストの『Aqours』のメンバーカードを1枚、そのメンバーがいたエリアに登場させる。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp3-006_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp3-006'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0102 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp3-016#A01`
- test_case_id: `PL!S-bp3-016#A01#T01`
- cardnumber: `PL!S-bp3-016`
- cardname: `国木田花丸`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分の成功ライブカード置き場にあるカード1枚につき、ステージにいるこのメンバーのコストを+1する。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp3-016_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp3-016'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0103 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp3-024#A01`
- test_case_id: `PL!S-bp3-024#A01#T01`
- cardnumber: `PL!S-bp3-024`
- cardname: `Deep Resonance`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ開始時>
自分のステージのセンターエリアにコスト9以上の『Aqours』のメンバーがいる場合、以下から1つを選ぶ。
・ライブ終了時まで、自分のステージにいるメンバー1人は、
<(ブレード)>
<(ブレード)>
を得る。
・相手のステージにいるコスト4以下のメンバ1人をウェイトにする。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp3-024_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp3-024'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0104 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp5-001#A02`
- test_case_id: `PL!S-bp5-001#A02#T01`
- cardnumber: `PL!S-bp5-001`
- cardname: `高海千歌`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
能力を持たないメンバーを自分の手札から登場させるためのコストは1減る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp5-001_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp5-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0105 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp5-004#A01`
- test_case_id: `PL!S-bp5-004#A01#T01`
- cardnumber: `PL!S-bp5-004`
- cardname: `黒澤ダイヤ`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<登場>
以下から1つを選ぶ。
・自分のステージにいるこのメンバー以外の『Aqours』のメンバー1人は、ライブ終了時まで、
<(ブレード)>
を得る。
・自分のステージにいる『Saint Snow』のメンバー1人をポジションチェンジさせる。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp5-004_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp5-004'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0106 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp5-008#A01`
- test_case_id: `PL!S-bp5-008#A01#T01`
- cardnumber: `PL!S-bp5-008`
- cardname: `小原鞠莉`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
相手の余剰ハートが2つ以上あるかぎり、自分のライブの合計スコアを+1する。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp5-008_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp5-008'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0107 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp6-002#A01`
- test_case_id: `PL!S-bp6-002#A01#T01`
- cardnumber: `PL!S-bp6-002`
- cardname: `桜内梨子`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン1回>
『Aqours』のライブカードが自分のライブカード置き場から控え室に置かれたとき、そのライブカードをデッキの一番上か一番下に置いてもよい。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp6-002_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp6-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0108 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp6-003#A01`
- test_case_id: `PL!S-bp6-003#A01#T01`
- cardnumber: `PL!S-bp6-003`
- cardname: `松浦果南`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
<(E)>
<(E)>
,手札を1枚控え室に置く：このメンバー以外の『Aqours』のメンバー1人を自分のステージから控え室に置いてもよい。そうした場合、自分の控え室から、そのメンバーのコストに2を足した数に等しいコストの『Aqours』のメンバーカードを1枚、そのメンバーがいたエリアに登場させる。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp6-003_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp6-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0109 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp6-004#A02`
- test_case_id: `PL!S-bp6-004#A02#T01`
- cardnumber: `PL!S-bp6-004`
- cardname: `黒澤ダイヤ`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ開始時>
能力を持たない『Aqours』のライブカードを1枚選び、デッキの一番上に置いてもよい。そうした場合、ライブ終了時まで、
<赤>
と
<緑>
を得る。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp6-004_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp6-004'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0110 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp6-009#A01`
- test_case_id: `PL!S-bp6-009#A01#T01`
- cardnumber: `PL!S-bp6-009`
- cardname: `黒澤ルビィ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
相手の成功ライブカード置き場にあるカードの枚数が自分より多いかぎり、その差に等しい数の
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp6-009_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp6-009'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0111 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp6-020#A01`
- test_case_id: `PL!S-bp6-020#A01#T01`
- cardnumber: `PL!S-bp6-020`
- cardname: `冒険Type A, B, C!!`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ開始時>
以下から1つを選ぶ。
・このカードは「
<ライブ成功時>
カードを1枚引く。」を得る。
・ライブ終了時まで、このターンにバトンタッチして登場した『Aqours』のメンバー1人は
<赤>
を得る。
・自分の成功ライブカード置き場にカードが2枚以上ある場合、このカードのスコアを+1する。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp6-020_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp6-020'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0112 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp7-003#A02`
- test_case_id: `PL!S-bp7-003#A02#T01`
- cardnumber: `PL!S-bp7-003`
- cardname: `松浦果南`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<登場>
以下から1つを選ぶ。
・ライブ終了時まで、自分のステージにいる元々持つ
<(ブレード)>
の数が3つ以下の『Aqours』のメンバーは、相手の効果によってはウェイトしない。
・このメンバーを『Aqours』か『Saint Snow』のメンバーがいるエリアにポジションチェンジする。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp7-003_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp7-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0113 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp7-005#A03`
- test_case_id: `PL!S-bp7-005#A03#T01`
- cardnumber: `PL!S-bp7-005`
- cardname: `渡辺曜`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<起動>
<センター>
<ターン1回>
手札を2枚控え室に置く：このメンバーと自分のステージにいるほかの『Aqours』のメンバー1人を選ぶ。それらが持つ
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp7-005_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp7-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0114 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp7-005#A04`
- test_case_id: `PL!S-bp7-005#A04#T01`
- cardnumber: `PL!S-bp7-005`
- cardname: `渡辺曜`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<登場>
能力それぞれ1つ発動させる。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp7-005_A04_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp7-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0115 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp7-006#A01`
- test_case_id: `PL!S-bp7-006#A01#T01`
- cardnumber: `PL!S-bp7-006`
- cardname: `津島善子`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ開始時>
自分のデッキの下からカードを3枚控え室に置く。それらがすべて『Aqours』のメンバーカードの場合、ライブ終了時まで、
<緑>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp7-006_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp7-006'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0116 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp7-015#A01`
- test_case_id: `PL!S-bp7-015#A01#T01`
- cardnumber: `PL!S-bp7-015`
- cardname: `津島善子`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のデッキの下からカードを1枚控え室に置く。それがライブカードの場合、ライブ終了時まで、
<赤>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp7-015_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp7-015'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0117 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp7-016#A01`
- test_case_id: `PL!S-bp7-016#A01#T01`
- cardnumber: `PL!S-bp7-016`
- cardname: `国木田花丸`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のステージにメンバーが3人以上いるかぎり、
<赤>
<緑>
<青>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp7-016_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp7-016'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0118 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-bp7-022#A01`
- test_case_id: `PL!S-bp7-022#A01#T01`
- cardnumber: `PL!S-bp7-022`
- cardname: `恋になりたいAQUARIUM`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のエールは、デッキの上から行う代わりにデッキの下から行う。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-bp7-022_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-bp7-022'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0119 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-pb1-006#A01`
- test_case_id: `PL!S-pb1-006#A01#T01`
- cardnumber: `PL!S-pb1-006`
- cardname: `津島善子`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
手札のライブカードを1枚公開する：相手は手札を1枚控え室に置いてもよい。そうしなかった場合、ライブ終了時まで、
<(ブレード)>
<(ブレード)>
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-pb1-006_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-pb1-006'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0120 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-pb1-009#A01`
- test_case_id: `PL!S-pb1-009#A01#T01`
- cardnumber: `PL!S-pb1-009`
- cardname: `黒澤ルビィ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分と相手の成功ライブカード置き場にカードが合計3枚以上ある場合、
<(ブレード)>
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-pb1-009_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-pb1-009'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0121 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-pb1-019#A02`
- test_case_id: `PL!S-pb1-019#A02#T01`
- cardnumber: `PL!S-pb1-019`
- cardname: `元気全開DAY！DAY！DAY！`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ成功時>
能力を無効にする。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-pb1-019_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-pb1-019'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0122 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!S-pb1-019#A03`
- test_case_id: `PL!S-pb1-019#A03#T01`
- cardnumber: `PL!S-pb1-019`
- cardname: `元気全開DAY！DAY！DAY！`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ成功時>
相手は、エネルギーデッキからエネルギーカードを1枚ウェイト状態で置く。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_S-pb1-019_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!S-pb1-019'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0123 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-PR-022#A01`
- test_case_id: `PL!SP-PR-022#A01#T01`
- cardnumber: `PL!SP-PR-022`
- cardname: `若菜四季`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分と相手のステージにメンバーが合計6人いるかぎり、
<赤>
<黄>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-PR-022_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-PR-022'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0124 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-PR-026#A01`
- test_case_id: `PL!SP-PR-026#A01#T01`
- cardnumber: `PL!SP-PR-026`
- cardname: `鬼塚夏美`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ開始時>
<センター>
自分のライブカード置き場にあるライブカードのスコアの合計が8以上の場合、『
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-PR-026_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-PR-026'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0125 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-PR-026#A02`
- test_case_id: `PL!SP-PR-026#A02#T01`
- cardnumber: `PL!SP-PR-026`
- cardname: `鬼塚夏美`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
ライブの合計スコアを+1する。』を得る。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-PR-026_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-PR-026'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0126 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp1-001#A01`
- test_case_id: `PL!SP-bp1-001#A01#T01`
- cardnumber: `PL!SP-bp1-001`
- cardname: `澁谷かのん`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のステージにほかのメンバーがいない場合、自分はライブできない。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp1-001_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp1-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0127 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp1-003#A01`
- test_case_id: `PL!SP-bp1-003#A01#T01`
- cardnumber: `PL!SP-bp1-003`
- cardname: `嵐千砂都`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
手札にあるメンバーカードを好きな枚数公開する：公開したカードのコストの合計が、10、20、30、40、50のいずれかの場合、ライブ終了時まで、「
<常時>
ライブの合計スコアを+1する。」を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp1-003_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp1-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0128 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp1-004#A01`
- test_case_id: `PL!SP-bp1-004#A01#T01`
- cardnumber: `PL!SP-bp1-004`
- cardname: `平安名すみれ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
ステージのセンターエリアにいる場合、
<(ブレード)>
<(ブレード)>
<(ブレード)>
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp1-004_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp1-004'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0129 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp2-001#A02`
- test_case_id: `PL!SP-bp2-001#A02#T01`
- cardnumber: `PL!SP-bp2-001`
- cardname: `澁谷かのん`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ開始時>
能力を、ライブ終了時まで、無効にしてもよい。これにより無効にした場合、自分の控え室から『Liella!』のカードを1枚手札に加える。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp2-001_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp2-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0130 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp2-004#A01`
- test_case_id: `PL!SP-bp2-004#A01#T01`
- cardnumber: `PL!SP-bp2-004`
- cardname: `平安名すみれ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のステージにいるメンバーのうち、センターエリアにいるメンバーが最も大きいコストを持つ場合、
<黄>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp2-004_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp2-004'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0131 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp2-006#A02`
- test_case_id: `PL!SP-bp2-006#A02#T01`
- cardnumber: `PL!SP-bp2-006`
- cardname: `桜小路きな子`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<起動>
<ターン1回>
手札のコスト4以下の『Liella!』のメンバーカードを1枚控え室に置く：これにより控え室に置いたメンバーカードの
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp2-006_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp2-006'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0132 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp2-006#A03`
- test_case_id: `PL!SP-bp2-006#A03#T01`
- cardnumber: `PL!SP-bp2-006`
- cardname: `桜小路きな子`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<登場>
能力1つを発動させる。
（
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp2-006_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp2-006'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0133 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp2-006#A04`
- test_case_id: `PL!SP-bp2-006#A04#T01`
- cardnumber: `PL!SP-bp2-006`
- cardname: `桜小路きな子`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<登場>
能力がコストを持つ場合、支払って発動させる。）
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp2-006_A04_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp2-006'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0134 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp2-008#A01`
- test_case_id: `PL!SP-bp2-008#A01#T01`
- cardnumber: `PL!SP-bp2-008`
- cardname: `若菜四季`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
<(E)>
：このメンバーがいるエリアとは別の自分のエリア1つを選ぶ。このメンバーをそのエリアに移動する。選んだエリアにメンバーがいる場合、そのメンバーは、このメンバーがいたエリアに移動させる。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp2-008_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp2-008'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0135 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp2-010#A01`
- test_case_id: `PL!SP-bp2-010#A01#T01`
- cardnumber: `PL!SP-bp2-010`
- cardname: `ウィーン・マルガレーテ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
相手のライブカード置き場にあるすべてのライブカードは、成功させるための必要ハートが
<任意>
多くなる。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp2-010_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp2-010'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0136 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp4-003#A02`
- test_case_id: `PL!SP-bp4-003#A02#T01`
- cardnumber: `PL!SP-bp4-003`
- cardname: `嵐千砂都`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
<センター>
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp4-003_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp4-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0137 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp4-004#A01`
- test_case_id: `PL!SP-bp4-004#A01#T01`
- cardnumber: `PL!SP-bp4-004`
- cardname: `平安名すみれ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このカードのプレイに際し、2人のメンバーとバトンタッチしてもよい。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp4-004_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp4-004'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0138 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp4-009#A01`
- test_case_id: `PL!SP-bp4-009#A01#T01`
- cardnumber: `PL!SP-bp4-009`
- cardname: `鬼塚夏美`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のステージにいるメンバーのコストが相手より低いかぎり、
<(ブレード)>
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp4-009_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp4-009'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0139 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp4-016#A01`
- test_case_id: `PL!SP-bp4-016#A01#T01`
- cardnumber: `PL!SP-bp4-016`
- cardname: `葉月恋`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
カードの効果で自分のエネルギー置き場にエネルギーカードが置かれるたび、ライブ終了時まで、
<紫>
を得る。
（相手のカードの効果でも発動する。）
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp4-016_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp4-016'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0140 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp4-021#A01`
- test_case_id: `PL!SP-bp4-021#A01#T01`
- cardnumber: `PL!SP-bp4-021`
- cardname: `ウィーン・マルガレーテ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のエネルギーが相手より多いかぎり、
<紫>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp4-021_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp4-021'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0141 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp5-001#A01`
- test_case_id: `PL!SP-bp5-001#A01#T01`
- cardnumber: `PL!SP-bp5-001`
- cardname: `澁谷かのん`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<登場>
/
<ライブ開始時>
<(E)>
支払ってもよい：以下から1つを選ぶ。
・相手のステージにいるコスト4以下のメンバー1人をウェイトにする。
・カードを1枚引く。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp5-001_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp5-001'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0142 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp5-003#A01`
- test_case_id: `PL!SP-bp5-003#A01#T01`
- cardnumber: `PL!SP-bp5-003`
- cardname: `嵐千砂都`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
コスト10の『Liella!』のメンバーカードを自分の手札から登場させるためのコストは2減る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp5-003_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp5-003'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0143 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp5-005#A01`
- test_case_id: `PL!SP-bp5-005#A01#T01`
- cardnumber: `PL!SP-bp5-005`
- cardname: `葉月恋`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
<ターン1回>
デッキの上からカードを3枚控え室に置く：ライブ終了時まで、これにより控え室に置いた『Liella!』のメンバーカード1枚につき、
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp5-005_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp5-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0144 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp5-005#A02`
- test_case_id: `PL!SP-bp5-005#A02#T01`
- cardnumber: `PL!SP-bp5-005`
- cardname: `葉月恋`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン1回>
自分のメインフェイズの際、自分のカードが1枚以上いずれかの領域から控え室に置かれるたび、
<(E)>
支払ってもよい。そうした場合、それらのカードの中から1枚手札に加える。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp5-005_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp5-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0145 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp5-011#A01`
- test_case_id: `PL!SP-bp5-011#A01#T01`
- cardnumber: `PL!SP-bp5-011`
- cardname: `鬼塚冬毬`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
<左サイド>
<赤>
<赤>
<赤>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp5-011_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp5-011'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0146 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp5-011#A02`
- test_case_id: `PL!SP-bp5-011#A02#T01`
- cardnumber: `PL!SP-bp5-011`
- cardname: `鬼塚冬毬`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
<センター>
<黄>
<黄>
<黄>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp5-011_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp5-011'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0147 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp5-011#A03`
- test_case_id: `PL!SP-bp5-011#A03#T01`
- cardnumber: `PL!SP-bp5-011`
- cardname: `鬼塚冬毬`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
<右サイド>
<青>
<青>
<青>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp5-011_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp5-011'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0148 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp5-012#A01`
- test_case_id: `PL!SP-bp5-012#A01#T01`
- cardnumber: `PL!SP-bp5-012`
- cardname: `澁谷かのん`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のライブカード置き場に必要ハートの合計が8以上の『Liella!』のライブカードがあるかぎり、
<黄>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp5-012_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp5-012'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0149 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp7-005#A01`
- test_case_id: `PL!SP-bp7-005#A01#T01`
- cardnumber: `PL!SP-bp7-005`
- cardname: `葉月恋`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン1回>
このメンバーが登場するか、自分のエネルギーがエネルギー置き場からエネロキーデッキに置かれたとき、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。そのエネルギーカードは、次のターンのアクティブフェイズにアクティブしない。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp7-005_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp7-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0150 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp7-005#A02`
- test_case_id: `PL!SP-bp7-005#A02#T01`
- cardnumber: `PL!SP-bp7-005`
- cardname: `葉月恋`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン2回>
自分のカードの効果によって、自分のエネルギー置き場にエネルギーが置かれたとき、ライブ終了時まで、
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp7-005_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp7-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0151 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-bp7-025#A01`
- test_case_id: `PL!SP-bp7-025#A01#T01`
- cardnumber: `PL!SP-bp7-025`
- cardname: `Memories`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ開始時>
ライブ終了時まで、自分のステージにいる「嵐千砂都」1人は
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-bp7-025_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-bp7-025'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0152 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-000#A01`
- test_case_id: `PL!SP-pb2-000#A01#T01`
- cardnumber: `PL!SP-pb2-000`
- cardname: `嵐千砂都＆鬼塚夏美`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このカードのプレイに際し、2人のメンバーとバトンタッチしてもよい。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-000_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-000'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0153 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-002#A01`
- test_case_id: `PL!SP-pb2-002#A01#T01`
- cardnumber: `PL!SP-pb2-002`
- cardname: `唐可可`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<起動>
<ターン1回>
手札の『Liella!』のカードを1枚控え室に置く：以下から1つを選ぶ。これにより控え室に置いたカードがブレードハートを持たないメンバーカードの場合、代わりに1つ以上を選ぶ。
・自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。
・ライブ終了時まで、自分のステージにいるこのメンバー以外の『Liella!』のメンバー1人は、
<紫>
<紫>
を得る。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-002_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-002'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0154 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-005#A02`
- test_case_id: `PL!SP-pb2-005#A02#T01`
- cardnumber: `PL!SP-pb2-005`
- cardname: `葉月恋`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このメンバーは、このメンバーの下に置かれている『Liella!』のメンバーカードが持つ
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-005_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0155 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-005#A03`
- test_case_id: `PL!SP-pb2-005#A03#T01`
- cardnumber: `PL!SP-pb2-005`
- cardname: `葉月恋`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<起動>
能力をすべて得る。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-005_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-005'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0156 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-006#A01`
- test_case_id: `PL!SP-pb2-006#A01#T01`
- cardnumber: `PL!SP-pb2-006`
- cardname: `桜小路きな子`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
このメンバーの下にある『Liella!』のメンバーカード1枚につき、このメンバーのコストを+1する。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-006_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-006'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0157 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-006#A02`
- test_case_id: `PL!SP-pb2-006#A02#T01`
- cardnumber: `PL!SP-pb2-006`
- cardname: `桜小路きな子`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン1回>
自分のライブが成功するか、このメンバーがエリアを移動したとき、自分の控室にある『Liella!』のメンバーカードを1枚、このメンバーの下に置く。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-006_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-006'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0158 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-010#A02`
- test_case_id: `PL!SP-pb2-010#A02#T01`
- cardnumber: `PL!SP-pb2-010`
- cardname: `ウィーン・マルガレーテ`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ成功時>
以下から1つ選ぶ。
・カードを2枚引く。
・自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-010_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-010'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0159 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-011#A01`
- test_case_id: `PL!SP-pb2-011#A01#T01`
- cardnumber: `PL!SP-pb2-011`
- cardname: `鬼塚冬毬`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<自動>
<ターン1回>
自分のステージのセンターエリアにいるメンバーがエリアを移動したとき、以下から1つを得る。
・ライブ終了時まで、
<(ブレード)>
<(ブレード)>
を得る。
・相手のステージにいる元々持つ
<(ブレード)>
の数が2つ以下のメンバー1人をウェイトにする。
・カードを1枚引く。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-011_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-011'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0160 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-022#A01`
- test_case_id: `PL!SP-pb2-022#A01#T01`
- cardnumber: `PL!SP-pb2-022`
- cardname: `鬼塚冬毬`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<自動>
<ターン1回>
自分のステージにいる『5yncri5e!』のメンバーがセンターエリアに移動したとき、ライブ終了時まで、
<(ブレード)>
<(ブレード)>
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-022_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-022'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0161 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-035#A01`
- test_case_id: `PL!SP-pb2-035#A01#T01`
- cardnumber: `PL!SP-pb2-035`
- cardname: `唐可可`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
<左サイド>
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-035_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-035'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0162 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-041#A01`
- test_case_id: `PL!SP-pb2-041#A01#T01`
- cardnumber: `PL!SP-pb2-041`
- cardname: `若菜四季`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
<右サイド>
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-041_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-041'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0163 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-046#A01`
- test_case_id: `PL!SP-pb2-046#A01#T01`
- cardnumber: `PL!SP-pb2-046`
- cardname: `Butterfly Wing`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
自分のステージにいるメンバーが持つ
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-046_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-046'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0164 [S1] DB_DATA_MISMATCH: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-046#A02`
- test_case_id: `PL!SP-pb2-046#A02#T01`
- cardnumber: `PL!SP-pb2-046`
- cardname: `Butterfly Wing`
- result_type: `DB_DATA_MISMATCH`
- human_rule_confirmation_required: `YES`

Effect text:

```text
<ライブ開始時>
能力は発動しない。
```

Expected: Runtime route reachable and testable

Actual: DB_DATA_MISMATCH

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-046_A02_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-046'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0165 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-046#A03`
- test_case_id: `PL!SP-pb2-046#A03#T01`
- cardnumber: `PL!SP-pb2-046`
- cardname: `Butterfly Wing`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ成功時>
自分のステージに
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-046_A03_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-046'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0166 [S3] UNREACHABLE: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-pb2-046#A04`
- test_case_id: `PL!SP-pb2-046#A04#T01`
- cardnumber: `PL!SP-pb2-046`
- cardname: `Butterfly Wing`
- result_type: `UNREACHABLE`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<ライブ開始時>
を持つメンバーがいる場合、このカードのスコアを+1する。
```

Expected: Runtime route reachable and testable

Actual: UNREACHABLE

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-pb2-046_A04_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-pb2-046'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```

## ISS-0167 [S2] NOT_IMPLEMENTED: implementation mapping incomplete or data mismatch
- audit_id: `PL!SP-sd2-004#A01`
- test_case_id: `PL!SP-sd2-004#A01#T01`
- cardnumber: `PL!SP-sd2-004`
- cardname: `平安名すみれ`
- result_type: `NOT_IMPLEMENTED`
- human_rule_confirmation_required: `NO`

Effect text:

```text
<常時>
<センター>
<(ブレード)>
<(ブレード)>
<(ブレード)>
<(ブレード)>
を得る。
```

Expected: Runtime route reachable and testable

Actual: NOT_IMPLEMENTED

Reproduction steps: Run the debug command from a clean shell; use the target card/effect described by audit_id; observe route/status in logs and UI. For non-implemented/static findings, command is a starting reproduction harness and may require refining setup candidates.

Log: `logs/PL_SP-sd2-004_A01_T01.log`

State diff: Not executed to PASS criteria in this static audit. State diff must be captured during follow-up runtime/UI execution.

Screenshot/path: `screenshots/ (not captured in static audit)`

Related code: ``

Suspected cause: Generic matcher/resolver missing, unreachable compiled ability, or audit/runtime DB mismatch depending on result_type.

Fix direction: Investigate generic matcher/resolver or DB correction; do not apply during audit.

Affected scope: Potentially all cards sharing the same effect text family; inspect implementation_mapping.csv matcher_or_rule for neighboring patterns.

Debug command:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!SP-sd2-004'
export LLOCG_START_STAGE_R='PL!HS-PR-001'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py

```
