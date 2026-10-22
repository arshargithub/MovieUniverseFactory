"""Preserve a failed344 candidate and replan within the same shared ceiling."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
assert 34<=s['cycle']<=37 and s['stage']!='REPLAN_REQUIRED'
reason=sys.argv[1];p=r/f"results/sikh335/look01/rejection-c{s['cycle']}.json";assert not p.exists()
p.write_text(json.dumps(dict(cycle=s['cycle'],status='FAIL',reason=reason,
 source=dict(path='src/movie_factory/adapters/blender/nihang_refit.py',sha256=pk.file_hash(r/'src/movie_factory/adapters/blender/nihang_refit.py'))),indent=2)+'\n')
d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],reason,f"sikh344-actor-reject-c{s['cycle']}")
print({k:c.state(task)[k] for k in ('stage','cycle','max_corrections')})
