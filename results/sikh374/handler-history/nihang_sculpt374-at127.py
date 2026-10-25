"""Bounded positive horse torso sculpt; proposed trusted handler, not executed yet."""
import json,hashlib,importlib.util
from pathlib import Path
import numpy as np

def mod(name):
 s=importlib.util.spec_from_file_location('sculpt374_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def smooth(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)

def validate(edit):
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

def run(bpy,out,edit):
 validate(edit)
 from mathutils import Vector
 from mathutils.kdtree import KDTree
 horse=bpy.data.objects['horse'];nap=bpy.data.objects.get('317 rig-bound short horse nap');scene=mod('nihang_support').select_production_scene(bpy)
 if horse.get('form374'):raise ValueError('FORM374_REAPPLY')
 actions=mod('nihang_padsolve370').actions(bpy);before=mod('nihang_prep367').frozen(bpy);keys=horse.data.shape_keys.key_blocks;p=np.array([v.co[:] for v in keys[0].data]);rows=[{horse.vertex_groups[g.group].name:g.weight for g in v.groups} for v in horse.data.vertices]
 breast=np.array([sum(w for n,w in row.items() if n.startswith('DEF-breast.')) for row in rows]);limb=np.array([sum(w for n,w in row.items() if n.startswith(('DEF-upper_arm.','DEF-forearm.','DEF-shoulder.'))) for row in rows]);delta=form_delta(p,breast,limb,edit['strength'])
 # Establish cloth-owned surface exclusion from the actual accepted source,
 # before moving the skin. This is not a relaxed post-hoc clearance threshold.
 from mathutils.bvhtree import BVHTree
 ids0=np.flatnonzero(np.linalg.norm(delta,axis=1)>1e-8).tolist();minimum=np.full(len(p),np.inf);saved0=scene.frame_current;levels0=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF']
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
 # Revalidate the torso/cache interface on every accepted frame. The source
 # caches themselves and all animation are frozen, but that alone is not proof
 # of clearance after a surface change. Cage-neighbour expansion catches the
 # subdivision support around each changed point; final rendered surfaces are
 # separately inspected in the complete pose/view matrix.
 from mathutils.bvhtree import BVHTree
 affected=set(np.flatnonzero(np.linalg.norm(delta,axis=1)>1e-8).tolist())
 edges=np.array([e.vertices[:] for e in horse.data.edges])
 for _ in range(2):
  neighbours=edges[np.isin(edges[:,0],list(affected))|np.isin(edges[:,1],list(affected))];affected.update(neighbours.ravel().tolist())
 influence=influence_bound(delta,edges);ids=sorted(affected);required=np.maximum(.002,2*influence[ids]);saved=scene.frame_current;levels=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF'];clearance=[]
 caches=[bpy.data.objects[n] for n in ['370 contact-solved saddle cloth','371 apex contact-solved saddle cloth','373 landing contact-solved saddle cloth']]
 try:
  for m,_ in levels:m.show_viewport=False
  for f in range(276,368):
   scene.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=horse.evaluated_get(dg);mesh=ev.to_mesh()
   try:points=[ev.matrix_world@mesh.vertices[i].co for i in ids]
   finally:ev.to_mesh_clear()
   distances=[]
   for ob in caches:
    if ob.hide_render:continue
    obj=ob.evaluated_get(dg);me=obj.to_mesh()
    try:
     tree=BVHTree.FromPolygons([obj.matrix_world@v.co for v in me.vertices],[tuple(q.vertices) for q in me.polygons],all_triangles=False)
     distances.append([tree.find_nearest(q)[3] for q in points])
    finally:obj.to_mesh_clear()
   if not distances:raise ValueError('FORM374_ACTIVE_CACHE_MISSING:'+str(f))
   gaps=np.min(np.asarray(distances),axis=0);gap=float(gaps.min());margin=float(np.min(gaps-required));clearance.append(dict(frame=f,changed_cage_to_cache=gap,minimum_local_influence_margin=margin))
   if margin<0:
    index=int(np.argmin(gaps-required));(out/'horse-sculpt374-failure.json').write_text(json.dumps(dict(frame=f,gap=float(gaps[index]),required=float(required[index]),vertex=ids[index],local_influence=float(influence[ids[index]]),source_contact=float(minimum[ids[index]]),scope='Post-sculpt local influence/contact guard rejected candidate; no save.'),indent=2)+'\n');raise ValueError('FORM374_TORSO_CACHE_CLEARANCE:'+str((f,gap,margin)))
 finally:
  for m,v in levels:m.show_viewport=v
  scene.frame_set(saved);bpy.context.view_layer.update()
 horse['form374']=json.dumps(dict(strength=edit['strength'],method='bounded positive upper-pectoral/shoulder sculpt',source_basis=hashlib.sha256(p.astype('<f4').tobytes()).hexdigest()))
 np.savez_compressed(out/'horse-sculpt374.npz',before=p,delta=delta,after=newp)
 report=dict(changed_meshes=changed,changed_vertices=int((np.linalg.norm(delta,axis=1)>1e-8).sum()),maximum_delta=float(np.max(np.linalg.norm(delta,axis=1))),nap_changed=nap_changed,corrective_relative_error=error,actions_unchanged=True,weights_unchanged=True,back_and_seat_delta=0,accepted_cache_clearance=clearance,minimum_changed_cage_to_cache=min(x['changed_cage_to_cache'] for x in clearance),minimum_local_influence_margin=min(x['minimum_local_influence_margin'] for x in clearance),guard='2mm source-cache floor plus twice local two-ring displacement bound; not a claim of continuous rendered-surface collision certification.',scope='Candidate only; all matched posed views, complete action surface/interface controls and Director acceptance remain separate. Raw mesh synchronized to actual Basis; relative corrective shapes retained.')
 (out/'horse-sculpt374.json').write_text(json.dumps(report,indent=2)+'\n');return report
