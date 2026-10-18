"""Create a source-bound planning packet for Director300's local correction."""
import hashlib
import json
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/sikh300"

def main():
    task = json.loads((ROOT / "results/sikh299/task.json").read_text())
    task.update(id="sikh300-planning", phase="planning",
                intent="Director300 reduced42-degree stop with inter-lock upright recovery; coherent ditch/track/wheat/bike materials; correct horse forehooves/rear and develop crowd; leader design protected")
    task["execution_authority"] = {"source": "results/sikh300/STRATEGY.md", "scope": "Local reversible scene correction; no new paid calls, installations or leader redesign"}
    for rel in ("results/sikh300/STRATEGY.md", "results/sikh299/LEARNINGS.md",
                "results/sikh299/REVIEW.md", "results/sikh299/MOTION_BRIEF.md",
                ".runtime/art-direction/series01-sikh299/controls-07/sequence.blend"):
        task["inputs"][rel] = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    packet = pk.task_packet(ROOT, task)
    for name, data in (("task", task), ("packet", packet)):
        (OUT / (name + ".json")).write_text(json.dumps(data, indent=2) + "\n")
    (OUT / "packet.md").write_text(pk.packet_markdown(packet))
    print(pk.packet_markdown(packet))
    if not packet["dispatch_ready"]:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
