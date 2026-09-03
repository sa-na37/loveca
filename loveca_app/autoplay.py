#!/usr/bin/env python3
# BUILD_TAG = "autoplay_high_impact_stage_alternatives_20260901a"
"""Autoplay planning primitives for Loveca Application.

This module is intentionally side-effect free.  It evaluates a deck's cost
curve and returns policy candidates; runtime state mutation remains in the
simulator engine.
"""
from __future__ import annotations

import re
import random
from math import comb
from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable


BUILD_TAG = "autoplay_high_impact_stage_alternatives_20260901a"


CardLookup = Callable[[str], dict[str, Any]]


@dataclass(frozen=True)
class CostProgressionTemplate:
    key: str
    label: str
    turns: tuple[tuple[int, ...], ...]
    intent: str
    phase: str = "early"
    strengths: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()


COST_PROGRESSIONS: tuple[CostProgressionTemplate, ...] = (
    CostProgressionTemplate(
        key="t1_4_t2_9_t3_15",
        label="4 -> 9 -> 15単騎",
        turns=((4,), (9,), (15,)),
        intent="高コストを最速で着地させる進行",
        phase="high_cost_rush",
        strengths=("手札消費が少ない", "15コスト到達が早い"),
        risks=("序盤のステージ枚数が少ない", "低コスト横展開が弱くなりやすい"),
    ),
    CostProgressionTemplate(
        key="t1_4_t2_7_2_t3_13_2",
        label="4 -> 7-2 -> 13-2",
        turns=((4,), (7, 2), (13, 2)),
        intent="7コスト経由で13コストへ伸ばす進行",
        phase="mid_to_high",
        strengths=("高性能7/13コストを活かしやすい", "2コストを横に添えられる"),
        risks=("7コストの採用枚数に再現性が左右される"),
    ),
    CostProgressionTemplate(
        key="t1_4_t2_2_4_2_t3_2_10_2",
        label="4 -> 2-4-2 -> 2-10-2",
        turns=((4,), (2, 4, 2), (2, 10, 2)),
        intent="10コスト帯へ安定して接続する進行",
        phase="ten_axis",
        strengths=("10コストを探す猶予がある", "横展開を保ちやすい"),
        risks=("2ターン目に手札消費が増える", "エネルギーが余る場面がある"),
    ),
    CostProgressionTemplate(
        key="t1_2_2_t2_2_4_2_t3_2_10_2",
        label="2-2 -> 2-4-2 -> 2-10-2",
        turns=((2, 2), (2, 4, 2), (2, 10, 2)),
        intent="序盤から横展開して10コストへ接続する進行",
        phase="ten_axis",
        strengths=("1ターン目の盤面スタッツを作りやすい", "低コスト汎用札を活かしやすい"),
        risks=("手札消費が激しい", "中盤で高コストを引けないと伸び悩む"),
    ),
    CostProgressionTemplate(
        key="t1_2_2_t2_2_5_2_t3_2_11_2",
        label="2-2 -> 2-5-2 -> 2-11-2",
        turns=((2, 2), (2, 5, 2), (2, 11, 2)),
        intent="序盤の盤面強度を高く取り、11コストへ伸ばす進行",
        phase="eleven_axis",
        strengths=("序盤ライブを成功させやすい", "エネルギーロスが少ない"),
        risks=("5/11コストの採用枚数に依存する", "手札要求が高い"),
    ),
    CostProgressionTemplate(
        key="t1_2_2_t2_2_7_t3_2_13_2",
        label="2-2 -> 7-2 -> 13-2",
        turns=((2, 2), (7, 2), (13, 2)),
        intent="2コスト展開から7/13コストへ伸ばす進行",
        phase="thirteen_axis",
        strengths=("1ターン目を強く作りながら高コストへ接続できる",),
        risks=("7コストと13コストの両方を要求する", "追加2コスト登場は上振れとして扱う"),
    ),
    CostProgressionTemplate(
        key="t1_4_t2_6_2_t3_2_10_2",
        label="4 -> 6-2 -> 2-10-2",
        turns=((4,), (6, 2), (2, 10, 2)),
        intent="6コスト帯を経由して10コストへ伸ばす進行",
        phase="ten_axis",
        strengths=("5-7コスト帯の厚みを活かせる", "2コストを横に添えやすい"),
        risks=("6コスト単体の採用理由が薄いと中継が弱くなりやすい"),
    ),
    CostProgressionTemplate(
        key="t1_4_t2_8_t3_2_12_2",
        label="4 -> 8 -> 2-12-2",
        turns=((4,), (8,), (2, 12, 2)),
        intent="8コスト帯を中継し、12コスト周辺へ伸ばす進行",
        phase="mid_to_high",
        strengths=("8コストの採用が多い構築を活かせる", "3ターン目に横を残しやすい"),
        risks=("12コスト帯が薄いと4ターン目以降の伸びが止まりやすい"),
    ),
    CostProgressionTemplate(
        key="t1_2_2_t2_2_6_2_t3_2_12_2",
        label="2-2 -> 2-6-2 -> 2-12-2",
        turns=((2, 2), (2, 6, 2), (2, 12, 2)),
        intent="低コスト横展開から6/12コストへ伸ばす進行",
        phase="mid_to_high",
        strengths=("序盤のステージ枚数を維持しやすい", "5-10帯の厚みを広く使える"),
        risks=("手札消費が多く、ドロー/回収の補助が欲しい"),
    ),
    CostProgressionTemplate(
        key="t1_2_2_t2_2_8_t3_2_14_2",
        label="2-2 -> 2-8 -> 2-14-2",
        turns=((2, 2), (2, 8), (2, 14, 2)),
        intent="2コスト展開から8/14コストへ伸ばす進行",
        phase="mid_to_high",
        strengths=("8コストと14コストの採用が多い構築に合う",),
        risks=("14コスト帯が少ないと高コスト接続が不安定"),
    ),
    CostProgressionTemplate(
        key="t4_15_plus_anchor",
        label="4ターン目以降 15+単騎軸",
        turns=((4,), (9,), (15,), (15,)),
        intent="15コスト以上を継続して着地させる後半方針",
        phase="late",
        strengths=("高コスト札の枚数を勝ち筋に直結させやすい",),
        risks=("15コスト以上が少ないと後半の再現性が落ちる"),
    ),
    CostProgressionTemplate(
        key="t4_2_15_2_wide",
        label="4ターン目以降 2-15+-2横添え軸",
        turns=((2, 5, 2), (2, 11, 2), (2, 15, 2), (2, 15, 2)),
        intent="15コスト以上を中心にしつつ左右の低コストで盤面を支える後半方針",
        phase="late",
        strengths=("終盤もステージ枚数を維持しやすい", "2コストの採用枚数を活かせる"),
        risks=("手札消費と2コスト供給が課題になりやすい"),
    ),
    CostProgressionTemplate(
        key="t4_special_baton_high_cost",
        label="4ターン目以降 特殊バトンタッチ高コスト軸",
        turns=((2, 7), (2, 13, 2), (15,), (22,)),
        intent="バトンタッチ条件や特殊登場で15/22コスト級へ接続する後半方針",
        phase="late_special",
        strengths=("特殊バトンタッチ札がある構築の最大値を見やすい",),
        risks=("専用条件を満たせないと通常進行より不安定"),
    ),
)


GOAL_TYPE_PRESETS: tuple[dict[str, str], ...] = (
    {"key": "turn_live_card_success", "label": "nターン目に特定ライブカードを成功"},
    {"key": "turn_live_score_success", "label": "nターン目に合計スコアi以上のライブを成功"},
    {"key": "turn_member_cost_play", "label": "nターン目にxコストメンバーをプレイ"},
    {"key": "turn_stage_cost_shape", "label": "nターン目のステージコストをa-b-cにする"},
)


def _first_int(value: Any) -> int | None:
    if value in (None, "", [], {}):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    match = re.search(r"-?\d+", str(value))
    return int(match.group(0)) if match else None


def _card_type_kind(record: dict[str, Any]) -> str:
    text = str(
        record.get("card_type_norm")
        or record.get("card_type")
        or record.get("card_type_raw")
        or record.get("type")
        or ""
    ).casefold()
    if "メンバー" in text or "member" in text:
        return "member"
    if "ライブ" in text or "live" in text:
        return "live"
    return "other"


def _card_name(record: dict[str, Any], card_no: str) -> str:
    return str(record.get("cardname") or record.get("name") or card_no)


def _deck_rows_expanded(rows: list[dict[str, str]]) -> list[tuple[str, int]]:
    expanded: list[tuple[str, int]] = []
    for row in rows:
        card_no = str(row.get("card_no") or "").strip()
        if not card_no:
            continue
        try:
            count = int(str(row.get("count") or "0"))
        except ValueError:
            continue
        if count > 0:
            expanded.append((card_no, count))
    return expanded


def _expanded_card_objects(rows: list[dict[str, str]], card_lookup: CardLookup) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    seq = 0
    for card_no, count in _deck_rows_expanded(rows):
        record = card_lookup(card_no)
        kind = _card_type_kind(record)
        cost = _first_int(record.get("cost")) if kind == "member" else None
        score = _first_int(record.get("score")) if kind == "live" else None
        effect_text = str(
            record.get("effect_text_norm")
            or record.get("effect_text")
            or record.get("ability_text")
            or ""
        )
        draw_n = _effect_draw_count(effect_text)
        enter_draw_n = _timed_effect_draw_count(effect_text, "登場")
        live_success_draw_n = _timed_effect_draw_count(effect_text, "ライブ成功時")
        activated_draw_n = _timed_effect_draw_count(effect_text, "起動")
        energy_boost_n = _effect_energy_boost_count(effect_text)
        enter_energy_boost_n = _timed_effect_energy_boost_count(effect_text, "登場")
        live_success_energy_boost_n = _timed_effect_energy_boost_count(effect_text, "ライブ成功時")
        energy_activate_n = _effect_energy_activate_count(effect_text)
        activated_energy_activate_n = _timed_effect_energy_activate_count(effect_text, "起動")
        enter_energy_activate_n = _timed_effect_energy_activate_count(effect_text, "登場")
        member_recovery_n = _effect_member_recovery_count(effect_text)
        live_success_member_recovery_n = _timed_effect_member_recovery_count(effect_text, "ライブ成功時")
        low_cost_summon_n = _effect_low_cost_stage_summon_count(effect_text)
        live_success_low_cost_summon_n = _effect_live_success_under_low_cost_summon_count(effect_text)
        enter_top_stack_n = _timed_effect_top_stack_count(effect_text, "登場")
        enter_top_search = _timed_effect_top_search_profile(effect_text, "登場")
        recovery_kind = _effect_recovery_kind(effect_text)
        activated_recovery_kind = _timed_effect_recovery_kind(effect_text, "起動")
        activated_self_to_green_cost = _timed_effect_has_self_stage_to_green_cost(effect_text, "起動")
        cost_reduction = _has_cost_reduction_signal(effect_text)
        cost_reduction_n = _effect_cost_reduction_amount(effect_text)
        free_member_play = _has_free_member_play_signal(effect_text)
        overcost_member_play = _has_overcost_member_play_signal(effect_text)
        progression_accel_value = _effect_progression_accel_value(effect_text)
        progression_support_tags = _progression_support_tags(effect_text)
        base_hearts_raw = record.get("base_hearts_raw") or record.get("hearts") or ""
        required_hearts_raw = record.get("required_hearts_raw") or record.get("required_hearts") or ""
        for _ in range(count):
            seq += 1
            cards.append({
                "id": seq,
                "card_no": card_no,
                "name": _card_name(record, card_no),
                "kind": kind,
                "group": str(record.get("group") or ""),
                "unit": str(record.get("unit") or ""),
                "work_title": str(record.get("work_title") or ""),
                "cost": cost,
                "score": score,
                "base_hearts_raw": str(base_hearts_raw or ""),
                "required_hearts_raw": str(required_hearts_raw or ""),
                "blade_heart_raw": str(record.get("blade_heart_raw") or ""),
                "blade_heart_total": _first_int(record.get("blade_heart_total")) or 0,
                "effect_text": effect_text,
                "draw_n": draw_n,
                "enter_draw_n": enter_draw_n,
                "live_success_draw_n": live_success_draw_n,
                "activated_draw_n": activated_draw_n,
                "energy_boost_n": energy_boost_n,
                "enter_energy_boost_n": enter_energy_boost_n,
                "live_success_energy_boost_n": live_success_energy_boost_n,
                "energy_activate_n": energy_activate_n,
                "activated_energy_activate_n": activated_energy_activate_n,
                "enter_energy_activate_n": enter_energy_activate_n,
                "member_recovery_n": member_recovery_n,
                "live_success_member_recovery_n": live_success_member_recovery_n,
                "low_cost_summon_n": low_cost_summon_n,
                "live_success_low_cost_summon_n": live_success_low_cost_summon_n,
                "enter_top_stack_n": enter_top_stack_n,
                "enter_top_search": dict(enter_top_search),
                "recovery_kind": recovery_kind,
                "activated_recovery_kind": activated_recovery_kind,
                "activated_self_to_green_cost": activated_self_to_green_cost,
                "cost_reduction": cost_reduction,
                "cost_reduction_n": cost_reduction_n,
                "free_member_play": free_member_play,
                "overcost_member_play": overcost_member_play,
                "progression_accel_value": progression_accel_value,
                "progression_support_tags": list(progression_support_tags),
                "value": int(cost or score or 0),
            })
    return cards


def _card_object_from_number(card_no: str, card_lookup: CardLookup, *, seq: int = 0) -> dict[str, Any]:
    record = card_lookup(card_no)
    kind = _card_type_kind(record)
    cost = _first_int(record.get("cost")) if kind == "member" else None
    score = _first_int(record.get("score")) if kind == "live" else None
    effect_text = str(
        record.get("effect_text_norm")
        or record.get("effect_text")
        or record.get("ability_text")
        or ""
    )
    return {
        "id": seq,
        "card_no": card_no,
        "name": _card_name(record, card_no),
        "kind": kind,
        "group": str(record.get("group") or ""),
        "unit": str(record.get("unit") or ""),
        "work_title": str(record.get("work_title") or ""),
        "cost": cost,
        "score": score,
        "base_hearts_raw": str(record.get("base_hearts_raw") or record.get("hearts") or ""),
        "required_hearts_raw": str(record.get("required_hearts_raw") or record.get("required_hearts") or ""),
        "blade_heart_raw": str(record.get("blade_heart_raw") or ""),
        "blade_heart_total": _first_int(record.get("blade_heart_total")) or 0,
        "value": int(cost or score or 0),
        "effect_text": effect_text,
        "draw_n": _effect_draw_count(effect_text),
        "enter_draw_n": _timed_effect_draw_count(effect_text, "登場"),
        "live_success_draw_n": _timed_effect_draw_count(effect_text, "ライブ成功時"),
        "activated_draw_n": _timed_effect_draw_count(effect_text, "起動"),
        "energy_boost_n": _effect_energy_boost_count(effect_text),
        "enter_energy_boost_n": _timed_effect_energy_boost_count(effect_text, "登場"),
        "live_success_energy_boost_n": _timed_effect_energy_boost_count(effect_text, "ライブ成功時"),
        "energy_activate_n": _effect_energy_activate_count(effect_text),
        "activated_energy_activate_n": _timed_effect_energy_activate_count(effect_text, "起動"),
        "enter_energy_activate_n": _timed_effect_energy_activate_count(effect_text, "登場"),
        "member_recovery_n": _effect_member_recovery_count(effect_text),
        "live_success_member_recovery_n": _timed_effect_member_recovery_count(effect_text, "ライブ成功時"),
        "low_cost_summon_n": _effect_low_cost_stage_summon_count(effect_text),
        "live_success_low_cost_summon_n": _effect_live_success_under_low_cost_summon_count(effect_text),
        "enter_top_stack_n": _timed_effect_top_stack_count(effect_text, "登場"),
        "enter_top_search": _timed_effect_top_search_profile(effect_text, "登場"),
        "recovery_kind": _effect_recovery_kind(effect_text),
        "activated_recovery_kind": _timed_effect_recovery_kind(effect_text, "起動"),
        "activated_self_to_green_cost": _timed_effect_has_self_stage_to_green_cost(effect_text, "起動"),
        "cost_reduction": _has_cost_reduction_signal(effect_text),
        "cost_reduction_n": _effect_cost_reduction_amount(effect_text),
        "free_member_play": _has_free_member_play_signal(effect_text),
        "overcost_member_play": _has_overcost_member_play_signal(effect_text),
        "progression_accel_value": _effect_progression_accel_value(effect_text),
        "progression_support_tags": _progression_support_tags(effect_text),
        "special_baton": _is_special_baton_signal(effect_text, int(cost or 0)),
    }


def _effect_draw_count(effect_text: str) -> int:
    text = str(effect_text or "")
    best = 0
    for match in re.finditer(r"カードを(\d+)枚引", text):
        best = max(best, int(match.group(1)))
    for match in re.finditer(r"カードを1枚引", text):
        best = max(best, 1)
    return best


def _effect_sections(effect_text: str) -> dict[str, str]:
    text = str(effect_text or "")
    sections: dict[str, list[str]] = {}
    current = "全体"
    sections.setdefault(current, [])
    for raw_line in text.splitlines():
        line = raw_line.strip()
        header = re.fullmatch(r"<([^<>]+)>", line)
        if header:
            label = header.group(1).strip()
            if label in {"登場", "起動", "ライブ開始時", "ライブ成功時", "常時", "自動"}:
                current = label
                sections.setdefault(current, [])
                continue
        sections.setdefault(current, []).append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def _timed_effect_text(effect_text: str, timing: str) -> str:
    return _effect_sections(effect_text).get(str(timing or ""), "")


def _timed_effect_draw_count(effect_text: str, timing: str) -> int:
    return _effect_draw_count(_timed_effect_text(effect_text, timing))


def _timed_effect_energy_boost_count(effect_text: str, timing: str) -> int:
    return _effect_energy_boost_count(_timed_effect_text(effect_text, timing))


def _timed_effect_energy_activate_count(effect_text: str, timing: str) -> int:
    return _effect_energy_activate_count(_timed_effect_text(effect_text, timing))


def _timed_effect_member_recovery_count(effect_text: str, timing: str) -> int:
    return _effect_member_recovery_count(_timed_effect_text(effect_text, timing))


def _effect_recovery_kind(effect_text: str) -> str:
    text = str(effect_text or "")
    if "控え室" not in text or "手札に加え" not in text:
        return ""
    if "ライブカード" in text:
        return "live"
    if "メンバーカード" in text or "メンバー" in text:
        return "member"
    if "カード" in text:
        return "card"
    return ""


def _timed_effect_recovery_kind(effect_text: str, timing: str) -> str:
    return _effect_recovery_kind(_timed_effect_text(effect_text, timing))


def _effect_has_self_stage_to_green_cost(effect_text: str) -> bool:
    text = str(effect_text or "")
    return "このメンバーをステージから控え室" in text


def _timed_effect_has_self_stage_to_green_cost(effect_text: str, timing: str) -> bool:
    return _effect_has_self_stage_to_green_cost(_timed_effect_text(effect_text, timing))


def _timed_effect_has_condition(effect_text: str, timing: str) -> bool:
    text = _timed_effect_text(effect_text, timing)
    return bool(re.search(r"場合|なら|かぎり|そうした場合|枚以上|同じ場合", text))


def _effect_energy_boost_count(effect_text: str) -> int:
    text = str(effect_text or "")
    if "相手" in text and "自分と相手" not in text:
        return 0
    matches = re.findall(r"エネルギーデッキから、?エネルギーカードを?(\d+)?枚(?:アクティブ|ウェイト)状態で置", text)
    if not matches:
        matches = re.findall(r"エネルギーデッキから、?エネルギーカード(\d+)?枚を", text)
    total = 0
    for value in matches:
        total = max(total, int(value or "1"))
    return total


def _effect_energy_activate_count(effect_text: str) -> int:
    text = str(effect_text or "")
    if "エネルギーデッキ" in text:
        return 0
    if "相手" in text and "自分と相手" not in text:
        return 0
    best = 0
    for match in re.finditer(r"エネルギー(?:カード)?を?(\d+)?枚(?:まで)?アクティブ", text):
        best = max(best, int(match.group(1) or "1"))
    for match in re.finditer(r"(\d+)枚(?:まで)?(?:を)?アクティブ", text):
        if "エネルギー" in text[max(0, match.start() - 16):match.start()]:
            best = max(best, int(match.group(1)))
    return best


def _effect_member_recovery_count(effect_text: str) -> int:
    text = str(effect_text or "")
    if "相手" in text and "自分と相手" not in text:
        return 0
    if "控え室" not in text or "手札に加える" not in text:
        return 0
    recovery_text = ""
    for match in re.finditer(r"控え室から(?P<body>[^。:：]*?)手札に加える", text):
        recovery_text += match.group("body")
    if not recovery_text:
        return 0
    if "メンバーカード" not in recovery_text and "メンバー" not in recovery_text:
        return 0
    match = re.search(r"メンバーカードを(\d+)枚", recovery_text)
    if match:
        return max(1, int(match.group(1)))
    match = re.search(r"メンバーを(\d+)枚", recovery_text)
    if match:
        return max(1, int(match.group(1)))
    return 1


def _effect_low_cost_stage_summon_count(effect_text: str) -> int:
    text = str(effect_text or "")
    if "コスト2以下" in text and "メンバー" in text and "登場させる" in text:
        return 1
    return 0


def _effect_live_success_under_low_cost_summon_count(effect_text: str) -> int:
    text = str(effect_text or "")
    if (
        "ライブ成功時" in text
        and "このメンバーの下" in text
        and "コスト2以下" in text
        and "メンバー" in text
        and "登場させ" in text
    ):
        return 1
    return 0


def _effect_progression_accel_value(effect_text: str) -> int:
    """Energy-equivalent progression value for deck-axis setup effects."""
    text = str(effect_text or "")
    value = 0
    value = max(value, _effect_energy_boost_count(text))
    value = max(value, _effect_energy_activate_count(text))
    value = max(value, _effect_cost_reduction_amount(text))
    if _has_free_member_play_signal(text) or _has_overcost_member_play_signal(text):
        value = max(value, 2)
    if _effect_low_cost_stage_summon_count(text) > 0:
        value = max(value, 2)
    if _effect_live_success_under_low_cost_summon_count(text) > 0:
        value = max(value, 2)
    return max(0, int(value))


def _effect_top_stack_count(effect_text: str) -> int:
    text = str(effect_text or "")
    if "デッキの上から" not in text or "見る" not in text:
        return 0
    if "好きな枚数" not in text or "好きな順番" not in text or "残りを控え室" not in text:
        return 0
    match = re.search(r"デッキの上からカードを?(\d+)枚見る", text)
    return int(match.group(1)) if match else 0


def _timed_effect_top_stack_count(effect_text: str, timing: str) -> int:
    return _effect_top_stack_count(_timed_effect_text(effect_text, timing))


def _effect_top_search_profile(effect_text: str) -> dict[str, Any]:
    text = str(effect_text or "")
    if "デッキの上から" not in text or "見る" not in text or "手札に加え" not in text:
        return {}
    match = re.search(r"デッキの上からカードを?(\d+)枚見る", text)
    if not match:
        return {}
    group_match = re.search(r"『([^』]+)』", text)
    return {
        "look_n": int(match.group(1)),
        "member_only": "メンバーカード" in text or "メンバー" in text,
        "no_blade_heart": "ブレードハートを持たない" in text,
        "group": group_match.group(1) if group_match else "",
        "discard_hand_cost_n": 1 if "手札を1枚控え室" in text else 0,
    }


def _timed_effect_top_search_profile(effect_text: str, timing: str) -> dict[str, Any]:
    return _effect_top_search_profile(_timed_effect_text(effect_text, timing))


def _has_cost_reduction_signal(effect_text: str) -> bool:
    text = str(effect_text or "")
    return bool(re.search(r"コスト.*(?:減|少なく|軽減)|(?:減|少なく|軽減).*コスト", text))


def _effect_cost_reduction_amount(effect_text: str) -> int:
    text = str(effect_text or "")
    if not _has_cost_reduction_signal(text):
        return 0
    best = 0
    for pattern in (
        r"コスト(?:は|を)?(\d+)減る",
        r"コスト(?:は|を)?(\d+)少なく",
        r"(\d+)減る",
    ):
        for match in re.finditer(pattern, text):
            if "コスト" not in text[max(0, match.start() - 18):match.end() + 18]:
                continue
            best = max(best, int(match.group(1)))
    return best or 2


def _has_free_member_play_signal(effect_text: str) -> bool:
    text = str(effect_text or "")
    if "メンバー" not in text or "登場" not in text:
        return False
    return bool(re.search(r"(?:コスト|エネルギー).*支払わず|支払わず.*登場|コストなし.*登場", text))


def _has_overcost_member_play_signal(effect_text: str) -> bool:
    text = str(effect_text or "")
    if "メンバー" not in text or "登場" not in text:
        return False
    return bool(
        re.search(r"コスト\d+以下.*登場|合計コスト.*以下.*登場|払った.*コスト.*より.*大き", text)
    )


def _progression_support_tags(effect_text: str) -> list[str]:
    tags: list[str] = []
    if _effect_progression_accel_value(effect_text) >= 2:
        tags.append("major_acceleration")
    if _effect_energy_boost_count(effect_text) > 0:
        tags.append("energy_boost")
    if _effect_energy_activate_count(effect_text) > 0:
        tags.append("energy_activate")
    if _effect_member_recovery_count(effect_text) > 0:
        tags.append("member_recovery")
    if _has_cost_reduction_signal(effect_text):
        tags.append("cost_reduction")
    if _has_free_member_play_signal(effect_text):
        tags.append("free_member_play")
    if _has_overcost_member_play_signal(effect_text):
        tags.append("overcost_member_play")
    if _effect_low_cost_stage_summon_count(effect_text) > 0:
        tags.append("low_cost_summon")
    if _effect_live_success_under_low_cost_summon_count(effect_text) > 0:
        tags.append("live_success_low_cost_summon")
    return tags


def _is_special_baton_signal(effect_text: str, cost: int) -> bool:
    text = str(effect_text or "")
    if "バトンタッチ" not in text or cost < 10:
        return False
    if re.search(r"バトンタッチして登場した場合|バトンタッチしていた場合", text):
        return False
    return bool(
        re.search(r"登場させる|手札から.*登場|コスト\d+以下.*登場|このメンバーをステージから控え室に置く", text)
    )


def build_deck_curve(rows: list[dict[str, str]], card_lookup: CardLookup) -> dict[str, Any]:
    member_costs: Counter[int] = Counter()
    live_scores: Counter[int] = Counter()
    member_examples: dict[int, list[dict[str, Any]]] = {}
    live_examples: dict[int, list[dict[str, Any]]] = {}
    totals = {"member": 0, "live": 0, "other": 0, "cards": 0}
    special_signals: dict[str, list[dict[str, Any]]] = {
        "major_acceleration": [],
        "energy_boost": [],
        "energy_activate": [],
        "cost_reduction": [],
        "free_member_play": [],
        "overcost_member_play": [],
        "member_recovery": [],
        "live_member_recovery": [],
        "low_cost_summon": [],
        "live_success_low_cost_summon": [],
        "special_baton": [],
        "high_cost_anchor": [],
    }

    for card_no, count in _deck_rows_expanded(rows):
        record = card_lookup(card_no)
        kind = _card_type_kind(record)
        totals[kind if kind in totals else "other"] += count
        totals["cards"] += count
        if kind == "member":
            cost = _first_int(record.get("cost"))
            if cost is None:
                continue
            member_costs[cost] += count
            effect_text = str(
                record.get("effect_text_norm")
                or record.get("effect_text")
                or record.get("ability_text")
                or ""
            )
            signal_item = {"card_no": card_no, "name": _card_name(record, card_no), "count": count, "cost": cost}
            accel_value = _effect_progression_accel_value(effect_text)
            if accel_value >= 2 and len(special_signals["major_acceleration"]) < 12:
                special_signals["major_acceleration"].append({**signal_item, "accel_value": accel_value})
            if cost >= 15 and len(special_signals["high_cost_anchor"]) < 8:
                special_signals["high_cost_anchor"].append(signal_item)
            if _has_cost_reduction_signal(effect_text) and len(special_signals["cost_reduction"]) < 8:
                special_signals["cost_reduction"].append(signal_item)
            if _effect_energy_activate_count(effect_text) > 0 and len(special_signals["energy_activate"]) < 8:
                special_signals["energy_activate"].append(signal_item)
            if _effect_member_recovery_count(effect_text) > 0 and len(special_signals["member_recovery"]) < 8:
                special_signals["member_recovery"].append(signal_item)
            if _has_free_member_play_signal(effect_text) and len(special_signals["free_member_play"]) < 8:
                special_signals["free_member_play"].append(signal_item)
            if _has_overcost_member_play_signal(effect_text) and len(special_signals["overcost_member_play"]) < 8:
                special_signals["overcost_member_play"].append(signal_item)
            if _effect_low_cost_stage_summon_count(effect_text) > 0 and len(special_signals["low_cost_summon"]) < 8:
                special_signals["low_cost_summon"].append(signal_item)
            if _effect_live_success_under_low_cost_summon_count(effect_text) > 0 and len(special_signals["live_success_low_cost_summon"]) < 8:
                special_signals["live_success_low_cost_summon"].append(signal_item)
            if _is_special_baton_signal(effect_text, cost) and len(special_signals["special_baton"]) < 8:
                special_signals["special_baton"].append(signal_item)
            member_examples.setdefault(cost, [])
            if len(member_examples[cost]) < 4:
                member_examples[cost].append({
                    "card_no": card_no,
                    "name": _card_name(record, card_no),
                    "count": count,
                })
        elif kind == "live":
            score = _first_int(record.get("score"))
            if score is None:
                continue
            effect_text = str(
                record.get("effect_text_norm")
                or record.get("effect_text")
                or record.get("ability_text")
                or ""
            )
            signal_item = {"card_no": card_no, "name": _card_name(record, card_no), "count": count, "score": score}
            accel_value = _effect_progression_accel_value(effect_text)
            if accel_value >= 2 and len(special_signals["major_acceleration"]) < 12:
                special_signals["major_acceleration"].append({**signal_item, "accel_value": accel_value})
            if _effect_energy_boost_count(effect_text) > 0 and len(special_signals["energy_boost"]) < 8:
                special_signals["energy_boost"].append(signal_item)
            if _effect_member_recovery_count(effect_text) > 0 and len(special_signals["live_member_recovery"]) < 8:
                special_signals["live_member_recovery"].append(signal_item)
            live_scores[score] += count
            live_examples.setdefault(score, [])
            if len(live_examples[score]) < 4:
                live_examples[score].append({
                    "card_no": card_no,
                    "name": _card_name(record, card_no),
                    "count": count,
                })

    return {
        "totals": totals,
        "member_costs": dict(sorted(member_costs.items())),
        "live_scores": dict(sorted(live_scores.items())),
        "member_cost_bands": {
            "low_2_4": sum(count for cost, count in member_costs.items() if 2 <= cost <= 4),
            "mid_5_10": sum(count for cost, count in member_costs.items() if 5 <= cost <= 10),
            "bridge_11_14": sum(count for cost, count in member_costs.items() if 11 <= cost <= 14),
            "high_15_plus": sum(count for cost, count in member_costs.items() if cost >= 15),
        },
        "special_signals": special_signals,
        "member_examples": member_examples,
        "live_examples": live_examples,
    }


def _progression_needs(template: CostProgressionTemplate) -> Counter[int]:
    needs: Counter[int] = Counter()
    for turn in template.turns:
        needs.update(turn)
    return needs


def _signal_costs(signals: dict[str, Any], key: str) -> set[int]:
    return {
        int(item.get("cost") or 0)
        for item in signals.get(key, []) or []
        if isinstance(item, dict) and item.get("cost") is not None
    }


def _progression_energy_profile(
    turns: tuple[tuple[int, ...], ...],
    special_signals: dict[str, Any],
) -> dict[str, Any]:
    active = 3
    wait = 0
    deck_remaining = 9
    stage_costs: list[int] = []
    energy_activate_costs = _signal_costs(special_signals, "energy_activate")
    cost_reduction_costs = _signal_costs(special_signals, "cost_reduction")
    direct_turns = 0
    bridge_turns = 0
    shortfall = 0
    details: list[str] = []
    has_energy_boost = bool(special_signals.get("energy_boost"))
    for turn_index, turn in enumerate(turns, start=1):
        active += wait
        wait = 0
        if deck_remaining > 0:
            active += 1
            deck_remaining -= 1
        if any(cost in energy_activate_costs for cost in stage_costs):
            active += 1
        needed = _min_active_needed_to_reach_shape_from_costs(
            stage_costs,
            list(turn),
            cost_reduction_costs=cost_reduction_costs,
            reduction_enabled=bool(set(stage_costs) & energy_activate_costs),
        )
        if needed <= active:
            direct_turns += 1
            active -= needed
            wait += needed
            details.append(f"T{turn_index}:direct need={needed}")
        elif turn_index > 1 and has_energy_boost and needed <= active + 1 and deck_remaining > 0:
            bridge_turns += 1
            deck_remaining -= 1
            active = active + 1 - needed
            wait += needed
            details.append(f"T{turn_index}:boost need={needed}")
        else:
            gap = max(0, needed - active)
            shortfall += gap
            wait += max(0, active)
            active = 0
            details.append(f"T{turn_index}:short need={needed} gap={gap}")
        stage_costs = sorted([int(value) for value in turn], reverse=True)
    score = (direct_turns * 8.0) - (bridge_turns * 4.0) - (shortfall * 12.0)
    return {
        "score": round(score, 2),
        "direct_turns": direct_turns,
        "bridge_turns": bridge_turns,
        "shortfall": shortfall,
        "details": details,
    }


def evaluate_progression(
    curve: dict[str, Any],
    template: CostProgressionTemplate,
) -> dict[str, Any]:
    member_costs = Counter({int(k): int(v) for k, v in dict(curve.get("member_costs") or {}).items()})
    needs = _progression_needs(template)
    missing: dict[int, int] = {}
    unavailable: list[int] = []
    coverage_parts: list[float] = []
    for cost, needed in sorted(needs.items()):
        have = int(member_costs.get(cost, 0))
        if have <= 0:
            unavailable.append(cost)
        coverage_parts.append(min(1.0, have / max(1, needed * 3)))
        if have < needed:
            missing[cost] = needed - have

    first_turn = template.turns[0] if template.turns else ()
    hand_pressure = sum(len(turn) for turn in template.turns[:2])
    low_cost_support = int(member_costs.get(2, 0))
    cost_bands = curve.get("member_cost_bands") if isinstance(curve.get("member_cost_bands"), dict) else {}
    special_signals = curve.get("special_signals") if isinstance(curve.get("special_signals"), dict) else {}
    early_score_bonus = min(12, low_cost_support) / 12.0 if first_turn == (2, 2) else 0.0
    mid_curve_bonus = min(1.0, float(cost_bands.get("mid_5_10", 0) or 0) / 16.0) * 8.0
    late_bonus = 0.0
    special_bonus = 0.0
    if template.phase in {"late", "late_special", "high_cost_rush"}:
        late_bonus = min(1.0, float(cost_bands.get("high_15_plus", 0) or 0) / 8.0) * 14.0
    if template.phase == "late_special":
        special_bonus += min(1.0, len(special_signals.get("special_baton", []) or []) / 2.0) * 10.0
    if template.phase == "dynamic_energy_activate":
        special_bonus += 34.0
    if special_signals.get("cost_reduction"):
        special_bonus += 3.0
    major_accel_count = len(special_signals.get("major_acceleration", []) or [])
    if major_accel_count:
        special_bonus += min(1.0, major_accel_count / 4.0) * 18.0
    energy_profile = _progression_energy_profile(template.turns, special_signals)
    early_scarcity_penalty = 0.0
    for turn in template.turns[:3]:
        for cost, needed in Counter(int(value) for value in turn).items():
            if cost < 5:
                continue
            have = int(member_costs.get(cost, 0) or 0)
            desired_copies = max(3, int(needed) * 3)
            if have < desired_copies:
                early_scarcity_penalty += (desired_copies - have) * 4.0
    coverage = sum(coverage_parts) / max(1, len(coverage_parts))
    score = round(
        (coverage * 72.0)
        + (early_score_bonus * 10.0)
        + mid_curve_bonus
        + late_bonus
        + special_bonus
        + float(energy_profile.get("score") or 0.0)
        - early_scarcity_penalty
        - max(0, hand_pressure - 5) * 2.0,
        2,
    )

    return {
        "key": template.key,
        "label": template.label,
        "intent": template.intent,
        "phase": template.phase,
        "source": "dynamic" if str(template.key).startswith("dynamic_") else "template",
        "turns": [list(turn) for turn in template.turns],
        "score": score,
        "coverage": round(coverage, 3),
        "energy_path": energy_profile,
        "early_scarcity_penalty": round(early_scarcity_penalty, 2),
        "missing_costs": missing,
        "unavailable_costs": unavailable,
        "strengths": list(template.strengths),
        "risks": list(template.risks),
    }


def _dynamic_template_key(turns: tuple[tuple[int, ...], ...]) -> str:
    return "dynamic_" + "_".join("-".join(str(value) for value in sorted(turn, reverse=True)) for turn in turns)


def _normalized_turns(turns: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(sorted((int(value) for value in turn), reverse=True)) for turn in turns)


def _cost_count(member_costs: Counter[int], cost: int) -> int:
    return int(member_costs.get(int(cost), 0) or 0)


def _best_cost_at_least(member_costs: Counter[int], minimum: int, maximum: int | None = None) -> int | None:
    candidates = [
        int(cost)
        for cost, count in member_costs.items()
        if int(count or 0) > 0
        and int(cost) >= int(minimum)
        and (maximum is None or int(cost) <= int(maximum))
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda cost: (abs(cost - minimum), -_cost_count(member_costs, cost), cost))


def _best_cost_in_band(member_costs: Counter[int], low: int, high: int) -> int | None:
    candidates = [
        int(cost)
        for cost, count in member_costs.items()
        if int(count or 0) > 0 and int(low) <= int(cost) <= int(high)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda cost: (_cost_count(member_costs, cost), -abs(cost - ((low + high) // 2)), -cost))


def _energy_activate_member_costs_from_cards(cards: list[dict[str, Any]]) -> list[int]:
    return sorted({
        int(card.get("cost") or 0)
        for card in cards
        if card.get("kind") == "member"
        and card.get("cost") is not None
        and int(card.get("energy_activate_n") or 0) > 0
    })


def _cost_reduction_high_costs_from_cards(cards: list[dict[str, Any]]) -> list[int]:
    return sorted({
        int(card.get("cost") or 0)
        for card in cards
        if card.get("kind") == "member"
        and card.get("cost") is not None
        and int(card.get("cost") or 0) >= 15
        and bool(card.get("cost_reduction"))
    })


def _energy_activate_curve_shape_set(deck_cards: list[dict[str, Any]]) -> dict[str, Any]:
    costs = _member_cost_counts(deck_cards)
    activators = [cost for cost in _energy_activate_member_costs_from_cards(deck_cards) if 7 <= cost <= 11]
    high_costs = _cost_reduction_high_costs_from_cards(deck_cards)
    if not activators or not high_costs or costs.get(4, 0) <= 0 or costs.get(2, 0) <= 0:
        return {}
    accel = activators[0]
    high = high_costs[-1]
    late_mid_candidates = [
        cost for cost, count in sorted(costs.items())
        if int(count or 0) > 0 and 12 <= int(cost) < high
    ]
    if costs.get(13, 0) > 0:
        late_mid = 13
    else:
        late_mid = late_mid_candidates[-1] if late_mid_candidates else high
    return {
        "accelerator_cost": accel,
        "high_cost": high,
        "late_mid_cost": late_mid,
        "t1": [2, 2],
        "t2": [4, 2, 2],
        "t3": [accel, 4, 2],
        "t3_alt_high": [11, 2, 2] if costs.get(11, 0) > 0 and costs.get(2, 0) >= 2 else [],
        "t3_alt_single": [high, 2] if costs.get(high, 0) > 0 and costs.get(2, 0) > 0 else [],
        "t4": [high, accel, 2],
        "t5": [high, late_mid, 2],
        "t5_alt": [high, high, 2] if costs.get(high, 0) >= 2 and costs.get(2, 0) > 0 else [],
    }


def _dynamic_progression_templates(curve: dict[str, Any]) -> list[CostProgressionTemplate]:
    member_costs = Counter({int(k): int(v) for k, v in dict(curve.get("member_costs") or {}).items()})
    signals = curve.get("special_signals") if isinstance(curve.get("special_signals"), dict) else {}
    has_energy_boost = bool(signals.get("energy_boost"))
    has_cost_skip = any(bool(signals.get(key)) for key in ("cost_reduction", "free_member_play", "overcost_member_play", "energy_activate"))
    low_twos = _cost_count(member_costs, 2)
    fours = _cost_count(member_costs, 4)
    templates: list[CostProgressionTemplate] = []
    t1_shapes: list[tuple[int, ...]] = []
    if low_twos >= 8:
        t1_shapes.append((2, 2))
    if fours >= 2:
        t1_shapes.append((4,))
    if not t1_shapes:
        first = _best_cost_in_band(member_costs, 2, 4)
        if first is not None:
            t1_shapes.append((first,))
    mid_candidates = [
        cost for cost, count in sorted(member_costs.items())
        if 5 <= int(cost) <= 8 and int(count or 0) > 0
    ]
    if fours >= 2 and has_energy_boost:
        mid_candidates = [4] + mid_candidates
    for t1 in t1_shapes:
        for mid in mid_candidates:
            mid = int(mid)
            t2_shapes: list[tuple[int, ...]] = []
            if t1 == (2, 2) and low_twos >= 8 and mid >= 5:
                if mid <= 5:
                    t2_shapes.append(tuple(sorted((2, mid, 2), reverse=True)))
                else:
                    t2_shapes.append(tuple(sorted((mid, 2), reverse=True)))
            if fours >= 2 and low_twos >= 8 and (has_energy_boost or mid in {4, 5, 10, 11}):
                t2_shapes.append((4, 2, 2))
            if t1 == (4,) and mid >= 5:
                t2_shapes.append(tuple(sorted((mid, 2), reverse=True)) if low_twos >= 4 and mid <= 7 else (mid,))
            for t2 in list(dict.fromkeys(t2_shapes)):
                if mid == 4:
                    desired = 10
                elif mid <= 5:
                    desired = 11
                elif mid <= 7:
                    desired = 13
                elif mid <= 9:
                    desired = 15
                else:
                    desired = 10
                high = _best_cost_at_least(member_costs, desired, 16)
                if high is None and has_cost_skip:
                    high = _best_cost_at_least(member_costs, desired, None)
                if high is None:
                    continue
                if low_twos >= 8:
                    t3 = tuple(sorted((2, high, 2), reverse=True))
                else:
                    t3 = (high,)
                turns = _normalized_turns((tuple(t1), tuple(t2), tuple(t3)))
                label = "dynamic " + " -> ".join("-".join(str(value) for value in turn) for turn in turns)
                strengths = ["デッキ内のコスト分布から生成"]
                if has_energy_boost:
                    strengths.append("エネルギー追加ライブを進行補助として考慮")
                if has_cost_skip:
                    strengths.append("軽減/踏み倒し/エネルギー起動系の採用を考慮")
                templates.append(CostProgressionTemplate(
                    key=_dynamic_template_key(turns),
                    label=label,
                    turns=turns,
                    intent="デッキ構築から動的に推定したステージ進行",
                    phase="dynamic",
                    strengths=tuple(strengths),
                    risks=("実カード効果の発動条件は軽量評価",),
                ))
    signal_cards: list[dict[str, Any]] = []
    for key in ("energy_activate", "cost_reduction"):
        for item in signals.get(key, []) or []:
            if isinstance(item, dict):
                signal_cards.extend([{
                    "kind": "member",
                    "cost": item.get("cost"),
                    "energy_activate_n": 1 if key == "energy_activate" else 0,
                    "cost_reduction": key == "cost_reduction",
                }] * max(1, int(item.get("count") or 1)))
    curve_shapes = _energy_activate_curve_shape_set(signal_cards + [
        {"kind": "member", "cost": cost}
        for cost, count in member_costs.items()
        for _ in range(max(0, int(count)))
    ])
    if curve_shapes:
        turns = _normalized_turns((
            tuple(curve_shapes["t1"]),
            tuple(curve_shapes["t2"]),
            tuple(curve_shapes["t3"]),
            tuple(curve_shapes["t4"]),
            tuple(curve_shapes["t5"]),
        ))
        templates.append(CostProgressionTemplate(
            key=_dynamic_template_key(turns),
            label=(
                "dynamic energy-activate "
                + " -> ".join("-".join(str(value) for value in turn) for turn in turns)
            ),
            turns=turns,
            intent="エネルギーアクティブ化メンバーを盤面に残して高コストへ伸ばす進行",
            phase="dynamic_energy_activate",
            strengths=(
                "9前後のエネルギーアクティブ化メンバーを加速札として考慮",
                "17前後の軽減持ち高コストを後続到達先として考慮",
            ),
            risks=("加速札の起動条件とウェイト状態管理は軽量評価",),
        ))
    out: list[CostProgressionTemplate] = []
    seen: set[tuple[tuple[int, ...], ...]] = set()
    for template in sorted(templates, key=lambda item: (_normalized_turns(item.turns), item.key)):
        normalized = _normalized_turns(template.turns)
        if normalized in seen:
            continue
        seen.add(normalized)
        out.append(template)
    return out


def _best_member_for_cost(hand: list[dict[str, Any]], target_cost: int, max_cost: int | None = None) -> dict[str, Any] | None:
    candidates = [
        card for card in hand
        if card.get("kind") == "member"
        and card.get("cost") is not None
        and (max_cost is None or int(card.get("cost") or 0) <= max_cost)
    ]
    if not candidates:
        return None
    above = [card for card in candidates if int(card.get("cost") or 0) > target_cost]
    if above:
        return max(above, key=lambda card: (int(card.get("cost") or 0), str(card.get("card_no") or "")))
    exact = [card for card in candidates if int(card.get("cost") or 0) == target_cost]
    if exact:
        return max(exact, key=lambda card: (int(card.get("value") or 0), str(card.get("card_no") or "")))
    return max(candidates, key=lambda card: (int(card.get("cost") or 0), int(card.get("value") or 0)))


def _choose_stage_for_turn(hand: list[dict[str, Any]], target_shape: list[int]) -> list[dict[str, Any]]:
    remaining = list(hand)
    chosen: list[dict[str, Any]] = []
    sorted_targets = sorted(target_shape, reverse=True)
    remaining_budget = sum(sorted_targets)
    for index, target_cost in enumerate(sorted_targets):
        future_minimum = sum(sorted_targets[index + 1:])
        max_cost = max(target_cost, remaining_budget - future_minimum)
        card = _best_member_for_cost(remaining, target_cost, max_cost=max_cost)
        if card is None:
            continue
        chosen.append(card)
        remaining.remove(card)
        remaining_budget -= int(card.get("cost") or 0)
    return sorted(chosen, key=lambda card: int(card.get("cost") or 0), reverse=True)


def _choose_planning_shape(hand: list[dict[str, Any]], alternatives: list[list[int]]) -> list[int]:
    best_shape: list[int] = alternatives[0] if alternatives else []
    best_score = -1
    for shape in alternatives:
        remaining = list(hand)
        exact = 0
        covered = 0
        total = 0
        for target in sorted(shape, reverse=True):
            total += target
            card = _best_member_for_cost(remaining, target)
            if card is None:
                continue
            remaining.remove(card)
            cost = int(card.get("cost") or 0)
            if cost == target:
                exact += 1
            if cost >= target:
                covered += 1
        score = covered * 100 + exact * 10 - total
        if score > best_score:
            best_score = score
            best_shape = list(shape)
    return best_shape


def _shape_meets_target(costs: list[int], target_shape: list[int]) -> bool:
    available = sorted([int(cost) for cost in costs], reverse=True)
    targets = sorted([int(cost) for cost in target_shape], reverse=True)
    for target in targets:
        match_index = next((index for index, cost in enumerate(available) if cost >= target), None)
        if match_index is None:
            return False
        available.pop(match_index)
    return True


def _shape_meets_early_plan_slots(costs: list[int], target_shape: list[int]) -> bool:
    """Conservative visible-card check for mulligan T1/T2 plan security.

    General stage evaluation allows over-target placement, but using a 17-cost
    card to satisfy an opening 4-cost slot makes mulligan decisions unstable.
    For early planning, low/mid slots require the actual slot cost or the next
    cost band only; high slots keep the normal over-target rule.
    """
    available = sorted([int(cost) for cost in costs], reverse=True)
    targets = sorted([int(cost) for cost in target_shape], reverse=True)
    for target in targets:
        if target <= 10:
            match_index = next(
                (index for index, cost in enumerate(available) if target <= cost <= target + 1),
                None,
            )
        else:
            match_index = next((index for index, cost in enumerate(available) if cost >= target), None)
        if match_index is None:
            return False
        available.pop(match_index)
    return True


def _missing_for_shape(costs: list[int], target_shape: list[int]) -> list[int]:
    available = sorted([int(cost) for cost in costs], reverse=True)
    missing: list[int] = []
    for target in sorted([int(cost) for cost in target_shape], reverse=True):
        match_index = next((index for index, cost in enumerate(available) if cost >= target), None)
        if match_index is None:
            missing.append(target)
        else:
            available.pop(match_index)
    return missing


def _miss_reason(costs: list[int], alternatives: list[list[int]]) -> str:
    if not alternatives:
        return "no accepted target"
    best_missing = min(
        (_missing_for_shape(costs, alternative) for alternative in alternatives),
        key=lambda values: (len(values), sum(values)),
    )
    if not best_missing:
        return "unknown miss"
    return "missing " + "-".join(str(value) for value in best_missing)


def _stage_costs(stage: list[dict[str, Any] | None]) -> list[int]:
    return sorted(
        [int(card.get("cost") or 0) for card in stage if card and card.get("kind") == "member"],
        reverse=True,
    )


def _stage_text(stage: list[dict[str, Any] | None]) -> str:
    costs = _stage_costs(stage)
    return "-".join(str(cost) for cost in costs) if costs else "none"


def _stage_costs_with_virtual_low_summons(stage: list[dict[str, Any] | None]) -> list[int]:
    costs = _stage_costs(stage)
    bonus_costs: list[int] = []
    for card in stage:
        if not card:
            continue
        for _ in range(int(card.get("low_cost_summon_n") or 0)):
            if len(costs) + len(bonus_costs) < 3:
                bonus_costs.append(2)
    return sorted(costs + bonus_costs, reverse=True)


def _stage_score(stage: list[dict[str, Any] | None], target_shape: list[int]) -> int:
    costs = _stage_costs(stage)
    available = sorted(costs, reverse=True)
    targets = sorted([int(value) for value in target_shape], reverse=True)
    score = 0
    for target in targets:
        if not available:
            score -= target * 4
            continue
        above = [(index, cost) for index, cost in enumerate(available) if cost > target]
        exact = [(index, cost) for index, cost in enumerate(available) if cost == target]
        below = [(index, cost) for index, cost in enumerate(available) if cost < target]
        if above:
            index, cost = max(above, key=lambda item: item[1])
            score += 130 + min(20, cost - target)
        elif exact:
            index, cost = exact[0]
            score += 110
        elif below:
            index, cost = max(below, key=lambda item: item[1])
            score += 40 + cost
        else:
            continue
        available.pop(index)
    score += min(len(targets), len(costs)) * 5
    return score


def _best_target_shape_for_stage(stage: list[dict[str, Any] | None], alternatives: list[list[int]]) -> list[int]:
    if not alternatives:
        return []
    return max(alternatives, key=lambda shape: (_stage_score(stage, shape), sum(shape)))


def _stage_slots_to_replace(stage: list[dict[str, Any] | None], target_shape: list[int]) -> list[int]:
    if not stage:
        return []
    empty = [index for index, card in enumerate(stage) if card is None]
    replace = [index for index, card in enumerate(stage) if card is not None]
    replace.sort(key=lambda index: int((stage[index] or {}).get("cost") or 0))
    return empty + replace


def _cost_reduction_available_for_stage(stage: list[dict[str, Any] | None] | None) -> bool:
    return any(
        bool(card)
        and card.get("kind") == "member"
        and int(card.get("activated_energy_activate_n") or 0) > 0
        for card in stage or []
    )


def _member_play_cost_for_slot(
    card: dict[str, Any],
    old_card: dict[str, Any] | None,
    stage: list[dict[str, Any] | None] | None = None,
) -> int:
    cost = max(0, int(card.get("cost") or 0))
    if bool(card.get("cost_reduction")) and _cost_reduction_available_for_stage(stage):
        cost = max(0, cost - max(1, int(card.get("cost_reduction_n") or 2)))
    if old_card is None:
        return cost
    old_cost = max(0, int(old_card.get("cost") or 0))
    return max(0, cost - old_cost)


def _slot_satisfies_nonreplaceable_target(
    stage: list[dict[str, Any] | None],
    slot: int,
    target_shape: list[int],
) -> bool:
    if slot >= len(stage):
        return False
    old_card = stage[slot]
    if not old_card or old_card.get("kind") != "member" or old_card.get("cost") is None:
        return False
    old_cost = int(old_card.get("cost") or 0)
    target_need = Counter(int(value) for value in target_shape)
    if target_need.get(old_cost, 0) <= 0:
        return False
    current_count = sum(
        1 for card in stage
        if card and card.get("kind") == "member" and int(card.get("cost") or 0) == old_cost
    )
    return current_count <= int(target_need.get(old_cost, 0) or 0)


def _improve_persistent_stage(
    stage: list[dict[str, Any] | None],
    hand: list[dict[str, Any]],
    alternatives: list[list[int]],
    energy_state: dict[str, int] | None = None,
    planning_alternatives: list[list[int]] | None = None,
) -> list[dict[str, Any] | None]:
    if len(stage) < 3:
        stage.extend([None] * (3 - len(stage)))
    best_shape = _best_target_shape_for_stage(stage, planning_alternatives or alternatives)
    if not best_shape:
        return stage
    start_active = None if energy_state is None else max(0, int(energy_state.get("active", 0) or 0))
    start_wait = 0 if energy_state is None else max(0, int(energy_state.get("wait", 0) or 0))
    best_result: tuple[int, int, int, int, list[dict[str, Any] | None], list[dict[str, Any]], int, int] | None = None

    def remember(cur_stage: list[dict[str, Any] | None], cur_hand: list[dict[str, Any]], active: int | None, wait: int) -> None:
        nonlocal best_result
        score = _stage_score(cur_stage, best_shape)
        active_score = 999 if active is None else active
        total_cost = sum(_stage_costs(cur_stage))
        result = (score, active_score, -len(cur_hand), total_cost, list(cur_stage), list(cur_hand), active_score, wait)
        if best_result is None or result[:4] > best_result[:4]:
            best_result = result

    def walk(cur_stage: list[dict[str, Any] | None], cur_hand: list[dict[str, Any]], active: int | None, wait: int, depth: int) -> None:
        remember(cur_stage, cur_hand, active, wait)
        if depth >= 3:
            return
        cur_costs = _stage_costs_with_virtual_low_summons(cur_stage)
        if any(_shape_meets_target(cur_costs, sorted(alternative, reverse=True)) for alternative in alternatives):
            return
        current_missing_score = min(
            (len(_missing_for_shape(cur_costs, alternative)), sum(_missing_for_shape(cur_costs, alternative)))
            for alternative in alternatives
        )
        current_score = _stage_score(cur_stage, best_shape)
        has_empty_slot = any(slot_card is None for slot_card in cur_stage)
        for slot in _stage_slots_to_replace(cur_stage, best_shape):
            if _slot_satisfies_nonreplaceable_target(cur_stage, slot, best_shape):
                continue
            old_card = cur_stage[slot]
            for idx, card in enumerate(cur_hand):
                if card.get("kind") != "member" or card.get("cost") is None:
                    continue
                if old_card is not None and has_empty_slot:
                    full_play_cost = _member_play_cost_for_slot(card, None, cur_stage)
                    if active is None or full_play_cost <= active:
                        continue
                pay_cost = _member_play_cost_for_slot(card, old_card, cur_stage)
                if active is not None and pay_cost > active:
                    continue
                trial_stage = list(cur_stage)
                trial_stage[slot] = card
                trial_costs = _stage_costs_with_virtual_low_summons(trial_stage)
                trial_missing_score = min(
                    (len(_missing_for_shape(trial_costs, alternative)), sum(_missing_for_shape(trial_costs, alternative)))
                    for alternative in alternatives
                )
                if trial_missing_score >= current_missing_score and not any(
                    _shape_meets_target(trial_costs, sorted(alternative, reverse=True))
                    for alternative in alternatives
                ):
                    continue
                if _stage_score(trial_stage, best_shape) <= current_score:
                    continue
                trial_hand = list(cur_hand)
                trial_hand.pop(idx)
                next_active = None if active is None else active - pay_cost
                next_wait = wait + pay_cost
                enter_activate = int(card.get("enter_energy_activate_n") or 0)
                if next_active is not None and enter_activate > 0 and next_wait > 0:
                    activated = min(enter_activate, next_wait)
                    next_active += activated
                    next_wait -= activated
                walk(trial_stage, trial_hand, next_active, next_wait, depth + 1)

    walk(list(stage), list(hand), start_active, start_wait, 0)
    if best_result is None:
        return stage
    stage[:] = best_result[4]
    hand[:] = best_result[5]
    if energy_state is not None:
        energy_state["active"] = 0 if start_active is None else int(best_result[6])
        energy_state["wait"] = int(best_result[7])
    return stage


def _apply_stage_energy_activation_support(
    stage: list[dict[str, Any] | None],
    hand: list[dict[str, Any]],
    deck_cards: list[dict[str, Any]],
    alternatives: list[list[int]],
    energy_state: dict[str, int],
    future_alternatives_by_turn: list[list[list[int]]] | None,
    *,
    start_turn_index: int = 0,
) -> dict[str, Any]:
    original_active = max(0, int(energy_state.get("active", 0) or 0))
    active = original_active
    wait = max(0, int(energy_state.get("wait", 0) or 0))
    if not hand or not alternatives:
        return {"activated": [], "discarded": [], "energy_before": active, "energy_after": active}
    useful_gap = 0
    for slot_card in stage:
        for card in hand:
            if card.get("kind") != "member" or card.get("cost") is None:
                continue
            pay_cost = _member_play_cost_for_slot(card, slot_card, stage)
            if pay_cost <= active:
                continue
            trial_stage = list(stage)
            try:
                slot = stage.index(slot_card)
            except ValueError:
                continue
            trial_stage[slot] = card
            trial_costs = _stage_costs_with_virtual_low_summons(trial_stage)
            if any(_shape_meets_target(trial_costs, sorted(alternative, reverse=True)) for alternative in alternatives):
                useful_gap = max(useful_gap, pay_cost - active)
    if useful_gap <= 0:
        return {"activated": [], "discarded": [], "energy_before": active, "energy_after": active}
    activated: list[dict[str, Any]] = []
    discarded: list[dict[str, Any]] = []
    for card in stage:
        if not card:
            continue
        activate_n = int(card.get("energy_activate_n") or 0)
        if activate_n <= 0:
            continue
        activated.append(card)
        active += activate_n
        effect_text = str(card.get("effect_text") or "")
        if "手札を1枚控え室" in _timed_effect_text(effect_text, "起動") and hand:
            discard = _discard_after_effect_draw(
                hand,
                deck_cards,
                future_alternatives_by_turn,
                start_turn_index=start_turn_index,
            )
            if discard is not None:
                discarded.append(discard)
        if active >= original_active + useful_gap:
            break
    energy_state["active"] = active
    energy_state["wait"] = wait
    return {
        "activated": activated,
        "discarded": discarded,
        "energy_before": original_active,
        "energy_after": active,
    }


def _card_need_score(card: dict[str, Any], target_turns: list[list[int]], deck_cards: list[dict[str, Any]]) -> float:
    if card.get("kind") == "member" and card.get("cost") is not None:
        cost = int(card.get("cost") or 0)
        deck_count = max(1, _member_cost_counts(deck_cards).get(cost, 1))
        scarcity = 6.0 / deck_count
        score = 0.0
        for turn_index, target_shape in enumerate(target_turns[:3]):
            turn_weight = [5.0, 4.0, 3.0][turn_index]
            needs = Counter(int(value) for value in target_shape)
            if cost in needs:
                score += turn_weight * needs[cost] * scarcity
            elif any(int(target) < cost <= int(target) + 1 for target in target_shape):
                score += turn_weight * 0.7 * scarcity
        if cost == 2 and deck_count >= 16:
            score *= 0.55
        return score
    if card.get("kind") == "live":
        score = 0.0
        if int(card.get("draw_n") or 0) > 0:
            score += 2.0
        if int(card.get("energy_boost_n") or 0) > 0:
            score += 5.0
        return score
    return 0.0


def _card_need_score_by_turn(
    card: dict[str, Any],
    target_alternatives_by_turn: list[list[list[int]]],
    deck_cards: list[dict[str, Any]],
    *,
    start_turn_index: int = 0,
) -> float:
    upcoming_max_cost = _upcoming_max_target_cost(target_alternatives_by_turn[:4])
    energy_bridge_route = _has_energy_bridge_route(target_alternatives_by_turn[:3])
    if card.get("kind") == "member" and card.get("cost") is not None:
        cost = int(card.get("cost") or 0)
        deck_count = max(1, _member_cost_counts(deck_cards).get(cost, 1))
        scarcity = 8.0 / deck_count
        score = 0.0
        for offset, alternatives in enumerate(target_alternatives_by_turn[:4]):
            absolute_turn = start_turn_index + offset
            turn_weight = [8.0, 7.0, 9.0, 5.0][min(absolute_turn, 3)]
            exact_need = 0
            over_need = 0
            for shape in alternatives or []:
                needs = Counter(int(value) for value in shape)
                exact_need = max(exact_need, int(needs.get(cost, 0) or 0))
                if any(int(target) < cost <= int(target) + 1 for target in shape):
                    over_need = max(over_need, 1)
            if exact_need:
                score += turn_weight * exact_need * scarcity
                if absolute_turn >= 2 and deck_count <= 4:
                    score += 8.0
            elif over_need:
                score += turn_weight * 0.45 * scarcity
        if cost == 2 and deck_count >= 16:
            score *= 0.45
        support_tags = set(card.get("progression_support_tags") or [])
        if int(card.get("energy_activate_n") or 0) > 0:
            score += 8.0 + (5.0 if upcoming_max_cost >= 10 else 0.0)
        accel_value = int(card.get("progression_accel_value") or 0)
        if accel_value >= 2:
            score += 18.0 + min(3, accel_value) * 6.0
            if upcoming_max_cost >= 10:
                score += 8.0
        if "cost_reduction" in support_tags:
            score += 6.0 + (8.0 if upcoming_max_cost >= max(10, cost) else 0.0)
        if "free_member_play" in support_tags:
            score += 10.0 + (6.0 if upcoming_max_cost >= 10 else 0.0)
        if "overcost_member_play" in support_tags:
            score += 10.0 + (6.0 if upcoming_max_cost >= 10 else 0.0)
        if int(card.get("low_cost_summon_n") or 0) > 0:
            score += 8.0
        if int(card.get("live_success_low_cost_summon_n") or 0) > 0:
            score += 14.0 + (8.0 if upcoming_max_cost >= 10 else 0.0)
        if bool(card.get("special_baton")):
            score += 8.0
        return score
    if card.get("kind") == "live":
        score = 0.0
        if int(card.get("draw_n") or 0) > 0:
            score += 2.5
        if int(card.get("energy_boost_n") or 0) > 0:
            if energy_bridge_route:
                score += 28.0
            elif upcoming_max_cost >= 10:
                score += 16.0
            else:
                score += 7.0
            score += min(2, int(card.get("energy_boost_n") or 0)) * 2.0
        support_tags = set(card.get("progression_support_tags") or [])
        accel_value = int(card.get("progression_accel_value") or 0)
        if accel_value >= 2 or "major_acceleration" in support_tags:
            score += 20.0 + min(3, accel_value) * 6.0
            if upcoming_max_cost >= 13:
                score += 10.0
        return score
    return 0.0


def _early_target_costs(target_alternatives_by_turn: list[list[list[int]]], max_turns: int = 3) -> set[int]:
    return {
        int(value)
        for alternatives in target_alternatives_by_turn[:max_turns]
        for shape in alternatives or []
        for value in shape
    }


def _card_need_profile(
    card: dict[str, Any],
    target_alternatives_by_turn: list[list[list[int]]],
    deck_cards: list[dict[str, Any]],
    *,
    start_turn_index: int = 0,
) -> dict[str, float | list[str]]:
    future_play_value = _card_need_score_by_turn(
        card,
        target_alternatives_by_turn,
        deck_cards,
        start_turn_index=start_turn_index,
    )
    keep_value = float(future_play_value)
    exchange_cost = float(future_play_value)
    dig_target_value = 0.0
    recovery_value = 0.0
    sideboard_like = 0.0
    tags: list[str] = []
    early_costs = _early_target_costs(target_alternatives_by_turn)
    if card.get("kind") == "member" and card.get("cost") is not None:
        cost = int(card.get("cost") or 0)
        deck_count = max(1, _member_cost_counts(deck_cards).get(cost, 1))
        exact_offsets = [
            offset
            for offset, alternatives in enumerate(target_alternatives_by_turn[:4])
            if any(cost in [int(value) for value in shape] for shape in alternatives or [])
        ]
        if exact_offsets:
            first_offset = min(exact_offsets)
            dig_target_value = max(0.0, (4 - first_offset) * (8.0 / deck_count))
            tags.append(f"target_t+{first_offset}")
        if cost >= 13 and cost not in early_costs:
            sideboard_like = 1.0
            keep_value *= 0.25
            exchange_cost *= 0.2
            tags.append("sideboard_like")
        if cost == 2 and deck_count >= 12:
            exchange_cost *= 0.75
            tags.append("replaceable_low")
        if int(card.get("low_cost_summon_n") or 0) > 0:
            recovery_value += 8.0
            keep_value += 4.0
            exchange_cost += 4.0
            tags.append("low_cost_summon")
        if int(card.get("live_success_low_cost_summon_n") or 0) > 0:
            recovery_value += 10.0
            keep_value += 12.0
            exchange_cost += 14.0
            tags.append("live_success_low_cost_summon")
        if int(card.get("member_recovery_n") or 0) > 0:
            recovery_value += 7.0
            keep_value += 2.0
            exchange_cost += 2.0
            tags.append("member_recovery")
        if bool(card.get("overcost_member_play")) or "overcost_member_play" in set(card.get("progression_support_tags") or []):
            recovery_value += 4.0
            tags.append("overcost_play")
        accel_value = int(card.get("progression_accel_value") or 0)
        if accel_value >= 2 or "major_acceleration" in set(card.get("progression_support_tags") or []):
            keep_value += 18.0 + min(3, accel_value) * 5.0
            exchange_cost += 20.0 + min(3, accel_value) * 5.0
            recovery_value += 10.0
            tags.append("major_acceleration")
    elif card.get("kind") == "live":
        if int(card.get("energy_boost_n") or 0) > 0:
            dig_target_value += 12.0
            keep_value += 8.0
            exchange_cost += 6.0
            tags.append("energy_boost_live")
        if int(card.get("live_success_member_recovery_n") or card.get("member_recovery_n") or 0) > 0:
            recovery_value += 8.0
            keep_value += 3.0
            exchange_cost += 3.0
            tags.append("member_recovery_live")
        if int(card.get("draw_n") or 0) > 0:
            recovery_value += 3.0
            keep_value += 1.0
            tags.append("draw_live")
        accel_value = int(card.get("progression_accel_value") or 0)
        if accel_value >= 2 or "major_acceleration" in set(card.get("progression_support_tags") or []):
            dig_target_value += 16.0
            keep_value += 18.0 + min(3, accel_value) * 5.0
            exchange_cost += 18.0 + min(3, accel_value) * 5.0
            recovery_value += 8.0
            tags.append("major_acceleration_live")
        if int(card.get("score") or 0) >= 5 and not target_alternatives_by_turn:
            exchange_cost *= 0.8
    total = max(0.0, keep_value + dig_target_value * 0.2 + recovery_value * 0.25 - sideboard_like * 8.0)
    return {
        "total": round(total, 3),
        "keep_value": round(max(0.0, keep_value), 3),
        "exchange_cost": round(max(0.0, exchange_cost), 3),
        "future_play_value": round(max(0.0, future_play_value), 3),
        "dig_target_value": round(max(0.0, dig_target_value), 3),
        "recovery_value": round(max(0.0, recovery_value), 3),
        "sideboard_like": round(sideboard_like, 3),
        "tags": tags,
    }


def _has_energy_bridge_route(target_alternatives_by_turn: list[list[list[int]]]) -> bool:
    for alternatives in target_alternatives_by_turn:
        for shape in alternatives or []:
            if sorted(int(value) for value in shape) == [2, 2, 4]:
                return True
    return False


def _energy_boost_amount(card: dict[str, Any] | None) -> int:
    if not card or card.get("kind") != "live":
        return 0
    return max(0, int(card.get("live_success_energy_boost_n") or card.get("energy_boost_n") or 0))


def _max_available_energy_boost(hand: list[dict[str, Any]] | None) -> int:
    return max((_energy_boost_amount(card) for card in hand or []), default=0)


def _next_turn_active_energy_after_live(energy_state: dict[str, int] | None) -> int | None:
    if energy_state is None:
        return None
    active = max(0, int(energy_state.get("active", 0) or 0))
    wait = max(0, int(energy_state.get("wait", 0) or 0))
    deck_remaining = max(0, int(energy_state.get("deck_remaining", 1) or 0))
    normal_energy = 1 if deck_remaining > 0 else 0
    return active + wait + normal_energy


def _min_active_needed_to_reach_shape_from_costs(
    stage_costs: list[int],
    target_shape: list[int],
    *,
    cost_reduction_costs: set[int] | None = None,
    cost_reduction_amounts: dict[int, int] | None = None,
    reduction_enabled: bool = False,
) -> int:
    available = sorted([max(0, int(cost or 0)) for cost in stage_costs], reverse=True)
    required = 0
    for target in sorted([max(0, int(cost or 0)) for cost in target_shape], reverse=True):
        effective_target = target
        if reduction_enabled and target in (cost_reduction_costs or set()):
            effective_target = max(0, target - max(1, int((cost_reduction_amounts or {}).get(target, 2))))
        if not available:
            required += effective_target
            continue
        affordable_matches = [(index, cost) for index, cost in enumerate(available) if cost <= target]
        if affordable_matches:
            index, cost = max(affordable_matches, key=lambda item: item[1])
        else:
            index, cost = min(enumerate(available), key=lambda item: item[1])
        required += max(0, effective_target - cost)
        available.pop(index)
    return required


def _energy_bridge_plan_for_next_turn(
    stage: list[dict[str, Any] | None] | None,
    future_alternatives_by_turn: list[list[list[int]]] | None,
    energy_state: dict[str, int] | None,
    hand: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    next_alternatives = (future_alternatives_by_turn or [])[1] if len(future_alternatives_by_turn or []) > 1 else []
    boost_n = _max_available_energy_boost(hand)
    base_active = _next_turn_active_energy_after_live(energy_state)
    if not next_alternatives or base_active is None or boost_n <= 0:
        return {
            "needed": False,
            "reason": "no next target or boost card",
            "base_active_next": base_active,
            "boosted_active_next": None if base_active is None else base_active + boost_n,
            "boost_n": boost_n,
            "min_required": None,
            "next_target": "",
        }
    stage_costs = _stage_costs(stage or [])
    reduction_enabled = _cost_reduction_available_for_stage(stage)
    cost_reduction_costs = {
        int(card.get("cost") or 0)
        for card in (hand or [])
        if card.get("kind") == "member"
        and card.get("cost") is not None
        and bool(card.get("cost_reduction"))
    }
    cost_reduction_amounts = {
        int(card.get("cost") or 0): max(1, int(card.get("cost_reduction_n") or 2))
        for card in (hand or [])
        if card.get("kind") == "member"
        and card.get("cost") is not None
        and bool(card.get("cost_reduction"))
    }
    required_options = [
        (
            _min_active_needed_to_reach_shape_from_costs(
                stage_costs,
                list(shape),
                cost_reduction_costs=cost_reduction_costs,
                cost_reduction_amounts=cost_reduction_amounts,
                reduction_enabled=reduction_enabled,
            ),
            _shape_trace_label(list(shape)),
        )
        for shape in next_alternatives or []
    ]
    if not required_options:
        return {
            "needed": False,
            "reason": "no next target",
            "base_active_next": base_active,
            "boosted_active_next": base_active + boost_n,
            "boost_n": boost_n,
            "min_required": None,
            "next_target": "",
        }
    min_required, target_label = min(required_options, key=lambda item: item[0])
    boosted_active = base_active + boost_n
    needed = base_active < min_required <= boosted_active
    return {
        "needed": needed,
        "reason": "boost bridges next target" if needed else "base energy already enough or boost still short",
        "base_active_next": base_active,
        "boosted_active_next": boosted_active,
        "boost_n": boost_n,
        "min_required": min_required,
        "next_target": target_label,
    }


def _upcoming_max_target_cost(target_alternatives_by_turn: list[list[list[int]]]) -> int:
    best = 0
    for alternatives in target_alternatives_by_turn:
        for shape in alternatives or []:
            for value in shape:
                best = max(best, int(value))
    return best


def _member_cost_counts_from_cards(cards: list[dict[str, Any]]) -> Counter[int]:
    return Counter(
        int(card.get("cost") or 0)
        for card in cards
        if card.get("kind") == "member" and card.get("cost") is not None
    )


def _member_cost_list_from_counts(counts: Counter[int]) -> list[int]:
    out: list[int] = []
    for cost, count in counts.items():
        out.extend([int(cost)] * max(0, int(count)))
    return out


def _mulligan_draw_windows(keep_count: int, max_turns: int) -> list[int]:
    redraw = max(0, 6 - int(keep_count))
    # Conservative access window before each MAIN decision:
    # redraw to six, normal draw, and a limited allowance for prior live-set digging.
    # Full three-card exchange was too optimistic and made T1/T2 keeps unstable.
    windows = []
    for turn_index in range(max_turns):
        windows.append(redraw + 1 + turn_index * 2)
    return windows


def _relevant_target_costs(target_alternatives_by_turn: list[list[list[int]]]) -> list[int]:
    costs = sorted({
        int(value)
        for alternatives in target_alternatives_by_turn
        for shape in alternatives or []
        for value in shape
    })
    return costs


def _has_target_shape(target_alternatives_by_turn: list[list[list[int]]], shape: list[int]) -> bool:
    wanted = sorted(int(value) for value in shape)
    for alternatives in target_alternatives_by_turn:
        for alternative in alternatives or []:
            if sorted(int(value) for value in alternative) == wanted:
                return True
    return False


def _heart_counts(raw: Any) -> Counter[str]:
    counts: Counter[str] = Counter()
    for color, value in re.findall(r"<([^>]+)>\s*(\d+)", str(raw or "")):
        try:
            counts[str(color)] += int(value)
        except ValueError:
            continue
    return counts


def _colored_heart_match_score(member_card: dict[str, Any], live_card: dict[str, Any]) -> float:
    base = _heart_counts(member_card.get("base_hearts_raw"))
    required = _heart_counts(live_card.get("required_hearts_raw"))
    score = 0.0
    for color, need in required.items():
        if color in {"任意", "ALL", "all"}:
            continue
        score += min(int(base.get(color, 0) or 0), int(need or 0))
    return score


def _stage_heart_counts_for_live_estimate(stage: list[dict[str, Any] | None] | None) -> Counter[str]:
    counts: Counter[str] = Counter()
    for card in stage or []:
        if not card or card.get("kind") != "member":
            continue
        counts.update(_heart_counts(card.get("base_hearts_raw")))
    return counts


def _live_basic_success_candidate(stage: list[dict[str, Any] | None] | None, live_card: dict[str, Any] | None) -> bool:
    if not live_card or live_card.get("kind") != "live":
        return False
    stage_members = [card for card in stage or [] if card and card.get("kind") == "member"]
    if not stage_members:
        return False
    stage_costs = _stage_costs(stage or [])
    member_count = len(stage_members)
    # This is a coarse live-set heuristic, not a full cheer probability model.
    # High-value setup lives should stay selectable once the stage can plausibly
    # support them; strict base-heart checks were discarding real DM/LU lines.
    if int(live_card.get("energy_boost_n") or 0) > 0:
        return member_count >= 2 or sum(stage_costs) >= 4
    if int(live_card.get("draw_n") or 0) > 0 and int(live_card.get("score") or 0) == 0:
        return True
    score = int(live_card.get("score") or 0)
    if score >= 5:
        return member_count >= 3 or sum(stage_costs) >= 7
    if score >= 3:
        return member_count >= 2 or sum(stage_costs) >= 4
    required = _heart_counts(live_card.get("required_hearts_raw"))
    if not required:
        return True
    available = _stage_heart_counts_for_live_estimate(stage)
    colorless_required = 0
    for color, need in required.items():
        if color in {"任意", "ALL", "all"}:
            colorless_required += int(need or 0)
            continue
        if int(available.get(color, 0) or 0) < int(need or 0):
            return False
    if colorless_required:
        total_available = sum(int(value or 0) for value in available.values())
        colored_required = sum(int(need or 0) for color, need in required.items() if color not in {"任意", "ALL", "all"})
        return total_available - colored_required >= colorless_required
    return True


def _live_effect_play_value(
    live_card: dict[str, Any] | None,
    future_alternatives_by_turn: list[list[list[int]]],
    *,
    start_turn_index: int = 0,
    prefer_energy_boost: bool = False,
) -> float:
    if not live_card or live_card.get("kind") != "live":
        return 0.0
    score = 0.0
    upcoming_max = _upcoming_max_target_cost(future_alternatives_by_turn[:3])
    energy_bridge = _has_energy_bridge_route(future_alternatives_by_turn[:2])
    draw_n = int(live_card.get("live_success_draw_n") or live_card.get("draw_n") or 0)
    energy_n = int(live_card.get("live_success_energy_boost_n") or live_card.get("energy_boost_n") or 0)
    if energy_n > 0:
        score += 36.0 if (prefer_energy_boost or energy_bridge) else 14.0
        if upcoming_max >= 10:
            score += 10.0
        score += min(2, energy_n) * 3.0
    accel_value = int(live_card.get("progression_accel_value") or 0)
    support_tags = set(live_card.get("progression_support_tags") or [])
    if accel_value >= 2 or "major_acceleration" in support_tags:
        score += 30.0 + min(3, accel_value) * 8.0
        if upcoming_max >= 13:
            score += 12.0
    if draw_n > 0:
        # Draw effects are strongest before the next bottleneck turn, because
        # they convert a live success into extra looks at the target card.
        score += min(3, draw_n) * (5.0 if start_turn_index <= 1 else 3.0)
        if upcoming_max >= 10:
            score += 3.0
    live_score = int(live_card.get("score") or 0)
    if live_score >= 5:
        score += 2.0
    if live_score == 0 and draw_n >= 2:
        score += 8.0
    return score


def _card_effect_play_value(card: dict[str, Any] | None) -> float:
    if not card:
        return 0.0
    value = 0.0
    draw_n = max(
        int(card.get("draw_n") or 0),
        int(card.get("enter_draw_n") or 0),
        int(card.get("live_success_draw_n") or 0),
        int(card.get("activated_draw_n") or 0),
    )
    energy_n = max(
        int(card.get("energy_boost_n") or 0),
        int(card.get("enter_energy_boost_n") or 0),
        int(card.get("live_success_energy_boost_n") or 0),
    )
    if draw_n > 0:
        value += min(3, draw_n) * 2.0
    if energy_n > 0:
        value += min(3, energy_n) * 8.0
    if int(card.get("energy_activate_n") or 0) > 0:
        value += min(3, int(card.get("energy_activate_n") or 0)) * 7.0
    if int(card.get("low_cost_summon_n") or 0) > 0:
        value += 10.0
    if int(card.get("live_success_low_cost_summon_n") or 0) > 0:
        value += 16.0
    if bool(card.get("cost_reduction")):
        value += max(8.0, float(int(card.get("cost_reduction_n") or 2) * 5))
    if bool(card.get("free_member_play")) or bool(card.get("overcost_member_play")):
        value += 14.0
    accel_value = int(card.get("progression_accel_value") or 0)
    if accel_value >= 2 or "major_acceleration" in set(card.get("progression_support_tags") or []):
        value += 18.0 + min(3, accel_value) * 6.0
    return value


def _discard_after_effect_draw(
    hand: list[dict[str, Any]],
    deck_cards: list[dict[str, Any]],
    future_alternatives_by_turn: list[list[list[int]]] | None,
    *,
    start_turn_index: int = 0,
) -> dict[str, Any] | None:
    if not hand:
        return None
    alternatives = future_alternatives_by_turn or []

    def discard_rank(card: dict[str, Any]) -> tuple[float, float, int, str]:
        profile = _card_need_profile(
            card,
            alternatives,
            deck_cards,
            start_turn_index=start_turn_index,
        )
        keep_value = float(profile.get("keep_value") or 0.0)
        future_value = float(profile.get("future_play_value") or 0.0)
        effect_value = _card_effect_play_value(card)
        sideboard = float(profile.get("sideboard_like") or 0.0)
        return (
            keep_value + future_value * 0.35 + effect_value * 0.6 - sideboard * 10.0,
            effect_value,
            int(card.get("value") or 0),
            str(card.get("card_no") or ""),
        )

    discard = min(hand, key=discard_rank)
    hand.remove(discard)
    return discard


def _card_matches_top_search(card: dict[str, Any], profile: dict[str, Any]) -> bool:
    if not profile:
        return False
    if profile.get("member_only") and card.get("kind") != "member":
        return False
    if profile.get("no_blade_heart") and _search_condition_blade_heart_total(card) > 0:
        return False
    group = str(profile.get("group") or "")
    if group and group not in str(card.get("group") or ""):
        return False
    return True


def _search_condition_blade_heart_total(card: dict[str, Any]) -> int:
    """Return the DB-normalized blade-heart presence for card text filters."""
    return int(card.get("blade_heart_total") or 0)


def _topdeck_effect_card_value(
    card: dict[str, Any],
    deck_cards: list[dict[str, Any]],
    future_alternatives_by_turn: list[list[list[int]]] | None,
    *,
    start_turn_index: int = 0,
    stage: list[dict[str, Any] | None] | None = None,
) -> float:
    profile = _card_need_profile(
        card,
        future_alternatives_by_turn or [],
        deck_cards,
        start_turn_index=start_turn_index,
    )
    value = (
        float(profile.get("keep_value") or 0.0)
        + float(profile.get("future_play_value") or 0.0) * 0.45
        + float(profile.get("dig_target_value") or 0.0) * 0.25
        + _card_effect_play_value(card) * 0.7
        + int(card.get("score") or 0) * 0.15
    )
    if card.get("kind") == "member" and card.get("cost") is not None:
        cost = int(card.get("cost") or 0)
        if stage is not None and future_alternatives_by_turn:
            stage_costs = _stage_costs_with_virtual_low_summons(stage)
            current_alternatives = future_alternatives_by_turn[0] or []
            max_slots = max((len(shape) for shape in current_alternatives), default=0)
            slot_preserving_alternatives = [
                list(shape) for shape in current_alternatives
                if len(shape) == max_slots
            ] or current_alternatives
            best_current_shape = _best_target_shape_for_stage(stage, slot_preserving_alternatives)
            current_missing = {int(value) for value in _missing_for_shape(stage_costs, list(best_current_shape))}
            if cost in current_missing:
                value += 86.0
            if cost >= 13 and any(3 <= missing <= 11 for missing in current_missing):
                value -= 54.0
            current_target_costs = {
                int(value)
                for shape in current_alternatives
                for value in shape
            }
            if (
                3 <= cost <= 11
                and cost in current_target_costs
                and cost not in stage_costs
                and int(card.get("energy_activate_n") or 0) > 0
            ):
                value += 124.0
        for offset, alternatives in enumerate((future_alternatives_by_turn or [])[:3]):
            if any(cost in [int(value) for value in shape] for shape in alternatives or []):
                value += {0: 64.0, 1: 28.0, 2: 10.0}.get(offset, 0.0)
                if cost >= 13 and offset <= 1:
                    value += 4.0
                break
        if cost in {9, 17} and int(card.get("energy_activate_n") or 0) > 0:
            value += 6.0
        if cost >= 15 and bool(card.get("cost_reduction")):
            value += 5.0
    return value


def _playable_recovered_target_now(
    target: dict[str, Any],
    trial_stage: list[dict[str, Any] | None],
    trial_hand: list[dict[str, Any]],
) -> bool:
    if target.get("kind") == "member":
        return target not in trial_hand and any(card is target for card in trial_stage if card)
    if target.get("kind") == "live":
        return target in trial_hand and _live_basic_success_candidate(trial_stage, target)
    return False


def _apply_enter_topdeck_effects(
    played_cards: list[dict[str, Any]],
    stage: list[dict[str, Any] | None],
    hand: list[dict[str, Any]],
    deck: list[dict[str, Any]],
    draw_index: int,
    green: list[dict[str, Any]],
    deck_cards: list[dict[str, Any]],
    future_alternatives_by_turn: list[list[list[int]]] | None,
    *,
    start_turn_index: int = 0,
) -> tuple[int, list[dict[str, Any]]]:
    logs: list[dict[str, Any]] = []
    for source in played_cards:
        if source.get("kind") != "member":
            continue
        stack_n = int(source.get("enter_top_stack_n") or 0)
        if stack_n > 0 and draw_index < len(deck):
            visible = list(deck[draw_index: min(len(deck), draw_index + stack_n)])
            if visible:
                ranked = sorted(
                    visible,
                    key=lambda card: _topdeck_effect_card_value(
                        card,
                        deck_cards,
                        future_alternatives_by_turn,
                        start_turn_index=start_turn_index,
                        stage=stage,
                    ),
                    reverse=True,
                )
                keep = [
                    card for card in ranked
                    if _topdeck_effect_card_value(
                        card,
                        deck_cards,
                        future_alternatives_by_turn,
                        start_turn_index=start_turn_index,
                        stage=stage,
                    ) > 0
                ][:stack_n]
                if not keep and ranked:
                    keep = [ranked[0]]
                bottom_out = [card for card in visible if card not in keep]
                deck[draw_index: draw_index + len(visible)] = keep
                green.extend(bottom_out)
                logs.append({
                    "source": _card_trace_label(source),
                    "kind": "top_stack",
                    "looked": [_card_trace_label(card) for card in visible],
                    "kept_on_top": [_card_trace_label(card) for card in keep],
                    "moved_to_green": [_card_trace_label(card) for card in bottom_out],
                })
        search = source.get("enter_top_search")
        if isinstance(search, dict) and int(search.get("look_n") or 0) > 0 and draw_index < len(deck):
            look_n = int(search.get("look_n") or 0)
            visible = list(deck[draw_index: min(len(deck), draw_index + look_n)])
            candidates = [card for card in visible if _card_matches_top_search(card, search)]
            chosen = None
            discarded = None
            if candidates:
                chosen = max(
                    candidates,
                    key=lambda card: _topdeck_effect_card_value(
                        card,
                        deck_cards,
                        future_alternatives_by_turn,
                        start_turn_index=start_turn_index,
                        stage=stage,
                    ),
                )
                if int(search.get("discard_hand_cost_n") or 0) > 0:
                    discarded = _discard_after_effect_draw(
                        hand,
                        deck_cards,
                        future_alternatives_by_turn,
                        start_turn_index=start_turn_index,
                    )
                    if discarded is None:
                        chosen = None
            if chosen is None:
                logs.append({
                    "source": _card_trace_label(source),
                    "kind": "top_search",
                    "looked": [_card_trace_label(card) for card in visible],
                    "selected": "none",
                    "discarded_cost": _card_trace_label(discarded),
                    "moved_to_green": [],
                })
                continue
            deck[draw_index: draw_index + len(visible)] = []
            hand.append(chosen)
            moved = [card for card in visible if card is not chosen]
            green.extend(moved)
            logs.append({
                "source": _card_trace_label(source),
                "kind": "top_search",
                "looked": [_card_trace_label(card) for card in visible],
                "selected": _card_trace_label(chosen),
                "discarded_cost": _card_trace_label(discarded),
                "moved_to_green": [_card_trace_label(card) for card in moved],
            })
    return draw_index, logs


def _card_matches_recovery_kind(card: dict[str, Any], recovery_kind: str) -> bool:
    if recovery_kind == "card":
        return True
    if recovery_kind == "member":
        return card.get("kind") == "member"
    if recovery_kind == "live":
        return card.get("kind") == "live"
    return False


def _apply_stage_recovery_support(
    stage: list[dict[str, Any] | None],
    hand: list[dict[str, Any]],
    green: list[dict[str, Any]],
    deck_cards: list[dict[str, Any]],
    alternatives: list[list[int]],
    energy_state: dict[str, int],
    future_alternatives_by_turn: list[list[list[int]]] | None,
    *,
    planning_alternatives: list[list[int]] | None = None,
    start_turn_index: int = 0,
) -> dict[str, Any]:
    if not green or not alternatives:
        return {"used": False}
    best_shape = _best_target_shape_for_stage(stage, planning_alternatives or alternatives)
    current_costs = _stage_costs_with_virtual_low_summons(stage)
    current_meets = any(_shape_meets_target(current_costs, sorted(alternative, reverse=True)) for alternative in alternatives)
    current_score = _stage_score(stage, best_shape)
    current_total = sum(_stage_costs(stage))
    best: tuple[Any, ...] | None = None
    for slot, source in enumerate(stage):
        if not source or source.get("kind") != "member":
            continue
        if not bool(source.get("activated_self_to_green_cost")):
            continue
        recovery_kind = str(source.get("activated_recovery_kind") or source.get("recovery_kind") or "")
        if not recovery_kind:
            continue
        stage_without = list(stage)
        stage_without[slot] = None
        without_costs = _stage_costs_with_virtual_low_summons(stage_without)
        surplus_ok = current_meets and any(
            _shape_meets_target(without_costs, sorted(alternative, reverse=True))
            for alternative in alternatives
        )
        for target_index, target in enumerate(list(green)):
            if target is source or not _card_matches_recovery_kind(target, recovery_kind):
                continue
            trial_stage = list(stage_without)
            trial_hand = list(hand) + [target]
            trial_green = [card for index, card in enumerate(green) if index != target_index]
            trial_green.append(source)
            trial_energy = dict(energy_state)
            _improve_persistent_stage(
                trial_stage,
                trial_hand,
                alternatives,
                trial_energy,
                planning_alternatives=planning_alternatives,
            )
            trial_costs = _stage_costs_with_virtual_low_summons(trial_stage)
            trial_meets = any(_shape_meets_target(trial_costs, sorted(alternative, reverse=True)) for alternative in alternatives)
            trial_score = _stage_score(trial_stage, best_shape)
            trial_total = sum(_stage_costs(trial_stage))
            playable_now = _playable_recovered_target_now(target, trial_stage, trial_hand)
            if not playable_now:
                continue
            future_value = _topdeck_effect_card_value(
                target,
                deck_cards,
                future_alternatives_by_turn,
                start_turn_index=start_turn_index,
            )
            score_gain = trial_score - current_score
            total_gain = trial_total - current_total
            reason = ""
            if surplus_ok and target.get("kind") == "live" and future_value > 0:
                reason = "surplus target met; recover live playable this turn"
            elif trial_meets and (not current_meets or score_gain >= 0):
                reason = "recover and play target this turn while keeping progression"
            elif not current_meets and (score_gain > 0 or total_gain > 0):
                reason = "current progression miss; recovery plays target this turn"
            if not reason:
                continue
            rank = (
                2 if surplus_ok else 1,
                1 if trial_meets else 0,
                score_gain,
                total_gain,
                future_value,
                int(target.get("cost") or target.get("score") or 0),
                str(target.get("card_no") or ""),
                slot,
                target_index,
                reason,
                trial_stage,
                trial_hand,
                trial_green,
                trial_energy,
                source,
                target,
            )
            if best is None or rank[:7] > best[:7]:
                best = rank
    if best is None:
        return {"used": False}
    stage[:] = best[10]
    hand[:] = best[11]
    green[:] = best[12]
    energy_state.clear()
    energy_state.update(best[13])
    return {
        "used": True,
        "reason": best[9],
        "source": _card_trace_label(best[14]),
        "recovered": _card_trace_label(best[15]),
        "after_stage": _stage_text(stage),
        "energy_after": dict(energy_state),
    }


def _mulligan_profile_adjustment(
    kept_cards: list[dict[str, Any]],
    initial_hand: list[dict[str, Any]],
    target_alternatives_by_turn: list[list[list[int]]],
) -> float:
    """Human-guided early mulligan heuristics derived from progression shape.

    These are deliberately expressed by card kind/cost/effect/heart profile so
    the examples teach a reusable tendency instead of adding card-number rules.
    """
    if not initial_hand:
        return 0.0
    kept = list(kept_cards)
    redraws = 6 - len(kept)
    members = [card for card in kept if card.get("kind") == "member"]
    lives = [card for card in kept if card.get("kind") == "live"]
    initial_members = [card for card in initial_hand if card.get("kind") == "member"]
    initial_lives = [card for card in initial_hand if card.get("kind") == "live"]

    def member_cost(card: dict[str, Any]) -> int:
        return int(card.get("cost") or 0)

    def live_score(card: dict[str, Any]) -> int:
        return int(card.get("score") or 0)

    def energy_live(card: dict[str, Any]) -> bool:
        return card.get("kind") == "live" and int(card.get("energy_boost_n") or 0) > 0

    def no_ability(card: dict[str, Any]) -> bool:
        text = str(card.get("effect_text") or "").strip()
        return text in {"", "(なし)", "なし"}

    def member_recovery(card: dict[str, Any]) -> bool:
        text = str(card.get("effect_text") or "")
        return "控え室からメンバーカード" in text and "手札に加える" in text

    def two_quality(card: dict[str, Any], preferred_live: dict[str, Any] | None = None) -> float:
        value = 0.0
        if member_cost(card) != 2:
            return value
        if preferred_live:
            value += _colored_heart_match_score(card, preferred_live) * 4.0
        hearts = _heart_counts(card.get("base_hearts_raw"))
        if hearts.get("紫", 0):
            value += 2.0
        if hearts.get("青", 0):
            value += 1.5
        if hearts.get("赤", 0):
            value += 1.0
        if no_ability(card):
            value += 2.0
        if member_recovery(card):
            value += 1.0
        return value

    def cost_count(cost: int) -> int:
        return sum(1 for card in members if member_cost(card) == cost)

    def initial_has_cost(cost: int) -> bool:
        return any(member_cost(card) == cost for card in initial_members)

    def first_kept_cost(cost: int) -> bool:
        return any(member_cost(card) == cost for card in members)

    score = 0.0
    five_axis = _has_target_shape(target_alternatives_by_turn, [2, 5, 2])
    ten_axis = _has_target_shape(target_alternatives_by_turn, [2, 10, 2])
    kimi_axis = _has_target_shape(target_alternatives_by_turn, [7, 2])
    early_target_costs = {
        int(value)
        for alternatives in target_alternatives_by_turn[:3]
        for shape in alternatives or []
        for value in shape
    }
    for card in members:
        cost = member_cost(card)
        if cost >= 13 and cost not in early_target_costs:
            score -= 22.0

    if five_axis:
        initial_energy_lives = [card for card in initial_lives if energy_live(card)]
        initial_cost4_count = sum(1 for card in initial_members if member_cost(card) == 4)
        initial_two_count = sum(1 for card in initial_members if member_cost(card) == 2)
        if not initial_has_cost(5) and not initial_energy_lives:
            # 5軸で5/DM系が無い初手は、4や11を守るより掘り直す。
            score += redraws * 5.0 - len(kept) * 8.0
        score += min(cost_count(5), 1) * 16.0
        score -= max(0, cost_count(5) - 1) * 4.0
        kept_energy_lives = [card for card in lives if energy_live(card)]
        score += min(len(kept_energy_lives), 1) * 12.0
        score -= max(0, len(kept_energy_lives) - 1) * 5.0
        score += min(cost_count(2), 1) * 8.0
        if first_kept_cost(5) and not kept_energy_lives:
            score += min(max(0, cost_count(2) - 1), 1) * 7.0
            score -= max(0, cost_count(2) - 2) * 3.0
        elif kept_energy_lives and not first_kept_cost(4) and not first_kept_cost(5):
            score -= max(0, cost_count(2) - 1) * 6.0
        elif kept_energy_lives and first_kept_cost(4) and not first_kept_cost(5):
            score += min(max(0, cost_count(2) - 1), 1) * 6.0
            score -= max(0, cost_count(2) - 2) * 3.0
        else:
            score -= max(0, cost_count(2) - 1) * 1.5
        # 4はDM/5の代替進行を支える札で、単独キープ理由にはしない。
        if not first_kept_cost(5) and not kept_energy_lives:
            score -= cost_count(4) * 7.0
        else:
            score -= max(0, cost_count(4) - 1) * 4.0
        if kept_energy_lives and not first_kept_cost(5):
            score += min(cost_count(4), 1) * (14.0 if initial_cost4_count > 0 else 0.0)
        if first_kept_cost(5) and kept_energy_lives and cost_count(2) >= 1:
            # 主ルートの5+DM+2が見えている場合、4は代替ルート用なので返して掘る。
            score -= cost_count(4) * 6.0
        if first_kept_cost(5) and kept_energy_lives and cost_count(2) == 0 and initial_two_count == 0:
            # 2欠損時は5単独進行が崩れやすいので、4コストの逃げ道を残す。
            score += min(cost_count(4), 1) * 13.0
        if first_kept_cost(5) and kept_energy_lives and initial_two_count > 0 and cost_count(2) == 0:
            score -= cost_count(4) * 8.0
        score -= sum(1 for card in members if member_cost(card) >= 11) * 12.0
        if cost_count(2):
            best_two = max((two_quality(card) for card in members if member_cost(card) == 2), default=0.0)
            score += best_two * 0.8

    if ten_axis:
        initial_has_ten = initial_has_cost(10)
        initial_energy_lives = [card for card in initial_lives if energy_live(card)]
        initial_cost4_count = sum(1 for card in initial_members if member_cost(card) == 4)
        score += min(cost_count(10), 1) * 19.0
        score -= max(0, cost_count(10) - 1) * 5.0
        kept_energy_lives = [card for card in lives if energy_live(card)]
        if initial_has_ten:
            score += min(cost_count(4), 1) * 8.0
            if first_kept_cost(4):
                score += min(cost_count(2), 2) * 6.0
                score -= max(0, cost_count(2) - 2) * 2.0
            else:
                score += min(cost_count(2), 1) * 7.0
                score -= max(0, cost_count(2) - 1) * 5.0
            if first_kept_cost(4):
                score += min(len(kept_energy_lives), 1) * 9.0
            else:
                score -= len(kept_energy_lives) * 6.0
        else:
            if initial_energy_lives or initial_cost4_count >= 2:
                score += min(cost_count(4), 1) * 11.0
            else:
                score -= cost_count(4) * 8.0
            score -= cost_count(2) * 3.5
            score += min(len(kept_energy_lives), 1) * (12.0 if first_kept_cost(4) else 4.0)
            if kept_energy_lives and first_kept_cost(4):
                # DM系+4から入る10軸は、T2の2面補完を見て低コストを2枚まで残す。
                score += min(cost_count(2), 2) * 7.0
                score -= max(0, cost_count(2) - 2) * 3.0
            if not initial_energy_lives:
                score -= cost_count(2) * 7.0
                if initial_cost4_count < 2:
                    score += redraws * 4.5 - len(kept) * 7.0
        # 紫を多く持つ4コストはDM系ライブの成功に寄与しやすい。
        if cost_count(4):
            best_purple = max(
                (_heart_counts(card.get("base_hearts_raw")).get("紫", 0) for card in members if member_cost(card) == 4),
                default=0,
            )
            score += float(best_purple) * 2.0
        if cost_count(2) and (initial_has_ten or initial_energy_lives):
            best_two = max((two_quality(card) for card in members if member_cost(card) == 2), default=0.0)
            score += best_two * 0.9
        score -= max(0, cost_count(4) - 1) * 6.0
        for card in members:
            cost = member_cost(card)
            if cost >= 13:
                score -= 18.0 if initial_has_ten else 10.0

    if kimi_axis:
        if not initial_has_cost(7):
            # 7が無い君ここ型は、13/2や高スコアライブを握らず探し直す。
            score += redraws * 5.0 - len(kept) * 9.0
        score += min(cost_count(7), 1) * 17.0
        score -= max(0, cost_count(7) - 1) * 7.0
        setup_lives = [card for card in lives if live_score(card) == 0 and int(card.get("draw_n") or 0) >= 2]
        initial_two_count = sum(1 for card in initial_members if member_cost(card) == 2)
        setup_value = 14.0
        if initial_has_cost(7) and initial_two_count == 0:
            setup_value = -7.0
        elif not initial_has_cost(7):
            setup_value = 3.0
        score += min(len(setup_lives), 1) * setup_value
        score -= max(0, len(setup_lives) - 1) * 4.0
        preferred_live = setup_lives[0] if setup_lives else next(
            (card for card in initial_lives if live_score(card) == 0 and int(card.get("draw_n") or 0) >= 2),
            None,
        )
        kept_twos = [card for card in members if member_cost(card) == 2]
        if kept_twos:
            score += min(len(kept_twos), 2) * 5.0
            if preferred_live:
                score += max((_colored_heart_match_score(card, preferred_live) for card in kept_twos), default=0.0) * 5.0
            if initial_has_cost(7) and setup_lives and initial_two_count >= 3:
                score += min(max(0, len(kept_twos) - 1), 1) * 7.0
            else:
                score -= max(0, len(kept_twos) - 1) * 7.0
            score -= max(0, len(kept_twos) - 2) * 5.0
            best_two = max((two_quality(card, preferred_live) for card in kept_twos), default=0.0)
            score += best_two * 0.6
        for card in members:
            cost = member_cost(card)
            if cost >= 13:
                score -= 16.0
        score -= sum(1 for card in lives if live_score(card) >= 5) * 8.0

    return score


def _draw_cost_distribution(
    pool_counts: Counter[int],
    total_pool_cards: int,
    draws: int,
    relevant_costs: list[int],
) -> list[tuple[Counter[int], float]]:
    total_pool_cards = max(0, int(total_pool_cards))
    draws = max(0, min(int(draws), total_pool_cards))
    if draws == 0:
        return [(Counter(), 1.0)]
    denominator = comb(total_pool_cards, draws)
    if denominator <= 0:
        return [(Counter(), 1.0)]
    categories = [(cost, max(0, int(pool_counts.get(cost, 0) or 0))) for cost in relevant_costs]
    other_count = max(0, total_pool_cards - sum(count for _cost, count in categories))
    out: list[tuple[Counter[int], float]] = []

    def walk(index: int, remaining_draws: int, ways: int, picked: Counter[int]) -> None:
        if index >= len(categories):
            if remaining_draws <= other_count:
                final_ways = ways * comb(other_count, remaining_draws)
                out.append((Counter(picked), final_ways / denominator))
            return
        cost, available = categories[index]
        max_pick = min(available, remaining_draws)
        for picked_n in range(max_pick + 1):
            if picked_n:
                picked[cost] += picked_n
            walk(index + 1, remaining_draws - picked_n, ways * comb(available, picked_n), picked)
            if picked_n:
                picked[cost] -= picked_n
                if picked[cost] <= 0:
                    del picked[cost]

    walk(0, draws, 1, Counter())
    return out


def _access_probability_for_alternatives(
    kept_cards: list[dict[str, Any]],
    unavailable_cards: list[dict[str, Any]],
    deck_cards: list[dict[str, Any]],
    alternatives: list[list[int]],
    draws: int,
    *,
    early_plan_slots: bool = False,
) -> float:
    if not alternatives:
        return 0.0
    kept_counts = _member_cost_counts_from_cards(kept_cards)
    total_pool_cards = max(0, len(deck_cards) - len(unavailable_cards))
    pool_counts = _member_cost_counts_from_cards(deck_cards)
    for cost, count in _member_cost_counts_from_cards(unavailable_cards).items():
        pool_counts[cost] = max(0, pool_counts.get(cost, 0) - count)
    relevant_costs = _relevant_target_costs([alternatives])
    probability = 0.0
    for drawn_counts, chance in _draw_cost_distribution(pool_counts, total_pool_cards, draws, relevant_costs):
        combined = Counter(kept_counts)
        combined.update(drawn_counts)
        costs = _member_cost_list_from_counts(combined)
        matcher = _shape_meets_early_plan_slots if early_plan_slots else _shape_meets_target
        if any(matcher(costs, list(shape)) for shape in alternatives):
            probability += chance
    return min(1.0, max(0.0, probability))


def _mulligan_duplicate_penalty(kept_cards: list[dict[str, Any]], target_alternatives_by_turn: list[list[list[int]]]) -> float:
    kept_counts = _member_cost_counts_from_cards(kept_cards)
    max_needed: Counter[int] = Counter()
    for alternatives in target_alternatives_by_turn[:3]:
        for shape in alternatives or []:
            for cost, count in Counter(int(value) for value in shape).items():
                max_needed[cost] = max(max_needed[cost], count)
    penalty = 0.0
    for cost, count in kept_counts.items():
        extra = max(0, int(count) - max(1, int(max_needed.get(cost, 0) or 0)))
        if extra:
            penalty += extra * (0.75 if cost >= 5 else 0.35)
    return penalty


def _target_focus_costs(alternatives: list[list[int]], deck_cards: list[dict[str, Any]]) -> set[int]:
    deck_cost_counts = _member_cost_counts(deck_cards)
    focus_costs: set[int] = set()
    for shape in alternatives or []:
        values = [int(value) for value in shape]
        non_low = [value for value in values if value > 2]
        for value in non_low:
            if int(deck_cost_counts.get(value, 0) or 0) <= 4:
                focus_costs.add(value)
        if not non_low and values:
            focus_costs.add(max(values))
    return focus_costs


def _mulligan_bottleneck_focus(
    initial_hand: list[dict[str, Any]],
    deck_cards: list[dict[str, Any]],
    target_alternatives_by_turn: list[list[list[int]]],
) -> dict[str, Any]:
    if not target_alternatives_by_turn:
        return {}
    no_keep_windows = _mulligan_draw_windows(0, min(3, len(target_alternatives_by_turn)))
    turn_candidates: list[dict[str, Any]] = []
    for turn_index, alternatives in enumerate(target_alternatives_by_turn[:3]):
        if not alternatives:
            continue
        draws = no_keep_windows[turn_index] if turn_index < len(no_keep_windows) else no_keep_windows[-1]
        access_probability = _access_probability_for_alternatives([], initial_hand, deck_cards, alternatives, draws)
        focus_costs = _target_focus_costs(alternatives, deck_cards)
        has_four_bridge = any(sorted(int(value) for value in shape) == [2, 2, 4] for shape in alternatives)
        if not focus_costs and not has_four_bridge:
            continue
        def is_candidate_key(card: dict[str, Any]) -> bool:
            if card.get("kind") == "member" and card.get("cost") is not None and int(card.get("cost") or 0) in focus_costs:
                return True
            if card.get("kind") == "live" and int(card.get("energy_boost_n") or 0) > 0 and has_four_bridge:
                return True
            return False
        key_total = sum(1 for card in deck_cards if is_candidate_key(card))
        if key_total <= 0 or any(is_candidate_key(card) for card in initial_hand):
            continue
        severity = (1.0 - access_probability) * (1.0 + max(0, 2 - turn_index) * 0.25)
        turn_candidates.append({
            "turn_index": turn_index,
            "alternatives": alternatives,
            "access_probability": access_probability,
            "focus_costs": focus_costs,
            "has_four_bridge": has_four_bridge,
            "key_total": key_total,
            "severity": severity,
        })
    if not turn_candidates:
        return {}
    focus_turn_info = max(turn_candidates, key=lambda item: (float(item.get("severity") or 0.0), -int(item.get("turn_index") or 0)))
    focus_turn = int(focus_turn_info.get("turn_index") or 0)
    focus_costs = set(focus_turn_info.get("focus_costs") or set())
    has_four_bridge = bool(focus_turn_info.get("has_four_bridge"))

    def is_key(card: dict[str, Any]) -> bool:
        if card.get("kind") == "member" and card.get("cost") is not None and int(card.get("cost") or 0) in focus_costs:
            return True
        if card.get("kind") == "live" and int(card.get("energy_boost_n") or 0) > 0 and has_four_bridge:
            return True
        return False

    key_total = int(focus_turn_info.get("key_total") or 0)
    if key_total <= 0 or any(is_key(card) for card in initial_hand):
        return {}
    no_keep_draws = no_keep_windows[focus_turn] if focus_turn < len(no_keep_windows) else no_keep_windows[-1]
    two_keep_windows = _mulligan_draw_windows(2, min(3, len(target_alternatives_by_turn)))
    two_keep_draws = two_keep_windows[focus_turn] if focus_turn < len(two_keep_windows) else two_keep_windows[-1]
    no_keep_key_p = _probability_find_key_by_draws(deck_cards, initial_hand, is_key, draws=no_keep_draws)
    two_keep_key_p = _probability_find_key_by_draws(deck_cards, initial_hand, is_key, draws=two_keep_draws)
    no_keep_target_p = _access_probability_for_alternatives([], initial_hand, deck_cards, focus_turn_info.get("alternatives") or [], no_keep_draws)
    two_keep_target_p = _access_probability_for_alternatives([], initial_hand, deck_cards, focus_turn_info.get("alternatives") or [], two_keep_draws)
    return {
        "turn_index": focus_turn,
        "label": f"T{focus_turn + 1} bottleneck key",
        "key_total": key_total,
        "focus_costs": sorted(focus_costs),
        "turn_access_probability": float(focus_turn_info.get("access_probability") or 0.0),
        "no_keep_probability": no_keep_target_p,
        "two_keep_probability": two_keep_target_p,
        "key_no_keep_probability": no_keep_key_p,
        "key_two_keep_probability": two_keep_key_p,
        "gap": max(0.0, no_keep_target_p - two_keep_target_p),
        "is_key": is_key,
    }


def _probability_find_key_by_draws(
    deck_cards: list[dict[str, Any]],
    unavailable_cards: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
    *,
    draws: int,
) -> float:
    unavailable_counts = Counter(str(card.get("card_no") or "") for card in unavailable_cards)
    pool: list[dict[str, Any]] = []
    for card in deck_cards:
        card_no = str(card.get("card_no") or "")
        if unavailable_counts.get(card_no, 0) > 0:
            unavailable_counts[card_no] -= 1
            continue
        pool.append(card)
    total = len(pool)
    key_count = sum(1 for card in pool if predicate(card))
    draws = max(0, min(int(draws), total))
    if key_count <= 0 or draws <= 0:
        return 0.0
    if total - key_count < draws:
        return 1.0
    return 1.0 - (comb(total - key_count, draws) / comb(total, draws))


def _mulligan_candidate_diagnostics(
    kept_cards: list[dict[str, Any]],
    initial_hand: list[dict[str, Any]],
    deck_cards: list[dict[str, Any]],
    target_alternatives_by_turn: list[list[list[int]]],
    windows: list[int],
) -> dict[str, Any]:
    kept_costs = _member_cost_counts_from_cards(kept_cards)
    out: dict[str, Any] = {
        "kept_twos": int(kept_costs.get(2, 0) or 0),
        "redraws": max(0, 6 - len(kept_cards)),
    }
    if len(target_alternatives_by_turn) >= 2:
        turn_two = target_alternatives_by_turn[1] or []
        out["t2_need_twos"] = max((Counter(int(value) for value in shape).get(2, 0) for shape in turn_two), default=0)
        out["t2_targets"] = _alternatives_trace_label(turn_two)
    if len(target_alternatives_by_turn) >= 3:
        turn_three = target_alternatives_by_turn[2] or []
        turn_three_targets = sorted({
            int(value)
            for shape in turn_three
            for value in shape
            if int(value) > 2
        })
        draws = windows[2] if len(windows) > 2 else windows[-1] if windows else 0
        out["t3_targets"] = turn_three_targets
        out["t3_access"] = round(_access_probability_for_alternatives(kept_cards, initial_hand, deck_cards, turn_three, draws), 3)
        out["t3_draws"] = draws
    return out


def _progression_plan_label(plan: list[list[int]]) -> str:
    return " -> ".join(_shape_trace_label(list(shape)) for shape in plan) if plan else "none"


def _early_progression_plan_options(
    target_alternatives_by_turn: list[list[list[int]]],
    *,
    max_turns: int = 3,
    max_options_per_turn: int = 5,
) -> list[list[list[int]]]:
    turns = [
        [list(shape) for shape in alternatives[:max_options_per_turn]]
        for alternatives in target_alternatives_by_turn[:max_turns]
        if alternatives
    ]
    if not turns:
        return []
    plans: list[list[list[int]]] = [[]]
    for alternatives in turns:
        next_plans: list[list[list[int]]] = []
        for plan in plans:
            for shape in alternatives:
                next_plans.append(plan + [list(shape)])
        plans = next_plans[:125]
    unique: list[list[list[int]]] = []
    seen: set[tuple[tuple[int, ...], ...]] = set()
    for plan in plans:
        key = tuple(tuple(int(value) for value in shape) for shape in plan)
        if key in seen:
            continue
        seen.add(key)
        unique.append(plan)
    return unique


def _plan_access_score(
    kept_cards: list[dict[str, Any]],
    initial_hand: list[dict[str, Any]],
    deck_cards: list[dict[str, Any]],
    plan: list[list[int]],
    windows: list[int],
) -> dict[str, Any]:
    probabilities: list[float] = []
    prefix = 1.0
    score = 0.0
    weights = [22.0, 18.0, 13.0]
    kept_costs = _member_cost_list_from_counts(_member_cost_counts_from_cards(kept_cards))
    for index, shape in enumerate(plan[:3]):
        draws = windows[index] if index < len(windows) else windows[-1] if windows else 0
        probability = _access_probability_for_alternatives(
            kept_cards,
            initial_hand,
            deck_cards,
            [shape],
            draws,
            early_plan_slots=index < 2,
        )
        probabilities.append(probability)
        prefix *= probability
        score += weights[index] * prefix
        score += weights[index] * 0.2 * probability
        if _shape_meets_early_plan_slots(kept_costs, list(shape)):
            score += max(0.0, 3.0 - index)
    return {
        "label": _progression_plan_label(plan),
        "score": score,
        "probabilities": probabilities,
        "prefix": prefix,
    }


def _choose_early_progression_plans(
    initial_hand: list[dict[str, Any]],
    deck_cards: list[dict[str, Any]],
    target_alternatives_by_turn: list[list[list[int]]],
) -> dict[str, Any]:
    windows = _mulligan_draw_windows(0, min(3, len(target_alternatives_by_turn)))
    options = _early_progression_plan_options(target_alternatives_by_turn)
    ranked: list[dict[str, Any]] = []
    for plan in options:
        ranked.append({
            "plan": plan,
            **_plan_access_score(initial_hand, initial_hand, deck_cards, plan, [0, 0, 0]),
            "redraw_score": _plan_access_score([], initial_hand, deck_cards, plan, windows),
        })
    ranked.sort(
        key=lambda item: (
            float(item.get("score") or 0.0),
            float((item.get("redraw_score") or {}).get("score") or 0.0),
            item.get("label") or "",
        ),
        reverse=True,
    )
    main = ranked[0] if ranked else {}
    sub = ranked[1] if len(ranked) > 1 else {}
    return {
        "main_plan": main.get("plan") or [],
        "main_label": main.get("label") or "none",
        "main_initial_probabilities": list(main.get("probabilities") or []),
        "sub_plan": sub.get("plan") or [],
        "sub_label": sub.get("label") or "none",
        "sub_initial_probabilities": list(sub.get("probabilities") or []),
        "ranked": ranked[:5],
    }


def _is_progression_live_support(card: dict[str, Any], plan: list[list[int]]) -> bool:
    if card.get("kind") != "live":
        return False
    plan_costs = [int(value) for shape in plan for value in shape]
    high_goal = max(plan_costs, default=0) >= 10
    if _energy_boost_amount(card) > 0:
        return high_goal or any(sum(shape) >= 8 for shape in plan)
    tags = set(card.get("progression_support_tags") or [])
    if int(card.get("progression_accel_value") or 0) >= 2 or "major_acceleration" in tags:
        return high_goal or any(sum(shape) >= 8 for shape in plan)
    if "cost_reduction" in tags or bool(card.get("cost_reduction")):
        return high_goal
    if "overcost_member_play" in tags or bool(card.get("overcost_member_play")):
        return high_goal
    if int(card.get("live_success_member_recovery_n") or card.get("member_recovery_n") or 0) > 0:
        return high_goal
    return False


def _mulligan_visible_plan_card_adjustment(
    kept_cards: list[dict[str, Any]],
    initial_hand: list[dict[str, Any]],
    plan: list[list[int]],
    *,
    weight_scale: float = 1.0,
) -> float:
    if not plan:
        return 0.0
    score = 0.0
    kept_counts = _member_cost_counts_from_cards(kept_cards)
    initial_counts = _member_cost_counts_from_cards(initial_hand)
    turn_weights = [18.0, 13.0, 8.0]
    for turn_index, shape in enumerate(plan[:3]):
        weight = turn_weights[turn_index] if turn_index < len(turn_weights) else 5.0
        needed = Counter(int(value) for value in shape)
        for cost, needed_count in needed.items():
            visible = int(initial_counts.get(cost, 0) or 0)
            if visible <= 0:
                continue
            kept = min(int(kept_counts.get(cost, 0) or 0), int(needed_count))
            missing_visible = min(int(needed_count), visible) - kept
            score += kept * weight * weight_scale
            if missing_visible > 0:
                score -= missing_visible * weight * 1.35 * weight_scale
        # Do not double count the same exact low-cost slots too harshly across
        # turns, but still make T1/T2 visible cards matter.
        if turn_index >= 1:
            score *= 0.98
    support_lives = [card for card in initial_hand if _is_progression_live_support(card, plan)]
    kept_support_lives = [card for card in kept_cards if _is_progression_live_support(card, plan)]
    if support_lives:
        support_weight = 11.0 if max((int(value) for shape in plan for value in shape), default=0) >= 10 else 7.0
        score += min(len(kept_support_lives), 1) * support_weight * weight_scale
        if not kept_support_lives:
            score -= min(len(support_lives), 1) * support_weight * 0.85 * weight_scale
        score -= max(0, len(kept_support_lives) - 1) * 3.0 * weight_scale
    return score


def _mulligan_late_card_before_early_secured_penalty(
    kept_cards: list[dict[str, Any]],
    plan: list[list[int]],
) -> float:
    if not plan:
        return 0.0
    kept_costs = _member_cost_list_from_counts(_member_cost_counts_from_cards(kept_cards))
    earliest_miss = None
    for turn_index, shape in enumerate(plan[:3]):
        if not _shape_meets_early_plan_slots(kept_costs, list(shape)):
            earliest_miss = turn_index
            break
    if earliest_miss is None or earliest_miss > 1:
        return 0.0
    early_costs = {
        int(value)
        for shape in plan[: earliest_miss + 1]
        for value in shape
    }
    future_costs = {
        int(value)
        for shape in plan[earliest_miss + 1:3]
        for value in shape
    }
    penalty = 0.0
    for card in kept_cards:
        if card.get("kind") == "member":
            cost = int(card.get("cost") or 0)
            if cost >= 10 and cost in future_costs and cost not in early_costs:
                penalty += 44.0 if earliest_miss == 0 else 22.0
            elif cost >= 13 and cost not in early_costs:
                penalty += 36.0 if earliest_miss == 0 else 16.0
        elif card.get("kind") == "live" and not _is_progression_live_support(card, plan):
            score = int(card.get("score") or 0)
            if score >= 4:
                penalty += 18.0 if earliest_miss == 0 else 8.0
    return penalty


def _mulligan_subset_score(
    kept_cards: list[dict[str, Any]],
    initial_hand: list[dict[str, Any]],
    deck_cards: list[dict[str, Any]],
    target_alternatives_by_turn: list[list[list[int]]],
    focus: dict[str, Any] | None = None,
    plan_focus: dict[str, Any] | None = None,
) -> dict[str, Any]:
    windows = _mulligan_draw_windows(len(kept_cards), min(3, len(target_alternatives_by_turn)))
    probabilities: list[float] = []
    for index, alternatives in enumerate(target_alternatives_by_turn[:3]):
        draws = windows[index] if index < len(windows) else windows[-1] if windows else 0
        probabilities.append(_access_probability_for_alternatives(kept_cards, initial_hand, deck_cards, alternatives or [], draws))
    weights = [10.0, 8.0, 4.0]
    prefix = 1.0
    score = 0.0
    for index, probability in enumerate(probabilities):
        prefix *= probability
        score += weights[index] * prefix
        score += (weights[index] * 0.25) * probability
    kept_costs = _member_cost_list_from_counts(_member_cost_counts_from_cards(kept_cards))
    if target_alternatives_by_turn:
        if any(_shape_meets_target(kept_costs, list(shape)) for shape in target_alternatives_by_turn[0] or []):
            score += 3.0
    if len(target_alternatives_by_turn) >= 2:
        if any(_shape_meets_target(kept_costs, list(shape)) for shape in target_alternatives_by_turn[1] or []):
            score += 2.0
    plan_score: dict[str, Any] = {}
    if plan_focus:
        main_plan = plan_focus.get("main_plan") if isinstance(plan_focus.get("main_plan"), list) else []
        sub_plan = plan_focus.get("sub_plan") if isinstance(plan_focus.get("sub_plan"), list) else []
        if main_plan:
            main_metrics = _plan_access_score(kept_cards, initial_hand, deck_cards, main_plan, windows)
            score += float(main_metrics.get("score") or 0.0) * 1.25
            score += _mulligan_visible_plan_card_adjustment(kept_cards, initial_hand, main_plan, weight_scale=1.0)
            score -= _mulligan_late_card_before_early_secured_penalty(kept_cards, main_plan)
            plan_score["main_label"] = main_metrics.get("label") or ""
            plan_score["main_probabilities"] = list(main_metrics.get("probabilities") or [])
        if sub_plan:
            sub_metrics = _plan_access_score(kept_cards, initial_hand, deck_cards, sub_plan, windows)
            score += float(sub_metrics.get("score") or 0.0) * 0.45
            score += _mulligan_visible_plan_card_adjustment(kept_cards, initial_hand, sub_plan, weight_scale=0.35)
            plan_score["sub_label"] = sub_metrics.get("label") or ""
            plan_score["sub_probabilities"] = list(sub_metrics.get("probabilities") or [])
    score -= _mulligan_duplicate_penalty(kept_cards, target_alternatives_by_turn)
    score += _mulligan_profile_adjustment(kept_cards, initial_hand, target_alternatives_by_turn)
    if focus:
        redraws = 6 - len(kept_cards)
        focus_turn_index = int(focus.get("turn_index") or 0)
        deadline_weight = 1.0 + max(0, 2 - focus_turn_index) * 0.35
        # When a structurally fragile turn key is absent, favor redraws that dig toward it.
        score += redraws * deadline_weight * (0.8 + float(focus.get("gap") or 0.0) * 8.0)
        kept_counts = _member_cost_counts_from_cards(kept_cards)
        deck_cost_counts = _member_cost_counts(deck_cards)
        turn_one_costs = {
            int(value)
            for shape in target_alternatives_by_turn[0] or []
            for value in shape
        } if target_alternatives_by_turn else set()
        if kept_counts.get(2, 0) > 2:
            score -= (kept_counts.get(2, 0) - 2) * 2.0
        for card in kept_cards:
            if card.get("kind") != "member" or card.get("cost") is None:
                continue
            cost = int(card.get("cost") or 0)
            if cost in turn_one_costs:
                continue
            if cost not in set(focus.get("focus_costs") or []) and int(deck_cost_counts.get(cost, 0) or 0) > 4:
                # Future targets with enough copies should not block a weak bottleneck redraw plan.
                score -= 6.0 * deadline_weight
        if sum(1 for card in kept_cards if card.get("kind") == "member" and int(card.get("cost") or 0) >= 10) > 1:
            score -= 2.5
    # Prefer more redraws when probability is effectively tied.
    score += (6 - len(kept_cards)) * 0.015
    return {
        "score": score,
        "probabilities": probabilities,
        "draw_windows": windows,
        "diagnostics": _mulligan_candidate_diagnostics(kept_cards, initial_hand, deck_cards, target_alternatives_by_turn, windows),
        "critical_focus": {
            key: value for key, value in focus.items() if key != "is_key"
        } if focus else {},
        "plan_focus": plan_score,
    }


def _all_keep_subsets(hand: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    out: list[list[dict[str, Any]]] = []
    n = len(hand)
    for mask in range(1 << n):
        out.append([hand[index] for index in range(n) if mask & (1 << index)])
    return out


def _choose_mulligan_plan(
    hand: list[dict[str, Any]],
    target_turns: list[list[int]],
    deck_cards: list[dict[str, Any]],
    target_alternatives_by_turn: list[list[list[int]]] | None = None,
) -> dict[str, Any]:
    if target_alternatives_by_turn is None:
        target_alternatives_by_turn = [[list(turn)] for turn in target_turns]
    best: tuple[float, float, int, list[dict[str, Any]], dict[str, Any]] | None = None
    candidates: list[dict[str, Any]] = []
    focus = _mulligan_bottleneck_focus(hand, deck_cards, target_alternatives_by_turn)
    plan_focus = _choose_early_progression_plans(hand, deck_cards, target_alternatives_by_turn)
    for kept_cards in _all_keep_subsets(hand):
        metrics = _mulligan_subset_score(kept_cards, hand, deck_cards, target_alternatives_by_turn, focus, plan_focus)
        keep_need_score = sum(
            float(_card_need_profile(card, target_alternatives_by_turn, deck_cards).get("keep_value") or 0.0)
            for card in kept_cards
        )
        tie = (float(metrics["score"]), keep_need_score, 6 - len(kept_cards), kept_cards, metrics)
        candidates.append({
            "kept": kept_cards,
            "returned": [card for card in hand if card not in kept_cards],
            **metrics,
        })
        if best is None or tie[:3] > best[:3]:
            best = tie
    if best is None:
        return {"keep": [], "returned": list(hand), "score": 0.0, "probabilities": [], "draw_windows": [], "candidates": []}
    keep = list(best[3])
    ranked = sorted(candidates, key=lambda item: float(item.get("score") or 0), reverse=True)[:5]
    return {
        "keep": keep,
        "returned": [card for card in hand if card not in keep],
        "score": float(best[4].get("score") or 0),
        "probabilities": list(best[4].get("probabilities") or []),
        "draw_windows": list(best[4].get("draw_windows") or []),
        "critical_focus": dict(best[4].get("critical_focus") or {}),
        "plan_focus": plan_focus,
        "candidates": ranked,
    }


def _choose_mulligan_keep(
    hand: list[dict[str, Any]],
    target_turns: list[list[int]],
    deck_cards: list[dict[str, Any]],
    target_alternatives_by_turn: list[list[list[int]]] | None = None,
) -> list[dict[str, Any]]:
    return list(_choose_mulligan_plan(hand, target_turns, deck_cards, target_alternatives_by_turn).get("keep") or [])[:6]


def _apply_hand_smoothing(hand: list[dict[str, Any]], deck: list[dict[str, Any]], draw_index: int) -> int:
    usable = [card for card in hand if card.get("kind") == "live" and int(card.get("draw_n") or 0) > 0]
    if not usable:
        return draw_index
    live = max(usable, key=lambda card: int(card.get("draw_n") or 0))
    hand.remove(live)
    draw_n = min(int(live.get("draw_n") or 0), max(0, len(deck) - draw_index))
    for _ in range(draw_n):
        hand.append(deck[draw_index])
        draw_index += 1
    if draw_n >= 2 and hand:
        discard = min(hand, key=lambda card: (int(card.get("value") or 0), 0 if card.get("kind") == "other" else 1))
        hand.remove(discard)
    return draw_index


def _best_energy_boost_live(hand: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [
        card for card in hand
        if _energy_boost_amount(card) > 0
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda card: (_energy_boost_amount(card), int(card.get("score") or 0)))


def _choose_live_set_cards(
    hand: list[dict[str, Any]],
    prefer_energy_boost: bool,
    future_targets: list[list[int]],
    deck_cards: list[dict[str, Any]],
    live_score_target: dict[str, Any] | None = None,
    future_alternatives_by_turn: list[list[list[int]]] | None = None,
    start_turn_index: int = 0,
    stage: list[dict[str, Any] | None] | None = None,
    current_recovery_alternatives: list[list[int]] | None = None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    def member_cost(card: dict[str, Any]) -> int:
        return int(card.get("cost") or 0)

    def is_energy_live(card: dict[str, Any]) -> bool:
        return _energy_boost_amount(card) > 0

    def is_setup_draw_live(card: dict[str, Any]) -> bool:
        return card.get("kind") == "live" and int(card.get("score") or 0) == 0 and int(card.get("draw_n") or 0) >= 2

    def non_energy_lives(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [card for card in cards if card.get("kind") == "live" and not is_energy_live(card)]

    def highest_score_live(cards: list[dict[str, Any]]) -> dict[str, Any] | None:
        lives = non_energy_lives(cards)
        if not lives:
            return None
        return max(lives, key=lambda card: (int(card.get("score") or 0), int(card.get("draw_n") or 0), str(card.get("card_no") or "")))

    def lowest_score_live(cards: list[dict[str, Any]]) -> dict[str, Any] | None:
        lives = non_energy_lives(cards)
        if not lives:
            return None
        return min(lives, key=lambda card: (int(card.get("score") or 0), -int(card.get("draw_n") or 0), str(card.get("card_no") or "")))

    def add_unique(out: list[dict[str, Any]], card: dict[str, Any] | None) -> None:
        if card is not None and card in hand and card not in out and len(out) < 3:
            out.append(card)

    def target_score_live(cards: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not isinstance(live_score_target, dict):
            return None
        if live_score_target.get("score_priority_mode") != "finale_pressure":
            return None
        accepted_scores = {
            int(score)
            for score in live_score_target.get("accepted_scores", []) or []
        }
        if not accepted_scores:
            return None
        candidates = [
            card for card in cards
            if _live_basic_success_candidate(stage, card)
            and card.get("kind") == "live"
            and card.get("score") is not None
            and int(card.get("score") or 0) in accepted_scores
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda card: (
            int(card.get("score") or 0),
            int(card.get("draw_n") or 0),
            str(card.get("card_no") or ""),
        ))

    def selected_live_for_success(cards: list[dict[str, Any]]) -> dict[str, Any] | None:
        score_live = target_score_live(cards)
        if score_live is not None:
            return score_live
        candidates = [
            card for card in cards
            if _live_basic_success_candidate(stage, card)
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda card: (
            _live_effect_play_value(
                card,
                future_alternatives_by_turn or [],
                start_turn_index=start_turn_index,
                prefer_energy_boost=prefer_energy_boost,
            ),
            int(card.get("score") or 0),
            int(card.get("draw_n") or 0),
            str(card.get("card_no") or ""),
        ))

    def has_shape(shape: list[int]) -> bool:
        wanted = sorted(int(value) for value in shape)
        for alternatives in future_alternatives_by_turn or []:
            for alternative in alternatives or []:
                if sorted(int(value) for value in alternative) == wanted:
                    return True
        return False

    def future_exact_need(cost: int, *, min_offset: int = 1, max_offset: int = 3) -> int:
        need = 0
        for alternatives in (future_alternatives_by_turn or [])[min_offset:max_offset + 1]:
            for shape in alternatives or []:
                need = max(need, int(Counter(int(value) for value in shape).get(int(cost), 0) or 0))
        return need

    def total_available_cost_count(cost: int) -> int:
        return sum(1 for item in stage_costs if int(item) == int(cost)) + sum(1 for item in hand_costs if int(item) == int(cost))

    def future_anchor_protected(card: dict[str, Any]) -> bool:
        if card.get("kind") != "member" or card.get("cost") is None:
            return False
        cost = int(card.get("cost") or 0)
        if cost < 10:
            return False
        need = future_exact_need(cost)
        return need > 0 and total_available_cost_count(cost) <= need

    def best_two(cards: list[dict[str, Any]]) -> dict[str, Any] | None:
        twos = [card for card in cards if card.get("kind") == "member" and member_cost(card) == 2]
        if not twos:
            return None
        return max(twos, key=lambda card: (
            _heart_counts(card.get("base_hearts_raw")).get("紫", 0),
            _heart_counts(card.get("base_hearts_raw")).get("青", 0),
            1 if str(card.get("effect_text") or "").strip() in {"", "(なし)", "なし"} else 0,
            str(card.get("card_no") or ""),
        ))

    if future_alternatives_by_turn is None:
        future_alternatives_by_turn = [[list(target)] for target in future_targets]
    stage_costs = _stage_costs(stage or [])
    hand_members = [card for card in hand if card.get("kind") == "member" and card.get("cost") is not None]
    hand_costs = [member_cost(card) for card in hand_members]
    combined_costs = sorted(stage_costs + hand_costs, reverse=True)
    current_alternatives = future_alternatives_by_turn[0] if future_alternatives_by_turn else []
    stage_hits_current = bool(current_alternatives) and any(
        _shape_meets_target(stage_costs, list(shape))
        for shape in current_alternatives
    )
    stage_hits_recovery = bool(current_recovery_alternatives) and any(
        _shape_meets_target(stage_costs, list(shape))
        for shape in current_recovery_alternatives or []
    )
    recovery_rescue_mode = bool(stage_hits_recovery and not stage_hits_current)
    next_alternatives = future_alternatives_by_turn[1] if len(future_alternatives_by_turn) > 1 else (future_alternatives_by_turn[0] if future_alternatives_by_turn else [])
    next_reachable = bool(next_alternatives) and any(_shape_meets_target(combined_costs, list(shape)) for shape in next_alternatives)
    five_axis = has_shape([2, 5, 2])
    ten_axis = has_shape([2, 10, 2])
    kimi_axis = has_shape([7, 2])

    strategic: list[dict[str, Any]] = []
    if not stage_costs:
        return None, []
    if stage_costs and five_axis:
        has_energy = any(is_energy_live(card) for card in hand)
        has_mid = any(cost in {4, 5} for cost in hand_costs)
        has_two = any(cost == 2 for cost in hand_costs)
        stage_or_hand_has_mid = any(cost in {4, 5} for cost in stage_costs + hand_costs)
        stage_or_hand_has_two = any(cost == 2 for cost in stage_costs + hand_costs)
        next_alternatives_for_search = future_alternatives_by_turn[1] if len(future_alternatives_by_turn) > 1 else []
        next_needs_eleven = any(11 in [int(value) for value in shape] for shape in next_alternatives_for_search or [])
        if start_turn_index >= 1 and (stage_hits_current or stage_hits_recovery) and next_needs_eleven:
            if prefer_energy_boost:
                add_unique(strategic, next((card for card in hand if is_energy_live(card)), None))
            exchange_members = [
                card for card in hand_members
                if member_cost(card) != 11
                and not future_anchor_protected(card)
            ]
            for card in sorted(exchange_members, key=lambda item: (
                0 if member_cost(item) >= 13 else 1,
                0 if member_cost(item) in {2, 4, 5} else 1,
                member_cost(item),
                str(item.get("card_no") or ""),
            )):
                add_unique(strategic, card)
            add_unique(strategic, highest_score_live(hand))
            if strategic:
                return selected_live_for_success(strategic), strategic
        if has_energy and not stage_or_hand_has_mid:
            add_unique(strategic, best_two(hand))
            add_unique(strategic, next((card for card in hand_members if member_cost(card) >= 13), None))
            add_unique(strategic, lowest_score_live(hand))
        elif not stage_or_hand_has_two:
            duplicate_four = [card for card in hand_members if member_cost(card) == 4]
            add_unique(strategic, duplicate_four[0] if duplicate_four else None)
            add_unique(strategic, next((card for card in hand_members if member_cost(card) >= 13), None))
            add_unique(strategic, highest_score_live(hand))
        elif next_reachable:
            add_unique(strategic, highest_score_live(hand))
        if strategic:
            return selected_live_for_success(strategic), strategic

    if stage_costs and ten_axis:
        has_ten = any(cost == 10 for cost in hand_costs)
        has_energy = any(is_energy_live(card) for card in hand)
        has_four = any(cost == 4 for cost in hand_costs)
        has_two = any(cost == 2 for cost in hand_costs)
        stage_or_hand_has_four = any(cost == 4 for cost in stage_costs + hand_costs)
        stage_or_hand_has_two = any(cost == 2 for cost in stage_costs + hand_costs)
        if has_ten and not stage_or_hand_has_four:
            extra_twos = [card for card in hand_members if member_cost(card) == 2]
            add_unique(strategic, extra_twos[0] if extra_twos else None)
            add_unique(strategic, next((card for card in hand_members if member_cost(card) >= 13), None))
            add_unique(strategic, lowest_score_live(hand))
        elif has_ten and not stage_or_hand_has_two:
            for card in sorted((card for card in hand_members if member_cost(card) >= 13 and not future_anchor_protected(card)), key=lambda item: member_cost(item)):
                add_unique(strategic, card)
            add_unique(strategic, highest_score_live(hand))
        elif not has_ten and has_energy and has_four:
            add_unique(strategic, next((card for card in hand if is_energy_live(card)), None))
            for card in sorted((card for card in hand_members if member_cost(card) >= 13 and member_cost(card) != 11 and not future_anchor_protected(card)), key=lambda item: member_cost(item)):
                add_unique(strategic, card)
        elif not has_ten and not has_energy:
            if start_turn_index >= 2:
                add_unique(strategic, highest_score_live(hand))
            stage_has_four = any(cost == 4 for cost in stage_costs)
            stage_two_count = sum(1 for cost in stage_costs if cost == 2)
            if stage_two_count >= 2:
                for card in [card for card in hand_members if member_cost(card) == 2]:
                    add_unique(strategic, card)
            elif not stage_has_four:
                extra_twos = [card for card in hand_members if member_cost(card) == 2]
                add_unique(strategic, extra_twos[0] if extra_twos else None)
            for card in sorted((card for card in hand_members if member_cost(card) >= 13 and not future_anchor_protected(card)), key=lambda item: member_cost(item)):
                add_unique(strategic, card)
        if strategic:
            return selected_live_for_success(strategic), strategic

    if stage_costs and kimi_axis:
        has_seven = any(cost == 7 for cost in hand_costs)
        setup_live = next((card for card in hand if is_setup_draw_live(card)), None)
        if has_seven and setup_live is not None:
            add_unique(strategic, setup_live)
        elif has_seven:
            add_unique(strategic, highest_score_live(hand))
        elif setup_live is not None:
            add_unique(strategic, setup_live)
            add_unique(strategic, best_two(hand))
            add_unique(strategic, next((card for card in hand_members if member_cost(card) >= 13), None))
        if strategic:
            return selected_live_for_success(strategic), strategic

    if recovery_rescue_mode and next_alternatives:
        next_cost_needs: Counter[int] = Counter()
        for shape in next_alternatives:
            for cost, count in Counter(int(value) for value in shape).items():
                next_cost_needs[cost] = max(next_cost_needs[cost], count)
        for card in sorted(hand_members, key=lambda item: (
            0 if int(item.get("cost") or 0) >= 13 and not next_cost_needs.get(int(item.get("cost") or 0), 0) else 1,
            0 if int(item.get("cost") or 0) not in next_cost_needs else 1,
            int(item.get("cost") or 0),
            str(item.get("card_no") or ""),
        )):
            cost = member_cost(card)
            if future_anchor_protected(card):
                continue
            if next_cost_needs.get(cost, 0) and total_available_cost_count(cost) <= int(next_cost_needs.get(cost, 0)):
                continue
            add_unique(strategic, card)
        add_unique(strategic, highest_score_live(hand))
        if strategic:
            return selected_live_for_success(strategic), strategic

    selected: list[dict[str, Any]] = []
    live_for_success: dict[str, Any] | None = None
    if prefer_energy_boost:
        energy_lives = [
            card for card in hand
            if _energy_boost_amount(card) > 0
        ]
        if energy_lives:
            live_for_success = max(energy_lives, key=lambda card: (_energy_boost_amount(card), int(card.get("score") or 0)))
            selected.append(live_for_success)

    score_live = _best_live_for_score_target(hand, live_score_target, protect_energy_boost=not prefer_energy_boost)
    if score_live is not None and score_live not in selected:
        selected.append(score_live)
    if score_live is not None and (
        live_for_success is None
        or (isinstance(live_score_target, dict) and live_score_target.get("score_priority_mode") == "finale_pressure")
    ):
        live_for_success = score_live

    candidates = [card for card in hand if card not in selected]
    stage_cost_counts = Counter(int(card.get("cost") or 0) for card in (stage or []) if card and card.get("kind") == "member")
    hand_cost_counts = Counter(
        int(card.get("cost") or 0)
        for card in candidates
        if card.get("kind") == "member" and card.get("cost") is not None
    )
    protect_counts: Counter[int] = Counter()
    for alternatives in future_alternatives_by_turn[:2]:
        for shape in alternatives or []:
            for cost, count in Counter(int(value) for value in shape).items():
                protect_counts[cost] = max(int(protect_counts.get(cost, 0) or 0), int(count))
    for alternatives in future_alternatives_by_turn[2:3]:
        for shape in alternatives or []:
            for cost, count in Counter(int(value) for value in shape).items():
                if int(cost) >= 10:
                    protect_counts[cost] = max(int(protect_counts.get(cost, 0) or 0), int(count))
    exchange_budget_by_cost: Counter[int] = Counter()
    for cost, hand_count in hand_cost_counts.items():
        deck_count = _member_cost_counts(deck_cards).get(cost, 0)
        protected = int(protect_counts.get(cost, 0) or 0)
        available = int(stage_cost_counts.get(cost, 0) or 0) + int(hand_count)
        duplicate_budget = max(0, available - protected)
        if deck_count >= 8:
            exchange_budget_by_cost[cost] = duplicate_budget
        elif duplicate_budget > 0 and int(hand_count) > max(0, protected - int(stage_cost_counts.get(cost, 0) or 0)):
            exchange_budget_by_cost[cost] = duplicate_budget
    scored = sorted(
        (
            (
                card,
                float(_card_need_profile(
                    card,
                    future_alternatives_by_turn,
                    deck_cards,
                    start_turn_index=start_turn_index,
                ).get("exchange_cost") or 0.0),
            )
            for card in candidates
        ),
        key=lambda item: (item[1], int(item[0].get("value") or 0), str(item[0].get("card_no") or "")),
    )
    exchanged_by_cost: Counter[int] = Counter()
    for card, score in scored:
        if len(selected) >= 3:
            break
        if _energy_boost_amount(card) > 0 and not prefer_energy_boost:
            continue
        adjusted_score = float(score)
        cost = None
        if card.get("kind") == "member" and card.get("cost") is not None:
            cost = int(card.get("cost") or 0)
            if exchange_budget_by_cost.get(cost, 0) > exchanged_by_cost.get(cost, 0):
                adjusted_score *= 0.35
            elif score > 4.0:
                continue
        if adjusted_score <= 4.0:
            selected.append(card)
            if cost is not None:
                exchanged_by_cost[cost] += 1
    if live_for_success is None:
        live_for_success = selected_live_for_success(selected)
    return live_for_success, selected


def _live_set_exchange(
    hand: list[dict[str, Any]],
    deck: list[dict[str, Any]],
    draw_index: int,
    prefer_energy_boost: bool,
    future_targets: list[list[int]],
    deck_cards: list[dict[str, Any]],
    live_score_target: dict[str, Any] | None = None,
    future_alternatives_by_turn: list[list[list[int]]] | None = None,
    start_turn_index: int = 0,
    stage: list[dict[str, Any] | None] | None = None,
    current_recovery_alternatives: list[list[int]] | None = None,
) -> tuple[dict[str, Any] | None, int, list[dict[str, Any]]]:
    live_for_success, selected = _choose_live_set_cards(
        hand,
        prefer_energy_boost,
        future_targets,
        deck_cards,
        live_score_target,
        future_alternatives_by_turn,
        start_turn_index,
        stage,
        current_recovery_alternatives,
    )

    for card in selected:
        if card in hand:
            hand.remove(card)
    for _ in selected:
        if draw_index < len(deck):
            hand.append(deck[draw_index])
            draw_index += 1
    return live_for_success, draw_index, selected


def _card_trace_label(card: dict[str, Any] | None) -> str:
    if not card:
        return "none"
    name = str(card.get("name") or "").strip()
    card_no = str(card.get("card_no") or "").strip()
    kind = str(card.get("kind") or "").strip()
    value = card.get("cost") if kind == "member" else card.get("score")
    value_label = "cost" if kind == "member" else "score"
    tags = card.get("progression_support_tags") or []
    tag_text = "" if not tags else " tags=" + ",".join(str(tag) for tag in tags)
    base = " ".join(part for part in (card_no, name) if part)
    return f"{base or 'unknown'} {value_label}={value}{tag_text}"


def _cards_trace_label(cards: list[dict[str, Any]]) -> str:
    if not cards:
        return "none"
    return "; ".join(_card_trace_label(card) for card in cards)


def _shape_trace_label(shape: list[int]) -> str:
    return "-".join(str(value) for value in shape) if shape else "none"


def _alternatives_trace_label(alternatives: list[list[int]]) -> str:
    if not alternatives:
        return "none"
    return " / ".join(_shape_trace_label(list(shape)) for shape in alternatives)


def _need_score_trace(cards: list[dict[str, Any]], alternatives: list[list[list[int]]], deck_cards: list[dict[str, Any]], limit: int = 6) -> str:
    scored = sorted(
        (
            (card, _card_need_profile(card, alternatives, deck_cards))
            for card in cards
        ),
        key=lambda item: (-float(item[1].get("total") or 0.0), str(item[0].get("card_no") or "")),
    )[:limit]
    if not scored:
        return "none"
    parts: list[str] = []
    for card, profile in scored:
        tags = profile.get("tags") if isinstance(profile.get("tags"), list) else []
        tag_text = "" if not tags else " flags=" + ",".join(str(tag) for tag in tags)
        parts.append(
            "{} need={} keep={} exch={} future={} dig={} rec={} side={}{}".format(
                _card_trace_label(card),
                round(float(profile.get("total") or 0.0), 2),
                round(float(profile.get("keep_value") or 0.0), 2),
                round(float(profile.get("exchange_cost") or 0.0), 2),
                round(float(profile.get("future_play_value") or 0.0), 2),
                round(float(profile.get("dig_target_value") or 0.0), 2),
                round(float(profile.get("recovery_value") or 0.0), 2),
                round(float(profile.get("sideboard_like") or 0.0), 2),
                tag_text,
            )
        )
    return "; ".join(parts)


def _mulligan_candidate_trace(candidates: list[dict[str, Any]], limit: int = 5) -> list[str]:
    lines: list[str] = []
    for candidate in candidates[:limit]:
        kept = candidate.get("kept", []) if isinstance(candidate.get("kept"), list) else []
        probabilities = candidate.get("probabilities", []) if isinstance(candidate.get("probabilities"), list) else []
        diagnostics = candidate.get("diagnostics", {}) if isinstance(candidate.get("diagnostics"), dict) else {}
        plan_focus = candidate.get("plan_focus", {}) if isinstance(candidate.get("plan_focus"), dict) else {}
        probability_text = "/".join(str(round(float(value), 3)) for value in probabilities)
        main_probs = plan_focus.get("main_probabilities", []) if isinstance(plan_focus.get("main_probabilities"), list) else []
        main_prob_text = "/".join(str(round(float(value), 3)) for value in main_probs) if main_probs else "n/a"
        lines.append(
            "score={} p(T1/T2/T3)={} main_plan={} main_p={} kept2={}/{} redraws={} t3_targets={} t3_access={} t3_draws={} keep={}".format(
                round(float(candidate.get("score") or 0), 3),
                probability_text,
                plan_focus.get("main_label") or "none",
                main_prob_text,
                int(diagnostics.get("kept_twos") or 0),
                int(diagnostics.get("t2_need_twos") or 0),
                int(diagnostics.get("redraws") or 0),
                diagnostics.get("t3_targets") or [],
                diagnostics.get("t3_access") if diagnostics.get("t3_access") is not None else "n/a",
                diagnostics.get("t3_draws") if diagnostics.get("t3_draws") is not None else "n/a",
                _cards_trace_label(kept),
            )
        )
    return lines


def _apply_live_success_smoothing(
    hand: list[dict[str, Any]],
    deck: list[dict[str, Any]],
    draw_index: int,
    live: dict[str, Any] | None,
    deck_cards: list[dict[str, Any]],
    future_alternatives_by_turn: list[list[list[int]]] | None = None,
    *,
    start_turn_index: int = 0,
) -> tuple[int, list[dict[str, Any]], dict[str, Any] | None]:
    if not live:
        return draw_index, [], None
    live_draw_n = int(live.get("live_success_draw_n") or live.get("draw_n") or 0)
    if live_draw_n <= 0:
        return draw_index, [], None
    draw_n = min(live_draw_n, max(0, len(deck) - draw_index))
    drawn: list[dict[str, Any]] = []
    for _ in range(draw_n):
        card = deck[draw_index]
        hand.append(card)
        drawn.append(card)
        draw_index += 1
    discarded = None
    if draw_n >= 2 and hand:
        discarded = _discard_after_effect_draw(
            hand,
            deck_cards,
            future_alternatives_by_turn,
            start_turn_index=start_turn_index,
        )
    return draw_index, drawn, discarded


def _has_energy_boost_live(cards: list[dict[str, Any]]) -> bool:
    return any(card.get("kind") == "live" and int(card.get("energy_boost_n") or 0) > 0 for card in cards)


def _has_low_cost_stage_summon(cards: list[dict[str, Any]]) -> bool:
    return any(card.get("kind") == "member" and int(card.get("low_cost_summon_n") or 0) > 0 for card in cards)


def _has_live_success_low_cost_summon(cards: list[dict[str, Any]]) -> bool:
    return any(int(card.get("live_success_low_cost_summon_n") or 0) > 0 for card in cards)


def _target_alternatives_for_turn(target_shape: list[int], deck_cards: list[dict[str, Any]]) -> list[list[int]]:
    alternatives = [list(target_shape)] if _shape_costs_available(target_shape, deck_cards) else []
    if target_shape == [2, 2] and _shape_costs_available([4], deck_cards):
        alternatives.append([4])
    curve_shapes = _energy_activate_curve_shape_set(deck_cards)
    if curve_shapes:
        normalized_target = sorted((int(value) for value in target_shape), reverse=True)
        if normalized_target == sorted(curve_shapes.get("t2", []), reverse=True):
            accel_single = [int(curve_shapes["accelerator_cost"])]
            if _shape_costs_available(accel_single, deck_cards):
                alternatives.append(accel_single)
        if normalized_target == sorted(curve_shapes.get("t3", []), reverse=True):
            for shape in (
                curve_shapes.get("t3_alt_high", []),
                curve_shapes.get("t3_alt_single", []),
            ):
                if shape and _shape_costs_available(list(shape), deck_cards):
                    alternatives.append(list(shape))
        if normalized_target == sorted(curve_shapes.get("t5", []), reverse=True):
            alt = curve_shapes.get("t5_alt", [])
            if alt and _shape_costs_available(list(alt), deck_cards):
                alternatives.append(list(alt))
    has_energy = _has_energy_boost_live(deck_cards)
    if target_shape == [2, 5, 2] and has_energy and _shape_costs_available([2, 4, 2], deck_cards):
        alternatives.append([2, 4, 2])
    if target_shape == [2, 15, 2]:
        alternatives = []
        for late_shape in ([15, 5, 2], [15, 4, 2], [15, 2, 2]):
            if _shape_costs_available(late_shape, deck_cards):
                alternatives.append(list(late_shape))
    if target_shape == [15]:
        if _has_live_success_low_cost_summon(deck_cards):
            for tempo_shape in ([15, 2], [17, 4]):
                if _shape_costs_available(tempo_shape, deck_cards):
                    alternatives.append(list(tempo_shape))
    if target_shape in ([2, 17, 9], [17, 9], [2, 15, 9], [15, 9]):
        for late_shape in ([2, 17, 9], [17, 9], [2, 15, 17], [2, 17, 17], [2, 15, 9], [15, 9], [13, 9, 4]):
            if _shape_costs_available(late_shape, deck_cards):
                alternatives.append(list(late_shape))
    if target_shape == [2, 10, 2]:
        for upside in ([2, 11, 2],):
            if _shape_costs_available(upside, deck_cards):
                alternatives.append(list(upside))
    if _has_low_cost_stage_summon(deck_cards):
        if target_shape == [7, 2] and _shape_costs_available([7, 2], deck_cards):
            alternatives.append([7, 2, 2])
        if target_shape == [13, 2] and _shape_costs_available([13, 2], deck_cards):
            alternatives.append([13, 2, 2])
    if target_shape == [13, 7, 2]:
        high_reduction_costs = sorted({
            int(card.get("cost") or 0)
            for card in deck_cards
            if card.get("kind") == "member"
            and bool(card.get("cost_reduction"))
            and int(card.get("cost") or 0) > 13
        }, reverse=True)
        for high in high_reduction_costs:
            upside = [13, high, 2]
            if _shape_costs_available(upside, deck_cards):
                alternatives.append(upside)
    return _unique_shapes(alternatives)


def _unique_shapes(shapes: list[list[int]]) -> list[list[int]]:
    out: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()
    for shape in shapes:
        normalized = tuple(sorted((int(value) for value in shape), reverse=True))
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(list(normalized))
    return out


def _has_member_recovery_route(deck_cards: list[dict[str, Any]]) -> bool:
    return any(
        int(card.get("member_recovery_n") or 0) > 0
        or int(card.get("live_success_member_recovery_n") or 0) > 0
        for card in deck_cards
    )


def _recovery_compromise_shapes(accepted_shapes: list[list[int]], deck_cards: list[dict[str, Any]]) -> list[list[int]]:
    if not _has_member_recovery_route(deck_cards):
        return []
    accepted_keys = {tuple(sorted((int(value) for value in shape), reverse=True)) for shape in accepted_shapes}
    candidates: list[list[int]] = []
    available_costs = _member_cost_counts(deck_cards)
    for shape in accepted_shapes:
        normalized = sorted((int(value) for value in shape), reverse=True)
        if len(normalized) < 3:
            continue
        low_indexes = [index for index, value in enumerate(normalized) if value <= 2]
        if low_indexes:
            for index in reversed(low_indexes):
                candidate = [value for pos, value in enumerate(normalized) if pos != index]
                if candidate:
                    candidates.append(candidate)
        if len(normalized) == 3 and normalized[-1] <= 2:
            high_mid = [normalized[0], normalized[1]]
            if high_mid:
                candidates.append(high_mid)
        if len(normalized) == 3 and 5 in normalized and available_costs.get(4, 0) > 0:
            candidate = [4 if value == 5 else value for value in normalized]
            candidates.append(candidate)
            low_indexes = [index for index, value in enumerate(candidate) if value <= 2]
            if low_indexes:
                candidates.append([value for pos, value in enumerate(candidate) if pos != low_indexes[-1]])
    return [
        shape for shape in _unique_shapes(candidates)
        if tuple(shape) not in accepted_keys and _shape_costs_available(shape, deck_cards)
    ]


def _planning_shapes_for_goal(goal_plan: dict[str, Any]) -> list[list[int]]:
    accepted = [list(shape) for shape in goal_plan.get("accepted_shapes", []) or [] if isinstance(shape, list)]
    recovery = [list(shape) for shape in goal_plan.get("recovery_shapes", []) or [] if isinstance(shape, list)]
    primary = list(goal_plan.get("primary_shape", []))
    return _unique_shapes(accepted + recovery + ([primary] if primary else []))


def _stage_goal_plans(base_turns: list[list[int]], deck_cards: list[dict[str, Any]], max_turns: int) -> list[dict[str, Any]]:
    seed_turns = _deck_dynamic_target_turns(base_turns, deck_cards, max_turns)
    plans: list[dict[str, Any]] = []
    for turn_index, seed_shape in enumerate(seed_turns, start=1):
        accepted_shapes = _target_alternatives_for_turn(seed_shape, deck_cards)
        if not accepted_shapes and seed_shape:
            accepted_shapes = [list(seed_shape)]
        primary_shape = list(accepted_shapes[0]) if accepted_shapes else list(seed_shape)
        recovery_shapes = _recovery_compromise_shapes(accepted_shapes, deck_cards)
        plans.append({
            "turn": turn_index,
            "seed_shape": list(seed_shape),
            "primary_shape": primary_shape,
            "accepted_shapes": [list(shape) for shape in accepted_shapes],
            "recovery_shapes": [list(shape) for shape in recovery_shapes],
            "planning_shapes": _unique_shapes([list(shape) for shape in accepted_shapes] + [list(shape) for shape in recovery_shapes]),
        })
    return plans


def _shape_costs_available(shape: list[int], deck_cards: list[dict[str, Any]]) -> bool:
    costs = Counter(
        int(card.get("cost") or 0)
        for card in deck_cards
        if card.get("kind") == "member" and card.get("cost") is not None
    )
    for cost, needed in Counter(int(value) for value in shape).items():
        if costs.get(cost, 0) < needed:
            return False
    return True


def _member_cost_counts(deck_cards: list[dict[str, Any]]) -> Counter[int]:
    return Counter(
        int(card.get("cost") or 0)
        for card in deck_cards
        if card.get("kind") == "member" and card.get("cost") is not None
    )


def _deck_dynamic_target_turns(base_turns: list[list[int]], deck_cards: list[dict[str, Any]], max_turns: int) -> list[list[int]]:
    costs = _member_cost_counts(deck_cards)
    target_turns: list[list[int]] = []
    for turn in base_turns[:max_turns]:
        if _shape_costs_available(turn, deck_cards):
            target_turns.append([int(value) for value in turn])
    while len(target_turns) < max_turns:
        if target_turns and sorted(target_turns[-1], reverse=True) == [13, 2] and _shape_costs_available([13, 7, 2], deck_cards):
            target_turns.append([13, 7, 2])
            continue
        target_turns.append(_late_target_shape_from_deck(costs, len(target_turns) + 1))
    return target_turns[:max_turns]


def _primary_high_anchor_cost(costs: Counter[int]) -> int:
    high_counts = {int(cost): int(count) for cost, count in costs.items() if int(cost) >= 15 and int(count) > 0}
    if not high_counts:
        available = sorted((int(cost) for cost, count in costs.items() if int(count) > 0), reverse=True)
        return available[0] if available else 0
    return max(high_counts, key=lambda cost: (high_counts[cost], cost))


def _late_target_shape_from_deck(costs: Counter[int], turn_number: int) -> list[int]:
    available = sorted((cost for cost, count in costs.items() if count > 0), reverse=True)
    if not available:
        return []
    high = _primary_high_anchor_cost(costs) or next((cost for cost in available if cost >= 15), available[0])
    low_count = costs.get(2, 0)
    if turn_number >= 4 and high >= 15 and costs.get(9, 0) >= 3:
        if low_count >= 8:
            return [2, high, 9]
        return [high, 9]
    if turn_number >= 4 and low_count >= 2 and high >= 15:
        return [2, high, 2]
    return [high]


def _shape_goal_cards(shape: list[int], deck_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    goals: list[dict[str, Any]] = []
    used_ids: set[int] = set()
    for cost in sorted([int(value) for value in shape], reverse=True):
        candidates = [
            card for card in deck_cards
            if card.get("kind") == "member"
            and int(card.get("cost") or 0) == cost
            and int(card.get("id") or 0) not in used_ids
        ]
        if not candidates:
            continue
        card = sorted(candidates, key=lambda item: (str(item.get("card_no") or ""), str(item.get("name") or "")))[0]
        used_ids.add(int(card.get("id") or 0))
        goals.append({
            "cost": cost,
            "card_no": card.get("card_no"),
            "name": card.get("name"),
            "route": _goal_route_text(card, deck_cards),
        })
    return goals


def _goal_route_text(card: dict[str, Any], deck_cards: list[dict[str, Any]]) -> str:
    cost = int(card.get("cost") or 0)
    parts = ["手札から通常登場"]
    if int(card.get("energy_activate_n") or 0) > 0:
        parts.append("エネルギーアクティブ化で後続到達を補助")
    if cost >= 15 and bool(card.get("cost_reduction")):
        parts.append("自身のコスト軽減で到達候補")
    if int(card.get("low_cost_summon_n") or 0) > 0:
        parts.append("登場時に追加2コスト登場候補")
    return " / ".join(parts)


def _stage_goal_summary(stage_goal_plans: list[dict[str, Any]], deck_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "turn": int(plan.get("turn") or index),
            "alternatives": [
                {
                    "shape": list(shape),
                    "cards": _shape_goal_cards(shape, deck_cards),
                }
                for shape in plan.get("accepted_shapes", []) or []
                if isinstance(shape, list)
            ],
            "recovery_alternatives": [
                {
                    "shape": list(shape),
                    "cards": _shape_goal_cards(shape, deck_cards),
                    "route": "回収・ドロー・エネルギー加速で次ターン以降の復帰を狙う妥協進行",
                }
                for shape in plan.get("recovery_shapes", []) or []
                if isinstance(shape, list)
            ],
        }
        for index, plan in enumerate(stage_goal_plans, start=1)
    ]


def _live_cards(deck_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [card for card in deck_cards if card.get("kind") == "live"]


def _live_score_targets(deck_cards: list[dict[str, Any]], max_turns: int) -> list[dict[str, Any]]:
    lives = _live_cards(deck_cards)
    by_score: dict[int, list[dict[str, Any]]] = {}
    for live in lives:
        score = int(live.get("score") or 0)
        by_score.setdefault(score, [])
        if len(by_score[score]) < 4:
            by_score[score].append(live)
    scores = sorted(by_score)
    positive_scores = [score for score in scores if score > 0]
    target_scores = positive_scores or scores
    if not scores:
        return []
    targets: list[dict[str, Any]] = []
    for turn in range(1, max_turns + 1):
        if turn <= 1:
            preferred = target_scores[0]
        elif turn == 2:
            preferred = target_scores[min(1, len(target_scores) - 1)]
        else:
            preferred = target_scores[-1]
        examples = by_score.get(preferred, [])
        targets.append({
            "turn": turn,
            "target_score": preferred,
            "accepted_scores": [score for score in scores if score >= preferred],
            "cards": [
                {
                    "card_no": card.get("card_no"),
                    "name": card.get("name"),
                    "score": card.get("score"),
                }
                for card in examples
            ],
        })
    return targets


def _best_live_score_card(cards: list[dict[str, Any]]) -> dict[str, Any] | None:
    lives = [card for card in cards if card.get("kind") == "live" and card.get("score") is not None]
    if not lives:
        return None
    return max(lives, key=lambda card: (int(card.get("score") or 0), int(card.get("draw_n") or 0), str(card.get("card_no") or "")))


def _best_live_for_score_target(
    hand: list[dict[str, Any]],
    live_score_target: dict[str, Any] | None,
    *,
    protect_energy_boost: bool,
) -> dict[str, Any] | None:
    if not live_score_target:
        return None
    accepted_scores = {
        int(score)
        for score in live_score_target.get("accepted_scores", []) or []
    }
    if not accepted_scores:
        return None
    candidates = [
        card for card in hand
        if card.get("kind") == "live"
        and card.get("score") is not None
        and int(card.get("score") or 0) in accepted_scores
        and not (protect_energy_boost and int(card.get("energy_boost_n") or 0) > 0)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda card: (int(card.get("score") or 0), int(card.get("draw_n") or 0), str(card.get("card_no") or "")))


def build_autoplay_policy_context(
    rows: list[dict[str, str]],
    card_lookup: CardLookup,
    *,
    max_turns: int = 4,
) -> dict[str, Any]:
    report = build_autoplay_deck_report(rows, card_lookup)
    progressions = [item for item in report.get("progressions", []) if isinstance(item, dict)]
    early = [item for item in progressions if item.get("phase") != "late" and item.get("phase") != "late_special"]
    late = [item for item in progressions if item.get("phase") in {"late", "late_special"}]
    recommended_early = early[0] if early else (progressions[0] if progressions else {})
    recommended_late = late[0] if late else {}
    base_turns = [list(turn) for turn in recommended_early.get("turns", [])]
    deck_cards = _expanded_card_objects(rows, card_lookup)
    stage_goal_plans = _stage_goal_plans(base_turns, deck_cards, max_turns)
    target_alternatives = [list(plan.get("accepted_shapes", [])) for plan in stage_goal_plans]
    planning_alternatives = [_planning_shapes_for_goal(plan) for plan in stage_goal_plans]
    return {
        "report": report,
        "recommended_early": recommended_early,
        "recommended_late": recommended_late,
        "deck_cards": deck_cards,
        "stage_goal_plans": stage_goal_plans,
        "target_turns": [list(plan.get("primary_shape", [])) for plan in stage_goal_plans],
        "target_alternatives": target_alternatives,
        "planning_alternatives": planning_alternatives,
        "target_goal_summary": _stage_goal_summary(stage_goal_plans, deck_cards),
        "live_score_targets": _live_score_targets(deck_cards, max_turns),
    }


def _state_cardnumber(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("card_no", "cardnumber", "cn", "cardNumber", "id"):
            got = str(value.get(key) or "").strip()
            if got and not got.startswith("inst_"):
                return got
    return str(getattr(value, "cardnumber", "") or getattr(value, "card_no", "") or "").strip()


def _state_indexed_cards(values: Any, card_lookup: CardLookup) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, value in enumerate(list(values or [])):
        card_no = _state_cardnumber(value)
        if not card_no:
            continue
        card = _card_object_from_number(card_no, card_lookup, seq=index)
        card["state_index"] = index
        cards.append(card)
    return cards


def _state_stage_cards(state: dict[str, Any], card_lookup: CardLookup) -> list[dict[str, Any] | None]:
    raw_stage = state.get("stage") or {}
    values: list[Any]
    if isinstance(raw_stage, dict):
        values = [raw_stage.get(pos) for pos in ("L", "C", "R")]
    elif isinstance(raw_stage, list):
        values = list(raw_stage[:3])
    else:
        values = []
    while len(values) < 3:
        values.append(None)
    stage: list[dict[str, Any] | None] = []
    for index, value in enumerate(values[:3]):
        card_no = _state_cardnumber(value)
        if not card_no:
            stage.append(None)
            continue
        card = _card_object_from_number(card_no, card_lookup, seq=1000 + index)
        card["stage_index"] = index
        stage.append(card)
    return stage


def _cpu_turn_index(state: dict[str, Any], max_turns: int) -> int:
    raw_turn = _first_int(state.get("turn"))
    turn = int(raw_turn or 1)
    return max(0, min(max_turns - 1, turn - 1))


def _list_count(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return len([item for item in value.values() if item])
    try:
        return max(0, int(value or 0))
    except Exception:
        return 0


def _opponent_public_context(state: dict[str, Any]) -> dict[str, Any]:
    own_success = _list_count(state.get("success"))
    if not own_success:
        own_success = _list_count(state.get("success_count"))
    opponent_success = _list_count(state.get("opponent_success_count"))
    opponent_wait = _list_count(state.get("opponent_wait_count"))
    known_hand = _list_count(state.get("opponent_public_hand")) + _list_count(state.get("opponent_revealed_hand"))
    pressure = "even"
    if opponent_success > own_success:
        pressure = "behind"
    elif own_success > opponent_success:
        pressure = "ahead"
    tempo = "normal"
    if opponent_wait >= 2:
        tempo = "opponent_slow"
    elif opponent_wait <= 0 and pressure != "ahead":
        tempo = "opponent_ready"
    return {
        "own_success": own_success,
        "opponent_success": opponent_success,
        "opponent_finale": opponent_success >= 2,
        "opponent_wait": opponent_wait,
        "known_opponent_hand": known_hand,
        "pressure": pressure,
        "tempo": tempo,
    }


def _adjust_live_target_for_public_pressure(
    live_target: dict[str, Any] | None,
    hand: list[dict[str, Any]],
    public_context: dict[str, Any],
) -> dict[str, Any] | None:
    if not isinstance(live_target, dict):
        return live_target
    lives = [card for card in hand if card.get("kind") == "live" and card.get("score") is not None]
    if not lives:
        return live_target
    out = dict(live_target)
    scores = sorted({int(card.get("score") or 0) for card in lives if int(card.get("score") or 0) > 0})
    if not scores:
        return out
    if public_context.get("opponent_finale"):
        preferred = scores[-1]
        out["target_score"] = max(int(out.get("target_score") or 0), preferred)
        out["accepted_scores"] = [score for score in scores if score >= int(out["target_score"])]
        out["score_priority_mode"] = "finale_pressure"
        out["public_pressure_adjustment"] = "相手が千秋楽のため、手札内で狙える高スコアライブを優先"
    elif public_context.get("pressure") == "behind" or public_context.get("tempo") == "opponent_ready":
        out["public_pressure_adjustment"] = "相手は先行/動けそうだが千秋楽ではないため、進行を崩さずステージ目標を優先"
    elif public_context.get("pressure") == "ahead" and public_context.get("tempo") == "opponent_slow":
        out["public_pressure_adjustment"] = "こちらが先行し相手が遅れているため、ステージ進行と手札整備を優先"
    return out


def _pending_options(pending: dict[str, Any]) -> list[str]:
    for key in ("choices", "options", "items"):
        values = pending.get(key)
        if isinstance(values, list) and values:
            out: list[str] = []
            for value in values:
                if isinstance(value, dict):
                    for choice_key in ("value", "choice", "id", "key", "label", "text"):
                        got = str(value.get(choice_key) or "").strip()
                        if got:
                            out.append(got)
                            break
                    continue
                got = str(value).strip()
                if got:
                    out.append(got)
            if out:
                return out
    return []


def _pending_display_cards(pending: dict[str, Any]) -> list[str]:
    for key in ("display_cards", "cards", "candidates"):
        values = pending.get(key)
        if not isinstance(values, list):
            continue
        out: list[str] = []
        for value in values:
            if isinstance(value, dict):
                got = str(value.get("card_no") or value.get("cardnumber") or value.get("id") or "").strip()
            else:
                got = str(value or "").strip()
            if got:
                out.append(got)
        if out:
            return out
    return []


def _pending_choice_decision(pending: dict[str, Any]) -> dict[str, Any]:
    options = _pending_options(pending)
    kind = str(pending.get("kind") or "").casefold()
    action = str(pending.get("action") or "").casefold()
    message = str(pending.get("message") or pending.get("title") or "").casefold()
    context = " ".join([kind, action, message])
    low_options = [option.casefold() for option in options]

    def choose(value: str, confidence: str, reason: str) -> dict[str, Any]:
        return {
            "choice": value,
            "confidence": confidence,
            "reason": reason,
        }

    if len(options) == 1:
        return choose(options[0], "high", "単一選択肢のpendingを確定")

    display_cards = _pending_display_cards(pending)
    if "dual_opponent_topk_reorder_keep_any" in kind and display_cards:
        return {
            "choice": ",".join(display_cards),
            "confidence": "medium",
            "reason": "山札上複数枚確認は、未知評価では全カードを元順で保持して不用意な控え室送りを避ける",
            "selected_cards": [{"card_no": card_no, "name": card_no} for card_no in display_cards],
        }

    if "opponent" in low_options and any(token in context for token in ("opponent", "相手")):
        return choose("opponent", "medium", "相手領域に関わるpendingなのでopponent側を選択")
    if "相手" in options and any(token in context for token in ("opponent", "相手")):
        return choose("相手", "medium", "相手領域に関わるpendingなので相手側を選択")

    for positive in ("apply", "opponent_discard", "threshold_met", "green", "ok", "あなた"):
        if positive.casefold() in low_options:
            actual = options[low_options.index(positive.casefold())]
            confidence = "medium" if positive in {"apply", "ok", "green"} else "low"
            return choose(actual, confidence, f"`{actual}` をCPU既定の実行側選択として採用")

    for neutral in ("keep", "skip", "__skip__", "no", "not_discard"):
        if neutral.casefold() in low_options:
            actual = options[low_options.index(neutral.casefold())]
            return choose(actual, "low", f"効果価値を評価できないため `{actual}` を安全側の既定選択として採用")

    if options:
        return choose(options[0], "low", "未分類pendingは先頭選択肢を返す")

    if "optional" in kind or "skip" in kind:
        return choose("skip", "low", "選択肢なしの任意pendingはskipを返す")
    return choose("ok", "low", "選択肢なしの確認pendingはokを返す")


def _pending_default_choice(pending: dict[str, Any]) -> str:
    return str(_pending_choice_decision(pending).get("choice") or "ok")


def _pending_choice_trace(pending: dict[str, Any]) -> dict[str, Any]:
    decision = _pending_choice_decision(pending)
    options = _pending_options(pending)
    out = {
        "choice": decision.get("choice", "ok"),
        "confidence": decision.get("confidence", "low"),
        "reason": decision.get("reason", "pending既定選択"),
        "options": options,
        "pending_kind": str(pending.get("kind") or ""),
    }
    if isinstance(decision.get("selected_cards"), list):
        out["selected_cards"] = decision["selected_cards"]
    return out


def _cpu_pending_action(state: dict[str, Any]) -> dict[str, Any] | None:
    pending_items = state.get("pending")
    if not isinstance(pending_items, list) or not pending_items:
        return None
    first = pending_items[0] if isinstance(pending_items[0], dict) else {"value": pending_items[0]}
    trace = _pending_choice_trace(first)
    choice = trace["choice"]
    selected_cards = trace.get("selected_cards")
    return {
        "kind": "pending",
        "command": "resolve_pending",
        "payload": {"idx": 0, "choice": choice},
        "confidence": trace["confidence"],
        "reason": trace["reason"],
        "pending_kind": trace["pending_kind"],
        "options": trace["options"],
        **({"selected_cards": selected_cards} if isinstance(selected_cards, list) else {}),
    }


def _cpu_main_action(
    state: dict[str, Any],
    card_lookup: CardLookup,
    goal_plan: dict[str, Any],
) -> dict[str, Any] | None:
    hand = _state_indexed_cards(state.get("hand"), card_lookup)
    stage = _state_stage_cards(state, card_lookup)
    alternatives = list(goal_plan.get("accepted_shapes", [])) or [list(goal_plan.get("primary_shape", []))]
    primary_shape = list(goal_plan.get("primary_shape", []))
    planning_alternatives = [primary_shape] if primary_shape else alternatives
    best_shape = _best_target_shape_for_stage(stage, planning_alternatives)
    if not best_shape:
        return None
    best_score = _stage_score(stage, best_shape)
    try:
        active_energy = int(state.get("energy_active", 0) or 0)
    except Exception:
        active_energy = 0
    slot_names = ["L", "C", "R"]
    candidates: list[tuple[int, int, int, int, dict[str, Any], int]] = []
    for slot in _stage_slots_to_replace(stage, best_shape):
        if _slot_satisfies_nonreplaceable_target(stage, slot, best_shape):
            continue
        old_card = stage[slot] if slot < len(stage) else None
        for card in hand:
            if card.get("kind") != "member" or card.get("cost") is None:
                continue
            cost = int(card.get("cost") or 0)
            pay_cost = _member_play_cost_for_slot(card, old_card, stage)
            if pay_cost > active_energy:
                continue
            trial_stage = list(stage)
            trial_stage[slot] = card
            score = _stage_score(trial_stage, best_shape)
            gain = score - best_score
            if gain > 0:
                candidates.append((gain, -pay_cost, cost, -slot, card, slot))
    if not candidates:
        return None
    gain, neg_pay_cost, _cost, _slot_sort, card, slot = max(candidates, key=lambda item: (item[0], item[1], item[2], item[3]))
    pay_cost = -neg_pay_cost
    return {
        "kind": "main_play",
        "command": "play",
        "payload": {"hand_idx": int(card.get("state_index", 0)), "pos": slot_names[slot]},
        "confidence": "medium",
            "reason": "primary target {} に対するstage score gain +{}（active energy {} / pay {} で実行可能、代替達成より本命進行を優先）".format(
            "-".join(str(v) for v in best_shape),
            gain,
            active_energy,
            pay_cost,
        ),
        "card": {"card_no": card.get("card_no"), "name": card.get("name"), "cost": card.get("cost")},
    }


def _cpu_main_completion_action(
    state: dict[str, Any],
    card_lookup: CardLookup,
    goal_plan: dict[str, Any],
) -> dict[str, Any]:
    stage = _state_stage_cards(state, card_lookup)
    costs = _stage_costs(stage)
    alternatives = list(goal_plan.get("accepted_shapes", [])) or [list(goal_plan.get("primary_shape", []))]
    recovery_alternatives = [list(shape) for shape in goal_plan.get("recovery_shapes", []) or [] if isinstance(shape, list)]
    planning_alternatives = _planning_shapes_for_goal(goal_plan)
    best_shape = _best_target_shape_for_stage(stage, alternatives)
    matched_shape = next((shape for shape in alternatives if _shape_meets_target(costs, shape)), [])
    if matched_shape:
        return {
            "kind": "main_complete",
            "command": "NEXT",
            "payload": {},
            "confidence": "high",
            "reason": "MAIN目標達成済み: stage {} meets accepted target {}".format(
                _stage_text(stage),
                "-".join(str(v) for v in matched_shape),
            ),
            "stage_costs": costs,
            "target_shape": matched_shape,
        }
    recovery_shape = next((shape for shape in recovery_alternatives if _shape_meets_target(costs, shape)), [])
    if recovery_shape:
        return {
            "kind": "main_recovery_complete",
            "command": "NEXT",
            "payload": {},
            "confidence": "medium",
            "reason": "MAIN通常目標は未達だが復帰可能形: stage {} meets recovery target {} / accepted miss {}".format(
                _stage_text(stage),
                "-".join(str(v) for v in recovery_shape),
                _miss_reason(costs, alternatives),
            ),
            "stage_costs": costs,
            "target_shape": recovery_shape,
        }
    return {
        "kind": "main_pass",
        "command": "NEXT",
        "payload": {},
        "confidence": "low",
        "reason": "MAIN追加登場で改善できる候補なし: stage {} / best target {} / {}".format(
            _stage_text(stage),
            "-".join(str(v) for v in (best_shape or _best_target_shape_for_stage(stage, planning_alternatives))) if (best_shape or planning_alternatives) else "none",
            _miss_reason(costs, alternatives),
        ),
        "stage_costs": costs,
        "target_shape": best_shape,
    }


def suggest_autoplay_action(
    rows: list[dict[str, str]],
    card_lookup: CardLookup,
    state: dict[str, Any],
    *,
    max_turns: int = 4,
) -> dict[str, Any]:
    context = build_autoplay_policy_context(rows, card_lookup, max_turns=max_turns)
    turn_index = _cpu_turn_index(state, max_turns)
    goal_plan = context["stage_goal_plans"][turn_index] if turn_index < len(context["stage_goal_plans"]) else {}
    phase = str(state.get("phase") or "").upper()
    public_context = _opponent_public_context(state)
    pending_action = _cpu_pending_action(state)
    if pending_action is not None:
        pending_action["turn"] = turn_index + 1
        pending_action["phase"] = phase
        return pending_action
    if "MULLIGAN" in phase:
        hand = _state_indexed_cards(state.get("hand"), card_lookup)
        stage = _state_stage_cards(state, card_lookup)
        mulligan_targets = [
            alternative
            for alternatives in context["target_alternatives"][:3]
            for alternative in alternatives
        ]
        plan = _choose_mulligan_plan(hand, mulligan_targets, context["deck_cards"], context["target_alternatives"][:3])
        keep = list(plan.get("keep") or [])
        keep_indices = {int(card.get("state_index", -1)) for card in keep}
        indices = [int(card.get("state_index", 0)) for card in hand if int(card.get("state_index", 0)) not in keep_indices]
        return {
            "kind": "mulligan",
            "command": "NEXT",
            "payload": {"indices": indices},
            "turn": turn_index + 1,
            "phase": phase,
            "confidence": "medium",
            "reason": "T1-T3 accepted targetsの確率曲線を比較して戻す: score={} p={}".format(
                round(float(plan.get("score") or 0), 3),
                "/".join(str(round(float(value), 3)) for value in (plan.get("probabilities") or [])),
            ),
            "mulligan_keep": [
                {"card_no": card.get("card_no"), "name": card.get("name"), "kind": card.get("kind"), "cost": card.get("cost"), "score": card.get("score")}
                for card in keep
            ],
        }
    if "LIVE_SET" in phase:
        hand = _state_indexed_cards(state.get("hand"), card_lookup)
        stage = _state_stage_cards(state, card_lookup)
        alternatives = list(goal_plan.get("accepted_shapes", [])) or [list(goal_plan.get("primary_shape", []))]
        recovery_alternatives = [list(shape) for shape in goal_plan.get("recovery_shapes", []) or [] if isinstance(shape, list)]
        future_targets = [
            alternative
            for future_alternatives in context["target_alternatives"][turn_index: min(len(context["target_alternatives"]), turn_index + 3)]
            for alternative in future_alternatives
        ]
        future_alternatives_by_turn = context["target_alternatives"][turn_index: min(len(context["target_alternatives"]), turn_index + 3)]
        energy_state_for_bridge = {
            "active": int(state.get("energy_active", 0) or 0),
            "wait": int(state.get("energy_wait", 0) or 0),
            "deck_remaining": int(state.get("energy_deck_remaining", state.get("energy_deck_count", 1)) or 1),
        }
        energy_bridge_plan = _energy_bridge_plan_for_next_turn(
            stage,
            future_alternatives_by_turn,
            energy_state_for_bridge,
            hand,
        )
        prefer_energy_boost = any(alternative == [2, 4, 2] for alternative in alternatives) or bool(energy_bridge_plan.get("needed"))
        live_target = context["live_score_targets"][turn_index] if turn_index < len(context["live_score_targets"]) else {}
        live_target = _adjust_live_target_for_public_pressure(
            live_target if isinstance(live_target, dict) else None,
            hand,
            public_context,
        ) or {}
        live_for_success, selected = _choose_live_set_cards(
            hand,
            prefer_energy_boost,
            future_targets,
            context["deck_cards"],
            live_target if isinstance(live_target, dict) else None,
            future_alternatives_by_turn,
            turn_index,
            stage,
            recovery_alternatives,
        )
        indices = [int(card.get("state_index", 0)) for card in selected]
        target_score = None
        accepted_scores: list[int] = []
        if isinstance(live_target, dict):
            target_score = live_target.get("target_score")
            accepted_scores = [int(score) for score in live_target.get("accepted_scores", []) or []]
        live_score = int(live_for_success.get("score") or 0) if live_for_success is not None and live_for_success.get("score") is not None else None
        reason_parts = ["手札交換・ライブスコア目標・エネルギーブースト温存を同時評価"]
        if target_score is not None:
            reason_parts.append(f"live target {target_score}+")
        if live_for_success is not None:
            reason_parts.append("selected live {} score {}".format(live_for_success.get("card_no"), live_score if live_score is not None else "none"))
        if prefer_energy_boost:
            reason_parts.append(
                "energy bridge候補ターン next={} need={} base={} boost={}".format(
                    energy_bridge_plan.get("next_target") or "?",
                    energy_bridge_plan.get("min_required"),
                    energy_bridge_plan.get("base_active_next"),
                    energy_bridge_plan.get("boosted_active_next"),
                )
            )
        if isinstance(live_target, dict) and live_target.get("public_pressure_adjustment"):
            reason_parts.append(str(live_target.get("public_pressure_adjustment")))
        confidence = "medium"
        if live_score is not None and accepted_scores and live_score in set(accepted_scores):
            confidence = "high"
        return {
            "kind": "live_set",
            "command": "NEXT",
            "payload": {"indices": indices},
            "turn": turn_index + 1,
            "phase": phase,
            "confidence": confidence,
            "reason": " / ".join(reason_parts),
            "public_context": public_context,
            "live_target": {
                "target_score": target_score,
                "accepted_scores": accepted_scores,
                "score_priority_mode": live_target.get("score_priority_mode") if isinstance(live_target, dict) else None,
            },
            "recovery_rescue_mode": bool(
                recovery_alternatives
                and not any(_shape_meets_target(_stage_costs(stage), shape) for shape in alternatives)
                and any(_shape_meets_target(_stage_costs(stage), shape) for shape in recovery_alternatives)
            ),
            "energy_bridge_plan": energy_bridge_plan,
            "live_for_success": (
                {
                    "card_no": live_for_success.get("card_no"),
                    "name": live_for_success.get("name"),
                    "kind": live_for_success.get("kind"),
                    "score": live_for_success.get("score"),
                    "cost": live_for_success.get("cost"),
                }
                if live_for_success is not None else None
            ),
            "selected_cards": [
                {"card_no": card.get("card_no"), "name": card.get("name"), "kind": card.get("kind"), "score": card.get("score"), "cost": card.get("cost")}
                for card in selected
            ],
        }
    if "MAIN" in phase:
        action = _cpu_main_action(state, card_lookup, goal_plan)
        if action is not None:
            action["turn"] = turn_index + 1
            action["phase"] = phase
            return action
        action = _cpu_main_completion_action(state, card_lookup, goal_plan)
        action["turn"] = turn_index + 1
        action["phase"] = phase
        return action
    return {
        "kind": "next",
        "command": "NEXT",
        "payload": {},
        "turn": turn_index + 1,
        "phase": phase,
        "confidence": "low",
        "reason": "このフェイズで具体操作候補がないため中央Nextを提案",
    }


def simulate_autoplay_trials(
    rows: list[dict[str, str]],
    card_lookup: CardLookup,
    *,
    trials: int = 200,
    seed: int = 1,
    max_turns: int = 4,
    trace_trials: int = 0,
) -> dict[str, Any]:
    context = build_autoplay_policy_context(rows, card_lookup, max_turns=max_turns)
    recommended_early = context["recommended_early"]
    recommended_late = context["recommended_late"]
    deck_cards = context["deck_cards"]
    stage_goal_plans = context["stage_goal_plans"]
    target_turns = context["target_turns"]
    target_alternatives = context["target_alternatives"]
    planning_alternatives = context["planning_alternatives"]
    target_goal_summary = context["target_goal_summary"]
    live_score_targets = context["live_score_targets"]
    rng = random.Random(seed)
    turn_hits = [0 for _ in range(max_turns)]
    cumulative_hits = [0 for _ in range(max_turns)]
    recovery_hits = [0 for _ in range(max_turns)]
    recovery_cumulative_hits = [0 for _ in range(max_turns)]
    live_score_hits = [0 for _ in range(max_turns)]
    live_score_cumulative_hits = [0 for _ in range(max_turns)]
    combined_cumulative_hits = [0 for _ in range(max_turns)]
    total_values = [0 for _ in range(max_turns)]
    exact_shape_counts: Counter[str] = Counter()
    miss_reasons: list[Counter[str]] = [Counter() for _ in range(max_turns)]
    sample_lines: list[str] = []
    decision_traces: list[dict[str, Any]] = []
    for trial in range(trials):
        deck = list(deck_cards)
        rng.shuffle(deck)
        initial_hand = deck[:6]
        trace_enabled = trial < max(0, int(trace_trials or 0))
        trace: dict[str, Any] | None = None
        if trace_enabled:
            trace = {
                "trial": trial + 1,
                "initial_hand": [_card_trace_label(card) for card in initial_hand],
                "turns": [],
            }
        draw_index = 6
        mulligan_targets = [
            alternative
            for alternatives in target_alternatives[:3]
            for alternative in alternatives
        ]
        mulligan_plan = _choose_mulligan_plan(initial_hand, mulligan_targets, deck_cards, target_alternatives[:3])
        kept = list(mulligan_plan.get("keep") or [])
        mulliganed = [card for card in initial_hand if card not in kept]
        if trace is not None:
            plan_focus = mulligan_plan.get("plan_focus", {}) if isinstance(mulligan_plan.get("plan_focus"), dict) else {}
            trace["mulligan"] = {
                "targets": _alternatives_trace_label(mulligan_targets),
                "main_plan": plan_focus.get("main_label") or "none",
                "main_plan_initial_probabilities": [
                    round(float(value), 3)
                    for value in (plan_focus.get("main_initial_probabilities") or [])
                ] if isinstance(plan_focus.get("main_initial_probabilities"), list) else [],
                "sub_plan": plan_focus.get("sub_label") or "none",
                "sub_plan_initial_probabilities": [
                    round(float(value), 3)
                    for value in (plan_focus.get("sub_initial_probabilities") or [])
                ] if isinstance(plan_focus.get("sub_initial_probabilities"), list) else [],
                "kept": [_card_trace_label(card) for card in kept],
                "returned": [_card_trace_label(card) for card in mulliganed],
                "top_need_scores": _need_score_trace(initial_hand, target_alternatives[:3], deck_cards),
                "score": round(float(mulligan_plan.get("score") or 0), 3),
                "probabilities": [round(float(value), 3) for value in (mulligan_plan.get("probabilities") or [])],
                "draw_windows": list(mulligan_plan.get("draw_windows") or []),
                "critical_focus": mulligan_plan.get("critical_focus", {}),
                "top_candidates": _mulligan_candidate_trace(mulligan_plan.get("candidates", []) if isinstance(mulligan_plan.get("candidates"), list) else []),
            }
        deck_tail = deck[6:] + mulliganed
        deck = initial_hand + deck_tail
        hand = list(kept)
        redrawn_cards: list[dict[str, Any]] = []
        while len(hand) < 6 and draw_index < len(deck):
            redrawn = deck[draw_index]
            hand.append(redrawn)
            redrawn_cards.append(redrawn)
            draw_index += 1
        if trace is not None:
            trace["mulligan"]["redrawn"] = [_card_trace_label(card) for card in redrawn_cards]
            trace["mulligan"]["post_mulligan_hand"] = [_card_trace_label(card) for card in hand]
            post_plan_focus = _choose_early_progression_plans(hand, deck_cards, target_alternatives[:3])
            trace["mulligan"]["post_main_plan"] = post_plan_focus.get("main_label") or "none"
            trace["mulligan"]["post_sub_plan"] = post_plan_focus.get("sub_label") or "none"
        energy_state = {"active": 3, "wait": 0, "deck_remaining": 9}
        stage: list[dict[str, Any] | None] = [None, None, None]
        green: list[dict[str, Any]] = []
        trial_shapes: list[str] = []
        prefix_success = True
        recovery_prefix_success = True
        live_score_prefix_success = True
        combined_prefix_success = True
        for turn_index, goal_plan in enumerate(stage_goal_plans):
            target_shape = list(goal_plan.get("primary_shape", []))
            turn_trace: dict[str, Any] | None = None
            if trace is not None and turn_index < 3:
                turn_trace = {
                    "turn": turn_index + 1,
                    "target": _shape_trace_label(target_shape),
                    "accepted": _alternatives_trace_label(list(goal_plan.get("accepted_shapes", [])) or [target_shape]),
                    "recovery": _alternatives_trace_label(list(goal_plan.get("recovery_shapes", []))),
                    "start_stage": _stage_text(stage),
                    "start_hand": [_card_trace_label(card) for card in hand],
                    "start_energy": dict(energy_state),
                }
            if energy_state["wait"] > 0:
                energy_state["active"] += energy_state["wait"]
                energy_state["wait"] = 0
            if energy_state["deck_remaining"] > 0:
                energy_state["active"] += 1
                energy_state["deck_remaining"] -= 1
            if draw_index < len(deck):
                drawn_card = deck[draw_index]
                hand.append(drawn_card)
                draw_index += 1
                if turn_trace is not None:
                    turn_trace["normal_draw"] = _card_trace_label(drawn_card)
            elif turn_trace is not None:
                turn_trace["normal_draw"] = "none"
            alternatives = list(goal_plan.get("accepted_shapes", [])) or [target_shape]
            recovery_alternatives = [list(shape) for shape in goal_plan.get("recovery_shapes", []) or [] if isinstance(shape, list)]
            planning_shapes = _planning_shapes_for_goal(goal_plan)
            future_targets = [
                alternative
                for future_alternatives in target_alternatives[turn_index: min(len(target_alternatives), turn_index + 3)]
                for alternative in future_alternatives
            ]
            future_alternatives_by_turn = target_alternatives[turn_index: min(len(target_alternatives), turn_index + 3)]
            prefer_energy_boost = any(alternative == [2, 4, 2] for alternative in alternatives)
            live_target = live_score_targets[turn_index] if turn_index < len(live_score_targets) else {}
            activation_support = _apply_stage_energy_activation_support(
                stage,
                hand,
                deck_cards,
                alternatives,
                energy_state,
                future_alternatives_by_turn,
                start_turn_index=turn_index,
            )
            before_stage = list(stage)
            before_main_hand = list(hand)
            before_main_energy = dict(energy_state)
            primary_planning = [target_shape] if target_shape else planning_shapes
            stage = _improve_persistent_stage(
                stage,
                hand,
                alternatives,
                energy_state,
                planning_alternatives=primary_planning,
            )
            entered_cards = [card for card in stage if card and card not in before_stage]
            draw_index, enter_topdeck_effects = _apply_enter_topdeck_effects(
                entered_cards,
                stage,
                hand,
                deck,
                draw_index,
                green,
                deck_cards,
                future_alternatives_by_turn,
                start_turn_index=turn_index,
            )
            recovery_support = _apply_stage_recovery_support(
                stage,
                hand,
                green,
                deck_cards,
                alternatives,
                energy_state,
                future_alternatives_by_turn,
                planning_alternatives=primary_planning,
                start_turn_index=turn_index,
            )
            if turn_trace is not None:
                played = [card for card in stage if card and card not in before_stage]
                removed = [card for card in before_stage if card and card not in stage]
                turn_trace["main"] = {
                    "before_stage": _stage_text(before_stage),
                    "after_stage": _stage_text(stage),
                    "played_or_replaced_in": [_card_trace_label(card) for card in played],
                    "replaced_out": [_card_trace_label(card) for card in removed],
                    "activation_support": {
                        "activated": [_card_trace_label(card) for card in activation_support.get("activated", [])],
                        "discarded": [_card_trace_label(card) for card in activation_support.get("discarded", [])],
                        "energy_before": activation_support.get("energy_before"),
                        "energy_after": activation_support.get("energy_after"),
                    },
                    "enter_topdeck_effects": enter_topdeck_effects,
                    "recovery_support": recovery_support,
                    "energy_before": before_main_energy,
                    "energy_after": dict(energy_state),
                    "remaining_hand_top_need": _need_score_trace(before_main_hand, future_alternatives_by_turn, deck_cards),
                }
            before_live_hand = list(hand)
            stage_costs_before_live = _stage_costs(stage)
            energy_bridge_plan = _energy_bridge_plan_for_next_turn(
                stage,
                future_alternatives_by_turn,
                energy_state,
                hand,
            )
            prefer_energy_boost = prefer_energy_boost or bool(energy_bridge_plan.get("needed"))
            recovery_rescue_mode = bool(
                recovery_alternatives
                and not any(_shape_meets_target(stage_costs_before_live, shape) for shape in alternatives)
                and any(_shape_meets_target(stage_costs_before_live, shape) for shape in recovery_alternatives)
            )
            live_set_card, draw_index, _live_set_cards = _live_set_exchange(
                hand,
                deck,
                draw_index,
                prefer_energy_boost,
                future_targets,
                deck_cards,
                live_target if isinstance(live_target, dict) else None,
                future_alternatives_by_turn,
                turn_index,
                stage,
                recovery_alternatives,
            )
            if turn_trace is not None:
                turn_trace["live_set"] = {
                    "prefer_energy_boost": prefer_energy_boost,
                    "live_score_target": live_target.get("target_score") if isinstance(live_target, dict) else None,
                    "recovery_rescue_mode": recovery_rescue_mode,
                    "energy_bridge_plan": energy_bridge_plan,
                    "selected": [_card_trace_label(card) for card in _live_set_cards],
                    "live_for_success": _card_trace_label(live_set_card),
                    "exchanged_count": len(_live_set_cards),
                    "top_need_scores_before_exchange": _need_score_trace(before_live_hand, future_alternatives_by_turn, deck_cards),
                }
            bonus_costs: list[int] = []
            for card in stage:
                if not card:
                    continue
                for _ in range(int(card.get("low_cost_summon_n") or 0)):
                    if len(_stage_costs(stage)) + len(bonus_costs) < 3:
                        bonus_costs.append(2)
            if live_set_card is not None and _live_basic_success_candidate(stage, live_set_card):
                has_low_cost_in_hand = any(
                    card.get("kind") == "member"
                    and card.get("cost") is not None
                    and int(card.get("cost") or 0) <= 2
                    for card in hand
                )
                if has_low_cost_in_hand:
                    for card in stage:
                        if not card:
                            continue
                        for _ in range(int(card.get("live_success_low_cost_summon_n") or 0)):
                            if len(_stage_costs(stage)) + len(bonus_costs) < 3:
                                bonus_costs.append(2)
            costs = _stage_costs(stage)
            costs_with_bonus = sorted(costs + bonus_costs, reverse=True)
            draw_index, success_drawn_cards, success_discarded_card = _apply_live_success_smoothing(
                hand,
                deck,
                draw_index,
                live_set_card,
                deck_cards,
                future_alternatives_by_turn,
                start_turn_index=turn_index,
            )
            placed_energy = 0
            if live_set_card is not None:
                boost_n = max(0, int(live_set_card.get("live_success_energy_boost_n") or live_set_card.get("energy_boost_n") or 0))
                if boost_n > 0 and energy_state["deck_remaining"] > 0:
                    placed = min(boost_n, energy_state["deck_remaining"])
                    energy_state["wait"] += placed
                    energy_state["deck_remaining"] -= placed
                    placed_energy = placed
            turn_success = any(_shape_meets_target(costs_with_bonus, sorted(alternative, reverse=True)) for alternative in alternatives)
            recovery_success = turn_success or any(
                _shape_meets_target(costs_with_bonus, sorted(alternative, reverse=True))
                for alternative in recovery_alternatives
            )
            if turn_success:
                turn_hits[turn_index] += 1
            else:
                miss_reasons[turn_index][_miss_reason(costs_with_bonus, alternatives)] += 1
            prefix_success = prefix_success and turn_success
            if prefix_success:
                cumulative_hits[turn_index] += 1
            if recovery_success:
                recovery_hits[turn_index] += 1
            recovery_prefix_success = recovery_prefix_success and recovery_success
            if recovery_prefix_success:
                recovery_cumulative_hits[turn_index] += 1
            accepted_scores = live_target.get("accepted_scores", []) if isinstance(live_target, dict) else []
            live_score_card = live_set_card if live_set_card is not None and live_set_card.get("kind") == "live" else None
            live_score_success = live_score_card is not None and int(live_score_card.get("score") or 0) in set(int(v) for v in accepted_scores)
            if live_score_success:
                live_score_hits[turn_index] += 1
            live_score_prefix_success = live_score_prefix_success and live_score_success
            if live_score_prefix_success:
                live_score_cumulative_hits[turn_index] += 1
            combined_prefix_success = combined_prefix_success and turn_success and live_score_success
            if combined_prefix_success:
                combined_cumulative_hits[turn_index] += 1
            total_values[turn_index] += sum(costs_with_bonus)
            shape_text = "-".join(str(v) for v in costs_with_bonus) if costs_with_bonus else "none"
            trial_shapes.append(shape_text)
            if turn_trace is not None:
                turn_trace["result"] = {
                    "stage_costs": shape_text,
                    "turn_success": turn_success,
                    "recovery_success": recovery_success,
                    "recovery_match": _alternatives_trace_label([
                        shape for shape in recovery_alternatives
                        if _shape_meets_target(costs_with_bonus, sorted(shape, reverse=True))
                    ]),
                    "miss_reason": "" if turn_success else _miss_reason(costs_with_bonus, alternatives),
                    "live_score_success": live_score_success,
                    "live_success_drawn": [_card_trace_label(card) for card in success_drawn_cards],
                    "live_success_discarded": _card_trace_label(success_discarded_card),
                    "energy_added_by_live_success_model": placed_energy,
                    "end_energy": dict(energy_state),
                    "end_hand_count": len(hand),
                }
                trace["turns"].append(turn_trace)
        exact_shape_counts[" / ".join(trial_shapes)] += 1
        if len(sample_lines) < 5:
            sample_lines.append("T{}: ".format(trial + 1) + " -> ".join(trial_shapes))
        if trace is not None:
            trace["route"] = " -> ".join(trial_shapes)
            decision_traces.append(trace)

    return {
        "schema_version": 1,
        "model": "max_target_probability_heuristic",
        "trials": trials,
        "seed": seed,
        "max_turns": max_turns,
        "mulligan_policy": "choose main/sub progression plans from the opening six, then maximize the probability of keeping stage progression on plan before considering live success",
        "success_definition": "turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence",
        "decision_policy": [
            "Initial hand is six cards from the shuffled deck.",
            "Mulligan first chooses a main progression plan and a sub progression plan from the opening six, then scores every keep subset by the chance that turn 1-3 stage progression stays on those plans.",
            "The broad accepted targets are still used as fallback, but the main plan's consecutive stage-progression probability has the highest mulligan weight.",
            "Abundant 2-cost members are kept only up to the near-term need because extra copies are comparatively easy to redraw.",
            "Live cards with energy-boost text are kept when they are needed for a bridge route, but are protected from live-set exchange before that route.",
            "High-impact progression effects worth two or more energy-equivalent tempo are protected and prioritized as deck-axis engines, not treated as ordinary utility cards.",
            "Cards with low turn 1-3 target value are redrawn back to six cards.",
            "Each turn performs active, energy, normal draw, member placement, then live-set exchange in that order.",
            "During live set, up to three cards may be exchanged, including non-live cards.",
            "Live set exchanges low-priority or replaceable cards to dig toward the nearest target; it does not automatically set every live card.",
            "When multiple live cards are exchange candidates, the live card to actually resolve is chosen by practical effect value: energy acceleration for bridge turns first, then draw/search value, then live score.",
            "Live score targets are inferred from live cards actually present in the deck; the hit check uses the highest-score live card selected during that turn's live-set exchange.",
            "If the next turn's target is reachable only after an energy-boost live succeeds, the boost live is preferred as the live-set card for that turn.",
            "Member placement tracks active/wait energy, pays active energy for normal plays, applies baton and effect-based cost reduction for replacements, then scores feasible lines as higher than target first, exact target second, then the largest available fallback.",
            "If a staged member has a once-per-turn style energy-activation effect and active energy is the blocker for the current target, the model uses that effect before member placement and discards the lowest future-use card when a hand cost is visible.",
            "When a played member has an entry effect that readies energy, that ready effect is modeled immediately after the play and can support later plays in the same main phase.",
            "Extra members beyond the accepted target slot count are not played only for occupancy; the persistent stage keeps existing cards unless replacing them improves the current target.",
            "After live success, draw effects on the live-set card are modeled as hand smoothing for the following turn; discard choice protects near-future target cards and progression-support effects.",
            "Energy-boost lives place energy into wait for the next active phase.",
        ],
        "effect_assumptions": [
            "up to three cards are live-set exchanged after member planning, and each exchanged card draws one replacement",
            "the normal draw step is modeled once per turn, including turn 1",
            "live draw effects are modeled as hand smoothing after each turn",
            "when live-success draw effects discard a card, the discarded card is the lowest practical future-use card, not simply the lowest cost/score card",
            "member activation effects that ready energy are modeled only when they directly unblock the current stage target; detailed active/wait member state is not fully simulated yet",
            "member cost reduction amounts are parsed from effect text and included in member play cost and next-turn energy bridge estimates",
            "entry effects that ready energy are modeled as same-main-phase active energy after the member enters",
            "Energy-boost live cards are modeled as next-turn bridge cards when the current stage plus normal energy is short of the next target but succeeds with the boost; the added energy becomes usable from the next turn",
            "two-or-more energy-equivalent acceleration, cost reduction, free/overcost member play, and low-cost stage-summon effects receive additional keep/play priority as major progression effects",
            "low-cost stage summon effects add an extra virtual 2-cost member for progression matching",
        ],
        "recommended_early": recommended_early,
        "recommended_late": recommended_late,
        "target_turns": target_turns,
        "target_alternatives": target_alternatives,
        "planning_alternatives": planning_alternatives,
        "stage_goal_plans": stage_goal_plans,
        "target_goal_summary": target_goal_summary,
        "live_score_targets": live_score_targets,
        "turn_hit_rates": [
            round(hit / max(1, trials), 4)
            for hit in turn_hits
        ],
        "cumulative_hit_rates": [
            round(hit / max(1, trials), 4)
            for hit in cumulative_hits
        ],
        "recovery_hit_rates": [
            round(hit / max(1, trials), 4)
            for hit in recovery_hits
        ],
        "recovery_cumulative_hit_rates": [
            round(hit / max(1, trials), 4)
            for hit in recovery_cumulative_hits
        ],
        "live_score_hit_rates": [
            round(hit / max(1, trials), 4)
            for hit in live_score_hits
        ],
        "live_score_cumulative_hit_rates": [
            round(hit / max(1, trials), 4)
            for hit in live_score_cumulative_hits
        ],
        "combined_cumulative_hit_rates": [
            round(hit / max(1, trials), 4)
            for hit in combined_cumulative_hits
        ],
        "average_stage_costs": [
            round(value / max(1, trials), 2)
            for value in total_values
        ],
        "top_shape_routes": [
            {"route": route, "count": count, "rate": round(count / max(1, trials), 4)}
            for route, count in exact_shape_counts.most_common(10)
        ],
        "miss_reasons": [
            [
                {"reason": reason, "count": count, "rate": round(count / max(1, trials), 4)}
                for reason, count in counter.most_common(5)
            ]
            for counter in miss_reasons
        ],
        "sample_routes": sample_lines,
        "decision_traces": decision_traces,
    }


def build_autoplay_markdown_report(report: dict[str, Any], trial_result: dict[str, Any] | None = None) -> str:
    curve = report.get("curve") if isinstance(report.get("curve"), dict) else {}
    bands = curve.get("member_cost_bands") if isinstance(curve.get("member_cost_bands"), dict) else {}
    signals = curve.get("special_signals") if isinstance(curve.get("special_signals"), dict) else {}
    lines = [
        f"# Autoplay Policy Report: {report.get('deck_name') or report.get('deck_path') or 'deck'}",
        "",
        f"- model: `{report.get('model_stage', '')}`",
        f"- recommended: {dict(report.get('recommended_progression') or {}).get('label', '未判定')}",
        "",
        "## Cost Bands",
        "",
    ]
    for key, label in (
        ("low_2_4", "2-4"),
        ("mid_5_10", "5-10"),
        ("bridge_11_14", "11-14"),
        ("high_15_plus", "15+"),
    ):
        lines.append(f"- {label}: {bands.get(key, 0)}")
    major_accel = signals.get("major_acceleration", []) if isinstance(signals, dict) else []
    if major_accel:
        lines.extend(["", "## Major Progression Effects", ""])
        for item in major_accel[:12]:
            if not isinstance(item, dict):
                continue
            value = item.get("accel_value", "")
            base = item.get("cost", item.get("score", ""))
            lines.append(
                f"- {item.get('card_no', '')} {item.get('name', '')} "
                f"base={base} count={item.get('count', '')} accel_value={value}"
            )
    lines.extend(["", "## Progressions", ""])
    for item in report.get("progressions", []) or []:
        if not isinstance(item, dict):
            continue
        turns = " / ".join("-".join(str(v) for v in turn) for turn in item.get("turns", []))
        missing = item.get("missing_costs") if isinstance(item.get("missing_costs"), dict) else {}
        missing_text = "なし" if not missing else ", ".join(f"{k}コストx{v}" for k, v in sorted(missing.items(), key=lambda part: int(part[0])))
        energy = item.get("energy_path") if isinstance(item.get("energy_path"), dict) else {}
        energy_text = (
            "direct={} boost={} short={}".format(
                energy.get("direct_turns", ""),
                energy.get("bridge_turns", ""),
                energy.get("shortfall", ""),
            )
            if energy else "none"
        )
        lines.append(
            f"- {item.get('label')}: score={item.get('score')} coverage={item.get('coverage')} "
            f"energy={energy_text} scarce_penalty={item.get('early_scarcity_penalty', 0)} turns={turns} missing={missing_text}"
        )
    lines.extend(["", "## Special Signals", ""])
    for key, label in (
        ("energy_boost", "エネルギー追加ライブ"),
        ("energy_activate", "エネルギーアクティブ化"),
        ("cost_reduction", "コスト軽減"),
        ("free_member_play", "エネルギー支払いなし登場"),
        ("overcost_member_play", "支払い以上の登場"),
        ("low_cost_summon", "低コスト追加登場"),
        ("live_success_low_cost_summon", "ライブ成功時低コスト登場"),
        ("member_recovery", "メンバー回収"),
        ("live_member_recovery", "ライブ成功時メンバー回収"),
        ("special_baton", "特殊バトンタッチ"),
        ("high_cost_anchor", "15+高コスト"),
    ):
        items = signals.get(key, []) if isinstance(signals.get(key, []), list) else []
        lines.append(f"### {label}")
        if not items:
            lines.append("- なし")
        for item in items:
            if isinstance(item, dict):
                value_label = "cost" if item.get("cost") is not None else "score"
                value = item.get("cost") if item.get("cost") is not None else item.get("score")
                lines.append(f"- {item.get('card_no')} {item.get('name')} x{item.get('count')} {value_label}={value}")
        lines.append("")
    if trial_result:
        lines.extend(["## Trial Result", ""])
        lines.append(f"- model: `{trial_result.get('model', '')}`")
        lines.append(f"- trials: {trial_result.get('trials')}")
        if trial_result.get("base_seed") is not None or trial_result.get("effective_seed") is not None:
            lines.append(f"- seed: base={trial_result.get('base_seed', trial_result.get('seed'))} effective={trial_result.get('effective_seed', trial_result.get('seed'))}")
        else:
            lines.append(f"- seed: {trial_result.get('seed')}")
        lines.append(f"- mulligan: {trial_result.get('mulligan_policy', '未設定')}")
        lines.append(f"- success: {trial_result.get('success_definition', '完全一致')}")
        early = trial_result.get("recommended_early") if isinstance(trial_result.get("recommended_early"), dict) else {}
        late = trial_result.get("recommended_late") if isinstance(trial_result.get("recommended_late"), dict) else {}
        lines.append(f"- early policy: {early.get('label', '未判定')}")
        lines.append(f"- late policy: {late.get('label', '未判定')}")
        target_text = " / ".join("-".join(str(v) for v in turn) for turn in trial_result.get("target_turns", []) or [])
        lines.append(f"- target turns: {target_text}")
        target_alternatives = trial_result.get("target_alternatives", []) if isinstance(trial_result.get("target_alternatives"), list) else []
        if target_alternatives:
            alt_texts = []
            for alternatives in target_alternatives:
                if not isinstance(alternatives, list):
                    continue
                alt_texts.append(" or ".join("-".join(str(v) for v in alt) for alt in alternatives if isinstance(alt, list)))
            if alt_texts:
                lines.append(f"- accepted targets: {' / '.join(alt_texts)}")
        recovery_texts: list[str] = []
        for plan in trial_result.get("stage_goal_plans", []) or []:
            if not isinstance(plan, dict):
                continue
            recovery_shapes = plan.get("recovery_shapes", []) if isinstance(plan.get("recovery_shapes"), list) else []
            recovery_texts.append(" or ".join("-".join(str(v) for v in shape) for shape in recovery_shapes if isinstance(shape, list)))
        if any(recovery_texts):
            lines.append(f"- recovery targets: {' / '.join(text or 'none' for text in recovery_texts)}")
        assumptions = trial_result.get("effect_assumptions", []) if isinstance(trial_result.get("effect_assumptions"), list) else []
        if assumptions:
            lines.extend(["", "### Effect Assumptions", ""])
            for item in assumptions:
                lines.append(f"- {item}")
        decision_policy = trial_result.get("decision_policy", []) if isinstance(trial_result.get("decision_policy"), list) else []
        if decision_policy:
            lines.extend(["", "### Decision Policy", ""])
            for item in decision_policy:
                lines.append(f"- {item}")
        goal_summary = trial_result.get("target_goal_summary", []) if isinstance(trial_result.get("target_goal_summary"), list) else []
        if goal_summary:
            lines.extend(["", "### Target Cards And Routes", ""])
            for turn in goal_summary:
                if not isinstance(turn, dict):
                    continue
                lines.append(f"- T{turn.get('turn')}")
                alternatives = turn.get("alternatives", []) if isinstance(turn.get("alternatives"), list) else []
                for alternative in alternatives:
                    if not isinstance(alternative, dict):
                        continue
                    shape = "-".join(str(v) for v in alternative.get("shape", []) or [])
                    cards = alternative.get("cards", []) if isinstance(alternative.get("cards"), list) else []
                    card_text = " / ".join(
                        "{} {} route={}".format(card.get("card_no"), card.get("name"), card.get("route"))
                        for card in cards
                        if isinstance(card, dict)
                    )
                    lines.append(f"  - {shape}: {card_text or '該当カードなし'}")
                recovery_alternatives = turn.get("recovery_alternatives", []) if isinstance(turn.get("recovery_alternatives"), list) else []
                for alternative in recovery_alternatives:
                    if not isinstance(alternative, dict):
                        continue
                    shape = "-".join(str(v) for v in alternative.get("shape", []) or [])
                    cards = alternative.get("cards", []) if isinstance(alternative.get("cards"), list) else []
                    card_text = " / ".join(
                        "{} {} route={}".format(card.get("card_no"), card.get("name"), card.get("route"))
                        for card in cards
                        if isinstance(card, dict)
                    )
                    lines.append(f"  - recovery {shape}: {card_text or '該当カードなし'} / {alternative.get('route', '')}")
        hit_rates = trial_result.get("turn_hit_rates", []) or []
        recovery_rates = trial_result.get("recovery_hit_rates", []) or []
        recovery_cumulative_rates = trial_result.get("recovery_cumulative_hit_rates", []) or []
        averages = trial_result.get("average_stage_costs", []) or []
        lines.extend(["", "### Turn Summary", ""])
        lines.append("- `hit_rate` はそのターン単独の通常盤面形達成率、`cumulative` はT1からそのターンまで連続で通常達成した率。`recovery_cumulative` は回収・加速で復帰可能な妥協形も含む補助指標。")
        combined_rates = trial_result.get("combined_cumulative_hit_rates", []) or []
        for index, target in enumerate(trial_result.get("target_turns", []) or [], start=1):
            hit = hit_rates[index - 1] if index - 1 < len(hit_rates) else ""
            cumulative_rates = trial_result.get("cumulative_hit_rates", []) or []
            cumulative = cumulative_rates[index - 1] if index - 1 < len(cumulative_rates) else ""
            recovery = recovery_rates[index - 1] if index - 1 < len(recovery_rates) else ""
            recovery_cumulative = recovery_cumulative_rates[index - 1] if index - 1 < len(recovery_cumulative_rates) else ""
            combined = combined_rates[index - 1] if index - 1 < len(combined_rates) else ""
            avg = averages[index - 1] if index - 1 < len(averages) else ""
            lines.append(f"- T{index}: target={'-'.join(str(v) for v in target)} hit_rate={hit} cumulative={cumulative} recovery_hit={recovery} recovery_cumulative={recovery_cumulative} combined_cumulative={combined} avg_stage_cost={avg}")
        live_targets = trial_result.get("live_score_targets", []) if isinstance(trial_result.get("live_score_targets"), list) else []
        live_rates = trial_result.get("live_score_hit_rates", []) or []
        live_cumulative_rates = trial_result.get("live_score_cumulative_hit_rates", []) or []
        if live_targets:
            lines.extend(["", "### Live Score Targets", ""])
            for index, item in enumerate(live_targets, start=1):
                if not isinstance(item, dict):
                    continue
                rate = live_rates[index - 1] if index - 1 < len(live_rates) else ""
                cumulative = live_cumulative_rates[index - 1] if index - 1 < len(live_cumulative_rates) else ""
                cards = item.get("cards", []) if isinstance(item.get("cards"), list) else []
                card_text = " / ".join(
                    "{} {} score={}".format(card.get("card_no"), card.get("name"), card.get("score"))
                    for card in cards
                    if isinstance(card, dict)
                )
                lines.append(f"- T{index}: target_score={item.get('target_score')} accepted={item.get('accepted_scores')} hit_rate={rate} cumulative={cumulative} cards={card_text}")
        lines.extend(["", "### Top Routes", ""])
        for item in trial_result.get("top_shape_routes", []) or []:
            if isinstance(item, dict):
                lines.append(f"- {item.get('route')}: {item.get('count')} ({item.get('rate')})")
        lines.extend(["", "### Miss Reasons", ""])
        for index, reasons in enumerate(trial_result.get("miss_reasons", []) or [], start=1):
            if not reasons:
                lines.append(f"- T{index}: none")
                continue
            reason_text = ", ".join(
                f"{item.get('reason')} {item.get('count')} ({item.get('rate')})"
                for item in reasons
                if isinstance(item, dict)
            )
            lines.append(f"- T{index}: {reason_text}")
        lines.extend(["", "### Sample Routes", ""])
        for item in trial_result.get("sample_routes", []) or []:
            lines.append(f"- {item}")
        traces = trial_result.get("decision_traces", []) if isinstance(trial_result.get("decision_traces"), list) else []
        if traces:
            lines.extend(["", "## Decision Trace", ""])
            for trace in traces:
                if not isinstance(trace, dict):
                    continue
                lines.append(f"### Trial {trace.get('trial')}")
                lines.append(f"- route: {trace.get('route', '')}")
                initial_hand = trace.get("initial_hand", []) if isinstance(trace.get("initial_hand"), list) else []
                lines.append(f"- initial hand: {' | '.join(str(item) for item in initial_hand) if initial_hand else 'none'}")
                mulligan = trace.get("mulligan") if isinstance(trace.get("mulligan"), dict) else {}
                if mulligan:
                    kept = mulligan.get("kept", []) if isinstance(mulligan.get("kept"), list) else []
                    returned = mulligan.get("returned", []) if isinstance(mulligan.get("returned"), list) else []
                    lines.append(f"- mulligan target: {mulligan.get('targets', '')}")
                    lines.append(
                        "- mulligan plans: main={} initial_p={} / sub={} initial_p={}".format(
                            mulligan.get("main_plan", "none"),
                            mulligan.get("main_plan_initial_probabilities", []),
                            mulligan.get("sub_plan", "none"),
                            mulligan.get("sub_plan_initial_probabilities", []),
                        )
                    )
                    lines.append(f"- mulligan score: {mulligan.get('score', '')} p(T1/T2/T3)={mulligan.get('probabilities', '')} draw_windows={mulligan.get('draw_windows', '')}")
                    focus = mulligan.get("critical_focus") if isinstance(mulligan.get("critical_focus"), dict) else {}
                    if focus:
                        lines.append(
                            "- critical focus: {} focus_costs={} turn_access={} key_total={} all-redraw-p={} two-keep-p={} gap={}".format(
                                focus.get("label"),
                                focus.get("focus_costs"),
                                round(float(focus.get("turn_access_probability") or 0.0), 3),
                                focus.get("key_total"),
                                round(float(focus.get("no_keep_probability") or 0.0), 3),
                                round(float(focus.get("two_keep_probability") or 0.0), 3),
                                round(float(focus.get("gap") or 0.0), 3),
                            )
                        )
                    lines.append(f"- keep: {' | '.join(str(item) for item in kept) if kept else 'none'}")
                    lines.append(f"- return: {' | '.join(str(item) for item in returned) if returned else 'none'}")
                    redrawn = mulligan.get("redrawn", []) if isinstance(mulligan.get("redrawn"), list) else []
                    post_hand = mulligan.get("post_mulligan_hand", []) if isinstance(mulligan.get("post_mulligan_hand"), list) else []
                    lines.append(f"- redraw: {' | '.join(str(item) for item in redrawn) if redrawn else 'none'}")
                    lines.append(f"- post mulligan hand: {' | '.join(str(item) for item in post_hand) if post_hand else 'none'}")
                    lines.append(f"- post mulligan plans: main={mulligan.get('post_main_plan', 'none')} / sub={mulligan.get('post_sub_plan', 'none')}")
                    lines.append(f"- hand need score: {mulligan.get('top_need_scores', 'none')}")
                    top_candidates = mulligan.get("top_candidates", []) if isinstance(mulligan.get("top_candidates"), list) else []
                    if top_candidates:
                        lines.append("- mulligan candidate comparison:")
                        for item in top_candidates:
                            lines.append(f"  - {item}")
                for turn in trace.get("turns", []) or []:
                    if not isinstance(turn, dict):
                        continue
                    lines.extend(["", f"#### T{turn.get('turn')} target {turn.get('target')} accepted {turn.get('accepted')} recovery {turn.get('recovery', '')}"])
                    lines.append(f"- start stage: {turn.get('start_stage')}")
                    lines.append(f"- start energy: {turn.get('start_energy')}")
                    lines.append(f"- normal draw: {turn.get('normal_draw', 'none')}")
                    main = turn.get("main") if isinstance(turn.get("main"), dict) else {}
                    if main:
                        played = main.get("played_or_replaced_in", []) if isinstance(main.get("played_or_replaced_in"), list) else []
                        removed = main.get("replaced_out", []) if isinstance(main.get("replaced_out"), list) else []
                        lines.append(f"- main stage: {main.get('before_stage')} -> {main.get('after_stage')}")
                        lines.append(f"- main played/replaced in: {' | '.join(str(item) for item in played) if played else 'none'}")
                        lines.append(f"- main replaced out: {' | '.join(str(item) for item in removed) if removed else 'none'}")
                        enter_effects = main.get("enter_topdeck_effects", []) if isinstance(main.get("enter_topdeck_effects"), list) else []
                        for effect in enter_effects:
                            if not isinstance(effect, dict):
                                continue
                            lines.append(
                                "- enter topdeck effect: source={} kind={} looked={} selected={} kept_on_top={} moved_to_green={} discarded_cost={}".format(
                                    effect.get("source"),
                                    effect.get("kind"),
                                    " | ".join(str(item) for item in effect.get("looked", []) if item) if isinstance(effect.get("looked"), list) else "none",
                                    effect.get("selected", "none"),
                                    " | ".join(str(item) for item in effect.get("kept_on_top", []) if item) if isinstance(effect.get("kept_on_top"), list) else "none",
                                    " | ".join(str(item) for item in effect.get("moved_to_green", []) if item) if isinstance(effect.get("moved_to_green"), list) else "none",
                                    effect.get("discarded_cost", "none"),
                                )
                            )
                        recovery = main.get("recovery_support") if isinstance(main.get("recovery_support"), dict) else {}
                        if recovery.get("used"):
                            lines.append(
                                "- stage recovery support: source={} recovered={} reason={} after_stage={} energy_after={}".format(
                                    recovery.get("source"),
                                    recovery.get("recovered"),
                                    recovery.get("reason"),
                                    recovery.get("after_stage"),
                                    recovery.get("energy_after"),
                                )
                            )
                        activation = main.get("activation_support") if isinstance(main.get("activation_support"), dict) else {}
                        if activation and activation.get("activated"):
                            activated = activation.get("activated", []) if isinstance(activation.get("activated"), list) else []
                            discarded = activation.get("discarded", []) if isinstance(activation.get("discarded"), list) else []
                            lines.append(
                                "- main activated effect: {} energy {} -> {} discard={}".format(
                                    " | ".join(str(item) for item in activated) if activated else "none",
                                    activation.get("energy_before"),
                                    activation.get("energy_after"),
                                    " | ".join(str(item) for item in discarded) if discarded else "none",
                                )
                            )
                        lines.append(f"- main energy: {main.get('energy_before')} -> {main.get('energy_after')}")
                    live_set = turn.get("live_set") if isinstance(turn.get("live_set"), dict) else {}
                    if live_set:
                        selected = live_set.get("selected", []) if isinstance(live_set.get("selected"), list) else []
                        lines.append(f"- live set selected: {' | '.join(str(item) for item in selected) if selected else 'none'}")
                        bridge_plan = live_set.get("energy_bridge_plan") if isinstance(live_set.get("energy_bridge_plan"), dict) else {}
                        lines.append(
                            "- live set reason: prefer_energy_boost={} recovery_rescue_mode={} target_score={} live_for_success={} bridge={}".format(
                                live_set.get("prefer_energy_boost"),
                                live_set.get("recovery_rescue_mode"),
                                live_set.get("live_score_target"),
                                live_set.get("live_for_success"),
                                "next {} need {} base {} boosted {} ({})".format(
                                    bridge_plan.get("next_target") or "?",
                                    bridge_plan.get("min_required"),
                                    bridge_plan.get("base_active_next"),
                                    bridge_plan.get("boosted_active_next"),
                                    bridge_plan.get("reason") or "none",
                                ) if bridge_plan else "none",
                            )
                        )
                        lines.append(f"- pre-exchange need score: {live_set.get('top_need_scores_before_exchange', 'none')}")
                    result = turn.get("result") if isinstance(turn.get("result"), dict) else {}
                    if result:
                        lines.append(
                            "- result: stage={} stage_hit={} recovery_hit={} recovery_match={} live_score_hit={} miss={} energy_added={} end_energy={}".format(
                                result.get("stage_costs"),
                                result.get("turn_success"),
                                result.get("recovery_success"),
                                result.get("recovery_match"),
                                result.get("live_score_success"),
                                result.get("miss_reason") or "none",
                                result.get("energy_added_by_live_success_model"),
                                result.get("end_energy"),
                            )
                        )
                        drawn = result.get("live_success_drawn", []) if isinstance(result.get("live_success_drawn"), list) else []
                        if drawn or result.get("live_success_discarded"):
                            lines.append(
                                "- live success effect: drawn={} discarded={}".format(
                                    " | ".join(str(item) for item in drawn) if drawn else "none",
                                    result.get("live_success_discarded") or "none",
                                )
                            )
    return "\n".join(lines).rstrip() + "\n"


def build_autoplay_deck_report(
    rows: list[dict[str, str]],
    card_lookup: CardLookup,
) -> dict[str, Any]:
    curve = build_deck_curve(rows, card_lookup)
    dynamic_templates = _dynamic_progression_templates(curve)
    templates: list[CostProgressionTemplate] = []
    seen_keys: set[str] = set()
    seen_turns: set[tuple[tuple[int, ...], ...]] = set()
    for template in list(COST_PROGRESSIONS) + list(dynamic_templates):
        normalized = _normalized_turns(template.turns)
        if template.key in seen_keys or normalized in seen_turns:
            continue
        seen_keys.add(template.key)
        seen_turns.add(normalized)
        templates.append(template)
    progressions = [
        evaluate_progression(curve, template)
        for template in templates
    ]
    progressions = [
        item for item in progressions
        if not item.get("unavailable_costs")
    ]
    progressions.sort(key=lambda item: (
        -(float(item.get("score") or 0) - (1.0 if item.get("source") == "dynamic" else 0.0)),
        1 if item.get("source") == "dynamic" else 0,
        str(item.get("key") or ""),
    ))
    return {
        "schema_version": 1,
        "model_stage": "stage1_policy_template",
        "curve": curve,
        "dynamic_progressions": [
            {
                "key": item.key,
                "label": item.label,
                "turns": [list(turn) for turn in item.turns],
                "intent": item.intent,
            }
            for item in dynamic_templates
        ],
        "progressions": progressions,
        "recommended_progression": progressions[0] if progressions else {},
        "goal_type_presets": list(GOAL_TYPE_PRESETS),
        "notes": [
            "This is a deck-curve policy model, not a full engine-playing bot yet.",
            "Early choices emphasize 5-10 cost distribution; late choices emphasize 15+ cost distribution.",
            "Cost reduction and special baton-touch signals are detected from generic effect text.",
            "Stage 2 will add weighted target correction.",
            "Stage 3 will run repeated trials and propose construction changes.",
        ],
    }
