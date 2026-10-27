"""Fixed local corrective-shape isolation on the original live horse.

Mode0 is an actual no-edit control. Mode1 suppresses inherited corrective
DISPLACEMENTS only in the lower-neck/forequarter, never Basis or pose curves.
This is a causal diagnostic, not an automatic anatomical repair approval.
"""
import json
import numpy as np

KEYS=('Basis','corr.neck','corr.chin','corr.neck.2')

def validate(e):
    if not isinstance(e,dict) or set(e)!={'kind','target','mode'} or e.get('kind')!='mounted_anatomy388_corrective_control' or e.get('target')!='horse':raise ValueError('CORRECTIVE388_FIELDS')
    if type(e['mode']) is not int or e['mode'] not in (0,1):raise ValueError('CORRECTIVE388_MODE')
    return e

def local_mask(rest,skin):
    r=np.asarray(rest);s=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
    return skin*s((r[:,2]-.95)/.15)*s((1.88-r[:,2])/.28)*s((r[:,1]+1.4)/.18)*s((-.23-r[:,1])/.18)

def isolate(shapes,mask,mode):
    a=np.asarray(shapes);m=np.asarray(mask)
    if a.ndim!=3 or a.shape[0]!=4 or a.shape[2]!=3 or m.shape!=(a.shape[1],) or not np.isfinite(a).all() or not np.isfinite(m).all() or (m<0).any() or (m>1).any() or type(mode) is not int or mode not in (0,1):raise ValueError('CORRECTIVE388_ARRAYS')
    out=a.copy()
    if mode:
        out[1:]=a[0]+(a[1:]-a[0])*(1-m[None,:,None])
        out[:,m==0]=a[:,m==0]
    return out

def run(bpy,out,e,helpers):
    validate(e);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];scene=helpers('nihang_support').select_production_scene(bpy)
    if any(horse.get(k) for k in ('cache376','corrective388','muscle386','support386','weights386','bind_preserve386')):raise ValueError('CORRECTIVE388_SOURCE')
    keys=horse.data.shape_keys.key_blocks
    if tuple(k.name for k in keys)!=KEYS or len(horse.data.vertices)!=22514:raise ValueError('CORRECTIVE388_KEYS')
    raw=np.array([v.co[:] for v in horse.data.vertices],np.float32);shapes=np.array([[v.co[:] for v in k.data] for k in keys],np.float32);edges=np.array([e.vertices[:] for e in horse.data.edges]);skin=helpers('anatomy_domain386').main_skin(edges,len(raw));mask=local_mask(shapes[0],skin);new=isolate(shapes,mask,e['mode']);changed=np.any(new!=shapes,axis=(0,2))
    geometry=helpers('nihang_prep367').frozen(bpy);actions=helpers('nihang_padsolve370').actions(bpy);names,w=helpers('anatomy_bind386').weights(horse);restbones={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones};cap=helpers('anatomy_muscle386');all_names=[b.name for b in rig.pose.bones]
    before,mb=cap.capture(bpy,horse,rig,all_names,helpers);saved=(scene.frame_current,scene.frame_subframe);values={}
    for f in cap.FRAMES:
        scene.frame_set(f);bpy.context.view_layer.update();values[str(f)]={k.name:float(k.value) for k in keys}
    scene.frame_set(saved[0],subframe=saved[1]);bpy.context.view_layer.update()
    if e['mode']:
        for k,co in zip(keys,new):k.data.foreach_set('co',co.ravel())
        horse.data.shape_keys.update_tag();horse.data.update();horse.update_tag(refresh={'DATA'});bpy.context.view_layer.update()
    after,ma=cap.capture(bpy,horse,rig,all_names,helpers);error=np.linalg.norm(after-before,axis=2);other=helpers('nihang_prep367').frozen(bpy);geometry.pop('horse');other.pop('horse');_,wa=helpers('anatomy_bind386').weights(horse)
    preserved=(geometry==other and actions==helpers('nihang_padsolve370').actions(bpy) and np.array_equal(raw,np.array([v.co[:] for v in horse.data.vertices],np.float32)) and np.array_equal(w,wa) and restbones=={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones})
    actual=np.array([[v.co[:] for v in k.data] for k in keys],np.float32)
    report=dict(mode=e['mode'],frames=cap.FRAMES,source_key_values=values,changed_vertices=int(changed.sum()),max_key_delta=float(np.linalg.norm(new-shapes,axis=2).max()),max_surface_delta=float(error.max()),per_pose_max={str(f):float(error[i].max()) for i,f in enumerate(cap.FRAMES)},outside_error=float(error[:,~changed].max()) if e['mode'] else float(error.max()),primary_matrix_error=float(abs(ma-mb).max()),basis_exact=np.array_equal(actual[0],shapes[0]),actual_keys_exact=np.array_equal(actual,new),raw_weights_restbones_actions_othergeometry_preserved=preserved,scope='Actual fixed local neck-corrective isolation. No actor/primarymotion change. Anatomy, embedding and fullspeed remain separate.')
    np.savez_compressed(out/'anatomy388-corrective.npz',raw=raw,shapes_before=shapes,shapes_after=actual,mask=mask,pose_before=before,pose_after=after,rig_before=mb,rig_after=ma,frames=np.array(cap.FRAMES))
    (out/'anatomy388-corrective.json').write_text(json.dumps(report,indent=2)+'\n')
    if not preserved or not report['basis_exact'] or not report['actual_keys_exact'] or report['outside_error']>2e-5 or report['primary_matrix_error']>1e-7 or report['max_surface_delta']>.35:raise ValueError('CORRECTIVE388_PRESERVATION')
    report['diagnostic_render_profile']=helpers('anatomy_static387').freeze(scene)
    if e['mode']:horse['corrective388']=True
    (out/'anatomy388-corrective.json').write_text(json.dumps(report,indent=2)+'\n');return report
