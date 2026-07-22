# Loveca 配布構成メモ 20260721

## 採用する配布方針

- 正式入口は macOS では `launch_loveca.command`、Windows では `launch_loveca.bat`、共通手動起動では `python3 ./run_loveca_app.py`。
- 起動後は `Loveca Application` 管理画面を開き、そこから手動シミュレータ、リモート対戦、デッキ管理、DB更新へ進む。
- 専用ウィンドウは `run_loveca_app.py --window-mode app` で開く。Chrome / Edge のアプリウィンドウを優先し、失敗時は通常ブラウザへフォールバックする。
- 配布 zip は `tools/build_loveca_distribution.py` で生成する。
- 配布物は `loveca-macos.zip` / `loveca-windows.zip` / `loveca-source.zip` の3系統に分ける。
- 外部サイトから取得したカード画像はGitHub配布zipに含めない。カード画像はアプリ起動後、ユーザー許可の更新処理で取得する。
- UI用画像は `loveca-ui-assets.zip` として本体とは別に直接配布する。ユーザーは本体zip展開後の `loveca` フォルダ直下に置く。
- 起動時に `loveca-ui-assets.zip` または `loveca-ui-assets/` が直下にあれば、プレイマット、裏面、NoImage、texticons等を所定位置へ自動配置する。
- GitHub Releases 用には日付入りで `loveca-macos-YYYYMMDD.zip` / `loveca-windows-YYYYMMDD.zip` / `loveca-source-YYYYMMDD.zip` を作る。
- macOS / Windows の利用者向け zip には `README.md` と起動に必要な runtime / DB だけを含める。カード画像、UI画像、開発メモ、引き継ぎ、デバッグコマンド、`AGENTS.md` は含めない。
- `source` zip には開発・監査用に `AGENTS.md` と `docs/debug` / `docs/handoffs` / `docs/notes` を含める。
- `user_data/` は個人設定、選択デッキ、リモートセッション履歴を含むため配布zipから除外する。必要なフォルダはアプリ起動時に自動作成する。

## 配布に含めるもの

- `loveca_app/`
- `llocg_ui/`
- `llocg_dual_v2/`
- `llocg_ext/`
- `llocg_db_out_full/` の正本 DB とデッキリスト
- `manual_overrides/`
- 起動スクリプト類
- source zip のみ `docs/debug/`、`docs/handoffs/`、`docs/notes/`

## 配布から除外するもの

- `.git/`
- `.venv/`
- `.cache_llocg*`
- `__pycache__/`
- `jank/`
- `user_data/`
- 既存 zip
- 一時更新作業ディレクトリ
- macOS の `.DS_Store`
- 外部取得カード画像 `llocg_db_out_full/card_images/BP*/...`
- UI画像 `playmat.jpg` / `NoImage.PNG` / `back.png` / `card_images/texticons/*` は本体zipから除外し、UI資産バンドルへ分離する。

## 起動確認コマンド

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 ./run_loveca_app.py --window-mode none --port 8875
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 ./tools/build_loveca_distribution.py
```

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 ./tools/build_loveca_distribution.py --target macos --output ./_codex_outputs/loveca-macos.zip
python3 ./tools/build_loveca_distribution.py --target windows --output ./_codex_outputs/loveca-windows.zip
python3 ./tools/build_loveca_distribution.py --target source --output ./_codex_outputs/loveca-source.zip
```

GitHub Releases 用:

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 ./tools/build_loveca_distribution.py --target macos --output ./_codex_outputs/github_release/loveca-macos-20260721.zip
python3 ./tools/build_loveca_distribution.py --target windows --output ./_codex_outputs/github_release/loveca-windows-20260721.zip
python3 ./tools/build_loveca_distribution.py --target source --output ./_codex_outputs/github_release/loveca-source-20260721.zip
python3 ./tools/build_loveca_distribution.py --target ui-assets --output ./_codex_outputs/github_release/loveca-ui-assets-20260721.zip
```

## Windows 対応

- `launch_loveca.bat` を同梱する。
- Python 3 が PATH にある場合は `python`、なければ Windows Python Launcher の `py -3` を使う。
- 専用ウィンドウは Edge / Chrome の `--app=` を優先し、失敗時は通常ブラウザにフォールバックする。
- 初期配布は Python 3 インストール前提。次段階で PyInstaller による exe 化を検討する。
