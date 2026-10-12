"""Source-bound render/control operations for237; no arbitrary paths/code."""
import json,sys,time,struct
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
OPS={'opening-control':('opening01',[331,354,394],432,8),
     'route-control':('route02',[415,422,432,433,450,462,463,515,620,720],432,8),
     'opening-motion':('opening01',range(217,415,2),216,2),
     'route-motion':('route02',range(415,721,2),216,2),
     'opening-full':('opening01',range(217,415),432,8),
     'route-full':('route02',range(415,721),432,8)}
OPS.update({'opening03-clay':('opening03',range(217,415,2),432,0),
    'route04-clay':('route04',range(415,721,2),432,0),
    'opening03-full':('opening03',range(217,415),432,8),
    'route04-full':('route04',range(415,721),432,8),
    'opening03-reopen':('opening03',[217,270,271,331,354,414],432,8),
    'route04-reopen':('route04',[415,422,432,433,462,463,620,720],432,8)})
def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Closed237 review')
    op=job['operation'];folder,frames,width,samples=OPS[op];src=base.BASE/('finish237-'+folder)
    r=json.loads((src/'result.json').read_text());out=ROOT/'.runtime/art-direction/series01-finish237'/op
    if out.exists() or base.digest(src/'scene.blend')!=r['native_sha256']:raise ValueError('Source/output')
    if op.endswith('full'):
        gate=json.loads((src/'internal-review.json').read_text())
        if gate.get('status')!='PROCEED_TO_FULL_MOTION' or gate['source_sha256']!=r['native_sha256']:raise ValueError('No visual admission')
    for row in r['caches']:
        if base.digest((src/row['path']).resolve())!=row['sha256']:raise ValueError('Cache changed')
    out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                with Path(bpy.path.abspath(m.filepath)).open('rb') as f:nf,nv=struct.unpack('>ii',f.read(8))
                if nv!=len(ob.data.vertices) or list(ob.modifiers).index(m)!=0:raise ValueError('Cache topology/order '+ob.name)
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.resolution_x=width;scene.render.resolution_y=width*16//9;scene.render.resolution_percentage=100
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=samples;scene.render.use_persistent_data=False
    if samples==0:
        scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
        for ob in scene.objects:
            if any(s in ob.name.lower() for s in ('dust','wake')):ob.hide_render=True
    rows=[]
    for f in frames:
        start=time.monotonic();scene.frame_set(f);path=out/f'frame-{f-217:04d}.png';scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True);rows.append(dict(frame=f,index=f-217,sha256=base.digest(path),seconds=time.monotonic()-start))
        (out/'progress.json').write_text(json.dumps(dict(source_sha256=r['native_sha256'],frames=rows,complete=False),indent=2)+'\n');print('237 REVIEW',op,f,round(rows[-1]['seconds'],2),flush=True)
    (out/'result.json').write_text(json.dumps(dict(source_sha256=r['native_sha256'],frames=rows,complete=True),indent=2)+'\n');base.check_protected()
if __name__=='__main__':main()
