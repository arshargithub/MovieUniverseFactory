"""Closed, read-only source inspection for206 route-choice and hair work."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SOURCES={
 'opening':('entrance205-opening45','f63e6fb06268f32ecfb691b836b9fed4b21b00dd9e49f90893531da54cb8446a'),
 'route':('entrance205-arc52','b71b102f3ce251674bd248771be08d2030c5593cd770239a4f36a1e291c21517')}

def validate(job):
 if job not in ({'operation':'inspect01'},{'operation':'inspect02'},{'operation':'inspect03'}):raise ValueError('Closed206 source inspection')

def main():
 import bpy
 from wardrobe_motion178_controls import render_geometry_paused
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());validate(job)
 out=base.BASE/('entrance206-'+job['operation'])
 if out.exists():raise ValueError('Preserve inspection')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());result={}
 for kind,(folder,sha) in SOURCES.items():
  src=base.BASE/folder/'scene.blend'
  if base.digest(src)!=sha:raise ValueError('Source changed')
  bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
  rig=bpy.data.objects['MF_body156_fit_rig'];hair={};arrays={}
  for ob in scene.objects:
   if ob.type!='CURVES' or not ob.name.startswith('MF_natural147'):continue
   a=np.empty((len(ob.data.points),3),np.float32);ob.data.attributes['position'].data.foreach_get('vector',a.ravel())
   offsets=[c.first_point_index for c in ob.data.curves]+[len(a)]
   arrays[ob.name]=a;arrays[ob.name+'__offsets']=np.array(offsets)
   hair[ob.name]={'points':len(a),'curves':len(offsets)-1,'bounds':[a.min(0).tolist(),a.max(0).tolist()],
     'parent':ob.parent.name if ob.parent else None,'surface':getattr(getattr(ob.data,'surface',None),'name',None),
     'attributes':[(x.name,x.domain,x.data_type) for x in ob.data.attributes],
     'modifiers':[{'name':m.name,'type':m.type,'group':getattr(getattr(m,'node_group',None),'name',None)} for m in ob.modifiers]}
  np.savez_compressed(out/(kind+'-guides.npz'),**arrays)
  samples=[]
  with render_geometry_paused():
   for f in ((217,315,337,350,360) if kind=='opening' else (361,384,409,487,529,577,648)):
    scene.frame_set(f);bpy.context.view_layer.update()
    samples.append({'frame':f,'camera':np.array(scene.camera.matrix_world).tolist(),'lens':scene.camera.data.lens,
      'head':np.array(rig.matrix_world@rig.pose.bones['MF185_head'].matrix).tolist(),
      'hair_support':np.array(bpy.data.objects['MF_natural147_hair_retarget'].matrix_world).tolist()})
  horse=bpy.data.objects['MF185_gait_horse'];a=np.array([v.co[:] for v in horse.data.vertices])
  np.savez_compressed(out/(kind+'-horse-rest.npz'),points=a)
  result[kind]={'source_sha256':sha,'hair':hair,'samples':samples,'horse_rest_bounds':[a.min(0).tolist(),a.max(0).tolist()],
    'checkpoint_objects':[o.name for o in scene.objects if o.name.startswith(('MF204_guard','MF190_provisional_timber'))],
    'curves_readonly_sha256':base.digest(out/(kind+'-guides.npz'))}
  print('206 inspected',kind,flush=True)
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
