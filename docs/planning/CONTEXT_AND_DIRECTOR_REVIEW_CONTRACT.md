# Applying production knowledge and scheduling Director reviews

Exchange210, 2026-10-11. The current records preserve useful knowledge, but application still depends too heavily on the agent finding and following the right prose. A small local context-building and review-contract layer is warranted before scaling production. A large graph platform or vector database is not the immediate requirement.

The Director reaffirms predictable agreed reviews, clear intent/process, shot-specific perceptual priorities and agent-owned internal correction. The mechanism below is a proposed implementation slice, not an already running service or an approved set of new production gates. Existing authority, quality and spending boundaries remain in force. Current209 narration/voice selection is still open; this process discussion does not select treatment A.

## Current mechanism and its gaps

Today the entry points are AGENTS.md, the current work package, release state, the production learning index and topic-specific histories. The agent selects applicable lessons, reads their evidence, writes a learning delta, carries the checks into execution and records an internal exit review. Original decisions and accepted native versions remain authoritative within their scopes. This is more durable than chat-only memory, but it is a procedural bridge.

The important gaps are not solved by another long instruction file:

- Relevant knowledge is selected manually. There is no tested guarantee that a less obvious lesson will be retrieved.
- Current rules and superseded history coexist in long documents; recency or semantic similarity alone cannot settle authority.
- No general preflight verifies that a work package includes all required rules, versions and review obligations.
- A filled review form can still encode poor visual judgment. Required evidence and challenge controls are necessary, but cannot guarantee artistic quality.
- We have not measured retrieval misses, unnecessary handoffs, escaped defects or whether acceptance predicts the Director's response.
- The historical742-exchange capture still has one truncated assistant response;588 extracted candidates are not588 approved decisions. A search index would not repair that source or interpretation gap.

Verdict: adequate for a carefully supervised single active production thread, not sufficiently robust for scalable autonomous production or a model-independent Factory takeover.

## One local mechanism with three complementary parts

**Knowledge base:** versioned records of decisions, lessons, references and evidence. **Dependency graph:** explicit relationships between those records and the affected entities, shots, stages and checks. **Search:** ways to find relevant explanatory material. They answer different questions; they are not competing database choices.

For the first bridge implementation, keep reviewed compact JSON/Markdown records authoritative in Git. Build a disposable SQLite index with ordinary tables, relationship rows and FTS5 full-text search. The project Python already supports FTS5. This needs no database server, graph product, embedding service or model installation. SQLite can represent a small graph with typed edge rows; a dedicated graph database becomes justified only by actual query/scale needs.

Add local semantic retrieval when a small evaluation set demonstrates misses from wording differences that tags and full-text search cannot handle economically. If embeddings are used, combine them with exact identifiers, filters and keyword ranking. They suggest candidates; they cannot select canon, promote a rejected result or grant permission. Any new model download, installation or paid embedding route requires its own authorization. A future runtime database can become authoritative only through an explicit validated migration; do not create two competing writable truths.

Each compact record needs: stable ID/type; scope and applicable entities/stages; status (proposed/adopted/superseded/rejected/hypothesis); source and approval evidence; version; applicability conditions/exceptions; required action or check; dependencies; supersedes/conflicts links; evidence pointers and known limits. Preserve observed facts separately from engineering hypotheses and Director preferences. A lesson about189's GPU artifact is not a timeless ban on Metal. Current explicit intent overrides inferred taste within hard boundaries; it does not silently erase unrelated approvals.

Ingestion is not approval. Automatically extracted summaries start as candidates; evidence-backed technical findings and Director-owned creative decisions have different authority. An assistant writing "locked" cannot supply missing Director acceptance. Consolidate repeated failures into a scoped reusable lesson with linked regression examples instead of generating another permanent rule for every pass. Preserve source history and supersession links without loading that entire history into every task.

## From an upcoming action to a bounded context packet

1. **Describe the action.** Resolve production, shot/beat, stage, affected entity/asset IDs, current versions, audience/format, requested change and authority. Unknown high-impact scope requires investigation rather than a guessed default.
2. **Load mandatory constraints deterministically.** Bring in the small governing contract, current creative decisions, protected asset versions, spend/rights boundaries and the agreed review schedule. These must not compete for a top-k semantic slot.
3. **Expand relevant relationships.** A rider-pose change selects neck/head performance, hands/reins, garment support, hair, sword and horse contact dependencies. A camera change selects screen readability, route visibility and newly exposed terrain. Follow versioned `depends_on`, `applies_to`, `requires_check` and `supersedes` relationships; do not traverse the whole universe indiscriminately.
4. **Search for supporting evidence.** Retrieve relevant lesson cards and exact source sections, including informative failed controls. Keep rejected/superseded records visibly labeled as history. Inspect linked images or temporal evidence when text alone cannot establish the visual claim.
5. **Resolve and compile.** Produce a compact packet containing intent, invariants, applicable lesson IDs, concrete checks, evidence and the next authorized transition. Include why each item was selected and unresolved conflicts. Load detailed history on demand. If mandatory context cannot fit, split the task or retrieve in stages; never silently truncate obligations.
6. **Bind to execution.** Save the packet's input versions/hash in the work package. Before expensive jobs, check freshness, authority and prerequisites. At internal exit require actual evidence for each relevant obligation; a prose assurance is not enough. Objective checks can block automatically. Subjective checks remain agent judgments with evidence and explicit uncertainty.
7. **Invalidate selectively.** Rebuild the packet when scope, asset/version, camera, motion, audience/format or a relevant decision changes. Mark affected checks stale, not every accepted artifact. Compare the actual result with the packet before a planned handoff and record which lesson changed an action.

The working loop is: **resolve current task → fetch binding constraints → expand dependencies → retrieve evidence → compile checks → execute/review → record outcome**. Storing and finding a lesson is not the same as applying it. The application record is the link between a lesson, a changed action, an observed result and the decision that follows.

### Concrete example from the riding neck

For a close gallop beat, the audience should read physical effort and alert self-possession. Mandatory identity comes from the accepted character. The motion brief and dependency links bring in chest/neck/head coordination, contact constraints, collarbone readability, hair and shawl adjacency. The known failure is a rigid-looking cervical block despite nonzero bone animation.

The review must therefore show actual relative neck flex and head stabilization through several strides at the intended framing, with readable anatomy and unchanged rein contact—not merely report that neck keys exist. Inspect the neutral reference and temporal passage, and deliberately look for the old block-like motion. A passing numerical transform test cannot override a visible failure. Once that screen result passes, unrelated pores or a hidden shoulder seam are not automatically new production tasks.

## Tests for whether the mechanism is robust

Start with a small curated regression set drawn from real decisions: right versus left sword hip; shawl above harness; accepted native versus older portrait; stiff neck despite nonzero keys; double wrap superseding single wrap; CPU/Metal evidence with version-specific scope; narration quotation versus fictional words; new camera exposing unreviewed terrain; expired rights or approval; restart without duplicate spend. Include deliberate conflicting, stale and missing evidence.

Evaluate required-constraint recall, erroneous promotion of rejected history, version correctness, context size and retrieval effort, plus whether the prescribed action actually occurs. Proposed acceptance: every critical obligation in this curated set must be surfaced or explicitly reported unresolved; zero rejected proposals may become authoritative. This is a finite regression criterion, not a claim of universal recall. Keep some cases out of initial tuning and compare keyword-only with any later semantic route before adopting added complexity.

Rebuild from the source records, test a fresh context/model and confirm that pinned old productions keep their old versions. Inspect the packet's explanation of relevance. Retrieval quality and execution compliance are separate evaluations. A model saying it read a lesson does not prove that it applied it.

## Predictable reviews without removing creative control

The production agreement defines review stages before execution. A render finishing, a commit, an internal test or a method reassessment is not a Director review. Internal cycles may be numerous; external decision points should be few, explicit and useful. No promise of a fixed number of revision rounds can prevent a genuine creative revision or newly discovered scope conflict.

Recommended default for a new sequence, to agree before dispatch:

| Planned review | Director question | What should already be resolved internally |
|---|---|---|
| Creative contract and rough sequence | Does the story, staging, look/performance direction and sound intent deliver the desired experience? | Relevant constraints/references, feasible route, rough full sequence, major risks and alternatives. Existing approvals are reused, not re-asked. |
| Integrated sequence with scratch sound | Does the complete sequence work emotionally and cinematically? | Obvious anatomy/contact/layer defects, causal geography, readable acting, coherent secondary motion and a deliberate internal failure-seeking review. |
| Final picture and sound acceptance | Is this the production result we want to release? | Final-resolution/mix, captions, rights and delivery QC; technical exceptions disclosed. Publication remains separately authorized and may be bundled into this planned review. |

New principal-character identity/look selection can be bundled into the first stage; do not require every sleeve, prop or solver to have its own review. For the current Pashtun sequence much of the first stage already exists: the next decision is narration/voice, then the integrated sound/text preview, then final acceptance. Do not replay every historical asset gate because the process becomes more structured.

These are sequence or batch-level reviews, not three new gates for every shot. Related shots inherit an agreed creative contract, and each scheduled review can resolve a coherent batch. Show the agenda and decisions expected before work starts. Distinguish a planned review stage from revision rounds within it: three stages does not promise exactly three conversations regardless of creative feedback.

Unplanned handoff is justified only by a material creative/identity/intent conflict, a missing authority/budget/rights decision, a genuine blocker after safe investigation, or a consequential production-priority choice. State the consequence, viable options and recommendation. An understood repair within scope stays internal. If unable to meet the quality floor with existing authority, disclose that honestly rather than loop forever or present a known failure as ready.

## What the internal Director proxy must know

Clear direction and process are necessary but insufficient. Each beat also needs an explicit **audience-reading and salience brief**: what viewers should understand, feel and notice; what must remain recognizable; which moments carry the sequence; what would break believability; which details are optional at delivery size; and what near-term reuse requires.

For this entrance, hero priorities are speed/control, composed recognition, both checkpoint and escape route, the forceful turn, steep risky ascent, downward check and determined continuation. Identity, plausible anatomy/contact, wardrobe structure and rights remain quality-floor constraints. This is not permission to hide structural failures behind low salience. Other details can be deferred only with a named visibility/reuse trigger and recorded rationale.

The proxy should make two distinct judgments: a cold audience read of the whole passage, and a targeted failure-seeking inspection of interfaces and known defects. It must seek unlisted problems as well as satisfy the checklist. Technical and perceptual tests answer different questions. Use the actual intended temporal coverage and format; distinguish chronological frame inspection from real-time playback/listening, and state remaining uncertainty. Do not infer emotion or naturalness from controller values.

Calibrate against actual Director feedback: record the predicted concern, actual objection, whether it was a known defect, a newly revealed defect, ambiguous intent or a new preference. Treat unnecessary technical handoffs and known-defect escapes as process failures. Do not treat every rejection as poor Director communication, and do not convert one shot-specific taste into a universal preference. Current explicit instructions win over a learned preference.

Additional requirements are stable authority/version state; early proof of risky interfaces; quality criteria before expensive work; confidence/uncertainty handling; and a handoff policy that cannot be satisfied by merely writing a passing score. Track planned versus unplanned reviews, avoidable handoffs, escaped known defects, rework after creative changes and first-pass acceptance by gate. Fewer reviews alone is not success if failures reach the audience or the Director loses control.

## Minimum implementation recommendation

Build only a thin pilot: compact approved lesson/decision records, a typed relationship table, local full-text index, a context-packet builder and a preflight/exit checker for one real work package. Use the next audio unit and a retained neck/camera case as the first production/regression examples. Do not migrate all742 exchanges, reconcile all588 candidates, build a graph UI, install a vector stack or make a complete Factory app the prerequisite for the trailer.

First measure the pilot's retrieval and application. Add semantic search if the observed recall failures justify it; add a dedicated graph engine only if simple relationship queries become inadequate. After the tested pilot, shorten the always-loaded entry instructions into a stable governing contract and routing map, while preserving detailed history and checking that no binding rule is lost. Do not delete the current rules before the replacement demonstrates coverage.

## Continuity with original decisions

Full source proposals/user replies were read from the local historical capture for these specific topics; this is not a complete historical audit.

| Original decision | Disposition here |
|---|---|
| Typed truth versus derived search: proposal `7bedc522-4e94-4330-b59e-dc89586f07be`, acceptance `9701d930-0073-4eeb-8ff8-e246e2aadb52` | ADOPT. Search cannot establish canon/permissions; typed records plus versioned artifacts remain authoritative. |
| Up-front review agreement: Director `239aaa29-fb22-44f7-a8d7-886a9ad8dc5b` | ADOPT. Proposed three-stage default is an application to agree, not a claim that the old illustrative stages were already selected. |
| Contextual coherence: `5250231d-10ca-4326-922b-7d8d0c348d71`, following acceptance `48f8f3e3-3804-4256-b2e6-6eb1ac2ba79e` | ADOPT. Relevant learning informs judgment; current deliberate intent can override historical preferences within hard boundaries. |
| [Factory memory baseline](FACTORY_APP_AND_MEMORY_BASELINE.md) and [application index](../knowledge/PRODUCTION_LEARNING_APPLICATION_INDEX.md) | ADAPT into a small measurable local pilot; DEFER full platform/vector/graph deployment. No competing source of truth or automatic enforcement is claimed. |

Technical references: [SQLite FTS5](https://www.sqlite.org/fts5.html) supports local full-text indexing/ranking. [OpenAI retrieval documentation](https://developers.openai.com/api/docs/guides/retrieval) illustrates attribute filtering and hybrid text/semantic ranking; it is not a recommendation to upload this private project to a hosted vector store. No external embeddings, new installations or knowledge-service implementation occurred in this assessment.
