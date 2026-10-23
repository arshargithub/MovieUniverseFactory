"""Fresh main-agent integrated proof challenge; not an independent reviewer."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-continuous-performance';s=c.state(task);assert s['cycle']==25
cfg=pk.read_json(r,'results/sikh362/motion-c25.json')
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
rows={
 'grounding':('Original faithful14–19s action and accepted film quality remain;99 static dressed checks complete, but continuous transitions unreviewed. No old failure has been erased.',['strategy361','controls']),
 'expert_coverage':('Whole horse/rider support, distributed torso/head response, spear/hand/cuff/seat/reins, groom/cloth continuity and actual camera transitions require chronological evidence, not just hero poses.',['controls','director_preferences']),
 'film_alignment':('99 static supporting look is bound beside accepted Pashtun450; the new clip must retain texture/layer hierarchy and living-animal read through moving poses. No lower co-star floor.',['film_language']),
 'preferences':('No routine technical handover; complete isolated passage with one-second handles. Crowd stays deferred and motion25 uses retained authority, no new grant.',['director_preferences','strategy361']),
 'reference_roles':('Reference14–19s is faithful action authority, not a mood board. Timed phase/frame comparison must retain gather, drive, brief crest, accelerated arrival and absorption. Direct fluidity remains Director313 judgment.',['references']),
 'method':('Fixed save/reopen and bounded actual production-camera frame batches only. No new keys, collision repair, retime or weaker render substitution;432x768/16 matches static intended controls.',['constraints','strategy361']),
 'interfaces':('99 fitted seams and24 continuous rein construction may still expose an intermediate crossing. Inspect each of125 frames, both contact owners and original camera-cut boundaries before queueing.',['controls','lessons358']),
 'efficient_quality':('One worker, no whole-scene/Pashtun rerender. Existing static proofs precede continuous render; retain exact frame bindings and stop on known failure rather than render it to completion.',['director_preferences']),
 'authority':('Sol High, original task25/max31; appearance98..107 is separate. No Astra call, cloud, new spend/provider, sound or crowd construction.',['routing360','strategy361'])}
v=dict(outcome='admit',checks={key:dict(status='PASS',observation=text,comparison=cfg['proof'],source_ids=ids) for key,(text,ids) in rows.items()},strongest_counterexample='A complete successful encode can still contain a rigid rider, hovering rein loop, slow pre-contact hooves, cloth penetration or cut discontinuity. Source invariance and sparse images do not disprove these; chronological timed frames and faithful-reference comparison precede the explicitly pending Director full-speed judgment.',issues=[])
p=r/'results/sikh362/motion-c25-challenge.json';text=json.dumps(v,indent=2)+'\n'
if p.exists():assert p.read_text()==text
else:p.write_text(text)
if 'brief' not in s:print('Challenge prepared');raise SystemExit()
ev={p:bind(p) for p in ['results/sikh362/REQUEST.md','results/sikh362/STRATEGY.md','results/sikh362/STATIC_REVIEW99.md','results/sikh362/motion-c25.json','results/sikh362/motion-c25-challenge.json']}
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']=='TESTING' and g['plan']!=pk.digest(s['brief']):
  c.retrospective(task,'outcome',dict(attempt='362-motion25-'+key,role='diagnostic',origin='changed-integrated-proof',observations=[dict(requirement=key,status='UNKNOWN',observation='Integrated99 appearance changes proof conditions; earlier component motion/rein proof is retained but not a complete new-clip pass.')],evidence=ev),'sikh362-motion25-'+key+'-reopen')
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']!='OPEN':continue
 response=dict(cause=cfg['cause'],uncertainty='Unseen transition interfaces and full-speed fluidity remain unproved by static controls.',change_or_retain_rationale=cfg['method'],preserve='Original source/reference, all actions/camera/crowd and failures; only derivative save/render.',test=cfg['proof'],expected='No known source/frame-visible failure, then an explicit Director AV queue, not invented agent listening/playback.',failure_response='Stop on an actual failure and replan the affected interface on original retained limits; no blanket whole-motion pass.',target_stage='STRATEGIZING',plan=pk.digest(s['brief']),gate_digest=pk.digest(g),evidence=ev)
 event='sikh362-motion25-'+key+'-response';c.retrospective(task,'response',dict(key=key,response=response),event)
 challenge=dict(response_event=event,counterexample=v['strongest_counterexample'],evidence=ev,checks={k:dict(status='PASS',observation=x) for k,x in dict(causal_test=cfg['proof'],actual_method=cfg['method'],preservation='Bound99 native and original source clock; reviewed fixed handlers only.',authority='Original25/max31 retained; Sol High, no external operations or new sound/crowd work.').items()})
 c.retrospective(task,'admit',dict(key=key,challenge=challenge),'sikh362-motion25-'+key+'-admit')
print({k:g['status'] for k,g in c.retrospective_packet(task)['gates'].items()})
