"""Source-governed secondary pectoral insertion proof, never a primary pose edit.

Existing leaf controls only. Body geometry, skin weights, primary curves and
joint matrices are retained. Native anatomical quality is a separate verdict.
"""
import json
import numpy as np

BONES=['DEF-breast.L','DEF-breast.R']
FRAMES=[272,276,283,293,306,315,323,333,339,346,358,367,370]

def validate(e):
    if not isinstance(e,dict) or set(e)!={'kind','target','strength'} or e['kind']!='mounted_articulation387' or e['target']!='horse':raise ValueError('ARTICULATION387_FIELDS')
    if type(e['strength']) not in (int,float) or not np.isfinite(e['strength']) or not 0<=e['strength']<=1:raise ValueError('ARTICULATION387_STRENGTH')
    return e

def insertion_solution(head,tail,humeral_insertion,strength):
    h,t,p=map(lambda v:np.asarray(v,dtype=float),(head,tail,humeral_insertion))
    if any(x.shape!=(3,) or not np.isfinite(x).all() for x in [h,t,p]) or not np.isfinite(strength) or not 0<=strength<=1:raise ValueError('ARTICULATION387_ENDPOINT_INPUT')
    a=t-h;goal=t+(p-t)*strength;b=goal-h;la=np.linalg.norm(a);lb=np.linalg.norm(b)
    if not .05<=la<=.8 or not .05<=lb<=.8:raise ValueError('ARTICULATION387_LENGTH')
    a/=la;b/=lb;dot=float(np.clip(a@b,-1,1))
    if dot<-.999999:raise ValueError('ARTICULATION387_ANTIPODAL')
    q=np.r_[1+dot,np.cross(a,b)];q/=np.linalg.norm(q);scale=lb/la
    if not .2<=scale<=1.25:raise ValueError('ARTICULATION387_SCALE')
    return q,float(scale),goal

def run(bpy,out,e,helpers):
    from mathutils import Quaternion,Vector
    validate(e);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];scene=bpy.context.scene
    if any(horse.get(n) for n in ['cache376','weights386','bind_preserve386','support386','muscle386','articulation387']):raise ValueError('ARTICULATION387_SOURCE')
    keys=horse.data.shape_keys.key_blocks
    if [k.name for k in keys]!=['Basis','corr.neck','corr.chin','corr.neck.2'] or len(horse.data.vertices)!=22514:raise ValueError('ARTICULATION387_KEYS')
    if not rig.animation_data or not rig.animation_data.action:raise ValueError('ARTICULATION387_ACTION')
    action=rig.animation_data.action;muscle=helpers('anatomy_muscle386');paths=[]
    for n in BONES:
        pb=rig.pose.bones[n]
        if pb.children or pb.constraints:raise ValueError('ARTICULATION387_NOT_LEAF')
        paths.extend([pb.path_from_id('rotation_quaternion'),pb.path_from_id('scale')])
        forbidden=paths+[pb.path_from_id('rotation_euler'),pb.path_from_id('rotation_axis_angle')]
        if any(fc.data_path in forbidden for fc in muscle.curves(action)) or any(fc.data_path in forbidden for fc in rig.animation_data.drivers):raise ValueError('ARTICULATION387_EXISTING_CHANNEL')
    for pb in rig.pose.bones:
        if pb.name not in BONES and any(getattr(co,'target',None)==rig and getattr(co,'subtarget','') in BONES for co in pb.constraints):raise ValueError('ARTICULATION387_PRIMARY_DEPENDENT')
    for obj in bpy.data.objects:
        if obj==rig:continue
        stacks=[obj.constraints]+([pb.constraints for pb in obj.pose.bones] if obj.type=='ARMATURE' else [])
        if any(getattr(co,'target',None)==rig and getattr(co,'subtarget','') in BONES for stack in stacks for co in stack):raise ValueError('ARTICULATION387_FOREIGN_DEPENDENT')
    original_modes={n:rig.pose.bones[n].rotation_mode for n in BONES};rest_matrices={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones};geometry=helpers('nihang_prep367').frozen(bpy);actions=helpers('nihang_padsolve370').actions(bpy)
    names=[pb.name for pb in rig.pose.bones if pb.name not in BONES];saved=(scene.frame_current,scene.frame_subframe);raw=np.array([v.co[:] for v in horse.data.vertices],np.float32);gn,w=helpers('anatomy_bind386').weights(horse);affected=w[:,[gn.index(n) for n in BONES]].sum(1)>0
    before,mat_before=muscle.capture(bpy,horse,rig,names,helpers)
    # Gather all targets before writing any channel; new keys cannot feed back
    # into later source samples. Keep exact original293and boundary states.
    rows=[]
    for f,scale_old in muscle.contraction_keys(1.):
        scene.frame_set(f);bpy.context.view_layer.update();phase=1-scale_old
        for side,n in zip(['L','R'],BONES):
            pb=rig.pose.bones[n];arm=rig.pose.bones['DEF-upper_arm.'+side]
            # Local tissue handle inserts near proximal humerus, not distal hoof.
            insertion=arm.head.lerp(arm.tail,.5)
            q,scale,goal=insertion_solution(pb.head,pb.tail,insertion,e['strength']*phase)
            current=pb.matrix.to_quaternion();local=current.inverted()@Quaternion(q.tolist())@current
            rows.append(dict(frame=f,bone=n,quaternion=list(local),scale=scale,source_head=list(pb.head),source_tail=list(pb.tail),insertion=list(insertion),goal=goal.tolist()))
    if e['strength']:
        for row in rows:
            pb=rig.pose.bones[row['bone']];pb.rotation_mode='QUATERNION';pb.rotation_quaternion=row['quaternion'];pb.scale[1]=row['scale'];pb.keyframe_insert(data_path='rotation_quaternion',frame=row['frame']);pb.keyframe_insert(data_path='scale',index=1,frame=row['frame'])
        for fc in muscle.curves(action):
            if fc.data_path in paths:
                fc.extrapolation='CONSTANT'
                for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
    endpoint_audit=[]
    if e['strength']:
        for row in rows:
            scene.frame_set(row['frame']);bpy.context.view_layer.update();pb=rig.pose.bones[row['bone']]
            error=float(np.linalg.norm(np.array(pb.tail)-row['goal']));endpoint_audit.append(dict(frame=row['frame'],bone=row['bone'],actual_tail=list(pb.tail),goal=row['goal'],error=error))
        (out/'articulation387-endpoints.json').write_text(json.dumps(endpoint_audit,indent=2)+'\n')
        if max(x['error'] for x in endpoint_audit)>2e-5:raise ValueError('ARTICULATION387_ENDPOINT_IMPLEMENTATION')
    after,mat_after=muscle.capture(bpy,horse,rig,names,helpers)
    outside=float(abs(after[:,~affected]-before[:,~affected]).max());primary=float(abs(mat_after-mat_before).max());distal=raw[:,2]<.95;distal_error=float(abs(after[:,distal]-before[:,distal]).max());neutral=float(abs(after[muscle.FRAMES.index(283)]-before[muscle.FRAMES.index(283)]).max());boundary=float(abs(after[[0,-1]]-before[[0,-1]]).max());maximum=float(np.linalg.norm(after-before,axis=2).max())
    buffer=(raw[:,2]>=.95)&(raw[:,2]<=1.)&affected;buffer_error=float(np.linalg.norm(after[:,buffer]-before[:,buffer],axis=2).max())
    metrics=dict(outside_error=outside,primary_matrix_error=primary,true_distal_error=distal_error,neutral_error=neutral,boundary_error=boundary,max_posed_delta=maximum,upper_elbow_buffer_vertices=int(buffer.sum()),upper_elbow_buffer_error=buffer_error)
    (out/'articulation387-preflight.json').write_text(json.dumps(metrics,indent=2)+'\n')
    np.savez_compressed(out/'articulation387.npz',raw=raw,affected=affected,pose_before=before,pose_after=after,rig_before=mat_before,rig_after=mat_after,frames=np.array(muscle.FRAMES))
    # Explicit structural387policy: the eight pectoral-dominant upper-elbow
    # connectors may move up to15cm; true lowerlegs and all primary joints exact.
    # This does not mutate the stricter old386operators' policy.
    if max(outside,distal_error,neutral,boundary)>2e-5 or primary>1e-7 or buffer_error>.15 or maximum>.4:raise ValueError('ARTICULATION387_PRESERVATION')
    ignored={action.name:paths} if e['strength'] else {}
    if actions!=helpers('nihang_padsolve370').actions(bpy,ignore=ignored) or geometry!=helpers('nihang_prep367').frozen(bpy) or rest_matrices!={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones}:raise ValueError('ARTICULATION387_ORIGINAL_DRIFT')
    _,wa=helpers('anatomy_bind386').weights(horse)
    if not np.array_equal(w,wa):raise ValueError('ARTICULATION387_WEIGHT_DRIFT')
    if e['strength']:horse['articulation387']=True
    else:
        for n,mode in original_modes.items():rig.pose.bones[n].rotation_mode=mode
    scene.frame_set(saved[0],subframe=saved[1]);bpy.context.view_layer.update()
    report=dict(strength=e['strength'],metrics=metrics,targets=rows,endpoint_audit=endpoint_audit,new_paths=paths if e['strength'] else [],old_geometry_keys_weights_bones_primary_actions_exact=True,scope='Existingsecondaryleafmuscleinsertion proof, not a primarymotion edit. Original source retained; native anatomy/contact/fullspeed remain separate and unqualified.')
    (out/'articulation387.json').write_text(json.dumps(report,indent=2)+'\n');return report
