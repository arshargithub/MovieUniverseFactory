"""Extend the existing trouser rise beneath the belt, preserving lower legs.

This is a reversible garment derivative, not an anatomical change or an
overlay hiding failed cloth. Contact caches must be renewed before selection.
"""
import json
from pathlib import Path
import numpy as np


def rise(points):
    p=np.asarray(points,dtype=float);t=np.clip((p[:,2]+6.8)/1.08,0,1)
    w=t*t*(3-2*t);q=p.copy();q[:,2]+=.60*w
    return q,w


def rise_fit(z):
    t=np.clip((np.asarray(z)+6.4)/.6,0,1);weight=t*t*(3-2*t)
    s=np.clip((np.asarray(z)+5.9)/.5,0,1);clearance=.075-.045*s*s*(3-2*s)
    return weight,clearance


def run(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import WORKING_SHA
    from wardrobe185_lower import fast_geometry,world_points
    from wardrobe_motion178_controls import bind_render_surface
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-finishreview01/integration-working.blend'
    if digest(source)!=WORKING_SHA:raise ValueError('Unbound trouser source')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    ob=bpy.data.objects['MF_fit_trousers_173_visible']
    deform=[m for m in ob.modifiers if m.type=='SURFACE_DEFORM']
    if len(deform)!=1 or any(m.type=='ARMATURE' for m in ob.modifiers):raise ValueError('Unexpected trouser deformation stack')
    target=deform[0].target;points=np.array([v.co[:] for v in ob.data.vertices])
    world=world_points(points,np.array(ob.matrix_world));proposed,weight=rise(world)
    lower_ids=np.flatnonzero(world[:,2]<-6.8)
    samples=(1,169,193,217,223,326,360);before={}
    # Compare the unchanged lower region through its existing deformation.
    flags=[(m,m.show_viewport) for m in ob.modifiers if m.type in ('SUBSURF','SOLIDIFY')]
    for m,_ in flags:m.show_viewport=False
    for frame in samples:
        scene.frame_set(frame);bpy.context.view_layer.update();p,_=fast_geometry(ob)
        if len(p)!=len(points):raise ValueError('Unexpected base trouser topology')
        before[frame]=p[lower_ids]
    scene.frame_set(1);bpy.context.view_layer.update()
    p,f=fast_geometry(bpy.data.objects['MF_studio_adult_body'])
    tri=p[f];f=f[(tri[:,:,2].max(1)>-6.9)&(tri[:,:,2].min(1)<-4.7)&(np.abs(tri[:,:,0]).max(1)<2.)]
    tree=BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True)
    fitted=out.name.endswith('lowerpants02')
    fit_weight,clearance=rise_fit(proposed[:,2]) if fitted else (weight,np.full(len(weight),.075))
    for i in np.flatnonzero(weight>0):
        hit,normal,_,distance=tree.find_nearest(Vector(proposed[i]))
        if hit is None or distance>.8:raise ValueError('Trouser rise has no local torso support')
        # Preserve the existing lower construction; fit only the raised rise.
        proposed[i]=(1-fit_weight[i])*proposed[i]+fit_weight[i]*np.array(hit+normal*float(clearance[i]))
    for mod in deform:ob.modifiers.remove(mod)
    ob.data=ob.data.copy();local=world_points(proposed,np.linalg.inv(np.array(ob.matrix_world)))
    ob.data.vertices.foreach_set('co',local.astype(np.float32).ravel());ob.data.update()
    attr=ob.data.attributes.get('MF_173_material_coords')
    if attr:
        old=np.array([v.vector[:] for v in attr.data]);old[:,2]+=proposed[:,2]-world[:,2]
        attr.data.foreach_set('vector',old.astype(np.float32).ravel())
    bind_render_surface(ob,target)
    errors={}
    for frame in samples:
        scene.frame_set(frame);bpy.context.view_layer.update();p,_=fast_geometry(ob)
        errors[frame]=float(np.max(abs(p[lower_ids]-before[frame])))
    if max(errors.values())>.002:raise ValueError('Trouser rise changed the protected lower garment region: '+str(errors))
    for mod,state in flags:mod.show_viewport=state
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO';scene.cycles.device='CPU';scene.cycles.samples=8
    bpy.data.objects['MF_fit_tunic_173_visible'].hide_render=True
    for frame in (1,169,217,326):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for angle,view in ((90,'left'),(270,'right')):
            fit_render(out,'trouser-rise-'+view+'-'+str(frame),angle,(0,-.2,-5.8),4.8,(640,640))
    check_protected();scene.frame_set(217)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'integration-working.blend'),check_existing=False)
    (out/'result.json').write_text(json.dumps({'source_sha256':WORKING_SHA,'native_sha256':digest(out/'integration-working.blend'),
        'lower_region_max_errors':errors,'protected_exact':True,'visual_gate':'NOT_RUN',
        'scope':'Trouser-rise derivative only; renewed contact and cloth validation required'},indent=2)+'\n')
