"""Exchange188 fixed horse/world art operations; source-protected derivatives."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import entrance_astra as prior
BASE=prior.BASE


def validate(job):
    if job not in ({'operation':'horse01'},{'operation':'horse02'},{'operation':'horse03'},{'operation':'integrated01'},{'operation':'integrated02'},{'operation':'integrated03'},{'operation':'integrated04'},{'operation':'candidate05'}):raise ValueError('Fixed188 operation required')
    if prior.prior.actor.base.digest(prior.prior.SOURCE)!=prior.prior.SOURCE_SHA:raise ValueError('Actor binding failed')
    source=BASE/'entrance-astra-mane-cache01/samples.npz'
    if prior.prior.actor.base.digest(source)!='ef85af0aa87737b6af616e3373182768651107d111fafa81c66c194b338a5a6b':raise ValueError('Mane source changed')
    out=BASE/('entrance188-'+job['operation'])
    if out.exists() or out.is_symlink():raise ValueError('Preserve earlier evidence')
    dependencies=json.loads((prior.prior.SOURCE.parent/'result.json').read_text())['shared_cache_dependencies']
    for row in dependencies:
        path=(prior.prior.SOURCE.parent/row['path']).resolve()
        if not path.is_relative_to(BASE.resolve()) or not path.is_file() or prior.prior.actor.base.digest(path)!=row['sha256']:
            raise ValueError('Missing or changed shared actor cache')
    return out,source


def main():
    import bpy
    import entrance188_groom as groom
    from mathutils import Vector
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    job=json.loads(Path(args[0]).read_text());out,source=validate(job)
    out.mkdir()
    for module in (__file__,groom.__file__):
        path=Path(module);(out/path.name).write_bytes(path.read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(prior.prior.SOURCE),load_ui=False,use_scripts=False)
    prior.prior.actor.base.check_protected()
    report={'actor_sha256':prior.prior.SOURCE_SHA,'horse_materials':prior.horse_restore()}
    scene=bpy.context.scene
    report['mane']=groom.build(scene,out,source)
    report['coat']=groom.coat(bpy.data.objects['MF185_gait_horse'])
    report['fuzz']=groom.fuzz(scene,bpy.data.objects['MF185_gait_horse'])
    cam=scene.camera;cam.animation_data_clear();cam.data.animation_data_clear()
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
    scene.render.use_persistent_data=True
    if job['operation']=='integrated04':
        from wardrobe_motion178_review import preview_gpu
        report['renderer']=preview_gpu(scene)
    if job['operation'].startswith('integrated') or job['operation']=='candidate05':
        import entrance188_world as world
        import entrance_astra_world as camera
        from wardrobe_motion178_controls import render_geometry_paused
        use_corridor=job['operation'] in ('integrated03','integrated04','candidate05')
        report['world']=world.corridor(scene,out) if use_corridor else world.build(scene,out)
        scene.render.resolution_x=540;scene.render.resolution_y=960
        keys=[]
        with render_geometry_paused():
            for frame in range(217,361):
                scene.frame_set(frame);bpy.context.view_layer.update()
                row=camera.camera(scene,bpy.data.objects['MF_body156_fit_rig'],frame)
                height=world.trail_height if use_corridor else camera.terrain_height
                row['terrain_clearance']=row['position'][2]-height(row['position'][0],row['position'][1]-camera.SPEED*(frame-217)/24)
                if row['terrain_clearance']<2:raise ValueError('Camera crosses ground')
                keys.append(row)
                for prop in ('location','rotation_euler'):cam.keyframe_insert(data_path=prop,frame=frame)
                cam.data.keyframe_insert(data_path='lens',frame=frame)
        report['camera_keys']=keys
        if job['operation']=='candidate05':
            import os
            report['caches']=[]
            for ob in scene.objects:
                for mod in ob.modifiers:
                    if mod.type=='MESH_CACHE':
                        path=Path(bpy.path.abspath(mod.filepath)).resolve()
                        relative=os.path.relpath(path,out)
                        report['caches'].append({'object':ob.name,'path':relative,'sha256':prior.prior.actor.base.digest(path)})
                        mod.filepath='//'+relative
            # Pack image inputs; keep large native motion caches shared and relative.
            for im in bpy.data.images:
                if im.source=='FILE' and not im.packed_file and im.has_data:
                    im.pack()
            scene.frame_set(217);scene.cycles.seed=188;scene.cycles.use_animated_seed=False
            path=out/'scene.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False,compress=True)
            report['native_sha256']=prior.prior.actor.base.digest(path)
        for frame in (217,265,309,360):
            scene.frame_set(frame);bpy.context.view_layer.update();scene.render.filepath=str(out/('frame-%04d.png'%frame));bpy.ops.render.render(write_still=True)
            print('188 integrated',frame,flush=True)
        report['visual_gate']='NOT_RUN';report['native_saved']=job['operation']=='candidate05'
        (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        prior.prior.actor.base.check_protected()
        return
    for frame,name,position,target,lens in (
        (309,'side',(-35,0,-6),(0,-1,-8),46),
        (360,'reveal',(-9,-25,0),(0,-4,-4),48),
        (265,'opposite',(28,-18,-1),(0,-3,-6),46)):
        scene.frame_set(frame);bpy.context.view_layer.update()
        cam.data.type='PERSP';cam.data.lens=lens;cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36
        cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.dof.use_dof=False
        scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
        print('188 rendered',name,flush=True)
    report['visual_gate']='NOT_RUN';report['native_saved']=False
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    prior.prior.actor.base.check_protected()


if __name__=='__main__':main()
