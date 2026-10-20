"""Crowd makes room while retaining attention on the passing protagonist."""
import math,json
import bpy
from mathutils import Vector
from sikh257_layout import key
from sikh320_performance import crowd,rebind_neck,curves

def attention(out):
    s=bpy.context.scene;rider=bpy.data.objects['BIKE travel owner']
    preflight=[]
    for f in (252,365,381,417,441):
        s.frame_set(f);bpy.context.view_layer.update()
        for upper in [o for o in s.objects if o.name.startswith('320 articulated upper body FOOT')]:
            head=next(o for o in upper.children if o.name.startswith('secondary adult head'))
            direction=upper.matrix_world.to_3x3().inverted()@(rider.matrix_world.translation+Vector((0,0,1.25))-head.matrix_world.translation)
            yaw=math.atan2(direction.x,-direction.y)
            preflight.append({'frame':f,'actor':upper.parent.name,'body_yaw':upper.parent.rotation_euler.z,'head_yaw':head.rotation_euler.z,'target_yaw':yaw,'rider':list(rider.matrix_world.translation),'head':list(head.matrix_world.translation)})
    (out/'gaze-preflight.json').write_text(json.dumps(preflight,indent=2))
    report=crowd(out)
    rows=[]
    for index,upper in enumerate(sorted([o for o in s.objects if o.name.startswith('320 articulated upper body FOOT')],key=lambda o:o.name)):
        head=next(o for o in upper.children if o.name.startswith('secondary adult head'))
        features=next(o for o in upper.children if o.name.startswith('secondary facial and crown'))
        samples=[]
        for f in range(252,442):
            s.frame_set(f);bpy.context.view_layer.update()
            # Target rider chest, not the bike origin at ground level. Use
            # parent-space directions; the face donor's semantic front is -Y.
            target=rider.matrix_world.translation+Vector((0,0,1.25))
            direction=upper.matrix_world.to_3x3().inverted()@(target-head.matrix_world.translation)
            yaw=math.atan2(direction.x,-direction.y)
            delta=(yaw-math.pi+math.pi)%(2*math.pi)-math.pi
            yaw=math.pi+max(-1.12,min(1.12,delta))
            for ob in (head,features):ob.rotation_euler.z=yaw;key(ob,f)
            samples.append({'frame':f,'desired_neck_yaw':delta,'applied_neck_yaw':yaw-math.pi})
        rebind_neck(head)
        rows.append({'actor':upper.parent.name,'gaze_target':'rider chest throughout clearance','samples':samples})
    # The old thick saddle rolls pierced the upper trouser silhouette. Keep
    # the padded construction, but seat it below the rider's actual thigh.
    for ob in s.objects:
        if ob.name.startswith('saddle padded edge292'):
            ob.data=ob.data.copy();ob.data.bevel_depth=.009
            for sp in ob.data.splines:
                for p in sp.points:p.co.z-=.06
    (out/'attention.json').write_text(json.dumps(rows,indent=2))
    for row in rows:
        if max(abs(r['desired_neck_yaw']) for r in row['samples'])>1.35:
            raise ValueError('Gaze target exceeds comfortable head/torso range: '+row['actor'])
    for ob in s.objects:
        if ob.name.startswith(('320','secondary adult head','secondary facial and crown')):
            for owner in (ob,ob.data,getattr(ob.data,'shape_keys',None)):
                if owner is not None:
                    for fc in curves(owner):
                        for p in fc.keyframe_points:p.interpolation='LINEAR'
    (out/'attention.json').write_text(json.dumps(rows,indent=2))
