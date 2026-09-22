# Hair-flow continuation — crown and painted lengths

2026-09-22, exchange134. Director requested continued improvement; no hairstyle acceptance inferred. Appearance authority remains approved portrait pair B. Accepted face/skin/anatomy/controls and the current scalp-support/forehead-opening geometry remain protected. Clothing-free review only.

## Outcome

**YELLOW, review candidate, not production-qualified hair.** Current native: [hair-flow06](../../.runtime/art-direction/series01-facebuilder-trial-01/hairflow-package-06/hair-flow.blend), SHA-256 `ab3e7d974d9495733866eebbc687a51182e71b0284d69f40a05b133b990b0ccd`. [Machine result](../../.runtime/art-direction/series01-facebuilder-trial-01/hairflow-package-06/result.json). Immutable source: `framing-package-03/hair-framing.blend`, SHA-256 `f672d4faa324ffddb00234966d3d7e7c591ee7e9d81fad82598fa7620dcc51ee`. It is an unapproved technical starting point, not the visual authority.

The conspicuous crown band is substantially reduced by mapping a two-dimensional source footprint over the raised crown rather than stretching a near-constant image row. The original frontal painted-hair material remains. Hanging waves have modestly unequal bend/width/length, with fixed roots. Side/rear fallback material uses one newly authored dark-chestnut hair texture guided by the approved front image; the old transverse portrait projection is removed from the hanging locks.

Internal visual judgment from front, both three-quarter views and back: this is a useful improvement in crown continuity and illustrated rear detail, **not yet the loose, luscious, naturally layered silhouette of the approved original**. Side masses remain too solid, the cap-to-length join remains visible in obliques, and temple/ear edge integration is too tidy. Rear styling is provisional because neither approved portrait establishes a rear hairstyle. Do not promote this to an approved appearance baseline or resume costume/motion on the strength of technical tests.

## Preserved and verified

- Accepted non-hair geometry, material/UV state, rest attributes and expression controls match before/after and on fresh reopen.
- Additional full scalp-support geometry/topology/world-transform digest protects the current forehead opening. UV changes on upper hair are deliberate; unchanged geometry does not imply identical lit pixels because changed hair can affect shadowing.
- Source and two approved reference hashes pinned; new texture hash pinned and image packed into the native.
- **144 focused tests pass.** Fixed structured operations, sanitized Blender environment and auto-execution disabled. No arbitrary model-produced Blender code.
- Package reproduces all four inspected640×800 preview06 RGB images exactly; portrait front/left/right are955×1647 and were also visually inspected. Final machine evidence and operating card record results.
- Existing originals, earlier native files and failed previews are retained. No source-image edits or face redesign.

## Iterations and honest limits

1. Crown01: upper streaking exaggerated; lower waves separate into deliberate gaps. Internally rejected.
2. Crown02: lower wave variation reduced, but upper band remains. Internally rejected.
3. Crown03: continuous vertical sampling reduces the band. Retain this upper mapping; regular procedural rear remains unlike approved brushwork.
4. Source-strip material04: directly reusing a narrow illustrated side-hair swathe copies unwanted shapes and creates horizontal bands. Internally rejected, not a successful atlas.
5. Authored-texture05: one built-in generated hair-only texture produces finer irregular rear brushwork; transverse old front projection still crosses the hanging roots.
6. Final06: remove that projection from hanging locks; same crown and generated texture. This is the second preview of the authored-texture hypothesis, not a sixth variant of one hypothesis.

This **exceeds the initial three-preview forecast**. Reassessment and changed hypotheses were announced/recorded; forecast expanded from30 to45 net minutes and100 to120MB. Six previews and one package, no infinite loop or hidden fourth crown variant. Stop this bounded pass at a visually inspectable candidate. Next focused work should address side silhouette and cap/temple transitions, not more serial hairline lifts or another general texture noise layer.

Preview05 has an overbroad legacy Boolean `changes.new_assets_or_paid_calls=false`: a new built-in bitmap was in fact used, and its hash is present in that record. Final06 separates purchases, project-provider calls and built-in generation; the operating card records this correction without rewriting old evidence.

## Generated asset provenance

One **built-in image-generation tool** call, not the CLI/API fallback; no project-provider API calls or purchases. Tool usage/cost is unreported, not free/zero by inference. The original approved front portrait was supplied as style/palette reference only, not as an edit target. The image-generation skill led to a dedicated hair-only bitmap after direct source-strip projection failed; the comparison-view skill provides switching between originals, previous result and new angles.

- Workspace texture: [hairflow-painted-texture-v01.png](../../.runtime/art-direction/series01-facebuilder-trial-01/hairflow-painted-texture-v01.png).
- SHA-256: `e4f2d874ecebd5b46bd0b24923d4b746f0b6a159f82aaf0417bc3137ec215dbf`.
- Original tool output preserved: `/Users/adisharma/.codex/generated_images/01a0878c-e7a2-75e0-873c-c31d97f879a1/exec-84072721-5f66-4aa7-8149-99f2b3b8184f.png`.
- [Exact final prompt](../../.runtime/art-direction/series01-facebuilder-trial-01/hairflow-texture-prompt.txt): square, edge-to-edge dark-chestnut hair-only albedo; fine irregular hand-painted vertical waves guided by approved hair; no face, skin, scarf, background, roots, tips, horizontal bands or photoreal/plastic finish. Tileability was requested, **not formally qualified**.

## Operating evidence and durability

[Compact card](../../.runtime/art-direction/series01-facebuilder-trial-01/hairflow-operating/pass-summary.json), [events](../../.runtime/art-direction/series01-facebuilder-trial-01/hairflow-operating/pass-events.json), [artifact checksums](../../.runtime/art-direction/series01-facebuilder-trial-01/hairflow-operating/artifact-sha256.json). Card contains measured native durations, bytes, job reconciliation, captured activity excluding Director waits, and preview/package pixel comparison. Initial context recovery unmeasured; engineering model/effort/tokens/cost unknown. One built-in image call is separate from zero paid project-provider calls.

Seven successful reconciled native jobs,323.57 process-seconds.48 evidence/texture/prompt files,88,247,580bytes, excluding gallery/operating exports. Under both initial100MB and revised120MB artifact forecasts. Generated comparison embeds eight thumbnails and preserves full originals/renders locally.

Comparison layout and image switching were verified in the local browser preview; temporary tab/server closed afterward. Full rendered files, not the display thumbnails, are the native visual evidence.

Implementation commit `e4cb4c1`; design recorded separately in a local commit. No remote push this exchange; next checkpoint140. Native media remains SSD-local and is not newly backed up off-device. Accepted release gates remain1/25; no hair, costume, animation or release gate advanced.
