# AGENTS.md — Loveca / LLCG simulator 作業指示

## プロジェクト概要

このリポジトリは、ラブライブ！シリーズ オフィシャルカードゲーム（ラブカ / LLCG）のシミュレータ実装である。

主な作業対象は以下。

- ランタイム UI / engine 実装
- カード効果実装
- 効果 parser / matcher / resolver の一般化
- デバッグ起動コマンドの作成
- DB / compiled JSON / 画像 manifest の更新補助

このプロジェクトでは、カード1枚ごとの専用分岐を増やすのではなく、同型効果を拾える generic route / matcher / resolver に寄せることを最優先する。

---

## パス前提

作業ルート:

```bash
/Users/tekitou/Desktop/gsim/loveca
```

runtime 正本:

```text
./llocg_ui/
```

主要 runtime ファイル:

```text
./llocg_ui/server.py
./llocg_ui/engine.py
./llocg_ui/engine_effect.py
./llocg_ui/effects/
```

DB / compiled 正本:

```text
./llocg_db_out_full/cards_min_tokv1.csv
./llocg_db_out_full/cards_min_tokv1.json
./llocg_db_out_full/cards_compiled_v7h.json
```

runtime 修正で compiled DB を参照する場合、root 直下ではなく `./llocg_db_out_full/cards_compiled_v7h.json` を基準にする。

---

## 現在の重要前提

- 最新通過版を必ず土台にする。
- ユーザーが未適用と言ったパッチは正本扱いしない。
- 旧い ZIP や途中パッチがローカルに残っている前提で作業しない。
- 作業前に `git status` と変更対象ファイルの BUILD_TAG を確認する。
- 既存 helper / 常時 bonus 集計 / pending 経路を落とさない。
- `server.py` は UI / 表示 / state_json の正本。
- `engine.py` はフェイズ、pending、ライブ進行、特殊処理の正本。
- `engine_effect.py` は効果処理の入口。肥大化させず、実体は `effects/` 側へ寄せる。
- 新しい分割先として `effect_ext/` などの別フォルダを作らない。正式な分割先は `./llocg_ui/effects/`。

---

## コード編集方針

### 原則

1. カード番号専用分岐は禁止。
2. まず既存の generic route / registry / resolver / helper を調査する。
3. 既存 route に載せられる場合は、既存 route の拡張を優先する。
4. 新規 matcher を追加する場合は、同型カードを複数拾える形にする。
5. コメントや命名も、特定カード名ではなく効果ファミリー名・文型名で書く。
6. 既存の挙動確認済みカードを壊さない。
7. 表示修正と効果処理修正を混同しない。

### 典型的に避けること

避ける:

```python
if cardnumber == "PL!XXX-yyy-999":
    ...
```

許容される方向:

```python
# live-start: target stage member gains temporary icons
# condition: success zone count / green group count / live in progress predicate
```

### 特殊分岐が必要に見える場合

以下を先に行う。

1. DB の効果文を確認する。
2. `effects/registry.py` の既存 matcher を確認する。
3. `effects/live_start.py`, `effects/success_zone.py`, `effects/energy.py`, `effects/position.py` など意味単位の resolver を確認する。
4. `engine.py` の既存 pending / queue / live-start / live-success 特殊経路を確認する。
5. 同型カードが他にないか `cards_compiled_v7h.json` で検索する。
6. それでも一般化できない場合だけ、暫定 special として最小限にする。

---

## effects/ 配下の役割

```text
llocg_ui/effects/
  __init__.py
  registry.py       # matcher / rule table / effect text normalization
  helpers.py        # 共通 helper
  apply.py          # ext_key dispatch
  green_search.py   # 控え室検索 / required heart / group 条件
  topdeck.py        # topk / reorder / reveal / optional pick
  stage_triggers.py # 登場 / stage→green / leave-stage
  live_start.py     # live-start の blade / heart / score / required 操作
  success_zone.py   # success zone / live in progress / opponent comparison
  energy.py         # energy active / wait / energy deck
  position.py       # position change / formation
  special.py        # まだ一般化しきれていない例外
```

新規実装は、意味単位に応じて上記へ入れる。
`engine_effect.py` に大きな実装を戻さない。

---

## UI / pending 表示方針

- カード選択はカードリストで表示する。
- 効果モードは箇条書きや実行中効果のテキストを使う。
- 自動効果は確認ポップアップを出す。
- 1候補しかない場合でも、原則として選択 UI を出す。
- 確認ポップアップでは、実行中の効果だけを表示する。
- 複数効果を持つカードでも、未実行の別効果までフルテキスト表示しない。
- 同じ効果文を上段と下段で重複表示しない。
- 成功 / 未達は表示上わかるようにする。
- heart / blade overlay はカード個別ではなく共通 renderer に寄せる。
- 既存の texticons / token renderer を優先し、独自 glyph 表示を増やさない。

---

## デバッグコマンド方針


正本形式は次。

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

`DECK_CODE` wrapper は使わない。

### デバッグコマンド作成時の注意

- 対象カードを即座にプレイ / 解決できる状態にする。
- 必要エネルギーを足す。
- 必要な手札コスト用カードを足す。
- stage / green / success / deck top を不足なく入れる。
- 能力確認に不要な他の誘発はできるだけ消す。
- BODY 常時は、すでに stage に置いた状態で開始する。
- stage→green 誘発は、重ねプレイやバトンタッチで確実に起こせるようにする。
- LIVE 限定 / MEMBER 限定のテストでは、異種カードを混ぜてフィルタ漏れを確認する。
- エネルギー上限に引っかかる場合は、開始値が clamp される前提で書く。
- 成功ライブカード置き場に3枚以上置く初期状態は使わない。
- エール公開カードをライブセット時ドロー位置に直接置かない。必要なら `LLOCG_START_DECK_TOP` にダミーを前置きする。

---

## 作業記録 / デバッグメモ方針

このリポジトリではローカルファイルを直接編集する。
外部配布を前提にした古い運用は使わない。

作業記録は用途別に `docs/` 配下へ置く。

```text
docs/handoffs/  # 引き継ぎメモ
docs/debug/     # デバッグコマンド、実装確認メモ
docs/notes/     # 整理表、DB更新メモなど
```

root 直下へ作業メモ `.md` を増やさない。
root に残す Markdown は原則として `README.md` と `AGENTS.md` のみ。

実装した効果のデバッグコマンドは `docs/debug/` 配下へ追記する。
ユーザーが確認・監修する統合メモ `docs/debug/loveca_debug_commands_20260623.md` は、ユーザー指定の統合タイミング以外では直接編集しない。
通常の実装中は `docs/debug/loveca_debug_commands_current_updates_20260623.md` に現行更新分を追記し、統合指示が出たら統合メモへ移す。
「確認観点」だけでなく、環境変数を含む実行可能な個別起動コマンドを残す。

作業完了時は以下を報告する。

1. 変更した主なファイル
2. 実行した確認コマンドと結果
3. ファイル移動 / 削除 / バックアップ作成の有無
4. 未ステージまたは既存差分が残る場合はそのファイル

### BUILD_TAG

- 配布する各 `.py` の先頭付近に `BUILD_TAG` を入れる。
- 更新のたびに必ず変更する。
- 同日複数回更新する場合は末尾に `a`, `b`, `c` などを付けて一意にする。
- 例:

```python
BUILD_TAG = "live_start_conditional_stage_bonus_20260622g"
```

---

## 確認コマンド

変更対象に応じて `head -3` を出す。

例:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

head -3 ./llocg_ui/engine.py
head -3 ./llocg_ui/server.py
head -3 ./llocg_ui/effects/registry.py
head -3 ./llocg_ui/effects/live_start.py

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

---

## Git 運用

通常:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

git status
git add <changed files>
git commit -m "<message>"
git push origin main
```

force が必要な場合のみ:

```bash
git push --force-with-lease origin main
```

force push は明示的な理由があるときだけ使う。

---

## DB 更新方針

DB 更新は runtime 修正とは分ける。

標準工程:

1. 作業用フォルダで wiki 取得 / normalize / manifest 作成
2. `llocg_sim_tool_v7.py compile` で compiled DB 作成
3. `./llocg_db_out_full/` に反映
4. 画像 fetch は別工程

既存 `./llocg_db_out_full/` に直接 `all` をかけない。
毎回新しい作業用 outdir を使う。

---

## ルール確認

ルール解釈に関わる変更では、必要に応じて `LLCrule251121.pdf` を確認する。

特に以下は注意する。

- 成功ライブカード置き場が3枚以上になると勝敗処理に関わるため、デバッグ初期状態で3枚以上置かない。
- メンバー下に置かれたエネルギーは通常のエネルギー置き場とは別管理になる。
- 発生源、最終情報、解決時参照が絡む効果では、解決時条件判定か誘発時固定かを確認する。

---

## 作業完了時の自己チェック

作業完了前に必ず確認する。

- [ ] 最新通過版を土台にしたか
- [ ] カード番号専用分岐を増やしていないか
- [ ] 同型効果を複数拾える matcher / resolver になっているか
- [ ] 既存 helper / 常時 bonus 集計を落としていないか
- [ ] UI 表示と効果処理を混同していないか
- [ ] pending 表示が実行中効果だけになっているか
- [ ] 変更ファイルすべての BUILD_TAG を更新したか
- [ ] `python3 -m py_compile` を通したか
- [ ] 実装分の個別デバッグコマンドを `docs/debug/` の現行更新ファイルへ追記したか
- [ ] git 反映コマンドを提示したか
