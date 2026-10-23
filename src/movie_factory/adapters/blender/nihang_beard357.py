"""Bounded anatomical follicle domain and sparse guide proof on354/71.

No inherited hair roots, whole-body nearest hits, provider code or scene scripts.
"""
import math,json,importlib.util
from pathlib import Path
import numpy as np

def zone(x,d):
    """Rest eye-to-root distance in metres; explicit cheek/chin/lip region."""
    a=abs(x)
    if a>.071 or d<.027 or d>.113-.24*a:return None
    if a<.034 and .054<d<.079:return 'lip' if d<.065 else None
    if a<.022 and d<.087:return None
    if d<.079-.61*a:return None
    return 'chin' if a<.030 else 'cheek'

def guide(root,eye,index,kind):
    """Jaw-following initial tangent then full free beard, not neck projection."""
    r=np.asarray(root);a=abs(r[0]);side=1 if r[0]>=0 else -1
    t=np.linspace(0,1,24);p=np.tile(r,(24,1));group=round(r[0]/.012)
    if kind=='lip':
        p[:,0]+=side*(.012+.004*math.sin(index))*t
        p[:,1]-=.003*np.sin(np.pi*t)
        p[:,2]-=(.008+.008*a/.034)*t
    else:
        end=eye-.255+.045*(a/.071)**2+.012*math.sin(group*1.5)+.006*math.sin(index*2.399)
        p[:,0]+=-r[0]*.12*t+.005*np.sin(7*t+group)*np.sin(np.pi*t)
        p[:,1]-=(.025+.012*(1-a/.071))*t+.004*np.sin(10*t+group)*np.sin(np.pi*t)
        p[:,2]-=(r[2]-end)*t
    p[0]=r
    return p

def run(bpy,out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    spec=importlib.util.spec_from_file_location('tack354',Path(__file__).with_name('nihang_tack354.py'));h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    signature=h.action_signature(bpy)
    rig=bpy.data.objects['MF coherent Nihang rig'];body=bpy.data.objects['MF coherent Nihang body'];ob=bpy.data.objects['MF347 integrated beard and moustache']
    if not rig.get('tack354') or rig.get('beard357'):raise ValueError('BEARD357_PARENT')
    previous=rig.data.pose_position;rig.data.pose_position='REST';bpy.context.view_layer.update()
    ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mx=rig.matrix_world.inverted()@body.matrix_world
    vertices=[mx@v.co for v in ev.data.vertices]
    eye=float(rig.data.bones['eye.L'].head_local.z)
    # Spatially restricted head polygons. Normals and longitudinal ray further
    # exclude lateral pinna and rear surfaces; no nearest body-surface fallback.
    faces=[tuple(p.vertices) for p in ev.data.polygons if all(eye-.115<v.z<eye+.01 and abs(v.x)<.078 and v.y<.015 for v in (vertices[i] for i in p.vertices))]
    tree=BVHTree.FromPolygons(vertices,faces);roots=[];rng=np.random.default_rng(357)
    for i in range(3200):
        x=float(rng.uniform(-.071,.071));d=float(rng.uniform(.027,.113));kind=zone(x,d)
        if kind is None:continue
        hit,n,_,_=tree.ray_cast(Vector((x,-.6,eye-d)),Vector((0,1,0)))
        if hit is None or hit.y>-.045 or n.y>-.08:continue
        roots.append((hit+n*.0008,kind))
    if len(roots)<100:raise ValueError('BEARD357_ROOT_COVERAGE')
    # Evenly spread a small subset for actual visible rooting proof.
    roots=roots[::max(1,len(roots)//160)]
    data=bpy.data.curves.new('357 sparse anatomical beard guides','CURVE');data.dimensions='3D';data.bevel_depth=.00065;data.bevel_resolution=2
    mats=[]
    for name,color in [('cheek',(.07,.026,.008,1)),('chin',(.09,.045,.014,1)),('lip',(.06,.02,.009,1))]:
        m=bpy.data.materials.new('357 diagnostic '+name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.65;data.materials.append(m);mats.append(name)
    coords=[]
    for i,(root,kind) in enumerate(roots):
        pts=guide(root,eye,i,kind);s=data.splines.new('POLY');s.points.add(len(pts)-1);s.material_index=mats.index(kind)
        for j,(p,co) in enumerate(zip(s.points,pts)):p.co=(*co,1);p.radius=.12+.88*(1-j/(len(pts)-1))**.5
        coords.append(dict(root=list(root),kind=kind,end=pts[-1].tolist()))
    ob.data=data;rig.data.pose_position=previous;rig['beard357']=1;bpy.context.view_layer.update()
    if h.action_signature(bpy)!=signature:raise ValueError('BEARD357_ACTION_DRIFT')
    report=dict(changed=True,source_preserved=True,actions_unchanged=True,action_signature=signature,eye=eye,root_count=len(roots),restricted_faces=len(faces),roots=coords,scope='Sparse guide/root proof only; no finished groom or whole actor acceptance.')
    (out/'beard357.json').write_text(json.dumps(report,indent=2)+'\n');return report
