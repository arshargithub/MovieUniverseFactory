"""Coherent cultivated landscape; all assets authored locally, fixed seed."""
import math
import bpy
import numpy as np
from mathutils import Vector
from sikh257_native import mesh,material
from sikh292_assets import surface
from movie_factory.sikh304_motion import ground_height,ease

def remove(prefixes):
    for o in list(bpy.data.objects):
        if o.name.startswith(prefixes):bpy.data.objects.remove(o,do_unlink=True)

def bank_height(x,y):
    dx=x-7.5;dy=y+29;r=math.hypot(dx/(5.7 if dx<0 else 8.0),dy/10.4)
    ang=math.atan2(dy,dx);r/=1+.10*math.sin(3*ang+.6)+.045*math.sin(7*ang)
    u=max(0,min(1,(r-.32)/.68))
    return max(ground_height(x,y),3.19*(1-ease(u))+.045*math.sin(dx*2.2+dy*.6)*math.sin(dy*.9)*math.sin(u*math.pi))

def terrain():
    remove(('grounded road aggregate','bank rooted scrub292'))
    road=bpy.data.objects['irregular packed farm track']
    soil=surface('304 compacted silty farm soil',[(.16,.135,.085),(.255,.217,.145)],4.5,rough=.97,bump=.0014)
    n=soil.node_tree.nodes;l=soil.node_tree.links;b=n['Principled BSDF'];base=b.inputs['Base Color'].links[0].from_socket
    tex=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Object'],sep.inputs[0])
    absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE';l.new(sep.outputs['X'],absolute.inputs[0])
    edge=n.new('ShaderNodeMapRange');edge.inputs['From Min'].default_value=1.75;edge.inputs['From Max'].default_value=3.65;l.new(absolute.outputs[0],edge.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.54,.58,.38,1);l.new(edge.outputs[0],mix.inputs[0]);l.new(base,mix.inputs[1]);l.new(mix.outputs[0],b.inputs['Base Color'])
    road.data.materials.clear();road.data.materials.append(soil)
    bank=bpy.data.objects['low field bank for leader'];vs=[];fs=[];N=101
    for j in range(N):
        for i in range(N):
            x=7.5-9+i*.18;y=-29-12+j*.24;vs.append((x,y,bank_height(x,y)-.003))
    for j in range(N-1):
        for i in range(N-1):
            q=j*N+i
            if max(vs[k][2] for k in (q,q+1,q+N,q+N+1))>.08:fs.append((q,q+1,q+N+1,q+N))
    data=bpy.data.meshes.new('304 eroded bank without rectangular apron');data.from_pydata(vs,[],fs);data.update();bank.data=data
    bankmat=surface('304 earthy bank',[(.13,.12,.066),(.255,.224,.13)],3.7,rough=.96,bump=.002)
    data.materials.append(bankmat)
    for p in data.polygons:p.use_smooth=True
    return soil

def instancer(name,points,scales,proto,wind=False):
    data=bpy.data.meshes.new(name);data.from_pydata(points,[],[]);data.update();ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob)
    a=data.attributes.new('scale','FLOAT_VECTOR','POINT');a.data.foreach_set('vector',np.asarray(scales,dtype=np.float32).ravel())
    g=bpy.data.node_groups.new(name+' rooted instances','GeometryNodeTree');g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    n=g.nodes;l=g.links;inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');info=n.new('GeometryNodeObjectInfo');info.inputs['Object'].default_value=proto;info.transform_space='ORIGINAL'
    instances=n.new('GeometryNodeInstanceOnPoints');l.new(inp.outputs['Geometry'],instances.inputs['Points']);l.new(info.outputs['Geometry'],instances.inputs['Instance'])
    attr=n.new('GeometryNodeInputNamedAttribute');attr.data_type='FLOAT_VECTOR';attr.inputs['Name'].default_value='scale';l.new(attr.outputs['Attribute'],instances.inputs['Scale'])
    if wind:
        pos=n.new('GeometryNodeInputPosition');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.23,.13,0);l.new(pos.outputs[0],dot.inputs[0])
        time=n.new('ShaderNodeValue');time.name='travelling breeze time'
        for f in (1,529):time.outputs[0].default_value=(f-1)/24*1.8;time.outputs[0].keyframe_insert('default_value',frame=f)
        add=n.new('ShaderNodeMath');add.operation='ADD';l.new(dot.outputs['Value'],add.inputs[0]);l.new(time.outputs[0],add.inputs[1])
        sine=n.new('ShaderNodeMath');sine.operation='SINE';l.new(add.outputs[0],sine.inputs[0]);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY_ADD';mul.inputs[1].default_value=.075;mul.inputs[2].default_value=.065;l.new(sine.outputs[0],mul.inputs[0])
        rot=n.new('ShaderNodeCombineXYZ');l.new(mul.outputs[0],rot.inputs['X']);l.new(instances.outputs[0],out.inputs['Geometry']);l.new(rot.outputs[0],instances.inputs['Rotation'])
    else:l.new(instances.outputs[0],out.inputs['Geometry'])
    mod=ob.modifiers.new('rooted instances','NODES');mod.node_group=g
    return ob

def fields(soil):
    rng=np.random.default_rng(304);protos=[bpy.data.objects['300 reusable wheat tiller clump '+str(k)] for k in range(4)]
    remove(('300 dense rooted wheat','300 dense instanced wheat','300 crop rooted','300 wheat instances','300 rooted wheat heads'))
    # Identify only the four superseded GN scatter owners, never templates.
    for o in list(bpy.data.objects):
        if any(m.type=='NODES' and m.node_group and any(n.type=='OBJECT_INFO' and n.inputs.get('Object') and n.inputs['Object'].default_value in protos for n in m.node_group.nodes) for m in o.modifiers):bpy.data.objects.remove(o,do_unlink=True)
    for k,proto in enumerate(protos):
        # Existing cereal leaves and ears are useful; density/extent/response was not.
        mat=surface('304 ripening wheat '+str(k),[(.055+k*.006,.078+k*.007,.025),(.19+k*.02,.225+k*.018,.075)],7,rough=.9,bump=.0003)
        proto.data.materials.clear();proto.data.materials.append(mat)
    buckets=[([],[]) for _ in range(4)]
    # Occupied parcels continue well past the camera horizon. Narrow access
    # bunds and irrigation strips divide them, not uniform bare field planes.
    for side in (-1,1):
        ys=[-145,-111,-78,-46,-12,22,54,91,130]
        xs=[3.8,19.5,39,65,103]
        for iy,(ya,yb) in enumerate(zip(ys,ys[1:])):
            for ix,(xa,xb) in enumerate(zip(xs,xs[1:])):
                matidx=(iy+ix+(side==1))%4;density=7 if xa<20 else 1.8
                count=int((xb-xa)*(yb-ya)*density)
                for _ in range(count):
                    x=side*float(rng.uniform(xa+.80,xb-.80));y=float(rng.uniform(ya+.85,yb-.85));z=ground_height(x,y)
                    if x>0 and bank_height(x,y)>.12:continue
                    # Modest aligned rows, not evenly spaced isolated plants.
                    x=side*(round(abs(x)/.22)*.22+float(rng.uniform(-.055,.055)))
                    h=float(rng.uniform(.83,1.17))*(.94+.08*math.sin(iy*1.7+ix));w=1.25 if xa<20 else 2.1
                    buckets[matidx][0].append((x,y,z));buckets[matidx][1].append((w,w,h))
                # Walkable strip, mildly raised, with same earth not a dark overlay.
                vs=[];fs=[]
                for j in range(25):
                    x=side*(xa+(xb-xa)*j/24);y=ya+.12*math.sin(x*.17+iy)
                    for dy in (-.65,0,.65):vs.append((x,y+dy,ground_height(x,y+dy)+(.055 if dy==0 else .002)))
                    if j:
                        q=j*3;fs.extend([(q-3,q,q+1,q-2),(q-2,q+1,q+2,q-1)])
                ob=mesh('304 worn cross-field bund',vs,fs,soil)
                for p in ob.data.polygons:p.use_smooth=True
    for k,(pts,sc) in enumerate(buckets):instancer('304 cultivated parcel canopy '+str(k),pts,sc,protos[k],True)

def grass_and_ditch(soil):
    rng=np.random.default_rng(305);grass=surface('304 ditch grasses and bank cover',[(.035,.055,.018),(.13,.18,.057)],5,bump=.0003)
    vs=[];fs=[]
    def tuft(x,y,z,h):
        for k in range(11):
            a=float(rng.uniform(0,math.tau));d=Vector((math.cos(a),math.sin(a),0));w=Vector((-d.y,d.x,0))*float(rng.uniform(.002,.005));p=Vector((x,y,z));q=len(vs)
            hh=h*float(rng.uniform(.6,1.2))
            for j in range(6):
                u=j/5;center=p+d*hh*.65*u*u+Vector((0,0,hh*(u-.22*u*u)));width=w*math.sin((u*.97+.03)*math.pi)
                vs.extend([center-width,center+width])
                if j:fs.append((q+j*2-2,q+j*2-1,q+j*2+1,q+j*2))
    for i in range(12500):
        side=(-1,1)[i%2];y=float(rng.uniform(-140,130));x=side*float(rng.uniform(2.25,3.85));z=ground_height(x,y)
        if math.sin(y*.8+x*3)<-.55:continue
        tuft(x,y,z,float(rng.uniform(.06,.22)))
    for i in range(6000):
        x=float(rng.uniform(.8,15));y=float(rng.uniform(-40,-18));z=bank_height(x,y)
        if .1<z<3.12 and math.sin(x*1.7+y*.4)>-.45:tuft(x,y,z,float(rng.uniform(.08,.25)))
    ob=mesh('304 rooted ditch and bank vegetation',vs,fs,grass)
    damp=surface('304 moist ditch sediment',[(.04,.038,.023),(.085,.08,.045)],9,rough=.76,bump=.0008)
    for side in (-1,1):
        vs=[];fs=[]
        for j in range(541):
            y=-140+j*.5;edge=2.05+.09*math.sin(y*.14)+.035*math.sin(y*.61)
            width=.07+.035*math.sin(y*.3)
            for d in (-width,width):
                x=side*(edge+.63+d);vs.append((x,y,ground_height(x,y)+.001))
            if j and math.sin(y*.15)>-.35:q=j*2;fs.append((q-2,q-1,q+1,q))
        mesh('304 intermittent silt in ditch bed',vs,fs,damp)

def trees():
    remove(('tree trunk','tree branch','irregular broadleaf mass','branching tree trunk292','broken broadleaf crown292','297 broken leafy canopy'))
    rng=np.random.default_rng(306);bark=surface('304 fissured tree bark',[(.055,.047,.031),(.15,.13,.078)],9,bump=.009)
    leaves=[surface('304 foliage light plane '+str(k),[(.018+k*.007,.04+k*.01,.019),(.08+k*.018,.14+k*.021,.048+k*.009)],4,rough=.85,bump=.0002) for k in range(3)]
    # Branch and twig structure with discrete curved leaves, no solid canopy blobs.
    from sikh257_layout import tube
    for kind in range(3):
        trunkv=[];trunkf=[];lv=[];lf=[]
        def branch(a,b,ra,rb):
            a=Vector(a);b=Vector(b);d=(b-a).normalized();u=d.cross(Vector((1,0,0)))
            if u.length<.1:u=d.cross(Vector((0,1,0)))
            u.normalize();v=d.cross(u);q=len(trunkv)
            for p,r in ((a,ra),(a.lerp(b,.55)+Vector((.03,0,0)),(ra+rb)*.55),(b,rb)):
                for k in range(7):trunkv.append(p+(u*math.cos(k*math.tau/7)+v*math.sin(k*math.tau/7))*r)
            for row in range(2):
                for k in range(7):i=q+row*7+k;j=q+row*7+(k+1)%7;trunkf.append((i,j,j+7,i+7))
        branch((0,0,0),(.12,0,3.2),.16,.035)
        for j in range(17):
            ang=j*2.4+kind;z=1.35+j*.105;spread=float(rng.uniform(1.0,1.85));tip=Vector((math.cos(ang)*spread,math.sin(ang)*spread,z+float(rng.uniform(.6,1.6))))
            start=Vector((.04,0,z));branch(start,tip,.045,.008)
            for k in range(13):
                base=start.lerp(tip,.3+k*.05);az=ang+float(rng.uniform(-1.4,1.4));end=base+Vector((math.cos(az)*.6,math.sin(az)*.6,float(rng.uniform(.1,.6))));branch(base,end,.01,.002)
                for m in range(22):
                    p=base.lerp(end,float(rng.uniform(.15,1.25)))+Vector(tuple(rng.normal(0,.15,3)));a=float(rng.uniform(0,math.tau));length=float(rng.uniform(.10,.21));d=Vector((math.cos(a)*length,math.sin(a)*length,float(rng.uniform(-.04,.09))));w=Vector((-math.sin(a),math.cos(a),0))*length*.43;q=len(lv)
                    lv.extend([p-d,p-w+Vector((0,0,.018)),p+d,p+w,p+Vector((0,0,.035))]);lf.extend([(q,q+1,q+4),(q+1,q+2,q+4),(q+2,q+3,q+4),(q+3,q,q+4)])
        wood=mesh('304 tree branching prototype '+str(kind),trunkv,trunkf,bark);leaf=mesh('304 tree leaves prototype '+str(kind),lv,lf,leaves[kind]);wood.hide_render=leaf.hide_render=True;wood.hide_viewport=leaf.hide_viewport=True
        points=[];scales=[]
        for i in range(15):
            side=(-1,1)[i%2];x=side*(18.7 if i<6 else float(rng.uniform(38,80)));y=-128+i*17+kind*5
            if 0<x<32 and -50<y<-10:continue
            points.append((x,y,ground_height(x,y)));h=float(rng.uniform(1.1,1.75));scales.append((h*(.75+kind*.12),h,h))
        instancer('304 boundary tree branches '+str(kind),points,scales,wood)
        instancer('304 boundary tree foliage '+str(kind),points,scales,leaf)

def build():
    soil=terrain();fields(soil);grass_and_ditch(soil);trees()
