# Whole-bust skin continuity review

2026-09-20. Director accepted anatomy16 and requested skin/texture across the entire bust before returning to clothing, drapes or hair. Geometry frozen. Implementation exchange; planning counter remains119.

## Current result

**Director rejected candidate03's appearance:** chin, jaw, neck and forehead looked airbrushed and lost the illustrated skin detail. The assistant's earlier seam-removal/technical assessment was insufficient. This candidate is historical cleanup evidence, **not an accepted skin baseline**. See the [source-detail continuation](SERIES_01_BUST_SKIN_REVIEW_02.md) for the current review asset. Anatomy16 remains accepted and frozen.

Historical native path under `.runtime/art-direction/series01-facebuilder-trial-01/`: `bust-skin-build-03/character-upperbody.blend`. SHA-256 `13675790d95c399bc236803e3b3aecfb8314d6db5db70848d2ba204a3d7b5b9e`.

- Five matched camera-relative soft-light views: `bust-skin-build-03/{front,left,right,back,three-quarter}.png`. Left/right names denote camera positions; these are ±60° oblique views, not exact profiles.
- Five lighting-independent base-color views: `bust-skin-emission-03/`. These reveal remaining painted facial shading honestly rather than attributing all shadows to light.
- Fresh-open material/protected-state verification: `bust-skin-verify-final-03/result.json`.
- Original anatomy16 SHA-256 remains `76b2a6c7f4f1c2288ed746ebb3cf146b4146650058e263c6dd16b6f9225ef080`.

## Diagnosis and correction

The baseline had a horizontal neck color band, diagonal lower-neck projection boundaries, hair/scarf color painted onto scalp and nape, and overly dark ear surroundings. Clay approval did not resolve these material defects. Baseline lit and emission evidence is preserved in `bust-skin-inspect-00/` and `bust-skin-emission-00/`.

The new copied material retains the original accepted facial color around the central face, eyes and mouth. Smooth spatial masks blend it into a continuous three-dimensional procedural skin base across ears, scalp, nape, throat, clavicles and shoulders. The base samples130 points from an existing calibrated emission cheek region, then slightly reduces red and raises relative blue to reduce the initial orange cast. Subtle color variation avoids a completely flat fill. Roughness0.68, IOR1.4, specular level0.25 and small subsurface contribution replace the earlier IOR1.0 setup. No new bitmap generation, purchased assets or API calls.

Candidate01 is internally rejected for threshold-shaped facial blending edges and orange cast. Candidate02 improves blending but leaves a thin lateral hair-colored streak. Candidate03 insets the spatial transition and clears that streak. All three are retained. This reaches the three-variant checkpoint: proceed to visual review, not more speculative polishing.

The head is intentionally shown without hair/clothes in these diagnostic renders. This is not a bald-character redesign. Those objects are unchanged and retained in the native file; their saved visibility is also unchanged. Native files are saved before temporary review exclusions.

## Verification and boundaries

- Exact visible-bust geometry, connectivity, transforms, UVs and shape state match approved16. New material-mask attributes are the only mesh-data addition. Other mesh/curve geometry, materials and render visibility match the source. Original FBHead remains hidden and unchanged.
- Eight image dependencies remain packed. Native file reopens without running embedded scripts or loading FaceBuilder. Material recipe matches its saved JSON record after JSON normalization.
- 113 focused tests passed across skin, anatomy and related dressing/likeness handlers; this is a scoped suite, not a claim that the complete repository suite ran. The final handler is retested after the serialization fix.
- One verification job failed because in-memory tuples were compared with JSON lists, not because the native material changed. Earlier emission fresh-open records independently match the saved material. Failed output/job evidence is preserved; `verify-final` checks canonical JSON representation and unchanged native hash.
- All five lit and all five emission views were visually inspected. Neck/ear/scalp contamination and the old neck seam are removed in these views. The retained face still contains painted illumination and more illustrative detail than reconstructed skin. No claim of fully de-lit albedo, exact reference complexion under arbitrary lights, photographic pores, expression/rig readiness, or baked GLB portability is made.

## Handoff / process

Review skin before touching clothes/drapes/hair. Preserve approved anatomy and existing portrait likeness. Do not solve a shading concern by re-sculpting the face or neck. If accepted, this native material becomes the basis for later dressing; any exchange bake must be separately verified rather than assuming procedural nodes survive GLB.

Activity `bust-skin-1`: forecast35minutes/120MB; measured assistant activity982seconds (16.4minutes, excluding subsequent review wait), three material variants plus baseline/reopen reviews. Ten wrapped jobs reconciled: eight native jobs including one failed comparison check, plus two passing focused test runs. Retained skin evidence approximately98MB. Engineering model/effort/tokens unknown; no subscription-cost inference. Operating report in `bust-skin-01-operating/`. Implementation commit `f4e429c`; documentation committed separately, local only. Native assets remain ignored and are **not** remotely backed up by Git. No deletion, upload or push.
