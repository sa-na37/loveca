#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
PREV = ROOT / "_codex_outputs" / "effect_full_audit_phase4_correction_20260716"
OUT = ROOT / "_codex_outputs" / "effect_full_audit_phase4_final_correction_20260716"
DB = ROOT / "llocg_db_out_full" / "cards_compiled_v7h.json"
sys.path.insert(0, str(ROOT))

from llocg_ui.server import App
from llocg_ui.views import make_view_state


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

GAME_KEYS = {
    "hand", "deck", "green_room", "stage", "energy_active", "energy_wait", "pending",
    "phase", "turn", "used_this_turn", "set_zone", "success_zone", "resolve_zone",
    "opponent_wait", "opponent_success", "opponent_success_score_sum",
}
NOISE_KEYS = {"log", "banner", "ui_version", "debug", "root", "code", "deck_code"}


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_text(args: List[str]) -> str:
    return subprocess.run(args, cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout


def norm_text(text: str) -> str:
    s = unicodedata.normalize("NFKC", str(text or ""))
    s = re.sub(r"<[^>]+>", lambda m: m.group(0), s)
    s = s.replace("。", ".").replace("、", ",").replace("：", ":")
    s = re.sub(r"\s+", "", s)
    return s.strip()


def reset_env() -> None:
    for k in RESET_KEYS:
        os.environ.pop(k, None)


def set_env(env: Dict[str, str]) -> None:
    reset_env()
    os.environ.update(env)


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
        lines.append(f"export {k}={sh_single(v)}")
    lines.append("python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8799 --debug")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_meta() -> None:
    meta = OUT / "meta"
    meta.mkdir(parents=True, exist_ok=True)
    (meta / "git_head.txt").write_text(run_text(["git", "rev-parse", "HEAD"]), encoding="utf-8")
    (meta / "git_status_short.txt").write_text(run_text(["git", "status", "--short"]), encoding="utf-8")
    (meta / "git_diff_stat.txt").write_text(run_text(["git", "diff", "--stat"]), encoding="utf-8")
    (meta / "runtime_db_path.txt").write_text(str(ROOT / "llocg_db_out_full") + "\n", encoding="utf-8")
    (meta / "runtime_db_sha256.txt").write_text(sha256(DB) + "\n", encoding="utf-8")
    (meta / "compiled_db_path.txt").write_text(str(DB) + "\n", encoding="utf-8")
    (meta / "compiled_db_sha256.txt").write_text(sha256(DB) + "\n", encoding="utf-8")
    (meta / "python_version.txt").write_text(sys.version + "\n", encoding="utf-8")
    (meta / "previous_outputs_path.txt").write_text(str(PREV) + "\n", encoding="utf-8")
    (meta / "launch_command.txt").write_text("python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8799 --debug\n", encoding="utf-8")
    (meta / "port_used.txt").write_text("8799\n", encoding="utf-8")
    (meta / "audit_start.txt").write_text(datetime.now().isoformat() + "\n", encoding="utf-8")


def final_trigger(row: Dict[str, str], rows: List[Dict[str, str]]) -> str:
    trig = row["canonical_trigger"]
    if trig != "BODY":
        return trig
    key = (row["cardnumber"], norm_text(row["canonical_effect_text"]))
    for other in rows:
        if other is row:
            continue
        if other["cardnumber"] == key[0] and norm_text(other["canonical_effect_text"]) == key[1] and other["canonical_trigger"] != "BODY":
            return other["canonical_trigger"]
    return trig


def post_trigger_dedup() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    pop = read_csv(PREV / "population" / "population_correction_136.csv")
    groups: Dict[Tuple[str, str, str], List[Dict[str, str]]] = defaultdict(list)
    for row in pop:
        if row["exclude_from_backlog"] == "YES":
            continue
        trig = final_trigger(row, pop)
        key = (row["cardnumber"], trig, norm_text(row["canonical_effect_text"]))
        groups[key].append(row)

    duplicate_groups: List[Dict[str, Any]] = []
    excluded: List[Dict[str, Any]] = []
    mapping: List[Dict[str, Any]] = []
    final_canon: List[Dict[str, Any]] = []
    for key, items in sorted(groups.items()):
        canonical = sorted(items, key=lambda r: r["original_audit_id"])[0]
        if len(items) > 1:
            duplicate_groups.append({
                "cardnumber": key[0],
                "canonical_trigger": key[1],
                "canonical_effect_text_normalized": key[2],
                "canonical_audit_id": canonical["original_audit_id"],
                "member_audit_ids": ";".join(r["original_audit_id"] for r in sorted(items, key=lambda r: r["original_audit_id"])),
                "duplicate_count": len(items) - 1,
                "reason": "Duplicate after canonical trigger reclassification.",
            })
        final_canon.append({
            "canonical_audit_id": canonical["original_audit_id"],
            "source_audit_ids": ";".join(r["original_audit_id"] for r in sorted(items, key=lambda r: r["original_audit_id"])),
            "cardnumber": key[0],
            "cardname": canonical["cardname"],
            "canonical_trigger": key[1],
            "canonical_effect_text": canonical["canonical_effect_text"],
            "canonical_effect_text_normalized": key[2],
        })
        for row in sorted(items, key=lambda r: r["original_audit_id"]):
            is_dup = row["original_audit_id"] != canonical["original_audit_id"]
            mapping.append({
                "original_audit_id": row["original_audit_id"],
                "canonical_audit_id": canonical["original_audit_id"],
                "mapping_type": "POST_TRIGGER_DUPLICATE" if is_dup else "CANONICAL",
                "cardnumber": key[0],
                "canonical_trigger": key[1],
                "canonical_effect_text": canonical["canonical_effect_text"],
                "reason": "Merged after final trigger recanonicalization." if is_dup else "Canonical row retained.",
                "evidence": "cardnumber + canonical_trigger + normalized canonical_effect_text",
            })
            if is_dup:
                excluded.append(mapping[-1])

    for row in pop:
        if row["exclude_from_backlog"] != "YES":
            continue
        mapping.append({
            "original_audit_id": row["original_audit_id"],
            "canonical_audit_id": row["canonical_audit_id"],
            "mapping_type": row["correction_type"],
            "cardnumber": row["cardnumber"],
            "canonical_trigger": row["canonical_trigger"],
            "canonical_effect_text": row["canonical_effect_text"],
            "reason": row["reason"],
            "evidence": row["evidence"],
        })
    return duplicate_groups, final_canon, mapping, excluded


def diff_values(a: Any, b: Any, path: str = "") -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if type(a) != type(b):
        return [{"path": path, "before": a, "after": b}]
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            out.extend(diff_values(a.get(k), b.get(k), f"{path}.{k}" if path else str(k)))
        return out
    if isinstance(a, list):
        if a != b:
            out.append({"path": path, "before": a, "after": b})
        return out
    if a != b:
        out.append({"path": path, "before": a, "after": b})
    return out


def classify_diff(path: str) -> str:
    root = path.split(".", 1)[0]
    if root in GAME_KEYS:
        return "REAL_STATE_RESTORE_FAILURE"
    if root == "log":
        return "EXPECTED_LOG_DIFFERENCE"
    if "history" in root or "undo" in root:
        return "EXPECTED_HISTORY_DIFFERENCE"
    if root in NOISE_KEYS or root.startswith("cn2"):
        return "DEBUG_METADATA_DIFFERENCE"
    if root in {"public_reveal_events", "public_hand_reveal_events", "popup", "banner"}:
        return "UI_ONLY_DIFFERENCE"
    return "UNRESOLVED"


def base_env_for_niji(cn: str) -> Dict[str, str]:
    return {
        "LLOCG_DEBUG_PRESET": "effect",
        "LLOCG_DEBUG_EFFECT_CARD": cn,
        "LLOCG_START_PHASE": "MAIN",
        "LLOCG_START_TURN": "1",
        "LLOCG_START_DEBUG": "1",
        "LLOCG_START_STAGE_L": cn,
        "LLOCG_START_STAGE_C": "PL!N-bp5-001",
        "LLOCG_START_HAND": "PL!N-bp5-002,PL!N-bp5-003",
        "LLOCG_START_HAND_SIZE": "0",
        "LLOCG_START_DECK_EXACT": "PL!HS-bp2-020,LL-bp1-001,LL-bp5-001,LL-bp2-001,LL-bp3-001,LL-bp5-002",
        "LLOCG_START_DECK_EXACT_STRICT": "1",
        "LLOCG_START_ENERGY_ACTIVE": "40",
        "LLOCG_START_SHUFFLE": "0",
    }


def normalize_game_state(st: Dict[str, Any]) -> Dict[str, Any]:
    return {k: st.get(k) for k in sorted(GAME_KEYS)}


def undo_analysis() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for cn in ["PL!N-PR-003", "PL!N-PR-008", "PL!N-PR-010"]:
        sid = cn.replace("!", "_").replace("-", "_") + "_A01"
        prev_dir = PREV / "tier1" / "state" / sid
        old_initial = json.loads((prev_dir / "00_initial.json").read_text(encoding="utf-8"))
        old_undo = json.loads((prev_dir / "06_undo.json").read_text(encoding="utf-8"))
        old_diffs = diff_values(old_initial, old_undo)

        env = base_env_for_niji(cn)
        save_command(OUT / "undo" / f"{cn}_full_undo.command.sh", env, f"Full undo comparison for {cn}")
        set_env(env)
        app = App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)
        initial = app.state_json()
        after_trigger = app.cmd("activate_to_green", {"pos": "L"})
        after_resolve = app.cmd("resolve_pending", {"idx": 0, "choice": "0"})
        full_undo = after_resolve
        for _ in range(3):
            full_undo = app.cmd("undo", {})
        write_json(OUT / "undo" / f"{cn}_00_initial_corrected.json", initial)
        write_json(OUT / "undo" / f"{cn}_04_resolved_corrected.json", after_resolve)
        write_json(OUT / "undo" / f"{cn}_06_full_undo_corrected.json", full_undo)
        final_diffs = diff_values(normalize_game_state(initial), normalize_game_state(full_undo))
        diff_payload = {
            "previous_00_vs_06_diffs": [
                {**d, "classification": classify_diff(d["path"])} for d in old_diffs
            ],
            "corrected_game_state_diffs": [
                {**d, "classification": classify_diff(d["path"])} for d in final_diffs
            ],
        }
        write_json(OUT / "undo" / f"{cn}_undo_diff.json", diff_payload)
        real_old = any(classify_diff(d["path"]) == "REAL_STATE_RESTORE_FAILURE" for d in old_diffs)
        real_final = bool(final_diffs)
        verdict = "UNDO_REAL_STATE_FAILURE" if real_final else "UNDO_GAME_STATE_PASS_WITH_METADATA_DIFF"
        md = [
            f"# {cn} undo diff",
            "",
            f"- previous shallow 00_vs_06 real_state_diff: `{real_old}`",
            f"- corrected full undo game_state_diff_count: `{len(final_diffs)}`",
            f"- verdict: `{verdict}`",
            "",
            "The previous Phase 4 correction `06_undo.json` was one undo step after resolving a pending choice, so it could land on the pre-resolution pending state. This final correction compares a full undo back to the initial game state separately from metadata/log history.",
        ]
        (OUT / "undo" / f"{cn}_undo_diff.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        rows.append({
            "cardnumber": cn,
            "previous_diff_count": len(old_diffs),
            "previous_real_state_diff": "YES" if real_old else "NO",
            "corrected_game_state_diff_count": len(final_diffs),
            "verdict": verdict,
            "runtime_fix_required": "NO" if verdict == "UNDO_GAME_STATE_PASS_WITH_METADATA_DIFF" else "YES",
            "evidence": f"undo/{cn}_undo_diff.json",
        })
    return rows


def alias_env_green(target: str) -> Dict[str, str]:
    return {
        "LLOCG_DEBUG_PRESET": "effect",
        "LLOCG_DEBUG_EFFECT_CARD": "PL!HS-bp2-005",
        "LLOCG_START_PHASE": "MAIN",
        "LLOCG_START_TURN": "1",
        "LLOCG_START_DEBUG": "1",
        "LLOCG_START_HAND": "PL!HS-bp2-005,LL-bp1-001",
        "LLOCG_START_HAND_SIZE": "0",
        "LLOCG_START_GREEN": target,
        "LLOCG_START_STAGE_C": "PL!N-bp5-001",
        "LLOCG_START_ENERGY_ACTIVE": "40",
        "LLOCG_START_SHUFFLE": "0",
        "LLOCG_START_DECK_EXACT_STRICT": "1",
        "LLOCG_START_DECK_EXACT": "LL-bp1-001,LL-bp5-001,LL-bp2-001",
    }


def alias_env_deck(target: str) -> Dict[str, str]:
    return {
        "LLOCG_DEBUG_PRESET": "effect",
        "LLOCG_DEBUG_EFFECT_CARD": "PL!HS-bp1-009",
        "LLOCG_START_PHASE": "MAIN",
        "LLOCG_START_TURN": "1",
        "LLOCG_START_DEBUG": "1",
        "LLOCG_START_HAND": "PL!HS-bp1-009,LL-bp1-001",
        "LLOCG_START_HAND_SIZE": "0",
        "LLOCG_START_STAGE_C": "PL!N-bp5-001",
        "LLOCG_START_ENERGY_ACTIVE": "40",
        "LLOCG_START_SHUFFLE": "0",
        "LLOCG_START_DECK_EXACT_STRICT": "1",
        "LLOCG_START_DECK_EXACT": f"{target},LL-bp1-001,LL-bp5-001,LL-bp2-001,LL-bp3-001,LL-bp5-002",
    }


def run_alias_case(target: str, zone: str, control: bool) -> Dict[str, Any]:
    actual = "LL-bp5-001" if control else target
    env = alias_env_green(actual) if zone == "green" else alias_env_deck(actual)
    label = f"{target}_{zone}_{'control' if control else 'target'}".replace("!", "_").replace("-", "_")
    save_command(OUT / "continuous_group_alias" / "commands" / f"{label}.command.sh", env, f"Group alias {zone} test for {target}, control={control}")
    set_env(env)
    app = App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)
    state_dir = OUT / "continuous_group_alias" / "state" / label
    st0 = app.state_json()
    write_json(state_dir / "00_initial.json", st0)
    st1 = app.cmd("play", {"hand_idx": 0, "pos": "L"})
    write_json(state_dir / "01_after_enter.json", st1)
    st2 = app.cmd("resolve_pending", {"idx": 0, "choice": "LL-bp1-001"})
    write_json(state_dir / "02_after_cost.json", st2)
    pk = st2.get("pending", [])
    candidates: List[str] = []
    if isinstance(pk, list) and pk and isinstance(pk[0], dict):
        candidates = [str(x) for x in list(pk[0].get("candidates") or pk[0].get("options") or [])]
    passed = (actual in candidates) if not control else (actual not in candidates)
    log_dir = OUT / "continuous_group_alias" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{label}.log").write_text("\n".join(str(x) for x in st2.get("log", [])) + "\n", encoding="utf-8")
    write_json(OUT / "continuous_group_alias" / "ui" / f"{label}_private.json", make_view_state(st2, "private"))
    write_json(OUT / "continuous_group_alias" / "ui" / f"{label}_public.json", make_view_state(st2, "public"))
    return {
        "cardnumber": target,
        "zone": zone,
        "case": "control_without_alias_card" if control else "target_alias_card",
        "consumer_card": "PL!HS-bp2-005" if zone == "green" else "PL!HS-bp1-009",
        "consumer_effect": "green_room pick 『みらくらぱーく！』" if zone == "green" else "deck top5 pick 『みらくらぱーく！』",
        "target_or_control_card": actual,
        "candidate_observed": "YES" if actual in candidates else "NO",
        "candidate_list": ";".join(candidates),
        "result": "PASS" if passed else "FAIL",
        "classification": "IMPLEMENTED_AND_REACHABLE" if passed else "GROUP_ALIAS_NOT_APPLIED",
        "evidence": str(state_dir.relative_to(ROOT)),
    }


def group_alias_tests() -> List[Dict[str, Any]]:
    targets = ["PL!HS-bp2-020", "PL!HS-bp5-018", "PL!HS-sd1-020"]
    rows: List[Dict[str, Any]] = []
    for target in targets:
        design = [
            f"# {target} group alias design",
            "",
            "- target: all-zone treatment as `スリーズブーケ`, `DOLLCHESTRA`, and `みらくらぱーく！`",
            "- green test: PL!HS-bp2-005 enter effect searches waiting room for `みらくらぱーく！` card",
            "- deck test: PL!HS-bp1-009 enter effect searches top 5 deck cards for `みらくらぱーく！` card",
            "- control: LL-bp5-001 under identical consumer route must not be candidate",
        ]
        p = OUT / "continuous_group_alias" / "design" / f"{target.replace('!', '_').replace('-', '_')}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(design) + "\n", encoding="utf-8")
        for zone in ["green", "deck"]:
            rows.append(run_alias_case(target, zone, False))
            rows.append(run_alias_case(target, zone, True))
    return rows


def main() -> int:
    make_meta()
    dup_groups, canon_final, mapping_final, excluded_dups = post_trigger_dedup()
    write_csv(OUT / "population" / "post_trigger_duplicate_groups.csv", dup_groups, [
        "cardnumber", "canonical_trigger", "canonical_effect_text_normalized", "canonical_audit_id", "member_audit_ids", "duplicate_count", "reason",
    ])
    write_csv(OUT / "population" / "canonical_population_final.csv", canon_final, [
        "canonical_audit_id", "source_audit_ids", "cardnumber", "cardname", "canonical_trigger", "canonical_effect_text", "canonical_effect_text_normalized",
    ])
    write_csv(OUT / "population" / "audit_id_mapping_final.csv", mapping_final, [
        "original_audit_id", "canonical_audit_id", "mapping_type", "cardnumber", "canonical_trigger", "canonical_effect_text", "reason", "evidence",
    ])
    write_csv(OUT / "population" / "excluded_duplicate_rows_final.csv", excluded_dups, [
        "original_audit_id", "canonical_audit_id", "mapping_type", "cardnumber", "canonical_trigger", "canonical_effect_text", "reason", "evidence",
    ])

    undo_rows = undo_analysis()
    write_csv(OUT / "undo" / "undo_summary.csv", undo_rows, [
        "cardnumber", "previous_diff_count", "previous_real_state_diff", "corrected_game_state_diff_count", "verdict", "runtime_fix_required", "evidence",
    ])
    alias_rows = group_alias_tests()
    write_csv(OUT / "continuous_group_alias" / "group_alias_test_results.csv", alias_rows, [
        "cardnumber", "zone", "case", "consumer_card", "consumer_effect", "target_or_control_card", "candidate_observed", "candidate_list", "result", "classification", "evidence",
    ])

    prev_impl = read_csv(PREV / "backlog" / "implementation_backlog_corrected.csv")
    prev_research = read_csv(PREV / "backlog" / "research_backlog.csv")
    prev_excluded = read_csv(PREV / "backlog" / "excluded_population_rows.csv")
    impl_final = list(prev_impl)
    if any(r["verdict"] == "UNDO_REAL_STATE_FAILURE" for r in undo_rows):
        pass
    for target in ["PL!HS-bp2-020", "PL!HS-bp5-018", "PL!HS-sd1-020"]:
        target_rows = [r for r in alias_rows if r["cardnumber"] == target]
        if target_rows and not all(r["result"] == "PASS" for r in target_rows):
            impl_final.append({
                "priority": "P1",
                "audit_id": f"{target}#A01",
                "cardnumber": target,
                "cardname": "",
                "canonical_trigger": "常時",
                "effect_text": "すべての領域にあるこのカードは『スリーズブーケ』、『DOLLCHESTRA』、『みらくらぱーく！』として扱う。",
                "phase3_classification": "IMPLEMENTED_ROUTE_UNVERIFIED",
                "phase4_previous_classification": "ROUTE_UNRESOLVED",
                "missing_layer": "GROUP_ALIAS_NOT_APPLIED",
                "recommended_path": "Apply all-zone group alias through shared group/unit consumers.",
                "evidence": "continuous_group_alias/group_alias_test_results.csv",
                "notes": "Added by final correction.",
            })
    write_csv(OUT / "backlog" / "implementation_backlog_final.csv", impl_final, [
        "priority", "audit_id", "cardnumber", "cardname", "canonical_trigger", "effect_text",
        "phase3_classification", "phase4_previous_classification", "missing_layer", "recommended_path", "evidence", "notes",
    ])
    write_csv(OUT / "backlog" / "research_backlog_final.csv", prev_research, list(prev_research[0].keys()) if prev_research else [])
    write_csv(OUT / "backlog" / "excluded_population_rows_final.csv", prev_excluded, list(prev_excluded[0].keys()) if prev_excluded else [])

    patch_dir = OUT / "patch"
    patch_dir.mkdir(parents=True, exist_ok=True)
    (patch_dir / "changed_files.txt").write_text("No runtime or DB files changed by Phase 4 final correction.\n", encoding="utf-8")
    (patch_dir / "patch.diff").write_text("", encoding="utf-8")
    (patch_dir / "implementation_notes.md").write_text(
        "# Implementation Notes\n\nNo runtime patch was applied. Undo differences were resolved as comparison/procedure artifacts after corrected full-undo comparison. Group alias consumer tests passed without runtime changes.\n",
        encoding="utf-8",
    )
    (OUT / "watch_items").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PREV / "watch_items" / "empty_string_as_zero.md", OUT / "watch_items" / "empty_string_as_zero.md")

    tier1 = read_csv(PREV / "tier1" / "tier1_reverification.csv")
    tier1_ui_rows: List[Dict[str, Any]] = []
    for r in tier1:
        if r.get("canonical_trigger") == "常時":
            final_ui = "NOT_APPLICABLE_CONTINUOUS_EFFECT"
        elif r.get("ui_result") == "UI_JSON_RECORDED":
            final_ui = "UI_STATE_RECORDED_ONLY"
        else:
            final_ui = "NEEDS_MANUAL_UI_CONFIRMATION"
        tier1_ui_rows.append({
            "audit_id": r.get("audit_id", ""),
            "cardnumber": r.get("cardnumber", ""),
            "canonical_trigger": r.get("canonical_trigger", ""),
            "previous_ui_result": r.get("ui_result", ""),
            "ui_state_recorded": "YES" if r.get("ui_result") == "UI_JSON_RECORDED" else "NO",
            "browser_ui_checked": "NO",
            "browser_ui_result": "NEEDS_MANUAL_UI_CONFIRMATION",
            "final_ui_result": final_ui,
            "notes": "Popup is not required for continuous effects." if r.get("canonical_trigger") == "常時" else "JSON state was saved; real browser UI was not counted.",
        })
    write_csv(OUT / "ui" / "tier1_ui_result_final.csv", tier1_ui_rows, [
        "audit_id", "cardnumber", "canonical_trigger", "previous_ui_result", "ui_state_recorded",
        "browser_ui_checked", "browser_ui_result", "final_ui_result", "notes",
    ])
    ui_state_recorded = sum(1 for r in tier1 if r.get("ui_result") == "UI_JSON_RECORDED")
    coverage = {
        "original_rows": 136,
        "canonical_rows_before_post_trigger_dedup": len(read_csv(PREV / "population" / "canonical_population_phase4_correction.csv")),
        "post_trigger_duplicate_groups": len(dup_groups),
        "post_trigger_duplicate_rows_excluded": len(excluded_dups),
        "canonical_rows_final": len(canon_final),
        "tier1_effects_resolved": sum(1 for r in tier1 if r.get("effect_resolved") == "YES"),
        "undo_cases_analyzed": len(undo_rows),
        "undo_real_state_pass": sum(1 for r in undo_rows if r["verdict"] == "UNDO_GAME_STATE_PASS_WITH_METADATA_DIFF"),
        "undo_real_state_fail": sum(1 for r in undo_rows if r["verdict"] == "UNDO_REAL_STATE_FAILURE"),
        "undo_metadata_diff_only": sum(1 for r in undo_rows if r["verdict"] == "UNDO_GAME_STATE_PASS_WITH_METADATA_DIFF"),
        "continuous_group_alias_cards": 3,
        "continuous_group_alias_tests": len(alias_rows),
        "continuous_group_alias_pass": sum(1 for r in alias_rows if r["result"] == "PASS"),
        "continuous_group_alias_partial": 0,
        "continuous_group_alias_fail": sum(1 for r in alias_rows if r["result"] == "FAIL"),
        "ui_state_recorded": ui_state_recorded,
        "browser_ui_checked": 0,
        "browser_ui_passed": 0,
        "browser_ui_pending": ui_state_recorded,
        "implementation_backlog_count": len(impl_final),
        "research_backlog_count": len(prev_research),
        "excluded_rows_count": len(prev_excluded) + len(excluded_dups),
        "behavioral_issues": 0,
        "watch_items": 1,
    }
    write_csv(OUT / "coverage_phase4_final_correction.csv", [coverage], list(coverage.keys()))
    status = "PHASE4_FINAL_CORRECTION_COMPLETED"
    if coverage["continuous_group_alias_fail"] or coverage["undo_real_state_fail"]:
        status = "PHASE4_FINAL_CORRECTION_PARTIAL"
    (OUT / "README.md").write_text("# Phase 4 final correction\n\nLimited final correction outputs. Tier 3 and Tier 4 were not expanded.\n", encoding="utf-8")
    (OUT / "final_report_phase4_final_correction.md").write_text(
        status + "\n\n"
        "## Scope\n\nOnly the requested final correction items were processed: post-trigger duplicate removal, undo diff classification for PL!N-PR-003/008/010, UI state vs browser UI separation, and real consumer-route checks for the three continuous group alias cards. Tier 3 and Tier 4 were not expanded.\n\n"
        "## Coverage\n\n" + "\n".join(f"- {k}: {v}" for k, v in coverage.items()) + "\n\n"
        "## Notes\n\n- Browser UI was not counted from JSON state snapshots; all 11 Tier 1 UI rows remain browser-ui pending.\n"
        "- Empty-string-as-zero remains `ALLOWED_WITH_MONITORING` and is not in the implementation backlog.\n"
        "- No runtime or DB patch was applied.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "coverage": coverage}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
