"""Explicit supported horse-pose proof, not an automatic choreography system.

No recipe code, imports or paths. Preserve weighted donor and bone lengths;
resolve only inspected same-rig BBone targets and explicitly select FK ownership.
"""
import math
import re


def bend_joint(a, b, length_a, length_b, hint):
    """Two fixed-length links, chosen bend side. Inputs plain triples for tests."""
    def sub(x, y): return [u-v for u, v in zip(x, y)]
    def dot(x, y): return sum(u*v for u, v in zip(x, y))
    delta = sub(b, a); distance = math.sqrt(dot(delta, delta))
    if not abs(length_a-length_b)+1e-6 < distance < length_a+length_b-1e-6:
        raise ValueError('SUPPORT_UNREACHABLE_NO_STRETCH')
    axis = [v/distance for v in delta]
    along = (length_a**2-length_b**2+distance**2)/(2*distance)
    side = [h-dot(hint, axis)*v for h, v in zip(hint, axis)]
    norm = math.sqrt(dot(side, side))
    if norm < 1e-6: raise ValueError('SUPPORT_AMBIGUOUS_BEND')
    height = math.sqrt(max(0, length_a**2-along**2))
    return [a[i]+along*axis[i]+height*side[i]/norm for i in range(3)]


def repair_bbone_targets(bpy):
    rig = bpy.data.objects['horse.rig']
    curves = list(rig.data.animation_data.drivers)
    todo = []
    for fc in curves:
        d = fc.driver
        if d.is_valid: continue
        if (d.type != 'SUM' or not re.fullmatch(r'bones\["[\w.-]+"\]\.bbone_ease(in|out)', fc.data_path)
                or len(d.variables) != 1):
            raise ValueError('SUPPORT_UNRECOGNIZED_DRIVER')
        var = d.variables[0]
        if var.type != 'SINGLE_PROP' or len(var.targets) != 1: raise ValueError('SUPPORT_DRIVER_SHAPE')
        target = var.targets[0]
        if target.id is not None or target.id_type != 'OBJECT': raise ValueError('SUPPORT_DRIVER_OWNER')
        if not re.fullmatch(r'pose\.bones\["[\w.-]+"\]\["(rubber_tweak|finger_curve)"\]', target.data_path):
            raise ValueError('SUPPORT_DRIVER_PATH')
        value = rig.path_resolve(target.data_path)
        if not isinstance(value, (int, float)) or not math.isfinite(value): raise ValueError('SUPPORT_DRIVER_VALUE')
        rig.data.path_resolve(fc.data_path)
        todo.append(target)
    if len(todo) not in (0, 64): raise ValueError('SUPPORT_DRIVER_SET_CHANGED')
    for target in todo: target.id = rig
    rig.data.update_tag(); rig.update_tag(); bpy.context.view_layer.update()
    return len(todo)


def capture_stance(bpy):
    """Capture once before any frame authoring; never re-sample a modified stance."""
    from mathutils import Vector
    scene = bpy.context.scene
    rig = bpy.data.objects['horse.rig']; pivot = bpy.data.objects['HORSE hind support pivot']
    scene.frame_set(283); bpy.context.view_layer.update()
    base_world = rig.matrix_world.copy(); base_pivot = pivot.matrix_world.copy()
    base_rot = base_world.to_quaternion(); scale = base_world.to_scale()
    if max(scale)-min(scale) > 1e-3: raise ValueError('SUPPORT_NONUNIFORM_RIG_SCALE')
    unit = sum(scale)/3
    feet = {s: {n: (base_world @ rig.pose.bones[n+'.'+s].matrix).copy()
                for n in ('hind_foot_fk', 'r_toe_fk', 'r_hoof', 'forefoot_fk', 'f_toe_fk', 'f_hoof')}
            for s in ('L','R')}
    return {'world':base_world, 'pivot':base_pivot, 'rotation':base_rot, 'unit':unit, 'feet':feet,
            'rider':bpy.data.objects['mounted leader'].matrix_world.copy()}


def apply_pose(bpy, edit, baseline=None):
    from mathutils import Matrix, Vector, Quaternion
    scene = bpy.context.scene; frame = edit['frame']
    rig = bpy.data.objects['horse.rig']; pivot = bpy.data.objects['HORSE hind support pivot']
    baseline = baseline or capture_stance(bpy)
    base_world=baseline['world'];base_pivot=baseline['pivot'];base_rot=baseline['rotation']
    unit=baseline['unit'];feet=baseline['feet']
    def bw(v): return base_world @ Vector(v)
    def direction(v): return base_rot @ Vector(v)
    hip = bw((0, .52, 1.63))
    scene.frame_set(frame)
    # Rotate around the hip, not a ground pivot. Translation defines load/height;
    # legs are independently solved to world-ground endpoints afterward.
    pitch = Quaternion(direction((1,0,0)), edit['pitch']).to_matrix().to_4x4()
    shift = direction((0, edit['hip_back']*unit, -edit['hip_drop']*unit))
    pivot.matrix_world = Matrix.Translation(hip+shift) @ pitch @ Matrix.Translation(-hip) @ base_pivot
    pivot.rotation_mode='QUATERNION'
    for path in ('location','rotation_quaternion','scale'): pivot.keyframe_insert(path, frame=frame)
    # The ownership is explicit; removed Rigify drivers cannot override this.
    for side in ('L','R'):
        for name in ('thigh','lower_leg','hind_foot','r_toe','upper_arm','forearm','forefoot','f_toe'):
            pb = rig.pose.bones.get('ORG-'+name+'.'+side)
            if pb:
                for con in pb.constraints:
                    if con.type == 'COPY_TRANSFORMS':
                        con.influence = 1.0 if '_fk.' in con.subtarget else 0.0
                        con.keyframe_insert('influence', frame=frame)
        for name in ('MCH-r_hoof.','MCH-f_hoof.'):
            for con in rig.pose.bones[name+side].constraints:
                if con.type == 'COPY_TRANSFORMS':
                    con.influence=0; con.keyframe_insert('influence', frame=frame)
    # Remove inherited small oscillations from the body at this proof frame.
    for name in ('torso','hips','chest','neck_bend'):
        b=rig.pose.bones[name]; b.matrix_basis=Matrix.Identity(4); b.rotation_mode='QUATERNION'
        for path in ('location','rotation_quaternion','scale'): b.keyframe_insert(path, frame=frame)
    bpy.context.view_layer.update()
    def set_world(name, matrix):
        b=rig.pose.bones[name]; b.rotation_mode='QUATERNION'
        b.matrix = rig.matrix_world.inverted() @ matrix
        for path in ('location','rotation_quaternion','scale'): b.keyframe_insert(path, frame=frame)
        bpy.context.view_layer.update()
    def segment(name, start, end):
        b=rig.pose.bones[name]
        rest = base_world.to_3x3() @ b.bone.matrix_local.to_3x3()
        q = rest.col[1].normalized().rotation_difference((end-start).normalized())
        rot = q.to_matrix() @ rest
        m=rot.to_4x4(); m.translation=start
        set_world(name,m)
    def length(name): return rig.data.bones[name].length*unit
    evidence=[]
    for side in ('L','R'):
        suffix='.'+side
        # Fetlock/hoof targets remain in the standing ground frame. Choose a
        # physiologically flexed hock above the fetlock, then solve stifle.
        ankle=feet[side]['r_toe_fk'].translation.copy()
        foot_len=length('hind_foot_fk'+suffix)
        load=min(1,max(0,abs(edit['pitch'])/.8))
        standing=(feet[side]['hind_foot_fk'].translation-ankle).normalized()
        folded=direction((0,.12,math.sqrt(foot_len**2-(.12*unit)**2)/unit)).normalized()
        hock=ankle+standing.lerp(folded,load).normalized()*foot_len
        start=rig.matrix_world @ rig.pose.bones['thigh_fk'+suffix].head
        knee=Vector(bend_joint(list(start),list(hock),length('thigh_fk'+suffix),
                              length('lower_leg_fk'+suffix),list(direction((0,-1,0)))))
        segment('thigh_fk'+suffix,start,knee)
        segment('lower_leg_fk'+suffix,knee,hock)
        segment('hind_foot_fk'+suffix,hock,ankle)
        set_world('r_toe_fk'+suffix,feet[side]['r_toe_fk'])
        set_world('r_hoof'+suffix,feet[side]['r_hoof'])
        shoulder=rig.matrix_world @ rig.pose.bones['upper_arm_fk'+suffix].head
        # World-space sagittal folding; no roll that points hooves outwards.
        elbow=shoulder+direction((0,-.15,-math.sqrt(1-.15**2)))*length('upper_arm_fk'+suffix)
        folded_wrist=elbow+direction((0,-.9,math.sqrt(1-.9**2)))*length('forearm_fk'+suffix)
        leg=edit.get('forelegs',{}).get(side,{})
        fold=leg.get('fold',edit.get('fold',1.0))
        placement=direction((0,leg.get('back',0)*unit,leg.get('lift',0)*unit))
        wrist=(feet[side]['forefoot_fk'].translation+placement).lerp(folded_wrist,fold)
        # A straight interpolation of world-space wrist targets can leave the
        # reachable sphere as the shoulder rises on its arc. In flight only,
        # lift/retract the wrist to a flexed reachable target, never stretch a
        # segment or move a grounded hoof to conceal a bad stance.
        reach=length('upper_arm_fk'+suffix)+length('forearm_fk'+suffix)
        requested_distance=(wrist-shoulder).length
        wrist_adjustment=0.
        if fold>1e-6 and requested_distance>reach*.992:
            wrist_adjustment=requested_distance-reach*.992
            if wrist_adjustment>.12*unit:
                raise ValueError(f'SUPPORT_FLIGHT_PATH_TOO_FAR frame={frame} side={side} adjustment={wrist_adjustment:.6f}')
            wrist=shoulder+(wrist-shoulder).normalized()*reach*.992
        distance=(wrist-shoulder).length
        if not abs(length('upper_arm_fk'+suffix)-length('forearm_fk'+suffix))+1e-6<distance<reach-1e-6:
            raise ValueError(f'SUPPORT_FORE_REACH frame={frame} side={side} fold={fold:.6f} distance={distance:.6f} reach={reach:.6f}')
        elbow=Vector(bend_joint(list(shoulder),list(wrist),length('upper_arm_fk'+suffix),
                    length('forearm_fk'+suffix),list(direction((0,1,0)))))
        down=(feet[side]['f_toe_fk'].translation-feet[side]['forefoot_fk'].translation).normalized()
        down=down.lerp(direction((0,.15,-math.sqrt(1-.15**2))),fold).normalized()
        fetlock=wrist+down*length('forefoot_fk'+suffix)
        segment('upper_arm_fk'+suffix,shoulder,elbow)
        segment('forearm_fk'+suffix,elbow,wrist)
        segment('forefoot_fk'+suffix,wrist,fetlock)
        toe=feet[side]['f_toe_fk'].copy(); toe.translation=fetlock
        toe = Matrix.Translation(fetlock) @ Quaternion(direction((1,0,0)), .25*fold).to_matrix().to_4x4() @ Matrix.Translation(-fetlock) @ toe
        set_world('f_toe_fk'+suffix,toe)
        hoof=toe @ feet[side]['f_toe_fk'].inverted() @ feet[side]['f_hoof']
        set_world('f_hoof'+suffix,hoof)
        evidence.append({'side':side,'hip':list(start),'stifle':list(knee),'hock':list(hock),'fetlock':list(ankle),
            'flight_wrist_adjustment':wrist_adjustment,'fore_shoulder':list(shoulder),'fore_elbow':list(elbow),
            'fore_carpus':list(wrist),'fore_fetlock':list(fetlock),
            'fore_fold':fold,'fore_placement':list(placement),
            'fore_visible_hoof':list(rig.matrix_world @ rig.pose.bones['DEF-f_hoof'+suffix].head),
            'support_target':list(feet[side]['r_hoof'].translation),
            'visible_hoof':list(rig.matrix_world @ rig.pose.bones['DEF-r_hoof'+suffix].head)})
    # Independent neck base and poll; the head is not a rigid torso extension.
    for name, angle in (('neck',edit['neck_pitch']),('head',edit['poll_pitch'])):
        b=rig.pose.bones[name]; start=rig.matrix_world @ b.head
        m=(Quaternion(direction((1,0,0)),angle).to_matrix() @ (base_world.to_3x3() @ b.bone.matrix_local.to_3x3())).to_4x4()
        m.translation=start; set_world(name,m)
    scene.frame_set(frame); bpy.context.view_layer.update()
    return evidence
