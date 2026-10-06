"""Neutral staging and evidence-gated portable character selection.

The resting look is a frozen drape. New performances still need the declared
cloth recipe/contact fit and resimulation; it is not an all-motion cloth rig.
"""
import json
from pathlib import Path
import numpy as np

CRITERIA={'construction_route','reference_layering','neutral_partial_full_interfaces',
    'actual_gallop_temporal','wind_response','rider_horse_tack_contacts',
    'adjacent_regressions','finished_appearance'}


def review_gate(record,base):
    """Selection is unavailable until a deliberate evidence-backed review."""
    if record.get('status')!='INTERNAL_REVIEW_READY' or set(record.get('criteria',{}))!=CRITERIA:
        raise ValueError('Incomplete internal review')
    for row in record['criteria'].values():
        if row.get('status')!='PASS' or not row.get('judgment') or not row.get('evidence'):
            raise ValueError('Unresolved internal review criterion')
        for reference in row['evidence']:
            path=(base/reference).resolve()
            if not path.is_relative_to(base.resolve()) or not path.is_file():raise ValueError('Missing/outside review evidence')


def samples():
    import bpy
    from wardrobe_riding_fit import evaluated_surfaces
    names=['MF_studio_adult_body','MF185_moving_shawl','MF185_fitted_upper_tunic',
        'MF185_free_lower_tunic','MF_fit_trousers_173_visible','MF_173_waist_belt',
        'MF185_gait_horse','MF185_gait_saddle.stirrup']
    names.extend(ob.name for ob in bpy.context.scene.objects if 'buckle' in ob.name and ob.type=='MESH' and not ob.hide_render)
    output={}
    for frame in (217,253,289,325,360):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        for name,q in evaluated_surfaces(names).items():
            output[str(frame)+'__'+name]=q
            output[str(frame)+'__'+name+'__matrix']=np.array(bpy.data.objects[name].matrix_world)
        for name in ('MF_aimable_eye_Left','MF_aimable_eye_Right','MF_natural147_hair_temples','MF_natural147_hair_retarget'):
            output[str(frame)+'__'+name+'__matrix']=np.array(bpy.data.objects[name].matrix_world)
    return output


def seal(out):
    """Create portable shot and neutral natives only after the exit gate."""
    import shutil
    import bpy
    from wardrobe_motion178 import BASE,ROOT,digest,check_protected
    from wardrobe185_shot import REPAIRED_SHA,setup_camera,setup_lighting
    from wardrobe_riding_fit import fit_render
    import subprocess
    source=BASE/'wardrobe185-lowerreview07/integration-working.blend'
    review_path=BASE/'wardrobe185-operating/visual-review.json'
    review_gate(json.loads(review_path.read_text()),BASE)
    if digest(source)!=REPAIRED_SHA:raise ValueError('Selected working source changed')
    camera_proof=BASE/'wardrobe185-shotmotion02/motion-render.json'
    camera_record=json.loads(camera_proof.read_text())
    if camera_record['source_sha256']!=REPAIRED_SHA or [p['frame'] for p in camera_record['poses']]!=list(range(217,361)):
        raise ValueError('Incomplete matching camera proof')
    (out/'camera-proof.json').write_bytes(camera_proof.read_bytes())
    # This certifies the selection/packaging source, not retrospectively every
    # exploratory simulation. Their frozen inputs and snapshots stay explicit.
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    import hashlib
    rows=[]
    paths=[Path(__file__),ROOT/'scripts/wardrobe185_shot.py',ROOT/'scripts/wardrobe_doublewrap185.py',
        ROOT/'scripts/wardrobe_motion178.py',ROOT/'scripts/wardrobe185_gallop.py',ROOT/'scripts/wardrobe185_interface_audit.py',
        ROOT/'src/movie_factory/adapters/blender/wardrobe_riding_fit.py']
    for path in paths:
        relative=str(path.relative_to(ROOT));blob=subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)
        if hashlib.sha256(blob).hexdigest()!=digest(path):raise ValueError('Commit packaging handlers before selection')
        rows.append({'path':relative,'sha256':digest(path)});(out/path.name).write_bytes(blob)
    binding={'commit':commit,'files':rows,'working_source_sha256':REPAIRED_SHA,'manual_review_sha256':digest(review_path),
        'camera_proof_sha256':digest(camera_proof),
        'scope':'Selection and portable packaging source; upstream discovery inputs retained, not retrospective source certification'}
    (out/'source-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig'];check_protected()
    setup_lighting(scene)
    if len(bpy.data.libraries):raise ValueError('Resolve linked native libraries before declaring portability')
    deps=[];cache_dir=out/'cache';cache_dir.mkdir()
    for ob in scene.objects:
        for mod in ob.modifiers:
            if mod.type!='MESH_CACHE':continue
            path=Path(bpy.path.abspath(mod.filepath)).resolve()
            if not path.is_relative_to(BASE) or not path.is_file():raise ValueError('Cache outside asset scope')
            sha=digest(path);target=cache_dir/(sha+'.mdd')
            if not target.exists():shutil.copyfile(path,target)
            if digest(target)!=sha:raise ValueError('Cache copy differs')
            mod.filepath=str(target)
            deps.append({'object':ob.name,'file':'cache/'+target.name,'sha256':sha})
    for text in bpy.data.texts:text.use_module=False
    bpy.ops.file.pack_all()
    unpacked=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not im.packed_files]
    if unpacked:raise ValueError('Unpacked image dependencies: '+str(unpacked))
    for frame in range(217,361):
        scene.frame_set(frame);bpy.context.view_layer.update();setup_camera(scene,rig,frame)
        scene.camera.keyframe_insert(data_path='location',frame=frame);scene.camera.keyframe_insert(data_path='rotation_euler',frame=frame)
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.render.fps=24;scene.frame_start=217;scene.frame_end=360
    (out/'renders').mkdir();scene.render.filepath=str(out/'renders/frame-')
    np.savez_compressed(out/'evaluated-surfaces.npz',**samples())
    scene.frame_set(325);scene['MF185_scope']='Internal reviewed entrance asset; Director acceptance and release rights separate'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'riding-entrance.blend'),check_existing=False,compress=True)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'riding-entrance.blend'),check_existing=False,compress=True)
    shot_sha=digest(out/'riding-entrance.blend')
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO';neutral=neutral_state()
    from wardrobe185_interface_audit import neutral_lower
    neutral_lower()
    for ob in list(scene.objects):
        if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):bpy.data.objects.remove(ob,do_unlink=True)
    scene.cycles.device='CPU';scene.cycles.samples=8
    fit_render(out,'neutral-master-front',0,(0,.15,-1.7),8.,(640,640))
    from wardrobe_riding_fit import evaluated_surfaces
    names=['MF_studio_adult_body','MF185_moving_shawl','MF185_fitted_upper_tunic',
        'MF185_free_lower_tunic','MF_fit_trousers_173_visible','MF_173_waist_belt']
    np.savez_compressed(out/'neutral-surfaces.npz',**evaluated_surfaces(names))
    scene.render.filepath='//renders/neutral-'
    check_protected();bpy.ops.wm.save_as_mainfile(filepath=str(out/'neutral-look-master.blend'),check_existing=False,compress=True)
    (out/'result.json').write_text(json.dumps({'source_binding_sha256':digest(out/'source-binding.json'),
        'shot_sha256':shot_sha,'neutral_sha256':digest(out/'neutral-look-master.blend'),
        'cache_dependencies':deps,'neutral':neutral,'protected_exact':True,'director_acceptance':'PENDING',
        'rights':'UNRESOLVED_UPSTREAM_NOT_RELEASE_PERMISSION','off_device_recovery':'NOT_RUN'},indent=2)+'\n')


def verify(out):
    import bpy
    from mathutils import Vector
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import setup_camera,setup_lighting
    from wardrobe_riding_fit import evaluated_surfaces,fit_render
    source=BASE/'wardrobe185-seal01';record=json.loads((source/'result.json').read_text())
    if digest(source/'source-binding.json')!=record['source_binding_sha256']:raise ValueError('Selection binding changed')
    if digest(source/'riding-entrance.blend')!=record['shot_sha256']:raise ValueError('Selected native changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    for row in record['cache_dependencies']:
        path=(source/row['file']).resolve()
        if not path.is_relative_to(source) or digest(path)!=row['sha256']:raise ValueError('Copied dependency differs')
    bpy.ops.wm.open_mainfile(filepath=str(source/'riding-entrance.blend'),load_ui=False,use_scripts=False)
    check_protected();scene=bpy.context.scene
    for ob in scene.objects:
        for mod in ob.modifiers:
            if mod.type=='MESH_CACHE' and not Path(bpy.path.abspath(mod.filepath)).resolve().is_relative_to(source):
                raise ValueError('Native still depends on an external cache')
    with np.load(source/'evaluated-surfaces.npz',allow_pickle=False) as ref:
        actual=samples()
        if set(actual)!=set(ref.files):raise ValueError('Surface sample inventory changed')
        errors={key:float(np.max(abs(actual[key]-ref[key]))) if actual[key].shape==ref[key].shape else None for key in ref.files}
    if any(v is None or not np.isfinite(v) or v>2e-5 for v in errors.values()):raise ValueError('Fresh-open moving surfaces differ')
    binding=json.loads((source/'source-binding.json').read_text())
    if digest(source/'camera-proof.json')!=binding['camera_proof_sha256']:raise ValueError('Camera proof changed')
    camera_errors=[]
    for row in json.loads((source/'camera-proof.json').read_text())['poses']:
        if row['frame'] not in (217,253,289,325,360):continue
        scene.frame_set(row['frame']);bpy.context.view_layer.update();camera=scene.camera
        direction=(Vector(row['target'])-camera.location).normalized()
        forward=camera.matrix_world.to_quaternion()@Vector((0,0,-1))
        error=max((camera.location-Vector(row['position'])).length,(forward-direction).length,abs(camera.data.lens-row['lens_mm']))
        if not np.isfinite(error) or error>2e-5:raise ValueError('Reopened camera differs from rendered proof')
        camera_errors.append({'frame':row['frame'],'max_component_error':error})
    # Representative reuse: opposite-side camera on existing action/cache.
    scene.frame_set(325);bpy.context.view_layer.update();before=evaluated_surfaces(['MF185_moving_shawl'])['MF185_moving_shawl']
    alternate=scene.camera.copy();alternate.data=scene.camera.data.copy();alternate.animation_data_clear()
    alternate.name='MF185_alternate_reuse_camera';scene.collection.objects.link(alternate);scene.camera=alternate
    view=setup_camera(scene,bpy.data.objects['MF_body156_fit_rig'],325);setup_lighting(scene)
    scene.camera.location.x*=-1
    scene.camera.rotation_euler=(Vector(view['target'])-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    scene.render.filepath=str(out/'alternate-camera-325.png');bpy.ops.render.render(write_still=True)
    after=evaluated_surfaces(['MF185_moving_shawl'])['MF185_moving_shawl'];reuse_error=float(np.max(abs(after-before)))
    if reuse_error>1e-7:raise ValueError('Camera reuse unexpectedly changed cloth')
    if digest(source/'neutral-look-master.blend')!=record['neutral_sha256']:raise ValueError('Neutral native changed')
    bpy.ops.wm.open_mainfile(filepath=str(source/'neutral-look-master.blend'),load_ui=False,use_scripts=False)
    check_protected()
    with np.load(source/'neutral-surfaces.npz',allow_pickle=False) as ref:
        actual=evaluated_surfaces(ref.files);neutral_errors={key:float(np.max(abs(actual[key]-ref[key]))) for key in ref.files}
    if max(neutral_errors.values())>2e-5:raise ValueError('Fresh-open neutral surfaces differ')
    fit_render(out,'reopened-neutral-front',0,(0,.15,-1.7),8.,(640,640))
    unpacked=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not im.packed_files]
    if unpacked:raise ValueError('Neutral image dependencies are not packed')
    (out/'result.json').write_text(json.dumps({'shot_sha256':record['shot_sha256'],'neutral_sha256':record['neutral_sha256'],
        'moving_surface_errors':errors,'neutral_surface_errors':neutral_errors,'camera_reuse_geometry_error':reuse_error,
        'camera_proof_errors':camera_errors,
        'packed_images':True,'local_cache_paths':True,'protected_exact':True,'visual_gate':'NOT_RUN',
        'reuse_scope':'Opposite-side camera without rebuilding actor or resimulating cloth; new performances still require resimulation'},indent=2)+'\n')


def compatible_rest(proof):
    for name in ('head_matrices','chest_matrices'):
        q=np.asarray(proof[name])
        if q.shape!=(360,4,4) or not np.isfinite(q).all() or np.max(abs(q[0]-q[168]))>1e-7:
            raise ValueError('Settled cloth is not in the neutral upper-body frame')


def neutral_state():
    import bpy
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_gallop import JOINED_TRAJECTORY_SHA,JOINED_PROOF_SHA
    source=BASE/'wardrobe185-gallopcloth05/trajectory.npz';proof=source.parent/'motion-proof.npz'
    if digest(source)!=JOINED_TRAJECTORY_SHA or digest(proof)!=JOINED_PROOF_SHA:raise ValueError('Neutral drape input changed')
    with np.load(proof,allow_pickle=False) as data:compatible_rest(data)
    with np.load(source,allow_pickle=False) as data:points=data['frames'][168]
    scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    rig=bpy.data.objects['MF_body156_fit_rig'];rig.animation_data_clear()
    cloth=bpy.data.objects['MF185_moving_shawl']
    if np.max(abs(np.array(cloth.matrix_world)-np.eye(4)))>1e-7 or len(cloth.data.vertices)!=len(points):raise ValueError('Unexpected neutral cloth transform/topology')
    cloth.data=cloth.data.copy()
    for mod in list(cloth.modifiers):
        if mod.type=='MESH_CACHE':cloth.modifiers.remove(mod)
    cloth.data.vertices.foreach_set('co',points.astype(np.float32).ravel());cloth.data.update()
    cloth['qualification']='Frozen neutral drape; new motion requires the preserved cloth recipe and resimulation'
    for ob in scene.objects:
        if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):ob.hide_render=True;ob.hide_viewport=True
        if 'buckle' in ob.name and ob.animation_data:ob.animation_data_clear()
    scene.frame_start=scene.frame_end=1;bpy.context.view_layer.update();check_protected()
    return {'neutral_frame':1,'cloth_settle_frame':169,'upper_frame_parity':True,'new_motion_requires_resimulation':True}
