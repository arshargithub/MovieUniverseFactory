from pathlib import Path
import bpy, hashlib, math, os, stat, time
from mathutils import Matrix, Vector

HORSE_PATH = Path("/Users/adisharma/projects/MovieUniverseFactory/.runtime/assets/demonstrator-01/horse.blend")
HORSE_SHA256 = "b848037332fe62064989f250a94faa04c75e3fb21ae93f6a100f19079c1b21aa"
RIDER_PATH = Path("/Users/adisharma/projects/MovieUniverseFactory/.runtime/assets/demonstrator-01/Knight_0.blend")
RIDER_SHA256 = "d7461ba21f3d5768e4f8a782ac4e5283eac73fdb991e44fddeb5cb487c045e0c"
ROOT_PATH = Path("/Users/adisharma/projects/MovieUniverseFactory")

MODE = "demo_riding_preview"
FRAMES = range(60)
RIDER_MESHES = {"Man", "Belt", "BreastPlate", "cuisse", "eyes-Left", "eyes-Right",
                "Gauntlets", "Helmet", "Shoes", "Shoulder-Plate", "teeth-bottom",
                "teeth-top", "tongue"}
HORSE_MESHES = {"horse", "bit", "bridle", "bridle.body", "reins", "saddle",
                "saddle.pad", "saddle.stirrup", "saddle.stirrup.strap", "Torus.002"}
CONTROLS = [f"{n}.{s}" for n in ("thigh_fk", "shin_fk", "foot_fk", "upper_arm_fk",
            "forearm_fk", "hand_fk") for s in ("L", "R")] + ["torso", "chest", "head"]


def _file(path, digest):
    p = Path(path).expanduser()
    if p.is_symlink() or not p.exists() or not stat.S_ISREG(p.lstat().st_mode):
        raise ValueError(f"asset is not a regular non-symlink file: {p}")
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    if h.hexdigest().lower() != digest.lower():
        raise ValueError(f"SHA256 mismatch: {p}")
    return p.resolve()


def _output(job):
    if set(job) != {"mode", "output_dir", "profile"} or job["mode"] not in {MODE, "demo_riding_recovery", "demo_riding_motion", "demo_riding_audit", "demo_free_probe", "demo_free_motion", "demo_hoof_response", "demo_free_verify"} or job["profile"] != {}:
        raise ValueError("job must contain exactly mode=demo_riding_preview, output_dir, profile={}")
    root = ROOT_PATH.expanduser().resolve()
    base = (root / "runs" / "demonstrator-01").resolve()
    out = Path(job["output_dir"]).expanduser()
    out = (root / out).resolve() if not out.is_absolute() else out.resolve()
    if os.path.commonpath((str(out), str(base))) != str(base):
        raise ValueError("output_dir must be under ROOT_PATH/runs/demonstrator-01")
    cur = out
    while cur != cur.parent and cur.exists():
        if cur.is_symlink():
            raise ValueError(f"symlink forbidden in output path: {cur}")
        cur = cur.parent
    out.mkdir(parents=True, exist_ok=True)
    return out


def _hide(o, value=True):
    o.hide_viewport = value
    o.hide_render = value


def _bbox(obj, deps):
    e = obj.evaluated_get(deps)
    pts = [e.matrix_world @ Vector(c) for c in e.bound_box]
    if not pts or not all(math.isfinite(v) for p in pts for v in p):
        raise FloatingPointError(f"non-finite bounds: {obj.name}")
    lo = Vector(tuple(min(p[i] for p in pts) for i in range(3)))
    hi = Vector(tuple(max(p[i] for p in pts) for i in range(3)))
    return lo, hi


def _pb_world(arm, pb, tail=False):
    return arm.matrix_world @ (pb.tail if tail else pb.head)


def _refresh(scene, mf, frame):
    mf._set_scene_time(scene, float(frame))
    bpy.context.view_layer.update()


def _rotate_at_head(arm, pb, target):
    inv3 = arm.matrix_world.inverted_safe().to_3x3()
    desired = inv3 @ (Vector(target) - _pb_world(arm, pb))
    current = pb.tail - pb.head
    if desired.length < 1e-8 or current.length < 1e-8:
        raise ValueError(f"degenerate aim for {pb.name}")
    q = current.normalized().rotation_difference(desired.normalized())
    h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ q.to_matrix().to_4x4() @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()


def _roll(pb, angle):
    h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(angle, 4, "X") @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()


def _material(name, color, rough=.65):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1.0)
    bs.inputs["Roughness"].default_value = rough
    return m


def _invalid_drivers(objects):
    bad = []
    for o in objects:
        ad = getattr(o, "animation_data", None)
        for fc in (() if not ad else ad.drivers):
            if not fc.is_valid:
                bad.append({"object": o.name, "data_path": fc.data_path, "array_index": fc.array_index})
    return bad


def _fk_test(scene, mf, arm, props):
    deps = bpy.context.evaluated_depsgraph_get()
    candidates = []
    for endpoint in (0.0, 1.0):
        oldp = [(pb, key, pb[key]) for pb, key in props]
        for pb, key in props:
            pb[key] = endpoint
        _refresh(scene, mf, 0)
        total, reactions = 0.0, {}
        for ctl, stem in (("thigh_fk.L", "DEF-thigh"), ("upper_arm_fk.L", "DEF-upper_arm")):
            defs = [p.name for p in arm.pose.bones if p.name.startswith(stem) and p.name.endswith(".L")]
            if not defs:
                raise RuntimeError(f"missing evaluated dependency bone: {stem}.L")
            before = arm.evaluated_get(deps).pose.bones[defs[0]].tail.copy()
            pb = arm.pose.bones[ctl]
            saved = pb.matrix_basis.copy()
            pb.matrix_basis = saved @ Matrix.Rotation(math.radians(2), 4, "X")
            bpy.context.view_layer.update()
            after = arm.evaluated_get(deps).pose.bones[defs[0]].tail.copy()
            pb.matrix_basis = saved
            bpy.context.view_layer.update()
            reactions[ctl] = (after - before).length
            total += reactions[ctl]
        for pb, key, value in oldp:
            pb[key] = value
        candidates.append({"endpoint": endpoint, "response": reactions, "total": total})
    best = max(candidates, key=lambda x: x["total"])
    if min(best["response"].values()) <= 1e-7:
        raise RuntimeError(f"FK controls do not drive evaluated DEF limbs: {candidates}")
    for pb, key in props:
        pb[key] = best["endpoint"]
    bpy.context.view_layer.update()
    return {"selected_endpoint": best["endpoint"], "tests": candidates}


def _environment(path):
    sand = _material("diagnostic sand", (.38, .25, .12))
    ridge = _material("diagnostic ridge", (.18, .16, .13))
    bpy.ops.mesh.primitive_cube_add(location=(0, -4, -.16), scale=(4, 16, .16))
    road = bpy.context.object; road.name = "diagnostic road"; road.data.materials.append(sand)
    for y in range(-15, 11, 4):
        for x in (-2.2, 2.2):
            bpy.ops.mesh.primitive_cube_add(location=(x, y, .08), scale=(.06, .45, .08))
            bpy.context.object.data.materials.append(ridge)
    for x, y, z, s in ((-8, -10, 1, 3), (8, -13, 1.4, 4), (10, 5, 1, 3)):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=s, location=(x, y, z))
        bpy.context.object.data.materials.append(ridge)
    bpy.ops.mesh.primitive_cube_add(location=(9, -15, 2.1), scale=(.8, .8, 2.1))
    bpy.context.object.name = "distant tower"; bpy.context.object.data.materials.append(ridge)
    target = bpy.data.objects.new("camera target", None); bpy.context.collection.objects.link(target)
    target.parent = path; target.location = (0, 2.5, 1.5)
    cams = []
    for name, loc in (("lateral", (8.5, 2.5, 3.0)), ("threequarter", (7.0, -4.5, 3.8))):
        data = bpy.data.cameras.new(name); cam = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(cam); cam.parent = path; cam.location = loc
        data.lens = 52; c = cam.constraints.new("TRACK_TO"); c.target = target
        c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"; cams.append(cam)
    return cams


def build_preview(mf, out, job):
    recovery = job.get("mode") == "demo_riding_recovery"
    free_repair = job.get("mode") in {"demo_free_probe","demo_free_motion"}
    pose_only = job.get("mode") == "demo_free_probe"
    out = _output(job)
    if Path(out).resolve() != Path(job["output_dir"]).expanduser().resolve():
        raise ValueError("out argument and job.output_dir disagree")
    horse_file = _file(HORSE_PATH, HORSE_SHA256)
    rider_file = _file(RIDER_PATH, RIDER_SHA256)
    if out == horse_file or out == rider_file:
        raise ValueError("output cannot overwrite an input source")
    try:
        bpy.ops.wm.open_mainfile(filepath=str(horse_file), load_ui=False, use_scripts=False)
    except RuntimeError as error:
        if "has an invalid" not in str(error) or "from" not in str(error) or Path(bpy.data.filepath).resolve() != horse_file:
            raise
    scene = bpy.context.scene; scene.frame_start = 0; scene.frame_end = 59; scene.render.fps = 24
    scene.frame_set(0); bpy.context.view_layer.update()
    source_objects = list(scene.objects)
    horse = bpy.data.objects.get("horse.rig"); saddle = bpy.data.objects.get("saddle")
    action = bpy.data.actions.get("horse.gallop")
    if not horse or horse.type != "ARMATURE" or not saddle or not action:
        raise RuntimeError("horse.rig, saddle, or horse.gallop is missing")
    if tuple(round(v, 4) for v in action.frame_range) != (0.0, 10.0):
        raise RuntimeError(f"unexpected horse.gallop range: {tuple(action.frame_range)}")
    mesh = bpy.data.objects.get("horse")
    keys = [] if not mesh or not mesh.data.shape_keys else [k.name for k in mesh.data.shape_keys.key_blocks]
    if keys != ["Basis", "corr.neck", "corr.chin", "corr.neck.2"]:
        raise RuntimeError(f"horse shape keys changed: {keys}")
    mf.write_json(out / "horse-hierarchy-before.json", {o.name:{"parent":o.parent.name if o.parent else None,"world":[list(row) for row in o.matrix_world],"constraints":[{"type":c.type,"target":getattr(getattr(c,"target",None),"name",None)} for c in o.constraints]} for o in source_objects if o.type=="ARMATURE" or o.name in HORSE_MESHES})
    horse_world=horse.matrix_world.copy()
    for constraint in horse.constraints:
        if constraint.type == "FOLLOW_PATH": constraint.mute=True
    bpy.context.view_layer.update();horse.matrix_world=horse_world;bpy.context.view_layer.update()
    path = bpy.data.objects.new("horse diagnostic path", None); scene.collection.objects.link(path)
    bpy.context.view_layer.update()
    original_root_worlds = {o:o.matrix_world.copy() for o in source_objects if o.parent is None}
    for o in source_objects:
        if o.parent is None:
            w = original_root_worlds[o]; o.parent = path; o.matrix_world = w; bpy.context.view_layer.update()
        if o.type == "MESH" and o.name not in HORSE_MESHES:
            _hide(o)
        if o.name == "Plane" or "widget" in o.name.lower() or "custom" in o.name.lower():
            _hide(o)
    ad = horse.animation_data_create()
    for tr in ad.nla_tracks: tr.mute = True
    ad.action = None
    tr = ad.nla_tracks.new(); tr.name = "diagnostic authored gait"
    strip = tr.strips.new("horse.gallop x7", 0, action); strip.repeat = 7.0
    strip.extrapolation = "NOTHING"; strip.blend_type = "REPLACE"
    path.location = (0, 0, 0); path.keyframe_insert("location", frame=0)
    path.location.y = -3.45 * 60 / 24; path.keyframe_insert("location", frame=60)
    for fc in mf.action_channels(path.animation_data.action):
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
    with bpy.data.libraries.load(str(rider_file), link=False) as (src, dst):
        dst.objects = list(src.objects)
    appended = [o for o in dst.objects if o]
    for o in appended:
        if o.name not in scene.objects: scene.collection.objects.link(o)
    rider = bpy.data.objects.get("rig")
    if not rider or rider.type != "ARMATURE": raise RuntimeError("rider dependency armature 'rig' missing")
    _refresh(scene, mf, 0)
    if recovery: _pose_probe(mf, out, "01-import", appended)
    original = {o: o.matrix_world.copy() for o in appended}
    original_rig_z = original[rider].translation.z
    common = Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(1.8 / 4.2, 4)
    def depth(obj):
        n = 0
        while obj.parent is not None:
            obj = obj.parent; n += 1
        return n
    if True:
        normalizer=bpy.data.objects.new("rider normalization",None);scene.collection.objects.link(normalizer)
        for o in appended:
            if o.parent is None:
                world=o.matrix_world.copy();o.parent=normalizer;o.matrix_world=world
        bpy.context.view_layer.update()
        normalizer.matrix_world=common
        bpy.context.view_layer.update()
    for o in sorted(appended, key=depth):
        if o.type == "MESH" and o.name not in RIDER_MESHES: _hide(o)
        if o.name == "metarig" or "widget" in o.name.lower() or "prop" in o.name.lower(): _hide(o)
        if o.animation_data:
            o.animation_data.action = None
            for track in o.animation_data.nla_tracks: track.mute=True
    bpy.context.view_layer.update()
    if recovery: _pose_probe(mf, out, "02-normalized", appended)
    missing = [n for n in CONTROLS if n not in rider.pose.bones]
    if missing: raise RuntimeError(f"missing required rider controls: {missing}")
    props = [(pb, k) for pb in rider.pose.bones for k in pb.keys() if "ikfk" in "".join(c for c in k.lower() if c.isalnum())]
    mf.write_json(out / "rig-properties.json", {pb.name: {k:str(pb[k]) for k in pb.keys()} for pb in rider.pose.bones if list(pb.keys())})
    if not props: raise RuntimeError("no IK/FK custom properties discovered; inspect rig-properties.json")
    fk_response = _fk_test(scene, mf, rider, props)
    neutral = {pb.name: pb.matrix_basis.copy() for pb in rider.pose.bones}
    repair=None
    if free_repair:
        repair=prepare_free_repair(mf,out,scene,horse,rider,saddle,path)
    snapshots, perframe, hoof_proxy = {}, [], {}
    deps = bpy.context.evaluated_depsgraph_get()
    hoof_names = [p.name for p in horse.pose.bones if "hoof" in p.name.lower() or "foot" in p.name.lower()]
    for f in (range(1) if recovery else FRAMES):
        _refresh(scene, mf, f)
        if repair:
            repair["tack"].update_tack(f,key=False)
            seat=repair["seat"].matrix_world();S=seat.translation.copy()
            seat_delta=seat @ repair["seat0"].inverted()
        else:
            lo, hi = _bbox(saddle, deps); S = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, hi.z))
        for name, mat in neutral.items(): rider.pose.bones[name].matrix_basis = mat.copy()
        bpy.context.view_layer.update()
        pelvis = (_pb_world(rider, rider.pose.bones["thigh_fk.L"]) + _pb_world(rider, rider.pose.bones["thigh_fk.R"])) * .5
        delta_local = rider.matrix_world.inverted_safe().to_3x3() @ (S + Vector((0, 0, .10)) - pelvis)
        torso = rider.pose.bones["torso"]; torso.matrix = Matrix.Translation(delta_local) @ torso.matrix
        bpy.context.view_layer.update()
        if repair:
            h=torso.head.copy();rotation=seat_delta.to_quaternion()
            torso.matrix=Matrix.Translation(h) @ rotation.to_matrix().to_4x4() @ Matrix.Translation(-h) @ torso.matrix
            bpy.context.view_layer.update()
        lean = math.radians(12 + 5 * math.sin(2 * math.pi * (f-1) / 10.0)) if repair else math.radians(10 + 3 * math.sin(2 * math.pi * f / 10.0))
        _roll(rider.pose.bones["chest"], -lean if repair else lean); _roll(rider.pose.bones["head"], lean*.6 if repair else -lean)
        if repair:
            head=rider.pose.bones["head"];head_world=rider.matrix_world@head.matrix
            head.matrix=rider.matrix_world.inverted() @ (Matrix.Translation(head_world.translation) @ repair["head_rotation"].to_matrix().to_4x4())
            bpy.context.view_layer.update()
        goals, endpoints = {}, {}
        for side, sx in (("L", .29), ("R", -.29)):
            knee = S + Vector((sx, -.27, -.21)); ankle = S + Vector((math.copysign(.31, sx), -.17, -.61))
            toe = S + Vector((math.copysign(.31, sx), -.36, -.64)); elbow = S + Vector((math.copysign(.35, sx), -.10, .45))
            hand = S + Vector((math.copysign(.18, sx), -.43, .38))
            if repair:
                orient=seat_delta.to_3x3()
                ankle=S+orient @ Vector((math.copysign(.31,sx),-.05,-.63))
                hand=S+orient @ Vector((math.copysign(.16,sx),-.28,.32))
                repair["helper"].aim_two_bone_fk(rider,f"thigh_fk.{side}",f"shin_fk.{side}",_pb_world(rider,rider.pose.bones[f"thigh_fk.{side}"]),ankle,orient@Vector((math.copysign(.6,sx),-1,0)),repair["lengths"][f"thigh_fk.{side}"],repair["lengths"][f"shin_fk.{side}"],deps)
                repair["helper"].aim_two_bone_fk(rider,f"upper_arm_fk.{side}",f"forearm_fk.{side}",_pb_world(rider,rider.pose.bones[f"upper_arm_fk.{side}"]),hand,orient@Vector((math.copysign(1,sx),.3,-.2)),repair["lengths"][f"upper_arm_fk.{side}"],repair["lengths"][f"forearm_fk.{side}"],deps)
                _rotate_at_head(rider,rider.pose.bones[f"foot_fk.{side}"],ankle+orient@Vector((0,-.22,-.03)))
                _rotate_at_head(rider,rider.pose.bones[f"hand_fk.{side}"],hand+orient@Vector((0,-.12,-.04)))
                for stem in ("f_index","f_middle","f_ring","f_pinky"):
                    for segment in (1,2,3):
                        finger=rider.pose.bones.get(f"{stem}.{segment:02d}.{side}")
                        if finger:
                            finger.rotation_mode="XYZ";finger.rotation_euler.x=.7 if segment==1 else .9
                bpy.context.view_layer.update()
                goals[f"ankle.{side}"]=list(ankle);endpoints[f"ankle.{side}"]=list(_pb_world(rider,rider.pose.bones[f"shin_fk.{side}"],True))
                goals[f"hand.{side}"]=list(hand);endpoints[f"hand.{side}"]=list(_pb_world(rider,rider.pose.bones[f"forearm_fk.{side}"],True))
                continue
            for bone, target, label in ((f"thigh_fk.{side}", knee, "knee"), (f"shin_fk.{side}", ankle, "ankle"),
                                        (f"foot_fk.{side}", toe, "toe"), (f"upper_arm_fk.{side}", elbow, "elbow"),
                                        (f"forearm_fk.{side}", hand, "hand")):
                _rotate_at_head(rider, rider.pose.bones[bone], target)
                goals[f"{label}.{side}"] = list(target)
                endpoints[f"{label}.{side}"] = list(_pb_world(rider, rider.pose.bones[bone], True))
        pelvis = (_pb_world(rider, rider.pose.bones["thigh_fk.L"]) + _pb_world(rider, rider.pose.bones["thigh_fk.R"])) * .5
        snapshots[f] = {p.name: p.matrix_basis.copy() for p in rider.pose.bones if p.name in CONTROLS or (repair and p.name.startswith(("f_index.","f_middle.","f_ring.","f_pinky.")))}
        errors = {k: (Vector(endpoints[k]) - Vector(v)).length for k, v in goals.items()}
        bounds = {}
        for o in [x for x in scene.objects if x.type == "MESH" and not x.hide_render]:
            a, b = _bbox(o, deps); bounds[o.name] = [list(a), list(b)]
        for n in hoof_names:
            hoof_proxy.setdefault(n, []).append(list(_pb_world(horse, horse.pose.bones[n])))
        if repair:
            repair["tack_samples"][f]={o.name:o.matrix_world.copy() for o in repair["tack"].roots}
        perframe.append({"frame": f, "saddle_top_center": list(S),
                         "pelvis_error": (pelvis - (S + Vector((0, 0, .10)))).length,
                         "endpoint_errors": errors, "finite_mesh_bounds": bounds, "floor_height": 0.0})
    if recovery:
        _pose_probe(mf, out, "03-seated", [o for o in scene.objects if o.type == "MESH" and o.name in RIDER_MESHES | HORSE_MESHES])
        mf.write_json(out / "pose-metrics.json", {"per_frame":perframe,"fk_response":fk_response})
        return ["01-import.png","02-normalized.png","03-seated.png","pose-metrics.json"]
    mf.write_json(out / "travel-check.json", {"observed_saddle_delta_y":perframe[-1]["saddle_top_center"][1]-perframe[0]["saddle_top_center"][1],"expected_path_delta_y":-(repair["speed"] if repair else 3.45)*59/24})
    if abs((perframe[-1]["saddle_top_center"][1]-perframe[0]["saddle_top_center"][1])-(-(repair["speed"] if repair else 3.45)*59/24)) > .5:
        raise RuntimeError("Forward travel differs from path by over 0.5 m; refuse animation render")
    if repair:
        for f,mats in repair["tack_samples"].items():
            scene.frame_set(f)
            for name,matrix in mats.items():
                obj=bpy.data.objects[name];obj.matrix_world=matrix;obj.rotation_mode="QUATERNION"
                for prop in ("location","rotation_quaternion","scale"): obj.keyframe_insert(prop,frame=f)
    rider_action = bpy.data.actions.new("diagnostic rider FK bake")
    mf.assign_character_action(rider, rider_action)
    for f in FRAMES:
        scene.frame_set(f)
        for name, mat in snapshots[f].items():
            pb = rider.pose.bones[name]; pb.matrix_basis = mat
            pb.keyframe_insert("location", frame=f); pb.keyframe_insert("scale", frame=f)
            prop = "rotation_quaternion" if pb.rotation_mode == "QUATERNION" else ("rotation_axis_angle" if pb.rotation_mode == "AXIS_ANGLE" else "rotation_euler")
            pb.keyframe_insert(prop, frame=f)
    if repair:
        build_repaired_reins(mf,repair,rider,horse,scene)
        if not pose_only: record_repair_checks(mf,out,repair,rider,horse,path,scene,perframe)
    brown = _material("diagnostic horse brown", (.20, .075, .025))
    armor = _material("diagnostic dark armor", (.035, .045, .055), .32)
    for n in HORSE_MESHES:
        o = bpy.data.objects.get(n)
        if o and o.type == "MESH": o.data.materials.clear(); o.data.materials.append(brown)
    for n in RIDER_MESHES:
        o = bpy.data.objects.get(n)
        if o and o.type == "MESH": o.data.materials.clear(); o.data.materials.append(armor)
    for o in scene.objects:
        for mod in o.modifiers:
            if mod.type == "SUBSURF": mod.levels = mod.render_levels
    for o in list(scene.objects):
        if o.type == "LIGHT": bpy.data.objects.remove(o, do_unlink=True)
    world = bpy.data.worlds.new("diagnostic daylight"); world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (.5,.6,.8,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = .6
    scene.world = world
    light = bpy.data.lights.new("diagnostic sun", "SUN"); light.energy = 3
    sun = bpy.data.objects.new("diagnostic sun", light); scene.collection.objects.link(sun)
    sun.rotation_euler = (.4,-.5,-.4)
    _refresh(scene, mf, 0)
    cams = _environment(path)
    deps=bpy.context.evaluated_depsgraph_get()
    actor_meshes=[o for o in scene.objects if o.type=="MESH" and o.name in RIDER_MESHES | HORSE_MESHES and len(o.data.polygons)>0]
    bounds=[_bbox(o,deps) for o in actor_meshes]
    lo=Vector(tuple(min(b[0][i] for b in bounds) for i in range(3)))
    hi=Vector(tuple(max(b[1][i] for b in bounds) for i in range(3)))
    center=(lo+hi)*.5
    target=bpy.data.objects["camera target"];target.location=path.matrix_world.inverted() @ center
    for cam,direction in zip(cams,(Vector((1,0,.23)),Vector((1,-1,.35)))):
        cam.location=target.location+direction.normalized()*max((hi-lo).length*1.5,7)
        cam.data.lens=48
    bpy.context.view_layer.update()
    scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 8; scene.cycles.use_denoising = True
    scene.render.resolution_x = 640; scene.render.resolution_y = 360; scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"; scene.render.use_file_extension = True
    scene.render.use_stamp = False; scene.render.use_stamp_note = True
    scene.render.stamp_note_text = "UNQUALIFIED DIAGNOSTIC PREVIEW — NOT PHYSICALLY CALIBRATED"
    scene.render.use_stamp_date = False; scene.render.use_stamp_time = False; scene.render.use_stamp_render_time = False
    invalid = _invalid_drivers(list(scene.objects))
    contact_fail = any(x["pelvis_error"] > .04 or max(x["endpoint_errors"].values(), default=0) > .12 for x in perframe)
    metrics = {"mode": MODE, "frames": [0, 59], "fps": 24,
               "source": {"horse_sha256": HORSE_SHA256, "rider_sha256": RIDER_SHA256,
                          "horse_shape_keys": keys, "rider_original_armature_translation_z": original_rig_z},
               "source_warnings": ["Exact validated horse source loaded; known invalid orphan ShapeKey warning may occur."],
               "motion_notice": ("Forward speed fitted to evaluated hoof samples; see hoof-calibration.json; residual slip remains independently reported." if repair else "Forward -Y translation is provisional 3.45 m/s and not physically calibrated."),
               "fk_response": fk_response, "invalid_drivers": invalid,
               "action_channels": len(mf.action_channels(rider_action)), "per_frame": perframe,
               "hoof_control_proxy_trajectories": hoof_proxy,
               "hoof_proxy_notice": "Control trajectories are proxies and explicitly are not sole-slip measurements.",
               "contact_checks_failed": contact_fail, "render_seconds": {}}
    scene.camera = cams[0]
    mf.write_json(out / "metrics.json", metrics)
    if not pose_only: bpy.ops.wm.save_as_mainfile(filepath=str(out / "scene.blend"), check_existing=False)
    finite = all(math.isfinite(x["pelvis_error"]) and all(math.isfinite(v) for v in x["endpoint_errors"].values()) for x in perframe)
    if not finite: raise FloatingPointError("non-finite diagnostic measurements; rendering refused")
    for cam in (cams if repair and not pose_only else cams[:1]):
        scene.camera = cam; d = out / "renders" / cam.name; d.mkdir(parents=True, exist_ok=True)
        metrics["render_seconds"][cam.name] = []
        for f in ((0,3,7) if pose_only else FRAMES):
            scene.frame_set(f); scene.render.filepath = str(d / f"{f:04d}.png")
            t = time.perf_counter(); bpy.ops.render.render(write_still=True)
            metrics["render_seconds"][cam.name].append(time.perf_counter() - t)
            mf.write_json(out / "metrics.json", metrics)
    mf.write_json(out / "metrics.json", metrics)
    return (["metrics.json", "renders"] if pose_only else ["scene.blend", "metrics.json", "renders"])


def _pose_probe(mf, out, label, objects):
    scene=bpy.context.scene; bpy.context.view_layer.update()
    meshes=[o for o in objects if o.type == "MESH" and o.name in RIDER_MESHES | HORSE_MESHES]
    deps=bpy.context.evaluated_depsgraph_get()
    bounds={o.name: [list(v) for v in _bbox(o,deps)] for o in meshes}
    mf.write_json(out/(label+".json"), {"bounds":bounds,"objects":{o.name:{"parent":o.parent.name if o.parent else None,"matrix_world":[list(row) for row in o.matrix_world],"constraints":[{"type":c.type,"target":getattr(getattr(c,"target",None),"name",None)} for c in o.constraints]} for o in objects}})
    lo=Vector(tuple(min(b[0][i] for b in bounds.values()) for i in range(3)));hi=Vector(tuple(max(b[1][i] for b in bounds.values()) for i in range(3)))
    center=(lo+hi)*.5; radius=max((hi-lo).length*.5,1)
    hidden={o:o.hide_render for o in scene.objects}
    for o in scene.objects: o.hide_render=o not in meshes
    cd=bpy.data.cameras.new(label);cam=bpy.data.objects.new(label,cd);scene.collection.objects.link(cam)
    cam.location=center+Vector((1,-1,.4)).normalized()*radius*3.4
    cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler();cd.lens=45;scene.camera=cam
    world=bpy.data.worlds.new(label);world.use_nodes=True;world.node_tree.nodes["Background"].inputs["Strength"].default_value=.8;scene.world=world
    ld=bpy.data.lights.new(label,"SUN");ld.energy=3;light=bpy.data.objects.new(label,ld);scene.collection.objects.link(light);light.rotation_euler=(.4,-.5,-.5)
    mat=_material("pose diagnostic grey",(.5,.5,.5));bpy.context.view_layer.material_override=mat
    scene.render.engine="CYCLES";scene.cycles.device="CPU";scene.cycles.samples=8;scene.cycles.use_denoising=True
    scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.resolution_percentage=100
    scene.render.use_stamp=False;scene.render.image_settings.file_format="PNG";scene.render.filepath=str(out/(label+".png"))
    bpy.ops.render.render(write_still=True)
    for o,value in hidden.items(): o.hide_render=value
    bpy.data.objects.remove(cam,do_unlink=True);bpy.data.objects.remove(light,do_unlink=True)
    bpy.context.view_layer.material_override=None


def audit_fixture(mf,out,job):
    _output(job); asset=_file(HORSE_PATH,HORSE_SHA256)
    try: bpy.ops.wm.open_mainfile(filepath=str(asset),load_ui=False,use_scripts=False)
    except RuntimeError as e:
        if "has an invalid" not in str(e) or "from" not in str(e) or Path(bpy.data.filepath).resolve()!=asset: raise
    scene=bpy.context.scene;scene.frame_set(0);bpy.context.view_layer.update()
    result={"objects":{},"rig_controls":{}}
    for o in scene.objects:
        mods=[]
        for m in o.modifiers:
            mods.append({"name":m.name,"type":m.type,**{k:str(getattr(m,k)) for k in ("target","object","is_bound","levels","render_levels","show_viewport","show_render") if hasattr(m,k)}})
        particles=[]
        for ps in o.particle_systems:
            particles.append({"name":ps.name,"use_hair_dynamics":ps.use_hair_dynamics,"settings":{k:str(getattr(ps.settings,k)) for k in ("type","count","hair_length","child_type","child_percent","rendered_child_count") if hasattr(ps.settings,k)},"cache":{"start":ps.point_cache.frame_start,"end":ps.point_cache.frame_end,"baked":ps.point_cache.is_baked}})
        if o.name in HORSE_MESHES or particles:result["objects"][o.name]={"parent":o.parent.name if o.parent else None,"parent_type":o.parent_type,"parent_bone":o.parent_bone,"modifiers":mods,"particles":particles}
    arm=bpy.data.objects["horse.rig"]
    for name in ("torso","hips","chest","root","tail.001","tail.002"):
        pb=arm.pose.bones.get(name)
        if pb:result["rig_controls"][name]={"head":list(arm.matrix_world@pb.head),"tail":list(arm.matrix_world@pb.tail)}
    result["tail_bones"]=[p.name for p in arm.pose.bones if "tail" in p.name.lower()]
    if job["mode"]=="demo_hoof_response":
        for track in arm.animation_data.nla_tracks:track.mute=True
        mf.assign_character_action(arm,bpy.data.actions['horse.gallop'])
        for ps in bpy.data.objects['horse'].particle_systems:ps.use_hair_dynamics=False
        _refresh(scene,mf,3)
        result['hoof_response']=[]
        for name in ('r_hoof.L','r_hoof.R','f_hoof.L','f_hoof.R'):
            control=name.replace('r_hoof','hind_foot_ik').replace('f_hoof','forefoot_ik')
            pb=arm.pose.bones[control];saved=pb.matrix_basis.copy()
            for axis in range(3):
                baseline=hoof_surfaces(bpy.context.evaluated_depsgraph_get())['DEF-'+name]['center']
                delta=Vector((.01 if axis==0 else 0,.01 if axis==1 else 0,.01 if axis==2 else 0))
                pb.matrix=Matrix.Translation(arm.matrix_world.inverted().to_3x3()@delta)@pb.matrix;bpy.context.view_layer.update()
                measured=hoof_surfaces(bpy.context.evaluated_depsgraph_get())['DEF-'+name]['center']
                movement=Vector(measured)-Vector(baseline)
                result['hoof_response'].append({'control':control,'hoof':name,'axis':axis,'requested':list(delta),'measured':list(movement),'error_m':(movement-delta).length})
                pb.matrix_basis=saved;bpy.context.view_layer.update()
    mf.write_json(out/"audit.json",result)
    return ["audit.json"]


def prepare_free_repair(mf,out,scene,horse,rider,saddle,path):
    import importlib.util, sys
    spec=importlib.util.spec_from_file_location('mf_demo_kinematic',Path(__file__).with_name('demo_kinematic.py'))
    helper=importlib.util.module_from_spec(spec);sys.modules[spec.name]=helper;spec.loader.exec_module(helper)
    _refresh(scene,mf,0)
    body=bpy.data.objects['horse']
    prep=helper.prepare_diagnostic(scene,[ps for ps in body.particle_systems if ps.name=='horse.tail'])
    # These bindings depend on the incompatible surface chain; existing armature deformation remains on bridles.
    for name in ('bridle','bridle.body'):
        for mod in bpy.data.objects[name].modifiers:
            if mod.type=='SURFACE_DEFORM':mod.show_render=mod.show_viewport=False
    tack_objects=[bpy.data.objects[n] for n in ('saddle','saddle.pad','saddle.stirrup.strap','saddle.stirrup','Torus.002')]
    obsolete=[m for o in tack_objects for m in o.modifiers if m.type in {'SURFACE_DEFORM','ARMATURE'}]
    deps=bpy.context.evaluated_depsgraph_get()
    tack=helper.capture_tack(horse,'torso',tack_objects,deps,dependency_modifiers=obsolete)
    tack.update_tack(0,key=False)
    seat=helper.capture_seat_frame(tack,saddle,deps)
    seat0=seat.matrix_world().copy()
    lengths={n:(rider.pose.bones[n].tail-rider.pose.bones[n].head).length for n in CONTROLS}
    mf.write_json(out/'repair-adaptation.json',{'preparation':prep,'tail_dynamics':{ps.name:ps.use_hair_dynamics for ps in body.particle_systems},'tack_policy':'Rigid source geometry follows evaluated horse torso; obsolete tack armature/surface bindings disabled; original sources untouched','reins_policy':'Source simulated reins replaced in diagnostic copy by deterministic two-endpoint curves','seat0':[list(row) for row in seat0],'control_lengths_armature_units':lengths})
    calibration=calibrate_hoof_speed(mf,out,scene,horse,path)
    install_contact_overlay(mf,out,scene,horse,calibration)
    _refresh(scene,mf,0);tack.update_tack(0,key=False)
    return {'head_rotation':(rider.matrix_world@rider.pose.bones['head'].matrix).to_quaternion(),'speed':calibration['selected_speed_mps'],'helper':helper,'tack':tack,'seat':seat,'seat0':seat0,'lengths':lengths,'tack_samples':{},'out':out}


def build_repaired_reins(mf,repair,rider,horse,scene):
    old=bpy.data.objects['reins'];old.hide_render=old.hide_viewport=True
    for mod in old.modifiers:
        if mod.type=='CLOTH':mod.show_render=mod.show_viewport=False
    material=_material('repaired leather reins',(.07,.035,.014))
    curves=[]
    for side in ('L','R'):
        data=bpy.data.curves.new('repaired rein '+side,'CURVE');data.dimensions='3D';data.bevel_depth=.006;data.bevel_resolution=2
        spline=data.splines.new('POLY');spline.points.add(12)
        obj=bpy.data.objects.new('repaired rein '+side,data);scene.collection.objects.link(obj);obj.data.materials.append(material);curves.append((side,spline))
    gaps=[]
    for f in FRAMES:
        _refresh(scene,mf,f);deps=bpy.context.evaluated_depsgraph_get();lo,hi=_bbox(bpy.data.objects['bit'],deps)
        for side,spline in curves:
            hand=rider.pose.bones['hand_fk.'+side];grip=rider.matrix_world@hand.matrix@Vector((0,hand.length*.55,0))
            bit=Vector((hi.x if side=='L' else lo.x,(lo.y+hi.y)/2,(lo.z+hi.z)/2))
            delta=grip-bit
            points=[]
            for i in range(13):
                t=i/12;points.append(bit+delta*t+Vector((0,0,-.18*4*t*(1-t))))
            for point,co in zip(spline.points,points):point.co=(*co,1);point.keyframe_insert('co',frame=f)
            gaps.append({'frame':f,'side':side,'endpoint_to_hand_anchor_m':(Vector(spline.points[-1].co[:3])-grip).length})
    mf.write_json(repair['out']/'rein-endpoint-check.json',{'samples':gaps,'limitation':'Endpoint equality by construction; not independent proof of visual grasp or freedom from body intersections'})


def hoof_surfaces(deps):
    obj=bpy.data.objects['horse'];ev=obj.evaluated_get(deps);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
    names=['DEF-'+x for x in ('r_hoof.L','r_hoof.R','f_hoof.L','f_hoof.R')]
    indices={obj.vertex_groups[n].index:n for n in names if n in obj.vertex_groups}
    points={n:[] for n in names}
    try:
        for v in mesh.vertices:
            for group in v.groups:
                if group.group in indices and group.weight>.5:points[indices[group.group]].append(ev.matrix_world@v.co)
        result={}
        for n,pts in points.items():
            if not pts:raise ValueError('No evaluated hoof surface vertices for '+n)
            pts.sort(key=lambda p:p.z);low=pts[:max(3,len(pts)//10)]
            center=sum(low,Vector())/len(low)
            result[n]={'center':list(center),'min_z':pts[0].z,'vertices':len(pts)}
        return result
    finally:ev.to_mesh_clear()


def calibrate_hoof_speed(mf,out,scene,horse,path):
    import statistics
    action=path.animation_data.action;path.animation_data.action=None;path.location=(0,0,0)
    source=[]
    for i in range(21):
        _refresh(scene,mf,i/2);source.append({'frame':i/2,'hooves':hoof_surfaces(bpy.context.evaluated_depsgraph_get())})
    floor=min(h['min_z'] for sample in source for h in sample['hooves'].values())
    speeds=[]
    for a,b in zip(source,source[1:]):
        for n,h in a['hooves'].items():
            other=b['hooves'][n]
            if max(h['min_z'],other['min_z'])<=floor+.04:
                velocity=(other['center'][1]-h['center'][1])*48
                if .1<velocity<20:speeds.append(velocity)
    if not speeds:raise ValueError('No source stance sample pairs for speed calibration')
    speed=statistics.median(speeds)
    path.animation_data.action=action
    for fc in mf.action_channels(action):
        if fc.data_path=='location' and fc.array_index==1:
            for key in fc.keyframe_points:key.co.y=-speed*key.co.x/24
    _refresh(scene,mf,0)
    result={'selected_speed_mps':speed,'stance_speed_samples_mps':speeds,'source_minimum_z':floor,'source_samples':source,'method':'Median positive backward velocity of lowest decile of evaluated hoof-group vertices, consecutive half-frames within 4cm of source minimum. Screening estimate, not motion-capture ground truth.'}
    mf.write_json(out/'hoof-calibration.json',result)
    return result


def record_repair_checks(mf,out,repair,rider,horse,path,scene,expected):
    samples=[];bound_errors=[]
    for f in (0,3,7,10,20,59):
        _refresh(scene,mf,f);deps=bpy.context.evaluated_depsgraph_get()
        for name in ('Man','Helmet','saddle','horse'):
            actual=_bbox(bpy.data.objects[name],deps);target=expected[f]['finite_mesh_bounds'][name]
            bound_errors.append({'frame':f,'object':name,'max_error_m':max(abs(actual[j][i]-target[j][i]) for j in range(2) for i in range(3))})
    for tick in range(41):
        f=tick/2;_refresh(scene,mf,f)
        samples.append({'frame':f,'hooves':hoof_surfaces(bpy.context.evaluated_depsgraph_get())})
    screening=[]
    for n in samples[0]['hooves']:
        spans=[];current=[]
        for sample in samples:
            h=sample['hooves'][n]
            if h['min_z']<=.04:current.append((sample['frame'],Vector(h['center'])))
            elif current:spans.append(current);current=[]
        if current:spans.append(current)
        for span in spans:
            if len(span)<2:continue
            slip=max((Vector((p.x,p.y,0))-Vector((span[0][1].x,span[0][1].y,0))).length for _,p in span)
            screening.append({'hoof':n,'frames':[span[0][0],span[-1][0]],'horizontal_excursion_m':slip})
    original_path=path.animation_data.action
    duplicate=original_path.copy();path.animation_data.action=duplicate
    for fc in mf.action_channels(duplicate):
        if fc.data_path=='location' and fc.array_index==1:
            for key in fc.keyframe_points:key.co.y*=2
    _refresh(scene,mf,0);a=path.matrix_world.translation.copy();_refresh(scene,mf,10);b=path.matrix_world.translation.copy()
    travel_error=abs((b.y-a.y)-(-repair['speed']*10/24))
    path.animation_data.action=original_path
    rein=bpy.data.objects['repaired rein L'].data;original_rein=rein.animation_data.action
    wrong=original_rein.copy();rein.animation_data.action=wrong
    for fc in mf.action_channels(wrong):
        if fc.data_path.endswith('points[12].co') and fc.array_index==2:
            for key in fc.keyframe_points:key.co.y+=.25
    _refresh(scene,mf,5);hand=rider.pose.bones['hand_fk.L'];grip=rider.matrix_world@hand.matrix@Vector((0,hand.length*.55,0))
    gap=(Vector(rein.splines[0].points[-1].co[:3])-grip).length
    rein.animation_data.action=original_rein
    repeat=[]
    for f in (0,7,3,0):
        _refresh(scene,mf,f);lo,hi=_bbox(bpy.data.objects['horse'],bpy.context.evaluated_depsgraph_get());repeat.append({'frame':f,'bounds':[list(lo),list(hi)]})
    max_repeat=max(abs(repeat[0]['bounds'][j][i]-repeat[-1]['bounds'][j][i]) for j in range(2) for i in range(3))
    penetration=max(0,-min(h['min_z'] for sample in samples for h in sample['hooves'].values()))
    mf.write_json(out/'repair-validation.json',{'bake_bound_comparisons':bound_errors,'max_bake_bound_error_m':max(x['max_error_m'] for x in bound_errors),'hoof_samples':samples,'stance_segments':screening,'max_stance_excursion_m':max(x['horizontal_excursion_m'] for x in screening),'max_hoof_penetration_m':penetration,'repeat_mesh_bound_error_m':max_repeat,'negative_controls':{'doubled_path':{'error_m':travel_error,'detected':travel_error>.001},'offset_rein':{'gap_m':gap,'detected':gap>.01}},'limitations':['Hoof samples use low-decile evaluated weighted vertices; patch membership can change with foot orientation.','Repeat bounds exclude rendered hair strands; tail still requires full-playback review.','No physical grasp or contact-force simulation.','Rigid-rider baseline remains visual comparison, not automatically qualified negative control.']})
    _refresh(scene,mf,0)


def install_contact_overlay(mf,out,scene,horse,calibration):
    import importlib.util,sys,hashlib
    spec=importlib.util.spec_from_file_location('mf_demo_contact',Path(__file__).with_name('demo_contact.py'))
    contact=importlib.util.module_from_spec(spec);sys.modules[spec.name]=contact;spec.loader.exec_module(contact)
    source=bpy.data.actions['horse.gallop']
    def action_hash():
        return hashlib.sha256(repr([(fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points]) for fc in mf.action_channels(source)]).encode()).hexdigest()
    before=action_hash();samples=calibration['source_samples'];speed=calibration['selected_speed_mps']
    controls={'r_hoof.L':('hind_foot_ik.L',(9.5,12)),'r_hoof.R':('hind_foot_ik.R',(1.5,3)),'f_hoof.L':('forefoot_ik.L',(2.5,5)),'f_hoof.R':('forefoot_ik.R',(4,7))}
    records=[];maximum=0;source_lengths={}
    names=[p.name for p in horse.pose.bones if p.name.startswith(('DEF-thigh','DEF-shin','DEF-upper_arm','DEF-forearm'))]
    for tick in range(241):
        f=tick/4;_refresh(scene,mf,f)
        if tick%4==0:source_lengths[int(f)]={n:(horse.pose.bones[n].tail-horse.pose.bones[n].head).length for n in names}
        for hoof,(control,interval) in controls.items():
            def trajectory(t):
                a=min(int(t*2),19);w=t*2-a
                x=samples[a]['hooves']['DEF-'+hoof]['center'];y=samples[a+1]['hooves']['DEF-'+hoof]['center']
                return tuple(x[i]*(1-w)+y[i]*w for i in range(3))
            delta=contact.offset(f%10,trajectory,*interval,(0,-speed,0),blend=.5)
            maximum=max(maximum,Vector(delta).length)
            records.append((f,control,contact.control_delta(horse,horse.pose.bones[control],delta)))
    overlay=contact.bake_overlay(horse,records)
    ratios=[]
    for f,baseline in source_lengths.items():
        _refresh(scene,mf,f)
        for n,length in baseline.items():
            actual=(horse.pose.bones[n].tail-horse.pose.bones[n].head).length
            if length>1e-6:ratios.append(actual/length)
    mf.write_json(out/'contact-overlay.json',{'source_action_sha256_before':before,'source_action_sha256_after':action_hash(),'source_action_unchanged':before==action_hash(),'overlay_action':overlay.name,'controls':list(v[0] for v in controls.values()),'max_world_correction_m':maximum,'correction_limit_m':.30,'sample_step_frames':.25,'blend_margin_frames':.5,'source_limb_length_ratio_min':min(ratios),'source_limb_length_ratio_max':max(ratios),'policy':'Separate additive existing-IK location layer. Horizontal minimax stance target; source vertical trajectory preserved. Source gallop action retained unchanged. Sole and skin checks still required.'})
    _refresh(scene,mf,0)


def verify_free_scene(mf,out,job):
    import json
    out=_output(job)
    source=ROOT_PATH/'runs/demonstrator-01/free-motion-v2-retry'
    scene_file=_file(source/'scene.blend','32518f65560d6bdf9c08d200dbc4061e8fd890e4fe768d83d598dfd7b001a174')
    bpy.ops.wm.open_mainfile(filepath=str(scene_file),load_ui=False,use_scripts=False)
    scene=bpy.context.scene
    prior=json.loads((source/'metrics.json').read_text())['per_frame']
    errors=[];mesh_samples=[];hoof_samples=[];rein_gaps=[]
    rider=bpy.data.objects['rig']
    for tick in range(473):
        frame=tick/8
        _refresh(scene,mf,frame);deps=bpy.context.evaluated_depsgraph_get()
        hoof_samples.append({'frame':frame,'hooves':hoof_surfaces(deps)})
        for side in ('L','R'):
            hand=rider.pose.bones['hand_fk.'+side]
            grip=rider.matrix_world@hand.matrix@Vector((0,hand.length*.55,0))
            point=bpy.data.objects['repaired rein '+side].data.splines[0].points[-1].co
            rein_gaps.append((Vector(point[:3])-grip).length)
        if tick%8==0:
            bounds={n:[list(corner) for corner in _bbox(bpy.data.objects[n],deps)] for n in ('Man','Helmet','saddle','horse')}
            mesh_samples.append({'frame':frame,'bounds':bounds})
            expected=prior[int(frame)]['finite_mesh_bounds']
            errors.extend(abs(bounds[n][j][i]-expected[n][j][i]) for n in bounds for j in range(2) for i in range(3))
    spans=[]
    for name in hoof_samples[0]['hooves']:
        current=[]
        for sample in hoof_samples+[None]:
            if sample and sample['hooves'][name]['min_z']<=.04:
                current.append(sample)
            elif current:
                origin=Vector(current[0]['hooves'][name]['center'])
                slip=max(math.hypot(x['hooves'][name]['center'][0]-origin.x,x['hooves'][name]['center'][1]-origin.y) for x in current)
                spans.append({'hoof':name,'start':current[0]['frame'],'end':current[-1]['frame'],'slip_m':slip})
                current=[]
    repeated=[]
    for frame in (0,7.125,3.375,59,0):
        _refresh(scene,mf,frame);repeated.append(_bbox(bpy.data.objects['horse'],bpy.context.evaluated_depsgraph_get()))
    path=bpy.data.objects['horse diagnostic path']
    _refresh(scene,mf,0);start=path.matrix_world.translation.copy()
    _refresh(scene,mf,59);end=path.matrix_world.translation.copy()
    speed=json.loads((source/'hoof-calibration.json').read_text())['selected_speed_mps']
    result={'scene_sha256':'32518f65560d6bdf9c08d200dbc4061e8fd890e4fe768d83d598dfd7b001a174','frames':[0,59],'sample_step':.125,'path_displacement_error_m':abs((end.y-start.y)+speed*59/24),'source_follow_path_muted':all(c.mute for c in bpy.data.objects['horse.rig'].constraints if c.type=='FOLLOW_PATH'),
      'reopen_max_bounds_error_m':max(errors),'all_bounds_finite':all(math.isfinite(v) for x in mesh_samples for b in x['bounds'].values() for corner in b for v in corner),
      'max_stance_excursion_m':max(x['slip_m'] for x in spans),'max_hoof_penetration_m':max(0,-min(h['min_z'] for x in hoof_samples for h in x['hooves'].values())),
      'max_rein_endpoint_error_m':max(rein_gaps),'repeat_bounds_error_m':max(abs(repeated[0][j][i]-repeated[-1][j][i]) for j in range(2) for i in range(3)),
      'stance_segments':spans,'mesh_samples':mesh_samples,'limitations':['Same low-decile sole-patch estimator as calibration; not independent collision/contact proof.','Dense time samples are independent of quarter-frame bake keys.','Rein endpoints measure attachment, not hand surface enclosure.','Foot/stirrup and body/tack intersections remain unqualified.']}
    mf.write_json(out/'verification.json',result)
    _refresh(scene,mf,3)
    scene.camera=bpy.data.objects['lateral'];scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.cycles.samples=24
    scene.render.filepath=str(out/'representative-720p.png')
    started=time.perf_counter();bpy.ops.render.render(write_still=True)
    mf.write_json(out/'render-measurement.json',{'resolution':[1280,720],'samples':24,'frame':3,'render_seconds':time.perf_counter()-started,'scope':'Same diagnostic scene only; scenery, dust and finishing not represented'})
    return ['verification.json','representative-720p.png','render-measurement.json']
