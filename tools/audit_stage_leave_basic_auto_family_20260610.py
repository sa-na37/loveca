#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: audit_stage_leave_basic_auto_family_20260610f
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

TRIG = 'このメンバーがステージから控え室に置かれたとき、'

def load_cards(path: Path):
    data = json.loads(path.read_text(encoding='utf-8'))
    return data.get('cards', data if isinstance(data, list) else [])

def classify(eff: str) -> str:
    inner = eff.replace('\n','').strip()
    if inner.startswith(TRIG):
        inner = inner[len(TRIG):]
    if re.fullmatch(r'メンバー1人をアクティブにしてもよい。', inner):
        return 'implemented_leave_activate_member_optional'
    if re.fullmatch(r'自分のデッキの上からカードを\d+枚見る。その中からメンバーカードを1枚公開して手札に加えてもよい。残りを控え室に置く。', inner):
        return 'implemented_leave_topk_member_to_hand'
    if re.fullmatch(r'自分のデッキの上からカードを\d+枚見る。その中からライブカードを1枚公開して手札に加えてもよい。残りを控え室に置く。', inner):
        return 'implemented_leave_topk_live_to_hand'
    if re.fullmatch(r'カードを\d+枚引き、手札を\d+枚控え室に置く。', inner):
        return 'implemented_leave_draw_then_discard'
    if re.fullmatch(r'メンバー1人をポジションチェンジさせてもよい。', inner):
        return 'implemented_leave_position_change_optional'
    if '手札を1枚控え室に置いてもよい。そうした場合' in inner:
        return 'deferred_leave_optional_hand_discard_followup'
    if 'バトンタッチしていた場合' in inner:
        return 'deferred_leave_baton_condition_bonus'
    return 'needs_audit_unmatched'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--compiled', required=True)
    ap.add_argument('--outdir', required=True)
    args=ap.parse_args()
    cards=load_cards(Path(args.compiled))
    rows=[]
    for c in cards:
        cn=c.get('cardnumber') or c.get('card_number') or ''
        name=c.get('cardname') or c.get('name') or ''
        for ab in c.get('abilities',[]) or []:
            for cl in ab.get('clauses',[]) or []:
                eff=str(cl.get('effect_template') or cl.get('raw') or '').strip()
                if TRIG in eff:
                    rows.append({'cardnumber':cn,'cardname':name,'class':classify(eff),'effect':eff.replace('\n','')})
    outdir=Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    csvp=outdir/'loveca_stage_leave_basic_auto_family_audit_20260610f.csv'
    mdp=outdir/'loveca_stage_leave_basic_auto_family_audit_20260610f.md'
    with csvp.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=['cardnumber','cardname','class','effect'])
        w.writeheader(); w.writerows(rows)
    counts={}
    for r in rows: counts[r['class']]=counts.get(r['class'],0)+1
    lines=['# stage leave basic auto family audit 20260610f','',f'candidates: {len(rows)}','']
    for k in sorted(counts): lines.append(f'- {k}: {counts[k]}')
    lines += ['','## rows','']
    for r in rows:
        lines.append(f"- {r['cardnumber']} {r['cardname']} — {r['class']}")
        lines.append(f"  - {r['effect']}")
    mdp.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(mdp)
    print(csvp)

if __name__=='__main__':
    main()
