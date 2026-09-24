# Front hair fit — tapered forehead opening

2026-09-23, exchange135. The Director finds hair-flow06 still wig-like from the front and still missing the prominent forehead of the base portraits. Prioritize the front, not rear polish. Accepted pair B remains appearance authority; accepted facial width, anatomy, skin and controls must not be changed to make the hair appear better. No clothing review.

## Result and limits

**YELLOW, unapproved candidate.** [Native front-fit03](../../.runtime/art-direction/series01-facebuilder-trial-01/frontfit-package-03/hair-front-fit.blend), [machine result/hash](../../.runtime/art-direction/series01-facebuilder-trial-01/frontfit-package-03/result.json). Pinned technical input `hairflow-package-06/hair-flow.blend`, SHA-256 `ab3e7d974d9495733866eebbc687a51182e71b0284d69f40a05b133b990b0ccd`; it is not approved hair.

The area is the **frontal hairline and the roots/front hair volume immediately above it**. The reference forehead reads as tall and tapered. Raising its entire border makes a broad receded opening instead of restoring this shape. This pass raises the centre locally, retains more lateral framing, draws the heavy rim closer to the actual head surface, softens the upper part's artificial notch, and adds24 very fine tapered edge strands. Texture maps unchanged; source/reference files unchanged. Existing rear-lock geometry exact; upper crown is part of the authorized front-fit edit, so the entire hair surface is not claimed immutable.

Internal judgment: the central apex and taper are closer to the reference than the previous broad/flat border. **The front remains too smooth/coherent, and the rim/temple integration still can read as a cap.** This is not a finished hairstyle or confirmation that the wig problem is solved. The fine strands are subtle at compact size; do not oversell them as visible transformation. No approved appearance or release gate advanced.

## Three bounded previews

- 01: front edge raised and fitted closer to immutable head. Forehead exposed but too broad relative to reference.
- 02: same broad opening, soften part notch and add fine edge strands. Still not the right taper; internally superseded.
- 03: central rise with retained/lowered side framing, keeping02's notch/edge treatment. Retained for comparison, not Director-approved.

Matched-face-scale visual inspection and simple image-color probes informed the contour, not a calibrated landmark detector or likeness score. Background pixels can satisfy the color threshold, so those probes are diagnostic only. Orthographic raycasts record actual visible mesh-border movement separately: central world-Z border0.87→0.94, x±0.4 borders0.74→0.67/0.68; sampling resolution0.01. These numbers prove the taper changed, **not** that the reference is matched.

## Validation and review presentation

**155 focused tests pass.** Pinned structured operations, sanitized Blender environment, auto-execution disabled. Non-hair geometry/materials/UVs/rest attributes/expression state and existing rear-lock geometry protected before/after and on fresh reopen. The final operating card records reopen and four-view pixel reproduction results. All earlier attempts retained.

Measured package verification: fresh reopen passed; all four low-resolution package views reproduce preview03 RGB pixels exactly. Native SHA-256 `d099165e5c7803f0cb0d801f8ec52353ab41ab5c41a283f8589366d6ce627d87`. Four successful native jobs consumed257.10 process seconds;28 artifact files total78,251,484 bytes. Process duration is not total engineering effort.

New review uses the visualization skill: a maximum420px-high image stage, Previous/Next buttons, direct New front/Original front/Before buttons and keyboard arrows. No dropdown. Nine selectable views from seven embedded images: approximately matched-scale original/before/new fronts, full new front, both obliques, back, and full original front/side. Front crop scale/eye alignment is approximate, not calibrated; full originals remain accessible in the same sequence. Source images are not cropped or resampled in place. Only display thumbnails and CSS framing are used. The full-front/oblique/back renders are clothing-free.

The comparison fragment is831,547 bytes. Markup/selector review completed and static preview generated. Live browser interaction validation is **NOT_RUN**: the browser could not verify its admin-enforced policy and denied localhost navigation. No bypass attempted; temporary server stopped. Button behavior and app sizing are therefore not claimed browser-verified.

## Operating record and continuation

[Compact card](../../.runtime/art-direction/series01-facebuilder-trial-01/frontfit-operating/pass-summary.json), [events](../../.runtime/art-direction/series01-facebuilder-trial-01/frontfit-operating/pass-events.json), [checksums](../../.runtime/art-direction/series01-facebuilder-trial-01/frontfit-operating/artifact-sha256.json). Forecast30 net minutes, three previews,100MB. No paid provider calls, new image generation, purchases or model-setting change. Unknown engineering model/effort/tokens/cost stay null; initial context recovery unmeasured. No motion qualification, costume change or scalp/hair physics work.

Keep local implementation and design commits separate; no remote push at135, next checkpoint140. Native media remains SSD-local, not newly off-device backed up. Next front work must use the approved portraits and this smaller comparison, and must address the cohesive cap/edge rather than repeatedly raising the entire hairline. Director approval remains required before treating any derivative as an appearance baseline.

Implementation saved locally in `5089179`; this review record is in a separate design commit. Neither was pushed in this exchange.
