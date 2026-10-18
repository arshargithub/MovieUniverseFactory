"""Fixed299 operations; sanitized worker, source assets scripts disabled."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from movie_factory.sikh299_motion import validate,FRAMES
from sikh299_scene import build
from sikh257_native import camera_at
BASE=ROOT/'.runtime/art-direction/series01-sikh299'
SOURCE=ROOT/'.runtime/art-direction/series01-sikh297/controls-05/sequence.blend'
CONTROLS=(1,72,99,112,120,126,133,140,148,155,180,215,300,335,435,460,528)
def render(out,frames):
    s=bpy.context.scene
    for f in frames:s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
def main():
    p=Path(sys.argv[sys.argv.index('--')+1]);j=validate(json.loads(p.read_text()));op=j['operation'];out=BASE/f"{op}-{j['version']:02d}"
    if p.resolve()!=out/'job.json':raise ValueError('Unadmitted output')
    source=SOURCE if op=='controls' or (op=='inspect' and j['version']<3) else BASE/'controls-04/sequence.blend'
    if op=='controls' and j['version']>=6:source=BASE/'controls-05/sequence.blend'
    if op=='controls' and j['version']>=7:source=BASE/'controls-06/sequence.blend'
    if op in ('motion','movie','reopen'):source=BASE/('controls-06/sequence.blend' if op=='motion' else 'controls-07/sequence.blend')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);s=bpy.context.scene
    if op=='inspect':
        if j['version']>=6:
            from sikh299_scene import contact_shading
            contact_shading()
        s.frame_set(150);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();items=[]
        for o in s.objects:
            if o.name=='irregular packed farm track' or 'charcoal tire' in o.name:
                ev=o.evaluated_get(dg);m=ev.to_mesh();used={v for p in m.polygons for v in p.vertices}
                pts=[ev.matrix_world@v.co for v in m.vertices];items.append({'name':o.name,'matrix':list(map(list,o.matrix_world)),'modifiers':[(a.name,a.type,a.show_render) for a in o.modifiers],'all_min_z':min(p.z for p in pts),'used_min_z':min(pts[i].z for i in used),'verts':len(pts),'used':len(used),'polygons':len(m.polygons),'hide_render':o.hide_render});ev.to_mesh_clear()
        (out/'objects.json').write_text(json.dumps(items,indent=2))
        if j['version']>=3:
            from sikh257_native import material
            from mathutils import Vector
            trace=json.loads((BASE/'controls-04/motion-trace.json').read_text())[149]
            for k in ('front_tread_contact','rear_tread_contact'):
                p=trace[k];bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.015,location=p);bpy.context.object.data.materials.append(material('diagnostic contact',(0,1,0)))
            cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();cam.data.type='ORTHO';cam.data.ortho_scale=1.5
            settings={'eevee':{p.identifier:str(getattr(s.eevee,p.identifier)) for p in s.eevee.bl_rna.properties if any(k in p.identifier for k in ('shadow','ray','gtao','volum'))},'lights':[{p.identifier:str(getattr(o.data,p.identifier)) for p in o.data.bl_rna.properties if any(k in p.identifier for k in ('name','shadow','energy'))} for o in s.objects if o.type=='LIGHT']}
            (out/'shadows.json').write_text(json.dumps(settings,indent=2))
            p=Vector(trace['front_tread_contact']);camera_at(cam,p+Vector((2,0,.6)),p+Vector((0,0,.3)));s.render.filepath=str(out/'contact-marker.png');bpy.ops.render.render(write_still=True)
        return
    if op=='controls':
        if j['version']>=6:
            from sikh299_scene import moon
            if j['version']==6:moon()
            else:
                from sikh299_scene import greeting_eyeline
                greeting_eyeline(out)
            s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
        else:build(out)
        render(out,CONTROLS if j['version']<4 else ((148,180,195,215,240,260,280,300,335,380,435) if j['version']>=7 else (99,120,133,148,215,335,435)))
        cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();cam.data.type='PERSP'
        s.frame_set(150);camera_at(cam,(3.5,-2,1.1),(0,-3.5,.7));cam.data.lens=46;s.render.filepath=str(out/'contact-side.png');bpy.ops.render.render(write_still=True)
        s.frame_set(148);camera_at(cam,(0,-3.6,9),(0,-3.6,0));cam.data.lens=30;s.render.filepath=str(out/'contact-top.png');bpy.ops.render.render(write_still=True)
        s.frame_set(100);camera_at(cam,(-2.75,-7.2,2.4),(-2.75,-5.6,2.1));cam.data.lens=38;s.render.filepath=str(out/'fire-detail.png');bpy.ops.render.render(write_still=True)
        camera_at(cam,(15,-100,30),(15,-110,30));cam.data.lens=40;s.render.filepath=str(out/'moon-detail.png');bpy.ops.render.render(write_still=True)
    elif op in ('motion','movie'):
        (out/'frames').mkdir();s.render.filepath=str(out/'frames/frame-')
        if op=='motion':s.frame_start=105;s.frame_end=157
        bpy.ops.render.render(animation=True)
    else:
        render(out,(1,120,148,215,335,435));(out/'reopen.json').write_text(json.dumps({'source':str(source),'frames':[1,120,148,215,335,435]}))
if __name__=='__main__':main()
