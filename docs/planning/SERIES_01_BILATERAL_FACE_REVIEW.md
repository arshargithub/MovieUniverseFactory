# Bilateral face review and right-cheek correction

## Director acceptance — supersedes provisional face status below

After reviewing the matched-light left/right pair, Director said “I think we've nailed this” and instructed work on scarf and hair. `bilateral-04/head-bilateral.blend` is now the approved static facial baseline for this dressing work. Preserve its geometry, enabled shape-key values and material. This accepts the shown facial appearance, not unfinished dressing, full-angle likeness, animation or final illustrated rendering. The historical limitations and prior rejections below remain evidence, not current approval status. Implementation continuation; planning exchange count unchanged.

2026-09-19. Director says the shown left-angle face looks perfect, but the previously shown right remains wrong. Explicit instruction: compare both sides first, protect the liked side, then present left/front/right together. These refer to existing render suffixes (camera at -30/0/+30 degrees), not clinical anatomical left/right or true 90-degree profiles.

## Result

Current review candidate: `.runtime/art-direction/series01-facebuilder-trial-01/bilateral-04/head-bilateral.blend`. Identity approval remains provisional; no assumption of Director approval of the corrected right side or unfinished garment. Current authority is the liked left appearance plus approved portrait pair B. Do not present a single favorable side as completion evidence.

`bilateral-01/` diagnoses textured versus neutral-clay front and both angles under equal mirrored lights; original review lights are restored for final comparison. Clay shows modest geometric asymmetry but not the same strong discrepancy in cheek/jaw shading. The right side's texture has smoother, less distinct cheek-to-jaw transition. This supports material-first correction; it does not prove that every perceived side difference is exclusively texture.

`bilateral-02/` transfers only localized lower/outer-cheek color from the liked left side onto the flagged right through mirrored surface/UV correspondence with a smooth mask. Central face, upper face, original source images, all geometry and existing shape-key values are retained. Mask is zero on the left half. This is material detail transfer, **not** whole-face symmetry or altered bone anatomy. Portrait-derived baked shadows are also transferred, so this is not lighting-independent reconstructed skin.

Protected geometry/primary UV/shape-key/transform digest before and after: `f6a1e3970a74bb325e72a1c0b23c603a34673c225d9b3553b2c8a4a80ea658b6`. Source reconstructed blend SHA-256 remains `c61e0ea06ba7973e416fc2d3cbc78f929d2f491e06286f70292246a2cd1a59fc`. This digest includes the prior provisional cheek key; it must not be confused with original v02 geometry. Mirrored nearest-surface distances in 717 fully weighted sample vertices: mean .0038453, max .0084375 model units; descriptive correspondence metric, not an anatomical symmetry threshold.

Inspected `review-left.png`, `review-front.png`, `review-right.png` together. Right cheek/jaw material definition is improved without new global face slimming. Left-side shader input is unchanged; indirect illumination means pixel identity is not asserted. Garment holes/overlaps and rough shoulder folds persist and were intentionally not hidden or labeled fixed. No downloaded hair mesh is present in these renders; visible scalp hair remains projected texture.

Evidence includes `before-*`, `balanced-before-*`, `clay-*`, `balanced-after-*`, `review-*`, and `result.json`. Final review uses the same prior key/fill setup and framing at all three camera positions; the balanced comparison set uses equal mirrored lights for side diagnosis. No 90-degree profile/all-angle or animation qualification. Added UV/attribute/material nodes are not yet baked into the earlier portable head package.

45 scoped tests pass; native diagnostic and repair both succeeded. Source files preserved, no paid calls, local code/documentation commits only. Planning counter unchanged for this implementation continuation. Next creative review must retain the left/front/right set; no further changes to the liked side without a specific reason and approval.

## Follow-up: nose junction, jaw streak and mottled right cheek

Director judged bilateral-02 better but insufficient: right nose-to-cheek definition remains odd, a strong streak runs from chin along lower jaw, and right skin reads like badly applied makeup compared with the natural left. This is **not approval** of bilateral-02.

Two bounded material variants were rendered. `bilateral-03` widens the continuous right-side donor mask toward the nasal junction and extends it below the jaw into the neck, avoiding the earlier lower-cheek mask boundaries. `bilateral-04` additionally blends a maximum 60% nearby donor skin into a narrow right jaw band, using a separate UV lookup displaced +0.12 in model Z. This is approximate albedo infill, not recovered anatomy or physically de-lit skin. No raster source is overwritten. The central left half is protected; no geometry or shape-key values are changed. The source SHA and geometry digest above remain unchanged.

Inspected all three review views and balanced/clay diagnostics. The nasal blend is cleaner and jaw streak softened, but the difference is modest; residual jaw shading and painted-in tonal variation remain. Do not report the three complaints fully resolved or the character accepted. Do not keep widening repair masks indefinitely or reshape the liked left side to chase baked lighting. A substantially cleaner base color would be a different material-authoring step, to scope explicitly if this candidate remains insufficient.

The final review retains the original fixed key/fill setup, framing and exposure. Equal mirrored-light images are separate diagnostics, not substituted for the prior comparison. Left/front/right are ±30° three-quarter views, not true side profiles. Scarf defects remain visible and out of this face-only correction. Current material additions are not yet in the earlier portable GLB.

Both native jobs succeeded (about 33 seconds Blender elapsed each, not total engineering time). Latest scoped suite: 42 passed across bilateral, cleanup, scarf and hair handlers. No paid API calls; prior candidates preserved. Implementation and documentation committed separately locally, no remote push or native-asset backup. Planning counter remains unchanged.

## Camera-relative lighting comparison (no character changes)

At Director request, `matched-light-01/left.png` and `right.png` render the unchanged bilateral-04 candidate at -30/+30 degrees with the same camera-relative illumination. Two equal 300 W, size-5 area lights rotate with the camera around the same target; uniform world illumination, exposure, framing and material are shared. Both images use 768×960, 32 samples and a fixed seed. This is distinct from the earlier world-fixed balanced-light diagnosis. Scene lights are controlled, not eliminated: geometry and garment occlusion plus baked texture shading still affect appearance. The matched images still show tonal/detail differences; no claim of pure lighting causation or side equivalence.

Source SHA-256 `c263b6b715548e8fee58661eadd6f26f8b37c81295ae0fcc2c830a3786561322` and protected geometry digest verified unchanged. No material edits or source-scene save. `result.json` records camera/light positions. Six render-handler unit tests pass; native render succeeded in approximately 10 seconds. Both views visually inspected. No new creative approval, paid calls or remote push.
