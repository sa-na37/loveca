# Loveca implementation debug checklist 20260623

目的: 20260622h から 20260623i までに追加した実装の確認観点とコマンドを一箇所に集約する。

＊ユーザコメントとcodexコメントを区別しやすくするため、追加コメントについては別の記号を使うように
＊ユーザ/codexコメントツリーは該当デバッグが完全に完了するまで削除しない

## Common commands

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

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
# 必要な LLOCG_* を設定
python3 ./run_llocg_ui_web.py
```

Open:

```text
http://127.0.0.1:8787/
```

## Individual UI launch commands

Each block is self-contained and follows the `AGENTS.md` debug command format.
Stop the previous server before starting the next one if port `8787` is already in use.

## Debug comment handling rule

- `＊挙動問題なし` / `＊挙動確認済み`: active command から外し、Resolved debug confirmations へ移動する。
- `＊挙動問題あり`: 指摘内容を確認して修正し、修正内容コメントを追記する。必要なら起動コマンドも更新する。
- `＊` の次行にタブ付きコメント: 個別カードだけでなく同型 UI に広く効くよう一般化して実装し、修正内容コメントを追記する。
- Codex 側の追記コメントは `※` で始め、ユーザーコメントの `＊` と区別する。
- ユーザー/Codex コメントツリーは、該当デバッグが完全に完了するまで削除しない。

## Resolved debug confirmations

- `PL!-bp5-222` / `PL!HS-cl1-007` top 3 choose 1
  - 2026-06-23: 挙動確認済み。
  - 修正反映: 自己ウェイト＋手札コスト判定の一般化を確認済み。
- `PL!HS-bp5-008` cost 9+ Hasunosora member filter
  - 2026-06-23: 挙動確認済み。
  - 修正反映: 自己ウェイト＋手札コスト判定の一般化を確認済み。
- `PL!-sd1-007` mill top 5 then draw if live
  - 2026-06-23: 挙動確認済み。
  - 修正反映: 自動効果確認ポップアップ表示を確認済み。
- `PL!HS-bp1-008` mill top 3 then draw if all members
  - 2026-06-23: 挙動問題なし。
- `PL!HS-PR-019` / `PL!HS-PR-021` / `PL!HS-sd1-013` color-heart member condition
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 自動効果確認の条件文を日本語化し、ハート/ブレード表記を texticon 表示へ一般化。
- `PL!-bp5-010` mill top 3 then retrieve A-RISE member
  - 2026-06-23: 挙動問題なし。
- `PL!N-bp1-009` mill top 2 then retrieve member
  - 2026-06-23: 挙動問題なし。
- `PL!-pb1-006` topdeck μ's live then opponent-wait draw check
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 控え室からデッキ上に置く pending に発生源と効果内容を表示。
- `PL!-pb1-016` optional discard then lily white top 4 search
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 任意手札コストの表示で、条件と効果の重複表示を削減。
- `LL-bp6-001` top 6 choose 2 to hand
  - 2026-06-23: 挙動確認済み。
  - 2026-06-23 修正反映: top-k 複数枚選択は、カードを順番に即解決する方式ではなく、選択枠を付けて必要枚数を選び、確定ボタンでまとめて解決する UI に一般化。
- `PL!HS-cl1-004` simple mill top 3
  - 2026-06-23: 挙動問題なし。
  - 2026-06-23 修正反映: 登場時などの複数効果モード選択は、ポップアップ上部の効果説明の直下に `①効果1` / `②効果2` の枠付き選択肢として表示する UI に一般化。
- `PL!-sd1-019` top 3 keep any reorder
  - 2026-06-23: 挙動問題なし。
- `PL!HS-cl1-001` top1 optional mill
  - 2026-06-23: 挙動問題なし。
- `PL!HS-bp5-001` / `PL!HS-bp5-013` / `PL!HS-bp6-009` conditional blade gain
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 登場時効果を検証できるよう、対象カードを初期ステージから外したデバッグコマンドで確認済み。
- `PL!N-bp1-011` reveal until live
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 公開結果の移動先表示を追加し、カード番号ではなくカード名優先で表示するよう一般化。
- `PL!SP-bp5-013` Sunny Passion or blade-heart Liella member top 5
  - 2026-06-23: 挙動問題なし。
- `PL!N-bp4-021` waiting room any card to deck top
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 控え室からデッキ上へ置く pending に発生源と効果内容を表示。
- `PL!HS-pb1-004` mill top 3 then retrieve Cerise Bouquet live
  - 2026-06-23: 挙動問題なし。
  - 修正反映: エネルギー不足を避けるコマンドに変更し、控え室検索が group だけでなく unit も見るよう修正。
- `PL!HS-pb1-027` optional mill if Cerise Bouquet member exists
  - 2026-06-23: 挙動問題なし。
  - 修正反映: ライブ成功時効果を検証できるよう、対象 LIVE とステージ条件を固定したコマンドに修正。
- `PL!-bp6-016` top 3 reorder all
  - 2026-06-23: 挙動問題なし。
  - 修正反映: ステージ上の効果元と成功用 LIVE を分離したコマンドに修正。並べ替え UI は、カード上にドロップした時の挿入位置を移動方向に応じて対象カードの前後へ分けるよう一般化。
  - 保留: ウインドウリサイズ時の全体レイアウト追従は広範囲の UI 改修になるため別作業。
- `PL!S-bp6-005` all red/green/blue member top 2
  - 2026-06-23: 挙動問題なし。
- `PL!S-bp2-005` red/green/blue heart member top 7 up to 3
  - 2026-06-23: 挙動問題なし。
- `PL!-bp6-002` no-ability or always μ's top 2
  - 2026-06-25: 挙動問題なし。
  - 修正反映: <常時>能力判定を `ability_type` の `常時` のみに限定し、起動能力のみの μ's カードを候補外にした。
  - 補足: ユーザーコメントにより、起動能力持ちの除外はコマンド上では未確認だった旨を履歴として残す。


## Active debug commands integrated 20260625c

### 20260623l distinct group top-k up to 3

#### `PL!SP-bp5-007` top 5 choose up to 3 by distinct group

起動後: `PL!SP-bp5-007` を登場させ、任意手札コストを払う。上5枚のうち、各グループ名につき1枚ずつ、3枚まで選んで手札に加えられることを見る。同じ `Liella!` グループの候補は同時に選べないことも確認する。

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
export LLOCG_DEBUG_EFFECT_CARD=PL!SP-bp5-007
export LLOCG_START_HAND='PL!SP-bp5-007,PL!HS-PR-001'
export LLOCG_START_ENERGY_ACTIVE=99
export LLOCG_START_DECK_TOP='PL!SP-bp5-008,PL!HS-PR-001,PL!N-PR-003,PL!-bp3-015,PL!SP-bp5-009,PL!HS-PR-020'
python3 ./run_llocg_ui_web.py
```

※実装済み：`look_top_k_optional_distinct_group_upto_n` を追加。top-k 複数選択 pending に `unique_by_group` を持たせ、同じグループ名の重複選択を UI と解決時の両方で防ぐ。
※再確認待ち：上5枚のうち異なるグループを最大3枚まで選べ、`Liella!` 候補2枚を同時選択できないこと。

### 20260624a cost-le group member top-k stage-or-hand

#### `PL!SP-pb2-001` top 5 cost <=4 Liella member to empty stage or hand

起動後: `PL!SP-pb2-001` を登場させ、任意手札コストを払う。上5枚のうちコスト4以下の `Liella!` メンバーカードだけが候補になり、選んだカードを空きステージに登場させるか手札に加えられることを見る。

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
export LLOCG_DEBUG_EFFECT_CARD=PL!SP-pb2-001
export LLOCG_START_HAND='PL!SP-pb2-001,PL!HS-PR-001'
export LLOCG_START_ENERGY_ACTIVE=99
export LLOCG_START_STAGE='C=PL!HS-PR-001'
export LLOCG_START_DECK_TOP='PL!SP-bp1-012,PL!SP-bp2-007,PL!HS-PR-001,PL!SP-bp5-008,PL!HS-PR-020'
python3 ./run_llocg_ui_web.py
```

※実装済み：`look_top_k_optional_cost_le_group_member_stage_or_hand` を追加。選択後に `topk_stage_or_hand` pending を出し、手札または空きステージへの登場を選べるようにした。
※再確認待ち：コスト4以下の `Liella!` メンバーだけが候補になり、`L`/`R` など空きエリアまたは手札へ移動できること。

### 20260624b stage-cost lower draw then hand topdeck

#### `PL!N-bp4-009` draw 2 then hand to deck top if own stage cost is lower

起動後: `PL!N-bp4-009` をライブ開始時に解決する。相手ステージのコスト合計が未入力の環境では確認ポップアップで「使う」を選び、2枚引いたあと手札1枚をデッキの一番上に置けることを見る。

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
export LLOCG_DEBUG_EFFECT_CARD=PL!N-bp4-009
export LLOCG_DEBUG_LIVE_IN_HAND=1
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_STAGE='C=PL!N-bp4-009'
export LLOCG_START_HAND='PL!N-bp4-009,PL!HS-PR-001'
export LLOCG_START_DECK_TOP='PL!N-PR-004,PL!N-PR-006,PL!HS-PR-020'
python3 ./run_llocg_ui_web.py
```

※実装済み：`live_start_my_cost_lower_draw2_hand_top1` と `draw_then_hand_to_deck_top` を追加。相手ステージコストが取得できない場合は手動確認、確認後に2枚ドローして手札1枚をデッキ上へ置く。
※再確認待ち：確認ポップアップで「使う」を選んだ後、手札選択UIが出て、選んだカードがデッキ上へ置かれること。

### 20260624c mill top 2 then waiting LIVE to deck 4th

#### `PL!N-bp5-021` mill 2 then optional waiting LIVE to 4th from top

起動後: `PL!N-bp5-021` を登場させる。デッキ上2枚が控え室に置かれたあと、控え室のライブカードを1枚選ぶUIが出て、選んだカードがデッキの上から4枚目に置かれることを見る。

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
export LLOCG_DEBUG_EFFECT_CARD=PL!N-bp5-021
export LLOCG_START_HAND='PL!N-bp5-021,PL!HS-PR-001'
export LLOCG_START_GREEN='PL!-sd1-019'
export LLOCG_START_DECK_TOP='PL!HS-PR-001,PL!HS-PR-020,PL!-PR-001,PL!SP-bp1-001,PL!SP-bp1-002'
python3 ./run_llocg_ui_web.py
```

※実装済み：`mill_top_k_then_waiting_live_to_deck_nth_optional` と `choose_live_from_green_to_deck_nth` を追加。デッキ上2枚を控え室に置いたあと、控え室のライブカードを任意でデッキ上から指定枚目へ挿入できるようにした。
※再確認待ち：控え室のライブカード候補が表示され、選択したライブカードがデッキ上から4枚目に入ること。

### 20260625a reveal top cost member then position change

#### `PL!N-pb1-004` reveal top cost <=9 member to hand then position change

起動後: `PL!N-pb1-004` をライブ開始時に解決する。デッキトップのコスト9以下メンバーが公開されて手札に加わり、続けて `PL!N-pb1-004` の移動先を選べることを見る。

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
export LLOCG_DEBUG_EFFECT_CARD=PL!N-pb1-004
export LLOCG_DEBUG_LIVE_IN_HAND=1
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_STAGE='L=PL!HS-PR-001,C=PL!N-pb1-004'
export LLOCG_START_HAND='PL!-sd1-019'
export LLOCG_START_DECK_TOP='PL!N-bp1-001,PL!HS-PR-001,PL!-sd1-019'
python3 ./run_llocg_ui_web.py
```

※実装済み：`reveal_top1_cost_le_member_hand_then_self_position_change` を追加。条件に合うトップカードは手札へ、条件外カードは控え室へ置き、条件達成時は既存のポジションチェンジUIへつなぐ。
※再確認待ち：公開確認後、移動先選択UIで `PL!N-pb1-004` を `R` などへ移動できること。

### 20260625b stage member count top keep-one

#### `PL!HS-bp6-001` look top stage member count +2, keep one on top

起動後: `PL!HS-bp6-001` を登場させる。自分のステージにいるメンバー数+2枚を見て、選んだ1枚だけがデッキ上に戻り、残りが控え室に置かれることを見る。

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
export LLOCG_DEBUG_EFFECT_CARD=PL!HS-bp6-001
export LLOCG_DEBUG_LIVE_IN_HAND=1
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_STAGE='L=PL!HS-PR-001,C=PL!HS-bp6-001'
export LLOCG_START_HAND='PL!-sd1-019'
export LLOCG_START_DECK_TOP='PL!N-bp1-001,PL!-PR-001,PL!-sd1-019,PL!HS-PR-020,PL!SP-bp1-001'
python3 ./run_llocg_ui_web.py
```

※実装済み：`look_top_stage_member_count_plus_keep_one_top_rest_waiting` を追加。ステージ上のメンバー数を数えて+N枚を見たあと、既存の `choose_top_keep_one` UIで1枚をデッキ上へ戻す。
※再確認待ち：ステージメンバー2人なら上4枚が候補に出て、選択した1枚だけがデッキ上に戻ること。

### 20260625c remaining top-k audit batch

#### `LL-bp4-001` named member pick then opponent wait

起動後: デッキ上5枚から `絢瀬絵里` / `朝香果林` / `葉月恋` のメンバーカードを1枚手札に加える。選んだカードのコスト以下、かつ元々のブレード3以下の相手メンバーをウェイトにした人数を入力できることを見る。

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
export LLOCG_DEBUG_EFFECT_CARD=LL-bp4-001
export LLOCG_DEBUG_LIVE_IN_HAND=1
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_STAGE='C=LL-bp4-001'
export LLOCG_START_HAND='PL!-sd1-019'
export LLOCG_START_DECK_TOP='LL-bp4-001,PL!N-bp1-001,PL!HS-PR-001,PL!-PR-001,PL!SP-bp1-001'
python3 ./run_llocg_ui_web.py
```

※実装済み：`look_top_named_members_optional_then_opponent_wait_cost_blade` を追加。選んだカードのコストを使って既存の相手ウェイト人数入力UIへつなぐ。
※再確認待ち：対象名メンバー選択後、相手ウェイト人数入力が表示されること。

#### `PL!-bp6-006` choose heart color, reveal top5, pick μ's and gain blades

起動後: 好きなハート色を選び、公開5枚が指定色条件を満たす場合、公開カードから `μ's` のカード1枚を手札に加え、ブレード3本を得ることを見る。

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
export LLOCG_DEBUG_EFFECT_CARD=PL!-bp6-006
export LLOCG_DEBUG_LIVE_IN_HAND=1
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_STAGE='C=PL!-bp6-006'
export LLOCG_START_HAND='PL!-sd1-019'
export LLOCG_START_DECK_TOP='LL-bp4-001,LL-bp4-001,LL-bp4-001,LL-bp4-001,LL-bp4-001'
python3 ./run_llocg_ui_web.py
```

※実装済み：`choose_heart_color_reveal_topk_all_match_group_pick_gain_blades` を追加。色指定後に5枚公開し、条件達成時は対象グループ選択とブレード付与まで処理する。
※再確認待ち：色指定、公開カード選択、ブレード3本付与が順に動くこと。

#### `PL!N-bp5-029` Kasumi reveal pick grants picked heart colors

起動後: ステージに `中須かすみ` がいる状態でデッキ上4枚を公開し、「中須かすみ」のカード1枚を選ぶ。選んだカードが持つ色のハートがステージの `中須かすみ` に1つずつ付与され、公開カードはすべて控え室に置かれることを見る。

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
export LLOCG_DEBUG_EFFECT_CARD=PL!N-bp5-029
export LLOCG_DEBUG_LIVE_IN_HAND=1
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_STAGE='C=PL!N-PR-004'
export LLOCG_START_HAND='PL!-sd1-019'
export LLOCG_START_DECK_TOP='PL!N-PR-004,PL!HS-PR-001,PL!-PR-001,PL!SP-bp1-001'
python3 ./run_llocg_ui_web.py
```

※実装済み：`stage_named_exists_reveal_topk_named_pick_gain_picked_hearts` を追加。選んだカードは手札に入れず、公開カードをすべて控え室へ送る専用解決にした。
※再確認待ち：選択カード由来のハートがステージの `中須かすみ` に付与されること。

#### `PL!SP-bp5-009` repeat optional mill top1, gain blade, wait if live

起動後: デッキ上1枚を控え室に置くかを最大5回まで選ぶ。置いたたびにブレード1本を得て、置いたカードがライブカードならこのメンバーがウェイトになることを見る。

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
export LLOCG_DEBUG_EFFECT_CARD=PL!SP-bp5-009
export LLOCG_DEBUG_LIVE_IN_HAND=1
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_STAGE='C=PL!SP-bp5-009'
export LLOCG_START_HAND='PL!-sd1-019'
export LLOCG_START_DECK_TOP='PL!-sd1-019,PL!HS-PR-001,PL!-PR-001,PL!N-bp1-001,PL!SP-bp1-001'
python3 ./run_llocg_ui_web.py
```

※実装済み：`optional_repeat_mill_top1_gain_blade_wait_if_live` を追加。1回ごとに確認を出し、使った場合は上1枚を控え室、ブレード付与、ライブなら自身ウェイト、残回数があれば再確認へ進む。
※再確認待ち：最大5回まで繰り返し確認が出て、途中でスキップできること。


## DB-backed matcher count check

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 - <<'PY'
import csv
from collections import Counter
p='loveca_reports/loveca_topk_complex_family_audit_20260604a.csv'
with open(p, encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
c=Counter(r['status'] for r in rows)
print(dict(sorted(c.items())))
PY
```

Expected after 20260625c:

```text
needs_audit_unmatched_topk=0
```

## Focused UI debug targets

### 20260622h yell heart color conversion

- `PL!HS-bp6-027`: live start, revealed yell cards include Hasunosora members with all six heart colors. Confirm target-color conversion is applied until live end.
- `PL!SP-bp4-023`: Dazzling Game style color conversion. Confirm the chosen/target color is reflected during the live.

### 20260622i top-k choose N to hand

- `LL-bp6-001`: put six known cards on top. Confirm two selected cards go to hand and the other four go to waiting room.

### 20260622j sentence variant and simple mill

- `PL!-bp5-222` / `PL!HS-cl1-007`: confirm top 3 is shown, one selected card goes to hand, remaining two go to waiting room.
- `PL!HS-cl1-004`: confirm the top 3 cards move to waiting room.

### 20260622k cost-filtered group member

- `PL!HS-bp5-008`: put a cost 9+ Hasunosora member and non-matching cards in top five. Confirm only the matching member is selectable.
- `PL!-bp4-006`: set success live score sum to at least 3. Confirm the inner μ's member top-five search appears.

### 20260623a reorder typo and top1 optional mill

- `PL!-sd1-019`: confirm the top 3 reorder UI appears and kept cards return to deck top in selected order.
- `PL!HS-cl1-001`: confirm top card can be moved to waiting room or kept on top.

### 20260623b conditional mill followups

- `PL!-sd1-007`: top five include at least one live. Confirm top five go to waiting room, then draw 1.
- `PL!HS-bp1-008`: top three are all members. Confirm top three go to waiting room, then draw 1.
- `PL!HS-PR-019` / `PL!HS-PR-021` / `PL!HS-sd1-013`: top three are matching-color heart members. Confirm source gains the matching temporary heart.
- `PL!HS-bp5-001` / `PL!HS-bp5-013` / `PL!HS-bp6-009`: confirm source gains the expected temporary blade icons only when the milled cards meet the condition.

Note: if the followup draw empties the deck, existing refresh rules may immediately shuffle waiting room into the deck. Use a deck with extra remaining cards when checking waiting-room contents.

### 20260623c mill retrieve / reorder all / optional mill

- `PL!-bp5-010`: confirm top 3 move to waiting room, then A-RISE member picker appears.
- `PL!HS-pb1-004`: confirm top 3 move to waiting room, then Cerise Bouquet live picker appears.
- `PL!N-bp1-009`: confirm top 2 move to waiting room, then member picker appears.
- `PL!-pb1-006`: confirm μ's live topdeck UI appears, followed by opponent-wait draw confirmation.
- `PL!HS-pb1-027`: confirm optional mill prompt appears only when a Cerise Bouquet member is on your stage.
- `PL!-bp6-016`: confirm top 3 reorder UI requires all three cards to be placed back on deck top.
- `PL!-pb1-016`: confirm optional hand-discard picker appears first, then the lily white top-four search appears after paying the cost.

### 20260623d reveal until live

- `PL!N-bp1-011`: put non-live cards above one live card. After paying the optional hand-discard cost, confirm the live card goes to hand and all earlier revealed cards go to waiting room.

### 20260623e trailing punctuation top-k route

- `PL!SP-pb1-017`: put a `5yncri5e!` card and non-matching cards in the top five. Confirm only the matching unit card is selectable.

### 20260623f debug feedback pass

- `PL!-bp5-222` / `PL!HS-cl1-007`: confirm the source member becomes WAIT after paying the self WAIT plus hand-discard cost.
- `PL!HS-bp5-008`: confirm the source member becomes WAIT after paying, then the cost-9+ Hasunosora member filter appears.
- `PL!-sd1-007`: confirm automatic top-five mill then draw shows an `自動効果確認` popup with moved cards and result text.
- `LL-bp6-001`: confirm top-k multi-pick uses selected frames/order badges and one final confirm button.

### 20260623g top-k filter variants

- `PL!-bp6-002`: confirm no-ability μ's or <常時> μ's cards are selectable from top two.
- `PL!S-bp6-005`: confirm only members with red, green, and blue hearts are selectable from top two.
- `PL!SP-bp5-013`: after paying hand discard, confirm Sunny Passion members or blade-heart Liella! members are selectable from top five.
- `PL!N-bp4-021`: confirm any waiting-room card can be placed on top of the deck, with skip available.

### 20260623i top-k filtered up-to multi-pick

- `PL!S-bp2-005`: confirm only red/green/blue-heart members are selectable from top seven, and 0 to 3 selected cards can be moved to hand.

## Internal smoke check snippets

Use these only for quick engine-level confirmation when UI setup is slow.

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db, _get_card
from llocg_ui import engine
cards = load_cards_db(Path('.'))
targets = [
    'LL-bp6-001','PL!HS-bp5-008','PL!-sd1-019','PL!HS-cl1-001',
    'PL!-sd1-007','PL!HS-bp1-008','PL!HS-bp5-001',
    'PL!-bp5-010','PL!HS-pb1-004','PL!N-bp1-009',
    'PL!-pb1-006','PL!HS-pb1-027','PL!-bp6-016','PL!-pb1-016',
    'PL!N-bp1-011','PL!SP-pb1-017',
    'PL!-bp6-002','PL!S-bp6-005','PL!SP-bp5-013','PL!N-bp4-021',
    'PL!S-bp2-005',
]
for cn in targets:
    ci = _get_card(cards, cn)
    hits = []
    for ab in getattr(ci, 'abilities', []) or []:
        for cl in ab.get('clauses', []) or []:
            eff = str(cl.get('effect_template') or cl.get('raw') or '').strip()
            m = engine._match_effect_template(eff)
            if m:
                hits.append(m[0].get('id'))
    print(cn, getattr(ci, 'name', ''), hits)
PY
```
