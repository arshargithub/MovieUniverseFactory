"""Actual boundary stitching. No new task, pose curves or input-code vocabulary."""
import math,json
from collections import defaultdict


def boundary(points, faces, origin, normal):
    """Find the largest closed geometric cut loop near the admitted neck plane."""
    keys=[tuple(round(float(v),5) for v in p) for p in points]
    ids={};edges=defaultdict(int)
    for face in faces:
        for a,b in zip(face,face[1:]+face[:1]):
            x,y=keys[a],keys[b]
            if x==y:continue
            ids.setdefault(x,a);ids.setdefault(y,b);edges[tuple(sorted((x,y)))]+=1
    graph=defaultdict(set)
    for (a,b),count in edges.items():
        if count==1:graph[a].add(b);graph[b].add(a)
    seen=set();loops=[];components=[]
    for start in sorted(graph):
        if start in seen:continue
        component=set();todo=[start]
        while todo:
            p=todo.pop()
            if p in component:continue
            component.add(p);todo.extend(graph[p]-component)
        seen.update(component);components.append(dict(vertices=len(component),degrees=sorted(set(len(graph[p]) for p in component))))
        if len(component)<6 or any(len(graph[p])!=2 for p in component):continue
        # Classify complete components. Clipping edges at a search window can
        # falsely turn an existing closed neck loop into an open chain.
        if max(abs(sum((p[k]-origin[k])*normal[k] for k in range(3))) for p in component)>.35:continue
        order=[start];previous=None;current=start
        while True:
            choices=sorted(graph[current]-({previous} if previous is not None else set()))
            nxt=choices[0]
            if nxt==start:break
            if nxt in order:break
            order.append(nxt);previous,current=current,nxt
        if len(order)!=len(component):continue
        length=sum(math.dist(a,b) for a,b in zip(order,order[1:]+order[:1]))
        center=[sum(p[k] for p in order)/len(order) for k in range(3)]
        if math.dist(center,origin)<.45:loops.append((length,[ids[p] for p in order]))
    return (max(loops,key=lambda x:x[0])[1] if loops else []),components


def stitch(points,a,b):
    """Zipper triangulation shares literal endpoint vertices, not overlapping caps."""
    best=None
    for flip in [False,True]:
        q=list(reversed(b)) if flip else list(b)
        for shift in range(len(q)):
            seq=q[shift:]+q[:shift]
            cost=sum(math.dist(points[a[i]],points[seq[round(i*len(seq)/len(a))%len(seq)]])**2 for i in range(len(a)))
            if best is None or cost<best[0]:best=(cost,seq)
    b=best[1]
    def progress(seq):
        lens=[math.dist(points[x],points[y]) for x,y in zip(seq,seq[1:]+seq[:1])];total=sum(lens);values=[0.]
        for v in lens:values.append(values[-1]+v/total)
        return values
    aa=progress(a);bb=progress(b);i=j=0;faces=[]
    while i<len(a) or j<len(b):
        if j==len(b) or (i<len(a) and aa[i+1]<=bb[j+1]):
            faces.append((a[i%len(a)],a[(i+1)%len(a)],b[j%len(b)]));i+=1
        else:
            faces.append((a[i%len(a)],b[(j+1)%len(b)],b[j%len(b)]));j+=1
    return faces,b


def build(bpy,out,body,head,body_posed,head_posed,origin,normal):
    from mathutils import Vector
    body_faces=[list(p.vertices) for p in body.data.polygons];head_faces=[list(p.vertices) for p in head.data.polygons]
    a,ca=boundary(body_posed,body_faces,origin,normal)
    target=Vector(origin)+Vector(normal)*.08;b,cb=boundary(head_posed,head_faces,target,normal)
    report=dict(body_loop=len(a),head_loop=len(b),body_components=ca,head_components=cb)
    (out/'warhorse384-join.json').write_text(json.dumps(report,indent=2)+'\n')
    if not a or not b:raise ValueError('WARHORSE384_JOIN_CLOSED_LOOPS:'+str((len(a),len(b))))
    n=len(body.data.vertices);combined_posed=list(body_posed)+list(head_posed);b=[n+i for i in b]
    bridge,b=stitch(combined_posed,a,b)
    center=sum((Vector(combined_posed[i]) for i in a+b),Vector((0,0,0)))/(len(a)+len(b))
    direction=0.
    for f in bridge:
        x,y,z=[Vector(combined_posed[i]) for i in f];direction+=(y-x).cross(z-x).dot((x+y+z)/3-center)
    if direction<0:bridge=[tuple(reversed(f)) for f in bridge]
    body_names={g.index:g.name for g in body.vertex_groups};head_names={g.index:g.name for g in head.vertex_groups}
    coords=[tuple(v.co) for v in body.data.vertices]+[tuple(v.co) for v in head.data.vertices]
    weights=[{body_names[g.group]:g.weight for g in v.groups} for v in body.data.vertices]+[{head_names[g.group]:g.weight for g in v.groups} for v in head.data.vertices]
    materials=list(body.data.materials)+list(head.data.materials)
    from collections import Counter
    dominant=Counter(p.material_index for p in head.data.polygons).most_common(1)[0][0]
    material_offset=len(body.data.materials);skin=head.data.materials[dominant].copy();skin.name='MF384 continuous neck skin'
    nodes=skin.node_tree.nodes;links=skin.node_tree.links;bs=next(x for x in nodes if x.type=='BSDF_PRINCIPLED')
    # The same source coat projection as head; endpoint blend matches actual body UV.
    donor_bs=next(x for x in body.data.materials[0].node_tree.nodes if x.type=='BSDF_PRINCIPLED');image=donor_bs.inputs['Base Color'].links[0].from_socket.node.image
    attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='MF384_rest';sep=nodes.new('ShaderNodeSeparateXYZ');links.new(attr.outputs['Vector'],sep.inputs[0]);co=nodes.new('ShaderNodeCombineXYZ')
    for axis,factor,offset,to in [('X',.20,.40,'X'),('Z',.12,.25,'Y')]:
        mul=nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';links.new(sep.outputs[axis],mul.inputs[0]);mul.inputs[1].default_value=factor
        add=nodes.new('ShaderNodeMath');add.operation='ADD';links.new(mul.outputs[0],add.inputs[0]);add.inputs[1].default_value=offset;links.new(add.outputs[0],co.inputs[to])
    tex=nodes.new('ShaderNodeTexImage');tex.image=image;links.new(co.outputs[0],tex.inputs['Vector'])
    bodyuv=nodes.new('ShaderNodeAttribute');bodyuv.attribute_name='MF384_body_uv';oldtex=nodes.new('ShaderNodeTexImage');oldtex.image=image;links.new(bodyuv.outputs['Vector'],oldtex.inputs['Vector'])
    join=nodes.new('ShaderNodeAttribute');join.attribute_name='MF384_join';mix=nodes.new('ShaderNodeMixRGB');links.new(join.outputs['Fac'],mix.inputs[0]);links.new(oldtex.outputs['Color'],mix.inputs[1]);links.new(tex.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
    for l in list(bs.inputs['Normal'].links):links.remove(l)
    noise=nodes.new('ShaderNodeTexNoise');links.new(attr.outputs['Vector'],noise.inputs['Vector']);noise.inputs['Scale'].default_value=200.
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00025;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    for key,value in [('Roughness',.68),('Metallic',0.)]:
        for l in list(bs.inputs[key].links):links.remove(l)
        bs.inputs[key].default_value=value
    materials.append(skin);bridge_slot=len(materials)-1
    uv_body=[(0.,0.)]*n
    for loop,uv in zip(body.data.loops,body.data.uv_layers.active.data):uv_body[loop.vertex_index]=tuple(uv.uv)
    body_uv=list(uv_body)+[(0.,0.)]*len(head.data.vertices)
    for i in b:
        closest=min(a,key=lambda j:math.dist(combined_posed[i],combined_posed[j]));body_uv[i]=uv_body[closest]
    normals=[tuple(v.normal) for v in body.data.vertices]+[tuple(v.normal) for v in head.data.vertices]
    old_normals=[];uv_loops=[];slots=[]
    for ob,offset in [(body,0),(head,material_offset)]:
        for p in ob.data.polygons:
            slots.append(p.material_index+offset)
            for l in p.loop_indices:old_normals.append(tuple(ob.data.corner_normals[l].vector));uv_loops.append(tuple(ob.data.uv_layers.active.data[l].uv))
    for f in bridge:
        slots.append(bridge_slot)
        for i in f:old_normals.append(normals[i]);uv_loops.append((0.,0.))
    data=bpy.data.meshes.new('MF384 unified head neck body');data.from_pydata(coords,[],body_faces+[[n+i for i in f] for f in head_faces]+bridge);data.update()
    for mat in materials:data.materials.append(mat)
    for p,slot in zip(data.polygons,slots):p.material_index=slot;p.use_smooth=True
    uv=data.uv_layers.new(name='UVMap')
    for v,co in zip(uv.data,uv_loops):v.uv=co
    data.normals_split_custom_set(old_normals)
    body.data=data
    for i,ws in enumerate(weights):
        for name,w in ws.items():
            g=body.vertex_groups.get(name) or body.vertex_groups.new(name=name);g.add([i],w,'REPLACE')
    for name,typ,values,field in [('MF384_rest','FLOAT_VECTOR',[float(x) for p in combined_posed for x in p],'vector'),('MF384_body_uv','FLOAT_VECTOR',[float(x) for p in body_uv for x in (*p,0.)],'vector'),('MF384_join','FLOAT',[0.]*n+[1.]*len(head.data.vertices),'value')]:
        a_=data.attributes.new(name,typ,'POINT');a_.data.foreach_set(field,values)
    if coords[:n]!=[tuple(v.co) for v in data.vertices[:n]]:raise ValueError('WARHORSE384_JOIN_ORIGINAL_DRIFT')
    head.hide_render=True;body['mf384_merged']=True
    report.update(bridge_faces=len(bridge),literal_shared_boundary_vertices=True,new_vertices=0,body_vertices_preserved=n,combined_vertices=len(coords))
    (out/'warhorse384-join.json').write_text(json.dumps(report,indent=2)+'\n');return report
