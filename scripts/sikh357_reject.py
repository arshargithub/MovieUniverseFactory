"""Record inspected failure; preserve original task and cumulative cycles."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle'];step=sys.argv[1];reason=sys.argv[2]
path=f'results/sikh357/{step}-run-c{cy}.json';run=pk.read_json(r,path)
evidence=run.get('artifacts') or {'failed_run':dict(path=path,sha256=pk.file_hash(r/path))}
v=dict(verdict='FAIL',run_digest=pk.digest(run),evidence=evidence,observation=reason,comparison='Actual354 failed controls and accepted production quality; local technical success is not whole-form qualification.',open_defects=[reason])
if run['status']=='RETURNED':Bridge(c).record_review(task,step,v)
(r/f'results/sikh357/{step}-visual-c{cy}.json').write_text(json.dumps(v,indent=2)+'\n')
c.retrospective(task,'outcome',dict(attempt=f'357-c{cy}-{step}',role='diagnostic',origin='actual-native-images' if run.get('artifacts') else 'native-preflight-failure',observations=[dict(requirement='form',status='FAIL',observation=reason,foundation=True)],evidence=evidence),f'sikh357-c{cy}-{step}-failure')
print(c.replan(task,'GROUNDING',reason,f'sikh357-c{cy}-visual-replan')['cycle'])
