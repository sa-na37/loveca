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
    'mill_top_k_then_waiting_live_to_deck_nth_optional': 'implemented_mill_top_then_live_deck_nth',
    'live_success_reveal_top_no_bladeheart_score': 'implemented_live_success_reveal_top_no_bladeheart_score',
    'live_success_excess_total_top_reorder_keep_any': 'implemented_live_success_excess_top_reorder',
    'live_start_hand_group_to_deck_top_or_bottom_blade': 'implemented_live_start_hand_group_top_bottom_blade',
    'reveal_top1_cost_le_member_hand_then_self_position_change': 'implemented_reveal_top_cost_member_position_change',
    'look_top_stage_member_count_plus_keep_one_top_rest_waiting': 'implemented_stage_count_top_keep_one',
    'reveal_top_by_all_stage_members_live_score_rest_waiting': 'implemented_stage_count_reveal_live_score',
    'look_top_stage_group_count_keep_one_top_rest_waiting_reveal_score_if_live': 'implemented_stage_group_count_top_keep_reveal_score',
    'look_top_live_total_plus_n_choose_one_rest_waiting': 'implemented_live_total_plus_top_choose',
    'look_top_named_members_optional_then_opponent_wait_cost_blade': 'implemented_named_member_pick_opponent_wait_cost_blade',
    'reveal_until_live_or_cost_ge_member_to_hand_rest_waiting_choice': 'implemented_reveal_until_choice_live_or_cost_member',
    'choose_number_reveal_top_member_cost_compare_hand_or_blade': 'implemented_choose_number_top_cost_compare',
    'mill_top_then_retrieve_if_distinct_group_live_names_at_least': 'implemented_mill_then_distinct_group_live_retrieve',
    'look_top_k_optional_member_gain_icons_if_group_picked': 'implemented_top_member_pick_group_gain_icons',
    'choose_heart_color_reveal_top5_all_match_group_pick_gain_blades': 'implemented_choose_color_reveal_top5_group_pick_blades',
    'stage_named_exists_reveal_topk_named_pick_gain_picked_hearts': 'implemented_stage_named_reveal_pick_gain_picked_hearts',
    'optional_repeat_mill_top1_gain_blade_wait_if_live': 'implemented_optional_repeat_mill_blade_wait',
    'discarded_group_top4_choose2_else_retrieve_live': 'implemented_discarded_group_branch_topk_or_live_retrieve',
    'live_storage_count_choose_group_live_no_live_start_topdeck_gain_icons': 'implemented_live_storage_no_live_start_topdeck_gain_icons',
}

CARD_OVERRIDES = {
    # These are handled by timing-specific parsers rather than _match_effect_template.
    'PL!-bp6-007': ('implemented_live_success_reveal_top_no_bladeheart_score', 'live_success_reveal_top_no_bladeheart_score'),
    'PL!HS-bp6-028': ('implemented_live_success_excess_top_reorder', 'live_success_excess_total_top_reorder_keep_any'),
    'PL!N-PR-003': ('implemented_body_reveal_all_hand_no_live_top5_live', 'body_reveal_all_hand_no_live_top5_live'),
    'PL!N-PR-008': ('implemented_body_reveal_all_hand_no_live_top5_live', 'body_reveal_all_hand_no_live_top5_live'),
    'PL!N-PR-010': ('implemented_body_reveal_all_hand_no_live_top5_live', 'body_reveal_all_hand_no_live_top5_live'),
    'PL!S-bp6-002': ('implemented_live_storage_cleanup_top_or_bottom', 'live_storage_cleanup_top_or_bottom'),
    'PL!S-sd1-009': ('implemented_live_start_hand_group_top_bottom_blade', 'live_start_hand_group_to_deck_top_or_bottom_blade'),
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
        if c.get('cardnumber', '') in CARD_OVERRIDES:
            status, rule_id = CARD_OVERRIDES[c.get('cardnumber', '')]
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
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['cardnumber'], lineterminator='\n')
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
        remaining = [x for x in rows if x['status']=='needs_audit_unmatched_topk'][:40]
        if remaining:
            f.write('\n## Remaining unmatched examples\n\n')
        for r in remaining:
            f.write(f"- `{r['cardnumber']}` {r['cardname']} [{r['trigger']}] {r['effect_template']}\n")
    print(f'[OK] wrote: {csv_path}')
    print(f'[OK] wrote: {md_path}')

if __name__ == '__main__':
    main()
