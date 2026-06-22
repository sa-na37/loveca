# Loveca 引き継ぎメモ 2026-06-22c

## 今回の前提
- ユーザー確認により `loveca_generic_area_group_icon_gain_20260622b.zip` は問題なし。
- 今回は `20260622b` を通過版として継続。
- `20260622a` は引き続き未適用・不採用。

## 再確認した方針
- 特定カード番号・単一カード文専用の分岐を増やさない。
- 既存の generic rule / ext rule が、DB 側の表記差だけで不発になっている場合は、まず matcher 側の共通正規化で直す。
- 新規カード専用 parser より、既存実装済みルートを正しく拾う修正を優先する。
- チャット長が伸びる前に必ず引き継ぎファイルを出す。

## 今回の修正
### 対象ファイル
- `llocg_ui/effects/registry.py`

### BUILD_TAG
- `effect_registry_icon_normalize_20260622c`

### 実装内容
`effects.registry._norm_ws()` を拡張し、拡張 effect matcher 内で以下の公式風アイコン表記を runtime 側表記と同等に扱うようにした。

```text
<桃> <赤> <黄> <緑> <青> <紫> <任意> <ALL> <E> <ブレード>
```

例:

```text
<桃>  -> <(桃)>
<緑>  -> <(緑)>
<ALL> -> <(ALL)>
```

`<ライブ開始時>` などの能力タグは対象外。

## この修正で拾えるようになる既存 generic/ext 実装
新しいカード専用 rule は追加していない。既存 rule が表記差で不発だったものが通る。

確認した改善例:
- `PL!-bp4-013` 園田海未
  - `ライブ終了時まで、自分のステージにいるこのメンバー以外のメンバー1人は、<桃>を得る。`
  - 既存 `live_start_pick_stage_member_temp_bonus` へ接続。
- `PL!-sd1-003` 南ことり
  - `<桃>か<黄>か<紫>のうち、1つを選ぶ。...`
  - 既存 `live_start_choose_heart` へ接続。
- `PL!-bp3-009` 矢澤にこ
  - 起動効果の同型 heart choice が既存 `live_start_choose_heart` へ接続。
- `PL!HS-bp2-007` 百生吟子
  - `<緑><(ブレード)>` の混在表記が既存 `live_start_discarded_member_same_name_stage_member_temp_bonus` へ接続。
- `PL!N-bp3-008` エマ・ヴェルデ
  - `<緑>` 表記が既存 `live_start_activate_wait_member_and_both_temp_bonus` へ接続。
- `PL!-PR-003` / `PL!-PR-004`
  - 必要ハート `<黄>` / `<桃>` 参照の控え室回収が既存 rule へ接続。

## 確認済み
- 構文確認:

```bash
python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

- matcher 確認:
  - `PL!-bp4-013` 相当テキストが `live_start_pick_stage_member_temp_bonus` に一致。
  - `PL!-sd1-003` 相当テキストが `live_start_choose_heart` に一致。
  - `PL!HS-bp2-007` 相当テキストが `live_start_discarded_member_same_name_stage_member_temp_bonus` に一致。
- 簡易 apply スモーク:
  - `PL!-bp4-013` を L、別メンバーを C に置いた状態で、C に `pink:1` が付与されることを確認。

## 重要な注意
- `engine.py` は今回変更していない。
- `server.py` は今回変更していない。
- `PL!-bp5-023` の required heart reduction は今回も触っていない。
- 今回の修正は「表記ゆれで既存 generic/ext 実装が不発になる問題」の共通修正。

## 次に進む候補
1. `live_start_pick_stage_member_temp_bonus` / `live_start_apply_stage_temp_bonus` の既存 rule に乗せられる類似文を、正規表現または汎用 rule 化する。
2. 具体候補:
   - `自分のステージにいる『X』のメンバー1人は、<色/ブレード>を得る。`
   - `このメンバー以外の『X』のメンバー1人は、<色/ブレード>を得る。`
   - `コストN以上の『X』のメンバー1人は、<色/ブレード>を得る。`
3. `PL!-bp5-023` 系へ戻る場合は、単一カード文型ではなく「ステージ上のハート条件に応じた required heart delta」汎用設計として扱う。
