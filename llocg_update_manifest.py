#!/usr/bin/env python3
"""
LLCG project manifest/runlog updater.

Creates/updates:
  - <root>/_MANIFEST.json
  - <root>/_RUNLOG.md

Usage:
  python3 llocg_update_manifest.py --root /Users/tekitou/Desktop/gsim/loveca/llocg_db_out_full
  # If omitted, root defaults to ./llocg_db_out_full relative to current working dir.
"""
from __future__ import annotations
from pathlib import Path
import argparse, json, re, datetime, hashlib

VERSION_RE = re.compile(r"cards_compiled_v(\d+)([a-z]*)\.json$", re.IGNORECASE)

def _now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def _sha1(path: Path, max_bytes: int = 2_000_000) -> str:
    """Compute sha1 of up to max_bytes to keep it fast for large files."""
    h = hashlib.sha1()
    with path.open("rb") as f:
        remaining = max_bytes
        while remaining > 0:
            chunk = f.read(min(65536, remaining))
            if not chunk:
                break
            h.update(chunk)
            remaining -= len(chunk)
    return h.hexdigest()

def _safe_stat(p: Path):
    st = p.stat()
    return {
        "path": str(p),
        "size_bytes": int(st.st_size),
        "mtime": datetime.datetime.fromtimestamp(st.st_mtime).astimezone().isoformat(timespec="seconds"),
    }

def _parse_compiled_version(p: Path):
    m = VERSION_RE.search(p.name)
    if not m:
        return None
    vnum = int(m.group(1))
    suffix = (m.group(2) or "").lower()
    return (vnum, suffix)

def _is_valid_compiled_json(p: Path) -> tuple[bool, str]:
    """Minimal validity: JSON root is list and elements are dict (sampled)."""
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return (False, f"json_parse_error:{e.__class__.__name__}")
    if not isinstance(data, list):
        return (False, "root_not_list")
    if len(data) == 0:
        return (False, "empty_list")
    bad = 0
    for x in data[:2000]:
        if not isinstance(x, dict):
            bad += 1
            if bad >= 5:
                return (False, "contains_non_dict")
    return (True, "ok")

def _find_compiled_candidates(root: Path):
    cands = []
    for p in root.glob("cards_compiled_v*.json"):
        ver = _parse_compiled_version(p)
        if ver is None:
            continue
        ok, reason = _is_valid_compiled_json(p)
        cands.append({
            "path": str(p),
            "version_num": ver[0],
            "version_suffix": ver[1],
            "valid": bool(ok),
            "valid_reason": reason,
            "stat": _safe_stat(p),
            "sha1_prefix": _sha1(p)[:12],
        })
    cands.sort(key=lambda d: (d["version_num"], d["version_suffix"]))
    return cands

def _choose_latest_valid_compiled(cands):
    valids = [c for c in cands if c["valid"]]
    if not valids:
        return None
    return max(valids, key=lambda d: (d["version_num"], d["version_suffix"]))

def _list_patterns(patterns_dir: Path):
    if not patterns_dir.exists():
        return {"exists": False, "files": []}
    files = []
    for p in sorted(patterns_dir.rglob("*.yaml")):
        files.append({
            "path": str(p),
            "stat": _safe_stat(p),
            "sha1_prefix": _sha1(p)[:12],
        })
    return {"exists": True, "files": files}

def _maybe_file(root: Path, rel: str):
    p = root / rel
    if p.exists():
        return {"exists": True, **_safe_stat(p), "sha1_prefix": _sha1(p)[:12]}
    return {"exists": False, "path": str(p)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="llocg_db_out_full", help="Artifact root directory.")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"[ERROR] root not found: {root}")

    patterns_dir = root / "patterns"
    sim_out_dir = root / "sim_out"

    cands = _find_compiled_candidates(root)
    latest = _choose_latest_valid_compiled(cands)

    manifest = {
        "schema": "llocg_manifest_v1",
        "generated_at": _now_iso(),
        "root": str(root),
        "directories": {
            "patterns": str(patterns_dir),
            "sim_out": str(sim_out_dir),
        },
        "inputs": {
            "cards_min_tokv1_csv": _maybe_file(root, "cards_min_tokv1.csv"),
        },
        "compiled_db": {
            "candidates": cands,
            "latest_valid": latest,
            "selection_rule": (
                "Scan <root>/cards_compiled_v*.json. Keep files where JSON root is list and elements are dict. "
                "Choose max by (version_num, version_suffix) where suffix is '' or [a-z]*."
            ),
        },
        "patterns": _list_patterns(patterns_dir),
        "sim_outputs": {
            "sim_out_exists": sim_out_dir.exists(),
            "expected_files": [
                str(sim_out_dir / "sim_raw_turn_snapshots.csv"),
                str(sim_out_dir / "sim_success_by_state.csv"),
            ],
        },
        "conventions": {
            "artifact_root_policy": "All generated artifacts live under <root> (llocg_db_out_full).",
            "auto_discovery_policy": "Scripts should auto-discover prior artifacts; explicit paths are minimized.",
            "filename_suffix_policy": "Output filenames include config suffixes to avoid collisions.",
        },
        "notes": {
            "rule_pdf": "LLCrule251121.pdf ver1.04 2025-11-21 (stored at project root, not necessarily under <root>).",
            "simulation_expected_logic": [
                "Members: each turn, play to maximize total played cost.",
                "Live set: choose LIVE cards with required_hearts <= stats (hearts+blades on stage) and maximize total required hearts under stats. "
                "If fewer than 3 set cards, add members (lowest cost first, temporary) until total set cards (LIVE+MEMBER) == 3.",
                "Challenge: attempt all set LIVE cards (not just one).",
                "Yell: reveal top deck cards equal to total blades; add blade-hearts from revealed cards; draw extra cards for draw-icon count.",
                "ALL: at success-check start, choose one required color and reduce its requirement by 1.",
            ],
        },
    }

    man_path = root / "_MANIFEST.json"
    man_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    runlog_lines = []
    runlog_lines.append("# LLCG Project Runlog")
    runlog_lines.append(f"- Generated at: {manifest['generated_at']}")
    runlog_lines.append(f"- Root: `{root}`")
    runlog_lines.append("")
    runlog_lines.append("## Key artifacts")
    runlog_lines.append(f"- cards_min_tokv1.csv: `{manifest['inputs']['cards_min_tokv1_csv']['path']}` "
                        f"(exists={manifest['inputs']['cards_min_tokv1_csv']['exists']})")
    runlog_lines.append(f"- patterns dir: `{patterns_dir}` (exists={patterns_dir.exists()})")
    runlog_lines.append(f"- sim_out dir: `{sim_out_dir}` (exists={sim_out_dir.exists()})")
    runlog_lines.append("")
    runlog_lines.append("## Compiled DB selection")
    runlog_lines.append(f"- Candidates found: {len(cands)}")
    if latest:
        runlog_lines.append(f"- Latest valid: `{latest['path']}` (v{latest['version_num']}{latest['version_suffix']})")
    else:
        runlog_lines.append("- Latest valid: (none)  ← compiled JSON validity failed; check candidates in _MANIFEST.json")
    runlog_lines.append("")
    runlog_lines.append("## Auto-discovery rules (contract)")
    runlog_lines.append("- Prefer auto-discovery; minimize explicit paths.")
    runlog_lines.append("- Compiled DB: choose latest valid cards_compiled_v*.json by (version_num, suffix).")
    runlog_lines.append("- Outputs: include config suffixes to avoid collisions.")
    runlog_lines.append("")
    runlog_lines.append("## Next actions (per spec)")
    runlog_lines.append("1) Confirm rules for 8.3.10–8.3.15 (Yell / performance step).")
    runlog_lines.append("2) Rebuild simulator core to match expected logic (members cost-max, live selection, yell draw-icon, ALL).")
    runlog_lines.append("3) Keep outputs under <root>/sim_out/ with config suffixes.")
    runlog_lines.append("")
    (root / "_RUNLOG.md").write_text("\n".join(runlog_lines) + "\n", encoding="utf-8")

    print("[OK] Wrote:")
    print(f"  {man_path}")
    print(f"  {root / '_RUNLOG.md'}")
    if latest:
        print(f"[OK] Latest valid compiled: {latest['path']}")

if __name__ == "__main__":
    main()
