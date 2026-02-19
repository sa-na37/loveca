#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import pathlib
from llocg_ui.server import serve

def main() -> None:
    ap = argparse.ArgumentParser(description="LLCG Manual UI (clean, stdlib-only).")
    ap.add_argument("--deck-code", default="1RCBL", help="deck code (reads ./llocg_db_out_full/decklists/<code>.tsv or deck_<code>.tsv)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--root", default=".", help="project root (default: current dir)")
    ap.add_argument("--no-open", action="store_true", help="do not auto-open browser")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    serve(root=root, host=args.host, port=args.port, deck_code=args.deck_code, open_browser=(not args.no_open))

if __name__ == "__main__":
    main()
