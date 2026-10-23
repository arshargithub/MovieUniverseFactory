"""Fixed cue/strike/carry with a constant material grip, not a planted pole."""
import json,math,importlib.util
from pathlib import Path

def lift(frame,height):
    def ease(u):u=max(0.,min(1.,u));return u*u*(3-2*u)
    # The raising hand settles briefly; the strike accelerates into contact.
    # Symmetric smoothstep here produced the measured15 pre-contact slowdown.
    down=max(0.,min(1.,(frame-294)/6))
    return height*ease((frame-285)/8)*(1-down*down)

def accelerating_strike(velocities):
    return len(velocities)>=3 and all(b<a<0 for a,b in zip(velocities,velocities[1:]))

def ground_gap(frame):
    u=min(1.,abs(frame-300)/4);return .015*u*u*(3-2*u)

def module(name):
    spec=importlib.util.spec_from_file_location('gesture353_'+name,Path(__file__).with_name(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def run(bpy,out):
    from mathutils import Vector,Matrix
    support=module('nihang_support');motion=module('nihang_motion')
    scene=support.select_production_scene(bpy);rig=bpy.data.objects['MF coherent Nihang rig'];horse=bpy.data.objects['horse.rig']
    shaft=bpy.data.objects['LEADER spear world contact owner'];bones=rig.data.bones
    if not rig.get('integrate353') or rig.get('gesture353'):raise ValueError('GESTURE353_PARENT')
    names=[n for n in bones if n.name.endswith('.L') and n.name.startswith(('upperarm','lowerarm','wrist','finger'))]
    names=[n.name for n in names];capture={}
    across=(bones['finger2-1.L'].head_local-bones['finger5-1.L'].head_local).normalized()
    long=sum((bones[f'finger{i}-1.L'].head_local for i in range(2,6)),Vector())/4-bones['wrist.L'].head_local
    offset=long*.70;long=long.normalized()
    a=(bones['lowerarm01.L'].head_local-bones['upperarm01.L'].head_local).length
    b=(bones['wrist.L'].head_local-bones['lowerarm01.L'].head_local).length
    def grip(row):
        wrist=row['bones']['wrist.L'];rot=wrist.to_3x3()@bones['wrist.L'].matrix_local.to_3x3().inverted()
        dorsal=(rot@across).cross(rot@long).normalized()
        return wrist.translation+rot@offset-dorsal*.031
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update()
        capture[f]=dict(world=rig.matrix_world.copy(),bones={n:rig.pose.bones[n].matrix.copy() for n in names},shaft=shaft.matrix_world.copy(),horse=horse.matrix_world.copy())
    ground=capture[350]['shaft'].translation.copy();strike=capture[300];center=strike['world']@grip(strike)
    distance=(center-ground).length;axis=(center-ground).normalized();axis_local=strike['world'].to_quaternion().inverted()@axis
    if not .7<distance<2.8:raise ValueError('GESTURE353_GRIP_STATION')
    failures=[];chosen=None
    # Numeric preflight before any mutation; maximum expressive lift satisfying
    # actual existing lengths, wrist range and adjacent elbow continuity.
    for height in (.18,.15,.12):
        proposed={}
        try:
            for f,row in capture.items():
                world=row['world'];inv=world.inverted();old=row['bones'];up=(world.to_quaternion()@axis_local).normalized()
                target=world@grip(row)+Vector((0,0,lift(f,height)))
                origin=target-up*distance;target.z+=max(0,ground.z+ground_gap(f)-origin.z);origin=target-up*distance
                deform=old['wrist.L'].to_3x3()@bones['wrist.L'].matrix_local.to_3x3().inverted()
                wanted=(world.to_quaternion().inverted()@up).normalized()
                delta=(deform@across).normalized().rotation_difference(wanted).to_matrix();hand=delta@deform
                dorsal=(hand@across).cross(hand@long).normalized()
                wrist=inv@target+ dorsal*.031-hand@offset
                s=old['upperarm01.L'].translation;e=old['lowerarm01.L'].translation
                elbow=Vector(support.bend_joint(list(s),list(wrist),a,b,list(e-s)))
                bend=math.degrees(math.acos(max(-1,min(1,(wrist-elbow).normalized().dot((hand@long).normalized())))))
                if bend>45:raise ValueError('wrist:'+str(bend))
                if f>252 and (elbow-proposed[f-1]['elbow']).length>.04:raise ValueError('elbow continuity')
                proposed[f]=dict(elbow=elbow,wrist=wrist,hand=hand,center=target,origin=origin,up=up,bend=bend)
            strike_velocity=[24*(proposed[f]['origin'].z-proposed[f-1]['origin'].z) for f in range(296,301)]
            if not accelerating_strike(strike_velocity):raise ValueError('strike slowdown:'+str(strike_velocity))
            chosen=height;break
        except ValueError as error:failures.append(dict(height=height,error=str(error)))
    if chosen is None:raise ValueError('GESTURE353_PREFLIGHT:'+str(failures))
    records=[];maximum_grip=0.;maximum_horse=0.
    for f,row in capture.items():
        scene.frame_set(f);bpy.context.view_layer.update();old=row['bones'];v=proposed[f]
        s=old['upperarm01.L'].translation;e=old['lowerarm01.L'].translation;w=old['wrist.L'].translation
        for main,helpers,old_a,old_b,new_a,new_b in [('upperarm01.L',['upperarm01.L','upperarm02.L'],s,e,s,v['elbow']),('lowerarm01.L',['lowerarm01.L','lowerarm02.L'],e,w,v['elbow'],v['wrist'])]:
            rotation=(old_b-old_a).normalized().rotation_difference((new_b-new_a).normalized()).to_matrix().to_4x4()
            delta=Matrix.Translation(new_a)@rotation@Matrix.Translation(-old_a)
            for name in helpers:
                pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=delta@old[name]
                for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)
                bpy.context.view_layer.update()
        wm=(v['hand']@bones['wrist.L'].matrix_local.to_3x3()).to_4x4();wm.translation=v['wrist'];delta=wm@old['wrist.L'].inverted()
        for name in names:
            if not name.startswith(('wrist','finger')):continue
            pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=delta@old[name]
            for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)
            bpy.context.view_layer.update()
        sm=v['up'].to_track_quat('Z','Y').to_matrix().to_4x4()@Matrix.Diagonal((*row['shaft'].to_scale(),1));sm.translation=v['origin']
        shaft.rotation_mode='QUATERNION';shaft.matrix_world=sm
        for prop in ('location','rotation_quaternion','scale'):shaft.keyframe_insert(prop,frame=f)
        bpy.context.view_layer.update()
        actual=row['world']@grip(dict(bones={n:rig.pose.bones[n].matrix.copy() for n in names}))
        station=shaft.matrix_world@Vector((0,0,distance/row['shaft'].to_scale().z));maximum_grip=max(maximum_grip,(station-actual).length)
        maximum_horse=max(maximum_horse,max(abs(horse.matrix_world[i][j]-row['horse'][i][j]) for i in range(4) for j in range(4)))
        records.append(dict(frame=f,grip=list(actual),tip=list(v['origin']),wrist_bend=v['bend'],elbow=list(v['elbow'])))
    if maximum_grip>1e-4 or maximum_horse>1e-5:raise ValueError('GESTURE353_INTERFACE')
    for ob in (rig,shaft):
        for fc in motion.curves(ob):
            for k in fc.keyframe_points:
                if 252<=k.co.x<=441:k.interpolation='LINEAR'
    rig['gesture353']=1;scene.frame_set(327);bpy.context.view_layer.update()
    report=dict(changed=True,source_preserved=True,height=chosen,failed_numeric_preflights=failures,grip_station=distance,ground=list(ground),frames=records,
                strike_velocity=strike_velocity,
                maximum_material_grip_error=maximum_grip,maximum_horse_root_error=maximum_horse,maximum_wrist_bend=max(x['wrist_bend'] for x in records),
                scope='Phase-specific cue/strike/carry, fixed material grip; actual arm/cloth silhouette and AV remain unqualified.')
    (out/'gesture353.json').write_text(json.dumps(report,indent=2)+'\n');return report
