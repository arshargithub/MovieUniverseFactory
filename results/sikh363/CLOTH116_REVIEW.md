# Isolate collision subsystem

115 native diagnostic controls: gravity-only and breeze3/collisions-off both
solve all189frames with exact pins, maxstrain1.04814/1.03608. Collision-only
fails268 with1.87468. This falsifies wind/basic goal transport as sole cause.
116 two fixed cases use wind3 and same mass/topology/settings: pole collision
only and selfcollision only. Same guards, full sequential230..418, no production
flag or AV pass. Isolated error determines next repair; all failed data retained.
This avoids simply disabling all collision and hiding intersections.
