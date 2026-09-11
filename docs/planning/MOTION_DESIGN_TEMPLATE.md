# Human motion design brief

Complete this brief before production animation changes. Label unknowns and draft values; freeze numeric thresholds before scoring. This is an engineering artifact, not an extra permission form.

## Intention and scope

- What should the action communicate, and how should effort, speed and prop weight read?
- Which character, rig, prop, source revisions and accepted evidence are reused?
- What is required, optional or intentionally absent? Include explicit reasons for stillness.
- What Director observations prompted this pass? Preserve their exact wording separately.

## Reference and movement phases

Identify the reference clip or annotated authored pose board, its provenance, and the observations actually checked. Do not imply a human reference was reviewed when it was not.

| Phase and timing | Visible intention | Head/torso contribution | Shoulder/elbow/forearm/wrist contribution | Prop/contact and clearance |
|---|---|---|---|---|
| Anticipation | | | | |
| Reach/preparation | | | | |
| Contact/load | | | | |
| Main action | | | | |
| Deceleration/hold | | | | |

Define key poses, trajectories, orientation changes, ordering/overlap, and easing. Check the whole sequence, rather than fitting only its final pose. Describe why each participating joint moves and how neighboring joints accommodate it.

## Constraint compatibility

- Which transforms are fixed in world space, relative to a parent, or free within a bound?
- Does a world-space lock prevent the planned articulation?
- Which object owns each contact, and how are position and orientation continuous at transfer?
- Which bones may be edited? How will descendants be evaluated when torso/head motion is added?
- How are support contacts, limb lengths, balance cues, and evaluated mesh shape protected?
- Which timing changes are permitted, and what must be exactly or numerically preserved outside the interval?

## Review and validation contract

Separate geometric safety, temporal coordination and aesthetic judgment. Define measurements, sampling, numerical thresholds, their rationale, and actual scene/action controls that should fail them. Include contacts, unwanted intersections, pose/mesh deformation, joint trajectories, speeds, boundary continuity and replay.

Define what improvement should be visible before showing the scored result. Use full synchronized playback from an overview and contact/deformation views. An angle-range pass does not establish natural movement. Record Director observations, scores when supplied, and review time without inferring missing values.

## Ready for implementation / ready for scoring

Record the unresolved design choices, a bounded preview assignment, and its stop conditions. Confirm constraint compatibility before production implementation. Confirm complete preview evidence and freeze source/configuration, thresholds and evaluator budget before scoring. State whether the brief is manually authored, API-assisted or generated; account for those activities separately.
