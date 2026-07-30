# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import base64
import copy
import csv
import datetime as _dt
import json
import os
import pickle
import re
import threading
import time
from collections import Counter
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from loveca_app.autoplay import suggest_autoplay_action
from llocg_ui.server import App, HTML as SINGLE_HTML
from llocg_ui.views import make_view_state
from .core import ENERGY_DECK_SIZE, DualMatchEngine, Phase, discover_data_root

BUILD_TAG = "llocg_dual_v2_cpu_decision_trace_20260730a"


@dataclass
class PlayerViewRuntime:
    key: str
    player_id: int
    label: str
    color: str
    app: App


class LegacyUIAdapter:
    """Connect the legacy board UI to the v2 match controller.

    The v2 engine owns match order, turn/phase flow and match-level Undo.
    Each legacy App remains the authoritative rules runtime for that player's
    card play and effect resolution.  Polling the board must never overwrite
    stage/pending/effect state.
    """

    _APP_STATIC_ATTRS = {"root", "outdir", "cards_db", "img", "rng"}
    _CENTRAL_ONLY_COMMANDS = {
        "undo", "mulligan_next", "end_turn",
        "opponent_wait_delta", "opponent_success_delta", "turn_order_set",
    }
    # Presentation-only YELL confirmation flags.  Once acknowledged during a
    # performance, these must not be resurrected when the same legacy App is
    # temporarily re-entered at LIVE_RESOLVE for the dual 8.4 success timing.
    _YELL_NOTICE_ATTRS = (
        "yell_reveal_notice", "yell_reveal_pending", "show_yell_reveal",
        "yell_reveal_open", "yell_popup", "yell_popup_open",
        "show_yell_popup", "reveal_popup", "reveal_popup_open",
        "reveal_confirm", "reveal_confirm_pending",
    )
    # The legacy runtime is the authority for rule 8.3.15/8.3.16.
    # Read its explicit attempt result instead of inferring success from whether
    # set_zone happens to be populated at the adapter boundary.  Different
    # runtime generations have exported several aliases, so normalize them here.
    _ATTEMPT_RESULT_ATTRS = (
        "last_attempt_result", "live_attempt_result", "last_live_attempt_result",
        "attempt_result", "last_live_result", "live_result",
    )
    _ATTEMPT_SUCCESS_ATTRS = (
        "last_attempt_success", "last_attempt_succeeded",
        "live_attempt_success", "live_attempt_succeeded",
        "attempt_success", "attempt_succeeded", "last_attempt_ok",
        "last_live_success", "last_live_succeeded",
    )
    _ATTEMPT_FAILURE_ATTRS = (
        "last_attempt_failed", "live_attempt_failed", "attempt_failed",
        "last_live_failed",
    )
    _MAIN_COMMANDS = {
        "play", "activate_to_green", "toggle_stage_active",
        "resolve_pending", "ack_refresh_notice", "ack_yell_reveal", "next",
    }
    _GENERAL_EFFECT_COMMANDS = {
        "resolve_pending", "ack_refresh_notice", "ack_yell_reveal", "next",
    }

    def __init__(self, engine: DualMatchEngine, p1: PlayerViewRuntime, p2: PlayerViewRuntime):
        self.engine = engine
        self.players: Dict[str, PlayerViewRuntime] = {"p1": p1, "p2": p2}
        self.lock = threading.RLock()
        self.history: list[Dict[str, Any]] = []
        self.reset_config: Dict[str, Any] = {}
        # Canonical card-detail records are loaded lazily from the project DB.
        # The runtime cards_db can intentionally omit raw effect text.
        self._detail_db_cache: Optional[Dict[str, Any]] = None
        self._reset_runtimes_for_new_match()
        self._sync_core_to_views(include_zones=True)

    def configure_reset(
        self,
        *,
        project_root: Path,
        data_root: Path,
        deck1: str,
        deck2: str,
        seed: int,
        debug: bool,
        preserve_start_env: bool,
    ) -> None:
        self.reset_config = {
            "project_root": Path(project_root),
            "data_root": Path(data_root),
            "deck1": str(deck1),
            "deck2": str(deck2),
            "seed": int(seed),
            "debug": bool(debug),
            "preserve_start_env": bool(preserve_start_env),
        }

    def runtime(self, key: str) -> PlayerViewRuntime:
        if key not in self.players:
            raise KeyError(key)
        return self.players[key]


    def _reset_runtimes_for_new_match(self) -> None:
        """Remove one-player start overrides from the renderer runtimes."""
        for rt in self.players.values():
            gs = rt.app.gs
            gs.stage = {"L": None, "C": None, "R": None}
            gs.green_room = []
            gs.set_zone = []
            gs.success_zone = []
            gs.resolve_zone = []
            gs.pending = []
            gs.undo_stack = []
            gs.banner_text = ""
            gs.live_start_prompted = False
            setattr(rt.app, "_dual_performance_exit_pending", False)
            setattr(rt.app, "_dual_performance_entry_phase", "")
            setattr(rt.app, "_dual_performance_started", False)
            setattr(rt.app, "_dual_last_boundary_snapshot", None)
            setattr(rt.app, "_dual_judgment_entry_phase", "LIVE_RESOLVE")
            setattr(rt.app, "_dual_deferred_success_pending", [])
            setattr(rt.app, "_dual_success_runtime_started", False)
            setattr(rt.app, "_dual_success_runtime_done", False)
            setattr(rt.app, "_dual_live_attempt_succeeded", None)
            setattr(rt.app, "_dual_yell_notice_acknowledged", False)

    @staticmethod
    def _legacy_phase(phase: Phase, player_id: int, active_id: int) -> str:
        if phase in {Phase.MULLIGAN_FIRST, Phase.MULLIGAN_SECOND}:
            return "MULLIGAN" if player_id == active_id else "DUAL_WAIT_MULLIGAN"
        if phase in {
            Phase.ACTIVE_FIRST, Phase.ACTIVE_SECOND,
            Phase.ENERGY_FIRST, Phase.ENERGY_SECOND,
            Phase.DRAW_FIRST, Phase.DRAW_SECOND,
            Phase.MAIN_FIRST, Phase.MAIN_SECOND,
        }:
            return "MAIN" if player_id == active_id else "DUAL_WAIT_NORMAL"
        if phase in {Phase.LIVE_SET_FIRST, Phase.LIVE_SET_SECOND}:
            return "LIVE_SET" if player_id == active_id else "DUAL_WAIT_LIVE_SET"
        if phase in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND}:
            return "LIVE_RESOLVE" if player_id == active_id else "DUAL_WAIT_PERFORMANCE"
        if phase == Phase.LIVE_JUDGMENT:
            return "DUAL_JUDGMENT" if player_id == active_id else "DUAL_WAIT_JUDGMENT"
        if phase == Phase.GAME_OVER:
            return "DUAL_GAME_OVER"
        return "DUAL_WAIT"

    @staticmethod
    def _slot_cardnumber(slot: Any) -> Optional[str]:
        if slot is None:
            return None
        cn = getattr(slot, "cardnumber", None)
        if cn is not None:
            return str(cn)
        if isinstance(slot, str):
            return slot
        return None

    @staticmethod
    def _energy_under(gs: Any) -> int:
        total = 0
        for slot in dict(getattr(gs, "stage", {}) or {}).values():
            if slot is not None:
                total += max(0, int(getattr(slot, "energy_under", 0) or 0))
        return total

    def _capture_app(self, app: App) -> Dict[str, Any]:
        memo = {id(app.cards_db): app.cards_db}
        data: Dict[str, Any] = {
            "gs": copy.deepcopy(app.gs, memo),
            "rng_state": app.rng.getstate(),
            "attrs": {},
        }
        for name, value in vars(app).items():
            if name in self._APP_STATIC_ATTRS or name == "gs":
                continue
            if callable(value):
                continue
            try:
                copied = copy.deepcopy(value, memo)
                pickle.dumps(copied, protocol=pickle.HIGHEST_PROTOCOL)
                data["attrs"][name] = copied
            except Exception:
                # Runtime-only helpers are not required for board-state Undo.
                pass
        return data

    def _restore_app(self, app: App, snap: Dict[str, Any]) -> None:
        memo = {id(app.cards_db): app.cards_db}
        app.gs = copy.deepcopy(snap["gs"], memo)
        try:
            setattr(app.gs, "_cards_db", app.cards_db)
        except Exception:
            pass
        app.rng.setstate(snap["rng_state"])
        saved_attrs = dict(snap.get("attrs", {}) or {})
        for name in list(vars(app)):
            if name in self._APP_STATIC_ATTRS or name == "gs":
                continue
            if name not in saved_attrs:
                try:
                    delattr(app, name)
                except Exception:
                    pass
        for name, value in saved_attrs.items():
            setattr(app, name, copy.deepcopy(value, memo))

    def _capture_snapshot(self) -> Dict[str, Any]:
        return {
            "engine_state": copy.deepcopy(self.engine.state),
            "engine_rng_state": self.engine.rng.getstate(),
            "apps": {key: self._capture_app(rt.app) for key, rt in self.players.items()},
        }

    def _restore_snapshot(self, snap: Dict[str, Any]) -> None:
        self.engine.state = copy.deepcopy(snap["engine_state"])
        self.engine.rng.setstate(snap["engine_rng_state"])
        for key, app_snap in dict(snap.get("apps", {}) or {}).items():
            self._restore_app(self.runtime(key).app, app_snap)
        self._sync_metadata_to_views()

    def _push_history(self) -> None:
        self.history.append(self._capture_snapshot())
        if len(self.history) > 200:
            self.history = self.history[-200:]

    def _discard_failed_history(self) -> None:
        if self.history:
            snap = self.history.pop()
            self._restore_snapshot(snap)

    def export_suspend_data(self, label: str = "") -> Dict[str, Any]:
        with self.lock:
            state = self.state()
            payload = base64.b64encode(
                pickle.dumps(self._capture_snapshot(), protocol=pickle.HIGHEST_PROTOCOL)
            ).decode("ascii")
            return {
                "format": "llocg_dual_v2_suspend_state",
                "format_version": 1,
                "build_tag": BUILD_TAG,
                "created_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                "label": str(label or ""),
                "summary": {
                    "turn": state.get("turn"),
                    "phase": state.get("phase"),
                    "phase_label": state.get("phase_label"),
                    "active_player_key": state.get("active_player_key"),
                    "first_player_id": state.get("first_player_id"),
                    "winner_player_id": state.get("winner_player_id"),
                    "game_result": state.get("game_result"),
                    "players": state.get("players"),
                },
                "log": list(state.get("log", []) or []),
                "snapshot_b64": payload,
            }

    def import_suspend_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            if not isinstance(data, dict):
                raise ValueError("中断データの形式が不正です")
            if data.get("format") != "llocg_dual_v2_suspend_state":
                raise ValueError("2デッキ用シミュレーターの中断データではありません")
            raw = str(data.get("snapshot_b64", "") or "")
            if not raw:
                raise ValueError("中断データに復元用スナップショットがありません")
            try:
                snap = pickle.loads(base64.b64decode(raw.encode("ascii"), validate=True))
            except Exception as exc:
                raise ValueError(f"中断データを読み込めません: {exc}") from exc
            self._restore_snapshot(snap)
            self.history = []
            self.engine.history = []
            self.engine.state.log.append(
                f"[RESUME] 中断データから再開 label={str(data.get('label', '') or '')}"
            )
            self._sync_metadata_to_views()
            return self.state()

    @staticmethod
    def _normalize_record_result(value: Any) -> str:
        raw = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "p1": "p1_win",
            "p1_win": "p1_win",
            "player1": "p1_win",
            "player1_win": "p1_win",
            "win": "p1_win",
            "p2": "p2_win",
            "p2_win": "p2_win",
            "player2": "p2_win",
            "player2_win": "p2_win",
            "lose": "p2_win",
            "loss": "p2_win",
            "no": "no_game",
            "ng": "no_game",
            "nogame": "no_game",
            "no_game": "no_game",
            "draw": "no_game",
        }
        if raw not in aliases:
            raise ValueError("記録結果が不正です")
        return aliases[raw]

    def _append_match_result_record(self, result: str, state_before: Dict[str, Any]) -> Dict[str, Any]:
        result = self._normalize_record_result(result)
        data_root = Path((self.reset_config or {}).get("data_root") or self.players["p1"].app.root)
        record = {
            "schema_version": 1,
            "recorded_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "simulator": "dual_v2",
            "result": result,
            "winner_player_id": 0 if result == "p1_win" else (1 if result == "p2_win" else None),
            "turn": state_before.get("turn"),
            "phase": state_before.get("phase"),
            "game_result": state_before.get("game_result"),
            "players": state_before.get("players_by_key"),
            "build_tag": BUILD_TAG,
        }
        log_dir = data_root / "user_data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "loveca_match_results.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record

    def _fresh_reset_seed(self) -> int:
        return int(time.time() * 1000) & 0x7FFFFFFF

    def _reset_match_from_config(self) -> None:
        if not self.reset_config:
            raise RuntimeError("reset configuration is missing")
        cfg = dict(self.reset_config)
        project_root = Path(cfg["project_root"])
        data_root = Path(cfg["data_root"])
        deck1 = str(cfg["deck1"])
        deck2 = str(cfg["deck2"])
        debug = bool(cfg.get("debug", False))
        preserve_start_env = bool(cfg.get("preserve_start_env", False))
        new_seed = self._fresh_reset_seed()

        saved_env: Dict[str, str] = {}
        if not preserve_start_env:
            for key in list(os.environ):
                if key.startswith("LLOCG_START_") or key.startswith("LLOCG_DEBUG_"):
                    saved_env[key] = os.environ.pop(key)
        try:
            engine = DualMatchEngine.from_codes(project_root, deck1, deck2, seed=new_seed, data_root=data_root)
            p1_app = App(root=data_root, code="dual-v2-p1", deck_code=deck1, seed=new_seed, debug=debug)
            p2_app = App(root=data_root, code="dual-v2-p2", deck_code=deck2, seed=new_seed + 1, debug=debug)
        finally:
            os.environ.update(saved_env)

        self.engine = engine
        self.players["p1"].app = p1_app
        self.players["p2"].app = p2_app
        self.history = []
        try:
            self.engine.history = []
        except Exception:
            pass
        self._detail_db_cache = None
        self._reset_runtimes_for_new_match()
        self.engine.state.log.append(f"[RESET] new dual match seed={new_seed}")
        self._sync_core_to_views(include_zones=True)

    def record_result_and_reset(self, result: Any) -> Dict[str, Any]:
        with self.lock:
            state_before = self.state()
            record = self._append_match_result_record(str(result or ""), state_before)
            self._reset_match_from_config()
            self.engine.state.log.append(
                f"[MATCH-RECORD] result={record['result']} saved=user_data/logs/loveca_match_results.jsonl"
            )
            self._sync_metadata_to_views()
            return {"ok": True, "record": record, "state": self.state()}

    def _append_match_log(self, rt: PlayerViewRuntime) -> None:
        cursor = int(getattr(rt, "_match_log_cursor", 0) or 0)
        items = list(self.engine.state.log)
        if cursor < 0 or cursor > len(items):
            cursor = 0
        for line in items[cursor:]:
            rt.app.gs.log.append(str(line))
        setattr(rt, "_match_log_cursor", len(items))

    def _sync_opponent_contexts(self) -> None:
        for rt in self.players.values():
            other = self.runtime("p2" if rt.key == "p1" else "p1")
            rt.app.gs.opponent = self._make_opponent_context(other)
            rt.app.gs.opp = rt.app.gs.opponent
            wait_count = 0
            for slot in dict(getattr(other.app.gs, "stage", {}) or {}).values():
                if slot is not None and not bool(getattr(slot, "active", True)):
                    wait_count += 1
            rt.app.gs.opponent_wait_count = max(0, min(3, wait_count))
            rt.app.gs.opponent_success_count = max(
                0, min(2, len(list(getattr(other.app.gs, "success_zone", []) or [])))
            )
            rt.app.gs.opponent_excess_heart_count = max(
                0, min(9, int(getattr(other.app.gs, "last_excess_heart_count", 0) or 0))
            )

    @staticmethod
    def _stage_slot_context(slot: Any) -> Optional[SimpleNamespace]:
        if slot is None:
            return None
        cn = getattr(slot, "cardnumber", None)
        if cn is None and isinstance(slot, str):
            cn = slot
        cn = str(cn or "").strip()
        if not cn:
            return None
        return SimpleNamespace(
            cardnumber=cn,
            active=bool(getattr(slot, "active", True)),
            temp_blade=int(getattr(slot, "temp_blade", 0) or 0),
            temp_hearts=dict(getattr(slot, "temp_hearts", {}) or {}),
            temp_score=int(getattr(slot, "temp_score", 0) or 0),
            temp_cost=int(getattr(slot, "temp_cost", 0) or 0),
            temp_until=str(getattr(slot, "temp_until", "") or ""),
            energy_under=int(getattr(slot, "energy_under", 0) or 0),
            under_cards=list(getattr(slot, "under_cards", []) or []),
            heart_replace_color=str(getattr(slot, "heart_replace_color", "") or ""),
        )

    def _make_opponent_context(self, other: PlayerViewRuntime) -> SimpleNamespace:
        """Build a non-recursive opponent view for the shared one-player engine.

        The legacy effect helpers already know how to read ``gs.opponent`` for
        opponent comparisons.  Do not attach the real opponent GameState here:
        that would create recursive snapshots and allow accidental cross-player
        mutation from one-player resolvers.
        """
        gs = other.app.gs
        stage = {
            pos: self._stage_slot_context(dict(getattr(gs, "stage", {}) or {}).get(pos))
            for pos in ("L", "C", "R")
        }
        return SimpleNamespace(
            player_id=other.player_id,
            key=other.key,
            stage=stage,
            deck=list(getattr(gs, "deck", []) or []),
            deck_count=len(list(getattr(gs, "deck", []) or [])),
            hand_count=len(list(getattr(gs, "hand", []) or [])),
            green_room=list(getattr(gs, "green_room", []) or []),
            set_zone=list(getattr(gs, "set_zone", []) or []),
            success_zone=list(getattr(gs, "success_zone", []) or []),
            energy_active=int(getattr(gs, "energy_active", 0) or 0),
            energy_wait=int(getattr(gs, "energy_wait", 0) or 0),
            energy_total=int(getattr(gs, "energy_total", ENERGY_DECK_SIZE) or ENERGY_DECK_SIZE),
            live_score=int(getattr(gs, "last_attempt_final_score", 0) or 0),
            current_score=int(getattr(gs, "last_attempt_final_score", 0) or 0),
            last_excess_heart_count=int(getattr(gs, "last_excess_heart_count", 0) or 0),
        )

    def _sync_metadata_to_views(self) -> None:
        active_id = self.engine.active_player_id()
        match = self.engine.state
        for rt in self.players.values():
            gs = rt.app.gs
            gs.turn = int(match.turn)
            mapped_phase = self._legacy_phase(match.phase, rt.player_id, active_id)
            if match.phase in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND}:
                if rt.player_id == active_id:
                    # Preserve the real LIVE_* subphase. Polling must not reset
                    # LIVE_PERF/LIVE_ATTEMPT back to the entry phase.
                    current = str(getattr(gs, "phase", "") or "")
                    has_pending = bool(list(getattr(gs, "pending", []) or []))
                    exit_pending = bool(getattr(rt.app, "_dual_performance_exit_pending", False))
                    if not (self._legacy_is_performance_phase(current) or has_pending or exit_pending):
                        gs.phase = mapped_phase
                else:
                    gs.phase = mapped_phase
            elif match.phase == Phase.LIVE_JUDGMENT:
                if rt.player_id == active_id:
                    current = str(getattr(gs, "phase", "") or "")
                    has_pending = bool(list(getattr(gs, "pending", []) or []))
                    success_active = bool(getattr(rt.app, "_dual_success_runtime_started", False)) and not bool(
                        getattr(rt.app, "_dual_success_runtime_done", False)
                    )
                    if not (has_pending or success_active or current == "LIVE_RESOLVE"):
                        gs.phase = mapped_phase
                else:
                    gs.phase = mapped_phase
            else:
                gs.phase = mapped_phase
            gs.turn_order = "first" if rt.player_id == match.first_player_id else "second"
            gs.next_turn_order = ""
            # Do not clear the legacy live-flow guard while either player's
            # performance or the dual success timing is still in progress.
            # Clearing it when a player becomes the waiting side makes the old
            # App replay its YELL confirmation at LIVE_RESOLVE and can prevent
            # live-success triggers from being generated.
            if match.phase not in {
                Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND, Phase.LIVE_JUDGMENT
            } and not self._legacy_is_performance_phase(getattr(gs, "phase", "")):
                gs.live_start_prompted = False
            self._suppress_reopened_yell_notice(rt)
            self._append_match_log(rt)
        self._sync_opponent_contexts()

    def _sync_core_to_views(self, *, include_zones: bool) -> None:
        match = self.engine.state
        for rt in self.players.values():
            p = match.players[rt.player_id]
            gs = rt.app.gs
            if include_zones:
                gs.deck = list(p.main_deck)
                gs.hand = list(p.hand)
                gs.energy_active = int(p.energy_active)
                gs.energy_wait = int(p.energy_wait)
                gs.energy_total = ENERGY_DECK_SIZE
                gs.green_room = list(p.waiting_room)
                gs.set_zone = list(p.live_set)
                gs.success_zone = list(p.success_zone)
                # Stage/pending/resolve_zone are intentionally preserved.
                # They are owned by the legacy rules runtime after gameplay starts.
            self._append_match_log(rt)
        self._sync_metadata_to_views()

    def _sync_view_to_core(self, rt: PlayerViewRuntime) -> None:
        gs = rt.app.gs
        p = self.engine.state.players[rt.player_id]
        p.main_deck = list(getattr(gs, "deck", []) or [])
        p.hand = list(getattr(gs, "hand", []) or [])
        p.energy_active = max(0, int(getattr(gs, "energy_active", 0) or 0))
        p.energy_wait = max(0, int(getattr(gs, "energy_wait", 0) or 0))
        p.energy_under = self._energy_under(gs)
        p.energy_deck_remaining = max(
            0, ENERGY_DECK_SIZE - p.energy_active - p.energy_wait - p.energy_under
        )
        p.waiting_room = list(getattr(gs, "green_room", []) or [])
        p.live_set = list(getattr(gs, "set_zone", []) or [])
        p.success_zone = list(getattr(gs, "success_zone", []) or [])
        stage = dict(getattr(gs, "stage", {}) or {})
        p.stage = {pos: self._slot_cardnumber(stage.get(pos)) for pos in ("L", "C", "R")}

    def _sync_all_views_to_core(self) -> None:
        for rt in self.players.values():
            self._sync_view_to_core(rt)
        self.engine._assert_invariants()

    def _active_runtime(self) -> PlayerViewRuntime:
        return self.runtime("p1" if self.engine.active_player_id() == 0 else "p2")

    @staticmethod
    def _pending_text(item: Any) -> str:
        try:
            return json.dumps(item, ensure_ascii=False, sort_keys=True, default=str)
        except Exception:
            return str(item or "")

    @classmethod
    def _is_single_player_success_placement_pending(cls, item: Any) -> bool:
        text = cls._pending_text(item).lower()
        success = ("success" in text) or ("成功" in text)
        placement = any(token in text for token in (
            "success_zone", "success zone", "place_success", "put_success",
            "live_success_place", "success_live_place", "place_live",
            "success_zone_choice", "pick_success_live",
            "成功ライブカード置き場", "成功エリア", "成功置き場",
            "置くか", "置きますか", "置かない", "成功したライブを",
        ))
        if ("成功したライブ" in text or "成功ライブ" in text) and "置" in text:
            placement = True
        return bool(success and placement)

    @classmethod
    def _is_live_success_effect_pending(cls, item: Any) -> bool:
        if cls._is_single_player_success_placement_pending(item):
            return False
        text = cls._pending_text(item).lower()
        return ("live_success" in text) or ("ライブ成功時" in text) or ("ライブ成功" in text)

    @staticmethod
    def _notice_flags(gs: Any, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        names = (
            "refresh_notice", "refresh_notice_pending", "show_refresh_notice",
            "yell_reveal_notice", "yell_reveal_pending", "show_yell_reveal",
            "yell_reveal_open", "yell_popup", "yell_popup_open", "show_yell_popup",
            "reveal_popup", "reveal_popup_open", "reveal_confirm",
            "reveal_confirm_pending", "refresh_popup", "refresh_popup_open",
            "confirm_popup", "confirm_pending", "effect_confirm_pending",
            "auto_confirm_pending", "popup_open", "popup_pending",
            "modal_open", "modal_pending", "notice_pending", "ack_pending",
            "show_confirm",
        )
        out: Dict[str, Any] = {}
        for name in names:
            value = getattr(gs, name, None)
            if value not in (None, False, "", [], {}):
                out[name] = value
        for name, value in dict(state or {}).items():
            low = str(name).lower()
            if not any(token in low for token in ("notice", "popup", "modal", "show_yell", "confirm_open", "ack_pending")):
                continue
            if value not in (None, False, "", [], {}):
                out[f"state:{name}"] = value
        return out

    @staticmethod
    def _parse_attempt_result_value(value: Any) -> Optional[bool]:
        if value is None or value == "":
            return None
        if isinstance(value, bool):
            return bool(value)
        if isinstance(value, dict):
            for key in ("success", "succeeded", "ok", "result", "status", "value"):
                if key in value:
                    parsed = LegacyUIAdapter._parse_attempt_result_value(value.get(key))
                    if parsed is not None:
                        return parsed
            return None
        text = str(value).strip().lower().replace("_", " ").replace("-", " ")
        if not text:
            return None
        failure_tokens = (
            "failure", "failed", "fail", "not success", "unsuccessful",
            "失敗", "未達成", "条件未達成", "不成功",
        )
        success_tokens = ("success", "succeeded", "successful", "成功", "達成")
        if any(token in text for token in failure_tokens):
            return False
        if any(token in text for token in success_tokens):
            return True
        return None

    def _read_explicit_attempt_result(self, rt: PlayerViewRuntime) -> Tuple[Optional[bool], str]:
        gs = rt.app.gs
        try:
            raw_state = rt.app.state_json()
        except Exception:
            raw_state = {}
        state = raw_state if isinstance(raw_state, dict) else {}
        for container, prefix in ((gs, "gs"), (state, "state")):
            for name in self._ATTEMPT_RESULT_ATTRS:
                value = container.get(name) if isinstance(container, dict) else getattr(container, name, None)
                parsed = self._parse_attempt_result_value(value)
                if parsed is not None:
                    return parsed, f"{prefix}.{name}={value!r}"
            for name in self._ATTEMPT_SUCCESS_ATTRS:
                value = container.get(name) if isinstance(container, dict) else getattr(container, name, None)
                if value not in (None, ""):
                    parsed = self._parse_attempt_result_value(value)
                    if parsed is None and isinstance(value, (int, float)):
                        parsed = bool(value)
                    if parsed is not None:
                        return parsed, f"{prefix}.{name}={value!r}"
            for name in self._ATTEMPT_FAILURE_ATTRS:
                value = container.get(name) if isinstance(container, dict) else getattr(container, name, None)
                if value not in (None, "", False, 0):
                    return False, f"{prefix}.{name}={value!r}"
        return None, ""

    def _clear_legacy_attempt_result_state(self, rt: PlayerViewRuntime) -> None:
        """Start a fresh attempt epoch before any LIVE_CONFIRM/LIVE_PERF work.

        Legacy App generations keep last-attempt fields after a turn.  Those
        values describe the previous live and must never be consumed as the
        result of the newly set live.  Clear both GameState and App mirrors
        before entering performance, then snapshot the new explicit result only
        after LIVE_ATTEMPT has actually run.
        """
        targets = (rt.app.gs, rt.app)
        for target in targets:
            for name in self._ATTEMPT_RESULT_ATTRS:
                if hasattr(target, name):
                    try:
                        setattr(target, name, "")
                    except Exception:
                        pass
            for name in self._ATTEMPT_SUCCESS_ATTRS:
                if hasattr(target, name):
                    try:
                        setattr(target, name, None)
                    except Exception:
                        pass
            for name in self._ATTEMPT_FAILURE_ATTRS:
                if hasattr(target, name):
                    try:
                        setattr(target, name, False)
                    except Exception:
                        pass

        # Per-attempt score products are equally stale across turns.  They are
        # rebuilt by the legacy engine during this performance/success timing.
        for target in targets:
            for name in (
                "last_attempt_total_score", "last_attempt_score_total",
                "last_attempt_scores", "last_attempt_score_set",
                "last_attempt_score_add", "last_attempt_score_add_by_card",
                "last_attempt_score_bonus_by_card", "last_attempt_score_bonus",
                "last_attempt_score_delta",
            ):
                if hasattr(target, name):
                    try:
                        setattr(target, name, None)
                    except Exception:
                        pass

    @staticmethod
    def _attempt_result_can_be_new(before_phase: Any, after_phase: Any) -> bool:
        """True only after the current performance has reached its attempt."""
        before = str(before_phase or "").strip().upper()
        after = str(after_phase or "").strip().upper()
        return before == "LIVE_ATTEMPT" or after in {
            "LIVE_RESOLVE", "MAIN", "ACTIVE", "ENERGY", "DRAW"
        }

    def _apply_explicit_attempt_result(self, rt: PlayerViewRuntime, *, context: str) -> Optional[bool]:
        result, source = self._read_explicit_attempt_result(rt)
        if result is None:
            return None
        current = getattr(rt.app, "_dual_live_attempt_succeeded", None)
        if current is None or bool(current) != bool(result):
            self._record_live_attempt_outcome(rt, bool(result), source=f"{context}:{source}")
        if result is False:
            # Rule 8.3.16 is owned by the dual controller once the legacy result
            # is known.  Some runtime builds leave the cards in set_zone until
            # their one-player LIVE_RESOLVE tail; move them now so they cannot
            # be scored or selected as successful.
            gs = rt.app.gs
            failed_cards = list(getattr(gs, "set_zone", []) or [])
            if failed_cards:
                gs.green_room = list(getattr(gs, "green_room", []) or []) + failed_cards
                gs.set_zone = []
                self.engine.state.log.append(
                    f"[RULE 8.3.16][P{rt.player_id + 1}] moved {len(failed_cards)} failed live card(s) to waiting room"
                )
            gs.pending = [
                item for item in list(getattr(gs, "pending", []) or [])
                if not self._is_single_player_success_placement_pending(item)
                and not self._is_live_success_effect_pending(item)
            ]
            setattr(rt.app, "_dual_deferred_success_pending", [])
        return bool(result)

    @staticmethod
    def _is_yell_notice_key(name: Any) -> bool:
        low = str(name or "").strip().lower()
        if "yell" not in low and "エール" not in low:
            return False
        if "acknowledged" in low or "確認済" in low or "確認ずみ" in low:
            return False
        # Do not classify gameplay data such as ``yell_revealed_cards`` as a
        # popup.  Only presentation/control names are scrubbed; the revealed
        # card list and canonical acknowledgement marker must remain available
        # to live-success effects and the legacy fallback popup.
        return any(token in low for token in (
            "notice", "popup", "modal", "confirm", "ack", "open", "pending",
            "show", "確認",
        ))

    @classmethod
    def _is_yell_confirmation_pending(cls, item: Any) -> bool:
        text = cls._pending_text(item).lower()
        has_yell = "yell" in text or "エール" in text
        has_confirm = any(token in text for token in (
            "reveal", "公開", "confirm", "確認", "notice", "popup", "表示",
        ))
        return has_yell and has_confirm and not cls._is_live_success_effect_pending(item)

    def _sanitize_acknowledged_yell_state(self, rt: PlayerViewRuntime, state: Dict[str, Any]) -> Dict[str, Any]:
        if not bool(getattr(rt.app, "_dual_yell_notice_acknowledged", False)):
            return state
        out = copy.deepcopy(state)
        def scrub(obj: Any) -> None:
            if isinstance(obj, dict):
                # Some view generations expose a generic modal object such as
                # {title: "エール内容確認", open: true}.  Its key does not
                # contain "yell", so clear the presentation controls based on
                # the object's own title/message while preserving gameplay data.
                presentation_text = " ".join(
                    str(obj.get(name, "") or "")
                    for name in ("title", "message", "body", "text", "label", "notice")
                )
                if self._is_yell_confirmation_pending(presentation_text):
                    for name in ("open", "visible", "show", "active", "pending", "is_open", "isOpen"):
                        if name in obj:
                            obj[name] = False
                    for name in ("title", "message", "body", "text", "label", "notice"):
                        if name in obj and isinstance(obj.get(name), str):
                            obj[name] = ""
                for key in list(obj.keys()):
                    value = obj.get(key)
                    if self._is_yell_notice_key(key):
                        if isinstance(value, bool):
                            obj[key] = False
                        elif isinstance(value, (str, int, float)):
                            obj[key] = False
                        elif isinstance(value, list) and any(
                            self._is_yell_confirmation_pending(x) for x in value
                        ):
                            obj[key] = [x for x in value if not self._is_yell_confirmation_pending(x)]
                        elif isinstance(value, dict) and self._is_yell_confirmation_pending(value):
                            obj[key] = {}
                    elif isinstance(value, list):
                        obj[key] = [
                            x for x in value
                            if not self._is_yell_confirmation_pending(x)
                        ]
                        for child in obj[key]:
                            scrub(child)
                    elif isinstance(value, dict):
                        if self._is_yell_confirmation_pending(value):
                            obj[key] = {}
                        else:
                            scrub(value)
            elif isinstance(obj, list):
                for value in obj:
                    scrub(value)
        scrub(out)
        if isinstance(out.get("pending"), list):
            out["pending"] = [
                item for item in out["pending"]
                if not self._is_yell_confirmation_pending(item)
            ]
        out["dual_yell_notice_acknowledged"] = True
        out["dual_force_close_yell_notice"] = True
        return out

    def _active_yell_notice_names(self, rt: PlayerViewRuntime) -> List[str]:
        gs = rt.app.gs
        names = [
            name for name in self._YELL_NOTICE_ATTRS
            if getattr(gs, name, None) not in (None, False, "", [], {})
        ]
        try:
            state = rt.app.state_json()
        except Exception:
            state = {}
        if isinstance(state, dict):
            names.extend(
                f"state:{name}" for name, value in state.items()
                if self._is_yell_notice_key(name)
                and value not in (None, False, "", [], {})
            )
        return sorted(set(names))

    def _suppress_reopened_yell_notice(self, rt: PlayerViewRuntime) -> None:
        """Remove presentation-only YELL confirmations after acknowledgement.

        Legacy generations keep popup flags on either ``GameState`` or ``App``
        and some state_json implementations derive the popup from an App-side
        mirror.  Clearing only ``gs`` therefore lets the same confirmation
        reappear after a success effect.  Scrub both containers and always
        sanitize the response sent back to the embedded board.
        """
        if not bool(getattr(rt.app, "_dual_yell_notice_acknowledged", False)):
            return
        gs = rt.app.gs
        for target in (gs, rt.app):
            names = set(self._YELL_NOTICE_ATTRS)
            try:
                names.update(
                    name for name in vars(target)
                    if not str(name).startswith("_dual_")
                    and self._is_yell_notice_key(name)
                )
            except Exception:
                pass
            for name in names:
                if str(name).startswith("_dual_"):
                    continue
                if hasattr(target, name):
                    try:
                        setattr(target, name, False)
                    except Exception:
                        pass
            if hasattr(target, "pending"):
                try:
                    target.pending = [
                        item for item in list(getattr(target, "pending", []) or [])
                        if not self._is_yell_confirmation_pending(item)
                    ]
                except Exception:
                    pass
        gs.pending = [
            item for item in list(getattr(gs, "pending", []) or [])
            if not self._is_yell_confirmation_pending(item)
        ]

    def _acknowledge_yell_notice(self, rt: PlayerViewRuntime, *, source: str) -> None:
        """Persist a YELL acknowledgement for the current performance epoch."""
        already = bool(getattr(rt.app, "_dual_yell_notice_acknowledged", False))
        setattr(rt.app, "_dual_yell_notice_acknowledged", True)
        try:
            rt.app.gs.yell_reveal_acknowledged_this_live = True
        except Exception:
            pass
        self._suppress_reopened_yell_notice(rt)
        if not already:
            self.engine.state.log.append(
                f"[YELL ACK][P{rt.player_id + 1}] source={source}"
            )

    def _legacy_dialog_signature(self, rt: PlayerViewRuntime) -> str:
        gs = rt.app.gs
        try:
            state = rt.app.state_json()
        except Exception:
            state = {}
        payload = {
            "phase": str(getattr(gs, "phase", "") or ""),
            "pending": list(getattr(gs, "pending", []) or []),
            "flags": self._notice_flags(gs, state if isinstance(state, dict) else {}),
            "hand": list(getattr(gs, "hand", []) or []),
            "deck_n": len(list(getattr(gs, "deck", []) or [])),
            "set": list(getattr(gs, "set_zone", []) or []),
            "success": list(getattr(gs, "success_zone", []) or []),
            "resolve": list(getattr(gs, "resolve_zone", []) or []),
            "green_n": len(list(getattr(gs, "green_room", []) or [])),
        }
        return self._pending_text(payload)

    def _has_legacy_dialog(self, rt: PlayerViewRuntime) -> bool:
        self._suppress_reopened_yell_notice(rt)
        gs = rt.app.gs
        if list(getattr(gs, "pending", []) or []):
            return True
        try:
            state = rt.app.state_json()
        except Exception:
            state = {}
        return bool(self._notice_flags(gs, state if isinstance(state, dict) else {}))

    @staticmethod
    def _single_auto_order_choice(rt: PlayerViewRuntime) -> str:
        pending = list(getattr(rt.app.gs, "pending", []) or [])
        if len(pending) != 1 or not isinstance(pending[0], dict):
            return ""
        item = pending[0]
        if str(item.get("kind", "") or "") != "auto_order":
            return ""
        queue = list(item.get("queue", []) or [])
        options = [str(x or "").strip() for x in list(item.get("options", []) or []) if str(x or "").strip()]
        if len(queue) != 1 or len(options) != 1:
            return ""
        label = str((queue[0] or {}).get("label", "") or "").strip()
        return label or options[0]

    def _advance_active_legacy_dialog(self) -> bool:
        """Route the central NEXT to the active legacy confirmation first.

        Confirmation-only popups (YELL reveal, refresh notice, automatic-effect
        acknowledgement) have always supported NEXT as their OK/skip action.
        Mandatory choices remain open when the legacy runtime refuses an empty
        NEXT, and the central phase is never advanced in the same click.
        """
        rt = self._active_runtime()
        if not self._has_legacy_dialog(rt):
            return False
        before = self._legacy_dialog_signature(rt)
        acknowledged_yell_names = self._active_yell_notice_names(rt)
        boundary_before = self._capture_live_boundary(rt)
        setattr(rt.app, "_dual_last_boundary_snapshot", copy.deepcopy(boundary_before))
        before_phase = str(boundary_before.get("phase", "") or "")
        auto_order_choice = self._single_auto_order_choice(rt)
        if auto_order_choice:
            rt.app.cmd("resolve_pending", {"idx": 0, "choice": auto_order_choice})
            self.engine.state.log.append(
                f"[NEXT AUTO_ORDER][P{rt.player_id + 1}] {auto_order_choice}"
            )
        else:
            rt.app.cmd("next", {})
        if acknowledged_yell_names:
            self._acknowledge_yell_notice(rt, source="central-next")
        after_phase = str(getattr(rt.app.gs, "phase", "") or "")
        if self._attempt_result_can_be_new(before_phase, after_phase):
            self._apply_explicit_attempt_result(rt, context="dialog-next")
        self._suppress_reopened_yell_notice(rt)
        self._guard_after_legacy_command(rt, boundary_before)
        self._suppress_reopened_yell_notice(rt)
        self._sync_view_to_core(rt)
        self._sync_metadata_to_views()
        after = self._legacy_dialog_signature(rt)
        if after == before:
            raise ValueError("このポップアップは盤面上で対象・選択肢を指定して解決してください")
        self.engine.state.log.append(f"[NEXT ACK][P{rt.player_id + 1}] 確認・pendingを1段進めた")
        return True

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return int(default)

    @staticmethod
    def _record_value(record: Any, *names: str) -> Any:
        for name in names:
            if isinstance(record, dict) and name in record:
                value = record.get(name)
            else:
                value = getattr(record, name, None)
            if value not in (None, ""):
                return value
        return None

    def _card_record(self, rt: PlayerViewRuntime, cardnumber: str) -> Any:
        cn = str(cardnumber or "")
        db = rt.app.cards_db
        if isinstance(db, dict):
            if cn in db:
                return db[cn]
            cards = db.get("cards")
            if isinstance(cards, dict) and cn in cards:
                return cards[cn]
            if isinstance(cards, list):
                for item in cards:
                    if str(self._record_value(item, "cardnumber", "cn", "id") or "") == cn:
                        return item
        try:
            from llocg_ui.db import _get_card as db_get_card
            return db_get_card(db, cn)
        except Exception:
            return None

    @classmethod
    def _card_text_value(cls, value: Any) -> str:
        """Normalize tokv1/compiled card text into a readable detail string."""
        if value in (None, ""):
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, (list, tuple)):
            parts = [cls._card_text_value(item) for item in value]
            return "\n".join(part for part in parts if part)
        if isinstance(value, dict):
            if isinstance(value.get("abilities"), list):
                ability_parts: List[str] = []
                for ability in value.get("abilities", []):
                    if not isinstance(ability, dict):
                        text = cls._card_text_value(ability)
                        if text:
                            ability_parts.append(text)
                        continue
                    headers: List[str] = []
                    for header_key in ("ability_type", "trigger"):
                        header = str(ability.get(header_key, "") or "").strip()
                        if header and header not in {"BODY", "-"} and header not in headers:
                            headers.append(header)
                    body = cls._card_text_value(
                        ability.get("raw_text") or ability.get("raw") or ability.get("text") or ability.get("clauses")
                    )
                    prefix = "".join(f"<{header}>" for header in headers)
                    text = "\n".join(x for x in (prefix, body) if x)
                    if text:
                        ability_parts.append(text)
                if ability_parts:
                    return "\n".join(ability_parts)
            if isinstance(value.get("clauses"), list):
                clause_parts: List[str] = []
                for clause in value.get("clauses", []):
                    if isinstance(clause, dict):
                        raw = cls._card_text_value(clause.get("raw") or clause.get("raw_text") or clause.get("text"))
                        if not raw:
                            cost = cls._card_text_value(clause.get("cost_template"))
                            effect = cls._card_text_value(clause.get("effect_template"))
                            raw = "：".join(x for x in (cost, effect) if x)
                        if raw:
                            clause_parts.append(raw)
                    else:
                        text = cls._card_text_value(clause)
                        if text:
                            clause_parts.append(text)
                if clause_parts:
                    return "\n".join(clause_parts)
            preferred = (
                "effect_text_raw", "effect_text_norm", "effect_text",
                "card_text_raw", "card_text", "ability_text_raw",
                "ability_text", "raw_text", "raw", "source_text", "text",
                "effect_template", "description", "effect", "ability",
                "abilities", "clauses",
            )
            parts: List[str] = []
            for key in preferred:
                if key not in value:
                    continue
                text = cls._card_text_value(value.get(key))
                if text and text not in parts:
                    parts.append(text)
            return "\n".join(parts)
        return str(value).strip()

    @staticmethod
    def _json_card_rows(data: Any) -> List[Dict[str, Any]]:
        if isinstance(data, list):
            return [dict(row) for row in data if isinstance(row, dict)]
        if isinstance(data, dict) and isinstance(data.get("cards"), list):
            return [dict(row) for row in data.get("cards", []) if isinstance(row, dict)]
        if isinstance(data, dict):
            rows: List[Dict[str, Any]] = []
            for key, value in data.items():
                if not isinstance(value, dict):
                    continue
                row = dict(value)
                row.setdefault("cardnumber", key)
                rows.append(row)
            return rows
        return []

    def _canonical_detail_records(self, rt: PlayerViewRuntime) -> Dict[str, Any]:
        if self._detail_db_cache is not None:
            return self._detail_db_cache
        roots: List[Path] = []
        for raw_root in (
            getattr(rt.app, "root", None),
            getattr(rt.app, "outdir", None),
            Path.cwd(),
        ):
            try:
                root = Path(raw_root)
            except Exception:
                continue
            if root not in roots:
                roots.append(root)
        candidates: List[Path] = []
        for root in roots:
            candidates.extend([
                root / "llocg_db_out_full" / "cards_min_tokv1.json",
                root / "cards_min_tokv1.json",
                root / "llocg_db_out_full" / "cards_min_tokv1.csv",
                root / "cards_min_tokv1.csv",
                root / "llocg_db_out_full" / "cards_compiled_v7h.json",
                root / "cards_compiled_v7h.json",
            ])
        records: Dict[str, Any] = {}
        seen: set[str] = set()
        for path in candidates:
            key = str(path)
            if key in seen or not path.is_file():
                continue
            seen.add(key)
            try:
                if path.suffix.lower() == ".csv":
                    with path.open("r", encoding="utf-8-sig", newline="") as fh:
                        rows = [dict(row) for row in csv.DictReader(fh)]
                else:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    rows = self._json_card_rows(data)
            except Exception:
                continue
            for row in rows:
                cn = str(self._record_value(row, "cardnumber", "cn", "id") or "").strip()
                if not cn:
                    continue
                previous = records.get(cn)
                if previous is None or (not self._card_text_value(previous) and self._card_text_value(row)):
                    records[cn] = row
        self._detail_db_cache = records
        return records

    def _detail_card_record(self, rt: PlayerViewRuntime, cardnumber: str) -> Any:
        cn = str(cardnumber or "").strip()
        canonical = self._canonical_detail_records(rt).get(cn)
        runtime = self._card_record(rt, cn)
        if canonical is None:
            return runtime
        if runtime is None or not isinstance(runtime, dict):
            return canonical
        merged = dict(runtime)
        merged.update(dict(canonical))
        return merged

    def card_info_payload(self, key: str, cardnumber: str) -> Optional[Dict[str, str]]:
        """Return card detail data from the canonical DB record.

        ``llocg_ui.db._get_card`` intentionally exposes only runtime fields in
        some generations, so reading ``effect_text_*`` from that object makes
        every card appear to have no effect.  Prefer the raw/compiled DB record
        and accept the field aliases used by both tokv1 and compiled v7h.
        """
        rt = self.runtime(key)
        cn = str(cardnumber or "").strip()
        if not cn:
            return None
        record = self._detail_card_record(rt, cn)
        if record is None:
            return None

        def pick(*names: str) -> Any:
            return self._record_value(record, *names)

        effect_value = pick(
            "effect_text_raw", "effect_text_norm", "effect_text",
            "card_text_raw", "card_text", "ability_text_raw", "ability_text",
            "raw_text", "raw", "source_text", "text", "effect", "ability", "abilities",
            "clauses", "effects",
        )
        effect = self._card_text_value(effect_value)
        abilities = [part for part in effect.split("\n\n") if part.strip()]
        if not abilities and effect:
            abilities = [effect]
        return {
            "cn": cn,
            "name": str(pick("cardname", "name", "card_name") or ""),
            "type": str(pick("card_type_norm", "card_type", "type") or ""),
            "group": str(pick("group", "group_name") or ""),
            "cost": str(pick("cost", "cost_value") or ""),
            "blade": str(pick("blade", "blade_n", "blade_count") or ""),
            "effect": effect,
            "effect_text_raw": str(pick("effect_text_raw") or effect),
            "effect_text_norm": str(pick("effect_text_norm") or effect),
            "abilities": abilities,
        }

    def _cpu_deck_rows(self, key: str) -> List[Dict[str, str]]:
        deck_key = "deck2" if str(key).lower() == "p2" else "deck1"
        raw_path = str((self.reset_config or {}).get(deck_key, "") or "")
        candidates: List[Path] = []
        if raw_path:
            p = Path(raw_path)
            if p.is_absolute():
                candidates.append(p)
            for root_key in ("data_root", "project_root"):
                root = (self.reset_config or {}).get(root_key)
                if root:
                    root_path = Path(root)
                    candidates.append(root_path / raw_path)
                    candidates.append(root_path / "decklists" / f"{raw_path}.tsv")
                    candidates.append(root_path / "decklists" / f"deck_{raw_path}.tsv")
                    candidates.append(root_path / "sim_decks" / f"deck_{raw_path}.tsv")
            candidates.append(Path.cwd() / raw_path)
        for path in candidates:
            if not path.is_file():
                continue
            try:
                with path.open("r", encoding="utf-8-sig", newline="") as fh:
                    reader = csv.DictReader(fh, delimiter="\t")
                    rows = [dict(row) for row in reader if isinstance(row, dict)]
            except Exception:
                continue
            out: List[Dict[str, str]] = []
            for row in rows:
                card_no = str(row.get("card_no") or row.get("cardnumber") or row.get("cn") or "").strip()
                if not card_no:
                    continue
                count = str(row.get("count") or "0").strip()
                out.append({
                    "count": count,
                    "card_no": card_no,
                    "rarity": str(row.get("rarity") or ""),
                    "name": str(row.get("name") or row.get("cardname") or ""),
                    "variant_id": str(row.get("variant_id") or ""),
                })
            if out:
                return out
        return []

    def _cpu_card_lookup(self, rt: PlayerViewRuntime):
        def lookup(cardnumber: str) -> Dict[str, Any]:
            cn = str(cardnumber or "").strip()
            record = self._detail_card_record(rt, cn)

            def pick(*names: str) -> Any:
                return self._record_value(record, *names)

            effect_value = pick(
                "effect_text_raw", "effect_text_norm", "effect_text",
                "card_text_raw", "card_text", "ability_text_raw", "ability_text",
                "raw_text", "raw", "source_text", "text", "effect", "ability",
                "abilities", "clauses", "effects",
            )
            effect = self._card_text_value(effect_value)
            return {
                "cardnumber": cn,
                "card_no": cn,
                "cardname": str(pick("cardname", "name", "card_name") or cn),
                "name": str(pick("cardname", "name", "card_name") or cn),
                "card_type_norm": str(pick("card_type_norm", "card_type", "type") or ""),
                "type": str(pick("card_type_norm", "card_type", "type") or ""),
                "cost": pick("cost", "cost_value"),
                "score": pick("score", "score_value"),
                "effect_text_norm": effect,
                "effect_text": effect,
                "group": str(pick("group", "group_name") or ""),
                "unit": str(pick("unit", "unit_name") or ""),
            }

        return lookup

    def cpu_action_suggestion(self, max_turns: int = 4) -> Dict[str, Any]:
        with self.lock:
            self._sync_metadata_to_views()
            state = self.state()
            if state.get("phase") == "GAME_OVER":
                return {
                    "ok": True,
                    "active_player_key": state.get("active_player_key"),
                    "suggestion": {
                        "kind": "none",
                        "command": "",
                        "payload": {},
                        "reason": "対戦は終了しています",
                    },
                }
            key = "p1" if self.engine.active_player_id() == 0 else "p2"
            rt = self.runtime(key)
            player_state = self.player_state(key, "private")
            rows = self._cpu_deck_rows(key)
            if not rows:
                raise ValueError("CPU判断用のデッキ内容を読み込めませんでした")
            suggestion = suggest_autoplay_action(
                rows,
                self._cpu_card_lookup(rt),
                player_state,
                max_turns=max(1, int(max_turns or 4)),
            )
            suggestion["active_player_key"] = key
            suggestion["match_phase"] = state.get("phase")
            return {"ok": True, "active_player_key": key, "suggestion": suggestion}

    def apply_cpu_action_suggestion(self, max_turns: int = 4) -> Dict[str, Any]:
        with self.lock:
            suggestion_payload = self.cpu_action_suggestion(max_turns=max_turns)
            suggestion = dict(suggestion_payload.get("suggestion") or {})
            key = str(suggestion_payload.get("active_player_key") or "")
            command = str(suggestion.get("command") or "").strip()
            payload = suggestion.get("payload") if isinstance(suggestion.get("payload"), dict) else {}
            if not command:
                return {"ok": True, "suggestion": suggestion, "state": self.state(), "applied": False}
            if command.upper() == "NEXT":
                state = self.state()
                action_payload = dict(payload)
                action_payload.setdefault("expected_phase", state.get("phase"))
                action_payload.setdefault("expected_active_player_key", key)
                out = self.action("NEXT", action_payload)
                out["suggestion"] = suggestion
                out["applied"] = True
                return out
            rt = self.runtime(key)
            out = self.player_command(rt.key, command, payload)
            return {
                "ok": True,
                "suggestion": suggestion,
                "state": self.state(),
                "player_state": out,
                "applied": True,
            }

    def _card_effect_map(self, rt: PlayerViewRuntime) -> Dict[str, str]:
        """Return canonical effect text keyed by card number for the client UI."""
        cardnumbers: set[str] = set()
        gs = rt.app.gs
        for name in ("deck", "hand", "set_zone", "success_zone", "resolve_zone", "green_room"):
            for value in list(getattr(gs, name, []) or []):
                cn = self._slot_cardnumber(value)
                if cn:
                    cardnumbers.add(cn)
        for value in dict(getattr(gs, "stage", {}) or {}).values():
            cn = self._slot_cardnumber(value)
            if cn:
                cardnumbers.add(cn)
        db = getattr(rt.app, "cards_db", None)
        if isinstance(db, dict):
            cards = db.get("cards")
            if isinstance(cards, dict):
                cardnumbers.update(str(k) for k in cards.keys())
            else:
                cardnumbers.update(
                    str(k) for k, v in db.items()
                    if isinstance(v, dict) and k not in {"cards", "meta"}
                )
        out: Dict[str, str] = {}
        for cn in sorted(cardnumbers):
            payload = self.card_info_payload(rt.key, cn)
            if not payload:
                continue
            effect = str(payload.get("effect") or payload.get("effect_text_raw") or "").strip()
            if effect:
                out[cn] = effect
        return out

    def _decorate_player_state(self, rt: PlayerViewRuntime, state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply dual-only metadata after legacy public/private filtering."""
        out = self._sanitize_acknowledged_yell_state(
            rt, state if isinstance(state, dict) else {}
        )
        acknowledged = bool(getattr(rt.app, "_dual_yell_notice_acknowledged", False))
        out["dual_yell_notice_acknowledged"] = acknowledged
        out["dual_force_close_yell_notice"] = acknowledged
        out["dual_player_id"] = rt.key
        out["dual_active_player_id"] = "p1" if self.engine.active_player_id() == 0 else "p2"
        out["dual_card_effects"] = self._card_effect_map(rt)
        return out

    def _card_base_score(self, rt: PlayerViewRuntime, cardnumber: str) -> int:
        record = self._card_record(rt, cardnumber)
        return max(0, self._safe_int(self._record_value(record, "score", "base_score", "score_value"), 0))

    def _score_icon_count(self, rt: PlayerViewRuntime, cardnumber: str) -> int:
        record = self._card_record(rt, cardnumber)
        direct = self._record_value(
            record, "blade_heart_score_n", "score_icon_n", "blade_heart_score", "tok_score_delta_icon"
        )
        if direct not in (None, ""):
            return max(0, self._safe_int(direct, 0))
        raw = self._record_value(record, "blade_heart_special_counts_json", "blade_heart_special_counts")
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                raw = {}
        if isinstance(raw, dict):
            return max(0, self._safe_int(raw.get("score", 0), 0))
        return 0

    @staticmethod
    def _numeric_candidate(container: Any, names: Tuple[str, ...]) -> Optional[int]:
        for name in names:
            value = container.get(name) if isinstance(container, dict) else getattr(container, name, None)
            if isinstance(value, bool) or value in (None, ""):
                continue
            try:
                return int(float(value))
            except (TypeError, ValueError):
                continue
        return None

    @staticmethod
    def _named_value(container: Any, names: Tuple[str, ...]) -> Tuple[Any, str]:
        for name in names:
            value = container.get(name) if isinstance(container, dict) else getattr(container, name, None)
            if value not in (None, "", [], {}):
                return value, name
        return None, ""

    def _per_live_numeric_values(
        self,
        raw: Any,
        live_cards: List[str],
        *,
        scalar_for_single: bool = True,
    ) -> Optional[List[int]]:
        """Normalize legacy per-live score state without assuming one exact shape.

        The one-player runtime has used cardnumber-keyed dictionaries, index-keyed
        dictionaries and lists across different score-effect generations.  Dual
        judgment accepts all of those shapes so direct score-set effects and
        per-card additions survive the adapter boundary.
        """
        if raw in (None, "", [], {}):
            return None
        if isinstance(raw, dict):
            out: List[int] = []
            found = False
            for idx, cn in enumerate(live_cards):
                value = None
                for key in (cn, idx, str(idx), f"live:{idx}", f"set:{idx}"):
                    if key in raw:
                        value = raw.get(key)
                        break
                if value not in (None, ""):
                    found = True
                out.append(self._safe_int(value, 0))
            return out if found else None
        if isinstance(raw, (list, tuple)):
            if not raw:
                return None
            return [self._safe_int(raw[idx], 0) if idx < len(raw) else 0 for idx in range(len(live_cards))]
        if scalar_for_single and len(live_cards) == 1:
            try:
                return [int(float(raw))]
            except (TypeError, ValueError):
                return None
        return None

    def _first_semantic_value(
        self,
        gs: Any,
        state: Dict[str, Any],
        names: Tuple[str, ...],
    ) -> Tuple[Any, str]:
        for container, prefix in ((gs, "gs"), (state, "state")):
            value, name = self._named_value(container, names)
            if name:
                return value, f"{prefix}.{name}"
        return None, ""

    def _calculate_live_score(self, rt: PlayerViewRuntime) -> Tuple[int, str]:
        gs = rt.app.gs
        attempt = getattr(rt.app, "_dual_live_attempt_succeeded", None)
        if attempt is False:
            return 0, "attempt-failed"
        if attempt is None:
            # The attempt result is snapshotted at the 8.3.15/8.3.16 boundary.
            # Re-reading mutable legacy fields here can import a previous turn.
            return 0, "attempt-unresolved"
        live_cards = list(getattr(gs, "set_zone", []) or [])
        if not live_cards:
            return 0, "no-live"
        try:
            state_raw = rt.app.state_json()
        except Exception:
            state_raw = {}
        state = state_raw if isinstance(state_raw, dict) else {}

        # Prefer an explicit runtime total.  This is the most reliable value when
        # the one-player engine has already folded continuous effects, temporary
        # score changes and direct score-set effects into its attempt result.
        total_names = (
            "last_attempt_total_score", "last_attempt_score_total", "live_total_score",
            "total_live_score", "live_score_total", "last_live_total_score",
        )
        for container, prefix in ((gs, "gs"), (state, "state")):
            value = self._numeric_candidate(container, total_names)
            if value is not None:
                return value, f"{prefix}.computed"

        # Some runtime generations expose the final score of each live card.
        for container, prefix in ((gs, "gs"), (state, "state")):
            scores = container.get("last_attempt_scores") if isinstance(container, dict) else getattr(container, "last_attempt_scores", None)
            normalized = self._per_live_numeric_values(scores, live_cards)
            if normalized is not None:
                return sum(normalized), f"{prefix}.last_attempt_scores"

        card_scores = [self._card_base_score(rt, cn) for cn in live_cards]
        source_parts = [f"base={sum(card_scores)}"]

        # Direct “this card's score becomes N” effects use score-set state in the
        # current engine family.  Apply it before additions and YELL score icons.
        raw_set, set_source = self._first_semantic_value(
            gs, state,
            ("last_attempt_score_set", "live_score_set", "score_set_by_live", "live_score_overrides"),
        )
        score_sets = self._per_live_numeric_values(raw_set, live_cards)
        if score_sets is not None:
            for idx, value in enumerate(score_sets):
                # A sparse dict normalizes missing entries to zero; only replace
                # cards actually present in the original mapping.
                replace = True
                if isinstance(raw_set, dict):
                    cn = live_cards[idx]
                    replace = any(key in raw_set for key in (cn, idx, str(idx), f"live:{idx}", f"set:{idx}"))
                if replace:
                    card_scores[idx] = int(value)
            source_parts.append(f"set={set_source}")

        raw_add, add_source = self._first_semantic_value(
            gs, state,
            (
                "last_attempt_score_add", "last_attempt_score_add_by_card",
                "last_attempt_score_bonus_by_card", "live_score_add_by_card",
                "score_add_by_live",
            ),
        )
        score_adds = self._per_live_numeric_values(raw_add, live_cards)
        if score_adds is not None:
            card_scores = [score + score_adds[idx] for idx, score in enumerate(card_scores)]
            source_parts.append(f"per_card_add={add_source}")

        # Rule 8.4.2: each score icon among YELL-revealed cards adds one to the
        # player's initial total score.
        score_icons = sum(
            self._score_icon_count(rt, cn)
            for cn in list(getattr(gs, "resolve_zone", []) or [])
        )

        # Scalar legacy aliases remain as a guarded fallback.  Mirrors exported
        # in both gs and state are counted once, while genuinely different bonus
        # values can still coexist.
        bonus_names = (
            "last_attempt_score_bonus", "last_attempt_score_delta", "live_score_bonus",
            "temp_live_score", "temp_score", "live_score_add", "total_score_bonus",
        )
        bonus = 0
        seen_values: List[int] = []
        for container in (gs, state):
            value = self._numeric_candidate(container, bonus_names)
            if value is not None and value not in seen_values:
                seen_values.append(value)
                bonus += value

        source_parts.extend((f"cards={sum(card_scores)}", f"score_icons={score_icons}", f"scalar_bonus={bonus}"))
        return sum(card_scores) + score_icons + bonus, "fallback(" + ",".join(source_parts) + ")"

    def _set_opponent_score_contexts(self, scores: List[int]) -> None:
        for rt in self.players.values():
            own = int(scores[rt.player_id])
            opp = int(scores[1 - rt.player_id])
            gs = rt.app.gs
            for name in (
                "opponent_score", "opponent_total_score", "opponent_live_score",
                "opponent_live_total_score", "last_opponent_score", "last_opponent_live_score",
            ):
                setattr(gs, name, opp)
            for name in ("own_live_score", "live_total_score_dual", "dual_live_score"):
                setattr(gs, name, own)
            setattr(gs, "opponent_has_live", bool(list(getattr(self.runtime("p2" if rt.key == "p1" else "p1").app.gs, "set_zone", []) or [])))

    def _capture_opponent_wait_request(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        try:
            idx = int((payload or {}).get("idx", -1))
        except Exception:
            return None
        pend = list(getattr(rt.app.gs, "pending", []) or [])
        if idx < 0 or idx >= len(pend):
            return None
        item = pend[idx]
        if not isinstance(item, dict) or str(item.get("kind", "") or "") != "opponent_wait_notify":
            return None
        try:
            count = int(str((payload or {}).get("choice", "0") or "0").strip())
        except Exception:
            return None
        max_delta = max(0, min(3, int(item.get("max_delta", 3) or 3)))
        if count < 0 or count > max_delta:
            return None
        return {
            "count": count,
            "source_cn": str(item.get("source_cn", "") or ""),
            "effect_text": str(item.get("effect_text", "") or item.get("text", "") or ""),
            "text": str(item.get("text", "") or ""),
            "max_delta": max_delta,
        }

    @staticmethod
    def _opponent_wait_condition_text(request: Dict[str, Any]) -> str:
        return (
            str((request or {}).get("effect_text", "") or "")
            + "\n"
            + str((request or {}).get("text", "") or "")
        )

    def _card_numeric_field(self, rt: PlayerViewRuntime, cardnumber: str, *names: str) -> int:
        payload = self.card_info_payload(rt.key, cardnumber) or {}
        for name in names:
            raw = payload.get(name)
            if raw in (None, ""):
                continue
            try:
                return int(float(str(raw).strip()))
            except Exception:
                continue
        return 0

    def _card_text_field(self, rt: PlayerViewRuntime, cardnumber: str, *names: str) -> str:
        payload = self.card_info_payload(rt.key, cardnumber) or {}
        for name in names:
            raw = payload.get(name)
            if raw not in (None, ""):
                return str(raw)
        return ""

    def _opponent_wait_candidates(self, other: PlayerViewRuntime, request: Dict[str, Any]) -> List[str]:
        body = self._opponent_wait_condition_text(request)
        active_positions: List[str] = []
        for pos in ("L", "C", "R"):
            slot = dict(getattr(other.app.gs, "stage", {}) or {}).get(pos)
            if slot is not None and bool(getattr(slot, "active", True)) and self._slot_cardnumber(slot):
                active_positions.append(pos)

        if "右サイド" in body or "左サイド" in body:
            active_positions = [pos for pos in active_positions if pos in {"L", "R"}]

        cost_le = None
        cost_ge = None
        m = re.search(r"コスト\s*(\d+)\s*以下", body)
        if m:
            cost_le = int(m.group(1))
        m = re.search(r"コスト\s*(\d+)\s*以上", body)
        if m:
            cost_ge = int(m.group(1))

        blade_le = None
        blade_eq = None
        m = re.search(r"元々持つ<\(ブレード\)>[^。\n]*ちょうど\s*(\d+)", body)
        if m:
            blade_eq = int(m.group(1))
        m = re.search(r"元々持つ<\(ブレード\)>[^。\n]*(\d+)\s*(?:つ|個)?以下", body)
        if m and blade_eq is None:
            blade_le = int(m.group(1))

        group_not = ""
        m = re.search(r"『([^』]+)』以外", body)
        if m:
            group_not = m.group(1)

        out: List[str] = []
        for pos in active_positions:
            slot = dict(getattr(other.app.gs, "stage", {}) or {}).get(pos)
            cn = self._slot_cardnumber(slot)
            if not cn:
                continue
            if cost_le is not None and self._card_numeric_field(other, cn, "cost") > cost_le:
                continue
            if cost_ge is not None and self._card_numeric_field(other, cn, "cost") < cost_ge:
                continue
            blade = self._card_numeric_field(other, cn, "blade")
            if blade_eq is not None and blade != blade_eq:
                continue
            if blade_le is not None and blade > blade_le:
                continue
            if group_not:
                group = self._card_text_field(other, cn, "group")
                if group == group_not:
                    continue
            out.append(pos)
        return out

    def _apply_opponent_wait_request(self, rt: PlayerViewRuntime, request: Optional[Dict[str, Any]]) -> None:
        if not request:
            return
        requested = max(0, min(3, int(request.get("count", 0) or 0)))
        if requested <= 0:
            return
        other = self.runtime("p2" if rt.key == "p1" else "p1")
        candidates = self._opponent_wait_candidates(other, request)
        pick_n = min(requested, len(candidates))
        picked = candidates[:pick_n]
        for pos in picked:
            slot = dict(getattr(other.app.gs, "stage", {}) or {}).get(pos)
            if slot is not None:
                setattr(slot, "active", False)
        src = str(request.get("source_cn", "") or "?")
        other.app.gs.log.append(
            f"[DUAL EFFECT][OPPONENT WAIT] {src}: {picked if picked else 'none'} -> WAIT "
            f"(requested={requested}, candidates={candidates})"
        )
        rt.app.gs.log.append(
            f"[DUAL EFFECT][OPPONENT WAIT] {src}: opponent {other.key} {picked if picked else 'none'} -> WAIT "
            f"(requested={requested}, applied={pick_n})"
        )
        self._sync_view_to_core(other)

    def _pending_item_for_command(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        pend = list(getattr(rt.app.gs, "pending", []) or [])
        if not pend:
            return None
        if str(cmd or "") == "next":
            item = pend[0]
            return item if isinstance(item, dict) else None
        if str(cmd or "") != "resolve_pending":
            return None
        try:
            idx = int((payload or {}).get("idx", -1))
        except Exception:
            return None
        if idx < 0 or idx >= len(pend):
            return None
        item = pend[idx]
        return item if isinstance(item, dict) else None

    @staticmethod
    def _payload_choice_text(payload: Dict[str, Any]) -> str:
        return str((payload or {}).get("choice", "") or "").strip().lower()

    @classmethod
    def _choice_applies_optional_effect(cls, payload: Dict[str, Any]) -> bool:
        return cls._payload_choice_text(payload) in {
            "apply", "yes", "y", "1", "true", "use", "do", "go", "ok",
            "confirm", "使う", "はい",
        }

    def _capture_opponent_energy_wait_request(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item or str(item.get("kind", "") or "") != "message_ack":
            return None
        body = (
            str(item.get("label", "") or "")
            + "\n"
            + str(item.get("text", "") or "")
            + "\n"
            + str(item.get("message", "") or "")
        )
        if "相手エネルギー確認" not in body:
            return None
        n = None
        patterns = (
            r"相手[もは、]*[^。\n]*エネルギー(?:カード)?を\s*(\d+)\s*枚ウェイト状態で置",
            r"相手[もは、]*[^。\n]*エネルギーデッキから[^。\n]*(\d+)\s*枚ウェイト状態で置",
        )
        for pat in patterns:
            m = re.search(pat, body)
            if m:
                n = int(m.group(1))
                break
        if n is None:
            return None
        return {
            "n": max(0, n),
            "source_cn": str(item.get("source_cn", "") or ""),
            "text": body,
        }

    def _capture_opponent_draw_request(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item or str(item.get("kind", "") or "") != "confirm_effect":
            return None
        if not self._choice_applies_optional_effect(payload):
            return None
        body = (
            str(item.get("text", "") or "")
            + "\n"
            + str(item.get("message", "") or "")
            + "\n"
            + str(item.get("effect_text", "") or "")
        )
        m = re.search(r"相手はカードを\s*(\d+)\s*枚引", body)
        if not m:
            return None
        return {
            "n": max(0, int(m.group(1))),
            "source_cn": str(item.get("source_cn", "") or ""),
            "text": body,
        }

    def _apply_opponent_energy_wait_request(
        self,
        rt: PlayerViewRuntime,
        request: Optional[Dict[str, Any]],
    ) -> None:
        if not request:
            return
        n = max(0, int(request.get("n", 0) or 0))
        if n <= 0:
            return
        other = self.runtime("p2" if rt.key == "p1" else "p1")
        gs = other.app.gs
        active = max(0, int(getattr(gs, "energy_active", 0) or 0))
        wait = max(0, int(getattr(gs, "energy_wait", 0) or 0))
        under = self._energy_under(gs)
        remaining = max(0, ENERGY_DECK_SIZE - active - wait - under)
        add = min(n, remaining)
        if add > 0:
            gs.energy_wait = wait + add
            gs.energy_total = ENERGY_DECK_SIZE
        src = str(request.get("source_cn", "") or "?")
        suffix = " (clipped)" if add < n else ""
        other.app.gs.log.append(
            f"[DUAL EFFECT][OPPONENT ENERGY WAIT] {src}: +{add}/{n}{suffix} "
            f"(active={active}, wait={int(getattr(gs, 'energy_wait', 0) or 0)}, under={under})"
        )
        rt.app.gs.log.append(
            f"[DUAL EFFECT][OPPONENT ENERGY WAIT] {src}: opponent {other.key} +{add}/{n}{suffix}"
        )
        self._sync_view_to_core(other)

    def _apply_opponent_draw_request(
        self,
        rt: PlayerViewRuntime,
        request: Optional[Dict[str, Any]],
    ) -> None:
        if not request:
            return
        n = max(0, int(request.get("n", 0) or 0))
        if n <= 0:
            return
        other = self.runtime("p2" if rt.key == "p1" else "p1")
        gs = other.app.gs
        hand_before = len(list(getattr(gs, "hand", []) or []))
        try:
            from llocg_ui.engine import draw as shared_draw
            draw_n = int(shared_draw(gs, n, getattr(other.app, "rng", None)) or 0)
        except Exception as exc:
            deck = list(getattr(gs, "deck", []) or [])
            draw_n = min(n, len(deck))
            drawn = deck[:draw_n]
            gs.hand = list(getattr(gs, "hand", []) or []) + drawn
            gs.deck = deck[draw_n:]
            gs.log.append(f"[WARN] shared opponent draw failed; fallback without refresh: {exc}")
        hand_after = len(list(getattr(gs, "hand", []) or []))
        src = str(request.get("source_cn", "") or "?")
        refreshed = bool(getattr(gs, "deck_refreshed_this_turn", False))
        suffix = " (refreshed)" if refreshed else ""
        other.app.gs.log.append(
            f"[DUAL EFFECT][OPPONENT DRAW] {src}: draw {draw_n}/{n}{suffix} "
            f"(hand {hand_before}->{hand_after})"
        )
        rt.app.gs.log.append(
            f"[DUAL EFFECT][OPPONENT DRAW] {src}: opponent {other.key} draw {draw_n}/{n}{suffix}"
        )
        self._sync_view_to_core(other)

    def _card_kind_matches(self, rt: PlayerViewRuntime, cardnumber: str, kind: str) -> bool:
        want = str(kind or "ANY").upper()
        if want in ("", "ANY", "CARD"):
            return True
        payload = self.card_info_payload(rt.key, cardnumber) or {}
        card_type = (
            str(payload.get("card_type", "") or "")
            + " "
            + str(payload.get("type", "") or "")
            + " "
            + str(payload.get("kind", "") or "")
        ).upper()
        if want == "LIVE":
            return "LIVE" in card_type or "ライブ" in card_type
        if want == "MEMBER":
            return "MEMBER" in card_type or "メンバー" in card_type
        return True

    def _green_candidates_for_runtime(self, rt: PlayerViewRuntime, kind: str) -> List[str]:
        out: List[str] = []
        for cn in list(getattr(rt.app.gs, "green_room", []) or []):
            cn_s = str(cn or "").strip()
            if cn_s and self._card_kind_matches(rt, cn_s, kind):
                out.append(cn_s)
        return out

    def _capture_choose_opponent_green_bottom_request(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item or str(item.get("kind", "") or "") != "choose_player_for_green_bottom":
            return None
        if self._payload_choice_text(payload) not in {"opponent", "opp", "other", "相手"}:
            return None
        return {
            "kind": str(item.get("want_kind", "ANY") or "ANY"),
            "n": max(0, int(item.get("remaining", 0) or 0)),
            "allow_less": bool(item.get("allow_less", False) or item.get("allow_skip", False)),
            "source_cn": str(item.get("source_cn", "") or ""),
        }

    def _capture_opponent_mass_green_bottom_request(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item or str(item.get("kind", "") or "") != "manual_opponent_mass_bottom_threshold":
            return None
        return {
            "kind": "MEMBER",
            "n": 999,
            "allow_less": True,
            "shuffle": True,
            "source_cn": str(item.get("source_cn", "") or ""),
        }

    def _apply_opponent_green_bottom_request(
        self,
        rt: PlayerViewRuntime,
        request: Optional[Dict[str, Any]],
    ) -> None:
        if not request:
            return
        other = self.runtime("p2" if rt.key == "p1" else "p1")
        kind = str(request.get("kind", "ANY") or "ANY").upper()
        n = max(0, int(request.get("n", 0) or 0))
        if n <= 0:
            return
        candidates = self._green_candidates_for_runtime(other, kind)
        if not request.get("allow_less") and len(candidates) < n:
            src0 = str(request.get("source_cn", "") or "?")
            other.app.gs.log.append(
                f"[DUAL EFFECT][OPPONENT GREEN BOTTOM][ERR] {src0}: not enough {kind} candidates "
                f"(need={n}, have={len(candidates)})"
            )
            rt.app.gs.log.append(
                f"[DUAL EFFECT][OPPONENT GREEN BOTTOM][ERR] {src0}: opponent {other.key} not enough candidates"
            )
            return
        moved = list(candidates[: min(n, len(candidates))])
        if request.get("shuffle"):
            try:
                other.app.rng.shuffle(moved)
            except Exception:
                pass
        remaining_green = list(getattr(other.app.gs, "green_room", []) or [])
        for cn in moved:
            try:
                remaining_green.remove(cn)
            except ValueError:
                pass
        other.app.gs.green_room = remaining_green
        other.app.gs.deck = list(getattr(other.app.gs, "deck", []) or []) + moved
        src = str(request.get("source_cn", "") or "?")
        other.app.gs.log.append(
            f"[DUAL EFFECT][OPPONENT GREEN BOTTOM] {src}: {kind} {len(moved)}/{n} -> deck bottom"
        )
        rt.app.gs.log.append(
            f"[DUAL EFFECT][OPPONENT GREEN BOTTOM] {src}: opponent {other.key} {kind} {len(moved)}/{n}"
        )
        self._sync_view_to_core(other)

    def _capture_choose_opponent_deck_top_request(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item or str(item.get("kind", "") or "") != "choose_player_for_deck_top_action":
            return None
        if self._payload_choice_text(payload) not in {"opponent", "opp", "other", "相手"}:
            return None
        return {
            "action": str(item.get("action", "") or ""),
            "k": max(1, int(item.get("k", 1) or 1)),
            "source_cn": str(item.get("source_cn", "") or ""),
        }

    def _refresh_opponent_for_top_access(self, other: PlayerViewRuntime, need: int, source: str) -> None:
        try:
            from llocg_ui.engine import _rule_refresh_for_top_access
            _rule_refresh_for_top_access(
                other.app.gs,
                getattr(other.app, "rng", None),
                max(1, int(need or 1)),
                reason=f"dual_opponent_deck_top:{source or '?'}",
            )
        except Exception as exc:
            other.app.gs.log.append(f"[WARN] shared opponent top-access refresh failed: {exc}")

    def _install_opponent_deck_top_pending(
        self,
        rt: PlayerViewRuntime,
        request: Optional[Dict[str, Any]],
    ) -> None:
        if not request:
            return
        other = self.runtime("p2" if rt.key == "p1" else "p1")
        action = str(request.get("action", "") or "")
        k = max(1, int(request.get("k", 1) or 1))
        src = str(request.get("source_cn", "") or "")
        self._refresh_opponent_for_top_access(other, k, src)
        deck = list(getattr(other.app.gs, "deck", []) or [])
        revealed = deck[: min(k, len(deck))]
        pending = list(getattr(rt.app.gs, "pending", []) or [])
        replacement: Optional[Dict[str, Any]] = None
        if action == "top1_optional_green":
            if revealed:
                replacement = {
                    "kind": "dual_opponent_top1_to_green_or_keep",
                    "text": "相手のデッキの一番上のカードを確認。控え室に置くか、デッキ上に残すか選んでください。",
                    "options": ["green", "keep"],
                    "top_cn": revealed[0],
                    "display_cards": list(revealed),
                    "source_cn": src,
                }
            else:
                replacement = {
                    "kind": "message_ack",
                    "label": "相手デッキ確認",
                    "text": "相手のデッキに確認できるカードがありません。",
                    "options": ["ok"],
                    "source_cn": src,
                }
        elif action == "topk_reorder_keep_any":
            replacement = {
                "kind": "dual_opponent_topk_reorder_keep_any",
                "text": f"相手のデッキ上から{len(revealed)}枚を確認。デッキ上に残すカードを上から順に選び、残りを控え室に置きます。",
                "options": list(revealed),
                "display_cards": list(revealed),
                "pool": list(revealed),
                "source_cn": src,
            }
        if replacement is None:
            return
        for i in range(len(pending) - 1, -1, -1):
            item = pending[i]
            if isinstance(item, dict) and str(item.get("kind", "") or "") == "manual_opponent_deck_top_action_notify":
                pending[i] = replacement
                rt.app.gs.pending = pending
                rt.app.gs.log.append(
                    f"[DUAL EFFECT][OPPONENT DECK TOP] {src or '?'}: prepared action={action} revealed={revealed}"
                )
                other.app.gs.log.append(
                    f"[DUAL EFFECT][OPPONENT DECK TOP] {src or '?'}: revealed top {len(revealed)}/{k}"
                )
                self._sync_view_to_core(other)
                return
        pending.append(replacement)
        rt.app.gs.pending = pending
        rt.app.gs.log.append(
            f"[DUAL EFFECT][OPPONENT DECK TOP] {src or '?'}: prepared action={action} revealed={revealed}"
        )
        other.app.gs.log.append(
            f"[DUAL EFFECT][OPPONENT DECK TOP] {src or '?'}: revealed top {len(revealed)}/{k}"
        )
        self._sync_view_to_core(other)

    def _handle_dual_opponent_deck_pending(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item:
            return None
        kind = str(item.get("kind", "") or "")
        if kind not in {"dual_opponent_top1_to_green_or_keep", "dual_opponent_topk_reorder_keep_any"}:
            return None
        other = self.runtime("p2" if rt.key == "p1" else "p1")
        self._push_history()
        try:
            idx = int((payload or {}).get("idx", -1))
            pending = list(getattr(rt.app.gs, "pending", []) or [])
            if idx < 0 or idx >= len(pending):
                return self._full_state_with_error(rt, "対象の確認項目が見つかりません")
            pending.pop(idx)
            rt.app.gs.pending = pending
            low = self._payload_choice_text(payload)
            src = str(item.get("source_cn", "") or "?")
            if kind == "dual_opponent_top1_to_green_or_keep":
                if not list(getattr(other.app.gs, "deck", []) or []):
                    other.app.gs.log.append(f"[DUAL EFFECT][OPPONENT DECK TOP][ERR] {src}: opponent deck empty")
                elif low in {"green", "waiting", "wait", "控え室"}:
                    moved = other.app.gs.deck.pop(0)
                    other.app.gs.green_room.append(moved)
                    other.app.gs.log.append(f"[DUAL EFFECT][OPPONENT DECK TOP] {src}: top {moved} -> waiting room")
                    rt.app.gs.log.append(f"[DUAL EFFECT][OPPONENT DECK TOP] {src}: opponent top -> waiting room")
                elif low in {"keep", "top", "deck", "残す", "デッキ上"}:
                    kept = other.app.gs.deck[0]
                    other.app.gs.log.append(f"[DUAL EFFECT][OPPONENT DECK TOP] {src}: top {kept} kept")
                    rt.app.gs.log.append(f"[DUAL EFFECT][OPPONENT DECK TOP] {src}: opponent top kept")
                else:
                    rt.app.gs.pending.insert(idx, item)
                    rt.app.gs.log.append(f"[ERR] dual_opponent_top1_to_green_or_keep: invalid choice {low}")
                    self._discard_failed_history()
                    return self._full_state_with_error(rt, "選択が不正です")
            else:
                pool = [str(x or "") for x in list(item.get("pool", []) or []) if str(x or "").strip()]
                raw_choice = (payload or {}).get("choice", "")
                if isinstance(raw_choice, list):
                    keep = [str(x or "").strip() for x in raw_choice if str(x or "").strip()]
                else:
                    keep = [x.strip() for x in re.split(r"[,\\s]+", str(raw_choice or "").strip()) if x.strip()]
                keep = [cn for cn in keep if cn in pool]
                seen: List[str] = []
                for cn in keep:
                    if cn not in seen:
                        seen.append(cn)
                keep = seen
                rest = [cn for cn in pool if cn not in keep]
                deck = list(getattr(other.app.gs, "deck", []) or [])
                other.app.gs.deck = keep + deck[len(pool):]
                other.app.gs.green_room = list(getattr(other.app.gs, "green_room", []) or []) + rest
                other.app.gs.log.append(
                    f"[DUAL EFFECT][OPPONENT DECK TOP] {src}: keep={keep}; rest_to_waiting={rest}"
                )
                rt.app.gs.log.append(
                    f"[DUAL EFFECT][OPPONENT DECK TOP] {src}: opponent keep={len(keep)} rest={len(rest)}"
                )
            self._sync_view_to_core(other)
            self._sync_metadata_to_views()
            raw = rt.app.state_json()
            out = self._decorate_player_state(rt, raw if isinstance(raw, dict) else {})
            out["dual_transaction_committed"] = True
            return out
        except Exception:
            self._discard_failed_history()
            raise

    def _opponent_hand_discard_pending(self, other: PlayerViewRuntime, *, n: int, kind: str = "ANY", source_cn: str = "") -> Dict[str, Any]:
        hand = [str(x or "") for x in list(getattr(other.app.gs, "hand", []) or []) if str(x or "").strip()]
        kind_u = str(kind or "ANY").upper()
        options = [cn for cn in hand if self._card_kind_matches(other, cn, kind_u)]
        return {
            "kind": "dual_opponent_discard_from_hand",
            "text": f"相手の手札から{kind_u if kind_u != 'ANY' else 'カード'}を{int(n or 0)}枚控え室に置きます。相手が置くカードを選んでください。",
            "options": list(options),
            "display_cards": list(options),
            "remaining": max(0, int(n or 0)),
            "want_kind": kind_u,
            "source_cn": str(source_cn or ""),
        }

    def _install_opponent_hand_discard_pending(
        self,
        rt: PlayerViewRuntime,
        *,
        n: int,
        kind: str = "ANY",
        source_cn: str = "",
    ) -> None:
        if int(n or 0) <= 0:
            return
        other = self.runtime("p2" if rt.key == "p1" else "p1")
        pending = list(getattr(rt.app.gs, "pending", []) or [])
        pending.append(self._opponent_hand_discard_pending(other, n=n, kind=kind, source_cn=source_cn))
        rt.app.gs.pending = pending
        rt.app.gs.log.append(
            f"[DUAL EFFECT][OPPONENT HAND DISCARD] {source_cn or '?'}: choose opponent {other.key} {kind} x{int(n or 0)}"
        )

    def _capture_opponent_hand_discard_request(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item:
            return None
        kind = str(item.get("kind", "") or "")
        low = self._payload_choice_text(payload)
        if kind == "opponent_optional_discard_hand_else_self_gain_icons":
            if low in {"opponent_discard", "discard", "yes", "y", "1", "true", "捨てる", "置く", "はい"}:
                return {
                    "n": max(0, int(item.get("discard_n", 1) or 1)),
                    "kind": "ANY",
                    "source_cn": str(item.get("source_cn", "") or ""),
                }
        if kind == "confirm_effect":
            body = str(item.get("text", "") or "")
            if "相手がライブカードを控え室に置かなかった場合" in body and low in {"skip", "__skip__", "no", "n", "0", "false", "置いた", "スキップ"}:
                m = re.search(r"相手は手札からライブカードを\s*(\d+)\s*枚", body)
                return {
                    "n": max(0, int(m.group(1)) if m else 1),
                    "kind": "LIVE",
                    "source_cn": str(item.get("source_cn", "") or ""),
                }
        if kind == "favorite_icecream_answer":
            raw = str((payload or {}).get("choice", "") or "").strip()
            if raw == "チョコミント/ストロベリー/クッキー":
                return {"n": 1, "kind": "ANY", "source_cn": str(item.get("source_cn", "") or "")}
        return None

    def _capture_favorite_answer_side_effect(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item or str(item.get("kind", "") or "") != "favorite_icecream_answer":
            return None
        raw = str((payload or {}).get("choice", "") or "").strip()
        if raw == "あなた":
            return {"kind": "draw", "n": 1, "source_cn": str(item.get("source_cn", "") or "")}
        if raw == "それ以外":
            return {"kind": "stage_blade", "n": 1, "source_cn": str(item.get("source_cn", "") or "")}
        return None

    def _apply_favorite_answer_side_effect(self, rt: PlayerViewRuntime, request: Optional[Dict[str, Any]]) -> None:
        if not request:
            return
        if request.get("kind") == "draw":
            self._apply_opponent_draw_request(rt, request)
            return
        if request.get("kind") == "stage_blade":
            other = self.runtime("p2" if rt.key == "p1" else "p1")
            blade_n = max(0, int(request.get("n", 0) or 0))
            applied: List[str] = []
            for pos, slot in dict(getattr(other.app.gs, "stage", {}) or {}).items():
                if pos in {"L", "C", "R"} and slot is not None and self._slot_cardnumber(slot):
                    setattr(slot, "temp_blade", int(getattr(slot, "temp_blade", 0) or 0) + blade_n)
                    setattr(slot, "temp_until", "end_of_live")
                    applied.append(pos)
            src = str(request.get("source_cn", "") or "?")
            other.app.gs.log.append(f"[DUAL EFFECT][OPPONENT STAGE BLADE] {src}: positions={applied} blade+{blade_n}")
            rt.app.gs.log.append(f"[DUAL EFFECT][OPPONENT STAGE BLADE] {src}: opponent {other.key} positions={applied} blade+{blade_n}")
            self._sync_view_to_core(other)

    def _handle_dual_opponent_hand_pending(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item or str(item.get("kind", "") or "") != "dual_opponent_discard_from_hand":
            return None
        other = self.runtime("p2" if rt.key == "p1" else "p1")
        self._push_history()
        try:
            idx = int((payload or {}).get("idx", -1))
            pending = list(getattr(rt.app.gs, "pending", []) or [])
            if idx < 0 or idx >= len(pending):
                return self._full_state_with_error(rt, "対象の確認項目が見つかりません")
            pending.pop(idx)
            rt.app.gs.pending = pending
            cn = str((payload or {}).get("choice", "") or "").strip()
            opts = [str(x or "") for x in list(item.get("options", []) or [])]
            if cn not in opts:
                rt.app.gs.pending.insert(idx, item)
                self._discard_failed_history()
                return self._full_state_with_error(rt, "相手手札の選択が不正です")
            hand = list(getattr(other.app.gs, "hand", []) or [])
            try:
                hand.remove(cn)
            except ValueError:
                rt.app.gs.pending.insert(idx, item)
                self._discard_failed_history()
                return self._full_state_with_error(rt, "選んだカードが相手手札にありません")
            other.app.gs.hand = hand
            other.app.gs.green_room = list(getattr(other.app.gs, "green_room", []) or []) + [cn]
            src = str(item.get("source_cn", "") or "?")
            other.app.gs.log.append(f"[DUAL EFFECT][OPPONENT HAND DISCARD] {src}: {cn} -> waiting room")
            rt.app.gs.log.append(f"[DUAL EFFECT][OPPONENT HAND DISCARD] {src}: opponent {other.key} discarded 1")
            try:
                from llocg_ui.engine import _enqueue_hand_discard_auto_triggers
                _enqueue_hand_discard_auto_triggers(other.app.gs, other.app.cards_db, [cn])
            except Exception as exc:
                other.app.gs.log.append(f"[WARN] opponent hand-discard auto trigger enqueue failed: {exc}")
            rem = max(0, int(item.get("remaining", 0) or 0) - 1)
            if rem > 0:
                rt.app.gs.pending.insert(
                    idx,
                    self._opponent_hand_discard_pending(
                        other,
                        n=rem,
                        kind=str(item.get("want_kind", "ANY") or "ANY"),
                        source_cn=src,
                    ),
                )
            self._sync_view_to_core(other)
            self._sync_metadata_to_views()
            raw = rt.app.state_json()
            out = self._decorate_player_state(rt, raw if isinstance(raw, dict) else {})
            out["dual_transaction_committed"] = True
            return out
        except Exception:
            self._discard_failed_history()
            raise

    def _handle_dual_opponent_random_reveal_pending(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item or str(item.get("kind", "") or "") != "confirm_effect":
            return None
        body = str(item.get("text", "") or "")
        m = re.search(r"相手の手札を見ないで\s*(\d+)\s*枚公開", body)
        m_draw = re.search(r"カードを\s*(\d+)\s*枚引", body)
        if not m or "ライブカードがない場合" not in body:
            return None
        if self._payload_choice_text(payload) in {"skip", "__skip__", "no", "n", "0", "false", "スキップ"}:
            return None
        other = self.runtime("p2" if rt.key == "p1" else "p1")
        self._push_history()
        try:
            idx = int((payload or {}).get("idx", -1))
            pending = list(getattr(rt.app.gs, "pending", []) or [])
            if idx < 0 or idx >= len(pending):
                return self._full_state_with_error(rt, "対象の確認項目が見つかりません")
            pending.pop(idx)
            rt.app.gs.pending = pending
            count = max(0, int(m.group(1)))
            draw_n = max(0, int(m_draw.group(1)) if m_draw else 0)
            hand = list(getattr(other.app.gs, "hand", []) or [])
            indices = list(range(len(hand)))
            try:
                other.app.rng.shuffle(indices)
            except Exception:
                pass
            picked_indices = sorted(indices[: min(count, len(indices))])
            revealed = [str(hand[i] or "") for i in picked_indices]
            has_live = any(self._card_kind_matches(other, cn, "LIVE") for cn in revealed)
            drew = 0
            if not has_live and draw_n > 0:
                try:
                    from llocg_ui.engine import draw as shared_draw
                    drew = int(shared_draw(rt.app.gs, draw_n, getattr(rt.app, "rng", None)) or 0)
                except Exception as exc:
                    rt.app.gs.log.append(f"[WARN] shared random-reveal draw failed: {exc}")
            src = str(item.get("source_cn", "") or "?")
            rt.app.gs.pending.append({
                "kind": "show_revealed_cards_ack",
                "label": "相手手札ランダム公開",
                "text": f"{src}: 相手手札から{len(revealed)}/{count}枚をランダム公開しました。ライブカード{'あり' if has_live else 'なし'}、ドロー{drew}/{draw_n}。",
                "display_cards": list(revealed),
                "options": ["ok"],
                "source_cn": src,
            })
            rt.app.gs.log.append(
                f"[DUAL EFFECT][OPPONENT HAND REVEAL] {src}: revealed={revealed}; has_live={has_live}; draw={drew}/{draw_n}"
            )
            other.app.gs.log.append(
                f"[DUAL EFFECT][OPPONENT HAND REVEAL] {src}: hand cards revealed count={len(revealed)}"
            )
            self._sync_view_to_core(rt)
            self._sync_metadata_to_views()
            raw = rt.app.state_json()
            out = self._decorate_player_state(rt, raw if isinstance(raw, dict) else {})
            out["dual_transaction_committed"] = True
            return out
        except Exception:
            self._discard_failed_history()
            raise

    @staticmethod
    def _front_slot_for_opponent(source_pos: str) -> str:
        return {"L": "R", "C": "C", "R": "L"}.get(str(source_pos or "").upper(), "C")

    def _source_position_for_card(self, rt: PlayerViewRuntime, source_cn: str) -> str:
        want = str(source_cn or "").strip()
        for pos, slot in dict(getattr(rt.app.gs, "stage", {}) or {}).items():
            if pos in {"L", "C", "R"} and self._slot_cardnumber(slot) == want:
                return pos
        return ""

    def _capture_opponent_position_request(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item:
            return None
        kind0 = str(item.get("kind", "") or "")
        if kind0 not in {"effect_notice", "choose_stage_member_to_position_change_source"}:
            return None
        text = str(item.get("text", "") or "")
        src = str(item.get("source_cn", "") or "")
        if "相手ステージのメンバー1人をこのメンバーの正面" in text:
            src_pos = self._source_position_for_card(rt, src)
            return {
                "mode": "front",
                "source_cn": src,
                "dest": self._front_slot_for_opponent(src_pos),
            }
        if "相手も同じ移動" in text:
            return {"mode": "rotate", "source_cn": src}
        if "相手のセンター" in text:
            return {"mode": "center", "source_cn": src}
        return None

    def _install_opponent_position_pending(self, rt: PlayerViewRuntime, request: Optional[Dict[str, Any]]) -> None:
        if not request:
            return
        other = self.runtime("p2" if rt.key == "p1" else "p1")
        stage = dict(getattr(other.app.gs, "stage", {}) or {})
        src = str(request.get("source_cn", "") or "")
        if request.get("mode") == "rotate":
            old = {pos: stage.get(pos) for pos in ("L", "C", "R")}
            other.app.gs.stage["L"] = old.get("C")
            other.app.gs.stage["R"] = old.get("L")
            other.app.gs.stage["C"] = old.get("R")
            other.app.gs.log.append(f"[DUAL EFFECT][OPPONENT POSITION] {src or '?'}: rotate C->L L->R R->C")
            rt.app.gs.log.append(f"[DUAL EFFECT][OPPONENT POSITION] {src or '?'}: opponent {other.key} rotate")
            self._sync_view_to_core(other)
            return
        if request.get("mode") == "front":
            options = [pos for pos in ("L", "C", "R") if stage.get(pos) is not None]
            pending = {
                "kind": "dual_opponent_position_change",
                "text": f"相手ステージのメンバー1人を正面エリア（{request.get('dest')}）へポジションチェンジします。移動元を選んでください。",
                "options": options,
                "dest": str(request.get("dest", "C") or "C"),
                "source_cn": src,
            }
        else:
            options = [pos for pos in ("L", "R") if stage.get(pos) is not None]
            pending = {
                "kind": "dual_opponent_position_change",
                "text": "相手のセンターにいるメンバーをポジションチェンジします。移動先を選んでください。",
                "options": options,
                "src_pos": "C",
                "source_cn": src,
            }
        rt.app.gs.pending = list(getattr(rt.app.gs, "pending", []) or []) + [pending]
        rt.app.gs.log.append(f"[DUAL EFFECT][OPPONENT POSITION] {src or '?'}: prepared {request}")

    def _handle_dual_opponent_position_pending(
        self,
        rt: PlayerViewRuntime,
        cmd: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if str(cmd or "") != "resolve_pending":
            return None
        item = self._pending_item_for_command(rt, cmd, payload)
        if not item or str(item.get("kind", "") or "") != "dual_opponent_position_change":
            return None
        other = self.runtime("p2" if rt.key == "p1" else "p1")
        self._push_history()
        try:
            idx = int((payload or {}).get("idx", -1))
            pending = list(getattr(rt.app.gs, "pending", []) or [])
            if idx < 0 or idx >= len(pending):
                return self._full_state_with_error(rt, "対象の確認項目が見つかりません")
            pending.pop(idx)
            rt.app.gs.pending = pending
            choice = str((payload or {}).get("choice", "") or "").strip().upper()
            stage = getattr(other.app.gs, "stage", {}) or {}
            if "src_pos" in item:
                src_pos = str(item.get("src_pos", "") or "").upper()
                dest = choice
            else:
                src_pos = choice
                dest = str(item.get("dest", "") or "").upper()
            if src_pos not in {"L", "C", "R"} or dest not in {"L", "C", "R"} or src_pos == dest:
                rt.app.gs.pending.insert(idx, item)
                self._discard_failed_history()
                return self._full_state_with_error(rt, "ポジション選択が不正です")
            stage[src_pos], stage[dest] = stage.get(dest), stage.get(src_pos)
            src = str(item.get("source_cn", "") or "?")
            other.app.gs.log.append(f"[DUAL EFFECT][OPPONENT POSITION] {src}: swap {src_pos}<->{dest}")
            rt.app.gs.log.append(f"[DUAL EFFECT][OPPONENT POSITION] {src}: opponent {other.key} swap {src_pos}<->{dest}")
            self._sync_view_to_core(other)
            self._sync_metadata_to_views()
            raw = rt.app.state_json()
            out = self._decorate_player_state(rt, raw if isinstance(raw, dict) else {})
            out["dual_transaction_committed"] = True
            return out
        except Exception:
            self._discard_failed_history()
            raise

    @staticmethod
    def _clean_hand_indices(payload: Dict[str, Any]) -> list[int]:
        raw = payload.get("indices", []) if isinstance(payload, dict) else []
        if not isinstance(raw, list):
            return []
        out: list[int] = []
        for value in raw:
            try:
                idx = int(value)
            except (TypeError, ValueError):
                continue
            if idx >= 0 and idx not in out:
                out.append(idx)
        return sorted(out)

    @staticmethod
    def _legacy_is_live_set_phase(value: Any) -> bool:
        return str(value or "").strip().upper() in {"LIVE_SET", "DUAL_WAIT_LIVE_SET"}

    @staticmethod
    def _legacy_is_performance_phase(value: Any) -> bool:
        phase = str(value or "").strip().upper()
        return phase.startswith("LIVE_") and phase != "LIVE_SET"

    def _prepare_active_performance_runtime(self) -> PlayerViewRuntime:
        phase = self.engine.state.phase
        if phase not in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND}:
            raise ValueError("現在はパフォーマンスフェイズではありません")
        rt = self._active_runtime()
        gs = rt.app.gs
        started = bool(getattr(rt.app, "_dual_performance_started", False))
        if not started:
            # The one-player UI often reports LIVE_RESOLVE immediately after
            # LIVE_SET even though its actual performance flow still has to run.
            # Never treat that display value as the dual 8.3/8.4 boundary.
            # Restore a known pre-YELL entry phase exactly once per player.
            entry_phase = str(
                getattr(rt.app, "_dual_performance_entry_phase", "") or "LIVE_CONFIRM"
            ).strip().upper()
            if entry_phase not in {"LIVE_CONFIRM", "LIVE_PERF", "LIVE_ATTEMPT"}:
                entry_phase = "LIVE_CONFIRM"
            gs.phase = entry_phase
            gs.live_start_prompted = False
            setattr(rt.app, "_dual_yell_notice_acknowledged", False)
            setattr(rt.app, "_dual_live_attempt_succeeded", None)
            self._clear_legacy_attempt_result_state(rt)
            setattr(rt.app, "_dual_performance_started", True)
            setattr(rt.app, "_dual_last_boundary_snapshot", self._capture_live_boundary(rt))
        elif not self._legacy_is_performance_phase(getattr(gs, "phase", "")):
            gs.phase = "LIVE_CONFIRM"
        setattr(rt.app, "_dual_performance_exit_pending", False)
        return rt

    def _complete_active_performance(self, rt: PlayerViewRuntime) -> None:
        self._sync_view_to_core(rt)
        self.engine.complete_performance(rt.player_id, record_history=False)
        setattr(rt.app, "_dual_performance_exit_pending", False)
        setattr(rt.app, "_dual_performance_entry_phase", "")
        setattr(rt.app, "_dual_performance_started", False)
        setattr(rt.app, "_dual_last_boundary_snapshot", None)
        if self.engine.state.phase in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND}:
            self._prepare_active_performance_runtime()

    def _capture_live_boundary(self, rt: PlayerViewRuntime) -> Dict[str, Any]:
        gs = rt.app.gs
        return {
            "live": list(getattr(gs, "set_zone", []) or []),
            "success": list(getattr(gs, "success_zone", []) or []),
            "resolve": list(getattr(gs, "resolve_zone", []) or []),
            "green": list(getattr(gs, "green_room", []) or []),
            "phase": str(getattr(gs, "phase", "") or ""),
            "turn": int(getattr(gs, "turn", self.engine.state.turn) or self.engine.state.turn),
        }

    @staticmethod
    def _counter_added_contains(before: List[str], after: List[str], required: List[str]) -> bool:
        added = Counter(after) - Counter(before)
        needed = Counter(required)
        return all(added[cn] >= count for cn, count in needed.items())

    def _is_rule_8316_failure_transition(
        self, rt: PlayerViewRuntime, before: Dict[str, Any]
    ) -> bool:
        """Detect the legitimate all-live-to-waiting-room move of rule 8.3.16.

        The previous bridge restored every live-zone drift at LIVE_RESOLVE,
        accidentally undoing a failed live and then scoring it as successful.
        Restrict this recognition to a transition that began in LIVE_ATTEMPT,
        removed every live without changing the success zone, and added those
        exact cards to the waiting room.
        """
        phase_before = str(before.get("phase", "") or "").strip().upper()
        if not phase_before.startswith("LIVE_ATTEMPT"):
            return False
        live_before = list(before.get("live", []) or [])
        if not live_before:
            return False
        gs = rt.app.gs
        if list(getattr(gs, "set_zone", []) or []):
            return False
        if list(getattr(gs, "success_zone", []) or []) != list(before.get("success", []) or []):
            return False
        if self._has_single_player_success_prompt(rt):
            return False
        return self._counter_added_contains(
            list(before.get("green", []) or []),
            list(getattr(gs, "green_room", []) or []),
            live_before,
        )

    def _is_no_live_after_confirm_transition(
        self, rt: PlayerViewRuntime, before: Dict[str, Any]
    ) -> bool:
        """Detect LIVE_CONFIRM ending with no live cards to perform.

        This includes both a filtered-out non-LIVE set and a legal zero-card
        live set.  In either case no LIVE_ATTEMPT result is exported by the
        one-player runtime, so dual v2 must record a failed/no-live result.
        """
        phase_before = str(before.get("phase", "") or "").strip().upper()
        if phase_before != "LIVE_CONFIRM":
            return False
        gs = rt.app.gs
        phase_after = str(getattr(gs, "phase", "") or "").strip().upper()
        if phase_after != "LIVE_RESOLVE":
            return False
        if list(getattr(gs, "set_zone", []) or []):
            return False
        if list(getattr(gs, "success_zone", []) or []) != list(before.get("success", []) or []):
            return False
        live_before = list(before.get("live", []) or [])
        if not live_before:
            return True
        return self._counter_added_contains(
            list(before.get("green", []) or []),
            list(getattr(gs, "green_room", []) or []),
            live_before,
        )

    def _record_live_attempt_outcome(
        self, rt: PlayerViewRuntime, succeeded: bool, *, source: str = ""
    ) -> None:
        setattr(rt.app, "_dual_live_attempt_succeeded", bool(succeeded))
        result = "SUCCESS" if succeeded else "FAILURE"
        suffix = f" source={source}" if source else ""
        self.engine.state.log.append(
            f"[ATTEMPT RESULT][P{rt.player_id + 1}] {result} live_remaining="
            f"{len(list(getattr(rt.app.gs, 'set_zone', []) or []))}{suffix}"
        )

    def _has_single_player_success_prompt(self, rt: PlayerViewRuntime) -> bool:
        return any(
            self._is_single_player_success_placement_pending(item)
            for item in list(getattr(rt.app.gs, "pending", []) or [])
        )

    def _at_dual_success_boundary(
        self, rt: PlayerViewRuntime, *, include_live_resolve: bool = True
    ) -> bool:
        phase = str(getattr(rt.app.gs, "phase", "") or "").strip().upper()
        return (include_live_resolve and phase == "LIVE_RESOLVE") or self._has_single_player_success_prompt(rt)

    def _normalize_legacy_success_boundary(
        self,
        rt: PlayerViewRuntime,
        *,
        live_before: List[str],
        success_before: List[str],
        resolve_before: Optional[List[str]] = None,
        green_before: Optional[List[str]] = None,
    ) -> Tuple[int, int, int]:
        """Quarantine the legacy one-player continuation at the 8.3/8.4 edge.

        The legacy runtime may create its old success-store choice, move a live
        card, clean YELL cards, or even start the next turn.  None of those are
        legal owners in dual v2.  Keep card-effect side effects, but restore the
        protected live/success zones and remove only the one-player placement
        branch.  Live-success pending is deferred to dual rule 8.4.4/8.4.5.
        """
        gs = rt.app.gs
        success_after = list(getattr(gs, "success_zone", []) or [])
        remaining_before = list(success_before)
        added_success: List[str] = []
        for cn in success_after:
            if cn in remaining_before:
                remaining_before.remove(cn)
            else:
                added_success.append(cn)

        kept: List[Any] = []
        deferred: List[Any] = list(getattr(rt.app, "_dual_deferred_success_pending", []) or [])
        dropped = 0
        for item in list(getattr(gs, "pending", []) or []):
            if self._is_single_player_success_placement_pending(item):
                dropped += 1
                continue
            if self._is_live_success_effect_pending(item):
                deferred.append(copy.deepcopy(item))
                continue
            kept.append(item)
        gs.pending = kept
        setattr(rt.app, "_dual_deferred_success_pending", deferred)

        phase_after = str(getattr(gs, "phase", "") or "").strip().upper()
        emergency_cleanup = phase_after in {"MAIN", "ACTIVE", "ENERGY", "DRAW"}
        live_after = list(getattr(gs, "set_zone", []) or [])
        failed_attempt = getattr(rt.app, "_dual_live_attempt_succeeded", None) is False
        protected_live = [] if failed_attempt else list(live_before)
        zone_drift = live_after != protected_live or success_after != list(success_before)
        if added_success or dropped or zone_drift or emergency_cleanup:
            gs.set_zone = protected_live
            gs.success_zone = list(success_before)

        # Emergency recovery for a legacy command that got as far as its own
        # cleanup/next-turn code.  This path is not the normal bridge path; it
        # exists to prevent a second no-live judgment after any future runtime
        # change.  Remove duplicated protected cards from green before restoring
        # the YELL zone.
        if emergency_cleanup and resolve_before is not None:
            from collections import Counter
            baseline = Counter(list(green_before or []))
            protected = Counter(list(live_before) + list(resolve_before))
            current = list(getattr(gs, "green_room", []) or [])
            kept_green: List[str] = []
            seen = Counter()
            for cn in current:
                seen[cn] += 1
                extra_over_baseline = seen[cn] > baseline[cn]
                if protected[cn] > 0 and extra_over_baseline:
                    protected[cn] -= 1
                    continue
                kept_green.append(cn)
            gs.green_room = kept_green
            gs.resolve_zone = list(resolve_before)
            gs.turn = int(self.engine.state.turn)

        setattr(rt.app, "_dual_judgment_entry_phase", "LIVE_RESOLVE")
        if added_success or dropped or zone_drift or emergency_cleanup:
            self.engine.state.log.append(
                f"[DUAL BOUNDARY][P{rt.player_id + 1}] legacy success branch blocked "
                f"moved={len(added_success)} pending={dropped} "
                f"zone_drift={int(zone_drift)} emergency={int(emergency_cleanup)}"
            )
        return len(added_success), dropped, len(deferred)

    def _run_active_performance_step(self) -> bool:
        """Advance one real legacy performance substep, never its 1P tail."""
        rt = self._active_runtime()
        gs = rt.app.gs
        pending = list(getattr(gs, "pending", []) or [])
        exit_pending = bool(getattr(rt.app, "_dual_performance_exit_pending", False))

        if exit_pending:
            if pending:
                return False
            self._complete_active_performance(rt)
            return True

        self._prepare_active_performance_runtime()

        # Do not read legacy last_attempt_* fields here.  At performance entry
        # they may still describe the previous turn; the new attempt has not run.
        # LIVE_RESOLVE is the one-player hand-off into success effects/store.
        # In dual v2 it is a boundary marker, not a subphase to execute.
        if self._at_dual_success_boundary(rt):
            snap = getattr(rt.app, "_dual_last_boundary_snapshot", None) or self._capture_live_boundary(rt)
            if getattr(rt.app, "_dual_live_attempt_succeeded", None) is None:
                explicit = self._apply_explicit_attempt_result(rt, context="boundary-entry")
                if explicit is None and self._has_single_player_success_prompt(rt):
                    self._record_live_attempt_outcome(rt, True, source="legacy-success-prompt")
                elif explicit is None:
                    raise ValueError(
                        f"P{rt.player_id + 1}のライブ成否を旧Appから取得できません。"
                        "last_attempt_result系の状態を確認してください"
                    )
            self._normalize_legacy_success_boundary(
                rt,
                live_before=list(snap.get("live", []) or []),
                success_before=list(snap.get("success", []) or []),
                resolve_before=list(snap.get("resolve", []) or []),
                green_before=list(snap.get("green", []) or []),
            )
            self._sync_view_to_core(rt)
            self.engine.state.log.append(
                f"[PERFORMANCE][P{rt.player_id + 1}] dual boundary reached before legacy tail"
            )
            self._complete_active_performance(rt)
            return True

        before = self._capture_live_boundary(rt)
        setattr(rt.app, "_dual_last_boundary_snapshot", copy.deepcopy(before))
        before_phase = str(getattr(gs, "phase", "") or "")
        before_pending = len(list(getattr(gs, "pending", []) or []))
        rt.app.cmd("next", {})
        self._suppress_reopened_yell_notice(rt)
        after_phase = str(getattr(gs, "phase", "") or "")
        if self._attempt_result_can_be_new(before_phase, after_phase):
            self._apply_explicit_attempt_result(rt, context=f"performance:{before_phase}")

        # Rule 8.3.16 is a legitimate zone change, not legacy success-store
        # drift.  Preserve the failed cards in the waiting room and never
        # restore them to set_zone for the score comparison.
        if self._is_rule_8316_failure_transition(rt, before):
            self._record_live_attempt_outcome(rt, False)
            after_pending = list(getattr(gs, "pending", []) or [])
            self._sync_view_to_core(rt)
            self.engine.state.log.append(
                f"[PERFORMANCE][P{rt.player_id + 1}] "
                f"legacy_phase={before_phase}->{after_phase} "
                f"pending={before_pending}->{len(after_pending)} rule=8.3.16"
            )
            if after_pending or self._has_legacy_dialog(rt):
                setattr(rt.app, "_dual_performance_exit_pending", True)
                return False
            self._complete_active_performance(rt)
            return True

        # LIVE_CONFIRM can filter out every set card when the player set only
        # non-LIVE cards.  No live attempt occurs, so no legacy attempt result
        # exists; dual v2 should simply complete that player's performance with
        # no live remaining.
        if self._is_no_live_after_confirm_transition(rt, before):
            self._record_live_attempt_outcome(rt, False, source="no-live-after-filter")
            after_pending = list(getattr(gs, "pending", []) or [])
            self._sync_view_to_core(rt)
            self.engine.state.log.append(
                f"[PERFORMANCE][P{rt.player_id + 1}] "
                f"legacy_phase={before_phase}->{after_phase} "
                f"pending={before_pending}->{len(after_pending)} no_live_after_filter=1"
            )
            if after_pending or self._has_legacy_dialog(rt):
                setattr(rt.app, "_dual_performance_exit_pending", True)
                return False
            self._complete_active_performance(rt)
            return True

        if self._at_dual_success_boundary(rt) or after_phase.strip().upper() in {"MAIN", "ACTIVE", "ENERGY", "DRAW"}:
            if getattr(rt.app, "_dual_live_attempt_succeeded", None) is None:
                explicit = self._apply_explicit_attempt_result(rt, context="boundary-entry")
                if explicit is None and self._has_single_player_success_prompt(rt):
                    self._record_live_attempt_outcome(rt, True, source="legacy-success-prompt")
                elif explicit is None:
                    raise ValueError(
                        f"P{rt.player_id + 1}のライブ成否を旧Appから取得できません。"
                        "last_attempt_result系の状態を確認してください"
                    )
            self._normalize_legacy_success_boundary(
                rt,
                live_before=list(before["live"]),
                success_before=list(before["success"]),
                resolve_before=list(before["resolve"]),
                green_before=list(before["green"]),
            )
            after_pending = list(getattr(gs, "pending", []) or [])
            self._sync_view_to_core(rt)
            self.engine.state.log.append(
                f"[PERFORMANCE][P{rt.player_id + 1}] "
                f"legacy_phase={before_phase}->{after_phase} "
                f"pending={before_pending}->{len(after_pending)} boundary=dual"
            )
            if after_pending:
                setattr(rt.app, "_dual_performance_exit_pending", True)
                return False
            self._complete_active_performance(rt)
            return True

        after_pending = list(getattr(gs, "pending", []) or [])
        self._sync_view_to_core(rt)
        self.engine.state.log.append(
            f"[PERFORMANCE][P{rt.player_id + 1}] "
            f"legacy_phase={before_phase}->{after_phase} "
            f"pending={before_pending}->{len(after_pending)}"
        )
        if self._legacy_is_performance_phase(after_phase):
            return False
        if after_pending:
            setattr(rt.app, "_dual_performance_exit_pending", True)
            return False
        self._complete_active_performance(rt)
        return True

    def _prepare_success_runtime(self, player_id: int) -> PlayerViewRuntime:
        rt = self.runtime("p1" if int(player_id) == 0 else "p2")
        gs = rt.app.gs
        # Use the immutable dual snapshot captured at the attempt boundary.
        if (
            getattr(rt.app, "_dual_live_attempt_succeeded", None) is not True
            or not list(getattr(gs, "set_zone", []) or [])
        ):
            setattr(rt.app, "_dual_success_runtime_done", True)
            return rt
        self._suppress_reopened_yell_notice(rt)
        if not bool(getattr(rt.app, "_dual_success_runtime_started", False)):
            gs.phase = str(getattr(rt.app, "_dual_judgment_entry_phase", "") or "LIVE_RESOLVE")
            if str(gs.phase).strip().upper() != "LIVE_RESOLVE":
                gs.phase = "LIVE_RESOLVE"
            deferred = list(getattr(rt.app, "_dual_deferred_success_pending", []) or [])
            if deferred and not list(getattr(gs, "pending", []) or []):
                gs.pending = copy.deepcopy(deferred)
                setattr(rt.app, "_dual_deferred_success_pending", [])
            setattr(rt.app, "_dual_success_runtime_started", True)
        return rt

    def _run_success_trigger_step(self, player_id: int) -> bool:
        """Run one player's 8.4.4/8.4.5 legacy success-effect check timing."""
        rt = self._prepare_success_runtime(player_id)
        gs = rt.app.gs
        if bool(getattr(rt.app, "_dual_success_runtime_done", False)):
            return True
        if list(getattr(gs, "pending", []) or []):
            return False

        boundary = self._capture_live_boundary(rt)
        setattr(rt.app, "_dual_last_boundary_snapshot", copy.deepcopy(boundary))
        live_before = list(boundary["live"])
        success_before = list(boundary["success"])
        before_phase = str(getattr(gs, "phase", "") or "")
        rt.app.cmd("next", {})
        self._suppress_reopened_yell_notice(rt)
        after_phase = str(getattr(gs, "phase", "") or "")
        moved, dropped, _deferred = self._normalize_legacy_success_boundary(
            rt,
            live_before=live_before,
            success_before=success_before,
            resolve_before=list(boundary["resolve"]),
            green_before=list(boundary["green"]),
        )
        deferred_now = list(getattr(rt.app, "_dual_deferred_success_pending", []) or [])
        if deferred_now and not list(getattr(gs, "pending", []) or []):
            gs.pending = copy.deepcopy(deferred_now)
            setattr(rt.app, "_dual_deferred_success_pending", [])
        pending = list(getattr(gs, "pending", []) or [])
        self._sync_view_to_core(rt)
        self.engine.state.log.append(
            f"[LIVE SUCCESS][P{rt.player_id + 1}] "
            f"legacy_phase={before_phase}->{after_phase} pending={len(pending)}"
        )
        if pending:
            return False
        # When the only legacy output was its placement prompt/movement, the
        # success-trigger check timing is complete; do not call it again.
        if moved or dropped or not str(after_phase).strip().upper().startswith("LIVE_"):
            setattr(rt.app, "_dual_success_runtime_done", True)
            gs.phase = "DUAL_JUDGMENT"
            return True
        return False

    def _success_move_blocked(self, rt: PlayerViewRuntime, cardnumber: str) -> bool:
        gs = rt.app.gs
        for name in (
            "cannot_place_success", "success_zone_blocked", "prevent_success_move",
            "cannot_put_success_live", "dual_success_move_blocked",
        ):
            value = getattr(gs, name, False)
            if value is True:
                return True
            if isinstance(value, (list, tuple, set)) and cardnumber in value:
                return True
            if isinstance(value, dict) and bool(value.get(cardnumber) or value.get("all")):
                return True
        record = self._detail_card_record(rt, cardnumber)
        text = self._card_text_value(record)
        return "成功ライブカード置き場に置くことができない" in text

    def _move_success_card(self, player_id: int, live_index: int) -> str:
        rt = self.runtime("p1" if int(player_id) == 0 else "p2")
        gs = rt.app.gs
        cards = list(getattr(gs, "set_zone", []) or [])
        idx = int(live_index)
        if idx < 0 or idx >= len(cards):
            raise ValueError("成功ライブの選択位置が不正です")
        cardnumber = cards[idx]
        if self._success_move_blocked(rt, cardnumber):
            raise ValueError("このカードは成功ライブカード置き場に置けません")
        cards.pop(idx)
        gs.set_zone = cards
        gs.success_zone = list(getattr(gs, "success_zone", []) or []) + [cardnumber]
        self._sync_view_to_core(rt)
        moved = self.engine.state.success_moved_player_ids
        if int(player_id) not in moved:
            moved.append(int(player_id))
        self.engine.state.log.append(f"[SUCCESS MOVE][P{int(player_id) + 1}] {cardnumber}")
        return cardnumber

    def _set_success_pick_prompt(self) -> None:
        match = self.engine.state
        match.judgment_prompt = {}
        while match.success_move_queue:
            pid = int(match.success_move_queue[0])
            rt = self.runtime("p1" if pid == 0 else "p2")
            cards = list(getattr(rt.app.gs, "set_zone", []) or [])
            candidates = [
                {"index": idx, "cardnumber": cn}
                for idx, cn in enumerate(cards)
                if not self._success_move_blocked(rt, cn)
            ]
            if not candidates:
                match.success_move_queue.pop(0)
                continue
            if len(candidates) == 1:
                self._move_success_card(pid, int(candidates[0]["index"]))
                match.success_move_queue.pop(0)
                continue
            match.judgment_active_player_id = pid
            match.judgment_prompt = {
                "kind": "pick_success_live",
                "player_id": pid,
                "message": f"プレイヤー{pid + 1}: 成功ライブカード置き場に置くカードを1枚選んでください",
                "candidates": candidates,
            }
            return
        match.judgment_active_player_id = match.first_player_id
        match.judgment_step = "CLEANUP"

    def _determine_live_winners(self, scores: List[int]) -> List[int]:
        has_live = [
            getattr(self.runtime("p1").app, "_dual_live_attempt_succeeded", None) is True
            and bool(list(getattr(self.runtime("p1").app.gs, "set_zone", []) or [])),
            getattr(self.runtime("p2").app, "_dual_live_attempt_succeeded", None) is True
            and bool(list(getattr(self.runtime("p2").app.gs, "set_zone", []) or [])),
        ]
        if not any(has_live):
            return []
        if has_live[0] and not has_live[1]:
            return [0]
        if has_live[1] and not has_live[0]:
            return [1]
        if int(scores[0]) > int(scores[1]):
            return [0]
        if int(scores[1]) > int(scores[0]):
            return [1]
        return [0, 1]

    def _cleanup_live_zones(self) -> None:
        for rt in self.players.values():
            gs = rt.app.gs
            live = list(getattr(gs, "set_zone", []) or [])
            yell = list(getattr(gs, "resolve_zone", []) or [])
            gs.green_room = list(getattr(gs, "green_room", []) or []) + live + yell
            gs.set_zone = []
            gs.resolve_zone = []
            gs.pending = []
            gs.phase = "DUAL_WAIT"
            setattr(rt.app, "_dual_performance_entry_phase", "")
            setattr(rt.app, "_dual_performance_started", False)
            setattr(rt.app, "_dual_last_boundary_snapshot", None)
            setattr(rt.app, "_dual_judgment_entry_phase", "LIVE_RESOLVE")
            setattr(rt.app, "_dual_deferred_success_pending", [])
            setattr(rt.app, "_dual_success_runtime_started", False)
            setattr(rt.app, "_dual_success_runtime_done", False)
            setattr(rt.app, "_dual_live_attempt_succeeded", None)
            setattr(rt.app, "_dual_yell_notice_acknowledged", False)
            self._sync_view_to_core(rt)

    def _game_result_after_success_moves(self) -> Tuple[Optional[int], str]:
        # MatchState is the authoritative source for duel-level victory.  The
        # embedded one-player Apps are synchronized views and can be temporarily
        # behind during judgment/cleanup boundaries.
        counts = [
            len(list(getattr(self.engine.state.players[0], "success_zone", []) or [])),
            len(list(getattr(self.engine.state.players[1], "success_zone", []) or [])),
        ]
        if counts[0] >= 3 and counts[1] >= 3:
            return None, "DRAW"
        if counts[0] >= 3 and counts[1] <= 2:
            return 0, "P1_WIN"
        if counts[1] >= 3 and counts[0] <= 2:
            return 1, "P2_WIN"
        return None, ""

    def _run_dual_judgment_step(self, payload: Dict[str, Any]) -> None:
        match = self.engine.state
        if match.phase != Phase.LIVE_JUDGMENT:
            raise ValueError("現在はライブ勝敗判定フェイズではありません")
        first = int(match.first_player_id)
        second = 1 - first
        step = str(match.judgment_step or "")

        if not step:
            unresolved: List[int] = []
            for rt in self.players.values():
                # The result must already have been captured when LIVE_ATTEMPT
                # completed.  Do not re-import stale legacy fields at judgment.
                self._suppress_reopened_yell_notice(rt)
                if getattr(rt.app, "_dual_live_attempt_succeeded", None) is None:
                    unresolved.append(rt.player_id + 1)
            if unresolved:
                raise ValueError(
                    "ライブ成否が未確定です: " + ",".join(f"P{x}" for x in unresolved)
                )
            scores: List[int] = []
            sources: List[str] = []
            for key in ("p1", "p2"):
                score, source = self._calculate_live_score(self.runtime(key))
                scores.append(int(score)); sources.append(source)
            match.live_scores = scores
            match.judgment_step = "INITIAL_SCORE"
            match.judgment_active_player_id = first
            self._set_opponent_score_contexts(scores)
            match.log.append(
                f"[JUDGMENT 8.4.1-3] initial score P1={scores[0]} P2={scores[1]} "
                f"source={sources}"
            )
            return

        if step == "INITIAL_SCORE":
            match.judgment_step = "SUCCESS_FIRST"
            match.judgment_active_player_id = first
            self._prepare_success_runtime(first)
            match.log.append(f"[JUDGMENT 8.4.4-5] P{first + 1} ライブ成功時チェック")
            return

        if step == "SUCCESS_FIRST":
            if not self._run_success_trigger_step(first):
                return
            match.judgment_step = "SUCCESS_SECOND"
            match.judgment_active_player_id = second
            self._prepare_success_runtime(second)
            match.log.append(f"[JUDGMENT 8.4.4-5] P{second + 1} ライブ成功時チェック")
            return

        if step == "SUCCESS_SECOND":
            if not self._run_success_trigger_step(second):
                return
            match.judgment_step = "FINAL_SCORE"
            match.judgment_active_player_id = first
            return

        if step == "FINAL_SCORE":
            scores = []
            sources = []
            for key in ("p1", "p2"):
                score, source = self._calculate_live_score(self.runtime(key))
                scores.append(int(score)); sources.append(source)
            match.live_scores = scores
            self._set_opponent_score_contexts(scores)
            winners = self._determine_live_winners(scores)
            match.live_winners = list(winners)
            match.success_move_queue = []
            both_win = len(winners) == 2
            # If both players must choose simultaneously, the general choice
            # rule applies: the active/first player chooses before the other.
            # Keep the winner set itself canonical, but queue the choices in
            # current first-player order.
            for pid in (first, second):
                if pid not in winners:
                    continue
                rt = self.runtime("p1" if pid == 0 else "p2")
                cards = list(getattr(rt.app.gs, "set_zone", []) or [])
                success_count = len(list(getattr(rt.app.gs, "success_zone", []) or []))
                # Rule 8.4.7.1: when both players win, a player with exactly
                # two successful live cards does not move a card to the success
                # zone.  This depends on the success zone count, not on how many
                # cards were set for the current live.
                if both_win and success_count == 2:
                    match.log.append(f"[JUDGMENT 8.4.7.1][P{pid + 1}] 成功置き場2枚のため成功移動なし")
                    continue
                if cards:
                    match.success_move_queue.append(pid)
            match.judgment_step = "RESULT_CONFIRM"
            match.judgment_active_player_id = first
            match.judgment_prompt = {}
            match.log.append(
                f"[JUDGMENT 8.4.6] final score P1={scores[0]} P2={scores[1]} "
                f"winners={[pid + 1 for pid in winners]} source={sources}"
            )
            return

        if step == "RESULT_CONFIRM":
            # Keep the comparison result visible for one explicit NEXT.  Only
            # after confirmation does rule 8.4.7 move/choose success cards.
            match.judgment_step = "PICK_SUCCESS"
            self._set_success_pick_prompt()
            return

        if step == "PICK_SUCCESS":
            prompt = dict(match.judgment_prompt or {})
            if not prompt or prompt.get("kind") != "pick_success_live":
                self._set_success_pick_prompt()
                return
            raw_idx = payload.get("live_index") if isinstance(payload, dict) else None
            try:
                idx = int(raw_idx)
            except (TypeError, ValueError):
                raise ValueError("成功ライブカードを選択してください")
            valid = {int(item.get("index")) for item in list(prompt.get("candidates", []) or [])}
            if idx not in valid:
                raise ValueError("選択された成功ライブカードが候補にありません")
            pid = int(prompt.get("player_id"))
            self._move_success_card(pid, idx)
            if match.success_move_queue and int(match.success_move_queue[0]) == pid:
                match.success_move_queue.pop(0)
            match.judgment_prompt = {}
            self._set_success_pick_prompt()
            return

        if step == "CLEANUP":
            self._cleanup_live_zones()
            moved = list(match.success_moved_player_ids)
            next_first = int(moved[0]) if len(moved) == 1 else first
            winner_pid, game_result = self._game_result_after_success_moves()
            match.log.append(
                f"[JUDGMENT 8.4.8-13] cleanup moved={[pid + 1 for pid in moved]} "
                f"next_first=P{next_first + 1}"
            )
            self.engine.enter_turn_end(
                first_player_id=next_first,
                winner_player_id=winner_pid,
                game_result=game_result,
            )
            return

        raise ValueError(f"不明なライブ勝敗判定ステップです: {step}")

    def _commit_active_live_set(self, payload: Dict[str, Any]) -> tuple[bool, bool]:
        """Run the legacy App's real live-set action, then advance only when complete.

        Returns ``(phase_advanced, selection_consumed)``.  The caller owns the
        match-level snapshot so the legacy zone changes and central phase change
        are one Undo transaction in the normal no-pending case.
        """
        phase = self.engine.state.phase
        if phase not in {Phase.LIVE_SET_FIRST, Phase.LIVE_SET_SECOND}:
            raise ValueError("ライブセットフェイズではありません")

        rt = self._active_runtime()
        player = self.engine.state.players[rt.player_id]
        selection_consumed = bool(player.live_set_committed)

        if not player.live_set_committed:
            indices = self._clean_hand_indices(payload)
            gs = rt.app.gs
            before_set = len(list(getattr(gs, "set_zone", []) or []))
            before_hand = len(list(getattr(gs, "hand", []) or []))
            before_deck = len(list(getattr(gs, "deck", []) or []))

            # The one-player App remains the rules authority: its LIVE_SET NEXT
            # performs hand -> set_zone and the matching draw.  The dual engine
            # never edits these card arrays directly.
            rt.app.cmd("next", {"indices": indices})

            raw_phase = getattr(gs, "phase", "")
            after_set = len(list(getattr(gs, "set_zone", []) or []))
            after_hand = len(list(getattr(gs, "hand", []) or []))
            after_deck = len(list(getattr(gs, "deck", []) or []))
            pending = list(getattr(gs, "pending", []) or [])

            # A non-zero selection is committed once the set zone actually
            # changes.  A zero-card set is legal, so it is committed only when
            # the legacy App leaves LIVE_SET.
            committed = (after_set > before_set) or not self._legacy_is_live_set_phase(raw_phase)
            self._sync_view_to_core(rt)
            player = self.engine.state.players[rt.player_id]
            if committed:
                entry_phase = str(raw_phase or "").strip().upper()
                if entry_phase not in {"LIVE_CONFIRM", "LIVE_PERF", "LIVE_ATTEMPT"}:
                    # LIVE_RESOLVE is a legacy umbrella/tail value and must not
                    # become the dual performance entry point.
                    entry_phase = "LIVE_CONFIRM"
                setattr(rt.app, "_dual_performance_entry_phase", entry_phase)
                setattr(rt.app, "_dual_performance_started", False)
                setattr(rt.app, "_dual_last_boundary_snapshot", None)
                player.live_set_committed = True
                selection_consumed = True
                self.engine.state.log.append(
                    f"[LIVE SET][P{rt.player_id + 1}] selected={len(indices)} "
                    f"set={before_set}->{after_set} hand={before_hand}->{after_hand} "
                    f"deck={before_deck}->{after_deck}"
                )
            elif pending:
                # A start/check-timing effect may need resolution before the
                # actual selection is consumed.  Keep the central phase and the
                # browser selection intact; after pending resolution NEXT retries
                # the legacy live-set action exactly once.
                self._sync_metadata_to_views()
                return False, False
            else:
                raise ValueError(
                    "ライブセット処理が完了しませんでした。選択カードと旧AppのLIVE_SET処理を確認してください"
                )

        if list(getattr(rt.app.gs, "pending", []) or []):
            self._sync_metadata_to_views()
            return False, selection_consumed

        self.engine.advance(record_history=False)
        if self.engine.state.phase in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND}:
            self._prepare_active_performance_runtime()
        return True, selection_consumed

    def _judgment_ui_message(self) -> str:
        match = self.engine.state
        if match.phase != Phase.LIVE_JUDGMENT:
            return ""
        scores = list(match.live_scores or [0, 0])
        step = str(match.judgment_step or "")
        first = int(match.first_player_id)
        second = 1 - first
        if not step:
            return "ライブ判定フェイズを開始します。ライブカードとエールのスコアを集計します。"
        if step == "INITIAL_SCORE":
            return f"初期合計スコア　P1 {scores[0]} − {scores[1]} P2。先攻からライブ成功時能力を確認します。"
        if step == "SUCCESS_FIRST":
            return f"プレイヤー{first + 1}の「ライブ成功時」能力を確認・解決中です。"
        if step == "SUCCESS_SECOND":
            return f"プレイヤー{second + 1}の「ライブ成功時」能力を確認・解決中です。"
        if step == "FINAL_SCORE":
            return "すべてのライブ成功時能力の解決後、最終合計スコアを再計算します。"
        if step == "RESULT_CONFIRM":
            winners = list(match.live_winners or [])
            who = "勝者なし" if not winners else "・".join(f"P{pid + 1}" for pid in winners) + " がライブ勝利"
            return f"最終結果　P1 {scores[0]} − {scores[1]} P2 ／ {who}。NEXTで成功ライブ移動へ進みます。"
        if step == "PICK_SUCCESS":
            return "ライブに勝利したプレイヤーが成功ライブカード置き場へ移すカードを決定します。"
        if step == "CLEANUP":
            return "残りのライブカードとエール公開カードを控え室へ移し、次の先攻を決定します。"
        return "ライブ勝敗判定を処理中です。"

    def state(self) -> Dict[str, Any]:
        with self.lock:
            self._sync_metadata_to_views()
            out = self.engine.to_dict()
            out["history_depth"] = len(self.history)
            out["judgment_message"] = self._judgment_ui_message()
            out["players_by_key"] = {
                "p1": {"label": self.players["p1"].label, "deck_code": self.players["p1"].app.deck_code},
                "p2": {"label": self.players["p2"].label, "deck_code": self.players["p2"].app.deck_code},
            }
            out["active_player_key"] = "p1" if out["active_player_id"] == 0 else "p2"
            if out.get("phase") == "GAME_OVER":
                result = str(out.get("game_result") or "対戦終了")
                winner = out.get("winner_player_id")
                if winner == 0:
                    message = f"プレイヤー1の勝利 / {result}"
                elif winner == 1:
                    message = f"プレイヤー2の勝利 / {result}"
                elif result == "DRAW":
                    message = "引き分け / DRAW"
                else:
                    message = result
                out["game_over_message"] = message
            else:
                out["game_over_message"] = ""
            return out

    def player_state(self, key: str, mode: str) -> Dict[str, Any]:
        with self.lock:
            self._sync_metadata_to_views()
            rt = self.runtime(key)
            self._suppress_reopened_yell_notice(rt)
            raw = rt.app.state_json()
            raw = self._sanitize_acknowledged_yell_state(
                rt, raw if isinstance(raw, dict) else {}
            )
            view = make_view_state(raw, mode)
            return self._decorate_player_state(
                rt, view if isinstance(view, dict) else {}
            )

    def _full_state_with_error(self, rt: PlayerViewRuntime, message: str) -> Dict[str, Any]:
        try:
            rt.app.gs.log.append(f"[DUAL][BLOCK] {message}")
        except Exception:
            pass
        self._suppress_reopened_yell_notice(rt)
        raw = rt.app.state_json()
        out = self._decorate_player_state(
            rt, raw if isinstance(raw, dict) else {}
        )
        out["dual_command_error"] = message
        return out

    def _guard_after_legacy_command(self, rt: PlayerViewRuntime, before: Dict[str, Any]) -> bool:
        """Block a legacy success-store/cleanup branch created by any UI command."""
        phase = self.engine.state.phase
        if phase not in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND, Phase.LIVE_JUDGMENT}:
            return False
        legacy_phase = str(getattr(rt.app.gs, "phase", "") or "").strip().upper()
        boundary = self._has_single_player_success_prompt(rt) or legacy_phase in {"MAIN", "ACTIVE", "ENERGY", "DRAW"}
        if phase in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND}:
            boundary = boundary or legacy_phase == "LIVE_RESOLVE"
        if not boundary:
            return False
        if (
            phase in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND}
            and getattr(rt.app, "_dual_live_attempt_succeeded", None) is None
        ):
            self._record_live_attempt_outcome(
                rt, bool(list(getattr(rt.app.gs, "set_zone", []) or []))
            )
        self._normalize_legacy_success_boundary(
            rt,
            live_before=list(before.get("live", []) or []),
            success_before=list(before.get("success", []) or []),
            resolve_before=list(before.get("resolve", []) or []),
            green_before=list(before.get("green", []) or []),
        )
        remaining = list(getattr(rt.app.gs, "pending", []) or [])
        if phase in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND}:
            if remaining:
                setattr(rt.app, "_dual_performance_exit_pending", True)
            else:
                self._complete_active_performance(rt)
        elif phase == Phase.LIVE_JUDGMENT:
            if not remaining:
                setattr(rt.app, "_dual_success_runtime_done", True)
                rt.app.gs.phase = "DUAL_JUDGMENT"
        return True

    def player_command(self, key: str, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a board action as one match transaction.

        Rejected commands return a complete board-state payload, never a small
        error object.  This prevents the legacy client from replacing `st` with
        an error dictionary and rendering Turn/Phase as undefined.
        """
        with self.lock:
            self._sync_metadata_to_views()
            rt = self.runtime(key)
            cmd = str(name or "").strip()
            payload = payload if isinstance(payload, dict) else {}
            active_rt = self._active_runtime()
            print(
                f"[DUAL V2 PLAYER CMD] key={key} cmd={cmd} "
                f"phase={self.engine.state.phase.value} payload={payload}"
            )
            yell_ack_command = cmd == "ack_yell_reveal"
            # During dual judgment, YELL confirmation is presentation-only.
            # Never send this command back through the one-player LIVE_RESOLVE
            # machine: its fallback handler can acknowledge the log entry while
            # immediately deriving the same popup again from judgment state.
            # Mark it acknowledged in the dual adapter and return a sanitized
            # full state for both active and inactive players.
            if yell_ack_command and self.engine.state.phase == Phase.LIVE_JUDGMENT:
                self._acknowledge_yell_notice(rt, source="judgment-confirm-button")
                self._sync_metadata_to_views()
                raw = rt.app.state_json()
                out = self._decorate_player_state(
                    rt, raw if isinstance(raw, dict) else {}
                )
                self.engine.state.log.append(
                    f"[YELL ACK CLOSE][P{rt.player_id + 1}] direct dual-judgment close"
                )
                out["dual_transaction_committed"] = True
                out["dual_presentation_acknowledged"] = True
                out["dual_force_close_yell_notice"] = True
                return out
            # A stale presentation-only YELL popup can belong to the player who
            # is no longer the judgment-active runtime.  Let that player close
            # the popup locally instead of forcing them to wait for the other
            # player's success effects to finish.  Do not run the inactive
            # legacy App's phase machine.
            if rt.key != active_rt.key and yell_ack_command:
                self._acknowledge_yell_notice(rt, source="inactive-confirm-button")
                self._sync_metadata_to_views()
                raw = rt.app.state_json()
                out = self._decorate_player_state(
                    rt, raw if isinstance(raw, dict) else {}
                )
                out["dual_transaction_committed"] = True
                out["dual_presentation_acknowledged"] = True
                out["dual_force_close_yell_notice"] = True
                return out
            if rt.key != active_rt.key:
                return self._full_state_with_error(rt, "現在の処理プレイヤーではありません")
            if cmd in self._CENTRAL_ONLY_COMMANDS:
                return self._full_state_with_error(rt, "この操作は中央の対戦操作ボタンで行います")

            phase = self.engine.state.phase
            allowed = set(self._GENERAL_EFFECT_COMMANDS)
            if phase in {Phase.MAIN_FIRST, Phase.MAIN_SECOND}:
                allowed |= self._MAIN_COMMANDS
            if cmd not in allowed:
                return self._full_state_with_error(
                    rt, f"{phase.value} では {cmd or '(empty)'} を実行できません"
                )

            # An unqualified legacy NEXT must not end the match phase.  It is
            # accepted only while the App itself has a pending effect/notice.
            if cmd == "next" and not self._has_legacy_dialog(rt):
                return self._full_state_with_error(
                    rt, "フェイズ終了は中央のボタンで行います"
                )

            dual_deck_top_out = self._handle_dual_opponent_deck_pending(rt, cmd, payload)
            if dual_deck_top_out is not None:
                return dual_deck_top_out
            dual_hand_out = self._handle_dual_opponent_hand_pending(rt, cmd, payload)
            if dual_hand_out is not None:
                return dual_hand_out
            dual_random_reveal_out = self._handle_dual_opponent_random_reveal_pending(rt, cmd, payload)
            if dual_random_reveal_out is not None:
                return dual_random_reveal_out
            dual_position_out = self._handle_dual_opponent_position_pending(rt, cmd, payload)
            if dual_position_out is not None:
                return dual_position_out

            self._push_history()
            try:
                boundary_before = self._capture_live_boundary(rt)
                setattr(rt.app, "_dual_last_boundary_snapshot", copy.deepcopy(boundary_before))
                yell_notice_before = self._active_yell_notice_names(rt)
                opponent_wait_request = self._capture_opponent_wait_request(rt, cmd, payload)
                opponent_energy_wait_request = self._capture_opponent_energy_wait_request(rt, cmd, payload)
                opponent_draw_request = self._capture_opponent_draw_request(rt, cmd, payload)
                opponent_green_bottom_request = (
                    self._capture_choose_opponent_green_bottom_request(rt, cmd, payload)
                    or self._capture_opponent_mass_green_bottom_request(rt, cmd, payload)
                )
                opponent_deck_top_request = self._capture_choose_opponent_deck_top_request(rt, cmd, payload)
                opponent_hand_discard_request = self._capture_opponent_hand_discard_request(rt, cmd, payload)
                favorite_side_effect = self._capture_favorite_answer_side_effect(rt, cmd, payload)
                opponent_position_request = self._capture_opponent_position_request(rt, cmd, payload)
                out = rt.app.cmd(cmd, payload)
                self._apply_opponent_wait_request(rt, opponent_wait_request)
                self._apply_opponent_energy_wait_request(rt, opponent_energy_wait_request)
                self._apply_opponent_draw_request(rt, opponent_draw_request)
                self._apply_opponent_green_bottom_request(rt, opponent_green_bottom_request)
                self._install_opponent_deck_top_pending(rt, opponent_deck_top_request)
                self._install_opponent_hand_discard_pending(
                    rt,
                    n=int((opponent_hand_discard_request or {}).get("n", 0) or 0),
                    kind=str((opponent_hand_discard_request or {}).get("kind", "ANY") or "ANY"),
                    source_cn=str((opponent_hand_discard_request or {}).get("source_cn", "") or ""),
                )
                self._apply_favorite_answer_side_effect(rt, favorite_side_effect)
                self._install_opponent_position_pending(rt, opponent_position_request)
                if yell_ack_command or (cmd == "next" and yell_notice_before):
                    self._acknowledge_yell_notice(
                        rt,
                        source="confirm-button" if yell_ack_command else "board-next",
                    )
                else:
                    self._suppress_reopened_yell_notice(rt)
                self._guard_after_legacy_command(rt, boundary_before)
                self._suppress_reopened_yell_notice(rt)
                self._sync_view_to_core(rt)
                self.engine._assert_invariants()
                self._sync_metadata_to_views()
                # Re-read after metadata/opponent synchronization and sanitize
                # presentation flags before returning them to the embedded UI.
                raw = rt.app.state_json()
                out = self._decorate_player_state(
                    rt, raw if isinstance(raw, dict) else {}
                )
                out["dual_transaction_committed"] = True
                if yell_ack_command:
                    out["dual_presentation_acknowledged"] = True
                    out["dual_force_close_yell_notice"] = True
                return out
            except Exception as exc:
                self._discard_failed_history()
                msg = f"{type(exc).__name__}: {exc}"
                print(f"[DUAL V2 PLAYER CMD][ERR] {msg}")
                return self._full_state_with_error(rt, msg)

    def action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            a = str(action or "").upper()
            payload = payload if isinstance(payload, dict) else {}
            print(f"[DUAL V2 ACTION] action={a} phase={self.engine.state.phase.value} payload={payload}")
            if a == "UNDO":
                if not self.history:
                    raise ValueError("戻せる操作がありません")
                snap = self.history.pop()
                self._restore_snapshot(snap)
                return {"ok": True, "state": self.state()}

            if a != "NEXT":
                raise ValueError(f"unsupported action: {action}")
            if self.engine.state.phase == Phase.GAME_OVER:
                raise ValueError("対戦は終了しています")

            expected_phase = str(payload.get("expected_phase", "") or "").strip()
            expected_key = str(payload.get("expected_active_player_key", "") or "").strip()
            current_key = "p1" if self.engine.active_player_id() == 0 else "p2"
            if expected_phase and expected_phase != self.engine.state.phase.value:
                raise ValueError(
                    f"画面のフェイズが更新前です: expected={expected_phase} current={self.engine.state.phase.value}"
                )
            if expected_key and expected_key != current_key:
                raise ValueError(
                    f"操作プレイヤーが更新前です: expected={expected_key} current={current_key}"
                )

            # Suppress already-acknowledged YELL presentation notices for both
            # players before choosing which runtime owns this NEXT.  Otherwise a
            # stale P1 popup can remain visible while judgment_active_player_id
            # points at P2 and cannot be closed until P2 finishes.
            for runtime in self.players.values():
                self._suppress_reopened_yell_notice(runtime)

            # Intercept the one-player success-store boundary before generic
            # dialog acknowledgement can accidentally choose "skip" and run its
            # cleanup/next-turn code.
            active_rt = self._active_runtime()
            active_pending = list(getattr(active_rt.app.gs, "pending", []) or [])
            legacy_boundary_now = (
                self._has_single_player_success_prompt(active_rt)
                or (
                    self.engine.state.phase in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND}
                    and not active_pending
                    and self._at_dual_success_boundary(active_rt, include_live_resolve=True)
                )
            )
            if legacy_boundary_now and self.engine.state.phase in {
                Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND, Phase.LIVE_JUDGMENT
            }:
                self._push_history()
                try:
                    before = getattr(active_rt.app, "_dual_last_boundary_snapshot", None) or self._capture_live_boundary(active_rt)
                    self._guard_after_legacy_command(active_rt, before)
                    self._sync_core_to_views(include_zones=True)
                    return {
                        "ok": True,
                        "state": self.state(),
                        "clear_selected_hand": False,
                        "legacy_success_boundary_blocked": True,
                    }
                except Exception:
                    self._discard_failed_history()
                    raise

            # Confirmation/notice/pending always consumes the central NEXT
            # before any match phase or judgment step can advance.
            if self._has_legacy_dialog(active_rt):
                self._push_history()
                try:
                    self._advance_active_legacy_dialog()
                    self._sync_core_to_views(include_zones=True)
                    return {
                        "ok": True,
                        "state": self.state(),
                        "clear_selected_hand": False,
                        "dialog_acknowledged": True,
                    }
                except Exception:
                    self._discard_failed_history()
                    raise

            self._push_history()
            clear_selected_hand = False
            try:
                phase = self.engine.state.phase
                if phase in {Phase.MULLIGAN_FIRST, Phase.MULLIGAN_SECOND}:
                    pid = self.engine.active_player_id()
                    indices = self._clean_hand_indices(payload)
                    self.engine.mulligan(pid, indices, record_history=False)
                    clear_selected_hand = True
                elif phase in {Phase.LIVE_SET_FIRST, Phase.LIVE_SET_SECOND}:
                    _advanced, clear_selected_hand = self._commit_active_live_set(payload)
                elif phase in {Phase.PERFORMANCE_FIRST, Phase.PERFORMANCE_SECOND}:
                    self._run_active_performance_step()
                elif phase == Phase.LIVE_JUDGMENT:
                    self._run_dual_judgment_step(payload)
                elif phase == Phase.TURN_END:
                    self.engine.finish_turn(record_history=False)
                else:
                    self._sync_all_views_to_core()
                    self.engine.advance(record_history=False)
                self._sync_core_to_views(include_zones=True)
                return {
                    "ok": True,
                    "state": self.state(),
                    "clear_selected_hand": clear_selected_hand,
                }
            except Exception:
                self._discard_failed_history()
                raise


def _scoped_single_html(prefix: str, *, upper: bool, label: str, color: str) -> str:
    html = SINGLE_HTML
    html = html.replace('src="/playmat"', f'src="/{prefix}/playmat"')
    html = html.replace("'/llocg_db_out_full/card_images/texticons/", f"'/{prefix}/llocg_db_out_full/card_images/texticons/")
    html = html.replace("`/img?cn=", f"`/{prefix}/img?cn=")
    html = html.replace("/cardinfo?cn=", f"/{prefix}/cardinfo?cn=")
    html = html.replace("const url = IS_PUBLIC_VIEW ? '/state?view=public' : '/state';", f"const url = IS_PUBLIC_VIEW ? '/{prefix}/state?view=public' : '/{prefix}/state';")
    html = html.replace("fetch('/cmd',", f"fetch('/{prefix}/cmd',")
    html = html.replace('<title>LLCG Manual UI</title>', f'<title>{label} | LLCG Dual v2</title>')
    html = html.replace('<body>', f'<body class="dualPlayerView {"dualUpper" if upper else "dualLower"}">')
    # Export the legacy UI's lexical `selHand` from inside the SAME script
    # where it is declared. A separate appended <script> cannot access a
    # top-level `let selHand`, which previously made every central NEXT send
    # indices=[] even when the hand showed selected cards.
    clear_sel_src = "function clearSel(){ selHand = []; updateTop(); render(); }"
    clear_sel_bridge = """function clearSel(){ selHand = []; updateTop(); render(); }
  window.dualGetSelectedHand = function(){ return Array.isArray(selHand) ? selHand.slice() : []; };
  window.dualClearSelectedHand = function(){ clearSel(); };
  let dualYellAckEpoch = '';
  function dualYellEpoch(state){
    const s = state && typeof state === 'object' ? state : {};
    const cards = Array.isArray(s.yell_revealed_cards) ? s.yell_revealed_cards
      : (Array.isArray(s.resolve_zone) ? s.resolve_zone : []);
    return String(s.turn ?? '') + '|' + JSON.stringify(cards);
  }
  function dualIsYellNoticeKey(key){
    const low=String(key||'').toLowerCase();
    if(!(low.includes('yell')||low.includes('エール'))) return false;
    return ['notice','popup','modal','confirm','ack','open','pending','show','確認'].some(t=>low.includes(t));
  }
  function dualPendingText(value){ try{return JSON.stringify(value).toLowerCase()}catch(e){return String(value||'').toLowerCase()} }
  function dualIsYellConfirmPending(value){
    const text=dualPendingText(value);
    return (text.includes('yell')||text.includes('エール'))
      && ['reveal','公開','confirm','確認','notice','popup','表示'].some(t=>text.includes(t))
      && !text.includes('live_success') && !text.includes('ライブ成功時');
  }
  function dualScrubYellNotice(value){
    if(Array.isArray(value)){
      for(let i=value.length-1;i>=0;i--){
        if(dualIsYellConfirmPending(value[i])) value.splice(i,1);
        else dualScrubYellNotice(value[i]);
      }
      return;
    }
    if(!value||typeof value!=='object') return;
    for(const key of Object.keys(value)){
      const child=value[key];
      if(dualIsYellNoticeKey(key)){
        if(Array.isArray(child)) value[key]=child.filter(x=>!dualIsYellConfirmPending(x));
        else value[key]=false;
      } else dualScrubYellNotice(child);
    }
    if(Array.isArray(value.pending)) value.pending=value.pending.filter(x=>!dualIsYellConfirmPending(x));
  }
  window.dualScrubCurrentYellNotice = function(){
    const persistent=Boolean(st&&st.dual_yell_notice_acknowledged);
    if(persistent&&!dualYellAckEpoch) dualYellAckEpoch=dualYellEpoch(st);
    if(!dualYellAckEpoch) return false;
    const current=dualYellEpoch(st);
    if(current!==dualYellAckEpoch&&!persistent){ dualYellAckEpoch=''; return false; }
    dualScrubYellNotice(st);
    return true;
  };
  window.dualApplyCommandState = function(nextState){
    if(nextState && typeof nextState==='object') st=nextState;
    if(nextState && (nextState.dual_force_close_yell_notice||nextState.dual_yell_notice_acknowledged)){
      dualYellAckEpoch=dualYellEpoch(st);
      dualScrubYellNotice(st);
    }
    updateTop();
    render();
    return true;
  };
  window.dualRefreshFromServer = async function(options){
    const opts = options && typeof options === 'object' ? options : {};
    const keepSelection = Array.isArray(selHand) ? selHand.slice() : [];
    const result = await refreshStateFromServer({force:true});
    if(typeof window.dualScrubCurrentYellNotice==='function') window.dualScrubCurrentYellNotice();
    if(opts.preserveSelection !== false){
      const handLen = (typeof st !== 'undefined' && st && Array.isArray(st.hand)) ? st.hand.length : Number.MAX_SAFE_INTEGER;
      selHand = keepSelection.filter(i => Number.isInteger(Number(i)) && Number(i) >= 0 && Number(i) < handLen).map(Number);
      updateTop();
      render();
    }
    return result;
  };"""
    if clear_sel_src not in html:
        raise RuntimeError('legacy clearSel hook not found; cannot expose mulligan selection')
    html = html.replace(clear_sel_src, clear_sel_bridge, 1)
    # Embedded boards are refreshed by central actions and board-command events.
    # Do not add a periodic full-state refresh here: it destroys transient hand
    # selection and log-scroll state.
    poll_pattern = re.compile(
        r"(?P<head>\s*if\s*\(\s*IS_PUBLIC_VIEW\s*\)\s*\{\s*)"
        r"setInterval\s*\(\s*\(\)\s*=>\s*\{\s*refreshStateFromServer\s*\(\s*\{\s*force\s*:\s*false\s*\}\s*\)\s*;\s*\}\s*,\s*\d+\s*\)\s*;\s*"
        r"(?P<tail>window\.addEventListener\s*\(\s*['\"]storage['\"]\s*,\s*\(ev\)\s*=>\s*\{)",
        re.M,
    )
    # Embedded dual boards are event-driven. Enabling the legacy polling loop
    # rebuilds transient selections, log position, and acknowledged popups.
    # Remove the 250 ms loop from both embedded private/public board variants.
    match = poll_pattern.search(html)
    if not match:
        raise RuntimeError('legacy public polling block not found')
    poll_new = (
        match.group("head")
        + "// Dual embedded boards are refreshed only by central actions or board commands.\n"
        + match.group("tail")
    )
    html = html[:match.start()] + poll_new + html[match.end():]
    injected = f'''<style>
body.dualPlayerView{{--dualLabelW:178px}}
body.dualPlayerView::before{{content:{json.dumps(label, ensure_ascii=False)};position:fixed;left:12px;top:10px;z-index:50000;box-sizing:border-box;width:var(--dualLabelW);max-width:calc(100vw - 24px);padding:7px 12px;border-radius:999px;background:{color};color:#fff;font-size:14px;line-height:1.15;font-weight:900;box-shadow:0 3px 14px rgba(0,0,0,.55);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:center}}
body.dualUpper #zones{{transform:rotate(180deg);transform-origin:50% 50%}}
body.dualUpper #zones>.zone{{transform:rotate(180deg);transform-origin:50% 50%}}
body.dualPlayerView .energyUI button{{position:absolute!important;width:1px!important;height:1px!important;opacity:0!important;pointer-events:none!important;overflow:hidden!important}}
body.dualPlayerView #topBar .oppWaitPill{{display:none!important}}
body.dualPlayerView #topBar{{padding-left:calc(var(--dualLabelW) + 14px);max-width:calc(100% - var(--dualLabelW) - 24px);box-sizing:border-box}}
@media (max-width: 760px){{body.dualPlayerView{{--dualLabelW:150px}}body.dualPlayerView::before{{font-size:12px;padding-left:9px;padding-right:9px}}body.dualPlayerView #topBar{{padding-left:calc(var(--dualLabelW) + 10px)}}}}
html,body{{overflow:hidden}}
</style>'''
    html = html.replace('</head>', injected + '</head>')
    log_pin_script = rf'''<script>
(function(){{
  const SOURCE={json.dumps(prefix)};
  const scrollMemory=new Map();
  let restoring=false;

  function looksLikeLog(el){{
    if(!el || !(el instanceof HTMLElement)) return false;
    const sig=((el.id||'')+' '+(typeof el.className==='string'?el.className:'')).toLowerCase();
    if(/(?:^|[\s_-])(?:log|logs|history)(?:[\s_-]|$)|gamelog|logbox|logpanel/.test(sig)) return true;
    const style=getComputedStyle(el);
    const scrollable=/(auto|scroll)/.test(style.overflowY||'') && el.clientHeight>0 && el.clientHeight<=460;
    if(!scrollable && !/^(PRE|TEXTAREA)$/.test(el.tagName)) return false;
    const text=(el.textContent||'').slice(-3000);
    return /\[(?:PHASE|YELL|DRAW|ENERGY|PERFORMANCE|LIVE SET|MULLIGAN|DUAL|JUDGMENT|AUTO|ACT|COMPARE|DISPLAY|PENDING|ZONE|ACK|TURN_ORDER)\]/.test(text);
  }}
  function nearBottom(el){{ return el.scrollHeight-el.clientHeight-el.scrollTop<=28; }}
  function logEntries(){{
    const selectors=['#log','#logs','#logBox','#logPanel','#gameLog','.log','.logs','.logBox','.logPanel','.gameLog','pre','textarea','div'];
    const seen=new Set(), out=[];
    for(const sel of selectors){{
      for(const el of document.querySelectorAll(sel)){{
        if(seen.has(el)) continue; seen.add(el);
        if(!looksLikeLog(el)) continue;
        const sig=el.id ? '#'+el.id : (el.tagName+'.'+String(el.className||'').trim().replace(/\s+/g,'.'));
        out.push({{el,key:sig+'@'+out.length}});
      }}
    }}
    return out;
  }}
  function captureLogState(){{
    const snap=[];
    for(const item of logEntries()){{
      const old=scrollMemory.get(item.key);
      const follow=old ? Boolean(old.follow) : nearBottom(item.el);
      const row={{key:item.key,top:item.el.scrollTop,follow}};
      scrollMemory.set(item.key,row); snap.push(row);
    }}
    return snap;
  }}
  function restoreLogState(snapshot){{
    const byKey=new Map((snapshot||[]).map(x=>[x.key,x]));
    restoring=true;
    for(const item of logEntries()){{
      const saved=byKey.get(item.key)||scrollMemory.get(item.key)||{{top:0,follow:true}};
      if(saved.follow) item.el.scrollTop=item.el.scrollHeight;
      else item.el.scrollTop=Math.max(0,Math.min(Number(saved.top)||0,item.el.scrollHeight-item.el.clientHeight));
      scrollMemory.set(item.key,{{key:item.key,top:item.el.scrollTop,follow:Boolean(saved.follow)}});
    }}
    requestAnimationFrame(()=>{{restoring=false;}});
  }}
  function wrapRender(){{
    const fn=window.render;
    if(typeof fn!=='function'||fn.__dualPreserveLogScroll)return;
    function wrapped(){{
      const snapshot=captureLogState();
      try{{ if(typeof window.dualScrubCurrentYellNotice==='function') window.dualScrubCurrentYellNotice(); }}catch(e){{}}
      const out=fn.apply(this,arguments);
      requestAnimationFrame(()=>restoreLogState(snapshot));
      return out;
    }}
    wrapped.__dualPreserveLogScroll=true;
    window.render=wrapped;
  }}
  document.addEventListener('scroll',function(ev){{
    if(restoring)return;
    const el=ev.target;
    if(!looksLikeLog(el))return;
    for(const item of logEntries()){{
      if(item.el===el){{
        scrollMemory.set(item.key,{{key:item.key,top:el.scrollTop,follow:nearBottom(el)}});
        break;
      }}
    }}
  }},true);
  window.dualCaptureLogState=captureLogState;
  window.dualRestoreLogState=restoreLogState;

  const nativeFetch=window.fetch.bind(window);
  window.fetch=function(input,init){{
    const raw=(typeof input==='string')?input:(input&&input.url)||'';
    const isBoardCommand=/\/cmd(?:\?|$)/.test(String(raw));
    let commandName='';
    if(isBoardCommand&&init&&typeof init.body==='string'){{
      try{{commandName=String(JSON.parse(init.body).cmd||'')}}catch(e){{}}
    }}
    const promise=nativeFetch(input,init);
    if(isBoardCommand){{
      promise.then(resp=>{{
        if(resp&&resp.ok){{
          if(commandName==='ack_yell_reveal'){{
            resp.clone().json().then(data=>{{
              try{{ if(typeof window.dualApplyCommandState==='function') window.dualApplyCommandState(data); }}catch(e){{}}
            }}).catch(()=>{{}});
          }}
          setTimeout(()=>{{
            try{{ parent.postMessage({{type:'llocg-dual-board-command',source:SOURCE}},location.origin); }}catch(e){{}}
          }},0);
        }}
      }}).catch(()=>{{}});
    }}
    return promise;
  }};

  const start=function(){{
    wrapRender();
    requestAnimationFrame(()=>restoreLogState([]));
  }};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{{once:true}});else start();
}})();
</script>''' 
    return html.replace('</body>', log_pin_script + '</body>')


def _shell_html(*, cpu_ui: bool = False, cpu_auto_default: bool = False) -> str:
    title = "LLCG CPUオート2デッキ対戦 v2" if cpu_ui else "LLCG 2デッキ対戦 v2"
    cpu_controls = ""
    cpu_trace_panel = ""
    if cpu_ui:
        cpu_controls = '<div id="cpuMode"><button id="cpuP1" type="button">P1 CPU</button><button id="cpuP2" type="button">P2 CPU</button><button id="cpuAuto" type="button">自動</button></div><button id="cpuStep" type="button">CPU 1手</button>'
        cpu_trace_panel = '<div id="cpuTrace"><div id="cpuTraceHead"><strong>CPU判断ログ</strong><button id="cpuTraceClear" type="button">クリア</button></div><div id="cpuTraceList"></div></div>'
    cpu_ui_js = "true" if cpu_ui else "false"
    cpu_auto_default_js = "true" if (cpu_ui and cpu_auto_default) else "false"
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>
html,body{{height:100%;margin:0;background:#080a0e;color:#fff;font-family:system-ui,-apple-system,sans-serif;overflow:hidden}}
#shell{{height:100%;display:grid;grid-template-rows:1fr 74px 1fr}}.playerFrame{{width:100%;height:100%;border:0;background:#111}}
#divider{{position:relative;display:grid;grid-template-columns:minmax(150px,1fr) minmax(260px,1.35fr) minmax(390px,max-content);align-items:center;gap:12px;padding:0 14px;box-sizing:border-box;background:#151922;border-top:2px solid #343b4c;border-bottom:2px solid #343b4c;z-index:10;box-shadow:0 0 18px rgba(0,0,0,.6);overflow:hidden}}
#phaseBanner{{grid-column:2;grid-row:1;align-self:stretch;min-width:0;display:flex;flex-direction:column;justify-content:center;font-weight:950;font-size:23px;line-height:1.08;letter-spacing:.03em;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-shadow:0 2px 8px rgba(0,0,0,.75)}}
#phaseSub{{display:block;min-width:0;font-size:12px;font-weight:750;line-height:1.15;letter-spacing:0;margin-top:3px;opacity:.82;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
button{{border:1px solid rgba(255,255,255,.25);border-radius:8px;background:#2a3140;color:#fff;padding:7px 11px;font-weight:900;cursor:pointer;font-size:13px;line-height:1.15;white-space:nowrap}}button:hover{{background:#384258}}button:disabled{{opacity:.45;cursor:wait}}
#tag{{position:fixed;right:8px;top:4px;z-index:20;font-size:10px;color:#9aa4b5}}#controls{{grid-column:3;grid-row:1;justify-self:end;display:flex;align-items:center;gap:6px;min-width:0}}#controls form{{display:flex;margin:0}}
#next{{background:#276fca;min-width:108px}}#cpuStep{{background:#7659bd;min-width:86px}}#undo{{background:#555}}#save{{background:#2f7658}}#loadBtn{{background:#6a537c}}#cpuMode{{display:flex;align-items:center;gap:3px;padding:3px;border-radius:10px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14)}}#cpuMode button{{padding:5px 7px;font-size:11px;background:#303747;color:#dce5f2}}#cpuMode button.active{{background:#7b5fe0;color:#fff;border-color:rgba(255,255,255,.42)}}#cpuAuto.active{{background:#bd5f83}}#recordButtons{{position:fixed;right:14px;top:24px;z-index:65000;display:flex;align-items:center;gap:6px;padding:8px 9px;border-radius:13px;background:rgba(15,18,24,.84);border:1px solid rgba(255,255,255,.22);box-shadow:0 8px 26px rgba(0,0,0,.48);backdrop-filter:blur(6px)}}#recordButtons::before{{content:'RESET';font-size:10px;font-weight:900;letter-spacing:.06em;color:#d6deea;opacity:.88}}#recordButtons button{{padding-left:9px;padding-right:9px;background:#784358}}#recordButtons button:hover{{background:#934c64}}#error{{color:#ff8d8d}}#requestStatus{{grid-column:1;grid-row:1;justify-self:start;min-width:0;max-width:100%;font-size:11px;color:#aeb8ca;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
@media (max-width: 980px){{#divider{{grid-template-columns:minmax(80px,.6fr) minmax(160px,1fr) minmax(300px,max-content);gap:8px;padding:0 8px}}#phaseBanner{{font-size:20px}}button{{padding:6px 8px;font-size:12px}}#next{{min-width:92px}}}}
#gameOverNotice{{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:70000;display:none;min-width:min(620px,86vw);padding:22px 28px;border-radius:18px;background:rgba(22,27,38,.97);border:3px solid #ffd76b;box-shadow:0 18px 80px rgba(0,0,0,.78);text-align:center;font-weight:950}}
#gameOverTitle{{font-size:28px;margin-bottom:8px}}#gameOverBody{{font-size:18px;color:#f4ecd0}}
#judgmentOverlay{{position:fixed;inset:0;z-index:60000;background:rgba(3,5,9,.78);display:none;align-items:center;justify-content:center;padding:30px;box-sizing:border-box}}
#judgmentPanel{{width:min(900px,92vw);max-height:82vh;overflow:auto;background:#171c27;border:2px solid #4d5f7d;border-radius:18px;padding:22px;box-shadow:0 18px 70px rgba(0,0,0,.75)}}
#judgmentTitle{{font-size:24px;font-weight:950;text-align:center;margin-bottom:8px}}#judgmentMessage{{text-align:center;color:#d8e2f3;font-weight:750;margin-bottom:18px}}
#judgmentCards{{display:flex;flex-wrap:wrap;gap:16px;justify-content:center}}.judgmentCard{{width:150px;padding:10px;border-radius:14px;background:#252d3d;border:3px solid transparent;cursor:pointer;text-align:center;transition:.12s}}
.judgmentCard:hover{{background:#303b50}}.judgmentCard.selected{{border-color:#56a4ff;background:#213f69;box-shadow:0 0 0 3px rgba(86,164,255,.2)}}.judgmentCard img{{width:126px;height:176px;object-fit:contain;border-radius:8px;background:#080a0e}}.judgmentCard div{{font-size:12px;font-weight:850;word-break:break-all;margin-top:7px}}
#judgmentHint{{text-align:center;margin-top:16px;color:#ffdd84;font-weight:850}}
#judgmentNotice{{position:fixed;left:50%;top:50%;transform:translate(-50%,-112%);z-index:45000;display:none;max-width:min(920px,82vw);padding:12px 20px;border-radius:14px;background:rgba(21,28,42,.96);border:2px solid #6684b3;box-shadow:0 10px 40px rgba(0,0,0,.72);font-size:15px;font-weight:850;text-align:center;pointer-events:none}}
#cpuTrace{{position:fixed;left:12px;bottom:86px;z-index:50000;width:min(520px,46vw);max-height:28vh;display:flex;flex-direction:column;background:rgba(12,15,22,.9);border:1px solid rgba(255,255,255,.22);border-radius:12px;box-shadow:0 10px 36px rgba(0,0,0,.54);overflow:hidden;backdrop-filter:blur(6px)}}
#cpuTraceHead{{display:flex;align-items:center;gap:8px;padding:8px 10px;background:rgba(255,255,255,.08);font-size:12px}}#cpuTraceHead strong{{flex:1}}#cpuTraceHead button{{padding:4px 7px;font-size:11px;background:#394150}}
#cpuTraceList{{overflow:auto;padding:8px 10px;display:flex;flex-direction:column;gap:6px;font-size:11px;line-height:1.35;color:#dbe5f3}}.cpuTraceItem{{border-left:3px solid #7b5fe0;padding-left:8px}}.cpuTraceMeta{{color:#aeb8ca;font-weight:850}}.cpuTraceReason{{color:#f0e4b2}}.cpuTraceCards{{color:#c9d5e8;word-break:break-all}}
@media (max-width: 980px){{#cpuTrace{{width:min(480px,62vw);max-height:22vh;bottom:82px}}}}
</style></head><body><div id="tag">{BUILD_TAG}</div><div id="recordButtons"><button id="recordP1" type="button">P1勝利</button><button id="recordP2" type="button">P2勝利</button><button id="recordNG" type="button">No Game</button></div>{cpu_trace_panel}<div id="shell"><iframe id="p2frame" class="playerFrame" src="/p2/ui?upper=1"></iframe><div id="divider"><div id="phaseBanner">読み込み中</div><div id="requestStatus"></div><div id="controls"><form id="undoForm" method="post" action="/match_action_form"><input type="hidden" name="action" value="UNDO"><button id="undo" type="submit">UNDO</button></form><button id="save" type="button">中断保存</button><button id="loadBtn" type="button">再開読込</button>{cpu_controls}<input id="loadFile" type="file" accept="application/json,.json" hidden><form id="nextForm" method="post" action="/match_action_form"><input type="hidden" name="action" value="NEXT"><button id="next" type="submit">NEXT</button></form></div></div><iframe id="p1frame" class="playerFrame" src="/p1/ui"></iframe></div>
<div id="judgmentNotice"></div>
<div id="gameOverNotice"><div id="gameOverTitle">対戦終了</div><div id="gameOverBody"></div></div>
<div id="judgmentOverlay"><div id="judgmentPanel"><div id="judgmentTitle">成功ライブカードを選択</div><div id="judgmentMessage"></div><div id="judgmentCards"></div><div id="judgmentHint">カードを1枚選択して、中央の「成功ライブを決定」を押してください</div></div></div>
<script>
let S=null,busy=false,lastError='',requestSeq=0,selectedLiveIndex=null,promptKey='';
const CPU_UI={cpu_ui_js},CPU_AUTO_DEFAULT={cpu_auto_default_js};
let cpuPlayers={{p1:false,p2:false}},cpuAuto=false,cpuAutoTimer=0,cpuAutoEpoch=0,cpuTraceLog=[];
function activeFrame(){{return document.getElementById(S&&S.active_player_key==='p2'?'p2frame':'p1frame')}}
function status(t){{document.getElementById('requestStatus').textContent=t||''}}
function loadCpuPrefs(){{
  if(!CPU_UI){{cpuPlayers={{p1:false,p2:false}};cpuAuto=false;return}}
  try{{
    const saved=JSON.parse(localStorage.getItem('llocgDualCpuPrefs')||'{{}}');
    if(saved&&Object.prototype.hasOwnProperty.call(saved,'p1')){{
      cpuPlayers.p1=Boolean(saved.p1);cpuPlayers.p2=Boolean(saved.p2);cpuAuto=Boolean(saved.auto);
    }}else{{
      cpuPlayers={{p1:true,p2:true}};cpuAuto=CPU_AUTO_DEFAULT;
    }}
  }}catch(e){{cpuPlayers={{p1:true,p2:true}};cpuAuto=CPU_AUTO_DEFAULT}}
}}
function saveCpuPrefs(){{if(!CPU_UI)return;try{{localStorage.setItem('llocgDualCpuPrefs',JSON.stringify({{p1:cpuPlayers.p1,p2:cpuPlayers.p2,auto:cpuAuto}}))}}catch(e){{}}}}
function updateCpuButtons(){{
  if(!CPU_UI)return;
  const p1=document.getElementById('cpuP1'),p2=document.getElementById('cpuP2'),auto=document.getElementById('cpuAuto');
  if(p1)p1.classList.toggle('active',Boolean(cpuPlayers.p1));
  if(p2)p2.classList.toggle('active',Boolean(cpuPlayers.p2));
  if(auto)auto.classList.toggle('active',Boolean(cpuAuto));
}}
function cpuBlockedByPrompt(){{
  return Boolean(S&&S.judgment_prompt&&S.judgment_prompt.kind==='pick_success_live'&&selectedLiveIndex===null);
}}
function activePlayerIsCpu(){{
  const key=S&&S.active_player_key==='p2'?'p2':'p1';
  return Boolean(cpuPlayers[key]);
}}
function scheduleCpuAuto(){{
  clearTimeout(cpuAutoTimer);
  if(!CPU_UI||!cpuAuto||busy||!S||S.phase==='GAME_OVER'||cpuBlockedByPrompt()||!activePlayerIsCpu())return;
  const epoch=++cpuAutoEpoch;
  cpuAutoTimer=setTimeout(()=>{{if(epoch===cpuAutoEpoch&&cpuAuto&&!busy&&S&&S.phase!=='GAME_OVER'&&!cpuBlockedByPrompt()&&activePlayerIsCpu())cpuStep({{auto:true}})}},720);
}}
async function refreshBoard(id,options={{}}){{try{{const fn=document.getElementById(id).contentWindow.dualRefreshFromServer;if(typeof fn==='function')return await Promise.resolve(fn(options))}}catch(e){{}}return null}}
async function refreshBoards(){{await Promise.allSettled(['p1frame','p2frame'].map(id=>refreshBoard(id,{{preserveSelection:true}})))}}
let boardEventTimer=0;
window.addEventListener('message',ev=>{{if(ev.origin!==location.origin||!ev.data||ev.data.type!=='llocg-dual-board-command')return;clearTimeout(boardEventTimer);boardEventTimer=setTimeout(async()=>{{await refresh();const other=ev.data.source==='p1'?'p2frame':'p1frame';await refreshBoard(other,{{preserveSelection:true}})}},40)}});
function renderJudgmentPrompt(){{
  const overlay=document.getElementById('judgmentOverlay');
  const notice=document.getElementById('judgmentNotice');
  const inJudgment=S&&S.phase==='LIVE_JUDGMENT';
  notice.textContent=inJudgment?(S.judgment_message||'ライブ勝敗判定を処理中です。'):'';
  notice.style.display=inJudgment?'block':'none';
  const prompt=S&&S.judgment_prompt&&S.judgment_prompt.kind==='pick_success_live'?S.judgment_prompt:null;
  if(!prompt){{overlay.style.display='none';selectedLiveIndex=null;promptKey='';return}}
  const key=JSON.stringify([prompt.player_id,(prompt.candidates||[]).map(x=>[x.index,x.cardnumber])]);
  if(key!==promptKey){{selectedLiveIndex=null;promptKey=key}}
  document.getElementById('judgmentMessage').textContent=prompt.message||'';
  const cards=document.getElementById('judgmentCards');cards.innerHTML='';
  for(const item of (prompt.candidates||[])){{
    const el=document.createElement('div');el.className='judgmentCard'+(selectedLiveIndex===Number(item.index)?' selected':'');
    const img=document.createElement('img');img.src=`/${{Number(prompt.player_id)===1?'p2':'p1'}}/img?cn=${{encodeURIComponent(item.cardnumber)}}`;img.alt=item.cardnumber;
    const label=document.createElement('div');label.textContent=item.cardnumber;
    el.appendChild(img);el.appendChild(label);el.addEventListener('click',()=>{{selectedLiveIndex=Number(item.index);renderJudgmentPrompt();updateButtons()}});cards.appendChild(el);
  }}
  overlay.style.display='flex';
}}
function renderGameOver(){{
  const box=document.getElementById('gameOverNotice');
  const body=document.getElementById('gameOverBody');
  if(!S||S.phase!=='GAME_OVER'){{box.style.display='none';return}}
  const result=S.game_result||'対戦終了';
  let winner='';
  if(S.winner_player_id===0)winner='プレイヤー1の勝利';
  else if(S.winner_player_id===1)winner='プレイヤー2の勝利';
  else if(result==='DRAW')winner='引き分け';
  body.textContent=S.game_over_message||(winner?winner+' / '+result:result);
  box.style.display='block';
}}
function updateButtons(){{
  const prompt=S&&S.judgment_prompt&&S.judgment_prompt.kind==='pick_success_live';
  document.getElementById('next').disabled=busy||Boolean(prompt&&selectedLiveIndex===null);
  document.getElementById('undo').disabled=busy||!S||S.history_depth===0;
  document.getElementById('save').disabled=busy||!S;
  document.getElementById('loadBtn').disabled=busy;
  const cpuStepEl=document.getElementById('cpuStep'),cpuP1El=document.getElementById('cpuP1'),cpuP2El=document.getElementById('cpuP2'),cpuAutoEl=document.getElementById('cpuAuto');
  if(cpuStepEl)cpuStepEl.disabled=busy||!S||S.phase==='GAME_OVER'||cpuBlockedByPrompt();
  if(cpuP1El)cpuP1El.disabled=busy;
  if(cpuP2El)cpuP2El.disabled=busy;
  if(cpuAutoEl)cpuAutoEl.disabled=busy;
  document.getElementById('recordP1').disabled=busy||!S;
  document.getElementById('recordP2').disabled=busy||!S;
  document.getElementById('recordNG').disabled=busy||!S;
  updateCpuButtons();
}}
async function refresh(prefetched=null){{
  S=prefetched||await(await fetch('/match_state',{{cache:'no-store'}})).json();
  const p=S.players_by_key[S.active_player_key]||{{label:'',deck_code:''}};
  const score=(S.phase==='LIVE_JUDGMENT'&&Array.isArray(S.live_scores))?`　P1 ${{S.live_scores[0]}} - ${{S.live_scores[1]}} P2`:'';
  const over=(S.phase==='GAME_OVER')?'対戦終了：'+(S.game_over_message||S.game_result||'完了'):'操作：'+p.label+'（'+p.deck_code+'）'+score;
  const sub=lastError?'<span id="error">'+lastError+'</span>':over;
  document.getElementById('phaseBanner').innerHTML=`${{S.turn>0?'Turn '+S.turn+'　':''}}${{S.phase_label}}<span id="phaseSub">${{sub}}</span>`;
  document.getElementById('next').textContent=S.action_label||'NEXT';
  renderJudgmentPrompt();renderGameOver();updateButtons();scheduleCpuAuto();
}}
async function saveSuspend(){{
  if(busy||!S)return;busy=true;status('中断データ作成中…');updateButtons();
  try{{
    const r=await fetch('/suspend_state',{{cache:'no-store'}});
    if(!r.ok)throw new Error(await r.text());
    const data=await r.json();
    const blob=new Blob([JSON.stringify(data,null,2)],{{type:'application/json'}});
    const a=document.createElement('a');
    const stamp=new Date().toISOString().replace(/[:.]/g,'').slice(0,15);
    a.href=URL.createObjectURL(blob);a.download=`llocg_dual_v2_suspend_${{stamp}}.json`;
    document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1200);
    status('中断データを保存しました');
  }}catch(e){{lastError=String(e.message||e);status('中断保存に失敗')}}
  finally{{busy=false;await refresh();updateButtons();scheduleCpuAuto()}}
}}
async function loadSuspendFile(file){{
  if(!file)return;busy=true;lastError='';status('中断データ読込中…');updateButtons();
  try{{
    const text=await file.text();
    const data=JSON.parse(text);
    const r=await fetch('/resume_state',{{method:'POST',cache:'no-store',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(data)}});
    const j=await r.json();
    if(!r.ok||!j.ok)throw new Error(j.error||'再開に失敗しました');
    await refresh(j.state);await refreshBoards();status('中断データから再開しました');
  }}catch(e){{lastError=String(e.message||e);status('再開読込に失敗');await refresh()}}
  finally{{busy=false;document.getElementById('loadFile').value='';updateButtons();scheduleCpuAuto()}}
}}
async function act(action){{
  if(busy)return false;busy=true;lastError='';const seq=++requestSeq;status('送信中… #'+seq);updateButtons();
  try{{
    let indices=[];const f=activeFrame();
    if(action==='NEXT'&&S&&(String(S.phase).startsWith('MULLIGAN')||String(S.phase).startsWith('LIVE_SET'))){{try{{const got=f.contentWindow.dualGetSelectedHand();indices=Array.isArray(got)?got:[]}}catch(e){{indices=[]}}}}
    const payload={{indices,expected_phase:S&&S.phase,expected_active_player_key:S&&S.active_player_key}};if(selectedLiveIndex!==null)payload.live_index=selectedLiveIndex;
    const r=await fetch('/match_action',{{method:'POST',cache:'no-store',headers:{{'Content-Type':'application/json','X-Dual-Request':String(seq)}},body:JSON.stringify({{action,payload}})}});
    const text=await r.text();let j;try{{j=JSON.parse(text)}}catch(e){{throw new Error('サーバー応答がJSONではありません: '+text.slice(0,120))}}
    if(!r.ok||!j.ok)throw new Error(j.error||'操作に失敗しました');
    try{{if(action==='NEXT'&&j.clear_selected_hand)f.contentWindow.dualClearSelectedHand()}}catch(e){{}}
    await refresh(j.state);await refreshBoards();status('完了 #'+seq+' / '+S.phase);return false;
  }}catch(e){{lastError=String(e.message||e);status('失敗 #'+seq);await refresh();await refreshBoards();return false}}
  finally{{busy=false;updateButtons();scheduleCpuAuto()}}
}}
function describeCpuSuggestion(s){{
  if(!s||typeof s!=='object')return 'CPU操作を実行しました';
  const card=s.card&&s.card.card_no?` / ${{s.card.name||s.card.card_no}}`:'';
  const kind=s.kind?String(s.kind):'action';
  const reason=s.reason?` / ${{s.reason}}`:'';
  return `CPU ${{kind}}${{card}}${{reason}}`;
}}
function cpuTraceCardText(s){{
  if(!s||typeof s!=='object')return '';
  const cards=Array.isArray(s.selected_cards)?s.selected_cards:[];
  const parts=[];
  if(s.card&&s.card.card_no)parts.push(`${{s.card.name||s.card.card_no}}${{s.card.cost!=null?' cost='+s.card.cost:''}}`);
  for(const card of cards){{if(card&&card.card_no)parts.push(`${{card.name||card.card_no}}${{card.kind?' / '+card.kind:''}}${{card.score!=null?' score='+card.score:''}}${{card.cost!=null?' cost='+card.cost:''}}`)}}
  return parts.join('、');
}}
function renderCpuTrace(){{
  if(!CPU_UI)return;
  const list=document.getElementById('cpuTraceList');
  if(!list)return;
  list.innerHTML='';
  if(!cpuTraceLog.length){{const empty=document.createElement('div');empty.className='cpuTraceMeta';empty.textContent='まだCPU操作はありません。';list.appendChild(empty);return}}
  for(const item of cpuTraceLog.slice(-24).reverse()){{
    const row=document.createElement('div');row.className='cpuTraceItem';
    const meta=document.createElement('div');meta.className='cpuTraceMeta';meta.textContent=`#${{item.seq}} ${{item.player}} / T${{item.turn||'?'}} / ${{item.phase||'?'}} / ${{item.kind||'?'}} / ${{item.confidence||'?'}}`;
    const reason=document.createElement('div');reason.className='cpuTraceReason';reason.textContent=item.reason||'';
    row.appendChild(meta);if(item.cards){{const cards=document.createElement('div');cards.className='cpuTraceCards';cards.textContent=item.cards;row.appendChild(cards)}}row.appendChild(reason);list.appendChild(row);
  }}
}}
function pushCpuTrace(s,seq){{
  if(!CPU_UI||!s||typeof s!=='object')return;
  cpuTraceLog.push({{
    seq,
    player:String(s.active_player_key||(S&&S.active_player_key)||'?').toUpperCase(),
    turn:s.turn,
    phase:s.phase||s.match_phase,
    kind:s.kind,
    confidence:s.confidence,
    reason:s.reason,
    cards:cpuTraceCardText(s),
  }});
  if(cpuTraceLog.length>80)cpuTraceLog=cpuTraceLog.slice(-80);
  renderCpuTrace();
}}
async function cpuStep(options={{}}){{
  if(busy)return;busy=true;lastError='';const seq=++requestSeq;status('CPU判断中… #'+seq);updateButtons();
  try{{
    const r=await fetch('/cpu_action',{{method:'POST',cache:'no-store',headers:{{'Content-Type':'application/json','X-Dual-Request':String(seq)}},body:JSON.stringify({{max_turns:4}})}});
    const text=await r.text();let j;try{{j=JSON.parse(text)}}catch(e){{throw new Error('サーバー応答がJSONではありません: '+text.slice(0,120))}}
    if(!r.ok||!j.ok)throw new Error(j.error||'CPU操作に失敗しました');
    await refresh(j.state);await refreshBoards();pushCpuTrace(j.suggestion,seq);status(describeCpuSuggestion(j.suggestion));return false;
  }}catch(e){{lastError=String(e.message||e);status('CPU操作に失敗 #'+seq);await refresh();await refreshBoards();return false}}
  finally{{busy=false;updateButtons();scheduleCpuAuto()}}
}}
function toggleCpuPlayer(key){{if(!CPU_UI)return;cpuPlayers[key]=!cpuPlayers[key];saveCpuPrefs();updateButtons();scheduleCpuAuto()}}
function toggleCpuAuto(){{if(!CPU_UI)return;cpuAuto=!cpuAuto;saveCpuPrefs();updateButtons();status(cpuAuto?'CPU自動を開始':'CPU自動を停止');scheduleCpuAuto()}}
async function recordAndReset(result,label){{
  if(busy||!S)return;const msg=label+'として記録し、新しい対戦を開始します。よろしいですか？';
  if(!window.confirm(msg))return;busy=true;lastError='';status('勝敗を記録中…');updateButtons();
  try{{
    const r=await fetch('/match_record_reset',{{method:'POST',cache:'no-store',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{result}})}});
    const j=await r.json();
    if(!r.ok||!j.ok)throw new Error(j.error||'記録に失敗しました');
    await refresh(j.state);await refreshBoards();status('記録してリセットしました');
  }}catch(e){{lastError=String(e.message||e);status('記録リセットに失敗');await refresh();await refreshBoards()}}
  finally{{busy=false;updateButtons();scheduleCpuAuto()}}
}}
loadCpuPrefs();updateCpuButtons();
document.getElementById('nextForm').addEventListener('submit',e=>{{e.preventDefault();act('NEXT')}});document.getElementById('undoForm').addEventListener('submit',e=>{{e.preventDefault();act('UNDO')}});refresh();setInterval(()=>{{if(!busy&&!document.hidden)refresh()}},1000);
document.getElementById('save').addEventListener('click',saveSuspend);
document.getElementById('loadBtn').addEventListener('click',()=>document.getElementById('loadFile').click());
document.getElementById('loadFile').addEventListener('change',e=>loadSuspendFile(e.target.files&&e.target.files[0]));
if(document.getElementById('cpuStep'))document.getElementById('cpuStep').addEventListener('click',cpuStep);
if(document.getElementById('cpuP1'))document.getElementById('cpuP1').addEventListener('click',()=>toggleCpuPlayer('p1'));
if(document.getElementById('cpuP2'))document.getElementById('cpuP2').addEventListener('click',()=>toggleCpuPlayer('p2'));
if(document.getElementById('cpuAuto'))document.getElementById('cpuAuto').addEventListener('click',toggleCpuAuto);
if(document.getElementById('cpuTraceClear'))document.getElementById('cpuTraceClear').addEventListener('click',()=>{{cpuTraceLog=[];renderCpuTrace()}});
renderCpuTrace();
document.getElementById('recordP1').addEventListener('click',()=>recordAndReset('p1_win','P1勝利'));
document.getElementById('recordP2').addEventListener('click',()=>recordAndReset('p2_win','P2勝利'));
document.getElementById('recordNG').addEventListener('click',()=>recordAndReset('no_game','No Game'));
</script></body></html>'''


def _image_content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {'.jpg', '.jpeg'}:
        return 'image/jpeg'
    if suffix == '.webp':
        return 'image/webp'
    return 'image/png'


def _runtime_image_candidates(rt: PlayerViewRuntime, token: str) -> List[Path]:
    roots = []
    for root in (Path.cwd(), getattr(rt.app, 'root', None), getattr(rt.app, 'outdir', None)):
        try:
            p = Path(root)
        except Exception:
            continue
        if p not in roots:
            roots.append(p)
    try:
        project_root = Path(__file__).resolve().parents[1]
        if project_root not in roots:
            roots.append(project_root)
    except Exception:
        pass

    if token == '__BACK__':
        names = ('back.png', 'back.jpg', 'back.jpeg', 'back.webp', 'card_back.png', 'card_back.jpg', 'card_back.jpeg', 'card_back.webp')
        dirs = ('llocg_db_out_full/card_images', 'card_images', '')
    elif token == '__ENERGY__':
        names = ('energy.png', 'energy.jpg', 'energy.jpeg', 'energy.webp')
        dirs = ('llocg_db_out_full/card_images', 'card_images', 'llocg_db_out_full', '')
    else:
        names = ('NoImage.PNG', 'NoImage.png', 'noimage.png', 'noimage.PNG')
        dirs = ('llocg_db_out_full/card_images', 'card_images', '')

    cands: List[Path] = []
    for root in roots:
        for rel_dir in dirs:
            base = root / rel_dir if rel_dir else root
            for name in names:
                p = base / name
                if p not in cands:
                    cands.append(p)
    return cands


def _transparent_png_bytes() -> bytes:
    return bytes.fromhex(
        '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489'
        '0000000a49444154789c6360000002000154a24f5d0000000049454e44ae426082'
    )


def _first_existing_file(paths: List[Path]) -> Optional[Path]:
    for p in paths:
        try:
            if p.is_file():
                return p
        except Exception:
            continue
    return None


def _find_runtime_card_image(rt: PlayerViewRuntime, cardnumber: str) -> Optional[Path]:
    try:
        finder = getattr(getattr(rt.app, 'img', None), 'find', None)
        if callable(finder):
            found = finder(cardnumber)
            if found:
                p = Path(found)
                if p.is_file():
                    return p
    except Exception:
        pass
    return _first_existing_file(_runtime_image_candidates(rt, 'NoImage'))


class Handler(BaseHTTPRequestHandler):
    adapter: LegacyUIAdapter
    verbose_http: bool = False
    cpu_ui: bool = False
    cpu_auto_default: bool = False

    def log_message(self, fmt: str, *args: Any) -> None:
        path = urlparse(getattr(self, "path", "")).path
        if not self.verbose_http and path in {"/match_state", "/p1/state", "/p2/state"}:
            return
        print("[DUAL V2 HTTP] " + (fmt % args))
    def _send(self, status: int, body: bytes, ctype: str) -> None:
        self.send_response(status); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store"); self.end_headers()
        if self.command != "HEAD": self.wfile.write(body)
    def _route_player(self, path: str):
        parts = path.lstrip('/').split('/', 1)
        if parts and parts[0] in self.adapter.players: return self.adapter.runtime(parts[0]), '/' + (parts[1] if len(parts) > 1 else '')
        return None, path
    def do_HEAD(self): self.do_GET()
    def do_GET(self):
        u = urlparse(self.path)
        if u.path in {'/', '/dual'}:
            return self._send(
                200,
                _shell_html(cpu_ui=self.cpu_ui, cpu_auto_default=self.cpu_auto_default).encode(),
                'text/html; charset=utf-8',
            )
        if u.path == '/match_state': return self._send(200, json.dumps(self.adapter.state(), ensure_ascii=False).encode(), 'application/json; charset=utf-8')
        if u.path == '/cpu_suggest':
            try:
                payload = self.adapter.cpu_action_suggestion()
                return self._send(200, json.dumps(payload, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
            except Exception as exc:
                return self._send(400, json.dumps({'ok': False, 'error': f'{type(exc).__name__}: {exc}'}, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
        if u.path == '/suspend_state':
            return self._send(
                200,
                json.dumps(self.adapter.export_suspend_data(), ensure_ascii=False).encode(),
                'application/json; charset=utf-8',
            )
        rt, sub = self._route_player(u.path)
        if rt is None: return self._send(404, b'not found', 'text/plain')
        if sub in {'/', '/ui'}:
            upper = parse_qs(u.query).get('upper', ['0'])[0] == '1'
            return self._send(200, _scoped_single_html(rt.key, upper=upper, label=rt.label, color=rt.color).encode(), 'text/html; charset=utf-8')
        if sub == '/state':
            mode = parse_qs(u.query).get('view', ['private'])[0]
            state = self.adapter.player_state(rt.key, mode)
            return self._send(200, json.dumps(state, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
        if sub == '/playmat':
            for p in [Path.cwd()/'playmat.jpg', rt.app.root/'playmat.jpg']:
                if p.is_file(): return self._send(200, p.read_bytes(), 'image/jpeg')
            return self._send(404, b'', 'text/plain')
        if sub == '/img':
            cn = parse_qs(u.query).get('cn', [''])[0]
            if cn == '__BACK__':
                p = _first_existing_file(_runtime_image_candidates(rt, '__BACK__'))
                if p:
                    return self._send(200, p.read_bytes(), _image_content_type(p))
            if cn == '__ENERGY__':
                p = _first_existing_file(_runtime_image_candidates(rt, '__ENERGY__'))
                if p:
                    return self._send(200, p.read_bytes(), _image_content_type(p))
                return self._send(200, _transparent_png_bytes(), 'image/png')
            p = _find_runtime_card_image(rt, cn)
            if p and p.exists():
                return self._send(200, p.read_bytes(), _image_content_type(p))
            return self._send(404, b'', 'text/plain')
        if sub == '/cardinfo':
            cn = parse_qs(u.query).get('cn', [''])[0]
            payload = self.adapter.card_info_payload(rt.key, cn)
            if payload is None:
                return self._send(404, b'{}', 'application/json')
            return self._send(
                200,
                json.dumps(payload, ensure_ascii=False).encode(),
                'application/json; charset=utf-8',
            )
        if sub.startswith('/llocg_db_out_full/card_images/texticons/'):
            fname = sub.rsplit('/', 1)[-1]
            for base in [rt.app.root/'card_images'/'texticons', rt.app.root/'llocg_db_out_full'/'card_images'/'texticons', Path.cwd()/'llocg_db_out_full'/'card_images'/'texticons']:
                p = base/fname
                if p.is_file(): return self._send(200, p.read_bytes(), 'image/png')
            return self._send(404, b'', 'text/plain')
        return self._send(404, b'not found', 'text/plain')
    def do_POST(self):
        u = urlparse(self.path); n = int(self.headers.get('Content-Length','0') or 0); raw = self.rfile.read(n) if n else b'{}'
        if u.path == '/match_action_form':
            form = parse_qs(raw.decode('utf-8', errors='replace'))
            action = str(form.get('action', [''])[0])
            try:
                self.adapter.action(action, {'indices': []})
                self.send_response(303); self.send_header('Location', '/'); self.send_header('Cache-Control', 'no-store'); self.end_headers(); return
            except Exception as exc:
                return self._send(400, f'{type(exc).__name__}: {exc}'.encode('utf-8'), 'text/plain; charset=utf-8')
        try: obj = json.loads(raw.decode())
        except Exception: obj = {}
        if u.path == '/resume_state':
            try:
                state = self.adapter.import_suspend_data(obj)
                return self._send(
                    200,
                    json.dumps({'ok': True, 'state': state}, ensure_ascii=False).encode(),
                    'application/json; charset=utf-8',
                )
            except Exception as exc:
                return self._send(
                    400,
                    json.dumps({'ok': False, 'error': f'{type(exc).__name__}: {exc}'}, ensure_ascii=False).encode(),
                    'application/json; charset=utf-8',
                )
        if u.path == '/match_action':
            try:
                out = self.adapter.action(str(obj.get('action','')), obj.get('payload') if isinstance(obj.get('payload'),dict) else {})
                return self._send(200, json.dumps(out, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
            except Exception as exc:
                return self._send(400, json.dumps({'ok':False,'error':f'{type(exc).__name__}: {exc}'}, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
        if u.path == '/match_record_reset':
            try:
                out = self.adapter.record_result_and_reset(str(obj.get('result', '') or ''))
                return self._send(200, json.dumps(out, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
            except Exception as exc:
                return self._send(400, json.dumps({'ok':False,'error':f'{type(exc).__name__}: {exc}'}, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
        if u.path == '/cpu_action':
            try:
                max_turns = int(obj.get('max_turns', 4) or 4)
                out = self.adapter.apply_cpu_action_suggestion(max_turns=max_turns)
                return self._send(200, json.dumps(out, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
            except Exception as exc:
                return self._send(400, json.dumps({'ok':False,'error':f'{type(exc).__name__}: {exc}'}, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
        rt, sub = self._route_player(u.path)
        if rt is not None and sub == '/cmd':
            cmd = str(obj.get('cmd', '') or '').strip()
            payload = obj.get('payload', {}) if isinstance(obj.get('payload'), dict) else {}
            out = self.adapter.player_command(rt.key, cmd, payload)
            return self._send(
                200,
                json.dumps(out, ensure_ascii=False).encode(),
                'application/json; charset=utf-8',
            )
        return self._send(404, b'not found', 'text/plain')


def serve(*, host: str, port: int, project_root: Path, data_root: Path, deck1: str, deck2: str, seed: int, debug: bool, preserve_start_env: bool, verbose_http: bool, cpu_ui: bool = False, cpu_auto_default: bool = False) -> None:
    engine = DualMatchEngine.from_codes(project_root, deck1, deck2, seed=seed, data_root=data_root)
    saved_env: Dict[str, str] = {}
    if not preserve_start_env:
        for key in list(os.environ):
            if key.startswith("LLOCG_START_") or key.startswith("LLOCG_DEBUG_"):
                saved_env[key] = os.environ.pop(key)
    try:
        p1_app = App(root=data_root, code='dual-v2-p1', deck_code=deck1, seed=seed, debug=debug)
        p2_app = App(root=data_root, code='dual-v2-p2', deck_code=deck2, seed=seed+1, debug=debug)
    finally:
        os.environ.update(saved_env)
    adapter = LegacyUIAdapter(engine, PlayerViewRuntime('p1',0,'プレイヤー1','#2578d4',p1_app), PlayerViewRuntime('p2',1,'プレイヤー2','#d96a22',p2_app))
    adapter.configure_reset(
        project_root=project_root,
        data_root=data_root,
        deck1=deck1,
        deck2=deck2,
        seed=seed,
        debug=debug,
        preserve_start_env=preserve_start_env,
    )
    Handler.adapter = adapter
    Handler.verbose_http = bool(verbose_http)
    Handler.cpu_ui = bool(cpu_ui)
    Handler.cpu_auto_default = bool(cpu_auto_default)
    httpd = ThreadingHTTPServer((host, int(port)), Handler)
    print(f'[LLCG DUAL V2] BUILD_TAG={BUILD_TAG}')
    print(f'[LLCG DUAL V2] project_root={project_root}')
    print(f'[LLCG DUAL V2] data_root={data_root}')
    print(f'[LLCG DUAL V2] http://{host}:{port}')
    httpd.serve_forever()


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--data-root', default='')
    ap.add_argument('--deck1', required=True)
    ap.add_argument('--deck2', required=True)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=8877)
    ap.add_argument('--debug', action='store_true')
    ap.add_argument('--preserve-start-env', action='store_true')
    ap.add_argument('--verbose-http', action='store_true', help='定期state取得を含むHTTPアクセスログを表示する')
    ap.add_argument('--cpu-ui', action='store_true', help='CPU操作用の2デッキUIを表示する')
    ap.add_argument('--cpu-auto-default', action='store_true', help='CPU UI初回表示時に両側CPU/自動を既定ONにする')
    ns = ap.parse_args(argv)
    project_root = Path(ns.root).expanduser().resolve()
    explicit = Path(ns.data_root).expanduser() if ns.data_root else None
    data_root = discover_data_root(project_root, explicit)
    serve(host=ns.host, port=ns.port, project_root=project_root, data_root=data_root, deck1=ns.deck1, deck2=ns.deck2, seed=ns.seed, debug=ns.debug, preserve_start_env=ns.preserve_start_env, verbose_http=ns.verbose_http, cpu_ui=ns.cpu_ui, cpu_auto_default=ns.cpu_auto_default)
    return 0
