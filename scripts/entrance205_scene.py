"""Actual ledge terrain, grounded reusable dressing and a single actor path."""
import math
import numpy as np
import wardrobe_motion178 as base
from entrance205_geography import fields
FLOOR=np.array([0.,.2,-20.931])


def reverse_backdrop(scene):
    """Fixed opposite-world artwork; never rotate a painting with a camera."""
    import bpy
    from mathutils import Matrix
    from pathlib import Path
    from entrance_astra_world import mesh_object
    path=base.BASE.parent/'series01-entrance205/opposite-mountain-matte-v01.png'
    if not path.is_file():raise ValueError('Missing reverse-view artwork')
    col=bpy.data.collections['AS_composed_ochre_valley']
    # The opening matte was rotated for one camera corridor. Re-lay the two
    # fixed art panels around a common world centre, with their joins outside
    # the required OTS, frontal and continuous final-shot fields of view.
    primary=bpy.data.objects['MF188_distant_art_arc'];primary.data=primary.data.copy()
    if len(primary.data.vertices)!=322:raise ValueError('Unexpected primary matte topology')
    primary.parent=None;primary.matrix_world=Matrix.Identity(4)
    for i in range(161):
        a=math.radians(-76+212*i/160)
        primary.data.vertices[2*i].co=(math.cos(a)*8000,math.sin(a)*8000,FLOOR[2]-1000)
        primary.data.vertices[2*i+1].co=(math.cos(a)*8000,math.sin(a)*8000,FLOOR[2]+5000)
    primary.data.update()
    mat=bpy.data.materials.new('MF205_reverse_matte_painting');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links;n.clear()
    out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');tex=n.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(path),check_existing=True);tex.image.pack()
    l.new(tex.outputs['Color'],em.inputs['Color']);l.new(em.outputs[0],out.inputs['Surface'])
    points=[];faces=[];segments=180
    for i in range(segments+1):
        a=math.radians(136+148*i/segments)
        points.extend([(math.cos(a)*8000,math.sin(a)*8000,FLOOR[2]-1000),
                       (math.cos(a)*8000,math.sin(a)*8000,FLOOR[2]+5000)])
    for i in range(segments):faces.append((2*i,2*i+2,2*i+3,2*i+1))
    ob=mesh_object('MF205_fixed_reverse_matte',points,faces,col,None);ob.data.materials.append(mat)
    uv=ob.data.uv_layers.new(name='Unique opposite world panorama')
    for p in ob.data.polygons:
        for li in p.loop_indices:
            vi=ob.data.loops[li].vertex_index;uv.data[li].uv=((vi//2)/segments,vi%2)
    ob.visible_shadow=False;ob.visible_diffuse=False;ob.visible_glossy=False
    return {'path':str(path),'sha256':base.digest(path),'fixed_azimuth':[136,284],
            'prompt':str(path.with_suffix('.prompt.txt')),'prompt_sha256':base.digest(path.with_suffix('.prompt.txt')),
            'generation':'Built-in image generation, reference-guided opposite-direction matte; no external paid provider call',
            'original_matte':'Image unchanged; route derivative uses fixed -76..136-degree art panel about same world centre, radius8000. Opening source preserved.',
            'limitation':'Shot-corridor matte layout; artwork joins are not qualified for arbitrary360-degree cameras','visual_gate':'NOT_RUN'}


def actor(scene,route):
    import bpy
    from mathutils import Matrix
    from entrance190_integration import actor_object
    from entrance190_contacts import world_transform
    rig=bpy.data.objects['MF_body156_fit_rig']
    required={o for o in scene.objects if actor_object(o) and not o.hide_render}|{rig}
    for _ in range(12):
        before=len(required)
        for o in list(required):
            if o.parent:required.add(o.parent)
            for m in o.modifiers:
                for key in ('target','object'):
                    v=getattr(m,key,None)
                    if isinstance(v,bpy.types.Object):required.add(v)
            for c in o.constraints:
                v=getattr(c,'target',None)
                if isinstance(v,bpy.types.Object):required.add(v)
        if len(required)==before:break
    root=bpy.data.objects.new('MF205_shared_route_actor',None);scene.collection.objects.link(root);root.rotation_mode='QUATERNION'
    scene.frame_set(361);bpy.context.view_layer.update()
    for o in required:
        if o.parent is None and not any(c.type=='CHILD_OF' and c.target in required for c in o.constraints):
            matrix=o.matrix_world.copy();o.parent=root;o.matrix_world=matrix
    lights={o:o.matrix_world.copy() for o in scene.objects if o.type=='LIGHT' and o.data.type!='SUN'}
    for o in lights:
        if o.animation_data and o.animation_data.action:o.animation_data.action.use_fake_user=True
        o.animation_data_clear()
    for i in range(len(route['time'][::8])):
        root.matrix_world=world_transform(route,361+i)
        for prop in ('location','rotation_quaternion','scale'):root.keyframe_insert(prop,frame=361+i)
        for o,matrix in lights.items():
            o.matrix_world=Matrix.Translation(tuple(route['position'][i*8]*8.3))@matrix
            o.keyframe_insert('location',frame=361+i)
    return {'roots':[o.name for o in root.children],'light_support':'Area lights translate with actor without turning sunlight or rotating the world'}


def environment(scene,route):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from entrance201_cover import route_readability
    root=bpy.data.objects['AS_world_travel'];scene.frame_set(360);bpy.context.view_layer.update()
    oldworld=root.matrix_world.copy();root.animation_data_clear();root.matrix_world=oldworld
    land=bpy.data.objects['AS_valley_landform'];bpy.context.view_layer.update()
    inv=np.linalg.inv(np.array(land.matrix_world))
    x=np.r_[np.arange(-1500,-800,30),np.arange(-800,351,3),np.arange(380,1501,30)]
    y=np.r_[np.arange(-1600,-850,30),np.arange(-850,301,3),np.arange(330,1501,30)]
    xx,yy=np.meshgrid(x,y);xy=np.column_stack((xx.ravel(),yy.ravel()))
    height,dist=fields((xy-FLOOR[:2])/8.3,route);p=np.column_stack((xy,FLOOR[2]+height*8.3));local=p@inv[:3,:3].T+inv[:3,3]
    nx=len(x);faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(len(y)-1) for i in range(nx-1)]
    mesh=bpy.data.meshes.new('205 steep edge-side shared terrain');mesh.from_pydata(local.tolist(),[],faces);mesh.update()
    for m in land.data.materials:mesh.materials.append(m.copy())
    for f in mesh.polygons:f.use_smooth=True
    # Only the established checkpoint road gets the worn-earth stripe. The
    # barely-traceable escape is carried by rock/shelf geometry, not paint.
    attr=mesh.attributes.new('MF190_road_distance','FLOAT','POINT');attr.data.foreach_set('value',abs(xy[:,0]).astype(np.float32));land.data=mesh;land.hide_render=False
    route_readability()
    tree=BVHTree.FromPolygons(p.tolist(),faces)
    def ground(x,y):
        hit=tree.ray_cast(Vector((x,y,2000)),Vector((0,0,-1)),4000)[0]
        if hit is None:raise ValueError('Prop outside actual terrain')
        return hit.z
    # Retained opening dressings are not a qualified steep-route distribution.
    # Hide them in this derivative and place selected shared rock/brush meshes
    # on the newly evaluated surface; no floating old-height props survive.
    candidates=[]
    for o in scene.objects:
        if o.parent==root and o.type=='MESH' and o!=land and o.name!='MF188_distant_art_arc':
            if not o.hide_render and o.name.startswith(('MF196_','MF188_bank_stone')):candidates.append(o)
            o.hide_render=True
        if o.name.startswith(('MF196_debris','MF189_roadside','MF190_route_dressing','MF201_route_stone')):o.hide_render=True
    if not candidates:raise ValueError('No admitted rock donor')
    source=next((o for o in candidates if o.data.name.startswith('196 weathered clustered rock')),candidates[0]);mesh=source.data
    vertices=np.array([v.co[:] for v in mesh.vertices]);rng=np.random.default_rng(205);rows=[]
    # Source mesh/material reused. Sizes are authored in the new landscape;
    # broad low outcrops plus smaller fragments, not a uniform scatter field.
    for i in range(1300):
        index=int(rng.integers(0,len(route['time'][::8])));center=route['position'][index*8,:2];angle=route['heading'][index*8]
        normal=np.array([np.cos(angle),np.sin(angle)])
        xy_m=center+normal*rng.choice([-1,1])*rng.uniform(1.45,24)+rng.normal(0,1.2,2)
        h,d=fields(xy_m[None],route)
        if d[0]<1.35:continue
        o=bpy.data.objects.new('MF205_grounded_stone_'+str(i),mesh);scene.collection.objects.link(o)
        s=float(rng.uniform(.08,.45) if d[0]<2.7 else rng.uniform(.35,1.35) if d[0]<5 else rng.uniform(.8,3.8))
        o.scale=(s,s*rng.uniform(.75,1.35),s*.55);o.rotation_euler=(rng.uniform(.7,1.8),rng.uniform(-.5,.5),rng.uniform(0,2*math.pi))
        q=(vertices*np.array(o.scale))@np.array(o.rotation_euler.to_matrix()).T
        if np.max(np.linalg.norm(q[:,:2],axis=1))>(d[0]-1.1)*8.3:bpy.data.objects.remove(o,do_unlink=True);continue
        xy_native=xy_m*8.3+FLOOR[:2];o.location=(*xy_native,ground(*xy_native)-q[:,2].min()-.3*np.ptp(q[:,2]))
        # Actual low vertices must intersect the actual triangulated ground.
        ids=np.argsort(q[:,2])[:min(16,len(q))];world=q[ids]+np.array(o.location)
        clearance=[pt[2]-ground(pt[0],pt[1]) for pt in world]
        correction=max(0,min(clearance)+.12) if min(clearance)>0 else 0
        o.location.z-=correction
        clearance=[c-correction for c in clearance]
        rows.append({'name':o.name,'minimum_sampled_support_clearance':float(min(clearance)),'route_distance_m':float(d[0])})
    return {'vertices':len(p),'new_grounded_instances':len(rows),'dressing':rows,
        'old_dressing':'Hidden only in derivative; actual new terrain supports replacement instances',
        'support_test':'Evaluated terrain ray at instance base and16 lowest transformed mesh vertices; visual support still required'}


def checkpoint(scene):
    import bpy
    from mathutils import Vector
    from entrance204_build import guards
    # Opening contains no checkpoint; create provisional unmarked timber in
    # the original373 position, then use admitted guard-layout placement.
    mat=bpy.data.materials.new('205 provisional weathered timber');mat.diffuse_color=(.11,.062,.028,1);mat.use_nodes=True
    b=mat.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=mat.diffuse_color;b.inputs['Roughness'].default_value=.9
    z=FLOOR[2]
    for a,b in (((-21,-373,z),(-21,-373,z+12)),((21,-373,z),(21,-373,z+12)),((-24,-373,z+10),(24,-373,z+10)),((-24,-373,z+4),(24,-373,z+4))):
        a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=.65,depth=(b-a).length,location=(a+b)/2)
        o=bpy.context.object;o.name='MF190_provisional_timber_barrier';o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat)
    return guards(scene)
