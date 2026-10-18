"""Reviewed structured operation entry; never executes asset scripts."""
import sys,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from movie_factory import sikh305_motion as c
from sikh257_native import camera_at
BASE=ROOT/'.runtime/art-direction/series01-sikh305'
def main():
    path=Path(sys.argv[sys.argv.index('--')+1]);j=c.validate(json.loads(path.read_text()));op=j['operation'];v=j['version'];out=BASE/f'{"build" if op in ("refine","finish") else op}-{v:02d}'
    if path.resolve()!=out/'job.json':raise ValueError('Unadmitted job path')
    parent=7 if op=='refine' and v==9 else 11 if op=='finish' and v==13 else v-1
    src=ROOT/'.runtime/art-direction/series01-sikh304/repair-build-03/sequence.blend' if op in ('build','inspect') else BASE/f'build-{parent if op in ("refine","finish") else v:02d}/sequence.blend'
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);s=bpy.context.scene
    if op=='inspect':
        s.frame_set(1);bpy.context.view_layer.update()
        objects=[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':list(o.location),'world':list(o.matrix_world.translation),'materials':[m.name for m in o.data.materials] if o.type in ('MESH','CURVE') else []} for o in s.objects if any(k in o.name.lower() for k in ('horse','torch','flame','basket','leader','courtyard','mane','tail'))]
        (out/'objects.json').write_text(json.dumps(objects,indent=2))
        rig=bpy.data.objects['horse.rig'];(out/'bones.json').write_text(json.dumps({b.name:{'parent':b.parent.name if b.parent else None,'head':list(b.head),'tail':list(b.tail),'matrix':list(map(list,b.matrix)),'rest':list(map(list,b.bone.matrix_local))} for b in rig.pose.bones},indent=2))
        return
    if op in ('build','refine','finish'):
        from sikh305_scene import build,horse
        if op=='build':build(out)
        else:
            crops=[o for o in bpy.data.objects if o.name.startswith(('304 cultivated','305 departure parcel','304 boundary tree'))]
            for o in crops:o.hide_viewport=True
            if op=='refine':horse(out,rebuild_groom=v in (8,9,10,11))
            for o in crops:o.hide_viewport=False
            for name in ('coordinated-motion.json','camera-relative.json','construction.json','greeting-eyeline.json','contact-records.json'):
                shutil.copy2(BASE/f'build-{parent:02d}'/name,out/name)
            if op=='finish':
                shutil.copy2(BASE/f'build-{parent:02d}'/'whole-horse-motion.json',out/'whole-horse-motion.json')
                from sikh305_finish import finish,final_interfaces
                if v in (12,13):
                    shutil.copy2(BASE/f'build-{parent:02d}'/'impact-events.json',out/'impact-events.json')
                    final_interfaces(out)
                else:finish(out)
        from sikh305_audit import audit
        if op=='refine' and v==10:
            from sikh305_finish import launch_camera
            launch_camera(out)
        if op=='refine' and v in (8,9,10,11):
            from sikh305_impacts import build_impacts
            build_impacts(out)
        audit(out);s.frame_end=c.FRAMES;s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
        frames=(1,100,106,115,126,140,165,200,285,290,294,297,300,304,310,315,320,324,327,330,334,340,355,440,450,460,466,469,475,528,600,696)
    elif op=='proof':
        s.render.resolution_x=360;s.render.resolution_y=640;s.eevee.taa_render_samples=24
        for a,b,name in ((88,180,'stop'),(274,357,'rear'),(414,c.FRAMES,'departure')):
            (out/name).mkdir();s.frame_start=a;s.frame_end=b;s.render.filepath=str(out/name/'frame-');bpy.ops.render.render(animation=True)
        return
    elif op=='movie':
        s.render.resolution_x=720;s.render.resolution_y=1280;s.eevee.taa_render_samples=64
        (out/'frames').mkdir();s.frame_start=1;s.frame_end=c.FRAMES;s.render.filepath=str(out/'frames/frame-');bpy.ops.render.render(animation=True);return
    else:frames=(1,115,140,310,330,460,600,696)
    s.render.resolution_x=480;s.render.resolution_y=854;s.eevee.taa_render_samples=32
    for f in frames:
        s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
    if op in ('build','refine'):
        cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();s.render.resolution_x=s.render.resolution_y=600;cam.data.lens=48
        for f in (285,290,294,297,300,310,315,320,324,327,330,340):
            s.frame_set(f);camera_at(cam,(14,-28,5.2),(7.5,-29,5.0));s.render.filepath=str(out/f'horse-side-{f}.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
