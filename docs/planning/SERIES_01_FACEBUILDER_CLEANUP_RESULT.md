# Pashtun head — material cleanup and portable-base result

2026-09-19. Implementation continuation; no new creative planning exchange. Approved base: `head-v02-two-view.blend`, provisionally accepted at exchange 119. Illustrated pair B remains identity authority.

## Result

**YELLOW: usable approved facial starting point and verified portable base, not a completed character.**

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

Preserve accepted facial fit. Build actual hair/headscarf and repair only skin that remains exposed in the intended shot; do not spend on hidden full-head surfaces prematurely. Before animation, verify the dressed head in the intended illustrated-C lighting/framing and confirm eye construction/blink requirements. Body, horse integration, facial rigging and motion remain separate uncompleted scope. No new purchase, animation campaign or completed A5/E1 gate is implied.

Native assets are local SSD artifacts, excluded from Git. Documentation/code commits are not an off-machine asset backup.
