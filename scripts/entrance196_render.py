"""Fixed source-bound controls and full-motion renders of196, no runtime code."""
import json
import sys
import time
import shutil
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

OPERATIONS={'controls03':('entrance196-build02',(217,265,309,348,354,360),360,640,8),
            'motion04':('entrance196-build02',tuple(range(217,361)),360,640,8),
            'head05':('entrance196-build02',tuple(range(337,361)),288,512,8),
            'head-before06':('entrance193-bind03',tuple(range(337,361)),288,512,8),
            'verify07':('entrance196-build02',(265,360),360,640,8),
            'controls10':('entrance196-refine09',(217,265,309,360),432,768,12),
            'motion11':('entrance196-refine09',tuple(range(217,361)),432,768,12),
            'verify12':('entrance196-refine09',(265,360),432,768,12),
            'controls14':('entrance196-compose13',(217,265,309,360),432,768,12),
            'motion15':('entrance196-compose13',tuple(range(217,361)),432,768,12),
            'verify16':('entrance196-compose13',(265,360),432,768,12),
            'controls18':('entrance196-seat17',(217,265,309,360),432,768,12),
            'motion19':('entrance196-seat17',tuple(range(217,361)),432,768,12),
            'verify20':('entrance196-seat17',(265,360),432,768,12),
            'controls22':('entrance196-ground21',(217,265,309,360),432,768,12),
            'motion23':('entrance196-ground21',tuple(range(217,361)),432,768,12),
            'verify24':('entrance196-ground21',(265,360),432,768,12),
            'controls26':('entrance196-ground25',(217,265,309,360),432,768,12),
            'motion27':('entrance196-ground25',tuple(range(217,361)),432,768,12),
            'verify28':('entrance196-ground25',(265,360),432,768,12),
            'controls31':('entrance196-outcrops30',(217,265,309,360),432,768,12),
            'motion32':('entrance196-outcrops30',tuple(range(217,361)),432,768,12),
            'verify33':('entrance196-outcrops30',(265,360),432,768,12),
            'controls37':('entrance196-integrate36',(217,265,295,309,325,360),432,768,12),
            'motion38':('entrance196-integrate36',tuple(range(217,361)),432,768,12),
            'verify39':('entrance196-integrate36',(265,295,360),432,768,12)}
FULL_CONTROLS={'motion11':'controls10','motion15':'controls14','motion19':'controls18','motion23':'controls22','motion27':'controls26','motion32':'controls31','motion38':'controls37'}


def validate(job):
    if set(job)!={'operation'} or job['operation'] not in OPERATIONS:raise ValueError('Fixed render operation required')
    stage,frames,w,h,samples=OPERATIONS[job['operation']];source=base.BASE/stage/'scene.blend';out=base.BASE/('entrance196-'+job['operation'])
    r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Source mismatch or old evidence')
    for row in r['caches']:
        p=(source.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache mismatch')
    if job['operation']=='motion04' or job['operation'] in FULL_CONTROLS:
        gate=json.loads((source.parent/'internal-review.json').read_text())
        if gate['status']!='PROCEED_TO_FULL_MOTION':raise ValueError('Still gate missing')
    return source,out,r,frames,w,h,samples


def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());source,out,r,frames,w,h,samples=validate(job)
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    if job['operation'] in ('controls31','verify33','controls37','verify39'):
        scene.frame_set(217);bpy.context.view_layer.update();points={};clearance=[]
        for ob in scene.objects:
            if not ob.name.startswith(('MF196_rock_cluster_','MF196_scanned_scree_','MF196_path_chip_')):continue
            if ob.data.name not in points:points[ob.data.name]=np.array([v.co[:] for v in ob.data.vertices])
            m=np.array(ob.matrix_world);p=points[ob.data.name]@m[:3,:3].T+m[:3,3]
            clearance.append(float(np.min(abs(p[:,0]))))
        if not clearance or min(clearance)<4.19:raise ValueError('Actual reopened rock footprint enters protected corridor')
        (out/'actual-clearance.json').write_text(json.dumps({'minimum_abs_x':min(clearance),'objects':len(clearance),'scope':'Actual reopened vertex footprints at217; terrain parent translation only along Y'},indent=2)+'\n')
    if job['operation'].startswith('verify'):
        from entrance193_render import cache_parity
        cache_parity(r,out)
    else:
        for ob in scene.objects:
            for m in ob.modifiers:
                if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    if job['operation'].startswith('head'):
        # Independent locked close camera exposes actual motion rather than
        # camera compensation. Same source framing for both candidates.
        scene.frame_set(360);bpy.context.view_layer.update();cam=scene.camera
        matrix=cam.matrix_world.copy();lens=cam.data.lens
        cam.animation_data_clear();cam.data.animation_data_clear();cam.matrix_world=matrix;cam.data.lens=lens
    scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.resolution_percentage=100
    scene.cycles.device='CPU';scene.cycles.samples=samples;scene.render.use_persistent_data=True
    rows=[];ordered=frames
    if job['operation'] in FULL_CONTROLS:
        overview=(217,235,253,265,277,295,309,325,343,360)
        ordered=overview+tuple(f for f in frames if f not in overview)
    for frame in ordered:
        scene.frame_set(frame);start=time.monotonic();path=out/f'frame-{frame:04d}.png';scene.render.filepath=str(path)
        reused=False
        reuse_frames=(217,265,295,309,325,360) if job['operation']=='motion38' else (217,265,309,360)
        if job['operation'] in FULL_CONTROLS and frame in reuse_frames:
            control=base.BASE/('entrance196-'+FULL_CONTROLS[job['operation']]);cr=json.loads((control/'result.json').read_text())
            if cr['source_sha256']!=r['native_sha256'] or cr['resolution']!=[w,h]:raise ValueError('Control mismatch')
            shutil.copy2(control/path.name,path);reused=True
        else:
            status=bpy.ops.render.render(write_still=True)
            if status!={'FINISHED'} or not path.is_file():raise RuntimeError('Cancelled or missing frame')
        rows.append({'frame':frame,'seconds':time.monotonic()-start,'reused_control':reused})
        (out/'progress.json').write_text(json.dumps({'completed':len(rows),'total':len(frames),'last_frame':frame},indent=2)+'\n')
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'resolution':[w,h],'samples':samples,'fps':24,'frames':rows,
        'visual_gate':'NOT_RUN','native_modified':False,'fixed_close_camera':job['operation'].startswith('head')},indent=2)+'\n')


if __name__=='__main__':main()
