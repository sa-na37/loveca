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

### 20260721 GitHub release guide and package refresh

※20260721内部確認: `README.md` の初回起動ガイドへ、配布者から `GitHub Release URL` と `loveca-ui-assets.zip` を受け取っている前提の本体zip取得手順を追加。Release本文 `_codex_outputs/github_release/loveca-release-notes-20260721.md` も、GitHubページ上で `Assets` からOS別zipを選び、別配布UIバンドルを `loveca` 直下へ置く流れに更新。公開用本体zip3種を再生成し、本体zip内に画像が0件、README内にGitHub Release手順が含まれることを確認。UI画像バンドルは別配布用として再生成し、GitHub Releaseには添付していない。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 ./tools/build_loveca_distribution.py --target macos --output ./_codex_outputs/github_release/loveca-macos-20260721.zip
python3 ./tools/build_loveca_distribution.py --target windows --output ./_codex_outputs/github_release/loveca-windows-20260721.zip
python3 ./tools/build_loveca_distribution.py --target source --output ./_codex_outputs/github_release/loveca-source-20260721.zip
python3 ./tools/build_loveca_distribution.py --target ui-assets --output ./_codex_outputs/github_release/loveca-ui-assets-20260721.zip
shasum -a 256 _codex_outputs/github_release/loveca-windows-20260721.zip _codex_outputs/github_release/loveca-macos-20260721.zip _codex_outputs/github_release/loveca-source-20260721.zip _codex_outputs/github_release/loveca-ui-assets-20260721.zip > _codex_outputs/github_release/SHA256SUMS-20260721.txt
python3 -m py_compile ./loveca_app/assets.py ./loveca_app/main.py ./tools/build_loveca_distribution.py
git diff --check -- README.md _codex_outputs/github_release/loveca-release-notes-20260721.md tools/build_loveca_distribution.py loveca_app/assets.py loveca_app/main.py
```

確認結果:

- `loveca-windows-20260721.zip`: 98 files / image 0 / README GitHub guideあり
- `loveca-macos-20260721.zip`: 98 files / image 0 / README GitHub guideあり
- `loveca-source-20260721.zip`: 140 files / image 0 / README GitHub guideあり
- `loveca-ui-assets-20260721.zip`: image 13 / 別配布用
- GitHub draft release `v2026.07.21` は draft のまま、添付は `loveca-windows-20260721.zip`, `loveca-macos-20260721.zip`, `loveca-source-20260721.zip`, `SHA256SUMS-20260721.txt` の4件。公開後、`SHA256SUMS-20260721.txt` は利用者向けには不要としてRelease添付とREADME/Release本文から除外。

### 20260721 RM rarity image release hotfix

※20260721内部確認: レアリティRM画像が表示されない件に対応。カード番号専用分岐ではなく、画像名のレアリティ検出と探索を汎用化し、`-RM` / `_RM` / 空白区切りの画像名を同じ候補として扱うようにした。公式画像manifest生成でも、末尾トークンを既知レアリティに限定してRMを検出し、カード番号末尾の `001` などを誤ってレアリティ扱いしないよう補正。アプリ本体のカード画像APIは画像未取得時に404で空白にせず、`NoImage.PNG` があれば返すようにした。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./llocg_ui/images.py ./loveca_app/core.py ./loveca_app/web.py ./llocg_db_tool_v7.py ./tools/build_loveca_distribution.py
python3 ./tools/build_loveca_distribution.py --target macos --output ./_codex_outputs/github_release/loveca-macos-20260721.zip
python3 ./tools/build_loveca_distribution.py --target windows --output ./_codex_outputs/github_release/loveca-windows-20260721.zip
python3 ./tools/build_loveca_distribution.py --target source --output ./_codex_outputs/github_release/loveca-source-20260721.zip
git diff --check -- README.md _codex_outputs/github_release/loveca-release-notes-20260721.md llocg_ui/images.py loveca_app/core.py loveca_app/web.py llocg_db_tool_v7.py
```

確認結果:

- `infer_rarity_from_filename('PL!N-bp1-001-RM.png') -> RM`
- `infer_rarity_from_filename('PL!N-bp1-001_RM.png') -> RM`
- `split_display_card_and_rarity('PL!N-bp1-001') -> ('PL!N-bp1-001', '')`
- 一時フォルダ上の `PL!N-bp1-001_RM.png` を `ImageLocator.find(..., rarity='RM')` で解決。
- アプリ側 `no_image_path()` が `NoImage.PNG` を返すことを確認。
- 公開用zip3種は画像0件、README内に `SHA256SUMS` 表記なし、RM修正BUILD_TAG入り。

### 20260721 reprint rarity image fetch expansion mismatch hotfix

※20260721内部確認: 再録/並行レアリティ画像の取得時に、画像URLのエキスパンションフォルダとカード番号内のエキスパンション部が一致しないことで `RM` / `SECL` / `L+` 相当画像を取り逃がす可能性を確認して修正。原因は、manifest処理が通常画像1枚の成功で打ち切られ、同一カード番号の再録系manifest entryを処理しない場合があること、およびmanifest entryが失敗した場合に「通常画像成功済み」のためフォルダ横断heuristicへ進まないこと。修正後は `L2` / `SECL` / `RM` / `SRL` を再録系として扱い、manifestに載っている再録系レアリティは通常画像成功後も処理する。再録系manifest entryが失敗した場合は、カード番号由来フォルダだけでなく既知フォルダ/商品registryフォルダを横断して不足レアリティだけ再探索する。manifest生成側も、更新対象が120枚以下のときカード番号検索で再録系画像を補完し、画像URL側の実フォルダを保存する。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./llocg_db_tool_v7.py ./llocg_fetch_all_card_images.py ./llocg_update_database.py
```

内部smoke結果:

- `infer_rarity_from_filename('PL!N-bp1-001_RM.png') -> RM`
- `infer_rarity_from_filename('PL!S-bp5-SECL.png') -> SECL`
- `infer_rarity_from_filename('PL!SP-pb1-026-L+.png') -> L2`
- synthetic official HTML から、カード番号側 `bp1` に対して画像URLフォルダ `BP09` の `RM` をmanifest entryとして抽出。
- synthetic official HTML から、`PL!S-bp5-021` に対して画像URLフォルダ `BP07` の `SECL` をmanifest entryとして抽出。
- synthetic official HTML から、`PL!SP-pb1-026` に対して画像URLフォルダ `PBSP02` の `L2` をmanifest entryとして抽出。
- fetcherにて、`L` manifest取得成功後に `L2` manifestが失敗しても、registry由来の `BP09` フォルダ横断で `PL!N-bp1-001-L2.png` を取得できることを確認。

### 20260721 Windows launcher encoding hotfix

※20260721内部確認: Windowsで `launch_loveca.bat` 実行時に `'ca' は、内部コマンドまたは外部コマンド...` や文字化けした日本語断片が表示される件に対応。原因は `.bat` 内のUTF-8日本語echoがcmdのコードページによって安全に解釈されず、文字化けした断片がコマンド扱いになる可能性。`launch_loveca.bat` をASCIIのみへ変更し、`python` 実行失敗時だけ `py -3` へfallbackする単純な構造にした。

確認結果:

- `launch_loveca.bat` の全byteがASCII範囲内であることを確認。
- ランチャー内容は `python .\run_loveca_app.py --window-mode app`、失敗時に `py -3 .\run_loveca_app.py --window-mode app` の順で実行。

### 20260721 Windows update dependency bootstrap hotfix

※20260721内部確認: Windows配布版でデータ更新開始直後、`llocg_build_preview_manifest_from_x.py` の `import requests` が `ModuleNotFoundError: No module named 'requests'` で停止する件に対応。原因は、Python本体のみ導入された利用者環境に更新用追加パッケージ `requests` / `beautifulsoup4` / `lxml` / `pandas` が入っていないこと。`llocg_update_database.py` の開始直後に必要パッケージを確認し、不足時は同じPython環境へ `pip install` してから更新を続行する。pipがない場合は `ensurepip` を試し、通常install失敗時は `--user` で再試行する。ユーザー操作なしで更新を進めるため、更新確認UIとREADMEには初回更新時にPython追加部品を導入する場合がある旨を追記。

確認結果:

- `python3 -m py_compile ./llocg_update_database.py ./loveca_app/core.py ./loveca_app/web.py` OK。
- ローカル環境の不足なしパスで `ensure_update_python_dependencies(allow_install=False)` が成功。
- updater help に `--skip-dependency-install` が表示されることを確認。

### 20260721 seeded HTTP cache distribution

※20260721内部確認: 配布版初回更新時の429が重い件に対応。`llocg_db_out_full/_http_cache` は337ファイル/約10MBで、商品ページ/更新用HTMLキャッシュとして配布可能なサイズ。カード画像は引き続き同梱せず、配布ビルダーで `_http_cache` の `.html` / `.json` / `.txt` だけを公開zipへ入れる専用経路を追加した。これにより、利用者初回更新ではキャッシュ済みページを優先し、未キャッシュの新規ページだけ外部取得する。

確認観点:

- 公開zipに `llocg_db_out_full/_http_cache` が含まれる。
- 公開zip内の画像ファイル数は引き続き0件。
- UI画像バンドル/カード画像はGitHub公開zipには含めない。

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

### 20260721 Tier 3 P1 completion

※20260721内部確認: P1残件 `PL!S-bp3-006#A01` / `PL!S-bp6-003#A01` / `PL!S-pb1-006#A01` / `PL!-bp5-111#A01` を確認。カード番号専用分岐ではなく、複合起動コスト、ステージ→控え室→元エリア登場、手札LIVE公開コスト、相手任意手札discard、相手ウェイト人数方式の汎用 route と pending resolver へ接続した。engine API で主要分岐を確認し、HTTP API で各カードの代表経路を確認済み。発生源なし・自動効果の無言処理・複合コストの一部落ち・相手個別カードstate要求の再発がないことを確認。

#### PL!S-bp3-006#A01 起動: 自身WAIT+手札discard → 他Aqours控え室 → コスト+2登場

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
export LLOCG_START_STAGE_C='PL!S-bp3-006'
export LLOCG_START_STAGE_L='PL!S-bp3-001'
export LLOCG_START_HAND='PL!S-bp5-111'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_GREEN='PL!S-bp6-006,PL!S-bp3-004'
export LLOCG_START_DECK_TOP='PL!S-bp5-001,PL!S-bp5-002,PL!S-bp5-003'
export LLOCG_START_ENERGY_ACTIVE=0
export LLOCG_START_ENERGY_WAIT=0
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: 起動直後に `C.active true -> false` となり、自身WAITコストが落ちない。手札discard pending は `source_cn=PL!S-bp3-006` と後続効果を保持する。手札1枚を控え室に置いた後、`L` の他Aqoursを控え室へ置く pending が出る。`PL!S-bp3-001`（コスト15）を選ぶと、控え室候補はコスト17のAqours `PL!S-bp6-006` のみ。選択後、元エリア `L` に登場し、登場時効果も通常通り解決し、pending は空。

#### PL!S-bp6-003#A01 起動: E2+手札discard → 任意で他Aqours控え室 → コスト+2登場

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
export LLOCG_START_STAGE_C='PL!S-bp6-003'
export LLOCG_START_STAGE_L='PL!S-bp3-001'
export LLOCG_START_HAND='PL!S-bp5-111'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_GREEN='PL!S-bp6-006,PL!S-bp3-004'
export LLOCG_START_DECK_TOP='PL!S-bp5-001,PL!S-bp5-002,PL!S-bp5-003'
export LLOCG_START_ENERGY_ACTIVE=3
export LLOCG_START_ENERGY_WAIT=0
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: 起動直後に `energy_active 3 -> 1`、`energy_wait 0 -> 2` となり、E2コストが手札discard routeに飲まれない。手札discard後のステージ選択 pending は `L` と `skip` を持つ。`skip` では後続なしでpending空。`L` を選ぶと `PL!S-bp3-001` を控え室へ置き、コスト17のAqours `PL!S-bp6-006` だけを候補にし、登場後pending空。

#### PL!S-pb1-006#A01 起動: 手札LIVE公開 → 相手discard分岐 → 自身ブレード4

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
export LLOCG_START_STAGE_C='PL!S-pb1-006'
export LLOCG_START_HAND='PL!S-bp5-020,PL!S-bp5-111'
export LLOCG_START_HAND_SIZE=0
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: 起動後の公開コスト候補は手札LIVEのみで、MEMBERは候補外。LIVEを公開しても手札から移動しない。後続 pending は `opponent_discard` / `not_discard` を持ち、発生源は `PL!S-pb1-006`。`not_discard` で `C.temp_blade 0 -> 4`、`temp_until=end_of_live`、pending空。`opponent_discard` ではブレード付与なしでpending空。

#### PL!-bp5-111#A01 起動: 手札discard → WAITメンバーアクティブ / 相手WAIT人数方式

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_OPPONENT_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!-bp5-111'
export LLOCG_START_HAND='PL!S-bp5-111'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_GREEN='PL!S-bp5-020'
export LLOCG_START_OPPONENT_WAIT=2
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: 手札discard後、相手ウェイト人数がある場合は `opponent_wait` 選択肢が出る。`opponent_wait` 選択で `opponent_wait_count 2 -> 1`、pending空。DB文面の「自分の控え室からライブカードを1枚控え室に置く」は同一ゾーン移動のため no-op として明示ログを残す。自分ステージにWAITメンバーがいる場合は、そのエリア選択で自分のメンバーがACTIVEになる。相手個別カードstateを要求しないのは現行正式仕様通り。

### 20260721 Tier 3 runtime P1 remaining completion

※20260721内部確認: `tier3_runtime_reaudit_correction` のP1 12件のうち、未処理だった `PL!N-pb1-003#A01` / `PL!S-bp7-006#A01` を確認。これにより同P1は全件実装/代表経路確認済み。`PL!N-pb1-003` は手札起動汎用 route にEコスト支払いとグループ名対象抽出を追加し、`PL!S-bp7-006` はデッキ下ミル all group member 判定から自身へ一時ハートを付与する汎用 route を追加。どちらもカード番号専用分岐なし。

#### PL!N-pb1-003#A01 手札起動: E2 + 自身控え室 → 1ドロー → 虹ヶ咲メンバーへブレード

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_OPPONENT_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!N-bp3-009'
export LLOCG_START_HAND='PL!N-pb1-003'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_DECK_TOP='PL!N-bp4-030,PL!N-bp3-032'
export LLOCG_START_ENERGY_ACTIVE=3
export LLOCG_START_ENERGY_WAIT=0
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: 手札の `PL!N-pb1-003` に起動ボタンが出る。起動後、`energy_active 3 -> 1`、`energy_wait 0 -> 2`、`PL!N-pb1-003` は手札から控え室へ移動し、1ドローする。後続 pending は発生源 `PL!N-pb1-003` 付きで、対象候補はステージの『虹ヶ咲』メンバー `C`。`C` 選択で `temp_blade 0 -> 1`、`temp_until=end_of_live`、pending空。エネルギー不足時は `can_activate_from_hand=false` かつ起動しても手札/控え室は動かない。

#### PL!S-bp7-006#A01 ライブ開始時: デッキ下3枚控え室 → 全Aqours MEMBERなら自身に緑

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_OPPONENT_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=LIVE_SET
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!S-bp7-006'
export LLOCG_START_HAND='PL!N-bp1-029'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!N-bp4-030,PL!N-bp3-032,PL!S-bp5-020,PL!S-bp3-001,PL!S-bp6-006,PL!S-bp3-004'
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug
```

確認観点: LIVEをセットしてLIVE_CONFIRMへ進めると、`PL!S-bp7-006 ライブ開始時` が auto_order に出る。解決するとデッキ下3枚 `PL!S-bp3-004,PL!S-bp6-006,PL!S-bp3-001` が控え室へ移動し、全てAqours MEMBERのため `C.temp_hearts.green=1`、`temp_until=end_of_live` になる。Aqours MEMBER以外が混じるnegativeではミルのみ行い、ハート付与なし。

### 20260721 Tier 3 runtime P2 start

※20260721内部確認: `tier3_runtime_reaudit_correction` のP2先頭 `LL-bp2-001#A02` を再監査。過去 evidence は起動のみで、指定名カードが手札にないため実効果解決まで到達していなかった。正規の指定名カード `渡辺曜` / `鬼塚夏美` / `大沢瑠璃乃` を手札に置くコマンドへ補正し、ライブ開始時 auto_order 到達、発生源表示、指定名候補抽出、2枚支払い時の `discarded_count=2` / `C.temp_blade=2`、0枚スキップ時のログあり・ブレード増加なしを確認。監査中に、auto_orderの途中pendingをundoした場合に内部の残auto queueが復元されず、スキップ後に後続自動効果が復帰しない問題を確認したため、undo snapshotへ deferred auto queue/text を保存・復元する汎用修正を追加。カード番号専用分岐なし。

#### LL-bp2-001#A02 ライブ開始時: 指定名手札を任意枚数控え室 → 枚数ぶん自身にブレード

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_OPPONENT_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_PHASE=LIVE_SET
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='LL-bp2-001'
export LLOCG_START_STAGE_L=''
export LLOCG_START_STAGE_R=''
export LLOCG_START_HAND='PL!S-PR-029,PL!SP-bp1-009,PL!HS-bp2-014,PL!N-bp1-029'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!N-bp3-032,PL!S-bp2-026,PL!S-bp2-027,PL!HS-bp2-015,PL!HS-bp2-014,PL!N-bp3-009,LL-bp5-001,PL!SP-bp1-001,PL!S-PR-029,PL!SP-bp4-003'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=4
export LLOCG_START_ENERGY_WAIT=0
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8802 --debug
```

確認観点: `PL!N-bp1-029` をLIVEセットして `LIVE_CONFIRM` へ進める。次の `next` で auto_order に `C: LL-bp2-001 ライブ開始時` と `PL!N-bp1-029 ライブ開始時` が出る。`LL-bp2-001` を選ぶと、手札選択pendingは発生源 `LL-bp2-001` 付きで、候補は `PL!S-PR-029` / `PL!SP-bp1-009` / `PL!HS-bp2-014` の3枚のみ。`PL!S-PR-029,PL!SP-bp1-009` を選ぶと2枚が控え室へ移動し、`C.temp_blade=2`、`temp_until=end_of_live`、後続auto_order `PL!N-bp1-029` が残る。undoで手札・控え室・ブレード・選択pendingが復帰する。さらに空選択でスキップすると `[SKIP] LL-bp2-001: skipped optional multi-discard cost` が残り、ブレードは増えず、後続auto_order `PL!N-bp1-029 ライブ開始時` が復帰する。

#### PL!-bp3-002#A02 常時: 相手ウェイト状態メンバー1人につきブレード

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_OPPONENT_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!-bp3-002'
export LLOCG_START_HAND=''
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!N-bp1-029,PL!N-bp3-032,PL!S-bp2-026,PL!S-bp2-027,PL!HS-bp2-015,PL!HS-bp2-014,PL!N-bp3-009,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=4
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_START_OPPONENT_WAIT=0
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8802 --debug
```

確認観点: 初期 `opponent_wait_count=0` では `C.always_blade_bonus=0`。UI/APIの正式な相手ウェイト人数入力で `opponent_wait_delta +2` を送ると `opponent_wait_count=2`、`C.always_blade_bonus=2` になる。undoで `opponent_wait_count=0` と `C.always_blade_bonus=0` に戻る。相手個別カードstateの不在は現行正式仕様のため不具合扱いしない。

#### 成功ライブカード置き場 LIVE 常時: 手札登場コスト/必要ハート軽減

※20260721内部確認: `PL!-bp6-019#A01` / `PL!-bp6-022#A01` を確認。成功ライブカード置き場にある LIVE の `<常時>` から、元々のコスト/スコア閾値とグループ条件を参照し、手札から登場させる MEMBER のコスト軽減、およびLIVEの必要ハート `<任意>` 軽減へ反映する汎用 helper を追加。`この効果は重複しない` 文面に合わせ、同型複数枚は最大軽減値のみを使う。カード番号専用分岐なし。

確認観点: `success_zone=['PL!-bp6-019']` で元々のコスト17以上の `μ's` MEMBER を手札から登場させる場合、必要コストが2減る。`success_zone=['PL!-bp6-022']` で元々のスコア5以上の `μ's` LIVE をセットする場合、必要ハートの `<任意>` が2減る。条件外のグループ/低コスト/低スコアカードには適用されない。

#### PL!-bp4-002#A01 常時: 開始時/成功時を持たないライブ中LIVEがあるかぎり紫+2

```bash
cd /Users/tekitou/Desktop/gsim/loveca
unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_OPPONENT_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_DEBUG_EFFECT_CARD LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND
export LLOCG_DEBUG_PRESET=effect
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_PHASE=LIVE_SET
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!-bp4-002'
export LLOCG_START_HAND='PL!N-bp3-032,PL!N-bp1-029'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!S-bp2-026,PL!S-bp2-027,PL!HS-bp2-015,PL!HS-bp2-014,PL!N-bp3-009,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=4
export LLOCG_START_ENERGY_WAIT=0
python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8802 --debug
```

確認観点: `PL!N-bp3-032`（<ライブ開始時>/<ライブ成功時>なし）をLIVEセットすると、`C.always_hearts_bonus.purple=2` になる。undo後、`PL!N-bp1-029`（<ライブ開始時>あり）をLIVEセットした場合は `C.always_hearts_bonus={}` のまま。監査中、BODY常時blobが `<紫>` と `<ライブ開始時>` / `<ライブ成功時>` の表記を正規化できず、条件を満たしても紫+2が出ない問題を確認したため、BODY常時共通イテレータのアイコン正規化と能力ラベル有無の両対応を追加。

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

### 2026-07-21 Phase 2 P2 追加監査メモ

※20260721内部確認: P2対象48件はすべて確認・修正済み。今回追加で、BODY常時の単純ブレード加減算、グループ/コスト登場誘発、手札破棄誘発、エネルギー配置誘発、相手ウェイト後続誘発、単独時ライブ不可、成功ライブ置き場LIVE常時軽減、アクティブ→ウェイト誘発、控え室→手札/表向きライブ置き場配置誘発、ステージ移動後続誘発、LIVE置き場BODYによるステージライブ開始時抑止/解決後ALL付与、BODY内のデッキ下ミル、相手盤面比較BODYの手動確認経路、相手ライブカード置き場必要ハート増加の通知経路を汎用経路へ追加/確認した。いずれもカード番号専用分岐なし。発生源は `auto_order` / pending の `source_cn` とログに残る。

確認済み:

- `LL-bp2-001#A02`: live-start optional pay/skip、空スキップ、undoでdeferred queue復元。
- `PL!-bp3-002#A02`: 相手ウェイト人数入力に連動する常時ブレード。
- `PL!-bp4-002#A01`: ライブ開始時/成功時能力なしLIVE参照の紫+2。
- `PL!-bp4-018#A01`, `PL!-pb1-002#A02`, `PL!HS-bp5-016#A02`, `PL!N-PR-024#A01`, `PL!N-pb1-002#A02`, `PL!S-bp2-001#A01`, `PL!S-bp6-009#A01`, `PL!S-pb1-009#A01`, `PL!S-PR-029#A01`, `PL!S-PR-030#A01`, `PL!S-PR-031#A01`, `PL!S-PR-039#A01`, `PL!HS-bp1-003#A01`: 既存/追加の常時ブレード・ハート・スコア参照を直接確認。
- `PL!-bp6-009#A01`: 左右サイドの元々のブレード数参照によるライブ合計スコア+1。
- `PL!-bp6-019#A01`: 成功ライブ置き場LIVEによる手札MEMBER登場コスト軽減。
- `PL!-bp6-022#A01`: 成功ライブ置き場LIVEによるLIVE必要ハート `<任意>` 軽減。
- `PL!-pb1-015#A02`: 相手ウェイト人数入力値1送信後、コスト4以下ウェイト通知からドロー誘発。
- `PL!HS-bp6-007#A01`: Edel Note登場時、相手自身が1人ウェイトにする人数入力pending。
- `PL!HS-pb1-001#A01`: ほかのスリーズブーケ登場時、任意 `<E>` 支払い後エネルギー2枚アクティブ。
- `PL!HS-pb1-003#A02`: 手札からカードが控え室に置かれた時、発生源つきauto_order後に桃+ブレード付与。
- `PL!HS-pb1-009#A01`: 蓮ノ空登場時、センター条件を満たす発生源にブレード+2。
- `PL!HS-pb1-015#A01`: ほかのメンバー不在時ブレード-3、ほかのメンバーありで解除。
- `PL!N-PR-025#A01`: バトンタッチ登場時ドロー既存経路。
- `PL!N-bp4-018#A01`: 自分メンバーがアクティブからウェイトになった時、発生源つきauto_order後に1ドロー+手札1枚破棄pending。
- `PL!N-bp4-026#A01/#A02`: 控え室から手札に加わったLIVE誘発、任意で同名LIVEを表向きライブカード置き場へ置き、次ライブセット条件-1後に表向き配置誘発で虹ヶ咲メンバーへブレード+2。
- `PL!N-bp5-002#A01`: 相手ステージを含む全メンバーとのハート数比較を、発生源つきauto_orderから手動条件確認pendingへ送り、条件達成時のみライブ終了時までライブ合計スコア+1。
- `PL!N-bp4-012#A01`: 相手成功ライブカード置き場スコア合計の手動値に応じたライブ合計スコア+1。
- `PL!N-bp5-030#A01`: LIVE置き場BODYにより、ステージメンバーのライブ開始時能力解決後、そのメンバーが `<ALL>` を持たない場合にライブ終了時まで `<ALL>` を付与。
- `PL!N-pb1-005#A01`: コスト10メンバー登場時ドロー既存経路。
- `PL!N-pb1-012#A01`: このメンバー以外のコスト11メンバー登場時、エネルギー1枚ウェイト配置。
- `PL!S-bp6-002#A01`: ライブカード置き場掃除時、Aqours LIVEをデッキ上/下へ置くpending既存経路。
- `PL!S-bp7-015#A01`: BODY内のデッキ下1枚→控え室処理をライブ時auto_orderに明示表示。下から置いたカードがLIVEなら赤+1、非LIVEなら付与なし。cleanupで赤付与が消えることを確認。
- `PL!SP-bp1-001#A01`: ほかのメンバーがいない場合、ライブ試行をBODY常時でブロック。
- `PL!SP-bp2-010#A01`: 相手ライブカード置き場の全LIVE必要ハート `<任意>` +1は、相手側盤面未モデルのため、発生源つきauto_orderから `effect_notice` で手動反映を明示。A02のエール公開枚数-8既存経路とは分離。
- `PL!SP-bp4-003#A02`, `PL!SP-pb2-035#A01`, `PL!SP-pb2-041#A01`: センター/左/右サイド条件つき単純ブレード+2。
- `PL!SP-bp4-009#A01`: 自分/相手ステージコスト比較を、発生源つきauto_orderから手動条件確認pendingへ送り、条件達成時のみブレード+3。未達時は付与なし。
- `PL!SP-bp4-016#A01`: カード効果によるエネルギー配置時、紫+1。
- `PL!SP-bp7-005#A01`: このメンバー登場時、次ターン非アクティブ指定のエネルギー1枚ウェイト配置。
- `PL!SP-bp7-005#A02`: カード効果によるエネルギー配置時、ブレード+1。
- `PL!SP-pb2-006#A02`: ライブ成功またはエリア移動時、控え室のLiella!メンバーを発生源カードの下へ置く。
- `PL!SP-pb2-022#A01`: 5yncri5e!メンバーがセンターへ移動した時、発生源にブレード+4。
- `PL!SP-pb2-046#A01`: LIVE置き場BODYにより、ステージメンバーのライブ開始時能力を発動させない。対照LIVEでは通常どおりauto_orderを積むことも確認。

残件:

- P2内のruntime未実装残はなし。
- 1デッキ版では相手個別カードstate/相手ライブカード置き場stateを持たないため、`PL!N-bp5-002#A01`、`PL!SP-bp2-010#A01`、`PL!SP-bp4-009#A01` は現行仕様として手動確認・手動反映経路とする。
- 2デッキ版では相手state bridgeにより自動参照・実反映できるものを順次 adapter へ寄せる。相手情報の秘匿は2デッキ用UIでは不要。秘匿が必要なのは、1デッキ用かつパブリックウィンドウを用いるリモート用起動だけ。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

### 2026-07-21 next-target reconfirm: `PL!SP-pb2-001` / `PL!N-bp5-029`

※20260721内部確認: `docs/debug/loveca_remaining_implementation_list_20260701.md` の「次にやるなら」先頭2件を再確認した。どちらもruntime追加修正なしで現行経路が成立。カード番号専用分岐なし。

確認済み:

- `PL!SP-pb2-001#A01`: 登場時、手札1枚を控え室に置く任意コストが発生源 `PL!SP-pb2-001` つきで表示される。コスト支払い後、top5の `display_cards` に公開全体、`candidates` にコスト4以下Liella!メンバーのみが入り、`PL!SP-bp5-008` 選択後の `topk_stage_or_hand` pending は本文 `若菜四季（PL!SP-bp5-008） を...`、`display_cards=['PL!SP-bp5-008']`、`source_cn=PL!SP-pb2-001` を保持する。空きエリア `R` 選択でステージ登場し、`stage_enter_count_this_turn` と `stage_entered_cardnumbers_this_turn` にも記録される。snapshot/restoreで `topk_stage_or_hand` pending へ復帰することを確認。
- `PL!N-bp5-029#A01`: LIVE置き場からライブ開始時auto_orderに入り、`choose_revealed_for_heart_colors_to_stage_named` では公開4枚全体が `display_cards`、選択可能な「中須かすみ」だけが `candidates/options` になる。`PL!N-bp5-002` 選択後、`choose_stage_named_for_picked_hearts` は付与先 `L` のみを提示し、選択後は追加確認なしで黄/緑/青/紫ハート+1をライブ終了時まで付与し、公開カード全体を控え室へ置く。cleanupで付与ハートが消え、snapshot/restoreで付与先選択pendingへ復帰することを確認。

残件:

- この2件について、内部runtime経路の未解決残はなし。必要なら次段で実ブラウザ目視確認に回す。

### 2026-07-21 member under-energy family reconfirm

※20260721内部確認: `docs/debug/loveca_remaining_implementation_list_20260701.md` の「メンバー下エネルギー family」今回追加分を代表再確認した。通常エネルギー置き場、メンバー下エネルギー、エネルギーデッキ返却を混同しないことをstate差分で確認。カード番号専用分岐なし。

確認済み:

- `PL!N-bp3-013#A01`: 登場時に `pay_or_skip` pending が `source_cn=PL!N-bp3-013` / `cost_kind=energy_under_self` つきで出る。`pay` ではエネルギー置き場から1枚をこのメンバーの下へ置き、カードを2枚引く。`skip` では下エネルギー/ドローなし。pending残留なし。
- `PL!N-bp7-007#A01/A02`: `energy_under=0` では常時赤ハートなし、`energy_under=2` では赤ハート+2。ライブ成功時相当の `自分のエネルギーデッキから、エネルギーカード1枚をこのメンバーの下に置く。` は `energy_under` を 0→1 / 2→3 と増やす。
- `PL!N-bp3-025#A01`: LIVE置き場からライブ開始時auto_orderに入り、下エネルギーを持つステージメンバー選択 → 返却枚数 `0/1/2` 選択へ進む。`0` では下エネルギー2のまま、ハート付与なし。`2` では下エネルギー0、赤ハート+6をライブ終了時まで付与。pending残留なし。
- ステージ離脱時: `energy_under=2` の `PL!N-bp7-007` をバトンタッチで控え室へ置いた時、`[INFO] C: return under-energy x2 to energy deck` が出て、通常エネルギー置き場の `active/wait` は増えず、新メンバーの `energy_under=0`。下エネルギーはエネルギーデッキへ戻る扱いを確認。

残件:

- このfamilyの内部runtime経路の代表未解決残はなし。UI目視では、下エネルギーバッジ表示位置のユーザー実機再確認待ちは引き続き別扱い。

### 2026-07-21 `LL-bp5-002` stage group difference reconfirm

※20260721内部確認: `docs/debug/loveca_remaining_implementation_list_20260701.md` の `LL-bp5-002` ステージグループ差分参照を再確認。ライブ開始時 `<ALL>` 付与とライブ成功時の控え室候補絞り込みの両方を確認。カード番号専用分岐なし。

確認済み:

- ライブ開始時: ステージが `μ's` / `虹ヶ咲` / `蓮ノ空` の3グループなら `LL-bp5-002` のauto_order解決でセンターへ `<ALL>` +1、`temp_until=end_of_live`。cleanupで消える。
- ライブ開始時未達: ステージが `μ's` / `μ's` / `虹ヶ咲` の2グループなら `message_ack` pending を出し、`ステージの異なるグループ名は2/3種類` と表示して `<ALL>` 付与なし。
- ライブ成功時: ステージグループ `μ's` / `虹ヶ咲` / `蓮ノ空` の状態で、控え室 `PL!SP-pb2-008` / `PL!-bp4-005` / `PL!N-bp3-009` から候補は `PL!SP-pb2-008` のみ。`choose_card_from_green` pending に `source_cn=LL-bp5-002`、`display_cards=['PL!SP-pb2-008']`、`stage_groups=["μ's","虹ヶ咲","蓮ノ空"]` が入る。選択後、手札へ移動しpending残留なし。
- ライブ成功時候補なし: 控え室がステージ側グループのみの場合は `message_ack` pending を出し、候補なしを表示する。

残件:

- このfamilyの内部runtime経路の未解決残はなし。必要なら実ブラウザ目視確認に回す。

### 2026-07-21 former-area entry family reconfirm

※20260721内部確認: `docs/debug/loveca_remaining_implementation_list_20260701.md` の `PL!HS-bp1-002` / `PL!N-bp3-007` 元エリア登場 family を再確認。どちらも起動コスト支払いから、発生源つき pending、候補フィルタ、解決後の登場履歴、snapshot/restore まで現行runtimeで成立。カード番号専用分岐なし。

確認済み:

- `PL!N-bp3-007#A01`: Cに配置して起動すると `<(E)><(E)>` 支払い後に自身が控え室へ置かれ、`hand_member_to_former_area_then_energy_under` pending が `source_cn=PL!N-bp3-007` / `target_pos=C` つきで出る。手札 `PL!N-bp1-007` / `PL!N-bp1-001` では候補と `display_cards` が `PL!N-bp1-007` のみに絞られる。選択後、Cに登場し、その下へエネルギー1枚を置き、登場履歴にも記録される。snapshot/restoreで起動前stateへ戻る。
- `PL!N-bp3-007#A01` 候補なし: 手札に条件一致メンバーがない場合、コスト支払い後に `message_ack` pending を出し、`source_cn=PL!N-bp3-007` と候補なし文言を表示する。無言処理なし。
- `PL!HS-bp1-002#A01`: Lに配置して起動すると `<(E)><(E)>` 支払い後に自身が控え室へ置かれ、`green_member_to_former_area` pending が `source_cn=PL!HS-bp1-002` / `target_pos=L` つきで出る。控え室 `PL!HS-bp1-001` / `PL!N-bp1-001` では蓮ノ空メンバーのみ候補になる。選択後、Lに登場し、登場時自動効果も通常通り収集・解決される。snapshot/restoreで起動前stateへ戻る。
- `PL!HS-bp1-002#A01` 注意: このカード自身はコストで控え室へ置かれた後、コスト15以下の蓮ノ空メンバー条件を満たすため候補に含まれ得る。現行確認ではこれを不具合扱いせず、カード番号専用除外は入れない。

残件:

- このfamilyの内部runtime経路の未解決残はなし。実ブラウザでは、候補カード表示名/画像表示と、登場後の自動効果pendingの見え方を必要に応じて目視確認する。

### 2026-07-21 additional yell / revealed-card consumption family reconfirm

※20260721内部確認: `docs/debug/loveca_remaining_implementation_list_20260701.md` の追加エール / エール公開カード消費 family を再確認。公開カード確認 → エール時auto_order → 発生源つき効果pending → 解決後の追加エール公開確認まで、現行runtimeで成立。カード番号専用分岐なし。

確認済み:

- `PL!S-bp2-004#A01`: エール公開カードにLIVEがない場合、まず `show_revealed_cards_ack` で公開カード全体を表示し、その後 `auto_order` から `confirm_yell_revealed_all_to_green_then_extra_yell` へ進む。pending は `source_cn=PL!S-bp2-004`、`display_cards` は既存エール公開3枚、本文は「ライブカードがない」条件を表示する。`skip` は公開カードを動かさずpendingを消す。`pay` は既存公開カード3枚を控え室へ置き、3枚追加エールし、追加エール後に `show_revealed_cards_ack` で `base_yell_cards` と `additional_yell_cards` を同時表示する。追加エールのドローアイコンによるドローも処理される。
- `PL!S-bp3-020#A01`: LIVE置き場由来のエール時自動効果として収集される。公開カード中のブレードハート持ちが2枚以下の場合、`confirm_yell_revealed_all_to_green_then_extra_yell` が `source_cn=PL!S-bp3-020` つきで出る。本文は「ブレードハートを持つカードが0枚/2枚以下」「そのエールで得たブレードハートを失って、もう一度エール」を表示し、`PL!S-bp2-004` の「ライブカードがない」文面を流用していない。
- `PL!HS-bp6-027#A01`: LIVE置き場由来のエール時自動効果として収集される。エール公開 `PL!HS-PR-027` / `PL!HS-PR-029` / `PL!HS-bp5-022` では、ブレードハートを持たない蓮ノ空カード2枚だけが `choose_yell_revealed_to_green_then_extra_yell` の候補/表示カードになり、`PL!HS-bp5-022` は候補外。`optional=True`、`max_picks=3`。0枚終了ではカード移動/追加エールなしでpending解消。2枚選択では選択カードのみ控え室へ置き、2枚追加エールし、`show_revealed_cards_ack` に `base_yell_cards` 3枚と `additional_yell_cards` 2枚を同時保持する。

残件:

- このfamilyの内部runtime経路の未解決残はなし。server UI 側の `0枚で終了` / `選択を終了` ボタンとカード画像表示はコード上確認済みだが、必要なら実ブラウザ目視確認に回す。

### 2026-07-21 `PL!SP-pb2-008` live-success no-blade-heart Liella score reconfirm

※20260721内部確認: `PL!SP-pb2-008` のDB補正後タイミングを再確認。現行DBでは `trigger=ライブ成功時` で、エール時自動効果には拾われず、ライブ成功時キューでのみ処理される。カード番号専用分岐なし。

確認済み:

- エール時: Cに `PL!SP-pb2-008`、エール公開4枚の状態で `_enqueue_yell_revealed_body_auto_triggers` は0件。エール時pendingなし。
- ライブ成功時1枚: ブレードハートを持たないLiella!メンバー1枚では `show_revealed_cards_ack` が `source_cn=PL!SP-pb2-008` / `display_cards` つきで出て、「1/2枚のため、ライブの合計スコアは増えません」と表示する。
- ライブ成功時2枚: ブレードハートを持たないLiella!メンバー2枚で `message_ack` が `source_cn=PL!SP-pb2-008` つきで出て、ライブ合計スコア+1。`last_attempt_total_score_bonus=1`。
- ライブ成功時4枚: ブレードハートを持たないLiella!メンバー4枚で上限適用後+2。`last_attempt_total_score_bonus=2`。確認用カードにブレードハート持ちを混ぜるとカウントが下がるため、検証では `PL!SP-bp1-004` を使わず `PL!SP-bp1-006` を使用した。

残件:

- この効果の内部runtime経路の未解決残はなし。実ブラウザでは、ライブ成功時auto_order内で複数成功時効果が並ぶ場合の順序選択表示を必要に応じて目視確認する。

### 2026-07-21 `LL-bp5-001` movement / revealed LIVE / stage heart kinds condition reconfirm

※20260721内部確認: `LL-bp5-001` のライブ成功時3条件複合LIVEを再確認。エール公開LIVE数、ステージハート種類数、ターン中エリア移動履歴のいずれでも同じ `live_success_score_if_revealed_live_or_stage_heart_kinds_or_moved` 汎用routeを通り、発生源つき確認pendingを出す。カード番号専用分岐なし。

確認済み:

- エール公開LIVE条件: エール公開カードにLIVE2枚がある場合、`LL-bp5-001[ライブ成功時]` auto_order 解決で `message_ack` が出て、本文に `revealed LIVE=2/2` / `stage heart kinds=0/5` / `moved_this_turn=False` を表示し、このカードのスコア+1。`last_attempt_score_bonus=[1]`。
- ステージハート種類条件: ステージ上メンバーの現在ハート種類数が5種類以上の場合、エール公開LIVE0枚・移動履歴なしでもスコア+1。確認stateでは一時ハート込みで `stage heart kinds=6/5` と表示。
- エリア移動条件: `stage_moved_this_turn=True` と移動済みカード番号履歴がある場合、エール公開LIVE0枚・ステージハート不足でもスコア+1。本文に `moved_this_turn=True` を表示。
- 条件未達: エール公開LIVE不足、ステージハート不足、移動履歴なしの場合は `confirm_effect` pending を `source_cn=LL-bp5-001` つきで出す。`skip` ではスコア加算なし。無言処理なし。

残件:

- 内部runtime経路の未解決残はなし。実ブラウザ用コマンドは `PL!SP-bp5-006` の実ポジションチェンジで移動履歴を作る方式へ修正済みだが、UI目視は必要に応じて継続。

### 2026-07-21 `PL!SP-bp2-010` yell reveal count modifier reconfirm

※20260721内部確認: `PL!SP-bp2-010` のライブ開始時エール公開枚数減少を再確認。実カードのライブ開始時trigger収集から `live_start_yell_reveal_count_delta_if_other_stage_members_at_least` 汎用routeへ入り、条件達成/未達のどちらも発生源つき `message_ack` を出す。カード番号専用分岐なし。

確認済み:

- 単独ステージ: `PL!SP-bp2-010` 以外のステージメンバー0/1人のため、`message_ack` に「エール公開枚数は変更されません」と表示。`yell_reveal_count_delta_this_live=0`、base 3枚の `_current_yell_reveal_count` は3。
- 他メンバーあり: `PL!SP-bp2-010` 以外のステージメンバー1/1人で、`message_ack` に「このライブ終了時までエール公開枚数を8枚減らします」と表示。`yell_reveal_count_delta_this_live=-8`、base 3枚の `_current_yell_reveal_count` は0に丸められる。

残件:

- この効果の内部runtime経路の未解決残はなし。実ブラウザでは、ライブ開始時auto_order内で `PL!SP-bp2-010` を選んだ後の確認表示と、続くエール公開0枚の流れを必要に応じて目視確認する。

### 2026-07-21 empty-area entry family reconfirm

※20260721内部確認: `docs/debug/loveca_remaining_implementation_list_20260701.md` の空きエリア登場 family を代表再確認。控え室/手札からメンバーのいないエリアへ登場させる汎用route、複数空きエリアの登場先選択、登場後自動効果の収集まで成立。確認中に `mill_top_conditional_followup` の結果確認pendingで `source_cn` が欠ける再発を発見し、共通routeで補完した。カード番号専用分岐なし。

確認済み:

- `PL!HS-bp5-002#A02`: 起動効果の効果文先頭に埋め込まれた `<(E)><(E)>` を候補確認後に支払い、`energy_active/energy_wait=12/0 -> 10/2`。控え室 `PL!HS-bp1-008` / `PL!HS-bp1-001` ではコスト2以下の `PL!HS-bp1-008` のみ候補。`green_member_to_empty_area` pending は `source_cn=PL!HS-bp5-002`、`display_cards=['PL!HS-bp1-008']`、空きエリア `L/R` を保持する。snapshot/restoreで支払い前stateへ戻る。
- `PL!HS-bp5-002#A02` 解決後: `PL!HS-bp1-008` をLへ登場させ、登場履歴を記録。続く `PL!HS-bp1-008` 登場時の山札3枚ミル/全メンバー条件/1ドロー確認pendingは、修正後 `source_cn=PL!HS-bp1-008` を保持する。
- `PL!HS-bp6-016#A01`: 起動コスト `<(E)>x4` を支払い、控え室のコスト4以下蓮ノ空メンバーだけを候補にする。`PL!HS-bp6-015` をRへ登場させると、登場元 `green` として扱われ、`PL!HS-bp6-015` の「手札以外から登場」効果が2ドロー後に2枚同時破棄pendingへ進む。pending は `source_cn=PL!HS-bp6-015`。
- `PL!S-sd1-006#A01`: 通常登場後、任意手札1枚破棄コストを支払うと、控え室のコスト2以下Aqoursメンバーのみ候補にする。`PL!S-PR-025` は候補、非Aqoursの `PL!HS-bp1-008` は候補外。pending は `source_cn=PL!S-sd1-006`、`display_cards=['PL!S-PR-025']`、空きエリア `L/R` を保持する。

修正:

- `llocg_ui/engine.py` の `mill_top_conditional_followup` 結果確認 `show_revealed_cards_ack` に `source_cn` を追加。条件未達、ドロー後続、アイコン付与後続の3分岐すべてに適用。`BUILD_TAG=mill_followup_ack_source_20260721a`。

残件:

- このfamilyの内部runtime経路の未解決残はなし。実ブラウザではカード画像ボタン、登場先選択、2枚同時破棄UIを必要に応じて目視確認する。

### 2026-07-21 baton lower-cost entry condition family reconfirm

※20260721内部確認: `docs/debug/loveca_remaining_implementation_list_20260701.md` のバトンタッチ登場条件 family を再確認。通常 `cmd_play` のバトンタッチ経路から、バトンタッチ元コスト/グループ/同コスト不成立、内側効果への委譲、条件未達の発生源つき表示まで成立。カード番号専用分岐なし。

確認済み:

- `PL!HS-bp2-008#A01` 成立: Cの `PL!HS-bp2-004`（コスト2 / DOLLCHESTRA）へ手札 `PL!HS-bp2-008`（コスト4）をバトンタッチ登場。差額2を支払い、旧メンバーは控え室へ移動。登場時条件は `バトンタッチ元 PL!HS-bp2-004 のコスト 2 < このメンバーのコスト 4 / 『DOLLCHESTRA』` として成立し、内側の `gain_blade_until_end_live` がブレード+2を付与。`message_ack` は `source_cn=PL!HS-bp2-008` と条件/効果/処理結果を保持。
- `PL!HS-bp2-008#A01` 同コスト負例: Cの `PL!HS-bp1-013`（コスト4 / DOLLCHESTRA）からバトンタッチすると、旧コスト4 / 新コスト4のため条件未達。ブレード付与なし。`message_ack` は `source_cn=PL!HS-bp2-008` つきで、バトンタッチ元カード番号・旧コスト・新コストを表示する。
- `PL!-PR-015#A01` 成立: Cの `PL!-sd1-002`（コスト2）から手札 `PL!-PR-015`（コスト17）へバトンタッチ。テストでは `energy_total=20` とし、差額15を支払い。内側の `hand_member_to_empty_area` が `source_cn=PL!-PR-015` つきで開き、手札 `PL!-PR-007`（コスト4）のみ候補、`PL!SP-bp1-001`（コスト9）は候補外。Lへ登場後、`PL!-PR-007` 自身の登場時 `pay_or_skip` pending へ通常通りつながる。
- `PL!-PR-015#A01` 同コスト負例: Cの `PL!-bp6-006`（コスト17）からバトンタッチすると条件未達。`hand_member_to_empty_area` は開かず、`message_ack` が `source_cn=PL!-PR-015` つきで、旧コスト17 / 新コスト17の未達理由を表示する。ログも `[SKIP]` で、適用済みには見えない。

残件:

- このfamilyの内部runtime経路の未解決残はなし。実ブラウザでは、`PL!-PR-015` の高コスト差額支払い確認には通常上限12エネルギー外のテスト設定が必要。

### 2026-07-21 entry-origin / stage-movement BODY family reconfirm

※20260721内部確認: `docs/debug/loveca_remaining_implementation_list_20260701.md` の登場元条件 / 移動時BODY追加 family を代表再確認。控え室登場時の後続効果は空きエリア登場family内で確認済み。移動時BODYでは確認中に即時routeの無言処理を発見し、`draw_then_gain_icons_until_end_live` と `energy_activate` の共通routeへ発生源つき `message_ack` を追加した。カード番号専用分岐なし。

確認済み:

- `PL!HS-bp6-015#A01`: `PL!HS-bp6-016` により控え室から登場した場合、`entry_origin=green` として扱われ、2ドロー後に2枚同時破棄pendingへ進む。pending は `source_cn=PL!HS-bp6-015` と実行中効果本文を保持する。
- `PL!SP-bp5-004#A01`: 実際の `position_change` pending 解決でL→Rへ移動させると、`stage_moved_this_turn=True` と `stage_moved_cardnumbers_this_turn=['PL!SP-bp5-004']` が記録される。移動時auto_order解決後、1ドローし、Rの自身へ赤ハート+1をライブ終了時まで付与。修正後 `message_ack` は `source_cn=PL!SP-bp5-004`、移動時条件、効果本文、処理結果を表示する。
- `PL!SP-pb2-028#A01`: MAIN中に実際の `position_change` pending でL→Rへ移動させると、移動時auto_order解決後にエネルギー2枚をアクティブ化。`energy_active/energy_wait=4/3 -> 6/1`。修正後 `message_ack` は `source_cn=PL!SP-pb2-028`、移動時条件、効果本文、実際にアクティブ化した枚数を表示する。
- `PL!SP-pb2-028#A01` 非MAIN: 同じ移動でも `phase=LIVE_PERF` では自動効果pendingを出さず、エネルギー変化なし。MAIN限定条件を確認。

修正:

- `llocg_ui/engine.py` の `draw_then_gain_icons_until_end_live` に、ドロー枚数・得たアイコン・発生源を表示する `message_ack` を追加。
- `llocg_ui/engine.py` の `energy_activate` に、要求枚数・実際にアクティブ化した枚数・発生源を表示する `message_ack` を追加。
- `BUILD_TAG=auto_energy_activate_ack_20260721c`。

残件:

- `PL!SP-bp5-004` の「エネルギー置き場にエネルギーが置かれたとき」側は、既存残件どおりエネルギー配置イベントの一般ledger設計後に別監査。今回の対象は移動側。

### 2026-07-21 Mac起動/デッキ開始/レアリティ画像 確認メモ

※20260721内部確認: デッキ管理リスト右側の「開始」から `推し活` を起動し、iframe 内のシミュレータが `Turn: 0 | Phase: MULLIGAN | Energy: 3/3` まで描画されることを確認。`マリガン決定` は有効で、押下後 `Turn: 1 | Phase: MAIN` へ遷移した。原因修正として、`APP_VERSION` とクライアント側 `CLIENT_UI_VERSION` の不一致による通常画面の自動リロードループを解消し、通常画面ではバージョン差分リロードを走らせず public view のみに限定した。`/state` 取得は `fetch` 失敗時に XHR fallback を使う。

※20260721内部確認: デッキ管理から渡される `LLOCG_APP_DECK_VARIANTS_JSON` を元に、`/state` の `cn2image_rarity` / `cn2image_variant_id` を生成し、カード画像URLへ `rarity` / `variant_id` を付ける経路を確認。例として `PL!-bp6-001` は `rarity=P2` で `PL!-bp6-001-P2.png` を選択する。現時点ではカード番号単位の表示優先であり、同一カード番号の複数個体を別レアリティで追跡する完全な `instance_id` 管理は次作業で実装する。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./llocg_ui/images.py ./llocg_ui/server.py ./loveca_app/core.py ./loveca_app/web.py ./run_loveca_app.py
python3 ./run_loveca_app.py --host 127.0.0.1 --port 8875 --no-browser
# ブラウザで /decks を開き、推し活の「開始」→ iframe 内「マリガン決定」→ MAIN 遷移を確認
curl -sS http://127.0.0.1:<simulator_port>/suspend_state -o /private/tmp/loveca_suspend_download_check.json
python3 -m json.tool /private/tmp/loveca_suspend_download_check.json >/private/tmp/loveca_suspend_download_check.pretty.json
python3 ./tools/build_loveca_distribution.py --target macos --output /private/tmp/loveca-macos-download-check.zip
```

確認結果: 構文チェックOK。デッキ管理からの起動、MULLIGAN描画、マリガン決定後MAIN遷移OK。中断保存データ生成元の `/suspend_state` はJSONとして取得・整形OK。Mac向け配布ZIP `/private/tmp/loveca-macos-download-check.zip` 作成OK。ブラウザ自動操作ではBlob保存の download event は検出できなかったため、保存ボタン押下後のシミュレータ継続と保存データAPIのJSON妥当性で確認した。

### 2026-07-21 個体ID画像追跡 / 起動時DB更新 / README 整備

※20260721内部確認: デッキ管理から渡す初期デッキをカード番号だけでシャッフルせず、`instance_id` / `rarity` / `variant_id` 付きのカード個体としてシャッフルしてから、手札・山札へ分割する経路を追加。1デッキ用UIは `card_instances` / `card_instance_meta` を `/state` に出し、手札・ステージ・控え室・成功ライブ置き場・ライブ置き場の通常描画では同じ位置の個体IDからレアリティ画像を選ぶ。中断保存/再開にも個体追跡stateを含める。public view では非公開領域の個体ID/metaを出さないよう redaction を追加。

※20260721内部確認: Loveca Application 起動時にDB更新確認を自動開始する設定 `auto_update_on_startup` を追加。既存のデータ更新ページと同じ更新ジョブを使い、`--skip-startup-update` 指定時は起動時更新を開始しない。更新成功時はカードDB/画像/レアリティ関連のアプリ内キャッシュを破棄する。

※20260721内部確認: ユーザー向け取扱説明書として `README.md` を作成。rootへ新規追加したMarkdownは正式入口の `README.md` のみ。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./llocg_ui/images.py ./llocg_ui/server.py ./llocg_ui/views.py ./loveca_app/core.py ./loveca_app/main.py ./loveca_app/web.py ./run_loveca_app.py
git diff --check
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca
env LLOCG_START_PHASE=MAIN LLOCG_START_TURN=1 \
  LLOCG_START_HAND='PL!N-bp1-001,PL!N-bp1-001' \
  LLOCG_START_HAND_SIZE=0 \
  LLOCG_START_SHUFFLE=0 \
  LLOCG_START_DECK_EXACT='PL!N-bp1-001,PL!N-bp1-001,PL!N-bp1-002,PL!N-bp1-003,PL!N-bp1-004,PL!N-bp1-005' \
  LLOCG_START_DECK_EXACT_STRICT=1 \
  LLOCG_APP_INITIAL_INSTANCES_JSON='{"hand":[{"instance_id":"test_hand_a","cardnumber":"PL!N-bp1-001","rarity":"P","variant_id":"variant-a"},{"instance_id":"test_hand_b","cardnumber":"PL!N-bp1-001","rarity":"N","variant_id":"variant-b"}],"deck":[{"instance_id":"test_deck_a","cardnumber":"PL!N-bp1-001","rarity":"N","variant_id":"variant-c"},{"instance_id":"test_deck_b","cardnumber":"PL!N-bp1-001","rarity":"P","variant_id":"variant-d"},{"instance_id":"test_deck_c","cardnumber":"PL!N-bp1-002","rarity":"N","variant_id":"variant-e"},{"instance_id":"test_deck_d","cardnumber":"PL!N-bp1-003","rarity":"N","variant_id":"variant-f"},{"instance_id":"test_deck_e","cardnumber":"PL!N-bp1-004","rarity":"N","variant_id":"variant-g"},{"instance_id":"test_deck_f","cardnumber":"PL!N-bp1-005","rarity":"N","variant_id":"variant-h"}]}' \
  python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8892 --debug
curl -s http://127.0.0.1:8892/state
```

確認結果: 構文チェックOK。`git diff --check` OK。`/state` に `card_instances.hand=["test_hand_a","test_hand_b"]` と、それぞれ別の `rarity` / `variant_id` を持つ `card_instance_meta` が出ることを確認。

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 ./run_loveca_app.py --window-mode none --port 8893 --skip-startup-update
curl -s http://127.0.0.1:8893/api/update/status
curl -s http://127.0.0.1:8893/settings
curl -s -X POST http://127.0.0.1:8893/api/app/shutdown
```

確認結果: `--skip-startup-update` 付き起動では更新ジョブが `idle` のまま。設定画面に「起動時にカードデータ更新を確認する」が表示されることを確認。テスト用ランチャーは `/api/app/shutdown` で終了済み。

### 2026-07-21 更新引数エラー修正 / README分離

※20260721内部確認: `llocg_update_database.py: error: unrecognized arguments: --field-schema ...` の原因は、Loveca Application側が更新スクリプト未対応の `--field-schema` を渡していたこと。更新スクリプト内部の下流DBツールは既定の `manual_overrides/loveca_field_schema.json` を参照するため、ランチャー側から未対応引数を渡さないよう修正した。schemaファイルの存在確認は、欠落を早期検知するため維持。

※20260721内部確認: `README.md` をユーザー向け取扱説明書に限定し、配布zipへ含めるよう `tools/build_loveca_distribution.py` を修正。Git管理/限定配布/アップロード最小構成の説明は配布除外の `jank/loveca_github_management_note_20260721.md` へ分離。配布対象の `docs/notes/loveca_distribution_plan_20260721.md` から管理説明を削除。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./loveca_app/core.py ./loveca_app/main.py ./loveca_app/web.py ./tools/build_loveca_distribution.py ./llocg_update_database.py
python3 ./llocg_update_database.py --help
rg -n -e "--field-schema|field_schema" ./loveca_app/core.py ./llocg_update_database.py
python3 ./tools/build_loveca_distribution.py --target source --output /private/tmp/loveca-readme-split-check2.zip
python3 - <<'PY'
import zipfile
p='/private/tmp/loveca-readme-split-check2.zip'
with zipfile.ZipFile(p) as z:
    names=set(z.namelist())
    print('README', 'loveca/README.md' in names)
    print('jank note', 'loveca/jank/loveca_github_management_note_20260721.md' in names)
    hits=[]
    for n in names:
        if not n.endswith(('.md','.txt')): continue
        text=z.read(n).decode('utf-8', 'ignore')
        if any(word in text for word in ('GitHub','github','collaborator','private repository','Release asset')):
            hits.append(n)
    print('management text hits', hits[:20])
PY
git diff --check
```

確認結果: 構文チェックOK。`llocg_update_database.py --help` で `--field-schema` が存在しないことを確認。Loveca Application側から `--field-schema` 文字列は消え、schema存在確認のみ残存。配布zipには `README.md` が入り、`jank/` の管理メモは入らず、配布内Markdown/TXTにGit管理説明語句が残らないことを確認。`git diff --check` OK。

### 2026-07-21 README初回起動ガイド / 起動時更新画面 / rate limit対策

※20260721内部確認: `README.md` に「初回起動までのガイド」を追加。Windowsユーザー向け手順を先に置き、Python 3導入、`Add python.exe to PATH`、zip展開、`launch_loveca.bat` 起動、PowerShellでの `python --version` / `python .\run_loveca_app.py` 確認まで記載。macOS側も `python3 --version` と `launch_loveca.command` / 手動起動を追記。

※20260721内部確認: 起動時更新確認が有効な場合、アプリはメニュー `/` ではなく `/update` を開く。更新画面には「起動時更新確認が有効な場合、この画面を開いた状態で自動的に確認を開始します」と表示する。`--skip-startup-update` 指定時は従来どおり更新ジョブを開始しない。

※20260721内部確認: プロダクトページの rate limit 対策として、`llocg_update_database.py` に `--max-429` と `--http-cache-ttl-hours` を追加し、`llocg_db_tool_v7.py scrape/all` へ `--cache-ttl-sec` を渡せるようにした。アプリの起動時更新では `delay=10.0`、`max-429=8`、HTTP cache TTL 24時間、released product grace 0日、preview cache 24時間/公式ポストindex 360分で実行する。通常の手動更新は既存寄りの設定を維持。

※20260721内部確認: Loveca Application / launch scripts から `--field-schema` を渡す箇所は存在しない。まだ `llocg_update_database.py: error: unrecognized arguments: --field-schema ...` が出る場合は、古い起動済みアプリプロセス、古い配布zip、または古い `loveca_app/core.py` から起動している可能性が高い。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./loveca_app/core.py ./loveca_app/main.py ./loveca_app/web.py ./run_loveca_app.py ./llocg_update_database.py ./llocg_db_tool_v7.py ./tools/build_loveca_distribution.py
python3 ./llocg_update_database.py --help | rg -n "max-429|http-cache-ttl|field-schema|released-product-grace"
python3 ./llocg_db_tool_v7.py scrape --help | rg -n "cache-ttl|max-429|field-schema"
rg -n -e "--field-schema" ./loveca_app ./run_loveca_app.py ./launch_loveca.command ./launch_loveca.bat
python3 ./tools/build_loveca_distribution.py --target source --output /private/tmp/loveca-readme-startup-update-check.zip
python3 - <<'PY'
import zipfile
p='/private/tmp/loveca-readme-startup-update-check.zip'
with zipfile.ZipFile(p) as z:
    names=set(z.namelist())
    print('README', 'loveca/README.md' in names)
    text=z.read('loveca/README.md').decode('utf-8')
    for needle in ['初回起動までのガイド','Windowsで初めて起動する','Add python.exe to PATH','launch_loveca.bat']:
        print(needle, needle in text)
PY
python3 ./run_loveca_app.py --window-mode none --port 8894 --skip-startup-update
curl -s http://127.0.0.1:8894/update -o /private/tmp/loveca_update_page_check.html
rg -n "起動時更新確認|キャッシュを長め|データ更新" /private/tmp/loveca_update_page_check.html
curl -s http://127.0.0.1:8894/api/update/status
curl -s -X POST http://127.0.0.1:8894/api/app/shutdown
git diff --check
```

確認結果: 構文チェックOK。`llocg_update_database.py --help` に `--max-429` / `--http-cache-ttl-hours` が表示され、`--field-schema` は表示されない。DB下流ツール `llocg_db_tool_v7.py scrape --help` には正規引数として `--field-schema` と `--cache-ttl-sec` が表示される。Loveca Application側から `--field-schema` を渡す箇所はなし。配布zip内 `README.md` に初回起動ガイドが含まれる。`--skip-startup-update` 起動では更新ジョブ `idle`、更新画面に起動時更新確認とキャッシュ説明が表示される。テスト用ランチャーは終了済み。`git diff --check` OK。

### 2026-07-21 turn-enter-history / stage-movement auto ack reconfirm

※20260721内部確認: P2残件のうち、ターン登場履歴条件とステージ移動時自動効果を再監査。`PL!N-bp1-006` は実カード効果文の「このターン、自分のステージに『虹ヶ咲』のメンバーが登場している場合」wrapper から `energy_activate` へ到達し、エネルギーを2枚アクティブ化したあと、発生源 `source_cn=PL!N-bp1-006` 付き `message_ack` を出すことを確認。`PL!N-bp3-005` は `stage_enter_count_this_turn=3` の正規登場回数 ledger を参照し、手札0枚から5枚までドローしたあと、発生源付き `message_ack` を出すことを確認。

※20260721内部確認: `PL!SP-pb2-028` / `PL!SP-bp5-004` は、直接 `try_apply_effect_template` に投げるのではなく、正規の `position_change` pending 解決で `_record_stage_area_movement` と `stage_movement_auto` を通す必要がある。正規経路で `PL!SP-pb2-028` は MAIN 中の移動時にエネルギー2枚アクティブ化し、発生源付き `message_ack` を出すことを確認。`PL!SP-bp5-004` は自分のカード効果による移動時に1枚ドローし、移動後のステージ位置の自身へ赤ハート+1を付与し、発生源付き `message_ack` を出すことを確認。エネルギー置き場に置かれた時の同カード誘発は、後続の `2026-07-21 energy placement auto hook completion` で汎用 `energy_placed_auto` hook 接続済み。

※20260721内部確認: 追加で、`PL!S-bp5-005` の「このターンに登場した非Aqoursメンバーへ選んだハートを付与」route を再確認。実カード効果文から `choose_heart_color_for_stage_positions` pending に到達し、黄選択で L/R のみ `yellow +1`、Aqours の C は除外される。選択後に pending が空になる無言処理を避けるため、`choose_heart_color` / `choose_heart_color_for_moved_stage_members` / `choose_heart_color_for_stage_positions` の汎用解決部へ、選択結果を表示する `message_ack` を追加した。カード番号専用分岐は追加していない。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.db import load_cards_db, _get_card
from llocg_ui.engine import GameState, StageSlot, try_apply_effect_template, cmd_resolve_pending
root=Path('/Users/tekitou/Desktop/gsim/loveca')
cards=load_cards_db(root)

def effects(cn):
    ci=_get_card(cards, cn)
    return [(ab.get('trigger'), cl.get('effect_template') or cl.get('raw') or '') for ab in ci.abilities for cl in ab.get('clauses',[]) if (cl.get('effect_template') or cl.get('raw'))]

gs=GameState(str(root),'',1,debug=True)
gs.stage['L']=StageSlot('PL!N-bp1-001')
gs.stage['C']=StageSlot('PL!S-bp5-005')
gs.stage['R']=StageSlot('PL!SP-bp1-001')
gs.stage_entered_cardnumbers_this_turn=['PL!N-bp1-001','PL!S-bp5-005','PL!SP-bp1-001']
gs.stage_entered_positions_this_turn=['L','C','R']
text=effects('PL!S-bp5-005')[0][1]
assert try_apply_effect_template(gs, random.Random(1), cards, text, {'source_cn':'PL!S-bp5-005','pos':'C','auto_effect_detail':text})
cmd_resolve_pending(gs, cards, 0, '黄', random.Random(1))
assert gs.stage['L'].temp_hearts=={'yellow':1} and gs.stage['C'].temp_hearts=={} and gs.stage['R'].temp_hearts=={'yellow':1}
assert gs.pending and gs.pending[0]['kind']=='message_ack' and gs.pending[0].get('source_cn')=='PL!S-bp5-005'

gs=GameState(str(root),'',11,debug=True)
gs.stage['C']=StageSlot('PL!N-bp1-006')
gs.stage_entered_cardnumbers_this_turn=['PL!N-bp1-001']
gs.energy_active=8; gs.energy_wait=3
text=effects('PL!N-bp1-006')[0][1]
assert try_apply_effect_template(gs, random.Random(11), cards, text, {'source_cn':'PL!N-bp1-006','pos':'C','auto_effect_detail':text})
assert (gs.energy_active, gs.energy_wait)==(10,1)
assert gs.pending and gs.pending[0]['kind']=='message_ack' and gs.pending[0].get('source_cn')=='PL!N-bp1-006'

gs=GameState(str(root),'',12,debug=True)
gs.stage['C']=StageSlot('PL!N-bp3-005')
gs.stage_enter_count_this_turn=3
gs.deck=['PL!N-bp1-001','PL!N-bp1-002','PL!N-bp1-003','PL!N-bp1-004','PL!N-bp1-005','PL!N-bp1-006']
text=effects('PL!N-bp3-005')[0][1]
assert try_apply_effect_template(gs, random.Random(12), cards, text, {'source_cn':'PL!N-bp3-005','pos':'C','auto_effect_detail':text})
assert len(gs.hand)==5 and gs.pending and gs.pending[0]['kind']=='message_ack'

gs=GameState(str(root),'',21,debug=True)
gs.phase='MAIN'
gs.stage['L']=StageSlot('PL!SP-pb2-028')
gs.stage['R']=StageSlot('PL!N-bp1-001')
gs.energy_active=4; gs.energy_wait=3
gs.pending.append({'kind':'position_change','src_pos':'L','source_cn':'TEST-MOVE'})
cmd_resolve_pending(gs, cards, 0, 'R', random.Random(21))
cmd_resolve_pending(gs, cards, 0, 'PL!SP-pb2-028', random.Random(21))
assert (gs.energy_active, gs.energy_wait)==(6,1)
assert gs.pending and gs.pending[0]['kind']=='message_ack' and gs.pending[0].get('source_cn')=='PL!SP-pb2-028'

gs=GameState(str(root),'',22,debug=True)
gs.phase='MAIN'
gs.stage['L']=StageSlot('PL!SP-bp5-004')
gs.stage['R']=StageSlot('PL!N-bp1-001')
gs.deck=['PL!N-bp1-002','PL!N-bp1-003']
gs.pending.append({'kind':'position_change','src_pos':'L','source_cn':'TEST-MOVE'})
cmd_resolve_pending(gs, cards, 0, 'R', random.Random(22))
cmd_resolve_pending(gs, cards, 0, 'PL!SP-bp5-004', random.Random(22))
assert len(gs.hand)==1 and gs.stage['R'].temp_hearts=={'red':1}
assert gs.pending and gs.pending[0]['kind']=='message_ack' and gs.pending[0].get('source_cn')=='PL!SP-bp5-004'

print('OK turn-enter-history / movement ack reconfirm')
PY

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
git diff --check
```

確認結果: `PL!S-bp5-005` / `PL!N-bp1-006` / `PL!N-bp3-005` / `PL!SP-pb2-028` / `PL!SP-bp5-004` の代表経路で、状態差分と発生源付き確認 pending を確認。`python3 -m py_compile` OK。`git diff --check` OK。

※20260721追加確認: ターン内登場履歴 family を、ledger 直書きではなく通常の `cmd_play` 経路で再確認。`PL!N-bp1-006` は手札から `PL!N-bp1-013` を登場させた後に起動し、手札破棄 pending 解決後、登場履歴条件が成立してエネルギー2枚アクティブ化の `message_ack` を出す。`PL!N-bp3-005` は L/R への通常登場後、L へのバトンタッチ登場を3回目として数え、手札5枚までドローの `message_ack` を出す。`PL!S-bp5-005` は通常登場で作った L/R の非Aqours履歴を参照し、選んだハートを L/R にだけ付与する。カード番号専用分岐なし。

### 2026-07-21 energy placement auto hook completion

※20260721内部確認: 以前「設計待ち」として残っていた `PL!SP-bp5-004` の「自分のエネルギー置き場にエネルギーが置かれたとき」側を再確認。現行 runtime には `energy_placed_auto` の汎用収集/実行 route が存在していたため、未接続だったエネルギー配置 route へ `_enqueue_energy_placed_auto_triggers` を接続した。対象は通常のエネルギー置き場へエネルギーデッキから置く route であり、メンバー下エネルギーは通常のエネルギー置き場ではないため誘発対象外のまま。

修正:

- `energy_put_wait_then_manual_draw_if_no_bladeheart`
- `both_players_energy_put_wait`
- `energy_gte_put_wait`
- `energy_put_wait_under_plus_one_self`
- `baton_from_group_and_energy_gte_put_wait_energy`

確認済み:

- 単純な「自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。」で `energy_wait` が増え、`PL!SP-bp5-004[エネルギー配置誘発]` の `auto_order` が発生する。
- `auto_order` 解決後、`PL!SP-bp5-004` は1枚ドローし、自身へ赤ハート+1を付与し、発生源付き `message_ack` を出す。
- `energy_gte_put_wait` route でも同じ誘発へ到達する。
- エネルギーデッキ残数がなく `add=0` の場合は、偽のエネルギー配置誘発を出さない。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, StageSlot, try_apply_effect_template, cmd_resolve_pending
root=Path('/Users/tekitou/Desktop/gsim/loveca')
cards=load_cards_db(root)

gs=GameState(str(root),'',31,debug=True)
gs.stage['C']=StageSlot('PL!SP-bp5-004')
gs.energy_active=3; gs.energy_wait=3
gs.deck=['PL!N-bp1-001','PL!N-bp1-002']
text='自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。'
assert try_apply_effect_template(gs, random.Random(31), cards, text, {'source_cn':'SMOKE-ENERGY-SOURCE','pos':'L','auto_effect_detail':text})
assert gs.energy_wait==4
assert gs.pending and gs.pending[0]['kind']=='auto_order'
cmd_resolve_pending(gs, cards, 0, 'PL!SP-bp5-004', random.Random(31))
assert len(gs.hand)==1 and gs.stage['C'].temp_hearts=={'red':1}
assert gs.pending and gs.pending[0]['kind']=='message_ack' and gs.pending[0].get('source_cn')=='PL!SP-bp5-004'

gs=GameState(str(root),'',32,debug=True)
gs.stage['C']=StageSlot('PL!SP-bp5-004')
gs.energy_active=6; gs.energy_wait=0
gs.deck=['PL!N-bp1-001','PL!N-bp1-002']
text='自分のエネルギーが6枚以上ある場合、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。'
assert try_apply_effect_template(gs, random.Random(32), cards, text, {'source_cn':'SMOKE-GTE','pos':'L','auto_effect_detail':text})
assert gs.energy_wait==1
assert gs.pending and gs.pending[0]['kind']=='auto_order'
cmd_resolve_pending(gs, cards, 0, 'PL!SP-bp5-004', random.Random(32))
assert len(gs.hand)==1 and gs.stage['C'].temp_hearts=={'red':1}

gs=GameState(str(root),'',33,debug=True)
gs.stage['C']=StageSlot('PL!SP-bp5-004')
gs.energy_active=12; gs.energy_wait=0
assert try_apply_effect_template(gs, random.Random(33), cards, '自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。', {'source_cn':'SMOKE-NO-ENERGY','pos':'L'})
assert not gs.pending

print('OK energy placement auto hook completion')
PY

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
git diff --check
```

### 2026-07-21 起動時更新の許可確認ポップアップ化

※20260721内部確認: 起動時更新確認が有効な場合でも、起動直後に更新ジョブを開始しないよう変更。`run_loveca_app.py` は `/update?startup=1` を開くだけにし、更新画面で「カードデータの更新を確認しますか？」の確認パネルを表示する。ユーザーが `更新する` を押した場合のみ `/api/update/startup-confirmed` から `maybe_start_startup_update()` を呼び、rate limit対策つきの起動時更新設定で開始する。`あとで` では更新ジョブを開始しない。

※20260721内部確認: 確認文言には「公式情報・Wiki・画像取得先などの外部サイトへアクセスします」「許可した場合のみ更新を開始します」を含めた。READMEの初回起動/カードデータ更新説明も、外部サイト取得と許可後開始の表現に変更。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./loveca_app/core.py ./loveca_app/main.py ./loveca_app/web.py ./run_loveca_app.py
rg -n "startup-confirmed|waiting-for-user-confirmation|更新する|外部サイト|自動で更新確認を開始" ./loveca_app ./README.md
python3 ./run_loveca_app.py --window-mode none --port 8895
curl -s http://127.0.0.1:8895/update?startup=1 -o /private/tmp/loveca_startup_confirm_page.html
rg -n "カードデータの更新を確認しますか|許可した場合のみ|更新する|あとで" /private/tmp/loveca_startup_confirm_page.html
curl -s http://127.0.0.1:8895/api/update/status
curl -s -X POST http://127.0.0.1:8895/api/app/shutdown
git diff --check
```

確認結果: 構文チェックOK。`/update?startup=1` に確認パネル文言が表示される。起動直後の `/api/update/status` は `idle` のままで、許可前に外部更新ジョブは開始されない。テスト用ランチャーは終了済み。`git diff --check` OK。

### 2026-07-21 macOS起動ターミナル自動クローズ

※20260721内部確認: macOSで `launch_loveca.command` から起動した場合、アプリケーション終了後にTerminal/iTermのウインドウが残りやすいため、Pythonプロセス正常終了後に起動TTYと一致するTerminalタブ/ウインドウをAppleScriptで閉じる処理を追加。`exec` をやめ、終了コードを取得してから正常終了時のみ閉じる。起動失敗時はターミナルを残し、エラーを確認できるようにした。`LOVECA_KEEP_TERMINAL_OPEN=1` を指定した場合は閉じない。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
bash -n ./launch_loveca.command
ls -l ./launch_loveca.command
python3 ./tools/build_loveca_distribution.py --target macos --output /private/tmp/loveca-terminal-close-check.zip
python3 - <<'PY'
import zipfile
p='/private/tmp/loveca-terminal-close-check.zip'
with zipfile.ZipFile(p) as z:
    name='loveca/launch_loveca.command'
    info=z.getinfo(name)
    text=z.read(name).decode('utf-8')
    print(name, True)
    print('close function', 'close_loveca_terminal_window' in text)
    print('tty match', 'LOVECA_LAUNCH_TTY' in text)
    print('mode oct', oct((info.external_attr >> 16) & 0o777))
PY
```

確認結果: `bash -n` OK。`launch_loveca.command` の実行権限は維持。macOS配布zip内の `loveca/launch_loveca.command` に自動クローズ処理が含まれ、zip上のmodeも `755`。

### 2026-07-21 プロダクトページ長期キャッシュ

※20260721内部確認: 24時間HTTPキャッシュ切れ後にプロダクトページ再取得で429が発生しやすいため、商品ページ本文だけ長期TTLで再利用する経路を追加。`llocg_db_tool_v7.py fetch()` にリクエスト単位の `cache_ttl_sec` 上書きを追加し、`cmd_scrape()` の商品ページ取得では通常更新時のみ `--product-page-cache-ttl-days` を適用する。既定値は3650日。商品一覧ページは通常TTLのまま確認し、新規商品ページなどキャッシュ未保存のURLだけ外部取得が必要になる。

※20260721内部確認: `llocg_update_database.py` に `--product-page-cache-ttl-days` を追加し、下流 `llocg_db_tool_v7.py scrape` へ渡す。Loveca Applicationの起動時更新では `--product-page-cache-ttl-days 3650` を明示指定。`--full-refresh` 時は商品ページ長期TTLを使わず通常キャッシュ挙動に戻す。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./llocg_db_tool_v7.py ./llocg_update_database.py ./loveca_app/core.py ./loveca_app/main.py ./loveca_app/web.py ./run_loveca_app.py
python3 ./llocg_db_tool_v7.py scrape --help | rg -n "product-page-cache|cache-ttl|max-429"
python3 ./llocg_update_database.py --help | rg -n "product-page-cache|http-cache-ttl|max-429"
rg -n "product-page-cache-ttl-days|cache_ttl_sec=None if fresh|product_long_cache_ttl_sec|3650" ./llocg_db_tool_v7.py ./llocg_update_database.py ./loveca_app/core.py
python3 - <<'PY'
import os, tempfile, time
from pathlib import Path
import llocg_db_tool_v7 as db
with tempfile.TemporaryDirectory() as td:
    cache = Path(td)
    url = 'https://wikiwiki.jp/llocardgame/test-product-page'
    path = db.sha_path(cache, url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('cached-product-html', encoding='utf-8')
    old = time.time() - 7200
    os.utime(path, (old, old))
    db.CONFIG['cache_ttl_sec'] = 1.0
    got = db.fetch(url, cache, delay=0, user_agent='test', timeout=0.001, cache_ttl_sec=3650*86400)
    print('long_ttl_hit', got == 'cached-product-html')
PY
```

確認結果: 構文チェックOK。`scrape --help` / `llocg_update_database.py --help` に `--product-page-cache-ttl-days` が表示される。通常TTLより古いキャッシュでも、商品ページ用長期TTLを渡すと外部アクセスせず `long_ttl_hit True` になることを確認。最初の確認で通常TTL切れ時の外部アクセス待ちに入ったため中断したが、その後長期TTLキャッシュヒットのみのスモークで確認済み。

### 2026-07-21 broad UI layout handoff 対応

※20260721内部確認: `docs/handoffs/loveca_handoff_20260721_broad_ui_layout_items.md` を確認。具体的な単一不具合ではなく、広域UI/レイアウト作業のスコープ定義だったため、既存UIへ横断的に効くリサイズ安定化とポップアップカードリストの共通レイアウト補強を実装した。効果処理・runtime stateは変更していない。

※20260721内部確認: `llocg_ui/server.py` のウインドウリサイズ処理を `requestAnimationFrame` 経由に変更し、`visualViewport.resize` にも追従。連続resize中に即時 `render()` が多発する状態を避ける。

※20260721内部確認: `openCardListPopup` / `openCardPickPopup` のカードリスト描画を `renderPopupCardSurface()` へ共通化。ポップアップ種別と画面高さに応じてカードサイズを抑え、カード間隔も表示幅に応じて調整する。`#modalCards` / `#viewerCards` は `overscroll-behavior: contain` と `.broadCardListSurf` を使う。狭めの画面ではsource card columnとviewer modal幅もCSS media queryで縮める。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./llocg_ui/server.py
git diff --check
rg -n "broad_ui_layout_resize_popup_cards|renderPopupCardSurface|popupCardSurfaceMetrics|scheduleResizeRender|broadCardListSurf" ./llocg_ui/server.py
env LLOCG_START_PHASE=MAIN LLOCG_START_TURN=1 \
  LLOCG_START_HAND_SIZE=0 \
  LLOCG_START_DECK_EXACT='PL!N-bp1-001,PL!N-bp1-002,PL!N-bp1-003,PL!N-bp1-004,PL!N-bp1-005,PL!N-bp1-006' \
  LLOCG_START_DECK_EXACT_STRICT=1 \
  python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8896 --debug
curl -s http://127.0.0.1:8896/ -o /private/tmp/loveca_broad_ui_layout.html
python3 - <<'PY'
from pathlib import Path
html=Path('/private/tmp/loveca_broad_ui_layout.html').read_text(encoding='utf-8')
print('html_len', len(html))
print('build_tag', 'broad_ui_layout_resize_popup_cards_20260721a' in html)
print('card_surface', 'renderPopupCardSurface' in html)
start=html.find('<script>')
end=html.rfind('</script>')
if start >= 0 and end > start:
    js=html[start+len('<script>'):end]
    Path('/private/tmp/loveca_broad_ui_layout.js').write_text(js, encoding='utf-8')
    print('js_len', len(js))
else:
    print('no_script')
PY
```

確認結果: `py_compile` OK。`git diff --check` OK。生成HTMLに `broad_ui_layout_resize_popup_cards_20260721a` と `renderPopupCardSurface` が含まれることを確認。テスト用サーバーは終了済み。Node.jsが見つからない環境だったためJS単体の `node --check` は未実行。

### 2026-07-21 バトンタッチ登場参照 / メンバー下エネルギー無言処理補完

※20260721内部確認: 通常 `cmd_play` のバトンタッチ登場時に、登場時自動効果収集へ `entry_origin='hand'` が渡っていた箇所を `entry_origin='baton'` に修正。`stage_baton_entered_cardnumbers_this_turn` への記録自体は既存 generic ledger を使用し、カード番号専用分岐は追加していない。

※20260721内部確認: `PL!N-PR-025` をステージに置き、別エリアで通常プレイによるバトンタッチ登場を発生させる内部 smoke を実施。`stage_baton_entered_cardnumbers_this_turn` に新メンバーが記録され、`PL!N-PR-025` のバトンタッチ登場参照が発生源つき `message_ack` まで到達することを確認。

※20260721内部確認: `PL!N-bp7-019` のバトンタッチでステージを離れたときの効果について、エネルギーデッキからこのバトンタッチで登場したメンバーの下に置く処理が state 更新だけで終わらないよう、発生源つき `message_ack` を追加。あわせて、同型の「このメンバーの下に置く」直接処理と「ステージの指定グループメンバーの下に置く」選択解決後にも確認 pending を追加した。

※20260721内部確認: `PL!N-bp7-019` の通常バトンタッチ退場 trigger、直接 self under-energy 文型、指定グループ下置き選択文型の内部 smoke を実施。いずれも対象メンバーの `energy_under` が増え、発生源つき確認 pending が残ることを確認。

※20260721内部確認: `PL!HS-bp2-021` / `PL!HS-bp2-023` / `PL!HS-bp2-025` と同型の「このターン中にバトンタッチして登場した『蓮ノ空』のメンバーが2人以上いる場合、必要ハートを指定色ぶん減らす」文型について、テンプレート解決器の成功/未達両方で `message_ack` を出すように補完。内部 smoke で2人成立時は `live_start_required_override_by_cn` が更新され、1人のみの場合は override なしの未達 pending になることを確認。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -c "import random; from pathlib import Path; from llocg_ui.db import load_cards_db; from llocg_ui.engine import GameState, StageSlot, try_apply_effect_template; root=Path('.'); cards=load_cards_db(root); text='自分のステージに、このターン中にバトンタッチして登場した『蓮ノ空』のメンバーが2人以上いる場合、このカードを成功させるための必要ハートを<緑>減らす。'; gs=GameState(root=str(root), code='SMOKE', seed=1, debug=True); gs.phase='LIVE_START'; gs.stage={'L':StageSlot('PL!HS-bp2-008'), 'C':StageSlot('PL!HS-bp1-012'), 'R':StageSlot('PL!HS-PR-007')}; gs.stage_baton_entered_cardnumbers_this_turn=['PL!HS-bp2-008','PL!HS-PR-007']; ok=try_apply_effect_template(gs, random.Random(1), cards, text, {'source_cn':'PL!HS-bp2-021','pos':'SET','auto_effect_detail':text}); print('success_ok', ok); print('success_pending', gs.pending[-1] if gs.pending else None); print('success_override', gs.live_start_required_override_by_cn); gs2=GameState(root=str(root), code='SMOKE', seed=2, debug=True); gs2.phase='LIVE_START'; gs2.stage={'L':StageSlot('PL!HS-bp2-008'), 'C':StageSlot('PL!HS-bp1-012'), 'R':StageSlot('PL!N-bp1-006')}; gs2.stage_baton_entered_cardnumbers_this_turn=['PL!HS-bp2-008']; ok2=try_apply_effect_template(gs2, random.Random(2), cards, text, {'source_cn':'PL!HS-bp2-021','pos':'SET','auto_effect_detail':text}); print('failure_ok', ok2); print('failure_pending', gs2.pending[-1] if gs2.pending else None); print('failure_override', gs2.live_start_required_override_by_cn)"
```

確認結果: 成立時は `success_ok True`、`source_cn='PL!HS-bp2-021'` の `message_ack`、`{'PL!HS-bp2-021': {'green': 6, 'any': 5}}` の required override を確認。未達時は `failure_ok True`、override なし、未達理由を含む `message_ack` を確認。バトンタッチ登場参照は設計待ち/再監査残から外し、実ブラウザでは操作感と確認ポップアップの目視だけを別扱いにする。

### 2026-07-21 latest two decks runtime debug

※20260721内部確認: デッキ一覧の更新日時が新しい2件、`deck_444782643669fb371f81.tsv`（`7U1CT` / `ポムポムミアSaint`）と `deck_49921c3081c71d2fea40.tsv`（`540L5` / `トリオ名古屋`）を対象に、1デッキ用 `App` と2デッキ用 `LegacyUIAdapter` / `DualMatchEngine` を直接初期化して実行確認した。

※20260721内部確認: 1デッキ側で `PL!HS-PR-022` 等のライブ開始時任意 `<(E)>` コストが支払えない場合、旧挙動では `[ERR] ability: insufficient energy...` だけになっていた。`live_start_pay_effect` / `live_start_blade` の共通経路で、支払えない場合は `[SKIP]` ログと発生源つき `message_ack` を出すよう修正。

※20260721内部確認: 2デッキ側で0枚ライブセットから `LIVE_CONFIRM -> LIVE_RESOLVE` へ進む場合、旧Appが `last_attempt_result` を出さないため成否取得エラーになりうる経路を修正。0枚セットも no-live failure として記録する。

※20260721内部確認: 2デッキ終了判定は `MatchState.players[*].success_zone` を正本として参照するよう修正。短縮 state で P1勝利 / P2勝利 / 引き分け / 継続を確認済み。

詳細報告: `docs/debug/loveca_two_latest_decks_runtime_debug_20260721.md`

### 2026-07-21 deferred UI / runtime reaudit handoff 対応

※20260721内部確認: `docs/handoffs/loveca_handoff_20260721_deferred_ui_and_reaudit_items.md` を確認。残件表上、runtime 実装残は0件扱いだったが、引き継ぎで注意されていた movement BODY wrapper の通常経路を再監査し、`このメンバーが登場か、エリアを移動したとき/するたび` 型のBODY自動効果が、移動時は `position_change -> _record_stage_area_movement -> stage_movement_auto` で発火する一方、登場時のBODY収集に未接続であることを確認した。

※20260721内部確認: 上記文型を `BODY 自動` の登場時収集へ汎用追加。対象は現行DBでは `PL!SP-bp4-011` / `PL!SP-pb1-006`。カード番号専用分岐ではなく、同文型の `登場か、エリアを移動したとき/するたび` を拾う。移動時は既存の `stage_movement_auto` 側で内側効果を解決する方針を維持した。

※20260721内部確認: 同文型が直接 `try_apply_effect_template()` に投げられた場合、登場イベント文脈がない限り内側効果を誤適用しない guard を追加。登場側は収集済み trigger から内側効果を解決し、移動側は通常の位置変更 pending 解決でのみ発火する。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 - <<'PY'
import random
from pathlib import Path
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, StageSlot, try_apply_effect_template, cmd_resolve_pending, _collect_auto_triggers_on_member_enter, _exec_auto_trigger
root=Path('.')
cards=load_cards_db(root)
eff='このメンバーが登場か、エリアを移動するたび、ライブ終了時まで、<(ブレード)><(ブレード)>を得る。'
gs=GameState(str(root),'',1,debug=True)
gs.phase='MAIN'
gs.stage['C']=StageSlot('PL!SP-pb1-006')
ok=try_apply_effect_template(gs, random.Random(1), cards, eff, {'pos':'C','source_cn':'PL!SP-pb1-006'})
assert ok is True
assert int(getattr(gs.stage['C'], 'temp_blade', 0) or 0) == 0
assert any('enter-or-movement wrapper ignored' in x for x in gs.log)
gs2=GameState(str(root),'',2,debug=True)
gs2.phase='MAIN'
gs2.stage['C']=StageSlot('PL!SP-pb1-006')
trigs=_collect_auto_triggers_on_member_enter(gs2, cards, 'C', 'PL!SP-pb1-006', entry_origin='hand')
pick=[t for t in trigs if t.get('label')=='PL!SP-pb1-006[登場/移動誘発]'][0]
_exec_auto_trigger(gs2, cards, pick)
assert int(getattr(gs2.stage['C'], 'temp_blade', 0) or 0) == 2
gs3=GameState(str(root),'',3,debug=True)
gs3.phase='MAIN'
gs3.stage['L']=StageSlot('PL!SP-pb1-006')
gs3.pending.append({'kind':'position_change','src_pos':'L','source_cn':'PL!SP-pb1-006','options':['C','R']})
cmd_resolve_pending(gs3, cards, 0, 'C', random.Random(3))
assert getattr(gs3, 'stage_moved_this_turn', False) is True
assert gs3.pending and gs3.pending[0]['kind']=='auto_order'
cmd_resolve_pending(gs3, cards, 0, 'PL!SP-pb1-006', random.Random(3))
assert int(getattr(gs3.stage['C'], 'temp_blade', 0) or 0) == 2
print('OK enter-or-movement BODY enter/movement smoke')
PY

python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, StageSlot, _collect_auto_triggers_on_member_enter, _exec_auto_trigger
root=Path('.')
cards=load_cards_db(root)
gs=GameState(str(root),'',4,debug=True)
gs.phase='MAIN'
gs.stage['C']=StageSlot('PL!SP-bp4-011')
trigs=_collect_auto_triggers_on_member_enter(gs, cards, 'C', 'PL!SP-bp4-011', entry_origin='hand')
pick=[t for t in trigs if t.get('label')=='PL!SP-bp4-011[登場/移動誘発]'][0]
_exec_auto_trigger(gs, cards, pick)
assert gs.pending
assert gs.pending[0].get('source_cn') == 'PL!SP-bp4-011'
print('OK opponent wait enter-or-movement collected', gs.pending[0].get('kind'))
PY

python3 -m py_compile ./llocg_ui/engine.py
git diff --check
```

確認結果: `PL!SP-pb1-006` は直接解決ではブレードを得ず、BODY登場収集ではブレード+2、通常 `position_change` 経由の移動時でもブレード+2になることを確認。`PL!SP-bp4-011` はBODY登場収集から `opponent_wait_notify` pending へ到達し、`source_cn` も保持することを確認。

### 2026-07-21 GitHub release packaging 対応

※20260721内部確認: GitHub Releases 向け配布zipとして、macOS / Windows / source の3系統を生成する方針で `tools/build_loveca_distribution.py` を調整。macOS / Windows の利用者向けzipには開発メモ、引き継ぎ、`AGENTS.md`、`user_data/` を含めず、READMEと起動に必要なruntime/DB/画像だけを含める。source zipのみ `AGENTS.md` と `docs/debug` / `docs/handoffs` / `docs/notes` を含める。

※20260721内部確認: `user_data/remote_sessions` / `user_data/runtime` / `user_data/settings.json` は個人設定・選択デッキ・リモートセッション履歴を含むため、配布zipから除外した。必要なフォルダはアプリ起動時に作られる。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./tools/build_loveca_distribution.py
python3 ./tools/build_loveca_distribution.py --target macos --output ./_codex_outputs/github_release/loveca-macos-20260721.zip
python3 ./tools/build_loveca_distribution.py --target windows --output ./_codex_outputs/github_release/loveca-windows-20260721.zip
python3 ./tools/build_loveca_distribution.py --target source --output ./_codex_outputs/github_release/loveca-source-20260721.zip
python3 - <<'PY'
from pathlib import Path
import zipfile
for p in sorted(Path('_codex_outputs/github_release').glob('loveca-*-20260721.zip')):
    with zipfile.ZipFile(p) as z:
        names=z.namelist()
    checks={
        'README': 'loveca/README.md' in names,
        'mac_launcher': 'loveca/launch_loveca.command' in names,
        'win_launcher': 'loveca/launch_loveca.bat' in names,
        'AGENTS': 'loveca/AGENTS.md' in names,
        'docs_debug_any': any(n.startswith('loveca/docs/debug/') for n in names),
        'docs_handoffs_any': any(n.startswith('loveca/docs/handoffs/') for n in names),
        'user_data_any': any(n.startswith('loveca/user_data/') for n in names),
        'card_images_count': sum(1 for n in names if n.startswith('loveca/llocg_db_out_full/card_images/') and not n.endswith('/')),
        'file_count': len(names),
    }
    print(p.name, checks)
PY
python3 - <<'PY'
from pathlib import Path
import zipfile
for p in sorted(Path('_codex_outputs/github_release').glob('loveca-*-20260721.zip')):
    with zipfile.ZipFile(p) as z:
        bad=[n for n in z.namelist() if '.DS_Store' in n or n.endswith('.zip') or '__pycache__' in n or '/jank/' in n]
    print(p.name, 'bad_entries', bad[:10], 'count', len(bad))
PY
shasum -a 256 ./_codex_outputs/github_release/loveca-macos-20260721.zip ./_codex_outputs/github_release/loveca-windows-20260721.zip ./_codex_outputs/github_release/loveca-source-20260721.zip > ./_codex_outputs/github_release/SHA256SUMS-20260721.txt
git diff --check
```

確認結果: 3zip生成OK。macOS版は `launch_loveca.command` のみ、Windows版は `launch_loveca.bat` のみを含む。利用者向け2zipは `AGENTS.md` / docs debug / docs handoffs / `user_data/` を含まない。source版は開発docsと `AGENTS.md` を含む。全zipで `.DS_Store`、入れ子zip、`__pycache__`、`jank/` 混入なし。各zipのカード画像数は1514件。

### 2026-07-21 GitHub public zip 画像分離 / UI資産バンドル対応

※20260721内部確認: GitHubでPublic配布する本体zipには、外部サイトから取得したカード画像を含めない方針へ変更。`tools/build_loveca_distribution.py` の本体ビルドから `playmat.jpg` と `llocg_db_out_full/card_images` を除外し、macOS / Windows / source zip の画像ファイル数が0になることを確認した。

※20260721内部確認: UI用画像類は本体とは別の `loveca-ui-assets.zip` として生成するルートを追加。対象は `playmat.jpg`、`NoImage.PNG`、`back.png`、存在する場合の `energy.*`、`texticons/*.png`。本体zip展開後の `loveca` フォルダ直下に `loveca-ui-assets.zip` または `loveca-ui-assets/` がある場合、起動時に所定位置へ自動配置する。

※20260721内部確認: `loveca_app/assets.py` を追加し、バンドル展開時は許可リストにあるUI資産だけをコピーする。`..` を含むパスや想定外ファイルはスキップし、カード画像セット本体を誤って配置しないようにした。

実行確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./loveca_app/assets.py ./loveca_app/main.py ./tools/build_loveca_distribution.py
python3 ./tools/build_loveca_distribution.py --target macos --output ./_codex_outputs/github_release/loveca-macos-20260721.zip
python3 ./tools/build_loveca_distribution.py --target windows --output ./_codex_outputs/github_release/loveca-windows-20260721.zip
python3 ./tools/build_loveca_distribution.py --target source --output ./_codex_outputs/github_release/loveca-source-20260721.zip
python3 ./tools/build_loveca_distribution.py --target ui-assets --output ./_codex_outputs/github_release/loveca-ui-assets-20260721.zip
python3 - <<'PY'
from pathlib import Path
import zipfile
for p in sorted(Path('_codex_outputs/github_release').glob('loveca-*-20260721.zip')):
    with zipfile.ZipFile(p) as z:
        names=z.namelist()
    image_names=[n for n in names if n.lower().endswith(('.png','.jpg','.jpeg','.webp','.gif'))]
    print(p.name, 'files', len(names), 'images', len(image_names), 'has_user_data', any(n.startswith('loveca/user_data/') for n in names))
PY
python3 - <<'PY'
from pathlib import Path
import shutil, tempfile, zipfile
from loveca_app.assets import ensure_ui_assets_from_local_bundle
root=Path('.')
with tempfile.TemporaryDirectory() as td:
    tmp=Path(td)
    with zipfile.ZipFile(root/'_codex_outputs/github_release/loveca-macos-20260721.zip') as z:
        z.extractall(tmp)
    app=tmp/'loveca'
    shutil.copy2(root/'_codex_outputs/github_release/loveca-ui-assets-20260721.zip', app/'loveca-ui-assets.zip')
    result=ensure_ui_assets_from_local_bundle(app)
    required=[
        app/'playmat.jpg',
        app/'llocg_db_out_full/card_images/NoImage.PNG',
        app/'llocg_db_out_full/card_images/back.png',
        app/'llocg_db_out_full/card_images/texticons/icon_blade.png',
    ]
    assert all(p.exists() for p in required), required
    assert not any((app/'llocg_db_out_full/card_images').glob('BP*/*'))
    print('installed', len(result.installed), 'errors', result.errors)
PY
shasum -a 256 ./_codex_outputs/github_release/loveca-macos-20260721.zip ./_codex_outputs/github_release/loveca-windows-20260721.zip ./_codex_outputs/github_release/loveca-source-20260721.zip ./_codex_outputs/github_release/loveca-ui-assets-20260721.zip > ./_codex_outputs/github_release/SHA256SUMS-20260721.txt
git diff --check
```

確認結果: 本体3zipは画像0件、`user_data/` 混入なし。UI資産バンドルは13件で、別配布対象のUI画像のみを含む。仮展開した本体フォルダ直下へ `loveca-ui-assets.zip` を置いた状態で `ensure_ui_assets_from_local_bundle()` を実行し、13件配置、エラーなし、カード画像セット本体の混入なしを確認。

### 2026-07-21 dual opponent context bridge

※20260721内部確認: 2デッキ版で効果処理エンジンを1デッキ版へ寄せる第一歩として、`llocg_dual_v2.server.LegacyUIAdapter` が各プレイヤーの1デッキAppへ `gs.opponent` / `gs.opp` の非再帰スナップショットを渡すようにした。相手の実GameStateを直接ぶら下げず、ステージ、山札/手札枚数、控え室、ライブ置き場、成功ライブ置き場、エネルギー、直近ライブスコアなどの参照用情報だけを渡す。これにより、既存の `llocg_ui.effects.helpers` と共有resolverが相手ステージコスト等を自動参照できる。

確認済み:

- `gs.opponent` が存在し、相手ステージ `PL!N-pb1-007` のコスト15を `llocg_ui.effects.helpers._opp_stage_member_cost_sum()` が読める。
- `自分ステージにいるメンバーのコストの合計が相手より低い場合、カードを1枚引く。` は、2デッキadapter経由の相手contextありで手動pendingに落ちず、自動で条件達成時のみドローする。
- 逆条件では手動pendingなしで未適用になり、ログに条件未達が残る。
- opponent context は相手GameStateへの再帰参照を持たず、dual snapshot がpickle可能。
- 2デッキ既存ユニットテスト `llocg_dual_v2.tests.test_rule_core` / `llocg_dual_v2.tests.test_legacy_adapter_transactions` はOK。

残件:

- 今回は参照専用bridgeまで。相手メンバーをウェイトにする、相手手札を公開/破棄する、相手控え室/デッキを実際に移動する効果は、相手側Appへコマンドを配送する `opponent action bridge` が必要。ここは対象選択UI、相手側ログ、undo同期が絡むため次段で扱う。

### 2026-07-21 dual opponent wait action bridge

※20260721内部確認: `opponent action bridge` の第一段として、2デッキ版で `opponent_wait_notify` を解決した時、人数入力値を相手側Appの実ステージ状態へ反映する処理を追加した。UIは現行正式仕様の人数入力方式を維持し、2デッキadapterが入力値とpending本文から候補を絞り、相手stageの該当メンバーを `active=False` にする。カード番号専用分岐なし。

対応した候補条件:

- コストN以下 / コストN以上
- 元々持つブレードN以下 / ちょうどN
- 『グループ』以外
- 左右サイド指定
- すべて / 1人 / N人までの人数入力

確認済み:

- 効果テンプレート `相手のステージにいるコスト4以下のメンバーを1人までウェイト状態にする。` から `opponent_wait_notify` pending を生成し、2デッキadapter経由で `choice=1` を送ると、相手Cの `PL!-bp5-011`（コスト2）のみがWAITになり、相手Rの `PL!N-pb1-007`（コスト15）はACTIVEのまま残る。
- active側ログに `[ACK] opponent_wait_notify...` と `[DUAL EFFECT][OPPONENT WAIT]... applied=1` が残る。
- 相手側ログにも `[DUAL EFFECT][OPPONENT WAIT]... candidates=['C']` が残る。
- `opponent_wait_count` は相手実stageから1へ同期される。
- adapterのUNDOで相手CがACTIVEへ戻る。
- 2デッキ既存ユニットテストに相手ウェイト実反映/undoケースを追加し、`llocg_dual_v2.tests.test_rule_core` / `llocg_dual_v2.tests.test_legacy_adapter_transactions` 58件OK。

当時残件:

- 2デッキでの相手個別選択UIは、この段階では未実装。現時点では人数入力値に対して、候補をL/C/R順で自動適用する。
- 相手手札公開/破棄、相手控え室/デッキ移動、相手ステージのポジションチェンジは、この段階では未着手。後続の `dual opponent green/deck-top bridge` と `effect-debug residual policy cleanup` までに代表系はbridge化済み。

### 2026-07-21 dual opponent energy/draw bridge

※20260721内部確認: 2デッキ版で、相手側のエネルギーWAIT通知と「相手はカードをN枚引く」任意効果を、1デッキ効果エンジンのpending解決後に相手側Appへ反映するbridgeを追加した。発生源はpendingの `source_cn` を引き継ぎ、両プレイヤーログへ `[DUAL EFFECT]` を残す。カード番号専用分岐なし。

確認済み:

- テンプレート `相手は、エネルギーデッキからエネルギーカードを2枚ウェイト状態で置く。` から `message_ack` が生成され、2デッキadapter経由で `resolve_pending ok` を送ると、相手の `energy_wait` が0→2、core側 `players[1].energy_wait` も2へ同期される。
- 同操作はadapterのUNDOで相手 `energy_wait` とcore側 `energy_wait` が0へ戻る。
- テンプレート `自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置いてもよい。そうした場合、相手はカードを2枚引く。` から `confirm_effect` が生成され、`apply` 解決時に相手の手札が6→8、山札が54→52へ更新される。
- 任意効果の相手ドローもadapterのUNDOで相手の手札・山札枚数が元に戻る。
- 2デッキ既存ユニットテストに相手エネルギーWAIT/相手ドロー/undoケースを追加し、`llocg_dual_v2.tests.test_rule_core` / `llocg_dual_v2.tests.test_legacy_adapter_transactions` 60件OK。

実行した実Appスモーク:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.server import App
from llocg_ui.db import load_cards_db
from llocg_ui.engine import try_apply_effect_template
from llocg_dual_v2.core import DualMatchEngine, load_deck
from llocg_dual_v2.server import LegacyUIAdapter, PlayerViewRuntime
root=Path('llocg_db_out_full')
code1='444782643669fb371f81'
code2='49921c3081c71d2fea40'
deck1=load_deck(root, code1)
deck2=load_deck(root, code2)
engine=DualMatchEngine(deck1, deck2, code1, code2, seed=21)
p1_app=App(root=root, code='dual-smoke-p1', deck_code=code1, seed=21, debug=True)
p2_app=App(root=root, code='dual-smoke-p2', deck_code=code2, seed=22, debug=True)
adapter=LegacyUIAdapter(engine, PlayerViewRuntime('p1',0,'P1','#2578d4',p1_app), PlayerViewRuntime('p2',1,'P2','#d96a22',p2_app))
adapter.action('NEXT', {'indices': []})
adapter.action('NEXT', {'indices': []})
cards=load_cards_db(root)
try_apply_effect_template(p1_app.gs, random.Random(1), cards, '相手は、エネルギーデッキからエネルギーカードを2枚ウェイト状態で置く。', {'source_cn':'DUAL-SMOKE-ENERGY'})
before=p2_app.gs.energy_wait
adapter.player_command('p1','resolve_pending', {'idx': len(p1_app.gs.pending)-1, 'choice':'ok'})
assert (before, p2_app.gs.energy_wait, adapter.engine.state.players[1].energy_wait) == (0, 2, 2)
adapter.action('UNDO', {})
assert (p2_app.gs.energy_wait, adapter.engine.state.players[1].energy_wait) == (0, 0)
try_apply_effect_template(p1_app.gs, random.Random(2), cards, '自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置いてもよい。そうした場合、相手はカードを2枚引く。', {'source_cn':'DUAL-SMOKE-DRAW'})
hand_before=len(p2_app.gs.hand); deck_before=len(p2_app.gs.deck)
adapter.player_command('p1','resolve_pending', {'idx': len(p1_app.gs.pending)-1, 'choice':'apply'})
assert (len(p2_app.gs.hand), len(p2_app.gs.deck)) == (hand_before + 2, deck_before - 2)
adapter.action('UNDO', {})
assert (len(p2_app.gs.hand), len(p2_app.gs.deck)) == (hand_before, deck_before)
print('OK dual opponent energy/draw bridge smoke')
PY
```

追記 20260721:

- 相手ドローは `llocg_ui.engine.draw()` を共有利用する方式へ変更。相手の山札がドロー中またはドロー直後に空になった場合、相手App側で即時リフレッシュし、続くドローを継続する。
- 2デッキユニットテストで、相手山札1枚・相手控え室3枚の状態から相手が2枚引き、1枚目の後に即時リフレッシュして2枚目を引くこと、UNDOで山札/手札/控え室が完全に戻ることを確認。
- 実Appスモークでも同条件を確認済み。

### 2026-07-21 dual opponent green/deck-top bridge

※20260721内部確認: 2デッキ版で、相手控え室→相手デッキ下、および相手デッキ上確認系を実状態へ反映するbridgeを追加した。1デッキ側が生成する `choose_player_for_green_bottom` / `choose_player_for_deck_top_action` を入口にし、相手を選んだ場合だけ2デッキadapterで相手Appの実zoneを更新する。カード番号専用分岐なし。

確認済み:

- `自分か相手を選ぶ。自分は、そのプレイヤーの控え室にあるライブカードを2枚、そのプレイヤーのデッキの一番下に置く。` 系のpendingで相手を選ぶと、相手控え室のLIVE候補2枚が相手デッキ下へ移動し、core側 `waiting_room` / `main_deck` も同期される。
- `自分と相手はそれぞれ、自身の控え室にあるすべてのメンバーカードをシャッフルし、自身のデッキの下に置く。` 系の相手通知解決で、相手控え室のMEMBERだけが相手デッキ下へ移動する。
- `自分か相手を選ぶ。自分は、そのプレイヤーのデッキの一番上のカードを見る。自分はそのカードを控え室に置いてもよい。` で相手を選ぶと、相手デッキ上1枚が表示対象になり、`green` 解決で相手控え室へ移動する。
- `自分か相手を選ぶ。自分は、そのプレイヤーのデッキの上からカードをN枚見る。その中から好きな枚数を好きな順番でデッキの上に置き、残りを控え室に置く。` で相手を選ぶと、保持するカードの順序指定を相手デッキ上へ反映し、残りを相手控え室へ移動する。
- 上記はいずれもadapterのUNDOで戻る。
- 相手デッキ上確認前に相手山札枚数が足りない場合は、共有runtimeの top access refresh を呼び、通常の即時リフレッシュを行う。
- 2デッキ既存ユニットテストは `llocg_dual_v2.tests.test_rule_core` / `llocg_dual_v2.tests.test_legacy_adapter_transactions` で確認対象を追加。

実行した実Appスモーク:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.server import App
from llocg_ui.db import load_cards_db
from llocg_ui.engine import try_apply_effect_template
from llocg_dual_v2.core import DualMatchEngine, load_deck
from llocg_dual_v2.server import LegacyUIAdapter, PlayerViewRuntime
root=Path('llocg_db_out_full')
code1='444782643669fb371f81'
code2='49921c3081c71d2fea40'
deck1=load_deck(root, code1); deck2=load_deck(root, code2)
engine=DualMatchEngine(deck1, deck2, code1, code2, seed=31)
p1_app=App(root=root, code='dual-smoke-p1', deck_code=code1, seed=31, debug=True)
p2_app=App(root=root, code='dual-smoke-p2', deck_code=code2, seed=32, debug=True)
adapter=LegacyUIAdapter(engine, PlayerViewRuntime('p1',0,'P1','#2578d4',p1_app), PlayerViewRuntime('p2',1,'P2','#d96a22',p2_app))
adapter.action('NEXT', {'indices': []}); adapter.action('NEXT', {'indices': []})
cards=load_cards_db(root)
p2_app.gs.deck=['PL!N-pb1-001']; p2_app.gs.green_room=['PL!N-pb1-002','PL!N-pb1-003']; p2_app.gs.hand=[]
p1_app.gs.pending.append({'kind':'confirm_effect','text':'相手はカードを2枚引きます。','options':['apply','skip'],'source_cn':'DUAL-SMOKE-REFRESH'})
adapter.player_command('p1','resolve_pending', {'idx':0,'choice':'apply'})
assert len(p2_app.gs.hand)==2 and getattr(p2_app.gs,'deck_refreshed_this_turn',False)
adapter.action('UNDO', {})
try_apply_effect_template(p1_app.gs, random.Random(1), cards, '自分か相手を選ぶ。自分は、そのプレイヤーのデッキの一番上のカードを見る。自分はそのカードを控え室に置いてもよい。', {'source_cn':'DUAL-SMOKE-TOP1'})
adapter.player_command('p1','resolve_pending', {'idx':len(p1_app.gs.pending)-1,'choice':'opponent'})
assert p1_app.gs.pending and p1_app.gs.pending[-1].get('kind')=='dual_opponent_top1_to_green_or_keep'
top=p2_app.gs.deck[0]
adapter.player_command('p1','resolve_pending', {'idx':len(p1_app.gs.pending)-1,'choice':'green'})
assert top in p2_app.gs.green_room
print('OK dual opponent refresh/top1 smoke')
PY
```

残件:

- 旧残件: 相手手札公開/破棄、相手ステージのポジションチェンジ。以下の20260721追記で代表系をbridge化した。

追記 20260721:

- 相手手札破棄の代表系を2デッキ実状態へ反映するbridgeを追加。`opponent_optional_discard_hand_else_self_gain_icons` で相手が破棄を選んだ場合、相手の実手札候補を `dual_opponent_discard_from_hand` pending に表示し、選んだカードを相手控え室へ置く。相手手札から控え室へ置かれた通常誘発を落とさないよう、共有runtimeの手札破棄誘発キューも呼ぶ。
- `相手は手札からライブカードをN枚控え室に置いてもよい。そうしなかった場合...` 系は、相手が置く側を選んだ場合にLIVE候補だけを表示する。
- 好きなもの回答系の相手側副作用をbridge化。回答 `あなた` では相手も共有 `draw()` 経由で1枚引き、回答 `それ以外` では相手ステージ全メンバーにもブレード+1を付与する。
- `相手の手札を、自分は見ないでN枚選び公開する。これにより公開されたカードの中にライブカードがない場合...` 系は、ユーザーの条件判断confirmに任せず、2デッキadapterで相手実手札からランダム公開してLIVE有無を判定する。LIVEなしの場合だけ自分が共有 `draw()` 経由で引き、公開カードは確認pendingに表示する。
- 相手ポジションチェンジの代表系をbridge化。`相手ステージのメンバー1人をこのメンバーの正面のエリアへ` は、このメンバーの位置から相手側の正面エリアを決め、相手ステージの移動元を選択してswapする。`自分と相手は、自身のステージのセンターにいるメンバーをポジションチェンジする。` の相手センター分も、相手CからL/Rへの選択pendingにする。
- `相手も同じ移動` のC→L / L→R / R→C一括移動通知は、相手stageにも同じ回転を反映する。
- 2デッキ既存ユニットテストは `llocg_dual_v2.tests.test_rule_core` / `llocg_dual_v2.tests.test_legacy_adapter_transactions` 72件OK。

実行した実Appスモーク:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 - <<'PY'
from pathlib import Path
from llocg_ui.server import App
from llocg_ui.engine import StageSlot
from llocg_dual_v2.core import DualMatchEngine, load_deck
from llocg_dual_v2.server import LegacyUIAdapter, PlayerViewRuntime
root=Path('llocg_db_out_full')
code1='444782643669fb371f81'; code2='49921c3081c71d2fea40'
deck1=load_deck(root, code1); deck2=load_deck(root, code2)
engine=DualMatchEngine(deck1, deck2, code1, code2, seed=41)
p1_app=App(root=root, code='dual-smoke-p1', deck_code=code1, seed=41, debug=True)
p2_app=App(root=root, code='dual-smoke-p2', deck_code=code2, seed=42, debug=True)
adapter=LegacyUIAdapter(engine, PlayerViewRuntime('p1',0,'P1','#2578d4',p1_app), PlayerViewRuntime('p2',1,'P2','#d96a22',p2_app))
adapter.action('NEXT', {'indices': []}); adapter.action('NEXT', {'indices': []})
p2_app.gs.hand=['PL!N-pb1-001','PL!N-pb1-002']
p1_app.gs.pending.append({'kind':'opponent_optional_discard_hand_else_self_gain_icons','text':'相手は手札を1枚控え室に置いてもよい。','options':['opponent_discard','not_discard'],'source_cn':'DUAL-SMOKE-HAND','source_pos':'C','discard_n':1,'icons':'<(ブレード)>'})
adapter.player_command('p1','resolve_pending', {'idx':0,'choice':'opponent_discard'})
assert p1_app.gs.pending and p1_app.gs.pending[-1].get('kind')=='dual_opponent_discard_from_hand'
adapter.player_command('p1','resolve_pending', {'idx':len(p1_app.gs.pending)-1,'choice':'PL!N-pb1-002'})
assert 'PL!N-pb1-002' in p2_app.gs.green_room and 'PL!N-pb1-002' not in p2_app.gs.hand
adapter.action('UNDO', {})
assert p2_app.gs.hand==['PL!N-pb1-001','PL!N-pb1-002']
p1_app.gs.stage['L']=StageSlot('DUAL-SMOKE-POS')
p2_app.gs.stage['C']=StageSlot('PL!N-pb1-003')
p2_app.gs.stage['R']=None
p1_app.gs.pending.append({'kind':'effect_notice','text':'相手ステージのメンバー1人をこのメンバーの正面にポジションチェンジします。','options':['ok'],'source_cn':'DUAL-SMOKE-POS'})
adapter.player_command('p1','resolve_pending', {'idx':len(p1_app.gs.pending)-1,'choice':'ok'})
assert p1_app.gs.pending and p1_app.gs.pending[-1].get('kind')=='dual_opponent_position_change'
adapter.player_command('p1','resolve_pending', {'idx':len(p1_app.gs.pending)-1,'choice':'C'})
assert p2_app.gs.stage['R'] and p2_app.gs.stage['R'].cardnumber=='PL!N-pb1-003'
print('OK dual opponent hand/position smoke')
PY
```

残件:

- 2デッキ用UIでは情報秘匿不要のため、active側boardに相手手札候補を表示して選ぶ現行UIは残件扱いしない。1デッキ用リモートのパブリックウィンドウでは、従来どおり public view redaction が秘匿境界になる。
- 相手ポジションの「正面」対応は L↔R / C↔C の対面対応で実装。盤面表示/ルール解釈で逆向き定義が必要ならここだけ調整対象。

### 2026-07-21 app update cancel / Windows launcher close

実装内容:

- データ更新画面に「更新中断」ボタンを追加。更新中のみ表示し、押下時に `/api/update/stop` から実行中の更新処理を停止する。
- 更新中断後のジョブ状態を `cancelled` / `中断` として保持し、更新監視スレッドが後から `failed` に上書きしないようにした。
- Windowsでは更新処理が追加の子プロセスを起こす場合に備え、更新停止時は `taskkill /T /F` でプロセスツリーごと終了する。mac/Linuxでは既存どおりプロセスグループへ停止シグナルを送る。
- Windows用 `launch_loveca.bat` は、`pythonw` または `pyw` が見つかる場合にターミナルを残さない専用起動へ変更。見つからない場合は従来どおりコンソール起動にフォールバックする。
- アプリ終了ボタン押下後の専用ウインドウ閉じ処理を複数回リトライするようにした。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./run_loveca_app.py ./loveca_app/core.py ./loveca_app/web.py ./loveca_app/main.py ./loveca_app/launcher.py ./loveca_app/assets.py

python3 - <<'PY'
import subprocess
from pathlib import Path
from loveca_app.core import AppState
app=AppState(Path('.').resolve())
proc=subprocess.Popen(['python3','-c','import time; time.sleep(60)'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
with app.lock:
    app.update_process=proc
    app.update_job.reset('cancel-smoke')
    app.update_job.status='running'
    app.update_job.stage='実行中'
ok,msg=app.stop_update(reason='user')
assert ok, msg
assert proc.poll() is not None
assert app.update_job.status == 'cancelled'
assert app.update_job.stage == '中断'
print('OK update cancel smoke')
PY
```

※20260721内部確認: mac上の内部スモークでは更新中断APIの中核処理は正常。Windows固有の `pythonw` / `pyw` 起動と `taskkill /T /F` は配布zip反映後に実機確認対象。

追記 20260721:

- Windowsでアプリ本体を `pythonw.exe` から起動した場合、データ更新コマンドとその内部のcompile/audit/image処理まで `pythonw.exe` で実行され、失敗時の詳細ログが欠けることを確認。アプリ起動は `pythonw.exe` のまま許容しつつ、更新処理と更新スクリプト内の子コマンドは同じフォルダの `python.exe` へ切り替えるようにした。
- ユーザー環境で出ていたcompile失敗は、ローカル現行DBに対する `llocg_sim_tool_v7.py compile` では再現しなかった。次回Windows実行時は `[APP-UPDATE] command=...python.exe ...` と表示され、もしcompileが再発しても詳細エラーがログに出る想定。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/core.py ./llocg_update_database.py

python3 - <<'PY'
import os, sys, tempfile
from pathlib import Path
from unittest import mock
from loveca_app.core import console_python_executable as app_py
import llocg_update_database as updater
with tempfile.TemporaryDirectory() as td:
    d=Path(td)
    (d/'pythonw.exe').write_text('', encoding='utf-8')
    (d/'python.exe').write_text('', encoding='utf-8')
    fake=str(d/'pythonw.exe')
    with mock.patch.object(sys, 'executable', fake), mock.patch('loveca_app.core.platform.system', lambda: 'Windows'):
        assert os.path.basename(app_py()).lower() == 'python.exe'
    with mock.patch.object(sys, 'executable', fake), mock.patch('llocg_update_database.os.name', 'nt'):
        assert os.path.basename(updater.console_python_executable()).lower() == 'python.exe'
print('OK pythonw switches to python.exe for update commands')
PY

python3 ./llocg_sim_tool_v7.py compile --csv ./llocg_db_out_full/cards_min_tokv1.csv --out /private/tmp/loveca_compile_smoke.json --patterns-dir ./llocg_db_out_full
```

追記2 20260721:

- Windows実機ログで `llocg_sim_tool_v7.py compile` が `ModuleNotFoundError: No module named 'yaml'` により失敗することを確認。更新用依存チェックに `("yaml", "PyYAML")` が不足していたため、`PyYAML` を自動導入対象へ追加した。
- 次回更新時、`yaml` が未導入の環境では `[PY-DEPS] Missing Python packages... PyYAML` の後にpip導入が走り、その後compileへ進む想定。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_update_database.py ./llocg_sim_tool_v7.py

python3 - <<'PY'
import llocg_update_database as upd
from unittest import mock
real_find = upd.importlib.util.find_spec
def fake_find(name):
    if name == 'yaml':
        return None
    return real_find(name)
with mock.patch('llocg_update_database.importlib.util.find_spec', fake_find):
    missing = upd.missing_update_python_packages()
assert ('yaml', 'PyYAML') in missing
print('OK PyYAML dependency is detected when yaml is missing')
PY

python3 ./llocg_sim_tool_v7.py compile --csv ./llocg_db_out_full/cards_min_tokv1.csv --out /private/tmp/loveca_compile_smoke.json --patterns-dir ./llocg_db_out_full
```

追記3 20260721:

- Windowsでアプリを `pythonw.exe` 起動にした状態からDB更新を実行すると、更新用 `python.exe` のコンソールウインドウが前面に出ることを確認。ログはアプリ側で取得できているため、Windowsの更新子プロセスには `CREATE_NO_WINDOW` を付け、コンソールウインドウを作らないようにした。
- 対象はアプリ本体からの `llocg_update_database.py` 起動と、更新スクリプト内の `scrape` / `normalize` / `compile` / `audit` / pip確認・導入コマンド。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/core.py ./llocg_update_database.py

python3 - <<'PY'
from unittest import mock
import loveca_app.core as core
import llocg_update_database as upd
with mock.patch('loveca_app.core.platform.system', lambda: 'Windows'), mock.patch('loveca_app.core.subprocess.CREATE_NO_WINDOW', 0x08000000, create=True):
    assert core.no_window_subprocess_kwargs() == {'creationflags': 0x08000000}
with mock.patch('llocg_update_database.os.name', 'nt'), mock.patch('llocg_update_database.subprocess.CREATE_NO_WINDOW', 0x08000000, create=True):
    assert upd.no_window_subprocess_kwargs() == {'creationflags': 0x08000000}
print('OK CREATE_NO_WINDOW kwargs')
PY
```

### 2026-07-21 deck builder image fallback

実装内容:

- デッキ構築ツールのカード画像が読み込めない場合に `visibility:hidden` で透明化していた箇所を、共通 `fallbackCardImage()` で `/card-image` のフォールバック画像へ差し替える形に変更した。
- `/card-image` はカード画像が見つからない場合に従来どおり `NoImage.PNG` を優先し、NoImage自体も無い環境ではサーバ生成のSVGプレースホルダーを返すようにした。これにより、配布直後・UI画像バンドル未配置・カード画像未取得の状態でも、デッキ構築画面の画像枠が透明にならない。
- 対象画面はデッキ構築のデッキ行、検索結果、デッキ分析カード、デッキコード読込結果。デッキ詳細画面は既存の「画像なし」ラベル表示を維持する。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/web.py ./loveca_app/core.py ./run_loveca_app.py
git diff --check -- loveca_app/web.py

python3 ./run_loveca_app.py --host 127.0.0.1 --port 8891 --window-mode none --skip-startup-update

curl -s -I 'http://127.0.0.1:8891/card-image?card_no=NO-SUCH-CARD'
curl -s 'http://127.0.0.1:8891/decks/new' | rg -n "fallbackCardImage|search-card-image" -C 2
curl -s 'http://127.0.0.1:8891/api/cards/search?limit=1' | python3 -m json.tool | rg -n "variant_id|card_no|has_image" -C 1
```

※20260721内部確認: ローカルではNoImageが存在するため、存在しないカード番号でも `/card-image` はNoImage PNGをHTTP 200で返すことを確認。NoImage未配置時は同経路でSVGプレースホルダーを返す実装にした。

### 2026-07-21 first-run image directory / asset bundle / card image fetch

実装内容:

- 起動時に `llocg_db_out_full/card_images`、`llocg_db_out_full/card_images/texticons`、`llocg_db_out_full/preview_card_images` を必ず作成するようにした。配布zipが空ディレクトリを保持できない場合でも、初回起動後に画像配置先が存在する。
- UI用画像バンドル探索を、`loveca` フォルダ直下だけでなく、`loveca` の親フォルダ、現在の作業フォルダ、ユーザーの `Downloads` まで広げた。`loveca-ui-assets.zip` / `loveca_ui_assets.zip` と展開済み `loveca-ui-assets` / `loveca_ui_assets` に対応。
- DB更新時、`official_image_manifest.json` が同梱済みでも `card_images` に実カード画像が無い場合は初回画像取得として全カードを `image_fetch_targets` に入れるようにした。これにより、配布zipの「manifestあり・画像なし」状態で画像取得がスキップされない。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/assets.py ./loveca_app/main.py ./llocg_update_database.py

PYTHONPATH=/Users/tekitou/Desktop/gsim/loveca python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
import zipfile
from loveca_app.assets import ensure_ui_assets_from_local_bundle
with TemporaryDirectory() as td:
    base=Path(td)
    root=base/'loveca'
    root.mkdir()
    bundle=base/'loveca-ui-assets.zip'
    with zipfile.ZipFile(bundle,'w') as z:
        z.writestr('loveca-ui-assets/llocg_db_out_full/card_images/NoImage.PNG', b'png')
    result=ensure_ui_assets_from_local_bundle(root)
    assert (root/'llocg_db_out_full/card_images').is_dir()
    assert (root/'llocg_db_out_full/card_images/texticons').is_dir()
    assert (root/'llocg_db_out_full/preview_card_images').is_dir()
    assert (root/'llocg_db_out_full/card_images/NoImage.PNG').read_bytes()==b'png'
print('OK ui asset parent search and image dirs')
PY

python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
import llocg_update_database as upd
with TemporaryDirectory() as td:
    root=Path(td)
    image_dir=root/'card_images'
    image_dir.mkdir()
    assert not upd.scan_image_cardnumbers(image_dir)
    (image_dir/'NoImage.PNG').write_bytes(b'x')
    assert not upd.scan_image_cardnumbers(image_dir)
print('OK empty/noimage-only card_images triggers initial image fetch')
PY
```

※20260721内部確認: 実際の画像ダウンロードは外部通信と時間がかかるため、ここでは初回判定条件とディレクトリ/バンドル展開経路を内部確認した。Windows実機では更新ログに `[IMAGE-FETCH-INIT]` が出れば初回画像取得対象化が動いている。

### 2026-07-21 effect-debug residual policy cleanup

※20260721内部確認: 効果処理関連の残件を現行仕様に合わせて再分類した。2デッキ用UIでは秘匿不要のため、相手手札候補をactive側で表示することは不具合扱いしない。1デッキ版では相手個別カードstateを持たないため、相手成功ライブ置き場、相手ステージ、相手ライブカード置き場などの一部比較・反映は手入力/手動反映を正式経路とする。

確認結果:

- 旧デバッグ文書に残る `発生源なし` / `自動効果の無言処理` 系の代表指摘は、現行では `source_cn`、実行中効果本文、`message_ack` / `confirm_effect` / `auto_order` で確認対象を渡す方針に整理済み。直近P1/P2/2デッキbridge確認では再発なし。
- 旧デバッグ文書に残る相手未モデルコメントは、1デッキ版では手動確認仕様、2デッキ版では相手context/action bridgeで実反映する対象、という分類へ更新済み。
- UI目視・操作感に属するものは runtime 成否とは分離し、ユーザー実機確認用の日本語チェックリスト `docs/handoffs/loveca_handoff_20260721_visual_confirmation_checklist_ja.md` へ集約する。

### 2026-07-21 image fetch progress log / deck copy button

実装内容:

- `llocg_fetch_all_card_images.py` に開始ログと `--progress-every` を追加し、初期値10件ごとに `[IMAGE-FETCH-PROGRESS]` を即時表示するようにした。
- `llocg_update_database.py` からPython子スクリプトを呼ぶ際、`.py` 実行は `-u` 付きに自動変換し、画像取得中のログが更新画面へ溜まらず流れるようにした。
- デッキ一覧の操作欄に「コピー」ボタンを追加した。押すと元デッキを維持したまま、新しいデッキファイルとして保存し、コピー元情報をメタデータに残す。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_fetch_all_card_images.py ./llocg_update_database.py ./loveca_app/core.py ./loveca_app/web.py

python3 - <<'PY'
import llocg_update_database as upd
assert upd.unbuffered_python_command(['python3', 'tool.py', '--x']) == ['python3', '-u', 'tool.py', '--x']
assert upd.unbuffered_python_command(['python3', '-u', 'tool.py']) == ['python3', '-u', 'tool.py']
assert upd.unbuffered_python_command(['python3', '-m', 'json.tool']) == ['python3', '-m', 'json.tool']
print('OK unbuffered python command injection')
PY

python3 ./llocg_fetch_all_card_images.py --help

python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from loveca_app.core import AppState

with TemporaryDirectory() as td:
    root = Path(td).resolve()
    db = root / 'llocg_db_out_full'
    deckdir = db / 'decklists'
    deckdir.mkdir(parents=True)
    cards = [
        {'cardnumber':'PL!N-test-001','cardname':'member','card_type':'メンバー'},
        {'cardnumber':'PL!N-test-002','cardname':'live','card_type':'ライブ'},
    ]
    (db / 'cards_min_tokv1.json').write_text(json.dumps(cards, ensure_ascii=False), encoding='utf-8')
    (db / 'cards_compiled_v7h.json').write_text('[]', encoding='utf-8')
    source = deckdir / 'deck_source.tsv'
    source.write_text('count\tcard_no\trarity\tname\tvariant_id\n4\tPL!N-test-001\tN\tmember\tPL!N-test-001__N\n1\tPL!N-test-002\tN\tlive\tPL!N-test-002__N\n', encoding='utf-8')
    source.with_suffix('.meta.json').write_text(json.dumps({'deck_id':'source','deck_name':'テストデッキ','tags':['確認']}, ensure_ascii=False), encoding='utf-8')
    app = AppState(root)
    record = app.copy_deck('llocg_db_out_full/decklists/deck_source.tsv')
    assert record['name'] == 'テストデッキ のコピー'
    assert Path(root / record['path']).exists()
    meta = json.loads((root / record['path']).with_suffix('.meta.json').read_text(encoding='utf-8'))
    assert meta['source'] == 'deck_copy'
    assert meta['copied_from'].endswith('deck_source.tsv')
    _, rows = app.read_deck_rows(record['path'])
    assert len(rows) == 2
print('OK deck copy creates a new deck and preserves variant rows')
PY
```

※20260721内部確認: 実画像取得は外部通信と時間を伴うためここではヘルプと呼び出し変換を確認。実機更新では `[IMAGE-FETCH-START]` と `[IMAGE-FETCH-PROGRESS]` が更新ログへ表示される想定。

### 2026-07-21 cached reprint image route for RM / SECL / L2 / SRL

実装内容:

- RM / SECL / L2 / SRL を再録系画像レアリティとして扱い、通常画像の取得成功とは別ルートで補足できるようにした。
- `llocg_db_tool_v7.py` の official image manifest 生成時、既存HTTPキャッシュ内の公式カードリストHTMLを走査し、`card` 属性と画像URLから再録系画像を逆引きしてmanifestへ補強するようにした。
- `llocg_fetch_all_card_images.py` でも同じくHTTPキャッシュ逆引きを行い、manifest未更新でも `PL!S-bp5-021 -> BP05/PL!S-bp5-SECL.png` のような番号省略URLを直接取得候補へ追加するようにした。
- 再録系画像の推測URLでは、カード番号内の product token を画像フォルダ側へ合わせた候補も試す。例: `BP05 + PL!S-bp3-021 + SECL` から `PL!S-bp5-021-SECL.png` と `PL!S-bp5-SECL.png` を追加する。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_fetch_all_card_images.py ./llocg_db_tool_v7.py

python3 - <<'PY'
from llocg_fetch_all_card_images import remote_filename_variants
cases=[
 ('BP05','PL!S-bp3-021','SECL','PL!S-bp5-SECL.png'),
 ('BP05','PL!S-bp3-021','SECL','PL!S-bp5-021-SECL.png'),
 ('BP05','PL!-bp3-020','SECL','PL!-bp5-SECL.png'),
 ('PBSP','PL!SP-bp1-025','L2','PL!SP-bp1-025-L2.png'),
]
for folder, cardno, rarity, expected in cases:
    got=remote_filename_variants(folder, cardno, rarity)
    assert expected in got, (expected, got)
print('OK reprint filename variants')
PY

python3 - <<'PY'
from pathlib import Path
from llocg_fetch_all_card_images import _cached_reprint_image_index
idx=_cached_reprint_image_index(Path('llocg_db_out_full'), ['PL!S-bp5-021','PL!-bp3-020','PL!N-bp3-028','PL!SP-bp1-025'])
assert any(e['rarity_norm']=='SECL' and e['remote_filename']=='PL!S-bp5-SECL.png' for e in idx['PL!S-bp5-021'])
assert any(e['rarity_norm']=='SECL' and e['remote_filename']=='PL!-bp3-SECL.png' for e in idx['PL!-bp3-020'])
print('OK cached reprint index')
PY

python3 - <<'PY'
from pathlib import Path
import llocg_db_tool_v7 as db
items=db.parse_cached_official_reprint_items(Path('llocg_db_out_full/_http_cache'), {'PL!S-bp5-021','PL!-bp3-020','PL!N-bp3-028','PL!SP-bp1-025'})
assert any(item['cardnumber']=='PL!S-bp5-021' and item['remote_filename']=='PL!S-bp5-SECL.png' for item in items)
assert any(item['cardnumber']=='PL!-bp3-020' and item['remote_filename']=='PL!-bp3-SECL.png' for item in items)
print('OK db cached manifest enrichment parser')
PY
```

※20260721内部確認: 外部通信なしの既存HTTPキャッシュ確認。実画像のHTTP取得は実機更新時に `[IMAGE-FETCH-START] reprint_cache_cards=...` が出る状態で確認する。

### 2026-07-21 reprint image targets in update pipeline

実装内容:

- DB更新パイプライン側で、公式カードリストHTMLキャッシュ内の RM / SECL / L2 / SRL 画像候補を確認するようにした。
- 通常更新で `new_cards=0` かつ `official_manifest_targets=0` の場合でも、再録系画像候補があり、該当レアリティ画像が未取得なら `image_manifest_targets` / `image_fetch_targets` へ追加する。
- 更新ログに `[REPRINT-IMAGE-TARGETS] cached_candidates=N missing_cards=M` と `[IMAGE-MANIFEST-MODE] ... reprint_missing=M ...` が出るようにした。`M>0` なら画像取得フェーズがスキップされない。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_update_database.py

python3 - <<'PY'
from pathlib import Path
import llocg_update_database as upd
pairs=upd.scan_image_rarity_pairs(Path('llocg_db_out_full/card_images'))
targets=upd.cached_reprint_image_targets(
    cache_dir=Path('llocg_db_out_full/_http_cache'),
    wanted_cardnumbers={'PL!S-bp5-021','PL!-bp3-020','PL!N-bp3-028','PL!SP-bp1-025'},
    existing_pairs=pairs,
)
assert 'PL!S-bp5-021' in targets or ('PL!S-bp5-021','SECL') in pairs
assert 'PL!-bp3-020' in targets or ('PL!-bp3-020','SECL') in pairs
print('OK reprint missing target detection')
PY

git diff --check -- llocg_update_database.py
```

※20260721内部確認: ローカルキャッシュでは `cached_candidates=10 missing_cards=3` を確認。実機では更新ログに `reprint_missing` が表示され、未取得再録画像がある場合は `IMAGE-FETCH-MODE targets=0` で止まらない想定。

### 2026-07-21 reprint image display resolution

実装内容:

- デッキ内容表示/デッキ構築で使う画像バリアント解決に、`official_image_manifest.json` の `remote_filename` 対応表を追加した。
- 公式画像が収録弾フォルダ側のファイル名で保存されていても、manifest上の `cardnumber` / `rarity_norm` を使って元カードへ紐付けるようにした。
- `L2` / `SEC2` / `PR2` / `PE2` など、数値付きレアリティの画像ファイル名からのレアリティ抽出漏れを修正した。`L2` は表示・検索上 `L＋` として扱う。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/core.py

python3 - <<'PY'
from pathlib import Path
from loveca_app.core import AppState
app=AppState(Path('.').resolve())
assert app.find_card_image('PL!S-bp5-021', rarity='SECL') is not None
assert app.find_card_image('PL!SP-pb1-026', rarity='L＋') is not None
assert app.find_card_image('PL!SP-pb1-026', rarity='L2') is not None
print('OK reprint/L2 image resolution')
PY

git diff --check -- loveca_app/core.py
```

※20260721内部確認: デッキ内容表示と同じ `find_card_image(card_no, rarity=...)` 経路で確認。`PL!SP-pb1-026-L2.png` が `L＋` バリアントとして解決されることを確認した。

### 2026-07-21 deck view lookup for reprint product-folder aliases

実装内容:

- デッキ内容確認の `card_no + rarity` 画像検索で、公式カードリストHTMLキャッシュから作った `remote_filename -> 元カード番号/レアリティ` 対応表も使うようにした。
- 例: 元カード番号 `PL!-bp3-012` / レアリティ `RM` の画像が、収録弾フォルダ `BP05` 内の別名ファイルとして保存されている場合でも、デッキ内容確認から該当画像へ到達できる。
- デッキ行の `rarity` が空でも、保存済み `variant_id` が `card_no|RM|...` 形式なら、そこからレアリティを補完して画像検索するようにした。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/core.py

python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from loveca_app.core import AppState

with TemporaryDirectory() as td:
    root=Path(td).resolve()
    db=root/'llocg_db_out_full'
    (db/'card_images'/'BP05').mkdir(parents=True)
    (db/'_http_cache').mkdir(parents=True)
    (db/'cards_min_tokv1.json').write_text(json.dumps([
        {'cardnumber':'PL!-bp3-012','cardname':'test','card_type':'メンバー'},
    ], ensure_ascii=False), encoding='utf-8')
    (db/'cards_compiled_v7h.json').write_text('[]', encoding='utf-8')
    image_path=db/'card_images'/'BP05'/'PL!-bp5-012-RM.png'
    image_path.write_bytes(b'fake-png')
    (db/'_http_cache'/'cached.html').write_text('''
      <div card="PL!-bp3-012-RM"><img src="/wordpress/wp-content/images/cardlist/BP05/PL!-bp5-012-RM.png"></div>
    ''', encoding='utf-8')
    app=AppState(root)
    assert app.find_card_image('PL!-bp3-012', rarity='RM') == image_path
    row={'count':'1','card_no':'PL!-bp3-012','rarity':'','variant_id':'PL!-bp3-012|RM|old','name':''}
    display=app.card_display_data(row)
    assert display['rarity']=='RM', display
    assert app.find_card_image(display['card_no'], variant_id=display['variant_id'], rarity=display['rarity']) == image_path
print('OK deck view reprint alias lookup')
PY

git diff --check -- loveca_app/core.py
```

※20260721内部確認: ローカル実DBに `PL!-bp3-012` のRM実画像が無いため、一時DBで「元カード番号bp3、保存先フォルダ/ファイル名bp5」の状態を作り、デッキ内容確認と同じ画像解決経路を確認した。

### 2026-07-21 UI asset bundle date-suffix extraction

実装内容:

- UI画像バンドル自動配置で、`loveca-ui-assets.zip` / `loveca_ui_assets.zip` の完全一致に加えて、`loveca-ui-assets-20260721.zip` のような日付付きzipも検出するようにした。
- 展開済みフォルダも `loveca-ui-assets-20260721` のような日付付き名称を許容するようにした。
- 本体フォルダ直下だけでなく、本体フォルダの親階層、起動時カレント、Downloads の探索順は維持した。
- READMEの初回起動手順に、日付付きUI画像バンドルをそのまま置ける旨を追記した。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/assets.py ./loveca_app/main.py ./tools/build_loveca_distribution.py

python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
from loveca_app.assets import ensure_ui_assets_from_local_bundle

source = Path('_codex_outputs/github_release/loveca-ui-assets-20260721.zip').resolve()
with TemporaryDirectory() as td:
    root = Path(td) / 'loveca'
    root.mkdir()
    shutil.copy2(source, root / source.name)
    result = ensure_ui_assets_from_local_bundle(root)
    assert Path(result.source).name == 'loveca-ui-assets-20260721.zip'
    assert (root / 'llocg_db_out_full/card_images/NoImage.PNG').exists()
    assert (root / 'llocg_db_out_full/card_images/back.png').exists()
    assert (root / 'llocg_db_out_full/card_images/texticons/heart_00.png').exists()
    print('OK ui asset bundle extraction', len(result.installed))
PY

python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
from loveca_app.assets import ensure_ui_assets_from_local_bundle

source = Path('_codex_outputs/github_release/loveca-ui-assets-20260721.zip').resolve()
with TemporaryDirectory() as td:
    parent = Path(td)
    root = parent / 'loveca'
    root.mkdir()
    shutil.copy2(source, parent / source.name)
    result = ensure_ui_assets_from_local_bundle(root)
    assert Path(result.source).name == 'loveca-ui-assets-20260721.zip'
    assert (root / 'llocg_db_out_full/card_images/NoImage.PNG').exists()
    print('OK parent folder ui asset bundle extraction', len(result.installed))
PY
```

※20260721内部確認: 修正前は日付付き `loveca-ui-assets-20260721.zip` を本体フォルダ直下へ置いても `source="" installed=0` となり、`NoImage.PNG` が配置されなかった。修正後は同じzipで `installed=13`、親フォルダ配置でも `installed=13` を確認した。

### 2026-07-22 update image progress / public hand instance reveal / pb1 R 三船栞子 generic route

実装内容:

- 起動時DB更新のカード画像取得で `llocg_fetch_all_card_images.py` に `--progress-every 1` を渡すようにした。初回など画像確認対象が多い場合でも、1枚ごとにログが出て停止して見えにくくなる。
- 公開して手札に加えたカードの公開情報を、カード番号ではなく手札内の `instance_id` で保持するようにした。同名カードが複数ある場合でも、実際に公開されて手札に加わった個体だけを公開表示対象にする。
- pb1のR三船栞子相当 `PL!N-pb1-010` の登場時「以下から1つを選ぶ。」効果を、旧 `choose_enter_effect_mode` ではなく汎用 `choose_effects` ルートへ接続した。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_update_database.py ./llocg_ui/server.py ./llocg_ui/views.py ./llocg_ui/engine.py

python3 ./llocg_fetch_all_card_images.py --help | rg -n "progress-every"

python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, handle_enter_auto
root = Path('.')
cards = load_cards_db(root)
gs = GameState(root=str(root), code='TEST', seed=1, debug=True)
gs.phase = 'MAIN'
handle_enter_auto(gs, cards, 'C', 'PL!N-pb1-010')
assert gs.pending and gs.pending[0]['kind'] == 'choose_effects'
assert gs.pending[0].get('options') == [
    'エネルギーを1枚アクティブにする。',
    '自分の控え室にある『虹ヶ咲』のライブカードを2枚まで好きな順番でデッキの上に置く。',
]
print('OK PL!N-pb1-010 choose_effects route')
PY

python3 - <<'PY'
from llocg_ui.views import make_public_state
state = {
  'view_mode':'private', 'turn':1, 'phase':'MAIN',
  'hand':['PL!X-test-001','PL!X-test-001'], 'hand_count':2,
  'deck':[], 'green_room':[], 'set_zone':[], 'resolve_zone':[], 'success_zone':[],
  'stage':{'L':None,'C':None,'R':None}, 'stage_detail':{}, 'pending':[],
  'public_reveal_events':[], 'public_hand_reveal_events':[],
  'public_hand_revealed_cards':['PL!X-test-001'],
  'public_hand_revealed_instance_ids':['iid2'],
  'card_instances':{'deck':[], 'hand':['iid1','iid2'], 'green_room':[], 'set_zone':[], 'resolve_zone':[], 'success_zone':[], 'stage':{}},
  'card_instance_meta':{'iid1':{'id':'iid1','cardnumber':'PL!X-test-001','rarity':'N'}, 'iid2':{'id':'iid2','cardnumber':'PL!X-test-001','rarity':'RM'}},
  'cn2name':{'PL!X-test-001':'同名カード'}, 'cn2label':{}, 'cn2type':{}, 'cn2is_live':{},
  'cn2yell_hearts':{}, 'cn2yell_draw_icons':{}, 'cn2yell_score_icons':{},
  'cn2image_rarity':{}, 'cn2image_variant_id':{}, 'cn2group':{}, 'cn2unit':{}, 'cn2cost':{}, 'cn2score':{}
}
out = make_public_state(state)
assert out['card_instances'].get('public_hand_revealed') == ['iid2']
assert sorted(out['card_instance_meta'].keys()) == ['iid2']
print('OK public hand reveal keeps exact duplicate instance only')
PY

git diff --check -- llocg_update_database.py llocg_ui/server.py llocg_ui/views.py llocg_ui/engine.py

python3 - <<'PY'
from llocg_ui.server import App
from llocg_ui.engine import GameState
app = App.__new__(App)
app.gs = GameState(root='.', code='TEST', seed=1, debug=True)
app.gs.phase = 'MAIN'
app.gs.turn = 1
app.gs.hand = ['PL!X-test-001', 'PL!X-test-001']
app.gs.green_room = []
app.gs.resolve_zone = []
app.gs.success_zone = []
app.gs.set_zone = []
app.card_instance_zones = {'hand':['iid1','iid2'], 'deck':[], 'green_room':[], 'resolve_zone':[], 'success_zone':[], 'set_zone':[], 'stage:L':[], 'stage:C':[], 'stage:R':[]}
app.card_instance_meta = {'iid1':{'id':'iid1','cardnumber':'PL!X-test-001'}, 'iid2':{'id':'iid2','cardnumber':'PL!X-test-001'}}
app.card_instance_seq = 2
app._public_hand_revealed_turn = 1
app._public_hand_revealed_cards = []
app._public_hand_revealed_instance_ids = []
app._public_hand_reveal_events = []
app._public_hand_reveal_seq = 0
app._public_hand_before_source_counts = {}
app._remember_public_hand_reveals_after_cmd(['PL!X-test-001'], ['PL!X-test-001'], 'unit-test', 0, ['iid1'])
assert app._public_hand_revealed_cards == ['PL!X-test-001']
assert app._public_hand_revealed_instance_ids == ['iid2']
print('OK server remembers exact newly-added duplicate instance')
PY

python3 ./tools/build_loveca_distribution.py --target macos --output ./_codex_outputs/github_release/loveca-macos-20260721.zip
python3 ./tools/build_loveca_distribution.py --target windows --output ./_codex_outputs/github_release/loveca-windows-20260721.zip
python3 ./tools/build_loveca_distribution.py --target source --output ./_codex_outputs/github_release/loveca-source-20260721.zip
gh release upload v2026.07.21 ./_codex_outputs/github_release/loveca-macos-20260721.zip ./_codex_outputs/github_release/loveca-windows-20260721.zip ./_codex_outputs/github_release/loveca-source-20260721.zip --clobber
gh release view v2026.07.21 --json assets,url
```

※20260722内部確認: `py_compile` 通過。`llocg_fetch_all_card_images.py --help` に `--progress-every` が存在することを確認。`PL!N-pb1-010` は `choose_effects` へ入り、2つの選択肢が汎用ルートで出ることを確認。同名カード2枚の公開ビュー状態では、公開個体ID `iid2` のみが `public_hand_revealed` / `card_instance_meta` に残ることを確認。サーバー側の公開手札記録でも、元から手札にいた同名 `iid1` ではなく、増えた同名 `iid2` だけが公開対象になることを確認した。GitHub Release `v2026.07.21` の本体zip3種（macOS / Windows / source）を上書き済み。Release上のアセットは本体3種のみで、UIアセットzipはアップロードしていない。

### 2026-07-22 DB update missing existing card images refetch

実装内容:

- 既存 `card_images` フォルダが空でない場合でも、DB内のリリース済みカード番号と実画像ファイルを照合し、欠落しているカードを画像取得対象に追加するようにした。
- 更新ログの `[IMAGE-MANIFEST-MODE]` に `missing_existing=<件数>` を表示するようにした。
- 画像取得後にもリリース済みカード画像の欠落が残っている場合、`[DONE] Loveca DB + image update completed` まで進めず、欠落件数と先頭サンプルを表示してエラー終了するようにした。
- 前回追加した画像取得ログの `--progress-every 1` は維持。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_update_database.py

python3 - <<'PY'
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from llocg_update_database import missing_released_image_targets
with TemporaryDirectory() as td:
    root = Path(td) / 'card_images'
    (root / 'BP1').mkdir(parents=True)
    (root / 'BP1' / 'PL!N-bp1-001-N.png').write_bytes(b'x')
    release_dates = {'BP01': date(2020,1,1), 'BP09': date(2099,1,1)}
    missing = missing_released_image_targets(
        cardnumbers=['PL!N-bp1-001', 'PL!N-bp1-002', 'PL!N-bp9-001'],
        image_root=root,
        release_dates=release_dates,
        as_of=date(2026,7,22),
    )
    assert missing == {'PL!N-bp1-002'}, missing
    print('OK missing released image target scan')
PY

python3 ./llocg_update_database.py --help | rg -n "full-image-refresh|image"

git diff --check -- llocg_update_database.py

python3 ./tools/build_loveca_distribution.py --target macos --output ./_codex_outputs/github_release/loveca-macos-20260721.zip
python3 ./tools/build_loveca_distribution.py --target windows --output ./_codex_outputs/github_release/loveca-windows-20260721.zip
python3 ./tools/build_loveca_distribution.py --target source --output ./_codex_outputs/github_release/loveca-source-20260721.zip
gh release upload v2026.07.21 ./_codex_outputs/github_release/loveca-macos-20260721.zip ./_codex_outputs/github_release/loveca-windows-20260721.zip ./_codex_outputs/github_release/loveca-source-20260721.zip --clobber
gh release view v2026.07.21 --json assets,url
```

※20260722内部確認: ユーザー提供ログでは `[IMAGE-FETCH-MODE] targets=0` で画像取得自体がスキップされていた。原因は `card_images` が空でない場合、既存カードの画像欠落を再取得対象に入れていなかったこと。修正後はリリース済みカードの欠落を `missing_existing` として検出し、画像取得対象へ追加する。小テストでは既存1枚・欠落1枚・未発売1枚のうち、欠落したリリース済み1枚だけを検出することを確認。GitHub Release `v2026.07.21` の本体zip3種を再上書き済み。

### 2026-07-22 next release local changes: reset buttons, match result log, UI scale 200

実装内容:

- 初回リリース版 `v2026.07.21` 固定後のローカル更新として、次版向け変更メモ `docs/notes/loveca_next_release_changes_20260722.md` を作成。
- 1デッキ用シミュレーターに通常リセットボタンを追加。
- リモート対戦用の1デッキ画面では、勝ち/負け/No Gameを `user_data/logs/loveca_match_results.jsonl` へ記録してから新しい対戦へリセットするボタンを追加。
- 2デッキ用シミュレーターでは、P1勝利/P2勝利/No Gameを同じ記録ファイルへ追記し、同じデッキ組み合わせで新しい対戦を開始するボタンを追加。
- 簡易設定の画面表示サイズを最大200%まで選択できるようにした。
- 起動時DB更新の画像不足検出ログに `[IMAGE-MISSING-EXISTING]` を追加し、最終画像取得対象ログにも `missing_existing` を出すようにした。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/web.py ./llocg_ui/server.py ./llocg_dual_v2/server.py ./llocg_update_database.py

git diff --check

head -3 ./loveca_app/web.py
head -3 ./llocg_ui/server.py
head -35 ./llocg_dual_v2/server.py
head -28 ./llocg_update_database.py
```

※20260722内部確認: `py_compile` と `git diff --check` は通過。`pytest` はローカルPython環境に `pytest` が無いため実行不可。GitHub Releaseは更新せず、次版候補としてローカル差分とメモのみ作成した。

### 2026-07-22 deck detail popup / analysis title / PR suffix image request / texticon aliases

実装内容:

- デッキ内容確認ページのカード詳細ポップアップで、効果テキストを `effect_text_raw` / `effect_text_norm` 優先で渡すよう修正。
- コストとスコアを `15.0` のような小数表記ではなく整数表記へ整形。
- 詳細ポップアップにスコア行を追加し、ライブカードのスコアも確認できるようにした。
- デッキ編集画面の詳細分析ツールタイトルを「デッキ内容確認」から「詳細分析ツール」へ修正。
- ブレードハート内訳グラフで `blade_pink` / `b_heart01` など、公式カード検索UI由来のブレードハートtexticon名を優先して参照できるようにした。
- アセットバンドル解凍許可リストへ、ブレードハート用texticon候補ファイル名を追加。
- `PL!-bp3-012-PR` のような末尾レアリティ付き画像取得指定を、`PL!-bp3-012` + 希望レアリティ `PR` として扱うようにした。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from tempfile import NamedTemporaryFile
from llocg_fetch_all_card_images import load_cardnumber_requests, remote_filename_variants
with NamedTemporaryFile('w+', encoding='utf-8', delete=False) as f:
    f.write('PL!-bp3-012-PR\n')
    name=f.name
flt, req=load_cardnumber_requests(Path(name))
assert flt == {'PL!-bp3-012'}, flt
assert req == {'PL!-bp3-012': {'PR'}}, req
files=remote_filename_variants('PR','PL!-bp3-012','PR')
assert files == ['PL!-bp3-012-PR.png'], files
print('OK rarity suffix request parsing and PR filename candidates')
PY

python3 - <<'PY'
from pathlib import Path
from loveca_app.core import AppState
app=AppState(Path('.'))
row={'count':'1','card_no':'PL!-bp3-012','rarity':'','name':'','variant_id':''}
card=app.card_display_data(row)
assert card['cost'] == '2', card
assert 'ライブ開始時' in card['effect'], card['effect']
row2={'count':'1','card_no':'PL!-bp4-022','rarity':'','name':'','variant_id':''}
card2=app.card_display_data(row2)
assert 'score' in card2
print('OK deck display data formatting', card['cost'], bool(card2.get('score')))
PY

python3 -m py_compile ./loveca_app/core.py ./loveca_app/web.py ./loveca_app/assets.py ./llocg_fetch_all_card_images.py

git diff --check -- loveca_app/core.py loveca_app/web.py loveca_app/assets.py llocg_fetch_all_card_images.py

tmpfile=$(mktemp)
printf 'PL!-bp3-012-PR\n' > "$tmpfile"
python3 ./llocg_fetch_all_card_images.py \
  --root ./llocg_db_out_full \
  --compiled ./llocg_db_out_full/cards_compiled_v7h.json \
  --cardnumber-file "$tmpfile" \
  --outdir ./llocg_db_out_full/card_images \
  --preview-outdir ./llocg_db_out_full/preview_card_images \
  --timeout 2 --sleep 0 --jitter 0 --progress-every 1 \
  --max-warn-total 10 --max-warn-per-card 10
rm -f "$tmpfile"

curl -I -L \
  -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36' \
  -H 'Referer: https://llofficial-cardgame.com/cardlist/searchresults/?expansion=PR&sort=new&view=image' \
  'https://llofficial-cardgame.com/wordpress/wp-content/images/cardlist/PR/PL!-bp3-012-PR.png'
```

※20260722内部確認訂正: 以前の「該当PR画像を確認できていない」判断は、公式画像URLへのアクセス条件確認不足による誤り。ブラウザ相当のUser-Agentと公式カードリストReferer付きで `PR/PL!-bp3-012-PR.png` がHTTP 200になることを確認。カード番号は完全一致で扱い、`PL!-PR-012` など別カード番号への読み替えは禁止。

### 2026-07-22 PR folder card image resolution and Deck Log LLC texticons

実装内容:

- `PL!-bp3-012-PR` の画像取得について、URLフォルダが `PR` であるケースを正式候補として扱う。ただしファイル名側のカード番号は完全一致を維持し、`PL!-PR-012` 型の別カード番号候補は生成しない。
- manifest生成側で公式PR一覧を全カード番号へ完全一致照合し、`PR/PL!-bp3-012-PR.png` のように「URLフォルダだけPR」の画像を補完できるようにした。
- cached image scanの対象を再録系だけでなく `PR` / `PR2` まで広げた。
- アプリ表示側で、manifest/実ファイルの完全一致により `PL!-bp3-012 + PR` から `llocg_db_out_full/card_images/PR/PL!-bp3-012-PR.png` を解決できるようにした。
- Deck Log CSSからLLC用texticon `blade_heart01.png` から `blade_heart06.png`、各ON画像、`sp_all.png`、`sp_score.png`、`sp_draw.png` と各ON画像を取得し、`llocg_db_out_full/card_images/texticons/` に配置した。
- デッキ編集画面のブレードハート検索チップと詳細分析ツールのブレードハート内訳が、追加texticonを参照できるようにした。
- UIアセットバンドル許可リストを更新し、`loveca-ui-assets-20260722.zip` を生成した。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

curl -L \
  -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36' \
  'https://llofficial-cardgame.com/cardlist/searchresults/?expansion=PR&sort=new&view=image' \
  -o /tmp/loveca_official_pr_searchresults_ua.html

python3 - <<'PY'
from pathlib import Path
import json
from llocg_fetch_all_card_images import remote_filename_variants
from llocg_db_tool_v7 import parse_official_cardlist_items

assert remote_filename_variants('PR','PL!-bp3-012','PR') == ['PL!-bp3-012-PR.png']
html=Path('/tmp/loveca_official_pr_searchresults_ua.html').read_text(encoding='utf-8')
items=parse_official_cardlist_items(html, 'PR', {'PL!-bp3-012'})
assert any(item['cardnumber']=='PL!-bp3-012' and item['rarity_norm']=='PR' and item['remote_filename']=='PL!-bp3-012-PR.png' for item in items), items
manifest=json.loads(Path('llocg_db_out_full/official_image_manifest.json').read_text(encoding='utf-8'))
entries=manifest.get('cards', {}).get('PL!-bp3-012', [])
assert any(item.get('folder')=='PR' and item.get('remote_filename')=='PL!-bp3-012-PR.png' for item in entries), entries
print('OK exact PR folder manifest parsing')
PY

python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil, zipfile
from loveca_app.core import AppState
from loveca_app.assets import ensure_ui_assets_from_local_bundle

app=AppState(Path('.'))
app.dbdir = app.path('llocg_db_out_full')
assert app.find_card_image('PL!-bp3-012', rarity='PR').name == 'PL!-bp3-012-PR.png'
for token, expected in [
    ('blade_pink','blade_heart01.png'), ('blade_red','blade_heart02.png'),
    ('blade_yellow','blade_heart03.png'), ('blade_green','blade_heart04.png'),
    ('blade_blue','blade_heart05.png'), ('blade_purple','blade_heart06.png'),
    ('blade_all','sp_all.png'), ('blade_score','sp_score.png'), ('blade_draw','sp_draw.png')]:
    path=app.resolve_texticon(token)
    assert path and path.name == expected, (token, path)
source=Path('_codex_outputs/github_release/loveca-ui-assets-20260722.zip').resolve()
with TemporaryDirectory() as td:
    root=Path(td)/'loveca'
    root.mkdir()
    shutil.copy2(source, root/source.name)
    result=ensure_ui_assets_from_local_bundle(root)
    assert not result.errors, result.errors
    assert (root/'llocg_db_out_full/card_images/texticons/blade_heart01.png').exists()
    assert (root/'llocg_db_out_full/card_images/texticons/sp_draw.png').exists()
    print('OK PR image + texticons + ui bundle extraction', len(result.installed))
with zipfile.ZipFile(source) as z:
    names=z.namelist()
    assert any(name.endswith('blade_heart01.png') for name in names)
    print('zip entries', len(names))
PY

python3 -m py_compile ./llocg_fetch_all_card_images.py ./llocg_db_tool_v7.py ./loveca_app/core.py ./loveca_app/web.py ./loveca_app/assets.py
git diff --check -- llocg_fetch_all_card_images.py llocg_db_tool_v7.py loveca_app/core.py loveca_app/web.py loveca_app/assets.py docs/notes/loveca_next_release_changes_20260722.md docs/debug/loveca_debug_commands_current_updates_20260623.md
```

※20260722内部確認訂正: `PL!-bp3-012 + PR` はローカル実画像 `PR/PL!-bp3-012-PR.png` へ解決するのが正しい。`PR/PL!-PR-012-PR.png` は別カードの画像であり参照候補に含めない。公式画像URLはブラウザ相当ヘッダー付きでHTTP 200を確認し、権限付きPython実行で `llocg_db_out_full/card_images/PR/PL!-bp3-012-PR.png` を取得済み。manifest再生成では `pr_exact_all_scan pages=15 added=43` を確認し、`official_image_manifest.json` の `cards.PL!-bp3-012` にPR entryが追加された。追加texticonは `blade_pink` などのアプリ内トークンから解決でき、生成した `loveca-ui-assets-20260722.zip` の仮展開でも31件配置、エラーなしを確認。`py_compile` と `git diff --check` は通過。

### 2026-07-22 wiki printings image candidates / deck editor sticky save header / popup wheel scroll

実装内容:

- Wikiカードページの「収録状況」テーブルから、`収録セット`、収録状況上のカード番号、末尾レアリティを抽出し、DBレコードの `printings_json` に保存するようにした。
- `image-manifest` 生成時に `printings_json` を読み、収録セット名を `product_catalog.json` / `product_release_registry.json` の商品コードへ照合して、`収録弾フォルダ + 収録状況カード番号 + レアリティ` の完全一致URL候補を追加するようにした。
- デッキ編集画面で、アプリヘッダを固定表示し、デッキ名/タグ/保存/保存して開始/キャンセルを統合した固定ヘッダへ移動した。
- デッキTSV/metadataに `&amp;` などのHTMLエンティティが混入している場合、読込・保存時に通常文字へ戻すようにした。
- 1デッキ用シミュレーターのカード選択ポップアップで、上下ホイール操作を横スクロールへ変換する共通処理を追加した。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from bs4 import BeautifulSoup
import llocg_db_tool_v7 as db
p=Path('llocg_db_out_full/_http_cache/24c5f9e05e4885c4a9bf881dc1e0a5ad.html')
soup=BeautifulSoup(p.read_text(encoding='utf-8',errors='ignore'),'lxml')
items=db.parse_printings_table(soup)
assert items and items[0]['set_title']=='ブースターパック MELLOW MOMENT'
assert items[0]['card_attr'].endswith('-P') and items[0]['rarity_norm']=='P'
print('OK parse wiki printings table')
PY

python3 - <<'PY'
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import llocg_db_tool_v7 as db
with TemporaryDirectory() as td:
    root=Path(td)
    (root/'product_catalog.json').write_text(json.dumps({'products':{'BP05':{'name':'ブースターパック Anniversary 2026','title':'ブースターパック Anniversary 2026'}}}, ensure_ascii=False), encoding='utf-8')
    data=[{'cardnumber':'PL!-bp3-012','printings_json':json.dumps([{'set_title':'ブースターパック Anniversary 2026','card_attr':'PL!-bp3-012-RM','rarity_norm':'RM'}], ensure_ascii=False)}]
    j=root/'cards.json'; j.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    items=db.load_printing_manifest_items_from_db(j, None, root, {'PL!-bp3-012'})
    assert items[0]['folder']=='BP05'
    assert items[0]['remote_filename']=='PL!-bp3-012-RM.png'
print('OK wiki printings manifest candidates')
PY

python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from loveca_app.core import AppState
import json
with TemporaryDirectory(dir='.') as td:
    root=Path(td).resolve()
    (root/'llocg_db_out_full/decklists').mkdir(parents=True)
    deck=root/'llocg_db_out_full/decklists/deck_test.tsv'
    deck.write_text('count\tcard_no\trarity\tname\tvariant_id\n1\tPL!-bp3-012\tPR\t渡辺 曜&amp;鬼塚夏美&amp;大沢瑠璃乃\t\n', encoding='utf-8')
    meta=deck.with_suffix('.meta.json')
    meta.write_text(json.dumps({'deck_name':'A&amp;B','tags':['x&amp;y']}, ensure_ascii=False), encoding='utf-8')
    app=AppState(root)
    metadata, rows=app.read_deck_rows('llocg_db_out_full/decklists/deck_test.tsv')
    assert metadata['deck_name']=='A&B'
    assert metadata['tags']==['x&y']
    assert rows[0]['name']=='渡辺 曜&鬼塚夏美&大沢瑠璃乃'
print('OK deck html entity unescape')
PY

python3 - <<'PY'
from pathlib import Path
from loveca_app.core import AppState
from loveca_app.web import Handler
class S:
    app_state=AppState(Path('.'))
handler=object.__new__(Handler)
handler.server=S()
body=handler.deck_edit_body('', True)
assert 'class="deck-editor-toolbar"' in body
assert body.count('id="visible_deck_name"') == 1
assert body.count('id="visible_deck_tags"') == 1
assert '保存して開始' in body
print('OK deck edit html sticky toolbar')
PY

python3 -m py_compile ./llocg_db_tool_v7.py ./llocg_fetch_all_card_images.py ./loveca_app/core.py ./loveca_app/web.py ./llocg_ui/server.py
git diff --check -- llocg_db_tool_v7.py loveca_app/core.py loveca_app/web.py llocg_ui/server.py
```

※20260722内部確認: 現行DBはまだ `printings_json` 生成前のため、既存 `cards_min_tokv1` からの `wiki_printings` 候補は0件。次回DB更新後に `printings_json` が入る。今回の確認ではキャッシュ済みWiki HTMLと合成DBで、収録状況テーブル解析および収録弾フォルダ候補生成が通ることを確認した。

### 2026-07-22 simulator reset buttons top-right relocation

対象:

- `llocg_ui/server.py`
- `llocg_dual_v2/server.py`

実装:

- 1デッキ用シミュレーターのリセット/勝敗記録リセットボタンを、エネルギー領域内の操作列から外し、画面右上部の独立した `RESET` パネルへ移動した。
- 通常の1デッキ用シミュレーターでは `リセット` のみ表示し、リモート対戦モードでは `勝ち記録` / `負け記録` / `No Game` を表示する。
- public view ではリセットパネルを非表示にした。
- 2デッキ用シミュレーターでは、中央操作バー内の勝敗記録ボタンを外し、画面右上部の独立した `RESET` パネルへ移動した。
- リセット/勝敗記録API本体は変更せず、配置と表示切替のみを変更した。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/server.py ./llocg_dual_v2/server.py

rg -n "resetPanel|recordButtons|reset_panel_top_right|record_reset_top_right" \
  ./llocg_ui/server.py ./llocg_dual_v2/server.py

git diff --check -- ./llocg_ui/server.py ./llocg_dual_v2/server.py \
  ./docs/debug/loveca_debug_commands_current_updates_20260623.md
```

※20260722内部確認: 構文チェックは通過。1デッキ側は `renderEnergy()` からリセット系ボタン生成を除去し、右上固定パネル側の既存 `apiCmd("reset")` / `apiCmd("record_reset")` 経由に統一した。2デッキ側は中央 `#controls` から `#recordButtons` を外し、同じIDのまま右上固定配置に変更したため、既存イベントリスナーは維持される。

### 2026-07-22 card detail clamp / under-card inspect / PL!S-bp7-005 / refresh modal gating

対象:

- `llocg_ui/server.py`
- `llocg_ui/engine.py`

実装:

- カード詳細ポップアップを、表示直後およびカード情報取得後の実サイズで画面内に再配置するようにした。手札など画面端のカードから開いても、上下左右が画面外へ見切れないように補正する。
- ステージメンバーの下にメンバーカードがある場合、カード画像下部に `下部確認` ボタンを表示するようにした。押すと下に置かれているカードを小型リストポップアップで確認でき、リスト項目クリックでカード詳細も開ける。
- `このメンバーと自分のステージにいるほかの『X』のメンバー1人を選ぶ。それらが持つ<登場>能力それぞれ1つ発動させる。` を汎用テンプレートとして追加した。PL!S-bp7-005 はこのルートで、コスト支払い後にほかのAqoursメンバーを選び、既存の登場能力処理を再利用して解決する。
- 未確認のリフレッシュ通知が残っている間は、サーバ側で進行系コマンドを止めるようにした。`NEXT` はリフレッシュ確認のACKとして扱い、裏側のエール確認や次処理へは進めない。
- クライアント側でも、リフレッシュ確認ポップアップ表示中に `NEXT` を押すとポップアップを閉じるだけにした。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/server.py ./llocg_ui/engine.py

python3 - <<'PY'
from llocg_ui.engine import _match_effect_template
text='このメンバーと自分のステージにいるほかの『Aqours』のメンバー1人を選ぶ。それらが持つ<登場>能力それぞれ1つ発動させる。'
assert _match_effect_template(text)[0]['op']=='replay_enter_ability_self_and_other_group_member'
print('OK replay enter template match')
PY

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, StageSlot, try_apply_effect_template
root=Path('.')
cards_db=load_cards_db(root, compiled_path=root/'llocg_db_out_full/cards_compiled_v7h.json', tokv1_path=root/'llocg_db_out_full/cards_min_tokv1.csv')
gs=GameState(str(root), 'smoke', 1)
gs.stage['C']=StageSlot(cardnumber='PL!S-bp7-005', active=True)
gs.stage['L']=StageSlot(cardnumber='PL!S-bp7-006', active=True)
text='このメンバーと自分のステージにいるほかの『Aqours』のメンバー1人を選ぶ。それらが持つ<登場>能力それぞれ1つ発動させる。'
ok=try_apply_effect_template(gs,random.Random(1),cards_db,text,{'source_cn':'PL!S-bp7-005','pos':'C'})
assert ok
assert gs.pending and gs.pending[0]['kind']=='choose_stage_member_for_enter_ability_replay'
assert 'L' in gs.pending[0]['candidates']
print('OK replay enter pending')
PY

python3 - <<'PY'
from types import SimpleNamespace
from llocg_ui.server import App
app=object.__new__(App)
app.gs=SimpleNamespace(refresh_notices=[{'seq':1},{'seq':3}], refresh_notice_seq=3)
app._refresh_notice_ack_seq=1
assert app._latest_unacked_refresh_notice_seq()==3
app._ack_refresh_notice(3)
assert app._latest_unacked_refresh_notice_seq()==0
print('OK refresh ack helper')
PY

git diff --check -- ./llocg_ui/server.py ./llocg_ui/engine.py
```

※20260722内部確認: 構文チェック、PL!S-bp7-005効果文のテンプレート一致、効果適用時の対象選択pending生成、リフレッシュACK helperの未確認seq判定は通過。カード詳細の画面外補正と下部確認ポップアップはDOM実装まで確認済みで、最終的な見た目はユーザー目視確認対象。

### 2026-07-22 yell double colorless heart summary UI

対象:

- `llocg_ui/server.py`
- `llocg_ui/engine.py`

実装:

- DB上のブレードハート表記 `<無色×2>` を、エール判定用の不特定ハート `any:2` として扱うようにした。
- エール内容ポップアップの公開アイコン段に `ダブル無色` を追加し、ドロー / スコアUP / ダブル無色の3枠が横幅内に収まるように枠幅と余白を調整した。
- ライブ成功確認ポップアップの所持ハート欄を `桃 赤 黄 緑 青 紫 ALL 不特定 総数` にし、総数に不特定ハートを含めるようにした。
- 必要ハート欄にも `ALL` 列を追加し、所持ハート欄と列数を揃えた。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/server.py ./llocg_ui/engine.py

python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db
from llocg_ui.engine import _parse_heart_icons, _normalize_icon_token_text
root=Path('.')
db=load_cards_db(root, compiled_path=root/'llocg_db_out_full/cards_compiled_v7h.json', tokv1_path=root/'llocg_db_out_full/cards_min_tokv1.csv')
rows=[]
for cn, ci in db.items():
    raw=str(getattr(ci,'blade_heart_raw','') or '')
    if '無色' in raw:
        counts=_parse_heart_icons(_normalize_icon_token_text(raw))
        rows.append((cn, counts))
print(rows)
assert rows and all(r[1].get('any')==2 for r in rows)
PY

python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, cheer_hearts_from_resolve, _build_live_attempt_summary_pending
root=Path('.')
db=load_cards_db(root, compiled_path=root/'llocg_db_out_full/cards_compiled_v7h.json', tokv1_path=root/'llocg_db_out_full/cards_min_tokv1.csv')
gs=GameState(str(root),'smoke',1)
gs.resolve_zone=['PL!S-bp7-022']
cheer=cheer_hearts_from_resolve(gs, db)
assert cheer.get('any') == 2
p=_build_live_attempt_summary_pending(gs, db, lives=[], live_set_indices=[], ok_all=True, base_hearts={}, yell_hearts=cheer, owned_hearts=cheer, alloc_map={}, score_rows=[], card_score_total=0, stage_score_bonus=0, yell_score_icon_bonus=0, live_total_score=0)
owned=p['live_attempt_summary']['owned_hearts']
assert owned['total'].get('any') == 2
assert owned['count_total'] == 2
print('OK double colorless owned total')
PY

python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db
from llocg_ui.server import _ci_yell_heart_counts, _ci_yell_double_colorless_icon_count
root=Path('.')
db=load_cards_db(root, compiled_path=root/'llocg_db_out_full/cards_compiled_v7h.json', tokv1_path=root/'llocg_db_out_full/cards_min_tokv1.csv')
ci=db['PL!S-bp7-022']
assert _ci_yell_heart_counts(ci).get('any') == 2
assert _ci_yell_double_colorless_icon_count(ci) == 1
print('OK double colorless popup metadata')
PY

git diff --check -- ./llocg_ui/server.py ./llocg_ui/engine.py
```

※20260722内部確認: `<無色×2>` を持つ `PL!S-bp7-022` / `PL!SP-bp7-028` はどちらも `any:2` としてパースできることを確認。`cheer_hearts_from_resolve` とライブ成功確認payloadの `owned_hearts.count_total` に不特定ハート2個が反映されること、サーバ側表示メタでダブル無色1個として取れることを確認済み。ポップアップの最終レイアウトはユーザー目視確認対象。

## 20260722 current update: success-zone storage blocked by BODY text

目的: `このカードは成功ライブカード置き場に置くことができない。` の BODY 常時文を持つライブカードが、成功ライブカード置き場選択ポップアップで選択不可になり、直接選択しても engine 側で弾かれることを確認する。

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
export LLOCG_START_HAND='PL!S-bp2-024'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_DECK_TOP='PL!N-bp1-001,PL!N-bp1-002,PL!N-bp1-003,PL!N-bp1-004,PL!N-bp1-005,PL!N-bp1-006'
export LLOCG_START_ENERGY_ACTIVE=99
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260722内部確認: compiled DB の BODY/常時文から成功置き場不可を判定する汎用 helper を追加。成功置き場選択 pending に `disabled_options` を付与し、UI では選択不可表示、engine では直接選択も `[BLOCK] success_store` として拒否する。

## 20260722 current update: YELL reveal no-blade-heart count / refresh undo order / PL!S-bp7-022 referenced condition popup

目的: エール公開ポップアップでブレードハートを持たない公開カード枚数が表示されること、リフレッシュ発生時の確認順が `リフレッシュ -> エール内容 -> ハート内訳` になり undo で逆順に戻れること、`エールで/により公開されたカードの中に〜を含む場合` 系ライブ成功時効果が参照カード確認ポップアップを通ることを確認する。

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
export LLOCG_START_HAND='PL!S-bp7-022'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_STAGE_L='PL!S-PR-013'
export LLOCG_START_STAGE_C='PL!S-PR-014'
export LLOCG_START_STAGE_R='LL-bp6-001'
export LLOCG_START_DECK_TOP='PL!S-PR-013,PL!S-PR-014,PL!S-PR-015,PL!S-PR-016,PL!S-PR-017,PL!S-PR-018,PL!N-bp1-001,PL!N-bp1-002,PL!N-bp1-003,PL!N-bp1-004'
export LLOCG_START_ENERGY_ACTIVE=99
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db
from llocg_ui.engine import new_game, try_apply_effect_template, cmd_resolve_pending
cards=load_cards_db(Path('.'))
gs,rng=new_game(Path('llocg_db_out_full'),'test',seed=1,debug=True)
gs._cards_db=cards
gs._yell_revealed_this_live=['PL!S-PR-013']
eff='エールにより公開された自分のカードの中に、<(赤)>、<(緑)>、<(青)>を持つ『Aqours』のメンバーカードがそれぞれあるなら、このカードのスコアを+1する。'
assert try_apply_effect_template(gs,rng,cards,eff,{'source_cn':'PL!S-bp7-022'})
p=gs.pending[0]
assert p['kind']=='show_revealed_cards_ack'
assert p['label']=='エール公開条件確認'
assert p['condition_status']['state']=='met'
assert p['display_cards']==['PL!S-PR-013']
cmd_resolve_pending(gs,cards,0,'ok',rng)
assert gs.pending and gs.pending[-1]['kind']=='message_ack'
print('OK PL!S-bp7-022 referenced condition popup')
PY

python3 -m py_compile ./llocg_ui/server.py ./llocg_ui/engine.py ./loveca_app/core.py ./loveca_app/web.py ./llocg_dual_v2/core.py
git diff --check -- ./llocg_ui/server.py ./llocg_ui/engine.py ./loveca_app/core.py ./loveca_app/web.py ./llocg_dual_v2/core.py
```

※20260722内部確認: `PL!S-bp7-022` と同型の「エールで/により公開されたカードの中に赤・緑・青を持つグループメンバーがそれぞれあるなら」文型は、条件達成時に参照カードリスト付き `show_revealed_cards_ack` を出し、OK後にスコア補正へ進むことを確認。エール公開ポップアップには「BHなし」枚数を公開アイコン段へ追加。リフレッシュ確認済みseqをundo履歴へ保存するようにし、リフレッシュ確認・エール確認・ハート内訳確認がundoで逆順に戻れる構造へ修正。2デッキ対戦はアプリメニュー `/dual` から起動できる導線を追加。

## 20260722 DeckLog デッキコード読込 API 修正

報告:

- Windows配布環境でデッキコード読込が失敗。
- エラー:
  - `[ERR] No cards were parsed from the source.`
  - `[WARN] Playwright not available: ModuleNotFoundError: No module named 'playwright'`

原因:

- DeckLog表示画面の現行実装は `POST /system/app/api/view/{code}` をブラウザ由来ヘッダ付きで呼ぶ。
- 既存スクリプトはAPI取得がGET中心で、DeckLog側が返すJSONの `list` / `card_number` / `num` 形式も拾えていなかった。
- そのため、Playwright未導入環境では最終フォールバックも使えず、カード0枚として失敗していた。

修正:

- `llocg_deckcode_to_decklist.py`
  - `BUILD_TAG=decklog_api_post_card_number_parse_20260722a`
  - DeckLog API取得にPOST + `Origin` / `Referer` / `X-Requested-With` / `_is_appli=2` を追加。
  - JSON parserを `list` / `card_number` / `num` 形式対応に拡張。
  - `id` 数値をカード番号として誤読しないようにし、`PL!` / `LL-` 系カード番号だけを採用。
  - `PP` / `PE+` など、DeckLog返却に含まれる追加レアリティを受け付けるように拡張。

確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_deckcode_to_decklist.py

python3 ./llocg_deckcode_to_decklist.py \
  --root /private/tmp/loveca_deck_import_smoke \
  --code 1U4B5 \
  --no-playwright \
  --timeout 20
```

結果:

- Codex通常環境ではPython外部通信がDNS制限に当たり失敗したが、外部通信許可付き実行でPlaywrightなしの読込に成功。
- `1U4B5` は20種類のカードとしてTSV出力された。
- 先頭出力例:
  - `LL-bp2-001 / R2`
  - `PL!-bp5-333 / P+`
  - `PL!SP-pb2-005 / PP`

## 20260723 PL!SP-bp1-005 山札上Liella!カード選択の種類不問化

報告:

- `PL!SP-bp1-005` の登場効果で、山札上5枚から『Liella!』のライブカードを選べない。
- 効果文は「『Liella!』のカード」指定であり、メンバーカード限定ではない。

原因:

- `topk_filtered_optional_pick` の `filter_kind` が未指定の場合、旧互換キーと同じく `MEMBER` を既定値にしていた。
- そのため、DB側で `filter_group=Liella!` のみを指定している `PL!SP-bp1-005` もメンバーカード限定として扱われていた。

修正:

- `llocg_ui/effects/topdeck.py`
  - `BUILD_TAG=topdeck_any_card_group_filter_20260723a`
  - `topk_filtered_optional_pick` は `filter_kind` 未指定なら種類不問にする。
  - 旧互換キー `enter_top5_member_optional_pick` / `body_stage_to_green_top5_member_optional` / `body_stage_to_green_top5_live_optional` のみ、従来通りメンバー/ライブ指定を補完する。

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db
from llocg_ui.engine import new_game, try_apply_effect_template
cards=load_cards_db(Path('.'))
gs,rng=new_game(Path('llocg_db_out_full'),'test',seed=1,debug=True)
gs._cards_db=cards
gs.deck=['PL!SP-bp1-020','PL!SP-bp1-006','PL!N-bp4-030','PL!SP-bp5-023','PL!-bp3-020']
eff='自分のデッキの上からカードを5枚見る。その中から『Liella!』のカードを1枚まで公開して手札に加えてもよい。残りを控え室に置く。'
assert try_apply_effect_template(gs,rng,cards,eff,{'source_cn':'PL!SP-bp1-005'})
p=gs.pending[-1]
assert 'PL!SP-bp5-023' in p.get('options', [])
assert 'メンバーカード' not in p.get('text', '')
print('OK PL!SP-bp1-005 can choose Liella! live cards')
PY

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

※20260723内部確認: 上記コマンドで、`PL!SP-bp5-023` が選択候補に含まれ、表示文言もメンバーカード限定にならないことを確認済み。

## 20260723 「カード」指定の暗黙種類フィルタ監査

確認対象:

- `topk_filtered_optional_pick`
- engine `_EFFECT_RULES` の `look_top_choose_filtered`
- 控え室からグループ指定カード回収
- エール公開カードからの手札追加 / デッキ上・下移動

確認結果:

- 静的登録 `EXTRA_EFFECT_RULES` では、効果文が「のカード」指定なのに `want_kind` / `filter_kind` を持つ登録は0件。
- engine `_EFFECT_RULES` では、「カード」指定の代表ルートは `card_kind=ANY` または `kind` 未指定から `ANY` へ落ちることを確認。
- `メンバーカード` / `ライブカード` と明記された文型のみ、`MEMBER` / `LIVE` に絞る構造であることを確認。
- 再発防止として `docs/notes/loveca_runtime_implementation_rules_20260708.md` に「カード指定はANY扱い」のルールを追記。

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db
from llocg_ui.engine import new_game, try_apply_effect_template
cards=load_cards_db(Path('.'))

def fresh():
    gs,rng=new_game(Path('llocg_db_out_full'),'test',seed=1,debug=True)
    gs._cards_db=cards
    return gs,rng

gs,rng=fresh()
gs.deck=['PL!SP-bp1-020','PL!SP-bp5-023','PL!N-bp4-030','PL!-bp3-020','PL!SP-bp1-006']
eff='自分のデッキの上からカードを5枚見る。その中から『Liella!』のカードを1枚まで公開して手札に加えてもよい。残りを控え室に置く。'
assert try_apply_effect_template(gs,rng,cards,eff,{'source_cn':'audit_topdeck_group_card'})
p=gs.pending[-1]
assert 'PL!SP-bp1-020' in p.get('options', []) and 'PL!SP-bp5-023' in p.get('options', [])

gs,rng=fresh()
gs.green_room=['PL!SP-bp1-020','PL!SP-bp5-023','PL!N-bp4-030']
eff='自分の控え室から『Liella!』のカードを1枚手札に加える。'
assert try_apply_effect_template(gs,rng,cards,eff,{'source_cn':'audit_green_group_card'})
p=gs.pending[-1]
assert 'PL!SP-bp1-020' in p.get('options', []) and 'PL!SP-bp5-023' in p.get('options', [])

for eff in [
    'エールにより公開された自分のカードの中から、カードを1枚手札に加える。',
    'エールで公開された自分のカードの中から、カードを1枚デッキの一番上に置いてもよい。',
    'エールにより公開された自分のカードの中から、カードを2枚まで手札に加える。',
    'エールで公開された自分のカードの中から、カードを2枚までデッキの一番下に置く。',
]:
    gs,rng=fresh()
    gs._yell_revealed_this_live=['PL!SP-bp1-020','PL!SP-bp5-023']
    gs.resolve_zone=['PL!SP-bp1-020','PL!SP-bp5-023']
    assert try_apply_effect_template(gs,rng,cards,eff,{'source_cn':'audit_yell_any'})
    p=gs.pending[-1]
    assert 'PL!SP-bp1-020' in p.get('options', []) and 'PL!SP-bp5-023' in p.get('options', [])
    assert p.get('card_kind', 'ANY') == 'ANY'
print('OK generic card wording keeps MEMBER and LIVE candidates')
PY
```

※20260723内部確認: 山札上・控え室・エール公開の「カード」指定代表ルートで、メンバーとライブの両方が候補に残ることを確認。同型の暗黙MEMBER/LIVE化は追加検出なし。

## 20260723 手動シミュレータ開始時マリガン不可 / 公開ウィンドウ不安定

確認結果:

- `_force_mulligan_start()` の本体が誤って undo 復元処理側へ入り込んでおり、通常起動時にマリガン開始へ戻せていなかった。
- その影響で、手動シミュレータ開始直後に turn 1 / MAIN へ進んだ状態が残り、マリガン選択ボタンが使えない状態になっていた。
- 公開ウィンドウでは、サーバ側 `APP_VERSION` と HTML 内 `CLIENT_UI_VERSION` が不一致になっており、公開画面だけ自動リロードを繰り返す可能性があった。
- 公開用 state 生成自体は軽量で、手札・山札は中身を伏せ、枚数だけ返す状態を維持している。

修正:

- `_force_mulligan_start()` にマリガン復帰処理を戻し、undo 側に入り込んだ誤配置を解消。
- HTML 内の公開ウィンドウ用クライアントバージョンを `APP_VERSION` から自動注入する形へ変更。
- 公開ウィンドウの自動更新間隔を 250ms から 500ms へ変更し、公開窓を開いた状態の負荷を軽減。

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/server.py ./llocg_ui/engine.py ./llocg_ui/effects/*.py

python3 - <<'PY'
from llocg_ui.server import APP_VERSION, HTML
print('APP_VERSION', APP_VERSION)
print('version_in_html', APP_VERSION in HTML)
print('placeholder_left', '__LOVECA_APP_VERSION__' in HTML)
assert APP_VERSION in HTML
assert '__LOVECA_APP_VERSION__' not in HTML
PY

python3 - <<'PY'
import os
from pathlib import Path
from llocg_ui.server import App
from llocg_ui.views import make_view_state
hand='PL!SP-bp1-020,PL!SP-bp1-006,PL!N-bp4-030,PL!SP-bp5-023,PL!-bp3-020,PL!S-bp2-024'
deck=','.join(['PL!SP-bp1-020','PL!SP-bp1-006','PL!N-bp4-030','PL!SP-bp5-023','PL!-bp3-020','PL!S-bp2-024']*9)
old=os.environ.copy()
os.environ.update({
 'LLOCG_START_HAND': hand,
 'LLOCG_START_HAND_SIZE':'0',
 'LLOCG_START_DECK_EXACT': deck,
 'LLOCG_START_DECK_EXACT_STRICT':'1',
 'LLOCG_START_SHUFFLE':'0',
 'LLOCG_APP_NORMAL_MATCH_SETUP':'1',
 'LLOCG_APP_MULLIGAN_REQUIRED':'1',
})
for k in ['LLOCG_START_PHASE','LLOCG_START_TURN','LLOCG_DEBUG_PRESET']:
 os.environ.pop(k,None)
try:
 app=App(Path('.'), code='test', deck_code='llocg_db_out_full/decklists/deck_24a4efd236092325fdd1.tsv', seed=1, debug=False)
 st=app.state_json()
 pub=make_view_state(st, 'public')
 assert st.get('phase') == 'MULLIGAN'
 assert len(st.get('hand',[])) == 6
 assert pub.get('hand_count') == 6 and pub.get('deck_count') == 54
 assert pub.get('hand') == [] and pub.get('deck') == []
 app._cmd_mulligan_next([0,1])
 st2=app.state_json()
 assert st2.get('phase') == 'MAIN'
 assert len(st2.get('hand',[])) == 7
 print('OK mulligan start and public redaction')
finally:
 os.environ.clear(); os.environ.update(old)
PY
```

HTTP確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

env LLOCG_START_HAND=PL!SP-bp1-020,PL!SP-bp1-006,PL!N-bp4-030,PL!SP-bp5-023,PL!-bp3-020,PL!S-bp2-024 \
  LLOCG_START_HAND_SIZE=0 \
  LLOCG_START_SHUFFLE=0 \
  LLOCG_APP_NORMAL_MATCH_SETUP=1 \
  LLOCG_APP_MULLIGAN_REQUIRED=1 \
  python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8899

curl -i http://127.0.0.1:8899/public
curl -i 'http://127.0.0.1:8899/state?view=public'
curl -i http://127.0.0.1:8899/state
```

※20260723内部確認: `/public`、`/state?view=public`、`/state` が HTTP 200 で応答することを確認。公開 state は hand/deck の中身を返さず、`hand_count` / `deck_count` を返す。

## 20260723 メニュー起動速度 / 起動進捗 / public top-k reveal / remote nickname

確認結果:

- メニューの「デッキを選んで起動」遷移が重い主因は、デッキ構成チェックでカード種類だけを見る場面でも `searchable_card()` を呼び、画像バリアント/レアリティメタ構築まで初回実行していたこと。
- `AppState` に相対rootを渡した場合、絶対パスとの比較でデッキ検証が不正扱いになる不安定要因があった。
- リモート対戦の公開URL検出では、アプリが予約したポートが分かっているのに広めのポート探索へ進む余地があり、公開ウィンドウ起動待ちが長くなる要因になっていた。
- `公開して手札に加える` top-k 効果は、メイン画面の候補全体が公開情報になるべきだが、public view では `choose_from_topk` が非公開top-k扱いで伏せられていた。

修正:

- `deck_composition()` をカードDBの種別フィールド直接参照へ変更し、画像バリアント構築を起動前検証から外した。
- `AppState.root` を常に絶対パス化。
- アプリ起動後にカードDBインデックスをバックグラウンドで温める処理を追加。
- 手動/リモート/2デッキ起動状態に `progress_percent` / `stage` を追加し、メニュー右下の進捗バーへ表示。
- リモート時は予約済みポートから public URL を先に組み立て、検出処理も予約ポート中心にした。
- リモート対戦の入力表示を「ニックネーム（アルファベット）」に変更し、次回以降の既定値として保存。
- `公開して手札` の `choose_from_topk` pending に `public_reveal_pool` を付与し、public view では候補全体を公開カードとして表示。

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/core.py ./loveca_app/web.py ./llocg_ui/server.py ./llocg_ui/views.py ./llocg_ui/effects/topdeck.py ./llocg_ui/engine.py ./llocg_ui/effects/*.py

python3 - <<'PY'
from loveca_app.core import AppState
from pathlib import Path
import time
app=AppState(Path('.'))
for i in range(3):
    t=time.perf_counter()
    ds=app.list_decks()
    print(i, round(time.perf_counter()-t,4), len(ds), sum(1 for d in ds if d.get('valid')))
PY
```

確認結果: 初回 `list_decks()` は約0.014秒、2回目以降は約0.003秒。修正前に観測した約2.8秒の初回待ちを解消。

公開top-k確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db
from llocg_ui.engine import new_game, try_apply_effect_template
from llocg_ui.views import make_view_state
cards=load_cards_db(Path('.'))
gs,rng=new_game(Path('llocg_db_out_full'),'test',seed=1,debug=True)
gs._cards_db=cards
gs.deck=['PL!SP-bp1-020','PL!SP-bp5-023','PL!N-bp4-030','PL!-bp3-020','PL!SP-bp1-006']
eff='自分のデッキの上からカードを5枚見る。その中から『Liella!』のカードを1枚まで公開して手札に加えてもよい。残りを控え室に置く。'
assert try_apply_effect_template(gs,rng,cards,eff,{'source_cn':'PL!SP-bp1-005','effect_text':eff})
p=gs.pending[-1]
assert p.get('public_reveal_pool') is True
state={'phase':gs.phase,'turn':gs.turn,'deck':gs.deck,'hand':gs.hand,'green_room':gs.green_room,'set_zone':gs.set_zone,'resolve_zone':gs.resolve_zone,'success_zone':getattr(gs,'success_zone',[]),'stage':{},'stage_detail':{},'pending':gs.pending,'cn2name':{'PL!SP-bp1-020':'鬼塚夏美','PL!SP-bp5-023':'Shooting Voice!!','PL!N-bp4-030':'Daydream Mermaid','PL!-bp3-020':'Snow halation','PL!SP-bp1-006':'桜小路きな子'},'cn2label':{},'cn2type':{},'cn2is_live':{},'cn2yell_hearts':{},'cn2yell_draw_icons':{},'cn2yell_score_icons':{},'cn2image_rarity':{},'cn2image_variant_id':{},'cn2group':{},'cn2unit':{},'cn2cost':{},'cn2score':{},'card_instances':{},'card_instance_meta':{},'public_reveal_events':[]}
pub=make_view_state(state,'public')
assert pub['pending'][0].get('display_cards') == p.get('display_cards')
assert set(pub['cn2name']) >= set(p.get('display_cards'))
print('OK real topk route public pool')
PY
```

実起動確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from loveca_app.core import AppState
from pathlib import Path
import time
app=AppState(Path('.'))
deck=next(d for d in app.list_decks() if d.get('valid'))['path']
ok,msg=app.start_manual(deck)
print('start', ok, msg)
try:
    for i in range(30):
        st=app.manual_window_status()
        print('status', i, st.get('status'), st.get('progress_percent'), st.get('stage'), st.get('private_url'), st.get('public_url'), st.get('message'))
        if st.get('status') in ('ready','failed','timeout','stopped'):
            break
        time.sleep(0.3)
finally:
    print(app.stop_manual())
PY
```

確認結果: 通常起動は `starting 28 起動準備` から次回確認で `ready 100 起動完了` へ遷移。

リモート起動確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from loveca_app.core import AppState
from pathlib import Path
import time
app=AppState(Path('.'))
deck=next(d for d in app.list_decks() if d.get('valid'))['path']
rec=app.create_remote_session('CodexTest',4,'BCDE')
ok,msg=app.start_manual(deck, remote_session=rec)
print('start', ok, msg)
try:
    for i in range(30):
        st=app.manual_window_status()
        print('status', i, st.get('status'), st.get('progress_percent'), st.get('stage'), st.get('private_url'), st.get('public_url'), st.get('message'))
        if st.get('status') in ('ready','failed','timeout','stopped'):
            break
        time.sleep(0.3)
finally:
    print(app.stop_manual())
PY
```

確認結果: リモート起動は初回statusから `public_url=http://127.0.0.1:<port>/public` と `progress_percent=55` が入り、次回確認で `ready 100 起動完了` へ遷移。テストで生成した `user_data/remote_sessions/20260723-CodexTest-BCDE.json` は削除済み。

## 20260723 パブリックウィンドウ動作負荷軽減

原因整理:

- パブリックウィンドウは別サーバではなく、既にメイン画面と同じ `run_llocg_ui_web.py` / `ThreadingHTTPServer` の `/public` で配信されている。
- ただしメイン画面とパブリック画面がそれぞれ `/state` を取得すると、巨大な state 構築、カード名/画像/効果表示用 map 構築、public view 用 redaction が毎回走るため、2画面起動時に重複計算が発生していた。

修正:

- `llocg_ui/server.py` に短時間の view-state cache を追加。GET `/state` と `/public_state` は同じゲーム状態の短時間内で base state と serialized view state を共有する。
- `save_trace()` 実行時に cache revision を進めて破棄するため、コマンド実行後の状態更新は stale にならない。
- パブリック画面の定期 polling を `500ms` から `1200ms` へ緩和。メイン画面の操作時は `localStorage` の `llocg_public_refresh_ping` で即時更新されるため、操作追従性を保ちつつアイドル時負荷を下げる。

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from llocg_ui.server import App
app=App(Path('llocg_db_out_full'),'ui','1RCBL',seed=1,debug=False)
a=app.view_state_bytes('private')
b=app.view_state_bytes('public')
c=app.view_state_bytes('public')
assert a and b and c
assert b == c
print('OK view cache bytes', len(a), len(b))
PY
```

## 20260723 PL!-bp5-011 ハート選択肢復元 / リセットseed再シャッフル

原因整理:

- `PL!-bp5-011` は DB本文では `<緑>か<青>か<紫>` を選ぶ効果だが、compiled では先頭の `緑` が ability `conditions` に裸の色名として分離され、clause 側は `か<青>か<紫>...` になっていた。
- runtime 側に過去の `桃/黄/紫` 固定処理が残っており、似た効果を同一選択肢として扱う危険があった。
- アプリ起動デッキは初期手札/山札を環境変数で固定して渡すため、内部リセット時に新seedを作っても同じ `LLOCG_START_HAND` / `LLOCG_START_DECK_EXACT` が再適用され、同じ手札から始まっていた。

修正:

- ハート選択肢抽出を共通化し、`conditions` 側に分離された裸の色名 + clause 側の `<色>` を復元するよう修正。
- `live_start_success_heart_by_success` の解決を6色対応に修正。
- 横断確認として、「選んだハート」系の候補色を全件確認。`PL!-bp5-011` 以外にもカードごとに色組み合わせが異なることを確認し、固定色リストを使わないルールを `docs/notes/loveca_runtime_implementation_rules_20260708.md` に追記。
- 通常アプリ起動デッキの内部リセット時は、`LLOCG_APP_DECK_VARIANTS_JSON` から60枚の個体リストを再構築し、新seedで手札6枚/山札54枚を再シャッフルするよう修正。
- リモート勝敗記録ボタンは、記録後に `1: 同じデッキでもう一度対戦` / `2: デッキ変更` / `3: シミュレータ終了` を選ぶ流れへ変更。

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db, _get_card
from llocg_ui.engine import new_game, try_apply_effect_template, cmd_resolve_pending, StageSlot
cards=load_cards_db(Path('llocg_db_out_full'))
ci=_get_card(cards,'PL!-bp5-011')
gs,rng=new_game(Path('llocg_db_out_full'),'test',seed=1,debug=True)
gs.stage['C']=StageSlot('PL!-bp5-011')
gs.success_zone=['PL!-bp5-030','PL!-bp5-031']
ab=next(ab for ab in ci.abilities if 'ライブ開始時' in str(ab.get('trigger')))
cl=(ab.get('clauses') or [])[0]
eff=str(cl.get('effect_template') or cl.get('raw') or '')
assert try_apply_effect_template(gs,rng,cards,eff,{'source_cn':'PL!-bp5-011','pos':'C','condition_text':str(ab.get('conditions') or '')})
assert gs.pending[-1]['options'] == ['緑','青','紫']
cmd_resolve_pending(gs,cards,0,'緑',rng)
assert getattr(gs,'success_zone_heart_color','') == 'green'
print('OK PL!-bp5-011 choices/restored green')
PY
```

## 20260723 シミュレータ手動デバッグモード / stats 表示修正 / パッチzip

修正:

- ステージの「下部確認」ボタンをカード画像内からカード画像外の下部へ移動し、起動ボタンと重ならないようにした。
- 画面左上のターン表示列に「デバッグモード」ボタンを追加。ON の間は手札・山札・控え室・ステージ・成功ライブ置き場のカードを選んで任意領域へ移動できる。
- デバッグモード中は山札 / 控え室 / 成功ライブ置き場のポップアップを管理リスト表示に切り替え、山札と控え室は上下ボタンで順番を入れ替えられる。
- デバッグ移動は通常の効果処理 / post-process を走らせず、操作前の undo snapshot だけを残す。
- stats 表示は「基礎ブレード + 基礎ハート + 効果で増えたブレード + 効果で増えたハート」に修正。エールアイコン由来のハートを参照していた誤りを修正し、カード上の略記 `ST` を `stats` に変更した。
- 配布ビルドに `--target patch` を追加。最新の本体 zip とは別に、更新ファイルだけを含む上書き用パッチ zip を作成できるようにした。

内部確認予定:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/server.py ./tools/build_loveca_distribution.py

python3 ./tools/build_loveca_distribution.py --target patch --output ./_codex_outputs/github_release/loveca-patch-20260723.zip
```

## 20260723 登場能力再発動キュー / エール参照カード確認 / 起動・診断・画像欠落補強

修正:

- `このメンバーとほかの『グループ』メンバーが持つ<登場>能力をそれぞれ発動` 系の効果は、複数の登場能力をその場で連続処理せず、既存の `auto_order` に接続して1つずつ解決するよう修正。
- エール公開内容を参照するライブ成功時効果のうち、赤・緑・青など「各条件をそれぞれ満たす」文型は、条件ごとに実際に参照したカードだけを表示する `show_referenced_cards_ack` に変更。エール公開サマリーポップアップへ混線しないよう修正。
- エール公開カード確認ポップアップ内の横長カード列を、マウスホイールの上下操作でも横送りできるよう修正。
- 2デッキシミュレータの起動を即時 ready 扱いにせず、`/dual` が応答するまで起動確認するよう修正。起動失敗時は最後のログを表示する。
- 2デッキシミュレータのリセット記録ボタン `NG` 表記を `No Game` に変更。
- データ更新で、preview manifest に載っているが `preview_card_images` に実ファイルがないカードを画像取得対象へ追加。取得後も欠落している場合は成功扱いにしない。
- 診断・バージョンページは15秒キャッシュを追加し、初回表示で重い画像バリエーション照合を走らせないよう修正。

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./loveca_app/core.py ./llocg_dual_v2/server.py ./llocg_update_database.py ./llocg_fetch_all_card_images.py

git diff --check

python3 ./run_llocg_dual_v2.py --help

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, StageSlot, cmd_resolve_pending, try_apply_effect_template
cards=load_cards_db(Path('llocg_db_out_full'))
gs=GameState(root='.', code='smoke', seed=1, debug=True)
gs.stage['C']=StageSlot('PL!S-bp7-005')
gs.stage['L']=StageSlot('PL!S-bp7-006')
gs.pending.append({'kind':'choose_stage_member_for_enter_ability_replay','source_cn':'PL!S-bp7-005','source_pos':'C','candidates':['L'],'options':['L']})
cmd_resolve_pending(gs, cards, 0, 'L', random.Random(1))
assert gs.pending[0]['kind'] == 'auto_order'
assert len(gs.pending[0]['queue']) == 2

gs2=GameState(root='.', code='smoke', seed=2, debug=True)
gs2._yell_revealed_this_live=['PL!S-bp7-002','PL!S-bp7-003','PL!S-bp7-004','PL!S-bp7-005']
text='エールにより公開された自分のカードの中に、<(赤)>、<(緑)>、<(青)>を持つ『Aqours』のメンバーカードがそれぞれあるなら、このカードのスコアを+1する。'
try_apply_effect_template(gs2, random.Random(2), cards, text, {'source_cn':'PL!S-bp7-022'})
p=gs2.pending[0]
assert p['kind'] == 'show_referenced_cards_ack'
assert [s['cards'][0] for s in p['reference_sections']] == ['PL!S-bp7-004','PL!S-bp7-002','PL!S-bp7-003']
print('OK enter replay queue and referenced-card ack')
PY

python3 - <<'PY'
from pathlib import Path
from loveca_app.core import AppState
app=AppState(Path('.').resolve())
a=app.diagnostics()
b=app.diagnostics()
assert a.get('diagnostics_elapsed_ms', 9999) < 500
assert b.get('diagnostics_cached') is True
print('OK diagnostics fast/cache', a.get('diagnostics_elapsed_ms'), b.get('image_count'))
PY
```

## 20260727 効果監査ZIP確認 / エール置換・デッキ上下操作・条件付き選択効果修正

確認元:

- `/Users/tekitou/Downloads/loveca_effect_debug_commands_20260724.zip`
- `/Users/tekitou/Downloads/loveca_effect_behavior_audit_firstpass_20260724.zip`
- 作業用に `/private/tmp/loveca_effect_audit_20260724` へ一時展開。リポジトリ内のファイル移動・削除・バックアップ作成はなし。

修正:

- `PL!S-bp7-022` の `自分のエールはデッキ下から行う` BODY常時を、カード番号固定ではなく効果文検出で実装。通常エールと追加エールの両方がデッキ下から公開される。
- `PL!SP-bp7-028` の `エール公開カードがすべて『Liella!』ならスコア+1` を汎用文型として追加。公開0枚は条件未達。
- `PL!SP-bp7-028` のライブ開始時効果を、控え室の指定グループメンバーを指定枚数選んでシャッフルしデッキ下へ戻し、ステージ全員へブレード付与する汎用 route に追加。
- `PL!N-bp7-006` の `上から4枚見る。その後、好きな順番で上に置く` を既存 top reorder route に接続。
- `PL!N-bp7-006` の `山札上3枚を控え室に置く` コスト後、そのカード内容を参照して2択を出す route を追加。条件未達時に後続選択肢が独立実行されないよう修正。
- 同一カードに複数の起動効果がある場合の使用回数キーを、能力文ベースで分離。使用済み能力は飛ばして次の起動効果を確認するよう修正。
- `PL!S-bp7-004` のライブ開始時 `デッキ下から3枚見る` をデッキ下用 reorder route に追加。
- `PL!S-bp7-004` の登場時 `Aqoursからバトンタッチ時、手札を最大3枚残して残りをデッキ下、3ドロー` を既存バトンタッチ条件 route へ接続。自分側を処理し、相手側は手動処理メッセージを出す。
- 既存の再エール系 `PL!S-bp2-004` / `PL!S-bp3-020` / `PL!HS-bp6-027` / `PL!S-bp6-021` は現行コード上の汎用 YELL auto route に乗っていることを内部確認。
- `PL!N-bp4-002` / `PL!S-pb1-008` は選択プレイヤーのデッキ上確認 route にマッチ済みであることを内部確認。

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/engine.py

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, StageSlot, cmd_yell, _perform_additional_yell
cards=load_cards_db(Path('llocg_db_out_full'))
gs=GameState(root='.', code='audit', seed=1, phase='LIVE_PERF')
gs.stage['C']=StageSlot('PL!S-bp2-010')
gs.set_zone=['PL!S-bp7-022']
gs.deck=['PL!-PR-003','PL!-PR-004','PL!-PR-012','PL!-PR-014','PL!-PR-015','PL!S-PR-026','PL!S-PR-027','PL!S-PR-025']
cmd_yell(gs, random.Random(1), cards)
assert gs.resolve_zone[:3] == ['PL!S-PR-025','PL!S-PR-027','PL!S-PR-026']
gs2=GameState(root='.', code='audit', seed=2, phase='LIVE_PERF')
gs2.stage['C']=StageSlot('PL!S-bp2-010')
gs2.set_zone=['PL!S-bp7-022']
gs2.deck=['TOP','MID','BOT2','BOT1']
assert _perform_additional_yell(gs2, random.Random(2), cards, 2, reason='audit') == ['BOT1','BOT2']
print('OK PL!S-bp7-022 bottom-source YELL')
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, try_apply_effect_template
cards=load_cards_db(Path('llocg_db_out_full'))
eff=cards['PL!SP-bp7-028'].abilities[1]['clauses'][0]['effect_template']
gs=GameState(root='.', code='audit', seed=1)
gs._yell_revealed_this_live=['PL!SP-bp7-002','PL!SP-bp5-001']
try_apply_effect_template(gs, random.Random(1), cards, eff, {'source_cn':'PL!SP-bp7-028'})
assert 'score +1' in gs.log[-1]
gs2=GameState(root='.', code='audit', seed=1)
gs2._yell_revealed_this_live=['PL!SP-bp7-002','PL!S-bp7-002']
try_apply_effect_template(gs2, random.Random(1), cards, eff, {'source_cn':'PL!SP-bp7-028'})
assert 'not satisfied' in gs2.log[-1]
print('OK PL!SP-bp7-028 all revealed group score')
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, StageSlot, cmd_activate_to_green, cmd_resolve_pending, _ability_key
cards=load_cards_db(Path('llocg_db_out_full'))
ci=cards['PL!N-bp7-006']
gs=GameState(root='.', code='audit', seed=1, phase='MAIN')
gs.stage['C']=StageSlot('PL!N-bp7-006')
gs.used_this_turn[_ability_key(ci, ci.abilities[0], 'C')]=1
gs.deck=['LL-bp1-001','PL!S-bp7-002','PL!S-bp7-003','PL!N-bp7-011']
gs.energy_wait=2
cmd_activate_to_green(gs, cards, 'C', random.Random(1))
assert gs.pending and gs.pending[0]['kind'] == 'choose_effects'
cmd_resolve_pending(gs, cards, 0, 'ライブ終了時まで、<(ブレード)><(ブレード)>を得る。', random.Random(1))
assert gs.stage['C'].temp_blade == 2
print('OK PL!N-bp7-006 second activated choice')
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, try_apply_effect_template, cmd_resolve_pending
cards=load_cards_db(Path('llocg_db_out_full'))
eff=cards['PL!S-bp7-004'].abilities[0]['clauses'][0]['effect_template']
gs=GameState(root='.', code='audit', seed=1)
gs.hand=['PL!S-bp7-002','PL!S-bp7-003','PL!S-bp7-004','PL!S-bp6-001']
gs.deck=['PL!S-bp6-002','PL!S-bp6-003','PL!S-bp6-004','PL!S-bp6-005']
try_apply_effect_template(gs, random.Random(1), cards, eff, {'source_cn':'PL!S-bp7-004','baton_old_cns':['PL!S-bp7-002']})
assert gs.pending and gs.pending[0]['kind'] == 'choose_hand_keep_for_baton_bottom_draw'
cmd_resolve_pending(gs, cards, 0, 'PL!S-bp7-002', random.Random(1))
cmd_resolve_pending(gs, cards, 0, 'Done', random.Random(1))
assert gs.pending and gs.pending[0]['kind'] == 'message_ack'
print('OK PL!S-bp7-004 baton hand cleanup')
PY
```

## 20260727 デッキ構築 ラブカポイント表示・検証

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_loveca_app.py
```

確認観点:
- デッキ管理一覧に「ラブカPt」列が表示される。
- デッキ内容確認ページにラブカポイント合計と対象カード内訳が表示される。
- デッキ編集画面で `PL!N-bp1-003` の `R＋/P/P＋/SEC` など対象カードを追加すると、現在のデッキ欄のラブカPtが即時更新される。
- 合計が9ptを超えたデッキは保存前に確認が出る。保存は可能だが、一覧・手動シミュレータ起動欄では構成不正扱いとなり起動できない。
- 詳細分析ツールにラブカポイントの合計と対象カード内訳が表示される。

## 20260728 デッキ構築 レギュレーション指定保存

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_loveca_app.py
```

確認観点:
- デッキ編集画面の固定ヘッダでレギュレーションを選択できる。
- 既存デッキは未指定でも「通常60枚（ラブカPt 2026/4/3適用）」として扱われる。
- 「ハーフ30枚」を選ぶと、現在のデッキ欄がメンバー24 / ライブ6 / 合計30基準に切り替わる。
- 「通常60枚（ラブカPtなし）」を選ぶと、ラブカポイントが `0 / 制限なし` 相当で表示され、ポイント超過扱いにならない。
- 「通常60枚（ラブカPt 2026/8/8予定）」を選ぶと、`LL-bp2-001` が5pt、`PL!SP-bp2-024` が0pt扱いになる。
- 保存後のデッキ内容確認・デッキ一覧・手動シミュレータ起動欄に、保存したレギュレーション名とその基準での検証結果が表示される。

## 20260729 オートプレイ Stage 1 方針レポート

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from loveca_app.core import AppState

app = AppState(Path('.'))
decks = app.list_decks()
valid_decks = [deck for deck in decks if deck.get('valid')]
if not valid_decks:
    print('OK autoplay report skipped: no valid deck')
else:
    report = app.autoplay_deck_report(valid_decks[0]['path'])
    assert report['model_stage'] == 'stage1_policy_template'
    assert report['curve']['totals']['cards'] > 0
    assert report['progressions']
    assert report['recommended_progression']
    print('OK autoplay report', report['deck_name'], report['recommended_progression']['label'])
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_loveca_app.py
```

確認観点:
- メニューに「オートプレイ」が表示される。
- オートプレイ画面にデッキ一覧が表示され、構成検証済みデッキから方針レポートを開ける。
- 方針レポートに推奨コスト進行、メンバーコスト分布、ライブスコア分布、進行候補、Stage 2目標プリセットが表示される。
- 現段階では自動操作を開始せず、Stage 1の方針確認画面として動作する。

## 20260729 プレビュー探索・ラブカPt超過試行・オートプレイ拡張

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile \
  ./llocg_update_database.py \
  ./llocg_build_preview_manifest_from_x.py \
  ./loveca_app/autoplay.py \
  ./loveca_app/core.py \
  ./loveca_app/web.py \
  ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from loveca_app.core import AppState

app = AppState(Path('.'))
decks = app.list_decks()
playable_decks = [deck for deck in decks if deck.get('playable', deck.get('valid'))]
if not playable_decks:
    print('OK autoplay expanded report skipped: no playable deck')
else:
    report = app.autoplay_deck_report(playable_decks[0]['path'])
    assert report['curve']['member_cost_bands']
    assert 'special_signals' in report['curve']
    assert any(item.get('phase') in {'late', 'late_special'} for item in report['progressions'])
    markdown = app.autoplay_markdown_report(playable_decks[0]['path'])
    assert '## Cost Bands' in markdown
    print('OK autoplay expanded report', report['deck_name'], report['recommended_progression']['label'])
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --all --outdir docs/reports/autoplay
```

確認観点:
- `llocg_update_database.py` のプレビュー公式ポスト集約ページキャッシュが15分基準になる。
- 公式ポスト集約ページにあるがローカルDBへ未反映のプレビューカードは `[PREVIEW-INDEX-MISSING-DB]` に表示される。
- ラブカポイント超過のみのデッキは、警告表示のまま手動シミュレータ、リモート、2デッキ、オートプレイの対象に残る。
- 枚数不正、カード番号不明、同名枚数超過などのデッキとして成立しない不正は引き続き起動不可。
- オートプレイ方針レポートに、5-10コスト帯、15コスト以上、コスト軽減、特殊バトンタッチの検出結果が表示される。
- `docs/reports/autoplay/` にモデルデッキ比較用のMarkdownレポートを出力できる。

## 20260729 デッキコード読込 デフォルトデッキ名

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_deckcode_to_decklist.py ./loveca_app/core.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from llocg_deckcode_to_decklist import extract_deck_name_from_html
from loveca_app.core import AppState

html = Path('llocg_db_out_full/decklists/7QEC8.html').read_text(encoding='utf-8', errors='replace')
assert extract_deck_name_from_html(html, code='7QEC8') == '三神'
assert extract_deck_name_from_html('デッキ名「7QEC8」のデッキ', code='7QEC8') == ''
assert AppState._imported_deck_name_from_metadata({'deck_name':'7QEC8'}, '7QEC8') == ''
assert AppState._imported_deck_name_from_metadata({'deck_name':'三神'}, '7QEC8') == '三神'
print('OK deck import name extraction')
PY
```

確認観点:
- DeckLogのHTMLに `デッキ名「...」のデッキ` が含まれる場合、保存画面のデッキ名初期値にその名前が入る。
- APIでカード一覧だけ先に取れた場合も、デッキ名取得用にHTMLを補助取得する。
- デッキ名取得に失敗し、メタデータ上の `deck_name` がデッキコードそのものになっている場合は、コードをデフォルト名として表示しない。

## 20260729 パラレルレアリティのラブカPt / オートプレイ試行

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile \
  ./loveca_app/autoplay.py \
  ./loveca_app/core.py \
  ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from loveca_app.core import AppState

app = AppState(Path('.'))
for row in [
    {'count':'1','card_no':'PL!SP-bp2-024','rarity':'SRL','name':'ビタミンSUMMER！','variant_id':''},
    {'count':'1','card_no':'PL!SP-bp2-024-SRL','rarity':'','name':'ビタミンSUMMER！','variant_id':''},
]:
    pts = app.deck_loveca_points([row], 'standard_20260403')
    assert pts['total'] == 1, pts
print('OK loveca SRL points')
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --recent 3 --trials 500 --seed 29 --turns 4 --outdir docs/reports/autoplay
```

確認観点:
- `PL!SP-bp2-024` の202604レギュレーション対象レアリティに `SRL` が含まれ、`PL!SP-bp2-024-SRL` のようにカード番号末尾へレアリティが付いたデッキ行でもラブカPtが計算される。
- カード番号末尾のレアリティを分離する場合も、カード正本の番号照合は基礎カード番号で行う。
- 直近更新デッキ3件について、構築評価、目標ターン形、500回試行の完全一致率、上位進行、サンプル進行を `docs/reports/autoplay/` に出力できる。

## 20260729 オートプレイ試行 マリガン/上振れ/エネルギーブースト補正

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --recent 3 --trials 500 --seed 29 --turns 4 --outdir docs/reports/autoplay
```

確認観点:
- 試行レポートにマリガン方針、成功判定、効果近似の前提が表示される。
- `2-10-2` 目標に対して `2-11-2` などの上振れ盤面を達成扱いにする。
- 7コスト矢澤にこなど、コスト2以下メンバーを追加登場させる効果をコスト進行判定に含める。
- `君のこころは輝いてるかい？` などのライブ成功時ドロー効果を、手札改善として近似する。
- Daydream Mermaid などのエネルギーブーストライブを、5軸ミラステの `2-4-2 -> 2-11-2` 進行に含める。
- 東條希のように「バトンタッチして登場した場合」という受け身条件だけを持つカードを、特殊バトンタッチ札として誤検出しない。

## 20260729 オートプレイ試行 主目標/代替目標分離

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --recent 3 --trials 500 --seed 29 --turns 4 --outdir docs/reports/autoplay
```

確認観点:
- 君ここ系は主目標を `2-2 / 7-2 / 13-2` とし、`7-2-2` / `13-2-2` は `accepted targets` の上振れ代替に表示される。
- 5軸ミラステはT2の `accepted targets` に `2-5-2 or 2-4-2` が表示される。
- Daydream Mermaid系のエネルギーブーストは、そのターンにライブセットした場合だけ代替プランとして扱う。
- 10軸ミラステはT3の `accepted targets` に `2-10-2 or 2-11-2 or 2-13-2` が表示されていた。
  ※20260803内部確認: ユーザー確認により、この10軸ではT3に13コストを出さないため `2-13-2` は不適切。`autoplay_live_success_coarse_and_target_split_20260803a` で `2-13-2` をaccepted targetから除外し、現行確認では `2-10-2 / 2-11-2` のみ。
- 各ターンのライブセット1ドローが、メンバー計画前の手札循環として試行に含まれる。

## 20260729 オートプレイ試行 実デッキ内カード基準の目標生成

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --recent 3 --trials 500 --seed 29 --turns 4 --outdir docs/reports/autoplay
```

確認観点:
- 進行候補一覧と試行目標に、デッキ内に存在しないメンバーコストが出ない。
- 君ここレポートでT4目標が存在しない22コストではなく、実在する `LL-bp2-001` の20コスト目標になる。
- `Target Cards And Routes` に各ターンの目標カード名、カード番号、到達経路が表示される。
- `Decision Policy` にマリガンから1ターン目終了までの判断基準が表示される。

## 20260729 オートプレイ試行 マリガン/ライブセット/配置優先順位再補正

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --recent 3 --trials 500 --seed 29 --turns 4 --outdir docs/reports/autoplay
```

確認観点:
- マリガンがT1〜T3の達成率を基準にし、採用枚数の少ないT3目標カードを残しやすくする。
- 過剰な2コストは、引き直し期待が高いカードとして戻しやすくする。
- ライブセットを最大3枚の手札交換として扱い、非ライブカードも交換対象にする。
- Daydream Mermaid系のエネルギーブーストカードは、必要ターン以外で無条件にセットしない。
- 配置はターン目標予算内で、目標より大きいカード、目標ぴったり、最大妥協札の順に選ぶ。
- 君ここ系のT4主目標が `13-7-2`、NS三神系上振れ代替が `13-20-2` として表示される。

## 20260729 オートプレイ試行 ステージ継続モデル

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --recent 3 --trials 500 --seed 29 --turns 4 --outdir docs/reports/autoplay
```

確認観点:
- 各ターンの試行でステージ3枠が維持され、毎ターン手札からゼロベースで盤面を作り直さない。
- 既存ステージのうち目標形に近いカードは残し、空き枠または遠い枠だけを更新する。
- ターン目標で登場可能と見る最大コストを超えるメンバーを、そのターンに新規登場させない。
- T1 `2-2` 目標で13/20コストを置くような不自然なルートが出ない。
- ステージ継続により、以前の過大評価された試行結果が再計算される。

## 20260729 オートプレイ試行 低コスト妥協札の置換と複数T1目標

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --recent 3 --trials 500 --seed 29 --turns 4 --outdir docs/reports/autoplay
```

確認観点:
- T2の4/5コストなど、後続高コスト目標に対する低コスト妥協札を固定し続けない。
- T3に10/11/13コストを引いた場合、既存の低コスト妥協札を置き換え候補にする。
- 10軸ではT1 `2-2` だけでなく、T2 `2-4-2` に接続する `4` もT1代替目標として扱う。
- `Miss Reasons` に、君ここT2の `missing 7`、5軸T3の `missing 11`、10軸T3の `missing 10` などが出る。
- 10軸/5軸のT3到達率が、妥協札固定バグで極端に低くならない。

## 20260729 オートプレイ試行 累積達成率とライブスコア目標

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --recent 3 --trials 500 --seed 29 --turns 4 --outdir docs/reports/autoplay
```

確認観点:
- `Turn Summary` に `hit_rate` と `cumulative` の説明が表示される。
- 君ここ系のT4主目標が `13-7-2`、上振れ代替が `13-20-2` として表示され、進行の主評価は `cumulative` で確認できる。
- 5軸のT4受け入れ目標が `15-5-2 or 15-4-2 or 15-2-2` になっている。
- `Live Score Targets` に各ターンの目標スコア、受け入れスコア、該当ライブカード例、達成率が表示される。
- ライブスコア達成率は、効果処理用ライブではなくライブセット交換で選ばれたライブカードの最大スコアを基準に集計される。

## 20260729 オートプレイ試行 目標計画の一元化回帰

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from loveca_app.core import AppState

app = AppState(Path('.'))
paths = [
    'llocg_db_out_full/decklists/deck_2d69085d8135c787adcc.tsv',
    'llocg_db_out_full/decklists/deck_1d64365fb7bf71ac7081.tsv',
    'llocg_db_out_full/decklists/deck_fcc369ef393b3ed66e43.tsv',
]
for path in paths:
    result = app.autoplay_trial_report(path, trials=120, seed=29, max_turns=4)
    assert len(result['stage_goal_plans']) == 4
    assert result['target_turns'] == [plan['primary_shape'] for plan in result['stage_goal_plans']]
    assert result['target_alternatives'] == [plan['accepted_shapes'] for plan in result['stage_goal_plans']]
    for key in ('cumulative_hit_rates', 'live_score_cumulative_hit_rates', 'combined_cumulative_hit_rates'):
        for prev, cur in zip(result[key], result[key][1:]):
            assert cur <= prev + 1e-9, (key, result[key])
print('OK autoplay goal-plan invariants')
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --recent 3 --trials 500 --seed 29 --turns 4 --outdir docs/reports/autoplay
```

確認観点:
- `target_turns` は `stage_goal_plans[*].primary_shape` から生成され、表示専用の別補正を持たない。
- `target_alternatives` は `stage_goal_plans[*].accepted_shapes` から生成され、判定用の別補正を持たない。
- 盤面、ライブスコア、盤面+ライブスコアの累積率はターンが進んでも増加しない。
- 5軸T4は主目標 `15-5-2`、受け入れ目標 `15-5-2 or 15-4-2 or 15-2-2` として表示される。
- 君ここT4単独値が高くても、累積値と `combined_cumulative` で進行全体の達成度を確認できる。

## 20260729 CPU対戦準備 オートプレイ再試行と2デッキHTML変換回帰

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --all --trials 800 --seed 31 --turns 4 --outdir docs/reports/autoplay_cpu_prep_20260729
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_app/web.py ./loveca_autoplay_report.py ./run_llocg_dual_v2.py ./llocg_dual_v2/core.py ./llocg_dual_v2/server.py
```

確認観点:
- 全試行可能デッキのオートプレイレポートを `docs/reports/autoplay_cpu_prep_20260729/` に出力できる。
- CPU対戦準備の総括レポート `docs/reports/autoplay_cpu_prep_20260729_summary.md` を更新できる。
- 2デッキ埋め込みHTML生成は、1デッキ側のpublic polling間隔が変わっても失敗しない。
- 2デッキのルールコア/legacy adapterテストが全通過する。

## 20260729 CPU対戦準備 Step A action suggestion adapter

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_app/web.py ./loveca_autoplay_report.py ./llocg_dual_v2/server.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from loveca_app.core import AppState

app = AppState(Path('.'))
deck = 'llocg_db_out_full/decklists/deck_1d64365fb7bf71ac7081.tsv'
states = {
    'mulligan': {'phase':'MULLIGAN','turn':1,'hand':['PL!N-bp1-026','PL!N-bp3-030','PL!N-bp5-027','PL!N-bp1-001','PL!N-bp1-002','PL!N-bp1-003']},
    'live': {'phase':'LIVE_SET','turn':2,'hand':['PL!N-bp1-026','PL!N-bp3-030','PL!N-bp5-027','PL!N-bp1-001','PL!N-bp1-002','PL!N-bp1-003']},
    'main': {'phase':'MAIN','turn':2,'hand':['PL!N-bp1-001','PL!N-bp1-002','PL!N-bp1-003','PL!N-bp4-001'], 'stage': {'L': None, 'C': None, 'R': None}},
    'pending': {'phase':'MAIN','turn':1,'hand':[], 'pending':[{'kind':'confirm','choices':['ok']}]},
}
for label, state in states.items():
    out = app.autoplay_action_suggestion(deck, state)
    assert out.get('command'), out
    assert out.get('kind'), out
    print(label, out['kind'], out['command'], out.get('payload'))
PY
```

確認観点:
- `suggest_autoplay_action()` がマリガン、ライブセット、メイン登場、pending既定選択の候補を返す。
- CPU候補は `command` と `payload` を持ち、後続の2デッキUIからそのまま中央/プレイヤー操作へ変換できる。
- まだ完全自動対戦ではなく、1手分の提案を返す段階である。

## 20260730 CPU対戦準備 Step C 2デッキCPU 1手ボタン/API

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_dual_v2/server.py ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_app/web.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_llocg_dual_v2.py --deck1 W42B --deck2 W42B --host 127.0.0.1 --port 8898
```

別ターミナル:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

curl -sS http://127.0.0.1:8898/cpu_suggest
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

curl -sS -X POST http://127.0.0.1:8898/cpu_action -H 'Content-Type: application/json' --data '{"max_turns":4}'
```

確認観点:
- `/cpu_suggest` が現在手番プレイヤーの `suggestion` を返す。
- `/cpu_action` が返された候補を同じ中央/プレイヤー操作経路で1手実行する。
- `W42B` のようなDB内デッキコードでもCPU判断用のデッキTSVを読める。
- 中央UIに `CPU 1手` ボタンが表示され、対戦終了時や成功ライブ選択待ち中は無効化される。

## 20260730 CPU対戦準備 片側/両側CPU自動トグル

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_dual_v2/server.py ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_app/web.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from llocg_dual_v2.server import _shell_html
manual = _shell_html(cpu_ui=False)
cpu = _shell_html(cpu_ui=True, cpu_auto_default=True)
for needle in ['id="cpuP1"', 'id="cpuP2"', 'id="cpuAuto"']:
    assert needle not in manual, needle
    assert needle in cpu, needle
for needle in ['function scheduleCpuAuto', 'function toggleCpuAuto', 'CPU_UI=true', 'CPU_AUTO_DEFAULT=true']:
    assert needle in cpu, needle
assert 'CPU_UI=false' in manual
print('OK split manual/cpu shell hooks')
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_llocg_dual_v2.py --deck1 W42B --deck2 W42B --host 127.0.0.1 --port 8898
```

別ターミナルで順に確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

curl -sS -X POST http://127.0.0.1:8898/cpu_action -H 'Content-Type: application/json' --data '{"max_turns":4}'
```

確認観点:
- 通常起動の中央UIには `P1 CPU` / `P2 CPU` / `自動` トグルが表示されない。
- `--cpu-ui --cpu-auto-default` 起動時のみ中央UIに `P1 CPU` / `P2 CPU` / `自動` トグルが表示される。
- CPU設定は `localStorage` に保存される。
- `自動` on時、現在手番がCPU指定プレイヤーなら `/cpu_action` を1手ずつ呼び直す。
- 成功ライブカード選択待ちなど、人間入力が必要な中央ポップアップ中は自動操作が止まる。
- API確認では、P1マリガン、P2マリガン、P1メイン登場操作まで通る。

## 20260730 2デッキ入口分離

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_dual_v2/server.py ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_app/web.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from types import SimpleNamespace
from loveca_app.core import AppState
from loveca_app.web import Handler
from llocg_dual_v2.server import _shell_html
app = AppState(Path('/Users/tekitou/Desktop/gsim/loveca'))
h = object.__new__(Handler)
h.server = SimpleNamespace(app_state=app)
home = h.home_body()
manual = h.dual_body(False)
cpu = h.dual_body(True)
manual_shell = _shell_html(cpu_ui=False)
cpu_shell = _shell_html(cpu_ui=True, cpu_auto_default=True)
checks = {
    'home manual card': '手動2デッキ対戦' in home,
    'home cpu card': 'CPUオート2デッキ' in home,
  'home autoplay card': 'オートプレイ' in home,
    'manual start mode': "mode:'manual'" in manual,
    'cpu start mode': "mode:'cpu'" in cpu,
    'manual shell hides cpu': 'id="cpuP1"' not in manual_shell and 'CPU_UI=false' in manual_shell,
    'cpu shell shows cpu': 'id="cpuP1"' in cpu_shell and 'CPU_UI=true' in cpu_shell,
}
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL'), name)
if not all(checks.values()):
    raise SystemExit(1)
PY
```

確認観点:
- メニューに `手動2デッキ対戦` / `CPUオート2デッキ` / `オートプレイ` が別枠で表示される。
- `/dual` は完全手動の既存2デッキシミュレータ入口として動作する。
- `/dual-cpu` は片側CPU/両側CPU選択可能な2デッキシミュレータ入口として動作する。
- UIなし大量試行は `/autoplay` 側のレポート/CLI運用と分離して扱う。

## 20260730 CPU対戦 判断ログパネル

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_dual_v2/server.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from llocg_dual_v2.server import _shell_html
manual = _shell_html(cpu_ui=False)
cpu = _shell_html(cpu_ui=True, cpu_auto_default=True)
checks = {
    'manual no trace': 'id="cpuTrace"' not in manual,
    'manual no cpu controls': 'id="cpuP1"' not in manual,
    'cpu trace panel': 'id="cpuTrace"' in cpu and 'CPU判断ログ' in cpu,
    'cpu trace functions': 'function pushCpuTrace' in cpu and 'function renderCpuTrace' in cpu,
    'cpu controls': 'id="cpuP1"' in cpu and 'CPU_UI=true' in cpu,
}
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL'), name)
if not all(checks.values()):
    raise SystemExit(1)
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./run_llocg_dual_v2.py --deck1 W42B --deck2 W42B --host 127.0.0.1 --port 8898 --cpu-ui --cpu-auto-default
```

別ターミナル:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

curl -sS -X POST http://127.0.0.1:8898/cpu_action -H 'Content-Type: application/json' --data '{"max_turns":4}'
```

確認観点:
- CPU UI起動時のみ左下に `CPU判断ログ` パネルが表示される。
- `CPU 1手` または自動進行で、手番、ターン、フェイズ、操作種別、信頼度、理由、対象カードがログへ蓄積される。
- `クリア` ボタンで表示中のCPU判断ログだけを消せる。
- 手動2デッキ起動ではCPU判断ログパネルが表示されない。

## 20260730 UIなしオートプレイ 大量試行サマリ出力

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_autoplay_report.py ./loveca_app/autoplay.py ./loveca_app/core.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 1 --trials 5 --turns 4 --no-markdown --summary-csv sim_out/autoplay_summary_smoke.csv --summary-json sim_out/autoplay_summary_smoke.json
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
import csv, json
from pathlib import Path
csv_path = Path('sim_out/autoplay_summary_smoke.csv')
json_path = Path('sim_out/autoplay_summary_smoke.json')
rows = list(csv.DictReader(csv_path.open(encoding='utf-8')))
data = json.loads(json_path.read_text(encoding='utf-8'))
assert rows
assert data
for key in ['deck_path', 'deck_name', 'trials', 't1_target', 't4_cumulative', 't4_top_miss']:
    assert key in rows[0], key
print('OK autoplay summary smoke', rows[0].get('deck_name'), rows[0].get('trials'))
PY
```

確認観点:
- `--no-markdown` 指定時は、デッキごとのMarkdownを作らずCSV/JSONサマリだけを出力できる。
- サマリにはデッキ名、試行回数、各ターン目標、達成率、ライブ達成率、複合達成率、平均ステージコスト、主な未達理由が入る。
- 大量試行時は `--all --trials N --no-markdown --summary-csv ... --summary-json ...` で横比較用データを作れる。

## 20260730 CPU pending 既定選択ポリシー

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./llocg_dual_v2/server.py ./loveca_app/core.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from loveca_app.autoplay import suggest_autoplay_action

def lookup(cn):
    return {'cardnumber': cn, 'card_no': cn, 'name': cn, 'card_type_norm': 'メンバー', 'cost': 2, 'score': None, 'effect_text': ''}

rows = [{'count': '1', 'card_no': 'A-001'}]
base = {'turn': 1, 'phase': 'MAIN', 'hand': [], 'stage': []}
cases = [
    ({'kind': 'confirm', 'options': ['ok']}, 'ok', 'high'),
    ({'kind': 'choose_player_for_green_bottom', 'message': '相手を選ぶ', 'options': ['self', 'opponent']}, 'opponent', 'medium'),
    ({'kind': 'dual_opponent_top1_to_green_or_keep', 'options': ['green', 'keep']}, 'green', 'medium'),
    ({'kind': 'dual_opponent_topk_reorder_keep_any', 'options': ['B-010', 'B-011'], 'display_cards': ['B-010', 'B-011']}, 'B-010,B-011', 'medium'),
    ({'kind': 'optional_effect', 'options': ['apply', 'skip']}, 'apply', 'medium'),
]
for pending, expected_choice, expected_conf in cases:
    state = dict(base)
    state['pending'] = [pending]
    got = suggest_autoplay_action(rows, lookup, state)
    assert got['payload']['choice'] == expected_choice, got
    assert got['confidence'] == expected_conf, got
print('OK pending choice policy smoke')
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m unittest llocg_dual_v2.tests.test_rule_core llocg_dual_v2.tests.test_legacy_adapter_transactions
```

確認観点:
- 単一選択肢pendingは high confidence でその選択肢を返す。
- 相手領域に関わる `self/opponent` pending は `opponent` を選ぶ。
- `green/keep` は、効果実行側の `green` を選ぶ。
- 山札上複数枚確認で任意枚数保持するpendingは、未知評価では全カードを元順で保持し、不要な控え室送りを避ける。
- `apply/skip` は、CPU既定では `apply` を選び、判断ログに理由と信頼度を残す。

## 20260730 CPU MAIN 目標超過優先

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./llocg_dual_v2/server.py ./loveca_app/core.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from loveca_app.autoplay import _cpu_main_action

records = {
    'M-002': {'cardnumber': 'M-002', 'name': 'base two', 'card_type_norm': 'MEMBER', 'cost': '2'},
    'M-007': {'cardnumber': 'M-007', 'name': 'exact seven', 'card_type_norm': 'MEMBER', 'cost': '7'},
    'M-013': {'cardnumber': 'M-013', 'name': 'over thirteen', 'card_type_norm': 'MEMBER', 'cost': '13'},
}

def lookup(card_no):
    return records[card_no]

state = {'phase': 'MAIN', 'hand': ['M-007', 'M-013'], 'stage': ['M-002', None, None]}
plan = {'accepted_shapes': [[7, 2]], 'primary_shape': [7, 2]}
action = _cpu_main_action(state, lookup, plan)
assert action and action['card']['card_no'] == 'M-007', action

plan_with_upside = {'accepted_shapes': [[13, 2], [7, 2]], 'primary_shape': [13, 2]}
action_with_upside = _cpu_main_action(state, lookup, plan_with_upside)
assert action_with_upside and action_with_upside['card']['card_no'] == 'M-013', action_with_upside
print('OK playable-shape member priority', action, action_with_upside)
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 1 --trials 5 --turns 4 --no-markdown --summary-csv sim_out/autoplay_summary_smoke.csv --summary-json sim_out/autoplay_summary_smoke.json
```

確認観点:
- CPUのMAIN配置とUIなしオートプレイ試行の両方で、候補生成と達成判定を分離する。
- 20260731後続修正により、この検証は accepted playable shape 上限ではなく、実アクティブエネルギー制約へ置き換えた。
- active energy が足りない場合は高コストカードを置かず、active energy が足りる場合は目標超過を優先する。
- CPU判断ログの理由に、active energy と pay cost が残る。

※20260731内部確認:
- T1平均ステージコストが不自然に高くなる原因は、達成判定用の「目標以上ならOK」と配置候補生成が同じstage scoreだけを使っていたこと。
- 暫定的な accepted playable shape 上限は、Daydream Mermaidなどのエネルギー増加を扱えないため、実エネルギー制約に置き換えた。
- `_cpu_main_action` では state の `energy_active` とバトンタッチ軽減後の支払いコストを使って候補を制限する。
- UIなし試行の `_improve_persistent_stage` では `active/wait/energy_deck_remaining` を持ち、通常登場で active -> wait、ターン開始時に wait -> active、エネルギーフェイズで energy deck -> active、ライブ成功時エネルギー増加で energy deck -> wait を処理する。

## 20260730 CPU LIVE_SET ライブ目標ログ

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from loveca_app.autoplay import suggest_autoplay_action

records = {
    'L-001': {'cardnumber': 'L-001', 'name': 'score one', 'card_type_norm': 'LIVE', 'score': '1', 'effect_text': ''},
    'L-005': {'cardnumber': 'L-005', 'name': 'score five', 'card_type_norm': 'LIVE', 'score': '5', 'effect_text': ''},
    'M-002': {'cardnumber': 'M-002', 'name': 'two', 'card_type_norm': 'MEMBER', 'cost': '2', 'effect_text': ''},
}

def lookup(card_no):
    return records[card_no]

rows = [
    {'count': '1', 'card_no': 'L-001'},
    {'count': '1', 'card_no': 'L-005'},
    {'count': '1', 'card_no': 'M-002'},
]
state = {'turn': 1, 'phase': 'LIVE_SET_FIRST', 'hand': ['L-005', 'M-002'], 'stage': []}
action = suggest_autoplay_action(rows, lookup, state)
assert action['kind'] == 'live_set', action
assert action['confidence'] == 'high', action
assert 'live target' in action['reason'], action
assert 'L-005' in action['reason'], action
assert any(card['card_no'] == 'L-005' for card in action['selected_cards']), action
print('OK live-set score target trace', action)
PY
```

確認観点:
- ライブスコア目標を満たすライブカードを選んだ場合、CPU判断ログの信頼度が `high` になる。
- 判断理由にターンのライブ目標点と、実際に選んだライブカード番号・スコアが残る。
- 目標以上のライブスコアは達成候補として扱う。

## 20260730 CPU MAIN 終了判断ログ

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from loveca_app.autoplay import _cpu_main_completion_action, suggest_autoplay_action

records = {
    'M-002': {'cardnumber': 'M-002', 'name': 'two', 'card_type_norm': 'MEMBER', 'cost': '2'},
    'M-007': {'cardnumber': 'M-007', 'name': 'seven', 'card_type_norm': 'MEMBER', 'cost': '7'},
    'M-013': {'cardnumber': 'M-013', 'name': 'thirteen', 'card_type_norm': 'MEMBER', 'cost': '13'},
}

def lookup(card_no):
    return records[card_no]

plan = {'accepted_shapes': [[2, 2]], 'primary_shape': [2, 2]}
complete = _cpu_main_completion_action({'hand': [], 'stage': ['M-002', 'M-002']}, lookup, plan)
assert complete['kind'] == 'main_complete' and complete['confidence'] == 'high', complete

miss = _cpu_main_completion_action({'hand': [], 'stage': ['M-002']}, lookup, plan)
assert miss['kind'] == 'main_pass' and miss['confidence'] == 'low', miss

rows = [
    {'count': '4', 'card_no': 'M-002'},
    {'count': '4', 'card_no': 'M-007'},
    {'count': '4', 'card_no': 'M-013'},
]
play = suggest_autoplay_action(rows, lookup, {'turn': 2, 'phase': 'MAIN_FIRST', 'hand': ['M-013'], 'stage': ['M-002']})
assert play['kind'] == 'main_play' and play['card']['card_no'] == 'M-013', play
print('OK main completion trace', complete, miss, play)
PY
```

確認観点:
- MAINで追加登場候補がなく、盤面がaccepted targetを満たしている場合は `main_complete` / high confidence でNextする。
- MAINで追加登場候補がなく、盤面が未達の場合は `main_pass` / low confidence として、未達理由を判断ログに残す。
- 同一MAINフェイズ中にまだ改善候補がある場合は、従来通り `main_play` を返し、CPU自動が次の1手として継続できる。

## 20260731 オートプレイ精度比較サマリ

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_autoplay_report.py ./loveca_app/autoplay.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 3 --trials 200 --seed 29 --turns 4 \
  --no-markdown \
  --summary-csv docs/reports/autoplay/autoplay_baseline_20260731a.csv \
  --summary-json docs/reports/autoplay/autoplay_baseline_20260731a.json
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 3 --trials 200 --seed 29 --turns 4 \
  --no-markdown \
  --summary-csv docs/reports/autoplay/autoplay_current_20260731a.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260731a.json \
  --compare-json docs/reports/autoplay/autoplay_baseline_20260731a.json \
  --compare-csv docs/reports/autoplay/autoplay_compare_20260731a.csv \
  --compare-md docs/reports/autoplay/autoplay_compare_20260731a.md
```

確認観点:
- `--compare-json` に前回サマリを指定すると、今回サマリとの差分CSV/Markdownが生成される。
- 同一条件・同一コードで比較した場合、全metric deltaが0になる。
- 精度改善時は `tN_combined_cumulative_delta`、`tN_cumulative_delta`、`tN_live_cumulative_delta`、`tN_avg_stage_cost_delta`、`tN_top_miss_before/after` を報告する。

## 20260731 オートプレイ配置候補の実プレイ制約

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from loveca_app.autoplay import _cpu_main_action

records = {
    'M-002': {'cardnumber': 'M-002', 'name': 'base two', 'card_type_norm': 'MEMBER', 'cost': '2'},
    'M-007': {'cardnumber': 'M-007', 'name': 'exact seven', 'card_type_norm': 'MEMBER', 'cost': '7'},
    'M-013': {'cardnumber': 'M-013', 'name': 'over thirteen', 'card_type_norm': 'MEMBER', 'cost': '13'},
}

def lookup(card_no):
    return records[card_no]

low_energy = {'phase': 'MAIN', 'energy_active': 7, 'hand': ['M-007', 'M-013'], 'stage': ['M-002', None, None]}
restricted = _cpu_main_action(low_energy, lookup, {'accepted_shapes': [[13, 2], [7, 2]], 'primary_shape': [13, 2]})
assert restricted and restricted['card']['card_no'] == 'M-007', restricted

high_energy = {'phase': 'MAIN', 'energy_active': 13, 'hand': ['M-007', 'M-013'], 'stage': ['M-002', None, None]}
with_energy = _cpu_main_action(high_energy, lookup, {'accepted_shapes': [[13, 2], [7, 2]], 'primary_shape': [13, 2]})
assert with_energy and with_energy['card']['card_no'] == 'M-013', with_energy
print('OK energy-gated member priority', restricted, with_energy)
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 3 --trials 200 --seed 29 --turns 4 \
  --no-markdown \
  --summary-csv docs/reports/autoplay/autoplay_current_20260731c.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260731c.json \
  --compare-json docs/reports/autoplay/autoplay_baseline_20260731a.json \
  --compare-csv docs/reports/autoplay/autoplay_compare_20260731c_vs_baseline.csv \
  --compare-md docs/reports/autoplay/autoplay_compare_20260731c_vs_baseline.md
```

確認結果:
- 根本原因: 達成判定用の「目標以上ならOK」と、手札から出す配置候補生成が同じstage scoreだけを使っていた。そのためT1から13/20コストなどが置ける扱いになり、平均ステージコストと達成率が過大に出ていた。
- 修正: `_cpu_main_action` と `_improve_persistent_stage` の両方で、実アクティブエネルギーとバトンタッチ軽減後の支払いコストを配置候補の制約にした。
- 修正: `_stage_score` のステージ枚数加点を accepted target slot count までに制限し、目標枚数を超える空き枠埋めを抑制した。
- 比較: 初期基準比でT1平均ステージコストは、君ここ `29.79 -> 3.96`、5軸 `28.74 -> 6.04`、10軸 `27.96 -> 6.76` に低下。T1から高コストを置く過大評価が解消した。
- 比較: cumulativeは君ここT3 `0.965 -> 0.64`、5軸T3 `0.98 -> 0.76`、10軸T3 `0.975 -> 0.83` に低下。これは不正な早期高コスト配置が達成扱いから外れたためで、精度上は自然化。
- 残観点: 5軸/10軸のT3以降を上げるには、次にライブセット交換・マリガン・エネルギーブースト成功後の手札補充/配置経路を改善する。

## 20260731 オートプレイ実エネルギー制約への置換

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from loveca_app.autoplay import _cpu_main_action
records = {
    'M-002': {'cardnumber': 'M-002', 'name': 'base two', 'card_type_norm': 'MEMBER', 'cost': '2'},
    'M-007': {'cardnumber': 'M-007', 'name': 'exact seven', 'card_type_norm': 'MEMBER', 'cost': '7'},
    'M-013': {'cardnumber': 'M-013', 'name': 'over thirteen', 'card_type_norm': 'MEMBER', 'cost': '13'},
}
def lookup(card_no): return records[card_no]
low_energy = {'phase': 'MAIN', 'energy_active': 7, 'hand': ['M-007', 'M-013'], 'stage': ['M-002', None, None]}
restricted = _cpu_main_action(low_energy, lookup, {'accepted_shapes': [[13, 2], [7, 2]], 'primary_shape': [13, 2]})
assert restricted and restricted['card']['card_no'] == 'M-007', restricted
high_energy = {'phase': 'MAIN', 'energy_active': 13, 'hand': ['M-007', 'M-013'], 'stage': ['M-002', None, None]}
with_energy = _cpu_main_action(high_energy, lookup, {'accepted_shapes': [[13, 2], [7, 2]], 'primary_shape': [13, 2]})
assert with_energy and with_energy['card']['card_no'] == 'M-013', with_energy
print('OK energy-gated member priority')
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 3 --trials 200 --seed 29 --turns 4 \
  --no-markdown \
  --summary-csv docs/reports/autoplay/autoplay_current_20260731e.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260731e.json \
  --compare-json docs/reports/autoplay/autoplay_current_20260731c.json \
  --compare-csv docs/reports/autoplay/autoplay_compare_20260731e_vs_c.csv \
  --compare-md docs/reports/autoplay/autoplay_compare_20260731e_vs_c.md
```

確認結果:
- 暫定の accepted playable shape 上限は、Daydream Mermaid等のエネルギー増加を表現できないため廃止した。
- UIなし試行は `active/wait/energy_deck_remaining` を持ち、開始3エネルギー、各ターンのアクティブ/エネルギー/ドロー、通常登場の active -> wait、ライブ成功時エネルギー増加の energy deck -> wait を処理する。
- CPU MAIN候補は state の `energy_active` とバトンタッチ軽減後の支払いコストで判定する。同じ `13-2` 目標でも active 7 なら7コスト、active 13なら13コストを選ぶ。
- 比較: T1通常ドローを入れた影響で live cumulative は君ここT1 `0.34 -> 0.40`、5軸T1 `0.17 -> 0.325`、10軸T1 `0.095 -> 0.215` と改善。
- 比較: 実エネルギー制約により平均ステージコストは自然化した一方、T3 cumulative は3デッキとも `0.0`。次の根本課題は、T3用の希少高コスト札をマリガン/ライブセット交換/配置で温存・探索する未来ターン評価。
- 残観点: T2までの盤面達成だけを最大化すると、T3到達札を十分に守れない。次は future target protection とライブセット交換の優先順位を改善する。

## 20260731 オートプレイ future target protection 第一段

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from loveca_app.autoplay import _improve_persistent_stage, _stage_costs_with_virtual_low_summons
stage=[{'kind':'member','cost':7,'low_cost_summon_n':1},{'kind':'member','cost':2},None]
hand=[{'kind':'member','cost':13,'card_no':'M13'}]
energy={'active':10,'wait':9,'deck_remaining':6}
_improve_persistent_stage(stage, hand, [[13,2],[13,2,2]], energy)
assert 13 in _stage_costs_with_virtual_low_summons(stage), (stage, hand, energy)
print('OK baton future replacement', _stage_costs_with_virtual_low_summons(stage), hand, energy)
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 3 --trials 200 --seed 29 --turns 4 \
  --no-markdown \
  --summary-csv docs/reports/autoplay/autoplay_current_20260731f.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260731f.json \
  --compare-json docs/reports/autoplay/autoplay_current_20260731e.json \
  --compare-csv docs/reports/autoplay/autoplay_compare_20260731f_vs_e.csv \
  --compare-md docs/reports/autoplay/autoplay_compare_20260731f_vs_e.md
```

確認結果:
- 根本原因: `13-2` を目指すターンで、前ターンの7コストが2コスト目標の上振れとして固定され、13コストへのバトンタッチ候補から外れていた。
- 修正: `_stage_slots_to_replace` は空き枠と全占有枠を候補に出し、実際に置くかはstage scoreと実エネルギーで判定する。
- 修正: 直近accepted targetを仮想低コスト召喚込みで満たした場合、そのターン内の追加配置を止める。
- 比較: T3 cumulative は、君ここ `0.0 -> 0.695`、5軸 `0.0 -> 0.455`、10軸 `0.0 -> 0.10` に改善。
- 比較: T4 cumulative は、君ここ `0.0 -> 0.485`、5軸 `0.0 -> 0.25`、10軸 `0.0 -> 0.075` に改善。
- 残観点: 10軸はまだT3が低い。10コスト3枚などの希少札をマリガン/ライブセット交換でより強く守る評価が必要。
- 将来接続: 控え室からカードを手札に加える効果も、直近不足を優先し、不足がない場合は未来ターン希少札を拾う同じ評価関数へ接続する。

## 20260731 オートプレイ turn-aware future need

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 3 --trials 200 --seed 29 --turns 4 \
  --no-markdown \
  --summary-csv docs/reports/autoplay/autoplay_current_20260731h.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260731h.json \
  --compare-json docs/reports/autoplay/autoplay_current_20260731g.json \
  --compare-csv docs/reports/autoplay/autoplay_compare_20260731h_vs_g.csv \
  --compare-md docs/reports/autoplay/autoplay_compare_20260731h_vs_g.md
```

確認結果:
- 根本原因: マリガン/ライブセット交換の必要度評価がターンごとの目標候補を平坦化しており、10軸のT3希少札保護と、余剰低コスト交換の切り替えが弱かった。
- 修正: `_card_need_score_by_turn` を追加し、ターン構造、採用枚数の少なさ、T3/T4希少札を評価できるようにした。
- 修正: マリガン、CPUライブセット提案、UIなし試行ライブセット交換を同じturn-aware評価へ接続した。
- 修正: 2/4コストなど採用枚数が多いカードは、手札+ステージで直近必要数を超えている場合だけ交換候補へ戻す。
- 比較: 君ここT3 cumulative `0.75 -> 0.90`、T4 cumulative `0.625 -> 0.795`。
- 比較: 5軸T3 cumulative `0.455 -> 0.52`、T4 cumulative `0.295 -> 0.425`。
- 比較: 10軸T3 cumulative `0.10 -> 0.455`、T4 cumulative `0.095 -> 0.37`。
- 残観点: 10軸T3の未達はまだ `missing 10` が最大。次はライブセット交換後のドロー、ライブ成功時ドロー、控え室回収候補の評価を同じneed scoreへ接続して、10/11/13到達札の探索量を増やす。

## 20260731 オートプレイ progression support signals

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from loveca_app.core import AppState
from loveca_app.autoplay import build_autoplay_policy_context, _card_need_score_by_turn
app=AppState(Path('.'))
for deck in app.list_decks():
    name = deck.get('name') or ''
    if '10' in name or '5' in name or '君ここ' in name:
        meta, rows = app.read_deck_rows(deck['path'])
        ctx = build_autoplay_policy_context(rows, app.card_record, max_turns=4)
        print('DECK', name)
        for c in ctx['deck_cards']:
            tags = c.get('progression_support_tags') or []
            if tags or c.get('card_no') == 'PL!N-bp4-030':
                sc = _card_need_score_by_turn(c, ctx['target_alternatives'][:3], ctx['deck_cards'])
                print(' ', c.get('card_no'), c.get('name'), c.get('kind'), c.get('cost') or c.get('score'), tags, 'score=', round(sc, 2))
        report = app.autoplay_deck_report(deck['path'])
        print(' signals=', {k: len(v) for k,v in report['curve']['special_signals'].items() if v})
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 3 --trials 200 --seed 29 --turns 4 \
  --no-markdown \
  --summary-csv docs/reports/autoplay/autoplay_current_20260731i.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260731i.json \
  --compare-json docs/reports/autoplay/autoplay_current_20260731h.json \
  --compare-csv docs/reports/autoplay/autoplay_compare_20260731i_vs_h.csv \
  --compare-md docs/reports/autoplay/autoplay_compare_20260731i_vs_h.md
```

確認結果:
- Daydream Mermaid は `energy_boost` として検出され、5軸/10軸系の序盤必要度評価で need score `30.0`。
- 10軸青紫では `energy_activate` として近江彼方、三船栞子を検出。
- 君ここでは `cost_reduction`、`overcost_member_play`、`low_cost_summon` を検出。
- 同一seed 200試行の比較では、前回から cumulative/live/combined の数値差分は全て `0.0`。前回時点でエネルギー追加ライブの交換保護は効いていたため、今回は達成率改善ではなく、進行サポート札の汎用検出・スコアリング・レポート表示の追加。
- 残観点: この `progression_support_tags` を控え室回収、山札検索、ライブ成功時ドロー後の選択へ接続し、直近不足札と未来ターンの希少進行札を同じ評価で探せるようにする。

## 20260803 オートプレイ Decision Trace

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 3 --trials 50 --seed 29 --turns 4 --trace-trials 3 \
  --outdir docs/reports/autoplay/decision_trace_20260803a \
  --summary-csv docs/reports/autoplay/autoplay_trace_20260803a.csv \
  --summary-json docs/reports/autoplay/autoplay_trace_20260803a.json
```

確認結果:
- `--trace-trials N` を追加し、先頭N試行のマリガン、ライブセット、MAIN配置、結果をMarkdownへ出力できるようにした。
- 生成先: `docs/reports/autoplay/decision_trace_20260803a/`
- 5軸のDecision Traceで、T3目標 `2-11-2` に必要な11コスト札をライブセット交換で戻してしまうケースを確認。
- 原因候補: 同一コスト採用枚数が多い場合の交換予算が、直近ターンに必要な到達札にも適用されている。次は「このターンの到達に必要な手札上の最高価値札」を交換不可にする保護を追加する。
- 質問回答: 5軸で5コストもDaydream Mermaidによる `2-4-2` 代替も成立しない場合、現行モデルでは5軸のT2加速目標を満たせず、目標未達または後続のデッキ内高コストフォールバックへ落ちる。

## 20260803 オートプレイ probability mulligan 第一段

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 3 --trials 200 --seed 29 --turns 4 --trace-trials 3 \
  --outdir docs/reports/autoplay/decision_trace_20260803d \
  --summary-csv docs/reports/autoplay/autoplay_current_20260803d.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260803d.json \
  --compare-json docs/reports/autoplay/autoplay_current_20260731i.json \
  --compare-csv docs/reports/autoplay/autoplay_compare_20260803d_vs_i.csv \
  --compare-md docs/reports/autoplay/autoplay_compare_20260803d_vs_i.md
```

確認結果:
- マリガンは初手6枚の全キープ候補を評価し、T1/T2/T3までのアクセス確率 `p(T1/T2/T3)`、引ける想定枚数 `draw_windows`、上位候補比較をログへ出すようにした。
- マリガンで戻した後に実際に引き直したカード `redraw` と、引き直し後の手札 `post mulligan hand` をDecision Traceへ追加。
- `2,2,2,2,11,L` 型の手札で、2コスト過剰保持や11コスト過剰保持を避け、候補ごとの確率曲線を比較する土台を追加。
- MAIN配置は、目標未達内容を改善しない余分な低コスト配置を止めた。T2で4/5に届かないのに追加2コストを置いてT3エネルギーを潰す動きを抑制。
- 比較: 君ここ cumulative はT2 `0.91 -> 0.92`、T3 `0.90 -> 0.91`、T4 `0.795 -> 0.82`。
- 比較: 10軸 cumulative はT3 `0.455 -> 0.545`、T4 `0.37 -> 0.44`。
- 注意: 5軸 cumulative はT2 `0.795 -> 0.755`、T3 `0.52 -> 0.49` とまだ悪化。T2に5/4/Daydreamへ届かない試行の扱いと、確率モデルが「アクセス」を見ていて実配置/エネルギー制約を完全には織り込めていないことが残課題。
- 次の改善: 5軸向けに、T2加速札の探索価値をさらに重くしつつ、T3到達に必要な「T2で5または4+Daydreamを成立させる」条件を確率モデルに明示する。ライブセット交換側にも「このターン/次ターンの成立条件札を戻さない」保護を追加する。

## 20260803 オートプレイ bottleneck mulligan

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 3 --trials 200 --seed 29 --turns 4 --trace-trials 5 \
  --outdir docs/reports/autoplay/decision_trace_20260803h \
  --summary-csv docs/reports/autoplay/autoplay_current_20260803h.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260803h.json \
  --compare-json docs/reports/autoplay/autoplay_current_20260803f.json \
  --compare-csv docs/reports/autoplay/autoplay_compare_20260803h_vs_f.csv \
  --compare-md docs/reports/autoplay/autoplay_compare_20260803h_vs_f.md
```

確認結果:
- 根本原因: マリガン評価がT1-T3を合算していたため、5軸で5コスト/Daydream Mermaidを引けていない初手でも、枚数の多い11コストを未来札として残す判断が強く出ていた。
- 修正: 構築からT1-T3のaccepted targetを推定し、ターンごとの必要コスト採用枚数と想定ドロー数から到達率を概算するようにした。
- 修正: 初手に未確保のターンのうち、採用枚数が少ない到達札または進行サポート札を要求するターンをボトルネックとして扱い、全戻し/一部キープ時のターン目標到達率をマリガン評価とDecision Traceへ反映した。
- 修正: 未来ターンのカードでも、デッキ内枚数が十分あるコスト帯は弱点ターン探索を妨げないよう戻しやすくした。採用枚数が少ない到達札は希少札として保持価値を残す。
- 計算例: 5軸ではT2ボトルネックを5コストメンバー3枚 + Daydream Mermaid 4枚の7枚として扱う。5/DMなし初手では、T2目標到達率が全戻し約0.875、2枚キープ相当約0.746。
- Decision Trace確認: `docs/reports/autoplay/decision_trace_20260803h/5_deck_1d64365fb7bf71ac7081.md` のTrial 1で `critical focus` が表示され、5/DMなし初手は `keep: none` になった。
- 比較: 5軸 cumulative はT2 `0.74 -> 0.785`、T3 `0.495 -> 0.525`。combined cumulative はT2 `0.205 -> 0.23`。
- 比較: 10軸 cumulative はT2 `0.765 -> 0.79`、T3 `0.57 -> 0.59`。combined cumulative はT1 `0.545 -> 0.6`、T2 `0.215 -> 0.245`。
- 残観点: 5軸T4 cumulative は `0.425 -> 0.42` と小幅低下。T2/T3重視の副作用として15コスト探索が少し弱くなっている可能性があり、次はT3成立後のT4到達札保護を分離して改善する。

## 20260803 オートプレイ deck-specific seed

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from loveca_app.core import AppState, _autoplay_effective_seed
app=AppState(Path('.'))
for deck_path in ['llocg_db_out_full/decklists/deck_1d64365fb7bf71ac7081.tsv','llocg_db_out_full/decklists/deck_fcc369ef393b3ed66e43.tsv']:
    result=app.autoplay_trial_report(deck_path, trials=1, seed=29, max_turns=4, trace_trials=1)
    trace=result['decision_traces'][0]
    print('DECK', deck_path)
    print('base', result.get('base_seed'), 'effective', result.get('effective_seed'), 'helper', _autoplay_effective_seed(29, deck_path))
    print('initial', ' | '.join(trace.get('initial_hand') or []))
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --recent 3 --trials 200 --seed 29 --turns 4 --trace-trials 3 \
  --outdir docs/reports/autoplay/decision_trace_20260803j_seedfix_200 \
  --summary-csv docs/reports/autoplay/autoplay_current_20260803j_seedfix_200.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260803j_seedfix_200.json
```

確認結果:
- 根本原因: 5軸/10軸デッキの並びと共通カードがかなり近く、同じseedを各デッキに直接使うと同じシャッフル位置を参照して、初手が同一になることがあった。
- 修正: base seed と deck path から deterministic な effective seed を作り、デッキごとに異なる乱数列を使うようにした。同じデッキ・同じbase seedでは再現性を保つ。
- レポートに `base_seed` と `effective_seed` を出力するようにした。
- 確認: 5軸 base `29` effective `2363877751`、10軸 base `29` effective `1371471730` となり、初手が分離した。
- seed修正版200回結果: 5軸 T2 cumulative `0.79`、T3 cumulative `0.56`。10軸 T2 cumulative `0.82`、T3 cumulative `0.65`。
- 注意: seed生成方式を変えたため、過去のseed=29単体比較値とは直接比較しない。今後は固定base seedセットを複数用意して平均・ばらつきを見る。

## 20260803 オートプレイ mulligan user examples

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --deck llocg_db_out_full/decklists/deck_1d64365fb7bf71ac7081.tsv --trials 200 --trace-trials 5 --seed 29 --turns 4 \
  --outdir docs/reports/autoplay/decision_trace_20260803k_5 \
  --summary-csv docs/reports/autoplay/autoplay_current_20260803k_5.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260803k_5.json

python3 ./loveca_autoplay_report.py --root . --deck llocg_db_out_full/decklists/deck_fcc369ef393b3ed66e43.tsv --trials 200 --trace-trials 5 --seed 29 --turns 4 \
  --outdir docs/reports/autoplay/decision_trace_20260803k_10 \
  --summary-csv docs/reports/autoplay/autoplay_current_20260803k_10.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260803k_10.json

python3 ./loveca_autoplay_report.py --root . --deck llocg_db_out_full/decklists/deck_2d69085d8135c787adcc.tsv --trials 200 --trace-trials 5 --seed 29 --turns 4 \
  --outdir docs/reports/autoplay/decision_trace_20260803k_kimi \
  --summary-csv docs/reports/autoplay/autoplay_current_20260803k_kimi.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260803k_kimi.json
```

確認結果:
- ユーザー提示のマリガン9例を内部検査し、期待キープと全件一致した。
- 修正: card objectへ `base_hearts_raw` / `required_hearts_raw` を渡し、マリガン評価で要求色と基礎ハートの噛み合いを見られるようにした。
- 修正: 5軸/10軸/君ここ型を進行shapeから判定し、コスト・ライブスコア・エネルギーブースト・ハート要求で補正する汎用profile adjustmentを追加した。カード番号専用分岐は追加していない。
- 5軸: 5/DMなし初手は4/2/11を守らず全戻し寄り。5+DM+2が揃う場合は4を代替ルート札として返しやすくした。
- 10軸: 10コストが見えている場合は10+4+2を守り、13/15の孤立キープを強く抑制した。10が無い場合は4コスト中継札を1枚残し、紫ハートが多い4コストをやや優先する。
- 君ここ: 7コストが無い初手は全戻し寄り。7がある場合は0スコアドローライブと、その要求色に噛む2コストを保持しやすくした。
- 200回固定base seed比較（前回 `20260803j_seedfix_200` 比）:
  - 5軸 cumulative: T2 `0.79 -> 0.865`, T3 `0.56 -> 0.705`, T4 `0.475 -> 0.59`。combined cumulative: T2 `0.27 -> 0.34`, T3 `0.02 -> 0.03`。
  - 10軸 cumulative: T2 `0.82 -> 0.865`, T3 `0.65 -> 0.745`, T4 `0.505 -> 0.565`。combined cumulative: T2 `0.31 -> 0.405`, T3 `0.045 -> 0.05`。
  - 君ここ cumulative: T2 `0.90 -> 0.94`, T3 `0.88 -> 0.90`, T4 `0.79 -> 0.83`。combined cumulative: T2 `0.115 -> 0.155`, T3 `0.02 -> 0.035`。
- 注意: `--all` で200回レポートを開始したところ登録デッキ全体を拾って重くなったため中断した。途中生成物は `docs/reports/autoplay/decision_trace_20260803k_mulligan_examples/` に残っている。比較には上記3デッキ個別実行結果を使用した。

## 20260803 オートプレイ mulligan user examples second pass

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --root . --deck llocg_db_out_full/decklists/deck_1d64365fb7bf71ac7081.tsv --trials 200 --trace-trials 5 --seed 29 --turns 4 \
  --outdir docs/reports/autoplay/decision_trace_20260803l_5 \
  --summary-csv docs/reports/autoplay/autoplay_current_20260803l_5.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260803l_5.json

python3 ./loveca_autoplay_report.py --root . --deck llocg_db_out_full/decklists/deck_fcc369ef393b3ed66e43.tsv --trials 200 --trace-trials 5 --seed 29 --turns 4 \
  --outdir docs/reports/autoplay/decision_trace_20260803l_10 \
  --summary-csv docs/reports/autoplay/autoplay_current_20260803l_10.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260803l_10.json

python3 ./loveca_autoplay_report.py --root . --deck llocg_db_out_full/decklists/deck_2d69085d8135c787adcc.tsv --trials 200 --trace-trials 5 --seed 29 --turns 4 \
  --outdir docs/reports/autoplay/decision_trace_20260803l_kimi \
  --summary-csv docs/reports/autoplay/autoplay_current_20260803l_kimi.csv \
  --summary-json docs/reports/autoplay/autoplay_current_20260803l_kimi.json
```

確認結果:
- ユーザー提示の追加12例と前回9例を合わせた21例を内部検査し、期待キープと全件一致した。
- 修正: 5軸で5あり/DMなしの場合は2コスト2枚を守り、11以上は返す。DM+4+2+2は2ターン目DM成功ルートとして保持。DMあり4/5なしでは4探索のため2を1枚に絞る。
- 修正: 10軸で10あり4なしは10+質の高い2を1枚だけ保持。10/DMなしで4が1枚だけなら全戻し、4が複数なら質の高い4を1枚だけ残せるようにした。
- 修正: 君ここ型で7あり2なしは7単体キープ寄り。7+君ここ+2が3枚以上ある場合のみ2枚目の2を守る。
- 確認: `PL!-pb1-018` 矢澤にこは `energy_boost` ではなく `low_cost_summon` として検出される。accepted shape の `7-2-2` / `13-2-2` 代替に接続済み。
- 200回固定base seed比較（前回 `20260803k` 比）:
  - 5軸 cumulative: T2 `0.865 -> 0.86`, T3 `0.705 -> 0.71`, T4 `0.59 -> 0.59`。combined cumulative: T2 `0.34 -> 0.345`, T3 `0.03 -> 0.03`。
  - 10軸 cumulative: T2 `0.865 -> 0.855`, T3 `0.745 -> 0.755`, T4 `0.565 -> 0.575`。combined cumulative: T2 `0.405 -> 0.405`, T3 `0.05 -> 0.035`。
  - 君ここ cumulative: T2 `0.94 -> 0.94`, T3 `0.90 -> 0.90`, T4 `0.83 -> 0.83`。combined cumulative: T2 `0.155 -> 0.15`, T3 `0.035 -> 0.035`。
- 注意: 10軸は盤面到達率が上がった一方、T3 combined が小幅低下した。次の改善では、10軸の安定キープ後にライブセット交換でDM/スコア札をどう扱うかを分離して検査する。

## 20260803 プレリリースカード効果挙動監査

対象: 現行DBに効果文付きで入っている `bp7` / `sd2` 系57枚。画像manifestのみでDB効果文が未取得のカードは、効果挙動監査対象外としてDB更新完了後に再監査する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
import json,re
from pathlib import Path
from llocg_ui.engine import _match_effect_template
obj=json.loads(Path('llocg_db_out_full/cards_compiled_v7h.json').read_text(encoding='utf-8'))
rows=[]
for r in obj.get('cards',[]):
    cn=str(r.get('cardnumber',''))
    if not re.search(r'-(?:bp7|sd2)-', cn, re.I):
        continue
    for ab in r.get('abilities',[]) or []:
        for cl in ab.get('clauses',[]) or []:
            eff=str(cl.get('effect_template') or cl.get('raw') or '').strip()
            if not eff or eff in {'以下から1つを選ぶ。'}:
                continue
            match=_match_effect_template(eff)
            rows.append((bool(match), cn, r.get('cardname',''), ab.get('trigger',''), eff))
print('clauses', len(rows), 'match', sum(1 for x in rows if x[0]), 'unmatched', sum(1 for x in rows if not x[0]))
for ok,cn,name,trig,eff in rows:
    if not ok:
        print('UNMATCH', cn, name, trig, eff)
PY
```

確認結果:
- テンプレート到達: 75効果中72到達。開始時の75効果中62到達から改善。
- 実装: `PL!S-bp7-016` 型の「ステージにメンバーN人以上で複数ハート」、`PL!SP-bp7-013` 型の「指定ユニット/グループ3人でハート+ブレード」、`PL!SP-sd2-004` 型のセンター常時ブレード表示/判定、`PL!SP-bp7-025` 型のライブ開始時指定名メンバーへのブレード付与、`PL!SP-bp7-026` 型の指定名メンバー存在時ドロー/手札破棄、`PL!N-bp7-028` 型の控え室全カードデッキ下戻し+ステージグループ全体アイコン付与を汎用ルートで確認。
- 実装: エネルギー置き場からエネルギーデッキへ置かれたターンを記録し、`PL!SP-bp7-006` 型のライブ成功時スコア+1、`PL!SP-bp7-005` 型のエネルギー返却誘発を共通フックへ接続。
- 実装: `PL!SP-bp7-002` 型の「自分エネルギー7枚以上かつ相手より多い」コスト+2は、相手エネルギー値がstateに存在する環境でのみ適用。1デッキUIの標準入力項目は未整備のため、値がない場合は勝手に適用しない。
- 状態差分確認: `PL!S-bp7-016` はステージ2人でハートなし、3人で赤/緑/青+1。`PL!SP-bp7-013` はKALEIDOSCORE 3人で紫+1/ブレード+1。`PL!SP-sd2-004` はセンターでブレード+4、二重加算なし。`PL!N-bp7-028` は条件達成時pending発生、apply後に控え室全カードがデッキ下へ移動し、ステージの虹ヶ咲メンバーへ桃+1。

残件:
- `LL-bp7-001`: 手札の指定名3枚を任意コストとして捨て、プレイコストを10にする特殊プレイコスト。プレイUI/コスト支払い経路の拡張が必要。
- `PL!N-bp7-003`: 控え室コスト17以下の虹ヶ咲メンバーを下に置き、元々持つハートを置いたメンバーのハートと同じにする処理。現行stateは単色置換 `heart_replace_color` 中心で、複数色/複数個の元ハートコピーを保持する構造拡張が必要。
- `PL!S-bp7-022`: エールをデッキ上ではなくデッキ下から行う常時効果。エール処理の山札参照方向をカード効果で切り替える共通フックが必要。
- `PL!SP-bp7-005`: 「次のターンのアクティブフェイズにアクティブしない」対象エネルギーは、現行のエネルギーが枚数管理のため個別カード単位の不活性予約までは未実装。現時点ではログ/pending上の確認に留まる。

### 20260803 追記: 残件実装確認

上記残件は `llocg_ui/engine.py` BUILD_TAG `prerelease_effect_generic_routes_20260803b` で再確認。

実装:
- `LL-bp7-001` 型: BODY常時の「プレイに際し、手札から指定名メンバーカードをそれぞれ1枚ずつ控え室に置いてもよい。そうしたとき、このカードのコストはNになる。」を汎用検出。通常プレイ直前に `optional_named_hand_play_cost` pending を出し、Apply/Skip後は通常の `cmd_play` 経路へ戻す。
- `PL!N-bp7-003` 型: 「控え室のコストN以下指定グループメンバーをこのメンバーの下に置く。そうしたとき、元々持つハートは下に置いたメンバーが持つハートと同じになる。」を、既存の `green_member_cost_le_group_to_under_self` に後続処理フラグを付けて実装。`StageSlot.heart_replace_hearts` を追加し、undo/snapshot、ライブ終了cleanup、基本ハート集計、現在ハート色別/総数集計へ反映。
- `PL!S-bp7-022` 型: エールをデッキ下から行うBODY常時は既存runtimeに `_card_replaces_own_yell_with_deck_bottom` / `_yell_uses_deck_bottom` / `_take_yell_card_from_deck` が存在していたため、監査matcherへ `body_always_yell_from_deck_bottom` を追加して到達確認対象に含めた。
- `PL!SP-bp7-005` 型: 「ウェイト状態で置いたエネルギーは次のアクティブフェイズにアクティブしない」を枚数予約 `energy_no_active_next` として実処理化。次回 `refresh` で予約枚数分をウェイトに残し、予約はそのアクティブフェイズで解除する。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import json,random
from llocg_ui.db import load_cards_db
from llocg_ui import engine
from llocg_ui.engine import GameState, StageSlot, cmd_play, cmd_resolve_pending, try_apply_effect_template, refresh, owned_base_hearts, _slot_current_heart_color_counts, snapshot_state, restore_state
cards=load_cards_db(Path('.'), compiled_path=Path('llocg_db_out_full/cards_compiled_v7h.json'), tokv1_path=Path('llocg_db_out_full/cards_min_tokv1.json'))

obj=json.loads(Path('llocg_db_out_full/cards_compiled_v7h.json').read_text(encoding='utf-8'))
raw=obj.get('cards',{})
items=raw.items() if isinstance(raw,dict) else [(c.get('cardnumber') or c.get('card_number') or c.get('card_no') or '',c) for c in raw]
total=matched=0
un=[]
for cn,c in items:
    cn=str(cn or c.get('cardnumber') or '')
    if not any(x in cn for x in ['bp7','sd2']):
        continue
    if str(c.get('card_type') or c.get('type') or '').upper().startswith('ENERGY'):
        continue
    for ab in c.get('abilities') or []:
        for cl in ab.get('clauses') or []:
            eff=str(cl.get('effect_template') or cl.get('raw') or '').strip()
            if not eff:
                continue
            total += 1
            matched += 1 if engine._match_effect_template(eff) else 0
print('bp7/sd2 matcher', matched, '/', total, 'unmatched', total-matched)

gs=GameState(root='.', code='test', seed=1)
gs.hand=['LL-bp7-001','PL!S-PR-019','PL!N-PR-009','PL!SP-PR-005']
gs.energy_active=20
cmd_play(gs,cards,0,'C')
print('LL-bp7-001 pending', gs.pending[0]['kind'])
cmd_resolve_pending(gs,cards,0,'apply',random.Random(1))
print('LL-bp7-001 apply', gs.stage['C'].cardnumber, gs.energy_active, gs.green_room)

gs2=GameState(root='.', code='test', seed=2)
gs2.stage['C']=StageSlot('PL!N-bp7-003')
gs2.green_room=['PL!N-PR-003']
try_apply_effect_template(gs2,random.Random(2),cards,'自分の控え室にあるコスト17以下の『虹ヶ咲』のメンバーカード1枚をこのメンバーの下に置く。そうしたとき、ライブ終了時まで、このメンバーが元々持つハートは、これにより下に置いたメンバーカードが持つハートと同じになる。',{'source_cn':'PL!N-bp7-003','pos':'C'})
print('PL!N-bp7-003 hearts', gs2.stage['C'].under_cards, gs2.stage['C'].heart_replace_hearts, owned_base_hearts(gs2,cards), _slot_current_heart_color_counts(gs2,cards,'C',gs2.stage['C']))

gs3=GameState(root='.', code='test', seed=3)
gs3.energy_active=0
gs3.energy_wait=0
try_apply_effect_template(gs3,random.Random(3),cards,'自分のエネルギーデッキから、エネルギーカードを2枚ウェイト状態で置く。そのエネルギーカードは、次のターンのアクティブフェイズにアクティブしない。',{'source_cn':'TEST'})
print('energy reserve before refresh', gs3.energy_active, gs3.energy_wait, gs3.energy_no_active_next)
gs3.pending=[]
refresh(gs3)
print('energy reserve after refresh', gs3.energy_active, gs3.energy_wait, gs3.energy_no_active_next)

snap=snapshot_state(gs2)
gs2.stage['C'].heart_replace_hearts={}
restore_state(gs2,snap)
print('snapshot restore heart_replace_hearts', gs2.stage['C'].heart_replace_hearts)
PY
```

確認結果:
- `py_compile` 通過。
- `bp7/sd2 matcher 76 / 76 unmatched 0`。
- `LL-bp7-001` は `optional_named_hand_play_cost` pending発生、Applyで指定名3枚が控え室へ移動し、コスト10として通常プレイ完了。Skip経路も別確認し、通常コスト15でプレイされ指定名カードは手札に残る。
- `PL!N-bp7-003` は控え室の虹ヶ咲メンバーを下に置き、下に置いたカードの印刷ハート `{pink:1, green:1, purple:1}` がこのメンバーの元ハートとして集計される。
- `PL!SP-bp7-005` 型はウェイトエネルギー2枚を `energy_no_active_next=2` として予約し、次回refreshで active へ移さず wait に残し、予約を0へ戻す。
- snapshot/restoreで `heart_replace_hearts` と `energy_no_active_next` が復元される。

残件:
- 今回確認範囲のプレリリースDB登録済み効果について、matcher未到達残件は0。
- 画像manifestのみ取得済みでDB本文未取得の新規公開カードは、DB更新完了後に別途再監査が必要。

### 20260803 追記: no-active予約エネルギーの効果アクティブ優先

ユーザー指摘により、「次のターンのアクティブフェイズにアクティブしない」エネルギーがある状態で「エネルギーをアクティブにする効果」を解決した場合、予約中のウェイトエネルギーを優先してアクティブにする仕様へ補正。

実装:
- `llocg_ui/engine.py` に `_activate_wait_energy` を追加。
- 効果によるエネルギーアクティブ処理を同ヘルパーへ集約し、`energy_no_active_next` を優先消費するようにした。
- waitエネルギーをエネルギーデッキへ戻す/メンバー下へ移す場合も、存在しない予約が残らないよう `energy_no_active_next` を減算。
- 通常アクティブフェイズの `refresh` では従来通り、残った予約分をウェイトに残す。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.db import load_cards_db
from llocg_ui.engine import GameState, try_apply_effect_template, refresh, snapshot_state, restore_state
cards=load_cards_db(Path('.'), compiled_path=Path('llocg_db_out_full/cards_compiled_v7h.json'), tokv1_path=Path('llocg_db_out_full/cards_min_tokv1.json'))

gs=GameState(root='.', code='test', seed=1)
gs.energy_active=0
gs.energy_wait=3
gs.energy_no_active_next=2
try_apply_effect_template(gs, random.Random(1), cards, 'エネルギーを1枚アクティブにする。', {'source_cn':'TEST'})
print(gs.energy_active, gs.energy_wait, gs.energy_no_active_next)

gs2=GameState(root='.', code='test', seed=2)
gs2.energy_active=0
gs2.energy_wait=3
gs2.energy_no_active_next=2
try_apply_effect_template(gs2, random.Random(2), cards, 'エネルギーを2枚アクティブにする。', {'source_cn':'TEST'})
print(gs2.energy_active, gs2.energy_wait, gs2.energy_no_active_next)

gs3=GameState(root='.', code='test', seed=3)
gs3.energy_active=0
gs3.energy_wait=3
gs3.energy_no_active_next=2
try_apply_effect_template(gs3, random.Random(3), cards, 'エネルギーを1枚アクティブにする。', {'source_cn':'TEST'})
gs3.pending=[]
refresh(gs3)
print(gs3.energy_active, gs3.energy_wait, gs3.energy_no_active_next)

s=snapshot_state(gs)
gs.energy_no_active_next=99
restore_state(gs,s)
print(gs.energy_active, gs.energy_wait, gs.energy_no_active_next)
PY
```

確認結果:
- `py_compile` 通過。
- `wait=3 / energy_no_active_next=2` から効果で1枚アクティブ: `active=1 / wait=2 / energy_no_active_next=1`。
- 同条件から効果で2枚アクティブ: `active=2 / wait=1 / energy_no_active_next=0`。
- 効果で1枚だけ起こした後の通常refresh: 残った予約1枚だけがウェイトに残り、通常wait分はアクティブ化。
- snapshot/restoreで効果解決後の予約数が復元される。

### 20260803 追記: オートプレイのメイン配置→ライブセット順序修正

ユーザー指摘により、オートプレイのターン内処理順序を確認。旧実装では通常ドロー後にライブセット交換を行い、その交換で引いたカードを同じターンのメンバー配置へ使えていた。これは実プレイの「メインフェイズでステージ配置後にライブセットフェイズで交換する」順序と異なるため、ステージ進行率を過大評価していた。

実装:
- `loveca_app/autoplay.py` の試行順序を、通常ドロー→メイン配置→ライブセット交換へ修正。
- decision trace の表示順も同じ順序へ修正。
- ライブセット交換の判断で、ステージ配置後の盤面を参照するようにした。
- レポート内の `decision_policy` / `effect_assumptions` の説明文も現行順序へ修正。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
git diff --check
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import json
from loveca_app.autoplay import _improve_persistent_stage, _choose_live_set_cards

root = Path('.')
rows = json.loads((root / 'llocg_db_out_full/cards_min_tokv1.json').read_text(encoding='utf-8'))
by_no = {str(row.get('cardnumber') or row.get('card_no')): row for row in rows}

def card(cn):
    row = by_no[cn]
    typ = str(row.get('card_type_norm') or row.get('card_type') or row.get('type') or row.get('card_type_raw') or '')
    kind = 'member' if typ.upper() == 'MEMBER' or 'メンバー' in typ else 'live'
    return {
        'card_no': cn,
        'name': str(row.get('cardname') or row.get('name') or ''),
        'kind': kind,
        'cost': int(float(row.get('cost') or 0)) if kind == 'member' else None,
        'score': int(float(row.get('score') or 0)) if kind == 'live' and str(row.get('score') or '').strip() else 0,
        'draw_n': 2 if cn == 'PL!S-bp2-024' else 0,
        'energy_boost_n': 1 if cn == 'PL!N-bp4-030' else 0,
        'base_hearts_raw': str(row.get('base_hearts_raw') or ''),
        'effect_text': str(row.get('effect_text_norm') or row.get('effect_text') or ''),
        'value': 0,
    }

def run_case(label, hand_no, targets):
    hand = [card(cn) for cn in hand_no]
    stage = [None, None, None]
    energy = {'active': 4, 'wait': 0, 'deck_remaining': 20}
    stage = _improve_persistent_stage(stage, hand, targets[0], energy)
    live, selected = _choose_live_set_cards(
        hand,
        any(alt == [2, 4, 2] for alt in targets[0]),
        [alt for turn in targets[:3] for alt in turn],
        [card(cn) for cn in hand_no],
        {},
        targets[:3],
        0,
        stage,
    )
    print(label, [c['card_no'] if c else None for c in stage], [c['card_no'] for c in selected], live['card_no'] if live else None)

five_targets = [[[2,2],[4]], [[2,5,2],[2,4,2]], [[2,11,2]]]
ten_targets = [[[2,2],[4]], [[2,4,2]], [[2,10,2],[2,11,2]]]
kimi_targets = [[[2,2],[4]], [[7,2],[7,2,2]], [[13,2],[13,2,2]]]

run_case('5A', ['PL!N-bp5-001','PL!SP-sd1-019','PL!S-sd1-015','PL!HS-bp6-017','PL!N-pb1-011','PL!N-bp3-030','PL!N-bp5-027'], five_targets)
run_case('5B', ['PL!N-bp4-030','PL!HS-PR-022','PL!N-bp4-017','PL!SP-pb1-014','PL!HS-bp6-017','PL!N-pb1-011','PL!N-bp5-027'], five_targets)
run_case('5C', ['PL!N-bp4-030','PL!SP-sd1-019','PL!N-bp4-017','PL!S-sd1-015','PL!HS-bp6-017','PL!N-pb1-011','PL!N-bp3-030'], five_targets)
run_case('5D', ['PL!N-bp5-001','PL!N-bp4-030','PL!HS-PR-022','PL!SP-bp2-019','PL!HS-bp6-017','PL!N-pb1-011','PL!N-bp5-027'], five_targets)
run_case('10E', ['PL!SP-bp5-001','PL!SP-pb1-014','PL!N-bp4-017','PL!-bp5-011','PL!N-pb1-011','PL!N-bp4-030','PL!N-bp3-030'], ten_targets)
run_case('10F', ['PL!SP-bp5-001','PL!HS-PR-022','PL!SP-pb1-014','PL!N-bp4-030','PL!N-bp3-008','PL!N-pb1-011','PL!N-bp5-027'], ten_targets)
run_case('10G', ['PL!N-bp4-030','PL!HS-PR-022','PL!SP-pb1-014','PL!N-bp4-017','PL!N-bp3-008','PL!N-pb1-011','PL!N-bp3-030'], ten_targets)
run_case('10H', ['PL!HS-PR-022','PL!SP-pb1-014','PL!N-bp4-017','PL!-bp5-011','PL!N-bp3-008','PL!N-pb1-011','PL!N-bp3-030'], ten_targets)
run_case('kimiI', ['PL!N-bp5-007','PL!S-bp2-024','PL!HS-bp2-004','PL!SP-bp2-009','PL!SP-bp5-023','PL!SP-bp2-024','PL!S-sd1-015'], kimi_targets)
run_case('kimiJ', ['PL!N-bp5-007','PL!HS-bp2-004','PL!S-bp6-014','PL!SP-bp2-009','PL!SP-bp5-023','PL!SP-bp2-024','LL-bp5-001'], kimi_targets)
run_case('kimiK', ['PL!N-bp5-007','PL!S-bp2-024','PL!SP-bp2-009','PL!SP-bp5-002','PL!SP-bp5-023','PL!SP-bp2-024','LL-bp5-001'], kimi_targets)
run_case('kimiL', ['PL!S-bp2-024','PL!HS-bp2-004','PL!S-bp6-014','PL!N-bp5-021','PL!SP-bp2-009','PL!SP-bp5-023','PL!SP-bp2-024'], kimi_targets)
PY
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --recent 1 --deck-name 5 --trials 200 --seed 29 --turns 4 --trace-trials 5 --trace-out docs/reports/autoplay/decision_trace_20260803m_5 --summary-csv docs/reports/autoplay/autoplay_current_20260803m_5.csv --summary-json docs/reports/autoplay/autoplay_current_20260803m_5.json --compare-json docs/reports/autoplay/autoplay_current_20260803l_5.json --compare-csv /tmp/loveca_compare_5.csv --compare-md /tmp/loveca_compare_5.md
python3 ./loveca_autoplay_report.py --recent 1 --deck-name 10 --trials 200 --seed 29 --turns 4 --trace-trials 5 --trace-out docs/reports/autoplay/decision_trace_20260803m_10 --summary-csv docs/reports/autoplay/autoplay_current_20260803m_10.csv --summary-json docs/reports/autoplay/autoplay_current_20260803m_10.json --compare-json docs/reports/autoplay/autoplay_current_20260803l_10.json --compare-csv /tmp/loveca_compare_10.csv --compare-md /tmp/loveca_compare_10.md
python3 ./loveca_autoplay_report.py --recent 1 --deck-name 君ここ --trials 200 --seed 29 --turns 4 --trace-trials 5 --trace-out docs/reports/autoplay/decision_trace_20260803m_kimi --summary-csv docs/reports/autoplay/autoplay_current_20260803m_kimi.csv --summary-json docs/reports/autoplay/autoplay_current_20260803m_kimi.json --compare-json docs/reports/autoplay/autoplay_current_20260803l_kimi.json --compare-csv /tmp/loveca_compare_kimi.csv --compare-md /tmp/loveca_compare_kimi.md
```

確認結果:
- `py_compile` 通過。
- `git diff --check` 通過。
- ユーザー提示のT1開始時7枚手札ケース12件は、すべて期待どおりのステージ配置とライブセット対象に一致。
- decision trace は `normal_draw` → `main` → `live_set` → `result` の順に出力されることを確認。
- `20260803l` 以前はライブセット交換ドローを同ターン配置へ利用できる楽観値だったため、`20260803m` を新しい比較基準にする。
- 200試行/seed 29での `20260803l` 比較では、5軸T3 cumulative `0.71 -> 0.515`、10軸T3 `0.755 -> 0.64`、君ここT3 `0.9 -> 0.775`。低下はモデル劣化というより、同ターン交換ドローを使えなくしたことによる過大評価の補正。

### 20260803 追記: ステージ維持・対策枠need・重複中継札交換の補正

ユーザー指摘:
- 5軸ログで `PL!N-bp3-008 エマ・ヴェルデ cost=13 need=43.2` となっており、進行に使わない対策枠カードが不当に高評価されていた。
- `2-2` から `5-2-2` / `4-2-2` へ進む際、空き枠に追加せず2コストを置換してから別2コストを出し直すようなログがあり不自然。
- 10軸T1で重複した4コストをセットせず2枚だけセットしていた。
- 10軸T3で成功できそうな `Love U my friends` をライブセットしていなかった。

実装:
- `loveca_app/autoplay.py` の `BUILD_TAG` を `autoplay_stage_keep_and_sideboard_need_20260803a` へ更新。
- 空きステージ枠がある間は、メイン配置探索で既存メンバーの置換を候補にしないよう修正。
- need scoreの「目標より大きいコスト」評価を、目標との差が小さい代替に限定。単に大きいだけの13/15コスト対策枠は過保護にしない。
- ライブセット交換で、未来ターンに必要なコストでも、ステージ+手札で必要数を超えている重複分は交換候補にできるよう修正。
- 10軸T3以降で、戦略分岐がメンバーだけで交換枠を埋める前に、手札の有効スコアライブを交換候補へ入れるよう修正。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
git diff --check
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --deck llocg_db_out_full/decklists/deck_1d64365fb7bf71ac7081.tsv --trials 200 --seed 29 --turns 4 --trace-trials 5 --outdir docs/reports/autoplay/decision_trace_20260803n_5 --summary-csv docs/reports/autoplay/autoplay_current_20260803n_5.csv --summary-json docs/reports/autoplay/autoplay_current_20260803n_5.json --compare-json docs/reports/autoplay/autoplay_current_20260803m_5.json --compare-csv /tmp/loveca_compare_5_n.csv --compare-md /tmp/loveca_compare_5_n.md
python3 ./loveca_autoplay_report.py --deck llocg_db_out_full/decklists/deck_fcc369ef393b3ed66e43.tsv --trials 200 --seed 29 --turns 4 --trace-trials 5 --outdir docs/reports/autoplay/decision_trace_20260803o_10 --summary-csv docs/reports/autoplay/autoplay_current_20260803o_10.csv --summary-json docs/reports/autoplay/autoplay_current_20260803o_10.json --compare-json docs/reports/autoplay/autoplay_current_20260803m_10.json --compare-csv /tmp/loveca_compare_10_o.csv --compare-md /tmp/loveca_compare_10_o.md
```

確認結果:
- `py_compile` 通過。
- `git diff --check` 通過。
- 5軸T1/T2ログで `PL!N-bp3-008 エマ・ヴェルデ` のpre-exchange needが `43.2 -> 0.0` になり、ライブセット交換対象へ回ることを確認。
- 5軸T2で `2-2 -> 5-2-2` が `main played/replaced in: PL!N-bp5-001 上原歩夢 cost=5` / `main replaced out: none` になり、無駄な2コスト置換が消えた。
- 10軸T1で重複した4コスト `PL!HS-PR-022 セラス` がライブセット交換対象に入ることを確認。
- 10軸T2で `2-2 -> 4-2-2` が空き枠追加になり、`main replaced out: none` を確認。
- 10軸T3で `PL!N-bp3-030 Love U my friends` がライブセット対象に入ることを確認。
- 200試行/seed 29の比較では、5軸T2 cumulative `0.815 -> 0.865`、10軸T2 cumulative `0.775 -> 0.85`、10軸T3 cumulative `0.64 -> 0.705`。5軸T3 cumulativeは `0.515 -> 0.47` に低下。
  ※20260803内部確認: 「13/15を11の代替進行札として過保護にしなくなった影響」という説明は不正確。5軸T3は11コストを使うターンであり、13/15はT3進行札ではない。現行方針は、T2目標札が見つかった直後のライブセットから11探索へ切り替えること。

### 20260803 追記: オートプレイ 5軸T2後11探索・10軸T3 13候補除外

ユーザー指摘:
- 5軸でT2目標札を見つけた後、11コスト探索へ切り替える判断タイミングはライブセット時以外にない。
- 10軸でT1に4単騎を選ぶ場合は2欠損なので、手札の2コストを全て保持する。
- 2-2進行済みで手札に2コストが残っている場合、その2コストはライブセット交換へ出してよい。
- この10軸ではT3に13コストを絶対に出さないため、`2-13-2` をaccepted targetやneed計算へ混ぜない。
- ライブセット判断は手札交換だけでなく、簡易的な成功見込みも考慮する。

実装:
- `loveca_app/autoplay.py` の `BUILD_TAG` を `autoplay_live_success_coarse_and_target_split_20260803a` へ更新。
- 10軸T3の target alternatives から `2-13-2` を除外し、`2-10-2 / 2-11-2` のみにした。
- 5軸では、T2以降に現在のステージが当該ターン目標を満たしており、次ターンが11を必要とする場合、ライブセット交換を11探索へ寄せるようにした。11コストは交換対象から外し、13以上や低コスト重複、ライブを優先して流す。
- 10軸では、4単騎で入っている場合は2コストを交換対象にせず保持し、2-2で入れている場合は手札に残る2コストを交換対象にできるよう分岐した。
- マリガン候補評価で、初期3ターンの目標候補に含まれない13以上コストを「希少だから守る」方向へ寄せない補正を追加。
- ライブ成功候補は、厳密な基礎ハート充足判定ではなく、DM/LU/ドローライブを粗く候補化する軽量判定へ変更。精密なエール期待値モデルはステージ進行評価が安定してから追加する。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./loveca_app/autoplay.py ./loveca_app/core.py ./loveca_autoplay_report.py
git diff --check
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./loveca_autoplay_report.py --deck llocg_db_out_full/decklists/deck_fcc369ef393b3ed66e43.tsv --trials 200 --seed 29 --turns 4 --trace-trials 5 --outdir docs/reports/autoplay/decision_trace_20260803s_10 --summary-csv docs/reports/autoplay/autoplay_current_20260803s_10.csv --summary-json docs/reports/autoplay/autoplay_current_20260803s_10.json --compare-json docs/reports/autoplay/autoplay_current_20260803o_10.json --compare-csv /tmp/loveca_compare_10_s.csv --compare-md /tmp/loveca_compare_10_s.md
python3 ./loveca_autoplay_report.py --deck llocg_db_out_full/decklists/deck_1d64365fb7bf71ac7081.tsv --trials 200 --seed 29 --turns 4 --trace-trials 5 --outdir docs/reports/autoplay/decision_trace_20260803s_5 --summary-csv docs/reports/autoplay/autoplay_current_20260803s_5.csv --summary-json docs/reports/autoplay/autoplay_current_20260803s_5.json --compare-json docs/reports/autoplay/autoplay_current_20260803n_5.json --compare-csv /tmp/loveca_compare_5_s.csv --compare-md /tmp/loveca_compare_5_s.md
```

確認結果:
- `py_compile` 通過。
- `git diff --check` 通過。
- 10軸の `accepted targets` は `2-2 or 4 / 2-4-2 / 2-10-2 or 2-11-2 / 15-4-2 or 15-2-2` となり、`2-13-2` が消えた。
- 10軸Trial 1では、初手の13エマ/15ミアを返し、2千砂都/4セラス/2千砂都/10かのんをキープすることを確認。
- 5軸/10軸のT2で、Daydream Mermaidが `live_for_success` になり、`energy_added=1` として扱われるケースを確認。
- 200試行/seed 29のステージ進行比較では、5軸T3 cumulative `0.47 -> 0.565`、5軸T4 `0.265 -> 0.32`、10軸T2 `0.85 -> 0.87`、10軸T3 `0.705 -> 0.715`。
- ライブ込み指標は旧比較より低下しているが、これは以前の「交換したライブのうち最高スコアを成功扱いする」過大評価をやめ、実際にlive_for_successとして選んだライブだけを成功候補にした影響。ライブ成功率の精密評価は別途改善対象。
