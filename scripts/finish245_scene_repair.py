"""Correct only245 added scenery using current207 sentry anchor provenance."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
def main():
    import bpy
    from entrance205_actor import save
    from finish245_checkpoint import build
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'scenery02'},{'operation':'scenery03'}):raise ValueError('Closed scenery repair')
    newer=job['operation']=='scenery03'
    src=base.BASE/('finish245-route02' if newer else 'finish245-route01');out=base.BASE/('finish245-route03' if newer else 'finish245-route02');rec=json.loads((src/'result.json').read_text())
    if out.exists() or base.digest(src/'scene.blend')!=rec['native_sha256']:raise ValueError('Source/output')
    bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);s=bpy.context.scene;s.frame_set(451)
    for ob in list(s.objects):
        if ob.name.startswith('MF245_'):bpy.data.objects.remove(ob,do_unlink=True)
    out.mkdir();scenery=build(s,'route','visible03' if newer else 'original');save(s,out,dict(source_sha256=rec['native_sha256'],scenery=scenery,change='Only245 new guard/camp positioning; retained original sentries, actors/camera/caches unchanged'))
    for ob in s.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.render.use_persistent_data=False
    s.render.resolution_x=432;s.render.resolution_y=768;s.render.resolution_percentage=100
    for f in ((475,) if newer else (451,475,498,631)):
        s.frame_set(f);s.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True);print('245 SCENERY',f,flush=True)
    base.check_protected()
if __name__=='__main__':main()
