# Reproduction and bindings

The compact source snapshot and source-binding.json preserve the dirty worktree used for this milestone. The Git HEAD is a historical base, not a commit containing these repairs. The snapshot was captured after construction; earlier job provenance is therefore retrospective, with intermediate source copies and evidence retained. Do not claim every earlier worker was sealed at dispatch.

Use the repository .venv for outer Python and Blender 5.2.1 LTS (build 9e2066aef7ef). Assets remain local: see [asset manifest](../asset-manifest.json) for licenses and unresolved redistribution details. Do not redistribute the horse binary until its upstream attribution is resolved. No credentials or asset binaries are in source-snapshot.zip.

The fixed source fixture is `runs/demonstrator-01/realism-motion/scene.blend`, SHA-256 `37594a7ef2d59e5dcc9af42c332f28ab41e86e78f78a60e6bd5ff9e2a7ca961e`. The source-gallop build produces `runs/demonstrator-01/smooth-approach/scene.blend`; its SHA-256 is `46f9e2c15ad228cdf0136c6f9eaad20116f1c11f34d45d6e63f8a595e0ffd1a8`. The final integrated scene is identified by current-scene.json. Native job.json files record each fixed operation and profile.

## Offline inspection or replay

Open the final integrated scene with Blender auto-execution disabled. Frames 0–143 play at 24 fps. The path owns 12 m/s world travel; tail/dust are baked, deterministic authored effects. Camera `hero` includes dust; camera `contact` is the inspection view. Hide the `FX Contact Dust` collection for dust-free rendering. No provider calls or private environment are required.

For programmatic replay, use the existing `movie_factory.adapters.blender.runner.run_blender` through the operating-ledger job wrapper. The reviewed mode `demo_sustained_render` accepts only a view (`hero` or `contact`) and an integer half-open frame interval within [0,144). It verifies the scene path/hash from current-scene.json and renders numbered PNGs. Use a fresh output directory and unique operating job ID; never overwrite historical results. The runner launches Blender with --disable-autoexec and a sanitized environment.

`demo_sustained_check` uses an empty profile and the same receipt for the full-duration reopened mesh/contact scan. `demo_sustained_contact_control` performs a disposable +25% path-speed corruption alongside its positive control at off-grid times; it does not save the corrupted scene. The source build and FX modes are fixed fixture handlers, not arbitrary code execution endpoints.

The mode handlers currently embed this project's absolute base path. A different-machine reproduction requires adapting that path and staging the admitted source scene; this is not a portable general-purpose asset importer. Record that change.

Encode 144 numbered frames with ffmpeg at 24 fps, H.264/yuv420p and +faststart. The videos must report exactly six seconds and 144 frames. There is no duplicate endpoint and no claim of a seamless travelling loop. The HTML page has native controls and direct MP4 links as fallbacks.
