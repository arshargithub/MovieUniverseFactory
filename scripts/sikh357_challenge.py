"""Fresh explicit construction challenge and causal retro response."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle'];o=r/'results/sikh357';cfg=pk.read_json(r,f'results/sikh357/config-c{cy}.json')
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
rows={
'grounding':('Actual354/70 and72 close plus71 front inspected; inherited follicle domain and curtain/neck band fail. Sash/tack improvements retained.','Original quality retained.',['strategy357','lessons354']),
'expert_coverage':('Hair/costume/tack construction, contact ownership and cinematographic visibility determine proof.','Whole actor/horse remain independent vetoes.',['controls','cast_findings']),
'film_alignment':('Rich illustrated supporting actor must inhabit accepted Pashtun film.','No quality downgrade or silhouette-only exemption.',['film_language']),
'preferences':('Leader/horse before crowd; no incremental known-defect handover.','Ten total new corrections, no reset.',['director_preferences','strategy357']),
'reference_roles':('Original rearing is faithful motion authority; directional look is not pixel target.353 is negative control.','Motion16 preserved, not recertified.',['references','lessons354']),
'method':(cfg['method'],'Fixed handler tests isolate construction properties; actual rendering can falsify.',['controls','strategy357']),
'interfaces':('Existing root/owner transforms preserved, new forms reviewed across crest/landing.','Same attachment does not guarantee visible integration; reverse and intended view veto.',['constraints','cast_findings']),
'efficient_quality':('Cheap actual scoped views before continuous render; no noise-only polishing.','No useful outcome claimed from tests or source hashes.',['director_preferences','strategy357']),
'authority':('Ten additional73–82 on existing appearance task; motion16 preserved, no crowd/spend.','No external or principal authority.',['constraints','strategy357'])}
v=dict(outcome='admit',checks={k:dict(status='PASS',observation=a,comparison=b,source_ids=ids) for k,(a,b,ids) in rows.items()},strongest_counterexample='A rounded silhouette can remain a synthetic beard with disconnected roots; a smooth sash can still float through its support. Actual multi-view and intended-shot evidence, not geometry metrics, decide.',issues=[])
p=o/f'challenge-c{cy}.json';text=json.dumps(v,indent=2)+'\n'
if p.exists():assert p.read_text()==text
else:p.write_text(text)
if 'brief' not in s:
 print('Challenge prepared; admit plan before causal response binding.');raise SystemExit(0)
ev={p:bind(p) for p in ['results/sikh354/LEARNINGS.md','results/sikh357/REQUEST.md','results/sikh357/STRATEGY.md','results/sikh354/RETRO_AUDIT.md',f'results/sikh357/config-c{cy}.json',f'results/sikh357/challenge-c{cy}.json']}
causes={'form':'354/72 inherited follicle domain created neck band; long paths on wrong roots fail.', 'interfaces':'353 nearest-surface sash postprojection created irregular reverse edge; ownership/continuous route require construction proof.', 'evidence':'Prior local changes and technical proofs did not establish whole actor same-film readiness.', '__allowance__':'Previous353 authorized corrections exhausted;357 supplies ten total, preserved history.'}
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']=='TESTING' and g['plan']!=pk.digest(c.state(task)['brief']):
  c.retrospective(task,'outcome',dict(attempt=f'357-c{cy}-{key}',role='diagnostic',origin='changed-plan',observations=[dict(requirement=key,status='UNKNOWN',observation='Changed method retains unresolved whole-form/interface gates.')],evidence=ev),f'sikh357-c{cy}-{key}-reopen')
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']!='OPEN':continue
 response=dict(cause=cfg.get('cause',causes.get(key,'Whole actor readiness remains unestablished.')),uncertainty='Reconstructed curves/surfaces can still fail anatomy, rooting or posed support; no predeclared artistic pass.',change_or_retain_rationale=cfg['method'],preserve='Original references, motion16,64 waist and all failure history; ten total new corrections.',test=cfg['proof'],expected='Only observed corrected subproof can advance; whole actor remains failed until all visible requirements met.',failure_response='Replan actual failed representation and retain counters; no decorative substitution.',target_stage='STRATEGIZING',plan=pk.digest(c.state(task)['brief']),gate_digest=pk.digest(g),evidence=ev)
 event=f'sikh357-c{cy}-{key}-response';c.retrospective(task,'response',dict(key=key,response=response),event)
 ch=dict(response_event=event,counterexample=v['strongest_counterexample'],evidence=ev,checks={k:dict(status='PASS',observation=x) for k,x in dict(causal_test=cfg['proof'],actual_method='Fixed local handler with tests, original integrated scene bound; no arbitrary code transport.',preservation='No rig/action/master change authorized; reversible derivative.',authority='357 ten additional appearance corrections73–82 only; checkpoint77, no spend.').items()})
 c.retrospective(task,'admit',dict(key=key,challenge=ch),f'sikh357-c{cy}-{key}-admit')
print({k:v['status'] for k,v in c.retrospective_packet(task)['gates'].items()})
