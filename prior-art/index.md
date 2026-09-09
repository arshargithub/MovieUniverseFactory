# Prior-art assimilation record

Retrieval date: 2026-09-08. This bounded pass inspected primary publication records, project/repository documentation, LL3M's displayed license, and BlenderGym's setup script. No upstream software, prompts, weights, or assets were incorporated or executed. These are method-level lessons, not reproductions of paper results. Unresolved releases/licenses are recorded explicitly and do not block the original 3D-01 fixture.

| Component | Decision | Original implementation / reason |
|---|---|---|
| SceneCraft relation-first planning | Learn From | Dimensioned semantic plan with independent sofa support, table direction and clearance checks |
| SceneCraft reusable construction library | Learn From | Four small, reviewed procedural builders; no upstream code copied |
| LL3M documentation grounding | Learn From | Small pinned API topic index in [LL3M note](ll3m.md), direct runtime introspection for version differences |
| LL3M hosted client/server or restricted code | Ignore | License incompatible with unapproved reuse; server discontinuation reported upstream |
| BlenderGym edit categories | Learn From | Original placement/color edit and protected-camera/light/geometry/visibility negative controls |
| BlenderGym generator/verifier separation | Adapt concept | Separate machine visual review context plus deterministic expected-state/reference checks |
| BlenderGym assets/setup/dependencies | Ignore for 3D-01 | Code/data permission unresolved; unnecessary Infinigen/Torch dependency expansion |
| SimWorlds staged native-state verification | Learn From | Build → fresh reopen/inspect → render → edit parent → fresh inspect → independent render control |
| SimWorlds dynamic physics and long-lived server | Defer | Later tranche only; public reusable release/license unresolved in bounded pass |
| Geometry and image validators | Create New | Raw state arrays, deny-by-default comparison, explicit color conversion, mask-region SSIM/MAE |

Detailed evidence and separate license/runtime notes: [SceneCraft](scenecraft.md), [LL3M](ll3m.md), [BlenderGym](blendergym.md), [SimWorlds](simworlds.md).

Original fixture: `feasibility/3d/3d-01/fixtures/plan.json`. Original mutation controls: `tests/unit/test_structural_validation.py` and `tests/unit/test_perceptual_validation.py`. Integration execution, runtime measurements and observed success belong in campaign reports; this literature record makes no execution claim.
