# Shared solver-time material trajectory

118 exactnegative reproduces283 strain1.83053; reinforcedhem fails284 at2.01225.
Reject hem-as-root hypothesis, retain original3point pins and all failed evidence.

Collider was independently keyed with object transform quaternion/defaultBezier
curves. Clothpin goals use linear world-coordinate shape keys. Even exact integer
agreement does not mean solver substeps see the same material trajectory. This
is the same class of interface problem found in363 source-key/retime controls;
do not assume integer matrices qualify fractional collision.

119 exact-final41 controlled cases: A inherited objectcollider negative; B closed
pole collider animated by worldvertex goals using exactly the same linear clock
as cloth pins. Identity objecttransform, same geometric cylinder, bothcollisions,
three originalpins, all physical settings and unchanged guards. Actual quarterframe
pole vertices are compared to the pin-goal interpolant before CLOTH. Record max
error and legacy quaternion adjacency; sharedvertex case must be under10um.
No claim that quaternionflip is actualcause without observed negative dots.

If B solves, the intendedphysics/cache and actual images still decide supplecloth,
attachment/penetration/silhouette. If it fails with clock coherent, capture actual
collision geometry/collider settings atfailure rather than another blindstiffness
change. No broader pose/identity/style or authority changes. Original119/max127.
