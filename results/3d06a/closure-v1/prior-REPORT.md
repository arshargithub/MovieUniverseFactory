# 3D-06A — reference-timed gesture

Qualification: **YELLOW / Director review pending**. Lifecycle: **OPEN**. The latest frozen numerical suite and complete 384-frame render passed. Director acceptance is pending before GREEN. This is a modest, manually authored pose/time reference on the admitted stationary character, not human-video motion extraction or general choreography.

## Evidence

Current run: `runs/3d06a/qualification-20260911T224816Z-eddd9200`. Frozen source/configuration commit: `177802c`; implementation: `a2a83ce`. Exact dependencies and fixture hashes are in [frozen-campaign.json](frozen-campaign.json) and [work-package.json](work-package.json). The admitted packed fixture derives from accepted 3D-03.1. The manual board and complete development preview preceded scored freeze.

| Check | Observed | Frozen requirement |
|---|---:|---:|
| Baseline / revised cue | 47.99 / 43.99 frames | 48 / 44 ±1 frame |
| Outside-interval vertex difference | 0.000000400 m | ≤0.000001 m |
| Boundary position difference | 0.000000184 m | ≤0.00001 m |
| Added boundary velocity | 0.01807 m/s | ≤0.02 m/s |
| Added angular velocity | 1.926°/s | ≤10°/s |
| Maximum support displacement | 0.000000127 m | ≤0.003 m |
| Minimum mesh height | +0.000000061 m | ≥−0.002 m |
| Elbow edge length ratio | 0.6962–1.2097 | 0.35–1.50 |
| Shoulder-relative landmark RMS | 0.000252 m | ≤0.02 m |
| Selected orientation discrepancy | 0.06853° | ≤5° |

All five disposable native controls fail their designated gate: no-op cue, global timing leakage, boundary jump, support-foot drift, and elbow deformation. Their intended failures are absent from the positive case. Six baseline/candidate rest, cue and hold saves reopen with zero sampled vertex difference, exact pose hashes and protected state. Candidate rebuilding reproduces the complete measured result exactly. These are recorded in [controls.json](controls.json), [persistence.json](persistence.json), and [positive.json](positive.json).

The velocity limit is passed with limited margin. Very small fractional-frame finite differences are sensitive to Blender floating-point evaluation; preserve the same sampling and units in subsequent comparisons. We did not raise any numerical limit.

Complete playback: [A/B primary and side player](../../runs/3d06a/qualification-20260911T224816Z-eddd9200/review/index.html). Native rendering completed in 475.206 monotonic seconds. Both MP4s are verified as 96 frames / four seconds; every frame and native checkpoint is bound by [native-artifact-inventory.json](native-artifact-inventory.json).

## Director review

Review the complete synchronized primary and side A/B videos. Score each clip for readability, natural movement, transition smoothness and finish (1–5, half points allowed); record major defects and approximate review seconds. Candidate requires ≥4 in every dimension with no regression from baseline. Preference is optional: a tie is valid. A cyan marker at frame 44 indicates the requested cue. This is a one-shot gesture, not a seamless loop.

No scores or review duration have been inferred. Engineering contact-sheet inspection is not Director playback acceptance.

## Boundaries

This establishes only the measured gates on one small authored gesture and rig. It does not qualify motion capture, human-reference fidelity, broad retargeting, props, combat, expressive finger motion, or production rendering. The 26-edge elbow screen remains a fixture-specific regression test. The temporal warp is evaluated through linear keyed actions; fractional samples numerically test the resulting motion rather than assuming the analytic envelope alone guarantees continuity.

API cost is $0 for the local campaign. Engineering subscription consumption, native wall time, review time and total economics are separate; see the operating report and process review. Existing historical native archives remain local where previously documented; this run does not imply an off-machine archive upload.
