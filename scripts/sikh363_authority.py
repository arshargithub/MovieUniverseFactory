"""Preserve original rejection/history/unused corrections; exact ten top-ups."""
import json,sys
from pathlib import Path
from copy import deepcopy
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.production_allowance import extend
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh363';c=wf.Controller(r,DATABASE)
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
 return bind(str(p.relative_to(r)))
for label,task,cy,maximum in [('appearance','sikh335-supporting-appearance',100,107),('motion','sikh335-continuous-performance',27,31)]:
 s=c.state(task)
 if s['max_corrections']==maximum+10:
  assert s['cycle']==cy+1;print(label,'already applied',s['cycle'],s['max_corrections']);continue
 if s['cycle']==cy:
  assert s['stage'] in wf.READY
  c.retrospective(task,'outcome',dict(attempt='363-director-rejection',role='production',origin='actual-director-review',observations=[dict(requirement=('whole_look' if label=='appearance' else 'director_motion'),status='FAIL',observation=('Bulbous horse chest, bad right hand, rigid flag and face occlusion fail the intended shot.' if label=='appearance' else 'Full-speed rear too slow; uniform acceleration loses prep. Missing faithful slam/hoist signal, wrong eyeline and rigid flag.'),regressed=True)],evidence={'director':bind('results/sikh363/REQUEST.md')}),'sikh363-'+label+'-rejection')
  kt=pk.read_json(r,s['direction']['knowledge_task']);kt.update(id='sikh363-'+label,intent='Director363 correction: fast phased rear with readable prep, faithful slam/hoist permission, simulated tied flag, face eyeline/visibility and horse chest/right-hand repair; crowd deferred.')
  for p in ['results/sikh363/REQUEST.md','results/sikh363/STRATEGY.md','results/sikh362/LEARNINGS.md','results/sikh362/CLOSEOUT.md']:
   kt['inputs'][p]=pk.file_hash(r/p)
  kt['execution_authority']=dict(source='results/sikh363/REQUEST.md',scope='Ten additional each, original tasks/history/unused authority; Sol only, no external actions.')
  write(label+'-task.json',kt);packet=pk.task_packet(r,kt);assert packet['dispatch_ready'],packet['blockers'];write(label+'-knowledge-packet.json',packet)
  sources=deepcopy(s['direction']['context_sources']);next(x for x in sources if x['id']=='controls')['binding']=bind('results/sikh363/'+label+'-task.json')
  # Reviewed historical method text is superseded by363. Keep exact original
  # sources/statements available, select their applicable goal/interface excerpts
  # rather than carry every old proposed construction into the48KB packet.
  excerpts={'strategy362':[3,6],'strategy357':[12,12],'strategy358':[8,8],'strategy354':[6,6],'strategy361':[1,13]}
  for row in sources:
   if row['id'] in excerpts:row['lines']=excerpts[row['id']]
  # Existing source semantics/authority stay; actual new rejection has its own source.
  for row in sources:
   if row['binding']['path']=='results/sikh362/LEARNINGS.md':row['binding']=bind(row['binding']['path'])
  sources.append(dict(id='director363',binding=bind('results/sikh363/REQUEST.md'),category='director_preferences',status='adopted',required=True,statement='363 rejects362; ten additional each. Phased fast rear, readable prep, faithful slam/hoist signal, real tied-flag cloth, face eyeline/visibility, chest/right-hand repair.',scope='Original isolated leader/horse; no crowd, principal, external authority or model escalation.'))
  sources.append(dict(id='strategy363',binding=bind('results/sikh363/STRATEGY.md'),category='learnings',status='adopted',required=True,statement='Diagnose source form/hand and time consumers; prove cloth persistence on exact action; source/frame/Director AV separate.',scope='Technical strategy under363, not new creative authority.'))
  c.reground(task,sources,'results/sikh363/'+label+'-task.json',packet['packet_digest'],'363 rejects prior scope. Reviewed362 learning additions preserve prior authority and add qualification/editorial/AV limitations; old appearance source hash changed after100 planning and was not caught by prior final freshness check. Preserve stale result and explicitly reground; do not repin global307.','sikh363-'+label+'-reground')
 s=c.state(task);assert s['cycle']==cy+1 and s['max_corrections']==maximum and s['planning_step']=='GROUNDING'
 decision=dict(task=task,decision='approve_additional_corrections',additional_corrections=10,prior_cycle=s['cycle'],prior_max_corrections=maximum,question='363 original-task correction continuation, preserve unused corrections and rejection history.',director_reply='Approving 10 appearance and motion cycles each to address this.',source=bind('results/sikh363/REQUEST.md'))
 db=write(label+'-allowance.json',decision);req=dict(text=decision['director_reply'],operations=['code','document'],amendment_task=task,authority=db,rationale='Explicit ten additional corrections on original task, no native work in amendment.')
 write(label+'-amendment.json',req);rid='sikh363-'+label+'-allowance';c.route_request(rid,req);s=extend(c,task,rid,db,'sikh363-'+label+'-approved')
 write(label+'-authority.json',{k:s[k] for k in ['stage','cycle','max_corrections','planning_step']});print(label,s['cycle'],s['max_corrections'])
