"""Use bridge's existing600s timeout bound. No native attempt was made at900."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);t='sikh335-continuous-performance';s=c.state(t);cy=s['cycle'];step=sys.argv[1]
p='.runtime/factory-native/sikh353-c65-save/scene.blend'
source=dict(path=p,sha256=pk.file_hash(r/p)) if step=='save' else pk.read_json(r,f'results/sikh353/motion-save-run-c{cy}.json')['artifacts']['native']
recipe=next(x['native_recipe'] for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==step)
run=Bridge(c).dispatch(t,step,f'sikh353-motion-c{cy}-{step}',parent=source,blender_bin=BLENDER_BIN,timeout=600,recipe=recipe)
p=r/f'results/sikh353/motion-{step}-run-c{cy}.json';assert not p.exists();p.write_text(json.dumps(run,indent=2)+'\n')
print({k:run.get(k) for k in ['id','status','error']})
if run['status']!='RETURNED':raise SystemExit(2)
