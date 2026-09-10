from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from .packages import atomic_json, content_id, file_digest
from .plans import canonical_revision, fixture_plan
from .revision_compiler import compile_supported_revision
from .reporting import finalize_run_artifacts, write_comparison
from .schema import load_schema, validate


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _planner_prompt(brief: dict[str, Any], seed: int) -> str:
    return f"""You are the planning component of a measured 3D qualification harness. Return only the requested strict JSON scene plan. Create an intentional but simple procedural apartment interior. Use exactly the required stable IDs and values allowed by the schema.

Coordinate contract: positions are entity-root base contacts in metres, Z-up. The sofa, coffee table, and floor lamp position z MUST be exactly 0. The sofa faces local -Y. Put the coffee table in front of it with at least 0.45m clear travel toward the sofa without baseline or target overlap. Keep all object envelopes and the 0.4m table target inside the 5m x 4m x 2.8m room.

Use these safe planning bands: sofa position x [-0.15,0.15], y [0.8,1.0], dimensions x [2.2,2.5], y [0.8,0.95], z exactly 1.0. Coffee table position x [-0.1,0.1], y [-0.7,-0.55], dimensions x [1.1,1.3], y [0.55,0.7], z [0.38,0.45]. Floor lamp position x [-1.8,-1.6], y [0.7,1.0], dimensions x/y [0.4,0.5], z [1.65,1.8]. These bands keep envelopes within room bounds and leave the 0.4m table move clear.

Helmet support contract: put the helmet independently on the right sofa seat cushion, away from its edges and arms. Set its dimensions to about [0.34,0.36,0.30], rotation_z between -0.15 and 0.15, position x between 0.45 and 0.55, position y equal sofa.position.y minus 0.08, and position z MUST equal sofa.position.z + 0.54 * sofa.dimensions[2] exactly. It must remain supported when the table moves.

Use this frozen qualification camera rig exactly so visibility is comparable across seeds: camera_A/shot_A position [3.6,-5.4,2.55], target [0,0.55,0.75], lens_mm 43; camera_B/shot_B position [-3.15,-3.1,1.65], target [0.1,0.6,0.8], lens_mm 42; camera_C/shot_C position [1.65,-0.55,1.35], target [0.68,0.9,0.85], lens_mm 62. Shot A is the wide, shot B the medium, and shot C the helmet insert.

Use exactly two neutral qualification lights: key_light_01 is AREA at [-2,-1.5,3.4], target [0,0.7,0.6], color #FFF0D9, energy 650 W, size 3 m; fill_light_01 is AREA at [2.8,-0.8,2.8], target [0,0.8,0.8], color #D3E4FF, energy 250 W, size 2.5 m. Set world_strength exactly 0.12 and exposure exactly 0. Do not tint lighting red or green. The helmet starts palette red #C62828; dark green #163D2A is reserved for the revision. Do not add entities, fields, links, assets, animation, or procedural modifiers. Seed: {seed}. Brief: {json.dumps(brief, sort_keys=True)}"""


def _revision_prompt(revision: dict[str, Any], snapshot: dict[str, Any]) -> str:
    ids = sorted(obj["id"] for obj in snapshot.get("objects", {}).values())
    return f"""Return only the strict JSON revision operation list. The authorized instruction is: {revision['instruction']} The exact named palette is dark_green=#163D2A. Existing stable IDs are {ids}. Express 40 cm as 0.4 metres. Only the two authorized operations are permitted; do not add, delete, rebuild, or touch cameras, lights, geometry, transforms of other entities, or any other material field."""


def _provider_json(provider: Any, **kwargs: Any) -> dict[str, Any]:
    response = provider.generate_json(**kwargs)
    if response.get("error") or response.get("data") is None:
        raise RuntimeError(response.get("error") or "provider returned no structured data")
    return response


def _write_package(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    package = {**payload}
    package["package_id"] = content_id(package)
    atomic_json(path, package)
    return package


def run_pair(repo_root: Path, run_dir: Path, seed: int, profile: dict[str, Any], *, blender_bin: str, provider: Any | None = None, live: bool = False) -> dict[str, Any]:
    from .adapters.blender.runner import run_blender
    from .validators.structural import validate_baseline, validate_plan, validate_revision
    from .validators.perceptual import compare_renders

    run_dir.mkdir(parents=True, exist_ok=False)
    brief = _read(repo_root / "feasibility/3d/3d-01/brief.json")
    revision_brief = _read(repo_root / "feasibility/3d/3d-01/revision.json")
    calls: list[dict[str, Any]] = []
    initial_intent = _write_package(run_dir/"initial"/"intent-package.json", {
        "schema_version":"1.0","package_kind":"intent","experiment_id":"3D-01","run_id":run_dir.name,"stage":"initial","seed":seed,
        "brief_hash":content_id(brief),"render_profile":profile,"authority":{"operations":"structured_build","network":"controller_only","publishing":False},
        "budget":{"stage_usd":3.0,"max_calls":8},"toolchain":_read(repo_root/"config/toolchain.lock.json")
    })
    if live:
        base_prompt = _planner_prompt(brief, seed)
        plan = None; schema_errors=[]; semantic_errors=[]
        for attempt in range(3):
            feedback = "" if not (schema_errors or semantic_errors) else "\nYour previous plan was rejected by deterministic checks. Repair every error without changing the contract:\n- " + "\n- ".join(schema_errors + semantic_errors)
            result = _provider_json(provider, purpose="initial_plan" if attempt == 0 else "initial_plan_repair", prompt=base_prompt+feedback, schema=load_schema(repo_root,"scene-plan.schema.json"), images=None, run_id=run_dir.name, stage="initial", max_output_tokens=5000)
            calls.append({k:v for k,v in result.items() if k != "data"})
            plan = result["data"]; plan["seed"] = seed
            atomic_json(run_dir / "initial" / f"plan-attempt-{attempt+1}.json", plan)
            schema_errors = validate(repo_root,"scene-plan.schema.json",plan)
            semantic_errors = validate_plan(plan)
            if not schema_errors and not semantic_errors: break
    else:
        plan = fixture_plan(seed)
        schema_errors = validate(repo_root,"scene-plan.schema.json",plan)
        semantic_errors = validate_plan(plan)
    if schema_errors or semantic_errors:
        raise ValueError("invalid scene plan: " + "; ".join(schema_errors + semantic_errors))
    atomic_json(run_dir / "initial" / "plan.json", plan)
    _write_package(run_dir/"initial"/"executable-package.json", {
        "schema_version":"1.0","package_kind":"executable","intent_package_hash":initial_intent["package_id"],"stage":"initial",
        "plan_hash":content_id(plan),"plan_relpath":"plan.json","render_profile":profile,"worker":"trusted_structured_operations"
    })

    initial_build = run_dir / "initial" / "build"
    build_status = run_blender({"mode":"build","output_dir":str(initial_build),"seed":seed,"profile":profile,"plan":plan}, blender_bin=blender_bin, timeout=300)
    if not build_status.get("ok"):
        raise RuntimeError(f"initial build failed: {build_status.get('error')}")
    before_scene = initial_build / "scene.blend"
    before_snapshot = _read(initial_build / "snapshot.json")
    baseline_validation = validate_baseline(before_snapshot, plan)
    initial_render = run_dir / "initial" / "render"
    render_status = run_blender({"mode":"render","output_dir":str(initial_render),"seed":seed,"profile":profile,"parent_native":str(before_scene)}, blender_bin=blender_bin, timeout=900)
    if not render_status.get("ok"):
        raise RuntimeError(f"initial render failed: {render_status.get('error')}")

    compilation = compile_supported_revision(revision_brief["instruction"])
    if compilation["status"] == "compiled":
        operations = compilation["operations"]
    elif live:
        result = _provider_json(provider, purpose="revision_plan", prompt=_revision_prompt(revision_brief,before_snapshot), schema=load_schema(repo_root,"operations.schema.json"), images=None, run_id=run_dir.name, stage="revision", max_output_tokens=1200)
        calls.append({k:v for k,v in result.items() if k != "data"})
        operations = result["data"]
    else:
        raise ValueError("offline revision is outside the deterministic compiler vocabulary")
    operation_errors = validate(repo_root,"operations.schema.json",operations)
    if operation_errors:
        raise ValueError("invalid revision: " + "; ".join(operation_errors))
    atomic_json(run_dir / "revision" / "operations.json", operations)
    revision_intent = _write_package(run_dir/"revision"/"intent-package.json", {
        "schema_version":"1.0","package_kind":"intent","experiment_id":"3D-01","run_id":run_dir.name,"stage":"revision","seed":seed,
        "instruction_hash":content_id(revision_brief),"parent_native_hash":file_digest(before_scene),"parent_snapshot_hash":content_id(before_snapshot),
        "authority":{"operations":["translate_toward","set_base_color"],"network":"controller_only","publishing":False},"budget":{"stage_usd":2.0,"max_calls":6}
    })
    _write_package(run_dir/"revision"/"executable-package.json", {
        "schema_version":"1.0","package_kind":"executable","intent_package_hash":revision_intent["package_id"],"stage":"revision","parent_native_hash":file_digest(before_scene),
        "parent_native_relpath":"../initial/build/scene.blend","operations_hash":content_id(operations),"operations_relpath":"operations.json",
        "render_profile":profile,"seed":seed,"worker":"trusted_structured_operations"
    })

    revision_build = run_dir / "revision" / "build"
    revise_status = run_blender({"mode":"revise","output_dir":str(revision_build),"seed":seed,"profile":profile,"parent_native":str(before_scene),**operations}, blender_bin=blender_bin, timeout=300)
    if not revise_status.get("ok"):
        raise RuntimeError(f"revision failed: {revise_status.get('error')}")
    after_scene = revision_build / "scene.blend"
    after_snapshot = _read(revision_build / "snapshot.json")
    revision_validation = validate_revision(before_snapshot, after_snapshot, operations)
    revision_render = run_dir / "revision" / "render"
    revised_render_status = run_blender({"mode":"render","output_dir":str(revision_render),"seed":seed,"profile":profile,"parent_native":str(after_scene)}, blender_bin=blender_bin, timeout=900)
    if not revised_render_status.get("ok"):
        raise RuntimeError(f"revision render failed: {revised_render_status.get('error')}")

    expected_build = run_dir / "expected" / "build"
    expected_status = run_blender({"mode":"revise","output_dir":str(expected_build),"seed":seed,"profile":profile,"parent_native":str(before_scene),**canonical_revision()}, blender_bin=blender_bin, timeout=300)
    if not expected_status.get("ok"):
        raise RuntimeError(f"expected revision failed: {expected_status.get('error')}")
    expected_render = run_dir / "expected" / "render"
    expected_render_status = run_blender({"mode":"render","output_dir":str(expected_render),"seed":seed,"profile":profile,"parent_native":str(expected_build / 'scene.blend')}, blender_bin=blender_bin, timeout=900)
    if not expected_render_status.get("ok"):
        raise RuntimeError(f"expected render failed: {expected_render_status.get('error')}")
    image_validation = compare_renders(revision_render, expected_render, initial_render)

    visual_review = None
    if live:
        from .evaluator import visual_prompt
        images = [initial_render/"renders"/f"{s}.png" for s in profile["shots"]] + [revision_render/"renders"/f"{s}.png" for s in profile["shots"]]
        result = _provider_json(provider, purpose="visual_review", prompt=visual_prompt(), schema=load_schema(repo_root,"visual-review.schema.json"), images=images, run_id=run_dir.name, stage="revision", max_output_tokens=1200)
        calls.append({k:v for k,v in result.items() if k != "data"})
        visual_review = result["data"]
        atomic_json(run_dir / "visual-review.json", visual_review)
    required_dimensions = {"brief_fulfillment", "cinematography", "lighting_materials", "physical_finish", "continuity_revision"}
    visual_scores = visual_review.get("scores", []) if visual_review else []
    complete_rubric = len(visual_scores) == 5 and {item["dimension"] for item in visual_scores} == required_dimensions
    machine_visual = not live or (
        visual_review
        and complete_rubric
        and visual_review["recommendation"] == "pass"
        and visual_review["confidence"] >= .6
        and not visual_review["critical_findings"]
        and sum(item["score"] for item in visual_scores) / 5 >= 4
        and min(item["score"] for item in visual_scores) >= 3
    )
    passed = bool(baseline_validation.get("passed") and revision_validation.get("passed") and image_validation.get("passed") and machine_visual)
    result = {"schema_version":"1.0","run_id":run_dir.name,"seed":seed,"live":live,"passed":passed,"baseline_validation":baseline_validation,"revision_validation":revision_validation,"image_validation":image_validation,"visual_review":visual_review,"revision_compilation":{key:value for key,value in compilation.items() if key != "operations"},"provider_calls":calls,"parent_sha256":file_digest(before_scene),"revision_sha256":file_digest(after_scene),"director_status":"PENDING"}
    result["technical_status"] = "MACHINE_REVIEWED" if passed else "FAILED"
    result["creative_status"] = "AWAITING_DIRECTOR" if passed else "NOT_ELIGIBLE"
    known_costs=[call.get("cost_usd") for call in calls if call.get("cost_usd") is not None]
    costs={"known_api_cost_usd":sum(known_costs),"provider_calls":len(calls),"unknown_cost_calls":sum(call.get("cost_usd") is None for call in calls),"scope":"factory_runtime" if live else "qualification_control"}
    atomic_json(run_dir/"costs.json",costs)
    atomic_json(run_dir/"director-review.json",{"status":"PENDING","accepted":None,"scores":None,"notes":"Director review has not been entered."})
    atomic_json(run_dir / "result.json", result)
    comparison = write_comparison(run_dir, result)
    result["comparison"] = str(comparison)
    atomic_json(run_dir / "result.json", result)
    finalize_run_artifacts(run_dir, result)
    return result


def unique_run_id(seed: int) -> str:
    return f"seed-{seed}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:8]}"
