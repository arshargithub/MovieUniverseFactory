# 3D-05 closure campaign — pending Director review

**YELLOW: all technical gates pass; fresh Director scores and review duration are missing.** This is a new scored campaign, separate from the earlier YELLOW campaign and accepted development preview. No GREEN closure tag or claim is implied.

Review the [complete anonymous A/B videos](../../../runs/3d05-closure/interaction-v1-20260911T194804Z-9aafbc8a/review/video.html), or [primary](../../../runs/3d05-closure/interaction-v1-20260911T194804Z-9aafbc8a/review/primary-AB.mp4), [side](../../../runs/3d05-closure/interaction-v1-20260911T194804Z-9aafbc8a/review/side-AB.mp4), [rear](../../../runs/3d05-closure/interaction-v1-20260911T194804Z-9aafbc8a/review/rear-AB.mp4). A is left and B right in each video. Both variants already include the coordinated motion and head attention; the scored revision advances grasp/lift/hold timing only. The original [frame player](../../../runs/3d05-closure/interaction-v1-20260911T194804Z-9aafbc8a/review/index.html) remains available. Each view contains all 96 frames at 24 fps (four seconds); replay resets to the initial state and is not a seamless motion loop.

## Repair and independent evidence

The early reach was diagnosed using measured elbow edges, neighboring triangles, bone transforms and weights. We changed the approach route and delayed handle-orientation alignment, adding a temporary 2 cm standoff during alignment. The coordinated hand/forearm lift and head-attention design remain; the sword tilt and held position changed to improve clearance. Topology, weights and frozen deformation limits were retained.

The scored elbow-edge range is 0.35338–1.46908× against unchanged limits 0.35–1.50×. The prior rejected reach maximum was 1.821×. This is a 26-edge fixture regression screen, not proof of arbitrary skin quality. The conservative minimum head clearance is 0.13039 m against a separately declared 0.12 m staging target; comfortable appearance still requires Director judgment.

Both variants are measured with explicit handle/guard/blade regions and closed convex section proxies enclosing the visible geometry. The original sword has open edges; a nearest-normal penetration false positive was independently diagnosed before introducing closed proxies. Contact and angular enclosure continue to use actual rendered surfaces. Conservative triangle covers, narrow-phase intersections and containment supplement sampled contact. The method's admitted-fixture assumptions and conservative nature are explicit in the [closure contract](../../../feasibility/3d/3d-05/closure/SPEC.md).

Evaluated constraints—not schedule labels alone—establish ownership. The full scored run passed six checkpoint/reopen pairs, exact semantic reopen/rebuild and metric-identical replay. All 18 real Blender failure controls triggered their designated errors absent from the positive scene. The preflight blade-interior control passed the old vertex check at 0.10936 m while the surface test detected 84 forbidden intersections. The dual-owner control failed only the evaluated-owner gate.

## Provenance, validation and playback

Clean scored dispatch commit: `1bc89a30028516ac0a08480148c17221c6c11bb7`. Implementation freeze: `b1f1571`; the dispatch commit adds frozen configuration only. Campaign JSON records baseline native/asset hashes, scene/revision digests, exact Blender 5.2.1 LTS build `9e2066aef7ef`, render profile and zero provider budget. The [verified summary](summary.json) records the full run manifest digest and 1604 verified artifacts.

The offline suite passes **132 tests**, with 11 opt-in/native tests deselected. Separately, the full native preflight and the fresh scored campaign executed the real persistence/replay and 18-control qualification. Complete scored visual evidence comprises 576 PNGs: 96 frames × two variants × three views.

The frozen player generator requires a complete frame inventory and preloads the images. Added synchronized H.264 convenience copies preserve the original HTML and all source PNGs; ffprobe verifies 96 frames, 24 fps and four seconds for each view. [Video provenance](video-provenance.json) contains input hashes, encoding settings and FFmpeg version. Lossy video copies are review conveniences; PNGs remain exact image evidence. Browser automation could not open the local file URL because of its security policy; no browser workaround was attempted.

## Execution-cost review

The Director reports approximately **2.5 hours and excessive Codex token use**, considered rejecting the pass on process grounds, and chose to capture the learnings. This is recorded as an **execution overrun requiring correction**, independently of the technical pass. See the [process review](PROCESS_REVIEW.md) and [structured feedback](process-review.json). The two full native suites alone took 40.1 minutes; exact total and token attribution were not recorded. Paid API cost of $0 does not represent engineering cost.

## Director gate and economics

Record A and B scores in 0.5 increments for readability, grasp/contact, transition smoothness and hold/clearance, plus preference, visible defects and review seconds. The frozen candidate gate remains ≥4 in each dimension, ≥0.5 readability improvement, no regression elsewhere, candidate preference and zero major defects. A review that does not meet those criteria must remain non-GREEN. The older development pass with a 0.5-point forehead-proximity deduction is preserved; it supplies neither invented absolute scores nor acceptance of this new comparison.

Scored elapsed local wall time: 1529.82 seconds. Known provider calls: **0**; known API cost: **$0.00**. This is not total production cost. Historical human review/engineering time was not measured, and fresh Director review duration is pending. Job elapsed time is not CPU core-seconds.

## Retention and qualification limits

The [attempt history](../../../feasibility/3d/3d-05/ATTEMPT_HISTORY.md) retains rejected poses, unsuitable original handle proportions, failed approach probes, measurement corrections and model attribution limits. The prepared historical archive includes 10,412 files and full native/image evidence. Its public-repository draft upload awaits approval; local preservation is not called off-machine preservation. Source history is pushed separately. Verified copy-on-write storage sharing preserved every affected path and content hash without deleting evidence.

This qualifies progress on one stationary admitted rig, one modified sword, scripted kinematic enclosure/attachment and one bounded timing edit. It does not establish general prop fit, arbitrary skeleton support, physical grasp, release/drop, moving pickup, combat, autonomous creative direction or production rendering. Retain the motion-planning-first workflow, precise asset suitability checks, evaluated ownership, surface-sensitive controls and dense fractional sampling. Engineering-model switches were not controlled experiments and cannot alone explain the improvements.

Before recording a future Director decision, preserve the current pending result/review and manifest, then append the new review evidence and regenerate the final inventory. Only after all frozen Director gates pass should the final GREEN report, evidence tag and authoritative accepted bundle be created.
