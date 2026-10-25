"""Bounded positive horse torso sculpt; proposed trusted handler, not executed yet."""
import json,hashlib,importlib.util
from pathlib import Path
import numpy as np

def mod(name):
 s=importlib.util.spec_from_file_location('sculpt374_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def smooth(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)

def validate(edit):
 if edit.get('kind')=='mounted_horseform374_contact':
  if set(edit)!={'kind','target','frames'} or edit['target']!='horse':raise ValueError('FORM374_CONTACT_FIELDS')
  fs=edit['frames']
  if not isinstance(fs,list) or not 1<=len(fs)<=16 or any(type(f) is not int or not 276<=f<=367 for f in fs) or len(set(fs))!=len(fs):raise ValueError('FORM374_CONTACT_FRAMES')
  return edit
 if set(edit)!={'kind','target','strength'} or edit['kind']!='mounted_horseform374_sculpt' or edit['target']!='horse':raise ValueError('FORM374_SCULPT_FIELDS')
 if type(edit['strength']) not in (float,int) or not np.isfinite(edit['strength']) or not .25<=edit['strength']<=1.25:raise ValueError('FORM374_STRENGTH')
 return edit

def form_delta(points,breast,limb,strength):
 """Local broad sculpt strokes following positive pectoral/shoulder anatomy.

 No Laplacian, shrinkwrap target, bone scaling or projection/shelf. The field
 vanishes outside anterior torso and in strongly limb-owned vertices. Low
 sternum tapers instead of recreating the old pendant lower breast.
 """
 p=np.asarray(points,dtype=float);b=np.asarray(breast,dtype=float);l=np.asarray(limb,dtype=float)
 if p.ndim!=2 or p.shape[1]!=3 or len(b)!=len(p) or len(l)!=len(p) or not np.isfinite(p).all():raise ValueError('FORM374_ARRAY')
 x,y,z=p.T;w=smooth((z-1.06)/.17)*smooth((1.76-z)/.18)*smooth((-.24-y)/.38)*smooth(b/.55)*(1-smooth((l-.25)/.5))
 # Two broad upper pectoral continuities into shoulder, not isolated balls.
 paired=np.exp(-((np.abs(x)-.135)/.145)**2-((z-1.40)/.20)**2)
 central=np.exp(-(x/.13)**2-((z-1.31)/.22)**2)
 upper=np.exp(-((np.abs(x)-.22)/.13)**2-((z-1.48)/.18)**2)
 d=np.zeros_like(p);d[:,1]=-(.020*paired+.030*central)*w*strength
 d[:,0]=np.sign(x)*.012*upper*w*strength
 # A very shallow midline channel reveals connected anatomy without cleavage.
 d[:,1]+=.002*np.exp(-(x/.028)**2-((z-1.43)/.15)**2)*w*strength
 if not np.isfinite(d).all() or np.max(np.linalg.norm(d,axis=1))>.075:raise ValueError('FORM374_SCULPT_BOUND')
 return d

def influence_bound(delta,edges):
 bound=np.linalg.norm(np.asarray(delta),axis=1)
 for _ in range(2):
  old=bound.copy();np.maximum.at(bound,edges[:,0],old[edges[:,1]]);np.maximum.at(bound,edges[:,1],old[edges[:,0]])
 return bound

def audit_contact(bpy,out,frames):
 """Same actual-final-surface vertex/centroid test used in padsolve370.

 Integer-frame sampled qualification only, not continuous collision/physics.
 """
 from mathutils.bvhtree import BVHTree
 from mathutils import Vector
 scene=mod('nihang_support').select_production_scene(bpy);horse=bpy.data.objects['horse'];saved=scene.frame_current;before=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy)
 levels=[(m,m.levels,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF'];rows=[]
 caches=[bpy.data.objects[n] for n in ['370 contact-solved saddle cloth','371 apex contact-solved saddle cloth','373 landing contact-solved saddle cloth']]
 try:
  for m,_,_ in levels:m.levels=m.render_levels;m.show_viewport=True
  for frame in frames:
   scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=horse.evaluated_get(dg);mesh=ev.to_mesh()
   try:tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[tuple(q.vertices) for q in mesh.polygons])
   finally:ev.to_mesh_clear()
   active=[o for o in caches if not o.hide_render]
   if len(active)!=1:raise ValueError('FORM374_CACHE_OWNERSHIP:'+str((frame,[o.name for o in active])))
   ob=active[0];oe=ob.evaluated_get(dg);me=oe.to_mesh()
   try:
    me.calc_loop_triangles();vs=[oe.matrix_world@v.co for v in me.vertices];probes=vs+[sum((vs[i] for i in tri.vertices),Vector())/3 for tri in me.loop_triangles];gaps=[]
    for point in probes:
     q,n,face,distance=tree.find_nearest(point)
     if q is None:raise ValueError('FORM374_FINAL_SURFACE_MISSING')
     gaps.append(float((point-q).dot(n)))
    row=dict(frame=frame,cache=ob.name,samples=len(gaps),minimum_signed_gap=min(gaps),below_minus_1mm=sum(g<-.001 for g in gaps));rows.append(row)
    (out/'horse-contact374.json').write_text(json.dumps(dict(rows=rows,complete=False,scope='Actual final-surface vertex/triangle-centroid sampling; integer frames only.'),indent=2)+'\n')
    if min(gaps)<.002-1e-6:raise ValueError('FORM374_FINAL_SURFACE_CONTACT:'+str((frame,min(gaps))))
   finally:oe.to_mesh_clear()
 finally:
  for m,level,visible in levels:m.levels=level;m.show_viewport=visible
  scene.frame_set(saved);bpy.context.view_layer.update()
 if before!=mod('nihang_prep367').frozen(bpy) or actions!=mod('nihang_padsolve370').actions(bpy):raise ValueError('FORM374_CONTACT_READONLY_DRIFT')
 report=dict(rows=rows,complete=True,minimum_signed_gap=min(x['minimum_signed_gap'] for x in rows),geometry_actions_unchanged=True,scope='Reused padsolve370 actual final-surface vertex/triangle-centroid sampling,2mm floor with1micrometre numeric tolerance; integer frames only, rendered and subframe judgment separate.')
 (out/'horse-contact374.json').write_text(json.dumps(report,indent=2)+'\n');return report

def run(bpy,out,edit):
 validate(edit)
 if edit['kind']=='mounted_horseform374_contact':return audit_contact(bpy,out,edit['frames'])
 from mathutils import Vector
 from mathutils.kdtree import KDTree
 horse=bpy.data.objects['horse'];nap=bpy.data.objects.get('317 rig-bound short horse nap');scene=mod('nihang_support').select_production_scene(bpy)
 if horse.get('form374'):raise ValueError('FORM374_REAPPLY')
 actions=mod('nihang_padsolve370').actions(bpy);before=mod('nihang_prep367').frozen(bpy);keys=horse.data.shape_keys.key_blocks;p=np.array([v.co[:] for v in keys[0].data]);rows=[{horse.vertex_groups[g.group].name:g.weight for g in v.groups} for v in horse.data.vertices]
 breast=np.array([sum(w for n,w in row.items() if n.startswith('DEF-breast.')) for row in rows]);limb=np.array([sum(w for n,w in row.items() if n.startswith(('DEF-upper_arm.','DEF-forearm.','DEF-shoulder.'))) for row in rows]);delta=form_delta(p,breast,limb,edit['strength'])
 # Establish cloth-owned surface exclusion from the actual accepted source,
 # before moving the skin. This is not a relaxed post-hoc clearance threshold.
 from mathutils.bvhtree import BVHTree
 ids_set=set(np.flatnonzero(np.linalg.norm(delta,axis=1)>1e-8).tolist());edge_array=np.array([e.vertices[:] for e in horse.data.edges])
 for _ in range(2):ids_set.update(edge_array[np.isin(edge_array[:,0],list(ids_set))|np.isin(edge_array[:,1],list(ids_set))].ravel().tolist())
 ids0=sorted(ids_set);minimum=np.full(len(p),np.inf);saved0=scene.frame_current;levels0=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF']
 caches0=[bpy.data.objects[n] for n in ['370 contact-solved saddle cloth','371 apex contact-solved saddle cloth','373 landing contact-solved saddle cloth']]
 try:
  for modifier,_ in levels0:modifier.show_viewport=False
  for frame in (283,333,339,346,367):
   scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=horse.evaluated_get(dg);mesh=ev.to_mesh()
   try:points=[ev.matrix_world@mesh.vertices[i].co for i in ids0]
   finally:ev.to_mesh_clear()
   for ob in caches0:
    if ob.hide_render:continue
    obj=ob.evaluated_get(dg);me=obj.to_mesh()
    try:
     tree=BVHTree.FromPolygons([obj.matrix_world@v.co for v in me.vertices],[tuple(q.vertices) for q in me.polygons],all_triangles=False)
     for idx,point in zip(ids0,points):minimum[idx]=min(minimum[idx],tree.find_nearest(point)[3])
    finally:obj.to_mesh_clear()
 finally:
  for modifier,value in levels0:modifier.show_viewport=value
  scene.frame_set(saved0);bpy.context.view_layer.update()
 for _ in range(2):
  old=minimum.copy();np.minimum.at(minimum,edge_array[:,0],old[edge_array[:,1]]);np.minimum.at(minimum,edge_array[:,1],old[edge_array[:,0]])
 delta*=smooth((minimum-.065)/.085)[:,None]
 if np.count_nonzero(np.linalg.norm(delta,axis=1)>1e-8)<50:raise ValueError('FORM374_EMPTY_SCULPT')
 key_deltas=[np.array([v.co[:] for v in k.data])-p for k in keys]
 for k in keys:
  co=np.empty(len(k.data)*3,dtype=np.float32);k.data.foreach_get('co',co);k.data.foreach_set('co',(co.reshape(-1,3)+delta).ravel())
 # Remove the known historical raw/Basis discrepancy without reverting shape.
 horse.data.vertices.foreach_set('co',(p+delta).astype(np.float32).ravel())
 if nap is None or nap.type!='MESH':raise ValueError('FORM374_NAP_MISSING')
 kd=KDTree(len(p))
 for i,q in enumerate(p):kd.insert(Vector(q),i)
 kd.balance();mx=horse.matrix_world.inverted()@nap.matrix_world;inv=mx.inverted().to_3x3();nap_changed=0
 for v in nap.data.vertices:
  _,i,_=kd.find(mx@v.co)
  if np.linalg.norm(delta[i])>1e-8:v.co+=inv@Vector(delta[i]);nap_changed+=1
 horse.data.update();nap.data.update();bpy.context.view_layer.update();after=mod('nihang_prep367').frozen(bpy)
 changed=[n for n in before if before[n]!=after[n]]
 if set(changed)-{horse.name,nap.name} or actions!=mod('nihang_padsolve370').actions(bpy):raise ValueError('FORM374_OUTSIDE_SCOPE')
 newp=np.array([v.co[:] for v in keys[0].data]);error=max(float(np.max(np.abs((np.array([v.co[:] for v in k.data])-newp)-old))) for k,old in zip(keys,key_deltas))
 if error>3e-7 or np.any(delta[p[:,1]>-.24]):raise ValueError('FORM374_CORRECTIVE_OR_BACK_DRIFT')
 contact=audit_contact(bpy,out,[283,333,339,346,367])
 horse['form374']=json.dumps(dict(strength=edit['strength'],method='bounded positive upper-pectoral/shoulder sculpt',source_basis=hashlib.sha256(p.astype('<f4').tobytes()).hexdigest()))
 np.savez_compressed(out/'horse-sculpt374.npz',before=p,delta=delta,after=newp)
 report=dict(changed_meshes=changed,changed_vertices=int((np.linalg.norm(delta,axis=1)>1e-8).sum()),maximum_delta=float(np.max(np.linalg.norm(delta,axis=1))),nap_changed=nap_changed,corrective_relative_error=error,actions_unchanged=True,weights_unchanged=True,back_and_seat_delta=0,critical_final_surface_contact=contact,guard='Actual final-surface signed-gap sampling from padsolve370, not cage proxy.',scope='Candidate only; all matched posed views, complete action surface/interface controls and Director acceptance remain separate. Raw mesh synchronized to actual Basis; relative corrective shapes retained.')
 (out/'horse-sculpt374.json').write_text(json.dumps(report,indent=2)+'\n');return report
