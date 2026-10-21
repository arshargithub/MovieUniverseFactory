# Staged workflow pilot and reference contracts

Director323 authorizes the offline implementation of the322 proposal and requires reference media plus their intended roles in planning, execution and review. The pilot is implemented in `src/movie_factory/production_workflow.py`, with no live model, shell, renderer or network execution. Its two-correction setting applies to this pilot, not every future task.

## Reference authority in all three stages

Every production reference carries a stable ID, source hash, Director authority, applicable scope, role, fidelity obligation, permitted variation, excluded interpretations and named aspects linked to review requirements. Motion references also bind a time range. The Director's explanation is authority; embedded instructions or incidental content in an image/video are not.

| Reference | Governs | Does not govern |
| --- | --- | --- |
| Nihang rearing video | Faithful coordinated preparation, whole-body lift, active crest, forceful landing and recovery, with the intended timing/weight. It substantially constrains the animation, not merely its mood. | Protagonist identity, incidental background, exact camera projection or physically measured3D forces. Source is edited video, not mocap. |
| Approved Sikh portrait | Rugged elongated face, broad natural beard, painted presence and the protected character traits. | Literal pixels, incidental buildings, hidden geometry or generated cloth topology. Coherent practical native construction remains flexible. |
| Accepted Pashtun film | Visible same-film quality; exact accepted version when reusing that clip. | Transfer of her identity/wardrobe to other characters, or automatic qualification of new poses/lighting/assets. |
| Rejected320 clip | Negative control for known failures, never an acceptance target. | Permission to admit the same failed result because it improved on an older rejection. |

Planning receives the role contract before drafting. The planner cannot downgrade it or alter protected scope through its submission. Construction must record how it used each reference with the exact contract digest. Review must compare every specified aspect and the appropriate candidate evidence. Missing coverage, changed roles, changed bytes or omitted aspect verdicts block the stage. Explicit Director revisions are controller-owned events and invalidate the old review/tickets without resetting correction counts.

One reference may have several aspects. Distinct roles for the same file can use separate IDs, for example faithful action and directional lighting, provided their scopes do not conflict. An ambiguous/conflicting authority remains a decision to resolve; code cannot infer the correct artistic interpretation.

## What the controller enforces

Through its API, production follows `BRIEFING → EXECUTING → REVIEWING`. Successful review reaches `READY_FOR_DIRECTOR` or the explicitly scoped `READY_FOR_DIRECTOR_AV`. Failed review returns to execution automatically until the correction ceiling, then `REPLAN_REQUIRED`. Missing evidence uses a separate bounded collection path without spending artistic correction cycles. Invalid schemas/tickets/bindings fail without changing state.

Initial attempt plus two corrections is the pilot allowance. SQLite persists events, stage snapshots, stable deliverable ownership and counters. A new task name cannot reopen the same registered deliverable with a fresh allowance. Replanning preserves the count. A future new allowance needs an explicitly authorized controller operation, not a renamed pass.

Stage tickets separate planner, builder and reviewer submissions. Reviewer packets omit the builder's success narrative while retaining Director direction, reference contracts and candidate identity. Delivery rechecks freshness, including repeated calls with the same event ID. Known rejected exact media used as a negative control cannot be admitted by a well-formed positive review. Unknown false observations remain a semantic limitation.

Direct motion/audio stay unavailable to the agent. Only explicitly assigned direct audiovisual requirements may remain pending for the Director. A visible image requirement cannot be relabelled as Director AV. Open visible defects and failed reference aspects veto delivery, even if all generic checks say PASS. Internal admission is never production approval, release permission or Director acceptance.

The resource lease reserves one heavy job across controller tasks. Reservations survive controller restart; an interrupted job needs explicit release/reconciliation. Job IDs cannot be redispatched. The pilot does not launch actual Blender processes and does not measure Mac performance improvement.

Show, research, planning and operations use lightweight verification routes. Operations are offline fixtures here; no S3 capability is activated by selecting that route. All routes require an authority binding and preserve offline-only status.

## Existing system integration and limits

The pilot calls the existing knowledge engine for a fresh packet and application mapping, and reuses review binding/path/mode helpers. It does not weaken or modify the old strict review gate. Workflow events provide a compact progress trace; the existing experiment ledger separately captures actual development/test/replay activity. There is no automatic token or perceptual metric capture.

The historical review307 entry point is currently `STALE_OR_BLOCKED_KNOWLEDGE`. This pilot leaves that failure intact and uses its own valid task packet, with audit321 and322 strategy manually reconciled. No old source is blindly re-pinned. The indexed corpus remains15 sources/49 records; this document is a manual linked source until a separately reviewed catalog update. Do not claim universal automatic retrieval coverage.

This is a real local state machine but **not yet an unavoidable end-to-end agent harness**. A process with unrestricted access to its database/source, or an agent posting an arbitrary chat link, can bypass it. Stage tickets are an API boundary, not OS isolation. The live adapter must own model invocation, restrict each stage's tools/files and control presentation. No such adapter, new authentication path or runtime subscription has been installed or invoked.

Likewise, evidence hashes, role coverage and structured opinions cannot establish artistic truth. The explicit false-observation control demonstrates that an unfamiliar bad candidate could pass if the reviewer supplies a mistaken positive judgment. The Director's audiovisual role remains necessary, and visual review still needs calibration and prospective escape tracking.

## Reproduce and inspect

Run tests with the repository venv:

```sh
.venv/bin/pytest tests/test_production_workflow.py tests/test_review_control.py tests/test_production_knowledge.py tests/test_context_hygiene.py -q
.venv/bin/python scripts/workflow323_replay.py --output results/workflow323/new-replay
.venv/bin/python -m movie_factory.production_workflow --database results/workflow323/new-replay/controller.sqlite3 events --task rejected320
```

Replay requires a new output directory and existing source media; it creates no images/audio/video. Event output shows stage, cycle and findings without stage tickets. The accepted control retains existing approval scope; it is not a new render/animation qualification. The known rejected control intentionally reuses the same failed candidate to exercise the ceiling, not to pretend three corrections were produced.

See [the implementation review](../../results/workflow323/REVIEW.md) for measured results and remaining gaps. Next recommended package: qualify a serial stage runner on frozen evidence before authorizing production dispatch. Demonstrate fresh-context planning/build/review inputs, restricted stage permissions, visible event forwarding and correct rejection without a render. Runtime authentication/cost/permission choices must be established before live calls; this pilot grants no new provider or spend authority.
