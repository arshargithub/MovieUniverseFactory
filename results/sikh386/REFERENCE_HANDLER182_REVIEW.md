#182 fixed reference-control handler review

New closed kind mounted_anatomy386_reference accepts only a hash-bound NPZ inside
anatomy386-references, with vertices/faces keys, finite boundedpoints, integer
nondegenerate triangle indices, strict size/count limits and no objectcode/MTL/
texture/rig import. Trusted code creates one neutral reference mesh, preserving
all original geometry/actions and hiding other meshes on its derivative only.
Never edits accepted master. Exact source/refclass and figure-purpose stay bound.

Actual apply-path preflight includes the new kind as existing-horse operation,
covering the177bug class.52affected schema/owner/native controls passed in
anatomy386-reference10. Earlier test invocation09 named a nonexistent testfile and
ran none; retained as failed invocation, not a pass. Actual native integration
still NOT_RUN. Proxy and its images are reference only; not finished character,
qualified rig, retargeted animation or artisticPASS on our horse.
