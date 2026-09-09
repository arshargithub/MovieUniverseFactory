"""Opt-in native persistence and revision control, never calls an LLM.

Run MF_NATIVE_TEST=1 .venv/bin/pytest tests/native -q in a process allowed to
initialize Blender's macOS services. Default pytest remains lightweight.
"""
import hashlib
import json
import os
from pathlib import Path

import pytest
from PIL import Image

from movie_factory.adapters.blender.runner import run_blender
from movie_factory.validators.structural import validate_baseline, validate_revision


pytestmark = [
    pytest.mark.blender,
    pytest.mark.skipif(os.getenv("MF_NATIVE_TEST") != "1", reason="Opt-in native Blender integration"),
]
ROOT = Path(__file__).resolve().parents[2]
BINARY = os.getenv("BLENDER_BIN", "/Applications/Blender.app/Contents/MacOS/Blender")
PROFILE = {"name": "native_smoke", "width": 320, "height": 180, "samples": 4,
           "device": "CPU", "shots": ["shot_A", "shot_B", "shot_C"]}


def run_job(tmp_path, name, mode, **kwargs):
    output = tmp_path / name
    status = run_blender({"mode": mode, "output_dir": str(output), "profile": PROFILE,
                          "seed": 1701, **kwargs}, blender_bin=BINARY, timeout=180)
    assert status["ok"], f"{status}; inspect {output}/stderr.log"
    assert not any("TOKEN" in n or "KEY" in n for n in status["environment_names"])
    return output


def test_native_save_reopen_revision_render(tmp_path):
    plan = json.loads((ROOT / "feasibility/3d/3d-01/fixtures/plan.json").read_text())
    baseline = run_job(tmp_path, "build", "build", plan=plan)
    native = baseline / "scene.blend"
    parent_hash = hashlib.sha256(native.read_bytes()).hexdigest()
    reopened = run_job(tmp_path, "reopen", "inspect", parent_native=str(native))
    before = json.loads((reopened / "snapshot.json").read_text())
    assert before == json.loads((baseline / "snapshot.json").read_text())
    check = validate_baseline(before, plan)
    assert check["passed"], check
    operations = [{"op": "translate_toward", "entity_id": "coffee_table_01", "target_entity_id": "sofa_01", "distance_m": .4},
                  {"op": "set_base_color", "entity_id": "helmet_01", "material_id": "helmet_shell_01", "color_hex": "#163D2A"}]
    changed = run_job(tmp_path, "revise", "revise", parent_native=str(native), operations=operations)
    revised_inspection = run_job(tmp_path, "revised-reopen", "inspect", parent_native=str(changed / "scene.blend"))
    after = json.loads((revised_inspection / "snapshot.json").read_text())
    check = validate_revision(before, after, operations)
    assert check["passed"], check
    assert hashlib.sha256(native.read_bytes()).hexdigest() == parent_hash
    repeated = run_job(tmp_path, "retry-from-parent", "revise", parent_native=str(native), operations=operations)
    assert json.loads((repeated / "snapshot.json").read_text()) == after
    rendered = run_job(tmp_path, "render", "render", parent_native=str(changed / "scene.blend"))
    for shot in PROFILE["shots"]:
        for folder in ("renders", "masks"):
            with Image.open(rendered / folder / f"{shot}.png") as img:
                img.load()
                assert img.size == (320, 180)
                assert img.getbbox() is not None
