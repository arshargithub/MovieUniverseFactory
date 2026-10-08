"""Source-bound Director189 diagnostics and reversible shot corrections.

Only fixed reviewed operations are admitted; no supplied code or paths execute.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe_motion178 as base

SOURCE = base.BASE / 'entrance188-seal19/scene.blend'
SOURCE_SHA = '5387bb35da1a209d432e50ed7992e6aaa7a9d41bf78fabe6ebe36cc616fa944d'


def validate(job):
    if job not in ({'operation': 'diagnose01'}, {'operation': 'neck02'}, {'operation':'world03'}, {'operation':'candidate04'}, {'operation':'candidate05'}, {'operation':'attention06'}, {'operation':'attention07'}):
        raise ValueError('Fixed189 operation required')
    if SOURCE.is_symlink() or base.digest(SOURCE) != SOURCE_SHA:
        raise ValueError('Pinned188 source changed')
    source=SOURCE
    if job['operation'] in ('attention06','attention07'):source=base.BASE/'entrance189-candidate05/scene.blend'
    record = json.loads((source.parent / 'result.json').read_text())
    if source.is_symlink() or base.digest(source)!=record['native_sha256']:raise ValueError('Candidate changed')
    for row in record['caches']:
        path = (source.parent / row['path']).resolve()
        if not path.is_relative_to(base.BASE.resolve()) or base.digest(path) != row['sha256']:
            raise ValueError('Bound cache changed')
    out = base.BASE / ('entrance189-'+job['operation'])
    if out.exists() or out.is_symlink():
        raise ValueError('Preserve previous evidence')
    return out,source


def diagnose(scene, out):
    import bpy
    import numpy as np
    from wardrobe_motion178_controls import render_geometry_paused
    body = bpy.data.objects['MF_studio_adult_body']
    rig = bpy.data.objects['MF_body156_fit_rig']
    record = {'source_sha256': SOURCE_SHA, 'visual_gate': 'NOT_RUN'}
    record['body'] = {
        'matrix_world': [list(r) for r in body.matrix_world],
        'vertices': len(body.data.vertices),
        'keys': [{ 'name': k.name, 'value': k.value,
                   'range': [k.slider_min, k.slider_max] }
                 for k in body.data.shape_keys.key_blocks],
        'modifiers': [{'name': m.name, 'type': m.type} for m in body.modifiers],
        'materials': [m.name for m in body.data.materials if m],
    }
    rows = []
    with render_geometry_paused():
        for frame in range(217,361):
            scene.frame_set(frame); bpy.context.view_layer.update()
            rows.append({'frame': frame, 'bones': {
                n: {'matrix': [list(r) for r in rig.matrix_world @ rig.pose.bones[n].matrix],
                    'rotation': list(rig.pose.bones[n].rotation_quaternion)}
                for n in ('chest','MF185_neck','MF185_head')}})
    record['trajectory'] = rows
    record['attachments'] = [{
        'name': ob.name, 'parent': ob.parent.name if ob.parent else None,
        'constraints': [{'type': c.type, 'target': getattr(getattr(c,'target',None),'name',None),
                         'subtarget': getattr(c,'subtarget',None)} for c in ob.constraints]}
        for ob in scene.objects if ob.name.startswith(('MF_aimable','MF_natural','MF185_moving_shawl'))]
    record['lights'] = [{'name': ob.name, 'energy': ob.data.energy, 'type': ob.data.type,
                         'location': list(ob.location)} for ob in scene.objects if ob.type=='LIGHT']
    scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=True
    scene.render.resolution_x=540;scene.render.resolution_y=960;scene.render.resolution_percentage=100
    scene.frame_set(360);bpy.context.view_layer.update()
    scene.render.filepath=str(out/'textured360.png');bpy.ops.render.render(write_still=True)
    material=bpy.data.materials.new('189 diagnostic clay');material.use_nodes=True
    shader=material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(.38,.38,.38,1)
    shader.inputs['Roughness'].default_value=.8
    original=list(body.data.materials);body.data.materials.clear()
    for _ in original:body.data.materials.append(material)
    scene.render.filepath=str(out/'clay360.png');bpy.ops.render.render(write_still=True)
    record['rest_bounds']=[np.min([v.co[:] for v in body.data.vertices],axis=0).tolist(),
                           np.max([v.co[:] for v in body.data.vertices],axis=0).tolist()]
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')


def main():
    import bpy
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    job=json.loads(Path(args[0]).read_text());out,source=validate(job);out.mkdir()
    (out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    base.check_protected()
    scene=bpy.context.scene
    if job['operation']=='diagnose01':diagnose(scene,out)
    elif job['operation']=='neck02':neck_controls(scene,out)
    elif job['operation']=='world03':
        import entrance189_world as world
        (out/'world-handler.py').write_bytes(Path(world.__file__).read_bytes())
        result={'dust':world.dust(scene),'terrain':world.terrain(scene),'visual_gate':'NOT_RUN'}
        scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=True
        scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
        for frame in (309,217,360):
            scene.frame_set(frame);bpy.context.view_layer.update()
            scene.render.filepath=str(out/('frame-%04d.png'%frame));bpy.ops.render.render(write_still=True)
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    elif job['operation'] in ('candidate04','candidate05'):candidate(scene,out)
    elif job['operation'] in ('attention06','attention07'):attention(scene,out,source)
    base.check_protected()


def attention(scene,out,source):
    import bpy
    import os
    import entrance189_performance as performance
    from wardrobe_motion178_controls import render_geometry_paused
    (out/'performance-handler.py').write_bytes(Path(performance.__file__).read_bytes())
    body=bpy.data.objects['MF_studio_adult_body']
    controls={};driver_rows=[]
    for name in performance.facial_values(217):
        key=body.data.shape_keys.key_blocks[name]
        curves=[f for f in body.data.shape_keys.animation_data.drivers if f.data_path==key.path_from_id('value')]
        if len(curves)!=1 or len(curves[0].driver.variables)!=1:raise ValueError('Unexpected facial driver contract')
        variable=curves[0].driver.variables[0];target=variable.targets[0]
        if variable.type!='SINGLE_PROP' or target.id_type!='KEY':raise ValueError('Unexpected face source')
        controller=target.id
        if target.data_path!=controller.key_blocks[name].path_from_id('value'):raise ValueError('Unexpected driver path')
        controls[name]=controller.key_blocks[name]
        driver_rows.append({'name':name,'controller_id':controller.name,'expression':curves[0].driver.expression,'valid':curves[0].is_valid})
    # This assembly intentionally drives body blendshapes from the retained
    # accepted face controller. Animate the source, never its driven output.
    if body.data.shape_keys.animation_data:body.data.shape_keys.animation_data.action=None
    for key in controls.values():
        if key.id_data.animation_data:key.id_data.animation_data.action=None
    rows=[]
    with render_geometry_paused():
        body.hide_viewport=False
        for f in range(217,361):
            for name,value in performance.facial_values(f).items():
                k=controls[name];k.value=value;k.keyframe_insert(data_path='value',frame=f)
        for f in (217,265,309,312,337,360):
            scene.frame_set(f);bpy.context.view_layer.update()
            expected=performance.facial_values(f)
            actual={n:float(body.data.shape_keys.key_blocks[n].value) for n in expected}
            if max(abs(actual[n]-v) for n,v in expected.items())>1e-5:
                (out/'failure.json').write_text(json.dumps({'frame':f,'actual':actual,'expected':expected,'drivers':driver_rows},indent=2)+'\n')
                raise ValueError('Face driver transfer failed')
            rows.append({'frame':f,'actual':actual})
    scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=True
    scene.render.resolution_x=540;scene.render.resolution_y=960;scene.render.resolution_percentage=100
    # Hold the revealing camera, not the body, to inspect blink and effort.
    scene.frame_set(360);bpy.context.view_layer.update();camera=scene.camera.matrix_world.copy()
    camera_action=scene.camera.animation_data.action
    camera_slot=scene.camera.animation_data.action_slot
    lens_action=scene.camera.data.animation_data.action if scene.camera.data.animation_data else None
    lens_slot=scene.camera.data.animation_data.action_slot if scene.camera.data.animation_data else None
    scene.camera.animation_data_clear();scene.camera.matrix_world=camera
    scene.camera.data.animation_data_clear()
    for f in (360,312,265):
        scene.frame_set(f);bpy.context.view_layer.update()
        scene.render.filepath=str(out/('close-%04d.png'%f));bpy.ops.render.render(write_still=True)
    # Restore the exact existing actions/slots, without appending scene data.
    if not camera_action:raise ValueError('Source camera action missing')
    scene.camera.animation_data_create();scene.camera.animation_data.action=camera_action
    if camera_slot:scene.camera.animation_data.action_slot=camera_slot
    if lens_action:
        scene.camera.data.animation_data_create();scene.camera.data.animation_data.action=lens_action
        if lens_slot:scene.camera.data.animation_data.action_slot=lens_slot
    scene.frame_set(217);bpy.context.preferences.filepaths.save_version=0
    destination=out/'scene.blend';bpy.ops.wm.save_as_mainfile(filepath=str(destination),relative_remap=True,compress=True)
    result={'source_sha256':base.digest(source),'face_transfer':rows,'visual_gate':'NOT_RUN','caches':[]}
    for ob in scene.objects:
        for mod in ob.modifiers:
            if mod.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(mod.filepath)).resolve()
                if not p.is_relative_to(base.BASE.resolve()):raise ValueError('Cache escaped asset root')
                rel=os.path.relpath(p,out);mod.filepath='//'+rel
                result['caches'].append({'object':ob.name,'path':rel,'sha256':base.digest(p)})
    bpy.ops.wm.save_as_mainfile(filepath=str(destination),relative_remap=True,compress=True)
    result['native_sha256']=base.digest(destination)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def candidate(scene,out):
    import bpy
    import os
    import entrance189_world as world
    import entrance189_groom as groom
    import entrance189_performance as performance
    for module in (world,groom,performance):(out/Path(module.__file__).name).write_bytes(Path(module.__file__).read_bytes())
    result={'source_sha256':SOURCE_SHA,'visual_gate':'NOT_RUN','director_acceptance':'PENDING'}
    result['performance']=performance.animate(scene,out)
    result['mane']=groom.mane(scene,out)
    result['tail']=groom.fuller_tail(scene,out)
    result['dust']=world.dust(scene);result['ground']=world.terrain(scene)
    scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=True
    scene.render.resolution_x=540;scene.render.resolution_y=960;scene.render.resolution_percentage=100
    for frame in (360,309,217,312):
        scene.frame_set(frame);bpy.context.view_layer.update()
        scene.render.filepath=str(out/('frame-%04d.png'%frame));bpy.ops.render.render(write_still=True)
    scene.frame_set(217);bpy.context.preferences.filepaths.save_version=0
    destination=out/'scene.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(destination),relative_remap=True,compress=True)
    result['caches']=[]
    for ob in scene.objects:
        for mod in ob.modifiers:
            if mod.type!='MESH_CACHE':continue
            p=Path(bpy.path.abspath(mod.filepath)).resolve()
            if not p.is_relative_to(base.BASE.resolve()):raise ValueError('Out of scope cache')
            relative=os.path.relpath(p,out);mod.filepath='//'+relative
            result['caches'].append({'object':ob.name,'path':relative,'sha256':base.digest(p)})
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(destination),relative_remap=True,compress=True)
    result['native_sha256']=base.digest(destination)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def neck_controls(scene,out):
    import bpy
    import numpy as np
    body=bpy.data.objects['MF_studio_adult_body'];body.data=body.data.copy()
    scene.frame_set(360);bpy.context.view_layer.update()
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    mat=bpy.data.materials.new('189 neck clay');mat.use_nodes=True
    mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.38,.38,.38,1)
    for i in range(len(body.data.materials)):body.data.materials[i]=mat
    arm=next(m for m in body.modifiers if m.type=='ARMATURE')
    original=arm.use_deform_preserve_volume
    def render(label):
        bpy.context.view_layer.update();scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    render('source')
    arm.use_deform_preserve_volume=not original;render('alternate-skinning')
    arm.use_deform_preserve_volume=original
    from wardrobe_motion178_controls import smooth
    count=0
    for v in body.data.vertices:
        x,y,z=v.co
        if not (-2.05<z<-.8 and abs(x)<.88):continue
        blend=smooth((.88-abs(x))/.25)*smooth((z+2.05)/.25)*smooth((-.8-z)/.12)
        neck=smooth((z+1.95)/.65);head=smooth((z+1.24)/.40)
        weights={'chest':1-neck,'MF185_neck':neck*(1-head),'MF185_head':neck*head}
        for name,new in weights.items():
            g=body.vertex_groups[name]
            try:old=g.weight(v.index)
            except RuntimeError:old=0.
            g.add([v.index],old*(1-blend)+new*blend,'REPLACE')
        count+=1
    render('distributed-neck')
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,
        'original_preserve_volume':original,'distributed_vertices':count,'visual_gate':'NOT_RUN',
        'scope':'Two diagnostic factors separately compared to source; not selected correction'},indent=2)+'\n')


if __name__=='__main__':main()
