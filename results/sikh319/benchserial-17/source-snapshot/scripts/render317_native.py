"""Trusted read-only native render handler; accepts only bounded frame jobs."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from render317 import BASE,validate
def main():
    path=Path(sys.argv[sys.argv.index('--')+1]);j=validate(json.loads(path.read_text()));out=BASE/f"{j['operation']}-{j['version']:02d}"
    if path.resolve()!=out/'chunks'/str(j['start'])/'job.json':raise ValueError('Unadmitted job path')
    bpy.ops.wm.open_mainfile(filepath=str(BASE/f"build-{j['version']:02d}/sequence.blend"),load_ui=False,use_scripts=False)
    s=bpy.context.scene;proof=j['operation']=='proof';s.render.resolution_x=360 if proof else 720;s.render.resolution_y=640 if proof else 1280
    s.render.resolution_percentage=100;s.eevee.taa_render_samples=20 if proof else 32;s.eevee.shadow_ray_count=1
    for light in bpy.data.lights:
        if hasattr(light,'use_shadow_jitter'):light.use_shadow_jitter=light.type=='SUN'
        if hasattr(light,'shadow_maximum_resolution'):light.shadow_maximum_resolution=.01
    for f in range(j['start'],j['end']+1):
        dest=out/'frames'/f'frame-{f:04d}.png'
        if dest.exists():raise ValueError('Refusing render overwrite')
        s.frame_set(f);s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
