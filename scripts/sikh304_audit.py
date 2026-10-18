"""Actual-camera landscape occlusion check; not a perceptual pass."""
import json
import bpy
from mathutils import Vector
from movie_factory.sikh304_motion import FPS,FRAMES,RATE
def camera_clearance(out):
    s=bpy.context.scene;bank=bpy.data.objects['low field bank for leader'];root=bpy.data.objects['BIKE travel owner'];rows=[]
    for f in range(1,FRAMES+1):
        t=(f-1)/FPS*RATE
        if 13.5<=t<17.5:continue # Editorial subject is the leader here.
        s.frame_set(f);bpy.context.view_layer.update();origin=bank.matrix_world.inverted()@s.camera.matrix_world.translation
        for label,local in [('engine',(0,0,.60)),('head',(0,.32,1.54))]:
            target=bank.matrix_world.inverted()@(root.matrix_world@Vector(local));direction=target-origin;distance=direction.length
            hit,point,_,_=bank.ray_cast(origin,direction.normalized(),distance=max(0,distance-.05))
            if hit:rows.append({'frame':f,'target':label,'distance':distance,'occluder_distance':(point-origin).length})
    (out/'camera-bank-clearance.json').write_text(json.dumps({'scope':'Earth bank rays to rider head and engine; does not certify all visibility','frames':FRAMES,'occlusions':rows},indent=2)+'\n')
    if rows:raise ValueError('Bank blocks motorcycle camera: '+str(rows[:4]))
