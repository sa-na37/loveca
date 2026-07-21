# Loveca 配布構成メモ 20260721

## 採用する配布方針

- 正式入口は macOS では `launch_loveca.command`、Windows では `launch_loveca.bat`、共通手動起動では `python3 ./run_loveca_app.py`。
- 起動後は `Loveca Application` 管理画面を開き、そこから手動シミュレータ、リモート対戦、デッキ管理、DB更新へ進む。
- 専用ウィンドウは `run_loveca_app.py --window-mode app` で開く。Chrome / Edge のアプリウィンドウを優先し、失敗時は通常ブラウザへフォールバックする。
- 配布 zip は `tools/build_loveca_distribution.py` で生成する。
- GitHub Releases へ置く配布物は `loveca-macos.zip` / `loveca-windows.zip` / `loveca-source.zip` の3系統に分ける。

## 配布に含めるもの

- `loveca_app/`
- `llocg_ui/`
- `llocg_dual_v2/`
- `llocg_ext/`
- `llocg_db_out_full/` の正本 DB、画像、デッキリスト
- `manual_overrides/`
- 起動スクリプト類
- `docs/debug/` と `docs/notes/`

## 配布から除外するもの

- `.git/`
- `.venv/`
- `.cache_llocg*`
- `__pycache__/`
- `jank/`
- 既存 zip
- 一時更新作業ディレクトリ
- macOS の `.DS_Store`

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

## GitHub 配布メモ

- GitHub Releases には Release asset だけへ独自パスワードを設定する機能はない。
- 限定配布したい場合は private repository にし、ダウンロードできるユーザーを collaborator / team の read 権限で制限する。
- private repository の Release は read 権限を持つユーザーのみ閲覧・取得できる。
- 公開 repo の Releases は誰でも取得できるため、限定配布には向かない。
- GitHub アカウントを持たない相手へ個別配布する場合は、GitHub Releases ではなく、Google Drive / OneDrive / S3 などの共有リンク・期限付きURL・パスワード付きzipを検討する。

## Windows 対応

- `launch_loveca.bat` を同梱する。
- Python 3 が PATH にある場合は `python`、なければ Windows Python Launcher の `py -3` を使う。
- 専用ウィンドウは Edge / Chrome の `--app=` を優先し、失敗時は通常ブラウザにフォールバックする。
- 初期配布は Python 3 インストール前提。次段階で PyInstaller による exe 化を検討する。
