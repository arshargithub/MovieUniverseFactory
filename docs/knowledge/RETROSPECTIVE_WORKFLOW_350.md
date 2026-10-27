# Retrospective workflow and operating procedure

**386 extension:** [scope and effectiveness contract](MICRO_APPEARANCE_WORKFLOW_386.md).
New version2 interventions require scope/causal reassessment and a tested outcome
disposition before a replacement remedy. Failed tests can be evaluated by explicit
admission identity after reopening; this never closes unresolved/newer art.

**378 extension:** [purpose-qualified references](REFERENCE_READINESS_378.md)
adds `reference_gap` as an immediate outcome trigger. Current-contract responses
must assess retain/supplement/replace/no-reference-issue with bound evidence;
input gaps require Grounding, while adequate-reference execution failures retain
their targets. See the new contract for compatibility and semantic limits.

Exchange350 implements the offline controller portion of the approved349
proposal. The purpose is to make failures change the next operation, preserve
useful results through integration and avoid repeated Director corrections.
There is no new service, paid model call or mandatory subagent. The existing
controller records outcomes and enforces admission; the working agent performs
the causal reasoning and evidence review.

## When it runs

Native worker outcomes, native-step reviews, planning challenge rejections and
final reviews append retrospective events in the same transaction as their
corresponding result. Repeated callbacks are idempotent. An unsuccessful worker
is a technical outcome, not a claim about artistic quality.

| Recorded evidence | Controller response |
|---|---|
| Second distinct failed attempt against an unresolved requirement | Warning in the next packet |
| Third distinct failed attempt | Scoped causal-review obligation; dependent execution blocked |
| Strategy falsifier, unsupported foundation or regression | Immediate obligation |
| Missing or ambiguous evidence classified UNKNOWN | Evidence-reconciliation obligation |
| Changed registered proof use or conditions | Targeted revalidation, not automatically a broad retro |
| Exhaustion through review or manual replanning | Cross-cycle synthesis obligation; exhaustion remains separately binding |
| Completed scoped review | Compact closure record with pending Director status; no production acceptance inferred |

Multiple views of one attempt count once. Expected negative controls do not count
as failed production variants; an unexpected falsifier in a control still matters.
PASS does not close an existing obligation. NOT_TESTED remains visible in history
but is not automatically a creative failure; existing prerequisite/review checks
still govern required missing evidence.

The first version groups repeated failures conservatively by stable requirement
and attempt identity. It does **not** infer whether techniques are semantically
similar from a method name or code hash. A technically different method can still
trigger reassessment if the same requirement remains unresolved. The agent must
reconcile comparability and uncertainty in its response. This may cause an early
internal review, not another automatic Director handoff.

## Responding to a trigger

1. Read `Controller.retrospective_packet(task)` and retrieve the indicated original
   events with `retrospective.events(connection, task)`. Read the actual bound
   evidence and original intent/reference roles; do not reason only from the
   compact packet. Relevant348 garment and motion findings remain required
   sources for the next Nihang proof.
2. Identify causal alternatives, uncertainty, the useful result to preserve and
   the smallest discriminating test. Distinguish missing evidence, implementation
   fault, integration fault and failed strategy. Explain retain/change/abandon.
3. If the work plan must change, use existing `replan`, `reground` or authorized
   `revise` at the earliest affected planning stage. These retain shared limits
   and invalidate downstream artifacts. Retrospective bookkeeping itself neither
   grants corrections nor executes the proposed repair.
4. Record a response tied to the current brief and exact open finding. Challenge
   its causal test, actual method, preservation and authority separately. The
   challenge must state a counterexample and bind evidence. Admission checks the
   source hashes, plan and event state again.
5. An admitted response enters TESTING. Only the currently admitted plan may run,
   within existing authority. The original finding is not resolved merely because
   its proposed remedy sounds plausible.
6. Record the new outcome and evaluate effective, ineffective or inconclusive.
   Effective requires a subsequent matching production/diagnostic PASS against
   that plan with fresh evidence. A worker success or negative-control result
   cannot close an artistic finding. Failure or uncertainty reopens the review.

The challenge records are an internal review responsibility, not new Director
approvals. If an exhausted allowance or material creative choice requires the
Director, provide the cross-cycle synthesis, concrete alternatives and one
recommendation. No existing limit is enlarged by this mechanism.

## API and persistent records

`Controller.retrospective(task, action, data, event_id)` provides these actions:

- `outcome`: attempt, role, origin, observations and source bindings. Observation
  fields are requirement, status and actual observation; optional boolean flags
  are falsified, foundation, regressed, dependency_changed and reference_gap. Corrections name
  `supersedes`; original events remain immutable.
- `response`: key plus response containing cause, uncertainty,
  change_or_retain_rationale, preserve, test, expected, failure_response,
  target_stage, plan digest, gate digest and evidence bindings.
- `admit`: key plus challenge containing response_event, the four PASS checks
  with observations, counterexample and evidence bindings.
- `evaluate`: key plus evaluation containing result, outcome_event, observation
  and evidence bindings.
- `proof`: id, bound existing resource manifest, tested conditions and requirement
  IDs. This references the existing resource registry; it does not create a new
  asset or promote an unfinished manifest to qualified.

The runnable synthetic examples are in
[`test_retrospective350.py`](../../tests/test_retrospective350.py). Inspect an
initialized task without dispatch using:

```sh
.venv/bin/python -m movie_factory.production_workflow \
  --database .runtime/factory-entry.sqlite3 retrospective --task TASK_ID
```

Events persist in an append-only `retrospective_events` table in the existing
controller database. Its projection is separate from the main task stage. A task
can simultaneously be exhausted and have an open finding. Revision, restart and
allowance extension preserve these records. Repeated event IDs cannot silently
change their contents. Corrections recompute the projection and invalidate any
admission that depended on a superseded finding.

Packets include active findings, warnings, responses and proof references, not
the full attempt history. Closed findings retain a compact disposition. A60,000
character bound blocks oversized packets instead of dropping active obligations.
This is not a measured token or quality gain.

## Proof reuse and integration

Declare reused proofs in `brief.retrospective_proof_uses` with `task` when external,
`id`, `conditions` and, for an adaptation test, `purpose: diagnostic`. Plan
admission binds the exact registered proof version. Its manifest, input bytes,
rights, dependencies and intended conditions are checked again at dispatch and
delivery. A different version requires a new admitted plan; removing a prior
dependency requires explicit reconciliation rather than silently dropping it.

An untested condition may be explored only through a specifically admitted
diagnostic revalidation. This does not waive stale inputs, rights problems or
known failures, and does not update the old proof's qualification. Successful
adaptation requires new evidence and a new appropriately qualified manifest.
Regression in a proof's requirements blocks registered downstream consumers;
independent tasks can continue.

Dependencies must be declared. The controller does not infer unregistered asset
sharing from a Blender scene, and it cannot decide whether two differently named
requirements really mean the same thing. Requirement changes open reconciliation
and preserve old obligations; they do not silently erase them.

## Admission coverage and limits

The guards cover production builder packets/submission, heavy-job acquisition,
native reservation/capability, readiness delivery and replayed delivery receipts.
Native terminal results and step reviews are atomic with their outcome events.
Native capabilities bind the retrospective sequence, so new findings invalidate
an unlaunched reservation. Already-running work is preserved, not killed.

Recovery and allowance paths require current policy and retain findings; they do
not automatically clear them. Main-chat operations on registered paths must
honor the guard. Historical standalone launchers and arbitrary shell commands
are not an OS security boundary; router-first and trusted-handler rules still
prohibit bypassing admission. The inspected native entry remains
`NativeAdmission.dispatch` into the shared Blender runner.

The existing frozen-evidence runtime is not extended with new paid reasoning
calls. In this environment the working agent analyzes the packet and submits
the internal response/challenge. Automatic routing of retrospective reasoning
to a separate live LLM remains unqualified and would need its own authority.

The deliberate false-PASS test remains: well-formed false visual assertions can
evade these triggers. This is evidence bookkeeping and workflow enforcement,
not deterministic artistic judgment. Full-speed AV remains Director-owned under313.

## Migration and learning promotion

Legacy production tasks fail closed until reviewed migration. The implemented
`migrate_retrospective` API requires a source-bound decision, exact current state
digest, coverage, unknowns and evidence. It initializes the policy without
changing correction counts, native/planning pins or creative authority, and opens
a migration-evidence obligation. Migration is not permission to execute.

For the existing Nihang tasks, reconcile the actual335 history with348's audit,
retain52/52 and12/12, register useful proofs only within their demonstrated scope,
and resolve migration evidence before the proposed new bare-deformation/garment
transfer test. Renewed construction authority is still needed. No live task was
migrated in350.

Active findings are supplied by the controller immediately. General lessons are
not automatically promoted into the global retrieval catalog: source audit,
applicability/contradiction review, routing tests and prospective evidence still
apply. This prevents a speculative causal story from becoming a universal rule.

## Qualification and next proof

[Software verification](../../results/workflow350/VERIFICATION.md) records tests,
historical rehearsals and limits. Seven known-history classifications test policy
behavior; they are not blind prediction or newly inspected media. No reduction
in Director inputs, production time or rework is yet established.

The next production test should measure whether the bare deformation and23
garment transfer proof preserves useful form, changes the method when falsified,
and closes whole requirements without avoidable Director corrections. Track
false-positive holds, escaped findings, retained proofs, recurrence after causal
review, Director corrections and measured work/render time. Do not optimize for
the number of retrospectives or the number of internally rejected candidates.
