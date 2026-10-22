"""Preserve the actual failure and advance only within the existing ceiling."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
assert 30<=s['cycle']<=33 and s['stage']!='REPLAN_REQUIRED'
reason=sys.argv[1];path=r/f"results/sikh335/look01/rejection-c{s['cycle']}.json";assert not path.exists()
path.write_text(json.dumps({'cycle':s['cycle'],'status':'FAIL','reason':reason,
 'source':{'path':'src/movie_factory/adapters/blender/nihang_actor.py','sha256':pk.file_hash(r/'src/movie_factory/adapters/blender/nihang_actor.py')}},indent=2)+'\n')
d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],reason,f"sikh343-actor-reject-c{s['cycle']}")
print({k:c.state(task)[k] for k in ('stage','cycle','max_corrections')})
