# Movie Factory — experiment operating handoff

Prepared 2026-09-11. Proposed implementation specification for Codex in `/Users/adisharma/projects/MovieUniverseFactory`.

## Outcome and scope

Make experiment duration, engineering consumption, and learning transfer observable without creating a second large engineering project. Apply prospectively to the next experiment. Keep 3D-05 closed YELLOW: technical and minimum visual quality passed; the frozen timing-preference criterion did not. Do not rerun it or invent historical usage totals.

Extend the existing campaign records, `docs/engineering-intelligence/events.json`, and motion-design template. First deliver a small local event ledger, usage-import adapter, and generated Markdown/JSON summary. No dashboard, service, billing integration, or replacement harness is needed. No paid engineering API calls are introduced. Proposed defaults below are process policies, not retrospectively imposed qualification gates.

## 1. Experiment lifecycle and elapsed time

Start the experiment when its authorized design/implementation work begins, not when the scored Blender run launches. Close only after its disposition and required compact handoff are recorded. A closed outcome can be GREEN, YELLOW, RED, or abandoned with findings. Qualification colour and open/closed lifecycle are separate fields. Later reopened work is a new linked episode, preserving the earlier closure.

Append events with event ID, experiment/episode ID, UTC timestamp, event type, phase, task/turn/run IDs when available, reason, and evidence reference. Record a monotonic duration for live local jobs in addition to UTC boundaries. Make writes idempotent and recoverable. Corrections append superseding events; never silently rewrite history.

Minimum events: start, work_started, phase_changed, wait_started, wait_ended, job_started, job_completed, model_setting_observed, usage_observed, close, reopen. Wait reasons distinguish Director response, next prompt, explicit user pause, provider limit, machine failure, and other infrastructure waits.

Report these separate measures:

- Calendar elapsed: close minus start.
- Excluded human/input wait: union of intervals genuinely blocked on Director input, the next prompt, or an explicit user pause, during which no experiment work continues.
- Net experiment elapsed: calendar elapsed minus that excluded union. Include engineering, tests, rendering, failed attempts, debugging, packaging, and infrastructure delays. Do not remove slow machine processing to make the experiment look efficient.
- Native-job wall time: sum per job AND union of overlapping job intervals. The sum is process-seconds, not elapsed critical-path time or CPU core-seconds.
- Assistant-active/turn time, human-review time, and phase totals, only where measurable. Human review is reported separately even though it falls inside excluded input waiting for the headline metric.

If a question is outstanding while useful background work continues, that overlapping interval remains net work time. Use one experiment-level state with job/activity reconciliation rather than subtracting all task waits independently. Record when an assistant yields and when work resumes so overnight inter-prompt gaps do not count. A crashed process or unexplained gap becomes UNKNOWN, not inferred human wait; report coverage and uncertainty. Do not claim exact net time when lifecycle capture is incomplete.

Example acceptance fixture: 120 minutes calendar, 30 minutes of requested Director wait including 10 minutes of continuing render work, and 15 minutes of later idle prompt wait gives 35 excluded minutes and 85 net minutes. Overlapping jobs must not inflate the net result.

## 2. Engineering usage and cost

Keep four quantities distinct:

1. Factory experiment API usage and billed cost from the existing provider ledger.
2. Codex engineering usage attributable to this experiment, including diagnosis, implementation, review, handoffs and packaging across all linked tasks.
3. Account-wide allowance consumption, a separate capacity indicator.
4. Human time and local computation, with optional user-supplied costing assumptions.

The desktop usage-limit tool exposes account-wide percentages; those are not token counts or per-experiment charges. The official Codex app-server documentation describes `thread/tokenUsage/updated`, providing a candidate source of thread usage. First perform a short read-only capability check of the installed version and available task-local records. Do not assume the current desktop connection exposes that event, spawn a replacement server expecting historical visibility, or scrape unrelated conversation content. Prefer supported structured metadata; make local-log parsing versioned, optional, and explicitly described as such.

For each usage record retain source, timestamp, experiment/task/turn IDs, actual model/effort if available, reported token categories and their definitions, and whether values are cumulative or incremental. Distinguish observed runtime settings from user-reported settings. Do not add cumulative snapshots together. Handle retries, resumed tasks, model changes, resets, duplicate events and forked-history counters without double counting. Keep reasoning and cached tokens as subsets where the source schema defines them that way. Unknown fields are null, never zero.

Attribution coverage must be visible. If only a subset of engineering tasks is captured, label the sum partial. Time-window attribution in a reused task must exclude prior work. Never count inherited fork history as new generation. Do not infer tokens from response length, account percentages, or elapsed time.

If exact tokens cannot be obtained cheaply, ship the timer and report engineering tokens UNKNOWN with the reason. Continue recording turn count, tool-call count, candidate variants, failed attempts, repeated test suites, and net elapsed time; these are useful operational proxies, not token estimates. Keep telemetry discovery bounded; do not delay the next experiment to build invasive collection infrastructure.

Dollar reporting:

- Actual incremental API/credit purchases: report only supported charges.
- ChatGPT subscription: report as shared fixed overhead, with no fabricated per-token bill.
- Optional subscription allocation: use an explicit allocation rule across measured work, labelled accounting allocation rather than marginal cost.
- Optional API-equivalent estimate: only if model and sufficient token categories are available; use a dated official pricebook and cache/context rules. Label it a hypothetical comparable API estimate, never the subscription charge or cost of a proven equivalent production workflow.
- Quota deltas: keep their window/reset identifiers, rounding and concurrent-use caveats. A reset or other task activity makes naive before/after subtraction unsuitable for attribution.

Report consumption per CLOSED experiment alongside consumption per technically successful output and per Director-accepted output. A YELLOW experiment must still appear in costs; failed work is not free. Keep development investment separate from repeatable runtime generation cost.

## 3. Engineering model policy

Proposed next-run policy: retain Astra, use Medium for specified implementation, routine validation orchestration, report assembly and packaging. Use High for the initial unfamiliar motion/constraint design, unresolved coordinate/rig/collision diagnosis, or a material disagreement between machine measurements and visual evidence. Return to Medium after a demonstrated cause and concrete repair contract exist.

Treat this as a hypothesis to evaluate, not a promise of token savings or equivalent quality. Avoid repeated model switching within trivial steps. Record each work block's model/effort, input evidence, objective, result, retries and observed usage. Do not infer settings from the model's self-description. If app settings cannot be changed through an available supported interface, record that and ask for a user setting change at a natural handoff; never claim it happened.

Compare net time and attributable usage to an acceptable outcome, including rework. A short High diagnosis can be cheaper overall than repeated Medium attempts. Conversely, High is not needed simply to wait for Blender. No costly duplicate High/Medium benchmark campaign is required initially; collect observational data and label its confounding factors.

## 4. Fixture progression and next experiment

Keep the current low-poly rig as the known regression fixture. More polygons do not imply a more capable or better-deforming rig. Its bespoke repairs and elbow limitations make a better production-oriented fixture desirable, but changing rig, prop, reference method and action complexity together would obscure the source of failure.

Recommended progression:

- 3D-06A: one short reference-timed upper-body gesture on the known rig, stationary root, no prop. Select a comfortable range after a quick pose screen; avoid pushing its known elbow limitation. Freeze three to five pose/time landmarks and one timing revision. State whether landmark annotation is manual or automatic. Test reference fidelity, cue timing, no quality regression and reproducibility; do not demand a subjective preference for an arbitrary timing change.
- Fixture qualification, before richer choreography: admit one better-deforming humanoid separately. Require documented neutral/rest pose, usable bone axes and IK/FK controls, independent usable fingers if needed, stable skinning at elbow/shoulder/wrist extremes, consistent units, rights/provenance and reproducible import/reopen. Screen a handful of known poses and one known short gesture before using it in a scored reference-motion campaign. Record acquisition and adaptation effort.
- Then extend reference motion to that fixture and only afterward add the previously qualified sword or a short combat segment. Do not simultaneously introduce cloth, hair, facial performance, locomotion and a new prop.

The existing rig is a control, not an obligation to spend more hours overcoming its limitations. If even the small gesture fails fixture screening, pause that run and qualify the replacement first. No 3D-05 repair is implied.

## 5. Mandatory learning transfer

At closure create a compact experiment card: goal, disposition, demonstrated capability, failed/unproven claims, material causes, assets/source bindings, measured effort, reusable tests/tools, limitations and recommended next question. Preserve failures and distinguish observations from hypotheses.

Before the next freeze, add a short learning-delta table to its spec. Each row contains prior evidence, an explicit next-run change, its verification, and one of ADOPT / DEFER / NOT_APPLICABLE with rationale. Keep it to the few relevant lessons; do not repeatedly load entire prior histories.

Seed rows from 3D-05:

| Finding | Required next-run change | Verification |
|---|---|---|
| Four-frame timing change was acceptable but not preferred | Define a reference cue and timing tolerance, with a non-regression quality gate | Correct timing passes even if preference is tied |
| Fixture geometry and collision assumptions changed late | Check rig range and required geometry representations before tuning | A short fixture suitability record precedes candidate generation |
| Isolated-joint tuning looked unnatural | Complete the motion brief and pose/reference plan first | Full inexpensive preview before scored freeze |
| Full suites were duplicated | Map tests to changed dependencies; schedule one full qualification | Reused evidence has source/config/asset dependency hashes and explicit eligibility |
| Native work, orchestration and archival costs were mixed | Capture phases and forecast disk/output growth | Closing summary separates these costs and unknowns |
| Machine gates missed visual inadequacy | Include whole-motion review and discriminative scene controls | Expected control failure is absent from positive case |

Update the central engineering-intelligence record with evidence links, not unqualified model rankings. A fresh next-experiment task should receive a small briefing containing the accepted fixture, scope, open risks, learning-delta table, commands and stop conditions. Link large historical evidence rather than copying it all into the prompt.

## 6. Execution limits and minimal delivery

Implementation order: (1) small lifecycle ledger and reporting, (2) bounded usage-source probe with working adapter or explicit UNKNOWN fallback, (3) learning-card/delta templates, (4) 3D-06A spec. Do not start animation implementation as part of this bookkeeping delivery unless separately instructed.

Budget each task before starting, including telemetry setup. Proposed defaults: 20 net minutes before a diagnostic reassessment, at most three variants per hypothesis, and a 60-net-minute overall checkpoint. These trigger an evidence-based scope/plan review, not silent threshold relaxation or endless retries. Native work can legitimately exceed the estimate if forecast and justified before dispatch. A user-defined hard budget takes precedence.

Record setup cost separately; do not create an elaborate dashboard to measure an efficiency problem. Use targeted failing-frame probes, then one complete low-cost preview, then the frozen full suite. Reuse prior controls only when the spec explicitly permits it and all relevant dependencies match. Unchanged full suites need not be rerun for report edits. Preserve all existing mandatory gates.

During jobs use blocking/event waits appropriately, concise phase updates, and deterministic scripts for inventories/summaries. Avoid repeated large JSON dumps and unchanged status checks. Preflight disk capacity and expected artifacts. Reuse the verified video/export workflow. Record necessary post-closure archival maintenance separately rather than retroactively changing experiment time.

Definition of done for this handoff implementation:

- Automated ledger tests cover input waits, background work during waits, overlapping jobs, resumed episodes, missing events and clock discontinuities.
- Usage tests cover duplicate/cumulative records, counter resets, missing fields, shared-task boundaries and inherited history. A deliberate unsupported source returns UNKNOWN.
- A simulated short experiment produces a reconciled JSON/Markdown report with no invented token or dollar values.
- The next spec includes its learning-delta table, fixture boundary, process budget and measurable reference goal.
- No prior qualification colours, accepted evidence, API budget policy, or actual model settings are changed implicitly.

## Documentation basis and limits

Official sources checked 2026-09-11:

- Codex app-server usage/lifecycle events: https://learn.chatgpt.com/docs/app-server (documents `thread/tokenUsage/updated`; local capture feasibility still needs verification).
- Codex plan usage: https://learn.chatgpt.com/docs/pricing (allowance consumption depends on model, reasoning, context, tools and caching).
- Astra model and supported effort settings: https://developers.openai.com/api/docs/models/gpt-6-astra . Medium-versus-High routing above is a proposed project policy, not a documented performance guarantee.

Project evidence: `results/3d05/closure-v1/REPORT.md`, `PROCESS_REVIEW.md`, `docs/engineering-intelligence/README.md`, `docs/planning/MOTION_DESIGN_TEMPLATE.md`. The handoff drafts future behavior; it does not claim telemetry has already been implemented or historical token usage recovered.
