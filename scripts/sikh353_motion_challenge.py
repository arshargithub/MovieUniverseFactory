"""Fresh motion method challenge and retained retrospective response."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);t='sikh335-continuous-performance';cy=c.state(t)['cycle'];out=r/'results/sikh353'
rows={
 'grounding':('Actual reference-3 and12 crest show compact versus hanging lower forelegs. Current actor derivative has a small vertical placement delta from12.','Do not replay root/old costume to repair a local fold.',['strategy353','controls']),
 'expert_coverage':('Animal anatomy, choreography, support, editorial and rider interfaces preserve upper limb/root while articulating lower limb.','Final arrival is an independent invariant.',['learnings','references']),
 'film_alignment':('Larger-than-life supported rear and credible dark horse remain full goal, not numeric motion success.','Appearance65 remains an unaccepted candidate.',['film_language']),
 'preferences':('Leader/horse only; no crowd or incremental known-defect review.','Director AV does not excuse visible defects.',['director_preferences','strategy353']),
 'reference_roles':('Reference14–19s governs whole pose/phase.12 is corrected landing component, not general quality baseline.','Keep original review authority.',['references','controls']),
 'method':('Fixed all-frame capture before writes; rigid sagittal rotation of lower-leg chain; release zero by341. Two unit tests cover activation/bounds and exact arrival interval.','43degrees may overfold; render drive/crest/release and reject unnatural silhouette.',['controls','strategy353']),
 'interfaces':('Upper arm/carpus, root/hind/neck/rider preserved; connected toe/hoof share same rotation.','Deformation and interpenetration can fail despite preserved control transforms.',['constraints']),
 'efficient_quality':('Ten phase samples before full clip. No expensive whole-trailer render.','Static success is not fluidity proof.',['director_preferences']),
 'authority':('Motion13–16 plus appearance62–67, ten total; no new spend or reset.','Original task history retained.',['constraints','strategy353'])}
if cy>=14:
 rows['grounding']=('13 actual consuming branch retains old arrival slowdown despite compact crest.12 independent endpoint proof was never integrated.','Use actual67 ground baseline and source-bound12 method, not label inference.',['strategy353','controls'])
 rows['method']=('Fixed12 support/arrival solve, actual coherent spine/head attachment/arm/real-rein rebind; then13 curl. Negative test rejects observed13 velocity pocket.','Baseline, attachment and reach assumptions can fail before or after render; no numeric artistic pass.',['controls','strategy353'])
 rows['interfaces']=('All17 visible head parts captured relative to head; spear arm re-solved around actual tip; real right hand owns reins.','Local leg keys may no longer meet saddle/stirrups; actual posed interfaces are vetoes.',['constraints'])
 rows['expert_coverage']=('Animal support/phase, mounted-rider balance and prop ownership applied to consuming branch.','Human/horse visual timing and contact remain independent from numeric guards.',['learnings','references'])
if cy>=15:
 rows['grounding']=('Reference2/3 visibly carries spear off ground at rear;14 kept ground tip invariant and did not preserve material grip.','59 contact scaffold was not gesture qualification; retain14 arrival.',['references','controls'])
 rows['method']=('Phase-specific lift/strike/carry and constant shaft station, two-link arm with prior elbow preference; allframe reach/wrist/continuity preflight before mutation.','Numerical feasibility does not prove natural arm, cuffs or forceful gesture.',['controls','strategy353'])
 rows['interfaces']=('Strike300 at actual existing ground, then hand carries pole; horse/root and appearance geometry preserved.','Spear can still enter horse/costume or leave hand visually despite station metric; actual pose views veto.',['constraints'])
if cy==16:
 rows['grounding']=('15 tip slows from -0.938 to -0.295m/s before strike despite held grip; reference requires a firm cue.','A contact-state test without interior velocity missed the same failure already found at hooves.',['references','controls'])
 rows['method']=('Keep material station and horse trajectory; accelerating quadratic downstroke with actual tip velocity guard and15 negative test.','Numeric forcefulness does not prove fluidity or coordinated body weight.',['controls','strategy353'])
v=dict(outcome='admit',checks={k:dict(status='PASS',observation=a,comparison=b,source_ids=ids) for k,(a,b,ids) in rows.items()},strongest_counterexample='Correct accelerating endpoints or material grip can coexist with mechanical whole-body motion, wrong gaze, stiff gesture or malformed cloth. Actual full pose and continuous evidence must veto those. No complete-motion approval from this local proof.',issues=[])
p=out/f'motion-challenge-c{cy}.json'
if not p.exists():p.write_text(json.dumps(v,indent=2)+'\n')
if c.state(t)['planning_step']=='CHALLENGING':
 packet=c.packet(t);v['input_digest']=packet['planning_input_digest'];c.submit(t,packet['actor'],packet['ticket'],v,f'sikh353-motion{cy}-admit')
ev={p:dict(path=p,sha256=pk.file_hash(r/p)) for p in ['results/sikh353/MOTION_STRATEGY.md','results/sikh353/REQUEST.md','results/sikh335/motion01/landing-review-c12.md',f'results/sikh353/motion-challenge-c{cy}.json']}
if cy>=14:
 for pth in ['results/sikh353/INTEGRATION14_STRATEGY.md','results/sikh353/MOTION_INTEGRATION_FINDING.md']+(['results/sikh353/GESTURE15_STRATEGY.md'] if cy>=15 else []):
  ev[pth]=dict(path=pth,sha256=pk.file_hash(r/pth))
for key,g in c.retrospective_packet(t)['gates'].items():
 if g['status']=='TESTING' and g['plan']!=pk.digest(c.state(t)['brief']):
  c.retrospective(t,'outcome',dict(attempt=f'353-motion{cy}-{key}',role='diagnostic',origin='changed-plan',observations=[dict(requirement=key,status='UNKNOWN',observation='Retain12 narrow arrival result; full reference performance remains open.')],evidence=ev),f'sikh353-motion{cy}-{key}-reopen')
for key,g in c.retrospective_packet(t)['gates'].items():
 if g['status']!='OPEN':continue
 response=dict(cause='Current crest lower cannon/pastern remains near vertical, unlike compact reference fold. Whole performance not proven by improved arrival.',uncertainty='Extra sagittal curl may overfold or release awkwardly; reference is monocular and does not uniquely fix3D.',change_or_retain_rationale='Target only lower foreleg chain, preserve all341+ transforms and root/hind/neck/rider rather than globally retime.',preserve='Original whole reference, corrected arrival, current appearance derivative and all task limits. No crowd.',test='All190 captured matrices with exact preservation guards, ten phase frames against actual reference.',expected='Compact credible crest while retaining final landing, or a specific shape/transition failure.',failure_response='Replan targeted fold/release within existing four motion corrections, no handoff as ready.',target_stage='STRATEGIZING',plan=pk.digest(c.state(t)['brief']),gate_digest=pk.digest(g),evidence=ev)
 if cy>=14:
  response.update(cause='13 actual arrival slows because appearance branch omitted separately corrected12 motion.',uncertainty='New base can break head/arm/rein/seat interfaces despite numeric hoof success.',change_or_retain_rationale='Apply tested support solve to actual ground baseline; rebind coherent actor, actual head accessories and real hand reins; then compact curl.',test='Both final hoof velocity series, all190 attachment/contact samples, actual whole phase frames and source reference.',expected='Actual branch accelerates into contact and all coupled interfaces remain plausible, else specific failure retained.',preserve='Original source, appearance geometry, grounded world support and all cumulative task limits; no crowd.')
 if cy>=15:
  response.update(cause='14 preserved permanently grounded spear, unlike reference airborne carry; fixed hand lets pole slide through material grip.',uncertainty='Constant material grip can force unnatural arm/cloth or penetration; strike timing must remain readable.',change_or_retain_rationale='Keep14 horse trajectory; explicit lift/strike/carry and bounded arm solve with constant shaft grip station.',test='Actual190 pose guards then cue/contact/crest/landing images and revealing front hand/arm/cuff.',expected='Visible coordinated cue and carried pole without sliding, wrong wrist or loss of horse landing.',preserve='14 horse/root/arrival, actor geometry, all history and remaining two motion cycles; no crowd.')
 if cy==16:
  response.update(cause='15 downstroke ease-out slows actual tip before strike despite correct held grip.',change_or_retain_rationale='Change only descending lift profile; preserve prelift, constant material grip and14 horse trajectory.',test='15 measured negative velocity control; actual16 tip296–300 must accelerate downward; repeat front and production phase images.',expected='No pre-contact slowing or new arm/cuff/grip defect; whole form remains separately failed.',preserve='Original tasks and all prior evidence; this is the final authorized correction of353 total ten.')
 event=f'sikh353-motion{cy}-{key}-response';c.retrospective(t,'response',dict(key=key,response=response),event)
 challenge=dict(response_event=event,counterexample='Preserved endpoints do not imply anatomical fold or fluid interior.',evidence=ev,checks={k:dict(status='PASS',observation=v) for k,v in dict(causal_test='Direct lower-leg silhouette intervention tests observed crest mismatch.',actual_method='Fixed handler with source capture, pure rotation and arrival invariant.',preservation='No root/hind/neck/rider or341+ change; tested actual output still required.',authority='Four motion cycles from353 total ten, no external authority.').items()})
 if cy>=14:
  challenge['checks']['causal_test']['observation']='Actual source13 failed velocity series is a negative control; apply12 solve and verify consuming branch endpoints.'
  challenge['checks']['preservation']['observation']='Geometry preserved; changed motion requires complete rider/prop/seat/garment validation, not old matrix invariance.'
 if cy>=15:
  challenge['checks']['causal_test']['observation']='Change wrong ground-tip invariant to phase-specific contact and constant material grip, matching actual reference2/3.'
  challenge['checks']['preservation']['observation']='Horse unchanged; changed left arm requires full cuff/cloth/prop and pose review.'
 c.retrospective(t,'admit',dict(key=key,challenge=challenge),f'sikh353-motion{cy}-{key}-admit')
print(c.state(t)['stage'])
