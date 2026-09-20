# Source-derived illustrated skin continuation

2026-09-20. Director rejected the smooth `bust-skin-build-03` appearance and explicitly requested extension of the earlier cheek/face texture character across the entire bust before clothing or hair. This is a material-only implementation continuation; planning exchange remains119. Anatomy16 is accepted and immutable.

## Current review pointer

**Director rejected detail07:** the replacement still reads as a weird pattern, the cheek-to-ear transition is distinct, and dark brow/temple remnants include a scar-like line on the viewer-left side. Do not promote this to a preferred or accepted whole-bust material. The [regional follow-up](SERIES_01_BUST_SKIN_REVIEW_03.md) retains a local temple cleanup but does not resolve the global texture. All historical paths below are under `.runtime/art-direction/series01-facebuilder-trial-01/` on the SSD.

- Native SHA-256: `c591b45c6f666597498d418ebd90fa37010f37d9a7bccc2597508f2c96a23688`.
- Larger 960×1200, 48-sample front/left/right/back/three-quarter views: `bust-detail-portraits-07/`. Its `setup.png` is a separate 640×800 setup image, not a high-resolution final.
- Five standard 640×800, 24-sample views: `bust-detail-build-07/`.
- Five base-color emission views and independent fresh-open check: `bust-detail-emission-07/`.
- Original anatomy16 SHA: `76b2a6c7f4f1c2288ed746ebb3cf146b4146650058e263c6dd16b6f9225ef080`.

Left/right camera views are ±60°, not exact profiles. The three-quarter view is -35°. Two equal camera-relative softboxes, framing and color management remain fixed within the review. Hair/clothes are only hidden for rendering; their saved geometry, materials and visibility are untouched. This is not a bald-character design choice.

## What changed

The earlier pass preserved only central facial texture and substituted averaged color plus low-amplitude noise elsewhere. It solved continuity at the expense of art direction. **No-seam appearance and invariant tests are not enough to establish a correct skin material.**

This pass starts again from anatomy16, not the rejected smooth derivative. The original accepted bilateral facial material chain is retained before the old lower-neck projection/tint repairs. The central face, chin and jaw retain source detail; controlled perimeter masks exclude painted hair and transition to the transferred skin. The uppermost forehead/temple edge is a reconstructed texture transition, not pixel-identical accepted material. Original surface-response defaults are retained rather than changing specular/roughness at the same time.

The exposed scalp, ears, nape, neck and shoulders now receive **actual marks from the embedded approved frontal portrait**, sampled from a clean forehead region. Overlapping randomly rotated planar patches are blended across three projection directions. Donor median normalization controls broad complexion; a1.7 contrast gain compensates overlap losses. These are native texture-coordinate/material operations; no source bitmap is edited, no generative image/API call occurs, and no new image dependency is introduced.

Original facial illumination remains partly painted into the texture, including the under-chin shadow. Do not describe this as fully de-lit skin or erase all facial variation in pursuit of lighting purity. Material-space coordinates are a static prototype: bake/UV verification is required before animation or interchange to avoid deformation-related texture swimming. No GLB/baked-albedo portability, final illustrated renderer, dynamic lighting, facial rig or expression qualification is claimed.

## Iterations and checkpoints

All evidence is preserved; no native input overwritten.

1. `bust-detail-build-01`: restored face detail but included painted hair and repeated a donor-cheek dark mark.
2. `02`: shade-normalized the donor; repetition remained.
3. `03`: cleaner forehead donor, but mirrored mapping still created a visible repeating motif. Three-variant checkpoint: change mapping hypothesis, not blur the marks away.
4. `04`: continuous noise coordinates removed the grid but curved the marks into wood grain; internally rejected.
5. `05`: overlapping randomly rotated patches removed the motif/distortion, but broad overlap suppressed visible detail.
6. `06`: narrower overlap and2.6 contrast compensation made marks too prominent. Larger renders retained in `bust-detail-portraits-06/`.
7. `07`: same mapping as06, contrast reduced to1.7. This final amplitude-only calibration follows the second reassessment; no further variant planned before Director review.

A diagnostic on same-size lit front PNGs measured standard deviation of mean-RGB residual after a3px Gaussian blur: source cheek0.01021, source forehead0.00818,05 neck0.00349,06 neck0.01072,07 neck0.00665 (RGB normalized0–1). Sample boxes `(x0,y0,x1,y1)` are cheek `(235,286,277,337)`, forehead `(294,188,345,212)`, neck `(290,455,350,495)`. These are descriptive local-contrast checks, **not a style-match or acceptance metric**; they cannot assess mark shape, anatomy or repetition. Actual render inspection remains essential.

## Protection and evidence

- Native builds and independent fresh opens assert exact geometry/connectivity/transform/UV/shape-state equality to approved16; material-mask attributes are deliberately permitted additions. Every other mesh/curve object's geometry/material/render visibility is protected. Original FaceBuilder head is retained untouched.
- Native file hash and JSON-normalized material recipe are checked on reopen. All eight image dependencies remain packed. No embedded scripts or FaceBuilder execution is required.
- 124 focused tests pass across the new skin handler and related likeness/anatomy/dressing handlers. These do not claim creative approval or full repository qualification.
- Seven builds are appearance candidates, not seven successful creative outcomes. Internal rejects and the Director rejection of the previous pass are retained explicitly.

## Next decision and process learning

Review whether the reconstructed areas now belong to the same illustrated skin language as the earlier face, with appropriate—not identical—regional texture strength.07 is an internal preference, not a Director-approved replacement. Clothes/drapes/hair remain on hold until skin review is settled. Preserve accepted anatomy and the original portrait pair.

Future material reviews must compare against the approved source early, at useful image scale. Test texture mark shape, density and contrast separately from seam removal. Mirrored patches and noise-coordinate warps may pass technical checks while visibly failing style; do not call them complete. Reusing donor detail needs de-repetition and contrast calibration, not just average-color matching.

Activity `bust-skin-2`: forecast35minutes; measured assistant activity approximately1205seconds (20.1minutes), excluding subsequent Director wait. Twelve wrapped jobs reconcile: ten native jobs and two passing124-test runs. All completed successfully as executions; visual rejects remain rejects. Retained evidence227,676,672bytes, within the revised280MB forecast (initial150MB, raised as failed visual candidates were retained). All five larger lit and all five emission views inspected. At the20-minute checkpoint, work is ready for Director review rather than further variants. Local operating report: `bust-skin-02-operating/`. Implementation commit `d508960`; documentation committed separately. Engineering model/effort/tokens unknown. No paid calls, purchases, asset downloads, deletion, upload or remote push. Native files are ignored and not remotely backed up by Git.
