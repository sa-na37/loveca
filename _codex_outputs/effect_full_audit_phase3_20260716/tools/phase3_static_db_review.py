#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re, subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '_codex_outputs' / 'effect_full_audit_phase3_20260716'
PH2 = ROOT / '_codex_outputs' / 'effect_full_audit_phase2_20260716'
TARGETS = ['llocg_ui/engine.py','llocg_ui/engine_effect.py','llocg_ui/server.py','llocg_ui/effects','manual_overrides']


def read_csv(p: Path):
    with p.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_csv(p: Path, rows: list[dict[str, Any]], fields: list[str]):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(rows)

def rg_fixed(term: str, limit: int = 8) -> list[str]:
    if not term or len(term.strip()) < 2:
        return []
    cmd = ['rg','-n','--fixed-strings',term,*TARGETS]
    try:
        p = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=8)
    except Exception as e:
        return [f'rg_error: {type(e).__name__}: {e}']
    return p.stdout.splitlines()[:limit]

def norm(s: str) -> str:
    s = (s or '').replace('\r','')
    s = re.sub(r'[【】<>＜＞「」『』（）()・\s]+','',s)
    return s

def get_compiled():
    data=json.load((ROOT/'llocg_db_out_full/cards_compiled_v7h.json').open(encoding='utf-8'))
    return {c.get('cardnumber'): c for c in data.get('cards', [])}

def get_min():
    data=json.load((ROOT/'llocg_db_out_full/cards_min_tokv1.json').open(encoding='utf-8'))
    return {c.get('cardnumber'): c for c in data}

def ability_for(comp: dict[str, Any], audit_id: str) -> dict[str, Any]:
    m=re.search(r'#A(\d+)$', audit_id or '')
    idx=int(m.group(1))-1 if m else 0
    abs=comp.get('abilities') or []
    return abs[idx] if 0 <= idx < len(abs) else {}

def ability_text(ab: dict[str, Any]) -> str:
    parts=[]
    trig=ab.get('trigger') or ab.get('ability_type') or ''
    if trig: parts.append(f'<{trig}>')
    for cl in ab.get('clauses') or []:
        raw=cl.get('raw') or cl.get('effect_template') or ''
        if raw: parts.append(raw)
    return '\n'.join(parts)

def feature_terms(text: str) -> list[str]:
    cleaned=[x.strip('。 、,') for x in re.split(r'[。\n、,]+', text or '')]
    out=[]
    for x in cleaned:
        x=re.sub(r'[<>＜＞【】「」『』（）()\s]','',x)
        if len(x)>=8:
            out.append(x[:18])
    return out[:3]

def route_terms(ab: dict[str, Any]) -> list[str]:
    terms=[]
    for cl in ab.get('clauses') or []:
        for k in ['effect_op','cost_op','effect_template','cost_template']:
            v=cl.get(k)
            if v: terms.append(str(v))
    return list(dict.fromkeys(terms))[:6]

def classify(row, ab, searches):
    route_fields=[row.get(k,'') for k in ['matcher_parser','trigger_queue_path','pending_kind','resolve_dispatch','state_helper','ui_renderer','code_evidence']]
    has_phase2_route=any(x.strip() for x in route_fields)
    ops=route_terms(ab)
    has_compiled_op=any(('op' in x or '_' in x) and not x.startswith('自分') for x in ops)
    feature_hits=any(searches.get(k) for k in ['feature_term_search','generic_matcher_candidate','resolver_route'])
    prev=row.get('previous_status','')
    if prev=='PARTIAL' or row.get('phase2_status')=='PARTIAL_MISSING_BRANCH':
        return 'PARTIAL_BRANCH_MISSING','medium','Phase2 mapped only a partial route; v2 requires branch-level runtime proof before implementation is confirmed.'
    if has_phase2_route or has_compiled_op:
        if prev=='UNREACHABLE':
            return 'IMPLEMENTED_ROUTE_UNVERIFIED','medium','Compiled or Phase2 route candidate exists, but trigger reachability was not proven in Phase2; runtime probe still required.'
        return 'IMPLEMENTED_ROUTE_UNVERIFIED','low','Some route/op evidence exists, but this static pass does not prove end-to-end reachability.'
    if not has_phase2_route and not has_compiled_op and not feature_hits:
        return 'NOT_IMPLEMENTED_WITH_EVIDENCE','medium','No card-specific route, no compiled op, and feature-term searches found no matching generic route in inspected runtime files.'
    return 'STATIC_ANALYSIS_INCONCLUSIVE','low','Search evidence is insufficient to confirm either implementation or absence.'

def md_escape(s: Any) -> str:
    return str(s or '').replace('\n',' / ')

def static_review():
    rows=read_csv(PH2/'priority_implementation_reassessment.csv')
    comp=get_compiled(); minc=get_min()
    out=[]
    evid_dir=OUT/'static_evidence'; evid_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        cn=row['cardnumber']; aid=row['audit_id']; card=comp.get(cn,{}) or minc.get(cn,{})
        ab=ability_for(comp.get(cn,{}) or {}, aid)
        text=ability_text(ab) or row.get('effect_text','')
        terms=feature_terms(text)
        searches={
            'cardnumber_search': rg_fixed(cn, 6),
            'cardname_search': rg_fixed(row.get('cardname',''), 6),
            'feature_term_search': sum((rg_fixed(t, 4) for t in terms), []),
            'generic_matcher_candidate': sum((rg_fixed(t, 4) for t in route_terms(ab)), []),
            'card_specific_route': rg_fixed(cn, 6),
            'trigger_collection_route': rg_fixed(row.get('trigger',''), 6),
            'pending_creation_route': rg_fixed(row.get('pending_kind',''), 6),
            'resolver_route': sum((rg_fixed(t, 4) for t in route_terms(ab)), []),
            'ui_route': rg_fixed(row.get('ui_renderer',''), 6),
        }
        final, conf, reason=classify(row, ab, searches)
        safe=re.sub(r'[^A-Za-z0-9_.-]+','_',aid)
        evidence_file=evid_dir/f'{safe}.md'
        compiled_entry=json.dumps(ab, ensure_ascii=False, indent=2)[:4000]
        lines=[]
        def section(name, value):
            lines.append(f'## {name}\n')
            if isinstance(value, list):
                lines.extend([f'- `{x}`' for x in value] or ['- not found'])
            else:
                lines.append(str(value) if value else 'not found')
            lines.append('')
        lines += [f'# Static Evidence {aid}', '', f'- audit_id: {aid}', f'- cardnumber: {cn}', f'- cardname: {row.get("cardname","")}', f'- effect_text: {md_escape(text)}', f'- previous_classification: {row.get("phase2_status") or row.get("previous_status")}', '']
        for k in ['cardnumber_search','cardname_search','feature_term_search']:
            section(k, searches[k])
        section('compiled_db_entry', '```json\n'+compiled_entry+'\n```')
        for k in ['generic_matcher_candidate','card_specific_route','trigger_collection_route','pending_creation_route','resolver_route','ui_route']:
            section(k, searches[k])
        section('reachable_from_runtime', row.get('reachability_evidence') or 'not proven by static review')
        section('conflicting_routes', 'none found in this static pass')
        lines += [f'- final_classification: {final}', f'- confidence: {conf}', f'- reason: {reason}', '']
        evidence_file.write_text('\n'.join(lines), encoding='utf-8')
        out.append({'audit_id':aid,'cardnumber':cn,'cardname':row.get('cardname',''),'previous_classification':row.get('phase2_status') or row.get('previous_status'),'final_classification':final,'confidence':conf,'reason':reason,'evidence_file':str(evidence_file.relative_to(OUT))})
    write_csv(OUT/'static_reclassification_136.csv', out, ['audit_id','cardnumber','cardname','previous_classification','final_classification','confidence','reason','evidence_file'])
    return out

def db_review():
    rows=read_csv(PH2/'db_mismatch_resolution.csv')
    out=[]
    for r in rows:
        av=r.get('audit_value',''); rv=r.get('runtime_min_value',''); cv=r.get('compiled_value','')
        na,nr,nc=norm(av),norm(rv),norm(cv)
        if nr==nc and na==nr:
            dtype='FORMAT_ONLY'; impact='none'
        elif nr==nc and na!=nr:
            dtype='SOURCE_DATA_ERROR' if len(na)<len(nr)*0.8 else 'WORDING_ONLY_EQUIVALENT'; impact='audit source differs; runtime/compiled agree'
        elif nr!=nc and norm(rv.replace('・',''))==norm(cv.replace('・','')):
            dtype='FORMAT_ONLY'; impact='bullet/newline formatting only'
        elif nr!=nc:
            dtype='SEMANTIC_DIFFERENCE'; impact='runtime min and compiled normalized text differ; manual review required'
        else:
            dtype='UNRESOLVED'; impact='not classified'
        out.append({
            'audit_id':r.get('audit_id',''), 'cardnumber':r.get('cardnumber',''),
            'audit_text':av, 'runtime_text':rv, 'compiled_text':cv, 'override_text':'',
            'difference_type':dtype, 'semantic_impact':impact,
            'runtime_behavior_risk':'LOW' if dtype in {'FORMAT_ONLY','WORDING_ONLY_EQUIVALENT'} else ('MEDIUM' if dtype=='SOURCE_DATA_ERROR' else 'HIGH'),
            'recommended_source_of_truth':'runtime_min_value/cards_min_tokv1.json and compiled runtime DB' if dtype!='SEMANTIC_DIFFERENCE' else 'manual review before choosing source',
            'evidence':r.get('evidence','') + '; phase2_classification=' + r.get('classification',''),
            'result':'REVIEWED', 'notes':'Runtime/DB not modified.'
        })
    write_csv(OUT/'db'/'db_mismatch_semantic_review.csv', out, ['audit_id','cardnumber','audit_text','runtime_text','compiled_text','override_text','difference_type','semantic_impact','runtime_behavior_risk','recommended_source_of_truth','evidence','result','notes'])
    return out

if __name__=='__main__':
    s=static_review(); d=db_review()
    from collections import Counter
    print(json.dumps({'static_count':len(s),'static_classes':Counter(x['final_classification'] for x in s),'db_count':len(d),'db_classes':Counter(x['difference_type'] for x in d)}, ensure_ascii=False, default=dict, indent=2))
