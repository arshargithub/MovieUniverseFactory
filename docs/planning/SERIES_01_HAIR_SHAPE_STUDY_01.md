# Hair shape study — crown and temple volumes

2026-09-21, exchange127. Director authorizes the [shape-first recommendation](SERIES_01_ILLUSTRATED_HAIR_SECTION_01.md) after four earlier section previews failed. This authorizes a construction-method change, not a different character or approved appearance.

## Reference and protection contract

Appearance authority remains approved pair B: [frontal](../../.runtime/art-direction/series01-pashtun-baseline-v01/frontal-v02-individualized.png) and [three-quarter](../../.runtime/art-direction/series01-pashtun-baseline-v01/portrait-v07-individualized.png). Reinspect both before judging each candidate. The reference qualities are lifted but restrained roots around the center part, broad unequal overlapping waves, coherent sweeps toward/behind the ears, and natural temple framing. No bald spots, flat projecting strips, hooked card ends, repeated tubes or inflated helmet silhouette within the tested area. Fine illustrated detail is deferred until the forms work.

Use solid closed tapered volumes, not open image-textured strips. Neutral/clay views diagnose shape without painted highlights. Clay is not a new art direction, and passing geometry checks is not a likeness/style pass. The unseen back is not specified by the portraits; only supporting scalp volume is included there, not an approved full haircut.

Technical source remains `hair-anatomy-build-10/character-hair-anatomy.blend`, SHA-256 `3158f62b8eba1ce3c8244e8ba00773efceb3fc2892e8d4902f529a82dc8db8b0`. Its hair remains rejected. Do not change face/skin/neck, eyes, UVs, rest attributes or existing expression controls. Temporary clay material overrides must be restored before preservation checks and any native save. Hide clothes in review. Preserve all earlier files.

## Scope and budget

Open `SERIES01-LIKENESS-ASSET / facebuilder-trial-01` episode, activity `hair-sculpt8`. Forecast35 net minutes, three local variants,90MB;20-minute diagnostic and60-minute overall reassessment still apply. No new paid API calls, image generation, external assets, purchases, whole groom, scarf revision, animation or remote push. New handler `hair_volume_sculpt.py` admits fixed pinned-input preview/package jobs only and refuses existing outputs. Source portraits are not uploaded or altered.

Status: **YELLOW — provisional geometry blockout retained, not Director-approved hair and not a complete reference-fidelity pass**. No release-gate advancement. Four final clay angles inspected and protected non-hair state verified on fresh native reopen. Do not treat this as approval to expand a finished look to the whole hairstyle.

## Result and internal reference review

[Native shape study](../../.runtime/art-direction/series01-facebuilder-trial-01/hair-sculpt-package-03/hair-shape-study.blend), SHA-256 `34682c0487bf9057961082fb122e48a4caa8aa3ff083fa412568a27acaca9d21`. [Machine result](../../.runtime/art-direction/series01-facebuilder-trial-01/hair-sculpt-package-03/result.json). This file preserves the accepted skin material on the body and uses neutral gray on the new hair. The all-clay pictures use temporary review-only body/eye overrides, restored before saving. Original source and failed candidates remain intact.

Final views: [front](../../.runtime/art-direction/series01-facebuilder-trial-01/hair-sculpt-package-03/front.png), [three-quarter A](../../.runtime/art-direction/series01-facebuilder-trial-01/hair-sculpt-package-03/left.png), [three-quarter B](../../.runtime/art-direction/series01-facebuilder-trial-01/hair-sculpt-package-03/right.png), [back support](../../.runtime/art-direction/series01-facebuilder-trial-01/hair-sculpt-package-03/back.png). Names A/B avoid confusing anatomical left/right with the viewer's side. Rear support is unfinished scope, not an approved short haircut.

Compared against approved pair B, the new geometry establishes a center-parted crown with broad curved sweeps toward the temples, solid depth and a continuous attachment. Floating strips, outward card ends, jagged support margins and duplicated ear contours are removed in the tested views. **The reference's richness is not yet reproduced:** the crown remains too regular and smooth, the wave hierarchy is simplified, and finer asymmetric overlap/face framing remains open. Do not call it luscious/reference-matched merely because the construction is sound. No illustrated texture detail was added to disguise these remaining shape limitations.

Next bounded geometry work should develop unequal secondary overlapping forms and less uniform root/temple flow against the same two portraits, before illustrated highlights and selective fine strands. Do not reopen the protected face or neck, replace the approved images, infer a back design, start long-hair/scarf dynamics, or claim the original hairstyle is finished. Director review is a shape-direction checkpoint, not production acceptance.

## Preserved attempts and causal correction

1. `hair-sculpt-preview-01`: ten closed lens-section volumes, but raw guide positions float off the scalp; cropped support has stair-step edges. Internally rejected.
2. `hair-sculpt-preview-02`: scalp fitting, smoothed crop boundary and voxel union remove broad gaps. Too uniform; fitting against the entire body introduces upper-ear contours into hair.
3. `hair-sculpt-preview-03`: smooth fitted control curves, reduced relief and center-part valley; ear-contour contamination remains. Internally rejected as the final candidate.
4. `hair-sculpt-repair-03`: one explicitly bounded defect correction after the three-preview checkpoint. A convex scalp fitting proxy excludes ear-region points; the new support and volumes no longer copy the ear. This is a **fourth preview above the initial three-variant forecast**, recorded in the ledger, not hidden as cost-free bookkeeping. Still within time/storage forecast. No additional style sweep.
5. `hair-sculpt-package-03`: same repaired construction rebuilt, four views rendered, native saved and freshly reopened. Retain as a provisional shape blockout only.

The ten authored locks were checked closed before merging. Their18,980 vertices and support become a128,232-vertex working hair mesh after voxel union/smoothing. This is an editable sculpt study, not optimized production topology, a general groom or a rig/dynamics result. Hair object transform/rig attachment and animation clearance require later scoped checks; the existing facial controls themselves are preserved, not newly qualified with this hair.

## Verification and operating evidence

**55 focused tests pass.** Fixed operations reject unsupported/extra job fields, booleans as variant IDs, source symlinks, changed hashes and output overwrites. Both approved portrait hashes are pinned. Source geometry, topology, UVs, materials, object transforms, shape-key coordinates/values and rest-vector attributes are protected through the existing non-hair signature; temporary material overrides are restored. Fresh reopen preservation passes. No original native or approved image overwritten. No motion or collision qualification claimed.

Handler `src/movie_factory/adapters/blender/hair_volume_sculpt.py`, SHA-256 `357c8512608765dc8a7238b4e79e7601a8596349c4d33ce1b7ebd0a64973860f`. [Compact operating card](../../.runtime/art-direction/series01-facebuilder-trial-01/hair-sculpt-operating/pass-summary.json) records captured activity time, reconciled job duration, bytes and final disposition; [pass events](../../.runtime/art-direction/series01-facebuilder-trial-01/hair-sculpt-operating/pass-events.json) preserve source observations. Five native jobs including packaging, not five artistic variants. No paid API calls or purchases; engineering model/effort/tokens/cost unknown.

The six-image comparison uses the visualization skill: both original approved references and four clay angles, with explicit approved/unapproved labels. Display-only JPEG previews leave the originals unchanged. Its selector and previous/next actions were browser-checked; the temporary localhost server was stopped. Native/renders remain local SSD artifacts, not Git-backed or newly backed up off-device. Separate local implementation/design commits; no remote push this exchange. Next scheduled checkpoint remains130; overall accepted gates remain1/25.
