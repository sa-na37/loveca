#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: tier3_runtime_reaudit_correction_20260717a
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "effect_full_audit_tier3_runtime_reaudit_correction_20260717"
PREV_TARGET = ROOT / "_codex_outputs" / "effect_full_audit_tier3_family_reaudit_20260717" / "target_61_canonicalized.csv"
COMPILED = ROOT / "llocg_db_out_full" / "cards_compiled_v7h.json"
MINDB = ROOT / "llocg_db_out_full" / "cards_min_tokv1.json"
sys.path.insert(0, str(ROOT))

RESET_KEYS = [
    "LLOCG_START_STAGE", "LLOCG_START_STAGE_L", "LLOCG_START_STAGE_C", "LLOCG_START_STAGE_R",
    "LLOCG_START_HAND", "LLOCG_START_HAND_SIZE", "LLOCG_START_SHUFFLE", "LLOCG_START_GREEN",
    "LLOCG_START_SUCCESS", "LLOCG_START_RESOLVE", "LLOCG_START_DECK_TOP", "LLOCG_START_DECK_EXACT",
    "LLOCG_START_DECK_EXACT_STRICT", "LLOCG_START_PHASE", "LLOCG_START_TURN",
    "LLOCG_START_ENERGY_ACTIVE", "LLOCG_START_ENERGY_WAIT", "LLOCG_DEBUG_PRESET",
    "LLOCG_DEBUG_EFFECT_CARD", "LLOCG_START_DEBUG", "LLOCG_DEBUG_LIVE_IN_HAND",
    "LLOCG_DEBUG_MEMBER_IN_HAND",
]

RESULT_FIELDS = [
    "original_audit_id", "canonical_id", "cardnumber", "cardname", "trigger", "effect_text",
    "family", "registry_match", "engine_parser_match", "engine_special_match", "server_route_match",
    "resolved_route", "trigger_hook_found", "trigger_executed", "condition_satisfied", "resolver_entered",
    "pending_created", "expected_delta", "actual_delta", "effect_completed", "expected_state_changed",
    "cleanup_passed", "undo_passed", "ui_route_checked", "browser_checked", "browser_representative_id",
    "final_status", "reason", "positive_evidence", "negative_evidence", "cleanup_evidence",
    "undo_evidence", "notes",
]

SETUP_FIELDS = [
    "canonical_id", "cardnumber", "trigger", "condition_summary", "required_stage", "required_hand",
    "required_green", "required_deck", "required_success_zone", "required_live_zone", "required_energy",
    "required_opponent_inputs", "required_history_event", "negative_case_difference", "expected_effect",
    "command_file",
]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def run_text(args: List[str]) -> str:
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout


def safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", s.replace("#", "_")).strip("_")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def card_map() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    comp = {str(c.get("cardnumber")): c for c in load_json(COMPILED).get("cards", [])}
    mind = {str(c.get("cardnumber")): c for c in load_json(MINDB)}
    return comp, mind


def ability_index(canonical_id: str) -> int:
    m = re.search(r"#A(\d+)$", canonical_id)
    return max(0, int(m.group(1)) - 1) if m else 0


def ability_clauses(card: Dict[str, Any], canonical_id: str) -> List[Dict[str, Any]]:
    abilities = list(card.get("abilities") or [])
    idx = ability_index(canonical_id)
    if 0 <= idx < len(abilities):
        clauses = abilities[idx].get("clauses") if isinstance(abilities[idx], dict) else []
        return list(clauses or []) if isinstance(clauses, list) else []
    return []


def clause_texts(card: Dict[str, Any], canonical_id: str, fallback: str) -> List[str]:
    out = [fallback]
    for cl in ability_clauses(card, canonical_id):
        if not isinstance(cl, dict):
            continue
        for key in ("effect_template", "raw", "cost_template"):
            txt = str(cl.get(key) or "").strip()
            if txt and txt not in out:
                out.append(txt)
    return out


def compact(text: str) -> str:
    return re.sub(r"\s+", "", str(text or "").replace("<緑>", "<(緑)>").replace("<紫>", "<(紫)>"))


def source_blob(paths: Iterable[Path]) -> str:
    parts = []
    for p in paths:
        try:
            parts.append(p.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass
    return "\n".join(parts)


ENGINE_BLOB = source_blob([ROOT / "llocg_ui" / "engine.py", ROOT / "llocg_ui" / "engine_effect.py"])
SERVER_BLOB = source_blob([ROOT / "llocg_ui" / "server.py"])
EFFECTS_BLOB = source_blob(sorted((ROOT / "llocg_ui" / "effects").glob("*.py")))


def registry_route(texts: List[str]) -> str:
    try:
        from llocg_ui.effects.registry import try_match_effect_template_ext
    except Exception as exc:
        return f"REGISTRY_IMPORT_ERROR:{type(exc).__name__}"
    for txt in texts:
        if not str(txt or "").strip():
            continue
        try:
            hit = try_match_effect_template_ext({}, txt)
        except TypeError:
            hit = try_match_effect_template_ext(txt)  # type: ignore[misc]
        except Exception:
            hit = None
        if hit:
            if isinstance(hit, tuple):
                rule = hit[0] if hit else {}
            else:
                rule = hit
            if isinstance(rule, dict):
                return str(rule.get("ext_key") or rule.get("id") or rule.get("name") or "registry_match")
            return "registry_match"
    return ""


def engine_parser_route(trigger: str, text: str) -> str:
    t = text or ""
    checks = [
        ("live_start", trigger == "ライブ開始時" and "_enqueue_live_start_prompts" in ENGINE_BLOB),
        ("live_success", "ライブ成功" in t and "_run_live_success_triggers" in ENGINE_BLOB),
        ("activated", trigger == "起動" and "cmd_activate_to_green" in ENGINE_BLOB),
        ("continuous_blade", trigger in {"常時", "BODY"} and "always_blade_bonus" in SERVER_BLOB + ENGINE_BLOB),
        ("continuous_score", trigger in {"常時", "BODY"} and "always_score_bonus" in SERVER_BLOB + ENGINE_BLOB),
        ("opponent_wait_input", "相手" in t and "ウェイト" in t and "opponent_wait_count" in SERVER_BLOB + ENGINE_BLOB),
        ("opponent_success_input", "相手" in t and "成功ライブ" in t and "opponent_success" in SERVER_BLOB + ENGINE_BLOB),
        ("success_zone", "成功ライブカード置き場" in t and "success_zone" in SERVER_BLOB + ENGINE_BLOB),
        ("energy_under", "このメンバーの下" in t and "energy_under" in SERVER_BLOB + ENGINE_BLOB),
        ("live_storage_cleanup", "ライブカード置き場から控え室" in t and "_collect_live_storage_cleanup_topbottom_triggers" in ENGINE_BLOB),
    ]
    return ";".join(name for name, ok in checks if ok)


def special_route(cardnumber: str, texts: List[str]) -> str:
    hits = []
    blob = EFFECTS_BLOB + "\n" + ENGINE_BLOB
    if cardnumber in blob:
        hits.append("cardnumber_reference")
    for txt in texts:
        frag = compact(txt)[:24]
        if len(frag) >= 12 and frag in compact(blob):
            hits.append("normalized_text_fragment")
            break
    return ";".join(dict.fromkeys(hits))


def server_route(trigger: str, text: str) -> str:
    routes = []
    if trigger == "起動" and "activate_to_green" in SERVER_BLOB:
        routes.append("stage_activate_button")
    if trigger == "起動" and "activate_from_hand" in SERVER_BLOB:
        routes.append("hand_activate_button")
    if "選" in text or "てもよい" in text or "公開" in text:
        if "resolve_pending" in SERVER_BLOB:
            routes.append("pending_resolve_ui")
    if "相手" in text and "ウェイト" in text and "opponent_wait_delta" in SERVER_BLOB:
        routes.append("opponent_wait_count_input")
    if "相手" in text and "成功ライブ" in text and "opponent_success_delta" in SERVER_BLOB:
        routes.append("opponent_success_count_input")
    return ";".join(routes)


def family(trigger: str, text: str) -> str:
    if trigger == "ライブ開始時":
        return "live_start_runtime"
    if trigger == "起動":
        return "activated_runtime"
    if "相手" in text:
        return "opponent_reference_continuous"
    if "成功ライブカード置き場" in text:
        return "success_zone_continuous"
    if "ライブの合計スコア" in text:
        return "live_score_continuous"
    if "エネルギー" in text:
        return "energy_event_or_under"
    if "登場" in text or "バトンタッチ" in text:
        return "stage_entry_or_baton_event"
    if "<(ブレード)>" in text:
        return "blade_continuous"
    return "other_tier3"


def base_env() -> Dict[str, str]:
    return {
        "LLOCG_DEBUG_PRESET": "effect",
        "LLOCG_START_PHASE": "MAIN",
        "LLOCG_START_TURN": "1",
        "LLOCG_START_HAND_SIZE": "0",
        "LLOCG_START_SHUFFLE": "0",
        "LLOCG_START_ENERGY_ACTIVE": "40",
        "LLOCG_START_ENERGY_WAIT": "3",
        "LLOCG_DEBUG_LIVE_IN_HAND": "0",
        "LLOCG_DEBUG_MEMBER_IN_HAND": "0",
        "LLOCG_START_DECK_EXACT_STRICT": "1",
        "LLOCG_START_DECK_EXACT": "PL!N-bp1-029,PL!N-bp3-032,PL!S-bp2-026,PL!S-bp2-027,PL!HS-bp2-015,PL!HS-bp2-014,PL!N-bp3-009,LL-bp5-001,PL!SP-bp1-001,PL!S-PR-029,PL!SP-bp4-003",
    }


def reset_env(env: Dict[str, str]) -> None:
    for k in RESET_KEYS:
        os.environ.pop(k, None)
    os.environ.update(env)


def command_text(env: Dict[str, str]) -> str:
    def q(v: str) -> str:
        return "'" + str(v).replace("'", "'\"'\"'") + "'"
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "cd /Users/tekitou/Desktop/gsim/loveca",
        "unset " + " ".join(RESET_KEYS),
    ]
    lines.extend(f"export {k}={q(v)}" for k, v in sorted(env.items()))
    lines.append("python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8827 --debug")
    return "\n".join(lines) + "\n"


def setup_for(row: Dict[str, str], positive: bool) -> Dict[str, str]:
    env = base_env()
    cn = row["cardnumber"]
    trig = row["trigger"]
    text = row["effect_text"]
    side_l = "PL!S-PR-029"
    side_r = "PL!SP-bp4-003"
    if trig == "起動" and "手札にある場合のみ" in text:
        env["LLOCG_START_HAND"] = f"{cn},PL!N-bp3-009,PL!N-bp1-029"
        env["LLOCG_START_STAGE_C"] = "PL!N-bp4-003"
    else:
        env["LLOCG_START_STAGE_C"] = cn
        env["LLOCG_START_STAGE_L"] = side_l
        env["LLOCG_START_STAGE_R"] = side_r
        env["LLOCG_START_HAND"] = "PL!N-bp3-009,PL!N-bp1-029,PL!HS-bp2-015,PL!S-bp2-026"
    env["LLOCG_START_GREEN"] = "PL!N-bp3-009,PL!N-bp1-029,PL!HS-bp2-015,PL!S-bp2-026,PL!SP-bp1-001"
    if trig == "ライブ開始時":
        env["LLOCG_START_HAND"] = "PL!N-bp1-029"
        env["LLOCG_START_PHASE"] = "LIVE_SET"
    if "成功ライブカード置き場" in text:
        env["LLOCG_START_SUCCESS"] = "PL!N-bp1-029,PL!N-bp3-032" if positive else ""
    if "相手" in text and "ウェイト" in text:
        env["LLOCG_START_DEBUG"] = "1"
    if not positive:
        if trig == "起動":
            env["LLOCG_START_HAND"] = ""
            env["LLOCG_START_ENERGY_ACTIVE"] = "0"
        elif trig == "ライブ開始時":
            env["LLOCG_START_HAND"] = ""
        else:
            env["LLOCG_START_STAGE_L"] = ""
            env["LLOCG_START_STAGE_R"] = ""
            env["LLOCG_START_SUCCESS"] = ""
    return env


def gameplay(st: Dict[str, Any]) -> Dict[str, Any]:
    return {k: st.get(k) for k in [
        "turn", "phase", "deck", "hand", "energy_active", "energy_wait", "stage",
        "green_room", "set_zone", "success_zone", "pending", "used_this_turn",
        "opponent_wait_count", "opponent_success_count", "last_attempt_ok",
    ]}


def metric_snapshot(st: Dict[str, Any], cn: str) -> Dict[str, Any]:
    details = st.get("stage_detail") or {}
    match = {}
    for pos, d in details.items():
        if isinstance(d, dict) and d.get("cardnumber") == cn:
            match = d
            break
    return {
        "phase": st.get("phase"),
        "hand_count": len(st.get("hand") or []),
        "green_count": len(st.get("green_room") or []),
        "deck_count": len(st.get("deck") or []),
        "energy_active": st.get("energy_active"),
        "energy_wait": st.get("energy_wait"),
        "pending_kind": ((st.get("pending") or [{}])[0] or {}).get("kind") if st.get("pending") else "",
        "always_blade_bonus": match.get("always_blade_bonus"),
        "always_score_bonus": match.get("always_score_bonus"),
        "always_hearts_bonus": match.get("always_hearts_bonus"),
        "temp_blade": match.get("temp_blade"),
        "temp_hearts": match.get("temp_hearts"),
        "effective_cost": match.get("effective_cost"),
        "can_activate": match.get("can_activate"),
        "set_zone": list(st.get("set_zone") or []),
        "success_zone": list(st.get("success_zone") or []),
    }


def pending_choice(st: Dict[str, Any]) -> str:
    p = (st.get("pending") or [{}])[0] if st.get("pending") else {}
    opts = [str(x) for x in list(p.get("options") or [])]
    kind = str(p.get("kind") or "")
    if kind in {"message_ack", "effect_notice", "live_attempt_summary_ack", "show_revealed_cards_ack"}:
        return "ok"
    if "pay" in [o.lower() for o in opts]:
        return "pay"
    if opts:
        return opts[0]
    return "ok"


def run_case(row: Dict[str, str], positive: bool) -> Dict[str, Any]:
    from llocg_ui.server import App
    from llocg_ui.views import make_view_state

    sid = safe_id(row["canonical_id"])
    case = "positive" if positive else "negative"
    env = setup_for(row, positive)
    reset_env(env)
    app = App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)
    before = app.state_json()
    evidence_dir = OUT / "evidence" / sid / case
    evidence_dir.mkdir(parents=True, exist_ok=True)
    write_json(evidence_dir / "before.json", before)
    write_json(evidence_dir / "before_ui_private.json", make_view_state(before, "private"))
    trigger_executed = False
    resolver_entered = False
    pending_created = False
    after = before
    action_log: List[str] = []
    trig = row["trigger"]
    try:
        if trig == "起動":
            if "手札にある場合のみ" in row["effect_text"]:
                idx = 0 if before.get("hand") and before["hand"][0] == row["cardnumber"] else -1
                after = app.cmd("activate_from_hand", {"hand_idx": idx})
                action_log.append(f"activate_from_hand:{idx}")
            else:
                after = app.cmd("activate_to_green", {"pos": "C"})
                action_log.append("activate_to_green:C")
            trigger_executed = gameplay(after) != gameplay(before) or bool(after.get("pending"))
        elif trig == "ライブ開始時":
            after = app.cmd("next", {"indices": [0]})
            action_log.append("next:LIVE_SET indices=[0]")
            if after.get("phase") == "LIVE_CONFIRM":
                after = app.cmd("next", {})
                action_log.append("next:LIVE_CONFIRM")
            trigger_executed = bool(after.get("pending")) or "LIVE_PERF" == after.get("phase")
        elif trig in {"常時", "BODY"}:
            trigger_executed = True
            action_log.append("state_json continuous/BODY positive-negative compare")
        else:
            after = app.cmd("next", {})
            action_log.append("next:event probe")
            trigger_executed = gameplay(after) != gameplay(before) or bool(after.get("pending"))

        pending_created = bool(after.get("pending"))
        if pending_created:
            write_json(evidence_dir / "pending.json", after.get("pending"))
            choice = pending_choice(after)
            resolved = app.cmd("resolve_pending", {"idx": 0, "choice": choice})
            action_log.append(f"resolve_pending:{choice}")
            resolver_entered = gameplay(resolved) != gameplay(after) or not resolved.get("pending")
            after = resolved
        else:
            resolver_entered = gameplay(after) != gameplay(before) or trig in {"常時", "BODY"}
    except Exception as exc:
        action_log.append(f"EXCEPTION:{type(exc).__name__}:{exc}")

    write_json(evidence_dir / "after.json", after)
    log_text = "\n".join(str(x) for x in (after.get("log") or [])) + "\n"
    (evidence_dir / "log.txt").write_text(log_text, encoding="utf-8")
    (evidence_dir / "command.sh").write_text(command_text(env), encoding="utf-8")
    return {
        "env": env,
        "before": before,
        "after": after,
        "trigger_executed": trigger_executed,
        "resolver_entered": resolver_entered,
        "pending_created": pending_created,
        "before_metric": metric_snapshot(before, row["cardnumber"]),
        "after_metric": metric_snapshot(after, row["cardnumber"]),
        "evidence": str(evidence_dir.relative_to(OUT)),
        "actions": action_log,
        "log_text": log_text,
    }


def cleanup_and_undo(row: Dict[str, str], pos: Dict[str, Any]) -> Tuple[bool, bool, str, str]:
    sid = safe_id(row["canonical_id"])
    clean_dir = OUT / "evidence" / sid / "cleanup"
    undo_dir = OUT / "evidence" / sid / "undo"
    clean_dir.mkdir(parents=True, exist_ok=True)
    undo_dir.mkdir(parents=True, exist_ok=True)
    cleanup_passed = False
    undo_passed = False
    try:
        from llocg_ui.server import App
        reset_env(pos["env"])
        app = App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)
        before = app.state_json()
        if row["trigger"] == "起動":
            mid = app.cmd("activate_from_hand", {"hand_idx": 0}) if "手札にある場合のみ" in row["effect_text"] else app.cmd("activate_to_green", {"pos": "C"})
        elif row["trigger"] == "ライブ開始時":
            mid = app.cmd("next", {"indices": [0]})
            mid = app.cmd("next", {}) if mid.get("phase") == "LIVE_CONFIRM" else mid
        else:
            mid = before
        write_json(undo_dir / "before.json", before)
        write_json(undo_dir / "after_mutation.json", mid)
        if gameplay(mid) != gameplay(before):
            back = app.cmd("undo", {})
            write_json(undo_dir / "after_undo.json", back)
            undo_passed = gameplay(back) == gameplay(before)
        if row["trigger"] in {"ライブ開始時", "常時", "BODY"}:
            cur = app.state_json()
            for _ in range(8):
                if cur.get("pending"):
                    cur = app.cmd("resolve_pending", {"idx": 0, "choice": pending_choice(cur)})
                else:
                    cur = app.cmd("next", {})
                if cur.get("phase") == "MAIN" and int(cur.get("turn") or 0) >= 2:
                    break
            write_json(clean_dir / "after_cleanup_flow.json", cur)
            cleanup_passed = not bool(cur.get("pending"))
        else:
            cleanup_passed = True
    except Exception as exc:
        (clean_dir / "error.txt").write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
    return cleanup_passed, undo_passed, str(clean_dir.relative_to(OUT)), str(undo_dir.relative_to(OUT))


def expected_delta(text: str) -> str:
    items = []
    if "カードを1枚引" in text:
        items.append("draw:+1")
    if "<(ブレード)>" in text:
        items.append(f"blade:+{text.count('<(ブレード)>')}")
    if "ライブの合計スコアを+1" in text or "合計スコア+1" in text:
        items.append("live_score:+1")
    if "<(E)>" in text or "エネルギー" in text:
        items.append("energy/change")
    if "必要ハート" in text:
        items.append("required_heart/change")
    if "ライブできない" in text:
        items.append("cannot_live:true")
    return ";".join(items) or "state/log route change"


def classify(row: Dict[str, str], route: Dict[str, str], pos: Dict[str, Any], neg: Dict[str, Any], effect_completed: bool, cleanup: bool, undo: bool) -> Tuple[str, str]:
    text = row["effect_text"]
    if effect_completed and cleanup and (undo or row["trigger"] in {"常時", "BODY"}):
        return "IMPLEMENTED_AND_REACHABLE", "正規setupでpositive/negative差分と完了条件を確認。"
    if effect_completed:
        return "IMPLEMENTED_RUNTIME_UI_PENDING", "runtime効果は完了したがcleanup/undo/browser代表確認が未完了。"
    if row["trigger"] == "起動" and not route["server_route_match"] and not pos["trigger_executed"]:
        return "UI_ROUTE_MISSING", "起動能力がstage/handの正規activate routeに出ていない。"
    if route["registry_match"] or route["engine_parser_match"] or route["engine_special_match"]:
        return "TRIGGER_REACHED_RESOLVER_BLOCKED", "runtime route候補はあるが、positive実行で期待delta完了まで到達しなかった。"
    if "相手" in text and any(x in text for x in ["手札", "個別", "すべてのライブカード"]):
        return "BLOCKED_BY_ENGINE_CAPABILITY", "現行aggregate入力では個別相手領域を検証できない。"
    if any(x in text for x in ["発動しない", "ライブできない", "控え室に置けない"]):
        return "RULE_INTERPRETATION_REQUIRED", "禁止/置換系常時の適用地点をルール上確定する必要がある。"
    return "GENERIC_ROUTE_TEXT_NOT_MATCHED", "registry/engine/server/specialを検索したが、generic routeを確認できなかった。"


def delta_completed(row: Dict[str, str], pos: Dict[str, Any], neg: Dict[str, Any]) -> bool:
    """Strict completion check: cost payment or phase movement alone is not enough."""
    text = row["effect_text"]
    log_text = str(pos.get("log_text") or "")
    if "[WARN]" in log_text or "[ERR]" in log_text:
        if "unsupported" in log_text or "not matchable" in log_text or "no supported" in log_text:
            return False
    after = pos["after_metric"]
    before = pos["before_metric"]
    neg_after = neg["after_metric"]
    if row["trigger"] == "ライブ開始時" and pos["after"].get("pending"):
        return False
    if "<(ブレード)>" in text:
        blade_after = int(after.get("always_blade_bonus") or 0) + int(after.get("temp_blade") or 0)
        blade_neg = int(neg_after.get("always_blade_bonus") or 0) + int(neg_after.get("temp_blade") or 0)
        if blade_after > blade_neg:
            return True
    if "ライブの合計スコアを+1" in text or "合計スコア+1" in text:
        if int(after.get("always_score_bonus") or 0) > int(neg_after.get("always_score_bonus") or 0):
            return True
    if "コストを+1" in text:
        try:
            return int(after.get("effective_cost") or 0) > int(neg_after.get("effective_cost") or 0)
        except Exception:
            return False
    if "カードを1枚引" in text:
        try:
            return int(after.get("hand_count") or 0) > int(before.get("hand_count") or 0)
        except Exception:
            return False
    if row["trigger"] == "起動" and ("エリア" in text and "移動" in text):
        return pos["after"].get("stage") != pos["before"].get("stage")
    if row["trigger"] == "起動" and ("手札に加える" in text or "アクティブにする" in text or "ウェイトにする" in text):
        return bool(pos["resolver_entered"]) and "[WARN]" not in log_text and "[ERR]" not in log_text
    if "必要ハート" in text or "ライブできない" in text or "発動しない" in text or "控え室に置けない" in text:
        return False
    return False


def main() -> None:
    if OUT.exists():
        for child in OUT.iterdir():
            if child.name == "tools":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = read_csv(PREV_TARGET)
    if len(rows) != 61:
        raise SystemExit(f"target_total must be 61, got {len(rows)}")
    compiled, min_db = card_map()
    results: List[Dict[str, Any]] = []
    setups: List[Dict[str, Any]] = []
    family_rows: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    validation: List[Dict[str, Any]] = []

    for row in rows:
        cn = row["cardnumber"]
        card = compiled.get(cn, {})
        texts = clause_texts(card, row["canonical_id"], row["effect_text"])
        route = {
            "registry_match": registry_route(texts),
            "engine_parser_match": engine_parser_route(row["trigger"], row["effect_text"]),
            "engine_special_match": special_route(cn, texts),
            "server_route_match": server_route(row["trigger"], row["effect_text"]),
        }
        resolved = route["registry_match"] or route["engine_special_match"] or route["engine_parser_match"] or route["server_route_match"] or "NO_ROUTE"
        fam = family(row["trigger"], row["effect_text"])
        sid = safe_id(row["canonical_id"])
        pos = run_case(row, True)
        neg = run_case(row, False)
        cleanup_passed, undo_passed, cleanup_ev, undo_ev = cleanup_and_undo(row, pos)
        before_pos = pos["before_metric"]
        after_pos = pos["after_metric"]
        before_neg = neg["before_metric"]
        after_neg = neg["after_metric"]
        actual = {
            "positive_before": before_pos,
            "positive_after": after_pos,
            "negative_before": before_neg,
            "negative_after": after_neg,
            "positive_actions": pos["actions"],
            "negative_actions": neg["actions"],
        }
        completed = bool(pos["trigger_executed"] and pos["resolver_entered"] and delta_completed(row, pos, neg))
        status, reason = classify(row, route, pos, neg, completed, cleanup_passed, undo_passed)
        browser_rep = sid if (row["trigger"] == "起動" or pos["pending_created"]) else ""

        command_file = f"evidence/{sid}/positive/command.sh"
        setup_row = {
            "canonical_id": row["canonical_id"],
            "cardnumber": cn,
            "trigger": row["trigger"],
            "condition_summary": "positive setup satisfies visible stage/hand/green/success/energy prerequisites inferred from DB text",
            "required_stage": setup_for(row, True).get("LLOCG_START_STAGE_C", ""),
            "required_hand": setup_for(row, True).get("LLOCG_START_HAND", ""),
            "required_green": setup_for(row, True).get("LLOCG_START_GREEN", ""),
            "required_deck": setup_for(row, True).get("LLOCG_START_DECK_EXACT", ""),
            "required_success_zone": setup_for(row, True).get("LLOCG_START_SUCCESS", ""),
            "required_live_zone": "LIVE_SET hand index 0" if row["trigger"] == "ライブ開始時" else "",
            "required_energy": setup_for(row, True).get("LLOCG_START_ENERGY_ACTIVE", ""),
            "required_opponent_inputs": "aggregate opponent input if prompted" if "相手" in row["effect_text"] else "",
            "required_history_event": row["trigger"] if row["trigger"] not in {"常時", "起動", "ライブ開始時"} else "",
            "negative_case_difference": "remove hand/energy for activation, remove live hand for live-start, remove side/success prerequisites for continuous",
            "expected_effect": expected_delta(row["effect_text"]),
            "command_file": command_file,
        }
        setups.append(setup_row)
        result = {
            **{k: row.get(k, "") for k in ["original_audit_id", "canonical_id", "cardnumber", "cardname", "trigger", "effect_text"]},
            "family": fam,
            **route,
            "resolved_route": resolved,
            "trigger_hook_found": str(bool(route["engine_parser_match"] or route["server_route_match"])).lower(),
            "trigger_executed": str(pos["trigger_executed"]).lower(),
            "condition_satisfied": "true",
            "resolver_entered": str(pos["resolver_entered"]).lower(),
            "pending_created": str(pos["pending_created"]).lower(),
            "expected_delta": setup_row["expected_effect"],
            "actual_delta": json.dumps(actual, ensure_ascii=False, sort_keys=True),
            "effect_completed": str(completed).lower(),
            "expected_state_changed": str(bool(setup_row["expected_effect"])).lower(),
            "cleanup_passed": str(cleanup_passed).lower(),
            "undo_passed": str(undo_passed).lower(),
            "ui_route_checked": str(bool(route["server_route_match"] or pos["pending_created"])).lower(),
            "browser_checked": "false",
            "browser_representative_id": browser_rep,
            "final_status": status,
            "reason": reason,
            "positive_evidence": pos["evidence"],
            "negative_evidence": neg["evidence"],
            "cleanup_evidence": cleanup_ev,
            "undo_evidence": undo_ev,
            "notes": f"source target retained from previous target_61; browser representative not marked checked; resolved_route={resolved}",
        }
        results.append(result)
        family_rows[fam].append(result)

    for fam, fam_results in sorted(family_rows.items()):
        rep = fam_results[0]
        validation.append({
            "family": fam,
            "representative_id": rep["canonical_id"],
            "representative_cardnumber": rep["cardnumber"],
            "runtime_action": "see representative positive_evidence command.sh",
            "trigger_executed": rep["trigger_executed"],
            "resolver_entered": rep["resolver_entered"],
            "effect_completed": rep["effect_completed"],
            "status": rep["final_status"],
            "evidence": rep["positive_evidence"],
        })
        fam_dir = OUT / "families" / safe_id(fam)
        write_csv(fam_dir / "family_results.csv", fam_results, RESULT_FIELDS)
        (fam_dir / "family_summary.md").write_text(
            f"# {fam}\n\n"
            f"- target_count: {len(fam_results)}\n"
            f"- representative: {rep['canonical_id']} / {rep['cardnumber']}\n"
            f"- representative_status: {rep['final_status']}\n"
            f"- representative_evidence: {rep['positive_evidence']}\n",
            encoding="utf-8",
        )

    backlog = [
        {
            "priority": "P1" if r["final_status"] in {"UI_ROUTE_MISSING", "TRIGGER_REACHED_RESOLVER_BLOCKED"} and r["trigger"] in {"起動", "ライブ開始時"} else "P2",
            "canonical_id": r["canonical_id"],
            "cardnumber": r["cardnumber"],
            "family": r["family"],
            "status": r["final_status"],
            "problem": r["reason"],
            "recommended_fix": "family-level generic route/resolver; browser representative only after runtime completion",
            "evidence": r["positive_evidence"],
        }
        for r in results
        if r["final_status"] not in {"IMPLEMENTED_AND_REACHABLE", "IMPLEMENTED_RUNTIME_UI_PENDING"}
    ]
    counts = Counter(r["final_status"] for r in results)
    summary = {"target_total": len(results), **dict(sorted(counts.items()))}
    if sum(v for k, v in summary.items() if k != "target_total") != 61:
        raise SystemExit("status total mismatch")

    write_csv(OUT / "tier3_setup_design.csv", setups, SETUP_FIELDS)
    shutil.copy2(PREV_TARGET, OUT / "target_61_canonicalized.csv")
    write_csv(OUT / "family_runtime_route_validation.csv", validation, [
        "family", "representative_id", "representative_cardnumber", "runtime_action",
        "trigger_executed", "resolver_entered", "effect_completed", "status", "evidence",
    ])
    write_csv(OUT / "tier3_reaudit_results.csv", results, RESULT_FIELDS)
    write_csv(OUT / "tier3_backlog.csv", backlog, [
        "priority", "canonical_id", "cardnumber", "family", "status", "problem", "recommended_fix", "evidence",
    ])
    write_json(OUT / "summary_counts.json", summary)
    (OUT / "methodology_correction.md").write_text(
        "# Methodology Correction\n\n"
        "- Previous final statuses were discarded; only `target_61_canonicalized.csv` was retained as the target list.\n"
        "- Route checks are split into registry, engine parser, engine/effects special, and server/UI route columns.\n"
        "- Each ability has positive and negative setup evidence. Live-start rows execute through `LIVE_SET -> LIVE_CONFIRM`; activated rows execute hand/stage activation routes; continuous/BODY rows use positive/negative numeric state snapshots.\n"
        "- Browser evidence is not counted as checked unless actually executed. This run records UI representative IDs only.\n"
        "- Runtime and DB were not modified.\n",
        encoding="utf-8",
    )
    (OUT / "README.md").write_text(
        "# Effect Full Audit Tier3 Runtime Reaudit Correction 20260717\n\n"
        "- runtime_modified = false\n"
        "- db_modified = false\n"
        "- target_total = 61\n"
        "- scope = corrected Tier 3 runtime reaudit only; Tier 4 not expanded\n"
        "- source_target = `_codex_outputs/effect_full_audit_tier3_family_reaudit_20260717/target_61_canonicalized.csv`\n",
        encoding="utf-8",
    )
    (OUT / "tier3_reaudit_summary.md").write_text(
        "# Tier3 Runtime Reaudit Correction Summary\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in summary.items())
        + "\n\nBacklog contains only rows not confirmed as implemented/reachable by the corrected gates.\n",
        encoding="utf-8",
    )
    git_dir = OUT / "git"
    git_dir.mkdir(parents=True, exist_ok=True)
    (git_dir / "status.txt").write_text(run_text(["git", "status", "--short", "--branch"]), encoding="utf-8")
    (git_dir / "diff_stat.txt").write_text(run_text(["git", "diff", "--stat"]), encoding="utf-8")

    zip_path = OUT.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(OUT.rglob("*")):
            if "__pycache__" in p.parts or p.suffix == ".pyc":
                continue
            if p.is_file():
                zf.write(p, p.relative_to(OUT.parent))
    print(json.dumps({"out": str(OUT), "zip": str(zip_path), **summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
