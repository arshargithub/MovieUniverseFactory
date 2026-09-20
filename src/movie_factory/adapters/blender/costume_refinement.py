"""Reviewed, fixed reference-fit helpers for upperbody variants 16–26.

Not an arbitrary-code operation or dynamic clothing/rig qualification.
"""
import math


def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)


def neck_point(x,y,z,variant=16):
    """Preserve all facial points; define a continuous narrow neck/clavicle fan."""
    if z>=-.86:return (x,y,z)
    weight=smooth((-.86-z)/.32)
    if variant>=24:weight=smooth((-.86-z)/.18)
    angle=math.atan2(x,y-.22)
    sections=[(-.86,.63,.65),(-1.20,.59,.63),(-1.50,.62,.63),
              (-1.72,.80,.66),(-1.94,1.23,.70),(-2.30,1.75,.77)]
    if variant>=23:
        sections=[(-.86,.63,.65),(-1.20,.48,.58),(-1.50,.49,.59),
                  (-1.72,.70,.65),(-1.94,1.20,.70),(-2.30,1.75,.77)]
    if variant>=24:
        sections=[(-.86,.56,.64),(-1.20,.54,.61),(-1.50,.56,.62),
                  (-1.72,.75,.66),(-1.94,1.20,.70),(-2.30,1.75,.77)]
    for a,b in zip(sections,sections[1:]):
        if b[0]<=z<=a[0]:
            t=(a[0]-z)/(a[0]-b[0]);rx=a[1]*(1-t)+b[1]*t;ry=a[2]*(1-t)+b[2]*t;break
    else:rx,ry=sections[-1][1:]
    xx=rx*math.sin(angle);yy=(.10 if variant>=24 else .22)+ry*math.cos(angle)
    front=max(0.,-math.cos(angle))**2
    # Sternocleidomastoid approaches the central sternum, collarbones travel
    # laterally/upward from the notch; shallow relief, not bodybuilder anatomy.
    tendon=.15+.36*smooth((z+1.85)/.95)
    yy-=.070*math.exp(-((abs(xx)-tendon)/.085)**2)*math.exp(-((z+1.37)/.55)**2)*front
    collar=-1.88+.105*abs(xx)-.035*math.sin(abs(xx)*3)
    yy-=(.072 if variant>=23 else .095)*math.exp(-((z-collar)/(.085 if variant>=23 else .065))**2)*smooth((abs(xx)-.10)/.20)*front
    yy+=.060*math.exp(-(xx/.15)**2-((z+1.84)/.13)**2)*front
    yy+=.027*math.exp(-((abs(xx)-.70)/.40)**2-((z+1.67)/.12)**2)*front
    return (x*(1-weight)+xx*weight,y*(1-weight)+yy*weight,z)


def shawl_point(angle,t,variant=16):
    top=-2.06+.35*math.sin(angle)+.36*abs(math.sin(angle))
    bottom=-4.95+.55*math.sin(angle)
    z=top*(1-t)+bottom*t
    radius=1.90-.36*t+.10*math.sin(math.pi*t)
    phase=t*math.pi*6-.70*angle+.26*math.sin(angle*2+t*3)
    amp=(.065+.028*math.sin(angle*2+.4)**2)*(.35+.65*math.sin(math.pi*t)**.5)
    fold=amp*math.cos(phase)+.012*math.sin(phase*2.2)
    if variant>=17:
        # Stronger broad drape ridges, not a single flat diagonal bib.
        fold*=1.9
        z-=.16*max(0,math.sin(angle))*(1-t)**2
    x=(radius+fold)*math.sin(angle)
    y=.20-(.79+.20*math.sin(math.pi*t)+fold)*math.cos(angle)
    return x,y,z+.025*math.sin(phase+.6)*math.sin(math.pi*t)


def refine_neck(variant):
    import bpy
    obj=bpy.data.objects['MF_continuous_head_neck']
    for v in obj.data.vertices:v.co=neck_point(*v.co,variant)
    if variant>=24:
        import bmesh
        bm=bmesh.new();bm.from_mesh(obj.data)
        transition=[v for v in bm.verts if -1.40<v.co.z<-.86]
        for _ in range(18):bmesh.ops.smooth_vert(bm,verts=transition,factor=.35,use_axis_x=True,use_axis_y=True,use_axis_z=False)
        bm.normal_update();bm.to_mesh(obj.data);bm.free()
    obj.data.update()
    if variant>=17:
        attr=obj.data.attributes.new('MF_neck_anatomy_tone','FLOAT','POINT')
        for v in obj.data.vertices:
            x,y,z=v.co;weight=smooth((-.86-z)/.32)*smooth((.2-y)/.6)
            tendon=.15+.36*smooth((z+1.85)/.95)
            groove=math.exp(-((abs(x)-tendon-.10)/.10)**2)*math.exp(-((z+1.40)/.50)**2)
            collar=-1.88+.105*abs(x)-.035*math.sin(abs(x)*3)
            below=math.exp(-((z-collar+.09)/(.085 if variant>=26 else .055))**2)*smooth((abs(x)-.15)/.2)
            notch=math.exp(-(x/.15)**2-((z+1.84)/.11)**2)
            attr.data[v.index].value=1-weight*(.10*groove+(.065 if variant>=26 else .13)*below+.10*notch)
        n,l=obj.data.materials[0].node_tree.nodes,obj.data.materials[0].node_tree.links
        p=n.get('Principled BSDF');original=p.inputs['Base Color'].links[0].from_socket
        tone=n.new('ShaderNodeAttribute');tone.attribute_name=attr.name
        mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1
        l.new(original,mul.inputs[1]);l.new(tone.outputs['Fac'],mul.inputs[2]);l.new(mul.outputs[0],p.inputs['Base Color'])


def refine_hair(variant):
    import bpy
    from mathutils import Vector
    from reference_dressing import mesh_object
    # Restore roots into existing painted scalp; retain the locked face mesh and
    # authored waves, avoiding a new scalp cap or a second projected face image.
    for obj in bpy.context.scene.objects:
        if obj.type!='CURVE' or not obj.name.startswith('MF_fiber_lock'):continue
        for si,spline in enumerate(obj.data.splines):
            n=len(spline.points)-1
            for j,p in enumerate(spline.points):
                t=j/n;x,y,z,w=p.co
                root=(1-t)**3
                p.co=(x,y-.07*root,z+.44*root,w)
                p.radius*=smooth(t/.20)
                # Break up the identical bundled ends without adding flyaway
                # noise around the accepted eyes/face silhouette.
                p.co.z+=.035*math.sin(si*1.71+t*8)*smooth((t-.45)/.40)
        obj.data.bevel_depth*=.85
        if variant>=20:
            # Dark continuous lock volume below fine fibers prevents a bundle
            # of disconnected wires from defining the entire hair silhouette.
            strands=list(obj.data.splines);centers=[]
            for j in range(len(strands[0].points)):
                centers.append(sum((Vector(s.points[j].co[:3]) for s in strands),Vector())/len(strands))
            verts=[];faces=[]
            for j,center in enumerate(centers):
                t=j/(len(centers)-1);tangent=(centers[min(j+1,len(centers)-1)]-centers[max(0,j-1)]).normalized()
                outward=Vector((center.x,center.y-.22,.10)).normalized()
                across=tangent.cross(outward).normalized();normal=across.cross(tangent).normalized()
                taper=smooth(t/.18)*smooth((1-t)/.22)
                for k in range(8):
                    a=k*math.pi/4;v=center+across*(.046*taper*math.cos(a))+normal*(.023*taper*math.sin(a))
                    verts.append(tuple(v))
            for j in range(len(centers)-1):
                for k in range(8):faces.append((j*8+k,j*8+(k+1)%8,(j+1)*8+(k+1)%8,(j+1)*8+k))
            material=obj.data.materials[1]
            if variant>=23:
                material=bpy.data.materials.get('MF_soft_chestnut_lock_core')
                if material is None:
                    material=obj.data.materials[1].copy();material.name='MF_soft_chestnut_lock_core'
                    p=material.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.82;p.inputs['Specular IOR Level'].default_value=.08
            mesh_object('MF_cohesive_hair_lock',verts,faces,material,0)


def refine_cloth(variant):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    if variant>=26:
        from upperbody_refinement import torso_point
        tunic=bpy.data.objects['MF_upper_tunic'];nu,nv=96,72
        assert len(tunic.data.vertices)==nu*(nv+1)
        for i in range(nu):
            angle=i*math.pi*2/nu
            for j in range(nv+1):
                v=tunic.data.vertices[i*(nv+1)+j]
                z=v.co.z-.35*(1-j/nv)**4
                v.co=torso_point(angle,z)
        tunic.data.update();bpy.context.view_layer.update()
    bpy.data.objects['MF_layered_upper_scarf'].hide_render=True
    obj=bpy.data.objects['MF_diagonal_donor_wrap']
    nu,nv=80,56
    assert len(obj.data.vertices)==(nu+1)*(nv+1)
    dg=bpy.context.evaluated_depsgraph_get()
    supports=[BVHTree.FromObject(bpy.data.objects[name],dg) for name in
              ('MF_upper_tunic','MF_loose_tunic_sleeve_-1','MF_loose_tunic_sleeve_1')]
    for i in range(nu+1):
        angle=-1.9+3.8*i/nu
        for j in range(nv+1):
            x,y,z=shawl_point(angle,j/nv,variant)
            hits=[tree.ray_cast(Vector((x,-6,z)),Vector((0,1,0)),10)[0] for tree in supports]
            ys=[hit.y for hit in hits if hit is not None]
            if ys and y<.3:y=min(y,min(ys)-.045)
            obj.data.vertices[i*(nv+1)+j].co=(x,y,z)
    obj.data.update()
    # Keep portrait color vocabulary, but quiet projected mottling so actual
    # cloth folds, rather than mismatched painted creases, do most of the work.
    for name in ('MF_diagonal_donor_wrap','MF_adapted_donor_hood'):
        item=bpy.data.objects[name];mat=item.data.materials[0].copy();item.data.materials[0]=mat
        n,l=mat.node_tree.nodes,mat.node_tree.links;p=n.get('Principled BSDF')
        original=p.inputs['Base Color'].links[0].from_socket
        mix=n.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.42;mix.inputs[2].default_value=(.019,.045,.094,1)
        l.new(original,mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
    # A less rigid front edge; small smoothing retains the donor's hood drape.
    hood=bpy.data.objects['MF_adapted_donor_hood']
    modifier=hood.modifiers.new('Quiet hood scan facets','SMOOTH');modifier.factor=.45;modifier.iterations=3
    if variant==17:
        from reference_dressing import mesh_object
        from upperbody_refinement import torso_point,cloth_material
        verts=[];faces=[];ns,nr=96,20
        for i in range(ns):
            a=i*math.pi*2/ns;top=-1.42-.55*max(0,math.cos(a))**2
            inner=Vector(neck_point(.8*math.sin(a),.22-.7*math.cos(a),top))+Vector((math.sin(a)*.035,-math.cos(a)*.035,0))
            for j in range(nr+1):
                t=j/nr;z=top*(1-t)-2.55*t
                outer=Vector(torso_point(a,z))
                v=inner*(1-smooth(t))+outer*smooth(t);v.z=z
                verts.append(tuple(v))
        for i in range(ns):
            for j in range(nr):faces.append((i*(nr+1)+j,((i+1)%ns)*(nr+1)+j,((i+1)%ns)*(nr+1)+j+1,i*(nr+1)+j+1))
        liner=mesh_object('MF_fitted_inner_neckline',verts,faces,cloth_material('MF_inner_indigo',(.013,.030,.065),2),1)
        liner.modifiers.new('Thin tunic facing','SOLIDIFY').thickness=.012
    if variant>=18:
        import bmesh
        # Keep the donor's useful gathered folds, but give its neckline the
        # reference's open V instead of trying to make a flat substitute drape.
        upper=bpy.data.objects['MF_layered_upper_scarf'];upper.hide_render=False
        bm=bmesh.new();bm.from_mesh(upper.data)
        def rim(x):return -2.02+.42*abs(x)
        for vertex in bm.verts:vertex.co.z-=rim(vertex.co.x)
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,0),plane_no=(0,0,1),clear_outer=True,dist=.000001)
        for vertex in bm.verts:vertex.co.z+=rim(vertex.co.x)
        for _ in range(5):bmesh.ops.smooth_vert(bm,verts=list(bm.verts),factor=.35,use_axis_x=True,use_axis_y=True,use_axis_z=True)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(upper.data);bm.free()
        upper.data.materials[0]=obj.data.materials[0]
    if variant>=21:soft_layered_scarf(variant)


def soft_layered_scarf(variant):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from reference_dressing import mesh_object
    old=bpy.data.objects['MF_diagonal_donor_wrap'];mat=old.data.materials[0]
    old.name='MF_previous_diagonal_wrap_hidden';old.hide_render=True
    upper=bpy.data.objects['MF_layered_upper_scarf'];upper.name='MF_previous_gathered_wrap_hidden';upper.hide_render=True
    dg=bpy.context.evaluated_depsgraph_get()
    supports=[BVHTree.FromObject(bpy.data.objects[name],dg) for name in
              ('MF_upper_tunic','MF_loose_tunic_sleeve_-1','MF_loose_tunic_sleeve_1')]
    if variant>=22:supports.append(BVHTree.FromObject(bpy.data.objects['MF_continuous_head_neck'],dg))
    def outside(x,y,z,gap=.04):
        if y>.22:return (x,y,z)
        hits=[tree.ray_cast(Vector((x,-6,z)),Vector((0,1,0)),10)[0] for tree in supports]
        ys=[h.y for h in hits if h is not None]
        return (x,min(y,min(ys)-gap) if ys else y,z)
    verts=[];faces=[];nu,nv=128,48
    for i in range(nu):
        a=i*math.pi*2/nu;front=max(0,math.cos(a))
        top=-1.48-.48*front**2
        if variant>=22:top=-1.58-.53*front
        inner=Vector(neck_point(.8*math.sin(a),.22-.7*math.cos(a),top,variant))
        inner+=Vector((.04*math.sin(a),-.04*math.cos(a),0))
        bottom=-1.82-.93*front+.19*math.sin(a)
        for j in range(nv+1):
            t=j/nv;blend=smooth(t)
            x=inner.x*(1-blend)+(1.60 if variant>=23 else 1.85)*math.sin(a)*blend
            z=top*(1-t)+bottom*t
            y=inner.y*(1-blend)+(.22-.90*math.cos(a))*blend
            fold=.105*math.sin(t*math.pi*5+.35*math.sin(a*2))*math.sin(math.pi*t)
            x+=math.sin(a)*fold;y-=math.cos(a)*fold
            verts.append(outside(x,y,z))
    for i in range(nu):
        for j in range(nv):faces.append((i*(nv+1)+j,((i+1)%nu)*(nv+1)+j,((i+1)%nu)*(nv+1)+j+1,i*(nv+1)+j+1))
    cowl=mesh_object('MF_layered_upper_scarf',verts,faces,mat,2)
    if variant>=25:
        group=cowl.vertex_groups.new(name='MF_neckline_contact')
        for i in range(nu):
            for j in range(13):group.add([i*(nv+1)+j],1-smooth(j/12),'REPLACE')
        contact=cowl.modifiers.new('Evaluated neckline contact','SHRINKWRAP')
        contact.target=bpy.data.objects['MF_continuous_head_neck']
        contact.wrap_method='NEAREST_SURFACEPOINT';contact.wrap_mode='OUTSIDE_SURFACE'
        contact.offset=.045;contact.vertex_group=group.name
    cowl.modifiers.new('Soft cowl hem thickness','SOLIDIFY').thickness=.014
    verts=[];faces=[];nu,nv=96,64
    for i in range(nu+1):
        a=-1.85+3.70*i/nu
        top=-2.47+.63*math.sin(a);bottom=-4.77+.54*math.sin(a)
        if variant>=23:top=-2.70+.63*math.sin(a)
        for j in range(nv+1):
            t=j/nv;z=top*(1-t)+bottom*t;radius=1.93-.38*t
            phase=t*math.pi*6+.24*math.sin(a*2.3+t*2)
            fold=.14*math.sin(phase)*math.sin(math.pi*t)**.6
            x=(radius+fold*.4)*math.sin(a)
            y=.16-(.94+fold+.11*math.sin(math.pi*t))*math.cos(a)
            verts.append(outside(x,y,z,.065))
    for i in range(nu):
        for j in range(nv):faces.append((i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1))
    scarf=mesh_object('MF_diagonal_donor_wrap',verts,faces,mat,2)
    scarf.modifiers.new('Soft shawl edge thickness','SOLIDIFY').thickness=.014


def ribbon_frame(tangent,normal):
    """Width stays on the support tangent plane around shoulders, not fixed XZ."""
    tangent=tangent.normalized();normal=normal.normalized()
    across=normal.cross(tangent)
    if across.length<1e-7:raise ValueError('Degenerate strap frame')
    return across.normalized()


def shoulder_straps(variant):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from reference_dressing import mesh_object
    from upperbody_refinement import curve_object
    for obj in bpy.context.scene.objects:
        if obj.name.startswith(('MF_crossed_leather_strap','MF_saddle_stitch','MF_buckle_')):obj.hide_render=True
    leather=bpy.data.materials['MF_worn_brown_leather'];stitch=bpy.data.materials['MF_leather_edge_stitch'];brass=bpy.data.materials['MF_muted_brass_buckle']
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    names=('MF_upper_tunic','MF_loose_tunic_sleeve_-1','MF_loose_tunic_sleeve_1','MF_diagonal_donor_wrap')
    if variant>=18:names+=('MF_layered_upper_scarf',)
    trees=[BVHTree.FromObject(bpy.data.objects[name],dg) for name in names]
    shoulder_trees=trees[:3] if variant>=17 else trees
    for side in (-1,1):
        points=[];normals=[]
        # Continuous back -> over shoulder -> diagonal front. The upper section
        # is outside the scarf, making the reference shoulder loop legible.
        for j in range(49):
            t=j/48;a=math.pi*(1-t)
            x=side*(1.53+.08*math.sin(a));y=.22-.83*math.cos(a);z=-2.22+.55*math.sin(a)
            direction=Vector((side*.24,-math.cos(a),math.sin(a))).normalized()
            center=Vector((x,.22,-2.35));probe=Vector((x,y,z))
            # Radial support query around the shoulder cap.
            origin=center+direction*3
            hits=[tree.ray_cast(origin,-direction,5)[0] for tree in shoulder_trees]
            distances=[(h-center).dot(direction) for h in hits if h is not None]
            if distances:probe=center+direction*(max(distances)+.065)
            points.append(probe);normals.append(direction)
        if variant>=17:
            for j in range(49):
                t=j/48
                # The sleeve defines the shoulder. Do not let a projecting
                # shawl corner pull the harness into a square kink.
                a=math.pi*(1-t)
                points[j]=Vector((side*(1.74+.035*math.sin(a)),.22-.80*math.cos(a),-2.24+.49*math.sin(a)))
                normals[j]=Vector((side*.35,-math.cos(a),math.sin(a))).normalized()
                if variant>=18:
                    # Follow the OUTER deltoid, visible around the shoulder in
                    # the portrait, rather than burying a sagittal strip in it.
                    points[j]=Vector((side*(1.73+.61*math.sin(a)),.22-.73*math.cos(a),-2.34+.40*math.sin(a)))
                    normals[j]=Vector((side*math.sin(a),-math.cos(a),.20)).normalized()
                if variant>=19:
                    sleeve=trees[1 if side==-1 else 2]
                    center=Vector((side*1.64,.22,-2.40))
                    direction=Vector((side*.40,-math.cos(a),math.sin(a))).normalized()
                    hit,normal,_,_=sleeve.ray_cast(center+direction*3,-direction,5)
                    if hit is None:raise ValueError('Shoulder support ray missed')
                    points[j]=hit+normal*.04;normals[j]=normal
        start=points[-1]
        for j in range(1,101):
            t=j/100;x=start.x*(1-t)-side*1.45*t;z=start.z*(1-t)-5.65*t
            hits=[tree.ray_cast(Vector((x+offset,-6,z)),Vector((0,1,0)),10)[0] for tree in trees for offset in (-.14,0,.14)]
            ys=[h.y for h in hits if h is not None]
            y=(min(ys) if ys else -.6)-.065-(.028 if side==1 else 0)
            points.append(Vector((x,y,z)));normals.append(Vector((0,-1,0)))
        # Tension bridges recesses; smooth the support envelope without sinking.
        for j in range(50,len(points)-1):
            points[j].y=min(p.y for p in points[max(49,j-3):min(len(points),j+4)])
        for _ in range(8):
            old=[p.copy() for p in points]
            for j in range(1,len(points)-1):
                if j<49:points[j]=(old[j-1]+old[j]*2+old[j+1])/4
                else:points[j].y=(old[j-1].y+2*old[j].y+old[j+1].y)/4
        back_count=0
        if variant>=19:
            # Terminate below the waist, not as a free flap on the shoulder.
            start=points[0].copy();back=[];back_normals=[]
            for j in range(24):
                t=j/24;x=side*(.92*(1-t)+abs(start.x)*t);z=-5.65*(1-t)+start.z*t
                hits=[tree.ray_cast(Vector((x,5,z)),Vector((0,-1,0)),10)[0] for tree in trees[:3]]
                ys=[h.y for h in hits if h is not None]
                y=(max(ys) if ys else .98)+.045
                back.append(Vector((x,y,z)));back_normals.append(Vector((0,1,0)))
            points=back+points;normals=back_normals+normals;back_count=len(back)
        verts=[];faces=[];edges=[[],[]];frames=[]
        for j,point in enumerate(points):
            tangent=points[min(len(points)-1,j+1)]-points[max(0,j-1)]
            across=ribbon_frame(tangent,normals[j]);frames.append(across)
            for k in range(5):
                vertex=point+across*((k/4-.5)*.29)
                if variant>=19 and back_count<=j<back_count+49:
                    hit,normal,_,distance=trees[1 if side==-1 else 2].find_nearest(vertex)
                    if hit is not None and distance<.25:vertex=hit+normal*.045
                verts.append(tuple(vertex))
            for k,s in enumerate((-1,1)):edges[k].append(tuple(point+across*(s*.122)+normals[j]*.023))
        for j in range(len(points)-1):
            for k in range(4):faces.append((j*5+k,j*5+k+1,(j+1)*5+k+1,(j+1)*5+k))
        strap=mesh_object('MF_reference_shoulder_harness_'+str(side),verts,faces,leather,1)
        strap.modifiers.new('Leather thickness','SOLIDIFY').thickness=.028
        bevel=strap.modifiers.new('Soft leather edges','BEVEL');bevel.width=.012;bevel.segments=3
        for edge in edges:
            for j in range(0,len(edge)-2,3):curve_object('MF_shoulder_stitch',edge[j:j+2],stitch,.004)
        if side==1:
            idx=94+back_count;center=points[idx]+normals[idx]*.05;along=(points[idx+1]-points[idx-1]).normalized();across=frames[idx]
            corners=[(-.17,-.21),(.17,-.21),(.17,.21),(-.17,.21),(-.17,-.21)]
            curve_object('MF_reference_buckle',[tuple(center+across*u+along*v) for u,v in corners],brass,.025)
            curve_object('MF_reference_buckle_tongue',[tuple(center+across*u) for u in (-.16,.12)],brass,.018)
        strap['MF_route']='back over shoulder to crossed chest; no rig/dynamics qualification'


def body_z(z):
    if z>=-.86:return z
    return z+.23*smooth((-.86-z)/1.44)


def settle_body_proportion():
    import bpy
    from mathutils import Vector
    # The previous neck-to-collar distance exceeded the reference. Raise the
    # upper body gradually below the protected face, without changing the jaw.
    for obj in bpy.context.scene.objects:
        if obj.hide_render or obj.name=='FBHead':continue
        if obj.type not in ('MESH','CURVE'):continue
        if 'hair' in obj.name.lower() or 'fiber' in obj.name.lower():continue
        inv=obj.matrix_world.inverted()
        points=obj.data.vertices if obj.type=='MESH' else [p for s in obj.data.splines for p in s.points]
        for point in points:
            world=obj.matrix_world@Vector(point.co[:3]);world.z=body_z(world.z);local=inv@world
            if obj.type=='MESH':point.co=local
            else:point.co=(*local,point.co.w)
        if obj.type=='MESH':obj.data.update()


def refine(variant):
    refine_neck(variant);refine_hair(variant);refine_cloth(variant);shoulder_straps(variant)
    if variant>=20:settle_body_proportion()
