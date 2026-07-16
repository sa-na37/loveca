#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

BUILD_TAG = "llocg_fetch_decklog_by_code_20260715a"
CARD_RE = re.compile(r"\b(PL![A-Za-z0-9]+-[A-Za-z0-9]+-\d{3})\b", re.IGNORECASE)
COUNT_KEYS = ("count", "qty", "quantity", "num", "copies", "deck_count", "card_count")
CARD_KEYS = (
    "card_no", "cardnumber", "card_number", "cardNo", "number",
    "card_code", "cardCode", "management_number", "managementNumber",
)
NAME_KEYS = ("name", "card_name", "cardName")
RARITY_KEYS = ("rarity", "rare", "rarity_name")

def fetch(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 Chrome/149 Safari/537.36"
        ),
        "Accept-Language": "ja,en-US;q=0.8,en;q=0.7",
    }
    request = urllib.request.Request(url, headers=headers)
    contexts = [ssl.create_default_context()]
    insecure = ssl._create_unverified_context()
    contexts.append(insecure)

    errors: list[str] = []
    for context in contexts:
        try:
            with urllib.request.urlopen(request, timeout=30, context=context) as response:
                body = response.read()
                encoding = response.headers.get_content_charset() or "utf-8"
                return body.decode(encoding, errors="replace")
        except Exception as exc:
            errors.append(str(exc))
    raise RuntimeError("DECK LOGの取得に失敗しました: " + " / ".join(errors))

def first_value(item: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return None

def walk_json(value: Any, rows: list[dict[str, str]]) -> None:
    if isinstance(value, dict):
        card_no = first_value(value, CARD_KEYS)
        if isinstance(card_no, str):
            match = CARD_RE.search(card_no)
            if match:
                count_raw = first_value(value, COUNT_KEYS)
                try:
                    count = int(count_raw) if count_raw not in (None, "") else 1
                except (TypeError, ValueError):
                    count = 1
                rows.append({
                    "count": str(max(1, count)),
                    "card_no": match.group(1),
                    "rarity": str(first_value(value, RARITY_KEYS) or ""),
                    "name": str(first_value(value, NAME_KEYS) or ""),
                    "variant_id": "",
                })
        for child in value.values():
            walk_json(child, rows)
    elif isinstance(value, list):
        for child in value:
            walk_json(child, rows)

def parse_embedded_json(document: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    patterns = (
        r'<script[^>]+type=["\']application/json["\'][^>]*>(.*?)</script>',
        r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
    )
    for pattern in patterns:
        for match in re.finditer(pattern, document, re.IGNORECASE | re.DOTALL):
            raw = html.unescape(match.group(1)).strip()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            walk_json(payload, rows)
    return rows

def parse_html_text(document: str) -> list[dict[str, str]]:
    text = html.unescape(re.sub(r"<[^>]+>", "\n", document))
    rows: list[dict[str, str]] = []
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    for index, line in enumerate(lines):
        match = CARD_RE.search(line)
        if not match:
            continue
        card_no = match.group(1)
        context = " ".join(lines[max(0, index - 2): index + 3])
        count = 1
        count_patterns = (
            r"(?:×|x)\s*(\d+)",
            r"(\d+)\s*枚",
            r"\bcount\D{0,8}(\d+)\b",
        )
        for pattern in count_patterns:
            count_match = re.search(pattern, context, re.IGNORECASE)
            if count_match:
                count = int(count_match.group(1))
                break
        rows.append({
            "count": str(max(1, count)),
            "card_no": card_no,
            "rarity": "",
            "name": "",
            "variant_id": "",
        })
    return rows

def merge(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    totals: defaultdict[str, int] = defaultdict(int)
    for row in rows:
        card_no = row["card_no"].strip()
        if not CARD_RE.fullmatch(card_no):
            continue
        count = int(row.get("count") or 1)
        totals[card_no] += count
        current = merged.setdefault(card_no, {
            "count": "0",
            "card_no": card_no,
            "rarity": row.get("rarity", ""),
            "name": row.get("name", ""),
            "variant_id": "",
        })
        if not current["rarity"] and row.get("rarity"):
            current["rarity"] = row["rarity"]
        if not current["name"] and row.get("name"):
            current["name"] = row["name"]

    for card_no, count in totals.items():
        merged[card_no]["count"] = str(count)
    return sorted(merged.values(), key=lambda row: row["card_no"])

def write_tsv(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = ["count\tcard_no\trarity\tname\tvariant_id"]
    for row in rows:
        lines.append("\t".join([
            row["count"],
            row["card_no"],
            row.get("rarity", ""),
            row.get("name", ""),
            "",
        ]))
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deck-code", "--code", dest="deck_code", required=True)
    parser.add_argument("--out", "--output", dest="output", required=True)
    args = parser.parse_args()

    code = re.sub(r"[^A-Za-z0-9_-]", "", args.deck_code.strip().upper())
    if not code:
        print("[ERROR] empty deck code", file=sys.stderr)
        return 2

    url = "https://decklog.bushiroad.com/view/" + code
    try:
        document = fetch(url)
    except Exception as exc:
        print("[ERROR] " + str(exc), file=sys.stderr)
        return 1

    rows = parse_embedded_json(document)
    if not rows:
        rows = parse_html_text(document)
    rows = merge(rows)

    if not rows:
        debug_path = Path(args.output).with_suffix(".html")
        debug_path.write_text(document, encoding="utf-8")
        print(
            "[ERROR] カード番号を抽出できませんでした。"
            "取得HTMLを保存しました: {}".format(debug_path),
            file=sys.stderr,
        )
        return 1

    write_tsv(rows, Path(args.output))
    print("[OK] code={} cards={} total={} out={}".format(
        code,
        len(rows),
        sum(int(row["count"]) for row in rows),
        args.output,
    ))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
