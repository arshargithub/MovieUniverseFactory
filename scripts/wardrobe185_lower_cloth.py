"""Free lower-tunic cloth with a supported waist and actual moving contacts.

Standing and mounted dressing are separate solves. No mounting transition,
calibrated textile density, general-purpose garment rig or visual pass implied.
"""
import json
from pathlib import Path
import numpy as np

LAYOUT_SHA='2ed3c210125f020c6e361b0d573136675f5e49decb82fe5b165e31306aae7f4e'
WAIST_LAYOUT_SHA='6409b42c2d04cd37d22035146ef2c5566da9d92a011f4f3e62129fccd07d7f80'
BELT_LAYOUT_SHA='0cee805f1e5f54aaef195280a408872da200d68f9b496fb2389342dc062cfbdc'


def sample(ob):
    import bpy
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    q=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',q);ev.to_mesh_clear()
    return q.reshape(-1,3).astype(float)


def panel(name,p,faces):
    import bpy
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(p.tolist(),[],faces.tolist());mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(ob)
    return ob


def profile(ob,domain=None):
    from wardrobe_doublewrap185 import cloth_settings
    mod=cloth_settings(ob,1,domain);s=mod.settings
    s.mass=.3;s.air_damping=.2;s.bending_stiffness=.05
    s.tension_stiffness=200;s.compression_stiffness=200;s.shear_stiffness=100;s.quality=24
    s.use_dynamic_mesh=False
    return mod


def metric_control(out):
    """Prove authored metric survives this exact MDD + weld + cloth stack."""
    import bpy
    from wardrobe_shawl180_cache import cache
    from wardrobe_motion178 import sheet_grid
    result={}
    for shrink in (False,True):
        bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.gravity=(0,0,0)
        p,f=sheet_grid(9,9,lambda u,v:(.4*u,.4*v,1.));p=np.array(p);f=np.array(f)
        ob=panel('metric',p,f);ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Rest fabric')
        rest=p.copy()
        if shrink:rest[:,:2]*=.5
        key.data.foreach_set('co',rest.astype(np.float32).ravel());key.value=0
        group=ob.vertex_groups.new(name='support');group.add([0],1.,'REPLACE')
        cache(ob,np.repeat(p[None,:,:],48,axis=0),out/('unit-'+str(shrink)+'.mdd'))
        weld=ob.modifiers.new('Explicit rest evaluation','WELD');weld.merge_threshold=1e-7
        mod=profile(ob);mod.settings.rest_shape_key=key;mod.collision_settings.use_self_collision=False
        for frame in range(1,49):scene.frame_set(frame);bpy.context.view_layer.update();q=sample(ob)
        result[str(shrink)]=np.ptp(q,axis=0).tolist()
    (out/'rest-metric-control.json').write_text(json.dumps(result,indent=2)+'\n')
    ratio=np.array(result['True'])[:2]/np.array(result['False'])[:2]
    if not np.all((ratio>.35)&(ratio<.65)):raise ValueError('Cache stack does not preserve authored fabric metric')


def solve(out):
    import bpy
    from mathutils import Vector
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_lower_drape import SCALE,SURFACE_SHA,SOURCE_SHA,WAIST_SURFACE_SHA
    from wardrobe_shawl180_cache import cache
    from wardrobe185_gallop import apparent_airflow
    layout=BASE/'wardrobe185-lowerdress07/initial-layout.npz'
    contacts=BASE/'wardrobe185-lowersurface02/surfaces.npz'
    source=BASE/'wardrobe185-lowercapture02/moving-source.npz'
    convergence=out.name.endswith('lowercloth04')
    belt_bound=convergence or out.name.endswith('lowercloth03')
    waist=belt_bound or out.name.endswith('lowercloth02');layout_sha=LAYOUT_SHA;contact_sha=SURFACE_SHA
    if waist:
        layout=BASE/'wardrobe185-lowerdress09/initial-layout.npz';layout_sha=WAIST_LAYOUT_SHA
        contacts=BASE/'wardrobe185-waistcontact01/contact.npz';contact_sha=WAIST_SURFACE_SHA
    if belt_bound:layout=BASE/'wardrobe185-lowerdress10/initial-layout.npz';layout_sha=BELT_LAYOUT_SHA
    for p,h in ((layout,layout_sha),(contacts,contact_sha),(source,SOURCE_SHA)):
        if h is None or digest(p)!=h:raise ValueError('Unbound lower cloth input')
    if json.loads((layout.parent/'result.json').read_text())['admission']!='PASS':raise ValueError('Initial lower cloth not admitted')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(layout,allow_pickle=False) as d:cut={k:d[k] for k in d.files}
    with np.load(contacts,allow_pickle=False) as d:contact={k:d[k] for k in d.files}
    with np.load(source,allow_pickle=False) as d:pelvis=d['pelvis_matrices']
    metric_control(out)
    record={};outputs={};faces=cut['faces'];rest=cut['rest'];pins=cut['pin_indices'];weights=cut['pin_weights']
    for label in ('standing','mounted'):
        bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
        scene.render.fps=24;scene.unit_settings.scale_length=1.;scene.gravity=(0,0,-9.81)
        frames=np.ones(120,dtype=int) if label=='standing' else np.r_[np.full(120,169),np.arange(170,361)]
        source_ids={int(v):i for i,v in enumerate(contact['frame_ids'])};contact_ids=[source_ids[int(v)] for v in frames]
        p=cut[label];ob=panel('MF185_lower_cloth',p*SCALE,faces)
        ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Unstressed cut')
        key.data.foreach_set('co',(rest*SCALE).astype(np.float32).ravel());key.value=0
        group=ob.vertex_groups.new(name='support')
        for i,w in zip(pins,weights):group.add([int(i)],float(w),'REPLACE')
        drive=np.repeat(p[None,:,:],len(frames),axis=0)
        start=frames[0]-1;offset=p[pins]-cut['guided'][start,pins]
        local=offset@np.linalg.inv(pelvis[start,:3,:3]).T
        for j,frame in enumerate(frames):
            drive[j,pins]=cut['guided'][frame-1,pins]+local@pelvis[frame-1,:3,:3].T
        cache(ob,drive*SCALE,out/(label+'-support.mdd'))
        weld=ob.modifiers.new('Explicit rest evaluation','WELD');weld.merge_threshold=1e-7
        domain=bpy.data.collections.new('Actual lower contacts');scene.collection.children.link(domain)
        names=('pants',) if label=='standing' else ('pants','horse','saddle','pad')
        if waist:names=names+('waist',)
        for name in names:
            samples=contact[name+'_frames'][contact_ids]*SCALE
            co=panel('MF185_contact_'+name,samples[0],contact[name+'_faces']);domain.objects.link(co)
            cache(co,samples,out/(label+'-'+name+'.mdd'))
            co.modifiers.new('Actual moving collision','COLLISION')
            co.collision.thickness_outer=.0015;co.collision.cloth_friction=15
        mod=profile(ob,domain);mod.settings.rest_shape_key=key;mod.point_cache.frame_end=len(frames)
        if convergence:
            # Numerical refinement only: unchanged cut, contacts, material,
            # wind and supports distinguish resolution from design changes.
            mod.settings.quality=48;mod.collision_settings.collision_quality=8
        if label=='mounted':
            bpy.ops.object.effector_add(type='WIND');wind=bpy.context.object
            wind.rotation_euler=Vector(apparent_airflow(217)[0]).to_track_quat('Z','Y').to_euler()
            for i,source_frame in enumerate(frames):
                wind.field.strength=apparent_airflow(int(source_frame))[1];wind.keyframe_insert(data_path='field.strength',frame=i+1)
        trajectory=[]
        for frame in range(1,len(frames)+1):
            scene.frame_set(frame);bpy.context.view_layer.update();q=sample(ob)/SCALE
            if q.shape!=p.shape or not np.isfinite(q).all():raise ValueError('Invalid lower free cloth output')
            trajectory.append(q)
            if frame%24==0:print('185 lower cloth',label,frame,flush=True)
        trajectory=np.array(trajectory);outputs[label]=trajectory
        edges=np.unique(np.sort(np.concatenate([faces[:,[i,(i+1)%4]] for i in range(4)]),axis=1),axis=0)
        lengths=np.linalg.norm(rest[edges[:,0]]-rest[edges[:,1]],axis=1)
        ratios=np.linalg.norm(trajectory[:,edges[:,0]]-trajectory[:,edges[:,1]],axis=2)/lengths
        record[label]={'physics_frames':len(frames),'source_frame_ids':frames.tolist(),
            'quality_steps':mod.settings.quality,'collision_quality':mod.collision_settings.collision_quality,
            'maximum_edge_ratio':float(ratios.max()),'last_edge_quantiles':np.quantile(ratios[-1],[.01,.5,.99,1]).tolist(),
            'free_cloth':True,'mass_per_vertex_authored_not_calibrated':.3,'visual_gate':'NOT_RUN'}
        np.savez_compressed(out/(label+'.npz'),frames=trajectory,source_frame_ids=frames,faces=faces,rest=rest,pin_indices=pins)
        (out/'progress.json').write_text(json.dumps(record,indent=2)+'\n')
    for p,h in ((layout,layout_sha),(contacts,contact_sha),(source,SOURCE_SHA)):
        if digest(p)!=h:raise ValueError('Lower cloth changed an input')
    (out/'result.json').write_text(json.dumps({'layout_sha256':layout_sha,'contacts_sha256':contact_sha,
        'cases':record,'inputs_unchanged':True,'accepted_masters_not_opened':True,'visual_gate':'NOT_RUN',
        'scope':'Separate free standing/mounted lower cloth; not a mounting animation or final character pass'},indent=2)+'\n')
