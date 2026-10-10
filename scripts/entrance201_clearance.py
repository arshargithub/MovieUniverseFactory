"""Measured static hair-envelope clearance transported with the head.

The cloth correction acts on its supported crown, never sculpts the accepted
hair or projects a moving nearest-point surface each frame.
"""
import json,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
PINS={289:'f60f64c438d279f7a7440e1b32ffa0d651c0e10a396a2f304615469fe5e3bf02',360:'d6b2cea58704757e3fc3d212467719626dfcf1ac819f6973759d2ea9290e3f16'}

def clearance_delta(hair,cloth):
    d=np.zeros(2501)
    for i,q in enumerate(cloth):
        if not(q[1]>1.0 and abs(q[0])<1.01 and -.35<q[2]<.86):continue
        distance=(hair[:,0]-q[0])**2+(hair[:,2]-q[2])**2
        p=hair[distance<.09**2]
        if len(p)<5:continue
        d[i]=max(0,float(np.percentile(p[:,1],99))+.045-q[1])
    if d.max()>.30:raise ValueError('Measured crown requires larger redesign')
    need=d.reshape(41,61);q=need.copy()
    for _ in range(3):
        pad=np.pad(q,1,mode='edge');average=(pad[:-2,1:-1]+pad[2:,1:-1]+pad[1:-1,:-2]+pad[1:-1,2:])/4
        q=np.maximum(need,.4*q+.6*average)
    return q.ravel()

def apply(out,first,count):
    import bpy
    from entrance189_groom import read_mdd,write_mdd,attach_cache
    from wardrobe_motion178_controls import render_geometry_paused
    delta=np.zeros(2501)
    for f,sha in PINS.items():
        path=base.BASE/'entrance201-head20'/f'crown-{f}.npz'
        if base.digest(path)!=sha:raise ValueError('Contact evidence changed')
        with np.load(path) as z:delta=np.maximum(delta,clearance_delta(np.concatenate([z['hair0'],z['hair1']]),z['cloth']))
    np.save(out/'crown-clearance.npy',delta)
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig'];ob=bpy.data.objects['MF185_moving_shawl'];mod=next(m for m in ob.modifiers if m.type=='MESH_CACHE');source=Path(bpy.path.abspath(mod.filepath));a=read_mdd(source);start=int(mod.frame_start);heads=[]
    with render_geometry_paused():
        for f in range(first,first+count):
            scene.frame_set(f);bpy.context.view_layer.update();world=ob.parent.matrix_world@ob.matrix_parent_inverse@ob.matrix_basis if ob.parent else ob.matrix_basis
            heads.append(np.array(world.inverted()@rig.matrix_world@rig.pose.bones['MF185_head'].matrix))
    def frames():
        for k,p in enumerate(a):
            q=np.array(p,float,copy=True);i=k+start-first
            if 0<=i<count:q[:2501]+=delta[:,None]*heads[i][:3,1]
            yield q.astype(np.float32)
    path=out/'shawl-contact.mdd';write_mdd(path,len(a),a.shape[1],frames());attach_cache(ob,path,start)
    return {'source_cache_sha256':base.digest(source),'contact_evidence':PINS,'maximum_lift_native':float(delta.max()),'affected_vertices':int(np.count_nonzero(delta>1e-5)),'method':'Fixed crown displacement fitted to99th-percentile nearby native hair guide envelope plus.045native clearance, feathered spatially and transported with head; not a new cloth simulation'}

def main():
    import bpy
    from entrance201_fit import apply_opening
    from entrance201_cover import route_readability
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'opening21'},{'operation':'route22'}):raise ValueError('Fixed measured contact correction')
    opening=job['operation']=='opening21';stage='opening17' if opening else 'route16';sha='b96c743fee50ce355bd592544ffcf2b4b1a1b8dfe09efcd78720ca3aaabadf3f' if opening else '0e108be33bd395e4a9a939881677bdce4d4fdb3c8c5a3e739567d5b4f8cb01f9'
    source=base.BASE/('entrance201-'+stage)/'scene.blend';out=base.BASE/('entrance201-'+job['operation']);r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=sha:raise ValueError('Source/output')
    for row in r['caches']:
        if base.digest((source.parent/row['path']).resolve())!=row['sha256']:raise ValueError('Cache changed')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    for name in ('entrance201_fit.py','entrance201_cover.py'):(out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    if not opening:apply_opening(out,361,193);route_readability()
    fit=apply(out,217 if opening else 361,144 if opening else 193);caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    scene.frame_set(217 if opening else 361);bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    r.update(source_sha256=base.digest(source),native_sha256=base.digest(out/'scene.blend'),caches=caches,contact_fit=fit,visual_gate='NOT_RUN')
    (out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.cycles.samples=12;scene.cycles.device='CPU';scene.render.use_persistent_data=False
    if opening:
        scene.frame_set(360);cam=scene.camera;mat=cam.matrix_world.copy();lens=cam.data.lens;cam.animation_data_clear();cam.data.animation_data_clear();cam.matrix_world=mat;cam.data.lens=lens
    for f in ((289,312,336,360) if opening else (385,457,552)):
        scene.frame_set(f);scene.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
    if not opening:
        from entrance190_motion_review import geography_camera
        scene.frame_set(361);scene.camera.animation_data_clear();scene.camera.data.animation_data_clear();scene.camera.data.type='ORTHO';geography_camera(scene)
        scene.render.filepath=str(out/'geography.png');bpy.ops.render.render(write_still=True)
    base.check_protected()

if __name__=='__main__':main()
