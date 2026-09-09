# Movie Universe Factory — 3D feasibility harness

This repository implements **3D-01: Persistent Scene + Targeted Revision**, a measured Blender-first feasibility experiment. It builds a small apartment scene with persistent semantic identities, renders three shots, moves the coffee table 40 cm toward the sofa, changes a red motorcycle helmet to dark green, and verifies that protected scene state did not change.

The authoritative design is [MOVIE_FACTORY_3D_FEASIBILITY_SPEC.md](MOVIE_FACTORY_3D_FEASIBILITY_SPEC.md). [SETUP_README.md](SETUP_README.md) explains local setup and the review workflow.

## Local environment

All outer Python dependencies live in `.venv` inside this project. Blender uses its own bundled Python and receives no API or GitHub credentials.

```sh
source .venv/bin/activate
mf3d doctor --engine blender --output results/doctor.json
mf3d validate-spec --experiment feasibility/3d/3d-01
mf3d run --experiment feasibility/3d/3d-01 --provider mock --profile smoke
```

The live qualification command invokes the OpenAI API and is budget-capped by the campaign and persistent ledger. Run deterministic tests and Blender integration first:

```sh
.venv/bin/python -m pytest
MF_NATIVE_TEST=1 .venv/bin/python -m pytest -m blender
```

The completed five-pair campaign report is
[`results/3d01-20260908T200952Z/REPORT.md`](results/3d01-20260908T200952Z/REPORT.md).
Machine qualification is 5/5 and Director review accepted all five pairs at
4.8/5. Final disposition remains YELLOW because revision API economics are above
the GREEN ceiling.

Routine generated runs and large artifacts are excluded from Git. Small reports under `results/` describe what actually ran; a mock or incomplete campaign is never reported as a qualified result.
