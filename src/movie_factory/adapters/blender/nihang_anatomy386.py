"""Fixed previous-horse source export and bound numeric anatomy targets.

No recipe code or asset scripts. Derivatives remain shot-local, not a new rig
qualification. Positive anatomy is decided by actual rendered comparisons.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

VIEWS={'anatomy_chest_front386','anatomy_chest_side386','anatomy_chest_oblique386'}


def mod(name):
    s=importlib.util.spec_from_file_location('anatomy386_'+name,Path(__file__).with_name(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def validate(e):
    if e==dict(kind='mounted_anatomy386_export',target='horse'):
        return e
    if not isinstance(e,dict) or set(e)!={'kind','target','data'} or e.get('kind')!='mounted_anatomy386_target' or e.get('target')!='horse':
        raise ValueError('ANATOMY386_FIELDS')
    b=e['data']
    if (not isinstance(b,dict) or set(b)!={'path','sha256'} or not isinstance(b['path'],str)
        or not b['path'].startswith('.runtime/art-direction/anatomy386-targets/')
        or '..' in Path(b['path']).parts or not b['path'].endswith('.npz')
        or not isinstance(b['sha256'],str) or len(b['sha256'])!=64
        or any(c not in '0123456789abcdef' for c in b['sha256'])):
        raise ValueError('ANATOMY386_DATA_BINDING')
    return e


def load(root,b):
    p=(root/b['path']).resolve()
    if not p.is_relative_to(root.resolve()) or p.stat().st_size>160*1024*1024 or hashlib.sha256(p.read_bytes()).hexdigest()!=b['sha256']:
        raise ValueError('ANATOMY386_DATA_STALE')
    with np.load(p,allow_pickle=False) as q:
        if set(q.files)!={'source','target','rest','mask','times'}:raise ValueError('ANATOMY386_ARRAY_KEYS')
        v={k:q[k].copy() for k in q.files}
    if (v['source'].shape!=(183,22514,3) or v['target'].shape!=v['source'].shape
        or v['rest'].shape!=(22514,3) or v['mask'].shape!=(22514,)
        or not np.array_equal(v['times'],np.arange(552,735)/2)):
        raise ValueError('ANATOMY386_ARRAY_SHAPE')
    if not all(np.isfinite(x).all() for x in v.values()) or (v['mask']<0).any() or (v['mask']>1).any():
        raise ValueError('ANATOMY386_NONFINITE_OR_MASK')
    if np.linalg.norm(v['target']-v['source'],axis=2).max()>.45:raise ValueError('ANATOMY386_DISPLACEMENT')
    if not np.array_equal(v['target'][:,v['mask']==0],v['source'][:,v['mask']==0]):raise ValueError('ANATOMY386_OUTSIDE_DRIFT')
    return v


def camera(bpy,view):
    """Pose-owned fixed anatomical anchors, not a guessed control named chest."""
    from mathutils import Vector
    if view not in VIEWS:raise ValueError('ANATOMY386_VIEW')
    rig=bpy.data.objects['horse.rig'];scene=bpy.context.scene
    center=sum((rig.pose.bones[n].head for n in ['DEF-upper_arm.L','DEF-upper_arm.R','DEF-neck.001']),Vector())/3
    target=rig.matrix_world@center;rotation=rig.matrix_world.to_quaternion()
    offset={'anatomy_chest_front386':(0,-3,.08),'anatomy_chest_side386':(3,0,.08),
            'anatomy_chest_oblique386':(-2.4,-2.4,.10)}[view]
    data=bpy.data.cameras.new('386 actual forequarter diagnostic');data.type='ORTHO';data.ortho_scale=1.85
    ob=bpy.data.objects.new(data.name,data);scene.collection.objects.link(ob)
    ob.location=target+rotation@Vector(offset);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob


def export(bpy,out):
    base=mod('nihang_cache376');horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig']
    scene=mod('nihang_support').select_production_scene(bpy);saved=(scene.frame_current,scene.frame_subframe)
    geometry=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy)
    keys=horse.data.shape_keys.key_blocks;rest=np.array([v.co[:] for v in keys[0].data],dtype=np.float32)
    raw=np.array([v.co[:] for v in horse.data.vertices],dtype=np.float32)
    names=[g.name for g in horse.vertex_groups];w=np.zeros((len(rest),len(names)),dtype=np.float32)
    for v in horse.data.vertices:
        for g in v.groups:w[v.index,g.group]=g.weight
    levels=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF']
    times=np.arange(552,735)/2.;points=[];bone_names=['DEF-spine.003','DEF-spine.004','DEF-neck.001','DEF-breast.L','DEF-breast.R','DEF-upper_arm.L','DEF-upper_arm.R','DEF-forearm.L','DEF-forearm.R'];bones=[]
    try:
        for m,_ in levels:m.show_viewport=False
        for t in times:
            base.at(scene,float(t));bpy.context.view_layer.update();p,_=base.evaluated(bpy,horse)
            if p.shape!=rest.shape:raise ValueError('ANATOMY386_SOURCE_TOPOLOGY')
            points.append(p)
            B=horse.matrix_world.inverted()@rig.matrix_world
            bones.append([[list(B@rig.pose.bones[n].head),list(B@rig.pose.bones[n].tail)] for n in bone_names])
    finally:
        for m,v in levels:m.show_viewport=v
        scene.frame_set(saved[0],subframe=saved[1]);bpy.context.view_layer.update()
    if geometry!=mod('nihang_prep367').frozen(bpy) or actions!=mod('nihang_padsolve370').actions(bpy):
        raise ValueError('ANATOMY386_READONLY_DRIFT')
    dest=out/'anatomy386-source.npz'
    np.savez_compressed(dest,source=np.array(points,dtype=np.float32),rest=rest,raw=raw,
        weights=w,group_names=np.array(names),edges=np.array([ed.vertices[:] for ed in horse.data.edges],dtype=np.int32),
        times=times,bones=np.array(bones),bone_names=np.array(bone_names))
    report=dict(npz=dict(path=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),
        frames=[276,367],step=.5,samples=len(times),geometry_actions_unchanged=True,
        scope='Read-only actual evaluated cage/bone source, subdivision temporarily disabled/restored. Not anatomy or full-speed approval.')
    (out/'anatomy386-source.json').write_text(json.dumps(report,indent=2)+'\n');return report


def run(bpy,out,e):
    validate(e)
    if e['kind']=='mounted_anatomy386_export':return export(bpy,out)
    root=Path(__file__).resolve().parents[4];q=load(root,e['data']);base=mod('nihang_cache376')
    def target(p,rest,edges,breast,t):
        i=int(round((t-276)*2))
        if not np.array_equal(rest,q['rest']) or np.max(np.abs(p-q['source'][i]))>2e-5:
            raise ValueError('ANATOMY386_ACTUAL_SOURCE_MISMATCH')
        return q['target'][i]-p,q['mask']
    result=base.run(bpy,out,dict(kind='mounted_horse_cache376',target='horse'),target_function=target)
    result.update(target_binding=e['data'],method='386 bound positive-form target under exact accepted source action',artistic_pass=False)
    (out/'anatomy386-target.json').write_text(json.dumps(result,indent=2)+'\n');return result
