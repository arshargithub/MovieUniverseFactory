# Facial performance diagnostic01 — reuse works; integration remains

2026-09-21, exchange121. Bounded authorized implementation following [readiness recommendation](SERIES_01_FACE_PERFORMANCE_READINESS.md) and [authored motion brief](SERIES_01_FACE_PERFORMANCE_MOTION_BRIEF.md). **YELLOW, diagnostic complete; minimum acting proof incomplete.** This disposition does not close the whole FaceBuilder episode or change release gate counts.

## Outcome and material decision

We do not need to discard or remodel the accepted face to acquire useful expression controls. The installed FaceBuilder core generated51 source shapes. Nineteen were transferred to a separate accepted-bust derivative using unique original UV incident sets and verified edge adjacency:16938/16938 upper-head vertices mapped, zero facial-edge mismatches. No nearest-position transfer across lips/lids. New lower-neck vertices are not blindly indexed into the old head.

The cheap pose check exposed necessary localized integration:

- Blink: clay lids close plausibly in frontal/oblique renders, but the current projected dark eye texture stretches onto them. A closed-lid surface needs appropriate skin rather than a squeezed open-eye image.
- Gaze: no separate independently aimable eyeballs exist. The continuous head is one connected mesh; its only boundary chain is the306-vertex bottom opening. This is not an eye rig.
- Mouth: a small jaw-open test reveals vertical projected-color streaks/unfinished interior; it is not a usable oral cavity. No teeth/tongue qualification.
- Jaw/neck: direct donor jaw displacement produces a small scalloped transition near the fixed neck. A deformation corrective/better transfer falloff is required; **accepted neutral anatomy itself remains unchanged**.
- A restrained smile is a promising engineering preview, not Director-accepted acting. Full gaze/blink/skepticism/smile playback is NOT_RUN pending eye/mouth readiness. Hair/scarf remain deferred.

**Recommend the smallest structural integration, not a new general rig:** separate aimable eyes, clean closed-lid mapping, basic mouth lining and jaw/neck corrective, then the already-written10second acting proof. This requires an explicit localized exception to the current all-neutral-geometry/UV lock on the derivative for eye/mouth internal surfaces and their UVs. Preserve accepted external silhouette, neutral expression, brows/nose/lips and atlas02 reference. No paid assets or calls proposed; start with another20-net-minute checkpoint and stop if preserving likeness requires broader facial reconstruction. It is not yet proven that this local adaptation will be quick or fully automatic.

## Preservation and attachment checks

Changed five Object-coordinate shader links to a per-vertex rest-position attribute. This preserves current shading functions without introducing an additional cylindrical UV seam. Original UV layers remain unchanged. Rest positions persist in the native file and equal neutral coordinates. Neutral face geometry, polygon connectivity, original UVs, object transform and other scene objects match after a fresh process reopen. All file images packed. All19 expression controls are zero at saved neutral; Blender's `Basis` reference reports1.0 and is not an active expression.

Matched640×800 neutral renders: maximum per-channel8-bit delta1 in both front and oblique; mean absolute channel deltas0.00002490234375 and0.00002734375 respectively (including alpha). These are essentially identical neutral images, not proof of every animated lighting condition. Geometry preservation and unchanged source hash pass. Stable sampling is implemented; a complete moving-texture visual test remains NOT_RUN.

## Evidence bindings

Local base: `.runtime/art-direction/series01-facebuilder-trial-01/`.

| Artifact | SHA256 / evidence |
|---|---|
| Immutable accepted `bust-atlas-build-02/character-upperbody.blend` | `408a982610f4fe9260101f34245099ae80731de9c7b56e58e46963f854a22dd5` |
| Source expression deltas `face-performance-diagnose-01/donor-facs-deltas.npz` | `301d92be8bc3969fbf683940f8a49788cfb659bd257c3ff360165e64f2ae6703` |
| Derivative `face-performance-transfer-02/face-readiness.blend` | `747043d68620efc2f956bf0485a827e884d3f47cce2ecaed3ebfafe927288902` |
| Pose previews | `face-performance-transfer-02/{neutral,blink,smile,jaw}.png` |
| Matched appearance and clay blink | `face-performance-verify-03/` |
| Final reopen/preservation record | `face-performance-verify-04/result.json` |

No native source, earlier renders or failed evidence deleted. SSD native files are not committed or independently backed up by these Git notes. Handler result hashes identify executed revisions; final committed handler additionally contains later diagnostic/reporting corrections, not a claim that every run used identical code. Reproduction is local to this pinned installed core/asset setup, not a portable arbitrary-head tool.

## Efficiency and failed attempts

One transfer worker was terminated before save: accessing compressed NPZ arrays inside the vertex loop repeatedly decompressed them. Loading each array once fixed it; the corrected transfer plus four renders finished in about20seconds of Blender log time. Preserve the failed job; do not exclude it from effort. Verification02 stopped because its assertion incorrectly counted Basis=1 as a non-neutral expression. Verification03 exposed individual flags;04 correctly excludes Basis and checks evaluated neutral vertices. These were engineering defects, not model/rig evidence failures. Record explicit per-check outcomes before assertions in future diagnostics; cache decoded numeric arrays outside loops.

19 focused unit tests pass. No paid API calls, asset purchases or license changes. Measured diagnostic activity04:20:09.625758–04:37:09.740817UTC: **17minutes0.115seconds**, before final handoff bookkeeping. Six serial native jobs totaled218.488seconds (including132.959seconds for the terminated slow worker and16.870seconds for the failed assertion). Approximately44MB new local evidence. Initial file inspection before the work-start event is outside that measured interval; no exact whole-turn claim. Engineering model/effort/tokens and subscription cost allocation unknown, not zero. Full historical episode net time remains incomplete because of earlier coverage gaps. Compact operating report/evidence remains under `face-performance-operating-final/` after finalization. Implementation committed locally as `fe2027c`; design/handoff in a separate local commit. No remote push this exchange; next cadence checkpoint130.

## Closure card for this diagnostic slice

- Goal: test existing expression reuse and identify minimum facial readiness gaps without changing accepted appearance.
- Disposition: diagnostic complete YELLOW; broader facial readiness remains open, with zero Director-accepted acting clips.
- Reusable outputs: source shape library, validated UV/adjacency binding,19-control neutral derivative, stable rest-position shader mapping, preservation/pose evidence.
- Unproven: eye aim, clean textured blink, oral interior, jaw/neck continuity in motion, complete acting naturalness, animated costume clearance.
- Learning transfer: static likeness acceptance does not imply animation readiness; recover native deformation data before hand-sculpting controls; inspect clay and texture independently; preserve neutral identity as a separate authority.
- Next decision: limited internal eye/mouth surface/UV adaptation under an external-likeness lock, rather than dressing a still-only face or beginning unrestricted reconstruction.
