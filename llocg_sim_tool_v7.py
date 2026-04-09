#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLOCG Sim Tool (v7) — compile + TODO mining (paren/icon stitching)

Fixes vs v7:
- Adds stronger clause stitching to prevent "effect template fragments":
  - Parenthetical spans split across lines are re-joined.
  - Consecutive icon-only lines are collapsed and can be treated as cost prefixes.
  - Icon runs that attach to a sentence (e.g., "ハートに、<(青)>...") are merged.

Other fixes inherited from v4:
- Merges fragment clauses:
  - "<(X)>" + "を得る。" => "<(X)>を得る。"
  - Lines that are only "か", "/", "（" etc. are merged into neighbors.
  - Prefix fragments like "ライブ終了時まで、" are merged with the following line.
- compile can omit --cost-yaml/--effect-yaml and will auto-find them under ROOT.
- `todo` subcommand: ranks unresolved templates (op == "TODO") from compiled JSON.

Dependencies:
  pip install pandas pyyaml
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import yaml


NO_ABILITY_TEXTS = {"", "(なし)", "(テキストなし)"}


def _norm_effect_status(v: Any) -> str:
    if v is None:
        return ""
    try:
        s = str(v).strip()
    except Exception:
        return ""
    return s.upper()


def is_no_ability_row(row: pd.Series) -> bool:
    status = _norm_effect_status(row.get("effect_text_status", ""))
    if status == "NO_ABILITY":
        return True

    flag = row.get("effect_text_is_no_ability", None)
    if flag is not None:
        try:
            if int(flag) == 1:
                return True
        except Exception:
            sval = str(flag).strip().lower()
            if sval in {"1", "true", "yes"}:
                return True

    effect_text = str(row.get("effect_text_norm", "") or "").strip()
    return effect_text in NO_ABILITY_TEXTS


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


def _norm_brackets(t: str) -> str:
    if not isinstance(t, str):
        return ""
    return (
        t.replace("＜", "<").replace("＞", ">")         .replace("〈", "<").replace("〉", ">")         .replace("《", "<").replace("》", ">")    )


def split_trigger_blocks(effect_text_norm: str) -> List[Dict[str, Any]]:
    t = _norm_brackets(effect_text_norm)
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]

    ability_headers = {"自動", "起動", "常時"}
    auto_triggers = {
        "登場時", "登場した時", "登場",
        "ライブ開始時", "ライブ成功時", "ライブ終了時", "ライブ中",
        "アタック時", "アタックした時",
        "ターン開始時", "ターン終了時",
    }
    known_conditions = {"センター", "ライト", "レフト", "左サイド", "右サイド"}
    turn_n_re = re.compile(r"^ターン\s*[0-9０-９]+\s*回$")
    eventish_re = re.compile(r"(開始時|成功時|終了時|した時|時$)")

    def classify_header(h: str) -> Tuple[str, str]:
        h = h.strip()
        if h in ability_headers:
            return ("ability", h)
        if h.startswith("自動"):
            return ("ability", "自動")
        if h.startswith("起動"):
            return ("ability", "起動")
        if h.startswith("常時"):
            return ("ability", "常時")
        if h in known_conditions or turn_n_re.match(h):
            return ("condition", h)
        if h in auto_triggers or eventish_re.search(h):
            return ("trigger", h)
        return ("condition", h)

    header_angle = re.compile(r"^<([^<>]+)>$")
    header_kakko = re.compile(r"^[\[\【\（]([^\]\】\）]+)[\]\】\）]$")

    def parse_header_line(ln: str) -> Optional[str]:
        m = header_angle.match(ln)
        if m and not ln.startswith("<("):
            return m.group(1).strip()
        m = header_kakko.match(ln)
        if m:
            return m.group(1).strip()
        return None

    blocks: List[Dict[str, Any]] = []
    cur_ability = "UNKNOWN"
    cur_trigger = "BODY"
    cur_conditions: List[str] = []
    cur_lines: List[str] = []

    def flush():
        nonlocal cur_lines
        if cur_lines:
            inferred = cur_ability
            if inferred == "UNKNOWN" and cur_trigger != "BODY":
                inferred = "自動"
            blocks.append({
                "ability_type": inferred,
                "trigger": cur_trigger,
                "conditions": list(cur_conditions),
                "text": "\n".join(cur_lines).strip(),
            })
        cur_lines = []

    for ln in lines:
        h = parse_header_line(ln)
        if h is not None:
            kind, val = classify_header(h)
            if kind == "ability":
                flush()
                cur_ability = val
                cur_trigger = "BODY"
                cur_conditions = []
                continue
            if kind == "trigger":
                flush()
                cur_ability = "自動"
                cur_trigger = val
                cur_conditions = []
                continue
            flush()
            cur_conditions.append(val)
            continue
        cur_lines.append(ln)

    flush()
    return blocks


def split_cost_effect_clauses(block_text: str) -> List[Dict[str, Any]]:
    if not isinstance(block_text, str) or not block_text.strip():
        return []
    raw_lines = [ln.strip() for ln in block_text.splitlines() if ln.strip()]

    def clean_leading_punct(s: str) -> str:
        return s.lstrip("、。,.，・ ").strip() if isinstance(s, str) else ""

    # --- Pre-normalize common wiki line-break artifacts ---
    # (A) Parenthetical spans split across lines: "（..." + "<(X)>" + "...）"
    pre0: List[str] = []
    buf: List[str] = []
    in_paren = False
    for ln in raw_lines:
        if not in_paren:
            if "（" in ln and "）" not in ln:
                buf = [ln]
                in_paren = True
            else:
                pre0.append(ln)
        else:
            buf.append(ln)
            if "）" in ln:
                pre0.append("".join(buf))
                buf = []
                in_paren = False
    if in_paren and buf:
        # Unclosed paren — keep as-is rather than dropping content
        pre0.extend(buf)

    # (B) Collapse consecutive icon-only lines into one run: "<(E)>" x N => "<(E)><(E)>..."
    angle_token = re.compile(r"^<\([^()]+\)>$")
    # one-or-more concatenated icon tokens (after collapsing)
    icon_run = re.compile(r"^(?:<\([^()]+\)>)+$")
    pre1: List[str] = []
    run: List[str] = []
    for ln in pre0:
        if angle_token.match(ln):
            run.append(ln)
            continue
        if run:
            pre1.append("".join(run))
            run = []
        pre1.append(ln)
    if run:
        pre1.append("".join(run))

    # (C) If an icon-run precedes a cost/effect clause (has '：' or ':'), treat it as cost prefix.
    pre2: List[str] = []
    i0 = 0
    while i0 < len(pre1):
        ln = pre1[i0]
        if icon_run.match(ln) and i0 + 1 < len(pre1) and ("：" in pre1[i0 + 1] or ":" in pre1[i0 + 1]):
            nxt = pre1[i0 + 1]
            sep = "：" if "：" in nxt else ":"
            left, right = nxt.split(sep, 1)
            left = left.strip()
            right = right.strip()
            pre2.append(f"{ln}{left}{sep}{right}")
            i0 += 2
            continue
        pre2.append(ln)
        i0 += 1

    # (D) If an icon-run is attached to a sentence (previous ends with a joiner like '、'/'に'), merge into previous.
    joiners = ("、", "，", ",", "に", "に、", "が", "を", "は", "の", "と", "で", "へ", "から", "まで", "も", "や", "か", "または")
    pre3: List[str] = []
    for ln in pre2:
        if pre3 and icon_run.match(ln):
            if pre3[-1].endswith(joiners):
                pre3[-1] = pre3[-1] + ln
                continue
        pre3.append(ln)

    # --- Existing heuristic merges ---
    merge_tail = ("から", "を", "に", "へ", "の", "と", "して", "または", "および", "及び")
    merged1: List[str] = []
    for ln in pre3:
        if not merged1:
            merged1.append(ln)
            continue
        prev = merged1[-1]
        has_sep_prev = ("：" in prev) or (":" in prev)
        has_sep_ln = ("：" in ln) or (":" in ln)
        if (not has_sep_prev) and (not has_sep_ln) and any(prev.endswith(t) for t in merge_tail) and not ln.startswith("<"):
            merged1[-1] = prev + ln
        else:
            merged1.append(ln)

    # Reuse the same regex; icon-runs have already been collapsed.
    angle_token = re.compile(r"^<\([^()]+\)>$")
    icon_run = re.compile(r"^(?:<\([^()]+\)>)+$")
    fragile_only = {"か", "/", "／", "（", "）", "(", ")", "，", ",", "、", "。"}
    prefix_merge = ("ライブ終了時まで、", "ライブ終了時まで", "ライブ開始時まで、", "このターン中、")
    suffix_need_next = ("まで、", "まで", "まで，")

    merged2: List[str] = []
    i = 0
    while i < len(merged1):
        ln = merged1[i]

        if ln in {"(なし)", "(テキストなし)"}:
            i += 1
            continue

        if icon_run.match(ln) and i + 1 < len(merged1):
            nxt = merged1[i + 1].strip()
            if nxt in {"を得る。", "を得る", "を得る．"}:
                merged2.append(ln + nxt)
                i += 2
                continue

        if ln in fragile_only:
            if merged2:
                merged2[-1] = merged2[-1] + ln
            elif i + 1 < len(merged1):
                merged1[i + 1] = ln + merged1[i + 1]
            i += 1
            continue

        if ln.startswith(prefix_merge) and i + 1 < len(merged1):
            merged1[i + 1] = ln + merged1[i + 1]
            i += 1
            continue

        if ln.endswith(suffix_need_next) and i + 1 < len(merged1):
            merged1[i + 1] = ln + merged1[i + 1]
            i += 1
            continue

        merged2.append(ln)
        i += 1

    clauses: List[Dict[str, Any]] = []
    for ln in merged2:
        sep = "：" if "：" in ln else (":" if ":" in ln else None)
        if sep:
            left, right = ln.split(sep, 1)
            left, right = left.strip(), right.strip()
            optional = ("してもよい" in left) or ("してもよい" in ln)
            clauses.append({
                "optional": optional,
                "cost_text": clean_leading_punct(left),
                "effect_text": clean_leading_punct(right),
                "raw": ln,
            })
        else:
            clauses.append({
                "optional": ("してもよい" in ln),
                "cost_text": "",
                "effect_text": clean_leading_punct(ln),
                "raw": ln,
            })

    # --- Clause-level stitching (fixes residual fragment templates in TODO mining) ---
    # Merge patterns like: "<(桃)>" + "を得る。" or prefix + "減らす。" where the suffix became its own clause.
    icon_run_re = re.compile(r"^(?:<\([^()]+\)>)+$")
    suffix_set = {"を得る。", "を得る", "減らす。", "少なくなる。", "になる。"}

    stitched: List[Dict[str, Any]] = []
    for cl in clauses:
        if not stitched:
            stitched.append(cl)
            continue
        prev = stitched[-1]
        cur_eff = (cl.get("effect_text") or "").strip()
        prev_eff = (prev.get("effect_text") or "").strip()

        # icon-only + 得る => merge
        if icon_run_re.match(prev_eff) and cur_eff in {"を得る。", "を得る"}:
            prev["effect_text"] = prev_eff + cur_eff
            prev["raw"] = (prev.get("raw", "") + "\\n" + cl.get("raw", "")).strip()
            continue

        # prefix + short suffix (where prev doesn't already end a sentence)
        if cur_eff in suffix_set and prev_eff and not prev_eff.endswith("。") and not icon_run_re.match(cur_eff):
            prev["effect_text"] = prev_eff + cur_eff
            prev["raw"] = (prev.get("raw", "") + "\\n" + cl.get("raw", "")).strip()
            continue

        # If current is icon-only, it is typically a parameter line (e.g., color/heart list).
        # Merge into previous unless the previous already ends a sentence.
        if icon_run_re.match(cur_eff) and prev_eff and not prev_eff.endswith("。"):
            prev["effect_text"] = prev_eff + cur_eff
            prev["raw"] = (prev.get("raw", "") + "\n" + cl.get("raw", "")).strip()
            continue

        stitched.append(cl)

    return stitched


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
    patterns: Dict[str, Pattern] = {}
    for p in obj.get("patterns", []):
        tmpl = str(p.get("template", "")).strip()
        if not tmpl:
            continue
        patterns[tmpl] = Pattern(
            id=str(p.get("id", "")),
            template=tmpl,
            op=str(p.get("op", "TODO")).strip(),
            params=p.get("params", {}) or {},
            note=str(p.get("note", "")),
            confidence=float(p.get("confidence", 0.0)),
        )
    return patterns


def compile_cards(csv_path: Path, cost_yaml: Path, effect_yaml: Path, out_json: Path) -> None:
    df = pd.read_csv(csv_path)
    for col in ["cardnumber", "cardname", "card_type_norm", "effect_text_norm"]:
        if col not in df.columns:
            raise SystemExit(f"[ERROR] required column missing: {col}")

    cost_pats = load_patterns(cost_yaml)
    eff_pats = load_patterns(effect_yaml)

    compiled: Dict[str, Any] = {"schema_version": 1, "source_csv": str(csv_path), "cards": []}

    for _, r in df.iterrows():
        cardno = str(r.get("cardnumber", "")).strip()
        name = str(r.get("cardname", "")).strip()
        ctype = str(r.get("card_type_norm", "")).strip()
        effect_text = str(r.get("effect_text_norm", "") or "").strip()

        row_is_no_ability = is_no_ability_row(r)
        parse_status = "NO_ABILITY" if row_is_no_ability else "OK"

        abilities: List[Dict[str, Any]] = []
        if not row_is_no_ability:
            blocks = split_trigger_blocks(effect_text)

            for b in blocks:
                clauses = split_cost_effect_clauses(b.get("text", ""))
                conds = b.get("conditions", [])
                conds_s = ";".join([c for c in conds if isinstance(c, str) and c.strip()])

                compiled_clauses: List[Dict[str, Any]] = []
                for cl in clauses:
                    cost_t = cl.get("cost_text", "").strip()
                    eff_t = cl.get("effect_text", "").strip()
                    cost_pat = cost_pats.get(cost_t) if cost_t else None
                    eff_pat = eff_pats.get(eff_t) if eff_t else None

                    compiled_clauses.append({
                        "optional": bool(cl.get("optional", False)),
                        "cost_template": cost_t,
                        "effect_template": eff_t,
                        "cost_op": asdict(cost_pat) if cost_pat else None,
                        "effect_op": asdict(eff_pat) if eff_pat else None,
                        "raw": cl.get("raw", ""),
                    })

                abilities.append({
                    "ability_type": b.get("ability_type", "UNKNOWN"),
                    "trigger": b.get("trigger", "BODY"),
                    "conditions": conds_s,
                    "clauses": compiled_clauses,
                })

            # Defensive fallback: if text exists but nothing compiled, keep UNKNOWN for auditability.
            if effect_text and not abilities:
                parse_status = "UNKNOWN"

        compiled["cards"].append({
            "cardnumber": cardno,
            "cardname": name,
            "card_type": ctype,
            "parse_status": parse_status,
            "abilities": abilities,
        })

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(compiled, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DONE] wrote {out_json}")


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

    apc = sub.add_parser("compile")
    apc.add_argument("--csv", required=True, type=Path)
    apc.add_argument("--out", required=True, type=Path)
    apc.add_argument("--patterns-dir", type=Path, default=None)
    apc.add_argument("--cost-yaml", type=Path, default=None)
    apc.add_argument("--effect-yaml", type=Path, default=None)

    apt = sub.add_parser("todo")
    apt.add_argument("--compiled", required=True, type=Path)
    apt.add_argument("--outdir", type=Path, default=None)
    apt.add_argument("--top", type=int, default=200)
    apt.add_argument("--cardnumbers", type=Path, default=None)

    args = ap.parse_args()

    if args.cmd == "compile":
        cost_yaml, effect_yaml = _auto_find_patterns(args.csv, args.patterns_dir, args.cost_yaml, args.effect_yaml)
        compile_cards(args.csv, cost_yaml, effect_yaml, args.out)

    elif args.cmd == "todo":
        root = args.compiled.parent
        outdir = args.outdir if args.outdir is not None else (root / "todo_out")
        mine_todo(args.compiled, outdir, args.top, args.cardnumbers)


if __name__ == "__main__":
    main()
