#!/usr/bin/env python3
# BUILD_TAG = "loveca_seed_http_cache_distribution_20260721a"
"""Build a pruned Loveca Application distribution zip."""
from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
import zipfile
from datetime import datetime
from pathlib import Path


BUILD_TAG = "loveca_seed_http_cache_distribution_20260721a"


RUNTIME_INCLUDE_DIRS = (
    "llocg_dual_v2",
    "llocg_ext",
    "llocg_ui",
    "loveca_app",
    "manual_overrides",
    "tools",
)

SOURCE_DOC_DIRS = (
    "docs/debug",
    "docs/handoffs",
    "docs/notes",
)

DEFAULT_INCLUDE_FILES = (
    "README.md",
    "LLCrule251121.pdf",
    "llocg_build_preview_manifest_from_x.py",
    "llocg_db_tool_v7.py",
    "llocg_deckcode_to_decklist.py",
    "llocg_fetch_all_card_images.py",
    "llocg_fetch_decklog_by_code.py",
    "llocg_sim_tool_v7.py",
    "llocg_update_database.py",
    "refresh_loveca_product_catalog.py",
    "run_llocg_dual_v2.py",
    "run_llocg_ui_web.py",
    "run_loveca_app.py",
    "launch_loveca.command",
    "launch_loveca.bat",
)

SOURCE_ONLY_FILES = (
    "AGENTS.md",
)

DB_INCLUDE = (
    "cards_min_tokv1.csv",
    "cards_min_tokv1.json",
    "cards_compiled_v7h.json",
    "official_image_manifest.json",
    "official_preview_image_manifest.json",
    "product_catalog.json",
    "product_release_registry.json",
    "_http_cache",
    "decklists",
)

EXCLUDED_DIR_NAMES = {
    ".git",
    ".cache_llocg",
    ".venv",
    "__pycache__",
    "_http_cache",
    "_update_work",
    "_update_backups",
    "jank",
    "loveca_reports",
    "remote_sessions",
    "runtime",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".bak",
    ".zip",
    ".DS_Store",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


if str(project_root()) not in sys.path:
    sys.path.insert(0, str(project_root()))

from loveca_app.assets import build_ui_asset_bundle


def should_skip(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    if any(part in EXCLUDED_DIR_NAMES for part in rel_parts):
        return True
    name = path.name
    if name == ".DS_Store":
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return True
    if name.endswith(".zip"):
        return True
    return False


def add_file(zf: zipfile.ZipFile, root: Path, path: Path, package_root: str) -> None:
    if not path.is_file() or should_skip(path, root):
        return
    arcname = Path(package_root) / path.relative_to(root)
    zinfo = zipfile.ZipInfo(str(arcname).replace(os.sep, "/"))
    zinfo.date_time = datetime.fromtimestamp(path.stat().st_mtime).timetuple()[:6]
    mode = path.stat().st_mode
    if path.name.endswith(".command") or mode & stat.S_IXUSR:
        zinfo.external_attr = (0o755 & 0xFFFF) << 16
    else:
        zinfo.external_attr = (0o644 & 0xFFFF) << 16
    zf.writestr(zinfo, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)


def add_tree(zf: zipfile.ZipFile, root: Path, base: Path, package_root: str) -> None:
    if not base.exists():
        return
    for path in sorted(base.rglob("*")):
        add_file(zf, root, path, package_root)


def add_http_cache_tree(zf: zipfile.ZipFile, root: Path, base: Path, package_root: str) -> None:
    if not base.exists() or not base.is_dir():
        return
    allowed_suffixes = {".html", ".json", ".txt"}
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if path.name == ".DS_Store" or path.suffix.lower() not in allowed_suffixes:
            continue
        arcname = Path(package_root) / path.relative_to(root)
        zinfo = zipfile.ZipInfo(str(arcname).replace(os.sep, "/"))
        zinfo.date_time = datetime.fromtimestamp(path.stat().st_mtime).timetuple()[:6]
        zinfo.external_attr = (0o644 & 0xFFFF) << 16
        zf.writestr(zinfo, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)


def build(output: Path, *, include_docs: bool = True, target: str = "source") -> Path:
    root = project_root()
    package_root = "loveca"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    selected_target = str(target or "source").strip().lower()
    if selected_target not in {"source", "macos", "windows"}:
        raise ValueError("target must be source, macos, or windows")

    if selected_target in {"macos", "windows"} and include_docs:
        include_docs = False

    include_dirs = list(RUNTIME_INCLUDE_DIRS)
    if include_docs:
        include_dirs.extend(SOURCE_DOC_DIRS)

    include_files = list(DEFAULT_INCLUDE_FILES)
    if selected_target == "source":
        include_files.extend(SOURCE_ONLY_FILES)
    if selected_target == "macos":
        include_files = [item for item in include_files if item != "launch_loveca.bat"]
    elif selected_target == "windows":
        include_files = [item for item in include_files if item != "launch_loveca.command"]

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in include_files:
            add_file(zf, root, root / rel, package_root)

        for rel in include_dirs:
            add_tree(zf, root, root / rel, package_root)

        db_root = root / "llocg_db_out_full"
        for rel in DB_INCLUDE:
            path = db_root / rel
            if rel == "_http_cache" and path.is_dir():
                add_http_cache_tree(zf, root, path, package_root)
            elif path.is_dir():
                add_tree(zf, root, path, package_root)
            else:
                add_file(zf, root, path, package_root)

    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Loveca distribution zip")
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root() / "_codex_outputs" / "loveca_distribution.zip",
    )
    parser.add_argument("--no-docs", action="store_true")
    parser.add_argument(
        "--include-docs",
        action="store_true",
        help="Include development/debug docs. Ignored for macos/windows release zips.",
    )
    parser.add_argument(
        "--target",
        choices=("source", "macos", "windows", "ui-assets"),
        default="source",
        help="Prune launcher files for a target platform, or build the separate UI asset bundle",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if str(args.target) == "ui-assets":
        out = build_ui_asset_bundle(project_root(), args.output.expanduser().resolve())
        print("[LOVECA DIST] BUILD_TAG={}".format(BUILD_TAG))
        print("[LOVECA DIST] target ui-assets")
        print("[LOVECA DIST] wrote {}".format(out))
        print("[LOVECA DIST] place this zip beside the downloaded Loveca app folder before launch")
        return 0
    include_docs = args.include_docs or (str(args.target) == "source" and not args.no_docs)
    if args.no_docs:
        include_docs = False
    out = build(
        args.output.expanduser().resolve(),
        include_docs=include_docs,
        target=str(args.target),
    )
    print("[LOVECA DIST] BUILD_TAG={}".format(BUILD_TAG))
    print("[LOVECA DIST] target {}".format(args.target))
    print("[LOVECA DIST] wrote {}".format(out))
    if args.target == "windows":
        print("[LOVECA DIST] start: unzip, then double-click launch_loveca.bat")
    elif args.target == "macos":
        print("[LOVECA DIST] start: unzip, then double-click launch_loveca.command")
    else:
        print("[LOVECA DIST] start: unzip, then use launch_loveca.command or launch_loveca.bat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
