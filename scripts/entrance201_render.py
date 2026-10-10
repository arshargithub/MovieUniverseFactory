"""Closed native review operations for the integrated201 entrance."""
import json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
OPS={
 'route05':('route03','route',(361,385,409,433,457,481,505,529,552)),
 'opening06':('opening21','opening',tuple(range(217,361))),
 'attention07':('opening21','attention',tuple(range(289,337))),
 'route08':('route22','route',tuple(range(361,553))),
 'geography09':('route22','geography',tuple(range(48))),
 'openverify10':('opening21','opening',(217,295,343,350,360)),
 'routeverify11':('route22','route',(361,457,552)),
 'attention12':('opening14','attention',(289,312,336)),
 'geography13':('route16','geography',(0,24,47)),
}

def reopened_controls(record,out,kind):
    import bpy
    from entrance189_groom import read_mdd
    from wardrobe185_lower_cloth import sample
    from wardrobe_motion178_controls import render_geometry_paused
    opening=kind=='opening';frames=(217,295,360) if opening else (361,457,552)
    rows=[]
    with render_geometry_paused():
        for row in record['caches']:
            ob=bpy.data.objects[row['object']]
            if ob.hide_render:continue
            mods=[m for m in ob.modifiers if m.type=='MESH_CACHE']
            if len(mods)!=1 or list(ob.modifiers).index(mods[0])!=0:raise ValueError('Cache stack differs')
            m=mods[0];a=read_mdd(bpy.path.abspath(m.filepath));flags=[(x,x.show_viewport) for x in list(ob.modifiers)[1:]]
            for x,_ in flags:x.show_viewport=False
            ob.hide_viewport=False
            for f in frames:
                bpy.context.scene.frame_set(f);bpy.context.view_layer.update();p=sample(ob)
                expected=a[int(np.clip(f-int(m.frame_start),0,len(a)-1))]
                if p.shape!=expected.shape:raise ValueError('Evaluated cache topology')
                error=float(abs(p-expected).max());rows.append({'object':ob.name,'frame':f,'max_local_error':error})
                if error>1e-4:raise ValueError('Evaluated cache transfer differs')
            ob.hide_viewport=True
            for x,state in flags:x.show_viewport=state
    (out/'cache-parity.json').write_text(json.dumps({'status':'PASS','rows':rows},indent=2)+'\n')
    path=base.BASE/('entrance200-seal17/motion.npz' if opening else 'entrance201-route03/rig.npz')
    with np.load(path) as z:names=list(z['names']);expected=z['after']
    rig=bpy.data.objects['MF_body156_fit_rig'];errors=[]
    with render_geometry_paused():
        for f in frames:
            bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
            actual=np.array([np.array(rig.matrix_world@rig.pose.bones[n].matrix if opening else rig.pose.bones[n].matrix) for n in names])
            errors.append(float(abs(actual-expected[f-(217 if opening else 361)]).max()))
    (out/'pose-parity.json').write_text(json.dumps({'status':'PASS' if max(errors)<2e-5 else 'FAIL','frames':frames,'errors':errors,'expected_sha256':base.digest(path)},indent=2)+'\n')
    if max(errors)>=2e-5:raise ValueError('Reopened pose differs')

def main():
    import bpy
    from entrance198_terrain import fingerprint
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Fixed review operation')
    op=job['operation'];stage,kind,frames=OPS[op];source=base.BASE/('entrance201-'+stage)/'scene.blend';out=base.BASE/('entrance201-'+op)
    r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Source/output')
    for row in r['caches']:
        p=(source.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache mismatch')
    if len(frames)>12:
        review=json.loads((source.parent/'internal-review.json').read_text())
        if review.get('status')!='PROCEED_TO_FULL_MOTION' or review.get('source_sha256')!=r['native_sha256']:raise ValueError('Missing actual-camera admission')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    scene.frame_set(217 if kind in ('opening','attention') else 361);struct=fingerprint(scene)
    if 'verify' in op:reopened_controls(r,out,kind)
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                from entrance189_groom import read_mdd
                a=read_mdd(bpy.path.abspath(m.filepath))
                if a.shape[1]!=len(ob.data.vertices) or list(ob.modifiers).index(m)!=0:raise ValueError('Cache topology/order')
    if 'verify' not in op:
        for ob in scene.objects:
            for m in ob.modifiers:
                if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.cycles.samples=12;scene.cycles.device='CPU';scene.render.use_persistent_data=False
    if kind=='attention':
        scene.frame_set(360);matrix=scene.camera.matrix_world.copy();lens=scene.camera.data.lens
        scene.camera.animation_data_clear();scene.camera.data.animation_data_clear();scene.camera.matrix_world=matrix;scene.camera.data.lens=lens
    if kind=='geography':
        scene.camera.animation_data_clear();scene.camera.data.animation_data_clear();scene.camera.data.type='ORTHO';scene.camera.data.clip_start=.1;scene.camera.data.clip_end=12000
    rows=[]
    for f in frames:
        scene.frame_set(361 if kind=='geography' else f)
        if kind=='geography':
            from entrance190_motion_review import geography_camera
            geography_camera(scene,f/47)
        bpy.context.view_layer.update();path=out/f'frame-{f:04d}.png';scene.render.filepath=str(path);started=time.monotonic()
        if bpy.ops.render.render(write_still=True)!={'FINISHED'} or not path.exists():raise ValueError('Incomplete render')
        rows.append({'frame':f,'sha256':base.digest(path),'seconds':time.monotonic()-started})
        (out/'progress.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'frames':rows,'complete':False},indent=2)+'\n')
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'frames':rows,'fingerprint':struct,'cache_hashes':[x['sha256'] for x in r['caches']],'kind':kind,'resolution':[432,768],'persistent_data':False,'visual_gate':'NOT_RUN'},indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
