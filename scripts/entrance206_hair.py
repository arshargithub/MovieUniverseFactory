"""Root-pinned damped guide dynamics, cached into existing native hair graphs.

This is a bounded guide simulation with rest-shape/length constraints, not a
general hair/cloth collision solver. Actual contact still requires visual QA.
"""
import numpy as np
from entrance205_motion import smooth

def topology(rest,offsets):
 a=[];b=[];mob=np.zeros(len(rest));phase=np.zeros(len(rest))
 for j,(lo,hi) in enumerate(zip(offsets[:-1],offsets[1:])):
  lo,hi=int(lo),int(hi);length=np.linalg.norm(np.diff(rest[lo:hi],axis=0),axis=1);arc=np.r_[0,np.cumsum(length)];u=arc/max(arc[-1],1e-9)
  # Preserve covered crown and first two root samples exactly. Free only the
  # falling lengths. The accepted hairstyle, part and scalp are not remodeled.
  mob[lo:hi]=smooth((u-.12)/.70)*smooth((15.62-rest[lo:hi,2])/.9)*smooth((.25-rest[lo:hi,1])/.6);mob[lo:lo+2]=0
  phase[lo:hi]=(j*.61803398875%1)*np.pi*2
  a.extend(range(lo,hi-1));b.extend(range(lo+1,hi))
 a=np.array(a);b=np.array(b);return a,b,np.linalg.norm(rest[b]-rest[a],axis=1),mob,phase

def simulate(rest,offsets,wind,inertia,initial=None,phase_start=0,contact=None):
 a,b,length,mob,phase=topology(rest,offsets);p=rest.copy() if initial is None else initial[0].copy();v=np.zeros_like(p) if initial is None else initial[1].copy();rows=[];metrics=[]
 dt=1/96;den=mob[a]+mob[b];pin=mob==0
 for i,(w,acc) in enumerate(zip(wind,inertia)):
  for s in range(4):
   t=(i*4+s+phase_start*4)*dt
   flutter=np.column_stack((np.sin(8.7*t+phase),.55*np.sin(6.1*t+phase*.3),.4*np.sin(10.4*t+phase)))
   force=(w[None,:]*44-acc[None,:]*.16+flutter*11)*mob[:,None]-64*(p-rest)
   old=p.copy();v=(v+force*dt)*np.exp(-6.5*dt);p+=v*dt;p[pin]=rest[pin]
   for _ in range(12):
    d=p[b]-p[a];l=np.maximum(np.linalg.norm(d,axis=1),1e-9);c=d*((l-length)/l/np.maximum(den,1e-9))[:,None]
    change=np.zeros_like(p);np.add.at(change,a,c*mob[a,None]);np.add.at(change,b,-c*mob[b,None]);p+=change*.48;p[pin]=rest[pin]
   v=(p-old)/dt
  if contact is not None:
   before_contact=p.copy();p=contact(i,p);p[pin]=rest[pin]
   # Coherent covering restraint dissipates motion; do not inject an inward
   # velocity impulse by treating its rest-shape attenuation as a rebound.
   attenuation=np.clip(np.linalg.norm(p-rest,axis=1)/np.maximum(np.linalg.norm(before_contact-rest,axis=1),1e-9),0,1)
   v*=attenuation[:,None]
  if not np.isfinite(p).all():raise ValueError('Nonfinite guide simulation')
  rows.append(p.astype(np.float32));metrics.append([np.max(np.linalg.norm(p-rest,axis=1)),np.max(abs(np.linalg.norm(p[b]-p[a],axis=1)-length)),np.max(abs(p[pin]-rest[pin]))])
 return np.array(rows),np.array(metrics),(p,v)

def cloth_guard(scene,ob,rest,offsets,frames,matrices):
 """Keep guide displacement on its original side of the current shawl sheet.

 Roots/crown/rear are restrained by the covering; exposed lengths are dynamic.
 This is one-way contact against the actual cached garment, not two-way cloth.
 """
 import bpy
 from mathutils import Vector
 from mathutils.bvhtree import BVHTree
 from wardrobe_motion178_controls import render_geometry_paused
 from entrance189_groom import read_mdd
 shawl=bpy.data.objects['MF185_moving_shawl'];m=next(m for m in shawl.modifiers if m.type=='MESH_CACHE');cache=read_mdd(bpy.path.abspath(m.filepath));start=int(m.frame_start);shawl.data.calc_loop_triangles();tris=[tuple(t.vertices) for t in shawl.data.loop_triangles];transforms=[]
 with render_geometry_paused():
  for f in frames:
   scene.frame_set(f);bpy.context.view_layer.update();transforms.append(np.array(shawl.parent.matrix_world@shawl.matrix_parent_inverse@shawl.matrix_basis if shawl.parent else shawl.matrix_world))
 counts=[];last=[None,None]
 def collide(i,p):
  if last[0]!=i:
   matrix=np.linalg.inv(matrices[i])@transforms[i];q=np.asarray(cache[frames[i]-start]);q=q@matrix[:3,:3].T+matrix[:3,3];last[:]=[i,BVHTree.FromPolygons(q.tolist(),tris,all_triangles=True)]
  tree=last[1];delta=p-rest;length=np.linalg.norm(delta,axis=1);ratios=np.ones(len(p));count=0
  for j in np.flatnonzero(length>.01):
   hit=tree.ray_cast(Vector(rest[j]),Vector(delta[j]/length[j]),float(length[j]+.04))
   if hit[0] is not None:ratios[j]=min(1.,max(0.,hit[3]-.04)/length[j]);count+=1
  # Contact restrains a guide as a coherent strand. Pointwise projection
  # introduced a measured0.67-unit edge kink and is explicitly rejected.
  alpha=np.repeat(np.minimum.reduceat(ratios,offsets[:-1]),np.diff(offsets))
  counts.append(count);return rest+delta*alpha[:,None]
 return collide,counts

def install(scene,out,kind):
 import bpy
 from wardrobe_motion178_controls import render_geometry_paused
 from entrance189_groom import write_mdd,attach_cache
 frames=list(range(217,361)) if kind=='opening' else list(range(361,649));records=[]
 for ob in [o for o in scene.objects if o.type=='CURVES' and o.name.startswith('MF_natural147_hair_long hair')]:
  rest=np.empty((len(ob.data.points),3),np.float64);ob.data.attributes['position'].data.foreach_get('vector',rest.ravel());offsets=np.array([c.first_point_index for c in ob.data.curves]+[len(rest)])
  matrices=[]
  with render_geometry_paused():
   for f in frames:
    scene.frame_set(f);bpy.context.view_layer.update();matrices.append(np.array(ob.parent.matrix_world@ob.matrix_parent_inverse@ob.matrix_basis))
  matrices=np.array(matrices);rig=bpy.data.objects['MF_body156_fit_rig'];heads=[];wind=[]
  with render_geometry_paused():
   for i,f in enumerate(frames):
    scene.frame_set(f);bpy.context.view_layer.update();heads.append(np.array((rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation))
    if kind=='route':
     from entrance205_motion import sample
     y=sample((f-361)/24)['heading'];world=np.array([-np.sin(y),np.cos(y),.03])
    else:world=np.array([0.,1.,.03])
    rot=matrices[i,:3,:3];w=np.linalg.solve(rot,world);wind.append(w/np.linalg.norm(w))
  acc=np.gradient(np.gradient(np.array(heads),axis=0)*24,axis=0)*24
  # Bound the source acceleration around cut boundaries; no impulsive groom
  # change caused by a shot cut. Native positional gusts remain continuous.
  local=np.array([np.linalg.solve(m[:3,:3],a) for m,a in zip(matrices,acc)]);local=np.clip(local,-60,60)
  # Warm-up under constant wind avoids an artificial wind-on event at217.
  label='main' if ob.name.endswith('main') else 'strands'
  continuity=None
  if kind=='opening':
   _,_,state=simulate(rest,offsets,np.tile(wind[0],(72,1)),np.zeros((72,3)),phase_start=-72)
  else:
   import wardrobe_motion178 as base
   state_path=base.BASE/'entrance206-opening20'/f'hair-{label}-state.npz'
   expected={'main':'ab18bd0139cb073b39f900d7add5e2ee3d2114df63fb511417605338fba13e91','strands':'1309a3a6efc152e128328f4f2ff4452a1c4c440be347f4e6877368cd4ef679c9'}[label]
   if base.digest(state_path)!=expected:raise ValueError('Hair continuity state changed')
   continuity=dict(source=str(state_path.relative_to(base.ROOT)) if hasattr(base,'ROOT') else str(state_path),sha256=expected)
   z=np.load(state_path);state=(z['p'],z['v'])
   if not np.array_equal(rest,z['rest']):raise ValueError('Hair continuity topology mismatch')
  collide,counts=cloth_guard(scene,ob,rest,offsets,frames,matrices)
  rows,metrics,state=simulate(rest,offsets,np.array(wind),local,state,phase_start=frames[0]-217,contact=collide)
  np.savez_compressed(out/f'hair-{label}-state.npz',p=state[0],v=state[1],rest=rest)
  path=out/f'hair-{label}.mdd';write_mdd(path,len(rows),len(rest),iter(rows))
  mesh=bpy.data.meshes.new('206 '+label+' cached guide points');mesh.from_pydata(rest.tolist(),[],[]);mesh.update();proxy=bpy.data.objects.new('MF206_'+label+'_guide_dynamics',mesh);scene.collection.objects.link(proxy)
  proxy.parent=ob.parent;proxy.matrix_parent_inverse=ob.matrix_parent_inverse.copy();proxy.matrix_basis=ob.matrix_basis.copy();proxy.hide_render=True;proxy.display_type='WIRE';attach_cache(proxy,path,frames[0])
  group=bpy.data.node_groups.new('206 '+label+' cached guide motion','GeometryNodeTree');group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
  n,l=group.nodes,group.links;inp=n.new('NodeGroupInput');output=n.new('NodeGroupOutput');info=n.new('GeometryNodeObjectInfo');info.transform_space='RELATIVE';info.inputs['Object'].default_value=proxy
  pos=n.new('GeometryNodeInputPosition');idx=n.new('GeometryNodeInputIndex');sample=n.new('GeometryNodeSampleIndex');sample.data_type='FLOAT_VECTOR';sample.domain='POINT';l.new(info.outputs['Geometry'],sample.inputs['Geometry']);l.new(pos.outputs[0],sample.inputs['Value']);l.new(idx.outputs[0],sample.inputs['Index'])
  setpos=n.new('GeometryNodeSetPosition');l.new(inp.outputs['Geometry'],setpos.inputs['Geometry']);l.new(sample.outputs['Value'],setpos.inputs['Position']);l.new(setpos.outputs['Geometry'],output.inputs['Geometry'])
  mod=ob.modifiers.new('206 root-pinned guide simulation','NODES');mod.node_group=group;bpy.context.view_layer.objects.active=ob
  while list(ob.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
  np.savez_compressed(out/f'hair-{label}-metrics.npz',frames=frames,metrics=metrics,rest=rest,offsets=offsets,matrices=matrices,wind=wind,inertia=local)
  records.append(dict(object=ob.name,points=len(rest),maximum_tip_displacement_native=float(metrics[:,0].max()),maximum_edge_length_error_native=float(metrics[:,1].max()),root_error=float(metrics[:,2].max()),method='96Hz damped rest-shape springs plus12 length projections/substep; covered crown/roots/rear restrained; wind/inertia from source support; swept-rest one-way contact against current shawl sheet',continuity_source=continuity,contact_corrections=sum(counts),contact_gate='NOT_RUN'))
 return records
