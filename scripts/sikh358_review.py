"""Record actual inspected evidence on original tasks; never infer visual pass."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);label,step,status,requirement,reason=sys.argv[1:6]
task='sikh335-'+('supporting-appearance' if label=='appearance' else 'continuous-performance');s=c.state(task);cy=s['cycle'];tag=f'{label}-c{cy}'
path=f'results/sikh358/{tag}-{step}-run.json';run=pk.read_json(r,path);evidence=run.get('artifacts') or {'failed_run':dict(path=path,sha256=pk.file_hash(r/path))}
v=dict(verdict=status,run_digest=pk.digest(run),evidence=evidence,observation=reason,comparison='Actual returned images/technical data against explicit358 plan and original quality/reference requirements. No full-speed AV certification.',open_defects=[reason] if status=='FAIL' else [])
if run['status']=='RETURNED':Bridge(c).record_review(task,step,v)
(r/f'results/sikh358/{tag}-{step}-review.json').write_text(json.dumps(v,indent=2)+'\n')
c.retrospective(task,'outcome',dict(attempt=f'358-{tag}-{step}',role='diagnostic',origin='actual-native-evidence',observations=[dict(requirement=requirement,status=status,observation=reason,foundation=status=='FAIL')],evidence=evidence),f'sikh358-{tag}-{step}-outcome')
if status=='FAIL':print(c.replan(task,'GROUNDING',reason,f'sikh358-{tag}-{step}-replan')['cycle'])
