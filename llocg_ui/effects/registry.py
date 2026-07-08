# -*- coding: utf-8 -*-
# BUILD_TAG: stage_cost_lower_draw2_top_20260624b
# PATCH_TAG: effect_registry_generic_green_recovery_20260629z
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
    {
        "id": "live_start_my_cost_lower_draw2_hand_top1",
        "effect_template": "自分のステージにいるメンバーのコストの合計が相手より低い場合、カードを2枚引き、自分の手札を1枚デッキの一番上に置く。",
        "ext_key": "live_start_my_cost_lower_draw2_hand_top1",
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
    {
        "id": "enter_success_score_ge3_draw1_b5_015",
        "effect_template": "自分の成功ライブカード置き場にあるカードのスコアの合計が3以上の場合、カードを1枚引く。",
        "ext_key": "success_zone_score_threshold_action",
        "gd": {"threshold": "3", "action": "draw", "amount": "1", "source_name": "西木野真姫 bp5-015"},
    },
    {
        "id": "enter_success_score_ge6_put_active_energy1",
        "effect_template": "自分の成功ライブカード置き場にあるカードのスコアの合計が6以上の場合、自分のエネルギーデッキから、エネルギーカードを1枚アクティブ状態で置く。",
        "ext_key": "success_zone_score_threshold_action",
        "gd": {"threshold": "6", "action": "put_active_energy_from_deck", "amount": "1", "source_name": "星空凛 bp5-005"},
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
        "id": "look_top2_choose_one_to_hand_rest_green",
        "effect_template": "自分のデッキの上からカードを2枚見る。その中から1枚を手札に加え、残りを控え室に置く。",
        "ext_key": "topk_choose_one_to_hand_rest_green",
        "gd": {"topk": "2", "source_name": "top2 choose1"},
    },
    {
        "id": "look_top3_choose_one_to_hand_rest_green",
        "effect_template": "自分のデッキの上からカードを3枚見る。その中から1枚を手札に加え、残りを控え室に置く。",
        "ext_key": "topk_choose_one_to_hand_rest_green",
        "gd": {"topk": "3", "source_name": "top3 choose1"},
    },
    {
        "id": "look_top3_choose_one_hand_one_top_rest_green",
        "effect_template": "自分のデッキの上からカードを3枚見る。その中から1枚を手札に加え、1枚をデッキの上に置き、1枚を控え室に置く。",
        "ext_key": "topk_split_one_hand_one_top_rest_green",
        "gd": {"topk": "3", "source_name": "東條希 bp3-007"},
    },
    {
        "id": "body_mill10",
        "effect_template": "自分のデッキの上からカードを10枚控え室に置く。",
        "ext_key": "mill_topk_to_green",
        "gd": {"topk": "10", "source_name": "小泉花陽 sd1-008"},
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
        "ext_key": "green_pick_filtered_to_hand",
        "gd": {
            "source_name": "南ことり bp3-003",
            "want_kind": "MEMBER",
            "want_group": "μ's",
            "pending_label": "【南ことり】控え室からμ'sのメンバーカードを1枚選んでください",
            "no_candidates_log": "[AUTO_EXT] no μ's MEMBER in green_room (南ことり bp3-003)"
        },
    },
    # Prompt 16: PL!-bp3-004 園田海未 (ライブ開始時)
    # 成功置き場にカードがある場合のみ発動可
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # 控え室から μ's のライブカードを1枚手札に加える
    {
        "id": "live_start_success_zone_exists_discard1_pick_mus_live_from_green",
        "effect_template": "自分の控え室から『μ's』のライブカードを1枚手札に加える。",
        "ext_key": "green_pick_filtered_to_hand",
        "gd": {
            "source_name": "園田海未 bp3-004",
            "want_kind": "LIVE",
            "want_group": "μ's",
            "require_success_zone": "1",
            "pending_label": "【園田海未】控え室からμ'sのライブカードを1枚選んでください",
            "no_effect_log": "[AUTO_EXT] success_zone empty, no effect (園田海未 bp3-004)",
            "no_candidates_log": "[AUTO_EXT] no μ's LIVE in green_room (園田海未 bp3-004)"
        },
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
        "ext_key": "green_pick_filtered_to_hand",
        "gd": {
            "source_name": "日野下花帆",
            "want_kind": "LIVE",
            "want_group": "蓮ノ空",
            "score_max": "3",
            "pending_label": "【日野下花帆】控え室からスコア3以下の蓮ノ空ライブカードを1枚選んでください",
            "no_candidates_log": "[AUTO_EXT] no 蓮ノ空 LIVE score<=3 in green_room (日野下花帆)"
        },
    },
    # Prompt 76: PL!HS-bp2-005 大沢瑠璃乃 (登場)
    # cost=手札を1枚控え室に置いてもよい → engine 側 pay_or_skip
    # 他メンバーがいる場合、控え室から みらくらぱーく！ のカードを1枚手札に加える
    {
        "id": "enter_discard1_other_member_exists_pick_mirakupark_from_green",
        "effect_template": "自分のステージにほかのメンバーがいる場合、自分の控え室から『みらくらぱーく！』のカードを1枚手札に加える。",
        "ext_key": "green_pick_filtered_to_hand",
        "gd": {
            "source_name": "大沢瑠璃乃 bp2-005",
            "want_group": "みらくらぱーく！",
            "require_other_member": "1",
            "pending_label": "【大沢瑠璃乃】控え室からみらくらぱーく！のカードを1枚選んでください",
            "no_effect_log": "[AUTO_EXT] no other member on stage (大沢瑠璃乃 bp2-005 enter)",
            "no_candidates_log": "[AUTO_EXT] no みらくらぱーく！ card in green_room (大沢瑠璃乃 bp2-005 enter)"
        },
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
        "ext_key": "green_pick_filtered_to_hand",
        "gd": {
            "source_name": "Cutie Panther",
            "want_kind": "MEMBER",
            "want_group": "BiBi",
            "require_unit_diff_names_label": "BiBi",
            "require_unit_diff_names_ge": "2",
            "pending_label": "【Cutie Panther】控え室からBiBiのメンバーカードを1枚選んでください",
            "no_effect_log": "[AUTO_EXT] BiBi diff_names<2, no effect (Cutie Panther)",
            "no_candidates_log": "[AUTO_EXT] no BiBi MEMBER in green_room (Cutie Panther)"
        },
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
        "ext_key": "reorder_from_topk",
        "gd": {"topk": "3", "source_name": "乙宗梢 bp2-003"},
    },
    {
        "id": "body_tsukasa_mirakupark_count_blade",
        "effect_template": "自分のステージにいるほかの『みらくらぱーく！』のメンバー1人につき、<(ブレード)>を得る。",
        "ext_key": "body_mirakupark_others_count_blade",
    },
    {
        "id": "enter_kaho_bp2010_top5_member_optional",
        "effect_template": "自分のデッキの上からカードを5枚見る。その中からメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",
        "ext_key": "topk_filtered_optional_pick",
        "gd": {"topk": "5", "filter_kind": "MEMBER", "optional": "1", "source_name": "日野下花帆 bp2-010"},
    },
    {
        "id": "body_kozue_bp2012_stage_to_green_top5_member_optional",
        "effect_template": "このメンバーがステージから控え室に置かれたとき、自分のデッキの上からカードを5枚見る。その中からメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",
        "ext_key": "topk_filtered_optional_pick",
        "gd": {"topk": "5", "filter_kind": "MEMBER", "optional": "1", "source_name": "乙宗梢 bp2-012"},
    },
    {
        "id": "body_tsuzuri_bp2013_stage_to_green_top5_live_optional",
        "effect_template": "このメンバーがステージから控え室に置かれたとき、自分のデッキの上からカードを5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",
        "ext_key": "topk_filtered_optional_pick",
        "gd": {"topk": "5", "filter_kind": "LIVE", "optional": "1", "source_name": "夕霧綴理 bp2-013"},
    },
    {
        "id": "enter_umi_sd1004_top5_mus_live_optional",
        "effect_template": "自分のデッキの上からカードを5枚見る。その中から『μ's』のライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",
        "ext_key": "topk_filtered_optional_pick",
        "gd": {"topk": "5", "filter_kind": "LIVE", "filter_group": "μ's", "optional": "1", "source_name": "園田海未 sd1-004"},
    },
    {
        "id": "enter_ren_bp1005_top5_liella_card_optional",
        "effect_template": "自分のデッキの上からカードを5枚見る。その中から『Liella!』のカードを1枚まで公開して手札に加えてもよい。残りを控え室に置く。",
        "ext_key": "topk_filtered_optional_pick",
        "gd": {"topk": "5", "filter_group": "Liella!", "optional": "1", "source_name": "葉月恋 bp1-005"},
    },
    {
        "id": "enter_karin_pb1016_top2_named_member_optional",
        "effect_template": "自分のデッキの上からカードを2枚見る。その中から『朝香果林』のメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",
        "ext_key": "topk_filtered_optional_pick",
        "gd": {"topk": "2", "filter_kind": "MEMBER", "filter_names": "朝香果林", "optional": "1", "source_name": "朝香果林 pb1-016"},
    },
    {
        "id": "enter_eri_bp5002_top5_cost9_ge_mus_member_optional",
        "effect_template": "自分のデッキの上からカードを5枚見る。その中からコスト9以上の『μ's』のメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。",
        "ext_key": "topk_filtered_optional_pick",
        "gd": {"topk": "5", "filter_kind": "MEMBER", "filter_group": "μ's", "cost_min": "9", "optional": "1", "source_name": "絢瀬絵里 bp5-002"},
    },
    {
        "id": "enter_ginko_bp2016_reorder_top2",
        "effect_template": "自分のデッキの上からカードを2枚見る。その中から好きな枚数を好きな順番でデッキの上に置き、残りを控え室に置く。",
        "ext_key": "reorder_from_topk",
        "gd": {"topk": "2", "source_name": "百生吟子 bp2-016"},
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
        "ext_key": "mill_topk_to_green",
        "gd": {"topk": "5", "source_name": "村野さやか bp2-011"},
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
    """Normalize effect-template text for extension matching.

    The DB/compiler may emit official-style icon tokens such as ``<桃>`` while
    older extension rules use runtime-style tokens such as ``<(桃)>``. Treat those
    as equivalent here so existing generic rules are not bypassed just because of
    icon spelling. Trigger tags like ``<ライブ開始時>`` are intentionally left
    untouched.
    """
    import re as _re
    s = _re.sub(r'\s+', ' ', (text or "").strip())
    icon_names = "桃|赤|黄|緑|青|紫|任意|ALL|E|ブレード"
    s = _re.sub(r'<(' + icon_names + r')>', r'<(\1)>', s)
    # Remove space before icon token: "は、 <(ブレード)>" -> "は、<(ブレード)>"
    s = _re.sub(r' (<\([^)]*\)>)', r'\1', s)
    # Remove space after icon token: "<(ブレード)> を" -> "<(ブレード)>を"
    s = _re.sub(r'(<\([^)]*\)>) ', r'\1', s)
    return s



_COLOR_ICON_TO_KEY = {
    "桃": "pink",
    "赤": "red",
    "黄": "yellow",
    "緑": "green",
    "青": "blue",
    "紫": "purple",
    "任意": "any",
    "ALL": "all",
}


def _parse_temp_bonus_icon_run(icon_run: str) -> Dict[str, str]:
    """Return gd fragments for a contiguous icon run such as <(桃)><(ブレード)>."""
    import re as _re
    blade = 0
    hearts: Dict[str, int] = {}
    for raw in _re.findall(r'<\(([^)]+)\)>', _norm_ws(icon_run or "")):
        token = str(raw or "").strip()
        if token == "ブレード":
            blade += 1
            continue
        key = _COLOR_ICON_TO_KEY.get(token)
        if key:
            hearts[key] = int(hearts.get(key, 0) or 0) + 1
    gd: Dict[str, str] = {}
    if blade > 0:
        gd["blade"] = str(blade)
    if hearts:
        gd["hearts"] = ",".join(f"{k}:{v}" for k, v in hearts.items() if int(v or 0) > 0)
    return gd



def _parse_condition_for_stage_member_temp_bonus(condition_text: str) -> Optional[Dict[str, str]]:
    """Parse lightweight conditional wrappers for stage-member temp-bonus effects.

    Supported condition fragments are intentionally generic and data-shaped:
    - 成功ライブカード置き場にカードがN枚以上ある
    - 控え室に『X』のメンバーカードがN枚以上ある
    - ライブ中のライブカードに、ライブ開始時/ライブ成功時能力を持たないカードがある
    """
    import re as _re
    c = _norm_ws(condition_text or "")
    gd: Dict[str, str] = {}

    m = _re.fullmatch(r"自分の成功ライブカード置き場にカードが(?P<n>\d+)枚以上ある", c)
    if m:
        gd["require_success_zone_count_min"] = str(m.group("n"))
        return gd

    m = _re.fullmatch(r"自分の控え室に『(?P<group>[^』]+)』のメンバーカードが(?P<n>\d+)枚以上ある", c)
    if m:
        gd["require_green_group_or_unit_member_count_min"] = str(m.group("n"))
        gd["require_green_group_or_unit"] = str(m.group("group") or "").strip()
        return gd

    if _re.fullmatch(r"自分のライブ中のライブカードに、<ライブ開始時>能力も<ライブ成功時>能力も持たないカードがある", c):
        gd["require_live_without_live_start_success_abilities"] = "1"
        return gd

    return None


def _try_match_generic_conditional_stage_member_temp_bonus(effect_text: str) -> Optional[Tuple[Dict[str, Any], Dict[str, str]]]:
    """Generic conditional wrapper for one-target stage-member temp bonus.

    Covers effects of the form:
      <condition>場合、ライブ終了時まで、自分のステージにいる<target>メンバー1人は、<icons>を得る。

    This reuses the existing live_start_pick_stage_member_temp_bonus resolver and
    only adds condition metadata. Complex target predicates are still left out.
    """
    import re as _re
    t = _norm_ws(effect_text or "")
    m = _re.fullmatch(
        r"(?P<cond>.+?)場合、ライブ終了時まで、自分のステージにいる(?P<target>.*?)メンバー1人は、?(?P<icons>(?:<\([^)]*\)>)+)を得る。",
        t,
    )
    if not m:
        return None

    cond_gd = _parse_condition_for_stage_member_temp_bonus(str(m.group("cond") or ""))
    if cond_gd is None:
        return None

    target = str(m.group("target") or "")
    if "を持つ" in target or "名前" in target or "これにより" in target:
        return None

    gd = _parse_temp_bonus_icon_run(m.group("icons") or "")
    if not gd:
        return None
    gd.update(cond_gd)
    gd["select_text"] = "一時ボーナスを与えるメンバーを選んでください"
    gd["effect_text"] = t
    gd["auto_if_single"] = "0"
    if "このメンバー以外" in target or "ほかの" in target:
        gd["exclude_self"] = "1"
    cm = _re.search(r"コスト\s*(\d+)\s*以上", target)
    if cm:
        gd["cost_min"] = cm.group(1)
    quoted = _re.findall(r"『([^』]+)』", target)
    if len(quoted) == 1:
        gd["group_or_unit_eq"] = quoted[0].strip()
    elif len(quoted) > 1:
        return None
    gd["no_target_log"] = "no valid stage member target (generic conditional stage member temp bonus)"
    return (
        {"id": "generic_conditional_stage_member_temp_bonus", "op": "__ext__", "ext_key": "live_start_pick_stage_member_temp_bonus"},
        gd,
    )

def _try_match_generic_stage_member_temp_bonus(effect_text: str) -> Optional[Tuple[Dict[str, Any], Dict[str, str]]]:
    """Generic live-start target bonus matcher.

    Covers one-target stage-member effects of the form:
    - ライブ終了時まで、自分のステージにいるメンバー1人は、<icons>を得る。
    - ライブ終了時まで、自分のステージにいる『X』のメンバー1人は、<icons>を得る。
    - ライブ終了時まで、自分のステージにいるこのメンバー以外の『X』のメンバー1人は、<icons>を得る。
    - ライブ終了時まで、自分のステージにいるコストN以上の『X』のメンバー1人は、<icons>を得る。

    It intentionally does not absorb conditional wrappers such as
    「〜場合、ライブ終了時まで...」; those need a separate wrapper rule.
    """
    import re as _re
    t = _norm_ws(effect_text or "")
    m = _re.fullmatch(
        r"ライブ終了時まで、自分のステージにいる(?P<target>.*?)メンバー1人は、?(?P<icons>(?:<\([^)]*\)>)+)を得る。",
        t,
    )
    if not m:
        return None
    target = str(m.group("target") or "")
    # More complex target predicates need their own wrapper, not this simple matcher.
    if "を持つ" in target or "名前" in target or "これにより" in target:
        return None
    gd = _parse_temp_bonus_icon_run(m.group("icons") or "")
    if not gd:
        return None
    gd["select_text"] = "一時ボーナスを与えるメンバーを選んでください"
    gd["effect_text"] = t
    gd["auto_if_single"] = "0"
    if "このメンバー以外" in target or "ほかの" in target:
        gd["exclude_self"] = "1"
    cm = _re.search(r"コスト\s*(\d+)\s*以上", target)
    if cm:
        gd["cost_min"] = cm.group(1)
    quoted = _re.findall(r"『([^』]+)』", target)
    if len(quoted) == 1:
        gd["group_or_unit_eq"] = quoted[0].strip()
    elif len(quoted) > 1:
        return None
    gd["no_target_log"] = "no valid stage member target (generic stage member temp bonus)"
    return (
        {"id": "generic_stage_member_temp_bonus", "op": "__ext__", "ext_key": "live_start_pick_stage_member_temp_bonus"},
        gd,
    )



def _try_match_generic_topdeck_choose_to_hand_rest_green(effect_text: str):
    # BUILD_TAG: registry_generic_topdeck_choose_n_20260629aa
    import re as _re
    t = _norm_ws(effect_text or '')
    if not t or '公開' in t:
        return None
    m = _re.match(
        r'^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から(?:カードを)?(?P<n>\d+)枚(?P<upto>まで)?(?:を)?手札に加え(?:、|る。)残りを控え室に置く。?$',
        t,
    )
    if not m:
        return None
    k = str(m.group('k') or '')
    n = str(m.group('n') or '')
    upto = bool(m.group('upto'))
    gd = {
        'source_name': f'デッキ上{k}枚から{n}枚回収',
        'topk': k,
        'pick_count': n,
        'min_pick_count': '0' if upto else n,
        'max_pick_count': n,
        'optional': '1' if upto else '0',
        'effect_text': t,
    }
    return ({'id': 'generic_topdeck_choose_n_to_hand_rest_green', 'op': '__ext__', 'ext_key': 'topk_choose_n_to_hand_rest_green'}, gd)


def _try_match_generic_green_recovery(effect_text: str):
    """Generic matcher for safe one-card / up-to-N green-room recovery.

    This catches wording variants not worth enumerating as card-specific rules,
    while still restricting to green-room -> hand effects only.
    """
    import re as _re
    t = _norm_ws(effect_text or '')
    if not t:
        return None

    def _kind_from_jp(kind_jp: str) -> str:
        return 'LIVE' if 'ライブ' in kind_jp else ('MEMBER' if 'メンバー' in kind_jp else '')

    # 自分の控え室からコスト2以下のメンバーカードを2枚まで手札に加える。
    m = _re.match(r'^自分の控え室(?:から|にある)、?(?:(?:コスト(?P<cost>\d+)以下)|(?:(?P<cost2>\d+)コスト以下))の(?:(?:『(?P<group>[^』]+)』の))?メンバーカードを(?P<n>\d+)枚まで手札に加える。?$', t)
    if m:
        gd = {
            'source_name': '控え室回収',
            'want_kind': 'MEMBER',
            'cost_max': str((m.groupdict().get('cost') or m.groupdict().get('cost2') or '')),
            'min_picks': '0',
            'max_picks': str(m.group('n') or '1'),
            'effect_text': t,
        }
        if m.group('group'):
            gd['want_group'] = m.group('group').strip()
        return ({'id': 'generic_green_cost_le_member_upto_n', 'op': '__ext__', 'ext_key': 'green_pick_filtered_to_hand_multi'}, gd)

    # 自分の控え室からコスト2以下のメンバーカードを1枚手札に加える。
    m = _re.match(r'^自分の控え室(?:から|にある)、?(?:(?:コスト(?P<cost>\d+)以下)|(?:(?P<cost2>\d+)コスト以下))の(?:(?:『(?P<group>[^』]+)』の))?メンバーカード(?:を1枚|1枚を)手札に加える。?$', t)
    if m:
        gd = {
            'source_name': '控え室回収',
            'want_kind': 'MEMBER',
            'cost_max': str((m.groupdict().get('cost') or m.groupdict().get('cost2') or '')),
            'effect_text': t,
        }
        if m.group('group'):
            gd['want_group'] = m.group('group').strip()
        return ({'id': 'generic_green_cost_le_member_one', 'op': '__ext__', 'ext_key': 'green_pick_filtered_to_hand'}, gd)

    # 自分の控え室から、スコア6以上のライブカードを1枚手札に加える。
    m = _re.match(r'^自分の控え室(?:から|にある)、?スコア(?P<score>\d+)(?P<cmp>以上|以下)の(?:(?:『(?P<group>[^』]+)』の))?ライブカード(?:を1枚|1枚を)手札に加える。?$', t)
    if m:
        gd = {
            'source_name': '控え室回収',
            'want_kind': 'LIVE',
            'effect_text': t,
        }
        if m.group('cmp') == '以上':
            gd['score_min'] = str(m.group('score') or '')
        else:
            gd['score_max'] = str(m.group('score') or '')
        if m.group('group'):
            gd['want_group'] = m.group('group').strip()
        return ({'id': 'generic_green_live_score_threshold_one', 'op': '__ext__', 'ext_key': 'green_pick_filtered_to_hand'}, gd)

    # 控え室から必要ハートに<(黄)>を3以上含むライブカードを1枚手札に加える。
    m = _re.match(r'^(?:自分の)?控え室(?:から|にある)、?必要ハートに<\(?(?P<color>[^)>]+)\)?>を(?P<n>\d+)以上含むライブカード(?:を1枚|1枚を)手札に加える。?$', t)
    if m:
        color = str(m.group('color') or '').strip()
        color_map = {'桃': 'pink', '赤': 'red', '黄': 'yellow', '緑': 'green', '青': 'blue', '紫': 'purple'}
        gd = {
            'source_name': '必要ハート条件ライブ回収',
            'want_kind': 'LIVE',
            'req_heart_color': color_map.get(color, color),
            'req_heart_min': str(m.group('n') or '1'),
            'effect_text': t,
        }
        return ({'id': 'generic_green_live_required_heart_threshold_one', 'op': '__ext__', 'ext_key': 'green_pick_filtered_to_hand'}, gd)

    # 自分の控え室にあるライブカードを1枚手札に加える。
    # 自分の控え室から『Liella!』のライブカードを1枚手札に加える。
    m = _re.match(r'^自分の控え室(?:から|にある)、?(?:(?:『(?P<group>[^』]+)』の))?(?P<kind>ライブ|メンバー)カード(?:を1枚|1枚を)手札に加える。?$', t)
    if m:
        gd = {
            'source_name': '控え室回収',
            'want_kind': _kind_from_jp(m.group('kind') or ''),
            'effect_text': t,
        }
        if m.group('group'):
            gd['want_group'] = m.group('group').strip()
        return ({'id': 'generic_green_kind_one', 'op': '__ext__', 'ext_key': 'green_pick_filtered_to_hand'}, gd)

    # 自分の控え室から『みらくらぱーく！』のカードを1枚手札に加える。
    m = _re.match(r'^自分の控え室(?:から|にある)、?『(?P<group>[^』]+)』のカード(?:を1枚|1枚を)手札に加える。?$', t)
    if m:
        gd = {
            'source_name': '控え室回収',
            'want_group': m.group('group').strip(),
            'effect_text': t,
        }
        return ({'id': 'generic_green_group_card_one', 'op': '__ext__', 'ext_key': 'green_pick_filtered_to_hand'}, gd)

    return None

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
            gd0 = dict(r.get("gd") or {})
            gd0.setdefault("effect_text", s_norm)
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, gd0)
        if s_norm == _norm_ws(tpl):
            gd0 = dict(r.get("gd") or {})
            gd0.setdefault("effect_text", s_norm)
            return ({"id": r.get("id"), "op": "__ext__", "ext_key": r.get("ext_key")}, gd0)

    generic_topdeck_choose = _try_match_generic_topdeck_choose_to_hand_rest_green(s_norm)
    if generic_topdeck_choose is not None:
        return generic_topdeck_choose

    generic_green_recovery = _try_match_generic_green_recovery(s_norm)
    if generic_green_recovery is not None:
        return generic_green_recovery

    generic_conditional_stage_bonus = _try_match_generic_conditional_stage_member_temp_bonus(s_norm)
    if generic_conditional_stage_bonus is not None:
        return generic_conditional_stage_bonus

    generic_stage_bonus = _try_match_generic_stage_member_temp_bonus(s_norm)
    if generic_stage_bonus is not None:
        return generic_stage_bonus

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
        (("green_pick_filtered_to_hand", {
            "source_name": "園田海未 bp3-004",
            "want_kind": "LIVE",
            "want_group": "μ's",
            "require_success_zone": "1",
            "pending_label": "【園田海未】控え室からμ'sのライブカードを1枚選んでください",
            "no_effect_log": "[AUTO_EXT] success_zone empty, no effect (園田海未 bp3-004)",
            "no_candidates_log": "[AUTO_EXT] no μ's LIVE in green_room (園田海未 bp3-004)"
        }),
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
