"""20-second source-bound final renders/replay; one local Metal worker."""
import json,sys,time,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from finish248_fist import OUT,surface_config,base
OPS={
 'opening-final':('opening08',range(217,451)),
 'route-final':('route09',range(451,697)),
 'opening-reopen':('opening08',(305,360,410,450)),
 'route-reopen':('route09',(475,499,523,580,631,676,696)),
}
PROFILE={'width':1080,'height':1920,'samples':16,'device':'METAL','metalrt':'ON','persistent':False,'motion_blur':False}
def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Closed248 render')
    return OPS[job['operation']]
def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());name,frames=validate(job);op=job['operation']
    src=OUT/name;rec=json.loads((src/'result.json').read_text())
    if base.digest(src/'scene.blend')!=rec['native_sha256']:raise ValueError('Source changed')
    for c in rec['caches']:
        if base.digest((src/c['path']).resolve())!=c['sha256']:raise ValueError('Cache changed')
    admission=json.loads((OUT/'render-admission.json').read_text())
    if admission['status']!='PROCEED_TO_RENDER' or admission['sources'][name]!=rec['native_sha256']:raise ValueError('No current admission')
    dest=OUT/op;dest.mkdir(exist_ok=True)
    rows=[]
    if (dest/'progress.json').exists():
        old=json.loads((dest/'progress.json').read_text())
        if old['source_sha256']!=rec['native_sha256'] or old['profile']!=PROFILE:raise ValueError('Cannot resume different source/profile')
        rows=old['frames']
        if [r['frame'] for r in rows]!=list(frames)[:len(rows)]:raise ValueError('Invalid resume chronology')
        for r in rows:
            if base.digest(dest/r['file'])!=r['sha256']:raise ValueError('Changed acknowledged frame')
    bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene
    base.check_protected();surface_config(scene)
    for f in list(frames)[len(rows):]:
        start=time.monotonic();scene.frame_set(f);path=dest/f'frame-{f-217:04d}.png'
        if path.exists():raise ValueError('Unacknowledged frame needs explicit recovery review')
        scene.render.filepath=str(path)
        if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise RuntimeError('Incomplete frame')
        rows.append({'frame':f,'index':f-217,'file':path.name,'sha256':base.digest(path),'seconds':time.monotonic()-start})
        record={'source_sha256':rec['native_sha256'],'profile':PROFILE,'frames':rows,'complete':False}
        (dest/'progress.json').write_text(json.dumps(record,indent=2)+'\n')
        print('248',op,f,round(rows[-1]['seconds'],2),flush=True)
    record={'source_sha256':rec['native_sha256'],'profile':PROFILE,'frames':rows,'complete':True}
    (dest/'result.json').write_text(json.dumps(record,indent=2)+'\n')
    base.check_protected()
if __name__=='__main__':main()
