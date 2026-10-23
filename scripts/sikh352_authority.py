"""Extend existing task by the exact four352 corrections with fresh grounding."""
import json
from copy import deepcopy
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.production_allowance import extend
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh352';c=wf.Controller(r,DATABASE);t='sikh335-supporting-appearance'
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n')
s=c.state(t);kt=pk.read_json(r,s['direction']['knowledge_task'])
for p,h in kt['inputs'].items():assert pk.file_hash(r/p)==h,p
kt.update(id='sikh352-coordinated-arm',intent='Coordinated shoulder-elbow-wrist/shaft proof and dependent garment transfer; original whole appearance remains required.')
for p in ['results/sikh352/REQUEST.md','results/sikh352/STRATEGY.md','results/sikh351/CLOSEOUT.md','results/sikh351/DIAGNOSIS.md','results/sikh351/DIAGNOSIS57.md']:
 kt['inputs'][p]=pk.file_hash(r/p)
kt['execution_authority']=dict(source='results/sikh352/REQUEST.md',scope='Four additional appearance corrections58–61 only; motion allowance unchanged, no external spend.')
write('task.json',kt);packet=pk.task_packet(r,kt);assert packet['dispatch_ready'],packet['blockers'];write('knowledge-packet.json',packet)
sources=deepcopy(s['direction']['context_sources'])
next(x for x in sources if x['id']=='controls')['binding']=bind('results/sikh352/task.json')
sources.append(dict(id='strategy352',binding=bind('results/sikh352/STRATEGY.md'),category='learnings',status='adopted',required=True,statement='Coordinate arm and contact constraints; isolate pose versus skinning before independent garment transfer.',scope='Four authorized appearance corrections; no whole actor acceptance.'))
g=dict(context_sources=sources,knowledge_task='results/sikh352/task.json',knowledge_digest=packet['packet_digest'],reason='All351 sources unchanged; add actual351 failure evidence and explicit352 continuation. Old307 capsule remains stale, not repinned.',evidence={'strategy':bind('results/sikh352/STRATEGY.md')})
a=extend(c,t,'sikh352-allowance',bind('results/sikh352/allowance.json'),'sikh352-four-approved',grounding=g)
write('authority-receipt.json',dict(task=t,cycle=a['cycle'],maximum=a['max_corrections'],stage=a['stage'],motion_cycle=c.state('sikh335-continuous-performance')['cycle'],motion_maximum=c.state('sikh335-continuous-performance')['max_corrections']))
print({k:a[k] for k in ('cycle','max_corrections','stage')})
