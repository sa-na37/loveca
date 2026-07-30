# Loveca Implementation Reference Index 20260729

## 目的

これまでの実装内容、デバッグメモ、配布作業、DB更新メモを探しやすくするための索引。
詳細な履歴は各文書を正本として参照する。

## 常時確認するルール

- `docs/notes/loveca_runtime_implementation_rules_20260708.md`
  - 効果実装、UI実装、デバッグコメント処理、カード番号専用分岐禁止などの作業ルール。
- `AGENTS.md`
  - リポジトリ全体の作業ルール、デバッグコマンド形式、BUILD_TAG、git運用。

## 現行デバッグ文書

- `docs/debug/loveca_debug_commands_current_updates_20260623.md`
  - 通常実装中に追記する現行デバッグコマンド。
- `docs/debug/loveca_debug_commands_20260623.md`
  - ユーザー確認・監修用の統合デバッグメモ。
  - 指定タイミング以外では直接編集しない。
- `docs/debug/loveca_two_latest_decks_runtime_debug_20260721.md`
  - 2デッキ/リモート関連の実行確認メモ。

## 実装残件・整理表

- `docs/debug/loveca_remaining_implementation_list_20260701.md`
  - 未実装効果や実装残件の整理履歴。
- `docs/notes/loveca_cleanup_classification_table_20260622.md`
  - 初期整理時の分類表。

## DB / 画像 / 更新処理

- `docs/notes/loveca_db_update_process_memo_20260527.md`
  - DB更新工程の基本メモ。
- `docs/notes/loveca_db_update_speed_audit_20260722.md`
  - DB更新が重い原因と改善方針。
- `docs/notes/loveca_db_manual_corrections_20260715.md`
  - Wiki/DB由来の手動補正履歴。

## 配布 / GitHub / リリース

- `docs/notes/loveca_distribution_plan_20260721.md`
  - 配布ルート、GitHub Release、Windows/Mac対応の方針。
- `docs/notes/loveca_next_release_changes_20260722.md`
  - 次回リリースに含める変更内容のメモ。
- `docs/notes/loveca_global_viewport_scale_memo_20260715.md`
  - 表示倍率や画面スケール関連のメモ。

## UI / レイアウト / ハンドオフ

- `docs/handoffs/loveca_handoff_20260721_broad_ui_layout_items.md`
  - UIレイアウト全般の未処理/監査項目。
- `docs/handoffs/loveca_handoff_20260721_deferred_ui_and_reaudit_items.md`
  - 後回しUI項目と再監査項目。
- `docs/handoffs/loveca_handoff_20260721_visual_confirmation_checklist_ja.md`
  - 目視確認チェックリスト。

## 効果監査レポート

- `loveca_reports/`
  - 効果ファミリー単位の監査レポート置き場。
  - `*_family_audit_*.md` は、同型効果の代表例、実装対象、注意点を確認する時に参照する。
- `_codex_outputs/effect_full_audit_*/`
  - 大量監査や候補コマンド生成時の出力。
  - 正式文書というより作業成果物なので、必要な時だけ参照する。

## オートプレイ

- `docs/notes/loveca_autoplay_design_20260729.md`
  - オートプレイ3段階実装の設計文書。
  - Stage 1の実装対象、Stage 2/3のデータ案と方針を記載。
- `docs/reports/autoplay/`
  - `loveca_autoplay_report.py` で生成するモデルデッキ比較用の人間可読レポート。
  - デッキ名が空または重複しても見分けられるよう、デッキファイル由来の識別子をファイル名に含める。

## 文書配置ルール

- ルート直下に作業用 `.md` を増やさない。
- 引き継ぎは `docs/handoffs/`。
- デバッグコマンドは `docs/debug/`。
- 設計、DB、配布、索引は `docs/notes/`。
