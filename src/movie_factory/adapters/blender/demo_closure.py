"""Fixed deformation closure differential; no generated execution input."""
from pathlib import Path
import bpy,importlib.util,math
BASE=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01')
def run(mf,out,job,helper):
 if set(job)!={'mode','output_dir','profile'} or job['mode']!='demo_sustained_closure' or job['profile']!={}:raise ValueError('Invalid fixed closure')
 out=Path(out)
 if BASE.resolve() not in out.resolve().parents:raise ValueError('Invalid output')
 spec=importlib.util.spec_from_file_location('closure_replay',Path(__file__).with_name('demo_fullpace_replay.py'));replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)
 source={};frames=(1.875,3.25,3.875)
 def snapshot(h):
  obj=bpy.data.objects['horse'];deps=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(deps);m=ev.to_mesh();verts=[v.co.copy() for v in m.vertices];ev.to_mesh_clear()
  return {'verts':verts,'basis':{p.name:p.matrix_basis.copy() for p in h.pose.bones},'matrices':{p.name:p.matrix.copy() for p in h.pose.bones},'modes':{p.name:p.rotation_mode for p in h.pose.bones}}
 def observer(kind,f,h):
  if kind=='source' and f in frames:source[f]=snapshot(h)
 replay.reconstruct(mf,helper,observer);h=bpy.data.objects['horse.rig'];scene=bpy.context.scene
 controlnames=sorted({fc.data_path.split('"')[1] for fc in mf.action_channels(bpy.data.actions['horse.gallop']) if fc.data_path.startswith('pose.bones')})
 groups={'foot_heel':['forefoot_ik.R','forefoot_heel_ik.R'],'whole_distal':['forefoot_ik.R','forefoot_heel_ik.R','f_toe_ik.R','f_hoof.R'],'all_animated':controlnames,'all_pose':list(source[frames[0]]['basis'])}
 rows=[]
 for f in frames:
  for label,names in groups.items():
   # Re-evaluate the immutable candidate before each disposable intervention.
   for p in h.pose.bones:
    if p.name in ('forefoot_ik.L','forefoot_ik.R','hind_foot_ik.L','hind_foot_ik.R','forefoot_heel_ik.L','forefoot_heel_ik.R','hind_foot_heel_ik.L','hind_foot_heel_ik.R'):p.rotation_mode='QUATERNION'
   helper._refresh(scene,mf,f)
   for name in sorted(names,key=lambda n:len(h.pose.bones[n].parent_recursive)):
    h.pose.bones[name].rotation_mode=source[f]['modes'][name];h.pose.bones[name].matrix_basis=source[f]['basis'][name];bpy.context.view_layer.update()
   now=snapshot(h);diffs=[(a-b).length for a,b in zip(source[f]['verts'],now['verts'])];matrixdiff=[{'bone':n,'max_matrix_delta':max(abs(source[f]['matrices'][n][i][j]-now['matrices'][n][i][j]) for i in range(4) for j in range(4))} for n in source[f]['matrices']]
   rows.append({'frame':f,'group':label,'rms_vertex_delta':math.sqrt(sum(v*v for v in diffs)/len(diffs)),'max_vertex_delta':max(diffs),'worst_bones':sorted(matrixdiff,key=lambda x:x['max_matrix_delta'],reverse=True)[:15]})
 mf.write_json(out/'closure.json',{'comparisons':rows,'source_settings':'Configuration reference with no IK stretch, matching prior candidate; not untouched original reference. Mesh compared object-local, no scale alignment.','controls':controlnames})
 return ['closure.json']
