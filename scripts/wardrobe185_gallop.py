"""Integrated shot-envelope replay, using the exact admitted rider action.

Fixed local dependencies only. Each new stage is hash-bound before dispatch;
unset hashes deliberately prevent accidental qualification against a moving
input. Accepted static masters and source horse remain read-only.
"""
import json
from pathlib import Path
import numpy as np

RIDER_SHA='e5f0f7c1b78d5cec89ccbee2c366da698888eba699dc7ba554e7145a529b5ccb'
PREP_SHA='4e8d8aa3c508abf221e80469b0940523fb702ae0bac5ae5408754dd192e4e600'
TRAJECTORY_SHA=None
PROOF_SHA=None


def rest_parity(a,b):
    """Refuse animation transfer across incompatible rest skeletons."""
    if set(a.data.bones.keys())!=set(b.data.bones.keys()):
        raise ValueError('Rider/contact bone sets differ')
    error=0.
    for bone in a.data.bones:
        other=b.data.bones[bone.name]
        if (bone.parent.name if bone.parent else None)!=(other.parent.name if other.parent else None):
            raise ValueError('Rider/contact hierarchy differs')
        error=max(error,float(np.max(abs(np.array(bone.matrix_local)-np.array(other.matrix_local)))))
        if abs(bone.length-other.length)>1e-6:raise ValueError('Rider/contact bone lengths differ')
    if error>1e-6:raise ValueError('Rider/contact rest frames differ')
    return error


def transfer_action(source,target):
    rest_parity(source,target)
    if not source.animation_data or not source.animation_data.action:raise ValueError('Missing admitted rider action')
    target.animation_data_clear();target.animation_data_create()
    target.animation_data.action=source.animation_data.action
    target.animation_data.action_slot=source.animation_data.action_slot


def prep(out):
    import bpy
    from mathutils import Matrix
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_motion import SCALE
    base=BASE/'wardrobe185-motionprep02/motion-rig.blend'
    rider=BASE/'wardrobe185-riding06/rider-rig.blend'
    for path,sha in ((base,'a76ec35c1268ab77bbfc6fc9bdb8e330cdad8dbcee11b27b2eee9c7390df3b7f'),(rider,RIDER_SHA)):
        if sha is None or path.is_symlink() or digest(path)!=sha:raise ValueError('Unbound gallop dependency')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(base),load_ui=False,use_scripts=False)
    with bpy.data.libraries.load(str(rider),link=False) as (available,loaded):loaded.objects=['MF_body156_fit_rig']
    source=loaded.objects[0];bpy.context.scene.collection.objects.link(source)
    target=bpy.data.objects['MF178_metres_rig'];contact=bpy.data.objects['MF178_support_185_contact']
    # A libraries.write file stores data blocks, not scene membership. An
    # unlinked rig does not participate in dependency-graph frame evaluation.
    for ob in (target,contact):
        if ob.name not in bpy.context.scene.objects:bpy.context.scene.collection.objects.link(ob)
    error=rest_parity(source,target);transfer_action(source,target)
    original=np.array([v.co[:] for v in contact.data.vertices]);records=[];samples=[]
    for frame in range(1,361):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        maximum=0.
        for bone in ('pelvis','spine','chest','MF185_neck','MF185_head','upperarm.L','upperarm.R'):
            expected=Matrix.Scale(SCALE,4)@source.matrix_world@source.pose.bones[bone].matrix
            actual=target.matrix_world@target.pose.bones[bone].matrix
            maximum=max(maximum,float(np.max(abs(np.array(expected)-np.array(actual)))))
        if maximum>1e-5:raise ValueError('Canonical gallop frame mismatch '+str((frame,maximum)))
        if frame in (1,169,193,217,220,223,226,289,360):
            ev=contact.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
            q=np.array([v.co[:] for v in mesh.vertices]);ev.to_mesh_clear()
            if q.shape!=original.shape or not np.isfinite(q).all():raise ValueError('Invalid gallop collider')
            if frame==1 and np.max(abs(q-original))>2e-7:raise ValueError('Neutral collider changed')
            samples.append(q/SCALE)
        records.append({'frame':frame,'canonical_pose_error':maximum})
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    bpy.data.libraries.write(str(out/'motion-rig.blend'),{target,contact},fake_user=True,compress=True)
    np.savez_compressed(out/'contact-poses.npz',frames=np.array(samples),frame_ids=[1,169,193,217,220,223,226,289,360])
    # No actor is loaded here: scene-signature checks belong to the full
    # assembly, not a contact-only library. Verify these input files instead.
    if digest(base)!='a76ec35c1268ab77bbfc6fc9bdb8e330cdad8dbcee11b27b2eee9c7390df3b7f' or digest(rider)!=RIDER_SHA:
        raise ValueError('Contact transfer changed an input file')
    (out/'result.json').write_text(json.dumps({'rider_sha256':RIDER_SHA,'rest_error':error,'frames':records,
        'native_sha256':digest(out/'motion-rig.blend'),'visual_gate':'NOT_RUN','scope':'Exact action transfer to admitted contact proxy, not a cloth or trailer pass'},indent=2)+'\n')


def screen(out):
    import bpy
    from mathutils import Matrix
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe_shawl180_cache import cache
    from wardrobe_motion178_controls import render_geometry_paused
    from wardrobe185_riding import fit_tack
    from wardrobe_riding_fit import fit_render
    foundation=BASE/'wardrobe185-motionreview03/diagnostic.blend'
    rider=BASE/'wardrobe185-riding06/rider-rig.blend'
    horse=BASE/'wardrobe185-horsecache01/horse-library.blend'
    contacts=horse.parent/'contacts.npz'
    trajectory=BASE/'wardrobe185-gallopcloth01/trajectory.npz';proof=trajectory.parent/'motion-proof.npz'
    sources=((foundation,'0f128ba60947d4451f7e0bbaa3a5f6f275173702e3d4bddd245cef73d2310bd7'),
        (rider,RIDER_SHA),(horse,'8bccbbf45000cb61b8d50f014ff9db13973c97dd122b35b6bc6f77827e9e97a7'),
        (contacts,'15c434d960df8f9720b81d1d7d044ef0a29bca309631f310c7e1ba996de590c9'),
        (trajectory,TRAJECTORY_SHA),(proof,PROOF_SHA))
    for path,sha in sources:
        if sha is None or path.is_symlink() or digest(path)!=sha:raise ValueError('Unbound integrated gallop source '+str(path))
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(trajectory,allow_pickle=False) as d:frames=d['frames']
    with np.load(proof,allow_pickle=False) as d:matrices={n:d[n+'_matrices'] for n in ('chest','head')}
    with np.load(contacts,allow_pickle=False) as d:contact_data={n:d[n] for n in d.files}
    if frames.shape!=(360,7205,3) or any(a.shape!=(360,4,4) for a in matrices.values()):raise ValueError('Incomplete gallop trace')
    bpy.ops.wm.open_mainfile(filepath=str(foundation),load_ui=False,use_scripts=False)
    check_protected();scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    with bpy.data.libraries.load(str(rider),link=False) as (available,loaded):loaded.objects=['MF_body156_fit_rig']
    source=loaded.objects[0];scene.collection.objects.link(source)
    transfer_action(source,rig);bpy.data.objects.remove(source,do_unlink=True)
    ob=bpy.data.objects['MF185_moving_shawl']
    for mod in list(ob.modifiers):
        if mod.type=='MESH_CACHE':ob.modifiers.remove(mod)
    mod=cache(ob,frames,out/'cloth.mdd');bpy.context.view_layer.objects.active=ob
    while list(ob.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    with bpy.data.libraries.load(str(horse),link=False) as (available,loaded):loaded.objects=[n for n in available.objects if n.startswith('MF185_gait_')]
    if len(loaded.objects)!=10:raise ValueError('Incomplete horse assembly')
    for item in loaded.objects:scene.collection.objects.link(item)
    fit_tack(rig,contact_data,out,grasp=True)
    states=[(m,m.show_viewport) for m in ob.modifiers if m!=mod]
    for m,_ in states:m.show_viewport=False
    errors=[];cache_errors=[]
    with render_geometry_paused():
        ob.hide_viewport=False
        for frame in list(range(1,361))+[217,169,360,220]:
            scene.frame_set(frame);bpy.context.view_layer.update()
            for label,name in (('chest','chest'),('head','MF185_head')):
                bone=rig.pose.bones[name]
                matrix=rig.matrix_world@bone.matrix@bone.bone.matrix_local.inverted()@rig.matrix_world.inverted()
                errors.append(float(np.max(abs(np.array(matrix)-matrices[label][frame-1]))))
            if frame in (1,169,193,217,220,265,360):
                ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
                q=np.array([v.co[:] for v in mesh.vertices]);ev.to_mesh_clear()
                cache_errors.append(float(np.max(abs(q-frames[frame-1]))))
    for m,state in states:m.show_viewport=state
    if max(errors)>1e-5 or max(cache_errors)>2e-6:raise ValueError('Integrated rig/cloth mismatch')
    scene.frame_start=217;scene.frame_end=360;scene.frame_set(217)
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'diagnostic.blend'),check_existing=False,compress=True)
    for frame in (217,265,360):
        scene.frame_set(frame);bpy.context.view_layer.update()
        head=rig.matrix_world@rig.pose.bones['MF185_head'].head
        center=tuple(head+__import__('mathutils').Vector((0,0,-.6)))
        for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):
            fit_render(out,label+'-%03d'%frame,angle,center,8.,(640,640))
    for frame in (217,220,223,226):
        scene.frame_set(frame);bpy.context.view_layer.update()
        fit_render(out,'whole-%03d'%frame,35,(0,-1.8,-8),32.,(720,540))
    check_protected()
    (out/'result.json').write_text(json.dumps({'source_hashes':{str(p):h for p,h in sources},
        'head_chest_action_error':max(errors),'cloth_cache_error':max(cache_errors),
        'protected_local_data_exact':True,'native_sha256':digest(out/'diagnostic.blend'),
        'visual_gate':'NOT_RUN','full_playback':'NOT_RUN','wind_causality':'NOT_RUN','production_ready':False},indent=2)+'\n')
