# Residual posterior-neck contour correction

2026-09-20. Director: candidate 15 is **very close**, but a small neck bump remains above the shoulders in three-quarter and back views. This is a localized revision request, not approval or rejection of the entire bust. Planning counter remains 119.

Activity `neck-anatomy-4`: forecast 20 minutes / 70 MB, three variants maximum before reassessment. One native geometry variant used; no purchases, paid provider calls, new assets, texture/clothing edits, uploads or remote pushes. Model, effort and engineering tokens unknown.

## Result

**16's static anatomy is Director accepted.** Subsequent Director response: “ok great, I think this looks good,” followed by explicit direction to resolve the whole bust's skin/texture before clothes/drapes and hair. The approved geometry is now frozen for the [skin-only pass](SERIES_01_BUST_SKIN_REVIEW.md); this does not approve its old material or costume. A compact posterior radial correction reduces the residual swell without rebuilding the improved shoulders or anterior anatomy. Five soft-light views and rear/front three-quarter, back and front directional views inspected. No universal anatomical or rig qualification is claimed.

- Native: `.runtime/art-direction/series01-facebuilder-trial-01/posterior-neck-build-16/character-upperbody.blend`.
- SHA-256: `76b2a6c7f4f1c2288ed746ebb3cf146b4146650058e263c6dd16b6f9225ef080`.
- Soft-light front/left/right/back/three-quarter PNGs alongside it. Eight directional views and fresh-open results in `posterior-neck-raking-16/`.
- Input is immutable anatomy 15, SHA-256 `21c39b7215eddff50520621c7e8cc9184eb08915375617592d02e834caa0ebb6`.
- Edit corridor: posterior neck z=-0.50..-1.45, y>0.02, rear cosine>-0.12, smoothly fading to zero at boundaries. Maximum displacement 0.045 model units. This deliberately includes nape above the old z=-0.86 horizontal guard, **not the anterior face/jaw**. Do not reuse the earlier whole-horizontal-plane digest as a claimed invariant.
- Exact protected-state checks: 37,456 vertices outside the patch unchanged; all vertex Z coordinates, complete topology, all UVs, materials and other mesh/curve objects unchanged. Original FBHead retained unchanged; eight images remain packed. 9,408 vertices move more than 1e-8 units.
- Fresh reopen passes; no inward radial lower-neck faces or near-zero-area lower faces. **133 focused tests pass.** A preliminary unit check caught insufficient anterior exclusion; an explicit y-plane falloff was added before any native execution. Both native jobs passed.
- Implementation commit `0593dc5`; retained new build/review folders total 33,338,223 bytes, within forecast.

This does not authorize new face sculpting or flattening the collarbones. Preserve 15 and earlier evidence. Next costume work still needs to check garment clearance against the revised skin surface. Local implementation and documentation commits are separate; native files remain local, not remotely backed up by Git. Operating report: `posterior-neck-04-operating/` beneath the trial directory.
