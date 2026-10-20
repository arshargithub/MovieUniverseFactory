"""Reviewed native entry point; only fixed structured320 operations."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from sikh320 import validate,BASE,source
def main():
    j=validate(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text()));op=j['operation'];v=j['version'];out=BASE/f'{"build" if op=="layers" else op}-{v:02d}'
    bpy.ops.wm.open_mainfile(filepath=str(source(op,v)),load_ui=False,use_scripts=False)
    s=bpy.context.scene
    if op=='layers':
        from sikh320_layers import fit_layers
        report=[]
        for upper in [o for o in s.objects if o.name.startswith('320 articulated upper body')]:
            shirt=next(o for o in upper.children if o.name.startswith('319 anatomically'))
            report.extend(fit_layers(upper,shirt,upper.parent.name=='mounted leader'))
        (out/'layer-support.json').write_text(json.dumps(report,indent=2))
        s.frame_set(252);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'));return
    if op=='inspect':
        s.frame_set(283);bpy.context.view_layer.update()
        roots=[bpy.data.objects['mounted leader'],bpy.data.objects['FOOT WARRIOR 0']]
        data=[]
        for r in roots:
            children=[]
            for o in r.children:
                if o.hide_render:continue
                children.append({'name':o.name,'type':o.type,'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale),'vertices':len(o.data.vertices) if o.type=='MESH' else 0,'materials':[m.name for m in o.data.materials] if hasattr(o.data,'materials') else [],'keys':len(o.data.shape_keys.key_blocks) if o.type=='MESH' and o.data.shape_keys else 0})
            data.append({'root':r.name,'location':list(r.location),'rotation':list(r.rotation_euler),'scale':list(r.scale),'children':children})
        (out/'actors.json').write_text(json.dumps(data,indent=2));return
    if op=='build':
        from sikh320_performance import build
        from sikh320_costume import costume
        report=build(out);report['costume']=costume(out)
        (out/'construction.json').write_text(json.dumps(report,indent=2))
        s.frame_set(252);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'));return
    s.render.resolution_x=720;s.render.resolution_y=1280;s.render.resolution_percentage=100
    s.eevee.taa_render_samples=32;s.eevee.shadow_ray_count=1
    for light in bpy.data.lights:
        if hasattr(light,'use_shadow_jitter'):light.use_shadow_jitter=light.type=='SUN'
        if hasattr(light,'shadow_maximum_resolution'):light.shadow_maximum_resolution=.01
    for f in j['frames']:
        s.frame_set(f);s.render.filepath=str(out/'frames'/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
