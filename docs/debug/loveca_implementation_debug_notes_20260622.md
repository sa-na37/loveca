# Loveca implementation debug notes 20260622

Purpose: Track new implementation changes and later debug checks in one short file.

Rules:

- Keep long debug commands here only as concise check descriptions, not full handoff commands.
- Update this file whenever a new implementation route is added.
- Do not include local backup or `jank/` contents unless the implementation depends on them.

## 20260622i: top-k choose N to hand

Changed files:

- `llocg_ui/engine.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
- `docs/handoffs/loveca_handoff_20260622i.md`
- `README.md`
- `docs/notes/loveca_cleanup_classification_table_20260622.md`

Implemented route:

- `look_top_k_choose_n_rest_waiting`
- Effect shape: `自分のデッキの上からカードをK枚見る。その中からカードをN枚手札に加え、残りを控え室に置く。`

Covered examples:

- `LL-bp6-001` 南ことり＆黒澤ダイヤ＆徒町小鈴

Later debug checks:

- Start with `LL-bp6-001` in hand and at least six known cards on top of deck.
- Resolve the enter trigger.
- Confirm the top six are shown, two clicks are required, selected two go to hand, remaining four go to waiting room.

Already checked internally:

- Matcher maps the effect text to `look_top_choose_n`.
- Engine-only pending test selected 2 from 6 correctly.
- Python compile passed.

## 20260622j: top-k sentence variant and simple mill

Changed files:

- `llocg_ui/engine.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`

Implemented routes:

- `look_top_k_choose_1_rest_waiting_sentence_split`
- `mill_top_k_to_waiting`

Effect shapes:

- `自分のデッキの上からカードをK枚見る。その中から1枚を手札に加える。残りを控え室に置く。`
- `自分のデッキの上からカードをK枚控え室に置く。`
- `デッキの上からカードをK枚控え室に置く。`

Covered examples:

- `PL!-bp5-222` 優木あんじゅ
- `PL!HS-cl1-004` 百生吟子
- `PL!HS-cl1-007` セラス 柳田 リリエンフェルト

Later debug checks:

- For `PL!-bp5-222` / `PL!HS-cl1-007`, confirm top 3 is shown, one selected card goes to hand, the other two go to waiting room.
- For `PL!HS-cl1-004`, resolve the choose-one enter effect and confirm the top 3 cards go to waiting room when choosing the mill option.

Already checked internally:

- Matcher maps all three covered examples to the expected generic route.
- Engine-only mill test moved top 3 cards to waiting room.
- Engine-only choose-one sentence variant test selected 1 from top 3 correctly.
- Python compile passed.

## 20260622k: top-k cost-filtered group member

Changed files:

- `llocg_ui/engine.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`

Implemented route:

- `look_top_k_optional_cost_ge_group_member`

Effect shape:

- `自分のデッキの上からカードをK枚見る。その中からコストN以上の『GROUP』のメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。`

Covered examples:

- `PL!HS-bp5-008` 桂城泉
- `PL!-bp4-006` 西木野真姫 is also marked covered through the existing success-zone score-sum wrapper plus existing group-member top-k route.

Later debug checks:

- For `PL!HS-bp5-008`, place a cost 9+ Hasunosora member and non-matching cards in the top five; confirm only the matching member is clickable.
- For `PL!-bp4-006`, set success live score sum to at least 3, then confirm the inner μ's member top-five search appears.

Already checked internally:

- Matcher maps `PL!HS-bp5-008` to `look_top_k_optional_cost_ge_group_member`.
- Matcher maps `PL!-bp4-006` inner text through the success score wrapper to `look_top_k_optional_group_type`.
- Engine-only filter test showed only the cost 9+ Hasunosora member as candidate and moved the rest to waiting room.

## 20260623a: top-k reorder typo and top1 optional mill

Changed files:

- `llocg_ui/engine.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`

Implemented routes:

- `look_top_k_reorder_keep_any_rest_waiting` now accepts `順場` as a DB typo variant of `順番`.
- `look_top1_optional_mill`

Effect shapes:

- `自分のデッキの上からカードをK枚見る。その中から好きな枚数を好きな順場でデッキの上に置き、残りを控え室に置く。`
- `自分のデッキの上からカードを1枚見る。そのカードを控え室に置いてもよい。`

Covered examples:

- `PL!-sd1-019` START：DASH!!
- `PL!HS-cl1-001` 日野下花帆

Later debug checks:

- For `PL!-sd1-019`, confirm top 3 reorder UI appears and kept cards return to deck top in selected order.
- For `PL!HS-cl1-001`, confirm the top card is shown with choices to move it to waiting room or keep it on top.

Already checked internally:

- Matcher maps both examples to the expected route.
- Engine-only top1 optional test moved the top card to waiting room.

## 20260623b: top-k mill conditional followup

Changed files:

- `llocg_ui/engine.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`

Implemented route:

- `mill_top_conditional_followup`

Implemented match ids:

- `mill_top_k_draw_if_contains_live`
- `mill_top_k_draw_if_all_members`
- `mill_top_k_gain_icons_if_contains_live`
- `mill_top_k_gain_icons_if_all_members`
- `mill_top_k_gain_icons_if_all_member_heart_color`
- `mill_top_k_gain_icons_if_all_group_cards`

Effect shapes:

- `自分のデッキの上からカードをK枚控え室に置く。それらの中にライブカードがある場合、カードをN枚引く。`
- `自分のデッキの上からカードをK枚控え室に置く。それらがすべてメンバーカードの場合、カードをN枚引く。`
- `自分のデッキの上からカードをK枚控え室に置く。それらの中にライブカードがある場合、ライブ終了時まで、<icons>を得る。`
- `自分のデッキの上からカードをK枚控え室に置く。それらがすべてメンバーカードの場合、ライブ終了時まで、<icons>を得る。`
- `自分のデッキの上からカードをK枚控え室に置く。それらがすべて<color>を持つメンバーカードの場合、ライブ終了時まで、<icons>を得る。`
- `自分のデッキの上からカードをK枚控え室に置く。それらがすべて『GROUP』のカードの場合、ライブ終了時まで、<icons>を得る。`

Covered examples:

- `PL!-sd1-007` 東條希
- `PL!HS-PR-019` 百生吟子
- `PL!HS-PR-021` 安養寺姫芽
- `PL!HS-bp1-008` 徒町小鈴
- `PL!HS-bp5-001` 日野下花帆
- `PL!HS-bp5-013` 徒町小鈴
- `PL!HS-bp6-009` 日野下花帆
- `PL!HS-sd1-013` 徒町小鈴

Later debug checks:

- For `PL!-sd1-007`, put at least one live card in the top five and confirm those five move to waiting room, then one card is drawn.
- For `PL!HS-bp1-008`, put three member cards in the top three and confirm those three move to waiting room, then one card is drawn.
- For `PL!HS-PR-019` / `PL!HS-PR-021` / `PL!HS-sd1-013`, put three matching-color heart members in the top three and confirm the source member gains the matching temporary heart until live end.
- For `PL!HS-bp5-001` / `PL!HS-bp5-013` / `PL!HS-bp6-009`, confirm the source member gains the expected temporary blade icons only when the milled cards meet the condition.

Already checked internally:

- Matcher maps all eight examples to the expected generic route.
- Engine-only draw followup test moved top 5 cards to waiting room and drew 1 card.
- Engine-only heart-gain followup test moved top 3 cards to waiting room and granted source stage slot `green: 1`.
- Note: when the draw empties the remaining deck, existing refresh rules may immediately shuffle waiting room back into deck; retest with a larger deck when inspecting only the waiting-room contents.

Commands run:

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Internal DB-backed matcher check for the eight covered cardnumbers.
- Internal CSV status count check for `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`.

Results:

- Python compile passed.
- CSV counts: `implemented_existing_topk_or_deck=89`, `needs_audit_unmatched_topk=49`.

## 20260623c: top-k mill retrieve, reorder all, and optional conditional mill

Changed files:

- `llocg_ui/engine.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`

Implemented routes:

- `mill_top_then_retrieve_from_waiting`
- `look_top_reorder_all`
- `stage_group_optional_mill_top_k`

Implemented match ids:

- `mill_top_k_then_retrieve_waiting_group_type`
- `mill_top_k_then_retrieve_waiting_type`
- `look_top_k_reorder_all_on_top`
- `stage_group_optional_mill_top_k`
- `optional_discard_one_from_hand_then_effect_direct`

Newly classified existing route:

- `topdeck_green_live_group_upto1_then_draw_if_opponent_wait_exists`

Covered examples:

- `PL!-bp5-010` 高坂穂乃果
- `PL!HS-pb1-004` 百生吟子
- `PL!N-bp1-009` 天王寺璃奈
- `PL!-pb1-006` 西木野真姫
- `PL!HS-pb1-027` ユメワズライ
- `PL!-bp6-016` 東條希
- `PL!-pb1-016` 東條希

Later debug checks:

- For `PL!-bp5-010`, confirm top 3 move to waiting room, then the waiting-room A-RISE member picker appears.
- For `PL!HS-pb1-004`, confirm top 3 move to waiting room, then the waiting-room Cerise Bouquet live picker appears.
- For `PL!N-bp1-009`, confirm top 2 move to waiting room, then the waiting-room member picker appears.
- For `PL!-pb1-006`, confirm waiting-room μ's live topdeck UI appears, followed by the opponent-wait draw confirmation.
- For `PL!HS-pb1-027`, confirm the optional mill prompt appears only when a Cerise Bouquet member is on your stage.
- For `PL!-bp6-016`, confirm the top 3 reorder UI requires all three cards to be placed back on deck top.
- For `PL!-pb1-016`, confirm the optional hand-discard picker appears first, then the lily white top-four search appears after paying the cost.

Already checked internally:

- Matcher maps all seven examples to the expected route.
- Engine-only mill-then-retrieve test moved the top cards to waiting room and queued the waiting-room picker.
- Engine-only reorder-all test queued `reorder_topk_all`.
- Engine-only optional group mill test queued `confirm_mill_top_to_green` when the stage condition was met.
- Matcher maps `PL!-pb1-016` to the direct optional-discard wrapper, with the existing group top-k search as its followup.

Commands run:

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Internal DB-backed matcher check for the seven covered cardnumbers.
- Internal CSV status count check for `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`.

Results:

- Python compile passed.
- CSV counts: `implemented_existing_topk_or_deck=96`, `needs_audit_unmatched_topk=42`.

## 20260623d: reveal until live

Changed files:

- `llocg_ui/engine.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`

Implemented route:

- `reveal_until_match_to_hand_rest_waiting`

Implemented match id:

- `reveal_until_live_to_hand_rest_waiting`

Covered example:

- `PL!N-bp1-011` ミア・テイラー

Later debug checks:

- For `PL!N-bp1-011`, put non-live cards above one live card in the deck. After paying the optional hand-discard cost, confirm the first live card goes to hand and all earlier revealed cards go to waiting room.

Already checked internally:

- Matcher maps `PL!N-bp1-011` to `reveal_until_live_to_hand_rest_waiting`.
- Engine-only reveal-until-live test moved two non-live cards to waiting room and the first live card to hand.

Commands run:

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Internal CSV status count check for `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`.
- Internal DB-backed matcher smoke check from `docs/debug/loveca_debug_commands_20260623.md`.

Results:

- Python compile passed.
- CSV counts: `implemented_existing_topk_or_deck=97`, `needs_audit_unmatched_topk=41`.

## 20260623e: top-k trailing punctuation variant and existing-route reclassification

Changed files:

- `llocg_ui/engine.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
- `docs/debug/loveca_debug_commands_current_updates_20260623.md`

Implemented route adjustment:

- `look_top_k_optional_group`, `look_top_k_optional_group_type`, and `look_top_k_optional_type` now accept the DB sentence variant where the final `。` is missing.
- Top-k filtered group checks now use the existing group-or-unit matcher, so unit labels such as `5yncri5e!` are selectable.

Newly covered example:

- `PL!SP-pb1-017` 桜小路きな子

Newly reclassified existing routes:

- `PL!N-bp4-002` 中須かすみ — `choose_self_or_opponent_top1_mill_optional`
- `PL!N-bp5-009` 天王寺璃奈 — `look_top_k_optional_cost_ge_group_member`
- `PL!S-bp5-006` 津島善子 — `look_top_k_optional_cost_ge_group_member`
- `PL!S-bp6-012` 松浦果南 — `mill_top_k_to_waiting`
- `PL!S-bp6-017` 小原鞠莉 — `mill_top_k_to_waiting`
- `PL!S-bp6-019` Step! ZERO to ONE — `score_draw_then_hand_top_or_bottom_if_all_stage_group`
- `PL!S-pb1-008` 小原鞠莉 — `choose_self_or_opponent_topk_reorder_keep_any`
- `PL!S-sd1-013` 黒澤ダイヤ — `mill_top_k_to_waiting`
- `PL!SP-bp5-008` 若菜四季 — `look_top_k_optional_cost_ge_group_member`

Later debug checks:

- For `PL!SP-pb1-017`, put a `5yncri5e!` card and non-matching cards in the top five. Confirm the matching card is selectable and the rest go to waiting room.

Already checked internally:

- Matcher maps `PL!SP-pb1-017` to `look_top_k_optional_group`.
- Engine-only top-k filtered test shows only a `5yncri5e!` unit card in the top five as the selectable candidate.
- Current matcher maps the nine reclassified existing-route examples above to their expected route ids.

Commands run:

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Internal CSV status count check for `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`.

Results:

- Python compile passed.
- CSV counts: `implemented_existing_topk_or_deck=107`, `needs_audit_unmatched_topk=31`.

## 20260623f: debug feedback UI and cost fixes

Changed files:

- `llocg_ui/engine.py`
- `llocg_ui/server.py`
- `docs/debug/loveca_debug_commands_20260623.md`

Implemented feedback handling:

- Processed user `＊` debug comments in `docs/debug/loveca_debug_commands_20260623.md`.
- Moved confirmed-ok entries to the resolved list and removed their active debug command blocks.
- Added a persistent debug comment handling rule for future feedback passes.

Runtime fixes:

- Self WAIT plus hand-discard costs now remain classified as self WAIT costs even when the same cost text also contains `控え室` for the hand discard.
- True self-to-waiting-room costs are still distinguished from self WAIT costs by matching the self member move phrase directly.
- `mill_top_conditional_followup` automatic effects now enqueue an `自動効果確認` popup showing moved cards, condition result, and the follow-up draw/icon result.

UI fixes:

- Multi-pick `choose_from_topk` now supports selecting all required cards with visible selection order and confirming once.
- `choose_enter_effect_mode` now renders framed `①` / `②` style choices directly under the effect text.

Covered debug feedback examples:

- `LL-bp6-001`
- `PL!HS-cl1-004`
- `PL!-sd1-019`
- `PL!HS-cl1-001`
- `PL!-bp5-222` / `PL!HS-cl1-007`
- `PL!HS-bp5-008`
- `PL!-sd1-007`

Commands run:

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Extracted embedded UI script from `llocg_ui/server.py` and checked it with bundled Node.js `--check`.
- Internal engine-only WAIT cost regression checks for `PL!-bp5-222` and `PL!HS-bp5-008`.
- Internal engine-only automatic confirmation popup check for `PL!-sd1-007`.

Results:

- Python compile passed.
- Embedded UI script syntax check passed.
- WAIT plus hand-discard effects leave the source member in WAIT after paying.
- Automatic mill conditional follow-up effects now produce `show_revealed_cards_ack`.

## 20260623g: top-k filter variants and waiting-room topdeck text

Changed files:

- `llocg_ui/engine.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
- `docs/debug/loveca_debug_commands_20260623.md`

Implemented routes:

- `topdeck_green_any_upto1_waiting_card`
- `look_top_k_optional_member_heart_all_colors`
- `look_top_k_optional_group_no_ability_or_body`
- `look_top_k_optional_group_member_or_bladeheart_group_member`

Covered examples:

- `PL!N-bp4-021` 天王寺璃奈
- `PL!S-bp6-005` 渡辺曜
- `PL!-bp6-002` 絢瀬絵里
- `PL!SP-bp5-013` 唐可可

Later debug checks:

- For `PL!N-bp4-021`, put cards in waiting room and confirm one can be placed on deck top, with skip available.
- For `PL!S-bp6-005`, put one red/green/blue member and one non-matching card in the top two. Confirm only the all-three-colors member is selectable.
- For `PL!-bp6-002`, put a no-ability μ's card or <常時> μ's card in the top two. Confirm only matching μ's cards are selectable.
- For `PL!SP-bp5-013`, after paying hand discard, confirm Sunny Passion members or blade-heart Liella! members are selectable.

Already checked internally:

- Matcher maps all four covered examples to the expected route ids.
- Engine-only candidate-filter checks passed for the three top-k examples.
- Engine-only waiting-room topdeck pending check passed for `PL!N-bp4-021`.

Commands run:

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Internal DB-backed matcher and pending smoke check for the four covered examples.
- Internal CSV status count check for `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`.

Results:

- Python compile passed.
- CSV counts: `implemented_existing_topk_or_deck=111`, `needs_audit_unmatched_topk=27`.
- Debug commands are kept in the current-updates file until the user requests integration into `docs/debug/loveca_debug_commands_20260623.md`.

## 20260623h: debug memo integration and feedback fixes

Changed files:

- `llocg_ui/engine.py`
- `llocg_ui/server.py`
- `docs/debug/loveca_debug_commands_20260623.md`
- `docs/debug/loveca_debug_commands_current_updates_20260623.md`

Debug memo handling:

- Integrated the 20260623g current-update commands into `docs/debug/loveca_debug_commands_20260623.md`.
- Cleared `docs/debug/loveca_debug_commands_current_updates_20260623.md` back to the pending placeholder.
- Moved user-confirmed OK entries from active commands to the resolved confirmations list.
- Kept active only commands that still need re-check after command or runtime fixes.

Runtime fixes:

- Auto confirmation condition text now uses Japanese labels instead of internal condition keys.
- Heart/blade tokens in confirmation text are normalized for texticon rendering.
- Waiting-room-to-deck-top pending text now includes source and effect text.
- Reveal-until-live resolution now shows a result confirmation popup with revealed cards and destination summary.
- Reorder-all top-k effects use the selected-frame reorder UI and final confirmation.
- Optional hand-discard cost display avoids repeating the full condition/effect text.

Command fixes:

- `PL!HS-bp5-001` no longer starts on stage, so its enter effect can be checked from hand.
- `PL!HS-pb1-004` now starts with active energy for the cost.
- `PL!HS-pb1-027` and `PL!-bp6-016` now include `LLOCG_DEBUG_LIVE_IN_HAND=1` for live-success checks.
- The broad resize-layout note is left as deferred because it is a separate UI-wide task.

Commands run:

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Parsed all bash blocks in `docs/debug/loveca_debug_commands_20260623.md` with `bash -n`.
- Extracted embedded UI script from `llocg_ui/server.py` and checked it with bundled Node.js `--check`.
- Internal engine-only smoke check for Japanese condition labels, reveal result popup, topdeck source/effect text, optional cost display, and reorder-all pending.

Results:

- Python compile passed.
- Debug command bash syntax passed.
- Embedded UI script syntax check passed.
- Internal engine feedback smoke check passed.

## 20260623i: top-k filtered up-to multi-pick

Changed files:

- `llocg_ui/engine.py`
- `llocg_ui/server.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
- `docs/debug/loveca_debug_commands_current_updates_20260623.md`

Implemented route:

- `look_top_k_optional_member_heart_any_color_upto_n`

Covered example:

- `PL!S-bp2-005`: top 7, choose up to 3 member cards with any of the specified heart colors.

Runtime notes:

- Filtered `choose_from_topk` pending now supports a min/max pick range.
- The UI multi-pick confirm button now supports `0..N` selection ranges and sends `skip` when zero cards are chosen.
- Existing exact multi-pick flows keep their exact count behavior.

Commands run:

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Internal matcher check for `PL!S-bp2-005`.
- Internal engine-only smoke check for selecting two matching cards and for choosing zero cards.

Results:

- Python compile passed.
- Matcher maps `PL!S-bp2-005` to `look_top_k_optional_member_heart_any_color_upto_n`.
- Engine smoke check passed for 0-to-3 filtered top-k selection.

## 20260623j: debug response integration and follow-up fixes

Changed files:

- `llocg_ui/engine.py`
- `llocg_ui/server.py`
- `docs/debug/loveca_debug_commands_20260623.md`
- `docs/debug/loveca_debug_commands_current_updates_20260623.md`

Debug memo handling:

- Integrated the 20260623i current-update command into `docs/debug/loveca_debug_commands_20260623.md`.
- Cleared `docs/debug/loveca_debug_commands_current_updates_20260623.md` back to the pending placeholder.
- Moved confirmed OK entries to the resolved confirmations list.
- Kept corrected/recheck-needed commands active with `＊再確認待ち` comments.

Runtime fixes:

- Waiting-room retrieve filters now match group or unit, so `PL!HS-pb1-004` can find `PL!HS-pb1-027` as a `スリーズブーケ` LIVE.
- Reveal-until result text now prefers card names and keeps card numbers in parentheses for identification.

Command fixes:

- `PL!HS-pb1-004`: uses enough debug energy and keeps the `スリーズブーケ` LIVE in waiting room.
- `PL!HS-pb1-027`: starts with the target LIVE in hand and stage hearts sufficient for a successful live.
- `PL!-bp6-016`: separates the stage source member from the success LIVE and supplies the required hearts.
- `PL!-bp6-002`: attempted to include both no-ability and BODY/常時 μ's candidates; the BODY-vs-常時 distinction was corrected in 20260623k.
- Repaired the malformed `PL!S-bp6-005` command block.

Commands run:

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Internal engine-only smoke check for `PL!HS-pb1-004` unit-based waiting-room LIVE retrieval.
- Internal engine-only smoke check for reveal result card-name display.

Results:

- Python compile passed.
- `PL!HS-pb1-004` now enqueues `choose_live_from_green` with `PL!HS-pb1-027`.
- Reveal result text shows `START：DASH!!（PL!-sd1-019）` instead of only the card number.

## 20260623k: debug response for comment handling, always filter, and reorder drop UX

Changed files:

- `llocg_ui/engine.py`
- `llocg_ui/server.py`
- `docs/debug/loveca_debug_commands_20260623.md`
- `docs/debug/loveca_debug_commands_current_updates_20260623.md`

Debug memo handling:

- Current-update file had no pending command body, so no new command block was integrated.
- Moved user-confirmed OK commands to Resolved debug confirmations.
- Kept `PL!-bp6-002` active with the user `＊挙動問題あり` comment tree preserved.
- Added the rule that Codex response comments use `※` so they are distinguishable from user `＊` comments.

Runtime fixes:

- `group_no_ability_or_body` now treats only `ability_type` containing `常時` as the always-ability branch. BODY-zone activated abilities no longer satisfy the <常時> branch.
- Reorder popup drops on another card now insert before or after that card based on drag direction/card half, improving the shared top-k reorder UI.

Command fixes:

- `PL!-bp6-002`: deck top now uses no-ability μ's `PL!-bp3-015` and <常時> μ's `PL!-bp3-002`.

Commands run:

- `python3 -m py_compile ./llocg_ui/engine.py ./llocg_ui/server.py ./llocg_ui/engine_effect.py ./llocg_ui/effects/*.py`
- Internal engine-only smoke check for `PL!-bp6-002` no-ability / activated BODY / always BODY filtering.
- Embedded UI script syntax check.
- Debug memo bash block syntax check.
- Debug command forbidden-option scan.
- `git diff --check`

Results:

- `PL!-bp3-015` and `PL!-bp3-002` are candidates when they are the top two cards.
- `PL!-sd1-008` is not a candidate when paired with either the no-ability or <常時> μ's check card.

## 20260623l: distinct-group top-k up-to pick

Changed files:

- `llocg_ui/engine.py`
- `llocg_ui/server.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
- `docs/debug/loveca_debug_commands_current_updates_20260623.md`

Implemented route:

- `look_top_k_optional_distinct_group_upto_n`

Covered example:

- `PL!SP-bp5-007`: top 5, choose up to 3 cards, at most one per group name.

Runtime notes:

- Filtered `choose_from_topk` pending now supports `unique_by_group`.
- Engine resolution rejects multi-picks that contain duplicate group names, even if the UI is bypassed.
- The UI disables unselected candidates whose group name is already represented in the current selection.

Commands run:

- Internal matcher check for `PL!SP-bp5-007`.
- Internal engine-only smoke check for valid distinct-group picks and invalid duplicate-group picks.

Results:

- Matcher maps `PL!SP-bp5-007` to `look_top_k_optional_distinct_group_upto_n`.
- Valid picks across `Liella!`, `蓮ノ空`, and `虹ヶ咲` resolve to hand.
- Duplicate `Liella!` picks are rejected and the revealed pool is restored.

## 20260624a: top-k filtered pick to empty stage or hand

Changed files:

- `llocg_ui/engine.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
- `docs/debug/loveca_debug_commands_current_updates_20260623.md`

Implemented route:

- `look_top_k_optional_cost_le_group_member_stage_or_hand`

Covered example:

- `PL!SP-pb2-001`: top 5, choose up to 1 cost 4 or lower `Liella!` member, then move it to an empty stage area or to hand.

Runtime notes:

- `choose_from_topk` now supports `after_pick=stage_or_hand_empty_area` for single-card filtered picks.
- The selected card is removed from the revealed pool first; remaining revealed cards go to waiting room.
- `topk_stage_or_hand` pending lets the user choose `hand` or an empty `L`/`C`/`R` area. Stage placement does not pay play cost because it is effect placement.

Commands run:

- Internal matcher check for `PL!SP-pb2-001`.
- Internal engine-only smoke check for stage placement branch.
- Internal engine-only smoke check for hand branch.

Results:

- Matcher maps `PL!SP-pb2-001` to `look_top_k_optional_cost_le_group_member_stage_or_hand`.
- Cost 4 or lower `Liella!` members are candidates; cost 5 `Liella!` and non-`Liella!` cards are excluded.
- Selected candidate can be placed on an empty stage area or moved to hand.

## 20260624b: stage-cost lower draw 2 then hand topdeck

Changed files:

- `llocg_ui/engine.py`
- `llocg_ui/server.py`
- `llocg_ui/effects/registry.py`
- `llocg_ui/effects/live_start.py`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.md`
- `loveca_reports/loveca_topk_complex_family_audit_20260604a.csv`
- `docs/debug/loveca_debug_commands_current_updates_20260623.md`

Implemented routes:

- `live_start_my_cost_lower_draw2_hand_top1`
- `draw_then_hand_to_deck_top`

Covered example:

- `PL!N-bp4-009`: if own stage member cost total is lower than opponent's, draw 2, then put one hand card on deck top.

Runtime notes:

- When opponent stage cost is unavailable, the live-start route uses a `confirm_effect` pending, matching the existing draw-1 lower-cost route.
- Added `hand_to_deck_top` pending for effects that must put a hand card only on top, not top-or-bottom.

Commands run:

- Internal matcher check for `PL!N-bp4-009`.
- Internal engine-only smoke check for confirm -> draw 2 -> hand card to deck top.

Results:

- Matcher maps `PL!N-bp4-009` to `live_start_my_cost_lower_draw2_hand_top1`.
- Confirming the effect draws two cards and enqueues `hand_to_deck_top`.
- Resolving `hand_to_deck_top` moves the selected hand card to deck top.
