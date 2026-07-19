#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: tier3_pilot3_submission_preflight_20260717a
from __future__ import annotations

import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "_codex_outputs" / "effect_full_audit_tier3_pilot3_complete_gate_20260717"
FORBIDDEN = [
    "condition_satisfied = True", "state/log route change", "prepare the exact named",
    "apply the numeric", "depending on text", "likely", "TODO", "TBD",
]
REQUIRED = [
    "README.md", "pilot3_methodology.md", "pilot3_selection.md", "pilot3_setup_design.csv",
    "pilot3_setup_card_validation.csv", "pilot3_route_mapping.csv", "pilot3_results.csv",
    "validation/design_validation.txt", "validation/result_validation.txt",
    "tools/validate_pilot3_design.py", "tools/run_tier3_pilot3_complete.py",
    "tools/validate_pilot3_results.py", "tools/preflight_pilot3_submission.py",
    "git/status.txt", "git/diff_stat.txt",
]


def main() -> int:
    errors = []
    for rel in REQUIRED:
        if not (OUT / rel).exists():
            errors.append(f"missing:{rel}")
    for rel in ["validation/design_validation.txt", "validation/result_validation.txt"]:
        p = OUT / rel
        if p.exists() and p.read_text(encoding="utf-8").strip() != "PASS":
            errors.append(f"validation_not_pass:{rel}")
    rows = list(csv.DictReader((OUT / "pilot3_results.csv").open(encoding="utf-8"))) if (OUT / "pilot3_results.csv").exists() else []
    if len(rows) != 3:
        errors.append(f"result_rows={len(rows)}")
    if rows:
        browser_rows = [r for r in rows if r["ui_required"] == "true"]
        if sum(r["browser_checked"] == "true" and r["browser_passed"] == "true" for r in browser_rows) < 2:
            errors.append("browser_passed_less_than_2")
        for r in rows:
            if any(not str(v).strip() for v in r.values()):
                errors.append(f"{r.get('canonical_id')}:blank_result_cell")
            ev = OUT / r["evidence"]
            if not ev.exists():
                errors.append(f"{r.get('canonical_id')}:evidence_dir_missing")
    setup = list(csv.DictReader((OUT / "pilot3_setup_design.csv").open(encoding="utf-8"))) if (OUT / "pilot3_setup_design.csv").exists() else []
    if len(setup) != 3:
        errors.append(f"setup_rows={len(setup)}")
    for r in setup:
        if any(not str(v).strip() for v in r.values()):
            errors.append(f"{r.get('canonical_id')}:blank_setup_cell")
    blob = ""
    for p in OUT.rglob("*"):
        if "tools" in p.parts or "validation" in p.parts:
            continue
        if p.is_file() and p.suffix in {".csv", ".md", ".txt", ".json"}:
            blob += p.read_text(encoding="utf-8", errors="ignore")
    for word in FORBIDDEN:
        if word in blob:
            errors.append(f"forbidden:{word}")
    pngs = sorted((OUT / "evidence").glob("*/browser/*.png"))
    if len(pngs) < 10:
        errors.append(f"browser_png_count={len(pngs)}")
    hashes = {}
    for p in pngs:
        data = p.read_bytes()
        if len(data) < 5000 or len(set(data[:20000])) < 16:
            errors.append(f"blank_or_small_png:{p.relative_to(OUT)}")
        h = hashlib.sha256(data).hexdigest()
        if h in hashes:
            errors.append(f"duplicate_png:{p.relative_to(OUT)} and {hashes[h]}")
        hashes[h] = str(p.relative_to(OUT))
    out = OUT / "validation" / "submission_preflight.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    if errors:
        out.write_text("FAIL\n" + "\n".join(errors) + "\n", encoding="utf-8")
        print(out.read_text(encoding="utf-8"))
        return 1
    out.write_text("PASS\n", encoding="utf-8")
    zip_path = OUT.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(OUT.rglob("*")):
            if "__pycache__" in p.parts or p.suffix == ".pyc":
                continue
            if p.is_file():
                zf.write(p, p.relative_to(OUT.parent))
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
