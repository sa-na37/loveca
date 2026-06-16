# -*- coding: utf-8 -*-
# BUILD_TAG: popup_next_skip_and_keke_enter_trigger_20260616aq
from __future__ import annotations
"""llocg_ui.engine
UI から呼ばれるゲーム状態とコマンド処理（手動UI用の最小実装）。
注意：このファイルは「現状よく動く」単体版 llocg_ui_web.py のロジックをそのまま移植し、
機能欠けを起こさないことを最優先にしています。
今後ルール厳密化（フェイズ機械・ライブ選択最適化等）を行う場合も、
UI 側の API（cmd/state の入出力）を壊さないのが前提です。
"""
import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
# Energy deck total (fixed)
ENERGY_TOTAL_DEFAULT = 12
from .db import (
    CardInfo,
    _safe_int, _read_json, _write_text,
    _hearts_from_counts_json, _parse_tags_json, _count_draw_icons,
    is_member_type, is_live_type,
    _canon_cardno, _cardno_variants, _get_card,
)
# ----------------------------
# Effect-template rule engine (regex-based)
# ----------------------------
import re
# NOTE:
# - Embedded minimal, high-impact subset to avoid increasing external files.
# - Matching is strict (regex anchored with ^...$).
_EFFECT_RULES = [
    {"id": "draw_n", "pattern": r"^カードを(?P<n>\d+)枚引く。$", "op": "draw"},
    {"id": "draw_n_then_gain_icons_until_end_live", "pattern": r"^カードを(?P<n>\d+)枚引き、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "draw_then_gain_icons_until_end_live"},
    {"id": "draw_then_stage_group_member_temp_cost", "pattern": r"^カードを(?P<draw_n>\d+)枚引き、ライブ終了時まで、自分のステージにいる『(?P<group>[^』]+)』のメンバー1人のコストを\+(?P<cost_n>\d+)する。$", "op": "draw_then_stage_group_member_temp_cost"},
    {"id": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte", "pattern": r"^自分のステージにいる『(?P<group>[^』]+)』のメンバー1人を選ぶ。ライブ終了時まで、このメンバーのコストは、選んだメンバーが元々持つコストより(?P<minus_n>\d+)低い値に等しくなる。これによりこのカードのコストが(?P<threshold>\d+)以上になった場合、ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte"},
    {"id": "self_temp_cost_then_stage_group_cost_sum_gt_opponent_gain_icons", "pattern": r"^ライブ終了時まで、このメンバーのコストを\+(?P<cost_n>\d+)する。その後、自分のステージにいる『(?P<group>[^』]+)』のメンバーのコストの合計が、相手のステージにいるメンバーのコストの合計より高い場合、さらにライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "self_temp_cost_then_stage_group_cost_sum_gt_opponent_gain_icons"},
    {"id": "draw_n_discard_m", "pattern": r"^カードを(?P<n>\d+)枚引き、手札を(?P<m>\d+)枚控え室に置く。$", "op": "draw_then_discard"},
    {"id": "discard_hand_n", "pattern": r"^手札を(?P<n>\d+)枚控え室に置く。$", "op": "discard_from_hand"},
    {"id": "retrieve_waiting_live_n", "pattern": r"^自分の控え室からライブカードを(?P<n>\d+)枚手札に加える。$", "op": "retrieve_from_waiting_room", "card_kind": "LIVE"},
    {"id": "retrieve_waiting_member_n", "pattern": r"^自分の控え室からメンバーカードを(?P<n>\d+)枚手札に加える。$", "op": "retrieve_from_waiting_room", "card_kind": "MEMBER"},
    {"id": "retrieve_waiting_live_group_n", "pattern": r"^自分の控え室から『(?P<group>[^』]+)』のライブカードを(?P<n>\d+)枚手札に加える。$", "op": "retrieve_from_waiting_room", "card_kind": "LIVE"},
    {"id": "look_top_k_choose_1_rest_waiting", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から1枚を手札に加え、残りを控え室に置く。$", "op": "look_top_choose"},
    {"id": "look_top_k_choose_if_energy_gte", "pattern": r"^自分のエネルギーが(?P<n>\d+)枚以上ある場合、自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から1枚を手札に加え、残りを控え室に置く。$", "op": "look_top_choose_if", "cond": "energy_gte"},
        {"id": "look_top_k_reorder_keep_any_rest_waiting", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から好きな枚数を好きな順番でデッキの上に置き、残りを控え室に置く。$", "op": "look_top_reorder_keep_any"},
    {"id": "topdeck_green_any_upto1", "pattern": r"^自分の控え室からカードを1枚までデッキの一番上に置く。$", "op": "topdeck_from_green", "card_kind": "ANY", "allow_less": True},
    {"id": "topdeck_green_member_n", "pattern": r"^自分の控え室にあるメンバーカード(?P<n>\d+)枚を好きな順番でデッキの一番上に置く。$", "op": "topdeck_from_green", "card_kind": "MEMBER", "allow_less": False},
    {"id": "topdeck_green_live_group_upto_n", "pattern": r"^自分の控え室にある『(?P<group>[^』]+)』のライブカードを(?P<n>\d+)枚まで好きな順番でデッキの上に置く。$", "op": "topdeck_from_green", "card_kind": "LIVE", "allow_less": True},
    {"id": "topdeck_green_live_group_upto1_then_draw_if_opponent_wait_exists", "pattern": r"^自分の控え室から『(?P<group>[^』]+)』のライブカードを1枚までデッキの一番上に置く。その後、相手のステージにウェイト状態のメンバーがいる場合、カードを1枚引く。$", "op": "topdeck_green_live_group_upto1_then_draw_if_opponent_wait_exists"},
    # Put cards on the bottom of the deck. These use the same card-list UI
    # as other zone picks, but route to deck bottom instead of hand/topdeck.
    {"id": "bottomdeck_green_kind_upto_n", "pattern": r"^自分の控え室から(?:(?P<kind>ライブ|メンバー)カード|カード)を(?P<n>\d+)枚までデッキの一番下に置く。$", "op": "bottomdeck_from_green", "allow_less": True},
    {"id": "choose_self_or_opponent_green_member_upto_bottom", "pattern": r"^自分か相手を選ぶ。自分は、そのプレイヤーの控え室にあるメンバーカードを(?P<n>\d+)枚まで、好きな順番でデッキの一番下に置く。$", "op": "choose_player_green_to_bottom", "card_kind": "MEMBER", "allow_less": True},
    {"id": "choose_self_or_opponent_green_live_bottom_draw", "pattern": r"^自分か相手を選ぶ。自分は、そのプレイヤーの控え室にあるライブカードを(?P<n>\d+)枚、そのプレイヤーのデッキの一番下に置く。そうした場合、自分はカードを(?P<draw_n>\d+)枚引く。$", "op": "choose_player_green_to_bottom", "card_kind": "LIVE", "allow_less": False, "draw_if_moved": True},
    {"id": "choose_self_or_opponent_top1_mill_optional", "pattern": r"^自分か相手を選ぶ。自分は、そのプレイヤーのデッキの一番上のカードを見る。自分はそのカードを控え室に置いてもよい。$", "op": "choose_player_deck_top_action", "action": "top1_optional_green"},
    {"id": "choose_self_or_opponent_topk_reorder_keep_any", "pattern": r"^自分か相手を選ぶ。自分は、そのプレイヤーのデッキの上からカードを(?P<k>\d+)枚見る。その中から好きな枚数を好きな順番でデッキの上に置き、残りを控え室に置く。$", "op": "choose_player_deck_top_action", "action": "topk_reorder_keep_any"},
    {"id": "bottom_all_green_members_optional_group_threshold_stage_named_blade", "pattern": r"^自分の控え室にあるすべてのメンバーカードをシャッフルし、デッキの下に置いてもよい。これにより『(?P<threshold_group>[^』]+)』のカードを(?P<threshold_n>\d+)枚以上デッキの下に置いた場合、ライブ終了時まで、自分のステージにいる「(?P<target_name>[^」]+)」1人は(?P<blades>(?:<\(ブレード\)>)+)を得る。$", "op": "bottom_all_green_members_optional_group_threshold_stage_named_blade"},
    {"id": "both_players_bottom_all_green_members_threshold_retrieve_live_gain_blade", "pattern": r"^自分と相手はそれぞれ、自身の控え室にあるすべてのメンバーカードをシャッフルし、自身のデッキの下に置く。これにより自分と相手のカードが合計(?P<threshold_n>\d+)枚以上デッキの下に置かれた場合、自分の控え室からライブカードを(?P<retrieve_n>\d+)枚手札に加え、ライブ終了時まで、(?P<blades>(?:<\(ブレード\)>)+)を得る。$", "op": "both_players_bottom_all_green_members_threshold_retrieve_live_gain_blade"},
    {"id": "draw_then_hand_bottom", "pattern": r"^カードを(?P<draw_n>\d+)枚引き、手札を(?P<bottom_n>\d+)枚デッキの一番下に置く。$", "op": "draw_then_hand_to_deck_bottom"},
    {"id": "draw_then_hand_top_or_bottom", "pattern": r"^カードを(?P<draw_n>\d+)枚引き、手札からカードを(?P<n>\d+)枚デッキの一番上か一番下に置く。$", "op": "draw_then_hand_to_deck_top_or_bottom"},
    {"id": "score_draw_then_hand_top_or_bottom_if_all_stage_group", "pattern": r"^自分のステージにいるメンバーがすべて『(?P<group>[^』]+)』の場合、このカードのスコアを\+(?P<score_n>\d+)し、カードを(?P<draw_n>\d+)枚引き、手札からカードを(?P<n>\d+)枚デッキの一番上か一番下に置く。$", "op": "score_draw_then_hand_top_or_bottom_if_all_stage_group"},
    {"id": "live_zone_group_only_required_color_sum_gain_all", "pattern": r"^自分のライブカード置き場にあるカードが『(?P<group>[^』]+)』のみで、かつそれらの必要ハートに含まれる(?P<icons>(?:<\([^)]+\)>と?)+)の合計が(?P<threshold>\d+)以上の場合、ライブ終了時まで、(?P<all_icons>(?:<\(ALL\)>)+)を得る。$", "op": "live_zone_group_only_required_color_sum_gain_all"},
    {"id": "energy_put_wait_then_manual_draw_if_no_bladeheart", "pattern": r"^自分のエネルギーデッキから、エネルギーカードを(?P<n>\d+)枚ウェイト状態で置く。これにより控え室に置いたカードがブレードハートを持たない場合、カードを(?P<draw_n>\d+)枚引く。$", "op": "energy_put_wait_then_manual_draw_if_no_bladeheart"},
    {"id": "energy_put_wait_n", "pattern": r"^自分のエネルギーデッキから、エネルギーカードを(?P<n>\d+)枚ウェイト状態で置く。$", "op": "energy_put_wait"},
    {"id": "energy_put_wait_under_plus_one_self", "pattern": r"^(?:自分の)?エネルギーデッキから、このメンバーの下にあるエネルギーカードの枚数に1を足した枚数のエネルギーカードをウェイト状態で置く。$", "op": "energy_put_wait_under_plus_one_self"},
    {"id": "energy_activate_n", "pattern": r"^エネルギーを(?P<n>\d+)枚アクティブにする。$", "op": "energy_activate"},
    {"id": "gain_blade_until_end_live", "pattern": r"^ライブ終了時まで、(?P<blades>(?:<\(ブレード\)>)+)を得る。$", "op": "gain_blade_until_end_live"},
    {"id": "activate_stage_member_upto1", "pattern": r"^自分のステージにいるメンバーを1人までアクティブにする。$", "op": "activate_stage_member"},
    {"id": "activate_stage_member_optional_any", "pattern": r"^メンバー1人をアクティブにしてもよい。$", "op": "activate_stage_member", "optional": True},
    {"id": "position_change_stage_member_optional_any", "pattern": r"^メンバー1人をポジションチェンジさせてもよい。$", "op": "position_change_stage_member", "optional": True},
    {"id": "optional_discard_one_from_hand_then_effect", "pattern": r"^手札を1枚控え室に置いてもよい。そうした場合、(?P<after>.+)$", "op": "optional_discard_one_from_hand_then_effect"},
    {"id": "retrieve_waiting_live_and_member_upto1", "pattern": r"^自分の控え室からライブカードとメンバーカードをそれぞれ1枚まで手札に加える。$", "op": "retrieve_waiting_live_and_member_upto1"},
    {"id": "stage_member_gain_icons_until_end_live", "pattern": r"^ライブ終了時まで、自分のステージにいるメンバー1人は、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "stage_member_gain_icons_until_end_live"},
    {"id": "leave_baton_no_bladeheart_nijigasaki_energy_draw", "pattern": r"^このメンバーがコスト(?P<cost1>\d+)以上のブレードハートを持たない『(?P<group1>[^』]+)』のメンバーとバトンタッチしていた場合、エネルギーを(?P<energy_n>\d+)枚アクティブにする。コスト(?P<cost2>\d+)以上のブレードハートを持たない『(?P<group2>[^』]+)』のメンバーの場合、さらにカードを(?P<draw_n>\d+)枚引く。$", "op": "leave_baton_no_bladeheart_nijigasaki_energy_draw"},
    # Fixed-color hearts (and mixed hearts+blades): e.g. "ライブ終了時まで、<(黄)><(黄)>を得る。"
    # Must come AFTER gain_blade_until_end_live so pure-blade still matches first.
    {"id": "gain_icons_until_end_live", "pattern": r"^ライブ終了時まで、(?P<icons>(?:<(?:\([^)]+\)|[^<>]+)>)+)を得る。$", "op": "gain_icons_until_end_live"},
    # Free heart choice (self): "好きなハートの色を1つ指定する。ライブ終了時まで、そのハートを1つ得る。"
    {"id": "choose_heart_gain_self", "pattern": r"^好きなハートの色を1つ指定する。ライブ終了時まで、そのハートを1つ得る。$", "op": "choose_heart_gain_self"},
    # Free heart choice (other group member)
    {"id": "choose_heart_gain_other_member", "pattern": r"^好きなハートの色を1つ指定する。ライブ終了時まで、自分のステージにいるこのメンバー以外の『(?P<group>[^』]+)』のメンバー1人は、そのハートを1つ得る。$", "op": "choose_heart_gain_other_member"},
    # Activate all stage members
    {"id": "activate_all_stage_members", "pattern": r"^自分のステージにいるすべてのメンバーをアクティブにする。$", "op": "activate_all_stage_members"},
    # Energy activate up to n
    {"id": "energy_activate_upto_n", "pattern": r"^エネルギーを(?P<n>\d+)枚までアクティブにする。$", "op": "energy_activate_upto"},
    # Conditional draw
    {"id": "draw_if_energy_gte", "pattern": r"^自分のエネルギーが(?P<n>\d+)枚以上ある場合、カードを1枚引く。$", "op": "draw_if", "cond": "energy_gte"},
    {"id": "draw_if_stage_cost_gte", "pattern": r"^自分のステージにコスト(?P<n>\d+)以上のメンバーがいる場合、カードを1枚引く。$", "op": "draw_if", "cond": "stage_member_cost_gte"},
    {"id": "draw_if_success_nonempty", "pattern": r"^自分の成功ライブカード置き場にカードがある場合、カードを1枚引く。$", "op": "draw_if", "cond": "success_nonempty"},
    {"id": "draw_if_green_size_gte", "pattern": r"^自分の控え室にカードが(?P<n>\d+)枚以上ある場合、カードを1枚引く。$", "op": "draw_if", "cond": "green_size_gte"},
    {"id": "activate_wait_member_then_temp_blade", "pattern": r"^ウェイト状態のメンバー1人をアクティブにし、ライブ終了時まで、そのメンバーは(?P<blades>(?:<\(ブレード\)>)+)を得る。$", "op": "activate_wait_member_then_temp_blade"},
    # Self-wait (as effect): "このメンバーをウェイトにする。"
    {"id": "set_self_wait_member", "pattern": r"^このメンバーをウェイトにする。$", "op": "set_self_wait"},
    # Opponent wait family.  Opponent board is not modeled, so these resolve via
    # the shared manual-resolution notice.  Keep these broad enough to absorb
    # older/newer DB wording such as ウェイト状態にする / メンバ1人.
    {"id": "set_opponent_wait_upto_n_state", "pattern": r"^相手のステージ(?:に)?いるコスト(?P<cost>\d+)以下のメンバーを(?P<max_n>\d+)人までウェイト(?:状態)?にする。$", "op": "set_opponent_wait"},
    {"id": "set_opponent_wait_upto1_cost", "pattern": r"^相手のステージ(?:に)?いるコスト(?P<cost>\d+)以下のメンバーを(?P<max_n>1)人までウェイト(?:状態)?にする。$", "op": "set_opponent_wait"},
    {"id": "set_opponent_wait_exactly1", "pattern": r"^相手のステージ(?:に)?いるコスト(?P<cost>\d+)以下のメンバ(?:ー)?1人をウェイト(?:状態)?にする。$", "op": "set_opponent_wait_exactly1"},
    {"id": "set_opponent_wait_all_cost", "pattern": r"^相手のステージ(?:に)?いるすべてのコスト(?P<cost>\d+)以下のメンバーをウェイト(?:状態)?にする。$", "op": "set_opponent_wait_all_cost"},
    {"id": "set_opponent_wait_original_blade_le", "pattern": r"^相手のステージにいる元々持つ<\(ブレード\)>(?:の数)?が(?P<blade_lim>\d+)(?:つ|個)?以下のメンバー1人をウェイトにする。$", "op": "set_opponent_wait_original_blade_le"},
    {"id": "set_opponent_wait_original_blade_eq", "pattern": r"^相手のステージにいる元々持つ<\(ブレード\)>(?:の数)?がちょうど(?P<blade_eq>\d+)(?:つ|個)?のメンバー1人をウェイトにする。$", "op": "set_opponent_wait_original_blade_eq"},
    {"id": "set_opponent_wait_original_blade_le_not_group", "pattern": r"^相手のステージにいる元々持つ<\(ブレード\)>(?:の数)?が(?P<blade_lim>\d+)(?:つ|個)?以下の『(?P<group>[^』]+)』以外のメンバー1人をウェイトにする。$", "op": "set_opponent_wait_original_blade_le_not_group"},
    {"id": "set_opponent_wait_all_original_blade_le", "pattern": r"^相手のステージにいる元々持つ<\(ブレード\)>(?:の数)?が(?P<blade_lim>\d+)(?:つ|個)?以下のすべてのメンバーをウェイトにする。$", "op": "set_opponent_wait_all_original_blade_le"},
    {"id": "both_players_wait_all_original_blade_le", "pattern": r"^自分と相手のステージにいる元々持つ<\(ブレード\)>(?:の数)?が(?P<blade_lim>\d+)(?:つ|個)?以下のすべてのメンバーをウェイトにする。$", "op": "both_players_wait_all_original_blade_le"},
    {"id": "opponent_wait_side_cost_gte", "pattern": r"^相手のステージの右サイドエリアか左サイドエリアにいるコスト(?P<cost>\d+)以上のメンバー1人をウェイトにする。$", "op": "opponent_wait_manual_text"},
    {"id": "draw_1_then_opponent_wait_cost_upto1", "pattern": r"^カードを1枚引く。相手のステージ(?:に)?いるコスト(?P<cost>\d+)以下のメンバーを(?P<max_n>1)人までウェイト(?:状態)?にする。$", "op": "draw_then_opponent_wait"},
    {"id": "conditional_opponent_wait_manual", "pattern": r"^(?P<condition>.+場合)、(?P<action>相手(?:は|のステージ).+ウェイト.+)$", "op": "conditional_opponent_wait_manual"},
    # Opponent self-choice wait
    {"id": "set_opponent_wait_self_choice", "pattern": r"^相手は、?自身のステージにいるアクティブ状態のメンバー1人をウェイトにする。$", "op": "set_opponent_wait_self_choice"},
    # look_top with optional pick + type/group filter
    # e.g. "デッキ上5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残り控え室"
    {"id": "look_top_k_optional_type", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から(?P<kind>ライブ|メンバー)カードを1枚(?:まで)?公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True},
    # with group filter: "その中から『G』のカードを1枚公開して手札に加えてもよい"
    {"id": "look_top_k_optional_group", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から『(?P<group>[^』]+)』のカードを1枚(?:まで)?公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True},
    # with group+type: "その中から『G』のライブカードを1枚公開して..."
    {"id": "look_top_k_optional_group_type", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から『(?P<group>[^』]+)』の(?P<kind>ライブ|メンバー)カードを1枚(?:まで)?公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True},
    # with name filter: "その中から「名前A」か「名前B」のメンバーカードを1枚公開して..."
    {"id": "look_top_k_optional_names_type", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から(?P<names>(?:「[^」]+」(?:か「[^」]+」)*)の)?(?P<kind>ライブ|メンバー)カードを1枚公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True},
    # Additional top-k filtered pick variants from the updated DB.  These still
    # resolve through the same choose_from_topk pending; only the filter predicate
    # is widened here.
    {"id": "look_top_k_optional_cost_ge_any", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中からコスト(?P<cost_min>\d+)以上のカードを1枚公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True},
    {"id": "look_top_k_optional_group_live_required_total_ge", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から必要ハートの合計が(?P<required_total_min>\d+)以上の『(?P<group>[^』]+)』のライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True, "card_kind": "LIVE"},
    {"id": "look_top_k_optional_member_heart_color_min", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中からハートに(?P<member_heart_icon><(?:\([^)]+\)|[^<>]+)>)を(?P<member_heart_min>\d+)(?:つ|個)以上持つメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True, "card_kind": "MEMBER"},
    {"id": "look_top_k_optional_member_heart_any_color", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中からハートに(?P<member_heart_icons>(?:<(?:\([^)]+\)|[^<>]+)>か?)+)を持つメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True, "card_kind": "MEMBER"},
    {"id": "look_top_k_optional_member_heart_or_live_required", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中からハートに(?P<member_heart_icon><(?:\([^)]+\)|[^<>]+)>)を(?P<member_heart_min>\d+)(?:つ|個)以上持つメンバーカードか、必要ハートに(?P<live_req_icon><(?:\([^)]+\)|[^<>]+)>)を(?P<live_req_min>\d+)以上含むライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。$", "op": "look_top_choose_filtered", "optional": True, "filter_mode": "member_heart_or_live_req"},
    # 3-way split: 1->hand, 1->deck top, 1->green
    {"id": "look_top_3_split", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から1枚を手札に加え、1枚をデッキの上に置き、1枚を控え室に置く。$", "op": "look_top_3way_split"},
    # Retrieve from yell reveals: group-filtered
    {"id": "retrieve_yell_group_any", "pattern": r"^エールにより公開された自分のカードの中から、?『(?P<group>[^』]+)』のカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "ANY"},
    # Retrieve from yell reveals: type-filtered (LIVE or MEMBER)
    {"id": "retrieve_yell_live", "pattern": r"^エールにより公開された自分のカードの中から、ライブカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "LIVE"},
    {"id": "retrieve_yell_member", "pattern": r"^エールにより公開された自分のカードの中から、メンバーカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "MEMBER"},
    # Retrieve up to N cards from yell reveals (e.g. not ALONE not HITORI).
    {"id": "retrieve_yell_type_upto_n", "pattern": r"^エールにより公開された自分のカードの中から、(?:(?P<kind>ライブ|メンバー)カード|カード)を(?P<n>\d+)枚まで手札に加える。$", "op": "retrieve_from_yell", "up_to": True},
    # Retrieve from yell reveals: group+type (e.g. 『μ's』のメンバーカード)
    {"id": "retrieve_yell_group_member", "pattern": r"^エールにより公開された自分のカードの中から、?『(?P<group>[^』]+)』のメンバーカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "MEMBER"},
    {"id": "retrieve_yell_group_live", "pattern": r"^エールにより公開された自分のカードの中から、?『(?P<group>[^』]+)』のライブカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "LIVE"},
    {"id": "retrieve_yell_group_type_upto_n", "pattern": r"^エールにより公開された自分のカードの中から、?『(?P<group>[^』]+)』の(?P<kind>ライブ|メンバー)カードを(?P<n>\d+)枚まで手札に加える。$", "op": "retrieve_from_yell", "up_to": True},
    # Retrieve from yell reveals: cost2-member OR score2-live (e.g. PL!HS-PR-027, PL!N-PR-021, PL!SP-PR-016)
    {"id": "retrieve_yell_cost2member_or_score2live", "pattern": r"^エールにより公開された自分のカードの中から、コスト(?P<cost_lim>\d+)以下のメンバーカードか、スコア(?P<score_lim>\d+)以下のライブカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "COST_MEMBER_OR_SCORE_LIVE"},
    # Retrieve from yell reveals: additional generic filters introduced in newer DB.
    {"id": "retrieve_yell_any_one", "pattern": r"^エールにより公開された自分のカードの中から、カードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "ANY"},
    {"id": "retrieve_yell_cost_member_le", "pattern": r"^エールにより公開された自分のカードの中から、コスト(?P<cost_lim>\d+)以下のメンバーカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "COST_MEMBER_LE"},
    {"id": "retrieve_yell_cost_member_ge", "pattern": r"^エールにより公開された自分のカードの中から、コスト(?P<cost_min>\d+)以上のメンバーカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "COST_MEMBER_GE"},
    {"id": "retrieve_yell_group_cost_member_between", "pattern": r"^エールにより公開された自分のカードの中から、コスト(?P<cost_min>\d+)以上(?P<cost_lim>\d+)以下の『(?P<group>[^』]+)』のメンバーカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "COST_MEMBER_RANGE"},
    # Put cards revealed by yell onto the deck (top/bottom).  Keep both
    # 「エールで公開された」 and 「エールにより公開された」 variants because DB text uses both.
    {"id": "put_yell_revealed_any_to_deck_top_optional", "pattern": r"^エール(?:で|により)公開された自分のカードの中から、カードを1枚(?:まで)?デッキの一番上に置いてもよい。$", "op": "put_yell_to_deck_top", "card_kind": "ANY", "up_to": True},
    {"id": "put_yell_revealed_type_to_deck_top_optional", "pattern": r"^エール(?:で|により)公開された自分のカードの中から、(?P<kind>ライブ|メンバー)カードを1枚(?:まで)?デッキの一番上に置いてもよい。$", "op": "put_yell_to_deck_top", "up_to": True},
    # Put cards revealed by yell on the bottom of the deck (e.g. 未体験HORIZON).
    {"id": "put_yell_revealed_type_upto_deck_bottom", "pattern": r"^エール(?:で|により)公開された自分のカードの中から、(?:(?P<kind>ライブ|メンバー)カード|カード)を(?P<n>\d+)枚までデッキの一番下に置く。$", "op": "put_yell_to_deck_bottom"},
]
_EFFECT_RULES_COMPILED = [{**r, "re": re.compile(r["pattern"])} for r in _EFFECT_RULES]
_HEART_ICON_COLOR_MAP = {
    '桃': 'pink', '赤': 'red', '黄': 'yellow',
    '緑': 'green', '青': 'blue', '紫': 'purple',
}
_HEART_JP_MAP = {
    '桃': 'pink', '赤': 'red', '黄': 'yellow',
    '緑': 'green', '青': 'blue', '紫': 'purple',
    'pink': 'pink', 'red': 'red', 'yellow': 'yellow',
    'green': 'green', 'blue': 'blue', 'purple': 'purple',
}
def _parse_heart_icons(icon_blob: str) -> Dict[str, int]:
    """Parse heart icon strings into color -> count dict.

    The current compiled DB may contain either official-style ``<桃>`` tokens or
    older normalized ``<(桃)>`` tokens. Treat both as the same icon family, while
    ignoring non-heart tags such as ブレード / E / ALL.
    """
    counts: Dict[str, int] = {}
    for m in re.finditer(r'<(?:\(([^)]+)\)|([^<>]+))>', str(icon_blob or '')):
        jp = str((m.group(1) or m.group(2) or '')).strip()
        col = _HEART_ICON_COLOR_MAP.get(jp)
        if col:
            counts[col] = counts.get(col, 0) + 1
    return counts

def _heart_icon_to_color(icon_blob: str) -> str:
    counts = _parse_heart_icons(str(icon_blob or ''))
    for col in ('pink', 'red', 'yellow', 'green', 'blue', 'purple'):
        if counts.get(col, 0) > 0:
            return col
    return ''

def _heart_icons_to_colors(icon_blob: str) -> List[str]:
    counts = _parse_heart_icons(str(icon_blob or ''))
    return [col for col in ('pink', 'red', 'yellow', 'green', 'blue', 'purple') if counts.get(col, 0) > 0]

def _ci_member_heart_count(ci: Optional[CardInfo], color: str) -> int:
    """Count member heart icons of one color, including blade-hearts by rule 2.1.3."""
    col = str(color or '').strip().lower()
    if not ci or col not in {'pink','red','yellow','green','blue','purple'}:
        return 0
    total = 0
    for attr in ('base_hearts', 'blade_hearts'):
        try:
            total += int((getattr(ci, attr, {}) or {}).get(col, 0) or 0)
        except Exception:
            pass
    if total > 0:
        return total
    # fallback for older/newly scraped raw fields
    raw = str(getattr(ci, 'base_hearts_raw', '') or '') + ' ' + str(getattr(ci, 'blade_heart_raw', '') or '')
    return int(_parse_heart_icons(_normalize_icon_token_text(raw)).get(col, 0) or 0)

def _ci_live_required_heart_count(ci: Optional[CardInfo], color: str) -> int:
    col = str(color or '').strip().lower()
    if not ci or col not in {'pink','red','yellow','green','blue','purple'}:
        return 0
    try:
        val = int((getattr(ci, 'required_hearts', {}) or {}).get(col, 0) or 0)
        if val > 0:
            return val
    except Exception:
        pass
    raw = str(getattr(ci, 'required_hearts_raw', '') or '')
    return int(_parse_heart_icons(_normalize_icon_token_text(raw)).get(col, 0) or 0)

def _ci_live_required_total(ci: Optional[CardInfo]) -> int:
    if not ci:
        return 0
    try:
        total = sum(int(v or 0) for v in (getattr(ci, 'required_hearts', {}) or {}).values())
        if total > 0:
            return total
    except Exception:
        pass
    raw = str(getattr(ci, 'required_hearts_raw', '') or '')
    m = re.search(r'合計\s*(\d+)', _norm_digits_jp(raw))
    if m:
        return int(m.group(1))
    return sum(int(v or 0) for v in _parse_heart_icons(_normalize_icon_token_text(raw)).values())

def _normalize_icon_token_text(text: str) -> str:
    """Normalize official-style icon tags to the older internal <(...)> form.

    The updated DB contains both <桃>/<ALL>/<スコア+1> and legacy <(桃)> forms.
    Runtime regexes historically used <(...)>, so normalize at parser boundaries.
    """
    t = str(text or '')
    # Normalize split score icon spelling such as <(スコア)+1> into <(スコア+1)>.
    t = re.sub(r'<\(\s*スコア\s*\)\s*([+＋]\s*\d+)\s*>', lambda m: '<(スコア' + m.group(1).replace('＋', '+').replace(' ', '') + ')>', t)

    def repl(m: re.Match) -> str:
        inner = str(m.group(1) or '').strip()
        if not inner:
            return m.group(0)
        if inner.startswith('(') and inner.endswith(')'):
            return '<' + inner + '>'
        key = inner.replace('＋', '+').replace(' ', '')
        if key in {'桃', '赤', '黄', '緑', '青', '紫', '任意', 'ALL', 'ブレード', 'E'}:
            return f'<({key})>'
        if re.match(r'^(?:スコア|ドロー)[+\-]\d+$', key):
            return f'<({key})>'
        return m.group(0)

    return re.sub(r'<([^<>]+)>', repl, t)


def _parse_named_hand_discard_cost(cost_text: str) -> Optional[Dict[str, Any]]:
    """Parse optional costs that discard named cards from hand.

    Supported shared forms:
      - 手札の「A」と「B」と「C」を好きな枚数控え室に置いてもよい
      - 手札の「A」と「B」と「C」を、好きな組み合わせで合計3枚、控え室に置いてもよい

    Returns a small contract used by the generic hand-card selection pending.
    """
    t = str(cost_text or '').strip()
    if not t or '手札の「' not in t or '控え室に置いてもよい' not in t:
        return None
    t = _normalize_icon_token_text(t)
    names = [str(x or '').strip() for x in re.findall(r'「([^」]+)」', t) if str(x or '').strip()]
    if not names:
        return None
    # Exact-N optional cost: user may pay exactly N cards, or skip the optional cost.
    m_exact = re.search(r'好きな組み合わせで合計\s*(\d+)\s*枚、?控え室に置いてもよい', t)
    if m_exact:
        n = int(m_exact.group(1) or 0)
        if n <= 0:
            return None
        return {
            'names': names,
            'min_picks': n,
            'max_picks': n,
            'exact_or_zero': True,
            'mode': 'exact_or_skip',
        }
    # Up-to-any optional cost: after choosing Pay, the user may still choose 0..available.
    if re.search(r'好きな枚数控え室に置いてもよい', t):
        return {
            'names': names,
            'min_picks': 0,
            'max_picks': None,
            'exact_or_zero': False,
            'mode': 'up_to_any',
        }
    return None


def _parse_group_hand_discard_cost(cost_text: str) -> Optional[Dict[str, Any]]:
    """Parse optional costs that discard cards of a specified group/unit from hand.

    Supported shared forms:
      - 手札の『DOLLCHESTRA』のカードを1枚控え室に置いてもよい
      - 手札の『蓮ノ空』のカード1枚を控え室に置いてもよい
      - 手札の『蓮ノ空』のメンバーカードを3枚まで控え室に置いてもよい

    Returns a contract for the generic hand multi-select/discard pending.
    """
    t = _norm_digits_jp(str(cost_text or '').strip())
    if not t or '手札の『' not in t or '控え室に置いてもよい' not in t:
        return None
    t = _normalize_icon_token_text(t)
    m = re.search(r"手札の『(?P<group>[^』]+)』の(?P<kind>メンバーカード|ライブカード|カード)(?:を)?(?P<n>\d+)?枚(?P<upto>まで)?(?:を)?控え室に置いてもよい", t)
    if not m:
        return None
    group = str(m.group('group') or '').strip()
    kind_jp = str(m.group('kind') or 'カード')
    n = int(m.group('n') or 1)
    if n <= 0 or not group:
        return None
    kind = 'ANY'
    if 'メンバー' in kind_jp:
        kind = 'MEMBER'
    elif 'ライブ' in kind_jp:
        kind = 'LIVE'
    upto = bool(m.group('upto'))
    return {
        'group': group,
        'kind': kind,
        'min_picks': 0,
        'max_picks': n,
        'exact_or_zero': not upto,
        'mode': 'up_to' if upto else 'exact_or_skip',
    }


def _hand_named_card_candidates(gs: 'GameState', cards_db: Dict[str, CardInfo], names: List[str]) -> List[str]:
    wanted = {str(x or '').strip() for x in list(names or []) if str(x or '').strip()}
    out: List[str] = []
    if not wanted:
        return out
    for cn in list(getattr(gs, 'hand', []) or []):
        ci = _get_card(cards_db, cn)
        nm = str(getattr(ci, 'name', '') or getattr(ci, 'cardname', '') or '').strip() if ci else ''
        if nm in wanted:
            out.append(cn)
    return out


def _card_heart_colors_for_cost_result(ci: Optional[CardInfo]) -> List[str]:
    """Return distinct colored heart names a card has for cost-result effects.

    Blade-heart icons are also heart icons by rule, so include both base_hearts
    and blade_hearts. Ignore any/all/non-colored tags for this effect.
    """
    cols: List[str] = []
    if not ci:
        return cols
    for mp in (getattr(ci, 'base_hearts', {}) or {}, getattr(ci, 'blade_hearts', {}) or {}):
        try:
            items = list(mp.items())
        except Exception:
            items = []
        for col, n in items:
            c = str(col or '').strip().lower()
            if c in ('pink', 'red', 'yellow', 'green', 'blue', 'purple') and int(n or 0) > 0 and c not in cols:
                cols.append(c)
    return cols

def _is_named_hand_cost_result_effect(effect_text: str) -> bool:
    """Return True for effect templates whose value depends on selected/discarded hand cards."""
    t = _normalize_icon_token_text(str(effect_text or '').strip()).replace('\n', '')
    if not t:
        return False
    patterns = [
        r'^ライブ終了時まで、「<常時>ライブの合計スコアを\+\d+する。」を得る。$',
        r'^ライブ終了時まで、これ(?:によって|により)控え室に置いた枚数1枚につき(?:<\([^)]+\)>)+を得る。$',
        r'^ライブ終了時まで、これにより控え室に置いたそれらのカードが持つハートの色1つにつき、その色のハートを1つずつ得る。$',
    ]
    return any(re.match(pat, t) for pat in patterns)


def _is_success_storage_score_sum_effect_wrapper(effect_text: str) -> bool:
    """Return True for success-zone score/count conditional wrappers.

    These wrappers are handled explicitly in try_apply_effect_template().  They must
    also be recognized by _match_effect_template() so [登場] support detection can
    enqueue the auto trigger instead of silently ignoring the ability.
    """
    t = _normalize_icon_token_text(str(effect_text or '').strip()).replace('\n', '')
    if not t:
        return False
    pats = [
        r'^自分の成功ライブカード置き場にあるカードのスコア(?:の)?合計が\d+以上の場合、.+$',
        r'^自分の成功ライブカード置き場にカードが\d+枚以上あり、かつスコアの合計が\d+以下の場合、.+$',
        r"^自分の成功ライブカード置き場に<\(スコア\+1\)>を持つ『[^』]+』のカードが1枚ある場合、ライブ終了時まで、(?:『|「)<常時>ライブの合計スコアを\+1する。(?:』|」)を得る。2枚以上ある場合、代わりに(?:『|「)<常時>』?ライブの合計スコアを\+2する。(?:』|」)を得る。$",
    ]
    return any(re.match(pat, t) for pat in pats)


def _is_success_storage_count_effect_wrapper(effect_text: str) -> bool:
    """Return True for success-zone card-count conditional wrappers.

    These wrappers are solved explicitly by try_apply_effect_template(), and must
    also be visible to _match_effect_template() so entry/activated trigger
    collection can enqueue them.
    """
    t = _normalize_icon_token_text(str(effect_text or '').strip()).replace('\n', '')
    if not t:
        return False
    pats = [
        r'^自分の成功ライブカード置き場にカードがある場合、.+$',
        r'^自分の成功ライブカード置き場にカードが\d+枚以上(?:ある)?場合、.+$',
    ]
    return any(re.match(pat, t) for pat in pats)


def _strip_stage_to_green_trigger_prefix(effect_text: str) -> str:
    """Return the inner effect for BODY triggers of the form
    「このメンバーがステージから控え室に置かれたとき、...」.
    The trigger itself is handled by the stage-leave trigger collector; the inner
    effect should go through the normal generic effect-template route.
    """
    t = _normalize_icon_token_text(str(effect_text or '').strip()).replace('\n', '')
    prefix = 'このメンバーがステージから控え室に置かれたとき、'
    if t.startswith(prefix):
        return t[len(prefix):].strip()
    return str(effect_text or '').strip()

def _is_stage_to_green_effect_wrapper(effect_text: str) -> bool:
    inner = _strip_stage_to_green_trigger_prefix(effect_text)
    return bool(inner and inner != str(effect_text or '').strip() and _match_effect_template(inner))

def _match_effect_template(effect_text: str):
    s = (effect_text or "").strip()
    if not s:
        return None
    # Extension hook: keep runtime entrypoint stable in engine.py, while allowing
    # Claude-sized effect work to live in the much smaller engine_effect.py.
    # The extension module should stay import-light and must not import this
    # engine module at import time (avoid circular imports). It receives the
    # current engine globals only when matching is requested.
    try:
        from . import engine_effect as _engine_effect
        m_ext = _engine_effect.try_match_effect_template_ext(globals(), s)
        if m_ext:
            return m_ext
    except Exception:
        pass
    inner_stage_leave = _strip_stage_to_green_trigger_prefix(s)
    if inner_stage_leave != s and _match_effect_template(inner_stage_leave):
        return ({'id': 'stage_to_green_effect_wrapper', 'op': 'stage_to_green_effect_wrapper'}, {})
    if _is_success_storage_score_sum_effect_wrapper(s):
        return ({'id': 'success_storage_score_sum_wrapper', 'op': 'success_storage_score_sum_wrapper'}, {})
    if _is_success_storage_count_effect_wrapper(s):
        return ({'id': 'success_storage_count_wrapper', 'op': 'success_storage_count_wrapper'}, {})
    # Activation-cost reduction text is not part of the resolved effect. Strip it
    # before matching the inner effect so BODY activated abilities can be queued.
    # Only enter the activation-cost-reduction wrapper when the text actually
    # contains that sentence.  _strip_activated_success_count_discard_cost_reduction()
    # also normalizes icon spelling (<青> -> <(青)>); comparing its output to the
    # original string alone would incorrectly wrap ordinary effects containing
    # official-style icons.
    if 'この能力を起動するためのコストは' in s:
        s_act_cost = _strip_activated_success_count_discard_cost_reduction(s)
        if s_act_cost != s and _match_effect_template(s_act_cost):
            return ({'id': 'activated_success_count_discard_cost_reduction_wrapper', 'op': 'activated_success_count_discard_cost_reduction_wrapper'}, {})
    if _activated_success_score_sum_condition(s):
        return ({'id': 'activated_success_score_sum_condition_wrapper', 'op': 'activated_success_score_sum_condition_wrapper'}, {})
    if re.match(r'^自分のステージにほかの『[^』]+』のメンバーがいる場合、.+$', _normalize_icon_token_text(s).replace('\n','')):
        return ({'id': 'stage_has_other_group_or_unit_member_wrapper', 'op': 'stage_has_other_group_or_unit_member_wrapper'}, {})
    candidates = [s]
    s_norm = _normalize_icon_token_text(s)
    if s_norm != s:
        candidates.append(s_norm)
    for ss in candidates:
        for r in _EFFECT_RULES_COMPILED:
            m = r["re"].match(ss)
            if m:
                gd = {k: v for k, v in m.groupdict().items() if v is not None}
                return (r, gd)
    return None

def _yell_revealed_candidates(
    gs: GameState,
    cards_db: Dict[str, CardInfo],
    card_kind: str = 'ANY',
    group: str = '',
    cost_lim: int = 99,
    score_lim: int = 99,
    cost_min: int = 0,
) -> List[str]:
    """Return current selectable cards that were revealed by yell this live.

    Cards may still be in resolve_zone, or may already have been acknowledged into
    the green room. The tracker keeps the logical revealed set until live cleanup.
    """
    kind = str(card_kind or 'ANY').upper()
    group = str(group or '')
    pool = [_canon_cardno(x) for x in list(getattr(gs, '_yell_revealed_this_live', []) or [])]
    cands: List[str] = []
    seen: set = set()
    for zone_name in ('resolve_zone', 'green_room'):
        z = getattr(gs, zone_name, None)
        if not isinstance(z, list):
            continue
        for cn2 in list(z):
            canon2 = _canon_cardno(str(cn2 or ''))
            if not canon2 or canon2 in seen:
                continue
            if canon2 not in pool:
                continue
            ci2 = _get_card(cards_db, cn2)
            if not ci2:
                continue
            if kind == 'LIVE' and not _is_live_ci(ci2):
                continue
            if kind == 'MEMBER' and not _is_member_ci(ci2):
                continue
            if kind == 'COST_MEMBER_OR_SCORE_LIVE':
                ok2 = False
                if _is_member_ci(ci2) and int(getattr(ci2, 'cost', 0) or 0) <= int(cost_lim or 99):
                    ok2 = True
                if _is_live_ci(ci2) and int(getattr(ci2, 'score', 0) or 0) <= int(score_lim or 99):
                    ok2 = True
                if not ok2:
                    continue
            if kind == 'COST_MEMBER_LE':
                if not (_is_member_ci(ci2) and int(getattr(ci2, 'cost', 0) or 0) <= int(cost_lim or 99)):
                    continue
            if kind == 'COST_MEMBER_GE':
                if not (_is_member_ci(ci2) and int(getattr(ci2, 'cost', 0) or 0) >= int(cost_min or 0)):
                    continue
            if kind == 'COST_MEMBER_RANGE':
                cst = int(getattr(ci2, 'cost', 0) or 0)
                if not (_is_member_ci(ci2) and cst >= int(cost_min or 0) and cst <= int(cost_lim or 99)):
                    continue
            if group and not _ci_matches_group_or_unit(ci2, group):
                continue
            seen.add(canon2)
            cands.append(str(cn2 or ''))
    return cands

def _remove_from_yell_revealed_tracker(gs: GameState, cn: str) -> None:
    try:
        canon = _canon_cardno(str(cn or ''))
        pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
        for i, x in enumerate(list(pool)):
            if _canon_cardno(x) == canon:
                pool.pop(i)
                break
        setattr(gs, '_yell_revealed_this_live', pool)
    except Exception:
        pass


def _remove_one_from_zone_list(lst: Any, cn: str) -> bool:
    """Remove one matching card number from a mutable list-like zone."""
    try:
        canon = _canon_cardno(cn)
        for i, x in enumerate(list(lst or [])):
            if _canon_cardno(str(x or '')) == canon:
                try:
                    del lst[i]
                except Exception:
                    try:
                        lst.pop(i)
                    except Exception:
                        return False
                return True
    except Exception:
        return False
    return False


def _move_yell_revealed_to_green(gs: 'GameState', cn: str) -> bool:
    """Move one currently YELL-revealed card to green room and update logical trackers."""
    canon = _canon_cardno(cn)
    if not canon:
        return False
    removed = False
    try:
        removed = _remove_one_from_zone_list(gs.resolve_zone, canon) or removed
    except Exception:
        pass
    try:
        pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
        for i, x in enumerate(list(pool)):
            if _canon_cardno(str(x or '')) == canon:
                del pool[i]
                setattr(gs, '_yell_revealed_this_live', pool)
                removed = True
                break
    except Exception:
        pass
    if removed:
        try:
            gs.green_room.append(canon)
        except Exception:
            gs.green_room = [canon]
    return bool(removed)


def _perform_additional_yell(gs: 'GameState', rng: random.Random, cards_db: Dict[str, CardInfo], n: int, reason: str = '') -> List[str]:
    """Reveal n additional YELL cards, add draw icons, and queue any YELL-time autos."""
    n = max(0, int(n or 0))
    if n <= 0:
        return []
    revealed: List[str] = []
    for i in range(n):
        if not getattr(gs, 'deck', None):
            _rule_refresh_main_deck(gs, rng, reason=f'additional_yell@{i}')
        if not getattr(gs, 'deck', None):
            break
        revealed.append(gs.deck.pop(0))
    if not revealed:
        gs.log.append(f"[YELL+] additional yell 0 ({reason or 'no cards'})")
        return []
    try:
        gs.resolve_zone.extend(revealed)
    except Exception:
        gs.resolve_zone = list(revealed)
    try:
        pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
    except Exception:
        pool = []
    pool.extend(revealed)
    try:
        setattr(gs, '_yell_revealed_this_live', pool)
    except Exception:
        pass
    draw_n = 0
    for cn in revealed:
        c = _get_card(cards_db, cn)
        if c:
            draw_n += _count_draw_icons(c.blade_heart_tags_json)
    got = draw(gs, draw_n, rng) if draw_n > 0 else 0
    gs.log.append(f"[YELL+] revealed {len(revealed)} ({reason or 'additional'}, draw+{draw_n} -> drew {got})")
    try:
        _enqueue_yell_revealed_body_auto_triggers(gs, cards_db, revealed)
    except Exception as e:
        gs.log.append(f"[WARN] additional yell auto trigger enqueue failed: {e}")
    return revealed


def _yell_revealed_no_bladeheart_candidates(gs: 'GameState', cards_db: Dict[str, CardInfo], revealed: Optional[List[str]] = None, group: str = '', member_only: bool = False) -> List[str]:
    pool = list(revealed if revealed is not None else (getattr(gs, '_yell_revealed_this_live', []) or []))
    out: List[str] = []
    for cn in pool:
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if member_only and not _is_member_ci(ci):
            continue
        if group and not _ci_matches_group_or_unit(ci, group):
            continue
        try:
            has_bh = bool(_ci_blade_heart_raw_text(ci).strip()) and str(_ci_blade_heart_raw_text(ci)).strip() not in ('なし', '-', '0')
        except Exception:
            has_bh = False
        if has_bh:
            continue
        out.append(_canon_cardno(cn))
    return out

def _parse_energy_cost(cost_text: str) -> int:
    """Parse energy cost from cost_template.
    Supports:
      - Explicit counts like "<(E)> 3" or "[E]3"
      - Repeated icons like "<(E)><(E)><(E)>" (counts as 3)
    """
    t = (cost_text or "")
    total = 0
    # 1) explicit numeric forms
    for m in re.finditer(r"(?:<\(E\)>|\[E\]|Ｅ|E)\s*(\d+)", t):
        try:
            total += int(m.group(1))
        except Exception:
            pass
    # 2) icon repetition (each icon == 1), only if not already counted
    if total == 0:
        try:
            total += t.count("<(E)>")
        except Exception:
            pass
        try:
            total += len(re.findall(r"\[E\]", t))
        except Exception:
            pass
    return total
def _cost_requires_self_to_green(cost_text: str) -> bool:
    t = (cost_text or "")
    return ("このメンバー" in t) and ("控え室" in t) and ("置" in t)
def _cost_requires_self_wait(cost_text: str) -> bool:
    """Return True if cost requires this member to become WAIT (but NOT sent to green).
    Matches both 'ウェイトにする' and 'ウェイトにしてもよい' (optional cost).
    """
    t = str(cost_text or '').strip()
    if 'ウェイトにし' in t and 'このメンバー' in t:
        # Exclude self-to-green costs ("このメンバーをステージから控え室に置く")
        if '控え室' not in t and 'ステージから' not in t:
            return True
    return False
def _cost_requires_other_group_member_wait(cost_text: str) -> Dict[str, Any]:
    """Parse costs like:
    このメンバー以外の『虹ヶ咲』のメンバー1人をウェイト状態にする
    Returns {} when not matched.
    """
    t = _norm_digits_jp(str(cost_text or '').strip())
    m = re.search(r"^このメンバー以外の『(?P<group>[^』]+)』のメンバー\s*(?P<n>\d+)人をウェイト状態にする$", t)
    if not m:
        return {}
    try:
        n = int(m.group('n') or 0)
    except Exception:
        n = 0
    if n <= 0:
        return {}
    return {
        'group': str(m.group('group') or ''),
        'count': n,
        'exclude_self': True,
    }
def _other_group_member_wait_candidates(gs: 'GameState', cards_db: Dict[str, CardInfo], src_pos: str, group_name: str) -> List[str]:
    out: List[str] = []
    src_pos = str(src_pos or '').upper()
    gq = str(group_name or '')
    for pos in ('L', 'C', 'R'):
        if pos == src_pos:
            continue
        slot = (gs.stage or {}).get(pos)
        if not slot or not bool(getattr(slot, 'active', False)):
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci:
            continue
        if _is_live_ci(ci):
            continue
        if gq and gq not in str(getattr(ci, 'group', '') or ''):
            continue
        out.append(pos)
    return out
def _cost_requires_main_phase(cost_text: str) -> bool:
    t = str(cost_text or '').strip()
    return ('自分のメインフェイズ' in t) or ('メインフェイズの場合' in t)
def _current_live_set_limit(gs: 'GameState') -> int:
    try:
        return max(0, int(getattr(gs, 'live_set_limit', 3) or 3))
    except Exception:
        return 3
def _norm_digits_jp(s: str) -> str:
    if s is None:
        return ""
    t = str(s)
    # fullwidth digits -> ascii
    fw = "０１２３４５６７８９"
    for i,ch in enumerate(fw):
        t = t.replace(ch, str(i))
    return t
def _ability_usage_flags(ab: Dict[str, Any]) -> Dict[str, Any]:
    cond = _norm_digits_jp(str(ab.get('conditions', '') or ''))
    flags: Dict[str, Any] = {"once_per_turn": False, "turn_only": None}
    # <ターン1回> etc
    m = re.search(r"ターン\s*(\d+)\s*回", cond)
    if m:
        flags["once_per_turn"] = True
    # <ターン1のみ> etc (avoid matching ターン1回)
    m2 = re.search(r"ターン\s*(\d+)\s*(?:のみ|だけ)", cond)
    if m2:
        try:
            flags["turn_only"] = int(m2.group(1))
        except Exception:
            pass
    # If condition is like 'ターン1' alone (rare), treat as turn_only
    if flags["turn_only"] is None and ("ターン" in cond) and ("回" not in cond):
        m3 = re.search(r"ターン\s*(\d+)", cond)
        if m3:
            try:
                flags["turn_only"] = int(m3.group(1))
            except Exception:
                pass
    return flags
def _ability_key(ci: CardInfo, ab: Dict[str, Any], pos: str) -> str:
    cn = str(getattr(ci, 'cardnumber', '') or '')
    aid = str(ab.get('ability_id', '') or ab.get('ability_index', '') or '')
    return f"{pos}:{cn}:{aid}"
def _cost_move_active_energy_to_under(cost_text: str) -> bool:
    t = _norm_digits_jp(cost_text or '')
    # e.g. 自分のエネルギー置き場にあるエネルギー1枚をこのメンバーの下に置く
    if "エネルギー置き場" not in t:
        return False
    if "このメンバーの下" not in t:
        return False
    if "エネルギー" not in t:
        return False
    if "1枚" in t or "１枚" in t or re.search(r"\b1\b", t):
        return True
    # fallback: 'エネルギーカードを1枚' variants
    return bool(re.search(r"エネルギー.*?\d+枚.*?このメンバーの下", t))
def _cost_named_cards_to_deck_bottom(cost_text: str) -> Dict[str, Any]:
    """Parse cost like「園田海未」と「津島善子」と...合計N枚をシャッフルしてデッキの一番下に置く.
    Returns {'names': [...], 'total': N} or {} if not matched.
    """
    t = (cost_text or '')
    if 'デッキの一番下' not in t:
        return {}
    if 'シャッフル' not in t:
        return {}
    # extract 「名前」 patterns
    names = re.findall(r'「([^」]+)」', t)
    if not names:
        return {}
    # extract total count
    m = re.search(r'合計\s*(\d+)\s*枚', _norm_digits_jp(t))
    total = int(m.group(1)) if m else len(names)
    return {'names': names, 'total': total}
def _cost_green_members_to_deck_bottom_costsum(cost_text: str) -> Dict[str, Any]:
    """Parse optional cost: 控え室にあるメンバーカードN枚を好きな順番でデッキの一番下に置いてもよい.

    This is used by cards whose result depends on the total cost of the moved cards.
    Returns {'count': N} or {}.
    """
    t = _norm_digits_jp(cost_text or '')
    if '控え室' not in t or 'メンバーカード' not in t:
        return {}
    if 'デッキの一番下' not in t:
        return {}
    if '置いてもよい' not in t:
        return {}
    m = re.search(r'メンバーカード\s*(\d+)\s*枚', t)
    if not m:
        return {}
    return {'count': int(m.group(1))}

def _cost_hand_live_to_deck_bottom(cost_text: str) -> Dict[str, Any]:
    """Parse optional cost: 手札のライブカードをN枚公開し、デッキの一番下に置いてもよい."""
    t = _norm_digits_jp(cost_text or '')
    if '手札' not in t or 'デッキの一番下' not in t or '置いてもよい' not in t:
        return {}
    if 'ライブカード' not in t:
        return {}
    m = re.search(r'ライブカードを\s*(\d+)\s*枚', t)
    return {'kind': 'LIVE', 'count': int(m.group(1)) if m else 1}

def _cost_hand_group_card_optional_reveal(cost_text: str) -> Dict[str, Any]:
    """Parse optional cost: 手札の『G』のカードを1枚公開してもよい."""
    t = _norm_digits_jp(str(cost_text or '').strip())
    if '手札' not in t or '公開してもよい' not in t:
        return {}
    m = re.search(r"手札の『(?P<group>[^』]+)』のカードを(?P<n>\d+)?枚公開してもよい", t)
    if not m:
        return {}
    return {'kind': 'ANY', 'group': m.group('group'), 'count': int(m.group('n') or 1)}

def _move_all_green_members_to_deck_bottom_shuffled(gs: 'GameState', cards_db: Dict[str, CardInfo], rng: Optional[random.Random] = None) -> List[str]:
    """Move all own waiting-room MEMBER cards to deck bottom after shuffling.

    Returns the moved cardnumbers in the actual order appended to the deck.
    """
    members: List[str] = []
    rest: List[str] = []
    for cn in list(getattr(gs, 'green_room', []) or []):
        ci = _get_card(cards_db, cn)
        if ci and _is_member_ci(ci):
            members.append(cn)
        else:
            rest.append(cn)
    moved = list(members)
    try:
        (rng or random).shuffle(moved)
    except Exception:
        random.shuffle(moved)
    gs.green_room = rest
    try:
        gs.deck.extend(moved)
    except Exception:
        gs.deck = list(getattr(gs, 'deck', []) or []) + list(moved)
    return moved

def _stage_positions_by_member_name(gs: 'GameState', cards_db: Dict[str, CardInfo], name: str) -> List[str]:
    want = str(name or '').strip()
    out: List[str] = []
    if not want:
        return out
    for pos in ('L', 'C', 'R'):
        slot = (getattr(gs, 'stage', {}) or {}).get(pos)
        if not slot:
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci or not _is_member_ci(ci):
            continue
        nm = str(getattr(ci, 'name', '') or getattr(ci, 'cardname', '') or '')
        if want in nm:
            out.append(pos)
    return out

def _stage_distinct_named_members_from_list_count(gs: 'GameState', cards_db: Dict[str, CardInfo], names: List[str]) -> int:
    """Count how many distinct requested member names are currently represented on stage."""
    found: set = set()
    for nm0 in list(names or []):
        nm = str(nm0 or '').strip()
        if not nm:
            continue
        if _stage_positions_by_member_name(gs, cards_db, nm):
            found.add(nm)
    return int(len(found))

def _grant_stage_member_temp_blade(gs: 'GameState', cards_db: Dict[str, CardInfo], pos: str, blade_n: int, source_cn: str = '') -> bool:
    pos = str(pos or '').upper()
    slot = (getattr(gs, 'stage', {}) or {}).get(pos)
    if not slot:
        return False
    try:
        slot.temp_blade = int(getattr(slot, 'temp_blade', 0) or 0) + int(blade_n or 0)
        slot.temp_until = 'end_of_live'
    except Exception:
        return False
    gs.log.append(f'[AUTO] {source_cn}: stage {pos} temp blade +{int(blade_n or 0)} until end of live')
    return True

def _stage_group_member_positions(gs: 'GameState', cards_db: Dict[str, CardInfo], group_name: str) -> List[str]:
    group_name = str(group_name or '').strip()
    out: List[str] = []
    if not group_name:
        return out
    for ppos in ('L', 'C', 'R'):
        slot = (getattr(gs, 'stage', {}) or {}).get(ppos)
        if not slot:
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if ci and _is_member_ci(ci) and _ci_matches_group_or_unit(ci, group_name):
            out.append(ppos)
    return out


def _grant_stage_member_temp_cost(gs: 'GameState', cards_db: Dict[str, CardInfo], pos: str, cost_n: int, source_cn: str = '') -> bool:
    pos = str(pos or '').upper()
    slot = (getattr(gs, 'stage', {}) or {}).get(pos)
    if not slot:
        return False
    try:
        slot.temp_cost = int(getattr(slot, 'temp_cost', 0) or 0) + int(cost_n or 0)
        slot.temp_until = 'end_of_live'
    except Exception:
        return False
    gs.log.append(f'[AUTO] {source_cn}: stage {pos} temp cost +{int(cost_n or 0)} until end of live')
    return True


def _enqueue_stage_group_member_temp_cost(gs: 'GameState', cards_db: Dict[str, CardInfo], group_name: str, cost_n: int, source_cn: str = '') -> None:
    cands = _stage_group_member_positions(gs, cards_db, group_name)
    if not cands:
        gs.log.append(f'[SKIP] {source_cn}: no stage 『{group_name}』 member for temp cost +{int(cost_n or 0)}')
        return
    if len(cands) == 1:
        _grant_stage_member_temp_cost(gs, cards_db, cands[0], int(cost_n or 0), source_cn=source_cn)
        return
    gs.pending.append({
        'kind': 'choose_stage_member_for_temp_cost',
        'text': f'『{group_name}』のメンバー1人を選んで、ライブ終了時までコストを+{int(cost_n or 0)}します。',
        'options': list(cands),
        'candidates': list(cands),
        'cost_n': int(cost_n or 0),
        'source_cn': source_cn,
    })
    gs.log.append(f'[PENDING] {source_cn}: choose 『{group_name}』 member for temp cost +{int(cost_n or 0)}')

def _stage_group_cost_sum(gs: 'GameState', cards_db: Dict[str, CardInfo], group_name: str) -> int:
    """Return current/effective cost sum of own stage members matching group or unit."""
    total = 0
    group_name = str(group_name or '').strip()
    if not group_name:
        return 0
    for ppos in ('L', 'C', 'R'):
        slot = (getattr(gs, 'stage', {}) or {}).get(ppos)
        if not slot or not getattr(slot, 'cardnumber', ''):
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci or not _is_member_ci(ci):
            continue
        if not _ci_matches_group_or_unit(ci, group_name):
            continue
        try:
            total += int(_slot_effective_cost(gs, cards_db, ppos, slot) or 0)
        except Exception:
            try:
                total += int(getattr(ci, 'cost', 0) or 0)
            except Exception:
                pass
    return int(total)

def _enqueue_manual_stage_group_cost_sum_gt_opponent_then_icons(
    gs: 'GameState',
    cards_db: Dict[str, CardInfo],
    group_name: str,
    icons_blob: str,
    ctx: Optional[Dict[str, Any]] = None,
    source_cn: str = '',
) -> None:
    """Ask user to confirm opponent-comparison condition, then grant icons to source.

    Opponent stage is not modeled by this simulator, so the self total is shown and
    the opponent comparison is resolved with Apply/Skip.
    """
    ctx2 = dict(ctx or {})
    if source_cn and not ctx2.get('source_cn'):
        ctx2['source_cn'] = source_cn
    own_total = _stage_group_cost_sum(gs, cards_db, group_name)
    eff = f'ライブ終了時まで、{str(icons_blob or "")}を得る。'
    gs.pending.append({
        'kind': 'confirm_effect',
        'text': f'自分のステージにいる『{group_name}』のメンバーのコスト合計は {own_total} です。相手のステージにいるメンバーのコスト合計より高い場合、ライブ終了時まで {icons_blob} を得ます。条件を満たすなら Apply、満たさないなら Skip。',
        'options': ['apply', 'skip'],
        'after_effect_template': eff,
        'ctx': ctx2,
        'source_cn': source_cn,
    })
    gs.log.append(f'[PENDING] {source_cn}: manual stage cost-sum comparison for 『{group_name}』 own_total={own_total}; icons={icons_blob}')

def _base_member_cost(ci: Optional[CardInfo]) -> int:
    try:
        return int(getattr(ci, 'cost', 0) or 0)
    except Exception:
        return 0


def _grant_source_cost_equal_selected_original_minus_and_icon(
    gs: 'GameState',
    cards_db: Dict[str, CardInfo],
    source_pos: str,
    selected_pos: str,
    minus_n: int,
    threshold: int,
    icons_blob: str,
    source_cn: str = '',
) -> bool:
    """Make source member's cost equal selected member's printed/original cost minus N.

    Card text target: 「このメンバーのコストは、選んだメンバーが元々持つコストよりN低い値に等しくなる」.
    Implemented as a temporary cost delta on the source slot until end of live.
    """
    source_pos = str(source_pos or '').upper()
    selected_pos = str(selected_pos or '').upper()
    source_slot = (getattr(gs, 'stage', {}) or {}).get(source_pos)
    selected_slot = (getattr(gs, 'stage', {}) or {}).get(selected_pos)
    if not source_slot or not selected_slot:
        return False
    source_ci = _get_card(cards_db, getattr(source_slot, 'cardnumber', '') or '')
    selected_ci = _get_card(cards_db, getattr(selected_slot, 'cardnumber', '') or '')
    if not source_ci or not selected_ci or not _is_member_ci(source_ci) or not _is_member_ci(selected_ci):
        return False
    try:
        target_cost = int(_base_member_cost(selected_ci)) - int(minus_n or 0)
        source_base = int(_base_member_cost(source_ci))
        source_slot.temp_cost = int(target_cost) - int(source_base)
        source_slot.temp_until = 'end_of_live'
    except Exception:
        return False
    gs.log.append(f'[AUTO] {source_cn}: {source_pos} cost becomes {target_cost} (selected {selected_pos} original cost {int(_base_member_cost(selected_ci))} - {int(minus_n or 0)}) until end of live')
    try:
        if int(target_cost) >= int(threshold or 0):
            _grant_stage_member_temp_icons(gs, cards_db, source_pos, str(icons_blob or ''), source_cn=source_cn)
            gs.log.append(f'[AUTO] {source_cn}: cost threshold {target_cost}>={int(threshold or 0)} met -> {source_pos} gains {icons_blob}')
        else:
            gs.log.append(f'[AUTO] {source_cn}: cost threshold {target_cost}<{int(threshold or 0)} not met -> no icons')
    except Exception as e:
        gs.log.append(f'[WARN] {source_cn}: cost threshold icon grant failed: {e}')
    return True


def _enqueue_source_cost_equal_group_member_original_minus_and_icon(
    gs: 'GameState',
    cards_db: Dict[str, CardInfo],
    source_pos: str,
    group_name: str,
    minus_n: int,
    threshold: int,
    icons_blob: str,
    source_cn: str = '',
) -> None:
    source_pos = str(source_pos or '').upper()
    cands = _stage_group_member_positions(gs, cards_db, group_name)
    if not cands:
        gs.log.append(f'[SKIP] {source_cn}: no stage 『{group_name}』 member for cost-equal effect')
        return
    if len(cands) == 1:
        ok = _grant_source_cost_equal_selected_original_minus_and_icon(gs, cards_db, source_pos, cands[0], int(minus_n or 0), int(threshold or 0), str(icons_blob or ''), source_cn=source_cn)
        if not ok:
            gs.log.append(f'[ERR] {source_cn}: failed cost-equal effect source={source_pos} target={cands[0]}')
        return
    gs.pending.append({
        'kind': 'choose_stage_member_for_source_cost_equal_minus_icon',
        'text': f'『{group_name}』のメンバー1人を選び、このメンバーのコストを選んだメンバーの元々のコスト-{int(minus_n or 0)}にします。{int(threshold or 0)}以上なら{icons_blob}を得ます。',
        'options': list(cands),
        'candidates': list(cands),
        'source_pos': source_pos,
        'minus_n': int(minus_n or 0),
        'threshold': int(threshold or 0),
        'icons': str(icons_blob or ''),
        'source_cn': source_cn,
    })
    gs.log.append(f'[PENDING] {source_cn}: choose 『{group_name}』 member for source cost = original-{int(minus_n or 0)}; threshold {int(threshold or 0)} icons={icons_blob}')


def _resolve_mass_green_member_threshold_stage_blade(gs: 'GameState', cards_db: Dict[str, CardInfo], moved: List[str], threshold_group: str, threshold_n: int, target_name: str, blade_n: int, source_cn: str = '') -> None:
    group_n = 0
    for cn in list(moved or []):
        ci = _get_card(cards_db, cn)
        if ci and _ci_matches_group_or_unit(ci, threshold_group):
            group_n += 1
    if group_n < int(threshold_n or 0):
        gs.log.append(f'[AUTO] {source_cn}: mass bottom threshold not met ({threshold_group} {group_n}/{threshold_n})')
        return
    cands = _stage_positions_by_member_name(gs, cards_db, target_name)
    if not cands:
        gs.log.append(f'[AUTO] {source_cn}: threshold met but no stage member named {target_name}')
        return
    if len(cands) == 1:
        _grant_stage_member_temp_blade(gs, cards_db, cands[0], blade_n, source_cn=source_cn)
        return
    gs.pending.append({
        'kind': 'choose_stage_member_to_gain_blade',
        'text': f'「{target_name}」1人を選んで、ライブ終了時まで<(ブレード)>を{blade_n}つ得ます。',
        'options': list(cands),
        'candidates': list(cands),
        'blade_n': int(blade_n or 0),
        'source_cn': source_cn,
    })
    gs.log.append(f'[PENDING] {source_cn}: choose {target_name} to gain blade +{blade_n}')

def _apply_mass_bottom_threshold_followup(gs: 'GameState', cards_db: Dict[str, CardInfo], source_pos: str, source_cn: str, retrieve_n: int, blade_n: int) -> None:
    pos = str(source_pos or '').upper()
    if pos in ('L', 'C', 'R') and (getattr(gs, 'stage', {}) or {}).get(pos):
        _grant_stage_member_temp_blade(gs, cards_db, pos, blade_n, source_cn=source_cn)
    else:
        gs.log.append(f'[WARN] {source_cn}: threshold met but source stage position missing; blade +{blade_n} skipped')
    if int(retrieve_n or 0) > 0:
        cands = _green_candidates(gs, cards_db, 'LIVE')
        if cands:
            _enqueue_choose_from_green(gs, cards_db, kind='LIVE', n=int(retrieve_n or 1))
        else:
            gs.log.append(f'[INFO] {source_cn}: threshold met but no LIVE in waiting room to retrieve')

def _is_revealed_card_to_top_or_bottom_blade_effect(effect_text: str) -> bool:
    t = _normalize_icon_token_text(str(effect_text or '').strip()).replace('\n', '')
    return bool(re.match(r'^これにより公開したカードをデッキの一番上か一番下に置き、ライブ終了時まで、(?:<\(ブレード\)>)+を得る。$', t))

def _hand_candidates_by_kind(gs: 'GameState', cards_db: Dict[str, 'CardInfo'], kind: str = 'ANY', group: str = '') -> List[str]:
    kind = str(kind or 'ANY').upper()
    out: List[str] = []
    for cn in list(getattr(gs, 'hand', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if kind == 'LIVE' and not _is_live_ci(ci):
            continue
        if kind == 'MEMBER' and not _is_member_ci(ci):
            continue
        if group and not _ci_matches_group_or_unit(ci, group):
            continue
        out.append(cn)
    return out

def _green_candidates_for_kind(gs: 'GameState', cards_db: Dict[str, 'CardInfo'], kind: str = 'ANY', group: str = '') -> List[str]:
    kind = str(kind or 'ANY').upper()
    out: List[str] = []
    for cn in list(getattr(gs, 'green_room', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if kind == 'LIVE' and not _is_live_ci(ci):
            continue
        if kind == 'MEMBER' and not _is_member_ci(ci):
            continue
        if group and not _ci_matches_group_or_unit(ci, group):
            continue
        out.append(cn)
    return out

def _apply_bottom_costsum_result(gs: 'GameState', cards_db: Dict[str, 'CardInfo'], pos: str, source_cn: str, picked: List[str]) -> None:
    """Apply PL!N-bp3-009 style result after moving two green members to deck bottom."""
    pos = str(pos or '').upper()
    slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
    total = 0
    for cn in list(picked or []):
        ci = _get_card(cards_db, cn)
        try:
            total += int(getattr(ci, 'cost', 0) or 0) if ci else 0
        except Exception:
            pass
    if not picked:
        gs.log.append(f'[SKIP] {source_cn}: green member bottom cost skipped')
        return
    if total == 6:
        got = draw(gs, 1, random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0)))
        gs.log.append(f'[AUTO] {source_cn}: bottom cost total=6 -> draw {got}')
    elif total == 8:
        if slot:
            _grant_temp_heart(slot, 'all', 1)
            gs.log.append(f'[AUTO] {source_cn}: bottom cost total=8 -> {pos} gains <ALL> until end of live')
        else:
            gs.log.append(f'[WARN] {source_cn}: total=8 but source slot missing')
    elif total == 25:
        if slot:
            try:
                slot.temp_score = int(getattr(slot, 'temp_score', 0) or 0) + 1
                slot.temp_until = 'end_of_live'
            except Exception:
                pass
            gs.log.append(f'[AUTO] {source_cn}: bottom cost total=25 -> {pos} gains live total score +1 until end of live')
        else:
            gs.log.append(f'[WARN] {source_cn}: total=25 but source slot missing')
    else:
        gs.log.append(f'[AUTO] {source_cn}: bottom cost total={total} -> no matching result')
def can_activate_in_state(gs: 'GameState', cards_db: Dict[str, CardInfo], pos: str) -> bool:
    pos = str(pos or '').upper()
    if pos not in ('L','C','R'):
        return False
    slot = gs.stage.get(pos)
    if not slot:
        return False
    ci = _get_card(cards_db, slot.cardnumber)
    if not ci:
        return False
    # check activated abilities for supported clauses + satisfiable costs + conditions
    for ab in _iter_activated_abilities(ci):
        if not isinstance(ab, dict):
            continue
        flags = _ability_usage_flags(ab)
        key = _ability_key(ci, ab, pos)
        if flags.get("turn_only") is not None and int(gs.turn or 0) != int(flags["turn_only"]):
            continue
        if flags.get("once_per_turn"):
            used = int((getattr(gs, 'used_this_turn', {}) or {}).get(key, 0) or 0)
            if used >= 1:
                continue
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list) or not clauses:
            continue
        ok_any = False
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            cost = str(cl.get('cost_template', '') or '')
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            if not eff:
                continue
            # BODY起動効果（手札をすべて公開する）はeffect_templateが_EFFECT_RULESにないためスキップ
            is_body_cost = '手札をすべて公開する' in cost and str(ab.get('trigger', '') or '') == 'BODY'
            cond_thr = int(_activated_success_score_sum_condition(eff) or 0)
            eff_for_match = _strip_activated_success_score_sum_condition(eff) if cond_thr else eff
            eff_for_match = _strip_activated_success_count_discard_cost_reduction(eff_for_match)
            if cond_thr and not _success_score_sum_condition_met(gs, cards_db, cond_thr):
                continue
            if not is_body_cost and not (_match_effect_template(eff) or _match_effect_template(eff_for_match)):
                continue
            # energy cost check
            need_e = _parse_energy_cost(cost)
            if need_e > 0 and int(gs.energy_active or 0) < need_e:
                continue
            # special cost: move 1 energy from the energy zone under this member.
            # This is not an [E] payment, so either ACTIVE or WAIT energy can satisfy it.
            if _cost_move_active_energy_to_under(cost) and (int(gs.energy_active or 0) + int(gs.energy_wait or 0)) < 1:
                continue
            # named_cards_to_deck_bottom cost check: need enough matching cards in green room
            named_cost = _cost_named_cards_to_deck_bottom(cost)
            if named_cost:
                _names = named_cost['names']
                _total = named_cost['total']
                _cands = [gcn for gcn in (gs.green_room or [])
                          if any(n in str(getattr(_get_card(cards_db, gcn), 'name', '') or
                                         getattr(_get_card(cards_db, gcn), 'cardname', '') or gcn)
                                 for n in _names)]
                if len(_cands) < _total:
                    continue
            # self-wait cost check: member must currently be active
            if _cost_requires_self_wait(cost) and not slot.active:
                continue
            # cost: other same/target group member(s) become WAIT
            wait_other = _cost_requires_other_group_member_wait(cost)
            if wait_other:
                cands = _other_group_member_wait_candidates(gs, cards_db, pos, str(wait_other.get('group') or ''))
                if len(cands) < int(wait_other.get('count') or 0):
                    continue
            ok_any = True
        if ok_any:
            return True
    # legacy fallback (only when this card has no matchable activated ability templates)
    if not _has_matchable_activated(ci):
        if _has_green_live_take_ability(ci) or _has_green_member_take_ability(ci) or _has_sacrifice_ability(ci):
            return True
    return False
def _count_blade_icons_from_tagblob(s: str) -> int:
    t = str(s or "")
    return len(re.findall(r'<(?:\(ブレード\)|ブレード)>', t))
def _is_live_ci(ci: Optional[CardInfo]) -> bool:
    if not ci:
        return False
    t = str(getattr(ci, 'type', '') or '')
    if "LIVE" in t.upper() or "ライブ" in t:
        return True
    if "MEMBER" in t.upper() or "メンバー" in t:
        return False
    # Conservative fallback only for obviously LIVE-shaped rows.
    # Important: MEMBER rows in CardInfo often carry score=0 by default, so
    # score-is-not-None must NOT be treated as LIVE.
    try:
        req = getattr(ci, 'required_hearts', None)
        if isinstance(req, dict) and any(int(v or 0) > 0 for v in req.values()):
            return True
    except Exception:
        pass
    try:
        score = int(getattr(ci, 'score', 0) or 0)
    except Exception:
        score = 0
    try:
        cost = int(getattr(ci, 'cost', 0) or 0)
    except Exception:
        cost = 0
    try:
        blade = int(getattr(ci, 'blade', 0) or 0)
    except Exception:
        blade = 0
    try:
        base = getattr(ci, 'base_hearts', None)
        has_base = isinstance(base, dict) and any(int(v or 0) > 0 for v in base.values())
    except Exception:
        has_base = False
    if score > 0 and cost <= 0 and blade <= 0 and not has_base:
        return True
    return False
def _is_member_ci(ci: Optional[CardInfo]) -> bool:
    if not ci:
        return False
    return "MEMBER" in str(getattr(ci, 'type', '') or '').upper() or "メンバー" in str(getattr(ci, 'type', '') or '')
def _green_candidates(gs: 'GameState', cards_db: Dict[str, CardInfo], kind: str, group: str = "") -> List[str]:
    out = []
    for cn in list(gs.green_room):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if kind == 'LIVE' and not _is_live_ci(ci):
            continue
        if kind == 'MEMBER' and not _is_member_ci(ci):
            continue
        if group and (group not in str(getattr(ci, 'group', '') or '')):
            continue
        out.append(cn)
    return out
def _success_has_group(gs: 'GameState', cards_db: Dict[str, CardInfo], group: str) -> bool:
    group = str(group or '').strip()
    if not group:
        return False
    for cn in list(getattr(gs, 'success_zone', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if group in str(getattr(ci, 'group', '') or ''):
            return True
    return False
def _enqueue_discard_from_hand(gs: 'GameState', n: int, label: str = "") -> None:
    n = int(n or 0)
    if n <= 0:
        return
    if not gs.hand:
        gs.log.append('[ERR] discard: hand empty')
        return
    gs.pending.append({
        'kind': 'discard_from_hand',
        'remaining': n,
        'text': (label or f'手札を{n}枚控え室に置く'),
        'options': list(gs.hand),
    })
    gs.log.append(f'[PENDING] discard_from_hand remaining={n} hand={len(gs.hand)}')
def _auto_effect_detail_block(ctx: Optional[Dict[str, Any]], action_text: str = '') -> str:
    """Return a detailed text block for auto-effect choice popups.

    Selection popups created by automatic effects should show the source and
    resolved effect details, not just the resulting choice instruction.
    """
    try:
        ctx = dict(ctx or {})
    except Exception:
        ctx = {}
    detail = str(ctx.get('auto_effect_detail', '') or '').strip()
    action_text = str(action_text or '').strip()
    if detail and action_text:
        return f'{detail}\n\n処理：{action_text}'
    if detail:
        return detail
    src = str(ctx.get('source_cn', '') or '').strip()
    if src and action_text:
        return f'【{src}】自動効果\n処理：{action_text}'
    return action_text

def _with_auto_effect_detail(ctx: Optional[Dict[str, Any]], detail: str) -> Dict[str, Any]:
    out = dict(ctx or {})
    detail = str(detail or '').strip()
    if detail:
        out['auto_effect_detail'] = detail
    return out

def _auto_effect_detail_for_condition(ctx: Optional[Dict[str, Any]], effect_text: str, condition_text: str, timing: str = '自動効果') -> str:
    ctx0 = dict(ctx or {})
    src = str(ctx0.get('source_cn', '') or '').strip()
    head = f'【{src}】{timing}' if src else str(timing or '自動効果')
    lines = [head]
    cond = str(condition_text or '').strip()
    if cond:
        lines.append(f'条件：{cond}')
    eff = str(effect_text or '').strip()
    if eff:
        lines.append(f'効果：{eff}')
    return '\n'.join(lines)

def _enqueue_choose_from_green(gs: 'GameState', cards_db: Dict[str, CardInfo], kind: str, n: int = 1, group: str = "", ctx: Optional[Dict[str, Any]] = None, allow_less: bool = False, resume: Optional[Dict[str, Any]] = None) -> None:
    n = int(n or 1)
    cands = _green_candidates(gs, cards_db, kind=kind, group=group)
    if not cands:
        gs.log.append(f'[INFO] retrieve: no {kind} in waiting room' + (' (optional skip)' if allow_less else ''))
        if allow_less and resume:
            gs.pending.append(resume)
        return
    action_text = f'控え室の{("ライブ" if kind=="LIVE" else "メンバー")}カードを1枚手札に加える'
    if allow_less:
        action_text = f'控え室の{("ライブ" if kind=="LIVE" else "メンバー")}カードを1枚まで手札に加える'
    if group:
        action_text += f'（{group}）'
    auto_detail = str((ctx or {}).get('auto_effect_detail', '') or '').strip()
    prm = {
        'kind': f'choose_{kind.lower()}_from_green',
        'text': _auto_effect_detail_block(ctx, action_text),
        'options': cands,
        'want_kind': kind,
        'want_group': group,
        'remaining_picks': n,
        'source_cn': str((ctx or {}).get('source_cn', '') or ''),
        'auto_effect_detail': auto_detail,
        'suppress_card_text': bool(auto_detail),
        'allow_skip': bool(allow_less),
        'allow_less': bool(allow_less),
        'optional': bool(allow_less),
    }
    if resume:
        prm['_resume'] = resume
    gs.pending.append(prm)
    suffix = ' optional' if allow_less else ''
    if len(cands) == 1:
        gs.log.append(f'[PENDING] choose {kind} from waiting room (single candidate, confirm required{suffix})')
    else:
        gs.log.append(f'[PENDING] choose {kind} from waiting room ({len(cands)} candidates, picks={n}{suffix})')
def _grant_stage_member_temp_icons(gs: 'GameState', cards_db: Dict[str, CardInfo], pos: str, icons_blob: str, source_cn: str = '') -> bool:
    pos = str(pos or '').upper()
    slot = (getattr(gs, 'stage', {}) or {}).get(pos)
    if not slot:
        return False
    icons_blob = str(icons_blob or '')
    try:
        b = int(_count_blade_icons_from_tagblob(icons_blob) or 0)
    except Exception:
        b = 0
    if b > 0:
        slot.temp_blade = int(getattr(slot, 'temp_blade', 0) or 0) + b
        slot.temp_until = 'end_of_live'
    hearts = _parse_heart_icons(icons_blob)
    for col, cnt in hearts.items():
        _grant_temp_heart(slot, col, int(cnt or 0))
    try:
        if hearts:
            slot.temp_until = 'end_of_live'
    except Exception:
        pass
    gs.log.append(f'[AUTO] {source_cn}: stage {pos} temp icons {icons_blob} until end_of_live (blade+{b}, hearts={hearts})')
    return True

def _enqueue_stage_member_gain_icons(gs: 'GameState', cards_db: Dict[str, CardInfo], icons_blob: str, ctx: Optional[Dict[str, Any]] = None) -> None:
    opts = [p for p in ('L','C','R') if (getattr(gs, 'stage', {}) or {}).get(p)]
    src = str((ctx or {}).get('source_cn', '') or '')
    if not opts:
        gs.log.append(f'[INFO] {src}: no stage member to gain icons')
        return
    action_text = f'ステージのメンバー1人を選び、ライブ終了時まで{icons_blob}を得る'
    auto_detail = str((ctx or {}).get('auto_effect_detail', '') or '').strip()
    gs.pending.append({
        'kind': 'choose_stage_member_to_gain_icons',
        'text': _auto_effect_detail_block(ctx, action_text),
        'options': list(opts),
        'candidates': list(opts),
        'icons': str(icons_blob or ''),
        'source_cn': src,
        'auto_effect_detail': auto_detail,
        'suppress_card_text': bool(auto_detail),
    })
    gs.log.append(f'[PENDING] {src}: choose stage member to gain icons {icons_blob}')

def _enqueue_retrieve_live_and_member_upto1(gs: 'GameState', cards_db: Dict[str, CardInfo], ctx: Optional[Dict[str, Any]] = None) -> None:
    _enqueue_choose_from_green(gs, cards_db, kind='LIVE', n=1, ctx=ctx, allow_less=True)
    _enqueue_choose_from_green(gs, cards_db, kind='MEMBER', n=1, ctx=ctx, allow_less=True)

def _baton_new_member_condition(gs: 'GameState', cards_db: Dict[str, CardInfo], ctx: Optional[Dict[str, Any]], group: str, cost_min: int) -> Tuple[bool, int, str]:
    ctx = dict(ctx or {})
    new_cn = _canon_cardno(str(ctx.get('baton_new_cn', '') or ctx.get('baton_to_cn', '') or ''))
    new_pos = str(ctx.get('baton_new_pos', '') or ctx.get('pos', '') or '').upper()
    ci = _get_card(cards_db, new_cn)
    if not ci and new_pos in ('L','C','R'):
        slot = (getattr(gs, 'stage', {}) or {}).get(new_pos)
        if slot:
            new_cn = _canon_cardno(str(getattr(slot, 'cardnumber', '') or ''))
            ci = _get_card(cards_db, new_cn)
    if not ci or not _is_member_ci(ci):
        return False, 0, new_cn
    if group and not _ci_matches_group_or_unit(ci, group):
        return False, 0, new_cn
    if _ci_has_blade_heart_payload(ci):
        return False, 0, new_cn
    try:
        if new_pos in ('L','C','R') and (getattr(gs, 'stage', {}) or {}).get(new_pos):
            cost_val = int(_slot_effective_cost(gs, cards_db, new_pos, (getattr(gs, 'stage', {}) or {}).get(new_pos)) or 0)
        else:
            cost_val = int(getattr(ci, 'cost', 0) or 0)
    except Exception:
        try:
            cost_val = int(getattr(ci, 'cost', 0) or 0)
        except Exception:
            cost_val = 0
    return (cost_val >= int(cost_min or 0)), cost_val, new_cn

def _enqueue_topdeck_from_green(gs: 'GameState', cards_db: Dict[str, CardInfo], kind: str, n: int, group: str = '', allow_less: bool = False) -> None:
    kind = str(kind or '').upper()
    n = int(n or 0)
    group = str(group or '')
    if n <= 0:
        return
    # candidates from waiting room
    cands: List[str] = []
    for cn in list(gs.green_room):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if kind == 'LIVE' and not _is_live_ci(ci):
            continue
        if kind == 'MEMBER' and not _is_member_ci(ci):
            continue
        # ANY: no type filter
        if group and not _ci_matches_group_or_unit(ci, group):
            continue
        cands.append(cn)
    if not cands:
        gs.log.append(f'[INFO] topdeck: no {kind} candidates in waiting room')
        return
    if not allow_less:
        # if fewer than n available, just take all available (avoid deadlock)
        n = min(n, len(cands))
    opts = list(cands) + (['skip'] if allow_less else [])
    gs.pending.append({
        'kind': 'topdeck_from_green',
        'text': f'控え室の{kind}を{n}枚{("まで" if allow_less else "")}デッキ上に置く：1枚目=一番上。/ skipで終了' if allow_less else f'控え室の{kind}を{n}枚デッキ上（1枚目=一番上）',
        'options': opts,
        'remaining': n,
        'picked': [],
        'want_kind': kind,
        'want_group': group,
        'allow_less': bool(allow_less),
    })
    gs.log.append(f'[PENDING] topdeck_from_green: kind={kind} n={n} allow_less={allow_less} (cands={len(cands)})')
def _enqueue_bottomdeck_from_green(gs: 'GameState', cards_db: Dict[str, CardInfo], kind: str, n: int, group: str = '', allow_less: bool = True, after_draw_n: int = 0, source_cn: str = '') -> None:
    kind = str(kind or 'ANY').upper()
    n = int(n or 0)
    if n <= 0:
        return
    cands = _green_candidates_for_kind(gs, cards_db, kind=kind, group=group)
    if not cands:
        gs.log.append(f'[INFO] bottomdeck_from_green: no {kind} candidates in waiting room')
        return
    gs.pending.append({
        'kind': 'bottomdeck_from_green',
        'text': f'控え室の{kind}カードを{n}枚までデッキの一番下に置く',
        'options': (['skip'] + list(cands)) if allow_less else list(cands),
        'remaining': n,
        'picked': [],
        'want_kind': kind,
        'want_group': group,
        'allow_less': bool(allow_less),
        'allow_skip': bool(allow_less),
        'after_draw_n': int(after_draw_n or 0),
        'source_cn': str(source_cn or ''),
    })
    gs.log.append(f'[PENDING] bottomdeck_from_green: kind={kind} n={n} cands={len(cands)} allow_less={allow_less} after_draw={int(after_draw_n or 0)}')
def _enqueue_choose_player_green_to_bottom(gs: 'GameState', cards_db: Dict[str, CardInfo], kind: str, n: int, allow_less: bool = True, draw_after_n: int = 0, source_cn: str = '') -> None:
    """Choose self/opponent, then move that player's waiting-room cards to deck bottom.

    The current single-player simulator only has a concrete own waiting room/deck.
    Opponent selection is therefore represented as a manual-resolution popup.
    """
    kind = str(kind or 'ANY').upper()
    n = int(n or 0)
    if n <= 0:
        return
    jp = {'LIVE': 'ライブ', 'MEMBER': 'メンバー', 'ANY': '任意'}.get(kind, kind)
    draw_txt = f'。そうした場合、自分はカードを{int(draw_after_n or 0)}枚引く' if int(draw_after_n or 0) > 0 else ''
    gs.pending.append({
        'kind': 'choose_player_for_green_bottom',
        'text': f'自分か相手を選ぶ。選んだプレイヤーの控え室にある{jp}カードを{n}枚' + ('まで' if allow_less else '') + f'デッキの一番下に置く{draw_txt}',
        'options': ['self', 'opponent'],
        'want_kind': kind,
        'remaining': n,
        'allow_less': bool(allow_less),
        'draw_after_n': int(draw_after_n or 0),
        'source_cn': str(source_cn or ''),
    })
    gs.log.append(f'[PENDING] choose self/opponent green -> deck bottom: kind={kind} n={n} allow_less={allow_less} draw_after={int(draw_after_n or 0)}')
def _enqueue_choose_player_deck_top_action(gs: 'GameState', action: str, k: int = 1, source_cn: str = '') -> None:
    """Choose self/opponent, then apply a deck-top look/reorder action.

    Own deck actions are concrete in this single-player runtime. Opponent deck
    actions are represented as manual-resolution prompts because opponent deck
    state is not modeled.
    """
    action = str(action or '').strip()
    k = max(1, int(k or 1))
    if action == 'top1_optional_green':
        desc = 'そのプレイヤーのデッキの一番上のカードを見る。控え室に置いてもよい'
    elif action == 'topk_reorder_keep_any':
        desc = f'そのプレイヤーのデッキ上から{k}枚を見る。好きな枚数を好きな順番でデッキ上に置き、残りを控え室に置く'
    else:
        gs.log.append(f'[WARN] choose_player_deck_top_action: unsupported action={action}')
        return
    gs.pending.append({
        'kind': 'choose_player_for_deck_top_action',
        'text': f'自分か相手を選ぶ。選んだプレイヤーの{desc}。',
        'options': ['self', 'opponent'],
        'action': action,
        'k': k,
        'source_cn': str(source_cn or ''),
    })
    gs.log.append(f'[PENDING] choose self/opponent deck-top action: action={action} k={k}')

def _enqueue_hand_to_deck_top_or_bottom(gs: 'GameState', cards_db: Dict[str, CardInfo], kind: str = 'ANY', n: int = 1, group: str = '', after_gain_blade: int = 0, source_cn: str = '') -> None:
    kind = str(kind or 'ANY').upper()
    n = int(n or 0)
    if n <= 0:
        return
    cands = _hand_candidates_by_kind(gs, cards_db, kind=kind, group=group)
    if len(cands) < n:
        gs.log.append(f'[ERR] hand_to_deck_top_or_bottom: not enough {kind} cards in hand (need {n}, have {len(cands)})')
        return
    gs.pending.append({
        'kind': 'hand_to_deck_top_or_bottom',
        'text': f'手札の{kind}カードを{n}枚、デッキの一番上か一番下に置く',
        'options': list(cands),
        'remaining': n,
        'picked': [],
        'want_kind': kind,
        'want_group': group,
        'after_gain_blade': int(after_gain_blade or 0),
        'source_cn': str(source_cn or ''),
    })
    gs.log.append(f'[PENDING] hand_to_deck_top_or_bottom: kind={kind} group={group} n={n} cands={len(cands)}')

def _enqueue_hand_to_deck_bottom(gs: 'GameState', cards_db: Dict[str, CardInfo], kind: str, n: int, group: str = '', after_effect_template: str = '', after_ctx: Optional[Dict[str, Any]] = None, after_source_cn: str = '') -> None:
    kind = str(kind or 'ANY').upper()
    n = int(n or 0)
    if n <= 0:
        return
    cands = _hand_candidates_by_kind(gs, cards_db, kind=kind, group=group)
    if len(cands) < n:
        gs.log.append(f'[ERR] hand_to_deck_bottom: not enough {kind} cards in hand (need {n}, have {len(cands)})')
        return
    gs.pending.append({
        'kind': 'hand_to_deck_bottom',
        'text': f'手札の{kind}カードを{n}枚デッキの一番下に置く',
        'options': list(cands),
        'remaining': n,
        'picked': [],
        'want_kind': kind,
        'want_group': group,
        'after_effect_template': after_effect_template,
        'after_ctx': dict(after_ctx or {}),
        'after_source_cn': after_source_cn,
    })
    gs.log.append(f'[PENDING] hand_to_deck_bottom: kind={kind} n={n} cands={len(cands)}')
def _enqueue_choose_from_topk(gs: 'GameState', k: int, rng: Optional[random.Random] = None) -> None:
    k = int(k or 0)
    if k <= 0:
        return
    _rule_refresh_for_top_access(gs, rng, k, reason='look_top')
    if not gs.deck:
        gs.log.append('[INFO] look_top: deck empty')
        return
    pool = []
    for _ in range(min(k, len(gs.deck))):
        pool.append(gs.deck.pop(0))
    if len(pool) == 1:
        pick = pool[0]
        gs.hand.append(pick)
        gs.log.append(f'[AUTO] look_top: only 1 -> hand {pick}')
        return
    gs.pending.append({
        'kind': 'choose_from_topk',
        'text': f'デッキ上から{len(pool)}枚を見る：その中から1枚を手札に加え、残りを控え室に置く',
        'options': list(pool),
        'pool': list(pool),
        'display_cards': list(pool),
    })
    gs.log.append(f'[PENDING] choose 1 from top {len(pool)} (rest -> waiting room)')
def _enqueue_choose_from_topk_filtered(
    gs: 'GameState', k: int, rng: Optional[random.Random],
    cards_db: Dict[str, 'CardInfo'],
    filter_kind: str = '',   # 'LIVE' or 'MEMBER' or ''
    filter_group: str = '',  # group name or ''
    filter_names: List[str] = None,  # card name list or []
    optional: bool = False,
    cost_min: int = 0,
    cost_max: int = 0,
    required_total_min: int = 0,
    member_heart_color: str = '',
    member_heart_min: int = 0,
    member_heart_colors_any: List[str] = None,
    live_req_color: str = '',
    live_req_min: int = 0,
    filter_mode: str = '',
) -> None:
    """Look at top-k cards, let user pick 1 matching filter (optionally), rest to green."""
    filter_names = filter_names or []
    member_heart_colors_any = member_heart_colors_any or []
    k = int(k or 0)
    if k <= 0:
        return
    _rule_refresh_for_top_access(gs, rng, k, reason='look_top_filtered')
    if not gs.deck:
        gs.log.append('[INFO] look_top_filtered: deck empty')
        return
    pool = [gs.deck.pop(0) for _ in range(min(k, len(gs.deck)))]
    # determine which cards satisfy the filter
    def _matches(cn: str) -> bool:
        ci = _get_card(cards_db, cn)
        if not ci:
            return False
        mode = str(filter_mode or '').strip()
        if mode == 'member_heart_or_live_req':
            if _is_member_ci(ci):
                return bool(member_heart_color and _ci_member_heart_count(ci, member_heart_color) >= int(member_heart_min or 1))
            if _is_live_ci(ci):
                return bool(live_req_color and _ci_live_required_heart_count(ci, live_req_color) >= int(live_req_min or 1))
            return False
        if filter_kind:
            if filter_kind == 'LIVE' and not _is_live_ci(ci):
                return False
            if filter_kind == 'MEMBER' and not _is_member_ci(ci):
                return False
        if filter_group:
            if str(filter_group).strip() not in str(getattr(ci, 'group', '') or ''):
                return False
        if filter_names:
            name = str(getattr(ci, 'name', '') or getattr(ci, 'cardname', '') or cn)
            if not any(n in name for n in filter_names):
                return False
        if cost_min or cost_max:
            try:
                cost_val = int(getattr(ci, 'cost', 0) or 0)
            except Exception:
                cost_val = 0
            if cost_min and cost_val < int(cost_min):
                return False
            if cost_max and cost_val > int(cost_max):
                return False
        if required_total_min:
            if not _is_live_ci(ci):
                return False
            if _ci_live_required_total(ci) < int(required_total_min):
                return False
        if member_heart_colors_any:
            if not _is_member_ci(ci):
                return False
            if not any(_ci_member_heart_count(ci, col) > 0 for col in member_heart_colors_any):
                return False
        if member_heart_color and not mode:
            if not _is_member_ci(ci):
                return False
            if _ci_member_heart_count(ci, member_heart_color) < int(member_heart_min or 1):
                return False
        if live_req_color and not mode:
            if not _is_live_ci(ci):
                return False
            if _ci_live_required_heart_count(ci, live_req_color) < int(live_req_min or 1):
                return False
        return True
    candidates = [cn for cn in pool if _matches(cn)]
    label_parts = []
    if cost_min and cost_max:
        label_parts.append(f'コスト{cost_min}〜{cost_max}')
    elif cost_min:
        label_parts.append(f'コスト{cost_min}以上')
    elif cost_max:
        label_parts.append(f'コスト{cost_max}以下')
    if required_total_min:
        label_parts.append(f'必要ハート合計{required_total_min}以上')
    if filter_group:
        label_parts.append(f'『{str(filter_group).strip()}』')
    if filter_names:
        label_parts.append('・'.join(f'「{n}」' for n in filter_names))
    if member_heart_colors_any:
        label_parts.append('ハート' + '/'.join(member_heart_colors_any))
    if member_heart_color and not filter_mode:
        label_parts.append(f'{member_heart_color}ハート{int(member_heart_min or 1)}以上')
    if live_req_color and not filter_mode:
        label_parts.append(f'必要{live_req_color}{int(live_req_min or 1)}以上')
    if filter_mode == 'member_heart_or_live_req':
        label_parts.append(f'メンバー{member_heart_color}{int(member_heart_min or 1)}以上/ライブ必要{live_req_color}{int(live_req_min or 1)}以上')
    if filter_kind:
        label_parts.append({'LIVE': 'ライブカード', 'MEMBER': 'メンバーカード'}.get(filter_kind, filter_kind))
    label = '・'.join(label_parts) if label_parts else 'カード'
    if not candidates:
        # Show pool as popup even when no match; user confirms to send all to green
        gs.pending.append({
            'kind': 'view_topk_no_match',
            'text': f'デッキ上{len(pool)}枚を公開（{label}なし）→ 全て控え室へ',
            'options': ['確認'],
            'pool': list(pool),
            'display_cards': list(pool),
        })
        gs.log.append(f'[PENDING] look_top_filtered: no match, showing pool={pool} for confirmation')
        return
    if not optional and len(candidates) == 1:
        pick = candidates[0]
        rest = [c for c in pool if c != pick]
        gs.hand.append(pick)
        gs.green_room.extend(rest)
        gs.log.append(f'[AUTO] look_top_filtered: only match {pick} -> hand; {len(rest)} -> waiting room')
        return
    suffix = '（スキップ可）' if optional else ''
    opts = list(candidates)
    if optional:
        opts.append('skip')
    gs.pending.append({
        'kind': 'choose_from_topk',
        'text': f'デッキ上{len(pool)}枚から{label}を1枚手札へ{suffix}',
        'options': opts,
        'pool': list(pool),
        'display_cards': list(pool),
        'display_pool_all': list(pool),
        'candidates': list(candidates),
        'optional': optional,
    })
    gs.log.append(f'[PENDING] look_top_filtered: pool={len(pool)} candidates={len(candidates)} optional={optional}')
def _enqueue_look_top_3way_split(
    gs: 'GameState', k: int, rng: Optional[random.Random],
) -> None:
    """Look at k cards, user places 1->hand, 1->deck top, 1->green."""
    k = int(k or 0)
    if k <= 0:
        return
    _rule_refresh_for_top_access(gs, rng, k, reason='look_top_3way')
    if not gs.deck:
        gs.log.append('[INFO] look_top_3way: deck empty')
        return
    pool = [gs.deck.pop(0) for _ in range(min(k, len(gs.deck)))]
    if len(pool) < 3:
        # not enough cards: put all to hand (graceful fallback)
        gs.hand.extend(pool)
        gs.log.append(f'[AUTO] look_top_3way: only {len(pool)} cards -> all to hand')
        return
    gs.pending.append({
        'kind': 'look_top_3way_step',
        'text': f'デッキ上{len(pool)}枚から1枚を手札へ、1枚をデッキ上へ、1枚を控え室へ（順に選択）',
        'options': list(pool),
        'pool': list(pool),
        'display_cards': list(pool),
        'step': 'hand',   # hand -> topdeck -> green (auto)
        'picked_hand': '',
        'picked_top': '',
    })
    gs.log.append(f'[PENDING] look_top_3way: pool={pool}')
def _enqueue_reorder_from_topk_keep_any(gs: 'GameState', k: int, rng: Optional[random.Random] = None) -> None:
    k = int(k or 0)
    if k <= 0:
        return
    _rule_refresh_for_top_access(gs, rng, k, reason='look_top_reorder')
    if not gs.deck:
        gs.log.append('[INFO] look_top_reorder: deck empty')
        return
    pool: List[str] = []
    for _ in range(min(k, len(gs.deck))):
        pool.append(gs.deck.pop(0))
    if not pool:
        return
    # Prompt user to pick cards to keep on top in order; 'skip' ends early.
    opts = list(pool) + ['skip']
    gs.pending.append({
        'kind': 'reorder_topk_keep_any',
        'text': f'デッキ上から{len(pool)}枚を見る：好きな枚数を好きな順番でデッキ上に置く（1枚目=一番上）。残りは控え室。/ skipで終了',
        'options': opts,
        'pool': list(pool),
        'kept': [],
        'allow_less': True,
    })
    gs.log.append(f'[PENDING] reorder top {len(pool)} keep-any (rest -> waiting room)')
def _apply_effect_by_rule(gs: 'GameState', rng: random.Random, cards_db: Dict[str, CardInfo], rule: Dict[str, Any], gd: Dict[str, str], ctx: Dict[str, Any]) -> None:
    # Extension hook: try lightweight effect layer first. This lets day-to-day
    # effect implementation happen in engine_effect.py without forcing Claude to
    # ingest the full runtime file every time.
    try:
        from . import engine_effect as _engine_effect
        handled = _engine_effect.try_apply_effect_by_rule_ext(globals(), gs, rng, cards_db, rule, gd, ctx)
        if handled:
            return
    except Exception:
        pass
    op = rule.get('op')
    if op == 'draw':
        n = int(gd.get('n', 0) or 0)
        got = draw(gs, n, rng)
        gs.log.append(f'[AUTO] draw {n} -> drew {got}')
        return
    if op == 'draw_then_gain_icons_until_end_live':
        n = int(gd.get('n', 0) or 0)
        icons_blob = str(gd.get('icons', '') or '')
        got = draw(gs, n, rng)
        pos = str(ctx.get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
        if not slot:
            gs.log.append('[WARN] draw_then_gain_icons: no source slot')
            return
        b = _count_blade_icons_from_tagblob(icons_blob)
        if b > 0:
            slot.temp_blade += b
            slot.temp_until = 'end_of_live'
        heart_counts = _parse_heart_icons(icons_blob)
        for col, cnt in heart_counts.items():
            _grant_temp_heart(slot, col, cnt)
        gs.log.append(f'[AUTO] draw {n} -> drew {got}; {pos}: gain icons {icons_blob} (until end_of_live; blades={b} hearts={heart_counts})')
        return
    if op == 'draw_then_stage_group_member_temp_cost':
        draw_n = int(gd.get('draw_n', 0) or 0)
        group_name = str(gd.get('group', '') or '').strip()
        cost_n = int(gd.get('cost_n', 0) or 0)
        got = draw(gs, draw_n, rng)
        src = str((ctx or {}).get('source_cn', '') or '')
        gs.log.append(f'[AUTO] draw {draw_n} -> drew {got}; then choose 『{group_name}』 member cost +{cost_n}')
        _enqueue_stage_group_member_temp_cost(gs, cards_db, group_name, cost_n, source_cn=src)
        return
    if op == 'stage_group_member_cost_equal_original_minus_self_gain_icon_if_gte':
        group_name = str(gd.get('group', '') or '').strip()
        minus_n = int(gd.get('minus_n', 0) or 0)
        threshold = int(gd.get('threshold', 0) or 0)
        icons_blob = str(gd.get('icons', '') or '')
        src = str((ctx or {}).get('source_cn', '') or '')
        source_pos = str((ctx or {}).get('pos', '') or '').upper()
        _enqueue_source_cost_equal_group_member_original_minus_and_icon(
            gs, cards_db, source_pos, group_name, minus_n, threshold, icons_blob, source_cn=src
        )
        return
    if op == 'self_temp_cost_then_stage_group_cost_sum_gt_opponent_gain_icons':
        cost_n = int(gd.get('cost_n', 0) or 0)
        group_name = str(gd.get('group', '') or '').strip()
        icons_blob = str(gd.get('icons', '') or '')
        src = str((ctx or {}).get('source_cn', '') or '')
        source_pos = str((ctx or {}).get('pos', '') or '').upper()
        if source_pos not in ('L', 'C', 'R'):
            gs.log.append(f'[WARN] {src}: source position missing for self temp cost +{cost_n}')
            return
        ok = _grant_stage_member_temp_cost(gs, cards_db, source_pos, cost_n, source_cn=src)
        if not ok:
            gs.log.append(f'[WARN] {src}: failed to apply self temp cost +{cost_n}')
            return
        _enqueue_manual_stage_group_cost_sum_gt_opponent_then_icons(gs, cards_db, group_name, icons_blob, ctx=ctx, source_cn=src)
        return
    if op == 'draw_then_discard':
        n = int(gd.get('n', 0) or 0)
        m = int(gd.get('m', 0) or 0)
        got = draw(gs, n, rng)
        gs.log.append(f'[AUTO] draw {n} -> drew {got}; then discard {m}')
        _enqueue_discard_from_hand(gs, m)
        return
    if op == 'discard_from_hand':
        n = int(gd.get('n', 0) or 0)
        _enqueue_discard_from_hand(gs, n)
        return
    if op == 'retrieve_from_waiting_room':
        kind = str(rule.get('card_kind', '') or '').upper() or 'ANY'
        n = int(gd.get('n', 1) or 1)
        group = str(gd.get('group', '') or '')
        if kind not in ('LIVE','MEMBER'):
            gs.log.append('[WARN] retrieve: unsupported kind')
            return
        _enqueue_choose_from_green(gs, cards_db, kind=kind, n=n, group=group, ctx=ctx)
        return
    if op == 'optional_discard_one_from_hand_then_effect':
        after = str(gd.get('after', '') or '').strip()
        src = str((ctx or {}).get('source_cn', '') or '')
        detail = _auto_effect_detail_for_condition(ctx, '手札を1枚控え室に置いてもよい。そうした場合、' + after, 'このメンバーがステージから控え室に置かれたとき', timing='ステージ離脱時')
        ctx2 = _with_auto_effect_detail(ctx, detail)
        # Optional costs should open the actual cost-payment picker directly.
        # Choosing no card is represented by the Skip button; paying the cost continues
        # to the after_effect_template. This avoids an extra confirmation modal with no
        # actionable choices.
        gs.pending.append({
            'kind': 'discard_from_hand',
            'remaining': 1,
            'text': _auto_effect_detail_block(ctx2, 'コストとして控え室に置く手札を1枚選ぶ。支払わない場合はスキップ。'),
            'options': list(gs.hand),
            'after_effect_template': after,
            'after_ctx': ctx2,
            'after_source_cn': src,
            'auto_effect_detail': detail,
            'suppress_card_text': True,
            'allow_skip': True,
            'optional': True,
            'skip_reason': 'optional hand discard stage-leave cost',
        })
        gs.log.append(f'[PENDING] {src}: optional hand discard cost picker then stage-leave followup')
        return
    if op == 'retrieve_waiting_live_and_member_upto1':
        _enqueue_retrieve_live_and_member_upto1(gs, cards_db, ctx=ctx)
        return
    if op == 'stage_member_gain_icons_until_end_live':
        _enqueue_stage_member_gain_icons(gs, cards_db, str(gd.get('icons', '') or ''), ctx=ctx)
        return
    if op == 'leave_baton_no_bladeheart_nijigasaki_energy_draw':
        group1 = str(gd.get('group1', '') or '')
        group2 = str(gd.get('group2', '') or group1)
        c1 = int(gd.get('cost1', 0) or 0)
        c2 = int(gd.get('cost2', 0) or 0)
        energy_n = int(gd.get('energy_n', 0) or 0)
        draw_n = int(gd.get('draw_n', 0) or 0)
        ok1, actual_cost, new_cn = _baton_new_member_condition(gs, cards_db, ctx, group1, c1)
        src = str((ctx or {}).get('source_cn', '') or '')
        if not ok1:
            gs.log.append(f'[SKIP] {src}: baton target {new_cn or "?"} cost={actual_cost} does not meet no-bladeheart {group1} cost>={c1}')
            return
        take = min(max(0, energy_n), int(gs.energy_wait or 0))
        gs.energy_wait -= take
        gs.energy_active += take
        gs.log.append(f'[AUTO] {src}: baton target {new_cn} cost={actual_cost} no-bladeheart {group1} >= {c1} -> energy activate {energy_n} (moved {take})')
        ok2, _, _ = _baton_new_member_condition(gs, cards_db, ctx, group2, c2)
        if ok2 and draw_n > 0:
            got = draw(gs, draw_n, rng)
            gs.log.append(f'[AUTO] {src}: baton target {new_cn} cost={actual_cost} >= {c2} -> draw {draw_n} (drew {got})')
        return
    if op == 'topdeck_from_green':
        kind = str(rule.get('card_kind', '') or '').upper() or 'ANY'
        n = int(gd.get('n', 1) or 1)
        group = str(gd.get('group', '') or '')
        allow_less = bool(rule.get('allow_less', False))
        if kind not in ('LIVE','MEMBER','ANY'):
            gs.log.append('[WARN] topdeck: unsupported kind')
            return
        _enqueue_topdeck_from_green(gs, cards_db, kind=kind, n=n, group=group, allow_less=allow_less)
        return
    if op == 'topdeck_green_live_group_upto1_then_draw_if_opponent_wait_exists':
        group = str(gd.get('group', '') or '')
        src = str((ctx or {}).get('source_cn', '') or '')
        _enqueue_topdeck_from_green(gs, cards_db, kind='LIVE', n=1, group=group, allow_less=True)
        gs.pending.append({
            'kind': 'confirm_effect',
            'text': f'【{src or "この能力"}】相手のステージにウェイト状態のメンバーがいる場合、カードを1枚引きます。条件を満たすなら Apply、満たさないなら Skip。',
            'options': ['apply', 'skip'],
            'after_effect_template': 'カードを1枚引く。',
            'ctx': dict(ctx or {}),
            'source_cn': src,
        })
        gs.log.append(f'[PENDING] {src}: topdeck 『{group}』 live up to1, then manual opponent-wait draw check')
        return
    if op == 'bottomdeck_from_green':
        kind_jp = str(gd.get('kind', '') or '')
        kind = {'ライブ': 'LIVE', 'メンバー': 'MEMBER'}.get(kind_jp, str(rule.get('card_kind', '') or '').upper() or 'ANY')
        n = int(gd.get('n', 1) or 1)
        group = str(gd.get('group', '') or '')
        _enqueue_bottomdeck_from_green(gs, cards_db, kind=kind, n=n, group=group, allow_less=bool(rule.get('allow_less', True)))
        return
    if op == 'choose_player_green_to_bottom':
        kind = str(rule.get('card_kind', '') or '').upper() or 'ANY'
        n = int(gd.get('n', 1) or 1)
        draw_n = int(gd.get('draw_n', 0) or 0) if bool(rule.get('draw_if_moved', False)) else 0
        _enqueue_choose_player_green_to_bottom(
            gs, cards_db, kind=kind, n=n,
            allow_less=bool(rule.get('allow_less', False)),
            draw_after_n=draw_n,
            source_cn=str((ctx or {}).get('source_cn', '') or ''),
        )
        return
    if op == 'choose_player_deck_top_action':
        action = str(rule.get('action', '') or '')
        k = int(gd.get('k', 1) or 1)
        _enqueue_choose_player_deck_top_action(gs, action=action, k=k, source_cn=str((ctx or {}).get('source_cn', '') or ''))
        return
    if op == 'bottom_all_green_members_optional_group_threshold_stage_named_blade':
        source_cn = str((ctx or {}).get('source_cn', '') or '')
        gs.pending.append({
            'kind': 'confirm_mass_green_members_to_bottom',
            'text': '自分の控え室にあるすべてのメンバーカードをシャッフルし、デッキの下に置きますか？',
            'options': ['apply', 'skip'],
            'threshold_group': str(gd.get('threshold_group', '') or ''),
            'threshold_n': int(gd.get('threshold_n', 0) or 0),
            'target_name': str(gd.get('target_name', '') or ''),
            'blade_n': _count_blade_icons_from_tagblob(str(gd.get('blades', '') or '')),
            'source_cn': source_cn,
        })
        gs.log.append(f'[PENDING] {source_cn}: optional mass bottom all own MEMBER cards')
        return
    if op == 'both_players_bottom_all_green_members_threshold_retrieve_live_gain_blade':
        source_cn = str((ctx or {}).get('source_cn', '') or '')
        source_pos = str((ctx or {}).get('pos', '') or '').upper()
        moved = _move_all_green_members_to_deck_bottom_shuffled(gs, cards_db, rng)
        own_n = len(moved)
        threshold_n = int(gd.get('threshold_n', 0) or 0)
        retrieve_n = int(gd.get('retrieve_n', 1) or 1)
        blade_n = _count_blade_icons_from_tagblob(str(gd.get('blades', '') or ''))
        gs.log.append(f'[AUTO] {source_cn}: own waiting-room MEMBER all -> deck bottom shuffled ({own_n}); opponent does same manually')
        if own_n >= threshold_n:
            gs.pending.append({
                'kind': 'mass_bottom_auto_ack',
                'text': (
                    f'{source_cn} の自動効果を確認してください。\n'
                    f'自分の控え室からメンバーカード{own_n}枚をシャッフルしてデッキ下に戻しました。\n'
                    f'相手も同様に自身の控え室のメンバーカードをデッキ下に戻します。\n'
                    f'条件確認：自分側 {own_n}枚 / 必要 {threshold_n}枚。\n'
                    f'自分側だけで条件を満たしています。確認後、ライブカード回収とブレード+{blade_n}を処理します。'
                ),
                'options': ['ok'],
                'own_moved_n': own_n,
                'threshold_n': threshold_n,
                'retrieve_n': retrieve_n,
                'blade_n': blade_n,
                'source_pos': source_pos,
                'source_cn': source_cn,
            })
            gs.log.append(f'[PENDING] {source_cn}: mass bottom auto confirmation own={own_n}/{threshold_n}')
        else:
            need_opponent = max(0, int(threshold_n or 0) - int(own_n or 0))
            gs.pending.append({
                'kind': 'manual_opponent_mass_bottom_threshold',
                'text': f'【相手への効果】自分は控え室のメンバーカード{own_n}枚をシャッフルしてデッキ下に戻しました。相手も自身の控え室にあるすべてのメンバーカードをシャッフルし、相手のデッキの下に置きます。合計{threshold_n}枚以上、つまり相手側で少なくとも{need_opponent}枚以上戻った場合は「条件達成」を押してください。',
                'options': ['threshold_met', 'threshold_not_met'],
                'own_moved_n': own_n,
                'threshold_n': threshold_n,
                'retrieve_n': retrieve_n,
                'blade_n': blade_n,
                'source_pos': source_pos,
                'source_cn': source_cn,
            })
            gs.log.append(f'[PENDING] {source_cn}: manual opponent mass bottom threshold check own={own_n}/{threshold_n}')
        return
    if op == 'draw_then_hand_to_deck_bottom':
        draw_n = int(gd.get('draw_n', 0) or 0)
        bottom_n = int(gd.get('bottom_n', 1) or 1)
        got = draw(gs, draw_n, rng)
        gs.log.append(f'[AUTO] draw_then_hand_to_deck_bottom: drew {got}; choose {bottom_n} from hand -> deck bottom')
        _enqueue_hand_to_deck_bottom(gs, cards_db, kind='ANY', n=bottom_n, after_source_cn=str((ctx or {}).get('source_cn', '') or ''))
        return
    if op == 'draw_then_hand_to_deck_top_or_bottom':
        draw_n = int(gd.get('draw_n', 0) or 0)
        n = int(gd.get('n', 1) or 1)
        got = draw(gs, draw_n, rng)
        gs.log.append(f'[AUTO] draw_then_hand_to_deck_top_or_bottom: drew {got}; choose {n} from hand -> deck top/bottom')
        _enqueue_hand_to_deck_top_or_bottom(gs, cards_db, kind='ANY', n=n, source_cn=str((ctx or {}).get('source_cn', '') or ''))
        return
    if op == 'score_draw_then_hand_top_or_bottom_if_all_stage_group':
        group = str(gd.get('group', '') or '')
        if not _stage_all_members_are_group(gs, cards_db, group):
            gs.log.append(f'[AUTO] score/draw/top-or-bottom: condition not met (all stage members are {group})')
            return
        score_n = int(gd.get('score_n', 0) or 0)
        src_cn = str((ctx or {}).get('source_cn', '') or '')
        if score_n:
            _add_live_start_score_bonus(gs, score_n, source_cn=src_cn)
            gs.log.append(f'[AUTO] {src_cn}: all stage {group} -> live score +{score_n}')
        draw_n = int(gd.get('draw_n', 0) or 0)
        n = int(gd.get('n', 1) or 1)
        got = draw(gs, draw_n, rng)
        gs.log.append(f'[AUTO] {src_cn}: drew {got}; choose {n} hand card -> deck top/bottom')
        _enqueue_hand_to_deck_top_or_bottom(gs, cards_db, kind='ANY', n=n, source_cn=src_cn)
        return
    if op == 'live_zone_group_only_required_color_sum_gain_all':
        group = str(gd.get('group', '') or '')
        color_icons = str(gd.get('icons', '') or '')
        colors = _heart_icons_to_colors(color_icons)
        threshold = int(gd.get('threshold', 0) or 0)
        all_n = len(re.findall(r'<\(ALL\)>', str(gd.get('all_icons', '') or '')))
        pos = str((ctx or {}).get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
        ok_group, total, live_n = _live_zone_group_only_required_color_sum(gs, cards_db, group, colors)
        src_cn = str((ctx or {}).get('source_cn', '') or '')
        if not ok_group:
            gs.log.append(f'[SKIP] {src_cn}: live storage group-only condition not met ({group}, LIVE={live_n})')
            return
        if total < threshold:
            gs.log.append(f'[SKIP] {src_cn}: live storage required hearts {total}/{threshold} for {colors}')
            return
        if not slot:
            gs.log.append(f'[WARN] {src_cn}: live storage required-heart bonus skipped (source slot not found)')
            return
        if all_n > 0:
            _grant_temp_heart(slot, 'all', all_n)
        gs.log.append(f'[AUTO] {src_cn}: live storage all {group}, required hearts {total}/{threshold} -> {pos} gains <ALL> x{all_n}')
        return
    if op == 'look_top_choose':
        k = int(gd.get('k', 0) or 0)
        _enqueue_choose_from_topk(gs, k, rng)
        return
    if op == 'look_top_choose_if':
        cond = str(rule.get('cond', '') or '')
        ok = True
        if cond == 'energy_gte':
            need = int(gd.get('n', 0) or 0)
            ok = int(getattr(gs, 'energy_active', 0) or 0) + int(getattr(gs, 'energy_wait', 0) or 0) >= need
        if not ok:
            gs.log.append(f'[AUTO] look_top_choose_if: condition not met ({cond})')
            return
        k = int(gd.get('k', 0) or 0)
        _enqueue_choose_from_topk(gs, k, rng)
        return
    if op == 'look_top_choose_filtered':
        k = int(gd.get('k', 0) or 0)
        kind_jp = str(gd.get('kind', '') or '')
        kind = {'ライブ': 'LIVE', 'メンバー': 'MEMBER'}.get(kind_jp, '')
        group = str(gd.get('group', '') or rule.get('group', '') or '')
        optional = bool(rule.get('optional', False))
        # parse names like 「名前A」か「名前B」
        names_raw = str(gd.get('names', '') or '')
        names = re.findall(r'「([^」]+)」', names_raw) if names_raw else []
        if not kind:
            kind = str(rule.get('card_kind', '') or '').strip().upper()
        cost_min = int(gd.get('cost_min', 0) or 0)
        cost_max = int(gd.get('cost_max', 0) or 0)
        required_total_min = int(gd.get('required_total_min', 0) or 0)
        member_heart_color = _heart_icon_to_color(str(gd.get('member_heart_icon', '') or ''))
        member_heart_min = int(gd.get('member_heart_min', 0) or 0)
        member_heart_colors_any = _heart_icons_to_colors(str(gd.get('member_heart_icons', '') or ''))
        live_req_color = _heart_icon_to_color(str(gd.get('live_req_icon', '') or ''))
        live_req_min = int(gd.get('live_req_min', 0) or 0)
        filter_mode = str(rule.get('filter_mode', '') or '')
        _enqueue_choose_from_topk_filtered(gs, k, rng, cards_db,
                                           filter_kind=kind, filter_group=group,
                                           filter_names=names, optional=optional,
                                           cost_min=cost_min, cost_max=cost_max,
                                           required_total_min=required_total_min,
                                           member_heart_color=member_heart_color,
                                           member_heart_min=member_heart_min,
                                           member_heart_colors_any=member_heart_colors_any,
                                           live_req_color=live_req_color,
                                           live_req_min=live_req_min,
                                           filter_mode=filter_mode)
        return
    if op == 'look_top_3way_split':
        k = int(gd.get('k', 0) or 0)
        _enqueue_look_top_3way_split(gs, k, rng)
        return
    if op == 'look_top_reorder_keep_any':
        k = int(gd.get('k', 0) or 0)
        _enqueue_reorder_from_topk_keep_any(gs, k, rng)
        return
    if op == 'energy_put_wait_then_manual_draw_if_no_bladeheart':
        n = int(gd.get('n', 1) or 1)
        draw_n = int(gd.get('draw_n', 1) or 1)
        n = max(0, n)
        add = _put_wait_energy_from_deck(gs, n, reason='conditional no-bladeheart draw')
        ctx0 = dict(ctx or {})
        src_cn = str(ctx0.get('source_cn', '') or '')
        discarded = str(ctx0.get('discarded_cn', '') or '')
        if not discarded:
            discards = [str(x or '') for x in list(ctx0.get('discarded_cns', []) or []) if str(x or '').strip()]
            discarded = discards[-1] if discards else ''
        if add > 0 and draw_n > 0 and discarded:
            ci_disc = _get_card(cards_db, discarded)
            is_no_bh = bool(ci_disc and not _ci_has_blade_heart_payload(ci_disc))
            if is_no_bh:
                drew = draw(gs, draw_n, rng)
                gs.log.append(f'[AUTO] {src_cn or "?"}: energy wait +{add}; discarded {discarded} has no blade-heart -> draw {drew}')
                msg = f'{src_cn or "この能力"}：エネルギーデッキから{add}枚をウェイト状態で置きました。コストとして控え室に置いたカード {discarded} はブレードハートを持たないため、カードを{drew}枚引きました。'
            else:
                gs.log.append(f'[SKIP] {src_cn or "?"}: energy wait +{add}; discarded {discarded} has blade-heart -> no draw')
                msg = f'{src_cn or "この能力"}：エネルギーデッキから{add}枚をウェイト状態で置きました。コストとして控え室に置いたカード {discarded} はブレードハートを持つため、追加ドローは行いません。'
            gs.pending.append({
                'kind': 'show_revealed_cards_ack',
                'label': '控え室に置いたカード確認',
                'text': msg,
                'display_cards': [discarded],
                'options': ['ok'],
                'source_cn': src_cn,
            })
            return
        if add > 0 and draw_n > 0:
            gs.pending.append({
                'kind': 'confirm_effect',
                'text': f'{src_cn or "この能力"}：エネルギーデッキから{add}枚をウェイト状態で置きました。これにより控え室に置いたカードがブレードハートを持たない場合、カードを{draw_n}枚引きます。条件を満たすなら「使う」、満たさないなら「スキップ」を選んでください。',
                'options': ['apply', 'skip'],
                'after_effect_template': f'カードを{draw_n}枚引く。',
                'ctx': ctx0,
                'source_cn': src_cn,
            })
            gs.log.append(f'[PENDING] {src_cn or "?"}: energy wait +{add}; manual no-bladeheart draw check draw={draw_n}')
        return
    if op == 'energy_put_wait':
        n = int(gd.get('n', 1) or 1)
        n = max(0, n)
        rem = _energy_remaining_in_deck(gs)
        add = min(n, rem)
        if add > 0:
            gs.energy_wait += add
            _clamp_energy_zone(gs)
        gs.log.append(f"[AUTO] energy_put_wait +{add}{' (clipped)' if add<n else ''} (wait={gs.energy_wait})")
        return
    if op == 'energy_put_wait_under_plus_one_self':
        pos = str((ctx or {}).get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
        under = int(getattr(slot, 'energy_under', 0) or 0) if slot else 0
        n = max(0, under + 1)
        add = _put_wait_energy_from_deck(gs, n, reason=f'under+1 self at {pos or "?"}')
        gs.log.append(f"[AUTO] energy_put_wait_under_plus_one_self under={under} -> +{add} (wait={gs.energy_wait})")
        return
    if op == 'energy_activate':
        n = int(gd.get('n', 0) or 0)
        take = min(max(0, n), int(gs.energy_wait or 0))
        gs.energy_wait -= take
        gs.energy_active += take
        gs.log.append(f'[AUTO] energy_activate {n} -> moved {take} (active={gs.energy_active} wait={gs.energy_wait})')
        return
    if op == 'gain_blade_until_end_live':
        blades_blob = gd.get('blades', '')
        b = _count_blade_icons_from_tagblob(blades_blob)
        pos = str(ctx.get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L','C','R') else None
        if not slot:
            gs.log.append('[WARN] gain_blade: no source slot')
            return
        slot.temp_blade += int(b)
        slot.temp_until = 'end_of_live'
        gs.log.append(f'[AUTO] {pos}: gain blade +{b} (until end_of_live)')
        return
    if op == 'activate_stage_member':
        opts = [p for p in ('L','C','R') if gs.stage.get(p) and not bool(getattr(gs.stage.get(p), 'active', True))]
        if not opts:
            gs.log.append('[INFO] activate_member: no WAIT member on stage')
            return
        allow_skip = bool(rule.get('optional', False) or rule.get('allow_less', False))
        opts2 = list(opts) + (['skip'] if allow_skip else [])
        gs.pending.append({
            'kind': 'choose_stage_member_to_activate',
            'text': _auto_effect_detail_block(ctx, 'ステージのウェイト状態のメンバーを1人アクティブにする'),
            'options': opts2,
            'allow_skip': allow_skip,
            'auto_effect_detail': str((ctx or {}).get('auto_effect_detail', '') or ''),
            'suppress_card_text': bool(str((ctx or {}).get('auto_effect_detail', '') or '')),
        })
        gs.log.append('[PENDING] choose WAIT stage member to activate')
        return
    if op == 'position_change_stage_member':
        opts = [p for p in ('L','C','R') if gs.stage.get(p)]
        if not opts:
            gs.log.append('[INFO] position_change: no member on stage')
            return
        allow_skip = bool(rule.get('optional', False) or rule.get('allow_less', False))
        opts2 = list(opts) + (['skip'] if allow_skip else [])
        gs.pending.append({
            'kind': 'choose_stage_member_to_position_change_source',
            'text': _auto_effect_detail_block(ctx, 'ポジションチェンジさせるメンバーを1人選ぶ'),
            'options': opts2,
            'allow_skip': allow_skip,
            'auto_effect_detail': str((ctx or {}).get('auto_effect_detail', '') or ''),
            'suppress_card_text': bool(str((ctx or {}).get('auto_effect_detail', '') or '')),
        })
        gs.log.append('[PENDING] choose stage member to position-change')
        return
    if op == 'gain_icons_until_end_live':
        icons_blob = str(gd.get('icons', '') or '')
        pos = str(ctx.get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
        if not slot:
            gs.log.append('[WARN] gain_icons: no source slot')
            return
        b = _count_blade_icons_from_tagblob(icons_blob)
        if b > 0:
            slot.temp_blade += b
            slot.temp_until = 'end_of_live'
        heart_counts = _parse_heart_icons(icons_blob)
        for col, cnt in heart_counts.items():
            _grant_temp_heart(slot, col, cnt)
        gs.log.append(f'[AUTO] {pos}: gain icons {icons_blob} (until end_of_live; blades={b} hearts={heart_counts})')
        return
    if op == 'choose_heart_gain_self':
        pos = str(ctx.get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
        if not slot:
            gs.log.append('[WARN] choose_heart_gain_self: no source slot')
            return
        src = str(ctx.get('source_cn', '') or pos)
        gs.pending.append({
            'kind': 'choose_heart_color',
            'target': 'self',
            'pos': pos,
            'n': 1,
            'text': f'{src}: 好きなハートの色を1つ指定する → ライブ終了時まで+1',
            'options': ['桃', '赤', '黄', '緑', '青', '紫'],
        })
        gs.log.append(f'[PENDING] {pos}: choose heart color (self)')
        return
    if op == 'choose_heart_gain_other_member':
        pos = str(ctx.get('pos', '') or '').upper()
        group = str(gd.get('group', '') or '')
        src = str(ctx.get('source_cn', '') or pos)
        cands = []
        for p2 in ('L', 'C', 'R'):
            if p2 == pos:
                continue
            slot2 = gs.stage.get(p2)
            if not slot2:
                continue
            if group:
                ci2 = _get_card(cards_db, slot2.cardnumber)
                if not ci2 or group not in str(getattr(ci2, 'group', '') or ''):
                    continue
            cands.append(p2)
        if not cands:
            gs.log.append(f'[INFO] choose_heart_gain_other_member: no valid {group} target')
            return
        gs.pending.append({
            'kind': 'choose_heart_color_for_other',
            'src_pos': pos,
            'candidates': cands,
            'group': group,
            'n': 1,
            'chosen_color': '',
            'text': f'{src}: 好きなハートの色を1つ指定する → ステージの{group}メンバー1人に+1',
            'options': ['桃', '赤', '黄', '緑', '青', '紫'],
        })
        gs.log.append(f'[PENDING] {pos}: choose heart color for other {group} member')
        return
    if op == 'activate_all_stage_members':
        activated = []
        for p2 in ('L', 'C', 'R'):
            slot2 = gs.stage.get(p2)
            if slot2 and not slot2.active:
                slot2.active = True
                activated.append(p2)
        gs.log.append(f'[AUTO] activate all stage members: {activated if activated else "none (already active)"}')
        return
    if op == 'energy_activate_upto':
        n = int(gd.get('n', 0) or 0)
        actual = min(n, int(gs.energy_wait or 0))
        if actual > 0:
            gs.energy_wait -= actual
            gs.energy_active += actual
        gs.log.append(f'[AUTO] energy activate up to {n}: activated {actual} (wait={gs.energy_wait} active={gs.energy_active})')
        return
    if op == 'activate_wait_member_then_temp_blade':
        blades_blob = str(gd.get('blades', '') or '')
        blade_n = max(1, _count_blade_icons_from_tagblob(blades_blob))
        src_cn = str((ctx or {}).get('source_cn', '') or '')
        cands = [p2 for p2 in ('L', 'C', 'R') if gs.stage.get(p2) and not gs.stage[p2].active]
        if not cands:
            gs.log.append(f'[SKIP] {src_cn}: no waiting member to activate and gain blade')
            return
        gs.pending.append({
            'kind': 'choose_stage_wait_member_activate_gain_blade',
            'text': f'【{src_cn or "この能力"}】ウェイト状態のメンバー1人をアクティブにし、ライブ終了時まで、そのメンバーは<(ブレード)>を{blade_n}つ得る',
            'options': list(cands),
            'card_options': [gs.stage[p2].cardnumber for p2 in cands if gs.stage.get(p2)],
            'candidates': list(cands),
            'blade_n': int(blade_n),
            'source_cn': src_cn,
        })
        gs.log.append(f'[PENDING] {src_cn}: choose waiting member to activate + blade {blade_n} ({len(cands)} candidates)')
        return
    if op == 'set_self_wait':
        pos2 = str((ctx or {}).get('pos', '') or '').upper()
        slot2 = gs.stage.get(pos2) if pos2 in ('L', 'C', 'R') else None
        if slot2:
            slot2.active = False
            gs.log.append(f'[AUTO] {pos2}: {slot2.cardnumber} -> WAIT')
        else:
            gs.log.append(f'[WARN] set_self_wait: no member at pos={pos2}')
        return
    if op == 'set_opponent_wait':
        cost_lim = int(gd.get('cost', 99) or 99)
        max_n = int(gd.get('max_n', gd.get('n', 1)) or 1)
        _enqueue_opponent_wait_notice(gs, ctx, f'コスト{cost_lim}以下のメンバーを{max_n}人までウェイトにする')
        return
    if op == 'set_opponent_wait_exactly1':
        cost_lim = int(gd.get('cost', 99) or 99)
        _enqueue_opponent_wait_notice(gs, ctx, f'コスト{cost_lim}以下のメンバー1人をウェイトにする')
        return
    if op == 'set_opponent_wait_all_cost':
        cost_lim = int(gd.get('cost', 99) or 99)
        _enqueue_opponent_wait_notice(gs, ctx, f'すべてのコスト{cost_lim}以下のメンバーをウェイトにする')
        return
    if op == 'set_opponent_wait_original_blade_le':
        blade_lim = int(gd.get('blade_lim', 99) or 99)
        _enqueue_opponent_wait_notice(gs, ctx, f'元々持つ<(ブレード)>の数が{blade_lim}つ以下のメンバー1人をウェイトにする')
        return
    if op == 'set_opponent_wait_original_blade_eq':
        blade_eq = int(gd.get('blade_eq', 99) or 99)
        _enqueue_opponent_wait_notice(gs, ctx, f'元々持つ<(ブレード)>の数がちょうど{blade_eq}つのメンバー1人をウェイトにする')
        return
    if op == 'set_opponent_wait_original_blade_le_not_group':
        blade_lim = int(gd.get('blade_lim', 99) or 99)
        group_name = str(gd.get('group', '') or '').strip()
        _enqueue_opponent_wait_notice(gs, ctx, f'元々持つ<(ブレード)>の数が{blade_lim}つ以下で、かつ『{group_name}』以外のメンバー1人をウェイトにする')
        return
    if op == 'set_opponent_wait_all_original_blade_le':
        blade_lim = int(gd.get('blade_lim', 99) or 99)
        _enqueue_opponent_wait_notice(gs, ctx, f'元々持つ<(ブレード)>の数が{blade_lim}つ以下のすべてのメンバーをウェイトにする')
        return
    if op == 'both_players_wait_all_original_blade_le':
        blade_lim = int(gd.get('blade_lim', 99) or 99)
        own_waited = []
        for p2 in ('L', 'C', 'R'):
            slot2 = gs.stage.get(p2)
            if not slot2:
                continue
            ci2 = _get_card(cards_db, slot2.cardnumber)
            if _is_member_ci(ci2) and _original_blade_count(ci2) <= blade_lim:
                slot2.active = False
                own_waited.append(p2)
        gs.log.append(f'[AUTO] own original blade <= {blade_lim} -> WAIT {own_waited if own_waited else "none"}')
        _enqueue_opponent_wait_notice(gs, ctx, f'相手ステージの元々持つ<(ブレード)>の数が{blade_lim}つ以下のすべてのメンバーをウェイトにする')
        return
    if op == 'opponent_wait_manual_text':
        _enqueue_opponent_wait_notice(gs, ctx, text_norm)
        return
    if op == 'draw_then_opponent_wait':
        got = draw(gs, 1, rng)
        cost_lim = int(gd.get('cost', 99) or 99)
        max_n = int(gd.get('max_n', 1) or 1)
        gs.log.append(f'[AUTO] draw 1 -> drew {got}; then opponent wait manual')
        _enqueue_opponent_wait_notice(gs, ctx, f'コスト{cost_lim}以下のメンバーを{max_n}人までウェイトにする')
        return
    if op == 'conditional_opponent_wait_manual':
        condition = str(gd.get('condition', '') or '').strip()
        action = str(gd.get('action', '') or '').strip()
        body = f'条件「{condition}場合」を満たすなら、{action}' if condition else action
        _enqueue_opponent_wait_notice(gs, ctx, body)
        return
    if op == 'set_opponent_wait_self_choice':
        src_cn = str((ctx or {}).get('source_cn', '') or '')
        gs.log.append('[MANUAL] 相手は自身のステージのアクティブメンバー1人をウェイトにする（手動で処理してください）')
        _enqueue_opponent_wait_notice(gs, ctx, '相手は自身のステージのアクティブメンバー1人をウェイトにする', max_delta=1)
        return
    if op == 'retrieve_from_yell':
        kind = str(rule.get('card_kind', '') or '').upper() or 'ANY'
        kind_jp = str(gd.get('kind', '') or '')
        if kind_jp:
            kind = {'ライブ': 'LIVE', 'メンバー': 'MEMBER'}.get(kind_jp, 'ANY')
        group = str(gd.get('group', '') or '')
        cost_lim = int(gd.get('cost_lim', 99) or 99)
        cost_min = int(gd.get('cost_min', 0) or 0)
        score_lim = int(gd.get('score_lim', 99) or 99)
        max_n = int(gd.get('n', 1) or 1)
        up_to = bool(rule.get('up_to', False))
        src = str((ctx or {}).get('source_cn', '') or '')
        cands = _yell_revealed_candidates(gs, cards_db, kind, group, cost_lim, score_lim, cost_min)
        if not cands:
            gs.log.append(f'[INFO] retrieve_from_yell: no matching card in yell reveals (kind={kind} group={group})')
            return
        label = f'{src}[ライブ成功時]: エールで公開されたカードから{max_n}枚'
        label += 'まで' if up_to else ''
        label += '手札に加える'
        if kind == 'LIVE':
            label += '（ライブカード）'
        elif kind == 'MEMBER':
            label += '（メンバーカード）'
        elif kind == 'COST_MEMBER_OR_SCORE_LIVE':
            label += f'（コスト{cost_lim}以下のメンバーかスコア{score_lim}以下のライブ）'
        elif kind == 'COST_MEMBER_LE':
            label += f'（コスト{cost_lim}以下のメンバー）'
        elif kind == 'COST_MEMBER_GE':
            label += f'（コスト{cost_min}以上のメンバー）'
        elif kind == 'COST_MEMBER_RANGE':
            label += f'（コスト{cost_min}以上{cost_lim}以下のメンバー）'
        if group:
            label += f'（{group}）'
        opts = list(cands)
        if up_to:
            opts = ['skip'] + opts
        gs.pending.append({
            'kind': 'pick_from_yell',
            'text': label,
            'options': opts,
            'source_cn': src,
            'remaining_n': max_n,
            'card_kind': kind,
            'group': group,
            'cost_lim': cost_lim,
            'score_lim': score_lim,
            'cost_min': cost_min,
            'up_to': up_to,
        })
        gs.log.append(f'[PENDING] retrieve_from_yell: {len(cands)} candidates, take {max_n}{" up to" if up_to else ""}')
        return
    if op == 'put_yell_to_deck_top':
        kind_jp = str(gd.get('kind', '') or '')
        kind = {'ライブ': 'LIVE', 'メンバー': 'MEMBER'}.get(kind_jp, str(rule.get('card_kind', '') or '').upper() or 'ANY')
        max_n = int(gd.get('n', 1) or 1)
        src = str((ctx or {}).get('source_cn', '') or '')
        cands = _yell_revealed_candidates(gs, cards_db, kind)
        if not cands:
            gs.log.append(f'[INFO] put_yell_to_deck_top: no matching card in yell reveals (kind={kind})')
            return
        label = f'{src}[ライブ成功時]: エールで公開されたカードから1枚までデッキの一番上に置く'
        if kind == 'LIVE':
            label += '（ライブカード）'
        elif kind == 'MEMBER':
            label += '（メンバーカード）'
        gs.pending.append({
            'kind': 'pick_from_yell_to_deck_top',
            'text': label,
            'options': ['skip'] + list(cands),
            'source_cn': src,
            'remaining_n': max_n,
            'card_kind': kind,
            'up_to': True,
        })
        gs.log.append(f'[PENDING] put_yell_to_deck_top: {len(cands)} candidates, up to {max_n}')
        return
    if op == 'put_yell_to_deck_bottom':
        kind_jp = str(gd.get('kind', '') or '')
        kind = {'ライブ': 'LIVE', 'メンバー': 'MEMBER'}.get(kind_jp, 'ANY')
        max_n = int(gd.get('n', 1) or 1)
        src = str((ctx or {}).get('source_cn', '') or '')
        cands = _yell_revealed_candidates(gs, cards_db, kind)
        if not cands:
            gs.log.append(f'[INFO] put_yell_to_deck_bottom: no matching card in yell reveals (kind={kind})')
            return
        label = f'{src}[ライブ成功時]: エールで公開されたカードから{max_n}枚までデッキの一番下に置く'
        if kind == 'LIVE':
            label += '（ライブカード）'
        elif kind == 'MEMBER':
            label += '（メンバーカード）'
        gs.pending.append({
            'kind': 'pick_from_yell_to_deck_bottom',
            'text': label,
            'options': ['skip'] + list(cands),
            'source_cn': src,
            'remaining_n': max_n,
            'card_kind': kind,
        })
        gs.log.append(f'[PENDING] put_yell_to_deck_bottom: {len(cands)} candidates, up to {max_n}')
        return
    if op == 'draw_if':
        cond = str(rule.get('cond', '') or '')
        n = int(gd.get('n', 0) or 0)
        group = str(gd.get('group', '') or rule.get('group', '') or '')
        name = str(gd.get('name', '') or rule.get('name', '') or '')
        met = False
        if cond == 'energy_gte':
            met = (int(gs.energy_active or 0) + int(gs.energy_wait or 0)) >= n
        elif cond == 'stage_member_cost_gte':
            for _pos2, slot in gs.stage.items():
                if slot:
                    ci2 = _get_card(cards_db, slot.cardnumber)
                    eff_cost = int(_slot_effective_cost(gs, cards_db, _pos2, slot) or getattr(ci2, 'cost', 0) or 0)
                    if ci2 and eff_cost >= n:
                        met = True; break
        elif cond == 'success_nonempty':
            met = len(list(getattr(gs, 'success_zone', []) or [])) > 0
        elif cond == 'green_size_gte':
            met = len(gs.green_room) >= n
        elif cond == 'stage_has_other_group_member':
            trigger_cn = str(getattr(gs, '_trigger_cn', '') or '')
            for slot in gs.stage.values():
                if slot and slot.cardnumber != trigger_cn:
                    ci2 = _get_card(cards_db, slot.cardnumber)
                    if ci2 and group and group in str(getattr(ci2, 'group', '') or ''):
                        met = True; break
        elif cond == 'stage_has_named_member':
            for slot in gs.stage.values():
                if slot:
                    ci2 = _get_card(cards_db, slot.cardnumber)
                    if ci2 and name and name in str(getattr(ci2, 'name', '') or ''):
                        met = True; break
        if met:
            drew = draw(gs, 1, rng)
            gs.log.append(f'[AUTO] draw_if ({cond}): condition met -> drew {drew}')
        else:
            gs.log.append(f'[AUTO] draw_if ({cond}): condition not met -> skip')
        return
    gs.log.append(f"[WARN] effect op not implemented: {op}")

def _normalize_turn_order(value: Any, allow_empty: bool = False) -> str:
    s = str(value or '').strip().lower()
    if not s and allow_empty:
        return ''
    if s in ('second', 'gote', '後手', '2', 'false'):
        return 'second'
    if s in ('first', 'sente', '先手', '1', 'true'):
        return 'first'
    return '' if allow_empty else 'first'

def _turn_order_label(value: Any) -> str:
    return '後手' if _normalize_turn_order(value) == 'second' else '先手'

def _opponent_success_count(gs: 'GameState') -> int:
    try:
        return max(0, min(2, int(getattr(gs, 'opponent_success_count', 0) or 0)))
    except Exception:
        return 0

def _set_opponent_success_count(gs: 'GameState', value: int) -> int:
    v = max(0, min(2, int(value or 0)))
    try:
        gs.opponent_success_count = v
    except Exception:
        pass
    return v

def _set_turn_order(gs: 'GameState', value: Any) -> str:
    v = _normalize_turn_order(value)
    try:
        gs.turn_order = v
    except Exception:
        pass
    return v

def _reset_opponent_wait_count(gs: 'GameState', reason: str = '') -> None:
    before = _opponent_wait_count(gs)
    if before <= 0:
        return
    _set_opponent_wait_count(gs, 0)
    msg = f'[AUTO] opponent_wait_count reset {before} -> 0'
    if reason:
        msg += f' ({reason})'
    try:
        gs.log.append(msg)
    except Exception:
        pass

def _apply_turn_order_transition_resets(gs: 'GameState') -> None:
    # Current-turn reset: if we are first, opponent turn begins after our turn ends.
    cur = _normalize_turn_order(getattr(gs, 'turn_order', 'first'))
    if cur == 'first':
        _reset_opponent_wait_count(gs, '先手のターン終了時')
    # Apply next-turn order selected by success-storage decision, if any.
    nxt = _normalize_turn_order(getattr(gs, 'next_turn_order', ''), allow_empty=True)
    if nxt:
        try:
            gs.turn_order = nxt
            gs.next_turn_order = ''
            gs.log.append(f'[TURN_ORDER] next turn -> {_turn_order_label(nxt)}')
        except Exception:
            pass
    else:
        try:
            gs.turn_order = cur
        except Exception:
            pass
    # Next-turn reset: if we are second, opponent turn happened before our turn begins.
    if _normalize_turn_order(getattr(gs, 'turn_order', 'first')) == 'second':
        _reset_opponent_wait_count(gs, '後手のターン開始前')

def _opponent_wait_count(gs: 'GameState') -> int:
    try:
        return max(0, min(3, int(getattr(gs, 'opponent_wait_count', 0) or 0)))
    except Exception:
        return 0


def _set_opponent_wait_count(gs: 'GameState', value: int) -> int:
    v = max(0, min(3, int(value or 0)))
    try:
        gs.opponent_wait_count = v
    except Exception:
        pass
    return v


def _add_opponent_wait_count(gs: 'GameState', delta: int) -> int:
    return _set_opponent_wait_count(gs, _opponent_wait_count(gs) + int(delta or 0))


def _infer_opponent_wait_delta_max(text: str, default: int = 3) -> int:
    body = str(text or '')
    try:
        if 'すべて' in body:
            return 3
        m = re.search(r'(\d+)\s*人\s*まで', body)
        if m:
            return max(0, min(3, int(m.group(1))))
        m = re.search(r'(\d+)\s*人', body)
        if m:
            return max(0, min(3, int(m.group(1))))
    except Exception:
        pass
    return max(0, min(3, int(default or 3)))


def _enqueue_opponent_wait_notice(gs: 'GameState', ctx: Dict[str, Any], text: str, log_text: str = '', max_delta: Optional[int] = None) -> None:
    """Queue a shared opponent-wait prompt.

    The current simulator does not model individual opponent stage cards.  It now
    tracks only the number of opponent waiting members (0..3).  When a wait
    effect resolves, the player records how many opponent members were actually
    made WAIT; that count is used by continuous/reference effects.
    """
    src_cn = str((ctx or {}).get('source_cn', '') or '')
    body = str(text or '').strip()
    if not body:
        body = '相手のステージにいる該当メンバーをウェイトにする'
    if max_delta is None:
        max_delta = _infer_opponent_wait_delta_max(body, 3)
    max_delta = max(0, min(3, int(max_delta or 0)))
    opts = [str(i) for i in range(0, max_delta + 1)]
    before = _opponent_wait_count(gs)
    gs.log.append(str(log_text or f'[MANUAL] {body}（相手の盤面で処理し、実際にウェイトにした人数を選択）'))
    gs.pending.append({
        'kind': 'opponent_wait_notify',
        'text': f'【相手への効果】{body}\n実際にウェイト状態にした相手メンバー数を選んでください。現在の相手ウェイト数: {before}/3',
        'source_cn': src_cn,
        'options': opts,
        'max_delta': int(max_delta),
    })


def _original_blade_count(ci: Optional[CardInfo]) -> int:
    try:
        return int(getattr(ci, 'blade', 0) or 0)
    except Exception:
        return 0

def try_apply_effect_template(gs: 'GameState', rng: random.Random, cards_db: Dict[str, CardInfo], effect_text: str, ctx: Dict[str, Any]) -> bool:
    """Apply an effect_template using the embedded regex rules.
    Also supports a small subset of "mode/choice" wrappers used by key cards.
    """
    text = str(effect_text or '').strip()
    if not text:
        return False
    text_norm = _normalize_icon_token_text(text).replace('\n', '')
    # Stage-leave BODY auto wrapper.  Trigger collection verifies the timing,
    # then the inner effect is resolved through the same generic route as normal
    # effects (draw/discard, top-k search, activate member, position change, ...).
    inner_stage_leave = _strip_stage_to_green_trigger_prefix(text_norm)
    if inner_stage_leave != text_norm:
        detail = _auto_effect_detail_for_condition(ctx, text_norm, 'このメンバーがステージから控え室に置かれた', '自動効果')
        ctx2 = _with_auto_effect_detail(ctx, detail)
        return bool(try_apply_effect_template(gs, rng, cards_db, inner_stage_leave, ctx2))

    # Success live-card storage count wrappers.
    # Example: 自分の成功ライブカード置き場にカードが2枚以上ある場合、...
    m_success_count_gte = re.match(r'^自分の成功ライブカード置き場にカードが(?:(?P<count>\d+)枚以上(?:ある)?|ある)場合、(?P<inner>.+)$', text_norm)
    if m_success_count_gte:
        need_count = int(m_success_count_gte.group('count') or 1)
        own_count = len(list(getattr(gs, 'success_zone', []) or []))
        inner = str(m_success_count_gte.group('inner') or '').strip()
        if own_count >= need_count:
            gs.log.append(f'[AUTO] success-zone count {own_count}/{need_count} -> apply inner effect')
            ctx2 = _with_auto_effect_detail(ctx, _auto_effect_detail_for_condition(ctx, text_norm, f'自分の成功ライブカード置き場 {own_count}/{need_count}枚', '登場時'))
            return bool(try_apply_effect_template(gs, rng, cards_db, inner, ctx2))
        gs.log.append(f'[SKIP] success-zone count {own_count}/{need_count} -> condition not met')
        return True

    # Success live-card storage score-sum wrappers.
    # These are conditions around already-generic inner effects.
    # Example: 自分の成功ライブカード置き場にあるカードのスコア合計が3以上の場合、...
    m_success_score_gte = re.match(r'^自分の成功ライブカード置き場にあるカードのスコア(?:の)?合計が(?P<thr>\d+)以上の場合、(?P<inner>.+)$', text_norm)
    if m_success_score_gte:
        thr = int(m_success_score_gte.group('thr') or 0)
        got = int(_own_success_zone_score_sum(gs, cards_db) or 0)
        inner = str(m_success_score_gte.group('inner') or '').strip()
        if got >= thr:
            gs.log.append(f'[AUTO] success-zone score sum {got}/{thr} -> apply inner effect')
            ctx2 = _with_auto_effect_detail(ctx, _auto_effect_detail_for_condition(ctx, text_norm, f'成功ライブカード置き場のスコア合計 {got}/{thr}', '登場時'))
            return bool(try_apply_effect_template(gs, rng, cards_db, inner, ctx2))
        gs.log.append(f'[SKIP] success-zone score sum {got}/{thr} -> condition not met')
        return True

    # Example: 自分の成功ライブカード置き場にカードが1枚以上あり、かつスコアの合計が1以下の場合、...
    m_success_count_score_lte = re.match(r'^自分の成功ライブカード置き場にカードが(?P<count>\d+)枚以上あり、かつスコアの合計が(?P<thr>\d+)以下の場合、(?P<inner>.+)$', text_norm)
    if m_success_count_score_lte:
        need_count = int(m_success_count_score_lte.group('count') or 0)
        thr = int(m_success_count_score_lte.group('thr') or 0)
        own_count = len(list(getattr(gs, 'success_zone', []) or []))
        got_sum = int(_own_success_zone_score_sum(gs, cards_db) or 0)
        inner = str(m_success_count_score_lte.group('inner') or '').strip()
        if own_count >= need_count and got_sum <= thr:
            gs.log.append(f'[AUTO] success-zone count/score condition count={own_count}/{need_count}, score_sum={got_sum}<={thr} -> apply inner effect')
            ctx2 = _with_auto_effect_detail(ctx, _auto_effect_detail_for_condition(ctx, text_norm, f'成功ライブカード置き場 {own_count}/{need_count}枚、スコア合計 {got_sum}<={thr}', '登場時'))
            return bool(try_apply_effect_template(gs, rng, cards_db, inner, ctx2))
        gs.log.append(f'[SKIP] success-zone count/score condition count={own_count}/{need_count}, score_sum={got_sum}<={thr} -> condition not met')
        return True

    # Example: 成功ライブ置き場の <スコア+1> μ's cards: 1 -> +1, 2+ -> +2.
    m_success_score_tag = re.match(r"^自分の成功ライブカード置き場に<\(スコア\+1\)>を持つ『(?P<group>[^』]+)』のカードが1枚ある場合、ライブ終了時まで、(?:『|「)<常時>ライブの合計スコアを\+1する。(?:』|」)を得る。2枚以上ある場合、代わりに(?:『|「)<常時>』?ライブの合計スコアを\+2する。(?:』|」)を得る。$", text_norm)
    if m_success_score_tag:
        group_name = str(m_success_score_tag.group('group') or '').strip()
        got = int(_own_success_zone_count_with_score_tag_and_group(gs, cards_db, group_name) or 0)
        if got >= 2:
            return bool(_grant_source_live_total_score_until_end(gs, ctx, 2, label=f'success-zone <スコア+1> 『{group_name}』 cards={got}'))
        if got == 1:
            return bool(_grant_source_live_total_score_until_end(gs, ctx, 1, label=f'success-zone <スコア+1> 『{group_name}』 cards={got}'))
        gs.log.append(f'[SKIP] success-zone <スコア+1> 『{group_name}』 cards={got} -> condition not met')
        return True

    # Activation-only condition wrapper: check condition, then apply the inner effect.
    cond_thr = int(_activated_success_score_sum_condition(text_norm) or 0)
    if cond_thr:
        got_sum = int(_own_success_zone_score_sum(gs, cards_db) or 0)
        inner = _strip_activated_success_score_sum_condition(text_norm)
        if got_sum >= cond_thr:
            gs.log.append(f'[AUTO] activated success-zone score condition {got_sum}/{cond_thr} -> apply inner effect')
            return bool(try_apply_effect_template(gs, rng, cards_db, inner, ctx))
        gs.log.append(f'[SKIP] activated success-zone score condition {got_sum}/{cond_thr} -> condition not met')
        return True

    # Conditional wrapper: stage has another group/unit member -> apply inner effect.
    m_stage_other = re.match(r'^自分のステージにほかの『(?P<tag>[^』]+)』のメンバーがいる場合、(?P<inner>.+)$', text_norm)
    if m_stage_other:
        tag = str(m_stage_other.group('tag') or '').strip()
        inner = str(m_stage_other.group('inner') or '').strip()
        src_pos = str((ctx or {}).get('pos', '') or '').upper()
        if _stage_has_other_group_or_unit_member(gs, cards_db, src_pos, tag):
            gs.log.append(f'[AUTO] stage has other 『{tag}』 member -> apply inner effect')
            m_retrieve_group_live = re.match(r'^自分の控え室から『(?P<group>[^』]+)』のライブカードを1枚手札に加える。$', inner)
            if m_retrieve_group_live:
                group = str(m_retrieve_group_live.group('group') or '').strip()
                ctx2 = _with_auto_effect_detail(ctx, _auto_effect_detail_for_condition(ctx, text_norm, f'ステージにほかの『{tag}』メンバーがいる', '登場時'))
                _enqueue_choose_from_green(gs, cards_db, kind='LIVE', n=1, group=group, ctx=ctx2)
                gs.log.append(f'[PENDING] {str((ctx or {}).get("source_cn", "") or "")} stage-other-『{tag}』 condition -> retrieve 『{group}』 LIVE from waiting room')
                return True
            return bool(try_apply_effect_template(gs, rng, cards_db, inner, ctx))
        gs.log.append(f'[SKIP] stage has other 『{tag}』 member -> condition not met')
        return True

    # Cost-result: gain total live score while this source member remains in the live.
    # e.g. ライブ終了時まで、「<常時>ライブの合計スコアを+3する。」を得る。
    m_score = re.match(r'^ライブ終了時まで、「<常時>ライブの合計スコアを\+(?P<n>\d+)する。」を得る。$', text_norm)
    if m_score:
        pos = str((ctx or {}).get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
        if not slot:
            gs.log.append('[WARN] named-hand cost-result score: no source slot')
            return True
        n = int(m_score.group('n') or 0)
        slot.temp_score = int(getattr(slot, 'temp_score', 0) or 0) + n
        slot.temp_until = 'end_of_live'
        gs.log.append(f'[AUTO] {pos}: live total score +{n} (until end_of_live)')
        return True
    # Cost-result: gain icons once per card discarded by this cost.
    m_icons_per_discard = re.match(r'^ライブ終了時まで、これ(?:によって|により)控え室に置いた枚数1枚につき(?P<icons>(?:<\([^)]+\)>)+)を得る。$', text_norm)
    if m_icons_per_discard:
        pos = str((ctx or {}).get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
        if not slot:
            gs.log.append('[WARN] named-hand cost-result icons/count: no source slot')
            return True
        n = int((ctx or {}).get('discarded_count', 0) or 0)
        icons = str(m_icons_per_discard.group('icons') or '')
        b, hs = _grant_temp_icons_to_slot(slot, icons, n)
        gs.log.append(f'[AUTO] {pos}: cost-result discarded_count={n} -> icons {icons} x{n} (blades={b} hearts={hs})')
        return True
    # Cost-result: gain one heart of each color among discarded named cards' hearts.
    m_hearts_from_discarded = re.match(r'^ライブ終了時まで、これにより控え室に置いたそれらのカードが持つハートの色1つにつき、その色のハートを1つずつ得る。$', text_norm)
    if m_hearts_from_discarded:
        pos = str((ctx or {}).get('pos', '') or '').upper()
        slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
        if not slot:
            gs.log.append('[WARN] named-hand cost-result hearts/colors: no source slot')
            return True
        cols: List[str] = []
        for cn in list((ctx or {}).get('discarded_cns', []) or []):
            ci2 = _get_card(cards_db, cn)
            for col in _card_heart_colors_for_cost_result(ci2):
                if col not in cols:
                    cols.append(col)
        for col in cols:
            _grant_temp_heart(slot, col, 1)
        gs.log.append(f'[AUTO] {pos}: cost-result discarded heart colors -> {cols}')
        return True
    # Mode wrapper: choose one / choose one or more (Daydream Mermaid etc.)
    # Example:
    #   以下から1つを選ぶ。自分の成功ライブカード置き場に『虹ヶ咲』のカードがある場合、代わりに1つ以上を選ぶ。
    #   ・A...
    #   ・B...
    if ('以下から' in text) and ('選ぶ' in text) and ('・' in text):
        opts: List[str] = []
        for ln in text.splitlines():
            ln = str(ln).strip()
            if ln.startswith('・'):
                opts.append(ln[1:].strip())
        if opts:
            # default: exactly 1
            max_pick = 1
            # conditional: if success live storage has group X, allow 1+ selections
            mcond = re.search(r"成功ライブカード置き場に『(?P<g>[^』]+)』のカードがある場合、代わりに1つ以上を選ぶ。", text)
            if mcond:
                g = str(mcond.group('g') or '').strip()
                if g and _success_has_group(gs, cards_db, g):
                    max_pick = len(opts)
            # Prepare prompt
            src = str((ctx or {}).get('source_cn', '') or '')
            ttl = src if src else '効果'
            if max_pick > 1:
                msg = f'{ttl}: 以下から1つ以上を選ぶ'
            else:
                msg = f'{ttl}: 以下から1つを選ぶ'
            options = list(opts)
            # Add a finish button only when multiple picks are allowed
            if max_pick > 1:
                options.append('Done')
            gs.pending.append({
                'kind': 'choose_effects',
                'text': msg,
                'options': options,
                'remaining': list(opts),
                'picked': [],
                'min': 1,
                'max': int(max_pick),
                'ctx': dict(ctx or {}),
            })
            gs.log.append(f'[PENDING] choose_effects: {ttl} opts={len(opts)} max={max_pick}')
            return True
    # Plain regex rule
    m = _match_effect_template(text)
    if not m:
        return False
    rule, gd = m
    _apply_effect_by_rule(gs, rng, cards_db, rule, gd, ctx)
    return True
def _ability_has_choose_header(ab: Dict[str, Any]) -> bool:
    try:
        clauses = ab.get('clauses', [])
    except Exception:
        clauses = []
    if not isinstance(clauses, list):
        return False
    for cl in clauses:
        if not isinstance(cl, dict):
            continue
        eff0 = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
        if ('以下から' in eff0) and ('選ぶ' in eff0):
            return True
    return False

def _stage_has_group_or_unit_member(gs: 'GameState', cards_db: Dict[str, CardInfo], tag: str) -> bool:
    tag = str(tag or '').strip()
    if not tag:
        return False
    return bool(_stage_group_member_positions(gs, cards_db, tag))

def _build_choose_effects_prompt_from_ability(
    gs: 'GameState',
    cards_db: Dict[str, CardInfo],
    ab: Dict[str, Any],
    ctx: Dict[str, Any],
    *,
    timing: str = '効果',
) -> Optional[Dict[str, Any]]:
    """Build one pending prompt for abilities split as choose-header + option clauses.

    This prevents option clauses from being queued as independent auto effects.
    Conditional choose headers such as Private Wars still create a live-start
    trigger.  The header condition is checked at resolution time; if it is not
    met, the effect fizzles with an acknowledgement prompt instead of being
    removed from the trigger order.
    """
    try:
        clauses = ab.get('clauses', [])
    except Exception:
        clauses = []
    if not isinstance(clauses, list) or not clauses:
        return None
    header_i = None
    header_text = ''
    for i, cl in enumerate(clauses):
        if not isinstance(cl, dict):
            continue
        eff0 = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
        if ('以下から' in eff0) and ('選ぶ' in eff0):
            header_i = i
            header_text = eff0
            break
    if header_i is None:
        return None

    opts: List[str] = []
    for cl in clauses[header_i+1:]:
        if not isinstance(cl, dict):
            continue
        cost = str(cl.get('cost_template', '') or '').strip()
        eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
        if cost or not eff:
            # A split choose block with per-option costs is not supported by this
            # generic prompt.  Treat it as unhandled instead of partially queuing
            # the option clauses as independent live-start triggers.
            continue
        if eff.startswith('・'):
            eff = eff[1:].strip()
        if eff:
            opts.append(eff)
    if not opts:
        return None

    src = str((ctx or {}).get('source_cn', '') or '')
    ttl = src if src else '効果'

    # Header condition: 自分のステージに『X』のメンバーがいる場合、以下から1つを選ぶ。
    m_stage_group = re.search(r"自分のステージに『(?P<tag>[^』]+)』のメンバーがいる場合、以下から", header_text)
    if m_stage_group:
        tag = str(m_stage_group.group('tag') or '').strip()
        if tag and not _stage_has_group_or_unit_member(gs, cards_db, tag):
            # The ability itself has triggered.  Per rules, do not remove it
            # from the live-start order.  When the player resolves it, show that
            # the condition is unmet and apply no option.
            gs.log.append(f'[PENDING] {ttl}[{timing}]: choose block condition unmet (no stage 『{tag}』 member)')
            return {
                'kind': 'message_ack',
                'label': f'{ttl} {timing} condition unmet',
                'source_cn': src,
                'text': f'【{ttl}】{timing}：自分のステージに『{tag}』のメンバーがいないため、効果は適用されません。',
                'options': ['ok'],
            }

    max_pick = 1
    mcond = re.search(r"成功ライブカード置き場に『(?P<g>[^』]+)』のカードがある場合、代わりに1つ以上を選ぶ。", header_text)
    if mcond:
        g = str(mcond.group('g') or '').strip()
        if g and _success_has_group(gs, cards_db, g):
            max_pick = len(opts)

    msg = f"{ttl}: 以下から{'1つ以上' if max_pick>1 else '1つ'}を選ぶ"
    if m_stage_group:
        tag = str(m_stage_group.group('tag') or '').strip()
        if tag:
            msg = f"{ttl}: ステージに『{tag}』のメンバーがいる場合、以下から{'1つ以上' if max_pick>1 else '1つ'}を選ぶ"

    options = list(opts)
    if max_pick > 1:
        options.append('Done')
    return {
        'kind': 'choose_effects',
        'text': msg,
        'options': options,
        'remaining': list(opts),
        'picked': [],
        'min': 1,
        'max': int(max_pick),
        'ctx': dict(ctx or {}),
        'source_cn': src,
    }
def _enqueue_choose_effects_from_ability(gs: 'GameState', cards_db: Dict[str, CardInfo], ab: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
    """Handle 'mode' style abilities where the choice header and options are split across clauses.
    Typical pattern (Daydream Mermaid / Private Wars etc.):
      clause0: '以下から1つを選ぶ。' possibly with a condition
      clause1+: individual option effects (as separate clauses)
    """
    prm = _build_choose_effects_prompt_from_ability(gs, cards_db, ab, ctx, timing='選択効果')
    if not prm:
        return False
    if prm.get('_skipped'):
        return True
    gs.pending.append(prm)
    try:
        ttl = str((ctx or {}).get('source_cn', '') or '効果')
        gs.log.append(f"[PENDING] choose_effects: {ttl} opts={len(prm.get('remaining', []) or [])} max={int(prm.get('max', 1) or 1)}")
    except Exception:
        pass
    return True
def _iter_activated_abilities(ci: Optional[CardInfo]):
    if not ci or not getattr(ci, 'abilities', None):
        return []
    abilities = list(getattr(ci, 'abilities', None) or [])
    out = []
    for ab in abilities:
        if not isinstance(ab, dict):
            continue
        at = str(ab.get('ability_type', '') or '')
        if '起動' not in at:
            continue
        out.append(ab)
    return out
def _has_matchable_activated(ci: Optional[CardInfo]) -> bool:
    if not ci:
        return False
    for ab in _iter_activated_abilities(ci):
        if not isinstance(ab, dict):
            continue
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            if not eff:
                continue
            if _match_effect_template(eff):
                return True
    return False
def _iter_triggered_abilities(ci: Optional[CardInfo], trigger_kw: str):
    if not ci:
        return []
    abilities0 = list(getattr(ci, 'abilities', None) or [])
    # Some tokv1-only/PB cards can be present in the stat DB before the compiled
    # ability DB is refreshed. Keep this as a narrow fallback in the generic
    # triggered-ability shape so the normal [登場] optional-cost route still runs.
    # Do not require abilities0 to be empty: a partially parsed row may have
    # abilities but no [登場] trigger.
    if _canon_cardno(getattr(ci, 'cardnumber', '') or '') == 'PL!SP-pb2-013' and '登場' in str(trigger_kw or ''):
        has_enter = False
        for _ab0 in abilities0:
            if isinstance(_ab0, dict) and ('登場' in str(_ab0.get('trigger', '') or '')):
                has_enter = True
                break
        if not has_enter:
            abilities0 = list(abilities0) + [{
                'ability_type': '自動',
                'trigger': '登場',
                'conditions': '',
                'clauses': [{
                    'optional': True,
                    'cost_template': '手札の『KALEIDOSCORE』のカードを1枚控え室に置いてもよい',
                    'effect_template': '自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。これにより控え室に置いたカードがブレードハートを持たない場合、カードを1枚引く。',
                    'cost_op': None,
                    'effect_op': None,
                    'raw': '手札の『KALEIDOSCORE』のカードを1枚控え室に置いてもよい：自分のエネルギーデッキから、エネルギーカードを1枚ウェイト状態で置く。これにより控え室に置いたカードがブレードハートを持たない場合、カードを1枚引く。',
                }],
            }]
    if not abilities0:
        return []
    out = []
    for ab in abilities0:
        if not isinstance(ab, dict):
            continue
        trig = str(ab.get('trigger', '') or '')
        if trigger_kw not in trig:
            continue
        out.append(ab)
    return out
def _pretty_optional_effect_prompt_text(trigger_label: str, source_cn: str, cost_text: str, effect_text: str) -> str:
    trig = str(trigger_label or '').strip()
    src = str(source_cn or '').strip()
    cost = str(cost_text or '').strip()
    eff = str(effect_text or '').strip()
    prefix = f"{src}[{trig}]" if src and trig else (src or trig or '効果')
    try:
        m = _match_effect_template(eff)
    except Exception:
        m = None
    rule = m[0] if isinstance(m, tuple) and m else {}
    ext_key = str(rule.get('ext_key', '') or '')
    if ext_key == 'enter_pick_mus_member_from_green':
        return f"{prefix}: このメンバーをウェイトにしてもよい → 自分の控え室から『μ's』のメンバーカードを1枚手札に加える"
    if ext_key == 'live_start_pick_mus_live_from_green':
        return f"{prefix}: 自分の成功カード置き場にカードがある場合、手札を1枚控え室に置いてもよい → 自分の控え室から『μ's』のライブカードを1枚手札に加える"
    if ext_key == 'live_start_choose_pinkYellowPurple_heart':
        return f"{prefix}: 手札を1枚控え室に置いてもよい → 桃 / 黄 / 紫 から1つ選び、ライブ終了時までそのハートを1つ得る"
    if ext_key == 'live_start_no_mus_blade5_force_not_center':
        return f"{prefix}: 自分のステージにブレード5以上の『μ's』メンバーがいない場合、このメンバーはセンターエリア以外にポジションチェンジする"
    if cost and eff:
        if eff.startswith(cost) or cost.startswith(eff):
            return f"{prefix}: {eff if len(eff) >= len(cost) else cost}"
        return f"{prefix}: {cost} → {eff}"
    return f"{prefix}: {eff or cost}"
def _ability_has_supported_clause(ci: Optional[CardInfo], trigger_kw: str = '', activated: bool = False) -> bool:
    if not ci:
        return False
    abs_ = _iter_activated_abilities(ci) if activated else (ci.abilities or [])
    for ab in abs_:
        if trigger_kw:
            trig = str(ab.get('trigger', '') or '')
            if trigger_kw not in trig:
                continue
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            if not eff:
                continue
            if _match_effect_template(eff):
                return True
    return False
@dataclass
class StageSlot:
    cardnumber: str
    active: bool = True
    temp_blade: int = 0
    temp_hearts: Dict[str, int] = field(default_factory=dict)
    temp_score: int = 0
    temp_cost: int = 0
    temp_until: str = ""  # e.g., end_of_live
    energy_under: int = 0  # number of energy cards under this member (UI + some effects)
    heart_replace_color: str = ""  # 元々持つハートを置換する色（ライブ終了時まで）。空=無効
@dataclass
class GameState:
    root: str
    code: str
    seed: int
    debug: bool = False
    # Phase exists for UI/trace stability.
    # We'll keep it coarse until rules-accurate phase machine is implemented.
    phase: str = "MAIN"
    deck: List[str] = field(default_factory=list)
    hand: List[str] = field(default_factory=list)
    energy_active: int = 3
    energy_wait: int = 0
    # Energy deck total (fixed at 12)
    energy_total: int = ENERGY_TOTAL_DEFAULT
    stage: Dict[str, Optional[StageSlot]] = field(default_factory=lambda: {"L": None, "C": None, "R": None})
    green_room: List[str] = field(default_factory=list)
    set_zone: List[str] = field(default_factory=list)
    # hand->set during the current LIVE_SET phase; default 3, may be reduced by effects like 安養寺姫芽
    live_set_limit: int = 3
    # one-shot delta reserved for the next LIVE_SET phase (e.g. -1 by 安養寺姫芽)
    next_live_set_limit_delta: int = 0
    success_zone: List[str] = field(default_factory=list)  # 成功ライブカード置き場
    opponent_success_score_sum: int = -1  # manual/debug opponent success-zone score sum; -1 means unknown
    opponent_success_count: int = 0  # manual/UI tracked opponent success live storage count (0..2)
    opponent_wait_count: int = 0  # manual/UI tracked opponent waiting members count (0..3)
    turn_order: str = "first"  # current turn perspective: first/sente or second/gote
    next_turn_order: str = ""  # set by success-store decision; applied at next turn start
    resolve_zone: List[str] = field(default_factory=list)
    pending: List[Dict[str, Any]] = field(default_factory=list)
    live_start_prompted: bool = False
    # per-turn temporary (compat)
    turn_blade_bonus: int = 0
    # UI-only transient banner (e.g., LIVE success/fail)
    banner_text: str = ""
    banner_ts: float = 0.0
    banner_ttl: float = 0.0
    turn: int = 1
    log: List[str] = field(default_factory=list)
    undo_stack: List[Dict[str, Any]] = field(default_factory=list)
    # activation usage tracking (e.g., <ターン1回>)
    used_this_turn: Dict[str, int] = field(default_factory=dict)
    # last LIVE attempt result (for LIVE_RESOLVE timing / success-zone decision)
    last_attempt_lives: List[str] = field(default_factory=list)
    last_attempt_score_bonus: List[int] = field(default_factory=list)  # aligned to last_attempt_lives; success-phase temporary +N/-N after direct set
    last_attempt_score_set: List[Optional[int]] = field(default_factory=list)  # aligned to last_attempt_lives; direct 「スコアはNになる」 values
    last_attempt_total_score_bonus: int = 0  # live-success adjustment to the live total score, not tied to one LIVE
    last_attempt_score_rows: List[Dict[str, int]] = field(default_factory=list)  # per-live rows from attempt: {cn, base, delta, score}
    last_attempt_attempt_score: int = 0
    last_attempt_final_score: int = 0
    last_attempt_ok: bool = False
    need_live_success_triggers: bool = False
    need_success_store_choice: bool = False
    # live-start buff (until end of live): for each card in success storage, gain chosen heart
    success_zone_heart_color: str = ""  # e.g., 'pink'/'yellow'/'purple'
    success_zone_heart_pos: str = ""    # source stage slot for UI overlay, e.g., 'L'/'C'/'R'
    deck_refreshed_this_turn: bool = False
    live_start_score_bonus_by_set_idx: Dict[int, int] = field(default_factory=dict)
    live_start_required_any_reduction_by_set_idx: Dict[int, int] = field(default_factory=dict)
    live_start_score_bonus_by_cn: Dict[str, int] = field(default_factory=dict)
    live_start_required_any_reduction_by_cn: Dict[str, int] = field(default_factory=dict)
    live_start_required_any_increase_by_set_idx: Dict[int, int] = field(default_factory=dict)
    live_start_required_any_increase_by_cn: Dict[str, int] = field(default_factory=dict)
    vivid_world_blue_mode_this_live: bool = False
    vivid_world_bonus_this_live: int = 0
    live_start_resolved_set_idxs: List[int] = field(default_factory=list)
    cannot_live_until_end_of_live: bool = False
def post_process(gs: GameState) -> None:
    """Post-process hook to keep UI prompts consistent.
    Currently used to resume a deferred auto-order prompt.
    """
    q = getattr(gs, '_deferred_auto_queue', None)
    if not q:
        return
    try:
        pend = list(getattr(gs, 'pending', []) or [])
    except Exception:
        pend = []
    if pend:
        return
    # Build options from remaining trigger queue.
    opts = []
    try:
        for t in list(q):
            cn = str((t or {}).get('source_cn', '') or '').strip()
            if not cn:
                continue
            opts.append(cn)
    except Exception:
        opts = []
    # de-dup (canon) while preserving order
    seen = set()
    opts2: List[str] = []
    for x in opts:
        k = _canon_cardno(str(x))
        if not k or k in seen:
            continue
        seen.add(k)
        opts2.append(str(x))
    if not opts2:
        setattr(gs, '_deferred_auto_queue', [])
        return
    gs.pending.append({
        'kind': 'auto_order',
        'text': str(getattr(gs, '_deferred_auto_text', '') or '自動効果が複数発生：解決するカードを選択（1つずつ）'),
        'options': opts2,
        'queue': list(q),
    })
    setattr(gs, '_deferred_auto_queue', [])
def snapshot_state(gs: GameState) -> Dict[str, Any]:
    """Create an undo snapshot.
    IMPORTANT: Do NOT include gs.undo_stack itself in the snapshot.
    Including it causes recursive growth (snapshot contains past snapshots),
    which quickly becomes exponential and kills performance.
    We also exclude the text log (gs.log) to keep snapshots small; undo will
    append a new log entry instead of restoring prior logs.
    """
    stage_snap: Dict[str, Any] = {}
    for k in ("L", "C", "R"):
        slot = gs.stage.get(k)
        if slot is None:
            stage_snap[k] = None
        else:
            stage_snap[k] = {"cardnumber": slot.cardnumber, "active": bool(slot.active), "temp_blade": int(getattr(slot, "temp_blade", 0) or 0), "temp_hearts": dict(getattr(slot, "temp_hearts", {}) or {}), "temp_score": int(getattr(slot, "temp_score", 0) or 0), "temp_cost": int(getattr(slot, "temp_cost", 0) or 0), "temp_until": str(getattr(slot, "temp_until", "") or ""), "energy_under": int(getattr(slot, "energy_under", 0) or 0), "heart_replace_color": str(getattr(slot, "heart_replace_color", "") or "")}
    return {
        "phase": gs.phase,
        "deck": list(gs.deck),
        "hand": list(gs.hand),
        "energy_active": int(gs.energy_active),
        "energy_wait": int(gs.energy_wait),
        "energy_total": int(getattr(gs, "energy_total", ENERGY_TOTAL_DEFAULT) or ENERGY_TOTAL_DEFAULT),
        "stage": stage_snap,
        "green_room": list(gs.green_room),
        "set_zone": list(gs.set_zone),
        "live_set_limit": int(getattr(gs, "live_set_limit", 3) or 3),
        "next_live_set_limit_delta": int(getattr(gs, "next_live_set_limit_delta", 0) or 0),
        "success_zone": list(getattr(gs, "success_zone", []) or []),
        "opponent_success_score_sum": int(getattr(gs, "opponent_success_score_sum", -1) or -1),
        "opponent_success_count": max(0, min(2, int(getattr(gs, "opponent_success_count", 0) or 0))),
        "opponent_wait_count": max(0, min(3, int(getattr(gs, "opponent_wait_count", 0) or 0))),
        "turn_order": str(getattr(gs, "turn_order", "first") or "first"),
        "next_turn_order": str(getattr(gs, "next_turn_order", "") or ""),
        "resolve_zone": list(gs.resolve_zone),
        "pending": json.loads(json.dumps(gs.pending)) if gs.pending else [],
        "live_start_prompted": bool(gs.live_start_prompted),
        "turn": int(gs.turn),
        "used_this_turn": dict(getattr(gs, "used_this_turn", {}) or {}),
        "last_attempt_lives": list(getattr(gs, 'last_attempt_lives', []) or []),
        "last_attempt_score_bonus": [int(x) for x in (getattr(gs, 'last_attempt_score_bonus', []) or [])],
        "last_attempt_score_set": [None if x is None else int(x) for x in (getattr(gs, 'last_attempt_score_set', []) or [])],
        "last_attempt_total_score_bonus": int(getattr(gs, 'last_attempt_total_score_bonus', 0) or 0),
        "last_attempt_score_rows": [dict(x) for x in (getattr(gs, 'last_attempt_score_rows', []) or [])],
        "last_attempt_attempt_score": int(getattr(gs, 'last_attempt_attempt_score', 0) or 0),
        "last_attempt_final_score": int(getattr(gs, 'last_attempt_final_score', 0) or 0),
        "last_attempt_ok": bool(getattr(gs, 'last_attempt_ok', False)),
        "need_live_success_triggers": bool(getattr(gs, 'need_live_success_triggers', False)),
        "need_success_store_choice": bool(getattr(gs, 'need_success_store_choice', False)),
        # end-of-live buffs
        "success_zone_heart_color": str(getattr(gs, 'success_zone_heart_color', '') or ''),
        "success_zone_heart_pos": str(getattr(gs, 'success_zone_heart_pos', '') or ''),
        "deck_refreshed_this_turn": bool(getattr(gs, 'deck_refreshed_this_turn', False)),
        "live_start_score_bonus_by_set_idx": {int(k): int(v) for k, v in dict(getattr(gs, "live_start_score_bonus_by_set_idx", {}) or {}).items()},
        "live_start_required_any_reduction_by_set_idx": {int(k): int(v) for k, v in dict(getattr(gs, "live_start_required_any_reduction_by_set_idx", {}) or {}).items()},
        "live_start_score_bonus_by_cn": {str(k): int(v) for k, v in dict(getattr(gs, "live_start_score_bonus_by_cn", {}) or {}).items()},
        "live_start_required_any_reduction_by_cn": {str(k): int(v) for k, v in dict(getattr(gs, "live_start_required_any_reduction_by_cn", {}) or {}).items()},
        "live_start_required_any_increase_by_set_idx": {int(k): int(v) for k, v in dict(getattr(gs, "live_start_required_any_increase_by_set_idx", {}) or {}).items()},
        "live_start_required_any_increase_by_cn": {str(k): int(v) for k, v in dict(getattr(gs, "live_start_required_any_increase_by_cn", {}) or {}).items()},
        "vivid_world_blue_mode_this_live": bool(getattr(gs, "vivid_world_blue_mode_this_live", False)),
        "vivid_world_bonus_this_live": int(getattr(gs, "vivid_world_bonus_this_live", 0) or 0),
        "live_start_resolved_set_idxs": list(getattr(gs, "live_start_resolved_set_idxs", []) or []),
    }
def restore_state(gs: GameState, snap: Dict[str, Any]) -> None:
    """Restore from an undo snapshot (see snapshot_state)."""
    gs.phase = snap.get("phase", gs.phase)
    gs.deck = list(snap.get("deck", gs.deck))
    gs.hand = list(snap.get("hand", gs.hand))
    gs.energy_active = int(snap.get("energy_active", gs.energy_active))
    gs.energy_wait = int(snap.get("energy_wait", gs.energy_wait))
    gs.energy_total = int(snap.get("energy_total", getattr(gs, "energy_total", ENERGY_TOTAL_DEFAULT) or ENERGY_TOTAL_DEFAULT) or ENERGY_TOTAL_DEFAULT)
    _clamp_energy_zone(gs)
    stage_in = snap.get("stage", {}) or {}
    stage_new: Dict[str, Optional[StageSlot]] = {"L": None, "C": None, "R": None}
    for k in ("L", "C", "R"):
        v = stage_in.get(k)
        if v is None:
            stage_new[k] = None
        else:
            stage_new[k] = StageSlot(cardnumber=str(v.get("cardnumber", "")), active=bool(v.get("active", True)), temp_blade=_safe_int(v.get("temp_blade", 0), 0), temp_hearts=dict(v.get("temp_hearts", {}) or {}), temp_score=_safe_int(v.get("temp_score", 0), 0), temp_cost=_safe_int(v.get("temp_cost", 0), 0), temp_until=str(v.get("temp_until", "") or ""), energy_under=_safe_int(v.get("energy_under", 0), 0), heart_replace_color=str(v.get("heart_replace_color", "") or ""))
    gs.stage = stage_new
    gs.green_room = list(snap.get("green_room", gs.green_room))
    gs.set_zone = list(snap.get("set_zone", gs.set_zone))
    gs.live_set_limit = int(snap.get("live_set_limit", getattr(gs, "live_set_limit", 3) or 3) or 3)
    gs.next_live_set_limit_delta = int(snap.get("next_live_set_limit_delta", getattr(gs, "next_live_set_limit_delta", 0) or 0) or 0)
    gs.success_zone = list(snap.get("success_zone", getattr(gs, "success_zone", [])))
    gs.opponent_success_score_sum = _safe_int(snap.get("opponent_success_score_sum", getattr(gs, "opponent_success_score_sum", -1)), -1)
    gs.opponent_success_count = max(0, min(2, _safe_int(snap.get("opponent_success_count", getattr(gs, "opponent_success_count", 0)), 0)))
    gs.opponent_wait_count = max(0, min(3, _safe_int(snap.get("opponent_wait_count", getattr(gs, "opponent_wait_count", 0)), 0)))
    gs.turn_order = _normalize_turn_order(snap.get("turn_order", getattr(gs, "turn_order", "first")))
    gs.next_turn_order = _normalize_turn_order(snap.get("next_turn_order", getattr(gs, "next_turn_order", "")), allow_empty=True)
    gs.resolve_zone = list(snap.get("resolve_zone", gs.resolve_zone))
    gs.pending = list(snap.get("pending", gs.pending) or [])
    gs.live_start_prompted = bool(snap.get("live_start_prompted", gs.live_start_prompted))
    gs.turn = int(snap.get("turn", gs.turn))
    try:
        gs.used_this_turn = {str(k): int(v) for k, v in (snap.get("used_this_turn", {}) or {}).items()}
    except Exception:
        gs.used_this_turn = {}
    gs.last_attempt_lives = list(snap.get('last_attempt_lives', getattr(gs, 'last_attempt_lives', []) or []))
    try:
        gs.last_attempt_score_bonus = [int(x) for x in (snap.get('last_attempt_score_bonus', getattr(gs, 'last_attempt_score_bonus', []) or []) or [])]
    except Exception:
        gs.last_attempt_score_bonus = []
    try:
        _sets_in = list(snap.get('last_attempt_score_set', getattr(gs, 'last_attempt_score_set', []) or []) or [])
        gs.last_attempt_score_set = [None if x is None or str(x) == '' else int(x) for x in _sets_in]
    except Exception:
        gs.last_attempt_score_set = []
    try:
        gs.last_attempt_total_score_bonus = int(snap.get('last_attempt_total_score_bonus', getattr(gs, 'last_attempt_total_score_bonus', 0) or 0) or 0)
    except Exception:
        gs.last_attempt_total_score_bonus = 0
    try:
        gs.last_attempt_score_rows = [dict(x) for x in list(snap.get('last_attempt_score_rows', getattr(gs, 'last_attempt_score_rows', [])) or [])]
    except Exception:
        gs.last_attempt_score_rows = []
    while len(gs.last_attempt_score_bonus) < len(gs.last_attempt_lives):
        gs.last_attempt_score_bonus.append(0)
    if len(gs.last_attempt_score_bonus) > len(gs.last_attempt_lives):
        gs.last_attempt_score_bonus = gs.last_attempt_score_bonus[:len(gs.last_attempt_lives)]
    while len(gs.last_attempt_score_set) < len(gs.last_attempt_lives):
        gs.last_attempt_score_set.append(None)
    if len(gs.last_attempt_score_set) > len(gs.last_attempt_lives):
        gs.last_attempt_score_set = gs.last_attempt_score_set[:len(gs.last_attempt_lives)]
    gs.last_attempt_attempt_score = int(snap.get('last_attempt_attempt_score', getattr(gs, 'last_attempt_attempt_score', 0) or 0) or 0)
    gs.last_attempt_final_score = int(snap.get('last_attempt_final_score', getattr(gs, 'last_attempt_final_score', 0) or 0) or 0)
    gs.last_attempt_ok = bool(snap.get('last_attempt_ok', getattr(gs, 'last_attempt_ok', False)))
    gs.need_live_success_triggers = bool(snap.get('need_live_success_triggers', getattr(gs, 'need_live_success_triggers', False)))
    gs.need_success_store_choice = bool(snap.get('need_success_store_choice', getattr(gs, 'need_success_store_choice', False)))
    gs.success_zone_heart_color = str(snap.get('success_zone_heart_color', getattr(gs, 'success_zone_heart_color', '') or '') or '')
    gs.success_zone_heart_pos = str(snap.get('success_zone_heart_pos', getattr(gs, 'success_zone_heart_pos', '') or '') or '')
    gs.deck_refreshed_this_turn = bool(snap.get('deck_refreshed_this_turn', getattr(gs, 'deck_refreshed_this_turn', False)))
    try:
        gs.live_start_score_bonus_by_set_idx = {int(k): int(v) for k, v in dict(snap.get('live_start_score_bonus_by_set_idx', getattr(gs, 'live_start_score_bonus_by_set_idx', {}) or {}) or {}).items()}
    except Exception:
        gs.live_start_score_bonus_by_set_idx = {}
    try:
        gs.live_start_required_any_reduction_by_set_idx = {int(k): int(v) for k, v in dict(snap.get('live_start_required_any_reduction_by_set_idx', getattr(gs, 'live_start_required_any_reduction_by_set_idx', {}) or {}) or {}).items()}
    except Exception:
        gs.live_start_required_any_reduction_by_set_idx = {}
        gs.live_start_required_any_increase_by_set_idx = {}
    try:
        gs.live_start_score_bonus_by_cn = {str(k): int(v) for k, v in dict(snap.get('live_start_score_bonus_by_cn', getattr(gs, 'live_start_score_bonus_by_cn', {}) or {}) or {}).items()}
    except Exception:
        gs.live_start_score_bonus_by_cn = {}
    try:
        gs.live_start_required_any_reduction_by_cn = {str(k): int(v) for k, v in dict(snap.get('live_start_required_any_reduction_by_cn', getattr(gs, 'live_start_required_any_reduction_by_cn', {}) or {}) or {}).items()}
    except Exception:
        gs.live_start_required_any_reduction_by_cn = {}
        gs.live_start_required_any_increase_by_cn = {}
    gs.live_start_required_any_increase_by_set_idx = {}
    gs.live_start_required_any_increase_by_cn = {}
    try:
        gs.live_start_required_any_increase_by_set_idx = {int(k): int(v) for k, v in dict(snap.get('live_start_required_any_increase_by_set_idx', getattr(gs, 'live_start_required_any_increase_by_set_idx', {}) or {}) or {}).items()}
    except Exception:
        gs.live_start_required_any_increase_by_set_idx = {}
    try:
        gs.live_start_required_any_increase_by_cn = {str(k): int(v) for k, v in dict(snap.get('live_start_required_any_increase_by_cn', getattr(gs, 'live_start_required_any_increase_by_cn', {}) or {}) or {}).items()}
    except Exception:
        gs.live_start_required_any_increase_by_cn = {}
    gs.vivid_world_blue_mode_this_live = bool(snap.get('vivid_world_blue_mode_this_live', getattr(gs, 'vivid_world_blue_mode_this_live', False)))
    gs.vivid_world_bonus_this_live = int(snap.get('vivid_world_bonus_this_live', getattr(gs, 'vivid_world_bonus_this_live', 0) or 0) or 0)
    try:
        gs.live_start_resolved_set_idxs = [int(x) for x in (snap.get('live_start_resolved_set_idxs', getattr(gs, 'live_start_resolved_set_idxs', []) or []) or [])]
    except Exception:
        gs.live_start_resolved_set_idxs = []
def _trace_path(root: Path) -> Path:
    # Human-readable trace for this UI session (overwritten on new game).
    return root / "sim_trace.txt"
def trace_write(gs: GameState, msg: str) -> None:
    # Keep in-memory log + file trace.
    ts = time.strftime("%H:%M:%S")
    line = f"{ts} {msg}"
    gs.log.append(line)
    try:
        p = _trace_path(Path(gs.root))
        with p.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # Never break gameplay due to trace I/O.
        pass
def begin_turn(gs: GameState, rng: Optional[random.Random] = None) -> None:
    # reset per-turn usage
    try:
        gs.used_this_turn = {}
    except Exception:
        pass
    gs.deck_refreshed_this_turn = False
    try:
        gs.live_set_limit = 3
    except Exception:
        pass
    # reset last LIVE attempt (timing helpers)
    gs.last_attempt_lives = []
    gs.last_attempt_ok = False
    gs.need_live_success_triggers = False
    gs.need_success_store_choice = False
    gs.live_start_resolved_set_idxs = []
    gs.live_start_score_bonus_by_set_idx = {}
    gs.live_start_required_any_reduction_by_set_idx = {}
    gs.live_start_score_bonus_by_cn = {}
    gs.live_start_required_any_reduction_by_cn = {}
    gs.live_start_required_any_increase_by_set_idx = {}
    gs.live_start_required_any_increase_by_cn = {}
    # Rules order (coarse): ACTIVE -> ENERGY -> DRAW -> MAIN
    gs.phase = "ACTIVE"
    refresh(gs)
    trace_write(gs, f"[PHASE] ACTIVE (refresh) E active={gs.energy_active} wait={gs.energy_wait}")
    gs.phase = "ENERGY"
    energy_phase(gs)
    trace_write(gs, f"[PHASE] ENERGY (+1) E active={gs.energy_active} wait={gs.energy_wait}")
    gs.phase = "DRAW"
    d = draw(gs, 1, rng)
    trace_write(gs, f"[PHASE] DRAW (draw {d}) hand={len(gs.hand)} deck={len(gs.deck)}")
    gs.phase = "MAIN"
    trace_write(gs, f"[PHASE] MAIN turn={gs.turn}")
def push_undo(gs: GameState, rng: random.Random) -> None:
    gs.undo_stack.append({"snap": snapshot_state(gs), "rng": rng.getstate()})
def do_undo(gs: GameState, rng: random.Random) -> bool:
    if not gs.undo_stack:
        trace_write(gs, "[UNDO] nothing to undo")
        return False
    last = gs.undo_stack.pop()
    restore_state(gs, last["snap"])
    rng.setstate(last["rng"])
    trace_write(gs, "[UNDO] restored previous state")
    return True
def _guess_tsv_columns(fieldnames: List[str]) -> Tuple[str, str]:
    """Return (count_key, cardno_key) from TSV headers (case-insensitive)."""
    fn = [f.strip() for f in (fieldnames or []) if f]
    lower = {f.lower(): f for f in fn}
    # count
    for k in ["count", "qty", "quantity", "num", "枚数"]:
        if k in lower:
            count_key = lower[k]
            break
    else:
        count_key = fn[0] if fn else "count"
    # card number
    for k in ["card_no", "cardno", "cardnumber", "cn", "db_id", "id", "カード番号", "card"]:
        if k in lower:
            card_key = lower[k]
            break
    else:
        card_key = fn[1] if len(fn) >= 2 else (fn[0] if fn else "card_no")
    return count_key, card_key
def _read_deck_tsv(p: Path) -> List[str]:
    import csv
    cards: List[str] = []
    # TSV is the canonical decklist format in this project.
    # Must handle BOM + optional headers.
    text = p.read_text(encoding="utf-8-sig", errors="replace")
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    if not lines:
        return []
    sniffer = lines[0]
    has_header = any(x in sniffer.lower() for x in ["count", "card_no", "cardnumber", "rarity", "枚数", "カード"])
    if has_header:
        rdr = csv.DictReader(lines, delimiter="\t")
        count_key, card_key = _guess_tsv_columns(list(rdr.fieldnames or []))
        for row in rdr:
            if not row:
                continue
            cnt = _safe_int(row.get(count_key, 0), 0)
            cn = _canon_cardno(str(row.get(card_key, "") or ""))
            # Safety net: never accept numeric cn (cn=2/3事故対策)
            if cn.isdigit():
                cn = ""
            if cn and cnt > 0:
                cards.extend([cn] * cnt)
        return cards
    # No header: assume first two columns are (count, card_no)
    rdr2 = csv.reader(lines, delimiter="\t")
    for cols in rdr2:
        if not cols:
            continue
        cnt = _safe_int(cols[0] if len(cols) >= 1 else 0, 0)
        cn_raw = cols[1] if len(cols) >= 2 else ""
        cn = _canon_cardno(cn_raw)
        if cn.isdigit():
            cn = ""
        if cn and cnt > 0:
            cards.extend([cn] * cnt)
    return cards
def load_simdeck(root: Path, code: str) -> List[str]:
    """Load deck for `code`.
    Priority:
      1) sim_decks/deck_<code>.json (legacy)
      2) decklists/<code>.tsv (canonical)
      3) sim_decks/deck_<code>.tsv (alternate)
      4) decklists/deck_<code>.tsv (alternate)
    """
    # 1) Legacy JSON (keep for backward compatibility)
    p_json = root / "sim_decks" / f"deck_{code}.json"
    if p_json.exists():
        obj = _read_json(p_json)
        cards: List[str] = []
        for ent in (obj.get("cards", []) or []) if isinstance(obj, dict) else []:
            if not isinstance(ent, dict):
                continue
            cnt = _safe_int(ent.get("count", 0), 0)
            cn = _canon_cardno(
                str(
                    ent.get("db_id")
                    or ent.get("cardnumber")
                    or ent.get("card_no")
                    or ent.get("tsv_card_no")
                    or ""
                )
            )
            if cn.isdigit():
                cn = ""
            if cn and cnt > 0:
                cards.extend([cn] * cnt)
        return cards
    # 2-4) TSV decklists
    cand = [
        root / "decklists" / f"{code}.tsv",
        root / "sim_decks" / f"deck_{code}.tsv",
        root / "decklists" / f"deck_{code}.tsv",
        root / "decklists" / f"{code}.txt",
    ]
    for p in cand:
        if p.exists():
            return _read_deck_tsv(p)
    # Give a precise error with all candidate paths.
    msg = "\n".join([f"- {str(x)}" for x in [p_json] + cand])
    raise FileNotFoundError(
        f"deck file not found for code={code}. Looked for:\n{msg}"
    )
def new_game(root: Path, code: str, seed: int, debug: bool) -> Tuple[GameState, random.Random]:
    deck_cards = load_simdeck(root, code)
    rng = random.Random(seed)
    rng.shuffle(deck_cards)
    gs = GameState(root=str(root), code=code, seed=seed, debug=debug, phase="ACTIVE")
    gs.deck = deck_cards
    for _ in range(6):
        if gs.deck:
            gs.hand.append(gs.deck.pop(0))
    # Reset trace file for this UI session
    try:
        _trace_path(root).write_text("", encoding="utf-8")
    except Exception:
        pass
    trace_write(gs, f"[NEW] code={code} seed={seed} opening_hand=6 turn={gs.turn}")
    # Start turn 1 (ACTIVE→ENERGY→DRAW→MAIN) so energy/draw are applied at game start.
    begin_turn(gs, rng)
    return gs, rng
def draw(gs: GameState, n: int, rng: Optional[random.Random] = None) -> int:
    k = 0
    for _ in range(n):
        if not gs.deck:
            _rule_refresh_main_deck(gs, rng, reason='draw')
        if not gs.deck:
            break
        gs.hand.append(gs.deck.pop(0))
        k += 1
        # Rule timing: if the last card was just drawn and deck became empty,
        # refresh immediately instead of waiting for the next draw/check.
        if not gs.deck:
            _rule_refresh_main_deck(gs, rng, reason='draw@exhaust')
    return k
def pay_energy(gs: GameState, cost: int) -> bool:
    if cost <= 0:
        return True
    if gs.energy_active < cost:
        return False
    gs.energy_active -= cost
    gs.energy_wait += cost
    return True
def _energy_under_total(gs: 'GameState') -> int:
    s = 0
    for slot in (gs.stage or {}).values():
        if slot:
            s += int(getattr(slot, 'energy_under', 0) or 0)
    return int(s)
def _energy_in_play(gs: 'GameState') -> int:
    return int(gs.energy_active or 0) + int(gs.energy_wait or 0) + _energy_under_total(gs)
def _energy_remaining_in_deck(gs: 'GameState') -> int:
    total = int(getattr(gs, 'energy_total', ENERGY_TOTAL_DEFAULT) or ENERGY_TOTAL_DEFAULT)
    return max(0, total - _energy_in_play(gs))
def _clamp_energy_zone(gs: 'GameState') -> None:
    """Ensure active+wait does not exceed capacity = energy_total - under_total."""
    total = int(getattr(gs, 'energy_total', ENERGY_TOTAL_DEFAULT) or ENERGY_TOTAL_DEFAULT)
    cap = max(0, total - _energy_under_total(gs))
    cur = int(gs.energy_active or 0) + int(gs.energy_wait or 0)
    if cur <= cap:
        return
    over = cur - cap
    # reduce wait first, then active
    take_w = min(int(gs.energy_wait or 0), over)
    gs.energy_wait -= take_w
    over -= take_w
    if over > 0:
        take_a = min(int(gs.energy_active or 0), over)
        gs.energy_active -= take_a

def _return_under_energy_to_deck_from_slot(gs: 'GameState', slot: Optional['StageSlot'], pos: str = '', reason: str = '', cards_db: Optional[Dict[str, CardInfo]] = None) -> int:
    try:
        n = int(getattr(slot, 'energy_under', 0) or 0) if slot else 0
    except Exception:
        n = 0
    if n <= 0:
        return 0
    try:
        if slot is not None:
            slot.energy_under = 0
    except Exception:
        pass
    msg = f"[INFO] {str(pos or '?').upper()}: return under-energy x{n} to energy deck"
    if reason:
        msg += f" ({reason})"
    try:
        gs.log.append(msg)
    except Exception:
        pass
    # Energy deck is implicit by counts; clearing energy_under is enough.
    return n
    return int(n)
def refresh(gs: GameState) -> None:
    for k in ("L", "C", "R"):
        if gs.stage.get(k):
            gs.stage[k].active = True
    gs.energy_active += gs.energy_wait
    gs.energy_wait = 0
def _rule_refresh_main_deck(gs: GameState, rng: Optional[random.Random], reason: str = '') -> bool:
    if list(getattr(gs, 'deck', []) or []):
        return False
    pool = list(getattr(gs, 'green_room', []) or [])
    if not pool:
        return False
    try:
        if rng is not None:
            rng.shuffle(pool)
        else:
            import random as _random
            _random.shuffle(pool)
    except Exception:
        import random as _random
        _random.shuffle(pool)
    gs.green_room = []
    gs.deck = list(pool)
    gs.deck_refreshed_this_turn = True
    gs.log.append(f"[REFRESH] main deck <- waiting room x{len(pool)}" + (f" ({reason})" if reason else ""))
    return True
def _rule_refresh_for_top_access(gs: GameState, rng: Optional[random.Random], need: int, reason: str = '') -> bool:
    need = int(need or 0)
    if need <= 0:
        return False
    cur = len(getattr(gs, 'deck', []) or [])
    if cur >= need:
        return False
    pool = list(getattr(gs, 'green_room', []) or [])
    if not pool:
        return False
    keep = list(getattr(gs, 'deck', []) or [])
    try:
        if rng is not None:
            rng.shuffle(pool)
        else:
            import random as _random
            _random.shuffle(pool)
    except Exception:
        import random as _random
        _random.shuffle(pool)
    gs.green_room = []
    gs.deck = keep + pool
    gs.deck_refreshed_this_turn = True
    gs.log.append(f"[REFRESH] top-access need={need} cur={cur} add_waiting={len(pool)}" + (f" ({reason})" if reason else ""))
    return True
def energy_phase(gs: GameState) -> None:
    # Add 1 energy from the energy deck if available (total fixed at 12).
    rem = _energy_remaining_in_deck(gs)
    if rem <= 0:
        return
    gs.energy_active += 1
    _clamp_energy_zone(gs)
def _has_under_energy_blade_bonus(ci: Optional[CardInfo]) -> bool:
    """Detect 常時: 'このメンバーの下にあるエネルギーカード1枚につき、<(ブレード)>を得る。'"""
    if not ci or not getattr(ci, 'abilities', None):
        return False
    for ab in ci.abilities:
        if not isinstance(ab, dict):
            continue
        at = str(ab.get('ability_type', '') or '')
        if '常時' not in at:
            continue
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '')
            blob = _norm_digits_jp(eff)
            if ('このメンバーの下' in blob) and ('エネルギー' in blob) and ('ブレード' in blob):
                return True
    return False
def _has_body_always_cost13_blade_bonus(ci: Optional[CardInfo]) -> bool:
    """Return True if the card has a 常時(BODY) ability that grants +2 blade
    when self or opponent stage has a cost-13+ member.
    Matches PL!S-PR-029/030/031 effect:
      <常時> 自分か相手のステージにコスト13以上のメンバーがいる場合、<(ブレード)><(ブレード)>を得る。
    """
    if not ci or not getattr(ci, 'abilities', None):
        return False
    for ab in ci.abilities:
        if not isinstance(ab, dict):
            continue
        at = str(ab.get('ability_type', '') or '')
        if '常時' not in at:
            continue
        # trigger field may be 'BODY' for this card type
        trig = str(ab.get('trigger', '') or '')
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '')
            if 'コスト13以上' in eff and 'ブレード' in eff:
                return True
    return False
def _stage_has_cost13_plus_member(gs: 'GameState', cards_db: Dict[str, CardInfo]) -> bool:
    """Return True if any slot on stage (self) has current/effective cost >= 13."""
    for pos, slot in (gs.stage or {}).items():
        if not slot:
            continue
        ci = _get_card(cards_db, slot.cardnumber)
        if not ci:
            continue
        if _is_live_ci(ci):
            continue
        try:
            eff_cost = _slot_effective_cost(gs, cards_db, str(pos), slot)
            if int(eff_cost or getattr(ci, 'cost', 0) or 0) >= 13:
                return True
        except Exception:
            pass
    return False
def _stage_has_other_higher_cost_member(gs: 'GameState', cards_db: Dict[str, CardInfo], self_pos: str, self_cost: int) -> bool:
    """Return True if another stage member has current/effective cost strictly greater than self_cost."""
    try:
        for pos, slot in (gs.stage or {}).items():
            if pos == self_pos or not slot:
                continue
            ci = _get_card(cards_db, getattr(slot, 'cardnumber', ''))
            if not ci or _is_live_ci(ci):
                continue
            try:
                eff_cost = _slot_effective_cost(gs, cards_db, str(pos), slot)
                if int(eff_cost or getattr(ci, 'cost', 0) or 0) > int(self_cost or 0):
                    return True
            except Exception:
                pass
    except Exception:
        pass
    return False
def _stage_distinct_member_name_count(gs: 'GameState', cards_db: Dict[str, CardInfo]) -> int:
    """Count distinct member names currently on stage."""
    names = set()
    try:
        for pos in ('L', 'C', 'R'):
            slot = (gs.stage or {}).get(pos)
            if not slot or not getattr(slot, 'cardnumber', ''):
                continue
            ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
            if not ci or _is_live_ci(ci):
                continue
            nm = str(getattr(ci, 'name', '') or getattr(ci, 'cardname', '') or '').strip()
            if nm:
                names.add(nm)
    except Exception:
        pass
    return int(len(names))


def _stage_distinct_member_group_name_count(gs: 'GameState', cards_db: Dict[str, CardInfo]) -> int:
    """Count distinct non-empty group names among members currently on stage."""
    groups = set()
    try:
        for pos in ('L', 'C', 'R'):
            slot = (gs.stage or {}).get(pos)
            if not slot or not getattr(slot, 'cardnumber', ''):
                continue
            ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
            if not ci or _is_live_ci(ci):
                continue
            g = str(getattr(ci, 'group', '') or '').strip()
            if g:
                groups.add(g)
    except Exception:
        pass
    return int(len(groups))

def _stage_member_current_heart_color_counts(gs: 'GameState', cards_db: Dict[str, CardInfo]) -> Dict[str, int]:
    """Return current colored heart counts held by stage members.

    This is for card text of the form 「ステージにいるメンバーが持つハート」.
    It includes base hearts, blade-heart hearts, always-on bonuses, and temporary
    hearts granted until end of live.  <ALL> is deliberately not expanded into
    six colors here; it remains a non-colored wildcard for live requirement
    allocation, not a literal possession of all six named colored hearts.
    """
    out: Dict[str, int] = {}
    colors = {'pink', 'red', 'yellow', 'green', 'blue', 'purple'}
    try:
        for pos in ('L', 'C', 'R'):
            slot = (gs.stage or {}).get(pos)
            if not slot or not getattr(slot, 'cardnumber', ''):
                continue
            ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
            if not ci or _is_live_ci(ci):
                continue
            replace_col = str(getattr(slot, 'heart_replace_color', '') or '').lower().strip()
            if replace_col in colors:
                total = 0
                for mp in (getattr(ci, 'base_hearts', {}) or {}, getattr(ci, 'blade_hearts', {}) or {}):
                    for _k, _v in (mp or {}).items():
                        try:
                            if str(_k).lower() in colors:
                                total += int(_v or 0)
                        except Exception:
                            pass
                if total > 0:
                    out[replace_col] = int(out.get(replace_col, 0) or 0) + int(total)
            else:
                for mp in (getattr(ci, 'base_hearts', {}) or {}, getattr(ci, 'blade_hearts', {}) or {}):
                    for k, v in (mp or {}).items():
                        kk = str(k or '').lower().strip()
                        if kk in colors:
                            out[kk] = int(out.get(kk, 0) or 0) + int(v or 0)
            try:
                for k, v in (_slot_always_hearts_bonus(gs, cards_db, pos, slot) or {}).items():
                    kk = str(k or '').lower().strip()
                    if kk in colors:
                        out[kk] = int(out.get(kk, 0) or 0) + int(v or 0)
            except Exception:
                pass
            try:
                for k, v in (getattr(slot, 'temp_hearts', {}) or {}).items():
                    kk = str(k or '').lower().strip()
                    if kk in colors:
                        out[kk] = int(out.get(kk, 0) or 0) + int(v or 0)
            except Exception:
                pass
    except Exception:
        pass
    return {k: int(v) for k, v in out.items() if int(v or 0) > 0}

def _stage_member_has_all_heart_colors(gs: 'GameState', cards_db: Dict[str, CardInfo], colors: List[str]) -> Tuple[bool, List[str], List[str]]:
    need = [str(c or '').lower().strip() for c in list(colors or []) if str(c or '').lower().strip() in {'pink','red','yellow','green','blue','purple'}]
    counts = _stage_member_current_heart_color_counts(gs, cards_db)
    have = [c for c in need if int(counts.get(c, 0) or 0) > 0]
    missing = [c for c in need if c not in have]
    return (len(missing) == 0 and len(need) > 0, have, missing)


def _stage_member_heart_color_kind_count(gs: 'GameState', cards_db: Dict[str, CardInfo]) -> int:
    """Count distinct colored hearts currently held by stage members."""
    try:
        counts = _stage_member_current_heart_color_counts(gs, cards_db)
        return int(len([k for k, v in (counts or {}).items() if int(v or 0) > 0 and str(k) in {'pink','red','yellow','green','blue','purple'}]))
    except Exception:
        return 0


def _stage_all_areas_group_members_distinct_names(gs: 'GameState', cards_db: Dict[str, CardInfo], group_name: str) -> bool:
    """Return True if L/C/R are all occupied by members matching group/unit and have distinct names."""
    names = set()
    tag = str(group_name or '').strip()
    try:
        for pos in ('L', 'C', 'R'):
            slot = (gs.stage or {}).get(pos)
            if not slot or not getattr(slot, 'cardnumber', ''):
                return False
            ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
            if not ci or _is_live_ci(ci):
                return False
            if tag and not _ci_matches_group_or_unit(ci, tag):
                return False
            nm = str(getattr(ci, 'name', '') or getattr(ci, 'cardname', '') or getattr(ci, 'title', '') or getattr(slot, 'cardnumber', '') or '').strip()
            if not nm or nm in names:
                return False
            names.add(nm)
        return len(names) == 3
    except Exception:
        return False

def _heart_color_keys_to_jp(colors: List[str]) -> str:
    mp = {'pink':'桃', 'red':'赤', 'yellow':'黄', 'green':'緑', 'blue':'青', 'purple':'紫'}
    return '、'.join(mp.get(str(c), str(c)) for c in list(colors or []))

def _own_success_zone_score_sum(gs: 'GameState', cards_db: Dict[str, CardInfo]) -> int:
    """Return the effective score sum for own success live-card storage."""
    # Prefer the existing shared success-zone score helper so printed score and
    # future success-zone score modifiers are interpreted consistently.
    try:
        fn = globals().get('_success_zone_score_sum')
        if callable(fn) and fn is not _own_success_zone_score_sum:
            return int(fn(gs, cards_db) or 0)
    except Exception:
        pass
    total = 0
    try:
        for cn in list(getattr(gs, 'success_zone', []) or []):
            ci = _get_card(cards_db, cn)
            if not ci:
                continue
            try:
                total += int(getattr(ci, 'score', 0) or 0)
            except Exception:
                pass
    except Exception:
        pass
    return int(total)


def _success_score_sum_gte_from_blob(blob: str) -> int:
    """Parse threshold N from own success-zone score-sum >= N body/condition text."""
    try:
        b = _norm_digits_jp(str(blob or '')).replace(' ', '').replace('\n', '')
        m = re.search(r'自分の成功ライブカード置き場にあるカードのスコア(?:の)?合計が(\d+)以上', b)
        return int(m.group(1)) if m else 0
    except Exception:
        return 0

def _success_score_sum_condition_met(gs: 'GameState', cards_db: Dict[str, CardInfo], threshold: int) -> bool:
    try:
        return int(_own_success_zone_score_sum(gs, cards_db) or 0) >= int(threshold or 0)
    except Exception:
        return False

def _body_always_success_score_cost_bonus(ci: Optional[CardInfo], blob: str) -> int:
    """Parse BODY 常時: success-zone score sum >= N -> this member cost +M."""
    try:
        b = _norm_digits_jp(str(blob or '')).replace(' ', '').replace('\n', '')
        if '自分の成功ライブカード置き場にあるカードのスコア' not in b:
            return 0
        if 'このメンバーのコストを+' not in b:
            return 0
        m = re.search(r'このメンバーのコストを\+(\d+)する', b)
        return int(m.group(1)) if m else 0
    except Exception:
        return 0

def _body_always_success_score_heart_bonus_from_blob(blob: str) -> Dict[str, int]:
    """Parse BODY 常時: success-zone score sum >= N -> gain colored hearts.

    Currently used by PL!-bp5-008: <黄><黄>.
    """
    out: Dict[str, int] = {}
    try:
        b = _norm_digits_jp(str(blob or '')).replace(' ', '').replace('\n', '')
        if '自分の成功ライブカード置き場にあるカードのスコア' not in b:
            return {}
        col_map = {'桃': 'pink', '赤': 'red', '黄': 'yellow', '緑': 'green', '青': 'blue', '紫': 'purple', 'ALL': 'all'}
        # Match both <黄> and <(黄)> forms.
        for token in re.findall(r'<(?:\(([^)]+)\)|([^>]+))>', b):
            raw = str(token[0] or token[1] or '').strip()
            key = col_map.get(raw, '')
            if key:
                out[key] = int(out.get(key, 0) or 0) + 1
    except Exception:
        return {}
    return {k: int(v) for k, v in out.items() if int(v or 0) > 0}


def _body_always_success_count_cost_bonus_from_blob(blob: str, success_count: int) -> int:
    """Parse BODY 常時: success-zone card count -> this member cost +N per card."""
    try:
        b = _norm_digits_jp(str(blob or '')).replace(' ', '').replace('\n', '')
        if '自分の成功ライブカード置き場にあるカード1枚につき' not in b:
            return 0
        if 'このメンバーのコストを+' not in b and 'ステージにいるこのメンバーのコストを+' not in b:
            return 0
        m = re.search(r'(?:ステージにいる)?このメンバーのコストを\+(\d+)する', b)
        if not m:
            return 0
        return int(m.group(1) or 0) * max(0, int(success_count or 0))
    except Exception:
        return 0

def _body_always_success_group_hand_cost_reduction_from_blob(gs: 'GameState', cards_db: Dict[str, CardInfo], blob: str) -> int:
    """Parse BODY 常時: hand member cost reduction if success zone has a group/unit card."""
    try:
        b = _norm_digits_jp(str(blob or '')).replace(' ', '').replace('\n', '')
        m = re.search(r"自分の成功ライブカード置き場に『([^』]+)』のカードがある場合、手札にあるこのメンバーカードのコストは(\d+)減る", b)
        if not m:
            return 0
        tag = str(m.group(1) or '').strip()
        red = int(m.group(2) or 0)
        if not tag or red <= 0:
            return 0
        if _success_has_group_or_unit(gs, cards_db, tag):
            return red
        return 0
    except Exception:
        return 0

def _success_has_group_or_unit(gs: 'GameState', cards_db: Dict[str, CardInfo], tag: str) -> bool:
    tag = str(tag or '').strip()
    tag_compact = tag.replace(' ', '').replace('　', '')
    if not tag:
        return False
    for cn in list(getattr(gs, 'success_zone', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        group = str(getattr(ci, 'group', '') or '')
        unit = str(getattr(ci, 'unit', '') or '')
        group_compact = group.replace(' ', '').replace('　', '')
        unit_compact = unit.replace(' ', '').replace('　', '')
        if tag in group or tag in unit or tag_compact in group_compact or tag_compact in unit_compact:
            return True
    return False

def _stage_has_other_group_or_unit_member(gs: 'GameState', cards_db: Dict[str, CardInfo], src_pos: str, tag: str) -> bool:
    tag = str(tag or '').strip()
    src_pos = str(src_pos or '').upper()
    if not tag:
        return False
    for pos, slot in (getattr(gs, 'stage', {}) or {}).items():
        if str(pos or '').upper() == src_pos:
            continue
        if not slot or not getattr(slot, 'cardnumber', ''):
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci or _is_live_ci(ci):
            continue
        group = str(getattr(ci, 'group', '') or '')
        unit = str(getattr(ci, 'unit', '') or '')
        tag_compact = tag.replace(' ', '').replace('　', '')
        group_compact = group.replace(' ', '').replace('　', '')
        unit_compact = unit.replace(' ', '').replace('　', '')
        if tag in group or tag in unit or tag_compact in group_compact or tag_compact in unit_compact:
            return True
    return False

def _card_effective_play_cost_from_hand(gs: 'GameState', cards_db: Dict[str, CardInfo], cn: str) -> int:
    """Return current play cost for a MEMBER card in hand, including BODY hand modifiers."""
    ci = _get_card(cards_db, cn)
    if not ci:
        return 0
    base = int(getattr(ci, 'cost', 0) or 0)
    if not _is_member_ci(ci):
        return base
    reduction = 0
    for _eff, blob in _iter_body_always_effects(ci):
        reduction += int(_body_always_success_group_hand_cost_reduction_from_blob(gs, cards_db, blob) or 0)
    return max(0, int(base) - int(reduction or 0))

def _activated_success_count_discard_cost_reduction(effect_text: str, success_count: int) -> int:
    """Return hand-discard cost reduction from success-zone count in an activated effect."""
    try:
        t = _norm_digits_jp(_normalize_icon_token_text(str(effect_text or '')).replace('\n', '')).replace(' ', '')
        if 'この能力を起動するためのコストは' not in t:
            return 0
        if '自分の成功ライブカード置き場にあるカード1枚につき' not in t:
            return 0
        if '控え室に置く手札の数が1枚減る' not in t:
            return 0
        return max(0, int(success_count or 0))
    except Exception:
        return 0

def _strip_activated_success_count_discard_cost_reduction(effect_text: str) -> str:
    """Remove activation cost-reduction sentence before resolving the actual effect."""
    try:
        t = _normalize_icon_token_text(str(effect_text or '').strip()).replace('\n', '')
        t = re.sub(r'この能力を起動するためのコストは、自分の成功ライブカード置き場にあるカード1枚につき、控え室に置く手札の数が1枚減る。?', '', t).strip()
        return t
    except Exception:
        return str(effect_text or '').strip()

def _slot_effective_cost(gs: 'GameState', cards_db: Dict[str, CardInfo], pos: str, slot) -> int:
    """Return current cost including supported BODY always cost modifiers."""
    try:
        if not slot or not getattr(slot, 'cardnumber', ''):
            return 0
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci or _is_live_ci(ci):
            return 0
        base = int(getattr(ci, 'cost', 0) or 0)
        bonus = 0
        success_count = len(list(getattr(gs, 'success_zone', []) or []))
        for _eff, blob in _iter_body_always_effects(ci):
            try:
                thr = _success_score_sum_gte_from_blob(blob)
                if thr and _success_score_sum_condition_met(gs, cards_db, thr):
                    bonus += int(_body_always_success_score_cost_bonus(ci, blob) or 0)
                # BODY 常時: success-zone card count based current cost.
                bonus += int(_body_always_success_count_cost_bonus_from_blob(blob, success_count) or 0)
            except Exception:
                pass
        try:
            bonus += int(getattr(slot, 'temp_cost', 0) or 0)
        except Exception:
            pass
        return int(base + bonus)
    except Exception:
        return 0

def _activated_success_score_sum_condition(effect_text: str) -> int:
    """Parse 起動効果 condition: この能力は、成功ライブ置き場スコア合計N以上の場合のみ起動できる。"""
    try:
        t = _norm_digits_jp(_normalize_icon_token_text(str(effect_text or '')).replace('\n', '')).replace(' ', '')
        if 'この能力は' not in t or '場合のみ起動できる' not in t:
            return 0
        m = re.search(r'自分の成功ライブカード置き場にあるカードのスコア(?:の)?合計が(\d+)以上の場合のみ起動できる', t)
        return int(m.group(1)) if m else 0
    except Exception:
        return 0

def _strip_activated_success_score_sum_condition(effect_text: str) -> str:
    """Remove activation-only condition sentence before applying the inner effect."""
    try:
        t = _normalize_icon_token_text(str(effect_text or '').strip()).replace('\n', '')
        t = re.sub(r'この能力は、自分の成功ライブカード置き場にあるカードのスコア(?:の)?合計が\d+以上の場合のみ起動できる。?$', '', t).strip()
        return t
    except Exception:
        return str(effect_text or '').strip()

def _own_success_zone_count_with_score_tag_and_group(gs: 'GameState', cards_db: Dict[str, CardInfo], group_name: str = '') -> int:
    """Count own success-zone cards with a score+1 blade-heart tag and optional group."""
    n = 0
    group_name = str(group_name or '').strip()
    try:
        for cn in list(getattr(gs, 'success_zone', []) or []):
            ci = _get_card(cards_db, cn)
            if not ci:
                continue
            if group_name and group_name not in str(getattr(ci, 'group', '') or ''):
                continue
            if _ci_blade_heart_has_tag(ci, '<スコア+1>'):
                n += 1
    except Exception:
        pass
    return int(n)

def _grant_source_live_total_score_until_end(gs: 'GameState', ctx: Dict[str, Any], n: int, label: str = '') -> bool:
    """Grant temp live-total score bonus to the source stage slot."""
    pos = str((ctx or {}).get('pos', '') or '').upper()
    slot = gs.stage.get(pos) if pos in ('L', 'C', 'R') else None
    if not slot:
        gs.log.append(f'[WARN] {label or "success-zone score condition"}: no source slot for live total score +{int(n or 0)}')
        return False
    try:
        slot.temp_score = int(getattr(slot, 'temp_score', 0) or 0) + int(n or 0)
        slot.temp_until = 'end_of_live'
    except Exception:
        return False
    gs.log.append(f'[AUTO] {pos}: {label or "success-zone score condition"} -> live total score +{int(n or 0)} until end_of_live')
    return True

def _count_yell_revealed_live_cards_with_tag(gs: GameState, cards_db: Dict[str, CardInfo], tag_text: str) -> int:
    tag = _normalize_tag_marker(tag_text)
    if not tag:
        return 0
    n = 0
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci or not _is_live_ci(ci):
            continue
        if _ci_blade_heart_has_tag(ci, tag):
            n += 1
    return int(n)

def _count_yell_revealed_group_live_cards_with_tag(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str, tag_text: str) -> int:
    """Count YELL-revealed LIVE cards that match group/unit text and have the given blade-heart tag."""
    tag = _normalize_tag_marker(tag_text)
    group_name = str(group_name or '').strip()
    if not tag:
        return 0
    n = 0
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci or not _is_live_ci(ci):
            continue
        if group_name and (group_name not in str(getattr(ci, 'group', '') or '')) and (group_name not in str(getattr(ci, 'unit', '') or '')):
            continue
        if _ci_blade_heart_has_tag(ci, tag):
            n += 1
    return int(n)

def _ci_blade_heart_score_icon_bonus(ci: Optional[CardInfo]) -> int:
    """Return the score bonus from score-up blade-heart icons on a revealed card.

    Rule 8.4.2.1 adds +1 to live total score for each score icon revealed by YELL.
    Official text may be stored as <スコア+1>, <(スコア+1)>, or split <(スコア)+1>.
    """
    try:
        txt = _ci_blade_heart_raw_text(ci)
        total = 0
        for inner in re.findall(r'<\(([^)]+)\)>', txt):
            key = str(inner or '').strip().replace('＋', '+').replace(' ', '')
            m = re.match(r'^スコア([+\-]\d+)$', key)
            if m:
                total += int(m.group(1))
        return int(total)
    except Exception:
        return 0

def _yell_revealed_score_icon_bonus(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    """Total score icon bonus from this live's YELL-revealed cards."""
    total = 0
    try:
        for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
            ci = _get_card(cards_db, cn)
            if not ci:
                continue
            total += int(_ci_blade_heart_score_icon_bonus(ci) or 0)
    except Exception:
        pass
    return int(total)

def _stage_has_all_distinct_group_members(gs: 'GameState', cards_db: Dict[str, CardInfo], tag: str) -> bool:
    """Return True if all three stage areas are occupied by members matching tag (group or unit) with distinct names."""
    names = []
    want = str(tag or '')
    try:
        for pos in ('L', 'C', 'R'):
            slot = (gs.stage or {}).get(pos)
            if not slot or not getattr(slot, 'cardnumber', ''):
                return False
            ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
            if not ci or _is_live_ci(ci):
                return False
            g = str(getattr(ci, 'group', '') or '')
            u = str(getattr(ci, 'unit', '') or '')
            if want and (want not in g) and (want not in u):
                return False
            nm = str(getattr(ci, 'name', '') or getattr(ci, 'cardname', '') or '')
            if not nm:
                return False
            names.append(nm)
        return len(set(names)) == 3
    except Exception:
        return False

def _live_has_trigger_ability(ci: Optional[CardInfo], trig_text: str) -> bool:
    if not ci or not getattr(ci, 'abilities', None):
        return False
    want = str(trig_text or '')
    for ab in (getattr(ci, 'abilities', None) or []):
        if not isinstance(ab, dict):
            continue
        trig = str(ab.get('trigger', '') or '')
        if want and want in trig:
            return True
    return False
def _live_has_start_or_success_ability(ci: Optional[CardInfo]) -> bool:
    try:
        return _live_has_trigger_ability(ci, 'ライブ開始時') or _live_has_trigger_ability(ci, 'ライブ成功時')
    except Exception:
        return False

def _quoted_tag(blob: str) -> str:
    try:
        m = re.search(r'『([^』]+)』', str(blob or ''))
        return str(m.group(1) if m else '')
    except Exception:
        return ''

def _slot_matches_group_tag(ci: Optional[CardInfo], tag: str) -> bool:
    if not ci:
        return False
    want = str(tag or '')
    if not want:
        return False
    g = str(getattr(ci, 'group', '') or '')
    u = str(getattr(ci, 'unit', '') or '')
    return (want in g) or (want in u)

def _iter_body_always_effects(ci: Optional[CardInfo]):
    if not ci or not getattr(ci, 'abilities', None):
        return
    for ab in (getattr(ci, 'abilities', None) or []):
        if not isinstance(ab, dict):
            continue
        at = str(ab.get('ability_type', '') or '')
        if '常時' not in at:
            continue
        for cl in (ab.get('clauses', []) or []):
            if not isinstance(cl, dict):
                continue
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '')
            blob = _norm_digits_jp(eff).replace('＋', '+').replace(' ', '').replace('\n', '')
            yield eff, blob
def _slot_always_hearts_bonus(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, slot) -> Dict[str, int]:
    """Return always-on heart bonus currently attached to a stage slot."""
    try:
        if not slot or not getattr(slot, 'cardnumber', ''):
            return {}
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci or _is_live_ci(ci):
            return {}
        bonus: Dict[str, int] = {}
        for _eff, blob in _iter_body_always_effects(ci):
            try:
                # 常時 BODY: 相手のステージにいるウェイト状態のメンバー1人につき、<色>を得る。
                # Example: PL!-pb1-002 絢瀬絵里 -> opponent_wait_count 分の <紫>。
                # The opponent board itself is not modeled, so this uses the manual/UI counter.
                if ('相手のステージにいるウェイト状態のメンバー1人につき' in blob and 'を得る' in blob):
                    n_wait = int(_opponent_wait_count(gs) or 0)
                    if n_wait > 0:
                        hb_opp = _parse_heart_icons(blob)
                        for hk, hv in (hb_opp or {}).items():
                            bonus[hk] = int(bonus.get(hk, 0) or 0) + int(hv or 0) * n_wait
                    continue
                if ('ライブ開始時能力も' in blob and 'ライブ成功時能力も' in blob and '持たないカードがあるかぎり' in blob and blob.count('<(紫)>') >= 2):
                    found_plain_live = False
                    for cn_live in list(getattr(gs, 'set_zone', []) or []):
                        ci_live = _get_card(cards_db, cn_live)
                        if not ci_live or not _is_live_ci(ci_live):
                            continue
                        if not _live_has_start_or_success_ability(ci_live):
                            found_plain_live = True
                            break
                    if found_plain_live:
                        bonus['purple'] = int(bonus.get('purple', 0) or 0) + int(blob.count('<(紫)>'))
                elif ('自分のライブ中のカードが' in blob and 'その中に『' in blob and 'のライブカードを1枚以上含む場合' in blob and '<(ALL)>' in blob):
                    m = re.search(r'自分のライブ中のカードが(\d+)枚以上', blob)
                    need = int(m.group(1)) if m else 0
                    tag = _quoted_tag(blob)
                    live_cards = list(getattr(gs, 'set_zone', []) or [])
                    if len(live_cards) >= need:
                        has_group_live = False
                        for cn_live in live_cards:
                            ci_live = _get_card(cards_db, cn_live)
                            if ci_live and _is_live_ci(ci_live) and _slot_matches_group_tag(ci_live, tag):
                                has_group_live = True
                                break
                        if has_group_live:
                            bonus['all'] = int(bonus.get('all', 0) or 0) + int(blob.count('<(ALL)>'))
                else:
                    thr = int(_success_score_sum_gte_from_blob(blob) or 0)
                    if thr and _success_score_sum_condition_met(gs, cards_db, thr):
                        hb = _body_always_success_score_heart_bonus_from_blob(blob)
                        for hk, hv in (hb or {}).items():
                            bonus[hk] = int(bonus.get(hk, 0) or 0) + int(hv or 0)
            except Exception:
                pass
        return {str(k): int(v) for k, v in bonus.items() if int(v or 0) != 0}
    except Exception:
        return {}

def _success_zone_live_body_always_blade_bonus_for_slot(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, slot, c_slot: Optional[CardInfo]) -> int:
    """Return blade bonus granted by BODY-always effects of LIVE cards currently in success_zone.

    Generalizes former Love wing bell handling:
      このカードが自分の成功ライブカード置き場にあるかぎり、自分のセンターエリアにいる『X』のメンバーは<(ブレード)>を得る。
    The function scans success-zone LIVE cards and applies any matching generic pattern to the queried stage slot.
    """
    try:
        if not slot or not getattr(slot, 'cardnumber', '') or not c_slot:
            return 0
        if pos != 'C':
            return 0
        total = 0
        for cn_live in list(getattr(gs, 'success_zone', []) or []):
            ci_live = _get_card(cards_db, cn_live)
            if not ci_live or not _is_live_ci(ci_live):
                continue
            for _eff, blob in _iter_body_always_effects(ci_live):
                try:
                    if 'このカードが自分の成功ライブカード置き場にあるかぎり' not in blob:
                        continue
                    if '自分のセンターエリアにいる『' not in blob or 'のメンバーは' not in blob or 'ブレード' not in blob:
                        continue
                    tag = _quoted_tag(blob)
                    if tag and _slot_matches_group_tag(c_slot, tag):
                        total += int(_count_blade_icons_from_tagblob(blob))
                except Exception:
                    pass
        return int(total)
    except Exception:
        return 0

def _slot_always_score_bonus(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, slot) -> int:
    """Return always-on total score bonus granted by a stage member slot."""
    try:
        if not slot or not getattr(slot, 'cardnumber', ''):
            return 0
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci or _is_live_ci(ci):
            return 0
        bonus = int(getattr(slot, 'temp_score', 0) or 0)
        for _eff, blob in _iter_body_always_effects(ci):
            try:
                # Do not treat BODY effects that *grant a <ライブ成功時> ability* as an
                # always-on score bonus.  Example: PL!S-bp2-008 小原鞠莉 grants
                # a live-success ability that may later add live total score +1/+2;
                # applying +1 here pre-resolves the gained ability and causes a
                # duplicate bonus when the queued success trigger resolves.
                if '<ライブ成功時>' in blob or 'ライブ成功時' in blob:
                    continue
                if 'エリアすべてに『' in blob and 'のメンバーが登場しており、かつ名前が異なる場合' in blob and 'ライブの合計スコアを+1する' in blob:
                    tag = _quoted_tag(blob)
                    if _stage_has_all_distinct_group_members(gs, cards_db, tag):
                        bonus += 1
                elif '相手の成功ライブカード置き場にあるカードのスコアの合計が' in blob and 'ライブの合計スコアを+1する' in blob:
                    m = re.search(r'相手の成功ライブカード置き場にあるカードのスコアの合計が(\d+)以上', blob)
                    need = int(m.group(1)) if m else 0
                    if need and _opponent_success_score_sum(gs) >= need:
                        bonus += 1
            except Exception:
                pass
        return int(bonus)
    except Exception:
        return 0
def _has_body_always_2member_blade_heart(ci: Optional[CardInfo]) -> bool:
    """Return True if the card has a 常時(BODY) ability that grants blue heart +1 and blade +1
    when exactly 2 members are on stage.
    Matches PL!N-PR-020 / PL!S-PR-037 effect:
      <常時> 自分のステージにいるメンバーがちょうど2人であるかぎり、<(青)><(ブレード)>を得る。
    """
    if not ci or not getattr(ci, 'abilities', None):
        return False
    for ab in ci.abilities:
        if not isinstance(ab, dict):
            continue
        at = str(ab.get('ability_type', '') or '')
        if '常時' not in at:
            continue
        for cl in (ab.get('clauses', []) or []):
            if not isinstance(cl, dict):
                continue
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '')
            if 'ちょうど2人' in eff and 'アクティブ' not in eff and '<(青)>' in eff and 'ブレード' in eff:
                return True
    return False
def _stage_member_count(gs: 'GameState', cards_db: Dict[str, CardInfo]) -> int:
    """Return number of MEMBER-type slots on stage (excluding LIVE-type)."""
    n = 0
    for slot in (gs.stage or {}).values():
        if not slot or not getattr(slot, 'cardnumber', ''):
            continue
        ci = _get_card(cards_db, slot.cardnumber)
        if ci and _is_live_ci(ci):
            continue
        n += 1
    return int(n)

def _opponent_success_score_sum_known(gs: 'GameState') -> bool:
    try:
        return int(getattr(gs, 'opponent_success_score_sum', -1) or -1) >= 0
    except Exception:
        return False

def _opponent_success_score_sum(gs: 'GameState') -> int:
    try:
        return int(getattr(gs, 'opponent_success_score_sum', -1) or -1)
    except Exception:
        return -1

def _slot_always_blade_bonus(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, slot) -> int:
    """Return generic always/success-zone derived blade bonus currently attached to a stage slot.
    This centralizes UI-visible per-slot blade bonuses so server.py does not need
    card-specific patches. Temporary bonuses remain in slot.temp_blade.
    """
    try:
        if not slot or not getattr(slot, 'active', False):
            return 0
        c = _get_card(cards_db, slot.cardnumber)
        if not c:
            return 0
        bonus = 0
        has_cost13 = _stage_has_cost13_plus_member(gs, cards_db)
        if has_cost13 and _has_body_always_cost13_blade_bonus(c):
            bonus += 2
        has_exactly2 = (_stage_member_count(gs, cards_db) == 2)
        if has_exactly2 and _has_body_always_2member_blade_heart(c):
            bonus += 1
        try:
            bonus += int(_success_zone_live_body_always_blade_bonus_for_slot(gs, cards_db, pos, slot, c) or 0)
        except Exception:
            pass
        # Continuous: 相手のステージにいるウェイト状態のメンバー1人につき <(ブレード)> を得る。
        try:
            for _eff0, _blob0 in _iter_body_always_effects(c):
                if ('相手のステージにいるウェイト状態のメンバー1人につき' in str(_blob0 or '') and 'ブレード' in str(_blob0 or '')):
                    bonus += int(_count_blade_icons_from_tagblob(str(_blob0 or '')) or 1) * _opponent_wait_count(gs)
        except Exception:
            pass
        # Continuous: 相手の成功ライブカード置き場枚数が自分より多いかぎり、その差ぶん <(ブレード)> を得る。
        try:
            own_success_n = len(list(getattr(gs, 'success_zone', []) or []))
            opp_success_n = _opponent_success_count(gs)
            diff_success_n = max(0, int(opp_success_n) - int(own_success_n))
            if diff_success_n > 0:
                for _eff0, _blob0 in _iter_body_always_effects(c):
                    btxt = str(_blob0 or '')
                    if ('相手の成功ライブカード置き場にあるカードの枚数が自分より多いかぎり' in btxt and 'その差に等しい数' in btxt and 'ブレード' in btxt):
                        bonus += int(_count_blade_icons_from_tagblob(btxt) or 1) * diff_success_n
        except Exception:
            pass
        if _has_under_energy_blade_bonus(c):
            try:
                bonus += int(getattr(slot, 'energy_under', 0) or 0)
            except Exception:
                pass
        for _eff, blob in _iter_body_always_effects(c):
            try:
                if '成功ライブカード置き場にあるカード1枚につき' in blob and 'ブレード' in blob:
                    bonus += int(_count_blade_icons_from_tagblob(blob)) * len(list(getattr(gs, 'success_zone', []) or []))
                elif '自分の成功ライブカード置き場にあるカードのスコアの合計が相手より高い' in blob and 'ブレード' in blob:
                    opp_sum = _opponent_success_score_sum(gs)
                    if opp_sum >= 0 and int(_own_success_zone_score_sum(gs, cards_db) or 0) > int(opp_sum):
                        bonus += int(_count_blade_icons_from_tagblob(blob))
                elif 'このメンバーよりコストの大きいメンバーがいる場合' in blob and 'ブレード' in blob:
                    try:
                        self_cost = int(_slot_effective_cost(gs, cards_db, pos, slot) or getattr(c, 'cost', 0) or 0)
                    except Exception:
                        self_cost = int(getattr(c, 'cost', 0) or 0)
                    if _stage_has_other_higher_cost_member(gs, cards_db, pos, self_cost):
                        bonus += int(_count_blade_icons_from_tagblob(blob))
                elif 'ほかの『' in blob and 'のメンバー1人につき' in blob and 'ブレード' in blob:
                    tag = _quoted_tag(blob)
                    others = 0
                    for pos2, slot2 in (gs.stage or {}).items():
                        if pos2 == pos or not slot2:
                            continue
                        ci2 = _get_card(cards_db, getattr(slot2, 'cardnumber', '') or '')
                        if not ci2 or _is_live_ci(ci2):
                            continue
                        if _slot_matches_group_tag(ci2, tag):
                            others += 1
                    bonus += int(_count_blade_icons_from_tagblob(blob)) * int(others)
                elif ('自分のライブ中のカードが' in blob and 'その中に『' in blob and 'のライブカードを1枚以上含む場合' in blob and 'ブレード' in blob):
                    m = re.search(r'自分のライブ中のカードが(\d+)枚以上', blob)
                    need = int(m.group(1)) if m else 0
                    tag = _quoted_tag(blob)
                    live_cards = list(getattr(gs, 'set_zone', []) or [])
                    if len(live_cards) >= need:
                        has_group_live = False
                        for cn_live in live_cards:
                            ci_live = _get_card(cards_db, cn_live)
                            if ci_live and _is_live_ci(ci_live) and _slot_matches_group_tag(ci_live, tag):
                                has_group_live = True
                                break
                        if has_group_live:
                            bonus += int(_count_blade_icons_from_tagblob(blob))
            except Exception:
                pass
        return int(bonus)
    except Exception:
        return 0
def stage_blade(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    s = 0
    for pos, slot in gs.stage.items():
        if not slot or not slot.active:
            continue
        c = _get_card(cards_db, slot.cardnumber)
        base_b = (int(c.blade) if c else 0)
        temp_b = int(getattr(slot, "temp_blade", 0) or 0)
        always_b = _slot_always_blade_bonus(gs, cards_db, pos, slot)
        s += base_b + temp_b + always_b
    return s
def _success_zone_cardno_count(gs: "GameState", target_cn: str) -> int:
    if gs is None:
        return 0
    target = _canon_cardno(str(target_cn or ''))
    if not target:
        return 0
    n = 0
    for cn in list(getattr(gs, 'success_zone', []) or []):
        try:
            canon = _canon_cardno(cn)
        except Exception:
            canon = str(cn or '')
        if canon == target:
            n += 1
    return int(n)
def owned_base_hearts(gs: GameState, cards_db: Dict[str, CardInfo]) -> Dict[str, int]:
    pool: Dict[str, int] = {}
    # Check exactly-2-member condition once (PL!N-PR-020 / PL!S-PR-037)
    stage_member_n = _stage_member_count(gs, cards_db)
    has_exactly2 = (stage_member_n == 2)
    for pos, slot in (gs.stage or {}).items():
        if not slot:
            continue
        c = _get_card(cards_db, slot.cardnumber)
        if not c:
            continue
        replace_col = str(getattr(slot, 'heart_replace_color', '') or '').lower().strip()
        if replace_col:
            # 元々持つハートをすべて replace_col に置換（ライブ終了時まで）
            # 合計数を計算して、置換後の色に付与
            orig_total = sum(int(v) for v in (c.base_hearts or {}).values())
            if orig_total > 0:
                pool[replace_col] = pool.get(replace_col, 0) + orig_total
        else:
            for k, v in (c.base_hearts or {}).items():
                pool[k] = pool.get(k, 0) + int(v)
        for k, v in (_slot_always_hearts_bonus(gs, cards_db, pos, slot) or {}).items():
            pool[k] = pool.get(k, 0) + int(v)
        for k, v in (getattr(slot, 'temp_hearts', {}) or {}).items():
            pool[k] = pool.get(k, 0) + int(v)
        # 常時 BODY: ステージのメンバーがちょうど2人のとき、青ハート+1 (PL!N-PR-020 / PL!S-PR-037)
        if has_exactly2 and _has_body_always_2member_blade_heart(c):
            pool['blue'] = pool.get('blue', 0) + 1
    # Live-start buff: gain chosen heart per card in success live storage (until end of live)
    try:
        col = str(getattr(gs, 'success_zone_heart_color', '') or '').lower().strip()
    except Exception:
        col = ''
    if col:
        try:
            n = len(list(getattr(gs, 'success_zone', []) or []))
        except Exception:
            n = 0
        if n > 0:
            pool[col] = pool.get(col, 0) + int(n)
    return pool
def _stage_pos_label(gs: GameState, cards_db: Dict[str, CardInfo], pos: str) -> str:
    pos = str(pos or '').upper()
    slot = (gs.stage or {}).get(pos)
    if not slot or not getattr(slot, 'cardnumber', ''):
        return pos
    ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
    nm = str(getattr(ci, 'cardname', '') or getattr(ci, 'name', '') or getattr(slot, 'cardnumber', '') or '')
    return f"{pos}: {nm}" if nm else pos
def _emma_bp3_008_wait_candidates(gs: GameState, cards_db: Dict[str, CardInfo], src_pos: str) -> List[str]:
    out: List[str] = []
    src_pos = str(src_pos or '').upper()
    for pos in ('L', 'C', 'R'):
        if pos == src_pos:
            continue
        slot = (gs.stage or {}).get(pos)
        if not slot or not bool(getattr(slot, 'active', False)):
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci:
            continue
        if _is_live_ci(ci):
            continue
        if '虹ヶ咲' not in str(getattr(ci, 'group', '') or ''):
            continue
        out.append(pos)
    return out
def _grant_temp_heart(slot: StageSlot, color: str, n: int = 1) -> None:
    color = str(color or '').lower().strip()
    if not color:
        return
    th = dict(getattr(slot, 'temp_hearts', {}) or {})
    th[color] = int(th.get(color, 0) or 0) + int(n or 0)
    slot.temp_hearts = th
    slot.temp_until = 'end_of_live'
def _count_all_from_blade_tags(tags_json: str) -> int:
    try:
        txt = str(tags_json or '')
    except Exception:
        txt = ''
    # tokv1 normalized tags are typically like ["(ALL)", "(DRAW)"]
    return txt.count('(ALL)')
def cheer_hearts_from_resolve(gs: GameState, cards_db: Dict[str, CardInfo]) -> Dict[str, int]:
    pool: Dict[str, int] = {}
    for cn in gs.resolve_zone:
        c = _get_card(cards_db, cn)
        if not c:
            continue
        for k, v in (c.blade_hearts or {}).items():
            pool[k] = pool.get(k, 0) + int(v)
        try:
            txt = str(getattr(c, 'blade_heart_tags_json', '') or '')
        except Exception:
            txt = ''
        n_all = txt.count('(ALL)')
        if n_all > 0:
            pool['all'] = pool.get('all', 0) + int(n_all)
    if bool(getattr(gs, 'vivid_world_blue_mode_this_live', False)):
        pool = _convert_pool_nonblue_plus_any_to_blue(pool)
    return pool
def can_satisfy_req(req: Dict[str, int], owned: Dict[str, int]) -> Tuple[bool, Dict[str, Any]]:
    """Check if owned hearts can satisfy LIVE required hearts.
    Notes:
      - tokv1 uses multiple colors (e.g., blue/pink/purple/red/green/yellow) + 'any'.
      - Previous implementation was hard-coded to (red/green/blue), which misjudged success.
      - We treat any key other than {'any','all'} as a concrete color bucket.
      - 'all' (if present) is treated as a wildcard pool that can satisfy missing colored needs.
    """
    req0 = req or {}
    owned0 = owned or {}
    # normalize keys (lower)
    req_l = {str(k).lower(): int(v or 0) for k, v in req0.items()}
    pool = {str(k).lower(): int(v or 0) for k, v in owned0.items()}
    pool.setdefault("all", 0)
    colors = sorted(set([
        k for k in list(req_l.keys()) + list(pool.keys())
        if k not in ("any", "all")
    ]))
    alloc: Dict[str, Any] = {}
    for c in colors:
        alloc[f"use_{c}"] = 0
    alloc["use_all"] = 0
    # 1) satisfy specific color requirements
    for c in colors:
        need = int(req_l.get(c, 0) or 0)
        if need <= 0:
            continue
        have = int(pool.get(c, 0) or 0)
        take = min(have, need)
        alloc[f"use_{c}"] += take
        pool[c] = have - take
        need -= take
        if need > 0:
            # use wildcard pool if available
            if pool.get("all", 0) < need:
                return (False, {
                    "reason": f"lack {c} (and ALL)",
                    "need": need,
                    "pool_all": int(pool.get("all", 0) or 0),
                    "pool_color": int(pool.get(c, 0) or 0),
                })
            alloc["use_all"] += need
            pool["all"] -= need
    # 2) satisfy "any" requirement using remaining hearts
    need_any = int(req_l.get("any", 0) or 0)
    if need_any > 0:
        total = int(pool.get("all", 0) or 0) + sum(int(pool.get(c, 0) or 0) for c in colors)
        if total < need_any:
            return (False, {"reason": "lack total hearts", "need_any": need_any, "pool_total": total})
        # consume from largest piles first
        buckets = list(colors) + ["all"]
        buckets.sort(key=lambda kk: int(pool.get(kk, 0) or 0), reverse=True)
        for k in buckets:
            if need_any <= 0:
                break
            have = int(pool.get(k, 0) or 0)
            if have <= 0:
                continue
            take = min(have, need_any)
            pool[k] = have - take
            need_any -= take
            if k == "all":
                alloc["use_all"] += take
            else:
                alloc[f"use_{k}"] = int(alloc.get(f"use_{k}", 0) or 0) + take
    return (True, alloc)
def _apply_alloc_to_pool(alloc: Dict[str, Any], pool: Dict[str, int]) -> None:
    """Consume hearts from pool in-place using alloc returned by can_satisfy_req / solver."""
    if not alloc or not pool:
        return
    # alloc keys are like use_blue, use_purple, use_all
    for k, v in list(alloc.items()):
        if not k.startswith("use_"):
            continue
        try:
            take = int(v or 0)
        except Exception:
            take = 0
        if take <= 0:
            continue
        col = k[len("use_"):]
        if col not in pool:
            pool[col] = 0
        pool[col] = max(0, int(pool.get(col, 0) or 0) - take)
def _enumerate_allocations_for_req(req: Dict[str, int], pool_in: Dict[str, int], colors: List[str]) -> List[Tuple[Dict[str, Any], Dict[str, int]]]:
    """Enumerate (alloc, pool_after) pairs that satisfy req using pool_in.
    This is used to solve multi-LIVE success correctly: when multiple LIVE cards are set,
    the same owned-heart pool must be allocated across all of them without reusing icons.
    """
    req0 = req or {}
    pool0 = pool_in or {}
    req_l = {str(k).lower(): int(v or 0) for k, v in req0.items()}
    pool = {str(k).lower(): int(v or 0) for k, v in pool0.items()}
    pool.setdefault("all", 0)
    for c in colors:
        pool.setdefault(c, 0)
    fixed_need = {c: int(req_l.get(c, 0) or 0) for c in colors}
    need_any0 = int(req_l.get("any", 0) or 0)
    # quick impossible check by total icons
    total_pool = int(pool.get("all", 0) or 0) + sum(int(pool.get(c, 0) or 0) for c in colors)
    total_need = sum(int(v or 0) for v in fixed_need.values()) + int(need_any0 or 0)
    if total_pool < total_need:
        return []
    # helper to compute minimum ALL needed for remaining fixed colors
    def min_all_needed(rem_colors: List[str], pool_now: Dict[str, int]) -> int:
        need = 0
        for cc in rem_colors:
            n = int(fixed_need.get(cc, 0) or 0)
            have = int(pool_now.get(cc, 0) or 0)
            if n > have:
                need += (n - have)
        return need
    out: List[Tuple[Dict[str, Any], Dict[str, int]]] = []
    # recursion over fixed color requirements (using color + ALL)
    def rec_fixed(i: int, pool_now: Dict[str, int], alloc_now: Dict[str, Any]) -> None:
        if i >= len(colors):
            # allocate ANY using remaining pool
            need_any = int(need_any0 or 0)
            if need_any <= 0:
                out.append((dict(alloc_now), dict(pool_now)))
                return
            cats = list(colors) + ["all"]  # consume ALL last by default
            # prune
            tot = int(pool_now.get("all", 0) or 0) + sum(int(pool_now.get(c, 0) or 0) for c in colors)
            if tot < need_any:
                return
            def rec_any(j: int, need_left: int, pool2: Dict[str, int], alloc2: Dict[str, Any]) -> None:
                if need_left <= 0:
                    out.append((dict(alloc2), dict(pool2)))
                    return
                if j >= len(cats):
                    return
                cat = cats[j]
                have = int(pool2.get(cat, 0) or 0)
                if have <= 0:
                    rec_any(j + 1, need_left, pool2, alloc2)
                    return
                max_take = min(have, need_left)
                # deterministic enumeration:
                # - for color buckets, try consuming more first (avoid spending ALL if possible)
                # - for ALL bucket, try consuming less first (preserve flexibility)
                if cat == "all":
                    take_range = range(0, max_take + 1)
                else:
                    take_range = range(max_take, -1, -1)
                for take in take_range:
                    if take <= 0:
                        rec_any(j + 1, need_left, pool2, alloc2)
                        continue
                    pool3 = dict(pool2)
                    pool3[cat] = have - take
                    alloc3 = dict(alloc2)
                    if cat == "all":
                        alloc3["use_all"] = int(alloc3.get("use_all", 0) or 0) + take
                    else:
                        k = f"use_{cat}"
                        alloc3[k] = int(alloc3.get(k, 0) or 0) + take
                    rec_any(j + 1, need_left - take, pool3, alloc3)
            rec_any(0, need_any, dict(pool_now), dict(alloc_now))
            return
        c = colors[i]
        need = int(fixed_need.get(c, 0) or 0)
        if need <= 0:
            rec_fixed(i + 1, pool_now, alloc_now)
            return
        have_c = int(pool_now.get(c, 0) or 0)
        have_all = int(pool_now.get("all", 0) or 0)
        # We'll enumerate using as many colored hearts as possible first (minimize ALL usage).
        # use_from_color in [0..min(need,have_c)]
        for use_c in range(min(need, have_c), -1, -1):
            use_all = need - use_c
            if use_all > have_all:
                continue
            pool_next = dict(pool_now)
            pool_next[c] = have_c - use_c
            pool_next["all"] = have_all - use_all
            # prune: ensure remaining ALL can cover remaining fixed shortfalls
            rem_cols = colors[i + 1:]
            if pool_next.get("all", 0) < min_all_needed(rem_cols, pool_next):
                continue
            alloc_next = dict(alloc_now)
            if use_c > 0:
                k = f"use_{c}"
                alloc_next[k] = int(alloc_next.get(k, 0) or 0) + use_c
            if use_all > 0:
                alloc_next["use_all"] = int(alloc_next.get("use_all", 0) or 0) + use_all
            rec_fixed(i + 1, pool_next, alloc_next)
    # init alloc with explicit keys for stable logging
    alloc_init: Dict[str, Any] = {}
    for c in colors:
        alloc_init[f"use_{c}"] = 0
    alloc_init["use_all"] = 0
    # initial prune
    if pool.get("all", 0) < min_all_needed(colors, pool):
        return []
    rec_fixed(0, dict(pool), alloc_init)
    # de-duplicate identical resulting pools by keeping the first alloc (deterministic)
    seen = set()
    uniq: List[Tuple[Dict[str, Any], Dict[str, int]]] = []
    for alloc, pool_after in out:
        key = tuple(int(pool_after.get(c, 0) or 0) for c in colors) + (int(pool_after.get("all", 0) or 0),)
        if key in seen:
            continue
        seen.add(key)
        uniq.append((alloc, pool_after))
    return uniq
def _solve_multi_live_allocations(lives: List[str], cards_db: Dict[str, CardInfo], owned: Dict[str, int], live_set_indices: Optional[List[int]] = None) -> Tuple[bool, Dict[str, Dict[str, Any]]]:
    """Find allocations for ALL live cards without reusing hearts.
    Returns:
      ok_all, alloc_map[cn] = alloc dict (use_* keys).
    """
    lives = list(lives or [])
    live_set_indices = list(live_set_indices or [])
    pool0 = {str(k).lower(): int(v or 0) for k, v in (owned or {}).items()}
    pool0.setdefault("all", 0)
    # prefer canonical color order for deterministic state keys
    canon = ["pink", "red", "yellow", "green", "blue", "purple"]
    # include any extra keys that may appear (should be none, but safe)
    extra = sorted([k for k in pool0.keys() if k not in ("any", "all") and k not in canon])
    colors = [c for c in canon if (c in pool0)] + extra
    # Also include any colors that appear only in req (rare, but safe)
    for _i, cn in enumerate(lives):
        c = _get_card(cards_db, cn)
        _set_idx = live_set_indices[_i] if _i < len(live_set_indices) else None
        req = _effective_live_required_hearts(cn, c, globals().get('_CURRENT_GS_FOR_ATTEMPT'), cards_db, set_idx=_set_idx)
        for k in req.keys():
            kk = str(k).lower()
            if kk in ("any", "all"):
                continue
            if kk not in colors:
                colors.append(kk)
                pool0.setdefault(kk, 0)
    # normalize pool keys present in colors
    for c in colors:
        pool0.setdefault(c, 0)
    # prepare req list
    reqs = []
    for _i, cn in enumerate(lives):
        ci = _get_card(cards_db, cn)
        _set_idx = live_set_indices[_i] if _i < len(live_set_indices) else None
        reqs.append((cn, _set_idx, _effective_live_required_hearts(cn, ci, globals().get('_CURRENT_GS_FOR_ATTEMPT'), cards_db, set_idx=_set_idx)))
    # try permutations of live card processing order to find any satisfiable plan
    import itertools
    for perm in itertools.permutations(reqs, len(reqs)):
        memo = set()
        def pool_key(pool: Dict[str, int], i: int) -> Tuple[Any, ...]:
            return (i,) + tuple(int(pool.get(c, 0) or 0) for c in colors) + (int(pool.get("all", 0) or 0),)
        def dfs(i: int, pool_now: Dict[str, int], plan: List[Tuple[str, Dict[str, Any]]]) -> Optional[List[Tuple[str, Dict[str, Any]]]]:
            key = pool_key(pool_now, i)
            if key in memo:
                return None
            if i >= len(perm):
                return list(plan)
            cn, _set_idx, req = perm[i]
            options = _enumerate_allocations_for_req(req, pool_now, colors)
            for alloc, pool_after in options:
                plan.append((cn, alloc))
                res = dfs(i + 1, pool_after, plan)
                if res is not None:
                    return res
                plan.pop()
            memo.add(key)
            return None
        res_plan = dfs(0, dict(pool0), [])
        if res_plan is not None:
            alloc_map = {cn: alloc for cn, alloc in res_plan}
            return True, alloc_map
    return False, {}
def _count_blade_icons(text: str) -> int:
    t = text or ""
    n = len(re.findall(r'<(?:\(ブレード\)|ブレード)>', t))
    if n > 0:
        return n
    if "ブレードを一本" in t or "ブレードを1本" in t:
        return 1
    if "ブレードを二本" in t or "ブレードを2本" in t:
        return 2
    return 0
def _has_sacrifice_ability(ci: Optional[CardInfo]) -> bool:
    if not ci or not ci.abilities:
        return False
    for ab in ci.abilities:
        if not isinstance(ab, dict):
            continue
        at = str(ab.get("ability_type", "") or "")
        if "起動" not in at:
            continue
        clauses = ab.get("clauses", [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            raw = str(cl.get("raw", "") or "")
            eff = str(cl.get("effect_template", "") or "")
            cost = str(cl.get("cost_template", "") or "")
            blob = " ".join([raw, cost, eff])
            if ("控え室" in blob) and ("置く" in blob) and ("このメンバー" in blob):
                return True
    return False
def _has_green_member_take_ability(ci: Optional[CardInfo]) -> bool:
    """Detect activated abilities that move this member to green room and take 1 MEMBER from green room to hand.
    Generalized from the former PL!N-sd1-006 special-case.
    """
    if not ci or not ci.abilities:
        return False
    for ab in ci.abilities:
        if not isinstance(ab, dict):
            continue
        at = str(ab.get("ability_type", "") or "")
        if "起動" not in at:
            continue
        clauses = ab.get("clauses", [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            raw = str(cl.get("raw", "") or "")
            eff = str(cl.get("effect_template", "") or "")
            cost = str(cl.get("cost_template", "") or "")
            blob = " ".join([raw, cost, eff])
            # examples:
            # 「このメンバーをステージから控え室に置く：自分の控え室からメンバーカードを1枚手札に加える。」
            if ("このメンバー" in blob) and ("ステージから控え室に置" in blob or "控え室に置く" in blob):
                if ("控え室" in blob) and ("メンバー" in blob) and ("手札" in blob) and ("加える" in blob or "戻" in blob):
                    return True
    return False
def _has_green_live_take_ability(ci: Optional[CardInfo]) -> bool:
    """Detect 'put this member to green room' style activated ability that also takes 1 LIVE from green room to hand."""
    if not ci or not ci.abilities:
        return False
    for ab in ci.abilities:
        if not isinstance(ab, dict):
            continue
        at = str(ab.get("ability_type", "") or "")
        if "起動" not in at:
            continue
        clauses = ab.get("clauses", [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            raw = str(cl.get("raw", "") or "")
            eff = str(cl.get("effect_template", "") or "")
            cost = str(cl.get("cost_template", "") or "")
            blob = " ".join([raw, cost, eff])
            # examples: 「自分の控え室のライブカードを1枚手札に加える」
            if ("控え室" in blob) and ("ライブ" in blob) and ("手札" in blob) and ("加える" in blob or "戻" in blob):
                return True
    return False
def can_activate(ci: Optional[CardInfo]) -> bool:
    # Legacy hard-coded subset (kept)
    if _has_green_live_take_ability(ci) or _has_green_member_take_ability(ci) or _has_sacrifice_ability(ci):
        return True
    # Generic: any activated ability (起動) that contains a supported effect_template
    return _ability_has_supported_clause(ci, activated=True)
def activation_moves_self_to_green(ci: Optional[CardInfo]) -> bool:
    """Whether activation cost includes moving the activating member to green room."""
    return bool(_has_sacrifice_ability(ci) or _has_green_member_take_ability(ci))
def _is_live(ci: Optional[CardInfo]) -> bool:
    if not ci:
        return False
    t = str(ci.type or "").upper()
    return "LIVE" in t
def _green_live_candidates(gs: "GameState", cards_db: Dict[str, CardInfo]) -> List[str]:
    cands: List[str] = []
    for cn in list(gs.green_room):
        ci = _get_card(cards_db, cn)
        if _is_live(ci):
            cands.append(cn)
    # keep stable order (latest first is sometimes nicer for UX)
    return cands
def _enqueue_topdeck_from_hand(gs: 'GameState', n: int, label: str = '') -> None:
    n = int(n or 0)
    if n <= 0:
        return
    hand = list(getattr(gs, 'hand', []) or [])
    if not hand:
        gs.log.append('[INFO] topdeck_from_hand: hand empty')
        return
    n = min(n, len(hand))
    if n <= 0:
        return
    if n == 1 and len(hand) == 1:
        cn = gs.hand.pop(0)
        gs.deck = [cn] + gs.deck
        gs.log.append(f'[AUTO] topdeck_from_hand: placed 1 on top ({label})')
        return
    prompt = {
        'kind': 'topdeck_from_hand',
        'text': f'{label} 手札を{n}枚、好きな順番でデッキ上に置く（1枚目=一番上）',
        'options': list(hand),
        'remaining': n,
        'picked': [],
        'label': str(label or ''),
    }
    # Put this at the front so it resolves before later live-start prompts.
    try:
        gs.pending.insert(0, prompt)
    except Exception:
        gs.pending.append(prompt)
    gs.log.append(f'[PENDING] topdeck_from_hand remaining={n} hand={len(hand)} ({label})')
def _count_nijigasaki_members_on_stage(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    n = 0
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'cardnumber', ''):
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci:
            continue
        if _is_live_ci(ci):
            continue
        if '虹ヶ咲' in str(getattr(ci, 'group', '') or ''):
            n += 1
    return int(n)
def _enqueue_choose_top_keep_one(gs: 'GameState', k: int, label: str = '', source_cn: str = '', set_idx: Optional[int] = None, followup_ops: Optional[List[Dict[str, Any]]] = None) -> None:
    k = int(k or 0)
    if k <= 0:
        return
    _rule_refresh_for_top_access(gs, None, k, reason='tsunagaru_connect')
    top = list((getattr(gs, 'deck', []) or [])[:k])
    if not top:
        gs.log.append('[INFO] choose_top_keep_one: deck empty')
        return
    if len(top) == 1:
        keep = top[0]
        gs.deck = [keep] + list((getattr(gs, 'deck', []) or [])[1:])
        gs.log.append(f'[AUTO] choose_top_keep_one: only 1 card kept ({label})')
        gs.pending.insert(0, {
            'kind': 'choose_top_keep_one',
            'text': f'{label} デッキ上から見たカードのうち1枚をデッキ上に置き、残りを控え室に置く',
            'options': [keep],
            'top_cards': [keep],
            'label': str(label or ''),
            'source_cn': str(source_cn or ''),
            'set_idx': set_idx,
            'followup_ops': list(followup_ops or []),
        })
        return
    gs.pending.insert(0, {
        'kind': 'choose_top_keep_one',
        'text': f'{label} デッキ上から見たカードのうち1枚をデッキ上に置き、残りを控え室に置く',
        'options': list(top),
        'top_cards': list(top),
        'label': str(label or ''),
        'source_cn': str(source_cn or ''),
        'set_idx': set_idx,
        'followup_ops': list(followup_ops or []),
    })
    gs.log.append(f'[PENDING] choose_top_keep_one top={len(top)} ({label})')

def _apply_live_effect_op(gs: 'GameState', cards_db: Dict[str, CardInfo], op: Dict[str, Any], ctx: Optional[Dict[str, Any]] = None) -> bool:
    ctx = dict(ctx or {})
    kind = str((op or {}).get('op', '') or '')
    if kind == 'add_live_score':
        delta = int((op or {}).get('delta', 0) or 0)
        if delta <= 0:
            return True
        _add_live_start_score_bonus(
            gs,
            delta,
            set_idx=(op or {}).get('set_idx', ctx.get('set_idx', None)),
            source_cn=_source_cn_or_default(str((op or {}).get('source_cn', '') or ctx.get('source_cn', '') or ''), 'この能力'),
        )
        gs.log.append(f"[AUTO] live-op add_live_score: +{delta}")
        return True
    if kind == 'show_cards_ack':
        key = str((op or {}).get('cards_from', '') or '').strip()
        cards = list(ctx.get(key, []) or []) if key else []
        if not cards:
            return True
        gs.pending.append({
            'kind': 'show_revealed_cards_ack',
            'label': str((op or {}).get('label', '') or '公開カード確認'),
            'text': str((op or {}).get('text', '') or '公開されたカードを確認'),
            'display_cards': list(cards),
            'options': ['ok'],
        })
        return True
    gs.log.append(f"[WARN] live-op effect unsupported: {kind}")
    return False

def _run_live_start_ops(gs: 'GameState', cards_db: Dict[str, CardInfo], ops: List[Dict[str, Any]], ctx: Optional[Dict[str, Any]] = None) -> bool:
    ctx = dict(ctx or {})
    for op in list(ops or []):
        kind = str((op or {}).get('op', '') or '')
        if kind == 'reveal_deck_top':
            n = int((op or {}).get('count', 1) or 1)
            cards = list((getattr(gs, 'deck', []) or [])[:max(0, n)])
            save_as = str((op or {}).get('save_as', '') or '').strip()
            if save_as:
                ctx[save_as] = list(cards)
            if n == 1:
                ctx['revealed_top_card'] = str(cards[0] if cards else '')
            continue
        if kind == 'if_revealed_is_live':
            key = str((op or {}).get('cards_from', '') or 'revealed_top').strip()
            cards = list(ctx.get(key, []) or [])
            ok = False
            for cn in cards:
                ci = _get_card(cards_db, cn)
                if ci and _is_live_ci(ci):
                    ok = True
                    break
            if ok:
                if not _run_live_start_ops(gs, cards_db, list((op or {}).get('then', []) or []), ctx=ctx):
                    return False
            else:
                gs.log.append(f"[AUTO] live-op if_revealed_is_live: false ({len(cards)} cards)")
            continue
        if kind in ('add_live_score', 'show_cards_ack'):
            if not _apply_live_effect_op(gs, cards_db, op, ctx=ctx):
                return False
            continue
        gs.log.append(f"[WARN] live-op unsupported: {kind}")
        return False
    return True

def _resolve_choose_top_keep_one(gs: 'GameState', p: Dict[str, Any], choice_str: str, cards_db: Dict[str, CardInfo]) -> bool:
    top_cards = list((p or {}).get('top_cards', []) or [])
    if not top_cards:
        gs.log.append('[ERR] choose_top_keep_one: no top cards recorded')
        return False
    cn = _canon_cardno(choice_str)
    keep = None
    for x in top_cards:
        if _canon_cardno(x) == cn:
            keep = x
            break
    if keep is None:
        gs.log.append(f'[ERR] choose_top_keep_one: invalid choice {choice_str}')
        return False
    deck = list(getattr(gs, 'deck', []) or [])
    removed = []
    for x in top_cards:
        if deck and _canon_cardno(deck[0]) == _canon_cardno(x):
            removed.append(deck.pop(0))
        else:
            hit = None
            for i, y in enumerate(deck):
                if _canon_cardno(y) == _canon_cardno(x):
                    hit = i
                    break
            if hit is not None:
                removed.append(deck.pop(hit))
    rest = []
    picked_used = False
    for x in removed:
        if (not picked_used) and _canon_cardno(x) == _canon_cardno(keep):
            picked_used = True
            continue
        rest.append(x)
    gs.green_room.extend(rest)
    gs.deck = [keep] + deck
    reveal = gs.deck[0] if list(getattr(gs, 'deck', []) or []) else ''
    followup_ops = list((p or {}).get('followup_ops', []) or [])
    if followup_ops:
        ctx = {
            'source_cn': str((p or {}).get('source_cn', '') or ''),
            'set_idx': (p or {}).get('set_idx', None),
            'revealed_top': [reveal] if reveal else [],
            'revealed_top_card': str(reveal or ''),
        }
        return bool(_run_live_start_ops(gs, cards_db, followup_ops, ctx=ctx))
    ci = _get_card(cards_db, reveal) if reveal else None
    if ci and _is_live_ci(ci):
        _add_live_start_score_bonus(gs, 1, set_idx=(p or {}).get('set_idx', None), source_cn=_source_cn_or_default((p or {}).get('source_cn', ''), 'この能力'))
        gs.log.append(f'[AUTO] Tsunagaru Connect: revealed LIVE on top -> score +1 ({reveal})')
    else:
        gs.log.append(f'[AUTO] Tsunagaru Connect: revealed non-LIVE on top ({reveal})')
    if reveal:
        gs.pending.append({
            'kind': 'show_revealed_cards_ack',
            'label': 'ツナガルコネクト 公開カード確認',
            'text': 'ツナガルコネクトで公開されたカードを確認',
            'display_cards': [reveal],
            'options': ['ok'],
        })
    return True
def _convert_pool_nonblue_plus_any_to_blue(pool: Dict[str, int]) -> Dict[str, int]:
    out = {str(k).lower(): int(v or 0) for k, v in (pool or {}).items()}
    moved = 0
    for k in ('pink', 'red', 'yellow', 'green', 'purple', 'all'):
        moved += int(out.get(k, 0) or 0)
        if k in out:
            out.pop(k, None)
    if moved > 0:
        out['blue'] = int(out.get('blue', 0) or 0) + moved
    return out
def _revealed_group_members_have_all_six_colors(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> bool:
    cols = set()
    group_name = str(group_name or '').strip()
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if not _is_member_ci(ci):
            continue
        if group_name and group_name not in str(getattr(ci, 'group', '') or ''):
            continue
        for k, v in ((getattr(ci, 'base_hearts', None) or {}) or {}).items():
            if k in ('pink', 'red', 'yellow', 'green', 'blue', 'purple') and int(v or 0) > 0:
                cols.add(k)
    return len(cols) == 6

def _enqueue_live_start_prompts(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    """Queue live-start auto effects once per live (until Attempt resolves)."""
    if gs.live_start_prompted:
        return 0
    rng = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
    triggers: List[Dict[str, Any]] = []
    did_auto = False
    def _append_prompt(prompt: Dict[str, Any], label: str = '') -> None:
        pr = dict(prompt or {})
        txt = str(label or pr.get('text', '') or '')
        cn = str(pr.get('cn', '') or pr.get('source_cn', '') or '')
        triggers.append({
            'kind': 'enqueue_pending_prompt',
            'source_cn': cn,
            'label': txt,
            'prompt': pr,
        })
    for pos in ("L", "C", "R"):
        slot = gs.stage.get(pos)
        if not slot:
            continue
        # ウェイト状態でもライブ開始時効果は発火する（ただし後続の能力チェックで
        # コスト「このメンバーをウェイトにする」系はすでにウェイトなのでスキップ）
        ci = _get_card(cards_db, slot.cardnumber)
        if not ci or not ci.abilities:
            continue
        for ab in ci.abilities:
            if not isinstance(ab, dict):
                continue
            trig = str(ab.get("trigger", "") or "")
            if "ライブ開始時" not in trig:
                continue
            gs.log.append(f'[DEBUG] live_start ab found: pos={pos} cn={ci.cardnumber} trig={repr(trig)}')
            clauses = ab.get("clauses", [])
            if not isinstance(clauses, list):
                continue
            if _ability_has_choose_header(ab):
                prm_choice = _build_choose_effects_prompt_from_ability(
                    gs, cards_db, ab, {'source_cn': ci.cardnumber, 'pos': pos.upper()}, timing='ライブ開始時'
                )
                if prm_choice and prm_choice.get('_skipped'):
                    continue
                if prm_choice:
                    _append_prompt(prm_choice, f'{pos}: {ci.cardnumber} ライブ開始時')
                    continue
                # Do not fall through and queue individual option clauses as
                # independent live-start effects.
                gs.log.append(f'[WARN] {ci.cardnumber}[ライブ開始時]: unsupported choose block skipped')
                continue
            if (not str(getattr(gs, 'success_zone_heart_color', '') or '').strip()):
                try:
                    blob_all = ''.join([str((cl0.get('raw') or cl0.get('effect_template') or '') ) for cl0 in clauses if isinstance(cl0, dict)])
                except Exception:
                    blob_all = ''
                if (
                    ('成功ライブカード置き場' in blob_all) and
                    ('選んだハート' in blob_all) and
                    (('1つを選ぶ' in blob_all) or ('1つ選ぶ' in blob_all))
                ):
                    opts = [c for c in ['桃', '黄', '紫'] if f"<({c})>" in blob_all]
                    if len(opts) >= 2:
                        pr = {
                            'kind': 'live_start_success_heart_by_success',
                            'pos': pos,
                            'cn': ci.cardnumber,
                            'text': f"{pos}: {ci.cardnumber} ライブ開始時 → ({'/'.join(opts)})から1つ選ぶ：成功ライブ置き場1枚につき選んだハート+1 (ライブ終了時まで)",
                            'options': opts,
                        }
                        _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                        continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                raw = str(cl.get("raw", "") or "")
                # Cost and effect must stay separated. For no-cost clauses, falling
                # back to raw as cost can misroute a free live-start effect into the
                # generic [E]1 route when raw/effect icon spacing differs.
                cost_t = str(cl.get("cost_template", "") or "")
                eff_t = str(cl.get("effect_template", "") or "")
                cost = cost_t
                eff = eff_t if eff_t else raw
                if _parse_energy_cost(cost) <= 0:
                    blob = str(eff or "")
                    if (not str(getattr(gs, 'success_zone_heart_color', '') or '').strip()) and (
                        ('成功ライブカード置き場' in blob) and ('選んだハート' in blob) and
                        ('<(桃)>' in blob) and ('<(黄)>' in blob) and ('<(紫)>' in blob) and
                        ('1つを選ぶ' in blob)
                    ):
                        pr = {
                            'kind': 'live_start_success_heart_by_success',
                            'pos': pos,
                            'cn': ci.cardnumber,
                            'text': f"{pos}: {ci.cardnumber} ライブ開始時 → (桃/黄/紫)を選ぶ：成功ライブ置き場1枚につき選んだハート+1 (ライブ終了時まで)",
                            'options': ['桃', '黄', '紫'],
                        }
                        _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                        continue
                    # ハート変換（元々持つハートは選んだハートになる）
                    if '元々持つハートは選んだハートになる' in blob and '選ぶ' in blob:
                        opts_hr = re.findall(r'<\(([^)]+)\)>', blob)
                        color_opts = []
                        for jp in opts_hr:
                            col = _HEART_JP_MAP.get(jp, '')
                            if col and col not in color_opts:
                                color_opts.append(col)
                        if color_opts:
                            opts_disp = [{'桃':'桃','red':'赤','yellow':'黄','green':'緑','blue':'青','purple':'紫','pink':'桃'}.get(c, c) for c in color_opts]
                            opts_disp_jp = [c for c in re.findall(r'<\(([^)]+)\)>', blob) if c in ('桃','赤','黄','緑','青','紫')]
                            if not opts_disp_jp:
                                opts_disp_jp = opts_disp
                            pr = {
                                'kind': 'live_start_heart_replace',
                                'pos': pos,
                                'cn': ci.cardnumber,
                                'text': f"{pos}: {ci.cardnumber} ライブ開始時 → 元々持つハートを選んだハートに変換 (ライブ終了時まで)",
                                'options': opts_disp_jp,
                                'color_map': {jp: _HEART_JP_MAP.get(jp, jp) for jp in opts_disp_jp},
                            }
                            _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                            continue
                    # Optional green-room member cost to deck bottom; result depends on moved cards' cost total.
                    bottom_costsum = _cost_green_members_to_deck_bottom_costsum(cost)
                    if bottom_costsum and ('それらのカードのコストの合計' in eff):
                        cands = _green_candidates_for_kind(gs, cards_db, kind='MEMBER')
                        count_need = int(bottom_costsum.get('count') or 0)
                        pr = {
                            'kind': 'choose_member_from_green_multi_up_to',
                            'source_zone': 'green',
                            'action': 'deck_bottom_costsum',
                            'min_picks': 0,
                            'max_picks': count_need,
                            'exact_or_zero': True,
                            'text': f'{ci.cardnumber}: 控え室のメンバーカードを0枚または{count_need}枚選び、クリック順でデッキの一番下へ置く',
                            'options': list(cands),
                            'source_cn': ci.cardnumber,
                            'pos': pos,
                        }
                        _append_prompt(pr, f'{pos}: {ci.cardnumber} ライブ開始時')
                        continue
                    # Optional hand group-card reveal cost -> put the revealed card on top or bottom, then gain blade.
                    top_bottom_group_cost = _cost_hand_group_card_optional_reveal(cost)
                    if top_bottom_group_cost and _is_revealed_card_to_top_or_bottom_blade_effect(eff):
                        pr = {
                            'kind': 'live_start_pay_effect',
                            'pos': pos,
                            'cn': ci.cardnumber,
                            'need_e': 0,
                            'cost_kind': 'hand_group_to_deck_top_or_bottom',
                            'cost_n': int(top_bottom_group_cost.get('count') or 1),
                            'cost_group': str(top_bottom_group_cost.get('group') or ''),
                            'effect': eff,
                            'text': _pretty_optional_effect_prompt_text('ライブ開始時', ci.cardnumber, cost, eff),
                            'options': ['pay', 'skip'],
                        }
                        _append_prompt(pr, f'{pos}: {ci.cardnumber} ライブ開始時')
                        continue
                    # Optional hand live-card cost to deck bottom.
                    bottom_hand_live = _cost_hand_live_to_deck_bottom(cost)
                    if bottom_hand_live and _match_effect_template(eff):
                        cost_n = int(bottom_hand_live.get('count') or 1)
                        pr = {
                            'kind': 'live_start_pay_effect',
                            'pos': pos,
                            'cn': ci.cardnumber,
                            'need_e': 0,
                            'cost_kind': 'hand_live_to_deck_bottom',
                            'cost_n': cost_n,
                            'effect': eff,
                            'text': _pretty_optional_effect_prompt_text('ライブ開始時', ci.cardnumber, cost, eff),
                            'options': ['pay', 'skip'],
                        }
                        _append_prompt(pr, f'{pos}: {ci.cardnumber} ライブ開始時')
                        continue
                    # Optional hand-discard cost.  These should enter the actual
                    # cost-payment picker directly; declining the optional cost is the
                    # Skip / zero-pick action on that same screen.
                    if '控え室に置いてもよい' in cost and (_match_effect_template(eff) or _is_named_hand_cost_result_effect(eff)):
                        named_cost = _parse_named_hand_discard_cost(cost)
                        group_cost = _parse_group_hand_discard_cost(cost)
                        m_live = re.search(r'手札のライブカードを(\d+)枚控え室に置いてもよい', cost)
                        m_hand = re.search(r'手札を(\d+)枚控え室に置いてもよい', cost)
                        ctx = {'pos': pos.upper(), 'source_cn': ci.cardnumber}
                        prompt_text = _pretty_optional_effect_prompt_text('ライブ開始時', ci.cardnumber, cost, eff) + '\nコストとして控え室に置く手札を選んでください。支払わない場合はスキップ。'
                        if named_cost:
                            names = list(named_cost.get('names', []) or [])
                            cands = _hand_named_card_candidates(gs, cards_db, names)
                            max_raw = named_cost.get('max_picks', None)
                            max_picks = len(cands) if max_raw is None else int(max_raw or 0)
                            if max_raw is None:
                                max_picks = len(cands)
                            pr = {
                                'kind': 'choose_member_from_green_multi_up_to',
                                'source_zone': 'hand',
                                'action': 'discard_from_hand',
                                'min_picks': int(named_cost.get('min_picks', 0) or 0),
                                'max_picks': max(0, max_picks),
                                'exact_or_zero': bool(named_cost.get('exact_or_zero', False)),
                                'text': prompt_text,
                                'options': list(cands),
                                'source_cn': ci.cardnumber,
                                'after_effect_template': eff,
                                'after_ctx': ctx,
                                'after_source_cn': ci.cardnumber,
                                'skip_if_no_picks': True,
                            }
                            _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                            continue
                        if group_cost:
                            group = str(group_cost.get('group', '') or '')
                            kind2 = str(group_cost.get('kind', 'ANY') or 'ANY')
                            cands = _hand_candidates_by_kind(gs, cards_db, kind=kind2, group=group)
                            max_picks = min(int(group_cost.get('max_picks', 1) or 1), len(cands)) if not bool(group_cost.get('exact_or_zero', False)) else int(group_cost.get('max_picks', 1) or 1)
                            if int(group_cost.get('max_picks', 1) or 1) == 1:
                                pr = {
                                    'kind': 'discard_from_hand',
                                    'remaining': 1,
                                    'text': prompt_text,
                                    'options': list(cands),
                                    'source_cn': ci.cardnumber,
                                    'after_effect_template': eff,
                                    'after_ctx': ctx,
                                    'after_source_cn': ci.cardnumber,
                                    'allow_skip': True,
                                    'optional': True,
                                    'skip_reason': 'optional group hand discard live-start cost',
                                }
                            else:
                                pr = {
                                    'kind': 'choose_member_from_green_multi_up_to',
                                    'source_zone': 'hand',
                                    'action': 'discard_from_hand',
                                    'min_picks': int(group_cost.get('min_picks', 0) or 0),
                                    'max_picks': max(0, max_picks),
                                    'exact_or_zero': bool(group_cost.get('exact_or_zero', False)),
                                    'text': prompt_text,
                                    'options': list(cands),
                                    'source_cn': ci.cardnumber,
                                    'after_effect_template': eff,
                                    'after_ctx': ctx,
                                    'after_source_cn': ci.cardnumber,
                                    'skip_if_no_picks': True,
                                }
                            _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                            continue
                        if m_live:
                            cost_n = int(m_live.group(1))
                            cands = _hand_candidates_by_kind(gs, cards_db, kind='LIVE')
                        else:
                            cost_n = int(m_hand.group(1)) if m_hand else 1
                            cands = list(gs.hand)
                        if cost_n <= 1:
                            pr = {
                                'kind': 'discard_from_hand',
                                'remaining': 1,
                                'text': prompt_text,
                                'options': list(cands),
                                'source_cn': ci.cardnumber,
                                'after_effect_template': eff,
                                'after_ctx': ctx,
                                'after_source_cn': ci.cardnumber,
                                'allow_skip': True,
                                'optional': True,
                                'skip_reason': 'optional hand discard live-start cost',
                            }
                        else:
                            pr = {
                                'kind': 'choose_member_from_green_multi_up_to',
                                'source_zone': 'hand',
                                'action': 'discard_from_hand',
                                'min_picks': 0,
                                'max_picks': int(cost_n),
                                'exact_or_zero': True,
                                'text': prompt_text,
                                'options': list(cands),
                                'source_cn': ci.cardnumber,
                                'after_effect_template': eff,
                                'after_ctx': ctx,
                                'after_source_cn': ci.cardnumber,
                                'skip_if_no_picks': True,
                            }
                        _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                        continue
                    # self-wait コスト（「このメンバーをウェイトにしてもよい」「ウェイトにする」）付き効果
                    # ※Eコストなしブロック内でチェックしないと2709のcontinueに捕捉される
                    if _cost_requires_self_wait(cost) and not _cost_requires_self_to_green(cost):
                        if not slot.active:
                            # すでにウェイト → コスト払えないのでスキップ
                            continue
                        gs.log.append(f'[DEBUG] self_wait: pos={pos} cn={ci.cardnumber} cost={repr(cost)} eff={repr(eff)} match={bool(_match_effect_template(eff))}')
                        if _match_effect_template(eff):
                            pr = {
                                'kind': 'live_start_pay_effect',
                                'pos': pos,
                                'cn': ci.cardnumber,
                                'need_e': 0,
                                'cost_kind': 'self_wait',
                                'effect': eff,
                                'text': _pretty_optional_effect_prompt_text('ライブ開始時', ci.cardnumber, 'このメンバーをウェイトにしてもよい', eff),
                                'options': ['pay', 'skip'],
                            }
                            _append_prompt(pr, f'{pos}: {ci.cardnumber} ライブ開始時')
                        continue
                    # コストなし・フリー効果（activate_stage_member等）
                    # cards_compiled の raw にはアイコン前後の改行が残ることがあり、
                    # cost_template が空の clause で cost=raw 扱いだと
                    # `cost.strip() == eff.strip()` を外して free 判定に失敗する。
                    # その場合 generic [E]1 / blade+N に誤ルーティングされるため、
                    # 空白正規化 + アイコン前後空白除去でも同一なら free とみなす。
                    cost_norm = re.sub(r'\s+', ' ', cost.strip())
                    eff_norm = re.sub(r'\s+', ' ', eff.strip())
                    cost_norm = re.sub(r' (<\([^)]*\)>)', r'\1', cost_norm)
                    cost_norm = re.sub(r'(<\([^)]*\)>) ', r'\1', cost_norm)
                    eff_norm = re.sub(r' (<\([^)]*\)>)', r'\1', eff_norm)
                    eff_norm = re.sub(r'(<\([^)]*\)>) ', r'\1', eff_norm)
                    if not cost.strip() or cost.strip() == eff.strip() or cost_norm == eff_norm:
                        trig_free = _build_live_start_trigger_from_effect(
                            gs, cards_db, eff, ci.cardnumber, f'{pos}: {ci.cardnumber} ライブ開始時', {'source_cn': ci.cardnumber, 'pos': pos.upper()}
                        )
                        if trig_free:
                            triggers.append(trig_free)
                            continue
                        m_free = _match_effect_template(eff)
                        if m_free:
                            r_free, gd_free = m_free
                            op_free = r_free.get('op', '')
                            if op_free == 'activate_stage_member':
                                # 対象が現在いなくても誘発自体は待機に積む。
                                # 他の同時誘発の解決後にウェイト状態のメンバーが生じる可能性があるため、
                                # ここでは候補有無で不発にしない。
                                triggers.append({
                                    'kind': 'live_start_choose_activate',
                                    'source_cn': ci.cardnumber,
                                    'label': f'{pos}: {ci.cardnumber} ライブ開始時',
                                    'pos': pos.upper(),
                                })
                            else:
                                triggers.append({
                                    'kind': 'live_start_apply_effect',
                                    'source_cn': ci.cardnumber,
                                    'label': f'{pos}: {ci.cardnumber} ライブ開始時',
                                    'pos': pos.upper(),
                                    'effect': eff,
                                })
                        continue
                # self-wait コスト（Eコストあり扱いで来た場合のフォールバック・通常は上のブロックで処理済み）
                if _cost_requires_self_wait(cost) and not _cost_requires_self_to_green(cost):
                    if not slot.active:
                        # すでにウェイト → コスト払えないのでスキップ
                        continue
                    if _match_effect_template(eff):
                        pr = {
                            'kind': 'live_start_pay_effect',
                            'pos': pos,
                            'cn': ci.cardnumber,
                            'need_e': 0,
                            'cost_kind': 'self_wait',
                            'effect': eff,
                            'text': _pretty_optional_effect_prompt_text('ライブ開始時', ci.cardnumber, 'このメンバーをウェイトにしてもよい', eff),
                            'options': ['pay', 'skip'],
                        }
                        _append_prompt(pr, f'{pos}: {ci.cardnumber} ライブ開始時')
                    continue
                need_e = _parse_energy_cost(cost)
                if need_e <= 0:
                    need_e = 1
                blades = _count_blade_icons(eff)
                if blades > 0 and need_e == 1:
                    blade_mode = "per_live_card" if ("自分のライブ中のカード1枚につき" in eff or "自分のライブ中のカード１枚につき" in eff) else "fixed"
                    blade_text = (
                        f"{pos}: {ci.cardnumber} ライブ開始時 [E]1 → 自分のライブ中のカード1枚につきブレード+{blades} (ライブ終了時まで)"
                        if blade_mode == "per_live_card"
                        else f"{pos}: {ci.cardnumber} ライブ開始時 [E]1 → ブレード+{blades} (ライブ終了時まで)"
                    )
                    pr = {
                        "kind": "live_start_blade",
                        "pos": pos,
                        "cn": ci.cardnumber,
                        "need_e": 1,
                        "blades": int(blades),
                        "blade_mode": blade_mode,
                        "text": blade_text,
                        "options": ["pay", "skip"],
                    }
                    _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
                    continue
                if _match_effect_template(eff):
                    pr = {
                        "kind": "live_start_pay_effect",
                        "pos": pos,
                        "cn": ci.cardnumber,
                        "need_e": int(need_e),
                        "effect": eff,
                        "text": f"{pos}: {ci.cardnumber} ライブ開始時 [E]{need_e} → {eff}",
                        "options": ["pay", "skip"],
                    }
                    _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
    # Generic LIVE-card live-start hook for set_zone cards.
    #
    # Historically this function mostly scanned stage members and a few hard-coded
    # LIVE cards, so generic LIVE cards with <ライブ開始時> abilities in set_zone
    # never triggered.  We first try generic no-cost clauses here, then keep the
    # existing hard-coded LIVE handlers below.
    _generic_live_skip = set()
    try:
        for _set_idx, cn_live in enumerate(list(getattr(gs, 'set_zone', []) or [])):
            try:
                canon_live = _canon_cardno(str(cn_live or ''))
            except Exception:
                canon_live = str(cn_live or '')
            if canon_live in _generic_live_skip:
                continue
            ci_live = _get_card(cards_db, cn_live)
            if not ci_live or not getattr(ci_live, 'abilities', None):
                continue
            for ab in (getattr(ci_live, 'abilities', None) or []):
                if not isinstance(ab, dict):
                    continue
                trig = str(ab.get('trigger', '') or '')
                if 'ライブ開始時' not in trig:
                    continue
                gs.log.append(f'[DEBUG] live_start LIVE ab found: cn={getattr(ci_live, "cardnumber", cn_live)} trig={repr(trig)}')
                clauses = ab.get('clauses', [])
                if not isinstance(clauses, list):
                    continue
                if _ability_has_choose_header(ab):
                    src_live = getattr(ci_live, 'cardnumber', '') or str(cn_live or '')
                    prm_choice = _build_choose_effects_prompt_from_ability(
                        gs, cards_db, ab, {'source_cn': src_live, 'set_idx': _set_idx}, timing='ライブ開始時'
                    )
                    if prm_choice and prm_choice.get('_skipped'):
                        _generic_live_skip.add(canon_live)
                        continue
                    if prm_choice:
                        triggers.append({
                            'kind': 'enqueue_pending_prompt',
                            'source_cn': src_live,
                            'label': f'{src_live} ライブ開始時',
                            'effect_text': str(prm_choice.get('text', '') or ''),
                            'prompt': prm_choice,
                        })
                        _generic_live_skip.add(canon_live)
                        continue
                    gs.log.append(f'[WARN] {src_live}[ライブ開始時]: unsupported choose block skipped')
                    _generic_live_skip.add(canon_live)
                    continue
                for cl in clauses:
                    if not isinstance(cl, dict):
                        continue
                    raw = str(cl.get('raw', '') or '')
                    cost_t = str(cl.get('cost_template', '') or '')
                    eff_t = str(cl.get('effect_template', '') or '')
                    cost = cost_t if cost_t else ''
                    eff = eff_t if eff_t else raw
                    build_text = eff
                    try:
                        cost_cmp = re.sub(r'\s+', '', str(cost or ''))
                        eff_cmp = re.sub(r'\s+', '', str(eff or ''))
                        if str(cost or '').strip() and cost_cmp != eff_cmp:
                            build_text = f"{str(cost).strip()}：{str(eff).strip()}"
                    except Exception:
                        build_text = eff
                    src_live = getattr(ci_live, 'cardnumber', '') or str(cn_live or '')
                    trig = _build_live_start_trigger_from_effect(
                        gs, cards_db, build_text, src_live, f'{src_live} ライブ開始時', {'source_cn': src_live, 'set_idx': _set_idx}
                    )
                    if trig:
                        triggers.append(trig)
                        continue
                    # Only generic no-cost LIVE-card hooks here.
                    if _parse_energy_cost(cost) > 0:
                        continue
                    if _cost_requires_self_wait(cost) or _cost_requires_self_to_green(cost):
                        continue
                    m_live = re.search(r'手札のライブカードを(\d+)枚控え室に置いてもよい', cost)
                    m_hand = re.search(r'手札を(\d+)枚控え室に置いてもよい', cost)
                    if m_live or m_hand:
                        try:
                            n_cost = int((m_live or m_hand).group(1) or 0)
                        except Exception:
                            n_cost = 0
                        if n_cost > 0:
                            src_live = getattr(ci_live, 'cardnumber', '') or str(cn_live or '')
                            pr = {
                                'kind': 'pay_or_skip',
                                'cn': src_live,
                                'source_cn': src_live,
                                'text': _pretty_optional_effect_prompt_text('ライブ開始時', src_live, cost, eff),
                                'options': ['pay', 'skip'],
                                'cost_kind': 'discard_from_hand',
                                'cost_n': n_cost,
                                'after_effect_template': eff,
                                'ctx': {'source_cn': src_live},
                            }
                            _append_prompt(pr, pr['text'])
                        continue
                    if not cost.strip() or cost.strip() == eff.strip():
                        triggers.append({
                            'kind': 'live_start_apply_effect',
                            'source_cn': src_live,
                            'label': f'{src_live} ライブ開始時',
                            'effect': eff,
                        })
    except Exception:
        pass
    n = len(triggers)
    if n <= 0:
        if did_auto:
            gs.live_start_prompted = True
        return 0
    gs.live_start_prompted = True
    text = 'ライブ開始時効果が発生：解決するカードを選択' if n == 1 else 'ライブ開始時効果が複数発生：解決するカードを選択（1つずつ）'
    gs.pending.append({
        'kind': 'auto_order',
        'text': text,
        'options': [_auto_trigger_option_text(t) for t in triggers if _auto_trigger_option_text(t)],
        'queue': list(triggers),
    })
    gs.log.append(f'[PENDING] auto_order triggers={len(triggers)}')
    gs.log.append(f'[PROMPT] live-start abilities queued: {n}')
    return n
def _clear_end_of_live_buffs(gs: GameState, cards_db: Optional[Dict[str, CardInfo]] = None) -> None:
    for pos in ("L", "C", "R"):
        slot = gs.stage.get(pos)
        if not slot:
            continue
        if getattr(slot, "temp_until", "") == "end_of_live":
            slot.temp_blade = 0
            slot.temp_hearts = {}
            try:
                slot.temp_score = 0
            except Exception:
                pass
            try:
                slot.temp_cost = 0
            except Exception:
                pass
            slot.temp_until = ""
        # Always clear heart_replace_color at end of live (it's always "until end of live")
        try:
            slot.heart_replace_color = ""
        except Exception:
            pass
    # clear global end-of-live buffs
    try:
        gs.success_zone_heart_color = ""
        gs.success_zone_heart_pos = ""
    except Exception:
        pass
    try:
        gs.live_start_score_bonus_by_set_idx = {}
        gs.live_start_required_any_reduction_by_set_idx = {}
        gs.live_start_required_any_increase_by_set_idx = {}
    except Exception:
        pass
    try:
        gs.cannot_live_until_end_of_live = False
    except Exception:
        pass
def cmd_play(gs: GameState, cards_db: Dict[str, CardInfo], hand_idx: int, pos: str) -> None:
    pos = pos.upper()
    if pos not in ("L", "C", "R"):
        gs.log.append("[ERR] play: pos must be L/C/R")
        return
    if hand_idx < 0 or hand_idx >= len(gs.hand):
        gs.log.append("[ERR] play: invalid hand index")
        return
    existing = gs.stage.get(pos)
    baton_old_cn = None
    baton_old_cost = 0
    if existing is not None:
        # Baton touch (ルール 9.6.2.3.2): you may put your member in that area into green room to reduce the cost.
        baton_old_cn = existing.cardnumber
        old = _get_card(cards_db, baton_old_cn)
        # Baton touch reduces by the member's current/effective cost, not only printed cost.
        # This matters for BODY 常時 effects such as success-zone score sum >= 6 -> cost +3.
        try:
            baton_old_cost = int(_slot_effective_cost(gs, cards_db, pos, existing) or 0)
        except Exception:
            baton_old_cost = int(old.cost) if old else 0
        # If the replaced member had energies under it, they return to the energy deck (not to energy zone).
        _return_under_energy_to_deck_from_slot(gs, existing, pos=pos, reason=f'{baton_old_cn} leaves stage', cards_db=cards_db)
    cn = gs.hand[hand_idx]
    c = _get_card(cards_db, cn)
    ctype = (c.type if c else "")
    if not c or not is_member_type(ctype):
        gs.log.append(f"[ERR] play: not a MEMBER card: cn={cn} db_type='{ctype}'")
        return
    printed_cost = int(c.cost or 0)
    try:
        cost = int(_card_effective_play_cost_from_hand(gs, cards_db, cn) or printed_cost)
    except Exception:
        cost = printed_cost
    pay_cost = cost
    if baton_old_cn is not None:
        # Baton touch is only committed if the play itself succeeds.
        # Compute the reduced cost first, but do not move the replaced card yet.
        pay_cost = max(0, cost - int(baton_old_cost or 0))
    if not pay_energy(gs, pay_cost):
        gs.log.append(f"[ERR] play: insufficient energy (need {pay_cost}, have {gs.energy_active})")
        return
    if baton_old_cn is not None:
        # Now that payment succeeded, commit the baton move.
        gs.green_room.append(baton_old_cn)
        try:
            printed_old_cost = int(getattr(_get_card(cards_db, baton_old_cn), 'cost', 0) or 0)
        except Exception:
            printed_old_cost = int(baton_old_cost or 0)
        if int(printed_old_cost or 0) != int(baton_old_cost or 0):
            gs.log.append(f"[BATON] {pos}: {baton_old_cn} -> green room; reduce {cost} by effective cost {baton_old_cost} (printed {printed_old_cost}) => pay {pay_cost}")
        else:
            gs.log.append(f"[BATON] {pos}: {baton_old_cn} -> green room; reduce {cost} by {baton_old_cost} => pay {pay_cost}")
    gs.hand.pop(hand_idx)
    gs.stage[pos] = StageSlot(cardnumber=(c.cardnumber if c else cn), active=True)
    try:
        if int(printed_cost or 0) != int(cost or 0):
            gs.log.append(f"[PLAYCOST] {cn}: hand effective cost {cost} (printed {printed_cost})")
    except Exception:
        pass
    gs.log.append(f"[PLAY] {pos} <- {cn} (pay {pay_cost}; E active={gs.energy_active} wait={gs.energy_wait})")
    # Auto abilities can trigger simultaneously on this "member enters stage" event.
    # If multiple triggers exist, let the user choose the resolution order.
    triggers: List[Dict[str, Any]] = []
    if baton_old_cn is not None:
        try:
            triggers.extend(_collect_auto_triggers_on_member_leave_stage(gs, cards_db, left_pos=pos, left_cn=baton_old_cn, baton_new_cn=cn))
        except Exception:
            pass
    triggers.extend(_collect_auto_triggers_on_member_enter(gs, cards_db, entered_pos=pos, entered_cn=cn))
    if len(triggers) >= 2:
        opts2: List[str] = []
        for t in triggers:
            scn = _canon_cardno(str((t or {}).get('source_cn', '') or ''))
            if scn:
                # Keep duplicates so that multiple copies (e.g., 2×Ai) can be resolved separately.
                opts2.append(scn)
        gs.pending.append({
            'kind': 'auto_order',
            'text': '自動効果が複数発生：解決するカードを選択（1つずつ）',
            'options': opts2,
            'queue': triggers,
        })
        gs.log.append(f"[PENDING] auto_order triggers={len(triggers)}")
        return
    for t in triggers:
        _exec_auto_trigger(gs, cards_db, t)
def _has_supported_enter_auto(ci: Optional[CardInfo]) -> bool:
    if not ci:
        return False
    canon = _canon_cardno(getattr(ci, 'cardnumber', '') or '')    # Any costless, regex-matchable enter ability counts as supported.
    for ab in _iter_triggered_abilities(ci, '登場'):
        if not isinstance(ab, dict):
            continue
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            cost = str(cl.get('cost_template', '') or '')
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            if not eff:
                continue
            # allow optional discard-from-hand / energy / self-wait costs for [登場]
            if cost:
                m = re.search(r"手札を(\d+)枚控え室に置いてもよい", cost)
                n = 0
                if m:
                    try:
                        n = int(m.group(1) or 0)
                    except Exception:
                        n = 0
                if n <= 0 and ("手札を1枚控え室に置いてもよい" in cost):
                    n = 1
                group_cost = _parse_group_hand_discard_cost(cost)
                if group_cost and _match_effect_template(eff):
                    return True
                if n > 0 and _match_effect_template(eff):
                    return True
                if _parse_energy_cost(cost) > 0 and _match_effect_template(eff):
                    return True
                if _cost_requires_self_wait(cost) and not _cost_requires_self_to_green(cost) and _match_effect_template(eff):
                    return True
                # other cost templates unsupported for enter-auto support detection
                continue
            if _parse_energy_cost(cost) > 0 or _cost_requires_self_to_green(cost):
                continue
            if _match_effect_template(eff):
                return True
            # Mode-style (choose) header across clauses
            if ('以下から' in eff) and ('選ぶ' in eff):
                return True
    return False
def handle_enter_auto(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, cn: str, rng: Optional[random.Random] = None) -> None:
    # Handle [登場] auto abilities for a member that just entered stage.
    canon = _canon_cardno(cn)
    if rng is None:
        rng = random.Random(gs.seed)
    ci = _get_card(cards_db, canon)
    if not ci or not getattr(ci, 'abilities', None):
        return
    # Generic mode-style [登場]:
    # 先頭 clause が「以下から1つを選ぶ。」で、後続が costless & matchable な場合は
    # 汎用 choose_enter_effect_mode として処理する。
    for ab in _iter_triggered_abilities(ci, '登場'):
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list) or len(clauses) < 2:
            continue
        first = clauses[0] if isinstance(clauses[0], dict) else {}
        first_eff = str(first.get('effect_template', '') or first.get('raw', '') or '').strip()
        if ('以下から' not in first_eff) or ('選ぶ' not in first_eff):
            continue
        mode_effects = []
        mode_labels = []
        ok = True
        for cl in clauses[1:]:
            if not isinstance(cl, dict):
                ok = False
                break
            cost = str(cl.get('cost_template', '') or '').strip()
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            if cost or (not eff):
                ok = False
                break
            if not _match_effect_template(eff):
                ok = False
                break
            mode_effects.append(eff)
            label = eff.replace('。', '')
            if len(label) > 36:
                label = label[:36] + '…'
            mode_labels.append(label)
        if ok and mode_effects:
            gs.pending.append({
                'kind': 'choose_enter_effect_mode',
                'text': f"{canon}[登場]: 効果を1つ選ぶ",
                'options': list(mode_labels),
                'effects': list(mode_effects),
                'ctx': {'pos': pos.upper(), 'source_cn': canon},
                'source_cn': canon,
            })
            gs.log.append(f"[PENDING] {canon}[登場]: choose mode from {len(mode_effects)} effects")
            return
    for ab in _iter_triggered_abilities(ci, '登場'):
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            cost = str(cl.get('cost_template', '') or '')
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            if not eff:
                continue
            # Cost template handling for [登場]
            if cost:
                if _cost_requires_main_phase(cost) and gs.phase != 'MAIN':
                    gs.log.append(f"[INFO] {canon}[登場]: skipped outside MAIN: {cost}")
                    continue
                group_cost = _parse_group_hand_discard_cost(cost)
                m_live = re.search(r"手札のライブカードを(\d+)枚控え室に置いてもよい", cost)
                m = re.search(r"手札を(\d+)枚控え室に置いてもよい", cost)
                n = 0
                if m:
                    try:
                        n = int(m.group(1) or 0)
                    except Exception:
                        n = 0
                if n <= 0 and ("手札を1枚控え室に置いてもよい" in cost):
                    n = 1
                if group_cost and _match_effect_template(eff):
                    ctx = {'pos': pos.upper(), 'source_cn': canon}
                    group = str(group_cost.get('group', '') or '')
                    kind2 = str(group_cost.get('kind', 'ANY') or 'ANY')
                    cands = _hand_candidates_by_kind(gs, cards_db, kind=kind2, group=group)
                    need = int(group_cost.get('max_picks', 1) or 1)
                    prompt_text = _pretty_optional_effect_prompt_text('登場', canon, cost, eff) + '\nコストとして控え室に置く手札を選んでください。支払わない場合はスキップ。'
                    if need <= 1:
                        gs.pending.append({
                            'kind': 'discard_from_hand',
                            'remaining': 1,
                            'text': prompt_text,
                            'options': list(cands),
                            'after_effect_template': eff,
                            'after_ctx': ctx,
                            'after_source_cn': canon,
                            'allow_skip': True,
                            'optional': True,
                            'skip_reason': 'optional group hand discard enter-auto cost',
                        })
                    else:
                        gs.pending.append({
                            'kind': 'choose_member_from_green_multi_up_to',
                            'source_zone': 'hand',
                            'action': 'discard_from_hand',
                            'min_picks': int(group_cost.get('min_picks', 0) or 0),
                            'max_picks': need if bool(group_cost.get('exact_or_zero', False)) else min(need, len(cands)),
                            'exact_or_zero': bool(group_cost.get('exact_or_zero', False)),
                            'text': prompt_text,
                            'options': list(cands),
                            'after_effect_template': eff,
                            'after_ctx': ctx,
                            'after_source_cn': canon,
                            'skip_if_no_picks': True,
                        })
                    gs.log.append(f"[PENDING] {canon}[登場]: optional group discard cost picker then {eff}")
                    return
                if m_live and _match_effect_template(eff):
                    ctx = {'pos': pos.upper(), 'source_cn': canon}
                    n_live = int(m_live.group(1) or 1)
                    cands = _hand_candidates_by_kind(gs, cards_db, kind='LIVE')
                    prompt_text = _pretty_optional_effect_prompt_text('登場', canon, cost, eff) + '\nコストとして控え室に置くライブカードを選んでください。支払わない場合はスキップ。'
                    if n_live <= 1:
                        gs.pending.append({
                            'kind': 'discard_from_hand',
                            'remaining': 1,
                            'text': prompt_text,
                            'options': list(cands),
                            'after_effect_template': eff,
                            'after_ctx': ctx,
                            'after_source_cn': canon,
                            'allow_skip': True,
                            'optional': True,
                            'skip_reason': 'optional live hand discard enter-auto cost',
                        })
                    else:
                        gs.pending.append({
                            'kind': 'choose_member_from_green_multi_up_to',
                            'source_zone': 'hand',
                            'action': 'discard_from_hand',
                            'min_picks': 0,
                            'max_picks': n_live,
                            'exact_or_zero': True,
                            'text': prompt_text,
                            'options': list(cands),
                            'after_effect_template': eff,
                            'after_ctx': ctx,
                            'after_source_cn': canon,
                            'skip_if_no_picks': True,
                        })
                    gs.log.append(f"[PENDING] {canon}[登場]: optional live-card discard cost picker then {eff}")
                    return
                if n > 0:
                    ctx = {'pos': pos.upper(), 'source_cn': canon}
                    combo_self_wait = _cost_requires_self_wait(cost) and not _cost_requires_self_to_green(cost)
                    if combo_self_wait:
                        gs.pending.append({
                            'kind': 'pay_or_skip',
                            'text': _pretty_optional_effect_prompt_text('登場', canon, cost, eff),
                            'options': ['pay', 'skip'],
                            'cost_kind': 'self_wait_and_discard_from_hand',
                            'cost_n': n,
                            'after_effect_template': eff,
                            'ctx': ctx,
                            'source_cn': canon,
                        })
                        gs.log.append(f"[PENDING] {canon}[登場]: pay/skip -> self_wait + discard {n} then {eff}")
                        return
                    # Optional hand-discard costs on auto effects should open the actual
                    # cost-payment screen immediately.  Declining the effect is represented
                    # by the Skip button on that same hand-selection screen.
                    gs.pending.append({
                        'kind': 'discard_from_hand',
                        'remaining': n,
                        'text': _pretty_optional_effect_prompt_text('登場', canon, cost, eff) + '\nコストとして控え室に置く手札を選んでください。支払わない場合はスキップ。',
                        'options': list(gs.hand),
                        'after_effect_template': eff,
                        'after_ctx': ctx,
                        'after_source_cn': canon,
                        'allow_skip': True,
                        'optional': True,
                        'skip_reason': 'optional hand discard enter-auto cost',
                    })
                    gs.log.append(f"[PENDING] {canon}[登場]: optional discard cost picker {n} then {eff}")
                    return
                e_cost = _parse_energy_cost(cost)
                if e_cost > 0 and _match_effect_template(eff):
                    ctx = {'pos': pos.upper(), 'source_cn': canon}
                    gs.pending.append({
                        'kind': 'pay_or_skip',
                        'text': _pretty_optional_effect_prompt_text('登場', canon, cost, eff),
                        'options': ['pay', 'skip'],
                        'cost_kind': 'energy',
                        'cost_n': e_cost,
                        'after_effect_template': eff,
                        'ctx': ctx,
                        'source_cn': canon,
                    })
                    gs.log.append(f"[PENDING] {canon}[登場]: pay/skip -> energy {e_cost} then {eff}")
                    return
                if _cost_requires_self_wait(cost) and not _cost_requires_self_to_green(cost):
                    ctx = {'pos': pos.upper(), 'source_cn': canon}
                    gs.pending.append({
                        'kind': 'pay_or_skip',
                        'text': _pretty_optional_effect_prompt_text('登場', canon, cost, eff),
                        'options': ['pay', 'skip'],
                        'cost_kind': 'self_wait',
                        'cost_n': 0,
                        'after_effect_template': eff,
                        'ctx': ctx,
                        'source_cn': canon,
                    })
                    gs.log.append(f"[PENDING] {canon}[登場]: pay/skip -> self-wait then {eff}")
                    return
                # unsupported cost template for now
                gs.log.append(f"[INFO] {canon}[登場]: unsupported cost_template skipped: {cost}")
                continue
            # costless-only for now
            if _parse_energy_cost(cost) > 0 or _cost_requires_self_to_green(cost):
                continue
            ctx = {'pos': pos.upper(), 'source_cn': canon, 'auto_effect_detail': f'【{canon}】登場時効果\n効果：{eff}'}
            if try_apply_effect_template(gs, rng, cards_db, eff, ctx):
                gs.log.append(f"[AUTO] {canon}[登場]: applied {eff}")
                if gs.pending:
                    return
    # BODY効果（手札をすべて公開する）は起動効果のため cmd_activate_member で処理
def _handle_body_reveal_all_hand(
    gs: GameState,
    cards_db: Dict[str, CardInfo],
    pos: str,
    canon: str,
    eff: str,
    rng: Optional[random.Random],
) -> None:
    """BODY効果: 手札をすべて公開し、ライブカードがない場合にデッキ上5枚からライブカードを1枚手札へ。
    対象カード例:
      PL!N-PR-003 上原歩夢 / PL!N-PR-008 近江彼方 / PL!N-PR-010 エマ・ヴェルデ
    効果テキスト:
      自分のステージにほかのメンバーがおり、かつこれにより公開した手札の中にライブカードがない場合、
      自分のデッキの上からカードを5枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。
    """
    # 条件1: 自分のステージにほかのメンバーがいるか
    other_members = [p for p in ('L', 'C', 'R') if p != pos and gs.stage.get(p)]
    if not other_members:
        gs.log.append(f'[AUTO] {canon}[BODY]: 他メンバーなし → 効果なし')
        return
    # 手札を公開（内容をログに記録）
    hand_cns = list(gs.hand)
    live_in_hand = [cn for cn in hand_cns if _is_live_card(cards_db, cn)]
    gs.log.append(f'[AUTO] {canon}[BODY]: 手札公開 hand={hand_cns} live_in_hand={live_in_hand}')
    # 条件2: 公開した手札にライブカードがない
    if live_in_hand:
        gs.log.append(f'[AUTO] {canon}[BODY]: 手札にライブカードあり → 効果なし')
        return
    # 条件達成: デッキ上5枚を見てライブカード1枚を手札に加えてもよい
    k = 5
    _rule_refresh_for_top_access(gs, rng, k, reason=f'{canon}_body')
    pool = list(gs.deck[:k])
    if not pool:
        gs.log.append(f'[AUTO] {canon}[BODY]: デッキ空 → 効果なし')
        return
    # ライブカード候補を絞る
    live_cands = [cn for cn in pool if _is_live_card(cards_db, cn)]
    if not live_cands:
        # ライブカードなし → 全て控え室へ
        for cn in pool:
            gs.deck.remove(cn)
            gs.green_room.append(cn)
        gs.log.append(f'[AUTO] {canon}[BODY]: デッキ上{k}枚にライブカードなし → 全て控え室 {pool}')
        return
    gs.log.append(f'[PENDING] {canon}[BODY]: デッキ上{k}枚={pool} ライブ候補={live_cands}')
    gs.pending.append({
        'kind': 'body_reveal_pick_live',
        'cn': canon,
        'pos': pos,
        'pool': list(pool),
        'live_cands': list(live_cands),
        'k': k,
        'text': f'{canon}[BODY]: デッキ上{k}枚からライブカードを1枚手札に加えてもよい（スキップ可）',
        'options': list(live_cands) + ['skip'],
        'display_cards': list(pool),
        'candidates': list(live_cands),
        'optional': True,
    })
def _is_live_card(cards_db: Dict[str, CardInfo], cn: str) -> bool:
    """Return True if cn is a LIVE-type card."""
    ci = _get_card(cards_db, _canon_cardno(str(cn or '')))
    if not ci:
        return False
    return is_live_type(getattr(ci, 'type', '') or '')
def _has_auto_on_cost10_member_enter_draw1(ci: Optional[CardInfo]) -> bool:
    if not ci:
        return False
    try:
        abilities = list(getattr(ci, 'abilities', []) or [])
    except Exception:
        abilities = []
    target = '自分のステージにコスト10のメンバーが登場したとき、カードを1枚引く。'
    for ab in abilities:
        if not isinstance(ab, dict):
            continue
        at = str(ab.get('ability_type', '') or '')
        trig = str(ab.get('trigger', '') or '')
        cond = str(ab.get('conditions', '') or '')
        if ('自動' not in at) and ('BODY' not in trig) and ('自動' not in trig):
            continue
        if 'ターン1回' not in cond:
            continue
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            if eff == target:
                return True
    return False
def handle_stage_cost10_member_enter_draw1(gs: GameState, cards_db: Dict[str, CardInfo], entered_pos: str, entered_cn: str, source_pos: str = '', rng: Optional[random.Random] = None) -> None:
    """Handle auto abilities that trigger when a cost-10 MEMBER enters your stage.
    Generalized from PL!N-pb1-005 (宮下愛):
      <自動><ターン1回> 自分のステージにコスト10のメンバーが登場したとき、カードを1枚引く。
    """
    try:
        entered_pos = str(entered_pos or '').upper()
    except Exception:
        entered_pos = 'C'
    if rng is None:
        try:
            rng = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 29)
        except Exception:
            rng = random.Random(29)
    try:
        source_pos_u = str(source_pos or '').upper()
    except Exception:
        source_pos_u = ''
    canon_enter = _canon_cardno(entered_cn)
    ci_enter = _get_card(cards_db, canon_enter)
    if not ci_enter:
        return
    try:
        cost = int(getattr(ci_enter, 'cost', 0) or 0)
    except Exception:
        cost = 0
    if cost != 10:
        return
    def _resolve_one(p: str) -> None:
        slot = gs.stage.get(p)
        if not slot:
            return
        canon = _canon_cardno(slot.cardnumber)
        ci_src = _get_card(cards_db, canon)
        if not _has_auto_on_cost10_member_enter_draw1(ci_src):
            return
        key = f"{p}:{canon}:auto_cost10_enter_draw1"
        used = int((getattr(gs, 'used_this_turn', {}) or {}).get(key, 0) or 0)
        if used >= 1:
            return
        drew = draw(gs, 1, rng)
        try:
            gs.used_this_turn[key] = 1
        except Exception:
            gs.used_this_turn = {key: 1}
        gs.log.append(f"[AUTO] {canon}({p}): cost10 member entered ({canon_enter} @ {entered_pos}) -> drew {drew}")
    if source_pos_u in ('L', 'C', 'R'):
        _resolve_one(source_pos_u)
        return
    for p in ('L', 'C', 'R'):
        _resolve_one(p)
def _list_active_cost10_member_enter_draw_positions(gs: GameState, cards_db: Dict[str, CardInfo], entered_cn: str) -> List[str]:
    """Return stage positions of unused members that would trigger on cost-10 member enter and draw 1."""
    canon_enter = _canon_cardno(entered_cn)
    ci_enter = _get_card(cards_db, canon_enter)
    if not ci_enter:
        return []
    try:
        cost = int(getattr(ci_enter, 'cost', 0) or 0)
    except Exception:
        cost = 0
    if cost != 10:
        return []
    out: List[str] = []
    for p in ('L', 'C', 'R'):
        slot = gs.stage.get(p)
        if not slot:
            continue
        canon = _canon_cardno(slot.cardnumber)
        ci_src = _get_card(cards_db, canon)
        if not _has_auto_on_cost10_member_enter_draw1(ci_src):
            continue
        key = f"{p}:{canon}:auto_cost10_enter_draw1"
        used = int((getattr(gs, 'used_this_turn', {}) or {}).get(key, 0) or 0)
        if used < 1:
            out.append(p)
    return out
def _has_active_cost10_member_enter_draw_trigger(gs: GameState, cards_db: Dict[str, CardInfo], entered_cn: str) -> bool:
    return bool(_list_active_cost10_member_enter_draw_positions(gs, cards_db, entered_cn))
def _collect_auto_triggers_on_member_leave_stage(gs: GameState, cards_db: Dict[str, CardInfo], left_pos: str, left_cn: str, baton_new_cn: str = '') -> List[Dict[str, Any]]:
    """Collect auto triggers that happen when a MEMBER leaves your stage and goes to green room.
    Narrow support for cards whose compiled clause keeps the full trigger text inside
    effect_template, e.g.
      - このメンバーがステージから控え室に置かれたとき、...
    """
    out: List[Dict[str, Any]] = []
    canon_left = _canon_cardno(left_cn)
    ci_left = _get_card(cards_db, canon_left)
    if not ci_left or _is_live_ci(ci_left):
        return out
    for ab in getattr(ci_left, 'abilities', []) or []:
        if not isinstance(ab, dict):
            continue
        trig = str(ab.get('trigger', '') or '')
        # Compiled DB may store these as BODY-style clauses with the trigger phrase inline.
        if trig not in ('BODY', '自動', '') and ('控え室に置かれたとき' not in trig):
            continue
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list):
            continue
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            cost = str(cl.get('cost_template', '') or '')
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            if not eff:
                continue
            if 'このメンバーがステージから控え室に置かれたとき' not in eff:
                continue
            if cost:
                # leave-stage triggers in current scope are costless only
                continue
            if not _match_effect_template(eff):
                continue
            out.append({
                'kind': 'stage_to_green_auto',
                'source_cn': canon_left,
                'pos': str(left_pos or 'C').upper(),
                'cn': left_cn,
                'effect': eff,
                'label': f'{canon_left}[stage->green]',
                'baton_new_cn': _canon_cardno(str(baton_new_cn or '')),
            })
    return out
def _collect_auto_triggers_on_member_enter(gs: GameState, cards_db: Dict[str, CardInfo], entered_pos: str, entered_cn: str) -> List[Dict[str, Any]]:
    """Collect auto triggers that happen when a MEMBER enters your stage.
    Triggers are collected as individual instances (not de-duplicated), so that
    multiple copies of the same card (e.g., 2× 宮下愛) can be resolved separately
    in the order the player chooses.
    """
    out: List[Dict[str, Any]] = []
    canon_enter = _canon_cardno(entered_cn)
    ci_enter = _get_card(cards_db, canon_enter)
    if ci_enter and _has_supported_enter_auto(ci_enter):
        out.append({
            'kind': 'enter_auto',
            'source_cn': canon_enter,
            'pos': str(entered_pos or 'C').upper(),
            'cn': entered_cn,
        })
    # Generic: one trigger per unused member whose BODY says "when a cost-10 member enters, draw 1"
    for src_pos in _list_active_cost10_member_enter_draw_positions(gs, cards_db, entered_cn):
        slot = gs.stage.get(str(src_pos).upper())
        src_cn = _canon_cardno(getattr(slot, 'cardnumber', '') or '') if slot else ''
        out.append({
            'kind': 'cost10_enter_draw1_auto',
            'source_cn': src_cn,
            'source_pos': str(src_pos).upper(),
            'entered_pos': str(entered_pos or 'C').upper(),
            'entered_cn': entered_cn,
        })
    return out
def _auto_trigger_effect_text(t: Dict[str, Any]) -> str:
    """Return only the specific effect text represented by one queued auto trigger.

    This is intentionally separate from the card text as a whole.  When a card has
    multiple triggers at the same timing (e.g. Wish Song), the auto-order popup must
    show which effect each option will resolve.
    """
    if not isinstance(t, dict):
        return ''
    for key in ('effect_text', 'effect'):
        v = str(t.get(key, '') or '').strip()
        if v:
            return v
    prm = t.get('prompt', {})
    if isinstance(prm, dict):
        for key in ('after_effect_template', 'effect'):
            v = str(prm.get(key, '') or '').strip()
            if v:
                return v
    return ''

def _auto_trigger_option_text(t: Dict[str, Any]) -> str:
    try:
        opt_lbl = str((t or {}).get('option_label', '') or '').strip()
    except Exception:
        opt_lbl = ''
    if opt_lbl:
        return opt_lbl
    try:
        lbl = str((t or {}).get('label', '') or '').strip()
    except Exception:
        lbl = ''
    eff = _auto_trigger_effect_text(t or {})
    try:
        cn0 = str((t or {}).get('source_cn', '') or '').strip()
    except Exception:
        cn0 = ''
    kind0 = str((t or {}).get('kind', '') or '').strip()
    # Concise labels for auto-order options from the same source card.  The full
    # effect remains available through effect_text/effect for the hover detail.
    if kind0 == 'live_start_apply_effect' and eff:
        if 'カードを1枚引く' in eff and 'ウェイト' in eff and '相手のステージ' in eff:
            return f'{cn0}：1ドロー→相手ウェイト' if cn0 else '1ドロー→相手ウェイト'
    if kind0 == 'live_start_topdeck_green_group_members_upto_opponent_wait_count_manual':
        return f'{cn0}：相手ウェイト数ぶんデッキ上' if cn0 else '相手ウェイト数ぶんデッキ上'
    if kind0 == 'live_start_reduce_any_if_opponent_wait_exists_manual':
        return f'{cn0}：必要ハート軽減' if cn0 else '必要ハート軽減'
    if lbl and eff:
        return f'{lbl}：{eff}'
    if lbl:
        return lbl
    if cn0 and eff:
        return f'{cn0}：{eff}'
    return cn0
def _exec_auto_trigger(gs: GameState, cards_db: Dict[str, CardInfo], trig: Dict[str, Any]) -> None:
    kind = str((trig or {}).get('kind', '') or '')
    if kind == 'enter_auto':
        pos = str(trig.get('pos', 'C') or 'C').upper()
        cn = str(trig.get('cn', '') or '')
        handle_enter_auto(gs, cards_db, pos, cn)
        return
    if kind == 'cost10_enter_draw1_auto':
        handle_stage_cost10_member_enter_draw1(gs, cards_db, entered_pos=str(trig.get('entered_pos','C') or 'C'), entered_cn=str(trig.get('entered_cn','') or ''), source_pos=str(trig.get('source_pos','') or ''))
        return
    if kind == 'yell_revealed_body_auto':
        try:
            rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 23)
        except Exception:
            rng2 = random.Random(23)
        _apply_yell_revealed_body_auto_trigger(gs, rng2, cards_db, dict(trig or {}))
        return
    if kind == 'enqueue_pending_prompt':
        prm = dict((trig or {}).get('prompt', {}) or {})
        if prm:
            gs.pending.append(prm)
        return
    if kind == 'stage_to_green_auto':
        eff = str((trig or {}).get('effect', '') or '').strip()
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        if eff:
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 17)
            except Exception:
                rng2 = random.Random(17)
            detail = _auto_effect_detail_for_condition({'source_cn': src_cn}, eff, 'このメンバーがステージから控え室に置かれたとき', timing='ステージ離脱時')
            ctx = {'source_cn': src_cn, 'auto_effect_detail': detail}
            if pos:
                ctx.update({'pos': pos, 'src_pos': pos, 'baton_new_pos': pos})
            bnew = str((trig or {}).get('baton_new_cn', '') or '').strip()
            if bnew:
                ctx['baton_new_cn'] = bnew
            try_apply_effect_template(gs, rng2, cards_db, eff, ctx)
            gs.log.append(f"[AUTO] {src_cn or '?'}[stage->green]: applied {eff}")
        return
    if kind == 'live_start_apply_effect':
        eff = str((trig or {}).get('effect', '') or '').strip()
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        if eff:
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
            except Exception:
                rng2 = random.Random(0)
            ctx = {'source_cn': src_cn}
            if pos:
                ctx.update({'pos': pos, 'src_pos': pos})
            try_apply_effect_template(gs, rng2, cards_db, eff, ctx)
            if pos:
                gs.log.append(f"[AUTO] {src_cn or '?'}[ライブ開始時]: applied {eff}")
            else:
                gs.log.append(f"[AUTO] LIVE: {src_cn or '?'}[ライブ開始時] applied {eff}")
        return
    if kind == 'live_start_choose_activate':
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        wait_opts = [p2 for p2 in ('L','C','R') if gs.stage.get(p2) and not gs.stage[p2].active]
        wait_cns = [gs.stage[p2].cardnumber for p2 in wait_opts if gs.stage.get(p2)]
        text = f"{pos}: {src_cn} ライブ開始時 → ステージのメンバーを1人までアクティブにする（スキップ可）"
        if not wait_opts:
            text += ' / 現在対象なし'
        gs.pending.append({
            'kind': 'choose_stage_member_to_activate',
            'text': text,
            'options': wait_opts + ['skip'],
            'card_options': wait_cns,
            'allow_skip': True,
            'source_pos': pos,
            'source_cn': src_cn,
            'candidates': wait_opts,
        })
        gs.log.append(f"[PENDING] {pos}: {src_cn} ライブ開始時 → activate member choice ({len(wait_opts)} candidates)")
        return
    if kind == 'live_start_score_and_pick_group_member_temp_blade':
        group_name = str((trig or {}).get('condition_group_name', '') or '虹ヶ咲')
        src_cn = _source_cn_or_default((trig or {}).get('source_cn', ''), 'この能力')
        if int(getattr(gs, 'turn', 0) or 0) != 1:
            gs.log.append(f'[SKIP] {src_cn} live-start unresolved (not 1st turn at resolution)')
            return
        _add_live_start_score_bonus(gs, 1, set_idx=(trig or {}).get('set_idx', None), source_cn=src_cn)
        gs.log.append(f'[AUTO] {src_cn} live-start: score +1')
        cands = []
        for ppos in ('L','C','R'):
            slot2 = (gs.stage or {}).get(ppos)
            if not slot2 or not getattr(slot2, 'active', False):
                continue
            ci2 = _get_card(cards_db, getattr(slot2, 'cardnumber', '') or '')
            if not ci2:
                continue
            if group_name in str(getattr(ci2, 'group', '') or ''):
                cands.append(ppos)
        if not cands:
            gs.log.append(f'[SKIP] {src_cn} live-start blade target unresolved (no {group_name} member at resolution)')
            return
        opts = []
        for _pp in list(cands):
            _sl = (gs.stage or {}).get(_pp)
            _nm = ''
            try:
                _ci = _get_card(cards_db, getattr(_sl, 'cardnumber', '') or '') if _sl else None
                _nm = str(getattr(_ci, 'name', '') or '') if _ci else ''
            except Exception:
                _nm = ''
            opts.append(f"{_pp}: {_nm}" if _nm else str(_pp))
        gs.pending.append({
            'kind': 'pick_group_member_for_temp_blade',
            'cn': _source_cn_or_default((trig or {}).get('source_cn', ''), 'この能力'),
            'text': f"【{_source_cn_or_default((trig or {}).get('source_cn', ''), 'この能力')}】ライブ開始時：『{str((trig or {}).get('condition_group_name', '') or '虹ヶ咲')}』のメンバーを1人選ぶ（このライブ終了時まで、そのメンバーはブレード+1）",
            'options': list(opts),
            'pos_options': list(cands),
        })
        gs.log.append(f"[PENDING] group-member temp blade choice ({len(cands)} candidates)")
        return
    if kind == 'live_start_optional_pay_energy_for_self_score_if_group':
        gs.pending.append({
            'kind': 'optional_pay_energy_for_self_score_if_group',
            'cn': _source_cn_or_default((trig or {}).get('source_cn', ''), 'この能力'),
            'set_idx': (trig or {}).get('set_idx', None),
            'condition_group_name': str((trig or {}).get('condition_group_name', '') or '虹ヶ咲'),
            'text': f"【{_source_cn_or_default((trig or {}).get('source_cn', ''), 'この能力')}】ライブ開始時：エネルギー2枚を支払ってもよい。自分のステージに『{str((trig or {}).get('condition_group_name', '') or '虹ヶ咲')}』のメンバーがいる場合、このカードのスコアを+1する。",
            'options': ['pay', 'skip'],
        })
        return
    if kind == 'live_start_if_stage_group_cost_then_draw_then_ordered_topdeck':
        group_name = str((trig or {}).get('condition_group_name', '') or '虹ヶ咲')
        min_cost = int((trig or {}).get('condition_min_cost', 20) or 20)
        src_cn = _source_cn_or_default((trig or {}).get('source_cn', ''), 'この能力')
        if not _stage_all_group_cost_ready(gs, cards_db, group_name, min_cost):
            gs.log.append(f'[SKIP] {src_cn} live-start unresolved (condition not met at resolution)')
            return
        gs.pending.append({
            'kind': 'execute_draw_then_choose_hand_cards_ordered_topdeck',
            'cn': src_cn,
            'text': f'【{src_cn}】ライブ開始時：条件達成 → 3枚引き、手札を3枚好きな順番でデッキの上に置く',
            'options': ['ok'],
        })
        return
    if kind == 'live_start_top_keep_one_then_reveal_top_score_if_live_by_group_count':
        group_name = str((trig or {}).get('condition_group_name', '') or '虹ヶ咲')
        src_cn = _source_cn_or_default((trig or {}).get('source_cn', ''), 'この能力')
        _niji_n = _count_stage_group_members(gs, cards_db, group_name)
        if _niji_n <= 0:
            gs.log.append(f'[SKIP] {src_cn} live-start unresolved (no {group_name} member at resolution)')
            return
        gs.pending.append({
            'kind': 'execute_top_keep_one_then_reveal_top_score_if_live',
            'cn': src_cn,
            'text': f'【{src_cn}】ライブ開始時：ステージの『{group_name}』メンバー数ぶんデッキ上を見る → 1枚をデッキ上、残りを控え室。さらにデッキトップを公開し、ライブカードならスコア+1',
            'options': ['ok'],
            'k': int(_niji_n),
        })
        return
    if kind == 'live_start_convert_revealed_colors_to_single_color_until_end_of_live':
        target_color_jp = str((trig or {}).get('target_color_jp', '') or '青').strip()
        target_key = _HEART_ICON_COLOR_MAP.get(target_color_jp, 'blue')
        if target_key == 'blue':
            gs.vivid_world_blue_mode_this_live = True
            gs.log.append('[AUTO] VIVID WORLD live-start: cheer pink/red/yellow/green/purple/all -> blue until end of live')
        else:
            gs.log.append(f'[WARN] live-start color-convert unsupported target={target_color_jp}')
        return
    if kind == 'live_start_reduce_any_if_opponent_wait_exists_manual':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        reduce_any = int((trig or {}).get('reduce_any', 0) or 0)
        set_idx = (trig or {}).get('set_idx', None)
        try:
            _mark_live_start_set_idx_resolved(gs, set_idx)
        except Exception:
            pass
        if _opponent_wait_count(gs) <= 0:
            gs.log.append(f'[SKIP] {src_cn}[ライブ開始時]: opponent_wait_count=0 -> required(any) unchanged')
            return
        if reduce_any > 0:
            if set_idx is not None:
                _rmap = dict(getattr(gs, 'live_start_required_any_reduction_by_set_idx', {}) or {})
                _rmap[int(set_idx)] = max(int(_rmap.get(int(set_idx), 0) or 0), int(reduce_any))
                gs.live_start_required_any_reduction_by_set_idx = _rmap
            else:
                _k = _canon_cardno(src_cn)
                _rmap = dict(getattr(gs, 'live_start_required_any_reduction_by_cn', {}) or {})
                _rmap[_k] = max(int(_rmap.get(_k, 0) or 0), int(reduce_any))
                gs.live_start_required_any_reduction_by_cn = _rmap
        gs.log.append(f'[AUTO] {src_cn}[ライブ開始時]: opponent_wait_count={_opponent_wait_count(gs)} -> required(any) -{reduce_any}')
        return
    if kind == 'live_start_score_if_live_zone_group_count_at_least':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        need = int((trig or {}).get('condition_count', 0) or 0)
        delta = int((trig or {}).get('score_delta', 0) or 0)
        gs.pending.append({
            'kind': 'live_start_score_if_live_zone_group_count_at_least',
            'source_cn': src_cn,
            'set_idx': (trig or {}).get('set_idx', None),
            'condition_group_name': group_name,
            'condition_count': need,
            'score_delta': delta,
            'text': f'【{src_cn}】ライブ開始時：自分のライブ中の『{group_name}』のカードが{need}枚以上ある場合、このカードのスコアを+{delta}する。',
            'options': ['ok'],
        })
        return
    if kind == 'live_start_score_if_green_live_group_count_at_least':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        need = int((trig or {}).get('condition_count', 0) or 0)
        delta = int((trig or {}).get('score_delta', 0) or 0)
        gs.pending.append({
            'kind': 'live_start_score_if_green_live_group_count_at_least',
            'source_cn': src_cn,
            'set_idx': (trig or {}).get('set_idx', None),
            'condition_group_name': group_name,
            'condition_count': need,
            'score_delta': delta,
            'text': f'【{src_cn}】ライブ開始時：控え室に『{group_name}』のライブカードが{need}枚以上あるなら、このカードのスコアを+{delta}する。',
            'options': ['ok'],
        })
        return
    if kind == 'live_start_score_per_stage_group_member_heart_color_kind':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        per = int((trig or {}).get('score_delta_per_kind', 0) or 0)
        gs.pending.append({
            'kind': 'live_start_score_per_stage_group_member_heart_color_kind',
            'source_cn': src_cn,
            'set_idx': (trig or {}).get('set_idx', None),
            'condition_group_name': group_name,
            'score_delta_per_kind': per,
            'text': f'【{src_cn}】ライブ開始時：自分のステージにいる『{group_name}』のメンバーが持つ色1種類につき、このカードのスコアを+{per}する。',
            'options': ['ok'],
        })
        return
    if kind == 'live_start_score_if_success_zone_has_scores':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        a = int((trig or {}).get('score_a', 0) or 0)
        b = int((trig or {}).get('score_b', 0) or 0)
        one = int((trig or {}).get('score_delta_one', 0) or 0)
        both = int((trig or {}).get('score_delta_both', 0) or 0)
        gs.pending.append({
            'kind': 'live_start_score_if_success_zone_has_scores',
            'source_cn': src_cn,
            'set_idx': (trig or {}).get('set_idx', None),
            'score_a': a,
            'score_b': b,
            'score_delta_one': one,
            'score_delta_both': both,
            'text': f'【{src_cn}】ライブ開始時：成功ライブカード置き場にスコア{a}/{b}があるなら+{one}、両方あるなら代わりに+{both}。',
            'options': ['ok'],
        })
        return
    if kind == 'live_start_score_if_green_unique_live_names_group_count':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        c1 = int((trig or {}).get('condition_count_one', 0) or 0)
        d1 = int((trig or {}).get('score_delta_one', 0) or 0)
        c2 = int((trig or {}).get('condition_count_two', 0) or 0)
        d2 = int((trig or {}).get('score_delta_two', 0) or 0)
        gs.pending.append({
            'kind': 'live_start_score_if_green_unique_live_names_group_count',
            'source_cn': src_cn,
            'set_idx': (trig or {}).get('set_idx', None),
            'condition_group_name': group_name,
            'condition_count_one': c1,
            'score_delta_one': d1,
            'condition_count_two': c2,
            'score_delta_two': d2,
            'text': f'【{src_cn}】ライブ開始時：控え室にカード名の異なる『{group_name}』のライブカードが{c1}枚以上なら+{d1}、{c2}枚以上なら代わりに+{d2}。',
            'options': ['ok'],
        })
        return
    if kind == 'live_start_score_and_increase_any_per_success_zone_cardname_count':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        cardname = str((trig or {}).get('condition_cardname', '') or '')
        per_score = int((trig or {}).get('score_delta_per', 0) or 0)
        per_any = int((trig or {}).get('required_any_increase_per', 0) or 0)
        gs.pending.append({
            'kind': 'live_start_score_and_increase_any_per_success_zone_cardname_count',
            'source_cn': src_cn,
            'set_idx': (trig or {}).get('set_idx', None),
            'condition_cardname': cardname,
            'score_delta_per': per_score,
            'required_any_increase_per': per_any,
            'text': f'【{src_cn}】ライブ開始時：成功ライブカード置き場の「{cardname}」1枚につき、スコア+{per_score}、必要ハート<(任意)>を+{per_any}',
            'options': ['ok'],
        })
        return
    if kind == 'live_start_reduce_any_and_score_if_success_score_at_least':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        reduce_th = int((trig or {}).get('reduce_threshold', 0) or 0)
        reduce_any = int((trig or {}).get('reduce_any', 0) or 0)
        score_th = int((trig or {}).get('score_threshold', 0) or 0)
        delta = int((trig or {}).get('score_delta', 0) or 0)
        gs.pending.append({
            'kind': 'live_start_reduce_any_and_score_if_success_score_at_least',
            'source_cn': src_cn,
            'set_idx': (trig or {}).get('set_idx', None),
            'reduce_threshold': reduce_th,
            'reduce_any': reduce_any,
            'score_threshold': score_th,
            'score_delta': delta,
            'text': f'【{src_cn}】ライブ開始時：成功ライブカード置き場のスコア合計が{reduce_th}以上なら必要ハート<(任意)>を-{reduce_any}、{score_th}以上ならさらにこのカードのスコアを+{delta}する。',
            'options': ['ok'],
        })
        return
    if kind == 'live_start_score_if_either_success_count_and_distinct_stage_names_at_least':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        need_success = int((trig or {}).get('condition_success_count', 0) or 0)
        need_names = int((trig or {}).get('condition_distinct_names', 0) or 0)
        delta = int((trig or {}).get('score_delta', 0) or 0)
        own_n = len(list(getattr(gs, 'success_zone', []) or []))
        name_n = int(_stage_distinct_member_name_count(gs, cards_db))
        set_idx = (trig or {}).get('set_idx', None)
        if name_n < need_names:
            gs.pending.append({
                'kind': 'message_ack',
                'label': f'{src_cn} live-start success-count/name condition failed',
                'text': f'【{src_cn}】ライブ開始時：名前の異なるメンバーは{name_n}/{need_names}人のため、スコア+{delta}は適用されません。',
            })
            gs.log.append(f'[PENDING] {src_cn}[ライブ開始時]: distinct stage names {name_n}/{need_names} -> no score bonus')
            return
        if own_n >= need_success:
            gs.pending.append({
                'kind': 'live_start_success_count_distinct_names_score_ack',
                'source_cn': src_cn,
                'set_idx': set_idx,
                'score_delta': delta,
                'own_success_count': own_n,
                'condition_success_count': need_success,
                'distinct_name_count': name_n,
                'condition_distinct_names': need_names,
                'text': f'【{src_cn}】ライブ開始時：自分の成功ライブカード置き場={own_n}/{need_success}枚、名前の異なるメンバー={name_n}/{need_names}人。条件達成のため、このカードのスコアを+{delta}します。',
                'options': ['ok'],
            })
            gs.log.append(f'[PENDING] {src_cn}[ライブ開始時]: own success {own_n}/{need_success} and names {name_n}/{need_names} -> score +{delta}')
            return
        gs.pending.append({
            'kind': 'confirm_effect',
            'text': f'【{src_cn}】ライブ開始時：自分の成功ライブカード置き場は{own_n}/{need_success}枚、名前の異なるメンバーは{name_n}/{need_names}人です。相手の成功ライブカード置き場にカードが{need_success}枚以上ある場合、このカードのスコアを+{delta}します。条件を満たす場合は「使う」、満たさない場合は「スキップ」を選んでください。',
            'options': ['使う', 'スキップ'],
            'source_cn': src_cn,
            'after_live_start_score_bonus': {'source_cn': src_cn, 'set_idx': set_idx, 'bonus': delta, 'detail': f'opponent success-zone cards >= {need_success}; distinct names={name_n}'},
            'effect_text': _auto_trigger_effect_text(trig or {}),
        })
        gs.log.append(f'[PENDING] {src_cn}[ライブ開始時]: opponent success-count confirmation needed own={own_n}/{need_success}, names={name_n}/{need_names}')
        return

    if kind == 'live_start_score_if_own_success_count_less_than_opponent_manual':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        delta = int((trig or {}).get('score_delta', 0) or 0)
        own_n = len(list(getattr(gs, 'success_zone', []) or []))
        gs.pending.append({
            'kind': 'confirm_effect',
            'text': f'【{src_cn}】ライブ開始時：自分の成功ライブカード置き場は{own_n}枚です。相手の成功ライブカード置き場のカード枚数が自分より多い場合、このカードのスコアを+{delta}します。条件を満たす場合は「使う」、満たさない場合は「スキップ」を選んでください。',
            'options': ['使う', 'スキップ'],
            'source_cn': src_cn,
            'after_live_start_score_bonus': {'source_cn': src_cn, 'set_idx': (trig or {}).get('set_idx', None), 'bonus': delta, 'detail': f'opponent success-zone cards > own {own_n}'},
            'effect_text': _auto_trigger_effect_text(trig or {}),
        })
        gs.log.append(f'[PENDING] {src_cn}[ライブ開始時]: opponent success-count greater confirmation own={own_n}')
        return

    if kind == 'live_start_reduce_any_if_opponent_wait_exists_manual':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        reduce_any = int((trig or {}).get('reduce_any', 0) or 0)
        set_idx = (trig or {}).get('set_idx', None)
        try:
            _mark_live_start_set_idx_resolved(gs, set_idx)
        except Exception:
            pass
        if _opponent_wait_count(gs) <= 0:
            gs.log.append(f'[SKIP] {src_cn}[ライブ開始時]: opponent_wait_count=0 -> required(any) unchanged')
            return
        if reduce_any > 0:
            if set_idx is not None:
                _rmap = dict(getattr(gs, 'live_start_required_any_reduction_by_set_idx', {}) or {})
                _rmap[int(set_idx)] = max(int(_rmap.get(int(set_idx), 0) or 0), int(reduce_any))
                gs.live_start_required_any_reduction_by_set_idx = _rmap
            else:
                _k = _canon_cardno(src_cn)
                _rmap = dict(getattr(gs, 'live_start_required_any_reduction_by_cn', {}) or {})
                _rmap[_k] = max(int(_rmap.get(_k, 0) or 0), int(reduce_any))
                gs.live_start_required_any_reduction_by_cn = _rmap
        gs.log.append(f'[AUTO] {src_cn}[ライブ開始時]: opponent_wait_count={_opponent_wait_count(gs)} -> required(any) -{reduce_any}')
        return
    if kind == 'live_start_topdeck_green_group_members_upto_opponent_wait_count_manual':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        try:
            _mark_live_start_set_idx_resolved(gs, (trig or {}).get('set_idx', None))
        except Exception:
            pass
        n_wait = _opponent_wait_count(gs)
        if n_wait <= 0:
            gs.log.append(f'[SKIP] {src_cn}[ライブ開始時]: opponent_wait_count=0 -> no topdeck')
            return
        _enqueue_topdeck_from_green(gs, cards_db, kind='MEMBER', n=n_wait, group=group_name, allow_less=True)
        gs.log.append(f'[PENDING] {src_cn}[ライブ開始時]: opponent_wait_count={n_wait} -> topdeck up to {n_wait} 『{group_name}』 member(s) from green')
        return
    if kind == 'live_start_center_member_gain_all_if_distinct_stage_groups_at_least':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        need = int((trig or {}).get('condition_distinct_groups', 0) or 0)
        all_n = int((trig or {}).get('all_n', 0) or 0)
        got = int(_stage_distinct_member_group_name_count(gs, cards_db))
        slot = (gs.stage or {}).get('C')
        if got >= need and slot and getattr(slot, 'cardnumber', ''):
            ci_c = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
            if ci_c and not _is_live_ci(ci_c):
                if all_n > 0:
                    _grant_temp_heart(slot, 'all', all_n)
                gs.log.append(f'[AUTO] {src_cn}[ライブ開始時]: distinct stage groups {got}/{need} -> center gains <ALL> x{all_n}')
                return
        gs.pending.append({
            'kind': 'message_ack',
            'label': f'{src_cn} live-start distinct group condition failed',
            'text': f'【{src_cn}】ライブ開始時：ステージの異なるグループ名は{got}/{need}種類のため、センターへの<ALL>付与は適用されません。',
        })
        gs.log.append(f'[SKIP] {src_cn}[ライブ開始時]: distinct stage groups {got}/{need} -> no <ALL>')
        return

    if kind == 'live_start_member_gain_blade_if_stage_has_heart_colors':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        pos = str((trig or {}).get('pos', '') or '').upper()
        colors = list((trig or {}).get('condition_colors', []) or [])
        blade_n = int((trig or {}).get('blade_n', 0) or 0)
        ok, have, missing = _stage_member_has_all_heart_colors(gs, cards_db, colors)
        slot = (gs.stage or {}).get(pos) if pos in ('L', 'C', 'R') else None
        if ok and slot and getattr(slot, 'cardnumber', '') and blade_n > 0:
            slot.temp_blade = int(getattr(slot, 'temp_blade', 0) or 0) + int(blade_n)
            slot.temp_until = 'end_of_live'
            gs.log.append(f'[AUTO] {pos}: {src_cn}[ライブ開始時]: stage hearts {_heart_color_keys_to_jp(colors)} all present -> blade +{blade_n}')
            return
        gs.pending.append({
            'kind': 'message_ack',
            'label': f'{src_cn} live-start stage heart condition failed',
            'text': f'【{src_cn}】ライブ開始時：必要なハート色={_heart_color_keys_to_jp(colors)} / 不足={_heart_color_keys_to_jp(missing)} のため、ブレード+{blade_n}は適用されません。',
        })
        gs.log.append(f'[SKIP] {pos}: {src_cn}[ライブ開始時]: missing stage heart colors={_heart_color_keys_to_jp(missing)}')
        return

    if kind == 'live_start_score_if_stage_has_heart_colors':
        src_cn = str((trig or {}).get('source_cn', '') or '')
        colors = list((trig or {}).get('condition_colors', []) or [])
        delta = int((trig or {}).get('score_delta', 0) or 0)
        set_idx = (trig or {}).get('set_idx', None)
        ok, have, missing = _stage_member_has_all_heart_colors(gs, cards_db, colors)
        if ok and delta:
            _add_live_start_score_bonus(gs, delta, set_idx=set_idx, source_cn=src_cn)
            gs.log.append(f'[AUTO] {src_cn}[ライブ開始時]: stage hearts {_heart_color_keys_to_jp(colors)} all present -> score +{delta}')
            return
        gs.pending.append({
            'kind': 'message_ack',
            'label': f'{src_cn} live-start stage heart condition failed',
            'text': f'【{src_cn}】ライブ開始時：必要なハート色={_heart_color_keys_to_jp(colors)} / 不足={_heart_color_keys_to_jp(missing)} のため、スコア+{delta}は適用されません。',
        })
        gs.log.append(f'[SKIP] {src_cn}[ライブ開始時]: missing stage heart colors={_heart_color_keys_to_jp(missing)}')
        return

    if kind == 'add_live_success_score_bonus_per_weight_member':
        cn_live = str((trig or {}).get('source_cn', '') or '')
        per = int((trig or {}).get('bonus_per', 0) or 0)
        n = int(_stage_wait_member_count(gs, cards_db))
        bonus = int(per * n)
        _add_live_success_score_bonus(gs, cn_live, bonus, detail=(f"wait members={n}" if n > 0 else "wait members=0"))
        return
    if kind in ('enqueue_choose_effects_from_ability_on_live_success', 'success_enqueue_choose_effects'):
        ab = dict((trig or {}).get('ability', {}) or {})
        ctx = dict((trig or {}).get('ctx', {}) or {})
        _enqueue_choose_effects_from_ability(gs, cards_db, ab, ctx)
        return
    if kind in ('enqueue_optional_discard_from_hand_for_effect_on_live_success', 'success_enqueue_pay_effect'):
        prm = dict((trig or {}).get('prompt', {}) or {})
        if prm:
            gs.pending.append(prm)
        return
    if kind in ('enqueue_success_prompt', 'success_enqueue_prompt'):
        prm = dict((trig or {}).get('prompt', {}) or {})
        if prm:
            gs.pending.append(prm)
        return
    if kind in ('apply_effect_template_on_live_success', 'success_apply_effect'):
        eff = str((trig or {}).get('effect', '') or '').strip()
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        ctx = dict((trig or {}).get('ctx', {}) or {})
        if src_cn and not ctx.get('source_cn'):
            ctx['source_cn'] = src_cn
        if pos:
            ctx.setdefault('pos', pos)
        if eff:
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 41)
            except Exception:
                rng2 = random.Random(41)
            try_apply_effect_template(gs, rng2, cards_db, eff, ctx)
            if pos:
                gs.log.append(f"[AUTO] {pos}: {src_cn or '?'}[ライブ成功時] applied {eff}")
            else:
                gs.log.append(f"[AUTO] LIVE: {src_cn or '?'}[ライブ成功時] applied {eff}")
        return
    if kind in ('apply_effect_template_if_excess_color_and_stage_group_on_live_success', 'success_apply_effect_if_excess_color_and_stage_group'):
        eff = str((trig or {}).get('effect', '') or '').strip()
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        ctx = dict((trig or {}).get('ctx', {}) or {})
        color_jp = str((trig or {}).get('condition_color_jp', '') or '').strip()
        group_name = str((trig or {}).get('condition_group_name', '') or '').strip()
        if not _live_success_excess_color_and_stage_group_met(gs, cards_db, color_jp, group_name):
            if pos:
                gs.log.append(f"[SKIP] {pos}: {src_cn or '?'}[ライブ成功時] unresolved (condition not met at resolution: excess {color_jp} + stage {group_name})")
            else:
                gs.log.append(f"[SKIP] LIVE: {src_cn or '?'}[ライブ成功時] unresolved (condition not met at resolution: excess {color_jp} + stage {group_name})")
            return
        if src_cn and not ctx.get('source_cn'):
            ctx['source_cn'] = src_cn
        if pos:
            ctx.setdefault('pos', pos)
        if eff:
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 41)
            except Exception:
                rng2 = random.Random(41)
            try_apply_effect_template(gs, rng2, cards_db, eff, ctx)
            if pos:
                gs.log.append(f"[AUTO] {pos}: {src_cn or '?'}[ライブ成功時] applied {eff}")
            else:
                gs.log.append(f"[AUTO] LIVE: {src_cn or '?'}[ライブ成功時] applied {eff}")
        return
    if kind in ('apply_effect_template_if_stage_named_members_at_least_on_live_success',):
        eff = str((trig or {}).get('effect', '') or '').strip()
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        ctx = dict((trig or {}).get('ctx', {}) or {})
        names = list((trig or {}).get('condition_names', []) or [])
        need = int((trig or {}).get('condition_count', 0) or 0)
        got = int(_stage_distinct_named_members_from_list_count(gs, cards_db, names))
        if got < need:
            gs.log.append(f"[SKIP] LIVE: {src_cn}[ライブ成功時] unresolved (stage named members: {got} < {need}; names={names})")
            return
        if src_cn and not ctx.get('source_cn'):
            ctx['source_cn'] = src_cn
        if pos:
            ctx.setdefault('pos', pos)
        if eff:
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 43)
            except Exception:
                rng2 = random.Random(43)
            if try_apply_effect_template(gs, rng2, cards_db, eff, ctx):
                gs.log.append(f"[AUTO] LIVE: {src_cn}[ライブ成功時] applied {eff} (stage named members {got}/{need})")
            else:
                gs.log.append(f"[WARN] LIVE: {src_cn}[ライブ成功時] effect not matchable after stage named condition: {eff}")
        return


    if kind in ('add_live_success_score_bonus_if_revealed_live_or_stage_heart_kinds_or_moved',):
        src_cn = str((trig or {}).get('source_cn', '') or '')
        need_live = int((trig or {}).get('condition_revealed_live_count', 0) or 0)
        need_kinds = int((trig or {}).get('condition_stage_heart_kind_count', 0) or 0)
        bonus = int((trig or {}).get('bonus', 0) or 0)
        got_live = int(_count_yell_revealed_live_cards(gs, cards_db))
        got_kinds = int(_stage_member_heart_color_kind_count(gs, cards_db))
        if got_live >= need_live or got_kinds >= need_kinds:
            why = f"revealed LIVE={got_live}/{need_live}, stage heart kinds={got_kinds}/{need_kinds}"
            _add_live_success_score_bonus(gs, src_cn, bonus, detail=why)
            return
        gs.pending.append({
            'kind': 'confirm_effect',
            'text': f'{src_cn}[ライブ成功時] エール公開ライブは{got_live}/{need_live}枚、ステージのハート種類数は{got_kinds}/{need_kinds}種類です。このターンに自分のステージにいるメンバーがエリアを移動している場合、このカードのスコアを+{bonus}します。条件を満たす場合は「使う」、満たさない場合は「スキップ」を選んでください。',
            'options': ['apply', 'skip'],
            'after_live_success_score_bonus': {'source_cn': src_cn, 'bonus': bonus, 'detail': f'manual position-change condition; revealed LIVE={got_live}/{need_live}; stage heart kinds={got_kinds}/{need_kinds}'},
            'source_cn': src_cn,
        })
        gs.log.append(f"[PENDING] LIVE: {src_cn}[ライブ成功時] manual position-change check; revealed LIVE={got_live}/{need_live}, stage heart kinds={got_kinds}/{need_kinds}")
        return

    if kind in ('add_live_success_total_score_bonus_if_revealed_live_count_tier',):
        src_cn = str((trig or {}).get('source_cn', '') or '')
        pos = str((trig or {}).get('pos', '') or '').upper()
        c1 = int((trig or {}).get('condition_count_one', 1) or 1)
        b1 = int((trig or {}).get('bonus_one', 0) or 0)
        c2 = int((trig or {}).get('condition_count_two', 0) or 0)
        b2 = int((trig or {}).get('bonus_two', 0) or 0)
        got = int(_count_yell_revealed_live_cards(gs, cards_db))
        if c2 and got >= c2:
            _add_live_success_total_score_bonus(gs, cards_db, b2, detail=f"revealed LIVE={got}/{c2} -> tier bonus", source_cn=src_cn, pos=pos)
        elif got >= c1:
            _add_live_success_total_score_bonus(gs, cards_db, b1, detail=f"revealed LIVE={got}/{c1} -> tier bonus", source_cn=src_cn, pos=pos)
        else:
            gs.log.append(f"[SKIP] {pos + ': ' if pos else ''}{src_cn}[ライブ成功時] unresolved (revealed LIVE={got} < {c1})")
        return

    if kind in ('apply_effect_template_if_revealed_live_count_at_least_on_live_success',):
        eff = str((trig or {}).get('effect', '') or '').strip()
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        ctx = dict((trig or {}).get('ctx', {}) or {})
        need = int((trig or {}).get('condition_count', 0) or 0)
        got = int(_count_yell_revealed_live_cards(gs, cards_db))
        if got >= need and eff:
            rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 31)
            if try_apply_effect_template(gs, rng2, cards_db, eff, ctx):
                if pos:
                    gs.log.append(f"[AUTO] {pos}: {src_cn or '?'}[ライブ成功時] applied {eff}")
                else:
                    gs.log.append(f"[AUTO] LIVE: {src_cn or '?'}[ライブ成功時] applied {eff}")
        else:
            gs.log.append(f"[SKIP] LIVE: {src_cn}[ライブ成功時] unresolved (revealed live cards: {got} < {need})")
        return
    if kind in ('put_wait_energy_if_revealed_live_count_at_least',):
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        need = int((trig or {}).get('condition_count', 0) or 0)
        count = int((trig or {}).get('count', 0) or 0)
        got = int(_count_yell_revealed_live_cards(gs, cards_db))
        if got >= need and count > 0:
            _put_energy_from_deck(gs, count, to_wait=True)
            gs.log.append(f"[AUTO] LIVE: {src_cn}[ライブ成功時]: revealed live cards: {got} -> wait energy +{count}")
        else:
            gs.log.append(f"[SKIP] LIVE: {src_cn}[ライブ成功時] unresolved (revealed live cards: {got} < {need})")
        return
    if kind in ('add_live_success_total_score_bonus_if_revealed_group_live_score_tag_at_least',):
        src_cn = str((trig or {}).get('source_cn', '') or '')
        pos = str((trig or {}).get('pos', '') or '').upper()
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        need = int((trig or {}).get('condition_count', 0) or 0)
        bonus = int((trig or {}).get('bonus', 0) or 0)
        got = int(_count_yell_revealed_group_live_cards_with_tag(gs, cards_db, group_name, '<(スコア+1)>'))
        if got >= need and bonus:
            _add_live_success_total_score_bonus(gs, cards_db, bonus, detail=f"revealed 『{group_name}』 LIVE with <スコア+1>: {got}/{need}", source_cn=src_cn, pos=pos)
        else:
            gs.log.append(f"[SKIP] {pos + ': ' if pos else ''}{src_cn}[ライブ成功時] unresolved (revealed 『{group_name}』 LIVE with <スコア+1>: {got} < {need})")
        return
    if kind in ('draw_if_revealed_score_tag_live_or_success_score_above_original',):
        src_cn = str((trig or {}).get('source_cn', '') or '')
        pos = str((trig or {}).get('pos', '') or '').upper()
        got = int(_count_yell_revealed_live_cards_with_tag(gs, cards_db, '<(スコア+1)>'))
        if got >= 1:
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
            except Exception:
                rng2 = random.Random()
            drew = draw(gs, 1, rng2)
            gs.log.append(f"[AUTO] {pos + ': ' if pos else ''}{src_cn}[ライブ成功時]: revealed LIVE with <スコア+1>={got} -> draw {drew}")
            return
        gs.pending.append({
            'kind': 'confirm_effect',
            'text': f'{src_cn}[ライブ成功時] エール公開に<スコア+1>を持つライブカードはありません。自分のライブカード置き場に元々のスコアより高いスコアのライブカードがある場合、カードを1枚引きます。条件を満たすなら Apply、満たさないなら Skip。',
            'options': ['apply', 'skip'],
            'after_effect_template': 'カードを1枚引く。',
            'ctx': {'source_cn': src_cn, 'pos': pos} if pos else {'source_cn': src_cn},
            'source_cn': src_cn,
        })
        gs.log.append(f"[PENDING] {pos + ': ' if pos else ''}{src_cn}[ライブ成功時] success-zone above-original score condition manual; revealed score tag LIVE={got}")
        return
    if kind in ('add_live_success_score_bonus_if_revealed_group_member_count_at_least',):
        cn_live = str((trig or {}).get('source_cn', '') or '')
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        need = int((trig or {}).get('condition_count', 0) or 0)
        bonus = int((trig or {}).get('bonus', 0) or 0)
        got = int(_count_yell_revealed_group_members(gs, cards_db, group_name))
        if got >= need:
            _add_live_success_score_bonus(gs, cn_live, bonus, detail=f"revealed 『{group_name}』 members: {got}")
        else:
            gs.log.append(f"[SKIP] LIVE: {cn_live}[ライブ成功時] unresolved (revealed 『{group_name}』 members: {got} < {need})")
        return
    if kind in ('add_live_success_score_bonus_if_revealed_live_count_at_least',):
        cn_live = str((trig or {}).get('source_cn', '') or '')
        need = int((trig or {}).get('condition_count', 0) or 0)
        bonus = int((trig or {}).get('bonus', 0) or 0)
        got = int(_count_yell_revealed_live_cards(gs, cards_db))
        if got >= need:
            _add_live_success_score_bonus(gs, cn_live, bonus, detail=f"revealed live cards: {got}")
        else:
            gs.log.append(f"[SKIP] LIVE: {cn_live}[ライブ成功時] unresolved (revealed live cards: {got} < {need})")
        return
    if kind in ('add_live_success_score_bonus_if_revealed_group_live_has_tag',):
        cn_live = str((trig or {}).get('source_cn', '') or '')
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        tag = str((trig or {}).get('condition_tag', '') or '')
        bonus = int((trig or {}).get('bonus', 0) or 0)
        got = 0
        for cn2 in list(getattr(gs, '_yell_revealed_this_live', []) or []):
            ci2 = _get_card(cards_db, cn2)
            if not ci2 or not _is_live_ci(ci2):
                continue
            if group_name and group_name not in str(getattr(ci2, 'group', '') or ''):
                continue
            if _ci_blade_heart_has_tag(ci2, tag):
                got += 1
        if got >= 1:
            _add_live_success_score_bonus(gs, cn_live, bonus, detail=f"revealed 『{group_name}』 live with {tag}: {got}")
        else:
            gs.log.append(f"[SKIP] LIVE: {cn_live}[ライブ成功時] unresolved (revealed 『{group_name}』 live with {tag}: 0)")
        return
    if kind in ('put_wait_energy_if_revealed_group_card_count_at_least',):
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        need = int((trig or {}).get('condition_count', 0) or 0)
        count = int((trig or {}).get('count', 0) or 0)
        got = int(_count_yell_revealed_group_cards(gs, cards_db, group_name))
        if got >= need and count > 0:
            _put_energy_from_deck(gs, count, to_wait=True)
            gs.log.append(f"[AUTO] LIVE: {src_cn}[ライブ成功時]: revealed 『{group_name}』 cards: {got} -> wait energy +{count}")
        else:
            gs.log.append(f"[SKIP] LIVE: {src_cn}[ライブ成功時] unresolved (revealed 『{group_name}』 cards: {got} < {need})")
        return
    if kind in ('add_live_success_score_bonus_if_revealed_distinct_named_group_member_count_at_least',):
        cn_live = str((trig or {}).get('source_cn', '') or '')
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        need = int((trig or {}).get('condition_count', 0) or 0)
        bonus = int((trig or {}).get('bonus', 0) or 0)
        got = int(_count_yell_revealed_distinct_named_group_members(gs, cards_db, group_name))
        if got >= need:
            _add_live_success_score_bonus(gs, cn_live, bonus, detail=f"revealed distinct 『{group_name}』 members: {got}")
        else:
            msg = f"条件未達：エールにより公開された自分のカードの中の、名前が異なる『{group_name}』のメンバーカードは {got}/{need} 枚です。この効果は解決されません。"
            gs.log.append(f"[SKIP] LIVE: {cn_live}[ライブ成功時] unresolved (revealed distinct 『{group_name}』 members: {got} < {need})")
            gs.pending.append({
                'kind': 'effect_notice',
                'text': msg,
                'options': ['ok'],
                'source_cn': cn_live,
                'effect_text': _auto_trigger_effect_text(trig or {}),
            })
        return
    if kind in ('apply_effect_template_if_revealed_distinct_named_group_member_count_at_least_on_live_success',):
        eff = str((trig or {}).get('effect', '') or '').strip()
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        ctx = dict((trig or {}).get('ctx', {}) or {})
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        need = int((trig or {}).get('condition_count', 0) or 0)
        got = int(_count_yell_revealed_distinct_named_group_members(gs, cards_db, group_name))
        if got >= need and eff:
            rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 37)
            if try_apply_effect_template(gs, rng2, cards_db, eff, ctx):
                if pos:
                    gs.log.append(f"[AUTO] {pos}: {src_cn or '?'}[ライブ成功時] applied {eff}")
                else:
                    gs.log.append(f"[AUTO] LIVE: {src_cn or '?'}[ライブ成功時] applied {eff}")
        else:
            msg = f"条件未達：エールにより公開された自分のカードの中の、名前が異なる『{group_name}』のメンバーカードは {got}/{need} 枚です。この効果は解決されません。"
            gs.log.append(f"[SKIP] LIVE: {src_cn}[ライブ成功時] unresolved (revealed distinct 『{group_name}』 members: {got} < {need})")
            gs.pending.append({
                'kind': 'effect_notice',
                'text': msg,
                'options': ['ok'],
                'source_cn': src_cn,
                'effect_text': _auto_trigger_effect_text(trig or {}),
            })
        return
    if kind in ('apply_effect_template_if_revealed_no_bladeheart_group_member_at_least_on_live_success',):
        eff = str((trig or {}).get('effect', '') or '').strip()
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        ctx = dict((trig or {}).get('ctx', {}) or {})
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        need = int((trig or {}).get('condition_count', 1) or 1)
        got = int(_count_yell_revealed_no_bladeheart_group_members(gs, cards_db, group_name))
        if got >= need and eff:
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 53)
            except Exception:
                rng2 = random.Random(53)
            if pos and not ctx.get('pos'):
                ctx['pos'] = pos
            if src_cn and not ctx.get('source_cn'):
                ctx['source_cn'] = src_cn
            if try_apply_effect_template(gs, rng2, cards_db, eff, ctx):
                gs.log.append(f"[AUTO] {pos + ': ' if pos else ''}{src_cn}[ライブ成功時]: no-bladeheart 『{group_name}』 MEMBER revealed={got}/{need} -> applied {eff}")
            else:
                gs.log.append(f"[WARN] {pos + ': ' if pos else ''}{src_cn}[ライブ成功時]: effect not matchable after no-bladeheart condition: {eff}")
        else:
            gs.log.append(f"[SKIP] {pos + ': ' if pos else ''}{src_cn}[ライブ成功時] unresolved (no-bladeheart 『{group_name}』 MEMBER revealed: {got} < {need})")
        return

    if kind in ('reveal_top_to_hand_then_live_total_score_if_no_bladeheart_member',):
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        bonus = int((trig or {}).get('bonus', 0) or 0)
        try:
            rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 59)
        except Exception:
            rng2 = random.Random(59)
        if not list(getattr(gs, 'deck', []) or []):
            try:
                _rule_refresh_main_deck(gs, rng2, reason='top reveal for no-bladeheart member')
            except Exception:
                pass
        top_cn = str((getattr(gs, 'deck', []) or [''])[0] or '') if list(getattr(gs, 'deck', []) or []) else ''
        drew = draw(gs, 1, rng2) if top_cn else 0
        ci_top = _get_card(cards_db, top_cn) if top_cn else None
        is_no_bh_member = bool(ci_top and _is_member_ci(ci_top) and not _ci_has_blade_heart_payload(ci_top))
        if drew <= 0:
            gs.log.append(f"[SKIP] {pos + ': ' if pos else ''}{src_cn}[ライブ成功時]: deck top reveal failed")
            return
        gs.log.append(f"[AUTO] {pos + ': ' if pos else ''}{src_cn}[ライブ成功時]: revealed deck top {top_cn} -> hand")
        if is_no_bh_member and bonus:
            _add_live_success_total_score_bonus(gs, cards_db, bonus, detail=f"top revealed {top_cn} is no-bladeheart MEMBER", source_cn=src_cn, pos=pos)
            result = f'公開したカード {top_cn} はブレードハートを持たないメンバーカードです。手札に加え、ライブの合計スコアを+{bonus}しました。'
        else:
            gs.log.append(f"[SKIP] {pos + ': ' if pos else ''}{src_cn}[ライブ成功時]: top revealed {top_cn} is not no-bladeheart MEMBER")
            result = f'公開したカード {top_cn} はブレードハートを持たないメンバーカードではありません。手札には加えますが、ライブの合計スコアは増えません。'
        gs.pending.append({
            'kind': 'show_revealed_cards_ack',
            'label': 'デッキトップ公開',
            'text': f'{src_cn}[ライブ成功時]：自分のデッキの一番上のカードを公開し、手札に加えます。\n{result}',
            'display_cards': [top_cn],
            'options': ['ok'],
            'source_cn': src_cn,
            'effect_text': _auto_trigger_effect_text(trig or {}),
        })
        return

    if kind in ('set_live_success_score_if_no_revealed_no_bladeheart_or_excess_at_least',):
        cn_live = str((trig or {}).get('source_cn', '') or '')
        need_excess = int((trig or {}).get('condition_excess_count', 0) or 0)
        target = int((trig or {}).get('target_score', 0) or 0)
        no_bh_n = int(_count_yell_revealed_no_bladeheart_cards(gs, cards_db, member_only=False) or 0)
        excess_n = int(_last_attempt_excess_heart_total(gs) or 0)
        met_no_bh = (no_bh_n == 0)
        met_excess = (excess_n >= need_excess)
        if met_no_bh or met_excess:
            reason = f"revealed no-bladeheart cards={no_bh_n}, excess hearts={excess_n}/{need_excess}"
            _set_live_success_score_to(gs, cards_db, cn_live, target, detail=reason)
        else:
            gs.log.append(f"[SKIP] LIVE: {cn_live}[ライブ成功時] unresolved (revealed no-bladeheart cards={no_bh_n} != 0 and excess hearts={excess_n} < {need_excess})")
        return
    if kind in ('adjust_live_total_score_by_excess_heart_count',):
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        zero_bonus = int((trig or {}).get('zero_excess_bonus', 0) or 0)
        high_threshold = int((trig or {}).get('high_excess_threshold', 0) or 0)
        high_delta = int((trig or {}).get('high_excess_delta', 0) or 0)
        excess_n = int(_last_attempt_excess_heart_total(gs) or 0)
        prefix = f"[AUTO] {pos}: {src_cn}[ライブ成功時]" if pos else f"[AUTO] {src_cn}[ライブ成功時]"
        if excess_n <= 0:
            _add_live_success_total_score_bonus(gs, cards_db, zero_bonus, min_total=0, detail=f"excess hearts={excess_n} -> live total score +{zero_bonus}", source_cn=src_cn, pos=pos)
        elif excess_n >= high_threshold:
            _add_live_success_total_score_bonus(gs, cards_db, high_delta, min_total=0, detail=f"excess hearts={excess_n}/{high_threshold} -> live total score {high_delta}", source_cn=src_cn, pos=pos)
        else:
            gs.log.append(f"{prefix}: excess hearts={excess_n}; no score adjustment")
        return
    if kind in ('opponent_loses_excess_hearts_then_live_score_bonus_manual',):
        cn_live = str((trig or {}).get('source_cn', '') or '').strip()
        need = int((trig or {}).get('lost_threshold', 0) or 0)
        bonus = int((trig or {}).get('bonus', 0) or 0)
        gs.pending.append({
            'kind': 'confirm_effect',
            'text': f'{cn_live}[ライブ成功時] 相手は余剰ハートをすべて失います。相手が余剰ハートを{need}つ以上失っている場合、このカードのスコアを+{bonus}します。条件を満たす場合は「使う」、満たさない場合は「スキップ」を選んでください。',
            'options': ['使う', 'スキップ'],
            'source_cn': cn_live,
            'after_live_success_score_bonus': {'cn_live': cn_live, 'bonus': bonus, 'detail': f'opponent lost excess hearts >= {need}'},
            'effect_text': _auto_trigger_effect_text(trig or {}),
        })
        gs.log.append(f"[PENDING] LIVE: {cn_live}[ライブ成功時] opponent excess-heart loss confirmation threshold={need}")
        return

    if kind in ('add_live_success_score_bonus_if_excess_total_zero',):
        cn_live = str((trig or {}).get('source_cn', '') or '').strip()
        bonus = int((trig or {}).get('bonus', 0) or 0)
        excess_n = int(_last_attempt_excess_heart_total(gs) or 0)
        if excess_n <= 0:
            _add_live_success_score_bonus(gs, cn_live, bonus, detail=f"excess hearts={excess_n} -> score +{bonus}")
        else:
            gs.log.append(f"[SKIP] LIVE: {cn_live}[ライブ成功時] unresolved (excess hearts={excess_n} > 0)")
        return
    if kind in ('apply_effect_template_if_excess_total_at_least_on_live_success',):
        eff = str((trig or {}).get('effect', '') or '').strip()
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        ctx = dict((trig or {}).get('ctx', {}) or {})
        need = int((trig or {}).get('condition_excess_count', 0) or 0)
        excess_n = int(_last_attempt_excess_heart_total(gs) or 0)
        if excess_n >= need and eff:
            if src_cn and not ctx.get('source_cn'):
                ctx['source_cn'] = src_cn
            if pos:
                ctx.setdefault('pos', pos)
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 43)
            except Exception:
                rng2 = random.Random(43)
            ok = bool(try_apply_effect_template(gs, rng2, cards_db, eff, ctx))
            prefix = f"[AUTO] {pos}: {src_cn or '?'}[ライブ成功時]" if pos else f"[AUTO] LIVE: {src_cn or '?'}[ライブ成功時]"
            gs.log.append(f"{prefix}: excess hearts={excess_n}/{need} -> {'applied' if ok else 'no_match'} {eff}")
        else:
            prefix = f"[SKIP] {pos}: {src_cn or '?'}[ライブ成功時]" if pos else f"[SKIP] LIVE: {src_cn or '?'}[ライブ成功時]"
            gs.log.append(f"{prefix} unresolved (excess hearts={excess_n} < {need})")
        return
    if kind in ('apply_effect_template_if_excess_color_at_least_on_live_success',):
        eff = str((trig or {}).get('effect', '') or '').strip()
        src_cn = str((trig or {}).get('source_cn', '') or '').strip()
        pos = str((trig or {}).get('pos', '') or '').upper()
        ctx = dict((trig or {}).get('ctx', {}) or {})
        color_jp = str((trig or {}).get('condition_color_jp', '') or '').strip()
        color_key = str((trig or {}).get('condition_color_key', '') or '').strip().lower()
        need = int((trig or {}).get('condition_count', 0) or 0)
        got = int(_last_attempt_excess_color_count(gs, color_key) or 0)
        if got >= need and eff:
            if src_cn and not ctx.get('source_cn'):
                ctx['source_cn'] = src_cn
            if pos:
                ctx.setdefault('pos', pos)
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0) + 44)
            except Exception:
                rng2 = random.Random(44)
            ok = bool(try_apply_effect_template(gs, rng2, cards_db, eff, ctx))
            prefix = f"[AUTO] {pos}: {src_cn or '?'}[ライブ成功時]" if pos else f"[AUTO] LIVE: {src_cn or '?'}[ライブ成功時]"
            gs.log.append(f"{prefix}: excess {color_jp or color_key}={got}/{need} -> {'applied' if ok else 'no_match'} {eff}")
        else:
            prefix = f"[SKIP] {pos}: {src_cn or '?'}[ライブ成功時]" if pos else f"[SKIP] LIVE: {src_cn or '?'}[ライブ成功時]"
            gs.log.append(f"{prefix} unresolved (excess {color_jp or color_key}={got} < {need})")
        return
    if kind in ('add_live_success_score_bonus_and_clear_if_excess_total_at_least', 'add_live_success_score_bonus_and_clear_if_excess_total_exact'):
        cn_live = str((trig or {}).get('source_cn', '') or '').strip()
        bonus = int((trig or {}).get('bonus', 0) or 0)
        need = int((trig or {}).get('condition_excess_count', 0) or 0)
        mode = str((trig or {}).get('condition_mode', '') or '').strip().lower()
        at_least = (kind == 'add_live_success_score_bonus_and_clear_if_excess_total_at_least') or (mode == 'at_least')
        excess_n = int(_last_attempt_excess_heart_total(gs) or 0)
        ok = (excess_n >= need) if at_least else (excess_n == need)
        cond_text = f">={need}" if at_least else f"/{need}"
        skip_text = f"< {need}" if at_least else f"!= {need}"
        if ok:
            _add_live_success_score_bonus(gs, cn_live, bonus, detail=f"excess hearts={excess_n}{cond_text}; lost all excess hearts")
            try:
                gs.last_attempt_excess_hearts = {}
            except Exception:
                pass
            gs.log.append(f"[AUTO] LIVE: {cn_live}[ライブ成功時]: excess hearts lost -> 0")
        else:
            gs.log.append(f"[SKIP] LIVE: {cn_live}[ライブ成功時] unresolved (excess hearts={excess_n} {skip_text})")
        return
    if kind in ('add_live_success_score_bonus_if_either_success_count_and_revealed_score_tag_live_at_least',):
        cn_live = str((trig or {}).get('source_cn', '') or '').strip()
        need_success = int((trig or {}).get('condition_success_count', 0) or 0)
        need_revealed = int((trig or {}).get('condition_revealed_count', 1) or 1)
        bonus = int((trig or {}).get('bonus', 0) or 0)
        own_n = len(list(getattr(gs, 'success_zone', []) or []))
        got_revealed = int(_count_yell_revealed_live_cards_with_tag(gs, cards_db, '<(スコア+1)>'))
        if got_revealed < need_revealed:
            gs.log.append(f"[AUTO] LIVE: {cn_live}[ライブ成功時]: revealed score+1 LIVE={got_revealed}/{need_revealed} -> no score bonus")
            return
        if own_n >= need_success:
            _add_live_success_score_bonus(gs, cn_live, bonus, detail=f'own success-zone cards={own_n}/{need_success}; revealed score+1 LIVE={got_revealed}/{need_revealed}')
            return
        gs.pending.append({
            'kind': 'confirm_effect',
            'text': f'{cn_live}[ライブ成功時] 自分の成功ライブカード置き場は{own_n}/{need_success}枚、エール公開の<(スコア+1)>を持つライブカードは{got_revealed}/{need_revealed}枚です。相手の成功ライブカード置き場にカードが{need_success}枚以上ある場合、このカードのスコアを+{bonus}します。条件を満たす場合は「使う」、満たさない場合は「スキップ」を選んでください。',
            'options': ['使う', 'スキップ'],
            'source_cn': cn_live,
            'after_live_success_score_bonus': {'cn_live': cn_live, 'bonus': bonus, 'detail': f'opponent success-zone cards >= {need_success}; revealed score+1 LIVE={got_revealed}'},
            'effect_text': _auto_trigger_effect_text(trig or {}),
        })
        gs.log.append(f'[PENDING] LIVE: {cn_live}[ライブ成功時] opponent success-count confirmation own={own_n}/{need_success}, revealed score+1 LIVE={got_revealed}/{need_revealed}')
        return

    if kind in ('add_live_success_score_bonus_if_revealed_card_tag_count_at_least',):
        cn_live = str((trig or {}).get('source_cn', '') or '')
        tag = str((trig or {}).get('condition_tag', '') or '')
        need = int((trig or {}).get('condition_count', 0) or 0)
        bonus = int((trig or {}).get('bonus', 0) or 0)
        got = int(_count_yell_revealed_cards_with_tag(gs, cards_db, tag))
        if got >= need:
            _add_live_success_score_bonus(gs, cn_live, bonus, detail=f"revealed cards with {tag}: {got}")
        else:
            gs.log.append(f"[SKIP] LIVE: {cn_live}[ライブ成功時] unresolved (revealed cards with {tag}: {got} < {need})")
        return
    if kind in ('add_live_success_score_bonus_if_revealed_group_members_have_all_six_colors',):
        cn_live = str((trig or {}).get('source_cn', '') or '')
        group_name = str((trig or {}).get('condition_group_name', '') or '')
        bonus = int((trig or {}).get('bonus', 0) or 0)
        if _revealed_group_members_have_all_six_colors(gs, cards_db, group_name):
            _add_live_success_score_bonus(gs, cn_live, bonus, detail=f"revealed 『{group_name}』 members contain all six colors")
        else:
            gs.log.append(f"[SKIP] LIVE: {cn_live}[ライブ成功時] unresolved (revealed 『{group_name}』 members do not contain all six colors)")
        return
    if kind in ('add_live_success_score_bonus', 'success_score_bonus_all'):
        cn_live = str((trig or {}).get('source_cn', '') or '')
        bonus = int((trig or {}).get('bonus', 0) or 0)
        _add_live_success_score_bonus(gs, cn_live, bonus)
        return
    # legacy success_auto_* kinds are no longer emitted; keep the generic wrappers above as the single live-success path.
    # Unknown trigger
    gs.log.append(f"[WARN] auto_trigger: unknown kind={kind}")
def cmd_set(gs: GameState, rng: random.Random, indices: List[int]) -> None:
    limit = _current_live_set_limit(gs)
    if len(indices) > limit:
        gs.log.append(f"[ERR] set: max {limit} cards this LIVE_SET")
        return
    if any(i < 0 or i >= len(gs.hand) for i in indices):
        gs.log.append("[ERR] set: invalid indices")
        return
    idxs = sorted(set(indices), reverse=True)
    picked = []
    for i in idxs:
        picked.append(gs.hand.pop(i))
    picked.reverse()
    if not isinstance(getattr(gs, 'set_zone', None), list):
        gs.set_zone = []
    gs.set_zone.extend(picked)
    try:
        gs.live_start_resolved_set_idxs = []
        gs.live_start_score_bonus_by_set_idx = {}
        gs.live_start_required_any_reduction_by_set_idx = {}
        gs.live_start_required_any_increase_by_set_idx = {}
    except Exception:
        pass
    drawn = draw(gs, len(picked), rng)
    gs.log.append(f"[SET] set {len(picked)} cards (limit={limit}, total_in_set={len(gs.set_zone)}), drew {drawn}")
def cmd_yell(gs: GameState, rng: random.Random, cards_db: Dict[str, CardInfo]) -> None:
    # ライブ開始時プロンプトが未処理なら先に処理させる（ブレード変化が確定してからYELL）
    if _enqueue_live_start_prompts(gs, cards_db) > 0:
        gs.log.append("[INFO] yell: live-start prompts queued, resolve them first.")
        return
    n = stage_blade(gs, cards_db)
    if n <= 0:
        gs.log.append("[YELL] 0 (no blade on active stage members)")
        return
    revealed = []
    for i in range(n):
        if not gs.deck:
            _rule_refresh_main_deck(gs, rng, reason=f'yell@{i}')
        if not gs.deck:
            break
        revealed.append(gs.deck.pop(0))
    gs.resolve_zone.extend(revealed)
    # Track cheer reveals for this live (e.g., Poppin' Up!)
    try:
        _lst = list(getattr(gs, '_yell_revealed_this_live', []) or [])
    except Exception:
        _lst = []
    _lst.extend(list(revealed))
    try:
        setattr(gs, '_yell_revealed_this_live', _lst)
    except Exception:
        pass
    draw_n = 0
    for cn in revealed:
        c = _get_card(cards_db, cn)
        if c:
            draw_n += _count_draw_icons(c.blade_heart_tags_json)
    got = draw(gs, draw_n, rng) if draw_n > 0 else 0
    gs.log.append(f"[YELL] revealed {len(revealed)} (blade={n}), draw+{draw_n} -> drew {got}")
    _enqueue_yell_revealed_body_auto_triggers(gs, cards_db, revealed)

def _source_cn_or_default(source_cn: str, fallback: str = '') -> str:
    s = str(source_cn or '').strip()
    if s:
        return s
    f = str(fallback or '').strip()
    return f or 'この能力'


def _has_group_member_on_stage(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> bool:
    group_name = str(group_name or '').strip()
    if not group_name:
        return False
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'cardnumber', ''):
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci:
            continue
        if _is_live_ci(ci):
            continue
        if group_name in str(getattr(ci, 'group', '') or ''):
            return True
    return False
def _has_nijigasaki_member_on_stage(gs: GameState, cards_db: Dict[str, CardInfo]) -> bool:
    return _has_group_member_on_stage(gs, cards_db, '虹ヶ咲')
def _put_wait_energy_from_deck(gs: GameState, n: int, reason: str = '') -> int:
    n = int(n or 0)
    if n <= 0:
        return 0
    rem = int(_energy_remaining_in_deck(gs))
    if rem <= 0:
        gs.log.append("[INFO] energy deck empty" + (f" ({reason})" if reason else ""))
        return 0
    add = min(rem, n)
    gs.energy_wait += add
    _clamp_energy_zone(gs)
    gs.log.append(f"[AUTO] energy deck -> WAIT +{add}" + (f" ({reason})" if reason else ""))
    return int(add)
def _last_attempt_excess_color_count(gs: GameState, color_key: str) -> int:
    try:
        pool = dict(getattr(gs, 'last_attempt_excess_hearts', {}) or {})
    except Exception:
        pool = {}
    return int(pool.get(str(color_key or ''), 0) or 0)

def _last_attempt_excess_heart_total(gs: GameState) -> int:
    """Return total excess heart icons after the last LIVE_ATTEMPT allocation.

    This intentionally counts all remaining colored hearts and ALL hearts because
    effects that say just 「余剰ハート」 do not restrict the color.
    """
    try:
        pool = dict(getattr(gs, 'last_attempt_excess_hearts', {}) or {})
    except Exception:
        pool = {}
    total = 0
    for k, v in (pool or {}).items():
        try:
            n = int(v or 0)
        except Exception:
            n = 0
        if n <= 0:
            continue
        key = str(k or '').lower().strip()
        if key in {'pink', 'red', 'yellow', 'green', 'blue', 'purple', 'all', 'any'}:
            total += n
    return int(total)

def _count_stage_group_members(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> int:
    n = 0
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot:
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci:
            continue
        if str(group_name or '') and str(group_name or '') in str(getattr(ci, 'group', '') or ''):
            n += 1
    return n

def _stage_all_members_are_group(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> bool:
    group_name = str(group_name or '').strip()
    if not group_name:
        return False
    any_member = False
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'cardnumber', ''):
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci or not _is_member_ci(ci):
            continue
        any_member = True
        if group_name not in str(getattr(ci, 'group', '') or ''):
            return False
    return any_member

def _stage_all_group_cost_ready(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str, min_cost: int) -> bool:
    total = 0
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot:
            return False
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci:
            return False
        if str(group_name or '') not in str(getattr(ci, 'group', '') or ''):
            return False
        try:
            total += int(getattr(ci, 'cost', 0) or 0)
        except Exception:
            pass
    return int(total) >= int(min_cost or 0)


def _live_zone_group_card_count(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> int:
    total = 0
    g = str(group_name or '').strip()
    if not g:
        return 0
    for cn in list(getattr(gs, 'set_zone', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci or not _is_live_ci(ci):
            continue
        if g in str(getattr(ci, 'group', '') or ''):
            total += 1
    return int(total)

def _live_zone_group_only_required_color_sum(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str, colors: List[str]) -> Tuple[bool, int, int]:
    """Return (condition_ok, required_color_sum, live_count) for live-card storage.

    Used by PL!S-bp6-002 style effects. The live card storage must contain
    at least one LIVE card and every LIVE there must belong to the requested
    group; then we sum required hearts in the requested colors.
    """
    g = str(group_name or '').strip()
    cols = [str(c or '').strip().lower() for c in list(colors or []) if str(c or '').strip().lower() in {'pink','red','yellow','green','blue','purple'}]
    lives = []
    for cn in list(getattr(gs, 'set_zone', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci or not _is_live_ci(ci):
            continue
        lives.append(ci)
    if not lives or not g or not cols:
        return (False, 0, len(lives))
    total = 0
    for ci in lives:
        if g not in str(getattr(ci, 'group', '') or ''):
            return (False, total, len(lives))
        for col in cols:
            total += int(_ci_live_required_heart_count(ci, col) or 0)
    return (True, int(total), len(lives))

def _green_live_group_count(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> int:
    total = 0
    g = str(group_name or '').strip()
    if not g:
        return 0
    for cn in list(getattr(gs, 'green_room', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci or not _is_live_ci(ci):
            continue
        if g in str(getattr(ci, 'group', '') or ''):
            total += 1
    return int(total)

def _success_zone_score_total(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    return int(_success_zone_score_sum(gs, cards_db))


def _parse_live_start_score_if_live_zone_group_count(ci: Optional[CardInfo]) -> Optional[Tuple[str, int, int]]:
    try:
        if not ci or not getattr(ci, 'abilities', None):
            return None
        for ab in _iter_triggered_abilities(ci, 'ライブ開始時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                eff_norm = eff.replace('\n', '')
                m = re.match(r'^自分のライブ中の『(?P<group>[^』]+)』のカードが(?P<count>\d+)枚以上ある場合、このカードのスコアを\+(?P<delta>\d+)する。$', eff_norm)
                if m:
                    return (str(m.group('group') or '').strip(), int(m.group('count') or 0), int(m.group('delta') or 0))
    except Exception:
        return None
    return None

def _parse_live_start_score_if_live_count(ci: Optional[CardInfo]) -> Optional[Tuple[int, int]]:
    try:
        if not ci or not getattr(ci, 'abilities', None):
            return None
        for ab in _iter_triggered_abilities(ci, 'ライブ開始時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                eff_norm = eff.replace('\n', '')
                m = re.match(r'^自分のライブ中のカードが(?P<count>\d+)枚以上ある場合、このカードのスコアを\+(?P<delta>\d+)する。$', eff_norm)
                if m:
                    return (int(m.group('count') or 0), int(m.group('delta') or 0))
    except Exception:
        return None
    return None


def _parse_live_start_score_and_pick_group_member_temp_blade(ci: Optional[CardInfo]) -> Optional[str]:
    try:
        if not ci or not getattr(ci, 'abilities', None):
            return None
        for ab in _iter_triggered_abilities(ci, 'ライブ開始時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                eff_norm = eff.replace('\n', '')
                m = re.match(r'^このゲームの1ターン目のライブフェイズの場合、このカードのスコアを\+1し、ライブ終了時まで、自分のステージにいる『(?P<group>[^』]+)』のメンバー1人は、<\(ブレード\)>を得る。$', eff_norm)
                if m:
                    return str(m.group('group') or '').strip()
    except Exception:
        return None
    return None

def _parse_live_start_optional_pay_energy_for_self_score_if_group(ci: Optional[CardInfo]) -> Optional[str]:
    try:
        if not ci or not getattr(ci, 'abilities', None):
            return None
        for ab in _iter_triggered_abilities(ci, 'ライブ開始時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                cost = str(cl.get('cost_template', '') or '').strip()
                eff = str(cl.get('effect_template', '') or '').strip()
                raw = str(cl.get('raw', '') or '').strip()
                build = raw
                if cost and eff:
                    build = f'{cost}：{eff}'
                elif eff:
                    build = eff
                if not build:
                    continue
                eff_norm = build.replace('\n', '')
                m = re.match(r'^<\(E\)><\(E\)>支払ってもよい：自分のステージに『(?P<group>[^』]+)』のメンバーがいる場合、このカードのスコアを\+1する。$', eff_norm)
                if m:
                    return str(m.group('group') or '').strip()
    except Exception:
        return None
    return None

def _parse_live_start_top_keep_one_then_reveal_top_score_if_live_by_group_count(ci: Optional[CardInfo]) -> Optional[str]:
    try:
        if not ci or not getattr(ci, 'abilities', None):
            return None
        for ab in _iter_triggered_abilities(ci, 'ライブ開始時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                eff_norm = eff.replace('\n', '')
                m = re.match(r'^自分のステージにいる『(?P<group>[^』]+)』のメンバー1人につき、自分のデッキの上からカードを1枚見る。その中から1枚をデッキの上に置き、残りを控え室に置く。自分のデッキの一番上のカードを1枚公開する。これによりライブカードを公開したとき、このカードのスコアを\+1する。$', eff_norm)
                if m:
                    return str(m.group('group') or '').strip()
    except Exception:
        return None
    return None

def _parse_live_start_score_if_green_live_group_count(ci: Optional[CardInfo]) -> Optional[Tuple[str, int, int]]:
    try:
        if not ci or not getattr(ci, 'abilities', None):
            return None
        for ab in _iter_triggered_abilities(ci, 'ライブ開始時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                eff_norm = eff.replace('\n', '')
                m = re.match(r'^(?:自分の)?控え室に『(?P<group>[^』]+)』のライブカードが(?P<count>\d+)枚以上ある(?:場合|なら)、このカードのスコアを\+(?P<delta>\d+)する。$', eff_norm)
                if m:
                    return (str(m.group('group') or '').strip(), int(m.group('count') or 0), int(m.group('delta') or 0))
    except Exception:
        return None
    return None


def _parse_live_start_score_per_stage_group_member_heart_color_kind(ci: Optional[CardInfo]) -> Optional[Tuple[str, int]]:
    try:
        if not ci or not getattr(ci, 'abilities', None):
            return None
        for ab in _iter_triggered_abilities(ci, 'ライブ開始時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                eff_norm = eff.replace('\n', '')
                m = re.match(r'^自分のステージにいる『(?P<group>[^』]+)』のメンバーが持つ(?:<\([^)]*\)>)+のうち1色につき、このカードのスコアを[＋+](?P<delta>\d+)する。$', eff_norm)
                if m:
                    return (str(m.group('group') or '').strip(), int(m.group('delta') or 0))
    except Exception:
        return None
    return None


def _parse_live_start_score_if_success_zone_has_scores(ci: Optional[CardInfo]) -> Optional[Tuple[int, int, int, int]]:
    try:
        if not ci or not getattr(ci, 'abilities', None):
            return None
        for ab in _iter_triggered_abilities(ci, 'ライブ開始時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                eff_norm = eff.replace('\n', '')
                m = re.match(r'^自分の成功ライブカード置き場にスコアが(?P<a>\d+)か(?P<b>\d+)のカードがある場合、このカードのスコアを\+(?P<one>\d+)する。それらが両方ある場合、代わりにスコアを\+(?P<both>\d+)する。$', eff_norm)
                if m:
                    return (int(m.group('a') or 0), int(m.group('b') or 0), int(m.group('one') or 0), int(m.group('both') or 0))
    except Exception:
        return None
    return None


def _parse_live_start_score_if_green_unique_live_names_group_count(ci: Optional[CardInfo]) -> Optional[Tuple[str, int, int, int, int]]:
    try:
        if not ci or not getattr(ci, 'abilities', None):
            return None
        for ab in _iter_triggered_abilities(ci, 'ライブ開始時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                eff_norm = eff.replace('\n', '')
                m = re.match(r'^自分の控え室にカード名の異なる『(?P<group>[^』]+)』のライブカードが(?P<c1>\d+)枚以上ある場合、このカードのスコアを\+(?P<d1>\d+)する。(?P<c2>\d+)枚以上ある場合、代わりにスコアを\+(?P<d2>\d+)する。$', eff_norm)
                if m:
                    return (str(m.group('group') or '').strip(), int(m.group('c1') or 0), int(m.group('d1') or 0), int(m.group('c2') or 0), int(m.group('d2') or 0))
    except Exception:
        return None
    return None

def _parse_live_start_reduce_any_and_score_if_success_score(ci: Optional[CardInfo]) -> Optional[Tuple[int, int, int, int]]:
    try:
        if not ci or not getattr(ci, 'abilities', None):
            return None
        for ab in _iter_triggered_abilities(ci, 'ライブ開始時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                eff_norm = eff.replace('\n', '')
                m = re.match(r'^自分の成功ライブカード置き場にあるカードのスコアの合計が(?P<reduce_th>\d+)以上の場合、このライブを成功させるための必要ハートを<\(任意\)>減らす。スコアの合計が(?P<score_th>\d+)以上の場合、さらにこのカードのスコアを\+(?P<delta>\d+)する。$', eff_norm)
                if m:
                    return (int(m.group('reduce_th') or 0), 1, int(m.group('score_th') or 0), int(m.group('delta') or 0))
    except Exception:
        return None
    return None


def _parse_live_start_score_and_increase_any_per_success_zone_cardname_count(ci: Optional[CardInfo]) -> Optional[Tuple[str, int, int]]:
    try:
        if not ci or not getattr(ci, 'abilities', None):
            return None
        for ab in _iter_triggered_abilities(ci, 'ライブ開始時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                eff_norm = eff.replace('\n', '')
                m = re.search(r'自分の成功ライブカード置き場にあるカード名が「(?P<name>[^」]+)」のカード1枚につき、このカードのスコアを\+(?P<score>\d+)、成功させるための必要ハートを(?P<anys>(?:<\(任意\)>)+)増やす。', eff_norm)
                if not m:
                    continue
                cardname = str(m.group('name') or '').strip()
                per_score = int(m.group('score') or 0)
                per_any = len(re.findall(r'<\(任意\)>', str(m.group('anys') or '')))
                if cardname and (per_score > 0 or per_any > 0):
                    return (cardname, per_score, per_any)
    except Exception:
        return None
    return None


def _build_live_start_trigger_from_effect(gs: GameState, cards_db: Dict[str, CardInfo], eff: str, source_cn: str, label: str, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    eff_raw = str(eff or '').strip()
    eff_norm = _normalize_icon_token_text(eff_raw).replace('\n', '')
    # Generalized from Rise Up High!
    m = re.match(r'^このゲームの1ターン目のライブフェイズの場合、このカードのスコアを\+1し、ライブ終了時まで、自分のステージにいる『(?P<group>[^』]+)』のメンバー1人は、<\(ブレード\)>を得る。$', eff_norm)
    if m:
        group_name = str(m.group('group') or '').strip()
        return {
            'kind': 'live_start_score_and_pick_group_member_temp_blade',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'condition_group_name': group_name,
        }
    # Generalized from Butterfly.
    m = re.match(r'^<\(E\)><\(E\)>支払ってもよい：自分のステージに『(?P<group>[^』]+)』のメンバーがいる場合、このカードのスコアを\+1する。$', eff_norm)
    if m:
        group_name = str(m.group('group') or '').strip()
        return {
            'kind': 'live_start_optional_pay_energy_for_self_score_if_group',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'condition_group_name': group_name,
        }
    # Generalized from NEO SKY, NEO MAP!
    m = re.match(r'^自分のステージのエリアすべてに『(?P<group>[^』]+)』のメンバーがいて、かつそれらのコスト合計が(?P<cost>\d+)以上の場合、(?P<inner>.+)$', eff_norm)
    if m:
        group_name = str(m.group('group') or '').strip()
        inner = str(m.group('inner') or '').strip()
        try:
            min_cost = int(m.group('cost') or 0)
        except Exception:
            min_cost = 0
        return {
            'kind': 'live_start_if_stage_group_cost_then_draw_then_ordered_topdeck',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'condition_group_name': group_name,
            'condition_min_cost': min_cost,
            'effect': inner,
        }
    # Generalized from ツナガルコネクト.
    m = re.match(r'^自分のステージにいる『(?P<group>[^』]+)』のメンバー1人につき、自分のデッキの上からカードを1枚見る。その中から1枚をデッキの上に置き、残りを控え室に置く。自分のデッキの一番上のカードを1枚公開する。これによりライブカードを公開したとき、このカードのスコアを\+1する。$', eff_norm)
    if m:
        group_name = str(m.group('group') or '').strip()
        return {
            'kind': 'live_start_top_keep_one_then_reveal_top_score_if_live_by_group_count',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'condition_group_name': group_name,
        }

    # Generalized from VIVID WORLD.
    m = re.match(r'^ライブ終了時まで、エールによって公開される自分のカードが持つ<\(桃\)>、<\(赤\)>、<\(黄\)>、<\(緑\)>、<\(紫\)>、<\(ALL\)>は、すべて<\((?P<target>[^)]+)\)>になる。$', eff_norm)
    if m:
        target_color_jp = str(m.group('target') or '').strip()
        return {
            'kind': 'live_start_convert_revealed_colors_to_single_color_until_end_of_live',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'target_color_jp': target_color_jp,
        }
    # Generalized from 僕らのLIVE 君とのLIFE / Eutopia.
    m = re.match(r'^自分のライブ中の『(?P<group>[^』]+)』のカードが(?P<count>\d+)枚以上ある場合、このカードのスコアを\+(?P<delta>\d+)する。$', eff_norm)
    if m:
        return {
            'kind': 'live_start_score_if_live_zone_group_count_at_least',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'condition_group_name': str(m.group('group') or '').strip(),
            'condition_count': int(m.group('count') or 0),
            'score_delta': int(m.group('delta') or 0),
        }
    # Generalized from 青とシャボン.
    m = re.match(r'^(?:自分の)?控え室に『(?P<group>[^』]+)』のライブカードが(?P<count>\d+)枚以上ある(?:場合|なら)、このカードのスコアを\+(?P<delta>\d+)する。$', eff_norm)
    if m:
        return {
            'kind': 'live_start_score_if_green_live_group_count_at_least',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'condition_group_name': str(m.group('group') or '').strip(),
            'condition_count': int(m.group('count') or 0),
            'score_delta': int(m.group('delta') or 0),
        }

    # Generalized from Solitude Rain.
    m = re.match(r'^自分のステージにいる『(?P<group>[^』]+)』のメンバーが持つ(?:<\([^)]*\)>)+のうち1色につき、このカードのスコアを[＋+](?P<delta>\d+)する。$', eff_norm)
    if m:
        return {
            'kind': 'live_start_score_per_stage_group_member_heart_color_kind',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'condition_group_name': str(m.group('group') or '').strip(),
            'score_delta_per_kind': int(m.group('delta') or 0),
        }
    # Generalized from サイコーハート.
    m = re.match(r'^自分の成功ライブカード置き場にスコアが(?P<a>\d+)か(?P<b>\d+)のカードがある場合、このカードのスコアを\+(?P<one>\d+)する。それらが両方ある場合、代わりにスコアを\+(?P<both>\d+)する。$', eff_norm)
    if m:
        return {
            'kind': 'live_start_score_if_success_zone_has_scores',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'score_a': int(m.group('a') or 0),
            'score_b': int(m.group('b') or 0),
            'score_delta_one': int(m.group('one') or 0),
            'score_delta_both': int(m.group('both') or 0),
        }
    # Generalized from stars we chase.
    m = re.match(r'^自分の控え室にカード名の異なる『(?P<group>[^』]+)』のライブカードが(?P<c1>\d+)枚以上ある場合、このカードのスコアを\+(?P<d1>\d+)する。(?P<c2>\d+)枚以上ある場合、代わりにスコアを\+(?P<d2>\d+)する。$', eff_norm)
    if m:
        return {
            'kind': 'live_start_score_if_green_unique_live_names_group_count',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'condition_group_name': str(m.group('group') or '').strip(),
            'condition_count_one': int(m.group('c1') or 0),
            'score_delta_one': int(m.group('d1') or 0),
            'condition_count_two': int(m.group('c2') or 0),
            'score_delta_two': int(m.group('d2') or 0),
        }
    # Generalized from ？←HEARTBEAT.
    m = re.match(r'^自分の成功ライブカード置き場にあるカードのスコアの合計が(?P<reduce_th>\d+)以上の場合、このライブを成功させるための必要ハートを<\(任意\)>減らす。スコアの合計が(?P<score_th>\d+)以上の場合、さらにこのカードのスコアを\+(?P<delta>\d+)する。$', eff_norm)
    if m:
        return {
            'kind': 'live_start_reduce_any_and_score_if_success_score_at_least',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'reduce_threshold': int(m.group('reduce_th') or 0),
            'reduce_any': 1,
            'score_threshold': int(m.group('score_th') or 0),
            'score_delta': int(m.group('delta') or 0),
        }
    # Generalized from EMOTION.
    m = re.match(r'^自分の成功ライブカード置き場にあるカード名が「(?P<name>[^」]+)」のカード1枚につき、このカードのスコアを\+(?P<score>\d+)、成功させるための必要ハートを(?P<anys>(?:<\(任意\)>)+)増やす。$', eff_norm)
    if m:
        return {
            'kind': 'live_start_score_and_increase_any_per_success_zone_cardname_count',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'condition_cardname': str(m.group('name') or '').strip(),
            'score_delta_per': int(m.group('score') or 0),
            'required_any_increase_per': len(re.findall(r'<\(任意\)>', str(m.group('anys') or ''))),
        }
    # Generalized success-zone count based score bonuses.
    m = re.match(r'^自分か相手の成功ライブカード置き場にカードが(?P<count>\d+)枚以上あり、かつ自分のステージに名前の異なるメンバーが(?P<names>\d+)人以上いる場合、このカードのスコアを\+(?P<delta>\d+)する。$', eff_norm)
    if m:
        return {
            'kind': 'live_start_score_if_either_success_count_and_distinct_stage_names_at_least',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'condition_success_count': int(m.group('count') or 0),
            'condition_distinct_names': int(m.group('names') or 0),
            'score_delta': int(m.group('delta') or 0),
        }

    m = re.match(r'^自分の成功ライブカード置き場のカード枚数が相手より少ない場合、このカードのスコアを\+(?P<delta>\d+)する。$', eff_norm)
    if m:
        return {
            'kind': 'live_start_score_if_own_success_count_less_than_opponent_manual',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'score_delta': int(m.group('delta') or 0),
        }

    # Opponent wait-state reference families. Opponent stage is not modeled, so these resolve by manual Apply/Skip or count selection.
    m = re.match(r'^相手のステージにウェイト状態のメンバーがいる場合、このカードを成功させるための必要ハートを(?P<anys>(?:<\(任意\)>)+)減らす。$', eff_norm)
    if m:
        _reduce_any_n = len(re.findall(r'<\(任意\)>', str(m.group('anys') or '')))
        return {
            'kind': 'live_start_reduce_any_if_opponent_wait_exists_manual',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'option_label': f'{source_cn}：必要ハート軽減' if str(source_cn or '') else '必要ハート軽減',
            'effect_text': eff_norm,
            'reduce_any': _reduce_any_n,
        }

    m = re.match(r'^相手のステージにいるウェイト状態のメンバーの数まで、自分の控え室にある『(?P<group>[^』]+)』のメンバーカードを選ぶ。それらを好きな順番でデッキの上に置く。$', eff_norm)
    if m:
        _g_wait_top = str(m.group('group') or '').strip()
        return {
            'kind': 'live_start_topdeck_green_group_members_upto_opponent_wait_count_manual',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'option_label': f'{source_cn}：相手ウェイト数ぶんデッキ上' if str(source_cn or '') else '相手ウェイト数ぶんデッキ上',
            'effect_text': eff_norm,
            'condition_group_name': _g_wait_top,
        }

    # Stage group-name and heart-color condition families.
    m = re.match(r'^自分のステージにグループ名がそれぞれ異なるメンバーが(?P<count>\d+)人以上いる場合、ライブ終了時まで、自分のセンターエリアにいるメンバーは(?P<icons>(?:<\(ALL\)>)+)を得る。$', eff_norm)
    if m:
        return {
            'kind': 'live_start_center_member_gain_all_if_distinct_stage_groups_at_least',
            'source_cn': str(source_cn or ''),
            'set_idx': ctx.get('set_idx', None),
            'label': str(label or ''),
            'condition_distinct_groups': int(m.group('count') or 0),
            'all_n': len(re.findall(r'<\(ALL\)>', str(m.group('icons') or ''))),
        }

    m = re.match(r'^自分のステージにいるメンバーが持つハートの中に(?P<icons>(?:<\([^)]+\)>[、,]?)+)がすべてある場合、(?P<inner>.+)$', eff_norm)
    if m:
        colors = _heart_icons_to_colors(str(m.group('icons') or ''))
        inner = str(m.group('inner') or '').strip()
        m_score = re.match(r'^このカードのスコアを\+(?P<delta>\d+)する。$', inner)
        if m_score:
            return {
                'kind': 'live_start_score_if_stage_has_heart_colors',
                'source_cn': str(source_cn or ''),
                'set_idx': ctx.get('set_idx', None),
                'label': str(label or ''),
                'condition_colors': list(colors),
                'score_delta': int(m_score.group('delta') or 0),
            }
        m_blade = re.match(r'^ライブ終了時まで、(?P<blades>(?:<\(ブレード\)>)+)を得る。$', inner)
        if m_blade:
            return {
                'kind': 'live_start_member_gain_blade_if_stage_has_heart_colors',
                'source_cn': str(source_cn or ''),
                'pos': str(ctx.get('pos', '') or '').upper(),
                'label': str(label or ''),
                'condition_colors': list(colors),
                'blade_n': len(re.findall(r'<\(ブレード\)>', str(m_blade.group('blades') or ''))),
            }

    return None

def _live_success_excess_color_and_stage_group_met(gs: GameState, cards_db: Dict[str, CardInfo], color_jp: str, group_name: str) -> bool:
    # IMPORTANT: only real colored excess counts here. ALL does not satisfy this condition.
    color_key = _HEART_ICON_COLOR_MAP.get(str(color_jp or '').strip())
    if not color_key:
        return False
    if int(_last_attempt_excess_color_count(gs, color_key)) <= 0:
        return False
    return bool(_has_group_member_on_stage(gs, cards_db, group_name))
def _build_live_success_trigger_from_effect(gs: GameState, cards_db: Dict[str, CardInfo], eff: str, source_cn: str, label: str, ctx: Dict[str, Any], pos: str = '') -> Optional[Dict[str, Any]]:
    eff_raw = str(eff or '').strip()
    eff_norm = _normalize_icon_token_text(eff_raw).replace('\n', '')
    # Generalized live-success conditional wrapper: either player's success zone has at least N cards.
    # We can verify our own success zone directly. Opponent state is not modeled in the current
    # single-player simulator, so if our own side does not satisfy the condition we expose Apply/Skip.
    m = re.match(r'^自分か相手の成功ライブカード置き場にカードが(?P<n>\d+)枚以上ある場合、(?P<inner>.+)$', eff_norm)
    if m:
        threshold = int(m.group('n') or 0)
        inner = str(m.group('inner') or '').strip()
        if _match_effect_template(inner):
            own_n = len(list(getattr(gs, 'success_zone', []) or []))
            if own_n >= threshold:
                return {
                    'kind': 'apply_effect_template_on_live_success',
                    'effect': inner,
                    'source_cn': str(source_cn or ''),
                    'pos': str(pos or ''),
                    'ctx': dict(ctx or {}),
                    'label': f'{label} 自分の成功ライブカード置き場={own_n}枚で条件成立',
                }
            return {
                'kind': 'enqueue_success_prompt',
                'prompt': {
                    'kind': 'confirm_effect',
                    'text': f'{label} 条件付き効果：自分の成功ライブカード置き場は{own_n}枚です。相手の成功ライブカード置き場にカードが{threshold}枚以上ある場合のみ解決します。条件を満たすなら Apply、満たさないなら Skip。',
                    'options': ['apply', 'skip'],
                    'after_effect_template': inner,
                    'ctx': dict(ctx or {}),
                    'source_cn': str(source_cn or ''),
                },
                'source_cn': str(source_cn or ''),
                'label': str(label or ''),
            }

    # Generalized live-success conditional wrapper: opponent-score-higher -> confirm/skip, then existing template.
    # In this single-player simulator, conditions that compare with the opponent
    # cannot be auto-verified, so we normalize them into an explicit apply/skip prompt.
    m = re.match(r'^ライブの合計スコアが相手より高い場合、(?P<inner>.+)$', eff_norm)
    if m:
        inner = str(m.group('inner') or '').strip()
        if _match_effect_template(inner):
            return {
                'kind': 'enqueue_success_prompt',
                'prompt': {
                    'kind': 'confirm_effect',
                    'text': f'{label} 条件付き効果：ライブの合計スコアが相手より高い場合のみ解決します。条件を満たすなら Apply、満たさないなら Skip。',
                    'options': ['apply', 'skip'],
                    'after_effect_template': inner,
                    'ctx': dict(ctx or {}),
                    'source_cn': str(source_cn or ''),
                },
                'source_cn': str(source_cn or ''),
                'label': str(label or ''),
            }
    # Generalized live-success conditional wrapper: same live total score -> confirm/skip, then existing template.
    # The simulator does not model opponent live total, so this is resolved manually at effect resolution.
    m = re.match(r'^自分と相手のライブの合計スコアが同じ場合、(?P<inner>.+)$', eff_norm)
    if m:
        inner = str(m.group('inner') or '').strip()
        if _match_effect_template(inner):
            return {
                'kind': 'enqueue_success_prompt',
                'prompt': {
                    'kind': 'confirm_effect',
                    'text': f'{label} 条件付き効果：自分と相手のライブの合計スコアが同じ場合のみ解決します。条件を満たすなら Apply、満たさないなら Skip。',
                    'options': ['apply', 'skip'],
                    'after_effect_template': inner,
                    'ctx': dict(ctx or {}),
                    'source_cn': str(source_cn or ''),
                },
                'source_cn': str(source_cn or ''),
                'label': str(label or ''),
            }

    # Generalized live-success conditional wrapper: named stage members -> resolve-time condition check.
    # Example: Bubble Rise checks distinct named Liella! members, then retrieves from yell.
    m = re.match(r'^自分のステージに(?P<names>(?:「[^」]+」(?:、)?)+)のうち、名前の異なるメンバーが(?P<count>\d+)枚以上いる場合、(?P<inner>.+)$', eff_norm)
    if m:
        names = [str(x or '').strip() for x in re.findall(r'「([^」]+)」', str(m.group('names') or '')) if str(x or '').strip()]
        need = int(m.group('count') or 0)
        inner = str(m.group('inner') or '').strip()
        if names and need > 0 and _match_effect_template(inner):
            return {
                'kind': 'apply_effect_template_if_stage_named_members_at_least_on_live_success',
                'effect': inner,
                'condition_names': list(names),
                'condition_count': int(need),
                'source_cn': str(source_cn or ''),
                'pos': str(pos or ''),
                'ctx': dict(ctx or {}),
                'label': str(label or ''),
            }

    # Generalized live-success trigger for cards revealed by own yell.
    # Example: PL!S-bp3-002 can put itself into hand if live total score is higher.
    m = re.match(r'^ライブの合計スコアが相手より高い場合、このカードを手札に加えてもよい。この能力は、このカードが自分のエールによって公開されている場合のみ発動する。?$', eff_norm)
    if m:
        return {
            'kind': 'enqueue_success_prompt',
            'prompt': {
                'kind': 'confirm_revealed_self_to_hand',
                'text': f'{label} 条件付き効果：このカードが自分のエールで公開されています。ライブの合計スコアが相手より高い場合、このカードを手札に加えてもよいです。条件を満たし手札に加えるなら Apply、加えない/条件未達なら Skip。',
                'options': ['apply', 'skip'],
                'source_cn': str(source_cn or ''),
            },
            'source_cn': str(source_cn or ''),
            'label': str(label or ''),
        }

    # Generalized live-success conditional wrapper: excess color + stage group -> resolve-time condition check.
    # Important: do not decide trigger occurrence here from the current board.
    # Simultaneous live-success effects may change the state before this resolves.
    m = re.match(r'^このターン、自分が余剰ハートに<\((?P<color>[^)]+)\)>を1つ以上持っており、かつ自分のステージに『(?P<group>[^』]+)』のメンバーがいる場合、(?P<inner>.+)$', eff_norm)
    if m:
        inner = str(m.group('inner') or '').strip()
        color_jp = str(m.group('color') or '').strip()
        group_name = str(m.group('group') or '').strip()
        if _match_effect_template(inner):
            return {
                'kind': 'apply_effect_template_if_excess_color_and_stage_group_on_live_success',
                'effect': inner,
                'condition_color_jp': color_jp,
                'condition_group_name': group_name,
                'source_cn': str(source_cn or ''),
                'pos': str(pos or ''),
                'ctx': dict(ctx or {}),
                'label': str(label or ''),
            }
    # Generalized live-success conditional wrapper: compare number of cards revealed by yell.
    # This single-player simulator does not model the opponent's yell reveal pile, so the
    # opponent-side condition is resolved by an explicit Apply/Skip prompt after the
    # trigger has been queued at the normal live-success check timing.
    m = re.match(r'^エールにより公開された自分のカードの枚数が、相手がエールによって公開したカードの枚数より少ない場合、(?P<inner>.+)$', eff_norm)
    if m:
        inner = str(m.group('inner') or '').strip()
        if _match_effect_template(inner):
            try:
                self_revealed_n = len(list(getattr(gs, '_yell_revealed_this_live', []) or []))
            except Exception:
                self_revealed_n = 0
            return {
                'kind': 'enqueue_success_prompt',
                'prompt': {
                    'kind': 'confirm_effect',
                    'text': f'{label} 条件付き効果：自分のエール公開枚数は{self_revealed_n}枚です。相手がエールによって公開したカードの枚数より少ない場合のみ解決します。条件を満たすなら Apply、満たさないなら Skip。',
                    'options': ['apply', 'skip'],
                    'after_effect_template': inner,
                    'ctx': dict(ctx or {}),
                    'source_cn': str(source_cn or ''),
                },
                'source_cn': str(source_cn or ''),
                'label': str(label or ''),
            }

    # Generalized live-success conditional wrapper: distinct named group members revealed by yell.
    # Examples:
    # - PL!SP-bp4-006: if 3 distinct 『Liella!』 members were revealed, retrieve a 『Liella!』 LIVE from yell.
    # - PL!SP-bp4-026: if 5 distinct 『Liella!』 members were revealed, this LIVE gets score +1.
    m = re.match(r'^エールにより公開された自分のカードの中に、?名前が異なる『(?P<group>[^』]+)』のメンバーカードが(?P<count>\d+)枚以上ある場合、(?P<inner>.+)$', eff_norm)
    if m:
        group_name = str(m.group('group') or '').strip()
        need = int(m.group('count') or 0)
        inner = str(m.group('inner') or '').strip()
        m_score = re.match(r'^このカードのスコアを\+(?P<delta>\d+)する。?$', inner)
        if m_score:
            return {
                'kind': 'add_live_success_score_bonus_if_revealed_distinct_named_group_member_count_at_least',
                'condition_group_name': group_name,
                'condition_count': int(need),
                'bonus': int(m_score.group('delta') or 0),
                'source_cn': str(source_cn or ''),
                'pos': str(pos or ''),
                'ctx': dict(ctx or {}),
                'label': str(label or ''),
            }
        if _match_effect_template(inner):
            return {
                'kind': 'apply_effect_template_if_revealed_distinct_named_group_member_count_at_least_on_live_success',
                'effect': inner,
                'condition_group_name': group_name,
                'condition_count': int(need),
                'source_cn': str(source_cn or ''),
                'pos': str(pos or ''),
                'ctx': dict(ctx or {}),
                'label': str(label or ''),
            }

    # Revealed <スコア+1> group LIVE -> live total score bonus.
    # Example: PL!S-bp6-009 黒澤ルビィ.
    m = re.match(r'^エール(?:により|で)公開された自分のカードの中に、?<\(スコア\+1\)>を持つ『(?P<group>[^』]+)』のライブカードが(?P<count>\d+)?枚?(?:以上)?ある場合、ライブの合計スコアを\+(?P<delta>\d+)する。?$', eff_norm)
    if m:
        return {
            'kind': 'add_live_success_total_score_bonus_if_revealed_group_live_score_tag_at_least',
            'condition_group_name': str(m.group('group') or '').strip(),
            'condition_count': int(m.group('count') or 1),
            'bonus': int(m.group('delta') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }

    # Revealed <スコア+1> LIVE or manually confirmed above-original score in live storage -> draw.
    # Example: PL!SP-pb2-004 平安名すみれ.
    m = re.match(r'^自分のライブカード置き場の中に元々のスコアより高いスコアのライブカードがあるか、エールにより公開された自分のカードの中に<\(スコア\+1\)>を持つライブカードがある場合、カードを1枚引く。?$', eff_norm)
    if m:
        return {
            'kind': 'draw_if_revealed_score_tag_live_or_success_score_above_original',
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }

    # Generalized success-zone count + revealed score-tag LIVE condition.
    m = re.match(r'^自分か相手の成功ライブカード置き場にカードが(?P<count>\d+)枚以上あり、かつエール(?:によって|により)公開された自分のカードの中に<\(スコア\+1\)>を持つライブカードが(?P<reveal_n>\d+)枚以上ある場合、このカードのスコアを\+(?P<delta>\d+)する。?$', eff_norm)
    if m:
        return {
            'kind': 'add_live_success_score_bonus_if_either_success_count_and_revealed_score_tag_live_at_least',
            'condition_success_count': int(m.group('count') or 0),
            'condition_revealed_count': int(m.group('reveal_n') or 0),
            'bonus': int(m.group('delta') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }


    # Revealed LIVE count OR stage heart color kinds OR this-turn position change -> this LIVE score bonus.
    # Example: LL-bp5-001 Live with a smile!
    m = re.match(r'^エールにより公開された自分のカードの中にライブカードが(?P<live_n>\d+)枚以上あるか、自分のステージにいるメンバーが持つハートの中に<\(桃\)>、<\(赤\)>、<\(黄\)>、<\(緑\)>、<\(青\)>、<\(紫\)>のうち合計(?P<kind_n>\d+)種類以上あるか、このターンに自分のステージにいるメンバーがエリアを移動している場合、このカードのスコアを\+(?P<delta>\d+)する。?$', eff_norm)
    if m:
        return {
            'kind': 'add_live_success_score_bonus_if_revealed_live_or_stage_heart_kinds_or_moved',
            'condition_revealed_live_count': int(m.group('live_n') or 0),
            'condition_stage_heart_kind_count': int(m.group('kind_n') or 0),
            'bonus': int(m.group('delta') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }

    # No-blade-heart group MEMBER revealed -> apply an existing effect template.
    # Example: PL!-bp6-001 高坂穂乃果.
    m = re.match(r'^エールにより公開された自分のカードの中に、?ブレードハートを持たない『(?P<group>[^』]+)』のメンバーカードがある場合、(?P<inner>.+)$', eff_norm)
    if m:
        inner = str(m.group('inner') or '').strip()
        if _match_effect_template(inner):
            return {
                'kind': 'apply_effect_template_if_revealed_no_bladeheart_group_member_at_least_on_live_success',
                'effect': inner,
                'condition_group_name': str(m.group('group') or '').strip(),
                'condition_count': 1,
                'source_cn': str(source_cn or ''),
                'pos': str(pos or ''),
                'ctx': dict(ctx or {}),
                'label': str(label or ''),
            }

    # Reveal deck top, add it to hand, and if it is a no-blade-heart member, add to live total score.
    # Example: PL!-bp6-007 東條希.
    m = re.match(r'^自分のデッキの一番上のカードを公開し、手札に加える。それがブレードハートを持たないメンバーカードの場合、ライブの合計スコアを\+(?P<delta>\d+)する。?$', eff_norm)
    if m:
        return {
            'kind': 'reveal_top_to_hand_then_live_total_score_if_no_bladeheart_member',
            'bonus': int(m.group('delta') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }

    # Generalized from MIRACLE WAVE.
    # 「スコアはNになる」 is not a +bonus; it is stored as a direct score-set value.
    m = re.match(r'^このターン、エールにより公開された自分のカードの中にブレードハートを持たないカードが0枚の場合か、または自分の余剰ハートを(?P<excess>\d+)つ以上持っている場合、このカードのスコアは(?P<score>\d+)になる。?$', eff_norm)
    if m:
        return {
            'kind': 'set_live_success_score_if_no_revealed_no_bladeheart_or_excess_at_least',
            'condition_excess_count': int(m.group('excess') or 0),
            'target_score': int(m.group('score') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }

    m = re.match(r'^自分が余剰ハートを持たない場合、ライブの合計スコアを\+(?P<zero_bonus>\d+)する。自分が余剰ハートを(?P<high>\d+)つ以上持つ場合、ライブの合計スコアを(?P<delta>-\d+)する。この効果ではライブの合計スコアは0未満にならない。?$', eff_norm)
    if m:
        return {
            'kind': 'adjust_live_total_score_by_excess_heart_count',
            'zero_excess_bonus': int(m.group('zero_bonus') or 0),
            'high_excess_threshold': int(m.group('high') or 0),
            'high_excess_delta': int(m.group('delta') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }

    m = re.match(r'^ライブ終了時まで、相手は余剰ハートをすべて失う。これにより相手が余剰ハートを(?P<lost>\d+)つ以上失っている場合、このカードのスコアを\+(?P<delta>\d+)する。?$', eff_norm)
    if m:
        return {
            'kind': 'opponent_loses_excess_hearts_then_live_score_bonus_manual',
            'lost_threshold': int(m.group('lost') or 0),
            'bonus': int(m.group('delta') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }

    # Generalized live-success excess-heart conditions.
    m = re.match(r'^このターン、自分が余剰ハートを持たない場合、このカードのスコアを\+(?P<delta>\d+)する。?$', eff_norm)
    if m:
        return {
            'kind': 'add_live_success_score_bonus_if_excess_total_zero',
            'bonus': int(m.group('delta') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }

    m = re.match(r'^このターン、自分が余剰ハートを(?P<count>\d+)つ以上持っている場合、(?P<inner>.+)$', eff_norm)
    if m:
        inner = str(m.group('inner') or '').strip()
        if _match_effect_template(inner):
            return {
                'kind': 'apply_effect_template_if_excess_total_at_least_on_live_success',
                'effect': inner,
                'condition_excess_count': int(m.group('count') or 0),
                'source_cn': str(source_cn or ''),
                'pos': str(pos or ''),
                'ctx': dict(ctx or {}),
                'label': str(label or ''),
            }

    m = re.match(r'^自分が余剰ハートを(?P<count>\d+)つ以上持っている場合、(?P<inner>.+)$', eff_norm)
    if m:
        inner = str(m.group('inner') or '').strip()
        if _match_effect_template(inner):
            return {
                'kind': 'apply_effect_template_if_excess_total_at_least_on_live_success',
                'effect': inner,
                'condition_excess_count': int(m.group('count') or 0),
                'source_cn': str(source_cn or ''),
                'pos': str(pos or ''),
                'ctx': dict(ctx or {}),
                'label': str(label or ''),
            }

    m = re.match(r'^自分が余剰ハートに<\((?P<color>[^)]+)\)>を(?P<count>\d+)つ以上持つ場合、(?P<inner>.+)$', eff_norm)
    if m:
        inner = str(m.group('inner') or '').strip()
        color_jp = str(m.group('color') or '').strip()
        color_key = _HEART_JP_MAP.get(color_jp, '')
        if color_key and _match_effect_template(inner):
            return {
                'kind': 'apply_effect_template_if_excess_color_at_least_on_live_success',
                'effect': inner,
                'condition_color_jp': color_jp,
                'condition_color_key': color_key,
                'condition_count': int(m.group('count') or 0),
                'source_cn': str(source_cn or ''),
                'pos': str(pos or ''),
                'ctx': dict(ctx or {}),
                'label': str(label or ''),
            }

    m = re.match(r'^自分が余剰ハートを(?P<count>\d+)つ(?P<ge>以上)?持っている場合、それらをすべて失い、このカードのスコアを\+(?P<delta>\d+)する。?$', eff_norm)
    if m:
        # PL!S-bp5-020 Landing action Yeah!! was scraped from a wiki typo as「3つ」.
        # Official/manual correction is「3つ以上」, so force the card to the at-least semantics
        # even if an old uncorrected DB is accidentally loaded.
        force_at_least = str(source_cn or '') == 'PL!S-bp5-020'
        is_at_least = bool(m.group('ge')) or force_at_least
        return {
            'kind': 'add_live_success_score_bonus_and_clear_if_excess_total_at_least' if is_at_least else 'add_live_success_score_bonus_and_clear_if_excess_total_exact',
            'condition_mode': 'at_least' if is_at_least else 'exact',
            'condition_excess_count': int(m.group('count') or 0),
            'bonus': int(m.group('delta') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }

    # Generalized from VIVID WORLD.
    # DB text may or may not include Japanese comma separators between the six icons.
    eff_compact = eff_norm.replace('、', '').replace('，', '').replace(' ', '')
    m = re.match(r'^エールにより公開された自分の『(?P<group>[^』]+)』のメンバーが持つハートの中に<\(桃\)><\(赤\)><\(黄\)><\(緑\)><\(青\)><\(紫\)>がある場合このカードのスコアを\+1する。?$', eff_compact)
    if m:
        group_name = str(m.group('group') or '').strip()
        return {
            'kind': 'add_live_success_score_bonus_if_revealed_group_members_have_all_six_colors',
            'bonus': 1,
            'condition_group_name': group_name,
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }

    m = re.match(r'^エールにより公開された自分のカードの中に(?P<tag><\([^)]+\)>)を持つカードが(?P<n>\d+)枚以上ある場合このカードのスコアを\+(?P<delta>\d+)する。?$', eff_compact)
    if m:
        tag = str(m.group('tag') or '').strip()
        n = int(m.group('n') or 0)
        delta = int(m.group('delta') or 0)
        return {
            'kind': 'add_live_success_score_bonus_if_revealed_card_tag_count_at_least',
            'bonus': int(delta),
            'condition_tag': tag,
            'condition_count': int(n),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }
    m = re.match(r'^エールにより公開された自分のカードの中にライブカードが(?P<count>\d+)枚以上あるとき、自分のエネルギーデッキから、エネルギーカードを(?P<n>\d+)枚ウェイト状態で置く。?$', eff_norm)
    if m:
        need = int(m.group('count') or 0)
        n = int(m.group('n') or 0)
        return {
            'kind': 'put_wait_energy_if_revealed_live_count_at_least',
            'condition_count': int(need),
            'count': int(n),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }
    m = re.match(r'^エールにより公開された自分のカードの中に『(?P<group>[^』]+)』のカードが(?P<count>\d+)枚以上ある場合、自分のエネルギーデッキから、エネルギーカードを(?P<n>\d+)枚ウェイト状態で置く。?$', eff_norm)
    if m:
        group_name = str(m.group('group') or '').strip()
        need = int(m.group('count') or 0)
        n = int(m.group('n') or 0)
        return {
            'kind': 'put_wait_energy_if_revealed_group_card_count_at_least',
            'condition_group_name': group_name,
            'condition_count': int(need),
            'count': int(n),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }
    m = re.match(r'^エールにより公開された自分のカードの中に『(?P<group>[^』]+)』のメンバーカードが(?P<count>\d+)枚以上ある場合、このカードのスコアを\+(?P<delta>\d+)する。?$', eff_norm)
    if m:
        return {
            'kind': 'add_live_success_score_bonus_if_revealed_group_member_count_at_least',
            'condition_group_name': str(m.group('group') or '').strip(),
            'condition_count': int(m.group('count') or 0),
            'bonus': int(m.group('delta') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }
    m = re.match(r'^エールにより公開された自分のカードの中にライブカードが(?:1枚以上)?ある場合、このカードのスコアを\+(?P<delta>\d+)する。?$', eff_norm)
    if m:
        return {
            'kind': 'add_live_success_score_bonus_if_revealed_live_count_at_least',
            'condition_count': 1,
            'bonus': int(m.group('delta') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }
    m = re.match(r'^エールにより公開された自分のカードの中に、?(?P<tag><\([^)]+\)>)を持つ『(?P<group>[^』]+)』のライブカードが(?:1枚以上)?ある場合、ライブの合計スコアを\+(?P<delta>\d+)する。?$', eff_norm)
    if m:
        return {
            'kind': 'add_live_success_score_bonus_if_revealed_group_live_has_tag',
            'condition_tag': str(m.group('tag') or '').strip(),
            'condition_group_name': str(m.group('group') or '').strip(),
            'bonus': int(m.group('delta') or 0),
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }
    m = re.match(r'^自分のステージにいるウェイト状態のメンバー1人につき、このカードのスコアを\+(?P<per>\d+)する。?$', eff_norm)
    if m:
        per = int(m.group('per') or 0)
        return {
            'kind': 'add_live_success_score_bonus_per_weight_member',
            'bonus_per': per,
            'source_cn': str(source_cn or ''),
            'pos': str(pos or ''),
            'ctx': dict(ctx or {}),
            'label': str(label or ''),
        }
    return {
        'kind': 'apply_effect_template_on_live_success',
        'effect': eff_raw,
        'source_cn': str(source_cn or ''),
        'pos': str(pos or ''),
        'ctx': dict(ctx or {}),
        'label': str(label or ''),
    }
def _enqueue_success_auto_order(gs: GameState, triggers: List[Dict[str, Any]]) -> int:
    triggers = list(triggers or [])
    n = len(triggers)
    if n <= 0:
        return 0
    text = 'ライブ成功時効果が発生：解決するカードを選択' if n == 1 else 'ライブ成功時効果が複数発生：解決するカードを選択（1つずつ）'
    gs.pending.append({
        'kind': 'auto_order',
        'text': text,
        'options': [_auto_trigger_option_text(t) for t in triggers if _auto_trigger_option_text(t)],
        'queue': list(triggers),
    })
    gs.log.append(f"[PROMPT] live-success abilities queued: {n}")
    return n
def _run_live_success_triggers(gs: GameState, rng: random.Random, cards_db: Dict[str, CardInfo], lives: List[str]) -> None:
    success_triggers: List[Dict[str, Any]] = []
    """Collect and execute <ライブ成功時> triggers at LIVE_RESOLVE timing.
    All success triggers that occur at the same timing are first normalized into a
    common queue. If multiple triggers exist, the user chooses the resolution order.
    """
    # Stage-member success triggers
    for pos in ('L', 'C', 'R'):
        slot = gs.stage.get(pos)
        if not slot or not slot.active:
            continue
        ci_src = _get_card(cards_db, slot.cardnumber)
        if not ci_src or not getattr(ci_src, 'abilities', None):
            continue
        for ab in _iter_triggered_abilities(ci_src, 'ライブ成功時'):
            ctx = {'pos': pos, 'source_cn': ci_src.cardnumber}
            if isinstance(ab, dict) and _ability_has_choose_header(ab):
                success_triggers.append({
                    'kind': 'enqueue_choose_effects_from_ability_on_live_success',
                    'ability': dict(ab),
                    'ctx': dict(ctx),
                    'source_cn': ci_src.cardnumber,
                    'label': f"{pos}: {ci_src.cardnumber}[ライブ成功時]",
                })
                continue
            clauses = ab.get('clauses', [])
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                cost = str(cl.get('cost_template', '') or '')
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                if _parse_energy_cost(cost) > 0 or _cost_requires_self_to_green(cost):
                    continue
                m_opt = re.search(r'手札を(\d+)枚控え室に置いてもよい', cost)
                if m_opt and _match_effect_template(eff) and 'retrieve_from_yell' == (_match_effect_template(eff) or [{}])[0].get('op', ''):
                    cost_n = int(m_opt.group(1))
                    success_triggers.append({
                        'kind': 'enqueue_optional_discard_from_hand_for_effect_on_live_success',
                        'effect_text': eff,
                        'prompt': {
                            'kind': 'live_success_pay_effect',
                            'pos': pos,
                            'cn': ci_src.cardnumber,
                            'cost_kind': 'discard_from_hand',
                            'cost_n': cost_n,
                            'effect': eff,
                            'text': f"{pos}: {ci_src.cardnumber}[ライブ成功時] 手札を{cost_n}枚控え室に置いてもよい → {eff}",
                            'options': ['pay', 'skip'],
                            'source_cn': ci_src.cardnumber,
                            'ctx': {'pos': pos, 'source_cn': ci_src.cardnumber},
                        },
                        'source_cn': ci_src.cardnumber,
                        'label': f"{pos}: {ci_src.cardnumber}[ライブ成功時]",
                    })
                    continue
                trig = _build_live_success_trigger_from_effect(
                    gs,
                    cards_db,
                    eff,
                    str(ci_src.cardnumber or ''),
                    f"{pos}: {ci_src.cardnumber}[ライブ成功時]",
                    {'pos': pos, 'source_cn': ci_src.cardnumber},
                    pos=pos,
                )
                if trig:
                    try:
                        trig.setdefault('effect_text', eff)
                    except Exception:
                        pass
                    success_triggers.append(trig)
    # BODY-granted live-success abilities on active stage members.
    # Example: PL!S-bp2-008 小原鞠莉 gains a live-success total-score bonus ability
    # if all stage areas have distinct 『Aqours』 members.
    for pos in ('L', 'C', 'R'):
        slot = gs.stage.get(pos)
        if not slot or not slot.active:
            continue
        ci_src = _get_card(cards_db, slot.cardnumber)
        if not ci_src or not getattr(ci_src, 'abilities', None):
            continue
        for ab in list(getattr(ci_src, 'abilities', []) or []):
            if not isinstance(ab, dict):
                continue
            if 'BODY' not in str(ab.get('trigger', '') or '') and '常時' not in str(ab.get('ability_type', '') or ''):
                continue
            clauses = ab.get('clauses', [])
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if '「<ライブ成功時>' not in eff or 'ライブの合計スコア' not in eff:
                    continue
                eff_norm2 = _normalize_icon_token_text(eff).replace('\n', '')
                m = re.match(r'^自分のステージのエリアすべてに『(?P<group>[^』]+)』のメンバーが登場しており、かつ名前が異なる場合、「<ライブ成功時>エールにより公開された自分のカードの中にライブカードが(?P<c1>\d+)枚以上ある場合、ライブの合計スコアを\+(?P<b1>\d+)する。ライブカードが(?P<c2>\d+)枚以上ある場合、代わりに合計スコアを\+(?P<b2>\d+)する。」を得る。?$', eff_norm2)
                if not m:
                    continue
                group_name = str(m.group('group') or '').strip()
                if not _stage_all_areas_group_members_distinct_names(gs, cards_db, group_name):
                    gs.log.append(f"[SKIP] {pos}: {ci_src.cardnumber}[BODY gained live-success] stage all distinct 『{group_name}』 condition not met")
                    continue
                success_triggers.append({
                    'kind': 'add_live_success_total_score_bonus_if_revealed_live_count_tier',
                    'condition_count_one': int(m.group('c1') or 1),
                    'bonus_one': int(m.group('b1') or 0),
                    'condition_count_two': int(m.group('c2') or 0),
                    'bonus_two': int(m.group('b2') or 0),
                    'source_cn': ci_src.cardnumber,
                    'pos': pos,
                    'ctx': {'pos': pos, 'source_cn': ci_src.cardnumber},
                    'label': f"{pos}: {ci_src.cardnumber}[常時で得たライブ成功時]",
                    'effect_text': eff,
                })

    # Live-card success triggers
    for cn_live in list(lives or []):
        ci_live = _get_card(cards_db, cn_live)
        if not ci_live or not getattr(ci_live, 'abilities', None):
            continue
        for ab in _iter_triggered_abilities(ci_live, 'ライブ成功時'):
            ctx2 = {'source_cn': cn_live}
            if isinstance(ab, dict) and _ability_has_choose_header(ab):
                success_triggers.append({
                    'kind': 'enqueue_choose_effects_from_ability_on_live_success',
                    'ability': dict(ab),
                    'ctx': dict(ctx2),
                    'source_cn': cn_live,
                    'label': f"{cn_live}[ライブ成功時]",
                })
                continue
            clauses = ab.get('clauses', [])
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                cost = str(cl.get('cost_template', '') or '')
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if not eff:
                    continue
                if _parse_energy_cost(cost) > 0 or _cost_requires_self_to_green(cost):
                    continue
                trig = _build_live_success_trigger_from_effect(
                    gs,
                    cards_db,
                    eff,
                    str(cn_live or ''),
                    f"{cn_live}[ライブ成功時]",
                    {'source_cn': cn_live},
                )
                if trig:
                    try:
                        trig.setdefault('effect_text', eff)
                    except Exception:
                        pass
                    success_triggers.append(trig)
    # Cards revealed by YELL may themselves have <ライブ成功時> abilities.
    # Only collect abilities that explicitly say they work while this card is revealed by own yell.
    for cn_rev in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci_rev = _get_card(cards_db, cn_rev)
        if not ci_rev or not getattr(ci_rev, 'abilities', None):
            continue
        for ab in _iter_triggered_abilities(ci_rev, 'ライブ成功時'):
            clauses = ab.get('clauses', []) if isinstance(ab, dict) else []
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if 'このカードが自分のエールによって公開されている場合のみ発動する' not in eff:
                    continue
                trig = _build_live_success_trigger_from_effect(
                    gs,
                    cards_db,
                    eff,
                    str(cn_rev or ''),
                    f"{cn_rev}[ライブ成功時/エール公開]",
                    {'source_cn': cn_rev, 'from_yell_revealed': True},
                )
                if trig:
                    try:
                        trig.setdefault('effect_text', eff)
                    except Exception:
                        pass
                    success_triggers.append(trig)

    if success_triggers:
        _enqueue_success_auto_order(gs, success_triggers)
# ----------------------------
# Step21: LIVE scoring helpers (UI)
# ----------------------------
def _effective_success_zone_live_score(cn_live, gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    ci = _get_card(cards_db, cn_live)
    if not ci:
        return 0
    try:
        base = int(getattr(ci, 'score', 0) or 0)
    except Exception:
        base = 0
    bonus = 0
    # Future success-zone score modifiers should be routed here so all
    # "成功ライブカード置き場のスコア合計" references stay consistent.
    return int(base + bonus)

def _success_zone_score_sum(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    total = 0
    for cn in list(getattr(gs, 'success_zone', []) or []):
        try:
            total += int(_effective_success_zone_live_score(cn, gs, cards_db) or 0)
        except Exception:
            pass
    return int(total)
def _mu_live_cards_in_set_zone_count(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    n = 0
    for cn in list(getattr(gs, 'set_zone', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if not _is_live_ci(ci):
            continue
        if "μ's" in str(getattr(ci, 'group', '') or ''):
            n += 1
    return int(n)
def _ci_matches_group_or_unit(ci: Optional[CardInfo], label: str) -> bool:
    if not ci:
        return False
    lab = str(label or '').strip()
    if not lab:
        return False
    g = str(getattr(ci, 'group', '') or '').strip()
    u = str(getattr(ci, 'unit', '') or '').strip()
    if (g == lab) or (u == lab) or (lab in g if g else False) or (lab in u if u else False):
        return True
    # Some μ's BP5 A-RISE member rows can arrive from compiled DB with blank
    # group/unit despite the min DB carrying group=A-RISE.  Keep the fallback in
    # the shared matcher so condition checks and group filters stay consistent.
    if lab == 'A-RISE':
        cn = str(getattr(ci, 'cardnumber', '') or '').strip()
        nm = str(getattr(ci, 'name', '') or getattr(ci, 'cardname', '') or '').strip()
        if cn in {'PL!-bp5-111', 'PL!-bp5-222', 'PL!-bp5-333'}:
            return True
        if nm in {'綺羅ツバサ', '優木あんじゅ', '統堂英玲奈'}:
            return True
    return False
def _green_live_count_by_group_or_unit(gs: GameState, cards_db: Dict[str, CardInfo], label: str) -> int:
    n = 0
    for cn in list(getattr(gs, 'green_room', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if not _is_live_ci(ci):
            continue
        if _ci_matches_group_or_unit(ci, label):
            n += 1
    return int(n)
def _live_start_score_bonus_if_green_live_group_or_unit_count(cn_live, gs: GameState, cards_db: Dict[str, CardInfo], set_idx: Optional[int] = None) -> int:
    if not _live_start_set_idx_resolved(gs, set_idx):
        return 0
    mapped = int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
    if mapped > 0:
        return mapped
    ci = _get_card(cards_db, cn_live)
    parsed = _parse_live_start_score_if_green_live_group_count(ci)
    if not parsed:
        return 0
    group_name, need, delta = parsed
    cnt = int(_green_live_count_by_group_or_unit(gs, cards_db, group_name))
    return int(delta if cnt >= int(need) else 0)
def _live_start_set_idx_resolved(gs: Optional[GameState], set_idx: Optional[int]) -> bool:
    try:
        if gs is None:
            return False
        # Generalized live-start wrappers may not carry a concrete set_idx.
        # In that case, resolution itself is the gating event, so treat None as resolved.
        if set_idx is None:
            return True
        return int(set_idx) in [int(x) for x in (getattr(gs, 'live_start_resolved_set_idxs', []) or [])]
    except Exception:
        return False
def _mark_live_start_set_idx_resolved(gs: GameState, set_idx: Optional[int]) -> None:
    try:
        if set_idx is None:
            return
        xs = [int(x) for x in (getattr(gs, 'live_start_resolved_set_idxs', []) or [])]
        k = int(set_idx)
        if k not in xs:
            xs.append(k)
        gs.live_start_resolved_set_idxs = xs
    except Exception:
        pass

def _add_live_start_score_bonus(gs: GameState, bonus: int, set_idx: Optional[int] = None, source_cn: Optional[str] = None) -> None:
    try:
        bonus = int(bonus or 0)
        if bonus == 0:
            return
        if set_idx is not None:
            smap = dict(getattr(gs, 'live_start_score_bonus_by_set_idx', {}) or {})
            k = int(set_idx)
            smap[k] = int(smap.get(k, 0) or 0) + bonus
            gs.live_start_score_bonus_by_set_idx = smap
            return
        canon = _canon_cardno(str(source_cn or ''))
        if not canon:
            return
        smap = dict(getattr(gs, 'live_start_score_bonus_by_cn', {}) or {})
        smap[canon] = int(smap.get(canon, 0) or 0) + bonus
        gs.live_start_score_bonus_by_cn = smap
    except Exception:
        pass

def _live_score_delta_for_attempt(cn_live, lives_count, gs_turn):
    # Legacy base path retained for compatibility; generalized live-count wrappers
    # are handled in _extra_live_score_delta_for_attempt where cards_db is available.
    return 0

def _live_start_score_bonus_for_set_idx(gs: Optional[GameState], set_idx: Optional[int], source_cn: Optional[str] = None) -> int:
    try:
        if gs is None:
            return 0
        if set_idx is not None:
            v = int(dict(getattr(gs, 'live_start_score_bonus_by_set_idx', {}) or {}).get(int(set_idx), 0) or 0)
            if v > 0:
                return v
        canon = _canon_cardno(str(source_cn or ''))
        if not canon:
            return 0
        return int(dict(getattr(gs, 'live_start_score_bonus_by_cn', {}) or {}).get(canon, 0) or 0)
    except Exception:
        return 0

def _live_start_required_any_reduction_for_set_idx(gs: Optional[GameState], set_idx: Optional[int], source_cn: Optional[str] = None) -> int:
    try:
        if gs is None:
            return 0
        if set_idx is not None:
            v = int(dict(getattr(gs, 'live_start_required_any_reduction_by_set_idx', {}) or {}).get(int(set_idx), 0) or 0)
            if v > 0:
                return v
        canon = _canon_cardno(str(source_cn or ''))
        if not canon:
            return 0
        return int(dict(getattr(gs, 'live_start_required_any_reduction_by_cn', {}) or {}).get(canon, 0) or 0)
    except Exception:
        return 0



def _live_start_required_any_increase_for_set_idx(gs: Optional[GameState], set_idx: Optional[int], source_cn: Optional[str] = None) -> int:
    try:
        if gs is None:
            return 0
        if set_idx is not None:
            v = int(dict(getattr(gs, 'live_start_required_any_increase_by_set_idx', {}) or {}).get(int(set_idx), 0) or 0)
            if v > 0:
                return v
        canon = _canon_cardno(str(source_cn or ''))
        if not canon:
            return 0
        return int(dict(getattr(gs, 'live_start_required_any_increase_by_cn', {}) or {}).get(canon, 0) or 0)
    except Exception:
        return 0

def _success_zone_cardname_count(gs: GameState, cards_db: Dict[str, CardInfo], cardname: str) -> int:
    if gs is None:
        return 0
    target = str(cardname or '').strip()
    if not target:
        return 0
    n = 0
    for cn in list(getattr(gs, 'success_zone', []) or []):
        ci = _get_card(cards_db, cn)
        nm = str(getattr(ci, 'name', '') or '').strip() if ci else ''
        if nm == target:
            n += 1
    return int(n)

def _live_start_score_and_required_any_bonus_per_success_zone_cardname_count(cn_live, gs: GameState, cards_db: Dict[str, CardInfo], set_idx: Optional[int] = None) -> Tuple[int, int]:
    if not _live_start_set_idx_resolved(gs, set_idx):
        return 0, 0
    mapped_score = int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
    mapped_any = int(_live_start_required_any_increase_for_set_idx(gs, set_idx, source_cn=cn_live))
    if mapped_score > 0 or mapped_any > 0:
        return int(mapped_score), int(mapped_any)
    ci = _get_card(cards_db, cn_live)
    parsed = _parse_live_start_score_and_increase_any_per_success_zone_cardname_count(ci)
    if not parsed:
        return 0, 0
    cardname, per_score, per_any = parsed
    cnt = int(_success_zone_cardname_count(gs, cards_db, cardname))
    return int(per_score * cnt), int(per_any * cnt)
def _live_start_required_any_reduction_if_success_score(cn_live, gs: GameState, cards_db: Dict[str, CardInfo], set_idx: Optional[int] = None) -> int:
    if not _live_start_set_idx_resolved(gs, set_idx):
        return 0
    mapped = int(_live_start_required_any_reduction_for_set_idx(gs, set_idx, source_cn=cn_live))
    if mapped > 0:
        return mapped
    ci = _get_card(cards_db, cn_live)
    parsed = _parse_live_start_reduce_any_and_score_if_success_score(ci)
    if not parsed:
        return 0
    reduce_th, reduce_any, _score_th, _delta = parsed
    total = _success_zone_score_sum(gs, cards_db)
    return int(reduce_any if int(total) >= int(reduce_th) else 0)
def _live_start_score_bonus_if_success_score(cn_live, gs: GameState, cards_db: Dict[str, CardInfo], set_idx: Optional[int] = None) -> int:
    if not _live_start_set_idx_resolved(gs, set_idx):
        return 0
    mapped = int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
    if mapped > 0:
        return mapped
    ci = _get_card(cards_db, cn_live)
    parsed = _parse_live_start_reduce_any_and_score_if_success_score(ci)
    if not parsed:
        return 0
    _reduce_th, _reduce_any, score_th, delta = parsed
    total = _success_zone_score_sum(gs, cards_db)
    return int(delta if int(total) >= int(score_th) else 0)
def _live_start_score_bonus_if_live_zone_group_count(cn_live, gs: GameState, cards_db: Dict[str, CardInfo], set_idx: Optional[int] = None) -> int:
    if not _live_start_set_idx_resolved(gs, set_idx):
        return 0
    mapped = int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
    if mapped > 0:
        return mapped
    ci = _get_card(cards_db, cn_live)
    parsed = _parse_live_start_score_if_live_zone_group_count(ci)
    if not parsed:
        return 0
    group_name, need, delta = parsed
    cnt = int(_live_zone_group_card_count(gs, cards_db, group_name))
    return int(delta if cnt >= int(need) else 0)
def _effective_live_required_hearts(cn_live, ci, gs: GameState, cards_db: Optional[Dict[str, CardInfo]] = None, set_idx: Optional[int] = None) -> Dict[str, int]:
    req = dict((getattr(ci, 'required_hearts', {}) if ci else {}) or {})
    try:
        _emo_score, _emo_any = _live_start_score_and_required_any_bonus_per_success_zone_cardname_count(cn_live, gs, cards_db=(cards_db or {}), set_idx=set_idx)
        extra_any = int(_emo_any)
    except Exception:
        extra_any = 0
    if extra_any > 0:
        req['any'] = int(req.get('any', 0) or 0) + extra_any
    try:
        reduce_any = int(_live_start_required_any_reduction_if_success_score(cn_live, gs, cards_db=(cards_db or {}), set_idx=set_idx))
    except Exception:
        reduce_any = 0
    if reduce_any <= 0:
        try:
            reduce_any = int(_live_start_required_any_reduction_for_set_idx(gs, set_idx, source_cn=cn_live))
        except Exception:
            reduce_any = 0
    if reduce_any > 0:
        req['any'] = max(0, int(req.get('any', 0) or 0) - reduce_any)
    return req

def _extra_live_score_delta_for_attempt(cn_live, gs: GameState, cards_db: Dict[str, CardInfo], set_idx: Optional[int] = None, lives_count: Optional[int] = None) -> int:
    try:
        canon = _canon_cardno(cn_live)
    except Exception:
        canon = str(cn_live or '')
    ci_live = _get_card(cards_db, cn_live)
    parsed_live_count = _parse_live_start_score_if_live_count(ci_live)
    if parsed_live_count is not None:
        need, delta = parsed_live_count
        mapped = int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
        if mapped > 0:
            return mapped
        try:
            lc = int(lives_count if lives_count is not None else 0)
        except Exception:
            lc = 0
        return int(delta if lc >= int(need) else 0)
    if _parse_live_start_score_per_stage_group_member_heart_color_kind(ci_live) is not None:
        return int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
    if _parse_live_start_score_if_success_zone_has_scores(ci_live) is not None:
        return int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
    if _parse_live_start_score_if_green_unique_live_names_group_count(ci_live) is not None:
        return int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
    parsed_emotion = _parse_live_start_score_and_increase_any_per_success_zone_cardname_count(ci_live)
    if parsed_emotion is not None:
        _m = int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
        if _m > 0:
            return _m
        return int(_live_start_score_and_required_any_bonus_per_success_zone_cardname_count(cn_live, gs, cards_db, set_idx=set_idx)[0])
    if _parse_live_start_score_if_live_zone_group_count(_get_card(cards_db, cn_live)) is not None:
        _m = int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
        return _m if _m > 0 else int(_live_start_score_bonus_if_live_zone_group_count(cn_live, gs, cards_db, set_idx=set_idx))
    if _parse_live_start_score_if_green_live_group_count(_get_card(cards_db, cn_live)) is not None:
        _m = int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
        return _m if _m > 0 else int(_live_start_score_bonus_if_green_live_group_or_unit_count(cn_live, gs, cards_db, set_idx=set_idx))
    if _parse_live_start_reduce_any_and_score_if_success_score(_get_card(cards_db, cn_live)) is not None:
        _m = int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
        return _m if _m > 0 else int(_live_start_score_bonus_if_success_score(cn_live, gs, cards_db, set_idx=set_idx))
    if _parse_live_start_score_and_pick_group_member_temp_blade(ci_live) is not None:
        return int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
    if _parse_live_start_optional_pay_energy_for_self_score_if_group(ci_live) is not None:
        return int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
    if _parse_live_start_top_keep_one_then_reveal_top_score_if_live_by_group_count(ci_live) is not None:
        return int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live))
    # Generic fallback for live-start effects that are resolved through a confirmation/ack
    # prompt and stored directly by set_idx/card number.  This covers families whose
    # conditions are checked before score computation rather than recomputed here, such as
    # success-storage-count based score bonuses.
    _mapped_live_start_bonus = int(_live_start_score_bonus_for_set_idx(gs, set_idx, source_cn=cn_live) or 0)
    if _mapped_live_start_bonus:
        return _mapped_live_start_bonus
    return 0

def _compute_attempt_score_breakdown(lives, cards_db, gs_turn, gs=None, live_set_indices=None):
    lives_count = len(lives or [])
    total = 0
    rows = []
    live_set_indices = list(live_set_indices or [])
    for _i, cn in enumerate((lives or [])):
        set_idx = live_set_indices[_i] if _i < len(live_set_indices) else None
        ci = _get_card(cards_db, cn)
        base = int(getattr(ci, 'score', 0) or 0) if ci else 0
        delta = int(_live_score_delta_for_attempt(cn, lives_count, gs_turn))
        if gs is not None:
            delta += int(_extra_live_score_delta_for_attempt(cn, gs, cards_db, set_idx=set_idx, lives_count=lives_count))
        eff = base + delta
        total += eff
        rows.append({'cn': cn, 'base': base, 'delta': delta, 'score': eff})
    return total, rows
def _stage_group_member_heart_color_kinds(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> int:
    cols = set()
    tag = str(group_name or '').strip()
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'active', False):
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci or _is_live_ci(ci):
            continue
        if tag and not _slot_matches_group_tag(ci, tag):
            continue
        for k, v in ((getattr(ci, 'base_hearts', None) or {}) or {}).items():
            if k in ('pink', 'red', 'yellow', 'green', 'blue', 'purple') and int(v or 0) > 0:
                cols.add(k)
    return int(len(cols))
def _success_zone_score_set_bonus(gs: GameState, cards_db: Dict[str, CardInfo], score_a: int = 1, score_b: int = 5, delta_one: int = 1, delta_both: int = 2) -> int:
    has_a = False
    has_b = False
    for cn in list(getattr(gs, 'success_zone', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        sc = int(getattr(ci, 'score', 0) or 0)
        if sc == int(score_a):
            has_a = True
        elif sc == int(score_b):
            has_b = True
    if has_a and has_b:
        return int(delta_both)
    if has_a or has_b:
        return int(delta_one)
    return 0
def _green_unique_live_names_count(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> int:
    names = set()
    tag = str(group_name or '').strip()
    for cn in list(getattr(gs, 'green_room', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci or not _is_live_ci(ci):
            continue
        if tag and not _slot_matches_group_tag(ci, tag):
            continue
        nm = str(getattr(ci, 'name', '') or getattr(ci, 'cardname', '') or getattr(ci, 'title', '') or cn)
        if nm:
            names.add(nm)
    return int(len(names))

def _ci_blade_heart_raw_text(ci: Optional[CardInfo]) -> str:
    if not ci:
        return ''
    parts: List[str] = []
    raw = str(getattr(ci, 'blade_heart_raw', '') or '').strip()
    if raw:
        parts.append(raw)
    try:
        tags = _parse_tags_json(str(getattr(ci, 'blade_heart_tags_json', '') or '[]'))
        parts.extend([str(x) for x in tags if str(x).strip()])
    except Exception:
        pass
    try:
        for k, v in (getattr(ci, 'blade_hearts', {}) or {}).items():
            if int(v or 0) > 0:
                jp = {'pink':'桃','red':'赤','yellow':'黄','green':'緑','blue':'青','purple':'紫','all':'ALL'}.get(str(k), str(k))
                parts.append(f'<{jp}>')
    except Exception:
        pass
    return _normalize_icon_token_text(' '.join(parts))


def _ci_has_blade_heart_payload(ci: Optional[CardInfo]) -> bool:
    txt = _ci_blade_heart_raw_text(ci)
    if not txt:
        return False
    if txt.strip() in {'なし', '-', '[]'}:
        return False
    return bool(re.search(r'<\([^)]+\)>', txt))


def _ci_blade_heart_has_tag(ci: Optional[CardInfo], tag_text: str) -> bool:
    marker = _normalize_tag_marker(_normalize_icon_token_text(tag_text))
    if not marker:
        return False
    txt = _ci_blade_heart_raw_text(ci)
    # Compare by normalized inner marker: ALL, スコア+1, ドロー+1, etc.
    inners = [str(x).strip().replace('＋', '+').replace(' ', '') for x in re.findall(r'<\(([^)]+)\)>', txt)]
    return marker.replace('＋', '+').replace(' ', '') in inners


def _ci_base_heart_color_keys(ci: Optional[CardInfo]) -> set:
    colors = set()
    if not ci:
        return colors
    try:
        for k, v in (getattr(ci, 'base_hearts', {}) or {}).items():
            if int(v or 0) > 0 and str(k) in {'pink','red','yellow','green','blue','purple'}:
                colors.add(str(k))
    except Exception:
        pass
    raw = _normalize_icon_token_text(str(getattr(ci, 'base_hearts_raw', '') or ''))
    for inner in re.findall(r'<\(([^)]+)\)>', raw):
        col = _HEART_ICON_COLOR_MAP.get(str(inner or '').strip())
        if col:
            colors.add(col)
    return colors

def _normalize_tag_marker(tag_text: str) -> str:
    tag = _normalize_icon_token_text(str(tag_text or '').strip())
    if tag.startswith('<(') and tag.endswith(')>'):
        tag = tag[2:-2].strip()
    elif tag.startswith('<') and tag.endswith('>'):
        tag = tag[1:-1].strip()
    return str(tag or '').replace('＋', '+').replace(' ', '')

def _count_yell_revealed_cards_with_tag(gs: GameState, cards_db: Dict[str, CardInfo], tag_text: str) -> int:
    tag = _normalize_tag_marker(tag_text)
    if not tag:
        return 0
    n = 0
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if _ci_blade_heart_has_tag(ci, tag):
            n += 1
    return int(n)
def _count_yell_revealed_live_cards(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    n = 0
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if ci and _is_live_ci(ci):
            n += 1
    return int(n)

def _count_yell_revealed_group_cards(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> int:
    group_name = str(group_name or '').strip()
    n = 0
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if ci and _ci_matches_group_or_unit(ci, group_name):
            n += 1
    return int(n)

def _count_yell_revealed_group_members(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> int:
    group_name = str(group_name or '').strip()
    n = 0
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if ci and _is_member_ci(ci) and _ci_matches_group_or_unit(ci, group_name):
            n += 1
    return int(n)

def _count_yell_revealed_distinct_named_group_members(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> int:
    group_name = str(group_name or '').strip()
    names = set()
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci or not _is_member_ci(ci) or not _ci_matches_group_or_unit(ci, group_name):
            continue
        # Runtime CardInfo normally exposes the display name as `name`; older
        # extracted JSON uses `cardname`.  Use both before falling back to the
        # card number.  Without this, valid revealed Liella! members can be
        # counted as 0 because their group matches but their `cardname` attr is
        # absent.
        nm = str(
            getattr(ci, 'name', '')
            or getattr(ci, 'cardname', '')
            or getattr(ci, 'title', '')
            or cn
        ).strip()
        if nm:
            names.add(nm)
    return int(len(names))

def _yell_compact_text(text: str) -> str:
    t = _normalize_icon_token_text(_norm_digits_jp(str(text or '')))
    t = re.sub(r'\s+', '', t)
    t = t.replace('，', '、')
    return t

def _parse_icons_compact(icon_blob: str) -> Tuple[int, Dict[str, int]]:
    """Parse compact icon blob into (blade_count, hearts incl. ALL)."""
    b = 0
    hearts: Dict[str, int] = {}
    blob = _normalize_icon_token_text(str(icon_blob or ''))
    for m in re.finditer(r'<\(([^)]+)\)>', blob):
        jp = str(m.group(1) or '').strip()
        if jp == 'ブレード':
            b += 1
            continue
        if jp == 'ALL':
            hearts['all'] = int(hearts.get('all', 0) or 0) + 1
            continue
        col = _HEART_ICON_COLOR_MAP.get(jp)
        if col:
            hearts[col] = int(hearts.get(col, 0) or 0) + 1
    return int(b), hearts

def _grant_temp_icons_to_slot(slot: StageSlot, icon_blob: str, mult: int = 1) -> Tuple[int, Dict[str, int]]:
    try:
        mult_i = max(0, int(mult or 0))
    except Exception:
        mult_i = 1
    b, hearts = _parse_icons_compact(icon_blob)
    if b and mult_i:
        slot.temp_blade = int(getattr(slot, 'temp_blade', 0) or 0) + int(b * mult_i)
        slot.temp_until = 'end_of_live'
    applied_hearts: Dict[str, int] = {}
    for col, cnt in (hearts or {}).items():
        n = int(cnt or 0) * int(mult_i)
        if n:
            _grant_temp_heart(slot, col, n)
            applied_hearts[col] = int(applied_hearts.get(col, 0) or 0) + n
    return int(b * mult_i), applied_hearts

def _card_has_blade_heart(ci: Optional[CardInfo]) -> bool:
    return _ci_has_blade_heart_payload(ci)

def _count_yell_revealed_no_bladeheart_cards(gs: GameState, cards_db: Dict[str, CardInfo], member_only: bool = False) -> int:
    n = 0
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if member_only and not _is_member_ci(ci):
            continue
        if not _ci_has_blade_heart_payload(ci):
            n += 1
    return int(n)

def _count_yell_revealed_no_bladeheart_group_members(gs: GameState, cards_db: Dict[str, CardInfo], group_name: str) -> int:
    group_name = str(group_name or '').strip()
    n = 0
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci or not _is_member_ci(ci):
            continue
        if group_name and not _ci_matches_group_or_unit(ci, group_name):
            continue
        if not _ci_has_blade_heart_payload(ci):
            n += 1
    return int(n)

def _yell_revealed_bladeheart_kind_count(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    colors = set()
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        txt = _ci_blade_heart_raw_text(ci)
        for inner in re.findall(r'<\(([^)]+)\)>', txt):
            key = str(inner or '').strip()
            col = _HEART_ICON_COLOR_MAP.get(key)
            if col:
                colors.add(col)
            elif key == 'ALL':
                colors.update(['pink', 'red', 'yellow', 'green', 'blue', 'purple'])
    return int(len(colors))

def _collect_yell_revealed_body_auto_triggers(gs: GameState, cards_db: Dict[str, CardInfo], revealed: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Collect generic BODY <自動><ターン1回> triggers that look at this yell's revealed cards.

    This function only detects triggered abilities and builds queue entries.
    Actual effects are applied by _apply_yell_revealed_body_auto_trigger(), so the UI can always show
    a popup before resolution, matching the project's auto-trigger policy.
    """
    if revealed is None:
        revealed = list(getattr(gs, '_yell_revealed_this_live', []) or [])
    if not revealed:
        return []
    triggers: List[Dict[str, Any]] = []
    live_n = int(_count_yell_revealed_live_cards(gs, cards_db) or 0)
    no_bh_cards = int(_count_yell_revealed_no_bladeheart_cards(gs, cards_db, member_only=False) or 0)
    no_bh_members = int(_count_yell_revealed_no_bladeheart_cards(gs, cards_db, member_only=True) or 0)
    bh_kind_n = int(_yell_revealed_bladeheart_kind_count(gs, cards_db) or 0)

    def _append_trigger(pos: str, canon: str, usage_key: str, once_per_turn: bool, title: str, effect_kind: str, **params: Any) -> None:
        triggers.append({
            'kind': 'yell_revealed_body_auto',
            'source_cn': canon,
            'pos': str(pos or '').upper(),
            'usage_key': usage_key,
            'once_per_turn': bool(once_per_turn),
            'label': f"{canon}({str(pos or '').upper()})[エール時]: {title}",
            'effect_kind': effect_kind,
            **params,
        })

    sources: List[Tuple[str, str]] = []
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'cardnumber', ''):
            continue
        canon = _canon_cardno(getattr(slot, 'cardnumber', '') or '')
        if canon:
            sources.append((pos, canon))

    # LIVE cards in the current live storage can also have BODY-style
    # "自分がエールした時" abilities (e.g. PL!S-bp6-021 / PL!HS-bp6-027).
    # They must be checked at the same YELL timing as stage-member BODY autos.
    for i, cn_live in enumerate(list(getattr(gs, 'set_zone', []) or [])):
        canon = _canon_cardno(cn_live)
        ci_live = _get_card(cards_db, canon)
        if not canon or not ci_live or not _is_live_ci(ci_live):
            continue
        if not getattr(ci_live, 'abilities', None):
            continue
        sources.append((f'LIVE{i+1}', canon))

    seen_sources: Set[Tuple[str, str]] = set()
    for pos, canon in sources:
        key_src = (str(pos or '').upper(), _canon_cardno(canon))
        if key_src in seen_sources:
            continue
        seen_sources.add(key_src)
        ci_src = _get_card(cards_db, canon)
        if not ci_src:
            continue
        abs_ = list(getattr(ci_src, 'abilities', []) or [])
        for ai, ab in enumerate(abs_):
            if not isinstance(ab, dict):
                continue
            at = str(ab.get('ability_type', '') or '')
            trig = str(ab.get('trigger', '') or '')
            if ('自動' not in at) and ('自動' not in trig) and ('BODY' not in trig):
                continue
            flags = _ability_usage_flags(ab)
            clauses = ab.get('clauses', [])
            if not isinstance(clauses, list):
                continue
            for ci_idx, cl in enumerate(clauses):
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                if 'エール' not in eff:
                    continue
                ec = _yell_compact_text(eff)
                if 'ウェイト状態のメンバーが持つ' in ec:
                    continue
                key = f"{pos}:{canon}:yell_body:{ai}:{ci_idx}"
                once_per_turn = bool(flags.get('once_per_turn'))
                if once_per_turn and int((getattr(gs, 'used_this_turn', {}) or {}).get(key, 0) or 0) >= 1:
                    continue
                m_icons = re.search(r'ライブ終了時まで、?(?P<icons>(?:<\([^)]+\)>)+)を得る。?', ec)

                # reroll/extra-yell family: move revealed cards to green, then perform additional yell.
                # PL!S-bp2-004: no LIVE revealed -> put all revealed cards into green and yell again.
                if ('ライブカードがないとき' in ec) and ('それらのカードをすべて控え室に置いてもよい' in ec) and ('もう一度エール' in ec):
                    cur_revealed = list(revealed or [])
                    cur_live_n = sum(1 for _cn in cur_revealed if _is_live_ci(_get_card(cards_db, _cn)))
                    if cur_revealed and cur_live_n == 0:
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"ライブなし公開{len(cur_revealed)}枚 → 全て控え室に置き、再エール",
                            'confirm_move_all_current_yell_to_green_then_extra_yell',
                            candidates=list(cur_revealed), extra_count=int(len(cur_revealed)),
                            detail=f"no LIVE in current yell; move all {len(cur_revealed)} then extra yell {len(cur_revealed)}",
                        )
                    continue

                # PL!S-bp3-020: if current yell revealed 1+ cards and blade-heart cards are 2 or fewer,
                # optionally move all current revealed cards to green and perform the same number of extra yell.
                if ('エールにより自分のカードを1枚以上公開したとき' in ec) and ('ブレードハートを持つカードが2枚以下の場合' in ec) and ('それらのカードをすべて控え室に置いてもよい' in ec) and ('もう一度エール' in ec):
                    cur_revealed = list(revealed or [])
                    cur_bh_n = 0
                    for _cn in cur_revealed:
                        _ci = _get_card(cards_db, _cn)
                        if _ci and _ci_has_blade_heart_payload(_ci):
                            cur_bh_n += 1
                    if cur_revealed and cur_bh_n <= 2:
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"ブレードハート持ち公開{cur_bh_n}枚/2以下 → 全て控え室に置き、再エール",
                            'confirm_move_all_current_yell_to_green_then_extra_yell',
                            candidates=list(cur_revealed), extra_count=int(len(cur_revealed)),
                            detail=f"blade-heart revealed cards={cur_bh_n}/2; move all {len(cur_revealed)} then extra yell {len(cur_revealed)}",
                        )
                    continue

                # PL!HS-bp6-027: no blade-heart 『蓮ノ空』 cards, up to 3 -> extra yell equal to moved count.
                if ('ブレードハートを持たない' in ec) and ('3枚まで控え室に置いてもよい' in ec) and ('等しい枚数のエールを追加' in ec):
                    m_group = re.search(r"ブレードハートを持たない『(?P<group>[^』]+)』のカード", ec)
                    group = str(m_group.group('group') or '').strip() if m_group else ''
                    cands = _yell_revealed_no_bladeheart_candidates(gs, cards_db, revealed, group=group, member_only=False)
                    if cands:
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"ブレードハートなし『{group}』公開カードを最大3枚控え室→同数追加エール",
                            'choose_yell_revealed_to_green_then_extra_yell',
                            candidates=list(cands), max_picks=3, extra_mode='count',
                            detail=f"no-blade-heart {group} candidates={len(cands)}; max 3",
                        )
                    continue

                # PL!S-bp6-021: no blade-heart 『Aqours』 MEMBER up to 1 -> extra yell by cost//5, cap 4.
                if ('ブレードハートを持たない' in ec) and ('メンバーカードを1枚まで控え室に置いてもよい' in ec) and ('コスト5につき' in ec) and ('追加で' in ec) and ('エール' in ec):
                    m_group = re.search(r"ブレードハートを持たない『(?P<group>[^』]+)』のメンバーカード", ec)
                    group = str(m_group.group('group') or '').strip() if m_group else ''
                    cands = _yell_revealed_no_bladeheart_candidates(gs, cards_db, revealed, group=group, member_only=True)
                    if cands:
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"ブレードハートなし『{group}』メンバー1枚を控え室→コスト5につき追加エール",
                            'choose_yell_revealed_to_green_then_extra_yell',
                            candidates=list(cands), max_picks=1, extra_mode='cost_div5_cap4',
                            detail=f"no-blade-heart {group} MEMBER candidates={len(cands)}; extra by cost//5 cap4",
                        )
                    continue

                # no-blade-heart group MEMBER count -> live total score bonus per N, capped.
                # Example: PL!SP-pb2-008 若菜四季.
                if ('ブレードハートを持たない' in ec) and ('メンバーカード' in ec) and ('枚につき' in ec) and ('ライブの合計スコアを+' in ec) and ('までしか増えない' in ec):
                    m_sc = re.search(r"ブレードハートを持たない『(?P<group>[^』]+)』のメンバーカード(?P<per>\d+)枚につき、?ライブの合計スコアを\+(?P<delta>\d+)する。この能力では合計スコアは(?P<cap>\d+)までしか増えない", ec)
                    if m_sc:
                        group = str(m_sc.group('group') or '').strip()
                        per = max(1, int(m_sc.group('per') or 1))
                        delta = int(m_sc.group('delta') or 0)
                        cap = int(m_sc.group('cap') or 0)
                        cands = _yell_revealed_no_bladeheart_candidates(gs, cards_db, revealed, group=group, member_only=True)
                        got = len(cands)
                        bonus = min((got // per) * delta, cap)
                        if bonus > 0:
                            _append_trigger(
                                pos, canon, key, once_per_turn,
                                f"ブレードハートなし『{group}』メンバー{got}枚 → ライブ合計スコア+{bonus}",
                                'live_total_score_bonus', score_delta=int(bonus),
                                detail=f"no-blade-heart {group} MEMBER={got}; +{delta} per {per}, cap {cap}",
                            )
                    continue

                # 自分がエールしたとき、同じグループを持つメンバーカードが3枚ある/以上 -> icons
                if ('同じグループを持つメンバーカードが3枚' in ec) and m_icons:
                    group = str(getattr(ci_src, 'group', '') or '').split('/')[0].strip()
                    got = _count_yell_revealed_group_members(gs, cards_db, group)
                    if got >= 3:
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"エール公開の同グループメンバー{got}枚 → {m_icons.group('icons')}を得る",
                            'gain_icons', icons=m_icons.group('icons'), mult=1,
                            detail=f"same-group revealed members={got}; icons={m_icons.group('icons')}",
                        )
                    continue

                # ブレードハートを持たないメンバーカードがN枚以上 -> icons
                if ('ブレードハートを持たないメンバーカードが' in ec) and m_icons:
                    m_need = re.search(r'ブレードハートを持たないメンバーカードが(?P<n>\d+)枚以上', ec)
                    need = int(m_need.group('n')) if m_need else 1
                    if no_bh_members >= need:
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"ブレードハートなしメンバー{no_bh_members}/{need}枚 → {m_icons.group('icons')}を得る",
                            'gain_icons', icons=m_icons.group('icons'), mult=1,
                            detail=f"no-blade-heart revealed members={no_bh_members}; icons={m_icons.group('icons')}",
                        )
                    continue

                # revealed <スコア+1> group live cards -> icons
                if ('スコア+1' in ec) and ('ライブカードが1枚以上' in ec) and ('ライブ終了時まで' in ec) and m_icons:
                    m_group = re.search(r'を持つ『(?P<group>[^』]+)』のライブカードが1枚以上', ec)
                    group = str(m_group.group('group') or '').strip() if m_group else ''
                    got = 0
                    for cn2 in list(getattr(gs, '_yell_revealed_this_live', []) or []):
                        ci2 = _get_card(cards_db, cn2)
                        if not ci2 or not _is_live_ci(ci2):
                            continue
                        if group and group not in str(getattr(ci2, 'group', '') or ''):
                            continue
                        if _ci_blade_heart_has_tag(ci2, '<スコア+1>'):
                            got += 1
                    if got >= 1:
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"エール公開に<スコア+1>を持つ『{group}』ライブ{got}枚 → {m_icons.group('icons')}を得る",
                            'gain_icons', icons=m_icons.group('icons'), mult=1,
                            detail=f"revealed {group} live with score+1={got}; icons={m_icons.group('icons')}",
                        )
                    continue

                # ライブカードが1枚以上 -> icons
                if ('ライブカードが1枚以上' in ec) and ('ライブ終了時まで' in ec) and m_icons and ('手札が' not in ec):
                    if live_n >= 1:
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"エール公開にライブカード{live_n}枚 → {m_icons.group('icons')}を得る",
                            'gain_icons', icons=m_icons.group('icons'), mult=1,
                            detail=f"revealed live cards={live_n}; icons={m_icons.group('icons')}",
                        )
                    continue

                # ライブカードが1枚以上 and hand <= N -> draw 1
                if ('ライブカードが1枚以上' in ec) and ('手札が' in ec) and ('カードを1枚引く' in ec):
                    m_hand = re.search(r'手札が(?P<n>\d+)枚以下の場合、カードを1枚引く', ec)
                    hand_lim = int(m_hand.group('n')) if m_hand else 999
                    if live_n >= 1 and len(list(getattr(gs, 'hand', []) or [])) <= hand_lim:
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"エール公開にライブカード{live_n}枚かつ手札{len(list(getattr(gs, 'hand', []) or []))}/{hand_lim}枚以下 → 1ドロー",
                            'draw1', hand_lim=hand_lim,
                            detail=f"revealed live cards={live_n}; hand<={hand_lim}",
                        )
                    continue

                # revealed live cards count -> one icon per live, cap N
                if ('ライブカード1枚につき' in ec) and ('この能力では' in ec):
                    m_per = re.search(r'ライブカード1枚につき、?(?P<icon><\([^)]+\)>)を得る', ec)
                    m_cap = re.search(r'この能力では(?P<icon2><\([^)]+\)>)は(?P<n>\d+)つまで', ec)
                    if m_per and live_n > 0:
                        cap = int(m_cap.group('n')) if m_cap else live_n
                        mult = min(int(live_n), int(cap))
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"エール公開ライブ{live_n}枚ぶん（上限{cap}）→ {m_per.group('icon')}×{mult}を得る",
                            'gain_icons', icons=m_per.group('icon'), mult=mult,
                            detail=f"revealed live cards={live_n}; per-live icon={m_per.group('icon')} x{mult}",
                        )
                    continue

                # no revealed blade-heart card -> icons
                if ('ブレードハートを持つカードがないとき' in ec) and m_icons:
                    if no_bh_cards == len(list(revealed or [])):
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"ブレードハート持ち公開カードなし → {m_icons.group('icons')}を得る",
                            'gain_icons', icons=m_icons.group('icons'), mult=1,
                            detail=f"no revealed blade-heart cards; icons={m_icons.group('icons')}",
                        )
                    continue

                # blade-heart kind count thresholds -> heart and optional score
                if ('ブレードハートの中に' in ec) and ('3種類以上' in ec) and m_icons:
                    if bh_kind_n >= 3:
                        score_delta = 1 if (bh_kind_n >= 6 and 'ライブの合計スコアを+1する' in ec) else 0
                        _append_trigger(
                            pos, canon, key, once_per_turn,
                            f"ブレードハート種類数{bh_kind_n} → {m_icons.group('icons')}を得る" + ("、スコア+1" if score_delta else ""),
                            'gain_icons', icons=m_icons.group('icons'), mult=1, score_delta=score_delta,
                            detail=f"blade-heart kinds={bh_kind_n}; icons={m_icons.group('icons')}" + ("; score+1" if score_delta else ""),
                        )
                    continue
    return triggers


def _apply_yell_revealed_body_auto_trigger(gs: GameState, rng: random.Random, cards_db: Dict[str, CardInfo], trig: Dict[str, Any]) -> bool:
    """Resolve one queued yell-revealed BODY auto trigger."""
    pos = str((trig or {}).get('pos', '') or '').upper()
    src = str((trig or {}).get('source_cn', '') or '').strip()
    usage_key = str((trig or {}).get('usage_key', '') or '').strip()
    once_per_turn = bool((trig or {}).get('once_per_turn', False))
    if once_per_turn and usage_key and int((getattr(gs, 'used_this_turn', {}) or {}).get(usage_key, 0) or 0) >= 1:
        gs.log.append(f"[INFO] YELL AUTO: {src or '?'} already used this turn")
        return False
    effect_kind = str((trig or {}).get('effect_kind', '') or '')
    detail = str((trig or {}).get('detail', '') or '')
    ok = False
    if effect_kind == 'draw1':
        drew = draw(gs, 1, rng)
        detail = (detail + f" -> drew {drew}").strip()
        ok = True
    elif effect_kind == 'confirm_move_all_current_yell_to_green_then_extra_yell':
        cands = [str(x) for x in list((trig or {}).get('candidates', []) or []) if str(x or '').strip()]
        extra_count = int((trig or {}).get('extra_count', len(cands)) or 0)
        if not cands:
            gs.log.append(f"[SKIP] YELL AUTO: {src or '?'} no revealed cards to reroll")
            return False
        gs.pending.append({
            'kind': 'confirm_yell_revealed_all_to_green_then_extra_yell',
            'source_cn': src,
            'usage_key': usage_key,
            'once_per_turn': once_per_turn,
            'text': f'{src}[エール時] エール公開カードにライブカードがないため、公開カード{len(cands)}枚をすべて控え室に置いて、{extra_count}枚の追加エールを行いますか？',
            'options': ['pay', 'skip'],
            'display_cards': list(cands),
            'candidates': list(cands),
            'extra_count': int(extra_count),
        })
        gs.log.append(f"[PENDING] YELL AUTO: {src or '?'} reroll yell confirm candidates={len(cands)} extra={extra_count}")
        return True
    elif effect_kind == 'choose_yell_revealed_to_green_then_extra_yell':
        cands = [str(x) for x in list((trig or {}).get('candidates', []) or []) if str(x or '').strip()]
        max_picks = max(0, int((trig or {}).get('max_picks', 1) or 1))
        extra_mode = str((trig or {}).get('extra_mode', 'count') or 'count')
        if not cands or max_picks <= 0:
            gs.log.append(f"[SKIP] YELL AUTO: {src or '?'} no candidates for additional yell")
            return False
        gs.pending.append({
            'kind': 'choose_yell_revealed_to_green_then_extra_yell',
            'source_cn': src,
            'usage_key': usage_key,
            'once_per_turn': once_per_turn,
            'text': f'{src}[エール時] エール公開カードから控え室に置くカードを選んでください（最大{max_picks}枚、スキップ可）。選んだ内容に応じて追加エールを行います。',
            'options': list(cands),
            'display_cards': list(cands),
            'candidates': list(cands),
            'max_picks': int(max_picks),
            'optional': True,
            'picked': [],
            'extra_mode': extra_mode,
        })
        gs.log.append(f"[PENDING] YELL AUTO: {src or '?'} choose revealed cards for extra yell max={max_picks} candidates={len(cands)} mode={extra_mode}")
        return True
    elif effect_kind == 'live_total_score_bonus':
        bonus = int((trig or {}).get('score_delta', 0) or 0)
        if bonus <= 0:
            gs.log.append(f"[SKIP] YELL AUTO: {src or '?'} live total score bonus is 0")
            return False
        slot = (gs.stage or {}).get(pos) if pos in ('L', 'C', 'R') else None
        if slot and getattr(slot, 'cardnumber', ''):
            try:
                slot.temp_score = int(getattr(slot, 'temp_score', 0) or 0) + int(bonus)
                slot.temp_until = 'end_of_live'
            except Exception:
                pass
            detail = (detail + f"; live total score +{bonus}").strip()
            ok = True
        else:
            # LIVE-card source fallback: tie the bonus to the first current live if available.
            lives = list(getattr(gs, 'set_zone', []) or [])
            target_live = lives[0] if lives else ''
            if target_live:
                _add_live_start_score_bonus(gs, bonus, source_cn=target_live)
                detail = (detail + f"; live total score +{bonus} for {target_live}").strip()
                ok = True
            else:
                gs.log.append(f"[WARN] YELL AUTO: no source slot/current live for score bonus {src or '?'}")
                return False
    elif effect_kind == 'gain_icons':
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'cardnumber', ''):
            gs.log.append(f"[WARN] YELL AUTO: source slot {pos or '?'} is empty for {src or '?'}")
            return False
        if src and _canon_cardno(getattr(slot, 'cardnumber', '') or '') != _canon_cardno(src):
            gs.log.append(f"[WARN] YELL AUTO: source card moved before resolution ({src} not at {pos})")
            return False
        icons = str((trig or {}).get('icons', '') or '')
        mult = int((trig or {}).get('mult', 1) or 1)
        b, hs = _grant_temp_icons_to_slot(slot, icons, mult)
        score_delta = int((trig or {}).get('score_delta', 0) or 0)
        if score_delta:
            try:
                slot.temp_score = int(getattr(slot, 'temp_score', 0) or 0) + int(score_delta)
                slot.temp_until = 'end_of_live'
            except Exception:
                pass
        detail = (detail + f"; applied blades={b} hearts={hs}" + (f" score+{score_delta}" if score_delta else '')).strip()
        ok = True
    else:
        gs.log.append(f"[ERR] YELL AUTO: unsupported effect_kind={effect_kind}")
        return False
    if ok and once_per_turn and usage_key:
        try:
            gs.used_this_turn[usage_key] = 1
        except Exception:
            gs.used_this_turn = {usage_key: 1}
    gs.log.append(f"[AUTO] YELL: {src or '?'}({pos or '?'}) {detail}")
    return bool(ok)


def _enqueue_yell_revealed_body_auto_triggers(gs: GameState, cards_db: Dict[str, CardInfo], revealed: Optional[List[str]] = None) -> int:
    cur_revealed = list(revealed if revealed is not None else (getattr(gs, '_yell_revealed_this_live', []) or []))
    triggers = _collect_yell_revealed_body_auto_triggers(gs, cards_db, cur_revealed)
    if not triggers:
        return 0
    opts = [_auto_trigger_option_text(t) for t in triggers]
    auto_prompt = {
        'kind': 'auto_order',
        'text': 'エール時の自動効果が発生：解決するカードを選択（1つずつ）',
        'options': opts,
        'queue': list(triggers),
    }
    if cur_revealed:
        gs.pending.append({
            'kind': 'show_revealed_cards_ack',
            'label': 'エール公開カード確認',
            'text': 'エールで公開されたカードを確認してから、エール時自動効果を解決します。',
            'display_cards': list(cur_revealed),
            'options': ['ok'],
            '_resume': auto_prompt,
        })
    else:
        gs.pending.append(auto_prompt)
    gs.log.append(f"[PROMPT] yell-revealed auto abilities queued: {len(triggers)}")
    return int(len(triggers))


def _run_yell_revealed_body_auto_triggers(gs: GameState, rng: random.Random, cards_db: Dict[str, CardInfo], revealed: Optional[List[str]] = None) -> int:
    """Backward-compatible name. Queue triggers instead of silently resolving them."""
    return _enqueue_yell_revealed_body_auto_triggers(gs, cards_db, revealed)

def _add_last_attempt_live_score_bonus(gs: GameState, cn_live, bonus: int) -> None:
    canon = _canon_cardno(cn_live)
    lives = list(getattr(gs, 'last_attempt_lives', []) or [])
    bonuses = list(getattr(gs, 'last_attempt_score_bonus', []) or [])
    while len(bonuses) < len(lives):
        bonuses.append(0)
    for i, x in enumerate(lives):
        if _canon_cardno(x) == canon:
            bonuses[i] = int(bonuses[i] or 0) + int(bonus or 0)
            gs.last_attempt_score_bonus = bonuses
            return

def _last_attempt_live_attempt_score(gs: GameState, cn_live: str, cards_db: Dict[str, CardInfo]) -> int:
    canon = _canon_cardno(cn_live)
    lives = list(getattr(gs, 'last_attempt_lives', []) or [])
    rows = list(getattr(gs, 'last_attempt_score_rows', []) or [])
    for i, x in enumerate(lives):
        if _canon_cardno(x) == canon:
            try:
                row = rows[i] if i < len(rows) else {}
                return int((row or {}).get('score', 0) or 0)
            except Exception:
                break
    ci = _get_card(cards_db, cn_live)
    try:
        return int(getattr(ci, 'score', 0) or 0) if ci else 0
    except Exception:
        return 0

def _get_last_attempt_live_score_set(gs: GameState, cn_live: str) -> Optional[int]:
    canon = _canon_cardno(cn_live)
    lives = list(getattr(gs, 'last_attempt_lives', []) or [])
    sets = list(getattr(gs, 'last_attempt_score_set', []) or [])
    while len(sets) < len(lives):
        sets.append(None)
    for i, x in enumerate(lives):
        if _canon_cardno(x) == canon:
            v = sets[i] if i < len(sets) else None
            try:
                return None if v is None else int(v)
            except Exception:
                return None
    return None

def _set_last_attempt_live_score_set(gs: GameState, cn_live: str, target_score: int) -> None:
    canon = _canon_cardno(cn_live)
    lives = list(getattr(gs, 'last_attempt_lives', []) or [])
    bonuses = list(getattr(gs, 'last_attempt_score_bonus', []) or [])
    sets = list(getattr(gs, 'last_attempt_score_set', []) or [])
    while len(bonuses) < len(lives):
        bonuses.append(0)
    while len(sets) < len(lives):
        sets.append(None)
    for i, x in enumerate(lives):
        if _canon_cardno(x) == canon:
            sets[i] = int(target_score or 0)
            # A direct 「スコアはNになる」 resolution overwrites score changes that
            # resolved before it. Later +N effects can still add to this set score.
            bonuses[i] = 0
            gs.last_attempt_score_set = sets
            gs.last_attempt_score_bonus = bonuses
            return

def _last_attempt_live_current_success_score(gs: GameState, cards_db: Dict[str, CardInfo], cn_live: str) -> int:
    base = int(_last_attempt_live_attempt_score(gs, cn_live, cards_db) or 0)
    set_v = _get_last_attempt_live_score_set(gs, cn_live)
    bonus = int(_get_last_attempt_live_score_bonus(gs, cn_live) or 0)
    return int((base if set_v is None else int(set_v)) + bonus)

def _set_live_success_score_to(gs: GameState, cards_db: Dict[str, CardInfo], cn_live: str, target_score: int, detail: str = '') -> None:
    """Apply 「このカードのスコアはNになる」 as a direct set value.

    This keeps the runtime state aligned with the card text rather than encoding
    the result as a negative/positive delta. Score +N effects that resolve later
    may still add to this set score; score +N effects that resolved earlier are
    overwritten by the set.
    """
    try:
        target = int(target_score or 0)
    except Exception:
        target = 0
    current_score = int(_last_attempt_live_current_success_score(gs, cards_db, cn_live) or 0)
    _set_last_attempt_live_score_set(gs, cn_live, target)
    prefix = f"[AUTO] LIVE: {cn_live}[ライブ成功時]"
    if detail:
        gs.log.append(f"{prefix}: {detail} -> score set to {target} ({current_score}->{target})")
    else:
        gs.log.append(f"{prefix}: score set to {target} ({current_score}->{target})")

def _add_live_success_score_bonus(gs: GameState, cn_live: str, bonus: int, detail: str = '') -> None:
    try:
        bonus_i = int(bonus or 0)
    except Exception:
        bonus_i = 0
    if bonus_i > 0:
        _add_last_attempt_live_score_bonus(gs, cn_live, bonus_i)
        if detail:
            gs.log.append(f"[AUTO] LIVE: {cn_live}[ライブ成功時]: {detail} -> score +{bonus_i}")
        else:
            gs.log.append(f"[AUTO] LIVE: {cn_live}[ライブ成功時]: score +{bonus_i}")
    else:
        if detail:
            gs.log.append(f"[AUTO] LIVE: {cn_live}[ライブ成功時]: {detail} -> score +0")
        else:
            gs.log.append(f"[AUTO] LIVE: {cn_live}[ライブ成功時]: score +0")
def _last_attempt_total_before_total_bonus(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    lives = list(getattr(gs, 'last_attempt_lives', []) or [])
    bonuses = list(getattr(gs, 'last_attempt_score_bonus', []) or [])
    sets = list(getattr(gs, 'last_attempt_score_set', []) or [])
    base_rows = [dict(x) for x in list(getattr(gs, 'last_attempt_score_rows', []) or [])]
    while len(bonuses) < len(lives):
        bonuses.append(0)
    while len(sets) < len(lives):
        sets.append(None)
    total = 0
    for i, cn in enumerate(lives):
        row0 = base_rows[i] if i < len(base_rows) else {}
        ci = _get_card(cards_db, cn)
        attempt_eff = int(row0.get('score', getattr(ci, 'score', 0) or 0) or 0)
        set_v = sets[i] if i < len(sets) else None
        try:
            base_eff = attempt_eff if set_v is None else int(set_v)
        except Exception:
            base_eff = attempt_eff
        total += int(base_eff + int(bonuses[i] or 0))
    try:
        for pos, slot in (gs.stage or {}).items():
            if slot:
                total += int(_slot_always_score_bonus(gs, cards_db, pos, slot) or 0)
    except Exception:
        pass
    return int(total)

def _add_live_success_total_score_bonus(gs: GameState, cards_db: Dict[str, CardInfo], delta: int, min_total: Optional[int] = None, detail: str = '', source_cn: str = '', pos: str = '') -> None:
    try:
        delta_i = int(delta or 0)
    except Exception:
        delta_i = 0
    current_total = int(_last_attempt_total_before_total_bonus(gs, cards_db) + int(getattr(gs, 'last_attempt_total_score_bonus', 0) or 0))
    applied = delta_i
    if min_total is not None and current_total + applied < int(min_total):
        applied = int(min_total) - current_total
    gs.last_attempt_total_score_bonus = int(getattr(gs, 'last_attempt_total_score_bonus', 0) or 0) + int(applied)
    prefix = f"[AUTO] {pos}: {source_cn}[ライブ成功時]" if pos else f"[AUTO] {source_cn}[ライブ成功時]"
    if detail:
        gs.log.append(f"{prefix}: {detail} (applied {applied:+d}, total {current_total}->{current_total + applied})")
    else:
        gs.log.append(f"{prefix}: live total score {applied:+d} (total {current_total}->{current_total + applied})")

def _get_last_attempt_live_score_bonus(gs: GameState, cn_live) -> int:
    canon = _canon_cardno(cn_live)
    lives = list(getattr(gs, 'last_attempt_lives', []) or [])
    bonuses = list(getattr(gs, 'last_attempt_score_bonus', []) or [])
    while len(bonuses) < len(lives):
        bonuses.append(0)
    for i, x in enumerate(lives):
        if _canon_cardno(x) == canon:
            try:
                return int(bonuses[i] or 0)
            except Exception:
                return 0
    return 0
def _compute_final_compare_score_after_success(gs: GameState, cards_db: Dict[str, CardInfo]) -> tuple[int, list[tuple[str, int, int, int, Optional[int]]], int, int, int]:
    lives = list(getattr(gs, 'last_attempt_lives', []) or [])
    bonuses = list(getattr(gs, 'last_attempt_score_bonus', []) or [])
    sets = list(getattr(gs, 'last_attempt_score_set', []) or [])
    base_rows = [dict(x) for x in list(getattr(gs, 'last_attempt_score_rows', []) or [])]
    while len(bonuses) < len(lives):
        bonuses.append(0)
    while len(sets) < len(lives):
        sets.append(None)
    rows = []
    total = 0
    for i, cn in enumerate(lives):
        row0 = base_rows[i] if i < len(base_rows) else {}
        ci = _get_card(cards_db, cn)
        attempt_eff = int(row0.get('score', getattr(ci, 'score', 0) or 0) or 0)
        success_delta = int(bonuses[i] or 0) if i < len(bonuses) else 0
        set_v_raw = sets[i] if i < len(sets) else None
        try:
            set_v: Optional[int] = None if set_v_raw is None else int(set_v_raw)
        except Exception:
            set_v = None
        base_for_success = attempt_eff if set_v is None else int(set_v)
        eff_s = int(base_for_success + success_delta)
        rows.append((cn, attempt_eff, success_delta, eff_s, set_v))
        total += eff_s
    stage_score_bonus = 0
    try:
        for pos, slot in (gs.stage or {}).items():
            if not slot:
                continue
            stage_score_bonus += int(_slot_always_score_bonus(gs, cards_db, pos, slot) or 0)
    except Exception:
        stage_score_bonus = 0
    total_score_bonus = int(getattr(gs, 'last_attempt_total_score_bonus', 0) or 0)
    yell_score_icon_bonus = int(_yell_revealed_score_icon_bonus(gs, cards_db) or 0)
    total += int(stage_score_bonus) + int(total_score_bonus) + int(yell_score_icon_bonus)
    return int(total), rows, int(stage_score_bonus), int(total_score_bonus), int(yell_score_icon_bonus)
def cmd_attempt(gs: GameState, cards_db: Dict[str, CardInfo]) -> None:
    if bool(getattr(gs, "cannot_live_until_end_of_live", False)):
        gs.log.append("[ATTEMPT] blocked: you cannot live until end of live")
        gs.last_attempt_excess_hearts = {}
        gs.live_start_score_bonus_by_set_idx = {}
        gs.live_start_required_any_reduction_by_set_idx = {}
        gs.live_start_required_any_increase_by_set_idx = {}
        gs.vivid_world_blue_mode_this_live = False
        gs.vivid_world_bonus_this_live = 0
        gs.last_attempt_lives = []
        gs.last_attempt_score_bonus = []
        gs.last_attempt_score_set = []
        gs.last_attempt_total_score_bonus = 0
        gs.last_attempt_score_rows = []
        gs.last_attempt_attempt_score = 0
        gs.last_attempt_final_score = 0
        gs.last_attempt_attempt_score = 0
        gs.last_attempt_final_score = 0
        gs.last_attempt_ok = False
        gs.need_live_success_triggers = False
        gs.need_success_store_choice = False
        return
    if not gs.set_zone:
        gs.last_attempt_excess_hearts = {}
        gs.live_start_score_bonus_by_set_idx = {}
        gs.live_start_required_any_reduction_by_set_idx = {}
        gs.live_start_required_any_increase_by_set_idx = {}
        gs.vivid_world_blue_mode_this_live = False
        gs.vivid_world_bonus_this_live = 0
        gs.log.append("[ATTEMPT] no set cards")
        # clear end-of-live state defensively
        gs.last_attempt_lives = []
        gs.last_attempt_score_bonus = []
        gs.last_attempt_score_set = []
        gs.last_attempt_total_score_bonus = 0
        gs.last_attempt_score_rows = []
        gs.last_attempt_attempt_score = 0
        gs.last_attempt_final_score = 0
        gs.last_attempt_attempt_score = 0
        gs.last_attempt_final_score = 0
        gs.last_attempt_ok = False
        gs.need_live_success_triggers = False
        gs.need_success_store_choice = False
        _clear_end_of_live_buffs(gs, cards_db)
        gs.live_start_prompted = False
        return
    if gs.pending:
        gs.log.append("[WARN] attempt: pending prompts exist; resolve them first.")
        return
    if _enqueue_live_start_prompts(gs, cards_db) > 0:
        gs.log.append("[INFO] attempt: resolve live-start prompts, then click Attempt again.")
        return
    lives = []
    live_idxs = []
    nonlives = []
    for _set_idx, cn in enumerate(gs.set_zone):
        c = _get_card(cards_db, cn)
        if c and is_live_type(c.type):
            lives.append(cn)
            live_idxs.append(int(_set_idx))
        else:
            nonlives.append(cn)
    if nonlives:
        gs.green_room.extend(nonlives)
    base = owned_base_hearts(gs, cards_db)
    cheer = cheer_hearts_from_resolve(gs, cards_db)
    owned = dict(base)
    for k, v in cheer.items():
        owned[k] = owned.get(k, 0) + int(v)
    gs.log.append(f"[ATTEMPT] LIVE={len(lives)} base={base} cheer={cheer} owned={owned}")
    globals()['_CURRENT_GS_FOR_ATTEMPT'] = gs
    ok_all, alloc_map = _solve_multi_live_allocations(lives, cards_db, owned, live_set_indices=live_idxs)
    globals()['_CURRENT_GS_FOR_ATTEMPT'] = None
    if ok_all:
        try:
            _excess_pool = {str(k).lower(): int(v or 0) for k, v in (owned or {}).items()}
            for _cn0 in lives:
                _apply_alloc_to_pool(alloc_map.get(_cn0, {}) or {}, _excess_pool)
            gs.last_attempt_excess_hearts = dict(_excess_pool)
        except Exception:
            gs.last_attempt_excess_hearts = {}
        for _j, cn in enumerate(lives):
            c = _get_card(cards_db, cn)
            _set_idx = live_idxs[_j] if _j < len(live_idxs) else None
            req = _effective_live_required_hearts(cn, c, gs, cards_db, set_idx=_set_idx)
            alloc = alloc_map.get(cn, {}) or {}
            gs.log.append(f"  live: OK {cn} req={req} alloc={alloc}")
    else:
        gs.last_attempt_excess_hearts = {}
        # Failure trace (deterministic): consume hearts in current LIVE list order using the same reduction rule (8.3.15.1.2).
        pool_trace: Dict[str, int] = {str(k).lower(): int(v or 0) for k, v in (owned or {}).items()}
        pool_trace.setdefault("all", 0)
        failed_at = None
        for _j, cn in enumerate(lives):
            c = _get_card(cards_db, cn)
            _set_idx = live_idxs[_j] if _j < len(live_idxs) else None
            req = _effective_live_required_hearts(cn, c, gs, cards_db, set_idx=_set_idx)
            ok, alloc = can_satisfy_req(req, pool_trace)
            gs.log.append(f"  live: {'OK' if ok else 'NG'} {cn} req={req} alloc={alloc}")
            if ok:
                _apply_alloc_to_pool(alloc, pool_trace)
            else:
                failed_at = cn
                break
        # Mark remaining lives (if any) as not attempted in trace
        if failed_at is not None:
            seen_fail = False
            for _j, cn in enumerate(lives):
                if cn == failed_at:
                    seen_fail = True
                    continue
                if seen_fail:
                    c = _get_card(cards_db, cn)
                    _set_idx = live_idxs[_j] if _j < len(live_idxs) else None
                    req = _effective_live_required_hearts(cn, c, gs, cards_db, set_idx=_set_idx)
                    gs.log.append(f"  live: NG {cn} req={req} alloc={{'reason': 'not reached'}}")
    # Result & UI banner
    if ok_all:
        total_score, score_rows = _compute_attempt_score_breakdown(lives, cards_db, int(getattr(gs, 'turn', 0) or 0), gs, live_set_indices=live_idxs)
        stage_score_bonus = 0
        try:
            for pos, slot in (gs.stage or {}).items():
                if not slot:
                    continue
                stage_score_bonus += int(_slot_always_score_bonus(gs, cards_db, pos, slot) or 0)
        except Exception:
            stage_score_bonus = 0
        for r in score_rows:
            cn = r.get('cn', '')
            base_s = int(r.get('base', 0) or 0)
            delta_s = int(r.get('delta', 0) or 0)
            eff_s = int(r.get('score', 0) or 0)
            if delta_s:
                gs.log.append(f"  score: {cn} = {eff_s} ({base_s}+{delta_s})")
            else:
                gs.log.append(f"  score: {cn} = {eff_s}")
        if stage_score_bonus:
            gs.log.append(f"  score: stage always bonus = +{stage_score_bonus}")
            total_score += int(stage_score_bonus)
        yell_score_icon_bonus = int(_yell_revealed_score_icon_bonus(gs, cards_db) or 0)
        if yell_score_icon_bonus:
            gs.log.append(f"  score: yell score icons = +{yell_score_icon_bonus}")
            total_score += int(yell_score_icon_bonus)
        gs.log.append(f"[ATTEMPT] result=SUCCESS total_score={total_score}")
        gs.last_attempt_score_rows = [dict(r) for r in list(score_rows or [])]
        gs.last_attempt_attempt_score = int(total_score)
        gs.last_attempt_final_score = int(total_score)
        result_txt = f"SUCCESS (Attempt Score {total_score})"
    else:
        gs.log.append("[ATTEMPT] result=FAIL")
        result_txt = "FAIL"
    # UI banner (transient)
    gs.banner_text = result_txt
    gs.banner_ts = time.time()
    gs.banner_ttl = 4.0
    # Keep attempted LIVE cards in the live card storage until LIVE_RESOLVE.
    # Rules timing: after compare, the winner first moves one card from the live card
    # storage to success storage (8.4.7), then cards remaining in the live card storage
    # move to the waiting room (8.4.8). Do not move them to waiting room here.
    if lives:
        gs.set_zone = list(lives)
        if ok_all:
            gs.log.append(f"[ZONE] live storage holds {len(lives)} successful LIVE(s) until LIVE_RESOLVE")
            gs.last_attempt_lives = list(lives)
            gs.last_attempt_score_bonus = [0 for _ in range(len(lives))]
            gs.last_attempt_score_set = [None for _ in range(len(lives))]
            gs.last_attempt_total_score_bonus = 0
            gs.last_attempt_ok = True
            gs.need_live_success_triggers = True
            gs.need_success_store_choice = True
        else:
            gs.log.append(f"[ZONE] live storage holds {len(lives)} failed LIVE(s) until cleanup")
            gs.last_attempt_lives = []
            gs.last_attempt_score_bonus = []
            gs.last_attempt_score_set = []
            gs.last_attempt_total_score_bonus = 0
            gs.last_attempt_attempt_score = 0
            gs.last_attempt_final_score = 0
            gs.last_attempt_ok = False
            gs.need_live_success_triggers = False
            gs.need_success_store_choice = False
    else:
        gs.set_zone = []
        gs.last_attempt_lives = []
        gs.last_attempt_score_bonus = []
        gs.last_attempt_score_set = []
        gs.last_attempt_total_score_bonus = 0
        gs.last_attempt_score_rows = []
        gs.last_attempt_attempt_score = 0
        gs.last_attempt_final_score = 0
        gs.last_attempt_ok = False
        gs.need_live_success_triggers = False
        gs.need_success_store_choice = False
        _clear_end_of_live_buffs(gs, cards_db)
        gs.live_start_prompted = False
def cmd_ack(gs: GameState, rng: Optional[random.Random] = None) -> None:
    if not gs.resolve_zone:
        gs.log.append("[ACK] resolve zone empty")
        return
    n = len(gs.resolve_zone)
    gs.green_room.extend(gs.resolve_zone)
    gs.resolve_zone = []
    gs.log.append(f"[ACK] moved {n} revealed cards -> green room")
    _rule_refresh_main_deck(gs, rng, reason='ack')
def cmd_toggle_stage_active(gs: GameState, cards_db: Dict[str, CardInfo], pos: str) -> None:
    pos = str(pos or '').upper()
    if pos not in ('L', 'C', 'R'):
        gs.log.append(f"[ERR] toggle_stage_active: invalid pos={pos}")
        return
    slot = (gs.stage or {}).get(pos)
    if not slot or not getattr(slot, 'cardnumber', ''):
        gs.log.append(f"[ERR] toggle_stage_active: empty stage {pos}")
        return
    ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
    if ci and _is_live_ci(ci):
        gs.log.append(f"[ERR] toggle_stage_active: not a member at {pos}")
        return
    slot.active = (not bool(getattr(slot, 'active', False)))
    state = 'ACTIVE' if bool(slot.active) else 'WAIT'
    gs.log.append(f"[STATE] {pos} -> {state} ({getattr(slot, 'cardnumber', '')})")
def cmd_activate_to_green(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, rng: Optional[random.Random] = None) -> None:
    # Activate ability on stage member at pos.
    pos = str(pos or "").upper()
    if pos not in ("L", "C", "R"):
        gs.log.append("[ERR] activate: pos must be L/C/R")
        return
    slot = gs.stage.get(pos)
    if not slot:
        gs.log.append(f"[ERR] activate: empty stage {pos}")
        return
    ci = _get_card(cards_db, slot.cardnumber)
    if not ci:
        gs.log.append(f"[ERR] activate: card not in DB: {slot.cardnumber}")
        return
    if rng is None:
        rng = random.Random(gs.seed)
    # 1) Generic activated abilities（BODY起動効果もこのループ内で処理）
    for ab in _iter_activated_abilities(ci):
        flags = _ability_usage_flags(ab if isinstance(ab, dict) else {})
        akey = _ability_key(ci, ab if isinstance(ab, dict) else {}, pos)
        if flags.get('turn_only') is not None and int(gs.turn or 0) != int(flags['turn_only']):
            continue
        if flags.get('once_per_turn'):
            used = int((getattr(gs, 'used_this_turn', {}) or {}).get(akey, 0) or 0)
            if used >= 1:
                gs.log.append(f"[INFO] activate: already used this turn ({akey})")
                return
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list) or not clauses:
            continue
        gs.log.append(f"[ACT] {pos}: {ci.cardnumber} activated")
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            cost = str(cl.get('cost_template', '') or '')
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            cond_thr = int(_activated_success_score_sum_condition(eff) or 0)
            if cond_thr:
                got_sum = int(_own_success_zone_score_sum(gs, cards_db) or 0)
                if got_sum < cond_thr:
                    gs.log.append(f"[ERR] activate: success-zone score sum condition not met ({got_sum}/{cond_thr})")
                    return
                eff = _strip_activated_success_score_sum_condition(eff)
            success_count_for_cost = len(list(getattr(gs, 'success_zone', []) or []))
            discard_success_reduction = int(_activated_success_count_discard_cost_reduction(eff, success_count_for_cost) or 0)
            if discard_success_reduction > 0:
                eff = _strip_activated_success_count_discard_cost_reduction(eff)

            # コストのみのclause（effect_templateが空）も処理する
            # 例：「このメンバーをウェイトにする：カードを1枚引き、手札を1枚控え室に置く。」
            # の場合、cost_template="このメンバーをウェイトにする" / effect_template="" のclauseが
            # 先に来ることがあるため、コストだけ適用してcontinueする
            if not eff:
                # effが空でもコスト（self-wait）だけ処理してcontinue
                if _cost_requires_self_wait(cost) and not _cost_requires_self_to_green(cost):
                    if slot and slot.active:
                        slot.active = False
                        gs.log.append(f"[COST] {pos}: {getattr(slot,'cardnumber','?')} -> WAIT (self-wait cost, eff-empty clause)")
                continue
            # Cost: choose another on-stage group member to set WAIT
            wait_other = _cost_requires_other_group_member_wait(cost)
            if wait_other:
                group_name = str(wait_other.get('group') or '')
                total_need = int(wait_other.get('count') or 0)
                cands = _other_group_member_wait_candidates(gs, cards_db, pos, group_name)
                if len(cands) < total_need:
                    gs.log.append(f"[INFO] activate: ウェイトにできる『{group_name}』メンバーがいない")
                    return
                if flags.get('once_per_turn'):
                    try:
                        gs.used_this_turn[akey] = 1
                    except Exception:
                        try:
                            gs.used_this_turn = {akey: 1}
                        except Exception:
                            pass
                opts = [_stage_pos_label(gs, cards_db, pp) for pp in cands]
                gs.pending.append({
                    'kind': 'choose_stage_member_to_wait',
                    'text': f"【起動効果】ウェイトにする『{group_name}』メンバーを選んでください",
                    'options': list(opts),
                    'pos_options': list(cands),
                    'remaining': total_need,
                    'after_effect_template': eff,
                    'after_ctx': {'pos': pos, 'source_cn': ci.cardnumber},
                    'after_source_cn': ci.cardnumber,
                })
                gs.log.append(f"[PENDING] activate choose_stage_member_to_wait n={total_need} then {eff}")
                return
            # Cost: discard from hand (required, BODY起動)
            m_req_discard = re.search(r'手札を(\d+)枚控え室に置く', cost)
            req_discard_n = 0
            if m_req_discard:
                try:
                    req_discard_n = int(m_req_discard.group(1) or 0)
                except Exception:
                    req_discard_n = 0
            if req_discard_n <= 0 and ('手札を1枚控え室に置く' in cost):
                req_discard_n = 1
            if req_discard_n > 0 and int(discard_success_reduction or 0) > 0:
                printed_req_discard_n = int(req_discard_n)
                req_discard_n = max(0, int(req_discard_n) - int(discard_success_reduction or 0))
                gs.log.append(f"[COST] activate discard cost reduced by success-zone cards: {printed_req_discard_n}->{req_discard_n} (success={success_count_for_cost})")
            if req_discard_n > 0:
                if len(gs.hand) < req_discard_n:
                    gs.log.append(f"[ERR] activate: not enough cards in hand for discard cost (need {req_discard_n})")
                    return
                if flags.get('once_per_turn'):
                    try:
                        gs.used_this_turn[akey] = 1
                    except Exception:
                        try:
                            gs.used_this_turn = {akey: 1}
                        except Exception:
                            pass
                gs.pending.append({
                    'kind': 'discard_from_hand',
                    'remaining': req_discard_n,
                    'text': f'手札を{req_discard_n}枚控え室に置く',
                    'options': list(gs.hand),
                    'after_effect_template': eff,
                    'after_ctx': {'pos': pos, 'source_cn': ci.cardnumber},
                    'after_source_cn': ci.cardnumber,
                })
                gs.log.append(f"[PENDING] activate discard {req_discard_n} then {eff}")
                return
            need_e = _parse_energy_cost(cost)
            if need_e > 0:
                if not pay_energy(gs, need_e):
                    gs.log.append(f"[ERR] activate: insufficient energy for [E]{need_e} (have {gs.energy_active})")
                    return
                gs.log.append(f"[COST] paid [E]{need_e} (E active={gs.energy_active} wait={gs.energy_wait})")
            # Special cost: move 1 energy from energy zone under this member
            # Prefer WAIT energy first, then ACTIVE (Mia etc.).
            if _cost_move_active_energy_to_under(cost):
                a_act = int(gs.energy_active or 0)
                a_wait = int(gs.energy_wait or 0)
                if (a_act + a_wait) < 1:
                    gs.log.append(f"[ERR] activate: insufficient energy to place under (active={gs.energy_active} wait={gs.energy_wait})")
                    return
                src = 'active'
                try:
                    if a_wait >= 1:
                        gs.energy_wait -= 1
                        src = 'wait'
                    else:
                        gs.energy_active -= 1
                        src = 'active'
                except Exception:
                    pass
                try:
                    slot.energy_under = int(getattr(slot, 'energy_under', 0) or 0) + 1
                except Exception:
                    pass
                gs.log.append(f"[COST] moved 1 energy under {pos} from {src} (under={int(getattr(slot,'energy_under',0) or 0)}; E active={gs.energy_active} wait={gs.energy_wait})")
            if _cost_requires_self_to_green(cost):
                leaving_cn = str(getattr(slot, 'cardnumber', '') or '')
                _return_under_energy_to_deck_from_slot(gs, slot, pos=pos, reason=f'{leaving_cn} leaves stage by cost', cards_db=cards_db)
                gs.green_room.append(leaving_cn)
                gs.stage[pos] = None
                gs.log.append(f"[COST] {pos}: {leaving_cn} -> waiting room")
                try:
                    leave_trigs = _collect_auto_triggers_on_member_leave_stage(gs, cards_db, left_pos=pos, left_cn=leaving_cn)
                except Exception:
                    leave_trigs = []
                if len(leave_trigs) >= 2:
                    opts2 = []
                    for t in leave_trigs:
                        scn = _canon_cardno(str((t or {}).get('source_cn', '') or ''))
                        if scn:
                            opts2.append(scn)
                    gs.pending.append({
                        'kind': 'auto_order',
                        'text': '自動効果が複数発生：解決するカードを選択（1つずつ）',
                        'options': opts2,
                        'queue': leave_trigs,
                    })
                    gs.log.append(f"[PENDING] auto_order triggers={len(leave_trigs)}")
                    return
                for t in leave_trigs:
                    _exec_auto_trigger(gs, cards_db, t)
            # Cost: self-wait (member stays on stage but becomes WAIT)
            if _cost_requires_self_wait(cost) and not _cost_requires_self_to_green(cost):
                slot.active = False
                gs.log.append(f"[COST] {pos}: {slot.cardnumber} -> WAIT (self-wait cost)")
            # Cost: pick named cards from green room, shuffle to deck bottom
            named_cost = _cost_named_cards_to_deck_bottom(cost)
            if named_cost:
                names = named_cost['names']
                total = named_cost['total']
                # candidates: cards in green room whose name contains any target name
                cands = []
                for gcn in list(gs.green_room):
                    gci = _get_card(cards_db, gcn)
                    gname = str(getattr(gci, 'name', '') or getattr(gci, 'cardname', '') or gcn)
                    if any(n in gname for n in names):
                        cands.append(gcn)
                if len(cands) < total:
                    gs.log.append(f"[ERR] named_cards_cost: コスト支払い不可。必要{total}枚、控え室に{len(cands)}枚（{names}）")
                    # 消費済みコスト（エネルギー・自己控え室）を巻き戻す余裕はないので警告のみ
                    return
                else:
                    # Mark once-per-turn before suspending
                    if flags.get('once_per_turn'):
                        try:
                            gs.used_this_turn[akey] = 1
                        except Exception:
                            try:
                                gs.used_this_turn = {akey: 1}
                            except Exception:
                                pass
                    gs.pending.append({
                        'kind': 'named_cards_cost_multi',
                        'text': f'控え室から合計{total}枚を選択してデッキの一番下へ（{"・".join(names)}）',
                        'options': cands,
                        'total': total,
                        'resume_effect': eff,
                        'resume_pos': pos,
                        'resume_source_cn': ci.cardnumber,
                    })
                    gs.log.append(f"[PENDING] named_cards_cost_multi: total={total} cands={cands}")
                    return
            # Cost: 手札をすべて公開する（BODY起動効果）
            if '手札をすべて公開する' in cost:
                # Mark once-per-turn before suspending
                if flags.get('once_per_turn'):
                    try:
                        gs.used_this_turn[akey] = 1
                    except Exception:
                        try:
                            gs.used_this_turn = {akey: 1}
                        except Exception:
                            pass
                _handle_body_reveal_all_hand(gs, cards_db, pos, ci.cardnumber, eff, rng)
                return
            # Mark once-per-turn usage after costs are paid (even if effect creates pending)
            if flags.get('once_per_turn'):
                try:
                    gs.used_this_turn[akey] = 1
                except Exception:
                    try:
                        gs.used_this_turn = {akey: 1}
                    except Exception:
                        pass
            ctx = {'pos': pos, 'source_cn': ci.cardnumber}
            matched = try_apply_effect_template(gs, rng, cards_db, eff, ctx)
            if not matched:
                gs.log.append(f"[WARN] activate: unsupported effect_template: {eff}")
            if gs.pending:
                return
        return
    # If this card has matchable activated templates, do NOT fall back to legacy heuristics.
    if _has_matchable_activated(ci):
        gs.log.append(f"[ERR] activate: no usable activated ability on {ci.cardnumber} (conditions/cost/limit)")
        return
    # 2) Legacy fallback (kept)
    if not (_has_green_live_take_ability(ci) or _has_green_member_take_ability(ci) or _has_sacrifice_ability(ci)):
        gs.log.append(f"[ERR] activate: no supported activated ability on {ci.cardnumber}")
        return
    if _has_sacrifice_ability(ci):
        _return_under_energy_to_deck_from_slot(gs, slot, pos=pos, reason=f'{ci.cardnumber} leaves stage by legacy cost', cards_db=cards_db)
        gs.green_room.append(slot.cardnumber)
        gs.stage[pos] = None
        gs.log.append(f"[ACT] {pos}: {ci.cardnumber} -> waiting room (cost)")
    if _has_green_live_take_ability(ci):
        cands = _green_live_candidates(gs, cards_db)
        if not cands:
            gs.log.append("[ACT] no LIVE in waiting room to take")
        else:
            gs.pending.append({
                "kind": "pick_live_from_green",
                "text": "控え室のライブカードを1枚手札に加える",
                "options": cands,
            })
            gs.log.append(f"[PENDING] pick 1 LIVE from waiting room ({len(cands)} candidates; confirm required)")
    if _has_green_member_take_ability(ci):
        def _card_type_upper(x: Any) -> str:
            if x is None:
                return ""
            t = getattr(x, "type", None)
            if t is None:
                t = getattr(x, "cardtype", None)
            return str(t or "").upper()
        cands = [cn for cn in gs.green_room if (_get_card(cards_db, cn) and _card_type_upper(_get_card(cards_db, cn)) == "MEMBER")]
        if not cands:
            gs.log.append("[ACT] no MEMBER in waiting room to take")
        else:
            gs.pending.append({
                "kind": "pick_member_from_green",
                "text": "控え室のメンバーカードを1枚手札に加える",
                "options": cands,
            })
            gs.log.append(f"[PENDING] pick 1 MEMBER from waiting room ({len(cands)} candidates; confirm required)")
def cmd_resolve_pending(gs: GameState, cards_db: Dict[str, CardInfo], idx: int, choice: str, rng: Optional[random.Random] = None) -> None:
    if idx < 0 or idx >= len(gs.pending):
        # The browser can occasionally send a stale ACK/NEXT immediately after a
        # one-button notification prompt has already closed.  Treat that as an
        # idempotent acknowledgement rather than surfacing a false engine error.
        low_stale = str(choice or '').strip().lower()
        if not (getattr(gs, 'pending', None) or []) and low_stale in ('', 'ok', 'next', 'confirm', '確認'):
            return
        gs.log.append("[ERR] resolve_pending: invalid idx")
        return
    if rng is None:
        rng = random.Random(gs.seed)
    p = gs.pending.pop(idx)
    kind = str(p.get("kind", "") or "")
    choice_str = str(choice or "").strip()
    def _auto_queue_to_options(q: List[Dict[str, Any]]) -> List[str]:
        out: List[str] = []
        for t in (q or []):
            txt = _auto_trigger_option_text(t)
            if txt:
                out.append(txt)
        return out
    def _enqueue_auto_order_from_deferred() -> None:
        """Enqueue deferred auto-order prompt only when nothing else is pending.
        This prevents interleaving multiple auto triggers in the middle of a multi-step
        resolution chain (e.g., mode choice -> target pick).
        """
        q = getattr(gs, '_deferred_auto_queue', None)
        if not q:
            return
        if gs.pending:
            return
        # Avoid duplication
        if any((str(pp.get('kind','') or '') == 'auto_order') for pp in (gs.pending or [])):
            return
        opts2 = _auto_queue_to_options(list(q))
        if not opts2:
            setattr(gs, '_deferred_auto_queue', [])
            return
        gs.pending.append({
            'kind': 'auto_order',
            'text': str(getattr(gs, '_deferred_auto_text', '') or '自動効果が複数発生：解決するカードを選択（1つずつ）'),
            'options': opts2,
            'queue': list(q),
        })
        setattr(gs, '_deferred_auto_queue', [])
    def _mark_used_once_from_pending(pp: Dict[str, Any]) -> None:
        try:
            if bool(pp.get('once_per_turn', False)) and str(pp.get('usage_key', '') or '').strip():
                gs.used_this_turn[str(pp.get('usage_key'))] = 1
        except Exception:
            try:
                gs.used_this_turn = {str(pp.get('usage_key')): 1}
            except Exception:
                pass

    def _finish_extra_yell_from_picked(pp: Dict[str, Any], picked: List[str]) -> None:
        extra_mode = str(pp.get('extra_mode', 'count') or 'count')
        extra_n = 0
        if extra_mode == 'cost_div5_cap4':
            total = 0
            for cn0 in picked:
                ci0 = _get_card(cards_db, cn0)
                try:
                    total += max(0, int(getattr(ci0, 'cost', 0) or 0) // 5) if ci0 else 0
                except Exception:
                    pass
            extra_n = min(4, int(total))
        else:
            extra_n = int(len(picked))
        if picked:
            gs.log.append(f"[AUTO] {str(pp.get('source_cn','') or '?')}[エール時]: moved revealed cards to green {picked}; additional yell {extra_n}")
        else:
            gs.log.append(f"[SKIP] {str(pp.get('source_cn','') or '?')}[エール時]: no revealed cards moved; additional yell skipped")
        _mark_used_once_from_pending(pp)
        if extra_n > 0:
            _perform_additional_yell(gs, rng, cards_db, extra_n, reason=str(pp.get('source_cn','') or 'extra-yell'))
        _enqueue_auto_order_from_deferred()

    if kind == 'confirm_yell_revealed_all_to_green_then_extra_yell':
        low = choice_str.lower()
        cands = [str(x) for x in list(p.get('candidates', []) or []) if str(x or '').strip()]
        if low in ('pay', 'yes', 'y', '1', 'true', 'apply', 'use', '使う'):
            moved = []
            for cn0 in cands:
                if _move_yell_revealed_to_green(gs, cn0):
                    moved.append(_canon_cardno(cn0))
            extra_n = int(p.get('extra_count', len(moved)) or len(moved))
            if moved:
                gs.log.append(f"[AUTO] {str(p.get('source_cn','') or '?')}[エール時]: moved all revealed non-LIVE cards to green {moved}; additional yell {extra_n}")
                _mark_used_once_from_pending(p)
                if extra_n > 0:
                    _perform_additional_yell(gs, rng, cards_db, extra_n, reason=str(p.get('source_cn','') or 'reroll-yell'))
            else:
                gs.log.append(f"[SKIP] {str(p.get('source_cn','') or '?')}[エール時]: no current revealed cards moved")
                _mark_used_once_from_pending(p)
        else:
            gs.log.append(f"[SKIP] {str(p.get('source_cn','') or '?')}[エール時]: reroll yell skipped")
            _mark_used_once_from_pending(p)
        _enqueue_auto_order_from_deferred()
        return

    if kind == 'choose_yell_revealed_to_green_then_extra_yell':
        low = choice_str.lower()
        picked = [str(x) for x in list(p.get('picked', []) or []) if str(x or '').strip()]
        cands = [str(x) for x in list(p.get('candidates', []) or []) if str(x or '').strip()]
        max_picks = max(0, int(p.get('max_picks', 1) or 1))
        if low in ('skip', '__skip__', 'done', 'finish', 'no', 'n', '0', 'false', '使わない', 'スキップ'):
            _finish_extra_yell_from_picked(p, picked)
            return
        cn = _canon_cardno(choice_str)
        if not cn or cn not in [_canon_cardno(x) for x in cands]:
            gs.log.append(f"[ERR] choose_yell_revealed_to_green_then_extra_yell: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        if _move_yell_revealed_to_green(gs, cn):
            picked.append(cn)
        else:
            gs.log.append(f"[WARN] choose_yell_revealed_to_green_then_extra_yell: {cn} was not in current revealed zone")
        # Remove one selected instance from remaining candidates.
        removed = False
        rest = []
        for x in cands:
            if (not removed) and _canon_cardno(x) == cn:
                removed = True
                continue
            rest.append(x)
        if len(picked) >= max_picks or not rest:
            _finish_extra_yell_from_picked(p, picked)
            return
        p2 = dict(p)
        p2['picked'] = list(picked)
        p2['candidates'] = list(rest)
        p2['options'] = list(rest)
        p2['display_cards'] = list(rest)
        p2['text'] = f"{str(p.get('source_cn','') or '')}[エール時] 追加で控え室に置く公開カードを選んでください（{len(picked)}/{max_picks}枚選択済み。終了する場合はスキップ）。"
        p2['optional'] = True
        gs.pending.append(p2)
        gs.log.append(f"[PENDING] choose additional-yell revealed card picked={len(picked)}/{max_picks} remain={len(rest)}")
        return

    if kind == 'live_start_reduce_any_if_opponent_wait_exists_manual':
        low = choice_str.lower()
        src = str(p.get('source_cn', '') or '')
        set_idx = p.get('set_idx', None)
        reduce_any = int(p.get('reduce_any', 0) or 0)
        try:
            _mark_live_start_set_idx_resolved(gs, set_idx)
        except Exception:
            pass
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false', 'cancel', 'いいえ', 'スキップ'):
            gs.log.append(f'[SKIP] {src}[ライブ開始時]: opponent wait-state condition not met -> required(any) unchanged')
            _enqueue_auto_order_from_deferred()
            return
        if low not in ('apply', 'yes', 'y', '1', 'true', 'use', 'go', 'confirm', 'はい', '使う'):
            gs.log.append(f"[ERR] {kind}: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        if reduce_any > 0:
            _k = _canon_cardno(src)
            if set_idx is not None:
                _rmap = dict(getattr(gs, 'live_start_required_any_reduction_by_set_idx', {}) or {})
                _rmap[int(set_idx)] = max(int(_rmap.get(int(set_idx), 0) or 0), int(reduce_any))
                gs.live_start_required_any_reduction_by_set_idx = _rmap
            else:
                _rmap = dict(getattr(gs, 'live_start_required_any_reduction_by_cn', {}) or {})
                _rmap[_k] = max(int(_rmap.get(_k, 0) or 0), int(reduce_any))
                gs.live_start_required_any_reduction_by_cn = _rmap
        gs.log.append(f'[AUTO] {src}[ライブ開始時]: opponent wait-state condition applied -> required(any) -{reduce_any}')
        _enqueue_auto_order_from_deferred()
        return
    if kind == 'choose_opponent_wait_count_for_topdeck_green_group_members':
        src = str(p.get('source_cn', '') or '')
        group_name = str(p.get('condition_group_name', '') or '')
        try:
            n = int(str(choice_str or '0').strip())
        except Exception:
            n = -1
        if n < 0 or n > 3:
            gs.log.append(f"[ERR] {kind}: invalid count {choice_str}")
            gs.pending.append(p)
            return
        try:
            _mark_live_start_set_idx_resolved(gs, p.get('set_idx', None))
        except Exception:
            pass
        if n <= 0:
            gs.log.append(f'[SKIP] {src}[ライブ開始時]: opponent wait count=0 -> no topdeck')
            _enqueue_auto_order_from_deferred()
            return
        _enqueue_topdeck_from_green(gs, cards_db, kind='MEMBER', n=n, group=group_name, allow_less=True)
        gs.log.append(f'[PENDING] {src}[ライブ開始時]: topdeck up to {n} 『{group_name}』 member(s) from green')
        return
    if kind == 'choose_stage_member_to_position_change_source':
        allow_skip = bool(p.get('allow_skip', False) or p.get('optional', False))
        low = choice_str.lower()
        if allow_skip and low in ('skip', '__skip__', 'no', 'n', '0', 'false', '使わない', 'いいえ', 'スキップ'):
            gs.log.append('[SKIP] choose_stage_member_to_position_change_source: skipped')
            return
        src_pos = str(choice_str or '').upper()
        if src_pos not in ('L','C','R'):
            gs.log.append(f"[ERR] position_change_source: invalid pos {choice_str}")
            return
        slot_src = gs.stage.get(src_pos)
        if not slot_src:
            gs.log.append(f"[ERR] position_change_source: empty {src_pos}")
            return
        src_cn = str(getattr(slot_src, 'cardnumber', '') or '')
        dst_opts = [p2 for p2 in ('L','C','R') if p2 != src_pos]
        gs.pending.append({
            'kind': 'position_change',
            'src_pos': src_pos,
            'source_cn': src_cn,
            'text': f'{src_pos}: {src_cn or "メンバー"} の移動先を選んでください。移動先にメンバーがいる場合は入れ替わります。',
            'options': dst_opts,
        })
        gs.log.append(f'[PENDING] position_change source={src_pos} -> choose destination')
        return
    if kind == 'position_change':
        src_pos = str(p.get('src_pos', '') or '').upper()
        source_cn = str(p.get('source_cn', '') or '')
        valid_src = {'L', 'C', 'R'}
        valid_dst = {'L', 'C', 'R'}
        if src_pos not in valid_src:
            gs.log.append(f"[ERR] position_change: invalid src_pos '{src_pos}'")
            return
        if (choice_str == '') or (choice_str.lower() == 'skip'):
            gs.log.append(f"[POSITION_CHANGE] {source_cn or '?'} {src_pos} -> skip")
            return
        dst_pos = choice_str.upper()
        if dst_pos not in valid_dst:
            gs.log.append(f"[ERR] position_change: invalid choice '{choice_str}'")
            gs.pending.insert(idx, p)
            return
        stage = getattr(gs, 'stage', None)
        if not isinstance(stage, dict):
            gs.log.append('[ERR] position_change: stage missing')
            return
        src_slot = stage.get(src_pos)
        dst_slot = stage.get(dst_pos)
        if src_slot is None:
            gs.log.append(f"[WARN] position_change: source {src_pos} is empty")
            return
        if not source_cn:
            try:
                source_cn = str(getattr(src_slot, 'cardnumber', '') or '')
            except Exception:
                source_cn = ''
        stage[src_pos], stage[dst_pos] = dst_slot, src_slot
        gs.log.append(f"[POSITION_CHANGE] {source_cn or '?'} {src_pos} -> {dst_pos}")
        return
    if kind == 'auto_order':
        queue = list(p.get('queue', []) or [])
        if not queue:
            gs.log.append('[INFO] auto_order: empty queue')
            return
        cn_choice = _canon_cardno(choice_str)
        pick_i = None
        # First, require exact option text. This disambiguates multiple effects from
        # the same card (e.g. a LIVE card with two <ライブ成功時> abilities).
        for i, t in enumerate(queue):
            txt = _auto_trigger_option_text(t)
            if txt and txt == choice_str:
                pick_i = i
                break
        # Card-number fallback is safe only when exactly one queued trigger has that source.
        if pick_i is None and cn_choice:
            source_matches = [i for i, t in enumerate(queue) if _canon_cardno(str(t.get('source_cn', '') or '')) == cn_choice]
            if len(source_matches) == 1:
                pick_i = source_matches[0]
            elif len(source_matches) > 1:
                gs.log.append(f"[ERR] auto_order: ambiguous source card {choice_str}; choose the effect-specific option")
                gs.pending.append(p)
                return
        if pick_i is None:
            gs.log.append(f"[ERR] auto_order: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        trig = queue.pop(pick_i)
        _exec_auto_trigger(gs, cards_db, trig)
        # Defer remaining triggers until the current trigger (and any nested pending prompts) finishes.
        if queue:
            setattr(gs, '_deferred_auto_queue', list(queue))
            setattr(gs, '_deferred_auto_text', str(p.get('text', '') or '自動効果が複数発生：解決するカードを選択（1つずつ）'))
            _enqueue_auto_order_from_deferred()
        return
    # --- Generic effect-engine prompts ---
    if kind == 'effect_notice':
        txt = str(p.get('text', '') or '').strip()
        src = str(p.get('source_cn', '') or '').strip()
        if txt:
            gs.log.append(f"[INFO] {src or '?'}: notice acknowledged - {txt}")
        _enqueue_auto_order_from_deferred()
        return
    if kind == 'confirm_revealed_self_to_hand':
        src = str(p.get('source_cn', '') or '').strip()
        low = choice_str.lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false', 'cancel', 'skip effect', '使わない', 'いいえ', 'スキップ'):
            gs.log.append(f"[SKIP] {src}: revealed self-to-hand skipped")
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            _enqueue_auto_order_from_deferred()
            return
        if low not in ('apply', 'yes', 'y', '1', 'true', 'use', 'do', 'go', 'ok', 'confirm', '使う', 'はい'):
            gs.log.append(f"[ERR] confirm_revealed_self_to_hand: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        cn = _canon_cardno(src)
        moved = None
        for zone_name in ('resolve_zone', 'green_room'):
            z = getattr(gs, zone_name, None)
            if not isinstance(z, list):
                continue
            for i, x in enumerate(list(z)):
                if _canon_cardno(x) == cn:
                    moved = z.pop(i)
                    break
            if moved:
                break
        if not moved:
            gs.log.append(f"[ERR] confirm_revealed_self_to_hand: source not found in yell zones {cn}")
            return
        gs.hand.append(moved)
        _remove_from_yell_revealed_tracker(gs, moved)
        gs.log.append(f"[ACT] {src}: revealed self -> hand")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        _enqueue_auto_order_from_deferred()
        return

    if kind == 'confirm_effect':
        after_eff = str(p.get('after_effect_template', '') or '').strip()
        ctx0 = dict(p.get('ctx', {}) or {})
        src = str(p.get('source_cn', '') or '')
        low = choice_str.lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false', 'cancel', 'skip effect', '使わない', 'いいえ', 'スキップ'):
            gs.log.append(f"[SKIP] {src}: skipped optional effect")
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            return
        if low not in ('apply', 'yes', 'y', '1', 'true', 'use', 'do', 'go', 'ok', 'confirm', '使う', 'はい'):
            gs.log.append(f"[ERR] confirm_effect: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        if src and not ctx0.get('source_cn'):
            ctx0['source_cn'] = src
        applied = False
        if after_eff:
            try:
                rng = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
            except Exception:
                rng = random.Random()
            applied = bool(try_apply_effect_template(gs, rng, cards_db, after_eff, ctx0))
        score_bonus = p.get('after_live_success_score_bonus') if isinstance(p, dict) else None
        if isinstance(score_bonus, dict):
            _cn_bonus = str(score_bonus.get('cn_live', src) or src or '')
            _bonus_n = int(score_bonus.get('bonus', 0) or 0)
            _detail = str(score_bonus.get('detail', '') or '')
            _add_live_success_score_bonus(gs, _cn_bonus, _bonus_n, detail=_detail)
            applied = True
        live_start_bonus = p.get('after_live_start_score_bonus') if isinstance(p, dict) else None
        if isinstance(live_start_bonus, dict):
            _src_bonus = str(live_start_bonus.get('source_cn', src) or src or '')
            _bonus_n = int(live_start_bonus.get('bonus', 0) or 0)
            _set_idx = live_start_bonus.get('set_idx', None)
            try:
                _mark_live_start_set_idx_resolved(gs, _set_idx)
            except Exception:
                pass
            _add_live_start_score_bonus(gs, _bonus_n, set_idx=_set_idx, source_cn=_src_bonus)
            applied = True
        gs.log.append(f"[AUTO] {src}: confirm_effect -> {'applied' if applied else 'no_match'} {after_eff}")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        _enqueue_auto_order_from_deferred()
        return
    if kind == 'live_start_score_if_live_zone_group_count_at_least':
        low = choice_str.lower()
        if low not in ('ok', 'apply', 'yes', 'y', '1', 'true', 'use', 'go', 'confirm', 'はい', '使う'):
            gs.log.append(f"[ERR] {kind}: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        src = str(p.get('source_cn', '') or '')
        set_idx = p.get('set_idx', None)
        _mark_live_start_set_idx_resolved(gs, set_idx)
        group_name = str(p.get('condition_group_name', '') or '')
        need = int(p.get('condition_count', 0) or 0)
        delta = int(p.get('score_delta', 0) or 0)
        cnt = int(_live_zone_group_card_count(gs, cards_db, group_name))
        bonus = int(delta if cnt >= need else 0)
        if bonus > 0:
            _add_live_start_score_bonus(gs, bonus, set_idx=set_idx, source_cn=src)
        gs.log.append(f"[AUTO] {src}[ライブ開始時]: live-zone group({group_name})={cnt}/{need} -> score {bonus:+d}")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return
    if kind == 'live_start_score_if_green_live_group_count_at_least':
        low = choice_str.lower()
        if low not in ('ok', 'apply', 'yes', 'y', '1', 'true', 'use', 'go', 'confirm', 'はい', '使う'):
            gs.log.append(f"[ERR] {kind}: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        src = str(p.get('source_cn', '') or '')
        set_idx = p.get('set_idx', None)
        _mark_live_start_set_idx_resolved(gs, set_idx)
        group_name = str(p.get('condition_group_name', '') or '')
        need = int(p.get('condition_count', 0) or 0)
        delta = int(p.get('score_delta', 0) or 0)
        cnt = int(_green_live_count_by_group_or_unit(gs, cards_db, group_name))
        bonus = int(delta if cnt >= need else 0)
        if bonus > 0:
            _add_live_start_score_bonus(gs, bonus, set_idx=set_idx, source_cn=src)
        gs.log.append(f"[AUTO] {src}[ライブ開始時]: green live group({group_name})={cnt}/{need} -> score {bonus:+d}")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return

    if kind == 'live_start_score_per_stage_group_member_heart_color_kind':
        low = choice_str.lower()
        if low not in ('ok', 'apply', 'yes', 'y', '1', 'true', 'use', 'go', 'confirm', 'はい', '使う'):
            gs.log.append(f"[ERR] {kind}: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        src = str(p.get('source_cn', '') or '')
        set_idx = p.get('set_idx', None)
        _mark_live_start_set_idx_resolved(gs, set_idx)
        group_name = str(p.get('condition_group_name', '') or '')
        per = int(p.get('score_delta_per_kind', 0) or 0)
        cnt = int(_stage_group_member_heart_color_kinds(gs, cards_db, group_name))
        bonus = int(per * cnt)
        if bonus > 0:
            _add_live_start_score_bonus(gs, bonus, set_idx=set_idx, source_cn=src)
        gs.log.append(f"[AUTO] {src}[ライブ開始時]: stage group({group_name}) color kinds={cnt} -> score {bonus:+d}")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return
    if kind == 'live_start_score_if_success_zone_has_scores':
        low = choice_str.lower()
        if low not in ('ok', 'apply', 'yes', 'y', '1', 'true', 'use', 'go', 'confirm', 'はい', '使う'):
            gs.log.append(f"[ERR] {kind}: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        src = str(p.get('source_cn', '') or '')
        set_idx = p.get('set_idx', None)
        _mark_live_start_set_idx_resolved(gs, set_idx)
        a = int(p.get('score_a', 0) or 0)
        b = int(p.get('score_b', 0) or 0)
        one = int(p.get('score_delta_one', 0) or 0)
        both = int(p.get('score_delta_both', 0) or 0)
        bonus = int(_success_zone_score_set_bonus(gs, cards_db, score_a=a, score_b=b, delta_one=one, delta_both=both))
        if bonus > 0:
            _add_live_start_score_bonus(gs, bonus, set_idx=set_idx, source_cn=src)
        gs.log.append(f"[AUTO] {src}[ライブ開始時]: success scores({a}/{b}) -> score {bonus:+d}")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return
    if kind == 'live_start_score_if_green_unique_live_names_group_count':
        low = choice_str.lower()
        if low not in ('ok', 'apply', 'yes', 'y', '1', 'true', 'use', 'go', 'confirm', 'はい', '使う'):
            gs.log.append(f"[ERR] {kind}: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        src = str(p.get('source_cn', '') or '')
        set_idx = p.get('set_idx', None)
        _mark_live_start_set_idx_resolved(gs, set_idx)
        group_name = str(p.get('condition_group_name', '') or '')
        c1 = int(p.get('condition_count_one', 0) or 0)
        d1 = int(p.get('score_delta_one', 0) or 0)
        c2 = int(p.get('condition_count_two', 0) or 0)
        d2 = int(p.get('score_delta_two', 0) or 0)
        n_unique = int(_green_unique_live_names_count(gs, cards_db, group_name))
        bonus = int(d2 if n_unique >= int(c2) else (d1 if n_unique >= int(c1) else 0))
        if bonus > 0:
            _add_live_start_score_bonus(gs, bonus, set_idx=set_idx, source_cn=src)
        gs.log.append(f"[AUTO] {src}[ライブ開始時]: green unique live names({group_name}) count={n_unique} thresholds=({c1}/{c2}) -> score {bonus:+d}")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return
    if kind == 'live_start_score_and_increase_any_per_success_zone_cardname_count':
        low = choice_str.lower()
        if low not in ('ok', 'apply', 'yes', 'y', '1', 'true', 'use', 'go', 'confirm', 'はい', '使う'):
            gs.log.append(f"[ERR] {kind}: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        src = str(p.get('source_cn', '') or '')
        set_idx = p.get('set_idx', None)
        _mark_live_start_set_idx_resolved(gs, set_idx)
        cardname = str(p.get('condition_cardname', '') or '')
        per_score = int(p.get('score_delta_per', 0) or 0)
        per_any = int(p.get('required_any_increase_per', 0) or 0)
        cnt = int(_success_zone_cardname_count(gs, cards_db, cardname))
        bonus = int(per_score * cnt)
        add_any = int(per_any * cnt)
        if bonus > 0 or add_any > 0:
            _k = _canon_cardno(src)
            if set_idx is not None:
                if bonus > 0:
                    _add_live_start_score_bonus(gs, bonus, set_idx=set_idx, source_cn=src)
                if add_any > 0:
                    _imap = dict(getattr(gs, 'live_start_required_any_increase_by_set_idx', {}) or {})
                    _imap[int(set_idx)] = int(_imap.get(int(set_idx), 0) or 0) + int(add_any)
                    gs.live_start_required_any_increase_by_set_idx = _imap
            else:
                if bonus > 0:
                    _add_live_start_score_bonus(gs, bonus, set_idx=None, source_cn=src)
                if add_any > 0:
                    _imap = dict(getattr(gs, 'live_start_required_any_increase_by_cn', {}) or {})
                    _imap[_k] = int(_imap.get(_k, 0) or 0) + int(add_any)
                    gs.live_start_required_any_increase_by_cn = _imap
        gs.log.append(f"[AUTO] {src}[ライブ開始時]: success cardname({cardname}) count={cnt} -> required(any) +{add_any}, score {bonus:+d}")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return
    if kind == 'live_start_reduce_any_and_score_if_success_score_at_least':
        low = choice_str.lower()
        if low not in ('ok', 'apply', 'yes', 'y', '1', 'true', 'use', 'go', 'confirm', 'はい', '使う'):
            gs.log.append(f"[ERR] {kind}: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        src = str(p.get('source_cn', '') or '')
        set_idx = p.get('set_idx', None)
        _mark_live_start_set_idx_resolved(gs, set_idx)
        total = int(_success_zone_score_total(gs, cards_db))
        reduce_th = int(p.get('reduce_threshold', 0) or 0)
        reduce_any = int(p.get('reduce_any', 0) or 0)
        score_th = int(p.get('score_threshold', 0) or 0)
        delta = int(p.get('score_delta', 0) or 0)
        red = int(reduce_any if total >= reduce_th else 0)
        bonus = int(delta if total >= score_th else 0)
        if red > 0 or bonus > 0:
            _k = _canon_cardno(src)
            if set_idx is not None:
                if red > 0:
                    _rmap = dict(getattr(gs, 'live_start_required_any_reduction_by_set_idx', {}) or {})
                    _rmap[int(set_idx)] = max(int(_rmap.get(int(set_idx), 0) or 0), int(red))
                    gs.live_start_required_any_reduction_by_set_idx = _rmap
                if bonus > 0:
                    _add_live_start_score_bonus(gs, bonus, set_idx=set_idx, source_cn=src)
            else:
                if red > 0:
                    _rmap = dict(getattr(gs, 'live_start_required_any_reduction_by_cn', {}) or {})
                    _rmap[_k] = max(int(_rmap.get(_k, 0) or 0), int(red))
                    gs.live_start_required_any_reduction_by_cn = _rmap
                if bonus > 0:
                    _add_live_start_score_bonus(gs, bonus, set_idx=None, source_cn=src)
        gs.log.append(f"[AUTO] {src}[ライブ開始時]: success score total={total} -> required(any) -{red}, score {bonus:+d}")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return
    if kind == 'live_start_success_count_distinct_names_score_ack':
        low = choice_str.lower()
        if low not in ('ok', 'apply', 'yes', 'y', '1', 'true', 'use', 'go', 'confirm', 'はい', '使う'):
            gs.log.append(f"[ERR] {kind}: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        src = str(p.get('source_cn', '') or '')
        set_idx = p.get('set_idx', None)
        delta = int(p.get('score_delta', 0) or 0)
        _mark_live_start_set_idx_resolved(gs, set_idx)
        if delta > 0:
            _add_live_start_score_bonus(gs, delta, set_idx=set_idx, source_cn=src)
        gs.log.append(f"[AUTO] {src}[ライブ開始時]: success-count/name condition -> score +{delta}")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return

    if kind == 'pay_or_skip':
        # Generic optional-cost prompt (e.g., "...してもよい：<effect>")
        cost_kind = str(p.get('cost_kind', '') or '')
        cost_n = _safe_int(p.get('cost_n', 0), 0)
        after_eff = str(p.get('after_effect_template', '') or '').strip()
        ctx0 = dict(p.get('ctx', {}) or {})
        src = str(p.get('source_cn', '') or '')
        low = choice_str.lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false', 'cancel', '使わない', 'いいえ', 'スキップ'):
            gs.log.append(f"[SKIP] {src}: skipped optional cost")
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            return
        if low not in ('pay', 'yes', 'y', '1', 'true', '使う', 'はい'):
            gs.log.append(f"[ERR] pay_or_skip: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        if src and not ctx0.get('source_cn'):
            ctx0['source_cn'] = src
        if cost_kind == 'self_wait_and_discard_from_hand':
            pos = str(ctx0.get('pos', '') or '').upper()
            slot = (gs.stage or {}).get(pos) if isinstance(getattr(gs, 'stage', None), dict) else None
            if cost_n <= 0:
                gs.log.append("[ERR] pay_or_skip: invalid combo cost_n")
                return
            if len(gs.hand) < cost_n:
                gs.log.append(f"[ERR] pay_or_skip: not enough cards in hand for combo cost (need {cost_n})")
                return
            if slot is None or not bool(getattr(slot, 'cardnumber', None)):
                gs.log.append(f"[ERR] pay_or_skip: combo self_wait stage empty {pos}")
                return
            slot.active = False
            gs.log.append(f"[COST] {pos}: {getattr(slot,'cardnumber','?')} -> WAIT (self-wait cost)")
            gs.pending.append({
                'kind': 'discard_from_hand',
                'remaining': cost_n,
                'text': f'手札を{cost_n}枚控え室に置く',
                'options': list(gs.hand),
                'after_effect_template': after_eff,
                'after_ctx': ctx0,
                'after_source_cn': src,
            })
            return

        if cost_kind == 'discard_from_hand':
            if cost_n <= 0:
                gs.log.append("[ERR] pay_or_skip: invalid cost_n")
                return
            if len(gs.hand) < cost_n:
                gs.log.append(f"[ERR] pay_or_skip: not enough cards in hand (need {cost_n})")
                return
            gs.pending.append({
                'kind': 'discard_from_hand',
                'remaining': cost_n,
                'text': f'手札を{cost_n}枚控え室に置く',
                'options': list(gs.hand),
                'after_effect_template': after_eff,
                'after_ctx': ctx0,
                'after_source_cn': src,
            })
            return
        if cost_kind == 'self_wait':
            pos = str(ctx0.get('pos', '') or '').upper()
            slot = (gs.stage or {}).get(pos) if isinstance(getattr(gs, 'stage', None), dict) else None
            if slot is None or not bool(getattr(slot, 'cardnumber', None)):
                gs.log.append(f"[ERR] pay_or_skip: self_wait stage empty {pos}")
                return
            slot.active = False
            gs.log.append(f"[COST] {pos}: {getattr(slot,'cardnumber','?')} -> WAIT (self-wait cost)")
            applied = False
            if after_eff:
                try:
                    rng = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
                except Exception:
                    rng = random.Random()
                applied = bool(try_apply_effect_template(gs, rng, cards_db, after_eff, ctx0))
            gs.log.append(f"[AUTO] {src}: self_wait -> {'applied' if applied else 'no_match'} {after_eff}")
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            return
        if cost_kind == 'energy':
            if cost_n <= 0:
                gs.log.append("[ERR] pay_or_skip: invalid energy cost_n")
                return
            if int(getattr(gs, 'energy_active', 0) or 0) < cost_n:
                gs.log.append(f"[ERR] pay_or_skip: not enough active energy (need {cost_n})")
                return
            gs.energy_active = int(getattr(gs, 'energy_active', 0) or 0) - cost_n
            gs.energy_wait = int(getattr(gs, 'energy_wait', 0) or 0) + cost_n
            try:
                _clamp_energy_zone(gs)
            except Exception:
                pass
            gs.log.append(f"[COST] {src}: paid [E]{cost_n} -> energy_active={gs.energy_active} energy_wait={gs.energy_wait}")
            applied = False
            if after_eff:
                try:
                    rng = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
                except Exception:
                    rng = random.Random()
                applied = bool(try_apply_effect_template(gs, rng, cards_db, after_eff, ctx0))
            gs.log.append(f"[AUTO] {src}: energy_cost -> {'applied' if applied else 'no_match'} {after_eff}")
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            return
        if cost_kind in ('', 'none', 'no_cost', 'immediate'):
            applied = False
            if after_eff:
                try:
                    rng = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
                except Exception:
                    rng = random.Random()
                applied = bool(try_apply_effect_template(gs, rng, cards_db, after_eff, ctx0))
            gs.log.append(f"[AUTO] {src}: no-cost optional -> {'applied' if applied else 'no_match'} {after_eff}")
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            return
        gs.log.append(f"[ERR] pay_or_skip: unsupported cost_kind={cost_kind}")
        return
    if kind == 'discard_from_hand':
        rem = _safe_int(p.get('remaining', 0), 0)
        after_eff = str(p.get('after_effect_template', '') or '').strip()
        after_ctx = dict(p.get('after_ctx', {}) or {})
        after_src = str(p.get('after_source_cn', '') or '')
        low0 = str(choice_str or '').strip().lower()
        if low0 in ('skip', '__skip__', 'no', 'n', '0', 'false', 'cancel', '使わない', 'いいえ', 'スキップ') and bool(p.get('allow_skip') or p.get('optional')):
            gs.log.append(f"[SKIP] {after_src}: skipped optional discard cost")
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            _enqueue_auto_order_from_deferred()
            return
        cn = _canon_cardno(choice_str)
        pick_i = None
        for i, x in enumerate(list(gs.hand)):
            if _canon_cardno(x) == cn:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f"[ERR] discard: chosen not in hand {cn}")
            return
        moved = gs.hand.pop(pick_i)
        gs.green_room.append(moved)
        try:
            after_ctx['discarded_cn'] = str(moved or '')
        except Exception:
            pass
        rem -= 1
        gs.log.append(f"[ACT] discard 1 -> {moved} (remaining={rem})")
        if rem > 0:
            gs.pending.append({
                'kind': 'discard_from_hand',
                'remaining': rem,
                'text': f'手札を{rem}枚控え室に置く',
                'options': list(gs.hand),
                'after_effect_template': after_eff,
                'after_ctx': after_ctx,
                'after_source_cn': after_src,
            })
            return
        # After-cost effect (if any)
        if after_eff:
            rng2 = random.Random(getattr(gs, 'seed', 1) or 1)
            ok = try_apply_effect_template(gs, rng2, cards_db, after_eff, after_ctx)
            if ok:
                gs.log.append(f"[ACT] {after_src}: applied {after_eff}")
            else:
                gs.log.append(f"[WARN] {after_src}: after-cost effect not matchable {after_eff}")
        # resume parent prompt if provided
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        _enqueue_auto_order_from_deferred()
        return
    if kind == 'show_revealed_cards_ack':
        gs.log.append('[ACT] show_revealed_cards_ack: ok')
        _r = p.get('_resume') if isinstance(p, dict) else None
        if isinstance(_r, dict) and _r:
            gs.pending.append(_r)
        _enqueue_auto_order_from_deferred()
        return
    if kind == 'pick_success_to_store':
        lives = list(p.get('lives', []) or [])
        if not lives:
            gs.log.append('[INFO] success_store: no successful live cards')
            return
        c0 = str(choice_str or '').strip()
        if c0.lower() == 'skip':
            try:
                before_opp_success = _opponent_success_count(gs)
                after_opp_success = _set_opponent_success_count(gs, before_opp_success + 1)
                gs.next_turn_order = 'second'
                gs.log.append(f'[TURN_ORDER] success_store skipped -> next turn 後手; opponent_success_count {before_opp_success} -> {after_opp_success}')
            except Exception:
                pass
            gs.log.append('[ACT] success_store: skipped')
            return
        cn = _canon_cardno(c0)
        pick = None
        for x in lives:
            if _canon_cardno(x) == cn:
                pick = x
                break
        if not pick:
            gs.log.append(f"[ERR] success_store: invalid choice {cn}")
            gs.pending.insert(idx, p)
            return
        # Move the chosen card from the live card storage to success storage.
        pick_cn = None
        if pick in gs.set_zone:
            pick_cn = pick
        else:
            for v in _cardno_variants(pick):
                if v in gs.set_zone:
                    pick_cn = v
                    break
        if not pick_cn:
            pick_cn = pick
        try:
            if pick_cn in gs.set_zone:
                gs.set_zone.remove(pick_cn)
        except Exception:
            pass
        try:
            gs.success_zone.append(pick_cn)
        except Exception:
            gs.success_zone = list(getattr(gs, 'success_zone', []) or []) + [pick_cn]
        try:
            gs.next_turn_order = 'first'
            gs.log.append('[TURN_ORDER] success_store moved -> next turn 先手')
        except Exception:
            pass
        gs.log.append(f"[ACT] success_store: moved {pick_cn} -> success storage")
        return
    if kind == 'live_start_success_heart_by_success':
        ch = str(choice_str or '').strip()
        m = {
            '桃': 'pink',
            '黄': 'yellow',
            '紫': 'purple',
            'pink': 'pink',
            'yellow': 'yellow',
            'purple': 'purple',
        }
        col = m.get(ch, '')
        if not col:
            gs.log.append(f"[ERR] live_start_success_heart: invalid choice '{ch}'")
            gs.pending.append(p)
            return
        try:
            gs.success_zone_heart_color = col
            gs.success_zone_heart_pos = str(p.get('pos', '') or '').upper()
        except Exception:
            pass
        gs.log.append(f"[ACT] live_start_success_heart: pos={str(p.get('pos', '') or '').upper()} choose={col} (per success card, until end_of_live)")
        return
    if kind == 'live_start_heart_replace':
        pos2 = str(p.get('pos', '') or '').upper()
        cn2 = str(p.get('cn', '') or '')
        ch = str(choice_str or '').strip()
        color_map = dict(p.get('color_map', {}) or {})
        # ch may be Japanese color name
        col = _HEART_JP_MAP.get(ch, '') or color_map.get(ch, '') or ''
        if not col:
            gs.log.append(f"[ERR] live_start_heart_replace: invalid choice '{ch}' for {cn2}")
            gs.pending.append(p)
            return
        slot2 = gs.stage.get(pos2)
        if not slot2:
            gs.log.append(f"[SKIP] live_start_heart_replace: {pos2} empty")
            return
        slot2.heart_replace_color = col
        gs.log.append(f"[ACT] {pos2}: {cn2} 元々持つハートを'{col}'に変換 (ライブ終了時まで)")
        return
    if kind == 'choose_effects':
        remaining = list(p.get('remaining', []) or [])
        picked = list(p.get('picked', []) or [])
        min_pick = int(p.get('min', 1) or 1)
        max_pick = int(p.get('max', 1) or 1)
        ctx0 = dict(p.get('ctx', {}) or {})
        choice0 = str(choice_str or '').strip()
        if choice0.lower() in ('done', '__done__', 'finish', 'end', '終了', '完了'):
            if len(picked) < min_pick:
                # still need at least one selection
                gs.log.append(f"[ERR] choose_effects: select >= {min_pick} before Done")
                gs.pending.append(p)
                return
            gs.log.append(f"[ACT] choose_effects: done (picked={len(picked)})")
            _enqueue_auto_order_from_deferred()
            return
        if choice0 not in remaining:
            gs.log.append(f"[ERR] choose_effects: invalid choice '{choice0}'")
            gs.pending.append(p)
            return
        # remove one occurrence
        rem2 = list(remaining)
        try:
            rem2.remove(choice0)
        except Exception:
            rem2 = [x for x in remaining if x != choice0]
        picked2 = picked + [choice0]
        # Apply the chosen effect (may enqueue another pending)
        rng2 = random.Random(getattr(gs, 'seed', 1) or 1)
        ok = try_apply_effect_template(gs, rng2, cards_db, choice0, ctx0)
        if ok:
            gs.log.append(f"[ACT] choose_effects: applied {choice0}")
        else:
            gs.log.append(f"[WARN] choose_effects: not matchable {choice0}")
        # Need more selections?
        need_more = (len(picked2) < max_pick) and bool(rem2)
        if need_more:
            opts = list(rem2)
            if len(picked2) >= min_pick:
                opts.append('Done')
            resume = {
                'kind': 'choose_effects',
                'text': str(p.get('text', '') or '選択'),
                'options': opts,
                'remaining': list(rem2),
                'picked': list(picked2),
                'min': min_pick,
                'max': max_pick,
                'ctx': ctx0,
            }
            if gs.pending:
                # Attach resume to the next pending (e.g., choose_member_from_green)
                try:
                    gs.pending[-1]['_resume'] = resume
                except Exception:
                    gs.pending.append(resume)
            else:
                gs.pending.append(resume)
        _enqueue_auto_order_from_deferred()
        return
    if kind == 'choose_member_from_green_multi_up_to':
        max_picks = int(p.get('max_picks', 0) or 0)
        min_picks = int(p.get('min_picks', 0) or 0)
        options = list(p.get('options', []) or [])
        raw_picks = [s.strip() for s in choice_str.split(',') if s.strip() and s.strip().lower() not in ('__done__', 'done', 'skip')]
        exact_or_zero = bool(p.get('exact_or_zero', False))
        if exact_or_zero:
            if not (len(raw_picks) == 0 or len(raw_picks) == max_picks):
                gs.log.append(f"[ERR] choose_member_from_green_multi_up_to: invalid pick count {len(raw_picks)} (need 0 or {max_picks})")
                gs.pending.insert(0, p)
                return
        elif len(raw_picks) < min_picks or len(raw_picks) > max_picks:
            gs.log.append(f"[ERR] choose_member_from_green_multi_up_to: invalid pick count {len(raw_picks)} (min={min_picks}, max={max_picks})")
            gs.pending.insert(0, p)
            return
        # Reuse the multi-select UI for hand discard as well.
        if str(p.get('source_zone', '') or '').lower() == 'hand' and str(p.get('action', '') or '') == 'discard_from_hand':
            opts_canon = [_canon_cardno(x) for x in options]
            hand_copy = list(gs.hand)
            picked = []
            for raw in raw_picks:
                cn = _canon_cardno(raw)
                if cn not in opts_canon:
                    gs.log.append(f"[ERR] choose_member_from_green_multi_up_to(hand): {cn} not in options")
                    gs.pending.insert(0, p)
                    return
                found_idx = None
                found_cn = None
                for i, hcn in enumerate(hand_copy):
                    if _canon_cardno(hcn) == cn:
                        found_idx = i
                        found_cn = hcn
                        break
                if found_idx is None:
                    gs.log.append(f"[ERR] choose_member_from_green_multi_up_to(hand): {cn} not in hand")
                    gs.pending.insert(0, p)
                    return
                picked.append(found_cn)
                hand_copy.pop(found_idx)
            if not picked and bool(p.get('skip_if_no_picks', False)):
                gs.log.append(f"[SKIP] {str(p.get('after_source_cn', '') or '')}: skipped optional multi-discard cost")
                _r = p.get('_resume') if isinstance(p, dict) else None
                if _r:
                    gs.pending.append(_r)
                _enqueue_auto_order_from_deferred()
                return
            gs.hand = hand_copy
            gs.green_room.extend(picked)
            gs.log.append(f"[ACT] discard multi -> {picked}")
            after_eff = str(p.get('after_effect_template', '') or '').strip()
            after_ctx = dict(p.get('after_ctx', {}) or {})
            after_src = str(p.get('after_source_cn', '') or '')
            try:
                after_ctx['discarded_cns'] = [str(x or '') for x in list(picked or [])]
                after_ctx['discarded_count'] = int(len(picked or []))
            except Exception:
                pass
            if picked:
                try:
                    after_ctx['discarded_cn'] = str(picked[-1] or '')
                except Exception:
                    pass
            if after_eff:
                rng2 = random.Random(getattr(gs, 'seed', 1) or 1)
                ok = try_apply_effect_template(gs, rng2, cards_db, after_eff, after_ctx)
                if ok:
                    gs.log.append(f"[ACT] {after_src}: applied {after_eff}")
                else:
                    gs.log.append(f"[WARN] {after_src}: after-cost effect not matchable {after_eff}")
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            return
        opts_canon = [_canon_cardno(x) for x in options]
        green_copy = list(gs.green_room)
        picked = []
        for raw in raw_picks:
            cn = _canon_cardno(raw)
            if cn not in opts_canon:
                gs.log.append(f"[ERR] choose_member_from_green_multi_up_to: {cn} not in options")
                gs.pending.insert(0, p)
                return
            found_idx = None
            found_cn = None
            for i, gcn in enumerate(green_copy):
                if _canon_cardno(gcn) == cn:
                    ci2 = _get_card(cards_db, gcn)
                    if not _is_member_ci(ci2):
                        gs.log.append(f"[ERR] choose_member_from_green_multi_up_to: not MEMBER {gcn}")
                        gs.pending.insert(0, p)
                        return
                    found_idx = i
                    found_cn = gcn
                    break
            if found_idx is None:
                gs.log.append(f"[ERR] choose_member_from_green_multi_up_to: {cn} not in waiting room")
                gs.pending.insert(0, p)
                return
            picked.append(found_cn)
            green_copy.pop(found_idx)
        action = str(p.get('action', '') or '')
        if action in ('deck_bottom', 'deck_bottom_costsum'):
            gs.green_room = green_copy
            gs.deck.extend(picked)
            gs.log.append(f"[ACT] choose_member_from_green_multi_up_to: picked={picked} -> deck bottom")
            if action == 'deck_bottom_costsum':
                _apply_bottom_costsum_result(gs, cards_db, str(p.get('pos', '') or ''), str(p.get('source_cn', '') or ''), picked)
            return
        gs.green_room = green_copy
        gs.hand.extend(picked)
        gs.log.append(f"[ACT] choose_member_from_green_multi_up_to: picked={picked} -> hand")
        return
    if kind in ('choose_live_from_green','choose_member_from_green'):
        want_kind = 'LIVE' if kind=='choose_live_from_green' else 'MEMBER'
        low_choice = str(choice_str or '').strip().lower()
        if bool(p.get('allow_skip', False) or p.get('allow_less', False) or p.get('optional', False)) and low_choice in ('skip', '__skip__', 'none', 'no', 'n', '0', 'false', 'スキップ'):
            gs.log.append(f"[SKIP] retrieve optional {want_kind} from waiting room")
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            return
        cn = _canon_cardno(choice_str)
        pick_cn = None
        if cn in gs.green_room:
            pick_cn = cn
        else:
            for x in _cardno_variants(cn):
                if x in gs.green_room:
                    pick_cn = x
                    break
        if not pick_cn:
            gs.log.append(f"[ERR] retrieve: not in waiting room {cn}")
            return
        ci2 = _get_card(cards_db, pick_cn)
        if want_kind=='LIVE' and not _is_live_ci(ci2):
            gs.log.append(f"[ERR] retrieve: not LIVE {pick_cn}")
            return
        if want_kind=='MEMBER' and not _is_member_ci(ci2):
            gs.log.append(f"[ERR] retrieve: not MEMBER {pick_cn}")
            return
        after_ext_key = str(p.get('after_ext_key', '') or '').strip()
        if after_ext_key:
            src = str(p.get('source_cn', '') or '')
            ctx2 = dict(p.get('ctx', {}) or {})
            if src and not ctx2.get('source_cn'):
                ctx2['source_cn'] = src
            ctx2['choice'] = pick_cn
            ctx2['chosen_cn'] = pick_cn
            ctx2['chosen_kind'] = want_kind
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
            except Exception:
                rng2 = random.Random()
            try:
                _apply_effect_by_rule(gs, rng2, cards_db, {'op':'__ext__','ext_key':after_ext_key}, {}, ctx2)
                applied = True
            except Exception:
                applied = False
                raise
            finally:
                try:
                    gs.log.append(f"[AUTO] choose_from_green -> {'applied' if applied else 'error'} {after_ext_key} ({pick_cn})")
                except Exception:
                    pass
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            return
        gs.green_room.remove(pick_cn)
        gs.hand.append(pick_cn)
        gs.log.append(f"[ACT] retrieved {want_kind} {pick_cn} -> hand")
        # n>1 連続回収
        remaining_picks = int(p.get('remaining_picks', 1) or 1) - 1
        if remaining_picks > 0:
            _enqueue_choose_from_green(gs, cards_db, kind=want_kind, n=remaining_picks,
                                       group=str(p.get('want_group', '') or ''),
                                       ctx={'source_cn': str(p.get('source_cn', '') or ''), 'auto_effect_detail': str(p.get('auto_effect_detail', '') or '')},
                                       allow_less=bool(p.get('allow_skip', False) or p.get('allow_less', False) or p.get('optional', False)))
            return
        # resume parent prompt if provided (e.g., choose_effects)
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return
    if kind == 'choose_card_from_green':
        allow_skip = bool(p.get('allow_skip', False) or p.get('optional', False))
        low = choice_str.lower()
        if allow_skip and low in ('skip', '__skip__', 'no', 'n', '0', 'false', '使わない', 'いいえ', 'スキップ'):
            gs.log.append(f"[SKIP] choose_card_from_green: skipped")
            after_ext_key = str(p.get('after_ext_key', '') or '').strip()
            if after_ext_key:
                src = str(p.get('source_cn', '') or '')
                ctx2 = dict(p.get('ctx', {}) or {})
                if src and not ctx2.get('source_cn'):
                    ctx2['source_cn'] = src
                ctx2['choice'] = 'SKIP'
                ctx2['chosen_cn'] = 'SKIP'
                try:
                    rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
                except Exception:
                    rng2 = random.Random()
                _apply_effect_by_rule(gs, rng2, cards_db, {'op':'__ext__','ext_key':after_ext_key}, {}, ctx2)
            return
        cn = _canon_cardno(choice_str)
        candidates = list(p.get('candidates', []) or p.get('options', []) or [])
        pick_cn = None
        for x in list(gs.green_room):
            if _canon_cardno(x) == cn:
                if candidates and (not any(_canon_cardno(c) == cn for c in candidates)):
                    continue
                pick_cn = x
                break
        if not pick_cn:
            gs.log.append(f"[ERR] choose_card_from_green: not in waiting room {cn}")
            return
        after_ext_key = str(p.get('after_ext_key', '') or '').strip()
        if after_ext_key:
            src = str(p.get('source_cn', '') or '')
            ctx2 = dict(p.get('ctx', {}) or {})
            if src and not ctx2.get('source_cn'):
                ctx2['source_cn'] = src
            ctx2['choice'] = pick_cn
            ctx2['chosen_cn'] = pick_cn
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
            except Exception:
                rng2 = random.Random()
            try:
                _apply_effect_by_rule(gs, rng2, cards_db, {'op':'__ext__','ext_key':after_ext_key}, {}, ctx2)
                applied = True
            except Exception:
                applied = False
                raise
            finally:
                try:
                    gs.log.append(f"[AUTO] choose_card_from_green -> {'applied' if applied else 'error'} {after_ext_key} ({pick_cn})")
                except Exception:
                    pass
            _r = p.get('_resume') if isinstance(p, dict) else None
            if _r:
                gs.pending.append(_r)
            return
        gs.green_room.remove(pick_cn)
        gs.hand.append(pick_cn)
        gs.log.append(f"[ACT] retrieved CARD {pick_cn} -> hand")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return
    if kind == 'live_storage_to_deck_top_or_bottom':
        raw = str(choice_str or '').strip()
        low = raw.lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false', '使わない', 'いいえ', 'スキップ'):
            try:
                key0 = str(p.get('trigger_key', '') or '')
                if key0:
                    used = set(getattr(gs, 'once_used', set()) or set())
                    used.add(key0)
                    gs.once_used = used
            except Exception:
                pass
            gs.log.append('[SKIP] live_storage_to_deck_top_or_bottom: skipped')
            return
        cn = _canon_cardno(raw)
        cands = [_canon_cardno(x) for x in list(p.get('candidate_lives', []) or [])]
        if cn not in cands:
            gs.log.append(f'[ERR] live_storage_to_deck_top_or_bottom: invalid live {cn}')
            gs.pending.insert(0, p)
            return
        pick_cn = None
        for x in list(getattr(gs, 'set_zone', []) or []):
            if _canon_cardno(x) == cn:
                pick_cn = x
                break
        if not pick_cn:
            gs.log.append(f'[ERR] live_storage_to_deck_top_or_bottom: not in live storage {cn}')
            gs.pending.insert(0, p)
            return
        gs.pending.append({
            'kind': 'choose_deck_top_or_bottom_for_live_storage_card',
            'text': f'{pick_cn}: デッキの一番上か一番下に置く',
            'options': ['top', 'bottom'],
            'selected_cn': pick_cn,
            'source_cn': str(p.get('source_cn', '') or ''),
            'trigger_key': str(p.get('trigger_key', '') or ''),
        })
        gs.log.append(f'[PENDING] live_storage_to_deck_top_or_bottom: selected {pick_cn}; choose top/bottom')
        return
    if kind == 'choose_deck_top_or_bottom_for_live_storage_card':
        cn = _canon_cardno(str(p.get('selected_cn', '') or ''))
        dest = str(choice_str or '').strip().lower()
        if dest not in ('top', 'bottom'):
            gs.log.append(f'[ERR] live_storage top/bottom: invalid destination {choice_str}')
            return
        pick_cn = None
        for x in list(getattr(gs, 'set_zone', []) or []):
            if _canon_cardno(x) == cn:
                pick_cn = x
                break
        if not pick_cn:
            gs.log.append(f'[ERR] live_storage top/bottom: selected card not in live storage {cn}')
            return
        try:
            gs.set_zone.remove(pick_cn)
        except Exception:
            pass
        if dest == 'top':
            gs.deck.insert(0, pick_cn)
        else:
            gs.deck.append(pick_cn)
        try:
            key0 = str(p.get('trigger_key', '') or '')
            if key0:
                used = set(getattr(gs, 'once_used', set()) or set())
                used.add(key0)
                gs.once_used = used
        except Exception:
            pass
        gs.log.append(f'[ACT] live_storage_to_deck_top_or_bottom: {pick_cn} -> deck {dest} instead of waiting room')
        return
    if kind == 'hand_to_deck_top_or_bottom':
        rem = int(p.get('remaining', 0) or 0)
        if rem <= 0:
            return
        cn = _canon_cardno(choice_str)
        pick_i = None
        for i, hcn in enumerate(list(gs.hand)):
            if _canon_cardno(hcn) == cn:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f'[ERR] hand_to_deck_top_or_bottom: chosen not in hand {cn}')
            return
        gs.pending.append({
            'kind': 'choose_deck_top_or_bottom_for_hand_card',
            'text': f'{cn}: デッキの一番上か一番下に置く',
            'options': ['top', 'bottom'],
            'selected_cn': cn,
            'remaining': rem,
            'picked': list(p.get('picked', []) or []),
            'want_kind': str(p.get('want_kind', 'ANY') or 'ANY'),
            'want_group': str(p.get('want_group', '') or ''),
            'after_gain_blade': int(p.get('after_gain_blade', 0) or 0),
            'source_cn': str(p.get('source_cn', '') or ''),
        })
        gs.log.append(f'[PENDING] hand_to_deck_top_or_bottom: selected {cn}; choose top/bottom')
        return
    if kind == 'choose_deck_top_or_bottom_for_hand_card':
        cn = _canon_cardno(str(p.get('selected_cn', '') or ''))
        dest = str(choice_str or '').strip().lower()
        if dest not in ('top', 'bottom'):
            gs.log.append(f'[ERR] choose_deck_top_or_bottom: invalid destination {choice_str}')
            return
        pick_i = None
        for i, hcn in enumerate(list(gs.hand)):
            if _canon_cardno(hcn) == cn:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f'[ERR] choose_deck_top_or_bottom: selected card not in hand {cn}')
            return
        moved = gs.hand.pop(pick_i)
        if dest == 'top':
            gs.deck.insert(0, moved)
        else:
            gs.deck.append(moved)
        picked = list(p.get('picked', []) or []) + [moved]
        rem = int(p.get('remaining', 0) or 0) - 1
        gs.log.append(f'[ACT] hand_to_deck_top_or_bottom: {moved} -> deck {dest} (remaining={rem})')
        if rem > 0:
            kind_need = str(p.get('want_kind', 'ANY') or 'ANY')
            group_need = str(p.get('want_group', '') or '')
            cands = _hand_candidates_by_kind(gs, cards_db, kind=kind_need, group=group_need)
            gs.pending.append({
                'kind': 'hand_to_deck_top_or_bottom',
                'text': str(p.get('text', '') or f'手札からデッキの一番上か一番下に置くカードを選ぶ（残り{rem}）'),
                'options': list(cands),
                'remaining': rem,
                'picked': picked,
                'want_kind': kind_need,
                'want_group': group_need,
                'after_gain_blade': int(p.get('after_gain_blade', 0) or 0),
                'source_cn': str(p.get('source_cn', '') or ''),
            })
            return
        blade_gain = int(p.get('after_gain_blade', 0) or 0)
        src_cn = str(p.get('source_cn', '') or '')
        if blade_gain > 0:
            pos = ''
            for pp in ('L', 'C', 'R'):
                slot0 = gs.stage.get(pp)
                if slot0 and _canon_cardno(getattr(slot0, 'cardnumber', '') or '') == _canon_cardno(src_cn):
                    pos = pp
                    break
            slot = gs.stage.get(pos) if pos else None
            if slot:
                slot.temp_blade += blade_gain
                slot.temp_until = 'end_of_live'
                gs.log.append(f'[AUTO] {src_cn}: after top/bottom cost -> {pos} temp blade +{blade_gain}')
            else:
                gs.log.append(f'[WARN] {src_cn}: after top/bottom cost blade +{blade_gain} skipped (source not on stage)')
        return
    if kind == 'hand_to_deck_bottom':
        rem = int(p.get('remaining', 0) or 0)
        if rem <= 0:
            return
        cn = _canon_cardno(choice_str)
        pick_i = None
        for i, hcn in enumerate(list(gs.hand)):
            if _canon_cardno(hcn) == cn:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f'[ERR] hand_to_deck_bottom: chosen not in hand {cn}')
            return
        moved = gs.hand.pop(pick_i)
        gs.deck.append(moved)
        picked = list(p.get('picked', []) or []) + [moved]
        rem -= 1
        gs.log.append(f'[ACT] hand_to_deck_bottom: {moved} -> deck bottom (remaining={rem})')
        if rem > 0:
            kind_need = str(p.get('want_kind', 'ANY') or 'ANY')
            group_need = str(p.get('want_group', '') or '')
            cands = _hand_candidates_by_kind(gs, cards_db, kind=kind_need, group=group_need)
            gs.pending.append({
                'kind': 'hand_to_deck_bottom',
                'text': str(p.get('text', '') or f'手札からデッキの一番下に置くカードを選ぶ（残り{rem}）'),
                'options': list(cands),
                'remaining': rem,
                'picked': picked,
                'want_kind': kind_need,
                'want_group': group_need,
                'after_effect_template': str(p.get('after_effect_template', '') or ''),
                'after_ctx': dict(p.get('after_ctx', {}) or {}),
                'after_source_cn': str(p.get('after_source_cn', '') or ''),
            })
            return
        after_eff = str(p.get('after_effect_template', '') or '').strip()
        after_ctx = dict(p.get('after_ctx', {}) or {})
        after_src = str(p.get('after_source_cn', '') or '')
        after_ctx['bottomed_cns'] = list(picked)
        after_ctx['bottomed_count'] = len(picked)
        if after_eff:
            rng2 = random.Random(getattr(gs, 'seed', 1) or 1)
            ok = try_apply_effect_template(gs, rng2, cards_db, after_eff, after_ctx)
            gs.log.append(f"[ACT] {after_src}: after bottom cost -> {'applied' if ok else 'no_match'} {after_eff}")
        return
    if kind == 'choose_player_for_green_bottom':
        choice_low = str(choice_str or '').strip().lower()
        kind_need = str(p.get('want_kind', 'ANY') or 'ANY').upper()
        n = int(p.get('remaining', p.get('n', 1)) or 1)
        allow_less = bool(p.get('allow_less', False) or p.get('allow_skip', False))
        draw_after_n = int(p.get('draw_after_n', 0) or 0)
        src_cn = str(p.get('source_cn', '') or '')
        if choice_low in ('self', 'me', 'own', 'you', '自分'):
            gs.log.append(f'[ACT] choose player: self -> bottomdeck own {kind_need} x{n}')
            # For effects that say "好きな順番でデッキの一番下に置く", use the
            # ordered multi-select template rather than one-card-at-a-time prompts.
            # The resolver for choose_member_from_green_multi_up_to preserves the
            # comma-separated click order, and action=deck_bottom appends in that order
            # (first choice is the upper card among the returned bottom stack).
            if kind_need == 'MEMBER' and n > 1 and allow_less and draw_after_n <= 0:
                cands = _green_candidates_for_kind(gs, cards_db, kind=kind_need, group='')
                if not cands:
                    gs.log.append('[INFO] choose_player_green_bottom: no own MEMBER candidates in waiting room')
                    return
                gs.pending.append({
                    'kind': 'choose_member_from_green_multi_up_to',
                    'text': f'控え室のメンバーカードを{n}枚まで、好きな順番でデッキの一番下に置く（クリック順：1枚目=上側、最後=一番下）',
                    'options': list(cands),
                    'max_picks': n,
                    'min_picks': 0,
                    'action': 'deck_bottom',
                    'source_zone': 'green',
                    'ordered': True,
                    'order_hint': 'deck_bottom_top_to_bottom',
                })
                gs.log.append(f'[PENDING] choose player self -> ordered bottomdeck own MEMBER up to {n} (cands={len(cands)})')
                return
            _enqueue_bottomdeck_from_green(gs, cards_db, kind=kind_need, n=n, allow_less=allow_less, after_draw_n=draw_after_n, source_cn=src_cn)
            return
        if choice_low in ('opponent', 'opp', 'other', '相手'):
            jp = {'LIVE': 'ライブ', 'MEMBER': 'メンバー', 'ANY': 'カード'}.get(kind_need, kind_need)
            if draw_after_n > 0:
                opts = ['draw', 'no_draw']
                text = f'【相手への効果】相手の控え室にある{jp}カードを{n}枚、相手のデッキの一番下に置く。置いた場合は「引く」を押してください。'
            else:
                opts = ['ok']
                text = f'【相手への効果】相手の控え室にある{jp}カードを{n}枚' + ('まで' if allow_less else '') + '、相手のデッキの一番下に置く。'
            gs.pending.append({
                'kind': 'manual_opponent_green_bottom_notify',
                'text': text,
                'options': opts,
                'draw_after_n': draw_after_n,
                'source_cn': src_cn,
            })
            gs.log.append(f'[MANUAL] opponent green -> deck bottom: kind={kind_need} n={n} draw_after={draw_after_n}')
            return
        gs.log.append(f'[ERR] choose_player_for_green_bottom: invalid choice {choice_str}')
        return
    if kind == 'choose_player_for_deck_top_action':
        choice_low = str(choice_str or '').strip().lower()
        action = str(p.get('action', '') or '')
        k = max(1, int(p.get('k', 1) or 1))
        src_cn = str(p.get('source_cn', '') or '')
        if choice_low in ('self', 'me', 'own', 'you', '自分'):
            if action == 'top1_optional_green':
                if not gs.deck:
                    gs.log.append('[INFO] choose_player deck-top: own deck empty')
                    return
                top_cn = gs.deck[0]
                gs.pending.append({
                    'kind': 'self_top1_to_green_or_keep',
                    'text': '自分のデッキの一番上のカードを確認。控え室に置くか、デッキ上に残すか選んでください。',
                    'options': ['green', 'keep'],
                    'top_cn': top_cn,
                    'source_cn': src_cn,
                })
                gs.log.append(f'[PENDING] choose player self -> view top1 {top_cn}; choose green/keep')
                return
            if action == 'topk_reorder_keep_any':
                gs.log.append(f'[ACT] choose player: self -> reorder own top {k} keep-any')
                _enqueue_reorder_from_topk_keep_any(gs, k, rng)
                return
            gs.log.append(f'[ERR] choose_player deck-top: unsupported action {action}')
            return
        if choice_low in ('opponent', 'opp', 'other', '相手'):
            if action == 'top1_optional_green':
                text2 = '【相手への効果】相手のデッキの一番上のカードを見ます。そのカードを控え室に置いてもよいです。'
            elif action == 'topk_reorder_keep_any':
                text2 = f'【相手への効果】相手のデッキの上からカードを{k}枚見ます。その中から好きな枚数を好きな順番でデッキの上に置き、残りを控え室に置きます。'
            else:
                text2 = f'【相手への効果】未対応のデッキ上処理です: {action}'
            gs.pending.append({
                'kind': 'manual_opponent_deck_top_action_notify',
                'text': text2,
                'options': ['ok'],
                'source_cn': src_cn,
            })
            gs.log.append(f'[MANUAL] opponent deck-top action: action={action} k={k}')
            return
        gs.log.append(f'[ERR] choose_player_for_deck_top_action: invalid choice {choice_str}')
        return
    if kind == 'self_top1_to_green_or_keep':
        low = str(choice_str or '').strip().lower()
        top_cn = _canon_cardno(str(p.get('top_cn', '') or ''))
        if not gs.deck:
            gs.log.append('[ERR] self_top1_to_green_or_keep: deck empty')
            return
        actual = _canon_cardno(gs.deck[0])
        if top_cn and actual != top_cn:
            gs.log.append(f'[WARN] self_top1_to_green_or_keep: top changed expected={top_cn} actual={actual}')
        if low in ('green', 'waiting', 'wait', '控え室'):
            moved = gs.deck.pop(0)
            gs.green_room.append(moved)
            gs.log.append(f'[ACT] viewed own deck top -> waiting room {moved}')
            return
        if low in ('keep', 'top', 'deck', '残す', 'デッキ上'):
            gs.log.append(f'[ACT] viewed own deck top -> kept on top {gs.deck[0]}')
            return
        gs.log.append(f'[ERR] self_top1_to_green_or_keep: invalid choice {choice_str}')
        return
    if kind == 'manual_opponent_deck_top_action_notify':
        gs.log.append('[MANUAL] opponent deck-top action notification closed')
        return
    if kind == 'manual_opponent_green_bottom_notify':
        low = str(choice_str or '').strip().lower()
        draw_n = int(p.get('draw_after_n', 0) or 0)
        if low == 'draw' and draw_n > 0:
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
            except Exception:
                rng2 = random.Random()
            got = draw(gs, draw_n, rng2)
            gs.log.append(f'[MANUAL] opponent bottomdeck resolved -> draw {draw_n} (drew {got})')
            return
        gs.log.append('[MANUAL] opponent bottomdeck notification closed')
        return
    if kind == 'bottomdeck_from_green':
        low = str(choice_str or '').strip().lower()
        allow_less = bool(p.get('allow_less', False) or p.get('allow_skip', False))
        if allow_less and low in ('skip', '__skip__', 'no', 'n', '0', 'false', 'スキップ'):
            gs.log.append('[SKIP] bottomdeck_from_green: done')
            return
        rem = int(p.get('remaining', 0) or 0)
        cn = _canon_cardno(choice_str)
        opts = [_canon_cardno(x) for x in list(p.get('options', []) or [])]
        if opts and cn not in opts:
            gs.log.append(f'[ERR] bottomdeck_from_green: invalid choice {choice_str}')
            return
        pick_i = None
        for i, gcn in enumerate(list(gs.green_room)):
            if _canon_cardno(gcn) == cn:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f'[ERR] bottomdeck_from_green: chosen not in waiting room {cn}')
            return
        moved = gs.green_room.pop(pick_i)
        gs.deck.append(moved)
        picked = list(p.get('picked', []) or []) + [moved]
        rem -= 1
        gs.log.append(f'[ACT] bottomdeck_from_green: {moved} -> deck bottom (remaining={rem})')
        if rem > 0:
            kind_need = str(p.get('want_kind', 'ANY') or 'ANY')
            group_need = str(p.get('want_group', '') or '')
            cands = _green_candidates_for_kind(gs, cards_db, kind=kind_need, group=group_need)
            if cands:
                gs.pending.append({
                    'kind': 'bottomdeck_from_green',
                    'text': str(p.get('text', '') or f'控え室からデッキの一番下に置くカードを選ぶ（残り{rem}）'),
                    'options': (['skip'] + list(cands)) if allow_less else list(cands),
                    'remaining': rem,
                    'picked': picked,
                    'want_kind': kind_need,
                    'want_group': group_need,
                    'allow_less': allow_less,
                    'allow_skip': allow_less,
                    'after_draw_n': int(p.get('after_draw_n', 0) or 0),
                    'source_cn': str(p.get('source_cn', '') or ''),
                })
            return
        after_draw_n = int(p.get('after_draw_n', 0) or 0)
        if after_draw_n > 0 and len(picked) > 0:
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
            except Exception:
                rng2 = random.Random()
            got = draw(gs, after_draw_n, rng2)
            src_cn = str(p.get('source_cn', '') or '')
            gs.log.append(f'[AUTO] {src_cn}: bottomdeck_from_green moved {len(picked)} -> draw {after_draw_n} (drew {got})')
        return
    if kind == 'view_topk_no_match':
        # User confirmed viewing the pool; send all to green room
        pool = list(p.get('pool', []) or [])
        gs.green_room.extend(pool)
        gs.log.append(f'[ACT] view_topk_no_match: confirmed -> {len(pool)} cards to waiting room')
        return
    if kind == 'choose_from_topk':
        pool = list(p.get('pool', []) or [])
        if not pool:
            gs.log.append('[ERR] topk: pool missing')
            return
        optional = bool(p.get('optional', False))
        # skip: put all pool cards to waiting room
        if choice_str.strip().lower() in ('skip', 'スキップ', '__skip__'):
            if optional:
                gs.green_room.extend(pool)
                gs.log.append(f'[ACT] topk: skip chosen -> {len(pool)} cards to waiting room')
            else:
                gs.log.append('[ERR] topk: skip not allowed (not optional)')
                gs.deck = pool + gs.deck
            return
        cn = _canon_cardno(choice_str)
        pick_idx = None
        candidates = list(p.get('candidates', pool) or pool)
        for i, x in enumerate(pool):
            if _canon_cardno(x) == cn:
                # validate against candidates if filtered
                if candidates and cn not in [_canon_cardno(c) for c in candidates]:
                    gs.log.append(f'[ERR] topk: {cn} not in filtered candidates')
                    gs.deck = pool + gs.deck
                    return
                pick_idx = i
                break
        if pick_idx is None:
            gs.log.append(f"[ERR] topk: invalid choice {cn}")
            gs.deck = pool + gs.deck
            return
        pick_cn = pool.pop(pick_idx)
        gs.hand.append(pick_cn)
        gs.green_room.extend(pool)
        gs.log.append(f"[ACT] topk chose {pick_cn} -> hand; rest {len(pool)} -> waiting room")
        return
    if kind == 'look_top_3way_step':
        pool = list(p.get('pool', []) or [])
        step = str(p.get('step', 'hand') or 'hand')
        if not pool:
            gs.log.append('[ERR] look_top_3way: pool missing')
            return
        cn = _canon_cardno(choice_str)
        match_idx = None
        for i, x in enumerate(pool):
            if _canon_cardno(x) == cn:
                match_idx = i
                break
        if match_idx is None:
            gs.log.append(f'[ERR] look_top_3way: {cn} not in pool {pool}')
            gs.deck = pool + gs.deck
            return
        picked = pool.pop(match_idx)
        if step == 'hand':
            gs.hand.append(picked)
            gs.log.append(f'[ACT] look_top_3way: {picked} -> hand')
            if len(pool) >= 2:
                remaining = list(pool)
                gs.pending.append({
                    'kind': 'look_top_3way_step',
                    'text': f'残り{len(remaining)}枚からデッキ上に置く1枚を選ぶ（残りは控え室）',
                    'options': remaining,
                    'pool': remaining,
                    'step': 'topdeck',
                    'picked_hand': picked,
                    'picked_top': '',
                })
            else:
                # only 1 left -> goes to deck top, none to green
                if pool:
                    gs.deck.insert(0, pool[0])
                    gs.log.append(f'[AUTO] look_top_3way: {pool[0]} -> deck top (only card left)')
        elif step == 'topdeck':
            gs.deck.insert(0, picked)
            gs.log.append(f'[ACT] look_top_3way: {picked} -> deck top')
            gs.green_room.extend(pool)
            gs.log.append(f'[AUTO] look_top_3way: {pool} -> waiting room')
        return
    if kind == 'named_cards_cost_multi':
        total = int(p.get('total', 0) or 0)
        options = list(p.get('options', []) or [])
        resume_eff = str(p.get('resume_effect', '') or '')
        resume_pos = str(p.get('resume_pos', '') or '')
        resume_src = str(p.get('resume_source_cn', '') or '')
        # choice_str はカンマ区切りの cardnumber リスト（server.py から送信）
        raw_picks = [s.strip() for s in choice_str.split(',')
                     if s.strip() and s.strip().lower() not in ('__done__', 'done', 'skip')]
        if len(raw_picks) != total:
            gs.log.append(f"[ERR] named_cards_cost_multi: 枚数不一致（必要{total}枚、選択{len(raw_picks)}枚）")
            gs.pending.insert(0, p)  # 再度選択させる
            return
        picks_canon = [_canon_cardno(x) for x in raw_picks]
        green_copy = list(gs.green_room)
        picked = []
        ok = True
        for cn in picks_canon:
            found = False
            for i, gcn in enumerate(green_copy):
                if _canon_cardno(gcn) == cn and gcn in options:
                    picked.append(green_copy.pop(i))
                    found = True
                    break
            if not found:
                gs.log.append(f"[ERR] named_cards_cost_multi: {cn} が控え室/選択肢に見つからない")
                ok = False
                break
        if not ok:
            return
        gs.green_room = green_copy
        rng_local = random.Random(gs.seed)
        rng_local.shuffle(picked)
        gs.deck = gs.deck + picked
        gs.log.append(f"[COST] named_cards_cost_multi: {picked} → デッキ下（シャッフル済）")
        if resume_eff:
            ctx = {'pos': resume_pos, 'source_cn': resume_src}
            matched = try_apply_effect_template(gs, rng, cards_db, resume_eff, ctx)
            if not matched:
                gs.log.append(f"[WARN] named_cards_cost_multi: 効果テンプレート非対応: {resume_eff}")
        return
    if kind == 'topdeck_from_green':
        rem = _safe_int(p.get('remaining', 0), 0)
        picked = list(p.get('picked', []) or [])
        want_kind = str(p.get('want_kind', '') or '').upper()
        want_group = str(p.get('want_group', '') or '')
        allow_less = bool(p.get('allow_less', False))
        low = choice_str.lower()
        if allow_less and low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            if picked:
                # picked list is already in desired top order
                gs.deck = picked + gs.deck
                gs.log.append(f"[ACT] topdeck_from_green: placed {len(picked)} on top (early finish)")
            else:
                gs.log.append("[SKIP] topdeck_from_green: picked 0")
            return
        # pick card in waiting room (allow variants)
        cn = _canon_cardno(choice_str)
        pick_i = None
        for i, x in enumerate(list(gs.green_room)):
            if _canon_cardno(x) == cn:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f"[ERR] topdeck_from_green: chosen not in waiting room {cn}")
            # restore picked back to waiting room (best effort)
            if picked:
                gs.green_room.extend(picked)
            return
        pick_cn = gs.green_room.pop(pick_i)
        ci2 = _get_card(cards_db, pick_cn)
        if want_kind == 'LIVE' and not _is_live_ci(ci2):
            gs.log.append(f"[ERR] topdeck_from_green: not LIVE {pick_cn}")
            gs.green_room.append(pick_cn)
            if picked:
                gs.green_room.extend(picked)
            return
        if want_kind == 'MEMBER' and not _is_member_ci(ci2):
            gs.log.append(f"[ERR] topdeck_from_green: not MEMBER {pick_cn}")
            gs.green_room.append(pick_cn)
            if picked:
                gs.green_room.extend(picked)
            return
        # want_kind == 'ANY': no type check
        if want_group and not _ci_matches_group_or_unit(ci2, want_group):
            gs.log.append(f"[ERR] topdeck_from_green: group/unit mismatch {pick_cn} for {want_group}")
            gs.green_room.append(pick_cn)
            if picked:
                gs.green_room.extend(picked)
            return
        picked.append(pick_cn)
        rem -= 1
        if rem <= 0:
            gs.deck = picked + gs.deck
            gs.log.append(f"[ACT] topdeck_from_green: placed {len(picked)} on top")
            return
        # rebuild candidates
        cands: List[str] = []
        for x in list(gs.green_room):
            ci = _get_card(cards_db, x)
            if not ci:
                continue
            if want_kind == 'LIVE' and not _is_live_ci(ci):
                continue
            if want_kind == 'MEMBER' and not _is_member_ci(ci):
                continue
            # want_kind == 'ANY': no type filter
            if want_group and not _ci_matches_group_or_unit(ci, want_group):
                continue
            cands.append(x)
        if not cands:
            # no more candidates; finalize with what we have
            gs.deck = picked + gs.deck
            gs.log.append(f"[ACT] topdeck_from_green: candidates exhausted; placed {len(picked)} on top")
            return
        opts = list(cands) + (['skip'] if allow_less else [])
        gs.pending.append({
            'kind': 'topdeck_from_green',
            'text': f'控え室の{want_kind}をデッキ上に置く（残り{rem}枚）/ skipで終了' if allow_less else f'控え室の{want_kind}をデッキ上に置く（残り{rem}枚）',
            'options': opts,
            'remaining': rem,
            'picked': picked,
            'want_kind': want_kind,
            'want_group': want_group,
            'allow_less': allow_less,
        })
        gs.log.append(f"[PENDING] topdeck_from_green: picked {pick_cn}; remaining {rem}")
        return
    if kind == 'reorder_topk_keep_any':
        pool = list(p.get('pool', []) or [])
        kept = list(p.get('kept', []) or [])
        if not pool and not kept:
            gs.log.append('[ERR] reorder_topk: state missing')
            return
        low = choice_str.lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            # finalize early
            if pool:
                gs.green_room.extend(pool)
            if kept:
                gs.deck = kept + gs.deck
            gs.log.append(f"[ACT] reorder_topk: kept {len(kept)} on top; rest {len(pool)} -> waiting room")
            return
        cn = _canon_cardno(choice_str)
        pick_idx = None
        for i, x in enumerate(pool):
            if _canon_cardno(x) == cn:
                pick_idx = i
                break
        if pick_idx is None:
            gs.log.append(f"[ERR] reorder_topk: invalid choice {cn}")
            # best-effort restore
            gs.deck = kept + pool + gs.deck
            return
        pick_cn = pool.pop(pick_idx)
        kept.append(pick_cn)
        if not pool:
            # done
            gs.deck = kept + gs.deck
            gs.log.append(f"[ACT] reorder_topk: kept {len(kept)} on top; rest 0 -> waiting room")
            return
        # queue next pick
        opts = list(pool) + ['skip']
        gs.pending.append({
            'kind': 'reorder_topk_keep_any',
            'text': f'次にデッキ上に置くカードを選択（残り{len(pool)}枚）/ skipで終了',
            'options': opts,
            'pool': list(pool),
            'kept': list(kept),
            'allow_less': True,
        })
        gs.log.append(f"[PENDING] reorder_topk: picked {pick_cn}; remaining {len(pool)}")
        return
    if kind == 'optional_pay_energy_for_self_score_if_group':
        src_cn = _source_cn_or_default(p.get('cn', ''), 'この能力')
        group_name = str(p.get('condition_group_name', '') or '虹ヶ咲')
        low = str(choice_str or '').strip().lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append(f'[SKIP] {src_cn} live-start skipped')
            return
        if low not in ('pay', 'yes', 'y', '1', 'true'):
            gs.log.append(f'[ERR] {src_cn} live-start: invalid choice {choice_str}')
            return
        if int(getattr(gs, 'energy_active', 0) or 0) < 2:
            gs.log.append(f'[SKIP] {src_cn} live-start unresolved (not enough active energy at resolution)')
            return
        if not _has_group_member_on_stage(gs, cards_db, group_name):
            gs.log.append(f'[SKIP] {src_cn} live-start unresolved (no {group_name} member at resolution)')
            return
        if not pay_energy(gs, 2):
            gs.log.append(f'[SKIP] {src_cn} live-start unresolved (not enough active energy at resolution)')
            return
        _add_live_start_score_bonus(gs, 1, set_idx=p.get('set_idx', None), source_cn=src_cn)
        gs.log.append(f'[AUTO] {src_cn} live-start: paid E2 -> score +1')
        return
    if kind == 'execute_draw_then_choose_hand_cards_ordered_topdeck':
        drew = draw(gs, 3, None)
        gs.log.append(f'[AUTO] NEO SKY, NEO MAP!: drew {drew}')
        opts = list(gs.hand)
        if not opts:
            gs.log.append('[INFO] NEO SKY, NEO MAP!: hand empty after draw')
            return
        if len(opts) <= 3:
            picked = list(opts)
            gs.hand = []
            gs.deck = picked + gs.deck
            gs.log.append(f'[ACT] NEO SKY, NEO MAP!: placed {len(picked)} on top (auto)')
            return
        gs.pending.append({
            'kind': 'choose_hand_cards_ordered_topdeck',
            'text': 'NEO SKY, NEO MAP!：手札から3枚を選び、クリックした順にデッキの上へ置く（1枚目が一番上）',
            'options': opts,
            'min_picks': 3,
            'max_picks': 3,
            'label': 'NEO SKY, NEO MAP!',
        })
        gs.log.append('[PENDING] choose_hand_cards_ordered_topdeck hand=3 (NEO SKY, NEO MAP!)')
        return
    if kind == 'opponent_wait_notify':
        # 相手ウェイト効果：実際にウェイト状態にした人数を記録し、参照効果に使う。
        try:
            n = int(str(choice_str or '0').strip())
        except Exception:
            n = -1
        max_delta = max(0, min(3, int(p.get('max_delta', 3) or 3)))
        if n < 0 or n > max_delta:
            gs.log.append(f'[ERR] opponent_wait_notify: invalid count {choice_str}')
            gs.pending.append(p)
            return
        before = _opponent_wait_count(gs)
        after = _add_opponent_wait_count(gs, n)
        gs.log.append(f'[ACK] opponent_wait_notify: opponent_wait_count {before} +{n} -> {after}')
        _enqueue_auto_order_from_deferred()
        return
    if kind == 'message_ack':
        gs.log.append(f"[ACK] {str(p.get('label', p.get('text', 'message'))) }")
        return
    if kind == 'body_reveal_pick_live':
        pool = list(p.get('pool', []) or [])
        live_cands = list(p.get('live_cands', []) or [])
        cn_src = str(p.get('cn', '') or '')
        chosen = _canon_cardno(str(choice_str or ''))
        # pool をデッキから除去
        deck_copy = list(gs.deck)
        for c2 in pool:
            try:
                deck_copy.remove(c2)
            except ValueError:
                pass
        gs.deck = deck_copy
        if choice_str.lower() in ('skip', '__skip__', 'no', '0', 'false'):
            # スキップ: 全て控え室
            for c2 in pool:
                gs.green_room.append(c2)
            gs.log.append(f'[SKIP] {cn_src}[BODY]: 全て控え室 {pool}')
            return
        # 選択されたカードが候補にあるか確認
        matched = None
        for c2 in live_cands:
            if _canon_cardno(c2) == chosen:
                matched = c2
                break
        if not matched:
            gs.log.append(f'[ERR] {cn_src}[BODY]: {chosen} not in live_cands {live_cands}')
            # エラー時は全て控え室
            for c2 in pool:
                gs.green_room.append(c2)
            return
        # 選択カードを手札へ、残りを控え室へ
        gs.hand.append(matched)
        rest = [c2 for c2 in pool if _canon_cardno(c2) != _canon_cardno(matched)]
        for c2 in rest:
            gs.green_room.append(c2)
        gs.log.append(f'[ACT] {cn_src}[BODY]: {matched} -> hand, rest -> green {rest}')
        return
    if kind == 'choose_hand_cards_ordered_topdeck':
        picks = [str(x).strip() for x in str(choice_str or '').split(',') if str(x).strip()]
        min_picks = int(p.get('min_picks', 0) or 0)
        max_picks = int(p.get('max_picks', 0) or 0)
        label = str(p.get('label', 'ordered_topdeck') or 'ordered_topdeck')
        if max_picks <= 0:
            gs.log.append(f'[ERR] choose_hand_cards_ordered_topdeck: invalid max_picks {max_picks}')
            return
        if len(picks) < min_picks or len(picks) > max_picks:
            gs.log.append(f'[ERR] choose_hand_cards_ordered_topdeck: invalid pick count {len(picks)} expected {min_picks}..{max_picks}')
            gs.pending.insert(0, p)
            return
        hand_copy = list(getattr(gs, 'hand', []) or [])
        picked = []
        for cn in picks:
            if cn not in hand_copy:
                gs.log.append(f'[ERR] choose_hand_cards_ordered_topdeck: chosen not in hand {cn}')
                gs.pending.insert(0, p)
                return
            hand_copy.remove(cn)
            picked.append(cn)
        gs.hand = hand_copy
        gs.deck = list(picked) + list(getattr(gs, 'deck', []) or [])
        gs.log.append(f'[ACT] choose_hand_cards_ordered_topdeck: placed {len(picked)} on top ({label})')
        return
    if kind == 'topdeck_from_hand':
        rem = int(p.get('remaining', 0) or 0)
        picked = list(p.get('picked', []) or [])
        label = str(p.get('label', '') or '')
        cn = _canon_cardno(choice_str)
        pick_i = None
        for i, x in enumerate(list(gs.hand)):
            if _canon_cardno(x) == cn:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f'[ERR] topdeck_from_hand: chosen not in hand {cn}')
            return
        pick_cn = gs.hand.pop(pick_i)
        picked.append(pick_cn)
        rem -= 1
        if rem <= 0:
            gs.deck = picked + gs.deck
            gs.log.append(f'[ACT] topdeck_from_hand: placed {len(picked)} on top ({label})')
            return
        opts = list(gs.hand)
        if not opts:
            gs.deck = picked + gs.deck
            gs.log.append(f'[ACT] topdeck_from_hand: hand exhausted; placed {len(picked)} on top ({label})')
            return
        prompt = {
            'kind': 'topdeck_from_hand',
            'text': f'{label} 次にデッキ上に置くカードを選択（残り{rem}枚）',
            'options': opts,
            'remaining': rem,
            'picked': picked,
            'label': label,
        }
        try:
            gs.pending.insert(0, prompt)
        except Exception:
            gs.pending.append(prompt)
        gs.log.append(f'[PENDING] topdeck_from_hand picked {pick_cn}; remaining {rem} ({label})')
        return
    if kind == 'execute_top_keep_one_then_reveal_top_score_if_live':
        k = int(p.get('k', 0) or 0)
        followup_ops = [
            {
                'op': 'if_revealed_is_live',
                'cards_from': 'revealed_top',
                'then': [
                    {
                        'op': 'add_live_score',
                        'delta': 1,
                        'source_cn': str(p.get('cn', '') or ''),
                        'set_idx': p.get('set_idx', None),
                    }
                ],
            },
            {
                'op': 'show_cards_ack',
                'label': 'ツナガルコネクト 公開カード確認',
                'text': 'ツナガルコネクトで公開されたカードを確認',
                'cards_from': 'revealed_top',
            },
        ]
        _enqueue_choose_top_keep_one(
            gs,
            k,
            'ツナガルコネクト',
            source_cn=str(p.get('cn', '') or ''),
            set_idx=p.get('set_idx', None),
            followup_ops=followup_ops,
        )
        return
    if kind == 'choose_top_keep_one':
        ok = _resolve_choose_top_keep_one(gs, p, choice_str, cards_db)
        if not ok:
            return
        return
    if kind == 'confirm_mass_green_members_to_bottom':
        low = str(choice_str or '').strip().lower()
        src = str(p.get('source_cn', '') or '')
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false', 'cancel', '使わない', 'いいえ', 'スキップ'):
            gs.log.append(f'[SKIP] {src}: optional mass bottom skipped')
            return
        if low not in ('apply', 'yes', 'y', '1', 'true', 'use', 'do', 'go', 'ok', 'confirm', '使う', 'はい'):
            gs.log.append(f'[ERR] confirm_mass_green_members_to_bottom: invalid choice {choice_str}')
            gs.pending.append(p)
            return
        try:
            rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
        except Exception:
            rng2 = random.Random()
        moved = _move_all_green_members_to_deck_bottom_shuffled(gs, cards_db, rng2)
        threshold_group = str(p.get('threshold_group', '') or '')
        threshold_n = int(p.get('threshold_n', 0) or 0)
        target_name = str(p.get('target_name', '') or '')
        blade_n = int(p.get('blade_n', 0) or 0)
        group_n = 0
        for _cn in list(moved or []):
            _ci = _get_card(cards_db, _cn)
            if _ci and _ci_matches_group_or_unit(_ci, threshold_group):
                group_n += 1
        gs.log.append(f'[ACT] {src}: waiting-room MEMBER all -> deck bottom shuffled ({len(moved)}); {threshold_group}={group_n}/{threshold_n}')
        gs.pending.append({
            'kind': 'mass_bottom_optional_result_ack',
            'text': (
                f'{src} の効果処理結果を確認してください。\n'
                f'自分の控え室からメンバーカード{len(moved)}枚をシャッフルしてデッキ下に戻しました。\n'
                f'そのうち『{threshold_group}』のカード：{group_n}枚 / 必要 {threshold_n}枚です。\n'
                f'条件{"達成" if group_n >= threshold_n else "未達"}です。'
            ),
            'options': ['ok'],
            'moved_cns': list(moved or []),
            'moved_n': len(moved),
            'group_moved_n': int(group_n),
            'threshold_group': threshold_group,
            'threshold_n': threshold_n,
            'target_name': target_name,
            'blade_n': blade_n,
            'source_cn': src,
        })
        gs.log.append(f'[PENDING] {src}: mass bottom optional result confirmation moved={len(moved)} group={group_n}/{threshold_n}')
        return
    if kind == 'mass_bottom_optional_result_ack':
        low = str(choice_str or '').strip().lower()
        src = str(p.get('source_cn', '') or '')
        if low not in ('ok', 'confirm', 'apply', 'yes', 'y', '1', 'true', '確認', 'はい'):
            gs.log.append(f'[ERR] mass_bottom_optional_result_ack: invalid choice {choice_str}')
            gs.pending.append(p)
            return
        _resolve_mass_green_member_threshold_stage_blade(
            gs, cards_db, list(p.get('moved_cns', []) or []),
            str(p.get('threshold_group', '') or ''),
            int(p.get('threshold_n', 0) or 0),
            str(p.get('target_name', '') or ''),
            int(p.get('blade_n', 0) or 0),
            source_cn=src,
        )
        gs.log.append(f'[ACK] {src}: mass bottom optional result confirmed moved={int(p.get("moved_n", 0) or 0)} group={int(p.get("group_moved_n", 0) or 0)}/{int(p.get("threshold_n", 0) or 0)} -> followup')
        return
    if kind == 'mass_bottom_auto_ack':
        low = str(choice_str or '').strip().lower()
        src = str(p.get('source_cn', '') or '')
        if low not in ('ok', 'confirm', 'apply', 'yes', 'y', '1', 'true', '確認', 'はい'):
            gs.log.append(f'[ERR] mass_bottom_auto_ack: invalid choice {choice_str}')
            gs.pending.append(p)
            return
        _apply_mass_bottom_threshold_followup(
            gs, cards_db,
            str(p.get('source_pos', '') or '').upper(),
            src,
            int(p.get('retrieve_n', 1) or 1),
            int(p.get('blade_n', 0) or 0),
        )
        gs.log.append(f'[ACK] {src}: mass bottom auto confirmed own={int(p.get("own_moved_n", 0) or 0)}/{int(p.get("threshold_n", 0) or 0)} -> followup')
        return
    if kind == 'manual_opponent_mass_bottom_threshold':
        low = str(choice_str or '').strip().lower()
        src = str(p.get('source_cn', '') or '')
        if low in ('threshold_met', 'met', 'yes', 'y', '1', 'true', '達成', '条件達成'):
            _apply_mass_bottom_threshold_followup(
                gs, cards_db,
                str(p.get('source_pos', '') or '').upper(),
                src,
                int(p.get('retrieve_n', 1) or 1),
                int(p.get('blade_n', 0) or 0),
            )
            gs.log.append(f'[MANUAL] {src}: opponent mass bottom threshold met own={int(p.get("own_moved_n", 0) or 0)}/{int(p.get("threshold_n", 0) or 0)} -> followup')
            return
        if low in ('threshold_not_met', 'not_met', 'no', 'n', '0', 'false', '未達', '条件未達'):
            gs.log.append(f'[MANUAL] {src}: opponent mass bottom threshold not met own={int(p.get("own_moved_n", 0) or 0)}/{int(p.get("threshold_n", 0) or 0)} -> no followup')
            return
        gs.log.append(f'[ERR] manual_opponent_mass_bottom_threshold: invalid choice {choice_str}')
        gs.pending.append(p)
        return
    if kind == 'choose_stage_member_to_gain_icons':
        pos2 = str(choice_str or '').strip().upper()
        cand = [str(x).upper() for x in list(p.get('candidates', []) or []) if str(x).upper() in ('L','C','R')]
        if pos2 not in ('L','C','R') or (cand and pos2 not in cand):
            gs.log.append(f'[ERR] choose_stage_member_to_gain_icons: invalid target {choice_str}')
            gs.pending.append(p)
            return
        ok = _grant_stage_member_temp_icons(gs, cards_db, pos2, str(p.get('icons', '') or ''), source_cn=str(p.get('source_cn', '') or ''))
        if not ok:
            gs.log.append(f'[ERR] choose_stage_member_to_gain_icons: failed target {pos2}')
        return
    if kind == 'choose_stage_member_to_gain_blade':
        pos2 = str(choice_str or '').strip().upper()
        cand = [str(x).upper() for x in list(p.get('candidates', []) or []) if str(x).upper() in ('L','C','R')]
        if pos2 not in ('L','C','R') or (cand and pos2 not in cand):
            gs.log.append(f'[ERR] choose_stage_member_to_gain_blade: invalid target {choice_str}')
            gs.pending.append(p)
            return
        ok = _grant_stage_member_temp_blade(gs, cards_db, pos2, int(p.get('blade_n', 0) or 0), source_cn=str(p.get('source_cn', '') or ''))
        if not ok:
            gs.log.append(f'[ERR] choose_stage_member_to_gain_blade: failed target {pos2}')
        return
    if kind == 'choose_stage_member_to_wait':
        raw = str(choice_str or '').strip()
        pos2 = (raw[:1].upper() if raw else '')
        pos_opts = list(p.get('pos_options', []) or [])
        rem = _safe_int(p.get('remaining', 1), 1)
        after_eff = str(p.get('after_effect_template', '') or '').strip()
        after_ctx = dict(p.get('after_ctx', {}) or {})
        after_src = str(p.get('after_source_cn', '') or '')
        if pos2 not in ('L','C','R') or (pos_opts and pos2 not in pos_opts):
            gs.log.append(f"[ERR] choose_stage_member_to_wait: invalid target {choice_str}")
            return
        slot2 = (gs.stage or {}).get(pos2)
        if not slot2:
            gs.log.append(f"[ERR] choose_stage_member_to_wait: empty stage {pos2}")
            return
        slot2.active = False
        after_ctx['waited_pos'] = pos2
        try:
            after_ctx.setdefault('waited_positions', [])
            if pos2 not in after_ctx['waited_positions']:
                after_ctx['waited_positions'].append(pos2)
        except Exception:
            pass
        rem -= 1
        gs.log.append(f"[ACT] stage {pos2} set WAIT (remaining={rem})")
        if rem > 0:
            remain_opts = [pp for pp in pos_opts if pp != pos2]
            gs.pending.append({
                'kind': 'choose_stage_member_to_wait',
                'text': f'【起動効果】ウェイトにするメンバーをさらに選んでください（残り{rem}）',
                'options': [_stage_pos_label(gs, cards_db, pp) for pp in remain_opts],
                'pos_options': remain_opts,
                'remaining': rem,
                'after_effect_template': after_eff,
                'after_ctx': after_ctx,
                'after_source_cn': after_src,
            })
            return
        if after_eff:
            rng2 = random.Random(getattr(gs, 'seed', 1) or 1)
            ok = try_apply_effect_template(gs, rng2, cards_db, after_eff, after_ctx)
            if ok:
                gs.log.append(f"[ACT] {after_src}: applied {after_eff}")
            else:
                gs.log.append(f"[WARN] {after_src}: after-cost effect not matchable {after_eff}")
        return
    if kind == 'choose_stage_wait_member_activate_gain_blade':
        pos2 = str(choice_str or '').upper()
        cands = [str(x).upper() for x in list(p.get('candidates', []) or []) if str(x).upper() in ('L', 'C', 'R')]
        if pos2 not in ('L', 'C', 'R') or (cands and pos2 not in cands):
            gs.log.append(f"[ERR] activate_gain_blade: invalid pos {choice_str}")
            gs.pending.append(p)
            return
        slot2 = gs.stage.get(pos2)
        if not slot2:
            gs.log.append(f"[ERR] activate_gain_blade: empty {pos2}")
            gs.pending.append(p)
            return
        blade_n = int(p.get('blade_n', 1) or 1)
        slot2.active = True
        slot2.temp_blade = int(getattr(slot2, 'temp_blade', 0) or 0) + blade_n
        slot2.temp_until = 'end_of_live'
        gs.log.append(f"[ACT] stage {pos2} set ACTIVE and temp blade +{blade_n}")
        _enqueue_auto_order_from_deferred()
        return
    if kind == 'choose_stage_member_to_activate':
        # 汎用のステージメンバー選択 pending。
        # 既存用途: 選んだメンバーを ACTIVE 化。
        # 拡張用途: after_ext_key がある場合、選択結果を ctx に積んで ext resolver へ渡す。
        allow_skip = bool(p.get('allow_skip', False) or p.get('optional', False))
        low = choice_str.lower()
        if allow_skip and low in ('skip', '__skip__', 'no', 'n', '0', 'false', '使わない', 'いいえ', 'スキップ'):
            gs.log.append(f"[SKIP] choose_stage_member_to_activate: skipped")
            after_ext_key = str(p.get('after_ext_key', '') or '').strip()
            if after_ext_key:
                src = str(p.get('source_cn', '') or '')
                ctx2 = dict(p.get('ctx', {}) or {})
                if src and not ctx2.get('source_cn'):
                    ctx2['source_cn'] = src
                ctx2['choice'] = 'SKIP'
                ctx2['chosen_pos'] = 'SKIP'
                try:
                    rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
                except Exception:
                    rng2 = random.Random()
                _apply_effect_by_rule(gs, rng2, cards_db, {'op':'__ext__','ext_key':after_ext_key}, {}, ctx2)
            _enqueue_auto_order_from_deferred()
            return
        pos2 = str(choice_str or '').upper()
        if pos2 not in ('L','C','R'):
            gs.log.append(f"[ERR] activate_member: invalid pos {choice_str}")
            return
        cand = [str(x).upper() for x in list(p.get('candidates', []) or []) if str(x).upper() in ('L','C','R')]
        if cand and pos2 not in cand:
            gs.log.append(f"[ERR] activate_member: pos {pos2} not in candidates {cand}")
            return
        slot2 = gs.stage.get(pos2)
        if not slot2:
            gs.log.append(f"[ERR] activate_member: empty {pos2}")
            return
        after_ext_key = str(p.get('after_ext_key', '') or '').strip()
        if after_ext_key:
            src = str(p.get('source_cn', '') or '')
            ctx2 = dict(p.get('ctx', {}) or {})
            if src and not ctx2.get('source_cn'):
                ctx2['source_cn'] = src
            ctx2['choice'] = pos2
            ctx2['chosen_pos'] = pos2
            try:
                rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
            except Exception:
                rng2 = random.Random()
            try:
                _apply_effect_by_rule(gs, rng2, cards_db, {'op':'__ext__','ext_key':after_ext_key}, {}, ctx2)
                applied = True
            except Exception:
                applied = False
                raise
            finally:
                try:
                    gs.log.append(f"[AUTO] choose_stage_member_to_activate -> {'applied' if applied else 'error'} {after_ext_key} ({pos2})")
                except Exception:
                    pass
            _enqueue_auto_order_from_deferred()
            return
        slot2.active = True
        gs.log.append(f"[ACT] stage {pos2} set ACTIVE")
        _enqueue_auto_order_from_deferred()
        return
    # Generic "skip / finish early" for prompts that allow fewer picks than the max.
    # The UI can send __SKIP__ to stop selecting additional cards.
    if choice_str == "__SKIP__" and p.get("allow_less"):
        gs.log.append(f"[SKIP] prompt {kind}: user skipped remaining selections")
        return
    # 1) Live-start optional payment -> temp blade
    if kind == "live_start_free_effect":
        pos = str(p.get("pos", "") or "").upper()
        op_free = str(p.get("op", "") or "")
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f"[SKIP] live_start_free_effect: stage {pos} empty")
            return
        if choice_str.lower() in ("do", "yes", "y", "1", "true"):
            if op_free == "activate_stage_member":
                # ウェイト状態のメンバーから選択させる
                wait_opts = [p2 for p2 in ('L','C','R') if gs.stage.get(p2) and not gs.stage[p2].active]
                if not wait_opts:
                    gs.log.append(f"[INFO] live_start_free_effect: no wait member to activate")
                    return
                if len(wait_opts) == 1:
                    target = wait_opts[0]
                    gs.stage[target].active = True
                    gs.log.append(f"[AUTO] {pos}: live_start activate → {target} set ACTIVE")
                else:
                    gs.pending.append({
                        'kind': 'choose_stage_member_to_activate',
                        'text': f'{pos}: ステージのメンバーを1人アクティブにする（対象を選択）',
                        'options': wait_opts,
                    })
                    gs.log.append(f"[PENDING] {pos}: live_start activate member choice")
        else:
            gs.log.append(f"[SKIP] {pos}: live_start_free_effect ({op_free}) skipped")
        return
    if kind == "live_start_blade":
        pos = str(p.get("pos", "") or "").upper()
        need_e = _safe_int(p.get("need_e", 1), 1)
        blades = _safe_int(p.get("blades", 0), 0)
        blade_mode = str(p.get("blade_mode", "fixed") or "fixed")
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f"[SKIP] prompt: stage {pos} empty (ignored)")
            return
        if choice_str.lower() in ("pay", "yes", "y", "1", "true"):
            if not pay_energy(gs, need_e):
                gs.log.append(f"[ERR] ability: insufficient energy for [E]{need_e} (have {gs.energy_active})")
                return
            gain = int(blades)
            if blade_mode == "per_live_card":
                gain = int(blades) * int(len(getattr(gs, 'set_zone', []) or []))
            slot.temp_blade += gain
            slot.temp_until = "end_of_live"
            if blade_mode == "per_live_card":
                gs.log.append(f"[AUTO] {pos}: paid [E]{need_e} -> temp blade +{gain} ({blades}×LIVE{len(getattr(gs, 'set_zone', []) or [])}) (until end of live)")
            else:
                gs.log.append(f"[AUTO] {pos}: paid [E]{need_e} -> temp blade +{gain} (until end of live)")
        else:
            gs.log.append(f"[SKIP] {pos}: live-start blade ability skipped")
        return
    
    # 1b) Live-start optional payment -> generic effect template (regex engine)
    if kind == "live_start_pay_effect":
        pos = str(p.get("pos", "") or "").upper()
        need_e = _safe_int(p.get("need_e", 0), 0)
        cost_kind = str(p.get("cost_kind", "") or "")
        cost_n = _safe_int(p.get("cost_n", 0), 0)
        eff = str(p.get("effect", "") or "").strip()
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f"[SKIP] prompt: stage {pos} empty (ignored)")
            return
        if choice_str.lower() in ("pay", "yes", "y", "1", "true"):
            # エネルギーコスト（即時支払い）
            if need_e > 0:
                if not pay_energy(gs, need_e):
                    gs.log.append(f"[ERR] ability: insufficient energy for [E]{need_e} (have {gs.energy_active})")
                    return
            src_cn = str(p.get("cn", "") or "")
            after_ctx = {"pos": pos, "source_cn": src_cn}
            # 手札の指定グループカードを公開し、デッキ上/下に置くコスト → ユーザーに選ばせる
            if cost_kind == 'hand_group_to_deck_top_or_bottom' and cost_n > 0:
                group_need = str(p.get('cost_group', '') or '')
                blade_gain = _count_blade_icons_from_tagblob(eff)
                _enqueue_hand_to_deck_top_or_bottom(gs, cards_db, kind='ANY', n=cost_n, group=group_need, after_gain_blade=blade_gain, source_cn=src_cn)
                return
            # 手札のライブカードをデッキ下に置くコスト → ユーザーに選ばせる
            if cost_kind == 'hand_live_to_deck_bottom' and cost_n > 0:
                _enqueue_hand_to_deck_bottom(gs, cards_db, kind='LIVE', n=cost_n, after_effect_template=eff, after_ctx=after_ctx, after_source_cn=src_cn)
                return
            # 手札のライブカードを捨てるコスト → ユーザーに選ばせる
            if cost_kind == 'discard_live_from_hand' and cost_n > 0:
                live_in_hand = [c for c in list(gs.hand) if _is_live(_get_card(cards_db, c))]
                if len(live_in_hand) < cost_n:
                    gs.log.append(f"[ERR] live_start_pay_effect: not enough live cards in hand (need {cost_n}, have {len(live_in_hand)})")
                    return
                gs.pending.append({
                    'kind': 'discard_from_hand',
                    'remaining': cost_n,
                    'text': f'手札のライブカードを{cost_n}枚控え室に置く',
                    'options': live_in_hand,
                    'after_effect_template': eff,
                    'after_ctx': after_ctx,
                    'after_source_cn': src_cn,
                })
                return
            # 手札の指定名カードを捨てるコスト → ユーザーにカードを選ばせる
            if cost_kind == 'discard_named_from_hand':
                names = [str(x or '').strip() for x in list(p.get('cost_names', []) or []) if str(x or '').strip()]
                cands = _hand_named_card_candidates(gs, cards_db, names)
                exact_or_zero = bool(p.get('exact_or_zero', False))
                min_picks = int(p.get('min_picks', 0) or 0)
                max_raw = p.get('max_picks', None)
                if max_raw is None:
                    max_picks = len(cands)
                else:
                    max_picks = int(max_raw or 0)
                if max_picks < 0:
                    max_picks = 0
                if exact_or_zero and len(cands) < max_picks:
                    gs.log.append(f"[ERR] live_start_pay_effect: not enough named cards in hand for {names} (need {max_picks}, have {len(cands)})")
                    return
                if (not exact_or_zero) and max_picks > len(cands):
                    max_picks = len(cands)
                gs.pending.append({
                    'kind': 'choose_member_from_green_multi_up_to',
                    'source_zone': 'hand',
                    'action': 'discard_from_hand',
                    'min_picks': int(min_picks),
                    'max_picks': int(max_picks),
                    'exact_or_zero': bool(exact_or_zero),
                    'text': f"手札から {', '.join(names)} を{('0枚または' + str(max_picks) + '枚') if exact_or_zero else ('0〜' + str(max_picks) + '枚')}選び、控え室に置く",
                    'options': list(cands),
                    'after_effect_template': eff,
                    'after_ctx': after_ctx,
                    'after_source_cn': src_cn,
                })
                return
            # 手札を捨てるコスト（汎用）→ ユーザーに選ばせる
            if cost_kind == 'discard_from_hand' and cost_n > 0:
                if len(gs.hand) < cost_n:
                    gs.log.append(f"[ERR] live_start_pay_effect: not enough cards in hand (need {cost_n})")
                    return
                if cost_n > 1:
                    gs.pending.append({
                        'kind': 'choose_member_from_green_multi_up_to',
                        'source_zone': 'hand',
                        'action': 'discard_from_hand',
                        'min_picks': cost_n,
                        'max_picks': cost_n,
                        'text': f'手札のカードを{cost_n}枚クリックして確定してください',
                        'options': list(gs.hand),
                        'after_effect_template': eff,
                        'after_ctx': after_ctx,
                        'after_source_cn': src_cn,
                    })
                else:
                    gs.pending.append({
                        'kind': 'discard_from_hand',
                        'remaining': cost_n,
                        'text': f'手札を{cost_n}枚控え室に置く',
                        'options': list(gs.hand),
                        'after_effect_template': eff,
                        'after_ctx': after_ctx,
                        'after_source_cn': src_cn,
                    })
                return
            # self-wait コスト → このメンバーをウェイトにして効果適用
            if cost_kind == 'self_wait':
                slot.active = False
                gs.log.append(f"[COST] {pos}: {slot.cardnumber} -> WAIT (self-wait cost)")
            # コストなし（エネルギーのみ or コストなし or self-wait処理済み）→ 即時効果適用
            rng = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
            ok = try_apply_effect_template(gs, rng, cards_db, eff, after_ctx)
            if ok:
                gs.log.append(f"[AUTO] {pos}: paid cost -> applied {eff}")
            else:
                gs.log.append(f"[WARN] {pos}: paid cost but effect not matchable: {eff}")
        else:
            gs.log.append(f"[SKIP] {pos}: live-start ability skipped")
        return
    # 1c) Live-start Rise Up High: choose 1 Nijigasaki member -> temp blade +1
    if kind == 'choose_stage_member_for_source_cost_equal_minus_icon':
        pos2 = str(choice_str or '').strip().upper()
        cand = [str(x).upper() for x in list(p.get('candidates', []) or []) if str(x).upper() in ('L','C','R')]
        if pos2 not in ('L','C','R') or (cand and pos2 not in cand):
            gs.log.append(f"[ERR] choose_stage_member_for_source_cost_equal_minus_icon: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        ok = _grant_source_cost_equal_selected_original_minus_and_icon(
            gs,
            cards_db,
            str(p.get('source_pos', '') or '').upper(),
            pos2,
            int(p.get('minus_n', 0) or 0),
            int(p.get('threshold', 0) or 0),
            str(p.get('icons', '') or ''),
            source_cn=str(p.get('source_cn', '') or ''),
        )
        if not ok:
            gs.log.append(f"[ERR] choose_stage_member_for_source_cost_equal_minus_icon: failed for {pos2}")
            gs.pending.append(p)
        return
    if kind == 'choose_stage_member_for_temp_cost':
        pos2 = str(choice_str or '').strip().upper()
        opts = list(p.get('options', []) or [])
        if pos2 not in ('L', 'C', 'R') or (opts and pos2 not in opts):
            gs.log.append(f"[ERR] choose_stage_member_for_temp_cost: invalid choice {choice_str}")
            return
        ok = _grant_stage_member_temp_cost(gs, cards_db, pos2, int(p.get('cost_n', 0) or 0), source_cn=str(p.get('source_cn', '') or ''))
        if not ok:
            gs.log.append(f"[ERR] choose_stage_member_for_temp_cost: failed for {pos2}")
        return
    if kind == 'pick_group_member_for_temp_blade':
        raw = str(choice_str or '').strip()
        pos = (raw[:1].upper() if raw else '')
        pos_opts = p.get('pos_options', None)
        if (not isinstance(pos_opts, list)) or (not pos_opts):
            pos_opts = p.get('options', []) or []
        if pos not in ('L','C','R') or (isinstance(pos_opts, list) and pos_opts and pos not in pos_opts):
            gs.log.append(f'[ERR] RiseUpHigh: invalid choice {choice_str}')
            return
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'active', False):
            gs.log.append(f'[ERR] RiseUpHigh: stage {pos} empty')
            return
        slot.temp_blade += 1
        slot.temp_until = 'end_of_live'
        gs.log.append(f'[AUTO] group-member temp blade: {pos} temp blade +1 (until end of live)')
        return
    # 1e) Generic yell-retrieve: pick card(s) from yell reveals -> hand
    if kind == 'pick_from_yell':
        opts = list(p.get('options', []) or [])
        if choice_str.lower() in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append('[SKIP] pick_from_yell: done')
            _enqueue_auto_order_from_deferred()
            return
        cn = _canon_cardno(choice_str)
        valid_opts = [x for x in opts if str(x).lower() not in ('skip', '__skip__')]
        if valid_opts and not any(_canon_cardno(x) == cn for x in valid_opts):
            gs.log.append(f'[ERR] pick_from_yell: invalid choice {choice_str}')
            return
        moved = None
        for zone_name in ('resolve_zone', 'green_room'):
            z = getattr(gs, zone_name, None)
            if not isinstance(z, list):
                continue
            for i, x in enumerate(list(z)):
                if _canon_cardno(x) == cn:
                    moved = z.pop(i)
                    break
            if moved:
                break
        if not moved:
            gs.log.append(f'[ERR] pick_from_yell: chosen card not found in zones {cn}')
            return
        gs.hand.append(moved)
        _remove_from_yell_revealed_tracker(gs, moved)
        gs.log.append(f'[ACT] pick_from_yell: took {moved} -> hand')
        remaining = int(p.get('remaining_n', 1) or 1) - 1
        if remaining > 0:
            card_kind = str(p.get('card_kind', 'ANY') or 'ANY')
            group = str(p.get('group', '') or '')
            cost_lim = int(p.get('cost_lim', 99) or 99)
            score_lim = int(p.get('score_lim', 99) or 99)
            up_to = bool(p.get('up_to', False))
            next_opts = _yell_revealed_candidates(gs, cards_db, card_kind, group, cost_lim, score_lim, int(pend.get('cost_min', 0) or 0))
            if next_opts:
                opts2 = list(next_opts)
                if up_to:
                    opts2 = ['skip'] + opts2
                gs.pending.append({
                    'kind': 'pick_from_yell',
                    'text': f'続けて、エールで公開されたカードを手札に加える（残り{remaining}枚{"まで" if up_to else ""}）',
                    'options': opts2,
                    'source_cn': str(p.get('source_cn', '') or ''),
                    'remaining_n': remaining,
                    'card_kind': card_kind,
                    'group': group,
                    'cost_lim': cost_lim,
                    'score_lim': score_lim,
                    'up_to': up_to,
                })
        _enqueue_auto_order_from_deferred()
        return
    if kind == 'pick_from_yell_to_deck_top':
        if choice_str == 'skip':
            gs.log.append('[ACT] pick_from_yell_to_deck_top: skipped')
            gs.pending.clear()
            return
        try:
            idx = int(choice_str)
            opts = list(pend.get('options', []) or [])
            cn = opts[idx] if 0 <= idx < len(opts) else choice_str
        except Exception:
            cn = choice_str
        moved = ''
        for zone_name in ('resolve_zone', 'green_room'):
            z = getattr(gs, zone_name, None)
            if isinstance(z, list):
                for i, x in enumerate(list(z)):
                    if _canon_cardno(x) == _canon_cardno(cn):
                        moved = z.pop(i)
                        break
            if moved:
                break
        if not moved:
            gs.log.append(f'[ERR] pick_from_yell_to_deck_top: chosen card not found in zones {cn}')
            return
        gs.deck.insert(0, moved)
        _remove_from_yell_revealed_tracker(gs, moved)
        gs.log.append(f'[ACT] pick_from_yell_to_deck_top: moved {moved} -> deck top')
        gs.pending.clear()
        return
    if kind == 'pick_from_yell_to_deck_bottom':
        opts = list(p.get('options', []) or [])
        if choice_str.lower() in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append('[SKIP] pick_from_yell_to_deck_bottom: done')
            _enqueue_auto_order_from_deferred()
            return
        cn = _canon_cardno(choice_str)
        valid_opts = [x for x in opts if str(x).lower() not in ('skip', '__skip__')]
        if valid_opts and not any(_canon_cardno(x) == cn for x in valid_opts):
            gs.log.append(f'[ERR] pick_from_yell_to_deck_bottom: invalid choice {choice_str}')
            return
        moved = None
        for zone_name in ('resolve_zone', 'green_room'):
            z = getattr(gs, zone_name, None)
            if not isinstance(z, list):
                continue
            for i, x in enumerate(list(z)):
                if _canon_cardno(x) == cn:
                    moved = z.pop(i)
                    break
            if moved:
                break
        if not moved:
            gs.log.append(f'[ERR] pick_from_yell_to_deck_bottom: chosen card not found in zones {cn}')
            return
        gs.deck.append(moved)
        _remove_from_yell_revealed_tracker(gs, moved)
        gs.log.append(f'[ACT] pick_from_yell_to_deck_bottom: moved {moved} -> deck bottom')
        remaining = int(p.get('remaining_n', 1) or 1) - 1
        if remaining > 0:
            card_kind = str(p.get('card_kind', 'ANY') or 'ANY')
            next_opts = _yell_revealed_candidates(gs, cards_db, card_kind)
            if next_opts:
                gs.pending.append({
                    'kind': 'pick_from_yell_to_deck_bottom',
                    'text': f'続けて、エールで公開されたカードをデッキの一番下に置く（残り{remaining}枚まで）',
                    'options': ['skip'] + list(next_opts),
                    'source_cn': str(p.get('source_cn', '') or ''),
                    'remaining_n': remaining,
                    'card_kind': card_kind,
                })
        _enqueue_auto_order_from_deferred()
        return
    # 1f) live-success optional-cost pay/skip (hand discard -> retrieve_from_yell)
    if kind == 'live_success_pay_effect':
        low = str(choice_str or '').strip().lower()
        pos2 = str(p.get('pos', '') or '').upper()
        src_cn = str(p.get('source_cn', '') or '')
        eff = str(p.get('effect', '') or '')
        cost_kind = str(p.get('cost_kind', '') or '')
        cost_n = int(p.get('cost_n', 0) or 0)
        ctx2 = dict(p.get('ctx', {}) or {})
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append(f'[SKIP] {src_cn}[ライブ成功時] optional cost skipped')
            return
        if low not in ('pay', 'yes', 'y', '1', 'true'):
            gs.log.append(f'[ERR] live_success_pay_effect: invalid choice {choice_str}')
            return
        if cost_kind == 'discard_from_hand':
            if len(gs.hand) < cost_n:
                gs.log.append(f'[ERR] live_success_pay_effect: not enough hand cards to discard')
                return
            # enqueue discard first; after_effect_template fires when discard completes
            gs.pending.append({
                'kind': 'discard_from_hand',
                'remaining': cost_n,
                'text': f'{src_cn}[ライブ成功時] 手札を{cost_n}枚控え室に置く',
                'options': list(gs.hand),
                'after_effect_template': eff,
                'after_ctx': ctx2,
                'after_source_cn': src_cn,
            })
            gs.log.append(f'[PENDING] {src_cn}[ライブ成功時] discard {cost_n} then {eff}')
        return
# 2) Pick 1 LIVE from green room to hand
    if kind == "pick_live_from_green":
        if choice_str.lower() in ("skip", "no", "n", "0", "false"):
            gs.log.append("[SKIP] pick live from green room")
            return
        opts = p.get("options", [])
        cn = _canon_cardno(choice_str)
        if isinstance(opts, list) and opts and cn not in opts:
            gs.log.append(f"[ERR] pick live: invalid choice {cn}")
            return
        # allow variants in green room list
        # exact match first; else try variant hit
        gr = list(gs.green_room)
        pick_cn = None
        if cn in gr:
            pick_cn = cn
        else:
            for x in _cardno_variants(cn):
                if x in gr:
                    pick_cn = x
                    break
        if not pick_cn:
            gs.log.append(f"[ERR] pick live: not in green room {cn}")
            return
        ci2 = _get_card(cards_db, pick_cn)
        if not _is_live(ci2):
            gs.log.append(f"[ERR] pick live: not a LIVE card {pick_cn}")
            return
        gs.green_room.remove(pick_cn)
        gs.hand.append(pick_cn)
        gs.log.append(f"[ACT] took LIVE {pick_cn} from green room -> hand")
        return
    # 2b) Pick 1 MEMBER from green room to hand (sd1-006)
    if kind == "pick_member_from_green":
        if choice_str.lower() in ("skip", "no", "n", "0", "false"):
            gs.log.append("[SKIP] pick member from green room")
            return
        opts = p.get("options", [])
        cn = _canon_cardno(choice_str)
        if isinstance(opts, list) and opts and cn not in opts:
            gs.log.append(f"[ERR] pick member: invalid choice {cn}")
            return
        gr = list(gs.green_room)
        pick_cn = None
        if cn in gr:
            pick_cn = cn
        else:
            for x in _cardno_variants(cn):
                if x in gr:
                    pick_cn = x
                    break
        if not pick_cn:
            gs.log.append(f"[ERR] pick member: not in green room {cn}")
            return
        ci2 = _get_card(cards_db, pick_cn)
        if _is_live(ci2):
            gs.log.append(f"[ERR] pick member: LIVE is not allowed {pick_cn}")
            return
        gs.green_room.remove(pick_cn)
        gs.hand.append(pick_cn)
        gs.log.append(f"[ACT] took MEMBER {pick_cn} from green room -> hand")
        return
        if mode in ("topdeck", "deck", "b", "1"):
            cands: List[str] = []
            for x in list(gs.green_room):
                ci = _get_card(cards_db, x)
                if not ci:
                    continue
                if not _is_live(ci):
                    continue
                g = str(getattr(ci, "group", "") or "")
                if "虹ヶ咲" not in g:
                    continue
                cands.append(x)
            if not cands:
                gs.log.append("[AUTO] 栞子[登場]: chose TOPDECK but no Nijigasaki LIVE in green room")
                return
            gs.pending.append({
                "kind": "shioriko_topdeck_pick1",
                "text": "栞子[登場]: 控え室の『虹ヶ咲』LIVEを最大2枚デッキ上。まず1枚目（=一番上）を選ぶ / Skip可",
                "options": cands,
            })
            gs.log.append(f"[PENDING] 栞子[登場]: pick topdeck #1 from {len(cands)} candidates")
            return
        gs.log.append(f"[ERR] 栞子[登場]: invalid mode '{choice_str}'")
        return
        opts = p.get("options", [])
        cn = _canon_cardno(choice_str)
        # find actual card in green room (allow variants)
        pick_cn = None
        if cn in gs.green_room:
            pick_cn = cn
        else:
            for x in _cardno_variants(cn):
                if x in gs.green_room:
                    pick_cn = x
                    break
        if not pick_cn:
            gs.log.append(f"[ERR] 栞子[登場]: pick1 not in green room {cn}")
            return
        ci = _get_card(cards_db, pick_cn)
        if not ci or (not _is_live(ci)) or ("虹ヶ咲" not in str(ci.group or "")):
            gs.log.append(f"[ERR] 栞子[登場]: pick1 invalid (need Nijigasaki LIVE) {pick_cn}")
            return
        # remove from green and put on deck top
        gs.green_room.remove(pick_cn)
        gs.deck.insert(0, pick_cn)
        gs.log.append(f"[AUTO] 栞子[登場]: topdeck #1 -> {pick_cn}")
        # second pick (optional) from remaining candidates
        cands2: List[str] = []
        for x in list(gs.green_room):
            ci2 = _get_card(cards_db, x)
            if not ci2:
                continue
            if not _is_live(ci2):
                continue
            if "虹ヶ咲" not in str(ci2.group or ""):
                continue
            cands2.append(x)
        if not cands2:
            gs.log.append("[AUTO] 栞子[登場]: topdeck #2 none")
            return
        gs.pending.append({
            "kind": "shioriko_topdeck_pick2",
            "text": "栞子[登場]: 2枚目（=上から2枚目）を選ぶ / Skip可",
            "options": cands2,
        })
        gs.log.append(f"[PENDING] 栞子[登場]: pick topdeck #2 from {len(cands2)} candidates")
        return
        cn = _canon_cardno(choice_str)
        pick_cn = None
        if cn in gs.green_room:
            pick_cn = cn
        else:
            for x in _cardno_variants(cn):
                if x in gs.green_room:
                    pick_cn = x
                    break
        if not pick_cn:
            gs.log.append(f"[ERR] 栞子[登場]: pick2 not in green room {cn}")
            return
        ci = _get_card(cards_db, pick_cn)
        if not ci or (not _is_live(ci)) or ("虹ヶ咲" not in str(ci.group or "")):
            gs.log.append(f"[ERR] 栞子[登場]: pick2 invalid (need Nijigasaki LIVE) {pick_cn}")
            return
        gs.green_room.remove(pick_cn)
        # place as 2nd card on top: insert at index 1
        gs.deck.insert(1 if len(gs.deck) >= 1 else 0, pick_cn)
        gs.log.append(f"[AUTO] 栞子[登場]: topdeck #2 -> {pick_cn}")
        return
    if kind == 'choose_enter_effect_mode':
        opts = list(p.get('options', []) or [])
        effs = list(p.get('effects', []) or [])
        ctx2 = dict(p.get('ctx', {}) or {})
        src = str(p.get('source_cn', '') or '')
        idx = -1
        raw = str(choice_str or '').strip()
        if raw in opts:
            idx = opts.index(raw)
        else:
            try:
                idx_i = int(raw)
                if 0 <= idx_i < len(effs):
                    idx = idx_i
            except Exception:
                idx = -1
        if idx < 0 or idx >= len(effs):
            gs.log.append(f"[ERR] choose_enter_effect_mode: invalid choice {choice_str}")
            return
        eff = str(effs[idx] or '').strip()
        try:
            rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
        except Exception:
            rng2 = random.Random()
        ok = try_apply_effect_template(gs, rng2, cards_db, eff, ctx2)
        if ok:
            gs.log.append(f"[AUTO] {src}[登場]: chose mode -> applied {eff}")
        else:
            gs.log.append(f"[WARN] {src}[登場]: chosen mode not matchable {eff}")
        return
    if kind == 'choose_heart_color':
        pos = str(p.get('pos', '') or '').upper()
        n = int(p.get('n', 1) or 1)
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f'[SKIP] choose_heart_color: stage {pos} empty')
            return
        col = _HEART_JP_MAP.get(str(choice_str or '').strip(), '')
        if not col:
            gs.log.append(f'[ERR] choose_heart_color: invalid color {choice_str!r}')
            gs.pending.append(p)
            return
        _grant_temp_heart(slot, col, n)
        gs.log.append(f'[AUTO] {pos}: temp heart +{n} {col} (until end_of_live)')
        return
    if kind == 'choose_heart_color_for_other':
        src_pos = str(p.get('src_pos', '') or '').upper()
        cands = list(p.get('candidates', []) or [])
        n = int(p.get('n', 1) or 1)
        chosen_color = str(p.get('chosen_color', '') or '')
        if not chosen_color:
            # Step 1: choose color
            col = _HEART_JP_MAP.get(str(choice_str or '').strip(), '')
            if not col:
                gs.log.append(f'[ERR] choose_heart_color_for_other: invalid color {choice_str!r}')
                gs.pending.append(p)
                return
            if len(cands) == 1:
                slot2 = gs.stage.get(cands[0])
                if slot2:
                    _grant_temp_heart(slot2, col, n)
                    gs.log.append(f'[AUTO] {cands[0]}: temp heart +{n} {col} from {src_pos}')
                return
            # Need to pick target member next
            gs.pending.append({**p, 'chosen_color': col,
                'text': f'ハートを与えるメンバーの位置を選ぶ（{col}×{n}）',
                'options': cands})
            return
        else:
            # Step 2: choose target position
            tgt = str(choice_str or '').upper()
            if tgt not in cands:
                gs.log.append(f'[ERR] choose_heart_color_for_other: invalid target {tgt!r}')
                gs.pending.append(p)
                return
            slot2 = gs.stage.get(tgt)
            if slot2:
                _grant_temp_heart(slot2, chosen_color, n)
                gs.log.append(f'[AUTO] {tgt}: temp heart +{n} {chosen_color} from {src_pos}')
            return
    gs.log.append(f"[WARN] resolve_pending: unknown kind='{kind}' (ignored)")
    # If a deferred auto-order exists and we are now free of other prompts, resume it.
    _enqueue_auto_order_from_deferred()
def cmd_end_turn(gs: GameState, rng: random.Random) -> None:
    """End MAIN and enter the Live phase (same turn).
    Note: We do NOT advance to the next turn here. The next turn begins after
    the Live phase is fully resolved (ACK done, resolve zone empty).
    """
    if gs.pending:
        gs.log.append("[WARN] end_turn: pending prompt exists; resolve it first.")
        return
    if gs.resolve_zone:
        gs.log.append("[WARN] end_turn: resolve_zone not empty; please ACK before ending.")
        return
    if gs.phase != "MAIN":
        gs.log.append(f"[WARN] end_turn: only allowed in MAIN (phase={gs.phase})")
        return
    # Enter Live phase (set step)
    gs.phase = "LIVE_SET"
    base_limit = 3
    try:
        delta = int(getattr(gs, 'next_live_set_limit_delta', 0) or 0)
    except Exception:
        delta = 0
    gs.live_set_limit = max(0, base_limit + delta)
    gs.next_live_set_limit_delta = 0
    # Keep any preloaded LIVE cards already placed into set_zone during MAIN.
    if not isinstance(getattr(gs, 'set_zone', None), list):
        gs.set_zone = []
    gs.live_start_prompted = False
    gs.turn_blade_bonus = 0
    gs.log.append(f"[PHASE] LIVE_SET (hand choose up to {gs.live_set_limit}; preloaded={len(gs.set_zone)}) turn={gs.turn}")
    if bool(getattr(gs, "cannot_live_until_end_of_live", False)):
        gs.log.append("[INFO] live_set: you cannot live until end of live; any set cards will not start a live and will go to green room")
def _advance_to_next_turn(gs: GameState, rng: random.Random) -> None:
    _apply_turn_order_transition_resets(gs)
    gs.turn += 1
    begin_turn(gs, rng)
def _collect_live_storage_cleanup_topbottom_triggers(gs: GameState, cards_db: Dict[str, CardInfo], live_cns: List[str]) -> List[Dict[str, Any]]:
    """Build pending prompts for BODY triggers when LIVE cards leave live storage to waiting room.

    Current target family: PL!S-bp6-002 style.
    Text: 『G』のライブカードが自分のライブカード置き場から控え室に置かれたとき、
          そのライブカードをデッキの一番上か一番下に置いてもよい。
    """
    prompts: List[Dict[str, Any]] = []
    live_list = [str(x or '') for x in list(live_cns or []) if str(x or '').strip()]
    if not live_list:
        return prompts
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'cardnumber', ''):
            continue
        ci_src = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci_src or not getattr(ci_src, 'abilities', None):
            continue
        for ab in (getattr(ci_src, 'abilities', None) or []):
            if not isinstance(ab, dict):
                continue
            for cl in (ab.get('clauses', []) or []):
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
                eff_norm = _normalize_icon_token_text(eff).replace('\n', '')
                m = re.match(r'^『(?P<group>[^』]+)』のライブカードが自分のライブカード置き場から控え室に置かれたとき、そのライブカードをデッキの一番上か一番下に置いてもよい。$', eff_norm)
                if not m:
                    continue
                group = str(m.group('group') or '').strip()
                trigger_key = f'live_storage_to_green_topbottom:{pos}:{getattr(slot, "cardnumber", "")}:{eff_norm}:turn{int(getattr(gs, "turn", 0) or 0)}'
                try:
                    used = set(getattr(gs, 'once_used', set()) or set())
                except Exception:
                    used = set()
                if 'ターン1回' in str(ab.get('conditions', '') or '') and trigger_key in used:
                    continue
                cands = []
                for lcn in live_list:
                    ci_live = _get_card(cards_db, lcn)
                    if ci_live and _is_live_ci(ci_live) and (not group or group in str(getattr(ci_live, 'group', '') or '')):
                        cands.append(lcn)
                if not cands:
                    continue
                prompts.append({
                    'kind': 'live_storage_to_deck_top_or_bottom',
                    'text': f'{getattr(slot, "cardnumber", "")} の自動効果：控え室に置かれる『{group}』のライブカードを1枚、デッキの一番上か一番下に置いてもよい。',
                    'options': ['skip'] + list(cands),
                    'candidate_lives': list(cands),
                    'group': group,
                    'source_pos': pos,
                    'source_cn': getattr(slot, 'cardnumber', ''),
                    'trigger_key': trigger_key,
                })
    return prompts

def cmd_next(gs: GameState, rng: random.Random, cards_db: Dict[str, CardInfo], indices: Optional[List[int]] = None) -> None:
    """Automatic progression for the current phase.
    The intended flow is:
      MAIN -> (Next/End Turn) -> LIVE_SET -> (Next) -> LIVE_CONFIRM -> (resolve live-start prompts)
      -> LIVE_PERF -> (Next) -> LIVE_ATTEMPT -> (Next) -> LIVE_RESOLVE -> (Next) -> next turn.
    """
    if indices is None:
        indices = []
    if gs.pending:
        # Let the global NEXT button acknowledge/skip simple pending popups.
        # The same prompts still have in-popup buttons; this is only a convenience
        # path so non-choice confirmation popups do not trap the flow.
        try:
            p0 = gs.pending[0] if isinstance(gs.pending[0], dict) else {}
            k0 = str(p0.get('kind', '') or '')
            opts0 = [str(x).strip().lower() for x in list(p0.get('options', []) or []) if str(x).strip()]
            ack_kinds = {
                'show_revealed_cards_ack', 'message_ack', 'effect_notice',
                'live_start_success_count_distinct_names_score_ack',
                'mass_bottom_auto_ack', 'mass_bottom_optional_result_ack',
            }
            if k0 in ack_kinds:
                cmd_resolve_pending(gs, cards_db, 0, 'ok', rng)
                return
            if k0 == 'pick_success_to_store':
                cmd_resolve_pending(gs, cards_db, 0, 'skip', rng)
                return
            if ('skip' in opts0 or '__skip__' in opts0) and (bool(p0.get('optional', False)) or bool(p0.get('allow_skip', False)) or k0 in ('pay_or_skip', 'confirm_effect', 'discard_from_hand')):
                cmd_resolve_pending(gs, cards_db, 0, 'skip', rng)
                return
        except Exception as e:
            try:
                gs.log.append(f'[WARN] next pending-skip helper failed: {e}')
            except Exception:
                pass
        gs.log.append("[WARN] next: pending prompt exists; resolve it first.")
        return
    if gs.phase == "MAIN":
        cmd_end_turn(gs, rng)
        return
    if gs.phase == "LIVE_SET":
        cmd_set(gs, rng, indices)
        gs.phase = "LIVE_CONFIRM"
        gs.log.append(f"[PHASE] LIVE_CONFIRM (filter set cards) turn={gs.turn}")
        return
    if gs.phase == "LIVE_CONFIRM":
        if not gs.set_zone:
            gs.log.append("[INFO] confirm: set_zone empty; skipping live.")
            gs.phase = "LIVE_RESOLVE"
            gs.log.append(f"[PHASE] LIVE_RESOLVE (no live) turn={gs.turn}")
            return
        if bool(getattr(gs, "cannot_live_until_end_of_live", False)):
            sent = list(gs.set_zone)
            gs.green_room.extend(sent)
            gs.set_zone = []
            gs.log.append(f"[INFO] confirm: cannot live until end of live; set cards {len(sent)} -> green room, live does not start")
            gs.phase = "LIVE_RESOLVE"
            gs.log.append(f"[PHASE] LIVE_RESOLVE (live forbidden) turn={gs.turn}")
            return
        lives: List[str] = []
        nonlives: List[str] = []
        for cn in gs.set_zone:
            c = _get_card(cards_db, cn)
            if c and c.type == "LIVE":
                lives.append(cn)
            else:
                nonlives.append(cn)
        if nonlives:
            gs.green_room.extend(nonlives)
            gs.log.append(f"[SET] non-live {len(nonlives)} -> green room")
        gs.set_zone = lives
        # FIX_V2_17_CONFIRM_NO_LIVE_AFTER_FILTER
        # If no LIVE cards remain after filtering, skip live (no cheer/attempt).
        if not gs.set_zone:
            gs.log.append('[INFO] confirm: no LIVE after filtering; skipping live.')
            gs.phase = 'LIVE_RESOLVE'
            gs.log.append(f'[PHASE] LIVE_RESOLVE (no live) turn={gs.turn}')
            return
        n = _enqueue_live_start_prompts(gs, cards_db)
        if n > 0:
            gs.log.append(f"[AUTO] live-start triggers queued={n}")
            return
        gs.phase = "LIVE_PERF"
        gs.log.append(f"[PHASE] LIVE_PERF (YELL) turn={gs.turn}")
        return
    if gs.phase == "LIVE_PERF":
        # FIX_V2_17_PERF_NO_LIVE_GUARD
        if not gs.set_zone:
            gs.log.append('[INFO] perf: no LIVE in set_zone; skipping cheer/attempt.')
            gs.phase = 'LIVE_RESOLVE'
            gs.log.append(f'[PHASE] LIVE_RESOLVE (no live) turn={gs.turn}')
            return
        cmd_yell(gs, rng, cards_db)
        gs.phase = "LIVE_ATTEMPT"
        gs.log.append(f"[PHASE] LIVE_ATTEMPT (attempt) turn={gs.turn}")
        return
    if gs.phase == "LIVE_ATTEMPT":
        cmd_attempt(gs, cards_db)
        gs.phase = "LIVE_RESOLVE"
        gs.log.append(f"[PHASE] LIVE_RESOLVE (ACK + next turn) turn={gs.turn}")
        return
    if gs.phase == "LIVE_RESOLVE":
        # Treat Next as the confirm/cleanup step (8.4 timing).
        # 1) Run <ライブ成功時> triggers (8.4.4)
        if bool(getattr(gs, 'need_live_success_triggers', False)):
            gs.need_live_success_triggers = False
            if bool(getattr(gs, 'last_attempt_ok', False)) and list(getattr(gs, 'last_attempt_lives', []) or []):
                lives = list(getattr(gs, 'last_attempt_lives', []) or [])
                _run_live_success_triggers(gs, rng, cards_db, lives)
                if gs.pending:
                    return
        # Recompute/log final compare score after <ライブ成功時> effects that change score.
        try:
            _bon = list(getattr(gs, 'last_attempt_score_bonus', []) or [])
            _lvs = list(getattr(gs, 'last_attempt_lives', []) or [])
            _attempt_total = int(getattr(gs, 'last_attempt_attempt_score', 0) or 0)
            if _lvs:
                _total, _rows, _stage_bonus, _total_bonus, _yell_score_icon_bonus = _compute_final_compare_score_after_success(gs, cards_db)
                _sets = list(getattr(gs, 'last_attempt_score_set', []) or [])
                _changed = bool(any(int(x or 0) != 0 for x in _bon)) or bool(any(x is not None for x in _sets)) or bool(int(_total_bonus or 0) != 0) or bool(int(_yell_score_icon_bonus or 0) != 0)
                for _cn, _base, _delta, _eff, _set_v in _rows:
                    if _set_v is not None and _delta:
                        gs.log.append(f"  success-score: {_cn} = {_eff} (set {_set_v}{'+' if int(_delta) >= 0 else ''}{_delta})")
                    elif _set_v is not None:
                        gs.log.append(f"  success-score: {_cn} = {_eff} (set {_set_v})")
                    elif _delta:
                        gs.log.append(f"  success-score: {_cn} = {_eff} ({_base}{'+' if int(_delta) >= 0 else ''}{_delta})")
                if _stage_bonus:
                    gs.log.append(f"  success-score: stage always bonus = +{_stage_bonus}")
                if _total_bonus:
                    gs.log.append(f"  success-score: live total adjustment = {_total_bonus:+d}")
                if _yell_score_icon_bonus:
                    gs.log.append(f"  success-score: yell score icons = +{_yell_score_icon_bonus}")
                gs.log.append(f"[COMPARE] final_score_after_success_effects={_total}")
                gs.last_attempt_final_score = int(_total)
                gs.banner_text = f"SUCCESS (Final Score {_total})"
                gs.banner_ts = time.time()
                gs.banner_ttl = 4.0
                if _total != _attempt_total:
                    gs.log.append(f"[DISPLAY] banner score updated: {_attempt_total} -> {_total}")
                else:
                    gs.log.append(f"[DISPLAY] banner score confirmed: {_total}")
        except Exception:
            pass
        # 2) Winner-based success storage decision (8.4.7).
        #    Since this simulator has no opponent, we let the user decide whether to store
        #    a successful LIVE into 成功ライブカード置き場 (skip allowed).
        if bool(getattr(gs, 'need_success_store_choice', False)):
            if bool(getattr(gs, 'last_attempt_ok', False)) and list(getattr(gs, 'last_attempt_lives', []) or []):
                lives = list(getattr(gs, 'last_attempt_lives', []) or [])
                gs.pending.append({
                    'kind': 'pick_success_to_store',
                    'text': f"成功ライブカード置き場に置くカードを選択（Skip可） / Final Score {int(getattr(gs, 'last_attempt_final_score', 0) or 0)}",
                    # candidates are LIVE cardnumbers (skip is a separate action)
                    'options': list(lives),
                    'lives': list(lives),
                })
                gs.need_success_store_choice = False
                gs.log.append(f"[PENDING] success store choice ({len(lives)} lives)")
                return
            gs.need_success_store_choice = False
        # 3) Move cards still remaining in the live card storage to the waiting room (8.4.8).
        try:
            _remain_live = list(getattr(gs, 'set_zone', []) or [])
        except Exception:
            _remain_live = []
        if _remain_live:
            # Before the default 8.4.8 waiting-room move, enqueue optional
            # BODY triggers such as PL!S-bp6-002.  The cards remain in set_zone
            # until those prompts are resolved, then normal cleanup continues on NEXT.
            try:
                _prompts = _collect_live_storage_cleanup_topbottom_triggers(gs, cards_db, _remain_live)
            except Exception:
                _prompts = []
            if _prompts:
                gs.pending.extend(_prompts)
                gs.log.append(f'[PENDING] live storage cleanup top/bottom triggers={len(_prompts)}')
                return
            try:
                gs.green_room.extend(_remain_live)
            except Exception:
                gs.green_room = list(getattr(gs, 'green_room', []) or []) + list(_remain_live)
            gs.log.append(f"[ZONE] waiting +{len(_remain_live)} (live storage cleanup)")
            gs.set_zone = []
        # 4) ACK revealed cards (resolve zone)
        if gs.resolve_zone:
            cmd_ack(gs, rng)
        if gs.resolve_zone:
            gs.log.append("[WARN] next: resolve_zone still not empty after ACK; abort.")
            return
        # End-of-live cleanup (always), including no-live / cannot-live cases.
        _clear_end_of_live_buffs(gs, cards_db)
        gs.live_start_prompted = False
        # Clear per-live cheer reveal tracker
        try:
            setattr(gs, '_yell_revealed_this_live', [])
        except Exception:
            pass
        # Clear last-attempt helpers
        gs.last_attempt_lives = []
        gs.last_attempt_score_bonus = []
        gs.last_attempt_score_set = []
        gs.last_attempt_total_score_bonus = 0
        gs.last_attempt_score_rows = []
        gs.last_attempt_attempt_score = 0
        gs.last_attempt_final_score = 0
        gs.last_attempt_ok = False
        _advance_to_next_turn(gs, rng)
        return
    gs.log.append(f"[WARN] next: unknown phase={gs.phase}")
