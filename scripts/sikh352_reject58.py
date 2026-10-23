import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
assert c.state(task)['cycle']==58
for step,files in {'anatomy_custom_front':['frame-0283.png','frame-0290.png','frame.png','frame-0350.png'],'anatomy_custom_back':['frame.png'],'anatomy_custom_side':['frame.png'],'anatomy_linear_front':['frame.png'],'anatomy_linear_back':['frame.png'],'leader_contact':['frame.png']}.items():
 run=pk.read_json(r,f'results/sikh352/{step}-run-c58.json');ev=dict(run['artifacts'])
 for f in files:
  p=f'.runtime/factory-native/sikh352-c58-{step}/{f}';ev[p]=dict(path=p,sha256=pk.file_hash(r/p))
 v=dict(verdict='FAIL',run_digest=pk.digest(run),evidence=ev,observation='Actual reviewed frames listed in evidence. Upper arm penetrates torso and leaves a shoulder bulb; both skinning methods fail. Hand contact cannot qualify malformed arm.',comparison='Paired skinning does not resolve pose failure; numeric393.6mm elbow jump is independently unacceptable.',open_defects=['Upper arm/torso collision','Wrist overbend and discontinuous elbow','Whole actor not qualified'])
 Bridge(c).record_review(task,step,v);(r/f'results/sikh352/{step}-visual-c58.json').write_text(json.dumps(v,indent=2)+'\n')
print(c.replan(task,'GROUNDING','58 actual pose and paired skinning fail.59 orients spear around unchanged tip to meet an anatomically supported arm; preserve all tip timing and horse motion.', 'sikh352-c59-replan')['cycle'])
