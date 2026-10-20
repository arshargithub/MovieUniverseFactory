"""Fixed, seeded supporting-actor authoring. Existing contact owners are retained."""
import math
import random
import bpy
import bmesh
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
from sikh257_native import mesh, material, sphere
from sikh292_assets import surface

TAU=math.tau
ROOT=Path(__file__).resolve().parents[1]
DONOR=ROOT/'.runtime/assets/series01-body-blender-studio/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'
_head=None
_body=None

def anatomical_head():
    global _head,_body
    if _head is not None:return _head.copy()
    with bpy.data.libraries.load(str(DONOR),link=False) as (_,loaded):
        loaded.objects=['GEO-body_male_realistic']
    ob=loaded.objects[0];bpy.context.collection.objects.link(ob)
    for mod in ob.modifiers:
        if mod.type=='MULTIRES':mod.levels=min(2,mod.total_levels)
    bpy.context.view_layer.update()
    evaluated=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    data=bpy.data.meshes.new_from_object(evaluated)
    points=[ob.matrix_world@v.co for v in data.vertices]
    center=(-2.705880880355835-1.8228728771209717)/2
    ids=[i for i,p in enumerate(points) if p.z>1.40]
    mapping={i:j for j,i in enumerate(ids)}
    _body=(np.array([(p.x-center,p.y,p.z) for p in points],dtype=np.float32),
           [tuple(p.vertices) for p in data.polygons])
    vs=[]
    for i in ids:
        p=points[i];x=p.x-center;y=p.y;w=max(0,min(1,(1.47-p.z)/.04))
        # The head donor contains shoulder remnants. Keep a continuous neck,
        # but bring that hidden lower ring inside the garment, not a jagged crop.
        radius=max(1,math.sqrt((x/.058)**2+((y+.015)/.055)**2))
        vs.append((x*(1-w)+x/radius*w,y*(1-w)+((y+.015)/radius-.015)*w,p.z-1.55))
    fs=[tuple(mapping[i] for i in p.vertices) for p in data.polygons if all(i in mapping for i in p.vertices)]
    _head=bpy.data.meshes.new('319 evaluated anatomical donor');_head.from_pydata(vs,[],fs);_head.update()
    for p in _head.polygons:p.use_smooth=True
    bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(data)
    return _head.copy()

def hide(o):
    o.hide_render=True
    o.hide_viewport=True

def child_mesh(name,vs,fs,mat,parent):
    o=mesh(name,vs,fs,mat);o.parent=parent
    return o

def strands(name,paths,radius,mat,parent,taper=True):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D'
    data.resolution_u=2;data.bevel_resolution=1;data.bevel_depth=radius
    for path in paths:
        sp=data.splines.new('POLY');sp.points.add(len(path)-1)
        for i,(p,co) in enumerate(zip(sp.points,path)):
            p.co=(*co,1);p.radius=max(.08,1-i/(len(path)-1)*.93) if taper else (0.85 if i==len(path)-1 else 1)
    ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob)
    ob.parent=parent;data.materials.append(mat)
    return ob

def grid_faces(rows,cols,closed=False):
    return [(j*cols+k,j*cols+(k+1)%cols,(j+1)*cols+(k+1)%cols,(j+1)*cols+k)
            for j in range(rows-1) for k in range(cols if closed else cols-1)]

def cloth(name,low,high):
    mat=surface(name,[low,high],5,rough=.93,bump=.0005)
    b=mat.node_tree.nodes['Principled BSDF'];b.inputs['Sheen Weight'].default_value=.16
    return mat

def crown(frame,index,leader,blue):
    """Broad cloth courses with crossing fronts and a compressed, rounded crown."""
    height=.255 if leader else .19+.012*(index%3)
    width=.098 if leader else .092+.003*(index%3)
    def profile(z):
        u=max(0,min(1,(z-.045)/height))
        dome=math.sqrt(max(0,1-max(0,(u-.70)/.30)**2))
        return width*(.92+.10*math.sin(u*math.pi))*dome
    def point(a,z,offset=0):
        r=profile(z)+offset
        return (r*math.sin(a),.012-r*1.1*math.cos(a),z)
    vs=[]
    for j in range(33):
        z=.045+height*j/32
        for k in range(96):
            a=TAU*k/96
            vs.append(point(a,z,.0008*math.sin(a*11+j*.4)))
    fs=grid_faces(33,96,True);fs.append(tuple(range(32*96,33*96)))
    child_mesh('319 supported dumalla core',vs,fs,blue,frame)
    # The shallow courses overlap; their ends are buried into the underlying cloth.
    for layer in range(7 if leader else 6):
        vs=[];rows=128;cols=9
        for k in range(rows):
            a=TAU*k/rows
            crossing=.027*math.sin(a+.16+layer*.42)*(1-.35*layer/6)
            for j in range(cols):
                u=j/(cols-1)
                z=.046+layer*(height-.075)/7+.052*u+crossing
                fold=.002*math.sin(a*8+layer*.8)*math.sin(u*math.pi)
                vs.append(point(a,z,.0015+.0035*math.sin(u*math.pi)+fold*.6))
        fs=grid_faces(rows,cols)+[((rows-1)*cols+j,(rows-1)*cols+j+1,j+1,j) for j in range(cols-1)]
        ob=child_mesh('319 overlapping tied cloth course',vs,fs,blue,frame)
        sol=ob.modifiers.new('Folded cloth edge thickness','SOLIDIFY');sol.thickness=.0013
    metal=material('319 worn crown steel '+str(index),(.16,.18,.19))
    b=metal.node_tree.nodes['Principled BSDF'];b.inputs['Metallic'].default_value=.72;b.inputs['Roughness'].default_value=.48
    paths=[]
    for z in ([.15,.215] if leader else [.145]):
        paths.append([point(TAU*k/96,z+.014*math.sin(TAU*k/96),.006) for k in range(97)])
    strands('319 restrained chakram edges',paths,.0018,metal,frame)

def beard(frame,index,leader):
    rng=random.Random(31900+index)
    dark=material('319 beard dark '+str(index),(.022,.017,.012) if not leader else (.055,.050,.040))
    mid=material('319 beard mid '+str(index),(.040,.030,.019) if not leader else (.10,.09,.07))
    silver=material('319 beard light '+str(index),(.17,.16,.13) if leader else (.075,.055,.032))
    for m in (dark,mid,silver):
        m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.83
    length=.18 if leader else .12+.018*(index%4)
    head=next(o for o in frame.parent.children if o.name.startswith('secondary adult head292'))
    skin=BVHTree.FromPolygons([v.co for v in head.data.vertices],[tuple(p.vertices) for p in head.data.polygons])
    # A continuous cheek/jaw envelope supports tapered hair, not hanging cylinders.
    def flow(a,t,phase=0):
        side=abs(math.sin(a))
        x=.077*math.sin(a)*(1-.22*t)
        root_y=-.062-.059*math.cos(a)
        root_z=-.066+.080*side
        hit=skin.ray_cast(Vector((.077*math.sin(a),-.4,root_z)),Vector((0,1,0)))[0]
        correction=hit.y-.001-root_y if hit else 0
        y=root_y-.098*math.sin(math.pi*t*.55)+correction*(max(0,1-t/.45)**2)
        z=(-.066+.080*side)-length*t*(.82+.18*math.cos(a))
        x+=.007*math.sin(t*9+phase)*math.sin(math.pi*t)
        y+=.006*math.sin(t*12+phase)*math.sin(math.pi*t)
        return Vector((x,y,z))
    vs=[]
    for j in range(25):
        t=j/24
        for k in range(65):
            a=-1.48+2.96*k/64;p=flow(a,t)
            p.y+=.006;p.x*=.97
            vs.append(p)
    # Diagnostic backing retained but hidden: it protruded between differently
    # curved locks in study05. Coverage now comes from actual overlapping hairs.
    backing=child_mesh('319 connected beard shadow mass',vs,grid_faces(25,65),dark,frame)
    hide(backing)
    buckets=[[],[],[]]
    for i in range(6000 if leader else 2400):
        a=rng.uniform(-1.48,1.48);phase=round(a*8)*.77+rng.uniform(-.25,.25)
        start=rng.uniform(0,.13);end=rng.uniform(.80,1.05)
        shift=rng.uniform(-.003,.003)
        pts=[]
        for j in range(15):
            t=start+(end-start)*j/14
            p=flow(a,t,phase);p.y-=rng.uniform(.0002,.001)
            p.x+=shift
            pts.append(p)
        bucket=2 if rng.random()<(0.24 if leader else .045*(index%3)) else i%2
        buckets[bucket].append(pts)
    for i,paths in enumerate(buckets):
        strands('319 tapered beard fibers',paths,.00045 if leader else .0006,(dark,mid,silver)[i],frame)
    paths=[]
    for side in (-1,1):
        for i in range(500):
            u=rng.random();pts=[];length=rng.uniform(.72,1.15)
            root_z=rng.uniform(-.008,.006);root_y=rng.uniform(-.003,.002)
            phase=rng.uniform(0,math.tau)
            for j in range(12):
                t=j/11*length
                pts.append((side*(.003+.059*t),-.161+.025*t*t+root_y-.003*math.sin(t*5+phase),
                            -.026+root_z-.036*t*t+.002*math.sin(t*8+phase)))
            paths.append(pts)
    strands('319 moustache overlapping lip',paths,.00065,mid,frame)
    # Short sideburns bridge the beard into the temple rather than exposing a gap.
    paths=[]
    for side in (-1,1):
        for i in range(100):
            y=rng.uniform(-.065,-.047);z=rng.uniform(.030,.075)
            path=[]
            for k in range(6):
                yy=y-.012*k/5;zz=z-.043*k/5
                hit=skin.ray_cast(Vector((side*.25,yy,zz)),Vector((-side,0,0)))[0]
                if hit:path.append((hit.x+side*.0008,yy,zz))
            if len(path)>1:paths.append(path)
    strands('319 rooted sideburns',paths,.0006,dark,frame)

def face(head,frame,index,leader):
    # Preserve the anatomical donor; make age and material readable at the shot scale.
    skin=surface('319 warm skin '+str(index),[(.16,.078,.040),(.31,.17,.095)],8,rough=.7,bump=.00035)
    skin.node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value=.035
    head.data=anatomical_head();head.data.materials.clear();head.data.materials.append(skin)
    # Existing eye and brow placement remains bound to the inherited animated head.
    for o in list(frame.children):
        if o.name.startswith('secondary eye'):
            m=material('319 muted eye ivory '+str(index),(.23,.21,.17))
            o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(m)
        if o.name.startswith('secondary brow') and not o.name.startswith('secondary brown') and o.type=='CURVE':
            o.data=o.data.copy();o.data.bevel_depth*=.75
        if o.name.startswith('secondary brown iris'):
            m=material('319 deep brown iris '+str(index),(.018,.009,.003))
            o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(m)
    brow=material('319 natural brows '+str(index),(.017,.011,.007))
    surface_tree=BVHTree.FromPolygons([p.co for p in head.data.vertices],[tuple(p.vertices) for p in head.data.polygons])
    rng=random.Random(777+index);paths=[]
    for side in (-1,1):
        for i in range(160):
            u=rng.random();x=side*(.010+.044*u);z=.037+.003*math.sin(u*math.pi)+rng.uniform(-.0015,.0015)
            path=[]
            for j in range(5):
                xx=x+side*.004*j/4;zz=z+.003*j/4+rng.uniform(-.001,.001)
                hit=surface_tree.ray_cast(Vector((xx,-.4,zz)),Vector((0,1,0)))[0]
                if hit:path.append((xx,hit.y-.0018,zz))
            if len(path)>1:paths.append(path)
        pupil=sphere('319 pupil',(side*.032,-.132,.023),(.0027,.001,.003),brow);pupil.parent=frame
    strands('319 surface fitted eyebrows',paths,.0007,brow,frame)
    return skin

def neck_interface(root,head,skin):
    """Head-owned top and torso-owned base, without rotating donor shoulders."""
    s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
    coords=[v.co.copy() for v in head.data.vertices]
    lower=[];upper=[]
    for p in head.data.polygons:
        (lower if any(coords[i].z<-.065 for i in p.vertices) else upper).append(tuple(p.vertices))
    def extract(faces):
        ids=sorted({i for f in faces for i in f});mapping={old:i for i,old in enumerate(ids)}
        return [coords[i] for i in ids],[tuple(mapping[i] for i in f) for f in faces]
    vs,fs=extract(lower)
    neck=child_mesh('319 torso to head neck bridge',vs,fs,skin,head)
    vs,fs=extract(upper)
    data=bpy.data.meshes.new('319 upper anatomical head');data.from_pydata(vs,[],fs);data.update()
    for p in data.polygons:p.use_smooth=True
    data.materials.append(skin);head.data=data
    points=np.array([v.co[:] for v in neck.data.vertices])
    w=np.clip((-.075-points[:,2])/.05,0,1);w=w*w*(3-2*w)
    neck.shape_key_add(name='Basis')
    keys=[]
    for i in range(3):
        for j in range(4):
            key=neck.shape_key_add(name=f'Anchored neck transform {i}{j}')
            key.slider_min=-2;key.slider_max=2
            moved=points.copy();moved[:,i]+=w*(points[:,j] if j<3 else 1)
            key.data.foreach_set('co',moved.astype(np.float32).ravel());keys.append((i,j,key))
    rest=head.matrix_local.copy()
    for f in list(range(1,697,3))+[696]:
        s.frame_set(f);bpy.context.view_layer.update()
        correction=np.array(head.matrix_local.inverted()@rest)-np.eye(4)
        for i,j,key in keys:key.value=float(correction[i,j]);key.keyframe_insert('value',frame=f)
    s.frame_set(283)
    return neck

def beard_follow(frame,track):
    """Bounded gravity/inertial follow through; not a general hair simulator."""
    s=bpy.context.scene;times,positions,rotations=track
    seconds=(np.array(times)-1)/24
    acc=np.gradient(np.gradient(np.array(positions),seconds,axis=0),seconds,axis=0)
    values=[];state=Vector((0,0,0))
    for q,a in zip(rotations,acc):
        gravity=q.inverted()@Vector((0,0,-1))
        inertia=q.inverted()@Vector(a)
        target=Vector((gravity.x*.035-inertia.x*.0015,gravity.y*.035-inertia.y*.0015,0))
        target.x=max(-.014,min(.014,target.x));target.y=max(-.018,min(.018,target.y))
        state=state.lerp(target,.30);values.append(state.copy())
    for o in frame.children:
        if not o.name.startswith('319 tapered beard fibers'):continue
        o.shape_key_add(name='Basis')
        for axis in (0,1):
            key=o.shape_key_add(name='Bounded inertial follow '+str(axis));key.slider_min=-1
            for p in key.data:
                weight=max(0,min(1,(-p.co.z-.025)/.21))**1.5
                p.co[axis]+=.02*weight
            for f,value in zip(times,values):
                key.value=value[axis]/.02;key.keyframe_insert('value',frame=f)
    s.frame_set(283)

def garment(root,index,leader,blue):
    robe=next(o for o in root.children if o.name.startswith('commander fitted chola' if leader else 'secondary chola292'))
    robe.data=robe.data.copy();robe.data.materials.clear();robe.data.materials.append(blue)
    waist=.06 if leader else .88;bottom=-.16 if leader else .36;top=.52 if leader else 1.42
    # Remove evenly-spaced fluting. Rebuild the surface with tension at sash,
    # shoulder folds and a flared, irregular lower chola.
    for v in robe.data.vertices:
        p=v.co;a=math.atan2(p.y/.15,p.x/.23);z=p.z
        if z<=top:
            if z<waist:
                u=max(0,min(1,(waist-z)/(waist-bottom)))
                rx=.166+.115*u;ry=.121+.060*u
                fold=(.005+.012*u)*(math.sin(7*a+u*.6)+.35*math.sin(11*a-u))
            else:
                u=max(0,min(1,(z-waist)/(top-waist)))
                rx=.166+.067*math.sin(u*math.pi*.68);ry=.121+.033*math.sin(u*math.pi*.75)
                fold=.008*math.sin(a*5+u*7)+.005*math.sin(a*9-u*4)
                fold+=.012*math.exp(-((u-.13)/.13)**2)*math.sin(a*10)
            p.x=(rx+fold)*math.cos(a);p.y=(ry+fold*.65)*math.sin(a)
    sub=robe.modifiers.new('Soft tailored chola','SUBSURF');sub.levels=1;sub.render_levels=1
    for o in root.children:
        if o.hide_render:continue
        if o.type=='MESH' and ('sleeve' in o.name or 'trousers' in o.name):
            o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(blue)
            # Deformation is applied consistently to every baked pose.
            blocks=[block.data for block in o.data.shape_keys.key_blocks] if o.data.shape_keys else [o.data.vertices]
            for pts in blocks:
                if len(pts)!=312:continue
                for j in range(13):
                    center=sum((pts[j*24+k].co for k in range(24)),Vector())/24
                    for k in range(24):
                        p=pts[j*24+k];a=TAU*k/24
                        compress=math.exp(-((j-6)/2.8)**2)
                        f=1+.060*compress*math.sin(j*1.8+a*3)+.025*math.sin(a*5+j*.4)
                        p.co=center+(p.co-center)*f
            sub=o.modifiers.new('Continuous cloth folds','SUBSURF');sub.levels=1;sub.render_levels=1
    # Broaden and fold the sash without changing its placement or adding free flaps.
    for o in root.children:
        if o.name.startswith(('297 woven diagonal sash','297 cloth waist sash')):
            o.data=o.data.copy()
            for p in o.data.vertices:p.co.y-=.003*math.sin(p.co.z*73+p.co.x*18)
            sol=o.modifiers.new('Sash thickness','SOLIDIFY');sol.thickness=.002

def unified_garment(root,leader,mat):
    """Solid rest union, then inherit the already-baked sleeve motion.

    The topology is fixed after the rest union. Animation maps existing sleeve
    deltas onto it with a shoulder blend, rather than remeshing every frame.
    """
    s=bpy.context.scene;s.frame_set(283);bpy.context.view_layer.update()
    robe=next(o for o in root.children if o.name.startswith('commander fitted chola' if leader else 'secondary chola292'))
    sleeves=[o for o in root.children if not o.hide_render and o.name.startswith(
        '318 endpoint-bound leader sleeve' if leader else '297 crowd sleeve')]
    vs=[];fs=[];rest=[];trees=[]
    for o in [robe]+sleeves:
        # Use base evaluated shape coordinates, then union/smooth consistently.
        oldmods=[(m,m.show_viewport) for m in o.modifiers]
        for m,_ in oldmods:m.show_viewport=False
        bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
        points=[v.co.copy() for v in ev.data.vertices];offset=len(vs)
        vs.extend(points);fs.extend(tuple(offset+i for i in p.vertices) for p in ev.data.polygons)
        n=64 if o==robe else 24
        fs.append(tuple(offset+i for i in reversed(range(n))))
        fs.append(tuple(offset+i for i in range(len(points)-n,len(points))))
        if o!=robe:
            rest.append(np.array(points,dtype=np.float32))
            tree=KDTree(len(points))
            for i,p in enumerate(points):tree.insert(p,i)
            tree.balance();trees.append(tree)
        for m,state in oldmods:m.show_viewport=state
    new=child_mesh('319 continuous sewn chola',vs,fs,mat,root)
    bpy.ops.object.select_all(action='DESELECT');new.select_set(True);bpy.context.view_layer.objects.active=new
    rem=new.modifiers.new('Rest-only sewn volume union','REMESH');rem.mode='VOXEL';rem.voxel_size=.0045;rem.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=rem.name)
    sm=new.modifiers.new('Relax sewn shoulders','SMOOTH');sm.factor=.55;sm.iterations=4
    bpy.ops.object.modifier_apply(modifier=sm.name)
    for p in new.data.polygons:p.use_smooth=True
    if leader:
        base=np.array([v.co[:] for v in new.data.vertices],dtype=np.float32)
        # Three-neighbor interpolation avoids copying a single vertex's jagged field.
        maps=[];weights=[]
        for tree in trees:
            near=[tree.find_n(Vector(p),3) for p in base]
            ids=np.array([[x[1] for x in row] for row in near])
            dist=np.array([[x[2] for x in row] for row in near])
            inverse=1/np.maximum(.0001,dist);inverse/=inverse.sum(axis=1)[:,None]
            ring=(ids*inverse).sum(axis=1)/24
            w=np.clip(ring/2.2,0,1)*np.clip((.035-dist[:,0])/.022,0,1)
            maps.append((ids,inverse));weights.append(w)
        total=np.maximum(1,np.sum(weights,axis=0))
        weights=[w/total for w in weights]
        new.shape_key_add(name='Basis')
        times=list(range(1,697,4))
        if times[-1]!=696:times.append(696)
        for o in sleeves:
            for m in o.modifiers:m.show_viewport=False
        for i,f in enumerate(times):
            s.frame_set(f);bpy.context.view_layer.update();result=base.copy()
            for o,reference,(ids,ws),w in zip(sleeves,rest,maps,weights):
                ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
                pts=np.array([v.co[:] for v in ev.data.vertices],dtype=np.float32)
                assert pts.shape==reference.shape
                delta=((pts-reference)[ids]*ws[:,:,None]).sum(axis=1)
                result+=delta*w[:,None]
            key=new.shape_key_add(name=f'bound{f:04d}')
            key.data.foreach_set('co',result.astype(np.float32).ravel())
            for ff,value in ((times[i-1] if i else 0,0),(f,1),(times[i+1] if i+1<len(times) else 697,0)):
                key.value=value;key.keyframe_insert('value',frame=ff)
        for fc in new.data.shape_keys.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
            for p in fc.keyframe_points:p.interpolation='LINEAR'
    for o in [robe]+sleeves:hide(o)
    s.frame_set(283)
    return new

def anatomical_garment(root,leader,mat):
    """Continuous donor-derived shoulder and arm topology, posed to existing owners."""
    s=bpy.context.scene;s.frame_set(283);bpy.context.view_layer.update()
    source,polygons=_body
    offset=-.90 if leader else .01
    waist=.06 if leader else .88
    # Keep the clothed torso/arms, excluding neck/head, hands and pelvis.
    ids=np.where((source[:,2]<1.435)&
        (((np.abs(source[:,0])<.19)&(source[:,2]>waist-offset-.045))|
         ((np.abs(source[:,0])>=.19)&(source[:,2]>.89))))[0]
    mapping={int(i):j for j,i in enumerate(ids)}
    vs=source[ids].copy();faces=[tuple(mapping[i] for i in p) for p in polygons if all(i in mapping for i in p)]
    shirt=child_mesh('319 anatomically supported chola upper',vs,faces,mat,root)
    bm=bmesh.new();bm.from_mesh(shirt.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(shirt.data);bm.free()
    # Suppress sculpted muscle/nipple detail before forming fabric over anatomy.
    bpy.ops.object.select_all(action='DESELECT');shirt.select_set(True);bpy.context.view_layer.objects.active=shirt
    smooth=shirt.modifiers.new('Fabric envelope over anatomy','SMOOTH');smooth.factor=.65;smooth.iterations=14
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    if len(shirt.data.vertices)>24000:
        dec=shirt.modifiers.new('Shot scaled garment topology','DECIMATE');dec.ratio=24000/len(shirt.data.vertices)
        bpy.ops.object.modifier_apply(modifier=dec.name)
    shirt.data.update()
    # Snapshot all normals before moving ANY vertex. Reading mutable cached
    # normals during sequential edits corrupted the earlier inflation surface.
    coords=np.array([v.co[:] for v in shirt.data.vertices],dtype=np.float32)
    normals=np.array([v.normal[:] for v in shirt.data.vertices],dtype=np.float32)
    amount=.007+.002*np.sin(coords[:,2]*37+coords[:,0]*11)+.002*np.sin(coords[:,2]*63-coords[:,0]*18)
    coords+=normals*amount[:,None]
    # Fabric bridges the pectoral details instead of reproducing bare anatomy.
    for p in coords:
        if abs(p[0])<.205 and .97<p[2]<1.37 and p[1]<-.04:
            u=(p[2]-.97)/.40
            support=-(.123+.032*math.sin(u*math.pi))*math.sqrt(max(.01,1-(p[0]/.29)**2))
            support+=.003*math.sin(p[0]*32+p[2]*25)*math.sin(u*math.pi)
            w=min(1,(p[2]-.97)/.05,(1.37-p[2])/.07,(.205-abs(p[0]))/.045)
            p[1]=p[1]*(1-w)+support*w
    shirt.data.vertices.foreach_set('co',coords.ravel())
    shirt.data.update()
    original=np.array([v.co[:] for v in shirt.data.vertices],dtype=np.float32)
    sleeves=sorted([o for o in root.children if not o.hide_render and o.name.startswith(
        '318 endpoint-bound leader sleeve' if leader else '297 crowd sleeve')],key=lambda o:o.name)
    assert len(sleeves)==2
    for o in sleeves:
        for mod in o.modifiers:mod.show_viewport=False
    # Rest joint locations measured from the neutral donor inspection.
    shoulders=[Vector((side*.18,0,1.36)) for side in (-1,1)]
    elbows=[Vector((side*.285,-.005,1.13)) for side in (-1,1)]
    cuff_ids={str(side):np.where((original[:,0]*side>.25)&(original[:,2]<.915))[0].tolist() for side in (-1,1)}
    assert all(len(ids)>8 for ids in cuff_ids.values())
    wrists=[Vector(original[cuff_ids[str(side)]].mean(axis=0)) for side in (-1,1)]
    import json
    shirt['cuff_indices']=json.dumps(cuff_ids)
    def ease(a):
        a=np.clip(a,0,1);return a*a*(3-2*a)
    armweight=ease((np.abs(original[:,0])-.145)/.085)
    foreweight=ease((1.19-original[:,2])/.12)
    times=list(range(1,697,4)) if leader else [283]
    if leader and times[-1]!=696:times.append(696)
    poses=[]
    for f in times:
        s.frame_set(f);result=original.copy();result[:,2]+=offset
        for k,(o,a,b,c) in enumerate(zip(sleeves,shoulders,elbows,wrists)):
            ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
            pts=np.array([v.co[:] for v in ev.data.vertices])
            assert len(pts)==312
            target=[Vector(pts[j*24:(j+1)*24].mean(axis=0)) for j in (0,6,12)]
            ta,tb,tc=target
            # Orient by the actual side rather than a numeric object suffix.
            side=-1 if ta.x<0 else 1
            a,b,c=[Vector((side*abs(p.x),p.y,p.z)) for p in (a,b,c)]
            mask=(original[:,0]*side>0)
            q1=(b-a).rotation_difference(tb-ta);q2=(c-b).rotation_difference(tc-tb)
            up=(original-np.array(a))@np.array(q1.to_matrix()).T+np.array(ta)
            low=(original-np.array(b))@np.array(q2.to_matrix()).T+np.array(tb)
            # Preserve the donor's radial form while matching segment lengths.
            axis=np.array((b-a).normalized())
            along=(original-np.array(a))@axis
            up+=along[:,None]*np.array((tb-ta).normalized())[None,:]*((tb-ta).length/(b-a).length-1)
            axis=np.array((c-b).normalized());along=(original-np.array(b))@axis
            low+=along[:,None]*np.array((tc-tb).normalized())[None,:]*((tc-tb).length/(c-b).length-1)
            moved=up*(1-foreweight[:,None])+low*foreweight[:,None]
            w=(armweight*mask)[:,None]
            result=result*(1-w)+moved*w
        poses.append(result.astype(np.float32))
    shirt.data.vertices.foreach_set('co',poses[0].ravel())
    if leader:
        shirt.shape_key_add(name='Basis')
        for i,(f,pts) in enumerate(zip(times,poses)):
            key=shirt.shape_key_add(name=f'bound{f:04d}');key.data.foreach_set('co',pts.ravel())
            for ff,value in ((times[i-1] if i else 0,0),(f,1),(times[i+1] if i+1<len(times) else 697,0)):
                key.value=value;key.keyframe_insert('value',frame=ff)
        for fc in shirt.data.shape_keys.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
            for p in fc.keyframe_points:p.interpolation='LINEAR'
    robe=next(o for o in root.children if o.name.startswith('commander fitted chola' if leader else 'secondary chola292'))
    # Preserve the flared chola lower section, hidden overlap under the waist sash.
    keep=[v.index for v in robe.data.vertices if v.co.z<waist+.04];mp={v:i for i,v in enumerate(keep)}
    lower=child_mesh('319 flared chola skirt',[robe.data.vertices[i].co[:] for i in keep],
        [tuple(mp[i] for i in p.vertices) for p in robe.data.polygons if all(i in mp for i in p.vertices)],mat,root)
    sub=lower.modifiers.new('Soft lower folds','SUBSURF');sub.levels=1;sub.render_levels=1
    for o in [robe]+sleeves:hide(o)
    s.frame_set(283)
    return shirt

def hands(root,skin):
    for old in list(root.children):
        if not old.name.startswith(('leader palm','secondary closed hand')):continue
        # The old animated palm remains the contact controller, not visible geometry.
        hide(old)
        palm=sphere('319 shaped palm',(.002,.022,-.002),(.027,.022,.042),skin);palm.parent=old
        paths=[]
        for j in range(4):
            z=-.030+j*.019
            paths.append([(.022,.022,z),(.035,.008,z+.001),(.032,-.012,z+.002),
                          (.014,-.024,z+.001),(-.008,-.023,z),(-.023,-.011,z-.002),(-.018,.003,z-.003)])
        strands('319 closed fingers rooted at knuckles',paths,.010,skin,old,taper=False)
        strands('319 opposing thumb',[[
            (-.023,.026,.027),(-.036,.013,.030),(-.034,-.008,.025),(-.020,-.026,.016),
            (-.003,-.029,.010)]],.011,skin,old,taper=False)

def chest_layer(root,body,mat,leader):
    """A supported overlapping chola front; no floating tube or shoulder flap."""
    waist=.06 if leader else .88;top=.515 if leader else 1.425
    surface_tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],[tuple(p.vertices) for p in body.data.polygons])
    vs=[];rows=41;cols=21
    for j in range(rows):
        t=j/(rows-1);z=top*(1-t)+waist*t
        right=-.060+.21*t
        left=-.085-.065*math.sin(t*math.pi)
        for k in range(cols):
            u=k/(cols-1);x=left+(right-left)*u
            hit=surface_tree.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)))[0]
            if hit is None:
                near=surface_tree.find_nearest(Vector((x,-.13,z)))[0]
                y=near.y
            else:y=hit.y
            y-=.002+.003*math.sin(u*math.pi)*math.sin(t*4)
            vs.append((x,y,z))
    panel=child_mesh('319 overlapping chola chest panel',vs,grid_faces(rows,cols),mat,root)
    sol=panel.modifiers.new('Turned panel edge','SOLIDIFY');sol.thickness=.0015
    edge=[vs[j*cols+cols-1] for j in range(rows)]
    strands('319 chola folded placket',[edge],.0018,mat,root,taper=False)
    # A softly rolled, body-supported collar binds the cut garment neckline.
    vs=[];base=.515 if leader else 1.425
    for j in range(7):
        u=j/6
        for k in range(96):
            a=math.tau*k/96;r=.075-.011*u
            vs.append((r*math.sin(a),-.015+r*.88*math.cos(a),base+.022*u))
    collar=child_mesh('319 bound chola neckline',vs,grid_faces(7,96,True),mat,root)
    sol=collar.modifiers.new('Turned collar cloth','SOLIDIFY');sol.thickness=.002
    for o in root.children:
        if not o.name.startswith('297 woven diagonal sash'):continue
        for p in o.data.vertices:
            hit=surface_tree.ray_cast(Vector((p.co.x,-.6,p.co.z)),Vector((0,1,0)))[0]
            if hit is not None:p.co.y=hit.y-.010

def build(follow=False):
    s=bpy.context.scene;s.frame_set(1)
    roots=[bpy.data.objects['mounted leader']]+sorted(
        [o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:o.name)
    report=[];heads=[]
    for index,root in enumerate(roots):
        leader=index==0
        frame=next(o for o in root.children if o.name.startswith('secondary facial and crown frame292'))
        head=next(o for o in root.children if o.name.startswith('secondary adult head292'))
        # Hide all obsolete contributors, including earlier hidden prototypes.
        for o in list(frame.children):
            if any(w in o.name for w in ('beard','moustache','crown','turban','chakram')):hide(o)
        blue=cloth('319 indigo cloth '+str(index),
                   (.006+.001*(index%3),.014+.003*(index%4),.055+.008*(index%3)),
                   (.025+.003*(index%3),.058+.004*(index%4),.18+.008*(index%3)))
        skin=face(head,frame,index,leader);crown(frame,index,leader,blue);beard(frame,index,leader)
        if not leader:
            # Three related, visibly distinct facial proportions; deform the
            # skin and its feature frame together, not eyes independently.
            proportions=((.95,1.02,1.02),(1.04,.98,.98),(1,1,1))[index%3]
            head.scale=proportions;frame.scale=proportions
        neck_interface(root,head,skin)
        garment(root,index,leader,blue);body=anatomical_garment(root,leader,blue)
        chest_layer(root,body,blue,leader);hands(root,skin)
        heads.append(frame)
        report.append({'root':root.name,'head':head.name,'attachment':frame.name,
                       'leader':leader,'inherited_contact_animation':True})
    if follow:
        times=list(range(1,697,3))+[696]
        tracks={frame.name:(times,[],[]) for frame in heads}
        for f in times:
            s.frame_set(f)
            for frame in heads:
                tracks[frame.name][1].append(np.array(frame.matrix_world.translation[:]))
                tracks[frame.name][2].append(frame.matrix_world.to_quaternion().copy())
        for frame in heads:beard_follow(frame,tracks[frame.name])
    s.frame_set(283);bpy.context.view_layer.update()
    return report
