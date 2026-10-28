# Integrated workflow397 — implementation and operating contract

Director392–397 adopts this framework and its scoped implementation, testing,
migration, Git push and verified replacement-backup retention. The primary goal
is finished footage at the accepted quality floor, with fewer avoidable Director
inputs. Infrastructure work does not count as artistic progress.

## Mandatory sequence and boundaries

Router332 remains first for every request. It selects lightweight operations or
the existing serial planning330 pipeline. No extra LLM sessions are required for
deterministic steps. Planning grounds exact sources, reference roles, Director
preferences, same-film requirements and applicable expert lenses. It translates
these into requirements, a causal micro-task, operation/proof dependencies and
a fresh completeness challenge. Execution consumes that admitted contract;
review consumes the original intent, contract, actual artifacts and failures.
A failed gate routes repair to its owning stage and invalidates dependent work.

`production_contract397` is required for newly admitted local-native briefs.
Every requirement has a typed criterion (measurement, evidence, judgment or
authority), criticality, assessment owner, explicit cells, coordinate space,
render/use profile, reference roles and invalidation condition. A numerical
criterion names calibration, negative control, metric key, comparator and bound.
The review reads the value from a hash-bound JSON artifact. A subjective rating
cannot be substituted for a measurement. Missing/ambiguous evidence blocks.
Human audiovisual requirements remain pending for the Director under313;
timed frames, tests and model declarations do not qualify full-speed AV.

## Micro-task admission and decomposition

Each scope states one discriminating question, first executable proof, success
and failure branches, smaller possible proof and an explicit coupling
counterexample. Changes share one causal control; unavoidable coupling must be
explained. Invariants identify ownership: Director intent, consuming interface,
method assumption or calibrated numeric bound. Do not preserve a failed method's
incidental property as though the Director required it.

Splitting creates at least two named child proofs, acceptance conditions, their
ordered dependency graph and current child. Merely writing “split” is invalid.
Two ineffective/inconclusive experiments on a stable feature force scope
reassessment. Finding count is not experiment count. Reassessment must select
split, keep, merge, change method or retire and bind the actual next operation;
the subsequent plan must apply that exact decision. A response alone does not
prove its remedy effective. Retros evaluate against new same-plan outcomes.

Proof dependencies distinguish transport, target form, pose form, continuous
performance and finish. Fitting/binding consumes qualified target form;
dense caches/finish consume qualified pose form. Actual native recipes and
reviewed prerequisite artifacts are checked at dispatch. Inherited custom
handlers cannot be relabeled as numeric transport to bypass this ordering.
Input proofs bind their qualification conditions and evidence. Changes outside
those conditions require new proof. Transport success is never art acceptance.

## Accounting, forward momentum and stopping

Append-only governance events live in `.runtime/factory-entry.sqlite3` alongside
the existing controller history. Hierarchy is release → milestone → capability
→ method family. Every prospective task has a finite allocation under those
ancestors; task/cycle identity counts once across stage retries and family
renames. Reservations count investment; completed outcomes count feature age.
Technical failures consume the existing cycle rather than granting free retries.
Original correction ceilings remain independently binding. Migration records
historical counters, evidence, gaps and any defensible feature-age floor. It
never invents a complete historical cycle census or refunds prior effort.

Defaults adopted for this implementation are **review every10 completed cycles
without a new retained scoped proof; stop at20**. They are provisional watchdogs,
not experimentally optimal numbers or automatic Director-review cadence. Task
profiles may differ only with a bound exact Director-approved profile. After
10, an internal investment/scope reassessment is mandatory. At20, or retirement,
construction stops and the agent recommends reallocation/viable bounded
alternatives. A larger generic cycle grant does not revive the method. A narrow
exception requires exact human-backed assignment, recipe hashes, finite existing
allowance and expiry; no automatic variants or renewal.

Allocation amendments require exact old/new approval and cannot refund spent
cycles, exceed original task authority or overallocate ancestors. No whole-film
cycle budget is invented. Release completion uses qualified milestone proofs
and declared weights, never consumed cycles or unreviewed candidate counts.
Director394's 1.5/12 =12.5% remains a rough scenario, not measured completion.
The agent must explain opportunity cost and recommend stopping a failed path;
it cannot keep asking for more cycles merely because success is unfalsifiable.

## Contradiction-first review and handover

Inspect the most revealing failing pose/region first, then intended framing,
reverse/partial poses, temporal boundaries, full beat and adjacent interfaces.
Each typed cell binds candidate/source/mode and observation. A known rejected
artifact, failed cell, failed native outcome or missing proof blocks aggregate
PASS. Retained scoped proofs are distinct from current-feature progress credit;
a later regression revokes credit without falsifying a previously valid artifact.

Only the Director can approve creative acceptance/release. No artistic pass is
claimed for397. Existing accepted motion66/75/80 and Pashtun20s remain protected;
the inherited horse's continuous anatomy is unqualified. Director handoffs occur
for integrated review, completion or a material decision; not algorithms,
incremental improvement or routine internal replanning. Name visible outcome,
included/excluded scope, evidence, remaining blocker and next package/exit test.

## Context, administration and recovery

Retrospective caches are derived, versioned, hash-checked projections. Full replay
remains the recovery oracle; superseding history forces replay. Atomic batched
retro actions preserve individual evidence/history while avoiding repeated large
controller-state copies. Planning packets emit phase-relevant bodies plus the
complete dependency manifest; mandatory context exceeding its declared bound
blocks rather than truncates. Authority and source grounding retain their
separate bounds. No end-to-end token or quality saving is asserted.

Explicit397 current-state adoption reads canonical governance instead of silently
repinning the obsolete307 capsule. The strict307 delivery route remains unchanged.
An opt-in status projection excludes only date and exchange-count cosmetics;
new/deleted/substantive fields invalidate it, and the original snapshot remains.
Legacy two-field source bindings still use strict whole-file hashes. Other
source updates require inspected diffs and reviewed pin reconciliation.

For current state run `context_hygiene current`; for governance run
`production_workflow governance --help` or use `Controller.governance_status`.
Node/migration/scope/retirement/exception/allocation actions use
`Controller.governance` and exact source-bound records. Public request IDs are
idempotent; changed retries conflict. No public arbitrary proof-PASS action exists.
Raw chat/OS tools remain outside interception: core instructions supply that
boundary. The mechanism constrains declarations and operations, not semantic truth.

## Qualification, rollback and protection

Offline tests exercise real Controller/Bridge mock dispatch, bad prerequisites,
contradictory reviews, accounting, stale evidence, cache replay and retention
failures. Historical replay compares full and cached interpretation on original
events. These are authored regressions, not independent artistic validation or
prospective proof of fewer Director inputs. Full local replay timings have only
their measured scope. Subsequent production must prospectively track escapes,
avoidable handovers, retained feature proof, cycles to acceptance and opportunity
cost. Preserve the semantic false-pass negative control.

Migration uses a consistent pre-migration SQLite backup at an idle boundary,
unchanged old counters/limits and hash-verified protected masters. Older native
plans remain subject to fresh engine/source admission; migration cannot clear
old artistic/retro findings. Rollback may restore software or derived caches but
must reconcile all spent cycles and retirement events; never replace history with
an older permissive database. No destructive schema rewrite is required.

Git pushes exclude native assets/secrets and preserve scoped commit history.
Recovery includes native/evidence/runtime state with consistent SQLite copies;
credentials, reproducible tooling and backup staging are excluded. S3 is private,
versioned and encrypted. A new manifest, full inventory and representative
streamed SHA256 restore must pass before old active generations or unreferenced
eligible object versions are deleted. Archived manifest references protect their
payloads. Unknown retained schema blocks cleanup. Retain one latest active copy,
not multiple hidden versioned copies. Local history is never deleted by retention.
