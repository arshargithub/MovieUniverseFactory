"""Deterministic screen-scale terrain and continuous trailing dust design."""
import math


def plume_width(y):
    return 3.2 + 22.0 * max(0., min(1., y / 200.)) ** .7


def dust(scene):
    """Continuous widening wake, not separate stationary smoke puffs.

    Authored advected volume field, not a fluid or calibrated particle solve.
    """
    import bpy
    from entrance_astra_world import mesh_object, FLOOR
    for ob in scene.objects:
        if ob.name.startswith('MF188_dust_'):ob.hide_render=True
    mat=bpy.data.materials.new('MF189 continuous ochre dust');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links;n.clear()
    def scalar(op,a,b=None):
        node=n.new('ShaderNodeMath');node.operation=op
        for i,v in enumerate((a,b) if b is not None else (a,)):
            if isinstance(v,(int,float)):node.inputs[i].default_value=v
            else:l.new(v,node.inputs[i])
        return node.outputs[0]
    coord=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ')
    l.new(coord.outputs['Generated'],sep.inputs[0])
    y=sep.outputs['Y'];x=scalar('MULTIPLY',scalar('SUBTRACT',sep.outputs['X'],.5),64)
    width=scalar('ADD',3.2,scalar('MULTIPLY',22,scalar('POWER',y,.7)))
    radial=scalar('DIVIDE',x,width)
    # Vertical column expands and rises with trail age; no hard hovering floor.
    z=scalar('MULTIPLY',sep.outputs['Z'],38)
    height=scalar('ADD',3.,scalar('MULTIPLY',35,scalar('POWER',y,.5)))
    vertical=scalar('DIVIDE',scalar('SUBTRACT',z,scalar('MULTIPLY',height,.24)),height)
    dist=scalar('ADD',scalar('MULTIPLY',radial,radial),scalar('MULTIPLY',vertical,vertical))
    fall=scalar('POWER',scalar('MAXIMUM',scalar('SUBTRACT',1,dist),0),2)
    near=scalar('MINIMUM',1,scalar('MULTIPLY',y,35))
    far=scalar('POWER',scalar('MAXIMUM',scalar('SUBTRACT',1,y),0),1.5)
    mapping=n.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(3.5,22,4.5)
    l.new(coord.outputs['Generated'],mapping.inputs[0])
    # Ground-relative advection in the horse-stationary coordinate convention.
    for f in (217,360):
        mapping.inputs['Location'].default_value=(0,-(f-217)/24*8.5,0)
        mapping.inputs['Location'].keyframe_insert(data_path='default_value',frame=f)
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.2
    noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.7
    l.new(mapping.outputs[0],noise.inputs['Vector'])
    turbulence=scalar('POWER',noise.outputs['Fac'],1.4)
    density=scalar('MULTIPLY',scalar('MULTIPLY',fall,near),scalar('MULTIPLY',far,turbulence))
    density=scalar('MULTIPLY',density,.20)
    volume=n.new('ShaderNodeVolumePrincipled');volume.inputs['Color'].default_value=(.95,.85,.65,1)
    volume.inputs['Anisotropy'].default_value=.28;l.new(density,volume.inputs['Density'])
    # Art-directed low-level in-scattering lift, density-bound so the volume
    # bounds never glow. This is a declared look treatment, not calibrated dust.
    volume.inputs['Emission Color'].default_value=(.65,.43,.20,1)
    l.new(scalar('MULTIPLY',density,.65),volume.inputs['Emission Strength'])
    out=n.new('ShaderNodeOutputMaterial');l.new(volume.outputs[0],out.inputs['Volume'])
    verts=[(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]
    faces=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
    ob=mesh_object('MF189_continuous_trailing_dust',verts,faces,scene.collection)
    ob.location=(0,108,FLOOR+19);ob.scale=(32,104,19);ob.data.materials.append(mat)
    return {'representation':'Single widening, advected heterogeneous volume; not fluid simulation',
            'trail_length_native':208,'peak_density_parameter':.20,'density_bound_art_light_lift':True,'source_dust_preserved_hidden':True}


def terrain(scene):
    import bpy
    import numpy as np
    from entrance_astra_world import mesh_object
    from entrance188_ground import bank_height
    ob=bpy.data.objects['AS_valley_landform'];mat=ob.data.materials[0].copy()
    mat.name='MF189 earth with visible aggregate';ob.data.materials[0]=mat
    n,l=mat.node_tree.nodes,mat.node_tree.links
    bsdf=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    coord=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=.65;noise.inputs['Detail'].default_value=4
    noise.inputs['Roughness'].default_value=.8;l.new(coord.outputs['Object'],noise.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.32
    ramp.color_ramp.elements[0].color=(.31,.25,.18,1)
    ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=(1,.94,.83,1)
    l.new(noise.outputs['Fac'],ramp.inputs[0])
    old=bsdf.inputs['Base Color'].links[0].from_socket
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.62
    l.new(old,mix.inputs[1]);l.new(ramp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bsdf.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.4;bump.inputs['Distance'].default_value=.12
    l.new(noise.outputs['Fac'],bump.inputs['Height'])
    if bsdf.inputs['Normal'].is_linked:l.new(bsdf.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
    l.new(bump.outputs[0],bsdf.inputs['Normal'])
    # One batched mesh for roadside gravel. Keep central hoof corridor unchanged.
    rng=np.random.default_rng(18901);verts=[];faces=[]
    proto=np.array([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)])
    tris=[(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)]
    for i in range(5200):
        x=float(rng.uniform(-150,150));y=float(rng.uniform(-650,140))
        if abs(x)<13 or rng.random()>.65+.25*math.sin(y/11+x/8):continue
        s=float(rng.uniform(.09,.48));p=proto*np.array((s,s*rng.uniform(.65,1.6),s*.45))
        theta=rng.uniform(0,math.tau);c,sn=math.cos(theta),math.sin(theta)
        p[:,:2]=p[:,:2]@np.array(((c,-sn),(sn,c)))
        p+=np.array((x,y,bank_height(x,y)+.04))
        start=len(verts);verts.extend(p.tolist());faces.extend(tuple(start+j for j in f) for f in tris)
    stones=mesh_object('MF189_roadside_aggregate',verts,faces,scene.collection,bpy.data.objects['AS_world_travel'])
    rock=bpy.data.materials.new('MF189 dusty gravel');rock.use_nodes=True
    shader=rock.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.17,.12,.065,1)
    shader.inputs['Roughness'].default_value=.95;stones.data.materials.append(rock)
    return {'gravel_count':len(verts)//6,'central_corridor_native':26,'ground_geometry_unchanged':True}
