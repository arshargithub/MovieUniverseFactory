"""Three fixed contact hypotheses and a pose-only neck readability control."""
import json,sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance200_inspect import base

def aim(b,target):
    from mathutils import Matrix
    direction=(target-b.head).normalized();q=(b.tail-b.head).normalized().rotation_difference(direction)
    m=q.to_matrix().to_4x4()@b.matrix;m.translation=b.head;b.matrix=m

def contact(rig,side,variant):
    import bpy
    from mathutils import Vector
    root=rig.pose.bones['MF_fit_finger_4_0.'+side];middle=rig.pose.bones['MF_fit_finger_4_1.'+side];tip=rig.pose.bones['MF_fit_finger_4_2.'+side]
    index=rig.pose.bones['MF_fit_finger_2_2.'+side]
    hand=rig.pose.bones['hand.'+side];local=hand.matrix.inverted()@index.head
    # Place the pad on the outside of the curled index, not the unreachable
    # top knuckle. The second joint stays gently curved, never reversed.
    local+=Vector((0,.025, -.07 if side=='L' else .07))
    target=hand.matrix@local;origin=root.head.copy()
    lengths=[b.bone.length for b in (root,middle,tip)];a=lengths[0];b=sum(lengths[1:]);d=min((target-origin).length,a+b-.001)
    axis=(target-origin).normalized();cosine=max(-1,min(1,(a*a+d*d-b*b)/(2*a*d)))
    # Anatomically outward bend planes are tested as explicit alternatives.
    bend=hand.matrix.to_3x3()@Vector((variant,.1,-.25 if side=='L' else .25));bend-=axis*bend.dot(axis);bend.normalize()
    joint=origin+axis*(a*cosine)+bend*(a*math.sqrt(1-cosine*cosine))
    aim(root,joint);bpy.context.view_layer.update();aim(middle,target);bpy.context.view_layer.update();aim(tip,target);bpy.context.view_layer.update()

def neck(body,rig):
    m=body.modifiers['200 preserve rest neck under riding extension'];group=body.vertex_groups[m.vertex_group]
    group.remove(list(range(len(body.data.vertices))))
    for v in body.data.vertices:
        x,y,z=v.co;w=max(0,1-(abs(x)/1.4)**2)*max(0,1-((z+1.65)/1.05)**2)
        if w:group.add([v.index],w,'REPLACE')
    m.use_only_smooth=True;m.iterations=24;m.factor=.8
    fc=m.driver_add('factor');d=fc.driver;d.type='SCRIPTED';v=d.variables.new();v.name='a';v.type='TRANSFORMS';t=v.targets[0];t.id=rig;t.bone_target='MF185_neck';t.transform_type='ROT_X';t.transform_space='LOCAL_SPACE'
    d.expression='min(0.8, abs(a)*2.0)'

def main():
    import bpy
    from mathutils import Vector
    from entrance200_render import crops,neutral_check
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'pose13'}:raise ValueError('Fixed control only')
    out=base.BASE/'entrance200-pose13';source=base.BASE/'entrance200-candidate03/scene.blend'
    if out.exists() or base.digest(source)!=json.loads((source.parent/'result.json').read_text())['native_sha256']:raise ValueError('Source/evidence mismatch')
    out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.frame_set(360);rig.animation_data.action=None
    bones=[b for b in rig.pose.bones if '4_' in b.name];original={b.name:b.matrix_basis.copy() for b in bones}
    scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.resolution_percentage=100;scene.render.use_persistent_data=True
    camera=scene.camera;camera.animation_data_clear();camera.data.lens=55;scene.render.resolution_x=480;scene.render.resolution_y=480
    for variant in (-1,0,1):
        for b in bones:b.matrix_basis=original[b.name]
        bpy.context.view_layer.update()
        for side in ('L','R'):contact(rig,side,variant)
        bpy.context.view_layer.update();target=rig.matrix_world@rig.pose.bones['hand.L'].head.lerp(rig.pose.bones['hand.L'].tail,.6)
        camera.location=target+Vector((2.8,-3.5,1.5));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/f'grip-{variant}.png');bpy.ops.render.render(write_still=True)
    neck(body,rig)
    # crops calls frame_set, but the action has been detached deliberately.
    crops(scene,out)
    (out/'result.json').write_text(json.dumps({'source_sha256':base.digest(source),'native_modified':False,'visual_gate':'NOT_RUN','neck_factor':body.modifiers['200 preserve rest neck under riding extension'].factor},indent=2)+'\n')

if __name__=='__main__':main()
