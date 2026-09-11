"""Trusted, bounded 3D-06A fixture screen and authored gesture builder."""
import math
import json
import hashlib
import importlib.util
from pathlib import Path
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
    if mf.file_sha256(Path(job['parent_native'])) != job['baseline_sha256']:
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


def _rules():
    spec=importlib.util.spec_from_file_location('gesture_rules', Path(__file__).parents[2]/'gesture.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def _hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def protected(mf):
    mesh=bpy.data.objects['character_01_mesh'];arm=bpy.data.objects['character_01_armature']
    inspect=mf.load_inspector()
    return _hash({'objects':[(o.name,o.type,inspect.custom(o),o.parent.name if o.parent else None,
                              [list(r) for r in o.matrix_world],o.hide_render) for o in bpy.data.objects],
        'vertices':[list(v.co) for v in mesh.data.vertices], 'faces':[list(p.vertices) for p in mesh.data.polygons],
        'weights':[[[g.group,g.weight] for g in v.groups] for v in mesh.data.vertices],
        'rests':{b.name:[list(r) for r in b.matrix_local] for b in arm.data.bones},
        'materials':[(m.name, list(m.diffuse_color),inspect.custom(m),inspect.nodes(m.node_tree)) for m in bpy.data.materials],
        'camera_lights':[(o.name,inspect.rna_values(o.data),inspect.custom(o.data)) for o in bpy.data.objects if o.type in {'CAMERA','LIGHT'}],
        'modifiers':[(m.name,inspect.rna_values(m),inspect.value(getattr(m,'object',None))) for m in mesh.modifiers],
        'original_actions':{a.name:mf._action_fingerprint(a) for a in bpy.data.actions if a.name!='character_action_gesture_3d06a_candidate'}})


def make_candidate(mf, control=None):
    rules=_rules();arm=bpy.data.objects['character_01_armature']
    baseline=bpy.data.actions['character_action_gesture_3d06a_baseline']
    old=bpy.data.actions.get('character_action_gesture_3d06a_candidate')
    if old:
        mf.assign_character_action(arm,baseline);bpy.data.actions.remove(old)
    samples={}
    for frame in range(97):
        t=frame if control=='no_op' else frame+4 if control=='global_timing' else rules.source_time(frame)
        mf.assign_character_action(arm,baseline);mf._set_scene_time(bpy.context.scene,t)
        samples[frame]={b.name:b.matrix_basis.copy() for b in arm.pose.bones}
    action=bpy.data.actions.new('character_action_gesture_3d06a_candidate');action.use_fake_user=True
    mf.assign_character_action(arm,action)
    for frame,values in samples.items():
        for name,basis in values.items():
            bone=arm.pose.bones[name];loc,rot,scale=basis.decompose()
            if control=='boundary_jump' and name=='RightHand' and frame==24:loc.x+=.08/max(1e-8,arm.matrix_world.to_scale().x)
            if control=='foot_drift' and name=='RightFoot':loc.x+=.02/max(1e-8,arm.matrix_world.to_scale().x)
            if control=='elbow_deformation' and name=='RightForeArm' and 36<=frame<=60:scale.y*=2.2
            bone.rotation_mode='QUATERNION';bone.location=loc;bone.rotation_quaternion=rot;bone.scale=scale
            for field in ['location','rotation_quaternion','scale']:bone.keyframe_insert(data_path=field,frame=frame,group=name)
    for curve in mf.action_channels(action):
        for key in curve.keyframe_points:key.interpolation='LINEAR'
    return action


def sample(mf, role, frame):
    arm=bpy.data.objects['character_01_armature'];mesh=bpy.data.objects['character_01_mesh']
    mf.assign_character_action(arm,bpy.data.actions['character_action_gesture_3d06a_'+role])
    mf._set_scene_time(bpy.context.scene,frame)
    shoulder=arm.matrix_world@arm.pose.bones['RightArm'].head
    return {'points':mf._evaluated_character_points(mesh),
        'rotations':{name:arm.pose.bones[name].matrix.to_quaternion().copy() for name in ['RightArm','RightForeArm','RightHand','Head']},
        'relative':[arm.matrix_world@arm.pose.bones[name].head-shoulder for name in ['RightForeArm','RightHand']],
        'forearm_local':arm.pose.bones['RightForeArm'].rotation_quaternion.copy(),
        'pose_digest':_hash({b.name:[list(r) for r in b.matrix] for b in arm.pose.bones})}


def measure(mf, edges, expected_protected):
    rules=_rules();neutral=sample(mf,'baseline',0)
    feet=[i for i,p in enumerate(neutral['points']) if p.z<.08]
    cue=sample(mf,'baseline',48)['forearm_local']
    cue_angle=neutral['forearm_local'].rotation_difference(cue).angle
    if abs(cue_angle-math.radians(19.2))>1e-4:
        raise ValueError('Measured cue does not match the authored 19.2-degree forearm landmark')
    metrics={'baseline_cue_frame':None,'candidate_cue_frame':None,'outside_max_vertex_delta_m':0.,
        'outside_max_rotation_delta_rad':0.,'boundary_position_delta_m':0.,'boundary_velocity_delta_m_s':0.,
        'boundary_angular_velocity_delta_deg_s':0.,'support_displacement_m':0.,'min_z_m':1e9,
        'elbow_min':1e9,'elbow_max':0.,'landmark_position_rms_m':0.,'landmark_rotation_error_deg':0.,
        'finite':True,'protected':protected(mf)==expected_protected}
    times={i*.5 for i in range(193)}
    for f in [24,44,48,72]:
        for offset in [-.5,-.25,-.1,-.01,-.001,0,.001,.01,.1,.25,.5]:times.add(f+offset)
    trajectory=[]
    for frame in sorted(times):
        pair={role:sample(mf,role,frame) for role in ['baseline','candidate']}
        for role,s in pair.items():
            points=s['points'];ratios=[(points[a]-points[b]).length/n for a,b,n in edges]
            metrics['finite'] &= all(math.isfinite(c) for p in points for c in p)
            metrics['min_z_m']=min(metrics['min_z_m'],min(p.z for p in points))
            metrics['support_displacement_m']=max(metrics['support_displacement_m'],max((points[i]-neutral['points'][i]).length for i in feet))
            metrics['elbow_min']=min(metrics['elbow_min'],min(ratios));metrics['elbow_max']=max(metrics['elbow_max'],max(ratios))
            angle=neutral['forearm_local'].rotation_difference(s['forearm_local']).angle
            if metrics[role+'_cue_frame'] is None and angle>=cue_angle-1e-5:metrics[role+'_cue_frame']=frame
        a,b=pair['baseline'],pair['candidate']
        delta=max((p-q).length for p,q in zip(a['points'],b['points']))
        if frame<=24 or frame>=72:
            metrics['outside_max_vertex_delta_m']=max(metrics['outside_max_vertex_delta_m'],delta)
            metrics['outside_max_rotation_delta_rad']=max(metrics['outside_max_rotation_delta_rad'],max(a['rotations'][n].rotation_difference(b['rotations'][n]).angle for n in a['rotations']))
        if frame in (24,72):metrics['boundary_position_delta_m']=max(metrics['boundary_position_delta_m'],delta)
        target=sample(mf,'baseline',rules.source_time(frame))
        metrics['landmark_position_rms_m']=max(metrics['landmark_position_rms_m'],math.sqrt(sum((p-q).length_squared for p,q in zip(target['relative'],b['relative']))/2))
        metrics['landmark_rotation_error_deg']=max(metrics['landmark_rotation_error_deg'],max(math.degrees(target['rotations'][n].rotation_difference(b['rotations'][n]).angle) for n in target['rotations']))
        trajectory.append({'frame':frame,'baseline_wrist':list(a['relative'][1]),'candidate_wrist':list(b['relative'][1])})
    for frame in (24,72):
        for h in (.001,.01,.1,.25,.5):
            s={role:[sample(mf,role,frame+offset) for offset in (-h,0,h)] for role in ['baseline','candidate']}
            delta_vel=[];delta_rot=[]
            for role in ['baseline','candidate']:
                p=s[role]
                delta_vel.append([(c-b)/(h/24)-(b-a)/(h/24) for a,b,c in zip(p[0]['points'],p[1]['points'],p[2]['points'])])
                delta_rot.append({n:(p[1]['rotations'][n].rotation_difference(p[2]['rotations'][n]).angle-p[0]['rotations'][n].rotation_difference(p[1]['rotations'][n]).angle)/(h/24) for n in p[0]['rotations']})
            metrics['boundary_velocity_delta_m_s']=max(metrics['boundary_velocity_delta_m_s'],max((a-b).length for a,b in zip(*delta_vel)))
            metrics['boundary_angular_velocity_delta_deg_s']=max(metrics['boundary_angular_velocity_delta_deg_s'],max(math.degrees(abs(delta_rot[0][n]-delta_rot[1][n])) for n in delta_rot[0]))
    return {'metrics':metrics,'validation':rules.validate(metrics),'trajectory':trajectory,'cue_threshold_radians':cue_angle}


def campaign(mf,out,job):
    if job.get('mode')!='gesture_campaign' or job.get('render_frames') not in (True,False) or job.get('stage') not in ('preview','qualification'):
        raise ValueError('Unrecognized gesture campaign')
    if mf.file_sha256(Path(job['parent_native'])) != job['baseline_sha256']:raise ValueError('Screened fixture hash mismatch')
    bpy.ops.wm.open_mainfile(filepath=job['parent_native'],load_ui=False,use_scripts=False)
    screen_data=json.loads(Path(job['screen_metrics']).read_text());edges=screen_data['elbow_reference_edges']
    expected=protected(mf)
    make_candidate(mf)
    positive=measure(mf,edges,expected);mf.write_json(out/'positive.json',positive)
    if not positive['validation']['passed']:
        mf.write_json(out/'campaign-result.json',{'status':'TECHNICAL_FAILURE','scored':False,'errors':positive['validation']['errors']})
        return ['positive.json','campaign-result.json']
    if job['stage']=='preview':
        mf.write_json(out/'campaign-result.json',{'status':'POSITIVE_PASS_PREVIEW','scored':False})
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),check_existing=False,compress=True,relative_remap=False)
        if job['render_frames']:render_frames(mf,out,job['profile'])
        return ['positive.json','campaign-result.json','scene.blend']
    controls={}
    for name,gate in [('no_op','candidate_cue'),('global_timing','outside_preserved'),('boundary_jump','boundary_position'),('foot_drift','support'),('elbow_deformation','deformation')]:
        make_candidate(mf,name)
        folder=out/'controls'/name;folder.mkdir(parents=True,exist_ok=True)
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),check_existing=False,compress=True,relative_remap=False)
        result=measure(mf,edges,expected)
        controls[name]={'expected_error':gate,'sensitive':gate in result['validation']['errors'] and gate not in positive['validation']['errors'],'validation':result['validation'],'metrics':result['metrics']}
    make_candidate(mf)
    replay=measure(mf,edges,expected)
    replay_equal=replay==positive
    mf.write_json(out/'controls.json',controls)
    checkpoints=[]
    for role in ['baseline','candidate']:
        for frame in [0,44 if role=='candidate' else 48,56 if role=='candidate' else 60]:
            before=sample(mf,role,frame)
            folder=out/'checkpoints'/f'{role}-{frame}';folder.mkdir(parents=True,exist_ok=True)
            bpy.context.preferences.filepaths.save_version=0
            bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),check_existing=False,compress=True,relative_remap=False)
            bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'),load_ui=False,use_scripts=False)
            after=sample(mf,role,frame)
            error=max((a-b).length for a,b in zip(before['points'],after['points']))
            checkpoints.append({'role':role,'frame':frame,'max_vertex_delta_m':error,'pose_equal':before['pose_digest']==after['pose_digest'],'protected':protected(mf)==expected})
    mf.write_json(out/'persistence.json',{'checkpoints':checkpoints,'rebuild_metrics_equal':replay_equal})
    passed=all(x['sensitive'] for x in controls.values()) and replay_equal and all(x['max_vertex_delta_m']<=1e-6 and x['pose_equal'] and x['protected'] for x in checkpoints)
    mf.write_json(out/'campaign-result.json',{'status':'MACHINE_PASS_DIRECTOR_PENDING' if passed else 'TECHNICAL_FAILURE','scored':job.get('scored',False),'positive_passed':True,'controls_sensitive':all(x['sensitive'] for x in controls.values()),'replay_equal':replay_equal})
    if job['render_frames'] and passed:
        render_frames(mf,out,job['profile'])
    return ['positive.json','controls.json','persistence.json','campaign-result.json']


def render_frames(mf,out,profile):
    scene=bpy.context.scene;mf.apply_profile(profile,306);scene.cycles.use_denoising=True
    for role in ['baseline','candidate']:
        for camera_name in ['camera_A','camera_B']:
            scene.camera=bpy.data.objects[camera_name]
            for frame in range(96):
                sample(mf,role,frame)
                path=out/'frames'/role/camera_name/f'frame-{frame:04d}.png';path.parent.mkdir(parents=True,exist_ok=True)
                scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)


def render_tail(mf,out,job):
    frames=job.get('frames')
    if not isinstance(frames,list) or not 1<=len(frames)<=16 or any(type(f) is not int or not 80<=f<=95 for f in frames):
        raise ValueError('Tail recovery is limited to 16 final candidate-side frames')
    if mf.file_sha256(Path(job['parent_native']))!=job['baseline_sha256']:raise ValueError('Preview native changed')
    bpy.ops.wm.open_mainfile(filepath=job['parent_native'],load_ui=False,use_scripts=False)
    scene=bpy.context.scene;mf.apply_profile(job['profile'],306);scene.cycles.use_denoising=True
    scene.camera=bpy.data.objects['camera_B']
    artifacts=[]
    for frame in frames:
        sample(mf,'candidate',frame)
        relative=f'frames/candidate/camera_B/frame-{frame:04d}.png'
        path=out/relative;path.parent.mkdir(parents=True,exist_ok=True)
        scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);artifacts.append(relative)
    return artifacts
