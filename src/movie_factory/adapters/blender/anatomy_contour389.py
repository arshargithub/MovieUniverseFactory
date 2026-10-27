"""One fixed authored forequarter sculpt, evaluated on the original source.

A broad smooth material displacement pulls the low anterior shelf into the
thorax and lifts its lower edge. It is a form hypothesis, not a simulator.
Only a static339proof is saved; no unsupported motion reuse.
"""
import json
import numpy as np

def validate(e):
    if e!={'kind':'mounted_anatomy389_contour','target':'horse'}:raise ValueError('CONTOUR389_FIELDS')
    return e

def sculpt(points,rest,skin):
    p=np.asarray(points);r=np.asarray(rest);skin=np.asarray(skin)
    if p.shape!=r.shape or p.ndim!=2 or p.shape[1]!=3 or skin.shape!=(len(p),) or not np.isfinite(p).all() or not np.isfinite(r).all():raise ValueError('CONTOUR389_ARRAYS')
    s=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
    m=skin*s((r[:,2]-.72)/.28)*s((1.88-r[:,2])/.25)*s((r[:,1]+1.4)/.25)*s((-.23-r[:,1])/.25)
    a=p.astype(float).copy()
    # Integrated broad stroke, immutable material support; no nearest-surface
    # jumps, group ownership seams, point clipping or fitted primitive proxy.
    for _ in range(16):
        strength=m*np.exp(-((a[:,2]-1.27)/.25)**2-((a[:,1]+.94)/.34)**2)
        a[:,1]+=.17/16*strength;a[:,2]+=.035/16*strength
    a=a.astype(p.dtype);a[m==0]=p[m==0]
    return a,m

def run(bpy,out,e,helpers):
    validate(e);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];scene=helpers('nihang_support').select_production_scene(bpy)
    if len(horse.data.vertices)!=22514 or any(horse.get(k) for k in ('cache376','probe389','weights386','bind_preserve386')):raise ValueError('CONTOUR389_SOURCE')
    arm=[x for x in horse.modifiers if x.type=='ARMATURE']
    if len(arm)!=1 or arm[0].use_deform_preserve_volume:raise ValueError('CONTOUR389_ARMATURE')
    cap=helpers('anatomy_muscle386');names=[b.name for b in rig.pose.bones];original_geometry=helpers('nihang_prep367').frozen(bpy);actions=helpers('nihang_padsolve370').actions(bpy)
    before,mb=cap.capture(bpy,horse,rig,names,helpers);rest=np.array([v.co[:] for v in horse.data.shape_keys.key_blocks[0].data],np.float32);edges=np.array([x.vertices[:] for x in horse.data.edges]);skin=helpers('anatomy_domain386').main_skin(edges,len(rest));targets=[]
    for p in before:
        t,m=sculpt(p,rest,skin);targets.append(t)
    targets=np.array(targets);error=np.linalg.norm(targets-before,axis=2)
    if error.max()>.2 or not np.array_equal(targets[:,m==0],before[:,m==0]):raise ValueError('CONTOUR389_DOMAIN')
    i=cap.FRAMES.index(339);frame=339;scene.frame_set(frame);bpy.context.view_layer.update();base=helpers('nihang_cache376');levels=[(x,x.show_viewport) for x in horse.modifiers if x.type=='SUBSURF']
    originals={k.name:np.array([v.co[:] for v in k.data],np.float32) for k in horse.data.shape_keys.key_blocks}
    arm[0].show_viewport=False;arm[0].show_render=False
    for k in horse.data.shape_keys.key_blocks:
        if k.name!='Basis':k.mute=True
    key=horse.shape_key_add(name='389 contour339 diagnostic ONLY',from_mix=False);key.data.foreach_set('co',targets[i].ravel());key.value=1.;bpy.context.view_layer.update()
    try:
        for x,_ in levels:x.show_viewport=False
        actual,_=base.evaluated(bpy,horse)
    finally:
        for x,v in levels:x.show_viewport=v
    actual_error=float(abs(actual-targets[i]).max());other=helpers('nihang_prep367').frozen(bpy);other.pop('horse');original_geometry.pop('horse')
    preserved=original_geometry==other and actions==helpers('nihang_padsolve370').actions(bpy) and all(np.array_equal(a,np.array([v.co[:] for v in horse.data.shape_keys.key_blocks[n].data],np.float32)) for n,a in originals.items())
    if actual_error>2e-6 or not preserved:raise ValueError('CONTOUR389_PRESERVATION')
    horse['probe389']='Static contour339only. Unsupported at otherframes; original rig/shapes/actions retained.'
    np.savez_compressed(out/'anatomy389-contour.npz',rest=rest,source=before,target=targets,mask=m,frames=np.array(cap.FRAMES),rig_before=mb)
    result=dict(frame=339,max_delta=float(error.max()),per_pose_max={str(f):float(error[j].max()) for j,f in enumerate(cap.FRAMES)},actual_error=actual_error,outside_exact=True,original_shapes_actions_othergeometry_preserved=preserved,scope='Static339 authored form hypothesis only. All otherpose data are diagnostics, not native motion qualification.')
    result['diagnostic_render_profile']=helpers('anatomy_static387').freeze(scene)
    (out/'anatomy389-contour.json').write_text(json.dumps(result,indent=2)+'\n');return result
