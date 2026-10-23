"""Exact five-per-task amendment, preserving unused appearance82."""
import json
from pathlib import Path
from copy import deepcopy
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.production_allowance import extend
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh358';c=wf.Controller(r,DATABASE)
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
 return bind(str(p.relative_to(r)))
for label,task,cy,mx in [('appearance','sikh335-supporting-appearance',82,82),('motion','sikh335-continuous-performance',16,16)]:
 s=c.state(task)
 if s['max_corrections']==mx+5:
  print(label,'already amended',s['cycle'],s['max_corrections']);continue
 assert s['cycle']==cy and s['max_corrections']==mx
 decision=dict(task=task,decision='approve_additional_corrections',additional_corrections=5,prior_cycle=cy,prior_max_corrections=mx,question='Continuation after357 integrated tack blocker; five more for each task.',director_reply='5 more cycles for appearance and motion each approved',source=bind('results/sikh358/REQUEST.md'))
 db=write(label+'-allowance.json',decision)
 req=dict(text=decision['director_reply'],operations=['code','document'],amendment_task=task,authority=db,rationale='Exact Director358 amendment on original task, preserving unused cycle and history; no native dispatch or spend from amendment.')
 write(label+'-amendment.json',req);rid='sikh358-'+label+'-allowance';c.route_request(rid,req)
 kt=pk.read_json(r,s['direction']['knowledge_task'])
 for p,h in kt['inputs'].items():assert pk.file_hash(r/p)==h,p
 kt.update(id='sikh358-'+label,intent='Integrated supported headstall and consumed rein attachment; leader/horse production proof, crowd deferred.')
 for p in ['results/sikh358/REQUEST.md','results/sikh358/STRATEGY.md','results/sikh357/LEARNINGS.md','results/sikh357/CLOSEOUT.md']:
  kt['inputs'][p]=pk.file_hash(r/p)
 kt['execution_authority']=dict(source='results/sikh358/REQUEST.md',scope='Five additional corrections each on original tasks; preserve appearance82; no external authority.')
 write(label+'-task.json',kt);packet=pk.task_packet(r,kt);assert packet['dispatch_ready'],packet['blockers'];write(label+'-knowledge-packet.json',packet)
 sources=deepcopy(s['direction']['context_sources']);control=next(x for x in sources if x['id']=='controls');control['binding']=bind(f'results/sikh358/{label}-task.json');control['lines']=[1,14]
 # Reviewed original sources remain bound; select the operative excerpts rather
 # than carrying obsolete status prose into every continuation packet. Full
 # native334 and film-state sources were read during358 bootstrap. Current
 # authority lives in REQUEST/STRATEGY358, not these historical status sections.
 bounds={'film_language':[23,27],'constraints':[11,29],
         'strategy357':[9,15]}
 for source in sources:
  if source['id'] in bounds:source['lines']=bounds[source['id']]
 for sid,p in [('strategy358','results/sikh358/STRATEGY.md'),('lessons357','results/sikh357/LEARNINGS.md')]:
  sources.append(dict(id=sid,binding=bind(p),category='learnings',status='adopted',required=True,statement='Correct actual headstall ownership and its consuming rein span; retain357 construction gains and original faithful action reference.',scope='Five additional corrections per original task; crowd excluded, no new spending.'))
 g=dict(context_sources=sources,knowledge_task=f'results/sikh358/{label}-task.json',knowledge_digest=packet['packet_digest'],reason='358 explicit current authority;357 actual images and handler source reviewed. Stale prior motion brief invalidated, not repinned; original direction retained.',evidence={'strategy':bind('results/sikh358/STRATEGY.md')})
 a=extend(c,task,rid,db,'sikh358-'+label+'-approved',grounding=g)
 write(label+'-authority.json',{k:a[k] for k in ('stage','cycle','max_corrections','planning_step')});print(label,{k:a[k] for k in ('stage','cycle','max_corrections')})
