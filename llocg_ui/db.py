from __future__ import annotations
import csv
import json
import pathlib
from typing import Any, Dict, List, Tuple

def normalize_card_no(s: str) -> str:
    s = (s or "").strip()
    s = s.replace("＋", "+")
    while s.endswith("-"):
        s = s[:-1]
    return s

def load_compiled_db(root: pathlib.Path) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    p = root / "llocg_db_out_full" / "cards_compiled_v7b.json"
    if not p.exists():
        cand = sorted((root / "llocg_db_out_full").glob("cards_compiled_*.json"))
        if cand:
            p = cand[-1]
    if not p.exists():
        return out
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, list):
        for row in data:
            if isinstance(row, dict):
                cn = normalize_card_no(str(row.get("cardnumber","")))
                if cn:
                    out[cn] = row
    elif isinstance(data, dict):
        for k,v in data.items():
            cn = normalize_card_no(str(k))
            if cn:
                out[cn] = v if isinstance(v, dict) else {"raw": v}
    return out

def load_tokv1(root: pathlib.Path) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    p = root / "cards_min_tokv1.json"
    if not p.exists():
        return out
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, list):
        for row in data:
            if isinstance(row, dict):
                cn = normalize_card_no(str(row.get("cardnumber","")))
                if cn:
                    out[cn] = row
    elif isinstance(data, dict):
        for k,v in data.items():
            cn = normalize_card_no(str(k))
            if cn:
                out[cn] = v if isinstance(v, dict) else {"raw": v}
    return out

def _sniff_delimiter(sample: str) -> str:
    if "\t" in sample:
        return "\t"
    if "," in sample and sample.count(",") >= sample.count(" "):
        return ","
    return "\t"

def load_decklist(root: pathlib.Path, deck_code: str) -> Tuple[List[Dict[str, Any]], str, str]:
    deck_code = (deck_code or "").strip()
    ddir = root / "llocg_db_out_full" / "decklists"
    cand = [
        ddir / f"{deck_code}.tsv",
        ddir / f"deck_{deck_code}.tsv",
        ddir / f"{deck_code}.txt",
        ddir / f"deck_{deck_code}.txt",
    ]
    deck_path = None
    for p in cand:
        if p.exists():
            deck_path = p
            break
    if deck_path is None:
        return [], f"Decklist not found under {ddir} for code={deck_code}", ""

    raw = deck_path.read_text(encoding="utf-8", errors="replace")
    lines = [ln for ln in raw.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    if not lines:
        return [], f"Decklist empty: {deck_path.name}", deck_path.name

    import io
    delim = _sniff_delimiter(raw[:4096])
    f = io.StringIO("\n".join(lines))
    reader = csv.DictReader(f, delimiter=delim)

    rows: List[Dict[str, Any]] = []
    for r in reader:
        def pick(*keys: str) -> str:
            for k in keys:
                for kk in (k, k.lower(), k.upper()):
                    if kk in r and r[kk] is not None and str(r[kk]).strip() != "":
                        return str(r[kk]).strip()
            return ""
        card_no = pick("card_no","cardnumber","cardNumber","cn","card")
        count = pick("count","num","quantity","qty")
        rarity = pick("rarity","rare","r")
        cn = normalize_card_no(card_no)
        if not cn:
            continue
        try:
            n = int(count) if count else 1
        except:
            n = 1
        for _ in range(max(n,1)):
            rows.append({"card_no": cn, "rarity": (rarity or "").strip()})
    return rows, "", deck_path.name
