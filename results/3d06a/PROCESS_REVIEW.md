# 3D-06A process review — pre-Director handoff

The work stayed within a no-prop stationary gesture. A written motion brief and measured fixture board preceded candidate generation. No replacement character or geometry repair was needed. The frozen quality gate explicitly allows a Director tie when the requested timing and non-regression requirements pass.

## Preserved attempts and avoidable costs

1. `screen-20260911T222609Z-70aa786f`: Blender crashed under the sandbox before the worker completed. Preserved; the permitted native invocation succeeded outside the sandbox. Infrastructure time remains part of net experiment time.
2. `screen-20260911T222625Z-370528ef`: admitted fixture, 193 half-frame samples and five landmarks passed. One pose design was sufficient.
3. `preview-20260911T223142Z-279f98ac`: valid positive metrics, but the 480-second deadline stopped rendering with three of 384 images missing. `preview-complete-69aa0805` preserves 381 unchanged images and records a bounded three-frame recovery. Future dispatch used a 900-second deadline based on measured throughput. Lesson: include startup/inspection margin in render forecasts.
4. `qualification-20260911T224552Z-be3ff346`: positive, replay and six persistence checks passed, but connected-bone location controls produced no evaluated movement. Qualification failed correctly; no final images were rendered. Corrected the corruption to rotate joints. Lesson: verify the injected defect exists in evaluated geometry before interpreting detector sensitivity.
5. `qualification-20260911T224712Z-14675f1c`: short worker error because the new quaternion control lacked its import. This was an implementation oversight, not a motion defect. Preserve it and use a native control smoke check before the next full qualification freeze.
6. `qualification-20260911T224816Z-eddd9200`: corrected controls, unchanged positive motion and unchanged thresholds; numerical qualification passed. Complete render ran only after those gates passed: 384 images, 475.206 seconds including native qualification.

We ran one broad offline suite (160 passed, 11 opt-in/native deselected), followed by two targeted pure timing tests. The native qualification exercised the corrected production controls. Two short failed qualification attempts caused duplicate numerical checks, but did not duplicate expensive final rendering. Preview and scored rendering are separate by the frozen contract; neither preview reuse nor weakened gates were used to reduce reported cost.

## Accounting and interpretation

Prospective ledger starts at 22:21:50 UTC, after initial repository inspection/push; pre-ledger inspection is unmeasured and excluded from claims of exact whole-task totals. The operating summary reports the captured window, ongoing native jobs, phases, and coverage. Work intervals are assistant task occupancy, not measured model compute. Native sums are process-seconds, not CPU core-seconds. Job completion records describe worker execution; the campaign result separately identifies technical qualification failure.

Optional task-local token import is bounded and partial. It retains numeric usage and model-setting metadata only. Cached/reasoning tokens are subsets, not extra charges. Runtime metadata observed Astra Medium; no engineering model switch occurred in this episode, and this is not a controlled model comparison. Factory API calls/cost are zero; subscription dollar allocation and complete engineering-token totals remain unknown. Manual reference-board design is included in assistant work, not fabricated human acquisition time. Director review time is pending.

At the next freeze: retain fixture screening, test that each native corruption visibly/measurably changes the intended observable, run a short native smoke check after adding Blender-only imports, and forecast rendering from actual frame throughput with margin. Do not change numerical thresholds to rescue failures.

The observed usage includes repeated large context inputs from this long-running task; most observed input tokens are cached. These are reported request-token totals, not unique text or new reasoning, and cannot be translated into subscription charges or quota consumption. A fresh next-experiment task with a compact accepted-fixture briefing should reduce unnecessary inherited context. This is a process recommendation, not a measured model-quality comparison.

A clock inconsistency was observed during final rendering: wall timestamps advanced about 69 minutes while the native monotonic timer advanced 311 seconds. Cause is UNKNOWN (clock adjustment/suspension was not independently established). This is not recorded as excluded Director wait. Whole-episode net time remains uncertain; native monotonic duration is reported separately. See `clock-observation.json`. The planned one-gesture scope remained unchanged at this checkpoint.
