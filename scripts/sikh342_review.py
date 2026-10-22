"""Record explicit human-readable image findings, never infer a visual pass."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE)
task='sikh335-supporting-appearance';cycle=c.state(task)['cycle']
step,verdict,observation,comparison=sys.argv[1:]
assert verdict in ('PASS','FAIL')
out=r/'results/sikh335/look01';run=pk.read_json(r,f'results/sikh335/look01/{step}-run-c{cycle}.json')
assert run['status']=='RETURNED'
for a in run['artifacts'].values():assert pk.file_hash(r/a['path'])==a['sha256']
v=dict(verdict=verdict,run_digest=pk.digest(run),evidence=run['artifacts'],
       observation=observation,comparison=comparison,open_defects=[] if verdict=='PASS' else [observation])
p=out/f'{step}-visual-review-c{cycle}.json';assert not p.exists()
Bridge(c).record_review(task,step,v);p.write_text(json.dumps(v,indent=2)+'\n')
print(verdict+' '+step+' (only the stated prerequisite)')
