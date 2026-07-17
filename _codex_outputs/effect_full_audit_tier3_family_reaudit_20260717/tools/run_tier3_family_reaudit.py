#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# BUILD_TAG: tier3_family_reaudit_tool_20260717b
from __future__ import annotations
import csv, json, os, re, shutil, subprocess, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '_codex_outputs' / 'effect_full_audit_tier3_family_reaudit_20260717'
SOURCE = ROOT / '_codex_outputs' / 'effect_full_audit_phase4_final_correction_20260716' / 'backlog' / 'research_backlog_final.csv'
PHASE4_TIER3 = ROOT / '_codex_outputs' / 'effect_full_audit_phase4_20260716' / 'tier3' / 'inconclusive_family_resolution.csv'
COMPILED = ROOT / 'llocg_db_out_full' / 'cards_compiled_v7h.json'
MINDB = ROOT / 'llocg_db_out_full' / 'cards_min_tokv1.json'
sys.path.insert(0, str(ROOT))
RESET_KEYS = ['LLOCG_START_STAGE','LLOCG_START_STAGE_L','LLOCG_START_STAGE_C','LLOCG_START_STAGE_R','LLOCG_START_HAND','LLOCG_START_HAND_SIZE','LLOCG_START_SHUFFLE','LLOCG_START_GREEN','LLOCG_START_SUCCESS','LLOCG_START_RESOLVE','LLOCG_START_DECK_TOP','LLOCG_START_DECK_EXACT','LLOCG_START_DECK_EXACT_STRICT','LLOCG_START_PHASE','LLOCG_START_TURN','LLOCG_START_ENERGY_ACTIVE','LLOCG_START_ENERGY_WAIT','LLOCG_DEBUG_PRESET','LLOCG_START_DEBUG','LLOCG_DEBUG_LIVE_IN_HAND','LLOCG_DEBUG_MEMBER_IN_HAND']
RESULT_FIELDS = ['original_audit_id','canonical_id','cardnumber','cardname','trigger','effect_text','primary_family','secondary_family','setup_id','matcher_route','trigger_reached','resolver_reached','pending_kind','runtime_state_changed','cleanup_checked','undo_checked','ui_required','ui_state_recorded','browser_ui_checked','browser_ui_passed','browser_ui_pending','final_status','reason','recommended_fix_scope','evidence','notes']
TARGET_FIELDS = ['original_audit_id','canonical_id','cardnumber','cardname','trigger','effect_text','previous_status','previous_reason','source_file','card_type','group','unit','cost','score','required_hearts','db_effect_text','db_match']
def read_csv(path):
    with path.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
def write_json(path,obj):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
def run_text(args): return subprocess.run(args,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout
def norm_text(s):
    s=str(s or '')
    for a,b in [('<桃>','<(桃)>'),('<赤>','<(赤)>'),('<黄>','<(黄)>'),('<緑>','<(緑)>'),('<青>','<(青)>'),('<紫>','<(紫)>')]: s=s.replace(a,b)
    return re.sub(r'\s+','',s).strip('。')
def safe_id(aid): return re.sub(r'[^A-Za-z0-9_]+','_',aid.replace('#','_')).strip('_')
def load_db():
    comp=json.loads(COMPILED.read_text(encoding='utf-8'))['cards']; mind=json.loads(MINDB.read_text(encoding='utf-8'))
    return {c['cardnumber']:c for c in comp},{c['cardnumber']:c for c in mind}
def ability_index(aid):
    m=re.search(r'#A(\d+)$',aid); return int(m.group(1))-1 if m else 0
def db_ability_text(card, aid):
    abs=list(card.get('abilities') or []); idx=ability_index(aid)
    if not (0<=idx<len(abs)): return ''
    parts=[]
    for cl in abs[idx].get('clauses') or []:
        raw=str(cl.get('raw') or '').strip(); cost=str(cl.get('cost_template') or '').strip(); eff=str(cl.get('effect_template') or '').strip()
        parts.append(raw or ((cost+'：') if cost else '')+eff)
    return ' / '.join(p for p in parts if p)
def db_clause_effects(card, aid):
    abs=list(card.get('abilities') or []); idx=ability_index(aid)
    if not (0<=idx<len(abs)): return []
    return [str(cl.get('effect_template') or cl.get('raw') or '').strip() for cl in abs[idx].get('clauses') or []]
def family_for(trigger,text,card_type):
    t=text or ''; fam='other'; sec=[]
    if '手札' in t and '控え室' in t: fam='hand_to_green / discard'
    if 'カードを' in t and '引' in t: fam = 'draw' if fam=='other' else fam; sec.append('draw')
    if 'カードを1枚引き' in t and '手札' in t and '控え室' in t: fam='draw_then_discard'; sec.append('hand_to_green / discard')
    if '控え室' in t and '手札に加える' in t: fam='green_to_hand'
    if any(x in t for x in ['デッキの上','デッキの下','一番上','一番下']): fam='topk / reveal / reorder' if ('見る' in t or '公開' in t) else 'deck_top_or_bottom_move'
    if 'エネルギー' in t or '<(E)>' in t or '<E>' in t: fam='energy_active_wait'
    if 'このメンバーの下' in t: fam='energy_under_member'
    if 'ポジションチェンジ' in t or ('エリア' in t and '移動' in t): fam='position / active_wait'
    if trigger=='ライブ開始時' and 'ブレード' in t: fam='live_start_temp_blade'
    if trigger=='ライブ開始時' and any(x in t for x in ['<(桃)>','<(赤)>','<(黄)>','<(緑)>','<(青)>','<(紫)>','<緑>']): fam='live_start_temp_heart'
    if 'ライブの合計スコア' in t or '合計スコア' in t: fam='live_start_score' if trigger=='ライブ開始時' else 'live_success_score' if 'ライブ成功' in trigger else 'stage_count_group_unit_name'
    if '必要ハート' in t: fam='live_start_required_heart'
    if '成功ライブカード置き場' in t: sec.append(fam); fam='success_zone_reference'
    if '相手' in t: sec.append('opponent_state_reference')
    if 'バトンタッチ' in t or '登場したとき' in t: sec.append('baton_touch / stage_entry_history')
    if trigger in ('常時','BODY') and fam=='other': fam='continuous_attribute'
    if any(x in t for x in ['てもよい','まで','好きな枚数']): sec.append('optional_cost')
    if '好きな枚数' in t or '1つ以上' in t: sec.append('multi_select')
    return fam, ';'.join(dict.fromkeys(x for x in sec if x and x!=fam))
def reset_env(env):
    for k in RESET_KEYS: os.environ.pop(k,None)
    os.environ.update(env)
def base_env():
    return {'LLOCG_DEBUG_PRESET':'effect','LLOCG_START_PHASE':'MAIN','LLOCG_START_TURN':'1','LLOCG_START_HAND_SIZE':'0','LLOCG_START_SHUFFLE':'0','LLOCG_START_ENERGY_ACTIVE':'40','LLOCG_START_ENERGY_WAIT':'0','LLOCG_DEBUG_LIVE_IN_HAND':'0','LLOCG_DEBUG_MEMBER_IN_HAND':'0','LLOCG_START_DECK_EXACT_STRICT':'1','LLOCG_START_DECK_EXACT':'LL-bp5-001,LL-bp5-002,PL!N-bp4-030,PL!N-bp3-032,PL!N-bp1-029,PL!S-bp2-026,PL!S-bp2-027,PL!S-bp2-028,PL!HS-bp2-015,PL!HS-bp2-014'}
def command_text(env,port=8812):
    q=lambda v: "'"+str(v).replace("'","'\"'\"'")+"'"
    lines=['#!/usr/bin/env bash','set -euo pipefail','cd /Users/tekitou/Desktop/gsim/loveca','unset '+' '.join(RESET_KEYS)]
    lines += [f'export {k}={q(v)}' for k,v in env.items()]
    lines.append(f'python3 ./run_llocg_ui_web.py --host 127.0.0.1 --port {port} --debug')
    return '\n'.join(lines)+'\n'
def gameplay(st): return {k:st.get(k) for k in ['turn','phase','deck','hand','energy_active','energy_wait','stage','green_room','set_zone','success_zone','pending','used_this_turn']}
def static_route_match(texts):
    from llocg_ui.effects.registry import try_match_effect_template_ext
    for t in texts:
        if str(t or '').strip():
            hit=try_match_effect_template_ext({},str(t))
            if hit:
                rule,gd=hit; return str(rule.get('ext_key') or rule.get('id') or 'matched')
    return ''
def audit_runtime(row):
    from llocg_ui.server import App
    from llocg_ui.views import make_view_state
    cn=row['cardnumber']; trig=row['trigger']; sid=safe_id(row['canonical_id'])
    env=base_env(); env['LLOCG_START_STAGE_C']=cn; env['LLOCG_START_HAND']='PL!N-bp3-009,PL!N-bp1-029,PL!HS-bp2-015'; env['LLOCG_START_GREEN']='PL!N-bp3-009,PL!N-bp1-029,PL!HS-bp2-015,PL!S-bp2-026'
    if '成功ライブカード置き場' in row['effect_text']: env['LLOCG_START_SUCCESS']='PL!N-bp1-029,PL!N-bp3-032'
    reset_env(env); app=App(root=ROOT/'llocg_db_out_full',code='ui',deck_code='1RCBL',seed=1,debug=True)
    st0=app.state_json(); state_dir=OUT/'evidence/state'/sid; ui_dir=OUT/'evidence/ui'/sid; log_dir=OUT/'evidence/logs'; cmd_dir=OUT/'evidence/commands'
    write_json(state_dir/'00_initial.json',st0); write_json(ui_dir/'00_initial_private.json',make_view_state(st0,'private')); write_json(ui_dir/'00_initial_public.json',make_view_state(st0,'public'))
    cmd_dir.mkdir(parents=True,exist_ok=True); (cmd_dir/f'{sid}.command.sh').write_text(command_text(env),encoding='utf-8')
    trigger=resolver=changed=undo=False; pending=''; notes=[]; final=st0; action='state_only'
    try:
        if trig=='起動':
            can=bool(((st0.get('stage_detail') or {}).get('C') or {}).get('can_activate')); action='activate_to_green' if can else 'stage_detail.can_activate=false'
            if can:
                st1=app.cmd('activate_to_green',{'pos':'C'}); final=st1; trigger=True; resolver=bool(st1.get('pending')) or gameplay(st1)!=gameplay(st0); changed=gameplay(st1)!=gameplay(st0); pending=str(((st1.get('pending') or {}).get('kind')) or '')
                write_json(state_dir/'01_after_activate.json',st1); write_json(ui_dir/'01_after_activate_private.json',make_view_state(st1,'private'))
            else: notes.append('UI route did not expose activate button for this setup')
        elif trig=='ライブ開始時':
            action='live_start_command_saved'; notes.append('Full live-set trigger flow not promoted without family browser/runtime representative completion')
        else:
            detail=(st0.get('stage_detail') or {}).get('C') or {}; blob=json.dumps(detail,ensure_ascii=False)+'\n'+'\n'.join(st0.get('log') or [])
            if any(k in blob for k in ['temp_','blade','score','required','bonus','cannot']): trigger=resolver=True
            pending=str(((st0.get('pending') or {}).get('kind')) or ''); notes.append('Continuous/BODY state inspected without mutation')
        if gameplay(final)!=gameplay(st0):
            st_undo=app.cmd('undo',{}); undo=(gameplay(st_undo)==gameplay(st0)); write_json(state_dir/'99_after_undo.json',st_undo)
    except Exception as e: notes.append(f'runtime exception: {type(e).__name__}: {e}')
    log_dir.mkdir(parents=True,exist_ok=True); (log_dir/f'{sid}.log').write_text('\n'.join(str(x) for x in (final.get('log') or []))+'\n',encoding='utf-8')
    return {'setup_id':sid,'trigger_reached':str(trigger).lower(),'resolver_reached':str(resolver).lower(),'pending_kind':pending,'runtime_state_changed':str(changed).lower(),'cleanup_checked':'false','undo_checked':str(undo).lower(),'ui_state_recorded':'true','evidence':f'evidence/state/{sid}; evidence/ui/{sid}; evidence/logs/{sid}.log; evidence/commands/{sid}.command.sh','runtime_notes':'; '.join(notes+[f'action={action}'])}
def status_for(row,matcher,runtime):
    t=row['effect_text']; trig=row['trigger']
    if matcher:
        if runtime['resolver_reached']=='true': return 'IMPLEMENTED_AND_REACHABLE',f'Matched ext route {matcher} and runtime state was recorded for non-browser state check.','no runtime fix'
        return 'IMPLEMENTED_BUT_SETUP_INVALID_PREVIOUSLY',f'Matched ext route {matcher}, but designed setup did not complete resolver; previous Tier3 was likely setup/trigger insufficient.','trigger-specific setup refinement'
    if '相手' in t and any(x in t for x in ['メンバー1人','すべてのライブカード','ほかのすべてのメンバー','手札を1枚']): return 'BLOCKED_BY_ENGINE_CAPABILITY','Effect needs opponent individual/member/live/hand state beyond current aggregate inputs.','engine capability design'
    if any(x in t for x in ['バトンタッチ','移動したとき','エネルギーがエネルギー置き場から','ライブカード置き場から控え室']): return 'TRIGGER_REACHED_RESOLVER_BLOCKED','Event-history trigger/hook family has no matching generic route for DB text.','event ledger + resolver family'
    if trig=='起動' and runtime['trigger_reached']=='false': return 'UI_ROUTE_MISSING','Activated ability did not expose a normal activate route in stage_detail for designed setup.','server/engine activated route'
    if any(x in t for x in ['控え室に置けない','ライブできない','発動しない']): return 'RULE_INTERPRETATION_REQUIRED','Continuous prohibition text requires rules-level enforcement point before implementation judgement.','rules interpretation'
    return 'GENERIC_ROUTE_TEXT_NOT_MATCHED','DB text did not match existing exact/normalized/fragment/generic matchers; not marked NOT_IMPLEMENTED without dedicated resolver audit.','generic matcher family'
def priority_for(status,trig):
    if status in ('TRIGGER_REACHED_RESOLVER_BLOCKED','UI_ROUTE_MISSING') and trig in ('起動','ライブ開始時'): return 'P1'
    if status in ('BLOCKED_BY_ENGINE_CAPABILITY','RULE_INTERPRETATION_REQUIRED'): return 'P3'
    return 'P2'
def main():
    for sub in ['target_61_canonicalized.csv','tier3_reaudit_results.csv','tier3_backlog.csv','family_index.csv','README.md','tier3_reaudit_summary.md','summary_counts.json']:
        p=OUT/sub
        if p.exists(): p.unlink()
    for sub in ['families','evidence','git']:
        p=OUT/sub
        if p.exists(): shutil.rmtree(p)
    compiled,min_db=load_db(); src_rows=[r for r in read_csv(SOURCE) if r.get('research_reason')=='GENERIC_ROUTE_UNRESOLVED']; phase4={r['audit_id']:r for r in read_csv(PHASE4_TIER3)}
    targets=[]; results=[]; backlog=[]
    for src in src_rows:
        aid=src['audit_id']; cn=src['cardnumber']; comp=compiled.get(cn,{}); mind=min_db.get(cn,{})
        dbtxt=db_ability_text(comp,aid); effect=src['effect_text']; dbmatch=str(norm_text(dbtxt)==norm_text(effect) or norm_text(effect) in norm_text(dbtxt)).lower()
        fam,sec=family_for(src['canonical_trigger'],effect,str(comp.get('card_type') or mind.get('card_type_norm') or ''))
        matcher=static_route_match([effect,dbtxt]+db_clause_effects(comp,aid))
        base={'original_audit_id':aid,'canonical_id':aid,'cardnumber':cn,'cardname':src['cardname'],'trigger':src['canonical_trigger'],'effect_text':effect,'previous_status':src['phase4_previous_classification'],'previous_reason':src['research_reason'],'source_file':str(SOURCE.relative_to(ROOT)),'card_type':str(comp.get('card_type') or mind.get('card_type_norm') or ''),'group':str(mind.get('group') or ''),'unit':str(mind.get('unit') or ''),'cost':str(mind.get('cost') or ''),'score':str(mind.get('score') or ''),'required_hearts':str(mind.get('required_hearts_total') or ''),'db_effect_text':dbtxt,'db_match':dbmatch}
        targets.append(base); rt=audit_runtime(base); status,reason,fix=status_for(base,matcher,rt)
        ui_req=str(src['canonical_trigger']=='起動' or any(x in effect for x in ['選ぶ','公開','てもよい','好きな枚数','上か一番下'])).lower()
        res={'original_audit_id':aid,'canonical_id':aid,'cardnumber':cn,'cardname':src['cardname'],'trigger':src['canonical_trigger'],'effect_text':effect,'primary_family':fam,'secondary_family':sec,'setup_id':rt['setup_id'],'matcher_route':matcher or 'NO_MATCH','trigger_reached':rt['trigger_reached'],'resolver_reached':rt['resolver_reached'],'pending_kind':rt['pending_kind'],'runtime_state_changed':rt['runtime_state_changed'],'cleanup_checked':rt['cleanup_checked'],'undo_checked':rt['undo_checked'],'ui_required':ui_req,'ui_state_recorded':rt['ui_state_recorded'],'browser_ui_checked':'false','browser_ui_passed':'false','browser_ui_pending':'true' if ui_req=='true' else 'false','final_status':status,'reason':reason,'recommended_fix_scope':fix,'evidence':rt['evidence'],'notes':f"db_match={dbmatch}; phase4_family={phase4.get(aid,{}).get('primary_family','')}; {rt['runtime_notes']}"}
        results.append(res)
        if status in {'TRIGGER_REACHED_RESOLVER_BLOCKED','UI_ROUTE_MISSING','GENERIC_ROUTE_TEXT_NOT_MATCHED','NOT_IMPLEMENTED_CONFIRMED','BLOCKED_BY_ENGINE_CAPABILITY'}:
            backlog.append({'cardnumber':cn,'canonical_id':aid,'status':status,'reproduction':rt['evidence'],'expected':'Effect reaches trigger/matcher/resolver route with valid setup and applies documented state/UI behavior.','actual':reason,'family':fam,'common_fix_candidate':fix,'affected_files':'llocg_ui/engine.py; llocg_ui/server.py; llocg_ui/effects/registry.py; llocg_ui/effects/*','priority':priority_for(status,src['canonical_trigger']),'evidence':rt['evidence']})
    if len(targets)!=61: raise SystemExit(f'target count must be 61 got {len(targets)}')
    write_csv(OUT/'target_61_canonicalized.csv',targets,TARGET_FIELDS); write_csv(OUT/'tier3_reaudit_results.csv',results,RESULT_FIELDS); write_csv(OUT/'tier3_backlog.csv',backlog,['cardnumber','canonical_id','status','reproduction','expected','actual','family','common_fix_candidate','affected_files','priority','evidence'])
    groups=defaultdict(list)
    for r in results: groups[r['primary_family']].append(r)
    findex=[]
    for fam,rows in sorted(groups.items()):
        fdir=OUT/'families'/safe_id(fam); fdir.mkdir(parents=True,exist_ok=True); write_csv(fdir/'family_results.csv',rows,RESULT_FIELDS); cnt=Counter(r['final_status'] for r in rows); rep=rows[0]
        (fdir/'family_summary.md').write_text(f"# Family: {fam}\n\n- target_count: {len(rows)}\n- representative: {rep['canonical_id']} / {rep['cardnumber']}\n- matcher: {rep['matcher_route']}\n- trigger_hook: {rep['trigger']}\n- resolver: {rep['pending_kind'] or 'none observed'}\n- UI route: {'required for some rows' if any(x['ui_required']=='true' for x in rows) else 'not required for representative state checks'}\n- pass_count: {cnt.get('IMPLEMENTED_AND_REACHABLE',0)}\n- unresolved_count: {len(rows)-cnt.get('IMPLEMENTED_AND_REACHABLE',0)}\n- confirmed_backlog_count: {sum(cnt[s] for s in ['TRIGGER_REACHED_RESOLVER_BLOCKED','UI_ROUTE_MISSING','GENERIC_ROUTE_TEXT_NOT_MATCHED','NOT_IMPLEMENTED_CONFIRMED','BLOCKED_BY_ENGINE_CAPABILITY'])}\n\n## Common Cause\nMost rows remain matcher or event-hook unresolved; no row is promoted to NOT_IMPLEMENTED_CONFIRMED without a dedicated resolver audit.\n\n## Recommended Fix Unit\nImplement by family-level generic matcher/resolver, then run representative browser checks where UI is required.\n",encoding='utf-8')
        findex.append({'primary_family':fam,'target_count':len(rows),'representative_canonical_id':rep['canonical_id'],'implemented_and_reachable':cnt.get('IMPLEMENTED_AND_REACHABLE',0),'backlog_count':sum(cnt[s] for s in ['TRIGGER_REACHED_RESOLVER_BLOCKED','UI_ROUTE_MISSING','GENERIC_ROUTE_TEXT_NOT_MATCHED','NOT_IMPLEMENTED_CONFIRMED','BLOCKED_BY_ENGINE_CAPABILITY']),'statuses':json.dumps(dict(cnt),ensure_ascii=False,sort_keys=True)})
    write_csv(OUT/'family_index.csv',findex,['primary_family','target_count','representative_canonical_id','implemented_and_reachable','backlog_count','statuses'])
    cnt=Counter(r['final_status'] for r in results); summary={'target_total':len(results),'implemented_and_reachable':cnt.get('IMPLEMENTED_AND_REACHABLE',0),'implemented_but_setup_invalid_previously':cnt.get('IMPLEMENTED_BUT_SETUP_INVALID_PREVIOUSLY',0),'implemented_runtime_ui_pending':cnt.get('IMPLEMENTED_RUNTIME_UI_PENDING',0),'trigger_reached_resolver_blocked':cnt.get('TRIGGER_REACHED_RESOLVER_BLOCKED',0),'ui_route_missing':cnt.get('UI_ROUTE_MISSING',0),'generic_route_text_not_matched':cnt.get('GENERIC_ROUTE_TEXT_NOT_MATCHED',0),'rule_interpretation_required':cnt.get('RULE_INTERPRETATION_REQUIRED',0),'not_implemented_confirmed':cnt.get('NOT_IMPLEMENTED_CONFIRMED',0),'duplicate_or_noncanonical':cnt.get('DUPLICATE_OR_NONCANONICAL',0),'blocked_by_engine_capability':cnt.get('BLOCKED_BY_ENGINE_CAPABILITY',0)}
    write_json(OUT/'summary_counts.json',summary)
    if sum(v for k,v in summary.items() if k!='target_total') != len(results): raise SystemExit('status total mismatch')
    (OUT/'README.md').write_text('# Tier 3 family reaudit 20260717\n\n- runtime_modified = false\n- db_modified = false\n- target_total = 61\n- source = effect_full_audit_phase4_final_correction_20260716/backlog/research_backlog_final.csv\n- scope = Tier 3 GENERIC_ROUTE_UNRESOLVED only\n',encoding='utf-8')
    (OUT/'tier3_reaudit_summary.md').write_text('# Tier 3 Reaudit Summary\n\n'+'\n'.join(f'- {k}: {v}' for k,v in summary.items())+'\n\n## Method\n\nThe 61 Phase 4 final `GENERIC_ROUTE_UNRESOLVED` rows were canonicalized, checked against compiled DB text, grouped by effect family, matched against the current registry, and exercised through conservative runtime state/setup checks. Browser checks were not counted as passed unless actually performed. No runtime or DB files were modified. Rows that still need implementation are split by final status and priority in `tier3_backlog.csv`.\n',encoding='utf-8')
    g=OUT/'git'; g.mkdir(parents=True,exist_ok=True); (g/'status.txt').write_text(run_text(['git','status','--short']),encoding='utf-8'); (g/'diff_stat.txt').write_text(run_text(['git','diff','--stat']),encoding='utf-8')
    zpath=OUT.with_suffix('.zip')
    if zpath.exists(): zpath.unlink()
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(OUT.parent))
    print(json.dumps({'out':str(OUT),'zip':str(zpath),**summary},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
