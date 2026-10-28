# Framework400 conformance audit — substantial foundation, incomplete conformance

Director requested verification before production resumes. This is a source/code/
state audit by the same agent with fresh adversarial probes, not an independent
model audit or a production pilot. No implementation repairs, native/media work,
allowance extension, migration, model/provider call or remote mutation occurred.

## Verdict against the goal

The adopted392–396 direction is substantially represented in real Controller/
Bridge code. It is not just policy prose. However, the earlier397 claim of a
complete integrated implementation was too strong. Four deterministic conformance
counterexamples remain, the current full regression is not green, and the live
production-economics configuration is incomplete. Do not describe the framework
as fully verified/production-proven or resume native qualification on that basis.

The goal is finished footage at the accepted quality floor with fewer avoidable
Director inputs. Existing tests establish selected mechanical controls; they do
not establish that that production outcome has improved. The new bounded source
qualification would be a prospective pilot only after conformance gaps close and
its separate allowance is approved. It is not authorized by this audit request.

## Original intent → actual implementation

| Intended outcome | Implementation/evidence | Audit disposition |
|---|---|---|
| Every request routes; production planning is serial, expert/reference grounded and source bound | task_router, planning_pipeline, expert_planning, Controller/Bridge; existing regression exercises stages, omissions and source drift | Implemented at supported entry points. Semantic classification/insight and raw OS-tool boundary remain agent duties. |
| Typed measurement/evidence/judgment/authority, contradictions before aggregate success | production_contracts.review and Controller.review_result; failed-cell/known-bad controls in suite; fresh scalar controls below | Core checks work. Calibration/control provenance is not actually validated. |
| Micro-tasks ask one discriminating question; split decisions change executable order | scope_contract, scope_review, validate_plan; bindings and ordered proof/build operations exist | Partial: contradictory scope decisions and unmapped child prerequisites are admitted. |
| Target form before fitting; pose form before dense cache/finish | operation classes, native recipe classification, actual dispatch prerequisite/run/review checks | Implemented conservative checks. Artistic truth of an asserted form proof is still fallible; not a universally qualified authoring system. |
| Retros evaluate remedies against actual outcomes; ineffective remedies require reassessment | capture_effect, retrospective outcome/evaluate/admit, stable feature counters and batch/cache paths | Implemented for migrated covered tasks. Reassessment's executable split connection has the gaps below. |
| Stable cycle/family/capability investment, no reset on rename/model/replan | append-only canonical events, reserved task:cycle IDs, ancestor caps, same-capability feature continuity | Implemented/tested for enrolled tasks. Not a complete whole-factory/whole-history cycle census. |
| Review at10 and stop at20 charged cycles without retained critical proof | task_progress + guard, retained proof sequence, regression cutoff, retirement and exact exception | Completed-result path works; charged-but-pending peer attempts are omitted from watchdog age. Hard reservation/ancestor caps still count them. |
| A generic allowance cannot revive a retired method | exact exception/recipe/assignment approval and independent old task ceiling | Implemented. Current inherited anatomy remains STOP_AND_REALLOCATE. |
| Progress reflects qualified retained milestones, not attempts; release-linked allocation | release_progress/economics + node hierarchy/allocation APIs | Engine foundation exists; live release has no total weights, prospective allowance0, no prospective cycles. No measured release percentage or whole-projectC. |
| Quantified forward momentum and opportunity cost | prospective cycle/lane counts, burn, feature age, conditional394 scenario | Partial operating coverage. Rolling yield/escape/cost-per-usable-output and a full reconciled baseline are not a populated integrated live scorecard; process/admin outside enrolled tasks is not automatically included. |
| Bounded context/admin without losing obligations/history | phase packets + full dependency digests,24KiB dynamic cap,48KiB source scope, replay-equivalent caches/batching, strict old bindings | Implemented scoped controls; no reduction of this chat's host/history context and no measured end-to-end/token saving. Historical replay evidence is non-independent. |
| Preserve original budgets/masters and rollback history | migration snapshot, exact counters/fingerprints, protected hashes, canonical append-only retirement | Fresh check: appearance261/261, motion80/80, six protected hashes unchanged;806 native runs;0 heavy leases; cached/full governance equal. |
| Verified remote protection before removing old active copies | base/journal restore and retention receipts |397 receipts support completion:35journal members restored/hash-matched, one active generation;103superseded versions/5,085,876,537bytes removed earlier. This audit did not repeat cloud reads. |

## Reproduced conformance failures

Run `.venv/bin/python results/workflow400/probes.py`. It creates temporary SQLite
fixtures and calls actual implementation functions, not the discarded392example
branch function. COUNTEREXAMPLES.json records expected/observed results. These
are validator-level counterexamples; no full native run was attempted or claimed.
The probe program records outcomes and exits normally; its exit0 does not mean
conformance passed. Four of six policy expectations fail; two scalar controls pass.

### F1 — split can be recorded while keep is executed (high)

`production_governance.scope_review` accepts outer decision `split` with diagnostic
`keep`. With no child proofs, `validate_plan` then accepts the same keep diagnostic
and original first operation. The two decision fields are not reconciled.
Source: production_governance.py:455 (scope_review), production_contracts.py:16.
Consequence: scope reassessment can satisfy formal bookkeeping without actually
applying the promised decomposition. This is directly contrary to393's purpose.
Repair acceptance: one canonical decision; conflicting decision fields block;
public Controller tests must prove the changed child/operation is enforced.

### F2 — child proof graph is not joined to execution (high)

A split has a syntactically ordered target→binding child graph, selects binding
as current child without a qualified target, and has only a transport operation.
`production_contracts.validate` admits it. It checks child order/names but does not
bind child acceptance/dependencies to actual operation/proof IDs or eligibility.
Source: production_contracts.py:23 and operation validation at76 onward.
The separate operation-kind ordering still blocks a declared fitting operation
without target form. That protection does not repair the missing split linkage.
Repair acceptance: selecting a child with missing prerequisites blocks; actual
first operation must belong to eligible child and produce its contracted proof;
child completion cannot be inferred from prose or unrelated transport success.

### F3 — numeric calibration provenance can be fictional (high)

A criterion names nonexistent `missing-calibration.json` and
`missing-negative.json`. Validation admits both because it requires only nonempty
strings. Actual scalar comparison does work: a bound measured3against threshold0
cannot be called PASS; measured0can. The weakness is provenance/appropriateness,
not arithmetic. Source: production_contracts.py:62.
Repair acceptance: bind/version calibration and negative-control artifacts with
metric/space/profile/use conditions, validate them before admission, and block
missing/stale/incompatible records. Honest uncalibrated diagnostics may be stored
but cannot silently become qualified production thresholds.

### F4 — charged pending attempts do not age the capability (medium)

In an isolated100-cycle family,21enrolled peer tasks reserve one attempt each,
with no proof and no completed outcome. All21reservations succeed; feature age
remains0. Each spent peer's task allowance is exhausted, but the shared capability
never receives its10/20watchdog alert and a further allocated peer remains a
route around that intended safeguard. Ancestor caps still limit total spending;
normal sequential Controller transitions usually close their prior cycle.
Source: production_governance.py:239–243 counts `completed`, while reservation
charges at427 onward.397docs changed wording to completed without reconciling
394's charged-cycle policy. Pending work must not be fabricated as a visual FAIL,
but its already-charged investment cannot disappear from the watchdog.
Repair acceptance: distinguish charged no-proof age, result/visual attempt age and
unresolved work; enforce the adopted charged investment review/hold across peers,
while allowing already reserved results and last-slot success to finish review.

## Configuration/measurement gaps, distinct from code defects

- Canonical economics currently reports0prospective cycles,0allocation at all
  migrated nodes, no root weight, no required-feature milestone weights and null
  release fraction. These are conservative defaults and prevent invented authority;
  they are not a configured operating production plan. Preserve the existing
  accepted25-gate readiness records separately; zero397earned is not0%of the film.
- BaselineC is unknown.80and261are task-specific historical slots, not a uniform
  whole-project census. The12.5%and7C/8C/7C/(B−C)relations are implemented only as
  explicitly conditional Director394illustrations. No affordability/efficiency
  forecast is established. Do not manufacture a total film envelope to fill this.
- Workflow/admin engineering and lightweight operations are not automatically
  enrolled in397cycle accounting. The current400audit itself uses the operating
  time ledger but does not reserve a397production cycle. A declared total-investment
  scorecard must reconcile these lanes instead of presenting enrolled counts as
  all effort. Lightweight actions need not become full production workflows.
- No prospective completed production unit under397exists. Fewer Director escapes,
  better yield, economic viability and unchanged review quality remain NOT_RUN.
- `context_hygiene current` still says finish397protection, despite the verified
  closure receipts. This stale next-action text should be reconciled during the
  repair; do not blindly rehash all sources or relax legacy307checks.

## Current regression and preservation evidence

Fresh full offline run: **2991passed,1failed,16skipped,37.09s**, command
`.venv/bin/python -m pytest tests --ignore=tests/native -q`, log at
`.runtime/context-hygiene/runs/workflow400-regression/stdout.log`.
The failure is `tests/test_calibration255.py::test_current_authority_excludes_old_pending_claim`:
its exact old literal phrase is absent after399's concise current-authority update.
Inspection confirms accepted253scope and strict replay/release-rights separation
remain in the new action and source. This is a brittle wording assertion, not
current evidence of lost Pashtun authority. It is still a genuine red regression;
399's50selected retrieval tests did not establish whole-suite green. The earlier
2992result was accurate for the frozen397state, not the399tree tested here.
That full run preceded400audit-only documentation persistence;88knowledge/context
controls pass after those reviewed changes. No new full-suite green is claimed.

No production code was changed to make tests pass. No counter was reset, old
artistic failure waived, master changed or source repinned. CANONICAL_VERIFY.json
contains fresh exact state/hash evidence; EVIDENCE.json binds source/code/logs.

## Recommended next package and exit

Close F1–F4 and replace the brittle wording check with explicit authority/meaning
controls, preserving its negative intent. Verify accounting enrollment boundaries,
add the missing rolling-metric/reporting connections, reconcile the stale current
next action, and document what cannot be populated until actual future authority/
observations exist. Test via actual Controller/Bridge mock dispatch, not only
standalone helper functions. Repeat no-loss checks and the full suite once fixes
are stable; retain these newly discovered counterexamples as regression tests.

Then admit one narrowly bounded real production proof under separately approved
allowance, with explicit operational weights/allocations for that scope. Compare
expected/actual review escapes, retained proof and charged effort. This is the
prospective test of our intended benefit, not a new policy-building campaign.
Do not increase source/host context budgets, mint new task allowances or invent
whole-film forecasts to turn this audit green. Production quality and Director AV
remain separate; no proposed horse source is adopted by this audit.

Persistence: reviewed400audit caution is appended to current authority/catalog;
other15source pins remain identical. This is a documentation/status reconciliation,
not a repair, new production allowance or clearing of the failed full regression.

The planning knowledge gate remains `ready_for_review:false` because the observed
framework-failure hypotheses are unresolved. This is intentionally retained; the
core permits labeled failure audits. It does not authorize a production handoff
or clear those findings. No hypothesis was mislabeled resolved to obtain green.

Checkpoint maintenance also lagged: the checkpoint ledger stopped at370while
status reached399.400records the current checkpoint and discloses missing380/390
entries instead of inventing them. This is an application/maintenance gap outside
the new native-controller gates.
