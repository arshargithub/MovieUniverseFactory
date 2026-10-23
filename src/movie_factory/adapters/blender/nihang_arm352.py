"""Bounded coordinated spear-arm proof; no runtime paths or code parameters."""
import math
import numpy as np


def unit(v):
    a=np.asarray(v,dtype=float);n=np.linalg.norm(a)
    if not np.isfinite(n) or n<1e-8:raise ValueError('ARM352_DEGENERATE')
    return a/n


def basis(a,b):
    y=unit(a);z=unit(np.cross(y,b));return np.column_stack((np.cross(y,z),y,z))


def turn(v,axis,angle):
    u=unit(axis);v=np.asarray(v);return v*math.cos(angle)+np.cross(u,v)*math.sin(angle)+u*np.dot(u,v)*(1-math.cos(angle))


def solve(s,center,up,rest,pole,drop,yaw):
    s0,e0,w0,across,longitudinal,offset=map(np.asarray,rest)
    s=np.asarray(s);up=unit(up);center=np.asarray(center)-up*drop
    forward=center-s;forward-=up*np.dot(forward,up);forward=unit(turn(unit(forward),up,yaw))
    # Index-to-little metacarpal axis follows the shaft; palm faces its grip.
    def frame(a,b):
        x=unit(a);y=unit(np.asarray(b)-x*np.dot(x,b));return np.column_stack((x,y,np.cross(x,y)))
    hand=frame(up,forward)@frame(across,longitudinal).T
    dorsal=unit(np.cross(hand@unit(across),hand@unit(longitudinal)))
    wrist=center+dorsal*.031-hand@offset
    a=np.linalg.norm(e0-s0);b=np.linalg.norm(w0-e0);delta=wrist-s;d=np.linalg.norm(delta)
    if not abs(a-b)+.002<d<a+b-.002:raise ValueError('ARM352_UNREACHABLE')
    axis=delta/d;x=(a*a-b*b+d*d)/(2*d);mid=s+axis*x
    hint=s+pole-mid;hint-=axis*np.dot(hint,axis)
    elbow=mid+unit(hint)*math.sqrt(max(0,a*a-x*x))
    ru=basis(elbow-s,wrist-elbow)@basis(e0-s0,w0-e0).T
    rl=basis(wrist-elbow,elbow-s)@basis(w0-e0,e0-s0).T
    bend=math.degrees(math.acos(float(np.clip(unit(wrist-elbow)@forward,-1,1))))
    # Twist relative to the minimal rotation aligning the upper-arm axis.
    old=unit(e0-s0);new=unit(elbow-s);v=np.cross(old,new);dot=float(old@new)
    if dot<-.9999:raise ValueError('ARM352_SHOULDER_ANTIPARALLEL')
    k=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    swing=np.eye(3)+k+k@k/(1+dot)
    twist=math.degrees(math.acos(float(np.clip((np.trace(swing.T@ru)-1)/2,-1,1))))
    score=(bend/25)**2+(twist/60)**2+20*max(0,elbow[1]-.12)**2+40*max(0,.18-elbow[0])**2
    return dict(wrist=wrist,elbow=elbow,hand=hand,upper=ru,lower=rl,center=center,score=score,bend=bend,twist=twist)


def supported_pose(s,origin,torso,rest):
    """Torso-supported arm; shaft meets hand while its ground tip stays fixed."""
    s0,e0,w0,across,longitudinal,offset=map(np.asarray,rest)
    s=np.asarray(s);origin=np.asarray(origin);torso=np.asarray(torso)
    elbow=s+torso@unit([.32,-.08,-.945])*np.linalg.norm(e0-s0)
    fore=torso@unit([.15,-.96,.23]);wrist=elbow+fore*np.linalg.norm(w0-e0)
    center=wrist.copy()
    def frame(a,b):
        x=unit(a);y=unit(np.asarray(b)-x*np.dot(x,b));return np.column_stack((x,y,np.cross(x,y)))
    for _ in range(12):
        up=unit(center-origin);forward=unit(fore-up*np.dot(fore,up))
        hand=frame(up,forward)@frame(across,longitudinal).T
        dorsal=unit(np.cross(hand@unit(across),hand@unit(longitudinal)))
        center=wrist+hand@offset-dorsal*.031
    up=unit(center-origin)
    ru=basis(elbow-s,wrist-elbow)@basis(e0-s0,w0-e0).T
    rl=basis(wrist-elbow,elbow-s)@basis(w0-e0,e0-s0).T
    bend=math.degrees(math.acos(float(np.clip(fore@(hand@unit(longitudinal)),-1,1))))
    if bend>45 or (torso.T@(elbow-s))[0]<.05:raise ValueError('ARM352_HARD_ANATOMY_BOUND')
    return dict(wrist=wrist,elbow=elbow,hand=hand,upper=ru,lower=rl,center=center,up=up,bend=bend,twist=0.)


def run(bpy,out):
    import json
    from mathutils import Matrix,Vector
    scene=bpy.context.scene;rig=bpy.data.objects['MF coherent Nihang rig'];body=bpy.data.objects['MF coherent Nihang body']
    if rig.get('arm352'):raise ValueError('ARM352_ALREADY_APPLIED')
    shaft=bpy.data.objects['LEADER spear world contact owner'];bones=rig.data.bones
    s0=np.array(bones['upperarm01.L'].head_local);e0=np.array(bones['lowerarm01.L'].head_local);w0=np.array(bones['wrist.L'].head_local)
    across=np.array(bones['finger2-1.L'].head_local-bones['finger5-1.L'].head_local)
    long=np.mean([np.array(bones[f'finger{i}-1.L'].head_local) for i in range(2,6)],axis=0)-w0
    rest=(s0,e0,w0,across,long,long*.70);samples={}
    names=[n for n in bones.keys() if n.endswith('.L') and n.startswith(('upperarm','lowerarm','wrist','finger'))]
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update();inv=rig.matrix_world.inverted()
        old={n:rig.pose.bones[n].matrix.copy() for n in names};wrist=old['wrist.L']
        rot=np.array(wrist.to_3x3()@bones['wrist.L'].matrix_local.to_3x3().inverted())
        palm=np.array(wrist.translation)+rot@rest[-1]
        origin=np.array(inv@shaft.matrix_world.translation)
        up=unit(np.array(inv.to_3x3()@shaft.matrix_world.to_3x3()@Vector((0,0,1))))
        center=origin+up*np.dot(palm-origin,up)
        parent=rig.pose.bones['upperarm01.L'].parent
        torso=parent.matrix.to_3x3()@parent.bone.matrix_local.to_3x3().inverted()
        samples[f]=dict(old=old,s=np.array(old['upperarm01.L'].translation),center=center,up=up,
                        origin=origin,torso=np.array(torso),shaft=shaft.matrix_world.copy())
    solved={f:supported_pose(a['s'],a['origin'],a['torso'],rest) for f,a in samples.items()}
    if max(np.linalg.norm(solved[f]['elbow']-solved[f-1]['elbow']) for f in range(253,442))>.035:
        raise ValueError('ARM352_ELBOW_CONTINUITY')
    records=[]
    for f,a in samples.items():
        scene.frame_set(f);bpy.context.view_layer.update();v=solved[f]
        world_up=rig.matrix_world.to_3x3()@Vector(v['up'])
        sm=world_up.to_track_quat('Z','Y').to_matrix().to_4x4()
        sm=sm@Matrix.Diagonal((*a['shaft'].to_scale(),1));sm.translation=a['shaft'].translation
        shaft.rotation_mode='QUATERNION';shaft.matrix_world=sm
        for prop in ('location','rotation_quaternion','scale'):shaft.keyframe_insert(prop,frame=f)
        bpy.context.view_layer.update()
        for stems,rot,origin,target in ((('upperarm01','upperarm02'),v['upper'],s0,a['s']),
                                       (('lowerarm01','lowerarm02'),v['lower'],e0,v['elbow'])):
            for stem in stems:
                pb=rig.pose.bones[stem+'.L'];m=(Matrix(rot.tolist())@pb.bone.matrix_local.to_3x3()).to_4x4()
                m.translation=Vector(target+rot@(np.array(pb.bone.head_local)-origin))
                pb.rotation_mode='QUATERNION';pb.matrix=m
                for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)
                bpy.context.view_layer.update()
        wm=(Matrix(v['hand'].tolist())@bones['wrist.L'].matrix_local.to_3x3()).to_4x4();wm.translation=Vector(v['wrist'])
        delta=wm@a['old']['wrist.L'].inverted()
        for name,old in a['old'].items():
            if not name.startswith(('wrist','finger')):continue
            pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=delta@old
            for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)
            bpy.context.view_layer.update()
        actual=np.array(rig.pose.bones['wrist.L'].matrix.translation)
        if np.linalg.norm(actual-v['wrist'])>1e-4:raise ValueError('ARM352_POSE_EVALUATION')
        tip_error=(shaft.matrix_world.translation-a['shaft'].translation).length
        if tip_error>1e-5:raise ValueError('ARM352_SPEAR_TIP_MOVED')
        records.append(dict(frame=f,elbow=v['elbow'].tolist(),wrist=v['wrist'].tolist(),center=v['center'].tolist(),wrist_bend=v['bend'],spear_tip_error=tip_error))
    for m in body.modifiers:
        if m.type=='ARMATURE':m.use_deform_preserve_volume=True
    rig['arm352']=1;scene.frame_set(327);bpy.context.view_layer.update()
    report=dict(changed=True,method='Torso-supported arm, shaft meets hand around invariant tip',records=records,
                maximum_wrist_bend=max(x['wrist_bend'] for x in records),maximum_tip_error=max(x['spear_tip_error'] for x in records),
                maximum_adjacent_elbow_step=max(float(np.linalg.norm(solved[f]['elbow']-solved[f-1]['elbow'])) for f in range(253,442)),
                maximum_adjacent_wrist_step=max(float(np.linalg.norm(solved[f]['wrist']-solved[f-1]['wrist'])) for f in range(253,442)),
                scope='Coordinated pose candidate with paired skinning controls; numeric scores are not anatomical approval.')
    (out/'arm352.json').write_text(json.dumps(report,indent=2)+'\n');return report
