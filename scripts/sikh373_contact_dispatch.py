"""Valid bounded transport correction before reservation; same admitted recipe."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-continuous-performance';s=c.state(task)
assert s['cycle']==80 and s['stage']=='EXECUTING'
bridge=Bridge(c);assert 'contact' not in bridge.runs(s)
step=next(x for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']=='contact')
parent=json.loads((r/'results/sikh373/motion-c80-prepare-run.json').read_text())['artifacts']['native']
result=bridge.dispatch(task,'contact','sikh373-motion-c80-contact',parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=step['native_recipe'])
p=r/'results/sikh373/motion-c80-contact-run.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
if result['status']!='RETURNED':raise SystemExit(2)
