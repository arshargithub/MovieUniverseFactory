"""Record actual failed evidence and replan the same task/counter."""
import sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);t='sikh335-supporting-appearance';s=c.state(t);cy=s['cycle'];step=sys.argv[1];reason=sys.argv[2]
run=pk.read_json(r,f'results/sikh353/{step}-run-c{cy}.json')
v=dict(verdict='FAIL',run_digest=pk.digest(run),evidence=run['artifacts'],observation=reason,comparison='Original intent and352 retained negative controls; successful subproof cannot pass whole form.',open_defects=[reason])
Bridge(c).record_review(t,step,v)
(r/f'results/sikh353/{step}-visual-c{cy}.json').write_text(__import__('json').dumps(v,indent=2)+'\n')
c.retrospective(t,'outcome',dict(attempt=f'353-c{cy}-{step}',role='diagnostic',origin='actual-native-images',observations=[dict(requirement='interfaces',status='FAIL',observation=reason,foundation=True)],evidence=run['artifacts']),f'sikh353-c{cy}-{step}-failure')
print(c.replan(t,'GROUNDING',reason,f'sikh353-c{cy}-visual-replan')['cycle'])
