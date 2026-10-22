"""Actual neutral-body cloth prerequisite, separate from the posed production cast.

Only the fixed local Blender Studio donor is loaded. No asset scripts run. The
rest garment uses the donor's continuous shoulder/arm topology, not the rejected
rectangular armhole construction. This is a fit proof, not a tailoring pattern.
"""
import json
import math
from pathlib import Path
import numpy as np

DONOR = '.runtime/assets/series01-body-blender-studio/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'
BODY = 'MF Nihang neutral body proof'
CLOTH = 'MF Nihang neutral garment proof'


def connected_arm(points, faces, cut=1.17):
    """Below upper arm cut, topology separates hand/forearm from torso/leg."""
    p=np.asarray(points);mask=(p[:,2]<cut)&(p[:,0]>0)
    adj={int(i):set() for i in np.flatnonzero(mask)}
    for face in faces:
        members=[int(i) for i in face if mask[i]]
        for i in members:adj[i].update(members)
    candidates=np.flatnonzero(mask)
    seed=int(candidates[np.argmax(p[candidates,0])]);seen={seed};stack=[seed]
    while stack:
        for j in adj[stack.pop()]:
            if j not in seen:seen.add(j);stack.append(j)
    result=np.zeros(len(p),dtype=bool);result[list(seen)]=True
    return result


def bend_weights(points, arm=None):
    """One right elbow test; shoulder and opposite arm are deliberately fixed."""
    p=np.asarray(points)
    t=np.clip((1.19-p[:,2])/.12,0,1)
    side=np.clip((p[:,0]-.19)/.06,0,1)
    # Low hand vertices reach x=.199 on this donor. A lateral weight ramp
    # splits the hand, and a rectangular cutoff cannot identify anatomy.
    if arm is not None:side=np.where(p[:,2]<1.17,np.asarray(arm,dtype=float),side)
    return (t*t*(3-2*t))*(side*side*(3-2*side))


def bend_points(points, angle, arm=None):
    """Weighted rigid elbow rotation; no segment scaling or cuff target fitting."""
    p=np.asarray(points);w=bend_weights(p,arm)
    pivot=np.array([.285,-.005,1.13]);q=p-pivot
    a=angle*w;c=np.cos(a);s=np.sin(a)
    result=p.copy()
    result[:,1]=pivot[1]+q[:,1]*c-q[:,2]*s
    result[:,2]=pivot[2]+q[:,1]*s+q[:,2]*c
    result[w==0]=p[w==0]
    return result


def neutral_ease(points):
    """Bridge pectoral/abdominal sculpting in the rest garment, not body anatomy.

    The continuous shoulder/arm interface remains untouched. Front torso ease
    tapers to the collar and side seam instead of following individual muscles.
    """
    p=np.asarray(points);result=p.copy()
    x=abs(p[:,0]);z=p[:,2]
    front=np.clip((-p[:,1]-.005)/.05,0,1)
    side=np.clip((.205-x)/.045,0,1)
    height=np.clip((z-.98)/.06,0,1)*np.clip((1.385-z)/.07,0,1)
    curve=np.interp(z,[.97,1.08,1.22,1.29,1.385],[-.158,-.17,-.176,-.153,-.09])
    surface=curve*np.sqrt(np.maximum(.1,1-(x/.255)**2))
    result[:,1]=p[:,1]+np.minimum(0,surface-p[:,1])*front*side*height
    return result


def run(bpy, phase, out):
    import bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    root=Path(__file__).resolve().parents[4]
    if phase=='bend':
        # The caller binds the reviewed neutral derivative as the parent.
        if bpy.context.scene.name!='MF neutral garment studio':raise ValueError('NEUTRAL_PARENT_REQUIRED')
        evidence={}
        for name in (BODY,CLOTH):
            ob=bpy.data.objects.get(name)
            if ob is None or ob.get('neutral_rest_proof')!=1:raise ValueError('NEUTRAL_REST_REQUIRED')
            rest=np.array([v.co[:] for v in ob.data.vertices])
            faces=[tuple(p.vertices) for p in ob.data.polygons]
            arm=connected_arm(rest,faces)
            bent=bend_points(rest,math.radians(-75),arm)
            ob.data.vertices.foreach_set('co',bent.ravel());ob.data.update()
            ob['proof_bend_degrees']=-75
            np.savez_compressed(out/('body-bend.npz' if name==BODY else 'garment-bend.npz'),rest=rest,bent=bent,arm=arm)
            evidence[name]={'vertices':len(rest),'unchanged_shoulder':bool(np.array_equal(rest[rest[:,2]>1.21],bent[rest[:,2]>1.21])),
                            'max_displacement':float(np.linalg.norm(bent-rest,axis=1).max())}
        return {'phase':phase,'angle_degrees':-75,'objects':evidence,
                'limits':'Single static bend prerequisite. No rig, motion, pose cache or cast integration qualification.'}
    if phase!='neutral':raise ValueError('NEUTRAL_PHASE')
    donor=root/DONOR
    if not donor.is_file():raise ValueError('NEUTRAL_DONOR_MISSING')
    if bpy.data.objects.get(BODY):raise ValueError('NEUTRAL_ALREADY_EXISTS')
    studio=bpy.data.scenes.new('MF neutral garment studio');bpy.context.window.scene=studio
    studio.render.fps=24
    with bpy.data.libraries.load(str(donor),link=False) as (_,loaded):
        loaded.objects=['GEO-body_male_realistic']
    source=loaded.objects[0];studio.collection.objects.link(source)
    for m in source.modifiers:
        if m.type=='MULTIRES':m.levels=min(1,m.total_levels)
    bpy.context.view_layer.update()
    data=bpy.data.meshes.new_from_object(source.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    points=np.array([tuple(source.matrix_world@v.co) for v in data.vertices])
    points[:,0]-=(-2.705880880355835-1.8228728771209717)/2
    faces=[tuple(p.vertices) for p in data.polygons]
    bpy.data.objects.remove(source,do_unlink=True);bpy.data.meshes.remove(data)
    if not (1.55<points[:,2].max()<2.1 and abs(points[:,0].mean())<.03):raise ValueError('NEUTRAL_DONOR_FRAME')
    def mesh(name,coords,polys):
        d=bpy.data.meshes.new(name);d.from_pydata(coords,[],polys);d.update()
        ob=bpy.data.objects.new(name,d);studio.collection.objects.link(ob)
        bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
        for p in d.polygons:p.use_smooth=True
        return ob
    body=mesh(BODY,points,faces);body['neutral_rest_proof']=1
    # Real neutral donor support, no inherited posed Basis, no old cuff cache.
    ids=np.flatnonzero((points[:,2]<1.435)&(((abs(points[:,0])<.19)&(points[:,2]>.97))|((abs(points[:,0])>=.19)&(points[:,2]>.91))))
    mapping={int(i):j for j,i in enumerate(ids)}
    cf=[tuple(mapping[i] for i in f) for f in faces if all(i in mapping for i in f)]
    cloth=mesh(CLOTH,points[ids],cf)
    bpy.ops.object.select_all(action='DESELECT');cloth.select_set(True);bpy.context.view_layer.objects.active=cloth
    smooth=cloth.modifiers.new('Neutral fabric envelope','SMOOTH');smooth.factor=.65;smooth.iterations=12
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    if len(cloth.data.vertices)>7500:
        dec=cloth.modifiers.new('Cloth simulation topology','DECIMATE');dec.ratio=7500/len(cloth.data.vertices)
        bpy.ops.object.modifier_apply(modifier=dec.name)
    body.data.calc_loop_triangles();tri=np.array([tuple(t.vertices) for t in body.data.loop_triangles])
    tree=BVHTree.FromPolygons(points,tri,all_triangles=True)
    # Smooth cut-boundary sampling before adding ease. This repairs the visibly
    # saw-toothed crop without smoothing body anatomy or hiding it under a collar.
    bm=bmesh.new();bm.from_mesh(cloth.data)
    # Cut through faces at one coherent plane. Selecting only donor vertices
    # above/below a height leaves a stair-stepped opening; smoothing that stair
    # and pinning it merely preserves the defect through simulation.
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
        dist=1e-6,plane_co=(0,0,1.425),plane_no=(0,0,1),clear_outer=True)
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    boundary=[v for v in bm.verts if v.is_boundary]
    for _ in range(6):
        updates={v:sum((e.other_vert(v).co for e in v.link_edges if e.is_boundary),Vector())/
                 max(1,sum(e.is_boundary for e in v.link_edges)) for v in boundary}
        for v,p in updates.items():v.co=v.co.lerp(p,.45)
    bm.to_mesh(cloth.data);bm.free();cloth.data.update()
    bm=bmesh.new();bm.from_mesh(cloth.data);bm.verts.ensure_lookup_table()
    neck_ids=np.array([v.index for v in bm.verts if v.is_boundary and v.co.z>1.38],dtype=int)
    if len(neck_ids)<12:raise ValueError('NEUTRAL_NECK_BOUNDARY_MISSING')
    if any(sum(e.is_boundary for e in bm.verts[int(i)].link_edges)!=2 for i in neck_ids):
        raise ValueError('NEUTRAL_NECK_NONMANIFOLD')
    bm.free()
    raw=np.array([v.co[:] for v in cloth.data.vertices]);norm=np.array([v.normal[:] for v in cloth.data.vertices])
    designed=neutral_ease(raw+norm*.018)
    start=designed.copy()
    # Initial outside fit is distinct from settling; do not ask collision to
    # eject deep penetrations or inflate a posed rectangular armhole.
    for _ in range(3):
        for i,p in enumerate(start):
            hit,n,idx,dist=tree.find_nearest(Vector(p));signed=np.dot(p-np.array(hit),np.array(n))
            if signed<.009:start[i]+=np.array(n)*(.009-signed)
    # True opening follows a single level; radial ease leaves room for the
    # subdivided skin without changing body anatomy or hiding the edge.
    start[neck_ids,2]=1.427
    radial=start[neck_ids,:2]-np.array([0,-.018])
    start[neck_ids,:2]+=radial/np.maximum(1e-8,np.linalg.norm(radial,axis=1))[:,None]*.006
    fit=np.linalg.norm(start-designed,axis=1)
    if fit.max()>.045:raise ValueError('NEUTRAL_INITIAL_FIT_EXCESS')
    cloth.data.vertices.foreach_set('co',start.ravel());cloth.data.update()
    group=cloth.vertex_groups.new(name='Neutral shoulder collar waist cuff supports')
    z=start[:,2];x=abs(start[:,0])
    pins=np.maximum.reduce([np.clip((z-1.355)/.055,0,1)*(x<.22),
                            np.clip((.995-z)/.020,0,1)*(x<.19),
                            np.clip((.94-z)/.025,0,1)*(x>.25)])
    pins[neck_ids]=1
    for i,w in enumerate(pins):
        if w>0:group.add([i],float(w),'REPLACE')
    body.modifiers.new('Neutral support collision','COLLISION');body.collision.thickness_outer=.002
    mod=cloth.modifiers.new('Actual neutral drape','CLOTH');s=mod.settings
    s.quality=12;s.mass=.28;s.tension_stiffness=35;s.compression_stiffness=35;s.shear_stiffness=20
    s.bending_stiffness=1.5;s.air_damping=6;s.time_scale=.6;s.vertex_group_mass=group.name;s.pin_stiffness=1
    mod.collision_settings.distance_min=.004;mod.collision_settings.use_self_collision=True;mod.collision_settings.self_distance_min=.002
    mod.point_cache.frame_start=1;mod.point_cache.frame_end=40
    for frame in range(1,41):
        studio.frame_set(frame);bpy.context.view_layer.update()
        ev=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get())
    final=np.array([v.co[:] for v in ev.data.vertices]);delta=np.linalg.norm(final-start,axis=1)
    polys=[tuple(p.vertices) for p in cloth.data.polygons]
    np.savez_compressed(out/'neutral-proof.npz',body=points,triangles=tri,raw=raw,designed=designed,start=start,final=final,pins=pins,displacement=delta,neck_ids=neck_ids)
    if not np.isfinite(final).all() or delta.max()>.09:raise ValueError('NEUTRAL_DRAPE_DISPLACEMENT:'+str(float(delta.max())))
    cloth.modifiers.remove(mod);cloth.data.vertices.foreach_set('co',final.ravel());cloth.data.update()
    body.modifiers.clear();cloth['neutral_rest_proof']=1
    for ob,color in ((body,(.27,.22,.19,1)),(cloth,(.035,.075,.14,1))):
        mat=bpy.data.materials.new(ob.name+' material');mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.8
        ob.data.materials.clear();ob.data.materials.append(mat)
        sub=ob.modifiers.new('Proof smooth surface','SUBSURF');sub.levels=1;sub.render_levels=1
    solid=cloth.modifiers.new('Fabric thickness','SOLIDIFY');solid.thickness=.0015
    bpy.context.view_layer.update()
    deps=bpy.context.evaluated_depsgraph_get()
    body_eval=body.evaluated_get(deps);cloth_eval=cloth.evaluated_get(deps)
    bp=np.array([v.co[:] for v in body_eval.data.vertices]);body_eval.data.calc_loop_triangles()
    bt=[tuple(t.vertices) for t in body_eval.data.loop_triangles]
    final_tree=BVHTree.FromPolygons(bp,bt,all_triangles=True)
    cp=np.array([v.co[:] for v in cloth_eval.data.vertices]);mask=cp[:,2]>1.395
    distances=[]
    for p in cp[mask]:
        hit,n,_,_=final_tree.find_nearest(Vector(p));distances.append(float(np.dot(p-np.array(hit),np.array(n))))
    (out/'neck-clearance.json').write_text(json.dumps({'evaluated_samples':len(distances),
        'minimum_signed_vertex_clearance':min(distances),'negative_samples':sum(v<0 for v in distances),
        'boundary_z_range':float(np.ptp(final[neck_ids,2])),
        'limits':'Vertex samples after all render modifiers; not continuous face-face collision proof.'},indent=2))
    # Retain neutral body and garment as real editable native meshes, not an
    # image plane or a data plot. Lighting reveals armpit and shoulder forms.
    camera_data=bpy.data.cameras.new('MF neutral camera');camera=bpy.data.objects.new('MF neutral camera',camera_data)
    studio.collection.objects.link(camera);studio.camera=camera
    target=Vector((0,0,1.19));camera.location=(0,-3.0,1.30)
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=1.22
    for name,loc,power,size in [('key',(-1.8,-2.2,3),300,2),('fill',(1.8,-1,1.8),130,2),('rim',(0,2,2.5),220,1.5)]:
        d=bpy.data.lights.new('MF neutral '+name,'AREA');d.energy=power;d.shape='DISK';d.size=size
        ob=bpy.data.objects.new(d.name,d);studio.collection.objects.link(ob);ob.location=loc
        ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
    studio.world=bpy.data.worlds.new('MF neutral world');studio.world.use_nodes=True
    studio.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.15,.15,.15,1)
    studio.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
    studio.view_settings.view_transform='AgX';studio.frame_set(283)
    return {'phase':'neutral','donor':DONOR,'donor_pose':'actual native unposed rest mesh',
            'garment_vertices':len(final),'body_vertices':len(points),'settle_frames':40,
            'maximum_displacement':float(delta.max()),'maximum_initial_fit':float(fit.max()),
            'maximum_design_ease':float(np.linalg.norm(designed-raw,axis=1).max()),
            'construction':'Continuous donor-derived neutral shell with real cloth settling; not a flat manufacturing pattern.',
            'limits':'Native neutral fit prerequisite only. No face, crown, saddle, crowd or motion qualification.'}
