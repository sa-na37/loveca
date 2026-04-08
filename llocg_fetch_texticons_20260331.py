#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: fetch_texticons_20260408a_anyheart
"""
Fetch official text icons (heart colors / all / blade) and store them under
<root>/card_images/texticons/, plus write a manifest JSON under <root>.
Usage:
  python3 llocg_fetch_texticons_20260331.py --root ./llocg_db_out_full
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict

try:
    import requests
except ImportError:
    print("ERROR: requests is required. Install with: python3 -m pip install requests", file=sys.stderr)
    raise

BASE = "https://llofficial-cardgame.com/wordpress/wp-content/images/texticon/"

ICON_MAP: Dict[str, str] = {
    "pink": "heart_01.png",
    "red": "heart_02.png",
    "yellow": "heart_03.png",
    "green": "heart_04.png",
    "blue": "heart_05.png",
    "purple": "heart_06.png",
    "all": "icon_all.png",
    "blade": "icon_blade.png",
}

TOKEN_MAP: Dict[str, str] = {
    "<(桃)>": "pink",
    "<(赤)>": "red",
    "<(黄)>": "yellow",
    "<(緑)>": "green",
    "<(青)>": "blue",
    "<(紫)>": "purple",
    "<(ALL)>": "all",
    "<(ブレード)>": "blade",
}

def fetch_one(session: requests.Session, url: str, outpath: Path, quiet: bool = False) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    r = session.get(url, timeout=30)
    r.raise_for_status()
    outpath.write_bytes(r.content)
    if not quiet:
        print(f"[OK] {outpath}")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="./llocg_db_out_full")
    ap.add_argument("--subdir", default="card_images/texticons")
    ap.add_argument("--manifest-name", default="texticon_manifest_20260331.json")
    ap.add_argument("--sleep", type=float, default=0.15)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    outdir = root / args.subdir
    manifest_path = root / args.manifest_name
    outdir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "base_url": BASE,
        "icons": {},
        "token_map": TOKEN_MAP,
    }

    with requests.Session() as sess:
        sess.headers.update({"User-Agent": "Mozilla/5.0"})
        for key, filename in ICON_MAP.items():
            url = BASE + filename
            local_rel = f"{args.subdir}/{filename}"
            local_path = root / local_rel
            fetch_one(sess, url, local_path, quiet=args.quiet)
            manifest["icons"][key] = {
                "filename": filename,
                "url": url,
                "local_path": local_rel,
            }
            time.sleep(args.sleep)

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.quiet:
        print(f"[OK] manifest: {manifest_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
