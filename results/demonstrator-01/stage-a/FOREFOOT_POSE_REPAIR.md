# Forefoot pose repair checkpoint

**Repair attempted; pose qualification FAILED. Full-pace remains YELLOW / unqualified.** No complete gait, native scene, tail or dust playback was produced. Original assets, reviewed head/camera/intermediate motion and earlier evidence remain unchanged.

## What changed and what was tested

The pre-dispatch [pose contract](../../../feasibility/demonstrator-01/FOREFOOT_POSE_REPAIR.md) replaces the inappropriate same-frame source-stretch comparison only for this prospective development test. It uses clean source-cycle segment envelopes with 3% allowance, rig-relative articulation ranges with 5-degree margin, and the retained 5% edge/triangle envelope screen. Historical failures are not relabelled. This is a conservative development screen, not proof of universal anatomical limits or final aesthetics.

A deterministic search blends foot translation, orientation and heel control toward the source at the three identified recovery frames. Component-only controls were also measured. A second hypothesis uses evaluated armature-space control poses instead of local bases. Each hypothesis uses at most 21 predetermined interpolation samples per frame. These are disposable unkeyed pose solves, not new full gait variants.

| Recovery frame | Local-basis search | Evaluated-pose search |
|---|---|---|
| 1.875 | No passing pose | No passing pose |
| 3.25 | Pass at 80% source blend | Pass at 100% source blend |
| 3.875 | No passing pose | No passing pose |

The local passing pose changes the hoof recovery position by 0.418 m relative to the previous swing target. It therefore cannot simply replace one key in the old animation. Even the isolated success requires a newly fitted continuous swing path. At the best remaining local solutions, frame 1.875 still has 62 edges / 65 triangles outside the mesh envelope, and frame 3.875 has 21 / 22. Angle and segment-length screens pass there; mesh shape remains the binding screen. The parent-space hypothesis produces essentially the same residual problem and is not a demonstrated repair.

No interpolation limit was loosened. Support-pose compatibility, all-four-leg validation, continuous recovery, contact preservation, save/reopen, full playback and FX remain NOT_RUN. The contract requires all three recovery poses to pass before advancing; that condition was not met.

## Validator control repair

The first attempted 30% local mesh distortion unexpectedly passed because modifying mesh vertex coordinates alone did not change the active shape-key geometry. This was an ineffective negative control, retained in `forefoot-pose`. The corrected control modifies the corresponding coordinates in the shape-key blocks in a disposable copied mesh. It fails on 1,536 edges and 1,619 triangles, while the clean source positive passes. Its bone and angle screens remain passing, so detection is attributable to measured mesh deformation rather than a pre-existing rig failure.

The shape-key driver inventory contains neck/head corrective drivers; it does not establish a forefoot-specific driver fault. Neither parent-space conversion nor this validator repair proves the remaining mesh deviation is an asset defect. The selected weighted region and its boundary must be considered before any anatomical conclusion.

## Disposition and next scope

Stop this interpolation approach at the agreed pose checkpoint. Do not spend on a full gait or dust render to conceal an unresolved screen. No fourth full gait has been authored.

The demonstrated result is narrower than the requested repair: one feasible recovery pose and a trustworthy distortion control. A next motion approach would need source-aware whole-limb articulation and contact constraints, including upstream controls and skin-boundary behavior, rather than more foot/heel blends. This pass does not establish that the existing asset can deliver the requested 12 m/s / 5 m stride. The full-pace objective remains open; no lower speed is silently substituted and no asset purchase is proposed.

## Time, cost and process

Three native jobs completed in 28.064, 32.548 and 25.734 monotonic process seconds: **86.346 seconds total**, under the 120-second native envelope. No paid API calls; campaign calculated cost remains $2.550887501. Subscription token usage is unknown.

**Exact net supervising duration is UNKNOWN because wall-clock timestamps are discontinuous.** Between the first and last native job starts, UTC advances about 70 minutes while the monotonic clock advances about 10.9 minutes. Even the middle job records 285.6 UTC seconds versus 32.6 monotonic seconds. Preserve both; do not claim a 70-minute engineering duration or a proven sub-20-minute exact net total. The initial supervising start did not capture a monotonic timestamp, so an exact activity duration cannot be reconstructed. The next bounded activity should capture a monotonic deadline at its start and enforce checkpoints against it.

The runtime jobs completed successfully, but their semantic pose result is FAILED. These are distinct outcomes. Python syntax checks passed. No unrelated campaign suite was repeated. The corrected source-positive/mesh-negative control is native evidence; it does not establish the repair's success.

[Initial attempt](../../../runs/demonstrator-01/forefoot-pose/pose-results.json) · [Corrected control](../../../runs/demonstrator-01/forefoot-pose-control/pose-results.json) · [Parent-space attempt](../../../runs/demonstrator-01/forefoot-pose-space/pose-results.json) · [Inventory](forefoot-pose-manifest.json)
