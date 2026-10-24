"""Fixed localized lower pectoral volume correction, source shape/rig retained."""
import json
import numpy as np

def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def displacement(points,breast,limb):
 p=np.asarray(points,dtype=float);b=np.asarray(breast);l=np.asarray(limb)
 domain=smooth((p[:,2]-.90)/.15)*smooth((1.48-p[:,2])/.27)*smooth((-.40-p[:,1])/.25)*smooth(b/.6)*(1-smooth(l/.65))
 d=np.zeros_like(p);d[:,2]=.12*domain;d[:,0]=-.15*p[:,0]*domain;d[:,1]=.025*domain
 if not np.isfinite(d).all() or np.max(np.linalg.norm(d,axis=1))>.14:raise ValueError('CHEST363_FIELD_BOUND')
 return d
def run(bpy,out):
 from mathutils import Vector
 from mathutils.kdtree import KDTree
 horse=bpy.data.objects['horse']
 if horse.get('pectoral363'):raise ValueError('CHEST363_REAPPLY')
 p=np.array([v.co[:] for v in horse.data.vertices]);rows=[{horse.vertex_groups[g.group].name:g.weight for g in v.groups} for v in horse.data.vertices];b=np.array([sum(w for n,w in r.items() if n.startswith('DEF-breast.')) for r in rows]);l=np.array([sum(w for n,w in r.items() if n.startswith(('DEF-upper_arm.','DEF-forearm.','DEF-shoulder.'))) for r in rows]);d=displacement(p,b,l)
 for key in horse.data.shape_keys.key_blocks:
  co=np.empty(len(key.data)*3,dtype=np.float32);key.data.foreach_get('co',co);key.data.foreach_set('co',(co.reshape(-1,3)+d).ravel())
 nap=bpy.data.objects.get('317 rig-bound short horse nap');nap_count=0
 if nap and nap.type=='MESH':
  kd=KDTree(len(p))
  for i,q in enumerate(p):kd.insert(Vector(q),i)
  kd.balance();mx=horse.matrix_world.inverted()@nap.matrix_world;inv=mx.inverted().to_3x3()
  for v in nap.data.vertices:
   _,i,_=kd.find(mx@v.co);v.co+=inv@Vector(d[i]);nap_count+=1
 horse['pectoral363']=1;bpy.context.view_layer.update();report=dict(vertices=int((np.linalg.norm(d,axis=1)>1e-8).sum()),maximum_delta=float(np.max(np.linalg.norm(d,axis=1))),nap_vertices=nap_count,method='Smooth lower-pectoral lift and transverse narrowing; explicit limb-weight exclusion, same delta to all shape blocks and bound nap.',scope='Candidate only; actual standing/front/rearing and side must reject pinching, flat cuts or foreleg regression. Bones, weights and actions unchanged.')
 (out/'chest363.json').write_text(json.dumps(report,indent=2)+'\n');return report
