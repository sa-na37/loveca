#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "effect_full_audit_phase3_20260716"
PHASE2 = ROOT / "_codex_outputs" / "effect_full_audit_phase2_20260716"
PORTS = [8787, 8797, 8798, 8799, 8877, 8878, 8879]

RESET_VARS = [
    "LLOCG_START_STAGE", "LLOCG_START_STAGE_L", "LLOCG_START_STAGE_C", "LLOCG_START_STAGE_R",
    "LLOCG_START_HAND", "LLOCG_START_HAND_SIZE", "LLOCG_START_SHUFFLE",
    "LLOCG_START_GREEN", "LLOCG_START_SUCCESS", "LLOCG_START_RESOLVE",
    "LLOCG_START_DECK_TOP", "LLOCG_START_DECK_EXACT", "LLOCG_START_DECK_EXACT_STRICT",
    "LLOCG_START_PHASE", "LLOCG_START_TURN", "LLOCG_START_ENERGY_ACTIVE", "LLOCG_START_ENERGY_WAIT",
    "LLOCG_DEBUG_PRESET", "LLOCG_DEBUG_EFFECT_CARD", "LLOCG_START_DEBUG",
    "LLOCG_DEBUG_LIVE_IN_HAND", "LLOCG_DEBUG_MEMBER_IN_HAND",
]

NOISE_KEYS = {
    "now", "timestamp", "session", "session_id", "view_generated_at",
}


def ensure_dirs() -> None:
    for rel in [
        "meta", "pilot", "expected", "state", "ui", "commands/accepted",
        "commands/rejected", "commands/candidates", "logs", "static_evidence",
        "db", "tools", "docs", "screenshots",
    ]:
        (OUT / rel).mkdir(parents=True, exist_ok=True)


def run_text(args: list[str], timeout: int = 20) -> str:
    p = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    return p.stdout


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_cards() -> dict[str, dict[str, Any]]:
    data = json.load((ROOT / "llocg_db_out_full" / "cards_min_tokv1.json").open(encoding="utf-8"))
    return {str(c.get("cardnumber")): c for c in data}


def load_compiled() -> dict[str, dict[str, Any]]:
    data = json.load((ROOT / "llocg_db_out_full" / "cards_compiled_v7h.json").open(encoding="utf-8"))
    return {str(c.get("cardnumber")): c for c in data.get("cards", [])}


def http_json(method: str, url: str, obj: dict[str, Any] | None = None, timeout: float = 3.0) -> dict[str, Any]:
    body = None
    headers = {}
    if obj is not None:
        body = json.dumps(obj).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def q(s: str) -> str:
    return "'" + s.replace("'", "'\"'\"'") + "'"


def command_text(env: dict[str, str], port: int) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        f"cd {q(str(ROOT))}",
        "unset " + " ".join(RESET_VARS),
    ]
    for k, v in env.items():
        lines.append(f"export {k}={q(str(v))}")
    lines.append(f"python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port {port} --debug")
    return "\n".join(lines) + "\n"


def normalize_state(v: Any) -> Any:
    if isinstance(v, dict):
        out = {}
        for k, val in v.items():
            if k in NOISE_KEYS:
                continue
            out[k] = normalize_state(val)
        return out
    if isinstance(v, list):
        return [normalize_state(x) for x in v]
    return v


def diff(a: Any, b: Any, path: str = "") -> list[dict[str, Any]]:
    if type(a) is not type(b):
        return [{"path": path or "$", "before": a, "after": b}]
    if isinstance(a, dict):
        rows = []
        for k in sorted(set(a) | set(b)):
            rows.extend(diff(a.get(k), b.get(k), f"{path}.{k}" if path else k))
        return rows
    if isinstance(a, list):
        if a == b:
            return []
        return [{"path": path or "$", "before": a, "after": b}]
    if a != b:
        return [{"path": path or "$", "before": a, "after": b}]
    return []


def state_subset(st: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "phase", "turn", "hand", "deck", "green_room", "success_zone", "resolve_zone",
        "set_zone", "pending", "energy_active", "energy_wait",
        "opponent_wait_count", "opponent_success_count", "opponent_excess_heart_count",
        "stage",
    ]
    return {k: st.get(k) for k in keys if k in st}


def save_state(dir_: Path, name: str, st: dict[str, Any]) -> None:
    dir_.mkdir(parents=True, exist_ok=True)
    (dir_ / name).write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def post(base: str, cmd: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return http_json("POST", base + "/cmd", {"cmd": cmd, "payload": payload or {}}, timeout=3.0)


def get_state(base: str) -> dict[str, Any]:
    return http_json("GET", base + "/state?view=debug", timeout=3.0)


def start_server(env: dict[str, str], log_path: Path) -> tuple[subprocess.Popen[str], str, int, dict[str, Any]]:
    env2 = os.environ.copy()
    env2.update(env)
    errors: list[str] = []
    for port in PORTS:
        proc = subprocess.Popen(
            [sys.executable, "./run_llocg_ui_web.py", "--host", "127.0.0.1", "--port", str(port), "--debug"],
            cwd=ROOT,
            env=env2,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        base = f"http://127.0.0.1:{port}"
        st = None
        last = ""
        for _ in range(50):
            if proc.poll() is not None:
                break
            try:
                st = get_state(base)
                break
            except Exception as e:
                last = repr(e)
                time.sleep(0.1)
        if st is not None:
            return proc, base, port, st
        try:
            errors.append(f"port={port} failed {last} stdout={(proc.stdout.read() if proc.stdout else '')[:2000]}")
        except Exception:
            errors.append(f"port={port} failed {last}")
        try:
            proc.terminate()
            proc.wait(timeout=1)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    log_path.write_text("\n".join(errors), encoding="utf-8")
    raise RuntimeError("server did not start")


def base_env(cn: str) -> dict[str, str]:
    return {
        "LLOCG_DEBUG_PRESET": "effect",
        "LLOCG_START_PHASE": "MAIN",
        "LLOCG_START_TURN": "1",
        "LLOCG_START_DEBUG": "1",
        "LLOCG_DEBUG_EFFECT_CARD": cn,
        "LLOCG_START_HAND_SIZE": "0",
        "LLOCG_START_ENERGY_ACTIVE": "20",
        "LLOCG_START_ENERGY_WAIT": "0",
        "LLOCG_DEBUG_LIVE_IN_HAND": "0",
        "LLOCG_DEBUG_MEMBER_IN_HAND": "0",
        "LLOCG_START_HAND": cn,
        "LLOCG_START_DECK_EXACT_STRICT": "1",
    }


def pl_expected(cn: str, test_case_id: str, branch: str) -> dict[str, Any]:
    effects = {
        "draw_discard": [
            "カードを1枚引く",
            "手札から選んだ1枚だけを控え室へ置く",
            "解決後pendingが消える",
        ],
        "opponent_wait_all_cost2": [
            "相手ステージのコスト2以下メンバーをウェイトにする",
            "現runtimeは相手個別ステージを持たないため、人数入力pendingで代替される",
        ],
        "choice_required": [
            "必ず1つ選ぶ効果のためskip/nextで無選択解決できない",
        ],
    }
    return {
        "audit_id": f"{cn}#A01",
        "test_case_id": test_case_id,
        "cardnumber": cn,
        "effect_text": "<登場>\n以下から1つを選ぶ。\n・カードを1枚引き、手札を1枚控え室に置く。\n・相手のステージにいるすべてのコスト2以下のメンバーをウェイトにする。",
        "trigger": "登場",
        "preconditions": ["対象MEMBERを手札からCへ登場させる", "energy activeを十分量にする"],
        "costs": ["登場コスト9"],
        "choices": ["カードを1枚引き、手札を1枚控え室に置く", "相手のステージにいるすべてのコスト2以下のメンバーをウェイトにする"],
        "valid_targets": ["分岐A: ドロー後の手札カード", "分岐B: 相手ステージのコスト2以下アクティブメンバー"],
        "invalid_targets": ["分岐A: ステージ上の発生源自身", "分岐B: コスト3以上または既にwaitの相手メンバー"],
        "expected_state_changes": effects[branch],
        "expected_zone_moves": ["branchA: deck top -> hand -> selected card green_room"],
        "expected_count_changes": ["branchA: deck -1, hand +1 then -1, green_room +1"],
        "expected_temporary_modifiers": [],
        "expected_cleanup": ["pendingなし", "temporary modifierなし", "次操作を妨げない"],
        "expected_ui": ["2つの選択肢が重複なく表示", "発生源と実行中効果が表示"],
        "expected_logs": ["[PENDING]", "[AUTO]"],
        "expected_non_changes": ["発生源カードはステージに残る", "branchBでは自分の手札/山札は変化しない"],
    }


def ll_expected(test_case_id: str, branch: str) -> dict[str, Any]:
    return {
        "audit_id": "LL-bp1-001#A01",
        "test_case_id": test_case_id,
        "cardnumber": "LL-bp1-001",
        "effect_text": "<登場>\n自分の控え室からメンバーカードを1枚手札に加える。",
        "trigger": "登場",
        "preconditions": ["対象MEMBERを手札からCへ登場させる", "控え室候補をbranchごとに配置する"],
        "costs": ["登場コスト20"],
        "choices": ["控え室のメンバーカード1枚を選ぶ"],
        "valid_targets": ["MEMBERカード"],
        "invalid_targets": ["LIVEカード"],
        "expected_state_changes": [
            "candidate_multi/candidate_one: 選んだMEMBER 1枚だけがgreen_roomからhandへ移る",
            "candidate_zero: LIVEだけの控え室では候補が出ず、対象なし表示または自動解決になる",
        ],
        "expected_zone_moves": ["green_room selected MEMBER -> hand"],
        "expected_count_changes": ["candidate_multi/candidate_one: hand +1, green_room -1"],
        "expected_temporary_modifiers": [],
        "expected_cleanup": ["pendingなし", "temporary modifierなし"],
        "expected_ui": ["候補カード画像/名前/番号が一致", "LIVEカードは候補に出ない"],
        "expected_logs": ["[AUTO_EXT] or [AUTO]"],
        "expected_non_changes": ["LIVEカードはgreen_roomに残る", "発生源カードはステージに残る"],
    }


def tests() -> list[dict[str, Any]]:
    pl_deck = "LL-bp1-001,LL-bp5-001,LL-bp2-001,LL-bp3-001,LL-bp5-002"
    out: list[dict[str, Any]] = []
    for cn in ["PL!-PR-005", "PL!-PR-006", "PL!-PR-008"]:
        env = base_env(cn)
        env["LLOCG_START_DECK_EXACT"] = pl_deck
        out.append({"test_case_id": f"{cn}#A01#P3_draw_discard", "audit_id": f"{cn}#A01", "cardnumber": cn, "branch": "draw_discard", "condition_case": "success", "env": env})
    env = base_env("PL!-PR-005")
    env["LLOCG_START_DECK_EXACT"] = pl_deck
    out.append({"test_case_id": "PL!-PR-005#A01#P3_opponent_wait", "audit_id": "PL!-PR-005#A01", "cardnumber": "PL!-PR-005", "branch": "opponent_wait_all_cost2", "condition_case": "representative_manual_opponent", "env": env})
    env = base_env("PL!-PR-005")
    env["LLOCG_START_DECK_EXACT"] = pl_deck
    out.append({"test_case_id": "PL!-PR-005#A01#P3_choice_required", "audit_id": "PL!-PR-005#A01", "cardnumber": "PL!-PR-005", "branch": "choice_required", "condition_case": "no_selection", "env": env})

    env = base_env("LL-bp1-001")
    env["LLOCG_START_DECK_EXACT"] = "LL-bp5-002,PL!-PR-005,PL!-PR-006,LL-bp5-001"
    env["LLOCG_START_GREEN"] = "LL-bp2-001 LL-bp3-001 LL-bp5-001"
    out.append({"test_case_id": "LL-bp1-001#A01#P3_candidate_multi", "audit_id": "LL-bp1-001#A01", "cardnumber": "LL-bp1-001", "branch": "candidate_multi", "condition_case": "success", "env": env, "pick": "LL-bp2-001"})
    env = base_env("LL-bp1-001")
    env["LLOCG_START_DECK_EXACT"] = "LL-bp5-002,PL!-PR-005,PL!-PR-006,LL-bp5-001"
    env["LLOCG_START_GREEN"] = "LL-bp5-001"
    out.append({"test_case_id": "LL-bp1-001#A01#P3_candidate_zero", "audit_id": "LL-bp1-001#A01", "cardnumber": "LL-bp1-001", "branch": "candidate_zero", "condition_case": "no_valid_target", "env": env})
    env = base_env("LL-bp1-001")
    env["LLOCG_START_DECK_EXACT"] = "LL-bp5-002,PL!-PR-005,PL!-PR-006,LL-bp5-001"
    env["LLOCG_START_GREEN"] = "LL-bp2-001 LL-bp5-001"
    out.append({"test_case_id": "LL-bp1-001#A01#P3_candidate_one", "audit_id": "LL-bp1-001#A01", "cardnumber": "LL-bp1-001", "branch": "candidate_one", "condition_case": "single_valid_target", "env": env, "pick": "LL-bp2-001"})
    return out


def safe_name(test_case_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", test_case_id.replace("#", "_"))


def resolve_all_for_test(base: str, t: dict[str, Any], st: dict[str, Any], states: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], list[str], list[str]]:
    notes: list[str] = []
    issues: list[str] = []
    cn = t["cardnumber"]
    branch = t["branch"]
    hand = [str(x) for x in st.get("hand") or []]
    if cn not in hand:
        raise RuntimeError(f"{cn} not in hand")
    st = post(base, "play", {"hand_idx": hand.index(cn), "pos": "C"})
    states["01_triggered.json"] = st
    states["02_pending.json"] = st
    if branch == "draw_discard":
        choice = "カードを1枚引き、手札を1枚控え室に置く"
        st = post(base, "resolve_pending", {"idx": 0, "choice": choice})
        states["03_after_selection.json"] = st
        opts = list((st.get("pending") or [{}])[0].get("options") or []) if st.get("pending") else []
        if opts:
            st = post(base, "resolve_pending", {"idx": 0, "choice": str(opts[0])})
        else:
            issues.append("discard options missing")
        states["04_resolved.json"] = st
    elif branch == "opponent_wait_all_cost2":
        choice = "相手のステージにいるすべてのコスト2以下のメンバーをウェイトにする"
        st = post(base, "resolve_pending", {"idx": 0, "choice": choice})
        states["03_after_selection.json"] = st
        # Runtime models opponent board as a manual count. Select 2 as representative.
        if st.get("pending"):
            st = post(base, "resolve_pending", {"idx": 0, "choice": "2"})
        states["04_resolved.json"] = st
        issues.append("opponent individual stage is not modeled; cost filter cannot be state-verified")
    elif branch == "choice_required":
        st = post(base, "next", {})
        states["03_after_selection.json"] = st
        states["04_resolved.json"] = st
        if not st.get("pending"):
            issues.append("choice-required mode was cleared by next/no-selection")
        else:
            notes.append("pending remained after next/no-selection")
    elif branch in {"candidate_multi", "candidate_one"}:
        pick = t.get("pick", "LL-bp2-001")
        states["03_after_selection.json"] = st
        st = post(base, "resolve_pending", {"idx": 0, "choice": pick})
        states["04_resolved.json"] = st
    elif branch == "candidate_zero":
        if st.get("pending"):
            st = post(base, "resolve_pending", {"idx": 0, "choice": "ok"})
        states["03_after_selection.json"] = st
        states["04_resolved.json"] = st
    else:
        raise RuntimeError(f"unknown branch {branch}")
    states["05_after_cleanup.json"] = states["04_resolved.json"]
    return st, notes, issues


def expected_for(t: dict[str, Any]) -> dict[str, Any]:
    if t["cardnumber"].startswith("PL!-PR"):
        return pl_expected(t["cardnumber"], t["test_case_id"], t["branch"])
    return ll_expected(t["test_case_id"], t["branch"])


def temp_residue(st: dict[str, Any]) -> list[str]:
    residues = []
    if st.get("pending"):
        residues.append("pending_not_empty")
    for pos, slot in ((st.get("stage") or {}) if isinstance(st.get("stage"), dict) else {}).items():
        if not isinstance(slot, dict):
            continue
        for key in ["temp_hearts", "temp_blade", "heart_replace_color"]:
            val = slot.get(key)
            if val not in (None, "", {}, [], 0):
                residues.append(f"stage.{pos}.{key}")
    for key in ["temporary_modifiers", "live_temp_modifiers", "turn_temp_modifiers"]:
        if st.get(key):
            residues.append(key)
    return residues


def assert_result(t: dict[str, Any], states: dict[str, dict[str, Any]], undo_diff: list[dict[str, Any]]) -> tuple[str, str, str, str, str, list[str]]:
    branch = t["branch"]
    initial = states["00_initial.json"]
    triggered = states.get("01_triggered.json", {})
    pending = states.get("02_pending.json", {})
    resolved = states.get("04_resolved.json", {})
    cleanup = states.get("05_after_cleanup.json", resolved)
    issues: list[str] = []
    state_result = "STATE_PASS"
    target_filter = "TARGET_FILTER_NOT_APPLICABLE"
    cleanup_result = "CLEANUP_PASS" if not temp_residue(cleanup) else "CLEANUP_RESIDUE"
    undo_result = "UNDO_PASS" if not undo_diff else "UNDO_STATE_MISMATCH"

    if not pending.get("pending"):
        issues.append("pending not created")
    if branch == "draw_discard":
        if resolved.get("pending"):
            issues.append("pending remains after draw/discard")
        if len(resolved.get("deck") or []) != len(initial.get("deck") or []) - 1:
            issues.append("deck count did not decrease by 1")
        if len(resolved.get("green_room") or []) != len(initial.get("green_room") or []) + 1:
            issues.append("green_room count did not increase by 1")
        stage_c = ((resolved.get("stage") or {}).get("C") or {}).get("cardnumber")
        if stage_c != t["cardnumber"]:
            issues.append("source card not on stage C after resolution")
        target_filter = "TARGET_FILTER_PASS" if t["cardnumber"] not in ((states.get("03_after_selection.json", {}).get("pending") or [{}])[0].get("options") or []) else "FAIL_TARGET_FILTER"
    elif branch == "opponent_wait_all_cost2":
        if int(resolved.get("opponent_wait_count") or 0) != 2:
            issues.append("opponent_wait_count was not updated by manual resolution")
        issues.append("cannot verify individual opponent cost<=2 filtering because runtime tracks only count")
        target_filter = "FAIL_TARGET_FILTER"
    elif branch == "choice_required":
        if not resolved.get("pending"):
            issues.append("choice required pending cleared by next/no-selection")
        target_filter = "TARGET_FILTER_NOT_APPLICABLE"
    elif branch in {"candidate_multi", "candidate_one"}:
        pick = t.get("pick")
        if pick not in (resolved.get("hand") or []):
            issues.append("picked member not moved to hand")
        if pick in (resolved.get("green_room") or []):
            issues.append("picked member still in green_room")
        if "LL-bp5-001" not in (resolved.get("green_room") or []):
            issues.append("invalid LIVE candidate moved or removed")
        cand = (pending.get("pending") or [{}])[0].get("candidates") or []
        if "LL-bp5-001" in cand:
            issues.append("LIVE card appeared as valid candidate")
        target_filter = "TARGET_FILTER_PASS" if not any("candidate" in x for x in issues) else "FAIL_TARGET_FILTER"
    elif branch == "candidate_zero":
        if resolved.get("pending"):
            issues.append("candidate_zero pending remains")
        if len(resolved.get("hand") or []) != len(initial.get("hand") or []) - 1:
            issues.append("candidate_zero changed hand unexpectedly beyond played source")
        target_filter = "TARGET_FILTER_PASS"

    if issues:
        if any("cost<=2" in x or "candidate" in x for x in issues):
            state_result = "FAIL_TARGET_FILTER"
        elif any("pending" in x for x in issues):
            state_result = "FAIL_CLEANUP"
        else:
            state_result = "FAIL_BEHAVIOR"
    final = "PASS_STATE_UI_PENDING" if state_result == "STATE_PASS" and cleanup_result == "CLEANUP_PASS" and undo_result == "UNDO_PASS" else state_result
    if cleanup_result != "CLEANUP_PASS":
        final = "FAIL_CLEANUP"
    if undo_result != "UNDO_PASS":
        final = "FAIL_UNDO"
    return state_result, target_filter, cleanup_result, undo_result, final, issues


def run_one(t: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    tid = t["test_case_id"]
    sname = safe_name(tid)
    state_dir = OUT / "state" / sname
    log_path = OUT / "logs" / f"{sname}.log"
    cmd_path = OUT / "commands" / "candidates" / f"{sname}.command.sh"
    steps_path = OUT / "commands" / "candidates" / f"{sname}.steps.md"
    expected = expected_for(t)
    (OUT / "expected" / f"{sname}.json").write_text(json.dumps(expected, ensure_ascii=False, indent=2), encoding="utf-8")
    cmd_path.write_text(command_text(t["env"], 8787), encoding="utf-8")
    steps_path.write_text(f"# {tid}\n\n1. 起動する。\n2. 手札の `{t['cardnumber']}` をCへ登場。\n3. branch `{t['branch']}` の選択/解決を行う。\n4. `/state?view=debug` とUI表示を確認する。\n", encoding="utf-8")

    proc = None
    ui_rows: list[dict[str, Any]] = []
    issue_rows: list[dict[str, Any]] = []
    try:
        proc, base, port, st0 = start_server(t["env"], log_path)
        cmd_path.write_text(command_text(t["env"], port), encoding="utf-8")
        shutil.copy2(cmd_path, OUT / "commands" / "accepted" / cmd_path.name)
        shutil.copy2(steps_path, OUT / "commands" / "accepted" / steps_path.name)
        states: dict[str, dict[str, Any]] = {"00_initial.json": st0}
        resolved, notes, runtime_issues = resolve_all_for_test(base, t, st0, states)
        # Undo back to initial. Multiple mutating commands were used, so unwind until comparable or max 6.
        undo_state = resolved
        undo_diff: list[dict[str, Any]] = []
        for _ in range(6):
            undo_state = post(base, "undo", {})
            undo_diff = diff(normalize_state(state_subset(st0)), normalize_state(state_subset(undo_state)))
            if not undo_diff:
                break
        states["06_after_undo.json"] = undo_state

        for name, st in states.items():
            save_state(state_dir, name, st)
        (state_dir / "diff_initial_to_resolved.json").write_text(json.dumps(diff(normalize_state(state_subset(st0)), normalize_state(state_subset(states["04_resolved.json"]))), ensure_ascii=False, indent=2), encoding="utf-8")
        (state_dir / "diff_resolved_to_cleanup.json").write_text(json.dumps(diff(normalize_state(state_subset(states["04_resolved.json"])), normalize_state(state_subset(states["05_after_cleanup.json"]))), ensure_ascii=False, indent=2), encoding="utf-8")
        (state_dir / "diff_initial_to_undo.json").write_text(json.dumps(undo_diff, ensure_ascii=False, indent=2), encoding="utf-8")
        (state_dir / "normalization_notes.md").write_text("Excluded noise keys: " + ", ".join(sorted(NOISE_KEYS)) + "\n", encoding="utf-8")

        state_result, target_filter, cleanup_result, undo_result, final, assert_issues = assert_result(t, states, undo_diff)
        log_path.write_text(json.dumps({
            "port": port,
            "notes": notes,
            "runtime_issues": runtime_issues,
            "assert_issues": assert_issues,
            "log_tail": (states["04_resolved.json"].get("log") or [])[-80:],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        ui_rows.extend([
            {"test_case_id": tid, "screen": "private", "check_item": "popup/pending", "expected": "; ".join(expected["expected_ui"]), "actual": "state pending saved; screenshot not automated in this run", "result": "NEEDS_MANUAL_UI_CONFIRMATION", "evidence": str(state_dir / "02_pending.json"), "notes": "UI result separated from state result"},
            {"test_case_id": tid, "screen": "public", "check_item": "public UI residue", "expected": "popup residueなし/public state反映", "actual": "not visually checked", "result": "NEEDS_MANUAL_UI_CONFIRMATION", "evidence": "", "notes": ""},
        ])
        all_issues = runtime_issues + assert_issues
        if all_issues:
            issue_rows.append({
                "issue_id": f"P3-{sname}",
                "severity": "P1" if "opponent" in " ".join(all_issues) else "P2",
                "cardnumber": t["cardnumber"],
                "audit_id": t["audit_id"],
                "test_case_id": tid,
                "category": final if final.startswith("FAIL") else "NEEDS_MANUAL_CONFIRMATION",
                "effect_text": expected["effect_text"],
                "setup": json.dumps(t["env"], ensure_ascii=False),
                "command_file": str((OUT / "commands" / "accepted" / cmd_path.name).relative_to(OUT)),
                "steps_file": str((OUT / "commands" / "accepted" / steps_path.name).relative_to(OUT)),
                "expected": json.dumps(expected, ensure_ascii=False),
                "actual": "; ".join(all_issues),
                "state_diff": str((state_dir / "diff_initial_to_resolved.json").relative_to(OUT)),
                "log_file": str(log_path.relative_to(OUT)),
                "related_code": "llocg_ui/engine.py; llocg_ui/server.py",
                "reproducible": "YES",
                "notes": "Runtime was not modified.",
            })
        return {
            "test_case_id": tid,
            "audit_id": t["audit_id"],
            "cardnumber": t["cardnumber"],
            "branch": t["branch"],
            "condition_case": t["condition_case"],
            "command_status": "ACCEPTED",
            "server_started": "YES",
            "trigger_reached": "YES" if states.get("02_pending.json", {}).get("pending") else "NO",
            "pending_created": "YES" if states.get("02_pending.json", {}).get("pending") else "NO",
            "effect_resolved": "YES" if not states.get("04_resolved.json", {}).get("pending") or t["branch"] == "choice_required" else "NO",
            "state_checked": "YES",
            "state_result": state_result,
            "target_filter_result": target_filter,
            "cleanup_checked": "YES",
            "cleanup_result": cleanup_result,
            "undo_checked": "YES",
            "undo_result": undo_result,
            "ui_checked": "NO",
            "ui_result": "NEEDS_MANUAL_UI_CONFIRMATION",
            "final_result": final,
            "evidence": str(state_dir.relative_to(OUT)),
            "notes": "; ".join(notes + runtime_issues + assert_issues),
        }, ui_rows, issue_rows
    except Exception as e:
        log_path.write_text(f"exception={e!r}\n", encoding="utf-8")
        shutil.copy2(cmd_path, OUT / "commands" / "rejected" / cmd_path.name)
        shutil.copy2(steps_path, OUT / "commands" / "rejected" / steps_path.name)
        return {
            "test_case_id": tid,
            "audit_id": t["audit_id"],
            "cardnumber": t["cardnumber"],
            "branch": t["branch"],
            "condition_case": t["condition_case"],
            "command_status": "REJECTED",
            "server_started": "NO",
            "trigger_reached": "NO",
            "pending_created": "NO",
            "effect_resolved": "NO",
            "state_checked": "NO",
            "state_result": "BLOCKED_RUNTIME",
            "target_filter_result": "BLOCKED_RUNTIME",
            "cleanup_checked": "NO",
            "cleanup_result": "BLOCKED_RUNTIME",
            "undo_checked": "NO",
            "undo_result": "UNDO_BLOCKED",
            "ui_checked": "NO",
            "ui_result": "NEEDS_MANUAL_UI_CONFIRMATION",
            "final_result": "BLOCKED_RUNTIME",
            "evidence": str(log_path.relative_to(OUT)),
            "notes": repr(e),
        }, ui_rows, issue_rows
    finally:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass


def meta() -> None:
    (OUT / "meta" / "git_head.txt").write_text(run_text(["git", "rev-parse", "HEAD"]), encoding="utf-8")
    (OUT / "meta" / "git_status_short.txt").write_text(run_text(["git", "status", "--short"]), encoding="utf-8")
    (OUT / "meta" / "git_diff_stat.txt").write_text(run_text(["git", "diff", "--stat"], timeout=30), encoding="utf-8")
    dbs = [ROOT / "llocg_db_out_full" / "cards_min_tokv1.json", ROOT / "llocg_db_out_full" / "cards_compiled_v7h.json"]
    (OUT / "meta" / "runtime_db_sha256.txt").write_text("\n".join(f"{sha256(p)}  {p}" for p in dbs) + "\n", encoding="utf-8")
    (OUT / "meta" / "runtime_environment.md").write_text(
        "# Runtime Environment\n\n"
        f"- audit_start: {datetime.now().isoformat()}\n"
        f"- phase2_path: {PHASE2}\n"
        f"- python: {sys.version.split()[0]}\n"
        f"- ports: {PORTS}\n"
        "- runtime_db: `./llocg_db_out_full/cards_min_tokv1.json`, `./llocg_db_out_full/cards_compiled_v7h.json`\n"
        "- launch: `python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port <port> --debug`\n",
        encoding="utf-8",
    )


def write_docs() -> None:
    (OUT / "tools" / "compare_cleanup_state.py").write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "a=json.load(open(sys.argv[1],encoding='utf-8'))\n"
        "b=json.load(open(sys.argv[2],encoding='utf-8'))\n"
        "def filt(x):\n"
        "    if isinstance(x,dict): return {k:filt(v) for k,v in x.items() if k not in {'timestamp','session','session_id'}}\n"
        "    if isinstance(x,list): return [filt(v) for v in x]\n"
        "    return x\n"
        "print(json.dumps([] if filt(a)==filt(b) else {'before':filt(a),'after':filt(b)}, ensure_ascii=False, indent=2))\n",
        encoding="utf-8",
    )
    (OUT / "docs" / "cleanup_check_method.md").write_text(
        "# Cleanup Check Method\n\n"
        "1. Save `04_resolved.json` after the final pending resolves.\n"
        "2. Save `05_after_cleanup.json` at the cleanup checkpoint. For non-temporary effects this is the resolved state.\n"
        "3. Compare pending, temp modifiers, selection state, public/popup residue, and turn-scoped flags.\n"
        "4. Any remaining pending or temporary field is a cleanup failure unless explicitly expected.\n",
        encoding="utf-8",
    )
    (OUT / "docs" / "state_assertion_method.md").write_text(
        "# State Assertion Method\n\n"
        "Expected JSON is written before execution. State snapshots are saved at initial, trigger, pending, after selection, resolved, cleanup, and undo. Diffs use a reduced state subset and exclude session/timestamp noise.\n",
        encoding="utf-8",
    )
    (OUT / "docs" / "next_expansion_plan.md").write_text(
        "# Next Expansion Plan\n\n"
        "Gate C is not opened in this run because the representative opponent-wait branch cannot verify individual opponent cost filtering in current runtime state. Next phase should either add non-mutating observation support or classify opponent-board effects as manual-counter routes before expanding.\n",
        encoding="utf-8",
    )


def write_static_and_db_placeholders() -> None:
    # Gate B is blocked in this run; do not pretend 136 abilities were expanded.
    write_csv(OUT / "static_reclassification_136.csv", [], [
        "audit_id", "cardnumber", "cardname", "previous_classification", "final_classification", "confidence", "reason", "evidence_file",
    ])
    write_csv(OUT / "db" / "db_mismatch_semantic_review.csv", [], [
        "audit_id", "cardnumber", "audit_text", "runtime_text", "compiled_text", "override_text",
        "difference_type", "semantic_impact", "runtime_behavior_risk", "recommended_source_of_truth",
        "evidence", "result", "notes",
    ])


def main() -> None:
    ensure_dirs()
    meta()
    write_docs()
    rows: list[dict[str, Any]] = []
    ui_rows: list[dict[str, Any]] = []
    issue_rows: list[dict[str, Any]] = []
    for t in tests():
        result, ui, issues = run_one(t)
        rows.append(result)
        ui_rows.extend(ui)
        issue_rows.extend(issues)
    pilot_fields = [
        "test_case_id", "audit_id", "cardnumber", "branch", "condition_case",
        "command_status", "server_started", "trigger_reached", "pending_created",
        "effect_resolved", "state_checked", "state_result", "target_filter_result",
        "cleanup_checked", "cleanup_result", "undo_checked", "undo_result",
        "ui_checked", "ui_result", "final_result", "evidence", "notes",
    ]
    write_csv(OUT / "pilot" / "pilot_test_results.csv", rows, pilot_fields)
    write_csv(OUT / "ui" / "ui_checklist.csv", ui_rows, [
        "test_case_id", "screen", "check_item", "expected", "actual", "result", "evidence", "notes",
    ])
    issue_fields = [
        "issue_id", "severity", "cardnumber", "audit_id", "test_case_id", "category",
        "effect_text", "setup", "command_file", "steps_file", "expected", "actual",
        "state_diff", "log_file", "related_code", "reproducible", "notes",
    ]
    write_csv(OUT / "pilot" / "behavioral_issues.csv", issue_rows, issue_fields)
    write_static_and_db_placeholders()

    counts = {
        "command_candidates": len(rows),
        "commands_accepted": sum(r["command_status"] == "ACCEPTED" for r in rows),
        "commands_rejected": sum(r["command_status"] == "REJECTED" for r in rows),
        "server_started": sum(r["server_started"] == "YES" for r in rows),
        "trigger_reached": sum(r["trigger_reached"] == "YES" for r in rows),
        "effect_resolved": sum(r["effect_resolved"] == "YES" for r in rows),
        "state_checked": sum(r["state_checked"] == "YES" for r in rows),
        "state_passed": sum(r["state_result"] == "STATE_PASS" for r in rows),
        "ui_checked": sum(r["ui_checked"] == "YES" for r in rows),
        "ui_passed": sum(r["ui_result"] == "UI_PASS" for r in rows),
        "cleanup_passed": sum(r["cleanup_result"] == "CLEANUP_PASS" for r in rows),
        "undo_passed": sum(r["undo_result"] == "UNDO_PASS" for r in rows),
        "full_pass": sum(r["final_result"] == "PASS_FULL" for r in rows),
        "behavioral_failures": len(issue_rows),
        "static_missing_implementation_candidates": 0,
        "static_confirmed_with_evidence": 0,
        "db_semantic_differences": 0,
    }
    write_csv(OUT / "coverage_phase3.csv", [{"metric": k, "count": v} for k, v in counts.items()], ["metric", "count"])
    gate_a = all(r["server_started"] == "YES" and r["trigger_reached"] == "YES" and r["effect_resolved"] == "YES" for r in rows if r["cardnumber"] in {"PL!-PR-005", "PL!-PR-006", "PL!-PR-008", "LL-bp1-001"})
    gate_b = (
        any(r["branch"] == "opponent_wait_all_cost2" and r["final_result"].startswith("PASS") for r in rows)
        and any(r["branch"] == "candidate_multi" and r["final_result"].startswith("PASS") for r in rows)
        and any(r["branch"] == "candidate_zero" and r["final_result"].startswith("PASS") for r in rows)
        and all(r["cleanup_result"] == "CLEANUP_PASS" for r in rows)
        and all(r["undo_result"] == "UNDO_PASS" for r in rows)
    )
    status = "PHASE3_PILOT_PASSED" if gate_a and gate_b else "PHASE3_BLOCKED"
    summary = [
        "# Pilot Summary",
        "",
        f"- status: {status}",
        f"- Gate A: {'PASS' if gate_a else 'BLOCKED'}",
        f"- Gate B: {'PASS' if gate_b else 'BLOCKED'}",
        "- Gate C: NOT_OPENED",
        "",
    ] + [f"- {k}: {v}" for k, v in counts.items()]
    (OUT / "pilot" / "pilot_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    report = [
        status,
        "",
        "# Final Report Phase 3",
        "",
        "Gate A→B→C order was preserved. Gate C was not opened because Gate B did not pass.",
        "",
        "The blocking item is the PL opponent-wait branch: current runtime does not model individual opponent stage cards, so cost<=2 filtering and already-wait/cost3 non-change cannot be state-verified. It resolves through a manual `opponent_wait_notify` count prompt.",
        "",
    ] + [f"- {k}: {v}" for k, v in counts.items()]
    (OUT / "final_report_phase3.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Loveca Effect Full Audit Phase 3\n\n"
        f"Status: `{status}`\n\n"
        "Outputs are limited to Phase 3 pilot/Gate A-B artifacts. Runtime and DB were not modified.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "gate_a": gate_a, "gate_b": gate_b, **counts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
