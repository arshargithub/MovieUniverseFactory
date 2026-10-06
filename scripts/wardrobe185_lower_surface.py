"""Actual-surface lower contacts, avoiding all-pose convex inflation.

Coarsen once at neutral; retain fixed barycentric source correspondence for
every required pose. Boundary caps close invisible waist/ankle openings.
No rendered actor geometry is changed and no dynamic cloth is projected.
"""
import json
from pathlib import Path
import numpy as np


def capture(out):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import WORKING_SHA
    from wardrobe185_lower import fast_geometry
    from wardrobe185_lower_drape import triangle_weights
    from wardrobe_motion178_controls import render_geometry_paused
    source=BASE/'wardrobe185-finishreview01/integration-working.blend'
    if digest(source)!=WORKING_SHA:raise ValueError('Unbound actual-surface input')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    names={'pants':'MF_fit_trousers_173_visible','horse':'MF185_gait_horse',
           'saddle':'MF185_gait_saddle','pad':'MF185_gait_saddle.pad'}
    objects={key:bpy.data.objects[name] for key,name in names.items()}
    flags=[(m,m.show_viewport) for ob in objects.values() for m in ob.modifiers if m.type=='SOLIDIFY']
    for m,_ in flags:m.show_viewport=False
    mapping={};records={};payload={}
    for key,ob in objects.items():
        p,f,sig=fast_geometry(ob,True)
        mesh=bpy.data.meshes.new('Lower contact '+key);mesh.from_pydata(p.tolist(),[],f.tolist());mesh.update()
        proxy=bpy.data.objects.new('MF185_contact_'+key,mesh);scene.collection.objects.link(proxy)
        bpy.context.view_layer.objects.active=proxy
        # Close existing render-mask boundaries before simplifying them.
        bm=bmesh.new();bm.from_mesh(proxy.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
        loose=[v for v in bm.verts if not v.link_faces]
        if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
        boundary=[e for e in bm.edges if e.is_boundary]
        if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(proxy.data);bm.free()
        mod=proxy.modifiers.new('Contact-only reduction','DECIMATE');mod.ratio=min(1,4000/len(f))
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bm=bmesh.new();bm.from_mesh(proxy.data)
        isolated=[v for v in bm.verts if not v.link_faces]
        bmesh.ops.delete(bm,geom=isolated,context='VERTS')
        boundary=[e for e in bm.edges if e.is_boundary]
        if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
        bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bad=sum(not e.is_manifold for e in bm.edges);bm.to_mesh(proxy.data);bm.free()
        if bad:
            (out/'contact-failure.json').write_text(json.dumps({'object':key,'bad_edges':bad,
                'vertices':len(proxy.data.vertices),'faces':len(proxy.data.polygons)})+'\n')
            raise ValueError('Actual lower contact is not closed: '+key+' '+str(bad))
        q=np.array([v.co[:] for v in proxy.data.vertices]);cf=np.array([poly.vertices[:] for poly in proxy.data.polygons])
        tree=BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True)
        ids=[];weights=[];distances=[]
        for point in q:
            hit,_,index,distance=tree.find_nearest(Vector(point));tri=f[index]
            ids.append(tri);weights.append(triangle_weights(hit,p[tri]));distances.append(distance)
        ids=np.array(ids);weights=np.array(weights)
        mapping[key]=(ids,weights,sig);payload[key+'_faces']=cf
        records[key]={'source_vertices':len(p),'contact_vertices':len(q),'contact_faces':len(cf),
            'closed':True,'max_nearest_transfer_native':max(distances),'source_polygon_signature':sig}
        bpy.data.objects.remove(proxy,do_unlink=True)
    required=set(objects.values())
    for _ in range(8):
        prior=len(required)
        for ob in list(required):
            for mod in ob.modifiers:
                for prop in ('target','object'):
                    target=getattr(mod,prop,None)
                    if isinstance(target,bpy.types.Object):required.add(target)
        if len(required)==prior:break
    frames=[1,*range(169,361)];samples={key:[] for key in names}
    with render_geometry_paused():
        for ob in required:ob.hide_viewport=False
        for frame in frames:
            scene.frame_set(frame);bpy.context.view_layer.update()
            for key,ob in objects.items():
                p,f,sig=fast_geometry(ob,True);ids,weights,expected=mapping[key]
                if sig!=expected:raise ValueError('Moving lower source topology changed: '+key)
                q=np.einsum('njk,nj->nk',p[ids],weights)
                if not np.isfinite(q).all():raise ValueError('Invalid lower contact sample')
                samples[key].append(q.astype(np.float32))
            if frame%24==0:print('185 actual lower surfaces',frame,flush=True)
    for m,state in flags:m.show_viewport=state
    np.savez_compressed(out/'surfaces.npz',frame_ids=frames,**payload,
        **{key+'_frames':np.array(value) for key,value in samples.items()})
    check_protected()
    (out/'result.json').write_text(json.dumps({'working_sha256':WORKING_SHA,'surfaces_sha256':digest(out/'surfaces.npz'),
        'objects':records,'protected_exact':True,'visual_gate':'NOT_RUN',
        'scope':'Actual moving coarse contacts; coverage and self-contact still require admission'},indent=2)+'\n')
