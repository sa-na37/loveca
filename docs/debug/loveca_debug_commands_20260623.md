# Loveca implementation debug checklist 20260623

目的: 20260622h から 20260623i までに追加した実装の確認観点とコマンドを一箇所に集約する。

＊ユーザコメントとcodexコメントを区別しやすくするため、追加コメントについては別の記号を使うように
＊ユーザ/codexコメントツリーは該当デバッグが完全に完了するまで削除しない

0708
＊全体的に実装ルールに従えていない実装が多い(複数コスト選択時のUI、自動効果の無言処理、効果発生源の表示など)。一度ルールを整理するべきではないだろうか

※対応済み：実装前・デバッグ対応前・完了前に確認する補助ルールとして `docs/notes/loveca_runtime_implementation_rules_20260708.md` を作成した。複数コスト選択、自動効果の無言処理、効果発生源表示、カード番号だけの表示、公開/見る/エール表示、state の寿命と snapshot/restore まで必須チェック化した。

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
- `PL!N-bp4-009` draw 2 then hand to deck top if own stage cost is lower
  - 2026-06-29: 挙動問題なし。
  - 修正反映: 手動確認後に2枚引き、手札1枚をデッキ上へ置く動作を確認済み。
- `PL!N-pb1-004` reveal top cost <=9 member to hand then position change
  - 2026-06-29: 挙動問題なし。
  - 修正反映: ライブステップドロー後に確認対象を公開できるコマンドで、公開カード手札追加とポジションチェンジを確認済み。
- `LL-bp4-001` named member pick then opponent wait
  - 2026-06-29: 挙動問題なし。
  - 修正反映: ライブステップドロー後に対象名メンバーが候補に残るコマンドで、対象選択後の相手ウェイト人数入力を確認済み。
- `PL!SP-bp5-007` top 5 choose up to 3 by distinct group
  - 2026-06-30: 問題なし。
  - 修正反映: 同一ポップアップ内の複数選択、3枚上限、同一グループ候補のグレーアウト選択不可表示を確認済み。
- `PL!N-bp5-021` mill 2 then optional waiting LIVE to 4th from top
  - 2026-06-30: 問題なし。
  - 修正反映: 控え室ライブ候補のカードリスト表示と、リストの意味が分かる本文表示を確認済み。
- `PL!HS-bp6-001` look top stage member count +2, keep one on top
  - 2026-06-30: 問題なし。
  - 修正反映: 登場時効果を確認できるコマンドと、デッキ上に残す1枚を選ぶ説明表示を確認済み。
- `PL!-bp6-006` choose heart color, reveal top5, pick μ's and gain blades
  - 2026-06-30: 問題なし。
  - 修正反映: ハート色表示と、手札コスト支払いであることが分かる本文表示を確認済み。
- `PL!SP-bp5-009` repeat optional mill top1, gain blade, wait if live
  - 2026-06-30: 問題なし。
  - 修正反映: ミル結果カード、ブレード獲得、ライブカード時のウェイト結果表示を確認済み。


## Active debug commands integrated 20260625c

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

＊挙動問題なし
＊UI問題あり：対象選択後の選択肢が簡素すぎてわかりづらい。ボタンではなくリストで、単語ではなく文章で表示させたい

※実装済み：`look_top_k_optional_cost_le_group_member_stage_or_hand` を追加。選択後に `topk_stage_or_hand` pending を出し、手札または空きステージへの登場を選べるようにした。
※修正済み：`topk_stage_or_hand` の移動先選択を、手札/各ステージエリアが文章で分かるリスト表示へ変更した。
※再確認待ち：コスト4以下の `Liella!` メンバーだけが候補になり、`L`/`R` など空きエリアまたは手札へ移動できること。

＊表示は悪くない。ただし最後の選択肢が出るポップアップで対象のカードがカードナンバー表示になっているので修正。同時に「ポップアップ上で特定のカードを指定する場合は必ずカードナンバーだけの表示は行わず、メンバーカードの場合は[Nコスト メンバー名]ライブカードの場合はカード名で表示するようにテンプレート化する。これを毎回指摘していると非常に効率が悪い

※修正済み：ポップアップ上でカードを文章表示する共通関数を追加し、メンバーカードは「Nコスト メンバー名」、ライブカードはカード名で表示するようテンプレート化した。

＊メンバー名の表示が直っておらず、カードナンバーで表示される

※修正済み：`topk_stage_or_hand` の対象カード番号を pending のメタ情報収集対象に追加し、カード名/種別/コストを引けるようにした。

＊「効果の選択」の直下に出る文が「PL!SP-bp5-008 を手札に加えるか、メンバーのいないエリアに登場させます。」となっておりナンバー表示のまま



### 20260625c remaining top-k audit batch

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
export LLOCG_START_HAND='PL!N-bp5-029,PL!-sd1-019'
export LLOCG_START_DECK_TOP='PL!HS-PR-001,PL!N-PR-004,PL!-PR-001,PL!SP-bp1-001'
python3 ./run_llocg_ui_web.py
```

＊デバッグコマンド不備：該当のカードが初期状態のどこにも存在しない

※実装済み：`stage_named_exists_reveal_topk_named_pick_gain_picked_hearts` を追加。選んだカードは手札に入れず、公開カードをすべて控え室へ送る専用解決にした。
※修正済み：効果カードが初期状態に存在するよう手札へ追加し、ライブステップドロー後も確認対象の `中須かすみ` が候補に残るよう山札2枚目へ移動した。
※再確認待ち：選択カード由来のハートがステージの `中須かすみ` に付与されること。

＊挙動問題なし
＊UI問題あり：公開されたカードがポップアップ上に公開されない。選択させるポップアップだけが表示されるが何が起こっているのかまるでわからない。「公開されたカードのうち中州霞であるものを選択させるポップアップ」「選択したカードのハートを付与するステージ上メンバーを選択するポップアップ」の二段構えにする

※修正済み：公開カード全体を表示し、条件に合うカードだけ選べる1段目ポップアップと、選択カードのハートを付与するステージ上メンバーを選ぶ2段目ポップアップへ分離した。

＊UI修正：２段目の対象メンバー選択も画像表示が望ましい。また、２段目選択後の確認ポップアップはやや冗長なのでなくてもいい

※修正済み：2段目の付与先メンバー選択をステージ上メンバーの画像ボタン表示へ変更し、付与先選択後の追加確認ポップアップを省略するようにした。

＊問題なし
    効果によって公開されたカードがパブリックウインドウで公開領域として表示されていないバグがあるので要修正。「公開されたカードのリストから選択して効果処理」といった内容のポップアップでも公開されたカードリストはパブリックで公開表示されるべき。ただし、「山札の上からn枚見る」と「n枚公開する」で処理が異なる点には注意すること

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

### 20260702 YELL popup / draw icon and under-energy family

#### YELL reveal popup and two draw icons

起動後: `PL!S-bp3-020` をライブセットする。セット後ドローで `PL!-bp4-013` が手札に入り、YELL公開6枚の中に `PL!-bp4-021` と `PL!-pb1-030` が含まれることを見る。ログで `draw+2 -> drew 2` が出て、残り山札の `PL!-bp4-024` と `PL!-bp3-006` が追加ドローされることを確認する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!S-bp3-020'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!SP-bp2-010'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp3-020,PL!-bp4-021,PL!S-bp3-020,LL-bp5-001,PL!-pb1-030,PL!-bp4-020,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=8
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

補足: 山札8枚だけの厳密デッキでは、セット後ドロー1枚 + YELL公開6枚のあと残り山札が1枚だけになる。その場合はドローアイコン数が2でも実際に引けるカードが1枚しかないため、ログに `draw shortage requested=2 drew=1` が出る。

＊デバッグコマンド不備：export LLOCG_START_STAGE_C=PL!SP-bp2-010　シングルクオート必須
＊挙動問題なし


#### `PL!N-pb1-002` under-energy optional enter

起動後: `PL!N-pb1-002` を登場させ、登場時の任意効果で「使う」を選ぶ。エネルギー2枚がこのメンバーの下に置かれ、カード下エネルギー表示が2枚になることを見る。その後 `PL!HS-bp1-019` をライブセットして成功させ、ログで `stage always bonus = +1`、合計スコア2になることを確認する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!N-pb1-002,PL!HS-bp1-019'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=15
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし

#### `PL!N-bp3-025` return under-energy for temporary hearts

起動後: `PL!N-pb1-002` を登場させ、登場時の任意効果でエネルギー2枚を下に置く。その後 `PL!N-bp3-025` をライブセットし、ライブ開始時効果で下エネルギーがあるメンバーを選ぶ。戻す枚数で `2` を選び、下エネルギーが0になり、そのメンバーがライブ終了時まで赤ハート6個を得ることを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!N-pb1-002,PL!N-bp3-025'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=15
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI修正：ハート増加バッジがウインドウサイズ依存の可変になっていない
＊バグ：必要ハート色数を満たしていないはずなのに成功する

#### `PL!N-bp3-007` hand member to former area then under-energy

起動後: センターの `PL!N-bp3-007` の起動効果を使う。コストで `PL!N-bp3-007` が控え室へ置かれ、手札の `LL-bp2-001` を選ぶポップアップが出る。選択後、`LL-bp2-001` がセンターに登場し、そのメンバーの下エネルギー表示が1枚になることを見る。ログでは `[ACT] PL!N-bp3-007: hand LL-bp2-001 -> stage C; energy under +1` を確認する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!N-bp3-007'
export LLOCG_START_HAND='LL-bp2-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=3
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊デバッグコマンド不備：対象となるカードが手札に存在しない
＊挙動問題あり：対象が存在しない場合に無言で処理を終了している
※修正済み：現行コマンドでは対象 `LL-bp2-001` を手札に入れる形になっていることを確認。対象が存在しない場合は、手札/控え室から登場させる同系 route で確認ポップアップを返すよう修正済み。
＊対象がない場合の挙動は問題なし。
＊デバッグコマンド不備解消されず。手札にあるカードはコスト13以下でも優木せつ菜でもない

#### `LL-bp5-002` live-success retrieve different stage-group card

起動後: `LL-bp5-002` をライブセットして成功させる。ライブ成功時に、ステージ上メンバーの推定グループ名（`μ's` / `虹ヶ咲` / `蓮ノ空`）と異なるグループ名を持つ控え室カードだけが候補になることを見る。この例では `PL!SP-pb2-008` だけが候補になり、選択すると手札に加わる。`PL!-bp4-005` はステージ側に `μ's` がいるため候補外。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!-bp4-005'
export LLOCG_START_STAGE_C='PL!N-pb1-002'
export LLOCG_START_STAGE_R='PL!HS-bp5-002'
export LLOCG_START_HAND='LL-bp5-002'
export LLOCG_START_GREEN='PL!SP-pb2-008,PL!-bp4-005'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-bp4-013,PL!-bp3-020,PL!-bp4-020,PL!-pb1-030,PL!-bp4-024'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=12
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊デバッグコマンド不備：山札が少なすぎてリフレッシュするので控え室がなくなる
＊UI修正：条件不適の際に表示されるポップアップに確認ボタンがない
※修正済み：デッキ枚数不足でリフレッシュしにくいよう、`LLOCG_START_DECK_EXACT` を10枚に増量。条件不適時の `message_ack` に `ok` 選択肢を追加し、確認ボタンが出るよう修正。
＊デバッグコマンド不備解消されず。自分で盤面ブレード総数10本以上にしてるのになんで中途半端に山札を増やすのか理解できない、普通に50枚くらいにすればいい

#### `PL!HS-bp1-002` waiting-room member to former area

起動後: センターの `PL!HS-bp1-002` の起動効果を使う。コストで自身が控え室へ置かれ、控え室からコスト15以下の『蓮ノ空』メンバーを選ぶポップアップが出る。`PL!HS-bp5-002` を選択すると、センターにコスト支払いなしで登場する。`PL!SP-pb2-008` はグループ違いのため候補に出ないことも確認する。なお、コストで控え室へ置かれた `PL!HS-bp1-002` 自身も条件を満たすため候補になってよい。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!HS-bp1-002'
export LLOCG_START_GREEN='PL!HS-bp5-002,PL!SP-pb2-008'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=2
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI修正：効果対象選択ポップアップをテンプレートに合わせる
※修正済み：控え室から元エリアへ登場させる対象選択は `display_cards` 付きのカードリスト UI 経路を使用。起動効果由来のポップアップ見出しは `起動効果` 表示になるよう再適用済み。
＊問題なし。


#### `PL!HS-bp5-022` waiting-room group member to empty area

起動後: `PL!HS-bp5-022` をライブセットしてライブ開始時効果を解決する。控え室からコスト4以下の『Edel Note』メンバーだけが候補になり、選択後、空きエリアを選んで登場できることを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!HS-bp5-007'
export LLOCG_START_HAND='PL!HS-bp5-022'
export LLOCG_START_GREEN='PL!HS-bp5-008,PL!SP-pb2-008'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=12
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題あり：条件(ステージに9以上のedelnote)未達成でも効果を選択できてしまう
＊デバッグコマンド不備：ステージ条件未達成、控え室にも対象がない
※修正済み：条件付き「以下から1つを選ぶ」親句を後続選択肢に引き継ぐようにし、ステージにコスト9以上の『Edel Note』メンバーがいない場合は選択肢ではなく条件未達の確認ポップアップを出すよう修正。デバッグコマンドはステージ条件用に `PL!HS-bp5-007`、控え室対象用に `PL!HS-bp5-008` を入れる形へ更新。
※20260706再確認済み：ローカル更新で一部上書きされていたため、現行 `engine.py` に再適用。内部確認で条件未達時は確認ポップアップ、条件達成時は E2 付き選択肢になることを確認。
＊問題なし。

#### `PL!HS-bp5-002` embedded energy cost then waiting-room member to empty area

起動後: センターの `PL!HS-bp5-002` の起動効果を使う。効果文先頭の `<(E)><(E)>` が支払われ、控え室からコスト2以下のメンバーを選ぶポップアップが出る。`LL-bp6-001` を選び、空きエリアに登場することを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!HS-bp5-002'
export LLOCG_START_GREEN='LL-bp6-001,PL!HS-bp2-008'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=2
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題あり：コスト20のメンバーを対象選択できてしまう
＊デバッグコマンド不備：対象が控え室にない
＊UI問題あり：起動効果なのに自動効果としてポップアップが出ている、対象カードリストに画像が出ていない
※修正済み：控え室メンバー登場系の候補なし時は無言終了せず確認ポップアップを返すよう修正。起動効果由来の対象選択ポップアップは `起動効果` 表示にし、候補リストは `display_cards` 付きでカード画像表示される経路を維持。内部確認ではコスト2以下の `LL-bp6-001` のみ候補になり、コスト4の `PL!HS-bp2-008` は候補外。
※20260706再確認済み：ローカル更新で一部上書きされていたため、現行 `engine.py` に再適用。候補なしではエネルギーを支払わず確認ポップアップ、候補ありでは `LL-bp6-001` のみ候補になり、ポップアップ見出しが `起動効果` になることを内部確認。
＊デバッグコマンド不備：控え室にコスト２以下のメンバーが存在しない。LL-bp6-001はコスト２０のメンバーだが、これは正しく読み取れていますか？DBがおかしい？

#### `PL!HS-bp2-008` baton from lower-cost group member enter bonus

起動後: 手札の `PL!HS-bp2-008` をセンターにいる `PL!HS-bp2-004` へ重ねて登場させる。バトンタッチ元がこのメンバーよりコストが低い『DOLLCHESTRA』メンバーなので、登場時効果によりライブ終了時までブレード+2される。差額コスト2だけ支払われることも確認する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!HS-bp2-004'
export LLOCG_START_HAND='PL!HS-bp2-008'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=10
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
  要修正：自動効果が無言で処理されている

#### `PL!HS-bp2-008` baton condition negative cases

起動後: 手札の `PL!HS-bp2-008` をセンターへ重ねて登場させる。下記3パターンでは、バトンタッチ元が「このメンバーよりコストが低い『DOLLCHESTRA』」条件を満たさないため、ブレード+2が付与されないことを見る。

##### higher cost source

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!HS-sd1-016'
export LLOCG_START_HAND='PL!HS-bp2-008'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊同上

##### same cost source

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!HS-bp2-008'
export LLOCG_START_HAND='PL!HS-bp2-008'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```
＊デバッグコマンド不備：手札に該当のカードが存在しない。ステージに同カードナンバーのカードを置いたために起こったバグか？

##### different group source

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!SP-PR-004'
export LLOCG_START_HAND='PL!HS-bp2-008'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

※20260706修正済み：条件未達時に効果が適用されたようなログが出ないよう、バトンタッチ条件 wrapper がスキップ理由を返し、登場時ログも `SKIP` になるよう修正。

#### `PL!SP-pb2-008` yell-revealed no-blade-heart Liella score bonus

起動後: `LL-bp5-001` をライブセットしてライブ開始からエールへ進める。ステージの `PL!SP-pb2-008` が、エール公開されたブレードハートを持たない『Liella!』メンバー2枚につきライブ合計スコア+1する。下記は4枚公開で上限+2を確認する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!SP-pb2-008'
export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!SP-PR-004,PL!SP-PR-005,PL!SP-PR-006,PL!SP-PR-008,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI問題あり：常々言っているが効果を解決する際に条件達成の有無、詳細、発動した効果は必ずポップアップ表示すること

#### `PL!S-bp2-004` no-LIVE revealed reroll yell

起動後: `LL-bp5-001` をライブセットしてエールへ進める。ステージの `PL!S-bp2-004` により、公開カードにライブカードがない場合、それらをすべて控え室へ置いて追加エールする確認ポップアップが出ることを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!S-bp2-004'
export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!S-PR-028,PL!S-PR-032,PL!S-PR-013,PL!S-PR-016,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI問題あり：追加エールを行った際に行われたエールの詳細が表示されない。エール確認ポップアップの表示を「エールを行う」という事象が発生した直後のタイミングになるように調整できないだろうか

#### `PL!S-bp3-020` blade-heart two-or-fewer reroll yell

起動後: `PL!S-bp3-020` をライブセットしてエールへ進める。公開カードの中にブレードハートを持つカードが2枚以下なら、それらをすべて控え室へ置いて追加エールする確認ポップアップが出ることを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!S-bp2-004'
export LLOCG_START_HAND='PL!S-bp3-020'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!S-PR-028,PL!S-PR-032,PL!S-PR-013,PL!S-PR-016,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI問題あり：同上。エールの詳細表示がない

#### `PL!HS-bp6-027` choose revealed cards then extra yell

起動後: `PL!HS-bp6-027` をライブセットしてエールへ進める。公開されたブレードハートを持たない『蓮ノ空』カードを最大3枚まで選び、選んだ枚数ぶん追加エールできることを見る。`PL!HS-bp5-022` はライブカードでブレードハートを持つため候補外。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!HS-bp5-002'
export LLOCG_START_HAND='PL!HS-bp6-027'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!HS-PR-027,PL!HS-PR-029,PL!HS-bp5-022,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030,PL!-bp4-013'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題あり：追加エール後の詳細が見えていない

#### `PL!SP-bp2-010` yell reveal count modifier

起動後: `LL-bp5-001` をライブセットしてライブ開始時効果を解決する。他メンバーがいるため、`PL!SP-bp2-010` によりこのライブ終了時までエール公開枚数が8枚減ることを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!SP-bp2-010'
export LLOCG_START_STAGE_C='PL!SP-PR-004'
export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!SP-PR-004,PL!SP-PR-005,PL!SP-PR-006,PL!SP-PR-008,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI要修正：解決した結果何が起きたか表示されない。また、ブレード本数を減らす効果についてバッジ表示を試しに実装してみたい

#### `LL-bp5-001` movement condition live-success score bonus

起動後: `LL-bp5-001` をライブセットする前にステージメンバーをポジションチェンジさせる。ライブ成功時に、エール公開ライブ数やステージハート種類数が不足していても、このターンのエリア移動記録によりスコア+1されることを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!SP-PR-004'
export LLOCG_START_STAGE_C='PL!SP-PR-005'
export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_MOVED_THIS_TURN=1
export LLOCG_START_STAGE_MOVED_CARDS='PL!SP-PR-004'
export LLOCG_START_DECK_EXACT='PL!SP-PR-004,PL!SP-PR-005,PL!SP-PR-006,PL!SP-PR-008,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊デバッグコマンド不備：与えられた状況では移動できない。bp5のきな子(R)あたりの起動効果で動かせるようにするべき

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

### 20260706h hand member empty-area entry / generic lower-cost baton

#### `PL!-PR-015` lower-cost baton -> hand member cost <= 4 enters empty area

Confirm that playing `PL!-PR-015` by baton from a lower-cost member opens a hand member picker, then an empty-area picker. Select `PL!-sd1-002`, then choose `L` or `R`; it should enter stage without paying its play cost.

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

export LLOCG_START_HAND='PL!-PR-015,PL!-sd1-002'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_C='PL!-sd1-002'
export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

＊デバッグコマンド不備：効果対象が手札にない

#### `PL!-PR-015` lower-cost baton negative same-cost case

Confirm that playing `PL!-PR-015` by baton from another `PL!-PR-015` does not open the hand member entry picker and logs/skips the unmet lower-cost condition.

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

export LLOCG_START_HAND='PL!-PR-015,PL!-sd1-002'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_C='PL!-PR-015'
export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

＊デバッグコマンド不備：該当のカードが手札にない。やはりステージと手札で同カードナンバーのカードを設定しようとするとうまくいかないバグがある？

### 20260707a generic draw-until-hand / stage-member-count draw

#### `PL!HS-PR-031` hand size 5 draw route

Confirm that after paying the optional hand discard cost, the effect draws cards until the hand count reaches 5.

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

export LLOCG_START_HAND='PL!HS-PR-031,LL-bp5-001,PL!-bp4-013'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_DECK_EXACT='PL!HS-bp6-001,PL!HS-bp6-002,PL!HS-bp6-003,PL!HS-bp6-004,PL!HS-bp6-005,PL!HS-bp6-006,LL-bp6-001'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI要修正：複数枚のハンドコストを選択する場合は同時に選択するようにする。これも何回指摘しているかわからない

※修正済み：複数枚の手札捨てコストは共通 helper で `choose_member_from_green_multi_up_to` の hand multi-select pending を使うよう修正。`PL!HS-PR-031` は内部確認で 2枚同時選択 pending になることを確認済み。UI実機再確認待ち。

#### `PL!-bp3-004` stage member count draw then discard route

Confirm that the on-enter effect draws 1 card for each current stage member, then opens the hand discard picker for 1 card.

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

export LLOCG_START_HAND='PL!-bp3-004'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_L='PL!-sd1-002'
export LLOCG_START_STAGE_R='PL!-PR-007'
export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI要修正：効果の発生源と効果詳細が出ていない

※修正済み：ドロー後/効果後の手札捨て pending に `auto_effect_detail` と `source_cn` を渡すよう共通 helper を修正。`PL!-bp3-004` は内部確認で登場時効果の発生源と効果本文が pending text に入ることを確認済み。UI実機再確認待ち。

### 20260707b stage condition / score-filtered waiting LIVE retrieve

#### `PL!HS-bp6-008` self wait then retrieve score <= 4 Hasunosora LIVE

Confirm that the on-enter effect sets this member to WAIT, then opens a waiting-room picker containing only score 4 or lower `蓮ノ空` LIVE cards. The score 7 `蓮ノ空` LIVE and non-`蓮ノ空` LIVE should be excluded.

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

export LLOCG_START_HAND='PL!HS-bp6-008'
export LLOCG_START_GREEN='PL!HS-PR-011,PL!HS-bp5-018,PL!-bp3-021,PL!HS-bp2-025'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

＊挙動問題なし

### 20260707c moved self gains blade

#### `PL!SP-bp4-017` live-start moved self gains 2 blades

Confirm that a member listed in `LLOCG_START_STAGE_MOVED_CARDS` gains two temporary blade icons at live start. Removing `LLOCG_START_STAGE_MOVED_CARDS` and setting `LLOCG_START_STAGE_MOVED_THIS_TURN=0` should skip the effect.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_C='PL!SP-bp4-017'
export LLOCG_START_STAGE_MOVED_THIS_TURN=1
export LLOCG_START_STAGE_MOVED_CARDS='PL!SP-bp4-017'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

＊挙動問題あり：配置されているのが左サイドエリアではないのに効果が発動する
＊デバッグコマンド不備：移動させる効果を持ったカードで移動させた後確認する流れで無いと正しい挙動を確認できない

#### `PL!SP-sd2-003` live-success draw + moved bonus draw

Confirm that the live-success effect draws 1 card, then draws 1 additional card because this member is listed in `LLOCG_START_STAGE_MOVED_CARDS`.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_C='PL!SP-sd2-003'
export LLOCG_START_STAGE_MOVED_THIS_TURN=1
export LLOCG_START_STAGE_MOVED_CARDS='PL!SP-sd2-003'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006,PL!-bp3-004'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

### 20260707e stage movement BODY auto triggers

#### `PL!SP-sd2-002` self position-change then movement trigger

Confirm that activating `このメンバーをポジションチェンジする。` opens a destination picker. After moving, an auto-order prompt should appear for the movement trigger, and resolving it should grant a temporary purple heart to the moved member.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_STAGE_C='PL!SP-sd2-002'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

### 20260707g moved stage member bonus routes

#### `PL!S-bp5-022` moved stage members gain blade at live start

Confirm that only the stage member listed in `LLOCG_START_STAGE_MOVED_CARDS` gains a temporary blade at live start.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='PL!S-bp5-022'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_C='PL!SP-sd2-002'
export LLOCG_START_STAGE_MOVED_THIS_TURN=1
export LLOCG_START_STAGE_MOVED_CARDS='PL!SP-sd2-002'
export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

#### `PL!SP-bp5-014` enter draw if another stage member moved

Confirm that playing `PL!SP-bp5-014` draws 1 card because another stage member is listed in `LLOCG_START_STAGE_MOVED_CARDS`.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='PL!SP-bp5-014'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_L='PL!SP-sd2-002'
export LLOCG_START_STAGE_MOVED_THIS_TURN=1
export LLOCG_START_STAGE_MOVED_CARDS='PL!SP-sd2-002'
export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

#### `PL!SP-bp5-024` choose heart for moved stage members

Confirm that the live-start effect opens a heart-color picker, then grants the chosen heart to the stage member listed in `LLOCG_START_STAGE_MOVED_CARDS`.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='PL!SP-bp5-024'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_C='PL!SP-sd2-002'
export LLOCG_START_STAGE_MOVED_THIS_TURN=1
export LLOCG_START_STAGE_MOVED_CARDS='PL!SP-sd2-002'
export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

### 20260707i moved by group effect live-success score

#### `PL!SP-pb2-003` moved by Liella effect live total score +1

Confirm that the live-success effect adds +1 to the live total score when this member is listed in `LLOCG_START_STAGE_MOVED_CARDS`.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_C='PL!SP-pb2-003'
export LLOCG_START_STAGE_MOVED_THIS_TURN=1
export LLOCG_START_STAGE_MOVED_CARDS='PL!SP-pb2-003'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

### 20260707j entry origin and additional stage movement autos

#### `PL!S-bp6-008` brings `PL!S-bp6-006` from waiting room, then waiting-entry draw and blade gain

Start with `PL!S-bp6-008` on stage, activate its BODY ability, choose `PL!S-bp6-006` from waiting room, and confirm the entered member draws 2 and gains blade x3 because it entered from waiting room.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!S-bp6-008'
export LLOCG_START_GREEN='PL!S-bp6-006'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=6
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

#### `PL!HS-bp6-016` brings `PL!HS-bp6-015` from waiting room, then non-hand-entry draw and discard

Activate `PL!HS-bp6-016` BODY, choose `PL!HS-bp6-015` from waiting room, and confirm the entered member draws 2 and creates a discard-2 pending because it entered from outside the hand.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!HS-bp6-016'
export LLOCG_START_GREEN='PL!HS-bp6-015'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=8
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

#### Internal smoke: entry-origin effects and stage-movement BODY autos

Use this for quick engine-level confirmation of `PL!S-bp6-011`, `PL!S-bp6-006`, `PL!HS-bp6-015`, `PL!SP-bp5-004`, and `PL!SP-pb2-028`.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui import engine
from llocg_ui.db import load_cards_db

cards = load_cards_db(Path('.'))
rng = random.Random(1)

def make_gs():
    gs = engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
    gs.deck = ['PL!-bp4-013','PL!-bp4-020','PL!-bp4-024','PL!-bp4-021','PL!-bp3-006']
    gs.hand = []
    gs.stage = {'L': None, 'C': None, 'R': None}
    gs.green_room = []
    gs.pending = []
    gs.log = []
    gs.energy_active = 0
    gs.energy_wait = 2
    return gs

for cn, eff in [
    ('PL!S-bp6-011', '控え室から登場している場合、カードを2枚引き、手札を1枚控え室に置く。'),
    ('PL!HS-bp6-015', 'このメンバーが手札以外からステージに登場している場合、カードを2枚引き、手札を2枚控え室に置く。'),
    ('PL!S-bp6-006', 'カードを2枚引く。その後、控え室から登場している場合、ライブ終了時まで、<(ブレード)><(ブレード)><(ブレード)>を得る。'),
]:
    gs = make_gs()
    gs.stage['C'] = engine.StageSlot(cardnumber=cn, active=True)
    engine.try_apply_effect_template(gs, rng, cards, eff, {'pos': 'C', 'source_cn': cn, 'entry_origin': 'green'})
    print(cn, len(gs.hand), [p.get('kind') for p in gs.pending], getattr(gs.stage['C'], 'temp_blade', 0), gs.log[-2:])

for cn in ['PL!SP-bp5-004', 'PL!SP-pb2-028']:
    gs = make_gs()
    gs.stage['C'] = engine.StageSlot(cardnumber=cn, active=True)
    gs.stage_moved_this_turn = True
    gs.stage_moved_cardnumbers_this_turn = [cn]
    triggers = engine._collect_stage_movement_auto_triggers(gs, cards, [cn])
    for t in triggers:
        engine._exec_auto_trigger(gs, cards, t)
    print(cn, len(triggers), len(gs.hand), gs.energy_active, gs.energy_wait, getattr(gs.stage['C'], 'temp_hearts', {}), gs.log[-3:])
PY
```

### 20260707k stage-entered-this-turn condition

#### `PL!N-bp1-006` activates energy when a Nijigasaki member entered this turn

Play `PL!N-bp1-001` from hand first, then activate `PL!N-bp1-006` BODY and discard the remaining hand card as the cost. Confirm that 2 energy move from wait to active.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='PL!N-bp1-001,LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!N-bp1-006'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

### 20260707l turn-enter count and entered-member heart routes

#### Internal smoke: `PL!N-bp3-005` enter-count routes and `PL!S-bp5-005` entered-member heart picker

Confirm that the third stage entry triggers draw-until-hand-5, that 2+ entries grant live-total-score +1, and that the entered non-Aqours member gets the chosen heart.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui import engine
from llocg_ui.db import load_cards_db

cards = load_cards_db(Path('.'))
rng = random.Random(1)

gs = engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.deck = ['PL!-bp4-013','PL!-bp4-020','PL!-bp4-024','PL!-bp4-021']
gs.hand = ['LL-bp5-001']
gs.stage = {
    'L': engine.StageSlot(cardnumber='PL!N-bp3-005', active=True),
    'C': None,
    'R': engine.StageSlot(cardnumber='PL!N-bp1-001', active=True),
}
gs.stage_enter_count_this_turn = 3
gs.stage_entered_cardnumbers_this_turn = ['PL!N-bp1-002','PL!N-bp1-003','PL!N-bp1-001']
triggers = engine._collect_auto_triggers_on_member_enter(gs, cards, 'R', 'PL!N-bp1-001')
for t in triggers:
    engine._exec_auto_trigger(gs, cards, t)
print('enter3', [(t.get('kind'), t.get('source_cn')) for t in triggers], len(gs.hand), gs.log[-3:])

gs2 = engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs2.stage = {'L': None, 'C': engine.StageSlot(cardnumber='PL!N-bp3-005', active=True), 'R': None}
gs2.stage_enter_count_this_turn = 2
eff = 'このターン、自分のステージにメンバーが2回以上登場している場合、ライブ終了時まで、『<常時>ライブの合計スコアを+1する。』を得る。'
engine.try_apply_effect_template(gs2, rng, cards, eff, {'pos': 'C', 'source_cn': 'PL!N-bp3-005'})
print('enter2score', getattr(gs2.stage['C'], 'temp_score', 0), gs2.log[-3:])

gs3 = engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs3.stage = {
    'L': engine.StageSlot(cardnumber='PL!S-bp5-005', active=True),
    'C': engine.StageSlot(cardnumber='PL!N-bp1-001', active=True),
    'R': engine.StageSlot(cardnumber='PL!S-bp6-006', active=True),
}
gs3.stage_entered_cardnumbers_this_turn = ['PL!N-bp1-001','PL!S-bp6-006']
eff2 = '<黄>か<緑>か<青>のうち、1つを選ぶ。ライブ終了時まで、自分のステージにいるこのターンに登場したメンバーのうち、『Aqours』以外のすべてのメンバーは選んだハートを1つ得る。'
engine.try_apply_effect_template(gs3, rng, cards, eff2, {'pos': 'L', 'source_cn': 'PL!S-bp5-005'})
print('heartpending', [p.get('kind') for p in gs3.pending], gs3.pending[0].get('target_positions') if gs3.pending else None)
if gs3.pending:
    engine.cmd_resolve_pending(gs3, cards, 0, '黄', rng)
print('heartdone', getattr(gs3.stage['C'], 'temp_hearts', {}), getattr(gs3.stage['R'], 'temp_hearts', {}), gs3.log[-3:])
PY
```

### 20260707m entered-or-moved required-any reduction

#### Internal smoke: `PL!SP-pb1-025` reduces required `<任意>` by entered/moved `5yncri5e!` members

Confirm that one entered and one moved `5yncri5e!` stage member reduce the live card's required `<任意>` by 2 total.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui import engine
from llocg_ui.db import load_cards_db

cards = load_cards_db(Path('.'))
gs = engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.stage = {
    'L': engine.StageSlot(cardnumber='PL!SP-bp5-014', active=True),
    'C': engine.StageSlot(cardnumber='PL!SP-bp5-017', active=True),
    'R': engine.StageSlot(cardnumber='PL!S-bp6-006', active=True),
}
gs.stage_entered_cardnumbers_this_turn = ['PL!SP-bp5-014']
gs.stage_moved_cardnumbers_this_turn = ['PL!SP-bp5-017']
gs.stage_moved_this_turn = True
eff = '自分のステージにいる、このターン中に登場、またはエリアを移動した『5yncri5e!』のメンバー1人につき、このカードを成功させるための必要ハートを<(任意)>減らす。'
engine.try_apply_effect_template(gs, random.Random(1), cards, eff, {'source_cn': 'PL!SP-pb1-025'})
print(getattr(gs, 'live_start_required_any_reduction_by_cn', {}), gs.log[-3:])
PY
```

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
