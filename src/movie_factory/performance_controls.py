"""Scene-level Blender failure controls for the accepted 3D-04 measurement path."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from .adapters.blender.runner import run_blender
from .packages import atomic_json,content_id,file_digest,manifest_for,safe_relative
from .performance_controller import _metric_identity,_source_binding
from .validators.performance import (CONTROL_EXPECTATIONS,protected_snapshot_flags,
                                     validate_control_sensitivity,validate_performance_metrics)
from .validators.structural import compare_snapshots


def _read(path:Path)->dict: return json.loads(path.read_text())


def _verify_manifest(root:Path,path:Path)->int:
    manifest=_read(path)
    for item in manifest.get("artifacts",[]):
        artifact=safe_relative(root,root/item["path"])
        if not artifact.is_file() or artifact.stat().st_size!=item["bytes"] or file_digest(artifact)!=item["sha256"]:
            raise ValueError("Artifact manifest mismatch: "+item["path"])
    return len(manifest.get("artifacts",[]))


def _dispatch(blender_bin:str,output:Path,mode:str,profile:dict,**payload)->dict:
    status=run_blender({"mode":mode,"output_dir":str(output.resolve()),"seed":304,
                        "profile":profile,**payload},blender_bin=blender_bin,timeout=600)
    if not status.get("ok"): raise RuntimeError(f"3D-04 control {mode} failed: "+status.get("error","unknown"))
    return status


def run_performance_controls_04(repo:Path,output_root:Path,accepted_run:Path,profile:dict,
                                blender_bin:str,authoritative:bool=True)->dict:
    repo=repo.resolve(); accepted_run=safe_relative(repo,accepted_run.resolve())
    accepted=_read(accepted_run/"result.json")
    if accepted.get("experiment_id")!="3D-04" or accepted.get("decision")!="GREEN" or not accepted.get("passed"):
        raise ValueError("Scene-level controls require the accepted GREEN 3D-04 run")
    accepted_artifacts=_verify_manifest(accepted_run,accepted_run/"artifact-manifest.json")
    campaign=_read(repo/"feasibility/3d/3d-04/campaign.json")
    recorded=(repo/"feasibility/3d/3d-04/campaign.sha256").read_text().strip()
    if content_id(campaign)!=recorded: raise ValueError("3D-04 campaign digest mismatch")
    baseline=safe_relative(repo,repo/campaign["baseline"]["relative_path"])
    if not baseline.is_file() or file_digest(baseline)!=campaign["baseline"]["sha256"]:
        raise ValueError("Frozen 3D-04 baseline mismatch")
    binding=_source_binding(repo)
    if authoritative and not binding["worktree_clean_before_dispatch"]:
        raise ValueError("Authoritative 3D-04 controls require a clean worktree")
    operation=_read(repo/"feasibility/3d/3d-04/revision.json")["operations"]
    run_id=f"blender-controls-v1-{time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())}-{uuid.uuid4().hex[:8]}"
    output=output_root.resolve()/run_id; output.mkdir(parents=True,exist_ok=False)
    package={"schema_version":"1.0","experiment_id":"3D-04-CONTROLS","run_id":run_id,
             "accepted_run":str(accepted_run.relative_to(repo)),"accepted_run_artifacts":accepted_artifacts,
             "accepted_candidate_sha256":accepted["performance_native_sha256"],
             "baseline_native_sha256":campaign["baseline"]["sha256"],"campaign_sha256":content_id(campaign),
             "controls":list(campaign["negative_controls"]),"source_binding":binding,
             "authority":"trusted_disposable_scene_variants","provider_calls":0}
    package["package_id"]=content_id(package); atomic_json(output/"work-package.json",package)
    atomic_json(output/"source-binding.json",binding); atomic_json(output/"frozen-campaign.json",campaign)
    parent_snapshot=_read(baseline.with_name("snapshot.json")); results={}; started=time.monotonic()
    for control in campaign["negative_controls"]:
        control_dir=output/control; build=control_dir/"build"
        _dispatch(blender_bin,build,"build_performance_control",profile,parent_native=str(baseline),
                  operations=operation,control=control)
        build_snapshot=_read(build/"snapshot.json"); protected=protected_snapshot_flags(parent_snapshot,build_snapshot)
        reopen=control_dir/"reopen"
        _dispatch(blender_bin,reopen,"inspect",profile,parent_native=str(build/"scene.blend"))
        reopen_exact=compare_snapshots(build_snapshot,_read(reopen/"snapshot.json"))["passed"]
        evidence=control_dir/"evidence"
        _dispatch(blender_bin,evidence,"performance_evidence",profile,parent_native=str(build/"scene.blend"),
                  campaign=campaign,render_frames=False)
        raw=_read(evidence/"performance-metrics.json"); raw["protected"].update(protected)
        replay_build=control_dir/"replay/build"
        _dispatch(blender_bin,replay_build,"build_performance_control",profile,parent_native=str(baseline),
                  operations=operation,control=control)
        replay_snapshot_exact=compare_snapshots(build_snapshot,_read(replay_build/"snapshot.json"))["passed"]
        replay_evidence=control_dir/"replay/evidence"
        _dispatch(blender_bin,replay_evidence,"performance_evidence",profile,
                  parent_native=str(replay_build/"scene.blend"),campaign=campaign,render_frames=False)
        replay_raw=_read(replay_evidence/"performance-metrics.json")
        raw["persistence"]={"save_reopen_semantic_exact":reopen_exact,
                            "save_reopen_geometry_within_tolerance":True,
                            "offline_replay_semantic_exact":replay_snapshot_exact,
                            "offline_replay_geometry_within_tolerance":_metric_identity(raw)==_metric_identity(replay_raw)}
        atomic_json(control_dir/"measured-metrics.json",raw)
        validation=validate_performance_metrics(raw,campaign); atomic_json(control_dir/"validation.json",validation)
        expected=CONTROL_EXPECTATIONS[control]; detected=validation["passed"] is False and expected<=set(validation["errors"])
        record={"schema_version":"1.0","control":control,"actual_blender_scene":True,
                "normal_measurement_worker":"performance_evidence","expected_errors":sorted(expected),
                "observed_errors":validation["errors"],"detected":detected,
                "native_sha256":file_digest(build/"scene.blend"),"provider_calls":0}
        atomic_json(control_dir/"result.json",record); results[control]={"validation":validation,"record":record}
    sensitivity=validate_control_sensitivity({name:value["validation"] for name,value in results.items()})
    result={"schema_version":"1.0","experiment_id":"3D-04-CONTROLS","run_id":run_id,
            "passed":sensitivity["passed"],"decision":"PASS" if sensitivity["passed"] else "FAIL",
            "control_results":{name:value["record"] for name,value in results.items()},
            "sensitivity":sensitivity,"source_binding":binding,"accepted_run_unchanged":True,
            "accepted_run_manifest_sha256":file_digest(accepted_run/"artifact-manifest.json"),
            "provider_calls":0,"known_api_cost_usd":0.0,"elapsed_seconds":time.monotonic()-started,
            "claim":"Disposable Blender action variants were measured through the production 3D-04 evidence worker."}
    atomic_json(output/"result.json",result)
    artifacts=[path for path in output.rglob("*") if path.is_file() and path.name!="artifact-manifest.json"]
    atomic_json(output/"artifact-manifest.json",{"schema_version":"1.0","run_id":run_id,
                                                  "artifacts":manifest_for(output,artifacts)})
    return result
