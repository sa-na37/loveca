#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[3]
PREV = ROOT / "_codex_outputs" / "effect_full_audit_phase4_group_alias_completion_20260717"
OUT = ROOT / "_codex_outputs" / "effect_full_audit_phase4_group_alias_success_zone_realcard_20260717"
DB = ROOT / "llocg_db_out_full" / "cards_compiled_v7h.json"
sys.path.insert(0, str(ROOT))

from llocg_ui.server import App
from llocg_ui.views import make_view_state


TARGETS = ["PL!HS-bp2-020", "PL!HS-bp5-018", "PL!HS-sd1-020"]
UNITS = ["スリーズブーケ", "DOLLCHESTRA", "みらくらぱーく！", "蓮ノ空"]
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
FIELDS = [
    "test_id", "target_cardnumber", "test_axis", "reference_unit", "reference_zone",
    "reference_effect_cardnumber", "reference_effect_text", "expected", "actual",
    "count_expected", "count_actual", "duplicate_candidate_count", "ui_state_recorded",
    "browser_ui_checked", "browser_ui_passed", "browser_ui_pending", "runtime_passed",
    "result", "evidence", "notes",
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


def reset_env() -> None:
    for k in RESET_KEYS:
        os.environ.pop(k, None)


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


def app_with_env(env: Dict[str, str]) -> App:
    reset_env()
    os.environ.update(env)
    return App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)


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
    lines.append("# BLOCKED_NO_REAL_CARD_REFERENCE: no real DB card was found for this success-zone group/unit alias condition.")
    lines.append("python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8800 --debug")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ability_lines(card: Dict[str, Any]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for ab in card.get("abilities") or []:
        for cl in ab.get("clauses") or []:
            raw = str(cl.get("raw") or cl.get("effect_template") or "")
            out.append({
                "cardnumber": str(card.get("cardnumber") or ""),
                "cardname": str(card.get("cardname") or ""),
                "card_type": str(card.get("card_type") or ""),
                "ability_type": str(ab.get("ability_type") or ""),
                "trigger": str(ab.get("trigger") or ""),
                "effect_text": raw,
            })
    return out


def search_real_success_zone_references() -> Dict[str, List[Dict[str, str]]]:
    cards = json.load(DB.open(encoding="utf-8"))["cards"]
    all_success: List[Dict[str, str]] = []
    unit_success: List[Dict[str, str]] = []
    for card in cards:
        for line in ability_lines(card):
            text = line["effect_text"]
            if "成功ライブカード置き場" not in text:
                continue
            all_success.append(line)
            if any(unit in text for unit in UNITS):
                unit_success.append(line)
    return {"all_success_zone": all_success, "unit_success_zone": unit_success}


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
    (meta / "port_used.txt").write_text("8800\n", encoding="utf-8")
    (meta / "runtime_modified.txt").write_text("false\n", encoding="utf-8")
    (meta / "db_modified.txt").write_text("false\n", encoding="utf-8")
    (meta / "audit_start.txt").write_text(datetime.now().isoformat() + "\n", encoding="utf-8")


def save_blocked_success_zone_artifacts(target: str) -> str:
    env = base_env("BLOCKED_NO_REAL_CARD_REFERENCE")
    app_absent = app_with_env(env)
    absent_initial = app_absent.state_json()
    absent_after = app_absent.state_json()
    absent_after.setdefault("log", []).append("[AUDIT] BLOCKED_NO_REAL_CARD_REFERENCE: no real DB card references success zone group/unit for this target.")
    app_present = app_with_env(env)
    app_present.gs.success_zone = [target]
    present_initial = app_present.state_json()
    present_after = app_present.state_json()
    present_after.setdefault("log", []).append("[AUDIT] BLOCKED_NO_REAL_CARD_REFERENCE: target was placed in success zone, but no real card effect can legally reference it.")
    test_id = f"{safe(target)}_D_success_zone"
    base = OUT / "continuous_group_alias"
    for name, st in {
        "00_absent_initial": absent_initial,
        "01_absent_after_no_effect": absent_after,
        "02_present_initial": present_initial,
        "03_present_after_no_effect": present_after,
    }.items():
        write_json(base / "state" / f"{test_id}_{name}.json", st)
    write_json(base / "ui" / f"{test_id}_absent_private.json", make_view_state(absent_after, "private"))
    write_json(base / "ui" / f"{test_id}_absent_public.json", make_view_state(absent_after, "public"))
    write_json(base / "ui" / f"{test_id}_present_private.json", make_view_state(present_after, "private"))
    write_json(base / "ui" / f"{test_id}_present_public.json", make_view_state(present_after, "public"))
    (base / "logs").mkdir(parents=True, exist_ok=True)
    (base / "logs" / f"{test_id}.log").write_text(
        "\n".join(str(x) for x in absent_after.get("log", []))
        + "\n--- present case ---\n"
        + "\n".join(str(x) for x in present_after.get("log", []))
        + "\n",
        encoding="utf-8",
    )
    save_command(base / "commands" / f"{test_id}.command.sh", env, f"Blocked success-zone real-card route {target}")
    result_path = base / "results" / f"{test_id}_blocked.json"
    write_json(result_path, {
        "status": "BLOCKED_NO_REAL_CARD_REFERENCE",
        "target_cardnumber": target,
        "absent_success_zone": [],
        "present_success_zone": [target],
        "reason": "No real DB card references success zone by スリーズブーケ/DOLLCHESTRA/みらくらぱーく！/蓮ノ空.",
        "synthetic_effect_used": False,
        "generic_rule_used": False,
    })
    return str(result_path.relative_to(ROOT))


def blocked_row(target: str) -> Dict[str, Any]:
    return {
        "test_id": f"{safe(target)}_D_success_zone",
        "target_cardnumber": target,
        "test_axis": "D_success_zone",
        "reference_unit": "スリーズブーケ/DOLLCHESTRA/みらくらぱーく！/蓮ノ空",
        "reference_zone": "success zone",
        "reference_effect_cardnumber": "BLOCKED_NO_REAL_CARD_REFERENCE",
        "reference_effect_text": "",
        "expected": "A real DB card effect references the target in success zone; absent/present pair can be resolved.",
        "actual": "No real DB card effect references success zone by the target's group/unit aliases; runtime effect not executed.",
        "count_expected": 1,
        "count_actual": "",
        "duplicate_candidate_count": 0,
        "ui_state_recorded": "true",
        "browser_ui_checked": "false",
        "browser_ui_passed": "false",
        "browser_ui_pending": "true",
        "runtime_passed": "false",
        "result": "BLOCKED",
        "evidence": save_blocked_success_zone_artifacts(target),
        "notes": "Synthetic GENERIC_RULE_* effect was removed. DB search evidence is included under continuous_group_alias/db_search/.",
    }


def read_previous_rows() -> List[Dict[str, Any]]:
    with (PREV / "group_alias_test_results.csv").open(newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row.get("test_axis") != "D_success_zone"]


def write_search_evidence() -> Dict[str, int]:
    found = search_real_success_zone_references()
    base = OUT / "continuous_group_alias" / "db_search"
    fields = ["cardnumber", "cardname", "card_type", "ability_type", "trigger", "effect_text"]
    write_csv(base / "success_zone_references_all.csv", found["all_success_zone"], fields)
    write_csv(base / "success_zone_group_unit_references.csv", found["unit_success_zone"], fields)
    write_json(base / "search_summary.json", {
        "success_zone_references_all": len(found["all_success_zone"]),
        "success_zone_group_unit_references": len(found["unit_success_zone"]),
        "searched_terms": UNITS,
        "blocked_reason": "No real card in compiled DB references success zone by the target group/unit aliases.",
    })
    (base / "no_real_card_reference.md").write_text(
        "# Success Zone Real-Card Reference Search\n\n"
        "- Searched compiled DB: `llocg_db_out_full/cards_compiled_v7h.json`\n"
        "- Required zone phrase: `成功ライブカード置き場`\n"
        "- Required alias terms: `スリーズブーケ`, `DOLLCHESTRA`, `みらくらぱーく！`, `蓮ノ空`\n"
        f"- Matching real-card effects: `{len(found['unit_success_zone'])}`\n\n"
        "Because no matching real card exists in the current DB, the three success-zone rows are marked "
        "`BLOCKED_NO_REAL_CARD_REFERENCE`. The previous synthetic `GENERIC_RULE_*` route is not used as PASS evidence.\n",
        encoding="utf-8",
    )
    return {"all": len(found["all_success_zone"]), "unit": len(found["unit_success_zone"])}


def write_summary(rows: List[Dict[str, Any]], search_counts: Dict[str, int]) -> Dict[str, Any]:
    passed = sum(1 for r in rows if r["result"] == "PASS")
    failed = sum(1 for r in rows if r["result"] == "FAIL")
    blocked = sum(1 for r in rows if r["result"] == "BLOCKED")
    summary = {
        "status": "COMPLETED_WITH_BLOCKED_SUCCESS_ZONE",
        "total_tests": len(rows),
        "passed": passed,
        "failed": failed,
        "blocked": blocked,
        "success_zone_realcard_passed": 0,
        "success_zone_blocked_no_real_card_reference": blocked,
        "other_24_tests_preserved": passed == 24,
        "db_success_zone_reference_rows": search_counts["all"],
        "db_success_zone_group_unit_reference_rows": search_counts["unit"],
        "runtime_modified": False,
        "db_modified": False,
    }
    write_json(OUT / "summary.json", summary)
    (OUT / "README.md").write_text(
        "# Phase 4 group alias success-zone real-card audit 20260717\n\n"
        f"- status: `{summary['status']}`\n"
        f"- total_tests: `{len(rows)}`\n"
        f"- passed: `{passed}`\n"
        f"- failed: `{failed}`\n"
        f"- blocked: `{blocked}`\n"
        "- success zone rows were not passed with synthetic effects.\n"
        "- runtime_modified = false\n"
        "- db_modified = false\n",
        encoding="utf-8",
    )
    (OUT / "group_alias_success_zone_realcard_summary.md").write_text(
        "# Group Alias Success-Zone Real-Card Summary\n\n"
        f"- total_tests: {len(rows)}\n"
        f"- passed: {passed}\n"
        f"- failed: {failed}\n"
        f"- blocked: {blocked}\n"
        f"- success-zone real-card matches in DB: {search_counts['unit']}\n"
        "- Result: success-zone 3 rows are `BLOCKED_NO_REAL_CARD_REFERENCE`.\n"
        "- Other 24 rows are preserved from the previous completed audit.\n"
        "- No `GENERIC_RULE_*` reference remains in `group_alias_test_results.csv`.\n",
        encoding="utf-8",
    )
    return summary


def zip_output() -> Path:
    zip_path = OUT.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(OUT.parent))
    return zip_path


def main() -> int:
    self_path = Path(__file__).resolve()
    self_text = self_path.read_text(encoding="utf-8") if self_path.exists() else ""
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(PREV, OUT, ignore=shutil.ignore_patterns("*.zip", "__pycache__"))
    self_path.parent.mkdir(parents=True, exist_ok=True)
    self_path.write_text(self_text, encoding="utf-8")
    make_meta()
    search_counts = write_search_evidence()
    rows = read_previous_rows()
    rows.extend(blocked_row(target) for target in TARGETS)
    rows.sort(key=lambda r: (TARGETS.index(r["target_cardnumber"]) if r["target_cardnumber"] in TARGETS else 99, r["test_axis"], r["test_id"]))
    write_csv(OUT / "group_alias_test_results.csv", rows, FIELDS)
    write_csv(OUT / "continuous_group_alias" / "results" / "group_alias_test_results.csv", rows, FIELDS)
    summary = write_summary(rows, search_counts)
    zip_path = zip_output()
    print(json.dumps({"summary": summary, "zip": str(zip_path)}, ensure_ascii=False, indent=2))
    return 0 if summary["failed"] == 0 and summary["blocked"] == 3 and summary["passed"] == 24 else 1


if __name__ == "__main__":
    raise SystemExit(main())
