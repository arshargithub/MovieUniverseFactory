# Decision 0004: design human motion before implementing it

Status: adopted engineering workflow; automated Factory stage not implemented.

The 3D-05 grasp repairs established contact and preservation while repeatedly requiring Director corrections to human movement. The latest run passes its machine gates, but the Director observes a rigid-looking lift, slight elbow deformation, and missing attention toward the sword. These observations are recorded without inventing scores, severity, or an acceptance decision.

The workflow had interaction states, timings, geometric constraints, and reactive anatomy diagnostics. It did not require a coordinated movement brief covering intention, attention, joint contributions, contact, and transition into the hold before animation code was written. A collection of admissible poses is insufficient evidence of a convincing performance.

Before implementing or repairing human performance, complete a [motion design brief](../planning/MOTION_DESIGN_TEMPLATE.md). Specify what the character is doing, the movement phases, each participating body region, what remains deliberately still, and how the prop follows the hand. Check that the constraints allow the intended motion. In 3D-05, a fixed world hand frame and a fixed upright sword can conflict with the desired forearm/wrist articulation.

The sequence is: motion brief and constraint review → inexpensive complete motion preview → contact, deformation, continuity and preservation checks → freeze the scored contract → scored campaign → Director playback acceptance. Diagnostic inspection is allowed while developing the brief. This adds no blanket user-approval requirement; it requires engineering to establish a reviewable movement design before routine implementation and scoring.

Reference observations, authored choices and unverified hypotheses must be distinguished. More head, torso or wrist movement is not inherently better: include each cue only when it serves the intended action. Scope modest head orientation separately from eye animation, and authored weight cues from physical simulation.

Machine validation must address coordination and evaluated mesh deformation as well as joint-angle bounds. Negative controls should include a mechanically valid but rigid lift and the absence of any explicitly required attention cue. Director review remains the authority for perceived naturalness. Do not retroactively change an earlier run's thresholds or turn an optional performance enhancement into a historical formal failure.

This is a Factory planning/validation lesson shared across engineering models. Preserve the Astra improvements and subsequent Director corrections; do not attribute the missing planning step to Sol alone. The central engineering ledger records this outcome. No paid API planning stage or automatic model routing is introduced by this decision.
