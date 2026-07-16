#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: llocg_dual_controls_phase_banner_20260716d
from __future__ import annotations
import argparse, os
from pathlib import Path
from llocg_dual.server import serve_dual

START_ENV_PREFIXES=("LLOCG_START_","LLOCG_DEBUG_")
def clear_debug_start_environment()->list[str]:
    removed=[]
    for key in list(os.environ):
        if key.startswith(START_ENV_PREFIXES):
            removed.append(key); os.environ.pop(key,None)
    return sorted(removed)

def main()->None:
    ap=argparse.ArgumentParser(description='LLCG local two-deck simulator')
    ap.add_argument('--root',type=Path,default=Path('.')); ap.add_argument('--data-root',type=Path,default=None)
    ap.add_argument('--deck1',required=True); ap.add_argument('--deck2',required=True); ap.add_argument('--host',default='127.0.0.1'); ap.add_argument('--port',type=int,default=8876); ap.add_argument('--seed',type=int,default=1); ap.add_argument('--debug',action='store_true'); ap.add_argument('--compiled',type=Path,default=None); ap.add_argument('--tokv1',type=Path,default=None); ap.add_argument('--preserve-start-env',action='store_true',help='keep LLOCG_START_*/LLOCG_DEBUG_* test overrides')
    args=ap.parse_args(); project_root=args.root.resolve()
    removed=[] if args.preserve_start_env else clear_debug_start_environment()
    if args.data_root is not None:data_root=args.data_root.resolve() if args.data_root.is_absolute() else (project_root/args.data_root).resolve()
    else:
        candidates=[project_root/'llocg_db_out_full',project_root/'db_out_full',project_root/'llocg_db_out',project_root]; data_root=next((x.resolve() for x in candidates if (x/'decklists').is_dir() or (x/'sim_decks').is_dir()),project_root)
    print(f'[LLCG DUAL] project_root={project_root}'); print(f'[LLCG DUAL] data_root={data_root}'); print(f'[LLCG DUAL] cleared_start_env={",".join(removed) if removed else "none"}')
    serve_dual(host=args.host,port=args.port,root=data_root,deck1=args.deck1,deck2=args.deck2,seed=args.seed,debug=args.debug,compiled=args.compiled,tokv1=args.tokv1)
if __name__=='__main__':main()
