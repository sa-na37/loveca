#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from llocg_ui.server import App
OUT = ROOT / "_codex_outputs" / "effect_full_audit_phase3_correction_20260716"
STATE_DIR = OUT / "regression" / "state"
LOG_DIR = OUT / "regression" / "logs"
CMD_DIR = OUT / "regression" / "commands"

RESET_KEYS = [
    "LLOCG_START_STAGE", "LLOCG_START_STAGE_L", "LLOCG_START_STAGE_C", "LLOCG_START_STAGE_R",
    "LLOCG_START_HAND", "LLOCG_START_HAND_SIZE", "LLOCG_START_SHUFFLE",
    "LLOCG_START_GREEN", "LLOCG_START_SUCCESS", "LLOCG_START_RESOLVE",
    "LLOCG_START_DECK_TOP", "LLOCG_START_DECK_EXACT", "LLOCG_START_DECK_EXACT_STRICT",
    "LLOCG_START_PHASE", "LLOCG_START_TURN",
    "LLOCG_START_ENERGY_ACTIVE", "LLOCG_START_ENERGY_WAIT", "LLOCG_START_OPPONENT_WAIT",
    "LLOCG_DEBUG_PRESET", "LLOCG_DEBUG_EFFECT_CARD", "LLOCG_START_DEBUG",
    "LLOCG_DEBUG_LIVE_IN_HAND", "LLOCG_DEBUG_MEMBER_IN_HAND",
]


def setup_env(card: str, opponent_wait: int = 0) -> None:
    for k in RESET_KEYS:
        os.environ.pop(k, None)
    os.environ.update({
        "LLOCG_DEBUG_PRESET": "effect",
        "LLOCG_START_PHASE": "MAIN",
        "LLOCG_START_TURN": "1",
        "LLOCG_START_DEBUG": "1",
        "LLOCG_DEBUG_EFFECT_CARD": card,
        "LLOCG_START_HAND_SIZE": "0",
        "LLOCG_START_ENERGY_ACTIVE": "20",
        "LLOCG_START_ENERGY_WAIT": "0",
        "LLOCG_DEBUG_LIVE_IN_HAND": "0",
        "LLOCG_DEBUG_MEMBER_IN_HAND": "0",
        "LLOCG_START_HAND": card,
        "LLOCG_START_DECK_EXACT_STRICT": "1",
        "LLOCG_START_DECK_EXACT": "LL-bp1-001,LL-bp5-001,LL-bp2-001,LL-bp3-001,LL-bp5-002",
        "LLOCG_START_OPPONENT_WAIT": str(opponent_wait),
    })


def new_app(card: str, opponent_wait: int = 0) -> App:
    setup_env(card, opponent_wait)
    return App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)


def save_state(name: str, st: Dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / f"{name}.json").write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def save_log(name: str, st: Dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = st.get("log", [])
    if isinstance(log, list):
        txt = "\n".join(str(x) for x in log)
    else:
        txt = str(log)
    (LOG_DIR / f"{name}.log").write_text(txt + "\n", encoding="utf-8")


def pending_kind(st: Dict[str, Any]) -> str:
    p = st.get("pending", [])
    if isinstance(p, list) and p and isinstance(p[0], dict):
        return str(p[0].get("kind", "") or "")
    return ""


def pending_text(st: Dict[str, Any]) -> str:
    p = st.get("pending", [])
    if isinstance(p, list) and p and isinstance(p[0], dict):
        return str(p[0].get("text", "") or "")
    return ""


def pending_options(st: Dict[str, Any]) -> List[str]:
    p = st.get("pending", [])
    if isinstance(p, list) and p and isinstance(p[0], dict):
        opts = p[0].get("options", [])
        if isinstance(opts, list):
            return [str(x) for x in opts]
    return []


def choose_by_fragment(app: App, fragment: str) -> Dict[str, Any]:
    st = app.state_json()
    p = st.get("pending", [])
    if not isinstance(p, list) or not p or not isinstance(p[0], dict):
        raise AssertionError("no pending to choose")
    effects = [str(x) for x in list(p[0].get("effects", []) or [])]
    idx = 0
    for i, eff in enumerate(effects):
        if fragment in eff:
            idx = i
            break
    return app.cmd("resolve_pending", {"idx": 0, "choice": str(idx)})


def clear_first_selectable_pending(app: App, limit: int = 8) -> Dict[str, Any]:
    st = app.state_json()
    for _ in range(limit):
        kind = pending_kind(st)
        if not kind:
            return st
        opts = pending_options(st)
        choice = ""
        if "skip" in [x.lower() for x in opts]:
            choice = "skip"
        elif opts:
            choice = opts[0]
        else:
            choice = "ok"
        st = app.cmd("resolve_pending", {"idx": 0, "choice": choice})
    return st


def run_required_pending() -> Tuple[str, Dict[str, Any]]:
    app = new_app("PL!-PR-005")
    save_state("required_00_initial", app.state_json())
    st = app.cmd("play", {"hand_idx": 0, "pos": "C"})
    save_state("required_01_triggered", st)
    st = app.cmd("next", {})
    save_state("required_02_next_without_choice", st)
    next_ok = (
        pending_kind(st) == "choose_enter_effect_mode"
        and "必須選択" in pending_text(st)
        and any("[BLOCK] next: choose_enter_effect_mode requires a choice" in str(x) for x in st.get("log", []))
    )
    st = app.cmd("resolve_pending", {"idx": 0, "choice": ""})
    save_state("required_03_invalid_empty_choice", st)
    invalid_ok = pending_kind(st) == "choose_enter_effect_mode" and "必須選択" in pending_text(st)
    st = choose_by_fragment(app, "カードを1枚引く")
    st = clear_first_selectable_pending(app)
    save_state("required_04_resolved_after_valid_choice", st)
    resolved_ok = pending_kind(st) == ""
    undo_st = app.cmd("undo", {})
    save_state("required_05_after_undo", undo_st)
    undo_ok = isinstance(undo_st, dict) and "phase" in undo_st
    save_log("required_pending", st)
    return ("PASS" if (next_ok and invalid_ok and resolved_ok and undo_ok) else "FAIL", {
        "next_blocked": next_ok,
        "invalid_kept_pending": invalid_ok,
        "valid_choice_resolved": resolved_ok,
        "undo_ok": undo_ok,
    })


def run_draw_discard(card: str) -> Tuple[str, Dict[str, Any]]:
    app = new_app(card)
    st = app.cmd("play", {"hand_idx": 0, "pos": "C"})
    save_state(f"{card.replace('!', '_').replace('-', '_')}_draw_01_triggered", st)
    st = choose_by_fragment(app, "カードを1枚引く")
    st = clear_first_selectable_pending(app)
    name = f"{card.replace('!', '_').replace('-', '_')}_draw_02_resolved"
    save_state(name, st)
    save_log(name, st)
    undo_st = app.cmd("undo", {})
    save_state(f"{name}_after_undo", undo_st)
    undo_ok = isinstance(undo_st, dict) and "phase" in undo_st
    ok = pending_kind(st) == "" and any("chose mode" in str(x) for x in st.get("log", [])) and undo_ok
    return ("PASS" if ok else "FAIL", {"pending_kind": pending_kind(st), "hand_count": len(st.get("hand", []) or []), "undo_ok": undo_ok})


def run_opponent_wait(initial: int) -> Tuple[str, Dict[str, Any]]:
    app = new_app("PL!-PR-005", opponent_wait=initial)
    st = app.cmd("play", {"hand_idx": 0, "pos": "C"})
    st = choose_by_fragment(app, "ウェイト")
    if pending_kind(st) == "opponent_wait_notify":
        st = app.cmd("resolve_pending", {"idx": 0, "choice": "2"})
    name = f"opponent_wait_initial{initial}_resolved"
    save_state(name, st)
    save_log(name, st)
    got = int(st.get("opponent_wait_count", -1))
    expected = max(0, min(3, initial + 2))
    undo_st = app.cmd("undo", {})
    save_state(f"{name}_after_undo", undo_st)
    undo_ok = isinstance(undo_st, dict) and "phase" in undo_st
    ok = got == expected and pending_kind(st) == "" and undo_ok
    return ("PASS" if ok else "FAIL", {"initial": initial, "expected": expected, "got": got, "pending_kind": pending_kind(st), "undo_ok": undo_ok})


def run_optional_synthetic(kind: str, opts: List[str], allow_skip: bool, optional: bool) -> Tuple[str, Dict[str, Any]]:
    app = new_app("PL!-PR-005")
    app.gs.pending = [{
        "kind": kind,
        "text": f"synthetic optional regression: {kind}",
        "options": opts,
        "allow_skip": allow_skip,
        "optional": optional,
    }]
    st = app.cmd("next", {})
    name = f"optional_{kind}_next"
    save_state(name, st)
    save_log(name, st)
    undo_st = app.cmd("undo", {})
    save_state(f"{name}_after_undo", undo_st)
    undo_ok = isinstance(undo_st, dict) and "phase" in undo_st
    ok = pending_kind(st) != "choose_enter_effect_mode" and "必須選択" not in pending_text(st) and undo_ok
    return ("PASS" if ok else "FAIL", {"pending_kind": pending_kind(st), "pending_text": pending_text(st), "undo_ok": undo_ok})


def main() -> int:
    rows: List[Dict[str, Any]] = []
    tests = [
        ("mandatory_choice_next_and_invalid", run_required_pending),
        ("PL!-PR-005_draw_discard", lambda: run_draw_discard("PL!-PR-005")),
        ("PL!-PR-006_draw_discard", lambda: run_draw_discard("PL!-PR-006")),
        ("PL!-PR-008_draw_discard", lambda: run_draw_discard("PL!-PR-008")),
        ("PL!-PR-005_opponent_wait_count0", lambda: run_opponent_wait(0)),
        ("PL!-PR-005_opponent_wait_count1", lambda: run_opponent_wait(1)),
        ("PL!-PR-005_opponent_wait_existing1_plus2", lambda: run_opponent_wait(1)),
        ("PL!-PR-005_opponent_wait_count2", lambda: run_opponent_wait(2)),
        ("optional_confirm_effect_skip", lambda: run_optional_synthetic("confirm_effect", ["skip"], True, True)),
        ("optional_pay_or_skip_next", lambda: run_optional_synthetic("pay_or_skip", ["pay", "skip"], False, False)),
    ]
    for name, fn in tests:
        try:
            status, details = fn()
        except Exception as exc:
            status, details = "FAIL", {"error": repr(exc)}
        row = {"test": name, "status": status, "details": json.dumps(details, ensure_ascii=False, sort_keys=True)}
        rows.append(row)

    CMD_DIR.mkdir(parents=True, exist_ok=True)
    with (CMD_DIR / "phase3_correction_regression_results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "status", "details"])
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
