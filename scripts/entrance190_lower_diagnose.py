"""Failure-seeking views of the rejected skirt, not a ready candidate."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance190_integration import SOURCE_SHA,actor_object

def main():
    import bpy
    from entrance189_groom import attach_cache,write_mdd
    from wardrobe_riding_fit import fit_render
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'lowerdiagnose14'}:raise ValueError('Fixed failed-cloth diagnosis required')
    source=base.BASE/'entrance190-fitted12/fitted.blend';out=base.BASE/'entrance190-lowerdiagnose14'
    if out.exists() or base.digest(source)!=SOURCE_SHA:raise ValueError('Changed source or prior output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    with np.load(base.BASE/'entrance190-lower13/failed-prefix.npz',allow_pickle=False) as z:a=z['frames'][311:]
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene
    ob=bpy.data.objects['MF185_free_lower_tunic'];write_mdd(out/'failed-skirt.mdd',len(a),a.shape[1],iter(a));attach_cache(ob,out/'failed-skirt.mdd',361)
    cache_checks=[]
    for item in scene.objects:
        if item.type not in ('LIGHT','CAMERA','EMPTY'):item.hide_render=item.hide_render or not actor_object(item)
        if item.name in ('MF185_moving_shawl','MF188_flowing_mane','MF185_gait_Full Bushy Flowing Horse Tail'):item.hide_render=True
        if item.name.startswith('MF185_stirrup_leather'):
            cache_checks.append({'name':item.name,'vertices':len(item.data.vertices),'modifiers':[(m.name,m.type) for m in item.modifiers]})
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    final=360+len(a)
    for frame in (361,409,final):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for angle,label in ((70,'left'),(180,'rear'),(290,'right')):fit_render(out,label+'-'+str(frame),angle,(0,-.2,-7),12.,(640,640))
    (out/'result.json').write_text(json.dumps({'status':'FAILED_SKIRT_DIAGNOSTIC','last_frame':final,'cache_stack_checks':cache_checks},indent=2)+'\n')

if __name__=='__main__':main()
