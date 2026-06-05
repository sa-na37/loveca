#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit deck top/bottom choice family in compiled DB."""
from __future__ import annotations
BUILD_TAG = "audit_deck_top_bottom_choice_family_20260605a"
import argparse, csv, json, re
from pathlib import Path

def iter_clauses(compiled):
    for c in compiled.get('cards', []):
        for ab in c.get('abilities', []) or []:
            for cl in ab.get('clauses', []) or []:
                raw = str(cl.get('raw') or cl.get('effect_template') or '')
                cost = str(cl.get('cost_template') or '')
                eff = str(cl.get('effect_template') or '')
                if '一番上か一番下' in raw or '一番上か一番下' in cost or '一番上か一番下' in eff:
                    yield {
                        'cardnumber': c.get('cardnumber',''),
                        'cardname': c.get('cardname',''),
                        'card_type': c.get('card_type',''),
                        'ability_type': ab.get('ability_type',''),
                        'trigger': ab.get('trigger',''),
                        'conditions': ab.get('conditions',''),
                        'cost_template': cost,
                        'effect_template': eff,
                        'raw': raw,
                    }

def status(row):
    raw = (row.get('raw','') + row.get('cost_template','') + row.get('effect_template','')).replace('\n','')
    if '手札の『' in raw and '公開してもよい' in raw and 'これにより公開したカードをデッキの一番上か一番下に置き' in raw:
        return 'implemented_hand_group_cost_to_top_or_bottom_blade'
    if '自分のステージにいるメンバーがすべて' in raw and 'このカードのスコアを+' in raw and 'カードを1枚引き' in raw and '手札からカードを1枚デッキの一番上か一番下に置く' in raw:
        return 'implemented_stage_group_score_draw_hand_top_or_bottom'
    if 'ライブカード置き場から控え室に置かれたとき' in raw:
        return 'needs_live_to_green_replacement_event'
    if '手札からカードを' in raw and '一番上か一番下' in raw:
        return 'implemented_generic_draw_then_hand_top_or_bottom'
    return 'needs_audit_unmatched_top_or_bottom'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--compiled', default='./llocg_db_out_full/cards_compiled_v7h.json')
    ap.add_argument('--outdir', default='./loveca_reports')
    args=ap.parse_args()
    data=json.loads(Path(args.compiled).read_text(encoding='utf-8'))
    rows=[]
    for r in iter_clauses(data):
        r['status']=status(r)
        rows.append(r)
    out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)
    csvp=out/'loveca_deck_top_bottom_choice_family_audit_20260605a.csv'
    fields=['cardnumber','cardname','card_type','ability_type','trigger','conditions','status','cost_template','effect_template','raw']
    with csvp.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    counts={}
    for r in rows: counts[r['status']]=counts.get(r['status'],0)+1
    md=out/'loveca_deck_top_bottom_choice_family_audit_20260605a.md'
    lines=['# Loveca deck top/bottom choice family audit 20260605a','',f'candidates: {len(rows)}']
    for k in sorted(counts): lines.append(f'- {k}: {counts[k]}')
    lines += ['','## Rows']
    for r in rows:
        lines.append(f"- `{r['cardnumber']}` {r['cardname']} [{r['status']}] {r['trigger']}")
    md.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'[OK] wrote {csvp}')
    print(f'[OK] wrote {md}')
if __name__=='__main__': main()
