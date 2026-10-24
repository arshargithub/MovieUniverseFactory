"""Manually authored51 review observations; run only after actual final frame review.

This writes explicit source/image judgments, never Director AV acceptance.
"""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk,production_workflow as wf
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh368';media_root='.runtime/art-direction/sikh368-review-c51';c=wf.Controller(r,DATABASE);s=c.state('sikh335-continuous-performance');assert s['cycle']==51
assert (o/'FINAL_FRAME_REVIEW51.md').is_file() and (o/'ENCODED_REVIEW51.md').is_file()
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
paths={
 'review':('results/sikh368/FINAL_FRAME_REVIEW51.md','technical','Actual all39frame observations, originalreference and adjacent checks; no direct AV.'),
 'encoded':('results/sikh368/ENCODED_REVIEW51.md','technical','Actual decodedmedia/profile/crop checks.'),
 'pose':('results/sikh368/POSE_REVIEW51.md','technical','Actual side/oblique/shot controls.'),
 'report':('.runtime/factory-native/sikh368-motion-c51-prepare/prep367.json','technical','Actual39frame report and frozen1621 underlyinggeometry domains.'),
 'pole':('.runtime/factory-native/sikh368-motion-c51-audit/prepaudit367.json','technical','Actual11frame evaluatedCurve/terrain report.'),
 'forefeet':('results/sikh368/SOURCE_CONTROLS51.json','technical','Actual oppositeforefoot/braceplant landmark stability, not skin/force qualification.'),
 'brace_control':('results/sikh368/BRACE_EVENT_CONTROL51.json','technical','Actual49negative twoepisodes versus51singlebrace at three diagnostic thresholds.'),
 'hind_closure':('results/sikh368/HIND_CONTACT51_RESULT.json','technical','Actual38.8mm swing clearance/settledsupport; old50skate internallyrejected.'),
 'boundary':('results/sikh368/PHASE_BOUNDARIES51.json','technical','Actual finite24fps pose/velocity/contact handoff, later action invalidated.'),
 'preserved':('results/sikh368/PROTECTED_MASTERS.json','technical','Fresh acceptedPashtun/actual362source99 hashchecks.'),
 'manifest':('results/sikh368/media-manifest.json','technical','Exact39sourceframes/profile/canonical controls.'),
 'comparison':('results/sikh368/comparison-manifest.json','technical','Actual reference/candidate crops and normal-speed repeats.'),
 'ref_load':('.runtime/art-direction/sikh368-reference/reference-01.jpg','image','Actual30fps reference15.5..16.133: singlebrace and gathering.'),
 'ref_release':('.runtime/art-direction/sikh368-reference/reference-02.jpg','image','Actual30fps reference16.167..16.567: deepgather and rapid release.'),
 'side_swing':('.runtime/factory-native/sikh368-motion-c51-side/frame-0303.png','image','Actual hind swing while forefeet support.'),
 'side_load':('.runtime/factory-native/sikh368-motion-c51-side/frame-0306.png','image','Actual deep gathered neck/poll/body.'),
 'side_release':('.runtime/factory-native/sikh368-motion-c51-side/frame-0311.png','image','Actual head/neck release before substantial lift.'),
 'side_lift':('.runtime/factory-native/sikh368-motion-c51-side/frame.png','image','Actual firstlift with forelegs following.'),
 'shot_load':('.runtime/factory-native/sikh368-motion-c51-production/frame-0306.png','image','Actual shot load, not finalcamera/look pass.'),
 'shot_lift':('.runtime/factory-native/sikh368-motion-c51-production/frame.png','image','Actual shot firstlift; final speartip framing unqualified.'),
 'decoded':(media_root+'/decoded/candidate-sheet.jpg','image','Actual decodedcandidate samples.'),
 'decoded_comparison':(media_root+'/decoded/comparison-sheet.jpg','image','Actual decodedcomparison entry/load/release/exit.'),
}
for i in range(1,7):paths[f'phase{i:02d}']=(media_root+f'/phase{i:02d}.jpg','image','Actual complete chronological sourceframes, repeatedcanonical not added to timeline.')
ev={k:dict(binding=bind(p),mode=m,scope=t) for k,(p,m,t) in paths.items()}
apps={
 'preservation':'All1621 underlyingmesh/shape domains unchanged; fresh acceptedPashtun/actual362source99 hashes match. Originalsources/failures retained, disposablederivatives only. No material/identity/environment changes.',
 'prep_load':'Actual301..306 shows forebrace supporting hind gathering and body/poll load.50hindskate13.8cm was rejected;51actual38.8mm swing then settled306, checked in side/oblique/shot and completephase. Reference16.0..16.3 functional gathering governs, not a planted-foot angle statistic.',
 'step':'Actual292..300 contains one deliberate folded leftforebrace and plant; oppositeforehoof stays supporting through309. Actual49negative versus51landmark controls detect two versus one episodes at2/4/6cm, and allphase images confirm no secondforetap. Fullspeed weight remains Director judgment.',
 'head_body':'Actual300..307 visibly deeper gathered neck/poll/head with loaded trunk; actual309..311 rapid head/neck release leads substantial chest lift. Side and oblique distinguish deliberate coil from45danglingrelease; actual report preserves necklengths/seat. Chest appearance remains separately unaccepted.',
 'first_lift':'Actual309..314 head/neck rise overlaps chest drive; forelegs follow rather than initiate another flick. Hind support and rider seat/rein/pole retained. Actualmoving exit pose/velocity/contact recorded, no addedhold or wholeclip acceleration; real-time power/fluidity pending.',
 'scope':'Director368 prep only, originaltask51/max66 within50..57 (5new+3retained). No appearance/chest/laterrear/crowd/principal/environment/audio construction or newspend/provider/Astra/upload. Flagcache invalidated/hidden, not reused.',
 'evidence':'Actual39freshframes276..314, five side and four oblique/four shot controls, actual30fpsreference, source/contact controls, allsix sheets and decodedmedia reviewed. Native24fps1.625s silent proof plus3unchanged-speed repeats. No fullrear/production/release acceptance.',
 'director_motion':'NOT_RUN. Director313 owns fullspeed referencefaithfulness, preparation power/fluidity and head/neck/chest/foreleg ordering in exact clip; no agent direct-motion/listening claim.'}
sets={
 'preservation':['report','preserved','manifest'],
 'prep_load':['review','report','hind_closure','side_swing','side_load','ref_load','phase04','phase05'],
 'step':['review','report','forefeet','brace_control','ref_load','phase03','phase04','phase05'],
 'head_body':['review','report','pole','side_load','side_release','shot_load','ref_release','phase05','phase06'],
 'first_lift':['review','report','boundary','pole','side_release','side_lift','shot_lift','ref_release','phase05','phase06'],
 'scope':['review','report','manifest'], 'evidence':list(ev), 'director_motion':[]}
comp='Actual Director368 singlebrace/deepgather/rapidheadneckchestlead intent and original30fpsreference15.5..16.6, with fullphase15.0..16.625 context. View/slope differ; no pixelcopy or selfcertified100percent motion equivalence. Fullspeed AV pending.'
unit=s['brief']['work_unit'];positive={k:dict(status='PASS',observation=apps[k],comparison=comp,evidence=sets[k]) for k in ['prep_load','step','head_body','first_lift']}
bounds={k:dict(status='PASS',observation=('Actual276..277 stable entry state before cue, finitevelocity0; deliberately quiet referenceentry.' if k=='entry_stance' else 'Actual313..314 nonzero upward forehoof/bodymotion with hind support and forward-balanced rider; nextaction mustconsume exactexit, notheldzero velocity.'),comparison='Actual51 pose/finite24fps velocity/contact versus declared consuming interface; no subframe/force qualification.',evidence=['boundary','report','phase01' if k=='entry_stance' else 'phase06']) for k in ['entry_stance','firstlift_exit']}
review=dict(checks=[dict(id=k,status='NOT_RUN' if k=='director_motion' else 'PASS',observation=v,comparison=comp,evidence=sets[k]) for k,v in apps.items()],evidence=ev,reference_checks={'reference_rear':dict(observation='Actualonebrace/load/headneckchestlead features compared;49bilateral interpretation rejected,50hindcontact failure repaired. Natural-time fidelity remains Directorpending.',comparison=comp,evidence=list(ev),aspects=[dict(id=k,status='PASS',observation=apps[k]) for k in positive])},audience_read='One purposeful brace and deep gathering release into a fast head/neck/chest-led firstlift; fullspeed power judged by Director.',strongest_counterexample='Coherent source and clean stills can still play mechanically. Current proof ends at firstlift; fullrear/appearance cannot be inferred. IndependentAV notqualified.',adjacent_review='Fullphase and revealing side/oblique/shot support/neck/limbs/rider seat/rein/pole inspected.50skate rejected and repaired. Chest/look/finalcamera, laterrear and flagcache remain unaccepted outside prep.',open_visible_defects=[],intent_checks={'prep':dict(scope='supported_evidence_only',status='PASS',observation='Scoped source/image/technical positivefeatures and actualinternalcontactclosure checked. Fullspeed DirectorAV NOT_RUN; no fullrear or releasepass.',comparison=comp,evidence=list(ev))},planning_gaps=[],unit_review=dict(id=unit['id'],criteria=positive,boundaries=bounds,largest_remaining_mismatch=dict(blocking=False,observation='Fullspeed biological fluidity and powerful firstlift read cannot be passed from frame/source evidence; exactDirectorAV review remains required. Existinganatomy/look/latermotion notpassed.',evidence=['review','ref_release','phase05','phase06']),outside_scope_changes=[]))
m=pk.read_json(r,'results/sikh368/media-manifest.json');cm=pk.read_json(r,'results/sikh368/comparison-manifest.json')
data=dict(version='sikh368-c51-singlebrace-gather-headlead-39frames',applications=apps,reference_applications={'reference_rear':'Faithfulmotion authority explicitlyonefunctionalbrace, deepercoil and rapidheadneckchestlead; forelegsfollow. Actualreferencecaptions notstory/identity instruction. Later14..19s action remains scopefuture.'},unit_application=dict(id=unit['id'],criteria={k:apps[k] for k in positive},changed_domains=unit['allowed_domains'],boundaries={k:v['observation'] for k,v in bounds.items()}),review=review,derived_media=dict(clip=m['video'],manifest=bind('results/sikh368/media-manifest.json'),comparison=cm['three_normal_speed_repeats'],comparison_manifest=bind('results/sikh368/comparison-manifest.json')))
p=o/'final-input.json';assert not p.exists();p.write_text(json.dumps(data,indent=2)+'\n');print('Manually authored actual51 source/image findings; DirectorAV staysNOT_RUN')
