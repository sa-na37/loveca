#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

BUILD_TAG = "audit_topk_complex_family_20260604a"
import argparse, csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from llocg_ui.engine import _match_effect_template  # type: ignore

FOCUS_IDS = {
    'look_top_k_optional_cost_ge_any': 'implemented_cost_ge_any',
    'look_top_k_optional_group_live_required_total_ge': 'implemented_group_live_required_total_ge',
    'look_top_k_optional_member_heart_color_min': 'implemented_member_heart_color_min',
    'look_top_k_optional_member_heart_any_color': 'implemented_member_heart_any_color',
    'look_top_k_optional_member_heart_or_live_required': 'implemented_member_or_live_heart_filter',
    'look_top_k_choose_if_energy_gte': 'implemented_energy_conditional_topk_choose',
}

def iter_clauses(cards):
    for c in cards:
        for ab in c.get('abilities') or []:
            for cl in ab.get('clauses') or []:
                eff = (cl.get('effect_template') or cl.get('raw') or '').replace('\n','').strip()
                cost = (cl.get('cost_template') or '').replace('\n','').strip()
                if 'デッキの上から' not in eff and 'デッキの一番上' not in eff:
                    continue
                yield c, ab, cl, cost, eff

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiled', default='./llocg_db_out_full/cards_compiled_v7h.json')
    ap.add_argument('--outdir', default='./loveca_reports')
    ns = ap.parse_args()
    compiled = Path(ns.compiled)
    if not compiled.exists():
        compiled = ROOT / 'cards_compiled_v7h.json'
    data = json.loads(compiled.read_text(encoding='utf-8'))
    cards = data['cards'] if isinstance(data, dict) and 'cards' in data else data
    rows=[]
    for c, ab, cl, cost, eff in iter_clauses(cards):
        mt = _match_effect_template(eff)
        rule_id = ''
        status = 'needs_audit_unmatched_topk'
        if mt:
            rule, gd = mt
            rule_id = str(rule.get('id') or '')
            status = FOCUS_IDS.get(rule_id, 'implemented_existing_topk_or_deck')
        rows.append({
            'cardnumber': c.get('cardnumber',''),
            'cardname': c.get('cardname',''),
            'ability_type': ab.get('ability_type',''),
            'trigger': ab.get('trigger',''),
            'status': status,
            'rule_id': rule_id,
            'cost_template': cost,
            'effect_template': eff,
        })
    outdir=Path(ns.outdir); outdir.mkdir(parents=True, exist_ok=True)
    csv_path=outdir/'loveca_topk_complex_family_audit_20260604a.csv'
    md_path=outdir/'loveca_topk_complex_family_audit_20260604a.md'
    with csv_path.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['cardnumber'])
        w.writeheader(); w.writerows(rows)
    from collections import Counter
    cnt=Counter(r['status'] for r in rows)
    focus=[r for r in rows if r['status'].startswith('implemented_') and r['rule_id'] in FOCUS_IDS]
    with md_path.open('w', encoding='utf-8') as f:
        f.write('# Loveca topk complex family audit 20260604a\n\n')
        f.write(f'- source: `{compiled}`\n')
        f.write(f'- candidates: {len(rows)}\n')
        for k,v in sorted(cnt.items()):
            f.write(f'- {k}: {v}\n')
        f.write('\n## Newly covered focused variants\n\n')
        for r in focus:
            f.write(f"- `{r['cardnumber']}` {r['cardname']} — {r['rule_id']}\n")
        f.write('\n## Remaining unmatched examples\n\n')
        for r in [x for x in rows if x['status']=='needs_audit_unmatched_topk'][:40]:
            f.write(f"- `{r['cardnumber']}` {r['cardname']} [{r['trigger']}] {r['effect_template']}\n")
    print(f'[OK] wrote: {csv_path}')
    print(f'[OK] wrote: {md_path}')

if __name__ == '__main__':
    main()
