"""Source-bound native still and complete-motion terrain review."""
import json,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance198_terrain import fingerprint
OPERATIONS={'controls03':(217,223,228,295,325,360),'motion04':tuple(range(217,361)),'verify05':(223,295,360)}

def validate(job):
    if set(job)!={'operation'} or job['operation'] not in OPERATIONS:raise ValueError('Fixed render only')
    source=base.BASE/'entrance198-build02/scene.blend';out=base.BASE/('entrance198-'+job['operation'])
    r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Source mismatch or retained output')
    for row in r['caches']:
        p=(source.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache mismatch')
    if job['operation']=='motion04':
        gate=json.loads((source.parent/'internal-review.json').read_text())
        if gate.get('status')!='PROCEED_TO_FULL_MOTION' or gate.get('source_sha256')!=r['native_sha256']:raise ValueError('Source-matched still gate missing')
    return source,out,r

def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());source,out,r=validate(job);op=job['operation']
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(217);base.check_protected()
    actual=fingerprint(scene)
    (out/'structural-parity.json').write_text(json.dumps({'status':'PASS' if actual==r['fingerprint'] else 'FAIL','expected':r['fingerprint'],'actual':actual},indent=2)+'\n')
    if actual!=r['fingerprint']:raise ValueError('Reopened structure differs')
    if op=='verify05':
        from entrance193_render import cache_parity
        from entrance196_render import particle_parity
        cache_parity(r,out);particle_parity(scene,out)
    else:
        for o in scene.objects:
            for m in o.modifiers:
                if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=True
    frames=OPERATIONS[op]
    if op=='motion04':
        overview=(217,235,253,265,277,295,309,325,343,360);frames=overview+tuple(f for f in frames if f not in overview)
    rows=[]
    for f in frames:
        start=time.monotonic();scene.frame_set(f);path=out/f'frame-{f:04d}.png';scene.render.filepath=str(path);reuse=False
        if op=='motion04' and f in OPERATIONS['controls03']:
            control=base.BASE/'entrance198-controls03';cr=json.loads((control/'result.json').read_text())
            if cr['source_sha256']!=r['native_sha256'] or cr['resolution']!=[432,768] or cr['samples']!=12:raise ValueError('Control source/settings mismatch')
            shutil.copy2(control/path.name,path);reuse=True
        else:
            if bpy.ops.render.render(write_still=True)!={'FINISHED'} or not path.is_file():raise ValueError('Incomplete frame')
        rows.append({'frame':f,'seconds':time.monotonic()-start,'reused_control':reuse})
        (out/'progress.json').write_text(json.dumps({'completed':len(rows),'total':len(frames),'last_frame':f},indent=2)+'\n')
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'frames':rows,'resolution':[432,768],'samples':12,'fps':24,'native_modified':False,'visual_gate':'NOT_RUN','viewport_acceleration':op!='verify05'},indent=2)+'\n')

if __name__=='__main__':main()
