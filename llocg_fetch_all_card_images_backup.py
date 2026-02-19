#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llocg_fetch_all_card_images_v8.py

Fetch LoveLive! OCG card images from the official site, robust to:
- expansion folder variations (BP01-05, PB*, PR, *SD01, etc.)
- rarity suffix variations (N, R, R2, L, L2, SD, PR, SEC, P, P2, ...)
- card-number formatting variations (zero-padding, embedded "-R-" etc.)
- TLS certificate issues on some local Python installs (auto-fallback to verify=False)

Output layout (requested): group by EXPANSION FOLDER only
  <root>/card_images/<FOLDER>/<CARDNO>-<RARITY>.png

By default, already-existing files are skipped.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import requests
except Exception as e:  # pragma: no cover
    requests = None  # type: ignore


BASE_URL = "https://llofficial-cardgame.com/wordpress/wp-content/images/cardlist"

# Reasonable defaults; user can extend via _RARITIES.txt
DEFAULT_RARITIES = ["N", "R", "R2", "L", "L2", "SD", "PR", "SEC", "SECL", "AR", "RM", "P", "P2"]

# Folder candidates that are known to exist (user-provided).
KNOWN_FOLDERS = [
    "BP01", "BP02", "BP03", "BP04", "BP05",
    "PBSP", "PBLS", "PBLL", "PBnj",
    "PR",
    "SPSD01", "NSD01", "PLSD01", "LSSD01", "HSSD01",
]

# Mapping rules: card prefix -> PB folder (best-effort; still falls back to trying all PB* if needed)
PB_PREFIX_TO_FOLDER = {
    "PL!SP": "PBSP",
    "PL!LS": "PBLS",
    "PL!N":  "PBnj",  # based on user example
    "PL!":   "PBLL",  # "PL!-" no subtag tends to align with PBLL per user note
    "LL":    "PBLL",
}

SD_PREFIX_TO_FOLDER = {
    "PL!SP": "SPSD01",
    "PL!N":  "NSD01",
    "PL!HS": "HSSD01",
    "PL!LS": "LSSD01",
    "PL!":   "PLSD01",
}

BP_RE = re.compile(r"(?:^|-)bp([1-9])(?:-|$)", re.IGNORECASE)
SD_RE = re.compile(r"(?:^|-)sd([0-9]+)(?:-|$)", re.IGNORECASE)
PB_RE = re.compile(r"(?:^|-)pb([0-9]+)(?:-|$)", re.IGNORECASE)
PR_RE = re.compile(r"(?:^|-)PR-(\d+)$", re.IGNORECASE)


def _norm_cardno_for_filename(cardno: str) -> str:
    """
    Keep case & punctuation, only fix the *last* numeric token to 3-digit zero padding.
    Example:
      PL!-bp3-4   -> PL!-bp3-004
      LL-PR-4     -> LL-PR-004
      PL!-bp3-R-1 -> PL!-bp3-R-001
    """
    parts = cardno.split("-")
    if not parts:
        return cardno
    last = parts[-1]
    if last.isdigit():
        parts[-1] = last.zfill(3)
        return "-".join(parts)
    # Sometimes last token can be like "001R" etc. Only pad if purely numeric.
    return cardno


def _read_text_lines(p: Path) -> List[str]:
    try:
        return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()]
    except FileNotFoundError:
        return []


def load_rarities(root: Path, outdir: Path, extra_cli: Optional[str]) -> List[str]:
    """
    Priority:
      1) CLI --rarities "A,B,C"
      2) outdir/_RARITIES.txt
      3) root/_RARITIES.txt
      4) DEFAULT_RARITIES
    """
    if extra_cli:
        items = [x.strip() for x in extra_cli.split(",") if x.strip()]
        return _uniq_keep_order(items)

    for cand in [outdir / "_RARITIES.txt", root / "_RARITIES.txt"]:
        lines = [ln for ln in _read_text_lines(cand) if ln and not ln.startswith("#")]
        if lines:
            # allow comma-separated in lines
            items: List[str] = []
            for ln in lines:
                items.extend([x.strip() for x in ln.split(",") if x.strip()])
            return _uniq_keep_order(items)

    return list(DEFAULT_RARITIES)


def _uniq_keep_order(xs: Sequence[str]) -> List[str]:
    seen = set()
    out = []
    for x in xs:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def find_latest_compiled(root: Path) -> Path:
    """
    Accept both:
      cards_compiled_v*.json  (project standard)
      cards_compiled_*.json   (older)
    Choose the lexicographically largest as a stable approximation of "latest".
    """
    cand = list(root.glob("cards_compiled_v*.json")) + list(root.glob("cards_compiled_*.json"))
    if not cand:
        raise FileNotFoundError("No compiled DB found under root: expected cards_compiled_v*.json")
    cand = sorted(cand)
    return cand[-1]


def load_compiled(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_cardnos(compiled: Any) -> List[str]:
    """
    Robustly extract card numbers from various schemas:
      - list of dicts with 'card_no'/'cardno'/'id'/'number'
      - dict with key 'cards' that is list
      - dict mapping cardno -> dict
    """
    out: List[str] = []

    def push(x: Any):
        if isinstance(x, str) and x:
            out.append(x)

    if isinstance(compiled, dict):
        if "cards" in compiled and isinstance(compiled["cards"], list):
            for obj in compiled["cards"]:
                if isinstance(obj, dict):
                    for k in ("cardnumber", "cardNumber", "card_no", "cardno", "id", "number", "card_number"):
                        if k in obj and isinstance(obj[k], str):
                            push(obj[k])
                            break
                elif isinstance(obj, str):
                    push(obj)
        else:
            # maybe dict mapping id->entry
            # use keys that look like cardnos
            for k, v in compiled.items():
                if isinstance(k, str) and ("-" in k) and len(k) >= 6:
                    # heuristic: cardno often contains 'bp'/'sd'/'PR' etc.
                    if re.search(r"(bp|sd|PR|pb)", k, re.IGNORECASE):
                        push(k)
                # also check values if dict
                if isinstance(v, dict):
                    for kk in ("cardnumber", "cardNumber", "card_no", "cardno", "id", "number", "card_number"):
                        if kk in v and isinstance(v[kk], str):
                            push(v[kk])
                            break
    elif isinstance(compiled, list):
        for obj in compiled:
            if isinstance(obj, dict):
                for k in ("cardnumber", "cardNumber", "card_no", "cardno", "id", "number", "card_number"):
                    if k in obj and isinstance(obj[k], str):
                        push(obj[k])
                        break
            elif isinstance(obj, str):
                push(obj)

    # Clean + de-dup
    out = [o.strip() for o in out if isinstance(o, str) and o.strip()]
    out = _uniq_keep_order(out)

    # Safety: only keep strings that look like cardnos
    out2 = []
    for o in out:
        if "-" in o and len(o) >= 6:
            out2.append(o)
    return out2


def folder_candidates_for_cardno(cardno: str) -> List[str]:
    """
    Determine likely folder(s) to try, ordered by probability.
    We still allow fallback to KNOWN_FOLDERS to be robust.
    """
    c = cardno

    # 1) SD decks
    m = SD_RE.search(c)
    if m:
        pref = _card_prefix(c)
        folder = SD_PREFIX_TO_FOLDER.get(pref)
        # sd number also matters (sd1 -> *SD01)
        sdnum = m.group(1)
        sdtag = f"SD{sdnum.zfill(2)}"
        # Our known folders are ...SD01 ; build accordingly if pref mapping exists.
        cand: List[str] = []
        if folder:
            # ensure it matches the sd number; replace trailing digits
            if folder.endswith("SD01"):
                folder2 = folder[:-2] + sdnum.zfill(2)
            else:
                folder2 = folder
            cand.append(folder2)
        # fallback: try any folder that ends with sdtag (case-sensitive)
        for f in KNOWN_FOLDERS:
            if f.endswith(sdtag):
                cand.append(f)
        return _uniq_keep_order(cand)

    # 2) PR folder
    if "-PR-" in c:
        return ["PR"]

    # 3) BP expansions from bpX
    bm = BP_RE.search(c)
    if bm:
        x = int(bm.group(1))
        if 1 <= x <= 9:
            return [f"BP0{x}"]

    # 4) PB: based on prefix mapping + still try other PB folders
    pm = PB_RE.search(c)
    if pm:
        pref = _card_prefix(c)
        best = PB_PREFIX_TO_FOLDER.get(pref)
        cand = []
        if best:
            cand.append(best)
        # plus all PB* known
        cand.extend([f for f in KNOWN_FOLDERS if f.startswith("PB")])
        return _uniq_keep_order(cand)

    # 5) LL-bpX without bp marker? (unlikely)
    # Fallback: try all known folders
    return list(KNOWN_FOLDERS)


def _card_prefix(cardno: str) -> str:
    """
    Prefix is the first token or first two tokens if starts with PL!<TAG>.
    Examples:
      PL!N-sd1-025 -> PL!N
      PL!SP-sd1-020 -> PL!SP
      PL!-sd1-004 -> PL!
      LL-bp2-001 -> LL
    """
    parts = cardno.split("-")
    if not parts:
        return cardno
    head = parts[0]
    # PL!* may be embedded as first token (e.g., "PL!N", "PL!SP", "PL!")
    if head.startswith("PL!"):
        return head
    return head


@dataclass
class TryResult:
    ok: bool
    status: str
    url: str
    path: str
    folder: str
    cardno: str
    rarity: str
    bytes: int = 0


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def build_url(folder: str, remote_filename: str) -> str:
    return f"{BASE_URL}/{folder}/{remote_filename}"


def _rarity_mid_token(rarity: str) -> str:
    """Return a simplified rarity token sometimes used mid-filename.

    For BP03, we have observed the official image filenames embedding a
    rarity token immediately after the set code, and also at the suffix:
      - PL!-bp3-R-001-R.png
      - PL!N-bp3-N-022-N.png

    For suffix variants like R2/L2/P2, the mid token may appear either as
    the full token (R2) or the base token (R). This helper returns the
    base token.
    """
    r = (rarity or "").strip().upper()
    if r.endswith("2") and len(r) >= 2:
        return r[:-1]
    return r


def remote_filename_variants(folder: str, cardno: str, rarity: str) -> List[str]:
    """Generate remote filename candidates (not local save names).

    Default pattern:
      {cardno}-{rarity}.png

    BP03 has a known variant:
      {prefix}-bp3-{mid}-{num}-{rarity}.png
    where {mid} is usually equal to rarity (or the base token for *2)
    and {prefix} is the card prefix before '-bp3-'.
    """
    folder_u = (folder or "").strip().upper()
    r = (rarity or "").strip().upper()
    out: List[str] = []

    # Normal pattern (works for most folders)
    out.append(f"{cardno}-{r}.png")

    # BP03 variant (insert rarity token after bp3)
    cn_low = (cardno or "").lower()
    if folder_u == "BP03" and "-bp3-" in cn_low:
        idx = cn_low.find("-bp3-")
        prefix = cardno[:idx]  # up to the hyphen before bp3
        set_tok = cardno[idx + 1: idx + 4]  # 'bp3' in original case
        rest = cardno[idx + 5:]  # after '-bp3-'
        parts = rest.split("-")
        num = parts[-1]
        mids = [r, _rarity_mid_token(r)]
        for mid in list(dict.fromkeys([m for m in mids if m])):
            out.append(f"{prefix}-{set_tok}-{mid}-{num}-{r}.png")

    # De-dup while preserving order
    return list(dict.fromkeys(out))


def download_one(
    sess: "requests.Session",
    folder: str,
    cardno: str,
    rarity: str,
    outdir: Path,
    skip_existing: bool,
    timeout: float,
    sleep: float,
    jitter: float,
    allow_insecure_fallback: bool,
    state: Dict[str, Any],
) -> TryResult:
    """
    Download a single (folder,cardno,rarity) image.
    - Skips if already exists and skip_existing.
    - Auto-fallback to verify=False once if SSL fails.
    """
    # store by folder only (requested)
    folder_dir = outdir / folder
    filename = f"{cardno}-{rarity}.png"
    path = folder_dir / filename

    if skip_existing and path.exists() and path.stat().st_size > 0:
        return TryResult(ok=True, status="SKIP_EXISTS", url="", path=str(path), folder=folder, cardno=cardno, rarity=rarity, bytes=0)

    last_url = ""
    last_status = "NO_TRY"
    for remote_filename in remote_filename_variants(folder, cardno, rarity):
        url = build_url(folder, remote_filename)
        last_url = url
        # ensure folder only when actually writing
        verify = not bool(state.get("insecure", False))
        try:
            resp = sess.get(url, timeout=timeout, headers=state["headers"], verify=verify)
        except Exception as e:
            # SSL failure fallback
            msg = f"{type(e).__name__}: {e}"
            if allow_insecure_fallback and ("CERTIFICATE_VERIFY_FAILED" in msg or "SSLError" in msg or "ssl" in msg.lower()) and not state.get("insecure_used", False):
                state["insecure_used"] = True
                state["insecure"] = True
                try:
                    resp = sess.get(url, timeout=timeout, headers=state["headers"], verify=False)
                except Exception as e2:
                    last_status = f"EXC {type(e2).__name__}"
                    continue
            else:
                last_status = f"EXC {type(e).__name__}"
                continue

        if resp.status_code != 200 or not resp.content:
            last_status = f"HTTP {resp.status_code}"
            continue

        _ensure_dir(folder_dir)
        path.write_bytes(resp.content)
        return TryResult(True, "OK", url, str(path), folder, cardno, rarity, len(resp.content))

    return TryResult(False, last_status, last_url, str(path), folder, cardno, rarity, 0)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True, help="Project root (contains cards_compiled_*.json)")
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
    ap.add_argument("--sleep", type=float, default=0.05)
    ap.add_argument("--jitter", type=float, default=0.05)
    ap.add_argument("--max-warn-total", type=int, default=40, help="Rate-limit console warnings")
    ap.add_argument("--max-warn-per-card", type=int, default=2, help="Rate-limit warnings per card")
    ap.add_argument("--user-agent", type=str, default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")
    ap.add_argument("--insecure", action="store_true", help="Disable TLS verification (not recommended). Auto-fallback is enabled by default.")
    ap.add_argument("--no-insecure-fallback", action="store_true", help="Disable auto TLS fallback.")
    args = ap.parse_args(argv)

    root = args.root.resolve()
    compiled_path = args.compiled.resolve() if args.compiled else find_latest_compiled(root)
    outdir = args.outdir.resolve() if args.outdir else (root / "card_images")

    outdir.mkdir(parents=True, exist_ok=True)

    rarities = load_rarities(root, outdir, args.rarities)
    rarities = _uniq_keep_order(rarities)
    if not rarities:
        rarities = list(DEFAULT_RARITIES)

    compiled = load_compiled(compiled_path)
    cardnos = iter_cardnos(compiled)
    if not cardnos:
        print("[ERR] No card numbers found in compiled DB.")
        print("      compiled:", compiled_path)
        print("      Hint: check schema; expected dict['cards'] list or mapping keys.")
        return 2

    # normalize cardnos for filename usage (padding)
    cardnos_norm = [_norm_cardno_for_filename(cn) for cn in cardnos]
    # keep original order but normalized
    cardnos_norm = _uniq_keep_order(cardnos_norm)

    if requests is None:
        print("[ERR] requests not installed; please install requests or use a Python with requests available.")
        return 2

    sess = requests.Session()

    state: Dict[str, Any] = {
        "headers": {"User-Agent": args.user_agent},
        "insecure": bool(args.insecure),
        "insecure_used": False,
    }
    allow_fallback = (not args.no_insecure_fallback)

    results: List[TryResult] = []
    ok_files = 0
    skip_files = 0
    fail_attempts = 0

    warn_total = 0
    warn_by_card: Dict[str, int] = {}

    # Key idea: For each card, try folder candidates in order and download all rarities that exist for the *first folder* that yields at least 1 image.
    # This prevents massive warning spam across irrelevant folders.
    for i, cardno in enumerate(cardnos_norm, 1):
        folders = folder_candidates_for_cardno(cardno)

        saved_any_for_card = False
        chosen_folder = None

        for folder in folders:
            any_ok_in_folder = False
            folder_results: List[TryResult] = []

            for rarity in rarities:
                tr = download_one(
                    sess,
                    folder=folder,
                    cardno=cardno,
                    rarity=rarity,
                    outdir=outdir,
                    skip_existing=args.skip_existing,
                    timeout=args.timeout,
                    sleep=args.sleep,
                    jitter=args.jitter,
                    allow_insecure_fallback=allow_fallback,
                    state=state,
                )
                folder_results.append(tr)

                if tr.ok:
                    if tr.status == "SKIP_EXISTS":
                        skip_files += 1
                    else:
                        ok_files += 1
                    any_ok_in_folder = True
                    saved_any_for_card = True

                    if (not args.all_rarities) and tr.status != "SKIP_EXISTS":
                        # stop after first real download
                        break
                else:
                    fail_attempts += 1

                time.sleep(args.sleep + random.random() * args.jitter)

            # If this folder produced at least 1 image (downloaded or already existed), we accept this folder as the correct one.
            # Then we keep all folder_results (including failures) and stop trying other folders to reduce noise.
            if any_ok_in_folder:
                chosen_folder = folder
                results.extend(folder_results)
                break
            else:
                # Keep only *very limited* warnings, do not store all failures from wrong folders to avoid report bloat.
                # But if we're at the last folder candidate, store them for diagnostics.
                if folder == folders[-1]:
                    results.extend(folder_results)

                # Rate-limited warning on folder mismatch
                warn_by_card.setdefault(cardno, 0)
                if warn_total < args.max_warn_total and warn_by_card[cardno] < args.max_warn_per_card:
                    # show a single example URL from this folder
                    if folder_results:
                        ex = folder_results[0].url
                    else:
                        ex_remote = remote_filename_variants(folder, cardno, rarities[0])[0]
                        ex = build_url(folder, ex_remote)
                    print(f"[WARN] {cardno}: no images under folder={folder} (example {ex})")
                    warn_total += 1
                    warn_by_card[cardno] += 1

        if i % 100 == 0 or i == 1:
            print(f"[{i}/{len(cardnos_norm)}] ok_files={ok_files} skipped={skip_files} fail_attempts={fail_attempts} ...")

    # Write report
    report = {
        "root": str(root),
        "compiled": str(compiled_path),
        "outdir": str(outdir),
        "rarities": rarities,
        "counts": {
            "cards_total": len(cardnos_norm),
            "ok_files": ok_files,
            "skipped": skip_files,
            "fail_attempts": fail_attempts,
        },
        "notes": {
            "insecure_mode_used": bool(state.get("insecure_used", False) or state.get("insecure", False)),
            "strategy": "For each card: try likely folders; stop at first folder with any success; then try all rarities in that folder.",
        },
        "results": [tr.__dict__ for tr in results],
    }
    rep_path = outdir / "_download_report.json"
    rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Fail log: only actual failures (not SKIP_EXISTS)
    fail_lines: List[str] = []
    for tr in results:
        if (not tr.ok) and tr.status != "SKIP_EXISTS":
            fail_lines.append(f"{tr.cardno}\t{tr.folder}\t{tr.rarity}\t{tr.status}\t{tr.url}")
    fail_log = outdir / "_failures.log"
    fail_log.write_text("\n".join(fail_lines) + ("\n" if fail_lines else ""), encoding="utf-8")

    print("[DONE]")
    print("compiled :", compiled_path)
    print("outdir   :", outdir)
    print("rarities :", ", ".join(rarities))
    print("ok_files :", ok_files)
    print("skipped  :", skip_files)
    print("failed   :", len(fail_lines))
    print("report   :", rep_path)
    print("fail_log :", fail_log)

    if ok_files == 0 and skip_files == 0:
        print("[ERR] No files were downloaded or skipped. This usually means card list extraction failed or all URLs are unreachable.")
        print("      Check the report and failures log; also verify network/TLS on your environment.")
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
