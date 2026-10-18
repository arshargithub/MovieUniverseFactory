"""Allowlisted local scene300 operations, native scripts disabled."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from mathutils import Vector
from movie_factory.sikh300_motion import validate
from sikh257_native import camera_at
BASE=ROOT/'.runtime/art-direction/series01-sikh300'
SOURCE=ROOT/'.runtime/art-direction/series01-sikh299/controls-07/sequence.blend'
SELECTED=BASE/'controls-08/sequence.blend'
def main():
    p=Path(sys.argv[sys.argv.index('--')+1]);j=validate(json.loads(p.read_text()));out=BASE/f"{j['operation']}-{j['version']:02d}"
    if p.resolve()!=out/'job.json':raise ValueError('Unadmitted output')
    source=SELECTED if j['operation'] in ('motion','movie','reopen') or (j['operation']=='inspect' and j['version']>=4) else (BASE/'controls-07/sequence.blend' if (j['operation']=='inspect' and j['version']==3) or (j['operation']=='controls' and j['version']>=8) else (BASE/'controls-06/sequence.blend' if j['operation']=='controls' and j['version']==7 else SOURCE))
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);s=bpy.context.scene
    if j['operation'] in ('motion','movie'):
        (out/'frames').mkdir()
        if j['operation']=='motion':
            s.render.resolution_x=360;s.render.resolution_y=640
            ranges=[(105,157,'frames'),(290,355,'rear-frames')]
        else:ranges=[(1,528,'frames')]
        for start,end,folder in ranges:
            (out/folder).mkdir(exist_ok=True);s.frame_start=start;s.frame_end=end;s.render.filepath=str(out/folder/'frame-');bpy.ops.render.render(animation=True)
        return
    if j['operation']=='reopen':
        for f in (1,120,148,215,335,435):
            s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
        (out/'reopen.json').write_text(json.dumps({'source':str(source),'frames':[1,120,148,215,335,435]}));return
    if j['operation']=='inspect':
        if j['version']>=3:
            rows=[];horse=bpy.data.objects['horse'];s.frame_set(1);print([(g.index,g.name) for g in horse.vertex_groups],flush=True)
            # Inspect rendered mesh support, not only an IK target.
            groups={g.index:g.name for g in horse.vertex_groups if 'toe' in g.name.lower() and 'f_toe' not in g.name.lower()}
            indices=[v.index for v in horse.data.vertices if any(g.group in groups and g.weight>.2 for g in v.groups)]
            for f in (1,295,310,325,340,350,360):
                s.frame_set(f);bpy.context.view_layer.update();ev=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();points=[ev.matrix_world@m.vertices[i].co for i in indices]
                rows.append({'frame':f,'groups':groups,'vertices':len(indices),'hind_min_z':min(p.z for p in points),'hind_lowest':list(min(points,key=lambda p:p.z))});ev.to_mesh_clear()
            (out/'hind-contact.json').write_text(json.dumps(rows,indent=2))
            cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();cam.data.type='ORTHO';cam.data.ortho_scale=1.5;s.render.resolution_x=720;s.render.resolution_y=720
            for f in (1,310,325,340,360):
                s.frame_set(f);camera_at(cam,(10,-27,3.65),(7.7,-29.5,3.45));s.render.filepath=str(out/f'hind-{f}.png');bpy.ops.render.render(write_still=True)
            return
        s.frame_set(1);bpy.context.view_layer.update();rows=[]
        for o in s.objects:
            if o.name.startswith(('horse','HORSE','mounted','FOOT WARRIOR','individual wheat','297 wheat','irregular packed','cultivated','secondary','BIKE')) or o.type=='ARMATURE':
                rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale),'materials':[m.name for m in o.data.materials] if o.type in ('MESH','CURVE') else [],'mods':[(m.name,m.type) for m in o.modifiers],'verts':len(o.data.vertices) if o.type=='MESH' else None})
        rig=bpy.data.objects['horse.rig'];bones=[]
        for b in rig.pose.bones:bones.append({'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head),'tail':list(b.tail),'rest':list(map(list,b.bone.matrix_local)),'mode':b.rotation_mode,'constraints':[(c.name,c.type) for c in b.constraints]})
        drivers=[]
        if rig.animation_data:
            for fc in rig.animation_data.drivers:
                drivers.append({'path':fc.data_path,'valid':fc.is_valid,'expression':fc.driver.expression,'variables':[(v.name,[(t.data_path,t.id.name if t.id else None) for t in v.targets]) for v in fc.driver.variables]})
        (out/'inspection.json').write_text(json.dumps({'objects':rows,'bones':bones,'properties':{b.name:{k:str(b[k]) for k in b.keys()} for b in rig.pose.bones if b.keys()},'drivers':drivers},indent=2))
        if j['version']>=2:return
        cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();cam.data.lens=55
        s.render.resolution_x=720;s.render.resolution_y=720
        for f in (1,295,310,325,340,360):
            s.frame_set(f);camera_at(cam,(12,-23,5.0),(7.5,-29,4.65));s.render.filepath=str(out/f'horse-side-{f}.png');bpy.ops.render.render(write_still=True)
        s.frame_set(310);camera_at(cam,(5,-22,5),(7.5,-29,4.6));s.render.filepath=str(out/'horse-front.png');bpy.ops.render.render(write_still=True)
        return
    if j['operation']=='controls':
        from sikh300_scene import horse,build
        if j['version']>=8:
            from sikh300_scene import hind_support
            hind_support(out);s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
        elif j['version']==7:
            from sikh300_scene_land import dense_crops
            dense_crops();s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
        elif j['version']>=3:build(out)
        else:horse(out);s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
        if j['version']>=3:
            for f in (1,72,99,112,120,126,132,139,148,165,215,300,315,330,350,435,470,528):
                s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
        cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();cam.data.lens=55;s.render.resolution_x=720;s.render.resolution_y=720
        for f in (1,295,310,325,340,360):
            s.frame_set(f);camera_at(cam,(12,-23,5.0),(7.5,-29,4.65));s.render.filepath=str(out/f'horse-side-{f}.png');bpy.ops.render.render(write_still=True)
        s.frame_set(310);camera_at(cam,(5,-22,5),(7.5,-29,4.6));s.render.filepath=str(out/'horse-front.png');bpy.ops.render.render(write_still=True)
        if j['version']>=3:
            s.frame_set(215);camera_at(cam,(4,-13,2.7),(0,-18,1.2));cam.data.lens=48;s.render.filepath=str(out/'crowd.png');bpy.ops.render.render(write_still=True)
            s.frame_set(1);camera_at(cam,(5,4,1.5),(1,0,.2));cam.data.lens=38;s.render.filepath=str(out/'road-ditch.png');bpy.ops.render.render(write_still=True)
            s.frame_set(148);camera_at(cam,(3.5,-2,1.1),(0,-3.5,.7));cam.data.lens=46;s.render.filepath=str(out/'contact-side.png');bpy.ops.render.render(write_still=True)
        return
    raise ValueError('Implementation not yet admitted')
if __name__=='__main__':main()
