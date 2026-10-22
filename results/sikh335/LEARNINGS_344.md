# Carry-forward findings from the fifth shared continuation

These are implementation findings, not an artistic pass or a claim that the
whole workflow is qualified. Earlier failures remain available for comparison.

## Test the result of deformation, not the input control

Motion11 had plausible fold/pitch controls but its actual hoof endpoints slowed
before impact. Motion12 controls the last airborne world-space trajectory and
solves the fixed-length leg to it. Actual endpoint residuals, speed progression,
contact frames and images test the result. Carry this into hands, reins, wheels
and feet: a correct channel value is not proof of the visible interface.

Evidence: `motion01/impact-metrics-c12.json`, `motion01/landing-review-c12.md` and
`tests/test_nihang344_arrival.py`. Complete rearing rhythm is still a separate
full-speed judgment; do not generalize the narrow result.

## A valid dependent layer can faithfully follow an invalid base

Correction34 bound sash and belt to the coat successfully. Its actual posed
images exposed severe coat/body intersections. Measuring layer-to-coat distance
did not establish coat-to-body validity. Correction35 constructed the coat on
the actual rest-body surface, retained anatomical weights and then bound the
outer layers. Chest/shoulder coverage and layer visibility recovered together.

For the next garment, verify each dependency in order: body and pose; garment
fit and ownership; outer layers; contact; complete silhouette. Use the existing
three-phase proof before an expensive complete bake or ensemble copies.

## Coordinate selection is not anatomical ownership

The pants generator selected vertices by height. Low rest-pose fingertips fell
inside that interval, creating blue rings around the fingers. Earlier attempts
to fix cuffs were correcting the wrong object. Correction36 removed 1,372
vertices from these hand islands and the actual front images confirm their
disappearance. A regression test now excludes those fingertips from pants.

When an artifact survives an apparent repair, identify its actual object and
vertex/bone ownership before another geometric adjustment. Apply this to crowd
costumes, saddle pieces and all future body-derived garments. The pant extent
test is specific to this donor; a different donor requires new ownership tests.

## Continuity and layer order are separate checks

Extending the skirt closed a gap but hid the waist wrap in36. The final37
correction retains the longer coat and reduces the skirt extension. Test both
coverage and which layer should be outside, from front and reverse, in actual
seated/action poses. Do not accept one while silently breaking the other.

## Thumb opposition is not four-finger curl

The original common curling-axis method left long sideways thumbs. Correction37
uses the actual index grip as a target for a separate fixed-length thumb chain.
Endpoint accuracy is only a technical prerequisite: actual palm orientation,
finger silhouettes and prop contact still need visual inspection.

## Limits of the current process

The staged controller preserved failed candidates and prevented a false ready
handoff. It did not discover these representation mistakes automatically. The
useful change was an actual discriminating control at the affected interface,
not another generic review checklist. No reduction in Director inputs or
overall production cost has yet been measured from this continuation.

The global native-handler fingerprint also changes when an unrelated handler
is edited. Preserve already-produced evidence and its original fingerprint;
do not rehash it into current admission. Fine-grained handler dependencies may
be a future engineering task, not a reason to bypass provenance now.
