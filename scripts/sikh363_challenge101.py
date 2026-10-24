"""Failure-seeking main-agent challenge of diagnostic method, not art."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==101
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
rows={
'grounding':('Exact363 rejects362 and names chest/right hand/flag/face/performance; preserve this failure rather than inherit static praise.',['director363','strategy363']),
'expert_coverage':('Anatomy/contact and source ownership must discriminate rest shape from deformation before geometry repair. Both hand sides avoid actor/viewer naming error.',['cast_findings','director_preferences']),
'film_alignment':('No source material, lighting or geometry edits. Intended supporting quality remains accepted Pashtun, never softened to fit a schematic actor.',['film_language']),
'preferences':('Diagnostic work remains internal and goes directly into repair; no routine Director gate or whole-scene render.',['director_preferences','director363']),
'reference_roles':('Reference14..19s includes spear/whole-body sequence, not merely crest. New cropped evidence informs final clock; static inspection cannot certify real-time speed.',['references']),
'method':('Read-only audit plus fixed visible crops is a discriminating prerequisite; no arbitrary code payload or speculative smoothing of a horse.',['constraints','strategy363']),
'interfaces':('Enumerate both hand rest/posed chains, horse modifiers/base/evaluated sections, spear/flag/rein owners and action consumers before time remapping.',['strategy363','lessons361']),
'efficient_quality':('One saved audit plus four two-frame crops; no repeated full clip. Existing art retained, failed regions stay open; no hidden portrait polishing.',['director_preferences']),
'authority':('Original appearance101/max117, motion28/max41; Sol only. No new spend/tool/provider/cloud/crowd/principal authority.',['director363','routing360'])}
v=dict(outcome='admit',checks={k:dict(status='PASS',observation=t,comparison='Admit diagnosis only; known frame-visible and Director motion failures remain open until actual corrected evidence.',source_ids=ids) for k,(t,ids) in rows.items()},strongest_counterexample='A high-poly horse and reachable hand can still have bulbous chest or broken digits. Inventory counts/bounds and successful save cannot close appearance; visible chest/hand crops and actual motion must drive the subsequent method.',issues=[])
p=r/'results/sikh363/appearance-c101-challenge.json';t=json.dumps(v,indent=2)+'\n'
if p.exists():assert p.read_text()==t
else:p.write_text(t)
if s['stage']=='BRIEFING':print('Prepared');raise SystemExit()
ev={x:bind(x) for x in ['results/sikh363/REQUEST.md','results/sikh363/STRATEGY.md','results/sikh363/AUDIT_HANDLER_REVIEW.md','results/sikh363/appearance-c101-challenge.json']}
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']=='TESTING' and g['plan']!=pk.digest(s['brief']):
  c.retrospective(task,'outcome',dict(attempt='363-diagnosis-'+key,role='diagnostic',origin='director-rejected-source',observations=[dict(requirement=key,status='UNKNOWN',observation='New363 explicit rejection/diagnosis invalidates old test scope; old evidence retained, no artistic closure.')],evidence=ev),'sikh363-a101-'+key+'-reopen')
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']!='OPEN':continue
 response=dict(cause='Source/image review was too generous and lacked explicit chest/hand/spear-signal/flag and phase-specific timing scrutiny.',uncertainty='Chest rest form versus deformation cause, real hand digits and full retime consumer set need actual source evidence.',change_or_retain_rationale='Retain useful garment/skin/tack state; inspect source and visible anatomical interfaces before authoring.',preserve='Original tasks, failures, good layers and exact99 source, no native changes in audit.',test='Actual chest front/side and both hands at stance/crest plus source base/deformation/consumer report.',expected='Causal evidence to choose repair; no diagnosis-only appearance or AV pass.',failure_response='Repair diagnostic coverage or strategy on original remaining limits; do not ask Director to choose algorithm.',target_stage='GROUNDING',plan=pk.digest(s['brief']),gate_digest=pk.digest(g),evidence=ev)
 event='sikh363-a101-'+key+'-response';c.retrospective(task,'response',dict(key=key,response=response),event)
 ch=dict(response_event=event,counterexample=v['strongest_counterexample'],evidence=ev,checks={k:dict(status='PASS',observation=t) for k,t in dict(causal_test=response['test'],actual_method=response['change_or_retain_rationale'],preservation=response['preserve'],authority=rows['authority'][0]).items()})
 c.retrospective(task,'admit',dict(key=key,challenge=ch),'sikh363-a101-'+key+'-admit')
print({k:g['status'] for k,g in c.retrospective_packet(task)['gates'].items()})
