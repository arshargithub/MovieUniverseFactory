"""Authored coordinated rider on retained source gait, not biomechanical capture."""
import json
import math
from pathlib import Path
import numpy as np


def hinge_point(root,target,pole,a,b):
    root,target,pole=map(lambda p:np.asarray(p,dtype=float),(root,target,pole))
    axis=target-root;distance=float(np.linalg.norm(axis))
    if not abs(a-b)+1e-6<distance<a+b-1e-6:raise ValueError('Unreachable fixed-length limb target')
    axis/=distance;side=pole-root;side-=axis*np.dot(side,axis)
    length=float(np.linalg.norm(side))
    if length<1e-7:raise ValueError('Ambiguous limb bend plane')
    side/=length;along=(a*a-b*b+distance*distance)/(2*distance)
    return root+axis*along+side*math.sqrt(max(0,a*a-along*along))


def limb(rig,upper,lower,end,target,pole,orientation):
    import bpy
    from mathutils import Vector
    a=rig.pose.bones[upper];b=rig.pose.bones[lower];tip=rig.pose.bones[end]
    root=a.head.copy();joint=b.head.copy();oldtip=tip.head.copy()
    middle=Vector(hinge_point(root,target,pole,(joint-root).length,(oldtip-joint).length))
    for name,destination in ((upper,middle),(lower,Vector(target))):
        bone=rig.pose.bones[name]
        old=(bone.tail-bone.head).normalized();direction=(destination-bone.head).normalized()
        matrix=old.rotation_difference(direction).to_matrix().to_4x4()@bone.matrix
        matrix.translation=bone.head;bone.matrix=matrix;bpy.context.view_layer.update()
    error=(tip.head-Vector(target)).length
    if error>.008:raise ValueError('Limb target residual above 1mm: '+upper+' '+str(error))
    matrix=orientation.copy();matrix.translation=tip.head;tip.matrix=matrix;bpy.context.view_layer.update()
    return error


def animate_gallop(rig,contacts):
    import bpy
    from mathutils import Matrix,Quaternion,Vector
    from wardrobe_riding_fit import riding_pose
    from wardrobe_refinement import neutral
    from wardrobe_motion178_controls import render_geometry_paused
    from wardrobe185_motion import schedule
    saddles=contacts['saddle_matrices'];bits=contacts['bit_points']
    if saddles.shape!=(144,4,4) or bits.shape!=(144,2,3):raise ValueError('Unexpected contact clock')
    records=[]
    with render_geometry_paused():
        rig.animation_data_clear();riding_pose(rig,1)
        for name,angle in (('MF185_neck',-18),('MF185_head',-12)):
            rig.pose.bones[name].rotation_mode='QUATERNION';rig.pose.bones[name].rotation_quaternion=Quaternion((1,0,0),math.radians(angle))
        bpy.context.view_layer.update()
        goals={b.name:b.matrix_basis.decompose() for b in rig.pose.bones}
        points={b.name:b.head.copy() for b in rig.pose.bones}
        orientations={b.name:b.matrix.copy() for b in rig.pose.bones}
        inverse=rig.matrix_world.inverted().to_3x3()
        neutral(rig);identity=Quaternion((1,0,0,0))
        for frame in range(1,361):
            bpy.context.scene.frame_set(frame);phase=schedule(frame)
            for bone in rig.pose.bones:
                t=phase['legs'] if bone.name.startswith(('thigh.','shin.','foot.','toe.')) else phase['lean']
                loc,rot,scale=goals[bone.name];bone.rotation_mode='QUATERNION'
                bone.location=loc*t;bone.rotation_quaternion=identity.slerp(rot,t);bone.scale=Vector((1,1,1)).lerp(scale,t)
            row={'frame':frame,'limb_residuals_native':{}}
            if frame>=217:
                f=frame-217;delta=inverse@Vector(saddles[f,:3,3]-saddles[0,:3,3])
                rig.pose.bones['pelvis'].location+=delta*.5
                # Modest torso effort follows source saddle height, not an
                # unrelated sinusoidal clock. Neck keeps forward attention.
                angle=math.radians(1.5)*float(delta.z/.6)
                chest=rig.pose.bones['chest'];chest.rotation_quaternion=Quaternion((1,0,0),angle)@chest.rotation_quaternion
                bpy.context.view_layer.update()
                for j,side in enumerate(('L','R')):
                    leg_target=points['foot.'+side]+delta
                    pole=points['shin.'+side]+delta*.5
                    row['limb_residuals_native']['leg.'+side]=limb(rig,'thigh.'+side,'shin.'+side,'foot.'+side,leg_target,pole,orientations['foot.'+side])
                    bit_delta=inverse@Vector(bits[f,j]-bits[0,j])
                    hand_target=points['hand.'+side]+delta+.45*(bit_delta-delta)
                    pole=points['forearm.'+side]+delta*.5
                    row['limb_residuals_native']['arm.'+side]=limb(rig,'upperarm.'+side,'forearm.'+side,'hand.'+side,hand_target,pole,orientations['hand.'+side])
                row['saddle_delta_native']=list(delta)
            for bone in rig.pose.bones:
                for prop in ('location','rotation_quaternion','scale'):bone.keyframe_insert(data_path=prop,frame=frame)
            records.append(row)
        # Dense authored per-frame poses: avoid Bezier time overshoot.
        action=rig.animation_data.action
        for slot in action.slots:
            for layer in action.layers:
                for strip in layer.strips:
                    bag=strip.channelbag(slot)
                    if bag:
                        for curve in bag.fcurves:
                            for key in curve.keyframe_points:key.interpolation='LINEAR'
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        if max(abs(b.matrix_basis[i][j]-Matrix.Identity(4)[i][j]) for b in rig.pose.bones for i in range(4) for j in range(4))>1e-5:raise ValueError('Gallop pre-roll starts out of neutral')
    return records


def preview(out):
    import bpy
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe_riding_fit import fit_render
    scene_path=BASE/'wardrobe185-motionreview03/diagnostic.blend'
    horse_path=BASE/'wardrobe185-horsecache01/horse-library.blend'
    contacts_path=horse_path.parent/'contacts.npz'
    for path,sha in ((scene_path,'0f128ba60947d4451f7e0bbaa3a5f6f275173702e3d4bddd245cef73d2310bd7'),
        (horse_path,'8bccbbf45000cb61b8d50f014ff9db13973c97dd122b35b6bc6f77827e9e97a7'),
        (contacts_path,'15c434d960df8f9720b81d1d7d044ef0a29bca309631f310c7e1ba996de590c9')):
        if path.is_symlink() or digest(path)!=sha:raise ValueError('Riding dependency changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(contacts_path,allow_pickle=False) as d:contacts={n:d[n] for n in d.files}
    bpy.ops.wm.open_mainfile(filepath=str(scene_path),load_ui=False,use_scripts=False)
    check_protected();scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    ob=bpy.data.objects['MF185_moving_shawl'];ob.hide_render=True;ob.hide_viewport=True
    with bpy.data.libraries.load(str(horse_path),link=False) as (available,loaded):
        loaded.objects=[n for n in available.objects if n.startswith('MF185_gait_')]
    if len(loaded.objects)!=10:raise ValueError('Incomplete cached horse assembly')
    for ob in loaded.objects:scene.collection.objects.link(ob)
    records=animate_gallop(rig,contacts)
    (out/'kinematics.json').write_text(json.dumps(records,indent=2)+'\n')
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    for frame in (217,220,223,226):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for angle,label in ((90,'side'),(35,'quarter')):
            fit_render(out,label+'-%03d'%frame,angle,(0,-1.8,-8),32.,(720,540))
    check_protected()
    # Small rig library for the corresponding collision/cloth replay. It is
    # a diagnostic output, not a selected character or accepted performance.
    bpy.data.libraries.write(str(out/'rider-rig.blend'),{rig},fake_user=True,compress=True)
    (out/'result.json').write_text(json.dumps({'protected_local_data_exact':True,'visual_gate':'NOT_RUN',
        'cloth':'NOT_RUN for changed gallop; intentionally hidden','contacts':'Numeric limb targets only; tack fit pending',
        'rig_sha256':digest(out/'rider-rig.blend')},indent=2)+'\n')
