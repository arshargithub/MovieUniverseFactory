"""Continuous garment interface from the existing evaluated fitted waist belt."""
import json
from pathlib import Path
import numpy as np


def boundary(rest,pins,grid):
    """Tailor only the upper cut to the existing continuous belt interface."""
    t=np.clip((-5.35-rest[:,2])/2.10,0,1)
    theta=np.arctan2(rest[:,0]/(1.42+.57*t),(rest[:,1]-.085-.025*t)/(1.14+.25*t))
    u=(theta%(2*np.pi))*96/(2*np.pi);i=np.floor(u).astype(int)%96;v=u-np.floor(u)
    ring=np.asarray(grid)
    def interpolate(a):return a[:,i]*(1-v[None,:,None])+a[:,(i+1)%96]*v[None,:,None]
    bottom=interpolate(ring[:,:,0]);up=interpolate(ring[:,:,-1]-ring[:,:,0]);up/=np.linalg.norm(up,axis=2)[:,:,None]
    tangent=interpolate(np.roll(ring[:,:,0],-1,axis=1)-np.roll(ring[:,:,0],1,axis=1))
    outward=np.cross(up,tangent);outward/=np.linalg.norm(outward,axis=2)[:,:,None]
    desired=bottom+up*(.06-2.10*t)[None,:,None]+outward*(-.02+.50*t)[None,:,None]
    blend=np.clip((t-.05)/.35,0,1);blend=blend*blend*(3-2*blend)
    tailored=desired[0]*(1-blend[:,None])+rest*blend[:,None]
    targets=desired[:,list(pins)]
    np.testing.assert_allclose(tailored[list(pins)],targets[0],atol=1e-7)
    return tailored,targets


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
