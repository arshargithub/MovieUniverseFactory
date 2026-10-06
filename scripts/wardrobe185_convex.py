"""Pose-envelope contact volumes; no rendered actor or costume modification.

Contact is a union of overlapping convex regions, not a creased inflated skin.
Fitting uses current evaluated clothing at required poses in each bone frame.
The representation is scoped to this upper-shawl/racing motion, not general rig
qualification. Containment and excessive bulk are separate review questions.
"""
import json
from pathlib import Path
import numpy as np

RIDER07_SHA='bbe84ab2f4699cb50cb5036c2c08d4f872d272a62f3943db4944de51e1cc778b'
SOURCE_EXPORT_SHA='07612b8348e0275229f22524484532244cf32456836e7b58f72ff1794ab73247'
CONTACT_SHA='1e8e0394f0093b11a609c634d1065233eea5161097c2091352067b6e1e918ad2'


def region_masks(rest):
    x,y,z=np.asarray(rest).T
    upper=(z>-4.2)&(z<-1.35)
    return {'torso':upper&(abs(x)<1.5),
            'armL':upper&(x>1.35), 'armR':upper&(x<-1.35)}


def convex_outside(points,vertices,faces,tolerance=2e-5):
    """Outward half-spaces avoid ray/edge ambiguity on a convex volume."""
    tri=vertices[faces];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.linalg.norm(normal,axis=1)[:,None]
    plane=np.einsum('ij,ij->i',normal,tri[:,0]);result=[]
    for start in range(0,len(points),512):
        result.extend(np.max(points[start:start+512]@normal.T-plane,axis=1)>tolerance)
    return np.array(result)


def robust_hull(points,margin=.035):
    """Outer-Python preprocessing with the existing SciPy dependency.

    Do not import this compiled extension into Blender's different Python.
    Well-spaced supporting planes avoid nearly coincident hull vertices from
    dense repeated pose samples. Check float32 transfer independently.
    """
    from scipy.spatial import ConvexHull,HalfspaceIntersection
    points=np.asarray(points,dtype=float)
    if points.ndim!=2 or points.shape[1]!=3 or not np.isfinite(points).all():raise ValueError('Invalid hull input')
    i=np.arange(96);z=1-2*(i+.5)/len(i);phi=i*np.pi*(3-np.sqrt(5));radius=np.sqrt(1-z*z)
    directions=np.concatenate([np.stack([radius*np.cos(phi),radius*np.sin(phi),z],axis=1),np.eye(3),-np.eye(3)])
    planes=np.column_stack([directions,-(points@directions.T).max(0)-margin])
    expanded=HalfspaceIntersection(planes,points.mean(0)).intersections
    hull=ConvexHull(expanded);used=hull.vertices;lookup=np.full(len(expanded),-1,dtype=int);lookup[used]=np.arange(len(used))
    q=expanded[used];faces=lookup[hull.simplices].copy();tri=q[faces]
    signs=np.einsum('ij,ij->i',np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),hull.equations[:,:3])
    faces[signs<0]=faces[signs<0,::-1]
    if convex_outside(points,q,faces).any() or convex_outside(q,q,faces).any():raise ValueError('Double precision hull failed containment')
    if convex_outside(points,q.astype(np.float32).astype(float),faces).any():raise ValueError('Float32 transfer loses source containment')
    return q,faces


def capture(out):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.kdtree import KDTree
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_gallop import DIAGNOSTIC_SHA
    from wardrobe_doublewrap185_solve import inside
    from wardrobe_riding_fit import fit_render
    from wardrobe_motion178_controls import render_geometry_paused
    source=BASE/'wardrobe185-gallopscreen01/diagnostic.blend'
    if digest(source)!=DIAGNOSTIC_SHA:raise ValueError('Actor source changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    export_only=out.name.endswith('convexsource01')
    if export_only:
        from wardrobe185_gallop import transfer_action
        rider=BASE/'wardrobe185-riding07/rider-rig.blend'
        if RIDER07_SHA is None or digest(rider)!=RIDER07_SHA:raise ValueError('Hip-hinge action not admitted and bound')
        with bpy.data.libraries.load(str(rider),link=False) as (_,loaded):loaded.objects=['MF_body156_fit_rig']
        donor=loaded.objects[0];scene.collection.objects.link(donor);transfer_action(donor,rig);bpy.data.objects.remove(donor,do_unlink=True)
    scene.frame_set(1);bpy.context.view_layer.update();check_protected()
    names={'torso':'chest','armL':'upperarm.L','armR':'upperarm.R','head':'MF185_head'}
    sample_frames=(1,96,169,193,217,220,223,226,265,300,324,348,360)
    gathered={k:[] for k in names};pose_points={};matrices={k:[] for k in names}
    objects=[bpy.data.objects[n] for n in ('MF185_fitted_upper_tunic','MF_173_tension_harness_-1','MF_173_tension_harness_1','MF_studio_adult_body')]
    flags=[(m,m.show_viewport) for ob in objects for m in ob.modifiers if m.type=='SUBSURF']
    for m,_ in flags:m.show_viewport=False
    body_rest=np.array([v.co[:] for v in objects[-1].data.vertices])
    def delta(name):
        b=rig.pose.bones[name]
        return rig.matrix_world@b.matrix@b.bone.matrix_local.inverted()@rig.matrix_world.inverted()
    for frame in sample_frames:
        scene.frame_set(frame);bpy.context.view_layer.update();samples={k:[] for k in names}
        for ob in objects:
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
            points=np.array([ob.matrix_world@v.co for v in mesh.vertices])
            attr=mesh.attributes.get('MF_173_material_coords')
            rest=np.array([a.vector[:] for a in attr.data]) if ob!=objects[-1] and attr else body_rest
            if len(rest)!=len(points):raise ValueError('Missing stable region coordinates')
            masks=region_masks(rest)
            if ob==objects[-1]:
                masks={'torso':(abs(rest[:,0])<1.5)&(rest[:,2]>-3.8)&(rest[:,2]<-1.35),'head':rest[:,2]>-1.5}
            elif ob!=objects[0]:masks={'torso':(rest[:,2]>-4.2)&(rest[:,2]<-1.35)}
            for key,mask in masks.items():
                selected=points[mask];selected=selected[::max(1,len(selected)//4000)]
                samples[key].extend(selected.tolist())
            ev.to_mesh_clear()
        for key in names:
            p=np.asarray(samples[key]);inv=np.array(delta(names[key]).inverted())
            local=p@inv[:3,:3].T+inv[:3,3];gathered[key].append(local)
        pose_points[frame]=samples
        print('185 convex source',frame,flush=True)
    if export_only:
        output={key+'_source':np.concatenate(gathered[key]) for key in names}
        with render_geometry_paused():
            for frame in range(1,361):
                scene.frame_set(frame);bpy.context.view_layer.update()
                for key,bone in names.items():matrices[key].append(np.array(delta(bone)))
        output.update({key+'_matrices':np.array(matrices[key]) for key in names})
        np.savez_compressed(out/'fitted-source.npz',**output)
        (out/'source.json').write_text(json.dumps({'assembly_sha256':DIAGNOSTIC_SHA,'rider_sha256':RIDER07_SHA,'sample_frames':sample_frames,
            'scope':'Source points and exact action matrices for outer-Python conservative hull preparation; not contact admission'},indent=2)+'\n')
        for m,state in flags:m.show_viewport=state
        check_protected();return
    colliders={};report={};arrays={'frame_ids':np.arange(1,361)}
    for key in names:
        p=np.concatenate(gathered[key]);bm=bmesh.new()
        for point in p:bm.verts.new(point)
        bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
        unused=[v for v in bm.verts if not v.link_faces]
        if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
        # Small contact tolerance, not an attempt to inflate away a bad rig.
        for v in bm.verts:v.co+=v.normal*.035
        inflated=[v.co.copy() for v in bm.verts];bm.free();bm=bmesh.new()
        for point in inflated:bm.verts.new(point)
        bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
        unused=[v for v in bm.verts if not v.link_faces]
        if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.normal_update()
        if any(not e.is_manifold for e in bm.edges) or bm.calc_volume()<=0:raise ValueError('Invalid convex contact volume')
        mesh=bpy.data.meshes.new('185 convex '+key);bm.to_mesh(mesh);bm.free();mesh.calc_loop_triangles()
        ob=bpy.data.objects.new('MF185_convex_'+key,mesh);scene.collection.objects.link(ob);colliders[key]=ob
        q=np.array([v.co[:] for v in mesh.vertices]);f=np.array([t.vertices[:] for t in mesh.loop_triangles])
        tree=BVHTree.FromPolygons(q.tolist(),f.tolist(),all_triangles=True)
        np.savez_compressed(out/(key+'-hull.npz'),points=q,faces=f,source=p)
        tri=q[f];nn=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);nn/=np.linalg.norm(nn,axis=1)[:,None]
        plane=np.einsum('ij,ij->i',nn,tri[:,0]);violation=float(np.max(q@nn.T-plane))
        print('185 convex guard',key,len(q),len(f),violation,flush=True)
        if convex_outside(q,q,f).any():raise ValueError('Contact volume is not convex')
        outside=int(convex_outside(p,q,f).sum())
        if outside:raise ValueError('Convex envelope misses fitted samples: '+str((key,outside)))
        arrays[key+'_points']=q;arrays[key+'_faces']=f
        report[key]={'vertices':len(q),'faces':len(f),'source_points':len(p),'outside_fitted_samples':outside,'nonmanifold_edges':0}
    # The smooth groom envelope remains separate and rigid to actual head.
    groom_path=BASE/'wardrobe185-gallopcontact06/surface-contact.npz'
    if digest(groom_path)!='805e076fe6f33d4dcf63a80556541c1973e0b4c4789875860b40a46473d584cf':raise ValueError('Groom envelope changed')
    with np.load(groom_path,allow_pickle=False) as d:gp=d['groom_points'];gf=d['groom_faces']
    mesh=bpy.data.meshes.new('185 smooth groom contact');mesh.from_pydata(gp.tolist(),[],gf.tolist());mesh.update()
    gob=bpy.data.objects.new('MF185_convex_groom',mesh);scene.collection.objects.link(gob);colliders['groom']=gob
    arrays['groom_points']=gp;arrays['groom_faces']=gf;names['groom']='MF185_head';matrices['groom']=[]
    frames={key:[] for key in names};bulk=[]
    with render_geometry_paused():
        for frame in range(1,361):
            scene.frame_set(frame);bpy.context.view_layer.update()
            for key,bone in names.items():
                mat=np.array(delta(bone));p=arrays[key+'_points'];q=p@mat[:3,:3].T+mat[:3,3]
                frames[key].append(q);matrices[key].append(mat)
                if frame in pose_points and key!='groom':
                    samples=pose_points[frame][key];kd=KDTree(len(samples))
                    for i,point in enumerate(samples):kd.insert(point,i)
                    kd.balance();f=arrays[key+'_faces'];queries=np.concatenate([q,q[f].mean(1)])
                    gaps=np.array([kd.find(point)[2] for point in queries])*122.92759120464325
                    bulk.append({'frame':frame,'part':key,'nearest_sample_gap_mm_quantiles':np.quantile(gaps,[.5,.9,.99,1]).tolist(),
                        'meaning':'Distance to sampled visible points, not exact surface distance; includes closure caps and concavity bridges'})
        for key in names:
            arrays[key+'_frames']=np.array(frames[key]);arrays[key+'_matrices']=np.array(matrices[key])
    np.savez_compressed(out/'contact.npz',**arrays)
    (out/'result.json').write_text(json.dumps({'parts':report,'bulk':bulk,'source_sha256':DIAGNOSTIC_SHA,
        'sample_frames':sample_frames,'full_motion_captured':True,'visual_gate':'NOT_RUN','cloth_gate':'NOT_RUN','method':'Bone-local convex swept envelope of sampled actual upper garment/skin; separate groom'},indent=2)+'\n')
    for m,state in flags:m.show_viewport=state
    for ob in scene.objects:
        if ob.type in ('MESH','CURVE','CURVES'):ob.hide_render=True
    scene.frame_set(348);bpy.context.view_layer.update()
    for key,ob in colliders.items():
        for v,p in zip(ob.data.vertices,frames[key][347]):v.co=p
        ob.data.update();ob.hide_render=False
    target=rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-.6))
    scene.cycles.device='CPU';scene.cycles.samples=8
    for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):fit_render(out,'contact-'+label,angle,tuple(target),8.,(640,640))
    check_protected()


def prepare_offline():
    """Fixed local input/output only; run with the project's outer Python."""
    import shutil,sys,scipy
    from wardrobe_motion178 import BASE,digest
    source=BASE/'wardrobe185-convexsource01/fitted-source.npz'
    groom=BASE/'wardrobe185-gallopcontact06/surface-contact.npz'
    if SOURCE_EXPORT_SHA is None or digest(source)!=SOURCE_EXPORT_SHA or digest(groom)!='805e076fe6f33d4dcf63a80556541c1973e0b4c4789875860b40a46473d584cf':raise ValueError('Unbound hull preprocessing input')
    out=BASE/'wardrobe185-convexcontact04'
    if out.exists() or out.is_symlink():raise ValueError('Preserve hull evidence')
    out.mkdir();shutil.copy2(__file__,out/Path(__file__).name)
    with np.load(source,allow_pickle=False) as d:source_data={k:d[k] for k in d.files}
    arrays={'frame_ids':np.arange(1,361)};report={}
    for key in ('torso','armL','armR','head'):
        p=source_data[key+'_source'];q,f=robust_hull(p);matrices=source_data[key+'_matrices']
        frames=np.einsum('fij,nj->fni',matrices[:,:3,:3],q)+matrices[:,:3,3][:,None,:]
        arrays.update({key+'_points':q,key+'_faces':f,key+'_frames':frames,key+'_matrices':matrices})
        report[key]={'vertices':len(q),'faces':len(f),'source_samples':len(p),'outside':int(convex_outside(p,q,f).sum()),'float32_source_containment':not bool(convex_outside(p,q.astype(np.float32).astype(float),f).any())}
    with np.load(groom,allow_pickle=False) as d:q=d['groom_points'];f=d['groom_faces']
    matrices=source_data['head_matrices'];frames=np.einsum('fij,nj->fni',matrices[:,:3,:3],q)+matrices[:,:3,3][:,None,:]
    arrays.update(groom_points=q,groom_faces=f,groom_frames=frames,groom_matrices=matrices)
    np.savez_compressed(out/'contact.npz',**arrays)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_EXPORT_SHA,'rider_sha256':RIDER07_SHA,'parts':report,
        'python':sys.version,'scipy':scipy.__version__,'source_pose_containment':'PASS','visual_gate':'NOT_RUN','excess_bulk_gate':'NOT_RUN','cloth_gate':'NOT_RUN'},indent=2)+'\n')
    print(json.dumps(report),flush=True)


def screen(out):
    import bpy,bmesh
    from mathutils import Vector
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_gallop import DIAGNOSTIC_SHA,transfer_action
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-gallopscreen01/diagnostic.blend';path=BASE/'wardrobe185-convexcontact04/contact.npz';rider=BASE/'wardrobe185-riding07/rider-rig.blend'
    if CONTACT_SHA is None or digest(path)!=CONTACT_SHA or digest(source)!=DIAGNOSTIC_SHA or digest(rider)!=RIDER07_SHA:raise ValueError('Unbound regional contact screen')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(path,allow_pickle=False) as d:data={k:d[k] for k in d.files}
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    with bpy.data.libraries.load(str(rider),link=False) as (_,loaded):loaded.objects=['MF_body156_fit_rig']
    donor=loaded.objects[0];scene.collection.objects.link(donor);transfer_action(donor,rig);bpy.data.objects.remove(donor,do_unlink=True)
    for ob in scene.objects:
        if ob.type in ('MESH','CURVE','CURVES'):ob.hide_render=True
    proxies={};report={}
    for key in ('torso','armL','armR','head','groom'):
        mesh=bpy.data.meshes.new('185 regional '+key);mesh.from_pydata(data[key+'_points'].tolist(),[],data[key+'_faces'].tolist());mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
        if bad:raise ValueError('Transferred regional volume not closed: '+key)
        ob=bpy.data.objects.new('MF185_regional_'+key,mesh);scene.collection.objects.link(ob);proxies[key]=ob;report[key]={'nonmanifold_edges':bad}
    scene.cycles.device='CPU';scene.cycles.samples=8
    for frame in (1,217,348):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for key,ob in proxies.items():
            for v,p in zip(ob.data.vertices,data[key+'_frames'][frame-1]):v.co=p
            ob.data.update()
        target=rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-.6))
        for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):fit_render(out,'contact-'+label+'-'+str(frame),angle,tuple(target),8.,(640,640))
    check_protected();(out/'result.json').write_text(json.dumps({'parts':report,'visual_gate':'NOT_RUN','contact_sha256':CONTACT_SHA},indent=2)+'\n')


def static_contacts(out,scale):
    """Neutral union for staging only; no action, rig or moving cache."""
    import bpy,bmesh
    from wardrobe_motion178 import BASE,digest
    path=BASE/'wardrobe185-convexcontact04/contact.npz'
    if digest(path)!=CONTACT_SHA:raise ValueError('Unbound neutral regional contacts')
    contacts=[]
    with np.load(path,allow_pickle=False) as data:
        for key in ('torso','armL','armR','head','groom'):
            mesh=bpy.data.meshes.new('185 static '+key);mesh.from_pydata((data[key+'_points']*scale).tolist(),[],data[key+'_faces'].tolist());mesh.update()
            ob=bpy.data.objects.new('MF185_static_'+key,mesh);bpy.context.scene.collection.objects.link(ob);contacts.append(ob)
    union=contacts[0].copy();union.data=union.data.copy();bpy.context.scene.collection.objects.link(union)
    union.name='MF185_neutral_dressing_union';bpy.context.view_layer.objects.active=union
    for ob in contacts[1:]:
        mod=union.modifiers.new('Neutral union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(union.data);bad=sum(not e.is_manifold for e in bm.edges)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(union.data);bm.free()
    for ob in contacts:bpy.data.objects.remove(ob,do_unlink=True)
    if bad:raise ValueError('Neutral contact union is not closed')
    (out/'contact-binding.json').write_text(json.dumps({'contact_sha256':CONTACT_SHA,'neutral_only':True,'nonmanifold_edges':bad},indent=2)+'\n')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    return union


def solver_contacts(canonical,out,scale):
    """Load exact regional trajectories; union only for initial dressing.

    Moving collision uses distinct overlapping volumes. The stationary union
    is NEVER a collider and must not be mistaken for a moving actor proxy.
    """
    import bpy,bmesh
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    from mathutils import Matrix
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_gallop import transfer_action
    from wardrobe_shawl180_cache import cache
    path=BASE/'wardrobe185-convexcontact04/contact.npz';rider=BASE/'wardrobe185-riding07/rider-rig.blend'
    if CONTACT_SHA is None or digest(path)!=CONTACT_SHA or digest(rider)!=RIDER07_SHA:raise ValueError('Unbound regional solver input')
    with np.load(path,allow_pickle=False) as d:data={k:d[k] for k in d.files}
    with bpy.data.libraries.load(str(rider),link=False) as (_,loaded):loaded.objects=['MF_body156_fit_rig']
    donor=loaded.objects[0];bpy.context.scene.collection.objects.link(donor)
    transfer_action(donor,canonical);bpy.data.objects.remove(donor,do_unlink=True)
    errors=[];scene=bpy.context.scene
    for frame in range(1,361):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for key,name in (('torso','chest'),('head','MF185_head'),('armL','upperarm.L'),('armR','upperarm.R')):
            b=canonical.pose.bones[name];delta=canonical.matrix_world@b.matrix@b.bone.matrix_local.inverted()@canonical.matrix_world.inverted()
            native=Matrix.Scale(1/scale,4)@delta@Matrix.Scale(scale,4)
            errors.append(float(np.max(abs(np.array(native)-data[key+'_matrices'][frame-1]))))
    if max(errors)>1e-5:raise ValueError('Regional contact action mismatch')
    scene.frame_set(1);bpy.context.view_layer.update();contacts=[]
    for key in ('torso','armL','armR','head','groom'):
        mesh=bpy.data.meshes.new('185 contact '+key);mesh.from_pydata((data[key+'_points']*scale).tolist(),[],data[key+'_faces'].tolist());mesh.update()
        ob=bpy.data.objects.new('MF185_collision_'+key,mesh);scene.collection.objects.link(ob)
        cache(ob,data[key+'_frames']*scale,out/(key+'-contact.mdd'));contacts.append(ob)
    union=contacts[0].copy();union.data=union.data.copy();union.name='MF185_initial_union_NOT_COLLIDER';scene.collection.objects.link(union)
    for m in list(union.modifiers):union.modifiers.remove(m)
    bpy.context.view_layer.objects.active=union;union.select_set(True)
    for ob in contacts[1:]:
        mod=union.modifiers.new('Initial volume union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(union.data);bad=sum(not e.is_manifold for e in bm.edges)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(union.data);bm.free()
    if bad:raise ValueError('Initial regional union is not closed')
    (out/'regional-contact-binding.json').write_text(json.dumps({'contact_sha256':CONTACT_SHA,'rider_sha256':RIDER07_SHA,
        'canonical_pose_error_all_frames':max(errors),'moving_colliders':[o.name for o in contacts],
        'static_union_is_collider':False,'initial_union_nonmanifold_edges':bad},indent=2)+'\n')
    return union,contacts


def bind_regions(ob,canonical,head_count):
    """Declared crown-to-head and outer-course-to-torso support semantics."""
    import bpy
    ob.vertex_groups.clear()
    head=ob.vertex_groups.new(name='MF185_head');head.add(list(range(head_count)),1.,'REPLACE')
    chest=ob.vertex_groups.new(name='chest');chest.add(list(range(head_count,len(ob.data.vertices))),1.,'REPLACE')
    mod=ob.modifiers.new('Explicit regional support motion','ARMATURE');mod.object=canonical;mod.use_deform_preserve_volume=True
    bpy.context.view_layer.objects.active=ob
    while list(ob.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)


if __name__=='__main__':prepare_offline()
