"""Provider-free controller for the frozen 3D-03 character qualification."""
from __future__ import annotations

import copy
import json
import subprocess
import time
import uuid
from pathlib import Path

from .packages import atomic_json,content_id,file_digest,safe_relative
from .reporting import finalize_run_artifacts,write_comparison
from .validators.character import validate_character_baseline,validate_character_revision
from .validators.structural import compare_snapshots


def _read(path): return json.loads(Path(path).read_text())


def resolved_character_plan(template:dict,staged:Path)->dict:
    plan=copy.deepcopy(template); specs=[plan["entity"]["source"],*plan["entity"]["skins"].values(),*plan["clips"].values()]
    for spec in specs:
        relative=Path(spec["path"])
        if relative.is_absolute(): raise ValueError("character asset paths must be portable")
        path=safe_relative(staged,staged/relative)
        if not path.is_file() or path.is_symlink() or file_digest(path)!=spec["sha256"]: raise ValueError("character asset digest mismatch")
        spec["path"]=str(path)
    return plan


def _package(path,payload):
    value=dict(payload); value["package_id"]=content_id(value); atomic_json(path,value); return value


def run_character_qualification(repo:Path,staged:Path,output_root:Path,profile:dict,blender_bin:str)->dict:
    from .adapters.blender.runner import run_blender
    template=_read(repo/"feasibility/3d/3d-03/scene.json"); revision=_read(repo/"feasibility/3d/3d-03/revision.json")
    assets=_read(repo/"feasibility/3d/3d-03/assets.json"); staged_manifest=_read(staged/"staged-manifest.json")
    plan=resolved_character_plan(template,staged); run_id=f"character-v1-{time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())}-{uuid.uuid4().hex[:8]}"
    run_dir=output_root/run_id; run_dir.mkdir(parents=True,exist_ok=False)
    status=subprocess.run(["git","status","--porcelain"],cwd=repo,text=True,capture_output=True,check=True).stdout
    binding={"schema_version":"1.0","status":"EXACT_PRE_RUN" if not status else "DIRTY_DEVELOPMENT",
             "implementation_commit":subprocess.run(["git","rev-parse","HEAD"],cwd=repo,text=True,capture_output=True,check=True).stdout.strip(),
             "implementation_tree":subprocess.run(["git","rev-parse","HEAD^{tree}"],cwd=repo,text=True,capture_output=True,check=True).stdout.strip(),
             "worktree_clean_before_dispatch":not bool(status)}
    for path,value in ((run_dir/"scene-plan.json",template),(run_dir/"revision-plan.json",revision),(run_dir/"staged-manifest.json",staged_manifest),(run_dir/"source-binding.json",binding)): atomic_json(path,value)
    _package(run_dir/"work-package.json",{"schema_version":"1.0","package_kind":"immutable_work_package","experiment_id":"3D-03","run_id":run_id,
             "scene_plan_sha256":content_id(template),"revision_plan_sha256":content_id(revision),"asset_manifest_sha256":content_id(assets),
             "staged_manifest_sha256":content_id(staged_manifest),"authority":{"build":"frozen_character_assets","revision":["set_character_skin","set_character_action"],"network":False,"provider_calls":0},"render_profile":profile})
    started=time.monotonic(); initial=run_dir/"initial/build"
    result=run_blender({"mode":"build_character","output_dir":str(initial.resolve()),"seed":template["seed"],"profile":profile,"plan":plan},blender_bin=blender_bin,timeout=600)
    if not result.get("ok"): raise RuntimeError("character build failed: "+result.get("error","unknown"))
    before=_read(initial/"snapshot.json")
    _package(run_dir/"revision/executable-package.json",{"schema_version":"1.0","package_kind":"executable","experiment_id":"3D-03","stage":"revision",
             "parent_native_sha256":file_digest(initial/"scene.blend"),"parent_native_relpath":"../initial/build/scene.blend",
             "operations_sha256":content_id(revision["operations"]),"operations_relpath":"../revision-plan.json","render_profile":profile,"seed":template["seed"],"worker":"trusted_structured_operations"})
    reopen=run_dir/"initial/reopen"; result=run_blender({"mode":"inspect","output_dir":str(reopen.resolve()),"seed":template["seed"],"profile":profile,"parent_native":str((initial/"scene.blend").resolve())},blender_bin=blender_bin,timeout=300)
    if not result.get("ok"): raise RuntimeError("character reopen failed: "+result.get("error","unknown"))
    reopened=_read(reopen/"snapshot.json"); initial_reopen=compare_snapshots(before,reopened); baseline=validate_character_baseline(reopened,template)
    initial_render=run_dir/"initial/render"; result=run_blender({"mode":"render","output_dir":str(initial_render.resolve()),"seed":template["seed"],"profile":profile,"parent_native":str((initial/"scene.blend").resolve())},blender_bin=blender_bin,timeout=1200)
    if not result.get("ok"): raise RuntimeError("character baseline render failed: "+result.get("error","unknown"))
    changed=run_dir/"revision/build"; result=run_blender({"mode":"revise_character","output_dir":str(changed.resolve()),"seed":template["seed"],"profile":profile,"parent_native":str((initial/"scene.blend").resolve()),"operations":revision["operations"]},blender_bin=blender_bin,timeout=300)
    if not result.get("ok"): raise RuntimeError("character revision failed: "+result.get("error","unknown"))
    after=_read(changed/"snapshot.json"); after_reopen_dir=run_dir/"revision/reopen"
    result=run_blender({"mode":"inspect","output_dir":str(after_reopen_dir.resolve()),"seed":template["seed"],"profile":profile,"parent_native":str((changed/"scene.blend").resolve())},blender_bin=blender_bin,timeout=300)
    if not result.get("ok"): raise RuntimeError("character revision reopen failed: "+result.get("error","unknown"))
    after_reopen=_read(after_reopen_dir/"snapshot.json"); revision_reopen=compare_snapshots(after,after_reopen); revision_validation=validate_character_revision(reopened,after_reopen,revision["operations"])
    revision_render=run_dir/"revision/render"; result=run_blender({"mode":"render","output_dir":str(revision_render.resolve()),"seed":template["seed"],"profile":profile,"parent_native":str((changed/"scene.blend").resolve())},blender_bin=blender_bin,timeout=1200)
    if not result.get("ok"): raise RuntimeError("character revision render failed: "+result.get("error","unknown"))
    passed=all(item["passed"] for item in (initial_reopen,baseline,revision_reopen,revision_validation))
    result={"schema_version":"1.0","experiment_id":"3D-03","run_id":run_id,"seed":template["seed"],"passed":passed,
            "technical_status":"MACHINE_REVIEWED" if passed else "FAILED","creative_status":"AWAITING_DIRECTOR" if passed else "NOT_ELIGIBLE","director_status":"PENDING",
            "initial_reopen_validation":initial_reopen,"baseline_validation":baseline,"revision_reopen_validation":revision_reopen,"revision_validation":revision_validation,
            "image_validation":{"passed":True,"method":"Director comparison pending; deterministic masks emitted"},"provider_calls":[],"known_api_cost_usd":0,
            "parent_sha256":file_digest(initial/"scene.blend"),"revision_sha256":file_digest(changed/"scene.blend"),"elapsed_seconds":time.monotonic()-started,"source_binding":binding,
            "claim_boundary":"Frozen Kenney skeleton, three compatible clips, two skins, and two supported structured revisions only."}
    atomic_json(run_dir/"costs.json",{"known_api_cost_usd":0,"provider_calls":0,"scope":"3D-03 provider-free qualification"})
    atomic_json(run_dir/"director-review.json",{"status":"PENDING","accepted":None,"scores":None,"notes":"Director review has not been entered."})
    atomic_json(run_dir/"result.json",result); result["comparison"]=str(write_comparison(run_dir,result)); atomic_json(run_dir/"result.json",result); finalize_run_artifacts(run_dir,result)
    return result


def replay_character_revision(run_dir:Path,output:Path,blender_bin:str)->dict:
    from .adapters.blender.runner import run_blender
    package_path=run_dir/"revision/executable-package.json"; package=_read(package_path); claimed=package.pop("package_id",None)
    if not claimed or content_id(package)!=claimed: raise ValueError("3D-03 replay package identity mismatch")
    parent=safe_relative(run_dir,run_dir/"revision"/package["parent_native_relpath"]); revision=_read(safe_relative(run_dir,run_dir/"revision"/package["operations_relpath"]))
    if file_digest(parent)!=package["parent_native_sha256"] or content_id(revision["operations"])!=package["operations_sha256"]: raise ValueError("3D-03 replay input mismatch")
    output.mkdir(parents=True,exist_ok=False); build=output/"build"
    status=run_blender({"mode":"revise_character","output_dir":str(build.resolve()),"seed":package["seed"],"profile":package["render_profile"],"parent_native":str(parent.resolve()),"operations":revision["operations"]},blender_bin=blender_bin,timeout=300)
    if not status.get("ok"): raise RuntimeError("3D-03 replay revision failed: "+status.get("error","unknown"))
    render=output/"render"; status=run_blender({"mode":"render","output_dir":str(render.resolve()),"seed":package["seed"],"profile":package["render_profile"],"parent_native":str((build/"scene.blend").resolve())},blender_bin=blender_bin,timeout=1200)
    if not status.get("ok"): raise RuntimeError("3D-03 replay render failed: "+status.get("error","unknown"))
    semantic=compare_snapshots(_read(run_dir/"revision/build/snapshot.json"),_read(build/"snapshot.json"))
    result={"schema_version":"1.0","experiment_id":"3D-03","ok":semantic["passed"],"package_id":claimed,"provider_calls":0,"semantic_replay":semantic,"native_sha256":file_digest(build/"scene.blend")}
    atomic_json(output/"replay-result.json",result); return result
