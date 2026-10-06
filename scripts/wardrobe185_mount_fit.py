"""Measure the inherited horse-to-pad registration over the actual gait.

This is a source diagnostic, not a fitted native or garment admission. Fixed
vertical-ray footprint reports both necessary displacement and residual gaps.
"""
import json
from pathlib import Path
import numpy as np

HORSE_SHIFT=np.array([0.,0.,-1.05])


def run(out):
    if out.name.endswith('mountfit02'):return corrected(out)
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest
    source=BASE/'wardrobe185-lowersurface06/surfaces.npz'
    if digest(source)!='3bf762fe9244188ef563a8ce1f235fb83c07614e7f538c8bc6209ff076e0499e':raise ValueError('Contact source drift')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(source,allow_pickle=False) as d:data={k:d[k] for k in d.files}
    records=[]
    for frame in range(217,361):
        i=list(data['frame_ids']).index(frame)
        hp=data['horse_frames'][i];hf=data['horse_faces'];pp=data['pad_frames'][i];pf=data['pad_faces']
        ht=BVHTree.FromPolygons(hp.tolist(),hf.tolist(),all_triangles=True)
        pt=BVHTree.FromPolygons(pp.tolist(),pf.tolist(),all_triangles=True)
        # Central pad bearing patch. Peripheral hanging flaps are not a seat
        # height datum. Keep all measurements, including missing ray support.
        q=pp[(abs(pp[:,0])<.8)&(abs(pp[:,1]+.2)<.8)]
        if not len(q):raise ValueError('No central pad support')
        center=np.median(q,axis=0);samples=[]
        for x in (-.55,0.,.55):
            for y in (-.45,0.,.45):
                origin=Vector((center[0]+x,center[1]+y,0.))
                ph,pn,_,_=pt.ray_cast(origin,Vector((0,0,-1)),30.)
                hh,hn,_,_=ht.ray_cast(origin,Vector((0,0,-1)),30.)
                if ph is not None and hh is not None:
                    samples.append({'xy':list(origin)[:2],'pad_top_z':ph.z,'horse_top_z':hh.z,
                        'horse_shift_to_pad_top_native':ph.z-hh.z,'pad_normal_z':pn.z,'horse_normal_z':hn.z})
        if len(samples)<6:raise ValueError('Insufficient bearing footprint')
        records.append({'frame':frame,'samples':samples})
    values=np.array([s['horse_shift_to_pad_top_native'] for r in records for s in r['samples']])
    (out/'result.json').write_text(json.dumps({'source_sha256':digest(source),'frames':records,
        'shift_quantiles_native':np.quantile(values,[0,.05,.5,.95,1]).tolist(),
        'scope':'Coarse contact registration measurement only; pad top is not its underside',
        'visual_gate':'NOT_RUN'},indent=2)+'\n')


def corrected(out):
    """One fixed mount registration candidate; actor and saddle stay exact.

    Reins are retargeted at the bit only, retaining the checked hand channel.
    The previous lower cloth remains hidden; no old cache is called valid for
    the changed horse contact. No per-frame collision avoidance is applied.
    """
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_lower import fast_geometry
    from wardrobe185_lower_gap import local_faces
    from wardrobe_riding_fit import fit_render
    from wardrobe_motion178_controls import render_geometry_paused
    source=BASE/'wardrobe185-lowerpants02/integration-working.blend'
    if digest(source)!='b9cf3b8c3f07d9ad650279903c5f81d54e85c6d553f801c0fb353cb2bf298f0b':raise ValueError('Mount source drift')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;changed=[]
    for ob in scene.objects:
        if ob.name.startswith('MF185_gait_') and not ob.name.startswith('MF185_gait_saddle'):
            if ob.animation_data is not None:raise ValueError('Unexpected object transform action')
            ob.location+=Vector(HORSE_SHIFT);changed.append(ob.name)
    if len(changed)!=6:raise ValueError('Unexpected horse assembly selection: '+str(changed))
    # The source reins already contain all-frame control points. Preserve the
    # exact terminal grip/channel and apply a linearly vanishing bit offset.
    with render_geometry_paused():
        for frame in range(217,361):
            scene.frame_set(frame);bpy.context.view_layer.update()
            for side in ('L','R'):
                ob=bpy.data.objects['MF185_rein_'+side]
                for k,p in enumerate(ob.data.splines[0].points):
                    if k<16:
                        p.co.xyz+=Vector(HORSE_SHIFT)*(1-k/16)
                        p.keyframe_insert(data_path='co',frame=frame)
    report={};scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    names={'body':'MF_studio_adult_body','pants':'MF_fit_trousers_173_visible',
        'horse':'MF185_gait_horse','saddle':'MF185_gait_saddle','pad':'MF185_gait_saddle.pad'}
    for frame in (169,193,217,220,223,226,326,360):
        scene.frame_set(frame);bpy.context.view_layer.update();trees={};geometry={}
        for key,name in names.items():
            p,f=fast_geometry(bpy.data.objects[name]);f=local_faces(p,f,(-2,-3,-9),(2,2,-4.5))
            geometry[key]=(p,f);trees[key]=BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True)
        row={}
        for a,b in (('body','horse'),('pants','horse'),('body','saddle'),('pants','saddle'),('horse','pad')):
            pairs=trees[a].overlap(trees[b]);row[a+'__'+b]=len(pairs)
        report[frame]=row
        if frame in (169,217,223,226):
            fit_render(out,'seat-left-'+str(frame),90,(0,-.2,-6.8),6.,(720,720))
            fit_render(out,'full-mounted-'+str(frame),90,(0,-1.8,-8),32.,(900,650))
        print('Mount corrected contact',frame,row,flush=True)
    scene.frame_set(217);bpy.context.view_layer.update();check_protected()
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'integration-working.blend'),check_existing=False)
    (out/'result.json').write_text(json.dumps({'source_sha256':digest(source),
        'native_sha256':digest(out/'integration-working.blend'),'shift_native':HORSE_SHIFT.tolist(),
        'changed_horse_objects':changed,'frames':report,'actor_and_saddle_motion':'Unchanged',
        'lower_cloth':'NOT_RUN; changed horse contact invalidates prior lower caches',
        'visual_gate':'NOT_RUN','protected_exact':True},indent=2)+'\n')
