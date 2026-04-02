#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUILD_TAG: fix_temp_blade_live_end_patcher_20260402a

Patch engine_effect.py in place to fix temporary blade bonuses that should expire
at live end but persist because slot.temp_until is not set.

Targets:
- live_start_success_zone_count_x2_blade
- live_start_live_cards_count_x1_blade
- live_start_all_stage_filled_x2_blade

Usage:
  python3 patch_engine_effect_temp_blade_live_end.py

Run this from the project root (e.g. /Users/tekitou/Desktop/gsim/loveca), or place
the script there and execute it. The script will:
1) inspect llocg_ui/engine.py to guess the temp_until token used by the live-end clear logic
2) patch llocg_ui/engine_effect.py in place
3) save a backup under ./jank/
4) run py_compile on the patched file
"""
from __future__ import annotations

import datetime as _dt
import os
import py_compile
import re
import shutil
import sys
from pathlib import Path


TARGET_EXT_KEYS = [
    "live_start_success_zone_count_x2_blade",
    "live_start_live_cards_count_x1_blade",
    "live_start_all_stage_filled_x2_blade",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="")


def _guess_root() -> Path:
    cwd = Path.cwd()
    if (cwd / "llocg_ui" / "engine_effect.py").exists():
        return cwd
    if (cwd / "loveca" / "llocg_ui" / "engine_effect.py").exists():
        return cwd / "loveca"
    # fallback: script location
    here = Path(__file__).resolve().parent
    if (here / "llocg_ui" / "engine_effect.py").exists():
        return here
    if (here / "loveca" / "llocg_ui" / "engine_effect.py").exists():
        return here / "loveca"
    raise FileNotFoundError(
        "Could not find llocg_ui/engine_effect.py. Run this from the loveca root."
    )


def _infer_temp_until_value(engine_text: str) -> str:
    """
    Try to infer the sentinel value used by engine.py to clear temporary live-end modifiers.
    Defaults to 'live_end' if nothing explicit is found.
    """
    # Strong signals first: temp_until compared against literal strings containing live/end.
    candidates = []
    patterns = [
        r'temp_until\s*==\s*[\'"]([^\'"]+)[\'"]',
        r'temp_until\s*in\s*\((.*?)\)',
        r'getattr\([^)]*temp_until[^)]*,\s*[\'"]([^\'"]+)[\'"]\)',
    ]
    for pat in patterns:
        for m in re.finditer(pat, engine_text, flags=re.DOTALL):
            g = m.group(1)
            if pat.endswith(r'\((.*?)\)'):
                for s in re.findall(r'[\'"]([^\'"]+)[\'"]', g):
                    candidates.append(s)
            else:
                candidates.append(g)

    ranked = []
    for s in candidates:
        low = s.lower()
        score = 0
        if "live" in low:
            score += 3
        if "end" in low:
            score += 2
        if "turn" in low:
            score -= 2
        if low in {"live_end", "end_of_live", "until_live_end"}:
            score += 10
        ranked.append((score, s))
    ranked.sort(reverse=True)

    if ranked and ranked[0][0] > 0:
        return ranked[0][1]

    # Fallback: any explicit assignment nearby mentioning live and end.
    for m in re.finditer(r'temp_until\s*=\s*[\'"]([^\'"]+)[\'"]', engine_text):
        s = m.group(1)
        low = s.lower()
        if "live" in low and "end" in low:
            return s

    return "live_end"


def _patch_block(block: str, token: str) -> tuple[str, int]:
    """
    Insert slot.temp_until assignment after _add_temp_blade(...) inside a block,
    unless already present close by.
    """
    changed = 0
    lines = block.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if "_add_temp_blade(" in line:
            # Look ahead a few lines to avoid double insertion.
            nearby = "".join(lines[i + 1 : i + 6])
            if "temp_until" not in nearby:
                indent = re.match(r"(\s*)", line).group(1)
                out.append(f"{indent}try:\n")
                out.append(f"{indent}    slot.temp_until = {token!r}\n")
                out.append(f"{indent}except Exception:\n")
                out.append(f"{indent}    pass\n")
                changed += 1
        i += 1
    return "".join(out), changed


def _patch_ext_key_block(text: str, ext_key: str, token: str) -> tuple[str, int]:
    """
    Patch the logical block that contains the ext_key. We conservatively patch from the
    ext_key occurrence until the next top-level 'elif/if ext_key' line, or EOF.
    """
    # matches if/elif ext_key == "..." or ext_key in (...)
    key_pat = re.compile(
        rf'(^[ \t]*(?:if|elif)\b[^\n]*\b{re.escape(ext_key)}\b[^\n]*:\n)',
        flags=re.MULTILINE,
    )
    m = key_pat.search(text)
    if not m:
        # fallback: plain string occurrence
        idx = text.find(ext_key)
        if idx < 0:
            return text, 0
        start = text.rfind("\n", 0, idx) + 1
    else:
        start = m.start()

    next_pat = re.compile(r'^[ \t]*(?:if|elif)\b[^\n]*ext_key[^\n]*:\n', flags=re.MULTILINE)
    m2 = next_pat.search(text, start + 1)
    end = m2.start() if m2 else len(text)

    block = text[start:end]
    new_block, changed = _patch_block(block, token)
    if changed == 0:
        return text, 0
    return text[:start] + new_block + text[end:], changed


def main() -> int:
    root = _guess_root()
    engine_effect = root / "llocg_ui" / "engine_effect.py"
    engine = root / "llocg_ui" / "engine.py"

    src = _read_text(engine_effect)
    engine_text = _read_text(engine) if engine.exists() else ""
    token = _infer_temp_until_value(engine_text)

    patched = src
    total_changes = 0
    per_key = {}

    for ext_key in TARGET_EXT_KEYS:
        patched, n = _patch_ext_key_block(patched, ext_key, token)
        per_key[ext_key] = n
        total_changes += n

    if total_changes == 0:
        print("[INFO] No patch inserted.")
        print("[INFO] Either target ext_keys were not found, or temp_until was already present.")
        for k, n in per_key.items():
            print(f"  - {k}: {n}")
        return 0

    jank = root / "jank"
    jank.mkdir(parents=True, exist_ok=True)
    ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = jank / f"engine_effect.py.bak_{ts}"
    shutil.copy2(engine_effect, backup)

    _write_text(engine_effect, patched)
    py_compile.compile(str(engine_effect), doraise=True)

    print(f"[OK] patched: {engine_effect}")
    print(f"[OK] backup : {backup}")
    print(f"[OK] temp_until token inferred: {token!r}")
    for k, n in per_key.items():
        print(f"  - {k}: inserted after _add_temp_blade x {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
