"""Fixed topology-aware pectoral fairing, actual Basis and limb anchors."""
import json
import numpy as np

def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def fair_delta(points,edges,breast,limb,iterations=100):
 p=np.asarray(points,dtype=float);e=np.asarray(edges,dtype=int);b=np.asarray(breast);l=np.asarray(limb)
 if p.ndim!=2 or p.shape[1]!=3 or e.ndim!=2 or e.shape[1]!=2 or e.min()<0 or e.max()>=len(p):raise ValueError('CHEST363_TOPOLOGY')
 spatial=smooth((p[:,2]-.87)/.20)*smooth((1.70-p[:,2])/.22)*smooth((-.18-p[:,1])/.30)
 fixed=(l>.65)|(spatial==0);weight=smooth(b/.55)*spatial;weight[fixed]=0
 count=np.zeros(len(p));np.add.at(count,e[:,0],1);np.add.at(count,e[:,1],1)
 def average(v):
  total=np.zeros_like(v);np.add.at(total,e[:,0],v[e[:,1]]);np.add.at(total,e[:,1],v[e[:,0]]);return total/np.maximum(count,1).reshape((-1,)+(1,)*(v.ndim-1))
 for _ in range(8):weight=.6*weight+.4*average(weight);weight[fixed]=0
 q=p.copy()
 for _ in range(iterations):q+=(average(q)-q)*weight[:,None]*.55
 delta=q-p;length=np.linalg.norm(delta,axis=1);scale=np.ones(len(p));mask=length>1e-10;scale[mask]=.11*np.tanh(length[mask]/.11)/length[mask];delta*=scale[:,None];delta[fixed]=0
 if not np.isfinite(delta).all() or np.max(np.linalg.norm(delta,axis=1))>.110001:raise ValueError('CHEST363_FAIR_BOUND')
 return delta
def run(bpy,out):
 from mathutils import Vector
 from mathutils.kdtree import KDTree
 horse=bpy.data.objects['horse']
 if horse.get('pectoral363'):raise ValueError('CHEST363_REAPPLY')
 keys=horse.data.shape_keys.key_blocks;p=np.array([v.co[:] for v in keys[0].data]);raw=np.array([v.co[:] for v in horse.data.vertices]);rows=[{horse.vertex_groups[g.group].name:g.weight for g in v.groups} for v in horse.data.vertices]
 b=np.array([sum(w for n,w in r.items() if n.startswith('DEF-breast.')) for r in rows]);l=np.array([sum(w for n,w in r.items() if n.startswith(('DEF-upper_arm.','DEF-forearm.','DEF-shoulder.'))) for r in rows]);d=fair_delta(p,[tuple(e.vertices) for e in horse.data.edges],b,l)
 for key in keys:
  co=np.empty(len(key.data)*3,dtype=np.float32);key.data.foreach_get('co',co);key.data.foreach_set('co',(co.reshape(-1,3)+d).ravel())
 nap=bpy.data.objects.get('317 rig-bound short horse nap');nap_count=0
 if nap and nap.type=='MESH':
  kd=KDTree(len(p))
  for i,q in enumerate(p):kd.insert(Vector(q),i)
  kd.balance();mx=horse.matrix_world.inverted()@nap.matrix_world;inv=mx.inverted().to_3x3()
  for v in nap.data.vertices:
   _,i,_=kd.find(mx@v.co);v.co+=inv@Vector(d[i]);nap_count+=1
 horse['pectoral363']=1;bpy.context.view_layer.update();report=dict(vertices=int((np.linalg.norm(d,axis=1)>1e-8).sum()),maximum_delta=float(np.max(np.linalg.norm(d,axis=1))),basis_mesh_discrepancy=float(np.max(np.linalg.norm(p-raw,axis=1))),nap_vertices=nap_count,method='Topology-aware constrained pectoral fairing on actual Basis,100 local smooth-brush iterations with diffused falloff and fixed limb anchors. No prescribed height shelf.',scope='Candidate only; actual standing/rearing/front/side veto. Bones/weights/actions retained; original110 source and failed112 field remain preserved.')
 (out/'chest363.json').write_text(json.dumps(report,indent=2)+'\n');return report
