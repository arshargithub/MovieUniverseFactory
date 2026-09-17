# Historical knowledge and decision continuity

Established 2026-09-17 for [Release 01](../planning/RELEASE_01_PLAN.md). This index protects the original architecture/capability/UX work from being replaced by recent summaries.

## Capture status

Source: **AI Movie Production System**, task `6a82016c-3a88-83ea-a93b-b277f6526b97`.

- Retrieved all **75 available pages / 742 distinct exchanges**, ending with `hasMore=false`.
- **One assistant response is truncated by the retrieval interface's 20,000-character maximum:** “Movie Factory — v0.1 Mental Model,” source turn `8513f8af-73f1-4f7f-a0ca-cf3b8c04483f`, item `99b26944-00b4-41fd-9f73-f50a6d6569e0`. Its missing tail is unresolved; source export/full text is needed before declaring lossless capture.
- Attachments/external documents and material in other conversations are not automatically captured by this retrieval. Inventory them separately when referenced; no universal account-history coverage claim.
- Six local source snapshots under `.runtime/knowledge/ai-movie-production-system-20260917-part01.json` through `part06.json` preserve returned turns, user messages, assistant text and pagination. They are Git-ignored by existing policy, approximately 3 MB in total, and **not yet independently backed up by this planning pass**. Include them in the next approved private backup; do not assume the earlier S3 snapshot contains newly created files.
- [Source manifest](SOURCE_CAPTURE_MANIFEST.json) binds those exact local files. [Legacy decision register](LEGACY_DECISION_REGISTER.json) contains **588 heuristic candidates**, not 588 certified distinct decisions. Every candidate has source IDs, a short source excerpt and review status. Other source exchanges remain preserved even when the heuristic did not select them.

Capture completeness is not interpretation completeness. The register is deliberately unreviewed until each relevant item has been read in context, checked against user approval and later amendments, and mapped to an applicable requirement. Do not let automatic extraction declare canon.

## How to use it without rereading the entire conversation

1. Search candidate labels/excerpts for the current topic: universe/entity identity, representations, audience, production, approval, budget, reuse, retrieval, interface, orchestration, perception, soundtrack, distribution, etc.
2. Open the full local source turn and its preceding/following context. The page order is newest-first. Inspect the user's actual response; an assistant saying “Locked” is not alone sufficient evidence of scope or approval. Short excerpt fields are not full specifications.
3. Update the candidate with normalized decision statement, source/user approval evidence, status, conflicts/supersession, and an applicability disposition: ADOPT, ADAPT, DEFER, NOT_APPLICABLE or NEEDS_DIRECTOR_DECISION. Preserve the original excerpt/source pointer.
4. Link the reviewed decision to its current spec, implementation/test or explicit deferral. Record rationale for any deviation. Do not re-ask settled questions simply because a new orchestrator lacks context.
5. At release checkpoints report reviewed/mapped counts and critical gaps separately from captured counts. Review release-critical records first; deferred future capabilities remain preserved, not prematurely implemented.

## Migration acceptance

Before Factory takeover, enumerate the critical records across creative canon/alternatives, universe and production state, strategy/audience assumptions, reusable capabilities/assets, approvals, rights, job/budget state and original product/UX constraints. The Director accepts that checklist. Verify IDs/versions/provenance and representative question answers after export/import into a fresh app context, model change and controlled restart. Confirm an approved/rejected/conflicting decision cannot silently exchange status. Report incomplete sources honestly.

The current register and documents are the bridge, not an implemented universal memory service. They must remain readable outside Codex. “100% no loss” may be claimed only for a defined verified migration scope; source gaps and unknowns cannot be hidden behind that percentage.
