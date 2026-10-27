#170 actual head-boundary reconstruction

169 failed close images preserve overlapping broken forehead, not a coat success.
Read-only original GLB ray intersections (HEAD_LAYERS.json) show partial hidden
layers but no complete continuous head beneath the nasal plate. Delete-and-assume
is disallowed. New method explicitly closes actual resulting cut loops as skin.

Fixed warhorse_headrebuild384: original166 only, classify head armor by actual
metal atlas and rest-space/head-weight bounds; weld coincident head seams, remove
those faces, close connected cut boundaries, subdivide new skin only. Bind new
vertices to existing head bone; original non-head coordinates and skin weights
must match exact before/after dictionary or native call fails. Original body and
motion are retained. Restore original non-head custom normals; head normals and
topology are reconstructed. Eye/ear/muzzle visibility and natural contours still
require actual close proof. No name/hash/software pass substitutes for that.

The repair uses measured exposed source bridge profile to constrain new skin,
and the existing donor coat atlas sampled in surface-bound rest coordinates.
Skin patch has its own material, not camouflage over retained armor faces. No
reference pixels are incorporated. All output remains editable native geometry.

Reference reopening addressed: actual381 stud-rear.jpg is re-inspected for its
clear near-frontal head (not just its old torso role). A new explicit reference
ID/coverage covers front forehead/eye/bridge/muzzle relation under bridle. Existing
bare Campolina side and anatomical plate corroborate structure; no breed copy,
identity/style change or exact pixel target. Eye and muzzle geometry remain donor
surfaces. Coverage supports a gross head reconstruction, not veterinary anatomy.

Implementation preflight: closed dispatch/numeric/boundary tests pass; actual
bmesh topology/UV/weight preservation is NOT qualified before first worker.
Negative controls168/169 remain FAIL. If patch fails, reject before wholehorse
rendering, assess actual topology/region rather than repeat smoothing sweeps.
