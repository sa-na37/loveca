#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


DEFAULT_NOISE_KEYS = {
    "log",
    "banner",
    "root",
    "code",
    "deck_code",
    "debug",
    "cn2name",
    "cn2label",
    "cn2type",
    "cn2is_live",
    "cn2yell_hearts",
    "cn2yell_draw_icons",
    "cn2yell_score_icons",
    "cn2group",
    "cn2unit",
    "cn2cost",
    "cn2score",
    "public_reveal_events",
    "public_hand_reveal_events",
    "public_hand_revealed_cards",
    "public_hand_revealed_orient",
    "refresh_notices",
    "refresh_notice_seq",
    "refresh_notice_ack_seq",
}

ORDERLESS_KEYS = {
    "used_this_turn",
    "once_used",
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"failed to read JSON {path}: {exc}") from exc


def normalize(obj: Any, noise_keys: set[str], path: str = "") -> Any:
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for key, value in obj.items():
            if str(key) in noise_keys:
                continue
            out[str(key)] = normalize(value, noise_keys, f"{path}.{key}" if path else str(key))
        return out
    if isinstance(obj, list):
        items = [normalize(x, noise_keys, f"{path}[]") for x in obj]
        key = path.split(".")[-1]
        if key in ORDERLESS_KEYS:
            return sorted(items, key=lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True))
        return items
    return obj


def compare(a: Any, b: Any, path: str = "$") -> List[Dict[str, Any]]:
    diffs: List[Dict[str, Any]] = []
    if type(a) is not type(b):
        return [{"path": path, "kind": "type", "left": type(a).__name__, "right": type(b).__name__}]
    if isinstance(a, dict):
        keys = sorted(set(a.keys()) | set(b.keys()))
        for key in keys:
            if key not in a:
                diffs.append({"path": f"{path}.{key}", "kind": "missing_left", "right": b[key]})
            elif key not in b:
                diffs.append({"path": f"{path}.{key}", "kind": "missing_right", "left": a[key]})
            else:
                diffs.extend(compare(a[key], b[key], f"{path}.{key}"))
        return diffs
    if isinstance(a, list):
        if len(a) != len(b):
            diffs.append({"path": path, "kind": "list_length", "left": len(a), "right": len(b)})
        for i, (av, bv) in enumerate(zip(a, b)):
            diffs.extend(compare(av, bv, f"{path}[{i}]"))
        return diffs
    if a != b:
        return [{"path": path, "kind": "value", "left": a, "right": b}]
    return diffs


def write_markdown(path: Path, left: Path, right: Path, diffs: List[Dict[str, Any]], noise_keys: List[str]) -> None:
    lines = [
        "# Undo State Comparison",
        "",
        f"- left: `{left}`",
        f"- right: `{right}`",
        f"- equal: `{not diffs}`",
        f"- difference_count: `{len(diffs)}`",
        f"- noise_keys: `{', '.join(noise_keys)}`",
        "",
    ]
    if diffs:
        lines.append("## Differences")
        lines.append("")
        for d in diffs[:200]:
            lines.append(f"- `{d.get('path')}` {d.get('kind')}: left=`{json.dumps(d.get('left'), ensure_ascii=False)}` right=`{json.dumps(d.get('right'), ensure_ascii=False)}`")
        if len(diffs) > 200:
            lines.append(f"- ... truncated {len(diffs) - 200} additional differences")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("left")
    ap.add_argument("right")
    ap.add_argument("--json-out", required=True)
    ap.add_argument("--md-out", required=True)
    ap.add_argument("--noise-key", action="append", default=[])
    args = ap.parse_args()

    left = Path(args.left)
    right = Path(args.right)
    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    noise_keys = sorted(DEFAULT_NOISE_KEYS | set(args.noise_key or []))

    try:
        a = normalize(load_json(left), set(noise_keys))
        b = normalize(load_json(right), set(noise_keys))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    diffs = compare(a, b)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps({
        "left": str(left),
        "right": str(right),
        "equal": not diffs,
        "difference_count": len(diffs),
        "noise_keys": noise_keys,
        "differences": diffs,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md_out, left, right, diffs, noise_keys)
    return 0 if not diffs else 1


if __name__ == "__main__":
    raise SystemExit(main())
