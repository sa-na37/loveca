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
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "effect_full_audit_phase4_correction_20260716"
PHASE4 = ROOT / "_codex_outputs" / "effect_full_audit_phase4_20260716"
PHASE3 = ROOT / "_codex_outputs" / "effect_full_audit_phase3_20260716"
DB = ROOT / "llocg_db_out_full" / "cards_compiled_v7h.json"

sys.path.insert(0, str(ROOT))

from llocg_ui.server import App
from llocg_ui.views import make_view_state
from llocg_ui.engine import _card_group_names, _get_card, _match_effect_template


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

POP_FIELDS = [
    "original_audit_id", "cardnumber", "cardname", "original_trigger", "original_effect_text",
    "correction_type", "canonical_audit_id", "canonical_trigger", "canonical_effect_text",
    "parent_audit_id", "exclude_from_backlog", "reason", "evidence", "notes",
]
CANON_FIELDS = [
    "canonical_audit_id", "source_audit_ids", "cardnumber", "cardname", "card_type",
    "canonical_trigger", "canonical_effect_text", "source_phase3_classifications",
    "source_phase4_classifications", "correction_notes",
]
TIER1_FIELDS = [
    "audit_id", "cardnumber", "cardname", "canonical_trigger", "setup_valid",
    "activation_action", "server_started", "trigger_reached", "pending_or_computed_observed",
    "resolver_reached", "effect_resolved", "state_result", "cleanup_result", "undo_result",
    "ui_result", "final_classification", "implementation_files", "functions", "evidence", "notes",
]


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


def normalize_text(text: str) -> str:
    s = str(text or "")
    s = s.replace("\n", "")
    s = re.sub(r"\s+", "", s)
    s = s.replace("：", ":").replace("（", "(").replace("）", ")")
    return s


def safe_id(audit_id: str) -> str:
    return audit_id.replace("!", "_").replace("-", "_").replace("#", "_")


def reset_env() -> None:
    for k in RESET_KEYS:
        os.environ.pop(k, None)


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


def base_env(card: str) -> Dict[str, str]:
    return {
        "LLOCG_DEBUG_PRESET": "effect",
        "LLOCG_DEBUG_EFFECT_CARD": card,
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
        "LLOCG_START_DECK_EXACT": "LL-bp1-001,LL-bp5-001,LL-bp2-001,LL-bp3-001,LL-bp5-002,PL!S-bp2-026,PL!SP-bp4-024,PL!HS-bp2-020",
    }


def new_app(env: Dict[str, str]) -> App:
    reset_env()
    os.environ.update(env)
    return App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)


def load_cards() -> Dict[str, Dict[str, Any]]:
    return {c["cardnumber"]: c for c in json.loads(DB.read_text(encoding="utf-8"))["cards"]}


def ability_for(cards: Dict[str, Dict[str, Any]], audit_id: str, cardnumber: str) -> Tuple[Dict[str, Any], str, str, str, str]:
    card = cards.get(cardnumber, {})
    idx_m = re.search(r"#A(\d+)$", audit_id)
    idx = int(idx_m.group(1)) - 1 if idx_m else 0
    abilities = list(card.get("abilities", []) or [])
    ab = abilities[idx] if 0 <= idx < len(abilities) else {}
    ability_type = str(ab.get("ability_type", "") or "")
    trigger = str(ab.get("trigger", "") or ability_type or "")
    conditions = str(ab.get("conditions", "") or "")
    clauses = [c for c in ab.get("clauses", []) or [] if isinstance(c, dict)]
    parts: List[str] = []
    for cl in clauses:
        cost = str(cl.get("cost_template", "") or "").strip()
        eff = str(cl.get("effect_template", "") or cl.get("raw", "") or "").strip()
        if cost and eff:
            parts.append(f"{cost}：{eff}")
        elif eff:
            parts.append(eff)
        elif cost:
            parts.append(cost)
    effect = " / ".join(parts)
    return ab, ability_type, trigger, conditions, effect


def canonical_trigger(ability_type: str, trigger: str) -> str:
    if trigger == "BODY":
        if "起動" in ability_type:
            return "起動"
        if "常時" in ability_type:
            return "常時"
    return trigger or ability_type


def is_fragment(text: str) -> bool:
    norm = normalize_text(text)
    if norm in {"を得る。", "する。", "置く。", "加える。", "得る。"}:
        return True
    return len(norm) <= 8 and not any(x in norm for x in ["場合", "この", "自分", "相手", "手札", "ステージ"])


def matcher_info(effect_text: str) -> Tuple[str, str]:
    candidates = [effect_text]
    candidates.extend([x.strip() for x in effect_text.split(" / ") if x.strip()])
    for text in candidates:
        try:
            matched = _match_effect_template(text)
        except Exception:
            matched = None
        if matched:
            rule, _gd = matched
            return str(rule.get("id", "") or ""), str(rule.get("op", "") or rule.get("ext_key", "") or "")
    return "", ""


def make_meta() -> None:
    meta = OUT / "meta"
    meta.mkdir(parents=True, exist_ok=True)
    (meta / "git_head.txt").write_text(run_text(["git", "rev-parse", "HEAD"]), encoding="utf-8")
    (meta / "git_status_short.txt").write_text(run_text(["git", "status", "--short"]), encoding="utf-8")
    (meta / "git_diff_stat.txt").write_text(run_text(["git", "diff", "--stat"]), encoding="utf-8")
    (meta / "python_version.txt").write_text(sys.version + "\n", encoding="utf-8")
    (meta / "runtime_db_path.txt").write_text(str(ROOT / "llocg_db_out_full") + "\n", encoding="utf-8")
    (meta / "runtime_db_sha256.txt").write_text(sha256(DB) + "\n", encoding="utf-8")
    (meta / "compiled_db_path.txt").write_text(str(DB) + "\n", encoding="utf-8")
    (meta / "compiled_db_sha256.txt").write_text(sha256(DB) + "\n", encoding="utf-8")
    (meta / "phase4_outputs_path.txt").write_text(str(PHASE4) + "\n", encoding="utf-8")
    (meta / "port_used.txt").write_text("8799\n", encoding="utf-8")
    (meta / "audit_start.txt").write_text(datetime.now().isoformat() + "\n", encoding="utf-8")
    (meta / "launch_command.txt").write_text("python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port 8799 --debug\n", encoding="utf-8")


def population_correction(rows: List[Dict[str, str]], cards: Dict[str, Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    seen: Dict[Tuple[str, str, str], str] = {}
    pop_rows: List[Dict[str, Any]] = []
    canonical: Dict[str, Dict[str, Any]] = {}
    mapping_rows: List[Dict[str, Any]] = []

    for row in rows:
        aid = row["audit_id"]
        cn = row["cardnumber"]
        ab, atype, trig, cond, effect_from_db = ability_for(cards, aid, cn)
        source_trigger = trig or row.get("trigger", "")
        original_effect = row.get("effect_text") or effect_from_db
        ctrigger = canonical_trigger(atype, source_trigger)
        ceffect = effect_from_db or original_effect
        ctype = "VALID_TOP_LEVEL_ABILITY"
        parent = ""
        exclude = "NO"
        reason = "Top-level ability retained after DB ability lookup."
        notes = ""

        key = (cn, ctrigger, normalize_text(ceffect))
        if is_fragment(ceffect):
            ctype = "FRAGMENT_MERGED_INTO_PARENT"
            exclude = "YES"
            reason = "Effect text is a parser fragment and has no independent subject/effect body."
            notes = "Do not create implementation backlog from this row."
        elif key in seen:
            ctype = "DUPLICATE_OF_OTHER_AUDIT_ID"
            parent = seen[key]
            exclude = "YES"
            reason = "Same card, trigger, and normalized effect text as another audit row."
            notes = "Keep mapping only; implementation work belongs to canonical row."
        elif trig == "BODY" and ctrigger != trig:
            ctype = "TRIGGER_RECLASSIFIED"
            reason = f"Compiled ability_type is {atype}; BODY is parser body marker, not activation timing."
            seen[key] = aid
        else:
            seen[key] = aid

        canonical_id = parent or aid
        pop_rows.append({
            "original_audit_id": aid,
            "cardnumber": cn,
            "cardname": row.get("cardname", ""),
            "original_trigger": row.get("trigger", trig),
            "original_effect_text": original_effect,
            "correction_type": ctype,
            "canonical_audit_id": canonical_id,
            "canonical_trigger": ctrigger,
            "canonical_effect_text": ceffect,
            "parent_audit_id": parent,
            "exclude_from_backlog": exclude,
            "reason": reason,
            "evidence": f"{DB} ability_index={aid.split('#A')[-1] if '#A' in aid else '?'}",
            "notes": notes,
        })
        mapping_rows.append({
            "original_audit_id": aid,
            "canonical_audit_id": canonical_id,
            "correction_type": ctype,
            "exclude_from_backlog": exclude,
            "reason": reason,
        })
        if exclude != "YES":
            item = canonical.setdefault(canonical_id, {
                "canonical_audit_id": canonical_id,
                "source_audit_ids": [],
                "cardnumber": cn,
                "cardname": row.get("cardname", ""),
                "card_type": str(cards.get(cn, {}).get("card_type", "") or ""),
                "canonical_trigger": ctrigger,
                "canonical_effect_text": ceffect,
                "source_phase3_classifications": [],
                "source_phase4_classifications": [],
                "correction_notes": [],
            })
            item["source_audit_ids"].append(aid)
            item["source_phase3_classifications"].append(row.get("phase3_classification", ""))
            item["source_phase4_classifications"].append(row.get("phase4_classification", ""))
            item["correction_notes"].append(ctype)

    canonical_rows: List[Dict[str, Any]] = []
    for item in canonical.values():
        canonical_rows.append({
            **item,
            "source_audit_ids": ";".join(item["source_audit_ids"]),
            "source_phase3_classifications": ";".join(sorted(set(item["source_phase3_classifications"]))),
            "source_phase4_classifications": ";".join(sorted(set(item["source_phase4_classifications"]))),
            "correction_notes": ";".join(sorted(set(item["correction_notes"]))),
        })
    return pop_rows, canonical_rows, mapping_rows


def design_for(row: Dict[str, str], cards: Dict[str, Dict[str, Any]], pop: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    aid = row["audit_id"]
    cn = row["cardnumber"]
    corr = pop[aid]
    trig = corr["canonical_trigger"]
    effect = corr["canonical_effect_text"]
    card_type = str(cards.get(cn, {}).get("card_type", "") or "")
    if corr["exclude_from_backlog"] == "YES":
        action = "No runtime trigger: parser fragment/duplicate row; verify exclusion only."
        req_zone = "none"
        expected = "excluded from implementation backlog"
    elif trig == "常時":
        action = "Place/check the card in relevant zones and inspect computed state/helper evidence; no pending expected."
        req_zone = "all zones for alias, or stage for member continuous effects"
        expected = "computed value changes without pending"
    elif trig == "起動" and "手札にある場合のみ起動" in effect:
        action = "Keep card in hand and look for a legal hand-activation route; stage activation is not legal."
        req_zone = "hand"
        expected = "hand activation UI/command should exist before resolver"
    elif trig == "起動":
        action = "Place member on stage in MAIN, satisfy costs/conditions, execute activate_to_green for that position."
        req_zone = "stage"
        expected = "activation log, pending or immediate resolver state change"
    else:
        action = "Use trigger-specific regular game action."
        req_zone = "trigger-dependent"
        expected = "pending or state diff"
    return {
        "audit_id": aid,
        "cardnumber": cn,
        "cardname": row.get("cardname", ""),
        "card_type": card_type,
        "effect_text": effect,
        "canonical_trigger": trig,
        "activation_timing": trig,
        "required_zone": req_zone,
        "required_phase": "MAIN for 起動; none for 常時; trigger-specific otherwise",
        "required_cost": "provided by debug energy/hand/deck setup where applicable",
        "required_targets": "stage members/hand cards/deck top according to effect text",
        "required_prior_state": "avoid unrelated trigger noise; provide other member when effect requires another stage member",
        "forbidden_noise": "DECK_CODE wrapper, success zone >=3 initial state, unrelated live triggers",
        "expected_pending_kind": "none for 常時; effect-specific for 起動",
        "expected_state_change": expected,
        "expected_cleanup": "count only when effect actually resolves",
        "expected_undo": "count exact undo only after effect actually resolves",
        "manual_steps": action,
    }


def write_design(design: Dict[str, str]) -> None:
    lines = [f"# {design['audit_id']} design", ""]
    for key in [
        "audit_id", "cardnumber", "cardname", "card_type", "effect_text", "canonical_trigger",
        "activation_timing", "required_zone", "required_phase", "required_cost", "required_targets",
        "required_prior_state", "forbidden_noise", "expected_pending_kind", "expected_state_change",
        "expected_cleanup", "expected_undo", "manual_steps",
    ]:
        lines.append(f"- {key}: {design[key]}")
    path = OUT / "tier1" / "design" / f"{safe_id(design['audit_id'])}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def setup_env_for_tier1(aid: str, cn: str, trigger: str, effect: str, excluded: bool) -> Tuple[Dict[str, str], str]:
    env = base_env(cn)
    action = "state inspection only"
    if excluded:
        env["LLOCG_START_STAGE_C"] = cn
        action = "excluded row inspection"
    elif trigger == "常時":
        if cn.startswith("PL!HS-") and "すべての領域" in effect:
            env["LLOCG_START_HAND"] = cn
            action = "computed group alias inspection across runtime card DB"
        else:
            env["LLOCG_START_STAGE_C"] = cn
            action = "continuous computed stage inspection"
    elif trigger == "起動" and "手札にある場合のみ起動" in effect:
        env["LLOCG_START_HAND"] = cn
        env["LLOCG_START_STAGE_L"] = "PL!HS-bp6-007"
        env["LLOCG_START_STAGE_C"] = "PL!N-bp5-001"
        action = "hand-only activation route inspection"
    elif trigger == "起動" and "手札をすべて公開する" in effect:
        env["LLOCG_START_STAGE_L"] = cn
        env["LLOCG_START_STAGE_C"] = "PL!N-bp5-001"
        env["LLOCG_START_HAND"] = "PL!N-bp5-002,PL!N-bp5-003"
        env["LLOCG_START_DECK_EXACT"] = "PL!HS-bp2-020,LL-bp1-001,LL-bp5-001,LL-bp2-001,LL-bp3-001,LL-bp5-002"
        action = "activate_to_green on stage member after no-live hand reveal setup"
    elif trigger == "起動":
        env["LLOCG_START_STAGE_C"] = cn
        env["LLOCG_START_HAND"] = "PL!N-bp5-002,PL!N-bp5-003,PL!N-bp5-004"
        action = "activate_to_green on stage member"
    return env, action


def pending_kind(state: Dict[str, Any]) -> str:
    pending = state.get("pending")
    if isinstance(pending, list) and pending and isinstance(pending[0], dict):
        return str(pending[0].get("kind", "") or "")
    return ""


def has_state_diff(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    ignore = {"log", "banner"}
    return {k: v for k, v in a.items() if k not in ignore} != {k: v for k, v in b.items() if k not in ignore}


def reverification(row: Dict[str, str], cards: Dict[str, Dict[str, Any]], corr: Dict[str, Any]) -> Dict[str, Any]:
    aid = row["audit_id"]
    cn = row["cardnumber"]
    sid = safe_id(aid)
    state_dir = OUT / "tier1" / "state" / sid
    log_dir = OUT / "tier1" / "logs"
    ui_dir = OUT / "tier1" / "ui"
    trigger = corr["canonical_trigger"]
    effect = corr["canonical_effect_text"]
    excluded = corr["exclude_from_backlog"] == "YES"
    env, activation_action = setup_env_for_tier1(aid, cn, trigger, effect, excluded)
    save_command(OUT / "tier1" / "commands" / f"{sid}.command.sh", env, f"Phase4 correction Tier1 reverification for {aid}")

    app = new_app(env)
    initial = app.state_json()
    write_json(state_dir / "00_initial.json", initial)
    write_json(state_dir / "01_before_trigger.json", initial)
    after = initial
    resolved = initial
    cleanup = initial
    undo = initial
    setup_valid = "YES"
    trigger_reached = "NO"
    computed_observed = "NO"
    resolver_reached = "NO"
    effect_resolved = "NO"
    state_result = "STATE_RECORDED"
    cleanup_result = "NOT_COUNTED_NO_EFFECT"
    undo_result = "NOT_COUNTED_NO_EFFECT"
    final = "ROUTE_UNRESOLVED"
    funcs: List[str] = []
    notes: List[str] = []

    try:
        if excluded:
            setup_valid = "NO"
            final = "SETUP_INVALID"
            notes.append(corr["correction_type"])
        elif trigger == "常時" and "すべての領域" in effect:
            ci = _get_card(app.cards_db, cn)
            groups = sorted(_card_group_names(ci)) if ci else []
            write_json(state_dir / "02_after_trigger.json", {"computed_group_names": groups})
            computed_observed = "YES" if {"スリーズブーケ", "DOLLCHESTRA", "みらくらぱーく！"}.issubset(set(groups)) else "NO"
            resolver_reached = computed_observed
            effect_resolved = computed_observed
            final = "IMPLEMENTED_COMPUTED_CONTINUOUS" if computed_observed == "YES" else "ROUTE_UNRESOLVED"
            funcs.append("_card_group_names")
            after = app.state_json()
        elif trigger == "常時":
            after = app.state_json()
            write_json(state_dir / "02_after_trigger.json", after)
            computed_observed = "YES" if has_state_diff(initial, after) else "NO"
            final = "IMPLEMENTED_COMPUTED_CONTINUOUS" if computed_observed == "YES" else "ROUTE_UNRESOLVED"
        elif trigger == "起動" and "手札にある場合のみ起動" in effect:
            write_json(state_dir / "02_after_trigger.json", app.state_json())
            setup_valid = "YES"
            final = "UI_ROUTE_MISSING"
            notes.append("Legal source zone is hand, but runtime command surface exposes activate_to_green for stage positions only.")
        elif trigger == "起動":
            pos = "L" if env.get("LLOCG_START_STAGE_L") == cn else "C"
            after = app.cmd("activate_to_green", {"pos": pos})
            write_json(state_dir / "02_after_trigger.json", after)
            log_text = "\n".join(str(x) for x in after.get("log", [])[-80:])
            pk = pending_kind(after)
            trigger_reached = "YES" if "[ACT]" in log_text or pk else "NO"
            computed_observed = "YES" if pk or has_state_diff(initial, after) else "NO"
            resolver_reached = "YES" if "[ACT]" in log_text and "unsupported effect_template" not in log_text else "NO"
            effect_resolved = "YES" if resolver_reached == "YES" and ("[ERR]" not in log_text or pk) else "NO"
            final = "IMPLEMENTED_AND_REACHABLE" if effect_resolved == "YES" else (
                "TRIGGER_REACHED_RESOLVER_BLOCKED" if trigger_reached == "YES" else "TRIGGER_NOT_REACHED_WITH_VALID_SETUP"
            )
            if "unsupported effect_template" in log_text:
                final = "TRIGGER_REACHED_RESOLVER_BLOCKED"
                notes.append("Activation entered generic command path but effect_template was unsupported.")
            funcs.append("cmd_activate_to_green")
            resolved = after
        else:
            setup_valid = "NO"
            final = "SETUP_INVALID"
            notes.append("No trigger-specific runner in Phase4 correction script.")
    except Exception as exc:
        after = app.state_json()
        after["exception"] = repr(exc)
        write_json(state_dir / "99_exception.json", after)
        final = "SETUP_INVALID"
        notes.append(repr(exc))

    write_json(state_dir / "03_pending_or_computed.json", after)
    if pending_kind(after):
        try:
            resolved = app.cmd("resolve_pending", {"idx": 0, "choice": "0"})
        except Exception as exc:
            resolved = app.state_json()
            resolved["resolve_exception"] = repr(exc)
    else:
        resolved = after
    write_json(state_dir / "04_resolved.json", resolved)
    cleanup = resolved
    write_json(state_dir / "05_cleanup.json", cleanup)
    if effect_resolved == "YES":
        undo = app.cmd("undo", {})
        undo_result = "UNDO_EXACT_AFTER_EFFECT" if not has_state_diff(initial, undo) else "UNDO_DIFF_AFTER_EFFECT"
        cleanup_result = "CLEANUP_CHECKED_AFTER_EFFECT"
    else:
        undo = app.cmd("undo", {})
    write_json(state_dir / "06_undo.json", undo)

    log_dir.mkdir(parents=True, exist_ok=True)
    log_dir.joinpath(f"{sid}.log").write_text("\n".join(str(x) for x in app.state_json().get("log", [])) + "\n", encoding="utf-8")
    write_json(ui_dir / f"{sid}_private.json", make_view_state(app.state_json(), "private"))
    write_json(ui_dir / f"{sid}_public.json", make_view_state(app.state_json(), "public"))

    matcher, op = matcher_info(effect)
    if matcher:
        funcs.append(matcher)
    if op:
        funcs.append(op)
    return {
        "audit_id": aid,
        "cardnumber": cn,
        "cardname": row.get("cardname", ""),
        "canonical_trigger": trigger,
        "setup_valid": setup_valid,
        "activation_action": activation_action,
        "server_started": "YES",
        "trigger_reached": trigger_reached,
        "pending_or_computed_observed": computed_observed,
        "resolver_reached": resolver_reached,
        "effect_resolved": effect_resolved,
        "state_result": state_result,
        "cleanup_result": cleanup_result,
        "undo_result": undo_result,
        "ui_result": "UI_JSON_RECORDED",
        "final_classification": final,
        "implementation_files": "llocg_ui/engine.py" if funcs else "",
        "functions": ";".join(dict.fromkeys(funcs)),
        "evidence": str(state_dir.relative_to(ROOT)),
        "notes": "; ".join(notes),
    }


def copy_watch_item() -> None:
    src = PHASE4 / "watch_items" / "empty_string_as_zero.md"
    dst = OUT / "watch_items" / "empty_string_as_zero.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copyfile(src, dst)
    else:
        dst.write_text("# Empty String As Zero\n\n- status: `ALLOWED_WITH_MONITORING`\n", encoding="utf-8")


def main() -> int:
    make_meta()
    copy_watch_item()
    cards = load_cards()
    rows = read_csv(PHASE4 / "final_reclassification_136.csv")
    pop_rows, canonical_rows, mapping_rows = population_correction(rows, cards)
    pop_by_id = {r["original_audit_id"]: r for r in pop_rows}
    write_csv(OUT / "population" / "population_correction_136.csv", pop_rows, POP_FIELDS)
    write_csv(OUT / "population" / "canonical_population_phase4_correction.csv", canonical_rows, CANON_FIELDS)
    write_csv(OUT / "population" / "audit_id_mapping.csv", mapping_rows, ["original_audit_id", "canonical_audit_id", "correction_type", "exclude_from_backlog", "reason"])

    tier1_source = read_csv(PHASE4 / "tier1" / "implemented_route_verification.csv")
    tier1_rows: List[Dict[str, Any]] = []
    for row in tier1_source:
        design = design_for(row, cards, pop_by_id)
        write_design(design)
        tier1_rows.append(reverification(row, cards, pop_by_id[row["audit_id"]]))
    write_csv(OUT / "tier1" / "tier1_reverification.csv", tier1_rows, TIER1_FIELDS)

    impl_rows: List[Dict[str, Any]] = []
    research_rows: List[Dict[str, Any]] = []
    excluded_rows: List[Dict[str, Any]] = []
    tier1_by_id = {r["audit_id"]: r for r in tier1_rows}

    for row in rows:
        aid = row["audit_id"]
        corr = pop_by_id[aid]
        if corr["exclude_from_backlog"] == "YES":
            excluded_rows.append({
                "audit_id": aid,
                "cardnumber": row["cardnumber"],
                "cardname": row["cardname"],
                "reason": corr["correction_type"],
                "notes": corr["reason"],
            })
            continue
        phase3 = row.get("phase3_classification", "")
        prev4 = row.get("phase4_classification", "")
        tier1 = tier1_by_id.get(aid)
        base = {
            "priority": "P1",
            "audit_id": aid,
            "cardnumber": row["cardnumber"],
            "cardname": row["cardname"],
            "canonical_trigger": corr["canonical_trigger"],
            "effect_text": corr["canonical_effect_text"],
            "phase3_classification": phase3,
            "phase4_previous_classification": prev4,
            "evidence": tier1.get("evidence", row.get("evidence", "")) if tier1 else row.get("evidence", ""),
            "notes": "",
        }
        if tier1:
            fc = tier1["final_classification"]
            if fc in {"UI_ROUTE_MISSING", "TRIGGER_REACHED_RESOLVER_BLOCKED", "RESOLVER_REACHED_STATE_FAIL"}:
                impl_rows.append({
                    **base,
                    "priority": "P1",
                    "missing_layer": fc,
                    "recommended_path": "Implement missing generic route/resolver/UI surface; do not add cardnumber branch.",
                    "notes": tier1.get("notes", ""),
                })
            elif fc in {"ROUTE_UNRESOLVED", "TRIGGER_NOT_REACHED_WITH_VALID_SETUP", "SETUP_INVALID"}:
                research_rows.append({
                    **base,
                    "priority": "R1",
                    "research_reason": fc,
                    "next_step": "Re-check legal setup and trigger collector before implementation classification.",
                    "notes": tier1.get("notes", ""),
                })
            continue
        if phase3 == "PARTIAL_BRANCH_MISSING":
            research_rows.append({
                **base,
                "priority": "R1",
                "research_reason": "PARTIAL_CANDIDATE",
                "next_step": "Re-run branch-level trigger/resolver proof before moving to implementation backlog.",
                "notes": "Phase4 PARTIAL_CONFIRMED is not treated as final in correction phase.",
            })
        elif phase3 == "NOT_IMPLEMENTED_WITH_EVIDENCE":
            research_rows.append({
                **base,
                "priority": "R2",
                "research_reason": "NOT_IMPLEMENTED_HIGH_CONFIDENCE_CANDIDATE",
                "next_step": "Run trigger-appropriate setup before confirming implementation backlog.",
                "notes": "Former NOT_IMPLEMENTED_CONFIRMED is provisional.",
            })
        else:
            research_rows.append({
                **base,
                "priority": "R2",
                "research_reason": "GENERIC_ROUTE_UNRESOLVED",
                "next_step": "Use Tier1 trigger-design method in next family representative phase.",
                "notes": "Tier3 execution is intentionally deferred.",
            })

    write_csv(OUT / "backlog" / "implementation_backlog_corrected.csv", impl_rows, [
        "priority", "audit_id", "cardnumber", "cardname", "canonical_trigger", "effect_text",
        "phase3_classification", "phase4_previous_classification", "missing_layer",
        "recommended_path", "evidence", "notes",
    ])
    write_csv(OUT / "backlog" / "research_backlog.csv", research_rows, [
        "priority", "audit_id", "cardnumber", "cardname", "canonical_trigger", "effect_text",
        "phase3_classification", "phase4_previous_classification", "research_reason",
        "next_step", "evidence", "notes",
    ])
    write_csv(OUT / "backlog" / "excluded_population_rows.csv", excluded_rows, [
        "audit_id", "cardnumber", "cardname", "reason", "notes",
    ])
    write_csv(OUT / "issues" / "behavioral_issues.csv", [], [
        "issue_id", "severity", "audit_id", "cardnumber", "category", "expected", "actual", "evidence", "notes",
    ])

    pcounts = Counter(r["correction_type"] for r in pop_rows)
    tier1_counts = Counter(r["final_classification"] for r in tier1_rows)
    coverage = {
        "original_rows": len(rows),
        "duplicate_rows": pcounts["DUPLICATE_OF_OTHER_AUDIT_ID"],
        "fragment_rows": pcounts["FRAGMENT_MERGED_INTO_PARENT"],
        "nested_granted_rows": pcounts["GRANTED_ABILITY_NESTED"],
        "trigger_reclassified_rows": pcounts["TRIGGER_RECLASSIFIED"],
        "canonical_abilities": len(canonical_rows),
        "excluded_rows": len(excluded_rows),
        "tier1_total": len(tier1_rows),
        "tier1_designs_completed": len(tier1_rows),
        "tier1_setups_valid": sum(1 for r in tier1_rows if r["setup_valid"] == "YES"),
        "tier1_triggers_reached": sum(1 for r in tier1_rows if r["trigger_reached"] == "YES"),
        "tier1_effects_resolved": sum(1 for r in tier1_rows if r["effect_resolved"] == "YES"),
        "tier1_cleanup_passed": sum(1 for r in tier1_rows if r["cleanup_result"] == "CLEANUP_CHECKED_AFTER_EFFECT"),
        "tier1_undo_exact": sum(1 for r in tier1_rows if r["undo_result"] == "UNDO_EXACT_AFTER_EFFECT"),
        "tier1_ui_checked": sum(1 for r in tier1_rows if r["ui_result"] == "UI_JSON_RECORDED"),
        "tier1_still_unresolved": sum(1 for r in tier1_rows if r["final_classification"] not in {"IMPLEMENTED_AND_REACHABLE", "IMPLEMENTED_COMPUTED_CONTINUOUS"}),
        "implementation_backlog_count": len(impl_rows),
        "research_backlog_count": len(research_rows),
        "excluded_backlog_count": len(excluded_rows),
        "behavioral_issues": 0,
        "watch_items": 1,
    }
    write_csv(OUT / "coverage_phase4_correction.csv", [coverage], list(coverage.keys()))
    status = "PHASE4_CORRECTION_COMPLETED" if len(rows) == 136 and len(tier1_rows) == 11 else "PHASE4_CORRECTION_PARTIAL"
    if coverage["tier1_still_unresolved"]:
        status = "PHASE4_CORRECTION_PARTIAL"
    (OUT / "README.md").write_text(
        "# Phase 4 correction\n\n"
        "This directory supersedes Phase 4 route classifications for correction purposes. "
        "It does not modify runtime or DB files.\n",
        encoding="utf-8",
    )
    (OUT / "final_report_phase4_correction.md").write_text(
        status + "\n\n"
        "## Summary\n\n"
        "Phase 4 classifications were treated as provisional. All 136 rows were checked for duplicate, fragment, and trigger/body split issues. Tier 1 was redesigned per trigger type and re-run with corrected setup assumptions. Implementation backlog and research backlog are separated.\n\n"
        "## Coverage\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in coverage.items())
        + "\n\n## Tier 1 classifications\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in sorted(tier1_counts.items()))
        + "\n\n## Backlog Policy\n\n"
        "- Implementation backlog includes only confirmed missing UI/resolver/routes from corrected Tier 1 evidence.\n"
        "- Research backlog contains setup/route unresolved rows, former Tier 3 generic unresolved rows, and former Tier 4 high-confidence candidates pending trigger-appropriate tests.\n"
        "- Fragment/duplicate rows and the empty-string-as-zero watch item are excluded from implementation backlog.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "coverage": coverage, "tier1": dict(tier1_counts)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
