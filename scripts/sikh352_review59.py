"""Scoped sampled anatomy/contact result, not whole-actor acceptance."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';assert c.state(task)['cycle']==59
for step in [f'anatomy_{p}_{v}' for p in ('custom','linear') for v in ('front','back','side')]+['leader_contact']:
 run=pk.read_json(r,f'results/sikh352/{step}-run-c59.json');ev=dict(run['artifacts'])
 for f in ('frame-0283.png','frame-0290.png','frame.png','frame-0350.png'):
  p=f'.runtime/factory-native/sikh352-c59-{step}/{f}';ev[p]=dict(path=p,sha256=pk.file_hash(r/p))
 v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=ev,observation='All four frames inspected. Continuous shoulder/upper arm, separated elbow, plausible forearm/wrist and closed shaft grip in these sampled controls. No58 torso penetration or shelf. Scoped static result only.',comparison='Both linear and DQ preserve recognizable anatomy; retain DQ. Hand wraps actual tilted shaft while tip error is zero. Maximum288 wrist case still needs its exact view; animation/whole actor not passed.',open_defects=[])
 Bridge(c).record_review(task,step,v);(r/f'results/sikh352/{step}-visual-c59.json').write_text(json.dumps(v,indent=2)+'\n')
print(c.replan(task,'GROUNDING','59 sampled anatomy/contact supports garment transfer, not whole form acceptance.60 restores independent23 cloth and checks exact288 wrist extremum plus whole actor interfaces.', 'sikh352-c60-transfer')['cycle'])
