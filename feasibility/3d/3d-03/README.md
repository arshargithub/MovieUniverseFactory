# 3D-03 setup

The original qualification uses the project `.venv` and makes no model-provider calls. Implementation, debugging, and deterministic validation stay local. The temporal closure addendum permits one optional, budgeted API call only as a frozen experiment-evaluation stage after every deterministic check passes.

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

Run the temporal closure addendum against the frozen accepted native scene:

```bash
.venv/bin/mf3d validate-character-motion \
  --run runs/3d03/character-v1-20260910T201716Z-dd48f85a \
  --output runs/3d03-temporal
```

The addendum renders every frame of idle, run, and jump and measures evaluated mesh bounds, foot clearance, limb lengths, and frame continuity. A deterministic failure makes the API stage ineligible and records zero calls. Once a frozen source passes locally, repeat the exact command with `--live` to send the three complete contact sheets to one ledger-controlled experiment evaluator. The API can flag or veto evidence; it cannot override a deterministic failure or replace Director review of complete playback.
