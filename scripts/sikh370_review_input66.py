"""Manually authored66 source/frame judgments; Director AV remains NOT_RUN."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk,production_workflow as wf
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh370';media='.runtime/art-direction/sikh370-review-c66';s=wf.Controller(r,DATABASE).state('sikh335-continuous-performance');assert s['cycle']==66

def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
paths={
 'review':('results/sikh370/FINAL_FRAME_REVIEW66.md','technical','Actual39frame/source/reference and adjacent review; not direct AV.'),
 'encoded':('results/sikh370/ENCODED_REVIEW66.md','technical','Actual media/profile and decoded-image observations.'),
 'contact':('results/sikh370/CONTACT_SOURCE66.json','technical','Actual all39 thickened-surface checks and retained actions/material/UV.'),
 'report':('.runtime/factory-native/sikh370-motion-c66-prepare/padsolve370.json','technical','Actual final contact before/after witnesses and original invariants.'),
 'pose':('results/sikh370/SOURCE_CONTROLS66.json','technical','Fresh-open11frame pose/landmark equality to53.'),
 'brace':('results/sikh369/BRACE_EVENT_CONTROL53.json','technical','Retained53 singlebrace event controls; no new independent test claim.'),
 'load':('results/sikh369/HIND_LOADING53.json','technical','Retained53 deeper hind flexion/pelvis source; actions unchanged.'),
 'boundary':('results/sikh369/PHASE_BOUNDARIES53-v2.json','technical','Retained moving entry/exit pose/velocity/contact.'),
 'handoff':('results/sikh370/REUSE_HANDOFF.json','technical','Exact native/cache interval and future-use limits.'),
 'preserved':('results/sikh370/PROTECTED_MASTERS.json','technical','Current protected master hash matches.'),
 'manifest':('results/sikh370/media-manifest.json','technical','39 unique frames and canonical controls/profile.'),
 'comparison':('results/sikh370/comparison-manifest.json','technical','Actual unchanged-time reference/candidate crops/repeats.'),
 'ref_load':('.runtime/art-direction/sikh368-reference/reference-01.jpg','image','Original30fps reference singlebrace/gathering.'),
 'ref_release':('.runtime/art-direction/sikh368-reference/reference-02.jpg','image','Original30fps deep gathering/head-led release.'),
 'side':(media+'/side-controls.jpg','image','Actual five side poses.'),
 'oblique':(media+'/oblique-controls.jpg','image','Actual four oblique poses.'),
 'shot':(media+'/production-controls.jpg','image','Actual four shot-camera poses.'),
 'crop':(media+'/saddle-contacts-before-after.jpg','image','Actual53 negative versus66 repaired interface.'),
 'decoded':(media+'/decoded/candidate-sheet.jpg','image','Actual8 candidate decode samples.'),
 'decoded_comparison':(media+'/decoded/comparison-sheet.jpg','image','Actual5 comparison decode samples.')}
for i in range(1,7):paths[f'phase{i:02d}']=(media+f'/phase{i:02d}.jpg','image','Actual complete chronological batch, no addedtime.')
ev={k:dict(binding=bind(p),mode=m,scope=t) for k,(p,m,t) in paths.items()}
apps={
 'preservation':'All1621 originalmesh/shape domains andoriginalactions unchanged; exactfresh-open11frame horse/rider/bone/pole match53. One newtechnicalpad/cache explicit; sameUV/material andprotectedmasters match.',
 'prep_load':'Actual301..307 retains53deeperhindflexion and~39mmlowerpelvis versus51, coupledhead/neck/trunk gathering. Actualside/oblique/shot/allphase images reviewed; no secondforetap. Degree/weight/fullspeed referencefaithfulness remainDirectorpending.',
 'step':'Actual292..300 shows one foldedforehoof brace andplant, oppositeforehoof supporting. Retained53eventcontrol/sourceactions plusall39actualframes supportcount/function, not forces orbiologicalfluidity.',
 'head_body':'Actual300..307 loweredhead/poll/neck andgatheredtrunk;308..311 head/neck release leads substantialchest travel. Source53frozen and actualside/oblique/shot/allphase inspected; anatomy/look acceptance remains separate.',
 'first_lift':'Actual311..314 rise ismovingexit, forelegs followhead/neck/chest, hind support/riderseat/rein/pole preserved. Exact53pose/velocityhandoff and66cacheexit bound; laterrear/cacheunqualified. Noaddedhold/retime.',
 'scope':'Originaltask66/max66, allnineexistingDirector370corrections58..66 used. Frozen53performance, onepadcontactderivative only; no appearance/tail/latermotion/crowd/principal/environment/sound/spend/provider/Astra/upload.',
 'evidence':'All39sourceframes and13revealing/shotcontrols, actualreference, matchednegativecrop and8candidate/5comparisondecoded samples inspected. Native24fps1.625s and3normal-speed repeats4.875s. Scopedframe/source ready; no production/release/directAV pass.',
 'director_motion':'NOT_RUN. Director313 owns natural-time weight, power, referencefaithfulness/fluidity and temporalcloth read of exact clip. No agent direct-motion/listening assertion.'}
sets={'preservation':['contact','pose','preserved','handoff'],'prep_load':['review','pose','load','side','oblique','shot','ref_load','phase04','phase05'],'step':['review','pose','brace','ref_load','phase03','phase04'],'head_body':['review','pose','side','oblique','ref_release','phase05','phase06'],'first_lift':['review','pose','boundary','handoff','ref_release','phase06'],'scope':['review','handoff','preserved'],'evidence':list(ev),'director_motion':[]}
comp='OriginalDirector368/369functionalbrace/deeperhindload/headledrelease and reference15.0..16.625s. Frozen53 retained, tack repaired; camera/slope/form differ. No pixelcopy/100percentbiologicalequivalence ordirectAV claim.'
positive={k:dict(status='PASS',observation=apps[k],comparison=comp,evidence=sets[k]) for k in ['prep_load','step','head_body','first_lift']}
bounds={k:dict(status='PASS',observation=('Retained53quietentry276..277, actualframecontinuity andfiniteboundarysource;66cacheentry nowbound.' if k=='entry_stance' else 'Retained53moving313..314 exit withhind support/headledrise; exact66clothkeyexit and originalbodypose/velocity mustfeednextunit.'),comparison='Actualsource-bound53boundary versus66zero-differencepose controls andnewcache interval; notsubframequalification.',evidence=['boundary','pose','handoff','phase01' if k=='entry_stance' else 'phase06']) for k in ['entry_stance','firstlift_exit']}
review=dict(checks=[dict(id=k,status='NOT_RUN' if k=='director_motion' else 'PASS',observation=v,comparison=comp,evidence=sets[k]) for k,v in apps.items()],evidence=ev,reference_checks={'reference_rear':dict(observation='Actualreference sheets andnormal-time encodedcomparison checked forsinglefunctionalbrace, gather/headlead andfirstlift. Exacttemporalnaturalness pendingDirector.',comparison=comp,evidence=list(ev),aspects=[dict(id=k,status='PASS',observation=apps[k]) for k in positive])},audience_read='Purposeful singlebrace andgathering intohead-ledfirstlift; fullspeed power andfaithfulness remainDirector judgment.',strongest_counterexample='Clear sampledcontact andtimedframes canstilllookmechanical orjitter inplayback. Currentproofendsfirstlift; no wholehorseappearance/secondary/latermotion qualification.',adjacent_review='Actualcompletephase plus side/oblique/shot support,cloth,neck/rider/rein/pole inspected.53brownpatches gone; localbluefolds present withoutobviouslargespike/float intheseviews. Unseen-camera/fullpadasset andchest/tail/look notqualified.',open_visible_defects=[],intent_checks={'prep':dict(scope='supported_evidence_only',status='PASS',observation='Scopedsource/imageknowncontactclosure andpositivefeatures checked; DirectorfullspeedNOT_RUN andfullrear/appearance excluded.',comparison=comp,evidence=list(ev))},planning_gaps=[],unit_review=dict(id=s['brief']['work_unit']['id'],criteria=positive,boundaries=bounds,largest_remaining_mismatch=dict(blocking=False,observation='Natural-time referencefidelity/weight/fluidity andtemporalcloth read needplannedDirectorAV. Geometry/appearance andlaterrear remainunaccepted outsideunit.',evidence=['review','ref_release','phase05','phase06']),outside_scope_changes=[]))
m=pk.read_json(r,'results/sikh370/media-manifest.json');cm=pk.read_json(r,'results/sikh370/comparison-manifest.json')
data=dict(version='sikh370-c66-frozen53-preparation-contactrepair-39frames',applications=apps,reference_applications={'reference_rear':'Faithfulmotion authority forsinglefunctionalbrace/gathering/headneckchestlead; actualreference/wholeunitnormal-timecomparison bound. No identity/environment adoption andno laterphaseapproval.'},unit_application=dict(id=s['brief']['work_unit']['id'],criteria={k:apps[k] for k in positive},changed_domains=['tack_contact'],boundaries={k:v['observation'] for k,v in bounds.items()}),review=review,derived_media=dict(clip=m['video'],manifest=bind('results/sikh370/media-manifest.json'),comparison=cm['three_normal_speed_repeats'],comparison_manifest=bind('results/sikh370/comparison-manifest.json')))
p=o/'final-input66.json';assert not p.exists();p.write_text(json.dumps(data,indent=2)+'\n');print('Actual66scope/image/source observations recorded; DirectorAV staysNOT_RUN')
