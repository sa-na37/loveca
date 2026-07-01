#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: audit_success_count_cost_misc_family_20260610c
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

TARGETS = {
    'PL!S-bp3-016': 'implemented_body_success_count_cost_bonus',
    'PL!-pb1-014': 'implemented_hand_cost_reduction_if_success_group',
    'PL!-pb1-007': 'implemented_activated_discard_cost_reduction_per_success_count',
    'PL!-sd1-001': 'implemented_enter_success_count_retrieve_live_and_body_blade',
    'PL!-pb1-005': 'implemented_enter_success_nonempty_draw',
}

def load_cards(path: Path):
    data = json.loads(path.read_text(encoding='utf-8'))
    cards = data.get('cards', data if isinstance(data, list) else [])
    return cards

def ability_blob(card):
    parts=[]
    for ab in card.get('abilities') or []:
        parts.append(str(ab.get('ability_type','')))
        parts.append(str(ab.get('trigger','')))
        parts.append(str(ab.get('conditions','')))
        for cl in ab.get('clauses') or []:
            if isinstance(cl, dict):
                parts.append(str(cl.get('cost_template','')))
                parts.append(str(cl.get('effect_template','')))
                parts.append(str(cl.get('raw','')))
    return ''.join(parts).replace('\n','')

def classify(cn, blob):
    if cn in TARGETS:
        return TARGETS[cn]
    if '成功ライブカード置き場にあるカード1枚につき' in blob and 'このメンバーのコストを+' in blob:
        return 'candidate_body_success_count_cost_bonus'
    if '成功ライブカード置き場に' in blob and '手札にあるこのメンバーカードのコスト' in blob and '減る' in blob:
        return 'candidate_hand_cost_reduction_if_success_group'
    if 'この能力を起動するためのコスト' in blob and '成功ライブカード置き場にあるカード1枚につき' in blob and '控え室に置く手札の数が1枚減る' in blob:
        return 'candidate_activated_discard_cost_reduction_per_success_count'
    if re.search(r'成功ライブカード置き場にカードが\d+枚以上ある場合', blob):
        return 'candidate_success_count_conditional_wrapper'
    if '成功ライブカード置き場にカードがある場合' in blob:
        return 'candidate_success_nonempty_conditional_wrapper'
    return ''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--compiled', required=True)
    ap.add_argument('--outdir', required=True)
    ns=ap.parse_args()
    outdir=Path(ns.outdir); outdir.mkdir(parents=True, exist_ok=True)
    rows=[]
    for card in load_cards(Path(ns.compiled)):
        cn=str(card.get('cardnumber') or card.get('card_number') or '')
        if not cn: continue
        blob=ability_blob(card)
        cat=classify(cn, blob)
        if cat:
            rows.append({
                'cardnumber': cn,
                'cardname': str(card.get('cardname') or card.get('name') or ''),
                'category': cat,
                'implemented': 'yes' if cat.startswith('implemented_') else 'candidate',
                'ability_excerpt': blob[:500],
            })
    csv_path=outdir/'loveca_success_count_cost_misc_family_audit_20260610c.csv'
    md_path=outdir/'loveca_success_count_cost_misc_family_audit_20260610c.md'
    with csv_path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=['cardnumber','cardname','category','implemented','ability_excerpt'])
        w.writeheader(); w.writerows(rows)
    counts={}
    for r in rows:
        counts[r['category']]=counts.get(r['category'],0)+1
    lines=['# success_count_cost_misc_family audit 20260610c','',f'candidates: {len(rows)}','']
    for k in sorted(counts):
        lines.append(f'- {k}: {counts[k]}')
    lines += ['','## rows','']
    for r in rows:
        lines.append(f"- `{r['cardnumber']}` {r['cardname']} — {r['category']}")
    md_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(md_path)

if __name__=='__main__':
    main()
