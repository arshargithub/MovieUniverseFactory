"""Measured support/camera controls. These do not certify perceived motion."""
import json,math
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from movie_factory import sikh305_motion as c
def audit(out):
    s=bpy.context.scene;rig=bpy.data.objects['horse.rig'];road=bpy.data.objects['irregular packed farm track'];root=bpy.data.objects['BIKE travel owner']
    bvh=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    rows=[];occlusions=[];leader_camera=[]
    for f in range(1,c.FRAMES+1):
        t=(f-1)/24*c.RATE;s.frame_set(f);bpy.context.view_layer.update()
        if 13.5<=t<17.5:
            feet={}
            for name in ('DEF-f_toe.L','DEF-f_toe.R','DEF-r_toe.L','DEF-r_toe.R'):
                pb=rig.pose.bones[name];pts=[rig.matrix_world@pb.head,rig.matrix_world@pb.tail];gaps=[]
                for p in pts:
                    hit=bvh.ray_cast(Vector((p.x,p.y,12)),Vector((0,0,-1)))[0]
                    gaps.append(None if hit is None else p.z-hit.z)
                feet[name]={'head':list(pts[0]),'tail':list(pts[1]),'skeletal_endpoint_gaps':gaps}
            rows.append({'frame':f,'source_t':t,'feet':feet})
            head=rig.matrix_world@rig.pose.bones['head'].head;hips=rig.matrix_world@rig.pose.bones['hips'].head
            direction=head-hips;view=s.camera.location-hips;dot=direction.xy.normalized().dot(view.xy.normalized())
            leader_camera.append({'frame':f,'view_angle_from_horse_forward_deg':math.degrees(math.acos(max(-1,min(1,dot))))})
        else:
            origin=s.camera.matrix_world.translation
            for label,p in [('engine',(0,0,.60)),('head',(0,.32,1.54))]:
                target=root.matrix_world@Vector(p);d=target-origin;hit=bvh.ray_cast(origin,d.normalized(),max(0,d.length-.10))[0]
                if hit is not None:occlusions.append({'frame':f,'subject':label,'hit':list(hit)})
    record={'scope':'Actual static ground ray tests; evaluated skeletal toe endpoints, not exact deformed hoof mesh contacts or a visual pass','frames':c.FRAMES,'ground_occlusions':occlusions,'horse_support':rows,'leader_camera':leader_camera}
    (out/'support-and-camera-audit.json').write_text(json.dumps(record,indent=2))
    if occlusions:raise ValueError('Ground hides subject: '+repr(occlusions[:4]))
