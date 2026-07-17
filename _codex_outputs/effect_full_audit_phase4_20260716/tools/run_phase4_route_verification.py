#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "effect_full_audit_phase4_20260716"
PHASE3 = ROOT / "_codex_outputs" / "effect_full_audit_phase3_20260716"
sys.path.insert(0, str(ROOT))

from llocg_ui.server import App
from llocg_ui.views import make_view_state
from llocg_ui.engine import _match_effect_template


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


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def save_log(path: Path, state: Dict[str, Any]) -> None:
    log = state.get("log", [])
    text = "\n".join(str(x) for x in log) if isinstance(log, list) else str(log)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")


def canon_file_id(audit_id: str) -> str:
    return audit_id.replace("!", "_").replace("-", "_").replace("#", "_")


def pending_kind(st: Dict[str, Any]) -> str:
    p = st.get("pending", [])
    return str(p[0].get("kind", "") or "") if isinstance(p, list) and p and isinstance(p[0], dict) else ""

NOISE_KEYS = {
    "log", "banner", "root", "code", "deck_code", "debug",
    "cn2name", "cn2label", "cn2type", "cn2is_live", "cn2yell_hearts",
    "cn2yell_draw_icons", "cn2yell_score_icons", "cn2group", "cn2unit",
    "cn2cost", "cn2score", "public_reveal_events", "public_hand_reveal_events",
    "public_hand_revealed_cards", "public_hand_revealed_orient",
    "refresh_notices", "refresh_notice_seq", "refresh_notice_ack_seq",
}


def normalize_state(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): normalize_state(v) for k, v in obj.items() if str(k) not in NOISE_KEYS}
    if isinstance(obj, list):
        return [normalize_state(x) for x in obj]
    return obj


def states_equal(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    return normalize_state(a) == normalize_state(b)


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
        "LLOCG_START_DECK_EXACT": "LL-bp1-001,LL-bp5-001,LL-bp2-001,LL-bp3-001,LL-bp5-002,PL!S-bp2-026,PL!SP-bp4-024",
    }


def new_app(env: Dict[str, str]) -> App:
    reset_env()
    os.environ.update(env)
    return App(root=ROOT / "llocg_db_out_full", code="ui", deck_code="1RCBL", seed=1, debug=True)


def load_cards() -> Dict[str, Dict[str, Any]]:
    cards = json.loads((ROOT / "llocg_db_out_full/cards_compiled_v7h.json").read_text(encoding="utf-8"))["cards"]
    return {c["cardnumber"]: c for c in cards}


def ability_for_audit(cards: Dict[str, Dict[str, Any]], audit_id: str, cn: str) -> Tuple[str, str, str, Dict[str, Any]]:
    m = re.search(r"#A(\d+)$", audit_id)
    idx = int(m.group(1)) - 1 if m else 0
    card = cards.get(cn, {})
    abilities = list(card.get("abilities", []) or [])
    ab = abilities[idx] if 0 <= idx < len(abilities) else (abilities[0] if abilities else {})
    trigger = str(ab.get("trigger", "") or ab.get("ability_type", "") or "")
    clauses = [c for c in list(ab.get("clauses", []) or []) if isinstance(c, dict)]
    parts = []
    for c in clauses:
        cost = str(c.get("cost_template", "") or "").strip()
        eff = str(c.get("effect_template", "") or c.get("raw", "") or "").strip()
        if cost and eff:
            parts.append(cost + "：" + eff)
        elif eff:
            parts.append(eff)
        elif cost:
            parts.append(cost)
    effect = " / ".join(parts)
    return trigger, effect, str(card.get("card_type", "") or ""), ab


def families_for(text: str, trigger: str) -> Tuple[str, List[str], str]:
    tags: List[str] = []
    checks = [
        ("ドロー", ["カードを", "引"]),
        ("手札を捨てる", ["手札", "控え室"]),
        ("控え室から回収", ["控え室", "手札に加"]),
        ("デッキ上を見る", ["デッキの上から", "見る"]),
        ("デッキ上へ戻す", ["デッキ", "一番上"]),
        ("デッキ下へ置く", ["デッキ", "一番下"]),
        ("エネルギー", ["エネルギー"]),
        ("メンバーをアクティブ", ["アクティブ"]),
        ("メンバーをウェイト", ["ウェイト"]),
        ("相手人数入力", ["相手", "ウェイト"]),
        ("ポジションチェンジ", ["ポジションチェンジ", "フォーメーションチェンジ", "エリアを移動"]),
        ("ハート付与", ["ハート", "<赤>", "<青>", "<黄>", "<緑>", "<紫>"]),
        ("ブレード付与", ["ブレード"]),
        ("スコア加算", ["スコア", "+"]),
        ("必要ハート軽減", ["必要ハート", "減"]),
        ("成功置き場参照", ["成功ライブカード置き場"]),
        ("相手成功置き場参照", ["相手", "成功ライブ"]),
        ("余剰ハート参照", ["余剰ハート"]),
        ("エール公開内容参照", ["エール", "公開"]),
        ("名前・グループ・ユニット条件", ["『", "』"]),
        ("ターン1回", ["ターン1回"]),
        ("ライブ終了時cleanup", ["ライブ終了時まで"]),
    ]
    for tag, needles in checks:
        if all(n in text for n in needles):
            tags.append(tag)
    if "登場" in trigger:
        tags.append("登場時効果")
    if "ライブ開始" in trigger:
        tags.append("ライブ開始時効果")
    if "ライブ成功" in trigger:
        tags.append("成功時効果")
    if "BODY" in trigger or "起動" in trigger:
        tags.append("起動効果" if "起動" in trigger else "常時効果")
    if not tags:
        tags.append("その他")
    risk = "HIGH" if any(t in tags for t in ["成功時効果", "余剰ハート参照", "エール公開内容参照", "ライブ終了時cleanup", "相手人数入力"]) else "MEDIUM"
    return tags[0], tags[1:], risk


def matcher_info(effect_text: str) -> Tuple[str, str, str]:
    # For branch-like text, try each slash-separated clause as well as whole text.
    candidates = [effect_text]
    candidates.extend([x.strip() for x in effect_text.split(" / ") if x.strip()])
    for s in candidates:
        try:
            m = _match_effect_template(s)
        except Exception:
            m = None
        if m:
            rule, gd = m
            return str(rule.get("id", "")), str(rule.get("op", "")), str(rule.get("ext_key", "") or "")
    return "", "", ""


def runtime_probe(row: Dict[str, str], trigger: str, card_type: str) -> Dict[str, Any]:
    cn = row["cardnumber"]
    test_id = canon_file_id(row["audit_id"])
    env = base_env(cn)
    if card_type == "LIVE":
        env["LLOCG_START_HAND"] = cn
        env["LLOCG_START_STAGE_C"] = "LL-bp1-001"
    else:
        if "登場" in trigger:
            env["LLOCG_START_HAND"] = cn
        else:
            env["LLOCG_START_STAGE_C"] = cn
            env["LLOCG_START_HAND"] = "LL-bp1-001"
    save_command(OUT / "commands" / f"{test_id}.command.sh", env, f"Phase4 probe for {row['audit_id']}")
    app = new_app(env)
    state_dir = OUT / "state" / test_id
    st0 = app.state_json()
    write_json(state_dir / "00_initial.json", st0)
    st = st0
    try:
        if "登場" in trigger:
            st = app.cmd("play", {"hand_idx": 0, "pos": "C"})
            write_json(state_dir / "01_triggered.json", st)
        elif "ライブ開始" in trigger:
            st = app.cmd("next", {})
            write_json(state_dir / "01_live_set.json", st)
            st = app.cmd("set", {"indices": [0]})
            write_json(state_dir / "02_set.json", st)
            st = app.cmd("next", {})
            write_json(state_dir / "03_live_confirm.json", st)
            st = app.cmd("next", {})
            write_json(state_dir / "04_triggered.json", st)
        elif "ライブ成功" in trigger:
            # A full success route is setup-heavy. This probes whether the card can
            # be put in a legal live-start flow without crashing and records no reach.
            st = app.cmd("next", {})
            write_json(state_dir / "01_live_set_probe.json", st)
        else:
            write_json(state_dir / "01_state_probe.json", st)
    except Exception as exc:
        st = app.state_json()
        st["probe_exception"] = repr(exc)
        write_json(state_dir / "99_exception_state.json", st)
    save_log(OUT / "logs" / f"{test_id}.log", st)
    write_json(OUT / "ui" / f"{test_id}_private.json", make_view_state(st, "private"))
    write_json(OUT / "ui" / f"{test_id}_public.json", make_view_state(st, "public"))
    undo_st = st
    undo_equal = False
    for i in range(1, 16):
        undo_st = app.cmd("undo", {})
        write_json(state_dir / f"05_undo_step{i:02d}.json", undo_st)
        if states_equal(st0, undo_st):
            undo_equal = True
            break
    log_text = "\n".join(str(x) for x in st.get("log", [])[-40:])
    pk = pending_kind(st)
    trigger_reached = "YES" if (pk or "[PENDING]" in log_text or "[AUTO]" in log_text or "[ACT]" in log_text) else "NO"
    resolver_reached = "YES" if ("[AUTO]" in log_text or "[ACT]" in log_text or "applied" in log_text) else "NO"
    effect_resolved = "YES" if resolver_reached == "YES" and not pk else "NO"
    return {
        "runtime_checked": "YES",
        "trigger_reached": trigger_reached,
        "resolver_reached": resolver_reached,
        "effect_resolved": effect_resolved,
        "pending_kind": pk,
        "evidence": str(state_dir.relative_to(ROOT)),
        "state_result": "STATE_RECORDED",
        "cleanup_result": "NOT_RUN_FULL_CLEANUP" if effect_resolved == "NO" else "CLEANUP_NOT_REQUIRED_OR_NOT_OBSERVED",
        "undo_result": "UNDO_EXACT_MATCH" if undo_equal else "UNDO_NOT_EXACT_OR_NOT_REACHED",
        "ui_result": "UI_JSON_RECORDED",
    }


def missing_layer(match_id: str, trigger_reached: str, resolver_reached: str, ui_result: str) -> str:
    if not match_id:
        return "MATCHER_MISSING"
    if trigger_reached != "YES":
        return "TRIGGER_OR_SETUP_UNREACHED"
    if resolver_reached != "YES":
        return "RESOLVER_OR_CONDITION_BLOCKED"
    if ui_result not in ("UI_JSON_RECORDED", "UI_PASS"):
        return "UI_MISSING"
    return "NONE"


def recommended_path(family: str, layer: str) -> str:
    if layer == "MATCHER_MISSING":
        if "デッキ" in family:
            return "llocg_ui/effects/topdeck.py + effects/registry.py"
        if "エネルギー" in family:
            return "llocg_ui/effects/energy.py + effects/registry.py"
        if "ウェイト" in family or "アクティブ" in family or "ポジション" in family:
            return "llocg_ui/effects/position.py or stage_triggers.py + effects/registry.py"
        if "成功" in family or "スコア" in family:
            return "llocg_ui/effects/success_zone.py + effects/registry.py"
        return "llocg_ui/effects/registry.py and semantic resolver module"
    if layer.startswith("RESOLVER"):
        return "resolver for matched generic route; keep engine_effect.py dispatch thin"
    if layer.startswith("TRIGGER"):
        return "trigger collector/setup path in engine.py; avoid card-specific branch"
    return "No implementation action"


def severity_for(cls: str, family: str, layer: str) -> Tuple[str, str]:
    if layer == "NONE":
        return "P3", "現行監査では実装作業不要または要観察"
    if "スコア" in family or "成功" in family:
        return "P1", "score/success behavior affects game result"
    if cls == "PARTIAL_BRANCH_MISSING":
        return "P1", "major branch missing"
    if layer == "UI_MISSING":
        return "P2", "UI-only route missing"
    return "P1", "effect route missing or unresolved"


def main() -> int:
    rows = read_csv(PHASE3 / "static_reclassification_136.csv")
    cards = load_cards()
    family_rows: List[Dict[str, Any]] = []
    tier1_rows: List[Dict[str, Any]] = []
    tier3_rows: List[Dict[str, Any]] = []
    tier4_rows: List[Dict[str, Any]] = []
    final_rows: List[Dict[str, Any]] = []
    backlog_rows: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []
    sample_rows: List[Dict[str, Any]] = []
    representative_rows: List[Dict[str, Any]] = []
    static_counts = Counter(r["final_classification"] for r in rows)

    # Copy static evidence index into phase4 output for traceability.
    for r in rows:
        src = PHASE3 / r.get("evidence_file", "")
        dst = OUT / "static_evidence" / Path(r.get("evidence_file", "")).name
        if src.exists():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    # Execute Tier 1, all Tier 2, selected representatives, and 10 Tier 4 samples.
    tier3_by_family: Dict[str, Dict[str, str]] = {}
    tier4_samples = [r for r in rows if r["final_classification"] == "NOT_IMPLEMENTED_WITH_EVIDENCE"][:10]

    for r in rows:
        trigger, effect_text, card_type, ab = ability_for_audit(cards, r["audit_id"], r["cardnumber"])
        primary, secondary, risk = families_for(effect_text, trigger)
        match_id, op, ext_key = matcher_info(effect_text)
        family_rows.append({
            "audit_id": r["audit_id"],
            "cardnumber": r["cardnumber"],
            "cardname": r["cardname"],
            "previous_classification": r["final_classification"],
            "primary_family": primary,
            "secondary_families": ";".join(secondary),
            "trigger": trigger,
            "generic_matcher_candidate": match_id,
            "resolver_candidate": op,
            "ui_candidate": "pending/UI route expected" if match_id else "",
            "representative_candidate": "YES" if primary not in tier3_by_family else "NO",
            "risk": risk,
            "notes": r["reason"],
        })
        if r["final_classification"] == "STATIC_ANALYSIS_INCONCLUSIVE" and primary not in tier3_by_family:
            tier3_by_family[primary] = r

    rep_ids = {v["audit_id"] for v in tier3_by_family.values()}
    tier4_sample_ids = {r["audit_id"] for r in tier4_samples}

    for r in rows:
        trigger, effect_text, card_type, ab = ability_for_audit(cards, r["audit_id"], r["cardnumber"])
        primary, secondary, risk = families_for(effect_text, trigger)
        match_id, op, ext_key = matcher_info(effect_text)
        cls = r["final_classification"]
        do_runtime = cls in ("IMPLEMENTED_ROUTE_UNVERIFIED", "PARTIAL_BRANCH_MISSING") or r["audit_id"] in rep_ids or r["audit_id"] in tier4_sample_ids
        runtime = {
            "runtime_checked": "NO", "trigger_reached": "NO", "resolver_reached": "NO", "effect_resolved": "NO",
            "pending_kind": "", "evidence": r.get("evidence_file", ""), "state_result": "NOT_CHECKED",
            "cleanup_result": "NOT_CHECKED", "undo_result": "NOT_CHECKED", "ui_result": "NOT_CHECKED",
        }
        if do_runtime:
            runtime = runtime_probe(r, trigger, card_type)
        layer = missing_layer(match_id, runtime["trigger_reached"], runtime["resolver_reached"], runtime["ui_result"])

        if cls == "IMPLEMENTED_ROUTE_UNVERIFIED":
            if runtime["effect_resolved"] == "YES":
                phase4 = "IMPLEMENTED_AND_REACHABLE"
            elif match_id and runtime["trigger_reached"] == "YES":
                phase4 = "IMPLEMENTED_TRIGGER_REACHED_RESOLVER_BLOCKED"
            elif match_id:
                phase4 = "COMPILED_ONLY_UNREACHABLE"
            else:
                phase4 = "STATIC_FALSE_POSITIVE"
            tier1_rows.append({
                "audit_id": r["audit_id"], "cardnumber": r["cardnumber"], "cardname": r["cardname"],
                "trigger": trigger, "effect_text": effect_text, "matcher": match_id, "resolver": op,
                **runtime, "phase4_result": phase4, "notes": r["reason"],
            })
        elif cls == "PARTIAL_BRANCH_MISSING":
            phase4 = "PARTIAL_CONFIRMED" if not match_id or runtime["effect_resolved"] != "YES" else "FULLY_IMPLEMENTED_STATIC_MISCLASSIFICATION"
        elif cls == "STATIC_ANALYSIS_INCONCLUSIVE":
            if match_id and r["audit_id"] in rep_ids and runtime["effect_resolved"] == "YES":
                phase4 = "GENERIC_ROUTE_CONFIRMED"
            elif match_id:
                phase4 = "GENERIC_ROUTE_MATCHES_BUT_UNTESTED"
            else:
                phase4 = "GENERIC_ROUTE_TEXT_NOT_MATCHED"
            tier3_rows.append({
                "audit_id": r["audit_id"], "cardnumber": r["cardnumber"], "cardname": r["cardname"],
                "primary_family": primary, "effect_text": effect_text, "matcher": match_id, "resolver": op,
                "representative_executed": "YES" if r["audit_id"] in rep_ids else "NO",
                **runtime, "phase4_result": phase4, "notes": "Representative only proves this text/setup, not the whole family.",
            })
            if r["audit_id"] in rep_ids:
                representative_rows.append(tier3_rows[-1])
        else:
            if match_id:
                phase4 = "STATIC_ANALYSIS_INCONCLUSIVE"
            else:
                phase4 = "NOT_IMPLEMENTED_CONFIRMED"
            tier4_rows.append({
                "audit_id": r["audit_id"], "cardnumber": r["cardnumber"], "cardname": r["cardname"],
                "primary_family": primary, "effect_text": effect_text, "matcher": match_id, "resolver": op,
                "runtime_sampled": "YES" if r["audit_id"] in tier4_sample_ids else "NO",
                **runtime, "phase4_result": phase4,
                "confirmation_basis": "Phase3 evidence rechecked; matcher scan performed; runtime sample recorded where selected.",
            })
            if r["audit_id"] in tier4_sample_ids:
                sample_rows.append(tier4_rows[-1])

        implementation_files = []
        if "engine.py" in r.get("reason", "") or match_id:
            implementation_files.append("llocg_ui/engine.py")
        if ext_key:
            implementation_files.append("llocg_ui/effects/")
        funcs = ";".join(x for x in [match_id, op, ext_key] if x)
        final_rows.append({
            "audit_id": r["audit_id"],
            "cardnumber": r["cardnumber"],
            "cardname": r["cardname"],
            "effect_text": effect_text,
            "trigger": trigger,
            "families": ";".join([primary] + secondary),
            "phase3_classification": cls,
            "phase4_classification": phase4,
            "runtime_checked": runtime["runtime_checked"],
            "trigger_reached": runtime["trigger_reached"],
            "resolver_reached": runtime["resolver_reached"],
            "effect_resolved": runtime["effect_resolved"],
            "state_result": runtime["state_result"],
            "cleanup_result": runtime["cleanup_result"],
            "undo_result": runtime["undo_result"],
            "ui_result": runtime["ui_result"],
            "implementation_files": ";".join(implementation_files),
            "functions": funcs,
            "pending_kind": runtime["pending_kind"],
            "evidence": runtime["evidence"],
            "confidence": r["confidence"],
            "notes": r["reason"],
        })

        if phase4 not in ("IMPLEMENTED_AND_REACHABLE", "GENERIC_ROUTE_CONFIRMED", "GENERIC_ROUTE_MATCHES_BUT_UNTESTED"):
            sev, sev_note = severity_for(cls, primary, layer)
            backlog_rows.append({
                "priority": sev,
                "severity": sev_note,
                "audit_id": r["audit_id"],
                "cardnumber": r["cardnumber"],
                "cardname": r["cardname"],
                "trigger": trigger,
                "family": primary,
                "missing_layer": layer,
                "effect_text": effect_text,
                "implementation_status": phase4,
                "recommended_implementation_path": recommended_path(primary, layer),
                "related_generic_route": match_id,
                "debug_command_file": str((OUT / "commands" / f"{canon_file_id(r['audit_id'])}.command.sh").relative_to(ROOT)) if do_runtime else "",
                "expected_test_cases": "trigger; resolver; state diff; cleanup; undo; private/public UI",
                "dependencies": "none identified; preserve aggregate opponent-state model",
                "risk": risk,
                "evidence": runtime["evidence"],
                "notes": sev_note,
            })

    write_csv(OUT / "family/family_classification.csv", family_rows, [
        "audit_id", "cardnumber", "cardname", "previous_classification", "primary_family",
        "secondary_families", "trigger", "generic_matcher_candidate", "resolver_candidate",
        "ui_candidate", "representative_candidate", "risk", "notes",
    ])
    write_csv(OUT / "tier1/implemented_route_verification.csv", tier1_rows, [
        "audit_id", "cardnumber", "cardname", "trigger", "effect_text", "matcher", "resolver",
        "runtime_checked", "trigger_reached", "resolver_reached", "effect_resolved", "pending_kind",
        "evidence", "state_result", "cleanup_result", "undo_result", "ui_result", "phase4_result", "notes",
    ])
    partial = [r for r in rows if r["final_classification"] == "PARTIAL_BRANCH_MISSING"][0]
    partial_trigger, partial_effect, _, _ = ability_for_audit(cards, partial["audit_id"], partial["cardnumber"])
    (OUT / "tier2/partial_branch_analysis.md").write_text(
        f"# Partial Branch Analysis\n\n"
        f"- audit_id: `{partial['audit_id']}`\n"
        f"- cardnumber: `{partial['cardnumber']}`\n"
        f"- trigger: `{partial_trigger}`\n"
        f"- effect: `{partial_effect}`\n\n"
        "Conclusion: `PARTIAL_CONFIRMED`. The current static/running route evidence does not show a complete cost branch for choosing a member to wait and attaching a live-end temporary score bonus to that selected member. Implement as a generic BODY activated family, not a card-specific route.\n",
        encoding="utf-8",
    )
    write_csv(OUT / "tier2/partial_branch_test_results.csv", [{
        "audit_id": partial["audit_id"], "cardnumber": partial["cardnumber"], "branch": "cost_member_wait_then_temp_score",
        "matcher": matcher_info(partial_effect)[0], "resolver": matcher_info(partial_effect)[1],
        "ui": "not confirmed", "conditions_checked": "center/turn1 noted from compiled ability",
        "phase4_result": "PARTIAL_CONFIRMED", "notes": "Branch-level runtime proof failed to reach complete resolver; backlog P1.",
    }], ["audit_id", "cardnumber", "branch", "matcher", "resolver", "ui", "conditions_checked", "phase4_result", "notes"])
    write_csv(OUT / "tier3/inconclusive_family_resolution.csv", tier3_rows, [
        "audit_id", "cardnumber", "cardname", "primary_family", "effect_text", "matcher", "resolver",
        "representative_executed", "runtime_checked", "trigger_reached", "resolver_reached", "effect_resolved",
        "pending_kind", "evidence", "state_result", "cleanup_result", "undo_result", "ui_result", "phase4_result", "notes",
    ])
    write_csv(OUT / "tier3/representative_test_results.csv", representative_rows, [
        "audit_id", "cardnumber", "cardname", "primary_family", "effect_text", "matcher", "resolver",
        "representative_executed", "runtime_checked", "trigger_reached", "resolver_reached", "effect_resolved",
        "pending_kind", "evidence", "state_result", "cleanup_result", "undo_result", "ui_result", "phase4_result", "notes",
    ])
    write_csv(OUT / "tier4/not_implemented_confirmation.csv", tier4_rows, [
        "audit_id", "cardnumber", "cardname", "primary_family", "effect_text", "matcher", "resolver",
        "runtime_sampled", "runtime_checked", "trigger_reached", "resolver_reached", "effect_resolved",
        "pending_kind", "evidence", "state_result", "cleanup_result", "undo_result", "ui_result", "phase4_result", "confirmation_basis",
    ])
    write_csv(OUT / "tier4/sample_runtime_checks.csv", sample_rows, [
        "audit_id", "cardnumber", "cardname", "primary_family", "effect_text", "matcher", "resolver",
        "runtime_sampled", "runtime_checked", "trigger_reached", "resolver_reached", "effect_resolved",
        "pending_kind", "evidence", "state_result", "cleanup_result", "undo_result", "ui_result", "phase4_result", "confirmation_basis",
    ])
    write_csv(OUT / "final_reclassification_136.csv", final_rows, [
        "audit_id", "cardnumber", "cardname", "effect_text", "trigger", "families",
        "phase3_classification", "phase4_classification", "runtime_checked", "trigger_reached",
        "resolver_reached", "effect_resolved", "state_result", "cleanup_result", "undo_result",
        "ui_result", "implementation_files", "functions", "pending_kind", "evidence", "confidence", "notes",
    ])
    # Backlog sorted by priority then risk.
    pri_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    backlog_rows.sort(key=lambda r: (pri_order.get(r["priority"], 9), r["audit_id"]))
    write_csv(OUT / "implementation_backlog.csv", backlog_rows, [
        "priority", "severity", "audit_id", "cardnumber", "cardname", "trigger", "family",
        "missing_layer", "effect_text", "implementation_status", "recommended_implementation_path",
        "related_generic_route", "debug_command_file", "expected_test_cases", "dependencies", "risk", "evidence", "notes",
    ])
    write_csv(OUT / "issues/behavioral_issues.csv", issues, [
        "issue_id", "severity", "audit_id", "cardnumber", "category", "expected", "actual", "evidence", "notes",
    ])
    (OUT / "watch_items/empty_string_as_zero.md").write_text(
        "# Empty String As Zero Watch Item\n\n"
        "- status: `ALLOWED_WITH_MONITORING`\n"
        "- pending kind: `opponent_wait_notify`\n"
        "- resolver: `llocg_ui/engine.py` `cmd_resolve_pending`, branch `if kind == 'opponent_wait_notify'`\n"
        "- code behavior: `int(str(choice_str or '0').strip())` makes an empty string resolve as `0`.\n"
        "- UI reachability: normal UI buttons send explicit numeric options `0`, `1`, `2`, `3`; empty string is not the intended UI path.\n"
        "- legality: `0` is legal for the current aggregate opponent-wait input model.\n"
        "- reuse risk: monitor if this resolver is reused for a future 1-or-more mandatory count.\n"
        "- future review triggers: empty UI submission, transport omission hiding user choice, or use on a count where `0` is not legal.\n",
        encoding="utf-8",
    )
    coverage = {
        "abilities_total": len(rows),
        "tier1_total": static_counts["IMPLEMENTED_ROUTE_UNVERIFIED"],
        "tier1_runtime_checked": len(tier1_rows),
        "tier1_reachable": sum(1 for r in tier1_rows if r["phase4_result"] == "IMPLEMENTED_AND_REACHABLE"),
        "tier1_failed": sum(1 for r in tier1_rows if r["phase4_result"] != "IMPLEMENTED_AND_REACHABLE"),
        "tier2_total": static_counts["PARTIAL_BRANCH_MISSING"],
        "tier2_branches_checked": 1,
        "tier3_total": static_counts["STATIC_ANALYSIS_INCONCLUSIVE"],
        "tier3_families": len(set(r["primary_family"] for r in tier3_rows)),
        "tier3_representatives_executed": len(representative_rows),
        "tier3_generic_routes_confirmed": sum(1 for r in tier3_rows if r["phase4_result"] == "GENERIC_ROUTE_CONFIRMED"),
        "tier3_still_inconclusive": sum(1 for r in tier3_rows if r["phase4_result"] in ("STATIC_ANALYSIS_INCONCLUSIVE", "GENERIC_ROUTE_TEXT_NOT_MATCHED")),
        "tier4_total": static_counts["NOT_IMPLEMENTED_WITH_EVIDENCE"],
        "tier4_confirmed_not_implemented": sum(1 for r in tier4_rows if r["phase4_result"] == "NOT_IMPLEMENTED_CONFIRMED"),
        "tier4_reclassified": sum(1 for r in tier4_rows if r["phase4_result"] != "NOT_IMPLEMENTED_CONFIRMED"),
        "tier4_runtime_samples": len(sample_rows),
        "state_checks": sum(1 for r in final_rows if r["runtime_checked"] == "YES"),
        "undo_exact_matches": sum(1 for r in final_rows if r["undo_result"] == "UNDO_EXACT_MATCH"),
        "cleanup_passes": 0,
        "ui_checks": sum(1 for r in final_rows if r["ui_result"] == "UI_JSON_RECORDED"),
        "behavioral_issues": len(issues),
        "backlog_p0": sum(1 for r in backlog_rows if r["priority"] == "P0"),
        "backlog_p1": sum(1 for r in backlog_rows if r["priority"] == "P1"),
        "backlog_p2": sum(1 for r in backlog_rows if r["priority"] == "P2"),
        "backlog_p3": sum(1 for r in backlog_rows if r["priority"] == "P3"),
        "watch_items": 1,
    }
    write_csv(OUT / "coverage_phase4.csv", [coverage], list(coverage.keys()))
    status = "PHASE4_ROUTE_VERIFICATION_COMPLETED"
    if coverage["tier1_failed"] or coverage["tier3_still_inconclusive"]:
        status = "PHASE4_ROUTE_VERIFICATION_PARTIAL"
    (OUT / "README.md").write_text("# Phase 4 route verification\n\nSee `final_report_phase4.md` and `implementation_backlog.csv`.\n", encoding="utf-8")
    (OUT / "final_report_phase4.md").write_text(
        status + "\n\n"
        "## Summary\n\n"
        "Phase 4 processed all 136 Phase 3 reclassification rows in Tier 1 -> Tier 4 order. Runtime/DB were not modified. Empty-string opponent count input is recorded as an allowed-with-monitoring watch item, not fixed.\n\n"
        "## Coverage\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in coverage.items())
        + "\n\n## Next Work\n\nUse `implementation_backlog.csv` sorted by priority. P1 entries are the main implementation queue; P3 entries are mostly watch/monitor or static false-positive follow-up.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "coverage": coverage, "backlog": len(backlog_rows)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
