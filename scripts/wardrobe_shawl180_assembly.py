"""Staged headfall and shoulder-supported outer course, fixed native probe.

Render geometry is never projected after simulation. Hidden support points
are explicitly retained; this is authored drape, not automatic cloth tying.
"""
import json
import math
import numpy as np
import wardrobe_motion178 as foundation

HEAD=foundation.BASE/'wardrobe180-xpbdhead07/trajectory.npz'
HEAD_SHA='422be86e564f41328fb5bdabfb67aff2f1ba8c6597be4b9076309b2158b35632'
HEAD08=foundation.BASE/'wardrobe180-xpbdhead08/trajectory.npz'
HEAD08_SHA='55ce2f99edfbb45a7cf8a5898be31caa1f20bd7da3bb2ae2be9c43e49d7095e8'


def shoulder_course(contacts,closed_course=False,free_rear=False):
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    trees=[tree_for(o) for o in contacts]
    rows,cols=(96 if closed_course else 97),17;points=[];pins={}
    for i in range(rows):
        u=i/(rows-1);a=math.tau*i/rows if closed_course else -.33+u*(math.tau+.66)
        side=abs(math.sin(a))**10;front=max(0.,-math.cos(a));back=max(0.,math.cos(a))
        top=-2.05-.35*front-.30*back+.34*math.sin(a)*front
        if closed_course:top+=.60*back+.18*math.sin(a)*back
        width=.70+.45*front
        for j in range(cols):
            v=j/(cols-1);z=top-width*v
            direction=Vector((math.sin(a),math.cos(a),0));origin=Vector((0,.14,z));extent=0.
            for tree in trees:
                start=origin.copy();travel=0.
                for _ in range(24):
                    h,_,_,d=tree.ray_cast(start,direction,4.-travel)
                    if h is None:break
                    travel+=d;extent=max(extent,travel);travel+=1e-5;start=h+direction*1e-5
            if extent<=0:raise ValueError('Missing wrap support')
            radius=extent+.095+.04*math.sin(math.pi*v)
            p=origin+direction*radius
            # At the shoulders cloth lies ACROSS the cap. A vertical radial
            # band at this point wrapped the upper arm instead.
            sx=math.copysign((1.65+.38*v) if closed_course else (1.42+.42*v),math.sin(a));sy=.30+.9*math.cos(a)
            heights=[]
            for tree in trees:
                h,_,_,_=tree.ray_cast(Vector((sx,sy,.5)),Vector((0,0,-1)),5.)
                if h is not None:heights.append(h.z)
            if not heights and side>.8:raise ValueError('No shoulder contact at %s'%((i,j,sx,sy),))
            if heights:
                shoulder=Vector((sx,sy,max(heights)+.075+.025*math.sin(math.pi*v)))
                p=p.lerp(shoulder,side)
            points.append(tuple(p))
            if side>.99 and j in (4,8,12):pins[i*cols+j]=1. if not closed_course or j==8 else .8
            # Rear overlap ends are tucked, not allowed to become arm tails.
            if not closed_course and i in (0,rows-1) and j in (2,5,8):pins[i*cols+j]=1.
            if closed_course and not free_rear and i in (0,1,rows-1) and j==3:pins[i*cols+j]=1.
    _,faces=foundation.sheet_grid(rows,cols,lambda u,v:(0,0,0))
    if closed_course:faces.extend(((rows-1)*cols+j,(rows-1)*cols+j+1,j+1,j) for j in range(cols-1))
    return np.array(points),np.array(faces),pins


def initial_clearance(points,contact):
    """Resolve only initial penetration against the closed exterior proxy.

    No trajectory or final render projection is allowed. This records the
    displacement so an invalid start cannot be mistaken for solver success.
    """
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    tree=tree_for(contact);result=points.copy();distances=[]
    for i,p in enumerate(points):
        q=Vector(p)
        for _ in range(6):
            hit,normal,_,_=tree.find_nearest(q)
            clearance=(q-hit).dot(normal)
            if clearance>=.065:break
            q+=normal*(.065-clearance)
        distance=(q-Vector(p)).length
        if distance>.45:raise ValueError('Initial correction exceeds scoped clearance')
        distances.append(distance);result[i]=q[:]
    return result,{'vertices_adjusted':sum(d>1e-6 for d in distances),'max_native_displacement':max(distances)}


def closed_panel(points,faces,name,mat):
    import bpy,bmesh
    import wardrobe_studio as studio
    ob=studio.panel(name,points.tolist(),faces.tolist(),mat,.035,0)
    bpy.context.view_layer.objects.active=ob
    for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    ob.hide_render=True
    return ob


def union_contact(contacts, margin=.055):
    """One collision-only exterior, not intersecting layered thin shells."""
    import bpy,bmesh
    p=[];f=[]
    for ob in contacts:
        offset=len(p);p.extend(tuple(ob.matrix_world@v.co) for v in ob.data.vertices)
        f.extend(tuple(offset+i for i in poly.vertices) for poly in ob.data.polygons)
    mesh=bpy.data.meshes.new('MF180_contact_union');mesh.from_pydata(p,[],f);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,-4.8),plane_no=(0,0,1),clear_inner=True,clear_outer=False)
    boundary=[e for e in bm.edges if e.is_boundary]
    if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    ob=bpy.data.objects.new('MF178_support180_exterior_union',mesh);bpy.context.scene.collection.objects.link(ob);ob.hide_render=True
    mod=ob.modifiers.new('Contact union only','REMESH');mod.mode='VOXEL';mod.voxel_size=.035;mod.use_smooth_shade=True
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
    if len(ob.data.vertices)>500000:raise ValueError('Collision union complexity exceeded')
    # Conservative contact margin accounts for voxel and render smoothing.
    if not 0<=margin<=.055:raise ValueError('Bounded contact-only margin required')
    for v in ob.data.vertices:v.co+=v.normal*margin
    ob.data.update()
    return ob


def run(out,rig,mats):
    import bpy
    import wardrobe_studio as studio
    import wardrobe_motion178_controls as controls
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe_shawl180_dynamics import collision_snapshot,graph
    from wardrobe_shawl180 import measures
    from wardrobe_shawl179 import screens
    revised=out.name.endswith(('05','06'));free_rear=out.name.endswith('06')
    head_source,head_sha=(HEAD08,HEAD08_SHA) if revised else (HEAD,HEAD_SHA)
    if head_source.is_symlink() or foundation.digest(head_source)!=head_sha:raise ValueError('Inspected headfall changed')
    dress_actor(rig);repair(rig,'repair04')
    with np.load(head_source,allow_pickle=False) as data:hp=data['frames'][-1].copy();hf=data['faces'].copy()
    head=studio.panel('MF180_head_drape',hp.tolist(),hf.tolist(),mats['scarf'],.012,1)
    contacts=collision_snapshot(separate=True,closed=True)
    contacts.append(closed_panel(hp,hf,'MF178_support180_headfall',mats['scarf']))
    if out.name.endswith(('04','05','06')):contacts=[union_contact(contacts)]
    p,f,pins=shoulder_course(contacts,closed_course=revised,free_rear=free_rear)
    clearance=None
    if free_rear:p,clearance=initial_clearance(p,contacts[0])
    np.savez_compressed(out/'layout.npz',points=p,faces=f,pin_indices=list(pins),pin_weights=list(pins.values()),head=hp,head_faces=hf)
    mesh=bpy.data.meshes.new('MF180_course');mesh.from_pydata(p.tolist(),[],f.tolist());mesh.update()
    pin=mesh.attributes.new('MF180_pin','FLOAT','POINT')
    for i,w in pins.items():pin.data[i].value=w
    ob=bpy.data.objects.new('MF178_live_solver180_course',mesh);bpy.context.scene.collection.objects.link(ob);ob.hide_render=True
    graph(ob,contacts,'quality');samples=[]
    with controls.render_geometry_paused():
        for frame in range(1,73):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
            q=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear()
            if q.shape!=p.shape or not np.isfinite(q).all() or abs(q).max()>100:raise ValueError('Invalid native drape')
            samples.append(q)
            if frame%12==0:print('180 assembled course',frame,flush=True)
    np.savez_compressed(out/'trajectory.npz',points=p,faces=f,frames=np.array(samples),head=hp,head_faces=hf)
    studio.panel('MF180_outer_course',samples[-1].tolist(),f.tolist(),mats['scarf'],.012,1)
    screens(out,(72,));foundation.check_protected()
    report=measures(p,f,{1:samples[0],24:samples[23],72:samples[-1]},bpy.context.scene.unit_settings.scale_length)
    report.update({'head_sha256':head_sha,'closed_outer_course':revised,'protected_exact':True,'underarm_repair':'repair04',
        'initial_clearance':clearance,'rear_support_removed':free_rear,
        'visual_gate':'NOT_RUN','motion_gate':'NOT_RUN','head_static_during_outer_settle':True,
        'construction':'Separate staged cloth panels with hidden supports; continuity and riding are unqualified'})
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
