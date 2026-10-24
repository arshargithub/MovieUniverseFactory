"""Fresh failure-seeking challenge of the hand/corrective candidate."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==103
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
cfg=pk.read_json(r,'results/sikh363/appearance-c103.json')
rows={
'grounding':('Actual101 open claw and front chest failure retained; side crop error acknowledged, not reused as valid shape evidence.',['audit363','director363']),
'expert_coverage':('Actual MCP origins, segment lengths, wrist preservation and opposed thumb are necessary but insufficient; require closed silhouette and real rein path. Corrective versus mesh test precedes sculpt.',['audit363','director_preferences']),
'film_alignment':('Preserve actual99 materials/costume/head identity and accepted Pashtun floor. No texture hiding of chest or glove hiding of fingers.',['film_language']),
'preferences':('Complete hand and horse cause test internally before final faster-action/flag proof. No routine micro-handoff.',['director363','director_preferences']),
'reference_roles':('Faithful spear/rear remains downstream timing authority; hand source anatomy is not derived from a tiny video hand. No claim that diagnostics prove motion.',['references']),
'method':('Targeted right digit closure and hand-owned rein endpoint, no wrist or horse geometry mutation. Mute corrective only during controlled comparison and restore state.',['strategy363','audit363']),
'interfaces':('A tighter fist may still have a backward thumb or rein penetration; inspect actual right283/327 then whole-shot/retimed contact. Side camera uses measured neck base, not misleading chest control.',['audit363','constraints']),
'efficient_quality':('One190-frame hand solve, paired crops and corrective controls, not a whole render. Do not keep a corrective mute if it has no causal effect.',['director_preferences','strategy363']),
'authority':('Original103/max117, motion30/max41. No new grant, tools, spend, providers, cloud, crowd or Astra. Native outcome-owner change passed77 regression controls, not art.',['director363','routing360'])}
v=dict(outcome='admit',checks={k:dict(status='PASS',observation=t,comparison=cfg['proof'],source_ids=ids) for k,(t,ids) in rows.items()},strongest_counterexample='Fixed bone lengths and closer thumb target can still produce a distorted fist. Actual isolated hand silhouette and rein enclosure must reject it. Corrective keys may have zero effect; do not interpret a successful comparison as a repaired horse.',issues=[])
p=r/'results/sikh363/appearance-c103-challenge.json';t=json.dumps(v,indent=2)+'\n'
if p.exists():assert p.read_text()==t
else:p.write_text(t)
if s['stage']=='BRIEFING':print('Prepared');raise SystemExit()
ev={p:bind(p) for p in ['results/sikh363/REQUEST.md','results/sikh363/CAUSAL_AUDIT.md','results/sikh363/HAND_HANDLER_REVIEW.md','results/sikh363/appearance-c103-challenge.json']}
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']=='TESTING' and g['plan']!=pk.digest(s['brief']):
  c.retrospective(task,'outcome',dict(attempt='363-hand103-'+key,role='diagnostic',origin='changed-causal-proof',observations=[dict(requirement=key,status='UNKNOWN',observation='103 hand/corrective test changes prior diagnostic conditions; no old art verdict transferred.')],evidence=ev),'sikh363-a103-'+key+'-reopen')
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']!='OPEN':continue
 response=dict(cause='Open right grip and wrong side crop now observed; numerical hand length did not prove contact. Chest corrective cause remains unknown.',uncertainty='Larger actual MCP closure may still produce bad thumb or rein path; corrective contribution requires controlled image comparison.',change_or_retain_rationale=cfg['method'],preserve='Exact99 horse/materials/costume, wrist, other arm, original failures/tasks/limits.',test=cfg['proof'],expected='Visible closed hand plus causal evidence, not a whole appearance pass from component availability.',failure_response='Reject actual failed hand/coverage, replan original task; do not ask Director to choose pose math.',target_stage='GROUNDING',plan=pk.digest(s['brief']),gate_digest=pk.digest(g),evidence=ev)
 event='sikh363-a103-'+key+'-response';c.retrospective(task,'response',dict(key=key,response=response),event)
 ch=dict(response_event=event,counterexample=v['strongest_counterexample'],evidence=ev,checks={k:dict(status='PASS',observation=t) for k,t in dict(causal_test=response['test'],actual_method=response['change_or_retain_rationale'],preservation=response['preserve'],authority=rows['authority'][0]).items()});c.retrospective(task,'admit',dict(key=key,challenge=ch),'sikh363-a103-'+key+'-admit')
print({k:g['status'] for k,g in c.retrospective_packet(task)['gates'].items()})
