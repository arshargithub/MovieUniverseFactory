import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';assert c.state(task)['cycle']==60
for step in ['leader_front','leader_reverse']:
 run=pk.read_json(r,f'results/sikh352/{step}-run-c60.json');ev=dict(run['artifacts'])
 for f in ('frame-0283.png','frame-0288.png','frame.png','frame-0350.png'):
  p=f'.runtime/factory-native/sikh352-c60-{step}/{f}';ev[p]=dict(path=p,sha256=pk.file_hash(r/p))
 v=dict(verdict='FAIL',run_digest=pk.digest(run),evidence=ev,observation='Four actual poses inspected. Fabric volume improved, but visible rein elbow skin breakthrough and rear waist/hem lips remain.',comparison='59 bare anatomy preserved,23 volume regained, neither permits clothing intersection. Face/turban/tack remain whole-actor obligations.',open_defects=['Elbow sleeve penetration','Rear waist and coat hem overlap','Whole actor/crowd not ready'])
 Bridge(c).record_review(task,step,v);(r/f'results/sikh352/{step}-visual-c60.json').write_text(json.dumps(v,indent=2)+'\n')
print(c.replan(task,'GROUNDING','60 cloth fails elbow and rear waist interfaces.61 local elbow ease and coherent hem/band reconstruction, keeping59 body. Last approved correction.', 'sikh352-c61-interfaces')['cycle'])
