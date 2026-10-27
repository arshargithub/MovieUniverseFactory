"""Neutral-calibrated rigid secondary pectoral supports, no new primary motion.

Two exact-name single-segment deformation bones copy existing upper-arm pose
transforms. Rest calibration preserves breast deformation at283. Original
motion bones, actions, rest geometry and correctives remain unchanged.
"""
import json
import numpy as np

KIND='mounted_anatomy386_rigid_support'
NAMES=['MF386 pectoral rigid.L','MF386 pectoral rigid.R']

def validate(e):
    if set(e)!={'kind','target','strength'} or e['kind'] not in {KIND,'mounted_anatomy386_dominant_support'} or e['target']!='horse':raise ValueError('SUPPORT386_FIELDS')
    if type(e['strength']) not in (int,float) or not np.isfinite(e['strength']) or not 0<=e['strength']<=.7:raise ValueError('SUPPORT386_STRENGTH')
    return e

def calibrated_rest(breast_pose,breast_rest,arm_pose):
    a,b,c=map(lambda x:np.asarray(x,dtype=float),(breast_pose,breast_rest,arm_pose))
    if any(x.shape!=(4,4) or not np.isfinite(x).all() for x in (a,b,c)):raise ValueError('SUPPORT386_MATRIX')
    return np.linalg.inv(a@np.linalg.inv(b))@c

def qualify_roundtrip(zero_before,zero_after,failed_before,failed_after):
    arrays=[np.asarray(x) for x in (zero_before,zero_after,failed_before,failed_after)]
    if len({x.shape for x in arrays})!=1 or not all(np.isfinite(x).all() for x in arrays):raise ValueError('SUPPORT386_ROUNDTRIP_DATA')
    error=float(abs((arrays[1]-arrays[0])-(arrays[3]-arrays[2])).max())
    if error>2e-6:raise ValueError('SUPPORT386_ROUNDTRIP_NOT_EXPLANATORY')
    return error

def transfer(rest,w,names,edges,skin,strength,remap,*,dominant=False):
    candidate,mask=remap(rest,w,names,edges,strength,skin,core=True,dominant=dominant)
    result=np.pad(w,((0,0),(0,2)))
    for j,side in enumerate(['L','R']):
        col=names.index('DEF-breast.'+side);take=w[:,col]-candidate[:,col]
        result[:,col]-=take;result[:,-2+j]=take
    if result.min()<0 or np.max(abs(result.sum(1)-w.sum(1)))>2e-6:raise ValueError('SUPPORT386_WEIGHT_MASS')
    return result,mask

def samples(bpy,horse,rig,names,helpers):
    scene=bpy.context.scene;saved=(scene.frame_current,scene.frame_subframe);mods=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF'];poses=[];mat=[]
    try:
        for m,_ in mods:m.show_viewport=False
        for f in [283,333,339]:
            scene.frame_set(f);bpy.context.view_layer.update();poses.append(helpers('nihang_pose376').cage(bpy,horse));mat.append(np.array([[list(row) for row in horse.matrix_world]]+[[list(row) for row in rig.matrix_world@rig.pose.bones[n].matrix] for n in names]))
    finally:
        for m,v in mods:m.show_viewport=v
        scene.frame_set(saved[0],subframe=saved[1]);bpy.context.view_layer.update()
    return np.array(poses),np.array(mat)

def run(bpy,out,e,helpers):
    validate(e);from mathutils import Matrix
    horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];scene=bpy.context.scene
    if any(horse.get(k) for k in ['cache376','weights386','bind_preserve386','support386']):raise ValueError('SUPPORT386_SOURCE')
    if any(n in rig.data.bones or n in horse.vertex_groups for n in NAMES):raise ValueError('SUPPORT386_REAPPLY')
    keys=horse.data.shape_keys.key_blocks
    if [k.name for k in keys]!=['Basis','corr.neck','corr.chin','corr.neck.2'] or len(horse.data.vertices)!=22514:raise ValueError('SUPPORT386_KEYS')
    if any((m.show_viewport or m.show_render) and m.type not in {'ARMATURE','SUBSURF'} for m in horse.modifiers):raise ValueError('SUPPORT386_MODIFIERS')
    bone_names=[b.name for b in rig.pose.bones];bone_rest={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones}
    before_keys=np.array([[v.co[:] for v in k.data] for k in keys],np.float32);raw=np.array([v.co[:] for v in horse.data.vertices],np.float32);rest=before_keys[0];names,w=helpers('anatomy_bind386').weights(horse);edges=np.array([ed.vertices[:] for ed in horse.data.edges]);skin=helpers('anatomy_domain386').main_skin(edges,len(rest))
    geom=helpers('nihang_prep367').frozen(bpy);actions=helpers('nihang_padsolve370').actions(bpy);before,mat_before=samples(bpy,horse,rig,bone_names,helpers);saved=(scene.frame_current,scene.frame_subframe);old_active=bpy.context.view_layer.objects.active
    target,mask=transfer(rest,w,names,edges,skin,e['strength'],helpers('anatomy_weights386').remap,dominant=e['kind']=='mounted_anatomy386_dominant_support');selected=np.any(target[:,:len(names)]!=w,axis=1)
    calibrations={}
    scene.frame_set(283);bpy.context.view_layer.update()
    if e['strength']:
        for side in ['L','R']:
            breast=rig.pose.bones['DEF-breast.'+side];arm=rig.pose.bones['DEF-upper_arm.'+side]
            if breast.bone.bbone_segments!=1:raise ValueError('SUPPORT386_BREAST_NOT_RIGID')
            calibrations[side]=calibrated_rest(breast.matrix,breast.bone.matrix_local,arm.matrix)
    # Zero executes the identical edit-mode roundtrip, without adding bones.
    # This explicitly measures Blender's original-bone reconstruction noise.
    if bpy.context.object and bpy.context.object.mode!='OBJECT':raise ValueError('SUPPORT386_OBJECT_MODE_REQUIRED')
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    try:
        if e['strength']:
            for side,name in zip(['L','R'],NAMES):
                b=rig.data.edit_bones.new(name);b.head=(0,0,0);b.tail=(0,.25,0);b.matrix=Matrix(calibrations[side].tolist());b.use_deform=True
    finally:bpy.ops.object.mode_set(mode='OBJECT')
    if e['strength']:
        for side,name in zip(['L','R'],NAMES):
            rig.data.bones[name].bbone_segments=1;pb=rig.pose.bones[name];con=pb.constraints.new('COPY_TRANSFORMS');con.target=rig;con.subtarget='DEF-upper_arm.'+side;con.owner_space='POSE';con.target_space='POSE';con.mix_mode='REPLACE'
            horse.vertex_groups.new(name=name)
        for j,g in enumerate(horse.vertex_groups):
            old=w[:,j] if j<len(names) else np.zeros(len(w))
            for i in np.flatnonzero(target[:,j]!=old):
                value=float(target[i,j])
                if value<=1e-10:g.remove([int(i)])
                else:g.add([int(i)],value,'REPLACE')
    bpy.context.view_layer.objects.active=old_active;bpy.context.view_layer.update()
    after,mat_after=samples(bpy,horse,rig,bone_names,helpers);neutral_error=float(np.linalg.norm(after[0]-before[0],axis=1).max())
    original_rest_error=max(float(abs(np.asarray(bone_rest[n])-np.asarray(rig.data.bones[n].matrix_local)).max()) for n in bone_names)
    preflight=dict(neutral_error=neutral_error,original_rest_error=original_rest_error,original_motion_matrix_error=float(abs(mat_after-mat_before).max()),outside_error=float(abs(after[:,~selected]-before[:,~selected]).max()),max_posed_delta=float(np.linalg.norm(after-before,axis=2).max()))
    (out/'anatomy386-support-preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
    np.savez_compressed(out/'anatomy386-support-preflight.npz',pose_before=before,pose_after=after,rig_before=mat_before,rig_after=mat_after)
    # Explicit new-operator precision policy, independent of the unchanged
    # legacy1e-7 guard. Controller review must qualify the actual zero roundtrip
    # against222 before the nonzero candidate is allowed, then check cumulative
    # error against the original zero source. This is never a visual waiver.
    if max(preflight['outside_error'],preflight['original_motion_matrix_error'],original_rest_error)>1e-4:raise ValueError('SUPPORT386_PRECISION_CAP')
    pres=dict(poses=[283,333,339],outside_surface_max_error=preflight['outside_error'],skeleton_and_world_max_error=preflight['original_motion_matrix_error'],precision_cap=.0001,scope='Numerical edit-roundtrip policy only; must independently calibrate zero and cumulative original-source error. Not bit-exact or an art/contact approval.')
    if neutral_error>.0001:raise ValueError('SUPPORT386_NEUTRAL_DRIFT')
    if np.linalg.norm(after-before,axis=2).max()>.3:raise ValueError('SUPPORT386_POSED_BOUND')
    if geom!=helpers('nihang_prep367').frozen(bpy) or actions!=helpers('nihang_padsolve370').actions(bpy) or not np.array_equal(before_keys,np.array([[v.co[:] for v in k.data] for k in keys],np.float32)):raise ValueError('SUPPORT386_SOURCE_DRIFT')
    _,stored=helpers('anatomy_bind386').weights(horse);expected=target if e['strength'] else w
    if stored.shape!=expected.shape or np.max(abs(stored-expected))>2e-7:raise ValueError('SUPPORT386_STORED_WEIGHTS')
    horse.data.calc_loop_triangles();faces=np.array([t.vertices[:] for t in horse.data.loop_triangles]);faces=faces[np.all(skin[faces],axis=1)];affected=np.any(selected[faces],axis=1);cross=helpers('anatomy_bind386').crossing_pairs;surface=[]
    if e['strength']:
        for i,f in enumerate([283,333,339]):
            old=cross(before[i],faces,affected);new=cross(after[i],faces,affected);surface.append(dict(frame=f,before=len(old),after=len(new),introduced=len(new-old)))
    np.savez_compressed(out/'anatomy386-support.npz',rest=rest,raw=raw,weights_before=w,weights_after=stored,selected=selected,pose_before=before,pose_after=after,rig_before=mat_before,rig_after=mat_after)
    report=dict(strength=e['strength'],neutral_error=neutral_error,original_pose_preservation=pres,original_rest_error=original_rest_error,original_bone_count=len(bone_names),new_bones=NAMES if e['strength'] else [],changed_vertices=int(selected.sum()),source_geometry_keys_actions_exact=True,surface_diagnostics=surface,calibrated_rest={k:v.tolist() for k,v in calibrations.items()},scope='Secondary rigid support causal candidate/control only. Original primary motion retained within explicit calibrated precision, not bit-exact. Cage/contact/anatomical/consumer/AV verdicts separate and known failures remain open.')
    if e['strength']:horse['support386']=True
    scene.frame_set(saved[0],subframe=saved[1]);bpy.context.view_layer.update();(out/'anatomy386-support.json').write_text(json.dumps(report,indent=2)+'\n');return report
