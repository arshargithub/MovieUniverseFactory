"""Preserve failed actual geometry evidence and exhaust, never reset, allowance."""
import json,re,shutil
from pathlib import Path
import numpy as np
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.experiment_ledger import Ledger
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
assert s['cycle']==17 and s['max_corrections']==17
if s['stage']!='REPLAN_REQUIRED':
    d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],
        'Five340 corrections exhausted. No saved complete derivative. Leader numerical settle/attachment completed16/17, crowd still fails. Promised native neutral-body proof was not completed; stop posed-shell tuning and reassess representation.',
        'sikh340-c17-exhausted')
rows=[];events=Ledger(r/'.runtime/experiment-ops.sqlite3').events()
for cycle in range(13,18):
    base=r/f'.runtime/factory-native/sikh340-look-c{cycle}-save'
    run=pk.read_json(r,f'results/sikh335/look01/save-run-c{cycle}.json');assert run['status']=='FAILED'
    retained=out/f'failure-c{cycle}';retained.mkdir(exist_ok=True)
    for name in ('stdout.log','stderr.log'):
        shutil.copy2(base/name,retained/name)
    diagnostic=[]
    for path in sorted(base.glob('*.npz')):
        diagnostic.append({'path':str(path.relative_to(r)),'sha256':pk.file_hash(path),'bytes':path.stat().st_size})
    actors={}
    for name in ('leader','crowd'):
        path=base/(name+'-settle.npz')
        if path.exists():
            q=np.load(path);actors[name]={'maximum_displacement_m':float(q['displacement'].max()),
                'finite':bool(np.isfinite(q['final']).all()),'vertices':len(q['final'])}
    a=next(e for e in events if e['event_id']==f'sikh340-c{cycle}-save-start')
    b=next(e for e in events if e['event_id']==f'sikh340-c{cycle}-save-end')
    row={'cycle':cycle,'status':'FAILED','actors':actors,'diagnostic_arrays':diagnostic,
         'process_wall_seconds':b['monotonic_seconds']-a['monotonic_seconds'],
         'error':re.findall(r'ValueError: (.*)',(base/'stderr.log').read_text())[-1]}
    rows.append(row)
s=c.state(task);motion=c.state('sikh335-continuous-performance')
report={'task':task,'state':{k:s[k] for k in ('stage','cycle','max_corrections')},
        'attempts':rows,'process_wall_seconds':sum(x['process_wall_seconds'] for x in rows),
        'motion_state':{k:motion[k] for k in ('stage','cycle','max_corrections')},
        'new_saved_candidates':0,'new_production_renders':0,'new_external_spend':0,
        'limits':'Numeric geometry evidence only. Native neutral-body drape was NOT_RUN. No full appearance, AV, production, backup or efficiency pass.'}
(out/'exhaustion-c17.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('state','process_wall_seconds','motion_state','new_saved_candidates')}))
