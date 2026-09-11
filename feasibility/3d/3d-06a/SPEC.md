# 3D-06A — reference-timed upper-body gesture

Status: **AUTHORIZED / DEVELOPMENT**. The user authorized execution after the operating handoff. Begin with the reference plan and fixture screen; no scored freeze or Director acceptance is claimed yet.

## Question, reference and scope

On the known stationary humanoid, can a small right-hand acknowledgement match a reference pose/time plan, then hit an explicitly earlier cue without changing motion outside the permitted interval or reducing visual quality?

Use the accepted 3D-03.1 character, `character_01`, height 1.75 m, source FBX SHA-256 `18835fef534eede635b081ee7fe647d01a885550a591d2e6bf071010906167d8`; use the packed accepted fixture identified in the prior campaign, not a fresh uncontrolled import. Record the exact chosen `.blend` hash, rig/skin/action bindings and Blender build before freeze. Keep the stationary root, feet, identity, skin, cameras and lights protected. No sword or other prop, locomotion, contact transfer, facial performance, cloth, hair or combat.

The first reference is a **manually authored and annotated pose/time board**, not automatic motion extraction or faithful transfer from a human video. Complete the motion brief and commit 3–5 landmarks before candidate generation. Proposed 4-second clip at 24 fps, frames 0–96 with 96 unique playback samples and frame 96 retained for boundary inspection. Motion is one-shot, not required to loop. Gesture: modest forearm rise toward lower chest, small acknowledgement, then return; stay within the rig's comfortable range established by screening. Do not force the known elbow limitation.

| Landmark | Baseline frame | Meaning |
|---|---:|---|
| Rest | 0 | Stationary neutral pose |
| Preparation | 24 | Small coordinated shoulder/forearm preparation |
| Cue pose | 48 | First attainment of the annotated acknowledgement pose |
| Settle | 60 | Decelerated brief hold |
| Return | 96 | Back to neutral |

Before freeze, the board must contain explicit joint-space orientations and shoulder-relative wrist/elbow coordinates (or a specified measured cue observable) with units and hashes. Empty/unmeasurable landmark data block freeze. The cue is the first entry into the declared pose tolerance, not an arbitrary keyframe label. Manual annotation/acquisition effort is recorded separately. Future video-derived reference work needs its own provenance and annotation contract.

## Fixture suitability and motion planning

Complete `docs/planning/MOTION_DESIGN_TEMPLATE.md`. Screen neutral, preparation, cue, hold and return poses plus one inexpensive complete preview. Inspect shoulder/elbow/wrist skin, hand posture, limb reachability and balance. Preserve the existing 26-edge elbow regression screen's 0.35–1.50× band; do not reinterpret it as universal tissue quality. Freeze measured comfortable joint ranges. If the small gesture fails the admitted range/skin screen after at most three variants of one hypothesis, stop that episode and qualify the replacement rig separately.

Replacement admission (later, independent): documented rest pose, bone axes and usable IK/FK controls, independent fingers if needed, reliable skinning at selected elbow/shoulder/wrist extremes, units, rights/provenance, reproducible import/reopen, a short known gesture and acquisition/adaptation time. Only after that should reference motion move to the new fixture, followed later by the previously qualified prop or a short combat segment.

## Revision and proposed numerical acceptance contract

The revision requests the acknowledgement at **frame 44 instead of 48**. This cue has an explicit reference target; aesthetic preference is optional. Modification is confined to `[24,72]`, with a blending envelope of zero value and first derivative at both boundaries. Use an isolated action copy; do not change every repetition or the original reference. Head/torso coordination is authored in the baseline; timing revision changes timing, not the spatial gesture.

These are proposed thresholds to review against the fixture screen, then freeze before scoring. Any justified draft change must be versioned before candidate generation/scoring; it cannot be used to rescue an already-scored failure.

- Baseline cue: frame 48 ±1 frame; candidate cue: frame 44 ±1 frame. Candidate landmark pose RMS wrist/elbow position error ≤0.02 m relative to the annotated shoulder frame; selected joint orientation error ≤5°. Freeze interpolation and cue detection rules, including the first-attainment rule for a held pose.
- Exact equality for protected semantic IDs, mesh topology, materials, nonedited actions, ownership and metadata; sampled numerical preservation outside `[24,72]`: evaluated vertex/position error ≤1e-6 m, orientation error ≤1e-5 radians.
- Boundary continuity: added positional discontinuity ≤1e-5 m, added velocity discontinuity ≤0.02 m/s and angular velocity ≤10°/s, evaluated on the physical 24-fps timeline. Probe boundaries and cue windows at offsets ±0.001, ±0.01, ±0.1, ±0.25 and ±0.5 frame as well as every integer frame.
- Fixed root and support contacts: maximum foot displacement relative to baseline ≤0.003 m; floor penetration ≤0.002 m. Whole-clip finite coordinates, unchanged topology and no abrupt deformation; retain the admitted elbow-edge band and document any additional screen before freeze.
- Full playback Director scores: ≥4/5 readability, natural movement, transition smoothness and finish for the candidate; candidate must not regress in any dimension against baseline; no major defects. A tie meets the non-regression requirement. No required 0.5 preference/readability gain. Record review duration, observations and optional preference.
- Exact semantic persistence and deterministic numerical replay within the frozen tolerances. Save/reopen at rest, cue and hold. Reference pose data, timing revision, source/configuration, asset and implementation digests belong in the immutable work package.

GREEN requires reference/timing, preservation, deformation, controls, persistence/replay and complete Director gates. Missing reference/fixture screening is NOT_RUN. Missing required evidence/review is YELLOW; a technical failure is RED. A bounded investigation may close any colour with findings; colour is separate from lifecycle.

## Comparison, controls and validation economy

Use synchronized anonymously labelled baseline/candidate complete playback with a common reference cue marker and a clear primary plus elbow/hand view. Avoid duplicate endpoint holds using the verified player workflow. Preserve the original images and video provenance. Controls must be disposable real Blender action/scene mutations measured by the production inspector: no-op/wrong cue, whole-action timing leakage, boundary discontinuity, support-foot drift and elbow deformation. Each must fail its designated gate that passes in the positive scene. JSON-only number editing is insufficient.

During development run targeted fixture/landmark/boundary probes, then one complete inexpensive preview, then one full frozen suite. A dependency table in the frozen configuration must map each test to implementation/config/asset hashes. Reuse is only eligible when that test's inputs and all relevant implementation dependencies match an explicitly permitted prior result. New reference-cue controls and changed motion always execute in this scored suite. Do not omit unchanged mandatory gates unless the frozen contract expressly admits reusable evidence. Preserve failures.

## Learning delta

| Prior evidence | Next-run change | Verification | Decision / rationale |
|---|---|---|---|
| [3D-05 tie](../../../results/3d05/closure-v1/director-review.json) | Explicit frame-44 cue and non-regression quality gate | A tie with correct timing passes; no-op misses cue | ADOPT — instruction fidelity is the question |
| [Late geometry/fixture changes](../../../results/3d05/closure-v1/PROCESS_REVIEW.md) | Pose/range screen before candidates | Suitability record and landmark hashes predate candidate | ADOPT — avoid tuning an unsuitable fixture |
| [Coordinated motion lesson](../../../docs/decisions/0004-motion-design-before-implementation.md) | Motion brief and pose board first | Complete inexpensive preview before freeze | ADOPT — natural motion requires a whole-body plan |
| [Duplicate full suites](../../../results/3d05/closure-v1/PROCESS_REVIEW.md) | Target changed dependencies; one scored full suite | Dependency hashes and explicit reuse eligibility | ADOPT — retain rigor while bounding cost |
| [Mixed effort accounting](../../../results/3d05/closure-v1/PROCESS_REVIEW.md) | Phase ledger, disk forecast, scoped usage | Closing JSON shows known costs and unknown coverage | ADOPT — engineering cost is not API cost |
| [Machine/visual mismatch](../../../results/3d05/EXPERIMENT_CARD.md) | Full playback and discriminative scene controls | Target errors absent from positive case | ADOPT — measurements alone are insufficient |
| Sword grasp/ownership | No prop in this episode | Protected stationary/no-prop fixture | NOT_APPLICABLE — isolate reference timing |
| Better rig | Separate fixture admission before richer choreography | Admission report before later extension | DEFER — one variable at a time; screen can trigger it sooner |

## Process budget, provenance and handoff

Prospective forecast to refine before authorized execution: 15 net minutes design/fixture screen, 20 implementation/targeted checks, 10 preview/review preparation, 15 full suite/packaging; reassess at 20 net diagnostic minutes and 60 net minutes overall. At most three variants per hypothesis. Forecast actual render/storage growth from the chosen profile before dispatch; insufficient capacity stops dispatch. Human input waits are reconciled with continuing jobs; infrastructure delays stay in net time. Setup/tooling is a separate experiment episode. No paid engineering API calls; proposed evaluator budget is **$0 / zero calls**. A paid evaluator would need a separately frozen budget and existing provider ledger.

Policy hypothesis: Astra Medium for specified implementation/orchestration; High for initial unfamiliar constraint design or unresolved diagnosis; actual model/effort changes are recorded, never inferred or silently applied. Finish with an experiment card, learning transfer, ledger/usage report and compact reproducible evidence. Do not reopen 3D-05.

Execution briefing: use the admitted character and this spec, complete the manual reference board and fixture screen first, use `python -m movie_factory.experiment_ops` in `.venv` for lifecycle/jobs/reports, and stop if the fixture is unsuitable, the diagnostic budget expires without a new supported hypothesis, or required freeze inputs are missing. The user has now authorized this execution sequence.
