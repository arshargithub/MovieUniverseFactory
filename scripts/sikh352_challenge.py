"""Human-readable fresh challenge and retained retrospective admission."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';cycle=c.state(task)['cycle'];out=r/'results/sikh352'
assert cycle in (58,59,60,61)
rows={
 'grounding':('351 actual front failed despite improved rear.352 addresses coupled constraint rather than cosmetic symptoms.','Failed evidence remains authoritative.',['audit348','strategy352']),
 'expert_coverage':('Anatomy, prop contact, skinning and revealing camera controls explicitly coupled.','Joint lengths do not qualify skin.',['learnings','controls']),
 'film_alignment':('Bare proof only; whole face/clothing/tack and accepted Pashtun comparison remain unresolved.','No lower quality floor.',['film_language']),
 'preferences':('No known failure is handed over as ready; no sleeve concealment.','Technical choices remain agent owned.',['director_preferences']),
 'reference_roles':('Faithful rearing authority unchanged,23 useful cloth volume not finished approval,52 failed body shell.','No promotion of rejected reference.',['references','audit348']),
 'method':('22 focused tests; fixed reviewed handler solves all190frames before mutation, proper rotations and fixed policy. Paired DQ/LBS tests distinguish weighting from pose.','Tests not art proof; search score may still select unnatural anatomy.',['controls','strategy352']),
 'interfaces':('Grip can move along shaft; old hand location is not an approved creative requirement. Check actual fingers and opposite limb/hip effects of DQ.','Geometric palm proxy may not ensure believable contact.',['constraints','cast_findings']),
 'efficient_quality':('Four poses times paired three angles, only body and hand. Whole scene remains deferred.','No full render before foundational proof.',['director_preferences','audit348']),
 'authority':('Exactly58–61 existing appearance; motion12 unchanged; no new spending or egress.','No reset or expansion.',['constraints','strategy352'])}
if cycle==59:
 rows['method']=('23 tests.59 replaces failed fixed-shaft constraint with natural torso-supported arm; shaft tilts to hand around original tip. Hard wrist/clearance/continuity gates before keying.','No search score or metrics pass appearance.',['controls','strategy352'])
 rows['interfaces']=('Preserve spear tip position on every frame and original timings; only shaft orientation and arm contact change.','Verify grip stays credible and coat is not allowed to hide bare defects.',['constraints','cast_findings'])
 rows['grounding']=('Actual58 torso penetration and paired skinning failure directly motivate59 constraint change.','Other58 frames retained but not falsely claimed inspected.',['audit348','strategy352'])
if cycle==60:
 rows['grounding']=('59 all28 sampled images inspected; shoulder/arm shape and shaft grip locally viable. Not full actor or motion acceptance.','Exact288 extremum remains planned.',['strategy352','controls'])
 rows['method']=('26 tests. Restore real23 neutral cloth, interpolate body weights, outward-only rest clearance; no post-deform skin shrinkwrap.','Mapping may still distort shoulder or neckline; actual render decisive.',['controls','strategy352'])
 rows['interfaces']=('Hidden supports receive matching new mesh and owners; old edge/sash components must be inspected against new fabric. Body59 unchanged.','Stale trim or weighting can fail despite good neutral volume.',['constraints','cast_findings'])
 rows['efficient_quality']=('Actor front/reverse/contact and exact bare288, no crowd/full scene production render.','Foundation prerequisite scoped, not wholesale approval.',['director_preferences','audit348'])
if cycle==61:
 rows['grounding']=('60 front/reverse actual frames show elbow breakthrough and rear waist lips; exact288 body remains viable.','Known failures drive scoped repair.',['strategy352','controls'])
 rows['method']=('27 focused tests. Local radial ease preserves body; hem/band reconstructed at coherent overlap with rebinding of hidden supports.','Skinning or skirt root could still fail, so no guarantee from local geometry.',['controls','strategy352'])
 rows['interfaces']=('Inspect sleeves, neck, cuffs, sash and rear skirt transition together; no crowd copying.','Successful elbow fix cannot waive adjacent waist regression.',['constraints','cast_findings'])
 rows['authority']=('61 is final approved correction; no authority to reset or automatically extend. Motion12 unchanged.','Exhaustion retains failure rather than promoting candidate.',['constraints','strategy352'])
v=dict(outcome='admit',checks={k:dict(status='PASS',observation=a,comparison=b,source_ids=ids) for k,(a,b,ids) in rows.items()},strongest_counterexample='A correct body can still acquire distorted cloth at shoulder/neck or stale layer intersections. Weight transfer and topology equality cannot qualify this. Exact288 and whole actor views remain mandatory; static success does not pass animation.',issues=[])
p=out/f'challenge-c{cycle}.json';assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n')
