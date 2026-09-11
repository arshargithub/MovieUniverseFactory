"""API-assisted, every-frame closure evidence for the accepted 3D-03 character."""
from __future__ import annotations

import html
import json
import math
import subprocess
import time
import uuid
from pathlib import Path

from PIL import Image,ImageDraw,ImageOps

from .budget import BudgetLedger
from .packages import atomic_json,content_id,file_digest,manifest_for,safe_relative
from .providers.openai_provider import OpenAIProvider
from .validators.character_motion import validate_character_motion


def _read(path): return json.loads(Path(path).read_text())


def _binding(repo):
    status=subprocess.run(["git","status","--porcelain"],cwd=repo,text=True,capture_output=True,check=True).stdout
    return {"schema_version":"1.0","status":"EXACT_PRE_RUN" if not status else "DIRTY_DEVELOPMENT",
            "implementation_commit":subprocess.run(["git","rev-parse","HEAD"],cwd=repo,text=True,capture_output=True,check=True).stdout.strip(),
            "implementation_tree":subprocess.run(["git","rev-parse","HEAD^{tree}"],cwd=repo,text=True,capture_output=True,check=True).stdout.strip(),
            "worktree_clean_before_dispatch":not bool(status)}


def _contact_sheet(frames:list[Path],output:Path,clip:str):
    columns=6; cell_w,cell_h,label_h=320,180,24; rows=math.ceil(len(frames)/columns)
    canvas=Image.new("RGB",(columns*cell_w,rows*(cell_h+label_h)),"#181818"); draw=ImageDraw.Draw(canvas)
    for index,path in enumerate(frames):
        row,column=divmod(index,columns)
        with Image.open(path) as source: frame=ImageOps.fit(source.convert("RGB"),(cell_w,cell_h))
        x,y=column*cell_w,row*(cell_h+label_h); canvas.paste(frame,(x,y+label_h))
        draw.text((x+7,y+5),f"{clip} — frame {int(path.stem.split('-')[-1])}",fill="white")
    canvas.save(output,format="PNG",optimize=True)


def _metric_summary(raw):
    result={}
    for clip,item in raw["clips"].items():
        rows=[]
        for frame in item["frames"]:
            step=frame["step_from_previous"] or {"max_vertex_m":0,"rms_vertex_m":0}
            rows.append({"frame":frame["frame"],"bottom_z_m":round(frame["bounds"]["min"][2],5),
                         "left_foot_z_m":round(frame["foot_min_z_m"]["left"],5),
                         "right_foot_z_m":round(frame["foot_min_z_m"]["right"],5),
                         "height_m":round(frame["bounds"]["dimensions"][2],5),
                         "max_vertex_step_m":round(step["max_vertex_m"],5),
                         "rms_vertex_step_m":round(step["rms_vertex_m"],5)})
        result[clip]={"frames":rows,"loop_seam":item["loop_seam"]}
    return result


def _review_prompt(raw,validation):
    return """You are a conservative secondary motion-quality evaluator for a bounded 3D feasibility test.
The three attached contact sheets contain every frame, in order, for idle, run, and jump. Frame numbers are printed above each cell. Inspect every cell rather than judging only representative poses.

For each clip, decide whether its named motion is immediately readable, grounding is visually plausible, and the low-poly mesh is free of major deformation. Look closely at feet, ankles, knees, hands, elbows, shoulder attachment, torso continuity, takeoff, airborne pose, landing, and the seam between the final and first frames. Record each issue against a visible frame number. Minor low-poly faceting may receive a minor finding; stretched, inverted, detached, penetrating, sliding, or physically impossible anatomy is major or critical. A jump must visibly include takeoff, an airborne phase, and landing. Do not infer motion that the ordered frames do not show.

This output is only an additional screen. It cannot overrule deterministic failures or replace Director playback review. Use overall_recommendation=fail for any critical finding or clearly incorrect named motion, director_review for material ambiguity, and pass only when all three complete sequences are readable and have no major defect.

Deterministic validation result and compact per-frame measurements follow:
"""+json.dumps({"validation":validation,"measurements":_metric_summary(raw)},sort_keys=True,separators=(",",":"))


def _validate_api_screen(data,config):
    if not data: return {"passed":False,"errors":["provider_output_missing"]}
    errors=[]; reviews=data.get("clip_reviews",[])
    if {item.get("clip") for item in reviews}!={"idle","run","jump"} or len(reviews)!=3: errors.append("clip_set")
    if data.get("overall_recommendation")!="pass": errors.append("recommendation")
    if data.get("confidence",0)<config["pass_confidence"]: errors.append("confidence")
    if data.get("critical_findings"): errors.append("critical_findings")
    for item in reviews:
        if item.get("motion_readability")!="clear": errors.append(item.get("clip","unknown")+".readability")
        if not item.get("grounding_plausible"): errors.append(item.get("clip","unknown")+".grounding")
        if any(finding.get("severity") in {"major","critical"} for finding in item.get("findings",[])):
            errors.append(item.get("clip","unknown")+".major_finding")
    return {"passed":not errors,"errors":sorted(set(errors)),"authority":"secondary_perceptual_screen",
            "can_override_deterministic_failure":False,"can_replace_director":False}


def _write_review_html(output,config,result):
    panels=[]
    for clip,spec in config["request"]["clips"].items():
        frames=[f"worker/frames/{clip}/frame-{frame:04d}.png" for frame in range(spec["frame_start"],spec["frame_end"]+1)]
        fps=config.get("playback_fps_by_clip",{}).get(clip,config["playback_fps"])
        label="Jump source pose reference (not a complete jump)" if clip=="jump" and config.get("jump_claim")=="source_pose_reference_only" else clip.title()
        loop=clip in {"idle","run"}
        panels.append(f'''<section data-clip="{clip}" data-loop="{str(loop).lower()}" data-fps="{fps}" data-frames='{html.escape(json.dumps(frames),quote=True)}'>
<h2>{label} · {fps} fps</h2><img class="player" src="{frames[0]}" alt="{clip} animation frame">
<div><button type="button">Pause</button> <label>Frame <input type="range" min="0" max="{len(frames)-1}" value="0"></label> <output>{spec["frame_start"]}</output></div>
<p><a href="contact-sheet-{clip}.png">Open complete {clip} contact sheet</a></p></section>''')
    safe=html.escape(json.dumps(result,indent=2,sort_keys=True))
    document=f'''<!doctype html><meta charset="utf-8"><title>3D-03 temporal review</title>
<style>body{{font:16px system-ui;margin:2rem;background:#181818;color:#eee}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:1.5rem}}section{{background:#242424;padding:1rem;border-radius:.5rem}}img{{width:100%;background:#333}}input{{width:55%}}a{{color:#8fc7ff}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}.pending{{color:#ffd479}}</style>
<h1>3D-03 complete motion review</h1><p class="pending">Review every complete clip at least once. API screening is advisory; Director acceptance is still required.</p>
<main>{''.join(panels)}</main><h2>Recorded evidence</h2><pre>{safe}</pre>
<script>document.querySelectorAll('section[data-clip]').forEach(panel=>{{const frames=JSON.parse(panel.dataset.frames),img=panel.querySelector('img'),slider=panel.querySelector('input'),out=panel.querySelector('output'),button=panel.querySelector('button'),loop=panel.dataset.loop==='true',autoCount=loop?frames.length-1:frames.length;let index=0,playing=true;const show=i=>{{index=Number(i);img.src=frames[index];slider.value=index;out.value=index+1}};slider.oninput=()=>{{playing=false;button.textContent='Play';show(slider.value)}};button.onclick=()=>{{playing=!playing;button.textContent=playing?'Pause':'Play'}};setInterval(()=>{{if(playing)show((index+1)%autoCount)}},1000/Number(panel.dataset.fps));}});</script>'''
    (output/"review.html").write_text(document)


def run_character_motion_addendum(repo:Path,source_run:Path,output_root:Path,blender_bin:str,settings:dict,live:bool)->dict:
    from .adapters.blender.runner import run_blender
    config=_read(repo/"feasibility/3d/3d-03/temporal-validation.json")
    source_run=safe_relative(repo,source_run.resolve()); output_root=output_root.resolve()
    if source_run.name!=config["accepted_source_run"]: raise ValueError("Temporal addendum requires the frozen accepted 3D-03 run")
    source_result=_read(source_run/"result.json")
    if source_result.get("director_status")!="ACCEPTED": raise ValueError("Source 3D-03 run lacks Director acceptance")
    native=source_run/"initial/build/scene.blend"
    if file_digest(native)!=config["source_native_sha256"] or source_result.get("parent_sha256")!=config["source_native_sha256"]:
        raise ValueError("Temporal addendum source native identity mismatch")
    run_id=f"motion-v1-{time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())}-{uuid.uuid4().hex[:8]}"
    output=output_root/run_id; output.mkdir(parents=True,exist_ok=False)
    binding=_binding(repo)
    package={"schema_version":"1.0","package_kind":"immutable_work_package","experiment_id":"3D-03-TEMPORAL",
             "run_id":run_id,"source_run":source_run.name,"source_native_sha256":config["source_native_sha256"],
             "configuration_sha256":content_id(config),"request":config["request"],"playback_profile":config["playback_profile"],
             "authority":{"blender":"trusted_temporal_inspection","provider":"secondary_screen_only","director":"required"}}
    package["package_id"]=content_id(package)
    atomic_json(output/"work-package.json",package); atomic_json(output/"source-binding.json",binding); atomic_json(output/"frozen-config.json",config)
    worker=output/"worker"
    status=run_blender({"mode":"character_temporal","output_dir":str(worker),"seed":303,
                        "profile":config["playback_profile"],"parent_native":str(native),"request":config["request"]},
                       blender_bin=blender_bin,timeout=1800)
    if not status.get("ok"): raise RuntimeError("Temporal Blender inspection failed: "+status.get("error","unknown"))
    raw=_read(worker/"temporal-metrics.json")
    if raw.get("source_native_sha256")!=config["source_native_sha256"]: raise ValueError("Worker inspected an unexpected native file")
    deterministic=validate_character_motion(raw,config); atomic_json(output/"deterministic-validation.json",deterministic)
    sheets=[]
    for clip,spec in config["request"]["clips"].items():
        frames=[worker/"frames"/clip/f"frame-{frame:04d}.png" for frame in range(spec["frame_start"],spec["frame_end"]+1)]
        if not all(path.is_file() for path in frames): raise ValueError("Temporal render frame coverage is incomplete")
        sheet=output/f"contact-sheet-{clip}.png"; _contact_sheet(frames,sheet,clip); sheets.append(sheet)
    provider_result=None; api_screen={"passed":False,"errors":["NOT_RUN"],"authority":"secondary_perceptual_screen"}
    if live and deterministic["passed"]:
        evaluator=config["evaluator"]
        if evaluator["maximum_call_count"]!=1: raise ValueError("Temporal evaluator call count is not frozen at one")
        provider_settings=dict(settings); provider_settings.update({"MF_VISION_MODEL":evaluator["model"],
            "MF_VISION_REASONING_EFFORT":evaluator["reasoning_effort"],"MF_IMAGE_DETAIL":evaluator["image_detail"],"MF_COST_SCOPE":"scored"})
        ledger=BudgetLedger(repo/"results/budget.jsonl",campaign_limit=40)
        provider=OpenAIProvider(provider_settings,ledger,output/"provider")
        provider_result=provider.generate_json(purpose="3d03_temporal_visual_screen",prompt=_review_prompt(raw,deterministic),
            schema=_read(repo/"schemas/character-motion-review.schema.json"),images=sheets,run_id=run_id,stage="initial",
            max_output_tokens=evaluator["max_output_tokens"])
        atomic_json(output/"provider-result.json",provider_result)
        if provider_result.get("cost_usd") is not None and provider_result["cost_usd"]>evaluator["maximum_known_cost_usd"]:
            api_screen={"passed":False,"errors":["recorded_cost_exceeded_frozen_addendum_cap"],"authority":"secondary_perceptual_screen"}
        else: api_screen=_validate_api_screen(provider_result.get("data"),evaluator)
    elif live:
        api_screen={"passed":False,"errors":["deterministic_gate_failed"],
                    "authority":"secondary_perceptual_screen","provider_calls":0}
    deterministic_pass=deterministic["passed"]
    screened=api_screen["passed"] if live else False
    result={"schema_version":"1.0","experiment_id":"3D-03-TEMPORAL","run_id":run_id,"source_run":source_run.name,
            "source_native_sha256":config["source_native_sha256"],"source_binding":binding,"work_package_id":package["package_id"],
            "deterministic_validation":deterministic,"api_screening":api_screen,"provider_calls":[provider_result] if provider_result else [],
            "known_api_cost_usd":provider_result.get("cost_usd") if provider_result else 0,
            "technical_status":"MACHINE_REVIEWED" if deterministic_pass else "FAILED",
            "creative_status":"AWAITING_DIRECTOR" if deterministic_pass and screened else "NOT_ELIGIBLE",
            "director_status":"PENDING","decision":"YELLOW" if deterministic_pass and screened else "RED",
            "claim":"Complete idle, run, and jump motion remains unqualified until deterministic, API-screening, and Director gates all pass.",
            "evidence_hierarchy":["deterministic_every_frame_checks","secondary_api_screen","director_full_playback_acceptance"]}
    atomic_json(output/"result.json",result)
    atomic_json(output/"director-review.json",{"status":"PENDING","accepted":None,"clips":{},"notes":"Director has not reviewed all three complete clips."})
    _write_review_html(output,config,result)
    artifacts=[path for path in output.rglob("*") if path.is_file() and path.name!="artifact-manifest.json"]
    atomic_json(output/"artifact-manifest.json",{"schema_version":"1.0","run_id":run_id,"artifacts":manifest_for(output,artifacts)})
    return {**result,"review":str(output/"review.html")}


def run_character_motion_031(repo:Path,source_run:Path,output_root:Path,blender_bin:str)->dict:
    """Provider-free production evidence for the corrected transfer implementation."""
    from .adapters.blender.runner import run_blender
    source_run=safe_relative(repo,source_run.resolve()); output_root=output_root.resolve()
    source_result=_read(source_run/"result.json"); native=source_run/"initial/build/scene.blend"
    config_name="temporal-validation-authored.json" if source_result.get("experiment_id")=="3D-03.1" else "temporal-validation.json"
    config=_read(repo/"feasibility/3d/3d-03-1"/config_name)
    if not source_result.get("passed") or source_result.get("parent_sha256")!=file_digest(native):
        raise ValueError("3D-03.1 motion validation requires a machine-passed source run with matching native identity")
    run_id=f"motion-v2-{time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())}-{uuid.uuid4().hex[:8]}"
    output=output_root/run_id; output.mkdir(parents=True,exist_ok=False)
    binding=_binding(repo); native_sha=file_digest(native)
    package={"schema_version":"1.0","package_kind":"immutable_work_package","experiment_id":"3D-03.1-TEMPORAL",
             "run_id":run_id,"source_run":source_run.name,"source_native_sha256":native_sha,
             "configuration_sha256":content_id(config),"request":config["request"],"playback_profile":config["playback_profile"],
             "authority":{"blender":"trusted_temporal_inspection","provider_calls":0,"director":"required_for_idle_and_run"}}
    package["package_id"]=content_id(package)
    atomic_json(output/"work-package.json",package); atomic_json(output/"source-binding.json",binding); atomic_json(output/"frozen-config.json",config)
    worker=output/"worker"
    status=run_blender({"mode":"character_temporal","output_dir":str(worker),"seed":303,
                        "profile":config["playback_profile"],"parent_native":str(native),"request":config["request"]},
                       blender_bin=blender_bin,timeout=1800)
    if not status.get("ok"): raise RuntimeError("3D-03.1 temporal inspection failed: "+status.get("error","unknown"))
    raw=_read(worker/"temporal-metrics.json")
    if raw.get("source_native_sha256")!=native_sha: raise ValueError("Worker inspected an unexpected 3D-03.1 native file")
    deterministic=validate_character_motion(raw,config); atomic_json(output/"deterministic-validation.json",deterministic)
    for clip,spec in config["request"]["clips"].items():
        frames=[worker/"frames"/clip/f"frame-{frame:04d}.png" for frame in range(spec["frame_start"],spec["frame_end"]+1)]
        if not all(path.is_file() for path in frames): raise ValueError("3D-03.1 temporal render coverage is incomplete")
        _contact_sheet(frames,output/f"contact-sheet-{clip}.png",clip)
    full_jump=config.get("jump_claim")=="authored_full_jump"
    shared_errors={name for name in deterministic["errors"] if not name.startswith("jump.")}
    idle_run_pass=not shared_errors
    jump_pass=full_jump and not any(name.startswith("jump.") for name in deterministic["errors"])
    machine_pass=deterministic["passed"] if full_jump else idle_run_pass
    result={"schema_version":"1.0","experiment_id":"3D-03.1-TEMPORAL","run_id":run_id,
            "source_run":source_run.name,"source_native_sha256":native_sha,"source_binding":binding,
            "work_package_id":package["package_id"],"deterministic_validation":deterministic,
            "idle_run_machine_pass":idle_run_pass,"jump_full_motion_pass":jump_pass,
            "jump_status":"MACHINE_REVIEWED_AUTHORED_MOTION" if jump_pass else "FAILED" if full_jump else "SOURCE_POSE_REFERENCE_ONLY",
            "provider_calls":[],"known_api_cost_usd":0,
            "technical_status":"MACHINE_REVIEWED" if machine_pass else "FAILED",
            "creative_status":"AWAITING_DIRECTOR" if machine_pass else "NOT_ELIGIBLE",
            "director_status":"PENDING","decision":"YELLOW" if machine_pass else "RED",
            "claim":("Corrected idle/run transfer and separately labelled authored jump pass every-frame machine validation; Director full-playback review remains required."
                     if machine_pass and full_jump else "Corrected faithful transfer is machine-qualified for idle and run only. The admitted jump FBX is a pose reference and does not qualify complete jump motion.")}
    atomic_json(output/"result.json",result)
    clips={"idle":None,"run":None,"jump":None} if full_jump else {"idle":None,"run":None}
    notes=("Review complete idle, run, and separately authored jump playback." if full_jump else
           "Review complete idle and run playback. Jump is shown only to document the admitted source limitation.")
    atomic_json(output/"director-review.json",{"status":"PENDING","accepted":None,"clips":clips,"notes":notes})
    _write_review_html(output,config,result)
    artifacts=[path for path in output.rglob("*") if path.is_file() and path.name!="artifact-manifest.json"]
    atomic_json(output/"artifact-manifest.json",{"schema_version":"1.0","run_id":run_id,"artifacts":manifest_for(output,artifacts)})
    return {**result,"review":str(output/"review.html")}
