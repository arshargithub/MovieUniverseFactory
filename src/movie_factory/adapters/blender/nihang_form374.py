"""Fixed read-only horse form export on the accepted motion source; no recipe code."""
import json,hashlib,importlib.util
from pathlib import Path
import numpy as np

def mod(name):
 s=importlib.util.spec_from_file_location('form374_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def validate(edit):
 if edit!={'kind':'mounted_horseform374_inspect','target':'horse'}:raise ValueError('FORM374_INSPECT_FIELDS')
 return edit

def run(bpy,out,edit):
 validate(edit);scene=mod('nihang_support').select_production_scene(bpy);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];saved=scene.frame_current
 original=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy);data=horse.data;keys=data.shape_keys.key_blocks
 base=np.empty(len(data.vertices)*3,dtype=np.float32);data.vertices.foreach_get('co',base);base=base.reshape(-1,3)
 shape=np.array([[v.co[:] for v in key.data] for key in keys],dtype=np.float32)
 names=[g.name for g in horse.vertex_groups];weights=np.zeros((len(base),len(names)),dtype=np.float32)
 for v in data.vertices:
  for g in v.groups:weights[v.index,g.group]=g.weight
 edges=np.array([e.vertices[:] for e in data.edges],dtype=np.int32);data.calc_loop_triangles();triangles=np.array([t.vertices[:] for t in data.loop_triangles],dtype=np.int32)
 arrays=dict(mesh=base,shape=shape,shape_names=np.array([k.name for k in keys]),weights=weights,group_names=np.array(names),edges=edges,triangles=triangles);records=[]
 levels=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF']
 try:
  for m,_ in levels:m.show_viewport=False
  for f in (283,333,339,346,367):
   scene.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=horse.evaluated_get(dg);mesh=ev.to_mesh()
   try:
    if len(mesh.vertices)!=len(base):raise ValueError('FORM374_POSED_CAGE_INDEX')
    co=np.empty(len(base)*3,dtype=np.float32);mesh.vertices.foreach_get('co',co);arrays['posed_'+str(f)]=co.reshape(-1,3)
    records.append(dict(frame=f,horse_world=[list(x) for x in horse.matrix_world],rig_world=[list(x) for x in rig.matrix_world],shape_values={k.name:k.value for k in keys}))
   finally:ev.to_mesh_clear()
 finally:
  for m,v in levels:m.show_viewport=v
  scene.frame_set(saved);bpy.context.view_layer.update()
 if original!=mod('nihang_prep367').frozen(bpy) or actions!=mod('nihang_padsolve370').actions(bpy):raise ValueError('FORM374_READONLY_DRIFT')
 dest=out/'horse-form374.npz';np.savez_compressed(dest,**arrays)
 report=dict(vertices=len(base),groups=names,shape_names=[k.name for k in keys],basis_mesh_discrepancy=float(np.max(np.linalg.norm(base-shape[0],axis=1))),bounds=[shape[0].min(0).tolist(),shape[0].max(0).tolist()],modifiers=[dict(name=m.name,type=m.type,render=m.show_render,viewport=m.show_viewport,preserve_volume=getattr(m,'use_deform_preserve_volume',None)) for m in horse.modifiers],custom_properties={k:v for k,v in horse.items() if isinstance(v,(str,int,float,bool))},poses=records,npz=dict(file=dest.name,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),geometry_unchanged=True,actions_unchanged=True,scope='Actualrest/shape/weights/topologyandarmature-posedcageexport, subdivisiontemporarilydisabledandrestored; no render-surface/anatomical/AVapproval.')
 (out/'horse-form374.json').write_text(json.dumps(report,indent=2)+'\n');return dict(report='horse-form374.json',npz='horse-form374.npz',geometry_unchanged=True,actions_unchanged=True)
