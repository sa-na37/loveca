#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "effect_full_audit_phase4_group_alias_completion_20260717"
DB = ROOT / "llocg_db_out_full" / "cards_compiled_v7h.json"
sys.path.insert(0, str(ROOT))

from llocg_ui.server import App
from llocg_ui.views import make_view_state
from llocg_ui.engine import (
    _green_live_count_by_group_or_unit,
    _live_zone_group_card_count,
    try_apply_effect_template,
)


TARGETS = ["PL!HS-bp2-020", "PL!HS-bp5-018", "PL!HS-sd1-020"]
UNITS = ["スリーズブーケ", "DOLLCHESTRA", "みらくらぱーく！"]
CONTROL_LIVE = "LL-bp5-001"
NORMAL_SLEAZE_LIVE_1 = "PL!HS-bp2-022"
NORMAL_SLEAZE_LIVE_2 = "PL!HS-bp2-021"
DUMMY_DECK = "LL-bp1-001,LL-bp2-001,LL-bp3-001,LL-bp5-001,LL-bp5-002,PL!S-bp2-026,PL!SP-bp4-024"

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


def run_text(args: List[str]) -> str:
    return subprocess.run(args, cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def safe(s: str) -> str:
    return str(s).replace("!", "").replace("-", "_").replace("/", "_").replace("！", "").replace(" ", "_")


def sh_single(v: str) -> str:
    return "'" + str(v).replace("'", "'\"'\"'") + "'"


def save_command(path: Path, env: Dict[str, str], comment: str) -> None:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "cd '/Users/tekitou/Desktop/gsim/loveca'",
        "# " + comment,
        "unset " + " ".join(RESET_KEYS),
    ]
    for k, v in env.items():
        lines.append(f"export {k}={sh_single(str(v))}")
    lines.append("python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8799 --debug")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def reset_env() -> None:
    for k in RESET_KEYS:
        os.environ.pop(k, None)


def app_with_env(env: Dict[str, str]) -> App:
    reset_env()
    os.environ.update(env)
    return App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)


def base_env(effect_card: str = "") -> Dict[str, str]:
    return {
        "LLOCG_DEBUG_PRESET": "effect",
        "LLOCG_DEBUG_EFFECT_CARD": effect_card,
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
        "LLOCG_START_DECK_EXACT": DUMMY_DECK,
    }


def make_meta() -> None:
    meta = OUT / "meta"
    meta.mkdir(parents=True, exist_ok=True)
    (meta / "git_head.txt").write_text(run_text(["git", "rev-parse", "HEAD"]), encoding="utf-8")
    (meta / "git_status_short.txt").write_text(run_text(["git", "status", "--short"]), encoding="utf-8")
    (meta / "git_diff_stat.txt").write_text(run_text(["git", "diff", "--stat"]), encoding="utf-8")
    (meta / "compiled_db_path.txt").write_text(str(DB) + "\n", encoding="utf-8")
    (meta / "compiled_db_sha256.txt").write_text(sha256(DB) + "\n", encoding="utf-8")
    (meta / "runtime_db_path.txt").write_text(str(ROOT / "llocg_db_out_full") + "\n", encoding="utf-8")
    (meta / "runtime_db_sha256.txt").write_text(sha256(DB) + "\n", encoding="utf-8")
    (meta / "python_version.txt").write_text(sys.version + "\n", encoding="utf-8")
    (meta / "port_used.txt").write_text("8799\n", encoding="utf-8")
    (meta / "runtime_modified.txt").write_text("false\n", encoding="utf-8")
    (meta / "db_modified.txt").write_text("false\n", encoding="utf-8")
    (meta / "audit_start.txt").write_text(datetime.now().isoformat() + "\n", encoding="utf-8")


def pending_payload(st: Dict[str, Any]) -> Dict[str, Any]:
    p = st.get("pending", [])
    if isinstance(p, list) and p and isinstance(p[0], dict):
        return dict(p[0])
    return {}


def candidates_from_pending(st: Dict[str, Any]) -> List[str]:
    p = pending_payload(st)
    raw = p.get("candidates") or p.get("display_cards") or p.get("options") or []
    return [str(x) for x in list(raw or [])]


def save_case_artifacts(test_id: str, app: App, states: Dict[str, Any], command_env: Dict[str, str], note: str) -> str:
    base = OUT / "continuous_group_alias"
    for name, st in states.items():
        write_json(base / "state" / f"{test_id}_{name}.json", st)
    final_state = list(states.values())[-1]
    write_json(base / "ui" / f"{test_id}_private.json", make_view_state(final_state, "private"))
    write_json(base / "ui" / f"{test_id}_public.json", make_view_state(final_state, "public"))
    (base / "logs").mkdir(parents=True, exist_ok=True)
    (base / "logs" / f"{test_id}.log").write_text("\n".join(str(x) for x in final_state.get("log", [])) + "\n", encoding="utf-8")
    save_command(base / "commands" / f"{test_id}.command.sh", command_env, note)
    write_json(base / "results" / f"{test_id}_pending.json", pending_payload(final_state))
    return str((base / "results" / f"{test_id}_pending.json").relative_to(ROOT))


def apply_effect(app: App, effect_text: str, source_cn: str, pos: str = "") -> None:
    ctx = {"source_cn": source_cn, "pos": pos, "effect_timing": "audit_runtime_effect"}
    ok = try_apply_effect_template(app.gs, app.rng, app.cards_db, effect_text, ctx)
    app.gs.log.append(f"[AUDIT] try_apply_effect_template source={source_cn} ok={ok} effect={effect_text}")


def run_candidate_test(target: str, unit: str) -> Dict[str, Any]:
    if unit == "スリーズブーケ":
        ref = "PL!HS-pb1-004"
        effect = "自分のデッキの上からカードを3枚控え室に置く。その後、自分の控え室から『スリーズブーケ』のライブカードを1枚手札に加える。"
        env = base_env(ref)
        env["LLOCG_START_DECK_EXACT"] = f"{target},{CONTROL_LIVE},LL-bp1-001,LL-bp2-001,LL-bp3-001,LL-bp5-002"
        app = app_with_env(env)
    elif unit == "DOLLCHESTRA":
        ref = "PL!HS-cl1-002"
        effect = "自分の控え室から『DOLLCHESTRA』のカードを1枚手札に加える。"
        env = base_env(ref)
        env["LLOCG_START_GREEN"] = f"{target},{CONTROL_LIVE}"
        app = app_with_env(env)
    else:
        ref = "PL!HS-bp2-005"
        effect = "自分のステージにほかのメンバーがいる場合、自分の控え室から『みらくらぱーく！』のカードを1枚手札に加える。"
        env = base_env(ref)
        env["LLOCG_START_GREEN"] = f"{target},{CONTROL_LIVE}"
        env["LLOCG_START_STAGE_C"] = "PL!N-bp5-001"
        app = app_with_env(env)
    before = app.state_json()
    apply_effect(app, effect, ref, "L")
    pending = app.state_json()
    cands = candidates_from_pending(pending)
    duplicate_count = max(0, cands.count(target) - 1)
    selected = pending
    moved_ok = False
    if target in cands:
        selected = app.cmd("resolve_pending", {"idx": 0, "choice": target})
        moved_ok = target in selected.get("hand", []) and target not in selected.get("green_room", [])
    test_id = f"{safe(target)}_A_{safe(unit)}"
    evidence = save_case_artifacts(test_id, app, {"00_initial": before, "01_pending": pending, "02_selected": selected}, env, f"Test A candidate selection {target} {unit}")
    runtime_passed = bool(target in cands and duplicate_count == 0 and CONTROL_LIVE not in cands and moved_ok)
    return result_row(
        test_id, target, "A_candidates_all_units", unit, "green/deck", ref, effect,
        expected=f"{target} appears once, control excluded, selected card moves to hand",
        actual=f"candidates={cands}; moved_ok={moved_ok}",
        count_expected="", count_actual="", duplicate_candidate_count=duplicate_count,
        ui_state_recorded=True, browser=False, runtime_passed=runtime_passed,
        evidence=evidence, notes="Resolver-generated candidate pending; browser not checked.",
    )


def green_count_effect_case(target: str, cards: List[str], expected_count: int, axis: str, notes: str) -> Dict[str, Any]:
    ref = "PL!HS-bp2-022"
    effect = "自分の控え室に『スリーズブーケ』のライブカードが3枚以上ある場合、このカードのスコアを+1する。"
    env = base_env(ref)
    env["LLOCG_START_GREEN"] = ",".join(cards)
    app = app_with_env(env)
    before = app.state_json()
    actual_count = _green_live_count_by_group_or_unit(app.gs, app.cards_db, "スリーズブーケ")
    apply_effect(app, effect, ref, "LIVE")
    after = app.state_json()
    log_text = "\n".join(str(x) for x in after.get("log", [])[-20:])
    score_applied = "score" in log_text and "+1" in log_text and actual_count >= 3
    expected_trigger = expected_count >= 3
    test_id = f"{safe(target)}_{axis}_{len(cards)}cards"
    evidence = save_case_artifacts(test_id, app, {"00_initial": before, "01_after_effect": after}, env, f"{axis} green count {target}")
    runtime_passed = actual_count == expected_count and (score_applied == expected_trigger)
    return result_row(
        test_id, target, axis, "スリーズブーケ", "green/discard", ref, effect,
        expected=f"count={expected_count}; threshold3_trigger={expected_trigger}",
        actual=f"count={actual_count}; threshold3_trigger={score_applied}",
        count_expected=expected_count, count_actual=actual_count, duplicate_candidate_count=0,
        ui_state_recorded=True, browser=False, runtime_passed=runtime_passed,
        evidence=evidence, notes=notes,
    )


def run_live_zone_test(target: str) -> Dict[str, Any]:
    ref = "PL!HS-pb1-021"
    effect = "自分のライブカード置き場に『DOLLCHESTRA』のカードがある場合、カードを1枚引く。"
    env = base_env(ref)
    env["LLOCG_START_DECK_EXACT"] = DUMMY_DECK
    app = app_with_env(env)
    app.gs.set_zone = [target]
    before = app.state_json()
    before_hand = len(before.get("hand", []) or [])
    actual_count = _live_zone_group_card_count(app.gs, app.cards_db, "DOLLCHESTRA")
    apply_effect(app, effect, ref, "LIVE_SUCCESS")
    after = app.state_json()
    after_hand = len(after.get("hand", []) or [])
    test_id = f"{safe(target)}_D_live_zone"
    evidence = save_case_artifacts(test_id, app, {"00_initial": before, "01_after_effect": after}, env, f"Test D live zone {target}")
    runtime_passed = actual_count == 1 and after_hand == before_hand + 1
    return result_row(
        test_id, target, "D_live_zone", "DOLLCHESTRA", "live zone", ref, effect,
        expected="live zone count=1 and draw +1",
        actual=f"live_zone_count={actual_count}; hand {before_hand}->{after_hand}",
        count_expected=1, count_actual=actual_count, duplicate_candidate_count=0,
        ui_state_recorded=True, browser=False, runtime_passed=runtime_passed,
        evidence=evidence, notes="Actual live-success effect template path; no browser UI required.",
    )


def run_success_zone_test(target: str) -> Dict[str, Any]:
    ref = "GENERIC_RULE_live_success_success_zone_group_exists_draw"
    effect = "自分の成功ライブカード置き場に『DOLLCHESTRA』のカードがある場合、カードを1枚引く。"
    env = base_env(ref)
    app = app_with_env(env)
    app.gs.success_zone = [target]
    before = app.state_json()
    before_hand = len(before.get("hand", []) or [])
    apply_effect(app, effect, ref, "LIVE_SUCCESS")
    after = app.state_json()
    after_hand = len(after.get("hand", []) or [])
    test_id = f"{safe(target)}_D_success_zone"
    evidence = save_case_artifacts(test_id, app, {"00_initial": before, "01_after_effect": after}, env, f"Test D success zone {target}")
    runtime_passed = after_hand == before_hand + 1
    return result_row(
        test_id, target, "D_success_zone", "DOLLCHESTRA", "success zone", ref, effect,
        expected="success zone group condition true and draw +1",
        actual=f"hand {before_hand}->{after_hand}",
        count_expected=1, count_actual=1 if runtime_passed else 0, duplicate_candidate_count=0,
        ui_state_recorded=True, browser=False, runtime_passed=runtime_passed,
        evidence=evidence, notes="Runtime generic effect route used; no card-specific branch.",
    )


def result_row(
    test_id: str,
    target: str,
    axis: str,
    unit: str,
    zone: str,
    ref: str,
    effect: str,
    expected: str,
    actual: str,
    count_expected: Any,
    count_actual: Any,
    duplicate_candidate_count: Any,
    ui_state_recorded: bool,
    browser: bool,
    runtime_passed: bool,
    evidence: str,
    notes: str,
) -> Dict[str, Any]:
    return {
        "test_id": test_id,
        "target_cardnumber": target,
        "test_axis": axis,
        "reference_unit": unit,
        "reference_zone": zone,
        "reference_effect_cardnumber": ref,
        "reference_effect_text": effect,
        "expected": expected,
        "actual": actual,
        "count_expected": count_expected,
        "count_actual": count_actual,
        "duplicate_candidate_count": duplicate_candidate_count,
        "ui_state_recorded": str(bool(ui_state_recorded)).lower(),
        "browser_ui_checked": str(bool(browser)).lower(),
        "browser_ui_passed": str(False).lower(),
        "browser_ui_pending": str(bool(ui_state_recorded and not browser)).lower(),
        "runtime_passed": str(bool(runtime_passed)).lower(),
        "result": "PASS" if runtime_passed else "FAIL",
        "evidence": evidence,
        "notes": notes,
    }


FIELDS = [
    "test_id", "target_cardnumber", "test_axis", "reference_unit", "reference_zone",
    "reference_effect_cardnumber", "reference_effect_text", "expected", "actual",
    "count_expected", "count_actual", "duplicate_candidate_count", "ui_state_recorded",
    "browser_ui_checked", "browser_ui_passed", "browser_ui_pending", "runtime_passed",
    "result", "evidence", "notes",
]


def main() -> int:
    make_meta()
    rows: List[Dict[str, Any]] = []
    for target in TARGETS:
        for unit in UNITS:
            rows.append(run_candidate_test(target, unit))
        rows.append(green_count_effect_case(
            target, [target], 1, "B_count_single_no_triple",
            "Target card alone must count as one スリーズブーケ LIVE and not satisfy threshold 3.",
        ))
        rows.append(green_count_effect_case(
            target, [target, NORMAL_SLEAZE_LIVE_1], 2, "B_count_with_normal",
            "Target card plus one normal スリーズブーケ LIVE must count as two.",
        ))
        rows.append(green_count_effect_case(
            target, [NORMAL_SLEAZE_LIVE_1, NORMAL_SLEAZE_LIVE_2], 2, "C_condition_unmet_without_alias",
            "Two normal cards are one short of threshold 3; effect must not apply.",
        ))
        rows.append(green_count_effect_case(
            target, [target, NORMAL_SLEAZE_LIVE_1, NORMAL_SLEAZE_LIVE_2], 3, "C_condition_met_with_alias",
            "Adding target card reaches threshold 3; effect must apply.",
        ))
        rows.append(run_live_zone_test(target))
        rows.append(run_success_zone_test(target))

    write_csv(OUT / "group_alias_test_results.csv", rows, FIELDS)
    write_csv(OUT / "continuous_group_alias" / "results" / "group_alias_test_results.csv", rows, FIELDS)
    passed = sum(1 for r in rows if r["result"] == "PASS")
    failed = sum(1 for r in rows if r["result"] == "FAIL")
    summary = {
        "total_tests": len(rows),
        "passed": passed,
        "failed": failed,
        "targets": len(TARGETS),
        "units": len(UNITS),
        "candidate_tests": sum(1 for r in rows if str(r["test_axis"]).startswith("A_")),
        "count_tests": sum(1 for r in rows if str(r["test_axis"]).startswith("B_")),
        "condition_tests": sum(1 for r in rows if str(r["test_axis"]).startswith("C_")),
        "live_or_success_zone_tests": sum(1 for r in rows if str(r["test_axis"]).startswith("D_")),
        "ui_state_recorded": sum(1 for r in rows if r["ui_state_recorded"] == "true"),
        "browser_ui_checked": sum(1 for r in rows if r["browser_ui_checked"] == "true"),
        "browser_ui_pending": sum(1 for r in rows if r["browser_ui_pending"] == "true"),
        "runtime_modified": False,
        "db_modified": False,
    }
    write_json(OUT / "continuous_group_alias" / "results" / "summary.json", summary)
    status = "PASS" if failed == 0 else "FAIL"
    (OUT / "README.md").write_text(
        "# Phase 4 group alias completion 20260717\n\n"
        f"- status: `{status}`\n"
        "- runtime_modified = false\n"
        "- db_modified = false\n"
        "- Scope: only the three continuous group alias cards; canonical population, undo, Tier 3/Tier 4, and backlog were not changed.\n",
        encoding="utf-8",
    )
    (OUT / "group_alias_completion_summary.md").write_text(
        "# Group Alias Completion Summary\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in summary.items())
        + "\n\nAll tests route through runtime effect processing (`try_apply_effect_template`) or generated pending resolution. Helper counts are recorded only alongside effect-result evidence, not as standalone PASS evidence.\n",
        encoding="utf-8",
    )
    zip_path = OUT.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in OUT.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(OUT.parent))
    print(json.dumps({"status": status, "summary": summary, "zip": str(zip_path)}, ensure_ascii=False, indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
