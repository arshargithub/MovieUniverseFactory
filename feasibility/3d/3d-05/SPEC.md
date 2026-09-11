# 3D-05 — Stationary character–sword pickup

## Question

Can Movie Factory create and persist one scripted kinematic interaction in which the accepted stationary character reaches for the qualified sword, grasps it without a transform jump, lifts it, and holds it, then revise the interaction timing inside one frozen interval without changing motion outside it?

## Qualification boundary

GREEN qualifies one character, the previously admitted CC0 sword asset, one right-hand grip anchor, one scripted pickup, and one timing revision. The character root remains stationary. The sword follows authored transforms and a deterministic attachment relationship; no physics simulation decides the grasp.

This experiment does not qualify physical grasping, finger articulation, release or drop dynamics, moving-character pickups, arbitrary props or rigs, autonomous staging, or natural-language animation editing.

## Frozen inputs

- Character scene: accepted 3D-03.1 native scene, SHA-256 `bbf05848c30e531ca31fc4632210b8344f6f35166db9c26abe4adfa6150e2488`.
- Sword: 3D-02 `weapon-sword.glb`, SHA-256 `8e69eb27977f8c84a9b7cd423cd5830eddcf0d07ac1d7fed1969931387015b28`, normalized to a 1.0 m longest dimension using the qualified import path.
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

`sword_01` is a semantic root located at the handle grip point. Imported sword geometry is offset under that root so the root identifies the handle consistently. The right-hand grip anchor uses the evaluated `RightHand` bone tail as its palm-centre position and the evaluated `RightHand` orientation.

Before grasp, the sword root is owned by the support and follows its frozen world transform. The qualified sword geometry is blade-up in world space, with its handle supported 0.15 m above the support surface. At grasp, a trusted constraint transfers ownership to the right-hand anchor. The hand reaches the existing sword transform; the sword must not move to hide a reach error. Constraint activation must preserve the sword world position and orientation. The hand orientation remains constant through this bounded interaction, so the sword stays blade-up during lift and hold.

During `grasped`, `lifting`, and `held`, maximum sword-root translation relative to the hand anchor is 0.003 m and maximum orientation error is 0.5°. Hand contact inside a 0.280 m radius around the grip point is intentional; this radius admits the qualified asset's measured grip, pommel, and broad guard region. Sword geometry outside the handle-contact zone, including the blade, must remain at least 0.040 m from protected body geometry.

## Contact, support, and continuity gates

All distances use evaluated world-space metres.

| Gate | GREEN limit |
|---|---:|
| Initial sword support contact error | ≤ 0.010 m |
| Grip translation error after attachment | ≤ 0.003 m |
| Grip orientation error after attachment | ≤ 0.5° |
| Attachment position discontinuity at grasp | ≤ 0.002 m second difference |
| Attachment orientation discontinuity at grasp | ≤ 0.5° second difference |
| Non-handle sword–body clearance | ≥ 0.040 m |
| Character or sword floor penetration | no evaluated vertex below -0.015 m |
| Sword separation from support four frames after lift begins | ≥ 0.020 m |
| Sword separation from support during held state | ≥ 0.250 m |
| Character-root translation or rotation | ≤ 0.000001 m / 0.0001° |
| Adjacent half-frame character RMS displacement | ≤ 0.18 m |
| Adjacent half-frame sword-root translation | ≤ 0.08 m |

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

Measure every integer and half frame. Additionally measure every 1/8 frame on `[26,38]`, `[38,50]`, `[62,78]`, and around every baseline and candidate attachment/state transition. Use a 0.125-frame central difference and the physical 24 fps timeline for velocity and attachment-discontinuity calculations. Reject NaNs, non-finite matrices, missing objects, changed topology, inconsistent state ownership, or incomplete sampling.

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

GREEN requires the candidate to score at least 4.0 in every dimension, improve timing/readability by at least 0.5 without regressing another dimension, be preferred, and have no major defect. Complete playback in both views is mandatory.

## Cost and provenance

Development, deterministic validation, Blender controls, replay, and Director review are provider-free. A paid evaluator is disabled unless separately qualified and frozen before a later campaign. Record provider calls, known API cost, Blender elapsed time, total harness time, and Director review duration. Cost per accepted interaction and per accepted second must remain distinct from incomplete total production economics.

Every scored package binds the character native hash, sword asset hash, campaign and revision digests, implementation commit and tree, Blender version/build, render profile, and zero-call budget. Failed and superseded attempts remain evidence.

## Decisions

- **GREEN:** all structural, timing, ownership, contact, clearance, persistence, replay, actual-control, cost, provenance, and Director gates pass.
- **YELLOW:** engineering gates pass but the Director review or recorded review duration is pending, or the creative improvement rule is not met without a major defect.
- **RED:** identity/protected-state drift, invalid ownership, attachment jump, grip drift, penetration, inadequate support separation, leakage, continuity failure, replay drift, failed control sensitivity, budget violation, or Director rejection.

## Explicit non-goals

Physical grasping, finger articulation, release/drop behavior, rigid-body causality, moving-character pickups, forward locomotion, arbitrary props/skeletons, motion capture, retargeting, facial acting, cloth/hair, production rendering, natural-language planning, and unrestricted Blender Python are outside 3D-05.
