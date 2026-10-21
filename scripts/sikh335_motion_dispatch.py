"""Canonical admitted continuous335 native job; no raw Blender launch."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01'
c=wf.Controller(root,DATABASE);task='sikh335-continuous-performance';b=Bridge(c)
def bind(p):return {'path':p,'sha256':pk.file_hash(root/p)}
step=sys.argv[1];assert step in {'save','render'}
state=c.state(task);cycle=state['cycle']
if step=='save':
    p=c.packet(task);vf=out/f'challenge-verdict-c{cycle}.json'
    verdict=json.loads((vf if vf.exists() else out/'challenge-verdict.json').read_text())
    verdict['input_digest']=p['planning_input_digest']
    c.submit(task,p['actor'],p['ticket'],verdict,'sikh335-motion-challenge-'+str(cycle))
    parent=bind('.runtime/art-direction/series01-sikh320/build-10/sequence.blend')
else:
    parent=json.loads((out/f'save-run-c{cycle}.json').read_text())['artifacts']['native']
recipe=next(s['native_recipe'] for s in c.state(task)['planning_artifacts']['STRATEGIZING']['steps'] if s['id']==step)
run=b.dispatch(task,step,f'sikh335-motion-c{cycle}-{step}',parent=parent,blender_bin=BLENDER_BIN,
               timeout=600,recipe=recipe)
(out/f'{step}-run-c{cycle}.json').write_text(json.dumps(run,indent=2)+'\n')
print(json.dumps({'status':run['status'],'error':run.get('error'),'id':run['id'],'artifacts':run.get('artifacts')},indent=2))
if run['status']!='RETURNED':raise SystemExit(2)
