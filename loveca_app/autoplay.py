#!/usr/bin/env python3
# BUILD_TAG = "autoplay_main_completion_trace_20260730a"
"""Autoplay planning primitives for Loveca Application.

This module is intentionally side-effect free.  It evaluates a deck's cost
curve and returns policy candidates; runtime state mutation remains in the
simulator engine.
"""
from __future__ import annotations

import re
import random
from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable


BUILD_TAG = "autoplay_main_completion_trace_20260730a"


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
        energy_boost_n = _effect_energy_boost_count(effect_text)
        low_cost_summon_n = _effect_low_cost_stage_summon_count(effect_text)
        cost_reduction = bool(re.search(r"コスト.*(?:減|少なく|軽減)|(?:減|少なく|軽減).*コスト", effect_text))
        for _ in range(count):
            seq += 1
            cards.append({
                "id": seq,
                "card_no": card_no,
                "name": _card_name(record, card_no),
                "kind": kind,
                "cost": cost,
                "score": score,
                "draw_n": draw_n,
                "energy_boost_n": energy_boost_n,
                "low_cost_summon_n": low_cost_summon_n,
                "cost_reduction": cost_reduction,
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
        "cost": cost,
        "score": score,
        "value": int(cost or score or 0),
        "effect_text": effect_text,
        "draw_n": _effect_draw_count(effect_text),
        "energy_boost_n": _effect_energy_boost_count(effect_text),
        "low_cost_summon_n": _effect_low_cost_stage_summon_count(effect_text),
        "cost_reduction": bool(re.search(r"コスト.*(?:減|少なく|軽減)|(?:減|少なく|軽減).*コスト", effect_text)),
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


def _effect_low_cost_stage_summon_count(effect_text: str) -> int:
    text = str(effect_text or "")
    if "コスト2以下" in text and "メンバー" in text and "登場させる" in text:
        return 1
    return 0


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
        "cost_reduction": [],
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
            if cost >= 15 and len(special_signals["high_cost_anchor"]) < 8:
                special_signals["high_cost_anchor"].append(signal_item)
            if re.search(r"コスト.*(?:減|少なく|軽減)|(?:減|少なく|軽減).*コスト", effect_text) and len(special_signals["cost_reduction"]) < 8:
                special_signals["cost_reduction"].append(signal_item)
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
    if special_signals.get("cost_reduction"):
        special_bonus += 3.0
    coverage = sum(coverage_parts) / max(1, len(coverage_parts))
    score = round(
        (coverage * 72.0)
        + (early_score_bonus * 10.0)
        + mid_curve_bonus
        + late_bonus
        + special_bonus
        - max(0, hand_pressure - 5) * 2.0,
        2,
    )

    return {
        "key": template.key,
        "label": template.label,
        "intent": template.intent,
        "phase": template.phase,
        "turns": [list(turn) for turn in template.turns],
        "score": score,
        "coverage": round(coverage, 3),
        "missing_costs": missing,
        "unavailable_costs": unavailable,
        "strengths": list(template.strengths),
        "risks": list(template.risks),
    }


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
    score += min(3, len(costs)) * 5
    return score


def _best_target_shape_for_stage(stage: list[dict[str, Any] | None], alternatives: list[list[int]]) -> list[int]:
    if not alternatives:
        return []
    return max(alternatives, key=lambda shape: (_stage_score(stage, shape), sum(shape)))


def _stage_slots_to_replace(stage: list[dict[str, Any] | None], target_shape: list[int]) -> list[int]:
    if not stage:
        return []
    keep_indices: set[int] = set()
    for target in sorted([int(value) for value in target_shape], reverse=True):
        candidates = [
            (index, int(card.get("cost") or 0))
            for index, card in enumerate(stage)
            if card is not None and index not in keep_indices
        ]
        if not candidates:
            continue
        above = [item for item in candidates if item[1] > target]
        exact = [item for item in candidates if item[1] == target]
        below = [item for item in candidates if item[1] < target]
        if above:
            chosen = max(above, key=lambda item: item[1])
        elif exact:
            chosen = exact[0]
        elif below:
            continue
        else:
            continue
        keep_indices.add(chosen[0])
    empty = [index for index, card in enumerate(stage) if card is None]
    replace = [
        index for index, card in enumerate(stage)
        if card is not None and index not in keep_indices
    ]
    replace.sort(key=lambda index: int((stage[index] or {}).get("cost") or 0))
    return empty + replace


def _improve_persistent_stage(
    stage: list[dict[str, Any] | None],
    hand: list[dict[str, Any]],
    alternatives: list[list[int]],
) -> list[dict[str, Any] | None]:
    if len(stage) < 3:
        stage.extend([None] * (3 - len(stage)))
    best_shape = _best_target_shape_for_stage(stage, alternatives)
    if not best_shape:
        return stage
    best_score = _stage_score(stage, best_shape)
    while True:
        candidates: list[tuple[int, int, dict[str, Any]]] = []
        for slot in _stage_slots_to_replace(stage, best_shape):
            for card in hand:
                if card.get("kind") != "member" or card.get("cost") is None:
                    continue
                trial_stage = list(stage)
                trial_stage[slot] = card
                score = _stage_score(trial_stage, best_shape)
                gain = score - best_score
                if gain > 0:
                    candidates.append((gain, int(card.get("cost") or 0), card))
        if not candidates:
            break
        gain, _cost, card = max(candidates, key=lambda item: (item[0], item[1]))
        replace_slots = _stage_slots_to_replace(stage, best_shape)
        best_slot = None
        best_slot_score = best_score
        for slot in replace_slots:
            trial_stage = list(stage)
            trial_stage[slot] = card
            score = _stage_score(trial_stage, best_shape)
            if score > best_slot_score:
                best_slot = slot
                best_slot_score = score
        if best_slot is None:
            break
        stage[best_slot] = card
        hand.remove(card)
        best_score = best_slot_score
        if gain <= 0:
            break
    return stage


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
            elif any(cost > int(target) for target in target_shape):
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


def _choose_mulligan_keep(
    hand: list[dict[str, Any]],
    target_turns: list[list[int]],
    deck_cards: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    keep: list[dict[str, Any]] = []
    low_needed = max(2, max((Counter(turn).get(2, 0) for turn in target_turns[:2]), default=0))
    kept_low = 0
    scored = sorted(
        ((card, _card_need_score(card, target_turns, deck_cards)) for card in hand),
        key=lambda item: (-item[1], str(item[0].get("card_no") or "")),
    )
    for card, score in scored:
        if card.get("kind") == "member" and int(card.get("cost") or 0) == 2:
            if kept_low < low_needed and score >= 1.0:
                keep.append(card)
                kept_low += 1
            continue
        if score >= 3.0:
            keep.append(card)
    if not keep and hand:
        keep = [max(hand, key=lambda item: _card_need_score(item, target_turns, deck_cards))]
    return keep[:6]


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
        if card.get("kind") == "live" and int(card.get("energy_boost_n") or 0) > 0
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda card: (int(card.get("energy_boost_n") or 0), int(card.get("score") or 0)))


def _choose_live_set_cards(
    hand: list[dict[str, Any]],
    prefer_energy_boost: bool,
    future_targets: list[list[int]],
    deck_cards: list[dict[str, Any]],
    live_score_target: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    live_for_success: dict[str, Any] | None = None
    if prefer_energy_boost:
        energy_lives = [
            card for card in hand
            if card.get("kind") == "live" and int(card.get("energy_boost_n") or 0) > 0
        ]
        if energy_lives:
            live_for_success = max(energy_lives, key=lambda card: (int(card.get("energy_boost_n") or 0), int(card.get("score") or 0)))
            selected.append(live_for_success)

    score_live = _best_live_for_score_target(hand, live_score_target, protect_energy_boost=not prefer_energy_boost)
    if score_live is not None and score_live not in selected:
        selected.append(score_live)
    if score_live is not None and live_for_success is None:
        live_for_success = score_live

    candidates = [card for card in hand if card not in selected]
    scored = sorted(
        ((card, _card_need_score(card, future_targets, deck_cards)) for card in candidates),
        key=lambda item: (item[1], int(item[0].get("value") or 0), str(item[0].get("card_no") or "")),
    )
    for card, score in scored:
        if len(selected) >= 3:
            break
        if card.get("kind") == "live" and int(card.get("energy_boost_n") or 0) > 0 and not prefer_energy_boost:
            continue
        if score <= 1.5:
            selected.append(card)
    if live_for_success is None:
        live_for_success = next((card for card in selected if card.get("kind") == "live" and int(card.get("draw_n") or 0) > 0), None)
    return live_for_success, selected


def _live_set_exchange(
    hand: list[dict[str, Any]],
    deck: list[dict[str, Any]],
    draw_index: int,
    prefer_energy_boost: bool,
    future_targets: list[list[int]],
    deck_cards: list[dict[str, Any]],
    live_score_target: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, int, list[dict[str, Any]]]:
    live_for_success, selected = _choose_live_set_cards(
        hand,
        prefer_energy_boost,
        future_targets,
        deck_cards,
        live_score_target,
    )

    for card in selected:
        if card in hand:
            hand.remove(card)
    for _ in selected:
        if draw_index < len(deck):
            hand.append(deck[draw_index])
            draw_index += 1
    return live_for_success, draw_index, selected


def _apply_live_success_smoothing(hand: list[dict[str, Any]], deck: list[dict[str, Any]], draw_index: int, live: dict[str, Any] | None) -> int:
    if not live or int(live.get("draw_n") or 0) <= 0:
        return draw_index
    draw_n = min(int(live.get("draw_n") or 0), max(0, len(deck) - draw_index))
    for _ in range(draw_n):
        hand.append(deck[draw_index])
        draw_index += 1
    if draw_n >= 2 and hand:
        discard = min(hand, key=lambda card: (int(card.get("value") or 0), 0 if card.get("kind") == "other" else 1))
        hand.remove(discard)
    return draw_index


def _has_energy_boost_live(cards: list[dict[str, Any]]) -> bool:
    return any(card.get("kind") == "live" and int(card.get("energy_boost_n") or 0) > 0 for card in cards)


def _has_low_cost_stage_summon(cards: list[dict[str, Any]]) -> bool:
    return any(card.get("kind") == "member" and int(card.get("low_cost_summon_n") or 0) > 0 for card in cards)


def _target_alternatives_for_turn(target_shape: list[int], deck_cards: list[dict[str, Any]]) -> list[list[int]]:
    alternatives = [list(target_shape)] if _shape_costs_available(target_shape, deck_cards) else []
    if target_shape == [2, 2] and _shape_costs_available([4], deck_cards):
        alternatives.append([4])
    has_energy = _has_energy_boost_live(deck_cards)
    if target_shape == [2, 5, 2] and has_energy and _shape_costs_available([2, 4, 2], deck_cards):
        alternatives.append([2, 4, 2])
    if target_shape == [2, 15, 2]:
        alternatives = []
        for late_shape in ([15, 5, 2], [15, 4, 2], [15, 2, 2]):
            if _shape_costs_available(late_shape, deck_cards):
                alternatives.append(list(late_shape))
    if target_shape == [2, 10, 2]:
        for upside in ([2, 11, 2], [2, 13, 2]):
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
    return alternatives


def _stage_goal_plans(base_turns: list[list[int]], deck_cards: list[dict[str, Any]], max_turns: int) -> list[dict[str, Any]]:
    seed_turns = _deck_dynamic_target_turns(base_turns, deck_cards, max_turns)
    plans: list[dict[str, Any]] = []
    for turn_index, seed_shape in enumerate(seed_turns, start=1):
        accepted_shapes = _target_alternatives_for_turn(seed_shape, deck_cards)
        if not accepted_shapes and seed_shape:
            accepted_shapes = [list(seed_shape)]
        primary_shape = list(accepted_shapes[0]) if accepted_shapes else list(seed_shape)
        plans.append({
            "turn": turn_index,
            "seed_shape": list(seed_shape),
            "primary_shape": primary_shape,
            "accepted_shapes": [list(shape) for shape in accepted_shapes],
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


def _late_target_shape_from_deck(costs: Counter[int], turn_number: int) -> list[int]:
    available = sorted((cost for cost, count in costs.items() if count > 0), reverse=True)
    if not available:
        return []
    high = next((cost for cost in available if cost >= 15), available[0])
    low_count = costs.get(2, 0)
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
    return {
        "report": report,
        "recommended_early": recommended_early,
        "recommended_late": recommended_late,
        "deck_cards": deck_cards,
        "stage_goal_plans": stage_goal_plans,
        "target_turns": [list(plan.get("primary_shape", [])) for plan in stage_goal_plans],
        "target_alternatives": target_alternatives,
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
    best_shape = _best_target_shape_for_stage(stage, alternatives)
    if not best_shape:
        return None
    best_score = _stage_score(stage, best_shape)
    slot_names = ["L", "C", "R"]
    candidates: list[tuple[int, int, int, dict[str, Any], int]] = []
    for slot in _stage_slots_to_replace(stage, best_shape):
        for card in hand:
            if card.get("kind") != "member" or card.get("cost") is None:
                continue
            trial_stage = list(stage)
            trial_stage[slot] = card
            score = _stage_score(trial_stage, best_shape)
            gain = score - best_score
            if gain > 0:
                candidates.append((gain, int(card.get("cost") or 0), -slot, card, slot))
    if not candidates:
        return None
    gain, _cost, _slot_sort, card, slot = max(candidates, key=lambda item: (item[0], item[1], item[2]))
    return {
        "kind": "main_play",
        "command": "play",
        "payload": {"hand_idx": int(card.get("state_index", 0)), "pos": slot_names[slot]},
        "confidence": "medium",
        "reason": "accepted target {} に対するstage score gain +{}（目標超過を優先評価）".format("-".join(str(v) for v in best_shape), gain),
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
    return {
        "kind": "main_pass",
        "command": "NEXT",
        "payload": {},
        "confidence": "low",
        "reason": "MAIN追加登場で改善できる候補なし: stage {} / best target {} / {}".format(
            _stage_text(stage),
            "-".join(str(v) for v in best_shape) if best_shape else "none",
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
    pending_action = _cpu_pending_action(state)
    if pending_action is not None:
        pending_action["turn"] = turn_index + 1
        pending_action["phase"] = phase
        return pending_action
    if "MULLIGAN" in phase:
        hand = _state_indexed_cards(state.get("hand"), card_lookup)
        mulligan_targets = [
            alternative
            for alternatives in context["target_alternatives"][:3]
            for alternative in alternatives
        ]
        keep = _choose_mulligan_keep(hand, mulligan_targets, context["deck_cards"])
        keep_indices = {int(card.get("state_index", -1)) for card in keep}
        indices = [int(card.get("state_index", 0)) for card in hand if int(card.get("state_index", 0)) not in keep_indices]
        return {
            "kind": "mulligan",
            "command": "NEXT",
            "payload": {"indices": indices},
            "turn": turn_index + 1,
            "phase": phase,
            "confidence": "medium",
            "reason": "T1-T3 accepted targetsへの到達価値が低い手札を戻す",
        }
    if "LIVE_SET" in phase:
        hand = _state_indexed_cards(state.get("hand"), card_lookup)
        alternatives = list(goal_plan.get("accepted_shapes", [])) or [list(goal_plan.get("primary_shape", []))]
        prefer_energy_boost = any(alternative == [2, 4, 2] for alternative in alternatives)
        future_targets = [
            alternative
            for future_alternatives in context["target_alternatives"][turn_index: min(len(context["target_alternatives"]), turn_index + 3)]
            for alternative in future_alternatives
        ]
        live_target = context["live_score_targets"][turn_index] if turn_index < len(context["live_score_targets"]) else {}
        live_for_success, selected = _choose_live_set_cards(
            hand,
            prefer_energy_boost,
            future_targets,
            context["deck_cards"],
            live_target if isinstance(live_target, dict) else None,
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
            reason_parts.append("energy bridge候補ターン")
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
) -> dict[str, Any]:
    context = build_autoplay_policy_context(rows, card_lookup, max_turns=max_turns)
    recommended_early = context["recommended_early"]
    recommended_late = context["recommended_late"]
    deck_cards = context["deck_cards"]
    stage_goal_plans = context["stage_goal_plans"]
    target_turns = context["target_turns"]
    target_alternatives = context["target_alternatives"]
    target_goal_summary = context["target_goal_summary"]
    live_score_targets = context["live_score_targets"]
    rng = random.Random(seed)
    turn_hits = [0 for _ in range(max_turns)]
    cumulative_hits = [0 for _ in range(max_turns)]
    live_score_hits = [0 for _ in range(max_turns)]
    live_score_cumulative_hits = [0 for _ in range(max_turns)]
    combined_cumulative_hits = [0 for _ in range(max_turns)]
    total_values = [0 for _ in range(max_turns)]
    exact_shape_counts: Counter[str] = Counter()
    miss_reasons: list[Counter[str]] = [Counter() for _ in range(max_turns)]
    sample_lines: list[str] = []
    for trial in range(trials):
        deck = list(deck_cards)
        rng.shuffle(deck)
        initial_hand = deck[:6]
        draw_index = 6
        mulligan_targets = [
            alternative
            for alternatives in target_alternatives[:3]
            for alternative in alternatives
        ]
        kept = _choose_mulligan_keep(initial_hand, mulligan_targets, deck_cards)
        mulliganed = [card for card in initial_hand if card not in kept]
        deck_tail = deck[6:] + mulliganed
        deck = initial_hand + deck_tail
        hand = list(kept)
        while len(hand) < 6 and draw_index < len(deck):
            hand.append(deck[draw_index])
            draw_index += 1
        energy_boost_available = 0
        stage: list[dict[str, Any] | None] = [None, None, None]
        trial_shapes: list[str] = []
        prefix_success = True
        live_score_prefix_success = True
        combined_prefix_success = True
        for turn_index, goal_plan in enumerate(stage_goal_plans):
            target_shape = list(goal_plan.get("primary_shape", []))
            if turn_index > 0 and draw_index < len(deck):
                hand.append(deck[draw_index])
                draw_index += 1
            alternatives = list(goal_plan.get("accepted_shapes", [])) or [target_shape]
            prefer_energy_boost = any(alternative == [2, 4, 2] for alternative in alternatives)
            future_targets = [
                alternative
                for future_alternatives in target_alternatives[turn_index: min(len(target_alternatives), turn_index + 3)]
                for alternative in future_alternatives
            ]
            live_target = live_score_targets[turn_index] if turn_index < len(live_score_targets) else {}
            live_set_card, draw_index, _live_set_cards = _live_set_exchange(
                hand,
                deck,
                draw_index,
                prefer_energy_boost,
                future_targets,
                deck_cards,
                live_target if isinstance(live_target, dict) else None,
            )
            stage = _improve_persistent_stage(stage, hand, alternatives)
            bonus_costs: list[int] = []
            for card in stage:
                if not card:
                    continue
                for _ in range(int(card.get("low_cost_summon_n") or 0)):
                    if len(_stage_costs(stage)) + len(bonus_costs) < 3:
                        bonus_costs.append(2)
            costs = _stage_costs(stage)
            if live_set_card is not None and int(live_set_card.get("energy_boost_n") or 0) > 0 and turn_index <= 1:
                energy_boost_available += int(live_set_card.get("energy_boost_n") or 0)
            if energy_boost_available > 0 and target_shape == [2, 11, 2] and 11 not in costs:
                for card in hand:
                    if card.get("kind") == "member" and int(card.get("cost") or 0) == 11:
                        hand.remove(card)
                        replace_slots = _stage_slots_to_replace(stage, [2, 11, 2])
                        if replace_slots:
                            stage[replace_slots[0]] = card
                        costs = _stage_costs(stage)
                        energy_boost_available -= 1
                        break
            costs_with_bonus = sorted(costs + bonus_costs, reverse=True)
            draw_index = _apply_live_success_smoothing(hand, deck, draw_index, live_set_card)
            turn_success = any(_shape_meets_target(costs_with_bonus, sorted(alternative, reverse=True)) for alternative in alternatives)
            if turn_success:
                turn_hits[turn_index] += 1
            else:
                miss_reasons[turn_index][_miss_reason(costs_with_bonus, alternatives)] += 1
            prefix_success = prefix_success and turn_success
            if prefix_success:
                cumulative_hits[turn_index] += 1
            accepted_scores = live_target.get("accepted_scores", []) if isinstance(live_target, dict) else []
            live_score_card = _best_live_score_card(_live_set_cards)
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
        exact_shape_counts[" / ".join(trial_shapes)] += 1
        if len(sample_lines) < 5:
            sample_lines.append("T{}: ".format(trial + 1) + " -> ".join(trial_shapes))

    return {
        "schema_version": 1,
        "model": "max_target_probability_heuristic",
        "trials": trials,
        "seed": seed,
        "max_turns": max_turns,
        "mulligan_policy": "maximize turn 1-3 target access; keep scarce target members and redraw replaceable low-priority cards",
        "success_definition": "turn hit checks only that turn's current stage shape; cumulative requires all previous turn targets to have been met in sequence",
        "decision_policy": [
            "Initial hand is six cards from the shuffled deck.",
            "Mulligan scores cards against accepted turn 1-3 targets; scarce target costs such as a 3-copy 10-cost member are kept more strongly.",
            "Abundant 2-cost members are kept only up to the near-term need because extra copies are comparatively easy to redraw.",
            "Live cards with energy-boost text are kept when they are needed for a bridge route, but are protected from live-set exchange before that route.",
            "Cards with low turn 1-3 target value are redrawn back to six cards.",
            "During live set, up to three cards may be exchanged, including non-live cards.",
            "Live set exchanges low-priority or replaceable cards to dig toward the nearest target; it does not automatically set every live card.",
            "Live score targets are inferred from live cards actually present in the deck; the hit check uses the highest-score live card selected during that turn's live-set exchange.",
            "If the turn has a Daydream-like 2-4-2 bridge, an energy-boost live is preferred as the live-set card for that turn only.",
            "Member placement then chooses the available hand combination that best covers the turn's accepted target shapes without capping above-target members: higher than target first, exact target second, then the largest available fallback.",
            "After live success, draw effects on the live-set card are modeled as hand smoothing for the following turn.",
        ],
        "effect_assumptions": [
            "up to three cards are live-set exchanged before member planning, and each exchanged card draws one replacement",
            "live draw effects are modeled as hand smoothing after each turn",
            "Daydream-like energy boost live cards count as the 2-4-2 alternative bridge only when selected as the live-set card",
            "low-cost stage summon effects add an extra virtual 2-cost member for progression matching",
        ],
        "recommended_early": recommended_early,
        "recommended_late": recommended_late,
        "target_turns": target_turns,
        "target_alternatives": target_alternatives,
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
    lines.extend(["", "## Progressions", ""])
    for item in report.get("progressions", []) or []:
        if not isinstance(item, dict):
            continue
        turns = " / ".join("-".join(str(v) for v in turn) for turn in item.get("turns", []))
        missing = item.get("missing_costs") if isinstance(item.get("missing_costs"), dict) else {}
        missing_text = "なし" if not missing else ", ".join(f"{k}コストx{v}" for k, v in sorted(missing.items(), key=lambda part: int(part[0])))
        lines.append(f"- {item.get('label')}: score={item.get('score')} coverage={item.get('coverage')} turns={turns} missing={missing_text}")
    lines.extend(["", "## Special Signals", ""])
    for key, label in (
        ("cost_reduction", "コスト軽減"),
        ("special_baton", "特殊バトンタッチ"),
        ("high_cost_anchor", "15+高コスト"),
    ):
        items = signals.get(key, []) if isinstance(signals.get(key, []), list) else []
        lines.append(f"### {label}")
        if not items:
            lines.append("- なし")
        for item in items:
            if isinstance(item, dict):
                lines.append(f"- {item.get('card_no')} {item.get('name')} x{item.get('count')} cost={item.get('cost')}")
        lines.append("")
    if trial_result:
        lines.extend(["## Trial Result", ""])
        lines.append(f"- model: `{trial_result.get('model', '')}`")
        lines.append(f"- trials: {trial_result.get('trials')}")
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
        hit_rates = trial_result.get("turn_hit_rates", []) or []
        averages = trial_result.get("average_stage_costs", []) or []
        lines.extend(["", "### Turn Summary", ""])
        lines.append("- `hit_rate` はそのターン単独の盤面形達成率、`cumulative` はT1からそのターンまで連続で達成した率。主に比較する値は `cumulative`。")
        combined_rates = trial_result.get("combined_cumulative_hit_rates", []) or []
        for index, target in enumerate(trial_result.get("target_turns", []) or [], start=1):
            hit = hit_rates[index - 1] if index - 1 < len(hit_rates) else ""
            cumulative_rates = trial_result.get("cumulative_hit_rates", []) or []
            cumulative = cumulative_rates[index - 1] if index - 1 < len(cumulative_rates) else ""
            combined = combined_rates[index - 1] if index - 1 < len(combined_rates) else ""
            avg = averages[index - 1] if index - 1 < len(averages) else ""
            lines.append(f"- T{index}: target={'-'.join(str(v) for v in target)} hit_rate={hit} cumulative={cumulative} combined_cumulative={combined} avg_stage_cost={avg}")
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
    return "\n".join(lines).rstrip() + "\n"


def build_autoplay_deck_report(
    rows: list[dict[str, str]],
    card_lookup: CardLookup,
) -> dict[str, Any]:
    curve = build_deck_curve(rows, card_lookup)
    progressions = [
        evaluate_progression(curve, template)
        for template in COST_PROGRESSIONS
    ]
    progressions = [
        item for item in progressions
        if not item.get("unavailable_costs")
    ]
    progressions.sort(key=lambda item: (-float(item.get("score") or 0), str(item.get("key") or "")))
    return {
        "schema_version": 1,
        "model_stage": "stage1_policy_template",
        "curve": curve,
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
