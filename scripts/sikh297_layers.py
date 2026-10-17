"""Reviewed supporting-layer construction; independent of final protagonist."""
import math
import bpy
import numpy as np
from mathutils import Vector
from sikh257_native import mesh,material,sphere
from sikh257_layout import tube,capsule,key
from sikh292_assets import surface
from movie_factory.sikh297_contract import TORCHES,flicker,band_radius,FRAMES

def hide(ob):ob.hide_render=True;ob.hide_viewport=True

def torchlight():
    s=bpy.context.scene
    # Small lift between practical pools, preserving the existing cool night key.
    bpy.data.lights['sky fill'].energy=1.0
    wood=surface('297 charred torch wood',[(.022,.012,.007),(.10,.065,.027)],9,bump=.003)
    iron=material('297 forged iron baskets',(.055,.046,.033));iron.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.6
    fire=material('297 amber flame',(.6,.12,.008));b=fire.node_tree.nodes['Principled BSDF'];b.inputs['Emission Color'].default_value=(1,.25,.018,1);b.inputs['Emission Strength'].default_value=5
    core=material('297 hot flame core',(1,.65,.12));b=core.node_tree.nodes['Principled BSDF'];b.inputs['Emission Color'].default_value=(1,.65,.16,1);b.inputs['Emission Strength'].default_value=8
    for i,(x,y,z) in enumerate(TORCHES):
        height=1.9 if z==0 else 1.55
        capsule('297 torch planted pole',(x,y,z-.04),(x,y,z+height),.036,wood)
        for k in range(8):
            a=k*math.tau/8
            tube('297 basket rib',[(x+.05*math.cos(a),y+.05*math.sin(a),z+height-.10),(x+.105*math.cos(a),y+.105*math.sin(a),z+height+.18)],.008,iron)
        for zz,rr in ((height-.06,.06),(height+.10,.09)):
            tube('297 basket band',[(x+rr*math.cos(a),y+rr*math.sin(a),z+zz) for a in np.linspace(0,math.tau,25)],.009,iron)
        for k,(mat,width,length) in enumerate(((fire,.075,.44),(core,.042,.28))):
            vs=[];fs=[]
            for j in range(13):
                u=j/12;radius=width*math.sin(math.pi*(.12+.88*u))
                for c in range(12):
                    a=c*math.tau/12;vs.append((radius*math.cos(a)+.05*u*u,radius*math.sin(a),length*u))
                if j:
                    for c in range(12):q=j*12+c;r=j*12+(c+1)%12;fs.append((q-12,r-12,r,q))
            ob=mesh('297 flame',vs,fs,mat);ob.location=(x,y,z+height-.01)
            ob.shape_key_add(name='Basis');bend=ob.shape_key_add(name='wind')
            for p in bend.data:
                u=p.co.z/length;p.co.x+=.09*u*u;p.co.y+=.04*u*math.sin(u*5)
            for f in range(1,FRAMES+1,3):
                t=(f-1)/24;bend.value=.5+.4*math.sin(t*5.4+i);bend.keyframe_insert('value',frame=f)
                ob.scale=(1,.85,flicker(t,i+k));ob.keyframe_insert('scale',frame=f)
        light=bpy.data.lights.new('297 torch pool','POINT');light.color=(1,.58,.28);light.energy=850;light.shadow_soft_size=.35
        ob=bpy.data.objects.new('297 torch pool',light);s.collection.objects.link(ob);ob.location=(x,y,z+height+.52)
        for f in range(1,FRAMES+1,3):light.energy=850*flicker((f-1)/24,i);light.keyframe_insert('energy',frame=f)
        # Broad bounce shares the fixture origin; not a camera-mounted light.
        if y==-5.6 or z>0:
            d=bpy.data.lights.new('297 torch bounced fill','AREA');d.energy=340;d.color=(1,.70,.44);d.size=1.5
            target=Vector((-.3,-3.6,1.5)) if z==0 else Vector((7.5,-29,4.8))
            o=bpy.data.objects.new('297 torch bounced fill',d);s.collection.objects.link(o);origin=Vector((x,y,z+height+.18));o.location=origin+(target-origin).normalized()*.4
            o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()

def fields():
    rng=np.random.default_rng(297)
    soil=surface('297 dry field soil',[(.028,.024,.012),(.105,.083,.036)],1.2,bump=.004)
    ground=bpy.data.objects['cultivated plain292'];ground.data.materials.clear();ground.data.materials.append(soil)
    # Retain foliage bases; add an intelligible cereal canopy instead of a lawn.
    mats=[surface('297 grain heads '+str(k),[(.065+k*.01,.085+k*.008,.027),(.24+k*.025,.25+k*.015,.095)],7,bump=.001) for k in range(3)]
    for k,mat in enumerate(mats):
        vs=[];fs=[]
        for i in range(40000):
            side=-1 if i%2 else 1;x=side*(2.55+int(rng.integers(0,65))*.21+float(rng.uniform(-.065,.065)));y=float(rng.uniform(-105,100))
            # Raised leader bank excludes crop penetration.
            if ((x-7.5)/8)**2+((y+29)/9)**2<1:continue
            h=float(rng.uniform(.55,.82));lean=float(rng.uniform(-.06,.09));n=len(vs)
            # A stem plus alternating grains and tapered ear, batched by material.
            vs.extend([(x-.004,y,0),(x+.004,y,0),(x+lean+.003,y,h),(x+lean-.003,y,h)]);fs.append((n,n+1,n+2,n+3))
            a=float(rng.uniform(0,math.tau));n=len(vs);dx=.17*math.cos(a);dy=.17*math.sin(a)
            vs.extend([(x,y,h*.4),(x+dx*.5-.012*math.sin(a),y+dy*.5+.012*math.cos(a),h*.69),(x+dx,y+dy,h*.65),(x+dx*.5+.012*math.sin(a),y+dy*.5-.012*math.cos(a),h*.69)]);fs.append((n,n+1,n+2,n+3))
            for j in range(6):
                z=h+j*.013;w=.016*math.sin((j+1)/7*math.pi);n=len(vs)
                vs.extend([(x+lean,y-.007,z-.007),(x+lean+w,y,z),(x+lean,y+.007,z+.015),(x+lean-w,y,z)])
                fs.append((n,n+1,n+2,n+3))
        mesh('297 coherent cereal ears '+str(k),vs,fs,mat)
    # Soft, irregular earth shoulders and broken low bunds, not straight tubes.
    earth=surface('297 cultivated bund soil',[(.06,.045,.023),(.24,.18,.09)],5,bump=.008)
    for side in (-1,1):
        vs=[];fs=[]
        for j in range(421):
            y=-110+j*.5;center=side*(2.20+.06*math.sin(y*.31)+.035*math.sin(y*.91))
            for k in range(7):
                u=(k-3)/3;vs.append((center+u*.28,y,max(-.025,.085*(1-u*u)*(.8+.2*math.sin(y*.8)))))
            if j:
                for k in range(6):q=j*7+k;fs.append((q-7,q-6,q+1,q))
        mesh('297 irregular earthen verge',vs,fs,earth)
    # A less mottled, warm-earth road with footprint-scale patching in its shader.
    road=bpy.data.objects['irregular packed farm track'];mat=surface('297 compressed dry earth',[(.095,.073,.038),(.27,.22,.135)],.7,bump=.004)
    n=mat.node_tree.nodes;l=mat.node_tree.links;tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=14;tex.inputs['Detail'].default_value=2
    coords=n.new('ShaderNodeTexCoord');l.new(coords.outputs['Object'],tex.inputs[0]);rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.75;rough.inputs['To Max'].default_value=.96;l.new(tex.outputs['Fac'],rough.inputs[0]);l.new(rough.outputs[0],n['Principled BSDF'].inputs['Roughness'])
    road.data.materials.clear();road.data.materials.append(mat)
    # Foliage edges: individual oriented leaf clusters replace smooth crown balls.
    leaves=[surface('297 foliage '+str(k),[(.012,.025,.011),(.08+k*.015,.12+k*.016,.035+k*.01)],8,bump=.001) for k in range(3)]
    buckets=[([],[]) for _ in leaves]
    for i,o in enumerate(list(bpy.data.objects)):
        if not o.name.startswith('broken broadleaf crown292'):continue
        center=o.matrix_world.translation;extent=Vector(o.dimensions)*.48;o.scale*=.67;vs,fs=buckets[i%3]
        for j in range(75):
            a=float(rng.uniform(0,math.tau));v=float(rng.uniform(-1,1));r=float(rng.uniform(.15,1))**(1/3)
            q=center+Vector((math.cos(a)*math.sqrt(1-v*v)*extent.x*r,math.sin(a)*math.sqrt(1-v*v)*extent.y*r,v*extent.z*r))
            w=float(rng.uniform(.06,.13));u=Vector((math.cos(a)*w,math.sin(a)*w,0));b=Vector((-.035*math.sin(a),.035*math.cos(a),.035));n=len(vs)
            vs.extend([q-u,q+b,q+u,q-b]);fs.extend([(n,n+1,n+2),(n,n+2,n+3)])
    for k,(vs,fs) in enumerate(buckets):mesh('297 broken leafy canopy '+str(k),vs,fs,leaves[k])
    bank=bpy.data.objects['low field bank for leader'];bankmat=surface('297 eroded earthen bank',[(.065,.045,.024),(.22,.165,.085)],1.3,bump=.012)
    bank.data.materials.clear();bank.data.materials.append(bankmat)
    for v in bank.data.vertices:
        if .10<v.co.z<3.0:
            weight=math.sin(v.co.z/3.19*math.pi);v.co.z+=weight*(.09*math.sin(v.co.x*3.1+v.co.y*.2)+.045*math.sin(v.co.y*4.3))
    bank.data.update();bpy.context.view_layer.update()
    scrub=bpy.data.objects['bank rooted scrub292']
    for i in range(0,len(scrub.data.vertices),4):
        base=(scrub.data.vertices[i].co+scrub.data.vertices[i+1].co)/2
        hit,p,normal,index=bank.ray_cast(Vector((base.x,base.y,10)),Vector((0,0,-1)))
        if not hit:raise ValueError('Scrub root outside changed bank')
        delta=p.z-base.z
        for j in range(4):scrub.data.vertices[i+j].co.z+=delta

def close_shoulders(ob,top):
    """Replace the open torso pipe with supported shoulder-to-neck cloth."""
    vs=[v.co.copy() for v in ob.data.vertices];fs=[tuple(p.vertices) for p in ob.data.polygons];cols=64
    for j in range(18,22):
        for k in range(cols):vs[j*cols+k].z-=.07*abs(math.cos(k*math.tau/cols))*(j-17)/4
    last=[p.copy() for p in vs[-cols:]]
    for j in range(1,6):
        u=j/5;n=len(vs)
        for k,p in enumerate(last):
            a=k*math.tau/cols;neck=Vector((.068*math.cos(a),.072*math.sin(a),top+.075))
            q=p.lerp(neck,u);q.z+=.012*math.sin(u*math.pi);vs.append(q)
        prev=n-cols
        for k in range(cols):fs.append((prev+k,prev+(k+1)%cols,n+(k+1)%cols,n+k))
    old=ob.data;new=bpy.data.meshes.new(ob.name+' continuous shoulders');new.from_pydata(vs,[],fs);new.update()
    for m in old.materials:new.materials.append(m)
    for p in new.polygons:p.use_smooth=True
    ob.data=new

def fabric_sashes(parent,waist,top,mat):
    for o in list(parent.children):
        if o.name.startswith(('commander cross sash','commander waist sash','secondary shoulder sash','secondary waist sash')):hide(o)
    vs=[];fs=[]
    for k in range(81):
        a=k*math.tau/80
        for j in range(7):
            u=j/6;z=waist+(u-.5)*.10;rx=.172+.009*math.sin(u*math.pi);ry=.141+.006*math.sin(u*math.pi)
            vs.append((rx*math.cos(a),ry*math.sin(a),z+.005*math.sin(a*3)))
        if k:
            for j in range(6):q=k*7+j;fs.append((q-7,q-6,q+1,q))
    ob=mesh('297 cloth waist sash',vs,fs,mat);ob.parent=parent
    # Surface-following diagonal band; thick round tube predecessor is hidden.
    vs=[];fs=[]
    for j in range(25):
        u=j/24;x=-.18+.31*u;z=top-.045-(top-.045-waist)*u
        for k in range(5):
            w=(k/4-.5)*.065;vs.append((x+w,-.151-.008*math.sin(u*math.pi),z+w*.65))
        if j:
            for k in range(4):q=j*5+k;fs.append((q-5,q-4,q+1,q))
    ob=mesh('297 woven diagonal sash',vs,fs,mat);ob.parent=parent

def baked_limb(parent,up,lo,oldradii,radii,mat,name):
    s=bpy.context.scene;hide(up);hide(lo);times=list(range(1,FRAMES+1,4))+[FRAMES];samples=[]
    for f in times:
        s.frame_set(f);a,b=endpoints(up,oldradii[0]);b2,c=endpoints(lo,oldradii[1]);samples.append(sleeve_points(a,(b+b2)/2,c,radii))
    ob=mesh(name,samples[0],sleeve_faces(),mat);ob.parent=parent;ob.shape_key_add(name='Basis')
    for i,(f,pts) in enumerate(zip(times,samples)):
        sk=ob.shape_key_add(name=f'pose{f:04d}')
        for p,q in zip(sk.data,pts):p.co=q
        # Actual adjacent times are required for final nonuniform interval.
        for ff,val in ((times[i-1] if i else 0,0),(f,1),(times[i+1] if i+1<len(times) else FRAMES+1,0)):
            sk.value=val;sk.keyframe_insert('value',frame=ff)
    action=ob.data.shape_keys.animation_data.action
    for fc in action.layers[0].strips[0].channelbags[0].fcurves:
        for p in fc.keyframe_points:p.interpolation='LINEAR'
    return ob

def sleeve_points(a,b,c,radii):
    # Straight limb sections with a localized rounded elbow, not one noodle arc.
    centers=[];rr=[]
    for j in range(13):
        u=j/12
        if u<.38:p=a.lerp(b,u/.5)
        elif u>.62:p=b.lerp(c,(u-.5)/.5)
        else:
            v=(u-.38)/.24;p=(a.lerp(b,.76))*(1-v)**2+b*(2*v*(1-v))+b.lerp(c,.24)*v*v
        centers.append(p);rr.append(float(np.interp(u,[0,.48,1],radii)))
    vs=[]
    for j,p in enumerate(centers):
        tangent=(centers[min(12,j+1)]-centers[max(0,j-1)]).normalized();ref=Vector((0,1,0))
        if abs(tangent.dot(ref))>.95:ref=Vector((1,0,0))
        n=tangent.cross(ref).normalized();b=tangent.cross(n).normalized()
        for k in range(24):
            ang=k*math.tau/24;fold=1+.035*math.sin(ang*7+j*.6)
            vs.append(p+(n*math.cos(ang)+b*math.sin(ang))*rr[j]*fold)
    return vs

def sleeve_faces():return [(j*24+k,j*24+(k+1)%24,(j+1)*24+(k+1)%24,(j+1)*24+k) for j in range(12) for k in range(24)]

def endpoints(ob,r):
    d=ob.rotation_quaternion@Vector((0,0,ob.scale.z-r*.25));return ob.location-d,ob.location+d

def supporting_cast():
    s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
    rng=np.random.default_rng(298)
    # All changes are restricted to existing secondary parents, never hero data.
    frames=[o for o in bpy.data.objects if o.name.startswith('secondary facial and crown frame292')]
    for frame in frames:
        blue=next(o for o in frame.children if o.name.startswith('secondary tied crown core')).data.materials[0]
        for o in list(frame.children):
            if o.name.startswith(('secondary tied crown core','secondary diagonal turban course')):hide(o)
        vs=[];fs=[]
        for j in range(25):
            z=.045+j*.245/24;r=band_radius(z)
            for k in range(64):
                a=k*math.tau/64;vs.append((r*math.sin(a),.008-r*1.08*math.cos(a),z))
            if j:
                for k in range(64):q=j*64+k;r0=j*64+(k+1)%64;fs.append((q-64,r0-64,r0,q))
        ob=mesh('297 tapered crown foundation',vs,fs,blue);ob.parent=frame
        for layer in range(6):
            vs=[];fs=[]
            for k in range(81):
                a=k*math.tau/80
                for j in range(5):
                    u=j/4;z=.049+layer*.033+.044*u+.022*math.sin(a+.35*layer)
                    rad=band_radius(z)+.003+.002*math.sin(u*math.pi)+.001*math.sin(a*9+layer)
                    vs.append((rad*math.sin(a),.008-rad*1.08*math.cos(a),z))
                if k:
                    for j in range(4):q=k*5+j;fs.append((q-5,q-4,q+1,q))
            ob=mesh('297 overlapping fabric crown turn',vs,fs,blue);ob.parent=frame
        # Fine clustered beard fibers over the existing broad mass, no uniform sheet.
        hair=next(o for o in frame.children if o.name.startswith('secondary beard clump')).data.materials[0]
        for i in range(65):
            a=float(rng.uniform(-1.3,1.3));x=.076*math.sin(a);y=-.063-.059*math.cos(a);length=float(rng.uniform(.105,.165))
            tube('297 beard grouped fibers',[(x,y,-.016),(x*.94,y-.009,-.07),(x*.78+float(rng.uniform(-.008,.008)),y-.008,-length)],.0015,hair,frame)
    # Continuous sleeves from inherited joint pivots; preserve all controller data.
    rider=bpy.data.objects['mounted leader'];blue=bpy.data.objects['commander fitted chola'].data.materials[0]
    for side,suffix in ((-1,''),(1,'.001')):
        up=bpy.data.objects['leader upper arm'+suffix];lo=bpy.data.objects['leader forearm'+suffix];hide(up);hide(lo)
        samples=[];times=list(range(1,FRAMES+1,4))+[FRAMES]
        for f in times:
            s.frame_set(f);a,b=endpoints(up,.06);b2,c=endpoints(lo,.045);samples.append(sleeve_points(a,(b+b2)/2,c,(.075,.062,.042)))
        ob=mesh('297 continuous leader sleeve',samples[0],sleeve_faces(),blue);ob.parent=rider;ob.shape_key_add(name='Basis')
        for f,pts in zip(times,samples):
            sk=ob.shape_key_add(name=f'pose{f:04d}')
            for p,q in zip(sk.data,pts):p.co=q
            for ff,val in ((max(1,f-4),0),(f,1),(min(FRAMES+4,f+4),0)):sk.value=val;sk.keyframe_insert('value',frame=ff)
        # Key1 must be zero before another pose; one active interpolation pair.
        if ob.data.shape_keys.animation_data:
            for fc in ob.data.shape_keys.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
                for p in fc.keyframe_points:p.interpolation='LINEAR'
    s.frame_set(1)
    # Boots and shaped trousers replace disjoint floating ovals on the leader.
    leather=surface('297 worn rider boots',[(.02,.014,.009),(.085,.056,.027)],20,bump=.002)
    for side,suffix in ((-1,''),(1,'.001')):
        up=bpy.data.objects['leader thigh'+suffix];lo=bpy.data.objects['leader shin'+suffix];a,b=endpoints(up,.095);b2,c=endpoints(lo,.07);hide(up);hide(lo)
        ob=mesh('297 continuous leader trousers',sleeve_points(a,(b+b2)/2,c,(.115,.086,.056)),sleeve_faces(),blue);ob.parent=rider
        attach=sphere('297 mounted boot',c+Vector((0,-.035,-.018)),(.068,.13,.065),leather);attach.parent=rider
        tube('297 boot cuff',[(c.x+.063*math.cos(t),c.y+.06*math.sin(t),c.z+.12) for t in np.linspace(0,math.tau,33)],.012,leather,rider)
    # Robe placket/hem and wide sash have fabric surfaces, not golden pipes.
    for parent in [rider]+[o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')]:
        leader=parent==rider;top=.5 if leader else 1.4;waist=.06 if leader else .88;bottom=-.18 if leader else .36
        mat=blue if leader else next(o for o in parent.children if o.name.startswith('secondary chola')).data.materials[0]
        robe=next(o for o in parent.children if o.name.startswith('commander fitted chola' if leader else 'secondary chola'))
        close_shoulders(robe,top)
        trim=surface('297 faded edge binding',[(.10,.065,.024),(.28,.19,.065)],17,bump=.001)
        fabric_sashes(parent,waist,top,trim)
        # Front opening traces a supported garment, not additional loose strips.
        tube('297 chola front seam',[(.013,-.137,top),(.02,-.15,(waist+top)/2),(.022,-.14,waist)],.003,trim,parent)
        tube('297 lower hem binding',[(.275*math.cos(t),.18*math.sin(t),bottom+.009*math.sin(t*5)) for t in np.linspace(0,math.tau,81)],.004,trim,parent)
        if not leader:
            for ob in list(parent.children):
                if ob.name.startswith('PROXY arm'):
                    a,b=endpoints(ob,.064);hide(ob);c=a.lerp(b,.52)+Vector((0,.035,0));new=mesh('297 crowd sleeve',sleeve_points(a,c,b,(.075,.064,.045)),sleeve_faces(),mat);new.parent=parent
            uppers=sorted([o for o in parent.children if o.name.startswith('PROXY thigh')],key=lambda o:o.name)
            lowers=sorted([o for o in parent.children if o.name.startswith('PROXY calf')],key=lambda o:o.name)
            for up,lo in zip(uppers,lowers):baked_limb(parent,up,lo,(.074,.057),(.087,.072,.049),mat,'297 continuous crowd trousers')
    # More coherent horse coat with directional fiber-scale shading.
    body=bpy.data.objects['horse'];coat=surface('297 silver dapple coat',[(.075,.09,.10),(.25,.28,.28)],4.5,rough=.64,bump=.0006)
    body.data.materials.clear();body.data.materials.append(coat)
    b=coat.node_tree.nodes['Principled BSDF'];b.inputs['Sheen Weight'].default_value=.22;b.inputs['Sheen Roughness'].default_value=.65
    # Existing groom stays on existing bones; variation is local geometry, not detachment.
    for o in bpy.data.objects:
        if o.name.startswith(('rooted mane locks292','horse tail fullness292','horse forelock292')):
            o.data.bevel_depth*=.65
            for sp in o.data.splines:
                for i,p in enumerate(sp.points):
                    if i:p.co.x+=float(rng.uniform(-.007,.007))*i/max(1,len(sp.points)-1)

def build():
    fields();supporting_cast();torchlight();bpy.context.scene.frame_set(1)
