"""Read-only material-ID control for new rear coverage; not production art."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
def main():
 import bpy
 from mathutils import Vector
 from entrance204_build import camera_pose
 if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'coverage07'}:raise ValueError('Fixed diagnostic')
 src=base.BASE/'entrance204-route05/scene.blend';r=json.loads((src.parent/'result.json').read_text());out=base.BASE/'entrance204-coverage07'
 if out.exists() or base.digest(src)!=r['native_sha256']:raise ValueError('Source/output')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 scene=bpy.context.scene;base.check_protected();scene.frame_set(552);bpy.context.view_layer.update();camera_pose(scene,'final',552)
 rig=bpy.data.objects['MF_body156_fit_rig'];target=(rig.matrix_world@rig.pose.bones['pelvis'].matrix).translation
 cam=scene.camera;offset=cam.location-target;cam.location=target+offset.normalized()*24;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=60
 stats={}
 for name in ('MF_studio_adult_body','MF185_fitted_upper_tunic','MF185_free_lower_tunic','MF_173_waist_belt'):
  ob=bpy.data.objects[name];a=ob.data.attributes.get('MF_173_material_coords');p=np.array([v.co[:] for v in ob.data.vertices]);rest=np.array([v.vector[:] for v in a.data]) if a else p
  stats[name]={'rest_bounds':[rest.min(0).tolist(),rest.max(0).tolist()],'materials':[m.name if m else None for m in ob.data.materials],'modifiers':[{'name':m.name,'type':m.type} for m in ob.modifiers]}
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.use_persistent_data=False;scene.cycles.samples=8;scene.cycles.device='CPU'
 original={name:list(bpy.data.objects[name].data.materials) for name in ('MF_studio_adult_body','MF_173_waist_belt')}
 for label in ('beauty','material-id'):
  if label=='material-id':
   for name,color in (('MF_studio_adult_body',(1,0,1,1)),('MF_173_waist_belt',(0,1,0,1))):
    ob=bpy.data.objects[name];mat=bpy.data.materials.new('DIAGNOSTIC '+name);mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=color;o=n.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(e.outputs[0],o.inputs['Surface'])
    for i in range(len(ob.data.materials)):ob.data.materials[i]=mat
  scene.render.filepath=str(out/(label+'.png'))
  if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise ValueError('Render failed')
 for name,materials in original.items():
  for i,mat in enumerate(materials):bpy.data.objects[name].data.materials[i]=mat
 for f in (433,469):
  scene.frame_set(f);bpy.context.view_layer.update();camera_pose(scene,'wide',f);scene.render.filepath=str(out/f'wide-{f:04d}.png')
  if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise ValueError('Render failed')
 for f in (505,553):
  scene.frame_set(f);bpy.context.view_layer.update();camera_pose(scene,'final',f)
  head=(rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation
  target=head+Vector((0,0,-1.5));cam.location=target+(cam.location-target).normalized()*18;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=55
  scene.render.filepath=str(out/f'headfall-{f:04d}.png')
  if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise ValueError('Render failed')
 (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'objects':stats,'status':'DIAGNOSTIC_NOT_VISUAL_PASS'},indent=2)+'\n')
if __name__=='__main__':main()
