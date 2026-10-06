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


def comfortable_reach(direction,offsets,length,preferred=.93,reserve=.18):
    """One baseline reach for the whole motion; never per-frame clipping.

    Intersect the full trajectory's reachable intervals before keyframing.
    Preserve a fixed extension reserve for absorption rather than tuning one
    failed pose at a time. The final appearance still requires visual review.
    """
    d=np.asarray(direction,float);o=np.asarray(offsets,float);a=float(d@d)
    if a<=0 or o.ndim!=2 or o.shape[1]!=3 or length<=reserve:raise ValueError('Invalid reach domain')
    b=o@d;c=np.einsum('ij,ij->i',o,o)-(length-reserve)**2
    discriminant=b*b-a*c
    if np.any(discriminant<0):raise ValueError('Hand path has no feasible baseline reach')
    upper=(-b+np.sqrt(discriminant))/a;lower=(-b-np.sqrt(discriminant))/a
    value=min(preferred,float(upper.min()))
    if value<max(.65,float(lower.max())):raise ValueError('Replan rider/hand path instead of excessively shortening reach')
    return value


def limb(rig,upper,lower,end,target,pole,orientation):
    import bpy
    from mathutils import Vector
    a=rig.pose.bones[upper];b=rig.pose.bones[lower];tip=rig.pose.bones[end]
    root=a.head.copy();joint=b.head.copy();oldtip=tip.head.copy()
    try:middle=Vector(hinge_point(root,target,pole,(joint-root).length,(oldtip-joint).length))
    except ValueError as error:
        raise ValueError(str(error)+' '+upper+' frame='+str(bpy.context.scene.frame_current)+
            ' lengths='+str(((joint-root).length,(oldtip-joint).length))+' target_distance='+str((Vector(target)-root).length)) from error
    for name,destination in ((upper,middle),(lower,Vector(target))):
        bone=rig.pose.bones[name]
        old=(bone.tail-bone.head).normalized();direction=(destination-bone.head).normalized()
        matrix=old.rotation_difference(direction).to_matrix().to_4x4()@bone.matrix
        matrix.translation=bone.head;bone.matrix=matrix;bpy.context.view_layer.update()
    error=(tip.head-Vector(target)).length
    if error>.008:raise ValueError('Limb target residual above 1mm: '+upper+' '+str(error))
    matrix=orientation.copy();matrix.translation=tip.head;tip.matrix=matrix;bpy.context.view_layer.update()
    return error


def animate_gallop(rig,contacts,racing=False,grasp=False):
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
        if grasp:
            from wardrobe185_grip import riding_grip
            riding_grip(rig)
        if racing:
            rig.pose.bones['spine'].rotation_euler.x=math.radians(32)
            rig.pose.bones['chest'].rotation_euler.x=math.radians(16)
        for name,angle in (('MF185_neck',-22 if racing else -18),('MF185_head',-22 if racing else -12)):
            rig.pose.bones[name].rotation_mode='QUATERNION';rig.pose.bones[name].rotation_quaternion=Quaternion((1,0,0),math.radians(angle))
        bpy.context.view_layer.update()
        # The old static reach was nearly extended. Reserve elbow flexion for
        # absorption before deriving the complete motion, not per-frame limb
        # stretching or discontinuous target clipping.
        inverse=rig.matrix_world.inverted().to_3x3();reach_record={}
        for j,side in enumerate(('L','R')):
            upper=rig.pose.bones['upperarm.'+side];lower=rig.pose.bones['forearm.'+side];hand=rig.pose.bones['hand.'+side]
            offsets=(bits[:,j]-bits[0,j]-(saddles[:,:3,3]-saddles[0,:3,3]))@np.array(inverse).T*.20
            direction=hand.head-upper.head;length=(lower.head-upper.head).length+(hand.head-lower.head).length
            gain=comfortable_reach(direction,offsets,length)
            target=upper.head+direction*gain
            limb(rig,upper.name,lower.name,hand.name,target,lower.head.copy(),hand.matrix.copy())
            reach_record[side]={'global_reference_gain':gain,'maximum_planned_length':float(np.linalg.norm(np.array(direction)*gain+offsets,axis=1).max()),'limb_length':length,'reserve_native':.18}
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
            if frame==1:row['whole_gait_arm_feasibility']=reach_record
            if frame>=217:
                f=frame-217;delta=inverse@Vector(saddles[f,:3,3]-saddles[0,:3,3])
                bpy.context.view_layer.update()
                pelvis=rig.pose.bones['pelvis'];before=pelvis.matrix.translation.copy()
                # PoseBone.location is bone-local, not rig-space. Apply the
                # measured saddle displacement in the evaluated rig frame.
                matrix=pelvis.matrix.copy();matrix.translation+=delta*.5;pelvis.matrix=matrix
                bpy.context.view_layer.update()
                error=(pelvis.matrix.translation-before-delta*.5).length
                row['pelvis_displacement_error_native']=error
                if error>1e-5:raise ValueError('Pelvis displacement frame mismatch')
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
                    shoulder_delta=rig.pose.bones['upperarm.'+side].head-points['upperarm.'+side]
                    hand_target=points['hand.'+side]+shoulder_delta+.20*(bit_delta-delta)
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


def fit_tack(rig,contacts,out,grasp=False):
    """Kinematic reins and adjustable stirrups, retaining source ring geometry.

    Contacts are authored endpoints, not a force/rope or leather simulation.
    Inspect all contact views and temporal frames before accepting the fit.
    """
    import bpy
    from mathutils import Vector
    from wardrobe_motion178_controls import render_geometry_paused
    from wardrobe_shawl180_cache import cache
    scene=bpy.context.scene;stirrup=bpy.data.objects['MF185_gait_saddle.stirrup']
    bpy.data.objects['MF185_gait_saddle.stirrup.strap'].hide_render=True
    leather=bpy.data.objects['MF_173_tension_harness_1'].data.materials[0]
    reins={};straps={};ring_frames=[];strap_frames={s:[] for s in ('L','R')};records=[]
    for side in ('L','R'):
        data=bpy.data.curves.new('185 rein '+side,'CURVE');data.dimensions='3D';data.bevel_depth=.035;data.bevel_resolution=2
        spline=data.splines.new('POLY');spline.points.add(21 if grasp else 16)
        ob=bpy.data.objects.new('MF185_rein_'+side,data);scene.collection.objects.link(ob);data.materials.append(leather);reins[side]=ob
    with render_geometry_paused():
        stirrup.hide_viewport=False
        boots={side:[o for o in scene.objects if o.name.startswith(('MF_173_work_boot_','MF_173_boot_')) and ('_'+side) in o.name and o.type=='MESH'] for side in ('L','R')}
        for items in boots.values():
            for ob in items:ob.hide_viewport=False
        for frame in range(217,361):
            scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
            ev=stirrup.evaluated_get(deps);m=ev.to_mesh();p=np.array([stirrup.matrix_world@v.co for v in m.vertices]);ev.to_mesh_clear()
            row={'frame':frame,'contacts':{}}
            for j,(side,sign) in enumerate((('L',1),('R',-1))):
                foot=rig.pose.bones['foot.'+side]
                foot_head=rig.matrix_world@foot.head;foot_tail=rig.matrix_world@foot.tail
                target=foot_head+(foot_tail-foot_head).normalized()*.6
                sole=[]
                for ob in boots[side]:
                    ev=ob.evaluated_get(deps);m=ev.to_mesh();sole.extend((ob.matrix_world@v.co).z for v in m.vertices);ev.to_mesh_clear()
                if not sole:raise ValueError('No actual boot sole')
                target.z=min(sole)+.015
                ids=np.where(p[:,0]*sign>0)[0];a=p[ids]
                bottom=a[a[:,2]<a[:,2].min()+.15]
                center=(bottom.min(0)+bottom.max(0))*.5;center[2]=a[:,2].min()+.10
                p[ids]+=np.array(target)-center
                ring_top=Vector(p[ids][np.argmax(p[ids,2])])
                saddle_delta=contacts['saddle_matrices'][frame-217,:3,3]-contacts['saddle_matrices'][0,:3,3]
                anchor=Vector((sign*2.2,.2,-7.6))+Vector(saddle_delta)
                middle=anchor.lerp(ring_top,.5)+Vector((sign*.1,0,0))
                route=[anchor,middle,ring_top];vertices=[]
                for point in route:vertices.extend([list(point+Vector((0,-.08,0))),list(point+Vector((0,.08,0)))])
                strap_frames[side].append(vertices)
                finger_a=rig.pose.bones['MF_fit_finger_0_1.'+side];finger_b=rig.pose.bones['MF_fit_finger_1_1.'+side]
                grip=rig.matrix_world@((finger_a.head+finger_a.tail+finger_b.head+finger_b.tail)/4)
                channel=[]
                if grasp:
                    from wardrobe185_grip import rein_channel
                    channel=rein_channel(rig,side);grip=channel[0]
                bit=Vector(contacts['bit_points'][frame-217,j]);spline=reins[side].data.splines[0]
                for k,point in enumerate(spline.points):
                    if k<=16:
                        t=k/16;v=bit.lerp(grip,t);v.z-=.16*4*t*(1-t)
                    elif k<=19:v=channel[k-16]
                    else:
                        v=channel[-1]+(channel[-1]-channel[-2]).normalized()*(.12*(k-19))
                    point.co=(*v,1);point.keyframe_insert(data_path='co',frame=frame)
                row['contacts'][side]={'bit':list(bit),'grip':list(grip),'sole_height':min(sole),'plate_target':list(target),
                    'stirrup_leather_length_native':(anchor-ring_top).length,'hand_channel':[list(p) for p in channel]}
            ring_frames.append(p);records.append(row)
        for mod in list(stirrup.modifiers):
            if mod.type=='MESH_CACHE':stirrup.modifiers.remove(mod)
        mod=cache(stirrup,np.array(ring_frames),out/'fitted-stirrups.mdd');mod.frame_start=217
        for side,frames in strap_frames.items():
            data=bpy.data.meshes.new('185 adjustable stirrup leather '+side);data.from_pydata(frames[0],[],[(0,1,3,2),(2,3,5,4)]);data.update()
            ob=bpy.data.objects.new('MF185_stirrup_leather_'+side,data);scene.collection.objects.link(ob);data.materials.append(leather)
            mod=cache(ob,np.array(frames),out/('stirrup-leather-'+side+'.mdd'));mod.frame_start=217
            solid=ob.modifiers.new('Leather thickness','SOLIDIFY');solid.thickness=.016
            straps[side]=ob
    (out/'tack-contacts.json').write_text(json.dumps(records,indent=2)+'\n')
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
    racing=out.name.endswith(('riding05','riding06'));grasp=out.name.endswith('riding06')
    try:records=animate_gallop(rig,contacts,racing=racing,grasp=grasp)
    except Exception as error:
        (out/'failure.json').write_text(json.dumps({'frame':scene.frame_current,'error':str(error)},indent=2)+'\n')
        raise
    (out/'kinematics.json').write_text(json.dumps(records,indent=2)+'\n')
    if racing:fit_tack(rig,contacts,out,grasp=grasp)
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    for frame in (217,220,223,226):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for angle,label in ((90,'side'),(35,'quarter')):
            fit_render(out,label+'-%03d'%frame,angle,(0,-1.8,-8),32.,(720,540))
    if racing:
        scene.frame_set(217);bpy.context.view_layer.update()
        for side,angle in (('L',70),('R',290)):
            hand=rig.pose.bones['hand.'+side]
            fit_render(out,'hand-'+side,angle,tuple(rig.matrix_world@hand.head),2.8,(600,600))
    check_protected()
    # Small rig library for the corresponding collision/cloth replay. It is
    # a diagnostic output, not a selected character or accepted performance.
    bpy.data.libraries.write(str(out/'rider-rig.blend'),{rig},fake_user=True,compress=True)
    (out/'result.json').write_text(json.dumps({'protected_local_data_exact':True,'visual_gate':'NOT_RUN',
        'cloth':'NOT_RUN for changed gallop; intentionally hidden','contacts':'Authored stirrup/bit/hand contacts; rendered fit and complete temporal gate remain separate' if racing else 'Tack fit pending',
        'rig_sha256':digest(out/'rider-rig.blend')},indent=2)+'\n')
