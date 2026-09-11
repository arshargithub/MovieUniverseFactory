# 3D-05 — Stationary character–sword pickup

## Question

Can Movie Factory create and persist one scripted kinematic interaction in which the accepted stationary character reaches for the qualified sword, grasps it without a transform jump, lifts it, and holds it, then revise the interaction timing inside one frozen interval without changing motion outside it?

## Qualification boundary

GREEN qualifies one character, the previously admitted CC0 sword asset, one right-hand grip anchor, one scripted pickup with authored closure of its existing thumb/finger controls, and one timing revision. The character root remains stationary. The sword follows authored transforms and a deterministic attachment relationship; no physics simulation decides the grasp.

This experiment does not qualify physical grasping, general finger articulation, release or drop dynamics, moving-character pickups, arbitrary props or rigs, autonomous staging, or natural-language animation editing.

## Frozen inputs

- Character scene: accepted 3D-03.1 native scene, SHA-256 `bbf05848c30e531ca31fc4632210b8344f6f35166db9c26abe4adfa6150e2488`.
- Sword: 3D-02 `weapon-sword.glb`, SHA-256 `8e69eb27977f8c84a9b7cd423cd5830eddcf0d07ac1d7fed1969931387015b28`, normalized to a 1.0 m longest dimension using the qualified import path, then fitted using the explicit section normalization in `scene.json`. The source file remains unchanged. Handle X/Y scale is 0.12, guard X/Y is 0.65/0.35, blade X/Y is 0.75/0.20; guard height is reduced to 0.30 of its original height and blade height compensates to retain the 1.0 m total length. These are asset-specific geometry changes, not a claim that the original oversized handle was graspable.
- Timeline: integer frames 1–96 at 24 fps. Fractional evaluation is required.
- Character lower body, character root, skin, mesh, topology, weights, rest rig, lights, world, render settings, and source actions are protected.
- The primary camera shows the complete character, support, sword, reach, lift, and hold. Dedicated side and rear contact cameras expose the right hand, handle, blade clearance, and attachment transition without the sword hiding the grip in every view.

## Explicit interaction states and ownership

The baseline state machine is:

| State | Frames | Sword owner | Required behavior |
|---|---:|---|---|
| `supported` | 1–16 | `sword_support_01` | Sword is stationary and supported. |
| `reaching` | greater than 16 and less than 40 | `sword_support_01` | Right arm moves toward the frozen grip point; sword remains stationary. |
| `grasped` | 40 through less than 48 | `character_01/right_hand` | Attachment is active; sword remains at the support pose. |
| `lifting` | 48 through less than 68 | `character_01/right_hand` | Hand and sword follow the frozen lift path. |
| `held` | 68–96 | `character_01/right_hand` | Hand and sword remain in the frozen held pose. |

There is exactly one owner at every sampled time. Attachment activates at frame 40. The support ceases to own the sword at the same time; dual ownership and ownerless samples are invalid.

The candidate uses the same state machine with grasp, lift, and held transitions at frames 36, 44, and 64. The supported-to-reaching transition remains frame 16. These earlier times result only from the frozen timing revision below.

## Grip and attachment model

`sword_01` is a semantic root at the handle grip point. The admitted grip centre is `[-0.12, 0.145, -0.135]` in the existing RightHand bone frame (armature-local units). Negative hand X is the fixture's thumb side and points upward. Hand Y is horizontal at a 45° world-Z yaw from world -X. The forearm is rolled toward the hand's neutral rest relationship, while upper-arm roll follows the elbow hinge plane. The elbow position is solved from the two preserved segment lengths, selecting the reachable solution closest to the desired wrist direction.

The support and supported sword are at world X/Y = [-0.50, -0.20] m, 0.10 m inward and 0.28 m forward from the rejected thumb-down attempt. The held grip is [-0.55, -0.20, 1.25] m. Wrist orientation settles by source frame 24. Frames 16–24 interpolate the wrist toward a staging point 0.06 m behind the grip in positive local hand Z, with a smooth world-space clearance bow of [0.08, 0.14, 0.22] m multiplied by `sin(pi * rotation_weight)^2`. The wrist then advances to the handle over frames 24–32. The lower grip position clears the guard; this staging and the approach path are recorded explicitly in `scene.json`.

Index controls open initially and close over source frames 32–40 using a quintic envelope, reaching 0.85 of the admitted idle-pose quaternion rotation. Thumb controls start at 0.35 of that rotation and reach the same 0.85 final curl. The thumb base adds a -45° local-Y clearance rotation multiplied by `1 - closure`, which returns to zero at grasp. This is one authored closure using the admitted controls, not general dexterous grasping. The earlier thumb-down frame and closure are retained in rejected evidence; see [ANATOMY_REPAIR.md](ANATOMY_REPAIR.md).

At attachment the sword must retain its supported world position and blade-up orientation. The world offset used by the location constraint is derived from the frozen hand-local grip point, hand orientation, and armature scale. After grasp the orientation is fixed while the wrist and prop rise together. Translation error is at most 0.003 m and blade-up rotation error at most 0.5°. The same equations apply to baseline and candidate; source timing is the only revision.

Stable anchors are necessary but insufficient. Both clips must demonstrate an enclosing hand through independent measurements against evaluated sword surfaces. Thumb and finger surface samples must each approach within 0.005 m during grasp, lift, and hold. Surface samples within 0.008 m of the handle must span at least 170 degrees about its axis. Maximum sampled hand penetration is at most 0.004 m throughout the clip, including approach and closure. These gates supplement explicit Director acceptance of a visible grasp; a fist merely touching the handle cannot be accepted on anchor accuracy alone.

The measurement uses all skin vertices predominantly weighted to the right hand or its finger/thumb descendants plus interior samples on their triangles (six subdivisions). Signed nearest-surface distance measures penetration against the evaluated sword mesh. Contact angles use surface hits in the admitted handle band, -0.095 to +0.065 m relative to the grip centre. This finite sampling is not an exact continuous collision proof. It is checked at all frozen times in both clips; conservative limits and complete playback review remain required. Hand surface samples are also tested against the frozen axis-aligned support bounding box; this conservatively includes its bevelled-away corners. No intentional hand–support contact is admitted. The broader 0.280 m grip-region exclusion remains only for the separate protected-body clearance check, not a permission for hand penetration.

## Contact, support, and continuity gates

All distances use evaluated world-space metres. Before attachment, each sword must remain within 0.001 m of its frozen support position.

| Gate | GREEN limit |
|---|---:|
| Initial sword support contact error | ≤ 0.010 m |
| Grip translation error after attachment | ≤ 0.003 m |
| Blade-up orientation error after attachment | ≤ 0.5° |
| Thumb and finger surface contact distance after grasp | each ≤ 0.005 m |
| Angular contact coverage within 0.008 m of handle | ≥ 170° |
| Sampled hand–sword penetration at every time | ≤ 0.004 m |
| Sampled hand penetration into the support bounding box | ≤ 0.004 m |
| Wrist swing from the rig neutral relationship, all samples | ≤ 60° |
| Wrist swing while attached | ≤ 45° |
| Wrist axial twist from the rig neutral relationship | ≤ 30° |
| Forearm axial twist from the rig neutral relationship | ≤ 120° |
| Normalized index-root to thumb-root world-up dot, frame 24 onward | ≥ 0.50 |
| Attachment position discontinuity at grasp | ≤ 0.002 m second difference |
| Attachment orientation discontinuity at grasp | ≤ 0.5° second difference |
| Non-handle sword–body clearance | ≥ 0.040 m |
| Character or sword floor penetration | no evaluated vertex below -0.015 m |
| Sword separation from support four frames after lift begins | ≥ 0.020 m |
| Sword separation from support during held state | ≥ 0.250 m |
| Character-root translation or rotation | ≤ 0.000001 m / 0.0001° |
| Adjacent half-frame character RMS displacement | ≤ 0.18 m |
| Adjacent half-frame sword-root translation | ≤ 0.08 m |

Anatomical angles use evaluated pose rotations relative to the parent pose and the rig rest relationship, decomposed into swing and twist about the child bone Y axis. These are frozen fixture-specific regression screens, not universal human joint limits or proof of biological plausibility. The thumb direction uses evaluated thumb/index bone roots, independent of the authored target frame. Missing or non-finite anatomy measurements fail closed. Director review must still judge the entire shoulder–elbow–wrist approach and visible mesh deformation.

The blade/body clearance gate excludes only the defined handle-contact zone and right-hand vertices. It does not exempt forearm, torso, head, legs, or sword geometry outside that zone. Support contact is allowed only before lift.

## Frozen timing revision

Apply exactly `revision.json`: advance the grasp, lift, and held transitions by four frames while preserving the supported-to-reaching transition.

The authorized edit interval is `[28,76]`. Candidate-minus-baseline evaluated character geometry and sword transforms must be zero for every `t <= 28` and every `t >= 76`. The candidate time map is:

```text
T_candidate(t) = t + 4 E(t)
```

where `E(t)` is the quintic smootherstep envelope:

```text
E(t) = 0                         t <= 28
       S((t - 28) / 8)          28 < t < 36
       1                         36 <= t <= 68
       S((76 - t) / 8)          68 < t < 76
       0                         t >= 76

S(x) = 6x^5 - 15x^4 + 10x^3
```

Thus the edit has zero value and first derivative at frames 28 and 76. Candidate transitions occur exactly at frames 36, 44, and 64. A four-frame shift with tolerance 0.125 frame is required; a no-op cannot pass.

Outside-range character maximum vertex delta is at most 0.000001 m and RMS delta at most 0.00000025 m. Outside-range sword translation delta is at most 0.000001 m and orientation delta at most 0.0001°. At frames 28 and 76, candidate-minus-baseline RMS velocity change is at most 0.002 m/s for the character and sword translational velocity change is at most 0.005 m/s.

## Dense measurement

Measure every integer and half frame. Additionally measure every 1/8 frame on `[16,50]` and `[62,78]`, covering the complete approach, closure, attachment, and edit boundaries. Use a 0.125-frame central difference and the physical 24 fps timeline for velocity and attachment-discontinuity calculations. Also probe frames 28, 36, 40, and 76 at offsets ±0.061, ±0.01, and ±0.001 frame. These off-grid probes detect location interpolation before constraint activation. Sword base-location keys use constant interpolation because their coordinate meaning changes at attachment. Reject NaNs, non-finite matrices, missing objects, changed topology, inconsistent state ownership, or incomplete sampling.

## Persistence and replay

Create independent baseline and candidate actions while preserving all admitted source actions. For each role, save and reopen fresh checkpoint scenes at:

- frame 32: before grasp;
- frame 40.125 baseline / frame 36.125 candidate: immediately after attachment;
- frame 80: held.

At every checkpoint verify character and sword semantic identity, owner, attachment influence, sword and hand transforms, action identity, mesh/topology, and protected state. Rebuild from the frozen inputs in a separate output tree and require exact semantic replay plus evaluated numerical agreement within the same tolerances.

## Actual Blender negative controls

Each control is a disposable `.blend` variant and must be measured through the production interaction inspector. JSON-only mutation remains useful for validator unit tests but cannot satisfy this gate.

1. `early_attachment`: transfer ownership before the hand reaches the grip; detect wrong state timing and excessive grip/continuity error.
2. `attachment_teleportation`: move the sword at grasp; detect attachment position or orientation discontinuity.
3. `hand_sword_sliding`: add relative motion after grasp; detect grip translation/orientation error.
4. `penetration`: move or rotate the held blade into protected body geometry; detect the clearance gate.
5. `edit_leakage`: change candidate motion outside `[28,76]`; detect character or sword preservation failure.
6. `open_hand_attachment`: keep fingers open while the anchor still follows the sword; detect inadequate enclosure.
7. `oversized_handle`: double handle width/thickness with the anchor relationship intact; detect hand penetration.
8. `thumb_down_grasp`: rotate the actual hand and descendants 180° about hand Y by source frame 24; detect the reversed thumb-side direction.
9. `locked_forearm_roll`: retain the transported source forearm roll while applying the new hand orientation; detect excessive wrist twist.
10. `hand_support_penetration`: lower the actual candidate hand by 0.10 m over source frames 24–28; detect hand penetration into the support.

Controls may fail additional gates. All designated failures must be observed. They never enter Director scoring and never alter the accepted candidate.

## Director review

The Director reviews synchronized, anonymously labelled baseline/candidate playback in the primary, side, and rear views. The mapping is frozen before rendering and revealed only after submission. The Director records:

1. interaction readability, 1–5 in 0.5 increments;
2. grasp/contact believability, 1–5 in 0.5 increments;
3. attachment and transition smoothness, 1–5 in 0.5 increments;
4. hold stability and sword/body clearance, 1–5 in 0.5 increments;
5. concrete visible defects;
6. overall preference: A, B, or tie;
7. review duration in seconds.

GREEN requires the candidate to score at least 4.0 in every dimension, improve timing/readability by at least 0.5 without regressing another dimension, be preferred, and have no major defect. Complete playback in all three views is mandatory.

## Cost and provenance

Development, deterministic validation, Blender controls, replay, and Director review are provider-free. A paid evaluator is disabled unless separately qualified and frozen before a later campaign. Record provider calls, known API cost, Blender elapsed time, total harness time, and Director review duration. Cost per accepted interaction and per accepted second must remain distinct from incomplete total production economics.

Every scored package binds the character native hash, sword asset hash, campaign and revision digests, implementation commit and tree, Blender version/build, render profile, and zero-call budget. Failed and superseded attempts remain evidence.

## Decisions

- **GREEN:** all structural, timing, ownership, contact, clearance, persistence, replay, actual-control, cost, provenance, and Director gates pass.
- **YELLOW:** engineering gates pass but the Director review or recorded review duration is pending, or the creative improvement rule is not met without a major defect.
- **RED:** identity/protected-state drift, invalid ownership, attachment jump, grip drift, penetration, inadequate support separation, leakage, continuity failure, replay drift, failed control sensitivity, budget violation, or Director rejection.

## Explicit non-goals

Physical grasping, general finger articulation, release/drop behavior, rigid-body causality, moving-character pickups, forward locomotion, arbitrary props/skeletons, motion capture, retargeting, facial acting, cloth/hair, production rendering, natural-language planning, and unrestricted Blender Python are outside 3D-05.
