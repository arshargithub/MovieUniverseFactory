"""Bounded reference-led hair and lower-neck revision; fixed local operations."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'dressing-motion-build-04/character-dressed.blend'
SOURCE_SHA='77fa1fad9da232a6af156f0f62b1a3fd994f4aa28e89011643ea74574e77526e'
SELECTED=BASE/'hair-anatomy-build-05/character-hair-anatomy.blend'
SELECTED_SHA='a6198e7bbe061e26e96cff3d4ef44d234096c435984611d2cd829701bd9a6d8a'
REVIEW_SELECTED=BASE/'hair-anatomy-build-07/character-hair-anatomy.blend'
REVIEW_SHA='6ed538f7ba6efd95ae623fc457b1e22985f40ff8fe88a35e4841aa3142e46e06'
FINAL_SELECTED=BASE/'hair-anatomy-build-10/character-hair-anatomy.blend'
FINAL_SHA='3158f62b8eba1ce3c8244e8ba00773efceb3fc2892e8d4902f529a82dc8db8b0'
VIEWS=(('front',0),('left',-45),('right',45),('back',180))

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def selected_source(candidate):
    return {5:(SELECTED,SELECTED_SHA),7:(REVIEW_SELECTED,REVIEW_SHA),10:(FINAL_SELECTED,FINAL_SHA)}[candidate]

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:raise ValueError('Exact job required')
    if type(job['candidate']) is not int or (job['operation'],job['candidate']) not in (('inspect',0),('build',1),('build',2),('build',3),('build',4),('build',5),('build',6),('build',7),('build',8),('build',9),('build',10),('verify',5),('verify',7),('verify',10),('look',5),('look',6),('look',7)):raise ValueError('Unsupported operation')
    if SOURCE.is_symlink() or digest(SOURCE)!=SOURCE_SHA:raise ValueError('Pinned source changed')
    if job['operation'] in ('verify','look'):
        p,h=selected_source(job['candidate'] if job['operation']=='verify' else 5)
        if p.is_symlink() or digest(p)!=h:raise ValueError('Selected source changed')
    out=BASE/f'hair-anatomy-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or shutil.disk_usage(BASE).free<5_000_000_000:raise ValueError('Output exists or disk low')
    return out

def is_hair(o):return any(s in o.name.lower() for s in ('hair','fiber','groom','scalp'))

def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)

def neck_relief(x,y,z):
    if z>=-.82 or z<=-1.90 or y>=.04:return 0.
    ax=abs(x);fade=smooth((-.82-z)/.22)*smooth((z+1.90)/.20)*smooth((.04-y)/.45)
    path=.16+.45*smooth((z+1.60)/.72)
    scm=.040*math.exp(-((ax-path)/.105)**2-((z+1.22)/.45)**4)
    clav_z=-1.635+.065*math.sin(min(ax/1.45,1)*math.pi)-.012*ax
    clav=.022*math.exp(-((z-clav_z)/.090)**2)*smooth(ax/.2)*math.exp(-(ax/1.5)**8)
    notch=.018*math.exp(-(x/.16)**2-((z+1.54)/.11)**2)
    return (scm+clav-notch)*fade

def anatomy():
    import bpy
    ob=bpy.data.objects['MF_continuous_head_neck'];changes=[]
    for v in ob.data.vertices:
        delta=neck_relief(*v.co)
        if delta:
            v.co.y-=delta
            for key in ob.data.shape_keys.key_blocks:key.data[v.index].co.y-=delta
            changes.append(delta)
    ob.data.update()
    return {'moved':len(changes),'max_displacement':max(map(abs,changes))}

def spline(points,t):
    n=len(points)-1;f=max(0.,min(n-1e-9,t*n));i=int(f);u=f-i
    a,b,c,d=[points[max(0,min(n,j))] for j in (i-1,i,i+1,i+2)]
    return tuple(.5*((2*b[k])+(-a[k]+c[k])*u+(2*a[k]-5*b[k]+4*c[k]-d[k])*u*u+(-a[k]+3*b[k]-3*c[k]+d[k])*u**3) for k in range(3))

def groom(candidate):
    import bpy,bmesh,random
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from reference_dressing import mesh_object
    rng=random.Random(614)
    for o in bpy.context.scene.objects:
        if is_hair(o):o.hide_render=True
    body=bpy.data.objects['MF_continuous_head_neck'];bpy.context.view_layer.update()
    tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    mats=[]
    for i,color in enumerate(((.009,.0035,.0018,1),(.024,.009,.0045,1),(.048,.019,.008,1),(.084,.035,.014,1))):
        m=bpy.data.materials.new('MF_loose_hair_tone_'+str(i));m.use_nodes=True
        p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=.76;p.inputs['Specular IOR Level'].default_value=.12
        mats.append(m)
    if candidate>=5:
        ref=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01/frontal-v02-individualized.png'
        if ref.is_symlink() or digest(ref)!='7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75':raise ValueError('Reference changed')
        im=bpy.data.images.load(str(ref),check_existing=True);im.pack()
        illustrated=mats[1].copy();illustrated.name='MF_loose_hair_illustrated_lock'
        n,l=illustrated.node_tree.nodes,illustrated.node_tree.links;p=n['Principled BSDF']
        coords=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY_ADD';mapping.inputs[1].default_value=(.08,.06,0);mapping.inputs[2].default_value=(.26,.77,0)
        l.new(coords.outputs['UV'],mapping.inputs[0]);tex=n.new('ShaderNodeTexImage');tex.image=im;l.new(mapping.outputs[0],tex.inputs['Vector'])
        rgb=n.new('ShaderNodeSeparateColor');l.new(tex.outputs[0],rgb.inputs[0]);mask=n.new('ShaderNodeMath');mask.operation='GREATER_THAN';l.new(rgb.outputs['Red'],mask.inputs[0]);l.new(rgb.outputs['Blue'],mask.inputs[1])
        mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.013,.005,.0025,1);l.new(mask.outputs[0],mix.inputs[0]);l.new(tex.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
        p.inputs['Specular IOR Level'].default_value=.05;p.inputs['Roughness'].default_value=.9
    # Continuous scalp foundation: cropped original-head shell, no scarf pixels.
    source=bpy.data.objects['FBHead'];dg=bpy.context.evaluated_depsgraph_get()
    mesh=bpy.data.meshes.new_from_object(source.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
    bm=bmesh.new();bm.from_mesh(mesh)
    from dressing_motion_fit import hairline
    def edge(x,y):
        result=hairline(x,y)*(1-smooth((y+.05)/.5))-.36*smooth((y+.05)/.5)
        if candidate>=2:result-=.14*smooth((abs(x)-.69)/.2)*(1-smooth((y+.12)/.30))
        if candidate>=3:result-=.12*smooth((abs(x)-.78)/.15)*smooth((y+.55)/.25)
        return result
    remove=[]
    for f in bm.faces:
        c=f.calc_center_median()
        ear=abs(c.x)>.91 and -.10<c.y<.43 and c.z<.13
        if c.z<edge(c.x,c.y)-.07 or ear:remove.append(f)
    bmesh.ops.delete(bm,geom=remove,context='FACES');bm.normal_update()
    for v in bm.verts:v.co+=v.normal*(.002 if candidate>=2 else .012)
    bm.to_mesh(mesh);bm.free();mesh.materials.clear();mesh.materials.append(mats[0])
    for p in mesh.polygons:p.material_index=0;p.use_smooth=True
    base=bpy.data.objects.new('MF_loose_hair_scalp',mesh);bpy.context.scene.collection.objects.link(base)
    base.matrix_world=source.matrix_world.copy()
    if candidate>=2:
        mat=mats[0].copy();mesh.materials[0]=mat
        attr=mesh.attributes.new('MF_hair_root_density','FLOAT','POINT')
        for v in mesh.vertices:attr.data[v.index].value=smooth((v.co.z-edge(v.co.x,v.co.y))/.11)
        a=mat.node_tree.nodes.new('ShaderNodeAttribute');a.attribute_name=attr.name
        mat.node_tree.links.new(a.outputs['Fac'],mat.node_tree.nodes['Principled BSDF'].inputs['Alpha'])
    if candidate>=3:
        # A continuous under-groom closes gaps between layered surface locks.
        verts=[];faces=[];nu,nv=96,60
        for i in range(nu+1):
            a=-1.75+3.5*i/nu
            for j in range(nv+1):
                t=j/nv;z=.70-(2.85+.08*math.sin(a*7))*t
                r=.83+.15*smooth(t/.3)+.024*math.sin(a*11+t*7)*math.sin(math.pi*t)
                verts.append((r*math.sin(a),.13+(.73+.17*smooth(t/.3))*math.cos(a),z))
        for i in range(nu):
            for j in range(nv):faces.append((i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1))
        under=mesh_object('MF_loose_hair_underlayer',verts,faces,mats[0],1)
        # Transparent taper only at the last few centimeters, under longer locks.
        mat=mats[0].copy();under.data.materials[0]=mat
        attr=under.data.attributes.new('MF_hair_underlayer_density','FLOAT','POINT')
        for v in under.data.vertices:attr.data[v.index].value=smooth((1-(v.index%(nv+1))/nv)/.15)
        node=mat.node_tree.nodes.new('ShaderNodeAttribute');node.attribute_name=attr.name
        mat.node_tree.links.new(node.outputs['Fac'],mat.node_tree.nodes['Principled BSDF'].inputs['Alpha'])
    # Retain only the useful frontal illustrated crown overlay, without blue cloth.
    crown=bpy.data.objects['MF_reference_crown_hair'];crown.hide_render=False
    attr=crown.data.attributes['MF_crown_edge_blend']
    for v in crown.data.vertices:attr.data[v.index].value*=1-smooth((v.co.y+.30)/.50)
    for m in crown.data.materials:
        n,l=m.node_tree.nodes,m.node_tree.links;p=n.get('Principled BSDF')
        color=p.inputs['Base Color'].links[0].from_socket
        rgb=n.new('ShaderNodeSeparateColor');l.new(color,rgb.inputs[0])
        brown=n.new('ShaderNodeMath');brown.operation='GREATER_THAN';l.new(rgb.outputs['Red'],brown.inputs[0]);l.new(rgb.outputs['Blue'],brown.inputs[1])
        alpha=p.inputs['Alpha'].links[0].from_socket
        mult=n.new('ShaderNodeMath');mult.operation='MULTIPLY';l.new(alpha,mult.inputs[0]);l.new(brown.outputs[0],mult.inputs[1]);l.new(mult.outputs[0],p.inputs['Alpha'])
    guides=[]
    for side in (-1,1):
        if candidate>=8:
            # Place the lowest frontal guides on the *front* scalp surface,
            # not the topmost intersection of a downward ray. That distinction
            # matters around the widow's peak and the temporal recession.
            for k in range(18):
                f=k/17;phase=rng.uniform(0,math.tau);points=[]
                for x,z in ((.026,.855+.32*f),(.30,.90+.28*f),(.60,.72+.25*f),(.82,.47+.20*f),(.94,.17+.15*f)):
                    hit,normal,_,_=tree.ray_cast(Vector((side*x,-3,z)),Vector((0,1,0)),5)
                    if hit is None and candidate>=9:
                        hit,normal,_,distance=tree.find_nearest(Vector((side*x,-.4,z)))
                        if hit is None or distance>.35:raise ValueError(f'Hairline support too far at {(x,z)}')
                    if hit is None:raise ValueError('Hairline support absent')
                    points.append(tuple(hit+normal*.035))
                points.extend([(side*1.00,.09+.20*f,-.55),(side*(1.01+.07*math.sin(phase)),.29+.18*f,-1.52-.2*f)])
                guides.append((points,.035+.008*rng.random(),phase,'hairline'))
        if candidate>=7:
            # Continue the center part over the occiput; avoid two exposed
            # comb-shaped side caps ending abruptly above the rear locks.
            for k in range(12):
                f=k/11;phase=rng.uniform(0,math.tau)
                points=[(side*.025,.15+.65*f,1.22-.19*f),
                    (side*(.17+.36*f),.75+.15*f,1.00-.12*f),
                    (side*(.20+.58*f),1.00,.55),
                    (side*(.23+.60*f),1.14,-.15),
                    (side*(.22+.64*f),1.12,-1.1),
                    (side*(.20+.65*f),1.03,-1.88-.20*rng.random())]
                guides.append((points,.065,phase,'occipital'))
        if candidate>=6:
            # Frontal flow must be actual volume too: the previous guides
            # began behind a flat, separately painted forehead patch.
            for k in range(20):
                f=k/19;phase=rng.uniform(0,math.tau);y=-.87+.65*f
                top=tree.ray_cast(Vector((side*.025,y,3)),Vector((0,0,-1)),5)[0]
                if top is None:raise ValueError('Frontal root support absent')
                points=[tuple(top+Vector((0,0,.03))),
                    (side*.42,-.78+.4*f,1.02+.08*f),
                    (side*.79,-.56+.40*f,.62+.12*f),
                    (side*.94,-.20+.4*f,.14),
                    (side*1.01,.04+.50*f,-.65),
                    (side*(.98+.12*math.sin(phase)),.27+.50*f,-1.6-.40*f)]
                guides.append((points,.048+.012*rng.random(),phase,'frontal'))
        for k in range(24):
            f=k/23;phase=rng.uniform(0,math.tau);end=-2.05-rng.random()*.50
            if candidate>=2:end+=.22
            if candidate>=4:end=-1.72-rng.random()*.43
            y=-.54+1.18*f
            top=tree.ray_cast(Vector((side*.045,y,3)),Vector((0,0,-1)),5)[0]
            if top is None:raise ValueError('Root support absent')
            root=top+Vector((0,0,.018))
            points=[tuple(root),(side*.55,y*.83,1.07),(side*(.98+.035*math.sin(k)),.04+.65*f,.36),
                (side*(1.00+.10*math.sin(phase)),.12+.74*f,-.35),
                (side*(.97+.09*math.sin(phase+2)),.18+.83*f,-1.12),
                (side*(1.05+.17*math.sin(phase+4)),.23+.77*f,end)]
            guides.append((points,.065+.035*rng.random(),phase,'side'))
        for k in range(14):
            f=k/13;phase=rng.uniform(0,math.tau);x=side*(.06+.72*f)
            points=[(side*.03,.45+.30*f,1.12),(side*(.14+.60*f),1.00,.65),
                (x,1.10,.00),(x+.06*math.sin(phase),1.08,-.8),
                (x+.10*math.sin(phase+2),1.04,-1.6),(x+.10*math.sin(phase+4),.93,(-1.85 if candidate>=4 else -2.30)-rng.random()*(.30 if candidate>=4 else .4))]
            guides.append((points,.070+.025*rng.random(),phase,'back'))
        if candidate>=5:
            for k in range(4):
                f=k/3;phase=rng.uniform(0,math.tau)
                points=[(side*(.76+.06*f),-.39,.72),(side*(.89+.04*f),-.23,.36),
                    (side*1.01,-.01,-.10),(side*(.86+.07*f),.13,-.65),
                    (side*1.10,.25,-1.35),(side*(1.12+.06*f),.40,-1.90+.16*f)]
                guides.append((points,.030+.010*f,phase,'temple'))
            for k in range(8):
                f=k/7;phase=rng.uniform(0,math.tau)
                points=[(side*(.32+.45*f),.52,1.05),(side*(.45+.43*f),.77,.70),
                    (side*(.50+.42*f),.92,.18),(side*(.46+.40*f),1.0,-.65),
                    (side*(.51+.40*f),1.0,-1.45),(side*(.48+.4*f),.92,-2.0+.13*math.sin(phase))]
                guides.append((points,.055,phase,'rear-fill'))
    curves=bpy.data.curves.new('MF_loose_hair_fibers','CURVE');curves.dimensions='3D';curves.bevel_depth=.0022;curves.bevel_resolution=1
    for m in mats:curves.materials.append(m)
    for gi,(points,width,phase,kind) in enumerate(guides):
        centers=[];steps=64
        for j in range(steps+1):
            t=j/steps;p=Vector(spline(points,t));weight=smooth(t/.22)*smooth((1-t)/.12)
            amp=(.085 if candidate>=2 else .032)
            p.x+=amp*math.sin(t*12+phase)*weight;p.y+=amp*.65*math.sin(t*9+phase)*weight
            hit,normal,_,distance=tree.find_nearest(p)
            if hit is not None:
                if t<.42:p=p*(1-smooth((.42-t)/.14))+(hit+normal*.026)*smooth((.42-t)/.14)
                elif (p-hit).dot(normal)<.035 and p.z>-1.90:p=hit+normal*.035
            centers.append(p)
        if candidate>=5:
            for _ in range(8):
                previous=[p.copy() for p in centers]
                for j in range(1,steps):
                    centers[j]=previous[j]*.6+(previous[j-1]+previous[j+1])*.2
                    if j>12 and centers[j].z>-1.90:
                        hit,normal,_,_=tree.find_nearest(centers[j])
                        if hit is not None and (centers[j]-hit).dot(normal)<.020:centers[j]=hit+normal*.020
        if candidate>=7:
            for j,p in enumerate(centers):
                t=j/steps
                if t<.5:
                    hit,normal,_,_=tree.find_nearest(p)
                    p+=normal*(.026*(.5+.5*math.sin(t*23+phase))*smooth(t/.07)*smooth((.5-t)/.16))
        verts=[];faces=[];frames=[]
        for j,p in enumerate(centers):
            t=j/steps;tangent=(centers[min(j+1,steps)]-centers[max(j-1,0)]).normalized()
            outward=Vector((p.x,p.y-.1,.08)).normalized();across=tangent.cross(outward).normalized();normal=across.cross(tangent).normalized();frames.append((across,normal))
            taper=smooth(t/.10)*smooth((1-t)/.22)
            for q in range(8):
                a=q*math.tau/8;verts.append(tuple(p+across*(width*taper*math.cos(a))+normal*(.016*taper*math.sin(a))))
        for j in range(steps):
            for q in range(8):faces.append((j*8+q,j*8+(q+1)%8,(j+1)*8+(q+1)%8,(j+1)*8+q))
        lock=mesh_object('MF_loose_hair_lock',verts,faces,illustrated if candidate>=5 else mats[1 if gi%4 else 0],0)
        if candidate>=5:
            uv=lock.data.uv_layers.new(name='MF_reference_hair_flow')
            for poly in lock.data.polygons:
                for li in poly.loop_indices:
                    vi=lock.data.loops[li].vertex_index;uv.data[li].uv=((vi%8)/7,(vi//8)/steps)
        if candidate>=10:
            density=lock.data.attributes.new('MF_hair_lock_density','FLOAT','POINT')
            for v in lock.data.vertices:
                t=(v.index//8)/steps;a=(v.index%8)*math.tau/8
                density.data[v.index].value=smooth(t/.075)*smooth((1-t)/.08)*(.30+.70*abs(math.sin(a))**.35)
        for si in range(44):
            offset=rng.uniform(-1,1);phase2=rng.uniform(0,math.tau);s=curves.splines.new('POLY');s.points.add(steps);s.material_index=rng.choices([0,1,2,3],[.32,.43,.21,.04])[0]
            for j,point in enumerate(s.points):
                t=j/steps;across,normal=frames[j];taper=smooth(t/.10)*smooth((1-t)/.22)
                p=centers[j]+across*(offset*width*taper)+normal*(.020*taper+.004*math.sin(t*18+phase2)*taper)
                if candidate>=2:p.z+=.045*math.sin(phase2)*smooth((t-.6)/.4)
                point.co=(*p,1);point.radius=max(.01,smooth(t/.045)*smooth((1-t)/.10))
    obj=bpy.data.objects.new('MF_loose_hair_fibers',curves);bpy.context.scene.collection.objects.link(obj)
    if candidate>=4:
        # Fit the backing below the actual outer lock envelope, rather than
        # guessing an ellipsoid that can protrude as an opaque horizontal band.
        verts=[];faces=[]
        for ob in bpy.context.scene.objects:
            if not ob.name.startswith('MF_loose_hair_lock'):continue
            offset=len(verts);verts.extend(v.co.copy() for v in ob.data.vertices)
            faces.extend(tuple(offset+i for i in p.vertices) for p in ob.data.polygons)
        support=BVHTree.FromPolygons(verts,faces)
        under=bpy.data.objects['MF_loose_hair_underlayer']
        for v in under.data.vertices:
            x,y,z=v.co;a=math.atan2(x,y-.13);c=Vector((0,.13,z));d=Vector((math.sin(a),math.cos(a),0))
            radii=[]
            for offset in (-.065,-.03,0,.03,.065):
                dd=Vector((math.sin(a+offset),math.cos(a+offset),0));hit=support.ray_cast(c+dd*3,-dd,3)[0]
                if hit is not None:radii.append((hit-c).dot(dd))
            if radii:v.co=c+d*max(.25,min(radii)-.065)
        mat=under.data.materials[0];n,l=mat.node_tree.nodes,mat.node_tree.links;p=n['Principled BSDF']
        uv=under.data.uv_layers.new(name='MF_underhair_flow')
        for poly in under.data.polygons:
            for li in poly.loop_indices:
                vi=under.data.loops[li].vertex_index;uv.data[li].uv=((vi//61)/96,(vi%61)/60)
        coords=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(170,2,1);l.new(coords.outputs['UV'],scale.inputs[0])
        noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;l.new(scale.outputs[0],noise.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.005,.0016,.0008,1);ramp.color_ramp.elements[1].color=(.032,.011,.005,1)
        l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
        density=under.data.attributes['MF_hair_underlayer_density']
        for v in under.data.vertices:
            u=(v.index//61)/96;t=(v.index%61)/60
            density.data[v.index].value=smooth(t/.15)*smooth((1-t)/.24)*smooth(u/.09)*smooth((1-u)/.09)
    # Fine temporal roots and short tapered wisps, not a solid cheek-covering cap.
    for side in (-1,1):
        count=90 if candidate>=3 else 36
        for i in range(count):
            f=i/(count-1);s=curves.splines.new('POLY');s.points.add(24);s.material_index=1 if i%4 else 2
            end=.72+.28*rng.random();scatter=rng.uniform(-.025,.025)
            for j,p in enumerate(s.points):
                t=j/24;guide=Vector((side*(.78+.17*t+.035*f),-.46+.48*t,.52-.55*t-.10*f))
                if candidate>=2:guide=Vector((side*(.78+.09*t+.025*f),-.46+.19*t,.47-.38*t-.055*f))
                if candidate>=3:
                    q=t*end;guide=Vector((side*(.83+.10*q+scatter),-.35+.24*q+.10*f,.63-.54*q-.09*f))
                hit,normal,_,_=tree.find_nearest(guide);point=hit+normal*(.006+.012*math.sin(math.pi*t))
                p.co=(*point,1);p.radius=(.34 if candidate>=3 else .55)*smooth(t/.07)*smooth((1-t)/.18)
    return {'guides':len(guides),'fiber_splines':len(curves.splines),'back_design':'inferred long loose continuation, not an unseen reference match'}

def integrated_hair_material(candidate):
    """Low-specularity broken strokes; keep forehead reference as underlay."""
    import bpy
    bpy.data.objects['MF_loose_hair_fibers'].data.bevel_depth=.0007
    m=bpy.data.materials['MF_loose_hair_illustrated_lock'];n,l=m.node_tree.nodes,m.node_tree.links;p=n['Principled BSDF']
    uv=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(36,5,1);l.new(uv.outputs['UV'],scale.inputs[0])
    if candidate>=7:scale.inputs[1].default_value=(20,8,1)
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=2;l.new(scale.outputs[0],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.30;ramp.color_ramp.elements[0].color=(.008,.003,.0015,1)
    ramp.color_ramp.elements[1].position=.76;ramp.color_ramp.elements[1].color=(.16,.081,.04,1)
    mid=ramp.color_ramp.elements.new(.57);mid.color=(.036,.015,.007,1)
    l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color']);l.new(ramp.outputs[0],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.25
    if candidate>=10:
        density=n.new('ShaderNodeAttribute');density.attribute_name='MF_hair_lock_density';l.new(density.outputs['Fac'],p.inputs['Alpha'])

def visibility(hair=True):
    import bpy
    for o in bpy.context.scene.objects:
        if o.type in ('MESH','CURVE'):
            o.hide_render=not (o.name=='MF_continuous_head_neck' or o.name.startswith('MF_aimable_eye_') or (hair and is_hair(o) and not o.hide_render))

def review(out):
    import bpy
    from hijab_donor import review as render
    visibility();render(bpy.context.scene,out,(0,-.05,-.60),4.9,VIEWS)
    # Independent clay test: no skin material, hair, costume or painted shadows.
    body=bpy.data.objects['MF_continuous_head_neck'];old=list(body.data.materials)
    material=bpy.data.materials.new('MF_anatomy_clay');material.use_nodes=True
    p=material.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.35,.35,.35,1);p.inputs['Roughness'].default_value=.8
    for i in range(len(old)):body.data.materials[i]=material
    visibility(False)
    render(bpy.context.scene,out,(0,-.05,-.85),4.8,tuple(('clay-'+name,a) for name,a in VIEWS))
    for i,m in enumerate(old):body.data.materials[i]=m

def verify(out,candidate=5):
    import bpy
    import numpy as np
    from neck_anatomy_review import signature
    from hijab_donor import material_signature,review as render
    from face_surface_integration import performance
    selected,selected_sha=selected_source(candidate)
    def array(data):return np.array([list(p.co) for p in data])
    def state():
        ob=bpy.data.objects['MF_continuous_head_neck'];mesh=ob.data
        return {'vertices':array(mesh.vertices),'keys':{k.name:array(k.data) for k in mesh.shape_keys.key_blocks},
            'uv':[[list(v.uv) for v in layer.data] for layer in mesh.uv_layers],
            'faces':[list(p.vertices) for p in mesh.polygons],
            'materials':[material_signature(m) for m in mesh.materials],
            'rest':[list(p.vector) for p in mesh.attributes['MF_performance_rest_position'].data],
            'protected':{o.name:signature(o) for o in bpy.context.scene.objects if o.type in ('MESH','CURVE') and not is_hair(o) and o!=ob}}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False);before=state()
    bpy.ops.wm.open_mainfile(filepath=str(selected),load_ui=False,use_scripts=False);after=state()
    original=before['vertices'];delta=np.array([(0,-neck_relief(*p),0) for p in original]);expected=original+delta
    fixed=np.linalg.norm(delta,axis=1)==0
    geometry_error=float(np.abs(after['vertices']-expected).max())
    assert geometry_error<2e-7 and np.array_equal(after['vertices'][fixed],original[fixed])
    key_errors={k:float(np.abs(after['keys'][k]-before['keys'][k]-delta).max()) for k in before['keys']}
    assert max(key_errors.values())<2e-7
    for k in ('uv','faces','materials','rest','protected'):assert before[k]==after[k],k
    # Check the complete existing trajectory numerically; no stronger acting.
    ob=bpy.data.objects['MF_continuous_head_neck'];keys=list(ob.data.shape_keys.key_blocks)[1:]
    samples=[]
    for frame in range(240):
        values,gaze=performance(frame/24)
        for key in keys:key.value=values.get(key.name,0)
        for side in ('Left','Right'):bpy.data.objects['MF_aimable_eye_'+side].rotation_euler.z=gaze
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        points=array(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices)
        assert np.isfinite(points).all()
        if frame in (0,239):assert np.array_equal(points,after['vertices'])
        samples.append(float(np.linalg.norm(points-after['vertices'],axis=1).max()))
    for key in keys:key.value=0
    for side in ('Left','Right'):bpy.data.objects['MF_aimable_eye_'+side].rotation_euler.z=0
    visibility()
    if candidate>=7:render(bpy.context.scene,out,(0,-.05,-.60),4.9,VIEWS)
    # Close views of the previously failing temple/ear region from each side.
    render(bpy.context.scene,out,(0,-.1,.18),2.9,(('temple-left',-55),('temple-right',55)))
    for label,values in [('blink',{'eyeBlinkLeft':1,'eyeBlinkRight':1}),('smile',performance(6)[0]),('jaw',{'jawOpen':.2})]:
        for key in keys:key.value=values.get(key.name,0)
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        render(bpy.context.scene,out,(0,-.05,-.60),4.9,((label,0),))
    for key in keys:key.value=0
    result={'source_sha256':SOURCE_SHA,'selected_sha256':selected_sha,'fresh_open_without_addon':True,
        'geometry_max_error':geometry_error,'shape_key_displacement_errors':key_errors,
        'protected_face_posterior_vertices':int(fixed.sum()),'protected_vertices_exact':True,
        'original_uvs_topology_materials_rest_attribute_other_nonhair_objects_exact':True,
        'all_240_existing_frames_finite':True,'neutral_return_exact':True,
        'all_images_packed':all(bool(i.packed_file or i.packed_files) for i in bpy.data.images if i.source=='FILE'),
        'no_new_motion_qualification':True,'source_unchanged':digest(SOURCE)==SOURCE_SHA,
        'selected_unchanged':digest(selected)==selected_sha,'handler_sha256':digest(Path(__file__))}
    assert result['all_images_packed']
    (out/'result.json').write_text(json.dumps(result,indent=2))

def run(job):
    out=validate(job);out.mkdir()
    if job['operation']=='verify':verify(out,job['candidate']);return
    import bpy
    if job['operation']=='look':
        from hijab_donor import review as render
        bpy.ops.wm.open_mainfile(filepath=str(SELECTED),load_ui=False,use_scripts=False)
        bpy.data.objects['MF_loose_hair_fibers'].data.bevel_depth=.0007
        m=bpy.data.materials['MF_loose_hair_illustrated_lock'];p=m.node_tree.nodes['Principled BSDF']
        m.node_tree.links.new(p.inputs['Base Color'].links[0].from_socket,p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.18
        if job['candidate']>=6:
            # Broad broken painted strokes aligned with each surface lock.
            # This affects only hair; no skin texture or reference image edits.
            n,l=m.node_tree.nodes,m.node_tree.links
            uv=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(36,5,1);l.new(uv.outputs['UV'],scale.inputs[0])
            noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=2;l.new(scale.outputs[0],noise.inputs['Vector'])
            ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.30;ramp.color_ramp.elements[0].color=(.008,.003,.0015,1)
            ramp.color_ramp.elements[1].position=.76;ramp.color_ramp.elements[1].color=(.22,.125,.064,1)
            mid=ramp.color_ramp.elements.new(.57);mid.color=(.05,.023,.01,1)
            l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color']);l.new(ramp.outputs[0],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.32
            crown=bpy.data.objects['MF_reference_crown_hair']
            for mat in crown.data.materials:
                nn,ll=mat.node_tree.nodes,mat.node_tree.links;pp=nn['Principled BSDF'];source=pp.inputs['Base Color'].links[0].from_socket
                shade=nn.new('ShaderNodeMixRGB');shade.blend_type='MULTIPLY';shade.inputs[0].default_value=1;shade.inputs[2].default_value=(.70,.70,.70,1);ll.new(source,shade.inputs[1]);ll.new(shade.outputs[0],pp.inputs['Base Color'])
            if job['candidate']==7:
                cm=m.copy();cm.name='MF_unified_crown_hair';a=cm.node_tree.nodes.new('ShaderNodeAttribute');a.attribute_name='MF_crown_edge_blend';cm.node_tree.links.new(a.outputs['Fac'],cm.node_tree.nodes['Principled BSDF'].inputs['Alpha'])
                for i in range(len(crown.data.materials)):crown.data.materials[i]=cm
                curves=bpy.data.objects['MF_loose_hair_fibers'].data
                for s in list(curves.splines)[:4400]:
                    for point in s.points:point.radius*=.03
        visibility();render(bpy.context.scene,out,(0,-.05,-.60),4.9,VIEWS)
        (out/'result.json').write_text(json.dumps({'read_only_look_diagnostic':True,'selected_unchanged':digest(SELECTED)==SELECTED_SHA}))
        return
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    changes={}
    if job['operation']=='build':
        changes={'anatomy':anatomy(),'hair':groom(job['candidate'])}
        if job['candidate']>=6:integrated_hair_material(job['candidate'])
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'character-hair-anatomy.blend'))
    inventory=[]
    for o in bpy.context.scene.objects:
        if o.type not in ('MESH','CURVE'):continue
        if o.hide_render:continue
        inventory.append({'name':o.name,'type':o.type,'bounds':[list(v) for v in o.bound_box]})
    (out/'inventory.json').write_text(json.dumps(inventory,indent=2))
    review(out)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'source_unchanged':digest(SOURCE)==SOURCE_SHA,'handler_sha256':digest(Path(__file__)),
        'changes':changes,'native_sha256':digest(out/'character-hair-anatomy.blend') if job['operation']=='build' else None},indent=2))

if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
