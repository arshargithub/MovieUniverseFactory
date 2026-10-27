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
    if isinstance(e,dict) and e.get('kind')=='mounted_upperarm387_rigid':return mod('anatomy_upperarm387').validate(e)
    if isinstance(e,dict) and e.get('kind')=='mounted_anatomy387_static_control':return mod('anatomy_static387').validate(e)
    if isinstance(e,dict) and e.get('kind') in {'mounted_articulation387','mounted_articulation387_calibrated'}:return mod('anatomy_articulation387').validate(e)
    if isinstance(e,dict) and e.get('kind')=='mounted_anatomy386_muscle_contract':return mod('anatomy_muscle386').validate(e)
    if isinstance(e,dict) and e.get('kind') in {'mounted_anatomy386_rigid_support','mounted_anatomy386_dominant_support'}:return mod('anatomy_support386').validate(e)
    if isinstance(e,dict) and e.get('kind') in {'mounted_anatomy386_bind_preserve','mounted_anatomy386_bind_core'}:return mod('anatomy_bind386').validate(e)
    if isinstance(e,dict) and e.get('kind') in {'mounted_anatomy386_weights','mounted_anatomy386_weights_core'}:return mod('anatomy_weights386').validate(e)
    if e in [dict(kind='mounted_anatomy386_clay',target='horse'),dict(kind='mounted_anatomy386_raw_control',target='horse')]:return e
    if e==dict(kind='mounted_anatomy386_export',target='horse'):
        return e
    if isinstance(e,dict) and e.get('kind')=='mounted_anatomy386_reference':
        if set(e)!={'kind','target','data'} or e.get('target')!='horse':raise ValueError('ANATOMY386_REFERENCE_FIELDS')
        b=e['data']
        if (not isinstance(b,dict) or set(b)!={'path','sha256'} or not isinstance(b['path'],str) or not b['path'].startswith('.runtime/art-direction/anatomy386-references/') or '..' in Path(b['path']).parts or not b['path'].endswith('.npz') or not isinstance(b['sha256'],str) or len(b['sha256'])!=64 or any(c not in '0123456789abcdef' for c in b['sha256'])):raise ValueError('ANATOMY386_REFERENCE_BINDING')
        return e
    if not isinstance(e,dict) or set(e)!={'kind','target','data'} or e.get('kind') not in {'mounted_anatomy387_owner_target','mounted_anatomy387_static_target','mounted_anatomy386_target','mounted_anatomy386_rest','mounted_anatomy386_form','mounted_anatomy386_pectoral','mounted_anatomy386_connected','mounted_anatomy386_weights','mounted_anatomy386_weights_core','mounted_anatomy386_bind_preserve','mounted_anatomy386_bind_core'} or e.get('target')!='horse':
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


def load_reference(root,b):
    p=(root/b['path']).resolve()
    if not p.is_relative_to(root.resolve()) or p.stat().st_size>8*1024*1024 or hashlib.sha256(p.read_bytes()).hexdigest()!=b['sha256']:raise ValueError('ANATOMY386_REFERENCE_STALE')
    with np.load(p,allow_pickle=False) as q:
        if set(q.files)!={'vertices','faces'}:raise ValueError('ANATOMY386_REFERENCE_KEYS')
        v=q['vertices'].copy();f=q['faces'].copy()
    if (v.ndim!=2 or v.shape[1]!=3 or not 3<=len(v)<=10000 or f.ndim!=2 or f.shape[1]!=3 or not 1<=len(f)<=20000 or f.dtype.kind not in 'iu' or not np.isfinite(v).all() or abs(v).max()>5 or f.min()<0 or f.max()>=len(v) or np.any(np.diff(np.sort(f,axis=1),axis=1)==0)):raise ValueError('ANATOMY386_REFERENCE_TOPOLOGY')
    return v,f


def reference(bpy,out,e):
    root=Path(__file__).resolve().parents[4];v,f=load_reference(root,e['data'])
    name='MF Nihang anatomy spatial reference386'
    if bpy.data.objects.get(name):raise ValueError('ANATOMY386_REFERENCE_REAPPLY')
    horse=bpy.data.objects['horse'];geometry=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy)
    # Reference-only derivative: original geometry/action untouched. No rig,
    # material, script or texture is imported from the reference asset.
    hidden=[]
    for ob in bpy.data.objects:
        if ob.type=='MESH' and not ob.hide_render:ob.hide_render=True;hidden.append(ob.name)
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(v.tolist(),[],f.tolist());mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(ob);ob.matrix_world=horse.matrix_world.copy()
    for poly in mesh.polygons:poly.use_smooth=True
    mat=bpy.data.materials.new(name+' neutral');mat.use_nodes=True;node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.32,.29,.25,1);node.inputs['Roughness'].default_value=.8;mesh.materials.append(mat)
    after=mod('nihang_prep367').frozen(bpy);after.pop(name)
    if geometry!=after or actions!=mod('nihang_padsolve370').actions(bpy):raise ValueError('ANATOMY386_REFERENCE_SOURCE_DRIFT')
    report=dict(binding=e['data'],vertices=len(v),triangles=len(f),original_geometry_actions_unchanged=True,hidden_original_objects=hidden,scope='Spatial anatomy study only. Neutral static reference, not the production horse, retargeting, costume, material, animation or film adoption.')
    (out/'anatomy386-reference.json').write_text(json.dumps(report,indent=2)+'\n');return report


def clay(bpy,out):
    horse=bpy.data.objects['horse'];mesh=horse.data
    if horse.get('anatomy386_clay'):raise ValueError('ANATOMY386_CLAY_REAPPLY')
    geometry=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy)
    custom=bool(getattr(mesh,'has_custom_normals',False))
    if custom and not hasattr(mesh,'normals_split_custom_set'):raise ValueError('ANATOMY386_CLAY_NORMAL_API')
    # Select the connected skin only: alpha mane/eye cards keep their materials.
    parent=list(range(len(mesh.vertices)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for edge in mesh.edges:
        a,b=edge.vertices;aa,bb=find(a),find(b)
        if aa!=bb:parent[bb]=aa
    labels=[find(i) for i in range(len(parent))];counts={}
    for i in labels:counts[i]=counts.get(i,0)+1
    main=max(counts,key=counts.get)
    hidden=[]
    for ob in bpy.data.objects:
        if ob!=horse and ob.type in {'MESH','CURVE','CURVES','POINTCLOUD','VOLUME'} and not ob.hide_render:ob.hide_render=True;hidden.append(ob.name)
    mat=bpy.data.materials.new('386 neutral anatomy clay');mat.use_nodes=True;node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.32,.29,.25,1);node.inputs['Roughness'].default_value=.8
    mesh.materials.append(mat);index=len(mesh.materials)-1;changed=0
    for face in mesh.polygons:
        if all(labels[i]==main for i in face.vertices):face.material_index=index;changed+=1
    if custom:mesh.normals_split_custom_set([(0.,0.,0.)]*len(mesh.loops))
    horse['anatomy386_clay']=True;bpy.context.view_layer.update()
    if geometry!=mod('nihang_prep367').frozen(bpy) or actions!=mod('nihang_padsolve370').actions(bpy):raise ValueError('ANATOMY386_CLAY_GEOMETRY_DRIFT')
    report=dict(main_skin_vertices=counts[main],skin_polygons=changed,source_custom_normals=custom,normal_policy='automatic geometricnormals plus neutral skin shader; no skintexture/bump',original_geometry_actions_unchanged=True,hidden_other_objects=len(hidden),scope='Diagnostic derivative only; not a productionmaterial/look change. Original master and final shader remain separate.')
    (out/'anatomy386-clay.json').write_text(json.dumps(report,indent=2)+'\n');return report


def raw_control_data(raw,shapes):
    if raw.shape!=(22514,3) or shapes.shape!=(4,22514,3) or not np.isfinite(raw).all() or not np.isfinite(shapes).all():raise ValueError('ANATOMY386_RAW_TOPOLOGY')
    d=raw-shapes[0];length=np.linalg.norm(d,axis=1);ids=np.flatnonzero(length>1e-6)
    if len(ids)!=979 or length.max()>.200001:raise ValueError('ANATOMY386_RAW_SOURCE_CHANGED')
    p=shapes[0][ids]
    if abs(p[:,0]).max()>.4 or p[:,1].min()<-1.3 or p[:,1].max()>0 or p[:,2].min()<.9 or p[:,2].max()>1.8:raise ValueError('ANATOMY386_RAW_REGION')
    restored=raw[None,:,:]+(shapes-shapes[0][None,:,:]);restored[0]=raw
    return restored,ids


def raw_control(bpy,out):
    horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig']
    if horse.get('cache376') or horse.get('anatomy386_raw_control'):raise ValueError('ANATOMY386_RAW_REAPPLY')
    keys=horse.data.shape_keys.key_blocks
    if [k.name for k in keys]!=['Basis','corr.neck','corr.chin','corr.neck.2']:raise ValueError('ANATOMY386_RAW_KEYS')
    raw=np.array([v.co[:] for v in horse.data.vertices],dtype=np.float32);shapes=np.array([[v.co[:] for v in k.data] for k in keys],dtype=np.float32)
    restored,ids=raw_control_data(raw,shapes);before=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy)
    weights=[[(g.group,g.weight) for g in v.groups] for v in horse.data.vertices]
    for k,co in zip(keys,restored):k.data.foreach_set('co',co.ravel())
    horse['anatomy386_raw_control']=True;bpy.context.view_layer.update()
    after=mod('nihang_prep367').frozen(bpy)
    if any(before[n]!=h for n,h in after.items() if n!='horse') or actions!=mod('nihang_padsolve370').actions(bpy) or weights!=[[(g.group,g.weight) for g in v.groups] for v in horse.data.vertices]:raise ValueError('ANATOMY386_RAW_OUTSIDE_DRIFT')
    actual=np.array([[v.co[:] for v in k.data] for k in keys]);error=float(np.max(abs((actual-actual[0])-(shapes-shapes[0]))))
    if error>3e-7 or not np.array_equal(np.array([v.co[:] for v in horse.data.vertices],dtype=np.float32),raw):raise ValueError('ANATOMY386_RAW_IDENTITY_DRIFT')
    report=dict(changed_vertices=len(ids),max_restoration_delta=float(np.linalg.norm(raw-shapes[0],axis=1).max()),restored_basis_raw_error=float(abs(actual[0]-raw).max()),relative_corrective_error=error,weights_actions_other_geometry_unchanged=True,scope='Exact coherent original rawchest recovery control on original live rig. Not adopted anatomy, new motion or identity. Normals/material require separately qualified clay/film controls.')
    (out/'anatomy386-raw-control.json').write_text(json.dumps(report,indent=2)+'\n');return report


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
    times=np.arange(552,735)/2.;points=[];bone_names=['DEF-spine.003','DEF-spine.004','DEF-neck.001','DEF-breast.L','DEF-breast.R','DEF-upper_arm.L','DEF-upper_arm.R','DEF-forearm.L','DEF-forearm.R'];bones=[];worlds=[];rig_worlds=[]
    try:
        for m,_ in levels:m.show_viewport=False
        for t in times:
            base.at(scene,float(t));bpy.context.view_layer.update();p,_=base.evaluated(bpy,horse)
            if p.shape!=rest.shape:raise ValueError('ANATOMY386_SOURCE_TOPOLOGY')
            points.append(p);worlds.append([list(row) for row in horse.matrix_world]);rig_worlds.append([list(row) for row in rig.matrix_world])
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
        times=times,bones=np.array(bones),bone_names=np.array(bone_names),body_world=np.array(worlds),rig_world=np.array(rig_worlds))
    report=dict(npz=dict(path=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),
        frames=[276,367],step=.5,samples=len(times),geometry_actions_unchanged=True,
        scope='Read-only actual evaluated cage/bone source, subdivision temporarily disabled/restored. Not anatomy or full-speed approval.')
    (out/'anatomy386-source.json').write_text(json.dumps(report,indent=2)+'\n');return report


def run(bpy,out,e):
    if e['kind']=='mounted_upperarm387_rigid':return mod('anatomy_upperarm387').run(bpy,out,e,mod)
    if e['kind']=='mounted_anatomy387_static_control':return mod('anatomy_static387').control(bpy,out,mod)
    if e['kind'] in {'mounted_articulation387','mounted_articulation387_calibrated'}:return mod('anatomy_articulation387').run(bpy,out,e,mod)
    if e['kind']=='mounted_anatomy386_muscle_contract':return mod('anatomy_muscle386').run(bpy,out,e,mod)
    if e['kind'] in {'mounted_anatomy386_rigid_support','mounted_anatomy386_dominant_support'}:return mod('anatomy_support386').run(bpy,out,e,mod)
    if e['kind'] in {'mounted_anatomy386_bind_preserve','mounted_anatomy386_bind_core'}:return mod('anatomy_bind386').apply(bpy,out,e,mod)
    if e['kind'] in {'mounted_anatomy386_weights','mounted_anatomy386_weights_core'}:return mod('anatomy_weights386').apply(bpy,out,e,mod)
    validate(e)
    if e['kind']=='mounted_anatomy386_raw_control':return raw_control(bpy,out)
    if e['kind']=='mounted_anatomy386_clay':return clay(bpy,out)
    if e['kind']=='mounted_anatomy386_export':return export(bpy,out)
    if e['kind'] in {'mounted_anatomy386_rest','mounted_anatomy386_form','mounted_anatomy386_pectoral','mounted_anatomy386_connected'}:return mod('anatomy_rest386').apply(bpy,out,e['data'],mod,depth_only=e['kind']=='mounted_anatomy386_rest',allow_proximal=e['kind'] in {'mounted_anatomy386_pectoral','mounted_anatomy386_connected'},proximal_limit=.15 if e['kind']=='mounted_anatomy386_connected' else .06)
    if e['kind']=='mounted_anatomy386_reference':return reference(bpy,out,e)
    root=Path(__file__).resolve().parents[4];q=load(root,e['data']);base=mod('nihang_cache376')
    horse=bpy.data.objects['horse'];names=[g.name for g in horse.vertex_groups];weights=np.zeros((len(horse.data.vertices),len(names)),dtype=np.float32)
    for vertex in horse.data.vertices:
        for item in vertex.groups:weights[vertex.index,item.group]=item.weight
    if e['kind']=='mounted_anatomy387_owner_target':
        edges=np.array([ed.vertices[:] for ed in horse.data.edges]);domain_report=mod('anatomy_domain386').preserve_owner387(q['source'],q['target'],q['rest'],weights,names,edges)
    else:domain_report=mod('anatomy_domain386').preserve_forelegs(q['source'],q['target'],weights,names)
    def target(p,rest,edges,breast,t):
        i=int(round((t-276)*2))
        if not np.array_equal(rest,q['rest']) or np.max(np.abs(p-q['source'][i]))>2e-5:
            raise ValueError('ANATOMY386_ACTUAL_SOURCE_MISMATCH')
        return q['target'][i]-p,q['mask']
    result=base.run(bpy,out,dict(kind='mounted_horse_cache376',target='horse'),target_function=target)
    if e['kind'] in {'mounted_anatomy387_static_target','mounted_anatomy387_owner_target'}:result['diagnostic_render_profile']=mod('anatomy_static387').freeze(bpy.context.scene)
    result.update(target_binding=e['data'],domain_preservation=domain_report,method='386 bound positive-form target under exact accepted source action',artistic_pass=False)
    (out/'anatomy386-target.json').write_text(json.dumps(result,indent=2)+'\n');return result
