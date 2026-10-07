"""Composed native valley with scanned-source forms and a fixed art proof."""
import math
import random

FLOOR = -20.906909942626953
SPEED = 99.60000205


def terrain_height(x, y):
    from mathutils import noise, Vector
    edge = max(0., abs(x) - 170.)
    rise = min(1., edge / 900.)
    rise = rise * rise * (3 - 2 * rise)
    ridge = noise.ridged_multi_fractal(Vector((x / 400., y / 400., .45)), .9, 2.1, 5, 1., 2.)
    mass = 25 + 70 * min(2., ridge)
    return FLOOR + rise * mass


def mesh_object(name, points, faces, collection, root=None):
    import bpy
    data = bpy.data.meshes.new(name)
    data.from_pydata(points, [], faces)
    data.update()
    ob = bpy.data.objects.new(name, data)
    collection.objects.link(ob)
    ob.parent = root
    return ob


def palette_material(name, colors, image_path=None, tile=50.):
    import bpy
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    n,l = mat.node_tree.nodes,mat.node_tree.links
    bsdf=n.get('Principled BSDF'); bsdf.inputs['Roughness'].default_value=.88
    coord=n.new('ShaderNodeTexCoord')
    mapping=n.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=1/tile
    l.new(coord.outputs['Object'],mapping.inputs[0])
    if image_path:
        tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(image_path),check_existing=True)
        tex.projection='BOX';tex.projection_blend=.25;l.new(mapping.outputs[0],tex.inputs[0]);value=tex.outputs['Color']
    else:
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=1;tex.inputs['Detail'].default_value=4
        l.new(mapping.outputs[0],tex.inputs['Vector']);value=tex.outputs['Fac']
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='EASE'
    for i,(pos,color) in enumerate(colors):
        element = ramp.color_ramp.elements[i] if i<2 else ramp.color_ramp.elements.new(pos)
        element.position=pos;element.color=(*color,1)
    l.new(value,ramp.inputs[0]);l.new(ramp.outputs[0],bsdf.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.3;bump.inputs['Distance'].default_value=.13
    l.new(value,bump.inputs['Height']);l.new(bump.outputs[0],bsdf.inputs['Normal'])
    return mat,coord,ramp


def source_meshes(asset, col):
    import bpy
    import entrance_astra as job
    imported=job.import_asset(asset)
    rows=[]
    for ob in imported:
        data=ob.data.copy()
        transform=ob.matrix_world.copy();transform.translation=(0,0,0)
        data.transform(transform)
        zmin=min(v.co.z for v in data.vertices)
        for v in data.vertices:v.co.z-=zmin
        rows.append(data)
        bpy.data.objects.remove(ob,do_unlink=True)
    return rows


def instance(name,data,col,root,xyz,scale,angle):
    import bpy
    ob=bpy.data.objects.new(name,data);col.objects.link(ob);ob.parent=root
    ob.location=xyz;ob.scale=(scale,)*3;ob.rotation_euler[2]=angle
    return ob


def grass_mesh(col):
    import bpy
    rng=random.Random(602)
    p=[];f=[]
    for blade in range(38):
        x,y=rng.uniform(-1.2,1.2),rng.uniform(-1.2,1.2)
        a=rng.random()*math.tau;h=rng.uniform(.5,1.8);lean=rng.uniform(.3,1.1)
        start=len(p)
        for k in range(5):
            t=k/4;w=.07*(1-t)+.006
            for s in (-1,1):
                p.append((x+math.cos(a)*lean*t*t+s*w*math.sin(a),y+math.sin(a)*lean*t*t-s*w*math.cos(a),h*t))
        f.extend((start+k*2,start+k*2+1,start+k*2+3,start+k*2+2) for k in range(4))
    ob=mesh_object('AS_grass_template',p,f,col)
    mat,_,_=palette_material('AS_dry_grass',[(0,(.11,.085,.027)),(.55,(.38,.25,.07)),(1,(.67,.47,.19))],None,.7)
    ob.data.materials.append(mat);data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
    return data


def world(scene):
    import bpy
    from mathutils import Vector
    import entrance_astra as job
    col=bpy.data.collections.new('AS_composed_ochre_valley');scene.collection.children.link(col)
    root=bpy.data.objects.new('AS_world_travel',None);col.objects.link(root)
    for ob in scene.objects:
        if ob.type=='MESH' and ('floor' in ob.name.lower() or 'ground' in ob.name.lower()):
            ob.hide_render=True
    # Fine near-ground and coarse mountains are separate spatial scales.
    points=[];faces=[];nx=201;ny=201
    for j in range(ny):
        y=-1300+j*13
        for i in range(nx):
            x=-1300+i*13;points.append((x,y,terrain_height(x,y)))
    for j in range(ny-1):
        for i in range(nx-1):
            a=j*nx+i;faces.append((a,a+1,a+nx+1,a+nx))
    ground=mesh_object('AS_valley_landform',points,faces,col,root)
    for poly in ground.data.polygons:poly.use_smooth=True
    earth,coord,ramp=palette_material('AS_ochre_ground',[(.06,(.19,.115,.038)),(.25,(.35,.22,.072)),(.5,(.56,.36,.14)),(.8,(.72,.52,.28))],job.ASSETS/'rocks_ground_05/Diffuse.jpg',26)
    ground.data.materials.append(earth)
    n,l=earth.node_tree.nodes,earth.node_tree.links
    sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Object'],sep.inputs[0])
    absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE';l.new(sep.outputs['X'],absolute.inputs[0])
    mask=n.new('ShaderNodeMapRange');mask.inputs['From Min'].default_value=21;mask.inputs['From Max'].default_value=29
    mask.inputs['To Min'].default_value=0;mask.inputs['To Max'].default_value=1;l.new(absolute.outputs[0],mask.inputs['Value'])
    roadtex=n.new('ShaderNodeTexImage');roadtex.image=bpy.data.images.load(str(job.ASSETS/'rocks_ground_05/Diffuse.jpg'),check_existing=True);roadtex.projection='BOX';roadtex.projection_blend=.1
    scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/9
    l.new(coord.outputs['Object'],scale.inputs[0]);l.new(scale.outputs[0],roadtex.inputs[0])
    roadcolor=n.new('ShaderNodeValToRGB');roadcolor.color_ramp.elements[0].color=(.29,.20,.105,1);roadcolor.color_ramp.elements[1].color=(.74,.59,.38,1)
    l.new(roadtex.outputs['Color'],roadcolor.inputs[0])
    mix=n.new('ShaderNodeMixRGB');l.new(mask.outputs[0],mix.inputs[0]);l.new(roadcolor.outputs[0],mix.inputs[1]);l.new(ramp.outputs[0],mix.inputs[2])
    # Cool the distant ridges for depth instead of surrounding the rider with a giant brown bank.
    dist=n.new('ShaderNodeMapRange');dist.inputs['From Min'].default_value=180;dist.inputs['From Max'].default_value=1200;dist.inputs['To Max'].default_value=.8
    l.new(absolute.outputs[0],dist.inputs['Value'])
    haze=n.new('ShaderNodeMixRGB');haze.inputs[2].default_value=(.22,.30,.36,1)
    l.new(dist.outputs[0],haze.inputs[0]);l.new(mix.outputs[0],haze.inputs[1]);l.new(haze.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
    rng=random.Random(18704)
    rocks=source_meshes('namaqualand_boulder_03',col)
    cliffs=source_meshes('rock_face_01',col)
    trees=source_meshes('pine_sapling_small',col)
    shrubs=source_meshes('shrub_02',col)
    # Use the scanned silhouettes and source texture variation, not primitive polyhedra.
    grasses=[grass_mesh(col)]
    for count,data_list,kind in ((1700,rocks,'stone'),(22,cliffs,'outcrop'),(640,trees,'pine'),(1000,shrubs,'scrub'),(7200,grasses,'grass')):
        for i in range(count):
            y=rng.uniform(-1150,850)
            sign=1 if i%2 else -1
            x=sign*rng.uniform(29,160 if kind in ('grass','pine','scrub') else 360)
            # Keep the camera's close approach free and foreground plants at natural scale.
            if -135<x<-40 and -100<y<100:x-=70
            if kind=='stone':size=rng.uniform(.035,.20) if i%15 else rng.uniform(.4,1.1)
            elif kind=='outcrop':size=rng.uniform(.6,1.6);x=sign*rng.uniform(250,700)
            elif kind=='pine':size=rng.uniform(1.4,3.3) if abs(x)>70 else rng.uniform(.6,1.4)
            elif kind=='grass':size=rng.uniform(.65,1.4)
            else:size=rng.uniform(.10,.38)
            z=terrain_height(x,y)-(size*3 if kind in ('stone','outcrop') else .03)
            instance('AS_'+kind+'_%03d'%i,data_list[i%len(data_list)],col,root,(x,y,z),size,rng.random()*math.tau)
    # The far horizon retains 3D parallax and is deliberately lower contrast.
    far_mat,_,_=palette_material('AS_distant_slate',[(0,(.17,.24,.31)),(1,(.36,.43,.49))],None,140)
    for side in (-1,1):
        pts=[];fs=[]
        for j in range(81):
            y=-3500+j*87.5
            for i in range(23):
                x=side*(1200+i*110)
                peak=650+230*math.sin(y/330+.8)**2+140*math.cos(y/180)
                z=FLOOR+max(0,1-abs(i-9)/12)*peak
                pts.append((x,y,z))
        for j in range(80):
            for i in range(22):
                a=j*23+i;fs.append((a,a+1,a+24,a+23))
        ob=mesh_object('AS_far_ridge_'+str(side),pts,fs,col,root);ob.data.materials.append(far_mat)
    root.location=(0,0,0);root.keyframe_insert(data_path='location',frame=217)
    root.location.y=SPEED*143/24;root.keyframe_insert(data_path='location',frame=360)
    for layer in root.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
    world=bpy.data.worlds.new('AS_open_sky');world.use_nodes=True;scene.world=world
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.45,.57,.69,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
    sun=bpy.data.lights.new('AS_late_day_sun','SUN');sun.energy=2.0;sun.angle=.065;sun.color=(1,.85,.67)
    ob=bpy.data.objects.new(sun.name,sun);col.objects.link(ob);ob.rotation_euler=(.52,-.62,-.65)
    # Keep186's broad actor fill; no resculpt to accommodate outdoor light.
    leather,_,_=palette_material('AS_tack_worn_leather',[(0,(.025,.012,.005)),(1,(.15,.07,.025))],None,2)
    for ob in scene.objects:
        if ob.name.startswith('MF185_gait_') and any(s in ob.name for s in ('bridle','strap')):
            ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(leather)
            for poly in ob.data.polygons:poly.material_index=0
    return {'native_landform_vertices':len(points),'source_assets':['rock_face_01','namaqualand_boulder_03','pine_sapling_small','shrub_02'],
            'ground_z':FLOOR,'world_speed_native_per_second':SPEED}


def camera(scene,rig,frame):
    from mathutils import Vector
    from demo_reuse import camera_offset
    t=(frame-217)/143
    profile={'path_interpolation':'continuous','offset_start':[0,85,175],'offset_end':[-8,-19,3.4],
             'camera_path':[{'at':0.,'offset':[0,85,175]},{'at':.34,'offset':[-65,36,45]},
                            {'at':.64,'offset':[-110,0,8]},{'at':1.,'offset':[-8,-19,3.4]}]}
    q=max(0,min(1,(t-.64)/.36));q=q*q*(3-2*q)
    head=rig.matrix_world@rig.pose.bones['MF185_head'].head
    target=Vector((0,-.5,-8.5)).lerp(head+Vector((0,0,-.8)),q)
    cam=scene.camera;cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=24
    cam.data.lens=28+14*q;cam.data.dof.use_dof=False
    cam.location=target+Vector(camera_offset(profile,t));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    return {'frame':frame,'position':list(cam.location),'target':list(target),'lens':cam.data.lens}


def build_and_render(out):
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    scene=bpy.context.scene
    result=world(scene)
    if 'hybrid' in out.name:
        import entrance_astra_hybrid as hybrid
        from pathlib import Path
        (out/'hybrid-handler.py').write_bytes(Path(hybrid.__file__).read_bytes())
        result.update(hybrid.backdrop(scene));result['mane']=hybrid.mane(scene,out)
    scene.camera.animation_data_clear()
    keys=[]
    with render_geometry_paused():
        for frame in range(217,361):
            scene.frame_set(frame);bpy.context.view_layer.update()
            row=camera(scene,bpy.data.objects['MF_body156_fit_rig'],frame)
            ground=terrain_height(row['position'][0],row['position'][1]-SPEED*(frame-217)/24)
            row['terrain_clearance']=row['position'][2]-ground
            if row['terrain_clearance']<2:raise ValueError('Camera crosses terrain')
            keys.append(row)
            for prop in ('location','rotation_euler'):scene.camera.keyframe_insert(data_path=prop,frame=frame)
            scene.camera.data.keyframe_insert(data_path='lens',frame=frame)
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=True
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.render.use_persistent_data=True
    for frame in (217,265,309,360):
        scene.frame_set(frame);bpy.context.view_layer.update();scene.render.filepath=str(out/('frame-%04d.png'%frame))
        bpy.ops.render.render(write_still=True);print('Art proof frame',frame,flush=True)
    result.update({'camera_keys':keys,'visual_gate':'NOT_RUN','native_saved':False,
                   'scope':'Illustrated environment proof; no final footage or Director acceptance'})
    return result
