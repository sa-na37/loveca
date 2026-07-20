# Loveca dual v2 root ACK/cardinfo smoke 20260717

対象 BUILD_TAG:

- `llocg_dual_v2_root_ack_cardinfo_20260717v`
- `llocg_dual_v2_success_move_canonical_text_20260717w`
- `llocg_dual_v2_no_live_filter_boundary_20260717x`
- `llocg_dual_v2_central_single_auto_order_20260717y`

## 確認対象

- YELL公開確認のACKを、dual側の一時抑制だけでなく、単体UI側の正式フラグ `yell_reveal_acknowledged_this_live` にも反映する。
- ACK後のポップアップ掃除で、正式フラグを誤って消さない。
- カード詳細APIが単体UIの期待する `abilities` を返し、「効果なし」表示に落ちない。
- 旧DOM修復スクリプトを使わず、APIレスポンスでカード詳細を直す。
- PL!S-bp2-024 の「成功ライブカード置き場に置くことができない」常時効果を、dual v2 の成功ライブ移動処理でも正本DBから判定する。
- LIVE_CONFIRMで非LIVEカードだけが残っていた場合、成否フラグ未取得エラーにせず「ライブなし/失敗」としてパフォーマンスを完了する。
- 単一候補の `auto_order` は、中央NEXTで1段だけ解決する。複数候補は選択UIに残す。

## 実行確認

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_dual_v2/*.py ./run_llocg_dual_v2.py
```

結果: 成功。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

結果: 48 tests OK。

2026-07-17 追加確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_canonical_db_text_can_forbid_success_zone_move \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_card_text_can_forbid_success_zone_move
```

結果: 2 tests OK。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

結果: 49 tests OK。

2026-07-17 追加確認2:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_central_next_resolves_single_auto_order_pending \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_non_live_set_card_completes_performance_without_attempt_result
```

結果: 2 tests OK。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

結果: 51 tests OK。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_llocg_dual_v2.py --deck1 7QEC8 --deck2 1RCBL --seed 17 --host 127.0.0.1 --port 18181 --debug
```

ブラウザ/API確認:

- 初期画面: 上下iframe、中央UNDO/NEXT、BUILD_TAG表示あり。
- 中央操作のみで、マリガン、通常フェイズ、双方1枚ライブセット、先攻/後攻パフォーマンス、ライブ勝敗判定、ターン終了処理まで到達。
- 実プレイ中に発見した停止点:
  - 単一候補 `auto_order` が中央NEXTで進まない。
  - P2がMEMBERをライブセットしたとき、LIVE_CONFIRMで全カードが控え室へ落ちたあと成否未取得エラーになる。
- 上記2点を修正後、同条件でTURN_ENDまで通過。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from types import SimpleNamespace
from llocg_dual_v2.server import LegacyUIAdapter, PlayerViewRuntime

app = SimpleNamespace(
    root=Path('.'),
    outdir=Path('.'),
    cards_db={},
    gs=SimpleNamespace(
        deck=[], hand=[], set_zone=[], success_zone=[],
        resolve_zone=[], green_room=[], stage={},
    ),
)
rt = PlayerViewRuntime(key='p1', player_id=0, label='P1', color='', app=app)
adapter = object.__new__(LegacyUIAdapter)
adapter.players = {'p1': rt}
adapter._detail_db_cache = None
payload = adapter.card_info_payload('p1', 'PL!S-bp2-024')
print(payload['cn'])
print(bool(payload.get('effect')))
print(bool(payload.get('abilities')))
print(payload.get('effect', '')[:80].replace('\n', ' / '))
PY
```

結果:

```text
PL!S-bp2-024
True
True
<常時> / このカードは成功ライブカード置き場に置くことができない。 / <ライブ成功時> / カードを2枚引き、手札を1枚控え室に置く。
```

## 未確認

完全な `llocg_ui.App` 起動スモークは、現環境に `sim_decks/` または `decklists/` が無く、デッキコード `7QEC8` のデッキファイルを解決できなかったため未実施。

次回、実デッキファイルがある環境では `run_llocg_dual_v2.py` 起動後に以下を目視確認する。

- ライブ中のYELL公開確認を閉じた後、成功時能力解決後に同じYELL確認が再表示されない。
- カード詳細に効果文が表示され、「効果なし」へ落ちない。
- ライブ成功/失敗、成功時能力、スコア比較、成功ライブ移動が順に進む。

## 20260719 対戦終了通知 / 中断保存・再開読込

BUILD_TAG:

```text
llocg_dual_v2_suspend_resume_gameover_notice_20260719a
```

実装内容:

- 対戦終了状態 `GAME_OVER` で `game_over_message` を返すようにし、中央画面に対戦終了通知を表示。
- 中央画面に `中断保存` / `再開読込` ボタンを追加。
- `/suspend_state` で盤面・乱数・各プレイヤー状態を含む中断JSONを保存。
- `/resume_state` で中断JSONから保存地点へ復帰。復帰後のUNDO履歴は空にし、同じ保存地点から分岐を繰り返せる状態にする。
- 実Appの関数系内部属性はファイル保存に不要なため、中断データから除外。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_dual_v2/*.py ./run_llocg_dual_v2.py
```

結果: OK。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

結果: 54 tests OK。

追加確認:

- 片側が3枚目の成功ライブカードを置いた場合、`GAME_OVER` / 勝者ID / 勝利メッセージが返ることを確認。
- 双方が同時に3枚目の成功ライブカードを置いた場合、`DRAW` / 引き分けメッセージが返ることを確認。
- 中断保存データから復帰後、保存時点の手札・ステージ・フェイズへ戻り、別のステージ位置へプレイする分岐が可能なことを確認。

Web/API smoke:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_llocg_dual_v2.py --deck1 7QEC8 --deck2 1RCBL --seed 17 --host 127.0.0.1 --port 18181 --debug
```

別ターミナル:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

curl -s http://127.0.0.1:18181/suspend_state -o /tmp/loveca_dual_suspend_smoke.json -w '%{http_code} %{size_download}\n'

curl -s -X POST http://127.0.0.1:18181/match_action \
  -H 'Content-Type: application/json' \
  -d '{"action":"NEXT","payload":{"indices":[]}}'

curl -s -X POST http://127.0.0.1:18181/resume_state \
  -H 'Content-Type: application/json' \
  --data-binary @/tmp/loveca_dual_suspend_smoke.json
```

結果:

- `/suspend_state`: `200`、中断JSON生成。
- `NEXT`: `MULLIGAN_FIRST` から `MULLIGAN_SECOND` へ進行。
- `/resume_state`: `200`、`MULLIGAN_FIRST` へ復帰。ログに `[RESUME]` 追記、`history_depth=0`。

注意:

- 中断JSONはローカルシミュレーター用の復元データを含むため、同じリポジトリ/同じ実装世代で使う前提。外部から入手した中断JSONは読み込まない。

## 20260720 同値両者勝利時の成功置き場2枚処理修正

BUILD_TAG:

```text
llocg_dual_v2_tied_success_two_zone_block_20260720a
```

修正内容:

- 8.4.7.1 の成功移動禁止判定を、現在のライブ置き場/ライブセット枚数ではなく、成功ライブカード置き場の枚数で判定するよう修正。
- 同値両者勝利時、成功ライブカード置き場が2枚のプレイヤーは成功ライブを移動しない。
- `simultaneous_third_success_is_draw` は通常の 8.4.7 成功移動テストとして不適切なため、通常移動では同時3枚目DRAWを作らないテストへ置換。
- 1.2.1.2 の同時3枚以上DRAW判定は、特殊効果などで実際に同時3枚以上になった場合の保険として保持。
- 再発防止のため、`docs/notes/loveca_runtime_implementation_rules_20260708.md` に 2デッキ対戦ルール注意を追記。

対象確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_tie_both_win_success_zone_two_player_does_not_move \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_tie_both_win_depends_on_success_zone_not_live_set_count \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_draw_result_remains_as_simultaneous_three_success_safety \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_third_success_winner_is_announced
```

結果: 4 tests OK。

## 20260720 ルール再確認 / 1デッキ中断保存・再開読込反映

BUILD_TAG:

```text
single_suspend_resume_and_dual_rule_recheck_20260720a
```

確認内容:

- `docs/notes/loveca_runtime_implementation_rules_20260708.md` の 2デッキ対戦ルール注意を再確認。
- 8.4.6.2: スコア同値時は両方のプレイヤーがライブに勝利する。
- 8.4.7.1: 両方のプレイヤーが勝利している場合、成功ライブカード置き場が2枚のプレイヤーは成功ライブカード置き場へカードを移動しない。
- 判定軸は成功ライブカード置き場の枚数であり、ライブセット枚数/現在ライブ置き場枚数ではない。
- 1.2.1.2 の同時3枚以上DRAW判定は保険として保持。

1デッキ用反映:

- `llocg_ui/server.py` に `/suspend_state` と `/resume_state` を追加。
- 1デッキ用UIのトップバーに `中断保存` / `再開読込` を追加。
- 中断JSONには `gs`、乱数状態、公開ビュー用の公開/確認同期状態を保存。
- 再開時は保存地点へ復帰し、UNDO履歴を空にし、ログへ `[RESUME]` を追記。
- 公開ビューには再開後の更新通知を飛ばす。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/server.py ./llocg_ui/engine.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py ./run_llocg_ui_web.py ./llocg_dual_v2/*.py ./run_llocg_dual_v2.py
```

結果: OK。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_tie_both_win_success_zone_two_player_does_not_move \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_tie_both_win_depends_on_success_zone_not_live_set_count \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_draw_result_remains_as_simultaneous_three_success_safety \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_third_success_winner_is_announced
```

結果: 4 tests OK。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

結果: 55 tests OK。

1デッキWeb/API smoke:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 18182 --debug
```

別ターミナル:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

curl -s http://127.0.0.1:18182/suspend_state -o /tmp/loveca_single_suspend_smoke.json -w '%{http_code} %{size_download}\n'

curl -s -X POST http://127.0.0.1:18182/cmd \
  -H 'Content-Type: application/json' \
  -d '{"cmd":"mulligan_next","payload":{"indices":[]}}'

curl -s -X POST http://127.0.0.1:18182/resume_state \
  -H 'Content-Type: application/json' \
  --data-binary @/tmp/loveca_single_suspend_smoke.json
```

結果:

- `/suspend_state`: `200`、中断JSON生成。
- `mulligan_next`: `MULLIGAN` から `MAIN` へ進行。
- `/resume_state`: `200`、`MULLIGAN` / `turn=0` / `hand=6` / `deck=54` へ復帰。ログ末尾に `[RESUME]`。

注意:

- 1デッキ中断JSONもローカルシミュレーター用の復元データを含むため、同じリポジトリ/同じ実装世代で使う前提。外部から入手した中断JSONは読み込まない。

## 2026-07-20 dual中央バーUI被り修正

対象BUILD_TAG:

- `llocg_dual_v2_center_bar_grid_no_overlap_20260720a`

修正内容:

- dual画面中央部の `#divider` を3カラムgridに変更し、左からステータス表示、中央フェーズ表示、右操作ボタンに固定。
- `#controls` の絶対配置を廃止し、フェーズ表示やステータスと重ならない通常gridセルへ移動。
- `#phaseBanner` / `#controls` / `#requestStatus` に `grid-row:1` を明示し、ブラウザの自動配置で中央帯内の別行へ流れないようにした。
- 中央帯の高さは `74px` のまま維持。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_dual_v2/*.py ./run_llocg_dual_v2.py
```

結果: OK。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

結果: 55 tests OK。

ブラウザ実寸確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_llocg_dual_v2.py --deck1 7QEC8 --deck2 1RCBL --seed 17 --host 127.0.0.1 --port 18181 --debug
```

`http://127.0.0.1:18181/dual` を 1280x720 表示で確認。

- `#shell` rows: `323px 74px 323px`
- `#divider`: `y=323`, `h=74`
- `#phaseBanner`: `y=325`, `h=70`, divider内に収まる
- `#controls`: `y=344.52`, `h=30.95`, divider内に収まる
- `#controls` computed position: `static`
- `phaseBanner` / `controls` / `requestStatus` はすべて divider 内
- `phaseBanner` と `controls` の重なりなし
- `requestStatus` と `controls` の重なりなし
- `requestStatus` と `phaseBanner` の重なりなし

注意:

- 確認中のブラウザ再読込・停止タイミングにより、開発サーバーログに `BrokenPipeError` / `ConnectionResetError` が出る場合がある。画面再読込やブラウザ側の接続切断に伴うログで、今回の中央バー配置修正とは別件。

## 2026-07-20 dual UI追加監査 / NoImage接続確認

対象BUILD_TAG:

- `llocg_dual_v2_ui_audit_noimage_fallback_20260720a`

確認・修正内容:

- dual内プレイヤーラベルと各プレイヤーUIの `#topBar` が被る可能性を確認。
- `body.dualPlayerView` に `--dualLabelW` を追加し、ラベル幅とtopBar退避幅を同じCSS変数で管理するよう修正。
- ラベルは固定幅、1行、省略表示にし、長い日本語ラベルでもtopBarに重なりにくくした。
- dual側の `/p1/img` / `/p2/img` 配信について、カード背面・NoImage候補の探索を明示化。
- 通常カード画像が見つからない場合、`rt.app.img.find()` が失敗しても `NoImage.PNG` へ落ちる保険を追加。

HTTP確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_llocg_dual_v2.py --deck1 7QEC8 --deck2 1RCBL --seed 17 --host 127.0.0.1 --port 18181 --debug
```

別ターミナル:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

curl -s -D /tmp/loveca_dual_noimage_headers2.txt \
  -o /tmp/loveca_dual_noimage_body2.bin \
  'http://127.0.0.1:18181/p1/img?cn=NO_SUCH_CARD_20260720'

curl -s -D /tmp/loveca_dual_back_headers2.txt \
  -o /tmp/loveca_dual_back_body2.bin \
  'http://127.0.0.1:18181/p1/img?cn=__BACK__'

curl -s -D /tmp/loveca_dual_energy_headers2.txt \
  -o /tmp/loveca_dual_energy_body2.bin \
  'http://127.0.0.1:18181/p1/img?cn=__ENERGY__'
```

結果:

- `NO_SUCH_CARD_20260720`: `200 image/png`、`llocg_db_out_full/card_images/NoImage.PNG` と完全一致。
- `__BACK__`: `200 image/png`、`llocg_db_out_full/card_images/back.png` と完全一致。
- `__ENERGY__`: `200 image/png`、この時点ではエネルギー専用画像ファイルがローカルに無かったため `NoImage.PNG` と完全一致。その後の `deck_center_energy_plain_fallback_20260720a` で、エネルギーはNoImageではなく専用画像または透明PNGへ戻した。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_dual_image_helpers_find_back_energy_and_noimage_fallback \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_scoped_html_reserves_label_width_from_topbar \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_shell_html_has_suspend_resume_and_game_over_notice
```

結果: 3 tests OK。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

結果: 57 tests OK。

注意:

- アプリ内ブラウザでの追加DOM測定はタブ接続がタイムアウトしたため未完了。HTTP応答とHTML/CSS単体確認では、NoImage接続とラベル/topBar被り回避は確認済み。

## 2026-07-20 1デッキ/2デッキ共通 山札枠中央寄せ / エネルギー無地フォールバック

対象BUILD_TAG:

- 1デッキ: `deck_center_energy_plain_fallback_20260720a`
- 2デッキ: `llocg_dual_v2_deck_center_energy_plain_fallback_20260720a`

修正内容:

- エネルギー下敷き表示用の `__ENERGY__` は、`energy.png` / `energy.jpg` / `energy.jpeg` / `energy.webp` を `llocg_db_out_full/card_images`、`card_images`、ルート周辺から探索する。
- エネルギー専用画像が無い場合は、NoImageではなく以前と同じ透明PNGへ戻す。
- 山札表示は `renderTopCard(..., {useStandardSize:true})` の標準カードサイズを使いつつ、枠内の `availW` / `availH` を超えない倍率で縮小し、枠中央に収める。
- 山札描画は1デッキ用 `llocg_ui/server.py` の共通UIで修正しているため、dualのiframe内表示にも同じ修正が適用される。

HTTP確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 18182 --debug
python3 ./run_llocg_dual_v2.py --deck1 7QEC8 --deck2 1RCBL --seed 17 --host 127.0.0.1 --port 18181 --debug
```

別ターミナル:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

curl -s -D /tmp/loveca_single_energy_headers3.txt \
  -o /tmp/loveca_single_energy_body3.bin \
  'http://127.0.0.1:18182/img?cn=__ENERGY__'

curl -s -D /tmp/loveca_dual_energy_headers3.txt \
  -o /tmp/loveca_dual_energy_body3.bin \
  'http://127.0.0.1:18181/p1/img?cn=__ENERGY__'

curl -s -D /tmp/loveca_single_back_headers3.txt \
  -o /tmp/loveca_single_back_body3.bin \
  'http://127.0.0.1:18182/img?cn=__BACK__'

curl -s -D /tmp/loveca_dual_back_headers3.txt \
  -o /tmp/loveca_dual_back_body3.bin \
  'http://127.0.0.1:18181/p1/img?cn=__BACK__'
```

結果:

- 1デッキ `__ENERGY__`: `200 image/png`、66 bytes。
- 2デッキ `__ENERGY__`: `200 image/png`、66 bytes。
- 1デッキ/2デッキの `__ENERGY__` 応答は完全一致。現時点では専用画像が無いため透明PNG。
- 1デッキ `__BACK__`: `llocg_db_out_full/card_images/back.png` と完全一致。
- 2デッキ `__BACK__`: `llocg_db_out_full/card_images/back.png` と完全一致。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/server.py ./llocg_dual_v2/*.py ./run_llocg_dual_v2.py

python3 -m unittest \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_dual_image_helpers_find_back_energy_and_noimage_fallback \
  llocg_dual_v2.tests.test_legacy_adapter_transactions.LegacyAdapterTransactionTests.test_shell_html_has_suspend_resume_and_game_over_notice
```

結果:

- py_compile OK。
- 2 tests OK。
