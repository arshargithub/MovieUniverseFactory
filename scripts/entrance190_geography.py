"""Shared fork surface and derivative set dressing, in the actor route frame."""
import math
import numpy as np

FLOOR=-20.931


def fields(xy,route):
    p=np.asarray(xy,float);centre=route['position'][::8];heading=route['heading'][::8];grade=route['grade'][::8]
    forward=np.column_stack((np.sin(heading),-np.cos(heading)))
    # Continue both ends; the last hoof must not run off a diagnostic ribbon.
    centre=np.vstack((centre[0]+np.r_[forward[0]*-20,0],centre,centre[-1]+np.r_[forward[-1]*30,grade[-1]*30]))
    forward=np.vstack((forward[0],forward,forward[-1]));grade=np.r_[grade[0],grade,grade[-1]]
    distance=[];height=[]
    for j in range(0,len(p),2048):
        points=p[j:j+2048];delta=points[:,None,:]-centre[None,:,:2]
        ids=(delta**2).sum(2).argmin(1);offset=points-centre[ids,:2]
        # Perpendicular distance applies within the longitudinal end spans.
        along=(offset*forward[ids]).sum(1);cross=offset[:,0]*(-forward[ids,1])+offset[:,1]*forward[ids,0]
        distance.extend(abs(cross));height.extend(centre[ids,2]+along*grade[ids])
    distance=np.array(distance);height=np.array(height)
    main=abs(p[:,0]);road=np.minimum(main,distance)
    # Road contacts share the exact nearest-station tangent planes used in
    # the source horse solve. Roughness is outside the hoof corridor.
    ridge=3.2*np.exp(-((p[:,0]+6)/7)**2-((p[:,1]+40)/19)**2)
    farther=np.clip((distance-2.2)/9,0,1);farther=farther*farther*(3-2*farther)
    land=height+farther*(1.8+.7*np.sin(p[:,1]/8)+.4*np.cos(p[:,0]/5))
    land=np.maximum(land,ridge*farther)
    easy=np.clip((main-2.6)/4,0,1);easy=easy*easy*(3-2*easy)
    land*=easy
    # Exact shared contact surface wins at the branch, including its grade.
    land=np.where(distance<=2.2,height,land)
    # Behind the actual fork, continue the existing near-flat approach.
    blend=np.clip((12-p[:,1])/12,0,1);blend=blend*blend*(3-2*blend)
    land*=blend
    return land,road


def build(scene,route,visibility):
    import bpy
    from mathutils import Vector
    from entrance_astra_world import mesh_object
    from entrance188_ground import bank_height
    root=bpy.data.objects['AS_world_travel'];scene.frame_set(360);bpy.context.view_layer.update()
    root.animation_data_clear();root.location=(0,99.60000205*143/24,0)
    bpy.context.view_layer.update()
    for name,visible in visibility.items():
        ob=bpy.data.objects.get(name)
        if ob and (ob.parent==root or ob.name.startswith('AS_')):ob.hide_render=not visible
    for ob in scene.objects:
        if ob.name.startswith('MF189_roadside'):ob.hide_render=True
    # Keep the same packed distant artwork in its established world position.
    # The new high geographic framing must be checked for complete coverage.
    x=np.r_[np.arange(-1300,-750,35),np.arange(-750,351,3),np.arange(385,1301,35)]
    y=np.r_[np.arange(-1500,-750,35),np.arange(-750,251,3),np.arange(285,1501,35)]
    xx,yy=np.meshgrid(x,y);xy=np.column_stack((xx.ravel(),yy.ravel()));height,dist=fields((xy-[0,.2])/8.3,route)
    world=np.column_stack((xy,FLOOR+height*8.3));local=world-np.array(root.location)
    nx=len(x);ny=len(y);faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
    land=bpy.data.objects['AS_valley_landform'];old=land.data;me=bpy.data.meshes.new('190 shared fork terrain')
    me.from_pydata(local.tolist(),[],faces);me.update()
    for mat in old.materials:me.materials.append(mat.copy())
    for face in me.polygons:face.use_smooth=True
    attr=me.attributes.new('MF190_road_distance','FLOAT','POINT');attr.data.foreach_set('value',(dist*8.3).astype(np.float32))
    land.data=me;land.hide_render=False
    for mat in me.materials:
        node=mat.node_tree.nodes.new('ShaderNodeAttribute');node.attribute_name='MF190_road_distance'
        for n in list(mat.node_tree.nodes):
            if n.type=='MAP_RANGE' and abs(n.inputs['From Min'].default_value-15)<1e-5 and abs(n.inputs['From Max'].default_value-26)<1e-5:
                mat.node_tree.links.new(node.outputs['Fac'],n.inputs['Value'])
    # Seat retained nearby props on the changed ground; clear traversable road.
    embedding={}
    for ob in scene.objects:
        if ob.parent!=root or ob==land or ob.name=='MF188_distant_art_arc' or ob.hide_render:continue
        if ob.type!='MESH' or ob.name.startswith('MF189_roadside'):continue
        embedding[ob.name]=ob.location.z-bank_height(ob.location.x,ob.location.y)
        location=np.array(ob.matrix_world.translation);h,d=fields(((location[:2]-[0,.2])/8.3)[None],route)
        if d[0]<3.1:ob.hide_render=True;continue
        ob.location.z=FLOOR+h[0]*8.3+embedding[ob.name]
    # Reuse existing rocky forms and vegetation for the new branch. Instances
    # preserve the admitted materials, not newly invented asset dependencies.
    candidates=[o for o in scene.objects if o.parent==root and o.type=='MESH' and o.name.startswith(('AS_stone_','MF188_bank_','MF188_grove_'))]
    rng=np.random.default_rng(19018);created=0
    if candidates:
        for i in range(260):
            source=candidates[int(rng.integers(len(candidates)))];t=int(rng.integers(20,193));center=route['position'][t*8,:2]
            angle=route['heading'][t*8];side=np.array([np.cos(angle),np.sin(angle)]);side*=rng.choice([-1,1])*rng.uniform(3.4,14)
            xy_m=center+side;h,d=fields(xy_m[None],route)
            if d[0]<3.1:continue
            ob=source.copy();ob.data=source.data;ob.animation_data_clear();ob.name='MF190_route_dressing_'+str(i);scene.collection.objects.link(ob);ob.parent=root
            ob.location=(xy_m[0]*8.3,xy_m[1]*8.3+.2-root.location.y,FLOOR+h[0]*8.3+embedding.get(source.name,0.))
            ob.rotation_euler.z+=float(rng.uniform(-math.pi,math.pi));ob.hide_render=False;created+=1
    # A nonspecific timber obstruction establishes the route choice without
    # inventing uniforms, weapons, flags or a mission affiliation.
    mat=bpy.data.materials.new('190 weathered provisional timber');mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.11,.062,.028,1);bsdf.inputs['Roughness'].default_value=.9
    barrier=[]
    for a,b,r in [((-21,-373,FLOOR),( -21,-373,FLOOR+12),.65),((21,-373,FLOOR),(21,-373,FLOOR+12),.65),((-24,-373,FLOOR+10),(24,-373,FLOOR+10),.7),((-24,-373,FLOOR+4),(24,-373,FLOOR+4),.6)]:
        a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=(b-a).length,location=(a+b)/2)
        ob=bpy.context.object;ob.name='MF190_provisional_timber_barrier';ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();ob.data.materials.append(mat);barrier.append(ob.name)
    return {'terrain_vertices':len(world),'route_instances':created,'barrier_objects':barrier,'barrier_status':'Provisional neutral obstruction; armed guards/affiliation/mission facts not designed',
        'near_route_contact':'Same tangent-plane grade as the horse contact model; rendered-mesh ray verification still required','visual_gate':'NOT_RUN'}
