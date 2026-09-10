"""Opt-in native tests for the frozen 3D-02 asset boundary; no provider calls."""
import json
import os
from pathlib import Path

import pytest

from movie_factory.asset_controller import _resolved_plan
from movie_factory.adapters.blender.runner import run_blender
from movie_factory.validators.assets import validate_external_baseline, validate_external_revision
from movie_factory.validators.structural import compare_snapshots


ROOT = Path(__file__).resolve().parents[2]
STAGED = ROOT / ".runtime/assets/3d-02/staged-v2"
BINARY = os.getenv("BLENDER_BIN", "/Applications/Blender.app/Contents/MacOS/Blender")
PROFILE = {"name":"asset_native_smoke","width":320,"height":180,"samples":2,"device":"CPU","shots":["shot_A"]}
OPS = [{"op":"translate_entity","entity_id":"motorcycle_01","delta_m":[0.6,0,0]}, {"op":"rotate_entity_z","entity_id":"sword_01","degrees":25}]

pytestmark = [
    pytest.mark.blender,
    pytest.mark.skipif(os.getenv("MF_NATIVE_TEST") != "1", reason="Opt-in native Blender integration"),
    pytest.mark.skipif(not (STAGED / "staged-manifest.json").exists(), reason="Frozen assets are not staged"),
]


def job(tmp_path, name, mode, **kwargs):
    output=tmp_path/name
    result=run_blender({"mode":mode,"output_dir":str(output),"profile":PROFILE,"seed":302,**kwargs},blender_bin=BINARY,timeout=240)
    return result, output


def test_external_assets_persist_and_revise(tmp_path):
    template=json.loads((ROOT/"feasibility/3d/3d-02/scene.json").read_text())
    plan=_resolved_plan(template,STAGED)
    result, build=job(tmp_path,"build","build_external",plan=plan); assert result["ok"], result
    before=json.loads((build/"snapshot.json").read_text())
    assert validate_external_baseline(before,template)["passed"]
    result, reopen=job(tmp_path,"reopen","inspect",parent_native=str(build/"scene.blend")); assert result["ok"], result
    assert compare_snapshots(before,json.loads((reopen/"snapshot.json").read_text()))["passed"]
    result, revised=job(tmp_path,"revised","revise_external",parent_native=str(build/"scene.blend"),operations=OPS); assert result["ok"], result
    after=json.loads((revised/"snapshot.json").read_text())
    assert validate_external_revision(before,after,OPS)["passed"]
    result,replayed=job(tmp_path/"different-depth","replayed","revise_external",parent_native=str(build/"scene.blend"),operations=OPS); assert result["ok"], result
    assert compare_snapshots(after,json.loads((replayed/"snapshot.json").read_text()))["passed"]


def test_external_worker_rejects_digest_and_revision_scope(tmp_path):
    template=json.loads((ROOT/"feasibility/3d/3d-02/scene.json").read_text())
    plan=_resolved_plan(template,STAGED)
    plan["entities"][1]["source"]["sha256"]="0"*64
    result,_=job(tmp_path,"bad-digest","build_external",plan=plan)
    assert not result["ok"] and "digest mismatch" in result["error"].lower()

    plan=_resolved_plan(template,STAGED)
    result,build=job(tmp_path,"valid-parent","build_external",plan=plan); assert result["ok"], result
    invalid=[{"op":"translate_entity","entity_id":"courtyard_01","delta_m":[99,0,0]},OPS[1]]
    result,_=job(tmp_path,"bad-revision","revise_external",parent_native=str(build/"scene.blend"),operations=invalid)
    assert not result["ok"] and "frozen two-operation" in result["error"]
