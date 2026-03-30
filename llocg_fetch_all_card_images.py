#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llocg_fetch_all_card_images.py

Fetch LoveLive! OCG card images from the official site.

Strategy:
1) Build target card list from cards_min_tokv1.json (preferred) and compiled DB (union).
2) If <root>/official_image_manifest.json exists, try exact URLs from that manifest first.
3) Fall back to heuristic folder / rarity inference only for cards still missing.
4) For PR-family cards, heuristic rarity tries are restricted to PR / PR2 only.

Output layout:
  <root>/card_images/<FOLDER>/<CARDNO>-<RARITY>.png
"""
from __future__ import annotations

import argparse
import json
import random
import re
import time
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import requests
except Exception:
    requests = None  # type: ignore

BASE_URL = "https://llofficial-cardgame.com/wordpress/wp-content/images/cardlist"

DEFAULT_RARITIES = [
    "SD", "N", "R", "R2", "L", "L2", "PR", "PR2", "P", "P2",
    "SEC", "SEC2", "SECL", "AR", "RM", "RE", "PE", "PE2", "SECE", "LLE",
]

KNOWN_FOLDERS = [
    "BP01", "BP02", "BP03", "BP04", "BP05",
    "PBSP", "PBLS", "PBLL", "PBnj",
    "PR",
    "SPSD01", "NSD01", "PLSD01", "LSSD01", "HSSD01", "SSD01",
]

PB_PREFIX_TO_FOLDER = {
    "PL!SP": "PBSP",
    "PL!LS": "PBLS",
    "PL!N":  "PBnj",
    "PL!":   "PBLL",
    "LL":    "PBLL",
}
SD_PREFIX_TO_FOLDER = {
    "PL!SP": "SPSD01",
    "PL!N":  "NSD01",
    "PL!HS": "HSSD01",
    "PL!LS": "LSSD01",
    "PL!S":  "SSD01",
    "PL!":   "PLSD01",
}
RARITY_ALIAS = {
    "R+": "R2", "R＋": "R2",
    "L+": "L2", "L＋": "L2",
    "P+": "P2", "P＋": "P2",
    "PE+": "PE2", "PE＋": "PE2",
    "SEC+": "SEC2", "SEC＋": "SEC2",
    "PR+": "PR2", "PR＋": "PR2",
}

BP_RE = re.compile(r"(?:^|-)bp([1-9][0-9]*)(?:-|$)", re.IGNORECASE)
SD_RE = re.compile(r"(?:^|-)sd([0-9]+)(?:-|$)", re.IGNORECASE)
PB_RE = re.compile(r"(?:^|-)pb([0-9]+)(?:-|$)", re.IGNORECASE)


def _uniq_keep_order(xs: Sequence[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in xs:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def _read_text_lines(p: Path) -> List[str]:
    try:
        return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()]
    except FileNotFoundError:
        return []


def _normalize_rarity_token(rarity: str) -> str:
    r = (rarity or "").strip().upper().replace("＋", "+")
    return RARITY_ALIAS.get(r, r)


def _sanitize_rarities(items: List[str]) -> List[str]:
    out: List[str] = []
    for x in (items or []):
        if x is None:
            continue
        s = str(x).strip().upper().replace("＋", "+")
        if ":" in s:
            s = s.split(":", 1)[1].strip()
        for p in re.split(r"[\s,]+", s):
            p = _normalize_rarity_token(p.strip())
            if not p:
                continue
            if re.fullmatch(r"[A-Z0-9\+]{1,8}", p):
                out.append(p)
    return _uniq_keep_order(out)


def load_rarities(root: Path, outdir: Path, extra_cli: Optional[str]) -> List[str]:
    if extra_cli:
        items = [x.strip() for x in extra_cli.split(",") if x.strip()]
        rarities = _sanitize_rarities(items)
        return rarities or list(DEFAULT_RARITIES)
    for cand in [outdir / "_RARITIES.txt", root / "_RARITIES.txt"]:
        lines = [ln for ln in _read_text_lines(cand) if ln and not ln.startswith("#")]
        if lines:
            items: List[str] = []
            for ln in lines:
                items.extend([x.strip() for x in ln.split(",") if x.strip()])
            rarities = _sanitize_rarities(items)
            if rarities:
                return rarities
    return list(DEFAULT_RARITIES)


def find_latest_compiled(root: Path) -> Optional[Path]:
    cand = list(root.glob("cards_compiled_v*.json")) + list(root.glob("cards_compiled_*.json"))
    return sorted(cand)[-1] if cand else None


def find_tokv1_json(root: Path) -> Optional[Path]:
    p = root / "cards_min_tokv1.json"
    return p if p.exists() else None


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _norm_cardno_for_filename(cardno: str) -> str:
    parts = (cardno or "").split("-")
    if not parts:
        return cardno
    last = parts[-1]
    if last.isdigit():
        parts[-1] = last.zfill(3)
    return "-".join(parts)


def _card_prefix(cardno: str) -> str:
    parts = (cardno or "").split("-")
    if not parts:
        return cardno
    head = parts[0]
    if head.startswith("PL!"):
        return head
    return head


def _product_family(cardno: str) -> str:
    c = (cardno or "").lower()
    if "-pr-" in c:
        return "pr"
    if "-sd" in c:
        return "sd"
    if "-pb" in c:
        return "pb"
    if "-bp" in c:
        return "bp"
    return "other"


def _record_cardnumber(obj: Dict[str, Any]) -> Optional[str]:
    for k in ("cardnumber", "cardNumber", "card_no", "cardno", "id", "number", "card_number"):
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def load_compiled_records(path: Optional[Path]) -> List[Dict[str, Any]]:
    if not path or not path.exists():
        return []
    compiled = load_json(path)
    out: List[Dict[str, Any]] = []

    def push(cardno: str, meta: Optional[Dict[str, Any]] = None) -> None:
        rec = dict(meta or {})
        rec["cardnumber"] = cardno
        out.append(rec)

    if isinstance(compiled, dict):
        if isinstance(compiled.get("cards"), list):
            for obj in compiled["cards"]:
                if isinstance(obj, dict):
                    cn = _record_cardnumber(obj)
                    if cn:
                        push(cn, obj)
                elif isinstance(obj, str) and obj.strip():
                    push(obj.strip())
        else:
            for k, v in compiled.items():
                if isinstance(v, dict):
                    cn = _record_cardnumber(v)
                    if cn:
                        push(cn, v)
                if isinstance(k, str) and "-" in k and re.search(r"(bp|sd|pr|pb)", k, re.I):
                    push(k)
    elif isinstance(compiled, list):
        for obj in compiled:
            if isinstance(obj, dict):
                cn = _record_cardnumber(obj)
                if cn:
                    push(cn, obj)
            elif isinstance(obj, str) and obj.strip():
                push(obj.strip())

    dedup: Dict[str, Dict[str, Any]] = {}
    for rec in out:
        cn = rec["cardnumber"].strip()
        if cn:
            dedup[cn] = rec
    return list(dedup.values())


def load_tokv1_records(path: Optional[Path]) -> List[Dict[str, Any]]:
    if not path or not path.exists():
        return []
    obj = load_json(path)
    cards = obj if isinstance(obj, list) else obj.get("cards", obj)
    out: List[Dict[str, Any]] = []
    if isinstance(cards, list):
        for rec in cards:
            if isinstance(rec, dict):
                cn = rec.get("cardnumber")
                if isinstance(cn, str) and cn.strip():
                    out.append(rec)
    return out


def load_target_records(root: Path, compiled_path: Optional[Path]) -> Tuple[List[Dict[str, Any]], Optional[Path], Optional[Path]]:
    tokv1_path = find_tokv1_json(root)
    tokv1_records = load_tokv1_records(tokv1_path)
    compiled_records = load_compiled_records(compiled_path)

    merged: Dict[str, Dict[str, Any]] = {}
    for rec in compiled_records:
        cn = _norm_cardno_for_filename(rec["cardnumber"].strip())
        rec = dict(rec)
        rec["cardnumber"] = cn
        merged[cn] = rec
    for rec in tokv1_records:
        cn = _norm_cardno_for_filename(rec["cardnumber"].strip())
        merged.setdefault(cn, {}).update(rec)
        merged[cn]["cardnumber"] = cn
    records = [merged[k] for k in sorted(merged.keys())]
    return records, tokv1_path, compiled_path


def build_url(folder: str, remote_filename: str) -> str:
    return f"{BASE_URL}/{folder}/{remote_filename}"


def folder_candidates_for_cardno(cardno: str) -> List[str]:
    c = cardno

    m = SD_RE.search(c)
    if m:
        pref = _card_prefix(c)
        folder = SD_PREFIX_TO_FOLDER.get(pref)
        sdnum = m.group(1)
        sdtag = f"SD{sdnum.zfill(2)}"
        cand: List[str] = []
        if folder:
            if folder.endswith("SD01"):
                cand.append(folder[:-2] + sdnum.zfill(2))
            else:
                cand.append(folder)
        cand.extend([f for f in KNOWN_FOLDERS if f.endswith(sdtag)])
        return _uniq_keep_order(cand)

    if "-PR-" in c:
        return ["PR"]

    bm = BP_RE.search(c)
    if bm:
        return [f"BP{int(bm.group(1)):02d}"]

    pm = PB_RE.search(c)
    if pm:
        best = PB_PREFIX_TO_FOLDER.get(_card_prefix(c))
        cand = [best] if best else []
        cand.extend([f for f in KNOWN_FOLDERS if f.startswith("PB")])
        return _uniq_keep_order([x for x in cand if x])

    return list(KNOWN_FOLDERS)


def family_rarities(cardno: str, global_rarities: Sequence[str], manifest_entries: Optional[List[Dict[str, Any]]] = None) -> List[str]:
    manifest_rs: List[str] = []
    if manifest_entries:
        manifest_rs = [e.get("rarity_norm", "") for e in manifest_entries if isinstance(e, dict)]
        manifest_rs = _sanitize_rarities(manifest_rs)
    fam = _product_family(cardno)
    if fam == "sd":
        fam_order = ["SD"]
    elif fam == "pr":
        # PR family is intentionally narrow.
        # In current local validation, PR cards are covered by PR / PR2 only;
        # trying broader rarity families just generates large numbers of 404s.
        fam_order = ["PR", "PR2"]
    elif fam in {"bp", "pb"}:
        fam_order = ["N", "R", "R2", "L", "L2", "RM", "AR", "SEC", "SEC2", "SECL", "RE", "PE", "PE2", "SECE", "LLE", "P", "P2", "PR", "PR2"]
    else:
        fam_order = []
    if fam == "pr":
        combined = manifest_rs + fam_order
    else:
        combined = manifest_rs + fam_order + list(global_rarities)
    return _uniq_keep_order(_sanitize_rarities(combined))


def _rarity_mid_token(rarity: str) -> str:
    r = _normalize_rarity_token(rarity)
    if r.endswith("2") and len(r) >= 2:
        return r[:-1]
    return r


def remote_filename_variants(folder: str, cardno: str, rarity: str) -> List[str]:
    folder_u = (folder or "").strip().upper()
    r = _normalize_rarity_token(rarity)
    out: List[str] = [f"{cardno}-{r}.png"]

    if folder_u == "PR":
        cn2 = cardno
        cn2_low = cn2.lower()
        if "-pr-" in cn2_low:
            parts = re.split("(?i)-pr-", cn2)
            if len(parts) >= 2:
                cn_drop = "-".join([parts[0]] + parts[1:])
                out.append(f"{cn_drop}-{r}.png")

    cn_low = cardno.lower()
    if folder_u == "BP03" and "-bp3-" in cn_low:
        idx = cn_low.find("-bp3-")
        prefix = cardno[:idx]
        set_tok = cardno[idx + 1: idx + 4]
        rest = cardno[idx + 5:]
        parts = rest.split("-")
        num = parts[-1]
        mids = [r, _rarity_mid_token(r)]
        for mid in _uniq_keep_order([m for m in mids if m]):
            out.append(f"{prefix}-{set_tok}-{mid}-{num}-{r}.png")

    return _uniq_keep_order(out)


def load_official_manifest(root: Path) -> Dict[str, List[Dict[str, Any]]]:
    path = root / "official_image_manifest.json"
    if not path.exists():
        return {}
    try:
        obj = load_json(path)
    except Exception:
        return {}
    cards = obj.get("cards", {}) if isinstance(obj, dict) else {}
    out: Dict[str, List[Dict[str, Any]]] = {}
    if isinstance(cards, dict):
        for cn, entries in cards.items():
            if isinstance(cn, str) and isinstance(entries, list):
                out[_norm_cardno_for_filename(cn)] = [e for e in entries if isinstance(e, dict)]
    return out


@dataclass
class TryResult:
    ok: bool
    status: str
    url: str
    path: str
    folder: str
    cardno: str
    rarity: str
    mode: str
    bytes: int = 0


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _urllib_get(url: str, headers: Dict[str, str], timeout: float, insecure: bool) -> Tuple[int, bytes]:
    import ssl
    from urllib.request import Request, urlopen
    ctx = None
    if insecure:
        ctx = ssl._create_unverified_context()
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout, context=ctx) as r:
        data = r.read()
        return int(getattr(r, "status", 200) or 200), data


def _http_get(sess: Optional["requests.Session"], url: str, headers: Dict[str, str], timeout: float, verify: bool) -> Tuple[int, bytes]:
    if sess is None:
        return _urllib_get(url, headers=headers, timeout=timeout, insecure=not verify)
    resp = sess.get(url, timeout=timeout, headers=headers, verify=verify)
    return resp.status_code, resp.content


def _download_url(
    sess: Optional["requests.Session"],
    url: str,
    out_path: Path,
    timeout: float,
    allow_insecure_fallback: bool,
    state: Dict[str, Any],
) -> Tuple[bool, str, int]:
    verify = not bool(state.get("insecure", False))
    try:
        status_code, content = _http_get(sess, url, state["headers"], timeout=timeout, verify=verify)
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        if allow_insecure_fallback and ("CERTIFICATE_VERIFY_FAILED" in msg or "SSLError" in msg or "ssl" in msg.lower()) and not state.get("insecure_used", False):
            state["insecure_used"] = True
            state["insecure"] = True
            try:
                status_code, content = _http_get(sess, url, state["headers"], timeout=timeout, verify=False)
            except Exception as e2:
                return False, f"EXC {type(e2).__name__}", 0
        else:
            return False, f"EXC {type(e).__name__}", 0

    if status_code != 200 or not content:
        return False, f"HTTP {status_code}", 0

    _ensure_dir(out_path.parent)
    out_path.write_bytes(content)
    return True, "OK", len(content)


def try_manifest_entry(
    sess: Optional["requests.Session"],
    cardno: str,
    entry: Dict[str, Any],
    outdir: Path,
    skip_existing: bool,
    timeout: float,
    allow_insecure_fallback: bool,
    state: Dict[str, Any],
) -> TryResult:
    folder = str(entry.get("folder", "") or "")
    rarity = _normalize_rarity_token(str(entry.get("rarity_norm", "") or ""))
    remote_filename = str(entry.get("remote_filename", "") or "")
    exact_url = str(entry.get("exact_url", "") or "")
    if not folder or not rarity:
        return TryResult(False, "BAD_ENTRY", "", "", folder, cardno, rarity, "manifest", 0)

    out_path = outdir / folder / f"{cardno}-{rarity}.png"
    if skip_existing and out_path.exists() and out_path.stat().st_size > 0:
        return TryResult(True, "SKIP_EXISTS", exact_url, str(out_path), folder, cardno, rarity, "manifest", 0)

    urls = []
    if exact_url:
        urls.append(exact_url)
    if remote_filename:
        built = build_url(folder, remote_filename)
        if built not in urls:
            urls.append(built)

    last_status = "NO_TRY"
    last_url = ""
    for url in urls:
        last_url = url
        ok, status, nbytes = _download_url(sess, url, out_path, timeout, allow_insecure_fallback, state)
        if ok:
            return TryResult(True, status, url, str(out_path), folder, cardno, rarity, "manifest", nbytes)
        last_status = status

    return TryResult(False, last_status, last_url, str(out_path), folder, cardno, rarity, "manifest", 0)


def try_heuristic(
    sess: Optional["requests.Session"],
    cardno: str,
    folder: str,
    rarity: str,
    outdir: Path,
    skip_existing: bool,
    timeout: float,
    allow_insecure_fallback: bool,
    state: Dict[str, Any],
) -> TryResult:
    rarity = _normalize_rarity_token(rarity)
    out_path = outdir / folder / f"{cardno}-{rarity}.png"
    if skip_existing and out_path.exists() and out_path.stat().st_size > 0:
        return TryResult(True, "SKIP_EXISTS", "", str(out_path), folder, cardno, rarity, "heuristic", 0)

    last_status = "NO_TRY"
    last_url = ""
    for remote_filename in remote_filename_variants(folder, cardno, rarity):
        url = build_url(folder, remote_filename)
        last_url = url
        ok, status, nbytes = _download_url(sess, url, out_path, timeout, allow_insecure_fallback, state)
        if ok:
            return TryResult(True, status, url, str(out_path), folder, cardno, rarity, "heuristic", nbytes)
        last_status = status
    return TryResult(False, last_status, last_url, str(out_path), folder, cardno, rarity, "heuristic", 0)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True, help="Project root (contains cards_min_tokv1.json / cards_compiled_*.json)")
    ap.add_argument("--compiled", type=Path, default=None, help="Optional compiled JSON path")
    ap.add_argument("--outdir", type=Path, default=None, help="Output dir (default: <root>/card_images)")
    ap.add_argument("--rarities", type=str, default=None, help="Comma-separated rarities to try (overrides _RARITIES.txt)")
    ap.add_argument("--all-rarities", action="store_true", help="Try to fetch all rarities for each card (default ON)")
    ap.add_argument("--no-all-rarities", dest="all_rarities", action="store_false", help="Stop after first success per card+folder")
    ap.set_defaults(all_rarities=True)
    ap.add_argument("--skip-existing", action="store_true", help="Skip already-downloaded files (default ON)")
    ap.add_argument("--no-skip-existing", dest="skip_existing", action="store_false")
    ap.set_defaults(skip_existing=True)
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--sleep", type=float, default=0.02)
    ap.add_argument("--jitter", type=float, default=0.03)
    ap.add_argument("--max-warn-total", type=int, default=40)
    ap.add_argument("--max-warn-per-card", type=int, default=2)
    ap.add_argument("--user-agent", type=str, default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--insecure", action="store_true")
    ap.add_argument("--no-insecure-fallback", action="store_true")
    args = ap.parse_args(argv)

    def _log(*a, **k):
        if not args.quiet:
            print(*a, **k)

    root = args.root.resolve()
    compiled_path = args.compiled.resolve() if args.compiled else find_latest_compiled(root)
    outdir = args.outdir.resolve() if args.outdir else (root / "card_images")
    outdir.mkdir(parents=True, exist_ok=True)

    global_rarities = load_rarities(root, outdir, args.rarities)
    global_rarities = _uniq_keep_order(_sanitize_rarities(global_rarities)) or list(DEFAULT_RARITIES)

    target_records, tokv1_path, compiled_path = load_target_records(root, compiled_path)
    if not target_records:
        print("[ERR] No card numbers found in tokv1/compiled DB.")
        print("      tokv1   :", tokv1_path)
        print("      compiled:", compiled_path)
        return 2

    manifest = load_official_manifest(root)

    sess = requests.Session() if requests is not None else None
    state: Dict[str, Any] = {
        "headers": {"User-Agent": args.user_agent},
        "insecure": bool(args.insecure),
        "insecure_used": False,
    }
    allow_fallback = not args.no_insecure_fallback

    results: List[TryResult] = []
    ok_files = 0
    skip_files = 0
    fail_attempts = 0
    manifest_success = 0
    heuristic_success = 0
    manifest_cards = 0

    warn_total = 0
    warn_by_card: Dict[str, int] = {}

    for i, rec in enumerate(target_records, 1):
        cardno = _norm_cardno_for_filename(rec["cardnumber"].strip())
        manifest_entries = manifest.get(cardno, [])
        if manifest_entries:
            manifest_cards += 1

        per_card_results: List[TryResult] = []
        card_had_success = False

        # 1) exact manifest URLs
        if manifest_entries:
            for entry in manifest_entries:
                tr = try_manifest_entry(
                    sess=sess,
                    cardno=cardno,
                    entry=entry,
                    outdir=outdir,
                    skip_existing=args.skip_existing,
                    timeout=args.timeout,
                    allow_insecure_fallback=allow_fallback,
                    state=state,
                )
                per_card_results.append(tr)
                if tr.ok:
                    card_had_success = True
                    if tr.status == "SKIP_EXISTS":
                        skip_files += 1
                    else:
                        ok_files += 1
                    manifest_success += 1
                    if (not args.all_rarities) and tr.status != "SKIP_EXISTS":
                        break
                else:
                    fail_attempts += 1

                time.sleep(args.sleep + random.random() * args.jitter)

        # 2) heuristic fallback only if manifest absent or no manifest success
        if not card_had_success:
            folders = []
            if manifest_entries:
                folders.extend([str(e.get("folder", "") or "") for e in manifest_entries if str(e.get("folder", "") or "")])
            folders.extend(folder_candidates_for_cardno(cardno))
            folders = _uniq_keep_order([f for f in folders if f])

            rarities = family_rarities(cardno, global_rarities, manifest_entries=manifest_entries)
            chosen_folder = None

            for folder in folders:
                any_ok_in_folder = False
                folder_results: List[TryResult] = []

                for rarity in rarities:
                    tr = try_heuristic(
                        sess=sess,
                        cardno=cardno,
                        folder=folder,
                        rarity=rarity,
                        outdir=outdir,
                        skip_existing=args.skip_existing,
                        timeout=args.timeout,
                        allow_insecure_fallback=allow_fallback,
                        state=state,
                    )
                    folder_results.append(tr)

                    if tr.ok:
                        card_had_success = True
                        any_ok_in_folder = True
                        if tr.status == "SKIP_EXISTS":
                            skip_files += 1
                        else:
                            ok_files += 1
                        heuristic_success += 1
                        if (not args.all_rarities) and tr.status != "SKIP_EXISTS":
                            break
                    else:
                        fail_attempts += 1

                    time.sleep(args.sleep + random.random() * args.jitter)

                if any_ok_in_folder:
                    chosen_folder = folder
                    per_card_results.extend(folder_results)
                    break
                else:
                    if folder == folders[-1]:
                        per_card_results.extend(folder_results)

                    warn_by_card.setdefault(cardno, 0)
                    if warn_total < args.max_warn_total and warn_by_card[cardno] < args.max_warn_per_card:
                        ex = folder_results[0].url if folder_results else ""
                        _log(f"[WARN] {cardno}: no images under folder={folder} (example {ex})")
                        warn_total += 1
                        warn_by_card[cardno] += 1

        results.extend(per_card_results)

        if i % 100 == 0 or i == 1:
            _log(f"[{i}/{len(target_records)}] ok_files={ok_files} skipped={skip_files} fail_attempts={fail_attempts} manifest_cards={manifest_cards} ...")

    report = {
        "root": str(root),
        "tokv1": str(tokv1_path) if tokv1_path else "",
        "compiled": str(compiled_path) if compiled_path else "",
        "outdir": str(outdir),
        "manifest_present": bool(manifest),
        "rarities": global_rarities,
        "counts": {
            "cards_total": len(target_records),
            "cards_with_manifest": manifest_cards,
            "ok_files": ok_files,
            "skipped": skip_files,
            "fail_attempts": fail_attempts,
            "manifest_successes": manifest_success,
            "heuristic_successes": heuristic_success,
        },
        "notes": {
            "insecure_mode_used": bool(state.get("insecure_used", False) or state.get("insecure", False)),
            "strategy": "manifest exact URL first; heuristic folder/rarity fallback only when needed",
        },
        "results": [tr.__dict__ for tr in results],
    }
    rep_path = outdir / "_download_report.json"
    rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    fail_lines: List[str] = []
    for tr in results:
        if (not tr.ok) and tr.status != "SKIP_EXISTS":
            fail_lines.append(f"{tr.cardno}\t{tr.folder}\t{tr.rarity}\t{tr.mode}\t{tr.status}\t{tr.url}")
    fail_log = outdir / "_failures.log"
    fail_log.write_text("\n".join(fail_lines) + ("\n" if fail_lines else ""), encoding="utf-8")

    print("[DONE]")
    print("tokv1    :", tokv1_path)
    print("compiled :", compiled_path)
    print("outdir   :", outdir)
    print("manifest :", bool(manifest))
    print("rarities :", ", ".join(global_rarities))
    print("ok_files :", ok_files)
    print("skipped  :", skip_files)
    print("failed   :", len(fail_lines))
    print("report   :", rep_path)
    print("fail_log :", fail_log)

    if ok_files == 0 and skip_files == 0:
        print("[ERR] No files were downloaded or skipped. This usually means target extraction failed or all URLs are unreachable.")
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
