# Loveca implementation debug checklist 20260623

目的: 20260622h から 20260623i までに追加した実装の確認観点とコマンドを一箇所に集約する。

＊ユーザコメントとcodexコメントを区別しやすくするため、追加コメントについては別の記号を使うように
＊ユーザ/codexコメントツリーは該当デバッグが完全に完了するまで削除しない
※20260713f運用修正：コメントツリー維持は未解決項目のユーザーコメントを削除・上書きしないためのルール。該当デバッグが完了した項目は、重要な確認事項や再発防止ルールを `Resolved debug confirmations` または `docs/notes/loveca_runtime_implementation_rules_20260708.md` に残したうえで、active command から外す。

0708
＊全体的に実装ルールに従えていない実装が多い(複数コスト選択時のUI、自動効果の無言処理、効果発生源の表示など)。一度ルールを整理するべきではないだろうか

※対応済み：実装前・デバッグ対応前・完了前に確認する補助ルールとして `docs/notes/loveca_runtime_implementation_rules_20260708.md` を作成した。複数コスト選択、自動効果の無言処理、効果発生源表示、カード番号だけの表示、公開/見る/エール表示、state の寿命と snapshot/restore まで必須チェック化した。

※20260721再整理: 旧コメントに残る効果処理関連の指摘を現行実装と照合した。`発生源なし` / `自動効果の無言処理` / `対象なし無言終了` の代表経路は、現在は `source_cn`、実行中効果本文、`message_ack` / `confirm_effect` / `auto_order` を通す方針で対応済み。相手個別情報に関する旧指摘は、1デッキ版では手入力・手動確認を正式仕様、2デッキ版では相手context/action bridgeで実状態へ寄せる方針に再分類した。2デッキ用UIでは情報秘匿不要のため、相手手札候補がactive側に見えることは残件扱いしない。秘匿が必要なのは1デッキ用かつパブリックウィンドウを用いるリモート起動のみ。UI目視・操作感に残るものは `docs/handoffs/loveca_handoff_20260721_visual_confirmation_checklist_ja.md` へ分離し、この旧文書内の該当コメントは「実処理は対応済み、必要なら目視確認」扱いとする。

## Common commands

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

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
# 必要な LLOCG_* を設定
python3 ./run_llocg_ui_web.py
```

Open:

```text
http://127.0.0.1:8787/
```

## Individual UI launch commands

Each block is self-contained and follows the `AGENTS.md` debug command format.
Stop the previous server before starting the next one if port `8787` is already in use.

## Debug comment handling rule

- `＊挙動問題なし` / `＊挙動確認済み`: active command から外し、Resolved debug confirmations へ移動する。
- `＊挙動問題あり`: 指摘内容を確認して修正し、修正内容コメントを追記する。必要なら起動コマンドも更新する。
- `＊` の次行にタブ付きコメント: 個別カードだけでなく同型 UI に広く効くよう一般化して実装し、修正内容コメントを追記する。
- Codex 側の追記コメントは `※` で始め、ユーザーコメントの `＊` と区別する。
- 未解決のユーザー/Codex コメントツリーは、該当デバッグが完全に完了するまで削除・上書きしない。
- 完了済み項目は active 側に残し続けない。重要な確認事項やルールは、Resolved 側の補足または runtime implementation rules へ移して保持する。
- `※YYYYMMDD内部確認` はデバッグ対応時の確認対象に含める。現行コードと食い違う内部確認、検証条件が不足している内部確認、後続修正で壊れた可能性がある内部確認は再確認し、必要な修正と再確認結果を追記する。
- 内部監査で問題なしと判断した項目でも、UI表示・操作感・ユーザー指定観点の目視確認が必要かを再判定する。ユーザー確認不要なら active/current から外して Audited internal confirmations へ移し、ユーザー確認が必要なら理由を残して active/current に残す。

## Resolved debug confirmations

- `PL!N-bp5-029` Kasumi reveal pick grants picked heart colors
  - 2026-07-15: ユーザー確認済みとして active から移動。
  - 確認コメント: 問題なし
  - 修正/確認反映: 20260713e継続監査：挙動確認済み扱い。公開カードの public view 反映は `views.py` の pending/reveal event 公開カード抽出経路で継続確認対象。
- YELL reveal popup and two draw icons
  - 2026-07-15: ユーザー確認済みとして active から移動。
  - 確認コメント: 挙動問題なし
  - 修正/確認反映: 20260713e確認済み：現行コマンドは `export LLOCG_START_STAGE_C='PL!SP-bp2-010'` 形式に修正済み。挙動問題なし扱い。
- `PL!HS-bp1-002` waiting-room member to former area
  - 2026-07-15: ユーザー確認済みとして active から移動。
  - 確認コメント: 問題なし。
  - 修正/確認反映: 控え室から元エリアへ登場させる対象選択は `display_cards` 付きのカードリスト UI 経路を使用。起動効果由来のポップアップ見出しは `起動効果` 表示になるよう再適用済み。
- `PL!HS-bp5-022` waiting-room group member to empty area
  - 2026-07-15: ユーザー確認済みとして active から移動。
  - 確認コメント: 問題なし。
  - 修正/確認反映: 条件付き「以下から1つを選ぶ」親句を後続選択肢に引き継ぎ、ステージ条件未達時は条件未達の確認ポップアップを出すよう修正済み。デバッグコマンドも条件用ステージと控え室対象を入れる形へ更新済み。
- `PL!SP-pb2-001` top 5 cost <=4 Liella member to empty stage or hand
  - 2026-07-15: 末尾の「挙動問題なし」コメントにより active から移動。
  - 確認コメント: 挙動問題なし。
  - 修正/確認反映: top-k 候補を手札または空きステージへ移動する `topk_stage_or_hand` 経路、カード名表示、デッキから登場したメンバーの登場時自動効果収集を修正済み。
- `PL!N-bp3-025` return under-energy for temporary hearts
  - 2026-07-15: 末尾の「挙動問題なし」コメントにより active から移動。
  - 確認コメント: 挙動問題なし。
  - 修正/確認反映: 下エネルギー戻し枚数の数値選択 UI、ハート増加バッジ、必要ハート未達時の失敗判定を確認済み。数値選択 UI の再発防止ルールは runtime rules へ反映済み。
- `PL!HS-bp2-008` baton condition negative cases
  - 2026-07-15: 末尾の「挙動、ポップアップともに確認。問題なし。」コメントにより active から移動。
  - 確認コメント: 挙動、ポップアップともに確認。問題なし。
  - 修正/確認反映: higher cost / same cost / different group の負例で、ブレード+2が付与されないことと条件未達ポップアップを確認済み。same cost source は同一カード番号配置を避けるコマンドへ差し替え済み。

- `PL!-bp5-222` / `PL!HS-cl1-007` top 3 choose 1
  - 2026-06-23: 挙動確認済み。
  - 修正反映: 自己ウェイト＋手札コスト判定の一般化を確認済み。
- `PL!HS-bp5-008` cost 9+ Hasunosora member filter
  - 2026-06-23: 挙動確認済み。
  - 修正反映: 自己ウェイト＋手札コスト判定の一般化を確認済み。
- `PL!-sd1-007` mill top 5 then draw if live
  - 2026-06-23: 挙動確認済み。
  - 修正反映: 自動効果確認ポップアップ表示を確認済み。
- `PL!HS-bp1-008` mill top 3 then draw if all members
  - 2026-06-23: 挙動問題なし。
- `PL!HS-PR-019` / `PL!HS-PR-021` / `PL!HS-sd1-013` color-heart member condition
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 自動効果確認の条件文を日本語化し、ハート/ブレード表記を texticon 表示へ一般化。
- `PL!N-pb1-002` under-energy optional enter
  - 2026-07-13: 挙動確認済みとして active から移動。
  - 確認内容: 登場時任意効果でエネルギー2枚をメンバー下に置き、`PL!HS-bp1-019` のスコア常時ボーナスが反映される。
- `PL!HS-bp6-008` self wait then retrieve score <= 4 Hasunosora LIVE
  - 2026-07-13: 挙動確認済みとして active から移動。
  - 確認内容: 登場時に自身が WAIT になり、控え室候補はスコア4以下の『蓮ノ空』LIVE に絞られる。
- `PL!-bp5-010` mill top 3 then retrieve A-RISE member
  - 2026-06-23: 挙動問題なし。
- `PL!N-bp1-009` mill top 2 then retrieve member
  - 2026-06-23: 挙動問題なし。
- `PL!-pb1-006` topdeck μ's live then opponent-wait draw check
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 控え室からデッキ上に置く pending に発生源と効果内容を表示。
- `PL!-pb1-016` optional discard then lily white top 4 search
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 任意手札コストの表示で、条件と効果の重複表示を削減。
- `LL-bp6-001` top 6 choose 2 to hand
  - 2026-06-23: 挙動確認済み。
  - 2026-06-23 修正反映: top-k 複数枚選択は、カードを順番に即解決する方式ではなく、選択枠を付けて必要枚数を選び、確定ボタンでまとめて解決する UI に一般化。
- `PL!HS-cl1-004` simple mill top 3
  - 2026-06-23: 挙動問題なし。
  - 2026-06-23 修正反映: 登場時などの複数効果モード選択は、ポップアップ上部の効果説明の直下に `①効果1` / `②効果2` の枠付き選択肢として表示する UI に一般化。
- `PL!-sd1-019` top 3 keep any reorder
  - 2026-06-23: 挙動問題なし。
- `PL!HS-cl1-001` top1 optional mill
  - 2026-06-23: 挙動問題なし。
- `PL!HS-bp5-001` / `PL!HS-bp5-013` / `PL!HS-bp6-009` conditional blade gain
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 登場時効果を検証できるよう、対象カードを初期ステージから外したデバッグコマンドで確認済み。
- `PL!N-bp1-011` reveal until live
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 公開結果の移動先表示を追加し、カード番号ではなくカード名優先で表示するよう一般化。
- `PL!SP-bp5-013` Sunny Passion or blade-heart Liella member top 5
  - 2026-06-23: 挙動問題なし。
- `PL!N-bp4-021` waiting room any card to deck top
  - 2026-06-23: 挙動問題なし。
  - 修正反映: 控え室からデッキ上へ置く pending に発生源と効果内容を表示。
- `PL!HS-pb1-004` mill top 3 then retrieve Cerise Bouquet live
  - 2026-06-23: 挙動問題なし。
  - 修正反映: エネルギー不足を避けるコマンドに変更し、控え室検索が group だけでなく unit も見るよう修正。
- `PL!HS-pb1-027` optional mill if Cerise Bouquet member exists
  - 2026-06-23: 挙動問題なし。
  - 修正反映: ライブ成功時効果を検証できるよう、対象 LIVE とステージ条件を固定したコマンドに修正。
- `PL!-bp6-016` top 3 reorder all
  - 2026-06-23: 挙動問題なし。
  - 修正反映: ステージ上の効果元と成功用 LIVE を分離したコマンドに修正。並べ替え UI は、カード上にドロップした時の挿入位置を移動方向に応じて対象カードの前後へ分けるよう一般化。
  - 保留: ウインドウリサイズ時の全体レイアウト追従は広範囲の UI 改修になるため別作業。
- `PL!S-bp6-005` all red/green/blue member top 2
  - 2026-06-23: 挙動問題なし。
- `PL!S-bp2-005` red/green/blue heart member top 7 up to 3
  - 2026-06-23: 挙動問題なし。
- `PL!-bp6-002` no-ability or always μ's top 2
  - 2026-06-25: 挙動問題なし。
  - 修正反映: <常時>能力判定を `ability_type` の `常時` のみに限定し、起動能力のみの μ's カードを候補外にした。
  - 補足: ユーザーコメントにより、起動能力持ちの除外はコマンド上では未確認だった旨を履歴として残す。
- `PL!N-bp4-009` draw 2 then hand to deck top if own stage cost is lower
  - 2026-06-29: 挙動問題なし。
  - 修正反映: 手動確認後に2枚引き、手札1枚をデッキ上へ置く動作を確認済み。
- `PL!N-pb1-004` reveal top cost <=9 member to hand then position change
  - 2026-06-29: 挙動問題なし。
  - 修正反映: ライブステップドロー後に確認対象を公開できるコマンドで、公開カード手札追加とポジションチェンジを確認済み。
- `LL-bp4-001` named member pick then opponent wait
  - 2026-06-29: 挙動問題なし。
  - 修正反映: ライブステップドロー後に対象名メンバーが候補に残るコマンドで、対象選択後の相手ウェイト人数入力を確認済み。
- `PL!SP-bp5-007` top 5 choose up to 3 by distinct group
  - 2026-06-30: 問題なし。
  - 修正反映: 同一ポップアップ内の複数選択、3枚上限、同一グループ候補のグレーアウト選択不可表示を確認済み。
- `PL!N-bp5-021` mill 2 then optional waiting LIVE to 4th from top
  - 2026-06-30: 問題なし。
  - 修正反映: 控え室ライブ候補のカードリスト表示と、リストの意味が分かる本文表示を確認済み。
- `PL!HS-bp6-001` look top stage member count +2, keep one on top
  - 2026-06-30: 問題なし。
  - 修正反映: 登場時効果を確認できるコマンドと、デッキ上に残す1枚を選ぶ説明表示を確認済み。
- `PL!-bp6-006` choose heart color, reveal top5, pick μ's and gain blades
  - 2026-06-30: 問題なし。
  - 修正反映: ハート色表示と、手札コスト支払いであることが分かる本文表示を確認済み。
- `PL!SP-bp5-009` repeat optional mill top1, gain blade, wait if live
  - 2026-06-30: 問題なし。
  - 修正反映: ミル結果カード、ブレード獲得、ライブカード時のウェイト結果表示を確認済み。

## Audited internal confirmations

- 20260714 internal confirmation audit
  - 分類: ユーザー確認不要。
  - 理由: `※20260714内部確認` 27件のメタ監査で、主要 route の DB 実文 matcher、trigger 別 matcher missing、residual enter route smoke を確認する内部整合監査。UI目視やユーザー指定操作感の確認を含まないため、内部 smoke 通過で監査完了扱い。
  - 結果: `<登場>` / `<ライブ開始時>` / `<ライブ成功時>` の matcher missing は 0。内部 smoke は `internal confirmation audit OK`。監査用に手入力した文面の揺れが1件あったが、DB 実文では `PL!SP-sd2-003` が `draw_then_draw_if_self_moved_this_turn` に正しく match するため、コード修正不要。

- 20260714/20260715 internal smoke sections
  - 分類: ユーザー確認不要。
  - 理由: 見出しが `Internal smoke:` のエンジン内部確認で、UI目視・操作感・ユーザー指定画面表示の確認を目的にしないため、内部 smoke 通過で監査完了扱い。
  - 移動件数: 18件。
  - 対象:
    - Internal smoke: entry-origin effects and stage-movement BODY autos: ※20260714内部確認: 上記 smoke と同系統の確認として、登場元参照の `PL!S-bp6-006` は2ドロー+ブレード3、`PL!HS-bp6-015` は2ドロー+手札2枚同時 discard pending を確認。stage movement BODY auto は `PL!SP-sd2-002` の実移動から `auto_order` を経由して確認済み。
    - Internal smoke: `PL!N-bp3-005` enter-count routes and `PL!S-bp5-005` entered-member heart picker: ※20260714内部確認: `PL!N-bp3-005` は登場3回履歴で手札5枚までドロー、登場2回以上履歴でライブ合計スコア+1付与を確認。`PL!S-bp5-005` はこのターン登場した非Aqoursメンバーだけを対象に `choose_heart_color_for_stage_positions` pending を出し、選択した黄ハート+1を付与、Aqours側には付与しないことを確認。
    - Internal smoke: `PL!SP-pb1-025` reduces required `<任意>` by entered/moved `5yncri5e!` members: ※20260714内部確認: `stage_entered_cardnumbers_this_turn` と `stage_moved_cardnumbers_this_turn` にそれぞれ `5yncri5e!` メンバーを1枚ずつ入れ、`PL!SP-pb1-025` の必要ハート `<任意>` 減少が合計2として `live_start_required_any_reduction_by_cn` に記録されることを確認。登場/移動履歴を汎用 ledger で参照している。
    - Internal smoke: PL!S-bp6-020 mode choices and PL!HS-bp2-021/023/025 baton-entered required color reductions: ※20260714内部確認: smoke 通過。`PL!S-bp6-020` の3選択肢はそれぞれ `this_live_card_gains_live_success_effect_until_end_live` / `baton_entered_stage_group_member_gain_icons_until_end_live` / `success_storage_count_wrapper` に match。得た `<ライブ成功時>` 1ドローはライブ成功時 trigger で発火し、バトンタッチ登場済み Aqours メンバーへの赤ハート付与、`PL!HS-bp2-021/023/025` の蓮ノ空バトンタッチ登場2枚条件による必要色軽減も確認。
    - Internal smoke: generic live-start score routes for stage/live-zone conditions: ※20260714内部確認: smoke 通過。4件とも `live_start_score_if_*` の汎用 trigger に変換され、`PL!N-bp1-028` stage group member +1、`PL!N-bp1-029` live-zone count +2、`PL!-bp4-022` center group blade threshold +2、`PL!HS-bp5-020` stage group cost threshold +1 が `live_start_score_bonus_by_set_idx` に反映されることを確認。
    - Internal smoke: named / not-named group / exact-cost / no-ability baton-enter conditions: ※20260714内部確認: smoke 通過。バトンタッチ元の名前一致、コスト一致、能力なし、not-named group の各 wrapper が条件成立時のみ内側効果を解決し、negative named case は pending を出さず skip ログを残すことを確認。not-named group の控え室ライブ回収は `choose_card_from_green` pending で発生源付きの候補表示へ進む。
    - Internal smoke: lower-cost baton then both players discard-to-3/draw-3: ※20260714内部確認: smoke 通過。現在の実装では1枚ずつ discard ではなく、方針どおり `choose_member_from_green_multi_up_to` を使った手札2枚同時 discard pending を生成する。pending には `PL!-bp5-007` の発生源、条件、実行中効果本文が入り、2枚選択後に後続 `カードを3枚引く。` が解決されることを確認。相手側処理は manual ログで残る。
    - Internal smoke: retrieve / draw-blade references to members placed in waiting room by the current baton: ※20260714内部確認: smoke 通過。`baton_old_cardnumbers` と控え室の実カードを照合し、このバトンタッチで控え室に置かれた『Liella!』メンバーだけを参照して回収/ドロー/ブレード付与を解決することを確認。非Liella! の negative case は pending を出さず skip ログになる。カード番号専用ではなく、バトンタッチ元履歴と group 条件の汎用 route。
    - Internal smoke: unless-baton discard / energy gate / baton-enter BODY draw / two-baton effect resolution: ※20260714内部確認: smoke 通過。`Printemps` からのバトンタッチ時は discard を skip、非該当では1ドロー後に discard pending を出すことを確認。`Liella!` バトンタッチ+エネルギー7枚以上条件ではエネルギーデッキから wait +2、BODY 側の「自分のメンバーがバトンタッチして登場」誘発では発生源 `PL!N-PR-025` の自動効果で1ドロー、2人バトンタッチ条件では2ドロー後に控え室からコスト4以下『Liella!』メンバー登場 pending へ進む。
    - Internal smoke: place the member card put into waiting room by baton under this member: ※20260714内部確認: smoke 通過。バトンタッチで控え室に置かれた『Liella!』メンバーを、このメンバー下へ移動できることを確認。さらに `_move_under_cards_to_green_from_slot` でステージ離脱時に下のメンバーカードが控え室へ戻ることも確認。
    - Internal smoke: stage-leave effects that reference the baton-entered member: ※20260714内部確認: smoke 通過。ステージ離脱時のバトンタッチ先参照で、`PL!HS-sd1-001` style はバトンタッチ登場したコスト10以上『蓮ノ空』メンバーを見てエネルギー2枚アクティブ化、`PL!N-bp7-019` style はバトンタッチ登場した『虹ヶ咲』メンバー下へエネルギーデッキから1枚置くことを確認。
    - Internal smoke: put a cost-limited group member from waiting room under this member: ※20260714内部確認: smoke 通過。控え室からコスト9以下『虹ヶ咲』メンバーを、このメンバー下へ移動する route を確認。候補検索は控え室・cost・group 条件を使う汎用経路。
    - Internal smoke: baton-block BODY routes and no pre-commit under-card movement: ※20260714内部確認: smoke 通過。BODY によるバトンタッチ禁止は `cmd_play` の支払い前に判定され、ブロック時は手札・エネルギー・下エネルギー・下カード・控え室が動かないことを確認。unit/group 制限つきの禁止では、非該当メンバーは同様にブロックされ、該当する `みらくらぱーく！` メンバーへのバトンタッチだけ成功後に下カード/下エネルギー移動を行う。
    - Internal smoke: current cost counts matching member cards under this member: ※20260714内部確認: smoke 通過。`PL!SP-pb2-006` style の BODY 常時は、このメンバー下の条件一致メンバーカードだけを数え、現在コストが base 2 から effective 4 へ増えることを確認。
    - Internal smoke: hand/green/under-card routes and under-count bonuses: ※20260714内部確認: smoke 通過。手札のコスト制限 group メンバーを下に置いてハート色選択、下のコスト制限 group メンバーを空きエリアに登場、下メンバー枚数による一時コスト+ハート付与（3枚 cap）、下の名前種類数によるブレード付与、エネルギーデッキから指定ステージ/自身の下へ置く route、控え室メンバーを指定ステージメンバー下へ置く route を確認。いずれもカード番号専用ではなく zone/cost/group/name-count の汎用経路。
    - Internal smoke: energy-condition BODY bonuses, top-bottom pending, optional wait energy, bottomdeck no-BH threshold: ※20260714内部確認: smoke 通過。列挙された BODY 常時/起動系テキストはすべて generic matcher に match。top1 bottom/keep pending、任意 wait energy、控え室 group 3枚 bottomdeck + no-bladeheart 閾値ブレード付与、under-energy による常時ハート bonus、WAIT メンバーのアクティブ化 `choose_stage_member_to_activate` pending、ライブカード置き場2枚以上 draw、単純なライブ合計スコア+1を確認。
    - Internal smoke: BODY continuous conditions, live-zone conditions, and simple this-card score routes: ※20260714内部確認: smoke 通過。列挙された success-zone / stage / live-zone / this-card score 系テキストはすべて generic matcher に match。成功ライブ置き場 group による常時ハート、ステージ名前種類条件、ステージ cost/group 条件 draw、ライブカード置き場 group 条件 draw、ライブ置き場枚数条件の控え室ライブ回収 pending、ステージ group 条件スコア+1、成功ライブ置き場 group がある場合の追加 draw、スコア+1後の控え室 group LIVE 回収 pending を確認。
    - Internal smoke: energy thresholds, group activation, and energy-derived BODY bonuses: ※20260714内部確認: smoke 通過。列挙された energy threshold / activation 系テキストはすべて generic matcher に match。エネルギー枚数比例 draw、エネルギー11枚以上のライブ回収 pending、エネルギー6枚以上の wait energy 追加、エネルギー12枚以上/active energy 条件のスコア route、エネルギー6枚超過差分ハート、エネルギー10枚以上の BODY cost bonus、group メンバー1人アクティブ化 pending、group 全員+全エネルギーアクティブ化を確認。

- 20260715 pure engine-state internal confirmations
  - 分類: ユーザー確認不要。
  - 理由: デバッグコマンドに付属する内部確認のうち、ドロー枚数・条件成立・エネルギー/スコア補正などのエンジン状態で完了判定でき、UI目視・操作感の確認が主目的ではないもの。
  - 移動件数: 4件。
  - 対象:
    - `PL!SP-sd2-003` live-success draw + moved bonus draw: ※20260714内部確認: `PL!SP-sd2-003` の効果文を generic matcher `draw_then_draw_if_self_moved_this_turn` 経由で解決し、`stage_moved_cardnumbers_this_turn=['PL!SP-sd2-003']` の状態で通常1枚+追加1枚の計2枚ドローを確認。カード番号専用分岐ではなく「このメンバーがエリアを移動している場合、さらにドロー」の文型 route を通っている。
    - `PL!SP-bp5-014` enter draw if another stage member moved: ※20260714内部確認: `PL!SP-bp5-014` 自身とは別のステージメンバーを `stage_moved_cardnumbers_this_turn` に入れた状態で、登場時の「ほかのメンバーがエリアを移動している場合」条件が成立し1枚ドローを確認。履歴参照は汎用の stage movement ledger 経由。
    - PL!-bp4-004 enter success-zone score sum activates energy: ※20260714内部確認: 成功ライブ置き場スコア合計6/6で wrapper が成立し、内側のエネルギー2枚アクティブ化を確認。条件未達時は skip ログに落ちる汎用 `success_score_sum_gte_apply_inner` route。
    - PL!N-bp5-010 live success excess heart total score adjustment: ※20260714内部確認: 余剰ハート0では `last_attempt_total_score_bonus=1`、余剰ハート1では補正なし、余剰ハート2以上では `last_attempt_total_score_bonus=-1` になることを内部 smoke で確認。減算は「0未満にならない」処理のため、見える形で -1 を確認する場合は元スコア1以上のライブで試す必要がある。実装は `live_success_total_score_excess_zero_or_gte_adjust` の汎用 resolver で、カード番号専用分岐は追加されていない。

- 20260715 additional engine-state internal confirmations
  - 分類: ユーザー確認不要。
  - 理由: デバッグコマンドに付属する内部確認のうち、ブレード付与・スコア補正・必要ハート軽減・WAIT配置などのエンジン状態で完了判定できるもの。UI目視・操作感・ユーザー指定表示の確認を主目的にしないため監査済み扱い。
  - 移動件数: 5件。
  - 対象:
    - `PL!S-bp5-022` moved stage members gain blade at live start: ※20260714内部確認: `stage_moved_cardnumbers_this_turn=['PL!SP-sd2-002']` の状態で、移動済みステージメンバーだけに `temp_blade +1`、未移動メンバーには付与なしを確認。`このターン中にエリアを移動したメンバー` family の汎用 route を通り、対象カード番号専用分岐ではない。
    - `PL!SP-pb2-003` moved by Liella effect live total score +1: ※20260714内部確認: `PL!SP-pb2-003` が移動履歴にある状態で、ライブ成功時の `live_success_score_if_self_moved_by_group_effect` route が `last_attempt_total_score_bonus +1` を適用することを確認。ログは `PL!SP-pb2-003 moved by 『Liella!』 effect this turn` と発生源を含む。
    - PL!-bp3-023 stage blade total >= 10 reduces required any by 2: ※20260714内部確認: `PL!-bp3-023` の効果文を generic matcher 経由で解決し、ステージ現在ブレード合計10/10で `live_start_required_any_reduction_by_set_idx[0] = 2` を確認。YELL用のアクティブ限定ではなくステージ全体の現在ブレード合計を参照している。
    - PL!N-bp4-006 hand member entry wait if blade-heart: ※20260714修正/内部確認: `hand_member_cost_le_group_entry_wait_if_bladeheart` でも同じ未定義 `_apply_effect_rule` 呼び出しを検出し、汎用 dispatcher へ修正。`PL!N-bp4-006` は手札のコスト4以下『虹ヶ咲』メンバー `PL!N-bp4-003` を空きエリアへ登場させ、ブレードハート所持により WAIT 状態で置かれることを確認。
    - PL!HS-bp1-004 live-in-progress count gains blade: ※20260714内部確認: ライブ中カード0枚では skip ログ、2枚では発生源 `PL!HS-bp1-004` のステージメンバーへブレード+2が入ることを内部 smoke で確認。ライブ中カード枚数×アイコン数の汎用 route `live_in_progress_count_gain_blades_until_end_live` で処理され、カード番号専用分岐ではない。

## Active debug commands integrated 20260625c

### 20260625c remaining top-k audit batch

#### `PL!N-bp3-007` hand member to former area then under-energy

起動後: センターの `PL!N-bp3-007` の起動効果を使う。コストで `PL!N-bp3-007` が控え室へ置かれ、手札のコスト13以下の『優木せつ菜』メンバー `PL!N-bp1-007` だけが候補に出ることを見る。別名メンバー `PL!N-bp1-001` は候補外になる。選択後、`PL!N-bp1-007` がセンターに登場し、そのメンバーの下エネルギー表示が1枚になることを見る。ログでは `[ACT] PL!N-bp3-007: hand PL!N-bp1-007 -> stage C; energy under +1` を確認する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!N-bp3-007'
export LLOCG_START_HAND='PL!N-bp1-007,PL!N-bp1-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=3
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊デバッグコマンド不備：対象となるカードが手札に存在しない
＊挙動問題あり：対象が存在しない場合に無言で処理を終了している
※修正済み：現行コマンドでは対象 `LL-bp2-001` を手札に入れる形になっていることを確認。対象が存在しない場合は、手札/控え室から登場させる同系 route で確認ポップアップを返すよう修正済み。
＊対象がない場合の挙動は問題なし。
＊デバッグコマンド不備解消されず。手札にあるカードはコスト13以下でも優木せつ菜でもない
※20260713e修正済み（20260715訂正前）: 手札対象を `PL!N-bp1-001`（コスト9、上原歩夢）へ差し替えていたが、これは誤った「優木せつ菜以外」DB文面を前提にした暫定対応だった。
※20260715再修正: ユーザー指摘に基づき、ローカルDB正本の `PL!N-bp3-007` 効果文から「以外」を削除し、「コスト13以下の『優木せつ菜』のメンバーカード」に手動修正。runtime も `hand_member_cost_le_named_to_former_area_then_energy_under` 汎用 route を追加し、手札候補はコスト13以下かつカード名が『優木せつ菜』に一致するメンバーだけにした。デバッグ対象は `PL!N-bp1-007` へ差し替え。内部 smoke では手札に `PL!N-bp1-007` と別名メンバーを混ぜ、候補が `PL!N-bp1-007` のみに絞られ、解決後にセンター登場＋下エネルギー1枚になることを確認。カード番号専用分岐なし。

＊＊＊重要な不具合：表示されている効果文が間違っている。正しい効果文は「コスト13以下の「優木せつ菜」のメンバーカード」であるのに「優木せつ菜」以外となっている。DBを確認して齟齬の有無を確認、取得元から間違っているのかどうかを再確認すること。＊＊＊最優先事項＊＊＊
※20260715訂正: 前回のCodex調査コメントは誤り。ユーザーの再確認に従い、Wiki由来の誤取得としてローカルDBを手動修正し、実装も指定名一致 route へ切り替えた。以後このカードは「優木せつ菜以外」ではなく「優木せつ菜」のメンバーカードを対象にする。

＊挙動問題なし。ただし、手札にせつ菜以外のカードがなかったため指定名称以外が弾かれるかどうかは未確認
＊UI修正：メンバーの下に置かれたエネルギーカードの枚数をカード右下に小さくバッジ表示するようにしたい
※20260715修正済み：DB手動修正後は `PL!N-bp3-007` の対象が「優木せつ菜」指定になったため、指定名称以外を弾く挙動が正しい。内部 smoke で手札に `PL!N-bp1-007` と別名メンバーを混ぜ、候補が `PL!N-bp1-007` のみに絞られることを確認済み。UI はステージカード右下にメンバー下エネルギー枚数 `×N` の小型バッジを表示するよう修正。ユーザー実機再確認待ち。

＊手札にせつ菜以外のカードを混ぜたデバッグコマンドへ修正して欲しい
＊バッジの実装を確認。これだけだと何のバッジかわからないので「縦長長方形を二つ重ねて円で囲ったアイコンを数量表示の前につける」または「カード右下ではなく重ねられたカードのうち最も外側のものの右下に表示する」のいずれかもしくは両方で再実装する
※20260715修正済み：デバッグコマンドの手札に `PL!N-bp1-001` を追加し、別名メンバーが候補外になることを実機確認できる形へ修正。下エネルギーバッジはステージカード本体ではなく、重ねられたエネルギーカードの最外側右下に表示し、縦長カード2枚の重なりを表す小アイコン＋数量 `×N` の表示へ変更。ユーザー実機再確認待ち。

＊挙動問題なし
＊UI要修正：重ねられたカードの上に表示したことによってメンバーカードの背面に表示されており確認できなくなった。前面表示になるように修正する
※20260715再修正済み：下エネルギーバッジを重ねられたエネルギーカード要素の子からステージ枠内の前面レイヤーへ移し、最外側エネルギーカード右下に座標固定して表示するよう修正。メンバーカードより前面の `z-index` に上げたため、背面に隠れない想定。ユーザー実機再確認待ち。

＊問題なし。

#### `LL-bp5-002` live-success retrieve different stage-group card

起動後: `LL-bp5-002` をライブセットして成功させる。ライブ成功時に、ステージ上メンバーの推定グループ名（`μ's` / `虹ヶ咲` / `蓮ノ空`）と異なるグループ名を持つ控え室カードだけが候補になることを見る。この例では `PL!SP-pb2-008` だけが候補になり、選択すると手札に加わる。`PL!-bp4-005` はステージ側に `μ's` がいるため候補外。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!-bp4-005'
export LLOCG_START_STAGE_C='PL!N-pb1-002'
export LLOCG_START_STAGE_R='PL!HS-bp5-002'
export LLOCG_START_HAND='LL-bp5-002'
export LLOCG_START_GREEN='PL!SP-pb2-008,PL!-bp4-005'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-bp4-013,PL!-bp3-020,PL!-bp4-020,PL!-pb1-030,PL!-bp4-024,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-bp4-013,PL!-bp3-020,PL!-bp4-020,PL!-pb1-030,PL!-bp4-024,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-bp4-013,PL!-bp3-020,PL!-bp4-020,PL!-pb1-030,PL!-bp4-024,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-bp4-013,PL!-bp3-020,PL!-bp4-020,PL!-pb1-030,PL!-bp4-024,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-bp4-013,PL!-bp3-020,PL!-bp4-020,PL!-pb1-030,PL!-bp4-024'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=12
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊デバッグコマンド不備：山札が少なすぎてリフレッシュするので控え室がなくなる
＊UI修正：条件不適の際に表示されるポップアップに確認ボタンがない
※修正済み：デッキ枚数不足でリフレッシュしにくいよう、`LLOCG_START_DECK_EXACT` を10枚に増量。条件不適時の `message_ack` に `ok` 選択肢を追加し、確認ボタンが出るよう修正。
＊デバッグコマンド不備解消されず。自分で盤面ブレード総数10本以上にしてるのになんで中途半端に山札を増やすのか理解できない、普通に50枚くらいにすればいい

※修正済み：`choose_card_from_green` pending に `auto_effect_detail` とカード画像表示を追加。条件不適/候補選択時に発生源と効果詳細が残るよう共通経路を修正。デッキ枚数不足のコマンドは50枚相当の `LLOCG_START_DECK_EXACT` へ差し替え済み。
※20260715内部確認: `green_card_group_different_from_stage_members_retrieve` の汎用 route で、ステージのグループ名 `μ's` / `虹ヶ咲` / `蓮ノ空` を参照し、控え室候補は異なるグループ名の `PL!SP-pb2-008` のみに絞られることを確認。`PL!-bp4-005` はステージ側に `μ's` がいるため候補外。pending には `source_cn=LL-bp5-002`、実行中効果文、カード表示候補が入る。カード番号専用分岐なし。

＊挙動問題なし。
＊要確認：控え室から手札に加えたカードが公開されるエフェクトがなかった。公開情報として処理されているかを確認。同様に控え室からカードを手札に加える他の全ての効果において、加わったカードを公開領域として扱えているか回帰確認
※20260715内部確認: `server.py` の public hand reveal 経路を確認。`resolve_pending` 前に公開ソース（控え室/成功置き場/公開済みresolve等）の枚数を記録し、解決後に同じカードが手札へ増え、公開ソース側の枚数が減った場合は `_remember_public_hand_reveals_after_cmd` が `public_hand_revealed_cards` / `public_hand_reveal_events` に追加する。`LL-bp5-002` の `PL!SP-pb2-008` は控え室から手札に移るため、この汎用 public-zone -> hand ルールで public view の手札にも公開表示される想定。デバッグコマンドは `LLOCG_START_DECK_EXACT` を50枚相当に増やし、不要リフレッシュで控え室が消えない形になっている。ユーザー実機再確認待ち。

＊変わらずエフェクトはないが実装上問題がないのであれば問題なし。

#### `PL!HS-bp5-002` embedded energy cost then waiting-room member to empty area

起動後: センターの `PL!HS-bp5-002` の起動効果を使う。効果文先頭の `<(E)><(E)>` が支払われ、控え室からコスト2以下のメンバーを選ぶポップアップが出る。`PL!HS-bp1-008` を選び、空きエリアに登場することを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!HS-bp5-002'
export LLOCG_START_GREEN='PL!HS-bp1-008,PL!HS-bp2-008'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=2
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題あり：コスト20のメンバーを対象選択できてしまう
＊デバッグコマンド不備：対象が控え室にない
＊UI問題あり：起動効果なのに自動効果としてポップアップが出ている、対象カードリストに画像が出ていない
※修正済み：控え室メンバー登場系の候補なし時は無言終了せず確認ポップアップを返すよう修正。起動効果由来の対象選択ポップアップは `起動効果` 表示にし、候補リストは `display_cards` 付きでカード画像表示される経路を維持。内部確認ではコスト2以下の `LL-bp6-001` のみ候補になり、コスト4の `PL!HS-bp2-008` は候補外。
※20260706再確認済み：ローカル更新で一部上書きされていたため、現行 `engine.py` に再適用。候補なしではエネルギーを支払わず確認ポップアップ、候補ありでは `LL-bp6-001` のみ候補になり、ポップアップ見出しが `起動効果` になることを内部確認。
＊デバッグコマンド不備：控え室にコスト２以下のメンバーが存在しない。LL-bp6-001はコスト２０のメンバーだが、これは正しく読み取れていますか？DBがおかしい？
※20260713e修正済み：`LL-bp6-001` は現行DBでコスト20のため不適。控え室対象を `PL!HS-bp1-008`（コスト2、徒町小鈴）へ差し替え、比較用に `PL!HS-bp2-008`（コスト4）を残した。

＊挙動問題なし
＊他のカードの問題：PL!HS-bp1-008の効果で山札から控室に置かれたカードを公開するポップアップがエール公開ポップアップを通ってしまっている。通常のカード公開ポップアップを通るように修正。同様に山札の上からn枚を公開/見る他の全ての効果がエールポップアップを通っていないか回帰確認
※20260715修正済み：通常の山札公開/確認 `show_revealed_cards_ack` がエール公開カード確認の見出し・集計欄で表示される問題を確認し、UI側でエール公開 pending と通常公開 pending を分岐。`yell_reveal_ack` / エール系ラベル / エール系メタがある場合だけ「エール公開カード確認」とハート・アイコン集計を表示し、通常公開は「公開カード確認」または指定ラベルでカード確認だけを出すよう修正。ユーザー実機再確認待ち。

＊挙動問題なし
＊UI要修正：再三指摘している発生源の未表示。効果処理の共通ルートを再度よくよく確認して発生源が表示されない効果処理ポップアップが一つもないように網羅的に確認して潰せ
※20260715追加対応: 自動ブレード付与の汎用 route `gain_blade_until_end_live` がログだけで終わる経路を修正し、起動効果以外では `message_ack` pending に `source_cn` と `auto_effect_detail` を出すようにした。これによりバトンタッチ登場時のブレード付与など、即時解決される同型効果も発生源付き確認ポップアップを通る。ユーザー実機再確認待ち。

#### `PL!HS-bp2-008` baton from lower-cost group member enter bonus

起動後: 手札の `PL!HS-bp2-008` をセンターにいる `PL!HS-bp2-004` へ重ねて登場させる。バトンタッチ元がこのメンバーよりコストが低い『DOLLCHESTRA』メンバーなので、登場時効果によりライブ終了時までブレード+2される。差額コスト2だけ支払われることも確認する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!HS-bp2-004'
export LLOCG_START_HAND='PL!HS-bp2-008'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=10
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
  要修正：自動効果が無言で処理されている
※20260713e継続監査：挙動自体は確認済み。自動効果の無言処理は共通 UI 課題として、発生源/条件/効果詳細を確認ポップアップへ出す方針で継続。

＊無言処理を修正するように。
※20260715追加修正済み: `PL!HS-bp2-008` の内側効果が通る `gain_blade_until_end_live` 共通処理へ確認ポップアップを追加。解決時に `PL!HS-bp2-008` の発生源、条件詳細、ブレード+2の結果が表示される。

#### `PL!SP-pb2-008` yell-revealed no-blade-heart Liella score bonus

起動後: `LL-bp5-001` をライブセットしてライブ開始からエールへ進める。ステージの `PL!SP-pb2-008` が、エール公開されたブレードハートを持たない『Liella!』メンバー2枚につきライブ合計スコア+1する。下記は4枚公開で上限+2を確認する。



```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!SP-pb2-008'
export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!SP-PR-004,PL!SP-PR-005,PL!SP-PR-006,PL!SP-PR-008,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI問題あり：常々言っているが効果を解決する際に条件達成の有無、詳細、発動した効果は必ずポップアップ表示すること
※20260713e継続監査：挙動確認済み。効果詳細ポップアップは `auto_effect_detail` 補完対象を広げる共通課題として継続。
※20260715修正済み：エール時自動効果のうち即時解決される `draw1` / `live_total_score_bonus` / `gain_icons` 系で、解決結果を `message_ack` pending として表示するよう共通化。`PL!SP-pb2-008` ではエール公開のブレードハートなし『Liella!』メンバー枚数、加算スコア、上限適用後の結果が確認できる。ユーザー実機再確認待ち。

＊DB要照合：実際にはライブ成功時効果であるのにライブ開始時効果として処理されている。DBを確認し、不整合が発見された場合はDB全体を監査しローカル処理として修正する。修正した場合、監査メモを作成する。以前ローカル修正したもの(せつ菜)についてもメモが必要なのですでに作成済みであればそちらにまとめ、未作成であれば作成しこれとまとめる。
※20260715追加修正済み: ローカルDB正本 `cards_min_tokv1.csv` / `cards_min_tokv1.json` / `cards_compiled_v7h.json` の `PL!SP-pb2-008` を `<ライブ成功時>` に手動補正し、`manual_override_applied` / `manual_override_reason` を付与。runtime も、エール時自動効果収集が `<ライブ成功時>` を拾わないよう共通ガードを追加し、ライブ成功時側へ「ブレードハートなし『Liella!』メンバー2枚につきライブ合計スコア+1、上限+2」の汎用 resolver を追加した。監査メモは `docs/notes/loveca_db_manual_corrections_20260715.md` に作成。

#### `PL!S-bp2-004` no-LIVE revealed reroll yell

起動後: `LL-bp5-001` をライブセットしてエールへ進める。ステージの `PL!S-bp2-004` により、公開カードにライブカードがない場合、それらをすべて控え室へ置いて追加エールする確認ポップアップが出ることを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!S-bp2-004'
export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!S-PR-028,PL!S-PR-032,PL!S-PR-013,PL!S-PR-016,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI問題あり：追加エールを行った際に行われたエールの詳細が表示されない。エール確認ポップアップの表示を「エールを行う」という事象が発生した直後のタイミングになるように調整できないだろうか
※20260713e修正済み：追加エール直後に `追加エール公開カード確認` を出し、公開枚数/ドローアイコン数/ドロー枚数/公開カードを表示するよう修正。

＊問題なし。

#### `PL!S-bp3-020` blade-heart two-or-fewer reroll yell

起動後: `PL!S-bp3-020` をライブセットしてエールへ進める。公開カードの中にブレードハートを持つカードが2枚以下なら、それらをすべて控え室へ置いて追加エールする確認ポップアップが出ることを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!S-bp2-004'
export LLOCG_START_HAND='PL!S-bp3-020'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!S-PR-028,PL!S-PR-032,PL!S-PR-013,PL!S-PR-016,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI問題あり：同上。エールの詳細表示がない
※20260713e修正済み：追加エール共通処理側で確認ポップアップを生成するよう修正したため、同系ルートへ適用。

＊UI問題あり：PL!S-bp3-020[エール時] エール公開カードにライブカードがないため、公開カード3枚をすべて控え室に置いて、3枚の追加エールを行いますか？と表示されるが、実際の効果内容と異なっている。ダイヤのポップアップを流用しすぎ
※20260715追加修正済み: `confirm_move_all_current_yell_to_green_then_extra_yell` pending に効果ごとの `prompt_text` を渡すよう修正。`PL!S-bp3-020` は「ブレードハートを持つカードが2枚以下」「そのエールで得たブレードハートを失ってもう一度エール」の文面になり、ライブカードなし条件の文面を流用しない。ユーザー実機再確認待ち。


#### `PL!HS-bp6-027` choose revealed cards then extra yell

起動後: `PL!HS-bp6-027` をライブセットしてエールへ進める。公開されたブレードハートを持たない『蓮ノ空』カードを最大3枚まで選び、選んだ枚数ぶん追加エールできることを見る。`PL!HS-bp5-022` はライブカードでブレードハートを持つため候補外。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!HS-bp5-002'
export LLOCG_START_HAND='PL!HS-bp6-027'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!HS-PR-027,PL!HS-PR-029,PL!HS-bp5-022,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030,PL!-bp4-013'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題あり：追加エール後の詳細が見えていない
※20260713e修正済み：追加エール共通処理側で確認ポップアップを生成するよう修正。選択式追加エール後も同じ表示経路を通る。
※20260715内部確認: エール公開カード `PL!HS-PR-027` / `PL!HS-PR-029` / `PL!HS-bp5-022` で、`choose_yell_revealed_to_green_then_extra_yell` の汎用 route がブレードハートを持たない『蓮ノ空』カード2枚だけを候補にすることを確認。2枚選択後、選択カードは控え室へ移動し、同数の追加エールを行い、追加エール後に `show_revealed_cards_ack` で公開カード詳細を表示する。再発防止として追加エール詳細 pending に `source_cn=PL!HS-bp6-027` を渡すよう修正済み。カード番号専用分岐なし。

＊UI問題あり：効果処理時に控え室へ置くカードは3枚「まで」であるのに0枚選択が不可能なUIになっている。また、追加エールの確認はできるが既存のエール内容は同時に確認できないのは不親切。既存のエール内容＋追加のエール内容の表示になるように修正
※20260715追加修正済み: `choose_yell_revealed_to_green_then_extra_yell` にカード画像リストUIと `0枚で終了` / `選択を終了` ボタンを追加し、0枚選択を可能にした。追加エール後の確認 pending には `base_yell_cards` と `additional_yell_cards` を保持し、既存エール公開カード＋追加エール公開カードを同じ確認画面で表示するよう修正。ユーザー実機再確認待ち。

#### `PL!SP-bp2-010` yell reveal count modifier

起動後: `LL-bp5-001` をライブセットしてライブ開始時効果を解決する。他メンバーがいるため、`PL!SP-bp2-010` によりこのライブ終了時までエール公開枚数が8枚減ることを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!SP-bp2-010'
export LLOCG_START_STAGE_C='PL!SP-PR-004'
export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!SP-PR-004,PL!SP-PR-005,PL!SP-PR-006,PL!SP-PR-008,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI要修正：解決した結果何が起きたか表示されない。また、ブレード本数を減らす効果についてバッジ表示を試しに実装してみたい
※20260713e一部対応：ステージ/ライブカード上の増減バッジは UI スケール追従へ修正。エール公開枚数減少の結果表示は追加の確認表示として継続。
※20260715内部確認: 現行 `live_start_yell_reveal_count_delta_if_other_stage_members_at_least` route では、条件達成/未達のどちらも `message_ack` pending を出し、発生源 `PL!SP-bp2-010`、他ステージメンバー人数、エール公開枚数 -8 の適用結果を表示する。結果表示は実装済みのため、ユーザー実機再確認待ち。

＊問題なし。

#### `LL-bp5-001` movement condition live-success score bonus

起動後: 先に左サイドの `PL!SP-bp5-006` の起動効果を使い、右サイドへポジションチェンジさせる。その後 `LL-bp5-001` をライブセットして成功させる。エール公開ライブ数やステージハート種類数が不足していても、このターンの実際のエリア移動記録によりスコア+1されることを見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!SP-bp5-006'
export LLOCG_START_STAGE_C='PL!SP-PR-005'
export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!SP-PR-004,PL!SP-PR-005,PL!SP-PR-006,PL!SP-PR-008,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

＊デバッグコマンド不備：与えられた状況では移動できない。bp5のきな子(R)あたりの起動効果で動かせるようにするべき
※20260713e継続監査：開始フラグで移動済みを注入する形ではなく、実際のポジションチェンジ/移動効果で移動させてから確認するコマンドへ差し替え対象。
※20260715内部確認: `live_success_score_if_revealed_live_or_stage_heart_kinds_or_moved` の汎用 route で、エール公開LIVE数0/2、ステージハート種類数2/5でも、`stage_moved_this_turn=True` と移動済みカード履歴により `LL-bp5-001` のスコア+1が適用されることを確認。ライブ成功時スコア加算 helper を修正し、成功時も `message_ack` で `source_cn=LL-bp5-001` と条件内訳を表示する。実機コマンドは引き続き、開始フラグ注入ではなく実際の移動効果を通す形への差し替えが望ましい。
※20260715再修正済み：デバッグコマンドを開始フラグ注入方式から、`PL!SP-bp5-006` の起動効果「このメンバーはポジションチェンジする。」を実際に使って移動履歴を作る方式へ変更。起動後は `PL!SP-bp5-006` を左サイドから右サイドへ移動し、その後 `LL-bp5-001` をライブセットしてライブ成功時の移動条件スコア+1を確認する。

＊要修正：PL!SP-bp5-006の効果を正しく起動できない。実装されていない可能性がある
※20260715修正済み：起動効果 matcher を `このメンバーをポジションチェンジする。` だけでなく `このメンバーはポジションチェンジする。` にも対応するよう一般化。あわせて起動コスト `デッキの上からカードをN枚控え室に置く` を汎用コストとして支払えるよう修正。内部 smoke で `PL!SP-bp5-006` が起動可能になり、山札上3枚が控え室へ置かれ、`position_change` pending が出ることを確認。
※20260715追加確認：`LL-bp5-001` 用コマンドと同じ初期状態で `PL!SP-bp5-006` を左サイドから右サイドへ移動させ、`stage_moved_this_turn=True` と `stage_moved_cardnumbers_this_turn=['PL!SP-bp5-006']` が記録されることを確認。開始フラグ注入ではなく実移動を通す確認コマンドとして成立。

Expected after 20260625c:

```text
needs_audit_unmatched_topk=0
```

## Focused UI debug targets

### 20260622h yell heart color conversion

- `PL!HS-bp6-027`: live start, revealed yell cards include Hasunosora members with all six heart colors. Confirm target-color conversion is applied until live end.
- `PL!SP-bp4-023`: Dazzling Game style color conversion. Confirm the chosen/target color is reflected during the live.

### 20260622i top-k choose N to hand

- `LL-bp6-001`: put six known cards on top. Confirm two selected cards go to hand and the other four go to waiting room.

### 20260622j sentence variant and simple mill

- `PL!-bp5-222` / `PL!HS-cl1-007`: confirm top 3 is shown, one selected card goes to hand, remaining two go to waiting room.
- `PL!HS-cl1-004`: confirm the top 3 cards move to waiting room.

### 20260622k cost-filtered group member

- `PL!HS-bp5-008`: put a cost 9+ Hasunosora member and non-matching cards in top five. Confirm only the matching member is selectable.
- `PL!-bp4-006`: set success live score sum to at least 3. Confirm the inner μ's member top-five search appears.

### 20260623a reorder typo and top1 optional mill

- `PL!-sd1-019`: confirm the top 3 reorder UI appears and kept cards return to deck top in selected order.
- `PL!HS-cl1-001`: confirm top card can be moved to waiting room or kept on top.

### 20260623b conditional mill followups

- `PL!-sd1-007`: top five include at least one live. Confirm top five go to waiting room, then draw 1.
- `PL!HS-bp1-008`: top three are all members. Confirm top three go to waiting room, then draw 1.
- `PL!HS-PR-019` / `PL!HS-PR-021` / `PL!HS-sd1-013`: top three are matching-color heart members. Confirm source gains the matching temporary heart.
- `PL!HS-bp5-001` / `PL!HS-bp5-013` / `PL!HS-bp6-009`: confirm source gains the expected temporary blade icons only when the milled cards meet the condition.

Note: if the followup draw empties the deck, existing refresh rules may immediately shuffle waiting room into the deck. Use a deck with extra remaining cards when checking waiting-room contents.

### 20260623c mill retrieve / reorder all / optional mill

- `PL!-bp5-010`: confirm top 3 move to waiting room, then A-RISE member picker appears.
- `PL!HS-pb1-004`: confirm top 3 move to waiting room, then Cerise Bouquet live picker appears.
- `PL!N-bp1-009`: confirm top 2 move to waiting room, then member picker appears.
- `PL!-pb1-006`: confirm μ's live topdeck UI appears, followed by opponent-wait draw confirmation.
- `PL!HS-pb1-027`: confirm optional mill prompt appears only when a Cerise Bouquet member is on your stage.
- `PL!-bp6-016`: confirm top 3 reorder UI requires all three cards to be placed back on deck top.
- `PL!-pb1-016`: confirm optional hand-discard picker appears first, then the lily white top-four search appears after paying the cost.

### 20260623d reveal until live

- `PL!N-bp1-011`: put non-live cards above one live card. After paying the optional hand-discard cost, confirm the live card goes to hand and all earlier revealed cards go to waiting room.

### 20260623e trailing punctuation top-k route

- `PL!SP-pb1-017`: put a `5yncri5e!` card and non-matching cards in the top five. Confirm only the matching unit card is selectable.

### 20260623f debug feedback pass

- `PL!-bp5-222` / `PL!HS-cl1-007`: confirm the source member becomes WAIT after paying the self WAIT plus hand-discard cost.
- `PL!HS-bp5-008`: confirm the source member becomes WAIT after paying, then the cost-9+ Hasunosora member filter appears.
- `PL!-sd1-007`: confirm automatic top-five mill then draw shows an `自動効果確認` popup with moved cards and result text.
- `LL-bp6-001`: confirm top-k multi-pick uses selected frames/order badges and one final confirm button.

### 20260623g top-k filter variants

- `PL!-bp6-002`: confirm no-ability μ's or <常時> μ's cards are selectable from top two.
- `PL!S-bp6-005`: confirm only members with red, green, and blue hearts are selectable from top two.
- `PL!SP-bp5-013`: after paying hand discard, confirm Sunny Passion members or blade-heart Liella! members are selectable from top five.
- `PL!N-bp4-021`: confirm any waiting-room card can be placed on top of the deck, with skip available.

### 20260623i top-k filtered up-to multi-pick

- `PL!S-bp2-005`: confirm only red/green/blue-heart members are selectable from top seven, and 0 to 3 selected cards can be moved to hand.

### 20260706h hand member empty-area entry / generic lower-cost baton

#### `PL!-PR-015` lower-cost baton -> hand member cost <= 4 enters empty area

Confirm that playing `PL!-PR-015` by baton from a lower-cost member opens a hand member picker, then an empty-area picker. Select `PL!-PR-007`, then choose `L` or `R`; it should enter stage without paying its play cost.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='PL!-PR-015,PL!-PR-007'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_C='PL!-sd1-002'
export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

＊デバッグコマンド不備：効果対象が手札にない
※20260713e継続監査：対象カードを手札へ入れるコマンド修正対象。カード選定と効果条件を現行DB基準で再確認する。
※20260715修正・内部確認: 手札対象をステージのバトンタッチ元と重複しない `PL!-PR-007`（コスト4メンバー）へ差し替え。`m_baton_lower_any_enter` wrapper がバトンタッチ元 `PL!-sd1-002` コスト2 < `PL!-PR-015` コスト17を確認し、内側の `hand_member_cost_le_to_empty_area` 汎用 route で `hand_member_to_empty_area` pending を出すことを確認。pending には発生源、条件文、実行中効果文、カード表示候補が入る。カード番号専用分岐なし。

＊UI要修正：カードリスト選択ポップアップになっていない。これも再三指摘している内容なので絶対に再発させないように全ての類似効果について再確認および修正を行うこと。2度と同じ指摘をさせるな
※20260715追加修正済み: `hand_member_to_empty_area` 共通pendingにカード画像リスト選択UIを追加。`PL!-PR-015` だけでなく、手札からコスト条件を満たすメンバーを空きエリアへ登場させる同型効果は同じカードリストポップアップを通る。ユーザー実機再確認待ち。

#### `PL!-PR-015` lower-cost baton negative same-cost case

Confirm that playing `PL!-PR-015` by baton from another cost-17 member does not open the hand member entry picker and shows/skips the unmet lower-cost condition.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='PL!-PR-015,PL!-PR-007'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_C='PL!-bp6-006'
export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

＊デバッグコマンド不備：該当のカードが手札にない。やはりステージと手札で同カードナンバーのカードを設定しようとするとうまくいかないバグがある？
※20260713e継続監査：同一カード番号を手札/ステージに重複指定する確認ではなく、別カードを使うバトンタッチ負例として再構成する。
※20260715修正・内部確認: 負例はステージ側を別カード番号のコスト17メンバー `PL!-bp6-006` に差し替え、同一カード番号の手札/ステージ重複に依存しない形へ変更。内部 smoke では `baton_old_cost=17`、`new_cost=17` のため lower-cost 条件が不成立となり、`hand_member_to_empty_area` は開かず、`message_ack` で `source_cn=PL!-PR-015` と未達理由を表示することを確認。条件未達をログだけにしないよう `m_baton_lower_any_enter` / group variant に共通修正済み。

### 20260707a generic draw-until-hand / stage-member-count draw

#### `PL!HS-PR-031` hand size 5 draw route

Confirm that after paying the optional hand discard cost, the effect draws cards until the hand count reaches 5.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='PL!HS-PR-031,LL-bp5-001,PL!-bp4-013'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_DECK_EXACT='PL!HS-bp6-001,PL!HS-bp6-002,PL!HS-bp6-003,PL!HS-bp6-004,PL!HS-bp6-005,PL!HS-bp6-006,LL-bp6-001'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
※20260713f整理：同じツリーに複数枚ハンドコスト UI 指摘を含むため active に残す。再確認完了後は Resolved へ移動する。
＊UI要修正：複数枚のハンドコストを選択する場合は同時に選択するようにする。これも何回指摘しているかわからない

※修正済み：複数枚の手札捨てコストは共通 helper で `choose_member_from_green_multi_up_to` の hand multi-select pending を使うよう修正。`PL!HS-PR-031` は内部確認で 2枚同時選択 pending になることを確認済み。UI実機再確認待ち。

#### `PL!-bp3-004` stage member count draw then discard route

Confirm that the on-enter effect draws 1 card for each current stage member, then opens the hand discard picker for 1 card.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='PL!-bp3-004'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_L='PL!-sd1-002'
export LLOCG_START_STAGE_R='PL!-PR-007'
export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

＊挙動問題なし
＊UI要修正：効果の発生源と効果詳細が出ていない

※修正済み：ドロー後/効果後の手札捨て pending に `auto_effect_detail` と `source_cn` を渡すよう共通 helper を修正。`PL!-bp3-004` は内部確認で登場時効果の発生源と効果本文が pending text に入ることを確認済み。UI実機再確認待ち。

### 20260707b stage condition / score-filtered waiting LIVE retrieve

### 20260707c moved self gains blade

#### `PL!SP-bp4-017` live-start moved self gains 2 blades

Confirm that `PL!SP-bp4-017` gains two temporary blade icons at live start only when it is currently in the left-side area and is recorded as moved this turn. Moving it to center/right or removing `LLOCG_START_STAGE_MOVED_CARDNUMBERS` should skip the effect.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_L='PL!SP-bp4-017'
export LLOCG_START_STAGE_MOVED_THIS_TURN=1
export LLOCG_START_STAGE_MOVED_CARDNUMBERS='PL!SP-bp4-017'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006,LL-bp5-001,LL-bp5-002,PL!-bp4-005,PL!-bp4-006,PL!-bp4-007'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

＊挙動問題あり：配置されているのが左サイドエリアではないのに効果が発動する
＊デバッグコマンド不備：移動させる効果を持ったカードで移動させた後確認する流れで無いと正しい挙動を確認できない
※20260713e継続監査：効果条件の位置指定と、実際に移動させてから確認するコマンドの両方を再確認対象として残す。
※20260715内部確認: `gain_blade_if_self_moved_this_turn` の汎用 route で、`PL!SP-bp4-017` が移動済み履歴に含まれる場合は `temp_blade=2`、含まれない場合は付与なしになることを確認。成功時/条件未達時とも `message_ack` で `source_cn=PL!SP-bp4-017` と結果を表示するよう修正済み。なお、元コメントどおり UI実機コマンドは左サイド条件を通す配置と、実際の移動効果を通す流れへの差し替え余地が残る。
※20260715再修正済み：ライブ開始時 trigger に能力条件欄を保持し、条件欄に `左サイド` / `右サイド` / `センター` がある場合は現在位置と照合してから解決するよう汎用修正。内部 smoke で `PL!SP-bp4-017` がセンターにいる場合は移動済み履歴があってもブレードを得ず、左サイドにいる場合だけブレード+2になることを確認。デバッグコマンドも左サイド配置かつ `LLOCG_START_STAGE_MOVED_CARDNUMBERS` を使う形へ修正済み。

### 20260707e stage movement BODY auto triggers

#### `PL!SP-sd2-002` self position-change then movement trigger

Confirm that activating `このメンバーをポジションチェンジする。` opens a destination picker. After moving, an auto-order prompt should appear for the movement trigger, and resolving it should grant a temporary purple heart to the moved member.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_STAGE_C='PL!SP-sd2-002'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: 起動効果本文 `このメンバーをポジションチェンジする。` で `position_change` pending が出ること、移動先 `L` 解決後に `auto_order` pending が発生し、選択肢 `PL!SP-sd2-002[移動時]：このメンバーがエリアを移動したとき、ライブ終了時まで、<(紫)>を得る。` を解決して移動後のメンバーに紫ハート+1が付くことを確認。無言処理ではなく、移動後の自動効果は発生源付き pending を経由している。

### 20260707g moved stage member bonus routes

#### `PL!SP-bp5-024` choose heart for moved stage members

Confirm that the live-start effect opens a heart-color picker, then grants the chosen heart to the stage member listed in `LLOCG_START_STAGE_MOVED_CARDS`.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='PL!SP-bp5-024'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_C='PL!SP-sd2-002'
export LLOCG_START_STAGE_MOVED_THIS_TURN=1
export LLOCG_START_STAGE_MOVED_CARDS='PL!SP-sd2-002'
export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: 移動済みメンバーがいる状態で `choose_heart_color_for_moved_stage_members` pending が出ること、選択肢解決後に移動済みメンバーだけへ選んだハート+1が付くことを確認。選択 UI を経由しており、自動効果の無言処理ではない。

### 20260707i moved by group effect live-success score

### 20260707j entry origin and additional stage movement autos

#### `PL!S-bp6-008` brings `PL!S-bp6-006` from waiting room, then waiting-entry draw and blade gain

Start with `PL!S-bp6-008` on stage, activate its BODY ability, choose `PL!S-bp6-006` from waiting room, and confirm the entered member draws 2 and gains blade x3 because it entered from waiting room.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!S-bp6-008'
export LLOCG_START_GREEN='PL!S-bp6-006'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=6
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `cmd_activate_to_green` で起動コスト `<(E)><(E)>` と自身控え室送りを処理し、`green_member_to_former_area` pending から `PL!S-bp6-006` を元いた `C` に登場させた。登場元 `green` が記録され、`PL!S-bp6-006[登場]` が2枚ドロー+ブレード3付与を解決することを確認。発生源付き pending で候補カードリストも保持されている。

#### `PL!HS-bp6-016` brings `PL!HS-bp6-015` from waiting room, then non-hand-entry draw and discard

Activate `PL!HS-bp6-016` BODY, choose `PL!HS-bp6-015` from waiting room, and confirm the entered member draws 2 and creates a discard-2 pending because it entered from outside the hand.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!HS-bp6-016'
export LLOCG_START_GREEN='PL!HS-bp6-015'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=8
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `cmd_activate_to_green` で起動コスト `<(E)>`×4 を支払い、`green_member_to_empty_area` → `green_member_to_empty_area_place` で `PL!HS-bp6-015` を空きエリアに登場させた。登場元 `green` により `PL!HS-bp6-015[登場]` が2枚ドロー後、`choose_member_from_green_multi_up_to` の手札2枚同時選択 discard pending を生成することを確認。pending には発生源 `PL!HS-bp6-015` と実行中効果本文が渡っている。

### 20260707k stage-entered-this-turn condition

#### `PL!N-bp1-006` activates energy when a Nijigasaki member entered this turn

Play `PL!N-bp1-001` from hand first, then activate `PL!N-bp1-006` BODY and discard the remaining hand card as the cost. Confirm that 2 energy move from wait to active.

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='PL!N-bp1-001,LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!N-bp1-006'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp4-020,PL!-bp4-024,PL!-bp4-021,PL!-bp3-006'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=2
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `PL!N-bp1-001` を手札からプレイして `stage_entered_cardnumbers_this_turn=['PL!N-bp1-001']` が記録された後、`PL!N-bp1-006` の起動効果を手札1枚 discard pending 経由で解決し、ウェイトからアクティブへエネルギー2枚移動を確認。プレイコスト支払いがあるため最終値は開始値そのままではなく、起動効果前後の差分で `active +2 / wait -2` を確認する。

### 20260707l turn-enter count and entered-member heart routes

### 20260707m entered-or-moved required-any reduction

## Debug comment audit 20260713d

※目的: `＊` で始まるユーザーコメントの未対応状態を棚卸しし、今回対応したものと継続対応が必要なものを分ける。

※今回確認した結果:

- `＊` コメントのうち、直後の Codex 対応コメントがないものは 41 件。
- このうち `＊挙動問題なし` / `＊問題なし` 系は resolved へ移動対象。未解決指摘を同じツリーに含まないものから active 側から外す。
- `current updates` は `Integrated current updates 20260713d` へ統合済み。current 側は次回追記用に空へ整理済み。

※今回コード対応したもの:

- `choose_card_from_green` のカード番号表示問題: カード画像リスト表示対象へ追加し、`auto_effect_detail` を渡すよう修正。
- `choose_live_from_green` / `choose_member_from_green` の発生源・効果詳細不足: `_enqueue_choose_from_green` で `auto_effect_detail` を補完するよう修正。
- `self_top1_to_green_or_keep` / `self_top1_to_bottom_or_keep` の発生源・効果詳細不足: pending 生成時に詳細ブロックを付与。
- `LL-bp5-002` デバッグコマンドの山札不足: `LLOCG_START_DECK_EXACT` を50枚相当へ増量。

※継続対応が必要な主なコメント:

- `PL!N-bp3-025`: ハート増加バッジの可変表示、必要ハート色数未達でも成功する疑い。
- YELL 追加/再エール系: 追加エール後の詳細表示、エール確認ポップアップの表示タイミング。
- 自動即時解決系: 条件達成/未達、詳細、発動した効果を確認ポップアップに出す共通化。
- `PL!SP-bp2-010`: エール公開枚数減少の結果表示と、ブレード本数減少バッジの試験実装。
- `LL-bp5-001`: 移動条件確認用のデバッグコマンド不備。実際に移動効果で動かしてから確認する形へ修正が必要。
- `PL!N-bp3-007` / `PL!HS-bp5-002` など一部コマンド不備: DB上のコスト・対象カードがコメントと食い違うものは、カード選定から再確認が必要。

※次回優先:

1. YELL/追加エール表示の共通 UI 修正。
2. 必要ハート判定の再検証と `PL!N-bp3-025` 系の成功判定バグ確認。
3. `＊挙動問題なし` 系の resolved 移動。ただしユーザー確認済みのものから順に行う。

## Debug comment follow-up 20260713e

- 追加エール後に後続の自動効果がない場合も、`追加エール公開カード確認` ポップアップを必ず出すようにした。公開枚数、ドローアイコン数、実ドロー枚数、公開カード一覧を表示する。
- ステージ上カードの一時ハート/ブレード増加バッジと、ライブカードの必要ハート増減バッジで固定pxだったアイコンサイズ・間隔を UI スケール追従へ修正した。
- `PL!N-bp3-007` のデバッグコマンドは、対象を `PL!N-bp1-007` へ差し替えた。ローカルDB手動修正後の正しい条件で、コスト13以下の『優木せつ菜』メンバーを確認する。
- `PL!HS-bp5-002` のデバッグコマンドは、対象を `LL-bp6-001` から `PL!HS-bp1-008` へ差し替えた。`LL-bp6-001` は現行DBでコスト20のため、コスト2以下確認には不適。
- `PL!N-bp3-025` の必要ハート未達疑いは、現行の成功判定関数自体には今回の範囲で断定修正を入れていない。必要ハート `桃1/赤5/黄3/任意4` に対して、ライブ開始時に赤ハートだけを追加したケースで再現条件を分離して確認する。
- 20260713f: 確認済み項目の扱いを訂正。完了済み項目は active 側に残し続けず、重要な確認事項や再発防止ルールを Resolved または runtime rules 側へ移したうえで active から外す。
- `current updates` は統合済みで、現行更新ファイルは次回追記用の空状態を維持。

## Integrated current updates 20260713d

※ `docs/debug/loveca_debug_commands_current_updates_20260623.md` から統合。以後の追記は current updates 側に新規で行う。

### 20260709b live-start mode: gained success ability / baton-entered icon / required-color reduction

### 20260710a live-start score condition batch

### 20260710b enter-auto baton source condition wrappers

### 20260710c baton-old member reference routes

### 20260710d additional baton-enter condition routes

### 20260710e baton-old member under-card route

### 20260710f baton target stage-leave routes

### 20260710g waiting-room member under-card route

### 20260710h baton restriction and delayed under-card commit

### 20260710i under-card BODY cost bonus

### 20260710j under-card route batch

### 20260710k energy/top-bottom/body-always batch

### 20260712a continuous stage/success condition batch

### 20260712b energy activation/retrieve batch

### 20260713 audit: current updates against recurring UI/pending issues

※確認対象: このファイル内の 20260709b から 20260712b までの internal smoke 15本。

※参照した再発防止メモ:

- `docs/notes/loveca_runtime_implementation_rules_20260708.md`
- `docs/debug/loveca_debug_commands_20260623.md` 冒頭 0708 コメント
- 同メモ内の既知指摘: 自動効果の無言処理、効果発生源表示、条件達成/未達ポップアップ、候補なし時の無言終了、カード番号だけ表示、複数コスト/複数対象 UI

※実行確認:

- 15本すべて `STATUS=0`。
- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py` は通過。

※再監査結果:

- `DECK_CODE` wrapper 使用なし。
- 成功ライブカード置き場3枚以上の初期状態なし。
- 今回リスト対象カード番号の runtime 専用分岐は検出なし。
- `docs/debug/loveca_debug_commands_current_updates_20260623.md` の smoke は動作確認に寄っており、UI/pending 監査項目の出力が不足しているものがある。

※要確認/要修正候補:

- `choose_card_from_green`: `source_cn` はあるが、pending `text` / `auto_effect_detail` がなく、実行中効果本文が渡っていないケースを確認。例: 20260710b `not_named_group` の控え室 LIVE 回収。
- `choose_live_from_green`: 発生源は `text` に出るが、実行中効果本文ではなく「自動効果 / 処理」だけの pending になっているケースを確認。例: 20260712a live-zone count retrieval、score+retrieve、20260712b energy threshold LIVE retrieval。
- `self_top1_to_bottom_or_keep`: `source_cn` はあるが、pending `text` に発生源も実行中効果本文も出ていないケースを確認。例: 20260710k top1 optional bottom。
- `choose_hand_member_under_self` / `choose_under_member_to_empty_area`: `source_cn` と処理説明、`display_cards` はあるが、実行中効果本文は pending に渡っていないケースを確認。
- 自動で即時解決する draw / score / energy / under-card 移動系は log には結果が残るが、確認ポップアップが出る経路かどうかをこの smoke だけでは判定できない。過去指摘「自動効果の無言処理」の再発監査としては、確認ポップアップ有無を明示する追加 smoke が必要。

※次に見るべき共通経路:

- `_enqueue_choose_from_green`
- `_enqueue_discard_from_hand`
- `self_top1_to_bottom_or_keep` pending 生成箇所
- `choose_hand_member_under_self` / `choose_under_member_to_empty_area` pending 生成箇所
- 自動即時解決系を `message_ack` / `confirm_effect` / `auto_order` に乗せるべきかの共通方針

※20260713d対応:

- `_enqueue_choose_from_green`: `choose_live_from_green` / `choose_member_from_green` の `auto_effect_detail` が空になるケースに、発生源と処理内容を補完するよう修正。
- `choose_card_from_green`: UI のカード画像リスト表示対象へ追加し、発生源・効果詳細を pending に渡すよう修正。
- `self_top1_to_green_or_keep` / `self_top1_to_bottom_or_keep`: pending に発生源と効果詳細を表示するよう修正。
- `choose_hand_member_under_self` / `choose_under_member_to_empty_area`: 現行実装では `text` に `_auto_effect_detail_block`、`display_cards`、`source_cn` を渡していることを確認。`auto_effect_detail` が空のケースは継続監査対象。
- 自動即時解決系: 今回は未完了。`message_ack` / `confirm_effect` / `auto_order` に乗せる共通化方針は次回以降の継続対応。

※20260714再確認/追加修正:

- `choose_card_from_green` のうち `effects/green_search.py` → `effects/helpers.py` の `green_pick_filtered_to_hand` 経路では、`source_cn` しか pending に入らず `text` / `auto_effect_detail` / `display_cards` が欠けるケースが残っていた。
- `effects/helpers.py` の `_enqueue_choose_card_from_green_pending` を共通テンプレート化し、`text`、`options`、`display_cards`、`auto_effect_detail`、`suppress_card_text` を必ず渡すよう修正。
- 内部確認: `「徒町小鈴」以外の『蓮ノ空』のメンバーからバトンタッチして登場した場合、自分の控え室からライブカードを1枚手札に加える。` で、pending text が `【DEBUG】自動効果` と効果本文、処理文を含み、`display_cards=['PL!-bp3-020']` を持つことを確認。
- 併せて `engine.py` に残っていた孤立した `source_cn` 断片による `IndentationError` を除去。
- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py` 通過。
- `docs/debug/loveca_debug_commands_current_updates_20260623.md` の internal smoke 15本はすべて `STATUS=0`。

## 20260713a waiting-room score/retrieve batch

対象実装:

- 手札枚数が N 枚以下の場合、控え室からメンバーカードを回収
- 控え室から `<スコア+1>` を持つグループ LIVE を回収
- 控え室のカード名が異なる LIVE / グループ名が異なる LIVE の枚数条件から LIVE 回収
- 控え室のグループ LIVE 枚数 / 異名グループ LIVE 枚数条件からこのカードのスコア加算

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

個別デバッグ: `PL!N-bp5-011` 登場時、控え室のカード名が異なる LIVE 3枚以上 / グループ名が異なる LIVE 3枚以上から LIVE 回収 pending が出ること。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!N-bp5-011'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_GREEN='PL!-bp3-019,PL!-bp5-024,PL!HS-PR-010,PL!N-bp1-025'
export LLOCG_START_DECK_EXACT='LL-bp5-001,LL-bp5-002,PL!-bp4-013,PL!-bp4-020'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=9
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

## 20260713c generic remaining effect batch and debug-response UI fixes

対象実装:

- 成功ライブカード置き場枚数比例の「スコア加算 + 必要ハート増加」
- 成功ライブカード置き場枚数比例の「選んだハートを得る」
- ライブ中カード枚数条件からこのカードのスコア加算
- エネルギーデッキからウェイト配置し、次のアクティブフェイズにアクティブしない文型
- 自分/相手/双方のエネルギーデッキからのウェイト配置文型
- 手札コスト軽減 BODY 常時文型の matcher 追加
- ライブ中枚数/グループ条件 BODY 常時文型の matcher 追加

デバッグ対応:

- `choose_card_from_green` を UI のカード画像リスト表示対象に追加。
- `choose_card_from_green` pending に `auto_effect_detail` / `suppress_card_text` を渡すよう修正。
- `self_top1_to_green_or_keep` / `self_top1_to_bottom_or_keep` pending に発生源と効果詳細を表示するよう修正。
- current audit の「pending に発生源・効果詳細が不足する」指摘のうち、控え室カード選択と山札上1枚確認の共通経路を対応。

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

内部スモーク:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui.db import load_cards_db
from llocg_ui import engine
cards=load_cards_db(Path('.'))
texts=[
'自分のライブ中のカードが3枚以上ある場合、このカードのスコアを+2する。',
'自分のエネルギーデッキから、エネルギーカードを2枚ウェイト状態で置く。それらのエネルギーカードは、次のターンのアクティブフェイズにアクティブしない。',
'自分の成功ライブカード置き場にあるカード1枚につき、このカードのスコアを+2し、必要ハートを<桃><黄><紫><任意>増やす。',
'か<黄>か<紫>のうち、1つを選ぶ。ライブ終了時まで、自分の成功ライブカード置き場にあるカード1枚につき、選んだハートを1つ得る。',
'手札にあるこのメンバーカードのコストは、このカード以外の自分の手札1枚につき、1少なくなる。',
]
for t in texts:
    print('match', bool(engine._match_effect_template(t)), t[:70])
lives=[cn for cn,ci in cards.items() if engine._is_live_ci(ci)][:3]
gs=engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.set_zone=lives
engine.try_apply_effect_template(gs, random.Random(1), cards, texts[0], {'source_cn':lives[0], 'set_idx':0})
print('score_count', gs.live_start_score_bonus_by_set_idx)
gs=engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.energy_active=1; gs.energy_wait=0; gs.energy_total=12
engine.try_apply_effect_template(gs, random.Random(1), cards, texts[1], {'source_cn':'TEST','pos':'C'})
print('energy_no_active', gs.energy_wait, gs.pending[-1]['kind'] if gs.pending else None)
gs=engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.success_zone=lives[:2]
engine.try_apply_effect_template(gs, random.Random(1), cards, texts[2], {'source_cn':lives[0], 'set_idx':0})
print('success_inc_pending', gs.pending[-1]['kind'] if gs.pending else None, gs.pending[-1].get('required_increase_per') if gs.pending else None)
gs=engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.success_zone=lives[:2]
engine.try_apply_effect_template(gs, random.Random(1), cards, texts[3], {'source_cn':'TEST','pos':'C'})
print('success_heart_pending', gs.pending[-1]['kind'] if gs.pending else None, gs.pending[-1].get('options') if gs.pending else None)
PY
```

個別デバッグ: 成功ライブカード置き場2枚の状態で `PL!-bp5-022` をライブカード置き場へセットし、スコア +4、必要ハート `<桃><黄><紫><任意>` がそれぞれ2個ずつ増えること。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-PR-002'
export LLOCG_START_STAGE_R='PL!-PR-003'
export LLOCG_START_HAND='PL!-bp5-022'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_SUCCESS='PL!-bp3-019,PL!-bp3-020'
export LLOCG_START_DECK_EXACT='LL-bp5-001,LL-bp5-002,PL!-bp4-013,PL!-bp4-020'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=12
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

個別デバッグ: `PL!N-bp1-029` を含めてライブカードを3枚セットし、ライブ中カード3枚以上条件でこのカードのスコア +2 が入ること。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!N-PR-003'
export LLOCG_START_STAGE_C='PL!N-PR-004'
export LLOCG_START_STAGE_R='PL!N-PR-005'
export LLOCG_START_HAND='PL!N-bp1-029,PL!N-bp1-025,PL!N-bp1-026'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='LL-bp5-001,LL-bp5-002,PL!-bp4-013,PL!-bp4-020'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=12
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

個別デバッグ: `PL!S-sd1-007` BODY 起動時、手札2枚を控え室に置くコスト後に、控え室の `<スコア+1>` を持つ Aqours LIVE 回収 pending が出ること。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!S-sd1-007'
export LLOCG_START_HAND='LL-bp1-001,LL-bp3-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_GREEN='PL!S-bp2-024,PL!S-bp2-025'
export LLOCG_START_DECK_EXACT='LL-bp5-001,LL-bp5-002,PL!-bp4-013,PL!-bp4-020'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=8
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

## 20260713b stage/success/live-in-progress score batch

対象実装:

- ライブ中のグループカード枚数条件から、このカードのスコアを加算
- ステージの異なるグループ名メンバー数条件から、センターのメンバーへ `<ALL>` を付与
- 成功ライブカード置き場枚数に応じた一時ブレード付与
- 成功ライブカード置き場枚数に応じた必要ハート `<任意>` 減少

個別デバッグ: `PL!-bp3-019` と他の μ's LIVE を同時にライブカード置き場へセットし、`PL!-bp3-019` のライブ開始時スコア +1 が反映されること。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-PR-002'
export LLOCG_START_STAGE_R='PL!-PR-003'
export LLOCG_START_HAND='PL!-bp3-019,PL!-bp3-020'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='LL-bp5-001,LL-bp5-002,PL!-bp4-013,PL!-bp4-020'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=12
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

個別デバッグ: `LL-bp5-002` ライブ開始時、ステージに異なるグループ名のメンバーが3人いる場合、センターのメンバーに `<ALL>` が付くこと。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='LL-bp3-001'
export LLOCG_START_STAGE_R='LL-bp6-001'
export LLOCG_START_HAND='LL-bp5-002'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='LL-bp5-001,LL-bp5-002,PL!-bp4-013,PL!-bp4-020'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=12
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

個別デバッグ: 成功ライブカード置き場2枚の状態で `PL!-sd1-022` をライブカード置き場へセットし、必要ハート `<任意>` が合計4つ減ること。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_L='PL!-PR-001'
export LLOCG_START_STAGE_C='PL!-PR-002'
export LLOCG_START_STAGE_R='PL!-PR-003'
export LLOCG_START_HAND='PL!-sd1-022'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_SUCCESS='PL!-bp3-019,PL!-bp3-020'
export LLOCG_START_DECK_EXACT='LL-bp5-001,LL-bp5-002,PL!-bp4-013,PL!-bp4-020'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=12
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

## Internal smoke check snippets

Use these only for quick engine-level confirmation when UI setup is slow.

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 - <<'PY'
from pathlib import Path
from llocg_ui.db import load_cards_db, _get_card
from llocg_ui import engine
cards = load_cards_db(Path('.'))
targets = [
    'LL-bp6-001','PL!HS-bp5-008','PL!-sd1-019','PL!HS-cl1-001',
    'PL!-sd1-007','PL!HS-bp1-008','PL!HS-bp5-001',
    'PL!-bp5-010','PL!HS-pb1-004','PL!N-bp1-009',
    'PL!-pb1-006','PL!HS-pb1-027','PL!-bp6-016','PL!-pb1-016',
    'PL!N-bp1-011','PL!SP-pb1-017',
    'PL!-bp6-002','PL!S-bp6-005','PL!SP-bp5-013','PL!N-bp4-021',
    'PL!S-bp2-005',
]
for cn in targets:
    ci = _get_card(cards, cn)
    hits = []
    for ab in getattr(ci, 'abilities', []) or []:
        for cl in ab.get('clauses', []) or []:
            eff = str(cl.get('effect_template') or cl.get('raw') or '').strip()
            m = engine._match_effect_template(eff)
            if m:
                hits.append(m[0].get('id'))
    print(cn, getattr(ci, 'name', ''), hits)
PY
```

## Integrated current updates 20260714 debug対応

※ `docs/debug/loveca_debug_commands_current_updates_20260623.md` から移動。
※ 2026-07-14 デバッグ対応でコマンド形式を確認し、`DECK_CODE` wrapper 不使用、各 UI 起動コマンドの `cd` / `unset` 形式を確認済み。
※ `PL!N-bp3-025` の「必要ハート未達でも成功する」疑いは、内部再現では失敗判定。赤ハート6個追加後も `pink` / `yellow` / `any` 不足で `FAIL` になることを確認。
※ matcher 未実装残件: `<登場>` 366/366、`<ライブ開始時>` 291/291、`<ライブ成功時>` 118/118 で未マッチ 0。
※ 20260714再整理: 相手ステージ/相手選択に関わる効果は、相手側状態が未モデルのため手動確認ポップアップで扱う既定方針に従っていれば実装残件から外す。
※ 20260714再整理: 複数枚任意選択は既定の同時選択 UI があるため、`effect_notice` 手動案内のまま残っているものは実装残件として扱う。

残件分類 20260714:

方針どおりの手動確認扱い:

- `stage_only_group_opponent_front_position_notice`: 相手ステージのメンバーを正面へポジションチェンジ。相手ステージ未モデルのため確認ポップアップで手動処理。
- `opponent_named_member_compare_gain_blade_notice`: 相手ステージのメンバーとハート/コスト/元ブレード数を比較。相手ステージ未モデルのため確認ポップアップで手動確認。
- `green_distinct_live_names_opponent_choose_to_hand`: 自分が候補ライブを提示し、相手が1枚選ぶ。相手選択が未モデルのため確認ポップアップで手動選択。
- `ask_opponent_emma_punch` / `PL!N-PR-022` の回答分岐: 相手への質問・回答に依存するため確認ポップアップ扱い。
- `effect_notice` 系の相手効果によるアクティブ/ウェイト制限: 継続効果の制限を明示する通知扱い。

実装残件（20260714 residual 実装前の棚卸し。下記7件は `Integrated current updates 20260714 residual enter route implementation` で対応済み）:

- `discard_hand_group_members_any_draw_plus_one`: 手札から同グループメンバーを任意枚数控え室に置き、その枚数+1ドロー。既存の hand multi-select pending へ接続済み。
- `green_live_count_optional_discard_retrieve_member_and_live`: 任意手札コスト後、メンバーとライブを別条件で同時回収。手札複数コスト UI と二段回収 pending へ接続済み。
- `green_members_cost_sum_le_to_stage`: 控え室からコスト合計上限つきで複数メンバーをステージへ登場。既存の複数選択 UI と空きエリア自動配置へ接続済み。
- `success_group_live_swap_with_green_group_live`: 成功ライブ置き場の指定グループLIVEと控え室LIVEの入れ替え。成功置き場選択 pending へ接続済み。
- `success_zone_card_to_hand_then_revealed_to_success`: 成功ライブ置き場から手札に加え、公開カードを成功置き場へ置く。公開カード文脈と成功置き場選択 pending へ接続済み。
- `green_member_cost_le_group_use_enter_ability`: 控え室のカードの `<登場>` 能力を使用する。控え室カードを発生源にして既存 auto trigger 解決へ流す経路へ接続済み。
- `green_member_from_context_to_former_area`: 直前に控え室へ置いたメンバーと元エリアの対応がある場合は自動復元、文脈がない場合のみ確認表示。

現在の監査結果（20260714 debug対応で再確認）:

- matcher 未実装は 0。
- trigger 別の通知扱いは `<登場>` 8件、`<ライブ開始時>` 1件、`<ライブ成功時>` 1件。
- 通知扱いの内訳は、相手ステージ未モデル、相手選択/質問、双方同時移動、相手ライブ開始時への継続制限、勝敗処理時の成功置き場制限など。これらは residual enter route 実装残件からは外し、個別に UI/対戦相手モデルを拡張する時の対象として扱う。

## Integrated current updates 20260714 residual enter route implementation

※ `docs/debug/loveca_debug_commands_current_updates_20260623.md` から移動。
※ 20260714 residual実装で、残っていた generic enter route を実処理へ接続済み。

### 2026-07-14 residual enter route implementation

実装メモ:

- 複数枚任意手札破棄を既存の hand multi-select pending へ接続し、捨てた枚数+N のドローを自動処理。
- 手札2枚任意破棄後のメンバー/LIVE二段回収を、手札 multi-select と既存控え室回収 pending へ接続。
- 控え室からコスト合計上限つき複数メンバー登場を、複数選択 UI と空きエリア自動配置へ接続。
- 成功ライブ置き場から手札、公開カードを成功置き場へ置く経路を専用 pending へ接続。
- 成功ライブ置き場LIVEと控え室LIVEの入れ替えを専用 pending へ接続。
- 控え室メンバーの `<登場>` 能力使用を、控え室カードを発生源とする効果解決へ接続。
- 直前に控え室へ置いたメンバーを元エリアへ戻す効果は、文脈がある場合に自動復元し、文脈がない場合のみ確認表示。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

内部スモーク確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
import random
from llocg_ui import engine
from llocg_ui.db import load_cards_db

cards = load_cards_db(Path('.'))
rng = random.Random(1)

def assert_pending(gs, kind):
    assert gs.pending and gs.pending[0].get('kind') == kind, (kind, gs.pending, gs.log[-5:])

# 手札の同グループメンバーを任意枚数捨て、その枚数+1ドロー
gs = engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.hand = ['PL!HS-PR-005', 'PL!HS-PR-006', 'PL!N-PR-004']
gs.deck = ['LL-bp5-001', 'PL!HS-pb1-004', 'PL!HS-pb1-005', 'PL!HS-pb1-006']
engine.try_apply_effect_template(gs, rng, cards, "手札の『みらくらぱーく！』のメンバーカードを好きな枚数控え室に置き、その後、その枚数に1を足した枚数のカードを引く。", {'source_cn': 'PL!HS-pb1-003'})
assert_pending(gs, 'choose_member_from_green_multi_up_to')
engine.cmd_resolve_pending(gs, cards, 0, 'PL!HS-PR-005,PL!HS-PR-006', rng)
assert 'LL-bp5-001' in gs.hand and 'PL!HS-PR-005' in gs.green_room

# 任意手札破棄後、メンバーとLIVEを二段回収
gs = engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.hand = ['PL!N-PR-004', 'PL!N-PR-003']
gs.green_room = ['PL!HS-PR-014', 'PL!HS-PR-010', 'PL!HS-PR-011', 'PL!HS-PR-012']
engine.try_apply_effect_template(gs, rng, cards, "自分の控え室にライブカードが3枚以上ある場合、手札を2枚控え室に置いてもよい。そうした場合、自分の控え室から『スリーズブーケ』のメンバーカード1枚と『蓮ノ空』のライブカード1枚を手札に加える。", {'source_cn': 'PL!HS-pb1-020'})
assert_pending(gs, 'choose_member_from_green_multi_up_to')
engine.cmd_resolve_pending(gs, cards, 0, 'PL!N-PR-004,PL!N-PR-003', rng)
assert_pending(gs, 'choose_member_from_green')
engine.cmd_resolve_pending(gs, cards, 0, 'PL!HS-PR-014', rng)
assert gs.pending

# 成功置き場LIVEと控え室LIVEの入れ替え
gs = engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.success_zone = ['PL!N-bp1-025']
gs.green_room = ['PL!N-bp1-026', 'PL!HS-bp1-019']
engine.try_apply_effect_template(gs, rng, cards, "自分の成功ライブカード置き場にある『虹ヶ咲』のライブカードを1枚控え室に置いてもよい。そうした場合、自分の控え室にある『虹ヶ咲』のライブカードを1枚成功ライブカード置き場に置く。", {'source_cn': 'PL!N-bp4-010'})
assert_pending(gs, 'choose_success_group_live_for_swap')
engine.cmd_resolve_pending(gs, cards, 0, 'PL!N-bp1-025', rng)
assert_pending(gs, 'choose_green_live_to_success_zone')
engine.cmd_resolve_pending(gs, cards, 0, 'PL!N-bp1-026', rng)
assert gs.success_zone == ['PL!N-bp1-026']

# 成功置き場から手札、公開カードを成功置き場へ
gs = engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.success_zone = ['PL!-sd1-005']
gs.resolve_zone = ['PL!-sd1-006']
setattr(gs, '_yell_revealed_this_live', ['PL!-sd1-006'])
engine.try_apply_effect_template(gs, rng, cards, '自分の成功ライブカード置き場にあるカードを1枚手札に加える。そうした場合、これにより公開したカードを自分の成功ライブカード置き場に置く。', {'source_cn': 'PL!-sd1-006'})
assert_pending(gs, 'choose_success_to_hand_then_revealed_success')
engine.cmd_resolve_pending(gs, cards, 0, 'PL!-sd1-005', rng)
assert gs.hand == ['PL!-sd1-005'] and gs.success_zone == ['PL!-sd1-006']

# 控え室メンバーの登場能力を使用
gs = engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.green_room = ['PL!N-PR-004']
gs.deck = ['PL!N-bp1-001', 'PL!N-bp1-002', 'PL!N-bp1-003', 'PL!N-bp1-004']
engine.try_apply_effect_template(gs, rng, cards, "自分の控え室にあるコスト4以下の『虹ヶ咲』のメンバーカードを1枚選ぶ。そのカードの<登場>能力1つを使用する。", {'source_cn': 'PL!N-bp3-003'})
assert_pending(gs, 'choose_green_member_enter_ability_source')
engine.cmd_resolve_pending(gs, cards, 0, 'PL!N-PR-004', rng)
assert_pending(gs, 'choose_from_topk')

print('residual enter route smoke OK')
PY
```


### 20260713f live-start stage icon required-heart reductions

### 2026-07-14 enter generic route audit completion

実装メモ:

- 現行 `cards_compiled_v7h.json` 基準で <登場> clauses 366件を matcher 監査し、未マッチ 0 件まで更新。
- 相手状態・相手選択・成功ライブ置き場入れ替えなど未モデル領域を含む文型は、共通の確認ポップアップへ接続。
- 自分側だけで処理できるものは既存の控え室選択、手札登場、ポジションチェンジ、ドロー処理へ接続。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py
```

#### PL!-bp6-005 heart-member / required-live retrieve up to

確認観点:

- 控え室の<黄>を持つメンバーと、必要ハートに<黄>を含むライブが候補に出る。
- 「まで」回収なので skip/done 相当で少ない枚数でも終了できる。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!-bp6-005'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_GREEN='PL!-bp6-006,PL!-bp6-001,PL!-bp5-001,PL!N-bp5-010'
export LLOCG_START_DECK_EXACT='PL!-bp6-002,PL!-bp6-003,PL!-bp6-004,PL!-bp6-007,PL!-bp6-008,PL!-bp6-009'
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `PL!-bp6-005` は `choose_any_from_green` pending を生成し、控え室から<黄>を持つメンバー/必要ハートに<黄>を含むLIVEの候補だけを最大2枚まで回収できることを確認。pending は `source_cn=PL!-bp6-005` を保持し、skip/少数終了可能な optional 経路。

#### PL!-pb1-018 both players green member to empty WAIT

確認観点:

- 自分側の控え室からコスト2以下メンバーを選び、空きエリアにウェイト状態で登場できる。
- 相手側処理は未モデルのため、確認ログ/ポップアップで手動処理が案内される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!-pb1-018'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!-pb1-030'
export LLOCG_START_GREEN='PL!-PR-014,PL!-bp4-020,PL!-bp4-024'
export LLOCG_START_DECK_EXACT='PL!-bp4-013,PL!-bp3-020,PL!-bp4-021,LL-bp5-001,PL!-bp4-004,PL!-bp4-005'
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: 元コマンドの控え室 `PL!-pb1-030,PL!-bp4-020,PL!-bp4-024` はすべてLIVEで、コスト2以下メンバー候補が存在しなかったため不備。`PL!-PR-014`（コスト2メンバー）へ差し替え、`green_member_to_empty_area` pending から空きエリアへ WAIT 登場することを確認。途中で `both_players_green_member_cost_le_to_empty_wait` が未定義 `_apply_effect_rule` を呼ぶ runtime バグを検出し、汎用 dispatcher `_apply_effect_by_rule` に修正。

#### PL!SP-pb1-003 stage-only group rotate positions

確認観点:

- ステージが『5yncri5e!』のみの場合、自分の配置が C→L、L→R、R→C に移動する。
- 相手側の同処理は未モデルのため、確認ポップアップで手動処理が案内される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-pb1-003'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!SP-pb1-006'
export LLOCG_START_STAGE_C='PL!SP-pb1-003'
export LLOCG_START_DECK_EXACT='PL!SP-pb1-004,PL!SP-pb1-005,PL!SP-pb1-006,PL!SP-pb1-007,PL!SP-pb1-008,PL!SP-pb1-009'
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: 元コマンドの `PL!SP-pb1-001` / `PL!SP-pb1-002` は現行DBで 5yncri5e! ではなく、条件確認にならなかったため不備。ステージを 5yncri5e! のみに差し替え、C→L / L→R / R→C の自分側移動と、相手側手動処理の `effect_notice` を確認。

### 2026-07-14 enter generic route audit additions

#### PL!-PR-015 enter baton lower-cost member into hand-stage entry

確認観点:

- 低コストメンバーからバトンタッチして登場した場合、手札からコスト4以下メンバーを空きエリアへ登場させる選択UIが出る。
- バトンタッチ条件 wrapper は元メンバーのコストを見て処理される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!-bp4-003'
export LLOCG_START_HAND='PL!-PR-015,PL!-bp4-004'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!-bp4-001,PL!-bp4-002,PL!-bp4-004,PL!-bp4-006,PL!-bp4-007,PL!-bp4-008,PL!-bp4-009,PL!-bp4-010'
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: 元コマンドの `PL!-bp4-005` は現行DBでコスト13のため「コスト4以下メンバー」候補にならず不備。`PL!-bp4-004`（コスト2メンバー）へ差し替え、低コストメンバーからのバトンタッチ後に `hand_member_to_empty_area` pending が出て、空きエリアへ登場できることを確認。

#### PL!HS-PR-036 enter waiting-room count deficit mill and topdeck LIVE

確認観点:

- 控え室が8枚未満の場合、差分だけ山札上から控え室へ置く。
- これにより置いたカード内のライブカードをデッキ上へ置く選択UIが出る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-PR-036'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_GREEN='PL!HS-bp1-001,PL!HS-bp1-002'
export LLOCG_START_DECK_EXACT='PL!HS-bp6-025,PL!HS-bp1-003,PL!HS-bp1-004,PL!HS-bp1-005,PL!HS-bp1-006,PL!HS-bp1-007,PL!HS-bp1-008,PL!HS-bp1-009'
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: 控え室2枚から8枚へ不足分6枚をミルし、その中のLIVE `PL!HS-bp6-025` だけが `topdeck_from_green` 候補になることを確認。途中で `green_count_lt_mill_diff_topdeck_live_optional` が helper に未対応の `valid_cards` 引数を渡して落ちる runtime バグを検出し、`_enqueue_topdeck_from_green` に `valid_cards` 対応と `source_cn` / `display_cards` 付与を追加。これにより発生源付きで、ミルしたLIVEだけをカードリスト候補として表示できる。

### 2026-07-14 live-success generic route audit additions

#### LL-bp5-001 live success revealed LIVE / stage heart kinds / moved fallback

確認観点:

- エール公開にライブカードが2枚以上ある場合、このカードのスコア+1が入る。
- 条件未達時はステージのハート種類数とエリア移動条件の手動確認に落ちる。
- 文型はカード番号専用ではなく、ライブ成功時の複合 OR 条件として処理される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!N-bp4-002'
export LLOCG_START_DECK_EXACT='PL!N-bp4-003,PL!S-bp6-023,PL!HS-sd1-017,PL!N-bp3-030,PL!S-bp3-020,PL!SP-bp4-006,PL!-bp6-007,PL!N-bp5-007'
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: エール公開 LIVE 2枚以上の履歴では `LL-bp5-001` のスコア+1が自動適用され、条件未達の履歴では `confirm_effect` pending に落ちることを内部 smoke で確認。pending には `source_cn=LL-bp5-001` と実行中効果文が入り、エール公開条件・ステージハート種類数・移動履歴条件の OR を同一の汎用 route で扱っている。

#### PL!-bp6-001 live success no-bladeheart revealed member draw-discard

確認観点:

- エール公開にブレードハートを持たない指定グループのメンバーカードがある場合、既存テンプレート経由で1ドロー後に手札1枚控え室選択が出る。
- ブレードハート持ちだけを公開した場合は解決されない。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!-bp6-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!-bp6-003'
export LLOCG_START_DECK_EXACT='LL-bp3-001,PL!-bp6-005,PL!-bp6-006,PL!-bp6-007,PL!-bp6-008,PL!-bp6-009,PL!-bp6-010,PL!-bp6-011'
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `LL-bp3-001` をエール公開履歴に入れた smoke で、ブレードハートを持たない μ's メンバーのみ条件達成し、1ドロー後に `discard_from_hand` pending が発生することを確認。発生源 `PL!-bp6-001` と実行中効果文が pending に入り、無言処理にはなっていない。元コマンドの先頭候補は条件確認用として弱かったため、山札先頭を no-bladeheart μ's MEMBER に差し替えた。

#### PL!SP-pb2-004 live success revealed score icon or success-zone above-original draw

確認観点:

- エール公開に<スコア+1>を持つライブカードがある場合、カードを1枚引く。
- 公開条件がない場合は、成功ライブカード置き場の元スコア超過条件を手動確認する。
- `<スコア+1>` と `<(スコア+1)>` の表記差を同じタグとして扱う。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-pb2-004'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!SP-pb2-001'
export LLOCG_START_DECK_EXACT='LL-bp5-001,PL!SP-pb2-005,PL!SP-pb2-006,PL!SP-pb2-007,PL!SP-pb2-008,PL!SP-pb2-009,PL!SP-pb2-010,PL!SP-pb2-011'
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `<スコア+1>` LIVE として `LL-bp5-001` をエール公開履歴に入れた smoke で、`PL!SP-pb2-004` が1ドローを行い pending を残さず解決することを確認。元コマンドの `PL!SP-bp5-023` は draw+1 LIVE であり `<スコア+1>` 条件の確認カードとして不適だったため差し替えた。成功置き場超過側は手動確認 fallback になる実装で、公開されたカード条件とは混同されていない。

#### LL-PR-004 favorite answer manual outcome

確認観点:

- ライブ開始時に相手の回答を選ぶ pending が出る。
- 「あなた」は自分が1枚ドローする。相手のドローは手動ログ扱い。
- 「それ以外」は自分のステージメンバー全員がライブ終了時まで<(ブレード)>を得る。相手ステージぶんは手動ログ扱い。
- 指定フレーバー回答は自分の手札1枚を控え室に置く選択に進む。相手の手札破棄は手動ログ扱い。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='LL-PR-004,PL!N-bp1-003'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!N-bp1-003'
export LLOCG_START_STAGE_C='PL!N-bp1-004'
export LLOCG_START_STAGE_R='PL!N-bp1-006'
export LLOCG_START_DECK_EXACT='PL!N-bp1-007,PL!N-bp1-008,PL!N-bp1-009,PL!N-bp1-010,PL!N-bp1-011,PL!N-bp1-012,PL!N-bp1-013,PL!N-bp1-014'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: ライブ開始時に `favorite_icecream_answer` pending が発生し、選択肢が「チョコミント/ストロベリー/クッキー」「あなた」「それ以外」「skip」だけに限定されることを確認。各分岐は発生源 `LL-PR-004` の pending から手動結果を選ぶ形で、相手側処理はログ明記、自分側処理は draw / blade 付与 / 手札控え室選択へ進む設計になっている。自動効果の無言処理ではない。

#### PL!N-pb1-009 manual previous live-zone no-bladeheart member condition

確認観点:

- 条件履歴は現在の環境変数だけでは確定できないため、Apply / Skip の確認 pending が出る。
- Apply 時、カードを1枚引き、発生源がライブ終了時まで<黄><青><紫>を得る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!N-pb1-009'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!N-bp1-003'
export LLOCG_START_DECK_EXACT='PL!N-bp1-004,PL!N-bp1-005,PL!N-bp1-006,PL!N-bp1-007,PL!N-bp1-008,PL!N-bp1-009,PL!N-bp1-010,PL!N-bp1-011'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `manual_draw_gain_icons_self` pending で Apply / Skip が表示され、Apply 後に1ドローし、発生源のライブ終了時まで `yellow/blue/purple` ハートが付与されることを確認。前回ライブゾーン条件は開始環境変数だけで断定しない手動確認 route で、発生源と実行中効果文を保持している。

#### PL!N-pb1-037 manual Nijigasaki activation history condition

確認観点:

- このターン中の「虹ヶ咲効果でエネルギー/ステージメンバーをアクティブにした」履歴は手動確認 pending で選ぶ。
- Energy only はこのカードのスコア+1。
- Energy and stage member は代わりにスコア+2。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!N-pb1-037'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!N-bp1-003'
export LLOCG_START_STAGE_C='PL!N-bp1-004'
export LLOCG_START_STAGE_R='PL!N-bp1-006'
export LLOCG_START_DECK_EXACT='PL!N-bp1-007,PL!N-bp1-008,PL!N-bp1-009,PL!N-bp1-010,PL!N-bp1-011,PL!N-bp1-012,PL!N-bp1-013,PL!N-bp1-014'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `manual_nijigasaki_activation_score` pending で Energy only / Energy and stage member / Skip を選べることを確認。Energy only はスコア+1、Energy and stage member はスコア+2として `live_start_score_bonus_by_set_idx` に反映される。履歴条件をカード番号専用 state にせず、手動確認 pending で汎用的に扱っている。

#### PL!HS-pb1-025 waiting room group member count then stage group member gains heart

確認観点:

- 控え室の『蓮ノ空』メンバーカードが10枚以上ある場合のみ発動する。
- ステージの『蓮ノ空』メンバー1人を選び、ライブ終了時まで<緑>を得る。
- 対象候補が複数いる場合は選択UIが出る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-pb1-025'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!HS-bp1-002'
export LLOCG_START_STAGE_C='PL!HS-bp1-003'
export LLOCG_START_STAGE_R='PL!HS-bp1-004'
export LLOCG_START_GREEN='PL!HS-bp2-001,PL!HS-bp2-007,PL!HS-bp5-008,PL!HS-bp6-005,PL!HS-bp6-008,PL!HS-bp6-010,PL!HS-bp6-013,PL!HS-cl1-002,PL!HS-pb1-018,PL!HS-pb1-021'
export LLOCG_START_DECK_EXACT='PL!HS-bp1-005,PL!HS-bp1-006,PL!HS-bp1-007,PL!HS-bp1-008,PL!HS-bp1-009,PL!HS-bp1-010,PL!HS-bp1-011,PL!HS-bp1-012'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: 控え室に蓮ノ空 MEMBER 10枚を置いた状態で、ステージの蓮ノ空メンバー候補を選ぶ pending が出て、選択したメンバーへライブ終了時まで `<緑>` が付与されることを確認。候補なし・条件不足を無言で流すのではなく、既存のステージ対象選択 route を経由している。

#### PL!N-bp3-008 activate other wait member then both gain green

確認観点:

- 起動後、手動でこのメンバー以外のステージメンバーをウェイト状態にしてからライブ開始時能力を確認する。
- ウェイト状態のほかのメンバー1人をアクティブにし、選んだメンバーとこのメンバーがライブ終了時まで<緑>を得る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!N-bp1-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!N-bp1-003'
export LLOCG_START_STAGE_C='PL!N-bp3-008'
export LLOCG_START_STAGE_R='PL!N-bp1-004'
export LLOCG_START_DECK_EXACT='PL!N-bp1-005,PL!N-bp1-006,PL!N-bp1-007,PL!N-bp1-008,PL!N-bp1-009,PL!N-bp1-010,PL!N-bp1-011,PL!N-bp1-012'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: このメンバー以外のウェイトメンバーが1候補だけのとき、旧挙動では選択UIを出さず即時アクティブ化/緑付与していたため、1候補でも `activate_other_wait_then_both_gain_icons` pending を出すよう修正。再確認では pending に `source_cn=PL!N-bp3-008`、候補 `L`、実行中効果文が入り、選択後に対象メンバーと発生源の両方へ `<緑>` が付与された。

### 2026-07-14 LIVE_START generic route additions i

#### PL!N-bp4-027 success named EMOTION count score and required any increase

確認観点:

- 成功ライブカード置き場にあるカード名「EMOTION」1枚につき、このカードのスコアが+2される。
- 同じ枚数ぶん、成功させるための必要ハート<任意><任意><任意>が増える。
- 成功置き場が空の場合は未達としてスキップされる。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!N-bp4-027'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!N-bp1-003'
export LLOCG_START_STAGE_C='PL!N-bp1-004'
export LLOCG_START_STAGE_R='PL!N-bp1-006'
export LLOCG_START_SUCCESS='PL!N-bp4-027'
export LLOCG_START_DECK_EXACT='PL!N-bp1-007,PL!N-bp1-008,PL!N-bp1-009,PL!N-bp1-010,PL!N-bp1-011,PL!N-bp1-012,PL!N-bp1-013,PL!N-bp1-014'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: 効果文の必要ハート表記が `<任意>` のため、従来の `<(任意)>` 前提 parser では成功置き場の「EMOTION」枚数を拾えていなかった。`<任意>` / `<(任意)>` の表記揺れを同じ文型で数えるよう修正し、成功置き場1枚でスコア+2/必要任意+3、2枚でスコア+4/必要任意+6になることを確認。成功置き場3枚以上の初期状態は使っていない。

#### PL!HS-pb1-006 optional position change to other group member area then gain icons

確認観点:

- ほかの『みらくらぱーく！』メンバーがいるエリアだけが移動先候補になる。
- 移動を実行した場合、移動したメンバーがライブ終了時まで<桃><(ブレード)>を得る。
- skip を選ぶと移動とアイコン付与の両方を行わない。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-pb1-006'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!HS-bp2-005'
export LLOCG_START_STAGE_C='PL!HS-bp2-006'
export LLOCG_START_DECK_EXACT='PL!HS-bp1-009,PL!HS-bp2-009,PL!HS-bp6-003,PL!HS-bp6-004,PL!HS-bp6-005,PL!HS-bp6-006,PL!HS-bp6-007,PL!HS-bp6-008'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `PL!HS-pb1-006` はほかの『みらくらぱーく！』メンバーがいるエリアだけを候補にする pending を出し、skip では移動/付与なし、移動選択ではポジションチェンジ後の発生源に `<桃>` とブレード+1が入ることを確認。pending には発生源 `PL!HS-pb1-006` と効果文があり、任意処理を無言実行していない。

#### PL!S-bp5-023 Aqours and Saint Snow cost sum topdeck waiting room LIVE

確認観点:

- ステージに『Aqours』と『Saint Snow』のメンバーがいて、メンバーのコスト合計が20以上の場合のみ発動する。
- 控え室の『Aqours』/『Saint Snow』ライブカードを4枚まで、選んだ順番でデッキ上に置く。
- 2枚目以降の選択肢が対象グループのライブカードから広がらない。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!S-bp5-023'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!S-bp3-006'
export LLOCG_START_STAGE_C='PL!S-bp5-111'
export LLOCG_START_STAGE_R='PL!S-bp5-222'
export LLOCG_START_GREEN='PL!S-bp5-023,PL!S-bp5-020,PL!S-bp5-021,PL!S-bp5-019'
export LLOCG_START_DECK_EXACT='PL!S-bp5-001,PL!S-bp5-002,PL!S-bp5-003,PL!S-bp5-004,PL!S-bp5-005,PL!S-bp5-006,PL!S-bp5-007,PL!S-bp5-008'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: ステージ条件は Aqours/Saint Snow 両方あり、コスト合計28/20で達成することを確認。控え室候補は Aqours/Saint Snow の LIVE `PL!S-bp5-023`,`PL!S-bp5-020`,`PL!S-bp5-021` のみに絞られ、異種カードや未登録カードへ広がらない。検出時点では custom pending に `source_cn` が抜けていたため、`source_cn=PL!S-bp5-023`、`display_cards`、`valid_cards` を保持するよう修正済み。

### 20260714 Codex current updates: live-start condition batch

#### PL!SP-bp2-010 other stage member count reduces YELL reveal count

確認観点:

- 自分のステージにこのメンバー以外のメンバーが1人以上いる場合、ライブ終了時までエール公開枚数が8枚減る。
- 単独ステージでは減少しない。
- 既存のドローアイコン処理と併用しても、公開枚数補正はライブ中の同一参照値として扱われる。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-bp2-010'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!SP-PR-003'
export LLOCG_START_STAGE_C='PL!SP-PR-004'
export LLOCG_START_DECK_EXACT='PL!SP-bp2-001,PL!SP-bp2-002,PL!SP-bp2-003,PL!SP-bp2-004,PL!SP-bp2-005,PL!SP-bp2-006,PL!SP-bp2-007,PL!SP-bp2-008'
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: 他ステージメンバー1人ありで `yell_reveal_count_delta_this_live=-8`、単独ステージで0のままになることを内部 smoke で確認。成功/未達ともログだけでなく `message_ack` pending を出し、`source_cn=PL!SP-bp2-010` と条件達成/未達、エール公開枚数-8の結果を表示するよう修正。カード番号専用ではなく `live_start_yell_reveal_count_delta_if_other_stage_members_at_least` の汎用 route。

#### PL!HS-bp5-018 distinct stage names and costs score

確認観点:

- ステージに名前とコストが両方とも異なるメンバーが3人以上いる場合、このカードのスコアが+1される。
- 同名または同コストを混ぜた場合はスコア加算されない。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-bp5-018'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!HS-PR-014'
export LLOCG_START_STAGE_C='PL!HS-PR-003'
export LLOCG_START_STAGE_R='PL!HS-PR-007'
export LLOCG_START_DECK_EXACT='PL!HS-bp5-001,PL!HS-bp5-002,PL!HS-bp5-003,PL!HS-bp5-004,PL!HS-bp5-005,PL!HS-bp5-006,PL!HS-bp5-007,PL!HS-bp5-008'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: 元コマンドの `PL!HS-PR-001` / `PL!HS-PR-003` / `PL!HS-PR-005` はコスト種類が2種類しかなく、条件達成コマンドになっていなかった。`PL!HS-PR-014` / `PL!HS-PR-003` / `PL!HS-PR-007` に差し替え、メンバー3人・名前3種類・コスト3種類でスコア+1になることを確認。成功時も `message_ack` pending に発生源と達成内訳を表示するよう修正。

#### PL!N-bp5-026 all six heart colors score

確認観点:

- ステージ上のメンバーが持つハートに<桃><赤><黄><緑><青><紫>がすべてある場合、このカードのスコアが+1される。
- base hearts / blade hearts / temporary hearts / always hearts の現在値を参照する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!N-bp5-026'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!N-PR-003'
export LLOCG_START_STAGE_C='PL!N-PR-005'
export LLOCG_START_STAGE_R='PL!N-PR-019'
export LLOCG_START_DECK_EXACT='PL!N-bp5-001,PL!N-bp5-002,PL!N-bp5-003,PL!N-bp5-004,PL!N-bp5-005,PL!N-bp5-006,PL!N-bp5-007,PL!N-bp5-008'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: 元コマンドの `PL!N-PR-003` / `PL!N-PR-005` / `PL!N-PR-007` では黄ハートが不足し、条件未達 pending になることを確認。`PL!N-PR-019` を入れて六色すべてを揃える形へ差し替え、スコア+1と成功時 `message_ack` pending を確認。base / blade / temp / always を集計する既存ハート現在値 helper 経由で、カード番号専用ではない。

#### PL!SP-bp5-026 stage group heart total score

確認観点:

- 自分のステージにいる『Liella!』メンバーが持つハート総数が11以上の場合、このカードのスコアが+1される。
- ハート総数は現在値で集計される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-bp5-026'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!SP-pb1-001'
export LLOCG_START_STAGE_C='PL!SP-pb1-002'
export LLOCG_START_STAGE_R='PL!SP-PR-005'
export LLOCG_START_DECK_EXACT='PL!SP-bp5-001,PL!SP-bp5-002,PL!SP-bp5-003,PL!SP-bp5-004,PL!SP-bp5-005,PL!SP-bp5-006,PL!SP-bp5-007,PL!SP-bp5-008'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: 元コマンドの Liella! ステージはハート総数6/11で条件未達だった。`PL!SP-pb1-001` / `PL!SP-pb1-002` / `PL!SP-PR-005` に差し替え、Liella! ハート総数17/11でスコア+1になることを確認。成功/未達とも `message_ack` pending に発生源と集計値を表示するよう修正。

### 2026-07-14 live-start generic icon/required override additions

#### PL!SP-bp1-024 Tiny Stars named members gain icons

確認観点:

- ステージの「澁谷かのん」と「唐 可可」を名前表記揺れ込みで検出する。
- 「澁谷かのん」には<青>+ブレード、「唐 可可」には<桃>+ブレードがライブ終了時まで付く。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-bp1-024'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!SP-bp1-001'
export LLOCG_START_STAGE_C='PL!SP-bp1-002'
export LLOCG_START_DECK_EXACT='PL!SP-bp1-003,PL!SP-bp1-004,PL!SP-bp1-005,PL!SP-bp1-006,PL!SP-bp1-007,PL!SP-bp1-008'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: `PL!SP-bp1-001` の「澁谷かのん」と `PL!SP-bp1-002` の「唐 可可」を名前で検出し、それぞれ `<青>`+ブレード、`<桃>`+ブレードがライブ終了時まで付くことを確認。成功時がログだけだったため、`two_named_stage_members_gain_icons` 汎用 route で `source_cn=PL!SP-bp1-024` の `message_ack` pending を出し、指定名メンバーへの付与結果を表示するよう修正。

#### PL!HS-bp5-021 stage group original hearts all pink

確認観点:

- 『蓮ノ空』メンバーを選ぶ pending が出る。
- 選んだメンバーの元々持つハートがライブ終了時まで<桃>扱いになる。
- 『みらくらぱーく！』3人以上なら同じLIVEのスコア+1も維持される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-bp5-021'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!HS-bp5-003'
export LLOCG_START_STAGE_C='PL!HS-bp2-005'
export LLOCG_START_STAGE_R='PL!HS-PR-018'
export LLOCG_START_DECK_EXACT='PL!HS-bp5-001,PL!HS-bp5-002,PL!HS-bp5-004,PL!HS-bp5-005,PL!HS-bp5-006,PL!HS-bp5-007'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: 『蓮ノ空』メンバー3人が候補に出る `choose_stage_position_replace_original_hearts` pending を確認し、選択後に対象の `heart_replace_color=pink` / `temp_until=end_of_live` が入ることを確認。続く『みらくらぱーく！』3人条件は `stage group count -> this_card_score_plus` の汎用 route でスコア+1になり、内側の `this_card_score_plus` 成功時も発生源付き `message_ack` pending を出すよう修正した。

#### PL!N-bp5-007 same own/opponent success count gains red hearts

確認観点:

- 自分と相手の成功ライブカード置き場枚数が同じ場合、ソースが<赤><赤>を得る。
- 初期状態ではどちらも0枚なので条件達成として処理される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!N-bp5-007'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!N-bp5-001,PL!N-bp5-002,PL!N-bp5-003,PL!N-bp5-004,PL!N-bp5-005,PL!N-bp5-006'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: `opponent_success_count_same_gain_icons` の汎用 route で処理され、初期0/0枚条件でソース `PL!N-bp5-007` に `temp_hearts={'red': 2}` が入ることを確認。成功/未達ともログだけで終わらないよう、発生源付き `message_ack` pending を追加した。DECK_CODE、成功ライブ3枚以上初期状態、カード番号専用分岐はいずれもなし。

#### PL!SP-pb2-018 distinct CatChu names activate energy

確認観点:

- ソースと名前の異なる『CatChu!』メンバー数ぶん、ウェイトエネルギーがアクティブになる。
- 同名メンバーは数えない。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!SP-pb2-018'
export LLOCG_START_STAGE_L='PL!SP-bp1-001'
export LLOCG_START_STAGE_R='PL!SP-PR-003'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!SP-bp1-002,PL!SP-bp1-003,PL!SP-bp1-004,PL!SP-bp1-005,PL!SP-bp1-006,PL!SP-bp1-007'
export LLOCG_START_ENERGY_ACTIVE=0
export LLOCG_START_ENERGY_WAIT=6
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: `distinct_stage_group_member_energy_activate` の汎用 route で処理され、同名の澁谷かのん2枚は1種類として数え、ウェイトエネルギー6枚中1枚だけがアクティブ化されることを確認。処理結果が無言にならないよう、発生源付き `message_ack` pending を追加した。

#### PL!S-bp5-016 opponent cost comparison manual confirmation

確認観点:

- 相手ステージとのコスト比較は手動確認ポップアップで処理する。
- 「条件達成」を押すとソースがブレード2つを得る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!S-bp5-016'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!S-bp5-001,PL!S-bp5-002,PL!S-bp5-003,PL!S-bp5-004,PL!S-bp5-005,PL!S-bp5-006'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `stage_higher_than_all_opponent_cost_gain_icons` の汎用 route で `manual_condition_gain_icons_to_source` pending が出ることを確認。pending には `source_cn=PL!S-bp5-016`、実行中効果のみの確認文、選択肢 `条件達成/条件未達` が入り、`条件達成` 解決でソースの `temp_blade=2` になる。相手ステージ未モデル部分は手動確認に留めており、カード番号専用分岐なし。

### 2026-07-14 live-start required color reduction and formation additions

#### PL!HS-bp5-022 Retrofuture choose option required purple reduction

確認観点:

- ステージにコスト9以上の『Edel Note』メンバーがいる状態で、選択肢効果として必要ハート<紫>を1つ減らせる。
- 「以下から1つを選ぶ。」見出し自体は実処理せず、選択肢の実効果だけを処理対象にする。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-bp5-022'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!HS-PR-023'
export LLOCG_START_GREEN='PL!HS-bp5-008,PL!HS-bp5-015'
export LLOCG_START_DECK_EXACT='PL!HS-PR-022,PL!HS-bp5-007,PL!HS-bp5-016,PL!HS-bp6-032'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: 選択肢の必要ハート<紫>軽減は `this_live_required_color_reduction` の汎用 route で処理され、`live_start_required_color_reduction_by_set_idx={0: {'purple': 1}}` が入ることを確認。適用結果がログだけで終わらないよう、発生源付き `message_ack` pending を追加した。見出し効果は既存の noop/選択肢経路に留め、対象カード番号専用分岐はなし。

#### PL!SP-pb2-050 stage group count optional formation change

確認観点:

- ステージに『5yncri5e!』メンバーが2人以上いる場合、フォーメーションチェンジ対象選択UIが出る。
- 実体は既存のポジションチェンジUIを使う。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-pb2-050'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!SP-bp1-003'
export LLOCG_START_STAGE_C='PL!SP-bp1-006'
export LLOCG_START_STAGE_R='PL!SP-bp1-008'
export LLOCG_START_DECK_EXACT='PL!SP-bp4-024,PL!SP-bp4-004,PL!SP-bp4-007,PL!SP-pb1-001'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: `stage_group_count_formation_change_optional` の汎用 route で、5yncri5e! メンバー3/2人条件達成後に既存の `choose_stage_member_to_position_change_source` pending が出ることを確認。選択 `L` → 移動先 `R` でステージ入れ替えまで確認済み。条件未達/対象なしも無言終了しないよう `message_ack` pending を追加した。

#### PL!SP-sd2-001 draw then optional formation change

確認観点:

- カードを1枚引いた後、任意でステージメンバーをフォーメーションチェンジできる。
- フォーメーションチェンジしない場合はスキップできる。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-sd2-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!SP-bp1-003'
export LLOCG_START_STAGE_C='PL!SP-bp1-006'
export LLOCG_START_STAGE_R='PL!SP-bp1-008'
export LLOCG_START_DECK_EXACT='PL!SP-bp4-024,PL!SP-bp4-004,PL!SP-bp4-007,PL!SP-pb1-001'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `draw_then_optional_stage_member_position_change` の汎用 route でデッキ上1枚を引いた後、発生源 `PL!SP-sd2-001` 付きの任意フォーメーションチェンジ pending が出ることを確認。`skip` 選択も可能。カード番号専用分岐なし。

### 2026-07-14 live-start cost sum / required color / source icon additions

#### PL!HS-bp6-029 stage group cost sum look top and required any reduction

確認観点:

- ステージの『蓮ノ空』メンバーのコスト合計が20以上ならデッキ上2枚から1枚を手札に加え、残りをデッキ上に戻す。
- コスト合計が30以上なら、さらに必要ハート<(任意)>が2つ減る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-bp6-029'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!HS-PR-001'
export LLOCG_START_STAGE_C='PL!HS-PR-002'
export LLOCG_START_STAGE_R='PL!HS-PR-005'
export LLOCG_START_DECK_EXACT='PL!HS-PR-006,PL!HS-PR-007,PL!HS-PR-008,PL!HS-PR-009'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `live_start_stage_group_cost_sum_top_hand_rest_top_then_required_any` の汎用 live-start trigger で処理されることを確認。提示コマンドの蓮ノ空3人はコスト合計30なので、デッキ上2枚から1枚を手札に加え、残りをデッキ上に戻し、`live_start_required_any_reduction_by_set_idx={0: 2}` が入る。pending には `source_cn=PL!HS-bp6-029` とコスト合計30の説明が入る。カード番号専用分岐なし。

#### PL!S-bp5-013 live storage green required sum gains green

確認観点:

- ライブカード置き場の必要ハートに含まれる<緑>が合計4以上なら、ステージのこのメンバーが<緑>を得る。
- 「ライブカード置き場にあるカード」と「ライブ中のライブカード」の文面差を同じ文型で扱う。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!S-bp2-026'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!S-bp5-013'
export LLOCG_START_DECK_EXACT='PL!S-bp3-019,PL!S-bp6-021,PL!S-bp5-019,PL!S-pb1-023'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: `live_zone_required_color_sum_gain_heart` の汎用 route で、ライブカード置き場の `PL!S-bp2-026` の必要ハート<緑>6を参照し、閾値4達成でソース `PL!S-bp5-013` が `temp_hearts={'green': 1}` を得ることを確認。成功/未達とも無言処理にならないよう、発生源付き `message_ack` pending を追加した。

#### PL!SP-PR-009 discard live then blade and draw

確認観点:

- 手札1枚を控え室に置く任意コスト後、このメンバーがブレード+1を得る。
- これによりライブカードを控え室に置いた場合、さらにカードを1枚引く。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-bp1-026,PL!SP-bp2-010'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!SP-PR-009'
export LLOCG_START_DECK_EXACT='PL!SP-bp4-024,PL!SP-bp4-004,PL!SP-bp4-007,PL!SP-pb1-001'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: ライブ開始時の自動効果順序ポップアップから該当効果を選ぶと、`discard_from_hand` pending にコスト候補と発生源 `PL!SP-PR-009` が出ることを確認。ライブカード `PL!SP-bp1-026` を捨てると、後続効果へ `discarded_cn` が渡り、ソースがブレード+1、さらに1ドローになる。後続効果の結果もログだけで終わらないよう、発生源付き `message_ack` pending を追加した。

#### PL!HS-bp6-004 discard named member then extra blade

確認観点:

- 手札1枚を控え室に置く任意コスト後、このメンバーがブレード+1を得る。
- これにより「百生吟子」のメンバーカードを控え室に置いた場合、さらにブレード+1を得る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-bp6-029,PL!HS-bp6-004'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!HS-bp6-004'
export LLOCG_START_DECK_EXACT='PL!HS-PR-001,PL!HS-PR-002,PL!HS-PR-005,PL!HS-PR-006'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: ライブ開始時の自動効果順序ポップアップでは、相手ステージ手動効果と手札コスト効果が別選択肢として出る。手札コスト効果を選ぶと `discard_from_hand` pending にコスト候補と発生源 `PL!HS-bp6-004` が出ることを確認。手札の `PL!HS-bp6-004` を捨てると `discarded_cn` から「百生吟子」メンバーカード判定が成立し、ソースが合計ブレード+2を得る。後続効果の結果もログだけで終わらないよう、発生源付き `message_ack` pending を追加した。

#### PL!S-pb1-003 original hearts become green

確認観点:

- エネルギーを支払って効果を使うと、このメンバーが元々持つハートがライブ終了時まで全て<緑>として扱われる。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!S-bp2-026'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!S-pb1-003'
export LLOCG_START_DECK_EXACT='PL!S-bp3-019,PL!S-bp6-021,PL!S-bp5-019,PL!S-pb1-023'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: `replace_original_hearts_all_one_color` の汎用 route で処理され、ソース `PL!S-pb1-003` の `heart_replace_color='green'` / `temp_until=end_of_live` が入ることを確認。適用結果が無言にならないよう、発生源付き `message_ack` pending を追加した。カード番号専用分岐なし。

#### PL!SP-bp2-009 hand count blade gain

確認観点:

- 自分の手札2枚につき、このメンバーがブレード+1を得る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-bp1-026,PL!SP-bp1-008,PL!SP-bp2-001,PL!SP-bp4-004,PL!SP-bp4-007'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!SP-bp2-009'
export LLOCG_START_DECK_EXACT='PL!SP-bp4-024,PL!SP-pb1-001,PL!SP-pb2-005,PL!SP-sd2-001'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: `hand_count_div_gain_blades_until_end_live` の汎用 route で、手札5枚を2で割った切り捨て分としてソース `PL!SP-bp2-009` がブレード+2を得ることを確認。結果がログだけで終わらないよう、発生源付き `message_ack` pending を追加した。

#### PL!S-sd1-004 optional draw then hand top

確認観点:

- 任意でカードを1枚引き、そうした場合は手札2枚を好きな順番でデッキの上に置く。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!S-bp2-026,PL!S-sd1-001,PL!S-sd1-002'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!S-sd1-004'
export LLOCG_START_DECK_EXACT='PL!S-bp3-019,PL!S-bp6-021,PL!S-bp5-019,PL!S-pb1-023'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `optional_draw_then_hand_top` の汎用 route で `confirm_effect` pending が出て、`使う` 解決後に1ドローし、`hand_to_deck_top` pending で手札2枚を1枚ずつ選んで山札上に戻せることを確認。順番は選択順で作られ、例では `PL!S-bp2-026` → `PL!S-sd1-001` の順に選ぶと山札上が `PL!S-sd1-001, PL!S-bp2-026` になる。発生源 `PL!S-sd1-004` は後続 pending に保持される。

#### PL!SP-bp4-025 center original blade count becomes 3

確認観点:

- センターエリアの『Liella!』メンバーが元々持つブレード数が、ライブ終了時まで3つとして扱われる。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-bp4-025'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!SP-bp4-007'
export LLOCG_START_DECK_EXACT='PL!SP-bp4-024,PL!SP-bp4-004,PL!SP-pb1-001,PL!SP-pb2-005'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: `center_group_original_blade_count_set` の汎用 route で、センターの『Liella!』メンバー `PL!SP-bp4-007` の元々のブレード1を3として扱うため `temp_blade=2` / `temp_until=end_of_live` が入ることを確認。結果がログだけで終わらないよう、発生源付き `message_ack` pending を追加した。

### 2026-07-13 live-start generic score / required / blade condition additions

#### PL!HS-bp2-024 named cost comparison reduces required any

確認観点:

- 「村野さやか」よりコストの大きい「徒町小鈴」がステージにいる場合、必要ハート<(任意)>が3つ減る。
- カード番号固定ではなく、名前2種のコスト比較文型として処理される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-bp2-024'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!HS-PR-008'
export LLOCG_START_STAGE_C='PL!HS-PR-002'
export LLOCG_START_DECK_EXACT='PL!HS-PR-001,PL!HS-PR-003,PL!HS-PR-004,PL!HS-PR-005,PL!HS-PR-006'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: DB効果文は「徒町小鈴」よりコストの大きい「村野さやか」が条件で、確認観点の記述とは大小関係が逆。`live_start_required_any_reduction_if_named_member_cost_greater` の汎用 route で、`PL!HS-PR-008` 徒町小鈴コスト9 / `PL!HS-PR-002` 村野さやかコスト10を比較し、発生源付き `live_start_required_any_reduction_ack` pending が出ることを確認。`ok` 解決で `live_start_required_any_reduction_by_set_idx={0: 3}` が保存される。カード番号専用分岐なし。

#### PL!HS-pb1-026 stage plus green distinct Hasunosora names reduce required any

確認観点:

- ステージと控え室に名前の異なる『蓮ノ空』メンバーが6人以上いる場合、必要ハート<(任意)>が2つ減る。
- ステージと控え室を合わせて名前重複を除外して数える。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-pb1-026'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!HS-PR-001'
export LLOCG_START_STAGE_C='PL!HS-PR-002'
export LLOCG_START_STAGE_R='PL!HS-PR-003'
export LLOCG_START_GREEN='PL!HS-PR-005,PL!HS-PR-006,PL!HS-PR-007'
export LLOCG_START_DECK_EXACT='PL!HS-PR-008,PL!HS-PR-009,PL!HS-bp5-017,PL!HS-bp2-024'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: `live_start_required_any_reduction_if_stage_green_distinct_group_member_names_at_least` の汎用 route で、ステージ3人 + 控え室3人の名前の異なる『蓮ノ空』メンバー6/6人を数え、発生源付き `live_start_required_any_reduction_ack` pending が出ることを確認。名前重複除外は `_stage_and_green_distinct_group_member_name_count` を通る。

#### PL!N-pb1-042 same-name Nijigasaki members reduce required any

確認観点:

- ステージに同じ名前の『虹ヶ咲』メンバーが3人以上いる場合、必要ハート<(任意)>が3つ減る。
- 同名最大数で判定する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!N-pb1-042'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!N-PR-003'
export LLOCG_START_STAGE_C='PL!N-bp1-001'
export LLOCG_START_STAGE_R='PL!N-bp3-013'
export LLOCG_START_DECK_EXACT='PL!N-bp1-027,PL!N-bp3-004,PL!N-bp3-005,PL!N-PR-025'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714内部確認: DB効果文は「同じ名前の『虹ヶ咲』メンバーが2人以上」で、確認観点の3人以上は誤記。提示コマンドでは上原歩夢3人なので条件は3/2で達成し、`live_start_required_any_reduction_if_same_name_stage_group_members_at_least` の汎用 route から発生源付き `live_start_required_any_reduction_ack` pending が出ることを確認。同名最大数で判定しており、カード番号専用分岐なし。

#### PL!HS-bp2-026 exact named positions score plus

確認観点:

- 右サイド「大沢瑠璃乃」/ 左サイド「安養寺姫芽」/ センター「藤島慈」が揃うとスコア+2。
- 位置と名前の両方を確認する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-bp2-026'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!HS-PR-009'
export LLOCG_START_STAGE_C='PL!HS-PR-006'
export LLOCG_START_STAGE_R='PL!HS-PR-005'
export LLOCG_START_DECK_EXACT='PL!HS-PR-001,PL!HS-PR-002,PL!HS-PR-003,PL!HS-PR-004'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260714修正/内部確認: `live_start_score_if_named_members_in_exact_positions` の汎用 route で、R=大沢瑠璃乃 / L=安養寺姫芽 / C=藤島慈 の配置一致を確認し、`live_start_score_bonus_by_set_idx={0: 2}` が入ることを確認。成功時がログだけで終わらないよう、発生源付き `message_ack` pending を追加した。

#### PL!HS-bp5-017 stage group member plus distinct units score plus

確認観点:

- ステージに『蓮ノ空』メンバーを含むメンバー2人以上がいて、それらのユニット名が異なる場合、スコア+1。
- グループ条件とユニット名種類数を同時に見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-bp5-017'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!HS-PR-001'
export LLOCG_START_STAGE_C='PL!HS-PR-002'
export LLOCG_START_STAGE_R='PL!HS-PR-005'
export LLOCG_START_DECK_EXACT='PL!HS-PR-003,PL!HS-PR-004,PL!HS-PR-006,PL!HS-PR-007'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715修正/内部確認: `live_start_score_if_stage_has_group_member_and_distinct_units_at_least` の汎用 route で、ステージメンバー3/2人、ユニット名3/2種類、蓮ノ空メンバーありを確認し、`live_start_score_bonus_by_set_idx={0: 1}` が入ることを確認。成功時がログだけで終わらないよう、発生源付き `message_ack` pending を追加した。カード番号専用分岐なし。

#### PL!S-bp3-025 stage Aqours blade threshold score plus

確認観点:

- ステージの『Aqours』メンバー1人がブレード6つ以上を持つ場合、スコア+1。
- 元々のブレード、常時加算、一時加算を現在値として見る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!S-bp3-025'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!S-sd1-001'
export LLOCG_START_DECK_EXACT='PL!S-sd1-002,PL!S-bp3-001,PL!S-bp3-002,PL!S-bp3-003'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715修正/内部確認: `live_start_score_if_stage_group_member_blade_at_least` の汎用 route で、ステージの『Aqours』メンバーの現在ブレード最大値6/6（高海千歌）を参照し、`live_start_score_bonus_by_set_idx={0: 1}` が入ることを確認。成功時がログだけで終わらないよう、発生源付き `message_ack` pending を追加した。

#### PL!N-bp1-027 Solitude Rain stage color kinds score plus

確認観点:

- ステージの『虹ヶ咲』メンバーが持つ<桃>/<赤>/<黄>/<緑>/<青>/<紫>の色種類数ぶんスコアが増える。
- DB文面の読点区切りアイコン列でも拾える。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!N-bp1-027'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!N-bp3-004'
export LLOCG_START_STAGE_C='PL!N-bp3-005'
export LLOCG_START_STAGE_R='PL!N-PR-025'
export LLOCG_START_DECK_EXACT='PL!N-pb1-042,PL!N-bp1-001,PL!N-bp3-013,PL!N-bp3-014'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715内部確認: `live_start_score_per_stage_group_member_heart_color_kind` の汎用 route で、読点区切りの色アイコン列を parser が拾うことを確認。提示ステージでは『虹ヶ咲』メンバーの現在ハート色種類が5種類になり、`ok` 解決で `live_start_score_bonus_by_set_idx={0: 5}` が入る。発生源付き pending 経由で適用され、無言処理なし。

#### PL!SP-bp4-024 center cost comparison and left-side red hearts blade gain

確認観点:

- センターの『Liella!』メンバーのコストが相手センターより高いかどうかは手動確認ポップアップで「使う/スキップ」を選ぶ。
- 左サイドの『Liella!』メンバーが<赤>3つ以上を持つ場合、そのメンバーがブレード+2を得る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-bp4-024'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!SP-sd2-001'
export LLOCG_START_STAGE_C='PL!SP-bp2-010'
export LLOCG_START_STAGE_R='PL!SP-bp1-008'
export LLOCG_START_DECK_EXACT='PL!SP-bp4-004,PL!SP-bp4-007,PL!SP-pb1-001,PL!SP-pb2-005'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715修正/内部確認: 1つ目の効果は `live_start_score_if_own_center_group_member_cost_higher_than_opponent_manual` の汎用 route で、センター『Liella!』メンバーの自コスト15を表示する手動確認 `confirm_effect` pending が出る。`使う` 解決で `live_start_score_bonus_by_set_idx={0: 1}` が入る。2つ目の効果は `live_start_position_group_member_heart_color_at_least_gain_blades` の汎用 route で、左サイドの<赤>3/3条件達成により対象メンバーがブレード+2を得る。成功時がログだけで終わらないよう、2つ目の効果にも発生源付き `message_ack` pending を追加した。

#### PL!S-sd1-022 stage group members gain blades

確認観点:

- ライブ開始時にステージ上の『Aqours』メンバー全員がブレード+1を得る。
- 通常効果ルートの「ステージ指定グループ全員ブレード付与」文型で処理される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!S-sd1-022'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!S-sd1-001'
export LLOCG_START_STAGE_C='PL!S-sd1-002'
export LLOCG_START_STAGE_R='PL!S-bp3-001'
export LLOCG_START_DECK_EXACT='PL!S-bp3-002,PL!S-bp3-003,PL!S-bp3-025,PL!S-bp2-023'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715修正/内部確認: `stage_group_members_gain_blades_until_end_live` の汎用 route で、ステージの『Aqours』メンバー全員にブレード+1が入ることを確認。例ではL/Cの2人が対象。結果がログだけで終わらないよう、発生源付き `message_ack` pending を追加した。カード番号専用分岐なし。

#### PL!HS-bp2-020 distinct Hasunosora stage names score +2 each

確認観点:

- ライブ開始時、ステージにいる名前の異なる『蓮ノ空』メンバー1人につき、このカードのスコアが+2される。
- 同名重複は1人分として数える。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-bp2-020'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!HS-PR-001'
export LLOCG_START_STAGE_C='PL!HS-PR-002'
export LLOCG_START_STAGE_R='PL!HS-PR-003'
export LLOCG_START_DECK_EXACT='PL!HS-bp2-001,PL!HS-bp2-002,PL!HS-bp2-003,PL!HS-bp2-004,PL!HS-bp2-005,PL!HS-bp2-006,PL!HS-bp2-007,PL!HS-bp2-008'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715修正/内部確認: `live_start_score_per_distinct_stage_group_member_name` の汎用 route で、名前の異なる『蓮ノ空』メンバー3人を数え、1人につきスコア+2として `live_start_score_bonus_by_set_idx={0: 6}` が入ることを確認。成功時がログだけで終わらないよう、発生源付き `message_ack` pending を追加した。

#### PL!HS-bp5-018 distinct stage names and costs score +1

確認観点:

- ライブ開始時、名前とコストが両方ともそれぞれ異なるメンバーが3人以上いる場合、このカードのスコアが+1される。
- 現在コストを参照する。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!HS-bp5-018'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!HS-PR-001'
export LLOCG_START_STAGE_C='PL!HS-PR-003'
export LLOCG_START_STAGE_R='PL!HS-PR-007'
export LLOCG_START_DECK_EXACT='PL!HS-bp5-001,PL!HS-bp5-002,PL!HS-bp5-003,PL!HS-bp5-004,PL!HS-bp5-005,PL!HS-bp5-006,PL!HS-bp5-007,PL!HS-bp5-008'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715内部確認: `live_start_score_if_distinct_stage_names_and_costs_at_least` の汎用 route で、メンバー3人 / 名前3種類 / 現在コスト3種類を確認し、`live_start_score_bonus_by_set_idx={0: 1}` が入ることを確認。成功時の発生源付き `message_ack` pending は前回修正済み。

#### PL!-pb1-029 success empty and stage only lily white score +1

確認観点:

- ライブ開始時、成功ライブカード置き場が0枚で、ステージのメンバーが『lily white』のみの場合、このカードのスコアが+1される。
- ステージに異なるユニット/グループのメンバーが混ざる場合は適用されない。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!-pb1-029'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-PR-004'
export LLOCG_START_STAGE_C='PL!-PR-005'
export LLOCG_START_STAGE_R='PL!-PR-007'
export LLOCG_START_DECK_EXACT='PL!-pb1-001,PL!-pb1-002,PL!-pb1-003,PL!-pb1-004,PL!-pb1-005,PL!-pb1-006,PL!-pb1-007,PL!-pb1-008'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715修正/内部確認: `live_start_score_if_success_empty_and_stage_only_group` の汎用 route で、成功ライブ置き場0枚、ステージが『lily white』のみ=True を確認し、`live_start_score_bonus_by_set_idx={0: 1}` が入ることを確認。成功時がログだけで終わらないよう、発生源付き `message_ack` pending を追加した。成功ライブ3枚以上の初期状態なし。

#### PL!S-bp7-020 all stage members active required any -1

確認観点:

- ライブ開始時、ステージにいるすべてのメンバーがアクティブ状態なら、必要ハート<(任意)>が1つ減る。
- 確認ACK後に必要ハート表示へ反映される。
- このコマンドは1つ目のライブ開始時効果確認用。2つ目のデッキ下参照効果は別途未実装確認対象。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!S-bp7-020'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!S-bp5-007'
export LLOCG_START_STAGE_C='PL!S-pb1-003'
export LLOCG_START_STAGE_R='PL!S-pb1-007'
export LLOCG_START_DECK_EXACT='PL!S-bp7-002,PL!S-bp7-003,PL!S-bp7-005,PL!S-bp7-006,PL!S-bp7-015,PL!S-bp7-016,PL!S-bp7-019,PL!S-bp7-021'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715内部確認: `live_start_required_any_reduction_if_all_stage_members_active` の汎用 route で、ステージ3/3人がアクティブ状態として `live_start_required_any_reduction_ack` pending が出ることを確認。`ok` 解決後に `live_start_required_any_reduction_by_set_idx={0: 1}` が保存される。2つ目のデッキ下参照効果はこの項目の確認対象外のまま。

#### PL!SP-pb1-024 distinct KALEIDOSCORE stage names score +1

確認観点:

- ライブ開始時、名前の異なる『KALEIDOSCORE』メンバーが2人以上いる場合、このカードのスコアが+1される。
- ユニット名による判定を行う。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-pb1-024'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!SP-bp4-002'
export LLOCG_START_STAGE_C='PL!SP-bp4-005'
export LLOCG_START_STAGE_R='PL!SP-bp4-010'
export LLOCG_START_DECK_EXACT='PL!SP-pb1-001,PL!SP-pb1-002,PL!SP-pb1-003,PL!SP-pb1-004,PL!SP-pb1-005,PL!SP-pb1-006,PL!SP-pb1-007,PL!SP-pb1-008'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715修正/内部確認: `live_start_score_if_distinct_stage_group_member_names_at_least` の汎用 route で、名前の異なる『KALEIDOSCORE』メンバー3/2人を確認し、`live_start_score_bonus_by_set_idx={0: 1}` が入ることを確認。成功時がログだけで終わらないよう、発生源付き `message_ack` pending を追加した。ユニット名判定は group/unit 共通 matcher 経由。

#### PL!N-sd1-028 stage blade total >= 10 score +1

確認観点:

- ライブ開始時、ステージメンバーの現在ブレード合計が10以上なら、このカードのスコアが+1される。
- 常時ブレード / 一時ブレードがある場合も現在値として合算される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!N-sd1-028'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!N-bp3-004'
export LLOCG_START_STAGE_C='PL!N-bp3-005'
export LLOCG_START_STAGE_R='PL!N-PR-025'
export LLOCG_START_DECK_EXACT='PL!N-bp3-001,PL!N-bp3-002,PL!N-bp3-003,PL!N-bp3-007,PL!N-bp3-008,PL!N-bp3-009,PL!N-bp3-010,PL!N-bp3-011'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715修正/内部確認: `live_start_score_if_stage_blade_total_at_least` の汎用 route で、ステージメンバーの現在ブレード合計17/10を参照し、`live_start_score_bonus_by_set_idx={0: 1}` が入ることを確認。成功時がログだけで終わらないよう、発生源付き `message_ack` pending を追加した。

#### PL!S-pb1-020 Aqours green heart total >= 10 score +2

確認観点:

- ライブ開始時、ステージの『Aqours』メンバーが持つ<緑>の合計が10個以上なら、このカードのスコアが+2される。
- base hearts / blade hearts / temporary hearts / always hearts を現在値として数える。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!S-pb1-020'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!S-bp5-007'
export LLOCG_START_STAGE_C='PL!S-pb1-003'
export LLOCG_START_STAGE_R='PL!S-pb1-007'
export LLOCG_START_DECK_EXACT='PL!S-bp5-001,PL!S-bp5-002,PL!S-bp5-003,PL!S-bp5-004,PL!S-bp5-005,PL!S-bp5-006,PL!S-bp5-008,PL!S-bp5-009'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715内部確認: `live_start_score_if_stage_group_heart_color_total_at_least` の汎用 route で、ステージの『Aqours』メンバーが持つ<緑>15/10を現在値として参照し、`live_start_score_bonus_by_set_idx={0: 2}` が入ることを確認。発生源付き `message_ack` pending が出るため無言処理なし。

#### PL!SP-bp5-026 Liella stage heart total >= 11 score +1

確認観点:

- ライブ開始時、ステージの『Liella!』メンバーが持つハート総数が11以上なら、このカードのスコアが+1される。
- 色別ではなく総ハート数として数える。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-bp5-026'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!SP-bp5-001'
export LLOCG_START_STAGE_C='PL!SP-bp5-002'
export LLOCG_START_STAGE_R='PL!SP-bp5-003'
export LLOCG_START_DECK_EXACT='PL!SP-bp5-004,PL!SP-bp5-005,PL!SP-bp5-006,PL!SP-bp5-007,PL!SP-bp5-008,PL!SP-bp5-009,PL!SP-bp5-010,PL!SP-bp5-011'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715内部確認: `live_start_score_if_stage_group_heart_total_at_least` の汎用 route で、ステージの『Liella!』メンバーのハート総数19/11を参照し、`live_start_score_bonus_by_set_idx={0: 1}` が入ることを確認。発生源付き `message_ack` pending は前回修正済み。

#### PL!SP-pb2-045 Liella members with >= 4 hearts score +1 each

確認観点:

- ライブ開始時、ハートを4つ以上持つ『Liella!』メンバー1人につき、このカードのスコアが+1される。
- 対象人数ぶんの合計加算になる。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!SP-pb2-045'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!SP-bp5-001'
export LLOCG_START_STAGE_C='PL!SP-bp5-002'
export LLOCG_START_STAGE_R='PL!SP-bp5-003'
export LLOCG_START_DECK_EXACT='PL!SP-bp5-004,PL!SP-bp5-005,PL!SP-bp5-006,PL!SP-bp5-007,PL!SP-bp5-008,PL!SP-bp5-009,PL!SP-bp5-010,PL!SP-bp5-011'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715内部確認: `live_start_score_per_stage_group_member_with_heart_total_at_least` の汎用 route で、ハート4つ以上の『Liella!』メンバー3人を数え、1人につきスコア+1として `live_start_score_bonus_by_set_idx={0: 3}` が入ることを確認。成功時は発生源付き `message_ack` pending を出すよう修正済み。

#### PL!-bp3-026 live-success own stage heart total greater than opponent manual score +1

確認観点:

- ライブ成功時、自分のステージメンバーが持つハート総数を表示する。
- 相手ステージのハート総数は未モデルのため、条件を満たす場合は Apply、満たさない場合は Skip で手動確認する。
- Apply 時、このカードのスコアが+1される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!-bp3-026'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-bp3-001'
export LLOCG_START_STAGE_C='PL!-bp3-003'
export LLOCG_START_STAGE_R='PL!-bp3-008'
export LLOCG_START_DECK_EXACT='PL!-bp3-010,PL!-bp3-011,PL!-bp3-012,PL!-bp3-013,PL!-bp3-014,PL!-bp3-015,PL!-bp3-016,PL!-bp3-017'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715内部確認: `live_success_score_if_stage_heart_total_gt_opponent` の汎用 route で、自分のステージメンバーのハート総数11を表示する `confirm_effect` pending が出ることを確認。相手側は未モデルのため `apply/skip` 手動確認。`apply` 解決で `PL!-bp3-026[ライブ成功時]` のスコア+1が適用される。発生源付きで、カード番号専用分岐なし。

#### PL!-bp5-020 center group member yellow hearts reduce required any, cap 3

確認観点:

- センターの『μ's』メンバーが持つ<黄>2つにつき、対象LIVEの必要ハート<(任意)>が1つ減る。
- 軽減上限3が適用される。
- 確認ポップアップでセンターの<黄>個数、割り算、上限、今回の軽減値が表示される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!-bp5-020'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_C='PL!-bp5-003'
export LLOCG_START_DECK_EXACT='PL!-bp5-001,PL!-bp5-002,PL!-bp5-004,PL!-bp5-005,PL!-bp5-006,PL!-bp5-007,PL!-bp5-008,PL!-bp5-009'
export LLOCG_START_ENERGY_ACTIVE=25
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715内部確認: `live_start_required_any_reduction_by_center_group_member_heart_count` の汎用 route で、センターの『μ's』メンバーが持つ<黄>4個を参照し、2個につき1軽減、上限3の計算で今回-2の `live_start_required_any_reduction_ack` pending が出ることを確認。`ok` 解決後に `live_start_required_any_reduction_by_set_idx={0: 2}` が保存される。カード番号専用分岐なし。

#### PL!-bp5-023 stage members with non-pink/non-purple hearts reduce required any

確認観点:

- ステージにいる<桃>と<紫>以外の色のハートを持つメンバー1人につき、対象LIVEの必要ハート<(任意)>が1つ減る。
- base hearts / blade hearts / temporary hearts / always hearts を現在値として数える。
- 確認ポップアップで対象人数と軽減値が表示される。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_HAND='PL!-bp5-023'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_STAGE_L='PL!-bp5-003'
export LLOCG_START_STAGE_C='PL!-bp5-004'
export LLOCG_START_STAGE_R='PL!-bp5-009'
export LLOCG_START_DECK_EXACT='PL!-bp5-001,PL!-bp5-002,PL!-bp5-005,PL!-bp5-006,PL!-bp5-007,PL!-bp5-008,PL!-bp5-010,PL!-bp5-011'
export LLOCG_START_ENERGY_ACTIVE=30
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

※20260715内部確認: `live_start_required_any_reduction_per_stage_member_with_heart_except_colors` の汎用 route で、<桃>/<紫>以外のハートを持つメンバー3人（L/C/R）を数え、必要ハート<(任意)>-3の `live_start_required_any_reduction_ack` pending が出ることを確認。`ok` 解決後に `live_start_required_any_reduction_by_set_idx={0: 3}` が保存される。base/current heart helper 経由で判定し、カード番号専用分岐なし。

## Integrated current updates 20260715

※ `docs/debug/loveca_debug_commands_current_updates_20260623.md` から移動。
※ 2026-07-15 時点で current 側に残っていた未統合のデバッグ確認・修正メモを統合。

### 2026-07-15 yell-time auto result ack

対象: `PL!SP-pb2-008` yell-revealed no-blade-heart Liella score bonus

修正内容:

- エール時自動効果のうち、選択 pending を挟まず即時解決される `draw1` / `live_total_score_bonus` / `gain_icons` 系の結果がログ止まりだったため、共通で `message_ack` pending を出すよう修正。
- `PL!SP-pb2-008` では、エール公開されたブレードハートなし『Liella!』メンバー枚数と、上限適用後のライブ合計スコア加算結果が確認できる。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_START_STAGE_C='PL!SP-pb2-008'
export LLOCG_START_HAND='LL-bp5-001'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0
export LLOCG_START_DECK_EXACT='PL!SP-PR-004,PL!SP-PR-005,PL!SP-PR-006,PL!SP-PR-008,PL!-bp4-021,PL!-bp4-024,PL!-bp3-006,PL!-bp3-004,LL-bp5-001,PL!-pb1-030'
export LLOCG_START_DECK_EXACT_STRICT=1
export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1
python3 ./run_llocg_ui_web.py
```

確認観点:

- エール公開後の自動効果選択で `PL!SP-pb2-008` を解決する。
- 解決後、条件詳細とライブ合計スコア加算結果の確認ポップアップが出ること。
- 確認後、残りの自動効果キューがある場合は通常どおり続くこと。

### 2026-07-15 baton same-cost negative command correction

対象: `PL!HS-bp2-008` baton condition negative cases / same cost source

修正内容:

- 同一カード番号 `PL!HS-bp2-008` をステージと手札の両方に置くコマンドを修正。
- ステージ側を `PL!HS-bp1-013`（コスト4、DOLLCHESTRA）へ差し替え、手札の `PL!HS-bp2-008`（コスト4）でバトンタッチする同コスト負例にした。

確認観点:

- 手札の `PL!HS-bp2-008` をセンターへ重ねる。
- バトンタッチ元と登場先が同コストのため、「このメンバーよりコストが低い」条件は未達。
- ブレード+2が付与されず、条件未達の確認表示/ログが出ること。

### 2026-07-15 topk stage-or-hand pending card label

修正内容:

- `topk_stage_or_hand` pending の本文で、選択カードをカード番号のまま表示していた箇所を修正。
- `llocg_ui/engine.py` 側で共通表示名 `_card_display_name_with_no` を使い、メンバーカードは `Nコスト メンバー名`、ライブカードはカード名で表示する。
- pending に `display_cards` / `source_cn` / `auto_effect_detail` も渡し、ポップアップ本文とカード表示 UI の両方で対象カード情報を参照できるようにした。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
export LLOCG_DEBUG_EFFECT_CARD='PL!SP-pb2-001'
export LLOCG_START_HAND='PL!SP-pb2-001,PL!HS-PR-001'
export LLOCG_START_ENERGY_ACTIVE=99
export LLOCG_START_STAGE_C='PL!HS-PR-001'
export LLOCG_START_DECK_TOP='PL!SP-bp1-012,PL!SP-bp2-007,PL!HS-PR-001,PL!SP-bp5-008,PL!HS-PR-020'
python3 ./run_llocg_ui_web.py
```

確認観点:

- `PL!SP-pb2-001` を登場させ、任意手札コストを払う。
- 上5枚から `PL!SP-bp5-008` を選ぶ。
- 「効果の選択」直下の本文が `PL!SP-bp5-008 を...` ではなく、メンバーカード表示名で出ることを確認する。
- 手札/空きステージの選択肢も文章リストで表示され、対象カードの画像/表示名が参照できることを確認する。

### 2026-07-14 live attempt summary YELL ALL dedupe

修正内容:

- ライブ成功確認画面の所持ハート合計で、エール公開カードの `<ALL>` が二重計上される不具合を修正。
- 原因は `cheer_hearts_from_resolve()` が `blade_hearts['all']` と `blade_heart_tags_json` の `(ALL)` を両方加算していたこと。DB は同じ `<ALL>` を両方の形で持つため、カード1枚につき最大値として数えるようにした。

分類:

- 内部監査結果: 問題なし。
- ユーザー確認: 必要。
- 理由: 内部確認では成功確認 payload の `owned_hearts.yell.all == 1` / `owned_hearts.total.all == 1` まで確認済み。ただしユーザー指摘はライブ成功確認画面上の表示ズレであり、画面上で `ALL 0+1 / 合計 1` と見えるかの目視確認が残るため、current に残す。

確認コマンド:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT LLOCG_START_DECK_EXACT_STRICT \
  LLOCG_START_PHASE LLOCG_START_TURN \
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \
  LLOCG_START_STAGE_MOVED_THIS_TURN LLOCG_START_STAGE_MOVED_CARDS LLOCG_START_STAGE_MOVED_CARDNUMBERS \
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1

export LLOCG_START_HAND='PL!N-bp4-030'
export LLOCG_START_HAND_SIZE=0
export LLOCG_START_SHUFFLE=0

export LLOCG_START_STAGE_L='PL!SP-pb1-014'
export LLOCG_START_STAGE_C='PL!S-pb1-017'
export LLOCG_START_STAGE_R='PL!SP-pb1-014'

# 1枚目はライブセット時ドロー用ダミー、2枚目がエール公開の ALL 1枚。
export LLOCG_START_DECK_EXACT='PL!N-PR-004,PL!N-bp4-027,PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024'
export LLOCG_START_DECK_EXACT_STRICT=1

export LLOCG_START_ENERGY_ACTIVE=20
export LLOCG_START_ENERGY_WAIT=0
export LLOCG_DEBUG_LIVE_IN_HAND=0
export LLOCG_DEBUG_MEMBER_IN_HAND=0
export LLOCG_START_DEBUG=1

python3 ./run_llocg_ui_web.py
```

確認観点:

- `PL!N-bp4-030` をライブセットする。
- `PL!S-pb1-017` のライブ開始時効果を使用する。
- エール確認画面で ALL が1枚であることを確認する。
- ライブ成功確認画面の「所持ハート合計（盤面＋エール）」でも ALL が `0+1 / 合計 1` と表示されることを確認する。

内部確認:

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 - <<'PY'
from pathlib import Path
from llocg_ui import engine
from llocg_ui.db import load_cards_db

cards = load_cards_db(Path('.'))
gs = engine.GameState(root='.', code='debug', seed=1, debug=True, phase='MAIN')
gs.set_zone = ['PL!N-bp4-030']
gs.resolve_zone = ['PL!N-bp4-030']
gs.stage = {
    'L': engine.StageSlot(cardnumber='PL!SP-pb1-014', active=True),
    'C': engine.StageSlot(cardnumber='PL!S-pb1-017', active=True),
    'R': engine.StageSlot(cardnumber='PL!SP-pb1-014', active=True),
}
gs.live_start_prompted = True

assert engine.cheer_hearts_from_resolve(gs, cards).get('all') == 1
engine.cmd_attempt(gs, cards)
summary = gs.pending[-1]['live_attempt_summary']
assert summary['owned_hearts']['yell'].get('all') == 1
assert summary['owned_hearts']['total'].get('all') == 1
print('live attempt summary ALL dedupe OK')
PY
```

## Full command audit 20260715

※目的: 2026-07-15 の追加変更後、ユーザーコメントが残る項目だけでなく、コメントが付いていない `####` 個別コマンドも含めて `docs/debug/loveca_debug_commands_20260623.md` 全体を再監査する。

※静的監査結果:

- `####` 個別コマンド 77 件すべてを対象に、bash 起動ブロックのカード番号・初期成功ライブ置き場枚数・`!` を含むカード番号のクォート・`DECK_CODE` wrapper 混入・未登録カード混入を確認。
- 監査後の再チェックでは、未登録カード、未クォート `!`、成功ライブカード置き場3枚以上の初期状態は 0 件。
- `DECK_CODE` は起動 wrapper としては使われていない。本文中の「DECK_CODE wrapper 不使用」という監査メモ文字列のみ。
- `PL!SP-bp4-017` はライブ確認用の山札が5枚で余計なリフレッシュを招きやすかったため、10枚へ増量。
- `PL!S-bp5-023` は控え室候補に未登録の `PL!S-bp5-024` が残っていたため、現行DBに存在する `PL!S-bp5-019` へ差し替え。
- `PL!S-bp7-020` は山札に未登録の `PL!S-bp7-001` / `PL!S-bp7-004` / `PL!S-bp7-007` / `PL!S-bp7-008` が残っていたため、現行DBに存在する `PL!S-bp7-002` / `003` / `005` / `006` / `015` / `016` / `019` / `021` へ差し替え。
- 20260713 系の統合済みコマンドに残っていた未登録 `LL-bp5-003` / `LL-bp5-004` / `LL-bp5-005` は、実在する `LL-bp5-001` / `LL-bp5-002` / `PL!-bp4-013` / `PL!-bp4-020` のダミー山札へ差し替え。
- `Integrated current updates 20260715` 内の `LLOCG_START_STAGE='C=PL!HS-PR-001'` は、正本テンプレートに寄せて `LLOCG_START_STAGE_C='PL!HS-PR-001'` へ差し替え。

※内部 smoke 再確認:

- `PL!N-bp3-007`: DB補正後の「コスト13以下の『優木せつ菜』メンバーカード」route で、手札 `PL!N-bp1-007` / `PL!N-bp1-001` 混在時に候補が `PL!N-bp1-007` のみに絞られることを確認。指定名称以外を弾く。カード番号専用分岐なし。
- `LL-bp5-002`: ステージの `μ's` / `虹ヶ咲` / `蓮ノ空` グループを参照し、控え室候補が `PL!SP-pb2-008` のみに絞られることを確認。pending に `source_cn` / 実行中効果文 / `display_cards` あり。
- `PL!HS-bp2-008`: 低コスト『DOLLCHESTRA』メンバーからのバトンタッチ条件達成後、内側の `gain_blade_until_end_live` が `message_ack` で発生源・条件・ブレード+2結果を表示することを確認。
- `PL!SP-pb2-008`: 現行DBで trigger が `ライブ成功時` に補正されていることを確認。エール時自動効果として拾わない前提。
- `PL!S-bp2-004`: no-LIVE 公開時の再エール確認 pending が発生し、発生源 `PL!S-bp2-004` と公開カードリストが出ることを確認。
- `PL!S-bp3-020`: `PL!S-bp2-004` の no-LIVE 文面を流用せず、「ブレードハートを持つカードが2枚以下」「そのエールで得たブレードハートを失う」文面になっていることを確認。
- `PL!HS-bp6-027`: engine pending は `optional=True` とカード候補を持ち、server UI 側で `0枚で終了` / `選択を終了` ボタンを追加することを確認。1枚選択後に skip した場合、既存エール公開カード `base_yell_cards` と追加エール公開カード `additional_yell_cards` を持つ `show_revealed_cards_ack` が出る。
- `PL!SP-bp2-010`: 実際のライブ開始時 trigger 経路で、他メンバー1/1ならエール公開枚数 -8 の `message_ack`、0/1なら未達 `message_ack` が出ることを確認。
- `LL-bp5-001`: 移動済みステージメンバー履歴でスコア+1が適用され、`message_ack` に `source_cn=LL-bp5-001` と条件内訳が入ることを確認。
- `PL!-PR-015`: 正例は `hand_member_to_empty_area` pending に `display_cards=['PL!-PR-007']` が入り、負例は同コストバトン元で `message_ack` に未達理由が出ることを確認。
- `PL!SP-bp4-017`: 実際のライブ開始時 trigger 経路で、左サイド配置ではブレード+2、センター配置では `左サイド` 条件未達の `message_ack` となりブレード付与なしを確認。

※残るユーザー実機確認:

- 画像リスト表示やボタン文言、公開領域表示、下エネルギーバッジ前面表示など、UI目視・操作感に属するものは内部 smoke だけで完了扱いにしない。該当コメントツリーには `ユーザー実機再確認待ち` を残す。
- ただし runtime / pending データ上は、今回確認した範囲で発生源なし・自動効果の無言処理・カード番号専用分岐の再発は確認されなかった。
