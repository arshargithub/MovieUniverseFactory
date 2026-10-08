"""Refine the same analytic terrain, preserving planting and the flat hoof corridor."""
import numpy as np


def bank_height(x,y):
    import math
    from entrance_astra_world import FLOOR
    from entrance188_world import trail_height
    if x>=0:return trail_height(x,y)
    width=60+8*math.sin(y/63)
    bank=max(0.,min(1.,(-x-12)/width));bank=bank*bank*(3-2*bank)
    return FLOOR+bank*(1.4+.6*math.sin(y/47)+.4*math.cos(y/29))


def repair_bank(scene):
    import bpy
    from entrance188_world import trail_height
    land=bpy.data.objects['AS_valley_landform'];changed=0
    for v in land.data.vertices:v.co.z=bank_height(v.co.x,v.co.y)
    land.data.update()
    for ob in scene.objects:
        if ob.name.startswith(('MF188_bank_','MF188_grove_')) and ob.location.x<0:
            x,y=ob.location.x,ob.location.y
            ob.location.z+=bank_height(x,y)-trail_height(x,y);changed+=1
    return {'method':'Low rolling near-side bank, same flat hoof corridor and far bank; props reseated by analytic height delta',
            'reseated_objects':changed,'left_bank_height_above_floor_max_native':2.4,
            'actor_camera_lighting_materials_unchanged':True}


def geometry():
    from entrance188_world import trail_height
    xs=list(range(-1200,-120,40))+list(range(-120,121,2))+list(range(160,1201,40))
    ys=range(-1500,1201,3)
    points=np.array([(x,y,trail_height(x,y)) for y in ys for x in xs],dtype=np.float32)
    nx=len(xs);ny=len(ys)
    faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
    return points,faces


def refine(scene):
    import bpy
    ob=bpy.data.objects['AS_valley_landform'];old=ob.data
    points,faces=geometry()
    mesh=bpy.data.meshes.new('MF188_continuous_analytic_terrain')
    mesh.from_pydata(points.tolist(),[],faces);mesh.update()
    for material in old.materials:mesh.materials.append(material)
    for poly in mesh.polygons:poly.use_smooth=True
    ob.data=mesh
    return {'old_vertices':len(old.vertices),'new_vertices':len(mesh.vertices),
            'near_spacing_native':[2,3],'camera_clip_start':scene.camera.data.clip_start,
            'method':'Same analytic height field sampled more densely; no changed material, light, camera, actor or asset placement',
            'visual_gate':'NOT_RUN'}


def controls(scene,out):
    import bpy
    scene.cycles.device='CPU';scene.render.use_persistent_data=True
    scene.render.resolution_x=288;scene.render.resolution_y=512;scene.cycles.samples=8
    scene.frame_set(325);bpy.context.view_layer.update()
    ob=bpy.data.objects['AS_valley_landform'];mat=ob.data.materials[0]
    n,l=mat.node_tree.nodes,mat.node_tree.links
    bsdf=n.get('Principled BSDF');output=n.get('Material Output')
    source=bsdf.inputs['Base Color'].links[0].from_socket
    emission=n.new('ShaderNodeEmission');l.new(source,emission.inputs['Color']);l.new(emission.outputs[0],output.inputs['Surface'])
    scene.render.filepath=str(out/'unlit-color-0325.png');bpy.ops.render.render(write_still=True)
    clay=n.new('ShaderNodeBsdfPrincipled');clay.inputs['Base Color'].default_value=(.4,.3,.2,1);clay.inputs['Roughness'].default_value=1
    l.new(clay.outputs[0],output.inputs['Surface'])
    scene.render.filepath=str(out/'plain-lit-0325.png');bpy.ops.render.render(write_still=True)
    return {'controls':['ground original base color with emission','constant rough ground shader with original lighting'],
            'camera_clip':[scene.camera.data.clip_start,scene.camera.data.clip_end],
            'scope':'Only ground shader changes; no native saved; visual diagnosis separate'}


def rays(scene):
    import bpy
    from mathutils import Vector
    for ob in scene.objects:ob.hide_viewport=ob.hide_render
    scene.frame_set(325);bpy.context.view_layer.update()
    camera=scene.camera;corners=camera.data.view_frame(scene=scene)
    lowx=min(v.x for v in corners);highx=max(v.x for v in corners)
    lowy=min(v.y for v in corners);highy=max(v.y for v in corners)
    transform=camera.matrix_world;origin=transform.translation
    deps=bpy.context.evaluated_depsgraph_get();rows=[]
    for y in (.65,.70,.72,.74,.76,.78,.80,.85,.90,.95):
        for x in (.25,.5,.75):
            direction=transform.to_3x3()@Vector((lowx+x*(highx-lowx),highy-y*(highy-lowy),corners[0].z));direction.normalize()
            hit,location,normal,index,ob,matrix=scene.ray_cast(deps,origin,direction,distance=12000)
            rows.append({'pixel_fraction':[x,y],'object':ob.name if hit else None,'point':list(location),'normal':list(normal),'face':index})
    large=[]
    for ob in scene.objects:
        if ob.hide_render:continue
        if ob.type=='EMPTY' and ob.instance_type=='COLLECTION':large.append({'instance':ob.name,'collection':ob.instance_collection.name})
        if ob.name.startswith(('MF188_bank_','MF188_grove_')) and max(ob.dimensions)>50:
            large.append({'object':ob.name,'dimensions':list(ob.dimensions),'vertices':len(ob.data.vertices)})
    return {'rays':rows,'large_props_or_collection_instances':large}
