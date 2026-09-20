# Neck anatomy continuation: remove the middle swell

**Superseded assessment:** the Director subsequently rejected 07 for remaining neck-to-shoulder swelling and lost throat/collarbone definition. See [continuation 03](SERIES_01_NECK_ANATOMY_REVIEW_03.md) for the current review pointer. The measurements and renders below remain historical evidence, not acceptance.

2026-09-20. Director rejects anatomy candidate 04: the middle-neck bulge remains visible, particularly from back and three-quarter. This supersedes the prior assistant's favorable assessment, not the preserved evidence. Continue until a materially better all-angle clay result; no texture/clothing edits. Face/jaw and shortened vertical proportions remain locked. Planning counter 119 unchanged.

Activity `neck-anatomy-2`: prospective forecast 30 minutes / 100 MB, reassess at 20 minutes and three candidates per hypothesis. No paid calls, purchases, uploads, model switch or remote push. Earlier work remains in its separate activity. Native jobs serial. Model/effort/tokens unknown.

## Diagnosis and correction

Measured the rejected 04 from its hash-bound native file. At the rear-oblique and side cross-sections, radius grows and then shrinks again between z=-0.70 and -1.30. For example, the 60-degree rear-oblique radius is approximately 0.5837 at -0.90 and 0.5794 at -1.00. The surface averaging pass rounded this shape but retained the underlying swell. The posterior centerline alone was monotone and therefore insufficient as a diagnostic: inspect the whole circumference and actual renders, not just one ray or the front view.

05 replaces the broad profile with a smooth mathematical taper. It is rejected: the blend against the retained upper neck produces diagonal creasing and an abrupt lateral narrowing. Preserve `neck-anatomy-build-05/`; passing protected-state tests does not mean acceptable anatomy.

A read-only clay inspection of retained **FBHead** (`neck-anatomy-template-05/`) shows a cleaner continuous anatomical neck already present in the original fitted head. The constructed replacement discarded too much of that useful shape. 06 therefore restores the original fitted neck surface through z=-1.00 and extends only the lower surface toward the shoulders. It restores the strict full z>=-0.86 protected-face-plane invariant; no upper posterior-neck exception is needed. Its quintic lower extension still exaggerates the shoulder inflection. 07 uses a simpler endpoint-slope-matched cubic extension, slightly less posterior depth and softer collarbone relief. The original FBHead itself is never modified.

The lower shoulder/neck derivative's back depth changes: 07's terminal rear radius is 0.94 (previous 36 approximately 0.77). This is deliberate geometry, not texture or clothing adjustment. Costume objects remain byte-equivalent under their geometry/material guards, but their clearance to this changed support must be checked before resuming dressing. Do not claim a newly qualified clothed result.

## Localized defect measurement

Native cross-sections sample every 0.02 z units. In z=-0.70..-1.30, descending radial steps below -0.0002 were counted at seven posterior/lateral directions. This is a diagnostic for the observed swell, **not a general anatomical acceptance threshold**.

| Ray angle (0 = rear) | Rejected 04 descending steps | 07 descending steps |
| --- | ---: | ---: |
| 0 | 0 | 0 |
| 30 | 0 | 0 |
| 60 | 7 | 0 |
| 90 | 11 | 0 |
| 270 | 10 | 0 |
| 300 | 7 | 0 |
| 330 | 0 | 0 |

The minimum step in 07 across these rays is +0.001532 scene units; the prior side swell/return is removed in this sampled region. Evidence is in `neck-anatomy-profile-04/result.json` and `neck-anatomy-build-07/result.json`. Preserve lighting-based visual review as an independent requirement.

## Review and handoff

Current review candidate is **07, YELLOW pending Director acceptance**, not a claim of medical anatomy, finished shoulder/back sculpt, animation or rig readiness. Actual front, left/right profiles, back and three-quarter clay renders are alongside `neck-anatomy-build-07/character-upperbody.blend`. Native SHA-256 `5287c75331390e7b2ffa6523456098742e15d7941ae9519605d8af6b4b1c0b23`. Base/source remains `upperbody-package-36/character-upperbody.blend`, SHA-256 `983f128f82c51efd7b2ab35e06d8c679bbc3fdd38635eabd0687ccddbda71efa`.

Fresh-process eight-angle directional-light clay review is in `neck-anatomy-raking-07/`: front, ±45°, ±90°, ±135° and back. Its result also repeats original-head, other-object, material, UV, vertical-proportion, protected-face and packed-image guards before render-only material changes. Final inspection/verification findings below.

**Final inspection:** all five matched soft-light views and all eight directional-light views inspected. The pronounced middle band seen in 04 is no longer apparent; the posterior/lateral contours now transition continuously rather than swelling and narrowing. The shoulder/base anatomy remains simplified and fairly broad; a tiny local surface irregularity below the left side of the jaw remains visible under directional light, distinct from the removed circumferential bulge. Do not describe this as a finished close-up anatomy asset or use technical passes to substitute for Director judgment. No material/costume work resumed.

Fresh reopen passes: protected surface digest `fd256f12c5d2b7ae09496eab6da8615576a06bfa1abf60253031848d74c21f77`, 16,952 protected vertices, exact zero Z delta, original head and all other geometry/materials unchanged, eight embedded file images. No posterior exception is used in 07. **120 focused tests pass.** Implementation commit `63a51df`, sealed after the builds/review; individual results record their actual handler hash. Raking verification handler SHA `95b628a60dbb0908f18738f1c0905fbb566bc969e6316d1e0e3c4ec78969ed3b`.

Three new geometry candidates (05–07), all retained. Eight native jobs and one wrapped final test job completed successfully, no unfinished jobs. Earlier focused unwrapped test invocations are not included in the job count. Generated diagnostic/candidate evidence is 90,147,864 bytes, within the 100 MB forecast; this excludes ledger export/job inputs and previous activity evidence. Work began 16:33:45 UTC; final exact interval and review wait are exported to `neck-anatomy-02-operating/`. The roughly 18-minute working interval stays below the 20-minute diagnostic checkpoint; no further variants are planned in this continuation. Source/documentation local commits remain separate; native files remain local ignored assets, not remotely backed up by Git.

Process learning: start with the intact fitted anatomy as the reference; preserve useful source shape before creating replacement formulas. Surface smoothness, monotonically changing radii, protected-state tests and aesthetic correctness are separate checks. Repeatedly softening an implausible shape is not a fix. Use rear-oblique views and directional light early, and record Director rejection even when all technical tests pass. No engineering model comparison can be inferred from this continuation.
