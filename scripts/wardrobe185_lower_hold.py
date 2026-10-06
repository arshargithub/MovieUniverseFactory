"""Pose-held lower garment construction controls before more motion baking.

These are diagnostic states, not an alternate performance or visual approval.
No protected anatomy, old evidence, or free simulated points are edited.
"""
import json
from pathlib import Path
import numpy as np

SURFACE_SHA='6bf419b205c5bc909a325fde898575a443136aae0ae07dd708a9104ef76f4e57'
NATIVE_SHA='3dc4f8f14c88ff8fd4fb0c98ecb58a9348326ca2e1b4e24537d6c31783547626'


def rigid_layout(points,reference,current):
    transform=np.asarray(current)@np.linalg.inv(np.asarray(reference))
    p=np.asarray(points)
    return p@transform[:3,:3].T+transform[:3,3]


def contact_components(data,frame):
    """Keep closed source components, avoiding a fragile intersecting Boolean.

    Initial conditioning only. The summed winding is supplemented by explicit
    per-volume containment checks; this is not a collision-envelope approval.
    """
    from wardrobe185_lower_cloth import panel
    j=list(data['frame_ids']).index(frame);points=[];faces=[];volumes=[];offset=0
    for name in ('pants','upper','body','horse','saddle','pad'):
        p=data[name+'_frames'][j];f=data[name+'_faces']
        points.append(p);faces.append(f+offset);volumes.append((p,f));offset+=len(p)
    ob=panel('Initial closed components',np.concatenate(points),np.concatenate(faces))
    return ob,volumes


def exterior_contact(data,frame):
    """Static exterior control, not a transported animation collider."""
    import bpy,bmesh
    ob,volumes=contact_components(data,frame)
    bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Static volume exterior','REMESH');mod.mode='VOXEL';mod.voxel_size=.035
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=ob.modifiers.new('Exterior contact resolution','DECIMATE');mod.ratio=min(1,16000/len(ob.data.polygons))
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges)
    bm.to_mesh(ob.data);bm.free()
    if bad:raise ValueError('Static volume exterior not manifold')
    # Add no arbitrary inflated silhouette; initial exact source checks remain.
    return ob,volumes


def run(out):
    import bpy
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_lower_cloth import COMPLETE_LAYOUT_SHA,panel,profile,sample,metric_control
    from wardrobe185_lower_drape import SOURCE_SHA,SCALE,contact_union,condition,support_preflight
    from wardrobe185_lower import fast_geometry
    from wardrobe_riding_fit import fit_render
    paths=[(BASE/'wardrobe185-lowerdress14/initial-layout.npz',COMPLETE_LAYOUT_SHA),
        (BASE/'wardrobe185-lowersurface07/surfaces.npz',SURFACE_SHA),
        (BASE/'wardrobe185-lowercapture02/moving-source.npz',SOURCE_SHA),
        (BASE/'wardrobe185-trouserseat03/integration-working.blend',NATIVE_SHA)]
    for p,h in paths:
        if digest(p)!=h:raise ValueError('Held-pose input changed: '+p.name)
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(paths[0][0],allow_pickle=False) as d:cut={k:d[k] for k in d.files}
    with np.load(paths[1][0],allow_pickle=False) as d:contact={k:d[k] for k in d.files}
    with np.load(paths[2][0],allow_pickle=False) as d:pelvis=d['pelvis_matrices']
    rest=cut['rest'];faces=cut['faces'];pins=cut['pin_indices'];weights=cut['pin_weights']
    edges=np.unique(np.sort(np.concatenate([faces[:,[i,(i+1)%4]] for i in range(4)]),axis=1),axis=0)
    lengths=np.linalg.norm(rest[edges[:,0]]-rest[edges[:,1]],axis=1)
    metric_control(out);records={};finals={}
    for frame in (169,217):
        bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
        scene.render.fps=24;scene.gravity=(0,0,-9.81);scene.unit_settings.scale_length=1.
        j=list(contact['frame_ids']).index(frame)
        initial=rigid_layout(cut['mounted'],pelvis[168],pelvis[frame-1])
        initial[pins]=cut['guided'][frame-1,pins]
        exterior=out.name.endswith('lowerhold03')
        union,volumes=(exterior_contact(contact,frame) if exterior else
            contact_components(contact,frame) if out.name.endswith('lowerhold02') else contact_union(contact,frame,False))
        union.data.calc_loop_triangles()
        exterior_points=np.array([v.co[:] for v in union.data.vertices])
        exterior_faces=np.array([t.vertices[:] for t in union.data.loop_triangles])
        p,admission=condition(initial,faces,union,volumes,dict(zip(pins,weights)),
            convex=False,preserve_sewn=True,face_clearance=True)
        bpy.data.objects.remove(union,do_unlink=True)
        from wardrobe185_lower_surface import winding_numbers
        admission['individual_volume_inside_counts']=[int(np.count_nonzero(abs(winding_numbers(p,v,f))>.5)) for v,f in volumes]
        admission['remaining_inside_vertices']=max(admission['remaining_inside_vertices'],sum(admission['individual_volume_inside_counts']))
        (out/('admission-'+str(frame)+'.json')).write_text(json.dumps(admission,indent=2)+'\n')
        np.savez_compressed(out/('initial-'+str(frame)+'.npz'),points=p,faces=faces,rest=rest)
        if admission['remaining_inside_vertices'] or admission['nonadjacent_crossings'] or admission['actor_crossing_pairs']:
            records[str(frame)]={'state':'INITIAL_CONTACT_FAIL','admission':admission};continue
        if admission['max_initial_move_m']>.1 or admission['max_waist_move_m']>.015 or admission['min_edge_m']<.001:
            records[str(frame)]={'state':'INITIAL_CONSTRUCTION_FAIL','admission':admission};continue
        subset={k:(v[j:j+1] if k=='frame_ids' or k.endswith('_frames') else v) for k,v in contact.items()}
        support_preflight(p[None,pins],subset,out,'held-'+str(frame),.0035,np.flatnonzero(weights==1.))
        ob=panel('MF185_held_lower',p*SCALE,faces)
        ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Unstressed cut')
        key.data.foreach_set('co',(rest*SCALE).astype(np.float32).ravel());key.value=0
        group=ob.vertex_groups.new(name='support')
        for index,w in zip(pins,weights):group.add([int(index)],float(w),'REPLACE')
        # Same evaluation stack as moving controls, but all inputs held still.
        from wardrobe_shawl180_cache import cache
        cache(ob,np.repeat(p[None]*SCALE,120,axis=0),out/('held-'+str(frame)+'.mdd'))
        weld=ob.modifiers.new('Explicit rest evaluation','WELD');weld.merge_threshold=1e-7
        domain=bpy.data.collections.new('Outer clothing and mount');scene.collection.children.link(domain)
        for name in (('exterior',) if exterior else ('pants','upper','horse','saddle','pad')):
            cp,cf=(exterior_points,exterior_faces) if exterior else (contact[name+'_frames'][j],contact[name+'_faces'])
            co=panel('MF185_held_'+name,cp*SCALE,cf)
            domain.objects.link(co);co.modifiers.new('Stationary contact','COLLISION')
            co.collision.thickness_outer=.0015;co.collision.cloth_friction=15
        mod=profile(ob,domain);mod.settings.rest_shape_key=key;mod.settings.quality=48
        mod.collision_settings.collision_quality=8;mod.point_cache.frame_end=120
        frames=[];metrics=[]
        for t in range(1,121):
            scene.frame_set(t);bpy.context.view_layer.update();q=sample(ob)/SCALE
            if not np.isfinite(q).all():raise ValueError('Nonfinite held cloth')
            frames.append(q)
            if t%24==0:
                ratio=np.linalg.norm(q[edges[:,0]]-q[edges[:,1]],axis=1)/lengths
                row={'source_pose':frame,'physics_frame':t,'edge_quantiles':np.quantile(ratio,[.01,.5,.99,1]).tolist()}
                metrics.append(row);print('Held lower',json.dumps(row),flush=True)
                (out/('metrics-'+str(frame)+'.json')).write_text(json.dumps(metrics,indent=2)+'\n')
                if t>=72 and row['edge_quantiles'][2]>2.:
                    np.savez_compressed(out/('failed-prefix-'+str(frame)+'.npz'),frames=np.array(frames),faces=faces,rest=rest)
                    break
        np.savez_compressed(out/('held-'+str(frame)+'.npz'),frames=np.array(frames),faces=faces,rest=rest)
        finals[frame]=frames[-1];records[str(frame)]={'state':'METRIC_FAIL' if len(frames)<120 else 'SOLVED_NOT_REVIEWED',
            'metrics':metrics,'admission':admission,'static_exterior_control':exterior}
        (out/'progress.json').write_text(json.dumps(records,indent=2)+'\n')
    bpy.ops.wm.open_mainfile(filepath=str(paths[3][0]),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    old=bpy.data.objects['MF_fit_tunic_173_visible'];old.hide_render=True
    for ob in scene.objects:
        if ob.name.startswith('MF_173_tunic_toggle_'):ob.hide_render=True
    for frame,p in finals.items():
        scene.frame_set(frame);bpy.context.view_layer.update()
        ob=panel('MF185_held_result',p,faces)
        for mat in old.data.materials:ob.data.materials.append(mat)
        attr=ob.data.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT')
        attr.data.foreach_set('vector',rest.astype(np.float32).ravel())
        for poly in ob.data.polygons:poly.use_smooth=True
        sub=ob.modifiers.new('Cloth render smoothing','SUBSURF');sub.levels=sub.render_levels=2
        solid=ob.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.006
        for angle,label in ((90,'left'),(180,'rear')):
            fit_render(out,'held-'+str(frame)+'-'+label,angle,(0,-.2,-6.5),7.,(640,640))
        hidden=[]
        for item in scene.objects:
            if item.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):
                hidden.append((item,item.hide_render));item.hide_render=True
        fit_render(out,'held-'+str(frame)+'-front-control',0,(0,-.2,-6.5),7.,(640,640))
        for item,value in hidden:item.hide_render=value
        bpy.data.objects.remove(ob,do_unlink=True)
    check_protected()
    for p,h in paths:
        if digest(p)!=h:raise ValueError('Held control modified source')
    (out/'result.json').write_text(json.dumps({'cases':records,'inputs':{str(p):h for p,h in paths},
        'visual_gate':'NOT_RUN','protected_exact':True,
        'scope':'Independent held-pose diagnostic, no performance or garment approval'},indent=2)+'\n')
