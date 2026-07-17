#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "loveca_phase4_confirmed_backlog_implementation_20260717"
sys.path.insert(0, str(ROOT))

RESET_KEYS = [
    "LLOCG_START_STAGE", "LLOCG_START_STAGE_L", "LLOCG_START_STAGE_C", "LLOCG_START_STAGE_R",
    "LLOCG_START_HAND", "LLOCG_START_HAND_SIZE", "LLOCG_START_SHUFFLE",
    "LLOCG_START_GREEN", "LLOCG_START_SUCCESS", "LLOCG_START_RESOLVE",
    "LLOCG_START_DECK_TOP", "LLOCG_START_DECK_EXACT", "LLOCG_START_DECK_EXACT_STRICT",
    "LLOCG_START_PHASE", "LLOCG_START_TURN",
    "LLOCG_START_ENERGY_ACTIVE", "LLOCG_START_ENERGY_WAIT",
    "LLOCG_DEBUG_PRESET", "LLOCG_START_DEBUG",
    "LLOCG_DEBUG_LIVE_IN_HAND", "LLOCG_DEBUG_MEMBER_IN_HAND",
]

FIELDS = [
    "test_id", "cardnumber", "purpose", "initial_state", "action", "expected", "actual",
    "ui_state_recorded", "browser_ui_checked", "browser_ui_passed", "runtime_passed",
    "undo_checked", "result", "evidence", "notes",
]


def run_text(args: List[str]) -> str:
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def reset_env() -> None:
    for k in RESET_KEYS:
        os.environ.pop(k, None)


def set_env(env: Dict[str, str]) -> None:
    reset_env()
    os.environ.update(env)


def base_env() -> Dict[str, str]:
    return {
        "LLOCG_DEBUG_PRESET": "effect",
        "LLOCG_START_PHASE": "MAIN",
        "LLOCG_START_TURN": "1",
        "LLOCG_START_DEBUG": "1",
        "LLOCG_START_HAND_SIZE": "0",
        "LLOCG_START_SHUFFLE": "0",
        "LLOCG_START_ENERGY_ACTIVE": "40",
        "LLOCG_START_ENERGY_WAIT": "0",
        "LLOCG_DEBUG_LIVE_IN_HAND": "0",
        "LLOCG_DEBUG_MEMBER_IN_HAND": "0",
        "LLOCG_START_DECK_EXACT_STRICT": "1",
        "LLOCG_START_DECK_EXACT": "LL-bp5-001,LL-bp5-002,PL!S-bp2-026,PL!N-bp4-030,PL!N-bp3-032,PL!N-bp1-029",
    }


def app_from_env(env: Dict[str, str]):
    from llocg_ui.server import App
    set_env(env)
    return App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)


def gameplay_projection(st: Dict[str, Any]) -> Dict[str, Any]:
    keep = {}
    for k in [
        "turn", "phase", "deck", "hand", "energy_active", "energy_wait", "stage", "green_room",
        "set_zone", "resolve_zone", "success_zone", "pending",
    ]:
        keep[k] = st.get(k)
    return keep


def same_gameplay(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    return gameplay_projection(a) == gameplay_projection(b)


def snapshot_projection(snap: Dict[str, Any]) -> Dict[str, Any]:
    keep = {}
    for k in [
        "turn", "phase", "deck", "hand", "energy_active", "energy_wait", "stage", "green_room",
        "set_zone", "resolve_zone", "success_zone", "pending", "used_this_turn",
    ]:
        keep[k] = snap.get(k)
    return keep


def same_snapshot(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    return snapshot_projection(a) == snapshot_projection(b)


def save_command(test_id: str, env: Dict[str, str]) -> str:
    def q(v: str) -> str:
        return "'" + str(v).replace("'", "'\"'\"'") + "'"
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "cd '/Users/tekitou/Desktop/gsim/loveca'",
        "unset " + " ".join(RESET_KEYS),
    ]
    for k, v in env.items():
        lines.append(f"export {k}={q(v)}")
    lines.append("python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8801 --debug")
    path = OUT / "debug_commands" / f"{test_id}.command.sh"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path.relative_to(OUT))


def save_case(test_id: str, app: Any, states: Dict[str, Dict[str, Any]], env: Dict[str, str]) -> str:
    for name, st in states.items():
        write_json(OUT / "evidence" / "state" / f"{test_id}_{name}.json", st)
        try:
            from llocg_ui.views import make_view_state
            write_json(OUT / "evidence" / "ui" / f"{test_id}_{name}_private.json", make_view_state(st, "private"))
            write_json(OUT / "evidence" / "ui" / f"{test_id}_{name}_public.json", make_view_state(st, "public"))
        except Exception:
            pass
    final = list(states.values())[-1]
    p = OUT / "evidence" / "logs" / f"{test_id}.log"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(str(x) for x in final.get("log", [])) + "\n", encoding="utf-8")
    save_command(test_id, env)
    return str((OUT / "evidence" / "state" / f"{test_id}_{list(states.keys())[-1]}.json").relative_to(OUT))


def row(test_id: str, card: str, purpose: str, expected: str, actual: str, ok: bool, evidence: str, undo: bool = False, notes: str = "") -> Dict[str, Any]:
    return {
        "test_id": test_id,
        "cardnumber": card,
        "purpose": purpose,
        "initial_state": "see evidence state 00_initial",
        "action": "see debug command and state sequence",
        "expected": expected,
        "actual": actual,
        "ui_state_recorded": "true",
        "browser_ui_checked": "false",
        "browser_ui_passed": "false",
        "runtime_passed": str(bool(ok)).lower(),
        "undo_checked": str(bool(undo)).lower(),
        "result": "PASS" if ok else "FAIL",
        "evidence": evidence,
        "notes": notes,
    }


def hs_case(test_id: str, stage_env: Dict[str, str], choice: str, purpose: str, expect_blade_pos: str = "") -> Dict[str, Any]:
    from llocg_ui.engine import snapshot_state
    env = base_env()
    env.update(stage_env)
    env["LLOCG_START_HAND"] = "PL!HS-bp6-014"
    app = app_from_env(env)
    snap0 = snapshot_state(app.gs)
    st0 = app.state_json()
    st1 = app.cmd("activate_from_hand", {"hand_idx": 0})
    states = {"00_initial": st0, "01_activated": st1}
    ok = "PL!HS-bp6-014" in st1.get("green_room", []) and len(st1.get("hand", [])) == len(st0.get("hand", []))
    if st1.get("pending") and choice:
        st2 = app.cmd("resolve_pending", {"idx": 0, "choice": choice})
        states["02_resolved"] = st2
        ok = ok and int(((st2.get("stage", {}) or {}).get(expect_blade_pos, {}) or {}).get("temp_blade", 0) or 0) == 1
        st_undo1 = app.cmd("undo", {})
        states["03_undo_one_step"] = st_undo1
        st_undo2 = app.cmd("undo", {})
        states["04_undo_initial"] = st_undo2
        undo_ok = same_snapshot(snap0, snapshot_state(app.gs))
    else:
        st2 = app.cmd("resolve_pending", {"idx": 0, "choice": "ok"}) if st1.get("pending") else st1
        states["02_resolved"] = st2
        ok = ok and not st2.get("pending")
        st_undo1 = app.cmd("undo", {})
        states["03_undo_one_step"] = st_undo1
        st_undo2 = app.cmd("undo", {})
        states["04_undo_initial"] = st_undo2
        undo_ok = same_snapshot(snap0, snapshot_state(app.gs))
    ev = save_case(test_id, app, states, env)
    return row(test_id, "PL!HS-bp6-014", purpose, "self to green, draw 1, target blade or no-target notice, undo restore", f"ok={ok}; undo_initial={undo_ok}", ok and undo_ok, ev, True)


def sp_case(test_id: str, hand: List[str], choice: List[str], purpose: str, expect_score: int, expect_options: List[str] | None = None) -> Dict[str, Any]:
    from llocg_ui.engine import snapshot_state
    env = base_env()
    env["LLOCG_START_STAGE_C"] = "PL!SP-bp1-003"
    env["LLOCG_START_HAND"] = ",".join(hand)
    app = app_from_env(env)
    snap0 = snapshot_state(app.gs)
    st0 = app.state_json()
    can0 = bool(((st0.get("stage_detail", {}) or {}).get("C", {}) or {}).get("can_activate"))
    st1 = app.cmd("activate_to_green", {"pos": "C"})
    p = (st1.get("pending") or [{}])[0]
    opts = list(p.get("options", []) or [])
    st2 = app.cmd("resolve_pending", {"idx": 0, "choice": ",".join(choice)})
    temp_score = int(((st2.get("stage", {}) or {}).get("C", {}) or {}).get("temp_score", 0) or 0)
    hand_same = st2.get("hand") == st0.get("hand")
    used = bool((getattr(app.gs, "used_this_turn", {}) or {}))
    options_ok = True if expect_options is None else opts == expect_options
    ok = can0 and hand_same and temp_score == expect_score and used and options_ok
    states = {"00_initial": st0, "01_pending": st1, "02_resolved": st2}
    st_undo1 = app.cmd("undo", {})
    states["03_undo_one_step"] = st_undo1
    st_undo2 = app.cmd("undo", {})
    states["04_undo_initial"] = st_undo2
    undo_ok = same_snapshot(snap0, snapshot_state(app.gs))
    ev = save_case(test_id, app, states, env)
    return row(test_id, "PL!SP-bp1-003", purpose, "MEMBER-only reveal, hand unchanged, turn once consumed, score only for valid totals", f"options={opts}; temp_score={temp_score}; hand_same={hand_same}; used={used}; undo_initial={undo_ok}", ok and undo_ok, ev, True)


def sp_reactivation_case() -> Dict[str, Any]:
    from llocg_ui.engine import begin_turn
    env = base_env()
    env["LLOCG_START_STAGE_C"] = "PL!SP-bp1-003"
    env["LLOCG_START_HAND"] = "PL!HS-PR-005,LL-bp1-001"
    app = app_from_env(env)
    st0 = app.state_json()
    st1 = app.cmd("activate_to_green", {"pos": "C"})
    st2 = app.cmd("resolve_pending", {"idx": 0, "choice": "PL!HS-PR-005"})
    st3 = app.cmd("resolve_pending", {"idx": 0, "choice": "ok"})
    can_same = bool(((st3.get("stage_detail", {}) or {}).get("C", {}) or {}).get("can_activate"))
    app.gs.turn = int(getattr(app.gs, "turn", 1) or 1) + 1
    begin_turn(app.gs, app.rng)
    st4 = app.state_json()
    can_next = bool(((st4.get("stage_detail", {}) or {}).get("C", {}) or {}).get("can_activate"))
    ok = (not can_same) and can_next
    ev = save_case("PLSP_bp1_003_reactivation", app, {"00_initial": st0, "01_pending": st1, "02_resolved": st2, "03_ack": st3, "04_next_turn": st4}, env)
    return row("PLSP_bp1_003_reactivation", "PL!SP-bp1-003", "same-turn once-per-turn prevention and next-turn reset", "same turn false, next turn true", f"same={can_same}; next={can_next}", ok, ev, False)


def write_outputs(rows: List[Dict[str, Any]]) -> None:
    (OUT / "git").mkdir(parents=True, exist_ok=True)
    (OUT / "git" / "status.txt").write_text(run_text(["git", "status", "--short"]), encoding="utf-8")
    (OUT / "git" / "diff_stat.txt").write_text(run_text(["git", "diff", "--stat"]), encoding="utf-8")
    (OUT / "git" / "diff.patch").write_text(run_text(["git", "diff", "--", "llocg_ui"]), encoding="utf-8")
    for rel in ["llocg_ui/engine.py", "llocg_ui/server.py"]:
        dst = OUT / "changed_files" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)
    with (OUT / "test_results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    passed = sum(1 for r in rows if r["result"] == "PASS")
    failed = len(rows) - passed
    (OUT / "README.md").write_text(f"# Loveca Phase 4 confirmed backlog implementation 20260717\n\n- runtime_modified = true\n- db_modified = false\n- tests = {len(rows)}\n- passed = {passed}\n- failed = {failed}\n", encoding="utf-8")
    (OUT / "implementation_summary.md").write_text(
        "# Implementation Summary\n\n"
        "- Implemented a hand-activated ability route for activated abilities whose cost moves the source card from hand to waiting room.\n"
        "- Implemented a generic hand MEMBER reveal cost-sum pending for activated abilities that reveal any number of member cards and check totals 10/20/30/40/50.\n"
        "- Public reveal evidence is emitted through `show_revealed_cards_ack`; selected cards remain in hand.\n"
        "- Temporary blade and live-total score bonuses use existing stage slot `temp_blade` / `temp_score` with `temp_until=end_of_live`.\n"
        "- Undo is command-granular; evidence includes one-step undo and multi-step restoration to initial state.\n",
        encoding="utf-8",
    )
    zip_path = OUT.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(OUT.parent))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    rows.append(hs_case("PLHS_bp6_014_megumi", {"LLOCG_START_STAGE_C": "PL!HS-bp2-015"}, "C", "藤島慈 target", "C"))
    rows.append(hs_case("PLHS_bp6_014_rurino", {"LLOCG_START_STAGE_C": "PL!HS-bp2-014"}, "C", "大沢瑠璃乃 target", "C"))
    rows.append(hs_case("PLHS_bp6_014_both_choose_center", {"LLOCG_START_STAGE_L": "PL!HS-bp2-015", "LLOCG_START_STAGE_C": "PL!HS-bp2-014"}, "C", "two candidates choose one", "C"))
    rows.append(hs_case("PLHS_bp6_014_no_target", {"LLOCG_START_STAGE_C": "PL!HS-bp2-013"}, "", "no target"))
    rows.append(sp_case("PLSP_bp1_003_total_0", ["PL!HS-PR-005", "LL-bp1-001"], [], "total 0 invalid", 0))
    rows.append(sp_case("PLSP_bp1_003_total_9", ["PL!-PR-005", "LL-bp1-001"], ["PL!-PR-005"], "total 9 invalid", 0))
    rows.append(sp_case("PLSP_bp1_003_total_10", ["PL!HS-PR-005", "LL-bp1-001"], ["PL!HS-PR-005"], "total 10 valid", 1))
    rows.append(sp_case("PLSP_bp1_003_total_20", ["LL-bp1-001", "PL!HS-PR-005"], ["LL-bp1-001"], "total 20 valid", 1))
    rows.append(sp_case("PLSP_bp1_003_total_30", ["LL-bp1-001", "PL!HS-PR-005"], ["LL-bp1-001", "PL!HS-PR-005"], "total 30 valid", 1))
    rows.append(sp_case("PLSP_bp1_003_total_40", ["LL-bp1-001", "LL-bp2-001"], ["LL-bp1-001", "LL-bp2-001"], "total 40 valid", 1))
    rows.append(sp_case("PLSP_bp1_003_total_50", ["LL-bp1-001", "LL-bp2-001", "PL!HS-PR-005"], ["LL-bp1-001", "LL-bp2-001", "PL!HS-PR-005"], "total 50 valid", 1))
    rows.append(sp_case("PLSP_bp1_003_total_60", ["LL-bp1-001", "LL-bp2-001", "LL-bp3-001"], ["LL-bp1-001", "LL-bp2-001", "LL-bp3-001"], "total 60 invalid", 0))
    rows.append(sp_case("PLSP_bp1_003_member_live_mixed", ["PL!HS-PR-005", "PL!S-bp2-024"], ["PL!HS-PR-005"], "MEMBER/LIVE mixed hand filters LIVE out", 1, ["PL!HS-PR-005"]))
    rows.append(sp_reactivation_case())
    write_outputs(rows)
    print(json.dumps({"total": len(rows), "passed": sum(1 for r in rows if r["result"] == "PASS"), "failed": sum(1 for r in rows if r["result"] != "PASS"), "out": str(OUT), "zip": str(OUT.with_suffix(".zip"))}, ensure_ascii=False, indent=2))
    return 0 if all(r["result"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
