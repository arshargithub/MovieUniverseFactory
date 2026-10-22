"""First supporting-cast form candidate, from existing local scene assets only.

Fixed trusted construction; not recipe code, cloth simulation or art approval.
Preserve animated owners and every garment cache. Prove two actors before spread.
"""
import math


def drape_module():
    # Worker imports handlers by fixed file location, without a package context.
    import importlib.util
    from pathlib import Path
    spec=importlib.util.spec_from_file_location('mf_nihang_drape',Path(__file__).with_name('nihang_drape.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def garment_module():
    import importlib.util
    from pathlib import Path
    spec=importlib.util.spec_from_file_location('mf_nihang_garment',Path(__file__).with_name('nihang_garment.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def mesh(bpy,name,points,faces,material,parent,weld=False):
    data=bpy.data.meshes.new(name);data.from_pydata(points,[],faces);data.update()
    if weld:
        import bmesh
        bm=bmesh.new();bm.from_mesh(data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(data);bm.free();data.update()
    for p in data.polygons:p.use_smooth=True
    obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj)
    obj.parent=parent;data.materials.append(material)
    return obj


def grid(rows,cols):
    return [(j*cols+k,j*cols+k+1,(j+1)*cols+k+1,(j+1)*cols+k) for j in range(rows-1) for k in range(cols-1)]


def garment_envelope(u):
    """Nonnegative waist-to-shoulder support, including float32 endpoints."""
    import numpy as np
    values=np.asarray(u)
    if not np.isfinite(values).all():raise ValueError('ENVELOPE_NONFINITE')
    clipped=np.clip(values,0,1)
    wave=np.maximum(0,np.sin(math.pi*clipped))
    return np.where((clipped>0)&(clipped<1),wave**.7,0)


def crown_point(angle,z,height,width,offset=0):
    """Rounded supported crown; distinct cloth courses provide the layering."""
    u=max(0,min(1,(z-.042)/height))
    knots=((0,1),(.18,1.11),(.43,1.02),(.67,.87),(.87,.60),(1,.09))
    j=next((i for i in range(len(knots)-1) if u<=knots[i+1][0]),len(knots)-2)
    a,ra=knots[j];b,rb=knots[j+1];t=(u-a)/(b-a);t=t*t*(3-2*t)
    radius=width*(ra+(rb-ra)*t)
    radius*=1+.023*math.sin(angle*3+.7+u*4)+.018*math.cos(angle*5-u*3)
    radius+=offset
    return (radius*math.sin(angle)+.009*u*u,
            .012-radius*(1.12-.12*u)*math.cos(angle)+.008*u*u,z)


def wrapped_crown(bpy,frame,material,leader):
    """Tapered supported crown and one continuous oblique cloth winding.

    This replaces the old cylindrical silhouette, not its coordinates with noise.
    """
    for obj in frame.children:
        if obj.name.startswith(('319 supported dumalla','319 overlapping tied cloth','319 restrained chakram')):
            obj.hide_render=True;obj.hide_viewport=True
    height=.270 if leader else .220
    width=.114 if leader else .108
    def point(angle,z,offset=0):
        return crown_point(angle,z,height,width,offset)
    points=[];rows=41;cols=97
    for j in range(rows):
        z=.045+height*j/(rows-1)
        for k in range(cols):points.append(point(math.tau*k/(cols-1),z))
    faces=grid(rows,cols);faces.append(tuple(range((rows-1)*cols,rows*cols)))
    core=mesh(bpy,'MF Nihang wrapped crown core',points,faces,material,frame,weld=True)
    cloth=[]
    # Overlapping broad courses, not a constant-pitch spiral. Each course has a
    # different crossing angle and local compression where another layer holds it.
    courses=((.075,.040,.2,.066),(.107,-.031,-.5,.070),
             (.143,.037,.8,.067),(.181,.029,1.7,.071),
             (.220,-.023,.1,.060),(.253,.017,1.2,.048))
    for index,(center,slant,phase,bandwidth) in enumerate(courses):
        rows=129;cols=17;points=[];scale=height/.270
        for j in range(rows):
            angle=math.tau*j/(rows-1)
            pinch=.55+.45*abs(math.sin(angle+phase))
            middle=.042+(center-.042)*scale+slant*scale*math.sin(angle+phase)
            for k in range(cols):
                u=k/(cols-1)
                z=middle+bandwidth*scale*(u-.5)*pinch
                broad=.0028*math.sin(math.pi*u)
                crease=.0015*math.sin(3*math.pi*u+.5*math.sin(angle*2+index))
                edge=.0007*math.exp(-((u-.94)/.08)**2)
                points.append(point(angle,z,.0015+index*.00045+broad+crease+edge))
        wrap=mesh(bpy,'MF Nihang overlapped cloth course',points,grid(rows,cols),material,frame,weld=True)
        solid=wrap.modifiers.new('Thin folded cloth edge','SOLIDIFY');solid.thickness=.0012
        cloth.append(wrap.name)
    # Deliberate compressed cloth pleats near the raised top, not a smooth lid.
    points=[];rows=17;cols=65
    for j in range(rows):
        u=j/(rows-1);z=.045+height-.045+.052*u
        for k in range(cols):
            a=math.tau*k/(cols-1)
            p=point(a,z,.0015*(1-u)*math.cos(a*9))
            shrink=1-.80*u
            points.append((p[0]*shrink,.012+(p[1]-.012)*shrink,z))
    top=mesh(bpy,'MF Nihang gathered crown cloth',points,grid(rows,cols),material,frame,weld=True)
    return [core.name,*cloth,top.name]


def garment_form(bpy,root,leader):
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    upper=next(o for o in root.children if o.name.startswith('320 articulated upper body'))
    shirt=next(o for o in upper.children if o.name.startswith('319 anatomically'))
    # Copy data including all existing relative shape keys; original master stays
    # untouched on disk and no motion owner is renamed or reparented.
    shirt,drape=garment_module().build(bpy,shirt,leader)
    shirt['mf_supporting_appearance']=True
    blocks=[k.data for k in shirt.data.shape_keys.key_blocks] if shirt.data.shape_keys else [shirt.data.vertices]
    for obj in upper.children:
        if obj.name.startswith('319 overlapping chola chest panel'):
            # Continuous shirt exists underneath; retain the separate narrow placket.
            obj.hide_render=True;obj.hide_viewport=True
        if obj.name.startswith('319 bound chola neckline'):
            obj.hide_render=True;obj.hide_viewport=True
    # Refit only actual existing outside-facing layers to this changed torso.
    bpy.context.view_layer.update()
    evaluated=shirt.evaluated_get(bpy.context.evaluated_depsgraph_get())
    tree=BVHTree.FromPolygons([v.co for v in evaluated.data.vertices],[tuple(p.vertices) for p in evaluated.data.polygons])
    facing=-1 if leader else 1;layers=[]
    for obj in upper.children:
        if not obj.name.startswith(('297 woven diagonal sash','319 overlapping chola chest panel','319 chola folded placket')):continue
        obj.data=obj.data.copy();obj['mf_supporting_appearance']=True
        for mod in obj.modifiers:
            if mod.type=='SHRINKWRAP':mod.target=shirt
        points=obj.data.vertices if obj.type=='MESH' else [p for sp in obj.data.splines for p in sp.points]
        hits=0
        for p in points:
            x,y,z=p.co[:3];hit=tree.ray_cast(Vector((x,facing*.8,z)),Vector((0,-facing,0)))[0]
            if hit is not None:
                p.co.y=hit.y+facing*(.013 if obj.name.startswith('297 woven') else .004);hits+=1
        if obj.name.startswith('297 woven') and hits<.95*len(points):raise ValueError('LOOK_INCOMPLETE_SASH_FIT')
        layers.append({'object':obj.name,'hits':hits,'points':len(points)})
    return {'shirt':shirt.name,'vertices':len(shirt.data.vertices),'cached_poses':len(blocks),'layers':layers,'drape':drape}


def beard_volume(frame):
    """Broaden hanging masses without shifting skin-rooted upper hairs."""
    changed=[]
    for obj in frame.children:
        if not obj.name.startswith('319 tapered beard fibers') or obj.type!='CURVE':continue
        obj.data=obj.data.copy()
        blocks=([key.data for key in obj.data.shape_keys.key_blocks] if obj.data.shape_keys
                else [spline.points for spline in obj.data.splines])
        for block in blocks:
            for point in block:
                x,y,z=point.co[:3]
                u=max(0,min(1,(-z-.075)/.14))
                weight=u*u*(3-2*u)
                point.co.x=x*(1+.24*weight)
                point.co.y=y+.018*weight
        changed.append(obj.name)
    return changed


def horse_finish(bpy):
    """Preserve dark authored UV coat; separate short coat from polished tack."""
    body=bpy.data.objects['horse'];mat=body.data.materials[0].copy()
    mat.name='MF Nihang dark short coat'
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    bs=nodes.get('Principled BSDF')
    for link in list(bs.inputs['Roughness'].links):links.remove(link)
    bs.inputs['Roughness'].default_value=.73
    bs.inputs['Specular IOR Level'].default_value=.18
    bs.inputs['Sheen Weight'].default_value=.23
    for node in nodes:
        if node.bl_idname=='ShaderNodeValToRGB':
            node.color_ramp.elements[0].color=(.027,.014,.009,1)
            node.color_ramp.elements[-1].color=(.125,.063,.034,1)
        if node.bl_idname=='ShaderNodeBump':
            node.inputs['Strength'].default_value=.19
            node.inputs['Distance'].default_value=.00035
    body.data.materials[0]=mat
    return {'material':mat.name,'scope':'Existing dark UV source and rig retained; no shape, light or motion change.'}


def saddle_pad(bpy):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    old=bpy.data.objects['fitted saddle blanket292'];parent=old.parent
    body=bpy.data.objects['horse'];evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    tree=BVHTree.FromPolygons([body.matrix_world@v.co for v in evaluated.data.vertices],
                             [tuple(p.vertices) for p in evaluated.data.polygons])
    old_points=[v.co.copy() for v in old.data.vertices]
    low=Vector([min(p[i] for p in old_points) for i in range(3)])
    high=Vector([max(p[i] for p in old_points) for i in range(3)])
    center=(low+high)/2;inverse=parent.matrix_world.inverted()
    rows=25;cols=41;points=[];max_projection=0
    for j in range(rows):
        v=j/(rows-1)
        for k in range(cols):
            u=k/(cols-1);x=low.x+(high.x-low.x)*u
            y=low.y+(high.y-low.y)*v
            # Rounded corners and body-fitted drape; not a hovering quadrilateral.
            y=center.y+(y-center.y)*(1-.15*abs(2*u-1)**6)
            z=high.z-.36*abs(2*u-1)**2
            probe=parent.matrix_world@Vector((x,y,z))
            hit,normal,index,distance=tree.find_nearest(probe)
            if hit is None or distance>.25:raise ValueError('LOOK_SADDLE_SUPPORT_MISSING')
            max_projection=max(max_projection,distance)
            edge=abs(2*u-1)**5
            offset=.022+.003*math.sin(v*math.tau*3+.4)*edge
            points.append(inverse@(hit+normal*offset))
    material=old.data.materials[0].copy();material.name='MF Nihang supported wool saddle pad'
    bs=material.node_tree.nodes.get('Principled BSDF')
    if bs:
        for link in list(material.node_tree.links):
            if link.to_socket==bs.inputs['Roughness']:material.node_tree.links.remove(link)
        bs.inputs['Roughness'].default_value=.91
    obj=mesh(bpy,'MF Nihang body-fitted wool saddle pad',points,grid(rows,cols),material,parent)
    solid=obj.modifiers.new('Layered wool thickness','SOLIDIFY');solid.thickness=.009
    sub=obj.modifiers.new('Soft blanket edges','SUBSURF');sub.levels=1;sub.render_levels=1
    old.hide_render=True;old.hide_viewport=True
    return {'pad':obj.name,'vertices':len(points),'maximum_projection':max_projection,
            'scope':'Standing actual body surface fit; rising/reverse rider interfaces remain unqualified.'}


def run(bpy):
    bpy.context.scene.frame_set(283);bpy.context.view_layer.update()
    roots=[bpy.data.objects['mounted leader'],sorted([o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:o.name)[0]]
    report=[]
    for index,root in enumerate(roots):
        leader=index==0
        upper=next(o for o in root.children if o.name.startswith('320 articulated upper body'))
        frame=next(o for o in upper.children if o.name.startswith('secondary facial and crown'))
        core=next(o for o in frame.children if o.name.startswith('319 supported dumalla'))
        material=core.data.materials[0]
        report.append({'actor':root.name,'crown':wrapped_crown(bpy,frame,material,leader),
                       'garment':garment_form(bpy,root,leader),'beard':beard_volume(frame)})
    pad=saddle_pad(bpy)
    coat=horse_finish(bpy)
    return {'actors':report,'saddle':pad,'coat':coat,'scope':'Two-actor cloth and beard-volume proof plus existing dark horse coat treatment; no motion or appearance acceptance.'}
