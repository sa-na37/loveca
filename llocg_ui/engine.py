from __future__ import annotations
import copy
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

PHASES = ["MAIN", "LIVESET"]

@dataclass
class Card:
    cid: str
    card_no: str
    rarity: str = ""
    name: str = ""
    card_type: str = ""
    img_orient: str = ""
    text: str = ""

@dataclass
class GameState:
    turn: int = 1
    phase: str = "MAIN"
    deck: List[str] = field(default_factory=list)
    hand: List[str] = field(default_factory=list)
    liveset: List[str] = field(default_factory=list)
    stage: Dict[str, Optional[str]] = field(default_factory=lambda: {"L": None, "C": None, "R": None})
    energies_under: Dict[str, int] = field(default_factory=lambda: {"L": 0, "C": 0, "R": 0})
    waiting: List[str] = field(default_factory=list)
    resolve: List[str] = field(default_factory=list)
    energy_cur: int = 4
    energy_max: int = 4
    log: List[str] = field(default_factory=list)
    popup: Optional[Dict[str, Any]] = None

class Engine:
    def __init__(self, cards: Dict[str, Card], initial: GameState):
        self.cards = cards
        self.state = initial
        self._undo: List[GameState] = []

    def snapshot(self) -> None:
        self._undo.append(copy.deepcopy(self.state))
        if len(self._undo) > 50:
            self._undo = self._undo[-50:]

    def undo(self) -> None:
        if self._undo:
            self.state = self._undo.pop()
            self.state.log.append("UNDO")

    def _start_next_turn(self) -> None:
        self.state.turn += 1
        self.state.energy_max += 1
        self.state.energy_cur = self.state.energy_max
        self.state.log.append(f"TURN {self.state.turn} start: energy {self.state.energy_cur}/{self.state.energy_max}")

    def next_phase(self) -> None:
        self.snapshot()
        idx = PHASES.index(self.state.phase) if self.state.phase in PHASES else 0
        nxt = PHASES[(idx + 1) % len(PHASES)]
        if self.state.phase == "LIVESET" and nxt == "MAIN":
            self._start_next_turn()
        self.state.phase = nxt
        self.state.log.append(f"NEXT -> {self.state.phase}")

    def draw(self, n: int = 1) -> None:
        self.snapshot()
        n = max(1, int(n))
        for _ in range(n):
            if not self.state.deck:
                self.state.log.append("Deck empty")
                break
            cid = self.state.deck.pop(0)
            self.state.hand.append(cid)
        self.state.log.append(f"Draw {n}")

    def _is_live(self, cid: str) -> bool:
        c = self.cards.get(cid)
        if not c:
            return False
        t = (c.card_type or "").upper()
        if t == "LIVE":
            return True
        if t == "MEMBER":
            return False
        if (c.img_orient or "").lower() == "landscape":
            return True
        return False

    def play_to_stage(self, cid: str, slot: str) -> None:
        slot = (slot or "").upper()
        if slot not in self.state.stage:
            return
        if cid not in self.state.hand:
            return

        if self._is_live(cid):
            c = self.cards[cid]
            self.state.popup = {
                "mode":"optional",
                "kind":"info",
                "content":"text",
                "title":"プレイ不可",
                "text": f"{c.card_no} はライブカード（横）として扱われるためステージに出せません。",
                "closable": True,
                "next_closes": True,
            }
            self.state.log.append(f"BLOCK stage: {c.card_no} (LIVE)")
            return

        self.snapshot()
        self.state.hand.remove(cid)
        old = self.state.stage[slot]
        if old:
            self.state.waiting.append(old)
            self.state.energies_under[slot] = 0
        self.state.stage[slot] = cid
        self.state.log.append(f"Stage[{slot}] <- {self.cards[cid].card_no}")

    def add_energy_under(self, slot: str, k: int = 1) -> None:
        slot = (slot or "").upper()
        if slot not in self.state.energies_under:
            return
        self.snapshot()
        self.state.energies_under[slot] += max(1,int(k))
        self.state.log.append(f"Energy under {slot} +{k}")

    def move_to_liveset(self, cids: List[str]) -> None:
        self.snapshot()
        for cid in cids:
            if cid in self.state.hand:
                if len(self.state.liveset) >= 3:
                    self.state.log.append("LiveSet full (max 3)")
                    break
                self.state.hand.remove(cid)
                self.state.liveset.append(cid)
        self.state.log.append("Move to LiveSet")

    def move_liveset_to_resolve(self) -> None:
        self.snapshot()
        self.state.resolve.extend(self.state.liveset)
        self.state.liveset = []
        self.state.popup = {
            "mode":"confirm",
            "kind":"resolve_confirm",
            "content":"cards",
            "title":"Resolve確認",
            "text":"解決領域のカードを確認してください。",
            "closable": False,
            "next_closes": True,
            "requires_choice": False,
            "next_action": "ack_resolve",
            "ack_action": "ack_resolve",
        }
        self.state.log.append("LiveSet -> Resolve")

    def ack_resolve(self) -> None:
        self.snapshot()
        self.state.waiting.extend(self.state.resolve)
        self.state.resolve = []
        self.state.popup = None
        self.state.log.append("Resolve ACK -> Waiting")

    def open_waiting_popup(self) -> None:
        self.state.popup = {"mode":"optional","kind":"waiting","content":"cards","title":"控え室","closable": True,"next_closes": False}

    def close_popup(self, force: bool = False) -> None:
        if force or (self.state.popup and self.state.popup.get("closable", True)):
            self.state.popup = None

    def activate(self, slot: str) -> None:
        slot = (slot or "").upper()
        cid = self.state.stage.get(slot)
        if not cid:
            return
        self.snapshot()
        c = self.cards[cid]
        self.state.popup = {
            "mode":"confirm",
            "kind":"activate",
            "content":"text",
            "title": f"起動: {c.name or c.card_no}",
            "text": (c.text or "(テキスト未取得)"),
            "closable": True,
            "next_closes": True,
            "requires_choice": False,
            "next_action": "close_popup",
        }
        self.state.log.append(f"Activate {slot}: {c.card_no}")

    def to_view(self, image_url_by_cid) -> Dict[str, Any]:
        s = self.state
        def pack(cid: str) -> Dict[str, Any]:
            c = self.cards[cid]
            return {
                "cid": c.cid,
                "card_no": c.card_no,
                "rarity": c.rarity,
                "name": c.name,
                "card_type": c.card_type,
                "img_orient": c.img_orient,
                "text": c.text,
                "img": image_url_by_cid(cid),
            }
        view = {
            "turn": s.turn,
            "phase": s.phase,
            "counts": {"deck": len(s.deck), "waiting": len(s.waiting)},
            "energy": {"cur": s.energy_cur, "max": s.energy_max},
            "hand": [pack(cid) for cid in s.hand],
            "liveset": [pack(cid) for cid in s.liveset],
            "stage": {k: (pack(v) if v else None) for k,v in s.stage.items()},
            "energies_under": dict(s.energies_under),
            "waiting_top": pack(s.waiting[-1]) if s.waiting else None,
            "waiting": [pack(cid) for cid in s.waiting],
            "resolve": [pack(cid) for cid in s.resolve],
            "log": s.log[-200:],
            "popup": s.popup,
        }
        return view

def make_initial(deck_cids: List[str], auto_draw: int = 7) -> GameState:
    st = GameState()
    st.deck = deck_cids[:]
    random.shuffle(st.deck)
    st.turn = 1
    st.energy_max = 4
    st.energy_cur = 4
    st.log.append("INIT")
    for _ in range(max(0,int(auto_draw))):
        if st.deck:
            st.hand.append(st.deck.pop(0))
    st.log.append(f"INIT draw {auto_draw}")
    return st
