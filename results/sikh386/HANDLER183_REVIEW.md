#183 matched material/geometry control and local template fit

A geometric diagnosis needs a shader-independent control. New fixed clay kind
accepts only targethorse, chooses largest connected skin component (expected9990
vertices), changes only its diagnostic material, preserves alpha-card materials,
hides unrelated renderable objects on derivative, and uses automatic geometric
normals if custom normals existed. Source vertices/shapes/actions checked exact.
No productionshader/style adoption. Original80master remains unmodified.

56affected controls pass, including actualexisting-owner dispatcher, closedfields,
safe reference data and exact plane/edge/corner projection plus known-rigid
one-ring rotation controls. Actual native clayintegration still needs proof.

183compares identical-material sourcecontrol and templatefitted previoushorse in
neutral283andworst339. The atlasregistration is provisional; it cannot be treated
as measuredgroundtruth. One-ringrotation transfer uses actual source motion,
including Bbone effects, rather than guessing bone weights. Orientationguards
can retain bad source nearroots; actualviews must expose that, not waive it.

Only bounded local chest/root coordinates change; original head/hindquarters,
distal limbs, outside-mask points and accepted action are exact. New spatial
reference is formalized in all planning stages with its limited role, source,
qualification and CC0provenance. It does not govern identity/look/choreography.
