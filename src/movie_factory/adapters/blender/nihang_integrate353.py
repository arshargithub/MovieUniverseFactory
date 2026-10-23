"""Fixed consuming-branch integration of12 support and353 compact forelegs.

No recipe code or dynamic source paths. Actual attachments share the coherent
head delta; real hand, not legacy hidden palm, owns reins. Not physics simulation.
"""
import json,math,importlib.util
from pathlib import Path

def module(name):
    spec=importlib.util.spec_from_file_location('integrate353_'+name,Path(__file__).with_name(name+'.py'))
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

def attachment(name):
    return name.startswith(('MF Nihang wrapped crown','MF Nihang overlapped cloth','MF Nihang gathered crown',
                            'eyeball.','iris.','pupil.','brow.','MF347 integrated beard'))

def accelerating(values):
    return len(values)>=3 and all(b<a<0 for a,b in zip(values,values[1:]))

def run(bpy,out):
    from mathutils import Vector
    support=module('nihang_support');motion=module('nihang_motion');curl=module('nihang_motion353');arm=module('nihang_arm352')
    scene=support.select_production_scene(bpy);rig=bpy.data.objects['MF coherent Nihang rig']
    horse=bpy.data.objects['horse.rig']
    if rig.get('integrate353') or horse.get('motion353'):raise ValueError('INTEGRATE353_PARENT')
    if not rig.get('arm352') or not rig.get('finish353'):raise ValueError('INTEGRATE353_MISSING_APPEARANCE')
    accessories=[ob for ob in rig.children_recursive if attachment(ob.name) and not ob.hide_render]
    if len(accessories)!=17:raise ValueError('INTEGRATE353_ATTACHMENT_SET:'+str(len(accessories)))
    captured={}
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update()
        inv=rig.pose.bones['head'].matrix.inverted()
        captured[f]={ob.name:inv@rig.matrix_world.inverted()@ob.matrix_world for ob in accessories}
    path=Path(__file__).resolve().parents[4]/'results/sikh335/motion01/save-c12-recipe.json'
    edit=next(e for e in json.loads(path.read_text())['edits'] if e['kind']=='supported_motion')
    base=motion.run(bpy,edit,support)
    for row in base['frames']:
        f=row['frame'];scene.frame_set(f);bpy.context.view_layer.update()
        for name,factor in [('spine04',.35),('spine02',.65)]:
            pb=rig.pose.bones[name];pb.rotation_mode='XYZ';pb.rotation_euler=(row['rider_response']['pitch']*factor,0,0)
            pb.keyframe_insert('rotation_euler',frame=f)
        bpy.context.view_layer.update()
        # Preserve existing local head acting, update every evaluated attachment.
        for ob in accessories:
            ob.matrix_world=rig.matrix_world@rig.pose.bones['head'].matrix@captured[f][ob.name]
            for prop in ('location','rotation_quaternion','scale'):ob.keyframe_insert(prop,frame=f)
    # Owned arm operation is deliberately rebound after changed parent motion;
    # this does not alter workflow artistic counters or erase previous evidence.
    del rig['arm352'];arm_report=arm.run(bpy,out)
    reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name)
    bit=bpy.data.objects['292 bit support'];records=[];maximum_attachment=0.
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update()
        palm=(rig.pose.bones['finger3-1.R'].head+rig.pose.bones['finger3-2.R'].head)*.5
        end=rig.matrix_world@palm
        for sign,ob in zip((-1,1),reins):
            start=bit.matrix_world.translation+horse.matrix_world.to_3x3()@Vector((sign*.07,0,0));inv=ob.matrix_world.inverted()
            for j,p in enumerate(ob.data.splines[0].points):
                u=j/(len(ob.data.splines[0].points)-1)
                p.co=(*(inv@(start.lerp(end,u)+Vector((0,0,-.045*math.sin(math.pi*u))))),1);p.keyframe_insert('co',frame=f)
        for ob in accessories:
            expected=rig.matrix_world@rig.pose.bones['head'].matrix@captured[f][ob.name]
            maximum_attachment=max(maximum_attachment,max(abs(ob.matrix_world[i][j]-expected[i][j]) for i in range(4) for j in range(4)))
        records.append(dict(frame=f,rein_hand=list(end)))
    if maximum_attachment>1e-4:raise ValueError('INTEGRATE353_HEAD_ATTACHMENT')
    curled=curl.run(bpy,out);index={x['frame']:x for x in curled['frames']}
    velocity={s:[24*(index[f]['hooves'][s][2]-index[f-1]['hooves'][s][2]) for f in range(345+(s=='R'),351+(s=='R'))] for s in ('L','R')}
    if not all(accelerating(v) for v in velocity.values()):raise ValueError('INTEGRATE353_LANDING_SLOWDOWN:'+str(velocity))
    for owner in [rig,*accessories,*[o.data for o in reins]]:
        for fc in motion.curves(owner):
            for k in fc.keyframe_points:
                if 252<=k.co.x<=441:k.interpolation='LINEAR'
    rig['integrate353']=1;scene.frame_set(327);bpy.context.view_layer.update()
    report=dict(changed=True,source_preserved=True,base=base,curl=curled,arm=arm_report,rein_frames=records,
                maximum_attachment_error=maximum_attachment,landing_velocity=velocity,attachments=[o.name for o in accessories],
                scope='12 supported arrival consumed by current actor, head attachments/real reins/spear rebound. Pose and continuous reference review remain required.')
    (out/'integrate353.json').write_text(json.dumps(report,indent=2)+'\n');return report
