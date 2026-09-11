"""Trusted, bounded 3D-06A fixture screen and authored gesture builder."""
import math
import json
import bpy
from mathutils import Matrix, Vector


def validate_plan(plan):
    expected = {'schema_version', 'annotation_method', 'frame_rate', 'landmarks',
                'upper_arm_degrees', 'forearm_degrees', 'wrist_degrees', 'head_degrees', 'control'}
    if set(plan) != expected or plan['schema_version'] != '1.0' or plan['frame_rate'] != 24:
        raise ValueError('Unrecognized gesture plan')
    if plan['annotation_method'] != 'manual_authored_pose_time_board' or plan['control'] is not None:
        raise ValueError('Only the admitted no-prop screen is supported')
    if plan['landmarks'] != [[0, 0.0], [24, 0.1], [48, 0.6], [60, 1.0], [96, 0.0]]:
        raise ValueError('Unqualified reference timeline')
    for key, bound in [('upper_arm_degrees', 10), ('forearm_degrees', 35), ('wrist_degrees', 8), ('head_degrees', 4)]:
        if type(plan[key]) not in (int, float) or not math.isfinite(plan[key]) or abs(plan[key]) > bound:
            raise ValueError('Gesture exceeds bounded fixture screen')


def weight(frame, plan):
    for (a, x), (b, y) in zip(plan['landmarks'], plan['landmarks'][1:]):
        if a <= frame <= b:
            t = (frame-a)/(b-a)
            smooth = 6*t**5-15*t**4+10*t**3
            return x+(y-x)*smooth
    return 0.0


def _rotate_chain(armature, matrices, bone_name, axis, degrees):
    bone = armature.pose.bones[bone_name]
    origin = matrices[bone_name].translation
    transform = Matrix.Translation(origin)@Matrix.Rotation(math.radians(degrees), 4, axis)@Matrix.Translation(-origin)
    for item in armature.pose.bones:
        if item == bone or bone in item.parent_recursive:
            matrices[item.name] = transform@matrices[item.name]


def screen(mf, out, job):
    plan = job['plan']; validate_plan(plan)
    if mf.file_sha256(__import__('pathlib').Path(job['parent_native'])) != job['baseline_sha256']:
        raise ValueError('Gesture baseline digest mismatch')
    bpy.ops.wm.open_mainfile(filepath=job['parent_native'], load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    arm = bpy.data.objects['character_01_armature']; mesh = bpy.data.objects['character_01_mesh']
    original = {a.name: mf._action_fingerprint(a) for a in bpy.data.actions}
    mf.assign_character_action(arm, bpy.data.actions['character_action_idle'])
    mf._set_scene_time(scene, 1)
    initial = {b.name: b.matrix.copy() for b in arm.pose.bones}
    rest = {b.name: b.bone.matrix_local.copy() for b in arm.pose.bones}
    reference = mf._evaluated_character_points(mesh)
    center = arm.matrix_world@arm.pose.bones['RightForeArm'].head
    groups = {g.index for g in mesh.vertex_groups if g.name in {'RightArm', 'RightForeArm'}}
    selected = {v.index for v in mesh.data.vertices if (reference[v.index]-center).length < .09
                and any(g.group in groups and g.weight >= .05 for g in v.groups)}
    edges = [[a, b, (reference[a]-reference[b]).length] for edge in mesh.data.edges
             for a, b in [tuple(edge.vertices)] if a in selected and b in selected]
    if len(edges) != 26 or any(e[2] <= 1e-8 for e in edges):
        raise ValueError('Known 26-edge fixture screen changed; inspect fixture before proceeding')
    feet = [i for i, p in enumerate(reference) if p.z < .08]
    up = arm.matrix_world.to_quaternion().inverted()@Vector((0, 0, 1))
    axes = {}
    for name in ['RightArm', 'RightForeArm']:
        direction = initial[name].to_quaternion()@Vector((0, 1, 0))
        axis = direction.cross(up)
        if axis.length < 1e-6:
            raise ValueError('Degenerate lift plane')
        axes[name] = axis.normalized()
    action = bpy.data.actions.new('character_action_gesture_3d06a_baseline')
    action.use_fake_user = True
    mf.assign_character_action(arm, action)
    previous = {name: None for name in initial}
    interaction = mf.load_interaction()
    for frame in range(97):
        value = weight(frame, plan)
        desired = {name: m.copy() for name, m in initial.items()}
        _rotate_chain(arm, desired, 'RightArm', axes['RightArm'], value*plan['upper_arm_degrees'])
        _rotate_chain(arm, desired, 'RightForeArm', axes['RightForeArm'], value*plan['forearm_degrees'])
        _rotate_chain(arm, desired, 'RightHand', axes['RightForeArm'], value*plan['wrist_degrees'])
        _rotate_chain(arm, desired, 'Head', Vector((1, 0, 0)), value*plan['head_degrees'])
        interaction._insert_pose(mf, arm, action, frame, desired, rest, previous, key_names=tuple(initial))
    for curve in mf.action_channels(action):
        for key in curve.keyframe_points:
            key.interpolation = 'LINEAR'
    scene.render.fps = 24; scene.render.fps_base = 1
    scene.frame_start = 0; scene.frame_end = 96
    samples = []; landmarks = {}
    for frame in [i*.5 for i in range(193)]:
        mf._set_scene_time(scene, frame)
        points = mf._evaluated_character_points(mesh)
        ratios = [(points[a]-points[b]).length/length for a,b,length in edges]
        sample = {'frame': frame, 'elbow_min': min(ratios), 'elbow_max': max(ratios),
                  'min_z_m': min(p.z for p in points),
                  'foot_displacement_m': max((points[i]-reference[i]).length for i in feet),
                  'finite': all(math.isfinite(c) for p in points for c in p)}
        samples.append(sample)
        if frame in [x[0] for x in plan['landmarks']]:
            landmarks[str(int(frame))] = {name: {'world_head_m': list(arm.matrix_world@arm.pose.bones[name].head),
                'armature_rotation_quaternion': list(arm.pose.bones[name].matrix.to_quaternion())}
                for name in ['RightArm', 'RightForeArm', 'RightHand', 'Head']}
    checks = {'elbow_band': all(.35 <= x['elbow_min'] and x['elbow_max'] <= 1.50 for x in samples),
              'grounding': all(x['min_z_m'] >= -.002 for x in samples),
              'support_stationary': all(x['foot_displacement_m'] <= .003 for x in samples),
              'finite': all(x['finite'] for x in samples),
              'original_actions_preserved': all(mf._action_fingerprint(bpy.data.actions[name]) == fingerprint for name,fingerprint in original.items())}
    mf.write_json(out/'fixture-screen.json', {'status': 'MACHINE_PASS' if all(checks.values()) else 'FAILED',
        'scored': False, 'checks': checks, 'samples': samples, 'landmarks': landmarks,
        'axes_armature': {name: list(axis) for name,axis in axes.items()}, 'elbow_reference_edges': edges,
        'limits': {'elbow_min': .35, 'elbow_max': 1.5, 'foot_displacement_m': .003, 'floor_penetration_m': .002}})
    mf._set_scene_time(scene, 0)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'), check_existing=False, compress=True, relative_remap=False)
    mf.apply_profile(job['profile'], 306)
    for camera_name in ['camera_A', 'camera_B']:
        camera = bpy.data.objects.get(camera_name)
        if camera is None:
            raise ValueError('Qualified camera missing')
        scene.camera = camera
        for frame,_ in plan['landmarks']:
            mf._set_scene_time(scene, frame)
            path = out/'poses'/camera_name/f'frame-{frame:04d}.png'; path.parent.mkdir(parents=True, exist_ok=True)
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
    return ['fixture-screen.json', 'scene.blend']
