"""Reviewed derivative repairs. Preserve source305 and unaffected choreography."""
import math,json
import bpy
import numpy as np
from mathutils import Vector
from mathutils.noise import noise_vector
from mathutils.bvhtree import BVHTree
from movie_factory import sikh314_motion as m
from sikh257_layout import key

def n(x,y,scale=1):
    return noise_vector(Vector((x*scale,y*scale,4.719)))[0]

def terrain(out):
    from sikh305_land import road_height,bank_height
    from sikh292_assets import surface
    road=bpy.data.objects['irregular packed farm track']
    boundaries=(-245,-211,-178,-156,-145,-111,-78,-46,-12,22,54,91,130)
    def height(x,y):
        a=abs(x);base=road_height(x,y)
        if a<=1.60:return base
        old=bank_height(x,y) if 1.6<x<24 and -46<y<-12 else base
        if old>base+.06:
            core=math.hypot((x-7.5)/2.6,(y+29)/3.6)
            weight=min(1,max(0,(core-.85)/.65))
            return old+weight*(.08*n(x,y,1.2)+.04*n(x,y,4.3))
        mask=min(1,(a-1.60)/.5)
        center=2.85+.38*n(x*.1,y,.32)+.24*n(2,y,.77)
        width=.52+.26*n(4,y,.21)
        d=(a-center)/width
        # Irregular trapezoid bed/shoulders, with dissimilar cut and deposited banks.
        channel=-(.25+.09*n(7,y,.35))*max(0,1-abs(d)**1.6)
        lip=.08*math.exp(-((d-1.2)/.52)**2)*(1+.55*n(x,y,1.1))
        erosion=.055*n(x,y,3.2)*math.exp(-((abs(d)-.8)/.8)**2)
        z=.035*n(x,y,1.1)+.018*n(x,y,6.4)+channel+lip+erosion
        if a>3.9:
            closest=min(abs(y-b-.18*n(x,b,.23)) for b in boundaries)
            z+=.065*math.exp(-(closest/(.48+.08*n(x,y,.7)))**2)
        return base*(1-mask)+mask*z
    for v in road.data.vertices:
        if abs(v.co.x)>1.60:v.co.z=height(v.co.x,v.co.y)
    soil=surface('314 layered worn earthen track',[(.16,.125,.074),(.245,.195,.122)],12,rough=.94,bump=.002)
    nodes=soil.node_tree.nodes;links=soil.node_tree.links;bs=nodes['Principled BSDF']
    tex=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(6,1.8,3);links.new(tex.outputs['Object'],mapping.inputs[0])
    streak=nodes.new('ShaderNodeTexNoise');streak.inputs['Scale'].default_value=3.6;streak.inputs['Detail'].default_value=3;links.new(mapping.outputs[0],streak.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.45;bump.inputs['Distance'].default_value=.012;links.new(streak.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],bs.inputs['Normal'])
    grain=nodes.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=180;grain.inputs['Detail'].default_value=2;links.new(tex.outputs['Object'],grain.inputs['Vector'])
    micro=nodes.new('ShaderNodeBump');micro.inputs['Strength'].default_value=.25;micro.inputs['Distance'].default_value=.0015;links.new(grain.outputs['Fac'],micro.inputs['Height']);links.new(bump.outputs[0],micro.inputs['Normal']);links.new(micro.outputs[0],bs.inputs['Normal'])
    basecolor=bs.inputs['Base Color'].links[0].from_socket
    attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='314 soil zones'
    blend=nodes.new('ShaderNodeMixRGB');blend.blend_type='MULTIPLY';blend.inputs[0].default_value=.72;links.new(basecolor,blend.inputs[1]);links.new(attr.outputs['Color'],blend.inputs[2]);links.new(blend.outputs[0],bs.inputs['Base Color'])
    road.data.materials.clear();road.data.materials.append(soil)
    colors=road.data.color_attributes.new(name='314 soil zones',type='FLOAT_COLOR',domain='POINT')
    for v,c in zip(road.data.vertices,colors.data):
        x,y,z=v.co;a=abs(x)
        wet=math.exp(-((a-2.85)/.31)**2)*(.6+.4*n(x,y,.45))
        rut=math.exp(-((a-.72)/.24)**2)
        shade=1-.55*wet-.19*rut
        c.color=(shade,shade*.97,shade*.89,1)
    for p in road.data.polygons:p.material_index=0
    removed=[]
    for ob in list(bpy.data.objects):
        if ob.name.startswith('304 worn cross-field bund'):
            removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
    for ob in bpy.data.objects:
        if ob.type=='MESH' and ob.name.startswith(('304 rooted ditch','305 settled ditch','304 cultivated parcel','305 departure parcel')):
            # Mesh point origins are world-aligned; preserve blades' relative height.
            for v in ob.data.vertices:
                x,y=v.co.x+ob.location.x,v.co.y+ob.location.y
                old=max(road_height(x,y),bank_height(x,y)) if 1.6<x<24 and -46<y<-12 else road_height(x,y)
                v.co.z+=height(x,y)-old
    road.data.update()
    # Moisture-supported weed patches and fallen straw, not regularly spaced studs.
    from sikh257_native import mesh
    rng=np.random.default_rng(314);vs=[];fs=[]
    for _ in range(10000):
        y=float(rng.uniform(-250,135));x=float(rng.uniform(2.35,3.75))*(-1 if rng.random()<.5 else 1)
        if n(x,y,.37)<-.08:continue
        h=float(rng.uniform(.045,.16));p=Vector((x,y,height(x,y)+.002))
        for k in range(5):
            a=float(rng.uniform(0,math.tau));d=Vector((math.cos(a),math.sin(a),0));w=Vector((-d.y,d.x,0))*.009
            q=len(vs)
            for j in range(4):
                u=j/3;center=p+d*h*u*u*.8+Vector((0,0,h*(u-.25*u*u)))
                vs.extend([center-w*(1-u),center+w*(1-u)])
                if j:fs.append((q+j*2-2,q+j*2-1,q+j*2+1,q+j*2))
    weeds=surface('314 ditch sedges and dry stubble',[(.06,.067,.026),(.19,.175,.075)],8,rough=.96,bump=.0004)
    mesh('314 clustered drainage vegetation',vs,fs,weeds)
    (out/'terrain.json').write_text(json.dumps({'removed_green_overlays':removed,'contact_lane_preserved_abs_x':1.6,'plateau_preserved':True,'method':'integrated irregular banks and earth bunds; zone shading with longitudinal wear'},indent=2))

def performance(out):
    import sikh305_scene as old
    from movie_factory import sikh305_motion as c
    original_bone,original_key,original_rear=old.bone_x,old.key,c.rear
    changed=set();rest=bpy.data.objects['HORSE hind support pivot'].location.copy()
    def rekey(ob,f):
        t=(f-1)/24*c.RATE;p=m.pose(t)
        if ob.name=='HORSE hind support pivot' and f not in changed:
            changed.add(f)
            # More upright chest with support beneath pelvis; no world-space teleport.
            ob.rotation_euler.x-=.17*p['rise']
            ob.location.y-=.08*p['rise']
            ob.location.z+=.18*p['rise']
        original_key(ob,f)
    def bone(rig,name,angle,f):
        t=(f-1)/24*c.RATE;p=m.pose(t,'R' if name.endswith('.R') else 'L')
        if p['rise']>0:
            if name.startswith('upper_arm_fk'):angle=p['shoulder']
            elif name.startswith('forearm_fk'):angle=p['elbow']
            elif name.startswith('forefoot_fk'):angle=p['wrist']
            elif name.startswith('f_toe_fk'):angle=p['toe']
        if name=='neck':angle=p['neck']+.009*math.sin(t*1.7)
        elif name=='head':angle=p['head']+.012*math.sin(t*2.1)
        original_bone(rig,name,angle,f)
    c.rear=lambda t:m.pose(t)['rise'];old.key=rekey;old.bone_x=bone
    try:old.horse(out,rebuild_groom=True)
    finally:old.key=original_key;old.bone_x=original_bone;c.rear=original_rear

def debris(out):
    s=bpy.context.scene;road=bpy.data.objects['irregular packed farm track']
    bvh=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    records=[]
    for ob in bpy.data.objects:
        if not ob.name.startswith('299 tire-contact earth chip'):continue
        curves=[fc for ly in ob.animation_data.action.layers for st in ly.strips for bag in st.channelbags for fc in bag.fcurves]
        hide=next(fc for fc in curves if fc.data_path=='hide_render')
        birth=round(next(p.co.x for p in hide.keyframe_points if p.co.y==0))
        death=round(max(p.co.x for p in hide.keyframe_points))
        for i in range(len(hide.keyframe_points)-1,-1,-1):
            if hide.keyframe_points[i].co.x>birth:hide.keyframe_points.remove(hide.keyframe_points[i],fast=True)
        end=death-1
        # Find the ground-clamped part of the inherited flight, then stop spin.
        zcurve=next(fc for fc in curves if fc.data_path=='location' and fc.array_index==2)
        previous=None
        for f in range(birth+3,death):
            z=zcurve.evaluate(f)
            if previous is not None and abs(z-previous)<.00005:
                end=min(f+3,death-1);break
            previous=z
        for fc in curves:
            if fc.data_path in ('location','rotation_euler'):
                for i in range(len(fc.keyframe_points)-1,-1,-1):
                    if fc.keyframe_points[i].co.x>end:fc.keyframe_points.remove(fc.keyframe_points[i],fast=True)
        s.frame_set(end);bpy.context.view_layer.update()
        p=ob.location.copy();hit=bvh.ray_cast(Vector((p.x,p.y,8)),Vector((0,0,-1)))[0]
        if hit is None:raise ValueError('Debris has no support')
        p.z=hit.z+max(.003,ob.dimensions.z*.35)
        # Settled final key extends to the end; no lifetime visibility event.
        ob.location=p;key(ob,end);key(ob,m.FRAMES)
        ob.hide_render=False;ob.keyframe_insert('hide_render',frame=m.FRAMES)
        records.append({'name':ob.name,'birth':birth,'settled_frame':end,'settled_position':list(p),'visible_until':m.FRAMES})
    (out/'debris.json').write_text(json.dumps(records,indent=2))

def build(out):
    bpy.context.scene.frame_set(1)
    terrain(out);print('314 terrain complete',flush=True)
    crops=[o for o in bpy.data.objects if o.name.startswith(('304 cultivated','305 departure parcel','304 boundary tree'))]
    for ob in crops:ob.hide_viewport=True
    performance(out);print('314 independent horse profiles complete',flush=True)
    debris(out)
    for ob in crops:ob.hide_viewport=False
    bpy.context.scene.frame_set(1)
