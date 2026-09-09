# 3D-01 campaign report

**Decision: YELLOW**

Machine-valid pairs: **5/5**. Director reviews are recorded. Revision API economics are in the YELLOW band.

## Environment and frozen configuration

- macOS 26.3.1 on arm64; outer Python 3.12.11
- Blender 5.2.1 LTS; binary SHA-256 `ea651e507c6b197df0e234bfa04e5ed43e7f4d498267a7df93fcb38f21928a5c`
- Blender Cycles CPU, 1280×720, 64 samples, three frozen cameras; two neutral frozen lights
- Planner and visual reviewer: pinned `gpt-5.4-2026-03-05`, medium reasoning, no provider retries, `store=false`
- Scene interface: strict semantic plans and trusted structured Blender operations; no model-generated code is executed

## Source provenance

- Status: `post_hoc_reconstructed`; implementation commit `1a62dbb915ee7636f6e3f031e910b8804773af3c`; Git tree `72382e40a165b1c9668e5f4b58c36f482176991b`
- Evidence seal tag: `3d-01-v1-yellow`. The live API campaign ran before the implementation was committed. This binding identifies the sealed committed reconstruction used for offline replay, not a contemporaneous source commit for the live calls. Offline replay against this commit supplies the reproducibility check.

- Offline revision replay: seed 303; zero semantic differences; no provider calls; [attestation](replay-attestation.json)

## Machine outcome

All 5 selected pairs passed baseline structure, exact deny-by-default revision state, required mask visibility, oracle render comparison, and the model visual gate.
Each revision moved only `coffee_table_01` exactly 0.4 m toward `sofa_01` and changed only `helmet_shell_01` from `#C62828` to `#163D2A`; cameras, lighting, geometry, and protected materials remained unchanged.

Director review accepted all 5 pairs with a mean score of 4.8/5 per pair; minor sofa and table polygon faceting is recorded under physical finish.
The identical scorecards were intentionally entered as one batch review (`director-batch-3d01-20260909`) after the Director inspected every seed.

## Measured runtime and API use

- Selected-pair API calls: 15; input tokens: 45035; output tokens: 17788, including 12539 reasoning tokens
- Selected-pair known API cost: USD 0.379407500; average per machine-valid pair: USD 0.075881500
- Global durable-ledger committed amount, including remediation attempts and unresolved reservations: USD 0.858677507
- Median `R_edit`: 0.1679; median `R_api`: 0.9786
- Local rendering/provider-independent compute is measured in `metrics.csv`; no monetary value is assigned to local CPU time

Reasoning cost is an attribution within output cost and is not added twice. The ledger retains unknown reservations conservatively.

## Runs

- `seed-101-20260908T200952Z-a06e17f0` — machine-valid; model visual mean 4.0; Director mean 4.8; API USD 0.080372500; [comparison](../../runs/3d01-20260908T200952Z/seed-101-20260908T200952Z-a06e17f0/comparison.html)
- `seed-202-20260908T201252Z-fd79e5d8` — machine-valid; model visual mean 4.4; Director mean 4.8; API USD 0.070547500; [comparison](../../runs/3d01-20260908T200952Z/seed-202-20260908T201252Z-fd79e5d8/comparison.html)
- `seed-303-20260908T201610Z-8fbfe21a` — machine-valid; model visual mean 4.2; Director mean 4.8; API USD 0.075452500; [comparison](../../runs/3d01-20260908T200952Z/seed-303-20260908T201610Z-8fbfe21a/comparison.html)
- `seed-404-20260908T201921Z-936fd672` — machine-valid; model visual mean 4.4; Director mean 4.8; API USD 0.078512500; [comparison](../../runs/3d01-20260908T200952Z/seed-404-20260908T201921Z-936fd672/comparison.html)
- `seed-505-20260908T202234Z-f0ee1b7f` — machine-valid; model visual mean 4.2; Director mean 4.8; API USD 0.074522500; [comparison](../../runs/3d01-20260908T200952Z/seed-505-20260908T202234Z-f0ee1b7f/comparison.html)

## Failures, limits, and next action

Before freezing this selected campaign, 5 implementation-remediation attempts consumed USD 0.345125. Their artifacts and causes are retained in `remediation-attempts.json` and their costs remain included in the global ledger. They are not presented as Blender failures or selected results.
This five-pair experiment is evidence for the recorded 3D-01 configuration only; it is too small for a production reliability claim. Houdini and Unreal were not run.
The autonomy result is deliberately narrow: cameras and lights were frozen, planning bands were tight, and the revision contract allowed two known operations. It demonstrates persistent semantic state, trusted structured Blender execution, exact targeted revision, preservation, and offline replay. It does not demonstrate general autonomous cinematography, arbitrary natural-language editing, production asset quality, or unrestricted model control of Blender.
Director reviews are complete and recorded.
To pursue GREEN, reduce all revision-runtime API cost enough to bring median `R_api` from 0.9786 to at most 0.75 without weakening validation.
