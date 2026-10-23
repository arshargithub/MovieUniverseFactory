"""Submit explicit actual-evidence judgments through the original controller.

This helper never invents PASS observations or director AV acceptance. A complete
manually authored input, all native-step reviews and no active worker are needed.
"""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,expert_planning as ep
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);label=sys.argv[1]
task='sikh335-'+('supporting-appearance' if label=='appearance' else 'continuous-performance')
data=pk.read_json(r,f'results/sikh362/{label}-final-input.json');s=c.state(task);b=s['brief'];bridge=Bridge(c)
def write(name,value):
 p=r/'results/sikh362'/name;t=json.dumps(value,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,name
 else:p.write_text(t)
if s['stage']=='EXECUTING':
 artifacts={}
 for step,run in bridge.runs(s).items():
  bridge.qualified(run)
  artifacts.update({step+':'+name:binding for name,binding in run['artifacts'].items()})
 assert set(data['applications'])=={x['id'] for x in b['requirements']}
 assert set(data['reference_applications'])=={x['id'] for x in b['references']}
 media=data['derived_media'];wf.bindings(r,media)
 result=dict(fingerprint=s['fingerprint'],candidate=dict(version=data['version'],artifacts=artifacts,derived_media=media),requirement_uses={k:dict(plan_digest=ep.plan_digest(b),application=v) for k,v in data['applications'].items()},reference_uses={x['id']:dict(reference_digest=pk.digest(x),application=data['reference_applications'][x['id']]) for x in b['references']})
 p=c.packet(task);s=c.submit(task,p['actor'],p['ticket'],result,f'sikh362-{label}-builder-final');write(f'{label}-builder-final.json',result)
if s['stage']=='REVIEWING':
 review=data['review'];review.update(fingerprint=s['fingerprint'],candidate_digest=pk.digest(s['candidate']))
 for item in review['evidence'].values():item['candidate_digest']=pk.digest(s['candidate'])
 for ref in b['references']:review['reference_checks'][ref['id']]['reference_digest']=pk.digest(ref)
 p=c.packet(task);s=c.submit(task,p['actor'],p['ticket'],review,f'sikh362-{label}-review-final');write(f'{label}-review-final.json',review)
print({k:s[k] for k in ('stage','cycle','max_corrections','production_approved')})
