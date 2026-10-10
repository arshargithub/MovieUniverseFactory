"""Rebind distant guard poses and cover the actual camera corridor with fixed art."""
import math
import numpy as np
import wardrobe_motion178 as base

def guard_bindings(scene):
 import bpy
 from mathutils import Matrix,Vector
 from mathutils.bvhtree import BVHTree
 src=base.BASE/'entrance206-composition05/scene.blend'
 if base.digest(src)!='07c3f73df59bedf50a823b5683f866bf960b123ac1e2c0e7d42ea4e6b8694bf1':raise ValueError('Mounted source changed')
 targets={o.name:o for o in scene.objects if o.name.startswith(('MF206_guard0_','MF206_guard1_')) and o.type=='MESH'}
 with bpy.data.libraries.load(str(src),link=False) as (available,loaded):
  names=tuple(n for n in available.objects if n in targets)
  if set(names)!=set(targets):raise ValueError('Guard source names mismatch: '+repr(sorted(set(targets)-set(names))))
  loaded.objects=list(names)
 donors=dict(zip(names,loaded.objects))
 if any(o.parent or o.animation_data or o.constraints or o.modifiers for o in donors.values()):raise ValueError('Expected static unparented source proxies')
 # Unlinked library objects have unevaluated identity matrix_world. Their
 # stored local transform is authoritative for these unparented static props.
 originals={n:o.matrix_basis.copy() for n,o in donors.items()}
 errors=[];counts=[]
 land=bpy.data.objects['AS_valley_landform'];land.data.calc_loop_triangles();tree=BVHTree.FromPolygons([tuple(land.matrix_world@v.co) for v in land.data.vertices],[tuple(t.vertices) for t in land.data.loop_triangles],all_triangles=True);placements=[]
 for j,(x,y,delta) in enumerate(((-24,-876,-.45),(23,-871,.4))):
  nx,ny=((-38,-790) if j==0 else (38,-770));hit=tree.ray_cast(Vector((nx,ny,1000)),Vector((0,0,-1)),2000)
  if hit[0] is None:raise ValueError('Guard outside terrain')
  nz=hit[0].z;placements.append(dict(guard=j,anchor=[nx,ny,nz],distance_from_route_start_m=abs(ny)/8.3))
  root=bpy.data.objects[f'MF206_guard{j}_stance'];T=Matrix.Translation((x,y,-20.932861328125 if j==0 else -20.92694091796875));placed=Matrix.Translation((nx,ny,nz));root.matrix_world=placed@Matrix.Rotation(delta,4,'Z')
  for n,o in targets.items():
   if not n.startswith(f'MF206_guard{j}_'):continue
   # These are static distant proxies. Bake the explicit source-world pose
   # instead of depending on evaluated matrices of viewport-paused children.
   M=placed@Matrix.Rotation(delta,4,'Z')@T.inverted()@originals[n]
   old=np.array([v.co[:] for v in donors[n].data.vertices]);expected=old@np.array(M)[:3,:3].T+np.array(M)[:3,3]
   o.data=donors[n].data.copy();o.data.transform(M);o.parent=None;o.matrix_world=Matrix.Identity(4);o.data.update()
   actual=np.array([v.co[:] for v in o.data.vertices]);errors.append(float(np.max(abs(actual-expected))));counts.append(len(old))
 for o in loaded.objects:bpy.data.objects.remove(o,do_unlink=True)
 if max(errors)>5e-4:raise ValueError('Mounted rigid placement mismatch')
 for j in (0,1):
  horse=targets[f'MF206_guard{j}_horse'];head=targets[f'MF206_guard{j}_head'];hv=np.array([v.co[:] for v in horse.data.vertices]);dv=np.array([v.co[:] for v in head.data.vertices])
  if np.linalg.norm(hv.mean(0)[:2]-dv.mean(0)[:2])>10 or not 3<dv.mean(0)[2]-hv.mean(0)[2]<22:raise ValueError('Rider not seated above actual horse')
 return dict(source_sha256=base.digest(src),objects=len(targets),vertices=sum(counts),maximum_binding_error=max(errors),placements=placements,method='Bake stored source-local transforms and terrain-grounded anchor rotation into static distant meshes; separate mounted silhouettes from gateposts, no anatomy scaling')

def matte(scene):
 import bpy
 from entrance205_scene import FLOOR
 records=[]
 for name,a0,a1 in (('MF188_distant_art_arc',-154,140),('MF205_fixed_reverse_matte',140,206)):
  ob=bpy.data.objects[name]
  if ob.parent or np.max(abs(np.array(ob.matrix_world)-np.eye(4)))>1e-5:raise ValueError('Expected fixed world matte')
  ob.data=ob.data.copy();count=len(ob.data.vertices)//2
  for i in range(count):
   a=math.radians(a0+(a1-a0)*i/(count-1))
   for j in (0,1):ob.data.vertices[2*i+j].co.x=math.cos(a)*8000;ob.data.vertices[2*i+j].co.y=math.sin(a)*8000
  ob.data.update();records.append(dict(object=name,azimuth=[a0,a1],vertices=len(ob.data.vertices)))
 return dict(panels=records,reason='Required camera corner rays span about-146.5..127.7deg; put both artwork joins outside that corridor with translation margin',change='Existing primary painting carries the required corridor; fixed world meshes, unchanged image/UV/vertical scale and materials; alternate painting retained in unused sector',visual_gate='NOT_RUN')
