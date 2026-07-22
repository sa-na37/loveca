# Loveca latest two decks runtime debug 20260721

## 対象デッキ

`llocg_db_out_full/decklists` の更新日時が新しい順で以下2件を対象にした。

- `deck_444782643669fb371f81.tsv`
  - deck code: `7U1CT`
  - name: `ポムポムミアSaint`
  - simulator code: `444782643669fb371f81`
- `deck_49921c3081c71d2fea40.tsv`
  - deck code: `540L5`
  - name: `トリオ名古屋`
  - simulator code: `49921c3081c71d2fea40`

## 実施内容

- 1デッキ用 `llocg_ui.server.App` を直接初期化し、通常のデッキ読込、マリガン、MAIN、LIVE_SET、LIVE_CONFIRM、YELL、LIVE_ATTEMPT、LIVE_RESOLVE を自動操作で複数 seed 実行。
- 2デッキ用 `LegacyUIAdapter` / `DualMatchEngine` を直接初期化し、マリガンから複数ターンの中央フェイズ進行、ライブセット、パフォーマンス、ライブ勝敗判定ログを確認。
- 2デッキ終了判定は短縮 state で P1勝利 / P2勝利 / 引き分け / 継続の4ケースを確認。
- 実サーバ起動確認として、1デッキ用 `run_llocg_ui_web.py` と2デッキ用 `run_llocg_dual_v2.py` をそれぞれローカル起動し、状態APIが対象デッキを読めることを確認。

## 修正した問題

### 1. ライブ開始時の任意エネルギーコスト不足が `[ERR]` だけになる

発生:

- `PL!HS-PR-022` などの `live_start_pay_effect` / `live_start_blade` 系で、エネルギー0の状態でも自動操作が `pay` を選べた。
- 旧挙動では `[ERR] ability: insufficient energy for [E]1` のみが残り、任意効果を適用しなかった理由が UI/pending で分かりにくい。

対応:

- `llocg_ui/engine.py`
- `BUILD_TAG = live_start_optional_pay_insufficient_ack_20260721a`
- 支払えない場合は `[SKIP]` ログと `message_ack` を出し、発生源・任意コスト不足・現在のアクティブエネルギーを表示する。
- カード番号専用分岐ではなく `live_start_pay_effect` / `live_start_blade` 共通経路で修正。

確認:

- 1デッキ複数 seed 再走で、任意コスト不足は `[ERR]` ではなく不足理由つき確認ログへ変わることを確認。

### 2. 2デッキで0枚ライブセット時にライブ成否が記録されない

発生:

- `LIVE_CONFIRM -> LIVE_RESOLVE` でライブがない場合、既存の no-live 検出は `set_zone` が事前に非空だったケースだけを対象にしていた。
- 0枚ライブセットでは旧Appが `last_attempt_result` を出さないため、2デッキ側が「ライブ成否を旧Appから取得できません」となる可能性があった。

対応:

- `llocg_dual_v2/server.py`
- `BUILD_TAG = llocg_dual_v2_game_result_state_authority_20260721a`
- `LIVE_CONFIRM` から `LIVE_RESOLVE` へ進み、かつ `set_zone` が空なら、事前の `set_zone` が空でも no-live failure として記録する。

確認:

- 2デッキ直接進行で、0枚ライブセットを含むターンが即例外にならずライブ勝敗判定まで進むことを確認。

### 3. 2デッキ終了判定が App 側 success_zone に依存していた

発生:

- `_game_result_after_success_moves()` が embedded App の `success_zone` を見ていた。
- 2デッキの正本は `MatchState.players[*].success_zone` なので、判定境界で App 表示側が一時的に遅れると終了判定が不安定になりうる。

対応:

- `llocg_dual_v2/server.py`
- 終了判定を `self.engine.state.players[*].success_zone` 基準へ変更。

確認:

```text
p1_win    -> winner 0 / P1_WIN
p2_win    -> winner 1 / P2_WIN
draw      -> winner None / DRAW
no_result -> winner None / ""
```

## 確認できたこと

- 両デッキとも `App(root=llocg_db_out_full, deck_code=<deck_id>)` で初期化できる。
- 1デッキ側では、ライブ開始時、エール時、ライブ成功時の `auto_order` / `message_ack` / `show_revealed_cards_ack` / `live_attempt_summary_ack` が複数回発生し、ログに残る。
- YELLログには公開カード、ドローアイコン枚数、追加ドロー、ライブ成否、スコア内訳が残る。
- 2デッキ側では中央ログに `[LIVE SET]`, `[PERFORMANCE]`, `[ATTEMPT RESULT]`, `[JUDGMENT 8.4.x]`, `[PHASE]` が残る。
- 2デッキ終了判定の P1勝利 / P2勝利 / 引き分け / 継続は短縮 state で確認済み。

## 未対処 / 要追加確認

- 2デッキ自然完走を完全自動で何度も回すには、盤面側の対象選択 pending をより賢く選ぶテストドライバが必要。今回の簡易ドライバでは、一部の対象選択を中央NEXTで踏んで `このポップアップは盤面上で対象・選択肢を指定して解決してください` になるケースが残った。
- 長時間の2デッキ直接走行では、Undo用の深い snapshot が重くなり実行時間が伸びた。通常UI操作では必要な履歴だが、自動耐久テストでは履歴抑制または専用テストドライバを作る方がよい。
- 1デッキ側では成功ライブ置き場が3枚を超えても単体シミュが明示 GAME_OVER にならない。今回のユーザー指定では2デッキ終了を主確認対象としたため、単体シミュの勝利終了表示は別件として扱う。

## 実行確認

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./llocg_dual_v2/core.py ./llocg_dual_v2/server.py ./run_llocg_dual_v2.py ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
git diff --check
```

結果: どちらもOK。

実サーバ起動:

- 1デッキ: `http://127.0.0.1:8811/state` で `deck_code=444782643669fb371f81` / `phase=MULLIGAN` / `hand=6` / `deck=54` を確認。
- 2デッキ: `http://127.0.0.1:8812/match_state` で P1 `444782643669fb371f81`、P2 `49921c3081c71d2fea40`、`phase=MULLIGAN_FIRST` を確認。
