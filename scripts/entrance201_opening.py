"""Fixed opening dust derivative; accepted actor/terrain are preserved."""
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    from entrance201_dust import wake
    from entrance198_terrain import fingerprint
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    #02/04 remain retained failed natives with their original primary handler;
    #the current constructor exposes only the selected14 recipe.
    if job!={'operation':'opening14'}:raise ValueError('Fixed selected opening operation')
    source=base.BASE/'entrance200-seal17/scene.blend';out=base.BASE/('entrance201-'+job['operation'])
    if out.exists() or base.digest(source)!='0c898747a695db3e59ba8d8a9676961f306f91873c5f050e35d61f00d1a0623f':raise ValueError('Source/output')
    r=json.loads((source.parent/'result.json').read_text())
    for row in r['caches']:
        p=(source.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache changed')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    for name in ('entrance201_dust.py','entrance201_fit.py'):(out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;base.check_protected();dust=wake(scene,range(217,361));scene.render.use_persistent_data=False
    fit=None
    if job['operation'] in ('opening04','opening14'):
        from entrance201_fit import apply_opening
        fit=apply_opening(out)
    caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    scene.frame_set(217);bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.cycles.samples=12;scene.cycles.device='CPU'
    for f in (217,241,265,295,325,360):
        scene.frame_set(f);scene.render.filepath=str(out/('frame-%04d.png'%f));bpy.ops.render.render(write_still=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':base.digest(source),'native_sha256':base.digest(out/'scene.blend'),'caches':caches,'dust':dust,'fit':fit,'visual_gate':'NOT_RUN'},indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
