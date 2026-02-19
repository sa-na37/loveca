#!/usr/bin/env python3
"""Launch LLCG manual UI (web).

Examples:
  python3 run_llocg_ui_web.py
  python3 run_llocg_ui_web.py --deck-code 1RCBL
  python3 run_llocg_ui_web.py --deck-code 1RCBL --port 8787

Defaults:
  --root      ./llocg_db_out_full
  --deck-code 1RCBL
"""
from __future__ import annotations

import argparse
from pathlib import Path

from llocg_ui.server import App, Handler


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="./llocg_db_out_full", help="Path to llocg_db_out_full (default: ./llocg_db_out_full)")
    ap.add_argument("--deck-code", dest="deck_code", default="1RCBL", help="Deck code (reads decklists/<code>.tsv)")
    # backward-compat alias
    ap.add_argument("--code", dest="deck_code", help=argparse.SUPPRESS)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--debug", type=int, default=0)
    args = ap.parse_args()

    app = App(root=Path(args.root), code="ui", deck_code=args.deck_code, seed=args.seed, debug=bool(args.debug))
    Handler.app = app

    from http.server import ThreadingHTTPServer
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"[UI] open: http://{args.host}:{args.port}/")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
