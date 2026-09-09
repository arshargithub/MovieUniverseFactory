# Implementation coordination contract

Use the project `.venv` for all outer Python. Do not read or log secret values from `.env`; the provider module alone loads known aliases. Never install global packages. Work from the full root feasibility specification.

Root owns orchestration, CLI, package storage, schemas, config, reporting, README, and environment setup. Blender agent owns `adapters/blender/{worker,inspect,runner}.py` plus native integration tests. Validation agent owns `validators/*`, original fixture plan, validator tests, and prior-art notes. Provider agent owns `settings.py`, `budget.py`, `telemetry.py`, `providers/*`, and their unit tests. Coordinate shared contracts via messages; do not edit other ownership areas without agreement.

## Scene plan (plain JSON dict)

`schema_version: "1.0"`, `scene_id: "apartment_living_room_01"`, `seed: int`.

`room`: `{size_m: [5,4,2.8], wall_color_hex: str, floor_color_hex: str}`.

`entities`: exactly four dicts, each `{id, kind, position: [x,y,z], rotation_z: radians, dimensions: [x,y,z], color_hex, roughness}`. IDs/kinds: `sofa_01/sofa`, `coffee_table_01/coffee_table`, `floor_lamp_01/floor_lamp`, `helmet_01/motorcycle_helmet`. Entity positions are root origins at floor/base contact. Sofa local front is -Y; fixture sofa top cushion height needs explicit documentation by worker. Helmet is independent and supported by sofa, not table. `helmet_shell_01` dedicated material. Materials and geometry are deterministic generic procedural builders, not free-form Python. No background wall behind cameras must obscure the views; room is an intentional open-front interior with floor/back/side walls, no ceiling, exact interior bounds.

`cameras`: exactly three `{id, shot_id, position:[x,y,z], target:[x,y,z], lens_mm:number}`; IDs `camera_A/B/C`, shots `shot_A/B/C`. Dof off by default for reliable first qualification, record it.

`lights`: 1–6 `{id, type: "AREA"|"POINT", position:[x,y,z], target:[x,y,z], color_hex, energy_w:number, size_m:number}`. Worker lamp practical may have a dedicated child light; preserve all.

`world_strength`: number; `exposure`: number. All unknown fields rejected by root schema.

## Revision operations

`{"operations":[{"op":"translate_toward","entity_id":"coffee_table_01","target_entity_id":"sofa_01","distance_m":0.4},{"op":"set_base_color","entity_id":"helmet_01","material_id":"helmet_shell_01","color_hex":"#163D2A"}]}`.

Only these two operation types and those fields. Validators verify targets/types and magnitude. Worker applies absolute expected target calculated from the parent on every new attempt. Parent is reopened and never overwritten. Inspector needs source local geometry, root/local/world transform, shader data and strict state signatures.

## Worker executable protocol

`worker.py -- --job JOB_JSON`; JSON job modes: `build`, `revise`, `inspect`, `render`. Paths are controller-validated absolute paths.

Common fields: `mode`, `output_dir`, `seed`, `profile` dict `{name,width,height,samples,device:"CPU",shots:["shot_A",...]}`. Build includes `plan` dict. Revise includes `parent_native` path and `operations` list. Inspect/render include `parent_native` path. Build/revise saves `scene.blend` and `snapshot.json`; rendering separate mode loads native and produces `renders/shot_A.png`, `masks/shot_A.png` etc. Any mask legend goes in `mask-legend.json`. Inspect produces `snapshot.json`. All modes write `worker-status.json` with `ok`, `mode`, `artifacts`, `timings`, error if failed. Root runner caller checks status and exit; worker must make exceptions nonzero. Trusted worker imports sibling inspect module by exact pinned file path (name `mf_blender_inspect`, avoid stdlib inspect shadowing). No third-party outer deps in Blender.

## Outer runner interface

`run_blender(job:dict, *, blender_bin:str, timeout:float=300) -> dict` in `adapters/blender/runner.py`. It writes job.json inside output dir, strips child environment, uses dedicated Blender config/cache/temp, captures stdout/stderr files, kills process group on timeout, returns worker-status augmented with elapsed, exit_code, error, command, environment_names. No API keys inherited. Root handles immutable input/package digests.

Snapshot exact field structure to be agreed between worker and validation agents immediately. Root only depends on `entities` identity data through helper validator functions; include top-level `schema_version`, `scene_id`, `objects`, `materials`, `cameras`, `lights`, `world`, `render`, `external_files`.

## Validators interface

`validate_plan(plan)->list[str]` for semantic/cross-reference restrictions after root JSON schema.
`validate_baseline(snapshot, plan)->dict` and `validate_revision(before,after,operations)->dict`; return `{passed:bool, checks:[{name,passed,details}], errors:list[str]}`.
`canonical_revision(before)->dict` returns operations shape above (trusted control only).
`compare_renders(actual_dir, expected_dir, baseline_dir=None)->dict`; image paths from render protocol, calculate per-shot and mask crop metrics and visibility; return `{passed:bool, color:"GREEN"|"YELLOW"|"RED", shots:...,errors:...}`.

## Provider/budget interface

Settings: `load_settings(repo_root:Path)->dict` maps `.env` lowercase `openai_api_key`, `github_token`, `github_repository` plus conventional aliases; do not expose secret dict in logs. Configure GPT-5.4 snapshot after root confirms official docs; no model fallback.

`BudgetLedger(path:Path,campaign_limit:float=40)` persistent append-only reservation/settlement ledger; constructor/operation details provider agent decides and documents to root. Campaign limits include all live calls across retries/restarts. Stages initial $3/8 calls, revision $2/6 calls, development aggregate $10, faults $5; scored aggregate $25. Every pair has unique run_id.

`OpenAIProvider(settings:dict, ledger:BudgetLedger, log_dir:Path)` with `generate_json(*,purpose:str,prompt:str,schema:dict,images:list[Path]|None=None,run_id:str,stage:str,max_output_tokens:int=8192)->dict` returning `{data:dict|None,usage:dict,cost_usd:float|None,response_id:str|None,error:str|None}`. It validates structured Responses output, uses `store=False`, no external tools, SDK max_retries=0, bounded accounted retries, reasoning medium, reserves conservative total costs including images. Root makes planner and separate visual-review prompts. Never log raw exceptions with keys.

Provider agent must open official current GPT-5.4 and structured Responses docs before implementation; root has searched those. Official selected snapshot `gpt-5.4-2026-03-05`, ordinary <272K input rates $2.5 input/$0.25 cached/$15 output per million per https://developers.openai.com/api/docs/models/gpt-5.4 . Confirm before freezing. No live calls by agents independently; root controls live spend.
