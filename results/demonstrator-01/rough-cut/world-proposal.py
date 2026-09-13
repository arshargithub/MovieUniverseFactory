import os
import json
import time
import copy
import hashlib
import importlib

import bpy
from mathutils import Vector, Quaternion

ROOT = "/Users/adisharma/projects/MovieUniverseFactory"
RUN_ROOT = os.path.join(ROOT, "runs", "demonstrator-01")
SOURCE_BLEND = os.path.join(RUN_ROOT, "cut-motion", "scene.blend")
MOTION_JSON = os.path.join(RUN_ROOT, "cut-motion", "motion.json")
FINAL_BLEND = os.path.join(RUN_ROOT, "cut-world", "scene.blend")
RECEIPT = os.path.join(ROOT, "results", "demonstrator-01", "rough-cut", "scene-receipt.json")
SHOT_RANGES = {
    "shot1": (0, 144),
    "shot2": (144, 312),
    "shot3": (312, 432),
    "shot4": (432, 576),
}


def _real(path):
    return os.path.realpath(os.path.abspath(os.fspath(path)))


def _bounded(path):
    path = _real(path)
    if os.path.commonpath((path, _real(RUN_ROOT))) != _real(RUN_ROOT):
        raise ValueError("output path is outside the demonstrator run root")
    return path


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _open_blend(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)


def _collection(scene, name):
    old = bpy.data.collections.get(name)
    if old:
        for obj in list(old.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old)
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    return col


def _own(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def _material(helper, name, rgb, roughness=0.8):
    return helper._material(name, rgb, roughness)


def _assign(obj, mat):
    if not obj.data or not hasattr(obj.data, "materials"):
        return
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def _cube(col, name, location, dimensions, mat=None, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = _own(bpy.context.object, col)
    obj.name = name
    obj.dimensions = dimensions
    if mat:
        _assign(obj, mat)
    return obj


def _cylinder(col, name, location, radius, depth, mat=None, vertices=10):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = _own(bpy.context.object, col)
    obj.name = name
    if mat:
        _assign(obj, mat)
    return obj


def _cone(col, name, location, radius1, radius2, depth, mat=None, vertices=10):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=location
    )
    obj = _own(bpy.context.object, col)
    obj.name = name
    if mat:
        _assign(obj, mat)
    return obj


def _plane(col, name, location, size, mat=None):
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=location)
    obj = _own(bpy.context.object, col)
    obj.name = name
    obj.dimensions = size
    if mat:
        _assign(obj, mat)
    return obj


def _road_material():
    name = "Courier_WorldPosition_Road"
    old = bpy.data.materials.get(name)
    if old:
        bpy.data.materials.remove(old, do_unlink=True)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    geom = nodes.new("ShaderNodeNewGeometry")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    absolute = nodes.new("ShaderNodeMath")
    absolute.operation = "ABSOLUTE"
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.075
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = 0.7
    edge_scale = nodes.new("ShaderNodeMath")
    edge_scale.operation = "MULTIPLY"
    edge_scale.inputs[1].default_value = 0.5
    edge_bias = nodes.new("ShaderNodeMath")
    edge_bias.operation = "SUBTRACT"
    edge_bias.inputs[1].default_value = 0.25
    edge_add = nodes.new("ShaderNodeMath")
    edge_add.operation = "ADD"
    mask = nodes.new("ShaderNodeMath")
    mask.operation = "LESS_THAN"
    mask.inputs[1].default_value = 1.9

    green = nodes.new("ShaderNodeMixRGB")
    green.blend_type = "MIX"
    green.inputs[1].default_value = (0.035, 0.12, 0.025, 1.0)
    green.inputs[2].default_value = (0.12, 0.30, 0.055, 1.0)
    dirt = nodes.new("ShaderNodeMixRGB")
    dirt.blend_type = "MIX"
    dirt.inputs[1].default_value = (0.19, 0.095, 0.035, 1.0)
    dirt.inputs[2].default_value = (0.43, 0.245, 0.09, 1.0)
    final = nodes.new("ShaderNodeMixRGB")
    final.blend_type = "MIX"

    links.new(geom.outputs["Position"], sep.inputs[0])
    links.new(sep.outputs["X"], absolute.inputs[0])
    links.new(geom.outputs["Position"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], edge_scale.inputs[0])
    links.new(edge_scale.outputs[0], edge_bias.inputs[0])
    links.new(absolute.outputs[0], edge_add.inputs[0])
    links.new(edge_bias.outputs[0], edge_add.inputs[1])
    links.new(edge_add.outputs[0], mask.inputs[0])
    links.new(noise.outputs["Fac"], green.inputs[0])
    links.new(noise.outputs["Fac"], dirt.inputs[0])
    links.new(mask.outputs[0], final.inputs[0])
    links.new(green.outputs[0], final.inputs[1])
    links.new(dirt.outputs[0], final.inputs[2])
    links.new(final.outputs[0], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.92
    links.new(bsdf.outputs[0], out.inputs[0])
    return mat


def _configure_render(scene):
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        pass
    try:
        scene.eevee.taa_render_samples = 32
    except Exception:
        try:
            scene.eevee.render_samples = 32
        except Exception:
            pass
    try:
        scene.render.use_motion_blur = False
    except Exception:
        pass
    try:
        scene.eevee.use_motion_blur = False
    except Exception:
        pass
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass


def _environment(scene, col):
    world = scene.world or bpy.data.worlds.new("Courier_Daylight_World")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.16, 0.34, 0.62, 1.0)
    bg.inputs["Strength"].default_value = 0.65
    links.new(bg.outputs[0], out.inputs[0])

    data = bpy.data.lights.new("Courier_WarmSun", "SUN")
    data.energy = 3.0
    data.color = (1.0, 0.72, 0.47)
    data.angle = 0.08
    sun = bpy.data.objects.new("Courier_WarmSun", data)
    col.objects.link(sun)
    sun.rotation_euler = (0.72, -0.42, -0.78)
    return sun


def _make_landscape(scene, col, helper):
    grass = _material(helper, "Courier_Grass", (0.055, 0.22, 0.035), 0.95)
    dark_grass = _material(helper, "Courier_Hedge", (0.025, 0.12, 0.02), 0.98)
    dirt = _material(helper, "Courier_Soil", (0.30, 0.15, 0.055), 0.96)
    wood = _material(helper, "Courier_Wood", (0.20, 0.10, 0.045), 0.9)
    leaves = _material(helper, "Courier_Leaves", (0.035, 0.18, 0.025), 0.98)
    barn_red = _material(helper, "Courier_BarnRed", (0.30, 0.055, 0.025), 0.85)
    stone = _material(helper, "Courier_TowerStone", (0.29, 0.28, 0.23), 0.95)
    roof = _material(helper, "Courier_Roof", (0.11, 0.075, 0.045), 0.9)
    orange = _material(helper, "Courier_FlagOrange", (0.95, 0.20, 0.015), 0.65)

    meadow = _plane(col, "Courier_MeadowGround", (0, -155, -0.10), (500, 700), grass)
    strip = _plane(col, "Courier_DirtStrip", (0, -155, -0.045), (3.8, 410), dirt)

    roads = [o for o in scene.objects if o.type == "MESH" and "road" in o.name.lower()]
    if not roads:
        raise RuntimeError("reviewed diagnostic road object was not found")
    road = max(roads, key=lambda o: abs(o.dimensions.x * o.dimensions.y))
    _assign(road, _road_material())

    hills = []
    for i, (x, y, z, sx, sy, sz) in enumerate((
        (-115, -90, -5, 90, 65, 18), (125, -170, -7, 110, 78, 22),
        (-145, -310, -8, 105, 70, 24), (150, -355, -10, 125, 82, 27),
        (0, -440, -13, 170, 70, 31),
    )):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=(x, y, z))
        h = _own(bpy.context.object, col)
        h.name = "Courier_RollingHill_%02d" % i
        h.scale = (sx, sy, sz)
        _assign(h, grass)
        hills.append(h)

    hedges = []
    for i, (x, y, sy) in enumerate(((-25, -70, 105), (27, -205, 120), (-29, -300, 90))):
        hedges.append(_cube(col, "Courier_Hedge_%02d" % i, (x, y, 1.2), (4.2, sy, 2.4), dark_grass))

    fences = []
    for side in (-1, 1):
        x = side * 12.0
        for j, y in enumerate((-40, -130, -220, -300)):
            fences.append(_cube(col, "Courier_FenceRail_%s_%02d" % ("L" if side < 0 else "R", j),
                                (x, y, 1.0), (0.15, 72, 0.13), wood))
        for j, y in enumerate(range(20, -351, -37)):
            fences.append(_cube(col, "Courier_FencePost_%s_%02d" % ("L" if side < 0 else "R", j),
                                (x, y, 0.85), (0.24, 0.24, 1.7), wood))

    tree_positions = [
        (-38, 20), (42, -5), (-48, -55), (55, -82), (-64, -120), (44, -145),
        (-52, -185), (66, -215), (-41, -250), (52, -275), (-58, -315), (45, -345),
        (-88, -35), (94, -110), (-100, -205), (105, -285), (-76, -365), (84, -390),
    ]
    trunk0 = _cylinder(col, "Courier_TreeTrunk_00", (tree_positions[0][0], tree_positions[0][1], 2.2),
                       0.42, 4.4, wood, 8)
    crown0 = _cone(col, "Courier_TreeCrown_00", (tree_positions[0][0], tree_positions[0][1], 6.0),
                   3.3, 0.5, 7.0, leaves, 9)
    trees = [trunk0, crown0]
    for i, (x, y) in enumerate(tree_positions[1:], 1):
        scale = 0.80 + (i % 5) * 0.08
        for proto, kind, z in ((trunk0, "Trunk", 2.2 * scale), (crown0, "Crown", 6.0 * scale)):
            obj = proto.copy()
            obj.data = proto.data
            col.objects.link(obj)
            obj.name = "Courier_Tree%s_%02d" % (kind, i)
            obj.location = (x, y, z)
            obj.scale = (scale, scale, scale)
            trees.append(obj)

    barn = [
        _cube(col, "Courier_Barn", (-54, -235, 4.0), (16, 23, 8), barn_red),
        _cube(col, "Courier_BarnRoof", (-54, -235, 9.0), (18, 25, 2.2), roof, (0, 0.0, 0.0)),
        _cube(col, "Courier_BarnDoor", (-45.9, -235, 3.0), (0.2, 5.0, 6.0), wood),
    ]

    tower = []
    for i, (dx, dy) in enumerate(((-1.8, -1.8), (1.8, -1.8), (-1.8, 1.8), (1.8, 1.8))):
        tower.append(_cube(col, "Courier_TowerLeg_%02d" % i, (8 + dx, -320 + dy, 6.5),
                           (0.65, 0.65, 13), stone))
    tower.extend([
        _cube(col, "Courier_TowerPlatform", (8, -320, 13.0), (6.0, 6.0, 0.7), stone),
        _cube(col, "Courier_TowerCabin", (8, -320, 15.0), (4.7, 4.7, 3.4), wood),
        _cone(col, "Courier_TowerRoof", (8, -320, 17.3), 4.2, 0.0, 2.5, roof, 4),
        _cylinder(col, "Courier_FlagPole", (8, -320, 19.2), 0.10, 6.0, wood, 10),
    ])

    mesh = bpy.data.meshes.new("Courier_SignalFlagMesh")
    mesh.from_pydata([(0, 0, 0), (4.3, 0, -0.35), (3.8, 0, -2.0), (0, 0, -1.55)], [], [(0, 1, 2, 3)])
    mesh.update()
    flag = bpy.data.objects.new("Courier_SignalFlag", mesh)
    col.objects.link(flag)
    flag.location = (8, -320, 21.0)
    _assign(flag, orange)
    flag.rotation_mode = "XYZ"
    for frame, angle in ((0, -0.10), (383, -0.10), (408, 0.13), (432, -0.08),
                         (456, 0.15), (480, -0.12), (504, 0.11), (528, -0.07),
                         (552, 0.14), (575, -0.09)):
        flag.rotation_euler.z = angle
        flag.keyframe_insert("rotation_euler", frame=frame, index=2)
    if flag.animation_data and flag.animation_data.action:
        for fc in flag.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"

    return {
        "meadow": [meadow.name], "dirt_strip": [strip.name], "diagnostic_road": [road.name],
        "rolling_hills": [o.name for o in hills], "hedgerows": [o.name for o in hedges],
        "fences": [o.name for o in fences], "tree_instances": [o.name for o in trees],
        "farm": [o.name for o in barn], "watchtower": [o.name for o in tower],
        "signal_flag": [flag.name],
    }


def _load_events():
    with open(MOTION_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    events = data.get("contact_events") if isinstance(data, dict) else data
    if not isinstance(events, list):
        raise ValueError("motion.json contact_events must be a list")
    result = [copy.deepcopy(e) for e in events]
    cycle_zero = [e for e in events if int(e.get("cycle", 0)) == 0]
    for cycle in range(-4, 0):
        for source in cycle_zero:
            event = copy.deepcopy(source)
            event["cycle"] = cycle
            event["time"] = float(event.get("time", 0.0)) + cycle / 2.2
            anchor = event.get("anchor")
            delta = 12.0 * cycle / 2.2
            if isinstance(anchor, dict) and "y" in anchor:
                anchor["y"] = float(anchor["y"]) - delta
            elif isinstance(anchor, list) and len(anchor) >= 2:
                anchor[1] = float(anchor[1]) - delta
            result.append(event)
    return result


def _horse_point(scene, horse, helper, mf, frame):
    helper._refresh(scene, mf, frame)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = horse.evaluated_get(depsgraph)
    bone = evaluated.pose.bones.get("torso.head")
    if bone is None:
        raise RuntimeError("required evaluated horse bone torso.head was not found")
    return evaluated.matrix_world @ bone.head + Vector((0.0, 0.0, 0.6))


def _camera_object(col, name, lens):
    data = bpy.data.cameras.new(name + "_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.1
    data.clip_end = 1200.0
    data.dof.use_dof = False
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    obj.rotation_mode = "QUATERNION"
    return obj


def _smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def _bake_cameras(scene, col, horse, helper, mf):
    cameras = {
        "shot1": _camera_object(col, "Courier_Shot1", 46.0),
        "shot2": _camera_object(col, "Courier_Shot2", 52.0),
        "shot3": _camera_object(col, "Courier_Shot3", 43.0),
        "shot4": _camera_object(col, "Courier_Shot4", 48.0),
    }
    previous = {key: None for key in cameras}
    positions = {key: {} for key in cameras}

    for shot, (start, end) in SHOT_RANGES.items():
        cam = cameras[shot]
        for frame in range(start, end):
            body = _horse_point(scene, horse, helper, mf, frame)
            if shot == "shot1":
                t = _smoothstep((frame - start) / max(1, end - start - 1))
                offset = Vector((11.5 - 3.8 * t, -15.5 + 4.0 * t, 10.5 - 5.0 * t))
                target = body + Vector((0, -1.8 + 1.2 * t, -0.15))
            elif shot == "shot2":
                t = (frame - start) / max(1, end - start - 1)
                offset = Vector((-10.5 + 1.2 * t, 3.0, 3.2 + 0.4 * t))
                target = body + Vector((0, -1.5, -0.25))
            elif shot == "shot3":
                t = (frame - start) / max(1, end - start - 1)
                offset = Vector((12.5, 11.0 - 2.0 * t, 7.0))
                target = body + Vector((0, -13.0 - 6.0 * t, 0.1))
            else:
                t = (frame - start) / max(1, end - start - 1)
                offset = Vector((-10.5 + 1.0 * t, 10.5, 5.2 + 0.7 * t))
                target = body + Vector((0, -8.0 - 3.0 * t, -0.1))

            location = body + offset
            quat = (target - location).to_track_quat("-Z", "Y")
            old = previous[shot]
            if old is not None and quat.dot(old) < 0.0:
                quat = Quaternion((-quat.w, -quat.x, -quat.y, -quat.z))
            previous[shot] = quat.copy()
            cam.location = location
            cam.rotation_quaternion = quat
            cam.keyframe_insert("location", frame=frame)
            cam.keyframe_insert("rotation_quaternion", frame=frame)
            if frame in (start, (start + end - 1) // 2, end - 1):
                positions[shot][str(frame)] = [round(v, 5) for v in location]

        if cam.animation_data and cam.animation_data.action:
            for fc in cam.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "LINEAR"

    for marker in list(scene.timeline_markers):
        if marker.name.startswith("Courier_"):
            scene.timeline_markers.remove(marker)
    for shot, frame in (("shot1", 0), ("shot2", 144), ("shot3", 312), ("shot4", 432)):
        marker = scene.timeline_markers.new("Courier_" + shot, frame=frame)
        marker.camera = cameras[shot]
    scene.camera = cameras["shot1"]
    return cameras, positions


def _head_candidates(horse):
    candidates = []
    for bone in horse.pose.bones:
        name = bone.name.lower()
        if "head" in name and any(token in name for token in ("ctrl", "control", "ik", "target", "master")):
            candidates.append(bone.name)
    return sorted(candidates)


def _render_preflight(scene, cameras, out_dir, helper, mf):
    frames = {"shot1": 48, "shot2": 220, "shot3": 372, "shot4": 516}
    folder = os.path.join(out_dir, "preflight")
    os.makedirs(folder, exist_ok=True)
    records = []
    for shot, frame in frames.items():
        helper._refresh(scene, mf, frame)
        scene.camera = cameras[shot]
        path = os.path.join(folder, "%s_f%04d.png" % (shot, frame))
        scene.render.filepath = path
        started = time.monotonic()
        bpy.ops.render.render(write_still=True)
        elapsed = time.monotonic() - started
        helper._refresh(scene, mf, frame)
        records.append({
            "shot": shot, "frame": frame, "render_seconds": round(elapsed, 4),
            "image": os.path.relpath(path, out_dir),
            "camera_position": [round(v, 6) for v in cameras[shot].matrix_world.translation],
        })
    return records


def _world(mf, out_dir, helper):
    if _real(out_dir) != _real(os.path.dirname(FINAL_BLEND)):
        raise ValueError("demo_cut_world output_dir must be the fixed cut-world directory")
    if not os.path.isfile(MOTION_JSON):
        raise FileNotFoundError(MOTION_JSON)
    os.makedirs(out_dir, exist_ok=True)
    source_hash = _sha256(SOURCE_BLEND)
    motion_hash = _sha256(MOTION_JSON)
    _open_blend(SOURCE_BLEND)
    scene = bpy.context.scene
    scene.frame_start = 0
    scene.frame_end = 575
    scene.render.fps = 24
    scene.render.fps_base = 1.0
    _configure_render(scene)

    horse = bpy.data.objects.get("horse.rig")
    if horse is None or horse.type != "ARMATURE":
        raise RuntimeError("reviewed horse.rig armature was not found")
    if bpy.data.objects.get("meshhorse") is None:
        raise RuntimeError("reviewed meshhorse asset was not found")

    col = _collection(scene, "Courier_World")
    sun = _environment(scene, col)
    roles = _make_landscape(scene, col, helper)
    roles["daylight"] = [sun.name]

    fx = importlib.import_module(".sustained_fx", package=__package__)
    events = _load_events()
    fx.tail(scene, horse, helper, mf, 2.2, frames=577)
    fx.dust(scene, events, helper, frames=577)

    cameras, baked_positions = _bake_cameras(scene, col, horse, helper, mf)
    roles["cameras"] = [c.name for c in cameras.values()]
    roles["source_horse"] = ["horse.rig", "meshhorse"]
    roles["sustained_fx"] = ["tail", "dust"]

    preflight = _render_preflight(scene, cameras, out_dir, helper, mf)
    helper._refresh(scene, mf, 0)
    scene.camera = cameras["shot1"]
    scene.render.filepath = ""
    bpy.ops.wm.save_as_mainfile(filepath=FINAL_BLEND, check_existing=False)
    scene_hash = _sha256(FINAL_BLEND)

    receipt = {
        "film": "The Courier",
        "duration_seconds": 24,
        "fps": 24,
        "frame_range": [0, 576],
        "scene_path": FINAL_BLEND,
        "scene_sha256": scene_hash,
        "source_path": SOURCE_BLEND,
        "source_sha256": source_hash,
        "motion_sha256": motion_hash,
        "shot_ranges": {k: list(v) for k, v in SHOT_RANGES.items()},
        "camera_positions": baked_positions,
        "preflight": preflight,
        "asset_roles": roles,
        "head_reaction": {
            "performed": False,
            "reason": "No unreviewed pose controls were modified.",
            "eligible_head_control_candidates": _head_candidates(horse),
        },
    }
    _write_json(RECEIPT, receipt)
    return receipt


def _render(mf, out_dir, profile, helper):
    if not isinstance(profile, dict):
        raise ValueError("demo_cut_render profile must be an object")
    shot = profile.get("shot")
    if shot not in SHOT_RANGES:
        raise ValueError("profile shot must be shot1, shot2, shot3, or shot4")
    start = profile.get("start")
    end = profile.get("end")
    if isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int) or not isinstance(end, int):
        raise ValueError("profile start and end must be integer global frames")
    lower, upper = SHOT_RANGES[shot]
    if not (lower <= start < end <= upper):
        raise ValueError("profile frame bounds must be inside the selected fixed shot")
    if not os.path.isfile(RECEIPT):
        raise FileNotFoundError(RECEIPT)
    with open(RECEIPT, "r", encoding="utf-8") as f:
        receipt = json.load(f)
    expected = receipt.get("scene_sha256")
    if not isinstance(expected, str) or _sha256(FINAL_BLEND) != expected:
        raise RuntimeError("final scene SHA does not match the reviewed receipt")

    os.makedirs(out_dir, exist_ok=True)
    _open_blend(FINAL_BLEND)
    scene = bpy.context.scene
    _configure_render(scene)
    camera = bpy.data.objects.get("Courier_" + shot.capitalize())
    if camera is None or camera.type != "CAMERA":
        raise RuntimeError("baked camera for selected shot was not found")

    records = []
    for frame in range(start, end):
        helper._refresh(scene, mf, frame)
        scene.camera = camera
        png = os.path.join(out_dir, "frame_%04d.png" % frame)
        timing = os.path.join(out_dir, "frame_%04d.time.json" % frame)
        scene.render.filepath = png
        started = time.monotonic()
        bpy.ops.render.render(write_still=True)
        elapsed = time.monotonic() - started
        record = {
            "frame": frame,
            "shot": shot,
            "render_seconds": round(elapsed, 6),
            "png": os.path.basename(png),
            "camera": camera.name,
        }
        _write_json(timing, record)
        records.append(record)
    return {
        "mode": "demo_cut_render", "shot": shot, "start": start, "end": end,
        "frames_rendered": len(records), "output_dir": out_dir,
        "scene_sha256": expected,
    }


def run(mf, out, job, helper):
    if not isinstance(job, dict):
        raise ValueError("job must be an object")
    if set(job.keys()) - {"mode", "output_dir", "profile"}:
        raise ValueError("unsupported job keys")
    mode = job.get("mode")
    configured = _bounded(job.get("output_dir"))
    supplied = _bounded(out)
    if configured != supplied:
        raise ValueError("out and output_dir must resolve to the same path")
    profile = job.get("profile")
    if mode == "demo_cut_world":
        if profile not in ({}, None):
            raise ValueError("demo_cut_world profile must be empty")
        return _world(mf, supplied, helper)
    if mode == "demo_cut_render":
        return _render(mf, supplied, profile, helper)
    raise ValueError("unsupported mode")
