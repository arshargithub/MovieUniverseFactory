"""Fixed differential controls for Director186; no runtime-generated code."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe_motion178 as base

SOURCE = base.BASE / 'wardrobe185-redressreview02/integration-working.blend'
SOURCE_SHA = '72568c5841436b86b212761c3a89e50a913ac339cc69c7b9d6c44fc1fa19cdca'
OPERATIONS = ('inspect01','controls02','repair03','audit04','verify05','delivery06','motion06','reopen06')
REPAIR_SHA='773f68b4094fd061db41ed393a7695356f63db916dd0eebdf0e9534514001c40'


def evaluated(ob):
    import bpy
    import numpy as np
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    values=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',values)
    ev.to_mesh_clear();return values.reshape((-1,3))


def delivery(out):
    import bpy
    import numpy as np
    from mathutils import Vector
    from wardrobe185_delivery import camera_keys,samples
    from wardrobe185_shot import setup_lighting
    from wardrobe_riding_fit import fit_render
    candidate=base.BASE/'wardrobe186-repair03/candidate.blend'
    if base.digest(candidate)!=REPAIR_SHA:raise ValueError('Candidate changed')
    verification=json.loads((base.BASE/'wardrobe186-verify05/result.json').read_text())
    if max(r['outside_vertices'] for r in verification['contact_coverage'] if r['frame']>=217):raise ValueError('New riding support escapes cloth collision')
    bpy.ops.wm.open_mainfile(filepath=str(candidate),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig'];base.check_protected()
    scene.frame_set(265);bpy.context.view_layer.update();scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    visibility={o.name:o.hide_render for o in scene.objects}
    for ob in scene.objects:
        if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):ob.hide_render=True
    center=tuple(rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-1.4)))
    fit_render(out,'repaired-original-light-front',0,center,8.,(640,640))
    for ob in scene.objects:ob.hide_render=visibility[ob.name]
    setup_lighting(scene);fill_light(scene)
    proof=json.loads((base.BASE/'wardrobe185-seal02/camera-proof.json').read_text())
    scene.camera.animation_data_clear();scene.camera.data.type='PERSP';scene.camera.data.lens=42
    scene.camera.data.sensor_fit='VERTICAL';scene.camera.data.sensor_height=24;scene.camera.data.dof.use_dof=False
    for row in camera_keys(proof):
        scene.camera.location=Vector(row['position']);scene.camera.rotation_euler=(Vector(row['target'])-scene.camera.location).to_track_quat('-Z','Y').to_euler()
        scene.camera.keyframe_insert(data_path='location',frame=row['frame']);scene.camera.keyframe_insert(data_path='rotation_euler',frame=row['frame'])
    # Reuse the immutable15 cache files in the existing local bundle; this is a
    # declared dependency, not a new standalone/export package or media backup.
    dependencies=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type!='MESH_CACHE':continue
            old=Path(bpy.path.abspath(m.filepath)).resolve()
            if not old.is_relative_to(base.BASE):raise ValueError('Cache outside scoped asset')
            digest=base.digest(old);cached=base.BASE/'wardrobe185-seal02/cache'/(digest+'.mdd')
            if not cached.is_file() or base.digest(cached)!=digest:raise ValueError('Missing shared sealed cache')
            m.filepath=str(cached);dependencies.append({'object':ob.name,'sha256':digest,'path':'../wardrobe185-seal02/cache/'+cached.name})
    np.savez_compressed(out/'surface-proof.npz',**samples())
    for text in bpy.data.texts:text.use_module=False
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.render.fps=24;scene.frame_start=217;scene.frame_end=360;scene.frame_set(325)
    scene.render.filepath='//renders/frame-';scene.cycles.samples=4
    scene['MF186_status']='Internal correction; Director acceptance and final trailer context pending'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'riding-corrected.blend'),compress=True)
    bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'riding-corrected.blend'),compress=True)
    record={'native_sha256':base.digest(out/'riding-corrected.blend'),'repair_sha256':REPAIR_SHA,'shared_cache_dependencies':dependencies,
            'standing_master':'../wardrobe185-seal02/neutral-look-master.blend','visual_gate':'NOT_RUN','director_acceptance':'PENDING',
            'scope':'Moving arm correction and broad fill; static anatomy, action, head/hair and cloth caches preserved; dependent local derivative, not standalone export'}
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')


def delivered():
    folder=base.BASE/'wardrobe186-delivery06';record=json.loads((folder/'result.json').read_text())
    native=folder/'riding-corrected.blend'
    if base.digest(native)!=record['native_sha256']:raise ValueError('Delivered native changed')
    return folder,native,record


def motion(out):
    import bpy
    from wardrobe185_shot import setup_camera
    _,native,record=delivered();bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.camera.animation_data_clear();rig=bpy.data.objects['MF_body156_fit_rig']
    scene.cycles.device='CPU';scene.cycles.samples=4;scene.render.use_persistent_data=True
    poses=[]
    for frame in range(217,361):
        scene.frame_set(frame);bpy.context.view_layer.update();poses.append(setup_camera(scene,rig,frame))
        scene.render.filepath=str(out/('frame-%04d.png'%frame));bpy.ops.render.render(write_still=True)
    base.check_protected()
    (out/'motion-render.json').write_text(json.dumps({'native_sha256':record['native_sha256'],'poses':poses,'visual_gate':'NOT_RUN','frame_range':[217,360],'fps':24},indent=2)+'\n')


def reopen(out):
    import bpy
    import numpy as np
    from mathutils import Vector, Matrix
    from wardrobe185_delivery import samples
    from wardrobe_riding_fit import fit_render
    folder,native,record=delivered()
    for row in record['shared_cache_dependencies']:
        path=(folder/row['path']).resolve()
        if not path.is_relative_to(base.BASE) or base.digest(path)!=row['sha256']:raise ValueError('Cache dependency changed')
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    base.check_protected();actual=samples()
    with np.load(folder/'surface-proof.npz',allow_pickle=False) as data:
        errors={k:float(abs(actual[k]-data[k]).max()) for k in data.files}
    if max(errors.values())>2e-5:raise ValueError('Reopened surface mismatch')
    scene=bpy.context.scene;scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.cycles.samples=8;scene.cycles.device='CPU';scene.render.use_persistent_data=True
    for ob in scene.objects:
        if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):ob.hide_render=True
    rig=bpy.data.objects['MF_body156_fit_rig'];bounce=bpy.data.objects['MF186_bounce']
    for frame in (217,223,265,360):
        scene.frame_set(frame);bpy.context.view_layer.update();center=rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-1.4))
        for angle,label in ((0,'front'),(90,'left'),(270,'right')):
            rot=Matrix.Rotation(np.radians(angle),3,'Z');bounce.location=center+rot@Vector((0,-10,-1.5));bounce.rotation_euler=(center-bounce.location).to_track_quat('-Z','Y').to_euler()
            fit_render(out,label+'-'+str(frame),angle,center,8.,(640,640))
    (out/'result.json').write_text(json.dumps({'native_sha256':record['native_sha256'],'surface_errors':errors,'protected_exact':True,'visual_gate':'NOT_RUN'},indent=2)+'\n')


def verify(out):
    """Independent complete scene loads, not a partially remapped append rig."""
    import bpy
    import numpy as np
    from wardrobe_motion178_controls import render_geometry_paused
    candidate=base.BASE/'wardrobe186-repair03/candidate.blend'
    if base.digest(candidate)!=REPAIR_SHA:raise ValueError('Candidate changed')
    frames=(1,169,193,217,220,223,226,265,326,360)
    before={};rows=[]
    for stage,path in (('before',SOURCE),('after',candidate)):
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
        body=bpy.data.objects['MF_studio_adult_body'];scene=bpy.context.scene
        for m in body.modifiers:
            if m.type=='SUBSURF':m.show_viewport=False
        rest=np.array([v.co[:] for v in body.data.vertices])
        head=rest[:,2]>-1.35
        non_arm=(abs(rest[:,0])<1.0)|(rest[:,2]<-4)
        with render_geometry_paused():
            body.hide_viewport=False
            for frame in frames:
                scene.frame_set(frame);bpy.context.view_layer.update();q=evaluated(body)
                if not np.isfinite(q).all() or abs(q).max()>30:raise ValueError('Invalid independent body evaluation')
                if stage=='before':before[frame]=q.copy();continue
                delta=np.linalg.norm(q-before[frame],axis=1)
                row={'frame':frame,'max_delta_native':float(delta.max()),'head_delta_native':float(delta[head].max()),'central_or_distal_delta_native':float(delta[non_arm].max())}
                rows.append(row);print('INDEPENDENT',row,flush=True)
        base.check_protected()
    if rows[0]['max_delta_native']>2e-5:raise ValueError('Neutral changed')
    if max(r['head_delta_native'] for r in rows)>2e-5:raise ValueError('Head changed')
    # Exact old collision geometry may be reused only if the corrected support
    # remains covered. Inspect the complete moving upper-body clock, not one pose.
    body=bpy.data.objects['MF_studio_adult_body'];tunic=bpy.data.objects['MF185_fitted_upper_tunic']
    for m in tunic.modifiers:
        if m.type in ('SUBSURF','SOLIDIFY'):m.show_viewport=False
    rest=np.array([v.co[:] for v in body.data.vertices]);arm=(abs(rest[:,0])>1.25)&(rest[:,2]>-3.6)&(rest[:,2]<-1.5)
    rest=np.array([v.co[:] for v in tunic.data.vertices]);sleeve=(abs(rest[:,0])>1.25)&(rest[:,2]>-3.6)&(rest[:,2]<-1.5)
    contact_path=base.BASE/'wardrobe185-convexcontact04/contact.npz'
    from wardrobe185_convex import CONTACT_SHA
    if base.digest(contact_path)!=CONTACT_SHA:raise ValueError('Contact changed')
    with np.load(contact_path,allow_pickle=False) as d:contacts={k:d[k] for k in d.files}
    planes={}
    for key in ('torso','armL','armR'):
        p=contacts[key+'_points'];tri=p[contacts[key+'_faces']]
        n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
        n[np.einsum('ij,ij->i',n,tri[:,0]-p.mean(0))<0]*=-1
        planes[key]=(n,np.einsum('ij,ij->i',n,tri[:,0]))
    coverage=[]
    with render_geometry_paused():
        body.hide_viewport=False;tunic.hide_viewport=False
        for frame in range(170,361):
            scene.frame_set(frame);bpy.context.view_layer.update()
            points=np.concatenate((evaluated(body)[arm],evaluated(tunic)[sleeve]));outside=np.full(len(points),np.inf)
            for key,(n,d) in planes.items():
                inverse=np.linalg.inv(contacts[key+'_matrices'][frame-1]);q=points@inverse[:3,:3].T+inverse[:3,3]
                outside=np.minimum(outside,np.max(q@n.T-d,axis=1))
            coverage.append({'frame':frame,'max_outside_native':float(outside.max()),'outside_vertices':int(np.count_nonzero(outside>1e-5))})
            if frame%24==0:print('CONTACT',coverage[-1],flush=True)
    record={'independent_comparison':rows,'contact_coverage':coverage,'source_sha256':REPAIR_SHA,'visual_gate':'NOT_RUN',
            'scope':'Coarse visible support vertex containment; unchanged rest and bone motion; actual rendered garment contacts still require visual inspection',
            'supersedes':'audit04 appended-control body comparison is invalid; full scene dependencies required'}
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')


def fill_light(scene):
    import bpy
    from mathutils import Vector
    lights=[o for o in scene.objects if o.name.startswith('MF_body156_softbox')]
    data=bpy.data.lights.new('186 broad frontal bounce','AREA')
    data.energy=sum(o.data.energy for o in lights)*.22;data.shape='DISK';data.size=9
    ob=bpy.data.objects.new('MF186_bounce',data);scene.collection.objects.link(ob)
    ob.location=(0,-12,-4);ob.rotation_euler=(Vector((0,-2,-3))-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob


def audit(out):
    import bpy
    import numpy as np
    from mathutils import Vector, Matrix
    from wardrobe_riding_fit import fit_render
    from wardrobe_motion178_controls import render_geometry_paused
    candidate=base.BASE/'wardrobe186-repair03/candidate.blend'
    if base.digest(candidate)!=REPAIR_SHA:raise ValueError('Repair source changed')
    bpy.ops.wm.open_mainfile(filepath=str(candidate),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig']
    with bpy.data.libraries.load(str(SOURCE),link=False) as (_,loaded):loaded.objects=['MF_studio_adult_body']
    control=loaded.objects[0];scene.collection.objects.link(control);control.hide_render=True
    control.parent=rig;control.matrix_world=body.matrix_world.copy()
    for mod in control.modifiers:
        if mod.type=='ARMATURE':mod.object=rig
    points=np.array([v.co[:] for v in body.data.vertices]);arm=(abs(points[:,0])>1.25)&(points[:,2]>-3.6)&(points[:,2]<-1.5)
    clavicle=(abs(points[:,0])<1.15)&(points[:,2]>-2.4)&(points[:,2]<-1.72)
    tuning=bpy.data.objects['MF185_fitted_upper_tunic']
    rest=np.array([v.co[:] for v in tuning.data.vertices]);sleeve=(abs(rest[:,0])>1.25)&(rest[:,2]>-3.6)&(rest[:,2]<-1.5)
    frames=sorted(set([1,169,193,216,265,280,326,360]+list(range(217,229))))
    flags=[(m,m.show_viewport) for ob in (body,control,tuning) for m in ob.modifiers if m.type in ('SUBSURF','SOLIDIFY')]
    contacts_path=base.BASE/'wardrobe185-convexcontact04/contact.npz'
    from wardrobe185_convex import CONTACT_SHA
    if base.digest(contacts_path)!=CONTACT_SHA:raise ValueError('Changed contact input')
    with np.load(contacts_path,allow_pickle=False) as d:contacts={k:d[k] for k in d.files}
    planes={}
    for key in ('torso','armL','armR'):
        p=contacts[key+'_points'];f=contacts[key+'_faces'];tri=p[f]
        n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
        n[np.einsum('ij,ij->i',n,tri[:,0]-p.mean(0))<0]*=-1
        planes[key]=(n,np.einsum('ij,ij->i',n,tri[:,0]))
    rows=[]
    def q(ob):
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();a=np.array([v.co[:] for v in mesh.vertices]);ev.to_mesh_clear();return a
    try:
        for m,_ in flags:m.show_viewport=False
        with render_geometry_paused():
            for ob in (body,control,tuning):ob.hide_viewport=False
            for frame in frames:
                scene.frame_set(frame);bpy.context.view_layer.update()
                current=q(body);previous=q(control);delta=np.linalg.norm(current-previous,axis=1)
                garment=q(tuning);samples=np.concatenate([current[arm],garment[sleeve]])
                outside=np.full(len(samples),np.inf)
                for key,(n,d) in planes.items():
                    inverse=np.linalg.inv(contacts[key+'_matrices'][frame-1]);local=samples@inverse[:3,:3].T+inverse[:3,3]
                    distance=np.max(local@n.T-d,axis=1);outside=np.minimum(outside,distance)
                row={'frame':frame,'body_max_delta_native':float(delta.max()),'clavicle_max_delta_native':float(delta[clavicle].max()),
                     'upper_support_outside_old_proxy_max_native':float(outside.max()),'outside_vertices':int(np.count_nonzero(outside>1e-5))}
                rows.append(row);print('AUDIT',row,flush=True)
    finally:
        for m,state in flags:m.show_viewport=state
    bpy.data.objects.remove(control,do_unlink=True)
    base.check_protected()
    result={'source_sha256':REPAIR_SHA,'contact_sha256':CONTACT_SHA,'frames':rows,'visual_gate':'NOT_RUN',
            'scope':'Cage vertex containment diagnostic; not full subdivided face contact or temporal qualification'}
    (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO';scene.cycles.device='CPU';scene.cycles.samples=8
    scene.render.use_persistent_data=True;bounce=fill_light(scene)
    for ob in scene.objects:
        if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):ob.hide_render=True
    for frame in (265,193):
        scene.frame_set(frame);bpy.context.view_layer.update();center=rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-1.4))
        for angle,label in ((0,'front'),(90,'left'),(270,'right'),(180,'rear')):
            rot=Matrix.Rotation(np.radians(angle),3,'Z');bounce.location=center+rot@Vector((0,-10,-1.5))
            bounce.rotation_euler=(center-bounce.location).to_track_quat('-Z','Y').to_euler()
            fit_render(out,'filled-'+label+'-'+str(frame),angle,center,8.,(640,640))
    scene.frame_set(265);bpy.context.view_layer.update()
    (out/'lighting.json').write_text(json.dumps({'fill_energy':bounce.data.energy,'size':bounce.data.size,'ratio_to_existing_total':.22,'anatomy_unchanged':True},indent=2)+'\n')


def arm_support(weight):
    """Confine torso-to-arm blending to shoulder, not half the humerus."""
    from wardrobe_motion178_controls import smooth
    return smooth(weight/.65)


def repair(out):
    import bpy
    import numpy as np
    from mathutils import Vector
    from wardrobe_riding_fit import fit_render
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    scene.frame_set(1);bpy.context.view_layer.update()
    # All fitted garments must consume the same repair, including body copies.
    targets=[body]+[o for o in scene.objects if o.name.startswith('MF178_render_deform_target')]
    stats={};processed={}
    for ob in targets:
        if len(ob.data.vertices)!=len(body.data.vertices):raise ValueError('Unexpected body support topology')
        old=ob.data
        if old.name in processed:ob.data=processed[old.name];continue
        ob.data=old.copy();processed[old.name]=ob.data
        bone_groups={g.index:g for g in ob.vertex_groups if g.name in rig.data.bones}
        count=0
        for v in ob.data.vertices:
            weights={bone_groups[g.group].name:g.weight for g in v.groups if g.group in bone_groups}
            arm=sum(w for n,w in weights.items() if n.startswith(('upperarm.','forearm.','hand.','MF_fit_finger')))
            if not 1e-6<arm<1-1e-6:continue
            new=arm_support(arm)
            for n,w in weights.items():
                scale=new/arm if n.startswith(('upperarm.','forearm.','hand.','MF_fit_finger')) else (1-new)/(1-arm)
                ob.vertex_groups[n].add([v.index],w*scale,'REPLACE')
            count+=1
        stats[ob.name]=count
    base.check_protected()
    # Save an unqualified integrated derivative before diagnostic visibility.
    scene.frame_set(265);bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'candidate.blend'))
    visibility={o.name:o.hide_render for o in scene.objects}
    for frame in (1,193,265):
        scene.frame_set(frame);bpy.context.view_layer.update()
        center=tuple(rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-2.4)))
        for mode in ('body','dressed'):
            for ob in scene.objects:
                ob.hide_render=visibility[ob.name]
                if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):ob.hide_render=True
                if mode=='body' and ob!=body and ob.type in ('MESH','CURVE','CURVES') and not ob.name.startswith(('MF_natural','MF_aimable')):ob.hide_render=True
            for angle,label in ((0,'front'),(90,'left'),(270,'right')):
                fit_render(out,f'{mode}-{label}-{frame}',angle,center,10.,(640,640))
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'changed_weights':stats,'candidate_sha256':base.digest(out/'candidate.blend'),'visual_gate':'NOT_RUN','dependent_cloth_admission':'NOT_RUN'},indent=2)+'\n')


def controls(out):
    import bpy
    import numpy as np
    from mathutils import Vector, Matrix
    from wardrobe_riding_fit import fit_render
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig']
    for ob in scene.objects:
        if ob!=body and ob.type in ('MESH','CURVE','CURVES'):ob.hide_render=True
    scene.frame_set(265);bpy.context.view_layer.update()
    center=tuple(rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-2.4)))
    clay=bpy.data.materials.new('186 neutral gray');clay.use_nodes=True
    clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.25,.25,.25,1)
    clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8
    body.data=body.data.copy();body.data.materials.clear();body.data.materials.append(clay)
    for p in body.data.polygons:p.material_index=0
    main=next(m for m in body.modifiers if m.type=='ARMATURE')
    groups={g.index:g.name for g in body.vertex_groups}
    rows=[]
    for low in (-2.2,-2.5,-2.8,-3.1,-3.4):
        verts=[v for v in body.data.vertices if v.co.x>1.4 and low-.15<v.co.z<low+.15]
        rows.append({'z':low,'n':len(verts),'arm_range':[min((sum(g.weight for g in v.groups if groups[g.group].startswith('upperarm.')) for v in verts),default=0),max((sum(g.weight for g in v.groups if groups[g.group].startswith('upperarm.')) for v in verts),default=0)]})
    mods=[m for m in body.modifiers if m.type in ('SMOOTH','CORRECTIVE_SMOOTH')]
    state=[(m,m.show_render,m.show_viewport) for m in mods]
    for variant in ('original','linear','no_fairing'):
        main.use_deform_preserve_volume=variant!='linear'
        for m,r,v in state:m.show_render=False if variant=='no_fairing' else r;m.show_viewport=False if variant=='no_fairing' else v
        for angle,label in ((0,'front'),(90,'left')):fit_render(out,variant+'-'+label,angle,center,10.,(640,640))
    main.use_deform_preserve_volume=True
    for m,r,v in state:m.show_render=r;m.show_viewport=v
    # Identical neutral-to-chest rigid transform for camera and lights removes
    # incident-angle change; the remaining image difference is deformation.
    for frame in (1,265):
        scene.frame_set(frame);bpy.context.view_layer.update()
        chest=rig.pose.bones['chest'];transform=rig.matrix_world@chest.matrix@chest.bone.matrix_local.inverted()@rig.matrix_world.inverted()
        target=transform@Vector((0,.1,-1.65));camera=scene.camera
        camera.data.ortho_scale=5.5;camera.location=transform@Vector((0,-36,-1.05))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        for light,x in zip(sorted((o for o in scene.objects if o.name.startswith('MF_body156_softbox')),key=lambda o:o.name),(-7,7)):
            light.location=transform@Vector((x,-8.9,5.35));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/('chest-relative-'+str(frame)+'.png'));bpy.ops.render.render(write_still=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'upper_arm_weights':rows,'visual_gate':'NOT_RUN'},indent=2)+'\n')


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Fixed operation required')
    if SOURCE.is_symlink() or base.digest(SOURCE) != SOURCE_SHA:
        raise ValueError('Unbound source')
    out = base.BASE / ('wardrobe186-' + job['operation'])
    if out.exists() or out.is_symlink():
        raise ValueError('Preserve previous evidence')
    return out


def inspect(out):
    import bpy
    from mathutils import Vector
    from wardrobe_riding_fit import fit_render
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    scene.camera.animation_data_clear(); scene.camera.data.type = 'ORTHO'
    scene.cycles.device = 'CPU'; scene.cycles.samples = 8
    scene.render.use_persistent_data = True
    body = bpy.data.objects['MF_studio_adult_body']
    rig = bpy.data.objects['MF_body156_fit_rig']
    report = {'source_sha256': SOURCE_SHA, 'objects': {}, 'poses': {}}
    for ob in scene.objects:
        if ob.type != 'MESH' or not (ob == body or 'surface' in ob.name.lower() or 'tunic' in ob.name):
            continue
        report['objects'][ob.name] = {'vertices': len(ob.data.vertices), 'modifiers': [
            {'name': m.name, 'type': m.type, 'viewport': m.show_viewport,
             'render': m.show_render, 'group': getattr(m, 'vertex_group', None),
             'object': getattr(getattr(m, 'object', None), 'name', None),
             'target': getattr(getattr(m, 'target', None), 'name', None)} for m in ob.modifiers]}
    report['shape_keys'] = [(k.name, k.value) for k in body.data.shape_keys.key_blocks] if body.data.shape_keys else []
    # Direct body controls remove clothing, not anatomy. Hair/eyes remain.
    hidden = []
    for ob in scene.objects:
        if ob.hide_render or ob == body or ob.type not in ('MESH','CURVE','CURVES'):
            continue
        if ob.name.startswith(('MF_natural','MF_aimable')):
            continue
        hidden.append(ob.name); ob.hide_render = True
    report['hidden_for_body_control'] = hidden
    original = body.data
    clay = bpy.data.materials.new('186 diagnostic clay'); clay.diffuse_color = (.42,.42,.42,1)
    clay.use_nodes = True
    clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.42,.42,.42,1)
    clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8
    for frame in (1,193,265):
        scene.frame_set(frame); bpy.context.view_layer.update()
        report['poses'][str(frame)] = {b.name: {'head': list(b.head), 'tail': list(b.tail), 'scale': list(b.scale)}
            for b in rig.pose.bones if b.name.startswith(('chest','spine','MF185','upperarm','forearm'))}
        center=tuple(rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-2.4)))
        for material in ('skin','clay'):
            if material == 'clay':
                body.data = original.copy(); body.data.materials.clear(); body.data.materials.append(clay)
                for p in body.data.polygons: p.material_index=0
            for angle,label in ((0,'front'),(90,'left'),(270,'right')):
                fit_render(out, f'{material}-{label}-{frame}', angle, center, 10., (640,640))
            body.data = original
    (out/'result.json').write_text(json.dumps(report, indent=2)+'\n')
    if base.digest(SOURCE) != SOURCE_SHA: raise ValueError('Source changed')


def main():
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1: raise ValueError('One structured job file required')
    job=json.loads(Path(args[0]).read_text());out=validate(job);out.mkdir()
    (out/'handler.py').write_bytes(Path(__file__).read_bytes())
    if job['operation']=='inspect01':inspect(out)
    elif job['operation']=='controls02':controls(out)
    elif job['operation']=='repair03':repair(out)
    elif job['operation']=='audit04':audit(out)
    elif job['operation']=='verify05':verify(out)
    elif job['operation']=='delivery06':delivery(out)
    elif job['operation']=='motion06':motion(out)
    else:reopen(out)


if __name__ == '__main__': main()
