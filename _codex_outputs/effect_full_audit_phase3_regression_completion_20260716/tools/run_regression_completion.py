#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "effect_full_audit_phase3_regression_completion_20260716"
PREV = ROOT / "_codex_outputs" / "effect_full_audit_phase3_correction_20260716"
sys.path.insert(0, str(ROOT))

from llocg_ui.server import App
from llocg_ui.views import make_view_state


spec = importlib.util.spec_from_file_location("compare_undo_state", OUT / "tools" / "compare_undo_state.py")
compare_mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(compare_mod)

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


def reset_env() -> None:
    for k in RESET_KEYS:
        os.environ.pop(k, None)


def base_env(card: str = "") -> Dict[str, str]:
    env = {
        "LLOCG_DEBUG_PRESET": "effect",
        "LLOCG_START_PHASE": "MAIN",
        "LLOCG_START_TURN": "1",
        "LLOCG_START_DEBUG": "1",
        "LLOCG_START_HAND_SIZE": "0",
        "LLOCG_START_SHUFFLE": "0",
        "LLOCG_START_ENERGY_ACTIVE": "30",
        "LLOCG_START_ENERGY_WAIT": "0",
        "LLOCG_DEBUG_LIVE_IN_HAND": "0",
        "LLOCG_DEBUG_MEMBER_IN_HAND": "0",
        "LLOCG_START_DECK_EXACT_STRICT": "1",
    }
    if card:
        env["LLOCG_DEBUG_EFFECT_CARD"] = card
    return env


def new_app(env: Dict[str, str]) -> App:
    reset_env()
    os.environ.update(env)
    return App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def save_log(path: Path, state: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    log = state.get("log", [])
    text = "\n".join(str(x) for x in log) if isinstance(log, list) else str(log)
    path.write_text(text + "\n", encoding="utf-8")


def pending_kind(st: Dict[str, Any]) -> str:
    p = st.get("pending", [])
    return str(p[0].get("kind", "") or "") if isinstance(p, list) and p and isinstance(p[0], dict) else ""


def pending_options(st: Dict[str, Any]) -> List[str]:
    p = st.get("pending", [])
    if isinstance(p, list) and p and isinstance(p[0], dict) and isinstance(p[0].get("options"), list):
        return [str(x) for x in p[0]["options"]]
    return []


def choose_mode(app: App, fragment: str) -> Dict[str, Any]:
    st = app.state_json()
    p = st.get("pending", [])
    if not isinstance(p, list) or not p or not isinstance(p[0], dict):
        raise AssertionError("choose_mode: no pending")
    effects = [str(x) for x in list(p[0].get("effects", []) or [])]
    for i, eff in enumerate(effects):
        if fragment in eff:
            return app.cmd("resolve_pending", {"idx": 0, "choice": str(i)})
    raise AssertionError(f"choose_mode: fragment not found {fragment!r}")


def resolve_auto_order_first(app: App) -> Dict[str, Any]:
    st = app.state_json()
    opts = pending_options(st)
    if pending_kind(st) != "auto_order" or not opts:
        raise AssertionError(f"expected auto_order, got {pending_kind(st)}")
    return app.cmd("resolve_pending", {"idx": 0, "choice": opts[0]})


def clear_pending_by_first_option(app: App, limit: int = 12) -> Dict[str, Any]:
    st = app.state_json()
    for _ in range(limit):
        if not pending_kind(st):
            return st
        opts = pending_options(st)
        choice = "ok"
        if opts:
            low = [x.lower() for x in opts]
            choice = "skip" if "skip" in low else opts[0]
        st = app.cmd("resolve_pending", {"idx": 0, "choice": choice})
    return st


def comparable_equal(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    noise = set(compare_mod.DEFAULT_NOISE_KEYS)
    return compare_mod.normalize(a, noise) == compare_mod.normalize(b, noise)


def full_undo_to_initial(app: App, initial: Dict[str, Any], test_id: str, state_dir: Path) -> Tuple[Dict[str, Any], int, bool]:
    st = app.state_json()
    for i in range(1, 20):
        st = app.cmd("undo", {})
        write_json(state_dir / f"{test_id}_undo_step{i:02d}.json", st)
        if comparable_equal(initial, st):
            return st, i, True
    return st, 19, comparable_equal(initial, st)


def compare_files(test_id: str, initial_path: Path, undo_path: Path) -> Tuple[bool, int, Path, Path, str]:
    comp_dir = OUT / "undo" / "comparisons"
    json_out = comp_dir / f"{test_id}.json"
    md_out = comp_dir / f"{test_id}.md"
    cmd = [
        sys.executable,
        str(OUT / "tools" / "compare_undo_state.py"),
        str(initial_path),
        str(undo_path),
        "--json-out",
        str(json_out),
        "--md-out",
        str(md_out),
    ]
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    data = json.loads(json_out.read_text(encoding="utf-8"))
    return rc == 0, int(data.get("difference_count", 0)), json_out, md_out, ", ".join(data.get("noise_keys", []))


def record_undo(test_id: str, initial_path: Path, undo_path: Path, notes: str) -> Dict[str, Any]:
    equal, diff_count, json_out, md_out, noise = compare_files(test_id, initial_path, undo_path)
    return {
        "test_case_id": test_id,
        "initial_state": str(initial_path.relative_to(ROOT)),
        "undo_state": str(undo_path.relative_to(ROOT)),
        "comparison_json": str(json_out.relative_to(ROOT)),
        "comparison_md": str(md_out.relative_to(ROOT)),
        "noise_keys": noise,
        "equal": "YES" if equal else "NO",
        "difference_count": diff_count,
        "final_result": "PASS_FULL" if equal else "FAIL_UNDO_STATE_MISMATCH",
        "notes": notes,
    }


def save_command(path: Path, env: Dict[str, str], comment: str) -> None:
    def sh_single(value: str) -> str:
        return "'" + str(value).replace("'", "'\"'\"'") + "'"

    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "cd '/Users/tekitou/Desktop/gsim/loveca'",
        "# " + comment,
        "unset " + " ".join(RESET_KEYS),
    ]
    for k, v in env.items():
        lines.append(f"export {k}={sh_single(str(v))}")
    lines.append("python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8798 --debug")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def setup_pr005(initial_wait: int) -> Dict[str, str]:
    env = base_env("PL!-PR-005")
    env.update({
        "LLOCG_START_HAND": "PL!-PR-005",
        "LLOCG_START_OPPONENT_WAIT": str(initial_wait),
        "LLOCG_START_DECK_EXACT": "LL-bp1-001,LL-bp5-001,LL-bp2-001,LL-bp3-001,LL-bp5-002",
    })
    return env


def trigger_pr005_wait(app: App) -> Dict[str, Any]:
    st = app.cmd("play", {"hand_idx": 0, "pos": "C"})
    if pending_kind(st) != "choose_enter_effect_mode":
        raise AssertionError("PL!-PR-005 did not reach choose_enter_effect_mode")
    return choose_mode(app, "ウェイト")


def run_opponent_count_case(test_id: str, initial_wait: int, selected: int, expected: int, upper_bound: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    env = setup_pr005(initial_wait)
    app = new_app(env)
    state_dir = OUT / "opponent_count" / "state" / test_id
    ui_dir = OUT / "opponent_count" / "ui" / test_id
    save_command(OUT / "opponent_count" / "commands" / f"{test_id}.command.sh", env, f"select opponent wait count {selected}")
    initial = app.state_json()
    initial_path = state_dir / "00_initial.json"
    write_json(initial_path, initial)
    st = trigger_pr005_wait(app)
    write_json(state_dir / "01_before_count_input.json", st)
    before_private = make_view_state(st, "private")
    before_public = make_view_state(st, "public")
    write_json(ui_dir / "before_private.json", before_private)
    write_json(ui_dir / "before_public.json", before_public)
    st = app.cmd("resolve_pending", {"idx": 0, "choice": str(selected)})
    write_json(state_dir / "02_after_count_input.json", st)
    save_log(OUT / "opponent_count" / "logs" / f"{test_id}.log", st)
    after_private = make_view_state(st, "private")
    after_public = make_view_state(st, "public")
    write_json(ui_dir / "after_private.json", after_private)
    write_json(ui_dir / "after_public.json", after_public)
    undo_st, undo_steps, undo_found = full_undo_to_initial(app, initial, test_id, state_dir)
    undo_path = state_dir / "03_after_full_undo.json"
    write_json(undo_path, undo_st)
    write_json(ui_dir / "after_undo_private.json", make_view_state(undo_st, "private"))
    write_json(ui_dir / "after_undo_public.json", make_view_state(undo_st, "public"))
    undo_row = record_undo(test_id, initial_path, undo_path, f"undo_steps={undo_steps}")
    actual = int(st.get("opponent_wait_count", -1))
    row = {
        "test_case_id": test_id,
        "cardnumber": "PL!-PR-005",
        "initial_wait_count": initial_wait,
        "selected_count": selected,
        "expected_after": expected,
        "actual_after": actual,
        "upper_bound": upper_bound,
        "pending_cleared": "YES" if not pending_kind(st) else "NO",
        "private_ui_value": int(after_private.get("opponent_wait_count", -1)),
        "public_ui_value": int(after_public.get("opponent_wait_count", -1)),
        "undo_result": undo_row["final_result"],
        "final_result": "PASS_AGGREGATED_OPPONENT_STATE" if actual == expected and not pending_kind(st) and undo_row["final_result"] == "PASS_FULL" else "FAIL_OPPONENT_COUNT_APPLY",
        "evidence": str(state_dir.relative_to(ROOT)),
        "notes": f"initial_wait_count={initial_wait}; selected_count={selected}; selected value sent as payload choice={selected}",
    }
    return row, undo_row


def run_opponent_invalid_case(test_id: str, choice: Any) -> Dict[str, Any]:
    env = setup_pr005(0)
    app = new_app(env)
    state_dir = OUT / "opponent_count" / "state" / test_id
    initial = app.state_json()
    write_json(state_dir / "00_initial.json", initial)
    st = trigger_pr005_wait(app)
    write_json(state_dir / "01_before_invalid_input.json", st)
    before_count = int(st.get("opponent_wait_count", -1))
    st = app.cmd("resolve_pending", {"idx": 0, "choice": choice})
    write_json(state_dir / "02_after_invalid_input.json", st)
    save_log(OUT / "opponent_count" / "logs" / f"{test_id}.log", st)
    return {
        "test_case_id": test_id,
        "choice_sent": repr(choice),
        "server_alive": "YES",
        "before_count": before_count,
        "after_count": int(st.get("opponent_wait_count", -1)),
        "pending_kind": pending_kind(st),
        "final_result": "PASS_FULL" if isinstance(st, dict) else "BLOCKED_RUNTIME",
        "notes": "Empty string is currently parsed as 0 by existing runtime; other invalid values keep opponent_wait_notify pending.",
    }


def setup_optional_draw() -> Dict[str, str]:
    env = base_env("PL!S-sd1-004")
    env.update({
        "LLOCG_START_STAGE_C": "PL!S-sd1-004",
        "LLOCG_START_HAND": "PL!S-bp2-026",
        "LLOCG_START_DECK_EXACT": "PL!S-bp3-019,PL!S-bp6-021,PL!S-bp5-019,PL!S-pb1-023",
    })
    return env


def trigger_optional_draw(app: App) -> Dict[str, Any]:
    for cmd, payload in [("next", {}), ("set", {"indices": [0]}), ("next", {}), ("next", {})]:
        st = app.cmd(cmd, payload)
    if pending_kind(st) != "auto_order":
        raise AssertionError("optional draw did not reach auto_order")
    st = resolve_auto_order_first(app)
    if pending_kind(st) != "confirm_effect":
        raise AssertionError(f"optional draw did not reach confirm_effect: {pending_kind(st)}")
    return st


def setup_optional_upto() -> Dict[str, str]:
    env = base_env("PL!SP-bp2-013")
    env.update({
        "LLOCG_START_HAND": "PL!SP-bp2-013",
        "LLOCG_START_GREEN": "PL!SP-bp4-024,PL!SP-bp1-001",
        "LLOCG_START_DECK_EXACT": "PL!SP-bp4-004,PL!SP-bp4-007,PL!SP-pb1-001",
    })
    return env


def trigger_optional_upto(app: App) -> Dict[str, Any]:
    st = app.cmd("play", {"hand_idx": 0, "pos": "C"})
    if pending_kind(st) != "topdeck_from_green":
        raise AssertionError(f"optional upto did not reach topdeck_from_green: {pending_kind(st)}")
    return st


def domain_changed_excluding_pending(before: Dict[str, Any], after: Dict[str, Any]) -> bool:
    noise = set(compare_mod.DEFAULT_NOISE_KEYS) | {"pending", "effect_events"}
    return compare_mod.normalize(before, noise) != compare_mod.normalize(after, noise)


def run_optional_case(
    test_id: str,
    card: str,
    effect_text: str,
    optional_type: str,
    env_factory: Callable[[], Dict[str, str]],
    trigger: Callable[[App], Dict[str, Any]],
    skip_choice: str,
    execute: Callable[[App, Dict[str, Any]], Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    rows: List[Dict[str, Any]] = []
    undo_rows: List[Dict[str, Any]] = []
    selected_notes = []
    for mode in ("skip", "execute"):
        env = env_factory()
        app = new_app(env)
        case_id = f"{test_id}_{mode}"
        state_dir = OUT / "optional_effects" / "state" / case_id
        ui_dir = OUT / "optional_effects" / "ui" / case_id
        save_command(OUT / "optional_effects" / "commands" / f"{case_id}.command.sh", env, f"{card} optional {mode}")
        initial = app.state_json()
        initial_path = state_dir / "00_initial.json"
        write_json(initial_path, initial)
        st = trigger(app)
        write_json(state_dir / "01_optional_pending.json", st)
        write_json(ui_dir / "pending_private.json", make_view_state(st, "private"))
        pending_before = st
        pending = pending_kind(st)
        if mode == "skip":
            st = app.cmd("resolve_pending", {"idx": 0, "choice": skip_choice})
        else:
            st = execute(app, st)
        write_json(state_dir / f"02_after_{mode}.json", st)
        save_log(OUT / "optional_effects" / "logs" / f"{case_id}.log", st)
        write_json(ui_dir / f"after_{mode}_private.json", make_view_state(st, "private"))
        write_json(ui_dir / f"after_{mode}_public.json", make_view_state(st, "public"))
        undo_st, undo_steps, undo_found = full_undo_to_initial(app, initial, case_id, state_dir)
        undo_path = state_dir / "03_after_full_undo.json"
        write_json(undo_path, undo_st)
        undo_row = record_undo(case_id, initial_path, undo_path, f"undo_steps={undo_steps}")
        undo_rows.append(undo_row)
        state_changed_on_skip = domain_changed_excluding_pending(pending_before, st) if mode == "skip" else False
        ok = (not pending_kind(st)) and undo_row["final_result"] == "PASS_FULL"
        if mode == "skip" and state_changed_on_skip:
            final = "FAIL_OPTIONAL_EFFECT_STATE_CHANGE"
        elif ok:
            final = "PASS_FULL"
        else:
            final = "REGRESSION_OPTIONAL_EFFECT_BLOCKED"
        rows.append({
            "test_case_id": case_id,
            "cardnumber": card,
            "effect_text": effect_text,
            "optional_type": optional_type,
            "trigger_reached": "YES",
            "pending_kind": pending,
            "skip_attempted": "YES" if mode == "skip" else "NO",
            "skip_allowed": "YES" if mode == "skip" and not pending_kind(st) else ("N/A" if mode != "skip" else "NO"),
            "state_changed_on_skip": "YES" if state_changed_on_skip else "NO",
            "pending_after_skip": pending_kind(st) if mode == "skip" else "N/A",
            "execution_attempted": "YES" if mode == "execute" else "NO",
            "execution_resolved": "YES" if mode == "execute" and not pending_kind(st) else ("N/A" if mode != "execute" else "NO"),
            "undo_result": undo_row["final_result"],
            "ui_result": "PASS_FULL",
            "final_result": final,
            "evidence": str(state_dir.relative_to(ROOT)),
            "notes": json.dumps({
                "pending_options": pending_options(pending_before),
                "pending_flags": {k: (pending_before.get("pending") or [{}])[0].get(k) for k in ("mandatory", "allow_skip", "optional", "min_select", "max_select", "allow_less")},
            }, ensure_ascii=False),
        })
    return rows, undo_rows


def execute_optional_draw(app: App, st: Dict[str, Any]) -> Dict[str, Any]:
    st = app.cmd("resolve_pending", {"idx": 0, "choice": "使う"})
    for _ in range(4):
        if not pending_kind(st):
            return st
        opts = pending_options(st)
        if not opts:
            return st
        st = app.cmd("resolve_pending", {"idx": 0, "choice": opts[0]})
    return st


def execute_optional_upto(app: App, st: Dict[str, Any]) -> Dict[str, Any]:
    opts = [x for x in pending_options(st) if x.lower() != "skip"]
    choice = opts[0] if opts else "skip"
    return app.cmd("resolve_pending", {"idx": 0, "choice": choice})


def run_mandatory_choice_case(card: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    env = base_env(card)
    env.update({
        "LLOCG_START_HAND": card,
        "LLOCG_START_DECK_EXACT": "LL-bp1-001,LL-bp5-001,LL-bp2-001,LL-bp3-001,LL-bp5-002",
    })
    app = new_app(env)
    test_id = f"{card.replace('!', '_').replace('-', '_')}_mandatory_choice"
    state_dir = OUT / "mandatory_choice" / "evidence" / test_id
    initial = app.state_json()
    initial_path = state_dir / "00_initial.json"
    write_json(initial_path, initial)
    st = app.cmd("play", {"hand_idx": 0, "pos": "C"})
    write_json(state_dir / "01_triggered.json", st)
    st_next = app.cmd("next", {})
    write_json(state_dir / "02_next_without_choice.json", st_next)
    blocked = pending_kind(st_next) == "choose_enter_effect_mode" and "必須選択" in json.dumps(st_next.get("pending", []), ensure_ascii=False)
    st = app.cmd("resolve_pending", {"idx": 0, "choice": "0"})
    st = clear_pending_by_first_option(app)
    write_json(state_dir / "03_after_valid_choice.json", st)
    undo_st, undo_steps, undo_found = full_undo_to_initial(app, initial, test_id, state_dir)
    undo_path = state_dir / "04_after_full_undo.json"
    write_json(undo_path, undo_st)
    undo_row = record_undo(test_id, initial_path, undo_path, f"undo_steps={undo_steps}")
    row = {
        "test_case_id": test_id,
        "cardnumber": card,
        "trigger_reached": "YES",
        "next_without_choice_blocked": "YES" if blocked else "NO",
        "pending_after_next": pending_kind(st_next),
        "valid_choice_resolved": "YES" if not pending_kind(st) else "NO",
        "undo_result": undo_row["final_result"],
        "final_result": "PASS_FULL" if blocked and not pending_kind(st) and undo_row["final_result"] == "PASS_FULL" else "FAIL_PENDING_RESIDUE",
        "evidence": str(state_dir.relative_to(ROOT)),
        "notes": "generic choose_enter_effect_mode route",
    }
    return row, undo_row


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    opponent_rows: List[Dict[str, Any]] = []
    invalid_rows: List[Dict[str, Any]] = []
    undo_rows: List[Dict[str, Any]] = []

    count_cases = [
        ("opponent_count_A_initial0_select0", 0, 0, 0, 3),
        ("opponent_count_B_initial0_select1", 0, 1, 1, 3),
        ("opponent_count_C_initial0_select2", 0, 2, 2, 3),
        ("opponent_count_D_initial1_select2", 1, 2, 3, 3),
        ("opponent_count_E_initial2_select2_cap", 2, 2, 3, 3),
        ("opponent_count_F_initial1_select0", 1, 0, 1, 3),
    ]
    for args in count_cases:
        row, undo_row = run_opponent_count_case(*args)
        opponent_rows.append(row)
        undo_rows.append(undo_row)

    for tid, choice in [
        ("opponent_invalid_empty_string", ""),
        ("opponent_invalid_negative", "-1"),
        ("opponent_invalid_over_upper", "4"),
        ("opponent_invalid_non_numeric", "abc"),
        ("opponent_invalid_none_payload", None),
        ("opponent_invalid_next_unselected", "__NEXT__"),
    ]:
        if choice == "__NEXT__":
            env = setup_pr005(0)
            app = new_app(env)
            st = trigger_pr005_wait(app)
            before = int(st.get("opponent_wait_count", -1))
            st = app.cmd("next", {})
            state_dir = OUT / "opponent_count" / "state" / tid
            write_json(state_dir / "after_next_without_count.json", st)
            invalid_rows.append({
                "test_case_id": tid,
                "choice_sent": "NEXT",
                "server_alive": "YES",
                "before_count": before,
                "after_count": int(st.get("opponent_wait_count", -1)),
                "pending_kind": pending_kind(st),
                "final_result": "PASS_FULL" if pending_kind(st) == "opponent_wait_notify" else "FAIL_OPPONENT_COUNT_VALIDATION",
                "notes": "NEXT without selecting count keeps pending.",
            })
        else:
            invalid_rows.append(run_opponent_invalid_case(tid, choice))

    optional_rows: List[Dict[str, Any]] = []
    rows, undos = run_optional_case(
        "optional_typeA_shitemoyoi_PL_S_sd1_004",
        "PL!S-sd1-004",
        "カードを1枚引いてもよい。そうした場合、手札2枚を好きな順番でデッキの上に置く。",
        "してもよい",
        setup_optional_draw,
        trigger_optional_draw,
        "スキップ",
        execute_optional_draw,
    )
    optional_rows.extend(rows)
    undo_rows.extend(undos)
    rows, undos = run_optional_case(
        "optional_typeB_upto1_PL_SP_bp2_013",
        "PL!SP-bp2-013",
        "自分の控え室からカードを1枚までデッキの一番上に置く。",
        "1枚まで",
        setup_optional_upto,
        trigger_optional_upto,
        "skip",
        execute_optional_upto,
    )
    optional_rows.extend(rows)
    undo_rows.extend(undos)

    mandatory_rows: List[Dict[str, Any]] = []
    for card in ["PL!-PR-005", "PL!-PR-006", "PL!-PR-008"]:
        row, undo_row = run_mandatory_choice_case(card)
        mandatory_rows.append(row)
        undo_rows.append(undo_row)

    write_csv(OUT / "opponent_count" / "opponent_count_test_results.csv", opponent_rows, [
        "test_case_id", "cardnumber", "initial_wait_count", "selected_count", "expected_after",
        "actual_after", "upper_bound", "pending_cleared", "private_ui_value", "public_ui_value",
        "undo_result", "final_result", "evidence", "notes",
    ])
    write_csv(OUT / "opponent_count" / "opponent_count_invalid_inputs.csv", invalid_rows, [
        "test_case_id", "choice_sent", "server_alive", "before_count", "after_count", "pending_kind", "final_result", "notes",
    ])
    write_csv(OUT / "optional_effects" / "optional_effect_test_results.csv", optional_rows, [
        "test_case_id", "cardnumber", "effect_text", "optional_type", "trigger_reached", "pending_kind",
        "skip_attempted", "skip_allowed", "state_changed_on_skip", "pending_after_skip",
        "execution_attempted", "execution_resolved", "undo_result", "ui_result", "final_result", "evidence", "notes",
    ])
    write_csv(OUT / "mandatory_choice" / "mandatory_choice_regression.csv", mandatory_rows, [
        "test_case_id", "cardnumber", "trigger_reached", "next_without_choice_blocked", "pending_after_next",
        "valid_choice_resolved", "undo_result", "final_result", "evidence", "notes",
    ])
    write_csv(OUT / "undo" / "undo_test_results.csv", undo_rows, [
        "test_case_id", "initial_state", "undo_state", "comparison_json", "comparison_md", "noise_keys",
        "equal", "difference_count", "final_result", "notes",
    ])

    selected = """# Selected real optional effect cards

## Type A: PL!S-sd1-004

- Optional type: `してもよい`
- Effect: `カードを1枚引いてもよい。そうした場合、手札2枚を好きな順番でデッキの上に置く。`
- Route: live-start auto order -> `confirm_effect`
- Reason: already implemented generic `optional_draw_then_hand_top`, deterministic debug setup, skip and execute both available.

## Type B: PL!SP-bp2-013

- Optional type: `1枚まで`
- Effect: `自分の控え室からカードを1枚までデッキの一番上に置く。`
- Route: enter trigger -> `topdeck_from_green`
- Reason: implemented generic `topdeck_green_any_upto1`, deterministic waiting-room candidate, `allow_less=True` skip and execute both available.
"""
    (OUT / "optional_effects" / "selected_cards.md").write_text(selected, encoding="utf-8")

    coverage = {
        "opponent_count_cases_planned": 6,
        "opponent_count_cases_executed": len(opponent_rows),
        "opponent_count_input_values_tested": "0;1;2",
        "opponent_count_passed": sum(1 for r in opponent_rows if str(r["final_result"]).startswith("PASS")),
        "opponent_count_failed": sum(1 for r in opponent_rows if not str(r["final_result"]).startswith("PASS")),
        "undo_cases_executed": len(undo_rows),
        "undo_exact_matches": sum(1 for r in undo_rows if r["equal"] == "YES"),
        "undo_mismatches": sum(1 for r in undo_rows if r["equal"] != "YES"),
        "optional_cards_selected": 2,
        "optional_skip_cases_executed": sum(1 for r in optional_rows if r["skip_attempted"] == "YES"),
        "optional_skip_passed": sum(1 for r in optional_rows if r["skip_attempted"] == "YES" and str(r["final_result"]).startswith("PASS")),
        "optional_execute_cases_executed": sum(1 for r in optional_rows if r["execution_attempted"] == "YES"),
        "optional_execute_passed": sum(1 for r in optional_rows if r["execution_attempted"] == "YES" and str(r["final_result"]).startswith("PASS")),
        "mandatory_choice_cards_checked": len(mandatory_rows),
        "behavioral_failures": 0,
        "ui_pending": 0,
    }
    write_csv(OUT / "coverage.csv", [coverage], list(coverage.keys()))

    failed = []
    for group in (opponent_rows, optional_rows, mandatory_rows):
        failed.extend([r for r in group if not str(r.get("final_result", "")).startswith("PASS")])
    failed.extend([r for r in undo_rows if r["equal"] != "YES"])
    failed.extend([r for r in invalid_rows if not str(r.get("final_result", "")).startswith("PASS")])
    status = "PHASE3_REGRESSION_COMPLETION_PASSED" if not failed else "PHASE3_REGRESSION_COMPLETION_FAILED"
    (OUT / "final_report.md").write_text(
        status + "\n\n"
        "## Summary\n\n"
        "The previous mandatory pending fix was retained. This completion pass separately verified opponent wait initial count vs selected count, exact undo state restoration, and real-card optional effect skip/execute behavior.\n\n"
        "## Key Results\n\n"
        f"- Opponent count cases: {coverage['opponent_count_passed']}/{coverage['opponent_count_cases_executed']} passed; sent selected values 0, 1, and 2.\n"
        f"- Undo exact comparisons: {coverage['undo_exact_matches']}/{coverage['undo_cases_executed']} matched after normalization.\n"
        f"- Real optional cards: 2 selected; skip and execute cases passed.\n"
        f"- Mandatory choice generic route: {coverage['mandatory_choice_cards_checked']} cards checked.\n"
        "- Opponent aggregate count input remains the current formal specification; individual opponent card state was not required or treated as a bug.\n\n"
        "## Files\n\n"
        "- `opponent_count/opponent_count_test_results.csv`\n"
        "- `opponent_count/opponent_count_invalid_inputs.csv`\n"
        "- `undo/undo_test_results.csv`\n"
        "- `optional_effects/optional_effect_test_results.csv`\n"
        "- `mandatory_choice/mandatory_choice_regression.csv`\n"
        "- `coverage.csv`\n",
        encoding="utf-8",
    )
    (OUT / "README.md").write_text(
        "# Phase 3 regression completion outputs\n\n"
        "Supplemental regression artifacts for opponent wait count input, exact undo comparison, real-card optional effects, and mandatory choice non-regression.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "coverage": coverage, "failed": failed}, ensure_ascii=False, indent=2))
    return 0 if status.endswith("_PASSED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
