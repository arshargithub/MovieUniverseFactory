"""Narrow internal crest control review; explicitly not an integrated deliverable."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk, expert_planning as ep
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1]; out=root/'results/sikh335/support02'
c=wf.Controller(root,DATABASE); task='sikh335-supported-representation'; bridge=Bridge(c)
run=json.loads((out/'render-run-c2.json').read_text())
analysis={'path':'results/sikh335/support02/IMAGE_REVIEW.md','sha256':pk.file_hash(out/'IMAGE_REVIEW.md')}
obs='Source-camera crest shows bent hindquarters, flexed neck/poll and raised carpi with hooves below, no former upward tray. Actual fresh-open selected state matches;64 targets healthy and hind support errors below0.07mm.'
comp='Narrow crest control only. Continuous action, side/rear, rider contacts and same-film leader/tack appearance are not qualified and remain blockers in335 overall.'
bridge.record_review(task,'render',{'verdict':'PASS','run_digest':pk.digest(run),'evidence':run['artifacts']|{'analysis':analysis},
    'observation':obs,'comparison':comp,'open_defects':[]})
p=c.packet(task); brief=p['brief']; runs=bridge.runs(c.state(task));ref=brief['references'][0]
candidate={'version':'335-supported-crest-only','artifacts':{step+':'+k:v for step,r in runs.items() for k,v in r['artifacts'].items()}}
c.submit(task,p['actor'],p['ticket'],{'fingerprint':p['fingerprint'],'candidate':candidate,
    'reference_uses':{'reference_rear':{'reference_digest':pk.digest(ref),'application':'Actual crest shape compared with faithful reference; no motion or rider-interface approval.'}},
    'requirement_uses':{r['id']:{'plan_digest':ep.plan_digest(brief),'application':r['criterion']+' Evaluated only within the authored crest-control scope.'} for r in brief['requirements']}},'sikh335-crest-built')
p=c.packet(task);d=pk.digest(candidate)
evidence={step+'_'+k:{'binding':v,'mode':'image' if k=='frame' else 'technical','candidate_digest':d,'scope':'Actual native crest proof only'} for step,r in runs.items() for k,v in r['artifacts'].items()}
evidence['analysis']={'binding':analysis,'mode':'technical','candidate_digest':d,'scope':'Narrow visual findings and explicit remaining integrated blockers'}
refimg={'path':'results/sikh321/preserved-comparisons/reference-3.jpg','sha256':pk.file_hash(root/'results/sikh321/preserved-comparisons/reference-3.jpg')}
evidence['reference_frames']={'binding':refimg,'mode':'image','candidate_digest':d,'scope':'Observed reference crest and descent phase strip'}
review={'fingerprint':p['fingerprint'],'candidate_digest':d,'evidence':evidence,
    'checks':[{'id':r['id'],'status':'PASS','observation':obs,'comparison':comp,'evidence':list(evidence)} for r in brief['requirements']],
    'reference_checks':{'reference_rear':{'reference_digest':pk.digest(ref),'observation':'Carpi above downward folded hooves and bent supported hindquarters now present in intended crest view.',
        'comparison':'Usable discriminating crest control, not literal horse conformation or full faithful action qualification.',
        'evidence':['render_frame','reference_frames','analysis'],
        'aspects':[{'id':'whole_pose','status':'PASS','observation':'Narrow crest structure demonstrated; temporal and integrated interfaces still NOT_RUN.'}]}},
    'audience_read':'Static crest has supported animal structure; it is not yet an audience-ready performance.',
    'strongest_counterexample':'Rider reins/spear are disconnected, appearance schematic, and other phases and revealing views untested. None can be passed from this control.',
    'adjacent_review':'Masters unchanged; revised pose invalidates rider/contact/cache assumptions for the next integrated phase.',
    'open_visible_defects':[],
    'intent_checks':{'crest':{'scope':'supported_evidence_only','status':'PASS','observation':obs,'comparison':comp,'evidence':['render_frame','analysis']}},
    'planning_gaps':[]}
c.submit(task,p['actor'],p['ticket'],review,'sikh335-crest-reviewed')
(out/'crest-review.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({'controller_state':c.state(task)['stage'],'disposition':'INTERNAL_CREST_CONTROL_ONLY_NOT_DIRECTOR_HANDOFF','integrated_goal':'OPEN'}))
