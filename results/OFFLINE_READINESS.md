# 3D-01 offline readiness report

Date: 2026-09-08

Scope: Blender-first implementation and offline qualification
Live campaign status: **COMPLETED — 5/5 MACHINE-VALID AND DIRECTOR-ACCEPTED**

## Environment

- macOS 26.3.1 on Apple Silicon (`arm64`)
- Blender 5.2.1 LTS, build `9e2066aef7ef`
- Blender binary SHA-256: `ea651e507c6b197df0e234bfa04e5ed43e7f4d498267a7df93fcb38f21928a5c`
- CPython 3.12.11 managed under `.runtime/python`
- All outer Python packages installed in the project-local `.venv` from the hash-pinned `requirements.lock`
- `.env` mode verified as `0600`; the doctor reports credential presence as booleans and does not print values
- 43.06 GiB free at the recorded doctor run

The complete machine-readable result is `results/doctor.json`.

## Verification results

| Check | Result | Evidence |
|---|---:|---|
| JSON schemas, validators, packages, provider accounting, and failure cases | GREEN | 70 unit tests passed |
| Native Blender build, save, reopen, revise-from-parent, repeat, and three-shot render | GREEN | 1 opt-in native integration test passed |
| Mock end-to-end initial/revision pair | GREEN | `runs/controls/seed-101-20260908T194308Z-f110f853/result.json` |
| Frozen-scene render repeatability at 1280×720, 64 CPU samples, three shots | GREEN | `results/calibration.json`; two independent comparisons passed with pixel-identical output |
| Immutable package identity and offline rebuild/render replay | GREEN | `replays/seed-101-initial-semantic-v3/replay-result.json`; zero semantic differences |
| Deliberate schema, camera, unit, material-sharing, visibility, target, budget, and provider failures | GREEN | Fail-closed unit/failure-injection suite |

The mock pair proves the controller and deterministic Blender path. It is not counted as a live model qualification. Director review remains `PENDING` by design.

## API and budget state

The configured planner and visual-review model is pinned to `gpt-5.4-2026-03-05`. API authentication and structured output were verified in development preflights. After the authorized live campaign, the persistent ledger at `results/budget.jsonl` records:

- total known cost: **USD 0.846190007**
- unresolved conservative reservation: **USD 0.0124875**
- total committed amount: **USD 0.858677507**
- all scored calls and known cost, including retained remediation attempts: **22 / USD 0.724532506**
- selected five-pair campaign calls and known cost: **15 / USD 0.379407500**
- campaign cap: **USD 40**

The unresolved reservation came from a failed provider request that returned no billable usage. It remains charged against the local cap because the fail-closed ledger has no provider evidence that the cost was zero.

## Live qualification result

The authorized live run completed all five fixed seeds with three views per state. All five selected pairs passed structural validation, exact revision validation, required visibility, oracle render comparison, and the model visual gate. Director review accepted every pair at 4.8/5, recording minor polygon faceting under physical finish. The result remains YELLOW because median `R_api` is 0.9786, within the specification's YELLOW economics band but above its 0.75 GREEN ceiling. See `results/3d01-20260908T200952Z/REPORT.md` and its `metrics.csv`.

Houdini remains a later challenger adapter and Unreal remains a later real-time staging/render complement. Neither is required for the 3D-01 Blender qualification.
