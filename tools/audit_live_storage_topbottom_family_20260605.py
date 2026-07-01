#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit live-storage cleanup top/bottom + required-heart sum family."""
from __future__ import annotations
BUILD_TAG = "audit_live_storage_topbottom_family_20260605a"
import argparse, csv, json, re
from pathlib import Path


def iter_clauses(card):
    for ab in card.get('abilities') or []:
        for cl in ab.get('clauses') or []:
            yield ab, cl, str(cl.get('effect_template') or cl.get('raw') or '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiled', default='./llocg_db_out_full/cards_compiled_v7h.json')
    ap.add_argument('--outdir', default='./loveca_reports')
    ns = ap.parse_args()
    data = json.loads(Path(ns.compiled).read_text(encoding='utf-8'))
    cards = data.get('cards', data) if isinstance(data, dict) else data
    rows = []
    for c in cards:
        hit_cleanup = False
        hit_reqsum = False
        for ab, cl, eff in iter_clauses(c):
            norm = re.sub(r'\s+', '', eff.replace('<赤>','<(赤)>').replace('<緑>','<(緑)>').replace('<青>','<(青)>').replace('<ALL>','<(ALL)>'))
            if 'ライブカード置き場から控え室に置かれたとき' in norm and 'デッキの一番上か一番下' in norm:
                hit_cleanup = True
            if 'ライブカード置き場にあるカードが' in norm and '必要ハートに含まれる' in norm and '<(ALL)><(ALL)>' in norm:
                hit_reqsum = True
        if hit_cleanup or hit_reqsum:
            status = []
            if hit_cleanup: status.append('implemented_live_storage_cleanup_top_or_bottom')
            if hit_reqsum: status.append('implemented_live_start_group_req_color_sum_all')
            rows.append({
                'cardnumber': c.get('cardnumber',''),
                'cardname': c.get('cardname',''),
                'status': '+'.join(status),
                'has_cleanup_topbottom': int(hit_cleanup),
                'has_reqsum_all': int(hit_reqsum),
            })
    outdir = Path(ns.outdir); outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir/'loveca_live_storage_topbottom_family_audit_20260605a.csv'
    md_path = outdir/'loveca_live_storage_topbottom_family_audit_20260605a.md'
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['cardnumber','cardname','status','has_cleanup_topbottom','has_reqsum_all'])
        w.writeheader(); w.writerows(rows)
    n_cleanup = sum(int(r['has_cleanup_topbottom']) for r in rows)
    n_reqsum = sum(int(r['has_reqsum_all']) for r in rows)
    md = [
        '# Loveca live storage top/bottom family audit 20260605a',
        '',
        f'candidates: {len(rows)}',
        f'- implemented_live_storage_cleanup_top_or_bottom: {n_cleanup}',
        f'- implemented_live_start_group_req_color_sum_all: {n_reqsum}',
        '',
        '| cardnumber | cardname | status |',
        '|---|---|---|',
    ]
    for r in rows:
        md.append(f"| {r['cardnumber']} | {r['cardname']} | {r['status']} |")
    md_path.write_text('\n'.join(md)+'\n', encoding='utf-8')
    print(f'[OK] wrote {csv_path}')
    print(f'[OK] wrote {md_path}')

if __name__ == '__main__':
    main()
