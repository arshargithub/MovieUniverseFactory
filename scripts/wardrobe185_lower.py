"""Fixed close contact controls for the inherited lower tunic.

Read-only capture precedes choosing a deformation repair. Numerical crossings
must be located against the actual rendered garment and saddle, not waived.
"""
import json
from pathlib import Path
import numpy as np


def inspect(out):
    import bpy
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import WORKING_SHA
    from wardrobe185_exit_audit import geometry
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-finishreview01/integration-working.blend'
    if digest(source)!=WORKING_SHA:raise ValueError('Lower garment source changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    names=['MF_fit_tunic_173_visible','MF_fit_trousers_173_visible',
        'MF185_gait_horse','MF185_gait_saddle','MF185_gait_saddle.pad']
    records=[]
    for frame in (1,169,217,223,326):
        scene.frame_set(frame);bpy.context.view_layer.update();data={}
        for name in names:
            ob=bpy.data.objects[name];states=[(m,m.show_viewport) for m in ob.modifiers if m.type=='SOLIDIFY']
            for m,_ in states:m.show_viewport=False
            p,f,labels=geometry(ob)
            for m,state in states:m.show_viewport=state
            data[name+'__points']=p;data[name+'__faces']=f;data[name+'__labels']=labels
            records.append({'frame':frame,'object':name,'vertices':len(p),'triangles':len(f),
                'bounds':[p.min(0).tolist(),p.max(0).tolist()]})
        np.savez_compressed(out/('surfaces-%03d.npz'%frame),**data)
    (out/'geometry-inventory.json').write_text(json.dumps(records,indent=2)+'\n')
    scene.frame_set(217);bpy.context.view_layer.update()
    for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):
        fit_render(out,'mounted-'+label+'-217',angle,(0,-.35,-6.6),7.,(640,640))
    scene.frame_set(223);bpy.context.view_layer.update()
    for angle,label in ((90,'left'),(180,'rear')):
        fit_render(out,'mounted-'+label+'-223',angle,(0,-.35,-7.3),7.,(640,640))
    scene.frame_set(169);bpy.context.view_layer.update()
    fit_render(out,'head-tip-seam-169',0,(.7446,-1.1393,-2.1423),1.25,(640,640))
    for ob in scene.objects:
        if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):ob.hide_render=True
    scene.frame_set(1);bpy.context.view_layer.update()
    for angle,label in ((0,'front'),(90,'left'),(180,'rear')):
        fit_render(out,'neutral-lower-'+label,angle,(0,0,-6.7),7.,(640,640))
    check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':WORKING_SHA,'protected_exact':True,
        'native_changed':False,'visual_gate':'NOT_RUN'},indent=2)+'\n')
