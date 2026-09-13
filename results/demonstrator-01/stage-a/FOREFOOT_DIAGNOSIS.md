# Forefoot diagnosis — bounded follow-up

**Diagnosis complete; full-pace gait remains YELLOW / unqualified.** The user authorized up to 20 minutes of diagnosis, with no fourth authored gait variant. Two fixed native jobs measured the unchanged, hash-bound third candidate and disposable single-pose controls. No animation keys or native scenes were saved; no paid model calls or rendering occurred.

## Correction to the previous interpretation

The 12.1% “shortening” is relative to a stretched source pose, not the rig rest length. Right forefoot rest length is 0.198119 armature units. Candidate lengths remain 0.198044–0.198127 (within approximately 0.04% of rest), whereas source lengths span 0.197834–0.225424, reaching 13.8% above rest. The two deform segments use COPY_TRANSFORMS and STRETCH_TO constraints. Disabling IK stretch does not disable those separate deform constraints.

Consequently, the frozen same-frame source comparison is a real measured failure but an insufficient anatomical diagnosis. Different contact timing makes same-frame source stretch a poor sole target for this newly authored gait. **No threshold has been changed, and this finding does not promote the candidate to a pass.** Original results are preserved.

## Actual mesh and articulation evidence

Both source and candidate were inspected at 81 samples across the ten-frame cycle. Evaluated topology remained stable and sampled coordinates were finite. In the right forearm/forefoot/hoof weighted region, 1,869 of 8,535 edges and 2,323 of 8,461 triangles leave their individual source-cycle ranges by more than 5% at some time. The most compressed edge falls to about 11.4% of its source-cycle minimum; one triangle falls to about 1.88% of its source-cycle minimum. These are local geometry diagnostics, not universal aesthetic or anatomical gates; tiny features and bending can strongly affect ratios.

The upper-arm/forearm direction angle reaches 129.75 degrees in the candidate versus 82.70 degrees in the source cycle. Forearm/forefoot angle reaches 129.37 versus 108.70 degrees. These are angles between named bone directions, not clinical joint angles. The candidate therefore exercises substantially different articulation and skin deformation, even while segment lengths remain near rest. [Mesh projection](../../../runs/demonstrator-01/forefoot-diagnosis/mesh-comparison.png) shows weighted-region geometry only; omitted vertices cause apparent gaps and each panel is independently centered/scaled. It is not a production render or evidence of a disconnected hoof.

## Isolation controls

At frames 1.875, 3.25 and 3.875, restore source local foot and heel matrices separately and together in disposable evaluated poses. Keep the authored root and other legs. Re-evaluate the same candidate afterward to prove reset; all three reset results match exactly. These interventions are not usable new gait variants: their contacts and motion have not been qualified.

At frame 3.25:

| Control | Edges outside source envelope by >5% | Triangles outside by >5% | Worst triangle envelope factor |
|---|---:|---:|---:|
| Unchanged candidate | 387 | 246 | 53.17 |
| Restore source foot only | 11 | 3 | 1.42 |
| Restore source heel only | 383 | 291 | 22.54 |
| Restore both | 0 | 0 | 1.026 |
| Reset candidate | 387 | 246 | 53.17 |

Restoring both also reduces excursions at the other two frames, but does not remove all of them. This localizes a major contribution to the authored foot transform and its interaction with the heel/limb mechanism. It does **not** yet distinguish foot translation from orientation, prove a skin-weight defect, or establish the rig's maximum natural gallop speed. The earlier plan to adjust only the heel is inadequate.

## Concrete repair contract for the next authorized pass

1. Preserve current head, cameras, original assets and all failed evidence. No rig rebuild is justified by these findings.
2. Solve the foot target, heel and full limb articulation together. Use source whole-limb poses as the reference; bound bend and orientation while satisfying the ground-stationary stance. Do not force the current high swing path independently of reachability.
3. First prove a pose-level correction at the three diagnostic frames, separating translation and orientation effects. Inspect the weighted mesh and support error. Only then bake one new complete candidate; do not spend the next budget on successive heel-only guesses.
4. Before scoring, explicitly correct and freeze the deformation contract: distinguish rest-length preservation, phase-aware articulation and evaluated mesh quality. Retain the historical same-frame failure; do not just increase its ceiling. Qualify the measurement using source controls and a deliberate mesh-deformation failure. No replacement numerical acceptance contract was adopted in this diagnosis.
5. Validate full-cycle fractional samples, actual ground contact, target error, persistence and replay. Only after these pass, integrate the existing drafted tail/dust into one inexpensive preview plus dust-free contact view. Effects and full-pace appearance remain NOT_RUN.

Proposed next budget: 20 minutes for the pose-level correction and contract, with a checkpoint before a new full gait or effects render. No fourth gait, extra API spend or full-film production was dispatched here.

## Cost and durability

Native elapsed time: 14.429 + 16.459 = **30.888 seconds**. Nine existing pure-math tests pass; Python syntax checks pass. Repeated measurement reproduces the prior clean-reference result exactly, and all isolation resets reproduce their candidate metrics exactly. This is not a rerun of the whole campaign suite.

New API charges: **$0**; campaign calculated cost remains $2.550887501. Exact subscription tokens remain unknown. Recorded activity duration is captured in the operating ledger and compact summary. Historical reports and inventories remain intact. The diagnostic source snapshot and checksummed inventory bind this addendum without rebuilding any large archive.

[Raw measurements](../../../runs/demonstrator-01/forefoot-isolation/diagnosis.json) · [Isolation controls](../../../runs/demonstrator-01/forefoot-isolation/single-pose-controls.json) · [Inventory](forefoot-diagnosis-manifest.json)
