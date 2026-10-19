"""Read-only native invariants, not an artistic or physics qualification."""
import json,math
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def verify(out,source):
    road=bpy.data.objects['irregular packed farm track'];ground=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    trace=json.loads((source/'coordinated-motion.json').read_text());errors=[]
    for row in trace:
        for which in ('front','rear'):
            p=Vector(row[which+'_tread_contact']);hit=ground.ray_cast(Vector((p.x,p.y,10)),Vector((0,0,-1)))[0]
            if hit is None:raise ValueError('Missing actual terrain support')
            errors.append({'frame':row['frame'],'wheel':which,'signed_m':p.z-hit.z})
    assert max(abs(r['signed_m']) for r in errors)<.016
    s=bpy.context.scene;rig=bpy.data.objects['horse.rig'];s.frame_set(1);bpy.context.view_layer.update()
    original={n:rig.matrix_world@rig.pose.bones[n].head for n in ('hind_foot_ik.L','hind_foot_ik.R')};hind=[]
    for f in range(275,357):
        s.frame_set(f);bpy.context.view_layer.update()
        hind.append({'frame':f,**{n:(rig.matrix_world@rig.pose.bones[n].head-original[n]).length for n in original}})
    births=json.loads((source/'dust-ownership.json').read_text());drift=[]
    for b in births:
        ob=bpy.data.objects[b['name']];assert ob.parent is None
        times=sorted(set([max(1,b['birth_frame']),min(696,max(1,b['birth_frame']+24)),min(696,max(1,b['birth_frame']+72))]));prev=None
        for f in times:
            s.frame_set(f);age=(f-b['birth_frame'])/24;expected=Vector(b['world_birth'])+Vector(b['world_drift_mps'])*age+Vector((0,0,.16))
            err=(ob.location-expected).length;assert err<.002
            if prev is not None:assert min(ob.scale)>=prev-.001
            prev=min(ob.scale)
        drift.append({'object':ob.name,'parent':None,'tested_frames':times,'world_drift_error_m':err})
    chips=[o for o in bpy.data.objects if o.name.startswith('299 tire-contact earth chip')];s.frame_set(696)
    assert all(not o.hide_render for o in chips)
    (out/'native-checks.json').write_text(json.dumps({'wheel_contact_max_abs_m':max(abs(r['signed_m']) for r in errors),'wheel_contacts':errors,'hind_support_control_drift':hind,'world_space_dust':drift,'persistent_tire_chips_at_end':len(chips),'limits':'Support-control and source-curve checks do not establish rendered anatomy, naturalness, timing or sound.'},indent=2))
