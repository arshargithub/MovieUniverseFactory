# Supporting cast internal review

The integrated319 review candidate is complete. No candidate below has passed
Director review or the production gate.

## Source inspection

The current leader has a coarse anatomical donor head, separate facial details,
solid beard bars, regular crown layers, disconnected garment contributors and
mitten palms. Source318 frame283 and crowd frame480 show these at shot scale.
The original Nihang reference at16s establishes a tall tied crown, blue chola,
mounted command and coordinated acknowledgement. It does not authorize copying
incidental written commentary or changing the story.

The existing Blender Studio donor is the recorded CC0 anatomical substrate
(`SERIES_01_SIKH_ASSET_STRATEGY_262.md`, source strategy). The current secondary
extraction omitted its evaluated sculpt detail.319 retains that detail; it does
not import a new asset or qualify the donor as finished character art.

## Internal failures retained

| Candidate | Evidence | Finding and consequence |
| --- | --- | --- |
| Build01 | worker exception | Brow-prefix/type assumption failed; no scene or visual pass |
| Build02 | worker exception | Static vertex collection was confused with shape-key data; no scene or visual pass |
| Build03 | look03 frames283/375/480 | Beard intersects chest; hard sleeve-to-torso openings; inadequate brows and moustache. Rejected before full render |
| Build04 | study04 front/oblique and face-surface coordinates | Continuous garment representation built, but beard still reads as a straight curtain, crown courses produce pointed top/gaps, facial detail fit is wrong. Rejected before full render |
| Build05 | study05 and actual-shot proofs | Facial features are visible, but beard backing protrudes through curved hair and moustache tips look uniformly cut. Crown cap and shoulder form still require review. Rejected before full render |
| Build06 | saved native plus `build6-reopen-crash.txt` | Save succeeded but fresh open crashed. Curve-data shape-key follow was removed afterward; that association does not establish the exact native crash cause. No persistence pass |
| Build07 | study07 front/oblique; look07; check07 geometry | Donor-derived garment was visibly fragmented by the construction operation. Sash penetration and neckline contamination. Internal FAIL |
| Build08 | study08 | Removing sequential normal inflation restored a continuous garment. This is a discriminating construction control, not a finished costume: bare anatomy, neckline and moustache still needed work |
| Build09 | study09 and look09 | Snapshotting normals before vertex edits removed the catastrophic breakup; smaller seam and donor-shoulder problems remained. Shirt reproduced bare pectorals too literally |
| Build10 | study10 front/oblique | Fabric envelope improved; closed turban course had reversed seam winding, donor neck crop exposed jagged shoulder remnants, hair roots floated. Internal FAIL, not a review-ready character |
| Build11–12 | neutral and actual-shot studies | Crown closure improved; ear hair roots and head-owned lower-neck motion still exposed a discontinuity. Replaced rigid neck ownership with a torso/head blend and kept the jaw outside that blend |
| Build13 | look13 frame480 | Crowd donor torso faced opposite its head. Garment front and sash were not on the visible anatomical front; boot soles appeared separate. Internal FAIL |
| Build14 | look14 frames283/333/480 | Garment semantic orientation and boot connection improved; actual crowd frame exposed offset pole grips and empty clenched hands. Added shaft/handle fitting and bounded departure attention |
| Build15 | look15 and verify15/interfaces.json | Actual-shot forms improved, crowd spear-axis error under0.004mm; full696-frame check found a109.5mm leader cuff error during the rapid spear plant. Sparse four-frame garment samples were insufficient. Internal FAIL; candidate16 adds per-frame samples through that interval |
| Build16 | verify16; study16; benchmark16 | Frame-dense spear interval reduced cuff-centroid maximum to under0.01mm;1476 protected objects, actor roots and spear geometry/action unchanged. Neutral profile still showed excess beard projection. Two-worker benchmark was slower and exceeded the chosen combined-memory bound; serial selected |
| Refine17 | study17 front/oblique | Pointwise surface projection introduced sharp beard kinks. Visually rejected; its benchmark was deliberately stopped after identifying the exact worker. Partial logs/frames and failed job are retained |
| Refine18 | study18 oblique | Continuous replacement guides removed jumps but changed the established beard mass into a thin straight curtain. Rejected; no complete sequence render |
| Refine19 | study19 front/oblique; serial19 actual-shot controls; verify19 | Returned to16's lock design, fixed roots and reduced forward throw smoothly. Actual-shot leader/crowd forms and prop/cuff checks admitted to the complete render only, not Director/artistic approval. Full timeline contact and protected-object checks remain clear. Complete encoded review and Director AV still pending |

## Construction reassessment and evidence limits

The original tube-union representation was abandoned after its shoulder and
deformation failures. The replacement uses continuous anatomical shoulder/arm
topology, a fabric envelope that bridges bare anatomy, and measured wrist
attachments to the existing action owners. Donor shoulder remnants belong
inside a continuous neck/garment interface, not a visible jagged crop.

Surface mutation must use frozen coordinates/normals, followed by an explicit
update; it must not repeatedly read mutable normals while editing adjacent
vertices. Closed cloth routes need a winding/seam control, not connectivity
alone. Facial hair roots must be tested against the actual skin surface.

The initial builds regenerated all crowd variants before the leader proof had
passed. That contradicted the intended earliest-proof sequence and increased
local rework; it did not qualify their reuse. The internal gate did reject the
visible failures rather than requesting another Director micro-review.

The preservation test initially classified the deliberately replaced leader
flag and spear materials as out-of-scope scene changes. The corrected test
declares those equipment changes explicitly, while separately protecting spear
geometry/action and all actor root controls. This is a scope correction, not a
waiver of the independent cuff failure.

Builds01–06 retained native/render/log evidence and input hashes, but did not
retain complete per-version source snapshots before the working authoring code
was changed. Do not claim exact recipe replay for those versions. From07 onward,
dispatch retains bound Python/Markdown source snapshots. Native save, reopen,
visual inspection and complete AV acceptance remain separate findings.

## Unused donor rights discrepancy

The local Rehman Polanski beard_viking and moustache_viking `.mhclo` files say
CC0, while both corresponding OBJ headers say AGPL3. The earlier262 statement
that this pair was consistently labelled is insufficient for these actual
files. Neither donor was imported into319. This is a source-rights discrepancy,
not a legal conclusion about output rights or a reason to stop the independent
construction route. Clarify exact source rights before later reuse.

## Corrective tests

Whole-form test precedes texture counts or copying crowd variants. Evaluate the
complete face/beard/crown/shoulders under neutral and actual torch lighting.
Compare the accepted Pashtun's integrated material and form hierarchy, accounting
for different shot scale; do not lower that floor to match current proxies.

Use the donor surface for eyebrow and facial detail fitting. A contact point
or inherited controller is not a visible grip. Verify closed fingers, opposing
thumb, wrist/cuff and weapon together. The donor-derived garment has fixed
topology and follows the existing baked arm endpoints. Inspect
crest, landing and partial poses for shoulder distortion, not only the neutral
rest frame. Crowd variants must differ beyond colour and scale.

Direct motion and sound are not reviewed by the agent. Their flags remain false
under Director313; technical and timed-frame checks must not be relabeled as
playback or artistic acceptance.

## Full-render chronological inspection in progress

Candidate19 full render is frozen. Frames1–72 were inspected in
`progress-review-078/chronology-01..03.jpg`; frames73–192 were inspected in
`progress-review-200/chronology-04..08.jpg`. These are actual consecutive source
frames, not interpolated previews. The protected approach, camera transitions
and motorcycle stop show no newly observed missing objects or disconnected
interfaces at this review scale. The principal remains an explicit proxy.
This does not close playback timing or sound judgments, and does not yet
constitute review of the later supporting-cast/action section.

`progress-review-378/chronology-09..15.jpg` extends inspection through frame360.
Full-size movie frames283 and333 were additionally examined. The new beard,
crown, neck and garment remain connected through the rear; the spear hand/cuff
does not show the earlier sampled-bake separation. The dark horse and its timing
are inherited318, not newly qualified by319. The small rein line is low contrast
in the rest view; this remains a readability limitation, not a new claim of
hero close-up rein/contact fidelity. Full-speed naturalness remains pending.

`progress-review-536/chronology-16..22.jpg` extends inspection through frame528.
Near crowd retains continuous neck/shoulder/cuff forms, weapons follow the
holding hands, and differentiated heads turn toward departure without the
earlier unbridged neck seam. Faces are still supporting-shot detail, not
principal close-up assets. Boot contact and shared root controls are unchanged;
walk naturalness is not established by these stills. Existing departure dust,
terrain, motorcycle and principal proxy remain inherited, not re-qualified.
The26 selected319/317 routing, safety and construction regression tests pass.

## Completed review package

`delivery-19/chronology/chronology-23..29.jpg` completes chronological inspection
through frame696. All26 decoded encoded controls were inspected in four
`encoded-review` contact sheets. No new supporting-cast disconnect was observed;
this is not a playback naturalness judgment. Exact joined frame479 is the final
accepted Pashtun frame;480 is the first Sikh frame. Both were inspected directly.
Earlier timestamp-based boundary captures rounded onto the Sikh side and were
not used as proof of the preceding Pashtun frame. They remain diagnostic history.

Delivery preparation initially failed the narration/accepted-unit binding gate.
The task was corrected to bind the actual accepted Pashtun artifact and current
authority; a fresh delivery packet was generated and its additional obligations
reviewed. No narration was regenerated or changed. Both complete clips decode
cleanly, preserving318 audio and the exact accepted Pashtun source/pre-AAC PCM.

Fresh-open comparison remains strict FAIL: three of six controls exceed the
unchanged1/255 threshold, with maxima3/2/2 at80/283/380. The other three have
maximum1. This is separate from the earlier318 strict failure and from Director
AV acceptance. No threshold was relaxed. Native recovery succeeded.

The deliverable is the explicit313 manual AV review candidate, not a universal
rig/actor qualification or a production pass. Principal Sikh remains a proxy.
