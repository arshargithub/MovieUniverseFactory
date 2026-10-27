#176 last approved correction — complete-loop search

175 failed before save/render, correctly refusing body_loop0/head_loop50. Its
native diagnostics showed a29-vertex body chain with degree1 endpoints. Exact
read-only GLB control reproduced that chain. Searching complete components
revealed the existing30-vertex closed neck loop: one coarse donor vertex lies
0.211926m from the chosen plane, just beyond the old0.20m edge-search window.
It was a search-clipping error, not evidence of absent skin or a need to invent
a closing edge. Pure-plane and old-union controls agree; source pose differences
remain a native test rather than assumed from this rest-space control.

Repair: build full geometric boundary components first, require every vertex
degree2 and full closed traversal, then classify the complete near-neck component
with maximum0.35m plane distance and0.45m centroid bound. Keep every actual
endpoint. No artificial edge, missing-geometry waiver, policy/allowance reset or
new model. Synthetic negative/control reproduces the omitted0.212m cut vertex;
actual static source returns30 closed body vertices after repair.

This fixes only175's technical integration blocker. Surface shape, missing face,
neck band/fold, old tack, material mismatch or moving seam still fails actual
review.176 is the final authorized slot (167..176); full deferred clip may run
only after all scoped agent-look steps pass. No automatic new correction.
