"""Measure the inherited horse-to-pad registration over the actual gait.

This is a source diagnostic, not a fitted native or garment admission. Fixed
vertical-ray footprint reports both necessary displacement and residual gaps.
"""
import json
from pathlib import Path
import numpy as np

HORSE_SHIFT=np.array([0.,0.,-1.05])


def rein_points(bit,channel):
    bit=np.asarray(bit,float);channel=np.asarray(channel,float)
    tangent=channel[-1]-channel[-2];length=np.linalg.norm(tangent)
    if bit.shape!=(3,) or channel.shape!=(4,3) or length<1e-8:raise ValueError('Invalid rein contacts')
    points=[]
    for k in range(22):
        if k<=16:
            t=k/16;p=(1-t)*bit+t*channel[0];p[2]-=.16*4*t*(1-t)
        elif k<=19:p=channel[k-16]
        else:p=channel[-1]+tangent/length*(.12*(k-19))
        points.append(p)
    return np.array(points)


def run(out):
    if out.name.endswith('mountclear01'):return clearance(out)
    if out.name.endswith(('mountfit02','mountfit03')):return corrected(out)
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
    from wardrobe185_grip import rein_channel
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
    absolute=out.name.endswith('mountfit03')
    contacts=BASE/'wardrobe185-horsecache01/contacts.npz'
    if digest(contacts)!='15c434d960df8f9720b81d1d7d044ef0a29bca309631f310c7e1ba996de590c9':raise ValueError('Bit motion changed')
    with np.load(contacts,allow_pickle=False) as d:bits=d['bit_points']
    expected={}
    # The source reins already contain all-frame control points. Preserve the
    # exact terminal grip/channel and apply a linearly vanishing bit offset.
    with render_geometry_paused():
        for frame in range(217,361):
            scene.frame_set(frame);bpy.context.view_layer.update()
            for j,side in enumerate(('L','R')):
                ob=bpy.data.objects['MF185_rein_'+side]
                if absolute:
                    route=rein_points(bits[frame-217,j]+HORSE_SHIFT,rein_channel(bpy.data.objects['MF_body156_fit_rig'],side))
                    expected[frame,side]=route
                    for k,p in enumerate(ob.data.splines[0].points):
                        p.co=(*route[k],1);p.keyframe_insert(data_path='co',frame=frame)
                    continue
                for k,p in enumerate(ob.data.splines[0].points):
                    if k<16:
                        p.co.xyz+=Vector(HORSE_SHIFT)*(1-k/16)
                        p.keyframe_insert(data_path='co',frame=frame)
    endpoint_error=0.
    if absolute:
        for frame in (217,220,223,226,326,360,223,217):
            scene.frame_set(frame);bpy.context.view_layer.update()
            for side in ('L','R'):
                actual=np.array([p.co[:3] for p in bpy.data.objects['MF185_rein_'+side].data.splines[0].points])
                endpoint_error=max(endpoint_error,float(np.max(abs(actual-expected[frame,side]))))
        if endpoint_error>2e-5:raise ValueError('Rein control is not seek-stable')
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
        'rein_max_seek_error_native':endpoint_error if absolute else None,
        'lower_cloth':'NOT_RUN; changed horse contact invalidates prior lower caches',
        'visual_gate':'NOT_RUN','protected_exact':True},indent=2)+'\n')


def clearance(out):
    """Measure one constant saddle clearance across all144 current frames.

    No framewise avoidance path is authored. A 20mm maximum investigation
    range bounds this small registration hypothesis, not task duration.
    """
    import bpy
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_lower import fast_geometry
    from wardrobe185_lower_gap import local_faces
    from wardrobe_motion178_controls import render_geometry_paused
    source=BASE/'wardrobe185-trouserseat01/integration-working.blend'
    expected='b3a4e413c9d43e001b4b627769fac07c029643b1bfd9e053352c0f3d5d94be65'
    if digest(source)!=expected:raise ValueError('Unbound clearance source')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    pants=bpy.data.objects['MF_fit_trousers_173_visible'];saddle=bpy.data.objects['MF185_gait_saddle']
    for mod in pants.modifiers:
        if mod.type=='SOLIDIFY':mod.show_viewport=False
    rows=[];required=0.;unresolved=[]
    with render_geometry_paused():
        pants.hide_viewport=False;saddle.hide_viewport=False
        for frame in range(217,361):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
            p,f=fast_geometry(pants);q,g=fast_geometry(saddle)
            f=local_faces(p,f,(-2,-3,-9),(2,2,-4.5))
            tree=BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True)
            counts=[];first=None
            for shift in np.linspace(0,.16,9):
                moved=q-[0,0,shift]
                other=BVHTree.FromPolygons(moved.tolist(),g.tolist(),all_triangles=True)
                n=len(tree.overlap(other));counts.append([float(shift),n])
                if n==0:first=float(shift);break
            if first is None:unresolved.append(frame)
            else:required=max(required,first)
            rows.append({'frame':frame,'tests':counts,'first_clear_native':first})
            if frame%24==0:print('Saddle clearance',frame,'max required',required,'unresolved',len(unresolved),flush=True)
    check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':expected,'frames':rows,
        'maximum_first_clear_native':required,'unresolved_frames':unresolved,
        'scope':'Measured constant vertical registration candidate; full mount, pad, feet/reins and cloth still require renewed validation',
        'visual_gate':'NOT_RUN','protected_exact':True},indent=2)+'\n')
