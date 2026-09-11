# 3D-03.1 — Astra diagnosis and Sol implementation handoff

Status: **DIAGNOSIS PROVEN; STOP HERE FOR SWITCH TO SOL.**

This is a diagnostic experiment, not a new GREEN qualification. The aggregate 3D-03 result stays YELLOW. No paid provider calls were made. Production animation transfer, the evaluator model, the old thresholds, historical results, tags, and exports have not been changed by this diagnostic pass. The only worker dispatch addition is the fixed `character_bake_diagnostic` mode; its implementation lives separately in `character_diagnostic.py`.

## Proven first corruption point

The first observed corruption occurs **when assigning desired target pose matrices, before inserting target keyframes**. `import_character_action` assigns the whole bone chain with `bone.matrix = desired[name]`, then calls `view_layer.update()` once. Child local transforms are calculated using cached parent poses. Those parent poses belong to the preceding evaluation state, rather than the desired parent poses at the current sample.

This creates large errors in the initial frames and a false appearance of settling over later frames. Replacing the source animation, damping its rotations, changing rest-pose multiplication order, or paying a visual evaluator does not address this defect.

The controlled diagnostic uses the same verified source FBXs and captures source pose matrices before experimenting with target assignment. It compares six variants on identical samples: legacy forward bake, legacy reverse bake, legacy reset-to-rest per frame, per-parent evaluation updates, explicit parent-matrix conversion forward, and explicit conversion reverse. Each variant has a fresh target action and reset canonical pose. All source files pass the existing hash-checked importer.

Evidence from `runs/3d031-diagnostic/parent-evaluation-v4/diagnostic.json`:

- Source evaluation forward versus reverse: maximum matrix-component difference **0**, for all three clips. Source endpoints also match exactly.
- Legacy target assignment: maximum matrix-component errors **2.2804 idle, 2.9673 run, 3.2088 jump**. These are matrix errors, measured before scale/translation removal and key insertion; they are not distances in metres.
- Explicit conversion using current desired parent matrices: maximum assignment error **below 0.000008**, for every clip.
- Updating Blender immediately after each parent assignment is an independent control. It agrees with explicit conversion to **within 0.0000021 source units RMS** on evaluated mesh vertices.
- Explicit forward and reverse baking produce **identical evaluated meshes** at every sampled frame.
- The stored key values equal the values supplied at bake time; replaying completed actions forward or reverse gives identical meshes. This storage/replay is faithfully preserving already-corrupted legacy poses.
- Legacy reset-to-rest is smooth but wrong: its large assignment error persists. A smooth loop alone does not prove faithful pose transfer.
- Legacy baking introduces negative adjacent quaternion dot products; the explicit prototype has none at these integer samples. Sign continuity must nevertheless be enforced and tested at fractional times in production.
- A second independent Blender process reproduced the complete diagnostic report exactly. `execution-binding.json` and `execution-source/` capture the actual probe/worker/runner/launcher files before dispatch. This is file-level diagnostic provenance on a working tree, not a claim that a new implementation commit was sealed.

The explicit conversion uses Blender's `Bone.convert_local_to_pose(..., invert=True)` with the intended parent pose and parent rest matrix supplied. This API permits conversion without relying on a previously evaluated parent. The per-parent update control validates the mathematical result through the dependency graph. See [Blender's API documentation and hierarchy example](https://docs.blender.org/api/5.3/bpy.types.Bone.html).

## Full-frame visual and numeric proof

For the disposable diagnostic preview, only existing rotation and grounding channel values were replaced in a copy of the exact sealed scene. The mesh, weights, canonical rest skeleton, camera, lights, scale, and material came from that scene. No synthetic jump arc, rotation damping, resampling, or threshold relaxation was applied.

| Clip | Old peak mesh RMS step (m) | Diagnostic peak RMS step (m) | Diagnostic endpoint RMS (m) |
|---|---:|---:|---:|
| Idle | 0.348202 | 0.002631 | 0 |
| Run | 0.637168 | 0.160944 | 0 |
| Jump | 0.479453 | 0.001247 | 0 |

All 63 frames were rendered and measured. The old unmodified validator now reports only **`jump.airborne_phase`** failing. The opening contortions disappear from the idle/run sheets, and run alternates leg poses. Jump becomes a stable crouched pose with very small motion. This establishes the bake correction, not production-quality performance or Director acceptance.

The old 0.18 m RMS and 0.45 m maximum step limits were kept unchanged for this comparison. Geometry metrics in `diagnostic.json` are in source units; the table above uses the separately rendered scene's world-metre metrics in `old-contract-check.json`. Do not mix these measurements.

## Separate timing and root-motion findings

Blender imports **idle at 30 fps (33 samples; endpoint interval 32/30 = 1.0667 s)** and **run at 24 fps (17 samples; 16/24 = 0.6667 s)** and **jump at 24 fps (13 samples; 12/24 = 0.5 s)**. The existing final imported clip changes scene FPS. The previous review page displays every clip at 12 fps, further slowing playback. A frame index does not define a shared physical time across these clips.

The admitted jump evaluates as a held pose with slight movement. Its evaluated `HipsCtrl` is static, and foot-head movement is below 0.000004 source units over the clip. This is evidence about the imported FBX representation, not proof of the original author's intended jump semantics. A source root trajectory is absent in that representation. The sealed worker's per-frame grounding independently suppresses any airborne clearance that might otherwise survive. Adding the leftover 0.32 m synthetic sine arc in current `build_character` would be authored choreography, not faithful source-motion transfer. It must be removed from the faithful-transfer path or moved into a separately specified authored-motion experiment.


**Sol should first repair and qualify idle/run transfer using this character.** For jump, retain the existing-file identity and qualify only the supplied pose loop until a complete same-rig jump fixture with an observed trajectory and takeoff/landing is admitted. Do not claim full-jump qualification by renaming the pose loop or relaxing the airborne gate. No wholesale asset replacement is warranted by the present evidence.

## Production implementation design for Sol

1. **Keep capture, transform solving, and key writing as separate phases.** Capture verified source matrices (including object-world transforms and controller/root motion) at explicit physical timestamps with source FPS recorded. Use copies of matrices, not Blender references that mutate across evaluation updates. Freeze and hash the sampled representation.
2. **Solve target basis transforms using explicit current-frame parent matrices in hierarchy order.** Preserve the existing legacy desired armature-space rotations in this bounded exact-skeleton case. For each weighted bone, call `convert_local_to_pose(desired_pose, canonical_rest, parent_matrix=current_parent_pose, parent_matrix_local=canonical_parent_rest, invert=True)`. Solve unweighted ancestors too, including `HipsCtrl`, from their frozen basis and current parent matrix. Do not invent alternate rest-offset transforms or copy clip-specific deform scale/translation channels.
3. **Preserve canonical lengths and connections deliberately.** Extract rotations from the solved bases and set only those rotations on weighted bones, with zero local displacement and unit local scale under the existing bounded contract. Use `convert_local_to_pose` forward to calculate the actual normalized parent pose for children when enforcing these constraints; verify the intended rotational agreement rather than assuming discarded translations have no effect. Test against the slow update-after-each-parent control.
4. **Canonicalize quaternion signs across ordered times before writing keys.** Write the complete action after solving all samples, bind the correct action slot explicitly, and validate channels again after reopening. Sample fractional times to catch quaternion interpolation flips beyond integer endpoints.
5. **Separate source root trajectory from placement.** Record retained/discarded source axes and define an explicit root-motion policy per clip. Use one static placement transform for faithful vertical-motion transfer. Per-frame floor snapping is not suitable for an airborne trajectory. 3D-03.1 must report any intentionally normalized motion separately from source fidelity. A supplied pose loop remains a pose loop; an authored takeoff/landing is a separate configuration.
6. **Make timing explicit.** Choose and freeze a common output FPS and resample by physical time using the original per-clip rates. Retain the original samples as the reference; test interpolated target poses at corresponding source times. Do not let the last imported FBX silently choose the scene playback rate. Endpoint duplicate loop frames should not introduce an extra held tick in playback.
7. **Strengthen validation without erasing old failures.** Require all expected limb names, finite numeric fields checked independently of the worker's boolean `finite`, consistent timestamps and topology, and exact frame coverage. Measure displacement plus velocity per second at recorded delta-time. Use source-relative transfer residuals and meaningful motion controls to distinguish corruption from legitimate fast movement. Freeze speed/continuity ceilings before the new scored run; retain the old metre-per-frame results for comparison. Do not raise thresholds merely to pass this prototype.
8. **Define per-clip semantics.** Idle/run are loops; endpoints and seam velocity need checks. Jump requires takeoff, contiguous airborne interval, and landing only when the fixture supplies a full jump; loop-seam checks apply only to clips declared to loop. The current verified as-imported endpoints coincide, but that does not prove full-jump semantics. The current run validator currently calls counts of each foot's contact “alternating”; it does not actually test alternation. Make that truthful and add support/foot-sliding checks under the declared in-place/world-motion policy. A rig's constant bone lengths are not sufficient evidence of healthy mesh deformation.
9. **Requalify the implementation, not just this preview.** Add native regressions for forward/reverse/isolated sampling, two-pass baking, fractional times, render-order independence, and bake→save→reopen equality. Include negative controls for stale-parent assignment, missing limbs, bad timestamps, root snapping, and both-feet-always-contact. Repeat mesh/weight/rest-rig/identity persistence, protected-state revision, and provider-free offline replay checks. Rerender complete clips with feet visible and obtain Director full-clip acceptance before any GREEN claim.
10. **Keep experiment costs and authority fixed.** Routine coding and diagnostics use Codex. Paid API calls remain restricted to explicitly frozen experiment evaluation with the persistent budget ledger; the diagnostic correction does not require one. Keep the existing configured evaluator unchanged unless a separately justified experiment changes it. The reviewer cannot override deterministic failure or replace Director playback review.

## Reproducibility and retained artifacts

Run from the repository root with the project environment:

```bash
.venv/bin/python feasibility/3d/3d-03-1/run-diagnostic.py \
  --output runs/3d031-diagnostic/sol-reproduction-01
```

Blender executes the fixed `character_bake_diagnostic` operation through the trusted worker and sanitized environment. The launcher reads the accepted build's plan, which already contains absolute admitted paths; original FBX hashes and the sealed `.blend` hash are checked by the worker. It writes only to a new diagnostic run directory. No provider is constructed.

The full diagnostic workspace is `runs/3d031-diagnostic/parent-evaluation-v4/`; compact evidence is in `results/3d031-diagnostic/`. V1 records a rejected dispatch with relative asset paths; v2 is the numeric probe, v3 adds disposable visual playback, and v4 repeats v3 with source files captured before dispatch. All attempts remain preserved. The unmodified 3D-03 sealed native hash is `1fbb2535aedc3a25227c87ff3d778e8b2d77efb9e620d30e4eef7e635f5c16bb`.

## Boundary for the model switch

Astra's diagnosis, causal proof, local prototype, and validation-contract review are complete. **Switch to Sol now for the production correction, test integration, and later packaging.** No production bake correction or new qualification should be inferred from this diagnostic preview. The existing 3D-03 YELLOW decision stands until the revised claim is actually qualified.
