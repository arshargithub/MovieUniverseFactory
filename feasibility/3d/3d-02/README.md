# 3D-02 setup and execution

This experiment uses the project-local `.venv` and makes no model-provider calls.

Place the three original archives named in `assets.json` under `.runtime/assets/3d-02/source/`. Reproduce the admitted 20-file staging set:

```bash
.venv/bin/mf3d prepare-assets \
  --manifest feasibility/3d/3d-02/assets.json \
  --source .runtime/assets/3d-02/source \
  --output .runtime/assets/3d-02/staged-v2
```

Run the native qualification:

```bash
.venv/bin/mf3d qualify-assets \
  --staged .runtime/assets/3d-02/staged-v2 \
  --output runs/3d02 \
  --profile qualification_cpu
```

The command preserves the baseline and revised `.blend` files, fresh-process snapshots, three beauty renders and masks per stage, exact structural comparisons, a Director comparison page, cost record, and artifact manifests. The result stays YELLOW until Director review is recorded.

Replay a completed revision with no provider call:

```bash
.venv/bin/mf3d replay-assets \
  --run runs/3d02/<run-id> \
  --output replays/3d02/<run-id>
```
