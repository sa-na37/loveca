"""Loveca application command-line entrypoint."""
from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path

from .core import AppState, DEFAULT_HOST, DEFAULT_PORT
from .web import Handler, LovecaHTTPServer

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Loveca application launcher")
    parser.add_argument("--root", type=Path, default=Path(sys.argv[0]).resolve().parent, help="Loveca project root")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
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
    print("[LOVECА APP] BUILD_TAG=loveca_app_update_field_schema_20260716br")
    print(f"[LOVECА APP] root={root}")
    print(f"[LOVECА APP] open={url}")
    print("[LOVECА APP] stop with Ctrl+C")

    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[LOVECА APP] stopping")
        app_state.stop_all_child_processes()
    finally:
        server.server_close()
    return 0


