# Pole attachment collision repair

116 pole-only fails260, strain1.77182; self-only solves all189frames at1.43185.
115 gravity/breeze without collisions solved all189frames, so disabling cloth
simulation or all collisions is not the chosen solution. Original pole boundary
puts three exact pins at radius22mm, exactly the18mm pole +2mm collider +2mm cloth
response distance. Unpinned hem between ties has no initial collision slack.

117 candidate: outward32mm tie plane (14mm from18mm shaft), explicit1mm pole
inner/outer margins, same2mm cloth distance,12 collision iterations instead of
default2 and friction2. Both object/self collisions stay on, same mass.001,
quality20 and1.7/6mm guards. Tie loop extends from shaft to actual32mm cloth edge;
no hidden detached flag. Collider clearance is a causal hypothesis, not established
by its numeric configuration. Actual full solve and front/reverse/production images
must decide. Readback settings and exact matrix/cache provenance retained.
Final41 changed pole must rerun actual physics, no transplanted40 cache.
