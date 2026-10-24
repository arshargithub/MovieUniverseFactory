# Condition the collision proxy, not another force guess

120 currentclock no-pole actualsolve maxstrain1.33886; boundedcollisionimpulse and
outwardbreeze bothfail. No force setting adopted. Keep same positivewind3,
threepins, bothcollisions, correctedsharedclock and allguards.

Collisioncylinder had20 long sidequads,74cm high by5.6mm wide, aspect131.4.
Same exact geometric20sided cylinder now32verticalsegments:660vertices642faces,
sidequad aspect4.11. No larger proxy, guard change or collision disable. Pure
winding/aspect control verifies outwardfaces and boundedconditioning; actual
Blender collisionresponse is still unknown. Record actual cylinder/rest/deformed
cloth and polematrix on anyguard failure. This tests a contactdiscretization cause.

121 productionattempt on final41 motion: if actual189frame solvepasses, retain
editable solver scene, exactmatrix/hash NPZ and sampled finalmesh. Front/reverse
and actual283/306/314/322/333 productionviews must test freeedge/binding/silhouette,
face/hand/chest/garment interfaces. No artpass from finite or cache alone.
If physicsfails, inspect actual failedcollision geometry instead of another
parameterguess. Fullclip staysblocked until realcloth visually qualifies.
