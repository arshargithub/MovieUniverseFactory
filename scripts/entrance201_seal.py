"""Seal the matched15 dust treatment; all route/actor/caches stay unchanged."""
import json,os,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    from entrance201_dust_control import treatment
    from entrance198_terrain import fingerprint
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'route16'}:raise ValueError('Fixed seal')
    source=base.BASE/'entrance201-route03/scene.blend';out=base.BASE/'entrance201-route16';r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!='63877ab66c4713921c9fbcb21310cd15cdf108a523a64dc05cd16a5d28e4b52d':raise ValueError('Source/output')
    gate=json.loads((base.BASE/'entrance201-dust15/internal-review.json').read_text())
    if gate.get('status')!='PROCEED_TO_SEAL' or gate.get('source_sha256')!=r['native_sha256']:raise ValueError('No matched control admission')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());(out/'entrance201_dust_control.py').write_bytes((ROOT/'scripts/entrance201_dust_control.py').read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(361);before=fingerprint(scene);base.check_protected()
    treatment(bpy.data.materials['201 shaded sunlit earth wake']);scene.render.use_persistent_data=False;caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    if fingerprint(scene)!=before:raise ValueError('Material-only seal changed structure')
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    shutil.copy2(source.parent/'rig.npz',out/'rig.npz');r.update(source_sha256=base.digest(source),native_sha256=base.digest(out/'scene.blend'),caches=caches,fingerprint=before,visual_gate='FULL_MOTION_PENDING')
    r['dust'].update(profile='selected',density_gain=.09,emission_density_gain=.20,modulation='max(2.5*noise-.55,.02)')
    (out/'result.json').write_text(json.dumps(r,indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
