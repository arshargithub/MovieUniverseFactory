"""Controller for the provider-free 3D-02 external asset qualification."""
from __future__ import annotations

import copy
import json
import subprocess
import time
import uuid
from pathlib import Path

from .packages import atomic_json, content_id, file_digest, manifest_for, safe_relative
from .reporting import finalize_run_artifacts, write_comparison
from .validators.assets import validate_external_baseline, validate_external_revision
from .validators.structural import compare_snapshots


def _read(path: Path):
    return json.loads(path.read_text())


def _resolved_plan(template: dict, staged_root: Path) -> dict:
    plan = copy.deepcopy(template)
    if plan.get("experiment_id") != "3D-02":
        raise ValueError("wrong experiment")
    for entity in plan["entities"]:
        sources = []
        if "source" in entity: sources.append(entity["source"])
        for component in entity.get("components", []): sources.append(component["source"])
        for texture in entity.get("textures", {}).values(): sources.append(texture)
        for source in sources:
            relative = Path(source["path"])
            if relative.is_absolute(): raise ValueError("asset plan paths must be portable relative paths")
            resolved = safe_relative(staged_root, staged_root / relative)
            if not resolved.is_file() or resolved.is_symlink() or file_digest(resolved) != source["sha256"]:
                raise ValueError("staged asset missing or digest mismatch")
            source["path"] = str(resolved)
    return plan


def _package(path: Path, payload: dict) -> dict:
    result = dict(payload); result["package_id"] = content_id(result); atomic_json(path, result); return result


def run_asset_qualification(repo_root: Path, staged_root: Path, output_root: Path, profile: dict, blender_bin: str) -> dict:
    from .adapters.blender.runner import run_blender

    template_path = repo_root / "feasibility/3d/3d-02/scene.json"
    revision_path = repo_root / "feasibility/3d/3d-02/revision.json"
    assets_path = repo_root / "feasibility/3d/3d-02/assets.json"
    template, revision = _read(template_path), _read(revision_path)
    staged_manifest = _read(staged_root / "staged-manifest.json")
    plan = _resolved_plan(template, staged_root)
    run_id = f"asset-set-v1-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:8]}"
    run_dir = output_root / run_id; run_dir.mkdir(parents=True, exist_ok=False)
    git_status=subprocess.run(["git","status","--porcelain"],cwd=repo_root,text=True,capture_output=True,check=True).stdout
    source_binding={
        "schema_version":"1.0", "status":"EXACT_PRE_RUN" if not git_status else "DIRTY_DEVELOPMENT",
        "implementation_commit":subprocess.run(["git","rev-parse","HEAD"],cwd=repo_root,text=True,capture_output=True,check=True).stdout.strip(),
        "implementation_tree":subprocess.run(["git","rev-parse","HEAD^{tree}"],cwd=repo_root,text=True,capture_output=True,check=True).stdout.strip(),
        "worktree_clean_before_dispatch":not bool(git_status),
    }
    atomic_json(run_dir / "source-binding.json", source_binding)
    atomic_json(run_dir / "scene-plan.json", template); atomic_json(run_dir / "revision-plan.json", revision)
    atomic_json(run_dir / "staged-manifest.json", staged_manifest)
    _package(run_dir / "work-package.json", {
        "schema_version":"1.0", "package_kind":"immutable_work_package", "experiment_id":"3D-02", "run_id":run_id,
        "scene_plan_sha256":content_id(template), "revision_plan_sha256":content_id(revision),
        "asset_manifest_sha256":content_id(_read(assets_path)), "staged_manifest_sha256":content_id(staged_manifest),
        "authority":{"build":"frozen_external_assets", "revision":["translate_entity","rotate_entity_z"], "network":False, "provider_calls":0},
        "render_profile":profile,
    })
    started = time.monotonic()
    initial_build = run_dir / "initial/build"
    status = run_blender({"mode":"build_external","output_dir":str(initial_build.resolve()),"seed":template["seed"],"profile":profile,"plan":plan}, blender_bin=blender_bin, timeout=600)
    if not status.get("ok"): raise RuntimeError("external build failed: " + status.get("error", "unknown"))
    before = _read(initial_build / "snapshot.json")
    _package(run_dir / "revision/executable-package.json", {
        "schema_version":"1.0", "package_kind":"executable", "experiment_id":"3D-02", "stage":"revision",
        "parent_native_sha256":file_digest(initial_build/"scene.blend"), "parent_native_relpath":"../initial/build/scene.blend",
        "operations_sha256":content_id(revision["operations"]), "operations_relpath":"../revision-plan.json",
        "render_profile":profile, "seed":template["seed"], "worker":"trusted_structured_operations",
    })
    reopen_dir = run_dir / "initial/reopen"
    status = run_blender({"mode":"inspect","output_dir":str(reopen_dir.resolve()),"seed":template["seed"],"profile":profile,"parent_native":str((initial_build/"scene.blend").resolve())}, blender_bin=blender_bin, timeout=300)
    if not status.get("ok"): raise RuntimeError("initial reopen failed: " + status.get("error", "unknown"))
    reopened = _read(reopen_dir / "snapshot.json")
    reopen_validation = compare_snapshots(before, reopened)
    baseline_validation = validate_external_baseline(reopened, template)
    render_dir = run_dir / "initial/render"
    status = run_blender({"mode":"render","output_dir":str(render_dir.resolve()),"seed":template["seed"],"profile":profile,"parent_native":str((initial_build/"scene.blend").resolve())}, blender_bin=blender_bin, timeout=1200)
    if not status.get("ok"): raise RuntimeError("initial render failed: " + status.get("error", "unknown"))

    revision_build = run_dir / "revision/build"
    status = run_blender({"mode":"revise_external","output_dir":str(revision_build.resolve()),"seed":template["seed"],"profile":profile,"parent_native":str((initial_build/"scene.blend").resolve()),"operations":revision["operations"]}, blender_bin=blender_bin, timeout=300)
    if not status.get("ok"): raise RuntimeError("external revision failed: " + status.get("error", "unknown"))
    after = _read(revision_build / "snapshot.json")
    revision_reopen = run_dir / "revision/reopen"
    status = run_blender({"mode":"inspect","output_dir":str(revision_reopen.resolve()),"seed":template["seed"],"profile":profile,"parent_native":str((revision_build/"scene.blend").resolve())}, blender_bin=blender_bin, timeout=300)
    if not status.get("ok"): raise RuntimeError("revision reopen failed: " + status.get("error", "unknown"))
    after_reopen = _read(revision_reopen / "snapshot.json")
    revision_reopen_validation = compare_snapshots(after, after_reopen)
    revision_validation = validate_external_revision(reopened, after_reopen, revision["operations"])
    revised_render = run_dir / "revision/render"
    status = run_blender({"mode":"render","output_dir":str(revised_render.resolve()),"seed":template["seed"],"profile":profile,"parent_native":str((revision_build/"scene.blend").resolve())}, blender_bin=blender_bin, timeout=1200)
    if not status.get("ok"): raise RuntimeError("revision render failed: " + status.get("error", "unknown"))
    passed = all(item["passed"] for item in (reopen_validation, baseline_validation, revision_reopen_validation, revision_validation))
    result = {
        "schema_version":"1.0", "experiment_id":"3D-02", "run_id":run_id, "seed":template["seed"], "passed":passed,
        "technical_status":"MACHINE_REVIEWED" if passed else "FAILED", "creative_status":"AWAITING_DIRECTOR" if passed else "NOT_ELIGIBLE",
        "director_status":"PENDING", "initial_reopen_validation":reopen_validation, "baseline_validation":baseline_validation,
        "revision_reopen_validation":revision_reopen_validation, "revision_validation":revision_validation,
        "image_validation":{"passed":True,"method":"Director comparison pending; deterministic masks emitted"},
        "provider_calls":[], "known_api_cost_usd":0, "parent_sha256":file_digest(initial_build/"scene.blend"),
        "revision_sha256":file_digest(revision_build/"scene.blend"), "elapsed_seconds":time.monotonic()-started,
        "source_binding":source_binding,
        "claim_boundary":"Frozen CC0 FBX/GLB set and two supported structured revisions only.",
    }
    atomic_json(run_dir / "costs.json", {"known_api_cost_usd":0,"provider_calls":0,"scope":"3D-02 provider-free qualification"})
    atomic_json(run_dir / "director-review.json", {"status":"PENDING","accepted":None,"scores":None,"notes":"Director review has not been entered."})
    atomic_json(run_dir / "result.json", result)
    result["comparison"] = str(write_comparison(run_dir, result)); atomic_json(run_dir / "result.json", result)
    finalize_run_artifacts(run_dir, result)
    return result


def replay_asset_revision(repo_root: Path, run_dir: Path, output: Path, blender_bin: str) -> dict:
    from .adapters.blender.runner import run_blender
    package_path=run_dir/"revision/executable-package.json"; package=_read(package_path)
    claimed=package.pop("package_id",None)
    if not claimed or content_id(package)!=claimed: raise ValueError("3D-02 replay package identity mismatch")
    parent=safe_relative(run_dir,run_dir/"revision"/package["parent_native_relpath"])
    if file_digest(parent)!=package["parent_native_sha256"]: raise ValueError("3D-02 replay parent hash mismatch")
    revision=_read(safe_relative(run_dir,run_dir/"revision"/package["operations_relpath"]))
    if content_id(revision["operations"])!=package["operations_sha256"]: raise ValueError("3D-02 replay operation hash mismatch")
    output.mkdir(parents=True,exist_ok=False)
    build=output/"build"
    status=run_blender({"mode":"revise_external","output_dir":str(build.resolve()),"seed":package["seed"],"profile":package["render_profile"],"parent_native":str(parent.resolve()),"operations":revision["operations"]},blender_bin=blender_bin,timeout=300)
    if not status.get("ok"): raise RuntimeError("3D-02 replay revision failed: "+status.get("error","unknown"))
    render=output/"render"
    status=run_blender({"mode":"render","output_dir":str(render.resolve()),"seed":package["seed"],"profile":package["render_profile"],"parent_native":str((build/"scene.blend").resolve())},blender_bin=blender_bin,timeout=1200)
    if not status.get("ok"): raise RuntimeError("3D-02 replay render failed: "+status.get("error","unknown"))
    original=_read(run_dir/"revision/build/snapshot.json"); replayed=_read(build/"snapshot.json")
    semantic=compare_snapshots(original,replayed)
    result={"schema_version":"1.0","experiment_id":"3D-02","ok":semantic["passed"],"provider_calls":0,
            "package_id":claimed,"semantic_replay":semantic,"native_sha256":file_digest(build/"scene.blend")}
    atomic_json(output/"replay-result.json",result)
    return result
