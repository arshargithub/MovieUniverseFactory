"""Shot-limited existing-art matte control; no generation or new imagery."""
import math


def backdrop(scene):
    import bpy
    import entrance_astra as job
    from entrance_astra_world import FLOOR,mesh_object
    previous_clip=scene.camera.data.clip_end
    scene.camera.data.clip_end=10000
    image=job.ROOT/'.runtime/art-direction/series01-entrances-v04/C-illustrated-landscape.png'
    # Top-left mountains only, excluding people/cloth/buildings/horse.
    mat=bpy.data.materials.new('AS_existing_illustrated_mountain_matte');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links;n.clear()
    output=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');tex=n.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(image),check_existing=True);tex.interpolation='Linear'
    l.new(tex.outputs['Color'],em.inputs['Color']);l.new(em.outputs[0],output.inputs['Surface'])
    col=bpy.data.collections['AS_composed_ochre_valley'];root=bpy.data.objects['AS_world_travel']
    for sector in range(4):
        p=[];f=[]
        for i in range(49):
            a=math.tau*(sector+i/48)/4
            p.extend([(math.cos(a)*3000,math.sin(a)*3000,FLOOR-200),
                      (math.cos(a)*3000,math.sin(a)*3000,FLOOR+1400)])
        for i in range(48):f.append((i*2,i*2+2,i*2+3,i*2+1))
        ob=mesh_object('AS_art_matte_'+str(sector),p,f,col,root);ob.data.materials.append(mat)
        layer=ob.data.uv_layers.new(name='Approved art crop')
        for poly in ob.data.polygons:
            for li in poly.loop_indices:
                vi=ob.data.loops[li].vertex_index;t=(vi//2)/48
                if sector%2:t=1-t
                layer.data[li].uv=(.002+t*.322,.813+(vi%2)*.185)
        ob.visible_shadow=False;ob.visible_diffuse=False;ob.visible_glossy=False
    for ob in scene.objects:
        if ob.name.startswith(('AS_far_ridge','AS_outcrop')):ob.hide_render=True
    return {'previous_camera_clip_end':previous_clip,'camera_clip_end':scene.camera.data.clip_end,'matte_source':str(image.relative_to(job.ROOT)), 'uv_crop':[.002,.813,.324,.998],
            'limitations':['Finite-depth reused concept-art crop, not complete geography','Repeated source landmarks require full-camera review']}


def mane(scene,out):
    import bpy
    import numpy as np
    import entrance_astra as job
    from entrance_astra_world import mesh_object
    from wardrobe_shawl180_cache import cache
    source=job.BASE/'entrance-astra-mane-cache01/samples.npz'
    a=np.load(source)['points']
    if a.shape!=(144,1047,6,3) or not np.isfinite(a).all():raise ValueError('Mane samples invalid')
    # Restore actual donor short groom first, not invented long wind motion.
    tang=np.gradient(a,axis=2);tang/=np.maximum(np.linalg.norm(tang,axis=-1,keepdims=True),1e-8)
    u=np.cross(tang,np.array([1.,0,0]));u/=np.maximum(np.linalg.norm(u,axis=-1,keepdims=True),1e-8)
    v=np.cross(tang,u);radii=np.linspace(.018,.002,6)[None,None,:,None]
    points=np.stack([a+u*radii,a+v*radii,a-u*radii,a-v*radii],axis=3).reshape(144,-1,3).astype(np.float32)
    faces=[]
    for hair in range(1047):
        for k in range(5):
            for s in range(4):
                i=hair*24+k*4;faces.append((i+s,i+(s+1)%4,i+4+(s+1)%4,i+4+s))
    ob=mesh_object('AS_recovered_native_mane',points[0].tolist(),faces,scene.collection);ob.location.z=-1.05
    mat=bpy.data.materials.new('AS_native_mane_brown');mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.018,.009,.004,1);bsdf.inputs['Roughness'].default_value=.55
    ob.data.materials.append(mat)
    mod=cache(ob,points,out/'mane.mdd');mod.frame_start=217
    return {'source_sha256':job.prior.actor.base.digest(source),'cache_sha256':job.prior.actor.base.digest(out/'mane.mdd'),
            'guides':1047,'scope':'Recovered donor short groom, no new wind simulation or hairstyle acceptance'}
