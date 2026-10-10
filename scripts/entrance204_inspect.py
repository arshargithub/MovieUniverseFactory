"""Closed read-only inventory for approved story-performance continuation."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SOURCES={'opening':('entrance201-opening21','6876be12c139cbc50873355c0db3be0e0a72fbef1070dc71b27a37da9a49bf54'),'route':('entrance201-route22','a2fe859e2e84715c1a0be21dd7992c7200afd56f4765ec571a4214f8c2c960c3')}
def main():
 import bpy
 from wardrobe_motion178_controls import render_geometry_paused
 if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'inspect01'}:raise ValueError('Fixed operation')
 out=base.BASE/'entrance204-inspect01'
 if out.exists():raise ValueError('Preserve evidence')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());record={}
 for kind,(folder,sha) in SOURCES.items():
  path=base.BASE/folder/'scene.blend'
  if base.digest(path)!=sha:raise ValueError('Source changed')
  bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected();rig=bpy.data.objects['MF_body156_fit_rig'];rows=[]
  with render_geometry_paused():
   for f in ((289,324,350,360) if kind=='opening' else (361,409,457,505,552)):
    scene.frame_set(f);bpy.context.view_layer.update()
    rows.append({'frame':f,'camera':np.array(scene.camera.matrix_world).tolist(),'lens':scene.camera.data.lens,'rig':np.array(rig.matrix_world).tolist(),'bones':{n:np.array(rig.matrix_world@rig.pose.bones[n].matrix).tolist() for n in ('pelvis','chest','MF185_neck','MF185_head','hand.L','hand.R')}})
  obs={}
  for ob in scene.objects:
   if ob.name in ('MF_studio_adult_body','MF185_moving_shawl','MF188_flowing_mane','MF188_distant_art_arc','MF190_shared_route_actor') or (not ob.hide_render and any(s in ob.name.lower() for s in ('eye','hair','brow','rein'))):
    obs[ob.name]={'type':ob.type,'parent':ob.parent.name if ob.parent else None,'bone':ob.parent_bone,'matrix':np.array(ob.matrix_world).tolist(),'constraints':[{'type':c.type,'target':getattr(getattr(c,'target',None),'name',None),'subtarget':getattr(c,'subtarget',None)} for c in ob.constraints],'modifiers':[{'type':m.type,'target':getattr(getattr(m,'object',None),'name',None)} for m in ob.modifiers]}
  keys=bpy.data.objects['MF_studio_adult_body'].data.shape_keys
  record[kind]={'source_sha256':sha,'samples':rows,'objects':obs,'face_keys':[k.name for k in keys.key_blocks],'face_drivers':[{'path':d.data_path,'targets':[{'id':v.targets[0].id.name,'path':v.targets[0].data_path} for v in d.driver.variables]} for d in keys.animation_data.drivers]}
 (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__':main()
