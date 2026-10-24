#363 working synthesis, pending final checks

- A valid integer-frame pose can hide broken fractional interpolation. Repeated
support updates left stale fractional world keys between newer integer keys.
Actual source fractional reins were broken before retiming. Test source subframes,
not just pose endpoints. Atomic owned interval replacement preserves190 actual
integer poses; common inverse-clock sampling prevents sparse/dense consumers
from drifting. Quaternion unwrapping alone was a falsified alternative, retained.
- Retiming sparse keys independently does not commute with a nonlinear edit.
All armature/object/contact/camera/FX consumers need the same sampled source time;
check actual evaluated outputs before decorative changes or rebuilding ropes.
- An image hand problem is not proved by a single negative matrix dot. Wrong
palm curl sign, rest-binding and weight-assignment hypotheses were tested. Explicit
palm-frame phalangeal arc and thumb across index/middle improved actual110 images.
Final changed-motion right-hand evidence still pending, so no universal hand pass.
- Read actual Basis and relevant shape keys; Mesh.vertices differs16.1cm here.
Same displacement across all shape blocks avoids an edit disappearing on a key.
Weighted coordinate lift made a visible shelf; topology-aware constrained fairing
with fixed limb anchors yielded continuous113 chest front/side controls.
- Cloth solver mass is per vertex, not total garment mass. But mass correction
alone failed: never stop diagnosis at the first plausible explanation. Fixed
189-frame controls separate basic integration/wind from collision. Pole-only fails,
self-only solves. Exact ties alone do not prove a physically viable attachment.
- Source/camera/pose change invalidates cloth cache. Prove exact-final-action
physics before full media rendering; retain solver inputs, cache and matrix hash.
A solver guard near the threshold is still FAIL. No guard increase to force pass.
- Numeric projections can enlarge safety framing until the subject loses impact.
Separate Director intent from agent-added full-tip fit. Whole horse/face/flag must
remain visible; purposeful spearhead crop may be acceptable, subject to real images.
- Reference roles remain distinct: video faithful action authority; Director speed
feedback modifies airborne pace without erasing preparation; baseline images are
look direction. Controller checks/tests cannot self-pass motion or anatomy.
- Workflow issues retained: required source/handler revisions consumed original
corrections; code changes invalidated native dependencies; planning coverage115
initially omitted full requirement coverage and was rejected before any worker.
No duplicate authority, cap reset or newtask was used to erase those costs.

This working file is a synthesis of actual retained evidence, not a new rule or
Director-accepted artistic result. Final process/knowledge pointers follow only
after scoped checks and exact blocker accounting.
