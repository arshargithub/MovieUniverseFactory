"""Read-only, closed-operation Blender dependency inspection; no scene edits/save."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RESTORE=ROOT/'.runtime/protection255-restore'
OPS={'inspect-restored-opening':'opening08','inspect-restored-route':'route09'}

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job.get('operation') not in OPS:
        raise ValueError('Closed protection inspection operation')
    return RESTORE/'.runtime/art-direction/series01-finish248'/OPS[job['operation']]/'scene.blend'

def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    source=validate(job)
    if not source.is_file():raise ValueError('Restored native absent')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    refs=[]
    for image in bpy.data.images:
        if image.source in {'GENERATED','VIEWER'} or image.packed_file or getattr(image,'packed_files',[]):continue
        if image.filepath:refs.append(('image',image.name,image.filepath))
    for library in bpy.data.libraries:refs.append(('library',library.name,library.filepath))
    for obj in bpy.data.objects:
        for mod in obj.modifiers:
            if mod.type=='MESH_CACHE' and mod.filepath:refs.append(('mesh_cache',obj.name,mod.filepath))
    checked=[]
    for kind,name,path in refs:
        resolved=Path(bpy.path.abspath(path)).resolve()
        checked.append({'kind':kind,'name':name,'path':path,'inside_restore':resolved.is_relative_to(RESTORE.resolve()),'exists':resolved.is_file()})
    errors=[r for r in checked if not r['inside_restore'] or not r['exists']]
    # Dependency access/evaluation only; no pixel replay or motion-quality claim.
    for frame in (217,360) if 'opening' in job['operation'] else (475,631):
        bpy.context.scene.frame_set(frame)
        bpy.context.evaluated_depsgraph_get().update()
    dest=ROOT/'results/backup/protect255'/('native-'+job['operation']+'.json')
    dest.write_text(json.dumps({'operation':job['operation'],'blend_version':bpy.app.version_string,'references':checked,
       'dependency_scope':'unpacked images, linked libraries, mesh-cache modifiers; not all possible add-on dependencies',
       'passed':not errors,'errors':errors,'rendered':False,'scene_saved':False},indent=2)+'\n')
    if errors:raise RuntimeError('Restored dependency escape/missing; see report')

if __name__=='__main__':main()
