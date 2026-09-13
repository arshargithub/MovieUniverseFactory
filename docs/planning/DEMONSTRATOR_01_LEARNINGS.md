# Demonstrator 01 — consolidated learnings and adoption boundary

Recorded: 2026-09-13. Evidence baseline: Director-accepted Courier rough cut, repository commit `34c3b92`. This is a synthesis of existing evidence, not a new scored campaign or a claim that the original charter is fully complete.

## Conclusion

**Recommendation: adopt Blender as the current persistent 3D production backbone and end open-ended Blender qualification.** The accepted integrated cut demonstrates enough to justify this scoped technology choice. It does not qualify arbitrary rigs, photoreal output, autonomous filmmaking, or economical transfer to a new brief. Historical YELLOW/failed results remain unchanged. Record explicit Director adoption separately; this recommendation is not itself that approval.

The next useful question is whether the Factory can reuse this world through bounded controls with less engineering—not whether Blender can render another demonstration.

## Evidence snapshot

- [Accepted report](../../results/demonstrator-01/rough-cut/REPORT.md): four shots, 24 seconds, 576 frames at 24 fps, 960×540, original provisional sound; Director accepted the complete development cut.
- [Acceptance](../../results/demonstrator-01/rough-cut/director-acceptance/acceptance.json): film and scene hash-bound; no invented numerical scores or comprehensive realism claim.
- Independent review verified 1,485 artifact hashes, 720 symlinks, all 32 frozen implementation files, and the accepted film/scene hashes. No missing or mismatched entries were found. The 37 relevant offline tests passed again.
- Independent comparison of the retained preflight and reopened frame-220 images confirmed pixel equality. This was verification of existing replay evidence, not a new Blender render or independent full-scene rebuild.
- [Motion evidence](../../results/demonstrator-01/rough-cut/motion-validation.json): reported 4,609 fractional-time samples, 10.19 mm material hoof travel, no measured floor penetration, 3.55 mm maximum rein gap. [Actual corrupted-motion control](../../results/demonstrator-01/rough-cut/contact-control.json) detects introduced sliding. These measurements are not biological gait certification.
- Review inspected contact/sequence sheets and implementation. Full-speed creative/temporal acceptance comes from the recorded Director playback review, not from the reviewing assistant's still-image inspection.

## Learning delta for the next work

| Finding and evidence | Decision and next-run change | How to verify |
|---|---|---|
| Integrated film exposed composition, continuity, sound, and compute issues absent from isolated poses. [Process review](../../results/demonstrator-01/rough-cut/PROCESS_REVIEW.md) | ADOPT: organize work around a complete viewable deliverable and one clear production question. Stop routine isolated qualification campaigns. | Show the complete cheap preview before final rendering; name the decision it informs. |
| Local foot/heel repair repeatedly failed; restoring complete source control families enabled progress. [Sustained review](../../results/demonstrator-01/stage-a/sustained/PROCESS_REVIEW.md) | ADOPT: inspect dependencies and demonstrate source-state restoration before altering an unfamiliar rig. Preserve rotation modes, mechanism settings, and one owner of world travel. | Reproduce evaluated source poses, then validate coordinated controls and actual mesh motion. |
| Same-frame source-relative shortening compared against a stretched source pose. [Diagnosis](../../results/demonstrator-01/stage-a/FOREFOOT_DIAGNOSIS.md) | ADOPT: distinguish rest length, phase-aware source motion, articulation, and mesh deformation. Do not equate one diagnostic with anatomy. | Explain the measured quantity and use an appropriate positive control before treating a failure as a repair target. |
| Changing near-floor centroid membership distorted contact interpretation. [Final report](../../results/demonstrator-01/rough-cut/REPORT.md) | ADOPT: use fixed material-point evidence for rolling contact, while preserving the historical centroid failure. | Evaluate fractional times and a real path-speed corruption; do not fabricate a failure by editing measured JSON. |
| Initial mesh-negative control missed active shape-key geometry. [Pose repair](../../results/demonstrator-01/stage-a/FOREFOOT_POSE_REPAIR.md) | ADOPT: prove a corruption reaches the evaluated output, not merely source data. | Clean positive passes; intended corrupt evaluated geometry fails for the targeted reason. |
| Valid frame/timing math did not prove the perceived foreleg hitch was gone. | ADOPT: separate media integrity, motion measurements, and Director acceptance. Do not repair an accepted clip solely to eliminate a diagnostic. | Full playback acceptance and explicit limitation statement alongside numerical tests. |
| Early rendering preceded complete framing/temporal checks; expensive Cycles volume trial was unsuitable. | ADOPT: test intended renderer, camera extremes, and a complete cheap segment before committing frames. | Record measured frame cost and render forecast; reuse unaffected frames. |
| Two workers hit the disk reserve on the 16 GB machine. [Process review](../../results/demonstrator-01/rough-cut/PROCESS_REVIEW.md) | ADOPT: start with one worker, compressed new scenes, and memory/storage headroom. Exact swap attribution was not measured. | Demonstrate headroom before increasing concurrency; retain failed jobs and avoid double-counting overlapping durations. |
| Final world/shot logic remains fixture-specific. [Implementation](../../src/movie_factory/adapters/blender/demo_cut_world.py) | ADOPT: test a new shot and subsequent direction through a frozen minimal control interface. Do not mistake code-assisted revisions for runtime generalization. | Record source digest before/after the held-out request and count every code/manual intervention. |
| Paid proposals required supervisor corrections and retries. | ADOPT: give paid workers focused work packages and testable outputs; supervise rather than repeat their reasoning. No model superiority claim. | Record proposal accepted/modified/rejected, repair cause, API charges, and remaining supervisor effort. |
| Exact whole-demonstrator engineering/subscription usage remains unknown. | ADOPT prospectively; DEFER historical reconstruction. | Capture monotonic active intervals, waits, native process time, API usage, and coverage. Never infer experiment tokens from account percentages. |

## Economics: what may be claimed

The final recorded snapshot contains 17 paid requests and **$3.736270001 calculated cumulative cost**, including failures/retries, with no unresolved reservations. The rough-cut increment is **$0.513970**. These are conservative ledger calculations, not a reconciled invoice. The original $100 ceiling was subsequently constrained; the final rough-cut authorization uses an effective cumulative ceiling of $13.222300001. Do not treat unused original allowance as renewed authority for future work.

The rough-cut authorization-to-finalization envelope is approximately **102.3 minutes**; native process time totals **81.4 minutes**, overlapping that envelope. Neither is total demonstrator engineering time. Earlier repair activity, historical clock discontinuities, subscription consumption, and pure active engineering remain incompletely measured. No claim of cheap total production or successful subscription savings is supported.

## Capability boundary and remaining work

Demonstrated: one persistent world with admitted modified horse/rider fixtures, coordinated authored motion, four cameras/shots, procedural scenery, bounded dust/tail effects, provisional sound/editing, local preservation, selected-frame reproduction, and accepted integrated playback.

Not demonstrated: parameter-only post-baseline direction, held-out additional-shot reuse, arbitrary assets/rigs, reference-faithful choreography, production realism, physical hair/fluid simulation, off-machine restore, or repeatable low engineering cost. The existing scenery is visibly simplified. Higher resolution alone will not qualify its look.

Small closure actions: add one current authoritative index; explicitly map original charter items to completed/deferred/untested; reconcile lifecycle status without inventing missing timestamps; add a current asset record without overwriting candidate history; resolve horse upstream provenance before distribution; arrange separately approved private backup. Do not rebuild large archives or rerender to perform bookkeeping.

## Next decision

Follow [the closure and reuse handoff](DEMONSTRATOR_01_CLOSURE_AND_REUSE_SPEC.md). Treat Blender adoption, accepted rough-cut closure, and Factory reuse qualification as separate decisions. A failed reuse check does not automatically reopen Blender selection. If reuse works, the next production investment is a short look-quality pilot using working motion—not another horse repair or another engine without a demonstrated reason.
