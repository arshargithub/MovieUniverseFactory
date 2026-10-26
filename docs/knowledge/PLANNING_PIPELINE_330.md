# Serial planning pipeline — adopted at exchange330

**378 extension:** read [purpose-qualified reference readiness](REFERENCE_READINESS_378.md).
New native Grounding requires explicit reference needs/adequacy decisions;
Derivation, Strategy, Challenge, execution, review and retros retain the same
aspect contract. A reference gap returns to Grounding. This does not resume
paused work, reset limits or turn structural checks into artistic judgment.

Director330 authorizes critique, local implementation and testing of329. This
extends the existing controller, not a new orchestration service. The requested
software scope is complete after the linked qualification; it is not a claim of
better animation or autonomous studio-quality production.

**350 operational extension:** read
[Retrospective workflow and operating procedure](RETROSPECTIVE_WORKFLOW_350.md)
before continuing covered production tasks. Registered outcome events now enforce
scoped retrospective/revalidation obligations before dependent execution and
delivery. Admission to test a response is distinct from demonstrated effectiveness;
existing authority and correction limits remain binding. Legacy tasks require
reviewed migration;350 did not migrate or resume the exhausted Nihang tasks.

## Critique and design decisions

The idea is sound **if stages constrain subsequent work**. Merely splitting one
large prompt into four summaries would add latency, opportunities to lose intent
and false confidence. The321 audit is decisive: many correct requirements were
already present; an unsuitable pose strategy and generous judgment still passed.

Therefore the implemented boundary separates **procedural completeness** from
**quality of reasoning** and **quality of the result**. It enforces the first,
makes the second inspectable, and requires separate evidence for the third.
It does not make an LLM deterministic, exhaustive or unbiased.

| Stage | Specific responsibility | Persisted output / exit condition |
|---|---|---|
| Grounding | Reconcile original direction, applicable lessons, film language, Director preferences, reference roles, accepted/rejected controls and constraints | Source-bound applicability and implications; fresh learning obligations; explicit gap/conflict reconciliation. Required sources cannot be dismissed. |
| Derivation | Apply expert lenses to each beat, anticipating what audiences will understand, feel and find unbelievable | Concrete requirements linked in both directions to beats/lenses, context and lessons. No orphan requirements or disappearing applicable preferences. |
| Strategy | Choose the integrated representation and method, resolve interfaces and order the work | Frozen requirements/authority; chosen method versus alternatives; observed-versus-hypothesized capability; earliest discriminating proof; ordered proof/build dependencies; resource scope and replan triggers. |
| Challenge | Revisit original direction and evidence in a fresh reviewer context | Nine explicit comparisons: grounding, expert coverage, film alignment, preferences, reference roles, method, interfaces, efficient quality and authority. Admit an attempt, route repair to1/2/3, or identify a material Director decision. |

The outer workflow remains **PLAN → EXECUTE → REVIEW**. Final output review still
has original-intent vetoes and can identify planning omissions. It does not merely
check whether the builder followed a flawed plan. Appearance, motion, technical
integrity and Director acceptance remain separate.

The fixed lens inventory is a minimum coverage scaffold, not a claim to enumerate
all studio expertise. Cultural authenticity, garment construction, animal anatomy,
stunt balance, etc. must be applied concretely inside relevant derivations. Do not
create one agent/job per lens. A list of specialties with no requirement/proof is
not their application.

## What is actually enforced

- Separate stage tickets, exact input digests and event snapshots prevent skipping
  stages or admitting a response against different inputs. A completed stage is
  cached; a correction invalidates its downstream artifacts, candidate and receipt.
- Context keeps original statements, status, scope and references beside the
  interpretations. Actual verified text excerpts are supplied, deduplicated, with
  path/hash/line range. Binary reference media stays separately bound; a path or
  description is not a claim that the model has inspected it.
- Fresh retrieved obligations are supplied directly by the controller. Mandatory
  coverage cannot be replaced with a model's search summary. Manual source and
  relationship reconciliation remains necessary because the corpus is incomplete.
- Source or engine drift blocks dispatch. Trusted `reground` can reconcile new
  sources/bytes without changing original creative intent or promoting source
  status; it restarts grounding and consumes the existing correction allowance.
  Explicit `revise` handles Director direction changes and also restarts planning.
  Neither repins unknown material automatically.
- The challenge uses the reviewer route and does not receive the strategist's
  self-admission narrative. It still sees the method rationale it must critique.
  Fresh context is procedural separation, not independent expertise.
- `FAIL` or `NOT_RUN` challenge facets block admission. Repairs return to the
  earliest affected stage. Output-review planning omissions return to derivation;
  a source-level issue can be explicitly routed to grounding. Routine methods do
  not require a Director handoff. Material decisions need options, consequences
  and a recommendation. The validity of the claimed material decision remains a
  reasoning responsibility, not something a category name can prove.
- Planning repairs and production corrections share the package's persisted
  correction count. Task renaming cannot reuse the same deliverable identity to
  reset it. Exhaustion stops at `REPLAN_REQUIRED`; it is not a pass. Limits remain
  Director-set, not arbitrary elapsed-time deadlines.
- The serial runner retains at-most-once dispatch, recovery and one heavy-job
  lease. Progress events expose substage and correction count. No parallel workers
  are required; this implementation spawned none.
- Lightweight link/display/research routes remain lightweight. A bounded method
  correction can reuse current grounding/derivation and return to strategy.

## Context and resource tradeoffs

Each selected text excerpt is limited to12,000 UTF-8 bytes; deduplicated source
text totals at most48,000 bytes. Overflow requires explicit, reviewed selection,
not silent truncation. The runner's120,000-character request cap remains active.
These are packet bounds, **not measured LLM token consumption or quality gains**.

Four planning dispatches plus builder and output reviewer make six calls if each
stage uses an LLM. Grounding may instead be assembled/reconciled locally. Source
assembly and validation already use deterministic code; meaning and applicability
still require judgment. Extra stages cost latency and tokens, so the production
benefit must be measured in avoided rework, not assumed.

The original live qualification ceiling remains four calls, and325's allowance
remains exhausted. Offline simulation has a distinct persisted mode, cannot be
changed into live mode, and the live protocol refuses simulation requests. Tests
can exercise six or more mock calls without enlarging a live allowance. A future
live six-stage qualification needs its own explicitly scoped authority; none was
performed here. Existing326 planner/executor/reviewer routing applies, with the
challenge on the reviewer route. No main-chat model change is inferred.

## Evidence, limits and next measurement

- [Strategy and critique](../../results/workflow330/STRATEGY.md) preceded code.
- [Focused qualification](../../results/workflow330/validation/report.json) records
  actual test results, engine bindings and the scoped knowledge gate.
- [Four historical replays](../../results/workflow330/replay-qualified/report.json)
  pass through the actual controller and reject16 stage-specific mutations.
  These are analyst-authored with known later history, **not blind prediction or
  an independent model trial**. The planning task packet is intentionally scoped
  to workflow evaluation, not permission to dispatch production animation.
- A well-formed “rigid horse / slow landing” method still passes a rubber-stamp
  challenge. This deliberate semantic false negative stays in the tests. We have
  not measured fewer Director inputs, better footage or percentage efficiency.
- The runtime remains a tool-free frozen-evidence pathway, not a qualified Blender
  authoring worker. Strategy dependency order is enforced in the plan, not an
  automatic claim that every external tool obeys it. Reviewed native handlers and
  actual proof evidence remain separate execution requirements.

The next production-facing proof is the frozen
[Nihang package](../../results/workflow330/NIHANG_PROSPECTIVE_BRIEF.md). Measure
whether its *already recorded* hypotheses survive actual pose/look construction.
Record each escaped defect as missing requirement, retrieval, method, evidence,
judgment or admission failure. Count useful creative decisions separately from
avoidable technical corrections, include active work and render intervals, and
exclude verified Director idle. Compare with250 using declared scope and capture
gaps. One successful slice is promising evidence, not a general efficiency rate.

## Operational adoption

Before substantial production work read this record plus the applicable328
expert-plan requirements. Use the staged controller for the next scoped package;
do not present schema admission as a visual pass. Existing legacy briefs/databases
without the new grounded context fail closed and require explicit migration with
original authority, history and remaining limits preserved. No automatic migration
or reactivation of an exhausted runtime campaign is implemented.

Planning completion is not a routine Director checkpoint. For the next authorized
construction goal, proceed through internal proof and corrections, stopping only
at the agreed integrated review or a real Director-owned choice/blocker.
