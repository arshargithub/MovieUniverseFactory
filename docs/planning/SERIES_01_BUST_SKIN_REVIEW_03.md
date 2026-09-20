# Regional cleanup: local progress, whole-bust texture unresolved

2026-09-20. Director rejected detail07 for an artificial skin pattern, visible cheek-to-ear transition, dark streaks above/beside the eyebrows and a viewer-left scar-like temple remnant. Anatomy16 remains accepted. Planning counter remains119.

## Disposition

**The whole-bust skin objective is NOT achieved.** Do not promote the latest file as an accepted/preferred overall skin material. Two additional procedural infill variants were visually rejected internally. A local projected-hair cleanup is retained separately for controlled comparison, pending Director review.

`bust-region-build-03/character-upperbody.blend` under `.runtime/art-direction/series01-facebuilder-trial-01/` is a **local-repair diagnostic derivative**, not a new global solution. It intentionally keeps detail07's rejected body pattern and face blending so the brow/temple cleanup can be assessed independently. Native SHA and invariant checks are in its `result.json`. Five larger960×1200 views are in `bust-region-portraits-03/`; its `setup.png` is only640×800. The earlier source remains immutable.

## Findings and bounded attempts

- The diagonal dark/scar-like features are present in the previous base-color emission views. They are texture artifacts, not evidence of new facial grooves. Their location corresponds to retained/projected hair near the illustration's skin boundary. This diagnosis does not imply every natural crease or asymmetry is a texture defect.
- Tiny donor-patch reuse, altered orientation and broad masks did not produce coherent skin. A local-contrast statistic cannot establish equivalent texture character or hide a boundary between differently authored regions.
- Region01 tested aperiodic native color facets plus local forehead-skin transfer. Its new infill looked like a mosaic/camouflage rather than the approved face and was rejected.
- Region02 softened the facets and adjusted the temple mask. It still failed the whole-bust style match. The broader donor rectangle could also introduce a new near-hairline trace; it is not a solved local repair.
- Region03 narrows the donor to central forehead skin (approximatelyx449–511,y390–423 in the955×1647 source), then applies it only to outer upper-brow/temple regions. Central face, eyes and inner brows are excluded by the mask. It reconstructs detail07's material and replaces only that localized facial branch, retaining the original global texture for comparison. The dark remnants are reduced in the inspected build views; full visual acceptance is not asserted.

No face/neck/shoulder reshaping, hair changes or costume work occurred. Native geometry/connectivity/transform/UV/shape state and all other mesh/curve objects are checked against hash-pinned anatomy16. Eight image dependencies remain packed. Native fresh-open validation checks the file hash and material recipe.133 focused tests pass; these are technical protections, not proof of visual success.

## Recommended method change — not executed

Stop the shader-pattern/mini-patch loop. Author a coherent base-color texture map across connected outer-face, ear, neck and shoulder regions, while protecting the accepted central face and the approved geometry. Integrate reference-driven painting/inpainting at map scale, not another contrast adjustment to tiled samples. Check seam continuity and actual illustrated mark character in matched lit and emission views before considering it done. Preserve facial landmarks and natural tonal variation; do not erase them to force an easy blend.

This is a recommendation requiring Director direction before a new authoring trial. No image-generation call, paid provider, outside artist, subscription or purchase is authorized by this record. Any provider-assisted route must identify the tool, budget accounting and source/face preservation checks before execution. Image generation is not guaranteed to preserve UV alignment or likeness; authored output must be validated in Blender. A new atlas/UV channel must preserve original UVs and geometry and be documented explicitly.

## Process

Final inspection of both emission03 obliques confirms a reduced but still faint brow/temple trace; the cheek-to-ear boundary and patterned infill remain visible without lighting. No full cleanup claim is warranted. Diagnostic native SHA256: `861f8877c8785f3851d41cb0f503b14101d3e8e69e3212c61e06025c10b876dc`. Implementation is committed locally as `154f5ac`; no remote push.

Captured assistant activity: 771.64 seconds (12.86 minutes), excluding the unmeasured initial inspection noted below. Eight jobs reconciled successfully: six native jobs and two focused test runs. Three candidate variants retained. New regional artifacts occupy 106,437,230 bytes (about 106.4 MB), below the 120 MB forecast. These execution successes do not change the failed visual disposition. Work interval ended and Director-response wait started; no render remains running.

Activity `bust-skin-3`: bounded three candidates, initial forecast30minutes/120MB. All failures preserved. Initial read-only diagnosis occurred before lifecycle capture; its duration is unknown, so the captured work interval is not claimed as total task elapsed time. Operating report: `bust-skin-03-operating/`. No paid calls, purchases, downloads, deletes, uploads or remote pushes. Engineering model/effort/tokens unknown. Keep implementation and documentation commits separate; native files are ignored by Git and not remotely backed up.
