#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: audit_stage_heart_group_condition_family_20260608f
from __future__ import annotations

import argparse, csv, json, re
from pathlib import Path


def _cards(data):
    if isinstance(data, dict) and isinstance(data.get('cards'), list):
        return data['cards']
    if isinstance(data, list):
        return data
    return []


def _norm(s: str) -> str:
    s = str(s or '').replace('\n', '')
    # normalize official <桃> style to legacy <(桃)> style used by engine regexes
    def repl(m):
        inner = (m.group(1) or '').strip()
        if inner.startswith('(') and inner.endswith(')'):
            return '<' + inner + '>'
        return '<(' + inner + ')>'
    s = re.sub(r'<([^<>]+)>', repl, s)
    return s


def classify(eff: str) -> str:
    e = _norm(eff)
    if re.match(r'^自分のステージにグループ名がそれぞれ異なるメンバーが\d+人以上いる場合、ライブ終了時まで、自分のセンターエリアにいるメンバーは(?:<\(ALL\)>)+を得る。$', e):
        return 'implemented_live_start_distinct_stage_groups_center_all'
    m = re.match(r'^自分のステージにいるメンバーが持つハートの中に(?:<\([^)]+\)>[、,]?)+がすべてある場合、(?P<inner>.+)$', e)
    if m:
        inner = m.group('inner')
        if re.match(r'^このカードのスコアを\+\d+する。$', inner):
            return 'implemented_live_start_stage_all_heart_colors_score'
        if re.match(r'^ライブ終了時まで、(?:<\(ブレード\)>)+を得る。$', inner):
            return 'implemented_live_start_stage_all_heart_colors_self_blade'
    return ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiled', required=True)
    ap.add_argument('--outdir', required=True)
    ns = ap.parse_args()
    data = json.load(open(ns.compiled, encoding='utf-8'))
    rows = []
    for c in _cards(data):
        cn = c.get('cardnumber') or c.get('card_number') or ''
        name = c.get('cardname') or c.get('name') or ''
        for ab in c.get('abilities', []) or []:
            if not isinstance(ab, dict):
                continue
            if 'ライブ開始時' not in str(ab.get('trigger', '') or ''):
                continue
            for cl in ab.get('clauses', []) or []:
                if not isinstance(cl, dict):
                    continue
                eff = cl.get('effect_template') or cl.get('raw') or ''
                st = classify(eff)
                if st:
                    rows.append({'cardnumber': cn, 'cardname': name, 'trigger': ab.get('trigger',''), 'status': st, 'effect': eff})
    outdir = Path(ns.outdir); outdir.mkdir(parents=True, exist_ok=True)
    csvp = outdir / 'loveca_stage_heart_group_condition_family_audit_20260608f.csv'
    mdp = outdir / 'loveca_stage_heart_group_condition_family_audit_20260608f.md'
    with csvp.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['cardnumber','cardname','trigger','status','effect'])
        w.writeheader(); w.writerows(rows)
    counts = {}
    for r in rows:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    lines = []
    lines.append('# Stage heart/group condition live-start family audit 20260608f')
    lines.append('')
    lines.append(f'candidates: {len(rows)}')
    lines.append('')
    for k in sorted(counts):
        lines.append(f'- {k}: {counts[k]}')
    lines.append('')
    lines.append('## Cards')
    lines.append('')
    for r in rows:
        lines.append(f"- `{r['cardnumber']}` {r['cardname']} — {r['status']}")
    lines.append('')
    mdp.write_text('\n'.join(lines), encoding='utf-8')
    print(f'[OK] wrote: {csvp}')
    print(f'[OK] wrote: {mdp}')

if __name__ == '__main__':
    main()
