"""Record the actual landing defect before any handler change; no false pass."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01'
c=wf.Controller(root,DATABASE);task='sikh335-continuous-performance';b=Bridge(c)
run=json.loads((out/'render-run-c2.json').read_text())
path='results/sikh335/motion01/PHASE_REVIEW_C2.md'
verdict={'verdict':'FAIL','run_digest':pk.digest(run),
    'evidence':run['artifacts']|{'analysis':{'path':path,'sha256':pk.file_hash(root/path)}},
    'observation':'All9 phase images inspected. Actual visible forehoof slows from2.96m/s downward at347 to0.52m/s at350 contact; supported placements and contact rebake improved but do not erase this defect.',
    'comparison':'Reference/Director requires powerful rapid contact followed by absorption, not airborne easing. Generic endpoint interpolation violates that requirement.',
    'open_defects':['Pre-impact easing on forehoof contact trajectory','Full-speed motion and supporting-cast appearance remain unqualified']}
b.record_review(task,'render',verdict)
(out/'render-review-c2.json').write_text(json.dumps(verdict,indent=2)+'\n')
c.replan(task,'DERIVING','Separate finite-speed flight termination from grounded contact/absorption; actual trajectory reveals missed endpoint semantics. Existing correction allowance exhausted; no new dispatch without explicit extension.','sikh335-impact-replan-exhausted')
print(c.state(task)['stage'])
