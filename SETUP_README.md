# Movie Factory 3D — setup and Codex handoff

Start with [the full feasibility specification](MOVIE_FACTORY_3D_FEASIBILITY_SPEC.md). The Blender-first harness is implemented in this repository, its dependencies are installed only in the project-local `.venv`, and its offline readiness evidence is in [results/OFFLINE_READINESS.md](results/OFFLINE_READINESS.md). The explicitly authorized five-pair live qualification completed 5/5 machine-valid pairs and Director review accepted all five at 4.8/5; its report is [results/3d01-20260908T200952Z/REPORT.md](results/3d01-20260908T200952Z/REPORT.md). The disposition remains YELLOW because revision API economics exceed the GREEN ceiling.

## What you need first

- **Codex**, signed in through your existing account.
- **A writable local project folder and Git.** GitHub is optional. Existing GitHub CLI sign-in or SSH can handle remote access; a new GitHub token is not automatically required.
- **Blender** installed on the Mac that will execute the experiment. Use an official build; Apple Silicon starts with a verified Blender 5.2 LTS patch, Intel with a compatible 4.5 LTS patch. Record the exact working version.
- **Python 3.12** for the outer harness, isolated in a project virtual environment. Blender uses its own bundled Python.
- **An OpenAI API key and usable API project** when the harness is ready for live planning and visual evaluation. This key is for Movie Factory's runtime, separate from Codex sign-in.
- **No Houdini or Unreal installation yet.** Those are later comparison phases.

Compatibility and authentication details, official links, security requirements, environment names, budgets and acceptance gates are in the full spec. Codex should check the actual Mac before selecting a Blender build or renderer.

## Put this handoff into a repository

Copy both Markdown files into a normal writable repository, preferably under `docs/`. Do not build inside a read-only `sources/` directory or edit synced ChatGPT reference files.

Give Codex this instruction:

> Implement the Blender-first Movie Factory feasibility harness described in `docs/MOVIE_FACTORY_3D_FEASIBILITY_SPEC.md`. Follow the repository instructions. Complete preflight, prior-art notes, schemas, immutable packages, deterministic controls, stable-ID scene persistence, targeted revision, validation, budget/telemetry, failure injection and reporting. Continue offline work when live prerequisites are missing. Use the configured capped live campaign only after the runtime is ready and API access is available. Leave Houdini and Unreal as later-phase design notes. Preserve all evidence and report actual status; Director acceptance must be entered by me.

If you place the spec elsewhere, adjust that path in the instruction.

## Credential setup

Keep the API key in your existing secret manager or a local ignored configuration file. Do not paste it into the Codex conversation. The controller may read `OPENAI_API_KEY`; Blender must never receive it.

Codex should create a placeholder `.env.example` and the required ignore rules first. Once those exist, a local development option is:

```sh
cp .env.example .env.local
chmod 600 .env.local
```

Enter the key privately in `.env.local`, then set the explicitly selected planner/vision model IDs. The implementation must load this file as data. Do not put a real key into a shell command, commit, screenshot, prompt or generated Blender script. You can leave the key blank while implementing and testing mocks.

The full spec sets a **USD 40 maximum API spend for the initial campaign**, including calibration and fault probes, with **USD 3 initial / USD 2 revision** limits per scored pair. These are caps rather than expected prices, and the controller enforces them before dispatching requests.

## Expected implementation workflow

The project uses a local Python 3.12 environment at `.venv`. Dependencies are resolved with hashes and installed into that environment with `uv`:

```sh
UV_PYTHON_INSTALL_DIR="$PWD/.runtime/python" UV_CACHE_DIR="$PWD/.cache/uv" uv python install 3.12
UV_PYTHON_INSTALL_DIR="$PWD/.runtime/python" UV_CACHE_DIR="$PWD/.cache/uv" uv venv --python 3.12 .venv
UV_CACHE_DIR="$PWD/.cache/uv" uv pip sync --python .venv/bin/python --require-hashes requirements.lock
UV_CACHE_DIR="$PWD/.cache/uv" uv pip install --python .venv/bin/python --no-deps --no-build-isolation -e .
source .venv/bin/activate
```

The lock must include the declared build backend as well as runtime/test dependencies so the editable install works without fetching unpinned build tools. These commands are for the implemented repository; the documentation bundle alone is not installable.

Then use the CLI Codex implements:

```sh
mf3d doctor --engine blender --output results/doctor.json
mf3d validate-spec --experiment feasibility/3d/3d-01
mf3d run --experiment feasibility/3d/3d-01 --provider mock --profile smoke
mf3d calibrate --experiment feasibility/3d/3d-01 --profile qualification_cpu
mf3d inject-failures --suite tests/unit --provider mock
MF_NATIVE_TEST=1 .venv/bin/python -m pytest -m blender
mf3d qualify --campaign feasibility/3d/3d-01/campaign.json --live
```

Mock/smoke runs prove the harness works. The live campaign measures the runtime's own API planning and review, independently of Codex's development effort. It creates five initial/revision pairs, each with three camera views before and after.

## What to review

Open the generated comparison report and inspect the original/revised shots. Confirm the table moved toward the sofa, the helmet shell became dark green, the room still feels like the same scene, and framing/lighting remain intentional. Enter your scores and acceptance through the implemented review command or review JSON; pending review remains pending.

The final bundle should contain native `.blend` files, all six selected images per pair, operation/scripts, state diffs, validation, complete runtime usage/costs including reasoning, failure/recovery evidence, prior-art notes, and a GREEN/YELLOW/RED report. Replay must work from pinned artifacts without another model call.

Missing tools or credentials should leave a precise setup report and usable offline work. They must never be disguised as a completed feasibility test.
