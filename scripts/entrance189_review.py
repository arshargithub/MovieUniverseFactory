"""Fixed independent reopen, overview and complete motion of189 candidates."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def validate(job):
    if job not in ({'operation':'overview15'},{'operation':'motion16'},{'operation':'diagnostic08'},{'operation':'morph09'},{'operation':'source10'},{'operation':'source11'},{'operation':'source12'},{'operation':'repair13'},{'operation':'performance14'}):raise ValueError('Fixed review operation required')
    stage='performance14' if job['operation'] in ('overview15','motion16') else 'repair13' if job['operation']=='performance14' else 'attention07'
    folder=base.BASE/('entrance189-'+stage);record=json.loads((folder/'result.json').read_text())
    source=folder/'scene.blend'
    if source.is_symlink() or base.digest(source)!=record['native_sha256']:raise ValueError('Review source changed')
    for row in record['caches']:
        p=(folder/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Review dependency mismatch')
    out=base.BASE/('entrance189-'+job['operation'])
    if out.exists() or out.is_symlink():raise ValueError('Preserve evidence')
    if job['operation']=='motion16':
        gate=json.loads((base.BASE/'entrance189-overview15/internal-review.json').read_text())
        if gate.get('source_sha256')!=record['native_sha256'] or gate.get('status')!='PROCEED_TO_COMPLETE_MOTION':raise ValueError('Overview gate missing')
    return source,out,record


def main():
    import bpy
    import shutil
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    job=json.loads(Path(args[0]).read_text());source,out,record=validate(job);out.mkdir()
    (out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    base.check_protected();scene=bpy.context.scene
    if job['operation']=='performance14':
        from entrance189 import attention
        attention(scene,out,source);base.check_protected();return
    if job['operation']=='repair13':
        import entrance189_face as face
        (out/'face-handler.py').write_bytes(Path(face.__file__).read_bytes())
        repair=face.rebuild(scene,out)
        # The existing attention path reapplies source controls, renders three
        # close performance states, restores camera animation and saves hashes.
        from entrance189 import attention
        attention(scene,out,source)
        base.check_protected();return
    if job['operation']=='morph09':
        morph_diagnostic(scene,out);return
    if job['operation'] in ('source10','source11','source12'):
        import entrance189_face as face
        (out/'face-handler.py').write_bytes(Path(face.__file__).read_bytes())
        face.inspect(scene,out,rest=job['operation'] in ('source11','source12'));return
    if job['operation']=='diagnostic08':
        import numpy as np
        from mathutils import Vector
        scene.frame_set(360);bpy.context.view_layer.update()
        camera=scene.camera;body=bpy.data.objects['MF_studio_adult_body'];deps=bpy.context.evaluated_depsgraph_get()
        ev=body.evaluated_get(deps);mesh=ev.to_mesh();q=np.array([v.co[:] for v in mesh.vertices]);ev.to_mesh_clear()
        hit=scene.ray_cast(deps,camera.matrix_world.translation,camera.matrix_world.to_quaternion()@Vector((0,0,-1)))
        info={'camera':{'matrix':[list(r) for r in camera.matrix_world],'parent':camera.parent.name if camera.parent else None,
            'lens':camera.data.lens,'type':camera.data.type,'action':camera.animation_data.action.name if camera.animation_data else None},
            'body_bounds':[q.min(0).tolist(),q.max(0).tolist()],
            'camera_center_hit':hit[4].name if hit[0] else None,
            'body_keys':{k.name:k.value for k in body.data.shape_keys.key_blocks},
            'visible_head_objects':[ob.name for ob in scene.objects if not ob.hide_render and ob.name.startswith(('FBHead','MF_continuous'))]}
        (out/'inspection.json').write_text(json.dumps(info,indent=2)+'\n')
        scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.resolution_x=540;scene.render.resolution_y=960
        scene.render.filepath=str(out/'actual360.png');bpy.ops.render.render(write_still=True)
        return
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
    frames=list(range(217,361,6))+[360]
    if job['operation']=='motion16':
        prior=base.BASE/'entrance189-overview15'
        for f in frames:shutil.copy2(prior/('frame-%04d.png'%f),out/('frame-%04d.png'%f))
        frames=[f for f in range(217,361) if f not in frames]
    # Evaluate the original driver targets and actual output; an inserted
    # keyframe is not evidence that the assembled face responds.
    from entrance189_performance import facial_values
    body=bpy.data.objects['MF_studio_adult_body']
    rows=[]
    for f in frames:
        scene.frame_set(f);bpy.context.view_layer.update()
        values={n:float(body.data.shape_keys.key_blocks[n].value) for n in facial_values(f)}
        error=max(abs(values[n]-v) for n,v in facial_values(f).items())
        if error>1e-5:raise ValueError('Reopened face transfer failed')
        for name in ('MF185_moving_shawl','MF188_flowing_mane'):
            ob=bpy.data.objects[name];cache=[i for i,m in enumerate(ob.modifiers) if m.type=='MESH_CACHE']
            if len(cache)!=1 or cache[0]!=0:raise ValueError('Cache topology ordering regression')
        rows.append({'frame':f,'face_transfer_error':error,'camera':list(scene.camera.location)})
        scene.render.filepath=str(out/('frame-%04d.png'%f));bpy.ops.render.render(write_still=True)
        print('189 REVIEW FRAME',f,flush=True)
    base.check_protected()
    result={'source_sha256':record['native_sha256'],'frames':rows,'cache_hashes_checked':len(record['caches']),
        'protected_originals_exact':True,'visual_gate':'NOT_RUN','fps':24,
        'scope':'Preview-scale moving shot; not final-resolution release qualification'}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def morph_diagnostic(scene,out):
    import bpy
    import numpy as np
    from wardrobe_motion178_controls import render_geometry_paused
    body=bpy.data.objects['MF_studio_adult_body'];keys=body.data.shape_keys
    def coords(data):
        a=np.empty(len(data)*3,dtype=np.float32);data.foreach_get('co',a);return a.reshape(-1,3)
    basis=coords(keys.key_blocks[0].data)
    keyinfo=[]
    for k in keys.key_blocks:
        delta=coords(k.data)-basis
        ids=np.argsort(np.linalg.norm(delta,axis=1))[-3:]
        keyinfo.append({'name':k.name,'max_delta':float(abs(delta).max()),'largest_ids':ids.tolist(),
                        'basis_at_largest':basis[ids].tolist(),'delta_at_largest':delta[ids].tolist()})
    mods=[{'name':m.name,'type':m.type,'vertex_group':getattr(m,'vertex_group',None),
           'rest_source':getattr(m,'rest_source',None),'is_bind':getattr(m,'is_bind',None)} for m in body.modifiers]
    controls=[]
    for fc in keys.animation_data.drivers:
        for variable in fc.driver.variables:
            if variable.type=='SINGLE_PROP' and variable.targets[0].id_type=='KEY':
                controls.append(variable.targets[0].id)
    for control in set(controls):
        if control.animation_data:control.animation_data.action=None
        for k in list(control.key_blocks)[1:]:k.value=0
    rows=[]
    with render_geometry_paused():
        body.hide_viewport=False;scene.frame_set(360);bpy.context.view_layer.update()
        for expression in ('neutral','eyeSquintLeft','jawOpen','eyeBlinkLeft'):
            for control in set(controls):
                for k in list(control.key_blocks)[1:]:k.value=.1 if k.name==expression else 0
            body.data.update();bpy.context.view_layer.update()
            flags=[m.show_viewport for m in body.modifiers]
            for m in body.modifiers:m.show_viewport=False
            for stage in range(len(body.modifiers)+1):
                if stage:body.modifiers[stage-1].show_viewport=flags[stage-1]
                bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();q=coords(mesh.vertices);ev.to_mesh_clear()
                rows.append({'expression':expression,'through_modifier':body.modifiers[stage-1].name if stage else 'shape_keys_only',
                    'bounds':[q.min(0).tolist(),q.max(0).tolist()],'actual_value':keys.key_blocks[expression].value if expression!='neutral' else 0})
            print('189 MORPH CONTROL',expression,flush=True)
    (out/'result.json').write_text(json.dumps({'keys':keyinfo,'modifiers':mods,'controls':rows},indent=2)+'\n')


if __name__=='__main__':main()
