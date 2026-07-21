#!/usr/bin/env python3
# BUILD_TAG = "loveca_distribution_launcher_20260721a"
"""Desktop launcher helpers for Loveca Application."""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from typing import Iterable


BUILD_TAG = "loveca_distribution_launcher_20260721a"


ROOT_MARKERS = (
    "run_loveca_app.py",
    "llocg_ui",
    "llocg_dual_v2",
    "llocg_db_out_full",
)


def find_project_root(start: Path | None = None) -> Path:
    """Find the Loveca project root from a script path or current directory."""
    candidates: list[Path] = []
    if start is not None:
        candidates.append(start)
    candidates.append(Path.cwd())
    candidates.append(Path(sys.argv[0]).resolve().parent)

    for base in candidates:
        current = base.resolve()
        if current.is_file():
            current = current.parent
        for path in (current, *current.parents):
            if all((path / marker).exists() for marker in ROOT_MARKERS):
                return path
    return Path(sys.argv[0]).resolve().parent


def _which_any(names: Iterable[str]) -> str:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return ""


def _macos_open_app_window(url: str, browser_app: str = "auto") -> bool:
    requested = str(browser_app or "auto").strip().lower()
    app_candidates: list[str]
    if requested in {"chrome", "google chrome"}:
        app_candidates = ["Google Chrome"]
    elif requested in {"edge", "microsoft edge"}:
        app_candidates = ["Microsoft Edge"]
    else:
        app_candidates = ["Google Chrome", "Microsoft Edge"]

    for app_name in app_candidates:
        try:
            subprocess.Popen(
                [
                    "open",
                    "-na",
                    app_name,
                    "--args",
                    "--app={}".format(url),
                    "--new-window",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except Exception:
            continue

    # Safari does not support Chromium's --app mode, but it is still a clean
    # separate window target on many user machines.
    if requested in {"auto", "safari"}:
        try:
            subprocess.Popen(
                ["open", "-na", "Safari", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except Exception:
            pass
    return False


def _windows_open_app_window(url: str, browser_app: str = "auto") -> bool:
    requested = str(browser_app or "auto").strip().lower()
    if requested in {"chrome", "google chrome"}:
        names = ("chrome.exe", "chrome")
    elif requested in {"edge", "microsoft edge"}:
        names = ("msedge.exe", "msedge")
    else:
        names = ("msedge.exe", "msedge", "chrome.exe", "chrome")
    exe = _which_any(names)
    if not exe:
        return False
    try:
        subprocess.Popen(
            [exe, "--app={}".format(url), "--new-window"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )
        return True
    except Exception:
        return False


def _linux_open_app_window(url: str, browser_app: str = "auto") -> bool:
    requested = str(browser_app or "auto").strip().lower()
    if requested in {"chrome", "google chrome"}:
        names = ("google-chrome", "chrome", "chromium", "chromium-browser")
    elif requested in {"edge", "microsoft edge"}:
        names = ("microsoft-edge", "msedge")
    else:
        names = (
            "google-chrome",
            "chrome",
            "chromium",
            "chromium-browser",
            "microsoft-edge",
            "msedge",
        )
    exe = _which_any(names)
    if not exe:
        return False
    try:
        subprocess.Popen(
            [exe, "--app={}".format(url), "--new-window"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return True
    except Exception:
        return False


def open_loveca_window_later(
    url: str,
    *,
    mode: str = "app",
    browser_app: str = "auto",
    delay: float = 0.5,
) -> None:
    """Open the Loveca launcher URL after the HTTP server has started."""
    selected_mode = str(mode or "app").strip().lower()
    if selected_mode in {"none", "off", "no", "disabled"}:
        return

    def worker() -> None:
        if delay > 0:
            threading.Event().wait(delay)
        if selected_mode in {"app", "window", "dedicated"}:
            system = platform.system()
            ok = False
            if system == "Darwin":
                ok = _macos_open_app_window(url, browser_app)
            elif system == "Windows":
                ok = _windows_open_app_window(url, browser_app)
            else:
                ok = _linux_open_app_window(url, browser_app)
            if ok:
                return
        webbrowser.open(url)

    threading.Thread(target=worker, daemon=True).start()


def executable_python() -> str:
    """Return the Python executable that should be used by generated launchers."""
    return os.environ.get("PYTHON", "") or sys.executable or "python3"
