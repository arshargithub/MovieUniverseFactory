import json
import os
from pathlib import Path

import pytest

from movie_factory.adapters.blender.runner import run_blender
from movie_factory.interaction_controller import _resolved_scene
from movie_factory.validators.interaction import (CONTROL_EXPECTATIONS, interaction_protected_flags,
                                                   validate_control_sensitivity, validate_interaction_metrics)


ROOT = Path(__file__).resolve().parents[2]
BINARY = os.getenv("BLENDER_BIN", "/Applications/Blender.app/Contents/MacOS/Blender")
BASELINE = ROOT/"runs/3d031/character-v2-20260911T012644Z-2d7d8605/initial/build/scene.blend"
PROFILE = {"name":"interaction_native_smoke","width":320,"height":180,"samples":2,"device":"CPU","shots":["shot_A"]}

pytestmark = [
    pytest.mark.blender,
    pytest.mark.skipif(os.getenv("MF_NATIVE_TEST") != "1", reason="Opt-in native Blender integration"),
    pytest.mark.skipif(not BASELINE.exists(), reason="Accepted 3D-03.1 native baseline is unavailable"),
]


def _job(tmp_path, name, mode, **kwargs):
    output = tmp_path/name
    status = run_blender({"mode":mode,"output_dir":str(output),"profile":PROFILE,"seed":305,**kwargs},
                         blender_bin=BINARY,timeout=600)
    assert status["ok"], status
    return output


def _fixtures():
    campaign=json.loads((ROOT/"feasibility/3d/3d-05/campaign.json").read_text())
    scene=_resolved_scene(ROOT,json.loads((ROOT/"feasibility/3d/3d-05/scene.json").read_text()))
    parent=json.loads(BASELINE.with_name("snapshot.json").read_text())
    return campaign,scene,parent


def _validate(tmp_path, name, campaign, scene, parent, control=None):
    mode="build_interaction_control" if control else "build_interaction"
    build=_job(tmp_path,name+"-build",mode,parent_native=str(BASELINE),interaction=scene,role="candidate",control=control)
    evidence=_job(tmp_path,name+"-evidence","interaction_evidence",parent_native=str(build/"scene.blend"),
                  campaign=campaign,render_frames=False)
    raw=json.loads((evidence/"interaction-metrics.json").read_text())
    raw["protected"]=interaction_protected_flags(parent,json.loads((build/"snapshot.json").read_text()))
    raw["persistence"]={key:True for key in ("checkpoints_exact","save_reopen_semantic_exact",
                                              "offline_replay_semantic_exact","offline_replay_geometry_within_tolerance")}
    return validate_interaction_metrics(raw,campaign)


def test_interaction_passes_dense_native_measurement(tmp_path):
    campaign,scene,parent=_fixtures()
    result=_validate(tmp_path,"accepted",campaign,scene,parent)
    assert result["passed"],result["errors"]
    raw=json.loads((tmp_path/"accepted-evidence/interaction-metrics.json").read_text())
    for role,grasp in (("baseline",40),("candidate",36)):
        before=next(row for row in raw["samples"] if row["frame"] == grasp-.001)
        assert before[role+"_supported_translation_error_m"] < 1e-6


def test_actual_interaction_controls_are_detected(tmp_path):
    campaign,scene,parent=_fixtures(); results={}
    for control in campaign["negative_controls"]:
        results[control]=_validate(tmp_path,control,campaign,scene,parent,control)
        assert CONTROL_EXPECTATIONS[control] <= set(results[control]["errors"]),results[control]["errors"]
        if control in {"open_hand_attachment","oversized_handle"}:
            # A correct tracking proxy must not conceal an invalid mesh grasp.
            checks={item["name"]:item["passed"] for item in results[control]["checks"]}
            assert checks["grip.translation"] and checks["grip.orientation"]
    assert validate_control_sensitivity(results)["passed"]
