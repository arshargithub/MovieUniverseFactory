"""Encode the main agent's actual scoped observations, never an AV verdict."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];o=r/'results/sikh362'
def bind(p): return dict(path=p,sha256=pk.file_hash(r/p))
def evidence(p,mode,scope):return dict(binding=bind(p),mode=mode,scope=scope)
common={
 'chronology':evidence('results/sikh362/CHRONOLOGICAL_REVIEW.md','technical','Actual timed-frame/source observations; direct motion explicitly pending.'),
 'manifest':evidence('results/sikh362/media-manifest.json','technical','Verified source-frame/encoded media bindings and actual129-frame range.'),
 'source26':evidence('results/sikh362/source26-qualified.json','technical','Qualified exact99-source26 native output chain, not independent art approval.'),
 'landing':evidence('results/sikh362/LANDING_SOURCE_CONTROL.md','technical','Inherited actual14 accelerating arrival values and explicit source-preservation chain, not fresh26 measurements.'),
 'band':evidence('results/sikh362/appearance-c98-save-run.json','technical','Actual fixed seam construction output binding; visual evidence separately inspected.'),
 'finish':evidence('results/sikh362/appearance-c99-save-run.json','technical','Exact bounded crown/material change and source preservation, not anatomy or identity redesign.'),
 'static':evidence('results/sikh362/STATIC_REVIEW99.md','technical','Actual13 control observations, intended-shot limits and excluded principal closeups.'),
 'canonical':evidence('.runtime/factory-native/sikh362-appearance-c100-repeat/frame.png','image','Fresh production283, pixel-equal99 and27 canonical.'),
 'face':evidence('.runtime/factory-native/sikh362-appearance-c99-leader_face/frame.png','image','Diagnostic head/cloth/groom; simpler close face explicitly not qualified for principal portrait use.'),
 'reverse':evidence('.runtime/factory-native/sikh362-appearance-c99-leader_reverse/frame.png','image','Actual reverse stance seam/shoulder/crown/seat control.'),
 'crest':evidence('.runtime/art-direction/sikh362-review/frames11-sheet.jpg','image','Actual chronological332..339 with repeated283, not a playback substitute.'),
 'arrival':evidence('.runtime/art-direction/sikh362-review/frames13-sheet.jpg','image','Actual348..355 reach/contact/absorption/debris, not impact-audio evidence.'),
 'gather':evidence('.runtime/art-direction/sikh362-review/frames06-sheet.jpg','image','Actual292..299 gather, hands/cuffs and head/poll.'),
 'rise':evidence('.runtime/art-direction/sikh362-review/frames09-sheet.jpg','image','Actual316..323 upper rise and rider/cloth ownership.'),
 'tail':evidence('.runtime/art-direction/sikh362-review/tail_context-sheet.jpg','image','Actual377..380 unfinished principal context and canonical283, not crowd/principal acceptance.'),
 'accepted':evidence('.runtime/art-direction/series01-finish248/opening08/actual-450.png','image','Unmodified accepted Pashtun quality comparator; different identity, framing and light.'),
 'reference':evidence('.runtime/art-direction/series01-sikh257/reference-rear-contact.jpg','image','Preserved real reference phases, not direct playback or timing certification.')}
ev=list(common)
appearance={
'preservation':'Original accepted Pashtun control and native master remain unchanged;98/99 are reversible derivatives and100 no-edit save/reopen. Pixel identity at283 establishes readback at this profile, not universal strict replay.',
'form':'Rounded crown retains oblique cloth courses and fitted brow instead of pointed cap. Front/reverse posed controls retain supported coat, lower flare, uninterrupted ochre band and fitted saddle pad.',
'interfaces':'Actual stance/crest/arrival and chronological interiors retain neck/cuff/hand/band/seat/crown continuity.98 changes the consuming upper skirt edges, not a shader mask.99 preserves all actions and ownership.',
'evidence':'Actual13 all-angle99 controls and129 chronological source frames are bound to the same99 source.100/27 canonical repeats are pixel equal. Unfinished principal/crowd handles do not qualify those actors.',
'whole_look':'At the intended whole-mounted framing, indigo/ochre cloth layers, skin variation, full beard, rounded wrapped crown and dark bay coat/tack read coherently. Close diagnostic face is visibly simpler than the principal and is NOT admitted for close portrait reuse. No identified frame-visible blocker at this exact framing; fallible same-agent judgment, not Director acceptance.'}
motion={
'preservation':appearance['preservation']+'26/27 change neither action nor camera clock.',
'support':'Chronological stance/rise/descent retains visible hind support and folded/returning forelegs without an observed inversion; original segment/support controls retained through unchanged source. No universal animal-rig qualification.',
'phases':'Timed frames show gather/head lowering, driving rise, active upper pose, reaching descent, contact350 and subsequent absorption/debris. Inherited actual arrival data accelerate into contact; perceived biological fluidity and weight are reserved to Director313.',
'rider':'Pelvis/torso/head and arms differ through phases rather than a single rigid horse hinge; spear/cuffs/seat and complete reins remain attached in inspected images.24 full190-frame rein controls are retained; no physical rope/cloth simulation claim.',
'evidence':'All129 source frames252..380 at24fps and432x768/16 are bound; actual shot276..356 has24 frames each side. Canonical repeats agree; encoded technical decode is not direct-motion review.',
'director_motion':'NOT_RUN: Director must judge full-speed faithful-reference fluidity, weight, crest/arrival, rider/horse coordination and secondary response in this exact clip. No agent playback or listening is claimed.'}
for label,obs in [('appearance',appearance),('motion',motion)]:
 checks=[dict(id=k,status='NOT_RUN' if k=='director_motion' else 'PASS',observation=v,comparison='Original intent and faithful action reference; accepted-film supporting-shot floor, not rejected predecessor improvement. Human full-speed AV stays pending.',evidence=[] if k=='director_motion' else ev) for k,v in obs.items()]
 refs=dict(reference_rear=dict(observation='Whole action phase controls retain costume/seat/contact ownership through preparation, crest and landing. Real reference governs action, not identity.',comparison='Reference includes coordinated body/head/legs and absorption; current timed frames test these features but cannot certify real-time equivalence.',evidence=ev,aspects=[dict(id='whole_pose',status='PASS',observation='Image/source portion: real phased poses compared to actual gather/rise/crest/arrival; appearance ownership survives. Full-speed naturalness explicitly not passed.')]))
 if label=='appearance':refs['accepted_film']=dict(observation='Unmodified accepted Pashtun450 compared with actual99 supporting-shot controls, not close portrait pixel matching.',comparison='Differentiated materials, worn layered cloth and coherent actor/horse form at current framing; closer principal use would require renewed qualification.',evidence=ev,aspects=[dict(id='supporting_same_film',status='PASS',observation='Actual supporting framing retains material/layer richness without a known garment/contact defect; this fallible scoped judgment does not qualify the diagnostic face as a principal closeup.')])
 beat='appearance' if label=='appearance' else 'rear'
 review=dict(checks=checks,evidence=common,reference_checks=refs,audience_read='A mounted warrior responds through the rearing and settles, with layered costume and dark horse readable at this specific whole-shot size. Human full-speed effect pending.',strongest_counterexample='A complete clean encode and plausible poses may still feel robotic or too light. The diagnostic face also does not meet principal-closeup quality. Neither limitation is erased by hashes or tests; do not move this camera closer without new qualification.',adjacent_review='Checked band/coat consumers, reverse shoulder/seat/crown, face texture domain, hand/cuff/spear/reins and horse support/landing. Actual principal/crowd context remains unfinished and excluded; no new sound, environment or accepted Pashtun changes.',open_visible_defects=[],intent_checks={beat:dict(scope='supported_evidence_only',status='PASS',observation='All claimed source/timed-frame/image duties inspected; human motion remains NOT_RUN and unfinished context excluded. Old garment-only rationale does not substitute for explicit whole_look.',comparison='Original scoped mounted-leader intent, real rearing reference and accepted film floor, not only the inherited checklist.',evidence=ev)},planning_gaps=[])
 data=dict(version='sikh362-'+label+'-99-source-129frames',applications=obs,reference_applications={k:v['observation'] for k,v in refs.items()},review=review,derived_media={k:bind(p) for k,p in dict(clip='.runtime/art-direction/sikh362-review/nihang-leader-horse-362.mp4',manifest='results/sikh362/media-manifest.json').items()})
 p=o/(label+'-final-input.json');t=json.dumps(data,indent=2)+'\n'
 if p.exists():assert p.read_text()==t
 else:p.write_text(t)
 print(p)
