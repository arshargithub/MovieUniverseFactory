# Engineering model intelligence

This is the central record of **Codex engineering models**, distinct from the paid API models inside Movie Factory. Previously, model changes were recorded inconsistently in handoffs and conversation history. [events.json](events.json) starts a curated, machine-readable backfill. It is not an automatic capture of Codex runtime settings or token usage.

## Current evidence

| Experiment | Documented sequence | Observed outcome | Limit on interpretation |
|---|---|---|---|
| 3D-03.1 | Astra High diagnosis → Sol implementation | Causal bake diagnosis; subsequent bounded GREEN qualification | Earlier model and Sol effort are not established; production success belongs to the combined workflow |
| 3D-05 | User-reported Sol attempts → requested Astra repair | Earlier Astra thumb-down attempt rejected; subsequent thumb-up/support-clearance campaign passes machine checks and awaits Director playback | Partial progress, not an Astra repair success or proof that Sol is incapable |
| 3D-01.1 | User recalls a possible Sol → Astra switch | Unconfirmed in reviewed evidence | Exclude from escalation/success counts until corroborated |

Artifact references include hashes at recording. Conversation-derived attribution is labelled as such. Explicitly stated effort is retained; absent effort, timestamps, engineering tokens, engineering costs, and human review time remain null. The experiment's zero API cost does not imply zero engineering cost. Historical model identifiers are reported names, not verified runtime snapshots.

## Capture on each switch and outcome

Append an event when the user announces a switch, an engineering handoff occurs, or a Director outcome changes the assessment. Use a stable unique event ID. Record the experiment, task phase, failure class and trigger, model/effort before and after when known, attribution source, the actual diagnostic or implementation contribution, source commits/run IDs, machine and Director outcomes, and evidence links. Preserve both successful and unsuccessful attempts. Record measured time/tokens/cost where available; do not reconstruct them from subscription limits or API pricebooks.

Keep observations and causal claims separate. A model that inherits a diagnosis, tests, revised fixtures, and additional Director feedback has a different task from its predecessor. Track those changes explicitly. A model switch followed by progress is useful operational evidence, but does not establish that the switch alone caused the improvement.

## Feedback into the Factory design

The Factory should consume this record as an engineering-routing input alongside experiment telemetry. Initial policy hypotheses are:

1. Use Sol High for implementation of a specified, evidenced correction, test integration, replay and packaging.
2. Consider Astra High when a root cause remains unresolved across bounded attempts, particularly coordinate transforms, rig relationships, or conflicting geometric and visual evidence. Escalation requires a concrete diagnostic assignment and a success test.
3. Require anatomical/reference-pose checks when geometry gates pass but the Director rejects human motion. Upgrading the model does not repair a missing validation contract.
4. Hand routine work back only after the corrected pose and approach are demonstrated in short multi-view motion, the relevant negative controls exist, and the remaining implementation steps are explicit.
5. Preserve Director authority for both models. The current Astra attempt belongs in the failure record despite its improved grip measurements.

These are proposed routing rules, not deployed automatic model switching. Qualify them by task class using comparable starting snapshots, prompts, tools, effort settings, budgets, fixtures, and rubrics. Measure cost/time to an accepted result, human intervention, failure detection, and regressions across repeated trials. The observed cases are too few and too confounded to calculate a meaningful model superiority or escalation-success rate.

The subsequent 3D-05 anatomy repair is now machine-qualified in `interaction-v1-20260911T160515Z-85655dd3`, with 76 deterministic checks, ten actual controls, and full playback evidence. It corrects the hand frame, distributes arm roll, moves the prop in front of the character, and clears the support during approach. It remains YELLOW pending Director acceptance; the prior Astra rejection and intermediate failures remain evidence. Do not count this as an accepted repair or hand it off as proven natural motion before that review.
