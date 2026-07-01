# -*- coding: utf-8 -*-
# BUILD_TAG: audit_success_storage_score_sum_family_20260608g
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path
from typing import Any, Dict, List


def load_cards(path: str) -> List[Dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if isinstance(data, dict):
        if isinstance(data.get('cards'), list):
            return data['cards']
        if isinstance(data.get('data'), list):
            return data['data']
        return [v for v in data.values() if isinstance(v, dict)]
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []


def norm(s: str) -> str:
    t = str(s or '').replace('\n','').replace(' ', '')
    t = t.replace('<スコア+1>', '<(スコア+1)>')
    t = t.replace('<(スコア)+1>', '<(スコア+1)>')
    return t


def iter_abilities(cards):
    for c in cards:
        cn = c.get('cardnumber') or c.get('card_number') or c.get('id') or ''
        name = c.get('cardname') or c.get('name') or c.get('card_name') or ''
        for ab in c.get('abilities') or []:
            trig = ab.get('trigger','')
            typ = ab.get('ability_type','')
            for cl in ab.get('clauses') or []:
                eff = cl.get('effect_template') or cl.get('raw') or ''
                yield cn, name, typ, trig, eff


def classify(eff: str) -> str:
    e = norm(eff)
    if re.search(r'自分の成功ライブカード置き場にあるカードのスコア(?:の)?合計が\d+以上の場合、', e):
        return 'implemented_success_score_sum_ge_inner_effect'
    if re.search(r'自分の成功ライブカード置き場にカードが\d+枚以上あり、かつスコアの合計が\d+以下の場合、', e):
        return 'implemented_success_count_and_score_sum_le_inner_score'
    if '自分の成功ライブカード置き場に<(スコア+1)>を持つ' in e and '2枚以上ある場合、代わりに' in e:
        return 'implemented_success_score_tag_group_count_score_bonus'
    if '自分か相手の成功ライブカード置き場にカードが' in e and '<(スコア+1)>を持つライブカード' in e:
        return 'implemented_existing_either_success_count_revealed_score_tag_live_score'
    if 'この能力は' in e and 'のみ起動できる' in e:
        return 'deferred_activated_ability_condition'
    if 'であるかぎり' in e or 'である限り' in e or '高いかぎり' in e:
        return 'deferred_body_always_success_score_condition'
    return 'needs_audit_unmatched'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiled', required=True)
    ap.add_argument('--outdir', required=True)
    args = ap.parse_args()
    cards = load_cards(args.compiled)
    rows = []
    for cn, name, typ, trig, eff in iter_abilities(cards):
        if '成功ライブカード置き場' not in eff:
            continue
        if ('スコア合計' not in eff) and ('スコアの合計' not in eff) and ('<スコア+1>' not in eff) and ('<(スコア+1)>' not in eff) and ('<(スコア)+1>' not in eff):
            continue
        cat = classify(eff)
        rows.append({'cardnumber': cn, 'cardname': name, 'ability_type': typ, 'trigger': trig, 'category': cat, 'effect': eff})
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / 'loveca_success_storage_score_sum_family_audit_20260608g.csv'
    md_path = outdir / 'loveca_success_storage_score_sum_family_audit_20260608g.md'
    with csv_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['cardnumber','cardname','ability_type','trigger','category','effect'])
        w.writeheader(); w.writerows(rows)
    counts = {}
    for r in rows:
        counts[r['category']] = counts.get(r['category'], 0) + 1
    lines = []
    lines.append('# Success-storage score-sum / score-tag family audit 20260608g')
    lines.append('')
    lines.append(f'candidates: {len(rows)}')
    lines.append('')
    for k in sorted(counts):
        lines.append(f'- {k}: {counts[k]}')
    lines.append('')
    lines.append('## Implemented cards')
    for r in rows:
        if r['category'].startswith('implemented'):
            lines.append(f"- {r['cardnumber']} {r['cardname']}: {r['category']}")
    md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(md_path)

if __name__ == '__main__':
    main()
