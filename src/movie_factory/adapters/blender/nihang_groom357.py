"""Dense guide-group beard from the tested357 anatomical root domain."""
import math,json,importlib.util
from pathlib import Path
import numpy as np

def path(root,eye,index,kind):
    r=np.asarray(root);a=abs(r[0]);side=1 if r[0]>=0 else -1
    t=np.linspace(0,1,32);p=np.tile(r,(32,1));g=r[0]/.012;phase=g*.31+(eye-r[2])*7
    noise=math.sin(index*2.399);lengthvar=.012*noise
    if kind=='lip':
        p[:,0]+=side*(.012+.004*noise)*t
        p[:,1]-=.005*np.sin(np.pi*t)
        p[:,2]-=(.010+.007*a/.034)*t
    else:
        end=eye-.224+.036*(a/.071)**2+lengthvar
        # Continuous field avoids disconnected ribbon families. Keep the facial
        # breadth at the root, then converge below the jaw into a rounded mass.
        p[:,0]+=.003*math.tanh(r[0]/.012)*np.sin(np.pi*t)-.36*r[0]*t*t+.0025*np.sin(9*t+index*.071)*np.sin(np.pi*t)+.005*noise*t*t
        p[:,1]-=.025*t+.019*np.sin(np.pi*t)+.006*math.sin(index*1.73)*np.sin(np.pi*t)+.002*np.sin(11*t+index*.071)*np.sin(np.pi*t)
        p[:,2]-=(r[2]-end)*t
        p[:,2]+=.001*np.sin(14*t+phase)*np.sin(np.pi*t)
        p+=np.column_stack((.0008*np.sin(31*t+index),.0008*np.cos(28*t+index),.0005*np.sin(37*t+index)))*np.sin(np.pi*t)[:,None]
    p[0]=r;return p

def run(bpy,out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    def load(name):
        s=importlib.util.spec_from_file_location(name,Path(__file__).with_name('nihang_'+name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    sparse=load('beard357');h=load('tack354');sig=h.action_signature(bpy)
    rig=bpy.data.objects['MF coherent Nihang rig'];body=bpy.data.objects['MF coherent Nihang body'];ob=bpy.data.objects['MF347 integrated beard and moustache']
    if not rig.get('beard357') or rig.get('groom357'):raise ValueError('GROOM357_PARENT')
    previous=rig.data.pose_position;rig.data.pose_position='REST';bpy.context.view_layer.update()
    ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mx=rig.matrix_world.inverted()@body.matrix_world;vs=[mx@v.co for v in ev.data.vertices];eye=float(rig.data.bones['eye.L'].head_local.z)
    faces=[tuple(p.vertices) for p in ev.data.polygons if all(eye-.115<v.z<eye+.01 and abs(v.x)<.078 and v.y<.015 for v in (vs[i] for i in p.vertices))]
    tree=BVHTree.FromPolygons(vs,faces);rng=np.random.default_rng(35774);roots=[]
    for i in range(15000):
        x=float(rng.uniform(-.071,.071));d=float(rng.uniform(.027,.113));kind=sparse.zone(x,d)
        if kind is None:continue
        hit,n,_,_=tree.ray_cast(Vector((x,-.6,eye-d)),Vector((0,1,0)))
        if hit is None or hit.y>-.045 or n.y>-.08:continue
        # Feather density just inside the upper growth edge; no straight stamped line.
        if kind=='cheek' and d-(.079-.61*abs(x))<.007 and rng.random()>.45:continue
        roots.append((hit+n*.0006,kind))
    if len(roots)<4000:raise ValueError('GROOM357_DENSITY')
    data=bpy.data.curves.new('357 clumped free beard','CURVE');data.dimensions='3D';data.bevel_depth=.000075;data.bevel_resolution=1
    for i in range(12):
        m=bpy.data.materials.new('357 dark chestnut fiber '+str(i));m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');v=.35+.85*i/11
        b.inputs['Base Color'].default_value=(.026*v,.016*v,.009*v,1);b.inputs['Roughness'].default_value=.40;b.inputs['Specular IOR Level'].default_value=.32;data.materials.append(m)
    lengths=[]
    for i,(root,kind) in enumerate(roots):
        pts=path(root,eye,i,kind);s=data.splines.new('POLY');s.points.add(len(pts)-1);s.material_index=int(rng.integers(0,12))
        for j,(p,co) in enumerate(zip(s.points,pts)):p.co=(*co,1);p.radius=(.05+.95*(1-j/(len(pts)-1))**.5)*float(rng.uniform(.8,1.15))
        lengths.append(float(np.linalg.norm(pts[-1]-pts[0])))
    ob.data=data;rig.data.pose_position=previous;rig['groom357']=1;bpy.context.view_layer.update()
    if h.action_signature(bpy)!=sig:raise ValueError('GROOM357_ACTION_DRIFT')
    report=dict(changed=True,source_preserved=True,actions_unchanged=True,action_signature=sig,roots=len(roots),length_range=[min(lengths),max(lengths)],scope='Dense shape proof on qualified sparse root region; art and full motion remain separate.')
    (out/'groom357.json').write_text(json.dumps(report,indent=2)+'\n');return report
