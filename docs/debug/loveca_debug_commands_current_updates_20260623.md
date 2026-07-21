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

### 2026-07-21 effect-debug residual policy cleanup

※20260721内部確認: 効果処理関連の残件を現行仕様に合わせて再分類した。2デッキ用UIでは秘匿不要のため、相手手札候補をactive側で表示することは不具合扱いしない。1デッキ版では相手個別カードstateを持たないため、相手成功ライブ置き場、相手ステージ、相手ライブカード置き場などの一部比較・反映は手入力/手動反映を正式経路とする。

確認結果:

- 旧デバッグ文書に残る `発生源なし` / `自動効果の無言処理` 系の代表指摘は、現行では `source_cn`、実行中効果本文、`message_ack` / `confirm_effect` / `auto_order` で確認対象を渡す方針に整理済み。直近P1/P2/2デッキbridge確認では再発なし。
- 旧デバッグ文書に残る相手未モデルコメントは、1デッキ版では手動確認仕様、2デッキ版では相手context/action bridgeで実反映する対象、という分類へ更新済み。
- UI目視・操作感に属するものは runtime 成否とは分離し、ユーザー実機確認用の日本語チェックリスト `docs/handoffs/loveca_handoff_20260721_visual_confirmation_checklist_ja.md` へ集約する。
