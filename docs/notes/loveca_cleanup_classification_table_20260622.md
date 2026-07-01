# Loveca 整理対象分類表 — 現行リポジトリ更新版

作成日: 2026-06-22
更新日: 2026-06-23
目的: コード変更へ入る前に、現行リポジトリの実装済み route、未整理 family、旧 special / 専用寄り経路、Git 上の未整理ファイルを分類する。

このファイルは分類表であり、runtime 実装の正本ではない。
コード変更は、ここで候補を確認してから別タスクとして開始する。
2026-06-22 の整理では、不要または重複と判断したローカル生成物を `jank/cleanup_20260622/` に退避した。

---

## 0. 今回の調査基準

読んだ作業ルール:

- `AGENTS.md`

確認した主な runtime:

- `llocg_ui/engine.py`
- `llocg_ui/server.py`
- `llocg_ui/engine_effect.py`
- `llocg_ui/effects/registry.py`
- `llocg_ui/effects/live_start.py`
- `llocg_ui/effects/success_zone.py`
- `llocg_ui/effects/helpers.py`
- `llocg_ui/effects/apply.py`
- `llocg_ui/effects/topdeck.py`
- `llocg_ui/effects/green_search.py`
- `llocg_ui/effects/stage_triggers.py`
- `llocg_ui/effects/position.py`
- `llocg_ui/effects/energy.py`
- `llocg_ui/effects/special.py`

確認した主な資料:

- `docs/handoffs/loveca_handoff_20260622e.md`
- `docs/handoffs/loveca_handoff_20260622g.md`
- `loveca_reports/*.md`

現在の Git 状態メモ:

- ブランチ: `backup/before_db_update_20260527`
- 既存または今回発生した未コミット変更:
  - `llocg_ui/engine.py`（既存差分あり。20260622h で Dazzling Game 型の色変換汎用化を追加）
  - `llocg_fetch_all_card_images.py`（整理開始前からの既存差分。今回未編集）
  - `.gitignore`（生成キャッシュと zip の ignore 追加）
  - `README.md`（現行 runtime / DB 正本に合わせて更新）
- 未追跡の整理/監査/メモ類:
  - `AGENTS.md`
  - `docs/notes/loveca_cleanup_classification_table_20260622.md`
  - `docs/handoffs/loveca_handoff_20260622*.md` の一部
  - `loveca_reports/*`
  - `tools/audit_*.py` の一部
- 退避済み:
  - `jank/cleanup_20260622/.cache_llocg_image_manifest_clhs01_20260603`
  - `jank/cleanup_20260622/.cache_llocg_image_manifest_pbhs_20260603`
  - `jank/cleanup_20260622/.cache_llocg_update_20260527`
  - `jank/cleanup_20260622/cards_compiled_v7h.json`
  - `jank/cleanup_20260622/cards_min_tokv1.json`
  - `jank/cleanup_20260622/handoff_archive/loveca_handoff_20260622b.md`
  - `jank/cleanup_20260622/handoff_archive/loveca_handoff_20260622d.md`
  - `jank/cleanup_20260622/handoff_archive/loveca_handoff_20260622e.md`
  - `jank/cleanup_20260622/superseded_audits/loveca_excess_success_remaining_family_audit_20260608b.csv`
  - `jank/cleanup_20260622/superseded_audits/loveca_excess_success_remaining_family_audit_20260608b.md`
  - `jank/cleanup_20260622/superseded_audits/loveca_excess_success_score_family_audit_20260605b.csv`
  - `jank/cleanup_20260622/superseded_audits/loveca_excess_success_score_family_audit_20260605b.md`
  - `jank/cleanup_20260622/superseded_audits/audit_excess_success_score_family_20260605.py`
  - `jank/cleanup_20260622/ignored_artifacts/`（root / `llocg_ui` / `tools` などの `.DS_Store`, `__pycache__`）
- `.gitignore` 更新:
  - `/.cache_llocg_image_manifest_*/`
  - `/.cache_llocg_update_*/`
  - `*.zip`
- 退避先容量:
  - `jank/cleanup_20260622/`: 約141MB
  - 追跡済み旧キャッシュ `.cache_llocg/`, `.cache_llocg_bak_20260327/`: 合計約117MB（今回は未移動）

注意:

- 既存 diff は空ではない。整理開始前から画像取得スクリプトに差分がある。
- `engine.py` は既存差分に加えて、20260622h の色変換汎用化、20260622i の top-k 複数枚選択、20260622j の top-k 句読点差/単純mill、20260622k のコスト条件つきグループメンバーtop-k、20260623a の top-k 表記ゆれ/top1 optional mill、20260623b の top-k mill 条件つき後続処理、20260623c の top-k mill後回収 / 全戻し並べ替え / 条件つき任意mill、20260623d のライブ公開まで山札上公開、20260623e の top-k 文末句点なし表記 / group-or-unit 候補判定を追加済み。
- `README.md` の最新 handoff 参照は `docs/handoffs/loveca_handoff_20260625b.md` に更新済み。
- 実装分の統合デバッグメモは `docs/debug/loveca_debug_commands_20260623.md`。
- ユーザーとの同時編集を避けるため、現行実装分の新規デバッグコマンドは `docs/debug/loveca_debug_commands_current_updates_20260623.md` に追記し、ユーザー指定タイミングで統合メモへ移す。
- root 直下の作業メモ `.md` は `docs/` 配下へ移動済み。root に残す Markdown は `README.md` と `AGENTS.md` のみ。
- `loveca_reports` には古い `needs_*` と後続の `implemented_*` が混在する。より新しい監査ファイルと直近 handoff を優先する。

---

## 1. 現行正本の分類

| 区分 | パス | 現状分類 | メモ |
|---|---|---|---|
| runtime 正本 | `llocg_ui/` | 残す / 実装対象 | AGENTS.md 上の正本。効果実装は `effects/` に寄せる |
| UI / state 正本 | `llocg_ui/server.py` | 残す / 要回帰 | pending 表示、カード選択 UI、state_json の正本 |
| engine 正本 | `llocg_ui/engine.py` | 残す / 要慎重 | 巨大ファイル。既存差分あり。特殊経路も多く、変更前に BUILD_TAG と該当関数確認必須 |
| effect facade | `llocg_ui/engine_effect.py` | 残す | 入口のみ。肥大化させない |
| effect 分割先 | `llocg_ui/effects/` | 残す / 主作業場所 | `registry.py` で match、`apply.py` から意味単位 resolver へ dispatch |
| DB 正本 | `llocg_db_out_full/cards_compiled_v7h.json` | 残す | runtime 参照時の compiled 正本 |
| DB 正本 | `llocg_db_out_full/cards_min_tokv1.json` / `.csv` | 残す | stat / icon の正本 |
| root 直下 DB copy | `cards_compiled_v7h.json`, `cards_min_tokv1.json` | 退避済み | 正本 `llocg_db_out_full/` と SHA-256 が一致することを確認し、`jank/cleanup_20260622/` に移動済み |
| 監査スクリプト | `tools/audit_*.py` | Git 管理候補 | family 棚卸しに有用。未追跡が多い |
| 監査レポート | `loveca_reports/*.md`, `.csv` | Git 管理候補 / 一部退避済み | 新旧混在。`excess_success_remaining_20260608b` と `excess_success_score_20260605b` は `20260608c` に吸収済みとして退避 |
| 引き継ぎメモ | `docs/handoffs/loveca_handoff_*.md` | docs 配下に集約済み / 一部退避済み | root 直下には残さない。未追跡だった `b/d/e` は `jank/cleanup_20260622/handoff_archive/` に移動済み |
| キャッシュ | `.cache_llocg_image_manifest_*`, `.cache_llocg_update_20260527` | 退避済み / ignore 済み | `jank/cleanup_20260622/` に移動済み。容量が大きく、通常は正本ではない |
| 追跡済み旧キャッシュ | `.cache_llocg/`, `.cache_llocg_bak_20260327/` | 触らない / 要別判断 | Git 追跡済みで合計約117MB。整理するなら大量削除/履歴方針が絡むため別タスク |
| ignored 一時生成物 | `.DS_Store`, `__pycache__/` | 退避済み | `.venv/` は触らず、root / runtime / tools 配下のみ `jank/cleanup_20260622/ignored_artifacts/` に退避 |
| 古い実験/退避 | `jank/` | 退避先 | 追加退避時は日付つきサブフォルダを作る |
| ZIP | `llocg_ui.zip` | ignore 済み / 見つからず | 旧配布物の可能性。正本扱いしない |

---

## 1.1 残す Git 管理候補

未追跡だが、現行調査・今後の実装判断に有用なため Git 管理候補。

| 区分 | 候補 | 理由 |
|---|---|---|
| 作業ルール | `AGENTS.md` | このリポジトリの作業ルール正本 |
| 整理表 | `docs/notes/loveca_cleanup_classification_table_20260622.md` | 現行分類と退避記録 |
| 最新引き継ぎ | `docs/handoffs/loveca_handoff_20260625b.md` | 最新変更の短い handoff |
| DB更新メモ | `docs/notes/loveca_db_update_process_memo_20260527.md` | DB 更新手順の作業メモ |
| デバッグ統合メモ | `docs/debug/loveca_debug_commands_20260623.md` | ユーザー編集・確認コメント・最終統合用 |
| デバッグ現行更新 | `docs/debug/loveca_debug_commands_current_updates_20260623.md` | 実装中に追加する個別デバッグ起動コマンド。指定タイミングで統合メモへ移す |
| DB整合性確認 | `check_loveca_db_integrity_20260527.py` | DB 更新後の検査ツール |
| 監査レポート | `loveca_reports/loveca_deck_bottom_family_audit_20260604a.*` | deck-bottom family 全体棚卸し |
| 監査レポート | `loveca_reports/loveca_live_storage_topbottom_family_audit_20260605a.*` | live storage top/bottom family |
| 監査レポート | `loveca_reports/loveca_mass_green_bottom_family_audit_20260605a.*` | mass green-bottom family |
| 監査レポート | `loveca_reports/loveca_stage_leave_basic_auto_family_audit_20260610f.*` | stage leave basic family |
| 監査レポート | `loveca_reports/loveca_stage_leave_optional_discard_baton_family_audit_20260610h.*` | stage leave optional-discard / baton family 最新寄り |
| 監査レポート | `loveca_reports/loveca_success_count_cost_misc_family_audit_20260610c.*` | success count / cost misc family |
| 監査レポート | `loveca_reports/loveca_success_score_body_and_activate_condition_audit_20260610a.*` | success score BODY / activated condition |
| 監査レポート | `loveca_reports/loveca_success_storage_count_score_family_audit_20260608d.*` | success storage count score family |
| 監査レポート | `loveca_reports/loveca_success_storage_score_sum_family_audit_20260608g.*` | success storage score-sum family |
| 監査レポート | `loveca_reports/loveca_yell_revealed_family_audit_20260604a.*` | yell revealed family 残件抽出 |
| 監査スクリプト | `tools/audit_deck_bottom_family_20260604.py` | 上記レポート生成元 |
| 監査スクリプト | `tools/audit_live_storage_topbottom_family_20260605.py` | 上記レポート生成元 |
| 監査スクリプト | `tools/audit_mass_green_bottom_family_20260605.py` | 上記レポート生成元 |
| 監査スクリプト | `tools/audit_stage_leave_basic_auto_family_20260610.py` | 上記レポート生成元 |
| 監査スクリプト | `tools/audit_stage_leave_optional_discard_baton_family_20260610.py` | 上記レポート生成元 |
| 監査スクリプト | `tools/audit_success_count_cost_misc_family_20260610.py` | 上記レポート生成元 |
| 監査スクリプト | `tools/audit_success_score_body_and_activate_condition_20260610.py` | 上記レポート生成元 |
| 監査スクリプト | `tools/audit_success_storage_count_score_family_20260608.py` | 上記レポート生成元 |
| 監査スクリプト | `tools/audit_success_storage_score_sum_family_20260608.py` | 上記レポート生成元 |
| 監査スクリプト | `tools/audit_yell_family_20260604.py` | 上記レポート生成元 |

確認:

- `python3 -m py_compile tools/*.py` 通過。
- 未追跡の監査物は、各 family ごとに `.md` / `.csv` / `tools/audit_*.py` が揃っていることを確認済み。孤立ファイルは見当たらないため退避しない。

---

## 2. ファミリー別整理表

| 優先度 | ファミリー | 監査上の件数 | 現行分類 | 主な既存 route / state | 想定される実装単位 | 最初に見るファイル | 代表カード / 例 | 判定メモ |
|---:|---|---:|---|---|---|---|---|---|
| A | 条件付き stage member temp bonus | 7 前後 | 直近で generic 化済み / 回帰確認候補 | `generic_conditional_stage_member_temp_bonus`, `live_start_pick_stage_member_temp_bonus` | 条件 fragment 追加、target predicate 追加 | `effects/registry.py`, `effects/live_start.py`, `effects/helpers.py` | `PL!S-bp2-025`, `PL!HS-pb1-025`, `PL!-bp4-014` | 20260622g で実装済み。複雑な `ハートを持つメンバー` predicate は未対応 |
| A | エールで公開されたカード・色・枚数を参照 | 既実装37 / 残件は要再監査 | かなり実装済み / 20260622h で色変換を追加汎用化 | `current_yell_revealed`, `retrieve_from_yell`, `put_yell_to_deck_top/bottom`, live-success score helpers, `yell_heart_convert_target_color_this_live` | yell replacement / extra yell / score comparison / conversion の分離 | `engine.py`, `server.py`, `effects/helpers.py` | `PL!S-bp2-004`, `PL!S-bp3-020`, `PL!HS-bp6-027`, `PL!SP-bp4-023` | 現行 `engine.py` では追加エール系の一部も実装済み。古い audit の `needs_implementation` は再監査が必要 |
| A | topk / デッキ上公開 / filtered pick | 146 | 多数実装済み / 未監査17 | `_rule_look_top_choose_filtered`, `topk_filtered_optional_pick`, `reorder_from_topk`, `choose_from_topk`, `look_top_choose_n`, `mill_top_to_green`, `self_top1_optional_green`, `mill_top_conditional_followup`, `mill_top_then_retrieve_from_waiting`, `look_top_reorder_all`, `stage_group_optional_mill_top_k`, `optional_discard_one_from_hand_then_effect_direct`, `reveal_until_match_to_hand_rest_waiting`, `topdeck_from_green`, `look_top_k_optional_distinct_group_upto_n`, `look_top_k_optional_cost_le_group_member_stage_or_hand`, `live_start_my_cost_lower_draw2_hand_top1`, `mill_top_then_waiting_live_to_deck_nth_optional`, `live_success_reveal_top_no_bladeheart_score`, `live_start_hand_group_to_deck_top_or_bottom_blade`, `reveal_top1_cost_le_member_hand_then_self_position_change`, `live_success_excess_total_top_reorder_keep_any`, `look_top_stage_member_count_plus_keep_one_top_rest_waiting` | 未監査 topk の文型分類、既存 filtered pick の pattern 追加 | `engine.py`, `effects/topdeck.py`, `server.py`, `effects/live_start.py` | `PL!-bp5-014`, `PL!S-bp2-005`, `PL!S-bp5-007`, `PL!S-pb1-013/014/015`, `LL-bp6-001`, `PL!HS-cl1-001/004/007`, `PL!HS-bp5-008`, `PL!-sd1-007`, `PL!HS-bp1-008`, `PL!HS-bp5-001/013`, `PL!HS-bp6-009`, `PL!-bp5-010`, `PL!HS-pb1-004/027`, `PL!N-bp1-009`, `PL!-bp6-016`, `PL!-pb1-016`, `PL!N-bp1-011`, `PL!SP-pb1-017`, `PL!-bp6-002`, `PL!S-bp6-005`, `PL!SP-bp5-007`, `PL!SP-pb2-001`, `PL!N-bp4-009`, `PL!N-bp5-021`, `PL!N-pb1-004`, `PL!HS-bp6-028`, `PL!HS-bp6-001`, `PL!-bp6-007`, `PL!S-sd1-009`, `PL!SP-bp5-013`, `PL!N-bp4-021` | 20260622i で topK から N 枚手札、20260622j で句読点差の1枚手札と単純mill、20260622k でコスト条件つきグループメンバーtop-k、20260623a で表記ゆれとtop1 optional mill、20260623b でmill条件つき後続処理、20260623c でmill後回収 / 全戻し並べ替え / 条件つき任意mill / 直接任意手札コスト文型、20260623d でライブ公開まで山札上公開、20260623e で文末句点なし variant と unit label filtered pick、20260623g で能力なし/常時、全色ハート、ブレードハート持ちグループ、控え室任意topdeck文型、20260623i でハート色いずれかを持つメンバーを上限枚数まで選ぶ top-k、20260623l で各グループ名につき1枚ずつ最大N枚選ぶ top-k、20260624a でコスト以下グループメンバーを空きステージまたは手札へ送る top-k、20260624b でステージコスト比較後の2ドロー＋手札デッキ上、20260624c で2枚mill後ライブカードをデッキ上から4枚目に置く route、20260625a/25b でトップ公開コスト条件＋ポジションチェンジ route、余剰ハート条件top reorderの監査反映、ステージ人数参照top keep-one routeを追加。20260623k で `<常時>` 判定の BODY 起動能力誤判定と並べ替え UI のカード上ドロップ位置を修正。既存 UI が使えるものを優先 |
| A | stage→green / leave-stage optional discard / baton | 11 → 4 | 後続監査で実装済み寄り | `optional_discard_one_from_hand_then_effect`, `leave_baton_no_bladeheart_nijigasaki_energy_draw`, stage leave triggers | 回帰確認、旧 deferred 表記の更新 | `engine.py`, `effects/stage_triggers.py`, `effects/topdeck.py` | `PL!HS-bp6-017/018`, `PL!N-bp5-005`, `PL!S-bp2-002` | 20260610h では4件すべて実装済み。古い 20260610f の deferred は更新済み扱い |
| B | 成功ライブ置き場の枚数 / スコア合計 | 12 / 16 / 5 | 一部 generic 化済み / BODY 常時は残件 | `success_zone_score_threshold_action`, `_success_zone_score_sum`, `zone_count_temp_bonus` | success predicate helper の整理、BODY 常時条件の route 化 | `engine.py`, `effects/success_zone.py`, `effects/live_start.py` | `PL!-bp3-024`, `PL!S-bp6-020`, `PL!SP-sd2-023` | 20260622g で count 条件 wrapper の一部は吸収。BODY always / activated condition は慎重に分類 |
| B | デッキ上 / 下へ移動、top/bottom choice | 16 / 3 / 5 | 多く実装済み / replacement event が残る | `topdeck_from_green`, `bottomdeck_from_green`, `choose_player_deck_top_action`, live storage cleanup | event trigger と選択 UI の確認 | `engine.py`, `server.py`, `effects/topdeck.py` | `PL!S-bp6-002`, `PL!S-bp6-019`, `PL!S-sd1-009` | `PL!S-bp6-002` は live storage cleanup が実装済み報告あり。古い needs は要再監査 |
| B | エネルギーを active / wait で置く・参照 | 51 | 既存 route 多い / clamp 回帰候補 | `energy_put_active`, `energy_put_wait`, `energy_activate`, `_put_wait_energy_from_deck` | 文型追加より回帰テスト優先 | `engine.py`, `effects/energy.py`, `effects/success_zone.py` | `ド！ド！ド！`, `La Bella Patria` | active 置き route は `engine.py` に追加済み。上限 clamp と debug 初期値に注意 |
| B | 控え室検索 / multi-pick / group kind filter | 多数 | 既存 generic が充実 | `green_pick_filtered_to_hand`, `_green_room_filtered_cards`, `choose_card_from_green` | pattern / gd 追加で拾える可能性大 | `effects/green_search.py`, `effects/helpers.py`, `server.py` | μ's / 蓮ノ空 / みらくらぱーく！検索系 | 新規 UI は不要なものが多い。最初の実装候補として扱いやすい |
| B | excess heart / live success score-set | 9 | 20260608c では全件実装済み扱い | excess / score-set helpers in `engine.py` | 古い監査結果の更新、回帰確認 | `engine.py`, `loveca_reports/*excess*` | `MIRACLE WAVE`, `Landing action Yeah!!`, `ブルウモーメント` | 20260605b は古い。20260608c を優先 |
| C | エネルギーをメンバーの下に置く / 下のカード参照 | 2〜5 | 新規 state / UI 必要で重い | `StageSlot` under-energy 系の有無確認 | state追加 → 表示 → 離脱時処理 → 参照 | `engine.py`, `server.py`, `effects/energy.py` | ミア・テイラー, 鐘嵐珠 | 最初に着手しない。分類とルール確認を先行 |
| C | ポジションチェンジ / 移動済み参照 | 12 | 一部実装済み / movement flag は要確認 | `position_change`, `live_start_mus_only_pick_member_position_change` | movement_log の有無整理 | `effects/position.py`, `engine.py`, `server.py` | `Love wing bell`, `LL-bp5-001` | 「このターン移動している場合」は新規/既存 flag 確認が必要 |
| C | ライブできない / 開始不能化 | 2 | 一部実装済み / 回帰向き | `cannot_live_until_end_of_live` 系 | UI disabled state の回帰 | `engine.py`, `server.py`, `effects/stage_triggers.py` | `PL!HS-bp2-014` | 件数少。大きな整理より回帰テスト向き |
| C | old special / 専用寄り ext_key 整理 | 多数 | すぐ削除しない | `effects/special.py`, card-name comments, prompt-specific ext_key | generic 置換できるものだけ段階移行 | `effects/registry.py`, `effects/special.py`, `engine.py` | `enter_main_pay2_faceup_live_to_set_reduce_next_live_set` など | コメントにカード番号があるだけなら問題ではない。条件分岐が専用化している箇所だけ確認 |

---

## 3. 個別カード別整理表

| 優先度 | カード番号 | カード名 | 種別 | トリガー | 効果要約 | family | 現在の経路 | 実装状態 | 既存 generic に載るか | 必要な新規 state | 必要な UI | 想定変更ファイル | デバッグ難度 | 代表デバッグ条件 | 備考 |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | PL!S-bp2-025 | 青空Jumping Heart | LIVE | ライブ開始時 | 成功置き場条件で stage member temp bonus | conditional stage bonus | `generic_conditional_stage_member_temp_bonus` | 実装済み / 要回帰 | yes | なし | stage member choice | なし | 中 | success 1〜2枚、対象 stage member | 20260622g 代表 |
| A | PL!HS-pb1-025 | 抱きしめる花びら | LIVE | ライブ開始時 | ライブ中カード条件で stage member temp bonus | conditional stage bonus | `live_start_pick_stage_member_temp_bonus` | 実装済み / 要回帰 | yes | なし | stage member choice | なし | 中 | set_zone に条件カード | 20260622g で `set_zone` 参照対応 |
| A | PL!HS-bp6-027 | 月夜見海月 | MEMBER | 自分がエールした時 | no blade-heart 蓮ノ空カードを控え室へ置き、枚数分追加エール | yell revealed replacement / extra yell | unknown / `engine.py` yell 周辺 | 未実装候補 | 要調査 | current_yell_revealed の消費、extra_yell queue | multi-select / confirm | `engine.py`, `server.py` | 高 | yell 公開カードに条件カードを複数 | 重い。最初の実装には不向き |
| A | PL!S-bp2-004 | 黒澤ダイヤ | MEMBER | エール公開時 | LIVE がない場合、公開カードを控え室へ置いて再エール | yell replacement / extra yell | unknown / `engine.py` yell 周辺 | 未実装候補 | no | current_yell_revealed 消費、blade-heart loss | confirm | `engine.py`, `server.py` | 高 | LIVE なし yell 公開 | 同型に `PL!S-bp3-020` |
| A | PL!S-bp3-020 | ダイスキだったらダイジョウブ！ | LIVE | エール公開時 | blade-heart 2枚以下なら公開カードを控え室へ置き再エール | yell replacement / extra yell | unknown / `engine.py` yell 周辺 | 未実装候補 | no | current_yell_revealed 消費、blade-heart loss | confirm | `engine.py`, `server.py` | 高 | blade-heart 0〜2枚公開 | 黒澤ダイヤと family 化候補 |
| A | PL!SP-bp4-023 | Dazzling Game | LIVE | ライブ開始時 | エール公開カードの特定色を紫扱いに変換 | yell color conversion | `live_start_convert_revealed_colors_to_single_color_until_end_of_live` | 実装済み / 要UI実地確認 | yes | `yell_heart_convert_target_color_this_live` | なし | `engine.py` | 中 | yell 色変換対象を公開 | 20260622h で VIVID WORLD 型 route を青/紫など任意 target 色に汎用化 |
| A | PL!SP-pb2-008 | 若菜四季 | MEMBER | エール参照 | no blade-heart Liella! member 2枚につき live score +1、上限2 | yell revealed score bonus | unknown | 未実装候補 | yes? | current_yell_revealed | なし | `engine.py` | 中 | 条件 member 2/4枚公開 | score bonus helper に載せられる可能性 |
| B | PL!S-bp6-002 | 桜内梨子 | MEMBER | BODY / live storage event | Aqours live が live storage から控え室へ置かれた時 top/bottom | live storage cleanup | live storage cleanup route | 実装済み扱い / 要再監査 | yes | event source tracking | top/bottom choice | なし / 回帰 | 高 | live storage から対象 live が控え室へ | 古い report では needs、新しい report では implemented |
| B | PL!HS-bp6-017 | 日野下花帆 | MEMBER | stage leave | optional discard → live/member retrieve | leave optional discard | `optional_discard_one_from_hand_then_effect` | 実装済み | yes | なし | discard + green pick | なし / 回帰 | 中 | stage→green と手札1枚 | 20260610h で implemented |
| B | PL!HS-bp6-018 | 村野さやか | MEMBER | stage leave | optional discard → stage member gains 青+blade | leave optional discard | `optional_discard_one_from_hand_then_effect` + temp bonus | 実装済み | yes | なし | discard + stage choice | なし / 回帰 | 中 | stage→green と対象 member | 20260610h で implemented |
| B | PL!N-bp5-005 | 宮下愛 | MEMBER | stage leave | baton 条件で energy activate / draw | leave baton | `leave_baton_no_bladeheart_nijigasaki_energy_draw` | 実装済み | yes | baton last info | confirm? | なし / 回帰 | 高 | baton で stage leave | 発生源/最終情報に注意 |
| B | PL!S-bp6-019 | Step! ZERO to ONE | LIVE | ライブ開始時 | stage all Aqours → score + draw → hand top/bottom | top/bottom choice | `score_draw_then_hand_top_or_bottom_if_all_stage_group` | 実装済み | yes | なし | hand top/bottom choice | なし / 回帰 | 中 | stage all Aqours、手札1枚以上 | 20260605a implemented |
| B | PL!HS-bp6-031 | ファンファーレ！！！ | LIVE | ライブ開始時 | 控え室 member 全戻し、枚数条件で named stage blade | mass green bottom | `bottom_all_green_members_optional_group_threshold_stage_named_blade` | 実装済み | yes | opponent なし | confirm / deck bottom | なし / 回帰 | 中 | green に member 15枚以上 | 20260605a implemented |
| C | LL-bp5-001 | Live with a smile! | LIVE | ライブ成功時 | LIVE 公開数 / stage heart 種類 / movement の複合条件 | yell + stage + movement | unknown | 未実装候補 / 重い | no | movement_log | なし | `engine.py`, `effects/helpers.py` | 高 | 複合条件を個別に作る | movement flag が先 |
| C | PL!SP-bp2-010 | ウィーン・マルガレーテ | MEMBER | ライブ開始時 | エール公開枚数を8枚減らす | yell count modifier | unknown | 未実装候補 / 重い | no | live-until-end yell count modifier | なし | `engine.py` | 高 | stage に他 member あり | yell枚数計算に影響 |
| C | ミア・テイラー系 |  | MEMBER | 各種 | エネルギーをメンバーの下に置く / 参照 | attached energy | 要調査 | 後回し | no | attached_energy | stage overlay / state | `engine.py`, `server.py` | 高 | under energy 初期状態 | 新規 state が必要 |

---

## 4. 既存 route に載せられるもの / 新規 state が必要なもの / UI が必要なもの

### 既存 route に載せられる可能性が高い

| 候補 | 既存 route | 変更候補 | メモ |
|---|---|---|---|
| 条件付き stage member temp bonus の追加文型 | `live_start_pick_stage_member_temp_bonus` | `effects/registry.py`, `effects/live_start.py` | 条件 fragment / target predicate 追加で済むなら小さい |
| 控え室 filtered pick 系 | `green_pick_filtered_to_hand` | `effects/registry.py`, `effects/green_search.py` | `gd` 追加中心で済む可能性 |
| topk filtered optional pick の追加文型 | `look_top_choose_filtered`, `topk_filtered_optional_pick` | `engine.py`, `effects/topdeck.py` | UI は既存の左右分割が使える |
| success score/count 条件の単純 wrapper | `success_zone_score_threshold_action`, `zone_count_temp_bonus` | `effects/success_zone.py`, `effects/registry.py` | BODY 常時は別扱い |
| VIVID WORLD 型の色変換 | 既存 yell conversion helper 要確認 | `engine.py` | Dazzling Game が色違いなら小さめ |

### 新規 state が必要な可能性が高い

| 候補 | 必要 state | 理由 |
|---|---|---|
| 追加エール / 公開カードを控え室へ移す | current yell revealed の消費済み管理、extra yell queue、blade-heart loss | 公開カード列を参照するだけでは足りない |
| エール公開枚数を減らす | live-until-end yell count modifier | yell 枚数計算そのものに影響 |
| メンバー下エネルギー | attached_energy / under cards | 通常エネルギー置き場と別管理 |
| movement 条件 | movement_log / moved_this_turn | `LL-bp5-001` などの条件判定に必要 |
| live storage replacement event | event source / moved live card | 既に実装済み報告あり。削除・改修前に state を確認 |

### UI が必要 / 既存 UI の回帰が必要

| 候補 | UI | メモ |
|---|---|---|
| topk choose / filtered pick | 既存 `choose_from_topk`, 左右分割 UI | 既存 UI で足りることが多い |
| hand top/bottom choice | 既存 hand → top/bottom UI | top/bottom choice の回帰確認 |
| optional discard follow-up | discard pending + follow-up pending | pending 表示は実行中効果だけにする |
| extra yell replacement | confirm + revealed card multi-select | 新規/拡張 UI が必要そう |
| attached energy | stage 表示 / カード下表示 | 新規 UI が必要 |

---

## 5. 既存 special / 旧経路整理表

| 種別 | 識別子 | 所在ファイル | 現在の用途 | 置換先候補 | 削除可否 | 削除前に必要な回帰 | 備考 |
|---|---|---|---|---|---|---|---|
| special ext | `enter_main_pay2_faceup_live_to_set_reduce_next_live_set` | `effects/special.py` | 控え室 LIVE を set_zone へ置き、次 live set cost 減 | green/search + set-zone cost modifier helper | 要調査 | 対象カードの登場処理、LIVE 選択、次 live cost | まだ一般化しきれていない例外として残す |
| prompt-specific ext | `live_start_no_mus_blade5_force_not_center` | `effects/position.py` | μ's なし条件で center 以外へ強制移動 + blade | stage predicate + position helper | 要調査 | 候補 L/R 制限、強制/任意差 | 名前は専用寄り。文型化できるか確認 |
| prompt-specific ext | `live_start_mus_only_pick_member_position_change` | `effects/position.py` | μ's only 条件の position change | stage group predicate + position helper | 要調査 | 選択 member → position change | 同型が複数あるなら generic 化 |
| old engine route | `_EFFECT_RULES` 内の多数 op | `engine.py` | 汎用基本効果 | 維持 | no | 全体 smoke | 既に engine 正本。無理に effects へ移さない |
| cardnumber guard | `PL!SP-pb2-013` 登場 special | `engine.py` | 特定登場処理 | 文型/DB 条件 route | 要調査 | 対象カードの登場効果 | AGENTS 原則上は将来整理候補 |
| cardnumber correction | `PL!S-bp5-020` typo correction | `engine.py` | wiki typo の補正 | DB override / manual_overrides | 要調査 | Landing action Yeah!! | ルール/DB修正で置換できる可能性 |
| debug dummy guard | `PL!-bp5-111/222/333` | `engine.py` | debug / dummy 除外らしき処理 | 要確認 | 要調査 | 影響範囲確認 | 目的確認なしに削除しない |
| UI cardnumber hint | `server.py` 内 `PL!-bp4-020` 等 | `server.py` | UI 表示/補助判定 | state 側情報 | 要調査 | pending / label 表示 | 表示専用なら優先低 |

---

## 6. 最初に着手すべき小さな修正候補

### 完了: Dazzling Game 型のエール色変換を既存 VIVID WORLD route に載せる

- 対象: `PL!SP-bp4-023` Dazzling Game
- 状態: 20260622h で実装済み
- 内容: `live_start_convert_revealed_colors_to_single_color_until_end_of_live` を青専用から target 色汎用へ拡張
- 変更ファイル: `llocg_ui/engine.py`
- BUILD_TAG: `live_start_yell_color_convert_generic_20260622h`
- 残り: UI 実地操作での回帰確認

### 候補 2: topk 未監査41件のうち、既存 route で拾える文型を追加

- 対象: `loveca_topk_complex_family_audit_20260604a.md` の `needs_audit_unmatched_topk`
- 状態: 20260622i で `LL-bp6-001` 型の topK から N 枚手札、20260622j で句読点差の1枚手札と単純mill、20260622k でコスト条件つきグループメンバーtop-k、20260623a で表記ゆれとtop1 optional mill、20260623b でmill条件つき後続処理、20260623c でmill後回収 / 全戻し並べ替え / 条件つき任意mill / 直接任意手札コスト文型、20260623d でライブ公開まで山札上公開、20260623l で各グループ名につき1枚ずつ最大N枚選ぶ top-k、20260624a でコスト以下グループメンバーを空きステージまたは手札へ送る top-k、20260624b でステージコスト比較後の2ドロー＋手札デッキ上、20260624c で2枚mill後ライブカードをデッキ上から4枚目に置く route、20260625a/25b でトップ公開コスト条件＋ポジションチェンジ route、余剰ハート条件top reorderの監査反映、ステージ人数参照top keep-one routeを実装済み。残りの topk 未監査は17件
- 理由: 既存 UI と helper が揃っており、文型追加だけで複数カードを拾える可能性が高い
- 既存 route: `look_top_choose_filtered`, `topk_filtered_optional_pick`
- 変更候補: `engine.py`, `effects/registry.py`, `effects/topdeck.py`
- リスク: 監査対象が多いので、最初に同型2枚以上を抽出してから着手する

### 候補 3: success count conditional wrapper の後続確認

- 対象: `PL!-bp3-024`, `PL!S-bp6-020`, `PL!SP-sd2-023` など
- 理由: 20260622g の generic conditional stage bonus で一部吸収済みの可能性がある
- 既存 route: `generic_conditional_stage_member_temp_bonus`, `success_zone_score_threshold_action`
- 変更候補: まず監査レポート更新。コード変更はその後
- リスク: 古い report の `candidate_*` が既に実装済みになっている可能性がある

### 候補 4: old special / cardnumber guard の棚卸しだけ行う

- 対象: `effects/special.py`, `engine.py` の cardnumber guard
- 理由: 実装前に「本当に専用分岐か、コメントだけか」を分けると今後の事故が減る
- 変更候補: なし。まず report 作成
- リスク: すぐ削除しないこと

---

## 7. まだ実装しない候補

| 候補 | 理由 |
|---|---|
| 追加エール / 公開カードを控え室へ移す family | current_yell_revealed の消費、blade-heart loss、extra yell queue が絡む |
| エール公開枚数を減らす効果 | yell 枚数計算の根元に影響する |
| メンバー下エネルギー | 新規 state と UI が必要 |
| movement 条件を含む複合 LIVE | movement flag の整理が先 |
| `engine.py` の大規模分割 | 既存回帰範囲が大きい。AGENTS.md でも `effects/` へ新規実装を寄せる方針 |

---

## 8. 実装前のデバッグコマンド候補

ここでは方針だけを書く。実行可能な個別デバッグコマンドは `docs/debug/loveca_debug_commands_20260623.md` に集約する。

| 候補 | 初期配置 | 期待挙動 |
|---|---|---|
| Dazzling Game 色変換 | 対象 LIVE を手札、stage に条件 member、deck top に色持ちカード | ライブ中、指定色が紫扱いで yell / score 判定される |
| conditional stage bonus | success / green / set_zone 条件を満たす、stage に複数候補 | 候補選択後、選んだ member に heart/blade temp bonus |
| topk filtered pick | deck top に候補/非候補を混在 | 候補とその他が分かれて表示され、候補だけ選べる |
| optional discard stage leave | stage に対象、手札に discard 用、green に回収候補 | stage→green 後、discard confirm → follow-up |
| extra yell replacement | yell 公開列に条件カードだけを置く | 公開カードを控え室へ移し、追加 yell が発生 |

---

## 9. 次回 Codex への標準依頼文

```text
AGENTS.md と docs/notes/loveca_cleanup_classification_table_20260622.md を読んでください。

コード変更前に、対象 family の既存 route / matcher / resolver / helper を確認してください。
カード番号専用分岐は禁止です。

今回の対象は <family name> です。
まず同型カードを cards_compiled_v7h.json から複数抽出し、既存 generic route に載るか判定してください。
分類結果を出してから、実装に入ってください。
```

---

## 9.1 Git に載せる場合の推奨まとまり

まだ staging / commit はしていない。Git に載せる場合は、次のように分けるとレビューしやすい。

| まとまり | 対象 | 理由 |
|---|---|---|
| docs / cleanup | `.gitignore`, `README.md`, `AGENTS.md`, `docs/notes/loveca_cleanup_classification_table_20260622.md`, `docs/notes/loveca_db_update_process_memo_20260527.md`, `check_loveca_db_integrity_20260527.py` | 作業ルール、正本パス、ローカル生成物の扱いを先に固定する |
| implementation | `llocg_ui/engine.py`, `docs/handoffs/loveca_handoff_20260622h.md` | Dazzling Game 型のエール色変換汎用化と引き継ぎ |
| audits | `loveca_reports/loveca_*_family_audit_*.{md,csv}`, `tools/audit_*_family_*.py` | 今後の family 実装判断に使う監査資料一式 |

注意:

- `llocg_fetch_all_card_images.py` は整理開始前から差分があるため、今回の整理/実装コミットに混ぜない方がよい。
- `jank/cleanup_20260622/` は Git 無視対象。中に `MANIFEST.md` を置いたが、ローカル退避目録であり Git 管理候補ではない。
- `.cache_llocg/` と `.cache_llocg_bak_20260327/` は追跡済み旧キャッシュ。削除や Git 管理解除は別判断にする。

---

## 9.2 現時点の具体的な staging 案

まだ実行していない。実行するなら、既存差分の `llocg_fetch_all_card_images.py` を混ぜない。

確認:

- 下記 stage 対象ファイルはすべて存在確認済み。
- `git add -n` は `.git/index.lock` を作成できず失敗した。現セッションでは `.git` が read 権限中心のため、stage / commit には追加権限が必要。

### 1. docs / cleanup

```bash
git add .gitignore README.md AGENTS.md \
  docs/notes/loveca_cleanup_classification_table_20260622.md \
  docs/notes/loveca_db_update_process_memo_20260527.md \
  check_loveca_db_integrity_20260527.py
```

### 2. Dazzling Game 型の実装

```bash
git add llocg_ui/engine.py docs/handoffs/loveca_handoff_20260622h.md
```

### 3. family audit 一式

```bash
git add \
  loveca_reports/loveca_deck_bottom_family_audit_20260604a.* \
  loveca_reports/loveca_live_storage_topbottom_family_audit_20260605a.* \
  loveca_reports/loveca_mass_green_bottom_family_audit_20260605a.* \
  loveca_reports/loveca_stage_leave_basic_auto_family_audit_20260610f.* \
  loveca_reports/loveca_stage_leave_optional_discard_baton_family_audit_20260610h.* \
  loveca_reports/loveca_success_count_cost_misc_family_audit_20260610c.* \
  loveca_reports/loveca_success_score_body_and_activate_condition_audit_20260610a.* \
  loveca_reports/loveca_success_storage_count_score_family_audit_20260608d.* \
  loveca_reports/loveca_success_storage_score_sum_family_audit_20260608g.* \
  loveca_reports/loveca_yell_revealed_family_audit_20260604a.* \
  tools/audit_deck_bottom_family_20260604.py \
  tools/audit_live_storage_topbottom_family_20260605.py \
  tools/audit_mass_green_bottom_family_20260605.py \
  tools/audit_stage_leave_basic_auto_family_20260610.py \
  tools/audit_stage_leave_optional_discard_baton_family_20260610.py \
  tools/audit_success_count_cost_misc_family_20260610.py \
  tools/audit_success_score_body_and_activate_condition_20260610.py \
  tools/audit_success_storage_count_score_family_20260608.py \
  tools/audit_success_storage_score_sum_family_20260608.py \
  tools/audit_yell_family_20260604.py
```

### 4. 別判断で扱うもの

| パス | 扱い |
|---|---|
| `llocg_fetch_all_card_images.py` | 整理開始前からの既存差分。PBHS / CLHS 対応のように見えるため、今回の整理・Dazzling Game 実装とは別 commit 推奨 |
| `.cache_llocg/`, `.cache_llocg_bak_20260327/` | Git 追跡済み旧キャッシュ。削除や管理解除は別タスク |
| `jank/cleanup_20260622/` | ローカル退避先。Git には載せない |

---

## 10. 作業完了前チェック

- [x] `AGENTS.md` を読んだ
- [x] `git status` を確認した
- [x] 既存 diff がある場合、今回触ったファイルと分けて説明できる
- [x] カード番号専用分岐を増やしていない
- [x] 既存 route / helper を先に確認した
- [x] 変更した `.py` の BUILD_TAG を更新した
- [x] `python3 -m py_compile` を通した
- [x] `git diff --check` を通した
- [x] デバッグコマンドは `docs/debug/loveca_debug_commands_20260623.md` に集約した
- [x] ファイル移動・削除・退避・バックアップ作成をした場合、元パスと移動先を報告した

---

## 11. 20260625c top-k complex family 更新

`loveca_reports/loveca_topk_complex_family_audit_20260604a.*` を現行リポジトリ基準で再生成した。

結果:

- `needs_audit_unmatched_topk`: 0 件
- 追加実装:
  - `LL-bp4-001`: 対象名メンバー top5 任意回収 + 選んだコスト/元々ブレード数による相手ウェイト手入力
  - `PL!-bp6-006`: 色指定 + top5 条件達成時の `μ's` 回収 + ブレード3付与
  - `PL!N-bp5-029`: ステージ `中須かすみ` 条件 + top4 から `中須かすみ` 選択 + 選択カード色ハート付与
  - `PL!SP-bp5-009`: 最大5回の任意 top1 控え室 + ブレード付与 + ライブなら自身ウェイト
- 追加で監査済みにした実装済み系:
  - ライブ合計スコア+N枚を見る効果
  - ステージ人数/グループ人数参照の top-k / reveal 系
  - 公開継続、数指定コスト比較、指定グループライブ異名数、捨て札グループ分岐、ライブ置き場から topdeck する系

確認:

- `python3 -m py_compile llocg_ui/engine.py llocg_ui/server.py tools/audit_topk_complex_family_20260604.py`
- `python3 tools/audit_topk_complex_family_20260604.py`
- 新規4件の内部スモーク

備考:

- ファイル移動・削除・バックアップ作成は行っていない。
- デバッグコマンドは `docs/debug/loveca_debug_commands_current_updates_20260623.md` に追記し、統合ファイルは未変更。
