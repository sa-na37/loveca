# BUILD_TAG = "startup_update_prompt_interval_20260722a"
"""Loveca application command-line entrypoint."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .assets import ensure_ui_assets_from_local_bundle
from .core import AppState, DEFAULT_HOST, DEFAULT_PORT
from .launcher import find_project_root, open_loveca_window_later
from .web import Handler, LovecaHTTPServer

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Loveca application launcher")
    parser.add_argument("--root", type=Path, default=None, help="Loveca project root")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--window-mode", choices=("app", "browser", "none"), default="app", help="How to open the launcher UI")
    parser.add_argument("--browser-app", choices=("auto", "chrome", "edge", "safari"), default="auto", help="Preferred browser for app/window mode")
    parser.add_argument("--no-browser", action="store_true", help="Compatibility alias for --window-mode none")
    parser.add_argument("--skip-startup-update", action="store_true", help="Do not start the database update check on app launch")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = (args.root.expanduser().resolve() if args.root else find_project_root())
    if not root.exists():
        print(f"[ERROR] root does not exist: {root}", file=sys.stderr)
        return 2

    asset_result = ensure_ui_assets_from_local_bundle(root)
    if asset_result.source:
        print(f"[LOVECА APP] ui_assets_bundle={asset_result.source}")
        if asset_result.installed:
            print(f"[LOVECА APP] ui_assets_installed={len(asset_result.installed)}")
        if asset_result.errors:
            print(f"[WARN] ui_assets_errors={asset_result.errors}", file=sys.stderr)

    app_state = AppState(root)
    try:
        server = LovecaHTTPServer((args.host, args.port), Handler, app_state)
    except OSError as exc:
        print(
            "[ERROR] Loveca Applicationの待受ポートを使用できません: "
            f"{args.host}:{args.port}: {exc}",
            file=sys.stderr,
        )
        print(
            "[HINT] 既定ポートは8875です。残存プロセス確認: "
            f"lsof -nP -iTCP:{args.port} -sTCP:LISTEN",
            file=sys.stderr,
        )
        return 3
    if args.skip_startup_update:
        startup_update_enabled = False
        startup_update_reason = "--skip-startup-update"
    else:
        startup_update_enabled, startup_update_reason = app_state.should_show_startup_update_prompt()
    url = f"http://{args.host}:{args.port}/"
    open_url = f"http://{args.host}:{args.port}/update?startup=1" if startup_update_enabled else url
    print("[LOVECА APP] BUILD_TAG=startup_update_prompt_interval_20260722a")
    print(f"[LOVECА APP] root={root}")
    print(f"[LOVECА APP] open={open_url}")
    print("[LOVECА APP] stop with Ctrl+C")

    window_mode = "none" if args.no_browser else str(args.window_mode)
    open_loveca_window_later(
        open_url,
        mode=window_mode,
        browser_app=str(args.browser_app),
        delay=0.5,
    )
    if startup_update_enabled:
        print(f"[LOVECА APP] startup_update=waiting-for-user-confirmation: {startup_update_reason}")
    elif args.skip_startup_update:
        print("[LOVECА APP] startup_update=skipped: --skip-startup-update")
    else:
        print(f"[LOVECА APP] startup_update=skipped: {startup_update_reason}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[LOVECА APP] stopping")
        app_state.stop_all_child_processes()
    finally:
        server.server_close()
    return 0
