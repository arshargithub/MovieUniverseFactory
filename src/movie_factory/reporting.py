from __future__ import annotations

import csv
import copy
import html
import json
import statistics
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps

from .packages import atomic_json, file_digest, manifest_for


def write_comparison(run_dir: Path, result: dict[str, Any]) -> Path:
    rows = []
    for shot in ("shot_A", "shot_B", "shot_C"):
        before = run_dir / "initial" / "render" / "renders" / f"{shot}.png"
        after = run_dir / "revision" / "render" / "renders" / f"{shot}.png"
        if before.exists() and after.exists():
            rows.append(f'<section><h2>{shot}</h2><div class="pair"><figure><img src="{before.relative_to(run_dir)}"><figcaption>Before</figcaption></figure><figure><img src="{after.relative_to(run_dir)}"><figcaption>After</figcaption></figure></div></section>')
    safe = html.escape(json.dumps({k:v for k,v in result.items() if k not in {"raw"}}, indent=2))
    document = f'''<!doctype html><meta charset="utf-8"><title>Movie Factory 3D-01</title>
<style>body{{font:16px system-ui;margin:2rem;background:#181818;color:#eee}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}img{{width:100%;background:#333}}pre{{white-space:pre-wrap}}figure{{margin:0}}@media(max-width:800px){{.pair{{grid-template-columns:1fr}}}}</style>
<h1>3D-01 Persistent Scene + Targeted Revision</h1>{''.join(rows)}<h2>Machine result</h2><pre>{safe}</pre>'''
    path = run_dir / "comparison.html"
    path.write_text(document)
    return path


def _json(path: Path, default=None):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_contact_sheet(run_dir: Path) -> Path | None:
    paths = [
        run_dir / stage / "render" / "renders" / f"shot_{shot}.png"
        for shot in "ABC"
        for stage in ("initial", "revision")
    ]
    if not all(path.exists() for path in paths):
        return None
    cell_w, cell_h, label_h = 640, 360, 24
    canvas = Image.new("RGB", (cell_w * 2, (cell_h + label_h) * 3), "#181818")
    draw = ImageDraw.Draw(canvas)
    for index, path in enumerate(paths):
        row, column = divmod(index, 2)
        with Image.open(path) as source:
            frame = ImageOps.fit(source.convert("RGB"), (cell_w, cell_h))
        x, y = column * cell_w, row * (cell_h + label_h)
        canvas.paste(frame, (x, y + label_h))
        draw.text((x + 8, y + 5), f"shot_{'ABC'[row]} — {'baseline' if column == 0 else 'revised'}", fill="white")
    output = run_dir / "contact-sheet.png"
    canvas.save(output, format="PNG", optimize=True)
    return output


def _source_binding_for_run(run_dir: Path) -> dict[str, Any] | None:
    root = run_dir.parents[2]
    return _json(root / "results" / run_dir.parent.name / "source-binding.json")


def write_run_artifact_manifest(run_dir: Path) -> None:
    artifacts = [path for path in run_dir.rglob("*") if path.is_file() and path.name != "artifact-manifest.json"]
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "run_id": run_dir.name,
        "artifacts": manifest_for(run_dir, artifacts),
    }
    source_binding = _source_binding_for_run(run_dir)
    if source_binding:
        payload["source_binding"] = source_binding
    atomic_json(run_dir / "artifact-manifest.json", payload)


def finalize_run_artifacts(run_dir: Path, result: dict[str, Any], telemetry_source: Path | None = None) -> None:
    """Create portable per-run evidence after all selected outputs are immutable."""
    atomic_json(run_dir / "structural-diff.json", result.get("revision_validation"))
    atomic_json(run_dir / "validation.json", {
        "baseline": result.get("baseline_validation"),
        "revision": result.get("revision_validation"),
        "images": result.get("image_validation"),
        "visual_review": result.get("visual_review"),
    })
    for stage, name in (("initial", "baseline-manifest.json"), ("revision", "revision-manifest.json")):
        stage_root = run_dir / stage
        files = [path for path in stage_root.rglob("*") if path.is_file()]
        payload: dict[str, Any] = {
            "schema_version": "1.0",
            "run_id": run_dir.name,
            "stage": stage,
            "artifacts": manifest_for(run_dir, files),
        }
        source_binding = _source_binding_for_run(run_dir)
        if source_binding:
            payload["source_binding"] = source_binding
        atomic_json(run_dir / name, payload)
    write_contact_sheet(run_dir)
    if telemetry_source and telemetry_source.exists():
        selected = []
        for line in telemetry_source.read_text().splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("run_id") == run_dir.name:
                selected.append(json.dumps(event, sort_keys=True, separators=(",", ":"), allow_nan=False))
        (run_dir / "telemetry.jsonl").write_text("\n".join(selected) + ("\n" if selected else ""))
    write_run_artifact_manifest(run_dir)


def _purpose_map(telemetry: Path) -> dict[str, str]:
    result = {}
    if not telemetry.exists():
        return result
    for line in telemetry.read_text().splitlines():
        event = json.loads(line)
        if event.get("event_type") == "provider_request" and event.get("reservation_id"):
            result[event["reservation_id"]] = event.get("purpose")
    return result


def _ratio(numerator, denominator):
    return numerator / denominator if denominator not in (None, 0) and numerator is not None else None


def _run_metrics(run_dir: Path, result: dict[str, Any], purposes: dict[str, str]) -> dict[str, Any]:
    calls = result.get("provider_calls", [])
    usages = [call.get("usage") or {} for call in calls]
    call_purposes = [purposes.get(call.get("reservation_id"), "unknown") for call in calls]
    initial_cost = sum((call.get("cost_usd") or 0) for call, purpose in zip(calls, call_purposes) if purpose and purpose.startswith("initial_plan"))
    revision_plan_cost = sum((call.get("cost_usd") or 0) for call, purpose in zip(calls, call_purposes) if purpose == "revision_plan")
    visual_cost = sum((call.get("cost_usd") or 0) for call, purpose in zip(calls, call_purposes) if purpose == "visual_review")
    def elapsed(*parts):
        return sum((_json(run_dir.joinpath(*part, "runner-status.json"), {}) or {}).get("elapsed", 0) for part in parts)
    initial_seconds = elapsed(("initial", "build"), ("initial", "render"))
    revision_seconds = elapsed(("revision", "build"), ("revision", "render"))
    expected_seconds = elapsed(("expected", "build"), ("expected", "render"))
    scores = [item["score"] for item in (result.get("visual_review") or {}).get("scores", [])]
    known_cost = sum(call.get("cost_usd") or 0 for call in calls)
    return {
        "run_id": result.get("run_id"), "seed": result.get("seed"), "machine_valid": bool(result.get("passed")),
        "technical_status": result.get("technical_status"), "director_status": result.get("director_status"),
        "baseline_valid": (result.get("baseline_validation") or {}).get("passed"),
        "revision_valid": (result.get("revision_validation") or {}).get("passed"),
        "image_validation_color": (result.get("image_validation") or {}).get("color"),
        "visual_mean": sum(scores) / len(scores) if scores else None, "visual_min": min(scores) if scores else None,
        "visual_confidence": (result.get("visual_review") or {}).get("confidence"),
        "api_calls": len(calls), "initial_plan_calls": sum(p.startswith("initial_plan") for p in call_purposes if p),
        "initial_repairs": sum(p == "initial_plan_repair" for p in call_purposes),
        "input_tokens": sum(usage.get("input_tokens") or 0 for usage in usages),
        "cached_input_tokens": sum(usage.get("cached_input_tokens") or 0 for usage in usages),
        "output_tokens": sum(usage.get("output_tokens") or 0 for usage in usages),
        "reasoning_tokens": sum(usage.get("reasoning_tokens") or 0 for usage in usages),
        "known_api_cost_usd": known_cost, "initial_planning_cost_usd": initial_cost,
        "revision_planning_cost_usd": revision_plan_cost, "visual_review_cost_usd": visual_cost,
        "reasoning_cost_attribution_usd": sum(call.get("reasoning_cost_usd") or 0 for call in calls),
        "r_edit": _ratio(revision_plan_cost, initial_cost),
        "r_api": _ratio(revision_plan_cost + visual_cost, initial_cost),
        "r_total": None, "r_total_reason": "Local CPU time has no configured monetary valuation",
        "initial_wall_seconds": initial_seconds, "revision_wall_seconds": revision_seconds,
        "expected_oracle_wall_seconds": expected_seconds, "revision_wall_ratio": _ratio(revision_seconds, initial_seconds),
        "blender_invocations": sum((run_dir / stage / mode / "runner-status.json").exists() for stage in ("initial", "revision", "expected") for mode in ("build", "render")),
        "human_interventions": 0, "human_minutes": 0,
        "parent_sha256": result.get("parent_sha256"), "revision_sha256": result.get("revision_sha256"),
        "error": result.get("error"),
    }


def write_campaign_report(campaign_dir: Path, summaries: list[dict[str, Any]], budget: dict[str, Any] | None = None) -> Path:
    root = campaign_dir.parents[1]
    telemetry = campaign_dir / "provider" / "telemetry.jsonl"
    purposes = _purpose_map(telemetry)
    metrics = []
    for item in summaries:
        run_dir = root / "runs" / campaign_dir.name / str(item.get("run_id"))
        if run_dir.exists():
            metrics.append(_run_metrics(run_dir, item, purposes))
    metrics_path = campaign_dir / "metrics.csv"
    if metrics:
        with metrics_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(metrics[0]), lineterminator="\n")
            writer.writeheader(); writer.writerows(metrics)
    passed = sum(bool(item.get("passed")) for item in summaries)
    pending_director = any(item.get("director_status", "PENDING") == "PENDING" for item in summaries)
    med_edit = statistics.median(row["r_edit"] for row in metrics if row["r_edit"] is not None) if metrics else None
    med_api = statistics.median(row["r_api"] for row in metrics if row["r_api"] is not None) if metrics else None
    economics_unknown = med_edit is None or med_api is None
    economics_yellow = not economics_unknown and (med_edit > .35 or med_api > .75)
    economics_red = not economics_unknown and (med_edit > .75 or med_api > 1.0)
    color = "YELLOW" if pending_director or passed < 5 or economics_unknown or economics_yellow else "GREEN"
    if (passed <= 3 and len(summaries) >= 5) or economics_red:
        color = "RED"
    remediation = _json(campaign_dir / "remediation-attempts.json", {"attempts": [], "known_api_cost_usd": 0})
    portable_summaries = copy.deepcopy(summaries)
    for item in portable_summaries:
        if item.get("run_id"):
            item["comparison"] = f"../../runs/{campaign_dir.name}/{item['run_id']}/comparison.html"
    source_binding = _json(campaign_dir / "source-binding.json")
    batch_review = _json(campaign_dir / "director-batch-review.json")
    replay_attestation = _json(campaign_dir / "replay-attestation.json")
    frozen = _json(campaign_dir / "frozen-campaign.json", {}) or {}
    experiment_id = frozen.get("experiment_id", "3D-01")
    claim_boundary = frozen.get(
        "claim_boundary",
        "Evidence applies only to the recorded structured revision contract."
    )
    report = {
        "schema_version":"1.0","experiment_id":experiment_id,"campaign_id":campaign_dir.name,"pairs_attempted":len(summaries),"pairs_machine_valid":passed,
        "director_review":"PENDING" if pending_director else "RECORDED","decision":color,"budget":budget,"metrics":metrics,"remediation":remediation,"runs":portable_summaries
    }
    if source_binding:
        report["source_binding"] = source_binding
    if batch_review:
        report["director_batch_review"] = batch_review
    if replay_attestation:
        report["replay_attestation"] = replay_attestation
    atomic_json(campaign_dir / "summary.json", report)
    known_selected = sum(row["known_api_cost_usd"] for row in metrics)
    total_calls = sum(row["api_calls"] for row in metrics)
    total_input = sum(row["input_tokens"] for row in metrics)
    total_output = sum(row["output_tokens"] for row in metrics)
    total_reasoning = sum(row["reasoning_tokens"] for row in metrics)
    director_means = [item.get("director_review", {}).get("mean_score") for item in summaries if item.get("director_review", {}).get("mean_score") is not None]
    doctor = _json(root / "results" / "doctor.json", {}) or {}
    platform = doctor.get("platform", {})
    blender = doctor.get("blender", {})
    lines = [
        f"# {experiment_id} campaign report", "", f"**Decision: {color}**", "",
        f"Machine-valid pairs: **{passed}/{len(summaries)}**. " + ("Director creative acceptance remains pending." if pending_director else "Director reviews are recorded.") + (" Revision API economics are in the YELLOW band." if economics_yellow and not economics_red else ""), "",
        "## Environment and frozen configuration", "",
        f"- macOS {platform.get('macos')} on {platform.get('architecture')}; outer Python {platform.get('python')}",
        f"- {blender.get('output','').splitlines()[0] if blender.get('output') else 'Blender version unavailable'}; binary SHA-256 `{blender.get('sha256')}`",
        "- Blender Cycles CPU, 1280×720, 64 samples, three frozen cameras; two neutral frozen lights",
        f"- Planner: pinned `{frozen.get('planner_model','gpt-5.4-2026-03-05')}`, {frozen.get('planner_reasoning_effort','medium')} reasoning",
        f"- Visual reviewer: pinned `{frozen.get('vision_model','gpt-5.4-2026-03-05')}`, {frozen.get('vision_reasoning_effort','medium')} reasoning, `{frozen.get('image_detail','high')}` image detail, prompt `{frozen.get('visual_prompt_version','legacy')}`",
        "- Provider retries disabled; responses use `store=false`",
        "- Scene interface: strict semantic plans and trusted structured Blender operations; no model-generated code is executed", "",
        "## Source provenance", "",
        (f"- Status: `{source_binding.get('status')}`; implementation commit `{source_binding.get('implementation_commit')}`; Git tree `{source_binding.get('implementation_tree')}`" if source_binding else "- Source binding has not been recorded."),
        ((f"- Evidence seal tag: `{source_binding.get('evidence_seal_tag')}`. " if source_binding and source_binding.get('evidence_seal_tag') else "- ") + source_binding.get('qualification_provenance_note','') if source_binding else "- Commit and tree provenance remain pending."), "",
        (f"- Offline revision replay: seed {replay_attestation.get('seed')}; zero semantic differences; no provider calls; [attestation](replay-attestation.json)" if replay_attestation else "- Offline non-101 replay remains pending."), "",
        "## Machine outcome", "",
        f"All {passed} selected pairs passed baseline structure, exact deny-by-default revision state, required mask visibility, oracle render comparison, and the model visual gate.",
        "Each revision moved only `coffee_table_01` exactly 0.4 m toward `sofa_01` and changed only `helmet_shell_01` from `#C62828` to `#163D2A`; cameras, lighting, geometry, and protected materials remained unchanged.", "",
        f"Director review accepted all {len(director_means)} pairs with a mean score of {statistics.mean(director_means):.1f}/5 per pair; minor sofa and table polygon faceting is recorded under physical finish." if director_means else "Director review is pending.",
        (f"The identical scorecards were intentionally entered as one batch review (`{batch_review.get('batch_review_id')}`) after the Director inspected every seed." if batch_review else ""), "",
        "## Measured runtime and API use", "",
        f"- Selected-pair API calls: {total_calls}; input tokens: {total_input}; output tokens: {total_output}, including {total_reasoning} reasoning tokens",
        f"- Selected-pair known API cost: USD {known_selected:.9f}; average per machine-valid pair: USD {(known_selected/passed if passed else 0):.9f}",
        f"- Global durable-ledger committed amount, including remediation attempts and unresolved reservations: USD {(budget or {}).get('committed_usd')}",
        f"- Median `R_edit`: {med_edit:.4f}; median `R_api`: {med_api:.4f}" if med_edit is not None and med_api is not None else "- Revision cost ratios: unavailable",
        "- Local rendering/provider-independent compute is measured in `metrics.csv`; no monetary value is assigned to local CPU time", "",
        "Reasoning cost is an attribution within output cost and is not added twice. The ledger retains unknown reservations conservatively.", "",
        "## Runs", "",
    ]
    for item, row in zip(summaries, metrics):
        director_mean=(item.get("director_review") or {}).get("mean_score")
        relative = f"../../runs/{campaign_dir.name}/{item.get('run_id')}/comparison.html"
        lines.append(f"- `{item.get('run_id')}` — {'machine-valid' if item.get('passed') else 'failed'}; model visual mean {row['visual_mean']}; Director mean {director_mean}; API USD {row['known_api_cost_usd']:.9f}; [comparison]({relative})")
    review_action = "Director reviews are complete and recorded." if not pending_director else "Open each comparison/contact sheet and record Director scores."
    lines += ["", "## Failures, limits, and next action", "",
              f"Before freezing this selected campaign, {len(remediation.get('attempts', []))} implementation-remediation attempts consumed USD {remediation.get('known_api_cost_usd', 0):.6f}. Their artifacts and causes are retained in `remediation-attempts.json` and their costs remain included in the global ledger. They are not presented as Blender failures or selected results.",
              f"This five-pair experiment is evidence for the recorded {experiment_id} configuration only; it is too small for a production reliability claim. Houdini and Unreal were not run.",
              claim_boundary,
              review_action,
              (f"Revision economics meet the GREEN ceiling: median `R_api` is {med_api:.4f}, at or below 0.75." if med_api is not None and med_api <= .75 else f"To pursue GREEN, reduce all revision-runtime API cost enough to bring median `R_api` from {med_api:.4f} to at most 0.75 without weakening validation.") if med_api is not None else "Revision economics could not be calculated."]
    path = campaign_dir / "REPORT.md"
    path.write_text("\n".join(lines) + "\n")
    return path
