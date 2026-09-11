"""Trusted, data-only procedural Blender adapter for Movie Factory 3D-01.

No generated Python, shell, downloads, arbitrary paths in plans, or dynamic
add-ons are executed. Entity dimensions are total envelopes. Sofa seat cushion
support is exactly 0.54 * sofa height above its root, with local front at -Y.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
import traceback

import bpy
from mathutils import Matrix,Quaternion,Vector


def load_inspector():
    spec = importlib.util.spec_from_file_location("mf_blender_inspect", Path(__file__).with_name("inspect.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def srgb_channel(c):
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4


def color(hex_color):
    if not isinstance(hex_color, str) or len(hex_color) != 7 or not hex_color.startswith("#"):
        raise ValueError("Expected a six-digit RGB hex color")
    return tuple(srgb_channel(int(hex_color[i:i + 2], 16) / 255) for i in (1, 3, 5)) + (1.0,)


def file_sha256(path):
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""):
            digest.update(chunk)
    return digest.hexdigest()


def import_source_asset(spec):
    if not isinstance(spec,dict) or set(spec)!={"path","sha256","format"}:
        raise ValueError("Asset import requires only path, sha256, and format")
    path=Path(spec["path"])
    if not path.is_absolute() or not path.is_file() or path.is_symlink():
        raise ValueError("Asset path must be an absolute regular file")
    expected_format=spec["format"].lower()
    if expected_format not in {"glb","fbx"} or path.suffix.lower()!="."+expected_format:
        raise ValueError("Asset format is not allowlisted or does not match its suffix")
    if file_sha256(path)!=spec["sha256"]:
        raise ValueError("Asset digest mismatch")
    before=set(bpy.data.objects)
    if expected_format=="glb":
        bpy.ops.import_scene.gltf(filepath=str(path),import_pack_images=True)
    else:
        bpy.ops.import_scene.fbx(filepath=str(path),use_anim=False)
    imported=sorted(set(bpy.data.objects)-before,key=lambda item:(item.name,item.type))
    if not imported or not any(obj.type=="MESH" for obj in imported):
        raise ValueError("Asset import produced no mesh")
    return imported


def import_animated_fbx(spec):
    if not isinstance(spec,dict) or set(spec)!={"path","sha256","format"}:
        raise ValueError("Animated import requires only path, sha256, and format")
    path=Path(spec["path"])
    if not path.is_absolute() or not path.is_file() or path.is_symlink() or spec["format"]!="fbx" or path.suffix.lower()!=".fbx":
        raise ValueError("Animated asset must be an absolute regular FBX")
    if file_sha256(path)!=spec["sha256"]:
        raise ValueError("Animated asset digest mismatch")
    before_objects=set(bpy.data.objects); before_actions=set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=str(path),use_anim=True)
    objects=sorted(set(bpy.data.objects)-before_objects,key=lambda item:(item.name,item.type))
    actions=sorted(set(bpy.data.actions)-before_actions,key=lambda item:item.name)
    if not objects or not any(obj.type=="ARMATURE" for obj in objects):
        raise ValueError("Animated FBX produced no armature")
    return objects,actions


def action_channels(action):
    curves=[]
    if hasattr(action,"fcurves"):
        try: curves=list(action.fcurves)
        except RuntimeError: curves=[]
    if not curves and hasattr(action,"layers"):
        for layer in action.layers:
            for strip in layer.strips:
                for bag in getattr(strip,"channelbags",[]): curves.extend(bag.fcurves)
    return curves


def animation_probe(spec):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    imported,actions=import_animated_fbx(spec)
    bpy.context.view_layer.update()
    meshes=[obj for obj in imported if obj.type=="MESH"]
    armatures=[obj for obj in imported if obj.type=="ARMATURE"]
    evaluated={}
    scene=bpy.context.scene; original=scene.frame_current
    diagnostic_bones=("Hips","Spine","Chest","Head","LeftUpLeg","LeftLeg","LeftFoot",
                      "RightUpLeg","RightLeg","RightFoot","LeftArm","LeftForeArm","LeftHand",
                      "RightArm","RightForeArm","RightHand")
    if len(armatures)==1:
        armature=armatures[0]
        for action in actions:
            assign_character_action(armature,action)
            first,last=(int(round(value)) for value in action.frame_range)
            samples=[]
            for frame in range(first,last+1):
                scene.frame_set(frame); bpy.context.view_layer.update()
                hips=armature.pose.bones.get("Hips")
                low,high=evaluated_bounds(meshes) if meshes else ([None]*3,[None]*3)
                samples.append({"frame":frame,"armature_location":list(armature.location),
                                "hips_basis_location":list(hips.matrix_basis.translation) if hips else None,
                                "bone_pose":{name:{"head":list(armature.pose.bones[name].head),
                                                   "tail":list(armature.pose.bones[name].tail),
                                                   "rotation_quaternion":list(armature.pose.bones[name].matrix.to_quaternion())}
                                             for name in diagnostic_bones if name in armature.pose.bones},
                                "bounds_min":low,"bounds_max":high})
            evaluated[action.name]=samples
    scene.frame_set(original); bpy.context.view_layer.update()
    return {
        "schema_version":"1.0","source_sha256":spec["sha256"],"object_count":len(imported),
        "object_types":sorted({obj.type for obj in imported}),
        "objects":[{"name":obj.name,"type":obj.type,"parent":obj.parent.name if obj.parent else None,
                    "modifiers":[mod.type for mod in obj.modifiers],"vertex_groups":[group.name for group in obj.vertex_groups]} for obj in imported],
        "topology":{"vertices":sum(len(obj.data.vertices) for obj in meshes),"polygons":sum(len(obj.data.polygons) for obj in meshes)},
        "armatures":[{"name":obj.name,"bones":[{"name":bone.name,"parent":bone.parent.name if bone.parent else None,
                      "head":list(bone.head_local),"tail":list(bone.tail_local),"use_deform":bone.use_deform,
                      "constraints":[{"type":constraint.type,"target":getattr(getattr(constraint,"target",None),"name",None),
                                      "subtarget":getattr(constraint,"subtarget",None),"influence":constraint.influence}
                                     for constraint in obj.pose.bones[bone.name].constraints]}
                      for bone in obj.data.bones]} for obj in armatures],
        "actions":[{"name":action.name,"frame_range":list(action.frame_range),"curve_count":len(action_channels(action)),
                    "keyframe_count":sum(len(curve.keyframe_points) for curve in action_channels(action)),
                    "data_paths":sorted({curve.data_path for curve in action_channels(action)})} for action in actions],
        "evaluated_samples":evaluated,
    }


def asset_probe(spec):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    imported=import_source_asset(spec)
    bpy.context.view_layer.update()
    meshes=[obj for obj in imported if obj.type=="MESH"]
    points=[obj.matrix_world@Vector(corner) for obj in meshes for corner in obj.bound_box]
    bounds={"min":[min(p[i] for p in points) for i in range(3)],"max":[max(p[i] for p in points) for i in range(3)]}
    dimensions=[bounds["max"][i]-bounds["min"][i] for i in range(3)]
    materials=sorted({mat for obj in meshes for mat in obj.data.materials if mat},key=lambda mat:mat.name)
    return {
        "schema_version":"1.0","source_sha256":spec["sha256"],"format":spec["format"],
        "object_count":len(imported),"mesh_count":len(meshes),
        "vertex_count":sum(len(obj.data.vertices) for obj in meshes),
        "polygon_count":sum(len(obj.data.polygons) for obj in meshes),
        "object_types":sorted({obj.type for obj in imported}),
        "object_names":[obj.name for obj in imported],"bounds":bounds,"dimensions":dimensions,
        "materials":[{"name":mat.name,"uses_nodes":mat.use_nodes,"node_types":sorted(node.bl_idname for node in mat.node_tree.nodes) if mat.use_nodes else []} for mat in materials],
        "images":[{"name":image.name,"source":image.source,"packed":bool(image.packed_file)} for image in sorted(bpy.data.images,key=lambda image:image.name)],
    }


def identify(obj, oid, entity, kind):
    obj.name = oid
    obj["mf_id"] = oid
    obj["mf_entity"] = entity or ""
    obj["mf_kind"] = kind
    obj["mf_creation_id"] = hashlib.sha256((bpy.context.scene["mf_scene_id"] + ":" + str(bpy.context.scene["mf_seed"]) + ":procedural-v1:" + oid).encode()).hexdigest()
    if obj.data:
        obj.data.name = oid + "_data"
        obj.data["mf_id"] = oid + "_data"
    return obj


def identify_external(obj, oid, entity, kind, source_sha256):
    obj.name = oid
    obj["mf_id"] = oid
    obj["mf_entity"] = entity or ""
    obj["mf_kind"] = kind
    obj["mf_source_sha256"] = source_sha256
    obj["mf_creation_id"] = hashlib.sha256(
        (bpy.context.scene["mf_scene_id"] + ":external-v1:" + oid + ":" + source_sha256).encode()
    ).hexdigest()
    if obj.data:
        obj.data.name = oid + "_data"
        obj.data["mf_id"] = oid + "_data"
    return obj


def verified_image(spec):
    if not isinstance(spec, dict) or set(spec) != {"path", "sha256"}:
        raise ValueError("Texture requires only path and sha256")
    path = Path(spec["path"])
    if not path.is_absolute() or not path.is_file() or path.is_symlink():
        raise ValueError("Texture path must be an absolute regular file")
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg"} or file_sha256(path) != spec["sha256"]:
        raise ValueError("Texture format or digest mismatch")
    image = bpy.data.images.load(str(path), check_existing=False)
    image["mf_source_sha256"] = spec["sha256"]
    return image


def character_material(entity_id, skins):
    if set(skins)!={"cyborg","skater"}:
        raise ValueError("Character requires exactly cyborg and skater skins")
    loaded={name:verified_image(spec) for name,spec in skins.items()}
    for name,image in loaded.items():
        image.name=f"{entity_id}_skin_{name}"
        image["mf_id"]=image.name
        image["mf_skin_role"]=name
        image.use_fake_user=True
    mat=bpy.data.materials.new(entity_id+"_skin_material")
    mat["mf_id"]=mat.name; mat["mf_active_skin"]="cyborg"; mat.use_nodes=True
    tree=mat.node_tree; tree.nodes.clear()
    output=tree.nodes.new("ShaderNodeOutputMaterial"); output.name="Material Output"
    bsdf=tree.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.name="Principled BSDF"; bsdf.inputs["Roughness"].default_value=.62
    texture=tree.nodes.new("ShaderNodeTexImage"); texture.name="Character Skin"; texture.image=loaded["cyborg"]; texture.interpolation="Linear"
    tree.links.new(texture.outputs["Color"],bsdf.inputs["Base Color"]); tree.links.new(texture.outputs["Alpha"],bsdf.inputs["Alpha"])
    tree.links.new(bsdf.outputs["BSDF"],output.inputs["Surface"])
    return mat,loaded


def import_character_action(spec, clip_name, target_armature, target_mesh,capture_order="forward"):
    if capture_order not in {"forward","reverse","isolated"}:
        raise ValueError("Unsupported character source capture order")
    objects,actions=import_animated_fbx(spec)
    source_armatures=[obj for obj in objects if obj.type=="ARMATURE"]
    if len(source_armatures)!=1:
        raise ValueError("Animation FBX did not contain exactly one source armature")
    candidates=[action for action in actions if action.name.lower().endswith("|"+clip_name.lower())]
    if len(candidates)!=1:
        raise ValueError("Animation FBX did not contain exactly one named clip: "+clip_name)
    source_armature=source_armatures[0]; source=candidates[0]
    source_names={bone.name for bone in source_armature.pose.bones}; target_names={bone.name for bone in target_armature.pose.bones}
    if source_names!=target_names:
        raise ValueError("Animation skeleton does not exactly match the canonical character skeleton")
    assign_character_action(source_armature,source)
    # Animation-only FBXs can encode clip-specific bind/rest transforms. Raw
    # curve copying therefore produces plausible metadata but visibly broken
    # limbs on the model's canonical rig. Evaluate the verified source rig and
    # deterministically bake each same-name pose into canonical armature space.
    deform_names={group.name for group in target_mesh.vertex_groups}
    if not deform_names or not deform_names<=target_names:
        raise ValueError("Character mesh weights do not map to the canonical skeleton")
    ordered=sorted((bone for bone in target_armature.pose.bones if bone.name in deform_names),key=lambda bone:len(bone.parent_recursive))
    full_order=sorted(target_armature.pose.bones,key=lambda bone:len(bone.parent_recursive))
    scene=bpy.context.scene; first,last=(int(round(value)) for value in source.frame_range)
    source_to_target=target_armature.matrix_world.inverted()@source_armature.matrix_world
    source_fps=scene.render.fps/scene.render.fps_base
    source_rest={bone.name:(source_to_target@bone.matrix_local).copy() for bone in source_armature.data.bones}
    target_rest={bone.name:bone.bone.matrix_local.copy() for bone in full_order}
    # Capture the complete source before touching the target. Blender pose
    # matrices are mutable dependency-graph values, so every matrix is copied.
    captured={}
    frames=list(range(first,last+1))
    capture_frames=list(reversed(frames)) if capture_order=="reverse" else frames
    for frame in capture_frames:
        if capture_order=="isolated":
            scene.frame_set(first); bpy.context.view_layer.update()
        scene.frame_set(frame); bpy.context.view_layer.update()
        captured[frame]={name:(source_to_target@source_armature.pose.bones[name].matrix).copy() for name in source_names}

    action=bpy.data.actions.new("character_action_"+clip_name)
    assign_character_action(target_armature,action)
    solved_frames={}; floor_z={}
    for frame in frames:
        target_armature.location=(0,0,0)
        source_poses=captured[frame]
        desired={}
        for bone in ordered:
            source_pose=source_poses[bone.name]
            rotation=source_pose.to_quaternion().normalized().to_matrix().to_4x4()
            if bone.parent and bone.parent.name in desired:
                parent_rest=target_rest[bone.parent.name]
                local_rest=parent_rest.inverted()@target_rest[bone.name]
                location=desired[bone.parent.name]@local_rest.translation
            else:
                location=bone.bone.head_local+(source_pose.translation-source_rest[bone.name].translation)
            desired[bone.name]=Matrix.Translation(location)@rotation

        # Solve every bone against its parent pose from this frame. Assigning
        # bone.matrix across the hierarchy and updating only at the end makes
        # Blender derive child bases from stale parent poses.
        actual={}; rotations={}
        for bone in full_order:
            parent_args={"parent_matrix":actual[bone.parent.name],
                         "parent_matrix_local":target_rest[bone.parent.name]} if bone.parent else {}
            if bone.name in desired:
                raw_basis=bone.bone.convert_local_to_pose(
                    desired[bone.name],target_rest[bone.name],invert=True,**parent_args)
                rotation=raw_basis.to_quaternion().normalized()
                basis=rotation.to_matrix().to_4x4()
                rotations[bone.name]=rotation
            else:
                basis=Matrix.Identity(4)
            bone.rotation_mode="QUATERNION"; bone.matrix_basis=basis
            actual[bone.name]=bone.bone.convert_local_to_pose(
                basis,target_rest[bone.name],**parent_args)
        bpy.context.view_layer.update()
        low,_=evaluated_bounds([target_mesh]); floor_z[frame]=low[2]
        solved_frames[frame]=rotations

    # Equivalent quaternions q and -q represent the same orientation. Keep a
    # consistent sign so interpolation cannot take the long path between keys.
    for bone in ordered:
        previous=None
        for frame in frames:
            rotation=solved_frames[frame][bone.name]
            if previous is not None and rotation.dot(previous)<0: rotation.negate()
            previous=rotation.copy()

    # Use one placement offset for the whole clip. This avoids per-frame floor
    # snapping for these admitted rotation-only fixtures. Source bone and root
    # translations remain outside this bounded transfer contract.
    root_z=-min(floor_z.values())
    for frame in frames:
        scene.frame_set(frame)
        for bone in full_order:
            bone.rotation_mode="QUATERNION"; bone.location=(0,0,0); bone.scale=(1,1,1)
            bone.rotation_quaternion=solved_frames[frame][bone.name] if bone.name in deform_names else (1,0,0,0)
        target_armature.location=(0,0,root_z)
        bpy.context.view_layer.update()
        for bone in ordered:
            bone.keyframe_insert(data_path="rotation_quaternion",frame=frame,group=bone.name)
        target_armature.keyframe_insert(data_path="location",frame=frame,group="grounding")
    for curve in action_channels(action):
        for key in curve.keyframe_points: key.interpolation="LINEAR"
    action["mf_id"]=action.name; action["mf_clip_name"]=clip_name; action["mf_source_sha256"]=spec["sha256"]
    action["mf_source_fps"]=source_fps; action["mf_source_frame_start"]=first; action["mf_source_frame_end"]=last
    action["mf_transfer_method"]="explicit_parent_pose_rotation_bake_v2"
    action["mf_capture_order"]=capture_order
    action["mf_clip_semantics"]="loop" if clip_name in {"idle","run"} else "source_pose_reference"
    action["mf_root_motion_policy"]="static_clip_floor_offset_preserve_vertical_v1"; action.use_fake_user=True
    target_armature.animation_data.action=None
    for obj in objects: bpy.data.objects.remove(obj,do_unlink=True)
    for imported in actions:
        bpy.data.actions.remove(imported)
    return action


def author_character_jump(armature,mesh,idle,jump,world_height_m,character_scale):
    """Create the fixed 3D-03.1 jump from admitted idle and jump poses."""
    if world_height_m!=.34 or len(character_scale)!=3 or max(character_scale)-min(character_scale)>1e-12:
        raise ValueError("Authored jump parameters do not match the frozen 3D-03.1 contract")
    weighted={group.name for group in mesh.vertex_groups}
    def rotations(action,frame):
        values={name:[None]*4 for name in weighted}
        for curve in action_channels(action):
            if not curve.data_path.startswith('pose.bones['): continue
            name=curve.data_path.split('"')[1]
            if name in values and curve.array_index<4: values[name][curve.array_index]=curve.evaluate(frame)
        if any(any(value is None for value in quaternion) for quaternion in values.values()):
            raise ValueError("Authored jump reference action lacks quaternion channels")
        return {name:Quaternion(values[name]) for name in values}
    idle_values=rotations(idle,1); jump_values={frame:rotations(jump,frame) for frame in range(1,14)}
    weights=(0,.35,.75,1,.85,.65,.55,.65,.85,1,.75,.35,0)
    heights=(0,0,.03,.10,.20,.29,.34,.29,.20,.10,.03,0,0)
    pose_values={}; root_values={}
    assign_character_action(armature,jump)
    for frame,(weight,height) in enumerate(zip(weights,heights),1):
        scene=bpy.context.scene; scene.frame_set(frame)
        frame_values={}
        for bone in armature.pose.bones:
            bone.location=(0,0,0); bone.scale=(1,1,1); bone.rotation_mode="QUATERNION"
            if bone.name in weighted:
                start=idle_values[bone.name].copy(); reference=jump_values[frame][bone.name].copy()
                if start.dot(reference)<0: reference.negate()
                value=start.slerp(reference,weight).normalized()
                bone.rotation_quaternion=value; frame_values[bone.name]=value.copy()
            else:
                bone.rotation_quaternion=(1,0,0,0)
        armature.location=(0,0,0); bpy.context.view_layer.update()
        low,_=evaluated_bounds([mesh])
        armature.location.z=(-low[2]+height)/character_scale[2]
        bpy.context.view_layer.update(); pose_values[frame]=frame_values; root_values[frame]=armature.location.copy()
    for curve in action_channels(jump):
        if curve.data_path=="location": samples={frame:root[curve.array_index] for frame,root in root_values.items()}
        else:
            name=curve.data_path.split('"')[1]
            samples={frame:value[name][curve.array_index] for frame,value in pose_values.items()}
        for key in curve.keyframe_points:
            frame=int(round(key.co[0])); key.co[1]=samples[frame]
            key.handle_left[1]=key.co[1]; key.handle_right[1]=key.co[1]; key.interpolation="LINEAR"
        curve.update()
    jump["mf_clip_semantics"]="authored_full_jump"
    jump["mf_authored_motion_policy"]="idle_to_admitted_pose_takeoff_airborne_landing_v1"
    jump["mf_authored_peak_height_m"]=world_height_m
    jump["mf_source_role"]="pose_reference_only"
    jump["mf_root_motion_policy"]="authored_pose_grounding_plus_vertical_arc_v1"


def assign_character_action(armature,action):
    armature.animation_data_create(); armature.animation_data.action=action
    slots=list(getattr(action,"slots",[]))
    if slots:
        compatible=[slot for slot in slots if getattr(slot,"target_id_type",None)=="OBJECT"]
        if len(compatible)!=1: raise ValueError("Character action requires one compatible object slot")
        armature.animation_data.action_slot=compatible[0]
    return armature.animation_data


def evaluated_bounds(objects):
    bpy.context.view_layer.update(); deps=bpy.context.evaluated_depsgraph_get(); points=[]
    for obj in objects:
        if obj.type!="MESH": continue
        evaluated=obj.evaluated_get(deps)
        points.extend(evaluated.matrix_world@Vector(corner) for corner in evaluated.bound_box)
    if not points: raise ValueError("Character has no evaluated mesh bounds")
    return ([min(point[i] for point in points) for i in range(3)],[max(point[i] for point in points) for i in range(3)])


CHARACTER_MOTION_ACTIONS={
    "idle":("character_action_idle",1,33),
    "run":("character_action_run",1,17),
    "jump":("character_action_jump",1,13),
}
CHARACTER_MOTION_LIMBS=("LeftUpLeg","LeftLeg","LeftFoot","RightUpLeg","RightLeg","RightFoot",
                        "LeftArm","LeftForeArm","RightArm","RightForeArm")

PERFORMANCE_OPERATION={
    "op":"adjust_run_body_dynamics","entity_id":"character_01","frame_start":40,"frame_end":70,
    "blend_width_frames":6,"blend_envelope":"quintic_smootherstep_zero_value_and_slope_v1",
    "body_target":"Hips","vertical_body_amplitude_m":.035,"vertical_axis":"armature_local_z",
    "forward_torso_lean_degrees":6.0,"torso_target":"Chest","support_contact_clearance_m":.045,
    "support_compensation":"preserve_baseline_in_place_contact_trajectory_two_bone_ik_v1"}


def _set_scene_time(scene,frame):
    whole=math.floor(frame); scene.frame_set(whole,subframe=frame-whole); bpy.context.view_layer.update()


def _smootherstep(value):
    x=max(0.0,min(1.0,value)); return 6*x**5-15*x**4+10*x**3


def _performance_envelope(frame,operation):
    start=operation["frame_start"]; end=operation["frame_end"]; width=operation["blend_width_frames"]
    if frame<=start or frame>=end: return 0.0
    if frame<start+width: return _smootherstep((frame-start)/width)
    if frame>end-width: return _smootherstep((end-frame)/width)
    return 1.0


def _performance_phase(frame): return 1+(frame-1)%16


def _action_fingerprint(action):
    payload={"name":action.name,"properties":{key:action[key] for key in sorted(action.keys())},"curves":[]}
    for curve in sorted(action_channels(action),key=lambda item:(item.data_path,item.array_index)):
        payload["curves"].append({"data_path":curve.data_path,"array_index":curve.array_index,
            "keys":[[float(key.co[0]),float(key.co[1]),key.interpolation] for key in curve.keyframe_points]})
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


def _pose_at(armature,action,frame):
    assign_character_action(armature,action); _set_scene_time(bpy.context.scene,frame)
    return {bone.name:bone.matrix.copy() for bone in armature.pose.bones}


def _make_repeating_run_action(armature,source):
    captured={}
    for frame in range(1,97):
        _pose_at(armature,source,_performance_phase(frame))
        captured[frame]={"basis":{bone.name:bone.matrix_basis.decompose() for bone in armature.pose.bones},
                         "armature_location":armature.location.copy()}
    action=bpy.data.actions.new("character_action_run_3d04_baseline_96")
    assign_character_action(armature,action)
    for frame in range(1,97):
        values=captured[frame]
        armature.location=values["armature_location"]
        armature.keyframe_insert(data_path="location",frame=frame,group="grounding")
        for bone in armature.pose.bones:
            location,rotation,scale=values["basis"][bone.name]
            bone.rotation_mode="QUATERNION"; bone.location=location; bone.scale=scale
            bone.rotation_quaternion=rotation.normalized()
            bone.keyframe_insert(data_path="location",frame=frame,group=bone.name)
            bone.keyframe_insert(data_path="rotation_quaternion",frame=frame,group=bone.name)
            bone.keyframe_insert(data_path="scale",frame=frame,group=bone.name)
    for curve in action_channels(action):
        for key in curve.keyframe_points: key.interpolation="LINEAR"
    action["mf_id"]=action.name; action["mf_clip_name"]="run"; action["mf_source_action"]="character_action_run"
    action["mf_source_unique_frames"]=16; action["mf_timeline_fps"]=24.0; action["mf_frame_start"]=1; action["mf_frame_end"]=96
    action["mf_timeline_policy"]="repeat_16_unique_samples_without_endpoint_hold_v1"; action.use_fake_user=True
    return action


def _bone_tail(matrix,bone): return matrix@Vector((0,bone.bone.length,0))


def _orient_bone(matrix,bone,new_head,new_tail):
    old_head=matrix.translation; old_tail=_bone_tail(matrix,bone)
    old_direction=old_tail-old_head; new_direction=new_tail-new_head
    if old_direction.length<=1e-12 or new_direction.length<=1e-12: raise ValueError("Cannot orient zero-length performance bone")
    rotation=old_direction.rotation_difference(new_direction)
    return Matrix.Translation(new_head)@rotation.to_matrix().to_4x4()@Matrix.Translation(-old_head)@matrix


def _solve_leg(desired,baseline,armature,side,target):
    upper=armature.pose.bones[side+"UpLeg"]; lower=armature.pose.bones[side+"Leg"]; foot=armature.pose.bones[side+"Foot"]
    a=desired[upper.name].translation; base_knee=baseline[lower.name].translation; base_ankle=baseline[foot.name].translation
    l1=upper.bone.length; l2=lower.bone.length; direction=target-a; distance=direction.length
    if distance<=1e-9 or distance>=l1+l2-1e-7: raise ValueError("Support target is outside the qualified two-bone solve")
    unit=direction.normalized(); x=(l1*l1-l2*l2+distance*distance)/(2*distance); height=math.sqrt(max(0.0,l1*l1-x*x))
    normal=(base_knee-baseline[upper.name].translation).cross(base_ankle-base_knee)
    if normal.length<=1e-9: normal=Vector((1,0,0))
    normal.normalize(); bend=normal.cross(unit)
    if bend.length<=1e-9: bend=Vector((0,1,0))
    bend.normalize(); projected=base_knee-(a+unit*x)
    if bend.dot(projected)<0: bend.negate()
    knee=a+unit*x+bend*height
    desired[upper.name]=_orient_bone(desired[upper.name],upper,a,knee)
    desired[lower.name]=_orient_bone(desired[lower.name],lower,knee,target)
    foot_shift=target-baseline[foot.name].translation
    for bone in armature.pose.bones:
        if bone==foot or foot in bone.parent_recursive:
            desired[bone.name]=Matrix.Translation(foot_shift)@baseline[bone.name]


def build_performance(operations):
    if operations!=[PERFORMANCE_OPERATION]: raise ValueError("3D-04 accepts only the frozen timeline-local revision")
    scene=bpy.context.scene; armature=bpy.data.objects.get("character_01_armature"); mesh=bpy.data.objects.get("character_01_mesh")
    source=bpy.data.actions.get("character_action_run")
    if not armature or not mesh or not source: raise ValueError("3D-04 baseline character or source action is missing")
    if scene.render.fps!=24 or scene.render.fps_base!=1: raise ValueError("3D-04 requires the frozen 24 fps scene")
    source_before=_action_fingerprint(source); baseline=_make_repeating_run_action(armature,source)
    candidate=baseline.copy(); candidate.name="character_action_run_3d04_candidate_96"; candidate["mf_id"]=candidate.name
    candidate["mf_parent_action"]=baseline.name; candidate["mf_revision"]="adjust_run_body_dynamics_v1"
    candidate["mf_edit_interval"]="[40,70]"; candidate["mf_blend_envelope"]=PERFORMANCE_OPERATION["blend_envelope"]
    candidate.use_fake_user=True
    foot_vertices=_character_foot_vertices(mesh); internal=[40+i*.125 for i in range(241)]
    scale_z=(armature.matrix_world.to_3x3()@Vector((0,0,1))).length
    if scale_z<=0: raise ValueError("Character has invalid armature world scale")
    baseline_states={}
    for frame in internal:
        matrices=_pose_at(armature,baseline,frame); points=_evaluated_character_points(mesh)
        feet={side:min(points[index].z for index in indices) for side,indices in foot_vertices.items()}
        baseline_states[frame]={"matrices":matrices,"feet":feet}
    rest={bone.name:bone.bone.matrix_local.copy() for bone in armature.pose.bones}
    full_order=sorted(armature.pose.bones,key=lambda bone:len(bone.parent_recursive)); hips=armature.pose.bones["Hips"]
    edited=("Hips","Chest","LeftUpLeg","LeftLeg","LeftFoot","RightUpLeg","RightLeg","RightFoot")
    previous={name:None for name in edited}
    assign_character_action(armature,candidate)
    for frame in internal:
        state=baseline_states[frame]; base=state["matrices"]; envelope=_performance_envelope(frame,PERFORMANCE_OPERATION)
        phase=_performance_phase(frame); rhythm=.5+.5*math.cos(2*math.pi*(phase-1)/8)
        # Compress during planted support rather than lengthening an already
        # straight leg. Returning to baseline height at flight strengthens the
        # run's vertical contrast without moving the armature or character root.
        delta=-PERFORMANCE_OPERATION["vertical_body_amplitude_m"]*envelope*rhythm/scale_z
        translation=Matrix.Translation((0,0,delta)); desired={name:matrix.copy() for name,matrix in base.items()}
        for bone in armature.pose.bones:
            if bone==hips or hips in bone.parent_recursive: desired[bone.name]=translation@base[bone.name]
        for side in ("Left","Right"):
            if state["feet"][side.lower()]<=PERFORMANCE_OPERATION["support_contact_clearance_m"] and envelope>0:
                _solve_leg(desired,base,armature,side,base[side+"Foot"].translation.copy())
        chest=armature.pose.bones["Chest"]; chest_head=desired["Chest"].translation
        lean=math.radians(PERFORMANCE_OPERATION["forward_torso_lean_degrees"])*envelope
        chest_transform=Matrix.Translation(chest_head)@Quaternion((1,0,0),lean).to_matrix().to_4x4()@Matrix.Translation(-chest_head)
        for bone in armature.pose.bones:
            if bone==chest or chest in bone.parent_recursive: desired[bone.name]=chest_transform@desired[bone.name]
        actual={}; bases={}
        for bone in full_order:
            parent_args={"parent_matrix":actual[bone.parent.name],"parent_matrix_local":rest[bone.parent.name]} if bone.parent else {}
            basis=bone.bone.convert_local_to_pose(desired[bone.name],rest[bone.name],invert=True,**parent_args)
            location,rotation,_=basis.decompose(); rotation.normalize()
            if bone.name in previous and previous[bone.name] is not None and rotation.dot(previous[bone.name])<0: rotation.negate()
            if bone.name in previous: previous[bone.name]=rotation.copy()
            bases[bone.name]=(location,rotation)
            actual[bone.name]=bone.bone.convert_local_to_pose(Matrix.LocRotScale(location,rotation,Vector((1,1,1))),rest[bone.name],**parent_args)
        if envelope==0: continue
        for name in edited:
            bone=armature.pose.bones[name]; location,rotation=bases[name]
            bone.rotation_mode="QUATERNION"; bone.location=location; bone.rotation_quaternion=rotation
            bone.keyframe_insert(data_path="rotation_quaternion",frame=frame,group=name)
            if name=="Hips": bone.keyframe_insert(data_path="location",frame=frame,group=name)
    for curve in action_channels(candidate):
        for key in curve.keyframe_points: key.interpolation="LINEAR"
    if _action_fingerprint(source)!=source_before: raise ValueError("3D-04 mutated the immutable source action")
    assign_character_action(armature,candidate); armature["mf_active_action"]="run_3d04_candidate"
    scene.frame_start=1; scene.frame_end=96; scene.frame_set(1); scene.camera=bpy.data.objects["camera_B"]
    scene["mf_experiment_id"]="3D-04"; scene["mf_timeline_revision"]="adjust_run_body_dynamics_v1"
    scene["mf_source_action_sha256"]=source_before
    bpy.context.view_layer.update()
    return [{"op":"create_repeating_baseline_action","action":baseline.name,"source":source.name},
            {"op":"adjust_run_body_dynamics","action":candidate.name,"frame_start":40,"frame_end":70,
             "source_action_sha256":source_before}]


def _performance_sample(armature,mesh,action,frame,foot_vertices,rest_lengths):
    assign_character_action(armature,action); _set_scene_time(bpy.context.scene,frame)
    points=_evaluated_character_points(mesh); low=min(point.z for point in points)
    feet={side:min(points[index].z for index in indices) for side,indices in foot_vertices.items()}
    ankles={side:list(armature.matrix_world@armature.pose.bones[side.title()+"Foot"].head) for side in ("left","right")}
    ratios=[]
    for name,rest in rest_lengths.items():
        pose=armature.pose.bones[name]; length=(armature.matrix_world@pose.tail-armature.matrix_world@pose.head).length
        ratios.append(abs(length/rest-1))
    return {"points":points,"candidate_min_z_m":low,"feet":feet,"ankles":ankles,
            "maximum_limb_length_relative_error":max(ratios),
            "hips":armature.pose.bones["Hips"].matrix.copy(),"chest":armature.pose.bones["Chest"].matrix.copy()}


def _point_delta(left,right):
    distances=[(a-b).length for a,b in zip(left,right)]
    return max(distances),math.sqrt(sum(value*value for value in distances)/len(distances))


def performance_evidence(out,profile,seed,campaign,render_frames=False):
    baseline_spec=campaign.get("baseline",{}); sampling=campaign.get("sampling",{})
    expected_baseline={"action":"character_action_run","action_unique_frames":16,"source_fps":24,"timeline_fps":24,
                       "timeline_frame_start":1,"timeline_frame_end":96}
    if any(baseline_spec.get(key)!=value for key,value in expected_baseline.items()):
        raise ValueError("3D-04 evidence timeline does not match the frozen contract")
    if sampling.get("regular_step_frames")!=.5 or sampling.get("boundary_step_frames")!=.125 or sampling.get("boundary_windows")!=[[38,42],[68,72]]:
        raise ValueError("3D-04 evidence sampling does not match the frozen contract")
    scene=bpy.context.scene; armature=bpy.data.objects.get("character_01_armature"); mesh=bpy.data.objects.get("character_01_mesh")
    baseline=bpy.data.actions.get("character_action_run_3d04_baseline_96"); candidate=bpy.data.actions.get("character_action_run_3d04_candidate_96")
    source=bpy.data.actions.get("character_action_run")
    if not armature or not mesh or not baseline or not candidate or not source or scene.get("mf_experiment_id")!="3D-04":
        raise ValueError("3D-04 evidence targets are missing")
    times={1+i*.5 for i in range(191)}
    for low,high in sampling["boundary_windows"]: times.update(low+i*.125 for i in range(int((high-low)/.125)+1))
    times=sorted(times); foot_vertices=_character_foot_vertices(mesh)
    rest_lengths={name:(armature.matrix_world.to_3x3()@(armature.data.bones[name].tail_local-armature.data.bones[name].head_local)).length
                  for name in CHARACTER_MOTION_LIMBS}
    baseline_states={frame:_performance_sample(armature,mesh,baseline,frame,foot_vertices,rest_lengths) for frame in times}
    candidate_states={frame:_performance_sample(armature,mesh,candidate,frame,foot_vertices,rest_lengths) for frame in times}
    rows=[]; previous_frame=None; previous_points=None
    for frame in times:
        before=baseline_states[frame]; after=candidate_states[frame]; maximum,rms=_point_delta(before["points"],after["points"])
        if previous_points is None: step_max=step_rms=0.0
        else:
            step_max,step_rms=_point_delta(after["points"],previous_points); scale=1/(frame-previous_frame)
            step_max*=scale; step_rms*=scale
        rows.append({"frame":frame,"max_vertex_delta_m":maximum,"rms_vertex_delta_m":rms,
                     "candidate_min_z_m":after["candidate_min_z_m"],
                     "maximum_limb_length_relative_error":after["maximum_limb_length_relative_error"],
                     "candidate_step_max_vertex_m":step_max,"candidate_step_rms_vertex_m":step_rms})
        previous_frame=frame; previous_points=[point.copy() for point in after["points"]]
    h=sampling["velocity_half_width_frames"]; fps=baseline_spec["timeline_fps"]; boundaries={}
    for boundary in (40,70):
        center_max,center_rms=_point_delta(baseline_states[boundary]["points"],candidate_states[boundary]["points"])
        velocities=[]
        for b0,b1,c0,c1 in zip(baseline_states[boundary-h]["points"],baseline_states[boundary+h]["points"],
                               candidate_states[boundary-h]["points"],candidate_states[boundary+h]["points"]):
            velocities.append(((c1-c0)-(b1-b0))*(fps/(2*h)))
        magnitudes=[value.length for value in velocities]
        boundaries[str(boundary)]={"max_vertex_delta_m":center_max,"rms_vertex_delta_m":center_rms,
            "max_velocity_delta_m_per_s":max(magnitudes),
            "rms_velocity_delta_m_per_s":math.sqrt(sum(value*value for value in magnitudes)/len(magnitudes))}
    segments=[]
    for side in ("left","right"):
        run=[]; runs=[]
        for frame in times:
            if baseline_states[frame]["feet"][side]<=campaign["thresholds"]["support_contact_clearance_m"]: run.append(frame)
            elif run: runs.append(run); run=[]
        if run: runs.append(run)
        for run in runs:
            anchor_frame=min(run,key=lambda value:baseline_states[value]["feet"][side])
            baseline_anchor=Vector(baseline_states[anchor_frame]["ankles"][side]); candidate_anchor=Vector(candidate_states[anchor_frame]["ankles"][side])
            baseline_slide=max((Vector(baseline_states[frame]["ankles"][side])-baseline_anchor).xy.length for frame in run)
            candidate_slide=max((Vector(candidate_states[frame]["ankles"][side])-candidate_anchor).xy.length for frame in run)
            induced_slide=max((Vector(candidate_states[frame]["ankles"][side])-Vector(baseline_states[frame]["ankles"][side])).xy.length for frame in run)
            retained=all(candidate_states[frame]["feet"][side]<=campaign["thresholds"]["candidate_contact_clearance_m"] for frame in run)
            segments.append({"foot":side,"frame_start":run[0],"frame_end":run[-1],"baseline_slide_m":baseline_slide,
                             "candidate_slide_m":candidate_slide,"candidate_induced_slide_m":induced_slide,
                             "candidate_contact_retained":retained})
    achieved={"peak_absolute_pelvis_correction_m":0.0,"peak_chest_lean_degrees":0.0}
    for frame in times:
        if 40<=frame<=70:
            before=baseline_states[frame]; after=candidate_states[frame]
            hips_delta=(after["hips"].translation-before["hips"].translation).length*(armature.matrix_world.to_3x3()@Vector((0,0,1))).length
            chest_delta=math.degrees(before["chest"].to_quaternion().rotation_difference(after["chest"].to_quaternion()).angle)
            achieved["peak_absolute_pelvis_correction_m"]=max(achieved["peak_absolute_pelvis_correction_m"],hips_delta)
            achieved["peak_chest_lean_degrees"]=max(achieved["peak_chest_lean_degrees"],chest_delta)
    if render_frames:
        apply_profile(profile,seed); scene.camera=bpy.data.objects["camera_B"]
        for role,action in (("baseline",baseline),("candidate",candidate)):
            assign_character_action(armature,action); folder=out/"frames"/role; folder.mkdir(parents=True,exist_ok=True)
            for frame in range(1,97):
                scene.frame_set(frame); bpy.context.view_layer.update(); scene.render.filepath=str(folder/f"frame-{frame:04d}.png")
                bpy.ops.render.render(write_still=True)
    source_actual=_action_fingerprint(source); source_expected=scene.get("mf_source_action_sha256")
    source_equal=source_actual==source_expected
    payload={"schema_version":"1.0","experiment_id":"3D-04","baseline_native_sha256":baseline_spec["sha256"],
             "performance_native_sha256":file_sha256(Path(bpy.data.filepath)),
             "timeline":{"fps":24,"frame_start":1,"frame_end":96,"unique_source_frames":16},
             "protected":{"source_action_equal":source_equal,"source_action_expected_sha256":source_expected,
                          "source_action_actual_sha256":source_actual},"samples":rows,"boundaries":boundaries,
             "support_segments":segments,"achieved":achieved,"persistence":{},
             "rendered_frames_per_clip":96 if render_frames else 0,"provider_calls":0}
    write_json(out/"performance-metrics.json",payload); return payload


def _evaluated_character_points(mesh):
    depsgraph=bpy.context.evaluated_depsgraph_get(); evaluated=mesh.evaluated_get(depsgraph)
    temporary=evaluated.to_mesh()
    try:
        if len(temporary.vertices)!=len(mesh.data.vertices):
            raise ValueError("Temporal validation requires stable evaluated topology")
        return [evaluated.matrix_world@vertex.co for vertex in temporary.vertices]
    finally:
        evaluated.to_mesh_clear()


def _character_foot_vertices(mesh):
    result={}
    for side,names in {"left":("LeftFoot","LeftToes"),"right":("RightFoot","RightToes")}.items():
        group_ids={mesh.vertex_groups[name].index for name in names if mesh.vertex_groups.get(name)}
        indices=[vertex.index for vertex in mesh.data.vertices
                 if sum(link.weight for link in vertex.groups if link.group in group_ids)>=.25]
        if not indices:
            raise ValueError("Character foot has no sufficiently weighted vertices: "+side)
        result[side]=indices
    return result


def character_temporal_evidence(out,profile,seed,request):
    """Measure and render every frame without saving changes to the source scene."""
    expected={name:{"action":action,"frame_start":first,"frame_end":last}
              for name,(action,first,last) in CHARACTER_MOTION_ACTIONS.items()}
    if not isinstance(request,dict) or set(request)!={"schema_version","clips","camera_id"}:
        raise ValueError("Invalid temporal evidence request")
    if request["schema_version"]!="1.0" or request["clips"]!=expected or request["camera_id"]!="camera_B":
        raise ValueError("Temporal evidence request does not match the frozen contract")
    armature=bpy.data.objects.get("character_01_armature"); mesh=bpy.data.objects.get("character_01_mesh")
    camera=bpy.data.objects.get(request["camera_id"])
    if not armature or armature.type!="ARMATURE" or not mesh or mesh.type!="MESH" or not camera or camera.type!="CAMERA":
        raise ValueError("Frozen temporal evidence targets are missing")
    actions={name:bpy.data.actions.get(spec["action"]) for name,spec in request["clips"].items()}
    if any(action is None for action in actions.values()):
        raise ValueError("Frozen temporal evidence action is missing")
    foot_vertices=_character_foot_vertices(mesh)
    rest_lengths={}
    for name in CHARACTER_MOTION_LIMBS:
        bone=armature.data.bones.get(name)
        if bone is None: raise ValueError("Frozen limb bone is missing: "+name)
        rest_lengths[name]=(armature.matrix_world.to_3x3()@(bone.tail_local-bone.head_local)).length
        if rest_lengths[name]<=0: raise ValueError("Frozen limb has invalid rest length: "+name)
    apply_profile(profile,seed); scene=bpy.context.scene; scene.camera=camera
    original_frame=scene.frame_current
    original_action=armature.animation_data.action if armature.animation_data else None
    clips={}
    try:
        for clip,spec in request["clips"].items():
            assign_character_action(armature,actions[clip])
            source_fps=float(actions[clip].get("mf_source_fps",scene.render.fps/scene.render.fps_base))
            if not math.isfinite(source_fps) or source_fps<=0: raise ValueError("Frozen clip source FPS is invalid")
            folder=out/"frames"/clip; folder.mkdir(parents=True,exist_ok=True)
            frames=[]; previous=None; first_points=None
            for frame in range(spec["frame_start"],spec["frame_end"]+1):
                scene.frame_set(frame); bpy.context.view_layer.update()
                points=_evaluated_character_points(mesh)
                finite=all(math.isfinite(value) for point in points for value in point)
                if finite:
                    low=[min(point[axis] for point in points) for axis in range(3)]
                    high=[max(point[axis] for point in points) for axis in range(3)]
                    dimensions=[high[axis]-low[axis] for axis in range(3)]
                    centroid=[sum(point[axis] for point in points)/len(points) for axis in range(3)]
                    feet={side:min(points[index].z for index in indices) for side,indices in foot_vertices.items()}
                else:
                    low=high=dimensions=centroid=[None,None,None]; feet={"left":None,"right":None}
                limb_ratios={}
                for name,rest in rest_lengths.items():
                    pose=armature.pose.bones[name]
                    length=(armature.matrix_world@pose.tail-armature.matrix_world@pose.head).length
                    limb_ratios[name]=length/rest
                step=None
                if previous is not None and finite:
                    distances=[(point-prior).length for point,prior in zip(points,previous)]
                    delta_seconds=1/source_fps
                    step={"delta_seconds":delta_seconds,"max_vertex_m":max(distances),
                          "rms_vertex_m":math.sqrt(sum(value*value for value in distances)/len(distances))}
                    step["max_vertex_m_per_s"]=step["max_vertex_m"]/delta_seconds
                    step["rms_vertex_m_per_s"]=step["rms_vertex_m"]/delta_seconds
                if first_points is None: first_points=[point.copy() for point in points]
                frames.append({"frame":frame,"timestamp_seconds":(frame-spec["frame_start"])/source_fps,
                               "finite":finite,"bounds":{"min":low,"max":high,"dimensions":dimensions},
                               "centroid":centroid,"foot_min_z_m":feet,"limb_length_ratios":limb_ratios,
                               "step_from_previous":step})
                scene.render.filepath=str(folder/(f"frame-{frame:04d}.png"))
                bpy.ops.render.render(write_still=True)
                previous=[point.copy() for point in points]
            seam_distances=[(point-prior).length for point,prior in zip(previous,first_points)]
            clips[clip]={"action":spec["action"],"source_fps":source_fps,
                         "semantics":actions[clip].get("mf_clip_semantics","unspecified"),
                         "frame_start":spec["frame_start"],"frame_end":spec["frame_end"],
                         "frame_count":len(frames),"frames":frames,
                         "loop_seam":{"max_vertex_m":max(seam_distances),
                                      "rms_vertex_m":math.sqrt(sum(value*value for value in seam_distances)/len(seam_distances))}}
    finally:
        if original_action is not None: assign_character_action(armature,original_action)
        scene.frame_set(original_frame); bpy.context.view_layer.update()
    payload={"schema_version":"1.0","experiment_id":"3D-03-TEMPORAL","source_native_sha256":file_sha256(Path(bpy.data.filepath)),
             "camera_id":request["camera_id"],"vertex_count":len(mesh.data.vertices),
             "foot_vertex_counts":{key:len(value) for key,value in foot_vertices.items()},"clips":clips}
    write_json(out/"temporal-metrics.json",payload)
    return payload


def build_character(plan,profile):
    if plan.get("schema_version")!="1.0" or plan.get("experiment_id") not in {"3D-03","3D-03.1"}: raise ValueError("Unsupported character scene plan")
    if plan.get("entity",{}).get("id")!="character_01": raise ValueError("3D-03 requires character_01")
    if set(plan.get("clips",{}))!={"idle","run","jump"} or len(plan.get("cameras",[]))!=3 or len(plan.get("lights",[]))!=3:
        raise ValueError("3D-03 requires the frozen clips, camera rig, and light rig")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene; entity=plan["entity"]
    scene["mf_scene_id"]=plan["scene_id"]; scene["mf_seed"]=plan["seed"]; scene["mf_builder_version"]="character-v1"
    scene["mf_mask_palette_json"]=json.dumps(plan["mask_palette"],sort_keys=True); scene.unit_settings.system="METRIC"; scene.unit_settings.scale_length=1
    collection=bpy.data.collections.new("MovieFactoryCharacter"); collection["mf_id"]="collection_3d03_01"; scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    character=external_root(entity)
    imported,model_actions=import_animated_fbx(entity["source"])
    if model_actions: raise ValueError("Frozen character model unexpectedly contains animation")
    armatures=[obj for obj in imported if obj.type=="ARMATURE"]; meshes=[obj for obj in imported if obj.type=="MESH"]
    if len(armatures)!=1 or len(meshes)!=1: raise ValueError("Frozen character requires one armature and one mesh")
    armature,mesh=armatures[0],meshes[0]
    # Keep animation-controlled transforms below a separate normalization root.
    armature.parent=character; armature.matrix_parent_inverse=Matrix.Identity(4)
    identify_external(armature,"character_01_armature","character_01","character_armature",entity["source"]["sha256"])
    identify_external(mesh,"character_01_mesh","character_01","character_mesh",entity["source"]["sha256"])
    for bone in armature.data.bones:
        bone["mf_id"]="character_01_bone_"+bone.name
        bone["mf_source_name"]=bone.name
    for pose_bone in armature.pose.bones:
        for constraint in list(pose_bone.constraints): pose_bone.constraints.remove(constraint)
    armature["mf_animation_normalization"]="same_skeleton_pose_bake_v2"
    skin_material,skins=character_material("character_01",entity["skins"])
    mesh.data.materials.clear(); mesh.data.materials.append(skin_material)
    actions={name:import_character_action(spec,name,armature,mesh) for name,spec in plan["clips"].items()}
    assign_character_action(armature,actions["idle"]); scene.frame_set(1); bpy.context.view_layer.update()
    armature["mf_active_action"]="idle"; character["mf_active_skin"]="cyborg"
    scene.frame_start=1; scene.frame_end=33; scene.frame_set(1)
    low,high=evaluated_bounds([mesh]); height=high[2]-low[2]
    factor=entity["target_height_m"]/height
    character.scale=(factor,factor,factor); bpy.context.view_layer.update()
    if plan["experiment_id"]=="3D-03.1":
        if plan.get("jump_authoring")!={"method":"idle_to_admitted_pose_takeoff_airborne_landing_v1","peak_height_m":.34}:
            raise ValueError("3D-03.1 requires the frozen authored jump policy")
        author_character_jump(armature,mesh,actions["idle"],actions["jump"],.34,character.scale)
    elif "jump_authoring" in plan:
        raise ValueError("3D-03 faithful transfer does not accept authored jump motion")
    assign_character_action(armature,actions["idle"]); scene.frame_set(1); bpy.context.view_layer.update()
    scene.render.fps=24; scene.render.fps_base=1.0
    scene["mf_playback_fps"]=24
    for action in actions.values():
        action["mf_timeline_fps"]=24.0
        action["mf_nla_time_scale"]=24.0/action["mf_source_fps"]
    low,high=evaluated_bounds([mesh]); character.location=(-((low[0]+high[0])/2),-((low[1]+high[1])/2),-low[2]); bpy.context.view_layer.update()
    # Simple fixed studio stage; it is protected but not part of the imported character claim.
    stage=root({"id":"stage_01","kind":"stage","position":[0,0,0],"rotation_z":0})
    floor_mat=material("stage_floor_01","#6F7C86",.7); wall_mat=material("stage_wall_01","#39434D",.82)
    box(stage,"floor",(8,7,.08),(0,0,-.04),floor_mat,0)
    box(stage,"backdrop",(8,.08,4),(0,2.7,2),wall_mat,0)
    add_external_rig(plan,collection)
    for camera in plan["cameras"]: bpy.data.objects[camera["id"]]["mf_frame"]=camera["frame"]
    world=bpy.data.worlds.new("world_3d03_01"); world["mf_id"]="world_3d03_01"; world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=color(plan["world_color_hex"])
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=plan["world_strength"]; scene.world=world
    apply_profile(profile,plan["seed"]); scene.view_settings.exposure=plan["exposure"]; scene.camera=bpy.data.objects["camera_A"]
    bpy.ops.file.pack_all()
    for image in bpy.data.images:
        if image.packed_file: image.filepath="/__movie_factory_packed__/"+image.name
    bpy.context.view_layer.update()


def revise_character(operations):
    expected=[
        {"op":"set_character_skin","entity_id":"character_01","from":"cyborg","to":"skater"},
        {"op":"set_character_action","entity_id":"character_01","from":"idle","to":"run"},
    ]
    if operations!=expected: raise ValueError("3D-03 accepts only the frozen skin and action revision")
    character=bpy.data.objects.get("character_01"); armature=bpy.data.objects.get("character_01_armature")
    material=bpy.data.materials.get("character_01_skin_material"); action=bpy.data.actions.get("character_action_run")
    image=bpy.data.images.get("character_01_skin_skater")
    if not all((character,armature,material,action,image)): raise ValueError("Character revision target is missing")
    node=material.node_tree.nodes.get("Character Skin")
    if not node or material.get("mf_active_skin")!="cyborg" or armature.get("mf_active_action")!="idle": raise ValueError("Character baseline state is invalid")
    node.image=image; material["mf_active_skin"]="skater"; character["mf_active_skin"]="skater"
    assign_character_action(armature,action); armature["mf_active_action"]="run"
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    return [{"op":"set_character_skin","before":"cyborg","after":"skater"},{"op":"set_character_action","before":"idle","after":"run"}]


def pbr_motorcycle_material(entity_id, textures):
    if set(textures) != {"base_color", "normal", "orm"}:
        raise ValueError("Motorcycle repair requires the frozen BaseColor, Normal, and ORM maps")
    mat = bpy.data.materials.new(entity_id + "_pbr_01")
    mat["mf_id"] = entity_id + "_pbr_01"
    mat["mf_repair"] = "explicit_unreal_pbr_relink_v1"
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    output = tree.nodes.new("ShaderNodeOutputMaterial"); output.name = "Material Output"
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.name = "Principled BSDF"
    base = tree.nodes.new("ShaderNodeTexImage"); base.name = "Base Color"; base.image = verified_image(textures["base_color"])
    normal_tex = tree.nodes.new("ShaderNodeTexImage"); normal_tex.name = "Normal Texture"; normal_tex.image = verified_image(textures["normal"]); normal_tex.image.colorspace_settings.name = "Non-Color"
    normal = tree.nodes.new("ShaderNodeNormalMap"); normal.name = "Normal Map"
    orm = tree.nodes.new("ShaderNodeTexImage"); orm.name = "ORM Texture"; orm.image = verified_image(textures["orm"]); orm.image.colorspace_settings.name = "Non-Color"
    separate = tree.nodes.new("ShaderNodeSeparateColor"); separate.name = "ORM Channels"; separate.mode = "RGB"
    tree.links.new(base.outputs["Color"], bsdf.inputs["Base Color"])
    tree.links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    tree.links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
    tree.links.new(orm.outputs["Color"], separate.inputs["Color"])
    tree.links.new(separate.outputs["Green"], bsdf.inputs["Roughness"])
    tree.links.new(separate.outputs["Blue"], bsdf.inputs["Metallic"])
    tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat


def external_root(entity):
    obj = bpy.data.objects.new(entity["id"], None)
    bpy.context.collection.objects.link(obj)
    identify_external(obj, entity["id"], entity["id"], entity["kind"], entity["source_sha256"])
    obj["mf_is_entity"] = True
    obj.location = entity["position"]
    obj.rotation_euler[2] = math.radians(entity.get("rotation_z_degrees", 0))
    return obj


def asset_world_bounds(objects):
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ Vector(corner) for obj in objects if obj.type == "MESH" for corner in obj.bound_box]
    if not points:
        raise ValueError("Imported component has no mesh bounds")
    return ([min(point[i] for point in points) for i in range(3)],
            [max(point[i] for point in points) for i in range(3)])


def attach_import(root_obj, component_id, kind, source, *, target_longest=None, material_override=None):
    imported = import_source_asset(source)
    top_level = [obj for obj in imported if obj.parent not in imported]
    low, high = asset_world_bounds(imported)
    dimensions = [high[i] - low[i] for i in range(3)]
    factor = float(target_longest) / max(dimensions) if target_longest else 1.0
    normalize = Matrix.Translation((-factor*(low[0]+high[0])/2, -factor*(low[1]+high[1])/2, -factor*low[2])) @ Matrix.Scale(factor, 4)
    for obj in top_level:
        obj.matrix_world = normalize @ obj.matrix_world
        obj.parent = root_obj
        obj.matrix_parent_inverse = Matrix.Identity(4)
    ordered = sorted(imported, key=lambda obj: (obj.name, obj.type))
    for index, obj in enumerate(ordered):
        oid = f"{root_obj['mf_id']}_{component_id}_{index:02d}"
        identify_external(obj, oid, root_obj["mf_id"], kind, source["sha256"])
        if obj.type == "MESH":
            if material_override:
                obj.data.materials.clear(); obj.data.materials.append(material_override)
            else:
                for slot, mat in enumerate(list(obj.data.materials)):
                    if mat:
                        private = mat.copy()
                        private.name = f"{oid}_material_{slot:02d}"
                        private["mf_id"] = private.name
                        private["mf_source_sha256"] = source["sha256"]
                        obj.data.materials[slot] = private
    return imported


def duplicate_component(template_objects, base_matrices, root_obj, component_id, kind, source_sha256, transform):
    mapping = {}
    for index, original in enumerate(sorted(template_objects, key=lambda obj: obj["mf_id"])):
        copy = original.copy()
        if original.data:
            copy.data = original.data.copy()
        bpy.context.collection.objects.link(copy)
        identify_external(copy, f"{root_obj['mf_id']}_{component_id}_{index:02d}", root_obj["mf_id"], kind, source_sha256)
        mapping[original] = copy
    for original, copy in mapping.items():
        copy.parent = mapping.get(original.parent, root_obj)
        copy.matrix_parent_inverse = Matrix.Identity(4)
        copy.matrix_local = base_matrices[original].copy()
    first = mapping[sorted(template_objects, key=lambda obj: obj["mf_id"])[0]]
    first.matrix_local = transform @ base_matrices[sorted(template_objects, key=lambda obj: obj["mf_id"])[0]]
    return list(mapping.values())


def add_external_rig(plan, collection):
    for camera in plan["cameras"]:
        data = bpy.data.cameras.new(camera["id"] + "_data")
        obj = bpy.data.objects.new(camera["id"], data); collection.objects.link(obj)
        identify_external(obj, camera["id"], None, "camera", "rig-v1")
        obj["mf_shot_id"] = camera["shot_id"]; obj.location = camera["position"]; aim(obj, camera["target"])
        data.lens = camera["lens_mm"]; data.sensor_width = 36; data.clip_start = .01; data.clip_end = 100; data.dof.use_dof = False
    for light in plan["lights"]:
        if light["type"] != "AREA": raise ValueError("3D-02 uses AREA lights only")
        data = bpy.data.lights.new(light["id"] + "_data", "AREA")
        obj = bpy.data.objects.new(light["id"], data); collection.objects.link(obj)
        identify_external(obj, light["id"], None, "light", "rig-v1")
        obj.location = light["position"]; aim(obj, light["target"])
        data.energy = light["energy_w"]; data.color = color(light["color_hex"])[:3]; data.shape = "DISK"; data.size = light["size_m"]


def build_external(plan, profile):
    if plan.get("schema_version") != "1.0" or plan.get("experiment_id") != "3D-02":
        raise ValueError("Unsupported external scene plan")
    if [entity.get("id") for entity in plan.get("entities", [])] != ["courtyard_01", "motorcycle_01", "sword_01"]:
        raise ValueError("3D-02 requires exactly the frozen entity set and order")
    if len(plan.get("cameras", [])) != 3 or {item.get("id") for item in plan["cameras"]} != {"camera_A","camera_B","camera_C"}:
        raise ValueError("3D-02 requires the frozen three-camera rig")
    if len(plan.get("lights", [])) != 3 or {item.get("id") for item in plan["lights"]} != {"key_light_01","fill_light_01","rim_light_01"}:
        raise ValueError("3D-02 requires the frozen three-light rig")
    components = plan["entities"][0].get("components", [])
    if not 1 <= len(components) <= 8 or sum(len(item.get("instances", [])) for item in components) > 40:
        raise ValueError("3D-02 environment exceeds component or instance bounds")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene["mf_scene_id"] = plan["scene_id"]; scene["mf_seed"] = plan["seed"]; scene["mf_builder_version"] = "external-v1"
    scene["mf_mask_palette_json"] = json.dumps(plan["mask_palette"], sort_keys=True)
    scene.unit_settings.system = "METRIC"; scene.unit_settings.scale_length = 1
    collection = bpy.data.collections.new("MovieFactoryExternal"); collection["mf_id"] = "collection_3d02_01"; scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    entities = {entity["id"]: entity for entity in plan["entities"]}

    courtyard = external_root(entities["courtyard_01"])
    for component in entities["courtyard_01"]["components"]:
        imported = attach_import(courtyard, component["id"] + "_template", "environment", component["source"])
        template = sorted(imported, key=lambda obj: obj["mf_id"])
        base_matrices = {obj: obj.matrix_local.copy() for obj in template}
        for index, instance in enumerate(component["instances"]):
            matrix = Matrix.Translation(instance["position"]) @ Matrix.Rotation(math.radians(instance.get("rotation_z_degrees", 0)), 4, "Z") @ Matrix.Diagonal((*instance.get("scale", [1,1,1]), 1))
            if index == 0:
                first = template[0]; first.matrix_local = matrix @ base_matrices[first]
                for obj in template: obj["mf_component_id"] = component["id"]
            else:
                copies = duplicate_component(template, base_matrices, courtyard, f"{component['id']}_{index:02d}", "environment", component["source"]["sha256"], matrix)
                for obj in copies: obj["mf_component_id"] = component["id"]

    motorcycle = external_root(entities["motorcycle_01"])
    bike_material = pbr_motorcycle_material("motorcycle_01", entities["motorcycle_01"]["textures"])
    attach_import(motorcycle, "body", "motorcycle", entities["motorcycle_01"]["source"], target_longest=entities["motorcycle_01"]["target_longest_m"], material_override=bike_material)

    sword = external_root(entities["sword_01"])
    attach_import(sword, "blade", "sword", entities["sword_01"]["source"], target_longest=entities["sword_01"]["target_longest_m"])
    add_external_rig(plan, collection)
    world = bpy.data.worlds.new("world_3d02_01"); world["mf_id"] = "world_3d02_01"; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = color(plan["world_color_hex"])
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = plan["world_strength"]; scene.world = world
    apply_profile(profile, plan["seed"]); scene.view_settings.exposure = plan["exposure"]; scene.camera = bpy.data.objects[plan["cameras"][0]["id"]]
    bpy.ops.file.pack_all()
    # Packed bytes are authoritative. A canonical virtual path prevents Blender
    # from rebasing source-machine paths when a self-contained file is saved in
    # a different replay directory.
    for image in bpy.data.images:
        if image.packed_file:
            image.filepath = "/__movie_factory_packed__/" + image.name
    bpy.context.view_layer.update()


def revise_external(operations):
    if operations != [
        {"op":"translate_entity","entity_id":"motorcycle_01","delta_m":[0.6,0,0]},
        {"op":"rotate_entity_z","entity_id":"sword_01","degrees":25},
    ]:
        raise ValueError("3D-02 accepts only the frozen two-operation revision")
    objects = {obj.get("mf_id"): obj for obj in bpy.context.scene.objects}; initial_ids = set(objects)
    motorcycle = objects["motorcycle_01"]; sword = objects["sword_01"]
    before_motorcycle = list(motorcycle.location); before_sword = math.degrees(sword.rotation_euler.z)
    motorcycle.location.x += .6; sword.rotation_euler.z += math.radians(25); bpy.context.view_layer.update()
    if initial_ids != {obj.get("mf_id") for obj in bpy.context.scene.objects}: raise RuntimeError("Revision changed object identity set")
    return [
        {"op":"translate_entity","entity_id":"motorcycle_01","before":before_motorcycle,"after":list(motorcycle.location)},
        {"op":"rotate_entity_z","entity_id":"sword_01","before_degrees":before_sword,"after_degrees":math.degrees(sword.rotation_euler.z)},
    ]


def material(mid, rgb, roughness=.5, metallic=0, emission=0):
    mat = bpy.data.materials.new(mid)
    mat["mf_id"] = mid
    mat.use_nodes = True
    p = mat.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = color(rgb)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Metallic"].default_value = metallic
    if emission:
        p.inputs["Emission Color"].default_value = color(rgb)
        p.inputs["Emission Strength"].default_value = emission
    # Keep diffuse_color at a neutral fixed value: shell revision changes exactly
    # its Principled Base Color, and the inspector preserves every other value.
    return mat


def root(entity):
    obj = bpy.data.objects.new(entity["id"], None)
    bpy.context.collection.objects.link(obj)
    identify(obj, entity["id"], entity["id"], entity["kind"])
    obj["mf_is_entity"] = True
    obj.location = entity["position"]
    obj.rotation_euler[2] = entity["rotation_z"]
    return obj


def finish(obj, parent, suffix, mat, location, scale=None, bevel=0, smooth=False):
    identify(obj, parent["mf_id"] + "_" + suffix, parent["mf_id"], parent["mf_kind"])
    if scale:
        obj.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("baked_edge_rounding", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if smooth:
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    obj.data.materials.append(mat)
    obj.parent = parent
    obj.location = location
    return obj


def box(parent, suffix, dims, location, mat, bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1)
    return finish(bpy.context.object, parent, suffix, mat, location, dims, bevel=bevel)


def cylinder(parent, suffix, radius, depth, location, mat, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth)
    return finish(bpy.context.object, parent, suffix, mat, location, bevel=min(radius / 6, .008), smooth=True)


def meshpart(parent, suffix, verts, faces, mat, smooth=True):
    mesh = bpy.data.meshes.new(suffix)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(suffix, mesh)
    bpy.context.collection.objects.link(obj)
    identify(obj, parent["mf_id"] + "_" + suffix, parent["mf_id"], parent["mf_kind"])
    obj.parent = parent
    mesh.materials.append(mat)
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return obj


def curve_tube(parent, suffix, points, radius, mat):
    # Explicit mesh tube, avoiding persistent procedural curve dependencies.
    verts, faces = [], []
    sides = 8
    for i, point in enumerate(points):
        tangent = Vector(points[min(i + 1, len(points) - 1)]) - Vector(points[max(0, i - 1)])
        tangent.normalize()
        normal = tangent.cross(Vector((0, 0, 1)))
        if normal.length < .01:
            normal = tangent.cross(Vector((1, 0, 0)))
        normal.normalize()
        binormal = tangent.cross(normal).normalized()
        for j in range(sides):
            offset = radius * (math.cos(j * math.tau / sides) * normal + math.sin(j * math.tau / sides) * binormal)
            verts.append(tuple(Vector(point) + offset))
        if i:
            for j in range(sides):
                a = (i - 1) * sides + j
                b = (i - 1) * sides + (j + 1) % sides
                faces.append((a, b, b + sides, a + sides))
    faces += [tuple(reversed(range(sides))), tuple(range((len(points) - 1) * sides, len(points) * sides))]
    return meshpart(parent, suffix, verts, faces, mat)


def build_sofa(e):
    r = root(e)
    w, d, h = e["dimensions"]
    fabric = material(e["id"] + "_fabric", e["color_hex"], e["roughness"])
    seam = material(e["id"] + "_piping", "#8B9995", .85)
    wood = material(e["id"] + "_feet", "#4C3023", .4)
    for i, x in enumerate((-.40 * w, .40 * w)):
        for j, y in enumerate((-.36 * d, .36 * d)):
            cylinder(r, f"foot_{i}_{j}", .033, .13 * h, (x, y, .065 * h), wood)
    box(r, "base", (.96 * w, .94 * d, .29 * h), (0, 0, .255 * h), fabric, .04)
    box(r, "back", (.96 * w, .17 * d, .62 * h), (0, .415 * d, .69 * h), fabric, .06)
    for i, x in enumerate((-.43 * w, .43 * w)):
        box(r, f"arm_{i}", (.14 * w, .94 * d, .43 * h), (x, -.02 * d, .545 * h), fabric, .045)
    for i, x in enumerate((-.18 * w, .18 * w)):
        box(r, f"seat_cushion_{i}", (.345 * w, .70 * d, .14 * h), (x, -.085 * d, .47 * h), fabric, .027)
        box(r, f"back_cushion_{i}", (.345 * w, .15 * d, .40 * h), (x, .235 * d, .755 * h), fabric, .035)
        # Delicate front cushion seam makes the upholstery read at room scale.
        curve_tube(r, f"seat_piping_{i}", [(x-.15*w, -.439*d, .505*h), (x+.15*w, -.439*d, .505*h)], .0025, seam)


def build_table(e):
    r = root(e)
    w, d, h = e["dimensions"]
    wood = material(e["id"] + "_wood", e["color_hex"], e["roughness"])
    metal = material(e["id"] + "_legs", "#252928", .3, .55)
    top_thickness = min(.07, h * .16)
    box(r, "top", (w, d, top_thickness), (0, 0, h - top_thickness/2), wood, .025)
    for i, x in enumerate((-.40 * w, .40 * w)):
        for j, y in enumerate((-.35 * d, .35 * d)):
            box(r, f"leg_{i}_{j}", (.045, .045, h - top_thickness), (x, y, (h - top_thickness)/2), metal, .008)
    # Under-top apron remains part of the translated assembly.
    box(r, "apron", (.83*w, .74*d, .045), (0, 0, h-top_thickness-.0225), wood, .009)


def build_lamp(e):
    r = root(e)
    w, d, h = e["dimensions"]
    metal = material(e["id"] + "_metal", "#36332E", .28, .65)
    shade = material(e["id"] + "_shade", e["color_hex"], e["roughness"], emission=.15)
    bulb = material(e["id"] + "_bulb", "#FFE1AD", .2, emission=3)
    cylinder(r, "base", min(w,d)*.37, .035, (0,0,.0175), metal)
    cylinder(r, "stem", .013, h*.78, (0,0,h*.39+.035), metal)
    segments=48
    verts, faces=[],[]
    # Open fabric frustum with thickness: visible shade and actual illuminated interior.
    for z, rx, ry in ((.72*h,w/2,d/2), (h,.34*w,.34*d), (.72*h,.48*w,.48*d), (h,.32*w,.32*d)):
        verts += [(rx*math.cos(i*math.tau/segments),ry*math.sin(i*math.tau/segments),z) for i in range(segments)]
    for i in range(segments):
        j=(i+1)%segments
        faces += [(i,j,segments+j,segments+i), (2*segments+i,3*segments+i,3*segments+j,2*segments+j),
                  (i,2*segments+i,2*segments+j,j), (segments+i,segments+j,3*segments+j,3*segments+i)]
    meshpart(r,"shade",verts,faces,shade)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=.045)
    finish(bpy.context.object,r,"bulb",bulb,(0,0,.84*h),smooth=True)
    data=bpy.data.lights.new(e["id"]+"_practical_data", "POINT")
    obj=bpy.data.objects.new(e["id"]+"_practical",data)
    bpy.context.collection.objects.link(obj)
    identify(obj,e["id"]+"_practical",e["id"],e["kind"])
    obj.parent=r
    obj.location=(0,0,.82*h)
    data.energy=35
    data.color=color("#FFD39B")[:3]
    data.shadow_soft_size=.10


def build_helmet(e):
    r=root(e)
    w,d,h=e["dimensions"]
    shell=material("helmet_shell_01",e["color_hex"],e["roughness"],metallic=.12)
    visor=material("helmet_visor_01","#172731",.12,metallic=.5)
    trim=material("helmet_trim_01","#151719",.5)
    chrome=material("helmet_hardware_01","#9BA6AB",.24,.8)
    # Full-face shell: dome, side cheeks and chin bar share one dedicated shell
    # material. The eye opening is a real cutout with a separate curved visor.
    rows, cols=28,64
    pmax=.86*math.pi
    def surface(phi,theta,expand=1):
        return (expand*w*.5*math.sin(phi)*math.cos(theta),
                expand*d*.5*math.sin(phi)*math.sin(theta),
                h*.5+h*.5*math.cos(phi))
    verts=[surface(i*pmax/rows,j*math.tau/cols) for i in range(rows+1) for j in range(cols)]
    faces=[]
    for i in range(rows):
        phi=(i+.5)*pmax/rows
        for j in range(cols):
            theta=(j+.5)*math.tau/cols
            front=abs(math.atan2(math.sin(theta+math.pi/2),math.cos(theta+math.pi/2)))
            if .37*math.pi < phi < .61*math.pi and front < .90:
                continue
            faces.append((i*cols+j,i*cols+(j+1)%cols,(i+1)*cols+(j+1)%cols,(i+1)*cols+j))
    meshpart(r,"shell",verts,faces,shell)
    vr,vc=10,32
    pv=[surface(.37*math.pi+i*(.24*math.pi)/vr,-math.pi/2-.91+j*1.82/vc,1.009) for i in range(vr+1) for j in range(vc+1)]
    pf=[(i*(vc+1)+j,i*(vc+1)+j+1,(i+1)*(vc+1)+j+1,(i+1)*(vc+1)+j) for i in range(vr) for j in range(vc)]
    meshpart(r,"visor",pv,pf,visor)
    for name,phi in (("visor_upper_rim",.37*math.pi),("visor_lower_rim",.61*math.pi)):
        points=[surface(phi,-math.pi/2-.93+j*1.86/40,1.018) for j in range(41)]
        curve_tube(r,name,points,.006,trim)
    for side,theta in (("left",-math.pi/2-.92),("right",-math.pi/2+.92)):
        points=[surface(.37*math.pi+j*.24*math.pi/16,theta,1.018) for j in range(17)]
        curve_tube(r,"visor_"+side+"_rim",points,.005,trim)
        # Flat pivot discs orient normal to the curved visor side.
        pos=surface(.49*math.pi,theta,1.022)
        cap=cylinder(r,"visor_"+side+"_pivot",.020,.010,pos,chrome,24)
        cap.rotation_euler=(math.pi/2,0,theta+math.pi/2)
    # Bottom gasket meets the supporting cushion exactly at root Z.
    pts=[(w*.30*math.cos(j*math.tau/64),d*.30*math.sin(j*math.tau/64),.007) for j in range(65)]
    curve_tube(r,"bottom_gasket",pts,.007,trim)
    # Chin vent and top vent distinguish the prop from a colored sphere.
    chin=box(r,"chin_vent",(.24*w,.016,.07*h),(0,-d*.43,.19*h),trim,.006)
    chin.rotation_euler[0]=-.16
    for i,x in enumerate((-.055*w,.055*w)):
        top=box(r,f"top_vent_{i}",(.055*w,.16*d,.012),(x,-.055*d,.965*h),trim,.003)
        top.rotation_euler[0]=-.20


def aim(obj,target):
    direction=Vector(target)-obj.location
    if direction.length < .00001:
        raise ValueError("Camera/light target equals its position")
    obj.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()


def apply_profile(profile,seed):
    s=bpy.context.scene
    if profile.get("device") != "CPU":
        raise ValueError("Only explicitly qualified CPU renderer is implemented")
    width,height,samples=profile["width"],profile["height"],profile["samples"]
    if not (64<=width<=4096 and 64<=height<=2160 and 1<=samples<=256):
        raise ValueError("Render resource limits exceeded")
    s.render.engine="CYCLES"
    s.cycles.device="CPU"
    s.cycles.samples=samples
    s.cycles.seed=seed
    s.cycles.use_animated_seed=False
    s.cycles.use_adaptive_sampling=False
    s.cycles.use_denoising=False
    s.cycles.max_bounces=8
    s.cycles.diffuse_bounces=4
    s.cycles.glossy_bounces=4
    s.cycles.transmission_bounces=4
    s.render.resolution_x=width
    s.render.resolution_y=height
    s.render.resolution_percentage=100
    s.render.pixel_aspect_x=s.render.pixel_aspect_y=1
    s.render.film_transparent=False
    s.render.image_settings.file_format="PNG"
    s.render.image_settings.color_mode="RGB"
    s.render.image_settings.color_depth="8"
    s.render.image_settings.compression=30
    s.render.use_file_extension=True
    s.view_settings.view_transform="AgX"
    s.view_settings.look="AgX - Medium High Contrast"
    s.view_settings.gamma=1
    s.display_settings.display_device="sRGB"
    s.frame_set(1)


def build(plan,profile):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s=bpy.context.scene
    s["mf_scene_id"]=plan["scene_id"]
    s["mf_seed"]=plan["seed"]
    s["mf_builder_version"]="procedural-v1"
    s["mf_room_interior_bounds"]=list(plan["room"]["size_m"])
    s.unit_settings.system="METRIC"
    s.unit_settings.scale_length=1
    collection=bpy.data.collections.new("MovieFactory")
    collection["mf_id"]="collection_scene_01"
    s.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    room=root({"id":"room_01","kind":"room","position":[0,0,0],"rotation_z":0})
    rw,rd,rh=plan["room"]["size_m"]
    wall=material("room_wall_01",plan["room"]["wall_color_hex"],.88)
    floor=material("room_floor_01",plan["room"]["floor_color_hex"],.46)
    trim=material("room_baseboard_01","#E4DED1",.6)
    box(room,"floor",(rw,rd,.10),(0,0,-.05),floor,.0)
    box(room,"back_wall",(rw+.20,.10,rh),(0,rd/2+.05,rh/2),wall,.0)
    for side,x in (("left",-rw/2-.05),("right",rw/2+.05)):
        box(room,side+"_wall",(.10,rd,rh),(x,0,rh/2),wall,.0)
        box(room,side+"_baseboard",(.025,rd,.09),(math.copysign(rw/2-.0125,x),0,.045),trim,.002)
    box(room,"back_baseboard",(rw,.025,.09),(0,rd/2-.0125,.045),trim,.002)
    builders={"sofa":build_sofa,"coffee_table":build_table,"floor_lamp":build_lamp,"motorcycle_helmet":build_helmet}
    if len(plan["entities"]) != 4 or len(plan["cameras"]) != 3 or not 1 <= len(plan["lights"]) <= 6:
        raise ValueError("Plan exceeds bounded entity/camera/light vocabulary")
    for e in plan["entities"]:
        if e["kind"] not in builders:
            raise ValueError("Unsupported entity builder")
        builders[e["kind"]](e)
    for c in plan["cameras"]:
        data=bpy.data.cameras.new(c["id"]+"_data")
        obj=bpy.data.objects.new(c["id"],data)
        collection.objects.link(obj)
        identify(obj,c["id"],None,"camera")
        obj["mf_shot_id"]=c["shot_id"]
        obj.location=c["position"]
        aim(obj,c["target"])
        data.lens=c["lens_mm"]
        data.sensor_width=36
        data.sensor_fit="HORIZONTAL"
        data.clip_start=.01
        data.clip_end=100
        data.dof.use_dof=False
    for l in plan["lights"]:
        if l["type"] not in {"AREA","POINT"}:
            raise ValueError("Unsupported light type")
        data=bpy.data.lights.new(l["id"]+"_data",l["type"])
        obj=bpy.data.objects.new(l["id"],data)
        collection.objects.link(obj)
        identify(obj,l["id"],None,"light")
        obj.location=l["position"]
        aim(obj,l["target"])
        data.energy=l["energy_w"]
        data.color=color(l["color_hex"])[:3]
        if l["type"] == "AREA":
            data.shape="DISK"
            data.size=l["size_m"]
        else:
            data.shadow_soft_size=l["size_m"]
    world=bpy.data.worlds.new("world_01")
    world["mf_id"]="world_01"
    world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=color("#D5E3FF")
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=plan["world_strength"]
    s.world=world
    apply_profile(profile,plan["seed"])
    s.view_settings.exposure=plan["exposure"]
    s.camera=bpy.data.objects[plan["cameras"][0]["id"]]
    bpy.context.view_layer.update()


def revise(operations):
    if len(operations) != 2:
        raise ValueError("Canonical revision requires exactly two operations")
    objects={o.get("mf_id"):o for o in bpy.context.scene.objects}
    initial_ids=set(objects)
    applied=[]
    seen=set()
    for operation in operations:
        op=operation["op"]
        if op in seen:
            raise ValueError("Duplicate operation")
        seen.add(op)
        if op=="translate_toward":
            if set(operation)!={"op","entity_id","target_entity_id","distance_m"} or operation["entity_id"]!="coffee_table_01" or operation["target_entity_id"]!="sofa_01":
                raise ValueError("Unsupported translation target or fields")
            if abs(operation["distance_m"]-.4)>.0000001:
                raise ValueError("Canonical translation must be 0.4 meters")
            table,sofa=objects["coffee_table_01"],objects["sofa_01"]
            origin=table.location.copy()
            direction=sofa.location-origin
            direction.z=0
            if direction.length<.001:
                raise ValueError("Cannot compute table direction")
            target=origin+direction.normalized()*.4
            table.location=target
            applied.append({"op":op,"entity_id":"coffee_table_01","parent_position":list(origin),"absolute_target":list(target)})
        elif op=="set_base_color":
            if set(operation)!={"op","entity_id","material_id","color_hex"} or operation["entity_id"]!="helmet_01" or operation["material_id"]!="helmet_shell_01":
                raise ValueError("Unsupported material target or fields")
            if operation["color_hex"].upper()!="#163D2A":
                raise ValueError("Canonical helmet target must be #163D2A")
            mat=bpy.data.materials.get("helmet_shell_01")
            if not mat or not mat.use_nodes:
                raise ValueError("Missing dedicated helmet shell material")
            users=[o for o in objects.values() if hasattr(o.data,"materials") and mat.name in o.data.materials]
            if not users or any(o.get("mf_entity")!="helmet_01" for o in users):
                raise ValueError("Helmet shell material is not private")
            mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=color(operation["color_hex"])
            applied.append({"op":op,"material_id":"helmet_shell_01","base_color_linear":list(color(operation["color_hex"]))})
        else:
            raise ValueError("Unsupported revision operation")
    if initial_ids!={o.get("mf_id") for o in bpy.context.scene.objects}:
        raise RuntimeError("Revision changed object identity set")
    bpy.context.view_layer.update()
    return applied


EVALUATOR_CORRUPTIONS={"missing_object","wrong_color","camera_drift","lighting_drift","intersection","degraded_composition"}


def evaluator_corrupt(corruption):
    """Apply one fixed, labeled corruption for the offline evaluator benchmark."""
    if not isinstance(corruption,dict) or set(corruption)!={"kind"} or corruption["kind"] not in EVALUATOR_CORRUPTIONS:
        raise ValueError("Unsupported evaluator corruption")
    kind=corruption["kind"]
    objects={o.get("mf_id"):o for o in bpy.context.scene.objects if o.get("mf_id")}
    if kind=="missing_object":
        root=objects["floor_lamp_01"]
        stack=[root]
        while stack:
            current=stack.pop()
            current.hide_render=True
            stack.extend(current.children)
    elif kind=="wrong_color":
        mat=bpy.data.materials.get("helmet_shell_01")
        if not mat or not mat.use_nodes:
            raise ValueError("Missing helmet material")
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=color("#1565C0")
    elif kind=="camera_drift":
        camera=objects["camera_B"]
        camera.rotation_euler[2]+=.72
        camera.data.lens=58
    elif kind=="lighting_drift":
        key=objects["key_light_01"]
        fill=objects["fill_light_01"]
        key.data.energy=90
        key.data.color=color("#C62828")[:3]
        fill.data.energy=25
    elif kind=="intersection":
        table=objects["coffee_table_01"]
        sofa=objects["sofa_01"]
        table.location.x=sofa.location.x
        table.location.y=sofa.location.y-.25
        table.location.z=.45
    elif kind=="degraded_composition":
        camera=objects["camera_A"]
        camera.rotation_euler[2]+=.95
        camera.data.lens=110
    bpy.context.view_layer.update()
    return {"kind":kind,"fixture_only":True}


PALETTE={"helmet_01":[255,0,0],"coffee_table_01":[0,255,0],"sofa_01":[0,0,255],
         "floor_lamp_01":[255,255,0],"room_01":[128,128,128]}


def render(native,out,profile,seed):
    shots=profile["shots"]
    if not shots or set(shots)-{"shot_A","shot_B","shot_C"}:
        raise ValueError("Unknown render shot")
    for folder in ("renders","masks"):
        (out/folder).mkdir(exist_ok=True)
    times={}
    artifacts=[]
    # Reload parent for each beauty/mask pass. Transient material overrides never
    # touch the saved native scene or leak into a later shot.
    for shot in shots:
        t=time.monotonic()
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        apply_profile(profile,seed)
        s=bpy.context.scene
        s.camera=next(o for o in s.objects if o.type=="CAMERA" and o.get("mf_shot_id")==shot)
        s.frame_set(int(s.camera.get("mf_frame",1)))
        s.render.filepath=str(out/"renders"/(shot+".png"))
        bpy.ops.render.render(write_still=True)
        times[shot+"_beauty_seconds"]=time.monotonic()-t
        artifacts.append("renders/"+shot+".png")
        t=time.monotonic()
        maskmats={}
        palette=json.loads(s.get("mf_mask_palette_json",json.dumps(PALETTE)))
        if not isinstance(palette,dict) or not palette:
            raise ValueError("Scene mask palette is invalid")
        for entity,rgb in palette.items():
            mat=bpy.data.materials.new("__mask_"+entity)
            mat.use_nodes=True
            mat.node_tree.nodes.clear()
            emit=mat.node_tree.nodes.new("ShaderNodeEmission")
            emit.inputs["Color"].default_value=tuple(srgb_channel(c/255) for c in rgb)+(1,)
            emit.inputs["Strength"].default_value=1
            output=mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
            mat.node_tree.links.new(emit.outputs["Emission"],output.inputs["Surface"])
            maskmats[entity]=mat
        for obj in s.objects:
            if obj.type=="MESH":
                entity=obj.get("mf_entity")
                if entity not in maskmats:
                    raise ValueError("Mesh has no allowlisted entity mask: "+obj.name)
                mat=maskmats[entity]
                obj.data.materials.clear()
                obj.data.materials.append(mat)
                for face in obj.data.polygons:
                    face.material_index=0
        s.world.node_tree.nodes["Background"].inputs["Strength"].default_value=0
        s.view_settings.view_transform="Standard"
        s.view_settings.look="None"
        s.view_settings.exposure=0
        s.view_settings.gamma=1
        s.cycles.samples=1
        s.cycles.max_bounces=0
        s.cycles.use_denoising=False
        s.render.filepath=str(out/"masks"/(shot+".png"))
        bpy.ops.render.render(write_still=True)
        times[shot+"_mask_seconds"]=time.monotonic()-t
        artifacts.append("masks/"+shot+".png")
    write_json(out/"mask-legend.json",{"schema_version":"1.0","encoding":"rgb8","entities":palette,
        "background":[0,0,0],"method":"opaque emission Cycles CPU one-sample pass; edge antialiasing; stable entity colors"})
    return artifacts+["mask-legend.json"],times


def write_json(path,data):
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+"\n")
    temporary.replace(path)


def main():
    args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    parser=argparse.ArgumentParser()
    parser.add_argument("--job",required=True)
    parsed=parser.parse_args(args)
    job=json.loads(Path(parsed.job).read_text())
    out=Path(job["output_dir"])
    out.mkdir(parents=True,exist_ok=True)
    status={"ok":False,"mode":job["mode"],"artifacts":[],"timings":{}}
    start=time.monotonic()
    try:
        inspector=load_inspector()
        mode=job["mode"]
        profile=job["profile"]
        if mode=="asset_probe":
            probe=asset_probe(job["asset"])
            write_json(out/"probe.json",probe)
            status["artifacts"].append("probe.json")
        elif mode=="animation_probe":
            probe=animation_probe(job["asset"])
            write_json(out/"probe.json",probe)
            status["artifacts"].append("probe.json")
        elif mode=="character_bake_diagnostic":
            diagnostic_spec=importlib.util.spec_from_file_location("mf_character_diagnostic",Path(__file__).with_name("character_diagnostic.py"))
            diagnostic=importlib.util.module_from_spec(diagnostic_spec)
            diagnostic_spec.loader.exec_module(diagnostic)
            diagnostic.run(sys.modules[__name__],out,job["plan"],job.get("parent_native"))
            status["artifacts"].append("diagnostic.json")
        elif mode=="character_production_regression":
            diagnostic_spec=importlib.util.spec_from_file_location("mf_character_diagnostic",Path(__file__).with_name("character_diagnostic.py"))
            diagnostic=importlib.util.module_from_spec(diagnostic_spec)
            diagnostic_spec.loader.exec_module(diagnostic)
            diagnostic.run_production_regression(sys.modules[__name__],out,job["plan"])
            status["artifacts"].append("production-regression.json")
        elif mode=="build":
            build(job["plan"],profile)
        elif mode=="build_external":
            build_external(job["plan"], profile)
        elif mode=="build_character":
            build_character(job["plan"],profile)
        elif mode in {"revise","revise_external","revise_character","build_performance","inspect","render","evaluator_corrupt","character_temporal","performance_evidence"}:
            native=Path(job["parent_native"])
            if native.resolve()==(out/"scene.blend").resolve():
                raise ValueError("Parent native may never be overwritten")
            bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
            if mode=="revise":
                mutations=revise(job["operations"])
                write_json(out/"mutations.json",mutations)
                status["artifacts"].append("mutations.json")
            elif mode=="revise_external":
                mutations=revise_external(job["operations"])
                write_json(out/"mutations.json",mutations)
                status["artifacts"].append("mutations.json")
            elif mode=="revise_character":
                mutations=revise_character(job["operations"])
                write_json(out/"mutations.json",mutations)
                status["artifacts"].append("mutations.json")
            elif mode=="build_performance":
                mutations=build_performance(job["operations"])
                write_json(out/"mutations.json",mutations)
                status["artifacts"].append("mutations.json")
            elif mode=="evaluator_corrupt":
                mutation=evaluator_corrupt(job.get("corruption"))
                write_json(out/"corruption.json",mutation)
                status["artifacts"].append("corruption.json")
            elif mode=="character_temporal":
                evidence=character_temporal_evidence(out,profile,job["seed"],job["request"])
                status["artifacts"].append("temporal-metrics.json")
                status["artifacts"].extend(
                    f"frames/{clip}/frame-{frame:04d}.png"
                    for clip,item in evidence["clips"].items()
                    for frame in range(item["frame_start"],item["frame_end"]+1)
                )
            elif mode=="performance_evidence":
                evidence=performance_evidence(out,profile,job["seed"],job["campaign"],job.get("render_frames",False))
                status["artifacts"].append("performance-metrics.json")
                if job.get("render_frames",False):
                    status["artifacts"].extend(
                        f"frames/{role}/frame-{frame:04d}.png"
                        for role in ("baseline","candidate") for frame in range(1,97))
        else:
            raise ValueError("Unknown worker mode")
        if mode in {"build","build_external","build_character","revise","revise_external","revise_character","build_performance","evaluator_corrupt"}:
            bpy.context.preferences.filepaths.save_version=0
            bpy.ops.wm.save_as_mainfile(filepath=str(out/"scene.blend"),check_existing=False,compress=True,relative_remap=False)
            status["artifacts"].append("scene.blend")
        if mode in {"build","build_external","build_character","revise","revise_external","revise_character","build_performance","inspect","evaluator_corrupt"}:
            state=inspector.snapshot()
            write_json(out/"snapshot.json",state)
            status["artifacts"].append("snapshot.json")
        if mode=="render":
            artifacts,times=render(Path(job["parent_native"]),out,profile,job["seed"])
            status["artifacts"].extend(artifacts)
            status["timings"].update(times)
        status["ok"]=True
    except Exception as exc:
        status["error"]=type(exc).__name__+": "+str(exc)
        traceback.print_exc()
        raise
    finally:
        status["timings"]["worker_total_seconds"]=time.monotonic()-start
        status["toolchain"]={"blender":bpy.app.version_string,"build_hash":bpy.app.build_hash.decode(),"python":sys.version.split()[0]}
        write_json(out/"worker-status.json",status)


if __name__=="__main__":
    main()
