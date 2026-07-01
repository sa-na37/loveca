# -*- coding: utf-8 -*-
# BUILD_TAG: audit_stage_leave_optional_discard_baton_family_20260610h
import argparse, csv, json, re
from pathlib import Path

TARGET = 'このメンバーがステージから控え室に置かれたとき'

def iter_cards(data):
    cards = data.get('cards', data) if isinstance(data, dict) else data
    if isinstance(cards, dict):
        return cards.values()
    return cards or []

def card_text(c):
    parts=[]
    for ab in c.get('abilities',[]) or []:
        for cl in ab.get('clauses',[]) or []:
            parts.append(str(cl.get('effect_template') or cl.get('raw') or ''))
    return ' '.join(parts).replace('\n','')

def classify(t):
    if TARGET not in t:
        return ''
    if '手札を1枚控え室に置いてもよい。そうした場合、自分の控え室からライブカードとメンバーカードをそれぞれ1枚まで手札に加える' in t:
        return 'implemented_leave_optional_discard_retrieve_live_member_upto1'
    if '手札を1枚控え室に置いてもよい。そうした場合、ライブ終了時まで、自分のステージにいるメンバー1人' in t and 'ブレード' in t:
        return 'implemented_leave_optional_discard_stage_member_icons'
    if '手札を1枚控え室に置いてもよい。そうした場合、自分の控え室から' in t and 'ライブカードを1枚手札に加える' in t:
        return 'implemented_leave_optional_discard_retrieve_group_live'
    if 'バトンタッチしていた場合' in t and 'ブレードハートを持たない' in t:
        return 'implemented_leave_baton_no_bladeheart_energy_draw'
    if '手札を1枚控え室に置いてもよい' in t:
        return 'deferred_other_optional_discard'
    return ''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--compiled', default='./llocg_db_out_full/cards_compiled_v7h.json')
    ap.add_argument('--outdir', default='./loveca_reports')
    args=ap.parse_args()
    data=json.load(open(args.compiled, encoding='utf-8'))
    rows=[]
    counts={}
    for c in iter_cards(data):
        t=card_text(c)
        cls=classify(t)
        if cls:
            cn=c.get('cardnumber','')
            name=c.get('cardname','') or c.get('name','')
            rows.append({'cardnumber':cn,'cardname':name,'class':cls,'text':t})
            counts[cls]=counts.get(cls,0)+1
    outdir=Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    csv_path=outdir/'loveca_stage_leave_optional_discard_baton_family_audit_20260610h.csv'
    md_path=outdir/'loveca_stage_leave_optional_discard_baton_family_audit_20260610h.md'
    with csv_path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['cardnumber','cardname','class','text'])
        w.writeheader(); w.writerows(rows)
    lines=['# stage leave optional-discard / baton family audit 20260610h','',f'candidates: {len(rows)}','']
    for k in sorted(counts): lines.append(f'- {k}: {counts[k]}')
    lines += ['', '## rows', '']
    for r in rows:
        lines.append(f"- {r['cardnumber']} {r['cardname']} — {r['class']}")
        lines.append(f"  - {r['text']}")
    md_path.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(md_path)

if __name__=='__main__':
    main()
