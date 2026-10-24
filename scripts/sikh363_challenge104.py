"""Fresh104 revision challenge; preserves rejected103 observations."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==104
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
cfg=pk.read_json(r,'results/sikh363/appearance-c104.json');v=pk.read_json(r,'results/sikh363/appearance-c103-challenge.json')
replacements={
'grounding':'103 actual fist rejected; zero-effect corrective hypothesis falsified. Start99 again, preserve failed103 and actual right-hand negative images.',
'expert_coverage':'Fist must close at real MCP/PIP/DIP and thumb rest over fingers; stronger flexion can still self-intersect. Inspect actual closed silhouette and rein enclosure, not endpoint/length metrics.',
'method':'Fixed more complete joint closure, thumb target on curled middle index. Constant wrist-local pose avoids repeated expensive equivalent solves;190 actual wrist/length checks and rebased existing rein curves still required.',
'interfaces':'Existing right wrist/forearm remain unchanged; actual grip/rein end and thumb/fingers must agree. New chest source rest/evaluated vertices separate shape from rig; true-side camera uses neck base.',
'efficient_quality':'Do not render identical zero-effect corrective controls; actual values and evaluated displacement are exactly zero. Use one hand candidate plus required hand and correctly framed side controls.',
'authority':'Original appearance104/max117, motion30/max41. No new scope, external service/spend/crowd/principal/Astra.24 focused transport/geometry tests are not actual fist acceptance.'}
for key,text in replacements.items():v['checks'][key]['observation']=text
for row in v['checks'].values():row['comparison']=cfg['proof']
v['strongest_counterexample']='Additional curl may turn the old claw into intersecting fingers, or a wrong thumb target may still produce a hook. Efficient local-bone baking can be numerically exact and visually wrong. Actual cropped and full required-shot imagery still veto; no whole art or AV approval.'
p=r/'results/sikh363/appearance-c104-challenge.json';t=json.dumps(v,indent=2)+'\n'
if p.exists():assert p.read_text()==t
else:p.write_text(t)
if s['stage']=='BRIEFING':print('Prepared');raise SystemExit()
ev={p:bind(p) for p in ['results/sikh363/REQUEST.md','results/sikh363/GRIP104_REVIEW.md','results/sikh363/appearance-c103-right_hand-review.json','results/sikh363/appearance-c104-challenge.json']}
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']=='TESTING' and g['plan']!=pk.digest(s['brief']):
  c.retrospective(task,'outcome',dict(attempt='363-grip104-'+key,role='diagnostic',origin='actual103-rejection',observations=[dict(requirement=key,status='UNKNOWN',observation='104 changes failed103 hand method; no previous broader proof carried as current PASS.')],evidence=ev),'sikh363-a104-'+key+'-reopen')
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']!='OPEN':continue
 response=dict(cause='103 modest closure still leaves open claw and angular thumb. Native numeric preservation did not satisfy visible grasp. Horse corrective contribution is exactly zero.',uncertainty='Stronger actual finger curl/thumb-to-middle-index may self-intersect or miss rein; chest mesh versus deformation requires source comparison.',change_or_retain_rationale=cfg['method'],preserve='Exact99 source, wrist/forearm, good garments/materials and all failed history/limits.',test=cfg['proof'],expected='Actual visible closed grasp or clear rejection; useful true-side/source cause data, not a full art pass.',failure_response='Reject visibly wrong candidate; third comparable failed grip triggers method reassessment before another similar patch.',target_stage='GROUNDING',plan=pk.digest(s['brief']),gate_digest=pk.digest(g),evidence=ev)
 event='sikh363-a104-'+key+'-response';c.retrospective(task,'response',dict(key=key,response=response),event)
 ch=dict(response_event=event,counterexample=v['strongest_counterexample'],evidence=ev,checks={k:dict(status='PASS',observation=t) for k,t in dict(causal_test=response['test'],actual_method=response['change_or_retain_rationale'],preservation=response['preserve'],authority=replacements['authority']).items()});c.retrospective(task,'admit',dict(key=key,challenge=ch),'sikh363-a104-'+key+'-admit')
print({k:g['status'] for k,g in c.retrospective_packet(task)['gates'].items()})
