# Retrospective workflow implementation proposal

Status: proposed, not implemented or adopted. This consolidates the discussion
following the [Nihang retrospective](../../results/sikh348/RETROSPECTIVE.md).
The goal is fewer avoidable Director corrections and better production progress
at the existing quality floor, not more documentation or more internal rejections.

## Recommendation

Extend the existing controller with an event-driven retrospective policy and
persistent obligations. Capture a small outcome record at existing review points;
invoke a causal retrospective only when specific evidence warrants it. Require
its consequences in the next admitted plan and test their effectiveness later.
Reuse the current event store, planning stages, native admission path, knowledge
packets and resource manifests. Do not introduce another service, model, mandatory
subagent or separate paid inference path.

Use three responses, not one universal pause:

1. **Outcome capture:** a compact record after each attempt or useful proof.
2. **Targeted revalidation:** recheck affected proofs after a dependency or use
   change. This is not automatically a full retrospective.
3. **Causal retrospective:** compare attempts, assumptions and actual outcomes
   when a method fails repeatedly, a critical result regresses or a strategy is
   contradicted. Route the response to the affected planning stage.

## Critical changes to the earlier proposal

### Triggering only after final review misses the actual work loop

The current `Controller.submit` handles final review, but native steps have their
own `NativeAdmission.record_review` path. Many335 attempts stop before a complete
candidate reaches final review. Worker failures, step rejections and planning
challenge outcomes must feed the same policy; otherwise the expensive loop can
continue without the retrospective ever running.

### A dependency change is not necessarily a failure

A changed rig or garment method invalidates affected reuse claims. It should
first require a compatibility check, not a broad causal audit. Escalate when that
check fails materially, loses a protected result or exposes an unsupported
foundational assumption. Byte changes establish drift, not semantic incompatibility;
the affected interface and meaning need review.

### Two failures cannot mean two arbitrary cycles

Correction counters currently mix artistic experiments, planning repairs,
technical failures and evidence recovery. Keep those authorized counters intact,
but classify outcomes separately for diagnosis. A failed import is not an artistic
test; a deliberately bad control is not a failed production attempt.

The adopted [strategy rule](../decisions/0005-production-strategy-before-execution.md)
already calls for reassessment after three similar unsuccessful variants. Preserve
that default rather than silently replace it with the earlier proposed two-attempt
hard stop. At the second relevant failure attach a trend warning to the next
challenge. At the third, require a causal review. A strategy falsifier, unsupported
foundation or critical regression still triggers immediately. These are explicit
initial policy settings, not empirically optimized thresholds.

### A retro cannot prove its remedy before execution

Separate **response admitted for testing** from **intervention demonstrated
effective**. Otherwise a finding blocks the very diagnostic work required to
resolve it. An admitted test may proceed within existing authority; the original
finding remains open. Its next evidence determines effective, ineffective or
inconclusive status. A document or fresh strategy is not closure.

### Persistent IDs help but do not solve semantic misclassification

Defects must reference original requirement IDs, affected assets and test
conditions. Alias or merge issue labels without deleting their history. Retiring
a requirement needs recorded scope/authority reconciliation; generating a new ID
cannot remove an unresolved obligation. Require a disposition for every affected
requirement, including UNKNOWN and NOT_TESTED.

Whether two methods are materially similar, a visual result regressed or a cause
is established remains a reasoning judgment. A method hash only detects code
changes. The system must retain a negative test in which well-formed but false
review claims evade the semantic trigger. Do not advertise deterministic visual
understanding.

### Too many retros would become another failure mode

Merge multiple triggers affecting the same evidence window into one scoped retro.
Do not reopen it on every poll or restart. New material evidence can reopen it;
re-reading the same records cannot. Routine expected corrections remain local.
Successful completion produces a compact reuse/learning record, not a mandatory
essay, and generalizing it into the knowledge base need not delay an otherwise
qualified Director review. No new routine Director approval point is added.

## Trigger policy

| Event | Deterministic action from recorded evidence | Reasoning still required |
|---|---|---|
| Worker finishes or fails; native-step review; final review; planning challenge | Persist outcome and evaluate policy once per event | Classify failure stage, evidence quality and affected requirements |
| Same requirement remains unresolved after two relevant similar attempts | Add warning to next challenge | Confirm comparability and whether meaningful uncertainty was reduced |
| Third similar unsuccessful variant | Open scoped causal retro before dependent attempt | Determine why local repair is not converging |
| Explicit strategy falsifier observed or unsupported foundational assumption found | Open immediate causal retro | Match actual evidence to the falsifier; distinguish expected negative controls |
| Protected useful proof regresses | Hold affected dependent use; open integration retro | Identify scope and whether apparent regression is a changed condition |
| Body, rig, representation or intended use changes | Invalidate affected qualification and require targeted revalidation | Map dependency impact; do not interpret every file change as a new rig |
| Revalidation fails materially or integration loses the prior useful form | Escalate to causal retro | Identify interface fault versus invalid original proof |
| Correction allowance exhausted | Require cross-cycle synthesis before continuation request; preserve exhaustion | State viable next method and Director-owned consequences |
| Work package accepted, abandoned or terminally blocked | Capture scoped successes, failures, reuse limits and unresolved questions | Select lessons worth promoting rather than restating all events |

Missing classification/evidence causes a narrow evidence-reconciliation hold,
not an automatic claim that the creative method failed. Repeated infrastructure
failure routes to technical diagnosis rather than a horse-animation retrospective.
The Director may request a retro at any point. Task age alone does not impose an
arbitrary elapsed-time deadline.

## Records and state model

Keep additive versioned records associated with the existing deliverable lineage:

- **Attempt outcome:** task/attempt/event IDs; requirement and issue references;
  planned hypothesis/falsifier; actual operation/recipe and source bindings;
  production versus diagnostic/negative-control role; outcome stage; observation,
  evidence and uncertainty; affected dependencies and preserved/regressed proofs.
- **Useful proof:** exact artifact/version; demonstrated property; source body/rig
  or other interface; tested use/conditions; failed or untested uses; provenance and
  validity status. Reuse the resource-manifest structure rather than inventing a
  second asset registry. Useful is not synonymous with Director-accepted.
- **Retrospective obligation:** policy version, triggering events, affected branch
  and downstream requirements, evidence window and open findings.
- **Response and follow-up:** causal candidates with confidence, discriminating
  test, retain/change/abandon rationale, affected planning stage, expected evidence,
  admission digest, and later effective/ineffective/inconclusive disposition.

Use an orthogonal obligation state rather than replacing the task's main state.
A task can simultaneously be REPLAN_REQUIRED because its budget is exhausted and
have an open retrospective. Completing the retro does not remove exhaustion.

The proposed lifecycle is: required, analyzed, response admitted for testing,
effect evaluated. An ineffective result returns to targeted reassessment using
the new evidence; an inconclusive result names what evidence is missing. A
supported decision to retain the method needs a discriminating rationale, not
the word “continue.” Corrected reviews append superseding events and recompute
the affected obligations without erasing original evidence.

## Execution and review sequence

1. **Route first.** Preserve lightweight display, research and operational routes.
   A retrospective routes as analysis/planning; it grants no native effects.
2. **Record an event and evaluate triggers transactionally.** Duplicate callback
   or retry IDs cannot create another obligation or consume another correction.
3. **Assemble a bounded evidence packet.** Include original intent and roles,
   relevant attempt outcomes, decisive source excerpts, actual media bindings,
   useful proofs and existing applicable lessons. Summaries do not replace evidence.
4. **Analyze in a fresh review context.** Consider alternative explanations and
   missing evidence, distinguish strategy from implementation failure and identify
   the smallest test that could change the decision. Fresh context is not an
   independent expert or an automatic new model/API call.
5. **Challenge the response using the existing planning mechanism.** Route source
   issues to grounding, requirement gaps to derivation and method problems to
   strategy. Bind the retro findings to actual operations and expected observations.
6. **Admit the next scoped attempt only if all prerequisites and authority hold.**
   Admission for a test is not resolution of its underlying finding.
7. **Evaluate the intervention against new evidence.** Capture retention and
   regression of prior useful results as well as the targeted defect. An unchanged
   failed method cannot be legitimized by renamed files or another vague promise.

No automatic interruption of an already-running render is necessary. Freeze its
inputs and preserve its outputs; block dependent dispatch if new evidence affects
their validity. Unrelated authorized work can continue if its independence is
established. Unknown dependency relationships require reconciliation, not a guess.

## Implementation boundaries

The first implementation should add a pure policy evaluator and additive records
to the current controller, with one shared admission check. Wire that check into:

- full review submission and planning challenge outcomes;
- native-step verdicts and terminal worker outcomes, including failures before a
  candidate/save exists;
- replan, revise, reground, recovery and allowance-extension continuations;
- native dispatch and heavy-job acquisition;
- covered delivery and readiness checks so a stale receipt cannot bypass a hold.

In the present code the key surfaces are `production_workflow.py` (`submit`,
`_planning_submit`, `replan`, `revise`, `reground`, recovery, `job`, `deliver`) and
`native_admission.py` (`dispatch`, `record_review`, terminal run recording).
Implementation must enumerate any other direct writers/launchers in use and
either connect them or explicitly exclude them from the enforcement claim.

Bind admission to the current event sequence, brief, dependencies and policy
version. Recheck it while acquiring the existing job lease; reject stale tickets
after new findings. The trigger write and resulting hold must be atomic with the
terminal outcome. Recovery after a crash recomputes the same obligation rather
than dropping or duplicating it. Do not hold a database transaction while an LLM
reasons or Blender renders.

This is enforcement on registered workflow paths, not a security sandbox. It
cannot prevent an agent from bypassing all project tools with an arbitrary shell
command or falsely describing its evidence. Operational rules and semantic
qualification remain necessary.

Preserve all existing authority semantics. Bookkeeping a retro grants no new
attempt. Planning repairs and production corrections retain their existing shared
accounting; avoid double charging one transition, but do not create “free” repairs
by relabeling them retrospective work. Existing provider/live-call limits remain
unchanged. No mandatory parallel agents or additional heavy workers are required.

## Learning retrieval and promotion

Maintain observation, supported scoped lesson and prospectively tested intervention
as different statuses. Even a tested intervention carries conditions and limits;
one result is not a universal principle. Contradictory later evidence can revise it.

Active findings belong in the current task packet immediately. General lessons
enter the curated knowledge catalog only after source reconciliation, applicability
review, duplicate/conflict checks and routing tests. Keep original source pins and
history. The next task must link a retrieved lesson to a chosen action and later
evidence before recording application. Retrieval alone is not application.

New lessons should replace or refine redundant guidance, not inflate every prompt.
Surface a small current summary and fetch decisive source/media evidence when
needed. Expose progress states such as “integration retro: comparing garment proof
with changed rig” without automatically asking the Director to approve methods.

## Qualification and rollout

### Phase one offline implementation proof

Use mocks and frozen evidence only. Add table-driven and state-machine tests for:

1. Each trigger and its non-trigger counterpart, including expected negative
   controls, unrelated defects and a routine compatible dependency change.
2. Native failures before final review; rejected planning challenges; successful
   saves followed by appearance failure; infrastructure versus artistic outcomes.
3. Renamed/merged issues, new task names within one deliverable, and changed
   methods that do not change the underlying failed assumption.
4. Duplicate/out-of-order events, crash/restart, stale tickets, concurrent dispatch,
   corrected review history and idempotent obligation merging.
5. No bypass through recovery, replan, reground or allowance extension; no reset or
   double charge of correction counters; exhausted tasks remain exhausted.
6. A response can admit its diagnostic test while its finding stays unresolved;
   unchanged failures reopen the appropriate obligation rather than deadlocking.
7. Independent authorized branches remain usable; changed shared dependencies hold
   affected branches; unknown impact is reconciled.
8. Useful-proof validity, acceptance scope and no promotion of technical metrics
   into visual/motion/audio acceptance.
9. Knowledge routing includes relevant lessons, excludes irrelevant ones, rejects
   stale sources and preserves untested status.
10. Well-formed false review claims remain an explicit semantic negative control,
    not an omitted failure concealed by passing schema tests.

### Phase two historical semantic rehearsal

Use348 cases: c13 missing neutral proof,23→24 transfer,34→35 shell substitution,
c48 predicted failure, motion12 narrow success, and51 missing saddle binding.
Also include countercases from routine technical recovery, approved reuse and
lightweight display requests. Predeclare expected decisions before running each
replay. These are familiar, hindsight-assisted regressions, not blind validation
or measured prevention of past mistakes.

Check the generated response against actual operations, not merely required JSON
fields. A proposal that says “rebuild garment” but executes body-shell smoothing
must remain a semantic failure even if its structure is valid.

### Phase three prospective scoped pilot

Before renewed Nihang construction, explicitly migrate its state and known
findings into a versioned record. Preserve52/12 exhausted limits; do not infer
complete historical semantics from the numeric inventory. Reconcile any stale
knowledge/engine bindings, never blindly repin them. No renewed native work occurs
without its separate correction authority.

Activate the tested policy for that scoped package with automatic triggers and
manual source/evidence reconciliation alongside it. A silent shadow mode alone
would repeat the adoption failure; it may diagnose tests, but cannot count as
production enforcement. Retain the original policy/version for recovery. If the
new mechanism breaks, preserve holds and allow read-only diagnosis or independent
work; do not disable it to force dependent production through.

The pilot exit requires correct native-step/final-review integration, no bypass
or counter drift, a genuinely changed and tested response to any triggered
finding, and measured audit overhead. A better render alone does not validate
the trigger mechanism; a blocked bad render alone does not validate production
improvement. Expand beyond the registered production route only after its proof;
the common record can later support story, sound and engineering workflows.

## Measures and decision boundary

Track recurrence after a diagnosis, useful proofs retained through integration,
whole-beat obligations closed, Director-discovered avoidable defects and escaped
triggers. Also track unnecessary holds, retro work time/calls, evidence-recovery
cost and time spent waiting on the Director separately. Union overlapping work
and expose capture gaps. Manual review of sampled non-trigger events is needed
to estimate missed triggers; counting fired triggers alone cannot do that.

Do not optimize for fewest failures or handoffs at the expense of useful exploration
or the quality bar. There is no justified percentage efficiency forecast yet.

The recommendation is to implement phases one and two as one bounded software
package, with a documented migration plan for phase three. This request authorizes
the proposal only. Native correction allowances, spending and live-model calls
require their existing separate authority. No new routine Director choices about
algorithms are introduced.
