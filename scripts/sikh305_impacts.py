"""Contact-born earth response for the revised horse performance; no simulation claim."""
import json,math
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from sikh257_layout import key
from movie_factory import sikh305_motion as c

def build_impacts(out):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(('305 hoof earth puff','305 kicked soil clod')):
            bpy.data.objects.remove(ob,do_unlink=True)
    s=bpy.context.scene;rig=bpy.data.objects['horse.rig'];road=bpy.data.objects['irregular packed farm track']
    ground=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    rng=np.random.default_rng(3058);events=[]
    definitions=[('spear',14.28,None,.20),('grip-left',14.45,'DEF-f_toe.L',.25),('grip-right',14.55,'DEF-f_toe.R',.25),
                 ('hind-drive-left',14.89,'DEF-r_toe.L',.35),('hind-drive-right',14.92,'DEF-r_toe.R',.35),
                 ('landing-left',16.02,'DEF-f_toe.L',1.0),('landing-right',16.055,'DEF-f_toe.R',.85)]
    dust=bpy.data.materials['305 expanding advected dust'];earth=bpy.data.materials['305 weathered loam bank']
    for label,t,bone,power in definitions:
        birth=round(t/c.RATE*c.FPS)+1;s.frame_set(birth);bpy.context.view_layer.update()
        p=(rig.matrix_world@rig.pose.bones[bone].tail) if bone else bpy.data.objects['LEADER spear world contact owner'].location.copy()
        hit=ground.ray_cast(Vector((p.x,p.y,10)),Vector((0,0,-1)))[0]
        if hit is None:raise ValueError('Missing impact support')
        p.z=hit.z+.008;events.append({'event':label,'source_t':t,'frame':birth,'edit_seconds':(birth-1)/24,'ground_point':list(p),'power':power})
        for k in range(3):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);ob=bpy.context.object;ob.name='305 hoof earth puff '+label;ob.data.materials.append(dust)
            drift=Vector((float(rng.uniform(-.35,.35)),float(rng.uniform(-.35,.35)),.16+power*.10));offset=Vector((float(rng.uniform(-.06,.06)),float(rng.uniform(-.06,.06)),0))
            ob.hide_render=True;ob.keyframe_insert('hide_render',frame=1);ob.keyframe_insert('hide_render',frame=birth-1);ob.hide_render=False;ob.keyframe_insert('hide_render',frame=birth)
            for f in range(birth,birth+55,2):
                age=(f-birth)/24;size=.07+(.24+.32*power)*age;ob.location=p+offset+drift*age;ob.scale=(size*1.35,size,size*.55)
                den=(1-math.exp(-age*45))*math.exp(-age*2.4)*power*1.7;ob.color=(1,1,1,den);key(ob,f);ob.keyframe_insert('color',frame=f)
            ob.color=(1,1,1,0);ob.keyframe_insert('color',frame=birth+55);ob.hide_render=True;ob.keyframe_insert('hide_render',frame=birth+56)
        for k in range(round(10+24*power)):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1);ob=bpy.context.object;ob.name='305 kicked soil clod '+label;ob.data.materials.append(earth)
            rad=float(rng.uniform(.008,.024))*(.6+.5*power);ob.scale=(rad,rad*.7,rad*.6)
            theta=float(rng.uniform(0,math.tau));speed=float(rng.uniform(.5,1.8))*(.4+.6*power);v=Vector((speed*math.cos(theta),speed*math.sin(theta),float(rng.uniform(.6,1.8))*(.5+.5*power)))
            flight=2*v.z/9.81;start=p+Vector((0,0,rad*.6));ob.hide_render=True;ob.keyframe_insert('hide_render',frame=1);ob.keyframe_insert('hide_render',frame=birth-1);ob.hide_render=False;ob.keyframe_insert('hide_render',frame=birth)
            for f in range(birth,birth+49):
                age=(f-birth)/24;a=min(age,flight);q=start+Vector((v.x*a,v.y*a,v.z*a-4.905*a*a))
                if age>flight:
                    u=age-flight;bounce=min(u,flight*.3);q+=Vector((v.x*bounce*.3,v.y*bounce*.3,v.z*.3*bounce-4.905*bounce*bounce))
                q.z=max(start.z,q.z);ob.location=q;ob.rotation_euler=(min(age,flight*1.3)*5,min(age,flight*1.3)*7,theta);key(ob,f)
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for p in fc.keyframe_points:p.interpolation='CONSTANT' if fc.data_path=='hide_render' else 'LINEAR'
    (out/'impact-events.json').write_text(json.dumps({'events':events,'physical_scope':'Authored ballistic clods with one damped bounce on the flat supported hill core; expanding dilute dust, no general terrain simulator'},indent=2))
