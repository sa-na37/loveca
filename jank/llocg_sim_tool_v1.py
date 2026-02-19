#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLOCG Sim Tool (v1)
- Compile: cards_min_tokv1.csv + pattern YAMLs -> cards_compiled.json
- Sim: minimal placeholder sim to validate deck/hand evolution pipeline

Install:
  pip install pandas pyyaml

Usage:
  python3 llocg_sim_tool_v1.py compile \
    --csv llocg_db_out_full/cards_min_tokv1.csv \
    --cost-yaml llocg_patterns_seed_v1/cost_patterns_seed_v1.yaml \
    --effect-yaml llocg_patterns_seed_v1/effect_patterns_seed_v1.yaml \
    --out llocg_db_out_full/cards_compiled_v1.json

  python3 llocg_sim_tool_v1.py sim \
    --compiled llocg_db_out_full/cards_compiled_v1.json \
    --runs 200 \
    --out llocg_db_out_full/sim_out_v1
"""
from __future__ import annotations
import argparse, json, random, re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import yaml

def _auto_find_patterns(csv_path: Path,
                        patterns_dir: Path | None,
                        cost_yaml: Path | None,
                        effect_yaml: Path | None) -> tuple[Path, Path]:
    root = csv_path.parent

    # 優先順位：明示指定 > patterns-dir > root/patterns
    base = None
    if patterns_dir is not None:
        base = patterns_dir
    else:
        cand = root / "patterns"
        base = cand if cand.exists() else root

    # まず base 直下で探す
    def pick_one(globs: list[str]) -> Path | None:
        for g in globs:
            hits = sorted(base.glob(g))
            if hits:
                return hits[0]
        return None

    if cost_yaml is None:
        cost_yaml = pick_one(["cost_patterns*.yaml", "**/cost_patterns*.yaml"])
    if effect_yaml is None:
        effect_yaml = pick_one(["effect_patterns*.yaml", "**/effect_patterns*.yaml"])

    # baseで見つからない場合はroot配下を軽く探索
    if cost_yaml is None:
        hits = sorted(root.glob("**/cost_patterns*.yaml"))
        cost_yaml = hits[0] if hits else None
    if effect_yaml is None:
        hits = sorted(root.glob("**/effect_patterns*.yaml"))
        effect_yaml = hits[0] if hits else None

    if cost_yaml is None:
        raise FileNotFoundError(f"cost_patterns*.yaml not found under {root}")
    if effect_yaml is None:
        raise FileNotFoundError(f"effect_patterns*.yaml not found under {root}")

    print(f"[INFO] ROOT        : {root}")
    print(f"[INFO] patterns dir: {base}")
    print(f"[INFO] cost yaml   : {cost_yaml}")
    print(f"[INFO] effect yaml : {effect_yaml}")
    return cost_yaml, effect_yaml

def _norm_brackets(t: str) -> str:
    if not isinstance(t, str): return ""
    return (t.replace("＜","<").replace("＞",">")
              .replace("〈","<").replace("〉",">")
              .replace("《","<").replace("》",">"))

def split_trigger_blocks(effect_text_norm: str) -> List[Dict[str, Any]]:
    t = _norm_brackets(effect_text_norm)
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    ability_headers = {"自動","起動","常時"}
    auto_triggers = {"登場時","登場した時","登場","ライブ開始時","ライブ成功時","ライブ終了時","ライブ中",
                     "アタック時","アタックした時","ターン開始時","ターン終了時"}
    known_conditions = {"センター","ライト","レフト"}
    turn_n_re = re.compile(r"^ターン\s*[0-9０-９]+\s*回$")
    eventish_re = re.compile(r"(開始時|成功時|終了時|した時|時$)")

    def classify(h: str) -> Tuple[str,str]:
        h = h.strip()
        if h in ability_headers: return ("ability", h)
        if h.startswith("自動"): return ("ability","自動")
        if h.startswith("起動"): return ("ability","起動")
        if h.startswith("常時"): return ("ability","常時")
        if h in known_conditions or turn_n_re.match(h): return ("condition", h)
        if h in auto_triggers or eventish_re.search(h): return ("trigger", h)
        return ("condition", h)

    header_angle = re.compile(r"^<([^<>]+)>$")
    header_kakko = re.compile(r"^[\[\【\（]([^\]\】\）]+)[\]\】\）]$")

    def parse_header_line(ln: str) -> Optional[str]:
        m = header_angle.match(ln)
        if m and not ln.startswith("<("): return m.group(1).strip()
        m = header_kakko.match(ln)
        if m: return m.group(1).strip()
        return None

    blocks = []
    cur_ability, cur_trigger = "UNKNOWN", "BODY"
    cur_conditions: List[str] = []
    cur_lines: List[str] = []

    def flush():
        nonlocal cur_lines
        if cur_lines:
            ab = cur_ability
            if ab == "UNKNOWN" and cur_trigger != "BODY":
                ab = "自動"
            blocks.append({
                "ability_type": ab,
                "trigger": cur_trigger,
                "conditions": list(cur_conditions),
                "text": "\n".join(cur_lines).strip()
            })
        cur_lines = []

    for ln in lines:
        h = parse_header_line(ln)
        if h is None:
            cur_lines.append(ln); continue
        kind, val = classify(h)
        if kind == "ability":
            flush(); cur_ability = val; cur_trigger = "BODY"; cur_conditions = []; continue
        if kind == "trigger":
            flush()
            cur_ability = "自動"
            cur_trigger = val
            cur_conditions = []
            continue
        flush()
        cur_conditions.append(val)

    flush()
    return blocks

def split_cost_effect_clauses(block_text: str) -> List[Dict[str, Any]]:
    if not isinstance(block_text, str) or not block_text.strip(): return []
    raw = [ln.strip() for ln in block_text.splitlines() if ln.strip()]

    def clean(s: str) -> str:
        return s.lstrip("、。,.，・ ").strip()

    merge_tail = ("から","を","に","へ","の","と","して","または","および","及び")
    merged: List[str] = []
    for ln in raw:
        if not merged: merged.append(ln); continue
        prev = merged[-1]
        has_sep_prev = ("：" in prev) or (":" in prev)
        has_sep_ln = ("：" in ln) or (":" in ln)
        if (not has_sep_prev) and (not has_sep_ln) and any(prev.endswith(t) for t in merge_tail) and not ln.startswith("<"):
            merged[-1] = prev + ln
        else:
            merged.append(ln)

    clauses = []
    for ln in merged:
        sep = "：" if "：" in ln else (":" if ":" in ln else None)
        if sep:
            left,right = ln.split(sep,1)
            optional = ("してもよい" in left) or ("してもよい" in ln)
            clauses.append({"optional": optional, "cost_text": clean(left), "effect_text": clean(right), "raw": ln})
        else:
            clauses.append({"optional": ("してもよい" in ln), "cost_text": "", "effect_text": clean(ln), "raw": ln})
    return clauses

@dataclass
class Pattern:
    id: str
    template: str
    op: str
    params: Dict[str, Any]
    note: str = ""
    confidence: float = 0.0

def load_patterns(yaml_path: Path) -> Dict[str, Pattern]:
    obj = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    out: Dict[str, Pattern] = {}
    for p in obj.get("patterns", []):
        tmpl = str(p.get("template","")).strip()
        if not tmpl: continue
        out[tmpl] = Pattern(
            id=str(p.get("id","")),
            template=tmpl,
            op=str(p.get("op","TODO")).strip(),
            params=p.get("params", {}) or {},
            note=str(p.get("note","")),
            confidence=float(p.get("confidence", 0.0)),
        )
    return out

def compile_cards(csv_path: Path, cost_yaml: Path, effect_yaml: Path, out_json: Path) -> None:
    df = pd.read_csv(csv_path)
    req = ["cardnumber","cardname","card_type_norm","effect_text_norm"]
    for c in req:
        if c not in df.columns:
            raise SystemExit(f"[ERROR] missing column: {c}")

    cost_p = load_patterns(cost_yaml)
    eff_p = load_patterns(effect_yaml)

    compiled = {"schema_version": 1, "cards": []}
    for _, r in df.iterrows():
        blocks = split_trigger_blocks(str(r.get("effect_text_norm","") or ""))
        abilities = []
        for b in blocks:
            conds_s = ";".join([x for x in b.get("conditions",[]) if isinstance(x,str) and x.strip()])
            clauses = split_cost_effect_clauses(b.get("text",""))
            out_clauses = []
            for cl in clauses:
                ct = cl.get("cost_text","").strip()
                et = cl.get("effect_text","").strip()
                out_clauses.append({
                    "optional": bool(cl.get("optional", False)),
                    "cost_template": ct,
                    "effect_template": et,
                    "cost_op": asdict(cost_p[ct]) if ct in cost_p else None,
                    "effect_op": asdict(eff_p[et]) if et in eff_p else None,
                    "raw": cl.get("raw",""),
                })
            abilities.append({
                "ability_type": b.get("ability_type","UNKNOWN"),
                "trigger": b.get("trigger","BODY"),
                "conditions": conds_s,
                "clauses": out_clauses,
            })

        compiled["cards"].append({
            "cardnumber": str(r.get("cardnumber","")).strip(),
            "cardname": str(r.get("cardname","")).strip(),
            "card_type": str(r.get("card_type_norm","")).strip(),
            "abilities": abilities,
        })

    out_json.write_text(json.dumps(compiled, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DONE] {out_json}")

def run_min_sim(compiled_json: Path, runs: int, outdir: Path, seed: int = 1) -> None:
    obj = json.loads(compiled_json.read_text(encoding="utf-8"))
    cards = obj["cards"]
    rng = random.Random(seed)

    outdir.mkdir(parents=True, exist_ok=True)
    deck_proto = [c["cardnumber"] for c in cards]  # naive (1 copy each)

    rows = []
    for i in range(runs):
        deck = list(deck_proto); rng.shuffle(deck)
        hand, waiting = [], []

        def draw(n=1):
            nonlocal deck, hand
            for _ in range(n):
                if not deck: break
                hand.append(deck.pop(0))

        def discard_random(n=1):
            nonlocal hand, waiting
            for _ in range(n):
                if not hand: break
                j = rng.randrange(len(hand))
                waiting.append(hand.pop(j))

        draw(5)
        for _turn in range(1, 6):
            draw(1)

            disc_n = 0
            for c in cards:
                for ab in c.get("abilities", []):
                    for cl in ab.get("clauses", []):
                        cop = cl.get("cost_op")
                        if cop and cop.get("op") == "discard_hand":
                            n = cop.get("params", {}).get("n", 1)
                            if isinstance(n, str):
                                m = re.search(r"\d+", n)
                                n = int(m.group(0)) if m else 1
                            disc_n = int(n); break
                    if disc_n: break
                if disc_n: break
            if disc_n:
                discard_random(disc_n)

        rows.append({"run": i, "deck_left": len(deck), "hand": len(hand), "waiting_room": len(waiting)})

    pd.DataFrame(rows).to_csv(outdir/"summary.csv", index=False, encoding="utf-8-sig")
    (outdir/"summary.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DONE] sim out -> {outdir}")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("compile")
    c.add_argument("--csv", required=True, type=Path)
    c.add_argument("--cost-yaml", type=Path, default=None)
    c.add_argument("--effect-yaml", type=Path, default=None)
    c.add_argument("--patterns-dir", type=Path, default=None)


    s = sub.add_parser("sim")
    s.add_argument("--compiled", required=True, type=Path)
    s.add_argument("--runs", type=int, default=200)
    s.add_argument("--out", required=True, type=Path)
    s.add_argument("--seed", type=int, default=1)

    args = ap.parse_args()
    if args.cmd == "compile":
    cost_yaml, effect_yaml = _auto_find_patterns(
        csv_path=args.csv,
        patterns_dir=args.patterns_dir,
        cost_yaml=args.cost_yaml,
        effect_yaml=args.effect_yaml,
    )
    compile_cards(args.csv, cost_yaml, effect_yaml, args.out)
    else:
        run_min_sim(args.compiled, args.runs, args.out, args.seed)

if __name__ == "__main__":
    main()
