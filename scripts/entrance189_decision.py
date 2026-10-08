"""Film the existing attention phase from the revealing camera; no actor mutation."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def validate(job):
    if job not in ({'operation':'decision-overview19'},{'operation':'decision-motion20'}):
        raise ValueError('Fixed decision-shot operation required')
    source=base.BASE/'entrance189-performance14/scene.blend'
    record=json.loads((source.parent/'result.json').read_text())
    if source.is_symlink() or base.digest(source)!=record['native_sha256']:raise ValueError('Changed acting source')
    for row in record['caches']:
        p=(source.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Changed cache')
    out=base.BASE/('entrance189-'+job['operation'])
    if out.exists():raise ValueError('Preserve prior frames')
    if job['operation']=='decision-motion20':
        review=json.loads((base.BASE/'entrance189-decision-overview19/internal-review.json').read_text())
        if review.get('status')!='PROCEED_TO_COMPLETE_MOTION' or review.get('source_sha256')!=record['native_sha256']:
            raise ValueError('Decision camera overview not admitted')
    return source,out,record


def main():
    import bpy
    import shutil
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    job=json.loads(Path(args[0]).read_text());source,out,record=validate(job)
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    base.check_protected();scene=bpy.context.scene
    scene.cycles.device='CPU';scene.render.use_persistent_data=True
    if job['operation']=='decision-overview19':
        # Actual-source larger controls distinguish lost preview detail from
        # missing scene detail. They do not certify final-release rendering.
        scene.cycles.samples=24;scene.render.resolution_x=1080;scene.render.resolution_y=1920
        scene.render.resolution_percentage=100
        for f in (309,360):
            scene.frame_set(f);bpy.context.view_layer.update()
            scene.render.filepath=str(out/('large-%04d.png'%f));bpy.ops.render.render(write_still=True)
    scene.frame_set(360);bpy.context.view_layer.update()
    camera=scene.camera;matrix=camera.matrix_world.copy();lens=camera.data.lens
    camera.animation_data_clear();camera.data.animation_data_clear();camera.matrix_world=matrix;camera.data.lens=lens
    scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=True
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    overview=list(range(289,337,6))+[336];frames=overview
    if job['operation']=='decision-motion20':
        prior=base.BASE/'entrance189-decision-overview19'
        for f in overview:shutil.copy2(prior/('frame-%04d.png'%f),out/('frame-%04d.png'%f))
        frames=[f for f in range(289,337) if f not in overview]
    from entrance189_performance import facial_values
    body=bpy.data.objects['MF_studio_adult_body'];rows=[]
    for f in frames:
        scene.frame_set(f);bpy.context.view_layer.update()
        error=max(abs(body.data.shape_keys.key_blocks[n].value-v) for n,v in facial_values(f).items())
        if error>1e-5:raise ValueError('Face-source replay mismatch')
        scene.render.filepath=str(out/('frame-%04d.png'%f));bpy.ops.render.render(write_still=True)
        rows.append({'frame':f,'face_transfer_error':error})
        print('189 DECISION FRAME',f,flush=True)
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':record['native_sha256'],'frames':rows,
        'fps':24,'camera_matrix':[list(r) for r in matrix],'lens':lens,'actor_and_cache_edits':False,
        'protected_data_exact':True,'visual_gate':'NOT_RUN',
        'scope':'Two-second native attention coverage; story geography still requires the route reveal and turn'},indent=2)+'\n')


if __name__=='__main__':main()
