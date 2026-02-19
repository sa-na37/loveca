#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLCG trace formatting utilities."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable

Card = Any
PlayerState = Any
CardLabelFn = Callable[[Optional[Card], Optional[str]], str]

def _fmt_energy(p: PlayerState) -> str:
    return f"E(active={getattr(p,'energy_active',0)}, wait={getattr(p,'energy_wait',0)})"

def _fmt_stage(p: PlayerState, card_label: CardLabelFn) -> List[str]:
    out: List[str] = []
    total = 0
    for slot in ("L","C","R"):
        sm = p.stage.get(slot)
        if sm is None:
            out.append(f"  {slot}: (empty)")
        else:
            c = sm.card
            total += int(getattr(c,'cost',0) or 0)
            out.append(f"  {slot}: {card_label(c, None)} cost={getattr(c,'cost',0)} entered={getattr(sm,'entered_turn',None)} state={getattr(sm,'state',None)}")
    out.append(f"  stage_total_cost={total}")
    return out

def _fmt_hand(p: PlayerState, card_db: Dict[str, Card], card_label: CardLabelFn) -> str:
    return ", ".join(card_label(card_db.get(cn), cn) for cn in getattr(p,'hand',[]))


@dataclass
class TraceWriter:
    card_db: Dict[str, Card]
    card_label: CardLabelFn
    lines: List[str]

    def __init__(self, card_db: Dict[str, Card], card_label: CardLabelFn):
        self.card_db = card_db
        self.card_label = card_label
        self.lines = []

    def setup(self, initial_hand: str, mulligan_lines: List[str], energy_active: int):
        self.lines.append("=== SETUP ===")
        self.lines.append(f"Initial hand: {initial_hand}")
        self.lines.extend(mulligan_lines)
        self.lines.append(f"Initial energy active={energy_active}")
        self.lines.append("")

    def turn_header(self, turn: int, p: PlayerState):
        self.lines.append(f"=== TURN {turn} ===")
        self.lines.append(_fmt_energy(p))

    def turn_start_hand(self, p: PlayerState):
        self.lines.append("Turn start hand: " + _fmt_hand(p, self.card_db, self.card_label))

    def stage_after_main(self, p: PlayerState):
        self.lines.append("-- Main phase end: Stage --")
        self.lines.extend(_fmt_stage(p, self.card_label))

    def set_phase(self, set_detail_lines: List[str]):
        self.lines.append("-- Set phase --")
        self.lines.extend(set_detail_lines)

    def hand_after_set_draw(self, p: PlayerState):
        self.lines.append("Hand after set-draw: " + _fmt_hand(p, self.card_db, self.card_label))

    def performance_detail(self, perf_lines: List[str]):
        self.lines.append("-- Performance / success check --")
        self.lines.extend(perf_lines)

    def blank(self):
        self.lines.append("")
