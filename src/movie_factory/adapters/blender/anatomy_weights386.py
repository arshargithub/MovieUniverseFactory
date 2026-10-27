"""Closed chest-to-proximal-limb ownership diagnostic on the original live rig.

No pose authoring or rest sculpt. The original breast groups stay partly
anchored; only their local soft-tissue influence shares upper-arm deformation.
"""
import json
from pathlib import Path
import numpy as np

def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)

def validate(e):
    if set(e)!={'kind','target','strength'} or e['kind']!='mounted_anatomy386_weights' or e['target']!='horse':raise ValueError('WEIGHTS386_FIELDS')
    if type(e['strength']) not in (int,float) or not np.isfinite(e['strength']) or not 0<e['strength']<=.7:raise ValueError('WEIGHTS386_STRENGTH')
    return e

def remap(rest,weights,names,edges,strength,skin):
    names=list(names);r=np.asarray(rest);w=np.asarray(weights);x,y,z=r.T
    if r.shape!=(len(w),3) or len(names)!=w.shape[1] or not np.isfinite(w).all() or w.min()<0:raise ValueError('WEIGHTS386_ARRAYS')
    spatial=smooth(1.02,1.16,z)*(1-smooth(1.43,1.66,z))*smooth(-1.2,-1.10,y)*(1-smooth(-.45,-.25,y))*(1-smooth(.25,.36,abs(x)))*skin
    breast=[names.index('DEF-breast.'+s) for s in ['L','R']]
    ownership=w[:,breast].sum(1);mask=spatial*smooth(.03,.2,ownership)
    a,b=edges.T;count=np.bincount(edges.ravel(),minlength=len(r));fixed=(spatial==0)|(ownership<.03)
    for _ in range(6):
        total=np.zeros(len(r));np.add.at(total,a,mask[b]);np.add.at(total,b,mask[a]);mask=.75*mask+.25*total/np.maximum(count,1);mask[fixed]=0
    result=w.copy()
    for side,anchor in zip(['L','R'],breast):
        take=w[:,anchor]*mask*strength;result[:,anchor]-=take;result[:,names.index('DEF-upper_arm.'+side)]+=take
    if result.min()< -1e-7 or abs(result.sum(1)-w.sum(1)).max()>1e-6:raise ValueError('WEIGHTS386_MASS')
    return result,mask

def apply(bpy,out,e,helpers):
    validate(e);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];keys=horse.data.shape_keys.key_blocks
    if horse.get('cache376') or horse.get('weights386'):raise ValueError('WEIGHTS386_LIVE_OR_REAPPLY')
    rest=np.array([v.co[:] for v in keys[0].data],dtype=np.float32);names=[g.name for g in horse.vertex_groups];weights=np.zeros((len(rest),len(names)),np.float32)
    for v in horse.data.vertices:
        for g in v.groups:weights[v.index,g.group]=g.weight
    edges=np.array([ed.vertices[:] for ed in horse.data.edges]);skin=helpers('anatomy_domain386').main_skin(edges,len(rest))
    target,mask=remap(rest,weights,names,edges,e['strength'],skin);changed=np.any(target!=weights,axis=1)
    domain=helpers('anatomy_domain386');distal,_=domain.pectoral_domains(rest,weights,names)
    if np.any(changed&distal) or np.any(changed&~skin):raise ValueError('WEIGHTS386_PROTECTED')
    geom=helpers('nihang_prep367').frozen(bpy);actions=helpers('nihang_padsolve370').actions(bpy)
    before,rig_before=helpers('anatomy_rest386').pose_samples(bpy,horse,helpers)
    for j,g in enumerate(horse.vertex_groups):
        for i in np.flatnonzero(target[:,j]!=weights[:,j]):
            value=float(target[i,j])
            if value<=1e-10:g.remove([int(i)])
            else:g.add([int(i)],value,'REPLACE')
    stored=np.zeros_like(weights)
    for v in horse.data.vertices:
        for g in v.groups:stored[v.index,g.group]=g.weight
    if np.max(abs(stored-target))>2e-7 or np.max(abs(stored.sum(1)-weights.sum(1)))>2e-6:raise ValueError('WEIGHTS386_STORED_MASS')
    bpy.context.view_layer.update();after,rig_after=helpers('anatomy_rest386').pose_samples(bpy,horse,helpers)
    preservation=domain.evaluated_preservation(before,after,~changed,rig_before,rig_after)
    if geom!=helpers('nihang_prep367').frozen(bpy) or actions!=helpers('nihang_padsolve370').actions(bpy):raise ValueError('WEIGHTS386_GEOMETRY_ACTION_DRIFT')
    displacement=np.linalg.norm(after-before,axis=2)
    if displacement.max()>.3:raise ValueError('WEIGHTS386_EVALUATED_DISPLACEMENT')
    np.savez_compressed(out/'anatomy386-weights.npz',before=weights,after=target,mask=mask,pose_before=before,pose_after=after,rig_before=rig_before,rig_after=rig_after)
    report=dict(strength=e['strength'],changed_vertices=int(changed.sum()),pose_preservation=preservation,max_evaluated_delta=float(displacement.max()),geometry_actions_unchanged=True,distal_weights_exact=True,production_nap_not_updated=True,scope='Diagnostic local skin-ownership hypothesis only; original rest/action/rig unchanged. Actual native neutral/raised form and later nap/consumer interfaces must qualify before adoption.')
    horse['weights386']=True;(out/'anatomy386-weights.json').write_text(json.dumps(report,indent=2)+'\n');return report
