# Movie Factory Demonstrator 01 — integrated production charter

Date: 2026-09-12. Status: handoff charter; production has not started.

## 1. Decision and purpose

Replace the sequence of small Blender qualification experiments with one bounded, integrated filmmaking demonstrator. The question is now: **Can our system produce an appealing short sequence, preserve its editable world, and respond economically to meaningful direction?** Passing isolated technical checks is necessary but insufficient.

Build on the existing MovieUniverseFactory repository and closed 3D-01 through 3D-06A evidence. Do not reopen those campaigns, chase their remaining YELLOW ratings, or rebuild their harness. Existing results establish useful components, not production-quality filmmaking. Read the compact reports, current operating instructions, and relevant implementation—not every historical transcript or artifact.

This charter changes the next experiment's scope and allows paid API engineering work for this demonstrator. It does not retroactively change previous campaign permissions or claims.

## 2. Film brief

Produce a **20–30-second, four-shot sequence**, provisionally titled *The Courier*. A realistically proportioned rider gallops along a mountain road toward a distant watchtower, notices a signal, and continues with clear purpose. The sequence must have a readable beginning, development, and ending, not simply four unrelated technical showcases.

Provisional shot functions:

1. Establish the road, destination, and approaching rider.
2. Track the galloping horse and rider; reveal convincing motion, contact, and dust.
3. Show the signal and rider's response through framing, head/body orientation, and editing.
4. Resolve the sequence with the rider continuing toward the destination.

Use one atmospheric treatment: **dust on a dry road**. Snow is an alternative only if chosen before scope freeze; do not combine dust, rain, and snow. Add licensed or original hoofbeats, wind, and appropriate environmental sound. No dialogue or lip synchronization.

Use suitable licensed external assets and authored animation where available. The experiment tests assembly, direction, persistence, and revision—not whether we can invent a production horse rig or learn realistic galloping from scratch. Target credible cinematic realism at the selected shot distances; do not promise photorealism before inspecting assets and reference frames. Do not substitute a toy-like character or conceal a failed motion requirement through framing without explicitly recording a scope change.

Before locking the exact shots, verify asset suitability. A different brief may be proposed if it tests the same integration needs more economically, but changing the rider/horse concept requires Director agreement.

## 3. Required capability coverage

| Capability | Evidence in this demonstrator |
|---|---|
| Brief to coherent sequence | Shot plan, complete rough cut, and final edited sequence communicate the intended action. |
| Realistic asset integration | Rider, horse, tack, road, and scenery have compatible scale, materials, provenance, and usable rigs. |
| Persistent world and identity | The same actors, wardrobe, destination, and world survive shots, revisions, save, and reopen. |
| Coordinated motion | Gallop, forward speed, ground contact, and rider attachment are convincing in playback; no obvious sliding, floating, or gross penetration. |
| Cinematography | Intentional framing and camera movement, spatial continuity, readable subject, and useful shot variety. |
| Environment and light | Foreground/midground/background depth, consistent lighting, and a believable route through the scene. |
| Atmosphere | Dust supports motion without obscuring action; its implementation and limitations are declared. |
| Finishing | Edited timing, synchronized sound, and one viewable film with no missing frames. |
| Direction and revision | Two meaningful requests produce visible, correctly scoped changes without rebuilding the world. |
| Reuse | One additional 3–5-second shot uses the frozen world and existing controls. |
| Recovery | Reopen the project and reproduce one selected shot under recorded conditions. |
| Economics | Separate engineering, API, rendering, waiting, and revision costs; show whether reuse is cheaper. |

Not qualified: arbitrary characters/rigs, autonomous asset creation, facial acting, crowds, combat, physical cloth/fluid accuracy, general-purpose motion synthesis, or feature-film production. Authored cycles and artist-authored assets must be identified as such. A good final film does not establish autonomous generalization.

## 4. Stage gates: one experiment, visible progress

### Stage A — feasibility and production plan

Inventory reusable components. Select candidate assets, verify licenses and redistribution constraints, and test the hardest integration first: a **2–3-second rider/horse motion preview** with ground contact and forward travel. Complete the repository's motion-design planning requirements using these actual assets. Measure representative render time on the available hardware.

Deliver one compact plan: asset manifest, reference/look targets, shot list, motion/contact risks, measured render forecast, active-work forecast, and spend allocation. Establish asset-appropriate tolerances rather than importing thresholds designed for the previous simple rig.

Gate: a viable motion preview and a believable path to the complete film. Do not spend hours repairing an unsuitable horse or rig. At most two candidate integration approaches before presenting a fallback and the evidence. No custom rigging project without a scope decision.

### Stage B — complete rough cut

Make all four shots at inexpensive preview settings, with provisional sound and timing. Prioritize complete playback over polishing one isolated shot. The Director checks story clarity, motion, shot choices, and whether the chosen visual ambition is worth pursuing.

Gate: the whole sequence works well enough to justify finishing. A technically valid but unappealing or unreadable sequence does not pass. Collect one consolidated set of notes, not repeated micro-approvals.

### Stage C — representative look, then finish

Finish a representative frame and short motion segment; extrapolate render time before rendering everything. Use a 720p review cut and target 1080p final output only if the measured compute envelope supports it. Freeze resolution, frame rate (default 24 fps), renderer, sampling, and asset versions before final production.

Apply the approved look across the film. Rerender affected shots, not the entire campaign by default. Director approval of the rough cut and representative look may be combined into one review packet where practical.

### Stage D — direction and reuse challenge

After the baseline is frozen, accept two meaningful revision requests through the declared control surface. Suggested categories: make the ride more urgent through coordinated speed/timing changes, and alter a camera's composition or reveal timing. The Director chooses actual requests after seeing the baseline; do not pre-script the exact answers.

Declare expected downstream effects and protected state before executing. A speed change may legitimately alter stride timing and dust; do not demand identical dependent pixels. Judge instruction compliance separately from subjective preference.

Then create one additional 3–5-second shot from the existing world. No new assets or new implementation code should be needed for a request inside the declared supported scope. If code changes are needed, record the reuse gap honestly and permit at most one bounded repair cycle; do not silently call it successful code-free reuse.

### Stage E — close once

Reopen and reproduce one selected shot, run relevant existing tests plus narrowly necessary new tests, reconcile ledgers, and produce the compact closure packet. Do not repeat five-seed campaigns or build a new export framework unless evidence demonstrates a critical need.

## 5. Acceptance and stopping rules

Report three independent outcomes: **film quality, directability/reuse, and economics**. Technical success must not conceal poor filmmaking; a visually attractive result must not conceal manual reconstruction.

Before finishing, freeze a short Director scorecard: story clarity, motion credibility, visual coherence, cinematography, and sound/editing. Proposed acceptance is at least 4/5 on each dimension, with no major visible motion, continuity, or rendering defect. These are proposed creative thresholds for Director confirmation at Stage A, not objective measurements of realism. Review full playback, not only contact sheets. API image reviews provide frame-based evidence and cannot certify temporal quality alone.

For directability: both requests must visibly satisfy their stated acceptance conditions and preserve unrelated identities/state; the extra shot must meet the declared reuse conditions. Record human interventions and any repository changes separately from runtime operations.

Economics acceptance requires trustworthy accounting and staying within approved ceilings. This first integrated film establishes a baseline; do not invent a GREEN cost ratio from the earlier narrow experiments. Report initial build and marginal revision/extra-shot costs separately.

Use existing operating checkpoints: 20 net minutes on one diagnosis, three attempted variants, or 60 net active minutes overall trigger a concise progress/continue decision, not another unbounded loop. Stage A must present a total-time forecast and proposed active-work and rendering ceilings for approval before full production. Rendering and Director waits are not excuses to hide active engineering time. Stop earlier for a budget reservation failure, unsuitable core assets, unsafe execution, or missing necessary permission.

A YELLOW or failed integrated result can be closed with useful findings. Do not continue merely to make the status GREEN. Noncritical polish and speculative generalization go to the backlog.

## 6. Model routing and conserving subscription usage

**Main Codex task: Astra, Medium thinking.** This is a routing recommendation, not a claim that Medium is always as capable as High. Keep this task focused on orchestration, bounded inspection, applying changes, verification, and concise decisions. Use a fresh task with this charter and compact state rather than repeatedly loading the entire historical conversation.

| Work | Default route |
|---|---|
| Inventory, checksums, tests, rendering, cost arithmetic | Deterministic tools; no model call. |
| Bounded implementation/patch proposal with explicit tests | Paid Sol, Medium; escalate only on a specific demonstrated limitation. |
| Difficult integration design or unresolved diagnosis | Paid Astra, High, in a bounded work package. |
| Shot-plan or visual critique needing strong judgment | Paid Astra, Medium; selected timed frames and concise context. |
| Apply patches, verify outcomes, maintain task state | Main Codex Astra, Medium. |
| Creative acceptance | Director; model critique is advisory. |

The paid work package should do substantive work: provide the relevant code/constraints and request a patch, decision, or diagnostic plan with acceptance tests. Return a compact result and artifact references. Codex should check it, not independently redo the whole analysis. Do not add a second model review to every step. Escalate one unresolved issue at a time; High is not a standing setting for routine work. Record requested and observed model/effort separately when observation is unavailable.

**Billing boundary:** API calls made through the project key use API billing. The signed-in Codex task's own reasoning and orchestration still consume the ChatGPT allowance. Moving reviews alone will not substantially offload engineering. If supervision remains dominant, propose an API-key-authenticated Codex CLI workflow for engineering, but do not change the desktop login or launch an unbounded API agent. It must have compatible spend controls before using this charter's budget. Extra ChatGPT credits and API billing are different mechanisms.

## 7. Paid API authorization and hard controls

The Director approved **$100 USD total for paid model API calls** for this demonstrator, including engineering, planning, reviews, failures, retries, and revisions. This authorizes the bounded workflow described here, not spending during charter preparation. Asset purchases, paid media generation, and cloud rendering each remain **$0 authorized** until separately approved. Existing lawfully usable assets and local rendering may be used.

Suggested initial allocation:

| Purpose | Ceiling |
|---|---:|
| Feasibility and shot planning | $10 |
| Implementation and integration | $40 |
| Visual critique and finishing guidance | $15 |
| Direction and additional-shot challenge | $20 |
| Failure/retry contingency | $15 |
| **Total** | **$100** |

Use the existing persistent budget ledger in `src/movie_factory/budget.py`; extend minimally where required. Its per-run stage caps are not substitutes for campaign-wide category caps. Keep one campaign-wide total across workers and restarts. Do not create new ledgers to bypass an exhausted cap. Allocation transfers require an explicit recorded Director decision; never silently raise the total.

Before the first live call, verify credentials without printing them, confirm model access, freeze a dated pricebook from official provider pricing, and test accounting with one small metered request. That request counts toward the budget. Do not assume ChatGPT Pro includes API credit or guarantees API model access.

Reserve a conservative upper-bound cost atomically **before dispatch**, counting outstanding reservations alongside settled spend. Include input, maximum output/reasoning, images and any tool charges, plus applicable long-context pricing. Do not rely on cache discounts for the upper bound. If a call's cost cannot be bounded, do not dispatch it. Prefer calls bounded at $2 or less; absolute reservation ceiling $5 per request. Maximum two retries per work item, charged to contingency; unknown outcomes retain their reservations until reconciled. Limit the campaign to 60 physical model requests, including retries, unless the Director changes that limit without increasing the dollar ceiling.

Notify at 50% and 80% of the $100 committed exposure; hard-stop before a reservation would exceed 100%. Provider dashboard alerts alone are not the hard limiter. If observed charges exceed a reservation, stop and correct the bounding mechanism before further calls. Reconcile locally calculated charges against provider records when available; clearly label estimates versus reconciled amounts.

No hidden fallback to prolonged subscription-funded problem solving when API access or budget is exhausted: report the blocker and remaining options.

## 8. Minimum useful telemetry

Reuse the existing operating ledger and engineering-intelligence records. Do not make telemetry a new research project.

Track lifecycle events from design start through closure: active work, unattended render/compute, Director wait, between-prompt inactivity, and resume/close. Report gross elapsed time, elapsed time excluding human/between-prompt waits, and active engineering time separately. Do not double-count overlapping worker durations as wall-clock elapsed time. Mark missing intervals as unknown.

For each API request record work-item ID, purpose, requested/returned model, requested effort, provider response ID, prompt/artifact hashes, start/end, reservation, usage, calculated cost, error/retry relationship, and reconciliation status. Keep input, cached-input, output, and reasoning counters without double-counting nested fields. Preserve useful request/response evidence while excluding credentials and unnecessary private material.

Track subscription work separately: observable usage counters or account-window snapshots with timestamps and coverage limitations. Account allowance changes are not experiment-specific token meters; do not convert an allowance percentage into invented token counts or dollars. Missing subscription token data stays unknown. Any API-equivalent estimate must be explicitly hypothetical, not billed expense.

At each milestone show only: deliverable, net active time, rendering time, paid spend plus reservations, top blocker, and next bounded action. At closure distinguish one-time engineering from per-film and marginal revision costs; report cost/time per finished second as a descriptive baseline, not a universal production forecast.

## 9. Safety, artifacts, and closure

API-generated code is a proposal for reviewed, tested repository changes—not permission to execute arbitrary generated Blender Python. Preserve the existing validated operation boundary and credential-free Blender worker. No automatic purchases, remote pushes, public uploads, or deletion of previous evidence. Preserve failures and local user changes.

Deliver one authoritative artifact set: final film, preview/revision comparisons, additional shot, editable Blender project(s), asset/license manifest with redistribution restrictions, source binding, selected restore evidence, budget/time ledger, and one short closure report. Use references to large existing assets where licensing permits local reproduction but forbids redistribution. Do not duplicate multi-hundred-megabyte exports for each report edit.

The closure report answers: Does the film work? Which capabilities are genuinely demonstrated? What remains manual? Did direction and reuse work? Where did time and money go? What single next investment would most improve quality or throughput?

Choose the next experiment from the dominant observed bottleneck—not the next item in a prewritten list. Examples: animation/retargeting if motion limits the film; lighting/assets if appearance does; planning/control interfaces if revisions require code; shot assembly if continuity fails. If this demonstrator succeeds, the next step should be a second brief using the same system, measuring transfer and lower marginal effort rather than merely adding more effects.

## 10. Starting instruction for Codex

> Execute Movie Factory Demonstrator 01 using this charter. Start with Stage A only: inspect relevant existing capabilities, validate candidate assets and the hardest motion integration, and present the production forecast and scope-freeze packet. Use Astra Medium for the supervising task and the bounded paid API routes specified here. The total paid model API ceiling is $100; all retries count. Asset purchases, paid media generation, and cloud rendering require separate approval. Reuse existing controls and ledgers, preserve closed campaigns, and do not turn the handoff into a harness rewrite. Show the integrated movie as early as possible. Pause at the Stage A gate for agreement on the measured time/render envelope before full production.

### Model and billing references

Model availability, prices, and supported effort values must be verified when execution starts. Recommendation above is a workload judgment, not a benchmark result on this project.

- [Astra API model documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
- [Sol API model documentation](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- [Codex pricing and API-key billing](https://learn.chatgpt.com/docs/pricing)
