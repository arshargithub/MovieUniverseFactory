"""Fixed close contact controls for the inherited lower tunic.

Read-only capture precedes choosing a deformation repair. Numerical crossings
must be located against the actual rendered garment and saddle, not waived.
"""
import json
from pathlib import Path
import numpy as np


def world_points(local,matrix):
    p=np.asarray(local);m=np.asarray(matrix)
    if p.ndim!=2 or p.shape[1]!=3 or m.shape!=(4,4) or not np.isfinite(p).all() or not np.isfinite(m).all():
        raise ValueError('Invalid surface transform')
    return p@m[:3,:3].T+m[:3,3]


def fast_geometry(ob):
    import bpy
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
    p=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',p)
    f=np.empty(len(mesh.loop_triangles)*3,dtype=np.int32);mesh.loop_triangles.foreach_get('vertices',f)
    ev.to_mesh_clear()
    return world_points(p.reshape(-1,3),np.array(ob.matrix_world)),f.reshape(-1,3)


def capture(out):
    """Separate source capture from lightweight cloth/contact construction."""
    import bpy
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import WORKING_SHA
    from wardrobe_motion178_controls import render_geometry_paused
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-finishreview01/integration-working.blend'
    if digest(source)!=WORKING_SHA:raise ValueError('Lower contact source changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    skirt=bpy.data.objects['MF_fit_tunic_173_visible'];pants=bpy.data.objects['MF_fit_trousers_173_visible']
    states=[(m,m.show_viewport) for ob in (skirt,pants) for m in ob.modifiers if m.type=='SOLIDIFY']
    for m,_ in states:m.show_viewport=False
    sample_frames=(1,169,193,217,220,223,226,265,300,324,348,360)
    bones={'pelvis':'pelvis','thighL':'thigh.L','thighR':'thigh.R'}
    matrices={n:[] for n in bones};guide=[];sampled={};faces=None
    required={skirt,pants}
    for _ in range(8):
        prior=len(required)
        for ob in list(required):
            for mod in ob.modifiers:
                for prop in ('target','object'):
                    target=getattr(mod,prop,None)
                    if target is not None and isinstance(target,bpy.types.Object):required.add(target)
        if len(required)==prior:break
    with render_geometry_paused():
        for ob in required:ob.hide_viewport=False
        for frame in range(1,361):
            pants.hide_viewport=frame not in sample_frames
            scene.frame_set(frame);bpy.context.view_layer.update()
            for label,bone in bones.items():
                b=rig.pose.bones[bone]
                matrices[label].append(np.array(rig.matrix_world@b.matrix@b.bone.matrix_local.inverted()@rig.matrix_world.inverted()))
            p,f=fast_geometry(skirt)
            if faces is None:faces=f
            elif not np.array_equal(f,faces):raise ValueError('Lower guide topology changes')
            guide.append(p)
            if frame in sample_frames:
                p,pf=fast_geometry(pants)
                sampled['pants_'+str(frame)]=p
                if frame==1:sampled['pants_faces']=pf
                elif not np.array_equal(pf,sampled['pants_faces']):raise ValueError('Pant sampling topology changes')
            if frame%48==0:print('185 lower source',frame,flush=True)
    for m,state in states:m.show_viewport=state
    np.savez_compressed(out/'moving-source.npz',guide=np.array(guide),guide_faces=faces,
        **sampled,**{k+'_matrices':np.array(v) for k,v in matrices.items()})
    buckle=[]
    for ob in scene.objects:
        if ob.type=='MESH' and any(s in ob.name.lower() for s in ('buckle','rivet','keeper','tongue')):
            buckle.append({'name':ob.name,'hidden':ob.hide_render,'vertices':len(ob.data.vertices),
                'modifiers':[m.type for m in ob.modifiers],'constraints':[(c.type,getattr(c,'subtarget',None)) for c in ob.constraints]})
    (out/'fastening-inventory.json').write_text(json.dumps(buckle,indent=2)+'\n')
    scene.frame_set(169);bpy.context.view_layer.update();scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    for ob in scene.objects:
        if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):ob.hide_render=True
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    fit_render(out,'unoccluded-head-tip-seam-169',0,(.7446,-1.1393,-2.1423),1.25,(640,640))
    scene.frame_set(1);bpy.context.view_layer.update()
    fit_render(out,'neutral-fastening',0,(0,-1,-5.1),2.1,(640,640))
    check_protected()
    (out/'source.json').write_text(json.dumps({'working_sha256':WORKING_SHA,'sample_frames':sample_frames,
        'moving_source_sha256':digest(out/'moving-source.npz'),'protected_exact':True,
        'scope':'Source for lower cloth repair, not new lower garment or contact qualification'},indent=2)+'\n')


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
