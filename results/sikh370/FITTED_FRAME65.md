#65 per-frame fitted seed; first-lift counterexample first

64 reached the end of the loaded phase but failed total displacement at313:
PAD370_TOTAL_CONTACT_JUMP. No native derivative was saved. Partial positive
clearance is not enough; the contact solver/binding combination is rejected.

Change one interface: seed each frame from the original pad's ACTUAL evaluated
fit, rather than propagating a reference fit with Surface Deform. Original wrap
can miss face interiors, so retain minimum-intervention vertex/face correction,
render-matched horse, thickness and all displacement guards. Stable topology/UV
and original horse/rider actions remain mandatory. Surface-deform attribution is
a hypothesis: the new proof discriminates the seed interface, not model quality.

Evaluate313/314 FIRST, then276..312 without changing the animation time. This
catches the known expensive late counterexample before processing the whole
interval. Native cache remains39 keys at original frame indices; report sorts
chronologically. Missing/jumping/negative contacts fail. No guard relaxation,
new parameter family, tool, spend, scope or correction-cap increase.

If first-lift proof fails again, inspect actual offending positions instead of
running the full interval or offsetting harder. Even a numerical pass must survive
all side/oblique/shot and whole-preparation rendered review for float/fold/jitter.
