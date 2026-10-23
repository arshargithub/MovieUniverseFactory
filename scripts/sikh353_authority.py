"""Source-reconciled continuation of existing appearance and motion tasks."""
import json,sys
from copy import deepcopy
from pathlib import Path
from datetime import datetime,timezone
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.production_allowance import extend
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger
r=Path(__file__).resolve().parents[1];o=r/'results/sikh353';c=wf.Controller(r,DATABASE)
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;text=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==text,n
 else:p.write_text(text)
name=sys.argv[1];task='sikh335-supporting-appearance' if name=='appearance' else 'sikh335-continuous-performance'
s=c.state(task)
if name=='motion':
 reconciliation=dict(state_digest=pk.digest(s),coverage='Original motion0–12 retained,348 causal audit and actual12 landing review. Narrow precontact speed corrected; whole reference performance, actor/horse appearance and AV not passed.',unknowns='Full-speed judgment Director313. No integrated appearance59/60 plus motion12 proof; legacy state not automatically current.',evidence={p:bind(p) for p in ['results/sikh348/CAUSAL_LEDGER.md','results/sikh335/motion01/landing-review-c12.md','results/sikh353/REQUEST.md']})
 c.migrate_retrospective(task,bind('results/sikh353/REQUEST.md'),reconciliation,'sikh353-motion-retro-migration');s=c.state(task)
kt=pk.read_json(r,s['direction']['knowledge_task'])
for p,h in kt['inputs'].items():
 if pk.file_hash(r/p)!=h:
  assert p=='docs/knowledge/PLANNING_PIPELINE_330.md',p
  kt['inputs'][p]=pk.file_hash(r/p)
kt.update(id=f'sikh353-{name}',intent='Leader and horse only: appearance and faithful rearing motion. Crowd deferred until production ready.')
for p in ['results/sikh353/REQUEST.md','results/sikh353/STRATEGY.md','results/sikh352/CLOSEOUT.md','results/sikh352/LEARNINGS.md','results/sikh352/EVIDENCE_SCOPE_NOTES.md','results/sikh348/CAUSAL_LEDGER.md','results/sikh335/motion01/landing-review-c12.md']:
 kt['inputs'][p]=pk.file_hash(r/p)
kt['execution_authority']=dict(source='results/sikh353/REQUEST.md',scope='Ten total new cycles: six appearance62–67, four motion13–16. Leader/horse only; crowd deferred. No external authority.')
write(f'{name}-task.json',kt);packet=pk.task_packet(r,kt);assert packet['dispatch_ready'],packet['blockers'];write(f'{name}-knowledge-packet.json',packet)
sources=deepcopy(s['direction']['context_sources']);next(x for x in sources if x['id']=='controls')['binding']=bind(f'results/sikh353/{name}-task.json')
# Explicit source excerpts: historical method evidence, not a truncation of
# current authority or required rules. Full files remain hashed and preserved.
for x in sources:
 if x['id']=='strategy352':x['lines']=[9,22]
 if x['id']=='audit348':x['lines']=[24,44]
 if x['id']=='learnings':x['lines']=[1,40]
 if x['id']=='references':x['lines']=[11,37] if name=='appearance' else [11,53]
 if x['id']=='reconciliation351':x['lines']=[3,13]
for sid,p in [('strategy353','results/sikh353/STRATEGY.md'),('lessons352','results/sikh352/LEARNINGS.md')]:
 sources.append(dict(id=sid,binding=bind(p),category='learnings',status='adopted',required=True,statement='Apply causal interface tests and retain scoped successes; leader and horse precede crowd.',scope='Ten total authorized353 corrections, original reference and quality retained.'))
g=dict(context_sources=sources,knowledge_task=f'results/sikh353/{name}-task.json',knowledge_digest=packet['packet_digest'],reason='353 priority/allowance and352 actual evidence reconciled; motion old330 pin updated only for read350 amendment. Stale307 not repinned.',evidence={'strategy':bind('results/sikh353/STRATEGY.md')})
a=extend(c,task,f'sikh353-{name}-allowance',bind(f'results/sikh353/{name}-allowance.json'),f'sikh353-{name}-approved',grounding=g)
write(f'{name}-authority.json',dict(task=task,cycle=a['cycle'],maximum=a['max_corrections'],stage=a['stage']))
if name=='appearance':
 Ledger(r/'.runtime/experiment-ops.sqlite3').append(dict(event_id='sikh353-work-start',experiment_id='sikh335',episode_id='leader353',phase='construction',event_type='work_started',activity_id='sikh353-work',utc=datetime.now(timezone.utc).isoformat(),note='Leader and horse ten total cycle continuation; initial mandatory source bootstrap before interval.'))
print({k:a[k] for k in ('stage','cycle','max_corrections')})
