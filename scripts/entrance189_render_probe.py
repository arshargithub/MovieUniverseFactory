"""Two fixed matched CPU/Metal controls; no saved preferences or scene edits."""
import json
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def main():
    import bpy
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1 or json.loads(Path(args[0]).read_text())!={'operation':'device17'}:
        raise ValueError('Fixed device control only')
    source=base.BASE/'entrance189-performance14/scene.blend'
    record=json.loads((source.parent/'result.json').read_text())
    if source.is_symlink() or base.digest(source)!=record['native_sha256']:raise ValueError('Source changed')
    for row in record['caches']:
        path=(source.parent/row['path']).resolve()
        if not path.is_relative_to(base.BASE.resolve()) or base.digest(path)!=row['sha256']:raise ValueError('Cache changed')
    out=base.BASE/'entrance189-device17'
    if out.exists():raise ValueError('Preserve evidence')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;pref=bpy.context.preferences.addons['cycles'].preferences
    devices=pref.get_devices_for_type('METAL')
    info={'source_sha256':record['native_sha256'],
        'devices':[{'name':d.name,'type':d.type} for d in devices],
        'frames':[],'visual_gate':'NOT_RUN','saved_preferences':False}
    (out/'devices.json').write_text(json.dumps(info,indent=2)+'\n')
    if not any(d.type=='METAL' for d in devices):
        info['status']='NO_METAL_DEVICE';(out/'result.json').write_text(json.dumps(info,indent=2)+'\n');return
    pref.compute_device_type='METAL'
    for d in devices:d.use=d.type=='METAL'
    scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
    scene.cycles.samples=8;scene.render.use_persistent_data=True
    for device in ('CPU','GPU'):
        scene.cycles.device=device
        for f in (217,360):
            start=time.perf_counter();scene.frame_set(f);bpy.context.view_layer.update();prepared=time.perf_counter()
            scene.render.filepath=str(out/(device.lower()+'-%04d.png'%f));bpy.ops.render.render(write_still=True)
            info['frames'].append({'device':device,'frame':f,'frame_evaluation_seconds':prepared-start,
                'render_seconds':time.perf_counter()-prepared})
            (out/'progress.json').write_text(json.dumps(info,indent=2)+'\n')
    base.check_protected();info['status']='RENDERED_NOT_VISUALLY_QUALIFIED'
    (out/'result.json').write_text(json.dumps(info,indent=2)+'\n')


if __name__=='__main__':main()
