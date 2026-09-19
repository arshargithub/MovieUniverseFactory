# Pashtun head — material cleanup and portable-base result

2026-09-19. Implementation continuation; no new creative planning exchange. Approved base: `head-v02-two-view.blend`, provisionally accepted at exchange 119. Illustrated pair B remains identity authority.

## Result

**YELLOW: usable approved facial starting point and verified portable base, not a completed character.**

### Latest working derivative — localized under-ear repair

Director explicitly requested repair of the residual viewer-right jaw/under-ear transition, reopening that bounded correction rather than accepting concealment by future dressing. Three localized material variants were retained as `cleanup-under-ear-01/`, `cleanup-under-ear-02/`, and `cleanup-under-ear-03/`. Variant 01 removed remaining black contamination but left a color boundary; 02 improved coverage but retained a false painted crease. Variant 03 broadens the feather onto the front cheek so that the old portrait silhouette no longer reads as a sharp crease below the ear. Local skin infill uses distance-weighted nearby valid samples; no raster or facial-shape edits.

**Current assistant-selected working file:** `.runtime/art-direction/series01-facebuilder-trial-01/cleanup-under-ear-03/jaw-review.blend`. This supersedes jaw-correction-03 as the working material candidate only, not the Director-approved v02 source or portrait identity authority. Inspected all three `corrected-{front,left,right}.png` renders: the targeted black remnant/sharp boundary is removed; the infilled side remains visibly smoother and less detailed than the illustrated frontal skin. Do not claim final seamless illustrated skin, finished ears/hair, all-angle qualification or new Director likeness approval.

Native execution succeeded; 21 unit tests passed. Protected geometry, primary UVs, transforms and shape keys retain the original digest; source hash is unchanged. Three variants reached the bounded reassessment checkpoint: further texture-detail work belongs to a deliberate final skin pass, not additional unbounded micro-variants. No paid calls or purchases. Existing GLB proof still covers the original base only; this procedural derivative requires material baking/reconstruction for exchange. Earlier chronological findings below describe prior candidates and are retained as evidence, not current-file pointers. Planning counter remains 119 (implementation continuation).

- Reviewed/tested, data-only handler: `src/movie_factory/adapters/blender/likeness_cleanup.py`. Fixed source path and SHA-256; rejects unsupported operations/keys, changed source and existing output folders. Blender ran with factory startup and embedded scripts disabled, stripped environment and no FaceBuilder dependency. No provider calls, purchases or source-image edits.
- Native mesh has 18,024 vertices / 17,978 polygons. Cleanup preserves vertices, face connectivity, UVs, transform and shape keys exactly under the combined digest `95338f959e8486abbe52759ab79aaf7fe9e8418a00a35512587506794f110bcd`. Original blend hash remains `c0e5201fa25490e528396132edff5f45b5f4b803d9487983bca2fde194255e4c`.
- A reversible material mask replaces only the lower neck color, with a transition from normalized height 0.21 to 0.30. Above 0.30 it leaves the original face texture connected unchanged. The first candidate was too pale; second corrects sRGB-to-linear conversion of sampled neck color. Both retained.
- Second candidate removes scarf sliver and lower-neck clothing projections. **Infill is smooth/low-detail and remains provisional.** It does not fix missing side texture up to the ear/jaw, reconstruct ears, or create actual hair/headscarf. Do not call this final illustrated skin.
- Accepted original base exported as embedded-texture GLB and imported into an empty factory-startup scene. One mesh and packed 2048×2048 texture returned. UV splits and triangulation produce 18,097 vertices / 35,954 polygons; identical topology is not claimed.
- Bare exchange formats did not preserve the original Principled IOR: 1.0 became 1.5. The explicit `material-sidecar.json` restores original socket defaults. The verified portable unit is **GLB + material sidecar**, not GLB alone. This IOR reproduces the accepted preview, not a physically accurate skin claim.
- Under identical 512×640 lighting/cameras, source versus restored round-trip RGB mean absolute error (0–255) is front 0.00210, left 0.00176, right 0.00142; maximum channel differences 1, 3, 1. These are three static-view checks, not animation or all-angle equivalence.
- Cleanup's upper 360 image rows differ by RGB MAE 0.00385 / 0.00560 / 0.00843 across those views; rendering/indirect effects are not pixel-exact even with protected geometry and face shader input.

## Local evidence

Root: `.runtime/art-direction/series01-facebuilder-trial-01/cleanup-preview-02/`.

- `neck-material-candidate.blend`: working cleanup derivative, not a replacement for the accepted original.
- `before-{front,left,right}.png`, `after-{front,left,right}.png`: matched comparison.
- `approved-base.glb`, `material-sidecar.json`, `approved-base-roundtrip.blend`, `roundtrip-{front,left,right}.png`: original-base portability evidence.
- `inspection.json`, `result.json`: native audit and protection evidence.
- Earlier `cleanup-preview-01/` remains failed/partial evidence. Original UI-created candidates remain untouched.

**The cleanup shader itself is not baked into the GLB.** It is reusable in the derivative blend; portable cleanup requires baking or reconstructing the documented mask. The GLB round-trip proves the approved original base only.

## Verification / reproducibility

`tests/unit/test_likeness_cleanup.py`: 14 passed. The first sandboxed native launch crashed before work; the permitted native execution succeeded. Final comparison job took about eight seconds in Blender; this is not total engineering time. Historical setup/engineering usage coverage remains incomplete, so total tokens/cost/net effort must not be fabricated.

To reproduce using this trusted repository handler, provide JSON with exactly `operation: neck_material_preview` and a fresh `output_name` beginning `cleanup-`. Source is pinned and cannot be replaced via job data. Invoke Blender with `--background --factory-startup --disable-autoexec --python-exit-code 1 --python src/movie_factory/adapters/blender/likeness_cleanup.py -- /absolute/path/to/job.json`, through the operating-ledger job wrapper with a stripped environment. Do not use a console code string or runtime-generated script. No overwrite/retry in an existing evidence directory.

## Next production work

### Skin-gated jaw continuation

Director explicitly requests confident reversible implementation decisions proceed without repeated micro-approvals. This does not approve arbitrary creative redesigns, spending, publication or destructive changes. No planning-counter increment for this implementation continuation.

Two additional jaw-material variants were run, reaching the three-variant checkpoint for this correction hypothesis. `cleanup-jaw-correction-02/` gates frontal projection by front-facing normals and conservative local warm/lit color tests, preventing the new dark stripe but retaining the original missing-color gap. `cleanup-jaw-correction-03/` additionally fills only near-black pixels in a feathered viewer-right lower-face region using nearby valid skin samples. This is inferred material color, not recovered reference information or an ethnic/skin classifier. Source images and primary UVs were not edited; new shader attributes are derivative-only.

Reviewed final front and angled renders: the original black lower-jaw patch is replaced and the extra stripe is absent; the angled side still has a color/detail transition near the ear and under-jaw. Retain variant 03 as the **assistant-selected working material derivative**, not new Director-approved likeness or final skin. Do not produce further micro-variants on this hypothesis without reassessing the next production need. Full facial geometry, primary UV, transforms and shape-key digest remain equal to the accepted base. The authoritative v02 source is untouched.

Working file: `.runtime/art-direction/series01-facebuilder-trial-01/cleanup-jaw-correction-03/jaw-review.blend`; matching `corrected-front.png`, `corrected-left.png`, `corrected-right.png`, and `result.json`. Unit suite: 21 passed; native job exited successfully. Portable GLB checks from the earlier result remain checks of the original base, **not this procedural derivative**. Material baking/transfer, ears, true hair/scarf and final illustrated rendering remain open. No paid calls or purchases.

### Jaw diagnosis and localized correction test

Director flagged excessive apparent left/right jaw difference, texture mismatch and dark areas on viewer-right; authorized neutral diagnosis and texture-first correction. New operations `jaw_diagnostic` and `jaw_projection_preview` remain pinned to the original source and reject arbitrary data/code. Unit suite: 15 passed. This execution does not constitute a new accepted creative direction or increment the planning counter.

Evidence: `.runtime/art-direction/series01-facebuilder-trial-01/cleanup-jaw-diagnostic-01/` and `cleanup-jaw-correction-01/`. Each contains equal-mirrored-light textured, emission-only textured, and neutral-clay front/±30-degree renders. Geometry/primary-UV/shape-key digest is unchanged; original file remains unchanged. Emission-only views retain the dark viewer-right jaw/ear patch and side-to-side painted difference, so those features cannot be attributed solely to scene lights. Neutral clay shows modest natural asymmetry; there is no demonstrated need to modify the accepted jaw shape yet.

One localized lower-side-face shader correction reprojects the approved frontal portrait through its fitted camera, adding a separate UV layer and weight attribute (primary UV unchanged). Front-view transitions soften, but a dark stripe/contamination appears at the side/under-jaw in the angled view. **Do not promote this candidate** or use the better frontal image alone as evidence of completion. Preserve `jaw-review.blend` and all comparisons as partial/failed evidence. No source raster edits or paid calls were made. The approved v02 face and prior neck derivative remain authoritative/provisional respectively.

Next targeted fix needs a skin-only projection mask or local texture repair excluding occluding hair/scarf and portrait shadows. Do not symmetrize facial geometry to conceal this texture problem. Remaining jaw texture issue is explicitly OPEN, not fixed by this test.

Preserve accepted facial fit. Build actual hair/headscarf and repair only skin that remains exposed in the intended shot; do not spend on hidden full-head surfaces prematurely. Before animation, verify the dressed head in the intended illustrated-C lighting/framing and confirm eye construction/blink requirements. Body, horse integration, facial rigging and motion remain separate uncompleted scope. No new purchase, animation campaign or completed A5/E1 gate is implied.

Native assets are local SSD artifacts, excluded from Git. Documentation/code commits are not an off-machine asset backup.
