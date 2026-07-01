# Loveca / LLCG Simulator

ラブライブ！シリーズ オフィシャルカードゲーム（ラブカ / LLCG）の手動シミュレータ実装です。

## 使い方

Web UI を起動します。

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 ./run_llocg_ui_web.py
```

ブラウザで開きます。

```text
http://127.0.0.1:8787/
```

通常はデフォルトデッキで起動します。デバッグ時の初期状態は `LLOCG_*` 環境変数で指定します。

## 正本

- Runtime: `llocg_ui/`
- UI / state: `llocg_ui/server.py`
- Engine: `llocg_ui/engine.py`
- Effect matcher / resolver: `llocg_ui/effects/`
- Compiled DB: `llocg_db_out_full/cards_compiled_v7h.json`
- tokv1 DB: `llocg_db_out_full/cards_min_tokv1.json`

root 直下の DB コピーではなく、通常は `llocg_db_out_full/` 配下を基準にします。

## 作業ルール

作業前に `AGENTS.md` を読んでください。

特に重要なルール:

- カード番号専用分岐を増やさない
- 既存の generic route / matcher / resolver / helper を先に確認する
- 新規効果はカード単位ではなく効果ファミリー単位で一般化する
- 実装はできるだけ `llocg_ui/effects/` 配下へ寄せる
- 変更対象 `.py` の `BUILD_TAG` を更新する
- 変更後は `python3 -m py_compile` を通す

## 整理メモ

- 現行の整理分類表: `docs/notes/loveca_cleanup_classification_table_20260622.md`
- 最新の引き継ぎメモ: `docs/handoffs/loveca_handoff_20260625c.md`
- 実装分デバッグメモ: `docs/debug/loveca_debug_commands_20260623.md`
- 監査レポート: `loveca_reports/`
- 監査スクリプト: `tools/audit_*.py`

## デバッグ起動

効果テストでは環境変数で初期状態を作ってから起動します。
