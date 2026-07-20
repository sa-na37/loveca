# Loveca debug commands current updates 20260623

目的: 実装中に追加した新規デバッグコマンドを、ユーザー編集用の統合メモと衝突させず一時保持する。

運用:

- 統合・ユーザー編集・デバッグ内容監修用: `docs/debug/loveca_debug_commands_20260623.md`
- 現行更新分の追記先: `docs/debug/loveca_debug_commands_current_updates_20260623.md`
- ユーザーから統合指示が出るまで、現行更新分はこのファイルに残す。
- 統合時はこのファイルの該当ブロックを統合メモへ移し、移動済みのブロックをこのファイルから削除する。

## Pending current updates

※ 20260715 統合済み: 未統合の current updates は `docs/debug/loveca_debug_commands_20260623.md` の `Integrated current updates 20260715` へ移動済み。
※ 次回以降の実装・デバッグ確認分は、この見出しの下へ新規追記する。

### 20260717 Phase 4 confirmed backlog implementation

※20260717内部確認: `CODEX_INSTRUCTION_loveca_phase4_confirmed_backlog_implementation_20260717.md` 対応。対象は `PL!HS-bp6-014#A01` と `PL!SP-bp1-003#A01` の2能力のみ。runtime 14件 PASS、実ブラウザで手札起動ボタン、発生源つき pending、公開カード MEMBER-only 候補、0枚送信、合計10送信、public reveal 表示を確認。証跡は `_codex_outputs/loveca_phase4_confirmed_backlog_implementation_20260717`。

#### PL!HS-bp6-014#A01 手札起動: 自身を控え室、1ドロー、藤島慈へブレード

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-bp6-014'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_STAGE_C='PL!HS-bp2-015'
export LLOCG_START_DECK_TOP='PL!HS-bp2-016,PL!HS-bp2-017'
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: 手札カードに `能力` ボタンが出る。押下後、発生源 `PL!HS-bp6-014` と実行中効果だけを表示した対象選択 pending になる。`C` を選ぶと `PL!HS-bp6-014` が控え室へ移動し、1ドロー後、対象メンバーへ `temp_blade=1` が付く。

#### PL!SP-bp1-003#A01 手札メンバー公開コスト合計: 0枚/10達成

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!SP-bp1-003'
export LLOCG_START_HAND='PL!N-bp3-009,PL!N-bp3-009,PL!N-bp1-029'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_DECK_TOP='PL!N-bp4-030,PL!N-bp3-032'
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: `起動` 押下後、公開候補は MEMBER の `PL!N-bp3-009` 2枚だけで、LIVE の `PL!N-bp1-029` は候補にならない。0枚送信は条件未達で解決し、手札は減らない。1枚選択時は自動更新後も選択が維持され、`公開して解決 (1枚 / 合計10)` で条件達成、発生源の `temp_score=1`、public reveal で公開カード確認ができる。

### 20260720 Tier 3 pilot blocked routes follow-up

※20260720内部確認: `PL!N-bp4-008#A01` と `PL!SP-bp7-025#A01` の未到達/未実装経路を再確認。カード番号専用分岐ではなく、`エネルギーN枚か『group』のメンバー1人をアクティブ` と `ライブ開始時: 名前指定ステージメンバーへ一時ブレード付与` の汎用 route を `llocg_ui/engine.py` に追加。隣接する既存文型 `自分のステージにいるメンバー1人か、エネルギーN枚をアクティブ` も、Skip後手動確認ではなく同じ実解決 pending に寄せた。engine API で、起動効果の `energy` 入力と `L` 入力、ライブカード実セット後の auto_order 到達、対象 `L` 入力、pending 残留なしを確認済み。

#### PL!N-bp4-008#A01 起動: エネルギー1枚か虹ヶ咲メンバー1人をアクティブ

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!N-bp4-008'
export LLOCG_START_STAGE_L='PL!N-bp3-009'
export LLOCG_START_HAND='PL!N-bp4-009'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_ENERGY_ACTIVE=3
export LLOCG_START_ENERGY_WAIT=1
export LLOCG_START_DECK_TOP='PL!N-bp4-030,PL!N-bp3-032'
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: `C` の起動効果を押し、手札1枚をコストで控え室へ置く。後続 pending は発生源 `PL!N-bp4-008` つきで、選択肢 `energy` と `L` を出す。`energy` を選ぶと `energy_wait 1 -> 0 / energy_active 3 -> 4`。再起動して `L` を選ぶと `L` の虹ヶ咲メンバーが ACTIVE になり、エネルギー枚数は変わらない。いずれも pending 残留なし。

#### PL!SP-bp7-025#A01 ライブ開始時: 嵐千砂都1人にブレード

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=LIVE_SET
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!SP-bp4-003'
export LLOCG_START_HAND='PL!SP-bp7-025'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_DECK_TOP='PL!N-bp3-009,PL!N-bp4-009'
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: `PL!SP-bp7-025` を手札からライブカード置き場へセットし、ライブ開始時解決へ進む。auto_order に `PL!SP-bp7-025 ライブ開始時` が発生し、解決後に対象 `L` を選ぶとステージの `嵐千砂都` がライブ終了時まで `temp_blade=1` を得る。以前のように LIVE カードをステージへ置く初期状態ではなく、正式なライブセット手順で確認する。

### 20260720 Tier 3 P1 activated green-to-hand follow-up

※20260720内部確認: `PL!N-bp1-008#A01` を確認。カード番号専用分岐ではなく、`手札のメンバーカードをN枚控え室に置く` コスト候補の MEMBER 限定と、`これにより控え室に置いたメンバーカードよりコストの低いメンバーカードをN枚手札に加える` の汎用 route を `llocg_ui/engine.py` に追加。engine API と HTTP API で、起動可否 true、コスト候補から LIVE 除外、discarded context のコスト10参照、控え室候補のコスト10未満 MEMBER 限定、回収後 pending 残留なしを確認。手札に MEMBER がない場合は `can_activate=false` も確認。

#### PL!N-bp1-008#A01 起動: 手札 MEMBER discard → 低コスト MEMBER 回収

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!N-bp1-008'
export LLOCG_START_HAND='PL!N-bp3-009,PL!N-bp1-029'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_GREEN='PL!N-pb1-005,PL!N-bp1-012,PL!N-bp1-029'
export LLOCG_START_DECK_TOP='PL!N-bp4-030,PL!N-bp3-032'
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: `C` の起動効果が表示される。起動後のコスト選択は手札の MEMBER のみで、LIVE `PL!N-bp1-029` は候補に出ない。`PL!N-bp3-009`（コスト10）を控え室に置くと、回収候補はコスト10未満の MEMBER `PL!N-pb1-005` のみになり、LIVE とコスト10以上 MEMBER は候補外。選択後、`PL!N-pb1-005` が手札へ移動し、pending は残らない。

#### PL!N-bp5-003#A01 起動: 控え室 LIVE 選択 → スコア分エネルギー任意支払い → 回収

※20260720内部確認: `PL!N-bp5-003#A01` を確認。カード番号専用分岐ではなく、`控え室のライブカードをN枚選び、そのカードのスコアに等しい数のエネルギーを支払ってもよい。そうした場合、そのライブカードを手札に加える` の汎用 route を追加。engine API で pay / skip / エネルギー不足を確認し、HTTP API で代表 pay 経路を確認。控え室 LIVE のみ候補、pay pending に対象カード番号・スコア・発生源が出ること、pay 後に `energy_active 5 -> 0 / energy_wait 0 -> 5`、対象 LIVE が手札へ移動、pending 残留なしを確認。

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!N-bp5-003'
export LLOCG_START_HAND='PL!N-bp3-009'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_GREEN='PL!N-bp1-029,PL!N-bp3-032,PL!N-bp3-009'
export LLOCG_START_ENERGY_ACTIVE=5
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_START_DECK_TOP='PL!N-bp4-030,PL!N-bp3-032'
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: `C` の起動効果を使い、手札1枚を控え室へ置く。後続 pending は控え室 LIVE `PL!N-bp1-029` / `PL!N-bp3-032` のみを候補にする。`PL!N-bp1-029` を選ぶと、スコア5に基づく pay/skip pending が出る。`pay` でエネルギー5枚を支払い、`PL!N-bp1-029` が手札へ移動する。`skip` ではエネルギーと控え室 LIVE は変化しない。エネルギー不足時に `pay` を選ぶと pending は残り、エラーログを出す。

#### PL!N-bp7-004#A01 起動: エネルギー下置き → 下エネルギー枚数+1以下ブレード相手ウェイト

※20260720内部確認: `PL!N-bp7-004#A01` を確認。カード番号専用分岐ではなく、`このメンバーの下にあるエネルギーカードの枚数にNを足した数以下` の動的しきい値を持つ相手ウェイト汎用 route を追加。相手個別カード state は現行正式仕様では保持しないため、既存の `opponent_wait_notify` 人数入力方式へ接続した。engine API で起動コスト支払い後の `energy_under=1` を解決時に参照し、しきい値2の pending を生成すること、人数1入力で `opponent_wait_count=1`、pending 残留なしを確認。エネルギー不足時はコスト支払い前に止まり、pending を生成しないことも確認。HTTP API でも同経路を確認済み。

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!N-bp7-004'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_ENERGY_ACTIVE=3
export LLOCG_START_ENERGY_WAIT=0
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: `C` の起動効果を使う。コストでエネルギー1枚がこのメンバーの下に置かれ、`energy_active 3 -> 2`、`C.energy_under 0 -> 1` になる。その後、下エネルギー1枚+1により「元々持つ<(ブレード)>の数が2つ以下のメンバー1人をウェイトにする」人数入力 pending が発生する。選択肢は `0/1`、発生源は `PL!N-bp7-004`。`1` を入力すると `opponent_wait_count 0 -> 1`、pending は空になる。相手個別カード選択が出ないことは現行仕様通り。
