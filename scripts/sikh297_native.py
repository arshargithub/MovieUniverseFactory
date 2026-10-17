"""Fixed derivative/reopen dispatcher; asset scripts disabled by launcher."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from movie_factory.sikh297_contract import validate,CONTROLS,FRAMES
from sikh297_layers import build
BASE=ROOT/'.runtime/art-direction/series01-sikh297'
SOURCE=ROOT/'.runtime/art-direction/series01-sikh292/movie-01/sequence.blend'
def preservation():
    names=[o.name for o in bpy.data.objects if o.name.startswith(('BIKE ','RIDER '))]+[bpy.context.scene.camera.name]
    out={}
    for f in CONTROLS:
        bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
        out[str(f)]={n:[v for row in bpy.data.objects[n].matrix_world for v in row] for n in names}
    return out
def all_frame_protection():
    s=bpy.context.scene
    def protected(o):
        p=o
        while p:
            if p.name.startswith(('BIKE ','RIDER ')):return True
            p=p.parent
        return o==s.camera
    objs=[o for o in s.objects if protected(o)];geometry={}
    for o in objs:
        if o.type=='MESH':
            payload={'verts':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons]}
            if o.data.shape_keys:payload['shapes']={k.name:[list(v.co) for v in k.data] for k in o.data.shape_keys.key_blocks}
            geometry[o.name]=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    frames=[]
    for f in range(1,FRAMES+1):
        s.frame_set(f);bpy.context.view_layer.update()
        frames.append({o.name:[v for row in o.matrix_world for v in row] for o in objs})
    return geometry,frames
def render(out,frames):
    s=bpy.context.scene
    for f in frames:s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
def main():
    p=Path(sys.argv[sys.argv.index('--')+1]);j=validate(json.loads(p.read_text()));out=BASE/f"{j['operation']}-{j['version']:02d}"
    if p.resolve()!=out/'job.json':raise ValueError('Unadmitted path')
    op=j['operation'];source=SOURCE if op in ('inspect','controls') else BASE/'controls-05/sequence.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);s=bpy.context.scene
    if op=='inspect':
        (out/'inspection.json').write_text(json.dumps({'objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':list(o.location),'dimensions':list(o.dimensions)} for o in s.objects if 'leader' in o.name or o.type=='LIGHT'],'engine':s.render.engine},indent=2));return
    if op=='controls':
        before=preservation();build();after=preservation();assert before==after,'Protected transforms changed'
        (out/'preservation.json').write_text(json.dumps({'matched':True,'sampled_frames':list(CONTROLS),'before':before,'after':after},indent=2))
        s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'));render(out,CONTROLS)
        lights=[o for o in s.objects if o.type=='LIGHT' and o.name.startswith('297')]
        for o in lights:o.hide_render=True
        s.frame_set(215);s.render.filepath=str(out/'torch-off-0215.png');bpy.ops.render.render(write_still=True)
    elif op=='movie':
        (out/'frames').mkdir();s.render.filepath=str(out/'frames/frame-');bpy.ops.render.render(animation=True)
    else:
        new_geometry,new_frames=all_frame_protection()
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
        old_geometry,old_frames=all_frame_protection()
        assert new_geometry==old_geometry,'Protected principal/bike geometry changed'
        assert new_frames==old_frames,'Protected principal/bike/camera motion changed'
        (out/'full-protection.json').write_text(json.dumps({'frames':FRAMES,'protected_geometry_objects':len(old_geometry),'protected_transform_objects':len(old_frames[0]),'geometry_equal':True,'all_frame_transforms_equal':True},indent=2))
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
        render(out,(1,99,215,300,335,435));(out/'reopen.json').write_text(json.dumps({'source':str(source),'frames':[1,99,215,300,335,435]}))
if __name__=='__main__':main()
