# Pennant113 causal reassessment

Actual113 failed at272: max edge strain1.78624, exact moving pins. Median1.0003,
90th1.1323,95th1.2206,99th1.4958. Worst31/32 is not a pin edge;
this is not just one inaccurate tied vertex. Saved actual mesh/goals/edges and
failed solve remain in the native output. The rest/deformed plot is diagnostic,
not a production render or artistic approval.

The local Blender5.2 UI labels settings.mass **Vertex Mass**
(/Applications/Blender.app/Contents/Resources/5.2/scripts/startup/bl_ui/properties_physics_cloth.py:87).
Official manual corroborates the vertex-based property:
https://docs.blender.org/manual/en/5.1/physics/cloth/settings/physical_properties.html
The prior0.20kg per vertex means55.2kg across276 vertices for this small pennant.
Increasing mass in112 was the wrong direction and no solution should inherit it.

114 discriminating control: same geometry/three ties/pole motion/quality20,
stiffness80/shear50/bending.18/air4/wind3, change only per-vertex mass to.001kg
(0.276kg discrete total). Read back actual setting, preserve unchanged1.7 strain,
6mm pin and finite-topology guards. No raised thresholds or topology simplification.
This is an artist simulation setting, not a measured textile material. If it fails,
retain data and isolate wind/collision rather than blindly increasing stiffness.
If it succeeds, actual flag-front/reverse/production images can still reject stiffness,
collapse/intersections or silhouette. Any final pole-motion change requires a new solve.
