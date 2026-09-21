# Hair transitions and neck/clavicle definition

2026-09-21, exchange124. Director rejects dressing-fit04's wig-like hair, particularly above/around the ears and between temple and cheek. Hair is too groomed and possibly too short against the approved pair-B illustrations. Director also requests stronger neck/collarbone definition, authorizing diagnosis at both texture and model level. Prior facial identity, face proportions, skin character and restrained acting amplitude remain accepted; this is not permission to redesign the face.

## Review contract before presenting to Director

Use the actual selected native file, not historical renders. Hide all clothing, scarf, hood, straps and retained donors; show only bust, eyes and current hair. Inspect front, both45-degree three-quarter views and back. Separately inspect the same lower-neck anatomy in clay without painted shading or hair. Review both source illustrations at each selected comparison.

Reject obvious scalp gaps, cap-like hard margins, disconnected roots, floating hair bundles, mirrored/combed repetition, short outward ear-level tails, temple/ear occlusion mistakes and front-only successes. The back is an inferred continuation because the approved portraits do not specify it; do not claim an exact unseen reference match. Maintain some visible ear anatomy and natural tapered hair at the temples rather than concealing the entire area with a solid slab.

For anatomy, retain neck length and the accepted posterior silhouette/no-bulge correction. Check the suprasternal notch, paired neck-muscle transitions and clavicle course in clay and textured views; no new hard ring, central hump or painted contour stripe. If localized geometry relief is needed, apply the same displacement to all shape-key bases so existing expression deltas remain intact. Protect the entire face/jaw and unchanged upper-neck area; verify UV/material preservation. Texture edits are not required if geometry and existing material suffice.

## Scope and operating record

Pinned source `dressing-motion-build-04/character-dressed.blend`, SHA-256 `77fa1fad9da232a6af156f0f62b1a3fd994f4aa28e89011643ea74574e77526e`, under `.runtime/art-direction/series01-facebuilder-trial-01/`. Prior sources/failures retained. Activity `hair-anatomy6` in the open FaceBuilder episode, forecast45minutes/180MB/three candidate variants,20-minute diagnosis and60-minute overall reassessment. Serial preview jobs, no paid calls or new external assets. Engineering model/effort/token usage remain unknown. No new performance direction or full rig/dynamics qualification.

Status: **YELLOW, candidate10 for Director comparison; not final hair/style approval.** Dressing04 is Director-rejected for hair, not an approved baseline. No overall release gate advancement. This review tightens the earlier inadequate central-face-only numerical check: that metric did not validate hairline aesthetics or temple/ear integration.

## Diagnosis and implemented result

The wig impression was not simply missing sideburns. The old asset combined a separately painted crown with disconnected short side bundles, exposed temple/rear scalp and blue scarf pixels in the crown projection. The topmost-hit root projection also started new locks behind the actual frontal hairline. More fibers or a color adjustment alone could not repair these disconnected layers.

Candidate10 replaces that structure with continuous scalp support, longer irregularly layered locks, actual frontal/temporal/occipital flow and fine tapered roots. Hair reaches past the truncated bust's shoulders; its back is an inferred loose continuation, not an approved or reference-observed haircut. A darker low-specular, broken-stroke treatment reduces the brushed-fiber appearance. The narrow original painted hair underlay is retained beneath the physical fringe; it is not painted onto accepted skin. Ears were not resculpted: their existing simplified fidelity remains a limitation, not something hair coverage qualifies.

Neck/clavicle definition required **localized geometry relief**, not new painted contour stripes. Added modest anterior neck-muscle relief, clavicle definition and central notch shaping. Only15,366 vertices in the bounded anterior lower-neck/upper-chest region move, at most0.04022013 model units. Neck height/length, face/jaw and posterior no-bulge silhouette remain protected. The same offset is applied to all20 shape-key blocks, including Basis, so original expression deltas are preserved. Original skin materials, UVs and stable texture coordinates are unchanged.

## Actual evidence and preserved failures

All paths below are under `.runtime/art-direction/series01-facebuilder-trial-01/`.

| Evidence | Disposition |
|---|---|
| `hair-anatomy-inspect-00/` | Clothing-free baseline and clay diagnosis of Director-rejected dressing04 |
| `hair-anatomy-build-01/` through03 | Internally rejected: hard cap/temple streaks, then protruding rectangular backing |
| build04–05 | Corrected backing, added temple/rear coverage; still separate painted crown and overly fine regular strands |
| `hair-anatomy-look-05/` through07 | Three render-only material diagnostics; no saved native changes. Color/strand reduction insufficient; replacing crown color alone produces an unacceptable flat cap |
| build06–07 | Actual frontal volume and continued rear part; close-ups still expose a painted strip beneath the frontal guides |
| build08 | Failed safely before native save: frontal ray misses scalp at an edge; directory/job failure preserved |
| build09 | Distance-guarded nearest-surface fallback and front-surface root placement; improved continuity but blunt lock roots |
| **build10** | Current comparison candidate: softened lock root/edge density; same accepted face and bounded neck revision |

Selected native: **`hair-anatomy-build-10/character-hair-anatomy.blend`**, SHA-256 **`3158f62b8eba1ce3c8244e8ba00773efceb3fc2892e8d4902f529a82dc8db8b0`**. It retains the historical clothing and donors, not a clean redistribution bundle. The native is saved before review visibility changes; the clothing-free inspection PNGs are not evidence that clothing was deleted. There is no new keyed motion clip.

Current views: build10's `front.png`, `left.png`, `right.png`, `back.png`; left/right mean camera ±45degrees, not exact profiles. Gallery labels use nose direction to avoid viewer-versus-character left/right ambiguity. Matched camera-relative lighting removes the prior side-lighting confound. Four `clay-*.png` views remove both hair and skin shading. Fresh-open views plus both55-degree temple close-ups and blink/smile/modest-jaw frames are in `hair-anatomy-verify-10/`. Earlier verification05/07 is historical, not substituted for10.

## Review limits and next work

This is a materially improved **working hair/anatomy comparison**, not a claim that illustrated-C hair is finished. The crown remains more uniformly striated than the original painterly locks; root/part refinement and pointed lower lock ends remain stylistic risks. Back-view arrangement has no source illustration authority. Do not label this photo-real hair, a production groom, or Director-approved likeness/style merely because numerical preservation passes.

Static clothing-free checks cannot qualify hood clearance with the longer hair, scalp/ear intersections at every angle, wind, hair dynamics, head/neck turns, gallop or whole-character rigging. Clothing/hair integration must be rechecked before dressed motion; preserve the selected isolated review first. Existing plain closed-lid detail/basic mouth lining are unchanged documented facial-proof limitations. No new speech, stronger expression or facial-identity work is authorized by this pass.

## Reusable process improvements

1. Inspect undressed front/back/both three-quarter views plus tight bilateral temple crops **before** calling a hair result ready for Director review. One attractive angle or a face-clearance metric is insufficient.
2. Diagnose root placement, support-surface joins and direction of flow before increasing strand count. Material changes cannot fix disconnected hair volume; front scalp and topmost scalp ray intersections are different.
3. Separate anatomy from material with clay; keep definition in geometry when shape is the cause. Protect posterior repairs and apply coordinated shape-key offsets.
4. Use render-only material studies before writing another large native file. This pass still exceeded its initial three-variant/storage forecast; diagnosis should be narrower earlier. Record failed attempts and do not count process exit0 as creative success.
5. Stop short of claiming the unobserved back, simplified ears or static groom are qualified. Final artistic acceptance belongs to the Director; technical evidence has narrower scope.

No paid calls, image generation, purchases, new downloads, remote push or asset deletion. Engineering model/effort/token usage and allocated subscription cost remain unknown, not zero. The visualization skill supplies a ten-view comparison containing the four current renders, four clay views and the two original approved portraits; display-only compressed previews do not replace original PNGs.

## Final verification and operating card

- **51 focused unit tests pass.** Fixed structured jobs reject arbitrary paths/operations, changed source pins, symlink sources and existing output directories. No runtime-generated code input.
- Fresh reopen of10 without the add-on: **31,907 protected face/posterior/out-of-region vertices exact**. Original topology, UVs, skin material signatures, rest coordinates and other non-hair objects exact. The intended lower-neck offset matches within2.98e-8 model units in both mesh and every shape-key block.
- All240 samples of the existing restrained facial trajectory remain finite and return exactly to neutral. This is numerical regression evidence plus inspected blink/smile/jaw frames, **not a new motion video or hair-motion qualification**.
- Fresh-open front/back/both three-quarter renders are pixel-identical to the displayed build10 renders. All four clay renders are pixel-identical to the inspected07 clay images: later iterations changed hair only. Both final temple close-ups and all three pose images inspected separately.
- All native file images packed; original dressing04 and selected10 hashes unchanged. Implementation commit **`031c48a`** records the reviewed handler/tests after execution; per-job handler digests remain the actual run provenance, not a retroactive frozen-source claim.
- **17 wrapped native jobs**,16 completed technically and one failed safely; **454.852 native process-seconds**. All native/local job boundaries reconciled. Technical exit status is not artistic acceptance.
- **Ten geometry build attempts / nine retained native candidates, plus three render-only material variants**. This exceeds the initial three-variant forecast. Diagnosed repairs and reassessment are recorded, but they do not turn the miss into a met budget. Source-style join diagnosis should have preceded whole-head polish.
- Evidence **434,292,129 bytes /150 files**, excluding job inputs, gallery and operating exports. Both180MB initial forecast and350MB revised checkpoint were exceeded; no further variants dispatched after final verification. Keep the failures; no retention/deletion authority inferred. Future passes should preview a local patch before saving another whole scene.
- Activity `hair-anatomy6` boundaries, waits and compact pass manifest are in `hair-anatomy-operating/pass-summary.json` and `pass-events.json`; broader experiment report in the same directory retains historical coverage caveats. The FaceBuilder episode stays open. No per-token subscription price or fabricated usage.

Code/test and design commits remain separate and local, with remote design push still due at checkpoint130. Native assets are local SSD evidence and **are not backed up by Git commits**. The unrelated `.DS_Store` is untouched.
