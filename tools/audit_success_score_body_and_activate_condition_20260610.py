#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: audit_success_score_body_and_activate_condition_20260610a
"""Audit success-zone score-sum BODY/activated conditions.

This audit focuses on cards from the previous P13 deferred buckets:
- BODY always effects that reference success live-card storage score sum
- activated abilities whose activation condition references that score sum
"""
from __future__ import annotations
import argparse, csv, json, os, re
from typing import Any, Dict, Iterable, List

TARGETS = {
    'PL!-bp4-008': 'implemented_body_own_success_score_sum_cost_bonus',
    'PL!-bp4-018': 'implemented_body_own_gt_opponent_success_score_manual_blade',
    'PL!-bp5-008': 'implemented_body_own_success_score_sum_heart_bonus',
    'PL!N-bp4-012': 'implemented_body_opponent_success_score_sum_manual_total_score',
    'PL!-bp4-002': 'implemented_activated_success_score_sum_condition',
}

def _cards(obj: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(obj, dict):
        if isinstance(obj.get('cards'), list):
            return obj['cards']
        if isinstance(obj.get('data'), list):
            return obj['data']
        return [v for v in obj.values() if isinstance(v, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []

def _cn(c: Dict[str, Any]) -> str:
    return str(c.get('cardnumber') or c.get('card_number') or c.get('number') or '')

def _name(c: Dict[str, Any]) -> str:
    return str(c.get('cardname') or c.get('name') or '')

def _abilities(c: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    for ab in c.get('abilities') or []:
        if isinstance(ab, dict):
            yield ab

def _effect(ab: Dict[str, Any]) -> str:
    parts: List[str] = []
    for cl in ab.get('clauses') or []:
        if isinstance(cl, dict):
            parts.append(str(cl.get('raw') or cl.get('effect_template') or ''))
    return ' '.join(parts).replace('\n', ' ')

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiled', default='./llocg_db_out_full/cards_compiled_v7h.json')
    ap.add_argument('--outdir', default='./loveca_reports')
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    with open(args.compiled, 'r', encoding='utf-8') as f:
        data = json.load(f)
    rows: List[Dict[str, str]] = []
    for c in _cards(data):
        cn = _cn(c)
        if cn not in TARGETS:
            continue
        for ab in _abilities(c):
            eff = _effect(ab)
            eff_norm = eff.replace('\n', '').replace(' ', '')
            if '成功ライブカード置き場' not in eff_norm or 'スコア' not in eff_norm:
                continue
            rows.append({
                'cardnumber': cn,
                'cardname': _name(c),
                'ability_type': str(ab.get('ability_type') or ''),
                'trigger': str(ab.get('trigger') or ''),
                'category': TARGETS[cn],
                'effect': eff,
            })
    rows.sort(key=lambda r: r['cardnumber'])
    counts: Dict[str, int] = {}
    for r in rows:
        counts[r['category']] = counts.get(r['category'], 0) + 1
    md_path = os.path.join(args.outdir, 'loveca_success_score_body_and_activate_condition_audit_20260610a.md')
    csv_path = os.path.join(args.outdir, 'loveca_success_score_body_and_activate_condition_audit_20260610a.csv')
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['cardnumber','cardname','ability_type','trigger','category','effect'])
        w.writeheader(); w.writerows(rows)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('# Success-zone score BODY/activated condition audit 20260610a\n\n')
        f.write(f'candidates: {len(rows)}\n\n')
        for k in sorted(counts):
            f.write(f'- {k}: {counts[k]}\n')
        f.write('\n## Cards\n')
        for r in rows:
            f.write(f"- {r['cardnumber']} {r['cardname']}: {r['category']}\n")
    print(md_path)
    print(csv_path)

if __name__ == '__main__':
    main()
