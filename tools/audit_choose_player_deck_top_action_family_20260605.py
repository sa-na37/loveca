#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit choose-player deck-top action family for Loveca runtime."""
from __future__ import annotations

BUILD_TAG = "audit_choose_player_deck_top_action_family_20260605a"

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


def _clauses(card: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for ab in card.get('abilities') or []:
        for cl in ab.get('clauses') or []:
            raw = str(cl.get('raw') or cl.get('effect_template') or '').strip()
            if raw:
                out.append(raw.replace('\n', ''))
    return out


def classify(text: str) -> str:
    if '自分か相手を選ぶ' not in text:
        return ''
    if '控え室にあるメンバーカード' in text and 'デッキの一番下' in text:
        return 'implemented_other_family_green_member_bottom'
    if '控え室にあるライブカード' in text and 'デッキの一番下' in text and 'カードを1枚引く' in text:
        return 'implemented_other_family_green_live_bottom_draw'
    if 'デッキの一番上のカードを見る' in text and '控え室に置いてもよい' in text:
        return 'implemented_top1_optional_green'
    if 'デッキの上からカードを2枚見る' in text and '好きな枚数を好きな順番でデッキの上に置き' in text and '残りを控え室' in text:
        return 'implemented_topk_reorder_keep_any'
    return 'needs_audit_unmatched_choose_player'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiled', default='./llocg_db_out_full/cards_compiled_v7h.json')
    ap.add_argument('--outdir', default='./loveca_reports')
    args = ap.parse_args()
    data = json.loads(Path(args.compiled).read_text(encoding='utf-8'))
    cards = data.get('cards') if isinstance(data, dict) else data
    rows: List[Dict[str, str]] = []
    for c in cards:
        text = ' '.join(_clauses(c))
        if '自分か相手を選ぶ' not in text:
            continue
        status = classify(text)
        rows.append({
            'cardnumber': str(c.get('cardnumber') or ''),
            'cardname': str(c.get('cardname') or ''),
            'card_type': str(c.get('card_type') or c.get('card_type_norm') or ''),
            'status': status,
            'text': text,
        })
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / 'loveca_choose_player_deck_top_action_family_audit_20260605a.csv'
    md_path = outdir / 'loveca_choose_player_deck_top_action_family_audit_20260605a.md'
    with csv_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['cardnumber','cardname','card_type','status','text'])
        w.writeheader(); w.writerows(rows)
    cnt = Counter(r['status'] for r in rows)
    lines = ['# Loveca choose-player deck-top action family audit 20260605a', '', f'candidates: {len(rows)}']
    for k,v in sorted(cnt.items()):
        lines.append(f'- {k}: {v}')
    lines += ['', '## rows']
    for r in rows:
        lines.append(f"- `{r['cardnumber']}` {r['cardname']} — {r['status']}")
    md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'[OK] wrote {csv_path}')
    print(f'[OK] wrote {md_path}')

if __name__ == '__main__':
    main()
