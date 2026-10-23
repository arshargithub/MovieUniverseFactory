"""Fresh main-agent scope/reuse challenge; admits proof, not artistic approval."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==100
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
rows={
 'grounding':('Current integrated goal requires head/beard/horse appearance, not only the inherited garment proof.99 actual13 controls are retained, original crowd remains deferred.',['strategy362','controls']),
 'expert_coverage':('New whole_look requirement explicitly derives story/camera/anatomy/environment/reuse obligations and keeps all original form/contact checks. No head/horse disappearance into a generic evidence row.',['director_preferences','film_language']),
 'film_alignment':('Actual accepted Pashtun450 remains fixed floor; compare at actual supporting-shot size without demanding identical lighting or identity, and reject a smooth mannequin/horse even if newer.',['film_language']),
 'preferences':('Continue to the integrated review; routine qualification repair is agent-owned. Preserve original allowance/history and no arbitrary polish or time cutoff.',['director_preferences','strategy362']),
 'reference_roles':('Original faithful rear constrains costume/tack use; accepted film constrains whole visible forms/materials. Neither a texture measurement nor a static reference confers full-speed naturalness.',['references','film_language']),
 'method':('Exact99 source and current26 passage are reused without geometry, shader, pose or camera edits. One fresh canonical save/repeat checks actual readback; unchanged bound images may support the broader review, not a different asset.',['constraints','strategy362']),
 'interfaces':('Parent99, canonical283, profile432x768/16 and current trusted handlers must match. Body/crown/cloth, complete bit-to-hand span, saddle and horse surfaces all remain actual image obligations.',['controls','lessons361']),
 'efficient_quality':('Do not rerender125 identical frames merely to relabel the review. Do not use reuse to hide absent head/horse evidence; every known frame/source failure still blocks.',['director_preferences','lessons361']),
 'authority':('Appearance100/max107, same original task; seven later corrections remain. Sol High only, no Astra, spend, cloud, providers, identity/style change or crowd work.',['routing360','strategy362'])}
v=dict(outcome='admit',checks={k:dict(status='PASS',observation=t,comparison='Full original-intent review and actual source/frame checks remain necessary; proof admission is not whole appearance or Director acceptance.',source_ids=ids) for k,(t,ids) in rows.items()},strongest_counterexample='An unchanged canonical frame does not prove all surfaces/poses, and adding whole_look can still rubber-stamp a smooth face, beard shell or clay horse. Source-bound side/reverse/production controls and complete current passage must actually cover those regions; AV remains pending and crowd unqualified.',issues=[])
p=r/'results/sikh362/appearance-c100-challenge.json';text=json.dumps(v,indent=2)+'\n'
if p.exists():assert p.read_text()==text
else:p.write_text(text)
if 'brief' not in s:print('Challenge prepared');raise SystemExit()
ev={p:bind(p) for p in ['results/sikh362/SCOPE100.md','results/sikh362/STATIC_REVIEW99.md','results/sikh362/appearance-c100-challenge.json']}
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']=='TESTING' and g['plan']!=pk.digest(s['brief']):
  c.retrospective(task,'outcome',dict(attempt='362-appearance100-'+key,role='diagnostic',origin='broader-qualification-plan',observations=[dict(requirement=key,status='UNKNOWN',observation='Whole-look derivation scope now explicit; retain prior subproofs, final whole claim must be checked against100 before closure.')],evidence=ev),'sikh362-appearance100-'+key+'-reopen')
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']!='OPEN':continue
 response=dict(cause='Inherited garment-only derivation could falsely stand in for whole leader/horse qualification; actual good99 construction need not be rebuilt.',uncertainty='Full continuous source/frame-visible failure scan and Director AV remain pending; repeated canonical frame is not universal proof.',change_or_retain_rationale='Retain99 native/controls and26 passage; add explicit whole-look derivation, source-bound fresh save/repeat and final broader review.',preserve='All source/geometry/performance/reference roles and failed history; crowd deferred.',test='Canonical repeat plus actual all-angle99 and chronological26 frames must cover every new whole-look item; no image/source-visible failure.',expected='Evidence-backed bounded whole-look/frame review, then explicit Director AV queue, not a fabricated production pass.',failure_response='Repair actual failing requirement on original remaining limits; never relabel an unreviewed region passed.',target_stage='DERIVING',plan=pk.digest(s['brief']),gate_digest=pk.digest(g),evidence=ev)
 event='sikh362-appearance100-'+key+'-response';c.retrospective(task,'response',dict(key=key,response=response),event)
 ch=dict(response_event=event,counterexample=v['strongest_counterexample'],evidence=ev,checks={k:dict(status='PASS',observation=t) for k,t in dict(causal_test=response['test'],actual_method=response['change_or_retain_rationale'],preservation=response['preserve'],authority='100/max107 retained; no new art/spend/provider/identity authority; full-speed Director313 pending.').items()})
 c.retrospective(task,'admit',dict(key=key,challenge=ch),'sikh362-appearance100-'+key+'-admit')
print({k:g['status'] for k,g in c.retrospective_packet(task)['gates'].items()})
