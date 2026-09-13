# Rough-cut process review

The authorized target was a complete 24-second, four-shot film, including a gallop refinement, meadow/dust contrast, moving cameras, signal/reaction and provisional sound. The Director explicitly approved sustained work within four hours of engineering and four hours of native compute. This is a larger integration task than the earlier isolated gesture experiments. No further creative micro-approval was requested during production.

## What consumed work

- The continuous motion build evaluated and baked 576 frames at fractional intervals; its native process took approximately 11.3 minutes. Contact validation then sampled all 4,609 eighth-frame positions, including the unrendered end boundary.
- The first paid world proposal exhausted its output limit and was unusable. Its cost is counted. A bounded retry completed, then repository review corrected Blender API assumptions before native execution. A plane dimensionality error survived review and was caught by the native worker. The failure was preserved.
- Camera preflight exposed real composition problems: an undersized/cropped signal reaction, insufficient forward room in the lateral view, and a destination leaving the departure frame. Four world variants, including small framing refinements, were retained. The final extreme frames were checked before the full render. No gallop redesign followed the validated motion build.
- A missing helper import in the new validation dispatcher was caught before asset evaluation; the failed job and corrected rerun are retained.
- Available disk fell by about 2 GiB during the initial two-render-worker attempt, beyond the artifact forecast. This is consistent with native memory/swap pressure; no before/after RSS and swap time series was captured, so the exact attribution is an inference. The 5 GiB reserve correctly stopped both workers. Lossless round-trip-verified compression preserved the new intermediate scenes, and rendering resumed with one worker. This was an operational failure of the concurrency forecast, not an animation validation failure.
- Full image rendering and media assembly are separately recorded in the job ledger. Their durations are not described as model thinking or hidden inside API cost.

## Lessons for the Factory

1. Budget **peak memory and swap as well as final artifact bytes** before choosing native concurrency. Two Blender processes on this 16 GB Mac were counterproductive. Start with one measured worker unless a representative two-worker test demonstrates sufficient headroom.
2. Save new intermediate Blender scenes compressed from the outset. Preserve source bytes and hashes when archiving an existing scene; compression is not permission to discard failed evidence.
3. Use camera/frustum checks and representative extremes before all-frame rendering. A compositional critique can help prioritize changes, but stills cannot establish motion credibility or a readable temporal reaction.
4. Split paid implementation requests into bounded pieces or provide sufficient output allowance. Count incomplete outputs, retries, and reasoning. The proposal is input to a reviewed fixed handler, never directly executed.
5. Preserve the difference between a mathematical timing repair and a Director-confirmed improvement. The recovery warp passes monotonicity/support-boundary tests; whether the apex now feels right remains a playback judgment.
6. Keep simple original sound available as a fallback. Contact-timed synthesis avoided acquisition and licensing delays; its realism remains provisional.

`operating-summary.json` gives the final measured local process totals and conservative authorization-to-yield elapsed time. Subscription token usage and pure active-thinking time are unknown; no API-equivalent subscription cost is invented. Engineering-model changes are not isolated causal experiments. The paid Sol Medium proposal, supervisor corrections, altered staging, controls, and Director feedback must not be collapsed into a model-quality benchmark.
