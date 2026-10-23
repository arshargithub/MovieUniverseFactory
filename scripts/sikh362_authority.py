"""Exact appearance-only Director362 extension, retaining both original tasks."""
import json
from pathlib import Path
from copy import deepcopy
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.production_allowance import extend
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh362';c=wf.Controller(r,DATABASE)
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
 return bind(str(p.relative_to(r)))
task='sikh335-supporting-appearance';s=c.state(task)
assert s['cycle']==97 and s['max_corrections']==97
decision=dict(task=task,decision='approve_additional_corrections',additional_corrections=10,prior_cycle=97,prior_max_corrections=97,question='Continue original appearance task after361; preserve all remaining motion allowance.',director_reply='up to 10 more appearance cycles approved',source=bind('results/sikh362/REQUEST.md'))
db=write('appearance-allowance.json',decision)
req=dict(text=decision['director_reply'],operations=['code','document'],amendment_task=task,authority=db,rationale='Exact362 appearance-only extension; no reset, motion grant or external authority.')
write('appearance-amendment.json',req);rid='sikh362-appearance-allowance';c.route_request(rid,req)
kt=pk.read_json(r,s['direction']['knowledge_task'])
for p,h in kt['inputs'].items():assert pk.file_hash(r/p)==h,p
kt.update(id='sikh362-appearance',intent='Complete leader/horse dressed appearance, full layer proof and isolated passage; faithful original motion and accepted film floor; crowd deferred.')
for p in ['results/sikh362/REQUEST.md','results/sikh362/STRATEGY.md','results/sikh361/LEARNINGS.md','results/sikh361/CLOSEOUT.md']:
 kt['inputs'][p]=pk.file_hash(r/p)
kt['execution_authority']=dict(source='results/sikh362/REQUEST.md',scope='Ten additional appearance corrections98..107 only, motion25..31 retained. Sol High; no external authority.')
write('appearance-task.json',kt);packet=pk.task_packet(r,kt);assert packet['dispatch_ready'],packet['blockers'];write('appearance-knowledge-packet.json',packet)
sources=deepcopy(s['direction']['context_sources'])
next(x for x in sources if x['id']=='controls')['binding']=bind('results/sikh362/appearance-task.json')
# Reviewed superseded361 detailed method stays bound and available; its active
# authority/exit excerpts suffice beside the full current362 strategy and causal
# layer findings. No required source or original statement is dropped.
next(x for x in sources if x['id']=='strategy361')['lines']=[1,13]
next(x for x in sources if x['id']=='lessons358')['lines']=[5,10]
for sid,p,lines,statement in [
 ('strategy362','results/sikh362/STRATEGY.md',None,'362 adds ten appearance only; preserve motion25..31. Full dressed layer proof before whole leader and isolated passage.'),
 ('lessons361','results/sikh361/LEARNINGS.md',[34,61],'Compile complete layer graph; actual support domain, continuity and canonical state must be proved. Component success does not qualify whole art.')]:
 row=dict(id=sid,binding=bind(p),category='learnings',status='adopted',required=True,statement=statement,scope='Leader/horse only on original tasks; no new spend, providers or crowd.')
 if lines:row['lines']=lines
 sources.append(row)
g=dict(context_sources=sources,knowledge_task='results/sikh362/appearance-task.json',knowledge_digest=packet['packet_digest'],reason='Read361 actual layer failures and97 preflight; explicit362 appearance-only authority supersedes old numerical ceiling, not original direction. Global307 remains blocked.',evidence={'strategy':bind('results/sikh362/STRATEGY.md'),'lessons':bind('results/sikh361/LEARNINGS.md')})
a=extend(c,task,rid,db,'sikh362-appearance-approved',grounding=g)
write('appearance-authority.json',{k:a[k] for k in ('stage','cycle','max_corrections','planning_step')})
print({k:a[k] for k in ('stage','cycle','max_corrections')})
