"""Current evaluated-character collision cage, not an independently skinned suit.

The body surface correspondence is fixed at neutral. A separate closed groom
volume uses the actual head delta. Neither construction edits visible assets.
"""
import json
from pathlib import Path
import numpy as np


def frames_for_triangles(triangles):
    a=triangles[:,1]-triangles[:,0];n=np.cross(a,triangles[:,2]-triangles[:,0])
    la=np.linalg.norm(a,axis=1);ln=np.linalg.norm(n,axis=1)
    if np.any(la<1e-9) or np.any(ln<1e-10):raise ValueError('Degenerate surface correspondence')
    a/=la[:,None];n/=ln[:,None];b=np.cross(n,a)
    return np.stack((a,b,n),axis=2)


def deform(points,ids,bary,offsets):
    triangles=points[ids];basis=frames_for_triangles(triangles)
    return np.einsum('ni,nij->nj',bary,triangles)+np.einsum('nij,nj->ni',basis,offsets)


def structure(out):
    """Trace visible clothing's actual deformation dependencies against skin."""
    import bpy
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_gallop import DIAGNOSTIC_SHA
    source=BASE/'wardrobe185-gallopscreen01/diagnostic.blend'
    if digest(source)!=DIAGNOSTIC_SHA:raise ValueError('Actor input changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    body=bpy.data.objects['MF_studio_adult_body'];objects={body.name:body}
    for name in ('MF185_fitted_upper_tunic','MF_173_tension_harness_-1','MF_173_tension_harness_1'):
        ob=bpy.data.objects[name];objects[name]=ob
        for mod in ob.modifiers:
            if mod.type=='SURFACE_DEFORM':objects[mod.target.name]=mod.target
    description={}
    for name,ob in objects.items():
        description[name]={'data':ob.data.name,'vertices':len(ob.data.vertices),'matrix':np.array(ob.matrix_world).tolist(),
            'modifiers':[{'name':m.name,'type':m.type,'viewport':m.show_viewport,'render':m.show_render,
                'target':getattr(getattr(m,'target',None),'name',None),'object':getattr(getattr(m,'object',None),'name',None)} for m in ob.modifiers]}
        for m in ob.modifiers:
            if m.type=='SUBSURF':m.show_viewport=False
    poses=[]
    for frame in (1,193,217,348):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();points={}
        for name,ob in objects.items():
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
            points[name]=np.array([ob.matrix_world@v.co for v in mesh.vertices]);ev.to_mesh_clear()
        diffs={name:float(np.max(abs(p-points[body.name]))) if p.shape==points[body.name].shape else None for name,p in points.items()}
        poses.append({'frame':frame,'body_target_max_coordinate_difference':diffs,
            'shape_keys':{name:{k.name:k.value for k in ob.data.shape_keys.key_blocks if k.value} if ob.data.shape_keys else {} for name,ob in objects.items()}})
    (out/'structure.json').write_text(json.dumps({'objects':description,'poses':poses},indent=2)+'\n');check_protected()
    if out.name.endswith('gallopstructure02'):
        from mathutils import Vector
        from wardrobe_riding_fit import fit_render
        rig=bpy.data.objects['MF_body156_fit_rig'];scene=bpy.context.scene
        for ob in scene.objects:
            if ob.type in ('MESH','CURVE','CURVES'):ob.hide_render=True
        body.hide_render=False;body.hide_viewport=False
        clay=bpy.data.materials.new('Diagnostic skin geometry only');clay.diffuse_color=(.45,.45,.45,1)
        scene.view_layers[0].material_override=clay;scene.cycles.device='CPU';scene.cycles.samples=8
        for frame in (169,193,217):
            scene.frame_set(frame);bpy.context.view_layer.update()
            target=rig.matrix_world@rig.pose.bones['chest'].head+Vector((0,0,.2))
            for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):
                fit_render(out,'body-'+label+'-'+str(frame),angle,tuple(target),8.,(640,640))


def fidelity(out):
    """Sample actual visible upper garment/leather, not an obsolete rest suit."""
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_gallop import DIAGNOSTIC_SHA
    from wardrobe_doublewrap185_solve import inside
    source=BASE/'wardrobe185-gallopscreen01/diagnostic.blend'
    contact=BASE/'wardrobe185-gallopcontact06/surface-contact.npz'
    expected='805e076fe6f33d4dcf63a80556541c1973e0b4c4789875860b40a46473d584cf'
    if out.name.endswith('gallopfidelity02'):
        contact=BASE/'wardrobe185-gallopcontact07/surface-contact.npz';expected='d5a5d2f4d04dc14a8b72fe19bce2f5932ab4556570446a7cca77a72624634f91'
    if expected is None or digest(source)!=DIAGNOSTIC_SHA or digest(contact)!=expected:raise ValueError('Contact fidelity inputs changed')
    with np.load(contact,allow_pickle=False) as d:data={k:d[k] for k in d.files}
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig'];records=[]
    for j,frame in enumerate(data['frame_ids']):
        scene.frame_set(int(frame));bpy.context.view_layer.update()
        parts=[(data[k+'_frames'][j],data[k+'_faces']) for k in ('body','groom')]
        trees=[BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True) for p,f in parts]
        bone=rig.pose.bones['chest'];delta=rig.matrix_world@bone.matrix@bone.bone.matrix_local.inverted()@rig.matrix_world.inverted();inverse=delta.inverted()
        for name in ('MF185_fitted_upper_tunic','MF_173_tension_harness_-1','MF_173_tension_harness_1'):
            ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
            points=[ob.matrix_world@v.co for v in mesh.vertices]
            attr=mesh.attributes.get('MF_173_material_coords')
            if not attr or len(attr.data)!=len(points):raise ValueError('Missing stable garment region coordinates')
            rest=[a.vector.copy() for a in attr.data]
            ev.to_mesh_clear();selected=[p for p,r in zip(points,rest) if -3.8<r.z<-1.4 and abs(r.x)<2.1]
            selected=selected[::max(1,len(selected)//2500)]
            outside=[];ambiguous=0
            for p in selected:
                contained=False;unknown=False
                for tree in trees:
                    try:contained|=inside(tree,p)
                    except ValueError:unknown=True
                if contained:continue
                if unknown:ambiguous+=1;continue
                outside.append({'point':list(p),'rest':list(inverse@p),'gap_native':min(t.find_nearest(p)[3] for t in trees)})
            records.append({'frame':int(frame),'object':name,'sample_count':len(selected),'outside_count':len(outside),'ambiguous':ambiguous,
                'max_exposure_mm':max((r['gap_native'] for r in outside),default=0)*122.92759120464325,
                'worst':sorted(outside,key=lambda r:r['gap_native'],reverse=True)[:8]})
        (out/'coverage.json').write_text(json.dumps(records,indent=2)+'\n')
        print('185 actual garment coverage',int(frame),[(r['object'],r['outside_count'],r['max_exposure_mm']) for r in records[-3:]],flush=True)
    check_protected()


def capture(out):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.geometry import barycentric_transform
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_gallop import DIAGNOSTIC_SHA
    from wardrobe_motion178_controls import render_geometry_paused
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-gallopscreen01/diagnostic.blend'
    if digest(source)!=DIAGNOSTIC_SHA:raise ValueError('Evaluated actor source changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig']
    scene.frame_set(1);bpy.context.view_layer.update();check_protected()
    flags=[(m,m.show_viewport) for m in body.modifiers if m.type=='SUBSURF']
    for m,_ in flags:m.show_viewport=False
    def body_mesh():
        bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
        p=np.array([body.matrix_world@v.co for v in mesh.vertices]);normal=np.array([v.normal[:] for v in mesh.vertices])
        f=np.array([t.vertices[:] for t in mesh.loop_triangles])
        topology=tuple(tuple(poly.vertices) for poly in mesh.polygons)
        ev.to_mesh_clear();return p,normal,f,topology
    with render_geometry_paused():
        body.hide_viewport=False;p0,normal,body_faces,body_topology=body_mesh()
    if len(p0)!=len(body.data.vertices):raise ValueError('Body correspondence lacks source indices')
    groups={g.index:g.name for g in body.vertex_groups}
    arm=np.array([sum(g.weight for g in v.groups if groups[g.group].startswith(('upperarm.','forearm.','hand.','MF_fit_finger'))) for v in body.data.vertices])
    t=np.clip((-p0[:,2]-1.)/.75,0,1);t=t*t*(3-2*t)
    normal_field=out.name.endswith('gallopcontact08')
    torso_padding=.25 if out.name.endswith(('gallopcontact07','gallopcontact08')) else .15
    padding=.025*(1-t)+(torso_padding*(1-arm)+.08*arm)*t
    keep=np.all(p0[body_faces,2]>-5.8,axis=1);selected=body_faces[keep]
    ids=np.unique(selected);lookup=np.full(len(p0),-1,dtype=int);lookup[ids]=np.arange(len(ids))
    data=bpy.data.meshes.new('185 body collision cage');data.from_pydata((p0+normal*padding[:,None])[ids].tolist(),[],lookup[selected].tolist());data.update()
    bm=bmesh.new();bm.from_mesh(data);boundary=[e for e in bm.edges if e.is_boundary]
    if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    cage=bpy.data.objects.new('MF185_actual_body_cage',data);scene.collection.objects.link(cage)
    bpy.context.view_layer.objects.active=cage
    remesh=cage.modifiers.new('Closed collision envelope','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.04
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth=cage.modifiers.new('Collision fairing','SMOOTH');smooth.factor=.4;smooth.iterations=3;bpy.ops.object.modifier_apply(modifier=smooth.name)
    dec=cage.modifiers.new('Fixed contact resolution','DECIMATE');dec.ratio=min(1,12000/len(cage.data.polygons));bpy.ops.object.modifier_apply(modifier=dec.name)
    cage.data.calc_loop_triangles();q0=np.array([v.co[:] for v in cage.data.vertices]);faces=np.array([t.vertices[:] for t in cage.data.loop_triangles])
    bm=bmesh.new();bm.from_mesh(cage.data);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();bm.free()
    if nonmanifold or volume<=0:raise ValueError('Invalid body cage volume')
    tree=BVHTree.FromPolygons(p0.tolist(),body_faces.tolist(),all_triangles=True)
    anchors=[];barys=[]
    for p in q0:
        hit,_,tri,_=tree.find_nearest(Vector(p));indices=body_faces[tri]
        bary=barycentric_transform(hit,*(Vector(p0[i]) for i in indices),Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
        anchors.append(indices);barys.append(tuple(bary))
    anchors=np.array(anchors);barys=np.array(barys);basis=frames_for_triangles(p0[anchors])
    centers=np.einsum('ni,nij->nj',barys,p0[anchors]);offsets=np.einsum('nji,nj->ni',basis,q0-centers)
    parity=float(np.max(abs(deform(p0,anchors,barys,offsets)-q0)))
    if parity>1e-5:raise ValueError('Cage neutral correspondence mismatch')
    if normal_field:
        neutral_normals=np.einsum('ni,nij->nj',barys,normal[anchors]);neutral_normals/=np.linalg.norm(neutral_normals,axis=1)[:,None]
        normal_offsets=np.einsum('ni,ni->n',q0-centers,neutral_normals)
    smooth_binding=out.name.endswith(('gallopcontact05','gallopcontact06','gallopcontact07'))
    if smooth_binding:
        target=body
        if out.name.endswith(('gallopcontact06','gallopcontact07')):
            target=body.copy();target.name='MF185_triangulated_contact_target';scene.collection.objects.link(target)
            target.hide_render=True;target.hide_viewport=False
            tri=target.modifiers.new('Fixed diagonal surface correspondence','TRIANGULATE');tri.quad_method='FIXED';tri.ngon_method='CLIP'
        follow=cage.modifiers.new('Current body surface correspondence','SURFACE_DEFORM')
        follow.target=target;follow.falloff=4.
        bpy.context.view_layer.objects.active=cage;cage.select_set(True)
        bpy.context.view_layer.update();bpy.ops.object.surfacedeform_bind(modifier=follow.name)
        if not follow.is_bound:raise ValueError('Collision cage surface bind failed')
    groom=bpy.data.objects['MF_173_static_groom_clearance']
    ev=groom.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
    gp=np.array([groom.matrix_world@v.co for v in mesh.vertices]);gf=np.array([t.vertices[:] for t in mesh.loop_triangles]);ev.to_mesh_clear()
    gm=bpy.data.meshes.new('185 separate groom');gm.from_pydata(gp.tolist(),[],gf.tolist());gm.update()
    bm=bmesh.new();bm.from_mesh(gm);boundary=[e for e in bm.edges if e.is_boundary]
    if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(gm)
    groom_nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free();gm.calc_loop_triangles()
    gf=np.array([t.vertices[:] for t in gm.loop_triangles])
    if groom_nonmanifold:raise ValueError('Groom envelope not closed')
    if smooth_binding or normal_field:
        temporary=bpy.data.objects.new('185 groom fairing',gm);scene.collection.objects.link(temporary)
        bpy.context.view_layer.objects.active=temporary
        fair=temporary.modifiers.new('Remove envelope section ridges','SMOOTH');fair.factor=.6;fair.iterations=12
        bpy.ops.object.modifier_apply(modifier=fair.name)
        gp=np.array([v.co[:] for v in gm.vertices]);gm.calc_loop_triangles();gf=np.array([t.vertices[:] for t in gm.loop_triangles])
        bpy.data.objects.remove(temporary,do_unlink=True)
    frames=[];groom_frames=[];audits=[];sample_frames=(1,96,169,193,217,265,300,324,348,360)
    with render_geometry_paused():
        body.hide_viewport=False;cage.hide_viewport=False
        if smooth_binding:target.hide_viewport=False
        frame_ids=sample_frames if out.name.endswith(('gallopcontact03','gallopcontact04','gallopcontact05','gallopcontact06','gallopcontact07','gallopcontact08')) else range(1,361)
        for frame in frame_ids:
            scene.frame_set(frame);p,normals,_,topology=body_mesh()
            # Loop triangulation may flip a quad diagonal under deformation.
            # Polygon connectivity is the invariant; correspondence retains
            # the neutral triangles and their stable source vertex indices.
            if p.shape!=p0.shape or topology!=body_topology:raise ValueError('Body polygon topology changed during motion')
            try:
                if smooth_binding:
                    ev=cage.evaluated_get(bpy.context.evaluated_depsgraph_get());cm=ev.to_mesh()
                    q=np.array([v.co[:] for v in cm.vertices]);ev.to_mesh_clear()
                elif normal_field:
                    nn=np.einsum('ni,nij->nj',barys,normals[anchors]);nn/=np.linalg.norm(nn,axis=1)[:,None]
                    q=np.einsum('ni,nij->nj',barys,p[anchors])+nn*normal_offsets[:,None]
                    # Closing cap is not an outward skin offset. Retain its
                    # correspondence while offsetting only the actual surface.
                    cap=q0[:,2]<-5.55
                    q[cap]=deform(p,anchors[cap],barys[cap],offsets[cap])
                else:q=deform(p,anchors,barys,offsets)
            except ValueError as exc:
                np.savez_compressed(out/'failed-correspondence.npz',points=p,anchors=anchors,barycentric=barys,offsets=offsets)
                (out/'failure.json').write_text(json.dumps({'frame':frame,'error':str(exc)})+'\n')
                raise
            head=rig.pose.bones['MF185_head'];matrix=rig.matrix_world@head.matrix@head.bone.matrix_local.inverted()@rig.matrix_world.inverted()
            g=gp@np.array(matrix)[:3,:3].T+np.array(matrix)[:3,3]
            frames.append(q);groom_frames.append(g)
            if frame in sample_frames:
                bt=BVHTree.FromPolygons(q.tolist(),faces.tolist(),all_triangles=True)
                pairs=[(a,b) for a,b in bt.overlap(bt) if a<b and not set(faces[a])&set(faces[b])]
                # Distinguish irrelevant capped lower regions from the shawl's
                # upper support region; retain both, never silently discard.
                upper=[(a,b) for a,b in pairs if q0[faces[a],2].mean()>-3.5 or q0[faces[b],2].mean()>-3.5]
                audits.append({'frame':frame,'body_self_pairs':len(pairs),'upper_self_pairs':len(upper),
                    'examples':[{'triangles':[a,b],'center':q[faces[a]].mean(0).tolist(),'rest_center':q0[faces[a]].mean(0).tolist()} for a,b in upper[:16]]})
                (out/'pose-audit.json').write_text(json.dumps(audits,indent=2)+'\n')
                print('185 contact sample',frame,len(pairs),len(upper),flush=True)
            if frame%24==0:print('185 actual surface contact',frame,flush=True)
    for m,state in flags:m.show_viewport=state
    np.savez_compressed(out/'surface-contact.npz',frame_ids=np.array(list(frame_ids)),body_points=q0,body_faces=faces,body_frames=np.array(frames),
        groom_points=gp,groom_faces=gf,groom_frames=np.array(groom_frames),anchors=anchors,barycentric=barys,offsets=offsets)
    report={'source_sha256':DIAGNOSTIC_SHA,'body_vertices':len(q0),'body_faces':len(faces),'groom_vertices':len(gp),
        'body_nonmanifold':nonmanifold,'groom_nonmanifold':groom_nonmanifold,'neutral_correspondence_error':parity,
        'poses':audits,'fidelity_gate':'NOT_RUN','visual_gate':'NOT_RUN','source_body_changed':False}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    scene.frame_set(348);bpy.context.view_layer.update();target=rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-.6))
    for ob in scene.objects:
        if ob.type in ('MESH','CURVE','CURVES'):ob.hide_render=True
    pose_index=list(frame_ids).index(348)
    for mod in list(cage.modifiers):cage.modifiers.remove(mod)
    for v,p in zip(cage.data.vertices,frames[pose_index]):v.co=p
    cage.data.update();cage.hide_render=False
    for v,p in zip(gm.vertices,groom_frames[pose_index]):v.co=p
    gm.update();gob=bpy.data.objects.new('MF185_groom_audit',gm);scene.collection.objects.link(gob)
    scene.cycles.device='CPU';scene.cycles.samples=8
    for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):fit_render(out,'contact-'+label,angle,tuple(target),8.,(640,640))
    check_protected()
