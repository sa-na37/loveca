#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""llocg_ui_web.py (entrypoint)

単体版の UI と同じ CLI / 動作を保ったまま、内部を llocg_ui/* に分割した版です。

例:
  python3 llocg_ui_web.py --root ./llocg_db_out_full --code 7QEC8 --port 8000

（compiled/tokv1 は省略可：root 配下から自動検出）
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the local package (./llocg_ui) importable even when this script is
# launched from another working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from llocg_ui.server import App, Handler
from http.server import ThreadingHTTPServer


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--code', required=True)
    ap.add_argument('--deck-code', default=None, help='decklist code to load (default: same as --code)')
    ap.add_argument('--compiled', default=None, help='path to cards_compiled_*.json (optional)')
    ap.add_argument('--tokv1', default=None, help='path to cards_min_tokv1.csv/json (optional)')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--debug', action='store_true')
    ap.add_argument('--port', type=int, default=8000)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    compiled_p = Path(args.compiled).resolve() if args.compiled else None
    tokv1_p = Path(args.tokv1).resolve() if args.tokv1 else None

    deck_code = str(args.deck_code) if args.deck_code else str(args.code)
    app = App(root=root, code=str(args.code), deck_code=deck_code, seed=int(args.seed), debug=bool(args.debug), compiled=compiled_p, tokv1=tokv1_p)

    Handler.app = app
    server = ThreadingHTTPServer(('127.0.0.1', int(args.port)), Handler)
    print(f"[UI] root={root}")
    if deck_code != str(args.code):
        print(f"[UI] code={args.code} deck_code={deck_code} seed={args.seed} debug={args.debug}")
    else:
        print(f"[UI] code={args.code} seed={args.seed} debug={args.debug}")
    print(f"[UI] open: http://127.0.0.1:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n[UI] bye')
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
