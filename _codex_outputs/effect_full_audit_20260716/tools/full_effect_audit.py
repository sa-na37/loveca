
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate full-effect audit artifacts without modifying runtime."""
from __future__ import annotations
import csv, io, json, os, re, sys, zipfile, subprocess, hashlib, datetime, random, traceback
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path('/Users/tekitou/Desktop/gsim/loveca')
ZIP = Path('/Users/tekitou/Downloads/loveca_codex_full_effect_audit_20260716.zip')
ZIP_PREFIX = 'loveca_codex_full_effect_audit_20260716/'
OUT = ROOT / '_codex_outputs/effect_full_audit_20260716'
for d in ['debug_commands','logs','screenshots','tools']:
    (OUT/d).mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
from llocg_ui.db import load_cards_db  # type: ignore
from llocg_ui import engine  # type: ignore

COMMON_RESET = """cd /Users/tekitou/Desktop/gsim/loveca

unset LLOCG_START_STAGE LLOCG_START_STAGE_L LLOCG_START_STAGE_C LLOCG_START_STAGE_R \\
  LLOCG_START_HAND LLOCG_START_HAND_SIZE LLOCG_START_SHUFFLE \\
  LLOCG_START_GREEN LLOCG_START_SUCCESS LLOCG_START_RESOLVE \\
  LLOCG_START_DECK_TOP LLOCG_START_DECK_EXACT \\
  LLOCG_START_PHASE LLOCG_START_TURN \\
  LLOCG_START_ENERGY_ACTIVE LLOCG_START_ENERGY_WAIT \\
  LLOCG_DEBUG_PRESET LLOCG_START_DEBUG \\
  LLOCG_DEBUG_LIVE_IN_HAND LLOCG_DEBUG_MEMBER_IN_HAND

export LLOCG_DEBUG_PRESET=effect
export LLOCG_START_PHASE=MAIN
export LLOCG_START_TURN=1
"""
DUMMY_DECK = "PL!-bp4-013,PL!-bp4-020,PL!-bp4-021,PL!-bp4-024,LL-bp5-001,LL-bp5-002,PL!N-PR-004,PL!S-pb1-019,PL!HS-PR-001,PL!SP-PR-004"
DUMMY_STAGE = {'L':'PL!-PR-001','C':'PL!N-PR-003','R':'PL!HS-PR-001'}

def zread_text(name: str) -> str:
    with zipfile.ZipFile(ZIP) as z:
        return z.read(ZIP_PREFIX + name).decode('utf-8-sig')

def read_csv(name: str):
    txt = zread_text(name)
    return list(csv.DictReader(io.StringIO(txt)))

def read_json(name: str):
    return json.loads(zread_text(name))

def write_csv(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(rows)

def norm_text(s: str) -> str:
    s = str(s or '')
    s = s.replace('\r\n','\n').replace('\r','\n')
    s = re.sub(r'\s+', '', s)
    s = s.replace('<（','<(').replace('）>',')>')
    return s

def strip_trigger(effect_text: str) -> str:
    s = str(effect_text or '').strip()
    s = re.sub(r'^<[^>]+>\s*', '', s)
    lines=[ln.strip() for ln in s.splitlines() if ln.strip()]
    return ''.join(lines)

def get_runtime_ability(cards, cardnumber, ability_index):
    ci=cards.get(cardnumber)
    if not ci: return None
    abs=list(getattr(ci,'abilities',[]) or [])
    try: idx=int(ability_index or 1)-1
    except Exception: idx=0
    if 0 <= idx < len(abs): return abs[idx]
    return None

def runtime_effect_blob(ab):
    if not ab: return ''
    parts=[]
    for cl in list(ab.get('clauses',[]) or []):
        parts.append(str(cl.get('effect_template') or cl.get('raw') or ''))
    return ''.join(parts)

def clause_effects(ab):
    out=[]
    if not ab: return out
    for cl in list(ab.get('clauses',[]) or []):
        eff=str(cl.get('effect_template') or cl.get('raw') or '').strip()
        cost=str(cl.get('cost_template') or '').strip()
        raw=str(cl.get('raw') or '').strip()
        if eff:
            out.append((cost, eff, raw))
    return out

def split_candidate_sentences(effect_text: str):
    body=strip_trigger(effect_text)
    # Preserve quoted granted ability as a whole first; also test individual Japanese sentence chunks.
    chunks=[body]
    for p in re.split(r'(?<=。)', body):
        p=p.strip()
        if p: chunks.append(p)
    # common choose headers plus choices are not individually matchable, but inner fragments may be.
    return list(dict.fromkeys(chunks))

def safe_rule_match(text: str):
    try:
        m=engine._match_effect_template(text)
        if m:
            rule, gd=m
            return rule, gd
    except Exception:
        return None
    return None

def safe_build_live_start(cards_db, text: str, cn: str):
    try:
        gs=engine.GameState(root=str(ROOT), code='audit', seed=1, debug=True, phase='MAIN')
        gs.stage={'L':None,'C':None,'R':None}
        return engine._build_live_start_trigger_from_effect(gs, cards_db, text, cn, f'{cn} audit', {'source_cn':cn,'set_idx':0})
    except Exception:
        return None

def infer_pending_from_op(op: str, trigger: str, text: str) -> str:
    op=str(op or '')
    if not op: return ''
    if 'choose' in op or 'retrieve' in op or 'topdeck' in op or 'bottomdeck' in op: return 'selection_pending_or_card_list'
    if 'position_change' in op or 'formation' in op: return 'position_change'
    if 'draw' in op or 'score' in op or 'blade' in op or 'heart' in op or 'energy' in op or 'required' in op: return 'message_ack_or_auto_order'
    if 'manual' in op or 'opponent' in op: return 'confirm_effect'
    return 'effect_template_route'

def classify_style(rule_id: str, op: str, text: str) -> str:
    if re.search(r'PL![A-Z!-]*[-]?[A-Za-z0-9]+|LL-', str(rule_id)+str(op)): return 'CARD_SPECIFIC'
    if any(x in str(op) for x in ['group','named','stage','live_start','live_success','yell','baton','energy','position','success']): return 'GENERIC'
    return 'GENERIC'

def command_for(row, cards_db):
    cn=row['cardnumber']; trig=row.get('primary_trigger') or row.get('triggers') or ''
    hand=[]; stage=dict(DUMMY_STAGE); green=[]; success=[]
    if row.get('card_type') == 'LIVE' or 'ライブ' in trig or 'ライブ' in row.get('effect_text',''):
        hand=[cn]
    else:
        stage['C']=cn
    # keep false/true-ish filler but no success >=3
    cmd=COMMON_RESET
    cmd += f"export LLOCG_START_HAND='{','.join(hand)}'\n" if hand else "export LLOCG_START_HAND=''\n"
    cmd += "export LLOCG_START_HAND_SIZE=0\nexport LLOCG_START_SHUFFLE=0\n"
    for pos,val in stage.items():
        if val: cmd += f"export LLOCG_START_STAGE_{pos}='{val}'\n"
    if green: cmd += f"export LLOCG_START_GREEN='{','.join(green)}'\n"
    if success: cmd += f"export LLOCG_START_SUCCESS='{','.join(success)}'\n"
    cmd += f"export LLOCG_START_DECK_EXACT='{DUMMY_DECK}'\n"
    cmd += "export LLOCG_START_DECK_EXACT_STRICT=1\nexport LLOCG_START_ENERGY_ACTIVE=20\nexport LLOCG_START_ENERGY_WAIT=2\nexport LLOCG_DEBUG_LIVE_IN_HAND=0\nexport LLOCG_DEBUG_MEMBER_IN_HAND=0\nexport LLOCG_START_DEBUG=1\n\npython3 ./run_llocg_ui_web.py\n"
    return cmd

def safe_name(s: str) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]+','_',s)[:180]

def main():
    population=read_csv('loveca_effect_audit_population_enriched_20260716.csv')
    baseline=read_csv('loveca_effect_baseline_test_cases_20260716.csv')
    facts=read_csv('loveca_card_facts_reparsed_20260716.csv')
    source=read_json('cards_min_tokv1_audit_source_20260716.json')
    cards=load_cards_db(ROOT, compiled_path=ROOT/'llocg_db_out_full/cards_compiled_v7h.json', tokv1_path=ROOT/'llocg_db_out_full/cards_min_tokv1.json')
    facts_by_cn={r['cardnumber']:r for r in facts}
    source_by_cn={r['cardnumber']:r for r in source}
    runtime_cardset=set(cards.keys())
    source_cardset=set(source_by_cn.keys())

    db_mismatches=[]
    for cn in sorted(source_cardset | runtime_cardset):
        src=source_by_cn.get(cn); ci=cards.get(cn); fact=facts_by_cn.get(cn,{})
        if src and not ci:
            db_mismatches.append({'cardnumber':cn,'field':'card_presence','audit_value':'present','runtime_value':'missing','severity':'S1','notes':'audit source card missing from runtime DB'})
            continue
        if ci and not src:
            db_mismatches.append({'cardnumber':cn,'field':'card_presence','audit_value':'missing','runtime_value':'present','severity':'S4','notes':'runtime DB card not in audit source fixed population'})
            continue
        if not src or not ci: continue
        for fld in ['cardname','group','unit']:
            av=str(src.get(fld,'') or '')
            rv=str(getattr(ci, 'name' if fld=='cardname' else fld, '') or '')
            if fld=='cardname': rv=str(getattr(ci,'name','') or getattr(ci,'cardname','') or '')
            if norm_text(av)!=norm_text(rv):
                db_mismatches.append({'cardnumber':cn,'field':fld,'audit_value':av,'runtime_value':rv,'severity':'S3','notes':'source/runtime metadata differs'})
        for raw,rep,derived in [('base_hearts_raw','base_hearts_reparsed_json','base_hearts_counts_json'),('required_hearts_raw','required_hearts_reparsed_json','required_hearts_counts_json')]:
            if str(src.get(raw,'') or '').strip() and str(src.get(derived,'') or '').strip() in ('','{}'):
                db_mismatches.append({'cardnumber':cn,'field':derived,'audit_value':src.get(raw,''),'runtime_value':src.get(derived,''),'severity':'S2','notes':'raw heart exists but derived audit source counts empty; classify separately from runtime effect failure'})
            if fact.get(rep) and src.get(derived) and norm_text(fact.get(rep)) != norm_text(src.get(derived)):
                db_mismatches.append({'cardnumber':cn,'field':derived+'_vs_reparsed','audit_value':src.get(derived,''),'runtime_value':fact.get(rep,''),'severity':'S2','notes':'reparsed heart facts differ from source derived counts'})

    mapping=[]; issues=[]; issue_rows=[]; manual=[]
    by_audit={}
    for row in population:
        aid=row['audit_id']; cn=row['cardnumber']; ab=get_runtime_ability(cards, cn, row.get('ability_index'))
        runtime_blob=runtime_effect_blob(ab)
        pop_body=strip_trigger(row.get('effect_text',''))
        runtime_body=strip_trigger(runtime_blob)
        db_mismatch=False
        if ab is None:
            status='UNREACHABLE' if cn in runtime_cardset else 'DB_DATA_MISMATCH'
            db_mismatch=(cn not in runtime_cardset)
        elif pop_body and runtime_body and norm_text(pop_body) not in norm_text(runtime_body) and norm_text(runtime_body) not in norm_text(pop_body):
            status='DB_DATA_MISMATCH'; db_mismatch=True
        else:
            clause_routes=[]
            for cost,eff,raw in clause_effects(ab):
                candidates=[eff]
                if cost and cost != eff: candidates.append((cost+'：'+eff).strip('：'))
                candidates += split_candidate_sentences(eff)
                matched=False
                for cand in candidates:
                    m=safe_rule_match(cand)
                    if m:
                        rule,gd=m; clause_routes.append({'kind':'template','rule_id':rule.get('id',''),'op':rule.get('op',''),'text':cand}); matched=True; break
                    trig=safe_build_live_start(cards,cand,cn)
                    if trig:
                        clause_routes.append({'kind':'live_start_builder','rule_id':trig.get('kind',''),'op':trig.get('kind',''),'text':cand}); matched=True; break
                if not matched:
                    # Known collector families not exposed via _match_effect_template.
                    eff_comp=re.sub(r'\s+','',eff)
                    if 'エール' in eff_comp and any(x in eff_comp for x in ['公開','追加','ブレードハート']):
                        clause_routes.append({'kind':'yell_revealed_collector','rule_id':'_collect_yell_revealed_body_auto_triggers','op':'yell_revealed_body_auto','text':eff})
                    elif '能力を持つ' in eff_comp or '能力を得る' in eff_comp:
                        clause_routes.append({'kind':'nested_granted_ability','rule_id':'runtime_granted_ability','op':'granted_ability','text':eff})
                    else:
                        clause_routes.append({'kind':'unmatched','rule_id':'','op':'','text':eff})
            matched_n=sum(1 for r in clause_routes if r['kind']!='unmatched')
            if not clause_routes:
                status='AMBIGUOUS'
            elif matched_n==len(clause_routes):
                status='IMPLEMENTED'
            elif matched_n>0:
                status='PARTIAL'
            else:
                status='NOT_IMPLEMENTED'
        if db_mismatch:
            db_mismatches.append({'cardnumber':cn,'field':'effect_text','audit_value':row.get('effect_text',''),'runtime_value':runtime_blob,'severity':'S1','notes':f'audit_id={aid}; population effect text differs from runtime compiled ability'})
        # create route fields
        routes=[]
        if ab is not None and not db_mismatch:
            for cost,eff,raw in clause_effects(ab):
                for cand in [eff, cost+'：'+eff if cost else eff] + split_candidate_sentences(eff):
                    m=safe_rule_match(cand)
                    if m:
                        rule,gd=m; routes.append((rule.get('id',''), rule.get('op',''), 'llocg_ui/engine.py')) ; break
                    trig=safe_build_live_start(cards,cand,cn)
                    if trig:
                        routes.append((trig.get('kind',''), trig.get('kind',''), 'llocg_ui/engine.py')) ; break
        matcher=';'.join([r[0] for r in routes])
        symbols=';'.join([r[1] for r in routes])
        files=';'.join(sorted(set(r[2] for r in routes)))
        pending=';'.join(sorted(set(infer_pending_from_op(r[1],row.get('primary_trigger',''),row.get('effect_text','')) for r in routes if infer_pending_from_op(r[1],row.get('primary_trigger',''),row.get('effect_text','')))))
        style='GENERIC' if routes else ('MIXED' if status=='PARTIAL' else '')
        reachable='YES' if ab is not None and status not in ['UNREACHABLE','DB_DATA_MISMATCH'] else 'NO'
        notes=[]
        if row.get('manual_review_reason'): notes.append('manual_review_reason='+row.get('manual_review_reason',''))
        if row.get('nested_granted_ability_count') not in ('','0',0): notes.append('nested_granted_ability_count='+str(row.get('nested_granted_ability_count')))
        if status in ['NOT_IMPLEMENTED','PARTIAL','UNREACHABLE','DB_DATA_MISMATCH','AMBIGUOUS']:
            issue_id=f'ISS-{len(issue_rows)+1:04d}'
            sev='S1' if status=='DB_DATA_MISMATCH' else ('S2' if status in ['NOT_IMPLEMENTED','PARTIAL'] else 'S3')
            issue_rows.append({'issue_id':issue_id,'severity':sev,'audit_id':aid,'test_case_id':'','cardnumber':cn,'cardname':row.get('cardname',''),'result_type':status,'summary':f'{status}: implementation mapping incomplete or data mismatch','expected':'Runtime route reachable and testable','actual':status,'related_code':files,'human_rule_confirmation_required':'YES' if status in ['AMBIGUOUS','DB_DATA_MISMATCH'] else 'NO','fix_direction':'Investigate generic matcher/resolver or DB correction; do not apply during audit.'})
        mapping_row={'audit_id':aid,'cardnumber':cn,'cardname':row.get('cardname',''),'trigger':row.get('primary_trigger') or row.get('triggers',''),'implementation_status':status,'implementation_files':files,'implementation_symbols':symbols,'matcher_or_rule':matcher,'pending_kind':pending,'resolve_path':'cmd_resolve_pending / _exec_auto_trigger / try_apply_effect_template' if files else '','ui_render_path':'llocg_ui/server.py pending modal / state_json' if pending else '','implementation_style':style,'reachable':reachable,'duplicate_route_suspected':'NO','dead_route_suspected':'YES' if status=='UNREACHABLE' else 'NO','notes':' | '.join(notes)}
        mapping.append(mapping_row); by_audit[aid]=mapping_row

    # Test plan and results: preserve 4195 baseline, enrich with concrete but conservative commands and expected high-level checks.
    test_plan=[]; test_results=[]; cmd_count=0
    for t in baseline:
        aid=t['audit_id']; m=by_audit.get(aid,{}); status=m.get('implementation_status','AMBIGUOUS')
        cmd=command_for(t, cards)
        cmd_name=safe_name(t['test_case_id']+'_'+t['cardnumber'])+'.command'
        (OUT/'debug_commands'/cmd_name).write_text(cmd, encoding='utf-8')
        cmd_count+=1
        setup=t.get('setup_requirements') or 'Generated minimal effect preset; refine with valid/invalid candidates before manual UI run.'
        expected=t.get('expected_result') or 'Trigger reaches mapped route; candidates/state/UI must satisfy audit instruction PASS criteria.'
        if status=='IMPLEMENTED':
            result='NEEDS_MANUAL_CONFIRMATION'
            actual='Static route mapped; full UI/state PASS criteria not executed in browser in this audit run.'
        elif status in ['PARTIAL']:
            result='BLOCKED'; actual='Partial route mapping; complete execution would not be reliable until unmapped clause is investigated.'
        elif status in ['NOT_IMPLEMENTED']:
            result='NOT_IMPLEMENTED'; actual='No reachable runtime route found by static matcher/build-trigger audit.'
        elif status in ['UNREACHABLE']:
            result='UNREACHABLE'; actual='Runtime ability/card not reachable from current compiled DB.'
        elif status=='DB_DATA_MISMATCH':
            result='DB_DATA_MISMATCH'; actual='Audit population/source and current runtime compiled DB differ.'
        else:
            result='SPEC_AMBIGUOUS'; actual='Could not prove implementation route or rule semantics from static audit.'
        test_plan.append({**t,'setup_requirements':setup,'expected_result':expected,'debug_command':str(Path('debug_commands')/cmd_name),'generated_by':'full_effect_audit_static_generator','requires_ui':'YES','requires_state_assertion':'YES'})
        test_results.append({'test_case_id':t['test_case_id'],'audit_id':aid,'cardnumber':t['cardnumber'],'cardname':t['cardname'],'ability_index':t.get('ability_index',''),'trigger':t.get('trigger',''),'test_type':t.get('test_type',''),'result':result,'implementation_status':status,'actual_result':actual,'evidence_log':str(Path('logs')/(safe_name(t['test_case_id'])+'.log')),'debug_command':str(Path('debug_commands')/cmd_name),'notes':'PASS intentionally not assigned without full UI/state execution.'})
        (OUT/'logs'/(safe_name(t['test_case_id'])+'.log')).write_text(f"Static audit placeholder for {t['test_case_id']}\nimplementation_status={status}\nresult={result}\n", encoding='utf-8')

    # Manual UI checklist
    manual_groups=defaultdict(list)
    for r in test_results:
        if r['result']=='NEEDS_MANUAL_CONFIRMATION': manual_groups[r['cardnumber']].append(r)
    manual_md=['# Manual UI checklist\n','\nThese cases have static implementation mapping but require browser/UI and state verification before PASS.\n']
    for cn,items in sorted(manual_groups.items()):
        manual_md.append(f"\n## {cn}\n")
        for it in items[:20]:
            manual_md.append(f"- `{it['test_case_id']}` {it['trigger']} / {it['test_type']} / command: `{it['debug_command']}`\n")
        if len(items)>20: manual_md.append(f"- ... {len(items)-20} more cases\n")
    (OUT/'manual_ui_checklist.md').write_text(''.join(manual_md), encoding='utf-8')

    # Issues markdown
    issues_md=['# Issues\n\nRuntime and DB were not modified during this audit. Issues below are generated from static route/data mapping and require follow-up implementation work.\n']
    for ir in issue_rows:
        cmd=''
        tc=next((x for x in test_results if x['audit_id']==ir['audit_id']), None)
        if tc: cmd=(OUT/tc['debug_command']).read_text(encoding='utf-8') if (OUT/tc['debug_command']).exists() else ''
        issues_md.append(f"\n## {ir['issue_id']} [{ir['severity']}] {ir['summary']}\n")
        issues_md.append(f"- audit_id: `{ir['audit_id']}`\n- card: `{ir['cardnumber']}` {ir['cardname']}\n- result_type: `{ir['result_type']}`\n- expected: {ir['expected']}\n- actual: {ir['actual']}\n- related_code: {ir['related_code']}\n- human_rule_confirmation_required: {ir['human_rule_confirmation_required']}\n- fix_direction: {ir['fix_direction']}\n")
        if cmd:
            issues_md.append('\nDebug command:\n\n```bash\n'+cmd+'\n```\n')
    (OUT/'issues.md').write_text(''.join(issues_md), encoding='utf-8')

    # Coverage rows overall and by trigger/series/risk.
    map_counts=Counter(r['implementation_status'] for r in mapping)
    res_counts=Counter(r['result'] for r in test_results)
    def cov_row(scope_type, scope_value, maps, tests):
        mc=Counter(r['implementation_status'] for r in maps); rc=Counter(r['result'] for r in tests)
        return {'scope_type':scope_type,'scope_value':scope_value,'abilities_total':len(maps),'abilities_mapped':sum(mc[s] for s in ['IMPLEMENTED','PARTIAL']),'abilities_executed':0,'abilities_passed':0,'abilities_failed':mc['PARTIAL']+mc['DB_DATA_MISMATCH'],'abilities_blocked':mc['AMBIGUOUS'],'abilities_not_implemented':mc['NOT_IMPLEMENTED'],'abilities_unreachable':mc['UNREACHABLE'],'abilities_spec_ambiguous':mc['AMBIGUOUS'],'abilities_manual_confirmation':sum(1 for r in maps if r['implementation_status']=='IMPLEMENTED'),'test_cases_total':len(tests),'test_cases_executed':0,'test_cases_passed':0,'test_cases_failed':rc['BLOCKED']+rc['NOT_IMPLEMENTED']+rc['UNREACHABLE']+rc['DB_DATA_MISMATCH']+rc['SPEC_AMBIGUOUS']}
    coverage=[cov_row('overall','all',mapping,test_results)]
    for trig in sorted(set(r['trigger'] for r in mapping)):
        maps=[r for r in mapping if r['trigger']==trig]
        aids={r['audit_id'] for r in maps}; tests=[t for t in test_results if t['audit_id'] in aids]
        coverage.append(cov_row('trigger',trig,maps,tests))
    def series(cn): return cn.split('-')[0] if '-' in cn else cn[:4]
    for ser in sorted(set(series(r['cardnumber']) for r in mapping)):
        maps=[r for r in mapping if series(r['cardnumber'])==ser]
        aids={r['audit_id'] for r in maps}; tests=[t for t in test_results if t['audit_id'] in aids]
        coverage.append(cov_row('series',ser,maps,tests))
    for pr in sorted(set(r.get('audit_priority','') for r in population)):
        aids={r['audit_id'] for r in population if r.get('audit_priority','')==pr}
        maps=[r for r in mapping if r['audit_id'] in aids]; tests=[t for t in test_results if t['audit_id'] in aids]
        coverage.append(cov_row('audit_priority',pr,maps,tests))

    # Write outputs.
    map_fields=['audit_id','cardnumber','cardname','trigger','implementation_status','implementation_files','implementation_symbols','matcher_or_rule','pending_kind','resolve_path','ui_render_path','implementation_style','reachable','duplicate_route_suspected','dead_route_suspected','notes']
    write_csv(OUT/'implementation_mapping.csv', mapping, map_fields)
    plan_fields=list(test_plan[0].keys()) if test_plan else []
    write_csv(OUT/'test_plan_expanded.csv', test_plan, plan_fields)
    res_fields=['test_case_id','audit_id','cardnumber','cardname','ability_index','trigger','test_type','result','implementation_status','actual_result','evidence_log','debug_command','notes']
    write_csv(OUT/'test_results.csv', test_results, res_fields)
    cov_fields=['scope_type','scope_value','abilities_total','abilities_mapped','abilities_executed','abilities_passed','abilities_failed','abilities_blocked','abilities_not_implemented','abilities_unreachable','abilities_spec_ambiguous','abilities_manual_confirmation','test_cases_total','test_cases_executed','test_cases_passed','test_cases_failed']
    write_csv(OUT/'coverage_report.csv', coverage, cov_fields)
    issue_fields=['issue_id','severity','audit_id','test_case_id','cardnumber','cardname','result_type','summary','expected','actual','related_code','human_rule_confirmation_required','fix_direction']
    write_csv(OUT/'issues.csv', issue_rows, issue_fields)
    write_csv(OUT/'db_mismatches.csv', db_mismatches, ['cardnumber','field','audit_value','runtime_value','severity','notes'])

    checkpoint={'last_completed_audit_id':mapping[-1]['audit_id'] if mapping else '', 'completed_ability_count':len(mapping),'completed_test_count':len(test_results),'result_counts':dict(res_counts),'timestamp':datetime.datetime.now().isoformat(),'current_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True).stdout.strip(),'input_hashes':{}}
    with zipfile.ZipFile(ZIP) as z:
        for n in z.namelist():
            if n.startswith(ZIP_PREFIX) and not n.endswith('/'):
                checkpoint['input_hashes'][Path(n).name]=hashlib.sha256(z.read(n)).hexdigest()
    (OUT/'checkpoint.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf-8')

    # Summary
    dirty=subprocess.run(['git','status','--short'],cwd=ROOT,text=True,capture_output=True).stdout
    summary=[]
    summary.append('# Loveca full effect audit summary 20260716\n\n')
    summary.append('## Scope\n\n')
    summary.append(f'- Fixed ability population: {len(population)} audit_id rows.\n')
    summary.append(f'- Baseline test cases preserved: {len(baseline)} rows.\n')
    summary.append(f'- Runtime/DB modified during audit: NO. Only `_codex_outputs/effect_full_audit_20260716` was written.\n')
    summary.append(f'- Worktree dirty at start/current: YES. See `environment_snapshot.txt`; uncommitted changes were not reset.\n')
    summary.append('\n## Implementation Mapping Counts\n\n')
    for k,v in sorted(map_counts.items()): summary.append(f'- {k}: {v}\n')
    summary.append('\n## Test Result Counts\n\n')
    for k,v in sorted(res_counts.items()): summary.append(f'- {k}: {v}\n')
    summary.append('\n## Important Caveat\n\nNo case is marked PASS because the instruction requires both internal state and UI verification. This run completed full static mapping plus generated reproducible commands and manual UI checklist; browser UI execution remains required for PASS classification.\n')
    summary.append('\n## Main Output Files\n\n- `implementation_mapping.csv`\n- `test_plan_expanded.csv`\n- `test_results.csv`\n- `coverage_report.csv`\n- `issues.md` / `issues.csv`\n- `db_mismatches.csv`\n- `debug_commands/`\n- `logs/`\n- `manual_ui_checklist.md`\n')
    (OUT/'audit_summary.md').write_text(''.join(summary), encoding='utf-8')

    readme=[]
    readme.append('# effect_full_audit_20260716 outputs\n\n')
    readme.append('Generated by `_codex_outputs/effect_full_audit_20260716/tools/full_effect_audit.py`. Runtime files were imported for analysis but not modified.\n\n')
    readme.append('Start with `audit_summary.md`, then inspect CSVs. `test_results.csv` intentionally uses `NEEDS_MANUAL_CONFIRMATION` instead of PASS for statically mapped cases until UI/state execution is completed.\n')
    (OUT/'README.md').write_text(''.join(readme), encoding='utf-8')

    print(json.dumps({'population':len(population),'baseline':len(baseline),'mapping_counts':dict(map_counts),'result_counts':dict(res_counts),'issues':len(issue_rows),'db_mismatches':len(db_mismatches),'commands':cmd_count},ensure_ascii=False,indent=2))

if __name__=='__main__':
    try:
        main()
    except Exception:
        (OUT/'logs'/'audit_generator_exception.log').write_text(traceback.format_exc(), encoding='utf-8')
        raise
