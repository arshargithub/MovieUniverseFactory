"""Fit existing supporting-crowd wrists to their actual prop frames."""
import json
import bpy
from mathutils import Vector

def attention(roots):
    """A bounded look toward the departing rider; feet/clearance remain untouched."""
    s=bpy.context.scene;bike=bpy.data.objects['BIKE travel owner']
    tracks={r.name:[] for r in roots};crossings={}
    actors={r.name:[next(o for o in r.children if o.name.startswith(prefix))
                   for prefix in ('secondary adult head292','secondary facial and crown frame292')] for r in roots}
    for f in range(1,697):
        s.frame_set(f)
        for r in roots:
            tracks[r.name].append([o.rotation_euler.copy() for o in actors[r.name]])
            if r.name not in crossings and bike.matrix_world.translation.y<r.matrix_world.translation.y-.4:
                crossings[r.name]=f
    report=[]
    for index,r in enumerate(roots):
        assert r.name in crossings
        side=1 if r.location.x>0 else -1
        start=crossings[r.name]+2+(index%4)*2
        for f,rotations in enumerate(tracks[r.name],1):
            u=max(0,min(1,(f-start)/24));w=u*u*(3-2*u)
            for ob,rotation in zip(actors[r.name],rotations):
                ob.rotation_euler=rotation;ob.rotation_euler.z+=side*1.12*w
                ob.keyframe_insert('rotation_euler',frame=f)
        report.append({'actor':r.name,'pass_frame':crossings[r.name],'look_start':start,
                       'look_duration_frames':24,'additional_yaw_rad':side*1.12,
                       'body_and_feet_changed':False})
    s.frame_set(283)
    return report

def fit(root):
    bpy.context.scene.frame_set(283)
    palms=[o for o in root.children if o.name.startswith('secondary closed hand')]
    sleeves=[o for o in root.children if not o.hide_render and o.name.startswith('297 crowd sleeve')]
    pole=next(o for o in root.children if o.name=='spear' or o.name.startswith('spear.'))
    shield=next((o for o in root.children if o.name.startswith('300 round hide shield')),None)
    points=[pole.matrix_local@Vector(p.co[:3]) for p in pole.data.splines[0].points]
    a,b=points[0],points[-1]
    assert abs(b.z-a.z)>.5
    rows=[]
    for palm in palms:
        before=palm.location.copy()
        if before.x<0 and shield is None:continue
        if before.x>0:
            t=(before.z-a.z)/(b.z-a.z);goal=a.lerp(b,t);goal.x-=.005
            kind='spear axis through finger aperture'
        else:
            goal=shield.location.copy()
            # Shield geometry is authored in root coordinates with zero origin.
            if goal.length<.01:
                pts=[v.co for v in shield.data.vertices]
                goal=sum(pts,Vector())/len(pts)
            goal.y-=.090;goal.x-=.005
            from sikh257_layout import tube
            x,y,z=goal
            tube('319 shield rear handgrip',[(x+.005,y+.045,z-.075),(x+.005,y,z-.055),
                 (x+.005,y,z+.055),(x+.005,y+.045,z+.075)],.009,shield.data.materials[0],root)
            kind='shield rear support'
        sleeve=min(sleeves,key=lambda o:((sum((v.co for v in list(o.data.vertices)[-24:]),Vector())/24)-before).length)
        endpoint=sum((v.co for v in list(sleeve.data.vertices)[-24:]),Vector())/24
        assert (endpoint-before).length<.12
        delta=goal-endpoint
        sleeve.data=sleeve.data.copy()
        blocks=[k.data for k in sleeve.data.shape_keys.key_blocks] if sleeve.data.shape_keys else [sleeve.data.vertices]
        for block in blocks:
            assert len(block)==312
            for j in range(13):
                u=max(0,min(1,(j-4)/8));w=u*u*(3-2*u)
                for k in range(24):block[j*24+k].co+=delta*w
        palm.location=goal
        rows.append({'hand':palm.name,'prop':kind,'before':list(before),'after':list(goal),'sleeve':sleeve.name})
        sleeves.remove(sleeve)
    root['319_contact_fit']=json.dumps(rows)
    return rows
