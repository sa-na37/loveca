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

#### PL!SP-bp2-008#A01 起動: E支払い → 別エリア移動/入れ替え

※20260720内部確認: `PL!SP-bp2-008#A01` を確認。カード番号専用分岐ではなく、`このメンバーがいるエリアとは別の自分のエリア1つを選ぶ。このメンバーをそのエリアに移動する。選んだエリアにメンバーがいる場合、そのメンバーは、このメンバーがいたエリアに移動させる。` の明文化されたポジションチェンジ文型を既存 `position_change_self` resolver へ接続。engine API と HTTP API で、`<(E)>` 支払い、移動先 `L/R` pending、発生源 `PL!SP-bp2-008` 表示、`L` 選択時のC/L入れ替え、pending 残留なしを確認。

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
export LLOCG_START_STAGE_C='PL!SP-bp2-008'
export LLOCG_START_STAGE_L='PL!N-bp3-009'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_ENERGY_ACTIVE=2
export LLOCG_START_ENERGY_WAIT=0
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: `C` の起動効果を使う。`<(E)>` コストで `energy_active 2 -> 1`、`energy_wait 0 -> 1` になる。後続 pending は `position_change` で、選択肢は元エリアC以外の `L/R`。`L` を選ぶと `PL!SP-bp2-008` が `C -> L`、元Lの `PL!N-bp3-009` が `L -> C` へ入れ替わり、pending は空になる。

### 2026-07-20 パブリックウィンドウ UI / 非公開領域 redaction smoke

※20260720内部確認: パブリックウィンドウの表示経路を確認。公開 view state は手札・山札のカード番号を渡さず `hand_count` / `deck_count` のみを残す。ライブカード置き場は `LIVE_CONFIRM` かつ `live_start_prompted=false` の間だけ `__BACK__` に置換し、`LIVE_PERF` 以降は実カード番号を公開する。pending 内の非公開カード番号は `__BACK__` または `非公開カード` に置換する。UI 側では公開手札、山札、裏向きライブカード、非公開 pending カードのすべてが `/img?cn=__BACK__` 経由で `back.png` を表示する。古い CSS マスク `publicMaskCard` は未使用かつ back.png ではないため削除済み。公開/メイン画面の差分は、公開ビューの読み取り専用表示と非公開領域のカード redaction に限定する方針で確認。

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m unittest llocg_ui.tests.test_public_view
python3 -m py_compile ./llocg_ui/server.py ./llocg_ui/views.py ./llocg_ui/engine.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py ./llocg_dual_v2/*.py ./run_llocg_ui_web.py ./run_llocg_dual_v2.py
python3 -m unittest llocg_ui.tests.test_public_view llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

確認観点: `test_public_view` で、公開 view state が `hand=[]` / `deck=[]` と枚数のみを返すこと、ステージ・控え室・解決領域・成功ライブ置き場は表のまま残ること、ライブセット直後は `set_zone=["__BACK__", ...]` になり `LIVE_PERF` 以降は表になること、非公開 pending 候補が `__BACK__` に置換されること、公開されたまま手札に移動したカードだけが `public_hand_revealed_cards` として保持されることを確認する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 18182 --debug
curl -s 'http://127.0.0.1:18182/state?view=public'
curl -s -D - 'http://127.0.0.1:18182/img?cn=__BACK__' -o /private/tmp/loveca_back_from_server.png
cmp -s /private/tmp/loveca_back_from_server.png ./llocg_db_out_full/card_images/back.png; printf 'back_png_match=%s\n' "$?"
```

確認観点: `/state?view=public` が `view_mode=public`、`hand=[]`、`deck=[]`、`hand_count`、`deck_count` を返す。`/img?cn=__BACK__` は `llocg_db_out_full/card_images/back.png` と完全一致する。2デッキ側は同じ `make_view_state` と scoped HTML を通るため、`/p1/img?cn=__BACK__` でも同一画像を確認する。

#### 非公開領域扱いで裏面表示される想定状況

※20260720内部確認: 非公開領域扱いで `__BACK__` / `back.png` になる想定状況を列挙し、`llocg_ui.tests.test_public_view` に回帰テストを追加した。

- 山札: public state は `deck=[]` と `deck_count` のみを返す。UI は山札ゾーンに `renderTopCard(..., '__BACK__', ...)` を使う。
- 通常手札: public state は `hand=[]` と `hand_count` のみを返す。UI は `renderMaskedHand` で未知枚数分を `__BACK__` にする。
- ライブカード置き場の裏向き期間: `LIVE_CONFIRM` かつ `live_start_prompted=false` の間は `set_zone` を `__BACK__` に置換し、`set_zone_score_rows` も伏せる。`LIVE_CONFIRM` でも `live_start_prompted=true`、および `LIVE_PERF` / `LIVE_ATTEMPT` / `LIVE_RESOLVE` は表向き扱い。
- 非公開領域を見る/選ぶ pending: `choose_from_topk`、手札コスト/手札選択、山札上操作など、手札・山札由来のカード番号は値・リスト・dict key のいずれでも `__BACK__` または `非公開カード` に置換する。
- 公開例外: `show_revealed_cards_ack`、`public_reveal_events`、refresh notice の returned LIVE、公開されたまま手札へ移動したカードは裏面にせず、公開カードとしてカード番号と表示用メタデータを残す。

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m unittest llocg_ui.tests.test_public_view
```

確認結果: 9 tests OK。山札、通常手札、ライブセット裏向き期間、非公開 pending、公開例外、HTML 内の古い CSS マスク削除と `__BACK__` 描画経路を確認済み。
