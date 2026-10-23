"""Actual complete98 image review; garment component retained, whole look fails."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
assert c.state(task)['cycle']==98
observations={
 'leader_face':'Actual front: intact face/beard roots and garment neckline, but pointed smooth stacked crown and overly uniform smooth face/beard still fail integrated richness. This is not an approved close character.',
 'leader_face_left':'Actual left oblique: anatomy/ear/head ownership continuous, but smooth cap courses and brushed free beard remain too uniform. No whole-form pass.',
 'leader_face_right':'Actual right oblique: rooted beard/ear and side shape retained, but smooth conical cap and simple surface remain below same-film control.',
 'production':'Actual283/307/327/350: continuous waistband and retained rider/horse/seat/spear/reins through key phases. Larger forms intact at shot size, but costume still overly smooth and crown cone remains visible. No whole look or full-speed motion pass.'}
for step,reason in observations.items():
 path=f'results/sikh362/appearance-c98-{step}-run.json';run=pk.read_json(r,path)
 v=dict(verdict='FAIL',run_digest=pk.digest(run),evidence=run['artifacts'],observation=reason,comparison='Actual inspected images against accepted Pashtun film richness and original supporting-shot quality; source crop control diagnoses clipped detail, not visual closure.',open_defects=['Crown/form and integrated surface-read unresolved'])
 Bridge(c).record_review(task,step,v)
 (r/f'results/sikh362/appearance-c98-{step}-review.json').write_text(json.dumps(v,indent=2)+'\n')
c.retrospective(task,'outcome',dict(attempt='362-appearance-c98-whole',role='diagnostic',origin='actual-native-evidence',observations=[dict(requirement='form',status='FAIL',observation='Seam is corrected in all six front/reverse frames, but crown/face/textile smoothness remains visible in whole-look controls; actual source crop clips59.65percent at old range.',foundation=False)],evidence={'production':dict(path='results/sikh362/appearance-c98-production-review.json',sha256=pk.file_hash(r/'results/sikh362/appearance-c98-production-review.json'))}),'sikh362-c98-whole-outcome')
print(c.replan(task,'GROUNDING','Preserve98 supported skirt seam; change crown top shape and measured material contrast, then repeat intended full appearance proof.','sikh362-c98-replan')['cycle'])
