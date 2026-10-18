"""Bound forelimb diagnostic/repair, only the named horse FK channels."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from mathutils import Vector,Quaternion
from movie_factory.sikh291_motion import rear_amount,FPS,RATE
from sikh257_native import camera_at
BASE=ROOT/'.runtime/art-direction/series01-sikh304'
ANGLES={1:(-.30,-.25,1.65,.10),2:(-.30,.25,1.30,.10),3:(-.30,-.70,1.70,.10)}
def validate(j):
    if type(j)is not dict or set(j)!={'operation','variant'}:raise ValueError('Exact schema')
    if j['operation'] not in ('control','build','render','reopen') or type(j['variant'])is not int or j['variant'] not in ANGLES:raise ValueError('Unadmitted repair')
    return j
def pose(rig,f,v):
    t=(f-1)/FPS*RATE
    for side in ('L','R'):
        a=rear_amount(t-(.035 if side=='R' else 0))
        for name,angle in zip(('upper_arm_fk','forearm_fk','forefoot_fk','f_toe_fk'),ANGLES[v]):
            pb=rig.pose.bones[name+'.'+side]
            axis=pb.bone.matrix_local.to_3x3().inverted()@Vector((1,0,0))
            pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion(axis,angle*a)
            pb.keyframe_insert('rotation_quaternion',frame=f)
    bpy.context.view_layer.update()
def main():
    jp=Path(sys.argv[sys.argv.index('--')+1]);j=validate(json.loads(jp.read_text()));v=j['variant'];op=j['operation'];out=BASE/f'repair-{op}-{v:02d}'
    if jp.resolve()!=out/'job.json':raise ValueError('Unadmitted job location')
    src=BASE/('build-08/sequence.blend' if op in ('control','build') else f'repair-build-{v:02d}/sequence.blend')
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
    s=bpy.context.scene;rig=bpy.data.objects['horse.rig'];s.render.resolution_x=720;s.render.resolution_y=1280
    if op=='control':
        s.frame_set(320);pose(rig,320,v);s.render.filepath=str(out/'shot.png');bpy.ops.render.render(write_still=True)
        cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();cam.data.lens=55
        camera_at(cam,(2,-26,5.6),(7.4,-28.7,4.8));s.render.resolution_x=900;s.render.resolution_y=900
        s.render.filepath=str(out/'side.png');bpy.ops.render.render(write_still=True)
        (out/'joints.json').write_text(json.dumps({n:{'head':list(rig.matrix_world@rig.pose.bones[n].head),'tail':list(rig.matrix_world@rig.pose.bones[n].tail)} for n in ('upper_arm_fk.L','forearm_fk.L','forefoot_fk.L','f_toe_fk.L')},indent=2));return
    if op=='build':
        for f in range(1,529):s.frame_set(f);pose(rig,f,v)
        for layer in rig.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        if any(n in fc.data_path for n in ('upper_arm_fk','forearm_fk','forefoot_fk','f_toe_fk')):
                            for kp in fc.keyframe_points:kp.interpolation='LINEAR'
        s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'));return
    if op=='render':
        (out/'frames').mkdir();s.frame_start=276;s.frame_end=355;s.render.filepath=str(out/'frames/frame-');bpy.ops.render.render(animation=True)
        frames=(1,275,356,450)
    else:frames=(1,130,148,315,450)
    for f in frames:s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
