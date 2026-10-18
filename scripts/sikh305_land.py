"""Inhabited farm corridor: erosion hierarchy and advected irregular gusts."""
import math
import bpy
import numpy as np
from mathutils import Vector
from sikh257_native import mesh
from sikh292_assets import surface
from movie_factory.sikh305_motion import ground_height,FRAMES
from sikh304_land import bank_height as old_bank

def road_height(x,y):
    h=ground_height(x,y);a=abs(x)
    # Preserve bike/contact lane; shape the verge and drainage independently.
    w=max(0,min(1,(a-1.55)/.5))
    center=2.72+.12*math.sin(y*.18)+.06*math.sin(y*.63+.8)
    erosion=-.14*math.exp(-((a-center)/.33)**2)
    edge=.025*math.sin(y*2.7+x*3.2)+.018*math.sin(y*6.1+x*9)
    return h+w*(erosion+edge*math.exp(-((a-2.85)/1.0)**2))

def bank_height(x,y):
    dx=x-7.5;dy=y+29;theta=math.atan2(dy,dx)
    r=math.hypot(dx/(5.7 if dx<0 else 9.4),dy/12.5)
    r/=1+.16*math.sin(3*theta+.6)+.07*math.sin(5*theta-1.2)
    core=math.hypot(dx/2.6,dy/3.6)
    u=max(0,min(1,(r-.24)/.76));base=3.19*(1-u*u*(3-2*u))
    # Protected hoof/spear core, irregular exposed strata and rain-cut runnels.
    mask=min(1,max(0,(core-.72)/.65))*math.sin(math.pi*u)
    relief=(.13*math.sin(dx*1.9+dy*.63)+.065*math.sin(dy*3.8-dx*.9)
            -.12*abs(math.sin(theta*9+.4*dy))**8)*mask
    return max(road_height(x,y),base+relief)

def material_soil():
    mat=surface('305 compacted clay and silty road',[(.15,.125,.084),(.29,.247,.168)],1.3,rough=.94,bump=.001)
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF'];src=b.inputs['Base Color'].links[0].from_socket
    coord=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Object'],sep.inputs[0])
    ax=n.new('ShaderNodeMath');ax.operation='ABSOLUTE';l.new(sep.outputs['X'],ax.inputs[0])
    minus=n.new('ShaderNodeMath');minus.operation='SUBTRACT';minus.inputs[1].default_value=.70;l.new(ax.outputs[0],minus.inputs[0])
    absrut=n.new('ShaderNodeMath');absrut.operation='ABSOLUTE';l.new(minus.outputs[0],absrut.inputs[0])
    ramp=n.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=.05;ramp.inputs['From Max'].default_value=.38;ramp.inputs['To Min'].default_value=.35;ramp.inputs['To Max'].default_value=0;l.new(absrut.outputs[0],ramp.inputs[0])
    wear=n.new('ShaderNodeMixRGB');wear.blend_type='MULTIPLY';wear.inputs[2].default_value=(.76,.73,.66,1);l.new(ramp.outputs[0],wear.inputs[0]);l.new(src,wear.inputs[1])
    peb=n.new('ShaderNodeTexVoronoi');peb.inputs['Scale'].default_value=135;l.new(coord.outputs['Object'],peb.inputs[0])
    fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=235;fine.inputs['Detail'].default_value=2;l.new(coord.outputs['Object'],fine.inputs[0])
    grains=n.new('ShaderNodeValToRGB');grains.color_ramp.elements[0].position=.12;grains.color_ramp.elements[0].color=(.22,.18,.12,1);grains.color_ramp.elements[1].position=.50;grains.color_ramp.elements[1].color=(1,.95,.83,1);l.new(peb.outputs['Distance'],grains.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.42;l.new(wear.outputs[0],mix.inputs[1]);l.new(grains.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],b.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.4;bump.inputs['Distance'].default_value=.002;l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],b.inputs['Normal'])
    rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.78;rough.inputs['To Max'].default_value=.98;l.new(fine.outputs['Fac'],rough.inputs[0]);l.new(rough.outputs[0],b.inputs['Roughness'])
    return mat

def terrain():
    road=bpy.data.objects['irregular packed farm track'];vs=[];fs=[];xs=sorted(set([-110,-60,-30,-20,-15,-8]+[-4.86+i*.09 for i in range(109)]+[5+i*.15 for i in range(121)]+[30,60,110]));nx=len(xs)
    ys=sorted(set([-260+j*.5 for j in range(801)]+[-46+j*.25 for j in range(137)]))
    for j,y in enumerate(ys):
        for x in xs:vs.append((x,y,max(road_height(x,y),bank_height(x,y)) if 1.6<x<24 and -46<y<-12 else road_height(x,y)))
        if j:
            for i in range(nx-1):q=j*nx+i;fs.append((q-nx,q+1-nx,q+1,q))
    data=bpy.data.meshes.new('305 continuous farm crown verge drainage');data.from_pydata(vs,[],fs);data.materials.append(material_soil());data.update();road.data=data
    for p in data.polygons:p.use_smooth=True
    # A single continuous surface removes the cut-out floating skirt of a
    # second mound mesh. No hidden seam or overlapping z-fighting skirt.
    bank=bpy.data.objects['low field bank for leader'];bank.hide_render=True;bank.hide_viewport=True
    mat=surface('305 weathered loam bank',[(.10,.09,.054),(.25,.213,.135)],2.3,rough=.96,bump=.007);data.materials.append(mat)
    for p in data.polygons:
        q=data.vertices[p.vertices[0]].co
        if q.z>road_height(q.x,q.y)+.06:p.material_index=1
    # Move pre-existing rooted cover with its actual supporting surface.
    ob=bpy.data.objects.get('304 rooted ditch and bank vegetation')
    if ob:
        for v in ob.data.vertices:
            x,y,z=v.co
            delta=(bank_height(x,y)-old_bank(x,y)) if x>0 and old_bank(x,y)>.10 else road_height(x,y)-ground_height(x,y)
            v.co.z+=delta
    for ob in bpy.data.objects:
        if ob.name.startswith('304 intermittent silt'):
            for v in ob.data.vertices:v.co.z+=road_height(v.co.x,v.co.y)-ground_height(v.co.x,v.co.y)
    # Sparse collapsed bank clods and crop stubble are grounded, not floating
    # decorative road stones. Keep wheel lanes and the leader plateau clear.
    rng=np.random.default_rng(305)
    straw=surface('305 weathered ditch stubble',[(.075,.068,.036),(.20,.17,.087)],12,rough=.95,bump=.0004)
    vs=[];fs=[]
    for _ in range(2100):
        side=(-1,1)[int(rng.integers(2))];y=float(rng.uniform(-245,135));x=side*float(rng.uniform(2.2,3.8));z=road_height(x,y)+.002
        if math.sin(y*.25)<-.5:continue
        p=Vector((x,y,z));a=float(rng.uniform(0,math.tau));d=Vector((math.cos(a),math.sin(a),.08))*float(rng.uniform(.04,.16));w=Vector((-d.y,d.x,0)).normalized()*.002
        q=len(vs);vs.extend((p-w,p+w,p+d+w*.3,p+d-w*.3));fs.append((q,q+1,q+2,q+3))
    mesh('305 settled ditch stubble',vs,fs,straw)

def wind():
    for ob in bpy.data.objects:
        if not ob.name.startswith('304 cultivated parcel canopy'):continue
        g=next(m.node_group for m in ob.modifiers if m.type=='NODES');n=g.nodes;l=g.links
        instances=next(x for x in n if x.bl_idname=='GeometryNodeInstanceOnPoints')
        for link in list(instances.inputs['Rotation'].links):l.remove(link)
        p=n.new('GeometryNodeInputPosition');time=n.new('ShaderNodeValue');time.name='305 nonperiodic wind advection'
        for f in (1,FRAMES+1):time.outputs[0].default_value=(f-1)/24;time.outputs[0].keyframe_insert('default_value',frame=f)
        velocity=n.new('ShaderNodeCombineXYZ');speed=n.new('ShaderNodeMath');speed.operation='MULTIPLY';speed.inputs[1].default_value=2.6;l.new(time.outputs[0],speed.inputs[0]);l.new(speed.outputs[0],velocity.inputs['X'])
        adv=n.new('ShaderNodeVectorMath');adv.operation='SUBTRACT';l.new(p.outputs[0],adv.inputs[0]);l.new(velocity.outputs[0],adv.inputs[1])
        gust=n.new('ShaderNodeTexNoise');gust.inputs['Scale'].default_value=.115;gust.inputs['Detail'].default_value=2;gust.inputs['Roughness'].default_value=.58;l.new(adv.outputs[0],gust.inputs[0])
        bend=n.new('ShaderNodeMapRange');bend.inputs['From Min'].default_value=.27;bend.inputs['From Max'].default_value=.72;bend.inputs['To Min'].default_value=.025;bend.inputs['To Max'].default_value=.235;l.new(gust.outputs['Fac'],bend.inputs[0])
        small=n.new('ShaderNodeTexNoise');small.inputs['Scale'].default_value=1.8;small.inputs['Detail'].default_value=1;l.new(adv.outputs[0],small.inputs[0])
        side=n.new('ShaderNodeMapRange');side.inputs['To Min'].default_value=-.025;side.inputs['To Max'].default_value=.04;l.new(small.outputs['Fac'],side.inputs[0])
        rot=n.new('ShaderNodeCombineXYZ');l.new(bend.outputs[0],rot.inputs['Y']);l.new(side.outputs[0],rot.inputs['X']);l.new(rot.outputs[0],instances.inputs['Rotation'])
        # Far parcels preserve occupied land past the newly extended departure.
        data=ob.data;indices=[v.index for v in data.vertices if -145<v.co.y<-60];pts=[tuple(data.vertices[i].co) for i in indices]
        if pts:
            extension=ob.copy();new=bpy.data.meshes.new('305 far parcel roots');new.from_pydata(pts,[],[]);new.update()
            a=new.attributes.new('scale','FLOAT_VECTOR','POINT');a.data.foreach_set('vector',np.asarray([tuple(data.attributes['scale'].data[i].vector) for i in indices],dtype=np.float32).ravel())
            extension.data=new;bpy.context.scene.collection.objects.link(extension);extension.name='305 departure parcel extension';extension.location.y=-110

def farms():
    sources=[o for o in bpy.data.objects if o.name.startswith('distant mud courtyard')]
    for i,source in enumerate(sources):
        ob=source.copy();ob.data=source.data.copy();bpy.context.scene.collection.objects.link(ob);ob.name='305 approach courtyard'
        ob.location=(18+(i%3)*6+(i//3)*3,22+(i//3)*28+(i%2)*4,source.location.z)
        ob.rotation_euler.z=.10*(i%3-1)
    # The shared road/swale mesh already includes the surrounding plain and
    # extends to the departure endpoint; no overlapping second ground plane.

def build():
    terrain();wind();farms()
