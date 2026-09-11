# Running 3D-03.1

Use the project virtual environment. These commands make no provider calls.

```bash
.venv/bin/mf3d qualify-character-031 \
  --staged .runtime/assets/3d-03/staged-v1 \
  --output runs/3d031 \
  --profile asset_preview

.venv/bin/mf3d validate-character-motion-031 \
  --run runs/3d031/<character-v2-run> \
  --output runs/3d031-motion

.venv/bin/mf3d replay-character \
  --run runs/3d031/<character-v2-run> \
  --output runs/3d031-replay/<replay-run>

.venv/bin/mf3d export-character-031 \
  --output exports/<new-3d031-bundle>
```

The first command checks construction, persistence, revision, protected state, and renders. The second renders and measures every animation frame and writes `review.html`. The third replays the frozen structured revision offline.

The original source-only limitation can be reproduced by running ordinary `qualify-character`, followed by `validate-character-motion-031`. That path should qualify idle/run and retain jump as `SOURCE_POSE_REFERENCE_ONLY`.

The export command verifies the compact evidence manifest and packages the exact execution source, final validation tooling, native scenes, full frame sequences, playback page, replay, diagnostic, and admitted source assets. The destination must not already exist.
