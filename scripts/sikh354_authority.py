"""Explicit354 authority and fresh grounding; original task/counters retained."""
import json
from copy import deepcopy
from pathlib import Path
from datetime import datetime,timezone
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.production_allowance import extend
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger
r=Path(__file__).resolve().parents[1];o=r/'results/sikh354';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
s=c.state(task);kt=pk.read_json(r,s['direction']['knowledge_task'])
for p,h in kt['inputs'].items():assert pk.file_hash(r/p)==h,p
kt.update(id='sikh354-appearance',intent='Leader and horse whole appearance reconstruction on motion16; crowd deferred.')
for p in ['results/sikh354/REQUEST.md','results/sikh354/STRATEGY.md','results/sikh354/RETRO_AUDIT.md','results/sikh353/LEARNINGS.md','results/sikh353/CLOSEOUT.md']:
 kt['inputs'][p]=pk.file_hash(r/p)
kt['execution_authority']=dict(source='results/sikh354/REQUEST.md',scope='Five appearance corrections68–72; preserve motion16; crowd deferred; no external authority.')
write('appearance-task.json',kt);packet=pk.task_packet(r,kt);assert packet['dispatch_ready'],packet['blockers'];write('appearance-knowledge-packet.json',packet)
sources=deepcopy(s['direction']['context_sources']);next(x for x in sources if x['id']=='controls')['binding']=bind('results/sikh354/appearance-task.json')
for x in sources:
 if x['id']=='strategy353':x['lines']=[10,25]
 if x['id']=='lessons352':x['lines']=[24,38]
for sid,p in [('strategy354','results/sikh354/STRATEGY.md'),('retro354','results/sikh354/RETRO_AUDIT.md'),('lessons353','results/sikh353/LEARNINGS.md')]:
 sources.append(dict(id=sid,binding=bind(p),category='learnings',status='adopted',required=True,statement='Reconstruct failed whole-form appearance, preserve motion16 and original quality/reference authority.',scope='Five appearance68–72; leader/horse before crowd.'))
next(x for x in sources if x['id']=='lessons353')['lines']=[38,78]
g=dict(context_sources=sources,knowledge_task='results/sikh354/appearance-task.json',knowledge_digest=packet['packet_digest'],reason='354 exact allowance and353 failures reconciled. No stale source blindly rehashed;307 historical capsule not repinned.',evidence={'strategy':bind('results/sikh354/STRATEGY.md')})
a=extend(c,task,'sikh354-allowance',bind('results/sikh354/allowance.json'),'sikh354-approved',grounding=g)
write('authority.json',dict(task=task,cycle=a['cycle'],maximum=a['max_corrections'],stage=a['stage']))
Ledger(r/'.runtime/experiment-ops.sqlite3').append(dict(event_id='sikh354-work-start',experiment_id='sikh335',episode_id='leader354',phase='construction',event_type='work_started',activity_id='sikh354-work',utc=datetime.now(timezone.utc).isoformat(),note='Five appearance corrections on motion16; initial mandatory bootstrap not in interval.'))
print({k:a[k] for k in ('stage','cycle','max_corrections')})
