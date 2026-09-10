"""Deny-by-default validation for the frozen 3D-03 character experiment."""
from __future__ import annotations

import copy
import re
from typing import Any

from .structural import compare_snapshots


EXPECTED_ACTIONS={"character_action_idle":(1.0,33.0),"character_action_run":(1.0,17.0),"character_action_jump":(1.0,13.0)}
EXPECTED_OPS=[
    {"op":"set_character_skin","entity_id":"character_01","from":"cyborg","to":"skater"},
    {"op":"set_character_action","entity_id":"character_01","from":"idle","to":"run"},
]


def _check(checks:list[dict[str,Any]],name:str,passed:bool,details:Any=None)->None:
    checks.append({"name":name,"passed":bool(passed),"details":details})


def _result(checks):
    return {"passed":all(item["passed"] for item in checks),"checks":checks,
            "errors":[item["name"] for item in checks if not item["passed"]]}


def validate_character_baseline(snapshot:dict,plan:dict)->dict:
    checks=[]
    _check(checks,"identity.scene",snapshot.get("scene_id")==plan.get("scene_id"))
    _check(checks,"identity.entities",set(snapshot.get("entities",{}))=={"character_01","stage_01"},sorted(snapshot.get("entities",{})))
    _check(checks,"snapshot.supported",snapshot.get("unsupported")==[],snapshot.get("unsupported"))
    external=snapshot.get("external_files",[])
    _check(checks,"assets.images_packed",len(external)==2 and all(item.get("type")=="image" and item.get("packed") for item in external),external)
    observed={item.get("packed_sha256") for item in snapshot.get("images",{}).values()}
    required=set(plan.get("required_packed_image_sha256",[]))
    _check(checks,"assets.skin_identity",required==observed,{"required":sorted(required),"observed":sorted(x for x in observed if x)})
    try:
        entity=snapshot["entities"]["character_01"]; mesh=snapshot["objects"]["character_01_mesh"]; arm=snapshot["objects"]["character_01_armature"]
        bounds=entity["bounds_world"]; height=bounds["max"][2]-bounds["min"][2]
        _check(checks,"normalization.height",abs(height-1.75)<=1e-4,{"height_m":height})
        _check(checks,"normalization.ground_contact",abs(bounds["min"][2])<=1e-4,{"bottom_z_m":bounds["min"][2]})
        _check(checks,"topology.mesh",len(mesh["source_geometry"]["vertices"])==804 and len(mesh["source_geometry"]["faces"])==826)
        _check(checks,"rig.vertex_groups",len(mesh["vertex_groups"])==32 and all(mesh["vertex_groups"].values()))
        _check(checks,"rig.armature_modifier",len(mesh["modifiers"])==1 and mesh["modifiers"][0].get("type")=="ARMATURE" and mesh["modifiers"][0].get("target_object")=="character_01_armature",mesh["modifiers"])
        bones=arm["armature"]["bones"]
        _check(checks,"rig.bones",len(bones)==58 and all(item.get("id")=="character_01_bone_"+name for name,item in bones.items()))
        _check(checks,"actions.exact_set",set(snapshot["actions"])==set(EXPECTED_ACTIONS),sorted(snapshot["actions"]))
        for action_id,frame_range in EXPECTED_ACTIONS.items():
            action=snapshot["actions"][action_id]
            _check(checks,f"actions.{action_id}.range",tuple(action["frame_range"])==frame_range,action["frame_range"])
            _check(checks,f"actions.{action_id}.curves",len(action["curves"])==131)
            referenced=set(); grounding=[]
            allowed=True
            for curve in action["curves"].values():
                path=curve["data_path"]; match=re.fullmatch(r'pose\.bones\["([^"]+)"\]\.rotation_quaternion',path)
                if match: referenced.add(match.group(1))
                elif path=="location": grounding.append(curve)
                else: allowed=False
            grounding_by_index={curve["array_index"]:curve for curve in grounding}
            lateral_zero=all(all(abs(key["co"][1])<=1e-9 for key in grounding_by_index[index]["keyframes"]) for index in (0,1)) if set(grounding_by_index)=={0,1,2} else False
            vertical_bounded=all(abs(key["co"][1])<=.5 for key in grounding_by_index.get(2,{}).get("keyframes",[])) and bool(grounding_by_index.get(2,{}).get("keyframes",[]))
            _check(checks,f"actions.{action_id}.bone_compatibility",allowed and referenced==set(mesh["vertex_groups"]),{"referenced_bones":len(referenced)})
            _check(checks,f"actions.{action_id}.in_place_grounding",lateral_zero and vertical_bounded,{"location_curves":sorted(grounding_by_index)})
            _check(checks,f"actions.{action_id}.slot",len(action["slots"])==1 and action["slots"][0]["target_id_type"]=="OBJECT",action["slots"])
        _check(checks,"performance.active_idle",arm["animation"]["action"]=="character_action_idle" and arm["custom_properties"].get("mf_active_action")=="idle",arm["animation"])
        _check(checks,"performance.normalization",arm["custom_properties"].get("mf_animation_normalization")=="same_skeleton_pose_bake_v1")
        poses=arm["armature"]["sampled_pose_matrices"]
        _check(checks,"performance.idle_evaluates",poses["1"]!=poses["9"],"sampled bone matrices at frames 1 and 9")
        material=snapshot["materials"]["character_01_skin_material"]
        _check(checks,"wardrobe.active_cyborg",material["custom_properties"].get("mf_active_skin")=="cyborg" and material["nodes"]["Character Skin"]["image"]=="character_01_skin_cyborg")
        _check(checks,"identity.no_temporary_imports",not any("Root|Root|" in key for key in snapshot["actions"]) and not any(obj.get("id")=="Root" for obj in snapshot["objects"].values()))
    except (KeyError,TypeError,ValueError) as exc:
        _check(checks,"snapshot.malformed",False,f"{type(exc).__name__}: {exc}")
    return _result(checks)


def validate_character_revision(before:dict,after:dict,operations:list[dict])->dict:
    checks=[]; _check(checks,"revision.operations_frozen",operations==EXPECTED_OPS)
    try:
        expected=copy.deepcopy(before)
        # Explicit authorized semantic changes.
        expected["objects"]["character_01"]["custom_properties"]["mf_active_skin"]="skater"
        arm_expected=expected["objects"]["character_01_armature"]
        arm_expected["custom_properties"]["mf_active_action"]="run"
        arm_expected["animation"]["action"]="character_action_run"
        material=expected["materials"]["character_01_skin_material"]
        material["custom_properties"]["mf_active_skin"]="skater"
        material["nodes"]["Character Skin"]["image"]="character_01_skin_skater"
        # Evaluated state is allowed to derive from the newly assigned action;
        # source/rest state and the complete action datablocks remain protected.
        expected["entities"]["character_01"]["bounds_world"]=after["entities"]["character_01"]["bounds_world"]
        for oid in ("character_01_armature","character_01_mesh"):
            for field in ("location","rotation_euler","scale","matrix_local","matrix_world","dimensions","bounds_world","evaluated_geometry"):
                expected["objects"][oid][field]=copy.deepcopy(after["objects"][oid][field])
        arm_expected["armature"]["sampled_pose_matrices"]=copy.deepcopy(after["objects"]["character_01_armature"]["armature"]["sampled_pose_matrices"])
        comparison=compare_snapshots(expected,after)
        _check(checks,"revision.exact_expected_state",comparison["passed"],comparison["differences"][:25])
        _check(checks,"revision.action_data_unchanged",compare_snapshots(before["actions"],after["actions"])["passed"])
        _check(checks,"revision.rig_rest_unchanged",compare_snapshots(before["objects"]["character_01_armature"]["armature"]["bones"],after["objects"]["character_01_armature"]["armature"]["bones"])["passed"])
        _check(checks,"revision.source_mesh_unchanged",compare_snapshots(before["objects"]["character_01_mesh"]["source_geometry"],after["objects"]["character_01_mesh"]["source_geometry"])["passed"])
        _check(checks,"revision.weights_unchanged",compare_snapshots(before["objects"]["character_01_mesh"]["vertex_groups"],after["objects"]["character_01_mesh"]["vertex_groups"])["passed"])
        _check(checks,"revision.pose_changed",before["objects"]["character_01_armature"]["armature"]["sampled_pose_matrices"]["9"]!=after["objects"]["character_01_armature"]["armature"]["sampled_pose_matrices"]["9"])
    except (KeyError,TypeError,ValueError) as exc:
        _check(checks,"snapshot.malformed",False,f"{type(exc).__name__}: {exc}")
    return _result(checks)
