# -*- coding: utf-8 -*-
# BUILD_TAG: registry_success_zone_genericize_20260424a
from __future__ import annotations

"""llocg_ui.effects.registry

engine_effect の matcher / ルール定義の正本。

注意:
- ここでは rule table と matcher だけを扱う
- apply や zone 操作 helper は持ち込まない
- 未対応時は None を返し、engine.py 側既存実装へフォールバックさせる
"""

from typing import Any, Dict, Optional, Tuple

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
        "ext_key": "zone_count_temp_bonus",
        "gd": {"count_source": "success_zone", "blade_per_count": "2", "source_name": "西木野真姫", "zero_log": "success_zone=0, no blade added (西木野真姫)"},
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
        "ext_key": "success_zone_score_threshold_action",
        "gd": {"threshold": "6", "action": "activate_energy", "amount": "2", "source_name": "園田海未"},
    },
    # Prompt 31: PL!-bp4-016 東條希 (登場)
    {
        "id": "enter_success_score_ge3_draw1",
        "effect_template": "自分の成功ライブカード置き場にあるカードのスコアの合計が3以上の場合、カードを1枚引く。",
        "ext_key": "success_zone_score_threshold_action",
        "gd": {"threshold": "3", "action": "draw", "amount": "1", "source_name": "東條希"},
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
        "ext_key": "zone_count_temp_bonus",
        "gd": {"count_source": "live_in_progress", "blade_per_count": "1", "source_name": "夕霧綴理", "zero_log": "live_cards=0, no blade (夕霧綴理)"},
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
        "ext_key": "live_start_choose_heart",
        "gd": {"option_labels": "桃,赤,黄,緑,青,紫", "require_other_member": "1"},
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
        "ext_key": "live_start_choose_heart",
        "gd": {"option_labels": "桃,黄,紫", "require_other_member": "0"},
    },
    {
        "id": "live_start_discard1_choose_pink_yellow_purple_heart_v7h",
        "effect_template": "<(桃)>か<(黄)>か<(紫)>のうち、1つを選ぶ。ライブ終了時まで、選んだハートを1つ得る。",
        "ext_key": "live_start_choose_heart",
        "gd": {"option_labels": "桃,黄,紫", "require_other_member": "0"},
    },
    # Prompt: PL!N-bp1-003 桜坂しずく (ライブ開始時)
    # cost=<(E)> 支払いは engine 側 pay_or_skip
    # 好きなハート色1つを選ぶ（6色）
    {
        "id": "live_start_pay1_choose_any_heart",
        "effect_template": "好きなハートの色を1つ指定する。ライブ終了時まで、そのハートを1つ得る。",
        "ext_key": "live_start_choose_heart",
        "gd": {"option_labels": "桃,赤,黄,緑,青,紫", "require_other_member": "0"},
    },

    # Prompt: PL!N-bp3-008 エマ・ヴェルデ (ライブ開始時)
    # 共通部（実テキスト基準）:
    # - 「自分のステージにいるこのメンバー以外のウェイト状態のメンバー1人をアクティブにする。そうした場合、」
    # - 「これによりアクティブにしたメンバーと、このメンバーは、それぞれ〜を得る。」
    {
        "id": "live_start_discard2_activate_other_wait_member_both_green1",
        "effect_template": "自分のステージにいるこのメンバー以外のウェイト状態のメンバー1人をアクティブにする。そうした場合、ライブ終了時まで、これによりアクティブにしたメンバーと、このメンバーは、それぞれ<(緑)>を得る。",
        "ext_key": "live_start_activate_wait_member_and_both_temp_bonus",
        "gd": {
            "source_name": "エマ・ヴェルデ",
            "select_text": "アクティブにするメンバーを選んでください",
            "hearts": "green:1",
            "no_target_log": "no other wait member on stage (エマ・ヴェルデ)"
        },
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
        "ext_key": "live_start_pick_stage_member_temp_bonus",
        "gd": {"source_name": "Oh,Love&Peace!", "select_text": "ブレード+3を与えるメンバーを選んでください", "blade": "3", "auto_if_single": "1", "no_target_log": "no stage members, no blade (Oh,Love&Peace!)"},
    },
    # Prompt 30: PL!-bp4-013 園田海未 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    {
        "id": "live_start_pick_other_stage_member_pink1",
        "effect_template": "ライブ終了時まで、自分のステージにいるこのメンバー以外のメンバー1人は、<(桃)>を得る。",
        "ext_key": "live_start_pick_stage_member_temp_bonus",
        "gd": {"source_name": "園田海未", "select_text": "桃ハート+1を与えるメンバーを選んでください（このメンバー以外）", "hearts": "pink:1", "exclude_self": "1", "auto_if_single": "1", "no_target_log": "no other members on stage (園田海未 bp4-013)"},
    },
    # Prompt 32: PL!-bp4-017 小泉花陽 (ライブ開始時)
    # cost=このメンバーをウェイトにしてもよい → engine 側 pay_or_skip
    # センターの μ's メンバーにブレード付与（対象が固定なので選択不要）
    {
        "id": "live_start_center_mus_blade1",
        "effect_template": "ライブ終了時まで、自分のセンターエリアにいる『μ's』のメンバーは、<(ブレード)>を得る。",
        "ext_key": "live_start_apply_stage_temp_bonus",
        "gd": {"source_name": "小泉花陽", "positions": "C", "group_eq": "μ's", "blade": "1", "no_target_log": "center is not μ's or empty (小泉花陽 bp4-017)"},
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
        "ext_key": "live_start_pick_stage_member_temp_bonus",
        "gd": {"source_name": "小夜啼鳥恋詩", "select_text": "ブレード+1を与えるμ'sメンバーを選んでください", "blade": "1", "group_eq": "μ's", "auto_if_single": "0", "no_target_log": "no μ's on stage (小夜啼鳥恋詩)"},
    },
    # Prompt 46: PL!-pb1-010 高坂穂乃果 (ライブ開始時)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # このメンバー以外全員に +1ブレード（選択なし、対象が複数固定）
    {
        "id": "live_start_other_stage_members_blade1",
        "effect_template": "ライブ終了時まで、自分のステージにいるほかのメンバーは<(ブレード)>を得る。",
        "ext_key": "live_start_apply_stage_temp_bonus",
        "gd": {"source_name": "高坂穂乃果", "exclude_self": "1", "blade": "1", "no_target_log": "no other members on stage (高坂穂乃果 pb1-010)"},
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
    # 共通部（実テキスト基準）:
    # - 「これにより控え室に置いたカードがメンバーカードの場合、」
    # - 「控え室に置いたカードと同じ名前を持つメンバー1人は、」
    # - 「ライブ終了時まで、〜を得る。」
    {
        "id": "live_start_discard_member_same_name_green1_blade1",
        "effect_template": "これにより控え室に置いたカードがメンバーカードの場合、控え室に置いたカードと同じ名前を持つメンバー1人は、ライブ終了時まで、<(緑)><(ブレード)>を得る。",
        "ext_key": "live_start_discarded_member_same_name_stage_member_temp_bonus",
        "gd": {
            "source_name": "百生吟子",
            "discarded_type": "MEMBER",
            "select_text": "と同名のメンバーを選んでください",
            "hearts": "green:1",
            "blade": "1"
        },
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
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, dict(r.get("gd") or {}))
        if s_norm == _norm_ws(tpl):
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, dict(r.get("gd") or {}))

    # cards_compiled_v7b splits some abilities into multiple clauses.
    # Match the actual clause fragment that engine.py sees.
    fragment_rules = [
        # Prompt 60: cost-only split clause should be matched narrowly.
        # Do NOT match broader sentences like PL!-bp3-004 that also contain
        # "手札を1枚控え室に置いてもよい" but are different effects.
        (("live_start_choose_heart", {"option_labels": "桃,黄,紫", "require_other_member": "0"}),
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
    for payload, pred in fragment_rules:
        try:
            if not pred(s_norm):
                continue
            if isinstance(payload, tuple):
                ext_key, gd = payload
                return ({"id": ext_key, "op": "__ext__", "ext_key": ext_key}, dict(gd or {}))
            ext_key = payload
            return ({"id": ext_key, "op": "__ext__", "ext_key": ext_key}, {})
        except Exception:
            pass
    return None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
