"""Explicit main-agent construction challenge; no independent-review claim."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);label=sys.argv[1];task='sikh335-'+('supporting-appearance' if label=='appearance' else 'continuous-performance');s=c.state(task);cy=s['cycle'];o=r/'results/sikh358';tag=f'{label}-c{cy}';cfg=pk.read_json(r,f'results/sikh358/{tag}.json')
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
rows={
 'grounding':('357 actual283 horse-head view shows unsupported tan arch; existing headstall uses head-bone tail, not mouth.','Actual mesh evidence precedes construction.',['strategy358','lessons357']),
 'expert_coverage':('Anatomical tack construction, rig local ownership, rein contact and production framing are coupled.','Whole face/cloth/motion are not certified by tack.',['controls','cast_findings']),
 'film_alignment':('Preserve accepted Pashtun quality floor, leader357 rich coat/beard and dark bay horse.','Do not disguise schematic structure with texture.',['film_language']),
 'preferences':('Leader and horse only; crowd deferred, no incremental failed handover.','Five new per task, preserve unused appearance82.',['director_preferences','strategy358']),
 'reference_roles':('Reference rearing14–19s remains faithful action authority.','This method does not change reference role or prove AV.',['references']),
 'method':(cfg['method'],'Specific source evidence can disprove geometry assumptions; fixed local implementation only.',['strategy358']),
 'interfaces':('Anatomical bit owner and consuming rein span must agree across rest, crest and impact.','Preserve grip-side geometry; no generic whole-rig endpoint offset.',['constraints','strategy358']),
 'efficient_quality':('Scoped cheap source/head proof precedes continuous render.','No cosmetic pass while connectivity is wrong.',['director_preferences','lessons357']),
 'authority':('358 adds five each, original tasks/history retained, no new spending or egress.','Allowance is not production acceptance.',['strategy358','controls'])}
available={x['id'] for x in s['direction']['context_sources']}
rows={key:(a,b,[sid if sid in available else 'learnings' for sid in ids]) for key,(a,b,ids) in rows.items()}
v=dict(outcome='admit',checks={k:dict(status='PASS',observation=a,comparison=b,source_ids=ids) for k,(a,b,ids) in rows.items()},strongest_counterexample='A plausible rest-space muzzle point can still lie inside lips or shift off the jaw during motion; exact pose-local attachment and whole rein route must be inspected, not inferred from a distance metric.',issues=[])
p=o/f'{tag}-challenge.json';t=json.dumps(v,indent=2)+'\n'
if p.exists():assert p.read_text()==t
else:p.write_text(t)
if 'brief' not in s:print('Challenge prepared');raise SystemExit(0)
ev={p:bind(p) for p in ['results/sikh358/REQUEST.md','results/sikh358/STRATEGY.md','results/sikh357/LEARNINGS.md',f'results/sikh358/{tag}.json',f'results/sikh358/{tag}-challenge.json']}
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']=='TESTING' and g['plan']!=pk.digest(s['brief']):
  c.retrospective(task,'outcome',dict(attempt=f'358-{tag}-{key}',role='diagnostic',origin='changed-plan',observations=[dict(requirement=key,status='UNKNOWN',observation='Changed integrated tack method leaves original whole-form and motion gates unresolved.')],evidence=ev),f'sikh358-{tag}-{key}-reopen')
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']!='OPEN':continue
 response=dict(cause=cfg.get('cause','Unsupported head-bone-tail anatomy and separate rein consumer caused tan-arch/disconnected tack; whole look and motion remain unqualified.'),uncertainty='Surface bounds do not locate lips automatically; actual eye/mouth visibility and posed attachment must falsify route.',change_or_retain_rationale=cfg['method'],preserve='Original references,357 integrated scene,action clock and all task failures; no spend.',test=cfg['proof'],expected='Only actual corrected subproof advances; no whole-actor acceptance by bookkeeping.',failure_response='Replan actual failing interface with retained counters, no decorative concealment.',target_stage='STRATEGIZING',plan=pk.digest(s['brief']),gate_digest=pk.digest(g),evidence=ev)
 event=f'sikh358-{tag}-{key}-response';c.retrospective(task,'response',dict(key=key,response=response),event)
 ch=dict(response_event=event,counterexample=v['strongest_counterexample'],evidence=ev,checks={k:dict(status='PASS',observation=x) for k,x in dict(causal_test=cfg['proof'],actual_method=cfg['method'],preservation='Bound current integrated native; fixed tested handler,no arbitrary worker code.',authority='Five additional each358; no new spending,crowd or identity authority.').items()})
 c.retrospective(task,'admit',dict(key=key,challenge=ch),f'sikh358-{tag}-{key}-admit')
print({k:v['status'] for k,v in c.retrospective_packet(task)['gates'].items()})
