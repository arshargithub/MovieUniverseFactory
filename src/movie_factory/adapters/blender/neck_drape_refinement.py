"""Fixed native neck-continuity diagnostics and reference drape repairs.

Invoked only by the validated upperbody operation. No runtime code or paths.
"""
import json
import math


def monotone_hermite(a,b,da,db,t,length):
    """C1 radial bridge with limited end slopes: no artificial overshoot ring."""
    slope=(b-a)/length
    if abs(slope)<1e-10:return a
    alpha=max(0.,da/slope);beta=max(0.,db/slope)
    norm=math.hypot(alpha,beta)
    if norm>3:alpha*=3/norm;beta*=3/norm
    ma=alpha*slope*length;mb=beta*slope*length
    return (2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*ma+(-2*t**3+3*t*t)*b+(t**3-t*t)*mb


def repair_neck_geometry():
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    obj=bpy.data.objects['MF_continuous_head_neck'];bpy.context.view_layer.update()
    tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
    top,bottom=-.86,-1.45
    def radius(angle,z):
        d=Vector((math.sin(angle),math.cos(angle),0));c=Vector((0,.10,z))
        hit,_,_,_=tree.ray_cast(c+d*3,-d,5)
        if hit is None:raise ValueError('Neck cross-section ray missed')
        return (hit-c).dot(d)
    # Snapshot the support before editing any vertex. Query cost is bounded.
    table=[];count=512
    for i in range(count):
        a=2*math.pi*i/count;r0=radius(a,top);r1=radius(a,bottom)
        table.append((r0,r1,(r0-radius(a,top+.03))/.03,(radius(a,bottom-.03)-r1)/.03))
    for vertex in obj.data.vertices:
        x,y,z=vertex.co
        if not bottom<z<top:continue
        angle=math.atan2(x,y-.10)%(2*math.pi);f=angle/(2*math.pi)*count;i=int(f);w=f-i
        values=[table[i][k]*(1-w)+table[(i+1)%count][k]*w for k in range(4)]
        r=monotone_hermite(*values,(top-z)/(top-bottom),top-bottom)
        vertex.co.x=r*math.sin(angle);vertex.co.y=.10+r*math.cos(angle)
    obj.data.update();bpy.context.view_layer.update()


def boundary_skin_texture(head):
    """Bake a narrow accepted-neck color band; source head remains untouched."""
    import bpy
    from mathutils import Vector
    clone=head.copy();clone.data=head.data.copy();clone.name='MF_temporary_neck_band_source'
    bpy.context.scene.collection.objects.link(clone);clone.hide_render=False;clone.hide_set(False)
    mat=head.data.materials[0].copy();clone.data.materials[0]=mat
    n,l=mat.node_tree.nodes,mat.node_tree.links;original_uv=clone.data.uv_layers.active.name
    old_uv=n.new('ShaderNodeUVMap');old_uv.uv_map=original_uv
    for link in list(l):
        if link.from_node.type=='TEX_COORD' and link.from_socket.name=='UV':l.new(old_uv.outputs['UV'],link.to_socket)
    for node in list(n):
        if node.type=='TEX_IMAGE' and not node.inputs['Vector'].is_linked:l.new(old_uv.outputs['UV'],node.inputs['Vector'])
    uv=clone.data.uv_layers.new(name='MF_neck_band_bake_uv')
    for polygon in clone.data.polygons:
        values=[]
        for li in polygon.loop_indices:
            co=clone.data.vertices[clone.data.loops[li].vertex_index].co
            values.append((li,(math.atan2(co.x,co.y-.10)%(2*math.pi))/(2*math.pi),(co.z+.95)/.45))
        crosses=max(v[1] for v in values)-min(v[1] for v in values)>.5
        for li,u,v in values:uv.data[li].uv=(u+1 if crosses and u<.5 else u,v)
    clone.data.uv_layers.active=uv;uv.active_render=True
    atlas=bpy.data.images.new('MF_accepted_neck_boundary_color',width=1024,height=256,alpha=False)
    tex=n.new('ShaderNodeTexImage');tex.image=atlas;n.active=tex;tex.select=True
    shader=n.get('Principled BSDF');em=n.new('ShaderNodeEmission')
    l.new(shader.inputs['Base Color'].links[0].from_socket,em.inputs['Color']);l.new(em.outputs[0],n.get('Material Output').inputs['Surface'])
    for obj in bpy.context.scene.objects:obj.select_set(False)
    clone.select_set(True);bpy.context.view_layer.objects.active=clone
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8
    scene.render.bake.use_selected_to_active=False;scene.render.bake.use_clear=True;scene.render.bake.margin=4
    bpy.ops.object.bake(type='EMIT');atlas.pack()
    bpy.data.objects.remove(clone,do_unlink=True)
    return atlas


def veil_target(angle,t,origin,variant=34):
    """Soft widening to shoulders, then gathered fall; no stacked curtains."""
    x,y,z=origin
    blend=t*t*(3-2*t)
    width=1.40+.62*math.sin(math.pi*t*.78)
    depth=.95+.17*math.sin(math.pi*t)
    fold=(.045+.050*t)*math.sin(angle*9+.8*t)+.025*math.sin(angle*15-1.3*t)
    if variant>=35:fold=(.03+.16*t)*math.sin(angle*7+1.5*t)+.05*t*math.sin(angle*11-.8*t)
    target_x=(width+fold)*math.sin(angle)
    target_y=.22+(depth+fold)*math.cos(angle)
    target_z=-4.65+.23*math.cos(angle*2)+.09*math.sin(angle*5)
    return (x*(1-blend)+target_x*blend,y*(1-blend)+target_y*blend,z*(1-t)+target_z*t)


def rebuild_lower_veil(variant=34):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    obj=bpy.data.objects['MF_adapted_donor_hood'];bm=bmesh.new();bm.from_mesh(obj.data)
    # Retain the original crown and facial framing, replace only the poorly
    # extended lower donor. A single connected extension avoids stacked tiers.
    cut=-.30
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,cut),plane_no=(0,0,1),clear_inner=True,dist=.000001)
    edges=[e for e in bm.edges if e.is_boundary and all(abs(v.co.z-cut)<.0001 for v in e.verts)]
    if len(edges)<8:raise ValueError('Unexpected lower hood boundary')
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    supports=[BVHTree.FromObject(bpy.data.objects[name],dg) for name in ('MF_upper_tunic','MF_loose_tunic_sleeve_-1','MF_loose_tunic_sleeve_1','MF_continuous_head_neck')]
    rows={v:[v] for e in edges for v in e.verts};steps=64
    for v,row in rows.items():
        origin=tuple(v.co);angle=math.atan2(origin[0],origin[1]-.22)
        for j in range(1,steps+1):
            t=j/steps;x,y,z=veil_target(angle,t,origin,variant)
            d=Vector((math.sin(angle),math.cos(angle),0));center=Vector((0,.22,z))
            hits=[tree.ray_cast(center+d*4,-d,6)[0] for tree in supports]
            radii=[(hit-center).dot(d) for hit in hits if hit is not None]
            radial=(Vector((x,y,z))-center).dot(d)
            if radii and radial<max(radii)+.07:
                point=center+d*(max(radii)+.07);x,y=point.x,point.y
            row.append(bm.verts.new((x,y,z)))
    for e in edges:
        a,b=e.verts
        for j in range(steps):bm.faces.new((rows[a][j],rows[b][j],rows[b][j+1],rows[a][j+1]))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    for polygon in obj.data.polygons:polygon.use_smooth=True
    obj.data.update()


def audit_neck(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from hijab_donor import review
    obj=bpy.data.objects['MF_continuous_head_neck']
    tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
    sections=[]
    for i in range(81):
        z=-.60-i*.015;row={'z':z,'radii':{}}
        for degrees in (0,45,90,135,180,225,270,315):
            a=math.radians(degrees);d=Vector((math.sin(a),-math.cos(a),0));center=Vector((0,.10,z))
            hit,normal,_,distance=tree.ray_cast(center+d*3,-d,5)
            row['radii'][str(degrees)]=(hit-center).dot(d) if hit is not None else None
        sections.append(row)
    data={'has_custom_normals':obj.data.has_custom_normals,'vertices':len(obj.data.vertices),
          'modifiers':[(m.name,m.type) for m in obj.modifiers],
          'attributes':[(a.name,a.domain,a.data_type) for a in obj.data.attributes],
          'sections':sections}
    (out/'neck-sections.json').write_text(json.dumps(data,indent=2))
    for item in bpy.context.scene.objects:
        if item.type in ('MESH','CURVE'):item.hide_render=item!=obj
    old=obj.data.materials[0];mat=old.copy();obj.data.materials[0]=mat
    n,l=mat.node_tree.nodes,mat.node_tree.links;p=n.get('Principled BSDF')
    em=n.new('ShaderNodeEmission');l.new(p.inputs['Base Color'].links[0].from_socket,em.inputs['Color'])
    l.new(em.outputs[0],n.get('Material Output').inputs['Surface'])
    review(bpy.context.scene,out,(0,-.1,-.55),4.8,[('front',0),('left',-45),('right',45)])
    obj.data.materials[0]=old
