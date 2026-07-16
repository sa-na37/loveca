# Loveca DB manual corrections 20260715

ローカルDB正本へ手動補正した内容の監査メモ。
wiki再取得や compiled 再生成を行う場合、このメモの補正を再確認する。

## PL!N-bp3-007 優木せつ菜

- 補正対象: `llocg_db_out_full/cards_min_tokv1.csv`, `llocg_db_out_full/cards_min_tokv1.json`, `llocg_db_out_full/cards_compiled_v7h.json`
- 補正内容: 効果対象を「優木せつ菜以外」ではなく「優木せつ菜」のメンバーカードとして扱う。
- 理由: ユーザーによるカード画像/wiki直接確認で「以外」が誤りと確認済み。wiki側へ修正依頼済み。
- runtime 対応: 指定名一致の `hand_member_cost_le_named_to_former_area_then_energy_under` 汎用 route を使用。

## PL!SP-pb2-008 若菜四季

- 補正対象: `llocg_db_out_full/cards_min_tokv1.csv`, `llocg_db_out_full/cards_min_tokv1.json`, `llocg_db_out_full/cards_compiled_v7h.json`
- 補正内容: トリガーを `<ライブ開始時>` から `<ライブ成功時>` へ変更。
- 理由: ユーザーによるwiki/カード画像確認で、実際にはライブ成功時効果であることを確認済み。
- runtime 対応:
  - エール時自動効果収集が `<ライブ成功時>` 能力を拾わないよう共通ガードを追加。
  - ライブ成功時 resolver に「エール公開のブレードハートなし指定グループメンバーN枚につきライブ合計スコア+M、上限K」を追加。
- 補正済み marker: `manual_override_applied=1`, `manual_override_reason=20260715 local manual correction...`
