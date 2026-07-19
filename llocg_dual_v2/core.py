# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import csv
import json
import random
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

BUILD_TAG = "llocg_dual_v2_tied_success_two_zone_block_20260720a"
ENERGY_DECK_SIZE = 12
OPENING_HAND_SIZE = 6
OPENING_ENERGY_SIZE = 3


class Phase(str, Enum):
    MULLIGAN_FIRST = "MULLIGAN_FIRST"
    MULLIGAN_SECOND = "MULLIGAN_SECOND"
    ACTIVE_FIRST = "ACTIVE_FIRST"
    ENERGY_FIRST = "ENERGY_FIRST"
    DRAW_FIRST = "DRAW_FIRST"
    MAIN_FIRST = "MAIN_FIRST"
    ACTIVE_SECOND = "ACTIVE_SECOND"
    ENERGY_SECOND = "ENERGY_SECOND"
    DRAW_SECOND = "DRAW_SECOND"
    MAIN_SECOND = "MAIN_SECOND"
    LIVE_SET_FIRST = "LIVE_SET_FIRST"
    LIVE_SET_SECOND = "LIVE_SET_SECOND"
    PERFORMANCE_FIRST = "PERFORMANCE_FIRST"
    PERFORMANCE_SECOND = "PERFORMANCE_SECOND"
    LIVE_JUDGMENT = "LIVE_JUDGMENT"
    TURN_END = "TURN_END"
    GAME_OVER = "GAME_OVER"


PHASE_LABELS: Dict[Phase, str] = {
    Phase.MULLIGAN_FIRST: "先攻プレイヤーのマリガン",
    Phase.MULLIGAN_SECOND: "後攻プレイヤーのマリガン",
    Phase.ACTIVE_FIRST: "先攻通常フェイズ：アクティブフェイズ",
    Phase.ENERGY_FIRST: "先攻通常フェイズ：エネルギーフェイズ",
    Phase.DRAW_FIRST: "先攻通常フェイズ：ドローフェイズ",
    Phase.MAIN_FIRST: "先攻通常フェイズ：メインフェイズ",
    Phase.ACTIVE_SECOND: "後攻通常フェイズ：アクティブフェイズ",
    Phase.ENERGY_SECOND: "後攻通常フェイズ：エネルギーフェイズ",
    Phase.DRAW_SECOND: "後攻通常フェイズ：ドローフェイズ",
    Phase.MAIN_SECOND: "後攻通常フェイズ：メインフェイズ",
    Phase.LIVE_SET_FIRST: "ライブカードセットフェイズ：先攻プレイヤーのセット",
    Phase.LIVE_SET_SECOND: "ライブカードセットフェイズ：後攻プレイヤーのセット",
    Phase.PERFORMANCE_FIRST: "先攻パフォーマンスフェイズ",
    Phase.PERFORMANCE_SECOND: "後攻パフォーマンスフェイズ",
    Phase.LIVE_JUDGMENT: "ライブ勝敗判定フェイズ",
    Phase.TURN_END: "ターン終了処理",
    Phase.GAME_OVER: "対戦終了",
}


@dataclass
class PlayerState:
    player_id: int
    deck_code: str
    main_deck: List[str]
    hand: List[str] = field(default_factory=list)
    energy_deck_remaining: int = ENERGY_DECK_SIZE
    energy_active: int = 0
    energy_wait: int = 0
    energy_under: int = 0
    stage: Dict[str, Optional[str]] = field(default_factory=lambda: {"L": None, "C": None, "R": None})
    waiting_room: List[str] = field(default_factory=list)
    live_set: List[str] = field(default_factory=list)
    success_zone: List[str] = field(default_factory=list)
    mulligan_done: bool = False
    live_set_committed: bool = False

    def public_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "deck_code": self.deck_code,
            "deck_count": len(self.main_deck),
            "hand": list(self.hand),
            "hand_count": len(self.hand),
            "energy_deck_remaining": self.energy_deck_remaining,
            "energy_active": self.energy_active,
            "energy_wait": self.energy_wait,
            "energy_under": self.energy_under,
            "stage": dict(self.stage),
            "waiting_room_count": len(self.waiting_room),
            "live_set": list(self.live_set),
            "success_zone": list(self.success_zone),
            "mulligan_done": self.mulligan_done,
            "live_set_committed": self.live_set_committed,
        }


@dataclass
class MatchState:
    players: List[PlayerState]
    first_player_id: int = 0
    turn: int = 1
    phase: Phase = Phase.MULLIGAN_FIRST
    log: List[str] = field(default_factory=list)
    winner_player_id: Optional[int] = None
    game_result: str = ""
    judgment_step: str = ""
    judgment_active_player_id: Optional[int] = None
    live_scores: List[int] = field(default_factory=lambda: [0, 0])
    live_winners: List[int] = field(default_factory=list)
    success_move_queue: List[int] = field(default_factory=list)
    success_moved_player_ids: List[int] = field(default_factory=list)
    judgment_prompt: Dict[str, Any] = field(default_factory=dict)


class DeckLoadError(RuntimeError):
    pass


def _canon_cardno(value: Any) -> str:
    return str(value or "").strip()


def _read_deck_tsv(path: Path) -> List[str]:
    cards: List[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    for row in rows:
        if not row:
            continue
        lowered = [str(x).strip().lower() for x in row]
        if any(x in {"cardnumber", "card_no", "card number", "カード番号"} for x in lowered):
            continue
        count = 0
        cardno = ""
        for cell in row:
            s = str(cell).strip()
            if not s:
                continue
            if not cardno and ("-" in s or "!" in s):
                cardno = s
            if count <= 0:
                try:
                    v = int(float(s))
                    if 0 < v <= 60:
                        count = v
                except ValueError:
                    pass
        if cardno and count > 0:
            cards.extend([cardno] * count)
    return cards


def discover_data_root(project_root: Path, explicit: Optional[Path] = None) -> Path:
    if explicit:
        p = explicit if explicit.is_absolute() else project_root / explicit
        return p.resolve()
    candidates = [
        project_root / "llocg_db_out_full",
        project_root / "db_out_full",
        project_root / "llocg_db_out",
        project_root,
    ]
    for p in candidates:
        if (p / "decklists").is_dir() or (p / "sim_decks").is_dir():
            return p.resolve()
    return candidates[0].resolve()


def load_deck(data_root: Path, code: str) -> List[str]:
    candidates = [
        data_root / "sim_decks" / f"deck_{code}.json",
        data_root / "decklists" / f"{code}.tsv",
        data_root / "sim_decks" / f"deck_{code}.tsv",
        data_root / "decklists" / f"deck_{code}.tsv",
        data_root / "decklists" / f"{code}.txt",
    ]
    for path in candidates:
        if not path.exists():
            continue
        if path.suffix.lower() == ".json":
            obj = json.loads(path.read_text(encoding="utf-8"))
            entries = obj.get("cards", []) if isinstance(obj, dict) else []
            cards: List[str] = []
            for ent in entries:
                if not isinstance(ent, dict):
                    continue
                cn = _canon_cardno(ent.get("db_id") or ent.get("cardnumber") or ent.get("card_no") or ent.get("tsv_card_no"))
                try:
                    count = int(ent.get("count", 0) or 0)
                except (TypeError, ValueError):
                    count = 0
                if cn and count > 0:
                    cards.extend([cn] * count)
            if cards:
                return cards
        else:
            cards = _read_deck_tsv(path)
            if cards:
                return cards
    looked = "\n".join(f"- {p}" for p in candidates)
    raise DeckLoadError(f"deck file not found or empty for code={code}. Looked for:\n{looked}")


class DualMatchEngine:
    """Rule-flow-first two-player engine.

    This class owns the only phase value. UI code must never mutate phase.
    Every action snapshots both players, match metadata, and RNG state.
    """

    def __init__(self, deck1: Sequence[str], deck2: Sequence[str], code1: str, code2: str, seed: int = 1, first_player_id: int = 0):
        self.rng = random.Random(seed)
        self.history: List[Tuple[MatchState, object]] = []
        d1, d2 = list(deck1), list(deck2)
        self.rng.shuffle(d1)
        self.rng.shuffle(d2)
        self.state = MatchState(
            players=[PlayerState(0, code1, d1), PlayerState(1, code2, d2)],
            first_player_id=first_player_id,
            phase=Phase.MULLIGAN_FIRST,
        )
        self._draw_opening_hand(self.state.players[0])
        self._draw_opening_hand(self.state.players[1])
        self.state.log.append("[SETUP] 両プレイヤーがメインデッキをシャッフルし、手札6枚を引いた")
        self._assert_invariants()

    @classmethod
    def from_codes(cls, project_root: Path, code1: str, code2: str, seed: int = 1, data_root: Optional[Path] = None) -> "DualMatchEngine":
        root = discover_data_root(project_root, data_root)
        return cls(load_deck(root, code1), load_deck(root, code2), code1, code2, seed=seed)

    def _draw_opening_hand(self, p: PlayerState) -> None:
        if len(p.main_deck) < OPENING_HAND_SIZE:
            raise DeckLoadError(f"deck {p.deck_code} has fewer than {OPENING_HAND_SIZE} cards")
        p.hand.extend(p.main_deck[:OPENING_HAND_SIZE])
        del p.main_deck[:OPENING_HAND_SIZE]

    def _snapshot(self) -> None:
        self.history.append((copy.deepcopy(self.state), self.rng.getstate()))
        if len(self.history) > 200:
            self.history = self.history[-200:]

    def undo(self) -> bool:
        if not self.history:
            return False
        self.state, rng_state = self.history.pop()
        self.rng.setstate(rng_state)
        self._assert_invariants()
        return True

    def active_player_id(self) -> int:
        first = self.state.first_player_id
        second = 1 - first
        if self.state.phase in {Phase.MULLIGAN_FIRST, Phase.ACTIVE_FIRST, Phase.ENERGY_FIRST, Phase.DRAW_FIRST, Phase.MAIN_FIRST, Phase.LIVE_SET_FIRST, Phase.PERFORMANCE_FIRST}:
            return first
        if self.state.phase in {Phase.MULLIGAN_SECOND, Phase.ACTIVE_SECOND, Phase.ENERGY_SECOND, Phase.DRAW_SECOND, Phase.MAIN_SECOND, Phase.LIVE_SET_SECOND, Phase.PERFORMANCE_SECOND}:
            return second
        if self.state.phase == Phase.LIVE_JUDGMENT and self.state.judgment_active_player_id in {0, 1}:
            return int(self.state.judgment_active_player_id)
        return first

    def mulligan(self, player_id: int, selected_indices: Sequence[int], *, record_history: bool = True) -> None:
        """Resolve one player's mulligan as one match action.

        After the second mulligan, all mandatory setup/normal-phase steps that
        require no choice are executed immediately, stopping at the first main
        phase.  The whole sequence is covered by a single Undo snapshot.
        """
        expected_phase = Phase.MULLIGAN_FIRST if player_id == self.state.first_player_id else Phase.MULLIGAN_SECOND
        if self.state.phase != expected_phase:
            raise ValueError(f"mulligan is not available for player {player_id} in phase {self.state.phase.value}")
        p = self.state.players[player_id]
        indices = sorted(set(int(x) for x in selected_indices))
        if any(i < 0 or i >= len(p.hand) for i in indices):
            raise ValueError("mulligan hand index out of range")
        if record_history:
            self._snapshot()
        set_aside = [p.hand[i] for i in indices]
        selected = set(indices)
        p.hand = [cn for i, cn in enumerate(p.hand) if i not in selected]
        draw_n = len(set_aside)
        if len(p.main_deck) < draw_n:
            raise RuntimeError("not enough cards to complete mulligan")
        p.hand.extend(p.main_deck[:draw_n])
        del p.main_deck[:draw_n]
        p.main_deck.extend(set_aside)
        if draw_n > 0:
            self.rng.shuffle(p.main_deck)
        p.mulligan_done = True
        self.state.log.append(f"[MULLIGAN][P{player_id + 1}] {draw_n}枚を交換")
        if self.state.phase == Phase.MULLIGAN_FIRST:
            self.state.phase = Phase.MULLIGAN_SECOND
        else:
            for q in self.state.players:
                q.energy_active = OPENING_ENERGY_SIZE
                q.energy_wait = 0
                q.energy_deck_remaining = ENERGY_DECK_SIZE - OPENING_ENERGY_SIZE
            self.state.log.append("[SETUP] 両プレイヤーがエネルギーデッキ上から3枚をエネルギー置き場に移動")
            self.state.phase = Phase.ACTIVE_FIRST
            self._run_automatic_steps()
        self._assert_invariants()

    @staticmethod
    def _is_automatic_phase(phase: Phase) -> bool:
        return phase in {
            Phase.ACTIVE_FIRST, Phase.ENERGY_FIRST, Phase.DRAW_FIRST,
            Phase.ACTIVE_SECOND, Phase.ENERGY_SECOND, Phase.DRAW_SECOND,
        }

    def _advance_one_without_snapshot(self) -> None:
        """Execute exactly one rule step. Caller owns the Undo snapshot."""
        p = self.state.players[self.active_player_id()]
        phase = self.state.phase
        if phase == Phase.ACTIVE_FIRST:
            p.energy_active += p.energy_wait
            p.energy_wait = 0
            self.state.phase = Phase.ENERGY_FIRST
        elif phase == Phase.ENERGY_FIRST:
            self._energy_phase(p)
            self.state.phase = Phase.DRAW_FIRST
        elif phase == Phase.DRAW_FIRST:
            self._draw(p, 1)
            self.state.phase = Phase.MAIN_FIRST
        elif phase == Phase.MAIN_FIRST:
            self.state.phase = Phase.ACTIVE_SECOND
        elif phase == Phase.ACTIVE_SECOND:
            p.energy_active += p.energy_wait
            p.energy_wait = 0
            self.state.phase = Phase.ENERGY_SECOND
        elif phase == Phase.ENERGY_SECOND:
            self._energy_phase(p)
            self.state.phase = Phase.DRAW_SECOND
        elif phase == Phase.DRAW_SECOND:
            self._draw(p, 1)
            self.state.phase = Phase.MAIN_SECOND
        elif phase == Phase.MAIN_SECOND:
            # A live-set selection must be committed through the legacy rules
            # runtime before either player may leave their live-set step.
            for q in self.state.players:
                q.live_set_committed = False
            self.state.phase = Phase.LIVE_SET_FIRST
        elif phase == Phase.LIVE_SET_FIRST:
            if not p.live_set_committed:
                raise ValueError("先攻プレイヤーのライブセットが確定していません")
            self.state.phase = Phase.LIVE_SET_SECOND
        elif phase == Phase.LIVE_SET_SECOND:
            if not p.live_set_committed:
                raise ValueError("後攻プレイヤーのライブセットが確定していません")
            self.state.phase = Phase.PERFORMANCE_FIRST
        elif phase == Phase.PERFORMANCE_FIRST:
            self.state.phase = Phase.PERFORMANCE_SECOND
        elif phase == Phase.PERFORMANCE_SECOND:
            self.state.phase = Phase.LIVE_JUDGMENT
        elif phase == Phase.LIVE_JUDGMENT:
            self.state.phase = Phase.TURN_END
        elif phase == Phase.TURN_END:
            self.state.turn += 1
            for q in self.state.players:
                q.live_set_committed = False
            self._reset_judgment_state()
            self.state.phase = Phase.ACTIVE_FIRST
        elif phase == Phase.GAME_OVER:
            raise ValueError("対戦は終了しています")
        else:
            raise RuntimeError(f"unsupported phase: {phase}")
        self.state.log.append(f"[PHASE] {PHASE_LABELS[self.state.phase]}")

    def _run_automatic_steps(self) -> None:
        """Run mandatory no-choice phases until the next player decision."""
        guard = 0
        while self._is_automatic_phase(self.state.phase):
            self._advance_one_without_snapshot()
            guard += 1
            if guard > 16:
                raise RuntimeError("automatic phase loop did not reach a decision phase")

    def advance(self, *, record_history: bool = True) -> None:
        """Commit the current decision phase, then auto-run mandatory phases."""
        if self.state.phase in {Phase.MULLIGAN_FIRST, Phase.MULLIGAN_SECOND}:
            raise ValueError("マリガンは交換対象を確定して進めてください")
        if self._is_automatic_phase(self.state.phase):
            raise ValueError("このフェイズは自動処理されます")
        if self.state.phase in {
            Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND,
            Phase.LIVE_JUDGMENT, Phase.TURN_END, Phase.GAME_OVER,
        }:
            raise ValueError(
                "パフォーマンス以降は専用の2人対戦トランザクションで処理します。汎用advanceでは進められません"
            )
        if record_history:
            self._snapshot()
        self._advance_one_without_snapshot()
        self._run_automatic_steps()
        self._assert_invariants()

    def complete_performance(self, player_id: int, *, record_history: bool = True) -> None:
        """Close the currently active player's performance phase.

        The legacy one-player rules runtime executes all substeps inside the
        performance phase.  The dual controller calls this method only after
        that runtime has actually left its LIVE_* subphase and has no pending
        resolution left.  This keeps the central phase authoritative without
        advancing it merely because the central NEXT button was pressed.
        """
        if self.state.phase not in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND}:
            raise ValueError("現在はパフォーマンスフェイズではありません")
        if int(player_id) != self.active_player_id():
            raise ValueError("現在の手番プレイヤーのパフォーマンスではありません")
        if record_history:
            self._snapshot()
        self._advance_one_without_snapshot()
        self._assert_invariants()

    def _reset_judgment_state(self) -> None:
        self.state.judgment_step = ""
        self.state.judgment_active_player_id = None
        self.state.live_scores = [0, 0]
        self.state.live_winners = []
        self.state.success_move_queue = []
        self.state.success_moved_player_ids = []
        self.state.judgment_prompt = {}

    def set_judgment_active_player(self, player_id: Optional[int]) -> None:
        if player_id is not None and int(player_id) not in {0, 1}:
            raise ValueError("invalid judgment player")
        self.state.judgment_active_player_id = None if player_id is None else int(player_id)

    def enter_turn_end(self, *, first_player_id: int, winner_player_id: Optional[int] = None, game_result: str = "") -> None:
        """Commit the dual live-judgment result without using the one-player placement flow."""
        if self.state.phase != Phase.LIVE_JUDGMENT:
            raise ValueError("現在はライブ勝敗判定フェイズではありません")
        if int(first_player_id) not in {0, 1}:
            raise ValueError("invalid first player")
        self.state.first_player_id = int(first_player_id)
        self.state.winner_player_id = winner_player_id
        self.state.game_result = str(game_result or "")
        self.state.judgment_active_player_id = None
        self.state.judgment_prompt = {}
        if self.state.game_result:
            self.state.phase = Phase.GAME_OVER
            self.state.log.append(f"[GAME OVER] {self.state.game_result}")
        else:
            self.state.phase = Phase.TURN_END
            self.state.log.append(f"[PHASE] {PHASE_LABELS[self.state.phase]}")
        self._assert_invariants()

    def finish_turn(self, *, record_history: bool = True) -> None:
        if self.state.phase != Phase.TURN_END:
            raise ValueError("現在はターン終了処理ではありません")
        if record_history:
            self._snapshot()
        self._advance_one_without_snapshot()
        self._run_automatic_steps()
        self._assert_invariants()

    def _energy_phase(self, p: PlayerState) -> None:
        if p.energy_deck_remaining <= 0:
            return
        p.energy_deck_remaining -= 1
        p.energy_active += 1
        self.state.log.append(f"[ENERGY][P{p.player_id + 1}] エネルギーを1枚置いた")

    def _draw(self, p: PlayerState, n: int) -> None:
        for _ in range(n):
            if not p.main_deck:
                break
            p.hand.append(p.main_deck.pop(0))
        self.state.log.append(f"[DRAW][P{p.player_id + 1}] {n}枚引いた")

    def action_label(self) -> str:
        phase = self.state.phase
        if phase in {Phase.MULLIGAN_FIRST, Phase.MULLIGAN_SECOND}:
            return "マリガン決定"
        if phase == Phase.LIVE_JUDGMENT:
            return {
                "": "ライブ勝敗判定開始",
                "INITIAL_SCORE": "ライブ成功時処理へ",
                "SUCCESS_FIRST": "先攻の成功時処理を進める",
                "SUCCESS_SECOND": "後攻の成功時処理を進める",
                "FINAL_SCORE": "最終スコアを比較",
                "RESULT_CONFIRM": "勝敗結果を確認",
                "PICK_SUCCESS": "成功ライブを決定",
                "CLEANUP": "ライブ終了処理",
            }.get(self.state.judgment_step, "ライブ勝敗判定を進める")
        if phase == Phase.GAME_OVER:
            return "対戦終了"
        return {
            Phase.MAIN_FIRST: "メインフェイズ終了",
            Phase.MAIN_SECOND: "メインフェイズ終了",
            Phase.LIVE_SET_FIRST: "ライブセット確定",
            Phase.LIVE_SET_SECOND: "ライブセット確定",
            Phase.PERFORMANCE_FIRST: "先攻パフォーマンス進行",
            Phase.PERFORMANCE_SECOND: "後攻パフォーマンス進行",
            Phase.TURN_END: "次のターンへ",
        }.get(phase, "NEXT")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "build_tag": BUILD_TAG,
            "turn": self.state.turn,
            "phase": self.state.phase.value,
            "phase_label": PHASE_LABELS[self.state.phase],
            "action_label": self.action_label(),
            "active_player_id": self.active_player_id(),
            "first_player_id": self.state.first_player_id,
            "players": [p.public_dict() for p in self.state.players],
            "history_depth": len(self.history),
            "winner_player_id": self.state.winner_player_id,
            "game_result": self.state.game_result,
            "judgment_step": self.state.judgment_step,
            "judgment_active_player_id": self.state.judgment_active_player_id,
            "live_scores": list(self.state.live_scores),
            "live_winners": list(self.state.live_winners),
            "success_move_queue": list(self.state.success_move_queue),
            "success_moved_player_ids": list(self.state.success_moved_player_ids),
            "judgment_prompt": copy.deepcopy(self.state.judgment_prompt),
            "log": list(self.state.log[-80:]),
        }

    def _assert_invariants(self) -> None:
        if len(self.state.players) != 2:
            raise AssertionError("match must have exactly two players")
        for p in self.state.players:
            if p.energy_active < 0 or p.energy_wait < 0 or p.energy_under < 0 or p.energy_deck_remaining < 0:
                raise AssertionError("negative energy state")
            if p.energy_active + p.energy_wait + p.energy_under + p.energy_deck_remaining != ENERGY_DECK_SIZE:
                raise AssertionError("energy card conservation failed")
            if len(p.hand) < 0 or len(p.main_deck) < 0:
                raise AssertionError("negative card count")
        if self.state.phase == Phase.MULLIGAN_SECOND and not self.state.players[self.state.first_player_id].mulligan_done:
            raise AssertionError("second mulligan started before first completed")
