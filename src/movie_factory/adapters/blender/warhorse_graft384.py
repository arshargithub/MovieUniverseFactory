"""Reuse the existing native horse head on the heavier donor; fixed local route."""
import json,hashlib
from collections import Counter


def mapped_group(name):
    if name.startswith('DEF-jaw'):return 'jaw'
    if name.startswith('DEF-ear'):return 'ear_L' if name.endswith('.L') else 'ear_R'
    if name.startswith('DEF-neck'):
        return 'neck_01' if name.endswith('.001') else 'neck_02' if name.endswith('.002') else 'neck_03'
    return 'head'


def component_member(weights):
    head=sum(w for name,w in weights.items() if name.startswith(('DEF-head','DEF-jaw','DEF-ear','DEF-eye','DEF-teeth','DEF-tongue')))
    neck=sum(w for name,w in weights.items() if name in {'DEF-neck.003','DEF-neck.004'})
    return head>.015 or neck>.35


def run(bpy,out):
    import bmesh
    from mathutils import Vector,Matrix
    studio=bpy.context.scene;rig=bpy.data.objects['MF383 Warhorse rig'];body=bpy.data.objects['MF383 Warhorse surface']
    source=bpy.data.objects['horse'];sr=bpy.data.objects['horse.rig']
    if studio.name!='MF383 Warhorse studio' or bpy.data.objects.get('MF384 reused horse head'):raise ValueError('WARHORSE384_GRAFT_OWNERS')
    owners=[s for s in bpy.data.scenes if s!=studio and source.name in s.objects]
    if len(owners)!=1:raise ValueError('WARHORSE384_GRAFT_SOURCE_SCENE')
    owner=owners[0];oldframe=owner.frame_current;levels=[(m,m.show_viewport) for m in source.modifiers if m.type=='SUBSURF']
    bpy.context.window.scene=owner;owner.frame_set(283)
    for m,_ in levels:m.show_viewport=False
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=source.evaluated_get(dg);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
    source_names={g.index:g.name for g in source.vertex_groups}
    try:
        convert=sr.matrix_world.inverted()@source.matrix_world
        points=[convert@v.co for v in me.vertices]
        weights=[];raw_weights=[]
        for v in me.vertices:
            raw_weights.append({source_names[g.group]:g.weight for g in v.groups if g.weight>1e-8})
            w={}
            for g in v.groups:
                if g.weight>1e-8:
                    name=mapped_group(source_names[g.group]);w[name]=w.get(name,0.)+g.weight
            if not w:w={'head':1.}
            weights.append(w)
        # Broad candidate includes unclassified facial skin; final anatomical
        # section is made after landmark alignment, not by a face-cropping box.
        keep={i for i,w in enumerate(raw_weights) if component_member(w) or (points[i].y<-.70 and points[i].z>1.50)}
        faces=[p for p in me.polygons if all(i in keep for i in p.vertices)]
        ids=sorted({i for f in faces for i in f.vertices});remap={v:i for i,v in enumerate(ids)}
        if len(ids)<300:raise ValueError('WARHORSE384_GRAFT_HEAD_DOMAIN:'+str(len(ids)))
        coverage={}
        for label,prefix in [('left_ear','DEF-ear'),('jaw','DEF-jaw'),('eye','DEF-eye')]:
            expected={i for i,w in enumerate(raw_weights) if sum(v for n,v in w.items() if n.startswith(prefix))>.05}
            fraction=len(expected.intersection(ids))/max(1,len(expected))
            coverage[label]=dict(source=len(expected),included=len(expected.intersection(ids)),fraction=fraction)
            if expected and fraction<.98:raise ValueError('WARHORSE384_GRAFT_COMPONENT_CROP:'+label)
        data=dict(points=[points[i].copy() for i in ids],weights=[weights[i] for i in ids],source_ids=ids,
            faces=[tuple(remap[i] for i in f.vertices) for f in faces],materials=list(me.materials),slots=[f.material_index for f in faces],
            uv=[[tuple(me.uv_layers.active.data[l].uv) for l in f.loop_indices] for f in faces],
            poll=(sr.pose.bones['DEF-ear.L'].head+sr.pose.bones['DEF-ear.R'].head)/2,
            ears=(sr.pose.bones['DEF-ear.R'].head-sr.pose.bones['DEF-ear.L'].head).copy())
        # Clone the already fitted anatomical bridle, not inherited old rein spans.
        tack=[]
        for name in ['358 cheek leather L','358 cheek leather R','358 bit ring L','358 bit ring R','358 crown behind ears','358 brow above eyes','358 supported noseband']:
            ob=bpy.data.objects.get(name)
            if ob is None or ob.type!='MESH':raise ValueError('WARHORSE384_GRAFT_TACK:'+name)
            e=ob.evaluated_get(dg);m=e.to_mesh()
            try:tack.append(dict(name=name,points=[sr.matrix_world.inverted()@ob.matrix_world@v.co for v in m.vertices],faces=[tuple(p.vertices) for p in m.polygons],materials=list(m.materials),slots=[p.material_index for p in m.polygons]))
            finally:e.to_mesh_clear()
    finally:
        ev.to_mesh_clear()
        for m,value in levels:m.show_viewport=value
        owner.frame_set(oldframe);bpy.context.window.scene=studio;studio.frame_set(283);bpy.context.view_layer.update()
    groups={g.index:g.name for g in body.vertex_groups}
    headweight=[sum(g.weight for g in v.groups if groups[g.group] in {'head','jaw','ear_L','ear_R'}) for v in body.data.vertices]
    target_ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());target_me=target_ev.to_mesh()
    try:
        body_posed=[rig.matrix_world.inverted()@body.matrix_world@v.co for v in target_me.vertices]
        target_points=[p for i,p in enumerate(body_posed) if headweight[i]>.5]
    finally:target_ev.to_mesh_clear()
    def muzzle(points):
        front=min(p.y for p in points)
        selected=[p for p in points if p.y<front+.025]
        return sum(selected,Vector((0,0,0)))/len(selected)
    tp=(rig.pose.bones['ear_L'].head+rig.pose.bones['ear_R'].head)/2
    te=rig.pose.bones['ear_R'].head-rig.pose.bones['ear_L'].head
    sp=data['poll'];sf=muzzle(data['points'])-sp;tf=muzzle(target_points)-tp
    def frame(forward,ear):
        z=forward.normalized();x=(ear-z*ear.dot(z)).normalized();y=z.cross(x).normalized()
        return Matrix((x,y,z)).transposed()
    rotation=frame(tf,te)@frame(sf,data['ears']).transposed();scale=tf.length/sf.length
    if not .55<scale<1.4 or rotation.determinant()<.9:raise ValueError('WARHORSE384_GRAFT_TRANSFORM:'+str(scale))
    def transform(p):return tp+rotation@((p-sp)*scale)
    origin=(rig.pose.bones['neck_02'].head+rig.pose.bones['neck_03'].head)/2
    normal=(rig.pose.bones['head'].head-rig.pose.bones['neck_02'].head).normalized()
    mapped=[transform(p) for p in data['points']]
    selected=[j for j,f in enumerate(data['faces']) if all((mapped[i]-origin).dot(normal)>.08 for i in f)]
    used=sorted({i for j in selected for i in data['faces'][j]});lookup={i:j for j,i in enumerate(used)}
    data['faces']=[tuple(lookup[i] for i in data['faces'][j]) for j in selected]
    for key in ['slots','uv']:data[key]=[data[key][j] for j in selected]
    for key in ['points','weights','source_ids']:data[key]=[data[key][i] for i in used]
    actual=set(data['source_ids'])
    for label,prefix in [('ears','DEF-ear'),('jaw','DEF-jaw'),('eye','DEF-eye')]:
        expected={i for i,w in enumerate(raw_weights) if sum(v for n,v in w.items() if n.startswith(prefix))>.05}
        fraction=len(expected.intersection(actual))/max(1,len(expected));coverage[label]=dict(source=len(expected),included=len(expected.intersection(actual)),fraction=fraction)
        if expected and fraction<.98:raise ValueError('WARHORSE384_SECTION_COMPONENT:'+label+':'+str(fraction))
    if len(data['points'])<300:raise ValueError('WARHORSE384_SECTION_EMPTY')
    def bind(point,weights):
        total=sum(weights.values());weights={n:v/total for n,v in weights.items()}
        matrix=Matrix([[0.]*4 for _ in range(4)])
        for name,w in weights.items():
            bone=rig.pose.bones[name];m=bone.matrix@bone.bone.matrix_local.inverted()
            for i in range(4):
                for j in range(4):matrix[i][j]+=m[i][j]*w
        if abs(matrix.determinant())<1e-6:raise ValueError('WARHORSE384_GRAFT_SINGULAR')
        return matrix.inverted()@point,weights
    def create(name,points,faces,weights,mats,slots):
        desired=[transform(p) for p in points];bound=[bind(p,w) for p,w in zip(desired,weights)]
        me=bpy.data.meshes.new(name);me.from_pydata([p for p,w in bound],[],faces);me.update();ob=bpy.data.objects.new(name,me);studio.collection.objects.link(ob)
        ob.parent=rig;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4)
        for mat in mats:me.materials.append(mat.copy())
        for i,(point,w) in enumerate(bound):
            for bone,value in w.items():
                group=ob.vertex_groups.get(bone) or ob.vertex_groups.new(name=bone);group.add([i],value,'REPLACE')
        for p,slot in zip(me.polygons,slots):p.material_index=slot;p.use_smooth=True
        arm=ob.modifiers.new('MF384 reused head skinning','ARMATURE');arm.object=rig
        attr=me.attributes.new('MF384_rest','FLOAT_VECTOR','POINT');attr.data.foreach_set('vector',[float(x) for p in desired for x in p])
        return ob,desired
    head,desired=create('MF384 reused horse head',data['points'],data['faces'],data['weights'],data['materials'],data['slots'])
    uv=head.data.uv_layers.new(name='UVMap')
    for face,coords in zip(head.data.polygons,data['uv']):
        for loop,p in zip(face.loop_indices,coords):uv.data[loop].uv=p
    # Same source coat on main head skin; preserve separate eyes/mouth material slots and original fur relief.
    dominant=Counter(data['slots']).most_common(1)[0][0];mat=head.data.materials[dominant];mat.name='MF384 reused head matched coat'
    bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    donor_bs=next(n for n in body.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED');image=donor_bs.inputs['Base Color'].links[0].from_socket.node.image
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;a=nodes.new('ShaderNodeAttribute');a.attribute_name='MF384_rest';sep=nodes.new('ShaderNodeSeparateXYZ');links.new(a.outputs['Vector'],sep.inputs[0]);co=nodes.new('ShaderNodeCombineXYZ')
    for axis,factor,offset,outaxis in [('X',.20,.40,'X'),('Z',.12,.25,'Y')]:
        mul=nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';links.new(sep.outputs[axis],mul.inputs[0]);mul.inputs[1].default_value=factor
        add=nodes.new('ShaderNodeMath');add.operation='ADD';links.new(mul.outputs[0],add.inputs[0]);add.inputs[1].default_value=offset;links.new(add.outputs[0],co.inputs[outaxis])
    tex=nodes.new('ShaderNodeTexImage');tex.image=image;links.new(co.outputs[0],tex.inputs['Vector']);links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    copied=[]
    for item in tack:
        ob,_=create('MF384 reused '+item['name'],item['points'],item['faces'],[{'head':1.} for _ in item['points']],item['materials'],item['slots']);copied.append(ob.name)
    # Delete head faces only. No coordinate welding, normal recomputation or body vertex deletion.
    bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
    layer=bm.faces.layers.int.new('MF384_graft_source_face')
    for f in bm.faces:f[layer]=f.index+1
    original_normals={(p.index+1,body.data.loops[l].vertex_index):tuple(body.data.corner_normals[l].vector) for p in body.data.polygons for l in p.loop_indices}
    original_points=[tuple(v.co) for v in body.data.vertices]
    original_weights=[sorted((g.group,g.weight) for g in v.groups) for v in body.data.vertices]
    remove=[f for f in bm.faces if any((body_posed[v.index]-origin).dot(normal)>0 or headweight[v.index]>.15 for v in f.verts)]
    bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY');removed=len(remove);bm.to_mesh(body.data);bm.free();body.data.update()
    if original_points!=[tuple(v.co) for v in body.data.vertices]:raise ValueError('WARHORSE384_GRAFT_BODY_VERTEX_DRIFT')
    if original_weights!=[sorted((g.group,g.weight) for g in v.groups) for v in body.data.vertices]:raise ValueError('WARHORSE384_GRAFT_BODY_WEIGHT_DRIFT')
    normals=[]
    for p in body.data.polygons:
        old=body.data.attributes['MF384_graft_source_face'].data[p.index].value
        for l in p.loop_indices:normals.append(original_normals[old,body.data.loops[l].vertex_index])
    body.data.normals_split_custom_set(normals)
    import importlib.util
    from pathlib import Path
    spec=importlib.util.spec_from_file_location('mf_join384',Path(__file__).with_name('warhorse_join384.py'));join=importlib.util.module_from_spec(spec);spec.loader.exec_module(join)
    joint=join.build(bpy,out,body,head,body_posed,desired,origin,normal)
    bpy.context.view_layer.update();ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:error=max(((rig.matrix_world.inverted()@head.matrix_world@v.co)-p).length for v,p in zip(me.vertices,desired))
    finally:ev.to_mesh_clear()
    if error>.0001:raise ValueError('WARHORSE384_GRAFT_BIND_RESIDUAL:'+str(error))
    report=dict(head_vertices=len(head.data.vertices),head_faces=len(head.data.polygons),component_coverage=coverage,joint=joint,scale=scale,rotation=[list(row) for row in rotation],bind_residual=error,deleted_old_head_faces=removed,body_coordinates_exact=True,bridle=copied,source='Existing native horse head from protected373 derivative; donor heavier body retained.',scope='Head/neck fit and full rearing deformation require actual front/side/reverse review; no rig action edits or production adoption.')
    (out/'warhorse384-headgraft.json').write_text(json.dumps(report,indent=2)+'\n');return report
