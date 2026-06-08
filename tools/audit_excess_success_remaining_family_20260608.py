#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: audit_excess_success_remaining_family_20260608c
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

TARGETS = {
    'PL!-bp3-025': 'implemented_excess_zero_live_score_bonus',
    'PL!-bp4-023': 'implemented_excess_color_draw',
    'PL!HS-bp6-028': 'implemented_excess_total_topk_reorder',
    'PL!N-bp3-027': 'implemented_excess_color_stage_group_energy_wait',
    'PL!N-bp5-007': 'implemented_excess_total_draw_then_discard',
    'PL!S-bp5-020': 'implemented_excess_atleast_loss_score_bonus_db_corrected',
    'PL!N-bp5-010': 'implemented_self_excess_live_total_score_adjust',
    'PL!S-bp3-019': 'implemented_direct_score_set_no_bladeheart_or_excess',
    'PL!S-bp6-024': 'implemented_opponent_excess_loss_manual_live_score_bonus',
}

def iter_cards(obj):
    if isinstance(obj, dict) and isinstance(obj.get('cards'), list):
        return obj['cards']
    if isinstance(obj, list):
        return obj
    return []

def effects_of(card):
    for ab in card.get('abilities') or []:
        if not isinstance(ab, dict):
            continue
        trig = str(ab.get('trigger') or '')
        for cl in ab.get('clauses') or []:
            if isinstance(cl, dict):
                eff = str(cl.get('effect_template') or cl.get('raw') or '').replace('\n','')
                yield trig, eff

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--compiled', default='./llocg_db_out_full/cards_compiled_v7h.json')
    ap.add_argument('--outdir', default='./loveca_reports')
    args=ap.parse_args()
    cards=iter_cards(json.load(open(args.compiled, encoding='utf-8')))
    rows=[]
    for c in cards:
        cn=str(c.get('cardnumber') or '')
        if cn not in TARGETS:
            continue
        trig_eff=[]
        for trig, eff in effects_of(c):
            if '余剰ハート' in eff or 'ブレードハート' in eff:
                trig_eff.append(f'<{trig}> {eff}')
        rows.append({
            'cardnumber': cn,
            'cardname': str(c.get('cardname') or ''),
            'card_type': str(c.get('card_type') or ''),
            'status': TARGETS[cn],
            'effect': ' / '.join(trig_eff),
        })
    rows.sort(key=lambda r: r['cardnumber'])
    outdir=Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    csv_path=outdir/'loveca_excess_success_remaining_family_audit_20260608c.csv'
    md_path=outdir/'loveca_excess_success_remaining_family_audit_20260608c.md'
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['cardnumber','cardname','card_type','status','effect'])
        w.writeheader(); w.writerows(rows)
    counts={}
    for r in rows: counts[r['status']]=counts.get(r['status'],0)+1
    with md_path.open('w', encoding='utf-8') as f:
        f.write('# Loveca excess-heart live-success remaining family audit 20260608c\n\n')
        f.write(f'candidates: {len(rows)}\n\n')
        for k in sorted(counts):
            f.write(f'- {k}: {counts[k]}\n')
        f.write('\n## Rows\n\n')
        for r in rows:
            f.write(f"- `{r['cardnumber']}` {r['cardname']} — {r['status']}\n")
    print(f'[OK] wrote: {md_path}')
    print(f'[OK] wrote: {csv_path}')
if __name__ == '__main__':
    main()
