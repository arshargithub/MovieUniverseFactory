"""Manually authored failed71 source/frame review; never self-pass AV."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk,production_workflow as wf
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh371';media='.runtime/art-direction/sikh371-review-c71';s=wf.Controller(r,DATABASE).state('sikh335-continuous-performance');assert s['cycle']==71

def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
paths={
 'review':('results/sikh371/FINAL_FRAME_REVIEW71.md','technical','Actual58frame/revealing/source/reference failure-seeking review; no directAV.'),
 'encoded':('results/sikh371/ENCODED_REVIEW71.md','technical','Actualencodedprofiles/ninecandidate/fivecomparison decodedimages inspected.'),
 'contact':('results/sikh371/CONTACT_SOURCE71.json','technical','Actual19sampled finalsurfacecontact andoriginalmotion/mesh invariants.'),
 'source':('results/sikh371/SOURCE_CONTROLS71.json','technical','All39acceptedprefixstates andscalartrack errorzero.'),
 'pose':('.runtime/factory-native/sikh371-motion-c71-prepare/apex371.json','technical','All19actualphase poses, support/reach andprefixpreservation report.'),
 'solver':('src/movie_factory/adapters/blender/nihang_support.py','technical','Actualsolverlowerforefootdirection lacksindependentapexflexion.'),
 'protected':('results/sikh371/PROTECTED_MASTERS.json','technical','Acceptedmasterlocalhashes preserved.'),
 'handoff':('results/sikh371/REUSE_HANDOFF.json','technical','Candidate333state/source contact; NOTaccepted, no oldlanding/cache reuse.'),
 'side':('.runtime/factory-native/sikh371-motion-c71-side/frame-0323.png','image','Highcrest wholesideview andsaddlecontact.'),
 'reverse':('.runtime/factory-native/sikh371-motion-c71-reverse/frame-0323.png','image','Revealingreverse support/rider/contact view.'),
 'shot':('.runtime/factory-native/sikh371-motion-c71-production/frame-0323.png','image','Actualstoryframe; horsevisible, riderpartlybehindhorse, no storycameraapproval.'),
 'compare_apex':(media+'/decoded/comparison-04.png','image','Actualreference/candidate apex: lowerlegs hang instead ofcurling.'),
 'compare_hold':(media+'/decoded/comparison-05.png','image','Actualreference/candidate activecrest; insufficientlowerlimbarticulation.'),
 'reference':('.runtime/art-direction/sikh371-reference/crest-02.jpg','image','Actual17.0..17.467reference activecrest, faithfulmotionauthority.')}
for step in ['phase01','phase02','phase03','accepted01','accepted02','accepted03']:paths[step]=(media+'/'+step+'.jpg','image','Actualcomplete chronologicalframes inspected, notdirectmotion.')
ev={k:dict(binding=bind(p),mode=m,scope=t) for k,(p,m,t) in paths.items()}
apps={
 'preservation':'All39acceptedprefixposes/scalartracks exact; all1622originalmeshdomains unchanged. Contactchanges onlydeclaredvisibilitytracks/newnativecache. Masterslocalhashverified.',
 'rise':'Actual315..323 frame/sourceproof risesstronglyfrommoving314 tohighrear, forelegs gatherafterbody. Wholehead/feet visible in side/reverse/story controls. Fullspeedpowerhumanpending.',
 'crest':'FAIL. Matchedreferenceapex/hold andsource solver shownearverticalhanginglowerforelegs andinsufficientactivecurl. Tinyunequalkeychanges do notachieve requiredlivingcrest. Internalrejection, no readyqueue.',
 'balance':'Actualsampled hindgroundsupport/limblength guards andriderseat/rein/pole/coherentpad remain; no newobviousstretch/skate/contacthole inrevealingviews. Biologicalweight/fullspeed stillNOT_RUN.',
 'continuity':'Accepted276..314 frozen; exact314evaluatedboundarypinned beforefuturekeyreplacement. All58samefixedview, canonical333repeatdiffzero, finite333source/velocityhandoff bound butnotaccepted.',
 'scope':'Original71/max71, allfiveDirector371cycles67..71 used. No72/newspend/tool/provider/Astra/upload/landing/appearanceconstruction; failurehistory retained.',
 'evidence':'All58actualframes, primary/revealing/reverse/story/boundarycontrols, actualreference anddecodedcomparison inspected. Knowncrestfailure remainsopen; production/fullspeedapprovalnotclaimed.',
 'director_motion':'NOT_RUN. Director313 isdirectAVjudge, butknowncrestfailureblocksreadyqueue beforehumanacceptance.'}
sets={'preservation':['source','contact','protected','handoff'],'rise':['review','pose','side','reverse','reference','phase01'],'crest':['review','solver','compare_apex','compare_hold','reference','phase02','phase03'],'balance':['review','contact','pose','side','reverse','shot'],'continuity':['review','source','pose','handoff','accepted03','phase01'],'scope':['review','protected','handoff'],'evidence':list(ev),'director_motion':[]}
comp='OriginalDirector371apex/hold intent, faithful reference16.5..18.0, accepted66preparation. Currenthighpose/source/contact gains do notwaive missing lowerforelegcurl/activehold; fullspeedAVpending.'
positive={k:dict(status='FAIL' if k=='crest' else 'PASS',observation=apps[k],comparison=comp,evidence=sets[k]) for k in ['rise','crest','balance','continuity']}
bounds={k:dict(status='PASS',observation=('All39acceptedprefixpose/scalartrack samples exact; actual314 movingexit feeds315.' if k=='accepted_firstlift_entry' else 'Actual332333sourceposes/supports andnative bound; crest NOTaccepted, onlyfinitecurrentstate forfuturecorrection. Do notstartoldlanding.'),comparison=comp,evidence=['source','pose','handoff','accepted03' if k=='accepted_firstlift_entry' else 'phase03']) for k in ['accepted_firstlift_entry','active_crest_exit']}
review=dict(checks=[dict(id=k,status='NOT_RUN' if k=='director_motion' else 'FAIL' if k=='crest' else 'PASS',observation=v,comparison=comp,evidence=sets[k]) for k,v in apps.items()],evidence=ev,reference_checks={'reference_rear':dict(observation='Actualreference anddecodedcomparison revealmissingforefootcurl/activecrest. Currenthighrise isusefulbutwholeunitfails.',comparison=comp,evidence=list(ev),aspects=[dict(id=k,status='FAIL' if k=='crest' else 'PASS',observation=apps[k]) for k in positive])},audience_read='Bodyreachesahighrear, buthangingforefeet andinsufficientarticulationstillriskmechanicalstatue read.',strongest_counterexample='Nonzeroangles/contactmetrics passedwhileactualreferencecomparisonfails. Do notdelegateknownsource/framefailuretoDirectorAV.',adjacent_review='Wholephase/sides/reverse/story inspectsupport,seat/reins/pole,neck andpad. Frozenchest/look/tail/flag andlegacydusttiming remainunaccepted; nonequalifiedforthenewclock.',open_visible_defects=['Apexlowerforelegs hangnearverticalinstead ofreference-shapedcurl andactiveadjustment.'],intent_checks={'apex':dict(scope='supported_evidence_only',status='FAIL',observation=apps['crest'],comparison=comp,evidence=sets['crest'])},planning_gaps=[],unit_review=dict(id=s['brief']['work_unit']['id'],criteria=positive,boundaries=bounds,largest_remaining_mismatch=dict(blocking=True,observation=apps['crest'],evidence=sets['crest']),outside_scope_changes=[]))
m=pk.read_json(r,'results/sikh371/media-manifest.json');cm=pk.read_json(r,'results/sikh371/comparison-manifest.json')
data=dict(version='sikh371-c71-highrear-crest-INTERNAL-FAIL',applications=apps,reference_applications={'reference_rear':'Faithfulmotionauthority; actualreferencecomparison uncoversmissinglowerforelegcurl/activecrest despitehighpose andsourceguards.'},unit_application=dict(id=s['brief']['work_unit']['id'],criteria={k:apps[k] for k in positive},changed_domains=['horse_pose','rider_contact','rein_control','secondary_cache_invalidation','tack_contact'],boundaries={k:v['observation'] for k,v in bounds.items()}),review=review,derived_media=dict(clip=m['video'],manifest=bind('results/sikh371/media-manifest.json'),comparison=cm['three_normal_speed_repeats'],comparison_manifest=bind('results/sikh371/comparison-manifest.json')))
p=o/'final-input71.json';assert not p.exists();p.write_text(json.dumps(data,indent=2)+'\n');print('Actualfailedcrest/source/framejudgment recorded. No readyAVqueue.')
