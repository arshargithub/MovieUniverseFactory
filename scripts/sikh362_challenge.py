"""Explicit main-agent construction challenge; no independent-review claim."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);label=sys.argv[1];task='sikh335-'+('supporting-appearance' if label=='appearance' else 'continuous-performance');s=c.state(task);cy=s['cycle'];o=r/'results/sikh362';tag=f'{label}-c{cy}';cfg=pk.read_json(r,f'results/sikh362/{tag}.json')
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
rows={
 'grounding':('358 ring endpoints pass but visible span crosses neck; sparse path probes then miss final clearance.86 headstall retained as useful component.','Actual mesh evidence precedes construction.',['strategy362','lessons358']),
 'expert_coverage':('Anatomical tack construction, rig local ownership, rein contact and production framing are coupled.','Whole face/cloth/motion are not certified by tack.',['controls','cast_findings']),
 'film_alignment':('Preserve accepted Pashtun quality floor, leader357 rich coat/beard and dark bay horse.','Do not disguise schematic structure with texture.',['film_language']),
 'preferences':('Leader and horse only; crowd deferred, no incremental failed handover.','Ten appearance98..107, preserve motion25..31; Sol High, no Astra assignment.',['director_preferences','strategy358']),
 'reference_roles':('Reference rearing14–19s remains faithful action authority.','This method does not change reference role or prove AV.',['references']),
 'method':(cfg['method'],'Specific source evidence can disprove geometry assumptions; fixed local implementation only.',['strategy362']),
 'interfaces':('Anatomical bit owner and consuming rein span must agree across rest, crest and impact.','Preserve actual grip endpoint, reconstruct erroneous intermediate path; no generic whole-rig endpoint offset.',['constraints','strategy362']),
 'efficient_quality':('Scoped cheap source/head proof precedes continuous render.','No cosmetic pass while connectivity is wrong.',['director_preferences','lessons358']),
 'authority':('362 adds ten appearance only, original tasks/history retained; Sol High, no Astra or external authority.','Allowance is not production acceptance.',['strategy362','controls'])}
available={x['id'] for x in s['direction']['context_sources']}
if label=='appearance':
 rows['grounding']=('Actual retained full beard is too uniform;87 separated-lock variant was internally rejected.','Preserve density and roots; no incremental appearance pass.',['strategy362','lessons358'])
 rows['expert_coverage']=('Groom flow, density, mouth/cheek rooting, head ownership and intended-frame readability are coupled.','Fine strand count cannot certify a believable full beard.',['controls','cast_findings'])
 rows['interfaces']=('The original face roots and head action own the beard; no second solid layer or competing attachment.','Actual front and both three-quarter images must reject gaps, exposed root strips or shape regression.',['constraints','strategy362'])
 rows['method']=(cfg['method'],'Retained underlying volume and bounded variation still require actual rendered falsification.',['strategy362'])
rows={key:(a,b,[sid if sid in available else 'learnings' for sid in ids]) for key,(a,b,ids) in rows.items()}
v=dict(outcome='admit',checks={k:dict(status='PASS',observation=a,comparison=b,source_ids=ids) for k,(a,b,ids) in rows.items()},strongest_counterexample='Even a conservative static clearance test can produce changing path topology or a visibly unnatural curve across frames. Actual whole path, hand/ring endpoints and intended/reverse views must falsify it; full-speed AV remains pending.',issues=[])
if label=='appearance':v['strongest_counterexample']='Retaining roots and adding strand variation can still yield a smooth dark slab, separated locks, an exposed lip gap or a cheap stylized face in a richer film. Actual front, both three-quarter and intended framing must falsify those failures; numerical preservation is not artistic approval.'
if cfg['steps'][0]['recipe'].get('edits',[{}])[0].get('kind')=='mounted_look361':
 for key,text in {
  'grounding':'95 passes coat/band metrics but96 proves split-chola occlusion.97 invalid below-hem query was rejected before worker;98 samples supported waist height retaining skirt z.',
  'expert_coverage':'Dressed layer order, supported domain, seam weights/flare and stable surface grain must pass actual front/reverse/rest/crest/impact, then whole actor.',
  'interfaces':'Actual coat hem1.075, skirt top1.145 and band1.083..1.168 require underlap and torso-owned upper weights. Probe height>=1.095, original lower flare and actions retained.',
  'method':cfg['method']}.items():
  v['checks'][key]['observation']=text
  v['checks'][key]['comparison']='Actual intended and revealing poses, source texture crop and accepted film control must falsify defects; no material-only concealment or whole-art pass from tests.'
 v['strongest_counterexample']='Even correct supported-height seam queries can create a pinched skirt or miss another occluding layer; all-frame band/coat math did not detect95. Actual early reverse crest/impact must disprove blue interruptions, floating layer and flare regression. Only then whole actor/face/intended frames; full-speed AV remains pending.'
if cfg['steps'][0]['recipe'].get('edits',[{}])[0].get('kind')=='mounted_finish362':
 for key,text in {
  'grounding':'98 actual reverse/front closes the seam component; complete look remains rejected. Measured linear crop domain demonstrates lost contrast, not missing image assignment.',
  'expert_coverage':'Cloth construction, fitted cranial ownership, attached texture scale and supporting-shot visual hierarchy apply. No new anatomy/identity or random replacement groom.',
  'method':cfg['method'],
  'interfaces':'One common monotone deformation affects all eight crown meshes while preserving lower fitted edge. Exact old pigment range is corrected without altering other shader controls; all action keys protected.'}.items():
  v['checks'][key]['observation']=text
  v['checks'][key]['comparison']='Actual front, sides, whole actor/horse and intended poses must distinguish rich cloth/skin from noise or a smooth hat; numerical source controls alone cannot pass.'
 v['strongest_counterexample']='Source-domain contrast correction can create dirty/tiled skin and crossed normal detail can alias; crown rounding can remain a shell or squash its layering. First actual face and intended proof must reject that before dependent views or continuous render.'
p=o/f'{tag}-challenge.json';t=json.dumps(v,indent=2)+'\n'
if p.exists():assert p.read_text()==t
else:p.write_text(t)
if 'brief' not in s:print('Challenge prepared');raise SystemExit(0)
ev={p:bind(p) for p in ['results/sikh362/REQUEST.md','results/sikh362/STRATEGY.md','results/sikh358/LEARNINGS.md',f'results/sikh362/{tag}.json',f'results/sikh362/{tag}-challenge.json']}
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']=='TESTING' and g['plan']!=pk.digest(s['brief']):
  c.retrospective(task,'outcome',dict(attempt=f'362-{tag}-{key}',role='diagnostic',origin='changed-plan',observations=[dict(requirement=key,status='UNKNOWN',observation='Changed integrated tack method leaves original whole-form and motion gates unresolved.')],evidence=ev),f'sikh362-{tag}-{key}-reopen')
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']!='OPEN':continue
 response=dict(cause=cfg.get('cause','Unsupported head-bone-tail anatomy and separate rein consumer caused tan-arch/disconnected tack; whole look and motion remain unqualified.'),uncertainty='Adaptive distance certification may fail on a poor contact or visually unstable route; actual mesh and frame evidence remain decisive.',change_or_retain_rationale=cfg['method'],preserve='Original references,357 integrated scene,action clock and all task failures; no spend.',test=cfg['proof'],expected='Only actual corrected subproof advances; no whole-actor acceptance by bookkeeping.',failure_response='Replan actual failing interface with retained counters, no decorative concealment.',target_stage='STRATEGIZING',plan=pk.digest(s['brief']),gate_digest=pk.digest(g),evidence=ev)
 event=f'sikh362-{tag}-{key}-response';c.retrospective(task,'response',dict(key=key,response=response),event)
 ch=dict(response_event=event,counterexample=v['strongest_counterexample'],evidence=ev,checks={k:dict(status='PASS',observation=x) for k,x in dict(causal_test=cfg['proof'],actual_method=cfg['method'],preservation='Bound current integrated native; fixed tested handler,no arbitrary worker code.',authority='Ten appearance only362 on original tasks, retained motion25..31; Sol default, no new spending,crowd or identity authority.').items()})
 c.retrospective(task,'admit',dict(key=key,challenge=ch),f'sikh362-{tag}-{key}-admit')
print({k:v['status'] for k,v in c.retrospective_packet(task)['gates'].items()})
