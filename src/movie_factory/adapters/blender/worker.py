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
from mathutils import Vector
from mathutils import Matrix


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
    return {
        "schema_version":"1.0","source_sha256":spec["sha256"],"object_count":len(imported),
        "object_types":sorted({obj.type for obj in imported}),
        "objects":[{"name":obj.name,"type":obj.type,"parent":obj.parent.name if obj.parent else None,
                    "modifiers":[mod.type for mod in obj.modifiers],"vertex_groups":[group.name for group in obj.vertex_groups]} for obj in imported],
        "topology":{"vertices":sum(len(obj.data.vertices) for obj in meshes),"polygons":sum(len(obj.data.polygons) for obj in meshes)},
        "armatures":[{"name":obj.name,"bones":[{"name":bone.name,"parent":bone.parent.name if bone.parent else None,
                      "head":list(bone.head_local),"tail":list(bone.tail_local),"use_deform":bone.use_deform} for bone in obj.data.bones]} for obj in armatures],
        "actions":[{"name":action.name,"frame_range":list(action.frame_range),"curve_count":len(action_channels(action)),
                    "keyframe_count":sum(len(curve.keyframe_points) for curve in action_channels(action)),
                    "data_paths":sorted({curve.data_path for curve in action_channels(action)})} for action in actions],
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


def import_character_action(spec, clip_name, target_armature):
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
    action=bpy.data.actions.new("character_action_"+clip_name)
    target_armature.animation_data_create(); target_armature.animation_data.action=action
    # Animation-only FBXs can encode clip-specific bind/rest transforms. Raw
    # curve copying therefore produces plausible metadata but visibly broken
    # limbs on the model's canonical rig. Evaluate the verified source rig and
    # deterministically bake each same-name pose into canonical armature space.
    ordered=sorted(target_armature.pose.bones,key=lambda bone:len(bone.parent_recursive))
    scene=bpy.context.scene; first,last=(int(round(value)) for value in source.frame_range)
    source_to_target=target_armature.matrix_world.inverted()@source_armature.matrix_world
    for frame in range(first,last+1):
        scene.frame_set(frame); bpy.context.view_layer.update()
        poses={name:(source_to_target@source_armature.pose.bones[name].matrix).copy() for name in source_names}
        for bone in ordered:
            bone.rotation_mode="QUATERNION"; bone.matrix=poses[bone.name]
        bpy.context.view_layer.update()
        for bone in ordered:
            bone.keyframe_insert(data_path="location",frame=frame,group=bone.name)
            bone.keyframe_insert(data_path="rotation_quaternion",frame=frame,group=bone.name)
            bone.keyframe_insert(data_path="scale",frame=frame,group=bone.name)
    for curve in action_channels(action):
        for key in curve.keyframe_points: key.interpolation="LINEAR"
    action["mf_id"]=action.name; action["mf_clip_name"]=clip_name; action["mf_source_sha256"]=spec["sha256"]; action.use_fake_user=True
    target_armature.animation_data.action=None
    for obj in objects: bpy.data.objects.remove(obj,do_unlink=True)
    for imported in actions:
        bpy.data.actions.remove(imported)
    return action


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


def build_character(plan,profile):
    if plan.get("schema_version")!="1.0" or plan.get("experiment_id")!="3D-03": raise ValueError("Unsupported character scene plan")
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
    armature["mf_animation_normalization"]="same_skeleton_pose_bake_v1"
    skin_material,skins=character_material("character_01",entity["skins"])
    mesh.data.materials.clear(); mesh.data.materials.append(skin_material)
    actions={name:import_character_action(spec,name,armature) for name,spec in plan["clips"].items()}
    assign_character_action(armature,actions["idle"])
    armature["mf_active_action"]="idle"; character["mf_active_skin"]="cyborg"
    scene.frame_start=1; scene.frame_end=33; scene.frame_set(1)
    low,high=evaluated_bounds([mesh]); height=high[2]-low[2]
    factor=entity["target_height_m"]/height
    character.scale=(factor,factor,factor); bpy.context.view_layer.update()
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
        elif mode=="build":
            build(job["plan"],profile)
        elif mode=="build_external":
            build_external(job["plan"], profile)
        elif mode=="build_character":
            build_character(job["plan"],profile)
        elif mode in {"revise","revise_external","revise_character","inspect","render","evaluator_corrupt"}:
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
            elif mode=="evaluator_corrupt":
                mutation=evaluator_corrupt(job.get("corruption"))
                write_json(out/"corruption.json",mutation)
                status["artifacts"].append("corruption.json")
        else:
            raise ValueError("Unknown worker mode")
        if mode in {"build","build_external","build_character","revise","revise_external","revise_character","evaluator_corrupt"}:
            bpy.context.preferences.filepaths.save_version=0
            bpy.ops.wm.save_as_mainfile(filepath=str(out/"scene.blend"),check_existing=False,compress=True,relative_remap=False)
            status["artifacts"].append("scene.blend")
        if mode in {"build","build_external","build_character","revise","revise_external","revise_character","inspect","evaluator_corrupt"}:
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
