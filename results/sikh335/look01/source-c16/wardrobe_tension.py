"""Authored open leather load paths on height-local tension envelopes.

Bridges local cloth folds instead of tracing their individual surface normals.
Static visual tailoring, not a force simulation or dynamic contact model.
"""


def open_curve(anchors,steps=20):
    result=[]
    for i in range(len(anchors)-1):
        p0,p1,p2,p3=[anchors[max(0,min(len(anchors)-1,k))] for k in (i-1,i,i+1,i+2)]
        for j in range(steps):
            t=j/steps
            result.append(.5*(2*p1+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3))
    return result+[anchors[-1]]


def support_cloud():
    import bpy
    points=[]
    # The loose head-covering falls OVER the harness. Only the tunic and
    # wrapped chest cloth provide a support under the leather load path.
    for name in ('MF_fit_tunic_173_visible','MF_173_diagonal_scarf_fall'):
        ob=bpy.data.objects[name];coords=ob.data.attributes['MF_173_material_coords'].data
        for i,v in enumerate(ob.data.vertices):
            rest=coords[i].vector
            if -6.1<rest.z<-.8 and abs(rest.x)<2.35:points.append((rest.z,ob.matrix_world@v.co))
    return points


def at_height(cloud,z,band=.24):
    return [p for height,p in cloud if abs(height-z)<=band]


def cap_weight(z):
    t=max(0.,min(1.,(z+2.50)/.25))
    return t*t*(3-2*t)


def fair(values,rounds=12):
    values=list(values)
    for _ in range(rounds):values=[p if i in (0,len(values)-1) else values[i-1]*.20+p*.60+values[i+1]*.20 for i,p in enumerate(values)]
    return values


def shoulder_envelope(cloud):
    """Actual superior support, not a convex tent across a neckline hollow."""
    import bpy
    from mathutils.bvhtree import BVHTree
    from wardrobe_studio import single_surface_mesh
    ob=bpy.data.objects['MF_fit_tunic_173_visible'];data=single_surface_mesh(ob)
    tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in data.vertices],
                             [tuple(f.vertices) for f in data.polygons])
    bpy.data.meshes.remove(data)
    return (tree,)


def surface(q,cloud,cap):
    from mathutils import Vector
    from wardrobe_studio import torso_matrix
    from wardrobe_footbed import footprint,radius
    frame=torso_matrix(q.z);inverse=frame.inverted()
    weight=cap_weight(q.z);cap_hit=None;cap_normal=None
    if weight:
        root=torso_matrix(-2.8)@Vector((0,.14,-2.8))
        query=frame@q;hits=[]
        for tree in cap:
            hit,n,_,distance=tree.find_nearest(query)
            if hit is not None:hits.append((distance,hit,n))
        if not hits:raise ValueError('Missing authored superior shoulder support')
        _,cap_hit,cap_normal=min(hits,key=lambda row:row[0])
        # A solidified garment has inner faces too. Orient support away from
        # the torso before adding leather clearance, never into that shell.
        if cap_normal.dot(cap_hit-root)<0:cap_normal=-cap_normal
        if weight==1:return cap_hit,cap_normal
    sample=[inverse@p for p in at_height(cloud,q.z)]
    if len(sample)<3:sample=[inverse@p for p in at_height(cloud,q.z,.5)]
    hull=footprint([(p.x,p.y) for p in sample])
    center=Vector((0,.14,q.z));direction=Vector((q.x,q.y-.14,0)).normalized()
    r=radius(hull,(0,.14),(direction.x,direction.y))
    if r is None:raise ValueError('No bounded torso support at authored load path')
    point=frame@(center+direction*r)
    outward=(frame.to_3x3()@direction).normalized()
    if weight:
        # A shoulder strap goes OVER the superior shoulder, not horizontally
        # around the arm at a constant-height radial section.
        point=point.lerp(cap_hit,weight);outward=outward.lerp(cap_normal,weight).normalized()
    return point,outward


def harness(mats):
    import bpy
    from mathutils import Vector
    from wardrobe_studio import torso_point,panel,line
    from wardrobe_refinement import tree_for
    cloud=support_cloud();cap=shoulder_envelope(cloud);belt=tree_for(bpy.data.objects['MF_173_waist_belt'])
    # Open ends meet the waist belt. Shoulder crosses from front to back;
    # there is no old closed hip-return loop or disconnected scarf fragment.
    authored=[(-1.15,-1.00,-5.62),(-.65,-1.42,-4.55),(.35,-1.52,-3.45),
              (1.20,-1.12,-2.55),(1.55,-.42,-1.65),(1.62,.35,-1.65),
              (1.20,1.05,-2.65),(.35,1.28,-3.65),(-.65,1.20,-4.65),(-1.15,.92,-5.62)]
    for sign in (-1,1):
        rest=open_curve([Vector((sign*x,y,z)) for x,y,z in authored])
        centers=[];normals=[]
        for q in rest:
            hit,n=surface(q,cloud,cap)
            margin=(.085 if sign==1 else .045)*(1-cap_weight(q.z))+.060*cap_weight(q.z)
            centers.append(hit+n*margin);normals.append(n)
        for end in (0,len(centers)-1):
            hit,n,_,_=belt.find_nearest(torso_point(rest[end]));centers[end]=hit+n*.050;normals[end]=n
        centers=fair(centers,120);normals=[n.normalized() for n in fair(normals,120)]
        vertices=[];previous_width=None
        for i,p in enumerate(centers):
            tangent=(centers[min(len(centers)-1,i+1)]-centers[max(0,i-1)]).normalized()
            width=tangent.cross(normals[i]).normalized()*.125
            if previous_width is not None and width.dot(previous_width)<0:width=-width
            previous_width=width
            for vertex in (p-width,p+width):
                from wardrobe_studio import torso_matrix
                local=torso_matrix(rest[i].z).inverted()@vertex
                # Final cloth exclusion is one continuous OUTER tunic, not
                # the mixed support/height transitions that created kinks.
                hit,n,_,distance=cap[0].find_nearest(vertex)
                root=torso_matrix(rest[i].z)@Vector((0,.14,rest[i].z))
                if hit is not None and distance<.5:
                    if n.dot(hit-root)<0:n=-n
                    if (vertex-hit).dot(n)<.025:vertex=hit+n*.025
                vertices.append(tuple(vertex))
        faces=[(2*i,2*i+2,2*i+3,2*i+1) for i in range(len(centers)-1)]
        ob=panel('MF_173_tension_harness_'+str(sign),vertices,faces,mats['leather'],.026,0)
        wear=ob.data.attributes.get('MF_173_contact_wear') or ob.data.attributes.new('MF_173_contact_wear','FLOAT','POINT')
        import math
        for i,item in enumerate(wear.data):item.value=.12+.06*math.sin(i*.83)**2
        for edge in (0,1):line('MF_173_harness_welt_'+str(sign)+'_'+str(edge),[vertices[2*i+edge] for i in range(len(centers))],mats['thread'],.005)
        if sign==1:
            k=min((i for i,q in enumerate(rest) if q.y<0),key=lambda i:abs(rest[i].z+3.1))
            p=centers[k]+normals[k]*.035;t=(centers[k+1]-centers[k-1]).normalized();w=t.cross(normals[k]).normalized()
            ring=[tuple(p+w*a+t*b) for a,b in [(-.14,-.15),(.14,-.15),(.14,.15),(-.14,.15),(-.14,-.15)]]
            line('MF_173_strap_adjuster_1',ring,mats['metal'],.018)
    bpy.context.view_layer.update()


def pressure_weight(lateral):
    t=max(0.,min(1.,1-lateral/.18))
    return t*t*(3-2*t)


def press_visible_scarf():
    """Authored static leather pressure on the ACTUAL visible cloth sheet."""
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_studio import single_surface_mesh,torso_matrix
    scarf=bpy.data.objects['MF_173_open_scarf'];strips=[]
    for sign in (-1,1):
        ob=bpy.data.objects['MF_173_tension_harness_'+str(sign)]
        data=single_surface_mesh(ob)
        strips.append(BVHTree.FromPolygons([ob.matrix_world@v.co for v in data.vertices],
                                           [tuple(f.vertices) for f in data.polygons]))
        bpy.data.meshes.remove(data)
    # Use the same smooth single tunic as a lower exclusion floor.
    shirt=shoulder_envelope(())[0]
    inverse=torso_matrix(-2.8).inverted()
    for vertex in scarf.data.vertices:
        p=scarf.matrix_world@vertex.co;local=inverse@p
        if local.z>-1.35:continue
        root=torso_matrix(-2.8)@Vector((0,.14,local.z))
        changed=False
        for tree in strips:
            hit,n,_,distance=tree.find_nearest(p)
            if hit is None or distance>.45:continue
            if n.dot(hit-root)<0:n=-n
            offset=p-hit;signed=offset.dot(n)
            lateral=(offset-n*signed).length
            weight=pressure_weight(lateral)
            if -.03<signed<.35 and weight>0:
                p=p.lerp(hit-n*.027,weight);changed=True
        if not changed:continue
        hit,n,_,distance=shirt.find_nearest(p)
        if hit is not None and distance<.35:
            if n.dot(hit-root)<0:n=-n
            if (p-hit).dot(n)<.025:p=hit+n*.025
        vertex.co=scarf.matrix_world.inverted()@p
    scarf.data.update();bpy.context.view_layer.update()
