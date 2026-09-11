# 3D-05 coordinated lift: design brief

Status: opt-in unscored prototype implemented after Director feedback on `interaction-v1-20260911T160515Z-85655dd3`. See [authored pose board](prototypes/POSE_BOARD.md) and [prototype results](prototypes/RESULT.md). The existing scored configuration and evidence remain unchanged. New motion is not accepted or GREEN; the full-clip elbow deformation probe exposes a reach-stage limitation.

## What needs to change

The Director reports a lift that appears driven primarily by the shoulder/upper arm, with a level hand/forearm presentation and slight elbow deformation at the top. They also note that the character does not look or turn toward the sword, describing this as a more minor issue that may be outside the present criteria.

Code inspection establishes a fixed hand orientation after source frame 24 and fixed sword orientation throughout. The elbow is solved and does move; it is not literally a frozen joint. The fixed hand orientation restricts how it can participate. The current authored channels cover the right arm/hand/fingers, with no authored head/torso attention cue. The connection between these constraints and the perceived stiffness is a repair hypothesis supported by the feedback, not a complete anatomical diagnosis.

Reference basis so far: the admitted rig, existing previews and Director observations. No human pickup reference clip was reviewed in this pass. Before coding, choose a documented reference or create an annotated authored pose board showing preparation, contact, mid-lift and hold. Identify which choices are artistic and which were verified against a reference.

## Intended performance

A stationary character deliberately acquires the existing sword and raises it into a comfortable inspection hold. The sword should read as handled with modest effort, without an exaggerated heave. Preserve the enclosing thumb-up grip and support clearance already established. Naturalness comes from a coordinated movement, not adding motion to every joint.

| Phase, baseline source frames | Proposed movement | Contact and preservation |
|---|---|---|
| Prepare, before reach at 16 | A modest head orientation toward the handle precedes the hand. A small upper-torso contribution is optional if it improves the reference pose. | Root and lower body stay fixed; sword stays supported. New head orientation is a performance addition, not retroactive scoring of the current run. |
| Reach, 16–32 | Shoulder placement, elbow flexion and forearm rotation cooperate to bring the open hand around the support. The wrist adjusts toward the grip. | Retain full hand/support and hand/sword clearance measurements. Inspect the elbow mesh during the entire approach. |
| Close/contact, 32–40; load, 40–48 | Retain the enclosing closure. Let the pose settle into the grasp before lifting; any preparation must preserve the supported sword pose. | Transfer one owner at grasp with continuous world position and orientation. |
| Lift, 48–68 | Elbow flexion changes the forearm angle while the shoulder contributes. Permit a small planned wrist adjustment and a corresponding sword tilt; do not force the hand to remain level in world space. Head direction can follow the blade/handle toward the hold. | The sword remains rigid relative to the grip. Its blade clears body and support throughout. Re-evaluate mesh shape near peak elbow flexion. |
| Held, 68–96 | Arrive smoothly at a comfortable pose, with the character attending to the sword. Avoid adding arbitrary fidgets. | Hand–sword relationship remains stable. Any settling must be explicitly timed and end without an artificial joint snap. |

These frames retain the current state contract as the starting design. Angle amplitudes, trajectories, head timing and optional torso motion are not frozen here. Choose them from the pose/reference review, state the rationale, then freeze the next configuration before scoring. Do not increase motion merely to exceed a numerical minimum.

## Necessary architecture and contract changes

The current location-only attachment and world-upright orientation gate must not be carried over blindly. For a rotating grip, capture a complete rigid transform at grasp:

`hand_to_sword = inverse(hand_world_at_grasp) * sword_world_at_grasp`

`sword_world(t) = hand_world(t) * hand_to_sword`

This preserves the sword pose at attachment while allowing hand and sword to rotate together. Test actual evaluated relative position/orientation and unwanted contact, rather than equating stability with a constant world orientation. Retain a separately justified blade-orientation envelope if the brief requires it. Any change to the former 0.5-degree world-upright gate belongs to a new frozen campaign, not the existing evidence.

Head orientation is a small addition to the authored performance scope; this does not require eye articulation or qualify gaze tracking. If torso motion is included, explicitly admit those channels and recompute shoulder/arm placement against the current parent pose. Do not repeat the stale-parent evaluation failure from 3D-03.1. Keep root, lower body, source actions, identities, mesh, weights and rest rig protected.

Build a common improved baseline performance first. Derive the timing candidate through the existing bounded source-time mapping, including any coupled head/torso channels. Outside `[28,76]`, baseline and candidate must still match under the frozen preservation rules. The improved baseline may differ from the prior run; do not confuse that change with leakage in the timing revision.

## Preview and qualification assignment

1. Complete the key-pose/reference and constraint review before production animation edits. Compare natural elbow/forearm contribution with the current fixed-hand lift. Declare required attention cues and optional torso motion explicitly.
2. Produce one inexpensive complete motion preview in the overview and side/rear contact views. Examine speed, ordering of movement, elbow deformation and arrival at the hold, not just stills. This is development evidence, not a scored retry.
3. Add independent measurements of elbow flexion, forearm/hand world-orientation trajectories and rates, and evaluated elbow-region mesh deformation. Preserve existing full-clip contacts, clearance, fractional sampling, persistence and replay. If head orientation is required, check its timing/alignment using a verified head frame; do not call this eye-gaze validation.
4. Use actual controls for a rigid shoulder-dominated lift, wrist-only compensation, bad relative prop rotation, distorted elbow deformation, and absent attention when it is required. Existing controls and preservation checks remain applicable. Numerical ranges and meaningful-motion thresholds must be justified and frozen before the scored campaign; minimum angular movement alone cannot establish naturalness.
5. Freeze the new source, motion plan, scope and gates only after the complete preview supports the design. Then run the full anonymous A/B campaign and obtain Director acceptance. Do not start a further scored run merely because the angle bounds pass.

Stop the development attempt if solving the pose requires joint/skin distortion, grip sliding, clearance violations or unexplained threshold relaxation. Diagnose the rig/skin limitations before another render campaign. The task remains one scripted stationary interaction; full-body locomotion, physical weight simulation, arbitrary acting, eye animation and general dexterous manipulation remain out of scope.

This planning pass makes no provider calls. Any future API evaluation remains subject to its explicit campaign budget. Engineering model changes and Director corrections remain part of the Factory learning record.
