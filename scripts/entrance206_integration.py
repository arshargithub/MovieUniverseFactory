"""Rebind distant guard poses and cover the actual camera corridor with fixed art."""
import math
import numpy as np
import wardrobe_motion178 as base

def guard_bindings(scene):
 import bpy
 from mathutils import Matrix
 src=base.BASE/'entrance206-composition05/scene.blend'
 if base.digest(src)!='07c3f73df59bedf50a823b5683f866bf960b123ac1e2c0e7d42ea4e6b8694bf1':raise ValueError('Mounted source changed')
 targets={o.name:o for o in scene.objects if o.name.startswith(('MF206_guard0_','MF206_guard1_')) and o.type=='MESH'}
 with bpy.data.libraries.load(str(src),link=False) as (available,loaded):
  names=[n for n in available.objects if n in targets];loaded.objects=names
 if set(names)!=set(targets):raise ValueError('Guard source names mismatch')
 originals={n:o.matrix_world.copy() for n,o in zip(names,loaded.objects)}
 before={n:np.array(o.matrix_world) for n,o in targets.items()};errors=[]
 for j,(x,y,delta) in enumerate(((-24,-876,-.45),(23,-871,.4))):
  root=bpy.data.objects[f'MF206_guard{j}_stance'];T=Matrix.Translation((x,y,-20.931));root.matrix_world=T@Matrix.Rotation(delta,4,'Z')
  for n,o in targets.items():
   if not n.startswith(f'MF206_guard{j}_'):continue
   o.parent=root;o.matrix_parent_inverse=T.inverted();o.matrix_basis=originals[n]
  bpy.context.view_layer.update()
  for n,o in targets.items():
   if n.startswith(f'MF206_guard{j}_'):errors.append(float(np.max(abs(np.array(o.matrix_world)-np.array(root.matrix_world@T.inverted()@originals[n])))))
 for o in loaded.objects:bpy.data.objects.remove(o,do_unlink=True)
 if max(errors)>5e-4:raise ValueError('Mounted rigid placement mismatch')
 return dict(source_sha256=base.digest(src),objects=len(targets),maximum_binding_error=max(errors),maximum_correction=float(max(np.max(abs(before[n]-np.array(o.matrix_world))) for n,o in targets.items())),method='Restore source-world poses, bind through explicit checkpoint-anchor inverse, then rotate the complete horse/rider; no stale-parent assumption')

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
