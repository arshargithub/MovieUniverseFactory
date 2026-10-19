# Sikh317 carry-forward findings

## Contact owners and evaluated motion

The wheel and chassis need separate response paths. The inherited wheel solver
transmitted high-frequency terrain/tread changes to the whole rider. The new
chassis filter preserves recorded wheel transforms, but that alone does not
validate forks, pegs, grips or ground contact. Check the saved native's actual
rendered tire vertices against terrain, not only copied contact reports.

Crowd motion similarly needs world-space stance targets. A plausible pelvis
trajectory can make feet slide or force unreachable knees. Solve reachable
support before rebaking visible clothing, then check stance drift and the
complete clothed silhouette. The current short step-and-close pattern is specific
to this crowd and corridor; it is not general locomotion.

## Test the representation that actually renders

Two joint controls failed as diagnostics: Euler edits did not affect quaternion
bones, and unkeyed quaternion edits were reset at render evaluation. Preserve
those failures. A valid control must change the evaluated rendered representation,
not merely an inspected property or temporary viewport pose. Study06 keys each
bounded variant and records evaluated coordinates beside its image.

Reducing a named wrist angle did not mean lowering the hoof in this rig. Inspect
bone spaces and the complete chain before assuming a parameter's visual effect.
Any new poll motion also invalidates the bit-to-hand rein curve. Recalculate and
inspect that interface in the same pass.

The decisive hoof finding was downstream of the toe: `MCH-f_hoof` retained a
copy-transform from its IK socket through the FK rear. Inspect the whole control
chain, including the visible endpoint, before continuing to tune upstream angles.
Grounded and airborne phases need explicit ownership; changing that ownership
also requires a seam/contact check through the transfer, not just at the apex.

## Material dependencies are geometry dependencies

The short-coat mesh initially inherited a shader that expected a pigmentation
attribute it did not possess. Supply the attribute and deformation weights;
more triangles or a successful material assignment do not prove a coat works.
Keep coat, eye, muzzle and hoof regions separate, and judge the whole animal at
shot size rather than magnified shader noise.

The existing Pashtun authored coat texture is an available reuse candidate for
the same-film surface language. Adapt its luminance detail while retaining the
new horse's colour and test its original UV attachment during deformation.
Do not assume a scene material is reusable merely because its node graph loads.

## Hidden controls and visible geometry must be checked together

Full-resolution crowd375 caught an error missed by planted-foot checks: source
limbs excluded from viewport evaluation were frozen while clothing was baked.
Their animation curves existed, and boots remained planted, but the visible
trousers separated from the moving boots. Keep bake sources evaluated (render
visibility is separate), then measure the actual evaluated garment endpoint
against the boot, across the complete required timeline. The inherited helper
also ended at528 frames; the current sequence has696. Explicitly bind the bake
range rather than inheriting an unrelated historical constant.

Fixing that interface revealed exaggerated0.85m outward strides. A mathematically
reachable target can still make a person appear to do the splits. Check whole
clothed stance, step width relative to leg length and body support before final
rendering. The new hypothesis uses shorter0.425m steps without changing the
required clearance. Do not close naturalness from this numerical bound alone.

An adjacent check then found a66.6mm leader cuff/palm separation: one sleeve
had been rebaked in305 while the opposite sleeve still carried an older bake.
Treat both sides of a coupled performance as dependencies, even when only one
side received an explicit edit. Candidate08 retains proximal/elbow form and
binds the distal visible sleeve to the actual palm throughout696 frames;
fresh evaluated separation is below0.005mm. That measurement establishes the
specific interface, not sleeve aesthetics or the actor's performance.

## Render scheduling is separate from visual quality

Record per-frame or per-batch timings before blaming a renderer/model. The first
317 full-resolution batch slowed sharply within one process; fresh shorter
batches are being tested with identical native/settings and preserved completed
frames. Do not call that a proven memory leak or a measured speedup until the
receipts support it. Recovery must validate all original bindings and completed
images, fill only missing frames, and retain the interrupted receipt.

## Retrieval and reuse

The pilot now routes the relevant component lessons without relying on the
query wording. Resource sidecars preserve historical provenance and record
source, dependencies, conditions, evidence and failures. Declared reuse requests
are checked inside the task gate. Undeclared dependencies still require manual
reconciliation; schema and hash checks do not establish license interpretation,
visual truth or continuous audiovisual quality.

The practical improvement in this pass is not an estimated percentage of saved
tokens or time. Full-resolution review rejected detached trousers and excessive
stride width internally, and an adjacent numerical check found the stale sleeve
before handoff. Preserve those distinct internal defects and their evidence.
Measure future Director escapes against them; do not count test passes or more
documentation as proof that the production process is now efficient.

No production resource is promoted merely because the new validator passes its
schema. Current scene-specific resources remain in progress pending their exact
review scope, and unresolved upstream rights remain visible. Adaptation effort
stays unknown where the ledger cannot attribute it accurately.
