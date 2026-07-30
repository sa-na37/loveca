#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-command Loveca database + image updater.

Pipeline:
  1. incremental wiki scrape seeded from canonical raw DB by default
     (full existing-card rescan only with --full-refresh)
  2. merge fresh records with canonical old-only records (fresh wins)
  3. normalize / mine / audit
  4. incrementally update official image manifest for changed/released cards
  5. compile simulator DB
  6. strict five-file cardnumber generation audit
  7. backup and publish canonical DB files
  8. use the WIKIWIKI 公式ポスト aggregate index to build preview manifest
  9. fetch canonical + preview images only for changed card targets
 10. final strict generation audit

BUILD_TAG is intentionally visible for delivery verification.
"""

from __future__ import annotations

BUILD_TAG = "preview_index_freshness_20260729a"

import argparse
import csv
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

RARITY_SUFFIXES = {
    "SD", "CL", "N", "R", "R2", "L", "L2", "PR", "PR2", "P", "P2",
    "SEC", "SEC2", "SECL", "SRL", "DUO", "AR", "RM", "RE", "PE", "PE2",
    "SECE", "LLE",
}
RARITY_ALIASES = {
    "R+": "R2", "R＋": "R2",
    "L+": "L2", "L＋": "L2",
    "P+": "P2", "P＋": "P2",
    "PE+": "PE2", "PE＋": "PE2",
    "SEC+": "SEC2", "SEC＋": "SEC2",
    "PR+": "PR2", "PR＋": "PR2",
}
REPRINT_IMAGE_RARITIES = {"RM", "SECL", "L2", "SRL"}
CARD_RARITY_TAIL_RE = re.compile(r"^(?P<base>.+?)[-_\s](?P<rarity>[A-Za-z0-9＋\+]{1,8})$")

PB_PREFIX_TO_PRODUCT = {
    "PL!HS": "PBHS",
    "PL!SP": "PBSP",
    "PL!S": "PBLS",
    "PL!LS": "PBLS",
    "PL!N": "PBnj",
    "PL!": "PBLL",
    "LL": "PBLL",
}
SD_PREFIX_TO_PRODUCT = {
    "PL!SP": "SPSD",
    "PL!N": "NSD",
    "PL!HS": "HSSD",
    "PL!LS": "LSSD",
    "PL!S": "SSD",
    "PL!": "PLSD",
}
CL_PREFIX_TO_PRODUCT = {"PL!HS": "CLHS"}

CANONICAL_DB_FILES = [
    "cards_min.csv",
    "cards_min.json",
    "cards_min_tokv1.csv",
    "cards_min_tokv1.json",
    "cards_compiled_v7h.json",
]

PUBLISH_OPTIONAL_FILES = [
    "official_image_manifest.json",
    "official_image_manifest.tsv",
    "product_release_registry.json",
    "product_release_registry_audit.tsv",
    "product_catalog.json",
    "cardnumber_canonicalization_audit_normalize_csv.tsv",
    "cardnumber_canonicalization_audit_normalize_csv.json",
    "cardnumber_canonicalization_audit_normalize_json.tsv",
    "cardnumber_canonicalization_audit_normalize_json.json",
    "field_validation_corrections.tsv",
    "field_validation_corrections.json",
    "field_validation_unresolved.tsv",
    "field_validation_unresolved.json",
    "field_validation_corrections_scrape_finalize.tsv",
    "field_validation_corrections_scrape_finalize.json",
    "field_validation_unresolved_scrape_finalize.tsv",
    "field_validation_unresolved_scrape_finalize.json",
    "field_validation_summary.tsv",
    "field_validation_summary.json",
    "field_validation_summary_scrape_finalize.tsv",
    "field_validation_summary_scrape_finalize.json",
    "field_validation_idempotence_failures.tsv",
    "field_validation_idempotence_failures.json",
    "field_validation_idempotence_failures_scrape_finalize.tsv",
    "field_validation_idempotence_failures_scrape_finalize.json",
]

UPDATE_PYTHON_PACKAGES = [
    ("requests", "requests"),
    ("bs4", "beautifulsoup4"),
    ("lxml", "lxml"),
    ("pandas", "pandas"),
    ("yaml", "PyYAML"),
]


def console_python_executable() -> str:
    exe = sys.executable or ""
    if os.name == "nt" and os.path.basename(exe).lower() == "pythonw.exe":
        candidate = os.path.join(os.path.dirname(exe), "python.exe")
        if os.path.exists(candidate):
            return candidate
    return sys.executable or "python3"


def no_window_subprocess_kwargs() -> Dict[str, Any]:
    if os.name != "nt":
        return {}
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return {"creationflags": flags} if flags else {}


def unbuffered_python_command(cmd: Sequence[str]) -> List[str]:
    parts = [str(x) for x in cmd]
    if len(parts) < 2:
        return parts
    exe_name = os.path.basename(parts[0]).lower()
    if exe_name not in {"python", "python.exe", "python3", "python3.exe"}:
        return parts
    if parts[1] == "-u":
        return parts
    if parts[1].lower().endswith(".py"):
        return [parts[0], "-u", *parts[1:]]
    return parts


def run(cmd: Sequence[str], *, cwd: Path, env: Dict[str, str] | None = None) -> None:
    actual_cmd = unbuffered_python_command(cmd)
    printable = " ".join(str(x) for x in actual_cmd)
    print(f"\n[RUN] {printable}")
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(
        actual_cmd,
        cwd=str(cwd),
        env=merged_env,
        check=False,
        **no_window_subprocess_kwargs(),
    )
    if result.returncode != 0:
        raise SystemExit(
            f"[ERROR] command failed with exit={result.returncode}: {printable}"
        )


def missing_update_python_packages() -> List[Tuple[str, str]]:
    missing: List[Tuple[str, str]] = []
    for module_name, package_name in UPDATE_PYTHON_PACKAGES:
        if importlib.util.find_spec(module_name) is None:
            missing.append((module_name, package_name))
    return missing


def install_update_python_packages(missing: Sequence[Tuple[str, str]]) -> None:
    package_names = [package_name for _module_name, package_name in missing]
    if not package_names:
        return

    print(
        "[PY-DEPS] Missing Python packages for data update: "
        + ", ".join(package_names)
    )
    print("[PY-DEPS] Installing required packages with pip. This may take a few minutes.")

    pip_check = subprocess.run(
        [console_python_executable(), "-m", "pip", "--version"],
        check=False,
        **no_window_subprocess_kwargs(),
    )
    if pip_check.returncode != 0:
        print("[PY-DEPS] pip is not available. Trying ensurepip...")
        ensurepip = subprocess.run(
            [console_python_executable(), "-m", "ensurepip", "--upgrade"],
            check=False,
            **no_window_subprocess_kwargs(),
        )
        if ensurepip.returncode != 0:
            raise SystemExit(
                "[ERROR] pip is not available and ensurepip failed. "
                "Install Python with pip enabled, then run update again."
            )

    base_cmd = [
        console_python_executable(),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        *package_names,
    ]
    result = subprocess.run(base_cmd, check=False, **no_window_subprocess_kwargs())
    if result.returncode != 0:
        user_cmd = [
            console_python_executable(),
            "-m",
            "pip",
            "install",
            "--user",
            "--disable-pip-version-check",
            *package_names,
        ]
        print("[PY-DEPS] normal install failed. Retrying with --user...")
        result = subprocess.run(user_cmd, check=False, **no_window_subprocess_kwargs())
        if result.returncode != 0:
            raise SystemExit(
                "[ERROR] failed to install required Python packages: "
                + ", ".join(package_names)
            )

    still_missing = missing_update_python_packages()
    if still_missing:
        raise SystemExit(
            "[ERROR] Python packages were installed but still cannot be imported: "
            + ", ".join(package_name for _module, package_name in still_missing)
        )
    print("[PY-DEPS] required Python packages are ready.")


def ensure_update_python_dependencies(*, allow_install: bool) -> None:
    missing = missing_update_python_packages()
    if not missing:
        print("[PY-DEPS] required Python packages are already available.")
        return
    if not allow_install:
        raise SystemExit(
            "[ERROR] missing required Python packages: "
            + ", ".join(package_name for _module, package_name in missing)
            + ". Re-run without --skip-dependency-install to install them automatically."
        )
    install_update_python_packages(missing)


def canonical_cardnumber(value: str) -> Tuple[str, str]:
    cardno = str(value or "").strip()
    m = re.match(r"^(.*)-([A-Za-z0-9]+)$", cardno)
    if not m:
        return cardno, ""
    suffix = m.group(2).upper()
    if suffix not in RARITY_SUFFIXES:
        return cardno, ""
    base = m.group(1)
    if (
        re.search(r"-(?:bp|pb|sd|cl)\d+-\d+$", base, flags=re.IGNORECASE)
        or re.search(r"-PR-\d+$", base, flags=re.IGNORECASE)
    ):
        return base, suffix
    return cardno, ""


def load_json_rows(path: Path) -> List[Dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, list):
        return [dict(x) for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict) and isinstance(obj.get("cards"), list):
        return [dict(x) for x in obj["cards"] if isinstance(x, dict)]
    raise ValueError(f"expected list/card-list JSON: {path}")


def canonicalize_rows(
    rows: Iterable[Dict[str, Any]],
    *,
    source_label: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    out: List[Dict[str, Any]] = []
    audit: List[Dict[str, str]] = []
    for raw in rows:
        row = dict(raw)
        source = str(row.get("cardnumber", "") or "").strip()
        canonical, rarity = canonical_cardnumber(source)
        if source and canonical != source:
            row["cardnumber"] = canonical
            audit.append(
                {
                    "source": source_label,
                    "source_cardnumber": source,
                    "canonical_cardnumber": canonical,
                    "rarity_suffix": rarity,
                }
            )
        out.append(row)
    return out, audit


def merge_rows(
    *,
    old_rows: Sequence[Dict[str, Any]],
    fresh_rows: Sequence[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    old_numbers: set[str] = set()
    fresh_numbers: set[str] = set()

    for row in old_rows:
        cardno = str(row.get("cardnumber", "") or "").strip()
        if not cardno:
            continue
        old_numbers.add(cardno)
        merged[cardno] = dict(row)

    for row in fresh_rows:
        cardno = str(row.get("cardnumber", "") or "").strip()
        if not cardno:
            continue
        fresh_numbers.add(cardno)
        merged[cardno] = dict(row)

    ordered = [merged[key] for key in sorted(merged)]
    audit = {
        "old_count": len(old_numbers),
        "fresh_count": len(fresh_numbers),
        "merged_count": len(merged),
        "fresh_only": sorted(fresh_numbers - old_numbers),
        "old_only_preserved": sorted(old_numbers - fresh_numbers),
        "overlap_fresh_wins": len(old_numbers & fresh_numbers),
    }
    return ordered, audit


def write_rows_csv(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    fieldnames: List[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_rows_json(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(list(rows), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_merge_audit(
    workdir: Path,
    *,
    merge_audit: Dict[str, Any],
    canonicalization_audit: Sequence[Dict[str, str]],
) -> None:
    payload = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "merge": merge_audit,
        "cardnumber_canonicalization": list(canonicalization_audit),
    }
    (workdir / "db_update_merge_audit.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    path = workdir / "db_update_merge_audit.tsv"
    with path.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "kind",
            "source",
            "source_cardnumber",
            "canonical_cardnumber",
            "rarity_suffix",
        ]
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for row in canonicalization_audit:
            writer.writerow({"kind": "CARDNUMBER_CANONICALIZE", **row})
        for cardno in merge_audit["old_only_preserved"]:
            writer.writerow(
                {
                    "kind": "OLD_ONLY_PRESERVED",
                    "source": "canonical",
                    "source_cardnumber": cardno,
                    "canonical_cardnumber": cardno,
                    "rarity_suffix": "",
                }
            )
        for cardno in merge_audit["fresh_only"]:
            writer.writerow(
                {
                    "kind": "FRESH_ONLY",
                    "source": "fresh",
                    "source_cardnumber": cardno,
                    "canonical_cardnumber": cardno,
                    "rarity_suffix": "",
                }
            )


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)



def load_json_object(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return obj if isinstance(obj, dict) else {}


def write_product_catalog_from_registry(
    registry_path: Path,
    output_path: Path,
) -> Path:
    """Generate the app-facing expansion catalogue from the DB product registry.

    No extra network request is made here. The registry is produced during the
    normal DB scrape from the already-fetched product pages, so product names,
    release dates, and source URLs stay in the same audited generation.
    """
    registry = load_json_object(registry_path)
    products_raw = registry.get("products", {}) if isinstance(registry, dict) else {}
    if not isinstance(products_raw, dict):
        raise SystemExit(f"[ERROR] invalid product registry: {registry_path}")

    products: Dict[str, Dict[str, Any]] = {}
    for raw_code, raw in products_raw.items():
        if not isinstance(raw, dict):
            continue
        code = str(raw_code or "").strip().upper()
        title = str(raw.get("title", "") or "").strip()
        if not code:
            continue
        products[code] = {
            "name": title or code,
            "title": title or code,
            "release_date": str(raw.get("release_date", "") or "").strip(),
            "source_url": str(raw.get("source_url", "") or "").strip(),
            "card_link_count": int(raw.get("card_link_count", 0) or 0),
        }

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(),
        "source": "product_release_registry.json",
        "products": dict(sorted(products.items())),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"[PRODUCT-CATALOG] products={len(products)} "
        f"source={registry_path} output={output_path}"
    )
    return output_path


def cardnumber_set(rows: Sequence[Dict[str, Any]]) -> set[str]:
    return {
        str(row.get("cardnumber", "") or "").strip()
        for row in rows
        if str(row.get("cardnumber", "") or "").strip()
    }


def product_code_for_cardno(cardno: str) -> str:
    value = str(cardno or "").strip()
    prefix = value.split("-", 1)[0]
    m = re.search(r"(?:^|-)bp(\d+)(?:-|$)", value, flags=re.IGNORECASE)
    if m:
        return f"BP{int(m.group(1)):02d}"
    m = re.search(r"(?:^|-)pb(\d+)(?:-|$)", value, flags=re.IGNORECASE)
    if m:
        base = PB_PREFIX_TO_PRODUCT.get(prefix, "")
        if base:
            number = int(m.group(1))
            return base if number == 1 else f"{base}{number:02d}"
    m = re.search(r"(?:^|-)sd(\d+)(?:-|$)", value, flags=re.IGNORECASE)
    if m:
        base = SD_PREFIX_TO_PRODUCT.get(prefix, "")
        if base:
            return f"{base}{int(m.group(1)):02d}"
    m = re.search(r"(?:^|-)cl(\d+)(?:-|$)", value, flags=re.IGNORECASE)
    if m:
        base = CL_PREFIX_TO_PRODUCT.get(prefix, "")
        if base:
            return f"{base}{int(m.group(1)):02d}"
    if re.search(r"-PR-\d+(?:-|$)", value, flags=re.IGNORECASE):
        return "PR"
    return ""


def load_release_dates(registry_path: Path) -> Dict[str, date]:
    obj = load_json_object(registry_path)
    products = obj.get("products", {}) if isinstance(obj, dict) else {}
    out: Dict[str, date] = {}
    if not isinstance(products, dict):
        return out
    for code, raw in products.items():
        if not isinstance(raw, dict):
            continue
        value = str(raw.get("release_date", "") or "").strip()
        try:
            out[str(code).strip().upper()] = date.fromisoformat(value)
        except ValueError:
            continue
    return out


def is_prerelease_card(cardno: str, *, release_dates: Dict[str, date], as_of: date) -> bool:
    product = product_code_for_cardno(cardno)
    release_day = release_dates.get(product)
    return bool(release_day and as_of < release_day)


def normalize_rarity_token(value: str) -> str:
    rarity = str(value or "").strip().upper().replace("＋", "+")
    return RARITY_ALIASES.get(rarity, rarity)


def split_display_card_and_rarity(value: str) -> Tuple[str, str]:
    raw = str(value or "").strip()
    match = CARD_RARITY_TAIL_RE.match(raw)
    if not match:
        return raw, ""
    rarity = normalize_rarity_token(match.group("rarity"))
    if rarity not in RARITY_SUFFIXES:
        return raw, ""
    return match.group("base").strip(), rarity


def scan_image_cardnumbers(root: Path) -> set[str]:
    """Scan an image tree once and recover canonical cardnumbers from filenames."""
    if not root.is_dir():
        return set()
    pattern = re.compile(
        r"^(.+-(?:bp|pb|sd|cl)\d+-\d{3}|.+-PR-\d{3})-",
        flags=re.IGNORECASE,
    )
    out: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        match = pattern.match(path.stem)
        if match:
            canonical, _rarity = canonical_cardnumber(match.group(1))
            out.add(canonical)
    return out


def manifest_cardnumbers(path: Path) -> set[str]:
    cards = _manifest_cards(path)
    out: set[str] = set()
    for cardno0 in cards.keys():
        cardno, _rarity = canonical_cardnumber(str(cardno0 or "").strip())
        if cardno:
            out.add(cardno)
    return out


def scan_image_rarity_pairs(root: Path) -> set[Tuple[str, str]]:
    if not root.is_dir():
        return set()
    pattern = re.compile(
        r"^(.+-(?:bp|pb|sd|cl)\d+-\d{3}|.+-PR-\d{3})-([A-Za-z0-9]+)$",
        flags=re.IGNORECASE,
    )
    out: set[Tuple[str, str]] = set()
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        match = pattern.match(path.stem)
        if not match:
            continue
        canonical, _old_rarity = canonical_cardnumber(match.group(1))
        rarity = normalize_rarity_token(match.group(2))
        if rarity:
            out.add((canonical, rarity))
    return out


def missing_released_image_targets(
    *,
    cardnumbers: Iterable[str],
    image_root: Path,
    release_dates: Dict[str, date],
    as_of: date,
) -> set[str]:
    existing = scan_image_cardnumbers(image_root)
    out: set[str] = set()
    for cardno0 in cardnumbers:
        cardno = str(cardno0 or "").strip()
        if not cardno:
            continue
        if is_prerelease_card(cardno, release_dates=release_dates, as_of=as_of):
            continue
        if cardno not in existing:
            out.add(cardno)
    return out


def cached_reprint_image_targets(
    *,
    cache_dir: Path,
    wanted_cardnumbers: Iterable[str],
    existing_pairs: set[Tuple[str, str]],
) -> set[str]:
    if not cache_dir.is_dir():
        return set()
    try:
        from bs4 import BeautifulSoup
    except Exception:
        return set()

    wanted = {str(cardno or "").strip() for cardno in wanted_cardnumbers if str(cardno or "").strip()}
    needles = tuple(f"-{rarity}.png" for rarity in REPRINT_IMAGE_RARITIES)
    out: set[str] = set()
    candidate_count = 0

    for path in sorted(cache_dir.glob("*.html")):
        try:
            html = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if not any(needle in html for needle in needles):
            continue
        soup = BeautifulSoup(html, "lxml")
        for node in soup.select("[card]"):
            cardno, rarity = split_display_card_and_rarity(str(node.get("card") or ""))
            cardno = cardno.strip()
            rarity = normalize_rarity_token(rarity)
            if cardno not in wanted or rarity not in REPRINT_IMAGE_RARITIES:
                continue
            img = node.find("img")
            src = str(img.get("src") or "") if img else ""
            if not src or not any(needle in src for needle in needles):
                continue
            candidate_count += 1
            if (cardno, rarity) not in existing_pairs:
                out.add(cardno)

    print(
        "[REPRINT-IMAGE-TARGETS] "
        f"cached_candidates={candidate_count} missing_cards={len(out)}"
    )
    return out


def write_cardnumber_file(path: Path, cardnumbers: Iterable[str]) -> Path:
    values = sorted({str(x).strip() for x in cardnumbers if str(x).strip()})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{value}\n" for value in values), encoding="utf-8")
    return path


def _manifest_cards(path: Path) -> Dict[str, Any]:
    obj = load_json_object(path)
    cards = obj.get("cards", {}) if isinstance(obj, dict) else {}
    return cards if isinstance(cards, dict) else {}


def merge_official_image_manifests(
    *,
    base_path: Path,
    delta_path: Path,
    outdir: Path,
    all_cardnumbers: Iterable[str],
) -> Path:
    base = load_json_object(base_path)
    delta = load_json_object(delta_path)
    payload: Dict[str, Any] = dict(base) if base else {
        "version": 1,
        "source": "official_cardlist",
        "base_url": "https://llofficial-cardgame.com/wordpress/wp-content/images/cardlist",
    }
    cards: Dict[str, List[Dict[str, Any]]] = {}

    def merge_cards(source: Dict[str, Any]) -> None:
        raw_cards = source.get("cards", {}) if isinstance(source, dict) else {}
        if not isinstance(raw_cards, dict):
            return
        for cardno, entries in raw_cards.items():
            if not isinstance(entries, list):
                continue
            bucket = cards.setdefault(str(cardno), [])
            seen = {
                (
                    str(item.get("rarity_norm", "")),
                    str(item.get("remote_filename", "")),
                    str(item.get("folder", "")),
                    str(item.get("exact_url", "")),
                )
                for item in bucket
                if isinstance(item, dict)
            }
            for item in entries:
                if not isinstance(item, dict):
                    continue
                key = (
                    str(item.get("rarity_norm", "")),
                    str(item.get("remote_filename", "")),
                    str(item.get("folder", "")),
                    str(item.get("exact_url", "")),
                )
                if key not in seen:
                    bucket.append(dict(item))
                    seen.add(key)

    merge_cards(base)
    merge_cards(delta)
    all_numbers = sorted({str(x).strip() for x in all_cardnumbers if str(x).strip()})
    payload["cards"] = {cardno: cards[cardno] for cardno in sorted(cards) if cards[cardno]}
    payload["cards_total_in_db"] = len(all_numbers)
    payload["cards_with_manifest"] = len(payload["cards"])
    payload["cards_missing_manifest"] = len([x for x in all_numbers if x not in payload["cards"]])
    payload["generated_from"] = {
        "mode": "incremental_merge",
        "base_manifest": str(base_path) if base_path.exists() else "",
        "delta_manifest": str(delta_path) if delta_path.exists() else "",
    }
    expansions: Dict[str, Any] = {}
    for source in (base, delta):
        raw = source.get("expansions", {}) if isinstance(source, dict) else {}
        if isinstance(raw, dict):
            expansions.update(raw)
    payload["expansions"] = expansions

    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / "official_image_manifest.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fields = ["cardnumber", "rarity_norm", "rarity_display", "folder", "remote_filename", "exact_url"]
    with (outdir / "official_image_manifest.tsv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for cardno in sorted(payload["cards"]):
            for entry in payload["cards"][cardno]:
                writer.writerow({"cardnumber": cardno, **{key: entry.get(key, "") for key in fields if key != "cardnumber"}})
    return out_path


def changed_manifest_cardnumbers(before_path: Path, after_path: Path) -> set[str]:
    before = _manifest_cards(before_path)
    after = _manifest_cards(after_path)
    keys = set(before) | set(after)
    changed: set[str] = set()
    for key in keys:
        if before.get(key) != after.get(key):
            changed.add(str(key))
    return changed


def backup_canonical(dbdir: Path, backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    for name in CANONICAL_DB_FILES + PUBLISH_OPTIONAL_FILES:
        copy_if_exists(dbdir / name, backup_dir / name)
    for name in [
        "official_preview_image_manifest.json",
        "preview_x_post_cache.json",
        "preview_x_collection_state.json",
        "preview_x_match_audit.tsv",
        "preview_x_match_audit.json",
    ]:
        copy_if_exists(dbdir / name, backup_dir / name)


def publish_work(workdir: Path, dbdir: Path) -> None:
    for name in CANONICAL_DB_FILES:
        src = workdir / name
        if not src.exists():
            raise SystemExit(f"[ERROR] required work output missing: {src}")
        shutil.copy2(src, dbdir / name)
    for name in PUBLISH_OPTIONAL_FILES:
        copy_if_exists(workdir / name, dbdir / name)
    copy_if_exists(
        workdir / "db_update_merge_audit.json",
        dbdir / "db_update_merge_audit.json",
    )
    copy_if_exists(
        workdir / "db_update_merge_audit.tsv",
        dbdir / "db_update_merge_audit.tsv",
    )


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="One-command Loveca DB + card image updater"
    )
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument(
        "--dbdir",
        type=Path,
        default=Path("./llocg_db_out_full"),
    )
    ap.add_argument("--delay", type=float, default=5.0)
    ap.add_argument(
        "--max-429",
        type=int,
        default=6,
        help="Maximum consecutive HTTP 429 responses before the DB scraper stops safely",
    )
    ap.add_argument(
        "--http-cache-ttl-hours",
        type=float,
        default=24.0,
        help="Freshness window for cached WIKIWIKI product/card pages used by the DB scraper",
    )
    ap.add_argument(
        "--full-refresh",
        action="store_true",
        help=(
            "Rescan existing card pages too. Default operation is incremental: "
            "seed from canonical cards_min and fetch only newly discovered card pages."
        ),
    )
    ap.add_argument(
        "--full-image-refresh",
        action="store_true",
        help="Rebuild the official image manifest for every released card and fetch all image targets",
    )
    ap.add_argument(
        "--released-product-grace-days",
        type=int,
        default=7,
        help="Recheck product pages until this many days after release; stable older products reuse registry data",
    )
    ap.add_argument(
        "--product-page-cache-ttl-days",
        type=float,
        default=3650.0,
        help="Reuse cached WIKIWIKI product-page HTML for this many days during incremental updates",
    )
    ap.add_argument(
        "--preview-empty-recheck-hours",
        type=float,
        default=12.0,
        help="Recheck prerelease card pages with no official post only after this cache TTL",
    )
    ap.add_argument(
        "--preview-page-cache-ttl-hours",
        type=float,
        default=6.0,
        help=(
            "Freshness window for rendered WIKIWIKI card-page HTML shared with "
            "the DB scraper; fresh cache is parsed without extra HTTP requests"
        ),
    )
    ap.add_argument(
        "--preview-index-cache-minutes",
        type=float,
        default=15.0,
        help=(
            "Freshness window for the one-page WIKIWIKI 公式ポスト index cache. "
            "The updater prefetches this page before DB crawling so the preview stage "
            "does not add WIKIWIKI requests after the scrape."
        ),
    )
    ap.add_argument(
        "--http-cache",
        type=Path,
        default=Path("./llocg_db_out_full/_http_cache"),
        help="Persistent HTTP cache reused across updater runs; default is under the DB directory",
    )
    ap.add_argument(
        "--clear-http-cache",
        action="store_true",
        help="Clear the persistent HTTP cache before updating",
    )
    ap.add_argument("--mine-top", type=int, default=200)
    ap.add_argument("--top-unknown", type=int, default=50)
    ap.add_argument("--image-timeout", type=float, default=20.0)
    ap.add_argument("--image-sleep", type=float, default=0.05)
    ap.add_argument("--image-jitter", type=float, default=0.05)
    ap.add_argument(
        "--skip-preview-posts",
        "--skip-x",
        dest="skip_preview_posts",
        action="store_true",
        help="Skip prerelease official-post discovery and preview manifest update",
    )
    ap.add_argument(
        "--require-preview-posts",
        "--require-x",
        dest="require_preview_posts",
        action="store_true",
        help="Fail if no prerelease official-post ID can be discovered/cached",
    )
    ap.add_argument(
        "--x-max-pages",
        type=int,
        default=10,
        help="Deprecated compatibility option; paid X API is not used by the normal updater",
    )
    ap.add_argument(
        "--keep-work",
        action="store_true",
        help="Keep work/cache directories after success",
    )
    ap.add_argument(
        "--skip-dependency-install",
        action="store_true",
        help="Do not install missing Python packages automatically before update",
    )
    return ap


def main() -> int:
    args = parser().parse_args()
    project_root = args.project_root.resolve()
    dbdir = (
        args.dbdir.resolve()
        if args.dbdir.is_absolute()
        else (project_root / args.dbdir).resolve()
    )
    dbdir.mkdir(parents=True, exist_ok=True)

    print(f"BUILD_TAG={BUILD_TAG}")
    ensure_update_python_dependencies(
        allow_install=not bool(args.skip_dependency_install)
    )
    python_exe = console_python_executable()

    db_tool = project_root / "llocg_db_tool_v7.py"
    sim_tool = project_root / "llocg_sim_tool_v7.py"
    x_builder = project_root / "llocg_build_preview_manifest_from_x.py"
    image_fetcher = project_root / "llocg_fetch_all_card_images.py"

    required_scripts = [db_tool, sim_tool, image_fetcher]
    missing = [str(path) for path in required_scripts if not path.exists()]
    if missing:
        raise SystemExit("[ERROR] missing required scripts: " + ", ".join(missing))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    work_parent = dbdir / "_update_work"
    backup_parent = dbdir / "_update_backups"
    work_root = work_parent / f"run_{stamp}"
    fresh_dir = work_root / "fresh"
    final_dir = work_root / "final"
    cache_dir = (
        args.http_cache.resolve()
        if args.http_cache.is_absolute()
        else (project_root / args.http_cache).resolve()
    )
    canonical_image_dir = dbdir / "card_images"
    preview_image_dir = dbdir / "preview_card_images"
    backup_dir = backup_parent / f"backup_{stamp}"
    work_parent.mkdir(parents=True, exist_ok=True)
    backup_parent.mkdir(parents=True, exist_ok=True)
    fresh_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)
    canonical_image_dir.mkdir(parents=True, exist_ok=True)
    preview_image_dir.mkdir(parents=True, exist_ok=True)
    if args.clear_http_cache:
        shutil.rmtree(cache_dir, ignore_errors=True)
        print(f"[CACHE] cleared persistent HTTP cache: {cache_dir}")
    cache_dir.mkdir(parents=True, exist_ok=True)

    print(f"project_root={project_root}")
    print(f"dbdir={dbdir}")
    print(f"work_root={work_root}")
    print(f"backup_dir={backup_dir}")
    print(f"http_cache={cache_dir}")

    preview_prefetch_failed = False

    # Prefetch the single WIKIWIKI 公式ポスト aggregate page before the DB crawl.
    # This prevents the preview stage from adding per-card WIKIWIKI requests after
    # a scrape, which previously caused repeated 429 responses. The builder cache
    # is reused later in the same updater run.
    if not args.skip_preview_posts and x_builder.exists():
        prefetch_cmd = [
            python_exe,
            str(x_builder),
            "--root",
            str(dbdir),
            "--prefetch-official-posts-only",
            "--official-posts-cache-minutes",
            str(max(0.0, args.preview_index_cache_minutes)),
        ]
        if args.require_preview_posts:
            prefetch_cmd.append("--require-discovered-posts")
        try:
            run(prefetch_cmd, cwd=project_root)
        except SystemExit:
            if args.require_preview_posts:
                raise
            preview_prefetch_failed = True
            print(
                "[PREVIEW-PREFETCH][WARN] official-post index prefetch failed; "
                "DB update will continue and the preview stage will be skipped this run",
                file=sys.stderr,
            )

    # 1. Incremental scrape by default. Seed the isolated work directory with
    # canonical *raw* DB files so the DB tool can skip already-known card page
    # source URLs. Product pages are still checked to discover newly listed cards
    # and rebuild the release registry. Existing card pages are only rescanned
    # when --full-refresh is explicitly requested.
    scrape_cmd = [
        python_exe,
        str(db_tool),
        "scrape",
        "--outdir",
        str(fresh_dir),
        "--cache",
        str(cache_dir),
        "--delay",
        str(args.delay),
        "--max-429",
        str(max(1, int(args.max_429))),
        "--cache-ttl-sec",
        str(max(0.0, float(args.http_cache_ttl_hours)) * 3600.0),
        "--released-product-grace-days",
        str(max(0, args.released_product_grace_days)),
        "--product-page-cache-ttl-days",
        str(max(0.0, float(args.product_page_cache_ttl_days))),
    ]

    if args.full_refresh:
        scrape_cmd.append("--fresh")
        print("[UPDATE-MODE] full-refresh: existing card pages will be rescanned")
    else:
        seeded = []
        for name in (
            "cards_min.csv",
            "cards_min.json",
            "product_release_registry.json",
            "product_release_registry_audit.tsv",
        ):
            src = dbdir / name
            if src.exists():
                shutil.copy2(src, fresh_dir / name)
                seeded.append(name)
        print(
            "[UPDATE-MODE] incremental: "
            "existing card pages are reused; only newly discovered card pages are fetched "
            f"seeded={','.join(seeded) if seeded else 'none'}"
        )

    run(scrape_cmd, cwd=project_root)

    fresh_json = fresh_dir / "cards_min.json"
    if not fresh_json.exists():
        raise SystemExit(f"[ERROR] fresh scrape output missing: {fresh_json}")

    # 2. Merge fresh with current canonical old-only records; fresh wins.
    old_source = dbdir / "cards_min_tokv1.json"
    if not old_source.exists():
        old_source = dbdir / "cards_min.json"

    fresh_rows_raw = load_json_rows(fresh_json)
    old_rows_raw = load_json_rows(old_source) if old_source.exists() else []

    fresh_rows, fresh_canon = canonicalize_rows(
        fresh_rows_raw,
        source_label="fresh",
    )
    old_rows, old_canon = canonicalize_rows(
        old_rows_raw,
        source_label="canonical",
    )
    merged_rows, merge_audit = merge_rows(
        old_rows=old_rows,
        fresh_rows=fresh_rows,
    )

    write_rows_csv(final_dir / "cards_min.csv", merged_rows)
    write_rows_json(final_dir / "cards_min.json", merged_rows)
    copy_if_exists(
        fresh_dir / "product_release_registry.json",
        final_dir / "product_release_registry.json",
    )
    copy_if_exists(
        fresh_dir / "product_release_registry_audit.tsv",
        final_dir / "product_release_registry_audit.tsv",
    )
    write_product_catalog_from_registry(
        final_dir / "product_release_registry.json",
        final_dir / "product_catalog.json",
    )
    write_merge_audit(
        final_dir,
        merge_audit=merge_audit,
        canonicalization_audit=[*old_canon, *fresh_canon],
    )

    print(
        "[MERGE] "
        f"old={merge_audit['old_count']} "
        f"fresh={merge_audit['fresh_count']} "
        f"merged={merge_audit['merged_count']} "
        f"old_only_preserved={len(merge_audit['old_only_preserved'])} "
        f"fresh_only={len(merge_audit['fresh_only'])}"
    )

    # 3. Normalize / mine / audit.
    run(
        [
            python_exe,
            str(db_tool),
            "normalize",
            "--csv",
            str(final_dir / "cards_min.csv"),
            "--json",
            str(final_dir / "cards_min.json"),
            "--outdir",
            str(final_dir),
            "--suffix",
            "_tokv1",
        ],
        cwd=project_root,
    )
    run(
        [
            python_exe,
            str(db_tool),
            "mine",
            "--csv",
            str(final_dir / "cards_min_tokv1.csv"),
            "--outdir",
            str(final_dir),
            "--top",
            str(args.mine_top),
        ],
        cwd=project_root,
    )
    run(
        [
            python_exe,
            str(db_tool),
            "audit",
            "--csv",
            str(final_dir / "cards_min_tokv1.csv"),
            "--top-unknown",
            str(args.top_unknown),
        ],
        cwd=project_root,
    )

    # 4. Incremental official exact-image manifest.
    # Normal updates do not rescan the full 1k-card DB.  Only newly added
    # released cards and preview-only cards whose product has now released are
    # checked.  A clean installation with no base manifest performs the initial
    # full released-card build.  --full-image-refresh is the explicit slow path.
    all_cardnumbers = cardnumber_set(merged_rows)
    new_cardnumbers = set(merge_audit["fresh_only"])
    release_dates = load_release_dates(final_dir / "product_release_registry.json")
    today = date.today()
    base_image_manifest = dbdir / "official_image_manifest.json"
    canonical_image_cards_at_start = scan_image_cardnumbers(canonical_image_dir)
    canonical_image_rarity_pairs_at_start = scan_image_rarity_pairs(canonical_image_dir)
    initial_image_fetch_needed = not canonical_image_cards_at_start
    missing_existing_image_targets = missing_released_image_targets(
        cardnumbers=all_cardnumbers,
        image_root=canonical_image_dir,
        release_dates=release_dates,
        as_of=today,
    )
    reprint_image_targets = cached_reprint_image_targets(
        cache_dir=cache_dir,
        wanted_cardnumbers=[
            cardno
            for cardno in all_cardnumbers
            if not is_prerelease_card(cardno, release_dates=release_dates, as_of=today)
        ],
        existing_pairs=canonical_image_rarity_pairs_at_start,
    )

    if args.full_image_refresh or not base_image_manifest.exists():
        image_manifest_targets = {
            cardno
            for cardno in all_cardnumbers
            if not is_prerelease_card(cardno, release_dates=release_dates, as_of=today)
        }
        image_manifest_mode = "full" if args.full_image_refresh else "initial"
    else:
        image_manifest_targets = {
            cardno
            for cardno in new_cardnumbers
            if not is_prerelease_card(cardno, release_dates=release_dates, as_of=today)
        }
        preview_image_cards = scan_image_cardnumbers(dbdir / "preview_card_images")
        canonical_image_cards = scan_image_cardnumbers(dbdir / "card_images")
        for cardno in all_cardnumbers:
            if is_prerelease_card(cardno, release_dates=release_dates, as_of=today):
                continue
            if cardno in preview_image_cards and cardno not in canonical_image_cards:
                image_manifest_targets.add(cardno)
        image_manifest_mode = "incremental"
    image_manifest_targets.update(missing_existing_image_targets)
    image_manifest_targets.update(reprint_image_targets)

    print(
        "[IMAGE-MANIFEST-MODE] "
        f"mode={image_manifest_mode} targets={len(image_manifest_targets)} "
        f"new_cards={len(new_cardnumbers)} "
        f"missing_existing={len(missing_existing_image_targets)} "
        f"reprint_missing={len(reprint_image_targets)} "
        f"base_manifest={base_image_manifest.exists()}"
    )
    if initial_image_fetch_needed:
        print(
            "[IMAGE-FETCH-INIT] canonical card image folder is missing or empty; "
            "first update will fetch card images using the bundled manifest"
        )
    if missing_existing_image_targets:
        sample = ", ".join(sorted(missing_existing_image_targets)[:30])
        print(
            "[IMAGE-MISSING-EXISTING] "
            f"released_cards_without_local_image={len(missing_existing_image_targets)} "
            f"sample={sample}"
        )

    image_manifest_delta_dir = work_root / "image_manifest_delta"
    delta_manifest = image_manifest_delta_dir / "official_image_manifest.json"
    if image_manifest_targets:
        image_manifest_delta_dir.mkdir(parents=True, exist_ok=True)
        subset_json = work_root / "image_manifest_target_cards.json"
        write_rows_json(
            subset_json,
            [{"cardnumber": cardno} for cardno in sorted(image_manifest_targets)],
        )
        run(
            [
                python_exe,
                str(db_tool),
                "image-manifest",
                "--json",
                str(subset_json),
                "--outdir",
                str(image_manifest_delta_dir),
                "--cache",
                str(cache_dir),
                "--delay",
                str(args.delay),
            ],
            cwd=project_root,
        )
    merge_official_image_manifests(
        base_path=base_image_manifest,
        delta_path=delta_manifest,
        outdir=final_dir,
        all_cardnumbers=all_cardnumbers,
    )

    # 5. Compile simulator DB.
    pattern_dir = dbdir / "patterns"
    if not pattern_dir.is_dir():
        pattern_dir = dbdir
    run(
        [
            python_exe,
            str(sim_tool),
            "compile",
            "--csv",
            str(final_dir / "cards_min_tokv1.csv"),
            "--out",
            str(final_dir / "cards_compiled_v7h.json"),
            "--patterns-dir",
            str(pattern_dir),
        ],
        cwd=project_root,
    )

    # 6. Strict five-file generation audit before publication.
    run(
        [
            python_exe,
            str(db_tool),
            "db-generation-audit",
            "--dbdir",
            str(final_dir),
            "--strict",
        ],
        cwd=project_root,
    )

    # 7. Publish canonical DB generation atomically enough for this local tool:
    # preserve full backup first, then copy a fully audited generation.
    backup_canonical(dbdir, backup_dir)
    publish_work(final_dir, dbdir)

    run(
        [
            python_exe,
            str(db_tool),
            "db-generation-audit",
            "--dbdir",
            str(dbdir),
            "--strict",
        ],
        cwd=project_root,
    )

    # 8. Free prerelease official-post discovery. No X API key/credits are
    # required: the WIKIWIKI 公式ポスト aggregate page directly pairs
    # cardnumber(+rarity) rows with X post URLs. The page was prefetched before
    # the DB crawl, so this stage normally uses local index cache and only fetches
    # uncached public X tweet-result JSON.
    preview_manifest_path = dbdir / "official_preview_image_manifest.json"
    preview_before_path = work_root / "preview_manifest_before.json"
    copy_if_exists(preview_manifest_path, preview_before_path)

    if not args.skip_preview_posts and x_builder.exists() and not preview_prefetch_failed:
        x_cmd = [
            python_exe,
            str(x_builder),
            "--root",
            str(dbdir),
            "--official-posts-cache-minutes",
            str(max(0.0, args.preview_index_cache_minutes)),
        ]
        if args.require_preview_posts:
            x_cmd.append("--require-discovered-posts")
        run(x_cmd, cwd=project_root)
    elif preview_prefetch_failed:
        print("[PREVIEW] skipped because aggregate-page prefetch failed earlier in this run")
    elif not args.skip_preview_posts and not x_builder.exists():
        if args.require_preview_posts:
            raise SystemExit(f"[ERROR] X preview builder missing: {x_builder}")
        print(f"[X][WARN] preview builder missing; skipped: {x_builder}")

    preview_changed_cards = changed_manifest_cardnumbers(
        preview_before_path,
        preview_manifest_path,
    )
    preview_manifest_cards = manifest_cardnumbers(preview_manifest_path)
    preview_image_cards_after_manifest = scan_image_cardnumbers(preview_image_dir)
    missing_preview_image_targets = {
        cardno
        for cardno in preview_manifest_cards
        if cardno in all_cardnumbers and cardno not in preview_image_cards_after_manifest
    }

    # 9. Fetch images only for cards that can have changed in this update.
    # Initial installs still target every newly created DB card.  Subsequent
    # spoiler updates normally target only a handful of new/preview-changed cards.
    image_fetch_targets = (
        set(new_cardnumbers)
        | set(image_manifest_targets)
        | set(preview_changed_cards)
        | set(missing_preview_image_targets)
        | set(reprint_image_targets)
        | set(missing_existing_image_targets)
    )
    if initial_image_fetch_needed:
        image_fetch_targets.update(all_cardnumbers)
    if args.full_image_refresh:
        image_fetch_targets = set(all_cardnumbers)

    print(
        "[IMAGE-FETCH-MODE] "
        f"targets={len(image_fetch_targets)} new_cards={len(new_cardnumbers)} "
        f"official_manifest_targets={len(image_manifest_targets)} "
        f"preview_changed={len(preview_changed_cards)} "
        f"missing_preview={len(missing_preview_image_targets)} "
        f"missing_existing={len(missing_existing_image_targets)}"
    )
    if missing_preview_image_targets:
        sample = ", ".join(sorted(missing_preview_image_targets)[:30])
        print(
            "[IMAGE-MISSING-PREVIEW] "
            f"preview_manifest_cards_without_local_image={len(missing_preview_image_targets)} "
            f"sample={sample}"
        )
    if image_fetch_targets:
        image_target_file = write_cardnumber_file(
            work_root / "image_fetch_targets.txt",
            image_fetch_targets,
        )
        run(
            [
                python_exe,
                str(image_fetcher),
                "--root",
                str(dbdir),
                "--compiled",
                str(dbdir / "cards_compiled_v7h.json"),
                "--cardnumber-file",
                str(image_target_file),
                "--outdir",
                str(dbdir / "card_images"),
                "--preview-outdir",
                str(dbdir / "preview_card_images"),
                "--timeout",
                str(args.image_timeout),
                "--sleep",
                str(args.image_sleep),
                "--jitter",
                str(args.image_jitter),
                "--progress-every",
                "1",
            ],
            cwd=project_root,
        )
    else:
        print("[IMAGE-FETCH] no changed card targets; skipped")

    missing_after_image_fetch = missing_released_image_targets(
        cardnumbers=all_cardnumbers,
        image_root=dbdir / "card_images",
        release_dates=release_dates,
        as_of=today,
    )
    if missing_after_image_fetch:
        sample = ", ".join(sorted(missing_after_image_fetch)[:30])
        print(
            "[IMAGE-FETCH-ERROR] "
            f"missing released card images after fetch: {len(missing_after_image_fetch)}"
        )
        print(f"[IMAGE-FETCH-ERROR] sample={sample}")
        raise SystemExit(
            "[ERROR] card image update incomplete; retry the update after confirming network access"
        )
    missing_preview_after_image_fetch = {
        cardno
        for cardno in manifest_cardnumbers(preview_manifest_path)
        if cardno in all_cardnumbers and cardno not in scan_image_cardnumbers(preview_image_dir)
    }
    if missing_preview_after_image_fetch:
        sample = ", ".join(sorted(missing_preview_after_image_fetch)[:30])
        print(
            "[IMAGE-FETCH-ERROR] "
            f"missing preview card images after fetch: {len(missing_preview_after_image_fetch)}"
        )
        print(f"[IMAGE-FETCH-ERROR] preview_sample={sample}")
        raise SystemExit(
            "[ERROR] preview card image update incomplete; retry the update after confirming network access"
        )

    # 10. Final strict generation audit.
    run(
        [
            python_exe,
            str(db_tool),
            "db-generation-audit",
            "--dbdir",
            str(dbdir),
            "--strict",
        ],
        cwd=project_root,
    )

    print("\n[DONE] Loveca DB + image update completed")
    print(f"canonical_db={dbdir}")
    print(f"backup={backup_dir}")
    print(f"work={work_root}")
    print(
        f"merged_cards={merge_audit['merged_count']} "
        f"old_only_preserved={len(merge_audit['old_only_preserved'])}"
    )

    if not args.keep_work:
        shutil.rmtree(work_root, ignore_errors=True)
        print("[CLEAN] removed work directory")
    print(f"[CACHE] preserved HTTP cache for next run: {cache_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
