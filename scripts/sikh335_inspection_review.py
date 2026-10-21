"""Authored technical review of actual335 inspection, not a production-media pass."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk, expert_planning as ep
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE

root=Path(__file__).resolve().parents[1]; out=root/'results/sikh335'
c=wf.Controller(root,DATABASE); task='sikh335-control-ownership'; b=Bridge(c)
run=json.loads((out/'inspect-run.json').read_text())
finding={'path':'results/sikh335/CONTROL_FINDINGS.md','sha256':pk.file_hash(out/'CONTROL_FINDINGS.md')}
observation='456 bones,64 null-target BBone ease drivers,2 deformed meshes; fore FK and hind IK overrides identified. Native parent hash unchanged.'
comparison='Complete ownership evidence distinguishes smoothing-driver defects from missing object control drivers; it does not qualify any rejected pose or appearance.'
b.record_review(task,'inspect',{'verdict':'PASS','run_digest':pk.digest(run),
    'evidence':run['artifacts']|{'analysis':finding},'observation':observation,'comparison':comparison,'open_defects':[]})
p=c.packet(task); brief=p['brief']; ref=brief['references'][0]
candidate={'version':'335-read-only-ownership','artifacts':{'inspect:'+k:v for k,v in run['artifacts'].items()}}
c.submit(task,p['actor'],p['ticket'],{'fingerprint':p['fingerprint'],'candidate':candidate,
    'reference_uses':{'reference_rear':{'reference_digest':pk.digest(ref),'application':'Reference phase comparison identifies needed coordinated control chain; no performance result claimed.'}},
    'requirement_uses':{r['id']:{'plan_digest':ep.plan_digest(brief),'application':r['criterion']+' Actual evidence interpreted in CONTROL_FINDINGS.md.'} for r in brief['requirements']}},'sikh335-inspection-built')
p=c.packet(task); d=pk.digest(candidate)
evidence={k:{'binding':v,'mode':'technical','candidate_digest':d,'scope':'Read-only ownership inventory, not production-media approval'} for k,v in run['artifacts'].items()}
evidence['analysis']={'binding':finding,'mode':'technical','candidate_digest':d,'scope':'Exact ownership diagnosis and retained artistic rejection'}
review={'fingerprint':p['fingerprint'],'candidate_digest':d,'evidence':evidence,
    'checks':[{'id':r['id'],'status':'PASS','observation':observation,'comparison':comparison,'evidence':list(evidence)} for r in brief['requirements']],
    'reference_checks':{'reference_rear':{'reference_digest':pk.digest(ref),'observation':'Reference whole-body loading contrasts with source rigid pivot; inventory identifies the relevant chain.',
        'comparison':'Required joints and ownership are identified, not corrected or approved.', 'evidence':['rig','analysis'],
        'aspects':[{'id':'whole_pose','status':'PASS','observation':'Control-discovery requirement met; faithful-motion qualification explicitly not claimed.'}]}},
    'audience_read':'No new audience media; this internal precursor removes unsupported assumptions.',
    'strongest_counterexample':'Driver repair alone cannot make a faithful rear or credible leader; all artistic defects remain open in the overall335 package.',
    'adjacent_review':'Source unchanged; no deformation, material, camera or cache mutation.',
    'open_visible_defects':[],
    'intent_checks':{'ownership':{'scope':'supported_evidence_only','status':'PASS','observation':observation,'comparison':comparison,'evidence':['rig','analysis']}},
    'planning_gaps':[]}
c.submit(task,p['actor'],p['ticket'],review,'sikh335-inspection-reviewed')
(out/'inspection-review.json').write_text(json.dumps(review,indent=2)+'\n')
print(c.state(task)['stage'])
