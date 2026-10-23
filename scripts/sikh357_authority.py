"""Ten-cycle continuation; preserve canonical history and fresh source grounding."""
import json
from pathlib import Path
from copy import deepcopy
from datetime import datetime,timezone
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.production_allowance import extend
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger
r=Path(__file__).resolve().parents[1];o=r/'results/sikh357';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
s=c.state(task);kt=pk.read_json(r,s['direction']['knowledge_task'])
for p,h in kt['inputs'].items():assert pk.file_hash(r/p)==h,p
kt.update(id='sikh357-appearance',intent='Anatomical beard domain and integrated leader appearance on354/71, motion16 preserved, crowd deferred.')
for p in ['results/sikh357/REQUEST.md','results/sikh357/STRATEGY.md','results/sikh354/LEARNINGS.md','results/sikh354/CLOSEOUT.md']:
 kt['inputs'][p]=pk.file_hash(r/p)
kt['execution_authority']=dict(source='results/sikh357/REQUEST.md',scope='Ten appearance corrections73–82; per-cycle review and five-cycle internal strategy checkpoint; no new external authority.')
write('appearance-task.json',kt);packet=pk.task_packet(r,kt);assert packet['dispatch_ready'],packet['blockers'];write('appearance-knowledge-packet.json',packet)
sources=deepcopy(s['direction']['context_sources']);next(x for x in sources if x['id']=='controls')['binding']=bind('results/sikh357/appearance-task.json')
# Older method history remains bound; source text is restricted to actual lessons,
# not recursively appending repeated historical method narratives.
for x in sources:
 if x['id']=='controls':x['lines']=[1,14] # Full descriptor independently validated by knowledge_task.
 if x['id']=='lessons353':x['lines']=[38,50] # Old method history; current354 failures bound in full.
 if x['id']=='strategy354':x['lines']=[5,13]
 if x['id']=='retro354':x['lines']=[1,7]
for sid,p in [('strategy357','results/sikh357/STRATEGY.md'),('lessons354','results/sikh354/LEARNINGS.md')]:
 sources.append(dict(id=sid,binding=bind(p),category='learnings',status='adopted',required=True,statement='Replace invalid inherited follicle domain before density; retain354/71 sash/tack and motion16; review each cycle and cumulative fifth.',scope='Ten appearance73–82 on original task; no crowd or spend.'))
g=dict(context_sources=sources,knowledge_task='results/sikh357/appearance-task.json',knowledge_digest=packet['packet_digest'],reason='357 explicit extension and354 observed failures reconciled; historical307 not repinned. Original references/quality preserved.',evidence={'strategy':bind('results/sikh357/STRATEGY.md')})
a=extend(c,task,'sikh357-allowance-exact',bind('results/sikh357/allowance.json'),'sikh357-approved',grounding=g)
write('authority.json',dict(task=task,cycle=a['cycle'],maximum=a['max_corrections'],stage=a['stage']))
Ledger(r/'.runtime/experiment-ops.sqlite3').append(dict(event_id='sikh357-work-start',experiment_id='sikh335',episode_id='leader357',phase='construction',event_type='work_started',activity_id='sikh357-work',utc=datetime.now(timezone.utc).isoformat(),note='Ten appearance corrections; mandatory bootstrap before this interval not measured.'))
print({k:a[k] for k in ('stage','cycle','max_corrections')})
