# 3D-04 — Timeline-local performance revision

## Question

Can Movie Factory improve a bounded section of the accepted character's run performance while preserving the motion, character state, camera, lighting, and timing outside the authorized interval?

## Qualification boundary

GREEN qualifies one trusted structured edit on the accepted 3D-03.1 character and run cycle. It does not qualify arbitrary prompts, motion generation, retargeting, horizontal locomotion, other rigs, or unrestricted Blender control.

Development and failure-injection runs are provider-free. A scored run is forbidden until its work package binds the clean implementation commit and tree, `campaign.json` digest, revision digest, baseline native hash, Blender build, and evaluator budget. Failed and superseded attempts remain evidence.

## Frozen baseline and timeline

- Source evidence tag: `3d-03-1-v1-green-evidence`.
- Native scene: the accepted 3D-03.1 initial scene with SHA-256 `bbf05848c30e531ca31fc4632210b8344f6f35166db9c26abe4adfa6150e2488`.
- Preserve `character_action_run` as the immutable admitted source action. Create separate baseline and candidate 96-frame actions so a local edit cannot mutate the source or every repeated cycle.
- The display timeline contains integer frames 1 through 96 at 24 fps. Each frame is shown for 1/24 second, giving four seconds of playback.
- The admitted run has 16 unique samples plus a duplicate endpoint. The repeated phase at real-valued timeline time `t` is `1 + ((t - 1) mod 16)`; the duplicate source endpoint is never an additional held playback frame.
- Freeze camera B, lights, world, skin, rig/rest pose, mesh/topology, weights, materials, render settings, and source actions.

## Frozen structured revision

Apply exactly the operation in `revision.json`. It targets the pelvis (`Hips`) in armature-local Z and `Chest` for forward lean. It must not translate the armature object or character root.

The 3.5 cm value is the maximum absolute pelvis correction, not a whole-character lift. The trusted rhythm lowers the pelvis during planted support and returns it to the baseline height during flight; it does not lengthen a straight support leg. During baseline support contact, a deterministic two-bone leg solve compensates the affected `UpLeg` and `Leg` chain and holds the support ankle on its baseline world-space trajectory. The foot rotation remains the baseline rotation. When neither foot is in contact, no leg lock is applied. Temporary solving helpers and constraints must be removed before save; only baked action curves may persist.

Support contact is determined from the baseline, never from the candidate: a foot is planted when its frozen foot-vertex set has minimum Z at or below 0.045 m. Consecutive planted samples form one contact segment. Because the admitted source is an in-place treadmill cycle, the support foot intentionally travels backward in world space; absolute horizontal travel is recorded but is not unintended slide. The gated slide is the maximum candidate-induced horizontal departure from that baseline support trajectory.

## Exact edit interval and envelope

The authorized interval is the closed real interval `[40, 70]`. The candidate-minus-baseline pose and geometry delta must be zero for every `t <= 40` and every `t >= 70`; the endpoints belong to the interval for authorization but have zero edit weight. No source-action data may change.

Let `S(x) = 6x^5 - 15x^4 + 10x^3`, the quintic smootherstep. The six-frame blend envelope is:

```text
E(t) = 0                         t <= 40
       S((t - 40) / 6)          40 < t < 46
       1                         46 <= t <= 64
       S((70 - t) / 6)          64 < t < 70
       0                         t >= 70
```

Thus `E(40) = E(70) = 0` and `E'(40) = E'(70) = 0`. The implementation must preserve those value and first-derivative conditions in evaluated motion, not merely store matching integer endpoint keys.

Validation samples every integer and half frame. Around each boundary it additionally samples every 1/8 frame on `[38, 42]` and `[68, 72]`. Finite-difference velocity uses `h = 0.125` frame and physical time at 24 fps.

## Numerical acceptance criteria

The thresholds below are frozen in `campaign.json`. Distances are in evaluated world-space metres.

| Gate | GREEN limit |
| --- | ---: |
| Outside-range maximum vertex delta | ≤ 0.000001 m |
| Outside-range RMS vertex delta | ≤ 0.00000025 m |
| Boundary maximum vertex delta at frames 40 and 70 | ≤ 0.000001 m |
| Boundary RMS velocity-change magnitude | ≤ 0.002 m/s |
| Boundary maximum vertex velocity-change magnitude | ≤ 0.010 m/s |
| Floor penetration | no vertex below -0.015 m |
| Candidate-induced support-foot horizontal slide | ≤ 0.005 m |
| Candidate slide regression versus baseline | ≤ 0.005 m per segment |
| Baseline contact retained by candidate | foot minimum Z ≤ 0.060 m |
| Limb-length relative error | ≤ 0.01 |
| Adjacent-frame maximum vertex displacement | ≤ 0.45 m |
| Adjacent-frame RMS vertex displacement | ≤ 0.18 m |
| Meaningful edited-core maximum RMS vertex delta | ≥ 0.012 m |
| Meaningful edited-core maximum vertex delta | ≥ 0.025 m |
| Achieved peak forward chest lean | 4.0° to 6.5° |
| Achieved peak absolute pelvis correction | 0.025 m to 0.0355 m |

The edited core is frames 46–64. Passing the minimum-change gates does not establish creative improvement; it only rejects a no-op or imperceptibly small implementation.

Exact equality applies to semantic identifiers, source-action curves and metadata, topology, vertex groups and weights, materials and packed-image hashes, cameras, lights, world, render settings, and all protected custom properties. Numerical tolerances apply only to evaluated candidate geometry, foot/contact measurements, and finite-difference velocities explicitly listed above. Save/reopen and offline replay must reproduce the candidate semantic snapshot exactly and the evaluated geometry within the same tolerances.

## Comparison and negative controls

- Preserve the original repeating baseline action and compare it with a separate candidate action on the same scene, rig, timeline, camera, and render settings.
- A no-op control must preserve geometry within the outside-range tolerances and fail both minimum meaningful-change gates.
- An `edit_every_cycle` control must fail outside-range preservation.
- A `boundary_leakage` control with a nonzero boundary weight or slope must fail a boundary gate.
- A `support_foot_slide` control must fail the candidate-induced or regression foot-slide gate.
- Controls use trusted deterministic corruption modes, remain clearly labelled as controls, and never enter Director scoring.

## Director comparison contract

Render synchronized A/B clips with identical frame count, frame rate, camera, lighting, resolution, and starting frame. The review page identifies them only as A and B and starts them together. The mapping is frozen before rendering, recorded in a separate blind-key artifact, and revealed only after the Director submits ratings.

The Director records, for each anonymously labelled clip:

1. run readability, 1–5 in 0.5 increments;
2. foot-contact quality, 1–5 in 0.5 increments;
3. transition smoothness through both boundaries, 1–5 in 0.5 increments;
4. concrete visible defects;
5. overall preference: A, B, or tie.

Creative improvement passes only when the candidate's run-readability score exceeds baseline by at least 0.5, candidate contact quality is at least 4.0 and no lower than baseline, candidate transition smoothness is at least 4.0, the candidate is preferred, and no major defect is recorded. The mapping and this rule are frozen before review. Contact sheets may support inspection but cannot replace synchronized complete playback.

## Cost and provenance

Record total elapsed and Blender compute time, human review time when provided, provider calls, known API cost, and cost per accepted second. The frozen development budget is zero provider calls and USD 0.00. Any scored secondary evaluator requires a new pre-run frozen model, reasoning effort, media detail, prompt and schema digests, maximum call count, pricebook digest, and USD ceiling. It remains advisory and cannot override deterministic failure or replace Director review.

## Gates

- **GREEN:** provenance is exact; every deterministic, control, persistence, replay, cost, and Director improvement gate passes.
- **YELLOW:** engineering gates pass but Director review is pending, tied, or the frozen creative improvement rule is not met without a material defect.
- **RED:** any protected state or outside-range change, source-action mutation, boundary pop, failed control sensitivity, foot-slide/contact regression, penetration, invalid timing/deformation, replay drift, budget violation, or Director rejection.

## Non-goals

This experiment does not qualify arbitrary natural-language animation editing, new action generation, general inverse kinematics, retargeting, horizontal locomotion, character-prop interaction, facial acting, cloth/hair, or production-quality performance.
