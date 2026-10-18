"""Fixed operation native scene entry; source scripts are reviewed repository code."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from movie_factory.sikh304_motion import validate,source_name
from sikh257_native import camera_at
BASE=ROOT/'.runtime/art-direction/series01-sikh304'
def main():
    p=Path(sys.argv[sys.argv.index('--')+1]);j=validate(json.loads(p.read_text()));out=BASE/f"{j['operation']}-{j['version']:02d}"
    if p.resolve()!=out/'job.json':raise ValueError('Unadmitted path')
    src=ROOT/'.runtime/art-direction/series01-sikh300/ground-fix-01/sequence.blend' if j['operation'] in ('build','inspect') else BASE/source_name(j['operation'],j['version'])
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);s=bpy.context.scene
    if j['operation']=='inspect':
        rows=[]
        for f in (1,295,310,325,340,355):
            s.frame_set(f);bpy.context.view_layer.update();rig=bpy.data.objects['horse.rig']
            rows.append({'frame':f,'bones':{b.name:{'head':list(rig.matrix_world@b.head),'tail':list(rig.matrix_world@b.tail),'mode':b.rotation_mode,'rotation':list(b.rotation_quaternion),'constraints':[(c.name,c.type,getattr(c,'subtarget',''),c.influence) for c in b.constraints]} for b in rig.pose.bones if b.name.startswith(('DEF-','upper_arm_fk','forearm_fk','forefoot_fk','f_toe_fk','hind_foot_ik','thigh_fk','shin_fk','torso','hips','chest','neck','head'))}})
        (out/'rig.json').write_text(json.dumps(rows,indent=2))
        (out/'objects.json').write_text(json.dumps([{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'loc':list(o.location),'scale':list(o.scale)} for o in s.objects if not o.name.startswith(('299 tire-contact','staging dust'))],indent=2))
        return
    if j['operation'] in ('build','finish'):
        if j['operation']=='build':
            from sikh304_scene import build
            build(out)
        else:
            # Controlled rendering derivatives of the completed build04;
            # no character, action, camera, terrain or light energy changes.
            for light in bpy.data.lights:
                if hasattr(light,'use_shadow_jitter'):light.use_shadow_jitter=(j['version']==6 and light.type=='SUN') or j['version']==7
            s.eevee.taa_render_samples=32 if j['version'] in (6,7) else 64
            (out/'profile.json').write_text(json.dumps({'source':str(src),'jitter':'none' if j['version']==5 else 'sun-only' if j['version']==6 else 'all','samples':s.eevee.taa_render_samples},indent=2))
        s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
        frames=(1,72,99,120,130,139,148,165,215,300,315,330,350,435,450,458,464,470,528)
        s.render.resolution_x=540;s.render.resolution_y=960
    elif j['operation']=='movie':
        (out/'frames').mkdir();s.render.resolution_x=720;s.render.resolution_y=1280;s.frame_start=1;s.frame_end=528;s.render.filepath=str(out/'frames/frame-');bpy.ops.render.render(animation=True);return
    elif j['operation']=='proof':
        s.render.resolution_x=360;s.render.resolution_y=640
        for a,b,folder in ((105,157,'stop'),(290,355,'rear'),(430,478,'launch')):
            (out/folder).mkdir();s.frame_start=a;s.frame_end=b;s.render.filepath=str(out/folder/'frame-');bpy.ops.render.render(animation=True)
        return
    else:
        frames=(1,130,148,315,450);s.render.resolution_x=720;s.render.resolution_y=1280
    for f in frames:
        s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
    if j['operation'] in ('build','finish'):
        cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();cam.data.lens=55;s.render.resolution_x=720;s.render.resolution_y=720
        for f in (1,295,310,325,340,355):
            s.frame_set(f);camera_at(cam,(12,-23,5.0),(7.5,-29,4.65));s.render.filepath=str(out/f'horse-side-{f}.png');bpy.ops.render.render(write_still=True)
        s.frame_set(1);camera_at(cam,(5,4,1.5),(1,0,.3));cam.data.lens=38;s.render.filepath=str(out/'road-ditch.png');bpy.ops.render.render(write_still=True)
        # Fixed field camera one second apart: moving camera cannot prove wind.
        camera_at(cam,(6,24,2.7),(15,21,.5));cam.data.lens=42
        for f in (24,48):s.frame_set(f);s.render.filepath=str(out/f'wind-{f}.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
