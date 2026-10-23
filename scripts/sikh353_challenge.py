"""Explicit fresh challenge of semantic support, not inherited visual approval."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';cycle=c.state(task)['cycle'];out=r/'results/sikh353'
rows={
 'grounding':('Actual61 projecting strips contradict whole-character quality.352 preserves useful59/60 evidence without approving61.','Original source/reference and failures retained.',['lessons352','strategy353']),
 'expert_coverage':('Costume support, anatomical ownership, layered interfaces and revealing reverse camera determine this earliest proof.','Whole face/turban/horse motion remain explicit subsequent requirements.',['controls','cast_findings']),
 'film_alignment':('Same-film requirement survives; fixing waist alone cannot qualify supporting actor.','Accepted Pashtun quality unchanged.',['film_language']),
 'preferences':('No known-defect handoff; leader and horse first, crowd deferred.','No change to Director quality floor.',['director_preferences','strategy353']),
 'reference_roles':('Original rear governs action;61 is negative support control,60 independent volume useful.','No rejected candidate promoted as standard.',['references','lessons352']),
 'method':('8 focused tests including sleeve contamination and radial spike negatives. Fixed handler selects only trunk-weighted faces and compares old unrestricted rays.','Weights can themselves be wrong; actual multi-view garment proof remains decisive.',['controls','strategy353']),
 'interfaces':('Same coat and59 body retained; closed periodic band fitted to trunk with small smoothing.','Spine-bound band can still intersect moving hem or sash; all four poses front/reverse/contact must be inspected.',['constraints','cast_findings']),
 'efficient_quality':('Only scoped actor interface renders before whole-performance work.','No crowd/full sequence render on a failed foundation.',['director_preferences','strategy353']),
 'authority':('Six appearance62–67 plus four motion13–16 equals ten. No spend or remote actions.','Existing history and limits retained.',['constraints','strategy353'])}
if cycle>=64:
 rows['grounding']=('63 all four reverse images inspected: projecting strips gone, coat still penetrates band. Failure retained.','This does not reopen accepted body or confuse waist with actor pass.',['lessons352','strategy353'])
 rows['method']=('Copy weights from torso-owned coat rather than single spine; no radial smoothing across local peaks,22mm clearance.','Compatible weights still require posed visual evidence.',['controls','strategy353'])
if cycle>=65:
 rows['grounding']=('64 actual eight front/reverse images resolve sampled waist defects; face and whole figure remain below bar.','Retain narrow result without promoting whole actor.',['strategy353','controls'])
 rows['method']=('Owned crown/material/beard/sash changes retain native geometry and animation. New face diagnostic reveals eye and facial surface issues.','Shader changes cannot fix bad anatomy; close face and intended frame can veto.',['controls','strategy353'])
 rows['interfaces']=('Actual dressed coat supports sash; body64 and hand keys untouched.','Projected sash may lose tension or cause cuff/waist regression; inspect front/reverse.',['constraints','cast_findings'])
if cycle>=66:
 rows['grounding']=('65 actual face images exposed a smooth crown core masking narrowed courses and comb-like eyebrows.65 rejected.','Use64 source and preserve failed65 evidence; no visual approval inferred.',['strategy353','controls'])
 rows['method']=('All eight crown parts share scale/material; explicit membership assertion and negative unit test. Finer varied tapered brow curves retain roots.','Correct membership cannot guarantee authentic tied shape or face character; actual images veto.',['controls','strategy353'])
if cycle>=67:
 rows['grounding']=('66 restored crown layers but synthetic face and rigid hem remain; four actual production frames inspected.','No whole-form pass; final six-cycle appearance allowance.',['strategy353','controls'])
 rows['method']=('Retain64 source, complete crown, quieter dye and finer weave; bounded skirt folds/reduced thigh carry, actual UV horse nap, preserve saddle border.','Drape changes can enter horse/legs; reverse/crest are mandatory. Texture cannot pass bad form.',['controls','strategy353'])
v=dict(outcome='admit',checks={k:dict(status='PASS',observation=a,comparison=b,source_ids=ids) for k,(a,b,ids) in rows.items()},strongest_counterexample='Correct torso selection could still yield an unsupported hovering band because weighting or cloth topology is wrong. Hard numeric envelope cannot prove silhouette, cuffs or drape. Front/reverse/contact and whole actor are independent vetoes.',issues=[])
p=out/f'challenge-c{cycle}.json';assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n')
