"""Preserve rejected run history and consume the same task correction."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
s=c.state(task);reason=sys.argv[1];assert s['stage']!='REPLAN_REQUIRED'
out=r/'results/sikh335/look01';p=out/f"rejection-c{s['cycle']}.json";assert not p.exists()
p.write_text(json.dumps(dict(cycle=s['cycle'],reason=reason,status='FAIL',source_hash=pk.file_hash(r/'src/movie_factory/adapters/blender/nihang_neutral.py')),indent=2)+'\n')
d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],reason,f"sikh342-replan-c{s['cycle']}")
print({k:c.state(task)[k] for k in ('stage','cycle','max_corrections')})
