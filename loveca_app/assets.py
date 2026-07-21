# BUILD_TAG = "ui_asset_bundle_glob_search_20260721a"
"""Install locally supplied Loveca UI assets.

The public GitHub package intentionally excludes downloaded card images.  Small
UI images such as playmat/back/NoImage/texticons can be distributed separately
and placed next to the application folder as ``loveca-ui-assets.zip``.
Date-suffixed bundles such as ``loveca-ui-assets-20260721.zip`` are also
accepted.
"""
from __future__ import annotations

import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path


BUILD_TAG = "ui_asset_bundle_glob_search_20260721a"

ASSET_BUNDLE_NAMES = (
    "loveca-ui-assets.zip",
    "loveca_ui_assets.zip",
)

ASSET_DIR_NAMES = (
    "loveca-ui-assets",
    "loveca_ui_assets",
)

ASSET_BUNDLE_PATTERNS = (
    "loveca-ui-assets*.zip",
    "loveca_ui_assets*.zip",
)

ASSET_DIR_PATTERNS = (
    "loveca-ui-assets*",
    "loveca_ui_assets*",
)

ALLOWED_ASSET_PATHS = {
    "playmat.jpg",
    "llocg_db_out_full/card_images/NoImage.PNG",
    "llocg_db_out_full/card_images/NoImage.png",
    "llocg_db_out_full/card_images/back.png",
    "llocg_db_out_full/card_images/back.jpg",
    "llocg_db_out_full/card_images/back.jpeg",
    "llocg_db_out_full/card_images/back.webp",
    "llocg_db_out_full/card_images/energy.png",
    "llocg_db_out_full/card_images/energy.jpg",
    "llocg_db_out_full/card_images/energy.jpeg",
    "llocg_db_out_full/card_images/energy.webp",
    "llocg_db_out_full/card_images/texticons/heart_00.png",
    "llocg_db_out_full/card_images/texticons/heart_01.png",
    "llocg_db_out_full/card_images/texticons/heart_02.png",
    "llocg_db_out_full/card_images/texticons/heart_03.png",
    "llocg_db_out_full/card_images/texticons/heart_04.png",
    "llocg_db_out_full/card_images/texticons/heart_05.png",
    "llocg_db_out_full/card_images/texticons/heart_06.png",
    "llocg_db_out_full/card_images/texticons/icon_all.png",
    "llocg_db_out_full/card_images/texticons/icon_any.png",
    "llocg_db_out_full/card_images/texticons/icon_blade.png",
}


@dataclass
class AssetInstallResult:
    source: str = ""
    installed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.installed)


def _canonical_asset_rel(raw: str) -> str:
    rel = str(raw or "").replace("\\", "/").lstrip("/")
    parts = [p for p in rel.split("/") if p and p != "."]
    if not parts or any(p == ".." for p in parts):
        return ""
    if parts[0] in ASSET_DIR_NAMES:
        parts = parts[1:]
    if parts[:1] == ["loveca"]:
        parts = parts[1:]
    rel = "/".join(parts)
    if rel.startswith("card_images/"):
        rel = "llocg_db_out_full/" + rel
    return rel


def _install_bytes(root: Path, rel: str, data: bytes, result: AssetInstallResult) -> None:
    canon = _canonical_asset_rel(rel)
    if not canon or canon not in ALLOWED_ASSET_PATHS:
        result.skipped.append(str(rel))
        return
    target = root / canon
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() == data:
            result.skipped.append(canon)
            return
        target.write_bytes(data)
        result.installed.append(canon)
    except Exception as exc:
        result.errors.append(f"{canon}: {type(exc).__name__}: {exc}")


def _install_from_zip(root: Path, bundle: Path) -> AssetInstallResult:
    result = AssetInstallResult(source=str(bundle))
    try:
        with zipfile.ZipFile(bundle) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                canon = _canonical_asset_rel(info.filename)
                if not canon or canon not in ALLOWED_ASSET_PATHS:
                    result.skipped.append(info.filename)
                    continue
                _install_bytes(root, canon, zf.read(info), result)
    except Exception as exc:
        result.errors.append(f"{type(exc).__name__}: {exc}")
    return result


def _install_from_dir(root: Path, folder: Path) -> AssetInstallResult:
    result = AssetInstallResult(source=str(folder))
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(folder).as_posix()
            _install_bytes(root, rel, path.read_bytes(), result)
        except Exception as exc:
            result.errors.append(f"{path}: {type(exc).__name__}: {exc}")
    return result


def ensure_image_directories(root: Path) -> None:
    for rel in (
        "llocg_db_out_full/card_images",
        "llocg_db_out_full/card_images/texticons",
        "llocg_db_out_full/preview_card_images",
    ):
        (Path(root) / rel).mkdir(parents=True, exist_ok=True)


def _asset_search_dirs(root: Path) -> list[Path]:
    candidates = [
        root,
        root.parent,
        Path.cwd(),
        Path.home() / "Downloads",
    ]
    seen: set[Path] = set()
    out: list[Path] = []
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except Exception:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        out.append(resolved)
    return out


def _sorted_existing(paths: list[Path]) -> list[Path]:
    def key(path: Path) -> tuple[float, str]:
        try:
            return (-path.stat().st_mtime, path.name)
        except OSError:
            return (0.0, path.name)

    return sorted(paths, key=key)


def _find_asset_bundles(search_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    seen: set[Path] = set()
    for name in ASSET_BUNDLE_NAMES:
        path = search_dir / name
        if path.is_file():
            resolved = path.resolve()
            seen.add(resolved)
            candidates.append(path)
    for pattern in ASSET_BUNDLE_PATTERNS:
        for path in search_dir.glob(pattern):
            if not path.is_file():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            candidates.append(path)
    return _sorted_existing(candidates)


def _find_asset_dirs(search_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    seen: set[Path] = set()
    for name in ASSET_DIR_NAMES:
        path = search_dir / name
        if path.is_dir():
            resolved = path.resolve()
            seen.add(resolved)
            candidates.append(path)
    for pattern in ASSET_DIR_PATTERNS:
        for path in search_dir.glob(pattern):
            if not path.is_dir():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            candidates.append(path)
    return _sorted_existing(candidates)


def ensure_ui_assets_from_local_bundle(root: Path) -> AssetInstallResult:
    """Install UI assets from a local bundle beside the application root.

    The function is intentionally quiet and local-only.  It never downloads
    anything; it only copies whitelisted image files from a user-supplied bundle.
    """
    root = Path(root)
    ensure_image_directories(root)
    for search_dir in _asset_search_dirs(root):
        for bundle in _find_asset_bundles(search_dir):
            return _install_from_zip(root, bundle)
        for folder in _find_asset_dirs(search_dir):
            return _install_from_dir(root, folder)
    return AssetInstallResult()


def build_ui_asset_bundle(root: Path, output: Path) -> Path:
    """Build the separate directly-distributed UI asset bundle."""
    root = Path(root)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    candidates = [
        root / "playmat.jpg",
        root / "llocg_db_out_full" / "card_images" / "NoImage.PNG",
        root / "llocg_db_out_full" / "card_images" / "back.png",
        root / "llocg_db_out_full" / "card_images" / "energy.png",
    ]
    texticon_dir = root / "llocg_db_out_full" / "card_images" / "texticons"
    if texticon_dir.exists():
        candidates.extend(sorted(texticon_dir.glob("*")))

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in candidates:
            if not path.is_file():
                continue
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                continue
            if _canonical_asset_rel(rel) not in ALLOWED_ASSET_PATHS:
                continue
            zf.write(path, "loveca-ui-assets/" + rel)
    return output
