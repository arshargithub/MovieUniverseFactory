# Combined full-pace pass — blocked checkpoint

**YELLOW overall / authored full-pace motion NOT QUALIFIED. No combined tail/dust playback was produced.** Previous head, camera and intermediate-motion results remain intact. Do not describe the new source files as a completed or accepted performance.

## Completed work and evidence

The Director authorized one combined full-pace extended-stride, flowing-tail and trailing-dust preview. Existing assets and rig were retained. One generic paid Astra High design request supplied mathematical guidance for an explicitly authored gait; no scene samples or asset data were sent. Its result was reviewed and translated into fixed repository handlers. [Design response](fullpace-design-response.json) · [motion contract](../../../feasibility/demonstrator-01/FULL_PACE_PASS.md).

The proposed gait uses 12 m/s travel and 2.4 cycles/s, giving a 5 m stride, with explicit ground anchors and Hermite recovery. It is a new authored gait, not a larger contact correction to the old source motion. Three bounded native variants were attempted:

| Variant | Main change | Maximum near-floor travel | Reported deform-segment ratios | Disposition |
|---|---|---:|---:|---|
| 1 | Authored contacts, recovery and load-derived heave | 50.47 mm | 0.730–1.295 | Failed screen; no full render |
| 2 | Disable IK stretch, lower body reference, tighter stance/recovery | 35.43 mm | 0.428–1.046 | Failed screen; forefoot recovery localized |
| 3 | Coordinate foot and existing heel controls using reference phase | 34.67 mm | 0.766–1.214 | Failed current screen; independent audit pending |

The retained segment limits were 0.97–1.03; floor penetration <=20 mm and near-floor travel <=50 mm. Accurate hoof targets did not establish acceptable deformation. Small pose images were rendered to inspect failures; no failed candidate received a complete animation render. [Variant 1](../../../runs/demonstrator-01/fullpace-probe/checks.json) · [Variant 2](../../../runs/demonstrator-01/fullpace-probe2/checks.json) · [Variant 3](../../../runs/demonstrator-01/fullpace-probe3/checks.json).

## Measurement concern and external blocker

The original per-frame comparison captures a source baseline after earlier loop iterations have changed control rotation modes. That can prevent source Euler animation from restoring the intended reference state. Consequently, the reported ratios are failed development screens, **not yet an independently proven diagnosis of the asset's deformation limit**. This concern must not be used to wave away a failure or declare success.

A separate fixed handler reconstructs the exact third candidate from hash-bound authoring records and compares it with clean source measurements captured before candidate pose writes. It changes no gait parameters. That audit did not execute: the existing runner refused because the output volume had less than 5 GB free (approximately 4.6 GiB displayed by `df`). No limit was lowered and no evidence was deleted. Its implementation is unvalidated until the native audit runs.

The three-variant checkpoint is reached. No fourth gait variant is authorized by this pass. After disk headroom is restored, the first action should be this small independent audit, followed by a scope decision based on its evidence—not another automatic cycle of gait tuning.

## Tail, dust and unfinished work

`fullpace_fx.py` contains a drafted deterministic groom using correlated root-to-tip flow, bounded tapered tips and an explicit tail-root attachment. It also contains ground-anchored noisy dust volumes and sparse ballistic dirt driven by contact times. **These helpers have not run in Blender.** Their API compatibility, appearance, performance, collision behavior and save/reopen behavior remain NOT_RUN. No new tail-only Director review is requested.

A representative dust-frame timing, full combined movie, synchronized dust-free contact view and final native save/reopen therefore remain NOT_RUN. The ultimate full-pace/dust goal is still open. Full-film production remains at the Stage A gate.

## Cost, process and learning

One paid design call cost **$0.394875**, including 5,696 reasoning tokens within 7,822 output tokens. Reasoning is not added a second time to output cost. Campaign calculated total is **$2.550887501**, with no outstanding reservations; no invoice reconciliation. No purchases, paid media or cloud rendering.

The first proposed API dispatch was rejected before execution because approval review questioned scene-derived data and the High route. The revised request sent only a generic question; charter section 6 explicitly authorizes paid Astra High integration design, separate from the Medium supervisor. This resolved that approval issue. The later disk refusal is the runner's existing local guard, not another approval rejection.

The main consumption was supervising design/implementation and diagnosis, rather than render time. The generic design could not account for this rig's multi-stage paw/heel mechanism. The first two variants controlled insufficient parts of that mechanism, and source-reference capture was not sufficiently isolated. Next work should establish clean source-state measurements and the complete limb-control contract before generating a new gait. Repeating source-local cycle keys reduced unnecessary baking, but this does not compensate for an invalid comparison baseline.

Nine pure-math tests pass for stationary support, cycle translation, contact-velocity continuity and periodic bounded heave. Python syntax checks pass for the new helpers. These tests do not qualify Blender deformation, FX appearance or a complete performance. Exact subscription usage is unknown; no token or dollar estimate is fabricated. See the compact summary and operating ledger for recorded activity/native durations.

Recorded activity: **57.9 minutes**; native workers: **5.85 minutes**. [Compact summary](fullpace-summary.json) · [inventory](fullpace-manifest.json). All previous evidence retained; no new large scene/archive was written.
