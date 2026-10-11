"""Reopen and render only the reviewed214 native derivatives and fixed clocks."""
import json
import sys
import time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

OPS={
    'proof09':('opening08',(245,277,300,330,360),False),
    'proof10':('route07',(390,427,472,550,620),False),
    'motion11':('opening08',tuple(range(217,361)),True),
    'motion12':('route07',tuple(range(361,649)),True),
}

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:
        raise ValueError('Closed214 review operation required')
    return OPS[job['operation']]

def main():
    import bpy
    from entrance198_terrain import fingerprint
    from mathutils import Vector
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());folder,frames,full=validate(job)
    src=base.BASE/('entrance214-'+folder);out=base.BASE/('entrance214-'+job['operation'])
    record=json.loads((src/'result.json').read_text())
    if out.exists() or base.digest(src/'scene.blend')!=record['native_sha256'] or base.digest(src/'contact.npz')!=record['contact_sha256']:
        raise ValueError('Native/evidence changed or output exists')
    if full:
        admission=json.loads((src/'internal-review.json').read_text())
        if admission.get('status')!='PROCEED_TO_FULL_MOTION' or admission.get('source_sha256')!=record['native_sha256']:
            raise ValueError('Visual admission required')
    for row in record['caches']:
        path=(src/row['path']).resolve()
        if not path.is_relative_to(base.BASE.resolve()) or base.digest(path)!=row['sha256']:raise ValueError('Cache drift')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene
    base.check_protected()
    if fingerprint(scene)['geometry']!=record['protected_geometry_sha256']:raise ValueError('Geometry drift on reopen')
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
    scene.render.threads_mode='FIXED';scene.render.threads=8
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    with np.load(src/'contact.npz') as z:data={k:z[k].copy() for k in z.files}
    rig=bpy.data.objects['MF_body156_fit_rig'];rows=[]
    for f in frames:
        t=time.monotonic();scene.frame_set(f);bpy.context.view_layer.update();i=list(data['frames']).index(f)
        pose=np.array([np.array(rig.matrix_world@rig.pose.bones[str(n)].matrix) for n in data['names']])
        pose_error=float(abs(pose-data['before'][i]).max())
        camera_error=max(float(abs(np.array(scene.camera.matrix_world)-data['cameras'][i]).max()),abs(scene.camera.data.lens-data['lenses'][i]))
        thumb_error=float(abs(np.array([np.array(rig.pose.bones[str(n)].matrix_basis) for n in data['thumb_names']])-data['thumb_bases'][i]).max())
        pts=np.array([[list(ob.matrix_world@p.co.to_3d()) for p in ob.data.splines[0].points]
                      for ob in [bpy.data.objects['MF185_rein_'+s] for s in ('L','R')]])
        rein_error=float(abs(pts-data['reins'][i]).max())
        if max(pose_error,camera_error,thumb_error,rein_error)>2e-5:raise ValueError('Reopen motion or contact mismatch')
        p=out/f'frame-{f-217:04d}.png';scene.render.filepath=str(p)
        if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise ValueError('Render failed')
        row=dict(index=f-217,native_frame=f,sha256=base.digest(p),seconds=time.monotonic()-t,
                 protected_pose_error=pose_error,camera_error=camera_error,thumb_error=thumb_error,rein_error=rein_error)
        rows.append(row)
        tmp=out/'progress.tmp';tmp.write_text(json.dumps(dict(source_sha256=record['native_sha256'],frames=rows,complete=False),indent=2)+'\n');tmp.replace(out/'progress.json')
        print('214 FRAME',f,round(row['seconds'],2),flush=True)
    base.check_protected()
    (out/'result.json').write_text(json.dumps(dict(source_sha256=record['native_sha256'],frames=rows,complete=True,
       fps=24,resolution=[432,768],visual_gate='NOT_RUN'),indent=2)+'\n')

if __name__=='__main__':main()
