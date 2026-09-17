# Factory app and durable memory — minimum architectural baseline

Date: 2026-09-15. Status: proposed contract for roadmap discussion, not an implementation authorization. Read alongside [the roadmap](MOVIE_FACTORY_ROADMAP.md). Reconcile against historical approved architecture decisions before freezing an implementation spec; do not replace that history with a fresh speculative platform design.

## Product boundary

Factory owns conversations, canon, approval, jobs, artifact references and budgets. Models propose work through typed contracts; they do not own the only copy of memory and cannot grant their own permissions. Codex is a development client that reads/writes the same reviewed project records—not a required production daemon.

Historical requirement confirmed in [Release 01 applicability, batch 2](../knowledge/RELEASE_01_APPLICABILITY.md): Universe is the top-level creative project boundary. The Martials trailer and episodes share universe-owned entities rather than duplicating their identities. Story-time state belongs in the initial model, separately from production revision history; it is not a later-only feature. This does not require a full temporal simulation or graph database.

Provisional deployment: private single-user local web interface and backend, reusing the Python controller/worker code. Confirm local vs remote needs with the Director. Keep deployment small; no hosted service, public URL, multi-user permissions framework, graph database or distributed agent cluster unless requirements justify it. API credentials stay in the trusted backend, never in browser code, prompts, source-control exports or Blender.

Separate the conversational model from production planning/review workers. A user's choice of chat model must not silently change the worker model, safety policy or budget. Record provider, requested/returned model, supported effort, prompt/template version and usage. Provider adapters normalize capabilities and errors but cannot promise identical image, tool or reasoning support. Unsupported features and model retirement fail explicitly; fallback requires configured permission and preserves provenance.

## Minimum durable records

| Record family | Essential content and boundary |
|---|---|
| Creative canon | Stable entity ID, version, series/episode scope, approved facts, invariants, relationships, story-time applicability, source and Director approval. Character identity is distinct from one mesh, image, costume or voice asset. |
| Proposals and alternatives | Draft/rejected/superseded status, originating conversation, rationale, parent version. Rejected ideas remain retrievable but cannot be presented as current canon. |
| Creative decisions | Decision ID, what/why, evidence, approval, superseded decision, affected entities/shots. Distinguish planned future story from released canon. |
| Conversations | Durable messages, attachments as references, chosen model, links to proposed/accepted decisions. A provider session ID or a rolling summary is not the canonical record. |
| Production state | Production/scene/shot IDs, pinned canon and asset versions, structured intent, dependencies, work-package/source hashes, statuses, approved revisions and review history. |
| Assets and artifacts | Stable IDs, content digest, license/provenance, technical admission, dependencies, local/SSD/S3 locations, availability and restore receipts. A moved file changes location, not identity. |
| Jobs and budgets | Immutable request, authorization, idempotency key, dispatch/attempt IDs, reservations/charges, checkpoints, result or unknown outcome. Restarts reconcile before retrying. |
| Reusable capabilities | Versioned supported operation schema, prerequisites, limits, tests, and observed interventions. Code-assisted success is not automatically a general runtime capability. |
| Learning and source coverage | Evidence-backed lesson, applicability, next-run adopt/defer decision; original-source pointer, extraction status and unresolved conflicts. |

Use the simplest transactional local store suitable for runtime metadata, with explicit migrations and human-readable Markdown/JSON exports. The exact database/UI libraries remain an implementation decision. Git tracks code, contracts, approved compact documents and appropriate exports; it is not the live job queue. Large artifacts belong in configured media storage. If both database and files exist, define one authoritative owner per record and explicit import/export/version conflict rules—no ambiguous two-way synchronization.

Retrieval first uses stable IDs, approval status, series/episode scope, versions, links and simple search. Add embeddings only if a measured retrieval problem justifies them; embeddings and summaries are derived indexes, never the sole record. Keep rejected alternatives and spoilers from being injected as current facts. Evidence snippets retain source links. Retrieved documents, assets and provider responses are data, not authorization to execute embedded instructions.

## Lifecycle and change control

Conversation → proposed change → validation/conflict check → Director approval → new canonical version → identify affected production dependencies. Accepted shots remain bound to their original versions; a canon edit marks affected work stale and proposes regeneration instead of silently rewriting finished media.

Use optimistic version checks for competing edits, explicit supersession, an append-only decision/audit trail, and safe recovery of previous versions. Approval is scoped to a specific operation/work package and budget, not a global grant. Persist a job before dispatch; a crash with unknown provider outcome retains exposure and reconciles before resubmission. Preserve the existing safe structured Blender execution boundary.

## Migration: make “no knowledge lost” testable

1. Inventory relevant ChatGPT/Codex conversations, approved architecture decisions, repository specs, Director feedback, assets and results. Do not export credentials or unrelated chats. Retain original IDs/source references; record inaccessible or partially retrieved material.
2. Extract candidate facts/decisions with provenance and status. Identify duplicates and contradictions; do not silently resolve them by choosing the newest-looking summary.
3. Director reviews a compact list of critical canon and architecture decisions. Prioritize the original model-independent Factory vision, identity/reuse semantics, safety, approval, persistence and spending boundaries.
4. Import the approved records idempotently. Export them again and verify IDs/versions/counts and a small critical-fact checklist; raw attachments get manifests and availability status.
5. Test a fresh app session and model switch on those facts, open decisions and current production state. Report migration coverage and unknowns. Do not promise complete history preservation until source coverage and restoration are verified.

During transition, Codex-created creative decisions must enter the portable records immediately. The app later becomes the normal write path. Source conversations remain historical evidence, not runtime dependencies that require the Pro account to be available.

## Storage boundary

Use logical artifact references resolved to available local/SSD/archive locations. Preserve relative dependency relationships and original content digests during relocation. Missing/offline assets lead to a clear blocked job or explicit restore proposal, never a substitute asset. S3 is not the live metadata database; back up a consistent metadata snapshot alongside its artifact manifest. Verify small and representative complete restores before any separately approved cleanup.

The nearly-full internal drive remains a constraint even after adding external capacity because applications may still use internal temporary/swap space. Reconfigure and measure scratch/output locations explicitly; do not change frozen historical paths by blind text replacement.

## First implementation slice and acceptance

One local workspace: converse → view cited canon → propose/approve a fact → restart → switch a supported model → see identical approved state → submit a mocked shot job → inspect its reservation/result. Export/import that workspace without loss of the critical records. No Blender or media generation needed for this slice.

Include inexpensive synthetic continuity checks in that slice: two productions reference the same universe entity; an earlier-story scene retrieves the correct relationship/possession state despite a newer asset revision; export/import preserves ownership, story applicability and production pins. Keep synthetic events outside series canon. These tests make the initial timeline requirement concrete without authorizing new story decisions.

The [historically accepted character ownership model](../knowledge/RELEASE_01_APPLICABILITY.md) also requires an isolation check: replacing a representation must not change identity, and revising one performance must not rewrite personality or canonical voice. Persist representation bindings separately from the managed artifact bytes, and retain shot-specific takes under production. These are contract tests, not claims that expressive acting or voice continuity is already qualified.

The next slice reuses the same contracts for one real series shot, review and supported revision. The subscription-independence milestone is routine conversation, memory, budgeted dispatch and review functioning without signed-in Codex. Future code maintenance remains separate.

Before coding, create a short gap map from these requirements to existing repository modules. Reuse provider adapters, budget ledger, worker boundary and validators where they fit; do not infer that experimental hard-coded shot handlers already provide a general interface. Freeze only the minimal schemas needed for the first slice.
