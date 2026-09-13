# Reproduce the 24-second rough cut

This is the development cut of *The Courier*, not a newly scored qualification campaign. Preserve the historical previews and their rejected outcomes. The final film uses 576 unique timeline positions, frames 0–575 at 24 fps; frame 576 is a validation endpoint and is not appended to playback.

Use the project `.venv` for all outer Python. Blender is `/Applications/Blender.app/Contents/MacOS/Blender`, verified as 5.2.1 LTS. Native jobs use the existing runner and script-disabled worker; never execute an asset's embedded scripts. No API key is needed to reopen or render this cut. Do not pass `.env` values to Blender.

## Bindings and local assets

`FROZEN_CUT.json` binds the implementation files, motion base, final scene, and frame ranges. `final-reopen.json` records actual saved rendering settings: Eevee, 32 samples, 960×540, 24 fps. `frame-inventory.json` binds every rendered source image to the final scene receipt. The final source commit is recorded separately in `SOURCE_BINDING.json`; the pre-render dirty-tree digest is the contemporaneous source binding.

The native scene is `runs/demonstrator-01/cut-world-v4/scene.blend`. It is compressed and contains the shared world, horse/rider actions, cameras, original procedural scenery, tail and dust. The validated motion base is `runs/demonstrator-01/cut-motion/scene.blend`. The initial source fixture is `runs/demonstrator-01/realism-motion/scene.blend`; its SHA is retained in the motion receipt. These paths are fixed by the reviewed handlers. Restore local files at their documented paths; do not silently substitute another horse or rig.

The horse derives from fdoss001's BlendSwap “Horse Rigged All Gaits” listing, with upstream mesh credit to Tarnyloo. The listing says CC0, while the upstream mesh is recorded as CC-BY with version unresolved. The knight is crownjoshua's CC0 “Knight Rigged Mid Poly” from OpenGameArt. See `../stage-a/asset-manifest.json` for original acquisition URLs and hashes; that historical candidate record is not rewritten. The current run uses the admitted, modified local fixtures. Raw assets/native scenes remain local and were not included in the GitHub push. No new asset license or redistribution right is inferred here.

## Offline verification and replay

From the repository root:

```sh
.venv/bin/pytest tests/unit/test_cut_boundary.py tests/unit/test_cut_phase.py tests/unit/test_source_gallop_phase.py tests/unit/test_demonstrator_budget.py tests/unit/test_demo_asset_boundary.py tests/unit/test_demo_contact.py tests/unit/test_demo_realism_boundary.py -q
```

Run a fixed native operation with the existing runner, choosing a **new** output directory under `runs/demonstrator-01`. For example:

```python
from movie_factory.adapters.blender.runner import run_blender
result = run_blender(
    {"mode": "demo_cut_render",
     "output_dir": "/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01/cut-replay-new",
     "profile": {"shot": "shot2", "start": 220, "end": 221}},
    blender_bin="/Applications/Blender.app/Contents/MacOS/Blender",
    timeout=180,
)
assert result["ok"], result
```

Use `.venv/bin/python` and the operating-ledger job wrapper for that invocation. The render handler checks the final scene SHA before loading and refuses to continue below a 5 GiB disk reserve. It produces `frame_0220.png`, a per-frame timing record, `render.json`, worker/runner status and logs. Compare the image with frame 220's inventory entry; `replay.json` records the actual independent reproduction result from this pass.

Other fixed modes are `demo_cut_check` (full motion contact/finite/rein screen), `demo_cut_contact_control` (real path-speed corruption measured off-grid), and `demo_cut_final_check` (base/final protected geometry comparison around key moments, including fractional frames). They accept only an empty profile. Expected numerical results are in `motion-validation.json`, `contact-control.json` and `final-reopen.json`. The old changing-centroid diagnostic remains a failure; fixed material points are the accepted contact screen for this development pass.

## Assembly and playback

`render_cut.py` documents the bounded single-worker production batches (the initial two-worker attempt hit the storage guard). It refuses to overwrite existing output blocks. Reconcile completed blocks before any resume; the saved cut does not require repeating the motion build. `assemble_cut.py` admits only frame blocks matching the final scene SHA, adds the two preflight endpoint images, verifies all 576 PNG dimensions, and links them into `cut-review/frames` without copying their payloads. It then uses local FFmpeg to make `the-courier-24s.mp4`, checks duration/frame count/audio, and writes the inventory.

`create_audio.py` makes deterministic original provisional wind, hoofbeats at recorded contact times, and a quiet signal bell. It uses no downloaded sound or provider generation. Sound is provisional and Director acceptance remains pending.

Open `runs/demonstrator-01/cut-review/review.html` or the MP4. The player uses no network fetch and embeds no credentials. Manual stepping loads original numbered PNGs and updates the label only after loading; video labels use presented-frame callbacks where available. `review-template.html` preserves the player source. Relative symlinks in the frame directory require preserving the surrounding run folders, or explicitly materializing copies when preparing a separately authorized portable archive.

No large archive was rebuilt. Native scenes and source frames are local-only until separately backed up. The earlier authorized source push is recorded in `PREFLIGHT.md`; it predates the newly rendered cut.

The superseded first world scene is losslessly stored as `runs/demonstrator-01/cut-world/scene.blend.gz`. `storage-preservation.json` records a verified decompression hash matching its original scene receipt. Restore it with Python gzip or gunzip only if inspecting that superseded version; the final v4 scene remains directly usable.

The validated motion base is also losslessly archived as `cut-motion/scene.blend.gz`. To rerun contact/base-versus-final validation, first restore its original bytes to `cut-motion/scene.blend` with `.venv` Python's `gzip` and `shutil.copyfileobj`, and verify SHA-256 against `motion-receipt.json`. Allow approximately 758 MiB extra storage plus the native worker's memory/swap footprint. Rendering the saved final v4 scene does not require restoring either intermediate archive.
