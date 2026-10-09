"""Closed native review operations for the integrated201 entrance."""
import json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
OPS={
 'route05':('route03','route',(361,385,409,433,457,481,505,529,552)),
 'opening06':('opening14','opening',tuple(range(217,361))),
 'attention07':('opening14','attention',tuple(range(289,337))),
 'route08':('route16','route',tuple(range(361,553))),
 'geography09':('route16','geography',tuple(range(48))),
 'openverify10':('opening14','opening',(217,295,343,350,360)),
 'routeverify11':('route16','route',(361,457,552)),
 'attention12':('opening14','attention',(289,312,336)),
 'geography13':('route16','geography',(0,24,47)),
}

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
