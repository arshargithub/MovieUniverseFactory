# Reproducing 3D-02

This guide reproduces the frozen external-asset qualification without provider calls. Use the repository's project-local `.venv`; never install the Python dependencies globally and never copy `.env` into an evidence bundle.

## Prerequisites

- The Blender build recorded by the bundle verification metadata. The tested macOS executable is `/Applications/Blender.app/Contents/MacOS/Blender`.
- The repository source and `requirements.lock` included in the evidence bundle.
- The three original CC0 archives named and hashed in `feasibility/3d/3d-02/assets.json`.

## Install and verify

Create the local environment using `SETUP_README.md`, then run:

```bash
.venv/bin/python -m pytest
```

Place the three original archives under `.runtime/assets/3d-02/source/` and reproduce the admitted staging set:

```bash
.venv/bin/mf3d prepare-assets \
  --manifest feasibility/3d/3d-02/assets.json \
  --source .runtime/assets/3d-02/source \
  --output .runtime/assets/3d-02/staged-v2
```

The command must verify the recorded archive and member hashes before Blender receives any path.

## Fresh qualification

```bash
.venv/bin/mf3d qualify-assets \
  --staged .runtime/assets/3d-02/staged-v2 \
  --output runs/3d02 \
  --profile qualification_cpu
```

Expected outputs include baseline and revised `.blend` files, fresh-process snapshots, three beauty renders and masks per stage, structural comparisons, the immutable work package, costs, and artifact manifests. A fresh run remains YELLOW until its own Director comparison is reviewed; the historical acceptance must not be copied onto a new run.

## Offline replay

For the sealed run `asset-set-v1-20260910T034104Z-cffdd816`:

```bash
.venv/bin/mf3d replay-assets \
  --run runs/3d02/asset-set-v1-20260910T034104Z-cffdd816 \
  --output replays/3d02/asset-set-v1-20260910T034104Z-cffdd816
```

The replay is expected to make zero provider calls, reproduce the revision from its sealed executable package, and report no semantic differences. Verify native-file hashes, manifests, and source/evidence bindings rather than expecting cross-machine pixel equality from Blender.

## Provenance boundary

`results/3d02/source-binding.json` binds the live qualification to implementation commit `40f604e812cc2773ad0222e44c823eba354fd066` and tree `153726123a13547c775483183895e56821808f8d`. The tag `3d-02-v1-green` identifies that implementation. A later `3d-02-v1-green-evidence` tag identifies the final documentation and bundle state; the two tags intentionally have different meanings.
