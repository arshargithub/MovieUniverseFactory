# Movie Factory — roadmap from demonstrator to first series

**2026-09-17 update:** the [Release 01 plan](RELEASE_01_PLAN.md) is now the active outcome/sequence tracker for **a trailer plus episodes 1 and 2**, with ten-exchange checkpoints. This older roadmap remains supporting context; its calendar windows are not committed dates. The SSD migration is complete per the operations records. Trailer creative development remains paused for Director ideas; the new release scope does not revoke that pause.

Updated: 2026-09-15. Status: **DRAFT FOR DIRECTOR DECISIONS**. This document captures direction and proposed sequencing, not permission to execute every item, spend money, upload data, or delete local files. Dates are planning windows, not delivery promises. Director answers and available weekly capacity will determine the committed schedule.

## 1. Destination

Build a separate Movie Factory application whose conversational model is selectable and API-billed, whose knowledge belongs to the project, and whose production workflows do not require a signed-in Codex/ChatGPT session. Codex remains a development tool and an optional client, not the owner of production memory or the required runtime.

The first meaningful release should introduce the Director's **first series**. Develop enough characters, locations, world rules, and episode direction that assets and decisions used in the trailer/prologue transfer into the first episodes.

The earlier “AI Movie Production System” conversation explicitly proposed a **3–5-minute thesis film**. This is confirmed historical intent, not a newly approved duration. The current decision is whether that becomes a narrative prologue, a shorter promotional trailer, or both sharing footage. Recommendation pending Director choice: a **60–90-second trailer first**, with a **3–5-minute prologue** only if the story benefits from it. Do not silently replace the earlier length target. Duration, purpose, quality, and budget must be agreed before production planning.

Success is not just a released video: open the standalone app, select a model, retrieve approved series knowledge, develop a shot, approve a bounded production job, review/revise it, and carry the accepted state into another session or episode without asking Codex to reconstruct the project.

## 2. Current baseline and what has changed

- Blender adoption is recorded as **ADOPTED for the demonstrated persistent production backbone** in the [current demonstrator index](../../results/demonstrator-01/INDEX.md). No additional general Blender qualification series is proposed.
- The 24-second Courier rough cut is accepted. The smoother five-second camera successor is also [accepted](../../results/demonstrator-01/reuse-camera-revision/DIRECTOR_ACCEPTANCE.md), but remains **code-assisted**, not a parameter-only reuse pass. Do not repeat that test under the old spec or assume the reusable control gap is closed.
- Prior learnings remain in [Demonstrator 01 learnings](DEMONSTRATOR_01_LEARNINGS.md). Final visual quality, first-series characters, general reusable direction, and a standalone production app remain to be delivered.
- Local storage is blocking heavy work; the Director has ordered a 1 TB external SSD and plans separate S3 archiving work. This roadmap performs neither transfer nor deletion.
- The [racing/halt/rear/dismount brief](NEXT_PRODUCTION_EXPERIMENT_BRIEF.md) is retained but **not the automatic next priority**. Schedule any of it only if the selected series/trailer actually requires those capabilities and the Director approves the scope.
- The repository contains useful worker, validation, provider, ledger, and persistence code. Its original 3D-01 implementation contract is not yet a general product architecture. Adapt the existing components; do not rebuild all of them or apply apartment-fixture constraints to the whole application.

## 3. Parallel workstreams

| Track | Work that can start during the storage pause | Later dependency / visible outcome |
|---|---|---|
| Story and series development | Premise choices, audience/tone, series promise, core cast, world rules, episode 1–3 outlines, trailer/prologue beats | Director creative choices; approved series bible v0 and locked animatic |
| Durable knowledge | Inventory decisions/references; distinguish approved canon from drafts; define stable IDs, versions, approval and migration contracts | Used by both Codex and the app from the beginning; restart/model-switch memory check |
| Standalone app | Product scope, local interface design, model/provider boundary, small text-only app slice with mock production jobs | Separate implementation approval and tiny dependency footprint; no heavy renders required |
| Production integration | Inventory reusable controls and job/artifact contracts; prepare small mocked restart/retry tests and shot representation | SSD/resource readiness; app submits and reviews one real series shot |
| Storage and operations | Coordinate with separate S3 task; define metadata/media separation, path resolver, restore and cleanup contract | Verified archive/restore and SSD arrival; no blind move of hash-bound dependencies |

Parallel means independent deliverables can progress concurrently. It does not authorize spawning agents, starting multiple tasks, or running concurrent Blender workers. Avoid simultaneous edits to shared schemas; assign one implementation owner per shared contract when work is dispatched.

## 4. Proposed milestone roadmap

Use relative weeks from scope approval; the calendar examples assume approval around September 15. If the SSD, funding, weekly hours, or creative direction is delayed, move the dependent milestones rather than compressing quality work.

| Window | Milestone | Exit evidence |
|---|---|---|
| Now / week 1 | **M0: scope and preserve** — answer discovery questions, document series options, agree release type, inventory reusable code and critical knowledge, coordinate archive/SSD plan | Approved one-page product/creative brief; prioritized decision inventory; storage safety plan. No production spend implied. |
| Weeks 1–2, roughly Sep 15–28 | **M1: story + durable text workspace** — series bible v0, first three episode beat outlines, trailer/prologue treatment; app-owned knowledge and conversation records; first text-only conversational slice | Restart app and switch configured conversational model without losing approved facts, provenance, or unresolved questions. Codex not needed for normal conversation. |
| Weeks 3–4, roughly Sep 29–Oct 12 | **M2: actual-series production proof** — one recurring character/look and location tested in a 10–20-second reusable scene; minimal app job/review/revision workflow | Director accepts intended look/performance; same identity across contrasting shots; app-owned state survives restart. Requires verified storage and separately bounded production budget. |
| Weeks 5–8, roughly Oct 13–Nov 9 | **M3: locked plan to complete rough cut** — full release animatic, then shot batches using admitted assets; sound/edit assembly; only tests tied to required shots | Full target-length rough cut; every shot references canon/asset versions, costs, acceptance and dependencies; measurable marginal revision effort. |
| Weeks 9–12+, roughly Nov 10–Dec 7+ | **M4: finish and transition to episodic use** — selected polish, final sound, rights/credits, deliverables/backup; prepare episode 1 using the same cast/location | Accepted first release and portable project; episode 1 starts from existing assets/canon, not a reconstruction. A 3–5-minute prologue or high realism may push beyond this window. |

These windows are hypotheses, not estimates derived from the 24-second test. Do not extrapolate one rough-cut render rate into the complete production schedule. At M2 measure representative shot complexity, repair work, render time, storage and accepted-output costs; reforecast M3/M4. Agree one weekly prioritization/review session rather than another chain of micro-approval loops.

## 5. Remaining experiments: three integrated readiness checks

Each check belongs inside a useful deliverable. Freeze its scope, acceptance and resource limits before dispatch; preserve a failed result and make one decision instead of extending it into a new sequence of miniature campaigns.

### R1 — portable memory and independent conversation (storage-light)

Use a small Director-approved set of real project decisions and candidate series records. From the app: retrieve a canon fact with its source; distinguish a rejected idea from approved canon; propose but do not auto-approve a change; restart; select another supported conversational model; continue with the same canon/version and open work. Resolve a seeded conflicting revision explicitly. Export/import into a clean test workspace and compare record IDs, versions and critical facts. Unknown/unavailable historical material remains flagged, not invented.

Failure means fix the knowledge/approval boundary before extensive series authoring in the app. It does not require Blender. Start with one real provider and a tested adapter boundary; a second model tests model switching, but does not prove cross-provider parity. Add a second provider only if that is a confirmed requirement.

### R2 — first-series visual and performance proof (after storage readiness)

Use an actual intended recurring character and location, not another generic horse test. Create a 10–20-second scene with two or three contrasting shots and one directed revision. Demonstrate identity continuity, required acting/action, appearance, save/reopen and usable motion. Choose the hardest essential trailer beat, not the most elaborate imaginable effect. If spoken dialogue is essential, include a short voice/performance/lip-sync sample here; otherwise defer lip-sync. If hybrid finishing is allowed, test one controlled comparison with identity/editability checks here rather than running an unrelated provider tournament.

Freeze reference look and critical flaws in advance. Director full playback acceptance is required. Record unsupported capabilities and simplify the brief or make one targeted acquisition/implementation decision; do not endlessly repair unsuitable rigs.

### R3 — app-to-production repeatability (can share R2 footage)

Inside the Factory UI: choose the scene, request a supported shot/change, see proposed budget and affected dependencies, approve, dispatch, review, and accept. Restart the controller during a safe mocked/controlled job boundary; reconcile without duplicate paid submission. Produce a new shot and a meaningful supported revision without source-code changes after interface freeze. Outside-scope directions become explicit capability requests, not arbitrary runtime Python.

Measure setup separately from marginal shot/revision effort. If code is needed, report code-assisted and fix only the reusable capability required by the actual trailer. Do not repeat a new horse camera campaign just to change its label.

The full-release animatic and finishing review are production gates, not additional research experiments. New risks enter the schedule only when tied to a specific planned shot, a falsifiable question, a decision, and a capped work package. General Gatka, crowds, cloth, fluid simulation, Unreal/Houdini, and arbitrary rig support are deferred unless the first-series brief makes one essential.

## 6. Story development before expensive production

Update 2026-09-15: the Director has supplied the initial series seed, provisionally **The Martials**: a Jatt Sikh, a Gurkha and a female lead (possibly Pashtun) undertake unofficial missions for a British officer on the British India/Afghan frontier roughly 150 years ago. Colonial “martial races” ideology and conflicted service are central themes. See the [discovery brief](SERIES_01_DISCOVERY.md) for firm inputs, tentative choices and historical research boundaries. The title, exact year, female lead's background and release format are not frozen. CRE-01 can now advance to character motives and the concept brief; other open decisions remain.

Complete the [series discovery brief](SERIES_01_DISCOVERY.md). Early output should include:

- A clear premise, audience, tone, series promise and recurring source of conflict.
- Provisional core cast with motivations, relationships, appearance/voice invariants and intended development; distinguish required trailer characters from later cast.
- Core locations with dramatic purpose and reusable spatial/visual rules; do not construct the entire world.
- A season direction and short episode 1–3 outlines, including character/world state at entry and exit. Fully script only the release and the next production increment.
- A trailer promise or prologue story, distinguishing literal canon scenes from nonliteral promotional montage. Tag spoilers and unreleased future information.
- Approved look references and acquisition/creation strategy for essential reusable assets.

Do not promote brainstormed material to canon automatically. Every accepted creative decision should immediately enter portable project records, even while discussion still occurs in Codex.

## 7. Product and memory requirements before production scale

See [Factory app and memory baseline](FACTORY_APP_AND_MEMORY_BASELINE.md). Minimum product scope is a Director workspace: conversation/model selection, canon browser with sources, proposal/approval, shot/job list, media review and targeted feedback, artifact availability, and actual/reserved budget display. This is not a generic autonomous coding agent in a browser.

The transition happens incrementally: portable records now → text app early → app submits existing workers → app owns production state → Codex used only for development. Do not wait until “all code development is complete.” Maintenance will continue; the subscription downgrade milestone is **normal production no longer needs signed-in Codex**, not absence of future bugs or features.

OpenAI API usage has its own usage-based pricing; official Codex documentation also supports API-key-billed CLI/SDK workflows. A permanent Pro plan is therefore not technically mandatory even for every possible Codex-based design. The stronger reason for a standalone Factory is control over product behavior, memory, permissions, and provider choice. API billing is not a guarantee of lower total spend. Hosting/storage/rendering can have continuing costs even when model use is low. [Official Codex pricing](https://learn.chatgpt.com/docs/pricing) · [API pricing](https://developers.openai.com/api/docs/pricing).

## 8. Storage and budget guardrails

Keep code, compact canon/decision records, manifests and useful proxies small and locally accessible. Treat the SSD as an active media workspace and S3 as an explicitly configured archive/backup, not a live database or mounted production filesystem. Those roles are a proposed policy pending setup; an external SSD adds capacity, not RAM/GPU performance or an independent backup.

Use the existing [S3 archive contract](S3_ARCHIVE_SETUP.md): inventory, credential exclusion, verified upload plus representative restore, then a separately approved exact cleanup list. Do not construct another disk-sized archive while full. Preserve dependency and symlink mappings. The new app needs logical artifact IDs and a configurable location resolver so an archived or unplugged asset fails clearly instead of silently disappearing or changing identity.

While storage is blocked: no heavy rendering, large asset/model downloads, dependency sprawl, or duplicate exports. Even light development must fit a measured free-space envelope. Work with small text/mock fixtures; if dependency installation cannot fit safely, complete the contracts and creative planning first. Resume native work only after measured free space and dependency restore pass, not merely because the SSD arrived.

Agree separate budgets for development, conversational/model API use, generated media, assets/rights, compute, and storage/requests/retrieval. The previous demonstrator allowance is not a rolling monthly production budget. Track active engineering, unattended native time, Director waits, setup vs recurring costs, and reserved vs settled spend. Do not infer missing subscription tokens from plan percentages.

## 9. Next dispatches and ownership

These are queued work packages, not instructions to launch everything now:

| ID | Deliverable / owner role | Dependency | State |
|---|---|---|---|
| CRE-01 | Director + creative partner: series discovery and release brief | Director answers | READY FOR DISCUSSION |
| MEM-01 | Development: critical decision inventory and portable record/import contract | Source access; bounded task approval | READY TO SPECIFY |
| APP-01 | Development: thin text-only standalone app slice with persistence, model choice and cost ledger | MEM-01 contract; deployment choice; budget | READY TO SPECIFY |
| OPS-01 | Separate archive task: verified S3 transfer/restore and approved cleanup | AWS destination/permissions/budget | EXTERNALLY PLANNED; status must be checked |
| OPS-02 | Development: SSD artifact mapping and representative restore | SSD arrival; actual mount/storage choice | BLOCKED ON HARDWARE |
| PROD-01 | Creative + development: R2 series scene/look/performance | CRE-01, storage, asset/production approval | NOT READY |
| APP-02 | Development: R3 app-controlled shot/revision | APP-01 and a reusable scene/control boundary | NOT READY |
| REL-01 | Production: animatic → complete release → finish | R2/R3 gates, approved release scope | NOT READY |

Keep at most one main implementation item plus one independent creative/operations item active initially. Other queues may be planned in parallel, but should not compete for local storage or cause incompatible shared-schema changes. End each work package with outcome, evidence, consumption, remaining gap, and the single next decision.

## 10. Open decisions and provenance

Pending Director choices: series seed, release format/length, visual style and hybrid tolerance, dialogue/languages, episode length/platform, weekly hours, target deadline, category budgets, local/private vs remote/multi-user app, and manual creative involvement. The linked discovery brief records these without assuming answers.

Historical source: “AI Movie Production System,” task `6a82016c-3a88-83ea-a93b-b277f6526b97`, architecture-checkpoint turn `5074fd1c-46fd-4e0c-a292-6d697ed1f54d`, explicitly proposes the 3–5-minute thesis film and persistent production/runtime principles. Only relevant portions were revisited for this roadmap; the full historical decision corpus has **not** been migrated. MEM-01 must inventory it with source/coverage and Director review rather than claim no knowledge loss from a summary alone.

Execution baseline comes from the repository's current demonstrator index and camera acceptance. They supersede earlier review-pending descriptions. This planning pass makes no new experimental qualification claim and authorizes no cloud, model, asset or production expenditure.
