# Existing-free-asset repair — Stage A review packet

**YELLOW overall / RED dense hoof-contact screen. Full production has not started and scope cannot be frozen yet.** The existing horse and knight now have a complete repaired 2.5-second gallop in two views. [Synchronized before/after playback](../../../runs/demonstrator-01/free-motion-v2-retry/review.html) · [lateral MP4](../../../runs/demonstrator-01/free-motion-v2-retry/lateral.mp4) · [contact MP4](../../../runs/demonstrator-01/free-motion-v2-retry/threequarter.mp4).

## Changes and evidence

- Disabled the source tail's stale hair dynamics while retaining the visible groom. Disabled identified obsolete tack bindings and used an explicit rigid saddle frame following the horse's torso. Original downloads remain unchanged.
- Coordinated rider controls around the stable saddle frame, preserving limb lengths and head orientation. Replaced the source simulated reins in the disposable candidate with deterministic hand-to-bit curves. This establishes endpoints, not physical grasping.
- Fitted travel to evaluated source hoof samples at **3.45427 m/s**. A single speed still allowed **0.5220 m** of stance travel, so that attempt was stopped and retained.
- Added a separate existing-IK horizontal contact layer with short blends; preserved source vertical motion and the original gallop action hash. Maximum applied correction **0.2610 m**, below the 0.30 m adaptation cap. Sampled deform-bone length ratios relative to source range **0.9639–1.0083**. These are adaptation checks, not skin-quality proof.

## Remaining blocker

The half-frame candidate screen reported only 0.000011 m of stance travel. The saved-scene eighth-frame test instead finds **0.220464 m**, above the unchanged 0.05 m screen. The worst segment is rear-right **frames 1.375–3.25**, repeating every ten frames. The overlay had inferred support only at 1.5–3.0 from coarse source samples; the actual near-floor interval extends into its blends. Front-right also travels about 0.122 m across 3.625–7.25. This localizes the failure to contact transition coverage; it is not evidence that the render or preserved action is corrupt. No limit was raised and no fractional samples were discarded.

A future bounded correction should derive support onset/exit from dense source geometry first, then refit the contact envelope and prove correction/reach limits before rendering. There is no further iteration or production authorization implied here. The repaired movies remain useful development evidence, not an accepted solution.

## Numerical screens and limitations

| Check | Result | Frozen development limit |
|---|---:|---:|
| Stance excursion, reopened scene, eighth-frame sampling | **0.220464 m — FAIL** | 0.05 m |
| Hoof penetration | 0.001692 m | 0.02 m |
| Hand/rein endpoint error, dense samples | 0.003470 m | 0.01 m |
| Saved/reopened bounds versus authored poses | 0.000001907 m | 0.001 m |
| Repeated isolated-frame horse bounds | 0.000000000 m | 0.001 m |
| Path displacement error | 0.000000477 m | 0.001 m |

The native doubled-travel and displaced-rein controls both fail as intended. Source FOLLOW_PATH is muted; one external path owns travel. No invalid object drivers are reported. All sampled bounds are finite. **17 focused offline tests passed.** Full videos each contain 60 frames at 24 fps, 2.5 seconds, with no duplicate terminal frame.

The dense saved-scene check samples **0–59 every 0.125 frame**, distinct from quarter-frame overlay keys. The sole estimator uses the lowest decile of evaluated vertices weighted to hoof groups; patch membership can change with orientation. It is also used in calibration, so small residuals are not independent collision proof. Boot/stirrup surface fit, hand enclosure, body/tack intersections, skin deformation and hair-strand continuity remain **unqualified**. Mesh-bound repeatability excludes rendered strands. Velocity/acceleration quality is not established by positional continuity alone. Source dependency warnings are retained; a clean error counter is not a qualification claim.

The current knight is visibly stylized. Realistic proportions, final materials, landscape, dust, signal/story, audio and editing remain unqualified. Accepting this motion does not silently waive the charter's visual brief. No hidden distant framing or finishing was used to conceal the contact view.

## Time, money and production forecast

- This repair pass: **$0.8297 calculated API cost** across two paid work items and one retry. Entire demonstrator so far: **$2.1560**, zero open reservations, against the $100 ceiling. These are conservative local calculations, not invoice reconciliation. Purchases, paid media and cloud rendering: $0.
- Candidate worker: **6.84 minutes**, including two views; **6.51 minutes** rendering 120 frames. Mean diagnostic frame: **3.25 seconds** at 640×360, Cycles CPU, 8 samples.
- All native attempts in this repair pass, including failures: **11.39 process-minutes** against 15 allowed. See [compact job record](free-repair-summary.json). Recorded engineering activity interval: **44.2 minutes** against 60 allowed (includes overlapping native jobs and provider waits, not token-generation time); no invented subscription-token cost. Director review duration remains unknown until supplied.
- Representative repaired-scene frame at **1280×720 / 24 samples: 7.51 seconds**. At that exact complexity, 576 frames imply **1.20 hours** for one pass. A planning factor of 1.5 for scene growth and a further 1.5 for partial rerenders gives **2.70 hours**; these factors are explicit assumptions, not measurements. One frame is not a production timing guarantee.
- At measured 360p settings, 24 seconds imply **31.2 render-minutes** before new scenery and setup. Proposed **next gate**, only after the contact failure is repaired and this motion/look direction is accepted: one complete 24-second four-shot rough cut, at most 60 active engineering minutes and 60 local render-minutes, with a stop if the measured scene exceeds that envelope. Proposed extra API exposure: at most $5, still within the existing $100 ledger. These are proposals, not new authorization.

Do not freeze production while the dense contact screen is RED. The current pass stops with this evidence rather than spending another full render cycle. Do not freeze full-resolution production from this diagnostic frame alone. First agree whether this repaired fixture/look can support the brief, then show the complete rough cut before polish. No asset replacement or purchase is proposed.

## Rework and retained failures

The motion repair itself took several small probes: legacy tail/tack audit; two three-pose rider/rein variants; a full attempt stopped at the failed sole screen; a non-driving hoof-bone probe followed by the actual IK-control probe; then the contact-layer candidate. One sandbox Blender startup crashed before the handler; the authorized credential-free native retry completed. The first dense verification finished sampling but failed JSON serialization of Vector values; the report-only fix required repeating the probe. All are retained and charged to time; none is relabelled a creative success.

The inexpensive first checks prevented completing a known-bad 120-frame render. However, property/API assumptions, source naming, and a basic serialization error still created avoidable supervision/rework. The coarse-screen false confidence is an additional concrete lesson: derive support windows from dense source geometry before fitting a contact layer, and use off-grid validation before the complete render. Future fixture intake should establish the driving controls, effective evaluated sole response, cache policy, and serializable measurement contract before animation assembly. The Astra/Sol collaboration is observational evidence, not proof of model superiority.

Retaining the stopped native scene plus the new scene exceeds the plan's approximately 1 GB storage target (about 1.3 GB before small evidence files). No historical evidence was deleted to meet the target. More than 5 GB free disk remained at the final check. No large export, push or upload was performed.

## Reproduction and provenance

[Code review](FREE_REPAIR_REVIEW.md) · [source snapshot/binding](free-repair-source-binding.json) · [frozen screens](../../../feasibility/demonstrator-01/free-repair-screening.json) · [saved scene](../../../runs/demonstrator-01/free-motion-v2-retry/scene.blend) · [reopen evidence](../../../runs/demonstrator-01/free-verify-retry/verification.json) · [720p measurement](../../../runs/demonstrator-01/free-verify-retry/render-measurement.json).

Use this repository's `.venv`, installed Blender and the two hash-admitted local assets. The fixed `demo_free_motion` mode rebuilds in a fresh `runs/demonstrator-01/` output directory using `run_blender` with an empty profile. The fixed `demo_free_verify` mode reads only the exact admitted candidate hash. Source paths remain local fixture bindings; this Stage A packet is not a portable production export. Embedded asset scripts remain disabled; credentials never enter Blender. Source and native hashes are inventoried in the repair manifest, without copying another large archive.

Playback JavaScript passes syntax validation and both MP4 streams are checked. Automated browser playback inspection was blocked by the browser URL policy; no alternate browser/server workaround was attempted. Direct MP4s remain available for Director review. Full-clip acceptance and review duration are pending.

[Checksummed inventory](free-repair-manifest.json): 271 artifacts, retained in place. [Attempt history](free-repair-attempts.json) includes unsuccessful probes and the dense failure.
