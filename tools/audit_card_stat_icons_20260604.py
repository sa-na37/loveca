#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
# BUILD_TAG: audit_card_stat_icons_20260604a

"""Audit raw icon stat fields after the 2026 DB update.

Checks for rows where official-like raw fields such as '<赤> 2 <任意> 7'
exist, but normalized *_counts_json / *_tags_json are blank.  Also verifies
that the runtime db loader repairs these rows from raw fields.
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

FW_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")
ICON_RE = re.compile(r"<\s*\(?\s*([^<>（）()]+?)\s*\)?\s*>\s*(?:(?:×|x|X)\s*)?([0-9０-９]+)?")
COLOR_MAP = {"桃":"pink","赤":"red","黄":"yellow","緑":"green","青":"blue","紫":"purple","任意":"any","ALL":"all"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def jdict(s: Any) -> Dict[str, int]:
    try:
        d = json.loads(s or "{}") if isinstance(s, str) else (s or {})
    except Exception:
        return {}
    if not isinstance(d, dict):
        return {}
    out = {}
    for k, v in d.items():
        try:
            iv = int(v)
        except Exception:
            continue
        if iv:
            out[str(k)] = iv
    return out


def jlist(s: Any) -> List[str]:
    try:
        x = json.loads(s or "[]") if isinstance(s, str) else (s or [])
    except Exception:
        return []
    return [str(v) for v in x] if isinstance(x, list) else []


def raw_counts(raw: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for m in ICON_RE.finditer(str(raw or "").translate(FW_DIGITS)):
        tok = str(m.group(1) or "").strip().replace(" ", "").replace("＋", "+")
        key = COLOR_MAP.get(tok)
        if not key:
            continue
        n = int(m.group(2)) if m.group(2) else 1
        out[key] = int(out.get(key, 0) or 0) + n
    return out


def raw_tags(raw: str) -> List[str]:
    tags: List[str] = []
    for m in ICON_RE.finditer(str(raw or "").translate(FW_DIGITS).replace("＋", "+")):
        tok = str(m.group(1) or "").strip().replace(" ", "")
        if tok in COLOR_MAP:
            if tok == "ALL":
                tags.append("(ALL)")
            continue
        if tok:
            tags.append(f"({tok})")
    return list(dict.fromkeys(tags))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="project root")
    ap.add_argument("--tokv1", default="", help="cards_min_tokv1.json path; default auto-detect")
    ap.add_argument("--outdir", default="./loveca_reports")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    tokv1 = Path(args.tokv1) if args.tokv1 else root / "llocg_db_out_full" / "cards_min_tokv1.json"
    if not tokv1.exists():
        tokv1 = root / "cards_min_tokv1.json"
    if not tokv1.exists():
        raise SystemExit(f"cards_min_tokv1.json not found: {tokv1}")

    # Ensure local package import works both from project root and from tools/.
    sys.path.insert(0, str(root))
    from llocg_ui.db import load_cards_db, _get_card  # type: ignore

    raw_cards = read_json(tokv1)
    if isinstance(raw_cards, dict) and "cards" in raw_cards:
        raw_cards = raw_cards["cards"]
    if not isinstance(raw_cards, list):
        raise SystemExit("tokv1 JSON is not a card list")

    cards_db = load_cards_db(root, tokv1_path=tokv1)

    rows: List[Dict[str, Any]] = []
    summary = {
        "cards_total": len(raw_cards),
        "raw_required_rows": 0,
        "defect_required_counts_blank": 0,
        "runtime_required_still_blank": 0,
        "raw_base_rows": 0,
        "defect_base_counts_blank": 0,
        "runtime_base_still_blank": 0,
        "raw_blade_heart_rows": 0,
        "defect_blade_heart_counts_blank": 0,
        "runtime_blade_heart_still_blank": 0,
        "defect_blade_heart_tags_blank": 0,
        "runtime_blade_heart_tags_still_blank": 0,
    }

    field_defs = [
        ("required", "required_hearts_raw", "required_hearts_counts_json", "required_hearts"),
        ("base", "base_hearts_raw", "base_hearts_counts_json", "base_hearts"),
        ("blade_heart", "blade_heart_raw", "blade_heart_counts_json", "blade_hearts"),
    ]

    for r in raw_cards:
        if not isinstance(r, dict):
            continue
        cn = str(r.get("cardnumber", "") or "").strip()
        ci = _get_card(cards_db, cn)
        ctype = str(r.get("card_type_norm", "") or r.get("card_type_raw", "") or "")
        for label, raw_field, count_field, attr in field_defs:
            rc = raw_counts(str(r.get(raw_field, "") or ""))
            if rc:
                summary[f"raw_{label}_rows"] += 1
                stored = jdict(r.get(count_field, "{}"))
                runtime = getattr(ci, attr, {}) if ci else {}
                stored_blank = not any(int(v or 0) > 0 for v in stored.values())
                runtime_blank = not any(int(v or 0) > 0 for v in (runtime or {}).values())
                if stored_blank:
                    summary[f"defect_{label}_counts_blank"] += 1
                if runtime_blank:
                    summary[f"runtime_{label}_still_blank"] += 1
                if stored_blank or runtime_blank:
                    rows.append({
                        "cardnumber": cn,
                        "cardname": r.get("cardname", ""),
                        "card_type": ctype,
                        "field": label,
                        "raw": r.get(raw_field, ""),
                        "raw_parsed": json.dumps(rc, ensure_ascii=False, sort_keys=True),
                        "stored_counts": json.dumps(stored, ensure_ascii=False, sort_keys=True),
                        "runtime_counts": json.dumps(runtime or {}, ensure_ascii=False, sort_keys=True),
                        "stored_blank": int(stored_blank),
                        "runtime_blank_after_patch": int(runtime_blank),
                    })
            if label == "blade_heart":
                rt = raw_tags(str(r.get(raw_field, "") or ""))
                if rt:
                    stored_tags = jlist(r.get("blade_heart_tags_json", "[]"))
                    runtime_tags = jlist(getattr(ci, "blade_heart_tags_json", "[]") if ci else "[]")
                    stored_tag_blank = not stored_tags
                    runtime_tag_blank = not runtime_tags
                    if stored_tag_blank:
                        summary["defect_blade_heart_tags_blank"] += 1
                    if runtime_tag_blank:
                        summary["runtime_blade_heart_tags_still_blank"] += 1
                    if stored_tag_blank or runtime_tag_blank:
                        rows.append({
                            "cardnumber": cn,
                            "cardname": r.get("cardname", ""),
                            "card_type": ctype,
                            "field": "blade_heart_tags",
                            "raw": r.get(raw_field, ""),
                            "raw_parsed": json.dumps(rt, ensure_ascii=False),
                            "stored_counts": json.dumps(stored_tags, ensure_ascii=False),
                            "runtime_counts": json.dumps(runtime_tags, ensure_ascii=False),
                            "stored_blank": int(stored_tag_blank),
                            "runtime_blank_after_patch": int(runtime_tag_blank),
                        })

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "loveca_card_stat_icon_audit_20260604a.csv"
    md_path = outdir / "loveca_card_stat_icon_audit_20260604a.md"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        cols = ["cardnumber","cardname","card_type","field","raw","raw_parsed","stored_counts","runtime_counts","stored_blank","runtime_blank_after_patch"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    lines = []
    lines.append("# Loveca card stat icon audit 20260604a")
    lines.append("")
    lines.append(f"tokv1: `{tokv1}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for k in sorted(summary):
        lines.append(f"- `{k}`: {summary[k]}")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- `stored_*_blank` means the DB's normalized columns are blank despite parseable raw icon text.")
    lines.append("- `runtime_*_still_blank` should be 0 after `db_parse_raw_heart_icons_20260604a`.")
    lines.append("- This audit checks required hearts, member base hearts, blade-heart colors, and blade-heart non-color tags such as `<ドロー+1>` / `<スコア+1>`.")
    lines.append("")
    lines.append("## First rows")
    lines.append("")
    lines.append("| cardnumber | cardname | field | raw | runtime_blank_after_patch |")
    lines.append("|---|---|---|---|---:|")
    for row in rows[:40]:
        raw = str(row.get("raw", "")).replace("|", "｜")
        lines.append(f"| {row['cardnumber']} | {row['cardname']} | {row['field']} | {raw} | {row['runtime_blank_after_patch']} |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] wrote: {csv_path}")
    print(f"[OK] wrote: {md_path}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if any(v for k, v in summary.items() if k.startswith("runtime_") and k.endswith("still_blank")):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
