"""Reviewed whole-pose experiment on a reversible native derivative."""
import json, math
import bpy
from mathutils import Vector,Quaternion,Matrix
from movie_factory.sikh331_motion import pose
from sikh257_layout import key
from sikh305_scene import bone_x
def build(out,frames):
    s=bpy.context.scene;s.frame_set(283);bpy.context.view_layer.update()
    rig=bpy.data.objects['horse.rig'];pivot=bpy.data.objects['HORSE hind support pivot']
    root=bpy.data.objects['mounted leader'];upper=bpy.data.objects['320 articulated upper body mounted leader']
    rest=pivot.location.copy();rider_rest=root.location.copy()
    fixed={n:(rig.matrix_world@rig.pose.bones[n].matrix).copy() for n in ('hind_foot_ik.L','hind_foot_ik.R','forefoot_ik.L','forefoot_ik.R')}
    rows=[]
    for f in range(252,442):
        s.frame_set(f);p=pose(f)
        pivot.location=rest+Vector((0,p['forward'],p['drop']))
        pivot.rotation_euler=(p['pitch'],0,0);key(pivot,f)
        for name,angle in [('hips',-.35*p['spine']),('chest',p['spine']),('neck',p['neck']),('head',p['head'])]:bone_x(rig,name,angle,f)
        # Neck curvature is separate from the base rotation and poll angle.
        nb=rig.pose.bones['neck_bend'];nb.location=(0,0,.16*max(0,-p['pitch']));nb.keyframe_insert('location',frame=f)
        root.location=rider_rest;root.rotation_euler=(p['rider'],0,0);key(root,f)
        upper.rotation_euler=(.06*math.exp(-((f-354)/5)**2),0,.035*math.exp(-((f-296)/12)**2));key(upper,f)
        flight=min(max(0,(f-307)/4),max(0,(350-f)/4),1)
        airborne=flight>0
        for side in ('L','R'):
            q=pose(f-(1.25 if side=='R' and airborne else 0))
            for name,k in [('upper_arm_fk','shoulder'),('forearm_fk','elbow'),('forefoot_fk','wrist')]:
                offset=({'shoulder':.10,'elbow':.12,'wrist':-.13}[k]*max(0,-p['pitch'])) if side=='R' else 0
                bone_x(rig,name+'.'+side,q[k]+offset,f)
            bone_x(rig,'f_toe_fk.'+side,.20*max(0,-p['pitch']),f)
            parent=rig.pose.bones['upper_arm_parent.'+side]
            parent['IK_FK']=flight;parent.keyframe_insert('["IK_FK"]',frame=f)
            for c in rig.pose.bones['MCH-f_hoof.'+side].constraints:
                if c.type=='COPY_TRANSFORMS':c.influence=1-flight;c.keyframe_insert('influence',frame=f)
        bpy.context.view_layer.update()
        for name,world in fixed.items():
            b=rig.pose.bones[name];b.rotation_mode='QUATERNION';b.matrix=rig.matrix_world.inverted()@world
            b.keyframe_insert('location',frame=f);b.keyframe_insert('rotation_quaternion',frame=f)
        bpy.context.view_layer.update()
        if f in frames:
            names=tuple(n for n in rig.pose.bones.keys() if n.startswith(('DEF-head','DEF-neck','DEF-spine','DEF-thigh','DEF-lower_leg','DEF-r_toe','DEF-f_toe','DEF-upper_arm','DEF-forearm','DEF-forefoot','DEF-hind_foot')) and not n.endswith('.R'))
            rows.append({'frame':f,'pose':p,'bones':{n:{'head':list(rig.matrix_world@rig.pose.bones[n].head),'tail':list(rig.matrix_world@rig.pose.bones[n].tail)} for n in names if n in rig.pose.bones}})
    (out/'pose-evidence.json').write_text(json.dumps(rows,indent=2))
    # Main changes are pose controls; old contacts/cloth are not called qualified.
    from sikh320_performance import rebuild_reins
    rebuild_reins()
    s.frame_set(283);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
