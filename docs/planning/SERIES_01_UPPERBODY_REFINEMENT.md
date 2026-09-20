# Reference-led upper-body refinement

2026-09-19/20. Director authorized sustained autonomous work on (1) hair transition and cloth folds, (2) neck/collarbone definition, and (3) upper garments and crossed leather straps visible in the approved illustrations. Director explicitly accepts the present wider/squarer face for now: **do not touch face or jaw**. No new approval is required for reversible implementation choices in this scope. No purchases, paid calls, uploads or remote pushes.

Input: `reference-dress-18/dressed.blend`, SHA-256 `1fbe41cad8e01cab7d7ef41dee471e9a6aaad2253fb1e2beb4fcf9714da44e0b`. Original portrait B front/side and bilateral-04 remain authority. Implementation continuation; planning count stays 119.

Plan: inspect the actual saved scene; preserve FBHead geometry, shape values and material; add separate neck surface/detail below the facial boundary and upper-body clothing. Preserve original garment donor credit. Fit brown crossed leather straps with understated buckle/stitching to the illustrated design. No new armor, weapon, jewelry, full-body rig or performance. Neck definition should be subtle muscle/collarbone structure and illustrated skin variation, not an emaciated or muscular redesign.

Forecast: 60–90 net minutes, under 400 MB new evidence. Reassess every three variants and at 20/60 net minutes. Rendering is a diagnostic, not acceptance. Inspect front and both sides; record remaining weaknesses honestly. Native workers use reviewed repository code, validated bounded jobs, pinned sources, credential-free environment, factory startup and disabled automatic scripts. Original files remain immutable. No OS isolation qualification implied.

Work lifecycle continues in `SERIES01-LIKENESS-ASSET / facebuilder-trial-01`, activity `upperbody-reference-refinement`; the prior Director wait is ended before new activity. Engineering tokens/model effort remain unknown unless directly observed; no proxy-to-token conversion.

## First three candidates: join diagnosis

01 revealed a rectangular skin patch outside the tunic and straps over too much shawl. 02 quieted noisy leather/tunic materials, lengthened the rear veil and hid straps beneath the shawl, but showed the neck-to-chest join. 03 introduced a neck-only visible duplicate and one outside strap, but the original flared bust termination still produced an unnatural ledge. Its final attribute assertion also failed because stored float32 weights were compared for exact equality with computed float64 values. Evidence remains failed; later checks use a 1e-6 tolerance only for those weights, with the protected region still exactly zero. No failed result was called verified.

Reassessment: stop layering disconnected skin surfaces over the truncated bust. Candidate 04 cuts a **visible evaluated copy** below z=-0.95 and extends its actual closed boundary into a continuous neck/chest surface. The original FBHead mesh/material/shape values remain intact and hidden; index-independent evaluated facial surface positions and per-corner UVs above z=-0.86 must match exactly. The original facial material branch is retained and a position-clamped color blend changes only neck values below -0.86. This implements the authorized neck work without changing face/jaw. The visible derivative is static evaluated geometry, not a newly qualified facial rig; source shape keys remain preserved on the original.

## Neck mapping and second reassessment

04's continuous geometry passed, but its new faces had default UVs within the incomplete material blend, producing a horizontal seam. 05 moves the blend fully onto neck reference color before that join and smooths the junction below the protected facial boundary. Extending mesh bounds also changes Blender Generated coordinates: 05 freezes their original coordinate mapping rather than silently change the copied facial shader's behavior. 06 confines projection to an explicit neck-skin patch, eliminating cloth-colored fallback borders. This costs some of the source neck's directional definition; do not call uniform color a completed anatomical treatment.

At approximately 20 net minutes, keep continuous topology and frozen facial coordinates, and test original-versus-derivative facial base color with isolated matched emission renders. Next focus is higher collarbone relief within the exposed neckline, a less bib-like lower shawl, and close-up inspection of the hair junction. No reason to return to paid asset sourcing or face sculpting.

07 lengthened the donor lower wrap too far: reference UV coverage ran out and the straps followed deep folds into angular paths. Reject it. 08 repairs coverage, adds width-aware taut strap paths and returns to a denser swept groom instead of the sharp nearest-surface temple strands. But the adapted donor still reads as a short bib and cannot economically supply the intended shoulder-led drape. At this reassessment, retain 08 as a fallback; test one purpose-shaped shawl against the now-existing tunic/sleeve collision supports, with native static cloth settling. This differs from the earlier failed unsupported panels: there is now an actual fitted torso, explicit shoulder anchors, and a longer wrap pattern. Allow up to three bounded follow-ups (variants 09–12); remain inside the existing 60–90-minute forecast rather than open another sourcing campaign. Leather paths must continue over the shoulders rather than end as exposed cut strips.

## Dressing convergence and close-up corrections

09's settled cloth penetrated the support and appeared torn: reject the simulation result, not evidence for clothing dynamics. 10 uses a supported authored panel; 11 combines this lower panel with the donor's useful upper shoulder folds. 12 makes the separate tunic sleeves legible. This hybrid is the retained approach: adapt a donor where it supplies useful structure, author missing pieces, and avoid stretching one donor beyond its shape/UV coverage.

13 fixes chin-edge contamination in the neck reference patch. Larger views then exposed a gap beneath the left neckline fold and a flat temple support patch. 14 raises the underlayer locally and hides the flat cap while retaining swept fibers. Its close-up still showed horizontal side-neck projection stretch; 15 fades the frontal neck projection by surface orientation into a reference-sampled skin tone, without modifying the protected facial shader branch. These are explicitly bounded review repairs beyond 12, not a restarted asset search. Retain failures and superseded candidates.

## Scope of this delivery

- Denser swept hair transition and wavy side locks; indigo hood/rear veil and layered shoulder/chest folds.
- Continuous neck/upper-chest geometry with subtle tendon/clavicle relief. Much of the clavicle is covered by the scarf; not a claim of complete anatomical reconstruction.
- Separate modest tunic and sleeves, crossed leather straps extending over the shoulders, edge stitching and muted brass buckle.
- Original FBHead, material and shape values preserved. The visible derivative is evaluated static geometry with unchanged protected facial positions/UVs, not a working expression rig.

**Remaining visual limitations:** the scalp-to-lock junction is still more orderly and visibly constructed than the illustration; the scarf folds/edges are heavier and sharper, with more mottled projected color; cloth/contact areas are only assessed at the three reviewed angles. Neck sides have intentionally less reference detail rather than stretched pixels. The illustrated portrait's wind-swept silhouette and final illustrated-C lighting/material treatment are not yet reproduced. No face slimming, jaw reshaping, body/identity approval, rear/360-degree acceptance, dynamics, blink/expression, rig or horse integration is implied.

**Attribution:** adapted hood and upper folds are “Hijab” by lam_m_zack, [source](https://sketchfab.com/3d-models/hijab-ee50e01adc864ccc880caed9b5eb3bcb), CC BY 4.0. Lower shawl, tunic/sleeves, straps/buckle and neck extension were authored locally using the approved project illustrations as reference. Original donor preserved. Saved review scenes also retain hidden earlier source objects/materials; they are internal working files, not cleaned redistribution bundles. Prior attribution records remain applicable to retained data.

## Review-file binding

All artifact paths below are relative to `.runtime/art-direction/series01-facebuilder-trial-01/` on the SSD.

| Artifact | Purpose |
| --- | --- |
| `upperbody-package-15/character-upperbody.blend` | Preferred packed internal review file; source head retained hidden |
| `upperbody-package-15/result.json` | Native/source binding and packed image inventory |
| `upperbody-verify_package-15/result.json` | Fresh-process reopen, packing and protected-face checks |
| `upperbody-portraits-15/{front,left,right}.png` | 955×1647 wider upper-body views; left/right are ±45° three-quarter, not true profiles |
| `upperbody-detail-15/{front,left,right}.png` | 955×1647 close-up review views |
| `upperbody-facecheck-15/comparison.json` | Isolated original-versus-derivative base-color measurement, not aesthetic score |
| `upperbody-operating-snapshot/` | Compact lifecycle snapshot; full historical episode remains open |

Implementation source committed locally as `27c6b9d`; **90 scoped tests passed**. Native package SHA-256: `c2d1bd23ef5ce4fd07d6450fc66f62f948fa0258ab4ee6d529035641863441ec`; input build SHA-256: `1706fd81cbd4a366c7bccdce3a5266192f7cafca9bd6f94175c4aeaac5c37619`. All seven file-image entries are packed. Original FBHead geometry/UV/shape digest remains `f6a1e3970a74bb325e72a1c0b23c603a34673c225d9b3553b2c8a4a80ea658b6`; evaluated protected surface digest `fd256f12c5d2b7ae09496eab6da8615576a06bfa1abf60253031848d74c21f77` matches the original at build and fresh package reopen.

No paid provider calls, purchases, uploads or remote pushes were made in this pass. Native files and renders are ignored by Git: a local code/document commit is not asset backup. Engineering token totals and dollar allocation remain UNKNOWN. The earlier FaceBuilder lifecycle has historical coverage gaps; do not present its aggregate net time as exact.

All six final wider/close-up views were visually inspected. Final matched base-color RGB MAE (0–255), front/left/right: **0.003026 / 0.003076 / 0.003109**. Maximum channel differences: **1 / 1 / 4**; pixels exceeding 2: **0 / 0 / 1** in the fixed 592-row facial review region. These are descriptive measurements, not invented acceptance thresholds. Rendering is not pixel-exact; the exact geometric/UV invariant is separately checked. No claim that unchanged geometry alone preserves every lighting/shading effect.

Disposition: **YELLOW static wardrobe review candidate, Director acceptance pending**. The three requested areas have an implemented, inspected result; remaining stylistic shortcomings above are not closed. The next material decision is whether the assembled costume reads correctly before further polish/rig integration. This does not close the overall character or Blender qualification milestone.

This work block began at **2026-09-20 01:59:25 UTC**, approximately **57 minutes** to review handoff, including local render/check work and no Director wait within the block. Ledger timestamps are authoritative; this is not token-generation time. Fifteen build variants were preserved, with one native assertion failure (03) and additional visually rejected candidates described above. Evidence occupies **472,592 KiB (about 461.5 MiB)** before the small final record updates, exceeding the initial under-400-MB forecast. The bounded overrun retains diagnostic failures, final high-resolution views and two packed review copies; no old evidence was deleted to hide growth. SSD free space remained about 917 GiB. No new native jobs are needed for this handoff.

## Process learning

The high-resolution close-up should happen earlier: low-resolution full-body previews concealed root joins, a neckline gap and side-neck projection artifacts. Use one wide view plus one close-up before another three-view sweep. Do not run two large render suites concurrently on this Mac; contention increases latency. Pin/evaluate the accepted face independently of clothing and use an isolated base-color comparison to detect coordinate-mapping changes caused by altered mesh bounds. Do not equate passing geometry checks with visual acceptance. Future animation work must solve rig/eye/cloth prerequisites rather than carry this static evaluated copy forward as though those were complete.
