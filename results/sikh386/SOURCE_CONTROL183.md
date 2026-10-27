#183 matched clay source control

Actual control_front283/339 inspected. Raw source geometry remains a broad,
blocklike chest in stance and an unsupported apron/rounded side masses in lifted
pose after removing skintexture/bump and using automatic geometric normals.
This falsifies a purely material explanation; actual anatomy still needs repair.
No originalhorse artisticPASS. These are expected negativecontrols in the183test.

The actual source does have custom split normals. Any evaluated-position cache
that disables the armature must explicitly qualify normals/shading as well as
coordinates: retaining old custom normals can misrepresent the deformed surface.
Current matched-clay proofs remove this confound on both source and candidate.
Final-film integration must validate/rebuild or clear those normals with the
production shader; the current diagnostic does not establish that final look.

Comparison still changes shader and normalpolicy together, so it does not measure
the separate contribution of each to prior images. Geometry remains visibly
wrong regardless. Do not infer that clearing normals alone solves the chest.
