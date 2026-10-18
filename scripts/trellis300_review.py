"""Bind documentary quality research; never promote the failed actor."""
import hashlib
import json
from pathlib import Path

from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/trellis300"


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    paths = [
        "results/trellis300/QUALITY_REVIEW.md",
        "results/trellis298/ASSESSMENT.md",
        "scripts/trellis298_worker.py",
        "docs/knowledge/SIKH_FOUNDATION_REJECTION_271.md",
        "docs/planning/SERIES_01_SIKH_BASELINE_V01.md",
        "docs/decisions/0005-production-strategy-before-execution.md",
        ".runtime/trellis298c/retrieved/evidence/build.log",
        ".runtime/trellis298c/retrieved/evidence/weight-manifest.json",
        ".runtime/trellis298-source/trellis2/pipelines/trellis2_image_to_3d.py",
        ".runtime/trellis298-source/trellis2/modules/norm.py",
        ".runtime/trellis298-source/trellis2/models/sc_vaes/sparse_unet_vae.py",
        "results/trellis298/cloud-d/aggregate-reserved.json",
    ]
    task = dict(
        id="trellis300-quality-research", operation="modeling", phase="planning",
        entities=["sikh", "sikh_beard", "sikh_turban_cover"],
        query="Sikh source quality export preservation generation limits and actor admission",
        intent="Documentary quality-ceiling diagnosis and proposed controlled comparison; no actor creation or new cloud dispatch",
        inputs={p: sha(p) for p in paths}, open_decisions=[], max_context_characters=42000,
        execution_authority={"source": paths[0], "scope": "Read-only research; proposed controls are not execution authority"},
    )
    packet = pk.task_packet(ROOT, task)
    for name, value in (("task", task), ("packet", packet)):
        (OUT / f"{name}.json").write_text(json.dumps(value, indent=2) + "\n")
    (OUT / "packet.md").write_text(pk.packet_markdown(packet))
    print(pk.packet_markdown(packet))
    if not packet["dispatch_ready"]:
        raise SystemExit(2)
    documentary = {
        "authority": "Read-only model research only; no new GPU, paid call, upload or production choice.",
        "strategy": "Controlled export preservation precedes resolution and sampler comparisons; prospective tests remain unexecuted.",
        "anticipation": "Investigated false quality-ceiling inference, export-versus-decoder confusion and generation-versus-actor readiness.",
        "stopping": "Research question is answered; poor existing actor remains failed, not admitted to avoid more work.",
        "versioning": "Bound worker, pinned source, execution manifest and OOM log; exact public config hash matched execution manifest.",
        "economics": "No new paid compute;14USD liability/reservation is not actual spend; extra10 remains inactive.",
        "rights": "Existing scope retained; no new model/provider or asset upload; research is not rights clearance.",
        "current_state": "Pashtun master and approved Sikh v03 protected; failed static source is not a production actor.",
        "sikh_scope": "Sikh-only research remains separate from300 local scene corrections; no new leader design or Gurkha work.",
    }
    evidence = [{"path": p, "sha256": sha(p)} for p in paths]
    checks = []
    for rule in packet["obligations"]:
        key = rule["id"]
        checks.append(dict(
            id=key, kind=rule["check_kind"],
            status="PASS" if key in documentary else "FAIL" if key == "visual_gate" else "NOT_RUN",
            action_taken="Performed documentary reconciliation; retained existing actor failures and unexecuted controls separately.",
            observation=documentary.get(key, "No new visual, motion or asset qualification performed. Existing298 actor rejection remains; proposed controls are untested."),
            evidence=evidence,
        ))
    review = dict(packet_digest=packet["packet_digest"], scope="Research answer only; production admission deliberately blocked",
                  checks=checks, hypotheses=[
                      dict(prediction="The512 result demonstrates the quality ceiling.", observation="Only one input/seed/default run and limited export tested;1024 produced no mesh.", response="Reject ceiling claim; propose controlled comparisons.", result="resolved"),
                      dict(prediction="Lower texture or export polygon count could fix the1024 failure.", observation="Traceback fails at FP32 shape-decoder normalization before export.", response="Reject downstream-knob fix; isolate decoder capacity and preserve latents.", result="resolved"),
                  ], adjacent_regressions="No native asset or prior evidence modified; no new output claims.",
                  stopping_reason="Documentary question answered. Production visual/performance gate remains blocked, and proposed quality tests are NOT_RUN.")
    gate = pk.check_review(ROOT, packet, review)
    for name, value in (("research-review", review), ("production-gate", gate)):
        (OUT / f"{name}.json").write_text(json.dumps(value, indent=2) + "\n")
    print(json.dumps(gate, indent=2))
    if not gate["ready_for_review"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
