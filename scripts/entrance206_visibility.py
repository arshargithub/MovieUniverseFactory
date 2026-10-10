"""Camera/terrain line-of-sight evidence; not a semantic visual pass."""
import numpy as np

def inspect(scene,f):
 import bpy
 from mathutils import Vector
 from mathutils.bvhtree import BVHTree
 from bpy_extras.object_utils import world_to_camera_view
 from entrance205_scene import FLOOR
 from entrance205_motion import sample
 from entrance206_checkpoint import CHECKPOINT_Y
 land=bpy.data.objects['AS_valley_landform'];land.data.calc_loop_triangles();tree=BVHTree.FromPolygons([tuple(land.matrix_world@v.co) for v in land.data.vertices],[tuple(t.vertices) for t in land.data.loop_triangles],all_triangles=True)
 origin=scene.camera.matrix_world.translation;rows=[]
 targets=[('checkpoint',np.array([0,CHECKPOINT_Y,-10.]))]+[(f'route_t{t}',FLOOR+8.3*(sample(t)['position']+[0,0,.3])) for t in (2.5,3.,3.5,4.,4.5,5.,6.)]
 for name,p in targets:
  target=Vector(p);delta=target-origin;hit=tree.ray_cast(origin,delta.normalized(),delta.length-.01);screen=world_to_camera_view(scene,scene.camera,target)
  rows.append(dict(name=name,world=p.tolist(),screen=list(screen),terrain_occlusion=None if hit[0] is None else list(hit[0])))
 return dict(frame=f,targets=rows)
