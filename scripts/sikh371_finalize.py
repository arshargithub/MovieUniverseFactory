"""Submit manually authored scope/evidence judgments on the original task.

Never invent PASS checks or full-speed AV judgment. No worker may be active.
"""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk, expert_planning as ep
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE

r=Path(__file__).resolve().parents[1];o=r/'results/sikh371'
c=wf.Controller(r,DATABASE);task='sikh335-continuous-performance'
data=pk.read_json(r,'results/sikh371/final-input71.json');s=c.state(task);b=s['brief']
assert s['cycle']==71
def write(name,value):
    p=o/name;t=json.dumps(value,indent=2)+'\n'
    if p.exists():assert p.read_text()==t,name
    else:p.write_text(t)
if s['stage']=='EXECUTING':
    artifacts={};bridge=Bridge(c)
    for step,run in bridge.runs(s).items():
        bridge.qualified(run)
        artifacts.update({step+':'+k:v for k,v in run['artifacts'].items()})
    assert set(data['applications'])=={x['id'] for x in b['requirements']}
    wf.bindings(r,data['derived_media'])
    result=dict(fingerprint=s['fingerprint'],candidate=dict(version=data['version'],artifacts=artifacts,derived_media=data['derived_media']),requirement_uses={k:dict(plan_digest=ep.plan_digest(b),application=v) for k,v in data['applications'].items()},reference_uses={x['id']:dict(reference_digest=pk.digest(x),application=data['reference_applications'][x['id']]) for x in b['references']},unit_application=data['unit_application'])
    p=c.packet(task);s=c.submit(task,p['actor'],p['ticket'],result,'sikh371-builder-final71');write('builder-final71.json',result)
if s['stage']=='REVIEWING':
    review=data['review'];review.update(fingerprint=s['fingerprint'],candidate_digest=pk.digest(s['candidate']))
    for row in review['evidence'].values():row['candidate_digest']=pk.digest(s['candidate'])
    for ref in b['references']:review['reference_checks'][ref['id']]['reference_digest']=pk.digest(ref)
    p=c.packet(task);s=c.submit(task,p['actor'],p['ticket'],review,'sikh371-review-final71');write('review-final71.json',review)
print({k:s[k] for k in ('stage','cycle','max_corrections','production_approved')})
