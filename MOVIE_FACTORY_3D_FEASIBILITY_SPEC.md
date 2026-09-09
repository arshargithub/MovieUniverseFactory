# Movie Factory — 3D Feasibility Tranche

**Primary experiment:** 3D-01 — Persistent Scene + Targeted Revision

**Document version:** 1.0 · **Prepared:** 2026-09-08

**Audience:** Codex implementing a local qualification harness; Director reviewing evidence
**Status:** Implementation specification. No feasibility runs or local installation checks have been performed for this document.

## 1. Mandate and decision to be made

Build the smallest credible proto-Factory that turns a semantic filmmaking brief into an editable, persistent 3D scene, renders it, evaluates it, and makes a narrowly scoped revision without damaging protected state. Measure both quality and the complete cost of getting an accepted result, including the LLM work needed to operate the tools.

Use **Blender first** as Candidate A for the persistent content-creation backbone. Qualify **Houdini later** as a procedural/simulation challenger. Qualify **Blender → Unreal later** as a complementary cinematic staging, preview, and rendering pipeline. Do not treat these as three interchangeable products or implement three integrations at once.

The decision after 3D-01 is whether this particular approach is worth advancing to persistent external assets and Characters. Passing a static room experiment does not establish feature-film quality, motion feasibility, universal editing competence, or a permanent stack choice.

Normative terms: **MUST** is required for qualification; **SHOULD** may be varied with a recorded reason; **MAY** is optional. Numerical gates below are proposed experiment policy, not claims about achieved performance. Freeze them before scored runs.

### Canonical initial brief

> Create a modest apartment living room containing a sofa, coffee table, floor lamp, and distinctive red motorcycle helmet. Establish three intentional cinematic camera setups and intentional lighting. Save the persistent scene and render all three shots.

### Canonical revision

> Move the coffee table 40 cm toward the sofa and make the helmet dark green. Do not change the cameras, sofa, room geometry, lighting, or composition.

Interpret this precisely:

- Move the **whole table assembly** 0.40 m horizontally toward a frozen sofa anchor, preserving its rotation, scale, materials, and local geometry.
- Change only the helmet shell's base color. Preserve its silhouette, visor, trim, roughness, position, and semantic identity.
- Preserve camera transforms, optics, focus, exposure, framing controls, all other scene properties, and all other entity identities.
- The moving table may naturally change its screen position, occlusion, reflections, and shadows. The helmet may change indirect color contribution. These are expected physical consequences; pixel-for-pixel identity to the original images is not the requirement.
- Place the helmet on a stationary sofa cushion or arm in the initial scene, independently of the table. It must remain supported and visible after revision. This avoids an ambiguous carried-prop change.

## 2. Architecture principles carried into the spike

1. Semantic intent and creative invariants are authoritative; native files are versioned realizations of that intent.
2. Every consequential operation uses an immutable, version-pinned work package.
3. Durable inputs, outputs, telemetry, and acceptance live outside the worker process. Worker memory and caches are disposable.
4. Technical completion, machine evaluation, and Director acceptance are separate states.
5. Retrying an operation differs from generating a new creative candidate. Preserve both identities and charge every physical provider call.
6. Preserve useful generated operations, scripts, graphs, parameters, prompts, and error reports with provenance.
7. Long-lived credentials stay in the trusted controller. Generated code and Blender workers receive no provider or GitHub credentials.
8. Reuse → Adapt → Create New. Inspect relevant prior art and its license before introducing a nontrivial capability or dependency.
9. Local compute is already capitalized, but time, energy, storage, licensing, and human intervention still need accounting.

For this spike, a local filesystem artifact store is sufficient. Demonstrate export and restore into a fresh worker directory. Replication across machines and a production cloud store remain deferred; this local experiment does not prove disaster recovery beyond the Mac.

## 3. Prerequisites and setup checks

### Required versus conditional dependencies

| Dependency | Needed for | Requirement / qualification action |
|---|---|---|
| Codex desktop, CLI, or IDE | Development | Use the existing signed-in local Codex environment. ChatGPT sign-in can provide Codex access; an API key is a separate supported authentication route, not a mandatory addition to ChatGPT sign-in. Record development tooling separately from Factory runtime. [Codex authentication](https://developers.openai.com/codex/auth/) |
| Local folder + Git | Versioning and reproducibility | Create or use a normal local repository. Preserve existing files and follow its `AGENTS.md`. If working from a ChatGPT project mirror, `sources/` is read-only reference material; build in a separate writable directory. |
| GitHub account / authentication | Remote repositories or APIs only | Optional for local development and public reads. Use existing GitHub CLI browser authentication or SSH for Git operations. A personal access token is an alternative, not universally required. Scope any token to the necessary repository and operations. [GitHub CLI auth](https://cli.github.com/manual/gh_auth_login), [GitHub authentication](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github) |
| Blender | Native scene creation, edits, renders | Install an official build on the worker Mac. Default executable: `/Applications/Blender.app/Contents/MacOS/Blender`; discover or override it. No provider key is required by Blender. [Blender download](https://www.blender.org/download/) |
| Outer Python | Controller, schemas, telemetry, image checks | Target CPython 3.12 initially; record and pin the exact working patch version. Use an isolated `.venv`, `pyproject.toml`, and a fully resolved dependency lock. This is an experiment choice, not a Blender requirement. |
| Blender's Python | `bpy` worker scripts | Use Blender's bundled runtime. Do not assume it matches outer Python or install the outer environment into it. Keep worker dependencies to Blender and its bundled modules where possible. [Blender API introduction](https://docs.blender.org/api/current/info_quickstart.html) |
| OpenAI API project and key | Live proto-Factory planning and visual evaluation | Required for the live experiment; unnecessary for documentation, mock runs, and deterministic Blender checks. The controller reads `OPENAI_API_KEY`. Verify model access and billing independently of Codex access. [API quickstart](https://developers.openai.com/api/docs/quickstart) |
| Network access | Dependency acquisition; controller API calls | Worker execution is offline. Separate provisioning access from execution access. No asset downloads are needed in canonical 3D-01. |
| Image analysis packages | Automated render validation | Start with pinned Pillow, NumPy, and scikit-image; JSON Schema validation and pytest for the harness. Add the official OpenAI Python SDK. Prefer standard-library orchestration. |
| Git LFS or artifact storage | Retaining selected large native/media outputs | Conditional. Keep routine run directories out of Git; commit small manifests and reports. Choose LFS before committing large approved assets. [Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) |
| Houdini / appropriate license | Later challenger only | Not a 3D-01 Blender prerequisite. Qualify `hython`/`hou`, native formats, worker and renderer entitlement separately. |
| Unreal Engine / matching toolchain | Later complement only | Not a 3D-01 Blender prerequisite. Qualify Editor, Python plugin, rendering features, macOS/Xcode compatibility, and license terms for the exact version. |

### macOS qualification

The official Blender requirements distinguish **5.0+ on Apple Silicon/macOS 13+** from **4.5 LTS, the last Intel/macOS 11.2 branch**. Use the official compatibility page when installing. Apple Silicon baseline: a verified stable **5.2 LTS** patch; Intel fallback: a verified **4.5 LTS** patch. Freeze the exact version, build hash, binary checksum, architecture, and source URL after the smoke test. Run different Blender branches as separate cohorts; do not pool their scores. [Blender requirements](https://www.blender.org/download/requirements/)

`doctor` MUST record:

- macOS version/build, hardware model class, physical CPU architecture, process architecture, and whether running through Rosetta;
- RAM, free space in the actual output volume, CPU/GPU model, and available render devices, without machine serial numbers or account names;
- Blender executable path, version/build, binary checksum, bundled Python version, and supported engine identifiers;
- outer Python executable/version, lock digest, Git version and commit/dirty state;
- whether required environment names are set, with **no values for secrets**;
- an actual headless test: create a tiny scene, save, exit, reopen in a new process, inspect state, render one PNG, decode it;
- CPU rendering support first; test Metal separately. Never report GPU acceleration merely because the Mac has a GPU;
- isolation mode, write/network confinement checks, and directory permissions.

Initial working target: 16 GB RAM and 20 GB free storage. These are experiment comfort targets, not vendor minima. Below them, reduce only the declared smoke profile or report a resource limitation. Never silently lower the scored quality profile. Abort starting a worker if free space is below 5 GB. Capture memory pressure and thermal observations when available; unavailable measurements are `null`.

Useful read-only discovery commands:

```sh
uname -m
sw_vers
sysctl -n hw.memsize
git --version
python3 --version
"/Applications/Blender.app/Contents/MacOS/Blender" --version
```

The implementer MUST validate commands against the actual machine. This document does not assert Blender, Python 3.12, GitHub CLI, or Houdini are already installed. Do not disable Gatekeeper globally to make an installation work.

### Environment contract

The repository's `.env.example` MUST contain placeholders only. The trusted controller explicitly loads `.env.local` if used; Python does not automatically load dotenv files. Parse it as data, never as shell code. Existing process environment takes precedence; only known names are accepted. Effective non-secret values are frozen into the package. Proposed defaults:

```dotenv
# Optional local development fallback; leave empty in the tracked example.
OPENAI_API_KEY=
BLENDER_BIN=/Applications/Blender.app/Contents/MacOS/Blender
MF_PROVIDER=openai
MF_PLANNER_MODEL=
MF_VISION_MODEL=
MF_REASONING_EFFORT=medium
MF_EXECUTION_MODE=structured_ops
MF_RUN_ROOT=./runs
MF_ARTIFACT_ROOT=./artifacts
MF_PRICEBOOK=./config/prices.json
MF_RENDER_PROFILE=qualification_cpu
MF_MAX_INITIAL_API_USD=3.00
MF_MAX_REVISION_API_USD=2.00
MF_MAX_CAMPAIGN_API_USD=40.00
MF_MAX_INITIAL_CALLS=8
MF_MAX_REVISION_CALLS=6
MF_MAX_REPAIRS_PER_STAGE=2
MF_LLM_MAX_OUTPUT_TOKENS=8192
MF_API_TIMEOUT_SECONDS=180
MF_WORKER_TIMEOUT_SECONDS=300
MF_RENDER_TIMEOUT_SECONDS=600
MF_INITIAL_TIMEOUT_SECONDS=1200
MF_REVISION_TIMEOUT_SECONDS=600
MF_NETWORK_POLICY=controller_only
```

Model IDs MUST be deliberately resolved before live execution, with their supported structured-output, image-input, reasoning-effort, output-limit, and pricing capabilities checked. Prefer a stable model snapshot where offered; record the requested and returned identifiers. Do not infer API access from models visible in Codex. Leaving the model blank is a setup error, not permission to choose an expensive fallback. Pin prompt versions and model settings; omit unsupported parameters rather than pretending they took effect.

`GH_TOKEN`/`GITHUB_TOKEN`, an SSH agent, or `gh` credentials are optional developer-process configuration, never part of the Factory work package. Later adapters may add `HOUDINI_HYTHON` and `UNREAL_EDITOR_BIN` after qualification. Resolve relative paths against the repository root, reject symlink escapes, and pass absolute canonical paths to workers.

## 4. Security and credential boundary

The trusted controller may call the provider. It MUST NOT execute model-supplied shell commands or Python. For the default experiment, the model emits typed operations; a reviewed adapter compiles them into Blender calls.

Worker launch MUST use an explicit environment allowlist. Remove `OPENAI_API_KEY`, GitHub variables, cloud credentials, proxy credentials, SSH agent access, and unrelated variables. Give Blender private task-scoped user/config/cache/temp directories. Do not expose the developer's home, keychain, credential files, or browser profile to an untrusted code worker. Blender inputs are read-only; output/scratch directories are task-scoped.

**A subprocess, AST filter, timeout, or `--disable-autoexec` is not a security sandbox.** Autoexec controls do not neutralize a script explicitly passed through `--python`. The default path executes only the trusted adapter over validated data, with bounded object count, mesh complexity, paths, and resource use. A production-strength isolation claim requires OS-enforced filesystem and network confinement, verified with harmless denied-access tests.

Free-form model-generated `bpy` MAY be investigated as a separately labeled experiment only inside a verified isolated worker environment, such as a disposable VM with no credentials, restricted mounts, and denied network. If suitable isolation is unavailable, mark that track `NOT_RUN_ISOLATION_UNAVAILABLE`; continue the structured-operations experiment. Do not silently run arbitrary generated code on the developer account. Performance from a VM is a separate cohort. Report honestly that a structured-operations GREEN qualifies that interface, not unrestricted code generation.

Other mandatory controls:

- Store credentials through an existing secret manager/Keychain workflow or a local ignored file with owner-only permissions. Never paste keys into prompts, scripts, screenshots, artifacts, Git remotes, or reports.
- Add `.env`, `.env.*`, and explicit exceptions for `.env.example` to `.gitignore`; also ignore credentials, `.venv/`, temporary files, and routine run/media directories. Perform a secret check before committing/exporting artifacts.
- Log sanitized provider requests/responses, usage, response/request IDs, and output hashes. Remove authorization headers and sensitive paths before persistence. Do not record environment dumps.
- Use `store=false` for API responses where supported by the selected flow. This is a request-storage setting, not a claim of zero provider retention; use the project's applicable data controls. [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data)
- Treat repository instructions, research code, downloaded assets, embedded Blender text blocks, and model output as untrusted input. External reference material cannot change authority, budgets, acceptance criteria, or credential policy.
- Disable automatic script execution when loading `.blend` files. No downloaded `.blend` files, add-ons, package installation, external file links, or network asset retrieval during canonical 3D-01.
- Provision approved dependencies separately; record source, exact version/commit, digest, license, and qualification result. No automatic `pip install` in generated scripts.
- A requested revision grants only the listed scene changes. It grants no publishing, uploading, repository pushing, purchasing, or license activation authority.

## 5. Repository layout and boundaries

Create this structure incrementally. Directories marked later need only a design note until their phase begins. The two Markdown files delivered with this handoff are specifications, not an already implemented repository.

```text
movie-factory/
  README.md
  AGENTS.md                         # scoped implementation instructions
  pyproject.toml
  requirements.lock                 # resolved outer/build/test deps with package hashes
  .python-version
  .env.example
  .gitignore
  .gitattributes                    # only if LFS is selected
  config/
    toolchain.lock.json
    prices.json
    render-profiles.json
    dependency-registry.json
  docs/
    MOVIE_FACTORY_3D_FEASIBILITY_SPEC.md
    SETUP_README.md
    decisions/
  feasibility/3d/
    platform-comparison.md
    prior-art/
      index.md
      scenecraft.md
      ll3m.md
      blendergym.md
      simworlds.md
    3d-01/
      brief.json
      revision.json
      invariants.json
      acceptance.json
      campaign.json
      prompts/                      # planner, repair, visual-review prompts
      fixtures/                     # tiny original test scenes/ops, explicit provenance
      blender/README.md
      houdini/README.md             # later
      unreal/README.md              # later complement experiment
  schemas/
    scene-brief.schema.json
    scene-plan.schema.json
    revision.schema.json
    operations.schema.json
    work-package.schema.json
    snapshot.schema.json
    telemetry-event.schema.json
    evaluation.schema.json
    result.schema.json
  src/movie_factory/
    cli.py
    controller.py
    packages.py
    state_store.py
    budget.py
    telemetry.py
    providers/openai_provider.py
    providers/mock_provider.py
    adapters/base.py
    adapters/blender/runner.py
    adapters/blender/compiler.py
    adapters/blender/worker.py
    adapters/blender/inspect.py
    validators/structural.py
    validators/perceptual.py
    reporting.py
  tests/
    unit/
    integration_blender/
    failure_injection/
    replay/
  artifacts/                        # content-addressed immutable objects; ignored by default
  runs/<campaign-id>/<run-id>/       # logs, candidates, comparisons; ignored by default
  results/<campaign-id>/             # small shareable reports + manifests
```

Keep core schemas, budgeting, lineage, and evaluation engine-neutral. Native extraction and execution belong in adapters. Do not build a general plugin framework, database service, queue, web UI, or distributed scheduler for this spike.

## 6. Prior-art assimilation is an implementation task

Before building a nontrivial component, spend a bounded research pass looking for relevant existing methods. Start with these exact projects; similar names are not interchangeable.

| Project and primary source | Evidence relevant to Factory | Required assimilation task | Initial reuse disposition |
|---|---|---|---|
| **SceneCraft: An LLM Agent for Synthesizing 3D Scenes as Blender Code**, Hu et al., [official publication](https://proceedings.mlr.press/v235/hu24g.html), [arXiv:2403.01248](https://arxiv.org/abs/2403.01248) | Scene planning, Blender code, visual refinement, reusable function/library patterns | Trace brief → graph/layout → code → render → critique. Write original support, in-front-of, and clearance fixtures and document their value to 3D-01. Look for an author-linked code release and pin it if found. | Learn from the method. No verified reusable official code release established in this pass. Do not confuse it with the separate layout-guided diffusion SceneCraft repository. |
| **LL3M: Large Language 3D Modelers**, [paper](https://arxiv.org/abs/2508.08228), [official repository](https://github.com/threedle/ll3m), [published license](https://github.com/threedle/ll3m/blob/main/LICENSE) | Planning, documentation retrieval, code debugging, visual refinement | Verify the paper/project identity and current agreement before downloading or running code. Extract high-level design lessons from permitted public material; define an original small index of the pinned Blender API docs and an original traceback repair test. Record hosted-service/provider lifecycle risk. | Do not incorporate code, prompts, weights, or assets under its restrictive academic/evaluation agreement into Movie Factory. A public repository is not a commercial-use license. Obtain permission before any restricted evaluation; paper-level analysis can proceed. |
| **BlenderGym**, [project](https://blendergym.github.io/), [paper](https://arxiv.org/abs/2504.01786), [repository](https://github.com/richard-guyunqi/BlenderGym-Open), [dataset](https://huggingface.co/datasets/richard-guyunqi/BG_bench_data) | Editing benchmarks and visual feedback expose failures that attractive demos hide | Recheck author-linked code/data versions and licenses. Catalog placement, materials, lighting, and procedural-edit task types. Create an original small subset with our identity/invariant/cost requirements. Inspect setup scripts and nested dependencies before execution. | License verification required separately for code and assets. No blanket permission inferred from a website license. |
| **SimWorlds**, [project](https://dynsimworlds.github.io/), [arXiv:2607.01766](https://arxiv.org/abs/2607.01766) | Staged dynamic Blender construction; perceptual and actual engine-state verification; localized repair | Extract an original staged build/checkpoint/reviewer protocol. Reproduce one static state-verification idea in 3D-01; reserve physics/cache/temporal lessons for 3D-04–06. Verify any claimed public repository or dataset through author links. | Learn from paper/protocol; public reusable code/data availability and license remain unresolved here. Do not confuse it with the singular SimWorld Unreal simulator. |

Each prior-art note MUST include: identity/authors/date; paper/project/repo URLs; retrieval date; inspected scope; commit if code inspected; code/data/model licenses separately; runtime/hardware/provider requirements; runnable/not-runnable reason; relevant failure modes; and a **Reuse / Adapt / Learn From / Ignore** decision for each useful component.

Evidence in this handoff is a literature/documentation review, not a reproduction: no upstream repository was cloned or run. The LL3M README reports its hosted server discontinued after the paper's model retired. BlenderGym's setup script fetches an additional Infinigen fork; inspect that dependency before execution. SimWorlds' inspected project links did not establish an independently downloadable code/data release. Its long-lived Blender/MCP implementation is useful prior art, while this experiment deliberately qualifies cold CLI workers first. [LL3M README](https://github.com/threedle/ll3m), [BlenderGym setup](https://github.com/richard-guyunqi/BlenderGym-Open/blob/master/starter_setup.sh), [SimWorlds paper](https://arxiv.org/html/2607.01766v1)

Produce `prior-art/index.md` with a decision matrix and evidence links. If a release or license cannot be verified, explicitly mark it unresolved and implement the minimum original component from permitted high-level ideas. Do not make upstream service availability a blocker for 3D-01. Check for related work when a concrete implementation failure emerges; do not turn assimilation into an open-ended literature project.

## 7. Execution architecture: CLI launches; bpy manipulates

```text
Director brief + invariant policy + budgets
                 |
Trusted Python controller ---- provider adapter ---- OpenAI API
                 |                  (planning / critique; metered)
                 v
Validated semantic plan / targeted operation list
                 |
Pinned executable work package + trusted Blender adapter
                 |
Blender background process → bpy → native scene / renders
                 |
Fresh-process inspector → state snapshot + deterministic validators
                 |
Image comparison + separate visual-review call + Director review
                 |
Versioned result, lineage, cost ledger, acceptance record
```

### Minimum adapter interface

Implement `probe()`, `compile(plan)`, `build(package)`, `revise(package)`, `inspect(native_scene)`, and `render(native_scene, shot_profile)`. Return typed artifacts, diagnostics, resource measurements, and capability flags. The controller alone decides retry, budget, candidate selection, and acceptance.

Prefer direct `bpy.data` access for stable identity and mutations. Use `bpy.ops` when needed, with explicit scene/view-layer/selection context. No mouse/UI automation and no persistent Blender MCP server are needed. The CLI/background and Python flags are documented by Blender. [CLI arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)

Representative launch, with paths produced by the controller:

```sh
"$BLENDER_BIN" --background --factory-startup --disable-autoexec \
  --python-exit-code 17 --python "$MF_WORKER_SCRIPT" -- \
  --package "$MF_PACKAGE_JSON" --output "$MF_ATTEMPT_DIR"
```

`MF_WORKER_SCRIPT`, `MF_PACKAGE_JSON`, and `MF_ATTEMPT_DIR` above are per-launch paths, not secret environment settings. In real code, use an argument array and `shell=False`. Do not concatenate commands from model output. Blender arguments execute in order; `--` ends Blender arguments and introduces the worker's arguments.

For revisions, the trusted worker reads the package's validated parent path and calls `bpy.ops.wm.open_mainfile(...)` **before** applying operations. It must never rebuild a fresh scene as a shortcut. Save into a new temporary `.blend` within the attempt directory; close Blender; reopen it in a fresh inspector process; only then mark native integrity verified. Do not overwrite the parent. Record parent hash before and after.

Launch processes with process-group ownership. On timeout terminate, then kill remaining children after a short grace period. Capture exit code, signal, stdout/stderr, start/end, peak memory when available, and all completed artifacts. A zero exit code alone is not success. Require valid JSON status, fresh expected files, matching hashes, and a reopen check. Incomplete output stays quarantined.

### Default generation strategy

Use a small, engine-neutral typed operation vocabulary: create procedural mesh/primitive assembly, assign material, set transform, create camera/light, establish relation, save, inspect, render. The model must choose dimensions, arrangement, palette, camera framing, and lighting from the brief. Generic builders may provide sofa cushions, legs, helmet shell/visor, bevels, and simple room surfaces. Record any preauthored recipe contribution; a fixed entire apartment template is a control, not proof of autonomous construction.

No `eval`, arbitrary expressions, import strings, shell instructions, or unconstrained file paths in operations. Bound the initial scene to 200 objects, 2 million evaluated vertices, 32 materials, 8 lights, and the three scored cameras. Reject unknown operations before Blender starts.

Revision mode exposes a strictly smaller operation vocabulary and cannot call object creation/deletion, remeshing, camera setters, light setters, or full-scene builders. Preserve the actual compiled script and operation list. API documentation retrieval, if useful, is a small version-pinned local index; no vector database service is required.

## 8. Semantic input and schema contract

Implement JSON Schema Draft 2020-12 validation at all trust boundaries. Use strict objects (`additionalProperties: false`), finite numbers, explicit units, enums for operation types, unique IDs, bounded arrays, resolved references, and relative package paths without traversal. Validate cross-reference and geometry rules in code where JSON Schema is insufficient. The provider's structured-output subset may require a simpler schema; validate its response again against the complete local contract. Handle refusals, incomplete output, and unsupported fields without execution. [Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)

### Semantic brief example

This is a complete intended brief shape; Codex must encode and validate it in the repository. The resolved plan supplies exact geometry, material parameters, camera transforms, and lights. Do not put `bpy` names or backend-specific engine IDs in the semantic brief.

```json
{
  "schema_version": "1.0",
  "experiment_id": "3D-01",
  "scene_id": "apartment_living_room_01",
  "scene_version": 1,
  "units": {"length": "m", "angle": "rad", "up_axis": "Z", "handedness": "right"},
  "intent": "A modest, lived-in apartment living room, intentionally composed for a film.",
  "semantic_palette": {"red": "#C62828", "dark_green": "#163D2A"},
  "room": {"id": "room_01", "interior_size_m": [5.0, 4.0, 2.8]},
  "entities": [
    {"id": "sofa_01", "kind": "sofa", "description": "Modest two-seat fabric sofa"},
    {"id": "coffee_table_01", "kind": "coffee_table", "description": "Low wooden table; whole assembly moves together"},
    {"id": "floor_lamp_01", "kind": "floor_lamp", "description": "A practical lamp with a recognizable shade"},
    {"id": "helmet_01", "kind": "motorcycle_helmet", "description": "Recognizable helmet shell, dark visor and contrasting trim"}
  ],
  "materials": [
    {"id": "helmet_shell_01", "owner_entity_id": "helmet_01", "base_color_srgb_hex": "#C62828", "roughness": 0.32, "metallic": 0.0}
  ],
  "relations": [
    {"type": "inside", "subjects": ["sofa_01", "coffee_table_01", "floor_lamp_01", "helmet_01"], "target": "room_01"},
    {"type": "in_front_of", "subject": "coffee_table_01", "target": "sofa_01", "minimum_revision_travel_m": 0.4},
    {"type": "supported_by", "subject": "helmet_01", "target": "sofa_01"},
    {"type": "no_intersection", "subjects": ["coffee_table_01", "sofa_01"]}
  ],
  "shots": [
    {"id": "shot_A", "camera_id": "camera_A", "intent": "Wide establishing view; all four props readable", "preferred_focal_length_mm": 28},
    {"id": "shot_B", "camera_id": "camera_B", "intent": "Medium view relating table, sofa and helmet", "preferred_focal_length_mm": 50},
    {"id": "shot_C", "camera_id": "camera_C", "intent": "Helmet insert with enough room context to preserve identity", "preferred_focal_length_mm": 85}
  ],
  "lighting_intent": "Soft window-like key with motivated warm practical light and legible helmet color",
  "render_profile": "qualification_cpu",
  "seed": 101,
  "asset_policy": "original_procedural_only",
  "invariant_policy_id": "3d01-invariants-v1",
  "acceptance_policy_id": "3d01-acceptance-v1"
}
```

`preferred_focal_length_mm` is a build suggestion. Actual focal lengths are resolved, recorded, and frozen before revision. The room interior must fit within the specified size within 1 mm; decorative thickness can extend outwards. The scene plan fixes origin at floor center, +X right, +Y along the room depth, +Z up, and defines sofa forward direction explicitly. Anchors used in relations are named, persistent local points transformed into world space.

### Realized plan requirements

`scene-plan.json` MUST contain each entity's ID, class, parent, named anchors, dimensioned construction parameters, mesh parts with unique part IDs, transform, material slots, collision proxies, and provenance. Include all cameras and their projection/lens/sensor/clip/DOF settings; all lights and world/environment parameters; color management; frame; and resolved render settings.

Attach `mf_entity_id`, `mf_part_id`, `mf_created_in`, and stable material IDs in native custom properties, and maintain a matching external registry. Names like `Cube.003` are display labels, never identities. Assemblies have one stable root; part IDs remain unique across reloads. Revision changes the table root's translation and the dedicated helmet shell shader input, not their membership or creation lineage. Material sharing that would recolor another object is prohibited at baseline.

### Revision example

```json
{
  "schema_version": "1.0",
  "revision_id": "revision_01",
  "parent_scene_id": "apartment_living_room_01",
  "parent_scene_version": 1,
  "target_scene_version": 2,
  "instruction": "Move the coffee table 40 cm toward the sofa and make the helmet dark green. Do not change the cameras, sofa, room geometry, lighting or composition.",
  "changes": [
    {"op": "translate_toward", "entity_id": "coffee_table_01", "source_anchor": "floor_center", "target_entity_id": "sofa_01", "target_anchor": "floor_center", "distance_m": 0.4, "plane": "XY"},
    {"op": "set_base_color", "entity_id": "helmet_01", "material_id": "helmet_shell_01", "color_space": "sRGB", "hex": "#163D2A"}
  ],
  "preserve_policy_id": "3d01-invariants-v1",
  "allow_new_entities": false,
  "allow_deleted_entities": false
}
```

For the scored natural-language test, give the planner the `instruction`, parent state summary, stable-ID/anchor map, frozen semantic palette (`red = #C62828`, `dark_green = #163D2A`), and tool/policy schema. The palette is visible task context: the planner is not expected to guess an undisclosed exact shade. Hold the canonical `changes` and computed numeric expected delta in the trusted evaluator. The planner must produce a compatible operation list. A separate deterministic control directly applies `changes`; it is not scored as LLM comprehension.

Let `t` and `s` be the baseline world-space table and sofa floor-center anchors. Compute `d = (s.x-t.x, s.y-t.y, 0)` and `u = d / ||d||`. The expected table root translation is `p_after = p_before + 0.40*u`. Freeze this target once from the parent snapshot. Reject a zero/near-zero direction, insufficient clearance, or a target intersecting the sofa. Do not re-evaluate the direction or add another 0.40 m on a retry.

Color is not a vague text label: initial shell sRGB is `#C62828`; target is `#163D2A`. Convert each normalized sRGB channel to scene-linear using `c/12.92` for `c <= 0.04045`, otherwise `((c+0.055)/1.055)^2.4`. Alpha stays 1. Compare shader values in scene-linear space; separately assess the rendered appearance under frozen lighting and color management.

## 9. Immutable work packages, attempts, and persistence

Use two package layers to avoid pretending generated code existed before planning:

1. **Intent package:** semantic brief or revision, parent native/state hashes, entity versions, policies, budget, authority, prompts, model configuration, dependency lock, allowed assets, output contract.
2. **Executable package:** intent-package hash plus the validated plan/operations, compiled script hash, adapter hash, complete input manifest, render configuration, and exact worker toolchain. Freeze before that execution begins.

A repair creates a new executable package referencing the same frozen intent and the previous failed attempt. It cannot rewrite the package, invariant policy, or acceptance criteria. A new creative instruction creates a new intent package and lineage branch.

`work-package.schema.json` MUST require:

| Field | Contract |
|---|---|
| `schema_version`, `package_kind`, `package_id` | Versioned format and SHA-256 content identity |
| `experiment_id`, `campaign_id`, `logical_operation_id` | Experiment and stable operation lineage |
| `intent_package_hash` | Required for every executable package; null for an intent package, which never references its own hash |
| `parent_native_hash`, `parent_snapshot_hash` | Required for revision intent and revision executable packages; null for initial construction |
| `scene_id`, `input_scene_version`, `target_scene_version` | Explicit version lineage; no mutable “latest” paths |
| `input_manifest` | Relative path, byte size, media type, SHA-256, provenance/license reference for every input |
| `invariants_hash`, `acceptance_hash`, `prompt_hashes` | Frozen intent and evaluation policy |
| `plan_hash`, `operations_hash`, `script_hash`, `adapter_hash` | Required as applicable to executable packages |
| `toolchain`, `model_config`, `seed`, `render_profile_hash` | Exact engine, runtime, lock, model/settings, rendering dependencies |
| `authority` | Read roots, write root, network policy, allowed operations, no publishing authority |
| `budget` | Spend/calls/output-token/retry/time/object/geometry/storage ceilings |
| `expected_outputs` | Resolved per-profile manifest: native scene, snapshot, requested renders/masks, status and logs; qualification requires all three shots, smoke requires its one declared shot |
| `provenance` | Repository commit, tracked-source digest, dependency registry hash |

Hash canonical UTF-8 JSON with sorted keys, compact separators, finite numeric values, and deterministic array order. Hash the package manifest **excluding its own ID**; include all referenced file digests. Reject external symlinks and verify every input before launch. The final native scene hash identifies an artifact, not the semantic equivalence of two scenes.

Maintain an append-only attempt ledger with distinct `logical_operation_id`, `candidate_id`, `attempt_id`, `provider_request_id`, and artifact IDs. A process restart first checks valid completed checkpoints; it never blindly repeats a paid request. If an API timeout leaves completion/charges unknown, record `usage_unknown`, reserve its worst-case cost, and recover by response ID only if supported. A new call is a new physical realization and additional cost; do not assume provider idempotency.

Save checkpoints after a valid build, after validated revision, and after each rendered shot. Use temporary files and atomic promotion on the same volume; validate before updating the result pointer. A compare-and-swap on parent scene version prevents a stale result from becoming current. Stale outputs remain available for review with their true parent identity.

States MUST include `PLANNED`, `RUNNING`, `FAILED`, `TECHNICALLY_VALID`, `MACHINE_REVIEWED`, `AWAITING_DIRECTOR`, `ACCEPTED`, `REJECTED`, and `STALE`. Keep technical status and creative status in separate fields, not a single misleading success flag. Selecting a valid baseline for automated continuation is not Director acceptance.

## 10. Creative invariants and deterministic verification

Use a **deny-by-default diff**: every scene field is protected except the two authorized changes, scene-version bookkeeping, and explicitly enumerated non-creative render/output bookkeeping. No broad “ignore metadata” or “ignore transforms” rule.

### Required snapshot coverage

The trusted inspector, not the planner, writes the canonical snapshot from the reopened native scene. Include object/part/material IDs and relationships; local and world matrices; source geometry and topology digests; evaluated geometry digests; normals/UV/attributes; modifiers/constraints and their parameters; material node graphs, links and values; material assignment; render visibility and collection membership; camera data; lights and world; render/compositor/color management; external file references; animation/drivers; and provenance.

Canonicalize ordering by stable IDs. Exclude only documented transient data, such as memory addresses, UI selection, output paths, timing fields, and the currently selected render camera when iterating shots. Pin the shot-to-camera mapping separately. Reject unsupported modifiers, drivers, linked libraries, compositing nodes, or snapshot fields in this bounded experiment. A hash of names, IDs, or vertex counts alone is insufficient.

| Invariant | Exact requirement |
|---|---|
| Native persistence | Parent `.blend` unchanged; revised `.blend` reopens in a new process; all inputs/outputs match manifest hashes |
| Identity | Exact object/part/material ID sets, ownership, parents, collection membership, creation lineage; no duplicate/deleted/recreated entities |
| Table | Root translation equals frozen expected position within `1e-4 m`; displacement magnitude `0.4000 ± 0.0001 m`; no Z/rotation/scale change; every descendant local transform and local geometry unchanged |
| Table evaluated geometry | World geometry moves only by the allowed rigid translation; shape and topology remain equal in the assembly's local frame |
| Helmet | Only dedicated shell base-color RGB changes to target within `1e-6` per linear channel; alpha, shader topology, roughness, metallic, visor, trim, assignments, geometry and transforms unchanged |
| Sofa, room, lamp, other decor | Full protected geometry, transforms, materials, properties and visibility unchanged |
| Cameras | All three transforms, projection, lens, sensor/fit, shift, clips, DOF target/distance/aperture and shot bindings unchanged |
| Lighting/environment | Light IDs, transforms, shape, power, color, world nodes, environment, exposure, view transform and display settings unchanged |
| Render semantics | Engine/version/device, resolution, samples, seeds, frame, denoising, color management and compositor unchanged within a pair |
| Physical validity | No new table/sofa or table/room intersections; support and floor contact preserved; helmet remains supported; no hidden substitute geometry |
| Unexpected change | Any field outside the explicit allowlist fails, even if the images look acceptable |

Protected float values use an absolute tolerance of `1e-6` in stored native units, with normalized quaternion sign before rotation comparisons; exact strings, IDs, topology indices and counts use equality. Report raw max deltas, not just rounded pass/fail. Source geometry may be hashed after canonical quantization, but also compare numerical arrays within tolerance to avoid hash-boundary artifacts. Identical `.blend` file bytes are not required between semantically equal saves.

Check table clearance at baseline **and** target, using coarse bounding boxes followed by evaluated-mesh collision/contact checks where the coarse result is ambiguous. Freeze allowed contacts (feet/floor, helmet/sofa) separately from penetrations. Baseline must support the requested edit before entering the scored revision; a baseline that cannot support it is a failed initial construction.

To strengthen evidence against hidden reconstruction, revision mode starts only by opening the parent file, permits only the two operations, records each mutation, and denies creation/deletion. Matching snapshots alone cannot prove that an arbitrary Python program did not rebuild and restore the same state; do not overclaim this in the free-form-code track.

## 11. Rendering and perceptual validation

### Frozen render profiles

- `smoke`: 640×360, one camera, low samples; validates plumbing only.
- `qualification_cpu`: 1280×720, three cameras, Cycles CPU, 64 samples, fixed frame 1, fixed seed, denoising off for controlled comparisons. Pin color management and all settings supported by the selected Blender version.
- `qualification_metal`: same visual settings using a tested Metal device; separate cohort. Never silently fall back to CPU in a scored run.

Export lossless PNG beauty images and ID masks. A dedicated non-beauty mask pass must map stable IDs to pixels; camera and dimensions must match the beauty render. Derived contact sheets, flicker comparisons, and amplified differences are review aids, not replacements for original images.

Run three no-op re-renders of the same frozen scene on the same device/settings before scoring. Measure the numerical/render noise floor and pin the comparison configuration. If the proposed thresholds below cannot be met by no-op controls, investigate before scoring; record a new policy version rather than quietly widening tolerances afterwards.

### Independent evidence layers

1. **File/image validity:** fresh, decodable, correct size/type/camera mapping; detect blank/non-finite output and missing dependencies.
2. **Structural checks:** exact state validation from Section 10.
3. **Expected-revision control:** the trusted test adapter applies the canonical two changes to a separate copy of the parent and renders an oracle reference. The planner cannot see this reference or its operation payload. Compare the actual candidate to this expected revision, as well as the original. This separates legitimate lighting/occlusion changes from regressions. Count oracle rendering as qualification overhead, not Factory runtime.
4. **Perceptual metrics:** SSIM and normalized mean absolute RGB error on consistently decoded display-referred PNGs. Report per-shot full-frame, helmet crop, table crop, and remaining-region metrics. Use the union of before/after ID masks, expanded by 8 pixels at 1280×720, for local regions. Full-frame averages must not conceal small missing objects. Reflections/shadows can extend beyond masks; the oracle and reviewer resolve them.
5. **VLM review:** a separate context receives labeled original/revised images, brief, requested edit, and a fixed rubric. Require findings with shot IDs and image evidence; do not expose planner rationales or verdict targets. It grades appearance, not exact centimeter movement. Count every review and repair call.
6. **Director review:** provide a local comparison report, all six renders, invariant results, and costs. Record a human disposition and scores. Model approval cannot substitute for this record.

Expected-reference generation is an independent execution path for the known two-field edit, not a second LLM. The same trusted renderer can be used, but validate the oracle's state separately. Cross-renderer comparisons in later phases cannot use Blender pixel equality as ground truth.

### Visual rubric, scored 1–5

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Brief fulfillment / recognition | Missing or unrecognizable props | All props present but some ambiguous | Immediately readable room, furniture, lamp, motorcycle helmet |
| Cinematography | Accidental framing, clipping, blocked subjects | Serviceable views with uneven hierarchy | Three purposeful and distinct shots |
| Lighting / material legibility | Unreadable or broken | Readable with weaknesses | Motivated light, clear form and requested color |
| Physical plausibility / finish | Floating, intersecting, crude substitutes | Usable stylized scene | Coherent proportions, contact, material and silhouette detail |
| Continuity / targeted revision | Wrong scene or unintended change | Same scene with noticeable issues | Same scene; only intended edit and natural consequences apparent |

Use the first four dimensions for baseline acceptance and all five for revision. Stylized procedural assets are acceptable; disconnected primitives that do not read as the requested objects are not. A helmet is not merely a colored sphere. Require helmet visibility of at least 0.2% of image pixels in A and B, and 5% in C, measured from its visible ID mask. Require table visibility of at least 1% in A and B both before and after; C need not show the table. These are proposed visibility gates to freeze with the brief.

For each reviewer, average applicable per-shot scores within each dimension, then average those dimension scores with equal weight. Shot C is assessed against its insert intent, not a requirement to show every prop. The machine visual gate for candidate selection is a mean applicable VLM score of at least 4.0, no individual applicable score below 3, no critical finding, and passing visibility checks. Missing/malformed required scores or self-reported confidence below 0.6 yield `REVIEW_INCONCLUSIVE`, never a pass; any further review consumes the same bounded call budget. It is a machine continuation rule only. Director scores are collected independently using the same aggregation and may disagree; such disagreement must remain visible in the final disposition.

Visual-review JSON includes schema version, reviewer type/model, image hashes, per-shot scores, findings, severity, confidence, required corrections, and recommendation. Store Director identity as a chosen reviewer label, timestamp, acceptance/rejection, notes, and whether any hands-on edits occurred. Never invent a Director verdict.

## 12. Telemetry, reasoning cost, and cost-to-acceptance

Record development, qualification overhead, and proto-Factory runtime as distinct cost scopes. **Codex building the harness is development cost.** Runtime planning, API documentation retrieval if paid, debugging, visual self-evaluation, repair, and rerendering are Factory cost. Oracle renders, no-op calibration, fault injection, and human benchmark administration are qualification overhead. Report all scopes, but do not contaminate the initial-versus-revision operating ratio with development work.

### Required event fields

Each JSONL event includes `schema_version`, `event_id`, UTC time, monotonic duration where applicable, campaign/run/package/scene IDs, logical operation/candidate/attempt IDs, stage (`initial`, `revision`, `validation`, `recovery`), cost scope, event type, status, and sanitized artifact/request references.

For each provider call, record provider, requested/returned model, settings and prompt hash, request/response IDs, purpose, input image dimensions/count, latency, retries, error/status, `input_tokens`, `cached_input_tokens`, `output_tokens`, `reasoning_tokens`, `total_tokens`, pricing source/date/currency, estimated charge, known additional tool fees, and usage certainty. Preserve provider usage details for later reconciliation. Use `null` for missing fields; absence never means zero.

For each Blender invocation, record command arguments without secrets, executable/build, script/package hash, operation count/types, object/vertex counts, process startup/load/build/edit/save/render/inspect durations, per-shot render time, memory/resource measurements, timeout/exit status, warning/error classes, and produced bytes/hashes. Track machine and human repair counts separately, plus human minutes and reason for intervention.

### Reasoning cost without double counting

OpenAI reports reasoning usage within output-token details; reasoning tokens are billed as output tokens and can be consumed even when a response returns no usable final answer. Record the count, not hidden chain-of-thought content. `max_output_tokens` must budget for reasoning as well as other output. [Reasoning usage and limits](https://developers.openai.com/api/docs/guides/reasoning)

For a selected model whose pricebook uses ordinary input, cached input, and output rates per million tokens:

```text
I = reported input_tokens
C = reported cached input tokens (a subset of I)
O = reported output_tokens (includes R)
R = reported reasoning_tokens (a subset of O)

input_cost       = ((I - C) * rate_input + C * rate_cached_input) / 1_000_000
output_cost      = O * rate_output / 1_000_000
reasoning_cost   = R * rate_output / 1_000_000   # attribution within output_cost
other_output_cost = (O - R) * rate_output / 1_000_000
call_cost        = input_cost + output_cost + separately_billed_tool_fees
```

Do **not** add `reasoning_cost` again to `call_cost`. Do not label all `O-R` tokens visible prose; providers can include other output overhead. Do not add an image fee again if already represented in billed input tokens. Validate `0 <= C <= I` and `0 <= R <= O`; inconsistent or unavailable details require a diagnostic and qualified estimates. If a model introduces cache-write, long-context, service-tier, or other billing rules, implement that pricebook rule explicitly; do not force it into this formula. Use current official rates when configuring, freeze their source and effective date, and never hard-code this document's illustrative budget as pricing. [OpenAI pricing](https://developers.openai.com/api/docs/pricing)

### Cost and latency reports

Report initial construction and revision separately, including all failed attempts required to reach the selected candidate:

- API cost by planning, code/operation generation, debugging/repair, and visual evaluation;
- total tokens, reasoning tokens, provider calls, Blender invocations/operations, failures and repairs;
- end-to-end elapsed time, active controller time, Blender load/save/edit time, per-shot/total render time;
- direct external compute/provider/license cost; local compute seconds and optional energy/cost estimate with its assumptions;
- human interventions/minutes and optional cost assumption; Codex development cost shown separately if available;
- quality, machine validity, Director disposition, and total cost to the accepted result.

Compute `R_edit = revision planning+repair API cost / initial planning+repair API cost`, `R_api = all revision runtime API cost / all initial runtime API cost`, and `R_total = total revision runtime economic cost / total initial runtime economic cost`. Also report revision/build wall-time and render-time ratios. Return `null` with reason for zero/unknown denominators; never turn an undefined ratio into 0. Revision render cost may remain similar because all three shots are rendered again.

For a campaign, include **every attempted pair**, even abandoned failures. Aggregate cost per accepted pair equals total measured campaign Factory cost divided by accepted pairs; if none were accepted, report “no accepted result” and total spent. Keep actual external spend separate from estimated local cost. Do not claim local rendering is literally free or hide unsuccessful calls.

### Budget enforcement

Default proposed campaign ceiling: **USD 40 API spend**, allocated up to USD 10 for live calibration/development calls, USD 25 for five scored pairs (USD 3 initial + USD 2 revision per pair), and USD 5 for recovery probes. Unused allocation does not authorize exceeding any per-stage or campaign ceiling. Pure offline and local-render cost is reported separately; time/resource ceilings still apply.

Before a request, reserve its conservative upper cost using known input size/cost rules and maximum output tokens. Allow only one live call at a time initially. Reject a request that cannot fit; do not rely solely on a provider dashboard budget. Reconcile the reservation with actual usage. Unknown charges retain their reservation until resolved. Include SDK retries in both accounting and limits; prefer disabling opaque automatic retries and implementing two bounded transport retries for eligible transient failures, respecting rate-limit guidance. No automatic retry of auth failures, schema-policy violations, or unbounded truncated outputs.

Any increased cap, different model, new pricing, or threshold change creates a new recorded experiment configuration. A future user instruction to execute this specification authorizes only the configured run; it does not authorize unlimited API spend. This artifact delivery itself initiates no API or rendering jobs.

## 13. Canonical run and revision test protocol

1. Run `doctor`, offline tests, dependency/license qualification, isolation tests, and a model capability/price check before paid execution.
2. Freeze brief, schemas, prompts, operation vocabulary, seed list, toolchain, render profile, budget and acceptance policy. Capture the source commit and digest. Keep experimental tuning out of the scored cohort.
3. Run an original deterministic fixture to prove runner, snapshots, rendering and validation work without an LLM. This is a harness control only.
4. Calibrate no-op image reproducibility. Freeze the image thresholds before scored revision output is available.
5. For each of five scored runs with seeds `[101, 202, 303, 404, 505]`, ask the runtime planner to create the scene from the same semantic brief. Each run starts with a fresh process and no previously built apartment. Seeds control our procedural/render choices, not an assumed deterministic provider sampler.
6. Build, inspect, render all three shots, and run structural + visual self-review. Allow at most two repairs per stage within call/spend/time limits. Preserve every failed candidate. Select the baseline under a fixed rule: first candidate passing hard checks and the machine visual gate; never retrospectively select the most flattering result.
7. Freeze baseline native file, snapshot, ID registry, realized plan, images and manifest. The baseline must have space for the requested table movement and a dedicated helmet-shell material.
8. Close Blender. Send the exact natural-language revision to the runtime planner with baseline state and allowed operations. Validate the returned plan against the narrow authority. The trusted numeric oracle remains withheld.
9. Reopen the exact parent `.blend`, apply only the validated changes, save a new candidate, close, and inspect in a fresh process. Render all three shots using frozen settings. Generate the independent expected-revision reference for evaluation.
10. Produce state diffs, image metrics, annotated findings and a before/after report. Run visual self-review; if a repair is needed, start again from the unchanged parent with a new bounded executable package. Never incrementally apply another relative 40 cm move.
11. Collect Director scores and disposition for the selected baseline/revision pairs. Until supplied, label creative acceptance pending and final qualification at most YELLOW.
12. Run recovery/fault tests separately, restore a selected package into a fresh directory, replay without an LLM, and verify semantics and render tolerance. Export the evidence bundle and comparison report.

Hands-on Blender edits or scene-specific code changes during a scored run are interventions and invalidate autonomous success for that run. Fix the implementation, retain the failed evidence, and start a new campaign configuration. A missing key/license/tool yields `NOT_RUN` with the specific cause, not a fabricated benchmark failure or a GREEN result.

## 14. Failure injection and recovery requirements

Use tiny fixtures and mock providers for most faults. A fault succeeds when it is detected and handled as specified, not when it produces a beautiful image. Keep fault costs and timings outside normal performance statistics.

| Injected fault | Expected behavior and evidence |
|---|---|
| Invalid JSON / unknown operation / non-finite transform | Reject before execution; structured diagnostic; no scene mutation; bounded repair only if valid under budget |
| Wrong ID, duplicate ID, missing parent | Reject ambiguity; never guess by object display name; no new replacement entity |
| Protected camera/lamp/sofa edit | Block by operation policy or inspector; quarantine candidate; parent unchanged; explicit failing field |
| Shared helmet material | Baseline gate fails or revision is rejected; no accidental recoloring of other objects |
| Revision applied twice / duplicate job delivery | Return valid recorded result or reapply absolute target to original parent; total movement remains 0.40 m; no duplicate acceptance or ledger charge |
| Blender exception / syntax fault in a controlled fixture | Nonzero error result and captured traceback; no promotion; retry references original package and new attempt |
| Worker crash after native save | Reopen/check saved artifact, resume rendering if valid; preserve completed work; no unnecessary new planning call |
| Crash after shot B / before final acknowledgement | Verify A/B hashes and camera mapping; render only missing C; complete once; bill performed work once |
| Hung worker / child process | Kill owned process group within timeout/grace bounds, mark timeout, retain diagnostics; no orphan render loop |
| Partial/corrupt `.blend` or PNG | Decode/reopen/hash validation rejects it; resume from cheapest validated checkpoint |
| Missing asset / broken external link | Fail package validation or reopen validation; no network fetch or silent substitute |
| Stale parent / concurrent scene update | Preserve candidate as stale; compare-and-swap refuses promotion; no last-writer-wins overwrite |
| Disk floor reached / simulated write failure | Preflight or write handling stops safely; original scene and valid artifacts remain intact |
| API 429/5xx or unknown timeout outcome | Bounded controller retries, separate request identities, retained cost reservation; no blind unlimited retry |
| API refusal / truncated output / missing usage | No partial execution; diagnostic and bounded policy; missing usage remains unknown, not zero |
| Request would exceed spend/call/token cap | Deny before dispatch; budget-stop event; no unauthorized paid request |
| Harmless path escape/network/credential probe | Structured-op parser denies it. In isolated-code mode, OS policy independently denies access; audit the actual boundary |
| Worker emits fake success / modifies its own snapshot | Trusted fresh inspector and artifact checks override it; worker claims never establish acceptance |
| Reversed table direction / 0.4 cm unit error / hidden camera drift | Independent numeric validator rejects; demonstrate that render plausibility cannot override wrong state |

Acceptance transitions and cost ledger writes need crash-safe, exactly-once local recording keyed by event/request identity. Execution itself is at-least-once where unavoidable; distinguish these guarantees. Retrying stochastic model generation cannot promise identical output.

## 15. GREEN / YELLOW / RED decision rules

Evaluate dimensions separately, then set the overall color to the worst applicable dimension. These gates are for **3D-01 on the recorded machine/interface/configuration**. The experimental campaign is small; report counts and ranges, not a claim of population reliability.

| Dimension | GREEN | YELLOW | RED |
|---|---|---|---|
| Evidence completeness | All five predeclared scored pairs attempted; full manifests, metrics and costs; required recovery suite run | Fewer pairs, missing measurements, pending Director review, or dependency blocks | Falsified/irrecoverable evidence or a mandatory correctness/security check cannot be implemented |
| Autonomous initial + revision success | 5/5 pairs reach valid selected candidates within all caps, no hands-on edits | 4/5 succeed, or a recoverable limitation needs another campaign | 3/5 or fewer succeed, or success requires routine human scene/code repair |
| Structural preservation | Every selected revision passes 100% of hard invariants and native replay | Only quarantined failures were observed and repaired, but insufficient completed evidence | Any invalid candidate accepted/promoted as valid, missing authoritative check, or a selected candidate still violates a hard invariant |
| Director visual quality | Each accepted baseline/revision has mean applicable score ≥4.0 and no dimension <3; all five pairs accepted | Technically valid but mean 3.0–<4.0, disagreement, pending review, or only four accepted pairs | Mean <3.0 on reviewed candidates, critical missing/wrong content, or majority rejected |
| Expected-reference images | Every shot and required object crop has SSIM ≥0.98 and normalized MAE ≤0.01 | Every region still has SSIM ≥0.95 and MAE ≤0.03, or reproducibility prevents a confident pass | Any required region falls below SSIM 0.95 or above MAE 0.03 after valid calibration, or evidence shows unintended visual change |
| Revision operating economics | Median `R_edit ≤0.35` and `R_api ≤0.75`; known costs and all caps respected | `R_edit ≤0.75` and `R_api ≤1.00`, or denominators/usage prevent a sound ratio | Median exceeds either YELLOW ceiling, or budget enforcement permits overspend |
| Local latency | Median initial ≤10 min; revision ≤5 min; paired render-time ratio ≤1.25 | Completed within the 20 min initial / 10 min revision safety ceilings but misses a performance target, or hardware data is incomplete | Repeated timeouts/resource failures prevent the success gate |
| Recovery / execution boundary | All required faults detected; parents preserved; restart resumes correctly; boundary accurately scoped | A safe stop works but resumability or optional isolation track is unproven | Undetected corruption, credential exposure, forbidden access in a claimed sandbox, or silent invalid promotion |

SSIM/MAE use the exact reference pipeline in Section 11, not a naive comparison to the original image. If a crop has insufficient visible pixels, fail visibility or mark the metric inapplicable with a reason; never substitute a perfect score. Both SSIM and MAE gates must pass. Pixel metrics do not override structural or Director failures.

Count quarantined transient failures in first-attempt success, repair frequency, and cost. Their existence alone need not make a successfully repaired campaign RED. Every selected/accepted candidate must be clean. Report median, min/max, each run, first-attempt rate, and final bounded-repair rate; five trials are not enough for a production SLA or meaningful tail-latency claim.

A RED means “this tested configuration did not qualify.” Diagnose planner comprehension, operation vocabulary, adapter defects, engine limitation, evaluation quality, hardware, and economics separately. Do not attribute a harness bug to Blender or use one scene to dismiss an entire DCC.

## 16. Required outputs and artifact contract

For each initial/revision pair, leave:

```text
run.json                              # config, status, lineage; no credentials
initial/intent-package.json
revision/intent-package.json
attempts/<initial-or-revision>/<attempt-id>/
  executable-package.json
  plan.json / operations.json
  compiled_scene.py                    # trusted compiler output; provenance retained
  stdout.log / stderr.log
  worker-status.json
  scene.blend
  snapshot.json
  renders/shot_A.png
  renders/shot_B.png
  renders/shot_C.png
  masks/...
baseline-manifest.json
revision-manifest.json
structural-diff.json
validation.json
visual-review.json
director-review.json                   # pending until actually entered
telemetry.jsonl
costs.json
comparison.html                        # local, portable; no external scripts required
contact-sheet.png
artifact-manifest.json                 # path/type/bytes/SHA-256/role/lineage
```

Expected-revision reference renders, noise controls, replay evidence and failure reports live under clearly labeled qualification-overhead directories. Preserve the before and after native files as distinct content-addressed artifacts. Blender scripts and native files must be sufficient to replay without another LLM call, subject to the pinned toolchain/assets.

The campaign deliverable MUST include:

- `results/<campaign-id>/REPORT.md`: feasibility question, environment, approach, limits, per-run counts, quality, costs including reasoning, latency, invariants, failures, Director acceptance, decision color and next action;
- `summary.json` and `metrics.csv`: machine-readable results, with explicit null/unknown/not-run states;
- `platform-comparison.md`: Blender evidence and untested Houdini/Unreal entries clearly labeled; compare workflow roles, license/compute economics and qualification gaps;
- four prior-art notes and a component-level reuse decision matrix;
- toolchain/dependency/license record, frozen prices/settings/prompts, tests, replay/restore instructions;
- a portable selected-evidence bundle with checksums, sanitized logs, images and native files, plus an inventory of excluded bulky/raw data.

Retention default: keep all manifests, telemetry, selected and failed native candidates, plans/scripts and validation findings for the campaign; keep full renders for selected candidates and diagnostically useful failures. Do not delete evidence automatically during a campaign. Let a later explicit retention decision govern pruning.

## 17. Codex implementation instructions and completion contract

Treat this specification as an implementation task when the user asks to execute it. Work autonomously through the authorized Blender phase, making routine engineering choices. Do not interpret this handoff as authorization to buy software, upload assets, publish results, or run an unbounded research agent.

1. Inspect repository instructions and existing files; preserve synced/reference material. Create a normal working repository only in a writable location. Do not overwrite an existing `AGENTS.md` or README wholesale.
2. Read this spec and setup README. Create a short decision log covering execution strategy, exact versions, model selection/capabilities, isolation, asset policy and pricebook.
3. Run read-only preflight. If a required installation/key is missing, continue schema, mock, unit-test and documentation work, then report the precise remaining setup requirement. Never ask for a secret in chat or claim live success with mocks.
4. Complete the bounded prior-art notes and dependency qualification. Use original tiny fixtures until any reused material is cleared.
5. Implement strict schemas, content-addressed packages, append-only ledger, budget reservation, mock provider, and a narrow engine adapter interface.
6. Implement Blender build/open/edit/save/inspect/render with stable semantic identity. Start with deterministic fixture controls, then the LLM plan. Keep tests and the trusted oracle independent of planner-generated code.
7. Implement all deny-by-default structural invariants and negative tests before trusting visual approval. Implement comparison artifacts and human review entry.
8. Add the OpenAI provider and separate visual-review context. Meter calls at the provider boundary, including errors and repairs. Resolve a supported model and pricebook before live runs. Do not route Factory execution through an unmetered Codex conversation.
9. Run offline tests, Blender integration, no-op calibration and fault injection. Fix concrete failures; do not widen acceptance criteria merely to pass.
10. Execute the five-pair scored campaign only in the configured authorized live mode; retain all attempts. Export results even when blocked, YELLOW, or RED. Do not manufacture Director acceptance.
11. Reopen and replay selected artifacts in a fresh worker directory; verify package hashes and semantics. Review the report for unsupported claims and secret leakage.
12. Stop at the phase gate with reviewable evidence and a focused recommendation. Stub later adapters with documented interfaces; do not expand into the full movie system.

### CLI contract to implement

Expose `mf3d` from the package. Commands below are the requested future interface; they do not exist merely because this document exists.

```sh
mf3d doctor --engine blender --output results/doctor.json
mf3d validate-spec --experiment feasibility/3d/3d-01
mf3d run --experiment feasibility/3d/3d-01 --provider mock --profile smoke
mf3d calibrate --experiment feasibility/3d/3d-01 --profile qualification_cpu
mf3d qualify --campaign feasibility/3d/3d-01/campaign.json --live
mf3d inject-failures --suite tests/failure_injection --provider mock
mf3d review --run RUN_ID --open
mf3d review --run RUN_ID --import director-review.json
mf3d replay --package PACKAGE_PATH --offline --output REPLAY_DIR
mf3d report --campaign CAMPAIGN_ID
mf3d export --campaign CAMPAIGN_ID --output BUNDLE_DIR
```

`calibrate` uses the deterministic fixture and local rendering by default; any live tuning is separately labeled and explicitly enabled. `qualify --live` must show the frozen campaign ID/configuration and enforce its caps, with no surprise provider fallback. Human review entry/import changes only a review record and recalculates disposition. `replay --offline` cannot call a provider. All commands support machine-readable output and useful nonzero exits for setup/validation/execution failures. Reports remain writable on failure.

### Meaningful verification to implement

- Schema/reference/path/number validation; allowed edit diff versus forbidden edit; meter→centimeter error; sRGB conversion.
- Budget reservation, cached-token/reasoning arithmetic without double counting, unknown usage, duplicate event handling, campaign aggregation including failures.
- Parent hash and stale-version checks; absolute-target idempotency; crash-safe result promotion.
- Native build/reopen, semantic IDs, compound table movement, private helmet material, exact camera/light preservation, masks and image decoding.
- Negative controls that change a camera, hide a prop, alter lighting, reuse a material, or move the table incorrectly must fail the corresponding independent validator.
- Integration tests run with the pinned Blender executable; live API tests are opt-in and capped. CI's default suite uses mocks and original small fixtures.

Completion means the Blender harness, controls, negative tests, reports and replay work, and evidence reflects the actual run status. A finished implementation with missing API credentials or pending Director review may be delivered with explicit `NOT_RUN`/YELLOW results; it must not be described as qualified.

## 18. Phased implementation and subsequent 3D tranche

| Phase | Deliverable and exit condition |
|---|---|
| P0 — Grounding and environment | Preflight, license/provenance matrix, schemas, immutable packages, frozen experiment policy, chosen supported model. Continue offline work if live prerequisites are absent. |
| P1 — Deterministic Blender foundation | Original fixture builds, persists, reopens, renders; exact targeted revision and negative controls pass; credentials excluded and worker boundary documented. |
| P2 — Runtime intelligence | Semantic brief → LLM plan → bounded execution → self-review → repair. Full usage, reasoning cost and attempt telemetry. No hard-coded apartment masquerading as autonomous planning. |
| P3 — Blender qualification | Five scored pairs, fault suite, Director reviews, reproducible report and selected-artifact export. GREEN advances; YELLOW gets a bounded remediation campaign; RED gets a causal diagnosis. |
| P4 — Houdini challenger | Reuse neutral brief/invariants/cost schema. Implement only the smallest comparable static build/revision using `hython`/`hou`. Use procedural/native assets; save/reopen `.hip` or permitted license-specific format. Compare accepted quality, controllability, reasoning/repair burden, latency and software/worker/render licensing cost. |
| P5 — Unreal complement | Import a qualified Blender scene/assets into a pinned Unreal project. Preserve stable ID mapping, units, transforms, materials as supported, cameras and shot intent. Reopen the project; stage/render the three shots through Editor tooling. Repeat the table/color revision and test reimport propagation without losing Unreal-owned shot state. Measure interactive preview benefit and handoff cost. |

P4 does not require Blender to fail; run a bounded comparison after Blender evidence exists, especially if procedural complexity or repair cost is a concern. Do not carry every DCC through the entire tranche without evidence it can change the decision.

For Houdini, verify `hou` API, headless execution and license checkout in the chosen environment. Apprentice is a non-commercial license with restricted file/output workflows; it is not an assumed commercial Factory dependency. Check actual Indie/evaluation/commercial eligibility and batch/render entitlement before using it. Record current official price, currency, date and amortization assumptions; this spec does not pin historical license prices. [Houdini command-line Python](https://www.sidefx.com/docs/houdini/hom/commandline.html), [Houdini Apprentice](https://www.sidefx.com/products/houdini-apprentice/)

For Unreal, Python automation operates in the **Editor**, not as general packaged gameplay runtime scripting. Qualify Sequencer/Movie Render Queue and actual Mac feature support. Select USD, glTF or FBX through a small measured import test; no format promises automatic lossless material/rig/identity transfer. Freeze the ownership rule: Blender owns source geometry/material intent, Unreal may own staging/cinematic realization, and reimport updates only agreed fields. Record import mapping and losses. Use the same semantic acceptance tests plus explicit handoff invariants; assess visual quality by rubric, not cross-engine pixel equality. [Unreal Python scripting](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python), [Unreal macOS requirements](https://dev.epicgames.com/documentation/en-us/unreal-engine/macos-development-requirements-for-unreal-engine)

Treat these follow-on IDs as a staged agenda, not authorization to implement them now:

| ID | Feasibility question | Carry-forward evidence |
|---|---|---|
| 3D-02 — External/generated assets | Can acquired/generated motorcycle, sword and environment assets be imported, normalized, preserved and edited? | Asset provenance, licenses, scale/axis/material conversions, identity, targeted revision and total acquisition/repair cost |
| 3D-03 — Persistent humanoid Character | Can one Character retain identity across rig, wardrobe, materials, pose and camera changes? | Reusable rig/mesh/material state, close/wide review, versioning and identity evaluation |
| 3D-04 — Animation/performance | Can walk/run/sit and a subtle acting beat be staged and revised locally in time? | Temporal invariants, curve/rig state, motion quality, continuity and cost per accepted second |
| 3D-05 — Character–prop interaction | Can a Character interact persistently with a sword, motorcycle, door or placed object? | Contact, attachment, collision, physical causality and continuity |
| 3D-06 — Reference-driven motion | Can specific reference choreography, eventually the Gatka test, be reproduced and directed? | Reference provenance, motion alignment, technique fidelity, temporal/perceptual and human evaluation |
| 3D-07 — Hybrid realization | Can 3D blocking/cameras/motion/control passes guide generative finishing while preserving intent? | Identity, geometry, camera and temporal invariants across representation handoffs; accepted-second economics |

Each later experiment gets its own immutable brief, invariants, budget, failure cases, prior-art scan and acceptance gate. Advance only when preceding evidence supports the dependency, or run a separately justified risk probe.

## 19. Explicit non-goals

- A complete Movie Factory product, Studio desktop app, cloud orchestration platform, database architecture, marketplace, or publishing pipeline.
- A finished film, photoreal hero assets, proprietary asset downloads, paid generators, character creation/rigging, animation, physics, Gatka choreography, audio or generative video in 3D-01.
- Installing Houdini/Unreal before the Blender result; proving Blender is universally superior; selecting a permanent renderer from this single scene.
- Fine-tuning a model, building a large RAG service, training a 3D model, or importing a research codebase wholesale.
- Warm worker services, Blender MCP infrastructure, distributed rendering, multi-user collaboration or automatic cloud failover.
- Arbitrary script execution on the developer account, automatic dependency installation inside jobs, broad credentials in Blender, or bypassing software licenses.
- Editing original inputs in place, rebuilding the room during a targeted revision, or relaxing protected invariants to obtain prettier images.
- Treating a successful process exit, high SSIM, a VLM verdict, a mock run, or a polished report as Director acceptance.
- Treating undocumented vendor versions, prior conversation prices, paper claims, or unexecuted examples as measured results.

## 20. Definition of a useful outcome

The delivered evidence must let the Director answer: **Does this approach create a coherent editable world, preserve what I protect, make the requested change, recover from ordinary failures, and do so at an acceptable reasoning/tool/render cost?**

An honest YELLOW or RED with reproducible artifacts and a specific cause is a useful feasibility result. A GREEN without native persistence, protected-state proof, measured costs, and actual creative review is not.
