#61 established anatomical frame

60 stopped at its first exterior ray, before a saved derivative. The code used
the imported mesh object's axes as cross-body anatomy. Existing supported-pose
construction defines those axes in horse.rig's frame. That semantic orientation
contract was not applied to the new contact solver.

Use that established rig frame for seed-side classification and rotating rays,
keeping mesh.world only for actual surface coordinates. Preserve all other
method parameters and frozen53motion. A missing ray now records actual seed,
direction, nearest surface distance and both matrices before failing. Do not
guess or silently snap elsewhere. Native geometry is the discriminating test;
no new art acceptance, source/budget reset or tool call follows from compilation.
