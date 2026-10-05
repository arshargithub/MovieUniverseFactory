"""Fixed open-strip cloth solve on the audited exterior actor envelope."""
import json
from pathlib import Path
import numpy as np


def run(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import wardrobe_motion178 as base
    import wardrobe_doublewrap185 as recipe
    import wardrobe185_cut as cut
    from wardrobe_doublewrap185_solve import inside
    from wardrobe_shawl180 import measures
    for path in (Path(__file__),Path(cut.__file__)):(out/path.name).write_bytes(path.read_bytes())
    proxy=base.BASE/'wardrobe185-proxy02/proxy.npz'
    if base.digest(proxy)!='19cce587247a325e2f0b081f49e14eb0a40bf6c3364896a327af4639a6d4f7eb':raise ValueError('Envelope mismatch')
    with np.load(proxy,allow_pickle=False) as d:cp=d['points'];cf=d['faces']
    with np.load(recipe.HEAD,allow_pickle=False) as d:hp=cut.headfall(d['frames'][-1]);hf=d['faces']
    p=[hp];f=[hf];rest=[hp.copy()];counts=[len(hp)];offset=len(hp)
    pins={i:1. for i in range(20,29)}
    for layer in (0,1):
        q,g,r,holds=cut.strips(layer);p.append(q);f.append(g+offset);rest.append(r+np.array([20+20*layer,0,0]))
        pins.update({k+offset:v for k,v in holds.items()});counts.append(len(q));offset+=len(q)
    p=np.concatenate(p);f=np.concatenate(f);rest=np.concatenate(rest)
    layered=out.name.endswith(('cut06','cut07','cut08','cut09','cut10'))
    if layered:
        p,layer_record=cut.separate_layers(p,f,counts,margin=.15 if out.name.endswith(('cut07','cut08')) else .10)
        (out/'layer-conditioning.json').write_text(json.dumps(layer_record,indent=2)+'\n')
        np.savez_compressed(out/'layer-layout.npz',points=p,faces=f,counts=counts)
        if any(r['initial_layer_crossings'] for r in layer_record):raise ValueError('Starting layers still cross; do not simulate')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scale=.12292759120464325
    scene=bpy.context.scene;scene.render.fps=24;scene.gravity=(0,0,-9.81);scene.unit_settings.scale_length=scale
    mesh=bpy.data.meshes.new('Contact');mesh.from_pydata((cp*scale).tolist(),[],cf.tolist());mesh.update()
    contact=bpy.data.objects.new('Contact',mesh);scene.collection.objects.link(contact);bpy.context.view_layer.objects.active=contact
    dec=contact.modifiers.new('Contact reduction','DECIMATE');dec.ratio=min(1,12000/len(cf));bpy.ops.object.modifier_apply(modifier=dec.name)
    contact.data.calc_loop_triangles()
    vertices=np.array([v.co[:] for v in contact.data.vertices]);triangles=np.array([t.vertices[:] for t in contact.data.loop_triangles])
    tree=BVHTree.FromPolygons(vertices.tolist(),triangles.tolist(),all_triangles=True)
    distances=[];raw=p.copy();winding_fallbacks=0
    for i,point in enumerate(p*scale):
        q=Vector(point);h,n,_,distance=tree.find_nearest(q)
        try:within=inside(tree,q)
        except ValueError:
            within=cut.winding_inside(point,vertices[triangles]);winding_fallbacks+=1
        if within or distance<.005:
            direction=h-q if within else q-h
            if direction.length<1e-7:direction=n
            q=h+direction.normalized()*.005
        distances.append((q-Vector(point)).length);p[i]=np.array(q)/scale
    (out/'conditioning.json').write_text(json.dumps({'max_m':max(distances),'adjusted':sum(d>1e-7 for d in distances),'winding_fallbacks':winding_fallbacks},indent=2)+'\n')
    if max(distances)>.03:raise ValueError('Reconstruct cut before solving excessive penetration')
    rest[:len(hp)]=p[:len(hp)]
    if layered:
        rest[:len(hp)]=cut.rectangular_metric(p[:len(hp)],25,49,typical=out.name.endswith('cut10'))
        if out.name.endswith('cut10'):
            offset=len(hp)
            for count in counts[1:]:
                rest[offset:offset+count]=cut.rectangular_metric(p[offset:offset+count],113,21,typical=True)
                offset+=count
        offset=int(counts[0]);pairs=[]
        for count in counts[1:]:
            a=BVHTree.FromPolygons(p.tolist(),f[f[:,0]<offset].tolist())
            b=BVHTree.FromPolygons(p.tolist(),f[(f[:,0]>=offset)&(f[:,0]<offset+count)].tolist())
            pairs.append(len(a.overlap(b)));offset+=count
        (out/'post-contact-layer-check.json').write_text(json.dumps({'crossings':pairs})+'\n')
        if any(pairs):raise ValueError('Actor clearance reintroduced a layer crossing')
    np.savez_compressed(out/'construction.npz',points=p,raw=raw,faces=f,rest=rest,counts=counts,pin_indices=list(pins),pin_weights=list(pins.values()))
    contact.modifiers.new('Collision','COLLISION');contact.collision.thickness_outer=.0015;contact.collision.cloth_friction=15
    domain=bpy.data.collections.new('Contact domain');scene.collection.children.link(domain);domain.objects.link(contact)
    mesh=bpy.data.meshes.new('Scarf');mesh.from_pydata((p*scale).tolist(),[],f.tolist());mesh.update()
    ob=bpy.data.objects.new('Scarf',mesh);scene.collection.objects.link(ob)
    group=ob.vertex_groups.new(name='support')
    for i,w in pins.items():group.add([i],w,'REPLACE')
    ob.shape_key_add(name='Basis');flat=ob.shape_key_add(name='Tailored head and flat scarf metrics')
    for v,q in zip(flat.data,rest*scale):v.co=q
    flat.value=0.;ob.active_shape_key_index=0;ob.show_only_shape_key=False
    if out.name.endswith(('cut04','cut05')) or layered:
        weld=ob.modifiers.new('Rest metric evaluation workaround','WELD');weld.merge_threshold=1e-6
        bpy.context.view_layer.update()
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
        evaluated=np.array([v.co[:] for v in m.vertices]);evaluated_faces=np.array([v.vertices[:] for v in m.polygons])
        ev.to_mesh_clear()
        if evaluated.shape!=p.shape or not np.allclose(evaluated,p*scale,atol=1e-7) or not np.array_equal(evaluated_faces,f):
            raise ValueError('Rest metric workaround changed geometry or indexing')
        (out/'rest-workaround.json').write_text(json.dumps({'vertex_positions_and_face_indices_preserved':True,'threshold_m':1e-6,'positive_control':'wardrobe185-restunit03/weld'},indent=2)+'\n')
    mod=recipe.cloth_settings(ob,1,domain);mod.settings.rest_shape_key=flat
    mod.settings.use_dynamic_mesh=False
    mod.settings.mass=.3;mod.settings.air_damping=.2;mod.settings.bending_stiffness=.05
    mod.settings.tension_stiffness=200;mod.settings.compression_stiffness=200;mod.settings.shear_stiffness=100
    mod.settings.quality=24;mod.point_cache.frame_end=96
    samples=[]
    for frame in range(1,97):
        scene.frame_set(frame);bpy.context.view_layer.update()
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
        q=np.array([v.co[:] for v in m.vertices])/scale;ev.to_mesh_clear()
        if q.shape!=p.shape or not np.isfinite(q).all() or abs(q).max()>50:
            failure={'frame':frame,'shape':list(q.shape),'finite':bool(np.isfinite(q).all()),
                'max_abs_native':float(np.nanmax(abs(q))),'active_key':ob.active_shape_key_index,
                'flat_value':flat.value,'show_only_key':ob.show_only_shape_key}
            (out/'failure.json').write_text(json.dumps(failure,indent=2)+'\n')
            np.savez_compressed(out/'failed-frame.npz',points=q,frames=np.array(samples))
            raise ValueError('Invalid tailored drape: '+json.dumps(failure))
        samples.append(q)
        if frame%12==0:print('185 tailored drape',frame,flush=True)
    np.savez_compressed(out/'trajectory.npz',points=p,faces=f,rest=rest,frames=np.array(samples),counts=counts,pin_indices=list(pins),pin_weights=list(pins.values()))
    report={'dressed_metric':measures(p,f,{1:samples[0],48:samples[47],96:samples[-1]},scale),
        'fabric_metric':measures(rest,f,{1:samples[0],48:samples[47],96:samples[-1]},scale),
        'mass_is_physical_calibration':False,'visual_gate':'NOT_RUN','motion_gate':'NOT_RUN',
        'construction':'Clean lower headfall; open overlapping strips with rectangular rest metrics and concealed rear holds',
        'source_actor_not_loaded_or_changed':True,'scale':scale}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
