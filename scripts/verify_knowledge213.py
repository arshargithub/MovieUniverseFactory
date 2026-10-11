"""Reproducible offline qualification of the bounded context pilot, not scene QA."""
import json
import subprocess
import sys
from pathlib import Path

from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/knowledge/pilot/generated"


def save(name, value):
    (OUTPUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    evaluation = pk.evaluate(ROOT)
    save("evaluation.json", evaluation)
    save("coverage.json", pk.coverage(ROOT))
    packets = {}
    restarts = {}
    for name in ["rein", "audio", "render", "pilot"]:
        taskpath = f"docs/knowledge/pilot/tasks/{name}.json"
        packet = pk.task_packet(ROOT, pk.read_json(ROOT, taskpath))
        packets[name] = packet
        save(f"{name}-packet.json", packet)
        (OUTPUT / f"{name}-packet.md").write_text(pk.packet_markdown(packet))
        destination = f".runtime/knowledge-pilot213/restart-{name}.json"
        child = subprocess.run([sys.executable, "-m", "movie_factory.production_knowledge", "--root", str(ROOT), "packet", "--task", taskpath, "--output", destination], capture_output=True, text=True, cwd=ROOT)
        restarts[name] = {"returncode": child.returncode, "identical": child.returncode == 0 and pk.read_json(ROOT, destination) == packet}
    # Actual planning input promoted to execution must remain blocked on unselected narrative.
    audio_execution = {**packets["audio"]["task"], "phase": "execution", "open_decisions": []}
    blocked_audio = pk.task_packet(ROOT, audio_execution)
    save("audio-execution-blocked.json", blocked_audio)
    # Empty evidence on a real packet must never yield a production readiness claim.
    no_evidence = pk.check_review(ROOT, packets["rein"], {"packet_digest": packets["rein"]["packet_digest"]})
    save("rein-without-evidence-blocked.json", no_evidence)
    test = subprocess.run([sys.executable, "-m", "pytest", "tests/test_production_knowledge.py", "tests/test_render210_probe.py", "tests/unit", "-q"], capture_output=True, text=True, cwd=ROOT)
    result = {"test_returncode": test.returncode, "test_stdout": test.stdout, "test_stderr": test.stderr,
              "finite_retrieval_passed": evaluation["passed"], "fresh_process_restarts": restarts,
              "audio_execution_blockers": blocked_audio["blockers"],
              "unreviewed_rein_handoff_blocked": not no_evidence["ready_for_review"],
              "source_implementation": {p: pk.file_hash(ROOT / p) for p in ["src/movie_factory/production_knowledge.py", "tests/test_production_knowledge.py", "scripts/verify_knowledge213.py", pk.CATALOG, pk.PINS, "docs/knowledge/pilot/expectations.json"]},
              "production_assets_modified": False, "external_calls": 0,
              "scope": "Source files, offline tests, planning packets and CLI evidence gates; no new audiovisual/asset qualification. Fresh Python processes, not an independent LLM run."}
    result["passed"] = test.returncode == 0 and evaluation["passed"] and all(x["identical"] for x in restarts.values()) and not blocked_audio["dispatch_ready"] and not no_evidence["ready_for_review"]
    save("verification.json", result)
    print(json.dumps({"passed": result["passed"], "tests": test.stdout.strip().splitlines()[-1:], "restarts": restarts}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
