"""Opt-in native 3D-03 rig, animation, persistence, and failure tests."""
import json
import os
from pathlib import Path

import pytest

from movie_factory.adapters.blender.runner import run_blender
from movie_factory.character_controller import resolved_character_plan
from movie_factory.validators.character import validate_character_baseline,validate_character_revision
from movie_factory.validators.structural import compare_snapshots


ROOT=Path(__file__).resolve().parents[2]
STAGED=ROOT/".runtime/assets/3d-03/staged-v1"
BINARY=os.getenv("BLENDER_BIN","/Applications/Blender.app/Contents/MacOS/Blender")
PROFILE={"name":"character_native_smoke","width":320,"height":180,"samples":2,"device":"CPU","shots":["shot_A"]}
OPS=[{"op":"set_character_skin","entity_id":"character_01","from":"cyborg","to":"skater"},{"op":"set_character_action","entity_id":"character_01","from":"idle","to":"run"}]

pytestmark=[pytest.mark.blender,pytest.mark.skipif(os.getenv("MF_NATIVE_TEST")!="1",reason="Opt-in native Blender integration"),pytest.mark.skipif(not (STAGED/"staged-manifest.json").exists(),reason="Frozen character assets are not staged")]


def job(tmp_path,name,mode,**kwargs):
    output=tmp_path/name
    status=run_blender({"mode":mode,"output_dir":str(output),"profile":PROFILE,"seed":303,**kwargs},blender_bin=BINARY,timeout=300)
    return status,output


def test_character_persists_revises_and_replays(tmp_path):
    template=json.loads((ROOT/"feasibility/3d/3d-03/scene.json").read_text()); plan=resolved_character_plan(template,STAGED)
    status,build=job(tmp_path,"build","build_character",plan=plan); assert status["ok"],status
    before=json.loads((build/"snapshot.json").read_text()); assert validate_character_baseline(before,template)["passed"]
    status,reopen=job(tmp_path,"reopen","inspect",parent_native=str(build/"scene.blend")); assert status["ok"],status
    assert compare_snapshots(before,json.loads((reopen/"snapshot.json").read_text()))["passed"]
    status,revised=job(tmp_path,"revised","revise_character",parent_native=str(build/"scene.blend"),operations=OPS); assert status["ok"],status
    after=json.loads((revised/"snapshot.json").read_text()); assert validate_character_revision(before,after,OPS)["passed"]
    status,replayed=job(tmp_path/"different-depth","replay","revise_character",parent_native=str(build/"scene.blend"),operations=OPS); assert status["ok"],status
    assert compare_snapshots(after,json.loads((replayed/"snapshot.json").read_text()))["passed"]


def test_character_rejects_wrong_digest_and_revision_scope(tmp_path):
    template=json.loads((ROOT/"feasibility/3d/3d-03/scene.json").read_text()); plan=resolved_character_plan(template,STAGED)
    plan["clips"]["idle"]["sha256"]="0"*64
    status,_=job(tmp_path,"bad-digest","build_character",plan=plan)
    assert not status["ok"] and "digest mismatch" in status["error"].lower()
    plan=resolved_character_plan(template,STAGED); status,build=job(tmp_path,"parent","build_character",plan=plan); assert status["ok"],status
    bad=[OPS[0],{"op":"set_character_action","entity_id":"character_01","from":"idle","to":"jump"}]
    status,_=job(tmp_path,"bad-operation","revise_character",parent_native=str(build/"scene.blend"),operations=bad)
    assert not status["ok"] and "frozen skin and action" in status["error"]


def test_authored_jump_is_explicit_and_persists(tmp_path):
    template=json.loads((ROOT/"feasibility/3d/3d-03-1/scene.json").read_text()); plan=resolved_character_plan(template,STAGED)
    status,build=job(tmp_path,"authored-build","build_character",plan=plan); assert status["ok"],status
    before=json.loads((build/"snapshot.json").read_text()); assert validate_character_baseline(before,template)["passed"]
    jump=before["actions"]["character_action_jump"]["custom_properties"]
    assert jump["mf_clip_semantics"]=="authored_full_jump"
    assert jump["mf_source_role"]=="pose_reference_only"
    assert jump["mf_authored_peak_height_m"]==.34
    assert before["actions"]["character_action_idle"]["custom_properties"]["mf_nla_time_scale"]==.8
    assert before["actions"]["character_action_run"]["custom_properties"]["mf_nla_time_scale"]==1.0
    status,reopen=job(tmp_path,"authored-reopen","inspect",parent_native=str(build/"scene.blend")); assert status["ok"],status
    assert compare_snapshots(before,json.loads((reopen/"snapshot.json").read_text()))["passed"]


def test_production_transfer_is_order_independent_at_integer_and_fractional_frames(tmp_path):
    template=json.loads((ROOT/"feasibility/3d/3d-03-1/scene.json").read_text()); plan=resolved_character_plan(template,STAGED)
    status,output=job(tmp_path,"production-regression","character_production_regression",plan=plan); assert status["ok"],status
    report=json.loads((output/"production-regression.json").read_text())
    assert report["passed"] and report["provider_calls"]==0
    assert set(report["clips"])=={"idle","run","jump"}
    assert all(clip["fractional_sample_count"]>0 for clip in report["clips"].values())
