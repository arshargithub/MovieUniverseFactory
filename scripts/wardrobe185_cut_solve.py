"""Fixed open-strip cloth solve on the audited exterior actor envelope."""
import json
from pathlib import Path
import numpy as np


def run(out, motion=False):
    version=25 if motion else int(out.name.removeprefix('wardrobe185-cut'))
    articulated=out.name.endswith(('holdcheck01','motion03','motionoff03'))
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import wardrobe_motion178 as base
    import wardrobe_doublewrap185 as recipe
    import wardrobe185_cut as cut
    from wardrobe_doublewrap185_solve import inside
    from wardrobe_shawl180 import measures
    for path in (Path(__file__),Path(cut.__file__)):(out/path.name).write_bytes(path.read_bytes())
    closed=version>=15
    proxy=base.BASE/('wardrobe185-proxy03/proxy.npz' if closed else 'wardrobe185-proxy02/proxy.npz')
    proxy_sha='566257ec73b43170c6ad5414b8936ef537b7373b2d57de967286f13e3f091029' if closed else '19cce587247a325e2f0b081f49e14eb0a40bf6c3364896a327af4639a6d4f7eb'
    if base.digest(proxy)!=proxy_sha:raise ValueError('Envelope mismatch')
    with np.load(proxy,allow_pickle=False) as d:cp=d['points'];cf=d['faces']
    with np.load(recipe.HEAD,allow_pickle=False) as d:hp=cut.headfall(d['frames'][-1]);hf=d['faces']
    staged=version>=14
    head_rest=None;head_pins=None
    if staged:
        head_path=base.BASE/'wardrobe185-headdress02/trajectory.npz'
        head_sha='7fd22461eed787b5aa7ad237a87faa65277d584f01172c2f64027adc4e70633d'
        if version>=21:
            head_path=base.BASE/'wardrobe185-headdress04/trajectory.npz'
            head_sha='23c22dd0088aae880dca4cda8f42eb441c9b8d11e305690e5753895255871051'
        if base.digest(head_path)!=head_sha:raise ValueError('Staged head changed')
        with np.load(head_path,allow_pickle=False) as d:
            hp=d['frames'][-1];hf=d['faces'];head_rest=d['rest'];head_pins=dict(zip(d['pin_indices'].tolist(),d['pin_weights'].tolist()))
        (out/'staged-input.json').write_text(json.dumps({'head':str(head_path),'sha256':head_sha})+'\n')
    if version==12:
        grid=hp.reshape(25,49,3)
        for i in range(17,25):
            t=(i-16)/8;t=t*t*(3-2*t)
            grid[i,:,2]+=.90*t
        hp=grid.reshape(-1,3)
    p=[hp];f=[hf];rest=[hp.copy()];counts=[len(hp)];offset=len(hp)
    pins={i:1. for i in range(20,29)}
    if staged:pins=head_pins
    if version in (12,13):
        # Crown friction/support and concealed rear hem tucks. No shoulder
        # tabs or broad rigid hood; these supports must later follow the rig.
        pins.update({i:.8 for i in list(range(18,20))+list(range(29,31))})
        for i in (0,48):pins[i]=.8
        for i in (49,97):pins[i]=.5
        tuck_row=20 if version==13 else 24
        for j in range(18,31):pins[tuck_row*49+j]=.8 if 22<=j<=26 else .5
    for layer in (0,1):
        q,g,r,holds=cut.closed_course(layer,tailored=version>=20,fitted=version>=21,tucked=version>=23) if closed else cut.strips(layer)
        p.append(q);f.append(g+offset);rest.append(r+np.array([20+20*layer,0,0]))
        pins.update({k+offset:v for k,v in holds.items()});counts.append(len(q));offset+=len(q)
    p=np.concatenate(p);f=np.concatenate(f);rest=np.concatenate(rest)
    layered=version>=6
    if layered:
        p,layer_record=cut.separate_layers(p,f,counts,margin=.15 if out.name.endswith(('cut07','cut08')) else .10,periodic=closed,subsample=version>=22)
        (out/'layer-conditioning.json').write_text(json.dumps(layer_record,indent=2)+'\n')
        np.savez_compressed(out/'layer-layout.npz',points=p,faces=f,counts=counts)
        if any(r['initial_layer_crossings'] for r in layer_record):raise ValueError('Starting layers still cross; do not simulate')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scale=.12292759120464325
    scene=bpy.context.scene;scene.render.fps=24;scene.gravity=(0,0,-9.81);scene.unit_settings.scale_length=scale
    canonical=None
    if motion:
        library=base.BASE/('wardrobe185-motionprep02/motion-rig.blend' if articulated else 'wardrobe185-motionprep01/motion-rig.blend')
        library_sha='a76ec35c1268ab77bbfc6fc9bdb8e330cdad8dbcee11b27b2eee9c7390df3b7f' if articulated else '49f17f288ab056a3620a8eb8d94c4123ef3318097b78f8b1e527fe3716196835'
        if base.digest(library)!=library_sha:raise ValueError('Diagnostic motion library changed')
        names=['MF178_metres_rig','MF178_support_185_contact']
        with bpy.data.libraries.load(str(library),link=False) as (available,loaded):
            if not all(n in available.objects for n in names):raise ValueError('Incomplete motion library')
            loaded.objects=names
        for ob in loaded.objects:scene.collection.objects.link(ob)
        # Blender replaces entries of data_to.objects with loaded IDs; it
        # may mutate the assigned list rather than preserving name strings.
        canonical,contact=loaded.objects
        if canonical.type!='ARMATURE' or contact.type!='MESH':raise ValueError('Unexpected motion library object types')
        if not np.allclose(np.array([v.co[:] for v in contact.data.vertices]),cp*scale,atol=2e-7):raise ValueError('Motion contact basis changed')
        from wardrobe185_motion import schedule
        import math
        bpy.ops.object.effector_add(type='WIND',location=(4*scale,-3*scale,0))
        wind=bpy.context.object;wind.name='MF185_diagnostic_wind';wind.rotation_euler=(math.radians(72),0,math.radians(-25))
        gain=0. if out.name.endswith(('motionoff01','motionoff03')) else 1.
        for frame in list(range(1,361,4))+[360]:
            wind.field.strength=schedule(frame)['wind']*gain;wind.keyframe_insert(data_path='field.strength',frame=frame)
        scene.frame_set(1)
    else:
        mesh=bpy.data.meshes.new('Contact');mesh.from_pydata((cp*scale).tolist(),[],cf.tolist());mesh.update()
        contact=bpy.data.objects.new('Contact',mesh);scene.collection.objects.link(contact)
    bpy.context.view_layer.objects.active=contact
    if not closed:
        dec=contact.modifiers.new('Contact reduction','DECIMATE');dec.ratio=min(1,12000/len(cf));bpy.ops.object.modifier_apply(modifier=dec.name)
    contact.data.calc_loop_triangles()
    vertices=np.array([v.co[:] for v in contact.data.vertices]);triangles=np.array([t.vertices[:] for t in contact.data.loop_triangles])
    tree=BVHTree.FromPolygons(vertices.tolist(),triangles.tolist(),all_triangles=True)
    distances=[];raw=p.copy();winding_fallbacks=0
    for i,point in enumerate(p*scale):
        if version>=19 and i>=len(hp):
            distances.append(0.);continue
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
    if version>=19:
        p,radial_max=cut.radial_actor_fit(p,tree,len(hp),scale)
        (out/'radial-dressing.json').write_text(json.dumps({'maximum_m':radial_max,'preserves_course_height':True})+'\n')
    if version>=16:
        iterations=[]
        for iteration in range(8 if version>=17 else 1):
            if iteration:
                # Joint initial admissibility, never a solved-frame repair.
                # Recheck both constraints after each small contact step.
                for entry in violations:
                    if version>=19 and entry['index']>=len(hp):continue
                    i=entry['index'];q=Vector(p[i]*scale);h,n,_,_=tree.find_nearest(q)
                    direction=h-q if entry['inside'] else q-h
                    if direction.length<1e-7:direction=n
                    p[i]=np.array(h+direction.normalized()*.006)/scale
                if version>=19:p,_=cut.radial_actor_fit(p,tree,len(hp),scale)
            p,final_layers=cut.separate_layers(p,f,counts,periodic=True,subsample=version>=22)
            if any(r['initial_layer_crossings'] for r in final_layers):raise ValueError('Layer ordering failed after actor fit')
            violations=[]
            for i,point in enumerate(p*scale):
                q=Vector(point)
                try:within=inside(tree,q)
                except ValueError:within=cut.winding_inside(point,vertices[triangles])
                distance=tree.find_nearest(q)[3]
                if within or distance<.0035:violations.append({'index':i,'inside':within,'distance_m':distance})
            iterations.append({'iteration':iteration,'actor_violations':len(violations),'layers':final_layers})
            if not violations:break
        (out/'dressing-order.json').write_text(json.dumps({'order':'Joint actor clearance and inner-to-outer initial dressing','iterations':iterations},indent=2)+'\n')
        (out/'final-actor-clearance.json').write_text(json.dumps({'violations':violations},indent=2)+'\n')
        if violations:raise ValueError('Final layer dressing violated actor clearance')
        edge_lengths=np.concatenate([np.linalg.norm(p[f[:,i]]-p[f[:,(i+1)%4]],axis=1) for i in range(4)])*scale
        ids=np.concatenate([f[:,[i,(i+1)%4]] for i in range(4)])
        worst=np.argsort(edge_lengths)[:12]
        (out/'edge-admission.json').write_text(json.dumps({'minimum_m':float(edge_lengths.min()),'worst':[{'ids':ids[k].tolist(),'points':p[ids[k]].tolist(),'length_m':float(edge_lengths[k])} for k in worst]},indent=2)+'\n')
        np.savez_compressed(out/'final-initial-layout.npz',points=p,faces=f,rest=rest,counts=counts)
        if edge_lengths.min()<.001:raise ValueError('Initial conditioning collapsed a cloth edge')
    rest[:len(hp)]=p[:len(hp)]
    if layered:
        rest[:len(hp)]=head_rest if staged else cut.rectangular_metric(p[:len(hp)],25,49,typical=version>=10)
        if version>=10 and not closed:
            offset=len(hp)
            for count in counts[1:]:
                rest[offset:offset+count]=cut.rectangular_metric(p[offset:offset+count],113,21,typical=True)
                if staged:
                    # Cut width is an explicit fabric choice, not the narrow
                    # width of its gathered dressed cross-section.
                    rest[offset:offset+count,1]*=(.175/.12292759120464325)/np.ptp(rest[offset:offset+count,1])
                offset+=count
        offset=int(counts[0]);pairs=[]
        for count in counts[1:]:
            a=BVHTree.FromPolygons(p.tolist(),f[f[:,0]<offset].tolist())
            b=BVHTree.FromPolygons(p.tolist(),f[(f[:,0]>=offset)&(f[:,0]<offset+count)].tolist())
            pairs.append(len(a.overlap(b)));offset+=count
        (out/'post-contact-layer-check.json').write_text(json.dumps({'crossings':pairs})+'\n')
        if any(pairs):raise ValueError('Actor clearance reintroduced a layer crossing')
    if closed:
        offset=0;self_pairs=[]
        for count in counts:
            g=f[(f[:,0]>=offset)&(f[:,0]<offset+count)]
            tree=BVHTree.FromPolygons(p.tolist(),g.tolist())
            pairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not set(g[a])&set(g[b])]
            self_pairs.append(len(pairs));offset+=count
        (out/'initial-self-contact.json').write_text(json.dumps({'nonadjacent_crossings':self_pairs})+'\n')
        if any(self_pairs):raise ValueError('Reject initial self-crossing garment')
    np.savez_compressed(out/'construction.npz',points=p,raw=raw,faces=f,rest=rest,counts=counts,pin_indices=list(pins),pin_weights=list(pins.values()))
    contact.modifiers.new('Collision','COLLISION');contact.collision.thickness_outer=.0015;contact.collision.cloth_friction=15
    domain=bpy.data.collections.new('Contact domain');scene.collection.children.link(domain);domain.objects.link(contact)
    mesh=bpy.data.meshes.new('Scarf');mesh.from_pydata((p*scale).tolist(),[],f.tolist());mesh.update()
    ob=bpy.data.objects.new('Scarf',mesh);scene.collection.objects.link(ob)
    if motion:
        from wardrobe_motion178_controls import bind
        if articulated:
            from wardrobe185_motion import support_sampler
            bind(ob,canonical,support_sampler(contact,scale),scale=scale)
        else:bind(ob,canonical,scale=scale,chest_only=True)
    group=ob.vertex_groups.new(name='support')
    for i,w in pins.items():group.add([i],w,'REPLACE')
    ob.shape_key_add(name='Basis');flat=ob.shape_key_add(name='Tailored head and flat scarf metrics')
    for v,q in zip(flat.data,rest*scale):v.co=q
    flat.value=0.;ob.active_shape_key_index=0;ob.show_only_shape_key=False
    if version>=23:
        # Dressing pre-roll draws the concealed rear seam toward an actual
        # support surface. The earlier world-fixed holds had frozen a large
        # construction clearance in place. Free head/course fabric must
        # respond through self/contact simulation, not post-solve warping.
        target=ob.shape_key_add(name='Concealed rear tuck dressing');record=[]
        actor_tree=BVHTree.FromPolygons(vertices.tolist(),triangles.tolist(),all_triangles=True)
        head_tree=BVHTree.FromPolygons((p[:counts[0]]*scale).tolist(),hf.tolist())
        for layer in (0,1):
            offset=int(counts[0])+layer*int(counts[1])
            for row in (110,111,0,1,2):
                for col in range(8,13):
                    index=offset+row*21+col;q=Vector(p[index]*scale)
                    origin=Vector((0,.30*scale,q.z));direction=q-origin
                    radius=direction.length;direction.normalize();ray=origin.copy();outer=0.
                    for _ in range(64):
                        hit,_,_,_=actor_tree.ray_cast(ray,direction,2.)
                        if hit is None:break
                        outer=max(outer,(hit-origin).dot(direction));ray=hit+direction*1e-5
                    else:raise ValueError('Rear support ray failed')
                    if outer<=0:raise ValueError('No rear support surface')
                    distance_target=outer+.012+.010*layer
                    if version>=24:
                        # Preserve clearance to the actual underlying sheet,
                        # not merely the body beneath that folded sheet.
                        ray=origin.copy();head_outer=0.
                        for _ in range(64):
                            hit,_,_,_=head_tree.ray_cast(ray,direction,2.)
                            if hit is None:break
                            head_outer=max(head_outer,(hit-origin).dot(direction));ray=hit+direction*1e-5
                        else:raise ValueError('Rear inner-sheet query failed')
                        distance_target=max(distance_target,head_outer+.007+.008*layer)
                    destination=origin+direction*min(radius,distance_target)
                    if actor_tree.find_nearest(destination)[3]<.005:raise ValueError('Rear tuck lacks body clearance')
                    target.data[index].co=destination
                    record.append({'index':index,'travel_m':(destination-q).length,'actor_clearance_m':actor_tree.find_nearest(destination)[3],'target_m':list(destination)})
        target.value=0.;target.keyframe_insert(data_path='value',frame=1)
        target.value=1.;target.keyframe_insert(data_path='value',frame=72)
        target.value=0.;scene.frame_set(1)
        ob.active_shape_key_index=0
        (out/'rear-tuck-dressing.json').write_text(json.dumps({'kind':'Pre-roll kinematic concealed seam draw, not post-solve displacement','points':record},indent=2)+'\n')
    if out.name.endswith(('cut04','cut05')) or layered:
        weld=ob.modifiers.new('Rest metric evaluation workaround','WELD');weld.merge_threshold=1e-6
        bpy.context.view_layer.update()
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
        evaluated=np.array([v.co[:] for v in m.vertices]);evaluated_faces=np.array([v.vertices[:] for v in m.polygons])
        ev.to_mesh_clear()
        if evaluated.shape!=p.shape or not np.allclose(evaluated,p*scale,atol=1e-7) or not np.array_equal(evaluated_faces,f):
            raise ValueError('Rest metric workaround changed geometry or indexing')
        (out/'rest-workaround.json').write_text(json.dumps({'vertex_positions_and_face_indices_preserved':True,'threshold_m':1e-6,'positive_control':'wardrobe185-restunit03/weld'},indent=2)+'\n')
    if articulated:
        from wardrobe185_motion import hold_preflight
        hold_preflight(ob,contact,pins,out,scale)
        if out.name.endswith('holdcheck01'):return
    mod=recipe.cloth_settings(ob,1,domain);mod.settings.rest_shape_key=flat
    mod.settings.use_dynamic_mesh=False
    mod.settings.mass=.3;mod.settings.air_damping=.2;mod.settings.bending_stiffness=.05
    if version==11:mod.settings.bending_stiffness=.0005
    mod.settings.tension_stiffness=200;mod.settings.compression_stiffness=200;mod.settings.shear_stiffness=100
    end=360 if motion else 168 if version>=23 else 96
    mod.settings.quality=24;mod.point_cache.frame_end=end
    if version==24:
        mod.collision_settings.collision_quality=8
        mod.collision_settings.self_distance_min=.003
    samples=[];matrices=[];contact_samples=[];contact_frames=[]
    for frame in range(1,end+1):
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
        if motion:
            from mathutils import Matrix
            delta=canonical.matrix_world@canonical.pose.bones['chest'].matrix@canonical.data.bones['chest'].matrix_local.inverted()@canonical.matrix_world.inverted()
            matrices.append(np.array(Matrix.Scale(1/scale,4)@delta@Matrix.Scale(scale,4)))
            if frame in (1,169,193,217,265,360):
                ev=contact.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
                contact_samples.append(np.array([v.co[:] for v in m.vertices])/scale);contact_frames.append(frame);ev.to_mesh_clear()
        if frame%12==0:print('185 tailored drape',frame,flush=True)
    np.savez_compressed(out/'trajectory.npz',points=p,faces=f,rest=rest,frames=np.array(samples),counts=counts,pin_indices=list(pins),pin_weights=list(pins.values()))
    if motion:
        np.savez_compressed(out/'motion-proof.npz',chest_matrices=np.array(matrices),contact_frames=contact_frames,contact_points=np.array(contact_samples),contact_faces=cf)
    report={'dressed_metric':measures(p,f,{1:samples[0],48:samples[47],end:samples[-1]},scale),
        'fabric_metric':measures(rest,f,{1:samples[0],48:samples[47],end:samples[-1]},scale),
        'mass_is_physical_calibration':False,'visual_gate':'NOT_RUN','motion_gate':'NOT_RUN',
        'construction':('Staged clean headfall and two concealed-join courses with developable cylindrical rest metrics' if closed else 'Clean lower headfall; open overlapping strips with rectangular rest metrics and concealed rear holds'),
        'source_actor_not_loaded_or_changed':True,'scale':scale,'diagnostic_motion_executed':motion,
        'actual_trailer_gallop_qualified':False}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
