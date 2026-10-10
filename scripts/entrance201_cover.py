"""One further modest coverage step on the selected dust/actor derivatives."""
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def route_readability():
    import bpy
    mat=bpy.data.objects['AS_valley_landform'].data.materials[0];n,l=mat.node_tree.nodes,mat.node_tree.links
    bs=next(x for x in n if x.type=='BSDF_PRINCIPLED');paint=bs.inputs['Base Color'].links[0].from_socket
    attr=n.new('ShaderNodeAttribute');attr.attribute_name='MF190_road_distance'
    weight=n.new('ShaderNodeMapRange');weight.clamp=True;weight.interpolation_type='SMOOTHSTEP'
    weight.inputs['From Min'].default_value=16;weight.inputs['From Max'].default_value=29;weight.inputs['To Min'].default_value=.62;weight.inputs['To Max'].default_value=0
    l.new(attr.outputs['Fac'],weight.inputs['Value'])
    mix=n.new('ShaderNodeMixRGB');mix.label='201 worn earth on the actual two routes';l.new(weight.outputs[0],mix.inputs[0]);l.new(paint,mix.inputs[1]);mix.inputs[2].default_value=(.27,.18,.09,1);l.new(mix.outputs[0],bs.inputs['Base Color'])

def main():
    import bpy
    from entrance201_fit import apply_opening
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'opening17'},{'operation':'route18'}):raise ValueError('Fixed modest coverage correction')
    opening=job['operation']=='opening17';stage='opening14' if opening else 'route16'
    source=base.BASE/('entrance201-'+stage)/'scene.blend';out=base.BASE/('entrance201-'+job['operation']);r=json.loads((source.parent/'result.json').read_text())
    pins={'opening14':'a2b762b129abd8ca8fde6e04adcd6c2fa8f17e1af644ba7a445ad2e18db2ed58','route16':'0e108be33bd395e4a9a939881677bdce4d4fdb3c8c5a3e739567d5b4f8cb01f9'}
    if out.exists() or base.digest(source)!=pins[stage]:raise ValueError('Source/output')
    for row in r['caches']:
        if base.digest((source.parent/row['path']).resolve())!=row['sha256']:raise ValueError('Cache changed')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());(out/'entrance201_fit.py').write_bytes((ROOT/'scripts/entrance201_fit.py').read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected();fit=apply_opening(out,217 if opening else 361,144 if opening else 193)
    if not opening:route_readability()
    caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    scene.frame_set(217 if opening else 361);bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    r.update(source_sha256=base.digest(source),native_sha256=base.digest(out/'scene.blend'),caches=caches,fit={'additional_step':fit,'total':'Two feathered9-degree steps; not a rigid18-degree whole-cover rotation'},visual_gate='NOT_RUN')
    (out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
    if opening:
        scene.frame_set(360);cam=scene.camera;mat=cam.matrix_world.copy();lens=cam.data.lens;cam.animation_data_clear();cam.data.animation_data_clear();cam.matrix_world=mat;cam.data.lens=lens
        for ob in scene.objects:
            for m in ob.modifiers:
                if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
        scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.cycles.samples=12;scene.cycles.device='CPU';scene.render.use_persistent_data=False
        for f in (289,312,336,360):
            scene.frame_set(f);scene.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
    else:
        from entrance190_motion_review import geography_camera
        for ob in scene.objects:
            for m in ob.modifiers:
                if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
        scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.cycles.samples=12;scene.cycles.device='CPU';scene.render.use_persistent_data=False
        for f in (385,457,552):
            scene.frame_set(f);scene.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
        scene.frame_set(361);scene.camera.animation_data_clear();scene.camera.data.animation_data_clear();scene.camera.data.type='ORTHO';geography_camera(scene)
        scene.render.filepath=str(out/'geography.png');bpy.ops.render.render(write_still=True)
    base.check_protected()

if __name__=='__main__':main()
