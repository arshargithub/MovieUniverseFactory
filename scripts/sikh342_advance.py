"""Advance a qualified narrow prerequisite without claiming task completion."""
from pathlib import Path
import json
from movie_factory import production_workflow as wf
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);t='sikh335-supporting-appearance';s=c.state(t)
assert s['cycle']==23
bridge=Bridge(c)
for run in bridge.runs(s).values():bridge.qualified(run)
assert len(bridge.runs(s))==8
reason='Neutral and connected-arm bend prerequisites pass actual three views; entire supporting appearance task remains incomplete. Advance to actual actor transfer under TRANSFER_342 strategy. This is not a visual rejection of neutral23 and not Director acceptance.'
p=r/'results/sikh335/look01/prerequisite-c23.json';assert not p.exists();p.write_text(json.dumps({'status':'prerequisite_only','reason':reason},indent=2)+'\n')
d=s['direction'];c.reground(t,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],reason,'sikh342-transfer-replan')
print({k:c.state(t)[k] for k in ('stage','cycle','max_corrections')})
