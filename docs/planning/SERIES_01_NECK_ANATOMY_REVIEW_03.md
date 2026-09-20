# Neck, throat and shoulder continuation

**Subsequent Director feedback:** 15 is very close, with a remaining small posterior-neck bump. See [localized correction 04](SERIES_01_NECK_ANATOMY_REVIEW_04.md) for current candidate 16. This report retains the historical 15 assessment and evidence; it is not Director approval.

2026-09-20. Director rejected candidate 07: residual swelling where the neck spreads into the shoulders, with inadequate throat/collarbone definition. Earlier positive assistant assessments are not acceptance. Geometry-only continuation; accepted face/jaw, shortened proportions, textures, hair and costume remain protected. Planning exchange counter stays 119.

Activity `neck-anatomy-3`: forecast 35 minutes / 120 MB; reassess at 20 minutes, three variants per hypothesis and 60 minutes overall. No paid calls, purchases, new assets, uploads or remote push. Engineering model/effort/token totals are unknown. The local operating ledger records actual native jobs and activity/wait boundaries.

## Diagnosis and iteration

The previous lower extension was a radial neck-to-ellipse loft. Its broad conical silhouette and weak anterior landmarks could be smooth without looking anatomically convincing. A nondecreasing radius alone is not an anatomical acceptance test.

- **08, rejected internally:** separate lateral shoulder profile, anterior/posterior depths and rounded chest section improve the shoulder outline. Restored SCM/clavicle relief is too sharp; crossfading from the fitted neck produces a new posterior-oblique ridge. Preserved evidence, not a successful repair.
- **09:** replaces that crossfade with endpoint-value/slope-matched joining and reduces relief strength. The circumferential ridge is absent in soft-light views, but tiny cut-ring triangles leave visible bright blemishes.
- **10:** redistributes vertices locally on the same intended surface around the old cut. Small blemishes disappear. Existing topology/UV arrays are retained; local Z redistribution is at most 0.025, not a neck-length change. Overall vertical extent and all 16,952 protected face vertices are unchanged. Eight directional-light views reveal fine anterior rippling not obvious in the soft-light renders; do not finalize on soft lighting alone.
- **11:** a separate surface-quality correction regularizes lower-neck angular sampling and filters noise in the sampled joining slopes. Anatomical relief is applied separately, so this does not smooth away the deliberate collarbones/SCM. Directional lighting is improved but exposes residual coarse surface sampling near the tendons.
- **12, failed execution:** attempted local lower-neck subdivision; Blender invalidated vertex wrappers when temporary data layers were added. Failed before native output was saved. Preserve the job failure record and empty output directory.
- **13–14, failed execution:** subsequent wrapper-identity/equality assertions could not establish old vertex ordering through the native operation. Neither saved a native output. Do not describe these as geometry successes. Reassessment: vertex order is not the requested facial protection contract; exact facial coordinates, connectivity and UVs are.
- **15, preferred internal review:** local subdivision followed by projection onto the intended surface removes coarse throat rippling without flattening the landmarks. Only edges with both endpoints below z=-0.90 are subdivided; 26,790 vertices added. Source-height data is carried through native interpolation for the height guard. Face protection is now exact and index-independent: all 16,952 facial vertices and the per-face position/UV digest must equal the immutable source. Original face connectivity is therefore protected too. Vertex ordering is not retained; this is not a vertex-ID-compatible replacement for an existing facial rig. The retained original FBHead remains unchanged.

Three-variant reassessment after 08–10: broad form is substantially improved; remaining defect is local surface sampling/shading rather than a reason to keep changing the neck proportions. Continue with that narrower hypothesis. No additional creative direction or new asset needed.

Approximately 20-minute reassessment: retain the corrected anatomy and finish the local surface-quality test plus fresh reopen; no additional shape variants planned. Forecast storage increases from 120 MB to 170 MB to retain all rejected candidates and directional-light evidence. Time forecast remains 35 minutes. This is an internal process forecast, not paid spending authority.

All paths are beneath `.runtime/art-direction/series01-facebuilder-trial-01/`. Candidate folders contain the native `.blend`, actual neutral-clay renders and JSON evidence. Do not infer rig, motion, full-body or costume-clearance qualification from a static bust review.

Anatomical landmarks were checked against [OpenStax neck muscles](https://openstax.org/books/anatomy-and-physiology-2e/pages/11-3-axial-muscles-of-the-head-neck-and-back) and [pectoral girdle](https://openstax.org/books/anatomy-and-physiology-2e/pages/8-1-the-pectoral-girdle), together with the two approved character portraits. These are modeling references, not an anatomical certification.

## Current result and evidence

**YELLOW, internal static anatomy review ready; Director acceptance pending.** Assistant visual assessment: the current cropped head/neck/shoulder bust is anatomically believable at this stage. Neck-to-shoulder flow, paired collarbones, throat/SCM and central hollow now read as one form. No circumferential swelling or cut-line blemish is apparent in the inspected views. This is not a declaration that the whole future character, full torso, rig or clothing is production-qualified.

- Native: `neck-anatomy-build-15/character-upperbody.blend`, SHA-256 `21c39b7215eddff50520621c7e8cc9184eb08915375617592d02e834caa0ebb6`.
- Five soft-light clay views: `neck-anatomy-build-15/{front,left,right,back,three-quarter}.png`.
- Eight directional-light views and independent fresh-open verification: `neck-anatomy-raking-15/`.
- Native build/reopen JSON confirms exact protected facial surface digest `fd256f12c5d2b7ae09496eab6da8615576a06bfa1abf60253031848d74c21f77`, all other mesh/curve geometry and materials unchanged, original FBHead intact, all eight image files packed.
- Overall upper/lower Z extents unchanged. Local cut-ring redistribution is at most 0.025 model units; this changes sampling, not neck length. Lower-neck new UV corners are interpolated; only facial UV equality is asserted after local subdivision.
- 30,085 inspected lower faces; zero inward radial normals and zero area-below-1e-10 faces. These checks supplement visual review, not replace it.
- Final focused suite: **124 passed**. Local implementation commit `401ebeb`; native handler SHA-256 `4376ffa55b89f7cef283b057d72b2a2db4f391257f4c428ba4454a5cea135777`.

Eight build attempts in this activity: five rendered candidates, three execution failures. Twelve native jobs: nine technical passes, three failures, all reconciled. Two wrapped integration-suite runs; smaller focused checks also occurred. Retained candidate/review folders total **151,889,825 bytes**, within the revised 170 MB forecast. No prior evidence deleted. Generated activity report: `neck-anatomy-03-operating/`.

## Next work and limits

Do not continue geometry micro-variants without a concrete newly observed defect. Keep this anatomy-first review separate from texture quality. Next costume work must recheck scarf/tunic clearance to the changed shoulders, then address skin/cloth presentation; unchanged clothing does not imply newly demonstrated fit. Facial animation, body rig, movement and full-body anatomy remain unqualified. No paid calls, purchases, remote push or native-asset backup occurred here.

Process learning: inspect soft and directional lighting before presenting an anatomy candidate. Separate broad form, landmark relief and mesh sampling. Numerical smoothness and passing source guards cannot establish anatomical quality. Native topology changes need index-independent facial protection and a native integration check; pure Python math tests do not validate Blender's data-layer lifetimes.
