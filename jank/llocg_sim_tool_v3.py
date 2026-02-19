#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLOCG Sim Tool (v3) — compile + TODO mining + minimal sim

Adds:
- `todo` subcommand: ranks unresolved templates (op == "TODO") from compiled JSON.
- Optional filtering by a cardnumber list file (one per line; comments allowed).
- Default output under ROOT (parent of --compiled) unless --outdir is given.

Dependencies:
  pip install pandas pyyaml
"""
from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import yaml


def _auto_find_patterns(
    csv_path: Path,
    patterns_dir: Optional[Path],
    cost_yaml: Optional[Path],
    effect_yaml: Optional[Path],
) -> tuple[Path, Path]:
    root = csv_path.parent
    if patterns_dir is not None:
        base = patterns_dir
    else:
        cand = root / "patterns"
        base = cand if cand.exists() else root

    def pick_one(globs: List[str]) -> Optional[Path]:
        for g in globs:
            hits = sorted(base.glob(g))
            if hits:
                return hits[0]
        return None

    if cost_yaml is None:
        cost_yaml = pick_one(["cost_patterns*.yaml", "**/cost_patterns*.yaml"])
    if effect_yaml is None:
        effect_yaml = pick_one(["effect_patterns*.yaml", "**/effect_patterns*.yaml"])

    if cost_yaml is None:
        hits = sorted(root.glob("**/cost_patterns*.yaml"))
        cost_yaml = hits[0] if hits else None
    if effect_yaml is None:
        hits = sorted(root.glob("**/effect_patterns*.yaml"))
        effect_yaml = hits[0] if hits else None

    if cost_yaml is None:
        raise FileNotFoundError(f"cost_patterns*.yaml not found under: {root}")
    if effect_yaml is None:
        raise FileNotFoundError(f"effect_patterns*.yaml not found under: {root}")

    print(f"[INFO] ROOT        : {root}")
    print(f"[INFO] patterns dir: {base}")
    print(f"[INFO] cost yaml   : {cost_yaml}")
    print(f"[INFO] effect yaml : {effect_yaml}")
    return cost_yaml, effect_yaml


def _read_cardno_list(path: Path) -> set[str]:
    s: set[str] = set()
    for ln in path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        if "," in ln:
            ln = ln.split(",", 1)[0].strip()
        s.add(ln)
    return s


def mine_todo(compiled_path: Path, outdir: Path, top: int = 200, cardno_list: Optional[Path] = None) -> None:
    obj = json.loads(compiled_path.read_text(encoding="utf-8"))
    cards = obj.get("cards", [])
    filter_set: Optional[set[str]] = _read_cardno_list(cardno_list) if cardno_list else None

    rows: List[Dict[str, Any]] = []
    for c in cards:
        cardno = c.get("cardnumber", "")
        if filter_set is not None and cardno not in filter_set:
            continue
        cname = c.get("cardname", "")
        ctype = c.get("card_type", "")
        for ab in c.get("abilities", []):
            abt = ab.get("ability_type", "")
            trg = ab.get("trigger", "")
            cond = ab.get("conditions", "")
            for cl in ab.get("clauses", []):
                cost_t = (cl.get("cost_template", "") or "").strip()
                eff_t = (cl.get("effect_template", "") or "").strip()
                cop = cl.get("cost_op")
                eop = cl.get("effect_op")

                if cop and cop.get("op") == "TODO" and cost_t:
                    rows.append({
                        "kind": "cost",
                        "template": cost_t,
                        "ability_type": abt,
                        "trigger": trg,
                        "conditions": cond,
                        "cardnumber": cardno,
                        "cardname": cname,
                        "card_type": ctype,
                        "raw": cl.get("raw", ""),
                    })
                if eop and eop.get("op") == "TODO" and eff_t:
                    rows.append({
                        "kind": "effect",
                        "template": eff_t,
                        "ability_type": abt,
                        "trigger": trg,
                        "conditions": cond,
                        "cardnumber": cardno,
                        "cardname": cname,
                        "card_type": ctype,
                        "raw": cl.get("raw", ""),
                    })

    if not rows:
        print("[DONE] no TODO ops found (or filter removed all).")
        return

    df = pd.DataFrame(rows)
    outdir.mkdir(parents=True, exist_ok=True)

    agg = (df.groupby(["kind", "template", "ability_type", "trigger", "conditions"])
             .size()
             .reset_index(name="count")
             .sort_values("count", ascending=False))

    ex = (df.groupby(["kind", "template", "ability_type", "trigger", "conditions"], as_index=False)
            .first()[["kind","template","ability_type","trigger","conditions","cardnumber","cardname","card_type","raw"]])
    out = agg.merge(ex, on=["kind","template","ability_type","trigger","conditions"], how="left")

    out_csv = outdir / "todo_rank.csv"
    out.head(top).to_csv(out_csv, index=False, encoding="utf-8-sig")
    out[out["kind"]=="cost"].head(top).to_csv(outdir/"todo_rank_cost.csv", index=False, encoding="utf-8-sig")
    out[out["kind"]=="effect"].head(top).to_csv(outdir/"todo_rank_effect.csv", index=False, encoding="utf-8-sig")

    print(f"[DONE] wrote {out_csv}")
    print("[TOP 10]")
    print(out.head(10)[["kind","count","ability_type","trigger","conditions","template"]].to_string(index=False))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    apt = sub.add_parser("todo", help="rank unresolved templates (op==TODO) from compiled JSON")
    apt.add_argument("--compiled", required=True, type=Path)
    apt.add_argument("--outdir", type=Path, default=None)
    apt.add_argument("--top", type=int, default=200)
    apt.add_argument("--cardnumbers", type=Path, default=None,
                     help="optional cardnumber list file to filter targets")

    args = ap.parse_args()

    if args.cmd == "todo":
        root = args.compiled.parent
        outdir = args.outdir if args.outdir is not None else (root / "todo_out")
        mine_todo(args.compiled, outdir, args.top, args.cardnumbers)

if __name__ == "__main__":
    main()
