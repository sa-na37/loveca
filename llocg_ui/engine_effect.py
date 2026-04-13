# -*- coding: utf-8 -*-
# BUILD_TAG: engine_effect_hime_bp2batch2_no_live_flag_20260413d
from __future__ import annotations

"""llocg_ui.engine_effect

Claude向けの軽量効果拡張ファイル。

目的
----
- 現 runtime の正本は engine.py のまま維持する。
- 日常の新規効果実装は、できるだけこの小さいファイルだけで完結させる。
- server.py は .engine しか import しないため、engine.py 側 API は壊さない。

運用原則
--------
1. まずこのファイルだけを Claude に渡す。
2. handout / prompt も併せて渡すが、コード変更対象は原則このファイルのみ。
3. engine.py を編集するのは次の場合だけ:
   - 新しい pending kind を engine.py 側で UI/解決対応まで増やす必要がある。
   - 既存 helper / cmd / phase 遷移では表現できない。
   - 新しい dataclass field や state_json 契約の追加が必要。
4. UI の一時ブレード/ハート表示は StageSlot.temp_blade / temp_hearts が基本契約。
5. このファイルは engine.py を import しないこと。循環 import 防止のため、
   engine.py から globals() が渡される。

engine.py 側接続点
------------------
- _match_effect_template() の先頭で try_match_effect_template_ext() を呼ぶ。
- _apply_effect_by_rule() の先頭で try_apply_effect_by_rule_ext() を呼ぶ。
- このファイルは「拡張ルールがヒットした時だけ処理する」。
- 未対応なら None / False を返し、engine.py の既存巨大実装へフォールバックする。

Claude に渡す 3 点
------------------
- engine_effect.py   : このファイル（コード本体）
- handout            : runtime truth / UI 契約 / debug ルール / 対象カード最小DB
- prompt             : 今回の effect_template / 禁止事項 / 出力形式

最小 API 契約
-------------
try_match_effect_template_ext(eng, effect_text) -> Optional[(rule_dict, gd_dict)]
    - eng は engine.py の globals() dict
    - マッチしたら (rule, groupdict) を返す
    - 未対応なら None

try_apply_effect_by_rule_ext(eng, gs, rng, cards_db, rule, gd, ctx) -> bool
    - 自分の拡張ルールなら処理して True
    - 未対応なら False

実装方針
--------
- effect_template は exact match を第一選択にする。
  理由: 既存 regex 群と衝突しにくく、Claude 作業でも安全。
- 必要になった時だけ regex を使う。
- rule dict は最小限のキーだけ持つ:
    {"id": ..., "op": "__ext__", "ext_key": ...}
- helper はこのファイル内に小さく置く。共通化しすぎない。
- engine.py の既存 helper は eng["helper_name"] で使う。

注意
----
- このファイルに handout 相当の要点を残しておくが、長文化しすぎない。
- 対象カードの詳細 DB は handout 側に置く。ここには常設しない。
- 既存 UI 契約:
    slot.temp_blade: int
    slot.temp_hearts: {pink/red/yellow/green/blue/purple/all: int}
  を守る。
"""

from typing import Any, Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Extension rule table
# ---------------------------------------------------------------------------
# 通常の新規効果実装はここへ追加する。
# 形式:
#   {
#       "id": "human_readable_id",
#       "effect_template": "完全一致で扱う effect_template",
#       "ext_key": "dispatch key",
#   }
EXTRA_EFFECT_RULES = [
    # 既存
    {
        "id": "position_change_optional",
        "effect_template": "このメンバーをポジションチェンジしてもよい。",
        "ext_key": "position_change_optional",
    },
    # Prompt 17: PL!-bp3-006 西木野真姫 (ライブ開始時)
    {
        "id": "live_start_success_zone_count_x2_blade",
        "effect_template": "ライブ終了時まで、自分の成功ライブカード置き場にあるカード1枚につき、<(ブレード)><(ブレード)>を得る。",
        "ext_key": "live_start_success_zone_count_x2_blade",
    },
    # Prompt 24: PL!-bp4-001 高坂穂乃果 (ライブ開始時)
    {
        "id": "live_start_my_cost_lower_draw1",
        "effect_template": "自分ステージにいるメンバーのコストの合計が相手より低い場合、カードを1枚引く。",
        "ext_key": "live_start_my_cost_lower_draw1",
    },
    # Prompt 26: PL!-bp4-004 園田海未 (登場)
    {
        "id": "enter_success_score_ge6_activate2",
        "effect_template": "自分の成功ライブカード置き場にあるカードのスコアの合計が6以上の場合、エネルギーを2枚アクティブにする。",
        "ext_key": "enter_success_score_ge6_activate2",
    },
    # Prompt 31: PL!-bp4-016 東條希 (登場)
    {
        "id": "enter_success_score_ge3_draw1",
        "effect_template": "自分の成功ライブカード置き場にあるカードのスコアの合計が3以上の場合、カードを1枚引く。",
        "ext_key": "enter_success_score_ge3_draw1",
    },
    # Prompt 41: PL!-pb1-003 南ことり (登場) ※コストはエンジン側が pay_or_skip を積む想定
    {
        "id": "enter_printemps_count_activate_energy",
        "effect_template": "自分のステージにいる『Printemps』のメンバー1人につき、エネルギーを1枚アクティブにする。",
        "ext_key": "enter_printemps_count_activate_energy",
    },
    # Prompt 57: PL!-pb1-032 SENTIMENTAL StepS (ライブ成功時)
    {
        "id": "live_success_success_zone_has_mus_draw1",
        "effect_template": "自分の成功ライブカード置き場に『μ's』のカードがある場合、カードを1枚引く。",
        "ext_key": "live_success_success_zone_has_mus_draw1",
    },
    # Prompt 63: PL!-sd1-008 小泉花陽 (BODY 起動)
    {
        "id": "body_mill10",
        "effect_template": "自分のデッキの上からカードを10枚控え室に置く。",
        "ext_key": "body_mill10",
    },
    # Prompt 67: PL!HS-bp1-004 夕霧綴理 (ライブ開始時)
    {
        "id": "live_start_live_cards_count_x1_blade",
        "effect_template": "ライブ終了時まで、自分のライブ中のカード1枚につき、<(ブレード)>を得る。",
        "ext_key": "live_start_live_cards_count_x1_blade",
    },
    # Prompt 72: PL!HS-bp1-023 ド！ド！ド！ (ライブ成功時)
    {
        "id": "live_success_score_gt_opp_and_hasunosora_energy_wait",
        "effect_template": "ライブの合計スコアが相手より高く、かつ自分のステージに『蓮ノ空』のメンバーがいる場合、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。",
        "ext_key": "live_success_score_gt_opp_and_hasunosora_energy_wait",
    },
    # Prompt 77: PL!HS-bp2-005 大沢瑠璃乃 (ライブ開始時)
    {
        "id": "live_start_all_stage_filled_x2_blade",
        "effect_template": "自分のステージのエリアすべてにメンバーが登場している場合、ライブ終了時まで、<(ブレード)><(ブレード)>を得る。",
        "ext_key": "live_start_all_stage_filled_x2_blade",
    },
    # -----------------------------------------------------------------------
    # group3_A7B2_20260406a 新規追加
    # -----------------------------------------------------------------------
    # Prompt 6: PL!SP-bp4-008 若菜四季 (ライブ開始時, no-cost)
    # effect_template が先頭の "position_change_optional" と完全一致するため
    # 既存エントリを再利用。ここでは追加エントリ不要。
    # engine 側が ライブ開始時 no-cost として queue に積んでから dispatch される。
    # -----------------------------------------------------------------------
    # Prompt 69: PL!HS-bp1-006 藤島慈 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # 他メンバーがいる場合、好きなハートの色を1つ指定。ライブ終了時まで得る。
    {
        "id": "live_start_discard1_other_member_exists_choose_heart",
        "effect_template": "自分のステージにほかのメンバーがいる場合、好きなハートの色を1つ指定する。ライブ終了時まで、そのハートを1つ得る。",
        "ext_key": "live_start_other_member_exists_choose_heart",
    },
    # Prompt 14: PL!-bp3-003 南ことり (登場)
    # cost=このメンバーをウェイトにしてもよい → engine 側 self_wait pay_or_skip
    # 控え室から μ's のメンバーカードを1枚手札に加える
    {
        "id": "enter_self_wait_pick_mus_member_from_green",
        "effect_template": "自分の控え室から『μ's』のメンバーカードを1枚手札に加える。",
        "ext_key": "enter_pick_mus_member_from_green",
    },
    # Prompt 16: PL!-bp3-004 園田海未 (ライブ開始時)
    # 成功置き場にカードがある場合のみ発動可
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # 控え室から μ's のライブカードを1枚手札に加える
    {
        "id": "live_start_success_zone_exists_discard1_pick_mus_live_from_green",
        "effect_template": "自分の控え室から『μ's』のライブカードを1枚手札に加える。",
        "ext_key": "live_start_pick_mus_live_from_green",
    },
    # Prompt 60: PL!-sd1-003 南ことり (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # <(桃)>/<(黄)>/<(紫)> のうち1つを選ぶ。ライブ終了時まで得る。
    {
        "id": "live_start_discard1_choose_pink_yellow_purple_heart",
        "effect_template": "<(桃)>/<(黄)>/<(紫)>のうち1つを選ぶ。ライブ終了時まで、選んだハートを1つ得る。",
        "ext_key": "live_start_choose_pinkYellowPurple_heart",
    },
    {
        "id": "live_start_discard1_choose_pink_yellow_purple_heart_v7h",
        "effect_template": "<(桃)>か<(黄)>か<(紫)>のうち、1つを選ぶ。ライブ終了時まで、選んだハートを1つ得る。",
        "ext_key": "live_start_choose_pinkYellowPurple_heart",
    },
    {
        "id": "body_pick_live_req_yellow_ge3_from_green",
        "effect_template": "控え室から必要ハートに<(黄)>を3以上含むライブカードを1枚手札に加える。",
        "ext_key": "body_pick_live_req_yellow_ge3_from_green",
    },
    {
        "id": "body_pick_live_req_pink_ge3_from_green",
        "effect_template": "自分の控え室から必要ハートに<(桃)>を3以上含むライブカードを1枚手札に加える。",
        "ext_key": "body_pick_live_req_pink_ge3_from_green",
    },
    # Prompt 73: PL!HS-bp2-001 日野下花帆 (起動)
    # コスト: <(E)><(E)> → engine 側起動コスト処理
    # 控え室からスコア3以下の 蓮ノ空 ライブカードを1枚手札に加える
    {
        "id": "body_pick_hasunosora_live_score_le3_from_green",
        "effect_template": "自分の控え室からスコア3以下の『蓮ノ空』のライブカードを1枚手札に加える。",
        "ext_key": "body_pick_hasunosora_live_score_le3_from_green",
    },
    # Prompt 76: PL!HS-bp2-005 大沢瑠璃乃 (登場)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # 他メンバーがいる場合、控え室から みらくらぱーく！ のカードを1枚手札に加える
    {
        "id": "enter_discard1_other_member_exists_pick_mirakupark_from_green",
        "effect_template": "自分のステージにほかのメンバーがいる場合、自分の控え室から『みらくらぱーく！』のカードを1枚手札に加える。",
        "ext_key": "enter_other_member_exists_pick_mirakupark_from_green",
    },
    {
        "id": "enter_main_pay2_faceup_live_to_set_reduce_next_live_set",
        "effect_template": "自分の控え室からライブカードを1枚、表向きにライブカード置き場に置く。次のライブカードセットフェイズで自分がライブカード置き場に置けるカード枚数の上限が1枚減る。",
        "ext_key": "enter_main_pay2_faceup_live_to_set_reduce_next_live_set",
    },
    # Prompt 27: PL!-bp4-005 星空凛 (ライブ開始時)
    # ブレード5以上の μ's メンバーがいない場合、センター以外へ強制ポジションチェンジ
    {
        "id": "live_start_no_mus_blade5_force_position_change_not_center",
        "effect_template": "自分のステージに<(ブレード)>を5つ以上持つ『μ's』のメンバーがいない場合、このメンバーはセンターエリア以外にポジションチェンジする。",
        "ext_key": "live_start_no_mus_blade5_force_not_center",
    },
    # Prompt 56: PL!-pb1-030 Cutie Panther (ライブ成功時)
    # ステージに名前の異なる BiBi が2人以上 → 控え室から BiBi メンバー1枚手札へ
    {
        "id": "live_success_bibi_2diff_pick_bibi_member_from_green",
        "effect_template": "自分のステージに名前の異なる『BiBi』のメンバーが2人以上いる場合、自分の控え室から『BiBi』のメンバーカードを1枚手札に加える。",
        "ext_key": "live_success_bibi_2diff_pick_bibi_member_from_green",
    },

    # -----------------------------------------------------------------------
    # bp2_batch2_20260410b Claude merge (GPT debugged)
    # -----------------------------------------------------------------------
    {
        "id": "enter_sayaka_pick_cost_le2_member_from_green_up_to_2",
        "effect_template": "自分の控え室からコスト2以下のメンバーカードを2枚まで手札に加える。",
        "ext_key": "enter_pick_cost_le2_member_from_green_up_to_2",
    },
    {
        "id": "body_sayaka_higher_cost_member_exists_blade3",
        "effect_template": "自分のステージに、このメンバーよりコストの大きいメンバーがいる場合、<(ブレード)><(ブレード)><(ブレード)>を得る。",
        "ext_key": "body_higher_cost_member_exists_blade3",
    },
    {
        "id": "live_start_kozue_bp2003_reorder_top3",
        "effect_template": "自分のデッキの上からカードを3枚見る。その中から好きな枚数を好きな順番でデッキの上に置き、残りを控え室に置く。",
        "ext_key": "reorder_from_top3",
    },
    {
        "id": "body_tsukasa_mirakupark_count_blade",
        "effect_template": "自分のステージにいるほかの『みらくらぱーく！』のメンバー1人につき、<(ブレード)>を得る。",
        "ext_key": "body_mirakupark_others_count_blade",
    },
    {
        "id": "enter_kaho_bp2010_top5_member_optional",
        "effect_template": "自分のデッキの上からカードを5枚見る。その中からメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",
        "ext_key": "enter_top5_member_optional_pick",
    },
    {
        "id": "body_kozue_bp2012_stage_to_green_top5_member_optional",
        "effect_template": "このメンバーがステージから控え室に置かれたとき、自分のデッキの上からカードを5枚見る。その中からメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",
        "ext_key": "body_stage_to_green_top5_member_optional",
    },
    {
        "id": "body_tsuzuri_bp2013_stage_to_green_top5_live_optional",
        "effect_template": "このメンバーがステージから控え室に置かれたとき、自分のデッキの上からカードを5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",
        "ext_key": "body_stage_to_green_top5_live_optional",
    },
    {
        "id": "enter_ginko_bp2016_reorder_top2",
        "effect_template": "自分のデッキの上からカードを2枚見る。その中から好きな枚数を好きな順番でデッキの上に置き、残りを控え室に置く。",
        "ext_key": "reorder_from_top2",
    },
    {
        "id": "enter_kosuzu_bp2017_green_ge10_draw1",
        "effect_template": "自分の控え室にカードが10枚以上ある場合、カードを1枚引く。",
        "ext_key": "enter_green_ge10_draw1",
    },
    {
        "id": "enter_rurino_bp2014_draw1_cannot_live_until_end_of_live",
        "effect_template": "カードを1枚引く。ライブ終了時まで、自分はライブできない。",
        "ext_key": "enter_draw1_and_cannot_live_until_end_of_live",
    },
    # -----------------------------------------------------------------------
    # group2_single_target_20260402 新規追加
    # -----------------------------------------------------------------------
    # Prompt 22: PL!-bp3-026 Oh,Love&Peace! (ライブ開始時)
    # cost=手札を2枚控え室に置いてもよい → engine 側 pay_or_skip が積む想定
    {
        "id": "live_start_pick_stage_member_blade3",
        "effect_template": "ライブ終了時まで、自分のステージにいるメンバー1人は<(ブレード)><(ブレード)><(ブレード)>を得る。",
        "ext_key": "live_start_pick_stage_member_blade3",
    },
    # Prompt 30: PL!-bp4-013 園田海未 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    {
        "id": "live_start_pick_other_stage_member_pink1",
        "effect_template": "ライブ終了時まで、自分のステージにいるこのメンバー以外のメンバー1人は、<(桃)>を得る。",
        "ext_key": "live_start_pick_other_stage_member_pink1",
    },
    # Prompt 32: PL!-bp4-017 小泉花陽 (ライブ開始時)
    # cost=このメンバーをウェイトにしてもよい → engine 側 pay_or_skip
    # センターの μ's メンバーにブレード付与（対象が固定なので選択不要）
    {
        "id": "live_start_center_mus_blade1",
        "effect_template": "ライブ終了時まで、自分のセンターエリアにいる『μ's』のメンバーは、<(ブレード)>を得る。",
        "ext_key": "live_start_center_mus_blade1",
    },
    # Prompt 35: PL!-bp4-020 Love wing bell (ライブ開始時)
    # ステージが μ's のみ → メンバー1人をポジションチェンジさせてもよい
    {
        "id": "live_start_mus_only_pick_member_position_change",
        "effect_template": "自分のステージにいるメンバーが『μ's』のみの場合、自分のステージにいるメンバー1人をポジションチェンジさせてもよい。",
        "ext_key": "live_start_mus_only_pick_member_position_change",
    },
    # Prompt 37: PL!-bp4-024 小夜啼鳥恋詩 (ライブ開始時)
    # cost なし → μ's メンバー1人選択してブレード付与
    {
        "id": "live_start_pick_mus_stage_member_blade1",
        "effect_template": "ライブ終了時まで、自分のステージにいる『μ's』のメンバー1人は、<(ブレード)>を得る。",
        "ext_key": "live_start_pick_mus_stage_member_blade1",
    },
    # Prompt 46: PL!-pb1-010 高坂穂乃果 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # このメンバー以外全員に +1ブレード（選択なし、対象が複数固定）
    {
        "id": "live_start_other_stage_members_blade1",
        "effect_template": "ライブ終了時まで、自分のステージにいるほかのメンバーは<(ブレード)>を得る。",
        "ext_key": "live_start_other_stage_members_blade1",
    },
    # Prompt 48: PL!-pb1-012 南ことり (登場)
    # cost なし → Printemps のメンバー1人までアクティブ化（ウェイト状態が対象）
    {
        "id": "enter_printemps_activate_up_to_1",
        "effect_template": "自分のステージにいる『Printemps』のメンバーを1人までアクティブにする。",
        "ext_key": "enter_printemps_activate_up_to_1",
    },
    # bp2_batch3_local_20260413f
    {
        "id": "enter_sayaka_bp2011_mill5",
        "effect_template": "デッキの上からカードを5枚控え室に置く。",
        "ext_key": "enter_mill5",
    },
    {
        "id": "body_megumi_bp2015_leave_stage_draw2_discard1",
        "effect_template": "このメンバーがステージから控え室に置かれたとき、カードを2枚引き、手札を1枚控え室に置く。",
        "ext_key": "body_leave_stage_draw2_discard1",
    },

    # Prompt 80: PL!HS-bp2-007 百生吟子 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # 控え室に置いたカードがメンバーカードなら、同名ステージメンバーに green+1 blade+1
    {
        "id": "live_start_discard_member_same_name_green1_blade1",
        "effect_template": "これにより控え室に置いたカードがメンバーカードの場合、控え室に置いたカードと同じ名前を持つメンバー1人は、ライブ終了時まで、<(緑)><(ブレード)>を得る。",
        "ext_key": "live_start_discard_member_same_name_green1_blade1",
    },
]


def _norm_ws(text: str) -> str:
    """Collapse whitespace for effect_template comparison.

    Steps:
      1. Collapse every run of whitespace (including newlines) to a single space.
      2. Remove spaces that appear immediately before or after icon tokens of the
         form ``<(...)>`` — these spaces are an artefact of the card DB inserting
         newlines around icon tokens and must not prevent matching against the
         one-liner form used in EXTRA_EFFECT_RULES.
    """
    import re as _re
    s = _re.sub(r'\s+', ' ', (text or "").strip())
    # Remove space before icon token: "は、 <(ブレード)>" -> "は、<(ブレード)>"
    s = _re.sub(r' (<\([^)]*\)>)', r'\1', s)
    # Remove space after icon token: "<(ブレード)> を" -> "<(ブレード)>を"
    s = _re.sub(r'(<\([^)]*\)>) ', r'\1', s)
    return s


def try_match_effect_template_ext(
    eng: Dict[str, Any],
    effect_text: str,
) -> Optional[Tuple[Dict[str, Any], Dict[str, str]]]:
    """Match extension-owned effect templates.

    Matching strategy:
      1. Exact match after strip()
      2. Whitespace-normalized match
      3. Targeted fragment fallback for cards whose DB text is split across
         multiple clauses, or whose first clause is a cost-only raw fragment.
    """
    s = (effect_text or "").strip()
    if not s:
        return None

    s_norm = _norm_ws(s)

    for r in EXTRA_EFFECT_RULES:
        tpl = str(r.get("effect_template", "") or "").strip()
        if not tpl:
            continue
        if s == tpl:
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, {})
        if s_norm == _norm_ws(tpl):
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, {})

    # cards_compiled_v7b splits some abilities into multiple clauses.
    # Match the actual clause fragment that engine.py sees.
    fragment_rules = [
        # Prompt 60: cost-only split clause should be matched narrowly.
        # Do NOT match broader sentences like PL!-bp3-004 that also contain
        # "手札を1枚控え室に置いてもよい" but are different effects.
        ("live_start_choose_pinkYellowPurple_heart",
         lambda t: (_norm_ws(t) == _norm_ws("手札を1枚控え室に置いてもよい："))),
        # Prompt 27: second clause is the unique condition/result fragment
        ("live_start_no_mus_blade5_force_not_center",
         lambda t: ("を5つ以上持つ『μ's』のメンバーがいない場合" in t and "センターエリア以外にポジションチェンジする。" in t)),
        # Prompt 16: DB keeps the whole conditional sentence in one clause
        ("live_start_pick_mus_live_from_green",
         lambda t: ("成功カード置き場にカードがある場合" in t and "『μ's』のライブカードを1枚手札に加える。" in t)),
        # Prompt 14: exact should normally hit, but keep a safe fallback
        ("enter_pick_mus_member_from_green",
         lambda t: ("『μ's』のメンバーカードを1枚手札に加える。" in t and "控え室から" in t)),
        # bp2-015 / leave-stage trigger text may arrive as the full sentence
        ("body_leave_stage_draw2_discard1",
         lambda t: ("ステージから控え室に置かれたとき" in t and "カードを2枚引き" in t and "手札を1枚控え室に置く。" in t)),
    ]
    for ext_key, pred in fragment_rules:
        try:
            if pred(s_norm):
                return ({"id": ext_key, "op": "__ext__", "ext_key": ext_key}, {})
        except Exception:
            pass
    return None

    s_norm = _norm_ws(s)

    for r in EXTRA_EFFECT_RULES:
        tpl = str(r.get("effect_template", "") or "").strip()
        if not tpl:
            continue
        if s == tpl:
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, {})
        if s_norm == _norm_ws(tpl):
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, {})

    fuzzy_rules = [
        ("enter_pick_mus_member_from_green",
         ["控え室から『μ's』のメンバーカードを1枚手札に加える。"]),
        ("live_start_pick_mus_live_from_green",
         ["控え室から『μ's』のライブカードを1枚手札に加える。"]),
        ("live_start_choose_pinkYellowPurple_heart",
         ["<(桃)>", "<(黄)>", "<(紫)>", "選んだハートを1つ得る。"]),
        ("live_start_no_mus_blade5_force_not_center",
         ["<(ブレード)>", "5つ以上持つ『μ's』のメンバーがいない場合", "センターエリア以外にポジションチェンジする。"]),
        ("body_pick_live_req_yellow_ge3_from_green",
         ["必要ハートに<(黄)>", "3以上含むライブカード", "1枚手札に加える。"]),
        ("body_pick_live_req_pink_ge3_from_green",
         ["必要ハートに<(桃)>", "3以上含むライブカード", "1枚手札に加える。"]),
    ]
    for ext_key, needles in fuzzy_rules:
        if all(_norm_ws(nd) in s_norm for nd in needles):
            return ({"id": ext_key, "op": "__ext__", "ext_key": ext_key}, {})
    return None

    s_norm = _norm_ws(s)

    for r in EXTRA_EFFECT_RULES:
        tpl = str(r.get("effect_template", "") or "").strip()
        if not tpl:
            continue
        # 1. exact match (highest priority, no change to existing behaviour)
        if s == tpl:
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, {})
        # 2. whitespace-normalised fallback
        if s_norm == _norm_ws(tpl):
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, {})
    return None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _add_temp_blade(eng: Dict[str, Any], slot: Any, n: int) -> None:
    if not slot or n <= 0:
        return
    try:
        slot.temp_blade = int(getattr(slot, "temp_blade", 0) or 0) + int(n)
        slot.temp_until = "end_of_live"
    except Exception:
        pass


def _add_temp_hearts(eng: Dict[str, Any], slot: Any, hearts: Dict[str, int]) -> None:
    if not slot or not hearts:
        return
    try:
        cur = dict(getattr(slot, "temp_hearts", {}) or {})
    except Exception:
        cur = {}
    for k, v in (hearts or {}).items():
        try:
            iv = int(v or 0)
        except Exception:
            iv = 0
        if iv <= 0:
            continue
        cur[str(k)] = int(cur.get(str(k), 0) or 0) + iv
    try:
        slot.temp_hearts = cur
        slot.temp_until = "end_of_live"
    except Exception:
        pass


def _active_stage_slots(gs: Any) -> list:
    """Return list of active (non-None) StageSlots."""
    out = []
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                v = st.get(pos)
                if v is not None and bool(getattr(v, "active", False)):
                    out.append(v)
    except Exception:
        pass
    return out


def _all_stage_slots_filled(gs: Any) -> bool:
    """Return True if all 3 stage positions (L/C/R) have an active member."""
    try:
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return False
        for pos in ("L", "C", "R"):
            v = st.get(pos)
            if v is None or not bool(getattr(v, "cardnumber", None)):
                return False
        return True
    except Exception:
        return False


def _src_slot(gs: Any, ctx: Dict[str, Any]) -> Any:
    """Return the StageSlot for the source member, or None."""
    try:
        src_pos = str(
            (ctx or {}).get("src_pos") or (ctx or {}).get("pos") or ""
        ).upper()
        if src_pos not in ("L", "C", "R"):
            return None
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            return st.get(src_pos)
    except Exception:
        pass
    return None


def _success_zone_cards(gs: Any) -> list:
    """Return list of cards in the success live zone."""
    try:
        z = getattr(gs, "success_zone", None) or []
        if not isinstance(z, list):
            z = list(z)
        return z
    except Exception:
        return []


def _card_score(card: Any, cards_db: Dict[str, Any]) -> int:
    """Return the score of a card (from cards_db or card attribute)."""
    try:
        cn = str(getattr(card, "cardnumber", None) or card or "")
        info = cards_db.get(cn)
        if info is not None:
            s = getattr(info, "score", None)
            if s is None:
                s = (info if isinstance(info, dict) else {}). get("score")
            if s is not None and str(s).strip() not in ("", "None"):
                return int(str(s).strip())
        # fallback: card itself may have score attr
        sv = getattr(card, "score", None)
        if sv is not None and str(sv).strip() not in ("", "None"):
            return int(str(sv).strip())
    except Exception:
        pass
    return 0


def _lookup_cardinfo(cards_db: Dict[str, Any], card: Any) -> Any:
    try:
        cn = str(getattr(card, "cardnumber", None) or card or "").strip()
        if not cn:
            return None
        info = cards_db.get(cn)
        if info is not None:
            return info
        low = cn.lower()
        for k, v in (cards_db or {}).items():
            try:
                if str(k).strip().lower() == low:
                    return v
            except Exception:
                continue
    except Exception:
        pass
    return None

def _card_group(card: Any, cards_db: Dict[str, Any]) -> str:
    """Return the group string of a card."""
    try:
        info = _lookup_cardinfo(cards_db, card)
        if info is not None:
            g = getattr(info, "group", None)
            if g is None:
                g = (info if isinstance(info, dict) else {}).get("group")
            if g:
                return str(g)
        g = getattr(card, "group", None)
        if g:
            return str(g)
    except Exception:
        pass
    return ""


def _card_unit(card: Any, cards_db: Dict[str, Any]) -> str:
    """Return the unit string of a card."""
    try:
        info = _lookup_cardinfo(cards_db, card)
        if info is not None:
            u = getattr(info, "unit", None)
            if u is None:
                u = (info if isinstance(info, dict) else {}).get("unit")
            if u:
                return str(u)
        u = getattr(card, "unit", None)
        if u:
            return str(u)
    except Exception:
        pass
    return ""


def _card_cost(card: Any, cards_db: Dict[str, Any]) -> int:
    """Return the cost of a card as int."""
    try:
        cn = str(getattr(card, "cardnumber", None) or card or "")
        info = cards_db.get(cn)
        if info is not None:
            c = getattr(info, "cost", None)
            if c is None:
                c = (info if isinstance(info, dict) else {}).get("cost")
            if c is not None and str(c).strip() not in ("", "None"):
                return int(str(c).strip())
        cv = getattr(card, "cost", None)
        if cv is not None and str(cv).strip() not in ("", "None"):
            return int(str(cv).strip())
    except Exception:
        pass
    return 0


def _card_type_norm(card: Any, cards_db: Dict[str, Any]) -> str:
    """Return the normalized card type string (MEMBER / LIVE / etc.).

    Conservative rule:
    - Prefer explicit normalized/raw DB type when present.
    - Only fall back to LIVE when the row is obviously LIVE-shaped.
    - Never treat score=0 on MEMBER rows as evidence for LIVE.
    """
    def _infer_live_from_shape(info: Any) -> bool:
        try:
            req = getattr(info, 'required_hearts', None)
            if req is None and isinstance(info, dict):
                req = info.get('required_hearts')
            if isinstance(req, dict) and any(int(v or 0) > 0 for v in req.values()):
                return True
        except Exception:
            pass
        try:
            score = getattr(info, 'score', None)
            if score is None and isinstance(info, dict):
                score = info.get('score')
            score_i = int(score or 0)
        except Exception:
            score_i = 0
        try:
            cost = getattr(info, 'cost', None)
            if cost is None and isinstance(info, dict):
                cost = info.get('cost')
            cost_i = int(cost or 0)
        except Exception:
            cost_i = 0
        try:
            blade = getattr(info, 'blade', None)
            if blade is None and isinstance(info, dict):
                blade = info.get('blade')
            blade_i = int(blade or 0)
        except Exception:
            blade_i = 0
        try:
            base = getattr(info, 'base_hearts', None)
            if base is None and isinstance(info, dict):
                base = info.get('base_hearts')
            has_base = isinstance(base, dict) and any(int(v or 0) > 0 for v in base.values())
        except Exception:
            has_base = False
        return bool(score_i > 0 and cost_i <= 0 and blade_i <= 0 and not has_base)

    try:
        info = _lookup_cardinfo(cards_db, card)
        if info is not None:
            t = getattr(info, "card_type_norm", None)
            if t is None:
                t = (info if isinstance(info, dict) else {}).get("card_type_norm")
            if t:
                ts = str(t).strip().upper()
                if ts in ("MEMBER", "LIVE", "ENERGY"):
                    if ts == 'MEMBER' and _infer_live_from_shape(info):
                        return 'LIVE'
                    return ts

            raw = getattr(info, "card_type_raw", None)
            if raw is None:
                raw = (info if isinstance(info, dict) else {}).get("card_type_raw")
            if raw is None:
                raw = getattr(info, "type", None)
            if raw is None:
                raw = (info if isinstance(info, dict) else {}).get("type")
            if raw:
                s = str(raw).strip().upper()
                jp = str(raw).strip()
                if s in ("MEMBER", "LIVE", "ENERGY"):
                    if s == 'MEMBER' and _infer_live_from_shape(info):
                        return 'LIVE'
                    return s
                if jp == "メンバー":
                    return 'LIVE' if _infer_live_from_shape(info) else "MEMBER"
                if jp == "ライブ":
                    return "LIVE"
                if jp == "エネルギー":
                    return "ENERGY"

        t = getattr(card, "card_type_norm", None)
        if t:
            return str(t).strip().upper()

        raw = getattr(card, "card_type_raw", None) or getattr(card, "type", None)
        if raw:
            s = str(raw).strip().upper()
            jp = str(raw).strip()
            if s in ("MEMBER", "LIVE", "ENERGY"):
                return s
            if jp == "メンバー":
                return "MEMBER"
            if jp == "ライブ":
                return "LIVE"
            if jp == "エネルギー":
                return "ENERGY"
    except Exception:
        pass
    return ""


def _card_name(card: Any, cards_db: Dict[str, Any]) -> str:
    """Return the cardname string of a card."""
    try:
        info = _lookup_cardinfo(cards_db, card)
        if info is not None:
            n = getattr(info, "cardname", None)
            if n is None:
                n = (info if isinstance(info, dict) else {}).get("cardname")
            if n:
                return str(n)
        n = getattr(card, "cardname", None) or getattr(card, "name", None)
        if n:
            return str(n)
    except Exception:
        pass
    return ""


def _stage_member_cost_sum(gs: Any, cards_db: Dict[str, Any]) -> int:
    """Sum of costs of all active stage members."""
    total = 0
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    total += _card_cost(slot, cards_db)
    except Exception:
        pass
    return total


def _opp_stage_member_cost_sum(gs: Any, cards_db: Dict[str, Any]) -> int:
    """Sum of costs of all opponent active stage members."""
    total = 0
    try:
        opp = getattr(gs, "opponent", None) or getattr(gs, "opp", None)
        if opp is None:
            return 0
        st = getattr(opp, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    total += _card_cost(slot, cards_db)
    except Exception:
        pass
    return total


def _has_opponent_state(gs: Any) -> bool:
    """Best-effort check whether opponent state exists in this runtime."""
    try:
        opp = getattr(gs, "opponent", None) or getattr(gs, "opp", None)
        if opp is None:
            return False
        return True
    except Exception:
        return False


def _activate_energy(gs: Any, n: int) -> int:
    """Move up to n energy from energy_wait to energy_active. Returns count moved.
    energy_active / energy_wait are int fields in GameState (not lists).
    """
    moved = 0
    try:
        wait = int(getattr(gs, "energy_wait", 0) or 0)
        take = min(max(0, n), wait)
        if take > 0:
            gs.energy_wait -= take
            gs.energy_active += take
            moved = take
    except Exception:
        pass
    return moved


def _draw_cards(eng: Dict[str, Any], gs: Any, n: int) -> int:
    """Draw n cards from deck to hand. Returns count drawn."""
    drawn = 0
    try:
        # Try using engine helper if available
        draw_fn = eng.get("_draw") or eng.get("draw_cards")
        if callable(draw_fn):
            draw_fn(gs, n)
            return n
        # Fallback: direct list manipulation
        deck = getattr(gs, "deck", None)
        hand = getattr(gs, "hand", None)
        if deck is None or hand is None:
            return 0
        for _ in range(n):
            if not deck:
                break
            hand.append(deck.pop(0))
            drawn += 1
    except Exception:
        pass
    return drawn


def _live_in_progress_cards(gs: Any) -> list:
    """Return list of cards currently in the live zone (ライブ中のカード)."""
    try:
        # Try common field names
        for attr in ("live_zone", "live_cards", "current_live_cards", "live_area"):
            z = getattr(gs, attr, None)
            if z is not None:
                return list(z) if not isinstance(z, list) else z
        # Fallback: try live dict
        live = getattr(gs, "live", None)
        if live is not None:
            cards = getattr(live, "cards", None) or (live if isinstance(live, dict) else {}).get("cards")
            if cards is not None:
                return list(cards)
    except Exception:
        pass
    return []


def _live_score_total(gs: Any) -> int:
    """Return current live total score (自分)."""
    try:
        for attr in ("live_score", "score", "current_score"):
            v = getattr(gs, attr, None)
            if v is not None:
                return int(v)
        live = getattr(gs, "live", None)
        if live is not None:
            v = getattr(live, "score", None) or (live if isinstance(live, dict) else {}).get("score")
            if v is not None:
                return int(v)
    except Exception:
        pass
    return 0


def _opp_live_score_total(gs: Any) -> int:
    """Return opponent live total score."""
    try:
        for attr in ("opp_live_score", "opp_score"):
            v = getattr(gs, attr, None)
            if v is not None:
                return int(v)
        opp = getattr(gs, "opponent", None) or getattr(gs, "opp", None)
        if opp is not None:
            for attr in ("live_score", "score", "current_score"):
                v = getattr(opp, attr, None)
                if v is not None:
                    return int(v)
    except Exception:
        pass
    return 0


def _stage_has_group(gs: Any, cards_db: Dict[str, Any], group_name: str) -> bool:
    """Return True if any active stage member belongs to group_name."""
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    if _card_group(slot, cards_db) == group_name:
                        return True
    except Exception:
        pass
    return False


def _stage_all_group(gs: Any, cards_db: Dict[str, Any], group_name: str) -> bool:
    """Return True if ALL occupied stage positions belong to group_name."""
    try:
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return False
        found_any = False
        for pos in ("L", "C", "R"):
            slot = st.get(pos)
            if slot is None or not bool(getattr(slot, "cardnumber", None)):
                continue
            found_any = True
            if _card_group(slot, cards_db) != group_name:
                return False
        return found_any
    except Exception:
        return False


def _stage_unit_count(gs: Any, cards_db: Dict[str, Any], unit_name: str) -> int:
    """Count active stage members belonging to unit_name."""
    count = 0
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    if _card_unit(slot, cards_db) == unit_name:
                        count += 1
    except Exception:
        pass
    return count


def _stage_positions_with_group(gs: Any, cards_db: Dict[str, Any], group_name: str) -> list:
    """Return list of (pos, slot) tuples for stage members matching group_name."""
    result = []
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    if _card_group(slot, cards_db) == group_name:
                        result.append((pos, slot))
    except Exception:
        pass
    return result


def _stage_positions_with_unit(gs: Any, cards_db: Dict[str, Any], unit_name: str) -> list:
    """Return list of (pos, slot) tuples for stage members matching unit_name."""
    result = []
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    if _card_unit(slot, cards_db) == unit_name:
                        result.append((pos, slot))
    except Exception:
        pass
    return result


def _stage_positions_all_occupied(gs: Any) -> list:
    """Return list of (pos, slot) tuples for all occupied stage positions."""
    result = []
    try:
        st = getattr(gs, "stage", None)
        if isinstance(st, dict):
            for pos in ("L", "C", "R"):
                slot = st.get(pos)
                if slot is not None and bool(getattr(slot, "cardnumber", None)):
                    result.append((pos, slot))
    except Exception:
        pass
    return result


def _green_room_top(gs: Any) -> Any:
    """Return the most recently added card in green_room (控え室の最上位), or None."""
    try:
        gr = getattr(gs, "green_room", None)
        if gr is None:
            gr = (
                getattr(gs, "waiting_room", None)
                or getattr(gs, "graveyard", None)
                or getattr(gs, "discard", None)
            )
        if gr and isinstance(gr, list) and len(gr) > 0:
            return gr[-1]
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# group3 helpers
# ---------------------------------------------------------------------------

def _green_room_list(gs: Any) -> list:
    """Return the green_room (控え室) list, trying common field names."""
    try:
        for attr in ("green_room", "waiting_room", "graveyard", "discard"):
            gr = getattr(gs, attr, None)
            if gr is not None and isinstance(gr, list):
                return gr
    except Exception:
        pass
    return []


def _label_matches_group_or_unit(card: Any, cards_db: Dict[str, Any], label: str) -> bool:
    """Best-effort matcher for labels that may live in group or unit.
    Accept exact match or containment in either field.
    """
    try:
        lab = str(label or "").strip()
        if not lab:
            return False
        g = str(_card_group(card, cards_db) or "").strip()
        u = str(_card_unit(card, cards_db) or "").strip()
        return (g == lab) or (u == lab) or (lab in g if g else False) or (lab in u if u else False)
    except Exception:
        return False


def _green_room_members_by_group(gs: Any, cards_db: Dict[str, Any], group_name: str) -> list:
    """Return list of MEMBER cards in green_room belonging to group_name/unit_name."""
    result = []
    for card in _green_room_list(gs):
        try:
            if _card_type_norm(card, cards_db) == "MEMBER" and _label_matches_group_or_unit(card, cards_db, group_name):
                result.append(card)
        except Exception:
            pass
    return result


def _green_room_lives_by_group(gs: Any, cards_db: Dict[str, Any], group_name: str) -> list:
    """Return list of LIVE cards in green_room belonging to group_name/unit_name."""
    result = []
    for card in _green_room_list(gs):
        try:
            if _card_type_norm(card, cards_db) == "LIVE" and _label_matches_group_or_unit(card, cards_db, group_name):
                result.append(card)
        except Exception:
            pass
    return result


def _green_room_lives_by_group_score_le(
    gs: Any, cards_db: Dict[str, Any], group_name: str, score_max: int
) -> list:
    """Return LIVE cards in green_room with group_name and score <= score_max."""
    result = []
    for card in _green_room_lives_by_group(gs, cards_db, group_name):
        try:
            if _card_score(card, cards_db) <= score_max:
                result.append(card)
        except Exception:
            pass
    return result


def _green_room_cards_by_group_any_type(gs: Any, cards_db: Dict[str, Any], group_name: str) -> list:
    """Return cards of any type in green_room belonging to group_name/unit_name."""
    result = []
    for card in _green_room_list(gs):
        try:
            if _label_matches_group_or_unit(card, cards_db, group_name):
                result.append(card)
        except Exception:
            pass
    return result

def _card_required_hearts(card: Any, cards_db: Dict[str, Any]) -> Dict[str, int]:
    try:
        info = _lookup_cardinfo(cards_db, card)
        if info is not None:
            d = getattr(info, 'required_hearts', None)
            if d is None and isinstance(info, dict):
                d = info.get('required_hearts')
            if isinstance(d, dict):
                return {str(k): int(v or 0) for k, v in d.items()}
    except Exception:
        pass
    return {}


def _green_room_lives_with_required_heart_ge(gs: Any, cards_db: Dict[str, Any], color: str, n: int) -> list:
    result = []
    key = str(color or '').strip().lower()
    for card in _green_room_list(gs):
        try:
            if _card_type_norm(card, cards_db) != 'LIVE':
                continue
            req = _card_required_hearts(card, cards_db)
            if int(req.get(key, 0) or 0) >= int(n or 0):
                result.append(card)
        except Exception:
            pass
    return result


def _enqueue_pick_live_req_heart_from_green(gs: Any, cards_db: Dict[str, Any], color: str, n: int, src: str) -> bool:
    cands = _green_room_lives_with_required_heart_ge(gs, cards_db, color, n)
    if not cands:
        try:
            gs.log.append(f"[AUTO_EXT] no LIVE in green_room with required {color}>={n} ({src})")
        except Exception:
            pass
        return True
    if len(cands) == 1:
        ok = _move_card_from_green_to_hand(gs, cands[0])
        cn_str = str(getattr(cands[0], 'cardnumber', None) or cands[0] or '')
        try:
            gs.log.append(f"[AUTO_EXT] green->hand {cn_str} ({src}) ok={ok}")
        except Exception:
            pass
        return True
    cns = [str(getattr(c, 'cardnumber', None) or c or '') for c in cands]
    payload = {
        'kind': 'pick_live_from_green',
        'text': f"控え室の必要ハートに<{color}>を{n}以上含むライブカードを1枚手札に加える",
        'options': cns,
    }
    try:
        getattr(gs, 'pending').append(payload)
        gs.log.append(f"[PENDING] pick req-heart live from green color={color} n={n} opts={cns}")
    except Exception:
        pass
    return True


def _move_card_from_green_to_hand(gs: Any, card: Any) -> bool:
    """Remove card from green_room and add to hand. Returns True on success."""
    try:
        gr = _green_room_list(gs)
        if card in gr:
            gr.remove(card)
        else:
            # fallback: try to find by cardnumber
            cn = str(getattr(card, "cardnumber", None) or card or "")
            found = None
            for c in list(gr):
                if str(getattr(c, "cardnumber", None) or c or "") == cn:
                    found = c
                    break
            if found is None:
                return False
            gr.remove(found)
            card = found
        hand = getattr(gs, "hand", None)
        if hand is None:
            return False
        hand.append(card)
        return True
    except Exception:
        return False


def _move_live_from_green_to_set_zone(gs: Any, card: Any) -> bool:
    """Remove LIVE card from green_room and append to set_zone (face-up by current UI contract)."""
    try:
        gr = _green_room_list(gs)
        found = None
        if card in gr:
            found = card
        else:
            cn = str(getattr(card, "cardnumber", None) or card or "")
            for c in list(gr):
                if str(getattr(c, "cardnumber", None) or c or "") == cn:
                    found = c
                    break
        if found is None:
            return False
        gr.remove(found)
        sz = getattr(gs, "set_zone", None)
        if sz is None:
            setattr(gs, "set_zone", [])
            sz = getattr(gs, "set_zone")
        sz.append(found)
        return True
    except Exception:
        return False


def _reserve_next_live_set_limit_delta(gs: Any, delta: int, src: str = "") -> int:
    try:
        cur = int(getattr(gs, "next_live_set_limit_delta", 0) or 0)
    except Exception:
        cur = 0
    new_val = cur + int(delta or 0)
    try:
        setattr(gs, "next_live_set_limit_delta", new_val)
    except Exception:
        pass
    try:
        gs.log.append(f"[AUTO_EXT] reserved next live-set limit delta {new_val:+d} ({src})")
    except Exception:
        pass
    return new_val


def _opp_stage_has_wait_member(gs: Any) -> bool:
    """Return True if opponent stage has any member in wait (active==False) state."""
    try:
        opp = getattr(gs, "opponent", None) or getattr(gs, "opp", None)
        if opp is None:
            return False
        st = getattr(opp, "stage", None)
        if not isinstance(st, dict):
            return False
        for pos in ("L", "C", "R"):
            slot = st.get(pos)
            if slot is None or not bool(getattr(slot, "cardnumber", None)):
                continue
            if not bool(getattr(slot, "active", True)):
                return True
    except Exception:
        pass
    return False


def _stage_other_member_exists(gs: Any, src_pos: str) -> bool:
    """Return True if any stage position OTHER than src_pos has a member."""
    try:
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return False
        for pos in ("L", "C", "R"):
            if pos == src_pos:
                continue
            slot = st.get(pos)
            if slot is not None and bool(getattr(slot, "cardnumber", None)):
                return True
    except Exception:
        pass
    return False


def _stage_has_any_other_member(gs: Any, exclude_pos: str = "") -> bool:
    """Return True if any member is on stage (optionally excluding exclude_pos)."""
    try:
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return False
        for pos in ("L", "C", "R"):
            if pos == exclude_pos:
                continue
            slot = st.get(pos)
            if slot is not None and bool(getattr(slot, "cardnumber", None)):
                return True
    except Exception:
        pass
    return False


def _slot_total_blade(slot: Any) -> int:
    """Return total blade count of a slot (base + temp)."""
    try:
        base = int(getattr(slot, "blade", 0) or 0)
        temp = int(getattr(slot, "temp_blade", 0) or 0)
        return base + temp
    except Exception:
        return 0


def _stage_unit_count_diff_names(gs: Any, cards_db: Dict[str, Any], unit_name: str) -> int:
    """Count stage members with unit_name having DISTINCT cardnames."""
    names_seen = set()
    try:
        st = getattr(gs, "stage", None)
        if not isinstance(st, dict):
            return 0
        for pos in ("L", "C", "R"):
            slot = st.get(pos)
            if slot is None or not bool(getattr(slot, "cardnumber", None)):
                continue
            if not _label_matches_group_or_unit(slot, cards_db, unit_name):
                continue
            name = _card_name(slot, cards_db) or str(getattr(slot, "cardnumber", pos))
            names_seen.add(name)
    except Exception:
        pass
    return len(names_seen)


# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------

def try_apply_effect_by_rule_ext(
    eng: Dict[str, Any],
    gs: Any,
    rng: Any,
    cards_db: Dict[str, Any],
    rule: Dict[str, Any],
    gd: Dict[str, str],
    ctx: Dict[str, Any],
) -> bool:
    """Apply extension-owned effect rules.

    Return True only if this module handled the rule completely.
    Return False to fall back to engine.py legacy implementation.
    """
    if str(rule.get("op") or "") != "__ext__":
        return False

    ext_key = str(rule.get("ext_key") or "").strip()

    # confirm_effect helper path from engine.py (no-cost, single-player fallback)
    confirm_op = str((ctx or {}).get("_ext_confirm_op") or "").strip()
    if confirm_op == "draw1":
        drawn = _draw_cards(eng, gs, 1)
        try:
            gs.log.append(f"[AUTO_EXT] confirm -> draw {drawn}")
        except Exception:
            pass
        return True
    if confirm_op == "energy_wait_plus1":
        added = 0
        try:
            put_wait = eng.get("_put_wait_energy_from_deck")
            if callable(put_wait):
                added = int(put_wait(gs, 1, reason="confirm_effect") or 0)
            else:
                rem_fn = eng.get("_energy_remaining_in_deck")
                clamp_fn = eng.get("_clamp_energy_zone")
                rem = int(rem_fn(gs) if callable(rem_fn) else 0)
                if rem > 0:
                    gs.energy_wait = int(getattr(gs, "energy_wait", 0) or 0) + 1
                    if callable(clamp_fn):
                        clamp_fn(gs)
                    added = 1
        except Exception:
            pass
        try:
            gs.log.append(f"[AUTO_EXT] confirm -> energy_wait +{added}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # 既存: position_change_optional
    # ------------------------------------------------------------------
    if ext_key == "position_change_optional":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        if src_pos not in ("L", "C", "R"):
            try:
                gs.log.append(f"[WARN] position_change_optional: invalid src_pos='{src_pos}'")
            except Exception:
                pass
            return True
        options = [p for p in ("L", "C", "R") if p != src_pos] + ["skip"]
        payload = {
            "kind": "position_change",
            "src_pos": src_pos,
            "optional": True,
            "options": options,
            "source_cn": str((ctx or {}).get("source_cn") or ""),
        }
        try:
            getattr(gs, 'pending').append(payload)
            gs.log.append(f"[PENDING] position_change src={src_pos}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 17: PL!-bp3-006 西木野真姫
    # ライブ終了時まで、成功ライブ置き場の枚数 × +2ブレード
    # ------------------------------------------------------------------
    if ext_key == "live_start_success_zone_count_x2_blade":
        slot = _src_slot(gs, ctx)
        success_cards = _success_zone_cards(gs)
        n = len(success_cards) * 2
        if slot is not None and n > 0:
            _add_temp_blade(eng, slot, n)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_zone={len(success_cards)} -> +{n}blade (西木野真姫)"
                )
            except Exception:
                pass
        elif slot is not None:
            try:
                gs.log.append("[AUTO_EXT] success_zone=0, no blade added (西木野真姫)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 24: PL!-bp4-001 高坂穂乃果
    # 自ステージのコスト合計が相手より低い場合、カードを1枚引く。
    # ------------------------------------------------------------------
    if ext_key == "live_start_my_cost_lower_draw1":
        my_cost = _stage_member_cost_sum(gs, cards_db)
        opp_exists = _has_opponent_state(gs)
        opp_cost = _opp_stage_member_cost_sum(gs, cards_db) if opp_exists else 0
        src = str((ctx or {}).get("source_cn") or "")
        if opp_exists:
            if my_cost < opp_cost:
                drawn = _draw_cards(eng, gs, 1)
                try:
                    gs.log.append(f"[AUTO_EXT] stage_cost {my_cost}<{opp_cost} -> draw {drawn} (高坂穂乃果)")
                except Exception:
                    pass
            else:
                try:
                    gs.log.append(f"[AUTO_EXT] stage_cost {my_cost}>={opp_cost}, no draw (高坂穂乃果)")
                except Exception:
                    pass
            return True
        payload = {
            "kind": "confirm_effect",
            "text": "【高坂穂乃果】ライブ開始時：自分ステージのコスト合計が相手より低いなら、カードを1枚引く",
            "options": ["使う", "スキップ"],
            "after_effect_template": "自分ステージにいるメンバーのコストの合計が相手より低い場合、カードを1枚引く。",
            "ctx": {"source_cn": src, "_ext_confirm_op": "draw1"},
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 高坂穂乃果: confirm draw1 (my_cost={my_cost}, opp unavailable)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 26: PL!-bp4-004 園田海未
    # 成功ライブのスコア合計 ≥ 6 → energy 2枚アクティブ
    # ------------------------------------------------------------------
    if ext_key == "enter_success_score_ge6_activate2":
        success_cards = _success_zone_cards(gs)
        total_score = sum(_card_score(c, cards_db) for c in success_cards)
        if total_score >= 6:
            moved = _activate_energy(gs, 2)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}>=6 -> activate {moved} energy (園田海未)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}<6, no energy (園田海未)"
                )
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 31: PL!-bp4-016 東條希
    # 成功ライブのスコア合計 ≥ 3 → draw 1
    # ------------------------------------------------------------------
    if ext_key == "enter_success_score_ge3_draw1":
        success_cards = _success_zone_cards(gs)
        total_score = sum(_card_score(c, cards_db) for c in success_cards)
        if total_score >= 3:
            drawn = _draw_cards(eng, gs, 1)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}>=3 -> draw {drawn} (東條希)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_score={total_score}<3, no draw (東條希)"
                )
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 41: PL!-pb1-003 南ことり
    # ステージの Printemps メンバー数 × energy アクティブ
    # ------------------------------------------------------------------
    if ext_key == "enter_printemps_count_activate_energy":
        count = _stage_unit_count(gs, cards_db, "Printemps")
        if count > 0:
            moved = _activate_energy(gs, count)
            try:
                gs.log.append(
                    f"[AUTO_EXT] Printemps_on_stage={count} -> activate {moved} energy (南ことり)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append("[AUTO_EXT] no Printemps on stage, no energy (南ことり)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 57: PL!-pb1-032 SENTIMENTAL StepS
    # 成功ライブ置き場に μ's カードがある → draw 1
    # ------------------------------------------------------------------
    if ext_key == "live_success_success_zone_has_mus_draw1":
        success_cards = _success_zone_cards(gs)
        has_mus = any(_card_group(c, cards_db) == "μ's" for c in success_cards)
        if has_mus:
            drawn = _draw_cards(eng, gs, 1)
            try:
                gs.log.append(
                    f"[AUTO_EXT] success_zone has μ's -> draw {drawn} (SENTIMENTAL StepS)"
                )
            except Exception:
                pass
        else:
            try:
                gs.log.append("[AUTO_EXT] no μ's in success_zone, no draw (SENTIMENTAL StepS)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 63: PL!-sd1-008 小泉花陽
    # デッキ上から 10 枚控え室へ (mill 10)
    # ------------------------------------------------------------------
    if ext_key == "body_mill10":
        milled = 0
        try:
            deck = getattr(gs, "deck", None)
            waiting = getattr(gs, "green_room", None)
            if waiting is None:
                waiting = (
                    getattr(gs, "waiting_room", None)
                    or getattr(gs, "graveyard", None)
                    or getattr(gs, "discard", None)
                )
            if deck is not None and waiting is not None:
                for _ in range(10):
                    if not deck:
                        break
                    waiting.append(deck.pop(0))
                    milled += 1
            gs.log.append(f"[AUTO_EXT] mill {milled} cards to waiting_room (小泉花陽)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 67: PL!HS-bp1-004 夕霧綴理
    # ライブ終了時まで、ライブ中のカード 1 枚につき +1ブレード
    # ------------------------------------------------------------------
    if ext_key == "live_start_live_cards_count_x1_blade":
        slot = _src_slot(gs, ctx)
        live_cards = _live_in_progress_cards(gs)
        n = len(live_cards)
        if slot is not None and n > 0:
            _add_temp_blade(eng, slot, n)
            try:
                gs.log.append(
                    f"[AUTO_EXT] live_cards={n} -> +{n}blade (夕霧綴理)"
                )
            except Exception:
                pass
        elif slot is not None:
            try:
                gs.log.append("[AUTO_EXT] live_cards=0, no blade (夕霧綴理)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 72: PL!HS-bp1-023 ド！ド！ド！
    # ライブ合計スコア > 相手 かつ ステージに蓮ノ空メンバー → energy deck から 1枚 wait
    # ------------------------------------------------------------------
    if ext_key == "live_success_score_gt_opp_and_hasunosora_energy_wait":
        my_score = _live_score_total(gs)
        opp_score = _opp_live_score_total(gs)
        try:
            if (ctx or {}).get("live_score") is not None:
                my_score = int(ctx["live_score"])
            if (ctx or {}).get("opp_live_score") is not None:
                opp_score = int(ctx["opp_live_score"])
        except Exception:
            pass

        has_hasunosora = _stage_has_group(gs, cards_db, "蓮ノ空")
        if not has_hasunosora:
            try:
                gs.log.append("[AUTO_EXT] no 蓮ノ空 on stage, no energy (ド！ド！ド！)")
            except Exception:
                pass
            return True

        opp_exists = _has_opponent_state(gs)
        if opp_exists:
            if my_score > opp_score:
                added = 0
                try:
                    put_wait = eng.get("_put_wait_energy_from_deck")
                    if callable(put_wait):
                        added = int(put_wait(gs, 1, reason="ド！ド！ド！") or 0)
                    else:
                        rem_fn = eng.get("_energy_remaining_in_deck")
                        clamp_fn = eng.get("_clamp_energy_zone")
                        rem = int(rem_fn(gs) if callable(rem_fn) else 0)
                        if rem > 0:
                            gs.energy_wait = int(getattr(gs, "energy_wait", 0) or 0) + 1
                            if callable(clamp_fn):
                                clamp_fn(gs)
                            added = 1
                except Exception:
                    pass
                try:
                    gs.log.append(f"[AUTO_EXT] live_score {my_score}>{opp_score} & 蓮ノ空 on stage -> energy_wait +{added} (ド！ド！ド！)")
                except Exception:
                    pass
            else:
                try:
                    gs.log.append(f"[AUTO_EXT] live_score {my_score}<={opp_score}, no energy (ド！ド！ド！)")
                except Exception:
                    pass
            return True

        src = str((ctx or {}).get("source_cn") or "")
        payload = {
            "kind": "confirm_effect",
            "text": "【ド！ド！ド！】ライブ成功時：自分の合計スコアが相手より高いなら、エネルギーを1枚ウェイトで置く",
            "options": ["使う", "スキップ"],
            "after_effect_template": "ライブの合計スコアが相手より高く、かつ自分のステージに『蓮ノ空』のメンバーがいる場合、自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。",
            "ctx": {"source_cn": src, "_ext_confirm_op": "energy_wait_plus1"},
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] ド！ド！ド！: confirm energy_wait+1 (my_score={my_score}, opp unavailable)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 77: PL!HS-bp2-005 大沢瑠璃乃
    # ステージ全 3 エリアにメンバーがいる → ライブ終了時まで +2ブレード
    # ------------------------------------------------------------------
    if ext_key == "live_start_all_stage_filled_x2_blade":
        slot = _src_slot(gs, ctx)
        if _all_stage_slots_filled(gs):
            if slot is not None:
                _add_temp_blade(eng, slot, 2)
            try:
                gs.log.append("[AUTO_EXT] all stage filled -> +2blade (大沢瑠璃乃)")
            except Exception:
                pass
        else:
            try:
                gs.log.append("[AUTO_EXT] stage not full, no blade (大沢瑠璃乃)")
            except Exception:
                pass
        return True



    # ==================================================================
    # bp2_batch2_20260410b Claude merge (GPT debugged)
    # ==================================================================

    # PL!HS-bp2-002 村野さやか (登場)
    if ext_key == "enter_pick_cost_le2_member_from_green_up_to_2":
        src = str((ctx or {}).get("source_cn") or "")
        candidates = [
            c for c in _green_room_list(gs)
            if _card_type_norm(c, cards_db) == 'MEMBER' and _card_cost(c, cards_db) <= 2
        ]
        try:
            gs.log.append(f"[AUTO_EXT] 村野さやか: candidates={len(candidates)} (multi-pick) ({src})")
        except Exception:
            pass
        if not candidates:
            return True
        cns = [str(getattr(c, 'cardnumber', None) or c or '') for c in candidates]
        payload = {
            'kind': 'choose_member_from_green_multi_up_to',
            'text': '【村野さやか】控え室からコスト2以下のメンバーカードを0〜2枚選んで手札に加える',
            'options': cns,
            'min_picks': 0,
            'max_picks': min(2, len(cns)),
            'want_kind': 'MEMBER',
            'source_cn': src,
        }
        try:
            getattr(gs, 'pending').append(payload)
            gs.log.append(f"[PENDING] 村野さやか: multi-pick cost<=2 MEMBER opts={cns}")
        except Exception:
            pass
        return True

    # PL!HS-bp2-002 村野さやか (BODY)
    if ext_key == "body_higher_cost_member_exists_blade3":
        slot = _src_slot(gs, ctx)
        src = str((ctx or {}).get('source_cn') or '')
        if slot is None:
            return True
        my_cost = _card_cost(slot, cards_db)
        src_pos = str((ctx or {}).get('src_pos') or (ctx or {}).get('pos') or '').upper()
        found_higher = False
        try:
            st = getattr(gs, 'stage', None)
            if isinstance(st, dict):
                for pos in ('L','C','R'):
                    if pos == src_pos:
                        continue
                    other = st.get(pos)
                    if other is None or not bool(getattr(other, 'cardnumber', None)):
                        continue
                    if _card_type_norm(other, cards_db) == 'MEMBER' and _card_cost(other, cards_db) > my_cost:
                        found_higher = True
                        break
        except Exception:
            pass
        try:
            gs.log.append(f"[AUTO_EXT] 村野さやか BODY: my_cost={my_cost} found_higher={found_higher} ({src})")
        except Exception:
            pass
        if found_higher:
            _add_temp_blade(eng, slot, 3)
        return True

    # PL!HS-bp2-003 / PL!HS-bp2-016
    if ext_key in ('reorder_from_top3', 'reorder_from_top2'):
        k = 3 if ext_key == 'reorder_from_top3' else 2
        fn = eng.get('_enqueue_reorder_from_topk_keep_any')
        label = '乙宗梢 bp2-003' if k == 3 else '百生吟子 bp2-016'
        if callable(fn):
            try:
                fn(gs, k, rng)
                gs.log.append(f"[AUTO_EXT] {label}: enqueue reorder_from_top{k}")
            except Exception as e:
                try:
                    gs.log.append(f"[ERR] {label}: _enqueue_reorder_from_topk_keep_any failed: {e}")
                except Exception:
                    pass
        else:
            try:
                gs.log.append(f"[ERR] {label}: _enqueue_reorder_from_topk_keep_any not found")
            except Exception:
                pass
        return True

    # PL!HS-bp2-006 藤島慈 (BODY)
    if ext_key == 'body_mirakupark_others_count_blade':
        slot = _src_slot(gs, ctx)
        src_pos = str((ctx or {}).get('src_pos') or (ctx or {}).get('pos') or '').upper()
        if slot is None:
            return True
        count = 0
        try:
            st = getattr(gs, 'stage', None)
            if isinstance(st, dict):
                for pos in ('L','C','R'):
                    if pos == src_pos:
                        continue
                    other = st.get(pos)
                    if other is None or not bool(getattr(other, 'cardnumber', None)):
                        continue
                    if _card_type_norm(other, cards_db) == 'MEMBER' and _label_matches_group_or_unit(other, cards_db, 'みらくらぱーく！'):
                        count += 1
        except Exception:
            pass
        if count > 0:
            _add_temp_blade(eng, slot, count)
        try:
            gs.log.append(f"[AUTO_EXT] 藤島慈 BODY: みらくらぱーく！ others={count}")
        except Exception:
            pass
        return True

    # PL!HS-bp2-010 / 012 / 013 top5 filtered optional
    if ext_key in ('enter_top5_member_optional_pick', 'body_stage_to_green_top5_member_optional', 'body_stage_to_green_top5_live_optional'):
        filter_kind = 'LIVE' if ext_key == 'body_stage_to_green_top5_live_optional' else 'MEMBER'
        label = (
            '日野下花帆 bp2-010' if ext_key == 'enter_top5_member_optional_pick' else
            '乙宗梢 bp2-012' if ext_key == 'body_stage_to_green_top5_member_optional' else
            '夕霧綴理 bp2-013'
        )
        fn = eng.get('_enqueue_choose_from_topk_filtered')
        if callable(fn):
            try:
                fn(gs, 5, rng, cards_db, filter_kind=filter_kind, optional=True)
                gs.log.append(f"[AUTO_EXT] {label}: enqueue choose_from_top5 filter_kind={filter_kind} optional=True")
            except Exception as e:
                try:
                    gs.log.append(f"[ERR] {label}: _enqueue_choose_from_topk_filtered failed: {e}")
                except Exception:
                    pass
        else:
            try:
                gs.log.append(f"[ERR] {label}: _enqueue_choose_from_topk_filtered not found")
            except Exception:
                pass
        return True

    # PL!HS-bp2-017 徒町小鈴 (登場)
    if ext_key == 'enter_green_ge10_draw1':
        green_count = len(_green_room_list(gs))
        if green_count >= 10:
            drawn = _draw_cards(eng, gs, 1)
            try:
                gs.log.append(f"[AUTO_EXT] 徒町小鈴: green>=10 -> draw {drawn}")
            except Exception:
                pass
        else:
            try:
                gs.log.append(f"[AUTO_EXT] 徒町小鈴: green_room={green_count}<10, no draw")
            except Exception:
                pass
        return True

    # PL!HS-bp2-014 大沢瑠璃乃 (登場)
    if ext_key == 'enter_draw1_and_cannot_live_until_end_of_live':
        drawn = _draw_cards(eng, gs, 1)
        try:
            gs.cannot_live_until_end_of_live = True
        except Exception:
            setattr(gs, 'cannot_live_until_end_of_live', True)
        try:
            gs.log.append(f"[AUTO_EXT] 大沢瑠璃乃 bp2-014: draw {drawn}; cannot live until end of live")
        except Exception:
            pass
        return True
    # ==================================================================
    # group2_single_target_20260402 新規実装
    # ==================================================================

    # ------------------------------------------------------------------
    # Prompt 22: PL!-bp3-026 Oh,Love&Peace! (ライブ開始時)
    # ライブ終了時まで、ステージのメンバー1人（選択）に +3ブレード
    # cost=手札を2枚控え室に置いてもよい → engine 側 pay_or_skip pending が先行
    # effect handler では choose_stage_member_to_activate pending を流用して
    # 対象メンバーを1人選ばせ、解決時に temp_blade +3
    # ------------------------------------------------------------------
    if ext_key == "live_start_pick_stage_member_blade3":
        occupied = _stage_positions_all_occupied(gs)
        src = str((ctx or {}).get("source_cn") or "")
        if not occupied:
            try:
                gs.log.append("[AUTO_EXT] no stage members, no blade (Oh,Love&Peace!)")
            except Exception:
                pass
            return True
        if len(occupied) == 1:
            # 対象が1人のみなら選択不要で即付与
            _, slot = occupied[0]
            _add_temp_blade(eng, slot, 3)
            try:
                gs.log.append(f"[AUTO_EXT] only 1 member -> +3blade to {occupied[0][0]} (Oh,Love&Peace!)")
            except Exception:
                pass
            return True
        # 複数いる場合は choose_stage_member_to_activate pending で選択
        candidates = [pos for pos, _ in occupied]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_pick_stage_member_blade3__resolve",
            "source_cn": src,
            "label": "【Oh,Love&Peace!】ブレード+3を与えるメンバーを選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] Oh,Love&Peace!: choose member for +3blade from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_pick_stage_member_blade3__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_blade(eng, slot, 3)
            try:
                gs.log.append(f"[AUTO_EXT] +3blade -> {chosen_pos} (Oh,Love&Peace! resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 30: PL!-bp4-013 園田海未 (ライブ開始時)
    # このメンバー以外のステージメンバー1人（選択）に pink+1
    # src_pos から「このメンバー」を特定して除外候補を絞る
    # ------------------------------------------------------------------
    if ext_key == "live_start_pick_other_stage_member_pink1":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        occupied = _stage_positions_all_occupied(gs)
        others = [(pos, slot) for pos, slot in occupied if pos != src_pos]
        if not others:
            try:
                gs.log.append(f"[AUTO_EXT] no other members on stage (園田海未 bp4-013)")
            except Exception:
                pass
            return True
        if len(others) == 1:
            _, slot = others[0]
            _add_temp_hearts(eng, slot, {"pink": 1})
            try:
                gs.log.append(f"[AUTO_EXT] +pink to {others[0][0]} (園田海未 bp4-013)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in others]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_pick_other_stage_member_pink1__resolve",
            "source_cn": src,
            "label": "【園田海未】桃ハート+1を与えるメンバーを選んでください（このメンバー以外）",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 園田海未 bp4-013: choose other member for +pink from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_pick_other_stage_member_pink1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_hearts(eng, slot, {"pink": 1})
            try:
                gs.log.append(f"[AUTO_EXT] +pink -> {chosen_pos} (園田海未 bp4-013 resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 32: PL!-bp4-017 小泉花陽 (ライブ開始時)
    # センター(C)の μ's メンバーに +1ブレード（対象固定、選択不要）
    # ------------------------------------------------------------------
    if ext_key == "live_start_center_mus_blade1":
        st = getattr(gs, "stage", None)
        center_slot = (st or {}).get("C") if isinstance(st, dict) else None
        if center_slot is not None and bool(getattr(center_slot, "cardnumber", None)):
            if _card_group(center_slot, cards_db) == "μ's":
                _add_temp_blade(eng, center_slot, 1)
                try:
                    gs.log.append("[AUTO_EXT] center μ's -> +1blade (小泉花陽 bp4-017)")
                except Exception:
                    pass
            else:
                try:
                    gs.log.append("[AUTO_EXT] center member is not μ's, no blade (小泉花陽 bp4-017)")
                except Exception:
                    pass
        else:
            try:
                gs.log.append("[AUTO_EXT] center empty, no blade (小泉花陽 bp4-017)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 35: PL!-bp4-020 Love wing bell (ライブ開始時)
    # ステージが μ's のみ → ステージメンバー1人をポジションチェンジさせてもよい
    # ------------------------------------------------------------------
    if ext_key == "live_start_mus_only_pick_member_position_change":
        if not _stage_all_group(gs, cards_db, "μ's"):
            try:
                gs.log.append("[AUTO_EXT] stage not all μ's, skip (Love wing bell)")
            except Exception:
                pass
            return True
        occupied = _stage_positions_all_occupied(gs)
        src = str((ctx or {}).get("source_cn") or "")
        if not occupied:
            try:
                gs.log.append("[AUTO_EXT] no stage members, skip (Love wing bell)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in occupied]
        # 選択用 pending: choose_stage_member_to_activate でポジションを選ばせ、
        # 解決時に position_change pending を積む
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates + ["skip"],
            "optional": True,
            "after_ext_key": "live_start_mus_only_pick_member_position_change__resolve",
            "source_cn": src,
            "label": "【Love wing bell】ポジションチェンジするメンバーを選んでください（スキップ可）",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] Love wing bell: choose member for position_change from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_mus_only_pick_member_position_change__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        if chosen_pos == "SKIP" or chosen_pos not in ("L", "C", "R"):
            try:
                gs.log.append("[AUTO_EXT] position_change skipped (Love wing bell)")
            except Exception:
                pass
            return True
        options = [p for p in ("L", "C", "R") if p != chosen_pos] + ["skip"]
        src = str((ctx or {}).get("source_cn") or "")
        payload = {
            "kind": "position_change",
            "src_pos": chosen_pos,
            "optional": True,
            "options": options,
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] position_change src={chosen_pos} (Love wing bell)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 37: PL!-bp4-024 小夜啼鳥恋詩 (ライブ開始時)
    # ステージの μ's メンバー1人（選択）に +1ブレード
    # ------------------------------------------------------------------
    if ext_key == "live_start_pick_mus_stage_member_blade1":
        mus_members = _stage_positions_with_group(gs, cards_db, "μ's")
        src = str((ctx or {}).get("source_cn") or "")
        if not mus_members:
            try:
                gs.log.append("[AUTO_EXT] no μ's on stage (小夜啼鳥恋詩)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in mus_members]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_pick_mus_stage_member_blade1__resolve",
            "source_cn": src,
            "label": "【小夜啼鳥恋詩】ブレード+1を与えるμ'sメンバーを選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 小夜啼鳥恋詩: choose μ's member for +blade from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_pick_mus_stage_member_blade1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_blade(eng, slot, 1)
            try:
                gs.log.append(f"[AUTO_EXT] +1blade -> {chosen_pos} (小夜啼鳥恋詩 resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 46: PL!-pb1-010 高坂穂乃果 (ライブ開始時)
    # このメンバー以外のステージメンバー全員に +1ブレード（選択なし）
    # ------------------------------------------------------------------
    if ext_key == "live_start_other_stage_members_blade1":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        occupied = _stage_positions_all_occupied(gs)
        others = [(pos, slot) for pos, slot in occupied if pos != src_pos]
        if not others:
            try:
                gs.log.append(f"[AUTO_EXT] no other members on stage (高坂穂乃果 pb1-010)")
            except Exception:
                pass
            return True
        for pos, slot in others:
            _add_temp_blade(eng, slot, 1)
        try:
            gs.log.append(f"[AUTO_EXT] +1blade to {[p for p,_ in others]} (高坂穂乃果 pb1-010)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 48: PL!-pb1-012 南ことり (登場)
    # Printemps のウェイト状態メンバーを1人までアクティブにする
    # ウェイト = active==False のスロット
    # ------------------------------------------------------------------
    if ext_key == "enter_printemps_activate_up_to_1":
        src = str((ctx or {}).get("source_cn") or "")
        wait_printemps = []
        try:
            st = getattr(gs, "stage", None)
            if isinstance(st, dict):
                for pos in ("L", "C", "R"):
                    slot = st.get(pos)
                    if slot is None or not bool(getattr(slot, "cardnumber", None)):
                        continue
                    if _card_unit(slot, cards_db) != "Printemps":
                        continue
                    if not bool(getattr(slot, "active", True)):
                        wait_printemps.append((pos, slot))
        except Exception:
            pass

        if not wait_printemps:
            try:
                gs.log.append("[AUTO_EXT] no Printemps wait member to activate (南ことり pb1-012)")
            except Exception:
                pass
            return True
        candidates = [pos for pos, _ in wait_printemps] + ["skip"]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": True,
            "after_ext_key": "enter_printemps_activate_up_to_1__resolve",
            "source_cn": src,
            "label": "【南ことり】アクティブにするPrintempsメンバーを選んでください（スキップ可）",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 南ことり pb1-012: choose Printemps wait member from {[p for p,_ in wait_printemps]}")
        except Exception:
            pass
        return True

    if ext_key == "enter_printemps_activate_up_to_1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        if chosen_pos == "SKIP" or chosen_pos not in ("L", "C", "R"):
            try:
                gs.log.append("[AUTO_EXT] Printemps activate skipped (南ことり pb1-012)")
            except Exception:
                pass
            return True
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            try:
                slot.active = True
                gs.log.append(f"[AUTO_EXT] activate {chosen_pos} (南ことり pb1-012 resolve)")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # bp2_batch3_local_20260413f
    {
        "id": "enter_sayaka_bp2011_mill5",
        "effect_template": "デッキの上からカードを5枚控え室に置く。",
        "ext_key": "enter_mill5",
    },
    {
        "id": "body_megumi_bp2015_leave_stage_draw2_discard1",
        "effect_template": "このメンバーがステージから控え室に置かれたとき、カードを2枚引き、手札を1枚控え室に置く。",
        "ext_key": "body_leave_stage_draw2_discard1",
    },

    # Prompt 80: PL!HS-bp2-007 百生吟子 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # 控え室に置いたカードがメンバーカードなら、同名ステージメンバーに green+1 blade+1
    # ctx["discarded_cn"] に捨てたカードの cardnumber が渡される想定。
    # 渡されない場合は green_room の最新カードを参照する。
    # ------------------------------------------------------------------
    if ext_key == "live_start_discard_member_same_name_green1_blade1":
        src = str((ctx or {}).get("source_cn") or "")
        # 捨てたカードを特定
        discarded_cn = str((ctx or {}).get("discarded_cn") or "").strip()
        if not discarded_cn:
            top = _green_room_top(gs)
            if top is not None:
                discarded_cn = str(getattr(top, "cardnumber", None) or top or "").strip()

        if not discarded_cn:
            try:
                gs.log.append("[AUTO_EXT] could not identify discarded card (百生吟子)")
            except Exception:
                pass
            return True

        # カードタイプ確認（MEMBER でなければ効果なし）
        discarded_type = _card_type_norm(discarded_cn, cards_db)
        if discarded_type != "MEMBER":
            try:
                gs.log.append(f"[AUTO_EXT] discarded {discarded_cn} is not MEMBER (type={discarded_type}), no effect (百生吟子)")
            except Exception:
                pass
            return True

        # 同名のステージメンバーを探す
        discarded_name = _card_name(discarded_cn, cards_db)
        if not discarded_name:
            try:
                canon_fn = eng.get("_canon_cardno")
                get_card_fn = eng.get("_get_card")
                canon_cn = canon_fn(discarded_cn) if callable(canon_fn) else str(discarded_cn or "")
                ci_dis = get_card_fn(cards_db, canon_cn) if callable(get_card_fn) else None
                if ci_dis is not None:
                    discarded_name = str(
                        getattr(ci_dis, "cardname", "") or
                        getattr(ci_dis, "name", "") or
                        ((ci_dis if isinstance(ci_dis, dict) else {}).get("cardname")) or
                        ((ci_dis if isinstance(ci_dis, dict) else {}).get("name")) or
                        ""
                    )
            except Exception:
                pass

        def _same_name_or_card(slot_obj: Any, discarded_cn_val: str, discarded_name_val: str) -> bool:
            slot_cn = str(getattr(slot_obj, "cardnumber", "") or "")
            # まず cardnumber 一致を強く見る
            try:
                canon_fn = eng.get("_canon_cardno")
                if callable(canon_fn):
                    if canon_fn(slot_cn) == canon_fn(discarded_cn_val):
                        return True
                elif slot_cn == discarded_cn_val:
                    return True
            except Exception:
                if slot_cn == discarded_cn_val:
                    return True

            # 次に cardname 一致
            slot_name = _card_name(slot_obj, cards_db)
            if discarded_name_val and slot_name and slot_name == discarded_name_val:
                return True

            # 最後に engine の _get_card でもう一度引き直す
            try:
                canon_fn = eng.get("_canon_cardno")
                get_card_fn = eng.get("_get_card")
                canon_slot = canon_fn(slot_cn) if callable(canon_fn) else slot_cn
                ci_slot = get_card_fn(cards_db, canon_slot) if callable(get_card_fn) else None
                slot_name2 = str(
                    getattr(ci_slot, "cardname", "") or
                    getattr(ci_slot, "name", "") or
                    ((ci_slot if isinstance(ci_slot, dict) else {}).get("cardname")) or
                    ((ci_slot if isinstance(ci_slot, dict) else {}).get("name")) or
                    ""
                )
                if discarded_name_val and slot_name2 and slot_name2 == discarded_name_val:
                    return True
            except Exception:
                pass
            return False

        if not discarded_name:
            # 名前が取れなくても cardnumber 一致だけで通せるようにする
            try:
                gs.log.append(f"[AUTO_EXT] name fallback by cardnumber for {discarded_cn} (百生吟子)")
            except Exception:
                pass

        matched = []
        try:
            st = getattr(gs, "stage", None)
            if isinstance(st, dict):
                for pos in ("L", "C", "R"):
                    slot = st.get(pos)
                    if slot is None or not bool(getattr(slot, "cardnumber", None)):
                        continue
                    if _same_name_or_card(slot, discarded_cn, discarded_name):
                        matched.append((pos, slot))
        except Exception:
            pass

        if not matched:
            try:
                gs.log.append(f"[AUTO_EXT] no stage member named '{discarded_name}', no effect (百生吟子)")
            except Exception:
                pass
            return True

        if len(matched) == 1:
            _, slot = matched[0]
            _add_temp_hearts(eng, slot, {"green": 1})
            _add_temp_blade(eng, slot, 1)
            try:
                gs.log.append(f"[AUTO_EXT] discarded MEMBER '{discarded_name}' -> +green+blade to {matched[0][0]} (百生吟子)")
            except Exception:
                pass
            return True

        # 同名が複数いる場合は選択（通常は起きないが安全のため）
        candidates = [pos for pos, _ in matched]
        payload = {
            "kind": "choose_stage_member_to_activate",
            "candidates": candidates,
            "optional": False,
            "after_ext_key": "live_start_discard_member_same_name_green1_blade1__resolve",
            "source_cn": src,
            "discarded_name": discarded_name,
            "label": f"【百生吟子】{discarded_name}と同名のメンバーを選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 百生吟子: choose same-name member from {candidates}")
        except Exception:
            pass
        return True

    if ext_key == "live_start_discard_member_same_name_green1_blade1__resolve":
        chosen_pos = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_pos") or "").upper()
        st = getattr(gs, "stage", None)
        slot = (st or {}).get(chosen_pos) if isinstance(st, dict) else None
        if slot is not None:
            _add_temp_hearts(eng, slot, {"green": 1})
            _add_temp_blade(eng, slot, 1)
            try:
                gs.log.append(f"[AUTO_EXT] +green+blade -> {chosen_pos} (百生吟子 resolve)")
            except Exception:
                pass
        return True

    # ==================================================================
    # group3_A7B2_20260406a 新規実装
    # ==================================================================

    # ------------------------------------------------------------------
    # Prompt 69: PL!HS-bp1-006 藤島慈 (ライブ開始時)
    # cost=手札1枚控え室へ → engine 側 pay_or_skip
    # 他メンバーがいる場合: ハートの色を1つ選んで ライブ終了時まで得る
    # ------------------------------------------------------------------
    if ext_key == "live_start_other_member_exists_choose_heart":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        if not _stage_has_any_other_member(gs, exclude_pos=src_pos):
            try:
                gs.log.append("[AUTO_EXT] no other member on stage, no effect (藤島慈)")
            except Exception:
                pass
            return True
        payload = {
            "kind": "choose_heart_color",
            "pos": src_pos,
            "n": 1,
            "text": f"{src}: 好きなハートの色を1つ指定する → ライブ終了時まで+1",
            "options": ["桃", "赤", "黄", "緑", "青", "紫"],
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append("[PENDING] 藤島慈: choose heart color (self)")
        except Exception:
            pass
        return True


    # ------------------------------------------------------------------
    # Prompt 14: PL!-bp3-003 南ことり (登場)
    # cost=このメンバーをウェイトにしてもよい → engine 側 self_wait pay_or_skip
    # 控え室から μ's のメンバーカードを1枚手札に加える
    # ------------------------------------------------------------------
    if ext_key == "enter_pick_mus_member_from_green":
        src = str((ctx or {}).get("source_cn") or "")
        candidates = _green_room_members_by_group(gs, cards_db, "μ's")
        if not candidates:
            try:
                gs.log.append("[AUTO_EXT] no μ's MEMBER in green_room (南ことり bp3-003)")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            ok = _move_card_from_green_to_hand(gs, candidates[0])
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {cn_str} (南ことり bp3-003) ok={ok}")
            except Exception:
                pass
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_member_from_green",
            "text": "控え室のメンバーカードを1枚手札に加える",
            "options": cns,
            "want_kind": "MEMBER",
            "want_group": "μ's",
            "remaining_picks": 1,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 南ことり bp3-003: choose μ's MEMBER from green {cns}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 16: PL!-bp3-004 園田海未 (ライブ開始時)
    # 成功置き場にカードがある場合のみ発動可
    # cost=手札1枚控え室へ → engine 側 pay_or_skip
    # 控え室から μ's のライブカードを1枚手札に加える
    # ------------------------------------------------------------------
    if ext_key == "live_start_pick_mus_live_from_green":
        src = str((ctx or {}).get("source_cn") or "")
        if not _success_zone_cards(gs):
            try:
                gs.log.append("[AUTO_EXT] success_zone empty, no effect (園田海未 bp3-004)")
            except Exception:
                pass
            return True
        candidates = _green_room_lives_by_group(gs, cards_db, "μ's")
        if not candidates:
            try:
                gs.log.append("[AUTO_EXT] no μ's LIVE in green_room (園田海未 bp3-004)")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            ok = _move_card_from_green_to_hand(gs, candidates[0])
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {cn_str} LIVE (園田海未 bp3-004) ok={ok}")
            except Exception:
                pass
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_live_from_green",
            "text": "控え室のライブカードを1枚手札に加える",
            "options": cns,
            "want_kind": "LIVE",
            "want_group": "μ's",
            "remaining_picks": 1,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 園田海未 bp3-004: choose μ's LIVE from green {cns}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 60: PL!-sd1-003 南ことり (ライブ開始時)
    # cost=手札1枚控え室へ → engine 側 pay_or_skip
    # 桃/黄/紫 のうち1つ選んでライブ終了時まで得る
    # ------------------------------------------------------------------
    if ext_key == "live_start_choose_pinkYellowPurple_heart":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        payload = {
            "kind": "choose_heart_color",
            "pos": src_pos,
            "n": 1,
            "text": f"{src}: 桃/黄/紫から1つ選ぶ → ライブ終了時まで+1",
            "options": ["桃", "黄", "紫"],
            "source_cn": src,
            "src_pos": src_pos,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append("[PENDING] 南ことり sd1-003: choose pink/yellow/purple heart")
        except Exception:
            pass
        return True


    # ------------------------------------------------------------------
    # Prompt 73: PL!HS-bp2-001 日野下花帆 (起動)
    # コスト <(E)><(E)> → engine 側起動コスト処理
    # 控え室からスコア3以下の 蓮ノ空 ライブカードを1枚手札に加える
    # ------------------------------------------------------------------
    if ext_key == "body_pick_hasunosora_live_score_le3_from_green":
        src = str((ctx or {}).get("source_cn") or "")
        candidates = _green_room_lives_by_group_score_le(gs, cards_db, "蓮ノ空", 3)
        if not candidates:
            try:
                gs.log.append("[AUTO_EXT] no 蓮ノ空 LIVE score<=3 in green_room (日野下花帆)")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            ok = _move_card_from_green_to_hand(gs, candidates[0])
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {cn_str} (日野下花帆) ok={ok}")
            except Exception:
                pass
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_card_from_green",
            "candidates": cns,
            "optional": False,
            "after_ext_key": "body_pick_hasunosora_live_score_le3_from_green__resolve",
            "source_cn": src,
            "label": "【日野下花帆】控え室からスコア3以下の蓮ノ空ライブカードを1枚選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 日野下花帆: choose 蓮ノ空 LIVE score<=3 from green {cns}")
        except Exception:
            pass
        return True

    if ext_key == "body_pick_hasunosora_live_score_le3_from_green__resolve":
        chosen_cn = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_cn") or "").strip()
        gr = _green_room_list(gs)
        found = None
        for c in list(gr):
            if str(getattr(c, "cardnumber", None) or c or "").strip() == chosen_cn:
                found = c
                break
        if found is not None:
            ok = _move_card_from_green_to_hand(gs, found)
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {chosen_cn} (日野下花帆 resolve) ok={ok}")
            except Exception:
                pass
        return True

    if ext_key == "body_pick_live_req_yellow_ge3_from_green":
        src = str((ctx or {}).get("source_cn") or "PL!-PR-003")
        return _enqueue_pick_live_req_heart_from_green(gs, cards_db, 'yellow', 3, src)

    if ext_key == "body_pick_live_req_pink_ge3_from_green":
        src = str((ctx or {}).get("source_cn") or "PL!-PR-004")
        return _enqueue_pick_live_req_heart_from_green(gs, cards_db, 'pink', 3, src)

    # ------------------------------------------------------------------
    # Prompt 76: PL!HS-bp2-005 大沢瑠璃乃 (登場)

    # ------------------------------------------------------------------
    # Prompt 76: PL!HS-bp2-005 大沢瑠璃乃 (登場)
    # cost=手札1枚控え室へ → engine 側 pay_or_skip
    # 他メンバーがいる場合、控え室から みらくらぱーく！ のカードを1枚手札へ
    # 注意: Prompt 77（ライブ開始時+2ブレード）は既存実装。壊さない。
    # ------------------------------------------------------------------
    if ext_key == "enter_other_member_exists_pick_mirakupark_from_green":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        if not _stage_has_any_other_member(gs, exclude_pos=src_pos):
            try:
                gs.log.append("[AUTO_EXT] no other member on stage (大沢瑠璃乃 bp2-005 enter)")
            except Exception:
                pass
            return True
        candidates = _green_room_cards_by_group_any_type(gs, cards_db, "みらくらぱーく！")
        if not candidates:
            try:
                gs.log.append("[AUTO_EXT] no みらくらぱーく！ card in green_room (大沢瑠璃乃 bp2-005 enter)")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            ok = _move_card_from_green_to_hand(gs, candidates[0])
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {cn_str} (大沢瑠璃乃 bp2-005 enter) ok={ok}")
            except Exception:
                pass
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_card_from_green",
            "candidates": cns,
            "optional": False,
            "after_ext_key": "enter_other_member_exists_pick_mirakupark_from_green__resolve",
            "source_cn": src,
            "label": "【大沢瑠璃乃】控え室からみらくらぱーく！のカードを1枚選んでください",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 大沢瑠璃乃 bp2-005 enter: choose みらくらぱーく！ from green {cns}")
        except Exception:
            pass
        return True

    if ext_key == "enter_other_member_exists_pick_mirakupark_from_green__resolve":
        chosen_cn = str((ctx or {}).get("choice") or (ctx or {}).get("chosen_cn") or "").strip()
        gr = _green_room_list(gs)
        found = None
        for c in list(gr):
            if str(getattr(c, "cardnumber", None) or c or "").strip() == chosen_cn:
                found = c
                break
        if found is not None:
            ok = _move_card_from_green_to_hand(gs, found)
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {chosen_cn} (大沢瑠璃乃 bp2-005 enter resolve) ok={ok}")
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------
    # Prompt 27: PL!-bp4-005 星空凛 (ライブ開始時)
    # ブレード5以上の μ's メンバーがいない場合、このメンバーはセンター以外へポジションチェンジ
    # センター以外 = L / R のみ candidates にする
    # ------------------------------------------------------------------
    if ext_key == "live_start_no_mus_blade5_force_not_center":
        src_pos = str((ctx or {}).get("src_pos") or (ctx or {}).get("pos") or "").upper()
        src = str((ctx or {}).get("source_cn") or "")
        has_heavy_mus = False
        try:
            st = getattr(gs, "stage", None)
            if isinstance(st, dict):
                for pos in ("L", "C", "R"):
                    slot = st.get(pos)
                    if slot is None or not bool(getattr(slot, "cardnumber", None)):
                        continue
                    if _card_group(slot, cards_db) == "μ's" and _slot_total_blade(slot) >= 5:
                        has_heavy_mus = True
                        break
        except Exception:
            pass

        if has_heavy_mus:
            try:
                gs.log.append("[AUTO_EXT] μ's blade>=5 exists, no position_change (星空凛)")
            except Exception:
                pass
            return True

        # センター以外: src_pos が C なら L/R どちらかへ、L/R なら反対側へ
        if src_pos == "C":
            options = ["L", "R"]
        elif src_pos == "L":
            options = ["R"]
        elif src_pos == "R":
            options = ["L"]
        else:
            options = ["L", "R"]

        payload = {
            "kind": "position_change",
            "src_pos": src_pos,
            "optional": False,
            "options": options,
            "source_cn": src,
            "text": f"{src}: 自分のステージにブレード5以上の『μ's』メンバーがいないため、センターエリア以外にポジションチェンジする",
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] 星空凛: force position_change to {options} from {src_pos}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 80: PL!HS-bp2-018 安養寺姫芽 (登場)
    # MAIN 中に [E][E] を任意支払い → green の LIVE を表向きで set_zone に置き、
    # 次の LIVE_SET で手札から置ける上限を 1 減らす。
    # effect_template only; optional energy cost prompt は engine.py 側。
    # ------------------------------------------------------------------
    if ext_key == "enter_main_pay2_faceup_live_to_set_reduce_next_live_set":
        src = str((ctx or {}).get("source_cn") or "安養寺姫芽")
        phase = str(getattr(gs, "phase", "") or "").upper()
        if phase != 'MAIN':
            try:
                gs.log.append(f"[AUTO_EXT] not MAIN, no effect ({src})")
            except Exception:
                pass
            return True

        chosen_cn = str((ctx or {}).get("chosen_cn") or (ctx or {}).get("choice") or "").strip()
        if chosen_cn:
            ok = _move_live_from_green_to_set_zone(gs, chosen_cn)
            try:
                gs.log.append(f"[AUTO_EXT] green->set_zone {chosen_cn} ({src}) ok={ok}")
            except Exception:
                pass
            if ok:
                _reserve_next_live_set_limit_delta(gs, -1, src)
            return True

        candidates = [c for c in _green_room_list(gs) if _card_type_norm(c, cards_db) == 'LIVE']
        try:
            gs.log.append(f"[AUTO_EXT] {src}: green LIVE candidates={len(candidates)}")
        except Exception:
            pass
        if not candidates:
            try:
                gs.log.append(f"[AUTO_EXT] no LIVE in green_room ({src})")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            ok = _move_live_from_green_to_set_zone(gs, candidates[0])
            try:
                gs.log.append(f"[AUTO_EXT] green->set_zone {cn_str} ({src}) ok={ok}")
            except Exception:
                pass
            if ok:
                _reserve_next_live_set_limit_delta(gs, -1, src)
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_live_from_green",
            "text": "控え室のライブカードを1枚選び、表向きでライブカード置き場に置く",
            "options": cns,
            "want_kind": "LIVE",
            "remaining_picks": 1,
            "after_ext_key": "enter_main_pay2_faceup_live_to_set_reduce_next_live_set",
            "ctx": dict(ctx or {}),
            "source_cn": src,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] {src}: choose LIVE from green for set_zone {cns}")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # Prompt 56: PL!-pb1-030 Cutie Panther (ライブ成功時) — 後半のみ EFFECT_ONLY
    # ステージに名前の異なる BiBi が2人以上 → 控え室から BiBi メンバー1枚手札へ
    # 前半（必要ハート減算）は NEEDS_ENGINE のため未実装。
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # bp2_batch3_local_20260413f: PL!HS-bp2-011 村野さやか (登場)
    # デッキ上からカードを5枚控え室に置く。
    # ------------------------------------------------------------------
    if ext_key == "enter_mill5":
        milled = 0
        try:
            deck = getattr(gs, "deck", None)
            waiting = getattr(gs, "green_room", None)
            if waiting is None:
                waiting = (
                    getattr(gs, "waiting_room", None)
                    or getattr(gs, "graveyard", None)
                    or getattr(gs, "discard", None)
                )
            if deck is not None and waiting is not None:
                for _ in range(5):
                    if not deck:
                        break
                    waiting.append(deck.pop(0))
                    milled += 1
        except Exception:
            pass
        try:
            gs.log.append(f"[AUTO_EXT] mill {milled}/5 cards to waiting_room (村野さやか bp2-011)")
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------
    # bp2_batch3_local_20260413f: PL!HS-bp2-015 藤島慈 (自動/BODY)
    # leave-stage -> draw2, discard1
    # ------------------------------------------------------------------
    if ext_key == "body_leave_stage_draw2_discard1":
        trigger = str((ctx or {}).get("trigger") or "").lower()
        if trigger and trigger not in ("leave_stage", "stage_to_green", "stage_leave"):
            try:
                gs.log.append(f"[AUTO_EXT] 藤島慈 bp2-015: trigger={trigger!r} not leave-stage, skip")
            except Exception:
                pass
            return True
        drawn = _draw_cards(eng, gs, 2)
        try:
            gs.log.append(f"[AUTO_EXT] 藤島慈 bp2-015: draw {drawn} (leave-stage)")
        except Exception:
            pass
        enqueue_discard = eng.get("_enqueue_discard_from_hand")
        if callable(enqueue_discard):
            try:
                enqueue_discard(gs, 1, label="【藤島慈】手札を1枚控え室に置く")
            except Exception as e:
                try:
                    gs.log.append(f"[ERR] 藤島慈 bp2-015: enqueue_discard_from_hand failed: {e}")
                except Exception:
                    pass
        else:
            try:
                gs.log.append("[ERR] 藤島慈 bp2-015: _enqueue_discard_from_hand not found")
            except Exception:
                pass
        return True

    if ext_key == "live_success_bibi_2diff_pick_bibi_member_from_green":
        src = str((ctx or {}).get("source_cn") or "")
        diff_count = _stage_unit_count_diff_names(gs, cards_db, "BiBi")
        if diff_count < 2:
            try:
                gs.log.append(f"[AUTO_EXT] BiBi diff_names={diff_count}<2, no effect (Cutie Panther)")
            except Exception:
                pass
            return True
        candidates = _green_room_members_by_group(gs, cards_db, "BiBi")
        if not candidates:
            try:
                gs.log.append("[AUTO_EXT] no BiBi MEMBER in green_room (Cutie Panther)")
            except Exception:
                pass
            return True
        if len(candidates) == 1:
            ok = _move_card_from_green_to_hand(gs, candidates[0])
            cn_str = str(getattr(candidates[0], "cardnumber", None) or candidates[0] or "")
            try:
                gs.log.append(f"[AUTO_EXT] green->hand {cn_str} BiBi (Cutie Panther) ok={ok}")
            except Exception:
                pass
            return True
        cns = [str(getattr(c, "cardnumber", None) or c or "") for c in candidates]
        payload = {
            "kind": "choose_member_from_green",
            "text": "控え室のメンバーカードを1枚手札に加える",
            "options": cns,
            "want_kind": "MEMBER",
            "want_group": "BiBi",
            "remaining_picks": 1,
        }
        try:
            getattr(gs, "pending").append(payload)
            gs.log.append(f"[PENDING] Cutie Panther: choose BiBi MEMBER from green {cns}")
        except Exception:
            pass
        return True

    return False
