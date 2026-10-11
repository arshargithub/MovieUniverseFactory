# Local rendering acceleration investigation

Director exchange210, 2026-10-11. Investigate faster rendering on the current Mac without cloud compute, new purchases, installations or changes to accepted production scenes. This is a diagnostic work package, not a new renderer selection or permission to reduce quality.

## Strategy and protected result

Use the current209 opening and route natives as read-only sources. Preserve their hashes, actor/camera/material state and dependent caches. Render diagnostic outputs separately using trusted fixed-operation handlers, disabled embedded scripts and an environment without project credentials. Keep production defaults unchanged until evidence supports a recommendation.

The Mac reports an Apple M4 with10 CPU cores,8 GPU cores and16GB unified memory; currently on AC power. The older189 device test used two frames, persistent data and sequential CPU/GPU switching in one process. It showed a pale volume rectangle on one GPU image and no consistent timing advantage. Later CPU persistent-data history also produced groom shading regressions. Neither result proves that fresh-process Metal with the current scene will fail.

First inspect current Cycles settings, available Metal options and scene cost. Then compare matched current-scene CPU and isolated Metal renders with persistent data disabled, separating load/evaluation/render and cold/warm timing. Inspect dust-heavy wide coverage and close-character hair/skin; add turn/uphill controls if the opening route is promising. Test MetalRT or persistent data only as discriminating controls, not an uncontrolled settings sweep. Short chronological motion/repeated-frame controls must follow before any recommendation to use an apparently successful configuration in animation.

Quality floor: no new volume bounds, dark groom, lost texture/dust, changed composition or temporal artifacts at normal review size and relevant crops. Small sampling differences between devices are not automatically failures or proof of equivalence; record numerical differences separately from perceptual checks. Compare matched resolution/sample/denoising settings. Fast previews are not final1080×1920 qualification. Reject acceleration if it changes the intended look or creates unstable output.

Record local job time and failures, resource observations and output hashes. One worker at a time to avoid unified-memory pressure. No changes to global Blender preferences, power settings or other applications. No silent fallback counted as GPU success. Exact engineering usage remains unknown when unavailable. Stop a failed route when evidence falsifies it; no arbitrary elapsed-time quality waiver. Recommendations may include safe operating practices and a future final-resolution benchmark rather than a premature production switch.

## Learning and reuse

Apply PL09 visual evidence, PL10 discriminating controls, PL11 pinned dependencies and PL12 measured throughput. Preserve the old GPU failure as evidence; do not generalize it to all hardware/profile combinations. A successful profile must specify source, version, device/MetalRT, sampling, denoising, cache policy, tested frames and limits. It is a candidate reusable render profile, not blanket qualification of every future scene.

## Results

### Hardware and method

Live read-only inspection: MacBook Air/Mac16,12, Apple M4,10 CPU cores (4 performance/6 efficiency),8 GPU cores,16GB unified memory, macOS26.3.1(a). AC power, low-power mode off. Current swap usage during the CPU delivery test was approximately11.9GB; a snapshot does not prove active swapping, thermal throttling or the cause of a particular frame time. No applications were closed or power settings changed.

Blender5.2.1, fixed209 source hashes, six CPU threads, Cycles8 samples, adaptive sampling and OpenImageDenoise retained. Metal profile explicitly selects the M4 GPU, MetalRT ON, persistent data OFF. Each profile starts a fresh Blender process; no mid-process CPU/GPU switch. Source masters and global preferences are not saved. Scene inspection reports14,564 objects,1,160 mesh datablocks and approximately3.59million base vertices; these are not measured render-visible geometry counts. Existing shared meshes mean blind joining/rebuilding geometry is not an evidence-based optimization.

### Measured opening controls

| Workload | CPU | Metal GPU | Interpretation |
|---|---:|---:|---|
| Six432×768 renders, including a repeated frame: render-call total |165.89s|158.25s|No consistent per-frame advantage; individual timings vary. |
| Same six-render process, including launch/load/setup/exit |206.13s|213.87s|GPU was slightly slower end to end at preview size. |
|1080×1920 dust-heavy opening217, render call |84.28s|36.13s|2.33× speed ratio in this control. |
|1080×1920 close-up360, render call |147.19s|30.87s|4.77× speed ratio in this control. |
|Same two high-resolution frames, full process |288.91s|118.71s|2.43× end-to-end speed ratio; about59% less elapsed process time. |

These are single sequential runs on an in-use laptop, not replicated thermally controlled benchmarks. Six-frame preview medians are both about25.4s. The repeated CPU opening changed from21.19s to35.78s in the same process, showing why a cherry-picked frame is misleading. The1080×1920 controls retain the same low8-sample profile: delivery pixel dimensions do not establish a final-quality sampling/temporal profile. Do not extrapolate the two-frame ratio into a guaranteed whole-film deadline.

Matched opening217/300 and close343/349/360 images were inspected on both backends; both high-resolution controls were also viewed directly. No new rectangular dust-volume boundary, missing groom, black groom or material/style shift was visible in these comparisons. Source209's remaining creative status is unchanged. CPU/GPU images are not pixel-identical: high-resolution mean absolute RGB differences are0.0934 and0.2586 on the0–255 scale, with maximum individual-channel differences26 and39. Most differences are small; this is a numerical description, not an automatic visual pass.

Repeat-frame caveat: CPU217 repeats within1/255; Metal217 has17 of331,776 pixels exceeding1/255, maximum5/255, mean absolute difference0.00356/255. Thus the existing strict1/255 replay criterion is **not met by this Metal repeat**, despite no perceptible full-frame change. Preserve that failed strict gate. A production GPU profile needs evidence-backed backend-specific reproducibility validation; do not quietly relax the old criterion or claim bit-identical output.

Evidence: [CPU opening](../../.runtime/art-direction/series01-render210/cpu_open/result.json), [Metal opening](../../.runtime/art-direction/series01-render210/metal_open/result.json), [CPU higher-resolution](../../.runtime/art-direction/series01-render210/cpu_delivery/result.json), [Metal higher-resolution](../../.runtime/art-direction/series01-render210/metal_delivery/result.json). Each record names images, hashes, load/evaluation/render times and the fixed handler snapshot.

### Turn/uphill and chronological results

Matched route frames427/520/620 preserve the CPU appearance in direct comparisons: dust in the frontal turn, cloth/skin/hair in the uphill glance and continuing ride. Render-call totals were60.41s CPU versus46.76s Metal; full processes108.73s versus95.37s, a modest1.14× end-to-end ratio. [CPU route evidence](../../.runtime/art-direction/series01-render210/cpu_route/result.json); [Metal route evidence](../../.runtime/art-direction/series01-render210/metal_route/result.json).

All12 consecutive Metal close frames343–354 were inspected individually in chronological order. No new black/missing groom, gross shading discontinuity or rectangular volume artifact was observed. This is half a second of frame inspection, not real-time playback or full18-second temporal qualification. Fresh-process343 and sequential349 agree with the earlier Metal sparse controls within1/255; that success does not erase the separate217 repeat failure above. [Chronological evidence](../../.runtime/art-direction/series01-render210/metal_motion/result.json).

Eight native jobs completed successfully, including scene inspection;34 rendered image hashes verified. Native process time totals1,381.09s (about23minutes), not CPU core-time or additional time to add to overlapping assistant work. Both protected natives and19 cache references per source were rehashed unchanged. Six focused handler tests pass. Implementation commit `20ee420`; raw handler snapshots preserve earlier and later diagnostic versions. No paid provider calls, remote compute, installation, native publication or production-default change. Exact engineering tokens and subscription cost allocation remain unknown; initial context/hardware inspection preceded lifecycle capture.

Disposition: **investigation complete; YELLOW candidate profile, not production qualification**. The speed/appearance evidence supports further use-specific Metal qualification; strict replay, full-sequence/final-sampling temporal review and replicated throughput remain open. MetalRT OFF, persistent-data ON, alternate CPU-thread counts and appearance-changing shader/engine routes are NOT_RUN, not failures. The current ON/OFF-cache combination answers the first capability question without an uncontrolled settings sweep. The old189 failure's exact cause remains unresolved because source, cache policy and process isolation differ; current success does not establish which variable fixed it.

[Internal visual review](../../.runtime/art-direction/series01-render210/visual-review.json) separates scoped perceptual checks, strict repeat failure and unrun full-sequence qualification. [Operating report](../../.runtime/art-direction/series01-render210/operating-report/REPORT.md) retains the captured lifecycle, jobs and unknown usage; native evidence remains local/ignored and is not backed up by the design commit.

Lifecycle capture covers approximately1,838s of recorded assistant activity overlapping the native jobs, not additive to them. The strict report leaves exact net elapsed UNKNOWN because of an approximately0.085s uncovered event boundary; that is not a30-minute missing interval. Initial pre-capture investigation is also outside this interval. Do not present captured activity as complete turn duration or infer token cost from it.

## Recommendation and remaining qualification

1. **Qualify the isolated Metal/MetalRT ON, persistent-OFF profile for higher-resolution finishing.** It is now a credible local acceleration route, not a theoretical suggestion. Retain CPU fallback. Before promotion, inspect the full actual sequence at the intended final sampling/denoising settings, perform fresh-open representative replay and resolve the strict repeat-pixel criterion with documented evidence. Do not alter identity/materials to conceal a backend defect. Integrate this check with the next needed finishing render instead of launching an unrelated broad renderer campaign.
2. **Do not switch all previews blindly.** The opening preview process was slower on Metal; route controls show only a modest end-to-end benefit. Record a reusable profile by source class and resolution, rather than a universal device rule. Two high-resolution frames cannot forecast an entire episode.
3. **Preserve cache safety.** Persistent data previously caused a demonstrated black-groom regression on CPU. Do not enable it for a nominal speed gain without a dedicated chronological/reopen proof. The present working profile keeps it off.
4. **Keep one worker and leave memory headroom.**16GB unified memory is shared. The observed11.9GB swap footprint warrants avoiding concurrent heavy apps/renders, but does not establish a quantified speed gain from closing them. AC power and low-power mode off were already in place. No automatic application termination, swap deletion or power changes. Thermal/power-controlled repetitions and alternate CPU thread counts remain unmeasured.
5. **Avoid unnecessary rendering before degrading quality.** Use representative integrated frames/short motion for internal diagnosis, reuse exact compatible frames by source/profile hashes, and render the complete sequence when it is ready for the intended review. Preserve whole-sequence inspection at handoff; sparse controls alone missed an earlier groom failure. Profile scene synchronization/geometry/shaders if they remain material after GPU qualification. Current counts do not justify a blind geometry rewrite or losing semantic IDs.
6. **Do not trade away the selected visual language.** Eight samples are already low; reducing sampling, increasing denoising or switching to Eevee is not a free speedup. Volume steps/bounces, object visibility and render-layer reuse can affect dust, shadows, hair and style and need their own discriminating controls if later justified. No such appearance-changing optimization was executed here.

This investigation changes our evidence, not the production masters or defaults. It does not require cloud compute, paid calls, new assets or software installation. Technical context: [Apple M4 MacBook Air specifications](https://support.apple.com/en-us/122209) document the hardware family; actual configuration and renderer capability were read from this machine. Local measurements above, not vendor marketing, support the recommendation.
