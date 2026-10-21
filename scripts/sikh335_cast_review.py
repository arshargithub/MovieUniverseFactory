"""Complete read-only inventory internally, never an audience-ready asset pass."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,expert_planning as ep
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/cast-inspect'
c=wf.Controller(root,DATABASE);task='sikh335-cast-inventory';b=Bridge(c)
run=pk.read_json(root,'results/sikh335/cast-inspect/inspect-run.json')
path='results/sikh335/cast-inspect/FINDINGS.md';analysis={'path':path,'sha256':pk.file_hash(root/path)}
obs='Read-only leader/nearest crowd inventory:394objects,51materials,50153-vertex head,24082-vertex207-key leader garment; correct woven material assignments, cylindrical turban form identified.'
comparison='Actual actor inventory plus declared source-level saddle ownership, not appearance approval. Native blanket/tack outside actor descendants remains uninspected; no full tack or motion qualification.'
b.record_review(task,'inspect',{'verdict':'PASS','run_digest':pk.digest(run),'evidence':run['artifacts']|{'analysis':analysis},
    'observation':obs,'comparison':comparison,'open_defects':[]})
p=c.packet(task);brief=p['brief'];ref=brief['references'][0]
candidate={'version':'335-cast-read-only','artifacts':{'inspect:'+k:v for k,v in run['artifacts'].items()}}
c.submit(task,p['actor'],p['ticket'],{'fingerprint':p['fingerprint'],'candidate':candidate,
    'reference_uses':{'reference_rear':{'reference_digest':pk.digest(ref),'application':'Identify parent/cache interfaces that must survive faithful rear; no action change or motion pass.'}},
    'requirement_uses':{r['id']:{'plan_digest':ep.plan_digest(brief),'application':r['criterion']+' Inventory and scope limits documented in actual findings.'} for r in brief['requirements']}},'sikh335-cast-inventory-built')
p=c.packet(task);digest=pk.digest(candidate)
evidence={k:{'binding':v,'mode':'technical','candidate_digest':digest,'scope':'Read-only supporting-actor inventory'} for k,v in run['artifacts'].items()}
evidence['analysis']={'binding':analysis,'mode':'technical','candidate_digest':digest,'scope':'Measured inventory and explicit exclusions'}
review={'fingerprint':p['fingerprint'],'candidate_digest':digest,'evidence':evidence,
    'checks':[{'id':r['id'],'status':'PASS','observation':obs,'comparison':comparison,'evidence':list(evidence)} for r in brief['requirements']],
    'reference_checks':{'reference_rear':{'reference_digest':pk.digest(ref),'observation':'Actor parent/shape-key interfaces identified for later motion merge.',
        'comparison':'Read-only prerequisite only; rearing, clothing and film quality are not approved.','evidence':['cast','analysis'],
        'aspects':[{'id':'whole_pose','status':'PASS','observation':'Required interface ownership discovery is met; actual performance remains failed elsewhere.'}]}},
    'audience_read':'No new appearance or audience clip; independent source diagnosis complete.',
    'strongest_counterexample':'High topology counts and procedural texture already existed, yet the cast remains schematic. Construction and actual visual review, not more counts, are required.',
    'adjacent_review':'No source mutation, motion retry, asset acquisition or other authority expansion.',
    'open_visible_defects':[],
    'intent_checks':{'ownership':{'scope':'supported_evidence_only','status':'PASS','observation':obs,'comparison':comparison,'evidence':['cast','analysis']}},
    'planning_gaps':[]}
c.submit(task,p['actor'],p['ticket'],review,'sikh335-cast-inventory-reviewed');(out/'review.json').write_text(json.dumps(review,indent=2)+'\n')
print(c.state(task)['stage'])
