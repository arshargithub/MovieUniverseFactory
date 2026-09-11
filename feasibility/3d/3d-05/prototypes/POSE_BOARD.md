# Authored pose board and constraint review — coordinated lift v1

This is an authored animation design, not a traced human reference or measured biological model. It is grounded in the admitted rig and the Director's request. No external motion reference has been reviewed. The diagrams below describe joint contribution; rendered rig poses still need verification.

| Source frame | Pose intention | Arm/hand design | Attention |
|---|---|---|---|
| 1 | Rest | Preserve the starting stance and original arm approach reference. | Original head direction. |
| 16 | Prepared to acquire | Hand is about to reach; no sword movement. | Head has turned toward the handle, capped at 35° yaw and 18° additional pitch. |
| 32 | Open hand in place | Keep the measured support-clearing approach and enclosing grip location. | Head attends toward the handle. |
| 40 | Grasp | Retain thumb-up enclosure; capture the complete hand-to-sword transform without a jump. | Maintain attention. |
| 58 | Mid-lift | Shoulder and elbow raise the hand; its long axis pitches upward by about half the planned 25°. Forearm alignment and wrist accommodation are solved together. | Head direction follows the moving grip. |
| 68–96 | Inspection hold | Finish at 25° hand pitch with a corresponding prop tilt and greater forearm contribution. Ease to a stop; no added fidget. | Continue facing toward the sword. |

The 25° lift rotation is an artistic prototype parameter, chosen to make the forearm contribution visible without reversing the grasp. It is not a universal joint limit. The elbow solve must demonstrate actual forearm-angle change; merely rotating the wrist does not satisfy the brief.

Head local +Z is the proposed face-forward axis: the admitted head rest/pose frame points approximately toward the visible front of the face. Verify its sign in the preview. This is head orientation, not independently articulated eye gaze. Torso remains intentionally still in this bounded pass: the stationary reach is within arm range, and a modest head cue can communicate intent without changing torso/shoulder parent transforms. Add torso motion only if the complete preview establishes a need.

Constraint decisions: preserve the old approach, closure, support position, root/lower body and source actions. Replace the world-fixed hand and location-only prop attachment for this opt-in prototype with a smooth lift orientation and a complete rigid attachment. Keep the sword fixed on its support until grasp. Relative grip stability replaces constant world-upright orientation; measure blade/body clearance under the new tilt. Contact coverage must be measured around the sword's own axis, not world Z. Thumb orientation must distinguish intended whole-grip tilt from an inverted grasp.

Validation assignments: measure evaluated elbow flexion, forearm/hand pitch, head direction, elbow-region mesh strain, rigid relative grip errors, contacts, clearance and fractional continuity. Preserve all prior controls; add rigid lift, wrist-only compensation, wrong relative prop rotation, elbow skin distortion, and missing attention controls. Prototype thresholds are engineering probes until justified and frozen. Do not turn a failing numerical result into a pass by silently relaxing a ceiling.

Progression: inspect key poses, then a complete low-cost 96-frame preview in three views. Stop if the planned pose cannot retain mesh/contact integrity. Full Director review is needed before describing the motion as natural. This prototype is unscored; provider budget is zero.

Key-pose diagnostic v1 retained the old distant hold and extended the elbow to about 18° flexion. That does not meet the intended elbow-led lift. The next bounded pose probe brings the hold to [-0.42, -0.25, 1.25] m, closer laterally and in front of the character, to permit elbow flexion while retaining clearance. The original probe is preserved.

Prototype probes v3: evaluated lift measurements show 49.09° forearm pitch gain, 25.00° hand pitch gain and 20.90° peak elbow-flexion gain. The complete-clip elbow edge-length probe fails its initial 1.5× ceiling: 1.821× at source frame 20.25 during the preserved approach, versus 1.206× around mid-lift and 1.136× at the hold. This is a diagnostic failure, not a silently revised threshold. Keep the complete-clip check and its failure in the prototype result. The 26 selected mesh edges are an admitted-fixture deformation probe, not a universal tissue-strain measure. Full playback must expose the approach as well as the repair. Director review remains pending.
