"""Preserve an observed motion failure and continue the original task."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);t='sikh335-continuous-performance';cy=c.state(t)['cycle']
run=pk.read_json(r,f'results/sikh353/motion-render-run-c{cy}.json');reason=sys.argv[1]
v=dict(verdict='FAIL',run_digest=pk.digest(run),evidence=run['artifacts'],observation=reason,comparison='All ten actual phase images inspected against original whole-rear reference and recorded12 arrival. Static images do not establish fluidity.',open_defects=[reason])
Bridge(c).record_review(t,'render',v)
(r/f'results/sikh353/motion-visual-c{cy}.json').write_text(json.dumps(v,indent=2)+'\n')
c.retrospective(t,'outcome',dict(attempt=f'353-motion{cy}',role='diagnostic',origin='actual-native-images-and-frame-metrics',observations=[dict(requirement='rider' if cy==16 else 'phases',status='FAIL',observation=reason,foundation=True)],evidence=run['artifacts']),f'sikh353-motion{cy}-failure')
print(c.replan(t,'GROUNDING',reason,f'sikh353-motion{cy}-replan')['cycle'])
