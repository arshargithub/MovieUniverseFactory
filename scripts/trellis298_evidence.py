"""Record source assessment without promoting it to a production actor."""
import hashlib
import json
from pathlib import Path

from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/trellis298"
NATIVE = ".runtime/art-direction/series01-trellis298/head512-remeshed/"


def evidence(relative):
    path = ROOT / relative
    return {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    packet = json.loads((OUT / "blender-head512-remeshed-packet.json").read_text())
    refs = [evidence(p) for p in (
        "results/trellis298/ASSESSMENT.md",
        "results/trellis298/cloud-d/teardown-verification.json",
        ".runtime/trellis298d/retrieved/evidence/receipt.json",
        NATIVE + "inspection.json", NATIVE + "reopen.json",
        NATIVE + "front.png", NATIVE + "left-quarter.png",
        NATIVE + "right-quarter.png", NATIVE + "front-clay.png",
        NATIVE + "right-profile.png", NATIVE + "rear-left.png",
        NATIVE + "back.png",
    )]
    applied = {"authority", "strategy", "anticipation", "stopping", "versioning",
               "economics", "current_state", "sikh_scope"}
    failed = {"visual_gate", "representation", "look", "au_reference", "au_surface"}
    checks = []
    for obligation in packet["obligations"]:
        key = obligation["id"]
        status = "PASS" if key in applied else "FAIL" if key in failed else "NOT_RUN"
        checks.append({
            "id": key, "kind": obligation["check_kind"], "status": status,
            "action_taken": "Reviewed routed rule and source/actor separation; compared corrected geometry and clay to approved v03, preserved failed controls and blocked actor promotion.",
            "observation": (
                "Source-generation/export and cleanup evidence exists; no final actor, motion, release or off-device recovery claim. Full actor work remains open."
                if key in applied else
                "Fused eyes, chunky beard and noisy crown do not meet the approved shared-film quality floor."
                if key in failed else
                "Body, deforming anatomy, separate eye/lid performance, continuous cloth release and full actor-in-scene tests are not qualified; release rights remain separate."
            ),
            "evidence": refs,
        })
    review = {
        "packet_digest": packet["packet_digest"],
        "scope": "Completed GPU/static-source assessment, not completed production actor",
        "checks": checks,
        "hypotheses": [
            {"prediction": "Wrong signed/oriented conversion destroys useful unsigned source form.",
             "observation": "Exact same source with official unsigned reconstruction produces coherent face/crown; failed raw/signed controls preserved.",
             "response": "Use representation-matched exporter and open-sheet fixture; retain presimplification source.", "result": "resolved"},
            {"prediction": "A coherent textured source may still lack editable production eyes and convincing beard.",
             "observation": "Clay and textured views confirm fused eye forms and chunky beard; no actor rig or complete performance exists.",
             "response": "Block production admission. Next method is local semantic conversion and actual close-reveal proof, not more paid generation.", "result": "not_run"},
        ],
        "adjacent_regressions": [
            {"region": "protected source/scene", "result": "Raw tensors, failed controls, accepted Pashtun and isolated299 scene preserved."},
            {"region": "budget/resources", "result": "No extra10 activation; conservative14USD reservation/liability within15, actual invoice unknown; temporary d resources absent."},
        ],
        "stopping_reason": "GPU/source assessment concluded with a failed production-source admission; no known-failing head is inserted as a final character. The separately completed299 scene is delivered for scoped development review. Full298 actor goal remains open with a concrete local-conversion path, not a claimed success.",
    }
    gate = pk.check_review(ROOT, packet, review)
    for name, value in (("production-review", review), ("production-gate", gate)):
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")
    print(json.dumps(gate, indent=2))
    # An exit-code2 is expected and binding: this source must not be admitted as an actor.
    raise SystemExit(0 if gate["ready_for_review"] else 2)


if __name__ == "__main__":
    main()
