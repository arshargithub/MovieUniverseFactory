# Conditional coat integration strategy — body must pass first

Preserve existing follicle triangles/materials. Avoid183 copies of a large nap
mesh and avoid per-frame nearest-surface projection that can jump between limbs.
Bind each existing follicle once to a triangle on the final evaluated body at a
standing control: stable three vertex indices, barycentric root and tangent-frame
width/length offsets. Native Geometry Nodes Sample Index + Set Position can then
follow the body's actual final subdivided shape at every time without a second
large shape-key cache. Disable the nap's original armature to avoid double skin.

Prove evaluated target topology/index ordering stays identical at all sampled
poses; compare exact bound root reconstruction and inspect actual front/side/
reverse skin appearance. Refuse collapsed triangles, excessive nonlocal matches,
missing/unmapped roots or changed coat material. Target Object Info geometry must
be relative to nap coordinates, including real moving transforms. Surface roots,
not hair tips, are the binding datum. Current body source/camera and accepted
primary action remain preserved. This is a proposed trusted-handler integration;
not implemented, dispatched or visually qualified yet. No code addition while an
unreviewed body candidate is waiting: source freshness and review order apply.
