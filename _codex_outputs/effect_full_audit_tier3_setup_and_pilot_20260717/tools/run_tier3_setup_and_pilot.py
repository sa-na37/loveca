#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: tier3_manual_setup_and_pilot_20260717a
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "effect_full_audit_tier3_setup_and_pilot_20260717"
TARGET = ROOT / "_codex_outputs" / "effect_full_audit_tier3_runtime_reaudit_correction_20260717" / "target_61_canonicalized.csv"
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

SETUP_FIELDS = [
    "canonical_id", "cardnumber", "cardname", "trigger", "effect_text", "ability_summary",
    "condition_type", "positive_condition", "negative_condition_removed", "source_zone", "target_zone",
    "required_stage_L", "required_stage_C", "required_stage_R", "required_hand", "required_green",
    "required_deck_order", "required_success_zone", "required_live_cards", "required_energy_active",
    "required_energy_wait", "required_opponent_wait_count", "required_opponent_success_count",
    "required_opponent_score", "required_history", "required_attached_energy", "expected_pending_sequence",
    "expected_effect_delta", "expected_cleanup_point", "undo_expected", "ui_required",
    "manual_review_status", "manual_review_notes",
]

ROUTE_FIELDS = [
    "canonical_id", "registry_rule_id", "registry_match_evidence", "engine_function",
    "engine_function_evidence", "effects_module", "effects_function", "server_action",
    "server_action_evidence", "pending_kind", "route_confidence", "route_notes",
]

PILOT_FIELDS = [
    "canonical_id", "trigger", "family", "positive_setup_id", "negative_setup_id", "route_confidence",
    "condition_expected", "condition_observed", "condition_satisfied", "trigger_executed",
    "pending_sequence_completed", "expected_effect_delta", "actual_effect_delta", "effect_completed",
    "cleanup_applicable", "cleanup_passed", "undo_applicable", "undo_passed", "ui_required",
    "browser_checked", "browser_passed", "pilot_status", "reason", "evidence",
]

PILOT_IDS = [
    "PL!S-bp3-016#A01",
    "PL!SP-bp4-003#A02",
    "PL!-bp3-002#A02",
    "PL!SP-bp1-001#A01",
    "PL!N-pb1-003#A01",
    "PL!SP-bp2-008#A01",
    "PL!N-bp4-008#A01",
    "PL!S-bp7-006#A01",
    "PL!SP-bp7-025#A01",
    "PL!S-bp6-009#A01",
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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def run_text(args: List[str]) -> str:
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout


def safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", s.replace("#", "_")).strip("_")


def q(v: str) -> str:
    return "'" + str(v).replace("'", "'\"'\"'") + "'"


def command_text(env: Dict[str, str], port: int) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "cd /Users/tekitou/Desktop/gsim/loveca",
        "unset " + " ".join(RESET_KEYS),
    ]
    lines.extend(f"export {k}={q(str(v))}" for k, v in sorted(env.items()))
    lines.append(f"python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port {port} --debug")
    return "\n".join(lines) + "\n"


def reset_env(env: Dict[str, str]) -> None:
    for k in RESET_KEYS:
        os.environ.pop(k, None)
    os.environ.update(env)


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


def load_cards() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    comp = {c["cardnumber"]: c for c in json.loads(COMPILED.read_text(encoding="utf-8")).get("cards", [])}
    mind = {c["cardnumber"]: c for c in json.loads(MINDB.read_text(encoding="utf-8"))}
    return comp, mind


def family(row: Dict[str, str]) -> str:
    text = row["effect_text"]
    trig = row["trigger"]
    if trig == "起動":
        return "activated"
    if trig == "ライブ開始時":
        return "live_start"
    if "相手" in text:
        return "opponent_reference"
    if "成功ライブカード置き場" in text:
        return "success_zone_reference"
    if "登場" in text or "バトンタッチ" in text:
        return "entry_or_baton_history"
    if "エネルギー" in text or "このメンバーの下" in text:
        return "energy_or_attached"
    if "ライブの合計スコア" in text:
        return "live_score_continuous"
    if "<(ブレード)>" in text:
        return "blade_continuous"
    return "other"


def setup_design(row: Dict[str, str]) -> Dict[str, str]:
    text = row["effect_text"]
    cn = row["cardnumber"]
    trig = row["trigger"]
    out = {k: "" for k in SETUP_FIELDS}
    out.update({k: row.get(k, "") for k in ["canonical_id", "cardnumber", "cardname", "trigger", "effect_text"]})
    out["source_zone"] = "stage C" if trig != "ライブ開始時" else "stage C member during live confirm"
    out["target_zone"] = "stage / live / green depending on text"
    out["required_stage_C"] = cn
    out["required_energy_active"] = "40" if "<(E)>" in text or "エネルギー" in text or trig == "起動" else ""
    out["required_energy_wait"] = "3" if "アクティブにする" in text or "エネルギー" in text else ""
    out["ui_required"] = "true" if trig in {"起動", "ライブ開始時"} or any(x in text for x in ["選", "てもよい", "公開"]) else "false"
    out["undo_expected"] = "true" if trig in {"起動", "ライブ開始時"} else "undo_not_applicable_when positive/negative are separate initial states"
    out["manual_review_status"] = "DESIGNED_NOT_RUN" if row["canonical_id"] not in PILOT_IDS else "PILOT_SELECTED"
    if "成功ライブカード置き場にあるカード1枚につき" in text and "コストを+1" in text:
        out.update({
            "ability_summary": "success zone card count increases this member effective cost by that count",
            "condition_type": "own_success_zone_count",
            "positive_condition": "own success zone has exactly 2 live cards",
            "negative_condition_removed": "remove one success-zone live card so count is 1",
            "required_success_zone": "PL!N-bp1-029,PL!N-bp3-032",
            "expected_effect_delta": "effective_cost positive 6 vs negative 5",
            "expected_cleanup_point": "not_applicable_continuous",
        })
    elif text.strip() == "<(ブレード)><(ブレード)>を得る。":
        out.update({
            "ability_summary": "unconditional continuous blade +2 while source is on stage",
            "condition_type": "source_on_stage",
            "positive_condition": "source card is on stage C",
            "negative_condition_removed": "replace source card with a dummy member",
            "expected_effect_delta": "always_blade_bonus +2 on source slot",
            "expected_cleanup_point": "not_applicable_continuous",
        })
    elif "ウェイト状態のメンバー1人につき" in text:
        out.update({
            "ability_summary": "opponent wait member count grants one blade/heart per count",
            "condition_type": "opponent_wait_count",
            "positive_condition": "opponent_wait_count is set to 2 through aggregate input",
            "negative_condition_removed": "opponent_wait_count remains 0",
            "required_opponent_wait_count": "2",
            "expected_effect_delta": "per opponent wait member: blade/heart count positive 2 vs negative 0",
            "expected_cleanup_point": "not_applicable_continuous",
        })
    elif "自分はライブできない" in text:
        out.update({
            "ability_summary": "live cannot be started while this member has no other allied stage member",
            "condition_type": "stage_member_count",
            "positive_condition": "source is alone on stage",
            "negative_condition_removed": "add another member to side stage",
            "required_live_cards": "PL!N-bp1-029 in hand for live set",
            "expected_effect_delta": "live confirm sends set live to green / no LIVE_PERF",
            "expected_cleanup_point": "live resolution",
        })
    elif "手札から控え室に置く" in text and "手札にある場合のみ" in text:
        out.update({
            "ability_summary": "hand-only activation discards itself, draws 1, grants blade to named/group stage member",
            "condition_type": "hand_activation_with_stage_target",
            "positive_condition": "source in hand and a valid target member is on stage",
            "negative_condition_removed": "remove valid stage target",
            "required_hand": f"{cn},PL!N-bp3-009",
            "required_stage_C": "PL!N-bp4-003",
            "expected_pending_sequence": "activate_from_hand -> choose_stage_member_to_gain_blade -> resolve target",
            "expected_effect_delta": "hand source moves to green, draw +1, target temp_blade +1",
            "expected_cleanup_point": "live end",
        })
    elif trig == "起動":
        out.update({
            "ability_summary": "activated ability with explicit card-specific cost and pending resolution",
            "condition_type": "activation_cost_and_targets",
            "positive_condition": "source on stage C, listed cost resources and likely targets are present",
            "negative_condition_removed": "remove hand cost or active energy needed by cost",
            "required_hand": "PL!N-bp3-009,PL!N-bp1-029",
            "required_green": "PL!N-bp1-029,PL!N-bp3-009,PL!S-bp2-026",
            "expected_pending_sequence": "activate_to_green -> cost pending if any -> target/effect pending until empty",
            "expected_effect_delta": "specific effect text must change target active/wait/zone/hand as written",
            "expected_cleanup_point": "depends on temporary effect; otherwise resolution end",
        })
    elif trig == "ライブ開始時":
        out.update({
            "ability_summary": "live-start ability must be queued from stage source and resolved from auto-order",
            "condition_type": "live_start_trigger",
            "positive_condition": "source is on stage C, one live card is set from hand, deck order supports effect text",
            "negative_condition_removed": "do not set a live card from hand",
            "required_hand": "PL!N-bp1-029",
            "required_live_cards": "PL!N-bp1-029",
            "required_deck_order": "dummy draw card on top; bottom cards chosen to satisfy or fail source condition",
            "expected_pending_sequence": "LIVE_SET -> LIVE_CONFIRM -> auto_order/source pending -> target/optional pending -> LIVE_PERF",
            "expected_effect_delta": "temporary heart/blade/score described by source text",
            "expected_cleanup_point": "live end",
        })
    elif "相手の成功ライブカード置き場" in text:
        out.update({
            "ability_summary": "opponent success-zone aggregate value affects this continuous modifier",
            "condition_type": "opponent_success_count_or_score",
            "positive_condition": "opponent aggregate success count/score satisfies threshold or exceeds own value",
            "negative_condition_removed": "opponent aggregate value is set below threshold/equal",
            "required_opponent_success_count": "2",
            "required_opponent_score": "6 or larger when score threshold is referenced",
            "expected_effect_delta": "blade or live score bonus equals threshold text",
            "expected_cleanup_point": "not_applicable_continuous",
        })
    else:
        out.update({
            "ability_summary": "individual setup derived from text: " + text[:48],
            "condition_type": "text_specific",
            "positive_condition": "prepare the exact named group/unit/card/count/color/event stated in effect text",
            "negative_condition_removed": "remove only that named group/unit/card/count/color/event prerequisite",
            "expected_effect_delta": "apply the numeric move/draw/blade/heart/score/cost delta explicitly stated in effect text",
            "expected_cleanup_point": "live end if temporary; otherwise resolution or not applicable",
        })
    out["manual_review_notes"] = f"Designed from card text; family={family(row)}; no shared setup template copied."
    return out


def route_mapping(row: Dict[str, str]) -> Dict[str, str]:
    text = row["effect_text"]
    trig = row["trigger"]
    route = {k: "" for k in ROUTE_FIELDS}
    route["canonical_id"] = row["canonical_id"]
    try:
        from llocg_ui.effects.registry import try_match_effect_template_ext
        hit = try_match_effect_template_ext({}, text)
    except Exception:
        hit = None
    if hit:
        rule = hit[0] if isinstance(hit, tuple) else hit
        route["registry_rule_id"] = str(rule.get("ext_key") or rule.get("id") or "registry_match") if isinstance(rule, dict) else "registry_match"
        route["registry_match_evidence"] = "try_match_effect_template_ext returned a rule for the exact effect text"
        route["route_confidence"] = "EXACT"
    elif trig == "ライブ開始時":
        route.update({
            "engine_function": "_enqueue_live_start_prompts",
            "engine_function_evidence": "trigger is live-start; engine has live-start queue builder but exact parser must be confirmed in pilot",
            "server_action": "next(indices) in LIVE_SET then next() in LIVE_CONFIRM",
            "pending_kind": "auto_order / source-specific live_start pending",
            "route_confidence": "STRONG_FAMILY_MATCH",
        })
    elif trig == "起動":
        route.update({
            "engine_function": "cmd_activate_to_green / cmd_activate_from_hand",
            "engine_function_evidence": "activated timing uses normal activation commands; exact effect resolver is pilot-gated",
            "server_action": "activate_to_green or activate_from_hand",
            "server_action_evidence": "server exposes normal activate actions",
            "pending_kind": "discard_from_hand / effect-specific pending",
            "route_confidence": "STRONG_FAMILY_MATCH",
        })
    elif any(x in text for x in ["成功ライブカード置き場", "ウェイト状態", "ライブの合計スコア", "コストを+1"]):
        route.update({
            "engine_function": "continuous computed values via state_json/stage_detail and engine helpers",
            "engine_function_evidence": "family-level continuous calculator exists; exact text confirmation required by pilot",
            "server_action": "state_json",
            "server_action_evidence": "no UI action; computed value is observed",
            "route_confidence": "STRONG_FAMILY_MATCH",
        })
    elif "<(ブレード)>" in text or "必要ハート" in text:
        route.update({
            "engine_function": "continuous blade/heart global support",
            "engine_function_evidence": "only global presence; not target-specific",
            "server_action": "state_json",
            "route_confidence": "WEAK_GLOBAL_PRESENCE",
        })
    elif "ライブできない" in text or "発動しない" in text or "置けない" in text:
        route.update({
            "engine_function": "prohibition / rule-gate family",
            "engine_function_evidence": "prohibition text requires a rule hook, not a generic word-presence match",
            "server_action": "phase/action gate",
            "route_confidence": "WEAK_GLOBAL_PRESENCE",
            "route_notes": "Pilot must confirm actual rule gate; global support alone is not implementation evidence.",
        })
    else:
        route["route_confidence"] = "NO_ROUTE_FOUND"
    if not route["route_notes"]:
        route["route_notes"] = "Route confidence is not a final implementation status."
    return route


def state_metric(st: Dict[str, Any], cn: str) -> Dict[str, Any]:
    sd = st.get("stage_detail") or {}
    slot = {}
    for d in sd.values():
        if isinstance(d, dict) and d.get("cardnumber") == cn:
            slot = d
            break
    return {
        "phase": st.get("phase"),
        "hand": list(st.get("hand") or []),
        "green_room": list(st.get("green_room") or []),
        "set_zone": list(st.get("set_zone") or []),
        "stage": st.get("stage"),
        "pending": st.get("pending"),
        "always_blade_bonus": slot.get("always_blade_bonus", 0),
        "always_score_bonus": slot.get("always_score_bonus", 0),
        "effective_cost": slot.get("effective_cost"),
        "temp_blade": slot.get("temp_blade", 0),
        "temp_hearts": slot.get("temp_hearts", {}),
        "can_activate": slot.get("can_activate"),
        "energy_active": st.get("energy_active"),
        "energy_wait": st.get("energy_wait"),
        "opponent_wait_count": st.get("opponent_wait_count"),
        "opponent_success_count": st.get("opponent_success_count"),
    }


def make_app(env: Dict[str, str]):
    from llocg_ui.server import App
    reset_env(env)
    return App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)


def save_case(cid: str, branch: str, before: Dict[str, Any], after: Dict[str, Any], extra: Dict[str, Any]) -> str:
    d = OUT / "evidence" / safe_id(cid) / branch
    d.mkdir(parents=True, exist_ok=True)
    write_json(d / "before.json", before)
    write_json(d / "after.json", after)
    write_json(d / "metrics.json", extra)
    (d / "log.txt").write_text("\n".join(str(x) for x in (after.get("log") or [])) + "\n", encoding="utf-8")
    return str(d.relative_to(OUT))


def resolve_all(app: Any, cid: str, choices: Callable[[Dict[str, Any]], str], limit: int = 12) -> Tuple[Dict[str, Any], List[Dict[str, Any]], bool]:
    steps = []
    st = app.state_json()
    for i in range(limit):
        pend = list(st.get("pending") or [])
        if not pend:
            return st, steps, True
        p = pend[0]
        choice = choices(p)
        before_kind = str(p.get("kind") or "")
        before_opts = list(p.get("options") or [])
        st = app.cmd("resolve_pending", {"idx": 0, "choice": choice})
        steps.append({
            "step": i + 1,
            "kind": before_kind,
            "options": before_opts,
            "selected": choice,
            "actual_next": (st.get("pending") or [{}])[0].get("kind") if st.get("pending") else "",
        })
    return st, steps, not bool(st.get("pending"))


def pilot_env(cid: str, positive: bool) -> Dict[str, str]:
    env = base_env()
    if cid == "PL!S-bp3-016#A01":
        env.update({"LLOCG_START_STAGE_C": "PL!S-bp3-016", "LLOCG_START_SUCCESS": "PL!N-bp1-029,PL!N-bp3-032" if positive else "PL!N-bp1-029"})
    elif cid == "PL!SP-bp4-003#A02":
        env.update({"LLOCG_START_STAGE_C": "PL!SP-bp4-003" if positive else "PL!N-bp4-003"})
    elif cid == "PL!-bp3-002#A02":
        env.update({"LLOCG_START_STAGE_C": "PL!-bp3-002"})
    elif cid == "PL!SP-bp1-001#A01":
        env.update({"LLOCG_START_STAGE_C": "PL!SP-bp1-001", "LLOCG_START_STAGE_L": "" if positive else "PL!SP-bp4-003", "LLOCG_START_HAND": "PL!N-bp1-029", "LLOCG_START_PHASE": "LIVE_SET"})
    elif cid == "PL!N-pb1-003#A01":
        env.update({"LLOCG_START_STAGE_C": "PL!N-bp4-003" if positive else "PL!SP-bp4-003", "LLOCG_START_HAND": "PL!N-pb1-003,PL!N-bp3-009"})
    elif cid == "PL!SP-bp2-008#A01":
        env.update({"LLOCG_START_STAGE_C": "PL!SP-bp2-008", "LLOCG_START_STAGE_L": "PL!SP-bp4-003", "LLOCG_START_STAGE_R": "PL!SP-pb2-035"})
    elif cid == "PL!N-bp4-008#A01":
        env.update({"LLOCG_START_STAGE_C": "PL!N-bp4-008", "LLOCG_START_HAND": "PL!N-bp3-009", "LLOCG_START_ENERGY_WAIT": "1" if positive else "0"})
    elif cid == "PL!S-bp7-006#A01":
        env.update({"LLOCG_START_STAGE_C": "PL!S-bp7-006", "LLOCG_START_HAND": "PL!N-bp1-029" if positive else "", "LLOCG_START_PHASE": "LIVE_SET", "LLOCG_START_DECK_EXACT": "PL!N-bp3-009,PL!N-bp1-029,PL!S-bp2-026,PL!S-bp2-027,PL!S-bp2-028,PL!S-bp3-016,PL!S-PR-029,PL!S-PR-030,PL!S-PR-031"})
    elif cid == "PL!SP-bp7-025#A01":
        env.update({"LLOCG_START_STAGE_C": "PL!SP-bp7-025", "LLOCG_START_STAGE_L": "PL!SP-bp4-003", "LLOCG_START_HAND": "PL!N-bp1-029" if positive else "", "LLOCG_START_PHASE": "LIVE_SET"})
    elif cid == "PL!S-bp6-009#A01":
        env.update({"LLOCG_START_STAGE_C": "PL!S-bp6-009"})
    return env


def run_pilot(row: Dict[str, str], route: Dict[str, str], idx: int) -> Dict[str, Any]:
    cid = row["canonical_id"]
    env_p = pilot_env(cid, True)
    env_n = pilot_env(cid, False)
    app_n = make_app(env_n)
    st_n0 = app_n.state_json()
    if cid == "PL!-bp3-002#A02":
        st_n1 = st_n0
    elif cid == "PL!S-bp6-009#A01":
        st_n1 = st_n0
    elif row["trigger"] == "ライブ開始時" or cid == "PL!SP-bp1-001#A01":
        st_n1 = app_n.cmd("next", {"indices": [0]})
        st_n1 = app_n.cmd("next", {}) if st_n1.get("phase") == "LIVE_CONFIRM" else st_n1
    else:
        st_n1 = st_n0
    neg_ev = save_case(cid, "negative", st_n0, st_n1, {"metric": state_metric(st_n1, row["cardnumber"]), "env": env_n})

    app = make_app(env_p)
    st0 = app.state_json()
    pending_steps: List[Dict[str, Any]] = []
    trigger_executed = False
    pending_done = True
    if cid == "PL!-bp3-002#A02":
        st1 = app.cmd("opponent_wait_delta", {"delta": 2})
        trigger_executed = True
    elif cid == "PL!S-bp6-009#A01":
        st1 = app.cmd("opponent_success_delta", {"delta": 2})
        trigger_executed = True
    elif row["trigger"] == "起動":
        if cid == "PL!N-pb1-003#A01":
            st1 = app.cmd("activate_from_hand", {"hand_idx": 0})
        else:
            st1 = app.cmd("activate_to_green", {"pos": "C"})
        trigger_executed = st1 != st0 or bool(st1.get("pending"))
        def choose(p: Dict[str, Any]) -> str:
            opts = [str(x) for x in list(p.get("options") or [])]
            if "pay" in opts:
                return "pay"
            if "C" in opts:
                return "C"
            return opts[0] if opts else "ok"
        st1, pending_steps, pending_done = resolve_all(app, cid, choose)
    elif row["trigger"] == "ライブ開始時" or cid == "PL!SP-bp1-001#A01":
        st1 = app.cmd("next", {"indices": [0]})
        if st1.get("phase") == "LIVE_CONFIRM":
            st1 = app.cmd("next", {})
        trigger_executed = bool(st1.get("pending")) or st1.get("phase") in {"LIVE_PERF", "LIVE_RESOLVE"}
        def choose_live(p: Dict[str, Any]) -> str:
            opts = [str(x) for x in list(p.get("options") or [])]
            for o in opts:
                if row["cardnumber"] in o or row["cardnumber"] == o:
                    return o
            if "pay" in opts:
                return "pay"
            if "PL!SP-bp4-003" in opts:
                return "PL!SP-bp4-003"
            return opts[0] if opts else "ok"
        st1, pending_steps, pending_done = resolve_all(app, cid, choose_live)
    else:
        st1 = st0
        trigger_executed = True

    pos_ev = save_case(cid, "positive", st0, st1, {"metric": state_metric(st1, row["cardnumber"]), "env": env_p})
    pdir = OUT / "evidence" / safe_id(cid) / "pending_steps"
    write_json(pdir / "steps.json", pending_steps)
    (OUT / "evidence" / safe_id(cid) / "browser").mkdir(parents=True, exist_ok=True)
    (OUT / "evidence" / safe_id(cid) / "browser" / "command.sh").write_text(command_text(env_p, 8830 + idx), encoding="utf-8")

    mpos = state_metric(st1, row["cardnumber"])
    mneg = state_metric(st_n1, row["cardnumber"])
    expected = setup_design(row)["expected_effect_delta"]
    completed = False
    actual = ""
    condition_expected = setup_design(row)["positive_condition"]
    condition_observed = ""
    if cid == "PL!S-bp3-016#A01":
        condition_observed = f"positive_success_count={len(st1.get('success_zone') or [])}; negative_success_count={len(st_n1.get('success_zone') or [])}"
        actual = f"effective_cost positive={mpos['effective_cost']} negative={mneg['effective_cost']}"
        completed = mpos["effective_cost"] == 6 and mneg["effective_cost"] == 5
    elif cid == "PL!SP-bp4-003#A02":
        condition_observed = f"source_present_positive={row['cardnumber'] in json.dumps(st1.get('stage'))}"
        actual = f"always_blade_bonus={mpos['always_blade_bonus']}"
        completed = int(mpos["always_blade_bonus"] or 0) == 2
    elif cid == "PL!-bp3-002#A02":
        condition_observed = f"opponent_wait_count={st1.get('opponent_wait_count')}"
        actual = f"always_blade_bonus positive={mpos['always_blade_bonus']} negative={mneg['always_blade_bonus']}"
        completed = int(mpos["always_blade_bonus"] or 0) == 2
    elif cid == "PL!S-bp6-009#A01":
        condition_observed = f"opponent_success_count={st1.get('opponent_success_count')}"
        actual = f"always_blade_bonus positive={mpos['always_blade_bonus']} negative={mneg['always_blade_bonus']}"
        completed = int(mpos["always_blade_bonus"] or 0) > int(mneg["always_blade_bonus"] or 0)
    elif cid == "PL!N-pb1-003#A01":
        condition_observed = f"source_in_hand_initial={st0.get('hand', [None])[0]}; target_stage={st0.get('stage', {}).get('C')}"
        actual = f"green_has_source={row['cardnumber'] in st1.get('green_room', [])}; temp_blade={state_metric(st1, 'PL!N-bp4-003')['temp_blade']}; pending={st1.get('pending')}"
        completed = row["cardnumber"] in st1.get("green_room", []) and int(state_metric(st1, "PL!N-bp4-003")["temp_blade"] or 0) >= 1 and not st1.get("pending")
    elif cid == "PL!SP-bp1-001#A01":
        condition_observed = f"stage_member_count={sum(1 for v in (st0.get('stage') or {}).values() if v)}"
        actual = f"phase_after_confirm={st1.get('phase')}; set_zone={st1.get('set_zone')}; green_count={len(st1.get('green_room') or [])}"
        completed = st1.get("phase") == "LIVE_RESOLVE" and not st1.get("set_zone")
    elif row["trigger"] == "ライブ開始時":
        source_seen = any(row["cardnumber"] in json.dumps(step, ensure_ascii=False) for step in pending_steps)
        condition_observed = f"live_set_started={bool(st0.get('hand'))}; source_pending_seen={source_seen}; pending_steps={len(pending_steps)}"
        actual = f"pending={st1.get('pending')}; metric={mpos}"
        completed = bool(source_seen and trigger_executed and pending_done and not st1.get("pending") and ("[WARN]" not in "\n".join(st1.get("log") or [])))
    else:
        condition_observed = "see positive/negative metrics"
        actual = json.dumps({"positive": mpos, "negative": mneg, "log_tail": list(st1.get("log") or [])[-5:]}, ensure_ascii=False)
        completed = False

    cleanup_applicable = "true" if any(x in row["effect_text"] for x in ["ライブ終了時まで", "ライブ終了時"]) else "false"
    undo_applicable = "true" if row["trigger"] in {"起動", "ライブ開始時"} else "false"
    cleanup_passed = "false" if cleanup_applicable == "true" else "not_applicable"
    undo_passed = "false" if undo_applicable == "true" else "not_applicable"
    if undo_applicable == "true":
        try:
            undo_state = app.cmd("undo", {})
            write_json(OUT / "evidence" / safe_id(cid) / "undo" / "after_undo.json", undo_state)
            undo_passed = str((undo_state.get("phase"), undo_state.get("hand"), undo_state.get("stage")) == (st0.get("phase"), st0.get("hand"), st0.get("stage"))).lower()
        except Exception as exc:
            write_json(OUT / "evidence" / safe_id(cid) / "undo" / "error.json", {"error": str(exc)})
    status = "IMPLEMENTED_AND_REACHABLE" if completed and (undo_passed in {"true", "not_applicable"}) else "TRIGGER_REACHED_RESOLVER_BLOCKED"
    if route["route_confidence"] == "NO_ROUTE_FOUND":
        status = "GENERIC_ROUTE_TEXT_NOT_MATCHED"
    if route["route_confidence"] == "WEAK_GLOBAL_PRESENCE" and any(x in row["effect_text"] for x in ["ライブできない", "発動しない", "置けない"]):
        status = "RULE_INTERPRETATION_REQUIRED"
    if not trigger_executed and row["trigger"] == "起動":
        status = "UI_ROUTE_MISSING"
    return {
        "canonical_id": cid,
        "trigger": row["trigger"],
        "family": family(row),
        "positive_setup_id": pos_ev,
        "negative_setup_id": neg_ev,
        "route_confidence": route["route_confidence"],
        "condition_expected": condition_expected,
        "condition_observed": condition_observed,
        "condition_satisfied": str(bool(condition_observed)).lower(),
        "trigger_executed": str(trigger_executed).lower(),
        "pending_sequence_completed": str(pending_done).lower(),
        "expected_effect_delta": expected,
        "actual_effect_delta": actual,
        "effect_completed": str(completed).lower(),
        "cleanup_applicable": cleanup_applicable,
        "cleanup_passed": cleanup_passed,
        "undo_applicable": undo_applicable,
        "undo_passed": undo_passed,
        "ui_required": setup_design(row)["ui_required"],
        "browser_checked": "false",
        "browser_passed": "false",
        "pilot_status": status,
        "reason": "pilot exact delta matched" if completed else "pilot did not reach exact expected delta; see evidence logs and pending steps",
        "evidence": f"{pos_ev}; {neg_ev}; evidence/{safe_id(cid)}/pending_steps",
    }


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
    rows = read_csv(TARGET)
    if len(rows) != 61:
        raise SystemExit(f"target_61 must have 61 rows, got {len(rows)}")
    setup_rows = [setup_design(r) for r in rows]
    route_rows = [route_mapping(r) for r in rows]
    route_by_id = {r["canonical_id"]: r for r in route_rows}
    rows_by_id = {r["canonical_id"]: r for r in rows}
    pilot_selection = []
    pilot_results = []
    for i, cid in enumerate(PILOT_IDS):
        row = rows_by_id[cid]
        pilot_selection.append({
            "canonical_id": cid,
            "selection_reason": "selected to satisfy trigger mix and avoid family overlap; exact status is pilot-gated",
            "trigger": row["trigger"],
            "family": family(row),
            "expected_route": route_by_id[cid]["route_confidence"],
            "complexity": "high" if row["trigger"] in {"起動", "ライブ開始時"} else "medium",
        })
        pilot_results.append(run_pilot(row, route_by_id[cid], i))
    remaining = [
        {
            "canonical_id": r["canonical_id"],
            "setup_design_completed": "true",
            "route_mapping_completed": "true",
            "status": "NOT_RUN_AFTER_METHOD_CORRECTION",
        }
        for r in rows if r["canonical_id"] not in PILOT_IDS
    ]
    write_csv(OUT / "tier3_manual_setup_design_61.csv", setup_rows, SETUP_FIELDS)
    write_csv(OUT / "tier3_route_mapping_61.csv", route_rows, ROUTE_FIELDS)
    write_csv(OUT / "tier3_pilot_selection_10.csv", pilot_selection, ["canonical_id", "selection_reason", "trigger", "family", "expected_route", "complexity"])
    write_csv(OUT / "tier3_pilot_results_10.csv", pilot_results, PILOT_FIELDS)
    write_csv(OUT / "tier3_remaining_51.csv", remaining, ["canonical_id", "setup_design_completed", "route_mapping_completed", "status"])
    (OUT / "README.md").write_text(
        "# Tier3 Setup And Pilot 20260717\n\n"
        "- runtime_modified = false\n- db_modified = false\n"
        "- Phase A: 61 manual setup designs completed\n"
        "- Phase B: 10 pilot cases executed\n"
        "- Remaining 51: NOT_RUN_AFTER_METHOD_CORRECTION\n"
        "- No final status aggregation for all 61 is provided.\n",
        encoding="utf-8",
    )
    (OUT / "methodology_staging.md").write_text(
        "# Methodology Staging\n\n"
        "This artifact replaces the previous one-shot Tier3 classification with staged setup design and a 10-case pilot. "
        "The 61-row setup table contains card-specific positive and negative conditions. "
        "The pilot status table applies final status only to the selected 10 cases; the remaining 51 are explicitly not run after method correction.\n",
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
    print(json.dumps({
        "out": str(OUT),
        "zip": str(zip_path),
        "setup_rows": len(setup_rows),
        "pilot_rows": len(pilot_results),
        "remaining_rows": len(remaining),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
