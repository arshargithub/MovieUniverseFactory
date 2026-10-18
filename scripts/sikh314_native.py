"""Fixed reviewed Blender handler; assets never execute embedded scripts."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from movie_factory.sikh314_motion import validate,FRAMES
from sikh257_native import camera_at
BASE=ROOT/'.runtime/art-direction/series01-sikh314'
def main():
    path=Path(sys.argv[sys.argv.index('--')+1]);job=validate(json.loads(path.read_text()));op,v=job['operation'],job['version'];out=BASE/f'{op}-{v:02d}'
    if path.resolve()!=out/'job.json':raise ValueError('Unadmitted job path')
    source=ROOT/'.runtime/art-direction/series01-sikh305/build-13/sequence.blend' if op=='build' else BASE/f'build-{v:02d}/sequence.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);s=bpy.context.scene
    if op in ('audit','auditverify'):
        from sikh314_audit import audit
        audit(out,source);return
    if op in ('limbcontrol','hoofcontrol'):
        from sikh305_scene import bone_x
        s.frame_set(315);rig=bpy.data.objects['horse.rig'];cam=s.camera
        cam.animation_data_clear();cam.data.animation_data_clear();s.render.resolution_x=s.render.resolution_y=600;s.eevee.taa_render_samples=24;cam.data.lens=48
        for i,angle in enumerate((2.0,2.5,3.0) if op=='limbcontrol' else (.4,.8,1.2)):
            for side in ('L','R'):
                bone_x(rig,'forefoot_fk.'+side,angle if op=='limbcontrol' else 2.5,315)
                bone_x(rig,'f_toe_fk.'+side,-.25 if op=='limbcontrol' else angle,315)
            bpy.context.view_layer.update();camera_at(cam,(14,-28,5.2),(7.5,-29,5.0));s.render.filepath=str(out/f'limb-{i}.png');bpy.ops.render.render(write_still=True)
        return
    if op=='build':
        from sikh314_scene import build
        build(out);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
    if op=='movie':
        s.render.resolution_x=720;s.render.resolution_y=1280;s.eevee.taa_render_samples=64
        (out/'frames').mkdir();s.frame_start=1;s.frame_end=FRAMES;s.render.filepath=str(out/'frames/frame-');bpy.ops.render.render(animation=True);return
    if op=='proof':
        s.render.resolution_x=360;s.render.resolution_y=640;s.eevee.taa_render_samples=24
        (out/'frames').mkdir();s.frame_start=274;s.frame_end=357;s.render.filepath=str(out/'frames/frame-');bpy.ops.render.render(animation=True);return
    s.render.resolution_x=480;s.render.resolution_y=854;s.eevee.taa_render_samples=32
    frames=(80,126,150,285,294,300,306,310,315,320,324,330,340,355,450,600,648)
    for f in frames:
        s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
    if op=='build':
        cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();s.render.resolution_x=s.render.resolution_y=600;cam.data.lens=48
        for f in (294,306,315,324,330):
            s.frame_set(f);camera_at(cam,(14,-28,5.2),(7.5,-29,5.0));s.render.filepath=str(out/f'horse-side-{f:04d}.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
