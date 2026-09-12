# Reproduce 3D-06A

Use the repository `.venv` and local Blender. No API credentials are required or passed to Blender. The full native/image evidence remains under `runs/3d06a/`; this compact report directory is not a standalone asset bundle.

1. Check out frozen commit `177802c` in an isolated checkout and create its local `.venv`; install the project there using `.venv/bin/python -m pip install -e .`.
2. Restore `runs/3d06a/screen-20260911T222625Z-370528ef/scene.blend` and `fixture-screen.json` from the preserved local evidence. Verify their SHA-256 values against `feasibility/3d/3d-06a/campaign.json`. This packed native fixture avoids a fresh import or external asset lookup.
3. From a clean frozen checkout run `.venv/bin/python -m movie_factory.gesture_controller --stage qualification --screen runs/3d06a/screen-20260911T222625Z-370528ef`. The controller verifies source dependencies and input hashes and writes a unique run. On macOS Blender may require ordinary unsandboxed native execution. No arbitrary generated Python is admitted.
4. Expect positive metrics, five corrupted control scenes/results, six native checkpoints, exact candidate replay, and 384 PNG frames at 24 fps in two views. Native timeout is 900 seconds; faster/slower hardware does not change the gates.
5. Generate the convenience player using `movie_factory.gesture_controller.write_review(run, run)` with `pathlib.Path` arguments in the project environment. FFmpeg and ffprobe must be installed; both videos contain 96 unique frames and last four seconds. Review provenance binds every input image and output video. Player encoding is separate from the Blender qualification.

Verify the compact result manifest by hashing every listed relative path. The local run inventory binds native scenes and images separately. Reproducing numerical results does not reproduce a Director judgment: record a fresh full-clip review and its duration. The current review is pending.
