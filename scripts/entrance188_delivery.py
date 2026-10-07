"""Fresh-open, attachment and full-frame checks of a fixed native candidate."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SOURCE=base.BASE/'entrance188-candidate05'


def validate(job):
    if job not in ({'operation':'audit01'},{'operation':'reopen01'},{'operation':'motion01'},{'operation':'transport06'},{'operation':'audit07'},{'operation':'reopen07'},{'operation':'motion07'}):
        raise ValueError('Fixed delivery operation required')
    source=base.BASE/'entrance188-transport06' if job['operation'].endswith('07') else SOURCE
    record=json.loads((source/'result.json').read_text())
    path=source/'scene.blend'
    if path.is_symlink() or base.digest(path)!=record['native_sha256']:raise ValueError('Candidate changed')
    for row in record['caches']:
        dep=(source/row['path']).resolve()
        if not dep.is_relative_to(base.BASE.resolve()) or base.digest(dep)!=row['sha256']:
            raise ValueError('Cache binding failed')
    out=base.BASE/('entrance188-'+job['operation'])
    if out.exists() or out.is_symlink():raise ValueError('Preserve existing proof')
    return path,out,record


def audit(scene):
    import bpy
    import numpy as np
    horse=bpy.data.objects['MF185_gait_horse'];fuzz=bpy.data.objects['MF188_short_coat_fuzz']
    for ob in scene.objects:
        if ob.type in ('MESH','CURVE','CURVES'):ob.hide_viewport=ob not in (horse,fuzz)
    rows=[]
    for frame in range(217,361):
        scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        eh=horse.evaluated_get(deps);mh=eh.to_mesh()
        h=np.empty(len(mh.vertices)*3,dtype=np.float32);mh.vertices.foreach_get('co',h)
        matrix=np.array(eh.matrix_world);h=h.reshape(-1,3)@matrix[:3,:3].T+matrix[:3,3]
        ef=fuzz.evaluated_get(deps);mf=ef.to_mesh()
        f=np.empty(len(mf.vertices)*3,dtype=np.float32);mf.vertices.foreach_get('co',f);f=f.reshape(-1,3)
        def attr(name,dtype=float):
            a=np.empty(len(mf.vertices),dtype=dtype);mf.attributes[name].data.foreach_get('value',a);return a
        roots=np.flatnonzero(attr('tip_offset')<1e-8)[::17]
        expected=np.zeros((len(roots),3))
        for i in range(3):expected+=h[attr('bind_index_'+str(i),np.int32)[roots]]*attr('bind_weight_'+str(i))[roots,None]
        error=float(np.linalg.norm(f[roots]-expected,axis=1).max())
        if not np.isfinite(f).all() or error>.005:raise ValueError('Fuzz root attachment failed '+str((frame,error)))
        rows.append({'frame':frame,'sampled_root_vertices':len(roots),'max_radial_root_distance_native':error})
        ef.to_mesh_clear();eh.to_mesh_clear()
        if frame%24==0:print('188 attachment audit',frame,flush=True)
    return {'root_attachment_samples':rows,'scope':'All144 frames; root-ring distance, not a visual or whole-groom collision pass'}


def main():
    import bpy
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    job=json.loads(Path(args[0]).read_text());path,out,record=validate(job);out.mkdir()
    (out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    base.check_protected();scene=bpy.context.scene
    result={'native_sha256':record['native_sha256'],'cache_count':len(record['caches']),'visual_gate':'NOT_RUN'}
    if job['operation']=='transport06':
        import entrance188_groom as groom
        import os
        (out/'groom-handler.py').write_bytes(Path(groom.__file__).read_bytes())
        result['groom']=groom.fixed_transport(scene,out,bpy.data.objects['MF185_gait_horse'],base.BASE/'entrance-astra-mane-cache01/samples.npz')
        scene.cycles.device='CPU';scene.render.use_persistent_data=True
        for frame in (217,265,309,360):
            scene.frame_set(frame);bpy.context.view_layer.update();scene.render.filepath=str(out/('frame-%04d.png'%frame));bpy.ops.render.render(write_still=True)
            print('188 transported groom',frame,flush=True)
        scene.frame_set(217);bpy.context.preferences.filepaths.save_version=0
        destination=out/'scene.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(destination),relative_remap=True,compress=True)
        result['caches']=[]
        for ob in scene.objects:
            for mod in ob.modifiers:
                if mod.type=='MESH_CACHE':
                    dep=Path(bpy.path.abspath(mod.filepath)).resolve();rel=os.path.relpath(dep,out)
                    result['caches'].append({'object':ob.name,'path':rel,'sha256':base.digest(dep)});mod.filepath='//'+rel
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_as_mainfile(filepath=str(destination),relative_remap=False,compress=True)
        result['native_sha256']=base.digest(destination)
    elif job['operation'].startswith('audit'):result.update(audit(scene))
    else:
        scene.cycles.device='CPU';scene.render.use_persistent_data=True
        frames=(217,265,309,360) if job['operation'].startswith('reopen') else list(range(337,361))+list(range(217,337))
        if job['operation'].startswith('motion'):
            scene.render.resolution_x=288;scene.render.resolution_y=512;scene.cycles.samples=8
        for frame in frames:
            scene.frame_set(frame);bpy.context.view_layer.update();scene.render.filepath=str(out/('frame-%04d.png'%frame))
            bpy.ops.render.render(write_still=True);print('188 delivery frame',frame,flush=True)
        result.update({'frames':list(frames),'resolution':[scene.render.resolution_x,scene.render.resolution_y],
                       'samples':scene.cycles.samples,'renderer':'CPU','fps':24})
    result['protected_sources_unchanged']=True;base.check_protected()
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
