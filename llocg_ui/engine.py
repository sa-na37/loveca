# -*- coding: utf-8 -*-
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

from .db import (
    CardInfo,
    _safe_int, _read_json, _write_text,
    _hearts_from_counts_json, _parse_tags_json, _count_draw_icons,
    is_member_type, is_live_type,
    _canon_cardno, _cardno_variants, _get_card,
)

@dataclass
class StageSlot:
    cardnumber: str
    active: bool = True
    temp_blade: int = 0
    temp_until: str = ""  # e.g., end_of_live


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

    stage: Dict[str, Optional[StageSlot]] = field(default_factory=lambda: {"L": None, "C": None, "R": None})
    green_room: List[str] = field(default_factory=list)
    set_zone: List[str] = field(default_factory=list)
    resolve_zone: List[str] = field(default_factory=list)

    pending: List[Dict[str, Any]] = field(default_factory=list)
    live_start_prompted: bool = False

    # UI-only transient banner (e.g., LIVE success/fail)
    banner_text: str = ""
    banner_ts: float = 0.0
    banner_ttl: float = 0.0

    turn: int = 1
    log: List[str] = field(default_factory=list)
    undo_stack: List[Dict[str, Any]] = field(default_factory=list)


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
            stage_snap[k] = {"cardnumber": slot.cardnumber, "active": bool(slot.active), "temp_blade": int(getattr(slot, "temp_blade", 0) or 0), "temp_until": str(getattr(slot, "temp_until", "") or "")}

    return {
        "phase": gs.phase,
        "deck": list(gs.deck),
        "hand": list(gs.hand),
        "energy_active": int(gs.energy_active),
        "energy_wait": int(gs.energy_wait),
        "stage": stage_snap,
        "green_room": list(gs.green_room),
        "set_zone": list(gs.set_zone),
        "resolve_zone": list(gs.resolve_zone),
        "pending": json.loads(json.dumps(gs.pending)) if gs.pending else [],
        "live_start_prompted": bool(gs.live_start_prompted),
        "turn": int(gs.turn),
    }


def restore_state(gs: GameState, snap: Dict[str, Any]) -> None:
    """Restore from an undo snapshot (see snapshot_state)."""
    gs.phase = snap.get("phase", gs.phase)
    gs.deck = list(snap.get("deck", gs.deck))
    gs.hand = list(snap.get("hand", gs.hand))
    gs.energy_active = int(snap.get("energy_active", gs.energy_active))
    gs.energy_wait = int(snap.get("energy_wait", gs.energy_wait))

    stage_in = snap.get("stage", {}) or {}
    stage_new: Dict[str, Optional[StageSlot]] = {"L": None, "C": None, "R": None}
    for k in ("L", "C", "R"):
        v = stage_in.get(k)
        if v is None:
            stage_new[k] = None
        else:
            stage_new[k] = StageSlot(cardnumber=str(v.get("cardnumber", "")), active=bool(v.get("active", True)), temp_blade=_safe_int(v.get("temp_blade", 0), 0), temp_until=str(v.get("temp_until", "") or ""))
    gs.stage = stage_new

    gs.green_room = list(snap.get("green_room", gs.green_room))
    gs.set_zone = list(snap.get("set_zone", gs.set_zone))
    gs.resolve_zone = list(snap.get("resolve_zone", gs.resolve_zone))
    gs.pending = list(snap.get("pending", gs.pending) or [])
    gs.live_start_prompted = bool(snap.get("live_start_prompted", gs.live_start_prompted))
    gs.turn = int(snap.get("turn", gs.turn))



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


def begin_turn(gs: GameState) -> None:
    # Rules order (coarse): ACTIVE -> ENERGY -> DRAW -> MAIN
    gs.phase = "ACTIVE"
    refresh(gs)
    trace_write(gs, f"[PHASE] ACTIVE (refresh) E active={gs.energy_active} wait={gs.energy_wait}")
    gs.phase = "ENERGY"
    energy_phase(gs)
    trace_write(gs, f"[PHASE] ENERGY (+1) E active={gs.energy_active} wait={gs.energy_wait}")
    gs.phase = "DRAW"
    d = draw(gs, 1)
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
    begin_turn(gs)

    return gs, rng


def draw(gs: GameState, n: int) -> int:
    k = 0
    for _ in range(n):
        if not gs.deck:
            break
        gs.hand.append(gs.deck.pop(0))
        k += 1
    return k


def pay_energy(gs: GameState, cost: int) -> bool:
    if cost <= 0:
        return True
    if gs.energy_active < cost:
        return False
    gs.energy_active -= cost
    gs.energy_wait += cost
    return True


def refresh(gs: GameState) -> None:
    for k in ("L", "C", "R"):
        if gs.stage.get(k):
            gs.stage[k].active = True
    gs.energy_active += gs.energy_wait
    gs.energy_wait = 0


def energy_phase(gs: GameState) -> None:
    gs.energy_active += 1


def stage_blade(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    s = 0
    for slot in gs.stage.values():
        if not slot or not slot.active:
            continue
        c = _get_card(cards_db, slot.cardnumber)
        s += (int(c.blade) if c else 0) + int(getattr(slot, "temp_blade", 0) or 0)
    return s


def owned_base_hearts(gs: GameState, cards_db: Dict[str, CardInfo]) -> Dict[str, int]:
    pool: Dict[str, int] = {}
    for slot in gs.stage.values():
        if not slot:
            continue
        c = _get_card(cards_db, slot.cardnumber)
        if not c:
            continue
        for k, v in (c.base_hearts or {}).items():
            pool[k] = pool.get(k, 0) + int(v)
    return pool


def cheer_hearts_from_resolve(gs: GameState, cards_db: Dict[str, CardInfo]) -> Dict[str, int]:
    pool: Dict[str, int] = {}
    for cn in gs.resolve_zone:
        c = _get_card(cards_db, cn)
        if not c:
            continue
        for k, v in (c.blade_hearts or {}).items():
            pool[k] = pool.get(k, 0) + int(v)
    return pool


def can_satisfy_req(req: Dict[str, int], owned: Dict[str, int]) -> Tuple[bool, Dict[str, Any]]:
    pool = {k: int(v) for k, v in (owned or {}).items()}
    for k in ("red", "green", "blue", "all"):
        pool.setdefault(k, 0)

    alloc = {"use_red": 0, "use_green": 0, "use_blue": 0, "use_all": 0}

    for color, key in (("red", "use_red"), ("green", "use_green"), ("blue", "use_blue")):
        need = int(req.get(color, 0) or 0)
        take = min(pool[color], need)
        alloc[key] += take
        need -= take
        if need > 0:
            if pool["all"] < need:
                return (False, {"reason": f"lack {color} and ALL", "need": need, "pool_all": pool["all"]})
            alloc["use_all"] += need
            pool["all"] -= need

    need_all = int(req.get("all", 0) or 0)
    if need_all > 0:
        if pool["all"] < need_all:
            return (False, {"reason": "lack ALL", "need_all": need_all, "pool_all": pool["all"]})
        alloc["use_all"] += need_all
        pool["all"] -= need_all

    need_any = int(req.get("any", 0) or 0)
    if need_any > 0:
        total = pool["red"] + pool["green"] + pool["blue"] + pool["all"]
        if total < need_any:
            return (False, {"reason": "lack total hearts", "need_any": need_any, "pool_total": total})
        for k in sorted(("red", "green", "blue", "all"), key=lambda kk: pool[kk], reverse=True):
            if need_any <= 0:
                break
            take = min(pool[k], need_any)
            pool[k] -= take
            need_any -= take
            if k == "red":
                alloc["use_red"] += take
            elif k == "green":
                alloc["use_green"] += take
            elif k == "blue":
                alloc["use_blue"] += take
            else:
                alloc["use_all"] += take

    return (True, alloc)



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
    """Whether this card has a supported activated ability in the current engine."""
    return bool(_has_green_live_take_ability(ci) or _has_green_member_take_ability(ci) or _has_sacrifice_ability(ci))


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


def _enqueue_live_start_prompts(gs: GameState, cards_db: Dict[str, CardInfo]) -> int:
    """Queue live-start prompts once per live (until Attempt resolves)."""
    if gs.live_start_prompted:
        return 0
    prompts: List[Dict[str, Any]] = []
    for pos in ("L", "C", "R"):
        slot = gs.stage.get(pos)
        if not slot or not slot.active:
            continue
        ci = _get_card(cards_db, slot.cardnumber)
        if not ci or not ci.abilities:
            continue
        for ab in ci.abilities:
            if not isinstance(ab, dict):
                continue
            trig = str(ab.get("trigger", "") or "")
            if "ライブ開始時" not in trig:
                continue
            clauses = ab.get("clauses", [])
            if not isinstance(clauses, list):
                continue
            for cl in clauses:
                if not isinstance(cl, dict):
                    continue
                raw = str(cl.get("raw", "") or "")
                cost = str(cl.get("cost_template", "") or raw)
                eff = str(cl.get("effect_template", "") or raw)
                if "<(E)>" not in cost and "[E]" not in cost and "Ｅ" not in cost and "E" not in cost:
                    continue
                blades = _count_blade_icons(eff)
                if blades <= 0:
                    continue
                prompts.append({
                    "kind": "live_start_blade",
                    "pos": pos,
                    "cn": ci.cardnumber,
                    "need_e": 1,
                    "blades": int(blades),
                    "text": f"{pos}: {ci.cardnumber} ライブ開始時 [E]1 → ブレード+{blades} (ライブ終了時まで)",
                    # UI needs explicit choices here.
                    "options": ["pay", "skip"],
                })
    if prompts:
        gs.pending.extend(prompts)
        gs.live_start_prompted = True
        gs.log.append(f"[PROMPT] live-start abilities queued: {len(prompts)}")
    return len(prompts)


def _clear_end_of_live_buffs(gs: GameState) -> None:
    for pos in ("L", "C", "R"):
        slot = gs.stage.get(pos)
        if not slot:
            continue
        if getattr(slot, "temp_until", "") == "end_of_live":
            slot.temp_blade = 0
            slot.temp_until = ""

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

    # Auto abilities that trigger on enter ([登場])
    handle_enter_auto(gs, cards_db, pos, cn)



def handle_enter_auto(gs: GameState, cards_db: Dict[str, CardInfo], pos: str, cn: str) -> None:
    """Handle [登場] auto abilities for a member that just entered stage.

    Currently implemented:
    - PL!N-pb1-010 (三船栞子): choose one
      (A) エネルギーを1枚アクティブにする
      (B) 控え室の『虹ヶ咲』のライブカードを最大2枚、好きな順でデッキの上に置く
    """
    canon = _canon_cardno(cn)
    if canon != "PL!N-pb1-010":
        return

    # Push a choice prompt (mandatory)
    gs.pending.append({
        "kind": "choose_shioriko_enter",
        "cn": canon,
        "pos": pos.upper(),
        "text": "栞子[登場]: 効果を1つ選ぶ（エネルギー+1 / 控え室の虹ヶ咲LIVEを最大2枚デッキ上）",
        "options": ["energy", "topdeck"],
    })
    gs.log.append("[AUTO] 栞子[登場]: choose mode -> pending")



def cmd_set(gs: GameState, rng: random.Random, indices: List[int]) -> None:
    if len(indices) > 3:
        gs.log.append("[ERR] set: max 3 cards")
        return
    if any(i < 0 or i >= len(gs.hand) for i in indices):
        gs.log.append("[ERR] set: invalid indices")
        return
    idxs = sorted(set(indices), reverse=True)
    picked = []
    for i in idxs:
        picked.append(gs.hand.pop(i))
    picked.reverse()
    gs.set_zone = picked[:]
    drawn = draw(gs, len(picked))
    gs.log.append(f"[SET] set {len(picked)} cards, drew {drawn}")


def cmd_yell(gs: GameState, rng: random.Random, cards_db: Dict[str, CardInfo]) -> None:
    n = stage_blade(gs, cards_db)
    if n <= 0:
        gs.log.append("[YELL] 0 (no blade on active stage members)")
        return
    revealed = []
    for _ in range(n):
        if not gs.deck:
            break
        revealed.append(gs.deck.pop(0))
    gs.resolve_zone.extend(revealed)

    draw_n = 0
    for cn in revealed:
        c = _get_card(cards_db, cn)
        if c:
            draw_n += _count_draw_icons(c.blade_heart_tags_json)
    got = draw(gs, draw_n) if draw_n > 0 else 0
    gs.log.append(f"[YELL] revealed {len(revealed)} (blade={n}), draw+{draw_n} -> drew {got}")


def cmd_attempt(gs: GameState, cards_db: Dict[str, CardInfo]) -> None:
    if not gs.set_zone:
        gs.log.append("[ATTEMPT] no set cards")
        return

    if gs.pending:
        gs.log.append("[WARN] attempt: pending prompts exist; resolve them first.")
        return

    if _enqueue_live_start_prompts(gs, cards_db) > 0:
        gs.log.append("[INFO] attempt: resolve live-start prompts, then click Attempt again.")
        return

    lives = []
    nonlives = []
    for cn in gs.set_zone:
        c = _get_card(cards_db, cn)
        if c and is_live_type(c.type):
            lives.append(cn)
        else:
            nonlives.append(cn)

    if nonlives:
        gs.green_room.extend(nonlives)

    base = owned_base_hearts(gs, cards_db)
    cheer = cheer_hearts_from_resolve(gs, cards_db)
    owned = dict(base)
    for k, v in cheer.items():
        owned[k] = owned.get(k, 0) + int(v)

    ok_all = True
    gs.log.append(f"[ATTEMPT] LIVE={len(lives)} base={base} cheer={cheer} owned={owned}")
    for cn in lives:
        c = _get_card(cards_db, cn)
        req = (c.required_hearts if c else {}) or {}
        ok, alloc = can_satisfy_req(req, owned)
        ok_all = ok_all and ok
        gs.log.append(f"  live: {'OK' if ok else 'NG'} {cn} req={req} alloc={alloc}")

    if lives:
        gs.green_room.extend(lives)

    gs.set_zone = []
    result_txt = 'SUCCESS' if ok_all else 'FAIL'
    gs.log.append(f"[ATTEMPT] result={result_txt}")

    # UI banner (transient)
    gs.banner_text = result_txt
    gs.banner_ts = time.time()
    gs.banner_ttl = 2.5

    _clear_end_of_live_buffs(gs)
    gs.live_start_prompted = False


def cmd_ack(gs: GameState) -> None:
    if not gs.resolve_zone:
        gs.log.append("[ACK] resolve zone empty")
        return
    n = len(gs.resolve_zone)
    gs.green_room.extend(gs.resolve_zone)
    gs.resolve_zone = []
    gs.log.append(f"[ACK] moved {n} revealed cards -> green room")



def cmd_activate_to_green(gs: GameState, cards_db: Dict[str, CardInfo], pos: str) -> None:
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
    # Support only a small hard-coded subset of activated abilities.
    if not (_has_green_live_take_ability(ci) or _has_green_member_take_ability(ci) or _has_sacrifice_ability(ci)):
        gs.log.append(f"[ERR] activate: no supported 'to green room' ability on {ci.cardnumber}")
        return
    # Cost handling:
    # - Some cards require putting this member into the green room as part of the activated ability cost.
    # - Other cards can recover a card from green room without moving themselves.
    moved_self = False
    if _has_sacrifice_ability(ci):
        gs.green_room.append(slot.cardnumber)
        gs.stage[pos] = None
        gs.log.append(f"[ACT] {pos}: {ci.cardnumber} -> green room (cost)")
        moved_self = True
    else:
        gs.log.append(f"[ACT] {pos}: {ci.cardnumber} activated")

    # follow-up: take 1 LIVE from green room to hand (supported subset)
    if _has_green_live_take_ability(ci):
        cands = _green_live_candidates(gs, cards_db)
        if not cands:
            gs.log.append("[ACT] no LIVE in green room to take")
        elif len(cands) == 1:
            take_cn = cands[0]
            gs.green_room.remove(take_cn)
            gs.hand.append(take_cn)
            gs.log.append(f"[ACT] took LIVE {take_cn} from green room -> hand")
        else:
            gs.pending.append({
                "kind": "pick_live_from_green",
                "text": "控え室のライブカードを1枚手札に加える",
                "options": cands,
            })
            gs.log.append(f"[PENDING] pick 1 LIVE from green room ({len(cands)} candidates)")

    # follow-up: take 1 MEMBER from green room to hand (PL!N-sd1-006)
    if _has_green_member_take_ability(ci):
        # CardInfo schema uses field name "type" (db.py). Earlier versions used "cardtype".
        # Keep this tolerant so compiled DB variants don't crash the UI.
        def _card_type_upper(x: Any) -> str:
            if x is None:
                return ""
            t = getattr(x, "type", None)
            if t is None:
                t = getattr(x, "cardtype", None)
            return str(t or "").upper()

        cands = [
            cn
            for cn in gs.green_room
            if (_get_card(cards_db, cn) and _card_type_upper(_get_card(cards_db, cn)) == "MEMBER")
        ]
        if not cands:
            gs.log.append("[ACT] no MEMBER in green room to take")
        elif len(cands) == 1:
            take_cn = cands[0]
            gs.green_room.remove(take_cn)
            gs.hand.append(take_cn)
            gs.log.append(f"[ACT] took MEMBER {take_cn} from green room -> hand")
        else:
            gs.pending.append({
                "kind": "pick_member_from_green",
                "text": "控え室のメンバーカードを1枚手札に加える",
                "options": cands,
            })
            gs.log.append(f"[PENDING] pick 1 MEMBER from green room ({len(cands)} candidates)")


def cmd_resolve_pending(gs: GameState, cards_db: Dict[str, CardInfo], idx: int, choice: str) -> None:
    if idx < 0 or idx >= len(gs.pending):
        gs.log.append("[ERR] resolve_pending: invalid idx")
        return
    p = gs.pending.pop(idx)
    kind = str(p.get("kind", "") or "")
    choice_str = str(choice or "").strip()

    # Generic "skip / finish early" for prompts that allow fewer picks than the max.
    # The UI can send __SKIP__ to stop selecting additional cards.
    if choice_str == "__SKIP__" and p.get("allow_less"):
        gs.log.append(f"[SKIP] prompt {kind}: user skipped remaining selections")
        return

    # 1) Live-start optional payment -> temp blade
    if kind == "live_start_blade":
        pos = str(p.get("pos", "") or "").upper()
        need_e = _safe_int(p.get("need_e", 1), 1)
        blades = _safe_int(p.get("blades", 0), 0)
        slot = gs.stage.get(pos)
        if not slot:
            gs.log.append(f"[SKIP] prompt: stage {pos} empty (ignored)")
            return
        if choice_str.lower() in ("pay", "yes", "y", "1", "true"):
            if not pay_energy(gs, need_e):
                gs.log.append(f"[ERR] ability: insufficient energy for [E]{need_e} (have {gs.energy_active})")
                return
            slot.temp_blade += blades
            slot.temp_until = "end_of_live"
            gs.log.append(f"[AUTO] {pos}: paid [E]{need_e} -> temp blade +{blades} (until end of live)")
        else:
            gs.log.append(f"[SKIP] {pos}: live-start blade ability skipped")
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

    gs.log.append(f"[WARN] resolve_pending: unknown kind='{kind}' (ignored)")

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
    gs.set_zone = []
    gs.live_start_prompted = False
    gs.turn_blade_bonus = 0
    gs.log.append(f"[PHASE] LIVE_SET (choose up to 3 from hand) turn={gs.turn}")


def _advance_to_next_turn(gs: GameState, rng: random.Random) -> None:
    gs.turn += 1
    begin_turn(gs)


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
        # FIX_V2_16_NO_LIVE_AFTER_FILTER
        # If no LIVE cards were set (e.g., only MEMBER was set), skip the live entirely.
        if not lives:
            gs.log.append("[INFO] confirm: no LIVE in set_zone after filtering; skipping live.")
            gs.phase = "LIVE_RESOLVE"
            gs.log.append(f"[PHASE] LIVE_RESOLVE (no live) turn={gs.turn}")
            return


        n = _enqueue_live_start_prompts(gs, cards_db)
        if n > 0:
            gs.log.append(f"[AUTO] live-start triggers queued={n}")
            return

        gs.phase = "LIVE_PERF"
        gs.log.append(f"[PHASE] LIVE_PERF (YELL) turn={gs.turn}")
        return

    if gs.phase == "LIVE_PERF":
        # FIX_V2_16_SKIP_PERF_WHEN_NO_LIVE
        # If there is no LIVE card in set_zone, do not perform YELL/ATTEMPT.
        if not gs.set_zone:
            gs.log.append("[INFO] perf: no LIVE in set_zone; skipping cheer/attempt.")
            gs.phase = "LIVE_RESOLVE"
            gs.log.append(f"[PHASE] LIVE_RESOLVE (no live) turn={gs.turn}")
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
        # Treat Next as the confirm/cleanup step.
        if gs.resolve_zone:
            cmd_ack(gs)
        if gs.resolve_zone:
            gs.log.append("[WARN] next: resolve_zone still not empty after ACK; abort.")
            return
        _advance_to_next_turn(gs, rng)
        return

    gs.log.append(f"[WARN] next: unknown phase={gs.phase}")

