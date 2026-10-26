import json,hashlib
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path.cwd();o=r/'results/sikh375';c=w.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==132

def write(n,v):(o/n).write_text(json.dumps(v,indent=2)+'\n')
def bind(q):return dict(path=q,sha256=p.file_hash(r/q))
run=p.read_json(r,'results/sikh375/appearance-c132-worstfront-run.json');reason='Actual coatless front339 still has projecting rounded pendant chest bib; opposite339 also shows excessive projecting mass. Correction is smoother than source but not anatomically coherent. Rest bind and exact primary actions do not qualify positive form.'
v=dict(run_digest=p.digest(run),verdict='FAIL',observation=reason,comparison='Matched front/opposite339 against original129 and131 failures; body-only diagnostic proves remaining mass is actual skin, not coat.',open_defects=['chest_bib339_remains'],evidence=run['artifacts'],requirement_outcomes={q['id']:dict(status='FAIL',observation='Shared early appearance proof fails; no qualification: '+reason) for q in s['brief']['requirements']})
if s['stage']=='EXECUTING':
 Bridge(c).record_review(task,'worstfront',v);write('appearance-c132-worstfront-review.json',v)
 c.replan(task,'GROUNDING','132 body-only paired339front/opposite stillfails connected anatomy; four375slots exhausted. Preserve exact source/actions and reject before coat/fullproof. Narrow escalation proposal requires new Director authority.','sikh375-rejected132-exhausted')
s=c.state(task);assert s['stage']=='REPLAN_REQUIRED' and s['cycle']==s['max_corrections']==132
write('INTERNAL_REJECTION132.json',dict(status='FAIL',task=task,cycle=132,max_corrections=132,authority=bind('results/sikh375/REQUEST.md'),reason=reason,source=bind('.runtime/factory-native/sikh373-motion-c80-contact/scene.blend'),candidate=bind('.runtime/factory-native/sikh375-appearance-c132-inspect/scene.blend'),evidence={x:bind(x) for x in ['.runtime/factory-native/sikh375-appearance-c132-worstfront/frame-0339.png','.runtime/factory-native/sikh375-appearance-c132-worst/frame-0339.png','.runtime/factory-native/sikh375-appearance-c132-repair/horse-corrective375-body.json','results/sikh375/REJECT130.md','results/sikh375/REJECT131.md']},completed_cycles={'129':'Source ownership diagnosis and matched controls','130':'Torso-fixed weight test rejected','131':'Proximal sharing test rejected','132':'Rest-bound post-armature corrective rejected'},source_preservation='Raw geometry/shape/actions exact in132, accepted masters separately hash-verified.',not_run=['coat SurfaceDeform','final5x3 matrix','intended-light positive proof','all92frame contact','new fullspeed appearance clip','DirectorAV queue'],new_spend=False,model_escalation=False))
# Exact previously protected masters must remain byte-identical.
protected=p.read_json(r,'results/sikh374/PROTECTED_MASTERS128.json');write('PROTECTED_MASTERS_SOURCE.json',protected)
print(json.dumps(dict(stage=s['stage'],cycle=s['cycle'],maximum=s['max_corrections'],candidate='INTERNAL_FAIL')))
