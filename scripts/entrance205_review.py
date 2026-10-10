"""Closed source-bound205 controls and exact-clock motion renders.

No hidden retiming or synthetic frames. Process success leaves visual review
NOT_RUN; full motion requires a separately recorded controls admission.
"""
import json,sys,time,struct
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

OPS={
 'opening11':('opening04',(217,265,291,303,315,327,339,360),'controls'),
 'opening47':('opening45',(217,291,297,303,309,315,321,327,333,339,360),'controls'),
 'route12':('scene10',(361,384,391,409,427,445,469,487,505,529,553,577,613,648),'controls'),
 'opening13':('opening04',tuple(range(217,361,2)),'motion'),
 'route14':('scene41',tuple(range(361,649,2)),'motion'),
 'opening15':('opening04',tuple(range(218,361,2)),'motion'),
 'route16':('scene41',tuple(range(362,649,2)),'motion'),
 'reopen17':('opening04',(217,315,360),'reopen'),
 'reopen18':('scene41',(361,409,487,529,577,648),'reopen'),
 'route23':('scene22',(361,391,409,445,469,487,505,529,577,648),'controls'),
 'route25':('backdrop24',(391,469,487,529,551,577,648),'controls'),
 'route39':('scene38',(361,391,409,427,445,469,481,493,505,529,553,577,613,648),'controls'),
 'route42':('scene41',(361,391,409,427,445,469,481,493,505,529,553,577,613,648),'controls'),
}


def main():
 import bpy
 from entrance198_terrain import fingerprint
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Closed205 review operation')
 op=job['operation'];folder,frames,kind=OPS[op];src=base.BASE/('entrance205-'+folder)/'scene.blend';out=base.BASE/('entrance205-'+op)
 result=json.loads((src.parent/'result.json').read_text())
 if out.exists() or base.digest(src)!=result['native_sha256']:raise ValueError('Changed source/existing output')
 if kind=='motion':
  gate=json.loads((src.parent/'internal-review.json').read_text())
  if gate['status']!='PROCEED_TO_FULL_MOTION' or gate['source_sha256']!=result['native_sha256']:raise ValueError('Missing control admission')
 for row in result['caches']:
  p=(src.parent/row['path']).resolve()
  if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Changed native cache')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
 bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
 scene.frame_set(217 if folder.startswith('opening') else 361);bpy.context.view_layer.update();structure=fingerprint(scene)
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type=='MESH_CACHE':
    with Path(bpy.path.abspath(m.filepath)).open('rb') as stream:count,vertices=struct.unpack('>ii',stream.read(8))
    if vertices!=len(ob.data.vertices) or list(ob.modifiers).index(m)!=0:raise ValueError('Cache topology/order: '+ob.name)
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
 rig=bpy.data.objects['MF_body156_fit_rig'];bones=('pelvis','chest','MF185_neck','MF185_head','hand.L','hand.R','foot.L','foot.R');rows=[]
 tree=None
 if not folder.startswith('opening') and kind=='controls':
  from mathutils import Vector
  from mathutils.bvhtree import BVHTree
  land=bpy.data.objects['AS_valley_landform'];land.data.calc_loop_triangles()
  tree=BVHTree.FromPolygons([tuple(land.matrix_world@v.co) for v in land.data.vertices],
       [tuple(t.vertices) for t in land.data.loop_triangles],all_triangles=True)
 for f in frames:
  started=time.monotonic();scene.frame_set(f);bpy.context.view_layer.update()
  p=out/f'frame-{f-217:04d}.png';scene.render.filepath=str(p)
  if bpy.ops.render.render(write_still=True)!={'FINISHED'} or not p.is_file():raise ValueError('Incomplete native frame')
  row={'index':f-217,'source_frame':f,'sha256':base.digest(p),'seconds':time.monotonic()-started,
       'camera':np.array(scene.camera.matrix_world).tolist(),'lens':scene.camera.data.lens,
       'pose':{n:np.array(rig.matrix_world@rig.pose.bones[n].matrix).tolist() for n in bones}}
  if tree is not None:
   eye=bpy.data.objects['MF_aimable_eye_Left'].matrix_world.translation
   target=Vector((0,-550,-9.5));delta=target-eye
   hit=tree.ray_cast(eye,delta.normalized(),delta.length)
   down=tree.ray_cast(scene.camera.matrix_world.translation,Vector((0,0,-1)),4000)
   row['geography']={'eye_to_checkpoint_land_occlusion':None if hit[0] is None else list(hit[0]),
       'eye_world':list(eye),'checkpoint_target':list(target),
       'camera_ground_clearance_native':None if down[0] is None else down[3]}
   horse=bpy.data.objects['MF185_gait_horse'];ev=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
   try:
    points=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',points)
    matrix=np.array(ev.matrix_world);points=points.reshape(-1,3)@matrix[:3,:3].T+matrix[:3,3]
    lower=points[points[:,2]<np.quantile(points[:,2],.35)];clear=[]
    for pt in lower:
     hit=tree.ray_cast(Vector(pt+[0,0,1000]),Vector((0,0,-1)),4000)
     if hit[0] is not None:clear.append((pt[2]-hit[0].z)/8.3)
    row['geography']['horse_actual_mesh_ground_min_m']=float(min(clear))
    row['geography']['horse_mesh_points_below_1cm']=int(np.sum(np.array(clear)<-.01))
    if f in (577,613,648):
     me.calc_loop_triangles();horse_tree=BVHTree.FromPolygons(points.tolist(),[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True)
     origin=scene.camera.matrix_world.translation;delta=eye-origin
     h=horse_tree.ray_cast(origin,delta.normalized(),delta.length)
     row['geography']['final_camera_to_left_eye_horse_occlusion']=None if h[0] is None else list(h[0])
   finally:ev.to_mesh_clear()
  rows.append(row);(out/'progress.json').write_text(json.dumps({'source_sha256':result['native_sha256'],'frames':rows,'complete':False},indent=2)+'\n')
  print('205 FRAME',op,f,round(row['seconds'],2),flush=True)
 base.check_protected()
 (out/'result.json').write_text(json.dumps({'source_sha256':result['native_sha256'],'frames':rows,'fingerprint':structure,
  'fps':24,'resolution':[288,512],'samples':8,'visual_gate':'NOT_RUN','limits':'Native chronological choreography preview; not final motion-dependent finishing or release resolution'},indent=2)+'\n')


if __name__=='__main__':main()
