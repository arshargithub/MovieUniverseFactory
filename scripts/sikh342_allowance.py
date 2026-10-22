"""Allocate one shared Director ceiling to existing exhausted tasks, never reset."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
from movie_factory import production_workflow as wf,production_knowledge as pk,production_allowance as pa
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE)
authority='results/sikh335/allowance342.json';a=json.loads((r/authority).read_text())
task=sys.argv[1];count=int(sys.argv[2]);assert task in a['baseline'] and 0<count<=10
states={k:c.state(k) for k in a['baseline']}
allocated=sum(states[k]['max_corrections']-v for k,v in a['baseline'].items())
assert 0<=allocated and allocated+count<=a['additional_shared_cycles'], 'SHARED_CEILING'
s=states[task];assert s['stage']=='REPLAN_REQUIRED' and s['cycle']==s['max_corrections']
path=f"results/sikh335/look01/allowance342-{task}-{s['cycle']}.json"
decision=dict(task=task,decision='approve_additional_corrections',additional_corrections=count,
 prior_cycle=s['cycle'],prior_max_corrections=s['max_corrections'],director_reply=a['director_reply'],
 question='Agent allocation from the explicit shared ten-cycle continuation; no new Director question.',
 shared_authority={'path':authority,'sha256':pk.file_hash(r/authority)},
 allocated_before=allocated,unallocated_after=10-allocated-count)
p=r/path;assert not p.exists();p.write_text(json.dumps(decision,indent=2)+'\n')
binding={'path':path,'sha256':pk.file_hash(p)};event=f"sikh342-allocate-{task}-{s['cycle']}"
c.route_request(event,dict(text='Allocate approved shared correction pool to existing exhausted task.',
 operations=['code','test','document'],authority=binding,amendment_task=task,
 rationale='Shared total enforced against both live task caps; original intent, failures and limits retained.'))
updated=pa.extend(c,task,event,binding,event+'-extend')
receipt={k:updated[k] for k in ('task','stage','cycle','max_corrections')};receipt['unallocated']=decision['unallocated_after']
(r/path.replace('.json','-receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
