"""Manually authored scoped75 source/frame judgments; DirectorAV remains pending."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk,production_workflow as wf
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh372';media='.runtime/art-direction/sikh372-review-c75';s=wf.Controller(r,DATABASE).state('sikh335-continuous-performance');assert s['cycle']==75

def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
paths={
'review':('results/sikh372/FINAL_FRAME_REVIEW75.md','technical','Actualnewchronology/revealing/reference/source review; notdirectAV.'),
'encoded':('results/sikh372/ENCODED_REVIEW75.md','technical','Actualprofiles andninecandidate/fivecomparison decodedimages inspected.'),
'contact':('results/sikh372/CONTACT_SOURCE75.json','technical','NEW74cache all19finalsurfacechecks, notold71reuse.'),
'source':('results/sikh372/SOURCE_CONTROLS75.json','technical','All39acceptedprefixpose/scalartracks exact; geometryunchanged.'),
'pose':('.runtime/factory-native/sikh372-motion-c74-prepare/apex371.json','technical','Actual19coupledbody/rider/support/head states andprefixguards.'),
'distal':('.runtime/factory-native/sikh372-motion-c74-prepare/crest372.json','technical','Actualdistalarticulation/segment/wrist/upstreamsourceguard states.'),
'protected':('results/sikh372/PROTECTED_MASTERS.json','technical','Protectedmasterlocalhashes match, no newremotebackupclaim.'),
'handoff':('results/sikh372/REUSE_HANDOFF75.json','technical','Exact333native/source/velocity/support/cache andnextlandinglimits.'),
'early':('results/sikh372/EARLY_REVIEW74.md','technical','Fouractualpairedposes inspected BEFOREcache/fullrender.'),
'side':('.runtime/factory-native/sikh372-motion-c75-final_side/frame.png','image','Actualfinal333side AFTERnewcache; wholehead/feet/pad visible.'),
'reverse':('.runtime/factory-native/sikh372-motion-c74-reverse/frame.png','image','Actualreverse fromexact74contactsource laterreadonlysaved75.'),
'shot':('.runtime/factory-native/sikh372-motion-c74-production/frame.png','image','Actualstoryframe fromexactsource; no camera/leaderlookapproval.'),
'compare_apex':(media+'/decoded/comparison-04.png','image','Actualreference/current323 approachtohighercrest.'),
'compare_hold':(media+'/decoded/comparison-05.png','image','Actualreference/current333 highcrest withopenforelimbs.'),
'reference':('.runtime/art-direction/sikh371-reference/crest-02.jpg','image','Actual17.0..17.467referencebody/foreleg crestphase.'),
'overcurl72':('.runtime/art-direction/sikh372-review-c72/early-pair-0323.jpg','image','REJECTEDnegativecomparison: overcurl andprematurebodyhold, notcurrentcandidate.'),
'prefix':('.runtime/art-direction/sikh372-review-c75/prefix.jpg','image','Freshacceptedstance/load/firstlift pluscurrentcrest controls.'),
'save':('results/sikh372/SOURCE_SAVE75.json','technical','Exactselected333snapshot equality aftertrustedreadonlysave.'),
'jobs':('results/sikh372/OPERATING_JOBS75.json','technical','Actual16nativejobs andunknownengineeringusage, notartisticPASS.'),
'learnings':('results/sikh372/LEARNINGS.md','technical','Wholephase/earlypairedproof/versionedviews andtypedpreflight learning.')}
for step in ['phase01','phase02','phase03']:paths[step]=(media+'/'+step+'.jpg','image','Allnewchronologicalsourceframes inspected, no directmotion assertion.')
ev={k:dict(binding=bind(p),mode=m,scope=t) for k,(p,m,t) in paths.items()}
apps={
'preservation':'All39Directoraccepted276..314pose/scalarstates exact, originalgeometryunchanged; protectedmasters match.75readonlysource selectedsnapshot equals74, freshprefix/camera/hash checks justify39image reuse.',
'rise':'Actual315..329images/source showstrongcontinuedrise intohighercrest; forelegs gatherfollowingtrunk. Initial71anchors retainedthrough319 withlaterinterpolantsrevalidated, notclaimedexact. Fullspeedpower remainsDirectorjudgment.',
'crest':'Actualreferencepairs/newchronology/decoded333 showhigherbalancedcrest andmodestunequalforeleg/toe/head/body adjustments.72overcurl/prematurebodyhold corrected. No frozenidenticalposecopy, no source/frame-visibleknownblocker; actualnaturalhold/fluidity NOT_RUN.',
'balance':'Actual19support/reach/necklength/segmentguards pass, sampledside/reverse/story showgroundedhindfeet andcoherentseat/reins/pole. NEW74padall19min3.9996mm, finalsideAFTERcache showsnooldholes/spikes. No biologicalforce/subframephysicsclaim.',
'continuity':'Accepted314movingentry preserved,315zerodistaldelta; samefixedcamera, source/camera/hash/pixelprefix checks allpass.333native andlasttwocoupled/distalstates bindnextlanding; old334+action/cache notqualified.',
'scope':'Original75/max76, fourof5additional72..75used, one76remaining.75readonlycompletionof74motion; no landing/appearance/crowd/newspend/provider/model/install/upload. Allfailedhistory retained.',
'evidence':'All19newtimedframes, fourpairedside/oblique controls, postcache side/reverse/story/prefix andactualencoded samples inspected.58frameunretimedclip+3normal-timecomparisons; manual313AVpending, notproductionapproval.',
'director_motion':'NOT_RUN. Director313 ownsactualfullspeedpower/fluidity/weight/referencefaithfulness andbriefhold/clothread. Source/frame checks donotselfpass this.'}
sets={'preservation':['source','contact','protected','save','prefix','handoff'],'rise':['review','pose','early','compare_apex','reference','phase01','phase02'],'crest':['review','distal','early','compare_apex','compare_hold','reference','overcurl72','phase02','phase03'],'balance':['review','contact','pose','distal','side','reverse','shot'],'continuity':['review','source','pose','distal','handoff','prefix','phase01','phase03'],'scope':['review','protected','handoff','jobs'],'evidence':list(ev),'director_motion':[]}
comp='Director372reference-faithfulactivecrestmicro-motion withaccepted66preparation. Actualoriginalreference16.633..17.367/wholephase compared; supportedsource/frame features only, no directAV/wholeassetapproval.'
positive={k:dict(status='PASS',observation=apps[k],comparison=comp,evidence=sets[k]) for k in ['rise','crest','balance','continuity']}
bounds={k:dict(status='PASS',observation=('All39acceptedprefix/source/tracks exact,314movingboundary preserved; actualfreshprefixcontrols match.' if k=='accepted_firstlift_entry' else 'Actual333native/lasttwosupport/coupledbody anddistalstates bound, finiteentryfornextlanding; beyond333 invalidated, notqualified.'),comparison=comp,evidence=['source','pose','distal','handoff','prefix' if k=='accepted_firstlift_entry' else 'phase03']) for k in ['accepted_firstlift_entry','active_crest_exit']}
review=dict(checks=[dict(id=k,status='NOT_RUN' if k=='director_motion' else 'PASS',observation=v,comparison=comp,evidence=sets[k]) for k,v in apps.items()],evidence=ev,reference_checks={'reference_rear':dict(observation='Actualwholephase/referencepairedposes anddecodedcomparison supporthighcontinuedcrest/openunequalforelimbs andcorrected72failure. Natural-timefaithfulness remainsDirector313judgment.',comparison=comp,evidence=list(ev),aspects=[dict(id=k,status='PASS',observation=apps[k]) for k in positive])},audience_read='Reference-ledstrongrise intohighbalancedcrest withbriefunequalforelegadjustment; power/weight/fullspeednaturalness remainshumanpending.',strongest_counterexample='Posed/timedframes andclearcontactcanstilllookrobotic/jitterinplayback. No agentdirectmotioncapability; exactnormal-timeclip goes toplannedDirectorAV, notselfapprovedproduction.',adjacent_review='Actual19newframes plusfinalsideAFTERcache, reverse/story/prefix anddecodedcontrols inspectneck/limbs/support/rider/reins/pole/pad. Frozenlook/chest/tail/flag/legacydust/landing unqualified, nothiddenorpromoted.',open_visible_defects=[],intent_checks={'apex':dict(scope='supported_evidence_only',status='PASS',observation='Knownprematurecrest/72overtuck corrected inactualpaired/newframes; no scopedsource/frame blocker, DirectorAVpending andoutsideappearance/landing excluded.',comparison=comp,evidence=list(ev))},planning_gaps=[],unit_review=dict(id=s['brief']['work_unit']['id'],criteria=positive,boundaries=bounds,largest_remaining_mismatch=dict(blocking=False,observation='Actualfullspeedpower/fluidity/hold/read needsplannedDirector313AV. Frozenform/appearance/secondary/landing separatelyunaccepted; no knownscopedsource/framefailure.',evidence=['review','reference','compare_hold','phase03']),outside_scope_changes=[]))
m=pk.read_json(r,'results/sikh372/media-manifest75.json');cm=pk.read_json(r,'results/sikh372/comparison-manifest75.json')
data=dict(version='sikh372-c75-source-frame-ready-reference-led-crest',applications=apps,reference_applications={'reference_rear':'Faithfulmotionauthority, actualpairedreference/wholephasecomparison. No copyingidentity/slope/caption; fullspeedbiologicalperformance notselfqualified.'},unit_application=dict(id=s['brief']['work_unit']['id'],criteria={k:apps[k] for k in positive},changed_domains=['horse_pose','rider_contact','rein_control','secondary_cache_invalidation','tack_contact'],boundaries={k:v['observation'] for k,v in bounds.items()}),review=review,derived_media=dict(clip=m['video'],manifest=bind('results/sikh372/media-manifest75.json'),comparison=cm['three_normal_speed_repeats'],comparison_manifest=bind('results/sikh372/comparison-manifest75.json')))
p=o/'final-input75.json';assert not p.exists();p.write_text(json.dumps(data,indent=2)+'\n');print('Actual75source/frameobservations recorded; DirectorAV NOT_RUN.')
