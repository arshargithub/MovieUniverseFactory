# Authored skin-map trial — candidate01 for Director review

Follow-up: Director found01 very close/potentially usable and requested a cheek-led continuity refinement. [Review05 / atlas02](SERIES_01_BUST_SKIN_REVIEW_05.md) records that separate candidate.01 remains unchanged as the near-approved fallback; its historical pending status below is not a rejection.

2026-09-20. The Director approved switching from tiny-patch/procedural infill to coherent texture authoring and explicitly requested preservation of earlier versions. Planning counter remains119: this is an implementation continuation, not a new planning exchange.

## Current disposition

**YELLOW: materially improved internal review candidate; Director skin acceptance pending.** Do not treat this as an approved skin baseline, finished character or animation qualification. Approved anatomy16 remains unchanged. Hair and clothing have not been worked on during this pass.

Current native: [bust-atlas-build-01/character-upperbody.blend](../../.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-build-01/character-upperbody.blend).

SHA256: `9e788591c0029a9176bb73dd4f6f478de31cf5022f2be6ffaf2acc366348b24c`.

Matched larger views: [front](../../.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-portraits-01/front.png), [left oblique](../../.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-portraits-01/left.png), [right oblique](../../.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-portraits-01/right.png), [back](../../.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-portraits-01/back.png), [three-quarter](../../.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-portraits-01/three-quarter.png). These are960×1200; left/right are camera±60° obliques, not exact anatomical profiles. Each view uses equal camera-relative soft lighting. Color-only emission views are in `bust-atlas-emission-01/` under the same trial directory.

## What changed and what did not

1. Bake the regional03 diagnostic material into a2048² cylindrical reference map. Its old patterned skin is an edit target, not an accepted appearance. Temporary bake UV is removed afterward; every original UV remains identical.
2. Make **one built-in imagegen edit**, using that map as the exact-layout target and the accepted frontal portrait only as a skin-style reference. Output is1254², not the requested2048². No automatic upscale or second generation was performed.
3. Load that authored map as a packed color image. Use one continuous cylindrical mapping across the bust. Retain the source facial shader at full weight in the central protected region and feather it across outer cheeks, chin and upper forehead into the authored map. There are no repeated tiny image-patch infills or Voronoi-cell color patterns in the new output chain.
4. Save a new derivative, reopen it in separate processes, verify native hash and material recipe, and render lit and unlit diagnostics.

The final Blender material is deliberately a **hybrid of the authored map and protected original facial color**, not a fully flattened portable atlas. The generated map alone is not a new canonical face. A final single-map bake/export is deferred until visual acceptance; do not advertise the raw generated PNG as an independently qualified replacement for the face.

Vertex positions, topology, shape keys, object transforms, original UV data and all other mesh/curve objects match anatomy16 exactly. Skin geometry/UV/shape digest: `26a5965128408dd9a66581989e5320bfe79aa5f0b3ebbff8a07bbeb4de4b5abd`. Nine file-image dependencies are packed. No face slimming, neck reshaping, symmetry edit, hair change or clothing change occurred.

## Visual assessment and remaining limits

- The repeated swirling/scratch-like skin pattern is replaced by irregular illustrated marks; the outer-face/ear/neck transition reads more coherently in inspected left/right/front/back views.
- The conspicuous stray temple lines are reduced. The original eye contours, cheek shading and lower-jaw painted tone remain; do not erase intentional features just to make every region uniform.
- Lit and color-only views were inspected. They support improvement, not a claim of fully de-lit albedo, identical local mark scale everywhere, perfect seam continuity at arbitrary magnification, or Director approval. Forehead/neck texture strength and the remaining cheek tonal transition are appropriate review points.
- The image model was asked to preserve exact map layout, but that is not a guarantee. Central facial shader retention limits exposure to generated feature drift; the feathered outer-face regions still require visual review.
- The1254² map is an economical static trial, not a proven hero-close-up resolution. Cylindrical mapping can stretch at the crown/shoulder slopes; no motion/deformation/export qualification has occurred.

## Prior versions retained for comparison

All13 prior native skin candidates are still present: smooth skin01–03, detail01–07, and regional01–03. No prior native file, render, source portrait or failed evidence was overwritten or deleted. Important reference files:

| Reference | Native SHA256 | Status |
| --- | --- | --- |
| `posterior-neck-build-16/character-upperbody.blend` | `76b2a6c7f4f1c2288ed746ebb3cf146b4146650058e263c6dd16b6f9225ef080` | Approved anatomy, immutable input |
| `bust-skin-build-03/character-upperbody.blend` | `13675790d95c399bc236803e3b3aecfb8314d6db5db70848d2ba204a3d7b5b9e` | Director-rejected smooth skin |
| `bust-detail-build-07/character-upperbody.blend` | `c591b45c6f666597498d418ebd90fa37010f37d9a7bccc2597508f2c96a23688` | Director-rejected patterned skin |
| `bust-region-build-03/character-upperbody.blend` | `861f8877c8785f3851d41cb0f503b14101d3e8e69e3212c61e06025c10b876dc` | Partial temple cleanup, unresolved body pattern |

Paths above are relative to `.runtime/art-direction/series01-facebuilder-trial-01/`. Earlier reports remain historical evidence; this is the current review pointer, not retrospective approval of any previous result.

## Source, prompt and cost record

Authored map: [skin-authored.png](../../.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-input-01/skin-authored.png), SHA256 `a5c85d73f42f135af5980950967eed5549ca365e66c1d286280d26ebd2eb709a`.

Exact prompt: [prompt.txt](../../.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-input-01/prompt.txt). Call record: [generation-record.json](../../.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-input-01/generation-record.json). Both were persisted before dispatch; output hash/status added afterward. Built-in imagegen route, not CLI or paid API harness. No `.env` access, subscription purchase, asset purchase or paid API fallback. Image tool model, tokens and monetary cost are unavailable, not zero. Engineering model/effort/usage likewise remain unknown. The generated copy is stored on the project SSD, not solely in the tool cache.

## Verification and process

142 focused tests pass. Native source/protected-state/material-reopen checks pass. One initial Blender launch failed during Metal startup before loading a scene; its failed operating record is retained. The same reviewed handler succeeded outside the sandbox with a stripped environment, autoexec disabled and a validated structured job. No crash output was overwritten by task cleanup.

Bound: one image call, one native visual candidate; original forecast45minutes/250MB, with20-net-minute diagnostic checkpoint. Operating record: `bust-skin-04-operating/`. New files before final documentation/report occupy46,775,582 bytes (~46.8MB). Prior files are retained in place rather than duplicated. Native/media artifacts are ignored by Git and not backed up remotely by documentation commits. No remote push is performed.

Captured assistant work interval:692.78seconds (11.55minutes); initial file/skill inspection before capture is unmeasured, so this is not claimed as total elapsed time. Eight ledger-wrapped jobs reconciled: five native attempts (four succeeded; startup failure retained), two successful test jobs and one completed built-in image edit. An additional nine-test pre-dispatch check was run outside the job wrapper and is not included in that job count. All rendering is finished; Director-response wait is recorded. Implementation commit: `62d4278`, local only; review documentation is committed separately.

Next: Director review of skin continuity and illustrated texture, before resuming hair/scarf work. If accepted, retain this source and perform the final bake/export check when packaging the accepted material; do not rerun image generation solely to increase pixel dimensions without demonstrating a shot need.
