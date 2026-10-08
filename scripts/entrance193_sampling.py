"""One-variable control: do not sample illustrated surfaces as scene lights."""
import json
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def validate(job):
    if job!={'operation':'sampling16'}:raise ValueError('Fixed sampling control required')
    source=base.BASE/'entrance193-painter13/scene.blend';out=base.BASE/'entrance193-sampling16'
    if out.exists() or base.digest(source)!='5ffaf021e95b9ff8a93a7615bc9b4871c703525f8be0ef6d667a0f51f9653151':
        raise ValueError('Changed source or existing output')
    return source,out


def main():
    import bpy
    source,out=validate(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text()))
    record=json.loads((source.parent/'result.json').read_text())
    manifest=json.loads((base.BASE/'entrance193-bind03/result.json').read_text())
    for row in manifest['caches']:
        p=(base.BASE/'entrance193-bind03'/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache changed')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);base.check_protected()
    changes=[]
    for row in record['changes']:
        mat=bpy.data.materials[row['material']]
        changes.append({'material':mat.name,'before':mat.cycles.emission_sampling,'after':'NONE'})
        mat.cycles.emission_sampling='NONE'
    base.check_protected()
    for ob in bpy.context.scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':m.filepath=bpy.path.abspath(m.filepath)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    native_sha=base.digest(out/'scene.blend');scene=bpy.context.scene
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    scene.render.resolution_percentage=100;scene.render.resolution_x=360;scene.render.resolution_y=640
    rows=[]
    for f in (217,218,360):
        start=time.monotonic();scene.frame_set(f);scene.render.filepath=str(out/f'frame-{f:04d}.png')
        bpy.ops.render.render(write_still=True);rows.append({'frame':f,'seconds':time.monotonic()-start})
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':base.digest(source),'native_sha256':native_sha,
        'sampling_changes':changes,'frames':rows,'visual_gate':'NOT_RUN',
        'method':'Same shader graphs and scene; illustrated materials excluded from explicit emissive-light sampling only'},indent=2)+'\n')


if __name__=='__main__':main()
