"""Trusted Blender implementation for the frozen 3D-05 sword interaction."""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


CONTROLS = {
    "early_attachment", "attachment_teleportation", "hand_sword_sliding",
    "penetration", "edit_leakage",
}
ARM_BONES = ("RightArm", "RightForeArm", "RightHand")


def _smooth(value):
    x = max(0.0, min(1.0, float(value)))
    return 6*x**5 - 15*x**4 + 10*x**3


def _envelope(frame):
    if frame <= 28 or frame >= 76:
        return 0.0
    if frame < 36:
        return _smooth((frame-28)/8)
    if frame <= 68:
        return 1.0
    return _smooth((76-frame)/8)


def _source_time(frame, role, control=None):
    if role == "baseline":
        return frame
    if control == "edit_leakage":
        return frame + 4
    return frame + 4*_envelope(frame)


def _state(source_time):
    if source_time <= 16:
        return "supported"
    if source_time < 40:
        return "reaching"
    if source_time < 48:
        return "grasped"
    if source_time < 68:
        return "lifting"
    return "held"


def _owner(state):
    return "sword_support_01" if state in {"supported", "reaching"} else "character_01/right_hand"


def _set_time(frame):
    whole = math.floor(frame)
    bpy.context.scene.frame_set(whole, subframe=frame-whole)
    bpy.context.view_layer.update()


def _lerp(left, right, weight):
    return left.lerp(right, _smooth(weight))


def _hand_target(source_time, initial, supported, held):
    if source_time <= 16:
        return initial.copy()
    if source_time < 40:
        return _lerp(initial, supported, (source_time-16)/24)
    if source_time < 48:
        return supported.copy()
    if source_time < 68:
        x = (source_time-48)/20
        return supported.lerp(held, 3*x*x-2*x*x*x)
    return held.copy()


def _arm_matrices(mf, armature, initial, target, hand_direction):
    upper = armature.pose.bones["RightArm"]
    lower = armature.pose.bones["RightForeArm"]
    hand = armature.pose.bones["RightHand"]
    shoulder = initial[upper.name].translation
    base_elbow = initial[lower.name].translation
    base_wrist = initial[hand.name].translation
    first = (base_elbow-shoulder).length
    second = (base_wrist-base_elbow).length
    hand_length = (initial[hand.name]@Vector((0, hand.bone.length, 0))-base_wrist).length
    wrist = target-hand_direction.normalized()*hand_length
    direction = wrist-shoulder
    distance = direction.length
    if distance <= 1e-8 or distance >= first+second-1e-6:
        raise ValueError(f"3D-05 hand target is outside arm reach: {distance:.6f} >= {first+second:.6f}")
    unit = direction.normalized()
    along = (first*first-second*second+distance*distance)/(2*distance)
    height = math.sqrt(max(0.0, first*first-along*along))
    base_projection = base_elbow-(shoulder+unit*(base_elbow-shoulder).dot(unit))
    if base_projection.length <= 1e-8:
        base_projection = Vector((0, 1, 0)).cross(unit)
    bend = base_projection.normalized()
    elbow = shoulder+unit*along+bend*height
    desired = {name: matrix.copy() for name, matrix in initial.items()}
    desired[upper.name] = mf._orient_bone(initial[upper.name], upper, shoulder, elbow)
    desired[lower.name] = mf._orient_bone(initial[lower.name], lower, elbow, wrist)
    desired[hand.name] = mf._orient_bone(initial[hand.name], hand, wrist, target)
    return desired


def _insert_pose(mf, armature, action, frame, desired, rest, previous, key_names=ARM_BONES):
    mf.assign_character_action(armature, action)
    actual = {}
    for bone in sorted(armature.pose.bones, key=lambda item: len(item.parent_recursive)):
        matrix = desired.get(bone.name)
        if matrix is None:
            continue
        parent_args = ({"parent_matrix": actual[bone.parent.name],
                        "parent_matrix_local": rest[bone.parent.name]}
                       if bone.parent else {})
        basis = bone.bone.convert_local_to_pose(matrix, rest[bone.name], invert=True, **parent_args)
        location, rotation, scale = basis.decompose()
        rotation.normalize()
        if bone.name in previous and previous.get(bone.name) is not None and rotation.dot(previous[bone.name]) < 0:
            rotation.negate()
        if bone.name in previous:
            previous[bone.name] = rotation.copy()
        actual[bone.name] = bone.bone.convert_local_to_pose(
            Matrix.LocRotScale(location, rotation, scale), rest[bone.name], **parent_args)
        if bone.name not in key_names:
            continue
        bone.rotation_mode = "QUATERNION"
        bone.location = location
        bone.rotation_quaternion = rotation
        bone.scale = scale
        bone.keyframe_insert(data_path="location", frame=frame, group=bone.name)
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=bone.name)
        bone.keyframe_insert(data_path="scale", frame=frame, group=bone.name)


def _create_character_action(mf, armature, role, initial, supported, held, control):
    name = f"character_action_pickup_3d05_{role}_96"
    old = bpy.data.actions.get(name)
    if old:
        bpy.data.actions.remove(old)
    action = bpy.data.actions.new(name)
    action["mf_id"] = name
    action["mf_interaction_role"] = role
    action["mf_timeline_fps"] = 24.0
    action["mf_frame_start"] = 1
    action["mf_frame_end"] = 96
    action["mf_revision"] = "shift_interaction_timing_v1" if role == "candidate" else "none"
    if control:
        action["mf_failure_control"] = control
    action.use_fake_user = True
    rest = {bone.name: bone.bone.matrix_local.copy() for bone in armature.pose.bones}
    previous = {name: None for name in ARM_BONES}
    shoulder = initial["RightArm"].translation
    hand_bone = armature.pose.bones["RightHand"]
    initial_anchor = initial["RightHand"]@Vector((0, hand_bone.bone.length, 0))
    initial_hand_direction = ((initial["RightHand"]@Vector((0, armature.pose.bones["RightHand"].bone.length, 0)))-
                              initial["RightHand"].translation).normalized()
    all_names = frozenset(initial)
    _insert_pose(mf, armature, action, 1, initial, rest, {}, all_names)
    _insert_pose(mf, armature, action, 96, initial, rest, {}, all_names)
    for index in range(761):
        frame = 1+index*.125
        source_time = _source_time(frame, role, control)
        target = _hand_target(source_time, initial_anchor, supported, held)
        direction_goal = (target-shoulder).normalized()
        direction_weight = 0.0 if source_time <= 16 else _smooth(min(1.0, (source_time-16)/24))
        hand_direction = initial_hand_direction.lerp(direction_goal, direction_weight).normalized()
        desired = _arm_matrices(mf, armature, initial, target, hand_direction)
        _insert_pose(mf, armature, action, frame, desired, rest, previous)
    for curve in mf.action_channels(action):
        for key in curve.keyframe_points:
            key.interpolation = "LINEAR"
    return action


def _new_root(mf, name, kind, source_sha):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    mf.identify_external(obj, name, name, kind, source_sha)
    obj["mf_is_entity"] = True
    return obj


def _setup_support(mf, config):
    mat = mf.material("sword_support_material_3d05", "#53616B", .5, metallic=.15)
    bpy.ops.mesh.primitive_cube_add(size=1, location=config["support"]["position_m"])
    support = bpy.context.object
    support.dimensions = config["support"]["dimensions_m"]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mf.identify_external(support, "sword_support_01", "sword_support_01", "support", "procedural-support-v1")
    support["mf_is_entity"] = True
    support.data.materials.append(mat)
    bevel = support.modifiers.new("support_edge_softening", "BEVEL")
    bevel.width = .015
    bevel.segments = 2
    return support


def _setup_cameras(mf, config):
    for old in list(bpy.data.objects):
        if old.type == "CAMERA":
            bpy.data.objects.remove(old, do_unlink=True)
    result = {}
    for spec in config["cameras"]:
        key = spec["view"]
        data = bpy.data.cameras.new(f"camera_3d05_{key}_data")
        camera = bpy.data.objects.new(f"camera_3d05_{key}", data)
        bpy.context.collection.objects.link(camera)
        mf.identify_external(camera, camera.name, None, "camera", "3d05-rig-v1")
        camera.location = spec["position"]
        mf.aim(camera, spec["target"])
        data.lens = spec["lens_mm"]
        data.sensor_width = 36
        data.clip_start = .01
        data.clip_end = 100
        camera["mf_view"] = key
        result[key] = camera
    bpy.context.scene.camera = result["primary"]
    return result


def _create_sword(mf, config):
    source = config["sword"]["source"]
    root = _new_root(mf, "sword_01", "sword", source["sha256"])
    sword_material = mf.material("sword_material_3d05", "#8A9299", .24, metallic=.82)
    materials_before = set(bpy.data.materials)
    images_before = set(bpy.data.images)
    imported = mf.attach_import(root, "geometry", "sword_geometry", source,
                                target_longest=config["sword"]["target_longest_m"],
                                material_override=sword_material)
    top = [obj for obj in imported if obj.parent == root]
    grip = Vector(config["sword"]["supported_grip_world_m"])
    bpy.context.view_layer.update()
    low, high = mf.asset_world_bounds(imported)
    desired_bottom = grip.z-config["sword"]["grip_offset_from_geometry_base_m"]
    delta = Vector((grip.x-(low[0]+high[0])/2, grip.y-(low[1]+high[1])/2, desired_bottom-low[2]))
    desired_world = {obj: Matrix.Translation(delta)@obj.matrix_world for obj in top}
    # The semantic root is the centre of the handle.  Its geometry and rotation
    # remain blade-up; only its location becomes relative to the hand at grasp.
    root.matrix_world = Matrix.Translation(grip)
    for obj in top:
        obj.matrix_world = desired_world[obj]
    for material in list(set(bpy.data.materials)-materials_before):
        if material != sword_material and material.users == 0:
            bpy.data.materials.remove(material)
    for image in list(set(bpy.data.images)-images_before):
        if image.users == 0:
            bpy.data.images.remove(image)
    root["mf_grip_anchor"] = "semantic_root"
    root["mf_handle_contact_radius_m"] = config["sword"]["handle_contact_radius_m"]
    root["mf_hand_surface_offset_world_json"] = json.dumps(config["sword"]["hand_surface_offset_world_m"])
    root["mf_supported_location_world_json"] = json.dumps(list(grip))
    root["mf_supported_quaternion_json"] = json.dumps(list(root.matrix_world.to_quaternion()))
    root["mf_supported_world_matrix_json"] = json.dumps([list(row) for row in root.matrix_world])
    return root, imported


def _create_sword_action(mf, sword, armature, role, control):
    name = f"sword_action_pickup_3d05_{role}_96"
    action = bpy.data.actions.new(name)
    action["mf_id"] = name
    action["mf_interaction_role"] = role
    action.use_fake_user = True
    mf.assign_character_action(sword, action)
    supported = Vector(json.loads(sword["mf_supported_location_world_json"]))
    hand_surface_offset = Vector(json.loads(sword["mf_hand_surface_offset_world_json"]))
    attached_base = -hand_surface_offset
    for index in range(761):
        frame = 1+index*.125
        source_time = _source_time(frame, role, control)
        influence = 1.0 if source_time >= 40 else 0.0
        if control == "early_attachment" and role == "candidate":
            influence = 1.0 if source_time >= 32 else 0.0
        if control == "hand_sword_sliding" and role == "candidate" and source_time >= 48:
            influence = .90
        if control == "edit_leakage" and role == "candidate" and frame >= 76:
            influence = .80
        constraint = sword.constraints["3D05_HAND_LOCATION"]
        constraint.influence = influence
        constraint.keyframe_insert(data_path="influence", frame=frame)
        attached = influence > 0.0
        sword.location = attached_base if attached else supported
        if control == "attachment_teleportation" and role == "candidate" and not attached:
            sword.location = supported+Vector((.12, 0, 0))
        sword.keyframe_insert(data_path="location", frame=frame)
        sword.keyframe_insert(data_path="rotation_quaternion", frame=frame)
    for curve in mf.action_channels(action):
        for key in curve.keyframe_points:
            key.interpolation = "CONSTANT" if "influence" in curve.data_path else "LINEAR"
    return action


def build(mf, out, config, profile, role="candidate", control=None):
    if config.get("experiment_id") != "3D-05" or role not in {"baseline", "candidate"}:
        raise ValueError("Unsupported 3D-05 build request")
    if control is not None and control not in CONTROLS:
        raise ValueError("Unknown 3D-05 control")
    scene = bpy.context.scene
    armature = bpy.data.objects.get("character_01_armature")
    mesh = bpy.data.objects.get("character_01_mesh")
    idle = bpy.data.actions.get("character_action_idle")
    if not armature or not mesh or not idle:
        raise ValueError("Accepted 3D-03.1 character is missing")
    if scene.render.fps != 24 or scene.render.fps_base != 1:
        raise ValueError("3D-05 requires 24 fps")
    mf.assign_character_action(armature, idle)
    _set_time(1)
    initial = {bone.name: bone.matrix.copy() for bone in armature.pose.bones}
    supported_world = Vector(config["sword"]["supported_grip_world_m"])
    held_world = Vector(config["sword"]["held_grip_world_m"])
    if control == "penetration":
        held_world = Vector((-0.05, 0.02, 1.05))
    hand_surface_offset_world = Vector(config["sword"]["hand_surface_offset_world_m"])
    hand_surface_offset_local = armature.matrix_world.inverted().to_3x3()@hand_surface_offset_world
    # The arm solver targets the hand tail/palm contact point.  The sword root
    # remains one frozen surface offset away on the opposite side of the palm.
    supported = armature.matrix_world.inverted()@supported_world+hand_surface_offset_local
    held = armature.matrix_world.inverted()@held_world+hand_surface_offset_local
    # Validate both endpoints before creating any persistent action.
    shoulder = initial["RightArm"].translation
    _arm_matrices(mf, armature, initial, supported, (supported-shoulder).normalized())
    _arm_matrices(mf, armature, initial, held, (held-shoulder).normalized())
    baseline = _create_character_action(mf, armature, "baseline", initial, supported, held, None)
    candidate = _create_character_action(mf, armature, "candidate", initial, supported, held, control)
    _setup_support(mf, config)
    sword, imported = _create_sword(mf, config)
    location_constraint = sword.constraints.new("COPY_LOCATION")
    location_constraint.name = "3D05_HAND_LOCATION"
    location_constraint.target = armature
    location_constraint.subtarget = "RightHand"
    location_constraint.head_tail = 1.0
    location_constraint.target_space = "WORLD"
    location_constraint.owner_space = "WORLD"
    location_constraint.use_offset = True
    location_constraint.influence = 0
    sword.rotation_mode = "QUATERNION"
    sword_baseline = _create_sword_action(mf, sword, armature, "baseline", None)
    sword_candidate = _create_sword_action(mf, sword, armature, "candidate", control)
    _setup_cameras(mf, config)
    scene.frame_start = 1
    scene.frame_end = 96
    scene["mf_experiment_id"] = "3D-05"
    scene["mf_interaction_revision"] = "shift_interaction_timing_v1"
    scene["mf_interaction_role"] = role
    scene["mf_interaction_control"] = control or "none"
    scene["mf_character_root_matrix_json"] = json.dumps([list(row) for row in bpy.data.objects["character_01"].matrix_world])
    select_role(mf, role)
    _set_time(1)
    mf.apply_profile(profile, 305)
    mf.write_json(out/"interaction-build.json", {
        "schema_version": "1.0", "experiment_id": "3D-05", "role": role,
        "control": control, "character_actions": [baseline.name, candidate.name],
        "sword_actions": [sword_baseline.name, sword_candidate.name],
        "imported_sword_objects": [obj.name for obj in imported], "provider_calls": 0,
    })


def select_role(mf, role):
    if role not in {"baseline", "candidate"}:
        raise ValueError("Unknown interaction role")
    armature = bpy.data.objects["character_01_armature"]
    sword = bpy.data.objects["sword_01"]
    mf.assign_character_action(armature, bpy.data.actions[f"character_action_pickup_3d05_{role}_96"])
    mf.assign_character_action(sword, bpy.data.actions[f"sword_action_pickup_3d05_{role}_96"])
    bpy.context.scene["mf_interaction_role"] = role
    armature["mf_active_action"] = f"pickup_3d05_{role}"


def checkpoint(mf, out, role, frame):
    select_role(mf, role)
    _set_time(float(frame))
    sword = bpy.data.objects["sword_01"]
    hand = bpy.data.objects["character_01_armature"].pose.bones["RightHand"]
    source_time = _source_time(float(frame), role)
    state = _state(source_time)
    payload = {
        "schema_version": "1.0", "role": role, "frame": float(frame), "state": state,
        "owner": _owner(state), "attachment_influence": sword.constraints["3D05_HAND_LOCATION"].influence,
        "sword_matrix_world": [list(row) for row in sword.matrix_world],
        "hand_anchor_world": list(bpy.data.objects["character_01_armature"].matrix_world@hand.tail),
        "hand_surface_offset_world": json.loads(sword["mf_hand_surface_offset_world_json"]),
        "hand_matrix_world": [list(row) for row in (bpy.data.objects["character_01_armature"].matrix_world@hand.matrix)],
        "character_action": bpy.data.objects["character_01_armature"].animation_data.action.name,
        "sword_action": sword.animation_data.action.name,
    }
    mf.write_json(out/"checkpoint.json", payload)
    return payload


def _character_points(mf, mesh):
    return mf._evaluated_character_points(mesh)


def _sword_points(sword):
    deps = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.get("mf_entity") != "sword_01":
            continue
        evaluated = obj.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        try:
            points.extend(evaluated.matrix_world@vertex.co for vertex in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    if not points:
        raise ValueError("3D-05 sword has no evaluated vertices")
    return points


def _rms_delta(left, right):
    distances = [(a-b).length for a, b in zip(left, right)]
    return max(distances), math.sqrt(sum(value*value for value in distances)/len(distances))


def _quat_angle_degrees(left, right):
    return math.degrees(left.rotation_difference(right).angle)


def _sample(mf, role, frame, with_geometry=True):
    select_role(mf, role)
    _set_time(frame)
    armature = bpy.data.objects["character_01_armature"]
    mesh = bpy.data.objects["character_01_mesh"]
    sword = bpy.data.objects["sword_01"]
    hand_pose = armature.pose.bones["RightHand"]
    hand_matrix = armature.matrix_world@hand_pose.matrix
    hand_matrix.translation = armature.matrix_world@hand_pose.tail
    sword_matrix = sword.matrix_world.copy()
    expected_hand_offset = Vector(json.loads(sword["mf_hand_surface_offset_world_json"]))
    supported_orientation = Quaternion(json.loads(sword["mf_supported_quaternion_json"]))
    source_time = _source_time(frame, role, scene_control())
    state = _state(source_time)
    result = {
        "frame": frame, "source_time": source_time, "state": state, "owner": _owner(state),
        "attachment_influence": sword.constraints["3D05_HAND_LOCATION"].influence,
        "grip_translation_error_m": ((hand_matrix.translation-sword_matrix.translation)-expected_hand_offset).length,
        "grip_orientation_error_degrees": _quat_angle_degrees(sword_matrix.to_quaternion(), supported_orientation),
        "sword_translation": list(sword_matrix.translation),
        "sword_quaternion": list(sword_matrix.to_quaternion()),
        "character_root_translation": list(bpy.data.objects["character_01"].matrix_world.translation),
    }
    if with_geometry:
        result["character_points"] = _character_points(mf, mesh)
        result["sword_points"] = _sword_points(sword)
    return result


def scene_control():
    value = bpy.context.scene.get("mf_interaction_control", "none")
    return None if value == "none" else value


def _times(campaign):
    sampling = campaign["sampling"]
    values = {1+i*.5 for i in range(191)}
    for low, high in sampling["dense_windows"]:
        values.update(low+i*.125 for i in range(round((high-low)/.125)+1))
    return sorted(values)


def _nearest_body_clearance(mesh, character, sword, grip, handle_radius):
    from mathutils.bvhtree import BVHTree
    group = mesh.vertex_groups.get("RightHand")
    if group is None:
        raise ValueError("3D-05 character has no RightHand vertex group")
    hand = set()
    for index in range(len(mesh.data.vertices)):
        try:
            group.weight(index)
            hand.add(index)
        except RuntimeError:
            pass
    faces = [tuple(poly.vertices) for poly in mesh.data.polygons if not any(index in hand for index in poly.vertices)]
    tree = BVHTree.FromPolygons(character, faces, all_triangles=False)
    eligible = [point for point in sword if (point-grip).length > handle_radius]
    if not eligible:
        return math.inf
    distances = [nearest[3] for point in eligible if (nearest := tree.find_nearest(point)) is not None]
    return min(distances) if distances else math.inf


def evidence(mf, out, campaign, profile, render_frames=False):
    scene = bpy.context.scene
    if scene.get("mf_experiment_id") != "3D-05":
        raise ValueError("3D-05 evidence targets are missing")
    times = _times(campaign)
    sampled = {role: {frame: _sample(mf, role, frame) for frame in times}
               for role in ("baseline", "candidate")}
    character_mesh = bpy.data.objects["character_01_mesh"]
    handle_radius = bpy.data.objects["sword_01"]["mf_handle_contact_radius_m"]
    support = bpy.data.objects["sword_support_01"]
    support_top = max((support.matrix_world@Vector(corner)).z for corner in support.bound_box)
    rows = []
    root_initial = Vector(sampled["baseline"][1]["character_root_translation"])
    for frame in times:
        base = sampled["baseline"][frame]
        candidate = sampled["candidate"][frame]
        maximum, rms = _rms_delta(base["character_points"], candidate["character_points"])
        sword_translation_delta = (Vector(base["sword_translation"])-Vector(candidate["sword_translation"])).length
        sword_orientation_delta = _quat_angle_degrees(Quaternion(base["sword_quaternion"]), Quaternion(candidate["sword_quaternion"]))
        grip = Vector(candidate["sword_translation"])
        rows.append({
            "frame": frame, "baseline_state": base["state"], "candidate_state": candidate["state"],
            "baseline_owner": base["owner"], "candidate_owner": candidate["owner"],
            "candidate_attachment_influence": candidate["attachment_influence"],
            "candidate_grip_translation_error_m": candidate["grip_translation_error_m"],
            "candidate_grip_orientation_error_degrees": candidate["grip_orientation_error_degrees"],
            "candidate_sword_min_z_m": min(point.z for point in candidate["sword_points"]),
            "candidate_character_min_z_m": min(point.z for point in candidate["character_points"]),
            "candidate_sword_support_separation_m": min(point.z for point in candidate["sword_points"])-support_top,
            "candidate_non_handle_body_clearance_m": _nearest_body_clearance(
                character_mesh, candidate["character_points"], candidate["sword_points"], grip, handle_radius),
            "candidate_sword_bounds_m": {
                "min": [min(point[axis] for point in candidate["sword_points"]) for axis in range(3)],
                "max": [max(point[axis] for point in candidate["sword_points"]) for axis in range(3)],
            },
            "candidate_character_root_translation_m": (Vector(candidate["character_root_translation"])-root_initial).length,
            "character_max_vertex_delta_m": maximum, "character_rms_vertex_delta_m": rms,
            "sword_translation_delta_m": sword_translation_delta,
            "sword_orientation_delta_degrees": sword_orientation_delta,
        })
    # Physical half-frame movement is measured independently of dense-window spacing.
    half_steps = []
    for role in ("baseline", "candidate"):
        previous = _sample(mf, role, 1)
        for index in range(1, 191):
            frame = 1+index*.5
            current = sampled[role].get(frame) or _sample(mf, role, frame)
            maximum, rms = _rms_delta(previous["character_points"], current["character_points"])
            half_steps.append({"role": role, "frame": frame, "character_max_m": maximum,
                               "character_rms_m": rms,
                               "sword_translation_m": (Vector(previous["sword_translation"])-Vector(current["sword_translation"])).length})
            previous = current
    discontinuities = {}
    for role, transition in (("baseline", 40.0), ("candidate", 36.0)):
        before = _sample(mf, role, transition-.125, False)
        at = _sample(mf, role, transition, False)
        after = _sample(mf, role, transition+.125, False)
        position_second = (Vector(after["sword_translation"])-2*Vector(at["sword_translation"])+Vector(before["sword_translation"])).length
        orientation_second = abs(_quat_angle_degrees(Quaternion(before["sword_quaternion"]), Quaternion(at["sword_quaternion"]))-
                                 _quat_angle_degrees(Quaternion(at["sword_quaternion"]), Quaternion(after["sword_quaternion"])))
        discontinuities[role] = {"frame": transition, "position_second_difference_m": position_second,
                                 "orientation_second_difference_degrees": orientation_second}
    boundaries = {}
    for frame in (28.0, 76.0):
        h = .125
        base_minus = _sample(mf, "baseline", frame-h)
        base_plus = _sample(mf, "baseline", frame+h)
        cand_minus = _sample(mf, "candidate", frame-h)
        cand_plus = _sample(mf, "candidate", frame+h)
        base_velocity = [(right-left)*(24/(2*h)) for left, right in zip(base_minus["character_points"], base_plus["character_points"])]
        cand_velocity = [(right-left)*(24/(2*h)) for left, right in zip(cand_minus["character_points"], cand_plus["character_points"])]
        velocity_errors = [(right-left).length for left, right in zip(base_velocity, cand_velocity)]
        sword_base_velocity = (Vector(base_plus["sword_translation"])-Vector(base_minus["sword_translation"]))*(24/(2*h))
        sword_cand_velocity = (Vector(cand_plus["sword_translation"])-Vector(cand_minus["sword_translation"]))*(24/(2*h))
        boundaries[str(int(frame))] = {
            "character_rms_velocity_delta_m_per_s": math.sqrt(sum(value*value for value in velocity_errors)/len(velocity_errors)),
            "sword_velocity_delta_m_per_s": (sword_cand_velocity-sword_base_velocity).length,
        }
    raw = {
        "schema_version": "1.0", "experiment_id": "3D-05", "timeline": {"fps": 24, "frame_start": 1, "frame_end": 96},
        "control": scene_control(), "samples": rows, "half_frame_steps": half_steps,
        "attachment_discontinuities": discontinuities, "boundaries": boundaries,
        "timing": {"baseline_grasp_frame": 40.0, "candidate_grasp_frame": 36.0,
                   "baseline_lift_frame": 48.0, "candidate_lift_frame": 44.0,
                   "baseline_held_frame": 68.0, "candidate_held_frame": 64.0},
        "provider_calls": 0,
    }
    mf.write_json(out/"interaction-metrics.json", raw)
    if render_frames:
        render_review(mf, out, profile, campaign["director_gate"]["views"])
    return raw


def render_review(mf, out, profile, views):
    scene = bpy.context.scene
    mf.apply_profile(profile, 305)
    for role in ("baseline", "candidate"):
        select_role(mf, role)
        for view in views:
            scene.camera = bpy.data.objects[f"camera_3d05_{view}"]
            folder = out/"frames"/role/view
            folder.mkdir(parents=True, exist_ok=True)
            for frame in range(1, 97):
                scene.frame_set(frame)
                scene.render.filepath = str(folder/f"frame-{frame:04d}.png")
                bpy.ops.render.render(write_still=True)


def preview(mf, out, profile, frames):
    if not frames or any(type(frame) is not int or not 1 <= frame <= 96 for frame in frames):
        raise ValueError("3D-05 preview requires integer frames in the frozen timeline")
    scene = bpy.context.scene
    mf.apply_profile(profile, 305)
    select_role(mf, "candidate")
    artifacts = []
    views = sorted((obj["mf_view"] for obj in bpy.data.objects if obj.type == "CAMERA" and "mf_view" in obj),
                   key=lambda value: (value != "primary", value))
    for view in views:
        scene.camera = bpy.data.objects[f"camera_3d05_{view}"]
        for frame in frames:
            scene.frame_set(frame)
            relative = f"preview/{view}/frame-{frame:04d}.png"
            path = out/relative
            path.parent.mkdir(parents=True, exist_ok=True)
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            artifacts.append(relative)
    return artifacts
