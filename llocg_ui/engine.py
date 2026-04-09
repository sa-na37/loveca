# -*- coding: utf-8 -*-
# BUILD_TAG: hime_faceup_live_set_limit_20260409a
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
    {"id": "draw_n_discard_m", "pattern": r"^カードを(?P<n>\d+)枚引き、手札を(?P<m>\d+)枚控え室に置く。$", "op": "draw_then_discard"},
    {"id": "discard_hand_n", "pattern": r"^手札を(?P<n>\d+)枚控え室に置く。$", "op": "discard_from_hand"},
    {"id": "retrieve_waiting_live_n", "pattern": r"^自分の控え室からライブカードを(?P<n>\d+)枚手札に加える。$", "op": "retrieve_from_waiting_room", "card_kind": "LIVE"},
    {"id": "retrieve_waiting_member_n", "pattern": r"^自分の控え室からメンバーカードを(?P<n>\d+)枚手札に加える。$", "op": "retrieve_from_waiting_room", "card_kind": "MEMBER"},
    {"id": "retrieve_waiting_live_group_n", "pattern": r"^自分の控え室から『(?P<group>[^』]+)』のライブカードを(?P<n>\d+)枚手札に加える。$", "op": "retrieve_from_waiting_room", "card_kind": "LIVE"},
    {"id": "look_top_k_choose_1_rest_waiting", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から1枚を手札に加え、残りを控え室に置く。$", "op": "look_top_choose"},
        {"id": "look_top_k_reorder_keep_any_rest_waiting", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から好きな枚数を好きな順番でデッキの上に置き、残りを控え室に置く。$", "op": "look_top_reorder_keep_any"},
    {"id": "topdeck_green_any_upto1", "pattern": r"^自分の控え室からカードを1枚までデッキの一番上に置く。$", "op": "topdeck_from_green", "card_kind": "ANY", "allow_less": True},
    {"id": "topdeck_green_member_n", "pattern": r"^自分の控え室にあるメンバーカード(?P<n>\d+)枚を好きな順番でデッキの一番上に置く。$", "op": "topdeck_from_green", "card_kind": "MEMBER", "allow_less": False},
    {"id": "topdeck_green_live_group_upto_n", "pattern": r"^自分の控え室にある『(?P<group>[^』]+)』のライブカードを(?P<n>\d+)枚まで好きな順番でデッキの上に置く。$", "op": "topdeck_from_green", "card_kind": "LIVE", "allow_less": True},
    {"id": "energy_put_wait_n", "pattern": r"^自分のエネルギーデッキから、エネルギーカードを(?P<n>\d+)枚ウェイト状態で置く。$", "op": "energy_put_wait"},
    {"id": "energy_activate_n", "pattern": r"^エネルギーを(?P<n>\d+)枚アクティブにする。$", "op": "energy_activate"},
    {"id": "gain_blade_until_end_live", "pattern": r"^ライブ終了時まで、(?P<blades>(?:<\(ブレード\)>)+)を得る。$", "op": "gain_blade_until_end_live"},
    {"id": "activate_stage_member_upto1", "pattern": r"^自分のステージにいるメンバーを1人までアクティブにする。$", "op": "activate_stage_member"},
    # Fixed-color hearts (and mixed hearts+blades): e.g. "ライブ終了時まで、<(黄)><(黄)>を得る。"
    # Must come AFTER gain_blade_until_end_live so pure-blade still matches first.
    {"id": "gain_icons_until_end_live", "pattern": r"^ライブ終了時まで、(?P<icons>(?:<\([^)]+\)>)+)を得る。$", "op": "gain_icons_until_end_live"},
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
    # Self-wait (as effect): "このメンバーをウェイトにする。"
    {"id": "set_self_wait_member", "pattern": r"^このメンバーをウェイトにする。$", "op": "set_self_wait"},
    # Opponent wait: "相手のステージにいるコストN以下のメンバーをM人までウェイトにする。"
    {"id": "set_opponent_wait_upto_n", "pattern": r"^相手のステージにいるコスト(?P<cost>\d+)以下のメンバーを(?P<max_n>\d+)人までウェイト(?:状態に)?にする。$", "op": "set_opponent_wait"},
    # Opponent wait exactly 1: "相手のステージにいるコストN以下のメンバー1人をウェイトにする。"
    {"id": "set_opponent_wait_exactly1", "pattern": r"^相手のステージにいるコスト(?P<cost>\d+)以下のメンバー1人をウェイトにする。$", "op": "set_opponent_wait_exactly1"},
    # Opponent wait all: "相手のステージにいるすべてのコストN以下のメンバーをウェイトにする。"
    {"id": "set_opponent_wait_all_cost", "pattern": r"^相手のステージにいるすべてのコスト(?P<cost>\d+)以下のメンバーをウェイトにする。$", "op": "set_opponent_wait"},
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
    # 3-way split: 1->hand, 1->deck top, 1->green
    {"id": "look_top_3_split", "pattern": r"^自分のデッキの上からカードを(?P<k>\d+)枚見る。その中から1枚を手札に加え、1枚をデッキの上に置き、1枚を控え室に置く。$", "op": "look_top_3way_split"},
    # Retrieve from yell reveals: group-filtered
    {"id": "retrieve_yell_group_any", "pattern": r"^エールにより公開された自分のカードの中から、『(?P<group>[^』]+)』のカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "ANY"},
    # Retrieve from yell reveals: type-filtered (LIVE or MEMBER)
    {"id": "retrieve_yell_live", "pattern": r"^エールにより公開された自分のカードの中から、ライブカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "LIVE"},
    {"id": "retrieve_yell_member", "pattern": r"^エールにより公開された自分のカードの中から、メンバーカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "MEMBER"},
    # Retrieve from yell reveals: group+type (e.g. 『μ's』のメンバーカード)
    {"id": "retrieve_yell_group_member", "pattern": r"^エールにより公開された自分のカードの中から、『(?P<group>[^』]+)』のメンバーカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "MEMBER"},
    {"id": "retrieve_yell_group_live", "pattern": r"^エールにより公開された自分のカードの中から、『(?P<group>[^』]+)』のライブカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "LIVE"},
    # Retrieve from yell reveals: cost2-member OR score2-live (e.g. PL!HS-PR-027, PL!N-PR-021, PL!SP-PR-016)
    {"id": "retrieve_yell_cost2member_or_score2live", "pattern": r"^エールにより公開された自分のカードの中から、コスト(?P<cost_lim>\d+)以下のメンバーカードか、スコア(?P<score_lim>\d+)以下のライブカードを1枚手札に加える。$", "op": "retrieve_from_yell", "card_kind": "COST_MEMBER_OR_SCORE_LIVE"},
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
    """Parse <(色)> icon string into color -> count dict (excluding blades)."""
    counts: Dict[str, int] = {}
    for m in re.finditer(r'<\(([^)]+)\)>', str(icon_blob or '')):
        jp = m.group(1)
        col = _HEART_ICON_COLOR_MAP.get(jp)
        if col:
            counts[col] = counts.get(col, 0) + 1
    return counts


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

    for r in _EFFECT_RULES_COMPILED:
        m = r["re"].match(s)
        if m:
            gd = {k: v for k, v in m.groupdict().items() if v is not None}
            return (r, gd)
    return None


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

    # Special-case: Emma Verde bp3-008 activated ability
    if _canon_cardno(getattr(ci, 'cardnumber', '') or '') == _EMMA_BP3_008_CN_CANON:
        key = f"{pos}:{_EMMA_BP3_008_CN_CANON}:emma_bp3_008_activate"
        used = int((getattr(gs, 'used_this_turn', {}) or {}).get(key, 0) or 0)
        if used >= 1:
            return False
        return bool(_emma_bp3_008_wait_candidates(gs, cards_db, pos))

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
            if not is_body_cost and not _match_effect_template(eff):
                continue
            # energy cost check
            need_e = _parse_energy_cost(cost)
            if need_e > 0 and int(gs.energy_active or 0) < need_e:
                continue
            # special cost: move active energy to under
            if _cost_move_active_energy_to_under(cost) and int(gs.energy_active or 0) < 1:
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
            ok_any = True
        if ok_any:
            return True
    # legacy fallback (only when this card has no matchable activated ability templates)
    if not _has_matchable_activated(ci):
        if _has_green_live_take_ability(ci) or _has_green_member_take_ability(ci) or _has_sacrifice_ability(ci):
            return True


    return False

def _count_blade_icons_from_tagblob(s: str) -> int:
    return (s or "").count("<(ブレード)>")


def _is_live_ci(ci: Optional[CardInfo]) -> bool:
    if not ci:
        return False
    return "LIVE" in str(getattr(ci, 'type', '') or '').upper() or "ライブ" in str(getattr(ci, 'type', '') or '')


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


def _enqueue_choose_from_green(gs: 'GameState', cards_db: Dict[str, CardInfo], kind: str, n: int = 1, group: str = "") -> None:
    n = int(n or 1)
    cands = _green_candidates(gs, cards_db, kind=kind, group=group)
    if not cands:
        gs.log.append(f'[INFO] retrieve: no {kind} in waiting room')
        return
    if len(cands) == 1:
        pick = cands[0]
        gs.green_room.remove(pick)
        gs.hand.append(pick)
        gs.log.append(f'[AUTO] retrieved {kind} {pick} (only choice)')
        if n > 1:
            _enqueue_choose_from_green(gs, cards_db, kind=kind, n=n-1, group=group)
        return
    gs.pending.append({
        'kind': f'choose_{kind.lower()}_from_green',
        'text': f'控え室の{("ライブ" if kind=="LIVE" else "メンバー")}カードを1枚手札に加える',
        'options': cands,
        'want_kind': kind,
        'want_group': group,
        'remaining_picks': n,
    })
    gs.log.append(f'[PENDING] choose {kind} from waiting room ({len(cands)} candidates, picks={n})')




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
        if group and group not in str(getattr(ci, 'group', '') or ''):
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
) -> None:
    """Look at top-k cards, let user pick 1 matching filter (optionally), rest to green."""
    filter_names = filter_names or []
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
        if filter_kind:
            t = str(getattr(ci, 'type', '') or '').upper()
            if filter_kind == 'LIVE' and 'LIVE' not in t:
                return False
            if filter_kind == 'MEMBER' and 'MEMBER' not in t:
                return False
        if filter_group:
            if filter_group not in str(getattr(ci, 'group', '') or ''):
                return False
        if filter_names:
            name = str(getattr(ci, 'name', '') or getattr(ci, 'cardname', '') or cn)
            if not any(n in name for n in filter_names):
                return False
        return True

    candidates = [cn for cn in pool if _matches(cn)]

    label_parts = []
    if filter_kind:
        label_parts.append({'LIVE': 'ライブカード', 'MEMBER': 'メンバーカード'}.get(filter_kind, filter_kind))
    if filter_group:
        label_parts.append(f'『{filter_group}』')
    if filter_names:
        label_parts.append('・'.join(f'「{n}」' for n in filter_names))
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
        _enqueue_choose_from_green(gs, cards_db, kind=kind, n=n, group=group)
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



    if op == 'look_top_choose':
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
        _enqueue_choose_from_topk_filtered(gs, k, rng, cards_db,
                                           filter_kind=kind, filter_group=group,
                                           filter_names=names, optional=optional)
        return

    if op == 'look_top_3way_split':
        k = int(gd.get('k', 0) or 0)
        _enqueue_look_top_3way_split(gs, k, rng)
        return
    if op == 'look_top_reorder_keep_any':
        k = int(gd.get('k', 0) or 0)
        _enqueue_reorder_from_topk_keep_any(gs, k, rng)
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
        opts = [p for p in ('L','C','R') if gs.stage.get(p)]
        if not opts:
            gs.log.append('[INFO] activate_member: no member on stage')
            return
        gs.pending.append({
            'kind': 'choose_stage_member_to_activate',
            'text': 'ステージのメンバーを1人までアクティブにする（対象を選択）',
            'options': opts,
        })
        gs.log.append('[PENDING] choose stage member to activate')
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
        src_cn = str((ctx or {}).get('source_cn', '') or '')
        gs.log.append(f'[MANUAL] 相手のステージにいるコスト{cost_lim}以下のメンバーを{max_n}人までウェイトにする（手動で処理してください）')
        gs.pending.append({
            'kind': 'opponent_wait_notify',
            'text': f'【相手への効果】コスト{cost_lim}以下のメンバーを{max_n}人までウェイトにする\n（相手の盤面で手動で処理してください）',
            'source_cn': src_cn,
            'options': ['ok'],
        })
        return

    if op == 'set_opponent_wait_exactly1':
        cost_lim = int(gd.get('cost', 99) or 99)
        src_cn = str((ctx or {}).get('source_cn', '') or '')
        gs.log.append(f'[MANUAL] 相手のステージにいるコスト{cost_lim}以下のメンバー1人をウェイトにする（手動で処理してください）')
        gs.pending.append({
            'kind': 'opponent_wait_notify',
            'text': f'【相手への効果】コスト{cost_lim}以下のメンバー1人をウェイトにする\n（相手の盤面で手動で処理してください）',
            'source_cn': src_cn,
            'options': ['ok'],
        })
        return

    if op == 'set_opponent_wait_self_choice':
        src_cn = str((ctx or {}).get('source_cn', '') or '')
        gs.log.append('[MANUAL] 相手は自身のステージのアクティブメンバー1人をウェイトにする（手動で処理してください）')
        gs.pending.append({
            'kind': 'opponent_wait_notify',
            'text': '【相手への効果】相手は自身のステージのアクティブメンバー1人をウェイトにする\n（相手の盤面で手動で処理してください）',
            'source_cn': src_cn,
            'options': ['ok'],
        })
        return

    if op == 'retrieve_from_yell':
        kind = str(rule.get('card_kind', '') or '').upper() or 'ANY'
        group = str(gd.get('group', '') or '')
        cost_lim = int(gd.get('cost_lim', 99) or 99)
        score_lim = int(gd.get('score_lim', 99) or 99)
        src = str((ctx or {}).get('source_cn', '') or '')
        pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
        # collect candidates from resolve_zone first, then green_room (already sent there by ack)
        cands: List[str] = []
        seen: set = set()
        for zone_name in ('resolve_zone', 'green_room'):
            z = getattr(gs, zone_name, None)
            if not isinstance(z, list):
                continue
            for cn2 in z:
                canon2 = _canon_cardno(str(cn2 or ''))
                if canon2 in seen:
                    continue
                # only consider cards that were part of yell reveals this live
                if canon2 not in [_canon_cardno(x) for x in pool]:
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
                    if _is_member_ci(ci2) and int(getattr(ci2, 'cost', 0) or 0) <= cost_lim:
                        ok2 = True
                    if _is_live_ci(ci2) and int(getattr(ci2, 'score', 0) or 0) <= score_lim:
                        ok2 = True
                    if not ok2:
                        continue
                if group and (group not in str(getattr(ci2, 'group', '') or '')):
                    continue
                seen.add(canon2)
                cands.append(cn2)
        if not cands:
            gs.log.append(f'[INFO] retrieve_from_yell: no matching card in yell reveals (kind={kind} group={group})')
            return
        label = f'{src}[ライブ成功時]: エールで公開されたカードから1枚手札に加える'
        if kind == 'LIVE':
            label += '（ライブカード）'
        elif kind == 'MEMBER':
            label += '（メンバーカード）'
        elif kind == 'COST_MEMBER_OR_SCORE_LIVE':
            label += f'（コスト{cost_lim}以下のメンバーかスコア{score_lim}以下のライブ）'
        if group:
            label += f'（{group}）'
        gs.pending.append({
            'kind': 'pick_from_yell',
            'text': label,
            'options': list(cands),
            'source_cn': src,
        })
        gs.log.append(f'[PENDING] retrieve_from_yell: {len(cands)} candidates')
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
            for slot in gs.stage.values():
                if slot:
                    ci2 = _get_card(cards_db, slot.cardnumber)
                    if ci2 and int(getattr(ci2, 'cost', 0) or 0) >= n:
                        met = True; break
        elif cond == 'success_nonempty':
            met = len(gs.success_pile) > 0
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


def try_apply_effect_template(gs: 'GameState', rng: random.Random, cards_db: Dict[str, CardInfo], effect_text: str, ctx: Dict[str, Any]) -> bool:
    """Apply an effect_template using the embedded regex rules.

    Also supports a small subset of "mode/choice" wrappers used by key cards.
    """
    text = str(effect_text or '').strip()
    if not text:
        return False

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


def _enqueue_choose_effects_from_ability(gs: 'GameState', cards_db: Dict[str, CardInfo], ab: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
    """Handle 'mode' style abilities where the choice header and options are split across clauses.

    Typical pattern (Daydream Mermaid etc.):
      clause0: '以下から1つを選ぶ。...代わりに1つ以上を選ぶ。'
      clause1+: individual option effects (as separate clauses)
    """
    try:
        clauses = ab.get('clauses', [])
    except Exception:
        clauses = []
    if not isinstance(clauses, list) or not clauses:
        return False

    # Find the first 'choose' header clause
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
        return False

    # Collect option effect texts from subsequent clauses
    opts: List[str] = []
    for cl in clauses[header_i+1:]:
        if not isinstance(cl, dict):
            continue
        eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
        if not eff:
            continue
        # ignore bullet prefix if any remained
        if eff.startswith('・'):
            eff = eff[1:].strip()
        if eff:
            opts.append(eff)

    if not opts:
        return False

    # Determine selection range
    max_pick = 1
    mcond = re.search(r"成功ライブカード置き場に『(?P<g>[^』]+)』のカードがある場合、代わりに1つ以上を選ぶ。", header_text)
    if mcond:
        g = str(mcond.group('g') or '').strip()
        if g and _success_has_group(gs, cards_db, g):
            max_pick = len(opts)

    src = str((ctx or {}).get('source_cn', '') or '')
    ttl = src if src else '効果'
    msg = f"{ttl}: 以下から{'1つ以上' if max_pick>1 else '1つ'}を選ぶ"

    options = list(opts)
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
    gs.log.append(f"[PENDING] choose_effects: {ttl} opts={len(opts)} max={max_pick}")
    return True


def _iter_activated_abilities(ci: Optional[CardInfo]):
    if not ci or not getattr(ci, 'abilities', None):
        return []
    out = []
    for ab in ci.abilities:
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
    if not ci or not getattr(ci, 'abilities', None):
        return []
    out = []
    for ab in ci.abilities:
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
    success_zone: List[str] = field(default_factory=list)  # 成功ライブカード置き場
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
    last_attempt_ok: bool = False
    need_live_success_triggers: bool = False
    need_success_store_choice: bool = False

    # live-start buff (until end of live): for each card in success storage, gain chosen heart
    success_zone_heart_color: str = ""  # e.g., 'pink'/'yellow'/'purple'
    deck_refreshed_this_turn: bool = False
    butterfly_paid_this_live: int = 0
    tsunagaru_connect_bonus_this_live: int = 0
    vivid_world_blue_mode_this_live: bool = False
    vivid_world_bonus_this_live: int = 0
    live_start_resolved_set_idxs: List[int] = field(default_factory=list)
    next_live_set_limit_reduction: int = 0
    current_live_set_limit: int = 3


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
            stage_snap[k] = {"cardnumber": slot.cardnumber, "active": bool(slot.active), "temp_blade": int(getattr(slot, "temp_blade", 0) or 0), "temp_hearts": dict(getattr(slot, "temp_hearts", {}) or {}), "temp_until": str(getattr(slot, "temp_until", "") or ""), "energy_under": int(getattr(slot, "energy_under", 0) or 0), "heart_replace_color": str(getattr(slot, "heart_replace_color", "") or "")}

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
        "success_zone": list(getattr(gs, "success_zone", []) or []),
        "resolve_zone": list(gs.resolve_zone),
        "pending": json.loads(json.dumps(gs.pending)) if gs.pending else [],
        "live_start_prompted": bool(gs.live_start_prompted),
        "turn": int(gs.turn),
        "used_this_turn": dict(getattr(gs, "used_this_turn", {}) or {}),
        "last_attempt_lives": list(getattr(gs, 'last_attempt_lives', []) or []),
        "last_attempt_ok": bool(getattr(gs, 'last_attempt_ok', False)),
        "need_live_success_triggers": bool(getattr(gs, 'need_live_success_triggers', False)),
        "need_success_store_choice": bool(getattr(gs, 'need_success_store_choice', False)),

        # end-of-live buffs
        "success_zone_heart_color": str(getattr(gs, 'success_zone_heart_color', '') or ''),
        "deck_refreshed_this_turn": bool(getattr(gs, 'deck_refreshed_this_turn', False)),
        "butterfly_paid_this_live": int(getattr(gs, "butterfly_paid_this_live", 0) or 0),
        "tsunagaru_connect_bonus_this_live": int(getattr(gs, "tsunagaru_connect_bonus_this_live", 0) or 0),
        "vivid_world_blue_mode_this_live": bool(getattr(gs, "vivid_world_blue_mode_this_live", False)),
        "vivid_world_bonus_this_live": int(getattr(gs, "vivid_world_bonus_this_live", 0) or 0),
        "live_start_resolved_set_idxs": list(getattr(gs, "live_start_resolved_set_idxs", []) or []),
        "next_live_set_limit_reduction": int(getattr(gs, "next_live_set_limit_reduction", 0) or 0),
        "current_live_set_limit": int(getattr(gs, "current_live_set_limit", 3) or 3),
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
            stage_new[k] = StageSlot(cardnumber=str(v.get("cardnumber", "")), active=bool(v.get("active", True)), temp_blade=_safe_int(v.get("temp_blade", 0), 0), temp_hearts=dict(v.get("temp_hearts", {}) or {}), temp_until=str(v.get("temp_until", "") or ""), energy_under=_safe_int(v.get("energy_under", 0), 0), heart_replace_color=str(v.get("heart_replace_color", "") or ""))
    gs.stage = stage_new

    gs.green_room = list(snap.get("green_room", gs.green_room))
    gs.set_zone = list(snap.get("set_zone", gs.set_zone))
    gs.success_zone = list(snap.get("success_zone", getattr(gs, "success_zone", [])))
    gs.resolve_zone = list(snap.get("resolve_zone", gs.resolve_zone))
    gs.pending = list(snap.get("pending", gs.pending) or [])
    gs.live_start_prompted = bool(snap.get("live_start_prompted", gs.live_start_prompted))
    gs.turn = int(snap.get("turn", gs.turn))
    try:
        gs.used_this_turn = {str(k): int(v) for k, v in (snap.get("used_this_turn", {}) or {}).items()}
    except Exception:
        gs.used_this_turn = {}

    gs.last_attempt_lives = list(snap.get('last_attempt_lives', getattr(gs, 'last_attempt_lives', []) or []))
    gs.last_attempt_ok = bool(snap.get('last_attempt_ok', getattr(gs, 'last_attempt_ok', False)))
    gs.need_live_success_triggers = bool(snap.get('need_live_success_triggers', getattr(gs, 'need_live_success_triggers', False)))
    gs.need_success_store_choice = bool(snap.get('need_success_store_choice', getattr(gs, 'need_success_store_choice', False)))

    gs.success_zone_heart_color = str(snap.get('success_zone_heart_color', getattr(gs, 'success_zone_heart_color', '') or '') or '')
    gs.deck_refreshed_this_turn = bool(snap.get('deck_refreshed_this_turn', getattr(gs, 'deck_refreshed_this_turn', False)))
    gs.butterfly_paid_this_live = int(snap.get('butterfly_paid_this_live', getattr(gs, 'butterfly_paid_this_live', 0) or 0) or 0)
    gs.tsunagaru_connect_bonus_this_live = int(snap.get('tsunagaru_connect_bonus_this_live', getattr(gs, 'tsunagaru_connect_bonus_this_live', 0) or 0) or 0)
    gs.vivid_world_blue_mode_this_live = bool(snap.get('vivid_world_blue_mode_this_live', getattr(gs, 'vivid_world_blue_mode_this_live', False)))
    gs.vivid_world_bonus_this_live = int(snap.get('vivid_world_bonus_this_live', getattr(gs, 'vivid_world_bonus_this_live', 0) or 0) or 0)
    try:
        gs.live_start_resolved_set_idxs = [int(x) for x in (snap.get('live_start_resolved_set_idxs', getattr(gs, 'live_start_resolved_set_idxs', []) or []) or [])]
    except Exception:
        gs.live_start_resolved_set_idxs = []
    gs.next_live_set_limit_reduction = int(snap.get('next_live_set_limit_reduction', getattr(gs, 'next_live_set_limit_reduction', 0) or 0) or 0)
    gs.current_live_set_limit = int(snap.get('current_live_set_limit', getattr(gs, 'current_live_set_limit', 3) or 3) or 3)



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
    # reset last LIVE attempt (timing helpers)
    gs.last_attempt_lives = []
    gs.last_attempt_ok = False
    gs.need_live_success_triggers = False
    gs.need_success_store_choice = False
    gs.live_start_resolved_set_idxs = []
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
    """Return True if any slot on stage (self) has a member with cost >= 13."""
    for slot in (gs.stage or {}).values():
        if not slot:
            continue
        ci = _get_card(cards_db, slot.cardnumber)
        if not ci:
            continue
        if _is_live_ci(ci):
            continue
        try:
            if int(getattr(ci, 'cost', 0) or 0) >= 13:
                return True
        except Exception:
            pass
    return False


def _stage_has_other_higher_cost_member(gs: 'GameState', cards_db: Dict[str, CardInfo], self_pos: str, self_cost: int) -> bool:
    """Return True if another stage member has cost strictly greater than self_cost."""
    try:
        for pos, slot in (gs.stage or {}).items():
            if pos == self_pos or not slot:
                continue
            ci = _get_card(cards_db, getattr(slot, 'cardnumber', ''))
            if not ci or _is_live_ci(ci):
                continue
            try:
                if int(getattr(ci, 'cost', 0) or 0) > int(self_cost or 0):
                    return True
            except Exception:
                pass
    except Exception:
        pass
    return False



def _stage_has_all_distinct_hasunosora_members(gs: 'GameState', cards_db: Dict[str, CardInfo]) -> bool:
    """Return True if all three stage areas are occupied by Hasunosora members with distinct names."""
    names = []
    try:
        for pos in ('L', 'C', 'R'):
            slot = (gs.stage or {}).get(pos)
            if not slot or not getattr(slot, 'cardnumber', ''):
                return False
            ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
            if not ci or _is_live_ci(ci):
                return False
            if '蓮ノ空' not in str(getattr(ci, 'group', '') or ''):
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


def _slot_always_hearts_bonus(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, slot) -> Dict[str, int]:
    """Return always-on heart bonus currently attached to a stage slot."""
    try:
        if not slot or not getattr(slot, 'cardnumber', ''):
            return {}
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci or _is_live_ci(ci):
            return {}
        bonus: Dict[str, int] = {}
        # PL!-bp4-002 絢瀬絵里: if any LIVE in set_zone has neither live-start nor live-success ability, purple +2
        try:
            if _canon_cardno(getattr(slot, 'cardnumber', '') or '') == 'PL!-bp4-002':
                found_plain_live = False
                for cn_live in list(getattr(gs, 'set_zone', []) or []):
                    ci_live = _get_card(cards_db, cn_live)
                    if not ci_live or not _is_live_ci(ci_live):
                        continue
                    if not _live_has_start_or_success_ability(ci_live):
                        found_plain_live = True
                        break
                if found_plain_live:
                    bonus['purple'] = int(bonus.get('purple', 0) or 0) + 2
        except Exception:
            pass
        return {str(k): int(v) for k, v in bonus.items() if int(v or 0) != 0}
    except Exception:
        return {}


def _slot_always_score_bonus(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, slot) -> int:
    """Return always-on total score bonus granted by a stage member slot."""
    try:
        if not slot or not getattr(slot, 'cardnumber', ''):
            return 0
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci or _is_live_ci(ci):
            return 0
        bonus = 0
        # PL!HS-bp1-003 乙宗梢: all three stage areas are Hasunosora members with distinct names -> total score +1
        try:
            if _canon_cardno(getattr(slot, 'cardnumber', '') or '') == 'PL!HS-bp1-003':
                if _stage_has_all_distinct_hasunosora_members(gs, cards_db):
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
        # 常時 BODY: 自分か相手のステージにコスト13以上のメンバーがいる場合+2
        has_cost13 = _stage_has_cost13_plus_member(gs, cards_db)
        if has_cost13 and _has_body_always_cost13_blade_bonus(c):
            bonus += 2
        # 常時 BODY: ステージのメンバーがちょうど2人のとき+1
        has_exactly2 = (_stage_member_count(gs, cards_db) == 2)
        if has_exactly2 and _has_body_always_2member_blade_heart(c):
            bonus += 1
        # Love wing bell: success_zone にある間、センターの μ's メンバーに +1/copy
        try:
            if pos == 'C' and ("μ's" in str(getattr(c, 'group', '') or '')):
                bonus += int(_love_wing_bell_success_bonus_count(gs) or 0)
        except Exception:
            pass
        # PL!-sd1-001 高坂穂乃果: 成功ライブカード置き場1枚につき +1 blade
        try:
            if _canon_cardno(getattr(slot, 'cardnumber', '') or '') == 'PL!-sd1-001':
                bonus += len(list(getattr(gs, 'success_zone', []) or []))
        except Exception:
            pass
        # PL!HS-bp2-002 村野さやか: 自分より高コストのメンバーがいる場合 +3 blade
        try:
            if _canon_cardno(getattr(slot, 'cardnumber', '') or '') == 'PL!HS-bp2-002':
                self_cost = int(getattr(c, 'cost', 0) or 0)
                if _stage_has_other_higher_cost_member(gs, cards_db, pos, self_cost):
                    bonus += 3
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
        under_b = int(getattr(slot, "energy_under", 0) or 0) if _has_under_energy_blade_bonus(c) else 0
        always_b = _slot_always_blade_bonus(gs, cards_db, pos, slot)
        s += base_b + temp_b + under_b + always_b
    # Lanzhu (PL!N-bp1-012) live-only bonus: +2 blade per copy when condition met
    try:
        n_lz = _lanzhu_bp1_012_live_bonus_count(gs, cards_db)
    except Exception:
        n_lz = 0
    if n_lz > 0:
        s += 2 * int(n_lz)
    return s



def _lanzhu_bp1_012_live_bonus_count(gs: "GameState", cards_db: Dict[str, CardInfo]) -> int:
    """Return how many active Lanzhu (PL!N-bp1-012) provide the live-only bonus now.

    Condition from card text:
      - If you have 3+ cards in the live card storage (set_zone),
        and among them there is at least one Nijigasaki LIVE card,
        gain <(ALL)><(ALL)><(ブレード)><(ブレード)>.
    """
    try:
        live_cards = list(getattr(gs, "set_zone", []) or [])
    except Exception:
        live_cards = []
    if len(live_cards) < 3:
        return 0

    has_niji_live = False
    for cn in live_cards:
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if is_live_type(getattr(ci, "type", "")) and ("虹ヶ咲" in str(getattr(ci, "group", "") or "")):
            has_niji_live = True
            break
    if not has_niji_live:
        return 0

    n = 0
    for p in ("L", "C", "R"):
        slot = (gs.stage or {}).get(p)
        if not slot or not getattr(slot, "active", False):
            continue
        if _canon_cardno(getattr(slot, "cardnumber", "") or "") == "PL!N-bp1-012":
            n += 1
    return int(n)

def _love_wing_bell_success_bonus_count(gs: "GameState") -> int:
    """Return how many copies of Love wing bell (PL!-bp4-020) are in success_zone."""
    n = 0
    for cn in list(getattr(gs, 'success_zone', []) or []):
        try:
            canon = _canon_cardno(cn)
        except Exception:
            canon = str(cn or '')
        if canon == 'PL!-bp4-020':
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
    # Lanzhu (PL!N-bp1-012) live-only bonus: +2 <(ALL)> hearts per copy when condition met
    try:
        n_lz = _lanzhu_bp1_012_live_bonus_count(gs, cards_db)
    except Exception:
        n_lz = 0
    if n_lz > 0:
        pool['all'] = pool.get('all', 0) + 2 * int(n_lz)

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


def _emma_bp3_008_live_start_candidates(gs: GameState, cards_db: Dict[str, CardInfo], src_pos: str) -> List[str]:
    out: List[str] = []
    src_pos = str(src_pos or '').upper()
    for pos in ('L', 'C', 'R'):
        if pos == src_pos:
            continue
        slot = (gs.stage or {}).get(pos)
        if not slot or bool(getattr(slot, 'active', False)):
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
        pool = _apply_vivid_world_blue_mode(pool)
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
    n = t.count("<(ブレード)>")
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
    """Detect a specific activated ability we actually implement.

    PL!N-sd1-006: put this MEMBER into Green Room, then take 1 MEMBER from Green Room to hand.
    """
    if not ci:
        return False
    return str(getattr(ci, "cardnumber", "") or "") == "PL!N-sd1-006"


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



def _neo_sky_stage_ready(gs: GameState, cards_db: Dict[str, CardInfo]) -> bool:
    total_cost = 0
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'cardnumber', ''):
            return False
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci:
            return False
        if not _is_member_ci(ci):
            return False
        if '虹ヶ咲' not in str(getattr(ci, 'group', '') or ''):
            return False
        try:
            total_cost += int(getattr(ci, 'cost', 0) or 0)
        except Exception:
            total_cost += 0
    return total_cost >= 20


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


def _enqueue_choose_top_keep_one(gs: 'GameState', k: int, label: str = '') -> None:
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
        return
    gs.pending.insert(0, {
        'kind': 'choose_top_keep_one',
        'text': f'{label} デッキ上から見たカードのうち1枚をデッキ上に置き、残りを控え室に置く',
        'options': list(top),
        'top_cards': list(top),
        'label': str(label or ''),
    })
    gs.log.append(f'[PENDING] choose_top_keep_one top={len(top)} ({label})')


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
    ci = _get_card(cards_db, reveal) if reveal else None
    if ci and _is_live_ci(ci):
        gs.tsunagaru_connect_bonus_this_live = 1
        gs.log.append(f'[AUTO] Tsunagaru Connect: revealed LIVE on top -> score +1 ({reveal})')
    else:
        gs.tsunagaru_connect_bonus_this_live = 0
        gs.log.append(f'[AUTO] Tsunagaru Connect: revealed non-LIVE on top ({reveal})')
    return True



def _apply_vivid_world_blue_mode(pool: Dict[str, int]) -> Dict[str, int]:
    out = {str(k).lower(): int(v or 0) for k, v in (pool or {}).items()}
    moved = 0
    for k in ('pink', 'red', 'yellow', 'green', 'purple', 'all'):
        moved += int(out.get(k, 0) or 0)
        if k in out:
            out.pop(k, None)
    if moved > 0:
        out['blue'] = int(out.get('blue', 0) or 0) + moved
    return out


def _vivid_world_revealed_niji_has_all_six(gs: GameState, cards_db: Dict[str, CardInfo]) -> bool:
    cols = set()
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if not _is_member_ci(ci):
            continue
        if '虹ヶ咲' not in str(getattr(ci, 'group', '') or ''):
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

        # Special-case: 桜坂しずく bp1-003 live-start
        try:
            if _canon_cardno(getattr(ci, 'cardnumber', '') or '') == _SHIZUKU_BP1_003_CN_CANON:
                if int(getattr(gs, 'energy_active', 0) or 0) >= 1:
                    pr = {
                        'kind': 'live_start_shizuku_bp1_003_pay',
                        'pos': pos,
                        'cn': getattr(ci, 'cardnumber', '') or '',
                        'text': f"{pos}: {getattr(ci, 'cardnumber', '') or ''} ライブ開始時 [E]1 → 好きなハート色を1つ得る (ライブ終了時まで)",
                        'options': ['pay', 'skip'],
                    }
                    _append_prompt(pr, pr['text'])
                # special-case 処理済み → 汎用ループをスキップ
                continue
        except Exception:
            pass

        # Special-case: Emma Verde bp3-008 live-start
        try:
            if _canon_cardno(getattr(ci, 'cardnumber', '') or '') == _EMMA_BP3_008_CN_CANON:
                cands0 = _emma_bp3_008_live_start_candidates(gs, cards_db, pos)
                if cands0 and len(list(getattr(gs, 'hand', []) or [])) >= 2:
                    pr = {
                        'kind': 'emma_bp3_008_live_start_pay',
                        'pos': pos,
                        'cn': getattr(ci, 'cardnumber', '') or '',
                        'text': '【エマ・ヴェルデ】ライブ開始時：手札を2枚控え室に置いてもよい → このメンバー以外のウェイト状態の『虹ヶ咲』メンバー1人をアクティブにする。そうした場合、そのメンバーとこのメンバーはライブ終了時まで緑ハート+1',
                        'options': ['pay', 'skip'],
                        'pos_options': list(cands0),
                    }
                    _append_prompt(pr, f"{pos}: {getattr(ci, 'cardnumber', '') or ''} ライブ開始時")
                # special-case 処理済み → 汎用ループをスキップ
                continue
        except Exception:
            pass

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
                cost = str(cl.get("cost_template", "") or raw)
                eff = str(cl.get("effect_template", "") or raw)
                if "<(E)>" not in cost and "[E]" not in cost and "Ｅ" not in cost and "E" not in cost:
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
                    # Optional hand-discard cost（「手札をN枚控え室に置いてもよい」「手札のXを1枚控え室に置いてもよい」）
                    if '控え室に置いてもよい' in cost and _match_effect_template(eff):
                        # 手札のライブカードを捨てるコスト
                        m_live = re.search(r'手札のライブカードを(\d+)枚控え室に置いてもよい', cost)
                        m_hand = re.search(r'手札を(\d+)枚控え室に置いてもよい', cost)
                        if m_live:
                            cost_kind = 'discard_live_from_hand'
                            cost_n = int(m_live.group(1))
                        elif m_hand:
                            cost_kind = 'discard_from_hand'
                            cost_n = int(m_hand.group(1))
                        else:
                            cost_kind = 'discard_from_hand'
                            cost_n = 1
                        pr = {
                            'kind': 'live_start_pay_effect',
                            'pos': pos,
                            'cn': ci.cardnumber,
                            'need_e': 0,
                            'cost_kind': cost_kind,
                            'cost_n': cost_n,
                            'effect': eff,
                            'text': _pretty_optional_effect_prompt_text('ライブ開始時', ci.cardnumber, cost, eff),
                            'options': ['pay', 'skip'],
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
                    if not cost.strip() or cost.strip() == eff.strip():
                        m_free = _match_effect_template(eff)
                        if m_free:
                            r_free, gd_free = m_free
                            op_free = r_free.get('op', '')
                            if op_free == 'activate_stage_member':
                                opts_act = [p2 for p2 in ('L','C','R') if gs.stage.get(p2) and not gs.stage[p2].active]
                                if opts_act:
                                    # may効果なので1人でも複数でも必ず画像選択ポップアップ一発（skip可）
                                    wait_cns = [gs.stage[p2].cardnumber for p2 in opts_act if gs.stage.get(p2)]
                                    pr = {
                                        'kind': 'choose_stage_member_to_activate',
                                        'text': f"{pos}: {ci.cardnumber} ライブ開始時 → ステージのメンバーを1人までアクティブにする（スキップ可）",
                                        'options': opts_act + ['skip'],
                                        'card_options': wait_cns,
                                        'allow_skip': True,
                                        'source_pos': pos,
                                        'source_cn': ci.cardnumber,
                                    }
                                    _append_prompt(pr, f"{pos}: {ci.cardnumber} ライブ開始時")
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
    try:
        _generic_live_skip = {
            _RISE_UP_HIGH_CN_CANON,
            _BUTTERFLY_CN_CANON,
            _NEO_SKY_CN_CANON,
            _TSUNAGARU_CONNECT_CN_CANON,
            _VIVID_WORLD_CN_CANON,
            _BOKULIVE_BP3_019_CN_CANON,
            _HEARTBEAT_BP4_021_CN_CANON,
        }
    except Exception:
        _generic_live_skip = set()
    try:
        for cn_live in list(getattr(gs, 'set_zone', []) or []):
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
                for cl in clauses:
                    if not isinstance(cl, dict):
                        continue
                    raw = str(cl.get('raw', '') or '')
                    cost = str(cl.get('cost_template', '') or raw)
                    eff = str(cl.get('effect_template', '') or raw)
                    # Only generic no-cost LIVE-card hooks here.  Paid/special cards
                    # stay on the hard-coded paths below.
                    if ('<(E)>' in cost or '[E]' in cost or 'Ｅ' in cost or 'E' in cost):
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
                        src_live = getattr(ci_live, 'cardnumber', '') or str(cn_live or '')
                        triggers.append({
                            'kind': 'live_start_apply_effect',
                            'source_cn': src_live,
                            'label': f'{src_live} ライブ開始時',
                            'effect': eff,
                        })
    except Exception:
        pass

    # LIVE-card live-start: Rise Up High! (PL!N-bp4-029)
    try:
        if int(getattr(gs, 'turn', 0) or 0) == 1:
            for cn_live in list(getattr(gs, 'set_zone', []) or []):
                if _canon_cardno(str(cn_live or '')) != _RISE_UP_HIGH_CN_CANON:
                    continue
                gs.log.append('[AUTO] LIVE: PL!N-bp4-029 live-start: score +1 (turn1)')
                cands = []
                for ppos in ('L','C','R'):
                    slot2 = (gs.stage or {}).get(ppos)
                    if not slot2 or not getattr(slot2, 'active', False):
                        continue
                    ci2 = _get_card(cards_db, getattr(slot2, 'cardnumber', '') or '')
                    if not ci2:
                        continue
                    if '虹ヶ咲' in str(getattr(ci2, 'group', '') or ''):
                        cands.append(ppos)
                if cands:
                    _rise_up_high_opts = []
                    for _pp in list(cands):
                        _sl = (gs.stage or {}).get(_pp)
                        _nm = ''
                        try:
                            _ci = _get_card(cards_db, getattr(_sl, 'cardnumber', '') or '') if _sl else None
                            _nm = str(getattr(_ci, 'name', '') or '') if _ci else ''
                        except Exception:
                            _nm = ''
                        _rise_up_high_opts.append(f"{_pp}: {_nm}" if _nm else str(_pp))
                    pr = {
                        'kind': 'live_start_rise_up_high_pick',
                        'cn': _RISE_UP_HIGH_CN_CANON,
                        'text': '【Rise Up High!】ライブ開始時：『虹ヶ咲』のメンバーを1人選ぶ（このライブ終了時まで、そのメンバーはブレード+1）',
                        'options': list(_rise_up_high_opts),
                        'pos_options': list(cands),
                    }
                    _append_prompt(pr, 'PL!N-bp4-029 ライブ開始時')
                else:
                    gs.log.append('[INFO] Rise Up High: no Nijigasaki member on stage; blade bonus skipped')
                break
    except Exception:
        pass

    try:
        if int(getattr(gs, 'energy_active', 0) or 0) >= 2 and _has_nijigasaki_member_on_stage(gs, cards_db):
            _bf_n = 0
            for _cn0 in list(getattr(gs, 'set_zone', []) or []):
                try:
                    _canon0 = _canon_cardno(_cn0)
                except Exception:
                    _canon0 = str(_cn0 or '')
                if _canon0 == _BUTTERFLY_CN_CANON:
                    _bf_n += 1
            for _i in range(int(_bf_n or 0)):
                pr = {
                    'kind': 'live_start_butterfly_pay',
                    'cn': _BUTTERFLY_CN_CANON,
                    'text': '【Butterfly】ライブ開始時：エネルギー2枚を支払ってもよい。自分のステージに『虹ヶ咲』のメンバーがいる場合、このカードのスコアを+1する。',
                    'options': ['pay', 'skip'],
                }
                _append_prompt(pr, 'PL!N-bp1-028 ライブ開始時')
    except Exception:
        pass

    try:
        if _neo_sky_stage_ready(gs, cards_db):
            _neo_n = 0
            for _cn0 in list(getattr(gs, 'set_zone', []) or []):
                try:
                    _canon0 = _canon_cardno(_cn0)
                except Exception:
                    _canon0 = str(_cn0 or '')
                if _canon0 == _NEO_SKY_CN_CANON:
                    _neo_n += 1
            for _i in range(int(_neo_n or 0)):
                pr = {
                    'kind': 'neo_sky_execute',
                    'cn': _NEO_SKY_CN_CANON,
                    'text': '【NEO SKY, NEO MAP!】ライブ開始時：条件達成 → 3枚引き、手札を3枚好きな順番でデッキの上に置く',
                    'options': ['ok'],
                }
                _append_prompt(pr, 'PL!N-bp4-031 ライブ開始時')
    except Exception:
        pass

    try:
        _niji_n = _count_nijigasaki_members_on_stage(gs, cards_db)
        if _niji_n > 0:
            _tc_n = 0
            for _cn0 in list(getattr(gs, 'set_zone', []) or []):
                try:
                    _canon0 = _canon_cardno(_cn0)
                except Exception:
                    _canon0 = str(_cn0 or '')
                if _canon0 == _TSUNAGARU_CONNECT_CN_CANON:
                    _tc_n += 1
            for _i in range(int(_tc_n or 0)):
                pr = {
                    'kind': 'tsunagaru_connect_execute',
                    'cn': _TSUNAGARU_CONNECT_CN_CANON,
                    'text': '【ツナガルコネクト】ライブ開始時：ステージの『虹ヶ咲』メンバー数ぶんデッキ上を見る → 1枚をデッキ上、残りを控え室。さらにデッキトップを公開し、ライブカードならスコア+1',
                    'options': ['ok'],
                    'k': int(_niji_n),
                }
                _append_prompt(pr, 'PL!N-bp3-028 ライブ開始時')
    except Exception:
        pass


    # LIVE cards in set_zone: enqueue numeric live-start effects that should resolve in order
    try:
        for _set_idx, _cn_live in enumerate(list(getattr(gs, 'set_zone', []) or [])):
            _ci_live = _get_card(cards_db, _cn_live)
            if not _ci_live or not _is_live_ci(_ci_live):
                continue
            _canon_live = _canon_cardno(_cn_live)
            if _live_start_set_idx_resolved(gs, _set_idx):
                continue
            if _canon_live == _BOKULIVE_BP3_019_CN_CANON:
                pr = {
                    'kind': 'live_start_numeric_effect',
                    'source_cn': _cn_live,
                    'set_idx': int(_set_idx),
                    'effect_code': 'bp3_019_score',
                    "text": f"LIVE{_set_idx+1}: {_cn_live} ライブ開始時 → 自分のライブ中の『μ's』のカードが2枚以上なら、このカードのスコアを+1する。",
                    'options': ['ok'],
                }
                _append_prompt(pr, pr['text'])
            elif _canon_live == _HEARTBEAT_BP4_021_CN_CANON:
                pr = {
                    'kind': 'live_start_numeric_effect',
                    'source_cn': _cn_live,
                    'set_idx': int(_set_idx),
                    'effect_code': 'bp4_021_req_score',
                    "text": f"LIVE{_set_idx+1}: {_cn_live} ライブ開始時 → 成功ライブ置き場のスコア合計が6以上なら必要ハート(任意)-1、9以上ならさらにこのカードのスコアを+1する。",
                    'options': ['ok'],
                }
                _append_prompt(pr, pr['text'])
    except Exception:
        pass

    try:
        _vw_n = 0
        for _cn0 in list(getattr(gs, 'set_zone', []) or []):
            try:
                _canon0 = _canon_cardno(_cn0)
            except Exception:
                _canon0 = str(_cn0 or '')
            if _canon0 == _VIVID_WORLD_CN_CANON:
                _vw_n += 1
        for _i in range(int(_vw_n or 0)):
            triggers.append({
                'kind': 'live_start_vivid_world_auto',
                'source_cn': _VIVID_WORLD_CN_CANON,
                'label': 'PL!N-bp4-025 ライブ開始時',
            })
    except Exception:
        pass

    n = len(triggers)
    if n <= 0:
        if did_auto:
            gs.live_start_prompted = True
        return 0

    gs.live_start_prompted = True
    if n >= 2:
        gs.pending.append({
            'kind': 'auto_order',
            'text': 'ライブ開始時効果が複数発生：解決するカードを選択（1つずつ）',
            'options': [_auto_trigger_option_text(t) for t in triggers if _auto_trigger_option_text(t)],
            'queue': list(triggers),
        })
        gs.log.append(f'[PENDING] auto_order triggers={len(triggers)}')
        gs.log.append(f'[PROMPT] live-start abilities queued: {n}')
        return n

    for t in triggers:
        _exec_auto_trigger(gs, cards_db, t)
    gs.log.append(f'[AUTO] live-start triggers queued={n}')
    return n


def _clear_end_of_live_buffs(gs: GameState) -> None:
    for pos in ("L", "C", "R"):
        slot = gs.stage.get(pos)
        if not slot:
            continue
        if getattr(slot, "temp_until", "") == "end_of_live":
            slot.temp_blade = 0
            slot.temp_hearts = {}
            slot.temp_until = ""
        # Always clear heart_replace_color at end of live (it's always "until end of live")
        try:
            slot.heart_replace_color = ""
        except Exception:
            pass

    # clear global end-of-live buffs
    try:
        gs.success_zone_heart_color = ""
    except Exception:
        pass
    try:
        gs.butterfly_paid_this_live = 0
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
        baton_old_cost = int(old.cost) if old else 0
        # If the replaced member had energies under it, they return to the energy deck (not to energy zone).
        old_under = int(getattr(existing, 'energy_under', 0) or 0)
        if old_under > 0:
            try:
                gs.log.append(f"[INFO] {pos}: {baton_old_cn} leaves stage -> return under-energy x{old_under} to energy deck")
            except Exception:
                pass
            try:
                existing.energy_under = 0
            except Exception:
                pass

    cn = gs.hand[hand_idx]
    c = _get_card(cards_db, cn)
    ctype = (c.type if c else "")
    if not c or not is_member_type(ctype):
        gs.log.append(f"[ERR] play: not a MEMBER card: cn={cn} db_type='{ctype}'")
        return

    cost = int(c.cost or 0)
    pay_cost = cost
    if baton_old_cn is not None:
        # Always apply baton touch when the target stage area is occupied.
        # Reduce the cost by the replaced member's cost (min 0), and send the replaced member to green room.
        pay_cost = max(0, cost - int(baton_old_cost or 0))
        gs.green_room.append(baton_old_cn)
        gs.log.append(f"[BATON] {pos}: {baton_old_cn} -> green room; reduce {cost} by {baton_old_cost} => pay {pay_cost}")

    if not pay_energy(gs, pay_cost):
        gs.log.append(f"[ERR] play: insufficient energy (need {pay_cost}, have {gs.energy_active})")
        return

    gs.hand.pop(hand_idx)
    gs.stage[pos] = StageSlot(cardnumber=(c.cardnumber if c else cn), active=True)
    gs.log.append(f"[PLAY] {pos} <- {cn} (pay {pay_cost}; E active={gs.energy_active} wait={gs.energy_wait})")

    # Auto abilities can trigger simultaneously on this "member enters stage" event.
    # If multiple triggers exist, let the user choose the resolution order.
    triggers = _collect_auto_triggers_on_member_enter(gs, cards_db, entered_pos=pos, entered_cn=cn)
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



def handle_enter_auto(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, cn: str, rng: Optional[random.Random] = None) -> None:
    # Handle [登場] auto abilities for a member that just entered stage.
    canon = _canon_cardno(cn)

    # Hard-coded Shioriko (choice prompt)
    if canon == "PL!N-pb1-010":
        gs.pending.append({
            "kind": "choose_shioriko_enter",
            "cn": canon,
            "pos": pos.upper(),
            "text": "栞子[登場]: 効果を1つ選ぶ（エネルギー+1 / 控え室の虹ヶ咲LIVEを最大2枚デッキ上）",
            "options": ["energy", "topdeck"],
        })
        gs.log.append("[AUTO] 栞子[登場]: choose mode -> pending")
        return

    if rng is None:
        rng = random.Random(gs.seed)

    ci = _get_card(cards_db, canon)
    if not ci or not getattr(ci, 'abilities', None):
        return

    for ab in _iter_triggered_abilities(ci, '登場'):
        clauses = ab.get('clauses', [])
        if not isinstance(clauses, list):
            continue
        main_phase_only = False
        for cl in clauses:
            if not isinstance(cl, dict):
                continue
            cost = str(cl.get('cost_template', '') or '')
            eff = str(cl.get('effect_template', '') or cl.get('raw', '') or '').strip()
            if not eff:
                continue
            if eff == '自分のメインフェイズの場合、' and not cost:
                main_phase_only = True
                continue
            # Cost template handling for [登場]
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
                if n > 0:
                    ctx = {'pos': pos.upper(), 'source_cn': canon}
                    gs.pending.append({
                        'kind': 'pay_or_skip',
                        'text': _pretty_optional_effect_prompt_text('登場', canon, cost, eff),
                        'options': ['pay', 'skip'],
                        'cost_kind': 'discard_from_hand',
                        'cost_n': n,
                        'after_effect_template': eff,
                        'ctx': ctx,
                        'source_cn': canon,
                    })
                    gs.log.append(f"[PENDING] {canon}[登場]: pay/skip -> discard {n} then {eff}")
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
                need_e_main = _parse_energy_cost(cost)
                if ((('自分のメインフェイズ' in cost) or main_phase_only) and need_e_main > 0 and _match_effect_template(eff)):
                    if str(getattr(gs, 'phase', '') or '').upper() != 'MAIN':
                        gs.log.append(f"[INFO] {canon}[登場]: main-phase-only cost skipped outside MAIN")
                        main_phase_only = False
                        continue
                    if int(getattr(gs, 'energy_active', 0) or 0) < int(need_e_main):
                        gs.log.append(f"[INFO] {canon}[登場]: not enough active energy for optional cost [E]{need_e_main}")
                        main_phase_only = False
                        continue
                    pretty_cost = cost
                    if main_phase_only and ('自分のメインフェイズ' not in pretty_cost):
                        pretty_cost = '自分のメインフェイズの場合、' + pretty_cost
                    ctx = {'pos': pos.upper(), 'source_cn': canon}
                    gs.pending.append({
                        'kind': 'pay_or_skip',
                        'text': _pretty_optional_effect_prompt_text('登場', canon, pretty_cost, eff),
                        'options': ['pay', 'skip'],
                        'cost_kind': 'energy',
                        'cost_n': int(need_e_main),
                        'after_effect_template': eff,
                        'ctx': ctx,
                        'source_cn': canon,
                    })
                    gs.log.append(f"[PENDING] {canon}[登場]: pay/skip -> [E]{need_e_main} then {eff}")
                    return
                # unsupported cost template for now
                gs.log.append(f"[INFO] {canon}[登場]: unsupported cost_template skipped: {cost}")
                main_phase_only = False
                continue

            # costless-only for now
            if _parse_energy_cost(cost) > 0 or _cost_requires_self_to_green(cost):
                main_phase_only = False
                continue
            ctx = {'pos': pos.upper(), 'source_cn': canon}
            if try_apply_effect_template(gs, rng, cards_db, eff, ctx):
                gs.log.append(f"[AUTO] {canon}[登場]: applied {eff}")
                if gs.pending:
                    return
            main_phase_only = False

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


def handle_stage_cost10_member_enter(gs: GameState, cards_db: Dict[str, CardInfo], entered_pos: str, entered_cn: str, ai_pos: str = '', rng: Optional[random.Random] = None) -> None:
    """Handle auto abilities that trigger when a cost-10 MEMBER enters your stage.

    PL!N-pb1-005 (宮下愛):
      <自動><ターン1回> 自分のステージにコスト10のメンバーが登場したとき、カードを1枚引く。

    NOTE: We resolve *one* Ai instance per trigger so that 2×Ai produces 2 separate triggers
    that can be ordered and resolved independently (rule-consistent).
    """
    try:
        entered_pos = str(entered_pos or '').upper()
    except Exception:
        entered_pos = 'C'
    try:
        ai_pos_u = str(ai_pos or '').upper()
    except Exception:
        ai_pos_u = ''

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
        if canon != 'PL!N-pb1-005':
            return
        key = f"{p}:{canon}:auto_cost10_enter"
        used = int((getattr(gs, 'used_this_turn', {}) or {}).get(key, 0) or 0)
        if used >= 1:
            return
        drew = draw(gs, 1, rng)
        try:
            gs.used_this_turn[key] = 1
        except Exception:
            gs.used_this_turn = {key: 1}
        gs.log.append(f"[AUTO] {canon}({p}): cost10 member entered ({canon_enter} @ {entered_pos}) -> drew {drew}")

    if ai_pos_u in ('L', 'C', 'R'):
        _resolve_one(ai_pos_u)
        return

    # Fallback: resolve all (legacy behavior)
    for p in ('L', 'C', 'R'):
        _resolve_one(p)

def _has_supported_enter_auto(ci: Optional[CardInfo]) -> bool:
    if not ci or not getattr(ci, 'abilities', None):
        return False
    canon = _canon_cardno(getattr(ci, 'cardnumber', '') or '')
    # Special-cased Shioriko is always supported.
    if canon == 'PL!N-pb1-010':
        return True
    # Any costless, regex-matchable enter ability counts as supported.
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

            # allow optional discard-from-hand costs (e.g., "手札を1枚控え室に置いてもよい：...")
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
                if n > 0 and _match_effect_template(eff):
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


def _has_body_activated_in_text(ci: Optional[CardInfo]) -> bool:
    """Return True if the card has a BODY-style activated ability (手札をすべて公開する).
    Uses the structured abilities field (trigger='BODY', ability_type='起動').
    """
    if not ci:
        return False
    for ab in _iter_activated_abilities(ci):
        if str(ab.get('trigger', '') or '') != 'BODY':
            continue
        for cl in (ab.get('clauses', []) or []):
            if not isinstance(cl, dict):
                continue
            cost = str(cl.get('cost_template', '') or '')
            if '手札をすべて公開する' in cost:
                return True
    return False


def _list_active_ai_cost10_positions(gs: GameState, cards_db: Dict[str, CardInfo], entered_cn: str) -> List[str]:
    """Return stage positions of unused 宮下愛(PL!N-pb1-005) that would trigger on cost-10 member enter."""
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
        if canon != 'PL!N-pb1-005':
            continue
        key = f"{p}:{canon}:auto_cost10_enter"
        used = int((getattr(gs, 'used_this_turn', {}) or {}).get(key, 0) or 0)
        if used < 1:
            out.append(p)
    return out


def _has_active_ai_cost10_trigger(gs: GameState, cards_db: Dict[str, CardInfo], entered_cn: str) -> bool:
    return bool(_list_active_ai_cost10_positions(gs, cards_db, entered_cn))

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

    # 宮下愛(PL!N-pb1-005): one trigger per unused copy on stage
    for ai_pos in _list_active_ai_cost10_positions(gs, cards_db, entered_cn):
        out.append({
            'kind': 'ai_cost10_enter',
            'source_cn': 'PL!N-pb1-005',
            'ai_pos': str(ai_pos).upper(),
            'entered_pos': str(entered_pos or 'C').upper(),
            'entered_cn': entered_cn,
        })

    return out

def _auto_trigger_option_text(t: Dict[str, Any]) -> str:
    try:
        lbl = str((t or {}).get('label', '') or '').strip()
    except Exception:
        lbl = ''
    if lbl:
        return lbl
    try:
        cn = str((t or {}).get('source_cn', '') or '').strip()
    except Exception:
        cn = ''
    return cn


def _exec_auto_trigger(gs: GameState, cards_db: Dict[str, CardInfo], trig: Dict[str, Any]) -> None:
    kind = str((trig or {}).get('kind', '') or '')
    if kind == 'enter_auto':
        pos = str(trig.get('pos', 'C') or 'C').upper()
        cn = str(trig.get('cn', '') or '')
        handle_enter_auto(gs, cards_db, pos, cn)
        return
    if kind == 'ai_cost10_enter':
        handle_stage_cost10_member_enter(gs, cards_db, entered_pos=str(trig.get('entered_pos','C') or 'C'), entered_cn=str(trig.get('entered_cn','') or ''), ai_pos=str(trig.get('ai_pos','') or ''), rng=rng)
        return
    if kind == 'enqueue_pending_prompt':
        prm = dict((trig or {}).get('prompt', {}) or {})
        if prm:
            gs.pending.append(prm)
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
    if kind == 'live_start_vivid_world_auto':
        gs.vivid_world_blue_mode_this_live = True
        gs.log.append('[AUTO] VIVID WORLD live-start: cheer pink/red/yellow/green/purple/all -> blue until end of live')
        return
    # Unknown trigger
    gs.log.append(f"[WARN] auto_trigger: unknown kind={kind}")


def _live_set_limit(gs: GameState) -> int:
    try:
        lim = int(getattr(gs, 'current_live_set_limit', 3) or 0)
    except Exception:
        lim = 3
    return max(0, lim)


def _bump_next_live_set_limit_reduction(gs: GameState, amount: int = 1, source_cn: str = '') -> int:
    try:
        cur = int(getattr(gs, 'next_live_set_limit_reduction', 0) or 0)
    except Exception:
        cur = 0
    try:
        add = int(amount or 0)
    except Exception:
        add = 0
    if add <= 0:
        return cur
    cur += add
    gs.next_live_set_limit_reduction = cur
    if source_cn:
        gs.log.append(f"[AUTO] {source_cn}: next LIVE_SET hand-placement limit -{add} (pending total -{cur})")
    else:
        gs.log.append(f"[AUTO] next LIVE_SET hand-placement limit -{add} (pending total -{cur})")
    return cur


def _apply_temp_blade_to_stage_pos(gs: GameState, pos: str, n: int, source_cn: str = '') -> bool:
    p = str(pos or '').upper()
    slot = (gs.stage or {}).get(p) if isinstance(getattr(gs, 'stage', None), dict) else None
    if slot is None or not bool(getattr(slot, 'cardnumber', None)):
        return False
    try:
        slot.temp_blade = int(getattr(slot, 'temp_blade', 0) or 0) + int(n or 0)
        slot.temp_until = 'end_of_live'
    except Exception:
        return False
    if source_cn:
        gs.log.append(f"[AUTO] {source_cn}: {p} temp blade +{int(n or 0)} until end of live")
    return True


def _enqueue_dive_faceup_bonus_prompt(gs: GameState, cards_db: Dict[str, CardInfo], source_cn: str) -> None:
    cands: List[str] = []
    for p in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(p) if isinstance(getattr(gs, 'stage', None), dict) else None
        if slot is None or not bool(getattr(slot, 'cardnumber', None)):
            continue
        ci = _get_card(cards_db, slot.cardnumber)
        grp = str(getattr(ci, 'group', '') or '') if ci else ''
        unit = str(getattr(ci, 'unit', '') or '') if ci else ''
        if ('虹ヶ咲' in grp) or ('虹ヶ咲' in unit):
            cands.append(p)
    if not cands:
        gs.log.append(f"[AUTO] {source_cn}: no 虹ヶ咲 member on stage for face-up set bonus")
        return
    if len(cands) == 1:
        _apply_temp_blade_to_stage_pos(gs, cands[0], 2, source_cn=source_cn)
        return
    gs.pending.append({
        'kind': 'dive_faceup_pick_stage_member_blade2',
        'source_cn': source_cn,
        'text': 'DIVE! が表向きでライブカード置き場に置かれた：『虹ヶ咲』のメンバー1人にブレード+2（ライブ終了時まで）',
        'options': cands,
    })


def _on_faceup_live_put_into_set_zone(gs: GameState, cards_db: Dict[str, CardInfo], cn: str, source_cn: str = '') -> None:
    canon = _canon_cardno(str(cn or ''))
    if canon == 'PL!N-bp4-026':
        _enqueue_dive_faceup_bonus_prompt(gs, cards_db, source_cn=source_cn or canon)


def _move_live_from_green_to_set_zone(gs: GameState, cards_db: Dict[str, CardInfo], cn: str, source_cn: str = '') -> bool:
    pick_cn = None
    target = _canon_cardno(str(cn or ''))
    for x in list(getattr(gs, 'green_room', []) or []):
        if _canon_cardno(x) == target:
            pick_cn = x
            break
    if not pick_cn:
        return False
    ci = _get_card(cards_db, pick_cn)
    if not _is_live(ci):
        return False
    gs.green_room.remove(pick_cn)
    gs.set_zone.append(pick_cn)
    gs.log.append(f"[AUTO] {source_cn or target}: green->set(face-up) {pick_cn}")
    _on_faceup_live_put_into_set_zone(gs, cards_db, pick_cn, source_cn=source_cn or target)
    return True


def _move_named_live_from_hand_to_set_zone(gs: GameState, cards_db: Dict[str, CardInfo], choice_cn: str, required_name: str, source_cn: str = '') -> bool:
    target = _canon_cardno(str(choice_cn or ''))
    pick_cn = None
    for x in list(getattr(gs, 'hand', []) or []):
        if _canon_cardno(x) != target:
            continue
        ci = _get_card(cards_db, x)
        nm = str(getattr(ci, 'name', '') or '') if ci else ''
        if required_name and nm != required_name:
            continue
        if not _is_live(ci):
            continue
        pick_cn = x
        break
    if not pick_cn:
        return False
    gs.hand.remove(pick_cn)
    gs.set_zone.append(pick_cn)
    gs.log.append(f"[AUTO] {source_cn or target}: hand->set(face-up) {pick_cn}")
    _on_faceup_live_put_into_set_zone(gs, cards_db, pick_cn, source_cn=source_cn or target)
    return True


def cmd_set(gs: GameState, rng: random.Random, indices: List[int]) -> None:
    limit = _live_set_limit(gs)
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
    gs.set_zone.extend(picked)
    try:
        gs.live_start_resolved_set_idxs = []
    except Exception:
        pass
    drawn = draw(gs, len(picked), rng)
    gs.log.append(f"[SET] set {len(picked)} cards, drew {drawn} (live_set total={len(getattr(gs, 'set_zone', []) or [])})")


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

    try:
        if bool(getattr(gs, 'vivid_world_blue_mode_this_live', False)):
            gs.vivid_world_bonus_this_live = 1 if _vivid_world_revealed_niji_has_all_six(gs, cards_db) else 0
            if int(getattr(gs, 'vivid_world_bonus_this_live', 0) or 0) > 0:
                gs.log.append('[AUTO] VIVID WORLD: revealed Nijigasaki members contain all six colors -> score +1')
            else:
                gs.log.append('[AUTO] VIVID WORLD: revealed Nijigasaki members do not contain all six colors')
        else:
            gs.vivid_world_bonus_this_live = 0
    except Exception:
        gs.vivid_world_bonus_this_live = 0

    draw_n = 0
    for cn in revealed:
        c = _get_card(cards_db, cn)
        if c:
            draw_n += _count_draw_icons(c.blade_heart_tags_json)
    got = draw(gs, draw_n, rng) if draw_n > 0 else 0
    gs.log.append(f"[YELL] revealed {len(revealed)} (blade={n}), draw+{draw_n} -> drew {got}")



def _has_nijigasaki_member_on_stage(gs: GameState, cards_db: Dict[str, CardInfo]) -> bool:
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
            return True
    return False


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


def _la_bella_patria_green_excess(gs: GameState) -> int:
    try:
        pool = dict(getattr(gs, 'last_attempt_excess_hearts', {}) or {})
    except Exception:
        pool = {}
    return int(pool.get('green', 0) or 0)


def _la_bella_patria_can_trigger(gs: GameState, cards_db: Dict[str, CardInfo]) -> bool:
    # IMPORTANT: only real green excess counts here. ALL does not satisfy this condition.
    if int(_la_bella_patria_green_excess(gs)) <= 0:
        return False
    return bool(_has_nijigasaki_member_on_stage(gs, cards_db))


def _enqueue_success_auto_order(gs: GameState, triggers: List[Dict[str, Any]]) -> int:
    triggers = list(triggers or [])
    n = len(triggers)
    if n <= 0:
        return 0
    if n == 1:
        return 1
    gs.pending.append({
        'kind': 'auto_order',
        'text': 'ライブ成功時効果が複数発生：解決するカードを選択（1つずつ）',
        'options': [_auto_trigger_option_text(t) for t in triggers if _auto_trigger_option_text(t)],
        'queue': list(triggers),
    })
    gs.log.append(f"[PROMPT] live-success abilities queued: {n}")
    return n


def _run_live_success_triggers(gs: GameState, rng: random.Random, cards_db: Dict[str, CardInfo], lives: List[str]) -> None:
    try:
        setattr(gs, '_poppin_pending_queue', [])
    except Exception:
        pass
    success_triggers: List[Dict[str, Any]] = []
    """Run <ライブ成功時> triggers at LIVE_RESOLVE timing (before winner-based success storage).

    Some LIVE success effects conditionally depend on 成功ライブカード置き場 (e.g., Daydream Mermaid),
    and the current successful LIVE may be placed there. Therefore we execute these triggers after the
    optional 'store one successful LIVE card' prompt has been resolved.
    """
    # Stage-member success triggers (costless, regex-supported subset)
    for pos in ('L','C','R'):
        slot = gs.stage.get(pos)
        if not slot or not slot.active:
            continue
        ci_src = _get_card(cards_db, slot.cardnumber)
        if not ci_src or not getattr(ci_src, 'abilities', None):
            continue
        for ab in _iter_triggered_abilities(ci_src, 'ライブ成功時'):
            ctx = {'pos': pos, 'source_cn': ci_src.cardnumber}
            if isinstance(ab, dict) and _enqueue_choose_effects_from_ability(gs, cards_db, ab, ctx):
                return
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
                # Optional hand-discard cost for retrieve_from_yell effects
                m_opt = re.search(r'手札を(\d+)枚控え室に置いてもよい', cost)
                if m_opt and _match_effect_template(eff) and 'retrieve_from_yell' == (_match_effect_template(eff) or [{}])[0].get('op', ''):
                    cost_n = int(m_opt.group(1))
                    gs.pending.append({
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
                    })
                    gs.log.append(f"[PENDING] {pos}: {ci_src.cardnumber}[ライブ成功時] pay_or_skip -> {eff}")
                    return
                ctx = {'pos': pos, 'source_cn': ci_src.cardnumber}
                if try_apply_effect_template(gs, rng, cards_db, eff, ctx):
                    gs.log.append(f"[AUTO] {pos}: {ci_src.cardnumber}[ライブ成功時] applied {eff}")
                    if gs.pending:
                        return
            if gs.pending:
                return
        if gs.pending:
            return

    # Live-card success triggers (costless, regex-supported subset)
    for cn_live in list(lives or []):
        ci_live = _get_card(cards_db, cn_live)

        # Special: La Bella Patria (PL!N-bp3-027)
        try:
            if _canon_cardno(str(cn_live or '')) == _LA_BELLA_PATRIA_CN_CANON:
                if _la_bella_patria_can_trigger(gs, cards_db):
                    success_triggers.append({
                        'kind': 'success_auto_labella',
                        'source_cn': str(cn_live or ''),
                        'label': 'PL!N-bp3-027 ライブ成功時',
                    })
                else:
                    gs.log.append('[INFO] La Bella Patria: condition not met')
        except Exception:
            pass

        # Special: Poppin' Up! (PL!N-bp1-026)
        try:
            if _canon_cardno(str(cn_live or '')) == _POPPIN_UP_CN_CANON:
                pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
                cands = []
                for cn2 in pool:
                    ci2 = _get_card(cards_db, cn2)
                    if ci2 and ('虹ヶ咲' in str(getattr(ci2, 'group', '') or '')):
                        cands.append(cn2)
                if cands:
                    _pp_q = list(getattr(gs, '_poppin_pending_queue', []) or [])
                    _pp_q.append({
                        'kind': 'pick_poppinup_from_yell',
                        'text': "【Poppin' Up!】ライブ成功時：相手より合計スコアが高い場合、エールで公開された自分の『虹ヶ咲』カードを1枚手札に加える（条件を満たさない場合はSkip可）",
                        'options': list(cands),
                        'source_cn': str(cn_live or ''),
                    })
                    setattr(gs, '_poppin_pending_queue', _pp_q)
                    success_triggers.append({
                        'kind': 'success_auto_poppin',
                        'source_cn': str(cn_live or ''),
                        'label': "PL!N-bp1-026 ライブ成功時",
                    })
                    gs.log.append(f"[QUEUE] PoppinUp pick from yell ({len(cands)} candidates)")
                else:
                    gs.log.append("[INFO] PoppinUp: no Nijigasaki cards among yell reveals")
        except Exception:
            pass
        if not ci_live or not getattr(ci_live, 'abilities', None):
            continue
        for ab in _iter_triggered_abilities(ci_live, 'ライブ成功時'):
            ctx2 = {'source_cn': cn_live}
            if isinstance(ab, dict) and _enqueue_choose_effects_from_ability(gs, cards_db, ab, ctx2):
                return
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
                ctx2 = {'source_cn': cn_live}
                if try_apply_effect_template(gs, rng, cards_db, eff, ctx2):
                    gs.log.append(f"[AUTO] LIVE: {cn_live}[ライブ成功時] applied {eff}")
                    if gs.pending:
                        return
            if gs.pending:
                return
        if gs.pending:
            return

    # Execute success triggers (Poppin / La Bella).
    # If multiple triggers exist, show auto_order prompt for ordering.
    if success_triggers:
        if len(success_triggers) == 1:
            trig = success_triggers[0]
            k = str((trig or {}).get('kind', '') or '')
            if k == 'success_auto_labella':
                _put_wait_energy_from_deck(gs, 1, reason='La Bella Patria')
            elif k == 'success_auto_poppin':
                _pp_q = list(getattr(gs, '_poppin_pending_queue', []) or [])
                if _pp_q:
                    gs.pending.append(_pp_q[0])
                    setattr(gs, '_poppin_pending_queue', _pp_q[1:])
        else:
            _enqueue_success_auto_order(gs, success_triggers)


# ----------------------------
# Step21: LIVE scoring helpers (UI)
# ----------------------------
_EUTOPIA_CN_CANON = 'PL!N-bp1-029'
_RISE_UP_HIGH_CN_CANON = 'PL!N-bp4-029'

_POPPIN_UP_CN_CANON = 'PL!N-bp1-026'
_SOLITUDE_RAIN_CN_CANON = 'PL!N-bp1-027'
_PSYCHO_HEART_CN_CANON = 'PL!N-bp3-026'
_STARS_WE_CHASE_CN_CANON = 'PL!N-bp4-028'
_LOVE_U_MY_FRIENDS_CN_CANON = 'PL!N-bp3-030'
_MONSTER_GIRLS_CN_CANON = 'PL!N-bp3-031'
_EMOTION_CN_CANON = 'PL!N-bp4-027'
_LA_BELLA_PATRIA_CN_CANON = 'PL!N-bp3-027'
_BUTTERFLY_CN_CANON = 'PL!N-bp1-028'
_TSUNAGARU_CONNECT_CN_CANON = 'PL!N-bp3-028'
_VIVID_WORLD_CN_CANON = 'PL!N-bp4-025'
_SHIZUKU_BP1_003_CN_CANON = 'PL!N-bp1-003'
_NEO_SKY_CN_CANON = 'PL!N-bp4-031'
_EMMA_BP3_008_CN_CANON = 'PL!N-bp3-008'
_BOKULIVE_BP3_019_CN_CANON = 'PL!-bp3-019'
_HEARTBEAT_BP4_021_CN_CANON = 'PL!-bp4-021'

def _success_zone_score_sum(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    total = 0
    for cn in list(getattr(gs, 'success_zone', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        try:
            total += int(getattr(ci, 'score', 0) or 0)
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



def _live_start_set_idx_resolved(gs: Optional[GameState], set_idx: Optional[int]) -> bool:
    try:
        if gs is None or set_idx is None:
            return False
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

def _live_score_delta_for_attempt(cn_live, lives_count, gs_turn):
    # Eutopia: if 3+ LIVE cards are set in this attempt, score +2 for Eutopia
    # Rise Up High!: if turn==1 live phase, score +1 for this card
    try:
        canon = _canon_cardno(cn_live)
    except Exception:
        canon = str(cn_live or '')
    if canon == _EUTOPIA_CN_CANON and int(lives_count) >= 3:
        return 2
    if canon == _RISE_UP_HIGH_CN_CANON and int(gs_turn or 0) == 1:
        return 1
    return 0

def _heartbeat_required_any_reduction(cn_live, gs: GameState, cards_db: Dict[str, CardInfo], set_idx: Optional[int] = None) -> int:
    try:
        canon = _canon_cardno(cn_live)
    except Exception:
        canon = str(cn_live or '')
    if canon != _HEARTBEAT_BP4_021_CN_CANON:
        return 0
    if not _live_start_set_idx_resolved(gs, set_idx):
        return 0
    total = _success_zone_score_sum(gs, cards_db)
    return 1 if int(total) >= 6 else 0


def _heartbeat_score_bonus(cn_live, gs: GameState, cards_db: Dict[str, CardInfo], set_idx: Optional[int] = None) -> int:
    try:
        canon = _canon_cardno(cn_live)
    except Exception:
        canon = str(cn_live or '')
    if canon != _HEARTBEAT_BP4_021_CN_CANON:
        return 0
    if not _live_start_set_idx_resolved(gs, set_idx):
        return 0
    total = _success_zone_score_sum(gs, cards_db)
    return 1 if int(total) >= 9 else 0


def _bokulive_score_bonus(cn_live, gs: GameState, cards_db: Dict[str, CardInfo], set_idx: Optional[int] = None) -> int:
    try:
        canon = _canon_cardno(cn_live)
    except Exception:
        canon = str(cn_live or '')
    if canon != _BOKULIVE_BP3_019_CN_CANON:
        return 0
    if not _live_start_set_idx_resolved(gs, set_idx):
        return 0
    return 1 if _mu_live_cards_in_set_zone_count(gs, cards_db) >= 2 else 0


def _compute_attempt_score_breakdown(lives, cards_db, gs_turn, gs=None, live_set_indices=None):
    lives_count = len(lives or [])
    total = 0
    rows = []
    _butterfly_paid_remaining = int(getattr(gs, 'butterfly_paid_this_live', 0) or 0) if gs is not None else 0
    live_set_indices = list(live_set_indices or [])
    for _i, cn in enumerate((lives or [])):
        set_idx = live_set_indices[_i] if _i < len(live_set_indices) else None
        ci = _get_card(cards_db, cn)
        base = int(getattr(ci, 'score', 0) or 0) if ci else 0
        delta = int(_live_score_delta_for_attempt(cn, lives_count, gs_turn))
        if gs is not None:
            delta += int(_extra_live_score_delta_for_attempt(cn, gs, cards_db, set_idx=set_idx))
        try:
            canon = _canon_cardno(cn)
        except Exception:
            canon = str(cn or '')
        if canon == _BUTTERFLY_CN_CANON and _butterfly_paid_remaining > 0:
            delta += 1
            _butterfly_paid_remaining -= 1
        eff = base + delta
        total += eff
        rows.append({'cn': cn, 'base': base, 'delta': delta, 'score': eff})
    return total, rows




def _solitude_rain_stage_color_kinds(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    cols = set()
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot or not getattr(slot, 'active', False):
            continue
        ci = _get_card(cards_db, getattr(slot, 'cardnumber', '') or '')
        if not ci:
            continue
        if '虹ヶ咲' not in str(getattr(ci, 'group', '') or ''):
            continue
        for k, v in ((getattr(ci, 'base_hearts', None) or {}) or {}).items():
            if k in ('pink', 'red', 'yellow', 'green', 'blue', 'purple') and int(v or 0) > 0:
                cols.add(k)
    return int(len(cols))



def _psycho_heart_success_bonus(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    has1 = False
    has5 = False
    for cn in list(getattr(gs, 'success_zone', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        sc = int(getattr(ci, 'score', 0) or 0)
        if sc == 1:
            has1 = True
        elif sc == 5:
            has5 = True
    if has1 and has5:
        return 2
    if has1 or has5:
        return 1
    return 0



def _stars_we_chase_waiting_bonus(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    names = set()
    for cn in list(getattr(gs, 'green_room', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if not _is_live_ci(ci):
            continue
        if '虹ヶ咲' not in str(getattr(ci, 'group', '') or ''):
            continue
        nm = str(
            getattr(ci, 'name', '') or
            getattr(ci, 'cardname', '') or
            getattr(ci, 'title', '') or
            cn
        )
        if nm:
            names.add(nm)
    n = len(names)
    if n >= 6:
        return 2
    if n >= 4:
        return 1
    return 0



def _love_u_my_friends_success_bonus(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    for cn in list(getattr(gs, '_yell_revealed_this_live', []) or []):
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        txt = str(getattr(ci, 'blade_heart_tags_json', '') or '')
        if '(ALL)' in txt:
            return 1
    return 0



def _monster_girls_wait_bonus(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    n = 0
    for pos in ('L', 'C', 'R'):
        slot = (gs.stage or {}).get(pos)
        if not slot:
            continue
        cn = str(getattr(slot, 'cardnumber', '') or '')
        if not cn:
            continue
        ci = _get_card(cards_db, cn)
        if not ci:
            continue
        if _is_live_ci(ci):
            continue
        if bool(getattr(slot, 'active', False)):
            continue
        n += 1
    return int(n)



def _emotion_success_count(gs: GameState) -> int:
    if gs is None:
        return 0
    n = 0
    for cn in list(getattr(gs, 'success_zone', []) or []):
        try:
            canon = _canon_cardno(cn)
        except Exception:
            canon = str(cn or '')
        if canon == _EMOTION_CN_CANON:
            n += 1
    return int(n)


def _emotion_required_any_bonus(cn_live, gs: GameState) -> int:
    try:
        canon = _canon_cardno(cn_live)
    except Exception:
        canon = str(cn_live or '')
    if canon != _EMOTION_CN_CANON:
        return 0
    return 3 * int(_emotion_success_count(gs))


def _effective_live_required_hearts(cn_live, ci, gs: GameState, cards_db: Optional[Dict[str, CardInfo]] = None, set_idx: Optional[int] = None) -> Dict[str, int]:
    req = dict((getattr(ci, 'required_hearts', {}) if ci else {}) or {})
    try:
        extra_any = int(_emotion_required_any_bonus(cn_live, gs))
    except Exception:
        extra_any = 0
    if extra_any > 0:
        req['any'] = int(req.get('any', 0) or 0) + extra_any
    try:
        reduce_any = int(_heartbeat_required_any_reduction(cn_live, gs, cards_db=(cards_db or {}), set_idx=set_idx))
    except Exception:
        reduce_any = 0
    if reduce_any > 0:
        req['any'] = max(0, int(req.get('any', 0) or 0) - reduce_any)
    return req


def _extra_live_score_delta_for_attempt(cn_live, gs: GameState, cards_db: Dict[str, CardInfo], set_idx: Optional[int] = None) -> int:
    try:
        canon = _canon_cardno(cn_live)
    except Exception:
        canon = str(cn_live or '')
    if canon == _SOLITUDE_RAIN_CN_CANON:
        return int(_solitude_rain_stage_color_kinds(gs, cards_db))
    if canon == _PSYCHO_HEART_CN_CANON:
        return int(_psycho_heart_success_bonus(gs, cards_db))
    if canon == _STARS_WE_CHASE_CN_CANON:
        return int(_stars_we_chase_waiting_bonus(gs, cards_db))
    if canon == _LOVE_U_MY_FRIENDS_CN_CANON:
        return int(_love_u_my_friends_success_bonus(gs, cards_db))
    if canon == _MONSTER_GIRLS_CN_CANON:
        return int(_monster_girls_wait_bonus(gs, cards_db))
    if canon == _EMOTION_CN_CANON:
        return 2 * int(_emotion_success_count(gs))
    if canon == _BOKULIVE_BP3_019_CN_CANON:
        return int(_bokulive_score_bonus(cn_live, gs, cards_db, set_idx=set_idx))
    if canon == _HEARTBEAT_BP4_021_CN_CANON:
        return int(_heartbeat_score_bonus(cn_live, gs, cards_db, set_idx=set_idx))
    if canon == _TSUNAGARU_CONNECT_CN_CANON:
        return int(getattr(gs, 'tsunagaru_connect_bonus_this_live', 0) or 0)
    if canon == _VIVID_WORLD_CN_CANON:
        return int(getattr(gs, 'vivid_world_bonus_this_live', 0) or 0)
    return 0


def _enqueue_next_poppin_prompt(gs: GameState) -> bool:
    if list(getattr(gs, 'pending', []) or []):
        return False
    q = list(getattr(gs, '_poppin_pending_queue', []) or [])
    while q:
        p0 = dict(q.pop(0))
        pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
        raw_opts = list(p0.get('options', []) or [])
        counts: Dict[str, int] = {}
        for x in pool:
            cx = _canon_cardno(x)
            counts[cx] = counts.get(cx, 0) + 1
        filtered: List[str] = []
        for x in raw_opts:
            cx = _canon_cardno(x)
            if counts.get(cx, 0) > 0:
                filtered.append(x)
                counts[cx] -= 1
        if filtered:
            p0['options'] = list(filtered)
            gs.pending.append(p0)
            setattr(gs, '_poppin_pending_queue', q)
            gs.log.append(f"[PENDING] PoppinUp queued prompt ({len(filtered)} candidates)")
            return True
    setattr(gs, '_poppin_pending_queue', [])
    return False

def cmd_attempt(gs: GameState, cards_db: Dict[str, CardInfo]) -> None:
    if not gs.set_zone:
        gs.last_attempt_excess_hearts = {}
        gs.butterfly_paid_this_live = 0
        gs.tsunagaru_connect_bonus_this_live = 0
        gs.vivid_world_blue_mode_this_live = False
        gs.vivid_world_bonus_this_live = 0
        gs.log.append("[ATTEMPT] no set cards")
        # clear end-of-live state defensively
        gs.last_attempt_lives = []
        gs.last_attempt_ok = False
        gs.need_live_success_triggers = False
        gs.need_success_store_choice = False
        _clear_end_of_live_buffs(gs)
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


    # clear set zone (attempted)
    gs.set_zone = []

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
        gs.log.append(f"[ATTEMPT] result=SUCCESS total_score={total_score}")
        result_txt = f"SUCCESS (Score{total_score})"
    else:
        gs.log.append("[ATTEMPT] result=FAIL")
        result_txt = "FAIL"

    # UI banner (transient)
    gs.banner_text = result_txt
    gs.banner_ts = time.time()
    gs.banner_ttl = 4.0

    # Move attempted LIVE cards: by default they go to waiting room (green_room).
    if lives:
        gs.green_room.extend(lives)
        if ok_all:
            gs.log.append(f"[ZONE] waiting +{len(lives)} (success live)")
            # IMPORTANT (rules timing):
            # - Do NOT move a successful LIVE to success storage here.
            # - Do NOT run <ライブ成功時> triggers here.
            # These are handled in LIVE_RESOLVE (8.4 timing) so the just-succeeded LIVE
            # does NOT count as being in success storage during its own success-effect resolution.
            gs.last_attempt_lives = list(lives)
            gs.last_attempt_ok = True
            gs.need_live_success_triggers = True
            gs.need_success_store_choice = True
        else:
            gs.log.append(f"[ZONE] waiting +{len(lives)} (failed live)")
            gs.last_attempt_lives = []
            gs.last_attempt_ok = False
            gs.need_live_success_triggers = False
            gs.need_success_store_choice = False
            _clear_end_of_live_buffs(gs)
            gs.live_start_prompted = False
    else:
        gs.last_attempt_lives = []
        gs.last_attempt_ok = False
        gs.need_live_success_triggers = False
        gs.need_success_store_choice = False
        _clear_end_of_live_buffs(gs)
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

    # Special-case: Emma Verde bp3-008
    if _canon_cardno(getattr(ci, 'cardnumber', '') or '') == _EMMA_BP3_008_CN_CANON:
        key = f"{pos}:{_EMMA_BP3_008_CN_CANON}:emma_bp3_008_activate"
        used = int((getattr(gs, 'used_this_turn', {}) or {}).get(key, 0) or 0)
        if used >= 1:
            gs.log.append(f"[INFO] activate: already used this turn ({key})")
            return
        cands = _emma_bp3_008_wait_candidates(gs, cards_db, pos)
        if not cands:
            gs.log.append("[INFO] エマ・ヴェルデ: ウェイトにできる『虹ヶ咲』メンバーがいない")
            return
        opts = [_stage_pos_label(gs, cards_db, pp) for pp in cands]
        gs.pending.append({
            'kind': 'emma_bp3_008_wait_pick',
            'text': '【エマ・ヴェルデ】起動：このメンバー以外の『虹ヶ咲』メンバー1人をウェイト状態にする → カードを1枚引く',
            'options': list(opts),
            'pos_options': list(cands),
            'source_pos': pos,
            'source_cn': getattr(ci, 'cardnumber', '') or '',
            'ability_key': key,
        })
        gs.log.append(f"[PENDING] Emma bp3-008: choose 1 Nijigasaki member to set WAIT ({len(cands)} candidates)")
        return

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
                gs.green_room.append(slot.cardnumber)
                gs.stage[pos] = None
                gs.log.append(f"[COST] {pos}: {slot.cardnumber} -> waiting room")

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
        gs.green_room.append(slot.cardnumber)
        gs.stage[pos] = None
        gs.log.append(f"[ACT] {pos}: {ci.cardnumber} -> waiting room (cost)")

    if _has_green_live_take_ability(ci):
        cands = _green_live_candidates(gs, cards_db)
        if not cands:
            gs.log.append("[ACT] no LIVE in waiting room to take")
        elif len(cands) == 1:
            take_cn = cands[0]
            gs.green_room.remove(take_cn)
            gs.hand.append(take_cn)
            gs.log.append(f"[ACT] took LIVE {take_cn} from waiting room -> hand")
        else:
            gs.pending.append({
                "kind": "pick_live_from_green",
                "text": "控え室のライブカードを1枚手札に加える",
                "options": cands,
            })
            gs.log.append(f"[PENDING] pick 1 LIVE from waiting room ({len(cands)} candidates)")

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
        elif len(cands) == 1:
            take_cn = cands[0]
            gs.green_room.remove(take_cn)
            gs.hand.append(take_cn)
            gs.log.append(f"[ACT] took MEMBER {take_cn} from waiting room -> hand")
        else:
            gs.pending.append({
                "kind": "pick_member_from_green",
                "text": "控え室のメンバーカードを1枚手札に加える",
                "options": cands,
            })
            gs.log.append(f"[PENDING] pick 1 MEMBER from waiting room ({len(cands)} candidates)")



def cmd_resolve_pending(gs: GameState, cards_db: Dict[str, CardInfo], idx: int, choice: str, rng: Optional[random.Random] = None) -> None:
    if idx < 0 or idx >= len(gs.pending):
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
        for i, t in enumerate(queue):
            txt = _auto_trigger_option_text(t)
            if txt and txt == choice_str:
                pick_i = i
                break
            if _canon_cardno(str(t.get('source_cn', '') or '')) == cn_choice:
                pick_i = i
                break
        if pick_i is None:
            gs.log.append(f"[ERR] auto_order: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        trig = queue.pop(pick_i)
        if str(trig.get('kind','')) == 'success_auto_labella':
            _put_wait_energy_from_deck(gs, 1, reason='La Bella Patria')
        elif str(trig.get('kind','')) == 'success_auto_poppin':
            _pp_q = list(getattr(gs, '_poppin_pending_queue', []) or [])
            if _pp_q:
                gs.pending.append(_pp_q[0])
                setattr(gs, '_poppin_pending_queue', _pp_q[1:])
            else:
                gs.log.append('[INFO] PoppinUp: no pending queue')
        else:
            _exec_auto_trigger(gs, cards_db, trig)

        # Defer remaining triggers until the current trigger (and any nested pending prompts) finishes.
        if queue:
            setattr(gs, '_deferred_auto_queue', list(queue))
            setattr(gs, '_deferred_auto_text', str(p.get('text', '') or '自動効果が複数発生：解決するカードを選択（1つずつ）'))
            _enqueue_auto_order_from_deferred()
        return

    # --- Generic effect-engine prompts ---

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
        gs.log.append(f"[AUTO] {src}: confirm_effect -> {'applied' if applied else 'no_match'} {after_eff}")
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
        return


    if kind == 'live_start_numeric_effect':
        low = choice_str.lower()
        if low not in ('ok', 'apply', 'yes', 'y', '1', 'true', 'use', 'go', 'confirm', 'はい', '使う'):
            gs.log.append(f"[ERR] live_start_numeric_effect: invalid choice {choice_str}")
            gs.pending.append(p)
            return
        set_idx = p.get('set_idx', None)
        _mark_live_start_set_idx_resolved(gs, set_idx)
        src = str(p.get('source_cn', '') or '')
        eff_code = str(p.get('effect_code', '') or '')
        if eff_code == 'bp3_019_score':
            bonus = int(_bokulive_score_bonus(src, gs, cards_db, set_idx=set_idx))
            gs.log.append(f"[AUTO] {src}[ライブ開始時]: score {bonus:+d}")
        elif eff_code == 'bp4_021_req_score':
            red = int(_heartbeat_required_any_reduction(src, gs, cards_db, set_idx=set_idx))
            bonus = int(_heartbeat_score_bonus(src, gs, cards_db, set_idx=set_idx))
            gs.log.append(f"[AUTO] {src}[ライブ開始時]: required(any) -{red}, score {bonus:+d}")
        else:
            gs.log.append(f"[AUTO] {src}[ライブ開始時]: resolved")
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
            need_e = max(0, cost_n)
            if need_e <= 0:
                gs.log.append('[ERR] pay_or_skip: invalid energy cost')
                return
            if int(getattr(gs, 'energy_active', 0) or 0) < need_e:
                gs.log.append(f'[ERR] pay_or_skip: not enough active energy (need {need_e})')
                return
            gs.energy_active -= need_e
            gs.energy_wait += need_e
            gs.log.append(f'[COST] {src}: paid [E]{need_e}')
            applied = False
            if after_eff:
                try:
                    rng = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
                except Exception:
                    rng = random.Random()
                applied = bool(try_apply_effect_template(gs, rng, cards_db, after_eff, ctx0))
            gs.log.append(f"[AUTO] {src}: energy cost -> {'applied' if applied else 'no_match'} {after_eff}")
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
        return




    if kind == 'pick_success_to_store':
        lives = list(p.get('lives', []) or [])
        if not lives:
            gs.log.append('[INFO] success_store: no successful live cards')
            return
        c0 = str(choice_str or '').strip()
        if c0.lower() == 'skip':
            gs.log.append('[ACT] success_store: skipped')
            _clear_end_of_live_buffs(gs)
            gs.live_start_prompted = False
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
        # move the chosen card from waiting room to success storage
        pick_cn = None
        if pick in gs.green_room:
            pick_cn = pick
        else:
            for v in _cardno_variants(pick):
                if v in gs.green_room:
                    pick_cn = v
                    break
        if not pick_cn:
            # it should exist, but don't crash
            pick_cn = pick
        try:
            if pick_cn in gs.green_room:
                gs.green_room.remove(pick_cn)
        except Exception:
            pass
        try:
            gs.success_zone.append(pick_cn)
        except Exception:
            gs.success_zone = list(getattr(gs, 'success_zone', []) or []) + [pick_cn]
        gs.log.append(f"[ACT] success_store: moved {pick_cn} -> success storage")
        _clear_end_of_live_buffs(gs)
        gs.live_start_prompted = False
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
        except Exception:
            pass
        gs.log.append(f"[ACT] live_start_success_heart: choose={col} (per success card, until end_of_live)")
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
        return


    if kind in ('choose_live_from_green','choose_member_from_green'):
        want_kind = 'LIVE' if kind=='choose_live_from_green' else 'MEMBER'
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
        gs.green_room.remove(pick_cn)
        gs.hand.append(pick_cn)
        gs.log.append(f"[ACT] retrieved {want_kind} {pick_cn} -> hand")
        # n>1 連続回収
        remaining_picks = int(p.get('remaining_picks', 1) or 1) - 1
        if remaining_picks > 0:
            _enqueue_choose_from_green(gs, cards_db, kind=want_kind, n=remaining_picks,
                                       group=str(p.get('want_group', '') or ''))
            return
        # resume parent prompt if provided (e.g., choose_effects)
        _r = p.get('_resume') if isinstance(p, dict) else None
        if _r:
            gs.pending.append(_r)
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
        if want_group and (want_group not in str(getattr(ci2, 'group', '') or '')):
            gs.log.append(f"[ERR] topdeck_from_green: group mismatch {pick_cn}")
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
            if want_group and (want_group not in str(getattr(ci, 'group', '') or '')):
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

    if kind == 'live_start_butterfly_pay':
        low = str(choice_str or '').strip().lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append('[SKIP] Butterfly live-start skipped')
            return
        if low not in ('pay', 'yes', 'y', '1', 'true'):
            gs.log.append(f'[ERR] Butterfly live-start: invalid choice {choice_str}')
            return
        if int(getattr(gs, 'energy_active', 0) or 0) < 2:
            gs.log.append('[ERR] Butterfly live-start: not enough active energy')
            return
        if not _has_nijigasaki_member_on_stage(gs, cards_db):
            gs.log.append('[INFO] Butterfly live-start: no Nijigasaki member on stage')
            return
        gs.energy_active = max(0, int(getattr(gs, 'energy_active', 0) or 0) - 2)
        gs.butterfly_paid_this_live = int(getattr(gs, 'butterfly_paid_this_live', 0) or 0) + 1
        gs.log.append('[AUTO] Butterfly live-start: paid E2 -> score +1')
        return

    if kind == 'neo_sky_execute':
        drew = draw(gs, 3, None)
        gs.log.append(f'[AUTO] NEO SKY, NEO MAP!: drew {drew}')
        _enqueue_topdeck_from_hand(gs, 3, 'NEO SKY, NEO MAP!')
        return

    if kind == 'opponent_wait_notify':
        # 相手への効果通知：OKで閉じるだけ（相手盤面は手動処理）
        gs.log.append('[ACK] opponent_wait_notify: confirmed by user')
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

    if kind == 'tsunagaru_connect_execute':
        k = int(p.get('k', 0) or 0)
        _enqueue_choose_top_keep_one(gs, k, 'ツナガルコネクト')
        return

    if kind == 'choose_top_keep_one':
        ok = _resolve_choose_top_keep_one(gs, p, choice_str, cards_db)
        if not ok:
            return
        return

    if kind == 'live_start_shizuku_bp1_003_pay':
        pos = str(p.get('pos', '') or '').upper()
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f"[SKIP] prompt: stage {pos} empty (ignored)")
            return
        low = str(choice_str or '').strip().lower()
        if low in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append(f"[SKIP] {pos}: Shizuku bp1-003 live-start skipped")
            return
        if low not in ('pay', 'yes', 'y', '1', 'true'):
            gs.log.append(f"[ERR] Shizuku bp1-003 live-start: invalid choice {choice_str}")
            return
        if not pay_energy(gs, 1):
            gs.log.append(f"[ERR] ability: insufficient energy for [E]1 (have {gs.energy_active})")
            return
        gs.pending.insert(0, {
            'kind': 'live_start_shizuku_bp1_003_choose_color',
            'pos': pos,
            'cn': str(p.get('cn', '') or ''),
            'text': f"{pos}: 桜坂しずく ライブ開始時 → 好きなハート色を選ぶ",
            'options': ['桃', '赤', '黄', '緑', '青', '紫'],
        })
        gs.log.append(f"[PENDING] {pos}: Shizuku bp1-003 choose heart color")
        return

    if kind == 'live_start_shizuku_bp1_003_choose_color':
        pos = str(p.get('pos', '') or '').upper()
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f"[SKIP] prompt: stage {pos} empty (ignored)")
            return
        ch = str(choice_str or '').strip()
        m = {
            '桃': 'pink',
            '赤': 'red',
            '黄': 'yellow',
            '緑': 'green',
            '青': 'blue',
            '紫': 'purple',
            'pink': 'pink',
            'red': 'red',
            'yellow': 'yellow',
            'green': 'green',
            'blue': 'blue',
            'purple': 'purple',
        }
        col = m.get(ch, '')
        if not col:
            gs.log.append(f"[ERR] Shizuku bp1-003 choose color: invalid choice '{ch}'")
            return
        _grant_temp_heart(slot, col, 1)
        gs.log.append(f"[AUTO] {pos}: Shizuku bp1-003 -> temp heart +1 {col} (until end of live)")
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
            return
        slot2.active = True
        gs.log.append(f"[ACT] stage {pos2} set ACTIVE")
        return

    if kind == 'emma_bp3_008_wait_pick':
        raw = str(choice_str or '').strip()
        pos2 = (raw[:1].upper() if raw else '')
        pos_opts = list(p.get('pos_options', []) or [])
        src_pos = str(p.get('source_pos', '') or '').upper()
        key = str(p.get('ability_key', '') or '')
        if pos2 not in ('L','C','R') or (pos_opts and pos2 not in pos_opts):
            gs.log.append(f"[ERR] Emma bp3-008: invalid target {choice_str}")
            return
        slot2 = (gs.stage or {}).get(pos2)
        if not slot2:
            gs.log.append(f"[ERR] Emma bp3-008: empty stage {pos2}")
            return
        slot2.active = False
        rng2 = random.Random(int(getattr(gs, 'seed', 0) or 0) + int(getattr(gs, 'turn', 0) or 0))
        drew = draw(gs, 1, rng2)
        if key:
            try:
                gs.used_this_turn[key] = 1
            except Exception:
                gs.used_this_turn = {key: 1}
        gs.log.append(f"[ACT] Emma bp3-008: {pos2} set WAIT -> drew {drew}")
        return

    if kind == 'emma_bp3_008_live_start_pay':
        src_pos = str(p.get('pos', '') or '').upper()
        pos_opts = list(p.get('pos_options', []) or [])
        if choice_str.lower() not in ('pay', 'yes', 'y', '1', 'true'):
            gs.log.append('[SKIP] Emma bp3-008 live-start skipped')
            return
        if len(list(getattr(gs, 'hand', []) or [])) < 2:
            gs.log.append('[ERR] Emma bp3-008 live-start: not enough cards in hand for discard 2')
            return
        opts = [_stage_pos_label(gs, cards_db, pp) for pp in pos_opts]
        resume = {
            'kind': 'emma_bp3_008_live_start_pick',
            'text': '【エマ・ヴェルデ】ライブ開始時：アクティブにする『虹ヶ咲』メンバーを選ぶ',
            'options': list(opts),
            'pos_options': list(pos_opts),
            'source_pos': src_pos,
        }
        gs.pending.append({
            'kind': 'discard_from_hand',
            'remaining': 2,
            'text': '手札を2枚控え室に置く',
            'options': list(gs.hand),
            '_resume': resume,
        })
        return

    if kind == 'emma_bp3_008_live_start_pick':
        raw = str(choice_str or '').strip()
        pos2 = (raw[:1].upper() if raw else '')
        pos_opts = list(p.get('pos_options', []) or [])
        src_pos = str(p.get('source_pos', '') or '').upper()
        if pos2 not in ('L','C','R') or (pos_opts and pos2 not in pos_opts):
            gs.log.append(f"[ERR] Emma bp3-008 live-start: invalid target {choice_str}")
            return
        src_slot = (gs.stage or {}).get(src_pos)
        slot2 = (gs.stage or {}).get(pos2)
        if not src_slot or not slot2:
            gs.log.append('[ERR] Emma bp3-008 live-start: source/target missing')
            return
        slot2.active = True
        _grant_temp_heart(src_slot, 'green', 1)
        _grant_temp_heart(slot2, 'green', 1)
        gs.log.append(f"[AUTO] Emma bp3-008 live-start: {pos2} set ACTIVE; {src_pos} and {pos2} gain green +1 until end of live")
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
            # 手札を捨てるコスト（汎用）→ ユーザーに選ばせる
            if cost_kind == 'discard_from_hand' and cost_n > 0:
                if len(gs.hand) < cost_n:
                    gs.log.append(f"[ERR] live_start_pay_effect: not enough cards in hand (need {cost_n})")
                    return
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
    if kind == 'live_start_rise_up_high_pick':
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
        gs.log.append(f'[AUTO] RiseUpHigh: {pos} temp blade +1 (until end of live)')
        return
    # 1d) Live-success Poppin' Up!: pick 1 Nijigasaki card among yell reveals -> hand (Skip allowed)
    if kind == 'pick_poppinup_from_yell':
        if choice_str.lower() == 'skip':
            gs.log.append("[SKIP] PoppinUp: skipped")
            _enqueue_next_poppin_prompt(gs)
            return
        cn = _canon_cardno(choice_str)
        opts = list(p.get('options', []) or [])
        if opts and (not any(_canon_cardno(x) == cn for x in opts)):
            gs.log.append(f"[ERR] PoppinUp: invalid choice {choice_str}")
            return
        moved = None
        # remove from resolve_zone first, then green_room
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
            gs.log.append(f"[ERR] PoppinUp: chosen card not found in zones {cn}")
            _enqueue_next_poppin_prompt(gs)
            return
        gs.hand.append(moved)
        # remove one occurrence from tracker
        try:
            pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
            for i, x in enumerate(list(pool)):
                if _canon_cardno(x) == cn:
                    pool.pop(i)
                    break
            setattr(gs, '_yell_revealed_this_live', pool)
        except Exception:
            pass
        gs.log.append(f"[ACT] PoppinUp: took {moved} -> hand")
        _enqueue_next_poppin_prompt(gs)
        return

    # 1e) Generic yell-retrieve: pick 1 card from yell reveals -> hand
    if kind == 'pick_from_yell':
        opts = list(p.get('options', []) or [])
        if choice_str.lower() in ('skip', '__skip__', 'no', 'n', '0', 'false'):
            gs.log.append('[SKIP] pick_from_yell: skipped')
            return
        cn = _canon_cardno(choice_str)
        if opts and not any(_canon_cardno(x) == cn for x in opts):
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
        # remove from tracker
        try:
            pool = list(getattr(gs, '_yell_revealed_this_live', []) or [])
            for i, x in enumerate(list(pool)):
                if _canon_cardno(x) == cn:
                    pool.pop(i)
                    break
            setattr(gs, '_yell_revealed_this_live', pool)
        except Exception:
            pass
        gs.log.append(f'[ACT] pick_from_yell: took {moved} -> hand')
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

# 2) Pick 1 LIVE from green room to face-up set_zone
    if kind == 'pick_live_from_green_to_set_zone':
        if choice_str.lower() in ('skip', 'no', 'n', '0', 'false'):
            gs.log.append('[SKIP] pick live from green room to set_zone')
            return
        opts = p.get('options', [])
        cn = _canon_cardno(choice_str)
        if isinstance(opts, list) and opts and cn not in [_canon_cardno(x) for x in opts]:
            gs.log.append(f"[ERR] pick live to set_zone: invalid choice {cn}")
            return
        src = str(p.get('source_cn', '') or '')
        if not _move_live_from_green_to_set_zone(gs, cards_db, cn, source_cn=src or cn):
            gs.log.append(f"[ERR] pick live to set_zone: could not move {cn}")
            return
        _bump_next_live_set_limit_reduction(gs, int(p.get('reduce_next_live_set', 1) or 1), source_cn=src or cn)
        return

    if kind == 'pick_named_live_from_hand_to_set_zone':
        if choice_str.lower() in ('skip', 'no', 'n', '0', 'false'):
            gs.log.append('[SKIP] pick named live from hand to set_zone')
            return
        opts = p.get('options', [])
        cn = _canon_cardno(choice_str)
        if isinstance(opts, list) and opts and cn not in [_canon_cardno(x) for x in opts]:
            gs.log.append(f"[ERR] pick named live to set_zone: invalid choice {cn}")
            return
        required_name = str(p.get('required_name', '') or '')
        src = str(p.get('source_cn', '') or '')
        if not _move_named_live_from_hand_to_set_zone(gs, cards_db, cn, required_name, source_cn=src or cn):
            gs.log.append(f"[ERR] pick named live to set_zone: could not move {cn}")
            return
        _bump_next_live_set_limit_reduction(gs, int(p.get('reduce_next_live_set', 1) or 1), source_cn=src or cn)
        return

    if kind == 'dive_faceup_pick_stage_member_blade2':
        pos = str(choice_str or '').upper()
        if pos not in ('L', 'C', 'R'):
            gs.log.append(f"[ERR] dive faceup bonus: invalid choice {choice_str}")
            return
        src = str(p.get('source_cn', '') or 'PL!N-bp4-026')
        if not _apply_temp_blade_to_stage_pos(gs, pos, 2, source_cn=src):
            gs.log.append(f"[ERR] dive faceup bonus: no member at {pos}")
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

    # 3) Shioriko enter (PL!N-pb1-010): choose mode
    #    - energy: move 1 energy from wait -> active automatically
    #    - topdeck: choose up to 2 Nijigasaki LIVE from green room and place on deck top (order selectable)
    if kind == "choose_shioriko_enter":
        mode = choice_str.lower()
        if mode in ("energy", "e", "0", "a"):
            if gs.energy_wait > 0:
                gs.energy_wait -= 1
                gs.energy_active += 1
                gs.log.append("[AUTO] 栞子[登場]: chose ENERGY -> moved 1 (wait->active)")
            else:
                gs.log.append("[AUTO] 栞子[登場]: chose ENERGY but no wait energy")
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

    # 4) Shioriko topdeck pick #1
    if kind == "shioriko_topdeck_pick1":
        if choice_str.lower() in ("skip", "no", "n", "0", "false"):
            gs.log.append("[SKIP] 栞子[登場]: topdeck 0 cards")
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

    # 5) Shioriko topdeck pick #2
    if kind == "shioriko_topdeck_pick2":
        if choice_str.lower() in ("skip", "no", "n", "0", "false"):
            gs.log.append("[SKIP] 栞子[登場]: topdeck only 1 card")
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
    red = int(getattr(gs, 'next_live_set_limit_reduction', 0) or 0)
    gs.current_live_set_limit = max(0, 3 - red)
    gs.next_live_set_limit_reduction = 0
    gs.live_start_prompted = False
    gs.turn_blade_bonus = 0
    preload = len(getattr(gs, 'set_zone', []) or [])
    gs.log.append(f"[PHASE] LIVE_SET (choose up to {gs.current_live_set_limit} from hand; preloaded={preload}) turn={gs.turn}")


def _advance_to_next_turn(gs: GameState, rng: random.Random) -> None:
    gs.turn += 1
    begin_turn(gs, rng)


def cmd_next(gs: GameState, rng: random.Random, cards_db: Dict[str, CardInfo], indices: Optional[List[int]] = None) -> None:
    """Automatic progression for the current phase.

    The intended flow is:
      MAIN -> (Next/End Turn) -> LIVE_SET -> (Next) -> LIVE_CONFIRM -> (resolve live-start prompts)
      -> LIVE_PERF -> (Next) -> LIVE_ATTEMPT -> (Next) -> LIVE_RESOLVE -> (Next) -> next turn.
    """
    if indices is None:
        indices = []

    if gs.pending:
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
                if (not gs.pending) and _enqueue_next_poppin_prompt(gs):
                    return
                if gs.pending:
                    return

        # 2) Winner-based success storage decision (8.4.7).
        #    Since this simulator has no opponent, we let the user decide whether to store
        #    a successful LIVE into 成功ライブカード置き場 (skip allowed).
        if bool(getattr(gs, 'need_success_store_choice', False)):
            if bool(getattr(gs, 'last_attempt_ok', False)) and list(getattr(gs, 'last_attempt_lives', []) or []):
                lives = list(getattr(gs, 'last_attempt_lives', []) or [])
                gs.pending.append({
                    'kind': 'pick_success_to_store',
                    'text': '成功ライブカード置き場に置くカードを選択（Skip可）',
                    # candidates are LIVE cardnumbers (skip is a separate action)
                    'options': list(lives),
                    'lives': list(lives),
                })
                gs.need_success_store_choice = False
                gs.log.append(f"[PENDING] success store choice ({len(lives)} lives)")
                return
            gs.need_success_store_choice = False

        # 3) ACK revealed cards (resolve zone)
        if gs.resolve_zone:
            cmd_ack(gs, rng)
        if gs.resolve_zone:
            gs.log.append("[WARN] next: resolve_zone still not empty after ACK; abort.")
            return

        # Defensive cleanup if success-store prompt was skipped by older saves
        if bool(getattr(gs, 'last_attempt_ok', False)) and list(getattr(gs, 'last_attempt_lives', []) or []):
            _clear_end_of_live_buffs(gs)
            gs.live_start_prompted = False

        # Clear per-live cheer reveal tracker
        try:
            setattr(gs, '_yell_revealed_this_live', [])
        except Exception:
            pass

        # Clear last-attempt helpers
        gs.last_attempt_lives = []
        gs.last_attempt_ok = False

        _advance_to_next_turn(gs, rng)
        return

    gs.log.append(f"[WARN] next: unknown phase={gs.phase}")

