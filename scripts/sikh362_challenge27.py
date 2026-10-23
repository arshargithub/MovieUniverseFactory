"""Fresh boundary/source challenge, not human audiovisual acceptance."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1]; c=wf.Controller(r,DATABASE); task='sikh335-continuous-performance'
s=c.state(task); assert s['cycle']==27
def bind(p): return dict(path=p,sha256=pk.file_hash(r/p))
v=pk.read_json(r,'results/sikh362/motion-c26-challenge.json')
observations={
'grounding':'Actual shot276..356, not landing352, defines the editorial boundary; retain all125 completed26 frames and add377..380 only.',
'expert_coverage':'Chronological frame/source review covers contacts, silhouette, action phases and cut context. Explicit director_motion separately owns full-speed fluidity and weight.',
'film_alignment':'Same99 master, same profile, exact frame readback. No new visual design, source motion or lowered accepted-film floor.',
'preferences':'Complete isolated leader/horse proof with full second handles; principal and crowd remain unfinished context, no routine technical approval gate.',
'reference_roles':'Faithful reference still constrains all action phases. Numeric accelerating landing and static frames cannot establish perceived fluidity.',
'method':'No-edit save plus four missing context frames and canonical283; preserve all qualified26 outputs instead of rerendering them.',
'interfaces':'Exact99 source,432x768/16,24fps; cut357 and final380 must match actual camera sequence. Human AV cannot be passed by native availability.',
'efficient_quality':'Reuse only exact source-bound evidence, not a different asset or future closeup. Do not reconstruct art for a boundary bookkeeping correction.',
'authority':'Original motion27/max31 retained, four later cycles; appearance100/max107 separate. Sol only, no spend/provider/cloud/crowd/new sound.'}
for key,text in observations.items(): v['checks'][key].update(observation=text,comparison='Exact source/frames and explicit pending Director313 AV; no production acceptance.')
v['strongest_counterexample']='A complete129-frame encode may still look robotic at full speed. All known source/frame-visible failures remain agent-owned; Director AV is explicitly NOT_RUN, not an excuse to forward a known defect. Unfinished crowd/principal handles do not qualify those assets.'
p=r/'results/sikh362/motion-c27-challenge.json'; t=json.dumps(v,indent=2)+'\n'
if p.exists(): assert p.read_text()==t
else: p.write_text(t)
if s['stage']=='BRIEFING': print('Prepared'); raise SystemExit()
ev={p:bind(p) for p in ['results/sikh362/BOUNDARY_REPAIR.md','results/sikh362/source26-qualified.json','results/sikh362/motion-c27-challenge.json']}
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']=='TESTING' and g['plan']!=pk.digest(s['brief']):
  c.retrospective(task,'outcome',dict(attempt='362-motion27-'+key,role='diagnostic',origin='actual-boundary-scope',observations=[dict(requirement=key,status='UNKNOWN',observation='Boundary and human modality made explicit; prior observations retained, final exact-scope review pending.')],evidence=ev),'sikh362-motion27-'+key+'-reopen')
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']!='OPEN': continue
 response=dict(cause='Template used landing352 as editorial endpoint and prose-only human AV ownership.',uncertainty='Full-speed effect remains Director judgment; no-edit reuse does not prove it.',change_or_retain_rationale=observations['method'],preserve='All99/26 art, motion, cameras, references and failures.',test='Verify four tail frames, canonical equality and actual129-frame range252..380; preserve explicit NOT_RUN human requirement.',expected='Complete source/image proof and explicit human AV queue.',failure_response='Repair actual failing scope on original limits, never fabricate AV.',target_stage='DERIVING',plan=pk.digest(s['brief']),gate_digest=pk.digest(g),evidence=ev)
 event='sikh362-motion27-'+key+'-response'; c.retrospective(task,'response',dict(key=key,response=response),event)
 ch=dict(response_event=event,counterexample=v['strongest_counterexample'],evidence=ev,checks={k:dict(status='PASS',observation=t) for k,t in dict(causal_test=response['test'],actual_method=response['change_or_retain_rationale'],preservation=response['preserve'],authority=observations['authority']).items()})
 c.retrospective(task,'admit',dict(key=key,challenge=ch),'sikh362-motion27-'+key+'-admit')
print({k:g['status'] for k,g in c.retrospective_packet(task)['gates'].items()})
