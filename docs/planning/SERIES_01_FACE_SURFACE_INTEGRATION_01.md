# Localized facial integration and acting preview

2026-09-21, exchange122. Director approved the localized surface/UV exception proposed in [diagnostic01](SERIES_01_FACE_PERFORMANCE_DIAGNOSTIC_01.md). [Motion brief and authorization amendment](SERIES_01_FACE_PERFORMANCE_MOTION_BRIEF.md) remain the contract. **Bounded implementation complete; YELLOW pending Director playback/likeness review.** No production-quality facial-rig or dialogue qualification is claimed.

## What changed

- Fitted two independently aimable spheres to stationary inner-eye geometry (fit RMS0.000453/0.000905 scene units). Original illustrated eye color follows each sphere through stable mapping. Replaced98/114 inner-cap face render assignments with transparency, retaining all original mesh vertices and polygon connectivity. Nineteen blink-shape vertices per side receive a clearance corrective; neutral geometry remains unchanged.
- Added two closed-lid UV channels and blink-linked skin reconstruction. Native non-scripted AVERAGE drivers connect shape values to material blend factors; no runtime code callbacks. Original UV channels remain exact. Closed-lid detail is plainer than the cheek and not final eyelash/eyelid polish.
- Reassigned only50 high-stretch recessed mouth-cap faces to a dark lining material. This removes projected-color streaks in a modest0.2 jaw-open diagnostic while preserving the exterior lips. It is a **basic lining**, not a modeled dental/oral system or proof for larger opening, speaking or shouting.
- Smoothed jaw displacement through the upper-neck transition, without altering neutral neck anatomy. Hair, scarf and clothing not edited; deliberately hidden in facial review renders. Costume motion clearance remains open.

Candidate01 is preserved and rejected internally: its lid sampling included dark brow pixels, and its broad mouth mask extended onto the lip edge. Candidate02 uses cheek-side samples, lid/eye clearance, and mouth-cap selection based on deformation area growth rather than a broad rectangle/ellipse. No third surface variant was needed for this bounded preview.

## Complete preview and evidence

Local artifact root: `.runtime/art-direction/series01-facebuilder-trial-01/`.

- Review video: `face-surface-motion-02/review/acting-front-oblique.mp4` —10.000seconds,120frames,12fps,768×480 synchronized front/oblique views.
- Native acting file: `face-surface-motion-02/face-acting.blend`, SHA256 `2f213e15c9d03ae0ae30f1a8c62c2df3a04e8d108d601a86fa6e2404d8b06a31`. Native action24fps,frames1–240.
- Neutral integrated derivative: `face-surface-build-02/face-integrated.blend`, SHA256 `c7d119fe276d8198de3cd87bb2da46cfd6bbdeb580a62b34413afeb77edc57cf`.
- Original accepted atlas02 still SHA256 `408a982610f4fe9260101f34245099ae80731de9c7b56e58e46963f854a22dd5`; never overwritten.
- Six chronological contact sheets cover all240 rendered view-frames under the review directory. Agent inspected those sheets and full-size pose diagnostics; **Director real-time playback judgment remains pending**, not inferred from numeric gates.
- `face-surface-verify-02/result.json`: exact original geometry, polygon connectivity, transforms and original UV preservation; all images packed; valid blink drivers after fresh open; neutral return exact.
- White-eye visibility diagnostic:1565 visible pixels at neutral, zero at full blink, measured from640×800 frontal masks. Oblique closure inspected visually. This is a scoped diagnostic, not arbitrary-angle/all-expression collision certification.
- All240 native frames evaluated finite. Start/end geometry exact; front and oblique first/last rendered images are pixel-identical. Five saved-action checkpoints reproduce controls/eye rotations/blink drivers in a fresh add-on-free process (`face-surface-reopen-02/result.json`), with maximum observed control error below2e-8.
- Matched neutral versus prior derivative: mean absolute8-bit RGB delta0.0155801 globally; outside stated eye/mouth review rectangles mean0.00069294,max1. These comparisons support local appearance preservation, not a claim that new eye shading is identical under every light.

Performance is intentionally restrained: gaze about5degrees, brief blink near1.4seconds, unilateral brow lift/pressed lips around3seconds, small smile with cheek participation near6seconds, settling to neutral. It is a facial-only technical/creative preview, not a complete acted shot. Gaze timing, warmth and likeness still require Director judgment. Full phonemes, teeth/tongue, large eye excursions, extreme expressions, rig-wide collision checks and formal negative-control qualification remain deferred/unrun. Do not label all19 available controls individually qualified merely because this subset works.

## Effort, learning and next step

Recorded integration/review work07:05:33.044748–07:26:13.774673UTC: **20minutes40.730seconds**, followed by separately captured final handoff bookkeeping. Seven native jobs totaled266.751seconds; full two-view render186.291seconds. Two surface candidates, approximately184MB added local evidence,28 focused unit tests passing. Initial pre-ledger file reads are outside the measured interval. Paid API calls0; no asset purchases/license changes. Engineering model/effort/tokens unknown; no subscription-token cost inferred. Full historical episode net time remains incomplete, so these are current-slice measurements only.

Learning: preserve donor topology/UV identity; fit existing anatomical surfaces before inventing anatomy; use deformation behavior to isolate mouth interiors; test driver values and actual occlusion rather than trusting a plausible clay still. Static asset, deformation controls, material response and audience-facing acting are separate acceptances. Cheap six-pose diagnostics eliminated candidate01 defects before rendering the full sequence.

**Next:** Director review of the synchronized clip for identity, blink/gaze and restrained expression quality. If accepted for this bounded purpose, freeze this facial-motion baseline and resume hair/scarf/dressing with motion clearance. Do not reopen the accepted skin/anatomy for optional cosmetic refinement. If a visible defect is rejected, repair that specific demonstrated defect rather than restarting asset construction.

Source/tests and design notes use separate scoped local commits. No remote push this exchange; next checkpoint130. Native assets remain on the SSD, not in Git; no independent backup claim. Operating report: `face-surface-operating-final/REPORT.md` and `summary.json`. The whole FaceBuilder episode is not closed by this subtask result.
