"""Closed source-bound review renders; no supplied scene paths or executable code."""
import json
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def cache_parity(record,out):
    import bpy
    import numpy as np
    from entrance189_groom import read_mdd
    from wardrobe185_lower_cloth import sample
    from wardrobe_motion178_controls import render_geometry_paused
    rows=[]
    with render_geometry_paused():
        for row in record['caches']:
            ob=bpy.data.objects[row['object']]
            if ob.hide_render:continue
            mods=[m for m in ob.modifiers if m.type=='MESH_CACHE']
            if len(mods)!=1 or list(ob.modifiers).index(mods[0])!=0:raise ValueError('Cache topology stack mismatch')
            m=mods[0];a=read_mdd(bpy.path.abspath(m.filepath));flags=[(x,x.show_viewport) for x in list(ob.modifiers)[1:]]
            for x,_ in flags:x.show_viewport=False
            ob.hide_viewport=False
            for f in (217,288,360):
                bpy.context.scene.frame_set(f);bpy.context.view_layer.update();p=sample(ob)
                i=int(np.clip(f-int(m.frame_start),0,len(a)-1))
                if p.shape!=a[i].shape:raise ValueError('Actual cache topology differs: '+ob.name)
                error=float(np.max(abs(p-a[i])))
                rows.append({'object':ob.name,'frame':f,'max_local_error':error})
                if error>1e-4:raise ValueError('Actual cache transfer failed: '+ob.name)
            ob.hide_viewport=True
            for x,state in flags:x.show_viewport=state
    (out/'cache-parity.json').write_text(json.dumps({'status':'PASS','rows':rows},indent=2)+'\n')


def validate(job):
    allowed=('controls03','motion04','lookA10','lookB11','parityA14','parityB15','lookB18','parityB19')
    if job not in [{'operation':x} for x in allowed]:raise ValueError('Fixed render operation required')
    stage='entrance193-painter13' if job['operation'] in ('lookB11','parityB15') else 'entrance193-bind03'
    if job['operation'] in ('lookB18','parityB19'):stage='entrance193-sampling16'
    source=base.BASE/stage/'scene.blend';out=base.BASE/('entrance193-'+job['operation'])
    r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Changed source or prior evidence')
    common=base.BASE/'entrance193-bind03';manifest=json.loads((common/'result.json').read_text())
    for row in manifest['caches']:
        p=(common/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Changed cache')
    if job['operation'] in ('lookA10','lookB11','parityA14','parityB15','lookB18','parityB19'):
        gate_stage=stage if job['operation'] in ('lookB18','parityB19') else 'entrance193-painter13'
        gate=json.loads((base.BASE/gate_stage/'internal-review.json').read_text())
        if gate.get('status')!='PROCEED_TO_COMPLETE_MOTION':raise ValueError('Matched still review is missing')
    return source,out,r


def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());source,out,r=validate(job)
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);base.check_protected()
    scene=bpy.context.scene;control=job['operation']=='controls03'
    if control:cache_parity(r,out)
    if job['operation']=='parityB19':
        cache_parity(json.loads((base.BASE/'entrance193-bind03/result.json').read_text()),out)
    # Only nonpersistent viewport flags: rendering retains original modifiers.
    flags=[];parity=job['operation'] in ('parityA14','parityB15','parityB19')
    for ob in scene.objects:
        for m in ob.modifiers:
            if not parity and m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF') and m.show_viewport:
                flags.append((ob.name,m.name,m.show_render));m.show_viewport=False
    final=job['operation'] in ('lookA10','lookB11','lookB18') or parity
    scene.cycles.device='CPU';scene.cycles.samples=8 if control or final else 4
    scene.render.use_persistent_data=True;scene.render.resolution_percentage=100
    scene.render.resolution_x=432 if control else 216;scene.render.resolution_y=768 if control else 384
    if final:scene.render.resolution_x=360;scene.render.resolution_y=640
    frames=(360,) if parity else ((265,271,360) if control else range(217,361))
    rows=[]
    for f in frames:
        start=time.monotonic();scene.frame_set(f)
        scene.render.filepath=str(out/f'frame-{f:04d}.png');result=bpy.ops.render.render(write_still=True)
        if result!={'FINISHED'} or not Path(scene.render.filepath).is_file():raise RuntimeError('Render canceled or missing frame')
        rows.append({'frame':f,'seconds':time.monotonic()-start})
        (out/'progress.json').write_text(json.dumps({'completed':len(rows),'total':len(frames),'last_frame':f,'measured_seconds':sum(x['seconds'] for x in rows)},indent=2)+'\n')
    base.check_protected()
    import hashlib
    sys.path.insert(0,str(ROOT/'src/movie_factory/adapters/blender'))
    from worker import action_channels
    actions=[]
    for action in sorted(bpy.data.actions,key=lambda a:a.name):
        actions.append({'name':action.name,'channels':[{'path':fc.data_path,'index':fc.array_index,
            'keys':[(list(k.co),k.interpolation) for k in fc.keyframe_points]} for fc in action_channels(action)]})
    animation_sha=hashlib.sha256(json.dumps(actions,sort_keys=True).encode()).hexdigest()
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'frames':rows,
        'animation_sha256':animation_sha,'viewport_only_flags':flags,'visual_gate':'NOT_RUN','native_modified':False,
        'resolution':[scene.render.resolution_x,scene.render.resolution_y],'fps':24},indent=2)+'\n')


if __name__=='__main__':main()
