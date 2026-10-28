"""Bounded local context helpers. No semantic oracle, sandbox or authority grant."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

from movie_factory import review_control as rc

CATALOG='docs/knowledge/context/rules.json'
LOGS='.runtime/context-hygiene'
SIGNAL=re.compile(r'\b(warn(?:ing)?|error|fail(?:ed|ure)?|exception|traceback|fatal|not_run|blocked)\b',re.I)


def safe(root,relative):
    p=rc.path(root,relative)
    for part in p.relative_to(root.resolve()).parts:
        if part.startswith('.env') or part in {'.git','.aws','.codex','credentials'}:
            raise rc.Blocked('SENSITIVE_PATH')
    return p


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def load(root):
    data=json.loads(safe(root,CATALOG).read_text())
    if data['schema']!=1:raise rc.Blocked('UNKNOWN_SCHEMA')
    for key in ['original','core']:
        if sha(safe(root,data[key]['path']))!=data[key]['sha256']:
            raise rc.Blocked('STALE_'+key.upper())
    paragraphs=[x[2:] for x in safe(root,data['original']['path']).read_text().splitlines() if x.startswith('- ')]
    records=rc.unique(data['rules'])
    if len(paragraphs)!=len(records):raise rc.Blocked('COVERAGE_GAP')
    for i,text in enumerate(paragraphs,1):
        r=records.get(f'R{i:02}',{})
        if r.get('original_text')!=text or hashlib.sha256(text.encode()).hexdigest()!=r.get('sha256'):
            raise rc.Blocked('ALTERED_ORIGINAL_RULE')
        if not r.get('topics') and not r.get('core_sections'):raise rc.Blocked('UNMAPPED_RULE')
        for topic in r.get('topics',[]):
            if r['id'] not in data['topics'][topic]['rules']:raise rc.Blocked('ROUTE_MAP_MISMATCH')
    for topic,entry in data['topics'].items():
        if not set(entry['requires'])<=set(data['topics']) or not set(entry['rules'])<=set(records):
            raise rc.Blocked('INVALID_ROUTE')
        for rid in entry['rules']:
            if topic not in records[rid]['topics']:raise rc.Blocked('ROUTE_MAP_MISMATCH')
    return data,records


def route(root,topics,budget=24000):
    data,records=load(root)
    if not topics or set(topics)-set(data['topics']):raise rc.Blocked('UNKNOWN_TOPIC_RECONCILE_SCOPE')
    closure=set(topics);pending=list(topics)
    while pending:
        for dep in data['topics'][pending.pop()]['requires']:
            if dep not in closure:closure.add(dep);pending.append(dep)
    ids=sorted({rid for t in closure for rid in data['topics'][t]['rules']})
    result={'topics':sorted(closure),'rules':[{'id':rid,'text':records[rid]['original_text']} for rid in ids],
            'core_required':data['core'],'catalog_sha256':sha(safe(root,CATALOG)),
            'limits':'Read applicable linked deep sources in full. Topic closure is not semantic completeness or permission to execute.'}
    if len(json.dumps(result,ensure_ascii=False,indent=2))>budget:raise rc.Blocked('MANDATORY_ROUTE_EXCEEDS_BUDGET_SPLIT_SCOPE_OR_EXPLICITLY_EXPAND')
    return result


def current(root):
    load(root)
    adoption=root/'docs/knowledge/context/current397.json'
    if adoption.exists():
        from . import production_governance as gov
        import sqlite3
        a=json.loads(adoption.read_text())
        if a.get('schema')!=1 or a.get('database')!='.runtime/factory-entry.sqlite3':
            raise rc.Blocked('CURRENT397_ADOPTION_SCOPE')
        for b in a['sources'].values():rc.binding(root,b)
        for b in a['protected'].values():rc.binding(root,b)
        db=safe(root,a['database'])
        with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) as con:
            s=gov.snapshot(con)
            progress={t:gov.task_progress(s,t) for t in a['tasks']}
            for t in a['tasks']:
                for b in s['tasks'][t]['history_evidence'].values():rc.binding(root,b)
        status_path=safe(root,'docs/planning/RELEASE_01_STATUS.json');status=json.loads(status_path.read_text())
        return dict(outcome=status['outcome'],exchange=status['substantive_exchange_count'],
            next_checkpoint=status['next_checkpoint_exchange'],governance=progress,
            release_progress=gov.release_progress(s),protected=a['protected'],
            production_review_state='No new artistic approval; Director audiovisual review remains required.',
            legacy307='Preserved, not repinned or cleared. Strict review_control deliver unchanged.',
            next=status.get('current_next_action'),source_bindings=a['sources'],
            details='Explicit397 adoption reads canonical governance fresh; no new cycle, spend or native authority.')
    state=rc.capsule(root)  # all pinned307 state, source, candidate and knowledge checks
    status_path=safe(root,'docs/planning/RELEASE_01_STATUS.json')
    status=json.loads(status_path.read_text())
    return {'outcome':status['outcome'],'exchange':status['substantive_exchange_count'],
        'next_checkpoint':status['next_checkpoint_exchange'],
        'latest_process':status.get('current_process',status.get('context_cleanup_311',status.get('review_control_307'))),
        'production_review_state':'BLOCKED: '+', '.join(d['id'] for d in state['open_defects']),
        'protected':state['protected'],'open_defects':state['open_defects'],
        'review_fingerprint':state['fingerprint'],'capabilities':state['capabilities'],
        'next':status.get('current_next_action','Qualify audiovisual review on existing controls before production correction; cleanup grants no production authority.'),
        'source_bindings':{'status_sha256':sha(status_path),'review_registry_sha256':sha(safe(root,rc.REGISTRY))},
        'details':'Use review_control capsule for full13 scoped requirements; status is read fresh, not copied from a cached summary.'}


def excerpt(root,name,start=1,lines=60,chars=6000):
    if start<1 or not 1<=lines<=400 or not 256<=chars<=16000:raise rc.Blocked('INVALID_EXCERPT_BOUNDS')
    p=safe(root,name)
    chosen=[];used=0;signals=[];signal_count=0;count=0;cut=False
    # UTF8 text only. Binary/nontext input is not silently converted.
    with p.open(encoding='utf-8') as f:
        for count,line in enumerate(f,1):
            if '\0' in line:raise rc.Blocked('BINARY_INPUT')
            if SIGNAL.search(line):
                signal_count+=1
                if len(signals)<12:signals.append({'line':count,'excerpt':line.rstrip()[:200]})
            if start<=count<start+lines:
                if used<chars:
                    piece=line[:chars-used];chosen.append(piece);used+=len(piece)
                    if len(piece)<len(line):cut=True
                else:cut=True
    return {'path':name,'sha256':sha(p),'source_bytes':p.stat().st_size,'total_lines':count,
        'start_line':start,'text':''.join(chosen),'omitted':start>1 or count>=start+lines or cut,
        'signal_count':signal_count,'signals':signals,'signals_omitted':signal_count>len(signals),
        'limits':'Lexical warnings/errors only, including possible false positives. No semantic success judgment. Full artifact remains at path; inspect omitted material when needed.'}


def record(root,kind,result,ident):
    # Metadata only; no prompt/log bodies or command arguments in the use ledger.
    dest=safe(root,LOGS+'/usage.jsonl');dest.parent.mkdir(parents=True,exist_ok=True)
    item={'schema':2,'utc':datetime.now(timezone.utc).isoformat(),'kind':kind,'identity':ident,
          'emitted_utf8_bytes':len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()),
          'source_bytes':result.get('source_bytes'),'sha256':result.get('sha256'),
          'omitted':result.get('omitted'),'tokens':None}
    with dest.open('a') as f:f.write(json.dumps(item)+'\n')


def run(root,label,argv):
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,60}',label) or not argv:raise rc.Blocked('INVALID_RUN')
    folder=safe(root,LOGS+'/runs/'+label);folder.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    with (folder/'stdout.log').open('xb') as out,(folder/'stderr.log').open('xb') as err:
        try:code=subprocess.run(argv,cwd=root,stdout=out,stderr=err,check=False).returncode
        except OSError as exc:code=127;err.write(('Launch failed: '+str(exc)).encode())
    receipt={'exit_code':code,'elapsed_seconds':time.monotonic()-start,
             'stdout':str((folder/'stdout.log').relative_to(root)),
             'stderr':str((folder/'stderr.log').relative_to(root)),
             'stdout_sha256':sha(folder/'stdout.log'),'stderr_sha256':sha(folder/'stderr.log'),
             'limits':'Trusted non-sensitive argv only, no shell. Capturing output does not authorize this command or certify its result.'}
    (folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    result={**receipt,'stdout_summary':excerpt(root,receipt['stdout'],lines=12,chars=1400),
            'stderr_summary':excerpt(root,receipt['stderr'],lines=12,chars=1400)}
    return code,result


def usage(root):
    p=safe(root,LOGS+'/usage.jsonl')
    rows=[json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []
    ids=Counter((r['kind'],r['identity'],r.get('sha256')) for r in rows)
    return {'helper_events':len(rows),'emitted_utf8_bytes':sum(r['emitted_utf8_bytes'] for r in rows if r.get('schema')==2),
            'legacy_events_excluded_from_byte_sum':sum(r.get('schema')!=2 for r in rows),
            'repeated_identical_reads':sum(n-1 for (kind,_,_),n in ids.items() if kind=='read'),
            'tokens':None,'compactions':None,
            'limits':'Only calls through this helper. Not complete conversation/tool telemetry, token savings, cost or latency improvement.'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path.cwd())
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('current');sub.add_parser('usage')
    r=sub.add_parser('route');r.add_argument('--topics',nargs='+',required=True);r.add_argument('--budget',type=int,default=24000)
    e=sub.add_parser('read');e.add_argument('path');e.add_argument('--start-line',type=int,default=1);e.add_argument('--lines',type=int,default=60);e.add_argument('--chars',type=int,default=6000)
    x=sub.add_parser('run');x.add_argument('--label',required=True);x.add_argument('args',nargs=argparse.REMAINDER)
    args=p.parse_args(argv);root=args.root.resolve();code=0
    try:
        if args.command=='current':result=current(root);ident='current'
        elif args.command=='route':result=route(root,args.topics,args.budget);ident=','.join(sorted(args.topics))
        elif args.command=='read':result=excerpt(root,args.path,args.start_line,args.lines,args.chars);ident=args.path
        elif args.command=='usage':result=usage(root);ident='usage'
        else:code,result=run(root,args.label,args.args[1:] if args.args[:1]==['--'] else args.args);ident=args.label
        if args.command!='usage':record(root,args.command,result,ident)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return code if 0<=code<=255 else 1
    except (rc.Blocked, OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(json.dumps({'blocked':True,'error':str(exc)}));return 2


if __name__=='__main__':raise SystemExit(main())
