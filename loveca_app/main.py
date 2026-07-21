# BUILD_TAG = "loveca_distribution_launcher_20260721a"
"""Loveca application command-line entrypoint."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = (args.root.expanduser().resolve() if args.root else find_project_root())
    if not root.exists():
        print(f"[ERROR] root does not exist: {root}", file=sys.stderr)
        return 2

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
    url = f"http://{args.host}:{args.port}/"
    print("[LOVECА APP] BUILD_TAG=loveca_distribution_launcher_20260721a")
    print(f"[LOVECА APP] root={root}")
    print(f"[LOVECА APP] open={url}")
    print("[LOVECА APP] stop with Ctrl+C")

    window_mode = "none" if args.no_browser else str(args.window_mode)
    open_loveca_window_later(
        url,
        mode=window_mode,
        browser_app=str(args.browser_app),
        delay=0.5,
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[LOVECА APP] stopping")
        app_state.stop_all_child_processes()
    finally:
        server.server_close()
    return 0

