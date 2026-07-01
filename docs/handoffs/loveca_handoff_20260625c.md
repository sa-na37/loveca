# Loveca handoff 20260625c

## 実装概要

- top-k complex family の未監査残件をまとめて実装し、監査上の `needs_audit_unmatched_topk` を 0 件にした。
- `llocg_ui/engine.py` の BUILD_TAG は `unmatched_topk_batch_20260625c`。
- `llocg_ui/server.py` の APP_VERSION / BUILD_TAG も `unmatched_topk_batch_20260625c` に更新した。

## 追加した主な効果ファミリー

- `look_top_named_members_optional_then_opponent_wait_cost_blade`
  - `LL-bp4-001`
  - 対象名メンバーをデッキ上5枚から任意で手札に加え、選んだカードのコスト以下かつ元々ブレード3以下の相手メンバーをウェイトにする人数入力へ接続。
- `choose_heart_color_reveal_topk_all_match_group_pick_gain_blades`
  - `PL!-bp6-006`
  - 色指定後、公開5枚が指定色条件を満たす場合に `μ's` カードを手札へ加え、ブレード3本を付与。
- `stage_named_exists_reveal_topk_named_pick_gain_picked_hearts`
  - `PL!N-bp5-029`
  - ステージに `中須かすみ` がいる場合、公開4枚から `中須かすみ` カードを選び、選んだカードの色ハートをステージの `中須かすみ` へ付与。公開カードは全て控え室へ送る。
- `optional_repeat_mill_top1_gain_blade_wait_if_live`
  - `PL!SP-bp5-009`
  - 最大5回、任意でデッキ上1枚を控え室へ置き、ブレードを得る。置いたカードがライブなら自身をウェイトにする。

## 直前バッチから継続して入った効果

- ライブ合計スコア+N枚を見る効果。
- ステージ全体人数参照の公開スコア加算。
- ステージグループ人数分を見る、1枚をデッキ上へ戻して公開し、ライブならスコア加算。
- ライブ/コスト以上メンバーを選んで公開し続ける効果。
- 数指定後、トップメンバーのコスト比較で手札/ブレード付与する効果。
- 指定グループライブの異名数条件回収。
- 任意メンバー選択後、指定グループならアイコン付与。
- 捨てたカードのグループ一致で top-k choose、非一致でライブ回収。
- ライブカード置き場からライブ開始時能力なしライブをデッキ上へ戻してアイコン付与。

## 監査結果

- `python3 tools/audit_topk_complex_family_20260604.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
- `needs_audit_unmatched_topk`: 0 件

## 確認済み

- `python3 -m py_compile llocg_ui/engine.py llocg_ui/server.py tools/audit_topk_complex_family_20260604.py`
- 新規4件のテンプレート一致確認。
- 新規4件の内部スモーク:
  - `LL-bp4-001`
  - `PL!-bp6-006`
  - `PL!N-bp5-029`
  - `PL!SP-bp5-009`

## デバッグメモ

- 追加分のデバッグコマンドは `docs/debug/loveca_debug_commands_current_updates_20260623.md` に追記した。
- 統合ファイル `docs/debug/loveca_debug_commands_20260623.md` は今回触っていない。次回の「デバッグ対応」で統合する。

## 注意

- 今回、ファイル移動・削除・バックアップ作成は行っていない。
- `llocg_fetch_all_card_images.py`、`llocg_ui/views.py`、root 直下の未追跡 handoff/spec 系ファイルは触っていない。
