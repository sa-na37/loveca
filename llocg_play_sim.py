#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLCG play/sim (patched)

Patch focus (this update):
- Accept simulator deck JSON produced by decklist_to_simdeck (preferred) in addition to TSV decklists.
  * New CLI: --code <DECKCODE> (loads <root>/sim_decks/deck_<code>.json)
            --simdeck <path/to/deck_XXXX.json>
            --decklist <legacy TSV/CSV with cardnumber, quantity> (still supported)
- Keep folder structure stable: outputs remain under <root>/sim_out (no versioned folders).

This simulator is intentionally "minimal but rule-anchored": it focuses on producing per-turn live success
and score totals under a configurable heuristic policy, not on full opponent interaction.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import itertools
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


# ----------------------------
# Local modules (policy / trace)
# ----------------------------
try:
    import llocg_policy as _policy
except Exception:
    _policy = None  # type: ignore
try:
    from llocg_trace import TraceWriter as _TraceWriter
except Exception:
    _TraceWriter = None  # type: ignore


# ----------------------------
# Utilities
# ----------------------------

def _read_tsv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        sniff = f.read(4096)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sniff, delimiters="\t, ")
        reader = csv.DictReader(f, dialect=dialect)
        rows = [dict(r) for r in reader]
    return rows


def _safe_int(x, default=0) -> int:
    try:
        if x is None:
            return default
        if isinstance(x, (int,)):
            return int(x)
        s = str(x).strip()
        if s == "" or s.lower() == "nan":
            return default
        return int(float(s))
    except Exception:
        return default


def _json_load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _parse_version(p: Path) -> Tuple[int, str]:
    m = re.search(r"_v(\d+)([a-zA-Z]*)\.json$", p.name)
    if not m:
        return (-1, "")
    return (int(m.group(1)), m.group(2) or "")


def _auto_pick_latest_compiled(root: Path) -> Path:
    cands = sorted(root.glob("cards_compiled_v*.json"), key=lambda p: _parse_version(p))
    if not cands:
        raise FileNotFoundError(f"No cards_compiled_v*.json under: {root}")
    cands.sort(key=lambda p: (_parse_version(p)[0], _parse_version(p)[1]))
    return cands[-1]


def _auto_pick_cards_min(root: Path) -> Optional[Path]:
    p = root / "cards_min_tokv1.csv"
    return p if p.exists() else None


def _auto_update_manifest(root: Path) -> None:
    here = Path(__file__).resolve().parent
    tool = here / "llocg_update_manifest.py"
    if not tool.exists():
        return
    try:
        subprocess.run([sys.executable, str(tool), "--root", str(root)], check=False)
    except Exception:
        pass


def _count_draw_icons(tags_json: str) -> int:
    n = 0
    try:
        tags = json.loads(tags_json) if tags_json else []
    except Exception:
        tags = []
    for t in tags:
        m = re.search(r"ドロー\+(\d+)", str(t))
        if m:
            n += int(m.group(1))
    return n


def _count_score_icons(tags_json: str) -> int:
    n = 0
    try:
        tags = json.loads(tags_json) if tags_json else []
    except Exception:
        tags = []
    for t in tags:
        m = re.search(r"スコア\+(\d+)", str(t))
        if m:
            n += int(m.group(1))
    return n


def _hearts_from_counts_json(counts_json: str) -> Dict[str, int]:
    if not counts_json:
        return {}
    try:
        d = json.loads(counts_json)
        if isinstance(d, dict):
            return {str(k): int(v) for k, v in d.items() if int(v) != 0}
    except Exception:
        pass
    return {}


# ----------------------------
# Data models
# ----------------------------

@dataclass
class Card:
    cardnumber: str
    name: str
    type: str  # "MEMBER" or "LIVE" or others
    cost: int = 0
    blade: int = 0
    score: int = 0
    base_hearts: Dict[str, int] = None
    required_hearts: Dict[str, int] = None
    blade_hearts: Dict[str, int] = None
    blade_heart_tags_json: str = "[]"
    effect_text_raw: str = ""
    effect_text_norm: str = ""
    compiled: Dict[str, Any] = None

    def __post_init__(self):
        if self.base_hearts is None:
            self.base_hearts = {}
        if self.required_hearts is None:
            self.required_hearts = {}
        if self.blade_hearts is None:
            self.blade_hearts = {}
        if self.compiled is None:
            self.compiled = {}


@dataclass
class StageMember:
    card: Card
    entered_turn: int
    state: str = "ACTIVE"  # ACTIVE or WAIT


@dataclass
class SimTurnSnapshot:
    run: int
    turn: int
    hand_size_turn_start: int
    hand_size_after_energy: int
    hand_size_after_member: int
    hand_size_start: int
    hand_size_end: int
    stage_L: str
    stage_C: str
    stage_R: str
    cheer_n: int
    cheer_revealed: int
    cheer_draw: int
    lives_set: int
    lives_attempted: int
    lives_success: int
    turn_score: int
    note: str = ""


# ----------------------------
# DB loading
# ----------------------------

def load_compiled_cards(compiled_path: Path) -> List[Dict[str, Any]]:
    obj = _json_load(compiled_path)
    if isinstance(obj, dict) and "cards" in obj and isinstance(obj["cards"], list):
        return obj["cards"]
    if isinstance(obj, list):
        return obj
    raise ValueError(f"Unsupported compiled DB shape: {compiled_path}")


def load_stats(cards_min_path: Path) -> Dict[str, Dict[str, Any]]:
    import pandas as pd  # local import
    df = pd.read_csv(cards_min_path)
    out: Dict[str, Dict[str, Any]] = {}
    for _, r in df.iterrows():
        cn = str(r.get("cardnumber", "")).strip()
        if not cn:
            continue
        out[cn] = {
            "type": str(r.get("card_type_norm", "")).strip(),
            "name": str(r.get("cardname", "")).strip(),
            "cost": _safe_int(r.get("cost", 0), 0),
            "blade": _safe_int(r.get("blade", 0), 0),
            "score": _safe_int(r.get("score", 0), 0),
            "base_hearts": _hearts_from_counts_json(str(r.get("base_hearts_counts_json", ""))),
            "required_hearts": _hearts_from_counts_json(str(r.get("required_hearts_counts_json", ""))),
            "blade_hearts": _hearts_from_counts_json(str(r.get("blade_heart_counts_json", ""))),
            "blade_heart_tags_json": str(r.get("blade_heart_tags_json", "[]")),
            "effect_text_raw": str(r.get("effect_text_raw", "")).strip(),
            "effect_text_norm": str(r.get("effect_text_norm", "")).strip(),
        }
    return out


def merge_cards(compiled_cards: List[Dict[str, Any]], stats: Dict[str, Dict[str, Any]]) -> Dict[str, Card]:
    out: Dict[str, Card] = {}
    for c in compiled_cards:
        cn = str(c.get("cardnumber") or c.get("id") or "").strip()
        if not cn:
            continue
        st = stats.get(cn, {})
        name = str(c.get("name") or st.get("name") or "").strip()
        ctype = str(c.get("type") or st.get("type") or "").strip()
        if ctype.startswith("MEMBER"):
            ctype_norm = "MEMBER"
        elif ctype.startswith("LIVE"):
            ctype_norm = "LIVE"
        else:
            ctype_norm = ctype or "OTHER"
        out[cn] = Card(
            cardnumber=cn,
            name=name,
            type=ctype_norm,
            cost=_safe_int(st.get("cost", 0), 0),
            blade=_safe_int(st.get("blade", 0), 0),
            score=_safe_int(st.get("score", 0), 0),
            base_hearts=st.get("base_hearts", {}) or {},
            required_hearts=st.get("required_hearts", {}) or {},
            blade_hearts=st.get("blade_hearts", {}) or {},
            blade_heart_tags_json=st.get("blade_heart_tags_json", "[]") or "[]",
            effect_text_raw=st.get("effect_text_raw", "") or "",
            effect_text_norm=st.get("effect_text_norm", "") or "",
            compiled=c,
        )
    return out


# ----------------------------
# Deck loading
# ----------------------------

def load_deck_from_decklist_tsv(decklist_path: Path) -> List[str]:
    rows = _read_tsv(decklist_path)
    deck: List[str] = []
    for r in rows:
        cn = str(r.get("cardnumber", "")).strip()
        qty = _safe_int(r.get("quantity", 0), 0)
        if cn and qty > 0:
            deck.extend([cn] * qty)
    return deck


def load_deck_from_simdeck_json(simdeck_path: Path) -> List[str]:
    obj = _json_load(simdeck_path)
    if not isinstance(obj, dict) or "cards" not in obj:
        raise ValueError(f"Not a simdeck json: {simdeck_path}")

    deck: List[str] = []
    for ent in obj.get("cards", []) or []:
        if not isinstance(ent, dict):
            continue
        cnt = _safe_int(ent.get("count", 0), 0)
        cn = str(
            ent.get("db_id")
            or ent.get("cardnumber")
            or ent.get("card_no")
            or ent.get("tsv_card_no")
            or ""
        ).strip()
        if not cn or cnt <= 0:
            continue
        deck.extend([cn] * cnt)

    if deck and len(deck) != 60:
        print(f"[WARN] simdeck total={len(deck)} (expected 60): {simdeck_path}", file=sys.stderr)

    return deck


def resolve_deck_source(root: Path, decklist: Optional[str], simdeck: Optional[str], code: Optional[str]) -> Tuple[List[str], str]:
    if simdeck:
        p = Path(simdeck).expanduser().resolve()
        return load_deck_from_simdeck_json(p), str(p)
    if code:
        p = (root / "sim_decks" / f"deck_{code}.json").resolve()
        return load_deck_from_simdeck_json(p), str(p)
    if decklist:
        p = Path(decklist).expanduser().resolve()
        return load_deck_from_decklist_tsv(p), str(p)
    raise ValueError("Provide one of --simdeck, --code, or --decklist.")


# ----------------------------
# Zones / player
# ----------------------------

@dataclass
class PlayerState:
    deck: List[str]
    hand: List[str]
    energy_deck: List[str]
    energy_active: int
    energy_wait: int
    stage: Dict[str, Optional[StageMember]]  # L/C/R
    green_room: List[str]
    pending_set: List[str] = field(default_factory=list)

    def stage_members(self) -> List[StageMember]:
        return [m for m in self.stage.values() if m is not None]

    def stage_active_members(self) -> List[StageMember]:
        return [m for m in self.stage.values() if (m is not None and m.state == "ACTIVE")]

    def draw(self, n: int) -> int:
        k = 0
        for _ in range(n):
            if not self.deck:
                break
            self.hand.append(self.deck.pop(0))
            k += 1
        return k


def mulligan_once(p: PlayerState, card_db: Dict[str, Card], seed: int, log: Optional[List[str]] = None):
    rng = random.Random(seed)
    if not p.hand:
        return

    def is_member(cn: str) -> bool:
        c = card_db.get(cn)
        return bool(c and c.type == "MEMBER")

    def pick_one(pred):
        for cn in p.hand:
            if pred(cn):
                return cn
        return None

    keep = set()

    def cn_name(cn: str) -> str:
        c = card_db.get(cn)
        return c.name if c else ""

    def cn_cost(cn: str) -> int:
        c = card_db.get(cn)
        return int(c.cost) if c else 0

    shioriko = pick_one(lambda cn: is_member(cn) and cn_cost(cn) == 4 and ("栞子" in cn_name(cn)))
    if shioriko:
        keep.add(shioriko)
    else:
        any4 = pick_one(lambda cn: is_member(cn) and cn_cost(cn) == 4)
        if any4:
            keep.add(any4)

    any9 = pick_one(lambda cn: is_member(cn) and cn_cost(cn) == 9)
    if any9:
        keep.add(any9)

    kimi = pick_one(lambda cn: (card_db.get(cn) and card_db.get(cn).type == "LIVE" and ("君のこころは輝いてるかい" in cn_name(cn))))
    if kimi:
        keep.add(kimi)

    yoshiko11 = pick_one(lambda cn: is_member(cn) and cn_cost(cn) == 11 and ("善子" in cn_name(cn)))
    if yoshiko11:
        keep.add(yoshiko11)

    set_aside = [cn for cn in p.hand if cn not in keep]
    if not set_aside:
        if log is not None:
            log.append("  mulligan: keep all (0 returned)")
        return

    p.hand = [cn for cn in p.hand if cn in keep]
    drawn = p.draw(len(set_aside))
    p.deck.extend(set_aside)
    rng.shuffle(p.deck)

    if log is not None:
        log.append(f"  mulligan: returned={len(set_aside)} drawn={drawn} keep={len(keep)}")


def setup_player(deck_cards: List[str], seed: int) -> PlayerState:
    rng = random.Random(seed)
    deck = deck_cards[:]
    rng.shuffle(deck)

    energy_deck = ["ENERGY"] * 12
    rng.shuffle(energy_deck)

    hand: List[str] = []
    for _ in range(6):
        if deck:
            hand.append(deck.pop(0))

    energy_active = 3
    energy_wait = 0
    energy_deck = energy_deck[3:]

    stage = {"L": None, "C": None, "R": None}
    return PlayerState(deck=deck, hand=hand, energy_deck=energy_deck, energy_active=energy_active, energy_wait=energy_wait,
                       stage=stage, green_room=[])


def energy_phase(p: PlayerState):
    if p.energy_deck:
        p.energy_deck.pop(0)
        p.energy_active += 1


def refresh_phase(p: PlayerState):
    for m in p.stage_members():
        m.state = "ACTIVE"
    p.energy_active += p.energy_wait
    p.energy_wait = 0


def pay_energy(p: PlayerState, cost: int) -> bool:
    if cost <= 0:
        return True
    if p.energy_active < cost:
        return False
    p.energy_active -= cost
    p.energy_wait += cost
    return True


def card_label(card: Optional[Card], fallback_cn: str = "") -> str:
    if card is None:
        return fallback_cn or "UNKNOWN"
    try:
        return f"{int(card.cost)}:{card.name}({card.cardnumber})"
    except Exception:
        return f"{card.name}({card.cardnumber})"


def apply_enter_effects(p: PlayerState, card_db: Dict[str, Card], entered: Card, turn: int, log: List[str]):
    # kept minimal (same as current v2)
    cn = entered.cardnumber
    name = entered.name

    if cn == "PL!N-bp3-022" or ("三船" in name and "栞子" in name and int(entered.cost) == 4):
        peek_n = min(2, len(p.deck))
        peek = [p.deck.pop(0) for _ in range(peek_n)]
        log.append(f"  [EFFECT] Shioriko(4): revealed top{peek_n} -> " + ", ".join(card_label(card_db.get(x), x) for x in peek))
        kept: List[str] = []
        sent: List[str] = []
        for x in peek:
            c = card_db.get(x)
            if c and c.type == "MEMBER" and int(c.cost or 0) in (2, 4):
                p.green_room.append(x)
                sent.append(x)
            else:
                kept.append(x)
        p.deck = kept + p.deck
        if sent:
            log.append("    sent to green_room: " + ", ".join(card_label(card_db.get(x), x) for x in sent))
        if kept:
            log.append("    returned to deck: " + ", ".join(card_label(card_db.get(x), x) for x in kept))

    if ("村野" in name and "さやか" in name and int(entered.cost) == 13) or cn == "PL!HS-bp2-002":
        if p.deck:
            x = p.deck.pop(0)
            p.hand.append(x)
            log.append("  [EFFECT] Sayaka(13): drew -> " + card_label(card_db.get(x), x))

    if ("津島" in name and "善子" in name and int(entered.cost) == 11) or cn == "PL!S-bp2-006":
        need_e = 4
        empty = [pos for pos in ("L", "C", "R") if p.stage.get(pos) is None]
        if p.energy_active < need_e:
            log.append(f"    [EFFECT] Yoshiko(11): skip (need {need_e} energy, have {p.energy_active})")
        elif not empty:
            log.append("    [EFFECT] Yoshiko(11): skip (no empty stage slot)")
        else:
            cand = []
            for x in list(p.green_room):
                c = card_db.get(x)
                if not c or c.type != "MEMBER":
                    continue
                cc = int(c.cost or 0)
                if 0 < cc <= 4:
                    cand.append((x, cc))

            best = None
            best_key = None
            max_k = min(len(empty), 3)
            for k in range(1, max_k + 1):
                for idxs in itertools.combinations(range(len(cand)), k):
                    sel = [cand[i] for i in idxs]
                    tot = sum(co for _, co in sel)
                    if tot != 4:
                        continue
                    n2 = sum(1 for _, co in sel if co == 2)
                    mx = max(co for _, co in sel)
                    key = (1, tot, n2, k, -mx)
                    if best_key is None or key > best_key:
                        best_key = key
                        best = sel

            if not best:
                log.append("    [EFFECT] Yoshiko(11): skip (no green_room combo with total cost=4)")
            else:
                ok = pay_energy(p, need_e)
                if not ok:
                    log.append(f"    [EFFECT] Yoshiko(11): skip (failed to pay energy; active={p.energy_active})")
                else:
                    moved = []
                    for (x, cc), pos in zip(sorted(best, key=lambda t: (-t[1], t[0])), empty):
                        try:
                            p.green_room.remove(x)
                        except ValueError:
                            continue
                        p.stage[pos] = StageMember(card=card_db.get(x), entered_turn=turn, state="ACTIVE")
                        moved.append((pos, x))
                    if moved:
                        log.append(
                            "    [EFFECT] Yoshiko(11): paid 4 energy; green_room -> stage: "
                            + ", ".join(f"{pos} {card_label(card_db.get(x), x)}" for pos, x in moved)
                            + f" (E active={p.energy_active}, wait={p.energy_wait})"
                        )


def play_member_best_effort(p: PlayerState, card_db: Dict[str, Card], turn: int, log: List[str]) -> int:
    if _policy is None:
        raise RuntimeError("llocg_policy.py not found or failed to import")
    return _policy.play_member_best_effort(
        p, card_db, turn, log,
        pay_energy=lambda pp, c: pay_energy(pp, c),
        apply_enter_effects=lambda pp, db, card, t, lg: apply_enter_effects(pp, db, card, t, lg),
        card_label=lambda card, cn=None: card_label(card, cn),
    )


def choose_live_set_cards(p: PlayerState, card_db: Dict[str, Card], turn: int, log: List[str]) -> List[str]:
    chosen: List[str] = _policy.choose_live_set_cards(
        p,
        card_db,
        turn,
        log,
        card_label=card_label,
    ) or []

    flat: List[str] = []
    for x in chosen:
        if isinstance(x, list):
            flat.extend([y for y in x if isinstance(y, str)])
        elif isinstance(x, str):
            flat.append(x)
    chosen = flat

    set_list: List[str] = []
    seen = set()
    for cn in chosen:
        if not isinstance(cn, str):
            continue
        if cn in seen:
            continue
        if cn not in p.hand:
            continue
        seen.add(cn)
        set_list.append(cn)
        if len(set_list) >= 3:
            break

    lives_n = sum(1 for cn in set_list if (card_db.get(cn) and card_db.get(cn).type == "LIVE"))

    if set_list:
        for cn in set_list:
            try:
                p.hand.remove(cn)
            except ValueError:
                pass
        drawn = p.draw(len(set_list))
        log.append(f"set: set {len(set_list)} cards (LIVE={lives_n}) and drew {drawn}")
        log.append("  set: " + ", ".join(card_label(card_db.get(cn), cn) for cn in set_list))
    else:
        log.append("set: set 0 cards (LIVE=0) and drew 0")

    return set_list


def perform_lives(p: PlayerState, card_db: Dict[str, Card], live_set: List[str], log: List[str]) -> Tuple[int, int, int, int]:
    set_nonlive: List[str] = []
    lives: List[Card] = []
    for cn in live_set:
        c = card_db.get(cn)
        if c and c.type == "LIVE":
            lives.append(c)
        else:
            set_nonlive.append(cn)
            p.green_room.append(cn)

    if not lives:
        log.append("  performance: (skip) no LIVE in set")
        return (0, 0, 0, 0)

    cheer_n = sum(int(m.card.blade or 0) for m in p.stage_active_members())

    revealed: List[str] = []
    for _ in range(cheer_n):
        if not p.deck:
            break
        revealed.append(p.deck.pop(0))

    cheer_draw = 0
    cheer_blade_hearts: Dict[str, int] = {}
    cheer_score_icons = 0
    for cn in revealed:
        c = card_db.get(cn)
        if c:
            for k, v in (c.blade_hearts or {}).items():
                cheer_blade_hearts[k] = cheer_blade_hearts.get(k, 0) + int(v)
            cheer_draw += _count_draw_icons(getattr(c, "blade_heart_tags_json", "") or "")
            cheer_score_icons += _count_score_icons(getattr(c, "blade_heart_tags_json", "") or "")

    p.draw(cheer_draw)

    owned: Dict[str, int] = {}
    for m in p.stage_members():
        for k, v in (m.card.base_hearts or {}).items():
            owned[k] = owned.get(k, 0) + int(v)
    for k, v in cheer_blade_hearts.items():
        owned[k] = owned.get(k, 0) + int(v)

    def can_pay(req: Dict[str, int], pool: Dict[str, int]) -> Optional[Dict[str, int]]:
        pool2 = {k: int(v or 0) for k, v in (pool or {}).items()}
        for k in ("red", "green", "blue", "all"):
            pool2.setdefault(k, 0)

        req2 = {k: int(v or 0) for k, v in (req or {}).items()}

        all_req = int(req2.get("all", 0) or 0)
        if all_req > 0:
            if pool2["all"] < all_req:
                return None
            pool2["all"] -= all_req

        for color in ("red", "green", "blue"):
            need = int(req2.get(color, 0) or 0)
            if need <= 0:
                continue
            use = min(pool2[color], need)
            pool2[color] -= use
            need -= use
            if need > 0:
                if pool2["all"] < need:
                    return None
                pool2["all"] -= need

        any_req = int(req2.get("any", 0) or 0)
        if any_req > 0:
            remaining_total = pool2["red"] + pool2["green"] + pool2["blue"] + pool2["all"]
            if remaining_total < any_req:
                return None
            for k in sorted(("red", "green", "blue", "all"), key=lambda kk: pool2[kk], reverse=True):
                if any_req <= 0:
                    break
                take = min(pool2[k], any_req)
                pool2[k] -= take
                any_req -= take
        return pool2

    pool = dict(owned)
    for lv in lives:
        req = lv.required_hearts or {}
        if not req:
            return (len(lives), 0, 0, cheer_draw)
        new_pool = can_pay(req, pool)
        if new_pool is None:
            return (len(lives), 0, 0, cheer_draw)
        pool = new_pool

    turn_score = sum(int(lv.score or 0) for lv in lives) + int(cheer_score_icons or 0)
    for lv in lives:
        p.green_room.append(lv.cardnumber)
    return (len(lives), len(lives), turn_score, cheer_draw)


def simulate_once(run_idx: int, deck: List[str], card_db: Dict[str, Card], turns: int, seed: int) -> Tuple[List[SimTurnSnapshot], Dict[str, Any]]:
    p = setup_player(deck, seed=seed + run_idx * 10007)

    snapshots: List[SimTurnSnapshot] = []
    total_score = 0
    total_lives_attempted = 0
    total_lives_success = 0

    for turn in range(1, turns + 1):
        energy_phase(p)
        p.draw(1)

        for _ in range(20):
            played = play_member_best_effort(p, card_db, turn, [])
            if played <= 0:
                break

        live_set = choose_live_set_cards(p, card_db, turn, [])
        lives_set = sum(1 for cn in live_set if (card_db.get(cn) and card_db.get(cn).type == "LIVE"))

        lives_attempted, lives_success, turn_score, cheer_draw = perform_lives(p, card_db, live_set, [])

        total_score += turn_score
        total_lives_attempted += lives_attempted
        total_lives_success += lives_success

        refresh_phase(p)

        snapshots.append(SimTurnSnapshot(
            run=run_idx,
            turn=turn,
            hand_size_turn_start=0,
            hand_size_after_energy=0,
            hand_size_after_member=0,
            hand_size_start=0,
            hand_size_end=len(p.hand),
            stage_L=(p.stage["L"].card.cardnumber if p.stage["L"] else ""),
            stage_C=(p.stage["C"].card.cardnumber if p.stage["C"] else ""),
            stage_R=(p.stage["R"].card.cardnumber if p.stage["R"] else ""),
            cheer_n=sum(m.card.blade for m in p.stage_active_members()),
            cheer_revealed=0,
            cheer_draw=cheer_draw,
            lives_set=lives_set,
            lives_attempted=lives_attempted,
            lives_success=lives_success,
            turn_score=turn_score,
            note="",
        ))

    summary = {
        "run": run_idx,
        "turns": turns,
        "total_score": total_score,
        "lives_attempted": total_lives_attempted,
        "lives_success": total_lives_success,
        "live_success_rate": (total_lives_success / total_lives_attempted) if total_lives_attempted else None,
    }
    return snapshots, summary


def write_outputs(outdir: Path, snapshots_all: List[SimTurnSnapshot]):
    outdir.mkdir(parents=True, exist_ok=True)
    snap_path = outdir / "sim_raw_turn_snapshots.csv"
    with snap_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(snapshots_all[0]).keys()) if snapshots_all else [
            "run","turn","hand_size_turn_start","hand_size_after_energy","hand_size_after_member","hand_size_start","hand_size_end","stage_L","stage_C","stage_R","cheer_n","cheer_revealed",
            "cheer_draw","lives_set","lives_attempted","lives_success","turn_score","note"
        ])
        w.writeheader()
        for s in snapshots_all:
            w.writerow(asdict(s))


def cmd_simulate(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    outdir = root / "sim_out"
    compiled_path = Path(args.compiled).resolve() if args.compiled else _auto_pick_latest_compiled(root)

    stats_path = _auto_pick_cards_min(root)
    stats = load_stats(stats_path) if stats_path else {}
    compiled_cards = load_compiled_cards(compiled_path)
    card_db = merge_cards(compiled_cards, stats)

    deck, deck_src = resolve_deck_source(
        root,
        decklist=getattr(args, "decklist", None),
        simdeck=getattr(args, "simdeck", None),
        code=getattr(args, "code", None),
    )

    snapshots_all: List[SimTurnSnapshot] = []
    for r in range(args.runs):
        snaps, summ = simulate_once(r, deck, card_db, turns=args.turns, seed=args.seed)
        snapshots_all.extend(snaps)

    write_outputs(outdir, snapshots_all)

    print("[DONE]")
    print(f"deck    : {deck_src}")
    print(f"compiled: {compiled_path}")
    print(f"outdir  : {outdir}")
    print(f"  {outdir / 'sim_raw_turn_snapshots.csv'}")
    _auto_update_manifest(root)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=Path(__file__).name, add_help=True)
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("simulate", help="Run minimal rule-anchored simulation.")
    g = ps.add_mutually_exclusive_group(required=True)
    g.add_argument("--code", default=None, help="Deck code. Loads <root>/sim_decks/deck_<code>.json (preferred).")
    g.add_argument("--simdeck", default=None, help="Path to simdeck json (preferred).")
    g.add_argument("--decklist", default=None, help="Legacy TSV/CSV with columns cardnumber, quantity.")

    ps.add_argument("--root", required=True, help="Project output root (llocg_db_out_full)")
    ps.add_argument("--compiled", default=None, help="Optional compiled DB json path; default auto-pick latest under root")
    ps.add_argument("--runs", type=int, default=2000)
    ps.add_argument("--turns", type=int, default=6, help="Number of turns per run (default 6)")
    ps.add_argument("--seed", type=int, default=1)
    ps.set_defaults(func=cmd_simulate)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
