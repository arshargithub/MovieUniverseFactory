"""Continuous garment interface from the existing evaluated fitted waist belt."""
import json
from pathlib import Path
import numpy as np


def capture(out):
    import bpy
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import WORKING_SHA
    from wardrobe185_lower import fast_geometry
    from wardrobe_motion178_controls import render_geometry_paused
    source=BASE/'wardrobe185-finishreview01/integration-working.blend'
    if digest(source)!=WORKING_SHA:raise ValueError('Unbound belt interface source')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;belt=bpy.data.objects['MF_173_waist_belt']
    flags=[(m,m.show_viewport) for m in belt.modifiers if m.type!='SURFACE_DEFORM']
    for m,_ in flags:m.show_viewport=False
    targets=[m.target for m in belt.modifiers if m.type=='SURFACE_DEFORM']
    samples=[];signature=None;frames=[1,*range(169,361)]
    with render_geometry_paused():
        belt.hide_viewport=False
        for ob in targets:ob.hide_viewport=False
        for frame in frames:
            scene.frame_set(frame);bpy.context.view_layer.update();p,f,sig=fast_geometry(belt,True)
            if p.shape!=(480,3):raise ValueError('Belt interface topology changed')
            if signature is None:signature=sig
            elif sig!=signature:raise ValueError('Belt interface polygon identity changed')
            samples.append(p.reshape(96,5,3))
            if frame%48==0:print('185 belt interface',frame,flush=True)
    for m,state in flags:m.show_viewport=state
    q=np.array(samples);length=np.linalg.norm(np.roll(q[:,:,0],-1,axis=1)-q[:,:,0],axis=2)
    ratio=length/length[0]
    np.savez_compressed(out/'belt.npz',frames=q,frame_ids=frames)
    check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':WORKING_SHA,'belt_sha256':digest(out/'belt.npz'),
        'maximum_lower_edge_ratio':float(ratio.max()),'minimum_lower_edge_ratio':float(ratio.min()),
        'polygon_identity_exact':True,'protected_exact':True,'visual_gate':'NOT_RUN'},indent=2)+'\n')
