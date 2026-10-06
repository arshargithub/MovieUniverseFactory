"""One fixed-topology dressed-body exterior, not nested collision shells.

Neutral voxel union is advected through fixed source-triangle coordinates.
This is a collision-only candidate. Coverage, initial dressing, trajectory
continuity and rendered contacts still require independent admission.
"""
import json
from pathlib import Path
import numpy as np


def surface_frames(triangles):
    t=np.asarray(triangles)
    x=t[...,1,:]-t[...,0,:];length=np.linalg.norm(x,axis=-1)
    if np.any(length<1e-10):raise ValueError('Degenerate source contact edge')
    x/=length[...,None]
    z=np.cross(x,t[...,2,:]-t[...,0,:]);length=np.linalg.norm(z,axis=-1)
    if np.any(length<1e-10):raise ValueError('Degenerate source contact face')
    z/=length[...,None]
    y=np.cross(z,x)
    return np.stack((x,y,z),axis=-1)


def run(out):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_lower_cloth import panel
    from wardrobe185_lower_drape import triangle_weights
    source=BASE/'wardrobe185-lowersurface06/surfaces.npz'
    expected='3bf762fe9244188ef563a8ce1f235fb83c07614e7f538c8bc6209ff076e0499e'
    if digest(source)!=expected:raise ValueError('Exterior source changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(source,allow_pickle=False) as d:data={k:d[k] for k in d.files}
    chunks=[];faces=[];offset=0
    for name in ('body','upper','pants'):
        chunks.append(data[name+'_frames']);faces.append(data[name+'_faces']+offset)
        offset+=chunks[-1].shape[1]
    samples=np.concatenate(chunks,axis=1);source_faces=np.concatenate(faces)
    mounted_reference=out.name.endswith('lowerunion03')
    reference=1 if mounted_reference else 0
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ob=panel('Dressed body exterior',samples[reference],source_faces)
    bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('One exterior volume','REMESH');mod.mode='VOXEL';mod.voxel_size=.035
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=ob.modifiers.new('Light exterior fairing','SMOOTH');mod.factor=.3;mod.iterations=2
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=ob.modifiers.new('Contact resolution','DECIMATE');mod.ratio=min(1,6000/len(ob.data.polygons))
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges)
    bm.to_mesh(ob.data);bm.free()
    if bad:raise ValueError('Dressed exterior is not manifold')
    q=np.array([v.co[:] for v in ob.data.vertices]);cf=np.array([f.vertices[:] for f in ob.data.polygons])
    tree=BVHTree.FromPolygons(samples[reference].tolist(),source_faces.tolist(),all_triangles=True)
    indices=[];weights=[];offsets=[]
    for point in q:
        hit,_,index,_=tree.find_nearest(Vector(point));ids=source_faces[index]
        w=triangle_weights(hit,samples[reference,ids]);basis=surface_frames(samples[reference,ids])
        indices.append(ids);weights.append(w);offsets.append((point-w@samples[reference,ids])@basis)
    indices=np.array(indices);weights=np.array(weights);offsets=np.array(offsets)
    frames=[]
    continuous=mounted_reference or out.name.endswith('lowerunion02')
    if continuous:
        from wardrobe_shawl180_cache import cache
        from wardrobe185_lower_cloth import sample
        body=panel('One anatomical contact driver',data['body_frames'][reference],data['body_faces'])
        sequence=np.concatenate((data['body_frames'][reference:reference+1],data['body_frames']))
        cache(body,sequence,out/'body-contact.mdd')
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        deform=ob.modifiers.new('Continuous anatomical surface binding','SURFACE_DEFORM');deform.target=body
        bpy.context.view_layer.objects.active=ob
        bpy.ops.object.surfacedeform_bind(modifier=deform.name)
        if not deform.is_bound:raise ValueError('Exterior surface binding failed')
        for number in range(len(samples)):
            bpy.context.scene.frame_set(number+2);bpy.context.view_layer.update()
            actual=sample(ob)
            if not np.isfinite(actual).all():raise ValueError('Invalid exterior deformation')
            frames.append(actual.astype(np.float32))
    else:
        for number,points in enumerate(samples):
            tri=points[indices];basis=surface_frames(tri)
            actual=np.einsum('njk,nj->nk',tri,weights)+np.einsum('nij,nj->ni',basis,offsets)
            if not np.isfinite(actual).all():raise ValueError('Invalid advected exterior')
            frames.append(actual.astype(np.float32))
    frames=np.array(frames)
    if np.max(abs(frames[reference]-q))>2e-5:raise ValueError('Exterior reference reconstruction differs')
    edges=np.unique(np.sort(np.concatenate([cf[:,[i,(i+1)%3]] for i in range(3)]),axis=1),axis=0)
    lengths=np.linalg.norm(frames[:,edges[:,0]]-frames[:,edges[:,1]],axis=2)
    ratios=lengths[1:]/lengths[reference]
    payload={k:v for k,v in data.items() if k.split('_')[0] not in ('body','upper','pants')}
    np.savez_compressed(out/'surfaces.npz',**payload,exterior_frames=frames,exterior_faces=cf)
    np.savez_compressed(out/'correspondence.npz',indices=indices,weights=weights,local_offsets=offsets)
    (out/'result.json').write_text(json.dumps({'source_sha256':expected,'surfaces_sha256':digest(out/'surfaces.npz'),
        'vertices':len(q),'triangles':len(cf),'nonmanifold_edges':bad,'fixed_topology':True,
        'motion_mapping':'Native continuous body Surface Deform' if continuous else 'Independent nearest source triangle',
        'construction_source_frame':int(data['frame_ids'][reference]),
        'standing_scope':'Separate admitted standing layout/cache retained; mounted union is not a standing-to-mounting proof' if mounted_reference else 'Unqualified',
        'max_neutral_mapping_offset_mm':float(np.linalg.norm(offsets,axis=1).max()*122.92759120464325),
        'edge_ratio_quantiles':np.quantile(ratios,[0,.01,.5,.99,1]).tolist(),
        'admission':'NOT_RUN','visual_gate':'NOT_RUN','accepted_masters_not_opened':True},indent=2)+'\n')


def audit(out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_lower_surface import winding_numbers
    source=BASE/'wardrobe185-lowerunion03/surfaces.npz'
    actual=BASE/'wardrobe185-lowersurface06/surfaces.npz'
    if digest(source)!='aec530e8a9a47e9af509d9d99b777ed06c3cd24695af382e1fa381c79ba9691d':raise ValueError('Unbound exterior')
    if digest(actual)!='3bf762fe9244188ef563a8ce1f235fb83c07614e7f538c8bc6209ff076e0499e':raise ValueError('Unbound actual surfaces')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(source,allow_pickle=False) as d:data={k:d[k] for k in d.files}
    with np.load(actual,allow_pickle=False) as d:reference={k:d[k] for k in d.files}
    records={}
    for frame in (169,193,217,277,337,360):
        i=list(data['frame_ids']).index(frame);p=data['exterior_frames'][i];f=data['exterior_faces']
        tree=BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True)
        pairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not set(f[a])&set(f[b])]
        local=[(a,b) for a,b in pairs if -8.2<p[f[a],2].mean()<-4. and -8.2<p[f[b],2].mean()<-4.]
        row={'lower_nonadjacent_self_pairs':len(local),'coverage':{}}
        for name in ('body','upper','pants'):
            q=reference[name+'_frames'][i];q=q[(q[:,2]>-8.2)&(q[:,2]<-4.)][::3]
            candidates=[];distances=[]
            for point in q:
                hit,normal,_,distance=tree.find_nearest(Vector(point))
                if (Vector(point)-hit).dot(normal)>0 and distance*122.92759120464325>2.:
                    candidates.append(point);distances.append(distance*122.92759120464325)
            if candidates:
                w=winding_numbers(np.array(candidates),p,f);outside=abs(w)<.5
                measured=np.array(distances)[outside]
            else:measured=np.array([])
            row['coverage'][name]={'sample_count':len(q),'confirmed_exposed_beyond_2mm':len(measured),
                'maximum_exposure_mm':float(measured.max()) if len(measured) else 0.}
        records[frame]=row
    (out/'result.json').write_text(json.dumps({'frames':records,'visual_gate':'NOT_RUN',
        'scope':'Collision exterior diagnostic; 2mm is a coverage investigation threshold, not a visual acceptance claim'},indent=2)+'\n')


def gap_audit(out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest
    path=BASE/'wardrobe185-lowersurface06/surfaces.npz'
    cloth=BASE/'wardrobe185-lowerouter08/mounted.npz'
    for p,h in ((path,'3bf762fe9244188ef563a8ce1f235fb83c07614e7f538c8bc6209ff076e0499e'),
                (cloth,'cdf0becef0b57694bba353e48e0fe71e5f7625e756a4f19386ce30b74823fc17')):
        if digest(p)!=h:raise ValueError('Unbound contact-gap input')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(path,allow_pickle=False) as d:data={k:d[k] for k in d.files}
    with np.load(cloth,allow_pickle=False) as d:points=d['frames'][119:]
    records={}
    for frame in (169,193,216,217,223,265,326,360):
        i=list(data['frame_ids']).index(frame);trees={};row={'overlaps':{},'opposed_close_contacts':{}}
        for name in ('body','upper','pants','horse','saddle','pad'):
            trees[name]=BVHTree.FromPolygons(data[name+'_frames'][i].tolist(),data[name+'_faces'].tolist(),all_triangles=True)
        for actor in ('body','upper','pants'):
            for mount in ('horse','saddle','pad'):
                pairs=trees[actor].overlap(trees[mount]);f=data[actor+'_faces'];p=data[actor+'_frames'][i]
                central=[a for a,b in pairs if abs(p[f[a],0].mean())<.8 and -7.<p[f[a],2].mean()<-4.5]
                r={'all_pairs':len(pairs),'central_waist_pairs':len(central)}
                if central:
                    patch=p[np.unique(f[central])];r['central_patch_bounds']=[patch.min(0).tolist(),patch.max(0).tolist()]
                row['overlaps'][actor+'__'+mount]=r
            near=[]
            for index,p in enumerate(points[frame-169]):
                a,an,_,ad=trees[actor].find_nearest(Vector(p));b,bn,_,bd=trees['horse'].find_nearest(Vector(p))
                if ad<.0035/.12292759120464325 and bd<.0035/.12292759120464325 and an.dot(bn)<-.5:
                    near.append({'vertex':index,'position':p.tolist(),'actor_mm':ad*122.92759120464325,'horse_mm':bd*122.92759120464325})
            row['opposed_close_contacts'][actor]=near
        records[frame]=row
    (out/'result.json').write_text(json.dumps({'frames':records,'visual_gate':'NOT_RUN',
        'scope':'Coarse actor/horse contact compatibility; confirm any structural inference on exact rendered geometry'},indent=2)+'\n')
