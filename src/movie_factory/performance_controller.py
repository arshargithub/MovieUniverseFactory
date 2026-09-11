"""Provider-free controller for 3D-04 development and scored-candidate runs."""
from __future__ import annotations

import html
import json
import shutil
import subprocess
import time
import uuid
from copy import deepcopy
from pathlib import Path

from .packages import atomic_json,content_id,file_digest,manifest_for,safe_relative
from .validators.performance import (inject_performance_control,protected_snapshot_flags,
                                     validate_control_sensitivity,validate_performance_metrics)
from .validators.structural import compare_snapshots


def _read(path): return json.loads(Path(path).read_text())


def _source_binding(repo):
    status=subprocess.run(["git","status","--porcelain"],cwd=repo,text=True,capture_output=True,check=True).stdout
    return {"schema_version":"1.0","status":"EXACT_PRE_RUN" if not status else "DIRTY_DEVELOPMENT",
            "implementation_commit":subprocess.run(["git","rev-parse","HEAD"],cwd=repo,text=True,capture_output=True,check=True).stdout.strip(),
            "implementation_tree":subprocess.run(["git","rev-parse","HEAD^{tree}"],cwd=repo,text=True,capture_output=True,check=True).stdout.strip(),
            "worktree_clean_before_dispatch":not bool(status)}


def _metric_identity(raw):
    value=deepcopy(raw)
    value.pop("performance_native_sha256",None); value.pop("protected",None); value.pop("persistence",None)
    return content_id(value)


def _blind_assignment(package_id):
    candidate_first=int(package_id[:2],16)%2==0
    labels={"A":"candidate","B":"baseline"} if candidate_first else {"A":"baseline","B":"candidate"}
    payload={"schema_version":"1.0","package_id":package_id,"labels":labels}
    payload["blind_assignment_id"]=content_id(payload); return payload


def _write_review(run_dir,assignment):
    review=run_dir/"review"; (review/"frames/A").mkdir(parents=True); (review/"frames/B").mkdir(parents=True)
    for label,role in assignment["labels"].items():
        for source in sorted((run_dir/"evidence/frames"/role).glob("frame-*.png")):
            shutil.copy2(source,review/"frames"/label/source.name)
    panels=[]
    for label in ("A","B"):
        frames=[f"frames/{label}/frame-{frame:04d}.png" for frame in range(1,97)]
        panels.append(f'<section><h2>Clip {label}</h2><img data-label="{label}" src="{frames[0]}" alt="Anonymous run clip {label}"></section>')
    frame_sets={label:[f"frames/{label}/frame-{frame:04d}.png" for frame in range(1,97)] for label in ("A","B")}
    page=f'''<!doctype html><meta charset="utf-8"><title>3D-04 blinded synchronized review</title>
<style>body{{font:16px system-ui;margin:2rem;background:#171717;color:#eee}}main{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}section{{background:#242424;padding:1rem;border-radius:.5rem}}img{{width:100%;background:#333}}input{{width:min(700px,70vw)}}.notice{{color:#ffd479}}</style>
<h1>3D-04 anonymous A/B run review</h1><p class="notice">Watch the complete synchronized clips. One clip contains a timeline-local edit on frames 40–70. Labels do not reveal the mapping.</p>
<p><button type="button" id="toggle">Pause</button> <label>Frame <input id="frame" type="range" min="0" max="95" value="0"></label> <output id="number">1</output></p>
<main>{''.join(panels)}</main>
<h2>Frozen questions</h2><ol><li>Run readability for A and B, 1–5 in 0.5 increments.</li><li>Foot-contact quality for A and B, 1–5 in 0.5 increments.</li><li>Transition smoothness for A and B, 1–5 in 0.5 increments.</li><li>Concrete visible defects.</li><li>Overall preference: A, B, or tie.</li></ol>
<script>const frames={html.escape(json.dumps(frame_sets))},images=[...document.querySelectorAll('img[data-label]')],slider=document.querySelector('#frame'),number=document.querySelector('#number'),button=document.querySelector('#toggle');let index=0,playing=true;function show(value){{index=Number(value);images.forEach(image=>image.src=frames[image.dataset.label][index]);slider.value=index;number.value=index+1}}slider.oninput=()=>{{playing=false;button.textContent='Play';show(slider.value)}};button.onclick=()=>{{playing=!playing;button.textContent=playing?'Pause':'Play'}};setInterval(()=>{{if(playing)show((index+1)%96)}},1000/24);</script>'''
    (review/"index.html").write_text(page)
    return review/"index.html"


def run_performance_04(repo:Path,output_root:Path,profile:dict,blender_bin:str,render_frames:bool=True,scored:bool=False)->dict:
    from .adapters.blender.runner import run_blender
    campaign=_read(repo/"feasibility/3d/3d-04/campaign.json"); revision=_read(repo/"feasibility/3d/3d-04/revision.json")
    campaign_digest=content_id(campaign)
    recorded_digest=(repo/"feasibility/3d/3d-04/campaign.sha256").read_text().strip()
    if campaign_digest!=recorded_digest: raise ValueError("3D-04 campaign digest mismatch")
    baseline=safe_relative(repo,repo/campaign["baseline"]["relative_path"])
    if not baseline.is_file() or file_digest(baseline)!=campaign["baseline"]["sha256"]:
        raise ValueError("3D-04 frozen baseline native hash mismatch")
    parent_snapshot=_read(baseline.with_name("snapshot.json")); binding=_source_binding(repo)
    if scored:
        frozen=campaign.get("scored_source_binding",{})
        if campaign.get("campaign_status")!="FROZEN_FOR_SCORED_CAMPAIGN" or not binding["worktree_clean_before_dispatch"]:
            raise ValueError("A scored 3D-04 run requires the frozen campaign and a clean worktree")
        source_change=subprocess.run(["git","diff","--quiet",frozen.get("implementation_commit",""),"HEAD","--","src","tests"],cwd=repo)
        if source_change.returncode!=0: raise ValueError("3D-04 implementation differs from the frozen source commit")
        if not render_frames: raise ValueError("A scored 3D-04 run requires complete synchronized playback")
    run_id=f"performance-v1-{time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())}-{uuid.uuid4().hex[:8]}"
    run_dir=output_root/run_id; run_dir.mkdir(parents=True,exist_ok=False)
    package={"schema_version":"1.0","package_kind":"immutable_work_package","experiment_id":"3D-04","run_id":run_id,
             "campaign_sha256":campaign_digest,"revision_sha256":content_id(revision),
             "baseline_native_sha256":campaign["baseline"]["sha256"],"source_binding":binding,
             "render_profile":profile,"provider_budget":campaign["development_budget"]}
    package["package_id"]=content_id(package); assignment=_blind_assignment(package["package_id"])
    for path,value in ((run_dir/"frozen-campaign.json",campaign),(run_dir/"revision.json",revision),
                       (run_dir/"work-package.json",package),(run_dir/"source-binding.json",binding),
                       (run_dir/"blind-key.json",assignment)): atomic_json(path,value)
    started=time.monotonic(); build=run_dir/"build"
    status=run_blender({"mode":"build_performance","output_dir":str(build.resolve()),"seed":304,"profile":profile,
                        "parent_native":str(baseline.resolve()),"operations":revision["operations"]},
                       blender_bin=blender_bin,timeout=600)
    if not status.get("ok"): raise RuntimeError("3D-04 build failed: "+status.get("error","unknown"))
    if scored:
        frozen=campaign["scored_source_binding"]; toolchain=status.get("toolchain",{})
        if toolchain.get("blender")!=frozen["blender_version"] or toolchain.get("build_hash")!=frozen["blender_build_hash"]:
            raise ValueError("3D-04 Blender build differs from the frozen campaign")
    build_snapshot=_read(build/"snapshot.json"); protected=protected_snapshot_flags(parent_snapshot,build_snapshot)
    reopen=run_dir/"reopen"
    status=run_blender({"mode":"inspect","output_dir":str(reopen.resolve()),"seed":304,"profile":profile,
                        "parent_native":str((build/"scene.blend").resolve())},blender_bin=blender_bin,timeout=300)
    if not status.get("ok"): raise RuntimeError("3D-04 reopen failed: "+status.get("error","unknown"))
    reopen_exact=compare_snapshots(build_snapshot,_read(reopen/"snapshot.json"))["passed"]
    evidence=run_dir/"evidence"
    status=run_blender({"mode":"performance_evidence","output_dir":str(evidence.resolve()),"seed":304,"profile":profile,
                        "parent_native":str((build/"scene.blend").resolve()),"campaign":campaign,"render_frames":render_frames},
                       blender_bin=blender_bin,timeout=1800)
    if not status.get("ok"): raise RuntimeError("3D-04 evidence failed: "+status.get("error","unknown"))
    raw=_read(evidence/"performance-metrics.json"); raw["protected"].update(protected)
    replay_build=run_dir/"replay/build"
    status=run_blender({"mode":"build_performance","output_dir":str(replay_build.resolve()),"seed":304,"profile":profile,
                        "parent_native":str(baseline.resolve()),"operations":revision["operations"]},
                       blender_bin=blender_bin,timeout=600)
    if not status.get("ok"): raise RuntimeError("3D-04 replay build failed: "+status.get("error","unknown"))
    replay_snapshot_exact=compare_snapshots(build_snapshot,_read(replay_build/"snapshot.json"))["passed"]
    replay_evidence=run_dir/"replay/evidence"
    status=run_blender({"mode":"performance_evidence","output_dir":str(replay_evidence.resolve()),"seed":304,"profile":profile,
                        "parent_native":str((replay_build/"scene.blend").resolve()),"campaign":campaign,"render_frames":False},
                       blender_bin=blender_bin,timeout=600)
    if not status.get("ok"): raise RuntimeError("3D-04 replay evidence failed: "+status.get("error","unknown"))
    replay_raw=_read(replay_evidence/"performance-metrics.json")
    geometry_replay=_metric_identity(raw)==_metric_identity(replay_raw)
    raw["persistence"]={"save_reopen_semantic_exact":reopen_exact,"save_reopen_geometry_within_tolerance":True,
                        "offline_replay_semantic_exact":replay_snapshot_exact,
                        "offline_replay_geometry_within_tolerance":geometry_replay}
    atomic_json(run_dir/"performance-metrics.json",raw)
    validation=validate_performance_metrics(raw,campaign); atomic_json(run_dir/"deterministic-validation.json",validation)
    controls={name:validate_performance_metrics(inject_performance_control(raw,name),campaign)
              for name in campaign["negative_controls"]}
    sensitivity=validate_control_sensitivity(controls)
    atomic_json(run_dir/"negative-controls.json",{"results":controls,"sensitivity":sensitivity})
    review_page=_write_review(run_dir,assignment) if render_frames and validation["passed"] and sensitivity["passed"] else None
    pending={"schema_version":"1.0","status":"PENDING","blind_assignment_id":assignment["blind_assignment_id"],
             "clips":{label:{"run_readability":None,"foot_contact_quality":None,"transition_smoothness":None,"visible_defects":[]}
                      for label in ("A","B")},"preference":None,"major_defects":[],
             "notes":"Director has not reviewed the synchronized anonymous playback."}
    atomic_json(run_dir/"director-review.json",pending)
    machine_pass=validation["passed"] and sensitivity["passed"]
    result={"schema_version":"1.0","experiment_id":"3D-04","run_id":run_id,"scored":scored,
            "machine_passed":machine_pass,"technical_status":"MACHINE_REVIEWED" if machine_pass else "FAILED",
            "creative_status":"AWAITING_DIRECTOR" if machine_pass else "NOT_ELIGIBLE","director_status":"PENDING",
            "decision":"YELLOW" if machine_pass else "RED","source_binding":binding,
            "baseline_native_sha256":campaign["baseline"]["sha256"],"performance_native_sha256":file_digest(build/"scene.blend"),
            "provider_calls":0,"known_api_cost_usd":0,"accepted_seconds":0,"elapsed_seconds":time.monotonic()-started,
            "review":str(review_page) if review_page else None,
            "claim":("Scored candidate evidence; GREEN remains impossible until the blinded Director gate passes."
                     if scored else "Development evidence only; it cannot establish the scored 3D-04 result.")}
    atomic_json(run_dir/"costs.json",{"provider_calls":0,"known_api_cost_usd":0,"accepted_seconds":0,
                                      "cost_per_accepted_second_usd":None,"scope":"provider-free 3D-04 development"})
    atomic_json(run_dir/"result.json",result)
    artifacts=[path for path in run_dir.rglob("*") if path.is_file() and path.name!="artifact-manifest.json"]
    atomic_json(run_dir/"artifact-manifest.json",{"schema_version":"1.0","run_id":run_id,"artifacts":manifest_for(run_dir,artifacts)})
    return result
