"""Expose the real escape shelf without changing its traversed support."""
import json,sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance205_motion import smooth

def cutback(xy,height,distance):
 p=np.asarray(xy);release=(1-smooth((-p[:,1]-22)/10))*smooth((distance-1.35)/1.5)*smooth((p[:,0]+14)/4)
 return np.where(height>0,height*(1-release),height)

def terrain(scene,previous_world=None):
 import bpy
 from mathutils import Vector
 from mathutils.bvhtree import BVHTree
 from entrance205_scene import FLOOR
 from entrance205_motion import trajectory
 from entrance205_geography import fields
 land=bpy.data.objects['AS_valley_landform'];land.data=land.data.copy();land.data.calc_loop_triangles();tris=[tuple(t.vertices) for t in land.data.loop_triangles]
 matrix=np.array(land.matrix_world);local=np.array([v.co[:] for v in land.data.vertices]);old=local@matrix[:3,:3].T+matrix[:3,3];xy=(old[:,:2]-FLOOR[:2])/8.3
 _,distance=fields(xy,trajectory());height=(old[:,2]-FLOOR[2])/8.3;new=old.copy();new[:,2]=FLOOR[2]+8.3*cutback(xy,height,distance)
 protected=distance<=1.35;error=float(np.max(abs(new[protected]-old[protected])))
 if error>1e-5:raise ValueError('Traversed support changed')
 oldtree=BVHTree.FromPolygons((old if previous_world is None else previous_world).tolist(),tris,all_triangles=True);tree=BVHTree.FromPolygons(new.tolist(),tris,all_triangles=True);inv=np.linalg.inv(matrix);q=new@inv[:3,:3].T+inv[:3,3];land.data.vertices.foreach_set('co',q.ravel());land.data.update()
 def ground(tree,x,y):
  hit=tree.ray_cast(Vector((x,y,2000)),Vector((0,0,-1)),4000)
  if hit[0] is None:raise ValueError('Stone outside actual terrain')
  return hit[0].z
 rows=[]
 for o in scene.objects:
  if o.hide_render or not o.name.startswith('MF205_grounded_stone_'):continue
  x,y=o.location.x,o.location.y;delta=ground(tree,x,y)-ground(oldtree,x,y)
  if abs(delta)<1e-5:continue
  o.location.z+=delta
  v=np.array([v.co[:] for v in o.data.vertices]);R=np.array(o.rotation_euler.to_matrix());v=(v*np.array(o.scale))@R.T
  low=v[np.argsort(v[:,2])[:16]]+np.array(o.location);clear=[p[2]-ground(tree,p[0],p[1]) for p in low]
  adjust=max(0.,min(clear)+.12);o.location.z-=adjust
  rows.append(dict(name=o.name,height_change=float(delta-adjust),minimum_sampled_support_clearance=float(min(clear)-adjust)))
 return dict(changed_vertices=int(np.sum(abs(new[:,2]-old[:,2])>1e-5)),protected_vertices=int(protected.sum()),support_max_error=error,reseated_stones=rows,method='Localized approach-spur setback; preserved1.35m route/road envelope and original terrain beyond approach sector')

def checkpoint(scene):
 import bpy
 from mathutils import Vector
 for j,delta in ((0,-.45),(1,.40)):
  x,y,z=((-24,-876,-20.931) if j==0 else (23,-871,-20.931));root=bpy.data.objects.new(f'MF206_guard{j}_stance',None);scene.collection.objects.link(root);root.location=(x,y,z)
  for o in list(scene.objects):
   if o!=root and o.name.startswith(f'MF206_guard{j}_'):
    w=o.matrix_world.copy();o.parent=root;o.matrix_world=w
  root.rotation_euler.z=delta
 posts=[o for o in scene.objects if o.name.startswith('MF206_checkpoint_post')]
 if len(posts)!=2:raise ValueError('Checkpoint posts changed')
 for o in posts:o.scale.z*=32/19;o.location.z+=6.5
 wood=posts[0].data.materials[0];a,b=Vector((-28,-900,-20.931+31)),Vector((28,-900,-20.931+31))
 bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=1.0,radius2=1.0,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.name='MF206_checkpoint_lintel';o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(wood)
 return dict(mounted_stance='Angled across approach for readable horse/rider silhouettes; no anatomy scaling',barrier='Braced timber gate and stone wings, posts3.86m, opening6.75m, no faction insignia')

def main():
 import bpy
 from entrance205_actor import save
 from entrance206_checkpoint import camera
 from entrance206_visibility import inspect
 from wardrobe_motion178_controls import render_geometry_paused
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job!={'operation':'geography19'}:raise ValueError('Closed206 sightline correction')
 src=base.BASE/'entrance206-composition18';sha='4a2d096656b451a24eed4932ce67883d70feddb7da411f2fa91d452abe114ef3';out=base.BASE/'entrance206-geography19'
 if out.exists() or base.digest(src/'scene.blend')!=sha:raise ValueError('Source/output')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(361);base.check_protected()
 with render_geometry_paused():record=dict(source_sha256=sha,terrain=terrain(scene),checkpoint=checkpoint(scene))
 record['camera']=camera(scene);scene.frame_set(361);save(scene,out,record)
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;evidence=[]
 for f in (361,384,409,445,472,487):
  scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True);evidence.append(inspect(scene,f));print('206 GEOGRAPHY',f,flush=True)
 (out/'composition-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
