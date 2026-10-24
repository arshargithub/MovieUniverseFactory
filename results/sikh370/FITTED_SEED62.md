#62 fitted reference, not raw cage

Actual61 recorded its first seed89.66mm OUTSIDE the horse, missing a radial ray.
Its rig and mesh matrices are identical. Therefore the earlier axis explanation
is NOT the cause in this file. Keep the rig-frame contract, withdraw that causal
claim. The inspected raw seed omitted the reference fitting projection.

Bake the existing fitted pad shape at quiet283, subdivision2, before thickness,
with original material/UV. Bind THAT dense fitted reference to the horse using
Surface Deform, then use it as the stable per-frame seed. The old base cage is
never substituted for the approved/fitted reference. Remove temporary seed
helper after baking; retain one declared native output/cache.

An already-clear border can legitimately overhang the horse silhouette. If a
cross-body ray misses, preserve only a seed with measured positive7mm clearance
(more than3mm thickness). Otherwise test an exterior ray along its actual nearest
surface normal; never a direct nearest-point snap through another fold. Missing
hit or250mm jump still fails. All final thickened face/vertex checks remain.

Original geometry/materials/motion/actions stay unchanged; only the declared
derivative cache differs. Native proof must test the reference bind, guards,
all39contact states and actual renders. No success inferred from the diagnosis.
