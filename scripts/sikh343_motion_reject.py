"""Retain the actual endpoint failure; no animation pass from better numbers."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-continuous-performance';s=c.state(task)
assert s['cycle']==11 and s['stage']=='EXECUTING'
reason='Native11 owning-scene repair succeeds, but actual forehoof descent still slows in the final interval: left3.546 to2.937 and right3.116 to2.351 scene units/s. This fails the explicit no-airborne-ease criterion. Technical save PASS is not motion PASS. Skip expensive16-frame render of known temporal failure; preserve actual190-frame support evidence. Appearance can continue from unchanged motion5/23.'
p=r/'results/sikh335/motion01/rejection-c11.json';assert not p.exists()
p.write_text(json.dumps({'status':'FAIL','reason':reason,'metrics':{'path':'results/sikh335/motion01/impact-metrics-c11.json','sha256':pk.file_hash(r/'results/sikh335/motion01/impact-metrics-c11.json')},'render':'NOT_RUN','next_hypothesis':'Actual world-space hoof arrival needs direct trajectory control; fold and body curves jointly change endpoint velocity.'},indent=2)+'\n')
d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],reason,'sikh343-motion11-reject')
print({k:c.state(task)[k] for k in ('stage','cycle','max_corrections')})
