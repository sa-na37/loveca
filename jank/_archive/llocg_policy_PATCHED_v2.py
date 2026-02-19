from __future__ import annotations
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLCG policy (decision-making)

This module contains heuristics for:
- Member play / baton-touch decisions
- Live set selection decisions

It is intentionally side-effectful on PlayerState (mutates hand/stage/energy),
but keeps the heuristics isolated from core rules and IO.
"""


from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Callable

# Type aliases (duck-typed; we avoid importing the main module to prevent circular imports)
Card = Any
PlayerState = Any

CardLabelFn = Callable[[Optional[Card], Optional[str]], str]
PayEnergyFn = Callable[[PlayerState, int], bool]
ApplyEnterEffectsFn = Callable[[PlayerState, Dict[str, Card], Card, int, List[str]], None]


@dataclass
class PolicyConfig:
    """Tunable knobs. Defaults are conservative."""
    forbid_cost_decrease_baton: bool = True


def _stage_total_cost(p: PlayerState) -> int:
    total = 0
    for slot in ("L", "C", "R"):
        m = p.stage.get(slot)
        if m is not None:
            total += int(getattr(m.card, "cost", 0) or 0)
    return total


def _choose_plan_is_13(p: PlayerState, card_db: Dict[str, Card]) -> bool:
    """Heuristic: if a 13-cost MEMBER is present in hand/stage/green_room, prefer the 13-plan."""
    for cn in getattr(p, "hand", []):
        c = card_db.get(cn)
        if c and getattr(c, "type", None) == "MEMBER" and int(getattr(c, "cost", 0) or 0) == 13:
            return True
    for slot in ("L", "C", "R"):
        m = p.stage.get(slot)
        if m and int(getattr(m.card, "cost", 0) or 0) == 13:
            return True
    for cn in getattr(p, "green_room", []):
        c = card_db.get(cn)
        if c and getattr(c, "type", None) == "MEMBER" and int(getattr(c, "cost", 0) or 0) == 13:
            return True
    return False


def _desired_stage_total(turn: int, prefer_13: bool) -> int:
    """Soft target based on the user's ideal transitions (totals only)."""
    if turn <= 1:
        return 4
    if turn == 2:
        return 9
    if turn == 3:
        return 15
    if turn == 4:
        return 22
    if turn >= 5:
        return 35 if prefer_13 else 33
    return 0


def can_specify_stage_area(p: PlayerState, slot: str, turn: int) -> bool:
    """Rule check: cannot target a stage area whose member entered this turn."""
    m = p.stage.get(slot)
    if m is None:
        return True
    return (getattr(m, "entered_turn", None) != turn)


def play_member_best_effort(
    p: PlayerState,
    card_db: Dict[str, Card],
    turn: int,
    log: List[str],
    *,
    pay_energy: PayEnergyFn,
    apply_enter_effects: ApplyEnterEffectsFn,
    card_label: CardLabelFn,
    cfg: Optional[PolicyConfig] = None,
) -> int:
    """Play members to push stage towards an intended cost trajectory.

    Primary goals (in order):
    1) Avoid bad baton-touch: do not reduce total printed stage cost.
    2) Push total printed stage cost toward a per-turn soft target.
    3) Maximize printed cost played while minimizing effective cost.
    """
    cfg = cfg or PolicyConfig()
    total_cost_played = 0

    prefer_13 = _choose_plan_is_13(p, card_db)
    target_total = _desired_stage_total(turn, prefer_13)

    def member_candidates() -> List[Tuple[Tuple[int, int, int, int, int], int, str, str, int, int]]:
        # returns list of: (score_tuple, hand_index, slot, cn, printed, eff_cost)
        cands = []
        before_total = _stage_total_cost(p)

        for i, cn in enumerate(p.hand):
            card = card_db.get(cn)
            if not card or getattr(card, "type", None) != "MEMBER":
                continue
            printed = int(getattr(card, "cost", 0) or 0)

            for slot in ("L", "C", "R"):
                if not can_specify_stage_area(p, slot, turn):
                    continue

                existing = p.stage.get(slot)
                reduction = int(getattr(existing.card, "cost", 0) or 0) if existing else 0
                eff_cost = max(0, printed - reduction)
                # 20-cost Trio (LL-bp2-001): base cost becomes 20 - hand size (>=0), then baton-touch reduction applies.
                if printed >= 20 and getattr(card, 'number', None) == 'LL-bp2-001':
                    base20 = max(0, 20 - len(p.hand))
                    eff_cost = max(0, base20 - reduction)

                after_total = before_total - (reduction if existing else 0) + printed
                delta_total = after_total - before_total

                if existing is not None and cfg.forbid_cost_decrease_baton and delta_total < 0:
                    continue

                dist = abs(after_total - target_total)

                # Smaller dist is better; larger after_total is better; larger printed is better;
                # smaller eff_cost is better; larger reduction is better.
                score = (dist, -after_total, -printed, eff_cost, -reduction)
                cands.append((score, i, slot, cn, printed, eff_cost))

        return cands

    while True:
        cands = member_candidates()
        if not cands:
            break

        cands.sort(key=lambda t: t[0])
        chosen = None
        for score, i, slot, cn, printed, eff_cost in cands:
            if getattr(p, "energy_active", 0) >= eff_cost:
                chosen = (i, slot, cn, printed, eff_cost)
                break
        if not chosen:
            break

        i, slot, cn, printed, eff_cost = chosen
        card = card_db[cn]
        existing = p.stage.get(slot)

        if existing is not None:
            p.green_room.append(existing.card.cardnumber)
            log.append(f"  baton-touch: {slot} {card_label(existing.card, None)} -> green_room (reduce {existing.card.cost})")

        if not pay_energy(p, eff_cost):
            break

        # create StageMember without importing the class: reuse existing instance type if possible.
        if existing is not None:
            sm_cls = type(existing)
            p.stage[slot] = sm_cls(card=card, entered_turn=turn, state="ACTIVE")
        else:
            # fallback: infer from any existing stage member
            sample = None
            for s2 in ("L","C","R"):
                if p.stage.get(s2) is not None:
                    sample = p.stage.get(s2)
                    break
            if sample is not None:
                sm_cls = type(sample)
                p.stage[slot] = sm_cls(card=card, entered_turn=turn, state="ACTIVE")
            else:
                class _SM:
                    def __init__(self, card, entered_turn, state):
                        self.card = card
                        self.entered_turn = entered_turn
                        self.state = state
                p.stage[slot] = _SM(card, turn, "ACTIVE")

        p.hand.pop(i)

        total_cost_played += printed
        log.append(f"  play member: {slot} {card_label(card, None)} cost={printed} eff={eff_cost} (E active now {p.energy_active})")
        apply_enter_effects(p, card_db, card, turn, log)

    return total_cost_played


def choose_live_set_cards(p: Player, card_db: Dict[str, Card], turn: int) -> Tuple[List[str], Dict[str, Any]]:
    """
    Choose up to 3 cards to set this turn.
    - Prefer makeable LIVE first (success possible with current stage stats).
    - Then fill with non-LIVE according to priorities (for "it looks like a human" behavior):
        2-cost (turn 1-2 highest) >= 4-cost >> 11-cost.
    - Avoid setting:
        * unmakeable LIVE
        * 20-cost members (placeholder "almost forbidden")
        * the last remaining 11-cost member in hand (reserve for next turn plans)
    """
    stats = compute_stage_stats(p)
    makeable_lives: List[str] = []
    unmakeable_lives: List[str] = []
    nonlive: List[str] = []

    # count 11-cost members in current hand
    cnt_11 = 0
    for cn in p.hand:
        c = card_db.get(cn)
        if c and c.type == "MEMBER" and int(c.cost or 0) == 11:
            cnt_11 += 1

    def is_unmakeable_live(cn: str) -> bool:
        c = card_db.get(cn)
        if not c or c.type != "LIVE":
            return False
        return not is_live_makeable(c, stats)

    def is_forbidden_set(cn: str) -> bool:
        c = card_db.get(cn)
        if not c:
            return True
        # forbid unmakeable lives for now (will relax after learning)
        if c.type == "LIVE" and not is_live_makeable(c, stats):
            return True
        # temporarily "almost forbidden" 20-cost members
        if c.type == "MEMBER" and int(c.cost or 0) >= 20:
            return True
        # reserve 11-cost members for TURN 3 by default, and never set the only copy
        if c.type == "MEMBER" and int(c.cost or 0) == 11:
            if turn < 3:
                return True
            if cnt_11 <= 1:
                return True
        return False

    for cn in p.hand:
        c = card_db.get(cn)
        if not c:
            continue
        if c.type == "LIVE":
            (makeable_lives if is_live_makeable(c, stats) else unmakeable_lives).append(cn)
        else:
            nonlive.append(cn)

    chosen: List[str] = []
    meta: Dict[str, Any] = {"stats": stats, "makeable_lives": 0}

    # 1) choose 0-1 best makeable LIVE (we keep it conservative to avoid starving next-turn hand)
    makeable_lives_sorted = sorted(makeable_lives, key=lambda cn: live_difficulty(card_db.get(cn), stats))
    for cn in makeable_lives_sorted:
        if len(chosen) >= 3:
            break
        if is_forbidden_set(cn):
            continue
        chosen.append(cn)
        meta["makeable_lives"] += 1
        # keep at most 1 live for now unless hand is huge
        if meta["makeable_lives"] >= 1 and len(p.hand) <= 8:
            break

    # 2) fill with non-live cards
    def nonlive_priority(cn: str) -> int:
        c = card_db.get(cn)
        if not c:
            return -10**9
        if is_forbidden_set(cn):
            return -10**9
        if c.type == "MEMBER":
            cost = int(c.cost or 0)
            if cost == 2:
                return 9000 if turn <= 2 else 7000
            if cost == 4:
                return 6000
            if cost == 11:
                return 100  # very low
            return 1000
        # treat other types (e.g., EVENT) as mid priority
        return 800

    nonlive_sorted = sorted(nonlive, key=nonlive_priority, reverse=True)
    for cn in nonlive_sorted:
        if len(chosen) >= 3:
            break
        if cn in chosen:
            continue
        if nonlive_priority(cn) <= 0:
            continue
        chosen.append(cn)

    return chosen, meta
