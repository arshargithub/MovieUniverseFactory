"""Saddle-supported lower-limb response for the mounted supporting actor."""
import math,json
import bpy
from mathutils import Vector
from sikh257_native import mesh,material
from sikh257_layout import key
from sikh297_layers import endpoints,sleeve_points,sleeve_faces
from sikh319_cast import strands
from sikh320_performance import bell,curves,RATE
from movie_factory.sikh257_geometry import joint_between

def support(out):
    s=bpy.context.scene;s.frame_set(252);bpy.context.view_layer.update()
    root=bpy.data.objects['mounted leader'];pivot=bpy.data.objects['HORSE hind support pivot']
    old=sorted([o for o in root.children if not o.hide_render and o.name.startswith('297 continuous leader trousers')],key=lambda o:o.name)
    boots=sorted([o for o in root.children if o.name.startswith('297 mounted boot')],key=lambda o:o.name)
    cuffs=sorted([o for o in root.children if o.name.startswith('297 boot cuff')],key=lambda o:o.name)
    assert len(old)==len(boots)==len(cuffs)==2
    leather=material('320 stirrup worn dark leather',(.045,.026,.014));leather.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85
    iron=material('320 stirrup iron',(.11,.12,.13));bs=iron.node_tree.nodes['Principled BSDF'];bs.inputs['Metallic'].default_value=.72;bs.inputs['Roughness'].default_value=.48
    reports=[]
    for index,(source,boot,cuff) in enumerate(zip(old,boots,cuffs)):
        s.frame_set(252);bpy.context.view_layer.update();suffix='' if index==0 else '.001'
        a,b=endpoints(bpy.data.objects['leader thigh'+suffix],.095)
        bb,c=endpoints(bpy.data.objects['leader shin'+suffix],.07);b=(b+bb)/2
        l1=(b-a).length;l2=(c-b).length;boot_delta=boot.location-c;side=-1 if a.x<0 else 1
        anchor_local=a+Vector((side*.06,-.025,.015))
        anchor_pivot=pivot.matrix_world.inverted()@(root.matrix_world@anchor_local)
        delta_world=root.matrix_world@c-root.matrix_world@anchor_local
        length=delta_world.length
        strap=strands('320 saddle to stirrup leather',[[anchor_local,c]],.009,leather,root,False)
        strap.data.bevel_resolution=2
        loop=strands('320 supported stirrup iron',[[Vector((0,0,0)) for _ in range(17)]],.006,iron,root,False)
        poses=[];rows=[]
        for f in range(252,442):
            s.frame_set(f);bpy.context.view_layer.update();t=(f-1)/24*RATE
            anchor=pivot.matrix_world@anchor_pivot
            swing=.035*bell(t,14.1,14.75,15.35)-.045*bell(t,15.2,16.1,17.12)+.035*bell(t,17.10,17.23,17.75)
            d=delta_world+Vector((0,swing,0));d.normalize();target=anchor+d*length
            inv=root.matrix_world.inverted();q=inv@target
            knee=Vector(joint_between(a,q,l1,l2,(0,-1,0)))
            pts=sleeve_points(a,knee,q,(.115,.086,.056))
            # Preserve restrained gathered cloth, not a bare cylindrical limb.
            for j in range(13):
                center=sum((Vector(p) for p in pts[j*24:(j+1)*24]),Vector())/24
                for k in range(24):
                    idx=j*24+k;u=j/12
                    pts[idx]=center+(Vector(pts[idx])-center)*(1+.10*math.sin(math.pi*u)+.035*math.sin(k*math.tau/24*5+j*.7)*math.sin(math.pi*u))
            poses.append(pts);boot.location=q+boot_delta;key(boot,f)
            cuff.location=q-c;key(cuff,f)
            for p,co in zip(strap.data.splines[0].points,(inv@anchor,q+Vector((0,0,-.06)))):
                p.co=(*co,1);p.keyframe_insert('co',frame=f)
            for k,p in enumerate(loop.data.splines[0].points):
                angle=math.pi+math.pi*k/16
                co=q+Vector((.073*math.cos(angle),-.035,-.005+.075*math.sin(angle)))
                p.co=(*co,1);p.keyframe_insert('co',frame=f)
            rows.append({'frame':f,'hip':list(a),'knee':list(knee),'ankle':list(q),'ankle_support_radius_world':length,'strap_length_world':((root.matrix_world@(q+Vector((0,0,-.06))))-anchor).length,'thigh':(knee-a).length,'calf':(q-knee).length})
        ob=mesh('320 supported mounted trousers',poses[0],sleeve_faces(),source.data.materials[0]);ob.parent=root;ob.shape_key_add(name='Basis')
        for f,pts in zip(range(252,442),poses):
            sk=ob.shape_key_add(name=f'frame{f}')
            for p,q in zip(sk.data,pts):p.co=q
            for ff,val in ((f-1,0),(f,1),(f+1,0)):sk.value=val;sk.keyframe_insert('value',frame=ff)
        source.hide_render=True;source.hide_viewport=True
        reports.append({'side':side,'rest_lengths':[l1,l2],'rows':rows})
    for ob in bpy.data.objects:
        if ob.name.startswith(('320','297 mounted boot','297 boot cuff')):
            for owner in (ob,ob.data,getattr(ob.data,'shape_keys',None)):
                if owner is not None:
                    for fc in curves(owner):
                        for p in fc.keyframe_points:p.interpolation='LINEAR'
    (out/'lower-limb-support.json').write_text(json.dumps(reports,indent=2))
