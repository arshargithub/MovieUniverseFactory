# Exchange323 — offline workflow pilot outcome

The approved offline implementation is complete. The controller enforces stage transitions through its API, carries reference-role contracts through all three stages, and persists correction limits and evidence bindings. It does **not** yet run agents or enforce what an unrestricted chat agent can present.

## Measured results

| Check | Result and scope |
| --- | --- |
| Focused regression suite | **192 passed in 5.57s** in `validation01/tests.txt`: controller, existing review control, knowledge engine and context hygiene. |
| Fresh knowledge evidence gate | **Ready for review**, no failures; `validation01/knowledge-gate.json`. This validates this software work package, not production imagery. |
| Known rejected Nihang320 replay | Initial candidate plus two deliberately repeated failed submissions reaches **REPLAN_REQUIRED**; no delivery. No scene corrections were made in this replay. |
| Accepted Pashtun253 reuse control | Reaches **READY_FOR_DIRECTOR_AV** within the exact recorded reuse scope. No new acceptance or direct audiovisual judgment; historical strict replay failure remains separate. |
| Persistence/resource checks | Restart and brief revision retain the correction count; renamed tasks cannot reset a registered deliverable. Single heavy-job reservation and duplicate-job rejection tested without launching Blender. |
| Reference checks | Planner, builder and reviewer must cover the same contracts. Changed reference bytes/roles, missing aspects and inappropriate evidence modes block admission. |

Final replay evidence is `replay03/replay.json`, with a compact transition trace in `replay03/REPLAY.md`. Earlier replay01/02 remain local diagnostic history. SQLite replay databases are excluded from Git because they contain stage tickets; the replay script reproduces them from available source media.

## Reference roles, not merely attached media

The rearing video constrains coordinated preparation, lift, crest, forceful landing/recovery and intended motion timing. Directional Sikh portraits constrain identity and painted character, but permit practical native geometry instead of literal reconstruction. The accepted Pashtun supplies a same-film quality floor; rejected320 is a negative control, never a weaker replacement target.

Each contract records source/hash, authority, scope, role, fidelity, permitted variation, excluded interpretations and named aspects linked to requirements. Planning must preserve it; construction records its application; review compares its aspects against the candidate. Direct motion/audio aspects remain explicitly Director-owned and separate from agent-visible frame/appearance checks. Missing direct AV cannot conceal a visible failure.

I reinspected the preserved321 appearance and phase-comparison sheets. The visible issues still include straighter hind support/neck forms than the reference, angular paired forelegs, rigid rider appearance and simplified clothing/saddle forms. These remain negative evidence. This was a familiar frame-sheet review, not a new full-speed viewing or independent perceptual benchmark. Audit321 and its evidence were not changed.

## Failures and limits retained

- A broader pre-final test run returned **201 passed, 3 failed**. The failures are in unchanged historical317/319 source-pin/count expectations: `test_original_source_pins_preserved`, `test_delivery_preserves_exact_accepted_unit_without_new_narration_authority`, and `test_all_thirteen_previous_source_snapshots_are_unchanged`. The current corpus has evolved. I did not rewrite old expectations or repin sources to manufacture a clean result. The focused192 result is not a claim that the entire repository suite passes.
- The old review307 entry point still reports **STALE_OR_BLOCKED_KNOWLEDGE**. This pilot uses a separate fresh task packet and manual reconciliation of321/322/323, not a bypass approval for scene production.
- Known exact-negative hashes block admission, but an unfamiliar poor candidate with a well-formed, mistaken positive judgment can still pass. A test deliberately demonstrates this limitation. Structural enforcement is not artistic truth.
- Stage tickets are API separation, not OS isolation. The controller records the next stage; it does not invoke it. No live adapter controls model context, tools or final chat presentation yet.
- No speedup percentage, context-reduction percentage or improvement in visual-review accuracy was measured. Development lifecycle capture began after initial orientation; that gap and unknown model/token usage remain disclosed. See the operating report for captured intervals, not an exact total-effort claim.
- The new workflow document is a linked/manual source, not automatically admitted to every knowledge retrieval packet. Catalog integration requires its own source review and tests.

## Deliverable and next package

Implemented source: `src/movie_factory/production_workflow.py`; tests: `tests/test_production_workflow.py`; offline replay and validation scripts: `scripts/workflow323_replay.py` and `scripts/workflow323_validate.py`. The workflow explanation is in `docs/knowledge/PRODUCTION_WORKFLOW_323.md`.

**Recommended next action:** qualify a serial stage runner on frozen evidence before using it for Nihang construction. The Director should receive a readable end-to-end trace demonstrating planning → execution → review → correction or admitted handoff, with reference roles intact and progress visible throughout. Include fresh stage contexts, restricted tool/file access, retry/restart behavior and a presentation gate. Exclude new scene/media generation, parallel agents and new provider spending. Establish the supported runtime/authentication/cost route first; if it needs new authority, present that material choice rather than silently adding it.

Exit criteria: the runner cannot skip review, deliver a known-failing candidate, consume an extra correction through retries, or hide a stopped job. Only then apply it to the isolated Nihang/rearing/crowd sequence with the agreed continuity handles. A production-ready image or motion result is not claimed by this software pass.

This pass created no media, invoked no provider or cloud service, installed nothing and changed no scene. Commits are local and scoped; no remote push or S3 protection is part of this pass. Local commits are not disaster-recovery backups.
