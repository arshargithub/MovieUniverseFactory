## Decision: saddle-follow keys with an all-FK rider

Use one rider action: animate existing controls directly, without parenting, constraints, new bones, or rig scripts. Work in a separate preview file with a copied rider action; leave the horse animation unchanged.

### Setup and pose targets

Set rider object scale to **1.8/4.2 = 0.428571** and Z rotation to **π**; do not apply these transforms. Position the evaluated pelvis, not the armature origin.

Define saddle frame **S** at the visible saddle-top centre: initially world Z = **1.63 m**. Local −Y is forward, +X transverse, +Z upward. S must follow the evaluated saddle, including forward travel; it is not automatically a horse control’s head.

Provisional anatomical targets, metres relative to S:

| Landmark | (X, Y, Z) |
|---|---|
| Pelvis centre | (0, 0, +0.10) |
| Chest centre | (0, −0.08, +0.60) |
| Head centre | (0, −0.10, +0.88) |
| Knees | (±0.29, −0.27, −0.21) |
| Ankles | (±0.31, −0.17, −0.61) |
| Toes | (±0.31, −0.36, −0.64) |
| Hands | (±0.18, −0.43, +0.38) |

Match signs to anatomical sides after rotation. These are placement goals, not bone-head translations; preserve limb lengths and test barrel clearance.

### Controls and 60-frame motion

Select **FK** through existing custom properties, verifying which endpoint activates FK rather than assuming its numeric value. Pose thighs, shins and feet with their `*_fk.L/R` controls; similarly use upper-arm, forearm and hand FK. Leave hand/foot IK controls and thigh pole targets inactive.

Use `torso` to carry the seated pose; `hips` establishes pelvic orientation, `chest` the forward lean, and `head` the gaze. Manually key torso translation/orientation each frame against S, accounting for its offset from the pelvis.

Hold the seated leg pose. Add chest pitch of ±3° around the initial lean, maximum at saddle crest and minimum at trough; counterrotate upper arms and head approximately oppositely. Repeat these local offsets every **10 frames**, with frame 11 matching frame 1. Follow actual saddle translation—not repeated world positions—for frames **1–60 at 24 fps**.

### Fast checks and essential measurements

Before detailed posing, perturb torso, one FK thigh and one FK upper arm; scrub and confirm mesh response, then undo. Inspect the Drivers editor for invalid drivers/namespace errors. Blocked `rig_ui.py` alone does not establish breakage; working horse gait does not validate rider drivers.

Next measure S’s evaluated trajectory, rider joint lengths and barrel clearance. Track an **evaluated hoof-sole point during stance relative to ground**. Control-head speeds **2–15 m/s, median 3.45** imply **8–63 cm/frame, median 14 cm**; flag the apparent contact mismatch, but do not equate control heads with hoof surfaces.

### Go/no-go

**Go:** responsive controls, pelvis within 3 cm of target, reachable limbs without barrel penetration, and sole slip below 2 cm per stance. **No-go:** any failed check; show the labelled failure and stop—no rig repair loop.