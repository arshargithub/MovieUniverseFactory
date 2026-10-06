"""Static contact-family ablation with identical admitted initial cloth."""
import json
from pathlib import Path
import numpy as np


def remeshed_pants(contact,out):
    import bpy,bmesh
    from wardrobe185_lower_cloth import panel
    ob=panel('Clean pants contact',contact['pants_frames'][1],contact['pants_faces'])
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    ob.data.remesh_voxel_size=.025
    bpy.ops.object.voxel_remesh()
    mod=ob.modifiers.new('Contact relaxation','SMOOTH');mod.factor=.3;mod.iterations=2
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=ob.modifiers.new('Contact resolution','DECIMATE');mod.ratio=min(1,6000/len(ob.data.polygons))
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges)
    bm.to_mesh(ob.data);bm.free()
    p=np.array([v.co[:] for v in ob.data.vertices]);f=np.array([v.vertices[:] for v in ob.data.polygons])
    np.savez_compressed(out/'remeshed-pants.npz',points=p,faces=f)
    (out/'proxy-construction.json').write_text(json.dumps({'vertices':len(p),'faces':len(f),'nonmanifold_edges':bad,
        'scope':'Static mounted169 collision surface only. Not animated or visually admitted.'},indent=2)+'\n')
    if bad:raise ValueError('Pants-only remesh is not closed')
    bpy.data.objects.remove(ob,do_unlink=True)
    return p,f


def run(out):
    import bpy
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_lower_cloth import panel,profile,sample,COMPLETE_LAYOUT_SHA
    from wardrobe185_lower_hold import SURFACE_SHA
    from wardrobe185_lower_drape import SCALE
    from wardrobe_shawl180_cache import cache
    paths=[(BASE/'wardrobe185-lowerhold02/initial-169.npz','b088f7fb5779df6136906a90906110e97cb17f39dcb9c2943d50156592b3605d'),
        (BASE/'wardrobe185-lowerdress14/initial-layout.npz',COMPLETE_LAYOUT_SHA),
        (BASE/'wardrobe185-lowersurface07/surfaces.npz',SURFACE_SHA)]
    for p,h in paths:
        if digest(p)!=h:raise ValueError('Ablation input changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(paths[0][0],allow_pickle=False) as d:p=d['points']*SCALE;rest=d['rest']*SCALE;faces=d['faces']
    with np.load(paths[1][0],allow_pickle=False) as d:pins=d['pin_indices'];weights=d['pin_weights']
    with np.load(paths[2][0],allow_pickle=False) as d:contact={k:d[k] for k in d.files}
    edges=np.unique(np.sort(np.concatenate([faces[:,[i,(i+1)%4]] for i in range(4)]),axis=1),axis=0)
    lengths=np.linalg.norm(rest[edges[:,0]]-rest[edges[:,1]],axis=1);records={}
    revised=out.name.endswith('lowerisolate02')
    remesh=None
    if revised:
        bpy.ops.wm.read_factory_settings(use_empty=True);remesh=remeshed_pants(contact,out)
        from mathutils import Vector
        from mathutils.bvhtree import BVHTree
        from wardrobe185_lower_surface import winding_numbers
        tree=BVHTree.FromPolygons(remesh[0].tolist(),remesh[1].tolist(),all_triangles=True)
        ct=BVHTree.FromPolygons((p/SCALE).tolist(),faces.tolist())
        inside=int(np.count_nonzero(abs(winding_numbers(p/SCALE,*remesh))>.5));crossings=len(tree.overlap(ct))
        clearance=min(tree.find_nearest(Vector(point/SCALE))[3]*SCALE for point in p[pins])
        (out/'changed-contact-admission.json').write_text(json.dumps({'inside':inside,'cloth_face_pairs':crossings,
            'minimum_supported_clearance_m':clearance,'unchanged_initial_geometry':True})+'\n')
        if inside or crossings or clearance<.0035-1e-5:raise ValueError('Remeshed pants invalidates initial/support clearance')
    cases=(('pants',('pants',)),('all',('pants','upper','horse','saddle','pad'))) if revised else (
        ('no_external',()),('pants',('pants',)),('upper',('upper',)),('mount',('horse','saddle','pad')))
    for label,names in cases:
        bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=24
        scene.gravity=(0,0,-9.81);scene.unit_settings.scale_length=1.
        ob=panel('Lower admitted cloth',p,faces);ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Rest metric')
        key.data.foreach_set('co',rest.astype(np.float32).ravel())
        group=ob.vertex_groups.new(name='support')
        for i,w in zip(pins,weights):group.add([int(i)],float(w),'REPLACE')
        cache(ob,np.repeat(p[None],120,axis=0),out/(label+'-drive.mdd'))
        weld=ob.modifiers.new('Explicit rest evaluation','WELD');weld.merge_threshold=1e-7
        domain=bpy.data.collections.new('Contact family');scene.collection.children.link(domain)
        for name in names:
            cp,cf=remesh if revised and name=='pants' else (contact[name+'_frames'][1],contact[name+'_faces'])
            co=panel(name,cp*SCALE,cf)
            domain.objects.link(co);co.modifiers.new('Contact','COLLISION')
            co.collision.thickness_outer=.0015;co.collision.cloth_friction=15
        mod=profile(ob,domain);mod.settings.rest_shape_key=key;mod.settings.quality=48
        mod.collision_settings.collision_quality=8;mod.point_cache.frame_end=120
        frames=[];metrics=[]
        for frame in range(1,121):
            scene.frame_set(frame);bpy.context.view_layer.update();q=sample(ob);frames.append(q/SCALE)
            if not np.isfinite(q).all():raise ValueError('Nonfinite isolated cloth')
            if frame%24==0:
                ratio=np.linalg.norm(q[edges[:,0]]-q[edges[:,1]],axis=1)/lengths
                row={'frame':frame,'edge_quantiles':np.quantile(ratio,[.01,.5,.99,1]).tolist()};metrics.append(row)
                (out/(label+'-metrics.json')).write_text(json.dumps(metrics,indent=2)+'\n')
                print('Lower isolated',label,json.dumps(row),flush=True)
                if frame>=72 and row['edge_quantiles'][2]>2:break
        np.savez_compressed(out/(label+'.npz'),frames=np.array(frames),faces=faces,rest=rest/SCALE)
        records[label]={'contacts':names,'frames':len(frames),'metrics':metrics,
            'remeshed_pants_contact':revised,
            'state':'METRIC_FAIL' if len(frames)<120 else 'COMPLETE_NOT_VISUAL_PASS'}
        (out/'result.json').write_text(json.dumps({'cases':records,'initial_geometry_identical':True,
            'scope':'Contact isolation only. Missing domains deliberately invalidate garment qualification.',
            'visual_gate':'NOT_RUN'},indent=2)+'\n')
