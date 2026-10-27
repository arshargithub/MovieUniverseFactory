"""Fixed donor surface adaptation and revealing evidence views; no recipe code."""
import hashlib
import json

VIEWS = {'warhorse_head_front384', 'warhorse_head_side384',
         'warhorse_head_oblique384', 'warhorse_chest384'}


def validate(edit):
    if (not isinstance(edit, dict) or set(edit) != {'kind', 'target'} or
            edit['kind'] not in {'warhorse_surface384','warhorse_headblend384','warhorse_headrebuild384','warhorse_headgraft384'} or edit['target'] != 'warhorse383'):
        raise ValueError('WARHORSE384_FIELDS')


def fingerprint(mesh):
    return hashlib.sha256(json.dumps({
        'coordinates': [list(v.co) for v in mesh.data.vertices],
        'weights': [[(g.group, g.weight) for g in v.groups] for v in mesh.data.vertices],
        'faces': [list(p.vertices) for p in mesh.data.polygons],
    }, sort_keys=True).encode()).hexdigest()


def run(bpy, out, edit):
    validate(edit)
    if edit['kind'] == 'warhorse_headblend384': headblend(bpy, out)
    if edit['kind'] == 'warhorse_headrebuild384': headrebuild(bpy, out)
    if edit['kind'] == 'warhorse_headgraft384': graft(bpy,out)
    result=surface(bpy, out)
    if edit['kind'] == 'warhorse_headrebuild384': skin_material(bpy)
    return result


def graft(bpy,out):
    import importlib.util
    from pathlib import Path
    spec=importlib.util.spec_from_file_location('mf_headgraft384',Path(__file__).with_name('warhorse_graft384.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.run(bpy,out)


def headrebuild(bpy, out):
    """Remove classified head armor, close its actual cut boundaries as skin."""
    import bmesh
    from array import array
    mesh=bpy.data.objects['MF383 Warhorse surface'];me=mesh.data
    bsdf=next(n for n in me.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    socket=bsdf.inputs['Metallic'].links[0].from_socket
    for _ in range(8):
        node=socket.node
        if node.type=='TEX_IMAGE':break
        linked=[i.links[0].from_socket for i in node.inputs if i.is_linked]
        if len(linked)!=1:raise ValueError('WARHORSE384_REBUILD_METAL')
        socket=linked[0]
    else:raise ValueError('WARHORSE384_REBUILD_CHAIN')
    image=node.image;pixels=array('f',[0.])*len(image.pixels);image.pixels.foreach_get(pixels);width,height=image.size
    def metal(uv):
        x=min(width-1,max(0,int(uv.x*(width-1))));y=min(height-1,max(0,int(uv.y*(height-1))))
        return pixels[(y*width+x)*4+2]
    names={g.index:g.name for g in mesh.vertex_groups};head_index=mesh.vertex_groups['head'].index
    headids={v.index for v in me.vertices if sum(g.weight for g in v.groups if names[g.group] in {'head','jaw'})>.5}
    original={v.index+1:(tuple(v.co),sorted((g.group,g.weight) for g in v.groups)) for v in me.vertices if v.index not in headids}
    original_normals={(p.index+1,me.loops[l].vertex_index+1):tuple(me.corner_normals[l].vector) for p in me.polygons for l in p.loop_indices}
    bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
    uid=bm.verts.layers.int.new('MF384_original_vertex');fid=bm.faces.layers.int.new('MF384_original_face')
    headlayer=bm.verts.layers.int.new('MF384_head_domain')
    for v in bm.verts:v[uid]=v.index+1;v[headlayer]=int(v.index in headids)
    for f in bm.faces:f[fid]=f.index+1
    # Weld only coincident head duplicates so cut boundaries are real loops.
    bmesh.ops.remove_doubles(bm,verts=[v for v in bm.verts if v[headlayer]],dist=.00001)
    uv=bm.loops.layers.uv.active
    remove=[]
    for f in bm.faces:
        center=f.calc_center_median()
        if not all(v[headlayer] for v in f.verts) or not (1.51<center.z<2.075 and center.y<-.90):continue
        samples=[loop[uv].uv for loop in f.loops];mean=sum(samples,samples[0].copy()*0)/len(samples)
        if max([metal(p) for p in samples]+[metal(mean)])>.20:remove.append(f)
    if not 50<len(remove)<650:raise ValueError('WARHORSE384_REBUILD_DOMAIN:'+str(len(remove)))
    count=len(remove);prior_boundary={e for e in bm.edges if e.is_boundary}
    bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY')
    cuts={e for e in bm.edges if e.is_boundary and e not in prior_boundary}
    # Include connected original open seams only within the classified head.
    boundary={e for e in bm.edges if e.is_boundary and all(v[headlayer] and v.co.z>1.48 for v in e.verts)}
    selected=set(cuts);todo=list(cuts)
    while todo:
        e=todo.pop()
        for v in e.verts:
            for other in v.link_edges:
                if other in boundary and other not in selected:selected.add(other);todo.append(other)
    filled=bmesh.ops.holes_fill(bm,edges=list(selected),sides=0).get('faces',[])
    if not filled:raise ValueError('WARHORSE384_REBUILD_NO_PATCH')
    for f in filled:f[fid]=0
    # Refinement belongs only to new skin patches and their head boundaries.
    edges=list({e for f in filled for e in f.edges})
    bmesh.ops.triangulate(bm,faces=filled)
    new_faces=[f for f in bm.faces if f[fid]==0]
    if new_faces:
        bmesh.ops.subdivide_edges(bm,edges=list({e for f in new_faces for e in f.edges}),cuts=2,use_grid_fill=True)
    deform=bm.verts.layers.deform.verify();newverts=[v for v in bm.verts if v[uid]==0]
    for v in newverts:
        v[headlayer]=1;v[deform].clear();v[deform][head_index]=1.
    # Coherent bridge profile is constrained by measured source exposed skin.
    profile=[(1.50,-1.26),(1.60,-1.25),(1.70,-1.21),(1.80,-1.155),(1.90,-1.110),(2.,-1.030),(2.08,-.965)]
    for v in newverts:
        x,y,z=v.co
        if abs(x)<.16 and y<-.96 and 1.50<z<2.08:
            for (a,pa),(b,pb) in zip(profile,profile[1:]):
                if a<=z<=b:
                    target=pa+(pb-pa)*(z-a)/(b-a)+.055*(x/.16)**2
                    v.co.y=y+(target-y)*(.8*(1-(abs(x)/.16)**4));break
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bm.to_mesh(me);bm.free();me.update()
    uids=me.attributes['MF384_original_vertex'];domain=me.attributes['MF384_head_domain'];faceids=me.attributes['MF384_original_face']
    after={uids.data[v.index].value:(tuple(v.co),sorted((g.group,g.weight) for g in v.groups)) for v in me.vertices if not domain.data[v.index].value}
    if original!=after:raise ValueError('WARHORSE384_REBUILD_PROTECTED_SURFACE')
    normals=[]
    for p in me.polygons:
        p.use_smooth=True
        for l in p.loop_indices:
            vid=me.loops[l].vertex_index;key=(faceids.data[p.index].value,uids.data[vid].value)
            normals.append(original_normals[key] if not domain.data[vid].value and key in original_normals else tuple(me.vertices[vid].normal))
    me.normals_split_custom_set(normals)
    report=dict(deleted_armor_faces=count,filled_loops=len(filled),new_skin_vertices=len(newverts),vertices=len(me.vertices),faces=len(me.polygons),
        protected_non_head_vertices=len(after),protected_coordinates_weights_equal=True,
        method='Remove classified head armor faces, close actual cut loops, refine and bind new head skin; original non-head vertices/weights exact.',
        caveat='New skin continuity, eye visibility and shape require actual close review.')
    (out/'warhorse384-headrebuild.json').write_text(json.dumps(report,indent=2)+'\n')


def skin_material(bpy):
    mesh=bpy.data.objects['MF383 Warhorse surface'];material=mesh.data.materials[0].copy();material.name='MF384 reconstructed horse head skin'
    nodes=material.node_tree.nodes;links=material.node_tree.links;bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    links.new(nodes['MF384 same donor coat detail'].outputs['Color'],bsdf.inputs['Base Color'])
    for key,value in [('Metallic',0.),('Roughness',.68)]:
        for l in list(bsdf.inputs[key].links):links.remove(l)
        bsdf.inputs[key].default_value=value
    bump=nodes['MF384 subtle short coat relief'];links.new(nodes['MF384 actual surface normal'].outputs['Normal'],bump.inputs['Normal']);links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    mesh.data.materials.append(material)
    for p in mesh.data.polygons:
        if mesh.data.attributes['MF384_original_face'].data[p.index].value==0:p.material_index=1


def relax(points, adjacency, influence, iterations=24, limit=.045):
    """Bounded local edge relaxation; no global shrink or topology replacement."""
    import math
    result = [list(p) for p in points]
    for _ in range(iterations):
        nxt = [p[:] for p in result]
        for i, amount in enumerate(influence):
            if not amount or not adjacency[i]: continue
            mean = [sum(result[j][k] for j in adjacency[i])/len(adjacency[i]) for k in range(3)]
            value = [result[i][k]+.40*amount*(mean[k]-result[i][k]) for k in range(3)]
            delta = [value[k]-points[i][k] for k in range(3)];length=math.sqrt(sum(v*v for v in delta))
            nxt[i] = [points[i][k]+delta[k]*min(1.,limit/max(length,1e-15)) for k in range(3)]
        result = nxt
    return result


def headblend(bpy, out):
    from array import array
    from mathutils import Vector
    mesh=bpy.data.objects['MF383 Warhorse surface'];me=mesh.data
    if mesh.data.materials[0].name.startswith('MF384'): raise ValueError('WARHORSE384_NEEDS_ORIGINAL')
    bsdf=next(n for n in me.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    socket=bsdf.inputs['Metallic'].links[0].from_socket
    for _ in range(8):
        n=socket.node
        if n.type=='TEX_IMAGE': break
        upstream=[i.links[0].from_socket for i in n.inputs if i.is_linked]
        if len(upstream)!=1: raise ValueError('WARHORSE384_METAL_IMAGE')
        socket=upstream[0]
    else: raise ValueError('WARHORSE384_METAL_CHAIN')
    image=n.image;pixels=array('f',[0.])*len(image.pixels);image.pixels.foreach_get(pixels);width,height=image.size
    names={g.index:g.name for g in mesh.vertex_groups};head=[];ear=[];metal=[0.]*len(me.vertices)
    for v in me.vertices:
        head.append(sum(g.weight for g in v.groups if names[g.group] in {'head','jaw'}))
        ear.append(sum(g.weight for g in v.groups if names[g.group] in {'ear_L','ear_R'}))
    for loop,uv in zip(me.loops,me.uv_layers.active.data):
        x=min(width-1,max(0,int(uv.uv.x*(width-1))));y=min(height-1,max(0,int(uv.uv.y*(height-1))))
        metal[loop.vertex_index]=max(metal[loop.vertex_index],pixels[(y*width+x)*4+2])
    groups={};index=[];points=[]
    for v in me.vertices:
        key=tuple(round(float(x),5) for x in v.co)
        if key not in groups: groups[key]=len(points);points.append(list(v.co))
        index.append(groups[key])
    adjacency=[set() for _ in points];influence=[0.]*len(points)
    for edge in me.edges:
        a,b=[index[i] for i in edge.vertices]
        if a!=b:adjacency[a].add(b);adjacency[b].add(a)
    for v in me.vertices:
        if head[v.index]>.5 and ear[v.index]<.1 and metal[v.index]>.10 and 1.50<v.co.z<2.065:
            influence[index[v.index]]=1.
    seeds=sum(v>0 for v in influence)
    if not 50<seeds<600: raise ValueError('WARHORSE384_PLATE_DOMAIN:'+str(seeds))
    # One soft ring shares the border correction with adjacent skin; no eye/ear interior solve.
    for i,amount in enumerate(influence[:]):
        if amount==1:
            for j in adjacency[i]:
                if influence[j]==0:influence[j]=.35
    new=relax(points,adjacency,influence);changed=[]
    normals=[tuple(n.vector) for n in me.corner_normals]
    for v in me.vertices:
        j=index[v.index]
        if influence[j]:
            v.co=new[j];changed.append(v.index)
    me.update()
    # Recompute only affected split normals; preserve all other custom normals.
    sums=[Vector((0,0,0)) for _ in points]
    for face in me.polygons:
        ids=list(face.vertices);a,b,c=[me.vertices[i].co for i in ids[:3]];normal=(b-a).cross(c-a)
        for i in ids:sums[index[i]]+=normal
    for loop in me.loops:
        j=index[loop.vertex_index]
        if influence[j] and sums[j].length>1e-10:normals[loop.index]=sums[j].normalized()
    me.normals_split_custom_set(normals)
    move=max((Vector(a)-Vector(b)).length for a,b in zip(points,new))
    report=dict(seed_vertices=seeds,changed_vertices=len(changed),max_displacement=move,limit=.045,
        method='Weld-aware local plate-border relaxation, one soft boundary ring; only head coordinates/custom normals changed.',
        unresolved='Actual close anatomy/eye/bridle and motion proof required; no intact hidden-head claim.')
    (out/'warhorse384-headblend.json').write_text(json.dumps(report,indent=2)+'\n')


def surface(bpy, out):
    mesh = bpy.data.objects['MF383 Warhorse surface']
    if bpy.context.scene.name != 'MF383 Warhorse studio' or (len(mesh.data.materials) != 1 and not mesh.get('mf384_merged')):
        raise ValueError('WARHORSE384_OWNERS')
    if mesh.data.materials[0].name.startswith('MF384'):
        raise ValueError('WARHORSE384_ALREADY_ADAPTED')
    before = fingerprint(mesh)
    material = mesh.data.materials[0].copy()
    material.name = 'MF384 bare bay head and leather breastcollar'
    mesh.data.materials[0] = material
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    original = {}
    for key in ['Base Color', 'Metallic', 'Roughness', 'Normal']:
        if len(bsdf.inputs[key].links) != 1:
            raise ValueError('WARHORSE384_SOURCE_SOCKET:' + key)
        original[key] = bsdf.inputs[key].links[0].from_socket
    groups = {g.index: g.name for g in mesh.vertex_groups}
    head_values = []
    chest_values = []
    for v in mesh.data.vertices:
        head_values.append(min(1., sum(g.weight for g in v.groups
            if groups[g.group] in {'head', 'jaw', 'ear_L', 'ear_R'}) * 4.))
        x, y, z = v.co
        chest_values.append(float(abs(x) < .50 and y < -.20 and .90 < z < 1.90))
    for name, values in [('MF384_head', head_values), ('MF384_chest', chest_values)]:
        if mesh.data.attributes.get(name):
            raise ValueError('WARHORSE384_ATTRIBUTE_EXISTS')
        attr = mesh.data.attributes.new(name, 'FLOAT', 'POINT')
        attr.data.foreach_set('value', values)
    rest=mesh.data.attributes.get('MF384_rest')
    if rest is None:
        rest=mesh.data.attributes.new('MF384_rest','FLOAT_VECTOR','POINT')
        rest.data.foreach_set('vector',[float(x) for v in mesh.data.vertices for x in v.co])

    def node(kind, name):
        n = nodes.new(kind); n.label = name; n.name = 'MF384 ' + name
        return n

    def math(operation, a, b=None, name='math'):
        n = node('ShaderNodeMath', name); n.operation = operation
        for i, value in enumerate([a, b] if b is not None else [a]):
            if hasattr(value, 'node'): links.new(value, n.inputs[i])
            else: n.inputs[i].default_value = value
        return n.outputs[0]

    def mix(factor, a, b, name):
        n = node('ShaderNodeMixRGB', name)
        for i, value in enumerate([factor, a, b]):
            if hasattr(value, 'node'): links.new(value, n.inputs[i])
            else: n.inputs[i].default_value = value
        return n.outputs[0]

    masks = {}
    # Metal texture classifies the armor pixels, not all light-colored hair or eyes.
    threshold = node('ShaderNodeMapRange', 'metal-only transition')
    links.new(original['Metallic'], threshold.inputs['Value'])
    threshold.inputs['From Min'].default_value = .12
    threshold.inputs['From Max'].default_value = .55
    threshold.clamp = True
    for part in ['head', 'chest']:
        a = node('ShaderNodeAttribute', part + ' surface domain')
        a.attribute_name = 'MF384_' + part
        masks[part] = math('MULTIPLY', a.outputs['Fac'], threshold.outputs['Result'], part + ' armor mask')
    total = math('MAXIMUM', masks['head'], masks['chest'], 'combined adaptation')
    tex = node('ShaderNodeTexCoord', 'surface-bound detail')
    noise = node('ShaderNodeTexNoise', 'coat variation')
    noise.inputs['Scale'].default_value = 180.
    noise.inputs['Detail'].default_value = 2.
    noise.inputs['Roughness'].default_value = .7
    links.new(tex.outputs['UV'], noise.inputs['Vector'])
    source_image = original['Base Color'].node.image
    rest_node=node('ShaderNodeAttribute','rest coat projection');rest_node.attribute_name='MF384_rest'
    separate=node('ShaderNodeSeparateXYZ','head coat coordinates');links.new(rest_node.outputs['Vector'],separate.inputs[0])
    patch_offset=node('ShaderNodeCombineXYZ','existing coat patch')
    for axis,scale,offset in [('X',.20,.40),('Z',.12,.25)]:
        val=math('ADD',math('MULTIPLY',separate.outputs[axis],scale,axis+' coat scale'),offset,axis+' coat offset')
        links.new(val,patch_offset.inputs['X' if axis=='X' else 'Y'])
    coat_sample=node('ShaderNodeTexImage','same donor coat detail');coat_sample.image=source_image
    links.new(patch_offset.outputs[0],coat_sample.inputs['Vector'])
    coat = coat_sample.outputs['Color']
    leather = mix(noise.outputs['Fac'], (.020, .012, .009, 1), (.043, .024, .016, 1), 'worn dark leather')
    color = mix(masks['head'], original['Base Color'], coat, 'replace head metal')
    color = mix(masks['chest'], color, leather, 'replace chest metal')
    links.new(color, bsdf.inputs['Base Color'])
    keep = math('SUBTRACT', 1., total, 'keep original outside adaptation')
    links.new(math('MULTIPLY', original['Metallic'], keep, 'remove adapted metal'), bsdf.inputs['Metallic'])
    rough = mix(total, original['Roughness'], (.73, .73, .73, 1), 'coat leather roughness')
    links.new(rough, bsdf.inputs['Roughness'])
    geometry = node('ShaderNodeNewGeometry', 'actual surface normal')
    clean_normal = mix(masks['head'], original['Normal'], geometry.outputs['Normal'], 'remove baked plate relief')
    bump = node('ShaderNodeBump', 'subtle short coat relief')
    bump.inputs['Strength'].default_value = .12
    bump.inputs['Distance'].default_value = .00025
    links.new(coat, bump.inputs['Height'])
    links.new(clean_normal, bump.inputs['Normal'])
    # Keep unadapted normal response exactly; bump applies only to new coat/leather.
    links.new(mix(total, original['Normal'], bump.outputs['Normal'], 'adapted normal only'), bsdf.inputs['Normal'])
    if fingerprint(mesh) != before:
        raise ValueError('WARHORSE384_GEOMETRY_MUTATED')
    report = dict(geometry_fingerprint=before, material=material.name,
        head_vertices=sum(v > 0 for v in head_values), chest_vertices=sum(chest_values),
        method='Material-only reinterpretation of continuous outer surface; no hidden anatomy claim.',
        scope='Geometry, topology, weights and animation unchanged. Actual close review required.')
    (out / 'warhorse384.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def inventory(bpy):
    mesh = bpy.data.objects['MF383 Warhorse surface']
    attrs = {}
    for a in mesh.data.attributes:
        if a.name.startswith('MF384_') and a.data_type=='FLOAT':
            attrs[a.name] = hashlib.sha256(json.dumps([v.value for v in a.data]).encode()).hexdigest()
    material = mesh.data.materials[0]
    graph = [(n.name, n.bl_idname) for n in material.node_tree.nodes]
    edges = [(l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier)
             for l in material.node_tree.links]
    graft=bpy.data.objects.get('MF384 reused horse head');extra=None
    if graft:
        ev=graft.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
        try:posed=[list(v.co) for v in me.vertices]
        finally:ev.to_mesh_clear()
        extra=dict(fingerprint=fingerprint(graft),posed_sha256=hashlib.sha256(json.dumps(posed).encode()).hexdigest(),materials=[m.name for m in graft.data.materials])
    return dict(geometry_fingerprint=fingerprint(mesh), attributes=attrs,graft=extra,
                graph_sha256=hashlib.sha256(json.dumps([sorted(graph), sorted(edges)]).encode()).hexdigest())


def camera(bpy, view):
    from mathutils import Vector
    if view not in VIEWS: raise ValueError('WARHORSE384_VIEW')
    scene = bpy.context.scene; frame = scene.frame_current
    rig = bpy.data.objects['MF383 Warhorse rig']; mesh = bpy.data.objects.get('MF384 reused horse head') or bpy.data.objects['MF383 Warhorse surface']
    groups = {g.index: g.name for g in mesh.vertex_groups}
    ids = [v.index for v in mesh.data.vertices if v.co.z > 1.45 and
           sum(g.weight for g in v.groups if groups[g.group] in {'head', 'jaw'}) > .5]
    if len(ids) < 50: raise ValueError('WARHORSE384_HEAD_DOMAIN')
    ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh()
    try: points = [ev.matrix_world @ me.vertices[i].co for i in ids]
    finally: ev.to_mesh_clear()
    lo = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    hi = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    target = (lo + hi) / 2
    scene.frame_set(283); bpy.context.view_layer.update()
    forward = rig.matrix_world @ rig.pose.bones['head'].head - rig.matrix_world @ rig.pose.bones['pelvis'].head
    forward.z = 0; forward.normalize(); side = Vector((-forward.y, forward.x, 0))
    scene.frame_set(frame); bpy.context.view_layer.update()
    if view == 'warhorse_chest384':
        target = rig.matrix_world @ rig.pose.bones['spine_03'].head
        target.z -= .18
    data = bpy.data.cameras.new('MF384 revealing evidence camera'); data.type = 'ORTHO'
    data.ortho_scale = 1.70 if view == 'warhorse_chest384' else max(1.05, (hi-lo).length * 1.1)
    ob = bpy.data.objects.new(data.name, data); scene.collection.objects.link(ob)
    offset = (side * 4 if view == 'warhorse_head_side384' else
              forward * 3 - side * 3 if view == 'warhorse_head_oblique384' else forward * 4)
    ob.location = target + offset + Vector((0, 0, .08))
    ob.rotation_euler = (target - ob.location).to_track_quat('-Z', 'Y').to_euler()
    return ob
