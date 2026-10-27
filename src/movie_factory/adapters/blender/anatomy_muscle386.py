"""Fixed secondary pectoral contraction, preserving primary horse performance.

Only two existing leaf deformation bones receive new scale-Y channels. No bone
edit mode, new bones, mesh/weight edits, pose cache or original-curve overwrite.
"""
import json
import numpy as np
BONES=['DEF-breast.L','DEF-breast.R']
FRAMES=[272,276,283,306,315,323,333,339,346,358,367,370]

def validate(e):
    if set(e)!={'kind','target','amount'} or e['kind']!='mounted_anatomy386_muscle_contract' or e['target']!='horse':raise ValueError('MUSCLE386_FIELDS')
    if type(e['amount']) not in (int,float) or not np.isfinite(e['amount']) or not 0<=e['amount']<=.4:raise ValueError('MUSCLE386_AMOUNT')
    return e

def contraction_keys(amount):
    return [(f,1-amount*v) for f,v in [(276,0),(293,0),(306,.25),(315,.65),(323,.95),(333,1),(339,1),(346,.5),(358,0),(367,0)]]

def curves(action):
    result=[]
    if hasattr(action,'fcurves'):
        try:result=list(action.fcurves)
        except RuntimeError:pass
    if not result:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in getattr(strip,'channelbags',[]):result.extend(bag.fcurves)
    return result

def capture(bpy,horse,rig,names,helpers):
    scene=bpy.context.scene;saved=(scene.frame_current,scene.frame_subframe);mods=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF'];pose=[];mat=[]
    try:
        for m,_ in mods:m.show_viewport=False
        for f in FRAMES:
            scene.frame_set(f);bpy.context.view_layer.update();pose.append(helpers('nihang_pose376').cage(bpy,horse));mat.append(np.array([[list(row) for row in horse.matrix_world]]+[[list(row) for row in rig.matrix_world@rig.pose.bones[n].matrix] for n in names]))
    finally:
        for m,v in mods:m.show_viewport=v
        scene.frame_set(saved[0],subframe=saved[1]);bpy.context.view_layer.update()
    return np.array(pose),np.array(mat)

def run(bpy,out,e,helpers):
    validate(e);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];scene=bpy.context.scene
    if any(horse.get(n) for n in ['cache376','weights386','bind_preserve386','support386','muscle386']):raise ValueError('MUSCLE386_SOURCE')
    keys=horse.data.shape_keys.key_blocks
    if [k.name for k in keys]!=['Basis','corr.neck','corr.chin','corr.neck.2'] or len(horse.data.vertices)!=22514:raise ValueError('MUSCLE386_KEYS')
    if not rig.animation_data or not rig.animation_data.action:raise ValueError('MUSCLE386_ACTION_REQUIRED')
    action=rig.animation_data.action;paths=[rig.pose.bones[n].path_from_id('scale') for n in BONES]
    if any(fc.data_path in paths for fc in curves(action)) or any(d.data_path in paths for d in rig.animation_data.drivers):raise ValueError('MUSCLE386_EXISTING_CHANNEL')
    for n in BONES:
        pb=rig.pose.bones[n]
        if pb.children or pb.constraints:raise ValueError('MUSCLE386_NOT_LEAF_DEFORM')
    for pb in rig.pose.bones:
        if pb.name not in BONES and any(getattr(co,'target',None)==rig and getattr(co,'subtarget','') in BONES for co in pb.constraints):raise ValueError('MUSCLE386_PRIMARY_DEPENDENT')
    for obj in bpy.data.objects:
        if obj==rig:continue
        stacks=[obj.constraints]+([pb.constraints for pb in obj.pose.bones] if obj.type=='ARMATURE' else [])
        if any(getattr(co,'target',None)==rig and getattr(co,'subtarget','') in BONES for stack in stacks for co in stack):raise ValueError('MUSCLE386_FOREIGN_DEPENDENT')
    names=[pb.name for pb in rig.pose.bones if pb.name not in BONES];rest_matrices={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones};geometry=helpers('nihang_prep367').frozen(bpy);actions=helpers('nihang_padsolve370').actions(bpy)
    raw=np.array([v.co[:] for v in horse.data.vertices],np.float32);group_names,w=helpers('anatomy_bind386').weights(horse);breast=w[:,[group_names.index(n) for n in BONES]].sum(1);affected=breast>0
    if not affected.any() or raw[affected,2].min()<.95:raise ValueError('MUSCLE386_WEIGHT_DOMAIN')
    before,mat_before=capture(bpy,horse,rig,names,helpers)
    if e['amount']:
        for n in BONES:
            pb=rig.pose.bones[n]
            for f,v in contraction_keys(e['amount']):pb.scale[1]=v;pb.keyframe_insert(data_path='scale',index=1,frame=f)
        for fc in curves(action):
            if fc.data_path in paths:
                if fc.array_index!=1:raise ValueError('MUSCLE386_EXTRA_CHANNEL')
                fc.extrapolation='CONSTANT'
                for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
    after,mat_after=capture(bpy,horse,rig,names,helpers);outside=float(abs(after[:,~affected]-before[:,~affected]).max());primary=float(abs(mat_after-mat_before).max());distal=raw[:,2]<.95;distal_error=float(abs(after[:,distal]-before[:,distal]).max());buffer=(raw[:,2]>=.95)&(raw[:,2]<=1.)&affected;buffer_error=float(np.linalg.norm(after[:,buffer]-before[:,buffer],axis=2).max());neutral_index=FRAMES.index(283);neutral_error=float(abs(after[neutral_index]-before[neutral_index]).max());maximum=float(np.linalg.norm(after-before,axis=2).max())
    boundary_error=float(abs(after[[0,-1]]-before[[0,-1]]).max())
    metrics=dict(boundary_error=boundary_error,outside_error=outside,primary_matrix_error=primary,true_distal_error=distal_error,upper_elbow_buffer_vertices=int(buffer.sum()),upper_elbow_buffer_error=buffer_error,neutral_error=neutral_error,max_posed_delta=maximum)
    (out/'anatomy386-muscle-preflight.json').write_text(json.dumps(metrics,indent=2)+'\n');np.savez_compressed(out/'anatomy386-muscle.npz',raw=raw,breast=breast,pose_before=before,pose_after=after,rig_before=mat_before,rig_after=mat_after,frames=np.array(FRAMES))
    if max(outside,distal_error,boundary_error)>2e-5 or primary>1e-7 or neutral_error>2e-5 or buffer_error>.005 or maximum>.22:raise ValueError('MUSCLE386_PRESERVATION')
    ignored={action.name:paths} if e['amount'] else {};after_actions=helpers('nihang_padsolve370').actions(bpy,ignore=ignored)
    if actions!=after_actions or geometry!=helpers('nihang_prep367').frozen(bpy) or rest_matrices!={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones}:raise ValueError('MUSCLE386_ORIGINAL_DATA_DRIFT')
    _,w_after=helpers('anatomy_bind386').weights(horse)
    if not np.array_equal(w,w_after):raise ValueError('MUSCLE386_WEIGHT_DRIFT')
    edges=np.array([ed.vertices[:] for ed in horse.data.edges]);skin=helpers('anatomy_domain386').main_skin(edges,len(raw));horse.data.calc_loop_triangles();faces=np.array([t.vertices[:] for t in horse.data.loop_triangles]);faces=faces[np.all(skin[faces],axis=1)];relevant=np.any(affected[faces],axis=1);surface=[]
    if e['amount']:
        cross=helpers('anatomy_bind386').crossing_pairs
        for f in [283,333,339]:
            i=FRAMES.index(f);old=cross(before[i],faces,relevant);new=cross(after[i],faces,relevant);surface.append(dict(frame=f,before=len(old),after=len(new),introduced=len(new-old)))
    if e['amount']:horse['muscle386']=True
    report=dict(amount=e['amount'],metrics=metrics,old_geometry_keys_weights_rest_bones_primary_curves_exact=True,secondary_bones=BONES,new_channels=[dict(path=p,index=1) for p in paths] if e['amount'] else [],frames=FRAMES,surface_diagnostics=surface,scope='Secondary tissue deformation candidate/control only; no edit-mode precision change or primary motion edits. Full anatomical/contact/consumer/AV qualification remains separate.')
    (out/'anatomy386-muscle.json').write_text(json.dumps(report,indent=2)+'\n');return report
