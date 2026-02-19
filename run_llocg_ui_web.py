# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
from pathlib import Path

from llocg_ui.server import serve


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--root", default="./llocg_db_out_full")

    # UI code is just a label in /state; keep for compatibility
    ap.add_argument("--code", default="ui")

    # Accept both spellings (user previously used --deck-code)
    ap.add_argument("--deck-code", dest="deck_code", default="1RCBL")
    ap.add_argument("--deck_code", dest="deck_code", default=None)

    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--debug", action="store_true")

    # Optional explicit DB files; usually auto-detected under root
    ap.add_argument("--compiled", default=None)
    ap.add_argument("--tokv1", default=None)

    args = ap.parse_args()
    deck_code = args.deck_code or "1RCBL"

    compiled = Path(args.compiled) if args.compiled else None
    tokv1 = Path(args.tokv1) if args.tokv1 else None

    serve(
        host=str(args.host),
        port=int(args.port),
        root=Path(args.root),
        code=str(args.code),
        deck_code=str(deck_code),
        seed=int(args.seed),
        debug=bool(args.debug),
        compiled=compiled,
        tokv1=tokv1,
    )


if __name__ == "__main__":
    main()
