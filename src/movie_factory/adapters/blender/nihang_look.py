"""First supporting-cast form candidate, from existing local scene assets only.

Fixed trusted construction; not recipe code, cloth simulation or art approval.
Preserve animated owners and every garment cache. Prove two actors before spread.
"""
import math


def mesh(bpy,name,points,faces,material,parent):
    data=bpy.data.meshes.new(name);data.from_pydata(points,[],faces);data.update()
    for p in data.polygons:p.use_smooth=True
    obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj)
    obj.parent=parent;data.materials.append(material)
    return obj


def grid(rows,cols):
    return [(j*cols+k,j*cols+k+1,(j+1)*cols+k+1,(j+1)*cols+k) for j in range(rows-1) for k in range(cols-1)]


def wrapped_crown(bpy,frame,material,leader):
    """Tapered supported crown and one continuous oblique cloth winding.

    This replaces the old cylindrical silhouette, not its coordinates with noise.
    """
    for obj in frame.children:
        if obj.name.startswith(('319 supported dumalla','319 overlapping tied cloth','319 restrained chakram')):
            obj.hide_render=True;obj.hide_viewport=True
    height=.275 if leader else .225
    width=.114 if leader else .108
    def point(angle,z,offset=0):
        u=max(0,min(1,(z-.045)/height))
        # Full wrapped lower bowl; narrower raised crown rather than a cap.
        radius=width*(1+.13*math.sin(math.pi*min(1,u/.55)))*(1-.78*u**2.2)
        radius+=offset
        return (radius*math.sin(angle),.012-radius*1.1*math.cos(angle),z)
    points=[];rows=41;cols=97
    for j in range(rows):
        z=.045+height*j/(rows-1)
        for k in range(cols):points.append(point(math.tau*k/(cols-1),z))
    faces=grid(rows,cols);faces.append(tuple(range((rows-1)*cols,rows*cols)))
    core=mesh(bpy,'MF Nihang wrapped crown core',points,faces,material,frame)
    turns=7 if leader else 6;rows=turns*96+1;cols=11;points=[]
    for j in range(rows):
        progress=j/(rows-1);angle=math.tau*turns*progress
        center=.059+(height-.030)*progress+.038*math.sin(angle+.3)*(1-.45*progress)
        for k in range(cols):
            u=k/(cols-1)
            z=center+.049*(u-.5)
            ridge=.0045*math.sin(math.pi*u)+.0018*math.sin(u*math.pi*3+.4*math.sin(angle*2))
            points.append(point(angle,z,.0025+ridge))
    wrap=mesh(bpy,'MF Nihang continuous oblique cloth winding',points,grid(rows,cols),material,frame)
    solid=wrap.modifiers.new('Folded fabric thickness','SOLIDIFY');solid.thickness=.0015
    # Deliberate compressed cloth pleats near the raised top, not a smooth lid.
    points=[];rows=17;cols=65
    for j in range(rows):
        u=j/(rows-1);z=.045+height-.045+.052*u
        for k in range(cols):
            a=math.tau*k/(cols-1)
            p=point(a,z,.0015*(1-u)*math.cos(a*9))
            shrink=1-.80*u
            points.append((p[0]*shrink,.012+(p[1]-.012)*shrink,z))
    top=mesh(bpy,'MF Nihang gathered crown cloth',points,grid(rows,cols),material,frame)
    return [core.name,wrap.name,top.name]


def garment_form(bpy,root,leader):
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    upper=next(o for o in root.children if o.name.startswith('320 articulated upper body'))
    shirt=next(o for o in upper.children if o.name.startswith('319 anatomically'))
    # Copy data including all existing relative shape keys; original master stays
    # untouched on disk and no motion owner is renamed or reparented.
    shirt.data=shirt.data.copy();shirt['mf_supporting_appearance']=True
    blocks=[k.data for k in shirt.data.shape_keys.key_blocks] if shirt.data.shape_keys else [shirt.data.vertices]
    z0=.055 if leader else .885;zt=.455 if leader else 1.285
    for block in blocks:
        pts=np.empty(len(block)*3,dtype=np.float32);block.foreach_get('co',pts);pts=pts.reshape(-1,3)
        x=pts[:,0].copy();y=pts[:,1].copy();z=pts[:,2].copy()
        u=np.clip((z-z0)/(zt-z0),0,1)
        trunk=np.clip((.225-np.abs(x))/.065,0,1)*np.sin(math.pi*u)**.7
        fold=np.zeros_like(x)
        # Folds originate at the waist; oblique ridges spread toward shoulders.
        for anchor,slope,width,amp in ((-.13,-.15,.012,.009),(-.065,-.10,.010,.008),(.035,.12,.014,.010),(.13,.18,.012,.008)):
            d=x-(anchor+slope*(z-z0))
            fold+=amp*np.exp(-(d/width)**2)-amp*.38*np.exp(-((d-width*1.8)/(width*1.3))**2)
        pts[:,1]+=np.sign(y)*trunk*(.012+fold)
        pts[:,0]+=np.sign(x)*trunk*.008
        if not np.isfinite(pts).all():raise ValueError('LOOK_NONFINITE_GARMENT')
        block.foreach_set('co',pts.ravel())
    # Refit only actual existing outside-facing layers to this changed torso.
    bpy.context.view_layer.update()
    evaluated=shirt.evaluated_get(bpy.context.evaluated_depsgraph_get())
    tree=BVHTree.FromPolygons([v.co for v in evaluated.data.vertices],[tuple(p.vertices) for p in evaluated.data.polygons])
    facing=-1 if leader else 1;layers=[]
    for obj in upper.children:
        if not obj.name.startswith(('297 woven diagonal sash','319 overlapping chola chest panel','319 chola folded placket')):continue
        obj.data=obj.data.copy();obj['mf_supporting_appearance']=True
        points=obj.data.vertices if obj.type=='MESH' else [p for sp in obj.data.splines for p in sp.points]
        hits=0
        for p in points:
            x,y,z=p.co[:3];hit=tree.ray_cast(Vector((x,facing*.8,z)),Vector((0,-facing,0)))[0]
            if hit is not None:
                p.co.y=hit.y+facing*(.013 if obj.name.startswith('297 woven') else .004);hits+=1
        if obj.name.startswith('297 woven') and hits<.95*len(points):raise ValueError('LOOK_INCOMPLETE_SASH_FIT')
        layers.append({'object':obj.name,'hits':hits,'points':len(points)})
    return {'shirt':shirt.name,'vertices':len(shirt.data.vertices),'cached_poses':len(blocks),'layers':layers}


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
                       'garment':garment_form(bpy,root,leader)})
    pad=saddle_pad(bpy)
    return {'actors':report,'saddle':pad,'scope':'Initial structure-first supporting appearance candidate; no motion or appearance acceptance. Existing head/beard and horse surface unchanged for now.'}
