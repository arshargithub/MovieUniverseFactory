# Coordinated lift prototype — development result

Status: **Director accepted the complete development preview with a 0.5-point deduction for sword–head proximity. Technical diagnostic remains RED.** The complete-clip elbow skin probe still fails during the preserved reach. No new GREEN claim, scored campaign, or Sol handoff is made. Earlier scored inputs and evidence remain unchanged.

Run: `interaction-v1-20260911T165641Z-6f92e608`, under `runs/3d05-development/coordinated-validation/`. [Local playback](../../../../runs/3d05-development/coordinated-validation/interaction-v1-20260911T165641Z-6f92e608/motion-playback/index.html) contains the complete candidate performance in three synchronized views: 96 frames each at 24 fps, 640×360, four render samples. Press Play; playback stops at the hold instead of jumping back to the supported pose. This is a labelled development preview, not the earlier anonymous timing test. The visible-page timer is a review-time proxy, not proof of attention. The Director explicitly passed this playback, noting that the sword almost seems to touch the forehead at maximum elevation. This is a proximity observation, not independently confirmed collision. The 0.5-point deduction is recorded without inventing an absolute total or per-dimension scores. Review duration remains unknown. See `director-prototype-review.json` in the run directory.

## Design and observations

The [authored pose board](POSE_BOARD.md) preceded implementation. No external human reference clip was reviewed. The hold was brought closer to permit elbow flexion; the hand pitches upward and the sword follows its complete rigid transform. Head orientation turns toward the sword before the reach and follows the lift. Torso and lower body remain deliberately still; this does not qualify eye gaze, physical weight or general human animation.

| Evaluated probe | Result |
|---|---:|
| Forearm pitch gain through lift | 49.09° |
| Hand pitch gain through lift | 25.00° |
| Peak elbow flexion gain | 20.90° |
| Held elbow flexion | 69.54° |
| Minimum head-attention angular improvement after preparation | 34.30° |
| Maximum elbow edge-length ratio during lift | 1.209× |
| Maximum elbow edge-length ratio over complete clip | **1.821× at source frame 20.25** |

The original new whole-clip skin ceiling remains **1.50×**. Both timing variants fail that check during the earlier reach. This is an admitted-fixture probe using 26 elbow-region mesh edges relative to the evaluated initial idle pose, not a universal biological strain limit. It identifies an unresolved deformation concern; it does not itself establish how conspicuous it is in playback. Do not relax it merely to obtain a pass. The source frame of the peak is shared by the variants before the bounded timing edit.

The first retained probe, `coordinated-lift-v1`, kept the old distant hold and ended with an almost straight elbow (~18°). Probe v2 moved the hold closer. Probe v3 added measured elbow skin and attention diagnostics and exposed the reach-stage failure. Their native scenes, metrics, selected previews, input snapshots and copies of the interaction implementation remain under `runs/3d05-development/`. They are development evidence, not scored retries or accepted outcomes.

## Validation and bindings

Native scenes and original measurements bind to source commit `7492fac8605cf84429935eb42c0b9625a4ffbd8e`, with a clean tree before dispatch. Native scene SHA-256: `5908480144c0b2efdc9bcc48d0b385ef9e95f01c4c9f17867d579b7053b95105`.

The additive validator and convenience player bind to commit `95df2804428381d962c196985487712990df013f`. `validation-addendum.json` preserves the original result and full-clip failure, adds a lift-window skin check at the same limits, and requires a control's expected failure to be absent from the positive case. This prevents an already failing reach probe from giving false credit for detecting a deliberately distorted elbow. Raw Blender measurements were revalidated without modifying scenes or numerical thresholds.

- 88 of 90 additive positive checks pass; only the two full-clip elbow skin checks fail.
- All 15 actual Blender corruptions trigger their distinct expected failures, including rigid lift, wrist-only compensation, relative prop rotation, elbow skin distortion and missing attention. These are measured scene/action variants, not fabricated measured values.
- Six state checkpoints, save/reopen, exact semantic replay and numerical replay pass.
- Source actions, identity, topology, weights, rest rig, materials, lights and world are preserved; the timing variants match outside `[28,76]` within the existing numerical tolerances.
- The normal offline suite passes: **129 passed, 11 deselected**. Native evidence comes from the separate complete prototype execution; the deselected tests are not claimed as run.
- Browser inspection confirmed all 288 frames decoded and the player reached Ready. The Director subsequently accepted full motion with the clearance deduction noted above.

The original `artifact-manifest.json` remains untouched. `prototype-artifact-manifest.json` now inventories 697 artifacts, including full playback, additive validation, Director acceptance and preserved review history. The prior 694-artifact inventory remains preserved. Compact copies of results, bindings, validation and inventory are committed under `docs/engineering-intelligence/evidence/interaction-v1-20260911T165641Z-6f92e608/`. Full native scenes and images remain local, inventoried development evidence; no authoritative GREEN export is claimed.

Known experiment API usage: **0 calls, $0**. Measured validation/control elapsed time was 215.42 seconds and preview rendering 68.36 seconds (283.78 seconds combined). This excludes earlier pose probes, engineering time, browser checks and future human review. Engineering tokens/cost and Director time are unknown, not zero.

## Reproduction

Use the project `.venv`, the installed Blender build, and the same staged character/sword prerequisites as 3D-05. Never expose `.env` to Blender. The opt-in inputs are in `feasibility/3d/3d-05/prototypes/coordinated-lift/`; their campaign hash is checked by the controller. They retain the exact admitted baseline and sword asset hashes. The original default scored inputs remain in their original directory.

From the repository root:

```bash
.venv/bin/mf3d run-interaction-05 --configuration feasibility/3d/3d-05/prototypes/coordinated-lift --output runs/3d05-development/reproduced --no-render
```

A nonzero qualification exit is expected while the whole-clip skin probe fails. Inspect the newly created run directory, including persistence and actual controls. The current source includes the additive validator; to audit the original measurements, inspect the source commit above separately and preserve the original run.

To create the same inexpensive complete preview for a newly produced native scene, use the trusted worker from the project interpreter, substituting the new absolute run path:

```python
from pathlib import Path
from movie_factory.adapters.blender.runner import run_blender
run = Path('/absolute/path/to/new/run')
result = run_blender({
    'mode': 'interaction_preview', 'parent_native': str(run/'build/scene.blend'),
    'output_dir': str(run/'motion-playback'), 'frames': list(range(1,97)), 'seed':305,
    'profile': {'name':'coordinated_motion_prototype','width':640,'height':360,
                'samples':4,'device':'CPU','shots':['shot_A']},
}, blender_bin='/Applications/Blender.app/Contents/MacOS/Blender', timeout=1200)
assert result['ok'], result.get('error')
```

Then run `.venv/bin/python tools/interaction_motion_player.py /absolute/path/to/new/run`. It refuses to overwrite a player or accept missing frames. Open the resulting HTML, or serve only its `motion-playback` directory using `.venv/bin/python -m http.server 8766 --bind 127.0.0.1 --directory /absolute/path/to/new/run/motion-playback`.

Next decision: retain the accepted motion design, assess the sword–head staging concern, and diagnose the reach-stage skin finding before another scored freeze. Preserve the failure if it reflects an admitted-rig limitation; any justified contract change requires explicit rationale and a new freeze. Do not turn Director approval of the lift into retrospective approval of the failed full-clip probe.
