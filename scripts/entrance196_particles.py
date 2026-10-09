"""Replace a long disconnected debris cache with bounded visible instances."""
import json,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def fit_transform(reference,points):
    p=np.asarray(reference,float);q=np.asarray(points,float)
    if p.shape!=(17,3) or q.shape!=p.shape or not np.isfinite(q).all():raise ValueError('Particle topology')
    linear=np.linalg.lstsq(np.column_stack((p,np.ones(len(p)))),q,rcond=None)[0]
    m=np.eye(4);m[:3,:3]=linear[:3].T;m[:3,3]=linear[3]
    if np.max(abs(p@m[:3,:3].T+m[:3,3]-q))>2e-4:raise ValueError('Non-rigid particle source')
    return m

def main():
    import bpy
    from mathutils import Matrix
    from entrance189_groom import read_mdd
    from entrance196_build import prototype
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'particles40'}:raise ValueError('Fixed particle representation only')
    source=base.BASE/'entrance196-integrate36/scene.blend';out=base.BASE/'entrance196-particles40';r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Unbound source')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    old=bpy.data.objects['MF196_hoof_ejected_pebbles'];mod=next(m for m in old.modifiers if m.type=='MESH_CACHE');a=np.asarray(read_mdd(bpy.path.abspath(mod.filepath))).reshape(144,-1,17,3)
    old.hide_render=True;old.hide_viewport=True
    p,faces=prototype(np.random.default_rng(19604));meshes=[]
    for i,mat in enumerate(old.data.materials):
        mesh=bpy.data.meshes.new(f'196 bounded pebble material{i}');mesh.from_pydata(p.tolist(),[],faces);mesh.materials.append(mat);mesh.update();meshes.append(mesh)
    max_error=0.;rows=[]
    for j in range(a.shape[1]):
        sizes=np.max(np.ptp(a[:,j],axis=1),axis=1);active=np.flatnonzero(sizes>.01)
        if len(active)==0:continue
        ob=bpy.data.objects.new(f'MF196_bounded_pebble_{j:04d}',meshes[j%len(meshes)]);scene.collection.objects.link(ob);ob.parent=bpy.data.objects['AS_world_travel'];ob.rotation_mode='QUATERNION'
        first,last=int(active[0]),int(active[-1]);ob.hide_render=True;ob.hide_viewport=True
        for f,hidden in ((216,True),(first+217,False),(last+218,True)):
            ob.hide_render=hidden;ob.keyframe_insert(data_path='hide_render',frame=f)
            ob.hide_viewport=hidden;ob.keyframe_insert(data_path='hide_viewport',frame=f)
        for i in active:
            m=fit_transform(p,a[i,j]);ob.matrix_basis=Matrix(m.tolist());actual=np.array(ob.matrix_basis)
            error=float(np.max(abs(p@actual[:3,:3].T+actual[:3,3]-a[i,j])));max_error=max(max_error,error)
            for field in ('location','rotation_quaternion','scale'):ob.keyframe_insert(data_path=field,frame=int(i)+217)
        if ob.animation_data and ob.animation_data.action:
            for layer in ob.animation_data.action.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for fc in bag.fcurves:
                            for key in fc.keyframe_points:key.interpolation='CONSTANT' if fc.data_path.startswith('hide_') else 'LINEAR'
        rows.append({'object':ob.name,'first':first+217,'last':last+217})
    if max_error>3e-4:raise ValueError('Object decomposition changes trajectory')
    scene.frame_set(218);scene.frame_set(217);bpy.context.view_layer.update()
    caches=[]
    for ob in scene.objects:
        for mod in ob.modifiers:
            if mod.type=='MESH_CACHE':
                path=Path(bpy.path.abspath(mod.filepath)).resolve();mod.filepath=str(path);caches.append({'object':ob.name,'path':os.path.relpath(path,out),'sha256':base.digest(path),'start':mod.frame_start})
    (out/'particle-binding.json').write_text(json.dumps({'objects':rows,'maximum_reconstructed_vertex_error_native':max_error,'method':'Same active17-vertex particle trajectories fitted to bounded object transforms; lifetime visibility replaces underground inactive geometry. Not a new physics simulation.'},indent=2)+'\n')
    base.check_protected();bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':base.digest(source),'native_sha256':base.digest(out/'scene.blend'),'caches':caches,'bounded_particles':len(rows),'maximum_active_vertex_error_native':max_error,'visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
