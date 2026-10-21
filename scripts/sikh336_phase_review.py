"""Record actually inspected correction3 evidence before revising native code."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE

root=Path(__file__).resolve().parents[1]
out=root/'results/sikh335/motion01'
c=wf.Controller(root,DATABASE)
task='sikh335-continuous-performance'
run=pk.read_json(root,'results/sikh335/motion01/render-run-c3.json')
landing='results/sikh335/motion01/landing-audit-c3.json'
verdict={'verdict':'FAIL','run_digest':pk.digest(run),
    'evidence':run['artifacts']|{'landing':{'path':landing,'sha256':pk.file_hash(root/landing)}},
    'observation':'All13 phase images inspected, including351/353/357. Forehoof landmark contact speed is2.235m/s left and2.081m/s right, no last-frame collapse. Preparation294/301 and crest327 show too little poll articulation. Dirt appears at349 before left350/right351 contact. Cast and wardrobe remain schematic;353 shows absorption but cannot prove full-speed motion.',
    'comparison':'Reference strips2/3 show marked head lowering during load, muzzle lift on rise/crest, rapid arrival and post-impact debris. Finite-speed contact resolves the narrow c2 endpoint defect, not the complete coupled reference performance.',
    'open_defects':['Head/neck preparation and crest do not yet convey reference action','Landing debris precedes actual contact','Rider performance and supporting appearance remain unqualified','Full-speed audiovisual review NOT_RUN']}
Bridge(c).record_review(task,'render',verdict)
(out/'render-review-c3.json').write_text(json.dumps(verdict,indent=2)+'\n')
# Retain the previous artifacts for the affected-stage repair, not a new task.
(out/'replan-source-c4.json').write_text(json.dumps(c.state(task)['planning_artifacts'],indent=2)+'\n')
c.replan(task,'DERIVING','Correction3 resolves measured last-frame landing braking but exposes restrained reference head/neck articulation and premature dirt. Derive purposeful poll trajectory and contact-triggered existing FX, retaining support and all prior failures.','sikh336-head-impact-replan')
print({k:c.state(task)[k] for k in ('stage','planning_step','cycle','max_corrections')})
