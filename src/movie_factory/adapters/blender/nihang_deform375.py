"""Read-only actual horse skin ownership and evaluated bone-frame inspection."""
import hashlib,json,importlib.util
from pathlib import Path
import numpy as np

def mod(name):
 s=importlib.util.spec_from_file_location('deform375_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def validate(edit):
 if edit!={'kind':'mounted_horse_deform375_inspect','target':'horse'}:raise ValueError('DEFORM375_INSPECT_FIELDS')
 return edit

def run(bpy,out,edit):
 validate(edit);scene=mod('nihang_support').select_production_scene(bpy);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];saved=scene.frame_current;geometry=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy)
 bones=list(rig.data.bones);names=[b.name for b in bones];arrays=dict(names=np.array(names),rest=np.array([np.array(b.matrix_local) for b in bones]),deform=np.array([b.use_deform for b in bones]),parents=np.array([names.index(b.parent.name) if b.parent else -1 for b in bones]),segments=np.array([b.bbone_segments for b in bones]));records=[]
 try:
  for frame in (283,333,339,346,367):
   scene.frame_set(frame);bpy.context.view_layer.update();arrays['pose_'+str(frame)]=np.array([np.array(rig.pose.bones[n].matrix) for n in names]);arrays['horse_world_'+str(frame)]=np.array(horse.matrix_world);arrays['rig_world_'+str(frame)]=np.array(rig.matrix_world)
   records.append(dict(frame=frame,shape_values={k.name:k.value for k in horse.data.shape_keys.key_blocks},selected={n:dict(parent=rig.data.bones[n].parent.name if rig.data.bones[n].parent else None,rest_head=list(rig.data.bones[n].head_local),rest_tail=list(rig.data.bones[n].tail_local),head=list(rig.pose.bones[n].head),tail=list(rig.pose.bones[n].tail),scale=list(rig.pose.bones[n].scale),segments=rig.data.bones[n].bbone_segments,constraints=[dict(name=c.name,type=c.type,influence=c.influence,target=getattr(getattr(c,'target',None),'name',None),subtarget=getattr(c,'subtarget',None)) for c in rig.pose.bones[n].constraints]) for n in names if n.startswith(('DEF-breast.','DEF-shoulder.','DEF-neck.001','DEF-spine.006','breast.','shoulder.'))}))
 finally:scene.frame_set(saved);bpy.context.view_layer.update()
 if geometry!=mod('nihang_prep367').frozen(bpy) or actions!=mod('nihang_padsolve370').actions(bpy):raise ValueError('DEFORM375_READONLY_DRIFT')
 dest=out/'horse-deform375.npz';np.savez_compressed(dest,**arrays);report=dict(bones=len(names),poses=records,npz=dict(file=dest.name,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),geometry_actions_unchanged=True,scope='Actual bone rest/evaluated pose matrices, ownership and constraints; no authoring, no force reconstruction or causal/visual approval. Multi-segment bones require actual segment deformation before LBS counterfactual claims.')
 (out/'horse-deform375.json').write_text(json.dumps(report,indent=2)+'\n');return dict(report='horse-deform375.json',npz=dest.name,geometry_actions_unchanged=True)
