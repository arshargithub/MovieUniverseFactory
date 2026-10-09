"""Persist the demonstrated cache-safe render setting in an immutable derivative."""
import sys,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance200_inspect import base
SOURCE_SHA='dd7cac52d8ab6d0c41c23d01e3c9678c0db482f0e9db52ec7978eb88c02310e5'

def main():
    import bpy
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'seal17'}:raise ValueError('Fixed seal only')
    source=base.BASE/'entrance200-candidate10/scene.blend';out=base.BASE/'entrance200-seal17'
    if out.exists() or base.digest(source)!=SOURCE_SHA:raise ValueError('Source/history mismatch')
    r=json.loads((source.parent/'result.json').read_text())
    for row in r['caches']:
        p=(source.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache mismatch')
    out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    scene.render.use_persistent_data=False;caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p)
                caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    shutil.copy2(source.parent/'motion.npz',out/'motion.npz');shutil.copy2(Path(__file__),out/'handler.py')
    r.update({'source_sha256':SOURCE_SHA,'original198_sha256':r['source_sha256'],'native_sha256':base.digest(out/'scene.blend'),'caches':caches,
              'render_profile':{'persistent_data':False,'reason':'14 control removes temporal black-groom failure seen in07 without artwork changes'},
              'visual_gate':'FULL_NONPERSISTENT_SEQUENCE_PENDING','neutral_geometry':'controls11 zero neutral correction; source10 otherwise unchanged'})
    (out/'result.json').write_text(json.dumps(r,indent=2)+'\n')

if __name__=='__main__':main()
