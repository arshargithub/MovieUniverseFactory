"""Required riding proof for the recut, explicitly supported double wrap.

Reuse the admitted rider/contact action and lower assembly unchanged. Only
shawl construction changes. This produces diagnostic evidence, not approval.
"""
import json
from pathlib import Path
import numpy as np

STATIC_SHA='862a828f2d2de822929e7e55d37eacaa14b5a9a3c66abbd0daace9a217ee3864'
CONSTRUCTION_SHA='35e3c7a3cc1aa08a6da129d812c88404da70a10c34817c993f3509f2714b6a47'
MOTION_SHA='0c24c8e25c7e4f0e7c4aedb6511a038ba08b85d99436e452dd8914aea49caa74'
OFF_SHA='2d91d0978a038496658b7320dc73acef2c1064eaf55baf6a88ec4bc6c672a484'
REVIEW_SHA='72568c5841436b86b212761c3a89e50a913ac339cc69c7b9d6c44fc1fa19cdca'


def support_selection(ids,weights):
    """Release three medial shoulder points incompatible with arm motion.

    The central shoulder attachment and other six patch vertices remain;
    removed points become free cloth, never collision exemptions.
    """
    mask=~np.isin(ids,[4255,4256,4276])
    if len(ids)!=97 or np.count_nonzero(~mask)!=3:raise ValueError('Unexpected shoulder attachment semantics')
    return ids[mask],weights[mask]


def inputs():
    from wardrobe_motion178 import BASE,digest
    folder=BASE/'wardrobe185-redress04'
    for name,sha in (('redressed.npz',STATIC_SHA),('construction.npz',CONSTRUCTION_SHA)):
        if digest(folder/name)!=sha:raise ValueError('Unbound recut input')
    with np.load(folder/'redressed.npz',allow_pickle=False) as data:
        p=data['frames'][-1];f=data['faces'];rest=data['rest'];counts=data['counts']
    with np.load(folder/'construction.npz',allow_pickle=False) as data:
        ids=data['pin_indices'];weights=data['pin_weights'];stitches=data['stitches']
    if p.shape!=(7205,3) or len(ids)!=97 or not np.isfinite(p).all():raise ValueError('Unexpected recut construction')
    return p,f,rest,counts,ids,weights,stitches


def solve(out):
    import bpy
    from mathutils import Vector,Matrix
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_motion import SCALE,hold_preflight
    from wardrobe185_gallop import PREP_SHA,apparent_airflow
    from wardrobe185_convex import solver_contacts,bind_regions,CONTACT_SHA,RIDER07_SHA
    from wardrobe_doublewrap185 import cloth_settings
    from wardrobe_shawl180 import measures
    p,f,rest,counts,ids,weights,stitches=inputs()
    revised=out.name.endswith(('redressmotion02','redressoff02'))
    if revised:ids,weights=support_selection(ids,weights)
    library=BASE/'wardrobe185-gallopprep03/motion-rig.blend'
    if digest(library)!=PREP_SHA:raise ValueError('Changed canonical rig')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    (out/'construction-binding.json').write_text(json.dumps({'static_sha256':STATIC_SHA,'construction_sha256':CONSTRUCTION_SHA,
        'contact_sha256':CONTACT_SHA,'rider_sha256':RIDER07_SHA,'scope':'Recut shawl only; protected actor and lower assembly unchanged'},indent=2)+'\n')
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene.render.fps=24;scene.gravity=(0,0,-9.81);scene.unit_settings.scale_length=1.
    with bpy.data.libraries.load(str(library),link=False) as (_,loaded):loaded.objects=['MF178_metres_rig']
    rig=loaded.objects[0];scene.collection.objects.link(rig)
    union,contacts=solver_contacts(rig,out,SCALE)
    domain=bpy.data.collections.new('Exact regional moving contacts');scene.collection.children.link(domain)
    for ob in contacts:
        domain.objects.link(ob);ob.modifiers.new('Collision','COLLISION');ob.collision.thickness_outer=.0015;ob.collision.cloth_friction=15
    bpy.ops.object.effector_add(type='WIND',location=(4*SCALE,-3*SCALE,0))
    wind=bpy.context.object;wind.name='MF185_recut_apparent_airflow'
    wind.rotation_euler=Vector(apparent_airflow(217)[0]).to_track_quat('Z','Y').to_euler()
    gain=0. if out.name.endswith(('redressoff01','redressoff02')) else 1.
    for frame in list(range(1,361,4))+[360]:
        wind.field.strength=apparent_airflow(frame)[1]*gain;wind.keyframe_insert(data_path='field.strength',frame=frame)
    scene.frame_set(1)
    mesh=bpy.data.meshes.new('Recut scarf');mesh.from_pydata((p*SCALE).tolist(),stitches.tolist(),f.tolist());mesh.update()
    ob=bpy.data.objects.new('MF185_recut_simulation',mesh);scene.collection.objects.link(ob)
    bind_regions(ob,rig,2501,rear_on_head=True)
    group=ob.vertex_groups.new(name='support')
    for i,w in zip(ids,weights):group.add([int(i)],float(w),'REPLACE')
    ob.shape_key_add(name='Basis');metric=ob.shape_key_add(name='Developable fabric metrics')
    metric.data.foreach_set('co',(rest*SCALE).astype(np.float32).ravel())
    metric.value=0.;ob.active_shape_key_index=0;ob.show_only_shape_key=False
    weld=ob.modifiers.new('Verified rest metric evaluation','WELD');weld.merge_threshold=1e-6
    hold_preflight(ob,contacts,dict(zip(ids.tolist(),weights.tolist())),out,SCALE,dense=revised)
    mod=cloth_settings(ob,1,domain);s=mod.settings;s.rest_shape_key=metric;s.use_dynamic_mesh=False
    s.mass=.3;s.air_damping=.2;s.bending_stiffness=.05;s.tension_stiffness=200;s.compression_stiffness=200;s.shear_stiffness=100;s.quality=24
    s.use_sewing_springs=True;s.sewing_force_max=20.;mod.point_cache.frame_end=360
    frames=[];matrices={'chest':[],'head':[]};metrics=[]
    edges=np.unique(np.sort(np.concatenate([f[:,[i,(i+1)%4]] for i in range(4)]),axis=1),axis=0)
    rest_lengths=np.linalg.norm(rest[edges[:,0]]-rest[edges[:,1]],axis=1)
    for frame in range(1,361):
        scene.frame_set(frame);bpy.context.view_layer.update()
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();q=np.array([v.co[:] for v in m.vertices])/SCALE;ev.to_mesh_clear()
        if q.shape!=p.shape or not np.isfinite(q).all() or abs(q).max()>30:
            np.savez_compressed(out/'failed-prefix.npz',frames=np.array(frames),points=q)
            raise ValueError('Invalid recut moving cloth at '+str(frame))
        frames.append(q)
        ratios=np.linalg.norm(q[edges[:,0]]-q[edges[:,1]],axis=1)/rest_lengths
        metrics.append({'frame':frame,'p99':float(np.quantile(ratios,.99)),'max':float(ratios.max())})
        if frame>=169 and metrics[-1]['p99']>2:
            np.savez_compressed(out/'failed-prefix.npz',frames=np.array(frames))
            (out/'failure.json').write_text(json.dumps({'reason':'Severe fabric distortion','metric':metrics[-1]})+'\n')
            raise ValueError('Recut fabric distortion exceeds required-pose guard')
        for label,name in (('chest','chest'),('head','MF185_head')):
            bone=rig.pose.bones[name];delta=rig.matrix_world@bone.matrix@bone.bone.matrix_local.inverted()@rig.matrix_world.inverted()
            matrices[label].append(np.array(Matrix.Scale(1/SCALE,4)@delta@Matrix.Scale(SCALE,4)))
        if frame%24==0:print('185 recut motion',frame,flush=True)
    frames=np.array(frames)
    np.savez_compressed(out/'trajectory.npz',frames=frames,points=p,faces=f,rest=rest,counts=counts,pin_indices=ids,pin_weights=weights)
    np.savez_compressed(out/'motion-proof.npz',**{k+'_matrices':np.array(v) for k,v in matrices.items()})
    record={'fabric_metric':measures(rest,f,{n:frames[n-1] for n in (169,193,217,265,360)},SCALE),
        'wind_gain':gain,'wind_is_calibrated_velocity':False,'visual_gate':'NOT_RUN','actor_loaded':False,
        'trajectory_sha256':digest(out/'trajectory.npz')}
    (out/'frame-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    if gain==0:
        source=BASE/('wardrobe185-redressmotion02/trajectory.npz' if revised else 'wardrobe185-redressmotion01/trajectory.npz')
        if MOTION_SHA is None or digest(source)!=MOTION_SHA:raise ValueError('Unbound wind-on control')
        with np.load(source,allow_pickle=False) as data:on=data['frames']
        error=float(abs(on[:169]-frames[:169]).max());record['prewind_error_native']=error
        record['final_on_off_m_quantiles']=np.quantile(np.linalg.norm(on[-1]-frames[-1],axis=1)*SCALE,[.5,.95,1]).tolist()
        if error>1e-7:raise ValueError('Wind control differs before airflow')
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')


def screen(out):
    import bpy
    from mathutils import Vector
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import REPAIRED_SHA
    from wardrobe_shawl180_cache import cache
    from wardrobe185_finish import apply
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-lowerreview07/integration-working.blend'
    control=out.name.endswith('redressoffreview02')
    trace=BASE/('wardrobe185-redressoff02/trajectory.npz' if control else 'wardrobe185-redressmotion02/trajectory.npz' if out.name.endswith('redressreview02') else 'wardrobe185-redressmotion01/trajectory.npz')
    sha=OFF_SHA if control else MOTION_SHA
    if digest(source)!=REPAIRED_SHA or sha is None or digest(trace)!=sha:raise ValueError('Unbound recut review')
    with np.load(trace,allow_pickle=False) as data:frames=data['frames'];rest=data['rest'];counts=data['counts']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);check_protected()
    scene=bpy.context.scene;cloth=bpy.data.objects['MF185_moving_shawl']
    for mod in list(cloth.modifiers):
        if mod.type=='MESH_CACHE':cloth.modifiers.remove(mod)
    mod=cache(cloth,frames,out/'cloth.mdd');bpy.context.view_layer.objects.active=cloth
    while list(cloth.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    while len(cloth.data.materials)>1:cloth.data.materials.pop(index=len(cloth.data.materials)-1)
    apply(cloth,rest,counts,out)
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    horse=[(o,o.hide_render) for o in scene.objects if o.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_'))]
    for o,_ in horse:o.hide_render=True
    rig=bpy.data.objects['MF_body156_fit_rig']
    for frame in ((217,265,360) if control else (169,193,217,265,360)):
        scene.frame_set(frame);bpy.context.view_layer.update()
        center=tuple(rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-1.4)))
        for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):fit_render(out,label+'-'+str(frame),angle,center,9.,(640,640))
    for o,state in horse:o.hide_render=state
    scene.frame_set(217);check_protected()
    if not control:bpy.ops.wm.save_as_mainfile(filepath=str(out/'integration-working.blend'),check_existing=False,compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':REPAIRED_SHA,'trajectory_sha256':sha,
        'native_sha256':None if control else digest(out/'integration-working.blend'),'visual_gate':'NOT_RUN','protected_exact':True},indent=2)+'\n')
