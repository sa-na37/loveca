#!/usr/bin/env python3
# BUILD_TAG = "autoplay_trace_cli_20260803a"
"""Write human-readable autoplay policy reports for model deck testing."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from loveca_app.autoplay import build_autoplay_markdown_report
from loveca_app.core import AppState


BUILD_TAG = "autoplay_trace_cli_20260803a"


COMPARE_METRIC_SUFFIXES = (
    "_hit",
    "_cumulative",
    "_live",
    "_live_cumulative",
    "_combined_cumulative",
    "_avg_stage_cost",
)


def safe_name(value: str) -> str:
    out = "".join(ch if ch.isascii() and ch.isalnum() else "_" for ch in value)
    return "_".join(part for part in out.split("_") if part)[:80] or "deck"


def resolve_output_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else (root / path).resolve()


def metric_at(values: object, index: int) -> object:
    if isinstance(values, list) and 0 <= index < len(values):
        return values[index]
    return ""


def top_miss_reason(values: object, index: int) -> str:
    if not isinstance(values, list) or index >= len(values):
        return ""
    reasons = values[index]
    if not isinstance(reasons, list) or not reasons:
        return ""
    first = reasons[0]
    if not isinstance(first, dict):
        return ""
    return "{} {} ({})".format(first.get("reason", ""), first.get("count", ""), first.get("rate", ""))


def summary_row(deck_path: str, report: dict, trial_result: dict | None, max_turns: int) -> dict[str, object]:
    rec = report.get("recommended_progression") if isinstance(report.get("recommended_progression"), dict) else {}
    validation = report.get("validation") if isinstance(report.get("validation"), dict) else {}
    row: dict[str, object] = {
        "deck_path": deck_path,
        "deck_name": report.get("deck_name", ""),
        "valid": bool(validation.get("valid")),
        "playable": bool(validation.get("playable")),
        "validation_error": validation.get("error", ""),
        "recommended": rec.get("label", ""),
        "recommended_score": rec.get("score", ""),
        "trials": trial_result.get("trials", "") if trial_result else "",
        "seed": trial_result.get("seed", "") if trial_result else "",
        "max_turns": max_turns,
    }
    if trial_result:
        for index in range(max_turns):
            turn = index + 1
            targets = metric_at(trial_result.get("target_turns"), index)
            if isinstance(targets, list):
                target_text = "-".join(str(value) for value in targets)
            else:
                target_text = str(targets or "")
            row[f"t{turn}_target"] = target_text
            row[f"t{turn}_hit"] = metric_at(trial_result.get("turn_hit_rates"), index)
            row[f"t{turn}_cumulative"] = metric_at(trial_result.get("cumulative_hit_rates"), index)
            row[f"t{turn}_live"] = metric_at(trial_result.get("live_score_hit_rates"), index)
            row[f"t{turn}_live_cumulative"] = metric_at(trial_result.get("live_score_cumulative_hit_rates"), index)
            row[f"t{turn}_combined_cumulative"] = metric_at(trial_result.get("combined_cumulative_hit_rates"), index)
            row[f"t{turn}_avg_stage_cost"] = metric_at(trial_result.get("average_stage_costs"), index)
            row[f"t{turn}_top_miss"] = top_miss_reason(trial_result.get("miss_reasons"), index)
    return row


def metric_float(row: dict[str, object], key: str) -> float | None:
    value = row.get(key)
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def row_identity(row: dict[str, object]) -> str:
    deck_path = str(row.get("deck_path") or "").strip()
    if deck_path:
        return deck_path
    return str(row.get("deck_name") or "").strip()


def load_summary_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"ERROR: comparison summary not found: {path}")
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise SystemExit(f"ERROR: comparison JSON must be a list: {path}")
        return [dict(row) for row in data if isinstance(row, dict)]
    with path.open("r", encoding="utf-8", newline="") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def compare_summary_rows(before_rows: list[dict[str, object]], after_rows: list[dict[str, object]], max_turns: int) -> list[dict[str, object]]:
    before_by_id = {row_identity(row): row for row in before_rows if row_identity(row)}
    out: list[dict[str, object]] = []
    metric_keys = [
        f"t{turn}{suffix}"
        for turn in range(1, max_turns + 1)
        for suffix in COMPARE_METRIC_SUFFIXES
    ]
    for after in after_rows:
        identity = row_identity(after)
        before = before_by_id.get(identity)
        row: dict[str, object] = {
            "deck_path": after.get("deck_path", ""),
            "deck_name": after.get("deck_name", ""),
            "before_found": bool(before),
            "recommended_before": before.get("recommended", "") if before else "",
            "recommended_after": after.get("recommended", ""),
        }
        changed = False
        for key in metric_keys:
            before_value = metric_float(before, key) if before else None
            after_value = metric_float(after, key)
            if after_value is None:
                continue
            delta = "" if before_value is None else round(after_value - before_value, 4)
            row[f"{key}_before"] = "" if before_value is None else before_value
            row[f"{key}_after"] = after_value
            row[f"{key}_delta"] = delta
            if isinstance(delta, float) and abs(delta) > 0.00001:
                changed = True
        for turn in range(1, max_turns + 1):
            key = f"t{turn}_top_miss"
            row[f"{key}_before"] = before.get(key, "") if before else ""
            row[f"{key}_after"] = after.get(key, "")
        row["any_metric_changed"] = changed
        out.append(row)
    return out


def write_compare_markdown(path: Path, compare_rows: list[dict[str, object]], max_turns: int) -> None:
    lines = [
        "# Loveca Autoplay Comparison",
        "",
        "同じデッキ、seed、試行回数で出したサマリ同士の差分です。",
        "主に見る値は `combined_cumulative_delta` と `cumulative_delta` です。",
        "",
        "| Deck | Metric | Before | After | Delta |",
        "|---|---:|---:|---:|---:|",
    ]
    priority_suffixes = ("_combined_cumulative", "_cumulative", "_live_cumulative", "_avg_stage_cost")
    for row in compare_rows:
        deck = str(row.get("deck_name") or row.get("deck_path") or "")
        for turn in range(1, max_turns + 1):
            for suffix in priority_suffixes:
                key = f"t{turn}{suffix}"
                delta = row.get(f"{key}_delta", "")
                if delta == "":
                    continue
                before = row.get(f"{key}_before", "")
                after = row.get(f"{key}_after", "")
                lines.append(f"| {deck} | {key} | {before} | {after} | {delta} |")
    if len(lines) == 6:
        lines.append("| 変更なし | - | - | - | - |")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Loveca autoplay policy markdown reports")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--deck", action="append", default=[], help="Deck path relative to project root")
    parser.add_argument("--all", action="store_true", help="Generate reports for every playable deck")
    parser.add_argument("--recent", type=int, default=0, help="Generate reports for the N most recently modified playable decks")
    parser.add_argument("--trials", type=int, default=0, help="Run heuristic autoplay trials and include the result")
    parser.add_argument("--trace-trials", type=int, default=0, help="Include detailed human-readable decision traces for the first N trials")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--turns", type=int, default=4)
    parser.add_argument("--outdir", type=Path, default=Path("docs/reports/autoplay"))
    parser.add_argument("--no-markdown", action="store_true", help="Skip per-deck markdown files and only write summary outputs")
    parser.add_argument("--summary-csv", type=Path, default=Path("docs/reports/autoplay/autoplay_summary.csv"))
    parser.add_argument("--summary-json", type=Path, default=Path("docs/reports/autoplay/autoplay_summary.json"))
    parser.add_argument("--compare-json", type=Path, default=None, help="Previous summary JSON/CSV to compare against")
    parser.add_argument("--compare-csv", type=Path, default=Path("docs/reports/autoplay/autoplay_compare.csv"))
    parser.add_argument("--compare-md", type=Path, default=Path("docs/reports/autoplay/autoplay_compare.md"))
    args = parser.parse_args()

    app = AppState(args.root)
    deck_paths = list(dict.fromkeys(str(path) for path in args.deck if str(path).strip()))
    if args.all:
        for deck in app.list_decks():
            if deck.get("playable", deck.get("valid")):
                deck_paths.append(str(deck.get("path") or ""))
    if args.recent > 0:
        recent = sorted([
            deck for deck in app.list_decks()
            if deck.get("playable", deck.get("valid"))
        ], key=lambda deck: str(deck.get("modified") or ""), reverse=True)[:args.recent]
        deck_paths.extend(str(deck.get("path") or "") for deck in recent)
    deck_paths = list(dict.fromkeys(path for path in deck_paths if path))
    if not deck_paths:
        raise SystemExit("ERROR: specify --deck or --all")

    outdir = resolve_output_path(args.root, args.outdir)
    if not args.no_markdown:
        outdir.mkdir(parents=True, exist_ok=True)
    summary_rows: list[dict[str, object]] = []
    for deck_path in deck_paths:
        report = app.autoplay_deck_report(deck_path)
        trial_result = None
        max_turns = max(1, int(args.turns or 4))
        if int(args.trials or 0) > 0:
            trial_result = app.autoplay_trial_report(
                deck_path,
                trials=max(0, int(args.trials or 0)),
                seed=int(args.seed),
                max_turns=max_turns,
                trace_trials=max(0, int(args.trace_trials or 0)),
            )
        summary_rows.append(summary_row(deck_path, report, trial_result, max_turns))
        if not args.no_markdown:
            text = build_autoplay_markdown_report(report, trial_result)
            deck_token = safe_name(Path(deck_path).stem)
            name_token = safe_name(str(report.get("deck_name") or Path(deck_path).stem))
            filename = f"{name_token}_{deck_token}.md"
            target = outdir / filename
            target.write_text(text, encoding="utf-8")
            print(f"[AUTOPLAY-REPORT] {deck_path} -> {target}")
    summary_csv = resolve_output_path(args.root, args.summary_csv)
    summary_json = resolve_output_path(args.root, args.summary_json)
    summary_csv.parent.mkdir(parents=True, exist_ok=True)
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(key for row in summary_rows for key in row.keys()))
    with summary_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    summary_json.write_text(json.dumps(summary_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[AUTOPLAY-SUMMARY] csv -> {summary_csv}")
    print(f"[AUTOPLAY-SUMMARY] json -> {summary_json}")
    if args.compare_json is not None:
        before_rows = load_summary_rows(resolve_output_path(args.root, args.compare_json))
        compare_rows = compare_summary_rows(before_rows, summary_rows, max(1, int(args.turns or 4)))
        compare_csv = resolve_output_path(args.root, args.compare_csv)
        compare_md = resolve_output_path(args.root, args.compare_md)
        compare_csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(dict.fromkeys(key for row in compare_rows for key in row.keys()))
        with compare_csv.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(compare_rows)
        write_compare_markdown(compare_md, compare_rows, max(1, int(args.turns or 4)))
        print(f"[AUTOPLAY-COMPARE] csv -> {compare_csv}")
        print(f"[AUTOPLAY-COMPARE] md -> {compare_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
