"""Fixed supporting pigment/fabric grain; no anatomy, identity or action edits."""
import json
import importlib.util
from pathlib import Path

ATTRIBUTE='MF361 attached material rest'
SOURCE='.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-input-02/skin-authored.png'


def crop_bounds():
    # All three box-projection coordinate pairs stay in the same featureless
    # lower-left square. No eyes/nose/lips or identity transfer.
    return .01,.23


def waist_support(bpy,rig):
    """Post-deformation support from torso-only coat, never sleeves/hands."""
    spec=importlib.util.spec_from_file_location('waist353',Path(__file__).with_name('nihang_waist353.py'))
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    coat=bpy.data.objects['MF coherent coat'];band=bpy.data.objects['MF coherent waist wrap']
    if any(m.type not in {'ARMATURE','SUBSURF','SOLIDIFY'} for m in coat.modifiers):raise ValueError('LOOK361_COAT_SUPPORT_STACK')
    if coat.data.shape_keys:raise ValueError('LOOK361_UNSUPPORTED_COAT_KEYS')
    rows=[[(coat.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in coat.data.vertices]
    faces=[tuple(p.vertices) for p in coat.data.polygons];ids=helper.torso_faces(faces,rows)
    # Filtering faces BEFORE subdivision changes the boundary surface.89's
    # proxy therefore pulled the band inside the real coat. Use the actual
    # full evaluated coat instead; verify its contact owner on every frame.
    owned={v for i in ids for v in faces[i]}
    mask=coat.data.attributes.get('MF361 torso ownership') or coat.data.attributes.new('MF361 torso ownership','FLOAT','POINT')
    for i,datum in enumerate(mask.data):datum.value=1. if i in owned else 0.
    # Preserve the ENTIRE pre-thickness surface and its exact subdivision
    # neighborhood. A solid coat's hem/inner caps are not the dressed exterior.
    support=coat.copy();support.name='MF361 actual outer coat support'
    bpy.context.scene.collection.objects.link(support);support.hide_render=True
    for source in list(support.modifiers):
        if source.type=='SOLIDIFY':support.modifiers.remove(source)
    mod=band.modifiers.new('361 actual deformed torso support','SHRINKWRAP');mod.target=support
    #90 measured a0.092mm negative final clearance at4mm local offset.
    # Add3mm local (about2.6mm world at this rig scale) for turned thickness
    # and varying cloth normals; keep the unchanged1..12mm final world guard.
    mod.wrap_method='NEAREST_SURFACEPOINT';mod.wrap_mode='ABOVE_SURFACE';mod.offset=.007
    # Keep turned thickness outside this support constraint.
    index=list(band.modifiers).index(mod)
    solid=next((i for i,m in enumerate(band.modifiers) if m.type=='SOLIDIFY'),None)
    if solid is not None:band.modifiers.move(index,solid)
    return dict(target=support.name,torso_faces=len(ids),excluded_faces=len(faces)-len(ids),offset=.007,
                scope='Exact full pre-thickness outer coat, with all-frame actual solid-coat separation/volume and torso ownership checks. No filtered subdivision proxy or cloth simulation.')


def outside(bvh,point,direction):
    """Ray parity against a proven closed shell, fail on unbounded ambiguity."""
    origin=point.copy();count=0
    for _ in range(64):
        hit,_,_,_=bvh.ray_cast(origin,direction,100.)
        if hit is None:return count%2==0
        count+=1;origin=hit+direction*.00001
    # Not outside: the independent solid-angle test must resolve this case.
    return None


def winding_number(triangles,point):
    """Independent solid-angle inside check for exceptional ray/edge cases."""
    import numpy as np
    q=np.asarray(triangles,dtype=float)-np.asarray(point,dtype=float)
    a,b,c=q[:,0],q[:,1],q[:,2]
    la=np.linalg.norm(a,axis=1);lb=np.linalg.norm(b,axis=1);lc=np.linalg.norm(c,axis=1)
    numerator=np.einsum('ij,ij->i',a,np.cross(b,c))
    denominator=la*lb*lc+np.einsum('ij,ij->i',a,b)*lc+np.einsum('ij,ij->i',b,c)*la+np.einsum('ij,ij->i',c,a)*lb
    return float(np.arctan2(numerator,denominator).sum()/(2*np.pi))


def fit_skirt_seams(bpy,rig):
    """Dressed construction: skirt waist underlaps coat/band, lower flare stays."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.kdtree import KDTree
    spec=importlib.util.spec_from_file_location('cloth352',Path(__file__).with_name('nihang_cloth352.py'))
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    previous=rig.data.pose_position;rig.data.pose_position='REST';bpy.context.view_layer.update()
    coat=bpy.data.objects['MF coherent coat'];deps=bpy.context.evaluated_depsgraph_get();ev=coat.evaluated_get(deps);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
    mask=mesh.attributes['MF361 torso ownership'];matrix=rig.matrix_world.inverted()@ev.matrix_world
    faces=[list(p.vertices) for p in mesh.polygons if all(mask.data[i].value>.9 for i in p.vertices)]
    tree=BVHTree.FromPolygons([matrix@v.co for v in mesh.vertices],faces);ev.to_mesh_clear()
    raw_matrix=rig.matrix_world.inverted()@coat.matrix_world;kd=KDTree(len(coat.data.vertices))
    source_rows=[]
    for v in coat.data.vertices:
        kd.insert(raw_matrix@v.co,v.index)
        source_rows.append([(coat.vertex_groups[g.group].name,g.weight) for g in v.groups])
    kd.balance();records=[]
    for ob in rig.children_recursive:
        if ob.type!='MESH' or not ob.name.startswith('MF coherent split chola'):continue
        ob.data=ob.data.copy();original=[v.co.copy() for v in ob.data.vertices]
        weights=[{ob.vertex_groups[g.group].name:g.weight for g in v.groups} for v in ob.data.vertices]
        mx=rig.matrix_world.inverted()@ob.matrix_world;inv=mx.inverted();new=[];moved=0;maximum=0.
        for v,old in zip(ob.data.vertices,weights):
            p=mx@v.co;t=max(0.,min(1.,(p.z-1.00)/.10));t=t*t*(3-2*t)
            row=dict(old)
            if t:
                origin=Vector((0,-.02,p.z));axis=(p-origin).normalized()
                hit,n,_,_=tree.ray_cast(origin+axis*.6,-axis,1.2)
                if hit is None:raise ValueError('LOOK361_SKIRT_TORSO_SUPPORT')
                target=hit-axis*.0015
                v.co=inv@(p.lerp(target,t));maximum=max(maximum,(v.co-original[v.index]).length);moved+=1
                near=kd.find_n(hit,4);owned=helper.blend_weights([source_rows[i] for _,i,_ in near],[d for _,_,d in near])
                row={name:old.get(name,0)*(1-t)+owned.get(name,0)*t for name in set(old)|set(owned)}
            total=sum(row.values());new.append({name:w/total for name,w in row.items() if w>1e-8})
        if maximum>.12:raise ValueError('LOOK361_SKIRT_UNEXPECTED_RESHAPE')
        ob.vertex_groups.clear()
        for index,row in enumerate(new):
            for name,w in row.items():
                group=ob.vertex_groups.get(name) or ob.vertex_groups.new(name=name);group.add([index],w,'REPLACE')
        ob.data.update();records.append(dict(object=ob.name,moved_vertices=moved,maximum_displacement=maximum,lower_flare_preserved=True))
    if len(records)!=2:raise ValueError('LOOK361_SKIRT_PAIR')
    rig.data.pose_position=previous;bpy.context.view_layer.update();return records


def verify_waist(bpy,out):
    from mathutils.bvhtree import BVHTree
    from mathutils import Vector
    from collections import Counter
    scene=bpy.context.scene;frame=scene.frame_current
    coat=bpy.data.objects['MF coherent coat'];band=bpy.data.objects['MF coherent waist wrap'];records=[]
    direction=Vector((.371,.543,.754)).normalized()
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        a=coat.evaluated_get(deps);mesh=a.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
        mask=mesh.attributes.get('MF361 torso ownership')
        if mask is None:raise ValueError('LOOK361_LOST_TORSO_OWNERSHIP')
        if f==252:
            counts=Counter(tuple(sorted((a,b))) for p in mesh.polygons for a,b in zip(p.vertices,(*p.vertices[1:],p.vertices[0])))
            if any(value!=2 for value in counts.values()):raise ValueError('LOOK361_COAT_SHELL_NOT_CLOSED')
        tree=BVHTree.FromPolygons([a.matrix_world@v.co for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons])
        b=band.evaluated_get(deps);bm=b.to_mesh();distances=[];ownership=[];details=[];inside_count=0;exceptions=[]
        for v in bm.vertices:
            world=b.matrix_world@v.co;hit,n,index,_=tree.find_nearest(world)
            signed=(world-hit).dot(n);distances.append((world-hit).length)
            ray_outside=outside(tree,world,direction)
            if not ray_outside or signed<0:exceptions.append((v.index,world.copy(),ray_outside))
            ownership.append(min(mask.data[i].value for i in mesh.polygons[index].vertices))
            details.append(dict(vertex=v.index,world=list(world),hit=list(hit),normal=list(n),face=index,signed=signed,distance=distances[-1]))
        corroboration=[]
        if exceptions:
            import numpy as np
            mesh.calc_loop_triangles();verts=np.array([a.matrix_world@v.co for v in mesh.vertices]);triangles=verts[np.array([t.vertices[:] for t in mesh.loop_triangles])]
            for index,point,ray_outside in exceptions:
                value=winding_number(triangles,list(point));absolute=abs(value)
                if .05<absolute<.95:raise ValueError('LOOK361_VOLUME_WINDING_AMBIGUOUS:'+str((f,index,value)))
                if absolute>=.95:inside_count+=1
                corroboration.append(dict(vertex=index,ray_outside=ray_outside,winding=value))
        a.to_mesh_clear();b.to_mesh_clear()
        record=dict(frame=f,minimum=min(distances),maximum=max(distances),minimum_torso_ownership=min(ownership),inside_vertices=inside_count,volume_crosschecks=corroboration);records.append(record)
        if record['minimum']<.001 or record['maximum']>.012 or inside_count:
            # Preserve exact contact evidence before fail-closed rejection.
            solids=[m for m in band.modifiers if m.type=='SOLIDIFY']
            states=[(m,m.show_viewport,m.show_render) for m in solids]
            for m,_,_ in states:m.show_viewport=False;m.show_render=False
            bpy.context.view_layer.update();pre=band.evaluated_get(bpy.context.evaluated_depsgraph_get());pm=pre.to_mesh()
            before=[]
            for v in pm.vertices:
                world=pre.matrix_world@v.co;hit,n,index,_=tree.find_nearest(world)
                before.append(dict(vertex=v.index,world=list(world),hit=list(hit),normal=list(n),face=index,signed=(world-hit).dot(n)))
            pre.to_mesh_clear()
            for m,a,b in states:m.show_viewport=a;m.show_render=b
            bpy.context.view_layer.update()
            (out/'waist361-failure.json').write_text(json.dumps(dict(record=record,post=sorted(details,key=lambda x:x['signed'])[:20],pre=sorted(before,key=lambda x:x['signed'])[:20],pre_minimum=min(x['signed'] for x in before),pre_maximum=max(x['signed'] for x in before),modifiers=[dict(name=m.name,type=m.type) for m in band.modifiers]),indent=2)+'\n')
            raise ValueError('LOOK361_WAIST_CLEARANCE:'+str(record))
        if record['minimum_torso_ownership']<.9:raise ValueError('LOOK361_WRONG_CONTACT_OWNER:'+str(record))
    scene.frame_set(frame);bpy.context.view_layer.update()
    return records


def run(bpy,out):
    spec=importlib.util.spec_from_file_location('tack354',Path(__file__).with_name('nihang_tack354.py'))
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    signature=helper.action_signature(bpy)
    rig=bpy.data.objects['MF coherent Nihang rig'];body=bpy.data.objects['MF coherent Nihang body']
    if not rig.get('surface357') or rig.get('look361'):raise ValueError('LOOK361_PARENT')
    waist=waist_support(bpy,rig)
    skirt_seams=fit_skirt_seams(bpy,rig)
    image=bpy.data.images.load(str(Path(__file__).resolve().parents[4]/SOURCE),check_existing=True);image.pack()
    objects=[body]+[ob for ob in rig.children_recursive if ob.type=='MESH' and ob.name.startswith(('MF Nihang gathered crown','MF Nihang overlapped cloth','MF Nihang wrapped crown core','MF coherent coat','MF coherent split chola'))]
    changed=[]
    for ob in objects:
        if ob.type!='MESH':raise ValueError('LOOK361_MESH_OWNER')
        ob.data=ob.data.copy()
        attribute=ob.data.attributes.get(ATTRIBUTE) or ob.data.attributes.new(ATTRIBUTE,'FLOAT_VECTOR','POINT')
        for datum,vertex in zip(attribute.data,ob.data.vertices):datum.vector=vertex.co
        for index,old in enumerate(list(ob.data.materials)):
            if ob==body and index!=0:continue
            if old is None or not old.use_nodes:continue
            material=old.copy();ob.data.materials[index]=material;material.name='361 attached painterly grain '+ob.name
            n=material.node_tree.nodes;l=material.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
            previous=bs.inputs['Base Color'].links[0].from_socket if bs.inputs['Base Color'].is_linked else None
            base=tuple(bs.inputs['Base Color'].default_value)
            rest=n.new('ShaderNodeAttribute');rest.attribute_name=ATTRIBUTE
            scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=12
            l.new(rest.outputs['Vector'],scale.inputs[0])
            frac=n.new('ShaderNodeVectorMath');frac.operation='FRACTION';l.new(scale.outputs[0],frac.inputs[0])
            crop=n.new('ShaderNodeVectorMath');crop.operation='MULTIPLY';crop.inputs[1].default_value=(.23,.23,.23);l.new(frac.outputs[0],crop.inputs[0])
            offset=n.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.01,.01,.01);l.new(crop.outputs[0],offset.inputs[0])
            tex=n.new('ShaderNodeTexImage');tex.image=image;tex.projection='BOX';tex.projection_blend=.25;tex.extension='EXTEND';l.new(offset.outputs[0],tex.inputs[0])
            bw=n.new('ShaderNodeRGBToBW');l.new(tex.outputs['Color'],bw.inputs[0])
            contrast=n.new('ShaderNodeMapRange');contrast.clamp=True
            contrast.inputs['From Min'].default_value=.16;contrast.inputs['From Max'].default_value=.34
            contrast.inputs['To Min'].default_value=.70 if ob==body else .86
            contrast.inputs['To Max'].default_value=1.16 if ob==body else 1.10
            l.new(bw.outputs[0],contrast.inputs[0])
            mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=base
            if previous:l.new(previous,mix.inputs[1])
            l.new(contrast.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
            bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.00025 if ob==body else .00018
            if bs.inputs['Normal'].is_linked:l.new(bs.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
            l.new(bw.outputs[0],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
        changed.append(dict(name=ob.name,vertices=len(ob.data.vertices),material_slots=[m.name if m else None for m in ob.data.materials]))
    waist['frames']=verify_waist(bpy,out)
    rig['look361']=1;bpy.context.view_layer.update()
    if helper.action_signature(bpy)!=signature:raise ValueError('LOOK361_ACTION_DRIFT')
    report=dict(changed=True,source_preserved=True,actions_unchanged=True,action_signature=signature,objects=changed,waist=waist,skirt_seams=skirt_seams,
                featureless_crop=[.01,.01,.24,.24],source=SOURCE,rest_attribute=ATTRIBUTE,
                scope='Featureless authored pigment structure and torso-only waist support; stable attached coordinates, identity/anatomy/palette/actions retained. Actual posed support, grain/tiling/lighting review remains necessary.')
    (out/'look361.json').write_text(json.dumps(report,indent=2)+'\n');return report


def inspect_layers(bpy,out):
    """Read-only actual occluder diagnosis at the failed waistband interface."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from collections import Counter
    spec=importlib.util.spec_from_file_location('control361',Path(__file__).with_name('nihang_control.py'))
    control=importlib.util.module_from_spec(spec);spec.loader.exec_module(control)
    rig=bpy.data.objects['MF coherent Nihang rig'];band=bpy.data.objects['MF coherent waist wrap'];scene=bpy.context.scene;frame=scene.frame_current
    chosen=[ob for ob in rig.children_recursive if not ob.hide_render and ob.type=='MESH' and ob.name.startswith(('MF coherent','MF347 chola'))]
    if band not in chosen:raise ValueError('LOOK361_LAYER_OWNER')
    rows=[]
    for f in (283,327,350):
        scene.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();trees={};bounds={}
        for ob in chosen:
            ev=ob.evaluated_get(deps);mesh=ev.to_mesh();vs=[ev.matrix_world@v.co for v in mesh.vertices]
            trees[ob.name]=BVHTree.FromPolygons(vs,[list(p.vertices) for p in mesh.polygons])
            bounds[ob.name]=dict(local_z=[min(v.co.z for v in ob.data.vertices),max(v.co.z for v in ob.data.vertices)],world_z=[min(v.z for v in vs),max(v.z for v in vs)])
            ev.to_mesh_clear()
        ev=band.evaluated_get(deps);mesh=ev.to_mesh();matrix=ev.matrix_world.copy();normal_matrix=matrix.to_3x3().inverted().transposed()
        points=[(v.index,matrix@v.co,(normal_matrix@v.normal).normalized()) for v in mesh.vertices];ev.to_mesh_clear()
        camera=control.diagnostic_camera(bpy,'leader_reverse');bpy.context.view_layer.update();eye=camera.matrix_world.translation.copy();data=camera.data;bpy.data.objects.remove(camera,do_unlink=True);bpy.data.cameras.remove(data)
        count=Counter();samples=[]
        for index,p,normal in points:
            if index%3 or normal.dot(eye-p)<=0:continue
            ray=(p-eye).normalized();limit=(p-eye).length+.002;hits=[]
            for name,tree in trees.items():
                hit,_,_,distance=tree.ray_cast(eye,ray,limit)
                if hit is not None:hits.append((distance,name,hit))
            if not hits:continue
            distance,name,hit=min(hits,key=lambda x:x[0]);count[name]+=1
            if name!=band.name and len(samples)<40:samples.append(dict(vertex=index,band_world=list(p),first_object=name,hit=list(hit),occlusion_depth=(p-eye).length-distance))
        rows.append(dict(frame=f,first_visible_hits=dict(count),occlusion_samples=samples,bounds=bounds))
    materials=[]
    for material in band.data.materials:
        nodes=[]
        for node in material.node_tree.nodes:
            item=dict(name=node.name,type=node.type)
            if hasattr(node,'color_ramp'):item['ramp']=[dict(position=e.position,color=list(e.color)) for e in node.color_ramp.elements]
            if node.type=='BSDF_PRINCIPLED':item['alpha']=node.inputs['Alpha'].default_value
            nodes.append(item)
        materials.append(dict(name=material.name,nodes=nodes,links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in material.node_tree.links]))
    scene.frame_set(frame);bpy.context.view_layer.update()
    report=dict(changed=False,source_preserved=True,poses=rows,band_materials=materials,scope='Actual dressed-layer visibility diagnosis; no garment or appearance approval.')
    (out/'layers361.json').write_text(json.dumps(report,indent=2)+'\n');return report
