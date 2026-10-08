"""Repair first derivative's incorrectly rebased cache paths without recalculation."""
import json
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def main():
    import bpy
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'bind03'}:raise ValueError('Fixed repair only')
    source=base.BASE/'entrance193-motion02/scene.blend';out=base.BASE/'entrance193-bind03'
    r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Changed source or existing output')
    for row in r['caches']:
        p=(source.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Changed cache')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    for row in r['caches']:
        ob=bpy.data.objects[row['object']];mods=[m for m in ob.modifiers if m.type=='MESH_CACHE']
        if len(mods)!=1 or list(ob.modifiers).index(mods[0])!=0:raise ValueError('Cache stack topology mismatch')
        p=(source.parent/row['path']).resolve();mods[0].filepath=str(p)
        row['path']=os.path.relpath(p,out)
    base.check_protected();bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    r['motion02_sha256']=r['native_sha256'];r['native_sha256']=base.digest(out/'scene.blend')
    r['path_repair']='Absolute cache paths resolved before save; relative paths created only after new scene location exists'
    (out/'result.json').write_text(json.dumps(r,indent=2)+'\n')


if __name__=='__main__':main()
