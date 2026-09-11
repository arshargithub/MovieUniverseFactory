# 3D-05 thumb-up anatomy repair

The Director rejected `interaction-v1-20260911T151105Z-b556e5e5`: the enclosure looked better, but the hand approached backwards with the thumb downward. That attempt remains RED. The user explicitly retained Astra for this repair. Engineering model attribution and outcomes belong in `docs/engineering-intelligence/events.json`; this is not a controlled Astra/Sol comparison.

## Cause and correction

The earlier fixed hand frame mapped local X upward even though this rig's thumb root is on negative hand X. Its transported forearm roll also left the wrist to absorb excessive axial rotation. Read-only measurement of the preserved rejected native scene found a thumb-side world-up dot of -0.5853 and wrist twist of 121.18 degrees at the inspected grasp frame. The new inspector finds these failures independently of the authored target frame (`runs/3d05-development/astra-rejected-anatomy-control`).

The correction explicitly places the thumb side upward, yaws the hand 45 degrees toward the sword, aligns forearm roll toward the neutral hand relationship, and aligns upper-arm roll with the elbow hinge plane. The two original arm segment lengths remain the positional solve constraints. Parent-relative pose conversion and quaternion sign continuity remain in the bake.

An initial thumb-up attempt retained guard collisions, excessive lift-time wrist bend, and a distorted elbow. Later close previews exposed a hand–support collision that the sword-only gates did not measure. All development attempts are preserved under `runs/3d05-development/astra-thumb-up-v*`. Their intermediate passing subsets are not acceptance evidence.

The final development staging puts the sword in front of the character at [-0.50, -0.20, 0.95] m, with held grip [-0.55, -0.20, 1.25] m. A lower grip point clears the guard. The hand rises around the support using the recorded smooth approach bow, advances to the handle, and closes its existing index/thumb controls. The thumb begins partly flexed with an outward clearance swing. `scene.json` and the specification define all numeric values. The source sword asset, character mesh, rig, weights, and original actions remain unchanged; this is a revised authored staging and motion, not identical staging with a wrist-only patch.

## Validation contract

The v4 contract adds finite, evaluated wrist swing/twist, forearm twist, and thumb-side direction measurements, plus sampled hand–support bounding-box penetration. The anatomy thresholds are fixture-specific regression screens, not universal biological limits. Director playback remains necessary for arm posture, approach readability, and visible deformation.

Sampling covers 515 times per clip, including every eighth frame over the complete approach/attachment region and dense off-grid edit probes. Ten actual Blender corruptions include thumb reversal, uncorrected forearm roll, and hand–support penetration, in addition to the previous seven controls. Designated errors must be detected through the production inspector. Missing anatomy/support measurements fail closed.

Development `astra-thumb-up-v12` measures approximately 33.86 degrees maximum wrist swing, 16.64 degrees maximum wrist twist, positive thumb-side dot of at least 0.5853, approximately 186.50 degrees held contact coverage, and contact distances under 3.60 mm. Maximum sampled sword penetration is below 0.008 mm; sampled support penetration is zero. These figures describe the development fixture; the scored campaign must repeat all checks against its frozen source.

No provider calls are authorized or needed. Codex engineering usage and human review duration are not inferred from the zero API cost. A successful machine run remains YELLOW until the Director accepts full synchronized playback. No accepted anatomy outcome or Sol handoff is claimed yet.

## Pre-score verification

The offline suite passes 125 tests (11 opt-in tests deselected). `astra-anatomy-native-final` passes the corrected scene and the first nine actual controls. Its last control initially failed sensitivity because translating the connected hand did not change the evaluated pose. That failed attempt remains preserved; it is not reported as a passing suite. The corrected control raises the support's actual top to 1.05 m. `astra-support-control-final/validation.json` confirms both hand/support penetration gates reject that evaluated scene. The scored campaign must repeat all ten controls, checkpoints, and replay on the updated source binding.

The final inspected approach/closure/hold previews are in `runs/3d05-development/astra-anatomy-front-preview`. Positive development measurements and previews do not replace full playback review.
