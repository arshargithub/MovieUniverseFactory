# 3D-03.1 — Corrected transfer and bounded jump authoring

## Question

Can Movie Factory correct the proven parent-evaluation defect in same-skeleton animation transfer, preserve the existing 3D-03 state guarantees, and produce complete idle, run, and jump playback without hiding the admitted jump source's missing motion?

## Frozen inputs and claims

The character, rig, skins, and three FBXs remain the exact digest-paired Kenney CC0 inputs admitted by 3D-03. The official archive contains no additional animation files. Its `jump.fbx` evaluates as a near-static crouched pose and is admitted only as a pose reference.

This experiment makes two distinct claims:

1. Idle and run are same-skeleton, rotation-only transfers for these admitted fixtures. The worker captures all source samples before changing the target, solves every target basis against the current frame's explicit parent pose, preserves the canonical rig's lengths, canonicalizes quaternion signs, and uses a static clip placement offset. Bone and root translations are deliberately discarded, so this does not establish general vertical-trajectory transfer.
2. Jump is bounded authored motion. It deterministically blends the admitted idle and crouched reference poses over 13 frames and adds the frozen 0.34 m takeoff/airborne/landing trajectory. It is labelled `authored_full_jump`; it is not described as faithful transfer of a complete source jump.

All actions record their imported frame rate. The evidence player uses 30 fps for idle and 24 fps for run and jump. The Blender scene has a deterministic 24 fps default; consumers must honor each action's recorded source rate when exact imported timing matters.

## Qualification

- Preserve the failed 3D-03 temporal evidence and the diagnostic controls.
- Build through the production worker, then save and reopen in fresh Blender processes.
- Apply only the frozen skin and idle-to-run revision and require exact protected-state preservation.
- Replay that revision without provider calls and require an exact semantic snapshot.
- Render every frame of idle, run, and jump with feet visible.
- Require finite evaluated geometry, complete timestamps and limb fields, bounded mesh displacement, no floor penetration, true left/right run support, jump endpoint contact, a contiguous airborne phase, and an exact endpoint seam.
- Require Director playback acceptance for all three complete clips. Contact sheets alone are supporting evidence.

## Gates

- **GREEN:** all structural, persistence, revision, replay, every-frame temporal, and Director playback gates pass.
- **YELLOW:** machine evidence passes but Director review is pending, or only idle/run are qualified while complete jump remains unavailable.
- **RED:** hierarchy corruption returns; source/target identity drifts; revision/replay differs; idle or run becomes unreadable; or authored jump lacks takeoff, airborne motion, landing, continuity, or plausible deformation.

## Claim boundary

GREEN applies only to this Kenney character, its corrected idle/run transfers, the fixed authored-jump recipe, two skins, and the existing structured revision. It does not qualify arbitrary retargeting, arbitrary animation synthesis, horizontal root motion, general action editing, facial performance, physics, or production character quality.
