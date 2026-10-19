"""Trusted fixed native derivative and evidence operations."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from sikh317_run import validate,BASE,SOURCE
def main():
    path=Path(sys.argv[sys.argv.index('--')+1]);op,v=validate(json.loads(path.read_text()));out=BASE/f'{op}-{v:02d}'
    if path.resolve()!=out/'job.json':raise ValueError('Unadmitted job path')
    source=SOURCE if op in ('inspect','build') else BASE/f'build-{v:02d}/sequence.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    s=bpy.context.scene;s.frame_set(1)
    if op=='inspect':
        rows=[]
        for o in bpy.data.objects:
            if o.name.startswith(('BIKE','FOOT WARRIOR','leader','mounted leader','297 continuous crowd','secondary','horse')) or (o.parent and o.parent.name.startswith(('FOOT WARRIOR','BIKE'))):
                rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'loc':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'dimensions':list(o.dimensions),'hidden':o.hide_render,'shape_keys':len(o.data.shape_keys.key_blocks) if o.type=='MESH' and o.data.shape_keys else 0})
        rig=bpy.data.objects['horse.rig'];bones=[{'name':b.name,'head':list(b.head),'tail':list(b.tail),'matrix':list(sum((list(r) for r in b.bone.matrix_local),[]))} for b in rig.pose.bones if b.name.startswith(('fore','f_toe','upper_arm','DEF-f_'))]
        (out/'inspection.json').write_text(json.dumps({'objects':rows,'bones':bones},indent=2));return
    if op=='build':
        from sikh317_scene import build
        build(out);s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
    s.render.resolution_x=480;s.render.resolution_y=854;s.eevee.taa_render_samples=24
    s.eevee.shadow_ray_count=1
    for light in bpy.data.lights:
        if hasattr(light,'use_shadow_jitter'):light.use_shadow_jitter=light.type=='SUN'
        if hasattr(light,'shadow_maximum_resolution'):light.shadow_maximum_resolution=.01
    if op in ('proof','movie'):
        (out/'frames').mkdir();s.render.resolution_x=360 if op=='proof' else 720;s.render.resolution_y=640 if op=='proof' else 1280
        windows=((1,100),(270,460)) if op=='proof' else ((1,696),)
        for a,b in windows:s.frame_start=a;s.frame_end=b;s.render.filepath=str(out/'frames/frame-');bpy.ops.render.render(animation=True)
        return
    for f in (41,80,126,283,294,306,315,324,333,342,350,380,402,430,480,600):
        s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
