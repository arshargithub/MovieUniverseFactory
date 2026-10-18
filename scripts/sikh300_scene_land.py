"""Ground/crop/material construction for300, deterministic authored surfaces."""
import math
import bpy
import numpy as np
from mathutils import Vector
from sikh257_native import mesh
from sikh292_assets import surface
from movie_factory.sikh300_motion import ground_height

def landscape():
    # Remove only superseded inherited surfaces/crop, not trees, bank or props.
    prefixes=('individual wheat blades292','297 coherent cereal ears','297 irregular earthen verge','earth field margin','small field','field bund','thin crop leaves','lane gravel292')
    for o in list(bpy.data.objects):
        if o.name.startswith(prefixes) or o.name=='cultivated plain292':bpy.data.objects.remove(o,do_unlink=True)
    road=bpy.data.objects['irregular packed farm track'];old=road.data
    xs=sorted(set(list(np.linspace(-4.4,4.4,89))+[-110,-60,-30,-15,-8,8,15,30,60,110]));vs=[];fs=[]
    for j in range(591):
        y=-150+j*.5
        for x in xs:vs.append((x,y,ground_height(x,y)))
        if j:
            for k in range(len(xs)-1):q=j*len(xs)+k;fs.append((q-len(xs),q,q+1,q+1-len(xs)))
    data=bpy.data.meshes.new('300 continuous road swale field');data.from_pydata(vs,[],fs);data.update();road.data=data
    soil=surface('300 compacted earth and cultivated shoulders',[(.055,.044,.027),(.22,.18,.105)],.8,bump=.002)
    n=soil.node_tree.nodes;l=soil.node_tree.links;b=n['Principled BSDF'];base=b.inputs['Base Color'].links[0].from_socket
    tex=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Object'],sep.inputs[0])
    absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE';l.new(sep.outputs['X'],absolute.inputs[0])
    ramp=n.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=1.65;ramp.inputs['From Max'].default_value=3.7;l.new(absolute.outputs[0],ramp.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.48,.49,.37,1);l.new(ramp.outputs[0],mix.inputs[0]);l.new(base,mix.inputs[1]);l.new(mix.outputs[0],b.inputs['Base Color'])
    road.data.materials.append(soil)
    for p in data.polygons:p.use_smooth=True
    # Existing pebble meshes must sit on the same road, not the former plane.
    for o in bpy.data.objects:
        if o.name.startswith('grounded road aggregate') and o.type=='MESH' and not o.parent:
            for v in o.data.vertices:v.co.z+=ground_height(v.co.x,v.co.y)
    crops()

def crops():
    rng=np.random.default_rng(300);buckets=[([],[]) for _ in range(4)]
    mats=[surface('300 wheat ochre green '+str(k),[(.065+k*.008,.075+k*.007,.025),(.22+k*.035,.20+k*.028,.075+k*.014)],3,rough=.86,bump=.0004) for k in range(4)]
    for i in range(52000):
        side=-1 if i%2 else 1;row=int(rng.integers(0,105));x=side*(3.72+row*.23+float(rng.uniform(-.08,.08)));y=float(rng.uniform(-120,110))
        if ((x-7.5)/8.2)**2+((y+29)/9.4)**2<1:continue
        # Small irregular gaps and row-level height make crop masses, not a lawn.
        if math.sin(y*.31+row*.42)>.93:continue
        h=float(rng.uniform(.60,.86))+.045*math.sin(y*.2);z=ground_height(x,y);lean=float(rng.uniform(-.045,.085));ang=float(rng.uniform(0,math.tau));vs,fs=buckets[i%4]
        def quad(points):
            q=len(vs);vs.extend(points);fs.append(tuple(range(q,q+len(points))))
        # Three-sided culm with tapered top, both leaves connect to stem nodes.
        q=len(vs)
        for u in (0,.45,1):
            for k in range(3):a=ang+k*math.tau/3;vs.append((x+lean*u*u+.0028*math.cos(a),y+.0028*math.sin(a),z+h*u))
        for j in range(2):
            for k in range(3):a=q+j*3+k;b=q+j*3+(k+1)%3;fs.append((a,b,b+3,a+3))
        for j in (0,1):
            a=ang+j*2.7;u=.32+j*.28;p=Vector((x+lean*u*u,y,z+h*u));d=Vector((math.cos(a),math.sin(a),0));w=Vector((-d.y,d.x,0))*.014
            quad([p,p+d*.10+w+Vector((0,0,.09)),p+d*.23+Vector((0,0,.04)),p+d*.10-w+Vector((0,0,.09))])
        # Distinct tapering grain ear, alternating paired kernels and fine awns.
        center=Vector((x+lean,y,z+h));d=Vector((math.cos(ang),math.sin(ang),0));cross=Vector((-d.y,d.x,0))
        for j in range(7):
            level=center+Vector((0,0,j*.014));width=.012*math.sin((j+1)/8*math.pi)
            for side2 in (-1,1):
                p=level+d*(side2*width*.65);q=len(vs);vs.extend([p-cross*.004,p+d*side2*width+Vector((0,0,.008)),p+cross*.004,p+Vector((0,0,.020))]);fs.extend([(q,q+1,q+3),(q+1,q+2,q+3),(q+2,q,q+3)])
                tip=p+d*side2*.023+Vector((0,0,.05));quad([p-cross*.0006,p+cross*.0006,tip])
    for k,(vs,fs) in enumerate(buckets):
        ob=mesh('300 rooted wheat heads and leaves '+str(k),vs,fs,mats[k]);ob['root_surface']='irregular packed farm track'
        ob.shape_key_add(name='Basis');wind=ob.shape_key_add(name='coherent quiet breeze')
        # Bulk RNA update: per-coordinate assignment tags the entire key/scene
        # for every vertex and makes construction quadratic in practice.
        coords=np.asarray(vs,dtype=np.float32)
        heights=np.maximum(0,coords[:,2]-np.fromiter((ground_height(float(x),float(y)) for x,y in coords[:,:2]),dtype=np.float32,count=len(coords)))
        coords[:,0]+=.025*heights*heights;coords[:,1]+=.012*heights*heights
        wind.data.foreach_set('co',coords.ravel())
        for f in range(1,529,8):wind.value=.35+.25*math.sin(f/24*.85+k*.5);wind.keyframe_insert('value',frame=f)

def bike_materials():
    root=bpy.data.objects['BIKE travel owner'];seen={}
    def descendants(o):
        for c in o.children:
            if c.name.startswith(('RIDER','PROXY')):continue
            yield c;yield from descendants(c)
    for o in descendants(root):
        if o.type!='MESH' or o.name.startswith('PROXY'):continue
        for slot in o.material_slots:
            mat=slot.material
            if not mat:continue
            if mat.name in seen:slot.material=seen[mat.name];continue
            if not mat.use_nodes:continue
            b=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if not b:continue
            source=mat.name;mat=mat.copy();mat.name='300 bike lived material '+mat.name;slot.material=mat;seen[source]=mat;n=mat.node_tree.nodes;l=mat.node_tree.links
            b=next(n for n in n if n.type=='BSDF_PRINCIPLED');tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=65;noise.inputs['Detail'].default_value=2;l.new(tc.outputs['Object'],noise.inputs[0])
            previous_normal=b.inputs['Normal'].links[0].from_socket if b.inputs['Normal'].links else None
            bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.0006;l.new(noise.outputs['Fac'],bump.inputs['Height'])
            if previous_normal:l.new(previous_normal,bump.inputs['Normal'])
            l.new(bump.outputs[0],b.inputs['Normal'])
            rough=n.new('ShaderNodeMapRange');base=float(b.inputs['Roughness'].default_value);rough.inputs['To Min'].default_value=max(.22,base*.8);rough.inputs['To Max'].default_value=min(.98,base+.17);l.new(noise.outputs['Fac'],rough.inputs[0]);l.new(rough.outputs[0],b.inputs['Roughness'])
            original=b.inputs['Base Color'].links[0].from_socket if b.inputs['Base Color'].links else None;color=tuple(b.inputs['Base Color'].default_value)
            dirt=n.new('ShaderNodeTexNoise');dirt.inputs['Scale'].default_value=6;l.new(tc.outputs['Object'],dirt.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.66,.61,.52,1);l.new(dirt.outputs['Fac'],mix.inputs[0]);mix.inputs[1].default_value=color
            if original:l.new(original,mix.inputs[1])
            l.new(mix.outputs[0],b.inputs['Base Color'])

def dense_crops():
    """Screen-density first: reusable tiller clumps, not isolated costly ears."""
    for ob in list(bpy.data.objects):
        if ob.name.startswith('300 rooted wheat'):bpy.data.objects.remove(ob,do_unlink=True)
    rng=np.random.default_rng(30007)
    for k in range(4):
        mat=surface('300 cereal canopy '+str(k),[(.052+k*.005,.063+k*.004,.019),(.18+k*.025,.176+k*.022,.055+k*.008)],4,rough=.88,bump=.0003)
        vs=[];fs=[]
        def face(points):
            start=len(vs);vs.extend(points);fs.append(tuple(range(start,start+len(points))))
        for j in range(7):
            angle=float(rng.uniform(0,math.tau));x=float(rng.uniform(-.12,.12));y=float(rng.uniform(-.12,.12));h=float(rng.uniform(.62,.91));lean=float(rng.uniform(-.04,.06));d=Vector((math.cos(angle),math.sin(angle),0));w=Vector((-d.y,d.x,0))
            p=Vector((x,y,0));top=p+Vector((lean,0,h))
            face([p-w*.0022,p+w*.0022,top+w*.0015,top-w*.0015])
            for m in range(3):
                base=p+Vector((lean*(.2+m*.2),0,h*(.2+m*.2)));direction=d*((-1)**m);width=w*.014
                face([base,base+direction*.095+width+Vector((0,0,.09)),base+direction*.20+width*.45+Vector((0,0,.07)),base+direction*.29+Vector((0,0,-.015)),base+direction*.20-width*.45+Vector((0,0,.07)),base+direction*.095-width+Vector((0,0,.09))])
            # Grained ear silhouette survives at shot size; no giant corn leaves.
            for m in range(5):
                center=top+Vector((0,0,m*.018));r=.012*math.sin((m+1)/6*math.pi)
                face([center-w*r,center+d*.007+Vector((0,0,.013)),center+w*r,center-d*.007+Vector((0,0,.013))])
            face([top-w*.0006,top+w*.0006,top+Vector((0,0,.14))])
        proto=mesh('300 reusable wheat tiller clump '+str(k),vs,fs,mat);proto.hide_render=True;proto.hide_viewport=True
        pts=[];scales=[]
        for i in range(16250):
            near=i<10000;side=-1 if i%2 else 1
            row=int(rng.integers(0,23 if near else 90));x=side*((3.77 if near else 9.05)+row*.23+float(rng.uniform(-.08,.08)));y=float(rng.uniform(-120,110))
            if ((x-7.5)/8.2)**2+((y+29)/9.4)**2<1:continue
            if math.sin(y*.19+row*.35)>.985 and float(rng.random())>.30:continue
            pts.append((x,y,ground_height(x,y)));scale=float(rng.uniform(.87,1.12));scales.append((scale*(1 if near else 1.65),scale*(1 if near else 1.65),scale))
        data=bpy.data.meshes.new('300 cereal clump points');data.from_pydata(pts,[],[]);data.update();ob=bpy.data.objects.new('300 dense instanced wheat '+str(k),data);bpy.context.scene.collection.objects.link(ob)
        attr=data.attributes.new('clump scale','FLOAT_VECTOR','POINT');attr.data.foreach_set('vector',np.asarray(scales,dtype=np.float32).ravel())
        group=bpy.data.node_groups.new('300 rooted cereal instances '+str(k),'GeometryNodeTree');group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=group.nodes;l=group.links
        inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');info=n.new('GeometryNodeObjectInfo');info.inputs['Object'].default_value=proto;info.transform_space='ORIGINAL'
        inst=n.new('GeometryNodeInstanceOnPoints');l.new(inp.outputs['Geometry'],inst.inputs['Points']);l.new(info.outputs['Geometry'],inst.inputs['Instance'])
        scale=n.new('GeometryNodeInputNamedAttribute');scale.data_type='FLOAT_VECTOR';scale.inputs['Name'].default_value='clump scale';l.new(scale.outputs['Attribute'],inst.inputs['Scale'])
        rotation=n.new('ShaderNodeCombineXYZ');l.new(rotation.outputs[0],inst.inputs['Rotation'])
        for f in range(1,529,6):rotation.inputs['X'].default_value=.008*math.sin(f/24*.9+k*.45);rotation.inputs['X'].keyframe_insert('default_value',frame=f)
        l.new(inst.outputs['Instances'],out.inputs['Geometry']);modifier=ob.modifiers.new('300 true cereal instancing','NODES');modifier.node_group=group
