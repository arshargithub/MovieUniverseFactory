"""Exact ten-per-task amendment on retained tasks; no model/native invocation."""
import json
from pathlib import Path
from copy import deepcopy
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.production_allowance import extend
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh361';c=wf.Controller(r,DATABASE)
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
 return bind(str(p.relative_to(r)))
for label,task,cy,mx in [('appearance','sikh335-supporting-appearance',87,87),('motion','sikh335-continuous-performance',21,21)]:
 s=c.state(task)
 if s['max_corrections']==mx+10:
  print(label,'already amended',s['cycle'],s['max_corrections']);continue
 assert s['cycle']==cy and s['max_corrections']==mx
 decision=dict(task=task,decision='approve_additional_corrections',additional_corrections=10,prior_cycle=cy,prior_max_corrections=mx,question='Continue original leader/horse motion and appearance work after358 and policy360.',director_reply='ok go ahead. I am approving 10 cycles each for motion and appearance',source=bind('results/sikh361/REQUEST.md'))
 db=write(label+'-allowance.json',decision)
 req=dict(text=decision['director_reply'],operations=['code','document'],amendment_task=task,authority=db,rationale='Exact Director361 amendment; preserve untouched87, original task, failures, limits and Sol default. No native dispatch or external authority.')
 write(label+'-amendment.json',req);rid='sikh361-'+label+'-allowance';c.route_request(rid,req)
 kt=pk.read_json(r,s['direction']['knowledge_task'])
 for p,h in kt['inputs'].items():assert pk.file_hash(r/p)==h,p
 kt.update(id='sikh361-'+label,intent='Complete leader/horse contact, integrated look and isolated passage; original faithful motion and accepted film floor, crowd deferred.')
 for p in ['results/sikh361/REQUEST.md','results/sikh361/STRATEGY.md','results/sikh358/LEARNINGS.md','results/sikh358/CLOSEOUT.md','docs/engineering-intelligence/STAGE_MODEL_ROUTING.md']:
  kt['inputs'][p]=pk.file_hash(r/p)
 kt['execution_authority']=dict(source='results/sikh361/REQUEST.md',scope='Ten additional corrections each on original tasks; preserve87. Sol High, no Astra grant or external authority.')
 write(label+'-task.json',kt);packet=pk.task_packet(r,kt);assert packet['dispatch_ready'],packet['blockers'];write(label+'-knowledge-packet.json',packet)
 sources=deepcopy(s['direction']['context_sources']);control=next(x for x in sources if x['id']=='controls');control['binding']=bind(f'results/sikh361/{label}-task.json');control['lines']=[1,14]
 # Full documents have been read. Select applicable verbatim excerpts so the
 #48KB packet retains current361 strategy/lessons rather than old pass prose.
 for row in sources:
  if row['id']=='director_preferences':row['lines']=[1,23]
  if row['id']=='strategy358':row['lines']=[7,13]
  if row['id']=='lessons357':row['lines']=[5,14]
 for sid,p,lines,statement in [
  ('strategy361','results/sikh361/STRATEGY.md',None,'361 authorizes ten additional each and a conservative whole-segment proof, then integrated actor/horse review. Old358 endpoint and sparse-projection methods are rejected.'),
  ('lessons358','results/sikh358/LEARNINGS.md',None,'Apply actual anatomical ownership, whole consumer path, final thickness/sampling review, component versus integrated proof and honest cycle accounting.'),
  ('routing360','docs/engineering-intelligence/STAGE_MODEL_ROUTING.md',[1,27],'Sol6.1 High is default for planning/execution/review/retros; Astra needs a separate narrow Director-approved assignment, absent here.')]:
  row=dict(id=sid,binding=bind(p),category='learnings',status='adopted',required=True,statement=statement,scope='Leader/horse only under ten additional each; crowd, new spend and external operations excluded.')
  if lines:row['lines']=lines
  sources.append(row)
 g=dict(context_sources=sources,knowledge_task=f'results/sikh361/{label}-task.json',knowledge_digest=packet['packet_digest'],reason='Reviewed actual358 route failures and360 model policy; all original input/source bytes preserved, latest361 authority supersedes old pass scope. No global307 repin.',evidence={'strategy':bind('results/sikh361/STRATEGY.md'),'lessons':bind('results/sikh358/LEARNINGS.md')})
 a=extend(c,task,rid,db,'sikh361-'+label+'-approved',grounding=g)
 write(label+'-authority.json',{k:a[k] for k in ('stage','cycle','max_corrections','planning_step')});print(label,{k:a[k] for k in ('stage','cycle','max_corrections')})
