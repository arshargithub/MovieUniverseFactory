# Pashtun head: cleaned static asset handoff

2026-09-19. Implementation result, not a new creative specification or approval. Planning exchange remains 119. Original portrait pair B and provisional v02 facial acceptance remain authoritative.

## Disposition

**Latest dressing checkpoint (September 20 UTC):** [costume refinement 02](SERIES_01_COSTUME_REFINEMENT_02.md); preferred internal review file `upperbody-package-28/character-upperbody.blend` under the trial directory, with final front/left/right three-quarter renders in `upperbody-portraits-28/`. `upperbody-detail-26/` is earlier close-up evidence before the strap correction and final neck-tint guard; use 28 for final appearance. `upperbody-shoulders-27/` inspects the unchanged final harness geometry from side/back. YELLOW static review candidate: refined neck/clavicle junction, buried hair roots/lock volume, softer layered scarf and sleeve-fitted shoulder harness. Original accepted head is retained hidden; visible evaluated face positions/UVs are protected. This is not an approved costume, replacement canonical head, expression rig, 360-degree asset or clean redistribution bundle. The [first upper-body pass](SERIES_01_UPPERBODY_REFINEMENT.md), [sustained dressing pass](SERIES_01_SUSTAINED_DRESSING.md) and [free donor audit](SERIES_01_HIJAB_DONOR_RESULT.md) remain provenance; `reference-dress-18/dressed.blend` is the immutable input.

**Latest approved face pointer:** subsequent Director-requested right-side corrections are in `bilateral-04/head-bilateral.blend` under the same trial directory; see [bilateral review](SERIES_01_BILATERAL_FACE_REVIEW.md). Director approved the static face after matched-light comparison. Scarf/hair are not approved; [renewal results and sourcing dependency](SERIES_01_DRESSING_RENEWAL.md) record three rejected candidates. The approved face is not yet rebaked into the portable package below. The older portable head remains a reproducible baseline, not the latest appearance.

**YELLOW, technically portable cleaned static head.** Stop local face-refitting/ear micro-variants here. The accepted shape has been preserved and the localized material repairs are carried into an ordinary texture. This does not close A5/E1 or qualify a dressed, animated character. The cleaned derivative has not received separate Director approval.

All files below are relative to `.runtime/art-direction/series01-facebuilder-trial-01/cleanup-portable-01/` on the project SSD:

| File | Role |
| --- | --- |
| `head-procedural.blend` | Editable cleanup shader source; head geometry unchanged |
| `head-baked.blend` | Recommended native starting asset, packed 2048×2048 cleaned base color |
| `head-cleaned.glb` + `material-sidecar.json` | Exchange unit; restore sidecar Principled defaults after Blender import |
| `cleaned-base-color.png` | Baked color, not lighting-free recovered skin; original painted shadows remain |
| `head-roundtrip.blend` | Empty factory-scene GLB import with material defaults restored |
| `procedural-*`, `baked-*`, `roundtrip-*.png` | Matched front and ±30° renders, three of each |
| `result.json`, `verification.json` | Source/geometry checks, render comparisons, 17-file SHA-256 manifest |

Package size before verification record: 28,729,030 bytes. Native assets are ignored by Git and are **not backed up remotely by code/documentation commits**. No deletion of earlier evidence, upload or remote push was performed.

## Evidence

One bake/export/import execution, about 25 seconds Blender-reported elapsed; not total engineering effort. 22 handler unit tests pass. Trusted handler operation `portable_cleanup` takes only a fresh `cleanup-` output name and uses the fixed hash-pinned v02 source. Factory startup, autoexec disabled, stripped environment, no FaceBuilder dependency, no provider calls. Blender-side baking is a native material operation, not generated image replacement.

Original geometry/primary-UV/transform/shape-key digest remains `95338f959e8486abbe52759ab79aaf7fe9e8418a00a35512587506794f110bcd`; original file SHA-256 remains `c0e5201fa25490e528396132edff5f45b5f4b803d9487983bca2fde194255e4c`. Additional projection UVs/attributes are derivative implementation details. GLB triangulation and seam splitting are not topology identity.

Procedural → baked RGB MAE (0–255), front/left/right: **0.09744 / 0.09053 / 0.10039**, with maximum channel differences **18 / 18 / 20**. Baked → imported: **0.00343 / 0.00303 / 0.00302**, maximum **2 / 3 / 2**. These are descriptive measurements, not retroactively invented qualification thresholds. All three imported views visually inspected; no gross likeness or cleanup regression observed. Baking is not pixel-exact. This packaging pass uses the existing key/fill review setup, not the earlier equal-light diagnosis; comparisons within this pass use matching settings.

## What the next implementer must preserve

- Keep the v02 source and both approved portraits immutable. Do not symmetrize/re-sculpt the face to solve texture or lighting artifacts.
- Her strength is self-possession, not aggression; natural regal elegance, no makeup/jewelry, modest intentional asymmetry. Illustrated C remains the intended visual language; current Standard/Cycles preview is not that final style.
- Ear detail was mirrored as material only. Smooth neck fill, painted hair/scarf/ear occlusion, unobserved rear scalp, and baked portrait shadows remain provisional. Do not use this as a finished 360° close-up head.
- No blink/eye construction, expression, facial rig, body, horse integration or animation qualification has occurred.
- Separate design and implementation commits; checkpoint-only remote design pushes. No paid calls without the persistent provider ledger.

## Next bounded production step (existing plan, not started)

Update: [static dressing attempt and eye assessment](SERIES_01_HEAD_DRESSING_RESULT.md) now records three rejected dressing blockouts and the missing eye/blink prerequisites. Dressing is not accepted or complete; the cleaned-head starting asset remains unchanged.

Construct separate hair/headscarf matching the approved portraits and inspect the dressed head at intended shot angles in illustrated-C treatment. Inspect eye construction and blink needs before animation. Final exposed-skin work follows dressing/shot visibility; do not keep polishing unseen surfaces. Preserve her face and avoid inventing new costume/accessory design without Director review. Body/rig/motion integration remains a later deliverable with the required motion brief.

## Process learning

Repeated local smooth infill removed defects but lost detail and prompted further review. Diagnose geometry versus baked color first; use matched clay/emission/textured views. Where justified, bounded material transfer preserves more reference detail than flat infill. Keep explicit current-file pointers rather than letting a chronology of candidates become the handoff. Bake and verify the actual cleaned derivative: original-base portability alone did not prove the repairs would survive export. Exact historical total usage remains unknown; no token or subscription-cost inference is made.
