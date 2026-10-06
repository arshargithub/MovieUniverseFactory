"""Transport the successful static trouser contact and inspect its drape."""
import json
from pathlib import Path
import numpy as np


def run(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_lower_hold import SURFACE_SHA,NATIVE_SHA
    from wardrobe185_lower_cloth import panel,sample
    from wardrobe185_lower import fast_geometry
    from wardrobe_shawl180_cache import cache
    from wardrobe_riding_fit import fit_render
    paths=[(BASE/'wardrobe185-lowerisolate02/remeshed-pants.npz','179cf146993f08cd73f0cdc77a90e1a07147303d500fcc17311e01434f9e098f'),
        (BASE/'wardrobe185-lowersurface07/surfaces.npz',SURFACE_SHA),
        (BASE/'wardrobe185-lowerisolate02/all.npz','a168f2ec9c846c47d0acea14e7ae069479d5bf30f5ebbb6fb95a3dd4bc16f151'),
        (BASE/'wardrobe185-trouserseat03/integration-working.blend',NATIVE_SHA)]
    for p,h in paths:
        if digest(p)!=h:raise ValueError('Recontact input changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(paths[0][0],allow_pickle=False) as d:p=d['points'];faces=d['faces']
    with np.load(paths[1][0],allow_pickle=False) as d:contact={k:d[k] for k in d.files}
    with np.load(paths[2][0],allow_pickle=False) as d:cloth=d['frames'][-1];cf=d['faces'];rest=d['rest']
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    target=panel('Original pants motion target',contact['pants_frames'][1],contact['pants_faces'])
    sequence=np.concatenate((contact['pants_frames'][1:2],contact['pants_frames']))
    cache(target,sequence,out/'pants-target.mdd')
    ob=panel('Clean contact derivative',p,faces);scene.frame_set(1);bpy.context.view_layer.update()
    mod=ob.modifiers.new('Continuous fitted pants transport','SURFACE_DEFORM');mod.target=target
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    bpy.ops.object.surfacedeform_bind(modifier=mod.name)
    if not mod.is_bound:raise ValueError('Clean pants contact did not bind')
    relaxed=out.name.endswith('lowerrecontact03')
    corrected=out.name.endswith('lowerrecontact02')
    if corrected:
        group=ob.vertex_groups.new(name='Contact hip and leg flexion')
        w=np.clip((-5.9-p[:,2])/.6,0,1);w=w*w*(3-2*w)
        for i,value in enumerate(w):
            if value:group.add([i],float(value),'REPLACE')
        fair=ob.modifiers.new('Rest-preserving collision deformation','CORRECTIVE_SMOOTH')
        fair.vertex_group=group.name;fair.factor=1.;fair.iterations=24
        fair.smooth_type='LENGTH_WEIGHTED';fair.rest_source='BIND';fair.use_only_smooth=False
        bpy.context.view_layer.update();bpy.ops.object.correctivesmooth_bind(modifier=fair.name)
        if not fair.is_bind:raise ValueError('Contact corrective did not bind')
    if relaxed:
        fair=ob.modifiers.new('Collision surface low-pass','SMOOTH');fair.factor=.5;fair.iterations=12
    frames=[];records={}
    for j,frame in enumerate(contact['frame_ids']):
        scene.frame_set(j+2);bpy.context.view_layer.update();q=sample(ob);frames.append(q)
        if not np.isfinite(q).all():raise ValueError('Nonfinite clean contact')
        if int(frame) in (1,169,193,217,223,326,360):
            tree=BVHTree.FromPolygons(q.tolist(),faces.tolist(),all_triangles=True)
            pairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not set(faces[a])&set(faces[b])]
            local=[(a,b) for a,b in pairs if q[faces[a],2].max()>-9.5 and q[faces[b],2].max()>-9.5]
            signed=[]
            for point in contact['pants_frames'][j]:
                if point[2]<-9.5:continue
                hit,normal,_,distance=tree.find_nearest(Vector(point));signed.append(float((Vector(point)-hit).dot(normal)))
            records[str(int(frame))]={'all_nonadjacent_self_pairs':len(pairs),'upper_leg_seat_self_pairs':len(local),
                'source_signed_nearest_distance_native_quantiles':np.quantile(signed,[0,.5,.99,1]).tolist()}
            if local:
                vi=np.unique(faces[np.unique(np.array(local).ravel())])
                records[str(int(frame))]['crossing_patch_world_bounds']=[q[vi].min(0).tolist(),q[vi].max(0).tolist()]
                records[str(int(frame))]['crossing_patch_reference_bounds']=[p[vi].min(0).tolist(),p[vi].max(0).tolist()]
        if frame%48==0:print('Clean pants contact transport',int(frame),flush=True)
    frames=np.array(frames);error=float(np.max(abs(frames[1]-p)))
    if error>2e-5 and not relaxed:raise ValueError('Contact bind changes admitted169 surface')
    payload={k:v for k,v in contact.items() if k not in ('pants_frames','pants_faces')}
    np.savez_compressed(out/'surfaces.npz',**payload,pants_frames=frames,pants_faces=faces)
    (out/'transport.json').write_text(json.dumps({'frames':records,'reference_error_native':error,
        'surfaces_sha256':digest(out/'surfaces.npz'),'visual_gate':'NOT_RUN'},indent=2)+'\n')
    if corrected or relaxed:
        # This scene contains contacts only, not the actor signature targets.
        # File guards apply here; do not claim an unloaded actor was evaluated.
        for path,sha in paths:
            if digest(path)!=sha:raise ValueError('Contact-only derivative changed a source file')
        (out/'result.json').write_text(json.dumps({'transport':records,'reference_error_native':error,
            'rest_preserving_contact_corrective':corrected,'plain_contact_smoothing':relaxed,
            'visual_gate':'NOT_RUN','source_files_unchanged':True,'accepted_masters_not_opened':True,
            'scope':'Contact derivative only. Plain smoothing changes169 and requires fresh initial/static admission; no moving cloth proof.'},indent=2)+'\n')
        return
    # Inspect static causal success against the actual high-resolution scene.
    bpy.ops.wm.open_mainfile(filepath=str(paths[3][0]),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.frame_set(169);bpy.context.view_layer.update()
    old=bpy.data.objects['MF_fit_tunic_173_visible'];old.hide_render=True
    for item in scene.objects:
        if item.name.startswith('MF_173_tunic_toggle_'):item.hide_render=True
    ob=panel('Static repaired-contact cloth',cloth,cf)
    for mat in old.data.materials:ob.data.materials.append(mat)
    attr=ob.data.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT');attr.data.foreach_set('vector',rest.astype(np.float32).ravel())
    for poly in ob.data.polygons:poly.use_smooth=True
    sub=ob.modifiers.new('Render smoothing','SUBSURF');sub.levels=sub.render_levels=2
    solid=ob.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.006;solid.show_viewport=False
    cp,cfaces=fast_geometry(ob);tree=BVHTree.FromPolygons(cp.tolist(),cfaces.tolist(),all_triangles=True);crossings={}
    for name in ('MF_studio_adult_body','MF_fit_trousers_173_visible','MF185_fitted_upper_tunic','MF185_gait_horse','MF185_gait_saddle','MF185_gait_saddle.pad'):
        points,polys=fast_geometry(bpy.data.objects[name]);tri=points[polys]
        polys=polys[np.all(tri.max(1)>=cp.min(0)-.05,axis=1)&np.all(tri.min(1)<=cp.max(0)+.05,axis=1)]
        pairs=tree.overlap(BVHTree.FromPolygons(points.tolist(),polys.tolist(),all_triangles=True))
        crossings[name]={'triangle_pairs':len(pairs)}
        if pairs:
            patch=cp[np.unique(cfaces[np.unique(np.array(pairs)[:,0])])]
            crossings[name]['cloth_patch_bounds']=[patch.min(0).tolist(),patch.max(0).tolist()]
    solid.show_viewport=True
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO';scene.cycles.device='CPU';scene.cycles.samples=8
    scene.render.use_persistent_data=True
    for angle,label in ((90,'left'),(180,'rear'),(270,'right')):
        fit_render(out,'static169-'+label,angle,(0,-.2,-6.5),7.,(640,640))
    for item in scene.objects:
        if item.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):item.hide_render=True
    fit_render(out,'static169-front-control',0,(0,-.2,-6.5),7.,(640,640))
    check_protected()
    (out/'result.json').write_text(json.dumps({'source_hashes':{str(p):h for p,h in paths},'transport':records,
        'static_cloth_render_midsurface_contacts':crossings,'protected_exact':True,'visual_gate':'NOT_RUN',
        'scope':'Static drape and collision-only transport diagnostics; no complete moving cloth or selected native'},indent=2)+'\n')
