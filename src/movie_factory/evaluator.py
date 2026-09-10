from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

from .budget import BudgetLedger
from .packages import atomic_json, content_id, manifest_for
from .providers.openai_provider import OpenAIProvider


RUBRIC_DIMENSIONS = {"brief_fulfillment", "cinematography", "lighting_materials", "physical_finish", "continuity_revision"}
PROMPT_VERSION = "3d011-blind-review-v3"


def visual_prompt() -> str:
    return """You are blind-scoring one 3D revision case. The six images are ordered baseline shot_A, shot_B, shot_C, then candidate revision shot_A, shot_B, shot_C. The scene must contain a sofa, coffee table, floor lamp, and motorcycle helmet. The coffee table must be visibly present in both wide shot_A and medium shot_B; the floor lamp must remain visibly present in the wide coverage. The required revision is to move the coffee table toward the sofa and change only the helmet shell from red to dark green. Exact 0.4 metre displacement and exact #163D2A material data are checked separately from semantic scene state; do not reject a case because exact metric distance or an exact hex value cannot be inferred from pixels. Judge visible direction, red-to-dark-green intent, required object presence, composition, and continuity without assuming the candidate succeeded. Detect missing objects, clearly wrong colors, camera or lighting drift, intersections, degraded composition, and any other unintended visible change. Score each rubric dimension exactly once from 1 to 5: brief_fulfillment, cinematography, lighting_materials, physical_finish, continuity_revision. A 3 is serviceable, 4 good, and 5 unusually strong for a procedural prototype. Put each concrete visible defect in critical_findings. Recommend pass only when the mean is at least 4, no score is below 3, there are no critical findings, confidence is at least 0.6, and the requested visual revision is clearly correct. Return only the required JSON."""


def _copy_images(source_run: Path, destination: Path, candidate_stage: str) -> list[Path]:
    import shutil
    destination.mkdir(parents=True, exist_ok=True)
    paths = []
    for index, (stage, shot) in enumerate(
        [("initial", shot) for shot in ("shot_A", "shot_B", "shot_C")]
        + [(candidate_stage, shot) for shot in ("shot_A", "shot_B", "shot_C")], 1
    ):
        source = source_run / stage / "render" / "renders" / f"{shot}.png"
        if not source.is_file():
            raise FileNotFoundError(source)
        target = destination / f"{index:02d}.png"
        shutil.copy2(source, target)
        paths.append(target)
    return paths


def prepare_benchmark(root: Path, config: dict[str, Any], output: Path, *, blender_bin: str) -> dict[str, Any]:
    import shutil
    from .adapters.blender.runner import run_blender

    root, output = root.resolve(), output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    profile = json.loads((root / "config/render-profiles.json").read_text())["qualification_cpu"]
    accepted_root = root / "runs" / config["accepted_campaign"]
    accepted = {}
    for run_dir in accepted_root.iterdir():
        result_path = run_dir / "result.json"
        if result_path.is_file():
            result = json.loads(result_path.read_text())
            if result.get("passed") and result.get("director_status") == "ACCEPTED":
                accepted[result["seed"]] = (run_dir, result)
    if sorted(accepted) != [101, 202, 303, 404, 505]:
        raise ValueError("accepted source campaign is incomplete")

    generated = {}
    source_run = accepted_root / config["synthetic_source_run_id"]
    parent = source_run / "revision/build/scene.blend"
    for kind in config["corruptions"]:
        build_dir = output / "generated" / kind / "build"
        render_dir = output / "generated" / kind / "render"
        status = run_blender({"mode":"evaluator_corrupt","output_dir":str(build_dir),"seed":303,"profile":profile,"parent_native":str(parent),"corruption":{"kind":kind}}, blender_bin=blender_bin, timeout=300)
        if not status.get("ok"):
            raise RuntimeError(f"corruption build failed: {kind}")
        status = run_blender({"mode":"render","output_dir":str(render_dir),"seed":303,"profile":profile,"parent_native":str(build_dir/"scene.blend")}, blender_bin=blender_bin, timeout=900)
        if not status.get("ok"):
            raise RuntimeError(f"corruption render failed: {kind}")
        generated[kind] = render_dir

    labels: dict[str, Any] = {}
    cases = []
    label_sources: dict[str, tuple[str, Any]] = {}
    director_dimensions = {item["dimension"]: item["score"] for item in accepted[101][1]["director_review"]["scores"]}
    for seed, (run_dir, result) in accepted.items():
        label_sources[f"accepted_seed_{seed}"] = ("accepted", {"run_dir":run_dir,"seed":seed,"director_scores":director_dimensions})
    historical = config["historical_negative"]
    historical_run = root / "runs" / historical["campaign_id"] / historical["run_id"]
    label_sources["failed_framing"] = ("historical", {"run_dir":historical_run,"category":historical["category"]})
    for kind in config["corruptions"]:
        label_sources[kind] = ("synthetic", {"kind":kind})

    for number, source_name in enumerate(config["blind_case_order"], 1):
        case_id = f"case-{number:02d}"
        case_dir = output / "cases" / case_id
        source_type, details = label_sources[source_name]
        if source_type == "accepted":
            images = _copy_images(details["run_dir"], case_dir, "revision")
            label = {"expected":"pass","category":"accepted","seed":details["seed"],"director_scores":details["director_scores"]}
        elif source_type == "historical":
            images = _copy_images(details["run_dir"], case_dir, "revision")
            label = {"expected":"non_pass","category":details["category"]}
        else:
            case_dir.mkdir(parents=True)
            images=[]
            for index, shot in enumerate(("shot_A","shot_B","shot_C"),1):
                source=source_run/"initial/render/renders"/f"{shot}.png"; target=case_dir/f"{index:02d}.png"; shutil.copy2(source,target); images.append(target)
            for index, shot in enumerate(("shot_A","shot_B","shot_C"),4):
                source=generated[details["kind"]]/"renders"/f"{shot}.png"; target=case_dir/f"{index:02d}.png"; shutil.copy2(source,target); images.append(target)
            label = {"expected":"non_pass","category":details["kind"]}
        cases.append({"case_id":case_id,"images":[str(path.relative_to(output)) for path in images]})
        labels[case_id]=label
    image_paths=[output/path for case in cases for path in case["images"]]
    manifest={"schema_version":"1.0","benchmark_id":config["benchmark_id"],"prompt_version":PROMPT_VERSION,"prompt_hash":content_id(visual_prompt()),"cases":cases,"image_artifacts":manifest_for(output,image_paths)}
    atomic_json(output/"manifest.json",manifest)
    atomic_json(output/"labels.json",{"schema_version":"1.0","benchmark_id":config["benchmark_id"],"labels":labels})
    return {"benchmark":str(output),"cases":len(cases),"images":len(image_paths),"positive_cases":sum(x["expected"]=="pass" for x in labels.values()),"negative_cases":sum(x["expected"]=="non_pass" for x in labels.values())}


def _valid_review(data: Any) -> bool:
    scores = data.get("scores", []) if isinstance(data, dict) else []
    return len(scores)==5 and {item.get("dimension") for item in scores if isinstance(item,dict)}==RUBRIC_DIMENSIONS


def _predicted_pass(data: dict[str, Any]) -> bool:
    scores=[item["score"] for item in data["scores"]]
    return data["recommendation"]=="pass" and not data["critical_findings"] and data["confidence"]>=.6 and sum(scores)/5>=4 and min(scores)>=3


def score_candidate(responses: dict[str, Any], labels: dict[str, Any], thresholds: dict[str, float]) -> dict[str, Any]:
    valid={case_id:value for case_id,value in responses.items() if not value.get("error") and _valid_review(value.get("data"))}
    positives=[case_id for case_id,label in labels.items() if label["expected"]=="pass"]
    negatives=[case_id for case_id,label in labels.items() if label["expected"]=="non_pass"]
    positive_pass=sum(case_id in valid and _predicted_pass(valid[case_id]["data"]) for case_id in positives)/len(positives)
    negative_sensitivity=sum(case_id in valid and not _predicted_pass(valid[case_id]["data"]) for case_id in negatives)/len(negatives)
    critical_rate=sum(case_id in valid and bool(valid[case_id]["data"]["critical_findings"]) for case_id in negatives)/len(negatives)
    deltas=[]
    for case_id in positives:
        if case_id not in valid: continue
        actual={item["dimension"]:item["score"] for item in valid[case_id]["data"]["scores"]}
        deltas.extend(abs(actual[name]-labels[case_id]["director_scores"][name]) for name in RUBRIC_DIMENSIONS)
    mae=sum(deltas)/len(deltas) if deltas else None
    within=sum(delta<=1 for delta in deltas)/len(deltas) if deltas else 0
    valid_rate=len(valid)/len(labels)
    costs=[value.get("cost_usd") for value in responses.values() if value.get("cost_usd") is not None]
    metrics={"positive_pass_rate":positive_pass,"negative_sensitivity":negative_sensitivity,"negative_critical_finding_rate":critical_rate,"accepted_dimension_mae":mae,"accepted_scores_within_one":within,"response_valid_rate":valid_rate,"known_api_cost_usd":sum(costs),"median_case_cost_usd":statistics.median(costs) if costs else None}
    qualified=(positive_pass>=thresholds["positive_pass_rate_min"] and negative_sensitivity>=thresholds["negative_sensitivity_min"] and critical_rate>=thresholds["negative_critical_finding_rate_min"] and mae is not None and mae<=thresholds["accepted_dimension_mae_max"] and within>=thresholds["accepted_scores_within_one_min"] and valid_rate>=thresholds["response_valid_rate_min"])
    return {"qualified":qualified,"metrics":metrics}


def evaluate_benchmark(root: Path, config: dict[str, Any], benchmark: Path, output: Path, settings: dict[str, Any]) -> dict[str, Any]:
    root, benchmark, output = root.resolve(), benchmark.resolve(), output.resolve()
    manifest=json.loads((benchmark/"manifest.json").read_text()); labels=json.loads((benchmark/"labels.json").read_text())["labels"]
    if manifest["benchmark_id"]!=config["benchmark_id"] or manifest["prompt_hash"]!=content_id(visual_prompt()):
        raise ValueError("benchmark/config identity mismatch")
    output.mkdir(parents=True,exist_ok=True)
    ledger=BudgetLedger(root/"results/budget.jsonl",campaign_limit=40)
    schema=json.loads((root/"schemas/visual-review.schema.json").read_text())
    encoded_bound=len(visual_prompt().encode("utf-8"))+len(json.dumps(schema,sort_keys=True,separators=(",",":")).encode("utf-8"))+4096+4096*6
    price=config["pricebook"]
    reservation_per_call=(encoded_bound*price["input_per_million_usd"]+config["max_output_tokens"]*price["output_per_million_usd"])/1_000_000
    existing_summary=ledger.summary()
    existing_committed=sum(
        existing_summary.get("runs",{}).get(f"{config['benchmark_id']}-{candidate['candidate_id']}",{}).get("development",{}).get("committed_usd",0)
        for candidate in config["candidates"]
    )
    missing_calls=sum(
        not (output/candidate["candidate_id"]/f"{case['case_id']}.json").exists()
        for candidate in config["candidates"] for case in manifest["cases"]
    )
    if existing_committed+missing_calls*reservation_per_call>config["evaluation_api_limit_usd"]:
        raise ValueError("frozen evaluator campaign reservation exceeds its API limit")
    candidate_results=[]
    for candidate in config["candidates"]:
        candidate_dir=output/candidate["candidate_id"]; candidate_dir.mkdir(exist_ok=True)
        configured=dict(settings,MF_VISION_MODEL=candidate["model"],MF_VISION_REASONING_EFFORT=candidate["reasoning_effort"],MF_IMAGE_DETAIL=candidate["image_detail"],MF_COST_SCOPE="development")
        provider=OpenAIProvider(configured,ledger,candidate_dir/"provider")
        responses={}
        for case in manifest["cases"]:
            result_path=candidate_dir/f"{case['case_id']}.json"
            if result_path.exists():
                result=json.loads(result_path.read_text())
            else:
                images=[benchmark/path for path in case["images"]]
                result=provider.generate_json(purpose="evaluator_qualification",prompt=visual_prompt(),schema=schema,images=images,run_id=f"{config['benchmark_id']}-{candidate['candidate_id']}",stage="development",max_output_tokens=config["max_output_tokens"])
                atomic_json(result_path,result)
            responses[case["case_id"]]=result
        scored=score_candidate(responses,labels,config["thresholds"])
        candidate_results.append({**candidate,**scored})
        if scored["qualified"] and config.get("stop_on_first_qualified"):
            break
    qualified=[item for item in candidate_results if item["qualified"]]
    selected=min(qualified,key=lambda item:(item["metrics"]["median_case_cost_usd"],item["candidate_id"])) if qualified else None
    summary={"schema_version":"1.0","experiment_id":config["experiment_id"],"benchmark_id":config["benchmark_id"],"benchmark_manifest_hash":content_id(manifest),"prompt_version":PROMPT_VERSION,"prompt_hash":content_id(visual_prompt()),"thresholds":config["thresholds"],"candidate_results":candidate_results,"selected_candidate":selected,"claim_boundary":config["claim_boundary"],"budget":ledger.summary()}
    atomic_json(output/"summary.json",summary)
    return summary
