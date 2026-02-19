#!/usr/bin/env python3
"""Launch LLCG manual UI (web).

Run from the `loveca/` directory:
  python3 run_llocg_ui_web.py --root ./llocg_db_out_full --code 1RCBL --port 8000

This script is intentionally small and stable: it only wires CLI -> server.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from llocg_ui.server import App, Handler


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Path to llocg_db_out_full")
    ap.add_argument("--code", required=True, help="Deck code (decklists/<code>.tsv)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--debug", type=int, default=0)
    args = ap.parse_args()

    app = App(root=Path(args.root), code="ui", deck_code=args.code, seed=args.seed, debug=bool(args.debug))

    # Handler expects to read `Handler.app` as a class var.
    Handler.app = app

    from http.server import ThreadingHTTPServer

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"[UI] open: http://{args.host}:{args.port}/")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
