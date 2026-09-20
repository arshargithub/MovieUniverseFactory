# Sustained portrait dressing refinement

2026-09-19. Director explicitly requested persistent refinement until the result closely matches the approved front and side portraits, not another marginal donor fit. No purchases or paid calls authorized here. Keep approved bilateral-04 face geometry, shapes and material immutable. Implementation continuation, planning counter unchanged.

Target: loose indigo cloth behind chestnut waves; open jaw/neck; crown silhouette close to scalp; broad diagonal shoulder folds rather than a neck collar; illustrated texture, no exposed card roots or cloth/hair penetrations. Review front and both three-quarter views together. Original portrait B remains the visual authority; source assets are only donors.

Forecast: 30–45 net minutes including implementation, inexpensive renders, review and packaging, under 250 MB candidate growth. Reassess at 20 net minutes and every three variants; do not use persistence as permission to call weak results accepted. No full-body, rig or motion qualification implied.

## Hypothesis A: authored panels and native cloth settling

`reference-dress-01` rejected: repeated parallel folds, exposed hair roots, overly regular panel ends.
`reference-dress-02` rejected: native cloth settling softened folds, but shoulder support and anchored border produced floating collar edges; hair too straight/light.
`reference-dress-03` rejected: changed support occluded/intersected the cloth; hair still crossed the hood. This is not reference fidelity. Native jobs ran successfully, which does not make the images acceptable.

Three-variant reassessment: do not tune this panel/support arrangement further. Reuse the donor's real lower-garment folds as a separately fitted diagonal shoulder wrap. Keep the donor hood; move its side rim behind the hair. Test native texture projection from the accepted illustration onto cloth only, with blue-dominance filtering to exclude non-cloth content. This reuses original images as Blender material inputs; no raster source is edited/generated and no accepted face material is changed.

Results and final disposition follow below. No Director acceptance is implied.

## Hypothesis B: adapted donor folds and reference color

Variants 04–06 retained the source garment's folded lower cloth rather than the failed simulated sheets. Material transfer uses the approved front illustration, with non-blue samples excluded; source images are unchanged. This is projected, baked-in illustrated shading, not physically recovered albedo. Variant 05's texture cards remained chunky; rejected. Variant 06's fine-fiber locks and diagonal donor folds are a better direction but still have visible root/cloth intersections and open edges. Not yet a close match.

At the next three-variant reassessment, stop changing hair representation: keep fibers and diagnose root placement. Constant depth offsets put some roots outside the scalp; change offsets to grow only along the lock after its root. Fresh-process read-only inspection of variant 06 identifies small independent boundary loops on the wrap (24, 6 and 4 edges) separately from its intentional large perimeter. Close those small loops only. Add side-reference color projection to reduce front-projection stretching on the side of the hood. This is a focused topology/root/projection correction, not another unstructured material variation.

## Hypothesis C: topology, root and projection corrections

Variants 07–09 repair independent small wrap loops, round the static wrap shell, add side-image projection and move physical hair roots behind the ears. Variant 08's radial hood clearance creates abrupt strand compression and is not retained for later variants. The lower root path of 09 is better, but side views expose missing hair volume between the original painted scalp and new physical locks. Still not a close-match completion.

20-net-minute reassessment: retain donor folds/fine fibers rather than revive the failed sheets or cards. Continue within the original 30–45-minute forecast with a specific missing piece: a separate side/back hair cap bridging the painted scalp to the locks, plus a longer rear veil to eliminate its cropped rectangular hem. Do not alter the approved face or claim full-groom/animation readiness. Storage observed after variant 07 was about 95 MB; no native evidence deleted.

## Hypothesis D: hair-volume bridge and longer veil

Variant 10's generic cap filled space but its straight strands looked like a comb. Variant 11's duplicated scalp shell produced an unacceptable stepped front edge and was rejected; the original head itself was not changed. Variant 12 returned to the separate cap, lowered sharp neckline projections and used side-image color, but the broad color projection repeated part of an ear on the hair. Reject that material rather than call it a small remaining flaw. Next correction is a deliberately restricted hair-only sampling patch from the front portrait, and greater overlap of the separate cap with the original painted scalp. No raster source editing. These findings are retained so future workflows do not repeat broad color-threshold projection as if it reliably segments hair from skin.

## Hypothesis E: cap-to-lock junction

13's restricted patch excluded skin but stretched into visible stripes. 14 replaced it with edge-blended dark support and swept fibers; 15 moved the upper hood lip toward that junction. The visible brown cap still reads as a separate panel. Do not call this accepted merely because the source face passes checks. Next narrowly scoped correction removes the opaque cap from rendering, retains its swept fibers with more irregular flow, and changes the hood lip using its actual transformed position rather than the earlier incorrect source-front assumption. Continue visual checks of all three views before claiming completion.

## Selected review candidate: 18

16 removed the cap but left hair outside the pulled-forward hood. 17 added a hidden scalp-clearance envelope and outside-only Shrinkwrap limited to the upper hood. 18 reduced excessive rear depth of the physical hair cohorts and lowered the high outside shoulder lip. These changes address observed intersections without changing the face.

**Disposition: YELLOW, selected static dressing review candidate.** The loose indigo veil, chestnut waves, exposed jaw/neck and diagonal shoulder drape now substantially approach the approved portrait direction. This is the preferred working derivative, not a claim that the exact portrait has been reconstructed or a production-ready character delivered. All six final images (wide and portrait-format front/left/right) were visually inspected. Remaining visible differences: the original painted scalp and native side strands have different detail/flow; the hair is more orderly than the illustration; the shoulder folds are still bulkier and their surface more mottled. The pre-existing smooth lower neck and bust join are visible; they were not silently repainted or resculpted during this dressing task. Do not describe remaining differences as lighting alone.

Paths relative to `.runtime/art-direction/series01-facebuilder-trial-01/`:

- **Native working scene:** `reference-dress-18/dressed.blend`.
- Wide diagnostics: `reference-dress-18/{front,left,right}.png`, 640×800.
- Larger review: `reference-portraits-18/{front,left,right}.png`, 955×1647, 64 samples, same camera-relative symmetric lighting. These are narrower portrait framing, not additional geometry improvements. Keep wide diagnostics alongside them.
- Saved-file and protected-face verification: `reference-verify-18/result.json`.
- Candidate build inputs/checks: `reference-dress-18/result.json`.
- Views named left/right are camera azimuths −45°/+45°, not strict 90° profiles. No rear/all-angle qualification.

Native SHA-256: `1fbe41cad8e01cab7d7ef41dee471e9a6aaad2253fb1e2beb4fcf9714da44e0b`.
Approved head SHA-256 remains `c263b6b715548e8fee58661eadd6f26f8b37c81295ae0fcc2c830a3786561322`.
Face geometry/UV/shape-coordinate digest remains `f6a1e3970a74bb325e72a1c0b23c603a34673c225d9b3553b2c8a4a80ea658b6`; shape values and material node/link/default-input signature also pass fresh-process comparison. This is not exhaustive material/pixel equivalence or a proof of collision-free animation.

Implementation checkpoint: `7df3ac3`. 78 scoped unit tests passed across the new handler and existing donor, dressing, matched-light and face-cleanup handlers. Source-pinned structured operations, factory startup, autoexec disabled, credential-free environment; no runtime model-generated scripts. Native worker permission is not an OS sandbox qualification. Final portrait rendering and verification reopen the saved scene rather than reconstruct a visually different scene for presentation.

## Attribution, limitations and next use

Donor: “Hijab” by lam_m_zack, [source](https://sketchfab.com/3d-models/hijab-ee50e01adc864ccc880caed9b5eb3bcb), CC BY 4.0. Changes: mannequin removed, garment split, extended/deformed, shell repaired, recolored, fitted. Preserve credit with distribution. Final visible hair is locally authored native geometry plus the original head's painted scalp; the rejected variant 05 used 04saken CC BY 4.0 texture. Final cloth reuses the approved project illustrations as packed material inputs, without changing their image files. Its projected shadows are **baked illustrated shading, not recovered lighting-free albedo**. The blue mask is heuristic, not reliable semantic segmentation.

The bust support is a fitting aid, not approved full-body costume. No cloth/hair dynamics, retopology for deformation, facial expressions, eyes/blink, full-body rig, lighting-change robustness or galloping integration qualified. Preserve portrait B and bilateral-04 as authorities. Do not silently promote candidate 18 to Director-approved canon or declare the overall likeness experiment complete. Review this materially improved dressing silhouette before body/rig integration; any later exposed neck/body seam correction is separate from the approved facial identity.

## Efficiency and durability

18 inexpensive variants were retained, including failures. This was more iteration than forecast: broad geometric guesses and color-threshold material transfer repeatedly produced a plausible front with side-view defects. The successful diagnostic was explicit upper-hood clearance plus inspection of both sides, not another prompt or paid asset. Future grooming work should begin with a scalp/hair/cloth coverage and clearance map and evaluate small junction crops before another full set of variants. Freeze the successful drape while improving hair, rather than changing both together. Do not convert this single run into a controlled model benchmark.

The 30–45-minute/250-MB forecast was exceeded. Final scope was narrowed to one clearance correction, saved-scene verification and three larger review renders; no new sourcing, purchases, paid calls, rig or body campaign. Preserved reference-candidate/review evidence totals 324,001,014 bytes (about 324 MB); no earlier files deleted. The 21 recorded native jobs completed with no unmatched job starts and totaled 415.0 process-seconds; this excludes engineering, inspection, tests and documentation and is not total effort. Work began at 2026-09-20 00:56:45 UTC; the ledger records the work-end and excluded Director-review wait separately. Engineering token consumption remains unknown. Native assets and the operating ledger are ignored by Git and **not backed up remotely by local source/docs commits**. No remote push or upload was performed. Planning counter remains 119.
