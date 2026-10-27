"""Scoped native skinning comparison; fixed closed modes, no arbitrary payload.

Volume-preserving interpolation is evaluated on the actual live source rig.
Only the connected forequarter receives its displacement in the shot cache.
"""
import json
import numpy as np

def validate(e):
    if not isinstance(e,dict) or set(e)!={'kind','target','mode'} or e.get('kind')!='mounted_anatomy389_skinning' or e.get('target')!='horse':raise ValueError('SKINNING389_FIELDS')
    if type(e['mode']) is not int or e['mode'] not in (0,1,2):raise ValueError('SKINNING389_MODE')
    return e

def mask(rest,skin):
    r=np.asarray(rest);s=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
    return np.asarray(skin)*s((r[:,2]-.72)/.28)*s((1.88-r[:,2])/.25)*s((r[:,1]+1.4)/.25)*s((-.23-r[:,1])/.25)

def blend(source,alternative,m):
    a=np.asarray(source);b=np.asarray(alternative);m=np.asarray(m)
    if a.shape!=b.shape or a.ndim!=2 or a.shape[1]!=3 or m.shape!=(len(a),) or not all(np.isfinite(x).all() for x in (a,b,m)) or (m<0).any() or (m>1).any():raise ValueError('SKINNING389_ARRAY')
    out=(a+(b-a)*m[:,None]).astype(a.dtype);out[m==0]=a[m==0]
    return out

def run(bpy,out,e,helpers):
    validate(e);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];scene=helpers('nihang_support').select_production_scene(bpy)
    if len(horse.data.vertices)!=22514 or any(horse.get(k) for k in ('cache376','probe389','weights386','bind_preserve386','corrective388','muscle386','support386')):raise ValueError('SKINNING389_SOURCE')
    arms=[m for m in horse.modifiers if m.type=='ARMATURE']
    if len(arms)!=1 or arms[0].object!=rig or arms[0].use_deform_preserve_volume:raise ValueError('SKINNING389_ARMATURE')
    arm=arms[0];cap=helpers('anatomy_muscle386');names=[b.name for b in rig.pose.bones];geometry=helpers('nihang_prep367').frozen(bpy);actions=helpers('nihang_padsolve370').actions(bpy)
    before,mb=cap.capture(bpy,horse,rig,names,helpers)
    try:
        arm.use_deform_preserve_volume=True;horse.update_tag(refresh={'OBJECT','DATA'});bpy.context.view_layer.update();dq,ma=cap.capture(bpy,horse,rig,names,helpers)
    finally:
        arm.use_deform_preserve_volume=False;horse.update_tag(refresh={'OBJECT','DATA'});bpy.context.view_layer.update()
    raw=np.array([v.co[:] for v in horse.data.shape_keys.key_blocks[0].data],np.float32);edges=np.array([x.vertices[:] for x in horse.data.edges]);skin=helpers('anatomy_domain386').main_skin(edges,len(raw));m=mask(raw,skin)
    after=np.array([blend(a,b,m) for a,b in zip(before,dq)])
    if not e['mode']:after=before.copy()
    delta=np.linalg.norm(after-before,axis=2)
    report=dict(mode=e['mode'],frames=cap.FRAMES,primary_matrix_error=float(abs(ma-mb).max()),outside_error=float(delta[:,m==0].max()),max_surface_delta=float(delta.max()),per_pose_max={str(f):float(delta[i].max()) for i,f in enumerate(cap.FRAMES)},source_preserved=geometry==helpers('nihang_prep367').frozen(bpy) and actions==helpers('nihang_padsolve370').actions(bpy),original_preserve_volume=False,scope='Native local interpolation comparison. No anatomical or motion approval from source/zero checks.')
    np.savez_compressed(out/'anatomy389-skinning.npz',rest=raw,mask=m,source=before,dq=dq,target=after,frames=np.array(cap.FRAMES),rig_before=mb,rig_after=ma)
    (out/'anatomy389-skinning.json').write_text(json.dumps(report,indent=2)+'\n')
    if not report['source_preserved'] or report['primary_matrix_error']>1e-7 or report['outside_error']>2e-5 or report['max_surface_delta']>.2:raise ValueError('SKINNING389_PRESERVATION')
    if e['mode']==1:
        base=helpers('nihang_cache376')
        def target(p,rest,edges,breast,t):
            try:
                arm.use_deform_preserve_volume=True;horse.update_tag(refresh={'OBJECT','DATA'});bpy.context.view_layer.update();alternative,_=base.evaluated(bpy,horse)
            finally:
                arm.use_deform_preserve_volume=False;horse.update_tag(refresh={'OBJECT','DATA'});bpy.context.view_layer.update()
            result=blend(p,alternative,m);d=result-p
            if np.linalg.norm(d,axis=1).max()>.2:raise ValueError('SKINNING389_DENSE_LIMIT')
            return d,m
        report['cache']=base.run(bpy,out,dict(kind='mounted_horse_cache376',target='horse'),target_function=target)
    if e['mode']==2:
        # One actual posed cage first; original shapes and rig remain as data.
        # This intentionally supports ONLY339, never motion or production use.
        frame=339;scene.frame_set(frame);bpy.context.view_layer.update();base=helpers('nihang_cache376');levels=[(x,x.show_viewport) for x in horse.modifiers if x.type=='SUBSURF']
        try:
            for x,_ in levels:x.show_viewport=False
            actual_source,_=base.evaluated(bpy,horse)
        finally:
            for x,v in levels:x.show_viewport=v
        i=cap.FRAMES.index(frame)
        if abs(actual_source-before[i]).max()>2e-5:raise ValueError('SKINNING389_PROBE_SOURCE')
        originals={k.name:np.array([v.co[:] for v in k.data],np.float32) for k in horse.data.shape_keys.key_blocks}
        arm.show_viewport=False;arm.show_render=False
        for k in horse.data.shape_keys.key_blocks:
            if k.name!='Basis':k.mute=True
        k=horse.shape_key_add(name='389 fixed339 diagnostic ONLY',from_mix=False);k.data.foreach_set('co',after[i].ravel());k.value=1.
        bpy.context.view_layer.update()
        try:
            for x,_ in levels:x.show_viewport=False
            posed,_=base.evaluated(bpy,horse)
        finally:
            for x,v in levels:x.show_viewport=v
        error=float(abs(posed-after[i]).max())
        if error>2e-6 or any(not np.array_equal(a,np.array([v.co[:] for v in horse.data.shape_keys.key_blocks[n].data],np.float32)) for n,a in originals.items()):raise ValueError('SKINNING389_PROBE_TARGET')
        if actions!=helpers('nihang_padsolve370').actions(bpy):raise ValueError('SKINNING389_PROBE_ACTIONS')
        horse['probe389']='Static actual native339 only; unsupported at every other frame, no production or motion use.'
        report['static_probe']=dict(frame=frame,error=error,original_shapes_preserved=True,primary_actions_preserved=True,outside_error=float(np.linalg.norm(posed[m==0]-actual_source[m==0],axis=1).max()),scope='Static actual native339 only; do not reuse for motion.')
    report['diagnostic_render_profile']=helpers('anatomy_static387').freeze(scene)
    (out/'anatomy389-skinning.json').write_text(json.dumps(report,indent=2)+'\n');return report
