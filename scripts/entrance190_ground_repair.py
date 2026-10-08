"""Repair obsolete shot-domain fade and prove the shared terrain/cameras."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    from mathutils import Vector
    from entrance190_geography import fields
    from entrance190_scene import path_sample
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'ground21'}:raise ValueError('Fixed ground repair required')
    source=base.BASE/'entrance190-composition19/scene.blend';out=base.BASE/'entrance190-ground21'
    r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Unbound source')
    with np.load(base.BASE/'entrance190-rider09/route.npz',allow_pickle=False) as z:route={k:z[k] for k in z.files}
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    land=bpy.data.objects['AS_valley_landform'];mat=land.data.materials[0]
    mat.node_tree.links.new(mat.node_tree.nodes['Principled BSDF'].outputs[0],mat.node_tree.nodes['Material Output'].inputs['Surface'])
    hidden=[];bpy.context.view_layer.update()
    for ob in scene.objects:
        if ob.hide_render:continue
        if ob.name.startswith('MF188_grove_') or (ob.name.startswith('MF190_route_dressing_') and max(ob.dimensions)>8):
            p=np.array(ob.matrix_world.translation);h,d=fields(((p[:2]-[0,.2])/8.3)[None],route)
            if d[0]<13:ob.hide_render=True;hidden.append(ob.name)
    # Actual mesh vertical rays, not only the analytic height function.
    rays=[]
    for i in range(193):
        p=route['position'][i*8]*8.3+np.array([0,.2,-20.931]);local=land.matrix_world.inverted()@Vector(p)
        hit=land.ray_cast(local+Vector((0,0,1000)),Vector((0,0,-1)))
        if not hit[0]:raise ValueError('Route left rendered terrain')
        q=land.matrix_world@hit[1];error=abs(q.z-p[2]);rays.append(float(error))
        if error>.03:raise ValueError('Rendered terrain differs from route contact plane')
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    for f in (361,409,457,505,552):
        scene.frame_set(f);scene.render.filepath=str(out/('frame-%04d.png'%f));bpy.ops.render.render(write_still=True)
    cam=scene.camera;action=cam.animation_data.action;dataaction=cam.data.animation_data.action
    cam.animation_data.action=None;cam.data.animation_data.action=None;scene.frame_set(361)
    cam.location=(100,40,450);target=Vector((-115,-275,-10));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=640
    scene.render.filepath=str(out/'geography.png');bpy.ops.render.render(write_still=True)
    cam.animation_data.action=action;cam.data.animation_data.action=dataaction;scene.frame_set(362);scene.frame_set(361)
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':m.filepath=bpy.path.abspath(m.filepath)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'native_sha256':base.digest(out/'scene.blend'),'hidden_canopies':hidden,'terrain_ray_count':len(rays),'maximum_route_height_error_native':max(rays),'visual_gate':'NOT_RUN','repair':'Removed obsolete local-radius transparent fade; source protected'},indent=2)+'\n')

if __name__=='__main__':main()
