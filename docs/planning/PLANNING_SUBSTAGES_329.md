# Proposed serial planning substages

Status: response to Director329, proposed, not implemented or independently
qualified. Existing328 content gates remain active. No new inference allowance,
model dispatch, render or construction is authorized by this proposal.

## Objective

Reduce the chance that retrieval, expert derivation, creative alignment, technical
strategy and self-review compete within one large planning response. Determinism
enforces sequencing, required inputs/outputs, freshness and admission; reasoning
still determines applicability, taste, causality and method quality.

Keep three outer phases: PLAN, EXECUTE, REVIEW. For substantial production work,
PLAN becomes four serial steps with persisted artifacts and explicit exit gates:

1. **Ground the task.** Assemble original direction and beat intent; relevant
   historical learnings; movie identity/style/theme; Director preferences; source
   references and roles; accepted/rejected controls; constraints/authority.
   Separate these sections rather than flatten into prose. Each relevant item
   names its source, status, scope and expected implication. Missing coverage or
   unresolved authority blocks; unknown preferences remain hypotheses, not fact.
2. **Derive the creative/technical requirements.** Select and apply relevant
   expert perspectives per beat, grounded in step1. Predict audience understanding,
   feeling, dramatic carriers, believability hazards and interdependencies. Output
   derived requirements and tradeoffs, not construction code. Every contextual
   obligation is applied or explicitly out of scope with rationale.
3. **Design the execution strategy.** Resolve cross-discipline conflicts; choose
   representation/methods, interfaces, dependency order, reuse, earliest integrated
   proof, resource envelope, failure/replan tests and final evidence. Output one
   executable work package, not several independent specialists' wish lists.
4. **Challenge and admit.** A fresh review context compares original direction,
   authoritative grounding, derived requirements and proposed strategy. Seek
   missing expert lenses, ignored learnings, same-film mismatch, weak methods,
   expensive invisible work and unsupported assumptions. Outcome: admit, route a
   specific defect to1/2/3, or surface a material Director decision. Do not treat
   source hashes or complete fields as semantic proof.

The controller checks each output before dispatching the next. Cache valid
artifacts, bind source hashes and invalidate only affected downstream products.
Preserve package identity, shared correction/call budgets and stop rules through
loops. Do not give every substep a new retry allowance. No parallel heavy jobs or
one agent per lens. Use concise progress events, not hidden long subagent work.

Not every step needs a separate LLM call: retrieval/assembly/schema checks can
reuse deterministic tools; expert derivation, synthesis and fresh challenge are
distinct reasoning contexts for substantial work. Actual routing and call limits
must be scoped before live use. Simple link/display/lookups retain their lighter
routes; small bounded corrections inherit still-valid grounding and requirements.

Final output review must revisit original intent and challenge planning omissions,
not merely trust a planning admission. Prospective evaluation freezes the plan
before execution and records later missing requirements, method/evidence/judgment
escapes, useful creative choices, avoidable handoffs and work/render time.

Recommended next deliverable: implement and offline-test these substages in the
existing serial controller, including skipped-stage, stale-source, missing-context,
misrouted-repair and budget-reset controls; then freeze one real Nihang work package
for prospective application. No scene polish or production-quality claim belongs
in that implementation handoff.
