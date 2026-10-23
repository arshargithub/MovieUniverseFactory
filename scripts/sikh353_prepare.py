"""Bootstrap exact continuation and split allowance, no construction."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];o=r/'results/sikh353'
def write(n,v):
 p=o/n;assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n')
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
for name,task,prior,count in [('appearance','sikh335-supporting-appearance',61,6),('motion','sikh335-continuous-performance',12,4)]:
 write(f'{name}-allowance.json',dict(task=task,decision='approve_additional_corrections',additional_corrections=count,prior_cycle=prior,prior_max_corrections=prior,question='Continue leader and horse appearance and motion with ten total additional cycles, crowd deferred.',director_reply='approved for 10 more cycles. focus on leader appearance and motion. we\'ll move on to crowd once the nihang leader+horse is production ready.',aggregate_authority=bind('results/sikh353/REQUEST.md')))
 write(f'{name}-amendment.json',dict(text=f'Director353 ten total correction approval: allocate {count} to existing {name} task.',operations=['code','document'],amendment_task=task,authority=bind(f'results/sikh353/{name}-allowance.json'),rationale='Administrative amendment only; six plus four equals ten, no reset.'))
 write(f'{name}-request.json',dict(text='Continue Nihang leader and horse appearance and motion to production quality. Crowd deferred.',operations=['native_inspect','asset','motion','edit','render','code','test','document'],continuation=True,authority=bind('results/sikh353/REQUEST.md'),rationale='Existing task and limits retained; original faithful rearing intent, new leader-only priority. No spend or upload.'))
