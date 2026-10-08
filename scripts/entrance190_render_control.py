"""Nonpersistent viewport-evaluation control, with unchanged render modifiers."""
import json
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'render32'}:raise ValueError('Fixed render control required')
    folder=base.BASE/'entrance190-perspective29';source=folder/'scene.blend';out=base.BASE/'entrance190-render32'
    r=json.loads((folder/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Source changed or prior output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;base.check_protected();changed=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF') and m.show_viewport:
                changed.append({'object':ob.name,'modifier':m.name,'type':m.type,'show_render':m.show_render})
                m.show_viewport=False
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
    rows=[]
    for f in (362,457,552):
        started=time.monotonic();scene.frame_set(f)
        scene.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
        rows.append({'frame':f,'seconds':time.monotonic()-started})
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'changed_viewport_only':changed,'frames':rows,'visual_parity':'NOT_RUN','saved_native':False},indent=2)+'\n')

if __name__=='__main__':main()
