# 3D-03 setup

This experiment uses the project `.venv` and makes no model-provider calls.

Place the official archive named in `assets.json` under `.runtime/assets/3d-03/source/`, then run:

```bash
.venv/bin/mf3d prepare-assets \
  --manifest feasibility/3d/3d-03/assets.json \
  --source .runtime/assets/3d-03/source \
  --output .runtime/assets/3d-03/staged-v1
```

Probe the admitted model and clips:

```bash
.venv/bin/mf3d probe-character-assets \
  --staged .runtime/assets/3d-03/staged-v1 \
  --output runs/3d03-probes
```

Run the qualification and provider-free replay:

```bash
.venv/bin/mf3d qualify-character \
  --staged .runtime/assets/3d-03/staged-v1 \
  --output runs/3d03 \
  --profile qualification_cpu

.venv/bin/mf3d replay-character \
  --run runs/3d03/<run-id> \
  --output replays/3d03/<run-id>
```
