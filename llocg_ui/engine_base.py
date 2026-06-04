# -*- coding: utf-8 -*-
# BUILD_TAG: engine_base_under_energy_cost_check_20260604a
from __future__ import annotations

"""llocg_ui.engine_base

共通データクラス・helper関数群。engine_effects.py と engine.py 両方から import される。
このファイルは他のエンジンファイルを import しない（循環インポート防止）。
"""

import json
import re
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
    """Return True if cost requires this member to become WAIT (but NOT sent to green)."""
    t = str(cost_text or '').strip()
    if 'ウェイトにする' in t and 'このメンバー' in t:
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
            if not _match_effect_template(eff):
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

def stage_blade(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    s = 0
    for slot in gs.stage.values():
        if not slot or not slot.active:
            continue
        c = _get_card(cards_db, slot.cardnumber)
        base_b = (int(c.blade) if c else 0)
        temp_b = int(getattr(slot, "temp_blade", 0) or 0)
        under_b = int(getattr(slot, "energy_under", 0) or 0) if _has_under_energy_blade_bonus(c) else 0
        s += base_b + temp_b + under_b
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

def owned_base_hearts(gs: GameState, cards_db: Dict[str, CardInfo]) -> Dict[str, int]:
    pool: Dict[str, int] = {}
    for slot in gs.stage.values():
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
        for k, v in (getattr(slot, 'temp_hearts', {}) or {}).items():
            pool[k] = pool.get(k, 0) + int(v)

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


def _solve_multi_live_allocations(lives: List[str], cards_db: Dict[str, CardInfo], owned: Dict[str, int]) -> Tuple[bool, Dict[str, Dict[str, Any]]]:
    """Find allocations for ALL live cards without reusing hearts.

    Returns:
      ok_all, alloc_map[cn] = alloc dict (use_* keys).
    """
    lives = list(lives or [])
    pool0 = {str(k).lower(): int(v or 0) for k, v in (owned or {}).items()}
    pool0.setdefault("all", 0)

    # prefer canonical color order for deterministic state keys
    canon = ["pink", "red", "yellow", "green", "blue", "purple"]
    # include any extra keys that may appear (should be none, but safe)
    extra = sorted([k for k in pool0.keys() if k not in ("any", "all") and k not in canon])
    colors = [c for c in canon if (c in pool0)] + extra
    # Also include any colors that appear only in req (rare, but safe)
    for cn in lives:
        c = _get_card(cards_db, cn)
        req = _effective_live_required_hearts(cn, c, globals().get('_CURRENT_GS_FOR_ATTEMPT'))
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
    for cn in lives:
        ci = _get_card(cards_db, cn)
        reqs.append((cn, _effective_live_required_hearts(cn, ci, globals().get('_CURRENT_GS_FOR_ATTEMPT'))))

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
            cn, req = perm[i]
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


