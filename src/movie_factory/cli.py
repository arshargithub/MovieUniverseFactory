from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .controller import run_pair, unique_run_id
from .doctor import collect as doctor_collect
from .packages import atomic_json, content_id, file_digest, safe_relative
from .reporting import write_campaign_report
from .schema import validate


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_json(path: Path):
    return json.loads(path.read_text())


def load_settings_safe(root: Path):
    try:
        from .settings import load_settings
        return load_settings(root)
    except ImportError:
        return {"BLENDER_BIN":"/Applications/Blender.app/Contents/MacOS/Blender"}


def emit(value, output: Path | None = None):
    if output:
        atomic_json(output, value)
    print(json.dumps(value, indent=2, sort_keys=True))


DIRECTOR_DIMENSIONS = {
    "brief_fulfillment", "cinematography", "lighting_materials",
    "physical_finish", "continuity_revision",
}


def normalize_director_review(review):
    required={"reviewer","accepted","scores","notes"}
    if not required.issubset(review): raise ValueError(f"review missing {sorted(required-set(review))}")
    if not isinstance(review["reviewer"],str) or not review["reviewer"].strip(): raise ValueError("reviewer must be a non-empty label")
    if type(review["accepted"]) is not bool or not isinstance(review["notes"],str): raise ValueError("accepted must be boolean and notes must be text")
    scores=review["scores"]
    if isinstance(scores,dict): scores=[{"dimension":dimension,"score":score} for dimension,score in scores.items()]
    if not isinstance(scores,list) or len(scores)!=5 or {item.get("dimension") for item in scores if isinstance(item,dict)}!=DIRECTOR_DIMENSIONS:
        raise ValueError("review must score each Director dimension exactly once")
    def valid_director_score(item):
        score=item.get("score")
        return type(score) in {int,float} and 1<=score<=5 and score*2==int(score*2)
    if any(not valid_director_score(item) for item in scores):
        raise ValueError("Director scores must be half-point increments from 1 to 5")
    mean=sum(item["score"] for item in scores)/5
    hands_on=bool(review.get("hands_on_edits",False))
    if review["accepted"] and (mean<4 or min(item["score"] for item in scores)<3 or hands_on):
        raise ValueError("accepted review does not meet the Director gate")
    return {**review,"scores":scores,"mean_score":mean,"hands_on_edits":hands_on,
            "status":"ACCEPTED" if review["accepted"] else "REJECTED",
            "reviewed_at":review.get("reviewed_at") or datetime.now(timezone.utc).isoformat()}


def command_doctor(args) -> int:
    root = repo_root(); settings = load_settings_safe(root)
    result = doctor_collect(root, settings.get("BLENDER_BIN", "/Applications/Blender.app/Contents/MacOS/Blender"), settings)
    emit(result, args.output)
    return 0 if result["ok"] and result["disk"]["meets_minimum"] else 2


def command_validate(args) -> int:
    root = repo_root()
    errors = {}
    experiment = Path(args.experiment)
    if not experiment.is_absolute(): experiment = root / experiment
    campaign_path = experiment / "campaign.json"
    campaign = read_json(campaign_path) if campaign_path.exists() else {}
    mapping = {
        "brief.json": campaign.get("brief_path", "brief.json"),
        "revision.json": campaign.get("revision_path", "revision.json"),
        "campaign.json": "campaign.json",
    }
    for name, configured_path in mapping.items():
        path = Path(configured_path)
        if not path.is_absolute():
            path = (root / path) if "/" in str(path) else (experiment / path)
        if not path.exists(): errors[name] = ["missing"]
        else:
            try: read_json(path); errors[name] = []
            except Exception as exc: errors[name] = [str(exc)]
    for name in ("scene-plan.schema.json","operations.schema.json","visual-review.schema.json"):
        try: read_json(root/"schemas"/name); errors[name] = []
        except Exception as exc: errors[name] = [str(exc)]
    result = {"ok":not any(errors.values()),"errors":errors}
    emit(result)
    return 0 if result["ok"] else 2


def _profile(root: Path, name: str):
    profiles = read_json(root / "config/render-profiles.json")
    if name not in profiles: raise ValueError(f"unknown profile: {name}")
    return profiles[name]


def command_run(args) -> int:
    root = repo_root(); settings = load_settings_safe(root)
    seed = args.seed
    run_dir = root / "runs" / "controls" / unique_run_id(seed)
    result = run_pair(root,run_dir,seed,_profile(root,args.profile),blender_bin=settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"),live=False)
    emit({"ok":result["passed"],"run_id":result["run_id"],"comparison":result["comparison"]})
    return 0 if result["passed"] else 3


def command_calibrate(args) -> int:
    root = repo_root(); settings = load_settings_safe(root)
    profile = _profile(root,args.profile)
    from .adapters.blender.runner import run_blender
    from .plans import fixture_plan
    from .validators.perceptual import compare_renders
    calibration_id=unique_run_id(101); run_dir=root/"runs"/"calibration"/calibration_id; run_dir.mkdir(parents=True)
    build_dir=run_dir/"build"
    build=run_blender({"mode":"build","output_dir":str(build_dir.resolve()),"seed":101,"profile":profile,"plan":fixture_plan(101)},blender_bin=settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"),timeout=300)
    if not build.get("ok"): raise RuntimeError(build.get("error","calibration build failed"))
    renders=[]
    for index in range(3):
        output=run_dir/f"render-{index+1}"
        status=run_blender({"mode":"render","output_dir":str(output.resolve()),"seed":101,"profile":profile,"parent_native":str((build_dir/"scene.blend").resolve())},blender_bin=settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"),timeout=900)
        if not status.get("ok"): raise RuntimeError(status.get("error","calibration render failed"))
        renders.append(output)
    comparisons=[compare_renders(renders[index],renders[0]) for index in (1,2)]
    summary={"ok":all(x["passed"] for x in comparisons),"calibration_id":calibration_id,"profile":args.profile,"comparisons":comparisons,"note":"Three independent renders of one frozen native scene; no model call."}
    atomic_json(root/"results"/"calibration.json",summary); emit(summary); return 0 if summary["ok"] else 3


def command_qualify(args) -> int:
    if not args.live: raise ValueError("qualification requires explicit --live")
    root=repo_root(); settings=load_settings_safe(root)
    campaign_path=Path(args.campaign); campaign_path=campaign_path if campaign_path.is_absolute() else root/campaign_path
    campaign=read_json(campaign_path)
    setting_fields = {
        "planner_model":"MF_PLANNER_MODEL", "vision_model":"MF_VISION_MODEL",
        "planner_reasoning_effort":"MF_PLANNER_REASONING_EFFORT",
        "vision_reasoning_effort":"MF_VISION_REASONING_EFFORT",
        "image_detail":"MF_IMAGE_DETAIL",
    }
    for field, setting in setting_fields.items():
        if field in campaign:
            settings[setting] = campaign[field]
    settings["MF_COST_SCOPE"] = "scored"
    prefix=campaign.get("campaign_prefix","3d01")
    if not isinstance(prefix,str) or not prefix.replace("-","").isalnum():
        raise ValueError("invalid campaign_prefix")
    git_status=subprocess.run(["git","status","--porcelain"],cwd=root,text=True,capture_output=True,check=True).stdout
    if git_status:
        raise ValueError("qualification source tree must be clean before live dispatch")
    commit=subprocess.run(["git","rev-parse","HEAD"],cwd=root,text=True,capture_output=True,check=True).stdout.strip()
    tree=subprocess.run(["git","rev-parse","HEAD^{tree}"],cwd=root,text=True,capture_output=True,check=True).stdout.strip()
    campaign_id=time.strftime(f"{prefix}-%Y%m%dT%H%M%SZ",time.gmtime()); campaign_dir=root/"results"/campaign_id; campaign_dir.mkdir(parents=True)
    atomic_json(campaign_dir/"frozen-campaign.json",campaign)
    atomic_json(campaign_dir/"source-binding.json",{
        "schema_version":"1.0","status":"EXACT_PRE_RUN","implementation_commit":commit,
        "implementation_tree":tree,"worktree_clean_before_dispatch":True,
        "campaign_config_hash":content_id(campaign),
        "qualification_provenance_note":"Commit and Git tree were recorded from a clean worktree before the first live provider call."
    })
    from .budget import BudgetLedger
    from .providers.openai_provider import OpenAIProvider
    # One durable ledger covers development checks and every scored campaign so
    # a restart or a new results directory cannot reset the authorized ceiling.
    ledger=BudgetLedger(root/"results"/"budget.jsonl",campaign_limit=float(campaign["campaign_api_limit_usd"]))
    provider=OpenAIProvider(settings,ledger,campaign_dir/"provider")
    summaries=[]
    for seed in campaign["seeds"]:
        run_dir=root/"runs"/campaign_id/unique_run_id(seed)
        try:
            summaries.append(run_pair(root,run_dir,seed,_profile(root,campaign["profile"]),blender_bin=settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"),provider=provider,live=True))
        except Exception as exc:
            failure={"run_id":run_dir.name,"seed":seed,"passed":False,"error":f"{type(exc).__name__}: {exc}","director_status":"PENDING"}
            run_dir.mkdir(parents=True,exist_ok=True); atomic_json(run_dir/"result.json",failure); summaries.append(failure)
    report=write_campaign_report(campaign_dir,summaries,ledger.summary())
    emit({"campaign_id":campaign_id,"report":str(report),"machine_valid":sum(bool(x.get('passed')) for x in summaries),"attempted":len(summaries)})
    return 0 if all(x.get("passed") for x in summaries) else 3


def command_failures(args) -> int:
    root=repo_root(); env={"PATH":str(root/".venv/bin")+":"+str(Path("/usr/bin")),"PYTHONPATH":str(root/"src")}
    result=subprocess.run([str(root/".venv/bin/python"),"-m","pytest","-m","not live",str(Path(args.suite))],cwd=root,env=env,check=False)
    return result.returncode


def command_review(args) -> int:
    root=repo_root(); matches=list((root/"runs").glob(f"**/{args.run_id}"))
    if not matches: raise FileNotFoundError(args.run_id)
    run_dir=matches[0]
    if args.import_file:
        review=normalize_director_review(read_json(args.import_file))
        atomic_json(run_dir/"director-review.json",review)
        result_path=run_dir/"result.json"; result=read_json(result_path)
        result["director_status"]=review["status"]
        result["creative_status"]="DIRECTOR_ACCEPTED" if review["accepted"] else "DIRECTOR_REJECTED"
        result["director_review"]=review
        from .reporting import finalize_run_artifacts, write_comparison
        comparison=write_comparison(run_dir,result); result["comparison"]=str(comparison); atomic_json(result_path,result)
        campaign_id=run_dir.parent.name; campaign_dir=root/"results"/campaign_id
        telemetry=campaign_dir/"provider/telemetry.jsonl"
        finalize_run_artifacts(run_dir,result,telemetry)
        if campaign_dir.exists():
            from .budget import BudgetLedger
            summaries=[read_json(path) for path in sorted(run_dir.parent.glob("*/result.json"))]
            write_campaign_report(campaign_dir,summaries,BudgetLedger(root/"results/budget.jsonl",campaign_limit=40).summary())
        print(run_dir/"director-review.json")
    else: print(run_dir/"comparison.html")
    return 0


def resolve_replay_seed(package_path: Path, package: dict, stage: str, *, plan: dict | None = None) -> int:
    """Resolve a replay seed while authenticating legacy revision intent metadata."""
    if "seed" in package:
        seed = package["seed"]
    elif stage == "initial" and plan is not None:
        seed = plan.get("seed")
    elif stage == "revision":
        intent_path = package_path.parent / "intent-package.json"
        intent = read_json(intent_path)
        claimed = intent.pop("package_id", None)
        if not claimed or content_id(intent) != claimed:
            raise ValueError("revision intent package identity mismatch")
        if claimed != package.get("intent_package_hash"):
            raise ValueError("revision intent package does not match executable package")
        if intent.get("stage") != "revision":
            raise ValueError("revision intent package has wrong stage")
        seed = intent.get("seed")
    else:
        seed = None
    if type(seed) is not int or seed < 0:
        raise ValueError("replay package has no valid seed")
    return seed


def command_replay(args) -> int:
    root=repo_root(); settings=load_settings_safe(root); output=Path(args.output).resolve()
    if not args.offline: raise ValueError("replay must use --offline")
    output.mkdir(parents=True,exist_ok=False)
    from .adapters.blender.runner import run_blender
    package_path=Path(args.package).resolve(); package=read_json(package_path)
    claimed=package.pop("package_id",None)
    if not claimed or content_id(package) != claimed: raise ValueError("package identity mismatch")
    profile=package["render_profile"]
    stage=package.get("stage")
    if stage is None and {"parent_native_hash","parent_native_relpath","operations_hash","operations_relpath"} <= package.keys():
        # Backward-compatible recognition for preserved revision packages made
        # before the explicit stage field was added. Identity is still checked
        # against the original content and every referenced input remains hashed.
        stage="revision"
    if stage == "initial":
        plan_path=safe_relative(package_path.parent,Path(package["plan_relpath"])); plan=read_json(plan_path)
        if content_id(plan) != package["plan_hash"]: raise ValueError("plan hash mismatch")
        replay_seed=resolve_replay_seed(package_path,package,stage,plan=plan)
        status=run_blender({"mode":"build","output_dir":str(output/"build"),"seed":replay_seed,"profile":profile,"plan":plan},blender_bin=settings["BLENDER_BIN"],timeout=300)
    elif stage == "revision":
        replay_seed=resolve_replay_seed(package_path,package,stage)
        run_root=package_path.parent.parent
        parent=safe_relative(run_root,package_path.parent/Path(package["parent_native_relpath"])); operations=read_json(safe_relative(run_root,package_path.parent/Path(package["operations_relpath"])))
        if file_digest(parent) != package["parent_native_hash"] or content_id(operations) != package["operations_hash"]: raise ValueError("revision input hash mismatch")
        status=run_blender({"mode":"revise","output_dir":str(output/"build"),"seed":replay_seed,"profile":profile,"parent_native":str(parent),**operations},blender_bin=settings["BLENDER_BIN"],timeout=300)
    else: raise ValueError("unsupported package stage")
    if not status.get("ok"): raise RuntimeError(status.get("error","replay build failed"))
    render=run_blender({"mode":"render","output_dir":str(output/"render"),"seed":replay_seed,"profile":profile,"parent_native":str(output/"build/scene.blend")},blender_bin=settings["BLENDER_BIN"],timeout=900)
    from .validators.structural import compare_replay_snapshots
    original_snapshot=(package_path.parent/"build/snapshot.json").resolve()
    semantic=compare_replay_snapshots(read_json(original_snapshot),read_json(output/"build/snapshot.json")) if original_snapshot.exists() else {"passed":False,"differences":[{"path":"$","reason":"original snapshot missing"}]}
    result={"ok":bool(render.get("ok") and semantic.get("passed")),"package_id":claimed,"seed":replay_seed,"output":str(output),"native_sha256":file_digest(output/"build/scene.blend") if (output/"build/scene.blend").exists() else None,"semantic_replay":semantic}
    atomic_json(output/"replay-result.json",result); emit(result); return 0 if result["ok"] else 3


def command_report(args) -> int:
    root=repo_root(); campaign_dir=root/"results"/args.campaign
    summaries=[read_json(p) for p in sorted((root/"runs"/args.campaign).glob("*/result.json"))]
    from .budget import BudgetLedger
    from .reporting import finalize_run_artifacts
    telemetry=campaign_dir/"provider/telemetry.jsonl"
    for summary in summaries:
        run_dir=root/"runs"/args.campaign/summary["run_id"]
        if summary.get("passed"):
            finalize_run_artifacts(run_dir,summary,telemetry)
    budget=BudgetLedger(root/"results/budget.jsonl",campaign_limit=40).summary()
    report=write_campaign_report(campaign_dir,summaries,budget); print(report); return 0


def command_export(args) -> int:
    root=repo_root(); source=root/"results"/args.campaign; destination=Path(args.output).resolve()
    if destination.exists(): raise FileExistsError(destination)
    summary=read_json(source/"summary.json")
    frozen=read_json(source/"frozen-campaign.json") if (source/"frozen-campaign.json").exists() else {}
    source_binding=read_json(source/"source-binding.json") if (source/"source-binding.json").exists() else {}
    shutil.copytree(source,destination/"results"/args.campaign)
    for name in ("doctor.json","calibration.json","budget.jsonl","OFFLINE_READINESS.md"):
        candidate=root/"results"/name
        if candidate.exists():
            (destination/"results").mkdir(parents=True,exist_ok=True); shutil.copy2(candidate,destination/"results"/name)
    for item in summary.get("runs",[]):
        if item.get("passed"):
            run_source=root/"runs"/args.campaign/item["run_id"]
            run_destination=destination/"runs"/args.campaign/item["run_id"]
            shutil.copytree(run_source,run_destination)
            exported_result=read_json(run_destination/"result.json")
            exported_result["comparison"]="comparison.html"
            atomic_json(run_destination/"result.json",exported_result)
            from .reporting import write_comparison, write_run_artifact_manifest
            write_comparison(run_destination,exported_result)
            write_run_artifact_manifest(run_destination)
    replay_sources=sorted((root/"replays").glob(f"{args.campaign}-*")) if (root/"replays").exists() else []
    for replay_source in replay_sources:
        if any(replay_source.iterdir()):
            shutil.copytree(replay_source,destination/"replays"/replay_source.name)
    reviewer_qualification=frozen.get("reviewer_qualification") or {}
    qualification_record=root/"feasibility/3d/3d-01-1/evaluator-qualification.json"
    if reviewer_qualification and qualification_record.exists():
        record=read_json(qualification_record)
        for attempt in record.get("attempts",[]):
            attempt_source=safe_relative(root,root/attempt["result_dir"])
            attempt_destination=destination/attempt_source.relative_to(root)
            if not attempt_destination.exists():
                shutil.copytree(attempt_source,attempt_destination)
        benchmark_id=reviewer_qualification.get("benchmark_id")
        benchmark_matches=[]
        for manifest_path in (root/"runs/3d011-evaluator").glob("*/manifest.json"):
            if read_json(manifest_path).get("benchmark_id")==benchmark_id:
                benchmark_matches.append(manifest_path.parent)
        if len(benchmark_matches)!=1:
            raise ValueError("qualified evaluator benchmark is missing or ambiguous")
        benchmark_source=benchmark_matches[0]
        benchmark_destination=destination/"evaluator-benchmark"/benchmark_id
        benchmark_destination.mkdir(parents=True)
        shutil.copytree(benchmark_source/"cases",benchmark_destination/"cases")
        shutil.copy2(benchmark_source/"manifest.json",benchmark_destination/"manifest.json")
        shutil.copy2(benchmark_source/"labels.json",benchmark_destination/"labels.json")
    for relative in ("config","schemas","feasibility/3d/3d-01","feasibility/3d/3d-01-1","docs","prior-art","src","tests"):
        candidate=root/relative
        if candidate.is_dir(): shutil.copytree(candidate,destination/relative)
    for relative in ("MOVIE_FACTORY_3D_FEASIBILITY_SPEC.md","README.md","SETUP_README.md","requirements.lock","pyproject.toml",".python-version",".env.example","AGENTS.md"):
        candidate=root/relative
        if candidate.exists():
            target=destination/relative; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(candidate,target)
    if source_binding.get("implementation_commit"):
        import io
        import tarfile
        archive_paths=["src","tests","config","schemas","feasibility","docs","prior-art","MOVIE_FACTORY_3D_FEASIBILITY_SPEC.md","README.md","SETUP_README.md","requirements.lock","pyproject.toml",".python-version",".env.example","AGENTS.md"]
        archive=subprocess.run(["git","archive",source_binding["implementation_commit"],*archive_paths],cwd=root,check=True,capture_output=True)
        exact_source=destination/"execution-source"
        exact_source.mkdir(parents=True)
        with tarfile.open(fileobj=io.BytesIO(archive.stdout),mode="r:") as bundle:
            bundle.extractall(exact_source,filter="data")
    evidence_commit=subprocess.run(["git","rev-parse","HEAD"],cwd=root,text=True,capture_output=True,check=True).stdout.strip()
    evidence_tree=subprocess.run(["git","rev-parse","HEAD^{tree}"],cwd=root,text=True,capture_output=True,check=True).stdout.strip()
    atomic_json(destination/"bundle-source-binding.json",{
        "schema_version":"1.0","campaign_id":args.campaign,
        "execution_commit":source_binding.get("implementation_commit"),
        "execution_tree":source_binding.get("implementation_tree"),
        "evidence_tooling_commit":evidence_commit,"evidence_tooling_tree":evidence_tree,
        "note":"execution-source contains the exact live campaign revision; root source contains the final review and export tooling."
    })
    atomic_json(destination/"excluded-inventory.json",{
        "schema_version":"1.0","campaign_id":args.campaign,
        "excluded":[".env and all credential values",".git history",".venv and .runtime dependency installations","non-selected control/remediation run payloads","evaluator corruption build intermediates","API preflight logs","empty failed replay directory","Python and test caches"],
        "note":"Recreate the project-local environment from requirements.lock. Replays require the pinned Blender build or a separately qualified compatible build."
    })
    experiment_id=summary.get("experiment_id","3D-01")
    if source_binding.get("status")=="EXACT_PRE_RUN":
        provenance=(f"The live campaign was bound before dispatch to implementation commit `{source_binding['implementation_commit']}` and Git tree `{source_binding['implementation_tree']}`. An exact archive of that revision is in `execution-source/`; `bundle-source-binding.json` identifies the final root evidence tooling revision.")
    else:
        provenance="The live qualification predates its recorded Git commit. Its source binding is explicitly post-hoc; offline replay is the reproducibility evidence."
    (destination/"REPRODUCIBILITY.md").write_text(
        f"# Reproducing this {experiment_id} evidence bundle\n\n"
        "This bundle includes the exact live implementation in `execution-source/`, final evidence tooling in the root `src/`, tests, frozen configuration, selected run packages, native Blender scenes, renders, evaluator qualification cases and results, reports, and offline replays.\n\n"
        "Create the project-local `.venv` exactly as described in `SETUP_README.md`; never place credentials in this bundle. Run `.venv/bin/python -m pytest`, then replay any selected executable package with `mf3d replay --offline`. Comparison links in the campaign report are relative to this bundle.\n\n"
        f"See `results/{args.campaign}/source-binding.json` for the provenance boundary. {provenance}\n"
    )
    from .packages import manifest_for
    files=[path for path in destination.rglob("*") if path.is_file() and path.name!="inventory.json"]
    atomic_json(destination/"inventory.json",{"schema_version":"1.0","campaign_id":args.campaign,"artifacts":manifest_for(destination,files)})
    print(destination); return 0


def command_prepare_evaluator(args) -> int:
    root=repo_root(); settings=load_settings_safe(root)
    from .evaluator import prepare_benchmark
    config_path=Path(args.config); config_path=config_path if config_path.is_absolute() else root/config_path
    output=Path(args.output); output=output if output.is_absolute() else root/output
    emit(prepare_benchmark(root,read_json(config_path),output,blender_bin=settings["BLENDER_BIN"]))
    return 0


def command_prepare_assets(args) -> int:
    root=repo_root()
    from .assets import prepare_assets
    manifest_path=Path(args.manifest); manifest_path=manifest_path if manifest_path.is_absolute() else root/manifest_path
    source=Path(args.source); source=source if source.is_absolute() else root/source
    output=Path(args.output); output=output if output.is_absolute() else root/output
    result=prepare_assets(source,read_json(manifest_path),output)
    emit({"output":str(output),"assets":len(result["assets"]),"selected_bytes":result["selected_bytes"],"artifacts":len(result["artifacts"])})
    return 0


def command_qualify_assets(args) -> int:
    root=repo_root(); settings=load_settings_safe(root)
    staged=Path(args.staged); staged=staged if staged.is_absolute() else root/staged
    output=Path(args.output); output=output if output.is_absolute() else root/output
    from .asset_controller import run_asset_qualification
    result=run_asset_qualification(root,staged.resolve(),output.resolve(),_profile(root,args.profile),settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"))
    emit({"ok":result["passed"],"run_id":result["run_id"],"comparison":result["comparison"],"director_status":result["director_status"]})
    return 0 if result["passed"] else 3


def command_replay_assets(args) -> int:
    root=repo_root(); settings=load_settings_safe(root)
    run=Path(args.run); run=run if run.is_absolute() else root/run
    output=Path(args.output); output=output if output.is_absolute() else root/output
    from .asset_controller import replay_asset_revision
    result=replay_asset_revision(root,run.resolve(),output.resolve(),settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"))
    emit(result); return 0 if result["ok"] else 3


def command_probe_character_assets(args) -> int:
    root=repo_root(); settings=load_settings_safe(root)
    staged=Path(args.staged); staged=(staged if staged.is_absolute() else root/staged).resolve()
    output=Path(args.output); output=(output if output.is_absolute() else root/output).resolve()
    output.mkdir(parents=True,exist_ok=False)
    manifest=read_json(root/"feasibility/3d/3d-03/assets.json")
    members={item["archive_path"]:item["sha256"] for item in manifest["assets"][0]["members"]}
    sources={
        "model":"Model/characterMedium.fbx", "idle":"Animations/idle.fbx",
        "run":"Animations/run.fbx", "jump":"Animations/jump.fbx",
    }
    from .adapters.blender.runner import run_blender
    results={}
    for label,relative in sources.items():
        path=safe_relative(staged,staged/"character_source_01"/relative)
        status=run_blender({"mode":"animation_probe","output_dir":str(output/label),"seed":303,
                            "profile":_profile(root,"smoke"),"asset":{"path":str(path),"sha256":members[relative],"format":"fbx"}},
                           blender_bin=settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"),timeout=300)
        results[label]={"ok":status.get("ok"),"error":status.get("error"),"probe":str(output/label/"probe.json")}
    summary={"schema_version":"1.0","experiment_id":"3D-03","results":results,"ok":all(item["ok"] for item in results.values())}
    atomic_json(output/"summary.json",summary); emit(summary); return 0 if summary["ok"] else 3


def command_qualify_character(args) -> int:
    root=repo_root(); settings=load_settings_safe(root)
    staged=Path(args.staged); staged=(staged if staged.is_absolute() else root/staged).resolve()
    output=Path(args.output); output=(output if output.is_absolute() else root/output).resolve()
    from .character_controller import run_character_qualification
    result=run_character_qualification(root,staged,output,_profile(root,args.profile),settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"))
    emit({"ok":result["passed"],"run_id":result["run_id"],"comparison":result["comparison"],"director_status":result["director_status"]})
    return 0 if result["passed"] else 3


def command_qualify_character_031(args) -> int:
    root=repo_root(); settings=load_settings_safe(root)
    staged=Path(args.staged); staged=(staged if staged.is_absolute() else root/staged).resolve()
    output=Path(args.output); output=(output if output.is_absolute() else root/output).resolve()
    from .character_controller import run_character_qualification
    result=run_character_qualification(root,staged,output,_profile(root,args.profile),
                                       settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"),variant="3d-03-1")
    emit({"ok":result["passed"],"run_id":result["run_id"],"comparison":result["comparison"],"director_status":result["director_status"]})
    return 0 if result["passed"] else 3


def command_export_character_031(args) -> int:
    root=repo_root(); output=Path(args.output); output=(output if output.is_absolute() else root/output).resolve()
    from .character_export import export_character_031
    result=export_character_031(root,output); emit(result); return 0


def command_replay_character(args) -> int:
    root=repo_root(); settings=load_settings_safe(root)
    run=Path(args.run); run=(run if run.is_absolute() else root/run).resolve()
    output=Path(args.output); output=(output if output.is_absolute() else root/output).resolve()
    from .character_controller import replay_character_revision
    result=replay_character_revision(run,output,settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"))
    emit(result); return 0 if result["ok"] else 3


def command_validate_character_motion(args) -> int:
    root=repo_root(); settings=load_settings_safe(root)
    run=Path(args.run); run=(run if run.is_absolute() else root/run).resolve()
    output=Path(args.output); output=(output if output.is_absolute() else root/output).resolve()
    from .character_motion import run_character_motion_addendum
    result=run_character_motion_addendum(root,run,output,settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"),settings,args.live)
    emit({"ok":result["decision"]=="YELLOW","decision":result["decision"],"run_id":result["run_id"],
          "review":result["review"],"director_status":result["director_status"],"known_api_cost_usd":result["known_api_cost_usd"]})
    return 0 if result["decision"]=="YELLOW" else 3


def command_validate_character_motion_031(args) -> int:
    root=repo_root(); settings=load_settings_safe(root)
    run=Path(args.run); run=(run if run.is_absolute() else root/run).resolve()
    output=Path(args.output); output=(output if output.is_absolute() else root/output).resolve()
    from .character_motion import run_character_motion_031
    result=run_character_motion_031(root,run,output,settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"))
    emit({"ok":result["decision"]=="YELLOW","decision":result["decision"],"run_id":result["run_id"],
          "review":result["review"],"idle_run_machine_pass":result["idle_run_machine_pass"],
          "jump_status":result["jump_status"],"known_api_cost_usd":0})
    return 0 if result["decision"]=="YELLOW" else 3


def command_run_performance_04(args) -> int:
    root=repo_root(); settings=load_settings_safe(root)
    output=Path(args.output); output=(output if output.is_absolute() else root/output).resolve()
    from .performance_controller import run_performance_04
    result=run_performance_04(root,output,_profile(root,args.profile),
                              settings.get("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender"),
                              render_frames=not args.no_render,scored=args.scored)
    emit({"ok":result["machine_passed"],"decision":result["decision"],"run_id":result["run_id"],
          "review":result["review"],"director_status":result["director_status"],"scored":result["scored"]})
    return 0 if result["machine_passed"] else 3


def command_evaluate_evaluator(args) -> int:
    if not args.live: raise ValueError("evaluator qualification requires explicit --live")
    root=repo_root(); settings=load_settings_safe(root)
    from .evaluator import evaluate_benchmark
    config_path=Path(args.config); config_path=config_path if config_path.is_absolute() else root/config_path
    benchmark=Path(args.benchmark); benchmark=benchmark if benchmark.is_absolute() else root/benchmark
    output=Path(args.output); output=output if output.is_absolute() else root/output
    summary=evaluate_benchmark(root,read_json(config_path),benchmark,output,settings)
    emit({"output":str(output),"qualified_candidates":sum(x["qualified"] for x in summary["candidate_results"]),"selected_candidate":summary["selected_candidate"]})
    return 0 if summary["selected_candidate"] else 3


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="mf3d"); sub=p.add_subparsers(dest="command",required=True)
    q=sub.add_parser("doctor"); q.add_argument("--engine",default="blender",choices=["blender"]); q.add_argument("--output",type=Path); q.set_defaults(func=command_doctor)
    q=sub.add_parser("validate-spec"); q.add_argument("--experiment",required=True); q.set_defaults(func=command_validate)
    q=sub.add_parser("run"); q.add_argument("--experiment",required=True); q.add_argument("--provider",default="mock",choices=["mock"]); q.add_argument("--profile",default="smoke"); q.add_argument("--seed",type=int,default=101); q.set_defaults(func=command_run)
    q=sub.add_parser("calibrate"); q.add_argument("--experiment",required=True); q.add_argument("--profile",default="smoke"); q.set_defaults(func=command_calibrate)
    q=sub.add_parser("qualify"); q.add_argument("--campaign",required=True); q.add_argument("--live",action="store_true"); q.set_defaults(func=command_qualify)
    q=sub.add_parser("inject-failures"); q.add_argument("--suite",required=True); q.add_argument("--provider",default="mock"); q.set_defaults(func=command_failures)
    q=sub.add_parser("review"); q.add_argument("--run",dest="run_id",required=True); q.add_argument("--open",action="store_true"); q.add_argument("--import",dest="import_file",type=Path); q.set_defaults(func=command_review)
    q=sub.add_parser("replay"); q.add_argument("--package",required=True); q.add_argument("--offline",action="store_true"); q.add_argument("--output",required=True); q.set_defaults(func=command_replay)
    q=sub.add_parser("report"); q.add_argument("--campaign",required=True); q.set_defaults(func=command_report)
    q=sub.add_parser("export"); q.add_argument("--campaign",required=True); q.add_argument("--output",required=True); q.set_defaults(func=command_export)
    q=sub.add_parser("prepare-evaluator"); q.add_argument("--config",required=True); q.add_argument("--output",required=True); q.set_defaults(func=command_prepare_evaluator)
    q=sub.add_parser("prepare-assets"); q.add_argument("--manifest",required=True); q.add_argument("--source",required=True); q.add_argument("--output",required=True); q.set_defaults(func=command_prepare_assets)
    q=sub.add_parser("qualify-assets"); q.add_argument("--staged",required=True); q.add_argument("--output",default="runs/3d02"); q.add_argument("--profile",default="smoke"); q.set_defaults(func=command_qualify_assets)
    q=sub.add_parser("replay-assets"); q.add_argument("--run",required=True); q.add_argument("--output",required=True); q.set_defaults(func=command_replay_assets)
    q=sub.add_parser("probe-character-assets"); q.add_argument("--staged",required=True); q.add_argument("--output",required=True); q.set_defaults(func=command_probe_character_assets)
    q=sub.add_parser("qualify-character"); q.add_argument("--staged",required=True); q.add_argument("--output",default="runs/3d03"); q.add_argument("--profile",default="asset_preview"); q.set_defaults(func=command_qualify_character)
    q=sub.add_parser("qualify-character-031"); q.add_argument("--staged",required=True); q.add_argument("--output",default="runs/3d031"); q.add_argument("--profile",default="asset_preview"); q.set_defaults(func=command_qualify_character_031)
    q=sub.add_parser("export-character-031"); q.add_argument("--output",required=True); q.set_defaults(func=command_export_character_031)
    q=sub.add_parser("replay-character"); q.add_argument("--run",required=True); q.add_argument("--output",required=True); q.set_defaults(func=command_replay_character)
    q=sub.add_parser("validate-character-motion"); q.add_argument("--run",required=True); q.add_argument("--output",default="runs/3d03-temporal"); q.add_argument("--live",action="store_true"); q.set_defaults(func=command_validate_character_motion)
    q=sub.add_parser("validate-character-motion-031"); q.add_argument("--run",required=True); q.add_argument("--output",default="runs/3d031-motion"); q.set_defaults(func=command_validate_character_motion_031)
    q=sub.add_parser("run-performance-04"); q.add_argument("--output",default="runs/3d04"); q.add_argument("--profile",default="asset_preview"); q.add_argument("--no-render",action="store_true"); q.add_argument("--scored",action="store_true"); q.set_defaults(func=command_run_performance_04)
    q=sub.add_parser("evaluate-evaluator"); q.add_argument("--config",required=True); q.add_argument("--benchmark",required=True); q.add_argument("--output",required=True); q.add_argument("--live",action="store_true"); q.set_defaults(func=command_evaluate_evaluator)
    return p


def main(argv=None):
    args=parser().parse_args(argv)
    try: return args.func(args)
    except Exception as exc:
        print(f"mf3d: {type(exc).__name__}: {exc}",file=sys.stderr); return 2


if __name__ == "__main__": raise SystemExit(main())
