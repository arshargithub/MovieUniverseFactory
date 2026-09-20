"""Bounded native upper-body tailoring against pinned approved portraits.

No job-supplied paths/code, network or provider access. FBHead is immutable.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'reference-dress-18/dressed.blend'
SOURCE_SHA='1fbe41cad8e01cab7d7ef41dee471e9a6aaad2253fb1e2beb4fcf9714da44e0b'
REF=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01/frontal-v02-individualized.png'
REF_SHA='7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75'


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','variant'}:
        raise ValueError('Exact structured keys required')
    if job['operation'] not in ('audit','build','verify','portraits','detail','facecheck','package','verify_package','diagnostic','shoulders','clay','contacts'):
        raise ValueError('Unsupported operation')
    if type(job['variant']) is not int or not 1<=job['variant']<=28:
        raise ValueError('Unsupported variant')
    for path,digest in ((SOURCE,SOURCE_SHA),(REF,REF_SHA)):
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('Pinned source changed')
    out=BASE/f'upperbody-{job["operation"]}-{job["variant"]:02}'
    if out.exists() or shutil.disk_usage(BASE).free<5_000_000_000:
        raise ValueError('Existing output or disk low')
    return out


def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)


def neck_weight(z):
    # Fully zero above this plane: no jaw/face geometry or material edits.
    return smooth((-.86-z)/.22)


def muscle_relief(x,y,z):
    front=smooth((.3-y)/.55)
    center=.14+.34*smooth((z+1.65)/.72)
    tendon=.028*math.exp(-((abs(x)-center)/.10)**2)*math.exp(-((z+1.30)/.38)**2)
    return neck_weight(z)*front*tendon


def torso_point(angle,z):
    # Modest covered torso, not an anatomical/body-design approval.
    sections=[(-1.45,.65,.48),(-1.85,1.85,.69),(-2.35,1.88,.85),
              (-3.0,1.70,.91),(-3.8,1.49,.78),(-4.7,1.34,.70),(-5.8,1.55,.77)]
    for a,b in zip(sections,sections[1:]):
        if b[0]<=z<=a[0]:
            t=smooth((a[0]-z)/(a[0]-b[0]));rx=a[1]*(1-t)+b[1]*t;ry=a[2]*(1-t)+b[2]*t;break
    else:rx,ry=sections[-1][1:]
    fold=.028*math.sin(angle*13+z*3)+.016*math.sin(angle*23-z*2)
    return ((rx+fold)*math.sin(angle),.22-(ry+fold)*math.cos(angle),z)


def cloth_material(name,color,variant=1):
    import bpy
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    nodes,links=mat.node_tree.nodes,mat.node_tree.links;p=nodes.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.9
    coords=nodes.new('ShaderNodeTexCoord');noise=nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=22;noise.inputs['Detail'].default_value=2
    links.new(coords.outputs['Object'],noise.inputs['Vector'])
    ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
    ramp.color_ramp.elements[0].position=.35;ramp.color_ramp.elements[0].color=tuple(v*.5 for v in color)+(1,)
    ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=tuple(v*1.3 for v in color)+(1,)
    middle=ramp.color_ramp.elements.new(.50);middle.color=tuple(color)+(1,)
    if variant>=2:
        for element,factor in zip(sorted(ramp.color_ramp.elements,key=lambda e:e.position),(.82,1,1.12)):
            element.color=tuple(v*factor for v in color)+(1,)
        noise.inputs['Scale'].default_value=9
        scale=nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1.5,2,9)
        links.new(coords.outputs['Object'],scale.inputs[0]);links.new(scale.outputs[0],noise.inputs['Vector'])
    links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],p.inputs['Base Color'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.006
    links.new(noise.outputs[0],bump.inputs['Height']);links.new(bump.outputs[0],p.inputs['Normal'])
    return mat


def skin_material(variant):
    import bpy
    mat=cloth_material('MF_neck_illustrated_skin',(.34,.16,.075),variant)
    nodes,links=mat.node_tree.nodes,mat.node_tree.links;p=nodes.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.73
    p.inputs['Specular IOR Level'].default_value=.18
    coords=nodes.new('ShaderNodeTexCoord');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(coords.outputs['Object'],sep.inputs[0])
    u=nodes.new('ShaderNodeMath');u.operation='MULTIPLY_ADD';u.inputs[1].default_value=.238;u.inputs[2].default_value=.50;links.new(sep.outputs['X'],u.inputs[0])
    v=nodes.new('ShaderNodeMath');v.operation='MULTIPLY_ADD';v.inputs[1].default_value=.18;v.inputs[2].default_value=.646;links.new(sep.outputs['Z'],v.inputs[0])
    uv=nodes.new('ShaderNodeCombineXYZ');links.new(u.outputs[0],uv.inputs[0]);links.new(v.outputs[0],uv.inputs[1])
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(REF));tex.image.pack();tex.extension='EXTEND';links.new(uv.outputs[0],tex.inputs[0])
    rgb=nodes.new('ShaderNodeSeparateColor');links.new(tex.outputs['Color'],rgb.inputs[0])
    red=nodes.new('ShaderNodeMath');red.operation='GREATER_THAN';links.new(rgb.outputs['Red'],red.inputs[0]);links.new(rgb.outputs['Green'],red.inputs[1])
    bright=nodes.new('ShaderNodeMath');bright.operation='GREATER_THAN';bright.inputs[1].default_value=.14;links.new(rgb.outputs['Red'],bright.inputs[0])
    mask=nodes.new('ShaderNodeMath');mask.operation='MULTIPLY';links.new(red.outputs[0],mask.inputs[0]);links.new(bright.outputs[0],mask.inputs[1])
    mix=nodes.new('ShaderNodeMixRGB');old=p.inputs['Base Color'].links[0].from_socket
    links.new(old,mix.inputs[1]);links.new(tex.outputs['Color'],mix.inputs[2]);links.new(mask.outputs[0],mix.inputs[0]);links.new(mix.outputs[0],p.inputs['Base Color'])
    attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='MF_neck_overlay_weight';links.new(attr.outputs['Fac'],p.inputs['Alpha'])
    return mat


def make_neck(variant):
    import bpy,bmesh
    from reference_dressing import mesh_object
    head=bpy.data.objects['FBHead'];dg=bpy.context.evaluated_depsgraph_get()
    if variant>=4:
        return make_continuous_neck(head,variant)
    if variant>=3:
        return make_neck_replacement(head,variant)
    mesh=bpy.data.meshes.new_from_object(head.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,-.86),plane_no=(0,0,1),clear_outer=True,dist=.000001)
    bm.normal_update()
    for vert in bm.verts:
        x,y,z=vert.co;vert.co+=vert.normal*(.004*neck_weight(z));vert.co.y-=muscle_relief(x,y,z)
    bm.to_mesh(mesh);bm.free()
    ob=bpy.data.objects.new('MF_separate_neck_detail',mesh);bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world=head.matrix_world.copy();mesh.materials.clear();mat=skin_material(variant);mesh.materials.append(mat)
    weight=mesh.attributes.new('MF_neck_overlay_weight','FLOAT','POINT')
    for vertex in mesh.vertices:weight.data[vertex.index].value=neck_weight(vertex.co.z)
    # A separate upper-chest patch bridges the truncated neck into the tunic.
    verts=[];faces=[];nu,nv=96,40
    for i in range(nu+1):
        x=-1.50+3*i/nu
        for j in range(nv+1):
            z=-1.30-.90*j/nv
            clavicle=-1.72+.15*abs(x)+.035*math.sin(abs(x)*4)
            ridge=.050*math.exp(-((z-clavicle)/.075)**2)*smooth((abs(x)-.10)/.15)
            y=-.37-.23*smooth((-1.30-z)/.50)+.13*(x/1.50)**2-ridge
            verts.append((x,y,z))
    for i in range(nu):
        for j in range(nv):faces.append((i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1))
    ob=mesh_object('MF_clavicle_upper_chest',verts,faces,mat,1)
    weight=ob.data.attributes.new('MF_neck_overlay_weight','FLOAT','POINT')
    for vertex in ob.data.vertices:
        x,y,z=vertex.co;alpha=smooth((-1.32-z)/.10)
        if variant>=2:
            admitted_width=.80-.48*smooth((-1.35-z)/.60)
            alpha*=smooth((admitted_width-abs(x))/.07)
        weight.data[vertex.index].value=alpha


def protected_face_digest(obj):
    payload={'vertices':[(v.index,list(v.co)) for v in obj.data.vertices if v.co.z>=-.86],
             'shapes':{k.name:[(i,list(v.co)) for i,v in enumerate(k.data) if obj.data.vertices[i].co.z>=-.86]
                       for k in obj.data.shape_keys.key_blocks},
             'matrix':[list(row) for row in obj.matrix_world],
             'uv':[list(p.uv) for p in obj.data.uv_layers.active.data]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()


def protected_surface_digest(obj):
    """Index-independent evaluated facial positions and per-corner UVs."""
    import bpy
    dg=bpy.context.evaluated_depsgraph_get();evaluated=obj.evaluated_get(dg);mesh=evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
    uv=mesh.uv_layers.active.data;faces=[]
    for face in mesh.polygons:
        if all(mesh.vertices[i].co.z>=-.86 for i in face.vertices):
            corners=[(tuple(mesh.vertices[mesh.loops[li].vertex_index].co),tuple(uv[li].uv)) for li in face.loop_indices]
            faces.append(sorted(corners))
    evaluated.to_mesh_clear()
    return hashlib.sha256(json.dumps(sorted(faces),sort_keys=True).encode()).hexdigest()


def extend_neck_color(obj,head,variant):
    import bpy
    mat=head.data.materials[0].copy();mat.name='MF_protected_face_neck_extended'
    obj.data.materials.clear();obj.data.materials.append(mat)
    n,l=mat.node_tree.nodes,mat.node_tree.links;p=next(node for node in n if node.type=='BSDF_PRINCIPLED')
    original=p.inputs['Base Color'].links[0].from_socket
    if variant>=5:
        # Generated coordinates otherwise change when the neck extends the
        # bounding box. Freeze their original mapping to preserve facial color.
        generated=[link for link in list(l) if link.from_node.type=='TEX_COORD' and link.from_socket.name=='Generated']
        coords=n.new('ShaderNodeTexCoord');coords.object=head
        low=[min(v.co[c] for v in head.data.vertices) for c in range(3)]
        high=[max(v.co[c] for v in head.data.vertices) for c in range(3)]
        subtract=n.new('ShaderNodeVectorMath');subtract.operation='SUBTRACT';subtract.inputs[1].default_value=low;l.new(coords.outputs['Object'],subtract.inputs[0])
        divide=n.new('ShaderNodeVectorMath');divide.operation='DIVIDE';divide.inputs[1].default_value=tuple(b-a for a,b in zip(low,high));l.new(subtract.outputs[0],divide.inputs[0])
        for link in generated:l.new(divide.outputs[0],link.to_socket)
        obj['MF_frozen_generated_bounds']=json.dumps([low,high])
    coord=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Object'],sep.inputs[0])
    u=n.new('ShaderNodeMath');u.operation='MULTIPLY_ADD';u.inputs[1].default_value=.238;u.inputs[2].default_value=.5;l.new(sep.outputs['X'],u.inputs[0])
    v=n.new('ShaderNodeMath');v.operation='MULTIPLY_ADD';v.inputs[1].default_value=.18;v.inputs[2].default_value=.646;l.new(sep.outputs['Z'],v.inputs[0])
    uv=n.new('ShaderNodeCombineXYZ');l.new(u.outputs[0],uv.inputs[0]);l.new(v.outputs[0],uv.inputs[1])
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(REF));tex.image.pack();l.new(uv.outputs[0],tex.inputs[0])
    if variant>=6:
        # Explicit neck-skin reference patch; do not project the scarf back onto
        # a widened chest and then rely on RGB thresholds to hide the mistake.
        safe_u=n.new('ShaderNodeMapRange');safe_u.clamp=True;safe_u.inputs['From Min'].default_value=-.8;safe_u.inputs['From Max'].default_value=.8
        safe_u.inputs['To Min'].default_value=.40;safe_u.inputs['To Max'].default_value=.60;l.new(sep.outputs['X'],safe_u.inputs['Value']);l.new(safe_u.outputs['Result'],uv.inputs[0])
        safe_v=n.new('ShaderNodeMapRange');safe_v.clamp=True;safe_v.inputs['From Min'].default_value=-1.75;safe_v.inputs['From Max'].default_value=-.86
        safe_v.inputs['To Min'].default_value=.405;safe_v.inputs['To Max'].default_value=.49;l.new(sep.outputs['Z'],safe_v.inputs['Value']);l.new(safe_v.outputs['Result'],uv.inputs[1])
        if variant>=12:
            gain=n.new('ShaderNodeMapRange');gain.clamp=True;gain.inputs['From Min'].default_value=-1.7;gain.inputs['From Max'].default_value=-.95
            gain.inputs['To Min'].default_value=.125;gain.inputs['To Max'].default_value=.23;l.new(sep.outputs['Z'],gain.inputs['Value'])
            product=n.new('ShaderNodeMath');product.operation='MULTIPLY';l.new(sep.outputs['X'],product.inputs[0]);l.new(gain.outputs['Result'],product.inputs[1])
            offset=n.new('ShaderNodeMath');offset.operation='ADD';offset.inputs[1].default_value=.5;l.new(product.outputs[0],offset.inputs[0])
            low=n.new('ShaderNodeMath');low.operation='MAXIMUM';low.inputs[1].default_value=.37;l.new(offset.outputs[0],low.inputs[0])
            high=n.new('ShaderNodeMath');high.operation='MINIMUM';high.inputs[1].default_value=.63;l.new(low.outputs[0],high.inputs[0]);l.new(high.outputs[0],uv.inputs[0])
            safe_v.inputs['From Min'].default_value=-1.7;safe_v.inputs['From Max'].default_value=-.95
            safe_v.inputs['To Min'].default_value=.39;safe_v.inputs['To Max'].default_value=.51
            if variant>=13:
                # The previous upper patch sampled the illustrated chin edge.
                # Keep the visible neck reference below that dark painted line.
                safe_v.inputs['To Max'].default_value=.485
                gain.inputs['To Max'].default_value=.19
    rgb=n.new('ShaderNodeSeparateColor');l.new(tex.outputs[0],rgb.inputs[0])
    red=n.new('ShaderNodeMath');red.operation='GREATER_THAN';l.new(rgb.outputs['Red'],red.inputs[0]);l.new(rgb.outputs['Green'],red.inputs[1])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=45;noise.inputs['Detail'].default_value=1;l.new(coord.outputs['Object'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.27,.122,.053,1);ramp.color_ramp.elements[1].color=(.36,.185,.09,1);l.new(noise.outputs[0],ramp.inputs[0])
    skin=n.new('ShaderNodeMixRGB');l.new(red.outputs[0],skin.inputs[0]);l.new(ramp.outputs[0],skin.inputs[1]);l.new(tex.outputs[0],skin.inputs[2])
    if variant>=5:
        bright=n.new('ShaderNodeMapRange');bright.clamp=True;bright.inputs['From Min'].default_value=.10;bright.inputs['From Max'].default_value=.20;l.new(rgb.outputs['Red'],bright.inputs['Value'])
        gate=n.new('ShaderNodeMath');gate.operation='MULTIPLY';l.new(bright.outputs['Result'],gate.inputs[0]);l.new(red.outputs[0],gate.inputs[1]);l.new(gate.outputs[0],skin.inputs[0])
    if variant>=10:
        import statistics
        from likeness_cleanup import linear_channel
        pixels=list(tex.image.pixels);width,height=tex.image.size
        samples=[pixels[4*(int(height*(.415+j*.002))*width+int(width*(.48+i*.004))):4*(int(height*(.415+j*.002))*width+int(width*(.48+i*.004)))+3] for i in range(11) for j in range(11)]
        color=[linear_channel(statistics.median(s[k] for s in samples)) for k in range(3)]
        ramp.color_ramp.elements[0].color=tuple(c*.92 for c in color)+(1,)
        ramp.color_ramp.elements[1].color=tuple(c*1.08 for c in color)+(1,)
        fade=n.new('ShaderNodeMapRange');fade.clamp=True;fade.inputs['From Min'].default_value=-1.9;fade.inputs['From Max'].default_value=-1.48;l.new(sep.outputs['Z'],fade.inputs['Value'])
        safe=n.new('ShaderNodeMath');safe.operation='MULTIPLY';l.new(fade.outputs['Result'],safe.inputs[0]);l.new(gate.outputs[0],safe.inputs[1]);l.new(safe.outputs[0],skin.inputs[0])
        if variant>=15:
            # A frontal illustration cannot supply side-neck texture: fade its
            # projection by surface orientation rather than stretch edge rows.
            geo=n.new('ShaderNodeNewGeometry')
            dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(0,-1,0);l.new(geo.outputs['Normal'],dot.inputs[0])
            facing=n.new('ShaderNodeMapRange');facing.clamp=True;facing.interpolation_type='SMOOTHSTEP'
            facing.inputs['From Min'].default_value=.25;facing.inputs['From Max'].default_value=.85;l.new(dot.outputs['Value'],facing.inputs['Value'])
            projected=n.new('ShaderNodeMath');projected.operation='MULTIPLY';l.new(safe.outputs[0],projected.inputs[0]);l.new(facing.outputs['Result'],projected.inputs[1]);l.new(projected.outputs[0],skin.inputs[0])
    weight=n.new('ShaderNodeMapRange');weight.clamp=True;weight.inputs['From Min'].default_value=-.86;weight.inputs['From Max'].default_value=-1.10;l.new(sep.outputs['Z'],weight.inputs['Value'])
    if variant>=5:weight.inputs['From Max'].default_value=-.94
    mix=n.new('ShaderNodeMixRGB');l.new(weight.outputs['Result'],mix.inputs[0]);l.new(original,mix.inputs[1]);l.new(skin.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])


def make_continuous_neck(head,variant):
    import bpy,bmesh
    from mathutils import Vector
    baseline=protected_surface_digest(head);dg=bpy.context.evaluated_depsgraph_get()
    mesh=bpy.data.meshes.new_from_object(head.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,-.95),plane_no=(0,0,1),clear_inner=True,dist=.000001)
    edges=[e for e in bm.edges if e.is_boundary and all(abs(v.co.z+.95)<.0001 for v in e.verts)]
    ring={v for edge in edges for v in edge.verts}
    if len(ring)<16 or any(sum(e in edges for e in v.link_edges)!=2 for v in ring):raise ValueError('Neck termination must be a closed boundary')
    rows={v:[v] for v in ring};steps=32
    sections=[(-.95,.63,.70),(-1.2,.62,.65),(-1.40,.73,.65),(-1.65,1.16,.68),(-1.9,1.53,.70),(-2.3,1.75,.77)]
    for vertex,row in rows.items():
        ox,oy,oz=vertex.co;angle=math.atan2(ox,oy-.18)
        for j in range(1,steps+1):
            z=-.95-1.35*j/steps
            for a,b in zip(sections,sections[1:]):
                if b[0]<=z<=a[0]:
                    t=smooth((a[0]-z)/(a[0]-b[0]));rx=a[1]*(1-t)+b[1]*t;ry=a[2]*(1-t)+b[2]*t;break
            else:rx,ry=sections[-1][1:]
            blend=smooth((-.95-z)/.20)
            x=ox*(1-blend)+(rx*math.sin(angle))*blend
            y=oy*(1-blend)+(.22+ry*math.cos(angle))*blend
            clavicle=-1.73+.14*abs(x)
            if variant>=7:clavicle=-1.51+.07*abs(x)
            front=max(0,-math.cos(angle))
            y-=(.065 if variant>=7 else .05)*math.exp(-((z-clavicle)/.095)**2)*smooth((abs(x)-.1)/.2)*front
            y-=(1.5 if variant>=7 else 1)*muscle_relief(x,y,z)
            if variant>=7:y+=.032*math.exp(-(x/.18)**2-((z+1.52)/.16)**2)*front
            row.append(bm.verts.new((x,y,z)))
    for edge in edges:
        a,b=edge.verts
        for j in range(steps):bm.faces.new((rows[a][j],rows[b][j],rows[b][j+1],rows[a][j+1]))
    if variant>=5:
        transition=[v for v in bm.verts if -1.12<v.co.z<-.87]
        for _ in range(5):bmesh.ops.smooth_vert(bm,verts=transition,factor=.25,use_axis_x=True,use_axis_y=True,use_axis_z=False)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new('MF_continuous_head_neck',mesh);bpy.context.scene.collection.objects.link(obj);obj.matrix_world=head.matrix_world.copy()
    for poly in mesh.polygons:poly.use_smooth=True
    extend_neck_color(obj,head,variant);head.hide_render=True
    bpy.context.view_layer.update()
    assert protected_surface_digest(obj)==baseline
    obj['MF_protected_surface_digest']=baseline


def make_neck_replacement(head,variant):
    import bpy
    from reference_dressing import mesh_object
    # Preserve the approved source object. The visible copy only changes the
    # explicitly authorized neck below the protected facial boundary.
    duplicate=head.copy();duplicate.data=head.data.copy();duplicate.name='MF_display_head_neck'
    bpy.context.scene.collection.objects.link(duplicate);head.hide_render=True
    baseline=protected_face_digest(head)
    def shape(co):
        x,y,z=co;w=neck_weight(z)
        return (x*(1-.30*w),y-muscle_relief(x,y,z),z)
    for vertex in duplicate.data.vertices:vertex.co=shape(vertex.co)
    for key in duplicate.data.shape_keys.key_blocks:
        for vertex in key.data:vertex.co=shape(vertex.co)
    assert protected_face_digest(duplicate)==baseline
    duplicate['MF_protected_face_digest']=baseline
    mat=head.data.materials[0].copy();mat.name='MF_protected_face_with_neck_detail'
    duplicate.data.materials[0]=mat;n,l=mat.node_tree.nodes,mat.node_tree.links
    p=next(node for node in n if node.type=='BSDF_PRINCIPLED');original=p.inputs['Base Color'].links[0].from_socket
    coordinates=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(coordinates.outputs['Object'],sep.inputs[0])
    u=n.new('ShaderNodeMath');u.operation='MULTIPLY_ADD';u.inputs[1].default_value=.238;u.inputs[2].default_value=.5;l.new(sep.outputs['X'],u.inputs[0])
    v=n.new('ShaderNodeMath');v.operation='MULTIPLY_ADD';v.inputs[1].default_value=.18;v.inputs[2].default_value=.646;l.new(sep.outputs['Z'],v.inputs[0])
    uv=n.new('ShaderNodeCombineXYZ');l.new(u.outputs[0],uv.inputs[0]);l.new(v.outputs[0],uv.inputs[1])
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(REF));tex.image.pack();l.new(uv.outputs[0],tex.inputs[0])
    rgb=n.new('ShaderNodeSeparateColor');l.new(tex.outputs[0],rgb.inputs[0]);red=n.new('ShaderNodeMath');red.operation='GREATER_THAN';l.new(rgb.outputs['Red'],red.inputs[0]);l.new(rgb.outputs['Green'],red.inputs[1])
    attr=duplicate.data.attributes.new('MF_authorized_neck_only','FLOAT','POINT')
    for vertex in duplicate.data.vertices:attr.data[vertex.index].value=neck_weight(vertex.co.z)
    weight=n.new('ShaderNodeAttribute');weight.attribute_name=attr.name
    gate=n.new('ShaderNodeMath');gate.operation='MULTIPLY';l.new(weight.outputs['Fac'],gate.inputs[0]);l.new(red.outputs[0],gate.inputs[1])
    plane=n.new('ShaderNodeMath');plane.operation='LESS_THAN';plane.inputs[1].default_value=-.86;l.new(sep.outputs['Z'],plane.inputs[0])
    bounded=n.new('ShaderNodeMath');bounded.operation='MULTIPLY';l.new(gate.outputs[0],bounded.inputs[0]);l.new(plane.outputs[0],bounded.inputs[1])
    mix=n.new('ShaderNodeMixRGB');l.new(bounded.outputs[0],mix.inputs[0]);l.new(original,mix.inputs[1]);l.new(tex.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
    # New chest surface stays inside the garment instead of a flat rectangle
    # crossing its neckline. Collarbones are shallow actual surface relief.
    mat=skin_material(variant);verts=[];faces=[];nu,nv=96,48
    sections=[(-1.22,.60,.61),(-1.45,.68,.63),(-1.65,1.02,.65),(-1.90,1.53,.69),(-2.25,1.70,.73)]
    for j in range(nv+1):
        z=-1.22-1.03*j/nv
        for a,b in zip(sections,sections[1:]):
            if b[0]<=z<=a[0]:
                t=smooth((a[0]-z)/(a[0]-b[0]));rx=a[1]*(1-t)+b[1]*t;ry=a[2]*(1-t)+b[2]*t;break
        else:rx,ry=sections[-1][1:]
        for i in range(nu):
            angle=2*math.pi*i/nu;x=rx*math.sin(angle);y=.22-ry*math.cos(angle)
            clavicle=-1.76+.15*abs(x)
            ridge=.045*math.exp(-((z-clavicle)/.09)**2)*smooth((abs(x)-.08)/.15)*max(0,math.cos(angle))
            verts.append((x,y-ridge,z))
    for j in range(nv):
        for i in range(nu):faces.append((j*nu+i,j*nu+(i+1)%nu,(j+1)*nu+(i+1)%nu,(j+1)*nu+i))
    ob=mesh_object('MF_clavicle_upper_chest',verts,faces,mat,2)
    weight=ob.data.attributes.new('MF_neck_overlay_weight','FLOAT','POINT')
    for vertex in ob.data.vertices:weight.data[vertex.index].value=smooth((-1.22-vertex.co.z)/.17)


def curve_object(name,points,mat,radius=.012):
    import bpy
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=radius;curve.bevel_resolution=2
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points):p.co=(*co,1)
    curve.materials.append(mat);ob=bpy.data.objects.new(name,curve);bpy.context.scene.collection.objects.link(ob)
    return ob


def make_garments(variant):
    import bpy
    from reference_dressing import mesh_object
    mat=cloth_material('MF_indigo_tunic',(.021,.054,.12) if variant>=12 else (.013,.036,.075),variant)
    nu,nv=96,72
    verts=[];faces=[]
    for i in range(nu):
        a=2*math.pi*i/nu
        # Rounded modest neckline, lower in front for the collarbone glimpse.
        top=-1.53-.50*max(0,math.cos(a))**2
        for j in range(nv+1):
            z=top+(-5.8-top)*j/nv;verts.append(torso_point(a,z))
    for i in range(nu):
        for j in range(nv):faces.append((i*(nv+1)+j,((i+1)%nu)*(nv+1)+j,((i+1)%nu)*(nv+1)+j+1,i*(nv+1)+j+1))
    tunic=mesh_object('MF_upper_tunic',verts,faces,mat,2)
    tunic.modifiers.new('Tunic fabric thickness','SOLIDIFY').thickness=.025
    for side in (-1,1):
        verts=[];faces=[];nz,ns=48,40
        for j in range(nz+1):
            t=j/nz;z=-1.95-3.65*t;cx=side*(1.57+.38*math.sin(t*1.4));cy=.22+.08*t
            width=.56-.13*t+.025*math.sin(t*17)
            cap=1
            if variant>=3:
                z=-1.65-3.95*t;cap=max(.008,smooth(t/.14));width*=cap
            for k in range(ns):
                a=k*2*math.pi/ns;fold=(.070 if variant>=12 else .035)*math.sin(a*9+t*5)+.025*math.sin(t*24+a*2)
                verts.append((cx+(width+fold*cap)*math.sin(a),cy+(.65-.13*t+fold)*cap*math.cos(a),z+.10*cap*math.cos(a)))
        for j in range(nz):
            for k in range(ns):faces.append((j*ns+k,j*ns+(k+1)%ns,(j+1)*ns+(k+1)%ns,(j+1)*ns+k))
        sleeve=mesh_object('MF_loose_tunic_sleeve_'+str(side),verts,faces,mat,2)
        sleeve.modifiers.new('Sleeve cloth thickness','SOLIDIFY').thickness=.02
    return tunic


def tailor_wrap(variant):
    import bpy
    wrap=bpy.data.objects['MF_diagonal_donor_wrap']
    for vertex in wrap.data.vertices:
        x,y,z=vertex.co
        lower=smooth((-1.8-z)/1.5)
        vertex.co.x*=.94
        vertex.co.y=y*.77-.10
        vertex.co.z-=.75*lower
        if variant>=2:
            vertex.co.z-=.25*smooth((abs(x)-1.5)/.85)
        if variant>=7:
            # Continue the diagonal drape toward the waist rather than ending
            # it as a short rectangular chest bib.
            vertex.co.z-=(.35 if variant>=8 else .90)*lower
    # Darker indigo avoids the washed blue-grey of the initial fit preview.
    mat=wrap.data.materials[0];n,l=mat.node_tree.nodes,mat.node_tree.links
    p=n.get('Principled BSDF');source=p.inputs['Base Color'].links[0].from_socket
    multiply=n.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1
    multiply.inputs[2].default_value=(.64,.72,.85,1);l.new(source,multiply.inputs[1]);l.new(multiply.outputs[0],p.inputs['Base Color'])
    if variant>=8:
        for node in n:
            if node.type=='MATH' and node.operation=='MULTIPLY_ADD':
                if abs(node.inputs[1].default_value-.156)<.0001 and abs(node.inputs[2].default_value-.677)<.0001:
                    node.inputs[1].default_value=.115;node.inputs[2].default_value=.70
                if abs(node.inputs[1].default_value-.15)<.0001 and abs(node.inputs[2].default_value-.61)<.0001:
                    node.inputs[1].default_value=.105;node.inputs[2].default_value=.65
    # The hood shares this material, retaining a single illustrated cloth family.
    if variant>=2:
        hood=bpy.data.objects['MF_adapted_donor_hood']
        for vertex in hood.data.vertices:
            if vertex.co.z<-.70:vertex.co.z=-.70+(vertex.co.z+.70)*2.05
            if vertex.co.y>.80:vertex.co.y=.80+(vertex.co.y-.80)*.75


def make_reference_shawl(variant):
    import bpy
    from reference_dressing import mesh_object
    donor=bpy.data.objects['MF_diagonal_donor_wrap'];donor.name='MF_retained_donor_wrap_hidden';donor.hide_render=True
    mat=donor.data.materials[0].copy();mat.name='MF_shoulder_led_shawl_material'
    for node in mat.node_tree.nodes:
        if node.type=='MATH' and node.operation=='MULTIPLY_ADD':
            if abs(node.inputs[1].default_value-.115)<.0001 and abs(node.inputs[2].default_value-.70)<.0001:
                node.inputs[1].default_value=.105;node.inputs[2].default_value=.58
    nu,nv=80,56;verts=[];faces=[]
    for i in range(nu+1):
        angle=-1.9+3.8*i/nu
        top=-1.88+.28*math.sin(angle)+.07*abs(math.sin(angle))
        if variant>=14:top+=.38*math.exp(-((angle+.55)/.27)**2)
        for j in range(nv+1):
            t=j/nv;z=top-3.35*t
            radius=2.05-.48*t
            phase=t*15+angle*2+.9*math.sin(angle*1.3+t*4)
            amplitude=(.065+.055*math.sin(angle*2+t*6)**2)*math.sin(math.pi*(.06+.91*t))
            fold=amplitude*math.sin(phase)+.024*math.sin(phase*2.1+.8)
            x=(radius+fold)*math.sin(angle)
            y=.18-(.85+.24*math.sin(math.pi*t)+fold)*math.cos(angle)
            verts.append((x,y,z+.045*math.sin(phase+1)*math.sin(math.pi*t)))
    for i in range(nu):
        for j in range(nv):faces.append((i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1))
    obj=mesh_object('MF_diagonal_donor_wrap',verts,faces,mat,0)
    group=obj.vertex_groups.new(name='MF_shawl_shoulder_anchors')
    for i in range(nu+1):
        angle=-1.9+3.8*i/nu
        # Keep the top silhouette supported; cloth below relaxes against body.
        group.add([i*(nv+1)],1.0,'REPLACE')
        if i in (0,nu):group.add([i*(nv+1)+j for j in range(8)],1.0,'REPLACE')
    for name in ('MF_upper_tunic','MF_loose_tunic_sleeve_-1','MF_loose_tunic_sleeve_1'):
        body=bpy.data.objects[name];body.modifiers.new('Static shawl support','COLLISION')
    cloth=obj.modifiers.new('Settle supported shawl','CLOTH');cloth.settings.quality=6
    cloth.settings.mass=.18;cloth.settings.vertex_group_mass=group.name
    cloth.settings.tension_stiffness=25;cloth.settings.compression_stiffness=25;cloth.settings.shear_stiffness=15;cloth.settings.bending_stiffness=.35
    cloth.collision_settings.use_self_collision=True;cloth.collision_settings.self_distance_min=.012;cloth.collision_settings.distance_min=.018
    cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=18
    scene=bpy.context.scene;scene.gravity=(0,0,-.8)
    if variant<10:
        for frame in range(1,19):scene.frame_set(frame)
        bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=cloth.name);scene.frame_set(1)
    else:
        # The settling experiment starts too close to the sleeves and drives
        # parts inside them. Keep the composed pattern; enforce visible support.
        obj.modifiers.remove(cloth)
        from mathutils import Vector
        from mathutils.bvhtree import BVHTree
        bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
        trees=[BVHTree.FromObject(bpy.data.objects[name],dg) for name in ('MF_upper_tunic','MF_loose_tunic_sleeve_-1','MF_loose_tunic_sleeve_1')]
        for vertex in obj.data.vertices:
            x,y,z=vertex.co
            hits=[tree.ray_cast(Vector((x,-6,z)),Vector((0,1,0)),10)[0] for tree in trees]
            ys=[hit.y for hit in hits if hit is not None]
            if ys and y<.3:vertex.co.y=min(y,min(ys)-.07)
    obj.modifiers.new('Continuous cloth surface','SUBSURF').levels=2
    obj.modifiers.new('Shawl thin hem','SOLIDIFY').thickness=.014
    if variant>=11:
        # Preserve the donor's useful upper fold vocabulary; the new lower
        # panel supplies continuous coverage and avoids the former short bib.
        import bmesh
        upper=donor.copy();upper.data=donor.data.copy();upper.name='MF_layered_upper_scarf'
        bpy.context.scene.collection.objects.link(upper);upper.hide_render=False
        bm=bmesh.new();bm.from_mesh(upper.data)
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,-2.95),plane_no=(-.22,0,1),clear_inner=True,dist=.000001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(upper.data);bm.free()
        upper.location.z=-.08


def bridge_hair(variant):
    import bpy,random
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    head=bpy.data.objects['FBHead'];bpy.context.view_layer.update()
    tree=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get())
    mats=[m for m in bpy.data.materials if m.name.startswith('MF_warm_chestnut_fiber')][:4]
    rng=random.Random(301)
    if variant>=8:
        # The nearest-surface guide experiment made sharp temple spikes. Retain
        # the original swept groom and fill its coverage gaps from underneath.
        cap=bpy.data.objects['MF_separate_side_back_hair_base'];cap.hide_render=False
        if variant>=14:cap.hide_render=True
        p=cap.data.materials[0].node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.007,.0025,.001,1)
        for source in list(bpy.context.scene.objects):
            if source.type!='CURVE' or not source.name.startswith('MF_swept_scalp_fibers'):continue
            for sign in (-1,1):
                obj=source.copy();obj.data=source.data.copy();obj.name='MF_swept_groom_fill';bpy.context.scene.collection.objects.link(obj)
                for spline in obj.data.splines:
                    for j,point in enumerate(spline.points):
                        x,y,z,w=point.co;angle=.015*sign*math.sin(math.pi*j/(len(spline.points)-1))
                        point.co=(x*math.cos(angle)-(y-.23)*math.sin(angle),.23+x*math.sin(angle)+(y-.23)*math.cos(angle),z+.003*sign*math.sin(j*.3),w)
        return
    for side in (-1,1):
        for i in range(90):
            f=i/89;points=[]
            for j in range(49):
                t=j/48;x=side*(.63+.39*t+.10*f);y=-.55+.84*t+.04*f;z=.68-.95*t-.15*f
                point=Vector((x,y,z));hit,normal,_,_=tree.find_nearest(point)
                if t<.65 and hit is not None:point=hit+normal*(.009+.018*math.sin(t*math.pi))
                point.x+=side*.018*math.sin(t*9+f*4)*math.sin(math.pi*t)
                point.z+=.008*math.sin(t*18+f*9)
                points.append(tuple(point))
            ob=curve_object('MF_temple_hair_transition',points,mats[rng.randrange(len(mats))],.0023)
            for j,p in enumerate(ob.data.splines[0].points):p.radius=max(.01,math.sin(math.pi*j/48)**.5)


def make_straps(variant):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from reference_dressing import mesh_object
    leather=cloth_material('MF_worn_brown_leather',(.17,.071,.029),variant)
    leather.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.63
    stitch=cloth_material('MF_leather_edge_stitch',(.30,.17,.08),variant)
    brass=bpy.data.materials.new('MF_muted_brass_buckle');brass.use_nodes=True
    p=brass.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.24,.16,.068,1);p.inputs['Metallic'].default_value=.72;p.inputs['Roughness'].default_value=.48
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    names=('MF_upper_tunic',) if variant>=2 else ('MF_upper_tunic','MF_diagonal_donor_wrap')
    trees=[BVHTree.FromObject(bpy.data.objects[name],dg) for name in names]
    wrap_tree=BVHTree.FromObject(bpy.data.objects['MF_diagonal_donor_wrap'],dg)
    for side in (-1,1):
        active_trees=trees
        if variant>=3 and side==1:
            active_trees=trees+[wrap_tree]
        if variant>=11:active_trees=trees+[wrap_tree]
        points=[];count=100
        for j in range(count+1):
            t=j/count;x=side*(1.70-2.95*t);z=-2.13-3.37*t
            if variant>=2:x=side*(1.70-3.40*t);z=-2.13-4.17*t
            hits=[tree.ray_cast(Vector((x,-6,z)),Vector((0,1,0)),10)[0] for tree in active_trees]
            if variant>=8:
                across=Vector((-4.17,0,side*3.40)).normalized()
                for offset in (-.18,.18):
                    edge=Vector((x,-6,z))+across*offset
                    hits.extend(tree.ray_cast(edge,Vector((0,1,0)),10)[0] for tree in active_trees)
            ys=[h.y for h in hits if h is not None];y=min(ys) if ys else -.60
            if 6<=variant<8 and side==1 and t<.18:
                under=trees[0].ray_cast(Vector((x,-6,z)),Vector((0,1,0)),10)[0]
                if under is not None:
                    outside=smooth((t-.05)/.13);y=under.y*(1-outside)+y*outside
            if variant==7 and side==-1 and z<-3.80:
                outer=wrap_tree.ray_cast(Vector((x,-6,z)),Vector((0,1,0)),10)[0]
                if outer is not None:
                    outside=smooth((-3.80-z)/.40);y=y*(1-outside)+min(y,outer.y)*outside
            points.append(Vector((x,y-.055-(.035 if side==1 else 0),z)))
        if variant>=8:
            # Leather spans recesses instead of tracing every deep cloth fold.
            original=[p.y for p in points]
            for j,p in enumerate(points):p.y=min(original[max(0,j-5):min(count+1,j+6)])-.015
            for _ in range(15):
                original=[p.y for p in points]
                for j in range(1,count):points[j].y=(original[j-1]+2*original[j]+original[j+1])/4
        # Smooth high-frequency drape relief; keep strap just outside its support.
        for _ in range(3):
            original=[p.copy() for p in points]
            for j in range(1,count):points[j].y=min(original[j].y,(original[j-1].y+2*original[j].y+original[j+1].y)/4)
        added=0
        if variant>=9:
            start=points[0].copy();cap=[]
            for j in range(16):
                t=j/16
                cap.append(Vector((start.x,.85*(1-t)+start.y*t,start.z+.38*math.sin(math.pi*t))))
            points=cap+points;count+=16;added=16
        verts=[];faces=[];edges=[[],[]]
        for j,point in enumerate(points):
            tangent=(points[min(count,j+1)]-points[max(0,j-1)]).normalized()
            across=Vector((tangent.z,0,-tangent.x)).normalized()
            for k in range(5):verts.append(tuple(point+across*((k/4-.5)*.31)))
            for k,sign in enumerate((-1,1)):edges[k].append(tuple(point+across*(sign*.128)+Vector((0,-.008,0))))
        for j in range(count):
            for k in range(4):faces.append((j*5+k,j*5+k+1,(j+1)*5+k+1,(j+1)*5+k))
        strap=mesh_object('MF_crossed_leather_strap_'+str(side),verts,faces,leather,1)
        strap.modifiers.new('Leather thickness','SOLIDIFY').thickness=.035
        bevel=strap.modifiers.new('Rounded leather edges','BEVEL');bevel.width=.014;bevel.segments=3
        for edge in edges:
            for j in range(0,len(edge)-2,3):curve_object('MF_saddle_stitch',edge[j:j+2],stitch,.006)
        if side==1:
            idx=(38 if variant>=7 else 46)+added;center=points[idx]+Vector((0,-.045,0));along=(points[idx+1]-points[idx-1]).normalized();across=Vector((along.z,0,-along.x)).normalized()
            corners=[(-.19,-.24),(.19,-.24),(.19,.24),(-.19,.24),(-.19,-.24)]
            curve_object('MF_buckle_frame',[tuple(center+across*u+along*v) for u,v in corners],brass,.025)
            curve_object('MF_buckle_tongue',[tuple(center+across*u) for u in (-.18,.10)],brass,.018)


def run(job):
    out=validate(job)
    import bpy
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from likeness_cleanup import geometry_digest
    from hijab_donor import material_signature,bounds,review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    head=bpy.data.objects['FBHead'];before=geometry_digest(head)
    material_before=material_signature(head.data.materials[0])
    shapes={k.name:k.value for k in head.data.shape_keys.key_blocks}
    out.mkdir()
    if job['operation']=='audit':
        data={'objects':[{ 'name':o.name,'type':o.type,'bounds':bounds(o) if o.type=='MESH' else None,
                         'hidden':o.hide_render} for o in bpy.context.scene.objects if o.type in ('MESH','CURVE')],
              'neck_rings':[]}
        for level in (-.8,-.9,-1.,-1.2,-1.4,-1.6):
            points=[v.co for v in head.data.vertices if abs(v.co.z-level)<.06]
            data['neck_rings'].append({'z':level,'count':len(points),
                'bounds':[[min(p[c] for p in points) for c in range(3)],[max(p[c] for p in points) for c in range(3)]] if points else None})
        (out/'audit.json').write_text(json.dumps(data,indent=2))
    elif job['operation']=='build':
        build(job['variant'])
        review(bpy.context.scene,out,(0,-.1,-1.8),7.6,[('front',0),('left',-45),('right',45)])
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'upperbody.blend'))
    else:
        folder=BASE/f'upperbody-{"package" if job["operation"]=="verify_package" else "build"}-{job["variant"]:02}'
        record=json.loads((folder/'result.json').read_text())
        native=folder/('character-upperbody.blend' if job['operation']=='verify_package' else 'upperbody.blend')
        if hashlib.sha256(native.read_bytes()).hexdigest()!=record['native_sha256']:
            raise ValueError('Saved candidate changed')
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        if job['operation']=='portraits':
            review(bpy.context.scene,out,(0,-.1,-1.8),7.6,[('front',0),('left',-45),('right',45)],portrait=True)
        if job['operation']=='detail':
            review(bpy.context.scene,out,(0,-.1,-.48),4.6,[('front',0),('left',-45),('right',45)],portrait=True)
        if job['operation']=='diagnostic':
            review(bpy.context.scene,out,(0,-.1,-.60),4.8,[('front',0),('right',45)],portrait=True)
        if job['operation']=='shoulders':
            review(bpy.context.scene,out,(0,-.1,-1.8),7.6,[('side',90),('rear',135)])
        if job['operation']=='clay':
            for obj in bpy.context.scene.objects:
                if obj.type in ('MESH','CURVE'):obj.hide_render=obj.name!='MF_continuous_head_neck'
            obj=bpy.data.objects['MF_continuous_head_neck'];mat=bpy.data.materials.new('MF_diagnostic_clay');mat.use_nodes=True
            mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.35,.35,.35,1)
            mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
            obj.data.materials.clear();obj.data.materials.append(mat)
            review(bpy.context.scene,out,(0,-.1,-.55),4.8,[('front',0),('left',-45)])
        if job['operation']=='contacts':
            colors={'MF_continuous_head_neck':(.6,.35,.18,1),'MF_upper_tunic':(.9,.7,.01,1),
                    'MF_layered_upper_scarf':(.8,.03,.02,1),'MF_diagonal_donor_wrap':(.02,.5,.06,1)}
            for obj in bpy.context.scene.objects:
                if obj.hide_render or obj.type not in ('MESH','CURVE'):continue
                mat=bpy.data.materials.new('MF_contact_ID_'+obj.name);mat.use_nodes=True
                n,l=mat.node_tree.nodes,mat.node_tree.links;em=n.new('ShaderNodeEmission')
                em.inputs['Color'].default_value=colors.get(obj.name,(.025,.025,.08,1))
                l.new(em.outputs[0],n.get('Material Output').inputs['Surface'])
                obj.data.materials.clear();obj.data.materials.append(mat)
            review(bpy.context.scene,out,(0,-.1,-.60),4.8,[('front',0)])
        if job['operation']=='facecheck':
            facecheck(out)
        if job['operation']=='package':
            for obj in bpy.context.scene.objects:
                obj.select_set(False)
                if obj.type in ('MESH','CURVE'):obj.hide_set(obj.hide_render)
            visible=bpy.data.objects['MF_continuous_head_neck'];visible.hide_set(False);visible.select_set(True)
            bpy.context.view_layer.objects.active=visible
            for screen in bpy.data.screens:
                for area in screen.areas:
                    if area.type=='VIEW_3D':
                        area.spaces.active.region_3d.view_perspective='CAMERA'
                        area.spaces.active.shading.type='MATERIAL'
                        area.spaces.active.overlay.show_overlays=False
            bpy.context.scene['MF_review_status']='YELLOW static candidate; Director review pending; not rigged/animated'
            bpy.ops.wm.save_as_mainfile(filepath=str(out/'character-upperbody.blend'))
    head=bpy.data.objects['FBHead']
    assert geometry_digest(head)==before
    assert material_signature(head.data.materials[0])==material_before
    assert {k.name:k.value for k in head.data.shape_keys.key_blocks}==shapes
    if 'MF_display_head_neck' in bpy.data.objects:
        duplicate=bpy.data.objects['MF_display_head_neck']
        assert protected_face_digest(duplicate)==protected_face_digest(head)
        assert all(abs(a.value-neck_weight(v.co.z))<1e-6 for a,v in zip(duplicate.data.attributes['MF_authorized_neck_only'].data,duplicate.data.vertices))
    if 'MF_continuous_head_neck' in bpy.data.objects:
        assert protected_surface_digest(bpy.data.objects['MF_continuous_head_neck'])==protected_surface_digest(head)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    result={'source_sha256':SOURCE_SHA,'reference_sha256':REF_SHA,'operation':job['operation'],
            'variant':job['variant'],'face_geometry_digest':before,'face_material_signature':material_before,
            'shape_values':shapes,'protected_neck_top_z':-.86,'director_accepted':False,
            'scope':'Static upper-body reference fit; no animation or all-angle qualification.'}
    result['attribution']='Adapted hood and upper folds: Hijab by lam_m_zack, CC BY 4.0, https://sketchfab.com/3d-models/hijab-ee50e01adc864ccc880caed9b5eb3bcb. New lower shawl, tunic/sleeves, straps/buckle and neck extension authored locally; approved project illustrations reused as material references.'
    if job['variant']>=21:
        result['attribution']='Adapted hood: Hijab by lam_m_zack, CC BY 4.0, https://sketchfab.com/3d-models/hijab-ee50e01adc864ccc880caed9b5eb3bcb. Visible cowl/diagonal shawl, tunic/sleeves, harness/buckle, hair geometry and neck extension authored locally; approved project illustrations reused as material references. Hidden earlier donor objects remain retained: internal working scene, not a cleaned redistribution bundle.'
    if job['variant']>=16:
        result['verification_handler_sha256']={name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest() for name in ('upperbody_refinement.py','costume_refinement.py','reference_dressing.py','hijab_donor.py','likeness_cleanup.py')}
        result['visible_harness_objects']=[o.name for o in bpy.context.scene.objects if o.name.startswith('MF_reference_shoulder_harness') and not o.hide_render]
    if 'MF_display_head_neck' in bpy.data.objects:result['visible_protected_face_digest']=protected_face_digest(bpy.data.objects['MF_display_head_neck'])
    if 'MF_continuous_head_neck' in bpy.data.objects:result['visible_protected_surface_digest']=protected_surface_digest(bpy.data.objects['MF_continuous_head_neck'])
    if job['operation']=='build':result['native_sha256']=hashlib.sha256((out/'upperbody.blend').read_bytes()).hexdigest()
    elif job['operation']=='package':
        result['native_sha256']=hashlib.sha256((out/'character-upperbody.blend').read_bytes()).hexdigest()
        result['build_native_sha256']=record['native_sha256']
    elif job['operation'] in ('verify','portraits','detail','facecheck','verify_package','diagnostic','shoulders','clay','contacts'):result['verified_native_sha256']=record['native_sha256']
    if job['operation'] in ('package','verify_package'):
        result['file_images']=[{'name':im.name,'packed':bool(im.packed_file or im.packed_files)} for im in bpy.data.images if im.source=='FILE']
        assert all(item['packed'] for item in result['file_images'])
        assert bpy.data.objects['FBHead'].hide_get() and not bpy.data.objects['MF_continuous_head_neck'].hide_get()
    (out/'result.json').write_text(json.dumps(result,indent=2))


def build(variant):
    import bpy
    bpy.data.objects['MF_clothed_bust_support'].hide_render=True
    make_neck(variant);make_garments(variant);tailor_wrap(variant)
    if variant>=9:make_reference_shawl(variant)
    bridge_hair(variant);make_straps(variant)
    if variant>=16:
        from costume_refinement import refine
        refine(variant)
    bpy.context.scene.cycles.transparent_max_bounces=32


def facecheck(out):
    import bpy
    from hijab_donor import review
    for obj in bpy.context.scene.objects:
        if obj.type in ('MESH','CURVE'):obj.hide_render=True
    for label,name in (('original','FBHead'),('derivative','MF_continuous_head_neck')):
        obj=bpy.data.objects[name];old=obj.data.materials[0];mat=old.copy();obj.data.materials[0]=mat
        n,l=mat.node_tree.nodes,mat.node_tree.links;p=next(node for node in n if node.type=='BSDF_PRINCIPLED')
        color=p.inputs['Base Color'].links[0].from_socket
        emission=n.new('ShaderNodeEmission');l.new(color,emission.inputs['Color'])
        output=next(node for node in n if node.type=='OUTPUT_MATERIAL');l.new(emission.outputs[0],output.inputs['Surface'])
        obj.hide_render=False;folder=out/label;folder.mkdir()
        review(bpy.context.scene,folder,(0,-.1,0),3.5,[('front',0),('left',-45),('right',45)])
        obj.hide_render=True;obj.data.materials[0]=old


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
