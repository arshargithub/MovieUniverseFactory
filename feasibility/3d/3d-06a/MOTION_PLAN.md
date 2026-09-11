# 3D-06A first motion brief

Authorship: manually authored engineering pose/time plan. No reference video or automatic motion extraction is claimed. Objective: a restrained acknowledgement by a stationary character, raising the right forearm slightly in front of the torso, pausing, and returning. This is a comfortable-range suitability trial, not a claim that the known rig can perform arbitrary gestures.

Use the packed accepted 3D-03.1 scene identified in 3D-04's baseline binding (`bbf05848c30e531ca31fc4632210b8344f6f35166db9c26abe4adfa6150e2488`). Capture the initial idle pose at its original frame 1; retain the feet/root and left arm. Preserve original actions. The new action is isolated. Pose computation rotates full descendant chains and explicitly solves each child's local basis against the desired current parent pose, using the previously qualified conversion helper.

| Frame | Weight | Intention and coordination |
|---|---:|---|
| 0 | 0 | Relaxed stationary idle reference |
| 24 | 0.1 | Small preparation, shoulder and head begin to participate |
| 48 | 0.6 | Acknowledgement cue landmark on the upward approach |
| 60 | 1 | Modest peak, wrist follows forearm rather than staying world-locked |
| 96 | 0 | Smooth return to the same neutral pose |

Initial amplitude hypothesis: upper arm 6° toward world-up, forearm 32° toward world-up, wrist −4° in the same bend plane, head 2° nod. Rotation axes come from the neutral segment and world vertical, transformed into the armature frame. They are recorded in the output pose board. No longitudinal twisting, imposed hand orientation, finger curl or prop is added. Keep the torso quiet for this small movement; feet/root remain unchanged. Frozen candidate cue rules will be derived from a declared measurable joint/pose crossing before timing-revision generation, not guessed from keyframe labels.

Screen all half frames, retain the existing local 26-edge elbow selection and 0.35–1.50× limits, check finite coordinates, grounding and support displacement, and retain the five evaluated landmarks. Review inexpensive overview/contact poses before full playback. Any pre-existing awkward neutral hand must be identified separately; do not silently count it as repaired. At most three amplitude/routing variants of this hypothesis; stop and reassess on repeat deformation failure.

Native allocation: first small screen and ten stills, budget ≤3 minutes and <200 MB. If it passes, one complete low-cost preview, then freeze reference cue, revision, inspector and control contract for a single scored campaign. Overall initial estimate remains 60 net minutes with a 20-minute diagnostic checkpoint. No paid API use. Capture all attempts and timings in the operating ledger.
