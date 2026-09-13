import bpy
import hashlib
import hmac
import math
import os
import stat
import time
from pathlib import Path
from mathutils import Vector

_ALLOWED = {"mode", "asset_path", "asset_sha256", "output_dir", "frame", "profile"}

def _finite(values, label):
    out = [float(v) for v in values]
    if not all(math.isfinite(v) for v in out):
        raise ValueError("non-finite " + label)
    return out

def _bounds(obj):
    pts = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    vals = [v for p in pts for v in p]
    _finite(vals, "bounds for " + obj.name)
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]

def _channel_count(mf, action):
    channels = mf.action_channels(action)
    if isinstance(channels, int):
        return channels
    try:
        return len(channels)
    except TypeError:
        return sum(1 for _ in channels)

def inspect_asset(mf, out, job):
    started = time.monotonic()
    if not isinstance(job, dict) or set(job) - _ALLOWED:
        raise ValueError("invalid job keys")
    required = {"mode", "asset_path", "asset_sha256", "output_dir"}
    if not required.issubset(job) or job["mode"] != "demo_asset_inspect":
        raise ValueError("invalid or incomplete job")
    asset = job["asset_path"]
    output_dir = job["output_dir"]
    expected = job["asset_sha256"]
    if not isinstance(asset, str) or not os.path.isabs(asset) or not asset.lower().endswith(".blend"):
        raise ValueError("asset_path must be an absolute .blend path")
    if not os.path.exists(asset) or not stat.S_ISREG(os.lstat(asset).st_mode):
        raise ValueError("asset_path is not a regular file")
    if not isinstance(output_dir, str) or not os.path.isabs(output_dir):
        raise ValueError("output_dir must be absolute")
    if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
        raise ValueError("invalid asset_sha256")
    root = Path(__file__).resolve().parents[4]
    admitted = {'.runtime/assets/demonstrator-01/Knight_0.blend': 'd7461ba21f3d5768e4f8a782ac4e5283eac73fdb991e44fddeb5cb487c045e0c', '.runtime/assets/demonstrator-01/horse.blend': 'b848037332fe62064989f250a94faa04c75e3fb21ae93f6a100f19079c1b21aa'}
    try:
        relative = str(Path(asset).resolve().relative_to(root))
        Path(output_dir).resolve().relative_to(root / "runs" / "demonstrator-01")
    except ValueError:
        raise ValueError("Path outside the fixed demonstrator boundary")
    if admitted.get(relative) != expected:
        raise ValueError("Asset is not one of the two hash-admitted diagnostic inputs")
    frame = job.get("frame")
    if frame is not None and (isinstance(frame, bool) or not isinstance(frame, int) or not 1 <= frame <= 300):
        raise ValueError("frame must be an integer from 1 to 300")
    digest = hashlib.sha256()
    with open(asset, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    if not hmac.compare_digest(digest.hexdigest(), expected):
        raise ValueError("asset_sha256 mismatch")
    os.makedirs(output_dir, exist_ok=True)
    load_warning = None
    try:
        bpy.ops.wm.open_mainfile(filepath=asset, load_ui=False, use_scripts=False)
    except RuntimeError as error:
        if "has an invalid" not in str(error) or "from" not in str(error) or os.path.realpath(bpy.data.filepath) != os.path.realpath(asset):
            raise
        load_warning = "Blender loaded the file but reported deletion of an invalid shape-key block; admission remains unqualified."
    scene = bpy.context.scene
    if frame is not None:
        scene.frame_set(frame)
    objects = list(bpy.data.objects)
    armature_objects = [o for o in objects if o.type == "ARMATURE"]
    actions = list(bpy.data.actions)
    bone_count = sum(len(a.bones) for a in bpy.data.armatures)
    mf.write_json(out / "load-check.json", {"objects":len(objects),"bones":bone_count,"actions":len(actions),"warning":load_warning})
    if len(objects) > 2000 or bone_count > 2000 or len(actions) > 100:
        raise ValueError("asset exceeds object, bone, or action cap")
    if not armature_objects:
        raise ValueError("asset has no armatures")
    widgets = {p.custom_shape for o in armature_objects for p in o.pose.bones if p.custom_shape}
    mesh_objects = [o for o in objects if o.type == "MESH"]
    renderable = [o for o in mesh_objects if scene.objects.get(o.name) is o and not o.hide_render and o not in widgets and o.name not in {"Plane", "Arrow", "Shield", "Sword"}]
    if not mesh_objects:
        raise ValueError("asset has no meshes")
    if not renderable:
        raise ValueError("asset has no renderable meshes")
    meshes = []
    for obj in mesh_objects:
        low, high = _bounds(obj)
        meshes.append({"name": obj.name, "data": obj.data.name, "polygons": len(obj.data.polygons),
                       "renderable": obj in renderable, "custom_bone_widget": obj in widgets,
                       "bounds": {"min": low, "max": high}})
    lows, highs = zip(*[_bounds(o) for o in renderable])
    bound_min = [min(v[i] for v in lows) for i in range(3)]
    bound_max = [max(v[i] for v in highs) for i in range(3)]
    armatures = []
    for obj in armature_objects:
        bones = [{"name": b.name, "parent": b.parent.name if b.parent else None,
                  "head": _finite(b.head_local, "bone head"), "tail": _finite(b.tail_local, "bone tail"),
                  "connected": bool(b.use_connect)} for b in obj.data.bones]
        constraints = []
        for pose_bone in obj.pose.bones:
            for c in pose_bone.constraints:
                influence = _finite([c.influence], "constraint influence")[0]
                target = getattr(c, "target", None)
                constraints.append({"bone": pose_bone.name, "name": c.name, "type": c.type,
                                    "target": target.name if target else None,
                                    "subtarget": getattr(c, "subtarget", ""), "influence": influence})
        armatures.append({"object": obj.name, "data": obj.data.name, "bones": bones,
                          "pose_constraints": constraints})
    action_info = []
    for action in actions:
        action_range = _finite(action.frame_range, "action range")
        action_info.append({"name": action.name, "range": action_range,
                            "channel_count": _channel_count(mf, action)})
    nla = []
    for obj in objects:
        ad = obj.animation_data
        if not ad:
            continue
        tracks = []
        for track in ad.nla_tracks:
            strips = [{"name": s.name, "action": s.action.name if s.action else None,
                       "repeat": _finite([s.repeat], "NLA repeat")[0],
                       "scale": _finite([s.scale], "NLA scale")[0], "mute": bool(s.mute)} for s in track.strips]
            tracks.append({"name": track.name, "mute": bool(track.mute), "strips": strips})
        if tracks:
            nla.append({"object": obj.name, "tracks": tracks})
    images = []
    for image in bpy.data.images:
        packed = bool(image.packed_file) or bool(getattr(image, "packed_files", ()))
        path = image.filepath or ""
        resolved = bpy.path.abspath(path) if path else ""
        file_source = image.source in {"FILE", "SEQUENCE", "MOVIE", "TILED"}
        missing = bool(file_source and not packed and (not resolved or not os.path.isfile(resolved)))
        images.append({"name": image.name, "source": image.source, "filepath": path,
                       "packed": packed, "missing": missing})
    motion_probe = None
    if relative.endswith("horse.blend"):
        arm = bpy.data.objects["horse.rig"]
        if arm.animation_data:
            for track in arm.animation_data.nla_tracks: track.mute = True
        mf.assign_character_action(arm, bpy.data.actions["horse.gallop"])
        samples = []
        for tick in range(21):
            mf._set_scene_time(scene, tick / 2)
            samples.append({"frame": tick / 2, "bones": {n:list(arm.matrix_world @ arm.pose.bones[n].head) for n in ("root","torso","hips","chest","r_hoof.L","r_hoof.R","f_hoof.L","f_hoof.R")}})
        keys = bpy.data.objects["horse"].data.shape_keys
        motion_probe = {"gallop_samples":samples,"horse_shape_keys":None if keys is None else [k.name for k in keys.key_blocks],"autoexec_fail":bpy.app.autoexec_fail,"autoexec_fail_message":bpy.app.autoexec_fail_message}
        mf._set_scene_time(scene, 0)
    inventory = {"motion_probe":motion_probe,"load_warning":load_warning,"blender_version": bpy.app.version_string, "frame": scene.frame_current,
                 "fps": scene.render.fps / scene.render.fps_base, "meshes": meshes,
                 "render_bounds": {"min": bound_min, "max": bound_max}, "armatures": armatures,
                 "actions": action_info, "nla": nla, "images": images}
    for obj in objects:
        obj.hide_render = obj not in renderable
    for obj in [o for o in list(bpy.data.objects) if o.type == "LIGHT"]:
        bpy.data.objects.remove(obj, do_unlink=True)
    center = Vector([(bound_min[i] + bound_max[i]) * 0.5 for i in range(3)])
    radius = max((Vector(bound_max) - Vector(bound_min)).length * 0.5, 1.0e-5)
    ground_mesh = bpy.data.meshes.new("MF_DiagnosticGround")
    size = radius * 4.0
    z = bound_min[2] - radius * 0.01
    ground_mesh.from_pydata([(center.x-size, center.y-size, z), (center.x+size, center.y-size, z),
                            (center.x+size, center.y+size, z), (center.x-size, center.y+size, z)], [], [(0, 1, 2, 3)])
    ground = bpy.data.objects.new("MF_DiagnosticGround", ground_mesh)
    scene.collection.objects.link(ground)
    material = bpy.data.materials.new("MF_NeutralOverride")
    material.diffuse_color = (0.55, 0.55, 0.55, 1.0)
    bpy.context.view_layer.material_override = material
    world = bpy.data.worlds.new("MF_NeutralWorld")
    world.color = (0.05, 0.05, 0.05)
    scene.world = world
    camera_data = bpy.data.cameras.new("MF_DiagnosticCamera")
    camera = bpy.data.objects.new("MF_DiagnosticCamera", camera_data)
    scene.collection.objects.link(camera)
    direction = Vector((1.0, -1.0, 0.7)).normalized()
    distance = radius / math.sin(min(camera_data.angle_x, camera_data.angle_y) * 0.5) * 1.2
    camera.location = center + direction * distance
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.clip_start = max(radius * 1.0e-4, 1.0e-6)
    camera_data.clip_end = max(distance + radius * 5.0, camera_data.clip_start * 100.0)
    scene.camera = camera
    for location, energy, size_l in [((1.5, -2.0, 2.5), 1000.0, 4.0), ((-2.0, 1.0, 1.5), 600.0, 3.0)]:
        light_data = bpy.data.lights.new("MF_DiagnosticLight", "AREA")
        light_data.energy, light_data.shape, light_data.size = energy, "DISK", size_l * radius
        light = bpy.data.objects.new("MF_DiagnosticLight", light_data)
        scene.collection.objects.link(light)
        light.location = center + Vector(location).normalized() * radius * 3.0
        light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 8
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 640, 360, 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = os.path.join(output_dir, "preview.png")
    mf.write_json(out / "inventory.json", inventory)
    bpy.ops.render.render(write_still=True)
    inventory["wall_seconds"] = time.monotonic() - started
    mf.write_json(out / "inventory.json", inventory)
    return ["inventory.json", "preview.png"]
