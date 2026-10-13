"""Closed source-bound245 render and replay operations. No code/path payloads."""
import json,sys,time,os
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
OUT=ROOT/'.runtime/art-direction/series01-finish245'
OPS={
 'opening-coarse':('opening',tuple(range(217,451,3)),216,2,'CPU'),
 'route-coarse':('route',tuple(range(451,757,3)),216,2,'CPU'),
 'opening-control':('opening',(217,305,306,307,355,390,450),432,8,'CPU'),
 'route-control':('route',(451,475,497,498,499,523,580,631,700,756),432,8,'CPU'),
 'cpu-delivery':('opening',(217,390),1080,16,'CPU'),
 'gpu-delivery':('opening',(217,390,217),1080,16,'GPU'),
 'gpu-delivery02':('opening',(217,390,217),1080,16,'GPU'),
 'gpu-cache-control':('opening',(217,)+tuple(range(380,396))+(217,390),1080,16,'GPU'),
 'gpu-cache-route':('route',(475,523)+tuple(range(625,637))+(700,475,631),1080,16,'GPU'),
 'gpu-route':('route',(475,523,631,700),1080,16,'GPU'),
 'gpu-route02':('route',(475,523,631,700),1080,16,'GPU'),
 'opening-final':('opening',tuple(range(217,451)),1080,16,'GPU'),
 'opening-resume-final':('opening',tuple(range(217,451)),1080,16,'GPU'),
 'route-final':('route',tuple(range(451,757)),1080,16,'GPU'),
 'opening-reopen':('opening',(217,305,390,450),1080,16,'GPU'),
 'route-reopen':('route',(475,498,499,631,700,756),1080,16,'GPU'),
}
def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Closed245 render')
    return OPS[job['operation']]
def main():
    import bpy
    from worker import action_channels
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());kind,frames,width,samples,device=validate(job)
    op=job['operation'];version='01' if kind=='opening' else ('02' if op=='gpu-route' else '03')
    folder=base.BASE/('finish245-'+kind+version);src=folder/'scene.blend'
    rec=json.loads((folder/'result.json').read_text());out=OUT/op
    if out.exists() or base.digest(src)!=rec['native_sha256']:raise ValueError('Source/output mismatch')
    for c in rec['caches']:
        if base.digest((folder/c['path']).resolve())!=c['sha256']:raise ValueError('Changed cache')
    if op.endswith('final'):
        g=json.loads((OUT/'render-admission.json').read_text())
        if g['status']!='PROCEED_TO_COMPLETE_RENDER' or g[kind]!=rec['native_sha256']:raise ValueError('Missing current visual admission')
        audit=json.loads((OUT/'route-audit02.json').read_text())['preserved_route_authored_channels']
        if audit['maximum_difference']!=0 or audit['evaluated_camera_world_maximum_difference']>1e-6:
            raise ValueError('Preserved motion audit failed')
    out.mkdir(parents=True);(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);s=bpy.context.scene
    for ob in s.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    if device=='GPU':
        if op!='gpu-delivery' and os.environ.get('CYCLES_METAL_DISABLE_BINARY_ARCHIVES')!='1':
            raise ValueError('245 GPU control requires binary archive workaround, not a silent profile change')
        p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL'
        ds=p.get_devices_for_type('METAL')
        if not any(d.type=='METAL' for d in ds):raise ValueError('No GPU; no silent fallback')
        for d in ds:d.use=d.type=='METAL'
        p.metalrt='ON'
    persistent=op.startswith('gpu-cache-')
    s.render.engine='CYCLES';s.cycles.device=device;s.cycles.samples=samples;s.render.use_persistent_data=persistent
    s.render.resolution_x=width;s.render.resolution_y=width*16//9;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8'
    s.render.use_motion_blur=False
    rows=[];reuse={}
    if op.endswith('final'):
        previous=OUT/('gpu-delivery02' if kind=='opening' else 'gpu-route02')
        proof=json.loads((previous/'result.json').read_text())
        if proof['source_sha256']!=rec['native_sha256'] or proof['profile']!=dict(width=width,samples=samples,device=device,metalrt='ON',persistent=False):raise ValueError('Incompatible proof reuse')
        for row in proof['frames']:
            if row['frame'] not in reuse:reuse[row['frame']]=(previous/row['file'],row['sha256'])
        if op=='opening-resume-final':
            prior_folder=OUT/'opening-final';partial=json.loads((prior_folder/'progress.json').read_text())
            if partial['source_sha256']!=rec['native_sha256'] or partial['profile']!=proof['profile']:
                raise ValueError('Partial frames are not source/profile compatible')
            for row in partial['frames']:
                reuse[row['frame']]=(prior_folder/row['file'],row['sha256'])
    for i,f in enumerate(frames):
        t=time.monotonic();s.frame_set(f);path=out/f'frame-{f-217:04d}.png'
        if path.exists():path=out/f'repeat-{i:02d}-{f-217:04d}.png'
        reused=None
        if f in reuse:
            prior,digest=reuse[f]
            if base.digest(prior)!=digest:raise ValueError('Changed proof frame')
            os.link(prior,path);reused=str(prior.relative_to(ROOT))
        else:
            s.render.filepath=str(path)
            if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise RuntimeError('Render cancelled; incomplete frame is not acknowledged')
        rows.append(dict(frame=f,index=f-217,file=path.name,seconds=time.monotonic()-t,sha256=base.digest(path),reused_from=reused))
        result=dict(source_sha256=rec['native_sha256'],profile=dict(width=width,samples=samples,device=device,metalrt='ON' if device=='GPU' else None,persistent=persistent),binary_archives_disabled=os.environ.get('CYCLES_METAL_DISABLE_BINARY_ARCHIVES')=='1',frames=rows,complete=False)
        (out/'progress.json').write_text(json.dumps(result,indent=2)+'\n');print('245',op,f,round(rows[-1]['seconds'],2),flush=True)
    result['complete']=True;(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');base.check_protected()
if __name__=='__main__':main()
