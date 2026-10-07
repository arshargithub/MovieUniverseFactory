"""Purpose-built distant matte with native near ground and dust; scoped corridor."""
import math
from pathlib import Path


def backdrop(scene, image_path):
    import bpy
    from entrance_astra_world import FLOOR,mesh_object
    col=bpy.data.collections['AS_composed_ochre_valley']
    root=bpy.data.objects['AS_world_travel']
    mat=bpy.data.materials.new('MF188_purpose_built_mountain_art');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links;n.clear()
    output=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');tex=n.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(image_path),check_existing=True)
    l.new(tex.outputs['Color'],em.inputs['Color']);l.new(em.outputs[0],output.inputs['Surface'])
    points=[];faces=[];segments=160
    for i in range(segments+1):
        angle=math.radians(-20+140*i/segments)
        points.extend([(math.cos(angle)*4000,math.sin(angle)*4000,FLOOR-500),
                       (math.cos(angle)*4000,math.sin(angle)*4000,FLOOR+2500)])
    for i in range(segments):faces.append((2*i,2*i+2,2*i+3,2*i+1))
    ob=mesh_object('MF188_distant_art_arc',points,faces,col,root);ob.data.materials.append(mat)
    uv=ob.data.uv_layers.new(name='Unrepeated purpose-built panorama')
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            vi=ob.data.loops[li].vertex_index
            uv.data[li].uv=((vi//2)/segments,vi%2)
    ob.visible_shadow=False;ob.visible_diffuse=False;ob.visible_glossy=False
    scene.camera.data.clip_end=12000
    return {'image':str(image_path),'arc_degrees':140,'radius_native':4000,
            'repeat_or_mirroring':False,'scope':'Finite-depth shot corridor, not full 3D mountain geography'}


def ground_material(scene):
    import bpy
    mat=bpy.data.materials.new('MF188_ochre_earth_nonrepeating');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links
    bsdf=n.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.93
    coord=n.new('ShaderNodeTexCoord')
    large=n.new('ShaderNodeTexNoise');large.inputs['Scale'].default_value=.026;large.inputs['Detail'].default_value=3
    l.new(coord.outputs['Object'],large.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.20,.115,.043,1);ramp.color_ramp.elements[1].color=(.52,.34,.15,1)
    l.new(large.outputs['Fac'],ramp.inputs[0])
    fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=3.5;fine.inputs['Detail'].default_value=3
    l.new(coord.outputs['Object'],fine.inputs['Vector'])
    grain=n.new('ShaderNodeValToRGB');grain.color_ramp.elements[0].color=(.58,.50,.36,1);grain.color_ramp.elements[1].color=(1,1,1,1)
    l.new(fine.outputs['Fac'],grain.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.40
    l.new(ramp.outputs[0],mix.inputs[1]);l.new(grain.outputs[0],mix.inputs[2])
    sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Object'],sep.inputs[0])
    absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE';l.new(sep.outputs['X'],absolute.inputs[0])
    road=n.new('ShaderNodeMapRange');road.inputs['From Min'].default_value=15;road.inputs['From Max'].default_value=26;road.inputs['To Min'].default_value=.40;road.inputs['To Max'].default_value=0
    l.new(absolute.outputs[0],road.inputs['Value'])
    color=n.new('ShaderNodeMixRGB');l.new(road.outputs[0],color.inputs[0]);l.new(mix.outputs[0],color.inputs[1]);color.inputs[2].default_value=(.54,.365,.19,1)
    distance=n.new('ShaderNodeMapRange');distance.inputs['From Min'].default_value=100;distance.inputs['From Max'].default_value=1100;distance.inputs['To Max'].default_value=.64
    l.new(absolute.outputs[0],distance.inputs['Value'])
    haze=n.new('ShaderNodeMixRGB');l.new(distance.outputs[0],haze.inputs[0]);l.new(color.outputs[0],haze.inputs[1]);haze.inputs[2].default_value=(.29,.30,.27,1)
    l.new(haze.outputs[0],bsdf.inputs['Base Color'])
    # Purpose-built fine earth image, blended at incommensurate scales/angles.
    import entrance_astra as prior
    img=bpy.data.images.load(str(prior.ROOT/'.runtime/art-direction/series01-entrance-art188/earth-albedo-v01.png'),check_existing=True)
    texs=[]
    for scale_value,angle in ((.10,.0),(.071,.91)):
        mapping=n.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(scale_value,)*3;mapping.inputs['Rotation'].default_value=(0,0,angle)
        l.new(coord.outputs['Object'],mapping.inputs[0])
        tex=n.new('ShaderNodeTexImage');tex.image=img;tex.projection='BOX';tex.projection_blend=.25
        l.new(mapping.outputs[0],tex.inputs[0]);texs.append(tex)
    blend=n.new('ShaderNodeMixRGB');l.new(large.outputs['Fac'],blend.inputs[0]);l.new(texs[0].outputs['Color'],blend.inputs[1]);l.new(texs[1].outputs['Color'],blend.inputs[2])
    texture_mix=n.new('ShaderNodeMixRGB');texture_mix.blend_type='MULTIPLY';texture_mix.inputs[0].default_value=.55
    l.new(haze.outputs[0],texture_mix.inputs[1]);l.new(blend.outputs[0],texture_mix.inputs[2]);l.new(texture_mix.outputs[0],bsdf.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.26;bump.inputs['Distance'].default_value=.055
    l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bsdf.inputs['Normal'])
    ob=bpy.data.objects['AS_valley_landform'];ob.data.materials.clear();ob.data.materials.append(mat)
    from entrance_astra_world import FLOOR
    for v in ob.data.vertices:v.co.z=FLOOR+(v.co.z-FLOOR)*.22
    ob.data.update()
    # Replace uniform scatter with separated groves and quiet route margins.
    hidden=0
    for ob in scene.objects:
        if ob.name.startswith(('AS_far_ridge','AS_outcrop')):ob.hide_render=True
        if ob.name.startswith(('AS_pine_','AS_scrub_','AS_grass_')) and ob.parent:
            x,y=ob.location.x,ob.location.y
            cluster=math.sin(y/65+math.sin(x/40)*1.7)+.65*math.cos(y/127+x/47)
            if cluster<.12 or (ob.name.startswith('AS_pine_') and abs(x)<65):
                ob.hide_render=True;hidden+=1
        if ob.name.startswith('AS_stone_'):
            # Bury cut scan bases and break repeated upright block silhouettes.
            ob.rotation_euler.x=.20*math.sin(ob.location.y)
            ob.rotation_euler.y=.24*math.cos(ob.location.x)
            ob.scale.z*=.70
    # Keep all placed pieces seated after the terrain relief reduction.
    for ob in scene.objects:
        if ob.parent and ob.name.startswith(('AS_pine_','AS_scrub_','AS_grass_','AS_stone_')):
            from entrance_astra_world import terrain_height
            ob.location.z-=(terrain_height(ob.location.x,ob.location.y)-FLOOR)*.78
    return {'dual_scale_ground_texture':True,'cluster_culled_instances':hidden}


def dust(scene):
    import bpy
    from entrance_astra_world import FLOOR
    mat=bpy.data.materials.new('MF188_dry_hoof_dust');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links;n.clear()
    out=n.new('ShaderNodeOutputMaterial');volume=n.new('ShaderNodeVolumePrincipled')
    volume.inputs['Color'].default_value=(.94,.84,.65,1);volume.inputs['Anisotropy'].default_value=.25
    l.new(volume.outputs['Volume'],out.inputs['Volume'])
    coord=n.new('ShaderNodeTexCoord');sub=n.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,.5)
    l.new(coord.outputs['Generated'],sub.inputs[0])
    length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';l.new(sub.outputs[0],length.inputs[0])
    fall=n.new('ShaderNodeMapRange');fall.inputs['From Min'].default_value=.12;fall.inputs['From Max'].default_value=.5;fall.inputs['To Min'].default_value=.14;fall.inputs['To Max'].default_value=0
    l.new(length.outputs['Value'],fall.inputs['Value'])
    noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=8;noise.inputs['Detail'].default_value=3
    l.new(coord.outputs['Generated'],noise.inputs['Vector'])
    noise.inputs['W'].default_value=0;noise.inputs['W'].keyframe_insert(data_path='default_value',frame=217)
    noise.inputs['W'].default_value=1.7;noise.inputs['W'].keyframe_insert(data_path='default_value',frame=360)
    mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(fall.outputs[0],mul.inputs[0]);l.new(noise.outputs['Fac'],mul.inputs[1]);l.new(mul.outputs[0],volume.inputs['Density'])
    for i in range(9):
        from entrance_astra_world import mesh_object
        vertices=[(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]
        faces=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
        ob=mesh_object('MF188_dust_'+str(i),vertices,[tuple(reversed(face)) for face in faces],scene.collection)
        ob.location=(math.sin(i*2.3)*(1+i*.45),5+i*6,FLOOR+1+i*.35)
        ob.scale=(2+i*.60,5+i*.8,1.6+i*.5);ob.data.materials.append(mat)
    return {'representation':'Nine soft bounded native volumes, shot-limited advected look, not fluid dynamics'}


def build(scene,out):
    import entrance_astra as prior
    import entrance_astra_world as world
    result=world.world(scene)
    result['ground_art']=ground_material(scene)
    image_path=prior.ROOT/'.runtime/art-direction/series01-entrance-art188/mountain-matte-v01.png'
    result['matte']=backdrop(scene,image_path)
    result['matte']['sha256']=prior.prior.actor.base.digest(image_path)
    result['dust']=dust(scene)
    (out/'entrance188_world.py').write_bytes(Path(__file__).read_bytes())
    return result


def trail_height(x,y):
    from entrance_astra_world import FLOOR
    # Broad usable trail; banks have actual relief without blocking the lateral camera.
    bank=max(0.,min(1.,(abs(x)-12)/35))
    bank=bank*bank*(3-2*bank)
    return FLOOR+bank*((7 if x<0 else 17)+2.5*math.sin(y/47)+2*math.sin(y/21+x/24))


def corridor(scene,out):
    """Replace failed uniform field rather than patching its scatter again."""
    import bpy
    import random
    import entrance_astra as prior
    import entrance_astra_world as helpers
    from entrance_astra_world import mesh_object,instance,FLOOR,SPEED
    col=bpy.data.collections.new('AS_composed_ochre_valley');scene.collection.children.link(col)
    root=bpy.data.objects.new('AS_world_travel',None);col.objects.link(root)
    for ob in scene.objects:
        if ob.type=='MESH' and ('floor' in ob.name.lower() or 'ground' in ob.name.lower()):ob.hide_render=True
    xs=list(range(-1200,-120,40))+list(range(-120,121,4))+list(range(160,1201,40))
    nx,ny=len(xs),181;points=[];faces=[]
    for j in range(ny):
        y=-1500+j*15
        for i in range(nx):
            x=xs[i];points.append((x,y,trail_height(x,y)))
    for j in range(ny-1):
        for i in range(nx-1):
            a=j*nx+i;faces.append((a,a+1,a+nx+1,a+nx))
    land=mesh_object('AS_valley_landform',points,faces,col,root)
    for face in land.data.polygons:face.use_smooth=True
    ground_material(scene)
    # ground_material's old-landform reduction is not part of this authored corridor.
    for vertex,point in zip(land.data.vertices,points):vertex.co=point
    land.data.update()
    ground=land.data.materials[0];n,l=ground.node_tree.nodes,ground.node_tree.links
    coord=next(node for node in n if node.type=='TEX_COORD')
    distance=n.new('ShaderNodeVectorMath');distance.operation='LENGTH';l.new(coord.outputs['Object'],distance.inputs[0])
    fade=n.new('ShaderNodeMapRange');fade.inputs['From Min'].default_value=650;fade.inputs['From Max'].default_value=1150
    l.new(distance.outputs['Value'],fade.inputs['Value'])
    transparent=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader')
    bsdf=n.get('Principled BSDF');output=n.get('Material Output')
    l.new(fade.outputs[0],mix.inputs[0]);l.new(bsdf.outputs[0],mix.inputs[1]);l.new(transparent.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],output.inputs['Surface'])
    rocks=helpers.source_meshes('namaqualand_boulder_03',col)
    trees=helpers.source_meshes('pine_sapling_small',col)
    shrubs=helpers.source_meshes('shrub_02',col)
    grass=helpers.grass_mesh(col)
    rng=random.Random(18805)
    # Intentional banks and groves, with the moving left-side camera corridor kept clear.
    for i in range(150):
        y=rng.uniform(-1300,800);side=-1 if i%3==0 else 1
        x=side*rng.uniform(34,110)
        if side<0 and -650<y<160:x=-rng.uniform(145,210)
        for member in range(3):
            xx=x+rng.uniform(-5,5);yy=y+rng.uniform(-7,7)
            ob=instance('MF188_grove_%03d_%s'%(i,member),trees[(i+member)%len(trees)],col,root,(xx,yy,trail_height(xx,yy)),rng.uniform(1.8,3.2),rng.random()*math.tau)
            ob.scale.x*=1.7;ob.scale.y*=1.7
    for i in range(1250):
        y=rng.uniform(-1350,850);x=(-1 if i%2 else 1)*rng.uniform(16,150)
        size=rng.uniform(.04,.20)
        if i%12==0:size=rng.uniform(.42,.95)
        ob=instance('MF188_bank_stone_%04d'%i,rocks[0],col,root,(x,y,trail_height(x,y)-size*3),size,rng.random()*math.tau)
        ob.rotation_euler.x=rng.uniform(.7,2.0);ob.rotation_euler.y=rng.uniform(-.5,.5)
    for kind,count,meshes in (('scrub',1300,shrubs),('grass',7500,[grass])):
        for i in range(count):
            y=rng.uniform(-1350,850);x=(-1 if i%2 else 1)*rng.uniform(14,130)
            if math.sin(y/37+x/23)<-.55:continue
            size=rng.uniform(.18,.5) if kind=='scrub' else rng.uniform(.8,1.6)
            instance('MF188_bank_'+kind+'_'+str(i),meshes[i%len(meshes)],col,root,(x,y,trail_height(x,y)),size,rng.random()*math.tau)
    root.location=(0,0,0);root.keyframe_insert(data_path='location',frame=217)
    root.location.y=SPEED*143/24;root.keyframe_insert(data_path='location',frame=360)
    for layer in root.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for key in fc.keyframe_points:key.interpolation='LINEAR'
    world=bpy.data.worlds.new('MF188_mountain_day');world.use_nodes=True;scene.world=world
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.45,.56,.66,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
    sun=bpy.data.lights.new('MF188_afternoon_sun','SUN');sun.energy=2.4;sun.angle=.065;sun.color=(1,.85,.67)
    ob=bpy.data.objects.new(sun.name,sun);col.objects.link(ob);ob.rotation_euler=(.52,-.62,-.65)
    image_path=prior.ROOT/'.runtime/art-direction/series01-entrance-art188/mountain-matte-v01.png'
    result={'method':'Composed native trail corridor, original field replaced','matte':backdrop(scene,image_path),'dust':dust(scene)}
    (out/'entrance188_world.py').write_bytes(Path(__file__).read_bytes())
    return result
