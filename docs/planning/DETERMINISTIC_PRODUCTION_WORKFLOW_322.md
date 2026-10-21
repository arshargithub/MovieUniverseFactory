# Deterministic production workflow proposal

Director exchange322, 2026-10-21. **Proposed architecture, not implementation authorization.** Production remains paused for process work. Preserve audit321 and its rejection; do not generate another scene candidate from this discussion. The Director proposes ordered interpretation, execution and review with a Director-established correction limit. No value of that limit has been adopted.

The recommended change is a small controller that owns stage transitions, persistent state and delivery eligibility. Reasoning remains necessary within each stage. Deterministic orchestration can prevent skipped review, stale evidence and unauthorized extra cycles; it cannot make a model's artistic judgment correct. Audit321 demonstrated method, judgment and admission failures despite relevant instructions being available. It did not establish that hidden host instructions or context compaction caused them.

## Continuity and existing components

This extends, rather than replaces, [production strategy before execution](../decisions/0005-production-strategy-before-execution.md), [shot and beat quality briefs](SHOT_BEAT_QUALITY_BRIEF.md), the [knowledge bridge](../knowledge/pilot/README.md), lifecycle capture and [review control](../knowledge/review_control/README.md). Read [audit321](../knowledge/NIHANG_REARING_REVIEW_FAILURE_321.md) as a mandatory manual source until explicitly indexed and calibrated.

Original source exchanges were reread: role-lens proposal `23441466-1a7e-4985-a0fa-63d46e970b28` and approval `245cd028-d5f4-40f5-872d-1512c522517a` in captured part06; upfront-review correction `239aaa29-fb22-44f7-a8d7-886a9ad8dc5b` and preceding proposal `a253f9d8-af6f-4a6d-91f7-87a06b6e7200` in part05. Preserve expertise roles distinct from agents, artifact authority and reviews agreed in advance. No new organization chart or approval at every internal stage is intended.

The current `review_control.py` checks declarations, bindings, modalities and scope. It explicitly is not a chat interceptor. A valid declaration can still contain a mistaken observation. Its manual audiovisual route cannot excuse visible appearance or pose failures. A future controller must govern actual dispatch and presentation, not merely offer another optional command.

## Route by task type

| Task | Required workflow |
| --- | --- |
| Show an existing image or version | Resolve exact version and acceptance status, verify artifact, present. No production review loop. |
| Expiring S3 link | Resolve artifact and authorized destination/access, transfer only when authorized, verify object/link/expiry. No cinematography checklist. |
| Research assets or tools | Apply creative fit, rights, production path, cost and source-quality checks; return evidence-backed candidates. Research does not authorize procurement or construction. |
| Plan or explain | Inspect evidence and relevant history, propose or record the plan. Do not start construction implicitly. |
| Create or repair production work | Use the full workflow below, scaled to risk and scope. |

Routing itself may require reasoning. Once selected, the route is recorded; changing it requires a reason and authority check. Ambiguous scope must not silently become a production or external-write route.

## Stages and contracts

`ROUTE → BRIEF → EXECUTE → FREEZE → REVIEW → READY_FOR_DIRECTOR`

Review can instead return `REPAIR`, `EVIDENCE_NEEDED`, or `REPLAN_REQUIRED`. Material choices and authority boundaries route to `NEEDS_DIRECTOR_DECISION`; environmental/capability failures can route to `BLOCKED`. Safety, spending and user interruptions apply at every stage.

### Brief

Produce one versioned work package containing:

- Director intent, intended audience experience, protected choices and deliverable scope.
- Applicable mandatory rules, retrieved lessons, fresh source bindings and a manual missing-domain/interface check. Retrieval alone does not establish completeness.
- Explicit preferences separately from inferred preferences, with provenance and uncertainty. Rejected candidates never become acceptance targets through repetition.
- Relevant expertise lenses and their concrete requirements. One agent may apply several lenses; do not create an agent for every discipline.
- Per-beat observable acceptance conditions, likely unmentioned failures, visibility priorities, representative early proofs and relevant negative controls.
- Strategy, interfaces, resources, permitted tools/actions, evidence capabilities, review gates and correction limit.

For the Nihang this includes whole horse/rider balance and landing, purposeful crowd movement with continued attention, believable face/clothes/tack, same-film appearance and contact/continuity. “Head bone moves” is supporting evidence, not the requirement. “The rider visibly braces and recovers with the horse” describes the intended result.

Routine implementation uncertainty stays agent-owned. Material identity/style/story changes, scope changes or new spending/rights/tool authority require a Director choice. No unnecessary approval gate is inserted between brief and execution when authority is already sufficient.

### Execute and freeze

The builder receives the pinned work package and relevant asset state, not the whole conversation. It performs internal diagnostics and representative proofs, then submits an immutable candidate version with evidence and change provenance. It cannot declare its own candidate accepted, edit the acceptance contract or present production media directly.

Freeze binds candidate files, inputs, cameras/framing and applicable brief versions. Subsequent changes invalidate affected evidence and reviews. Preserve useful technical successes independently of artistic failure. Process crashes and retries must not duplicate paid calls or renders; resumable jobs need identity and ownership.

### Review

Use a separate review invocation/context where practicable, initially serial and read-only on production assets. Supply the same approved intent/references, exact candidate, known defects and required evidence, but withhold the builder's persuasive success narrative until the reviewer has recorded its observations. Then inspect implementation details as needed for diagnosis. A fresh context reduces construction bias; it is not an independent human expert or a guarantee against correlated errors.

Review first asks whether the overall result belongs in this film and communicates the intended action. Then apply specialist checks and deliberately look for adjacent failures. Record the strongest counterexample, not just evidence supporting success. Compare against accepted references and production quality, not a rejected predecessor.

Keep appearance, pose/contact, temporal performance, audio and technical integrity as separate verdicts. Any blocking failure vetoes admission; test counts and hash checks cannot compensate for an artistic failure. Missing evidence is `NOT_RUN`, not a generous pass. Evidence collection has a bounded retry policy; it cannot become an uncounted construction loop.

Current direct motion/audio capabilities remain false. Timed frames and trajectories help identify faults but cannot certify full-speed audiovisual feel. Under Director313, a candidate may reach the specifically agreed Director audiovisual review only after agent-owned visible failures are closed. This is `READY_FOR_DIRECTOR_AV`, not a full internal audiovisual PASS or release approval. Do not silently add Gemini or another reviewer/provider.

### Correct and stop

Define `n` as the maximum completed review-to-repair cycles after the initial candidate: initial attempt plus up to n corrections. **Recommendation for a first pilot: n = 2; Director choice pending.** There is no arbitrary elapsed-time quality cutoff.

Persist the count against the same deliverable across turns, context resets, file versions and replans. Renaming a pass does not reset it. Internal exploratory edits are not individual cycles, but repeated failed hypotheses trigger early method reassessment; do not hide endless variants inside execution. Technical transient retries have separate bounded accounting and all resource/spend limits remain binding.

On a failed review with cycles remaining, route findings directly to execution and then review without a routine Director handoff. On exhaustion, preserve failure and produce a method/feasibility decision packet: what failed, what was learned, viable alternatives, consequences and one recommendation. Never lower the bar, silently increase n, or present the failing candidate as complete. A material new choice can require interruption before the cap. A corrected brief does not erase failures or reset the cap.

An internal pass permits only the next agreed review/delivery stage. It is not Director acceptance, publication authority or automatic full-production completion. Lightweight informational tasks may finish without a creative approval stage.

## Serial execution and visible progress

Start with one active stage and one heavy local job. Planning, construction and review separation does not require parallel agents. In particular, a review context can run after the builder has stopped and released Blender. Add parallel work only for independent tasks with measured benefit, bounded resources and explicit delegation authority.

Mac slowdowns cannot be attributed to subagents alone from current evidence. Measure process memory, memory pressure/swap, concurrent Blender/encoder jobs and durations. Enforce a heavy-job lease, avoid duplicate scene loads, and serialize memory-intensive jobs. A CPU/GPU job limit matters separately from agent concurrency.

The orchestrator owns one visible progress stream: task and stage, correction cycle, current proof, concise findings, running job/progress, next transition and any decision needed. Example: “Review 1 rejected the foreleg silhouette and saddle drape; correction 1 of 2 is underway; scene integration remains blocked.” Stream useful work summaries, not private chain-of-thought. Persist events so restart does not erase progress. Do not promise that the current app exposes every subagent event automatically.

Stage packets contain a small mandatory core, applicable source excerpts, current intent, relevant evidence and open decisions; historical detail stays addressable on demand. The reviewer still sees the original creative authority. Omitted required context blocks dispatch rather than being silently truncated. Measure context size and actual usage when available; no percentage efficiency claim is justified yet.

## Small implementation path

1. **Offline controller and replay tests.** Reuse existing knowledge, review and lifecycle modules behind a persisted state machine, versioned brief/candidate/review schemas, cycle accounting and an event log. Test dispatch/delivery policy with fixtures; do not render or call a provider. Distinguish mocked control-flow proof from real reviewer accuracy.
2. **Calibrated staged review.** Replay the rejected320 evidence and relevant accepted Pashtun evidence under matched task scope, then test additional cases not used to tune the rules. Source-reference differences and existing technical failures remain explicit. Positive controls prevent an always-reject gate; audit321 is now a regression case, not held-out validation. Existing Director verdicts are the labels; additional expertise is not assumed.
3. **One production integration.** After the workflow is approved and the offline pilot passes, route only the isolated Nihang/rearing/crowd package through it. Bind admission to the actual delivery path, preserve the one-second handles, and keep other production work excluded. Compare escaped defects and unnecessary handoffs, not only successful schema checks.

The enforcement boundary must be explicit. A local CLI guard called voluntarily from this chat is an interim discipline, not deterministic orchestration. To own stage transitions across model turns, an outer controller must launch bounded stage calls, receive their results and decide the next call. Builder/reviewer contexts need scoped tools, with controller state and delivery outside their write authority. Repository conventions alone do not provide that isolation. Host sandbox and approval rules remain superior constraints.

The Codex SDK supports programmatic task start/resume/streaming; app-server exposes threads, turns, events and approval handling. These offer future adapter choices without replacing the whole Codex harness. Authentication, account terms, resource use and cost must be qualified before enabling an automated model driver; this proposal authorizes no new calls or subscription assumption. Keep workflow contracts provider-independent for the eventual Factory application. [Official integration overview](https://developers.openai.com/blog/codex-as-a-platform).

Multi-agent parallelism is not the default for this ordered, shared-state chain. Official guidance also distinguishes independent workstreams from dependent steps and shared-resource contention. [Official multi-agent guidance](https://developers.openai.com/api/docs/guides/responses-multi-agent).

## Required pilot checks and measures

- Cannot dispatch before a complete, current brief; cannot present an unreviewed/stale candidate.
- Failed appearance cannot use pending Director audio/motion judgment as a bypass.
- Missing modality evidence cannot become PASS; permitted human-review scope is explicit.
- Correction limit survives restart/replan; no fourth candidate when initial plus two corrections is the approved maximum.
- User direction changes invalidate affected work; protected approvals and unrelated evidence survive.
- Builder cannot rewrite review policy; reviewer cannot modify candidate; only controller can authorize presentation. Test actual access boundaries when connected to a model driver.
- One heavy-job lease prevents concurrent duplicate rendering; recovery does not repeat external side effects.
- Simple retrieval/research tasks do not acquire the full production ceremony.

Track stage violations, blocked attempted bypasses, false admissions, false rejections, escaped/repeated visible defects, Director-owned versus avoidable handoffs, active work/render/wait time and local resource pressure. Exclude verified Director idle, retain continuing jobs and union overlapping durations. Small-sample results are directional, not statistical proof of universal artistic judgment.

## Recommended next work package

Build and test the offline workflow pilot, then demonstrate its state/event trace using the rejected Nihang candidate and task-routing cases. The Director receives a concise replay report showing what was blocked, why, where correction would route, and how the iteration ceiling behaves. Included: existing-module integration, persistent states, fixture tests and calibrated review protocol. Excluded: scene repair/render, full Factory UI, new providers, paid calls, cloud execution and parallel agents. Exit requires the listed control-flow checks passing with honest remaining semantic-review limits. The only proposed policy selection needed now is the correction ceiling; n = 2 is recommended, not adopted.
