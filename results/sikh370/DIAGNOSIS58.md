#58 actual paired contact diagnosis

53 deepest-load306:12 evaluated cloth vertices penetrate, versus145 triangle
interiors. Minimum29.17mm lies inside the thighR.001 surface; three independent
ray directions agree it is inside.55 stable attachment reduces this to13 vertices
and67 interiors/min9.97mm. These are actual geometry failures, not merely shadows
or flipped nearest-normal statistics. Most error lies between projected vertices.

Actual target horse has subdivision viewport1/render2; older369 measurements
explicitly tested viewport geometry. Future contact checks must match render
subdivision and restore the original viewport setting before saving.

Next discriminating control: increase the existing pad subdivision BEFORE its
contact projection, preserving rest topology/UV/materials/offset/allmotion. The
flat projected faces bridge curved thigh surfaces; more surface samples should
reduce that error. Test on53 and55 sources, not a newoffset or bodypose. If the
vertex/interior pattern does not improve adequately, reassess correspondence or
construct the needed local cloth deformation; do not blindly add levels.

No faithfulmotion/appearance pass follows. Data identifies where construction
fails; actual rendered silhouette/contact and the wholephase remain required.
