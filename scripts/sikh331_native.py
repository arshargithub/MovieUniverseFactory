"""Trusted native inspection and scoped whole-pose proof."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from sikh331 import validate,source,BASE
def main():
    j=validate(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text()));op=j['operation'];out=BASE/f"{op}-{j['version']:02d}"
    bpy.ops.wm.open_mainfile(filepath=str(source(j)),load_ui=False,use_scripts=False)
    s=bpy.context.scene;rig=bpy.data.objects['horse.rig'];s.frame_set(283);bpy.context.view_layer.update()
    if op=='inspect':
        bones=[]
        for b in rig.pose.bones:
            if b.name.startswith(('DEF','MCH','ORG')): continue
            bones.append({'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head),'tail':list(b.tail),'rest':list(sum((list(r) for r in b.bone.matrix_local),[])),'local':list(b.location),'rotation':list(b.rotation_quaternion),'props':{k:b[k] for k in b.keys() if isinstance(b[k],(int,float,str))},'constraints':[{'type':c.type,'influence':c.influence,'subtarget':getattr(c,'subtarget','')} for c in b.constraints]})
        objects=[]
        for n in ('horse.rig','HORSE hind support pivot','mounted leader','320 articulated upper body mounted leader'):
            o=bpy.data.objects[n];objects.append({'name':n,'parent':o.parent.name if o.parent else None,'world':[list(r) for r in o.matrix_world],'local':list(o.location),'rotation':list(o.rotation_euler),'children':[x.name for x in o.children]})
        (out/'rig.json').write_text(json.dumps({'bones':bones,'objects':objects},indent=2));return
    if op=='pose':
        from sikh331_pose import build
        build(out,j['frames'])
        if j['version']>=2:
            from sikh331_look import build as look
            look(out);s.frame_set(283);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
    s.render.resolution_x=540;s.render.resolution_y=960;s.render.resolution_percentage=100
    s.eevee.taa_render_samples=16;s.eevee.shadow_ray_count=1
    for f in j['frames']:
        s.frame_set(f);s.render.filepath=str(out/'frames'/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__': main()
