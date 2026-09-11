# Engineering model intelligence

This is the central record of **Codex engineering models**, distinct from the paid API models inside Movie Factory. Previously, model changes were recorded inconsistently in handoffs and conversation history. [events.json](events.json) starts a curated, machine-readable backfill. It is not an automatic capture of Codex runtime settings or token usage.

## Current evidence

| Experiment | Documented sequence | Observed outcome | Limit on interpretation |
|---|---|---|---|
| 3D-03.1 | Astra High diagnosis → Sol implementation | Causal bake diagnosis; subsequent bounded GREEN qualification | Earlier model and Sol effort are not established; production success belongs to the combined workflow |
| 3D-05 | User-reported Sol attempts → requested Astra repair | Earlier Astra thumb-down attempt rejected; subsequent thumb-up/support-clearance campaign passes machine checks; Director requests more coordinated lift motion and notes missing attention | Partial progress, not an Astra repair success or proof that Sol is incapable |
| 3D-01.1 | User recalls a possible Sol → Astra switch | Unconfirmed in reviewed evidence | Exclude from escalation/success counts until corroborated |

Artifact references include hashes at recording. Conversation-derived attribution is labelled as such. Explicitly stated effort is retained; absent effort, timestamps, engineering tokens, engineering costs, and human review time remain null. The experiment's zero API cost does not imply zero engineering cost. Historical model identifiers are reported names, not verified runtime snapshots.

## Capture on each switch and outcome

Append an event when the user announces a switch, an engineering handoff occurs, or a Director outcome changes the assessment. Use a stable unique event ID. Record the experiment, task phase, failure class and trigger, model/effort before and after when known, attribution source, the actual diagnostic or implementation contribution, source commits/run IDs, machine and Director outcomes, and evidence links. Preserve both successful and unsuccessful attempts. Record measured time/tokens/cost where available; do not reconstruct them from subscription limits or API pricebooks.

Keep observations and causal claims separate. A model that inherits a diagnosis, tests, revised fixtures, and additional Director feedback has a different task from its predecessor. Track those changes explicitly. A model switch followed by progress is useful operational evidence, but does not establish that the switch alone caused the improvement.

## Feedback into the Factory design

The historical Sol/Astra routing proposals below are preserved as evidence of the earlier approach. The prospective next-run policy is now in [OPERATING_LEDGER.md](OPERATING_LEDGER.md): Astra Medium for specified work, High for unfamiliar design or unresolved diagnosis, with observed setting/usage attribution. This is a hypothesis, not an automatic switch or controlled comparison.

The Factory should consume this record as an engineering-routing input alongside experiment telemetry. Initial policy hypotheses are:

1. Use Sol High for implementation of a specified, evidenced correction, test integration, replay and packaging.
2. Consider Astra High when a root cause remains unresolved across bounded attempts, particularly coordinate transforms, rig relationships, or conflicting geometric and visual evidence. Escalation requires a concrete diagnostic assignment and a success test.
3. Require anatomical/reference-pose checks when geometry gates pass but the Director rejects human motion. Upgrading the model does not repair a missing validation contract.
4. Hand routine work back only after the corrected pose and approach are demonstrated in short multi-view motion, the relevant negative controls exist, and the remaining implementation steps are explicit.
5. Preserve Director authority for both models. The current Astra attempt belongs in the failure record despite its improved grip measurements.

These are proposed routing rules, not deployed automatic model switching. Qualify them by task class using comparable starting snapshots, prompts, tools, effort settings, budgets, fixtures, and rubrics. Measure cost/time to an accepted result, human intervention, failure detection, and regressions across repeated trials. The observed cases are too few and too confounded to calculate a meaningful model superiority or escalation-success rate.

The subsequent 3D-05 anatomy repair is now machine-qualified in `interaction-v1-20260911T160515Z-85655dd3`, with 76 deterministic checks, ten actual controls, and full playback evidence. It corrects the hand frame, distributes arm roll, moves the prop in front of the character, and clears the support during approach. Director feedback now identifies a rigid-looking lift and slight elbow deformation, plus minor missing head/torso attention. It remains YELLOW pending acceptance, with no invented scores or major-defect classification. The prior Astra rejection and intermediate failures remain evidence. [Decision 0004](../decisions/0004-motion-design-before-implementation.md) adopts a movement brief before implementation; this is a Factory workflow lesson, not an accepted repair or a model superiority result.

The coordinated-lift Astra follow-up is now an [unscored prototype](../../feasibility/3d/3d-05/prototypes/RESULT.md): measured forearm/elbow participation, rigid prop rotation and head attention improve the intended performance, while a new full-clip skin probe reveals reach-stage stretching. Its diagnostic result remains RED with Director review pending. The controls were strengthened to require failures absent from the positive case. Record both progress and the unresolved concern; no handoff success or paid API evaluator contribution is implied.

The Director subsequently **passed the complete coordinated-lift prototype**, deducting 0.5 points for the sword approaching the forehead at the top of the lift. Keep visual comfort around the head distinct from merely passing a geometric collision/clearance floor. The reach-stage skin probe remains failed; this accepted development performance is not a scored GREEN result. Review duration and absolute/per-dimension scores were not supplied.

The later scored repair is now **closed YELLOW**: technical execution and minimum visual quality passed; timing preference was not demonstrated; no further iteration planned. Both clips received 4.5/5 grasp and 5/5 elsewhere, tied, with approximately 120 seconds of review. See the [closure card](../../results/3d05/EXPERIMENT_CARD.md) and immutable [supplement](../../exports/3d05-closure-v1-supplement/README.md). Prior pending/rejected entries above remain historical observations.

Prospective lifecycle, usage and effort records use the small [local operating ledger](OPERATING_LEDGER.md). Its generated summary exposes coverage; the curated events here remain the cross-experiment learning index. See [3D-06A's learning delta](../../feasibility/3d/3d-06a/SPEC.md) for the next planned changes. No 3D-06A animation has run.
