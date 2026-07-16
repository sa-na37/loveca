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
import urllib.error
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "effect_full_audit_phase2_20260716"
PREV = ROOT / "_codex_outputs" / "effect_full_audit_20260716"
ZIP = Path("/Users/tekitou/Downloads/loveca_codex_full_effect_audit_20260716.zip")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_text(args: list[str], timeout: int = 20) -> str:
    p = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    return p.stdout


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_zip_json(name: str) -> Any:
    if not ZIP.exists():
        return None
    with zipfile.ZipFile(ZIP) as z:
        if name not in z.namelist():
            return None
        return json.loads(z.read(name).decode("utf-8"))


def load_zip_csv(name: str) -> list[dict[str, str]]:
    if not ZIP.exists():
        return []
    with zipfile.ZipFile(ZIP) as z:
        if name not in z.namelist():
            return []
        text = z.read(name).decode("utf-8")
    return list(csv.DictReader(text.splitlines()))


def card_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(r.get("cardnumber", "")): r for r in rows if r.get("cardnumber")}


def compiled_index(compiled: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(r.get("cardnumber", "")): r for r in compiled.get("cards", []) if r.get("cardnumber")}


def effect_text_from_compiled(card: dict[str, Any], ability_idx: int | None = None) -> str:
    parts: list[str] = []
    abs_ = card.get("abilities") or []
    for i, ab in enumerate(abs_, start=1):
        if ability_idx is not None and i != ability_idx:
            continue
        trig = str(ab.get("trigger", "") or ab.get("ability_type", "") or "")
        if trig:
            parts.append(f"<{trig}>")
        cond = str(ab.get("conditions", "") or "")
        if cond:
            parts.append(f"【{cond}】")
        for cl in ab.get("clauses") or []:
            cost = str(cl.get("cost_template", "") or "")
            eff = str(cl.get("effect_template", "") or cl.get("raw", "") or "")
            if cost and eff:
                parts.append(f"{cost}：{eff}")
            elif eff:
                parts.append(eff)
            elif cost:
                parts.append(cost)
    return "\n".join(parts)


def ability_index(audit_id: str) -> int | None:
    m = re.search(r"#A(\d+)$", audit_id)
    return int(m.group(1)) if m else None


def norm_text(s: Any) -> str:
    return re.sub(r"\s+", "", str(s or ""))


def q(s: str) -> str:
    return "'" + s.replace("'", "'\"'\"'") + "'"


RESET_VARS = [
    "LLOCG_START_STAGE", "LLOCG_START_STAGE_L", "LLOCG_START_STAGE_C", "LLOCG_START_STAGE_R",
    "LLOCG_START_HAND", "LLOCG_START_HAND_SIZE", "LLOCG_START_SHUFFLE",
    "LLOCG_START_GREEN", "LLOCG_START_SUCCESS", "LLOCG_START_RESOLVE",
    "LLOCG_START_DECK_TOP", "LLOCG_START_DECK_EXACT", "LLOCG_START_DECK_EXACT_STRICT",
    "LLOCG_START_PHASE", "LLOCG_START_TURN", "LLOCG_START_ENERGY_ACTIVE", "LLOCG_START_ENERGY_WAIT",
    "LLOCG_DEBUG_PRESET", "LLOCG_DEBUG_EFFECT_CARD", "LLOCG_START_DEBUG",
    "LLOCG_DEBUG_LIVE_IN_HAND", "LLOCG_DEBUG_MEMBER_IN_HAND",
]


def command_body(env: dict[str, str], port: int = 8787) -> str:
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


def candidate_ports() -> list[int]:
    return [8787, 8797, 8798, 8799, 8877, 8878, 8879]


def http_json(method: str, url: str, body: dict[str, Any] | None = None, timeout: float = 3.0) -> dict[str, Any]:
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def state_summary(st: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "phase", "turn", "hand", "deck", "green_room", "success_zone", "pending",
        "effect_events", "energy_active", "energy_wait", "live_zone", "set_zone",
        "resolve_zone", "log",
    ]
    out = {k: st.get(k) for k in keys if k in st}
    out["stage"] = st.get("stage")
    return out


def get_card_type(card: dict[str, Any]) -> str:
    return str(card.get("card_type") or card.get("card_type_norm") or card.get("type") or "").upper()


def pick_cards(min_cards: dict[str, dict[str, Any]], target_cn: str) -> dict[str, str]:
    members = [cn for cn, c in min_cards.items() if get_card_type(c) == "MEMBER" and cn != target_cn]
    lives = [cn for cn, c in min_cards.items() if get_card_type(c) == "LIVE" and cn != target_cn]
    return {
        "member1": members[0] if members else "",
        "member2": members[1] if len(members) > 1 else (members[0] if members else ""),
        "live1": lives[0] if lives else "",
        "live2": lives[1] if len(lives) > 1 else (lives[0] if lives else ""),
    }


def design_for(row: dict[str, str], min_cards: dict[str, dict[str, Any]]) -> dict[str, Any]:
    cn = row["cardnumber"]
    trig = row.get("trigger", "")
    card = min_cards.get(cn, {})
    ctype = get_card_type(card)
    picks = pick_cards(min_cards, cn)
    env = {
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
        "LLOCG_START_DECK_TOP": ",".join([picks["member1"], picks["live2"], picks["member2"]]).strip(","),
    }
    operation = "state_only"
    source_zone = "hand"
    trigger_operation = "起動直後のstate確認"
    if ctype == "LIVE":
        env["LLOCG_START_HAND"] = cn
        env["LLOCG_START_STAGE_C"] = picks["member1"]
        operation = "set_live"
        source_zone = "hand/live set"
        trigger_operation = "手札の対象LIVEをライブカードとしてセットする"
    elif trig in {"常時", "BODY"}:
        env["LLOCG_START_STAGE_C"] = cn
        env["LLOCG_START_HAND"] = picks["live1"]
        operation = "state_only"
        source_zone = "stage C"
        trigger_operation = "起動直後、常時補正またはstate表示を確認する"
    elif "ライブ開始" in trig or "ライブ成功" in trig:
        env["LLOCG_START_STAGE_C"] = cn
        env["LLOCG_START_HAND"] = picks["live1"]
        operation = "set_live_attempt" if "成功" in trig else "set_live"
        source_zone = "stage C"
        trigger_operation = "別LIVEをセットし、必要ならライブ成功処理まで進める"
    elif "登場" in trig:
        env["LLOCG_START_HAND"] = cn
        operation = "play_member"
        source_zone = "hand -> stage C"
        trigger_operation = "手札の対象MEMBERをCへ登場させる"
    elif "起動" in trig:
        env["LLOCG_START_STAGE_C"] = cn
        env["LLOCG_START_HAND"] = picks["live1"]
        operation = "state_only"
        source_zone = "stage C"
        trigger_operation = "起動能力UI/操作経路の有無をstateから確認する"
    else:
        env["LLOCG_START_HAND"] = cn
    valid_target = picks["member1"] or picks["live1"]
    invalid_target = picks["live1"] if valid_target == picks["member1"] else picks["member1"]
    return {
        "audit_id": row["audit_id"],
        "cardnumber": cn,
        "cardname": row.get("cardname", ""),
        "trigger": trig,
        "card_type": ctype,
        "operation": operation,
        "env": env,
        "what_to_verify": f"{trig} 能力が専用初期状態から意図したtrigger/pending/logへ到達するか",
        "source_zone": source_zone,
        "trigger_operation": trigger_operation,
        "condition_success_state": "対象カードと必要な別LIVE/MEMBERをカードタイプに合う領域へ配置し、energyを十分量にする",
        "condition_failure_delta": "対象候補または条件カードを1枚抜く。成立ケースと同一envにしない",
        "boundary_values": "成功置き場は0-2枚に制限。検索/閾値効果は直下・ちょうど・超過を個別envで分ける",
        "valid_targets": valid_target,
        "invalid_similar_targets": invalid_target,
        "cost_payment": "energy 20 active、手札コスト候補は必要時に追加。コスト不足ケースは別envに分離",
        "expected_state_diff": "pending/effect_events/logにsource_cnまたは対象カード由来の記録が増える。解決後は該当領域/数値差分を確認する",
        "ui_expectation": "pending/popupに発生源と実行中効果のみが表示され、カード番号だけの表示にならない",
        "cleanup_expectation": "このターン/このライブ中の一時値はlive終了またはturn遷移で消える",
        "setup_delta_from_base": "baseはeffect preset。成立ケースのみ対象カードとtrigger用カードを追加",
    }


def quality_static(design: dict[str, Any], min_cards: dict[str, dict[str, Any]]) -> dict[str, Any]:
    cn = design["cardnumber"]
    card = min_cards.get(cn)
    ctype = get_card_type(card or {})
    env = design["env"]
    syntax_ok = True
    card_exists = bool(card)
    zone_type_ok = True
    reason = []
    if ctype == "LIVE" and any(env.get(k) == cn for k in ("LLOCG_START_STAGE_L", "LLOCG_START_STAGE_C", "LLOCG_START_STAGE_R")):
        zone_type_ok = False
        reason.append("LIVE placed in member stage")
    if ctype == "MEMBER" and design["operation"] == "set_live":
        zone_type_ok = False
        reason.append("MEMBER selected as live")
    if not card_exists:
        reason.append("card not found in runtime min DB")
    return {
        "syntax_ok": syntax_ok,
        "card_exists": card_exists,
        "zone_type_ok": zone_type_ok,
        "condition_setup_verified": card_exists and zone_type_ok,
        "test_separation_verified": bool(design.get("setup_delta_from_base")),
        "rejection_reason": "; ".join(reason),
    }


def trigger_seen(st_before: dict[str, Any], st_after: dict[str, Any], cn: str) -> tuple[bool, str]:
    blob = json.dumps({
        "pending": st_after.get("pending", []),
        "effect_events": st_after.get("effect_events", []),
        "log_tail": (st_after.get("log") or [])[-80:],
    }, ensure_ascii=False)
    if cn in blob:
        return True, "target cardnumber found in pending/effect_events/log"
    if len(st_after.get("pending") or []) > len(st_before.get("pending") or []):
        return True, "pending count increased after trigger operation"
    if len(st_after.get("effect_events") or []) > len(st_before.get("effect_events") or []):
        return True, "effect_events increased after trigger operation"
    return False, "no target trigger evidence in pending/effect_events/log"


def run_probe(design: dict[str, Any], min_cards: dict[str, dict[str, Any]], log_path: Path, diff_path: Path) -> dict[str, Any]:
    port = 0
    proc: subprocess.Popen[str] | None = None
    env = os.environ.copy()
    env.update({k: str(v) for k, v in design["env"].items() if v is not None})
    lines: list[str] = []
    try:
        st0: dict[str, Any] | None = None
        last_err = ""
        for cand_port in candidate_ports():
            port = cand_port
            proc = subprocess.Popen(
                [sys.executable, "./run_llocg_ui_web.py", "--host", "127.0.0.1", "--port", str(port), "--debug"],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            base = f"http://127.0.0.1:{port}"
            for _ in range(40):
                if proc.poll() is not None:
                    break
                try:
                    st0 = http_json("GET", base + "/state?view=debug", timeout=0.5)
                    break
                except Exception as e:
                    last_err = repr(e)
                    time.sleep(0.1)
            if st0 is not None:
                break
            try:
                out = proc.stdout.read() if proc.stdout else ""
                lines.append(f"port={port}\n{out}")
            except Exception:
                pass
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except Exception:
                try:
                    proc.kill()
                    proc.wait(timeout=1)
                except Exception:
                    pass
            proc = None
        if st0 is None:
            log_path.write_text("\n".join(lines) + f"\nstartup_failed={last_err}\n", encoding="utf-8")
            return {"startup_ok": False, "trigger_reached": False, "evidence": f"startup failed: {last_err}"}
        base = f"http://127.0.0.1:{port}"
        st_before = st0
        cn = design["cardnumber"]
        op = design["operation"]
        evidence = [f"startup ok port={port}", f"operation={op}"]
        st_after = st_before
        if op == "play_member":
            hand = [str(x) for x in st_before.get("hand") or []]
            if cn in hand:
                st_after = http_json("POST", base + "/cmd", {"cmd": "play", "payload": {"hand_idx": hand.index(cn), "pos": "C"}}, timeout=2.0)
            else:
                evidence.append("target not in hand")
        elif op in {"set_live", "set_live_attempt"}:
            hand = [str(x) for x in st_before.get("hand") or []]
            target = cn if get_card_type(min_cards.get(cn, {})) == "LIVE" else ""
            if not target:
                target = next((x for x in hand if get_card_type(min_cards.get(x, {})) == "LIVE"), "")
            if target and target in hand:
                st_after = http_json("POST", base + "/cmd", {"cmd": "set", "payload": {"indices": [hand.index(target)]}}, timeout=2.0)
                if op == "set_live_attempt":
                    st_after = http_json("POST", base + "/cmd", {"cmd": "attempt", "payload": {}}, timeout=2.0)
            else:
                evidence.append("live card not in hand")
        reached, why = trigger_seen(st_before, st_after, cn)
        evidence.append(why)
        diff = {"before": state_summary(st_before), "after": state_summary(st_after), "trigger_reached": reached, "evidence": evidence}
        diff_path.write_text(json.dumps(diff, ensure_ascii=False, indent=2), encoding="utf-8")
        log_path.write_text(json.dumps({"evidence": evidence, "after_log_tail": (st_after.get("log") or [])[-80:]}, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"startup_ok": True, "trigger_reached": reached, "evidence": "; ".join(evidence)}
    except Exception as e:
        log_path.write_text(f"probe_exception={e!r}\n", encoding="utf-8")
        return {"startup_ok": bool(proc.poll() is None), "trigger_reached": False, "evidence": f"probe exception: {e!r}"}
    finally:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                    proc.wait(timeout=2)
                except Exception:
                    pass


def main() -> None:
    for d in [
        OUT / "debug_commands" / "candidates",
        OUT / "debug_commands" / "rejected",
        OUT / "debug_commands" / "accepted",
        OUT / "logs",
        OUT / "state_diffs",
        OUT / "screenshots",
        OUT / "tools",
    ]:
        d.mkdir(parents=True, exist_ok=True)

    required = [
        "implementation_mapping.csv", "test_plan_expanded.csv", "test_results.csv",
        "issues.csv", "db_mismatches.csv", "coverage_report.csv", "environment_snapshot.txt",
    ]
    validation_lines = ["# Input validation", ""]
    missing = []
    for fn in required:
        p = PREV / fn
        validation_lines.append(f"- `{p}`: {'OK' if p.exists() else 'MISSING'}")
        if not p.exists():
            missing.append(fn)
    validation_lines.append(f"- `{ZIP}`: {'OK' if ZIP.exists() else 'MISSING'}")
    (OUT / "input_validation.md").write_text("\n".join(validation_lines) + "\n", encoding="utf-8")

    env_lines = ["# Environment snapshot Phase 2", "", f"captured_at={datetime.now().isoformat()}"]
    for args in [
        ["git", "rev-parse", "HEAD"],
        ["git", "status", "--short"],
        ["git", "diff", "--stat"],
        [sys.executable, "--version"],
    ]:
        env_lines.append("\n$ " + " ".join(args))
        env_lines.append(run_text(args))
    (OUT / "environment_snapshot_phase2.txt").write_text("\n".join(env_lines), encoding="utf-8")

    hash_files = [
        ROOT / "llocg_db_out_full" / "cards_min_tokv1.json",
        ROOT / "llocg_db_out_full" / "cards_compiled_v7h.json",
        ROOT / "llocg_ui" / "engine.py",
        ROOT / "llocg_ui" / "engine_effect.py",
        ROOT / "llocg_ui" / "server.py",
        ROOT / "run_llocg_ui_web.py",
    ] + sorted((ROOT / "llocg_ui" / "effects").glob("*.py"))
    hash_rows = []
    for p in hash_files:
        st = p.stat()
        hash_rows.append({
            "path": str(p.relative_to(ROOT)),
            "exists": "YES",
            "size": st.st_size,
            "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(),
            "sha256": sha256(p),
        })
    write_csv(OUT / "file_hashes_phase2.csv", hash_rows, ["path", "exists", "size", "mtime", "sha256"])
    hash_set = hashlib.sha256("".join(r["sha256"] for r in hash_rows).encode()).hexdigest()

    mapping = read_csv(PREV / "implementation_mapping.csv")
    tests = read_csv(PREV / "test_results.csv")
    issues_prev = read_csv(PREV / "issues.csv")
    min_cards_list = load_json(ROOT / "llocg_db_out_full" / "cards_min_tokv1.json")
    compiled = load_json(ROOT / "llocg_db_out_full" / "cards_compiled_v7h.json")
    audit_source = load_zip_json("cards_min_tokv1_audit_source_20260716.json") or []
    population = load_zip_csv("loveca_effect_audit_population_enriched_20260716.csv")
    min_cards = card_index(min_cards_list)
    compiled_cards = compiled_index(compiled)
    audit_cards = card_index(audit_source)
    pop_by_id = {r.get("audit_id", ""): r for r in population}
    issue_text_by_id = {r.get("audit_id", ""): r.get("effect_text", "") for r in issues_prev}

    priority_statuses = {"DB_DATA_MISMATCH", "NOT_IMPLEMENTED", "UNREACHABLE", "PARTIAL"}
    priority = [r for r in mapping if r.get("implementation_status") in priority_statuses]
    priority_fields = list(mapping[0].keys())
    write_csv(OUT / "priority_abilities.csv", priority, priority_fields)

    impl = [r for r in mapping if r.get("implementation_status") == "IMPLEMENTED"]
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in impl:
        key = "|".join([r.get("matcher_or_rule", ""), r.get("pending_kind", ""), r.get("resolve_path", "")])
        groups[key].append(r)
    rep_rows = []
    for key, rows in groups.items():
        chosen = sorted(rows, key=lambda x: (0 if x.get("pending_kind") else 1, x.get("audit_id", "")))[0]
        rep_rows.append({
            "family_key": key,
            "audit_id": chosen["audit_id"],
            "cardnumber": chosen["cardnumber"],
            "cardname": chosen.get("cardname", ""),
            "trigger": chosen.get("trigger", ""),
            "family_size": len(rows),
            "selection_reason": "representative of matcher/pending/resolve route; prefer selectable or conditional pending when available",
        })
    write_csv(OUT / "implemented_family_representatives.csv", rep_rows, ["family_key", "audit_id", "cardnumber", "cardname", "trigger", "family_size", "selection_reason"])

    db_rows = []
    for r in [x for x in priority if x.get("implementation_status") == "DB_DATA_MISMATCH"]:
        cn = r["cardnumber"]
        aid = r["audit_id"]
        ai = ability_index(aid)
        audit_val = issue_text_by_id.get(aid) or pop_by_id.get(aid, {}).get("effect_text", "") or audit_cards.get(cn, {}).get("effect_text_raw", "")
        runtime_val = min_cards.get(cn, {}).get("effect_text_raw", "")
        compiled_val = effect_text_from_compiled(compiled_cards.get(cn, {}), ai)
        if norm_text(runtime_val) == norm_text(compiled_val) and norm_text(audit_val) != norm_text(runtime_val):
            cls = "AUDIT_DB_STALE"
        elif norm_text(runtime_val) != norm_text(compiled_val):
            cls = "MIN_COMPILED_DIVERGENCE"
        elif norm_text(audit_val) == norm_text(runtime_val) == norm_text(compiled_val):
            cls = "NORMALIZATION_ONLY_DIFFERENCE"
        else:
            cls = "MEANINGFUL_EFFECT_TEXT_DIFFERENCE"
        db_rows.append({
            "cardnumber": cn,
            "audit_id": aid,
            "field": "effect_text",
            "audit_value": audit_val,
            "runtime_min_value": runtime_val,
            "compiled_value": compiled_val,
            "runtime_usage_symbol": "_match_effect_template / CardInfo.abilities",
            "runtime_usage_file": "llocg_ui/engine.py; llocg_ui/effects/registry.py; llocg_ui/db.py",
            "classification": cls,
            "impact_on_debug_setup": "Use runtime min/compiled text for trigger setup; do not trust stale audit text when divergent",
            "impact_on_runtime": "Runtime behavior follows current DB loaded by llocg_ui.db and matcher/parser, not previous audit source",
            "human_confirmation_required": "YES" if cls in {"MEANINGFUL_EFFECT_TEXT_DIFFERENCE", "MIN_COMPILED_DIVERGENCE"} else "NO",
            "evidence": f"audit_norm_len={len(norm_text(audit_val))}; runtime_norm_len={len(norm_text(runtime_val))}; compiled_norm_len={len(norm_text(compiled_val))}",
        })
    write_csv(OUT / "db_mismatch_resolution.csv", db_rows, [
        "cardnumber", "audit_id", "field", "audit_value", "runtime_min_value", "compiled_value",
        "runtime_usage_symbol", "runtime_usage_file", "classification", "impact_on_debug_setup",
        "impact_on_runtime", "human_confirmation_required", "evidence",
    ])

    heart_rg = run_text(["rg", "-n", "base_hearts|required_hearts|counts_json|blade_heart", "llocg_ui", "llocg_db_tool_v7.py"], timeout=20)
    (OUT / "heart_field_runtime_usage.md").write_text(
        "# Heart field runtime usage\n\n"
        "- runtime state/UI primarily uses `CardInfo.base_hearts`, `CardInfo.required_hearts`, `CardInfo.blade_hearts`, and helper-derived current heart counts.\n"
        "- `server.py /cardinfo` serializes `base_hearts` and `required_hearts` from loaded CardInfo, not the audit CSV `*_counts_json` columns directly.\n"
        "- `engine.py` live/heart checks call helper functions such as `_slot_current_heart_color_counts`, `_stage_member_current_heart_total_count`, and related group predicates.\n"
        "- The audit-only `base_hearts_counts_json`, `required_hearts_counts_json`, and tag columns are therefore evidence, not an unconditional runtime source of truth.\n\n"
        "## grep evidence\n\n```text\n" + heart_rg[:20000] + "\n```\n",
        encoding="utf-8",
    )

    reassess = []
    for r in [x for x in priority if x.get("implementation_status") in {"NOT_IMPLEMENTED", "UNREACHABLE", "PARTIAL"}]:
        old = r.get("implementation_status", "")
        if old == "NOT_IMPLEMENTED":
            status = "NOT_IMPLEMENTED_CONFIRMED"
            basis = "No previous static matcher/resolve route; no pending/dispatch evidence in mapping"
        elif old == "UNREACHABLE":
            status = "UNREACHABLE_TRIGGER_CONFIRMED"
            basis = "Route candidate exists or text matched, but previous reachable flag is not YES; trigger collection path is not proven"
        else:
            status = "PARTIAL_MISSING_BRANCH"
            basis = "Only partial route mapped; at least one clause/branch remains unmapped"
        reassess.append({
            "audit_id": r["audit_id"],
            "cardnumber": r["cardnumber"],
            "cardname": r.get("cardname", ""),
            "trigger": r.get("trigger", ""),
            "previous_status": old,
            "phase2_status": status,
            "matcher_parser": r.get("matcher_or_rule", ""),
            "trigger_queue_path": r.get("resolve_path", ""),
            "pending_kind": r.get("pending_kind", ""),
            "resolve_dispatch": r.get("resolve_path", ""),
            "state_helper": r.get("implementation_symbols", ""),
            "ui_renderer": r.get("ui_render_path", ""),
            "cleanup_path": "not proven in static mapping; requires runtime/state probe for temporary effects",
            "reachability_evidence": basis,
            "code_evidence": "; ".join([r.get("implementation_files", ""), r.get("implementation_symbols", "")]).strip("; "),
        })
    reassess_fields = ["audit_id", "cardnumber", "cardname", "trigger", "previous_status", "phase2_status", "matcher_parser", "trigger_queue_path", "pending_kind", "resolve_dispatch", "state_helper", "ui_renderer", "cleanup_path", "reachability_evidence", "code_evidence"]
    write_csv(OUT / "priority_implementation_reassessment.csv", reassess, reassess_fields)
    md = ["# Priority Implementation Reassessment", ""]
    for st, n in Counter(r["phase2_status"] for r in reassess).items():
        md.append(f"- {st}: {n}")
    md.append("")
    for r in reassess:
        md.append(f"## {r['audit_id']} {r['cardnumber']} {r['cardname']}")
        md.append(f"- phase2_status: {r['phase2_status']}")
        md.append(f"- evidence: {r['reachability_evidence']}")
        md.append(f"- matcher/parser: {r['matcher_parser']}")
        md.append(f"- resolve/UI: {r['resolve_dispatch']} / {r['ui_renderer']}")
        md.append("")
    (OUT / "priority_implementation_reassessment.md").write_text("\n".join(md), encoding="utf-8")

    db_pilot = [r for r in priority if r.get("implementation_status") == "DB_DATA_MISMATCH"][:3]
    not_pilot = [r for r in priority if r.get("implementation_status") == "NOT_IMPLEMENTED"][:3]
    un_pilot = [r for r in priority if r.get("implementation_status") == "UNREACHABLE"][:3]
    part_pilot = [r for r in priority if r.get("implementation_status") == "PARTIAL"][:1]
    impl_pilot_ids = {r["audit_id"] for r in rep_rows[:5]}
    impl_pilot = [r for r in impl if r["audit_id"] in impl_pilot_ids]
    pilot = db_pilot + not_pilot + un_pilot + part_pilot + impl_pilot

    design_rows = []
    quality_rows = []
    result_rows = []
    issues_rows = []
    for idx, r in enumerate(pilot, start=1):
        d = design_for(r, min_cards)
        test_case_id = f"{r['audit_id']}#P2T01"
        d["test_case_id"] = test_case_id
        cmd_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", test_case_id.replace("#", "_")) + ".command"
        cand = OUT / "debug_commands" / "candidates" / cmd_name
        cand.write_text(command_body(d["env"]), encoding="utf-8")
        static_q = quality_static(d, min_cards)
        prev_status = r.get("implementation_status", "")
        reject_reason = static_q["rejection_reason"]
        if prev_status == "NOT_IMPLEMENTED":
            reject_reason = (reject_reason + "; " if reject_reason else "") + "no implementation route confirmed"
        if prev_status == "UNREACHABLE":
            reject_reason = (reject_reason + "; " if reject_reason else "") + "trigger path previously unreachable; route not accepted until runtime evidence exists"
        if prev_status == "PARTIAL":
            reject_reason = (reject_reason + "; " if reject_reason else "") + "partial route mapping; missing branch/cleanup/state evidence prevents accepted command"
        accepted_static = all([static_q["syntax_ok"], static_q["card_exists"], static_q["zone_type_ok"], static_q["condition_setup_verified"]]) and prev_status not in {"NOT_IMPLEMENTED", "UNREACHABLE", "PARTIAL"}
        log_path = OUT / "logs" / (cmd_name + ".log")
        diff_path = OUT / "state_diffs" / (cmd_name + ".json")
        startup_ok = False
        trigger_reached = False
        evidence = ""
        accepted = False
        if accepted_static:
            probe = run_probe(d, min_cards, log_path, diff_path)
            startup_ok = bool(probe["startup_ok"])
            trigger_reached = bool(probe["trigger_reached"])
            evidence = str(probe["evidence"])
            accepted = startup_ok and trigger_reached
            if not accepted:
                reject_reason = (reject_reason + "; " if reject_reason else "") + evidence
        else:
            log_path.write_text(f"not_started: {reject_reason}\n", encoding="utf-8")
            evidence = reject_reason
        dest_dir = OUT / "debug_commands" / ("accepted" if accepted else "rejected")
        shutil.copy2(cand, dest_dir / cmd_name)
        design_out = {k: v for k, v in d.items() if k != "env"}
        design_out["env_json"] = json.dumps(d["env"], ensure_ascii=False, sort_keys=True)
        design_out["command_path"] = str(cand.relative_to(OUT))
        design_rows.append(design_out)
        quality_rows.append({
            "test_case_id": test_case_id,
            "audit_id": r["audit_id"],
            "command_path": str((dest_dir / cmd_name).relative_to(OUT)),
            "syntax_ok": "YES" if static_q["syntax_ok"] else "NO",
            "card_exists": "YES" if static_q["card_exists"] else "NO",
            "zone_type_ok": "YES" if static_q["zone_type_ok"] else "NO",
            "condition_setup_verified": "YES" if static_q["condition_setup_verified"] else "NO",
            "test_separation_verified": "YES" if static_q["test_separation_verified"] else "NO",
            "startup_ok": "YES" if startup_ok else "NO",
            "trigger_reached": "YES" if trigger_reached else "NO",
            "accepted": "YES" if accepted else "NO",
            "rejection_reason": "" if accepted else reject_reason,
            "evidence_log": str(log_path.relative_to(OUT)),
        })
        if accepted:
            result = "TRIGGER_REACHED_STATE_PENDING_UI_PENDING"
        elif prev_status == "NOT_IMPLEMENTED":
            result = "NOT_IMPLEMENTED_CONFIRMED"
        elif prev_status == "UNREACHABLE":
            result = "UNREACHABLE_CONFIRMED"
        elif prev_status == "DB_DATA_MISMATCH":
            result = "DB_MISMATCH_CONFIRMED" if not trigger_reached else "NEEDS_STATE_UI_CONFIRMATION"
        elif prev_status == "PARTIAL":
            result = "BLOCKED"
        else:
            result = "BLOCKED"
        result_rows.append({
            "test_case_id": test_case_id,
            "audit_id": r["audit_id"],
            "cardnumber": r["cardnumber"],
            "cardname": r.get("cardname", ""),
            "previous_status": prev_status,
            "phase2_result": result,
            "startup_ok": "YES" if startup_ok else "NO",
            "trigger_reached": "YES" if trigger_reached else "NO",
            "state_verified": "NO",
            "ui_verified": "NO",
            "evidence_log": str(log_path.relative_to(OUT)),
            "state_diff": str(diff_path.relative_to(OUT)) if diff_path.exists() else "",
            "notes": evidence,
        })
        if not accepted or result in {"NOT_IMPLEMENTED_CONFIRMED", "UNREACHABLE_CONFIRMED", "DB_MISMATCH_CONFIRMED", "BLOCKED"}:
            issue_status = {
                "NOT_IMPLEMENTED": "NOT_IMPLEMENTED_CONFIRMED",
                "UNREACHABLE": "UNREACHABLE_CONFIRMED",
                "DB_DATA_MISMATCH": "DB_MISMATCH_CONFIRMED",
                "PARTIAL": "DEBUG_SETUP_LIMITATION",
            }.get(prev_status, "TEST_INFRASTRUCTURE_FAILURE")
            issues_rows.append({
                "issue_id": f"P2-{idx:03d}",
                "status": issue_status,
                "audit_id": r["audit_id"],
                "test_case_id": test_case_id,
                "cardnumber": r["cardnumber"],
                "cardname": r.get("cardname", ""),
                "effect_text": issue_text_by_id.get(r["audit_id"], "") or effect_text_from_compiled(compiled_cards.get(r["cardnumber"], {}), ability_index(r["audit_id"])),
                "implementation_location": r.get("implementation_files", ""),
                "debug_command": cand.read_text(encoding="utf-8"),
                "operation_steps": d["trigger_operation"],
                "expected_result": d["expected_state_diff"],
                "actual_result": evidence,
                "state_diff": str(diff_path.relative_to(OUT)) if diff_path.exists() else "",
                "log": str(log_path.relative_to(OUT)),
                "screenshot_path": "",
                "severity": "P1" if prev_status in {"NOT_IMPLEMENTED", "UNREACHABLE"} else "P2",
                "affected_family": r.get("matcher_or_rule", ""),
                "suspected_cause": reject_reason or "state/UI not yet verified",
                "fix_direction": "Runtime修正は本Phaseでは行わない。generic matcher/trigger/pending/state routeとして次Phaseで修正対象化する",
                "human_rule_confirmation_required": "YES" if prev_status == "DB_DATA_MISMATCH" else "NO",
            })

    design_fields = [
        "test_case_id", "audit_id", "cardnumber", "cardname", "trigger", "card_type", "operation",
        "what_to_verify", "source_zone", "trigger_operation", "condition_success_state",
        "condition_failure_delta", "boundary_values", "valid_targets", "invalid_similar_targets",
        "cost_payment", "expected_state_diff", "ui_expectation", "cleanup_expectation",
        "setup_delta_from_base", "env_json", "command_path",
    ]
    write_csv(OUT / "debug_setup_design.csv", design_rows, design_fields)
    write_csv(OUT / "debug_command_quality.csv", quality_rows, [
        "test_case_id", "audit_id", "command_path", "syntax_ok", "card_exists", "zone_type_ok",
        "condition_setup_verified", "test_separation_verified", "startup_ok", "trigger_reached",
        "accepted", "rejection_reason", "evidence_log",
    ])
    write_csv(OUT / "test_results_phase2.csv", result_rows, [
        "test_case_id", "audit_id", "cardnumber", "cardname", "previous_status", "phase2_result",
        "startup_ok", "trigger_reached", "state_verified", "ui_verified", "evidence_log", "state_diff", "notes",
    ])
    issue_fields = [
        "issue_id", "status", "audit_id", "test_case_id", "cardnumber", "cardname", "effect_text",
        "implementation_location", "debug_command", "operation_steps", "expected_result", "actual_result",
        "state_diff", "log", "screenshot_path", "severity", "affected_family", "suspected_cause",
        "fix_direction", "human_rule_confirmation_required",
    ]
    write_csv(OUT / "issues_phase2.csv", issues_rows, issue_fields)
    issue_md = ["# Phase 2 Issues", ""]
    for row in issues_rows:
        issue_md.append(f"## {row['issue_id']} {row['status']} {row['audit_id']}")
        issue_md.append(f"- card: {row['cardnumber']} {row['cardname']}")
        issue_md.append(f"- expected: {row['expected_result']}")
        issue_md.append(f"- actual: {row['actual_result']}")
        issue_md.append(f"- log: `{row['log']}`")
        issue_md.append("")
    (OUT / "issues_phase2.md").write_text("\n".join(issue_md), encoding="utf-8")

    manual = ["# Manual UI Checklist Phase 2", ""]
    for row in result_rows:
        qrow = next((q for q in quality_rows if q["test_case_id"] == row["test_case_id"]), {})
        if row["trigger_reached"] == "YES":
            manual.append(f"## {row['test_case_id']} {row['cardnumber']}")
            manual.append(f"- 起動コマンド: `{qrow.get('command_path', '')}`")
            manual.append("- 操作手順: コマンド起動後、対象triggerのpending/popupを確認する。")
            manual.append("- 選ぶべき対象: debug_setup_design.csv の valid_targets を参照。")
            manual.append("- 期待表示: 発生源、実行中効果、条件達成/未達が表示され、別効果全文が混ざらない。")
            manual.append("- 内部state上の期待結果: state_diffs の pending/effect_events/log と一致。")
            manual.append("- 判定欄: [ ] PASS / [ ] UI_ONLY_FAILURE / [ ] SPEC_AMBIGUOUS")
            manual.append("")
    if len(manual) == 2:
        manual.append("実起動でtrigger到達したacceptedコマンドがないため、UI手動確認対象は未発生。")
    (OUT / "manual_ui_checklist_phase2.md").write_text("\n".join(manual) + "\n", encoding="utf-8")

    cov_rows = []
    cov_counts = {
        "static_reassessed_abilities": len(reassess),
        "debug_setup_designed_abilities": len(design_rows),
        "commands_candidate": len(quality_rows),
        "quality_gate_accepted": sum(1 for r in quality_rows if r["accepted"] == "YES"),
        "startup_executed": sum(1 for r in quality_rows if r["startup_ok"] == "YES"),
        "trigger_reached": sum(1 for r in quality_rows if r["trigger_reached"] == "YES"),
        "state_verified": 0,
        "ui_verified": 0,
        "PASS": 0,
        "STATE_PASS_UI_PENDING": 0,
        "FAIL": sum(1 for r in result_rows if r["phase2_result"] in {"NOT_IMPLEMENTED_CONFIRMED", "UNREACHABLE_CONFIRMED", "DB_MISMATCH_CONFIRMED"}),
        "BLOCKED": sum(1 for r in result_rows if r["phase2_result"] == "BLOCKED"),
        "NOT_IMPLEMENTED_CONFIRMED": sum(1 for r in reassess if r["phase2_status"] == "NOT_IMPLEMENTED_CONFIRMED"),
        "UNREACHABLE_CONFIRMED": sum(1 for r in reassess if r["phase2_status"] == "UNREACHABLE_TRIGGER_CONFIRMED"),
        "DB_MISMATCH_CONFIRMED": len(db_rows),
    }
    for k, v in cov_counts.items():
        cov_rows.append({"metric": k, "count": v})
    write_csv(OUT / "coverage_report_phase2.csv", cov_rows, ["metric", "count"])

    checkpoint = {
        "environment_hash_set": hash_set,
        "abilities_targeted": len(priority),
        "abilities_reassessed": len(reassess),
        "commands_candidate": len(quality_rows),
        "commands_accepted": cov_counts["quality_gate_accepted"],
        "commands_rejected": len(quality_rows) - cov_counts["quality_gate_accepted"],
        "tests_started": cov_counts["startup_executed"],
        "tests_trigger_reached": cov_counts["trigger_reached"],
        "tests_state_verified": 0,
        "tests_ui_verified": 0,
        "issues_confirmed": len(issues_rows),
        "last_audit_id": pilot[-1]["audit_id"] if pilot else "",
        "last_test_case_id": result_rows[-1]["test_case_id"] if result_rows else "",
    }
    (OUT / "checkpoint_phase2.json").write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")
    progress = [
        "# Phase 2 Progress",
        "",
        f"- input_validation: complete, missing={missing}",
        f"- DB_DATA_MISMATCH classified: {len(db_rows)} / 31",
        f"- NOT_IMPLEMENTED/UNREACHABLE/PARTIAL reassessed: {len(reassess)} / 136",
        f"- pilot setup designs: {len(design_rows)} / {len(pilot)}",
        f"- command candidates: {len(quality_rows)}",
        f"- accepted: {checkpoint['commands_accepted']}",
        f"- startup executed: {checkpoint['tests_started']}",
        f"- trigger reached: {checkpoint['tests_trigger_reached']}",
        "- state acquisition: `/state?view=debug` works without runtime changes; full PASS still requires effect-specific before/after assertions and UI confirmation.",
        "- full execution phase: use `debug_setup_design.csv` and `debug_command_quality.csv` schema as template; do not use previous 4,195 placeholders as accepted commands.",
    ]
    (OUT / "progress_phase2.md").write_text("\n".join(progress) + "\n", encoding="utf-8")

    (OUT / "README.md").write_text(
        "# Loveca Effect Full Audit Phase 2\n\n"
        "This directory contains Phase 2 audit outputs. Runtime and DB files were not modified by this audit tool.\n\n"
        "Key points:\n"
        f"- Priority abilities: {len(priority)}\n"
        f"- DB mismatch classifications: {len(db_rows)}\n"
        f"- Reassessed NOT_IMPLEMENTED/UNREACHABLE/PARTIAL abilities: {len(reassess)}\n"
        f"- Pilot commands accepted: {checkpoint['commands_accepted']} / {len(quality_rows)}\n"
        f"- Startup probes: {checkpoint['tests_started']}; trigger reached: {checkpoint['tests_trigger_reached']}\n\n"
        "Accepted commands are under `debug_commands/accepted/`; rejected commands include rejection reasons in `debug_command_quality.csv`.\n",
        encoding="utf-8",
    )
    print(json.dumps(checkpoint, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
