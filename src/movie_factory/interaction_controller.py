"""Provider-free 3D-05 interaction campaign controller."""
from __future__ import annotations

import html
import json
import shutil
import subprocess
import time
import uuid
from copy import deepcopy
from pathlib import Path

from .packages import atomic_json, content_id, file_digest, manifest_for, safe_relative
from .validators.interaction import (CONTROL_EXPECTATIONS, interaction_protected_flags,
                                     validate_control_sensitivity, validate_interaction_metrics)
from .validators.structural import compare_snapshots


def _read(path):
    return json.loads(Path(path).read_text())


def _source_binding(repo):
    status = subprocess.run(["git", "status", "--porcelain"], cwd=repo, text=True, capture_output=True, check=True).stdout
    return {
        "schema_version": "1.0", "status": "EXACT_PRE_RUN" if not status else "DIRTY_DEVELOPMENT",
        "implementation_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True, check=True).stdout.strip(),
        "implementation_tree": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=repo, text=True, capture_output=True, check=True).stdout.strip(),
        "worktree_clean_before_dispatch": not bool(status),
    }


def _metric_identity(raw):
    value = deepcopy(raw)
    value.pop("protected", None)
    value.pop("persistence", None)
    return content_id(value)


def _blind_assignment(package_id):
    candidate_first = int(package_id[:2], 16) % 2 == 0
    labels = {"A": "candidate", "B": "baseline"} if candidate_first else {"A": "baseline", "B": "candidate"}
    payload = {"schema_version": "1.0", "package_id": package_id, "labels": labels}
    payload["blind_assignment_id"] = content_id(payload)
    return payload


def _script_json(value):
    return (json.dumps(value, separators=(",", ":"), ensure_ascii=False)
            .replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def _write_review(run_dir, assignment, views):
    review = run_dir/"review"
    for label, role in assignment["labels"].items():
        for view in views:
            target = review/"frames"/label/view
            target.mkdir(parents=True, exist_ok=True)
            sources = sorted((run_dir/"evidence"/"frames"/role/view).glob("frame-*.png"))
            if [source.name for source in sources] != [f"frame-{frame:04d}.png" for frame in range(1, 97)]:
                raise ValueError(f"Incomplete {role}/{view} playback evidence")
            for source in sources:
                shutil.copy2(source, target/source.name)
    frame_sets = {label: {view: [f"frames/{label}/{view}/frame-{frame:04d}.png" for frame in range(1, 97)]
                          for view in views} for label in ("A", "B")}
    panels = "".join(f'<section><h2>Clip {label} — {view.title()} view</h2><img data-label="{label}" data-view="{view}" src="{frame_sets[label][view][0]}"></section>'
                     for label in ("A", "B") for view in views)
    page = f'''<!doctype html><meta charset="utf-8"><title>3D-05 blinded interaction review</title>
<style>body{{font:16px system-ui;margin:2rem;background:#171717;color:#eee}}main{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}section{{background:#242424;padding:1rem;border-radius:.5rem}}img{{width:100%;background:#333}}input{{width:min(760px,72vw)}}.notice{{color:#ffd479}}</style>
<h1>3D-05 anonymous A/B sword-pickup review</h1><p class="notice">Watch all 96 synchronized frames in all three views. One clip advances the grasp, lift, and hold by four frames inside the frozen edit interval.</p>
<p><button id="toggle">Pause</button> <label>Frame <input id="frame" type="range" min="0" max="95" value="0"></label> <output id="number">1</output></p>
<p id="loading">Loading complete playback…</p><p>Visible-page time after loading: <output id="review-seconds">0</output> seconds. Use this as an estimate when reporting your review duration.</p><main>{panels}</main><h2>Frozen questions</h2><ol><li>Interaction readability for A and B, 1–5 in 0.5 increments.</li><li>Grasp/contact believability for A and B.</li><li>Attachment and transition smoothness for A and B.</li><li>Hold stability and sword/body clearance for A and B.</li><li>Concrete visible defects and overall preference.</li><li>Record total review time in seconds.</li></ol>
<script>const frames={_script_json(frame_sets)},images=[...document.querySelectorAll('img[data-label]')],slider=document.querySelector('#frame'),number=document.querySelector('#number'),button=document.querySelector('#toggle');let index=0,playing=false,ready=false;button.disabled=true;slider.disabled=true;const cached=[];let loaded=0;const urls=Object.values(frames).flatMap(views=>Object.values(views).flat());Promise.all(urls.map(url=>new Promise((resolve,reject)=>{{const im=new Image();cached.push(im);im.onload=()=>{{document.querySelector('#loading').textContent=`Loading ${{++loaded}}/${{urls.length}}`;resolve()}};im.onerror=()=>reject(new Error(url));im.src=url}}))).then(()=>{{ready=true;playing=true;button.disabled=false;slider.disabled=false;document.querySelector('#loading').textContent='Complete playback ready: 96 frames at 24 fps. Replay resets to the starting pose.'}}).catch(()=>{{document.querySelector('#loading').textContent='Playback failed to load. Use the verified video copies; do not score a still frame.'}});function show(value){{index=Number(value);images.forEach(image=>image.src=frames[image.dataset.label][image.dataset.view][index]);slider.value=index;number.value=index+1}}slider.oninput=()=>{{playing=false;button.textContent='Play';show(slider.value)}};button.onclick=()=>{{playing=!playing;button.textContent=playing?'Pause':'Play'}};setInterval(()=>{{if(playing)show((index+1)%96)}},1000/24);let visibleSeconds=0;setInterval(()=>{{if(ready&&!document.hidden)document.querySelector('#review-seconds').value=++visibleSeconds}},1000);</script>'''
    (review/"index.html").write_text(page)
    return review/"index.html"


def _resolved_scene(repo, scene):
    value = deepcopy(scene)
    source = safe_relative(repo, repo/".runtime/assets/3d-02/staged-v1"/value["sword"]["source"]["path"])
    if not source.is_file() or file_digest(source) != value["sword"]["source"]["sha256"]:
        raise ValueError("3D-05 sword asset hash mismatch")
    value["sword"]["source"]["path"] = str(source.resolve())
    return value


def _checkpoint_equal(first, second):
    return content_id(first) == content_id(second)


def _validate_frozen_inputs(campaign, scene, revision, profile):
    frozen = campaign.get("scored_source_binding") or {}
    if content_id(scene) != frozen.get("scene_sha256"):
        raise ValueError("3D-05 scene differs from the frozen input")
    if content_id(revision) != frozen.get("revision_sha256"):
        raise ValueError("3D-05 revision differs from the frozen input")
    if profile != campaign.get("render_profile"):
        raise ValueError("3D-05 render profile differs from the frozen input")


def run_interaction_05(repo: Path, output_root: Path, profile: dict, blender_bin: str,
                       render_frames: bool = True, scored: bool = False, configuration_dir: Path | None = None) -> dict:
    from .adapters.blender.runner import run_blender
    inputs = safe_relative(repo, configuration_dir or repo/"feasibility/3d/3d-05")
    campaign = _read(inputs/"campaign.json")
    revision = _read(inputs/"revision.json")
    scene_source = _read(inputs/"scene.json")
    campaign_digest = content_id(campaign)
    if campaign_digest != (inputs/"campaign.sha256").read_text().strip():
        raise ValueError("3D-05 campaign digest mismatch")
    baseline = safe_relative(repo, repo/campaign["baseline"]["character_relative_path"])
    if not baseline.is_file() or file_digest(baseline) != campaign["baseline"]["character_sha256"]:
        raise ValueError("3D-05 character baseline hash mismatch")
    staged_manifest = repo/".runtime/assets/3d-02/staged-v1/staged-manifest.json"
    if not staged_manifest.is_file() or file_digest(staged_manifest) != campaign["baseline"]["sword_staged_manifest_sha256"]:
        raise ValueError("3D-05 staged sword manifest hash mismatch")
    scene = _resolved_scene(repo, scene_source)
    binding = _source_binding(repo)
    if scored:
        frozen = campaign.get("scored_source_binding") or {}
        if campaign.get("campaign_status") != "FROZEN_FOR_SCORED_CAMPAIGN" or not binding["worktree_clean_before_dispatch"]:
            raise ValueError("A scored 3D-05 run requires the frozen campaign and a clean worktree")
        if campaign.get("acceptance_version") == "3d05-closure-v1":
            _validate_frozen_inputs(campaign, scene_source, revision, profile)
        source_change = subprocess.run(["git", "diff", "--quiet", frozen.get("implementation_commit", ""), "HEAD", "--", "src", "tests"], cwd=repo)
        if source_change.returncode != 0:
            raise ValueError("3D-05 implementation differs from the frozen source commit")
        if not render_frames:
            raise ValueError("A scored 3D-05 run requires complete playback evidence")
    run_id = f"interaction-v1-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:8]}"
    run_dir = output_root/run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    package = {
        "schema_version": "1.0", "package_kind": "immutable_work_package", "experiment_id": "3D-05", "run_id": run_id,
        "campaign_sha256": campaign_digest, "scene_sha256": content_id(scene_source), "revision_sha256": content_id(revision),
        "character_native_sha256": campaign["baseline"]["character_sha256"], "sword_asset_sha256": campaign["baseline"]["sword_asset_sha256"],
        "source_binding": binding, "render_profile": profile, "provider_budget": campaign["provider_budget"],
    }
    package["package_id"] = content_id(package)
    assignment = _blind_assignment(package["package_id"])
    for path, value in ((run_dir/"frozen-campaign.json", campaign), (run_dir/"scene.json", scene_source),
                        (run_dir/"revision.json", revision), (run_dir/"work-package.json", package),
                        (run_dir/"source-binding.json", binding), (run_dir/"blind-key.json", assignment)):
        atomic_json(path, value)
    started = time.monotonic()
    build = run_dir/"build"
    status = run_blender({"mode": "build_interaction", "output_dir": str(build.resolve()), "seed": 305, "profile": profile,
                          "parent_native": str(baseline.resolve()), "interaction": scene, "role": "candidate"}, blender_bin=blender_bin, timeout=600)
    if not status.get("ok"):
        raise RuntimeError("3D-05 build failed: "+status.get("error", "unknown"))
    if scored:
        frozen = campaign["scored_source_binding"]
        toolchain = status.get("toolchain", {})
        if toolchain.get("blender") != frozen["blender_version"] or toolchain.get("build_hash") != frozen["blender_build_hash"]:
            raise ValueError("3D-05 Blender build differs from the frozen campaign")
    parent_snapshot = _read(baseline.with_name("snapshot.json"))
    build_snapshot = _read(build/"snapshot.json")
    protected = interaction_protected_flags(parent_snapshot, build_snapshot)
    reopen = run_dir/"reopen"
    status = run_blender({"mode": "inspect", "output_dir": str(reopen.resolve()), "seed": 305, "profile": profile,
                          "parent_native": str((build/"scene.blend").resolve())}, blender_bin=blender_bin, timeout=300)
    if not status.get("ok"):
        raise RuntimeError("3D-05 reopen failed: "+status.get("error", "unknown"))
    reopen_exact = compare_snapshots(build_snapshot, _read(reopen/"snapshot.json"))["passed"]
    checkpoint_results = []
    for role, frames in campaign["sampling"]["checkpoints"].items():
        for frame in frames:
            name = f"{role}-{str(frame).replace('.', '_')}"
            checkpoint_dir = run_dir/"checkpoints"/name
            status = run_blender({"mode": "interaction_checkpoint", "output_dir": str(checkpoint_dir.resolve()), "seed": 305,
                                  "profile": profile, "parent_native": str((build/"scene.blend").resolve()), "role": role, "frame": frame},
                                 blender_bin=blender_bin, timeout=300)
            if not status.get("ok"):
                raise RuntimeError("3D-05 checkpoint failed: "+status.get("error", "unknown"))
            reopened_dir = run_dir/"checkpoints-reopen"/name
            status = run_blender({"mode": "interaction_checkpoint", "output_dir": str(reopened_dir.resolve()), "seed": 305,
                                  "profile": profile, "parent_native": str((checkpoint_dir/"scene.blend").resolve()), "role": role, "frame": frame},
                                 blender_bin=blender_bin, timeout=300)
            if not status.get("ok"):
                raise RuntimeError("3D-05 checkpoint reopen failed: "+status.get("error", "unknown"))
            checkpoint_results.append({"role": role, "frame": frame,
                                       "exact": _checkpoint_equal(_read(checkpoint_dir/"checkpoint.json"), _read(reopened_dir/"checkpoint.json"))})
    evidence = run_dir/"evidence"
    status = run_blender({"mode": "interaction_evidence", "output_dir": str(evidence.resolve()), "seed": 305, "profile": profile,
                          "parent_native": str((build/"scene.blend").resolve()), "campaign": campaign, "render_frames": render_frames},
                         blender_bin=blender_bin, timeout=2400)
    if not status.get("ok"):
        raise RuntimeError("3D-05 evidence failed: "+status.get("error", "unknown"))
    raw = _read(evidence/"interaction-metrics.json")
    replay_build = run_dir/"replay"/"build"
    status = run_blender({"mode": "build_interaction", "output_dir": str(replay_build.resolve()), "seed": 305, "profile": profile,
                          "parent_native": str(baseline.resolve()), "interaction": scene, "role": "candidate"}, blender_bin=blender_bin, timeout=600)
    if not status.get("ok"):
        raise RuntimeError("3D-05 replay build failed: "+status.get("error", "unknown"))
    replay_snapshot_exact = compare_snapshots(build_snapshot, _read(replay_build/"snapshot.json"))["passed"]
    replay_evidence = run_dir/"replay"/"evidence"
    status = run_blender({"mode": "interaction_evidence", "output_dir": str(replay_evidence.resolve()), "seed": 305, "profile": profile,
                          "parent_native": str((replay_build/"scene.blend").resolve()), "campaign": campaign, "render_frames": False},
                         blender_bin=blender_bin, timeout=600)
    if not status.get("ok"):
        raise RuntimeError("3D-05 replay evidence failed: "+status.get("error", "unknown"))
    raw["protected"] = protected
    raw["persistence"] = {
        "checkpoints_exact": bool(checkpoint_results) and all(item["exact"] for item in checkpoint_results),
        "save_reopen_semantic_exact": reopen_exact,
        "offline_replay_semantic_exact": replay_snapshot_exact,
        "offline_replay_geometry_within_tolerance": _metric_identity(raw) == _metric_identity(_read(replay_evidence/"interaction-metrics.json")),
    }
    atomic_json(run_dir/"checkpoint-validation.json", {"schema_version": "1.0", "results": checkpoint_results,
                                                       "passed": all(item["exact"] for item in checkpoint_results)})
    atomic_json(run_dir/"interaction-metrics.json", raw)
    validation = validate_interaction_metrics(raw, campaign)
    atomic_json(run_dir/"deterministic-validation.json", validation)
    control_results = {}
    for control in campaign["negative_controls"]:
        control_build = run_dir/"controls"/control/"build"
        status = run_blender({"mode": "build_interaction_control", "output_dir": str(control_build.resolve()), "seed": 305,
                              "profile": profile, "parent_native": str(baseline.resolve()), "interaction": scene,
                              "role": "candidate", "control": control}, blender_bin=blender_bin, timeout=600)
        if not status.get("ok"):
            raise RuntimeError(f"3D-05 {control} build failed: "+status.get("error", "unknown"))
        control_evidence = run_dir/"controls"/control/"evidence"
        status = run_blender({"mode": "interaction_evidence", "output_dir": str(control_evidence.resolve()), "seed": 305,
                              "profile": profile, "parent_native": str((control_build/"scene.blend").resolve()),
                              "campaign": campaign, "render_frames": False}, blender_bin=blender_bin, timeout=600)
        if not status.get("ok"):
            raise RuntimeError(f"3D-05 {control} evidence failed: "+status.get("error", "unknown"))
        controlled = _read(control_evidence/"interaction-metrics.json")
        controlled["protected"] = interaction_protected_flags(parent_snapshot, _read(control_build/"snapshot.json"))
        controlled["persistence"] = {name: True for name in ("checkpoints_exact", "save_reopen_semantic_exact",
                                                              "offline_replay_semantic_exact", "offline_replay_geometry_within_tolerance")}
        control_results[control] = validate_interaction_metrics(controlled, campaign)
        atomic_json(run_dir/"controls"/control/"validation.json", control_results[control])
    sensitivity = validate_control_sensitivity(control_results, coordinated=bool(campaign.get("motion_thresholds")), positive_result=validation, surface_ownership=bool(campaign.get("surface_ownership_thresholds")))
    atomic_json(run_dir/"control-sensitivity.json", sensitivity)
    machine_passed = validation["passed"] and sensitivity["passed"]
    review_page = _write_review(run_dir, assignment, campaign["director_gate"]["views"]) if render_frames and machine_passed else None
    pending = {"schema_version": "1.0", "status": "PENDING", "blind_assignment_id": assignment["blind_assignment_id"],
               "clips": {label: {"interaction_readability": None, "grasp_contact_believability": None,
                                  "transition_smoothness": None, "hold_clearance": None, "visible_defects": []}
                         for label in ("A", "B")}, "preference": None, "major_defects": [],
               "notes": "Director has not reviewed complete synchronized playback.", "review_seconds": None}
    atomic_json(run_dir/"director-review.json", pending)
    result = {"schema_version": "1.0", "experiment_id": "3D-05", "run_id": run_id, "scored": scored,
              "machine_passed": machine_passed, "technical_status": "MACHINE_REVIEWED" if machine_passed else "FAILED",
              "creative_status": "AWAITING_DIRECTOR" if machine_passed else "NOT_ELIGIBLE",
              "director_status": "PENDING", "decision": "YELLOW" if machine_passed else "RED",
              "source_binding": binding, "interaction_native_sha256": file_digest(build/"scene.blend"),
              "provider_calls": 0, "known_api_cost_usd": 0.0, "accepted_seconds": 0,
              "elapsed_seconds": time.monotonic()-started, "director_review_seconds": None,
              "review": str(review_page) if review_page else None,
              "claim": "Scripted kinematic pickup qualification pending Director review." if machine_passed else "3D-05 deterministic qualification failed."}
    atomic_json(run_dir/"costs.json", {"provider_calls": 0, "known_api_cost_usd": 0.0, "accepted_seconds": 0,
                                      "cost_per_accepted_interaction_usd": None, "director_review_seconds": None,
                                      "scope": "provider-free 3D-05 engineering and review"})
    atomic_json(run_dir/"result.json", result)
    artifacts = [path for path in run_dir.rglob("*") if path.is_file() and path.name != "artifact-manifest.json"]
    atomic_json(run_dir/"artifact-manifest.json", {"schema_version": "1.0", "run_id": run_id,
                                                   "artifacts": manifest_for(run_dir, artifacts)})
    return result
