#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: audit_success_storage_count_score_family_20260608d
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path


def iter_effect_rows(cards):
    for c in cards:
        cn = str(c.get('cardnumber','') or '')
        name = str(c.get('cardname','') or '')
        ctype = str(c.get('card_type','') or '')
        for ab in c.get('abilities', []) or []:
            trig = str(ab.get('trigger','') or '')
            ability_type = str(ab.get('ability_type','') or '')
            for cl in ab.get('clauses', []) or []:
                if not isinstance(cl, dict):
                    continue
                eff = str(cl.get('effect_template','') or cl.get('raw','') or '').strip()
                if not eff:
                    continue
                eff_norm = re.sub(r'\s+', '', eff.replace('＋','+'))
                eff_norm = re.sub(r'<\(\s*スコア\s*\)\s*([+]\s*\d+)>', lambda m: '<(スコア' + m.group(1).replace(' ', '') + ')>', eff_norm)
                yield cn, name, ctype, ability_type, trig, eff, eff_norm


def classify(cn, trig, eff, eff_norm):
    if re.search(r'自分か相手の成功ライブカード置き場にカードが\d+枚以上あり、かつ自分のステージに名前の異なるメンバーが\d+人以上いる場合、このカードのスコアを\+\d+する。?', eff_norm):
        return 'implemented_live_start_either_success_count_and_distinct_stage_names_score'
    if re.search(r'自分の成功ライブカード置き場のカード枚数が相手より少ない場合、このカードのスコアを\+\d+する。?', eff_norm):
        return 'implemented_live_start_own_success_count_less_than_opponent_manual_score'
    if re.search(r'自分か相手の成功ライブカード置き場にカードが\d+枚以上あり、かつエール(?:によって|により)公開された自分のカードの中に<\(スコア\+1\)>を持つライブカードが\d+枚以上ある場合、このカードのスコアを\+\d+する。?', eff_norm):
        return 'implemented_live_success_either_success_count_and_revealed_score_tag_live_score'
    return ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiled', required=True)
    ap.add_argument('--outdir', default='loveca_reports')
    ns = ap.parse_args()
    data = json.load(open(ns.compiled, encoding='utf-8'))
    cards = data.get('cards', data if isinstance(data, list) else [])
    rows = []
    for cn, name, ctype, ability_type, trig, eff, eff_norm in iter_effect_rows(cards):
        if '成功ライブカード置き場' not in eff and '成功ライブカード置き場' not in eff_norm:
            continue
        status = classify(cn, trig, eff, eff_norm)
        if not status:
            continue
        rows.append({
            'cardnumber': cn,
            'cardname': name,
            'card_type': ctype,
            'ability_type': ability_type,
            'trigger': trig,
            'status': status,
            'effect': eff.replace('\n',' '),
        })
    outdir = Path(ns.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / 'loveca_success_storage_count_score_family_audit_20260608d.csv'
    md_path = outdir / 'loveca_success_storage_count_score_family_audit_20260608d.md'
    with csv_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['cardnumber','cardname','card_type','ability_type','trigger','status','effect'])
        w.writeheader(); w.writerows(rows)
    counts = {}
    for r in rows:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    lines = []
    lines.append('# Loveca success-storage count score family audit 20260608d')
    lines.append('')
    lines.append(f'candidates: {len(rows)}')
    lines.append('')
    for k in sorted(counts):
        lines.append(f'- {k}: {counts[k]}')
    lines.append('')
    lines.append('## Rows')
    lines.append('')
    for r in rows:
        lines.append(f"- `{r['cardnumber']}` {r['cardname']} — {r['status']}")
    lines.append('')
    md_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'[OK] wrote: {csv_path}')
    print(f'[OK] wrote: {md_path}')

if __name__ == '__main__':
    main()
