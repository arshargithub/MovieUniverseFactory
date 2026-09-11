# 3D-05 grasp repair — 2026-09-11

The Director rejected `interaction-v1-20260911T143452Z-281f2ecf`: the fist touched the handle instead of grasping it, and the result was as bad as or worse than the preceding attempt. The user requested Astra for the next engineering repair and run. This records that request, not a controlled comparison between Codex models. The experiment evaluator remains disabled.

## Demonstrated causes

The admitted rig contains RightHandIndex1–3 and RightHandThumb1–2. The preceding repair treated the hand as a fixed mitten, retained the curled idle finger pose, and repositioned the wrist. The original 1 m sword normalization produced a handle roughly 241 mm wide, which could not fit this hand. Stable bone-tail offsets therefore did not establish a grasp.

Read-only inspection of the preserved rejected scene with the new mesh measurement found approximately 58.3° contact coverage and 26.8 mm sampled hand penetration at the inspected grasp frame. Its previous anchor gate passed. The original scenes and Director records are preserved.

## Corrected fixture and motion

The original character mesh, rig, weights, materials, and source actions remain protected. The repair authors an open-to-closed motion with the rig's existing five thumb/finger controls. It changes the admitted scope from no finger articulation to one explicit scripted closure; it does not qualify general finger articulation or physical grasping.

The sword is an explicitly normalized variant of the same hashed source asset. Its handle is now approximately 23–29 mm across, while separate blade and guard normalization retains a recognizable sword silhouette and a 1 m overall length. These modifications are recorded in `scene.json` and the native root metadata. The source GLB is unchanged. This qualification cannot be described as grasping the former oversized handle.

The open hand first approaches a point in front of the handle, then advances palm-first. Its fingers close only once positioned. An outward thumb arc avoids the collision observed with direct quaternion interpolation. The final hand frame and grip location are frozen before scoring. Full numeric details are in `SPEC.md` and `scene.json`.

An additional subframe defect was identified by code inspection: sword location keys changed coordinate meaning at attachment but used linear interpolation while constraint influence used constant interpolation. Location now also uses constant interpolation. Off-grid probes as close as 0.001 frame to attachment must confirm that the supported sword stays stationary.

## Validation changes and development evidence

The new gates measure thumb contact, finger contact, angular enclosure, and hand penetration against evaluated sword surfaces for both clips. They supplement anchor tracking and Director playback review. Finite surface/time sampling is not an exact collision proof.

- Native regression suite: 2 passed, including all seven actual Blender controls, in `runs/3d05-development/astra-native-final`.
- The added open-hand and oversized-handle controls retain passing anchor translation/orientation gates but fail their designated mesh gates.
- Final native sampling: 455 times per clip; worst hand penetration approximately 3.18 mm baseline / 3.38 mm candidate against the 4 mm ceiling. Held contact coverage is approximately 188.08° against a 170° minimum; thumb and finger distances stay within approximately 2.42 mm and 2.96 mm against 5 mm limits.
- Full unrendered development campaign: `runs/3d05-development/astra-full-validation/interaction-v1-20260911T150701Z-13302c88`. Dense validation, all checkpoints, save/reopen, independent replay, and seven controls passed. Development binding is honestly marked dirty; only the subsequent scored run binds a clean source commit.
- Close previews: `runs/3d05-development/astra-grasp-final-preview`.
- Diagnostic source-fixture geometry and finger controls: `runs/3d05-development/astra-grip-diagnostic-v2`.
- Rejected-scene sensitivity check: `runs/3d05-development/astra-rejected-run-control`.
- Intermediate fitting previews, collisions, and failed native attempts remain under `runs/3d05-development/astra-*`.

The subsequent scored run must repeat the full checks on the frozen source, render complete playback, and obtain explicit Director acceptance. Engineering success does not override a visual rejection. Provider calls and API cost remain zero; human review time must be supplied for the new run.
