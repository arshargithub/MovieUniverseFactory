# 3D-01.1 campaign report

**Decision: GREEN**

Machine-valid pairs: **5/5**. Director reviews are recorded.

## Environment and frozen configuration

- macOS 26.3.1 on arm64; outer Python 3.12.11
- Blender 5.2.1 LTS; binary SHA-256 `ea651e507c6b197df0e234bfa04e5ed43e7f4d498267a7df93fcb38f21928a5c`
- Blender Cycles CPU, 1280×720, 64 samples, three frozen cameras; two neutral frozen lights
- Planner: pinned `gpt-5.4-2026-03-05`, medium reasoning
- Visual reviewer: pinned `gpt-5.4-2026-03-05`, low reasoning, `low` image detail, prompt `3d011-blind-review-v3`
- Provider retries disabled; responses use `store=false`
- Scene interface: strict semantic plans and trusted structured Blender operations; no model-generated code is executed

## Source provenance

- Status: `EXACT_PRE_RUN`; implementation commit `5b56999a2fc6b8ae0d0cea46bb05d86de8c43ca1`; Git tree `1015278585bf51d7a85f478cd0f2c49020430f57`
- Commit and Git tree were recorded from a clean worktree before the first live provider call.

- Offline revision replay: seed 707; zero semantic differences; no provider calls; [attestation](replay-attestation.json)

## Machine outcome

All 5 selected pairs passed baseline structure, exact deny-by-default revision state, required mask visibility, oracle render comparison, and the model visual gate.
Each revision moved only `coffee_table_01` exactly 0.4 m toward `sofa_01` and changed only `helmet_shell_01` from `#C62828` to `#163D2A`; cameras, lighting, geometry, and protected materials remained unchanged.

Director review accepted all 5 pairs with a mean score of 4.8/5 per pair; minor sofa and table polygon faceting is recorded under physical finish.
The identical scorecards were intentionally entered as one batch review (`director-batch-3d011-20260909`) after the Director inspected every seed.

## Measured runtime and API use

- Selected-pair API calls: 10; input tokens: 41886; output tokens: 15274, including 10912 reasoning tokens
- Selected-pair known API cost: USD 0.333825000; average per machine-valid pair: USD 0.066765000
- Global durable-ledger committed amount, including remediation attempts and unresolved reservations: USD 2.52682723
- Median `R_edit`: 0.0000; median `R_api`: 0.5340
- Local rendering/provider-independent compute is measured in `metrics.csv`; no monetary value is assigned to local CPU time

Reasoning cost is an attribution within output cost and is not added twice. The ledger retains unknown reservations conservatively.

## Runs

- `seed-1001-20260910T023150Z-46182253` — machine-valid; model visual mean 4.6; Director mean 4.8; API USD 0.059555000; [comparison](../../runs/3d011-20260910T021945Z/seed-1001-20260910T023150Z-46182253/comparison.html)
- `seed-606-20260910T021945Z-3d552dc6` — machine-valid; model visual mean 4.4; Director mean 4.8; API USD 0.064397500; [comparison](../../runs/3d011-20260910T021945Z/seed-606-20260910T021945Z-3d552dc6/comparison.html)
- `seed-707-20260910T022228Z-683ada8a` — machine-valid; model visual mean 4.6; Director mean 4.8; API USD 0.065747500; [comparison](../../runs/3d011-20260910T021945Z/seed-707-20260910T022228Z-683ada8a/comparison.html)
- `seed-808-20260910T022523Z-c04607ec` — machine-valid; model visual mean 4.6; Director mean 4.8; API USD 0.076457500; [comparison](../../runs/3d011-20260910T021945Z/seed-808-20260910T022523Z-c04607ec/comparison.html)
- `seed-909-20260910T022835Z-c30de1a2` — machine-valid; model visual mean 4.4; Director mean 4.8; API USD 0.067667500; [comparison](../../runs/3d011-20260910T021945Z/seed-909-20260910T022835Z-c30de1a2/comparison.html)

## Failures, limits, and next action

Before freezing this selected campaign, 0 implementation-remediation attempts consumed USD 0.000000. Their artifacts and causes are retained in `remediation-attempts.json` and their costs remain included in the global ledger. They are not presented as Blender failures or selected results.
This five-pair experiment is evidence for the recorded 3D-01.1 configuration only; it is too small for a production reliability claim. Houdini and Unreal were not run.
GREEN applies only to supported, unambiguous structured revisions with LLM escalation for ambiguous instructions. Open-ended natural-language comprehension, general autonomous cinematography, production asset quality, and unrestricted model control of Blender remain outside this qualification.
Director reviews are complete and recorded.
Revision economics meet the GREEN ceiling: median `R_api` is 0.5340, at or below 0.75.
