# 3D-05 attempt history and closure status

The original scored campaign remains YELLOW. Development acceptance does not substitute for complete scored Director review and machine acceptance. Every original run remains at its original path; newer measurements never replace historical verdicts.

| Run or group | Outcome / reason for next attempt |
| --- | --- |
| `interaction-v1-20260911T042855Z-d0b75f25` | RED / Director rejected horizontal sword and obscured grasp views. |
| `interaction-v1-20260911T132551Z-1835c73e` | RED / hand entered handle, unnatural pregrasp posture. |
| `interaction-v1-20260911T143452Z-281f2ecf` | RED / closed fist touched rather than enclosed handle. User requested Astra diagnosis. |
| `interaction-v1-20260911T151105Z-b556e5e5` | RED / enclosure improved, but thumb-down/backward acquisition rejected. |
| `interaction-v1-20260911T160515Z-85655dd3` | YELLOW / rigid lift, elbow distortion and missing head attention prompted coordinated motion plan. |
| `coordinated-validation/interaction-v1-20260911T165641Z-6f92e608` | Development playback accepted with 0.5-point forehead-proximity deduction; no invented absolute score or review duration. Full reach deformation still failed (1.821×). Original diagnostic result and additive acceptance both preserved. |
| `closure-reach-v1` | Read-only edge/triangle/weight/bone diagnostic localized the reach failure around frames 16–24. No skin weights or thresholds changed. |
| `closure-reach-*`, `closure-pole*`, `closure-lateral*`, `closure-attention*`, `closure-settled*` | Bounded unscored routing/staging probes. Some improved edge stretch while causing support collision, compression, or inadequate head clearance. These are development evidence, not independent scored trials. |
| `closure-surface-v1`–`v6` | Introduced explicit surface/ownership measurement, refined elbow routing and orientation sequence. Final nearest-normal penetration finding was independently investigated. |
| `closure-penetration-classification`, `closure-penetration-topology` | Original render sword has 26 open edges. A nominal 18.9 mm nearest-normal penetration sample was outside under independent parity. Motivated closed enclosing section proxies; visible contact/enclosure still measured on render geometry. |
| `closure-surface-v7` | Closed proxies exposed inadequate conservative head clearance. |
| `closure-surface-v8` | Improved outward contact tilt/head clearance; small guard–hand crossings during alignment and a skin compression failure remained. |
| `closure-surface-v9` | Larger pregrasp clearance fixed guard crossing but compressed reach skin below 0.35×. |
| `closure-surface-v10` | Restored early 6 cm pregrasp route and added a temporary 2 cm alignment standoff at frames 24–32. Both timing variants pass all preflight motion, surface, grasp and evaluated ownership checks. Complete 96-frame, three-view inexpensive preview generated. Subsequent full native preflight passed: six checkpoint/reopen pairs, semantic and metric-identical replay, and all 18 real control sensitivities. Fresh scored Director qualification remains pending. |
| `closure-native-v10/interaction-v1-20260911T192603Z-96145c4f` | Partial run stopped by existing 5 GB disk guard during checkpoints; see actual `ABORTED.json` for identity. No evidence deleted. Restart uses a new run directory. |

Historical scored runs are under `runs/3d05/`; development groups are under `runs/3d05-development/`. Closure input revisions are preserved in `prototypes/closure-v1` through `closure-v10`. Some early closure probes predate the exact source commit and have native/job/config evidence but no independently frozen complete source tree. Do not retroactively claim exact source attribution for those probes. Full native preflight uses source commit `75b18bf`; its work package records the exact dispatch binding.

## Durability and economics

Source history through `54878e1` was pushed to the user-confirmed `arshargithub/MovieUniverseFactory` destination using the working Git credential helper. The separate configured API token returned HTTP 401; expiry was not established. A verified historical native/image backup contains 10,412 files, approximately 2.33 GB compressed, in `exports/3d05-development-backup-20260911T181445Z`. Upload as a draft release in the public repository awaits explicit approval; local preservation is not described as off-machine preservation.

Native runs retain elapsed timing in runner/status evidence. Provider calls and API cost are zero for this closure work. Historical human review time and interactive engineering time were not measured; total production economics remain incomplete. The next scored review must record its duration.

Verified APFS copy-on-write sharing recovered storage from byte-identical native/image/JSON files. Each path and content SHA-256 is preserved, and future writes remain independent. Receipts are `runs/3d05-development/storage-clone-receipt.json` and `storage-clone-json-receipt.json`. This is storage sharing, not evidence pruning.

## Reusable lessons

Plan human movement and fixture fit before fine joint edits. Validate contact surfaces and enclosure independently of anchors. Separate comfortable staging from nonintersection. Probe fractional times around coordinate/ownership changes. Negative controls must produce a targeted failure absent from the positive case. Retain fixture and measurement assumptions, particularly open surfaces and conservative collision proxies. Model-switch history is useful process intelligence, but the changed fixtures, constraints, measurements and Director feedback prevent attributing improvement to model choice alone.
