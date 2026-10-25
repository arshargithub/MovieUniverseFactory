"""Bounded373 descent/contact/absorption, preserving accepted preparation and crest.

Evaluated-world supported FK, actual hoof trajectories and coupled rider; no mesh sculpt.
"""
import json,math,hashlib,importlib.util
from pathlib import Path
import numpy as np


def module(name):
    spec=importlib.util.spec_from_file_location('landing373_'+name,Path(__file__).with_name(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def validate(edit):
    if not isinstance(edit,dict) or edit.get('target')!='mounted leader':raise ValueError('LANDING373_TARGET')
    if edit.get('kind')=='mounted_landing373_contact':
        if set(edit)!={'kind','target'}:raise ValueError('LANDING373_CONTACT_FIELDS')
        return edit
    fields=module('nihang_prep367').FIELDS
    bounds=dict(zip(fields,[(-1.25,.10),(-.05,.25),(0,.25),(-1.25,.6),(-.75,.8),
        (0,1),(0,1),(-.2,.2),(-.2,.2),(0,.22),(0,.22),(333,333),
        (0,.32),(0,.32),(0,.12),(0,.12),(-.1,.35)]))
    if set(edit)!={'kind','target','anchors','left_contact','right_contact'} or edit['kind']!='mounted_landing373':raise ValueError('LANDING373_FIELDS')
    for side in ('left','right'):
        if type(edit[side+'_contact']) is not int or not 340<=edit[side+'_contact']<=349:raise ValueError('LANDING373_CONTACT_FRAME')
    if not 0<=edit['right_contact']-edit['left_contact']<=2:raise ValueError('LANDING373_CONTACT_ORDER')
    rows=edit['anchors']
    if not isinstance(rows,list) or not 6<=len(rows)<=20 or rows[0].get('frame')!=333 or rows[-1].get('frame')!=367:raise ValueError('LANDING373_INTERVAL')
    prior=332
    for row in rows:
        if set(row)!=set(fields)|{'frame'} or type(row['frame']) is not int or not prior<row['frame']<=367:raise ValueError('LANDING373_ANCHOR_FIELDS')
        prior=row['frame']
        for k,(lo,hi) in bounds.items():
            if type(row[k]) not in (float,int) or not math.isfinite(row[k]) or not lo<=row[k]<=hi:raise ValueError('LANDING373_BOUND:'+k)
    if abs(rows[0]['pitch']+1.225)>1e-8:raise ValueError('LANDING373_ENTRY')
    return edit


def hoof_path(start, previous, end, frame, contact):
    # Ballistic vertical arrival, measured entry velocity. No airborne easing.
    t=(frame-333)/24.;duration=(contact-333)/24.
    v=(start[2]-previous[2])*24
    acceleration=2*(end[2]-start[2]-v*duration)/(duration*duration)
    if acceleration>=0:raise ValueError('LANDING373_NON_DOWNWARD_ACCELERATION')
    if frame>=contact:return list(end)
    u=max(0,min(1,t/duration));h=u*u*(3-2*u)
    return [start[i]+(end[i]-start[i])*h for i in (0,1)]+[start[2]+v*t+.5*acceleration*t*t]


def curves(bpy):
    for action in bpy.data.actions:
        found=[]
        if hasattr(action,'fcurves'):
            try:found=list(action.fcurves)
            except RuntimeError:pass
        if not found:
            for layer in action.layers:
                for strip in layer.strips:
                    for bag in getattr(strip,'channelbags',[]):found.extend(bag.fcurves)
        for fc in found:yield action.name,fc


def prefix_actions(bpy):
    # Actual original scalar tracks, not an assumption that later keys are harmless.
    result={}
    for name,fc in curves(bpy):result[(name,fc.data_path,fc.array_index)]=np.array([fc.evaluate(f) for f in range(276,334)])
    return result


def check_prefix_actions(bpy,before,raise_on_error=True):
    after=prefix_actions(bpy);errors={}
    for k,values in before.items():
        if k not in after:raise ValueError('LANDING373_ORIGINAL_TRACK_REMOVED')
        errors[str(k)]=float(np.max(np.abs(values-after[k])))
    if raise_on_error and max(errors.values(),default=0)>1e-6:raise ValueError('LANDING373_PREFIX_TRACK_CHANGED')
    return errors


def visibility_keys(prefix, future):
    if set(prefix)!=set(range(276,334)) or any(type(v) is not bool for v in prefix.values()):raise ValueError('LANDING373_VISIBILITY_PREFIX')
    if set(future)-{334,367,368} or any(type(v) is not bool for v in future.values()):raise ValueError('LANDING373_VISIBILITY_FUTURE')
    return sorted(prefix.items())+sorted(future.items())


def prefix_layout(bpy):
    hr=bpy.data.objects['horse.rig'];rig=bpy.data.objects['MF coherent Nihang rig'];root=bpy.data.objects['mounted leader']
    objects=sorted(set([hr,root,bpy.data.objects['LEADER spear world contact owner']]+list(root.children_recursive)),key=lambda o:o.name);labels=[]
    for ob in objects:labels.extend(f'{ob.name}.world[{i}]' for i in range(16))
    for ob in (hr,rig):
        for bone in ob.pose.bones:labels.extend(f'{ob.name}:{bone.name}.matrix[{i}]' for i in range(16))
    for ob in sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name):
        for i,point in enumerate(ob.data.splines[0].points):labels.extend(f'{ob.name}.point{i}[{j}]' for j in range(4))
    labels.extend('370cloth.key:'+k.name for k in bpy.data.objects['370 contact-solved saddle cloth'].data.shape_keys.key_blocks)
    labels.extend('371cloth.key:'+k.name for k in bpy.data.objects['371 apex contact-solved saddle cloth'].data.shape_keys.key_blocks)
    labels.extend(['370cloth.hide_render','371cloth.hide_render','originalpad.hide_render']);return labels


def prefix_states(bpy):
    scene=module('nihang_support').select_production_scene(bpy);hr=bpy.data.objects['horse.rig'];rig=bpy.data.objects['MF coherent Nihang rig']
    root=bpy.data.objects['mounted leader']
    objects=sorted(set([hr,root,bpy.data.objects['LEADER spear world contact owner']]+list(root.children_recursive)),key=lambda o:o.name)
    pad=bpy.data.objects['370 contact-solved saddle cloth'];original=bpy.data.objects['fitted saddle blanket292'];result={}
    for f in range(276,334):
        scene.frame_set(f);bpy.context.view_layer.update();values=[]
        for ob in objects:values.extend(v for row in ob.matrix_world for v in row)
        for ob in (hr,rig):
            for bone in ob.pose.bones:values.extend(v for row in bone.matrix for v in row)
        for ob in sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name):
            for point in ob.data.splines[0].points:values.extend(point.co)
        values.extend(k.value for k in pad.data.shape_keys.key_blocks)
        crest=bpy.data.objects['371 apex contact-solved saddle cloth'];values.extend(k.value for k in crest.data.shape_keys.key_blocks);values.extend([float(pad.hide_render),float(crest.hide_render),float(original.hide_render)])
        result[f]=np.array(values)
    return result


def run(bpy,out,edit):
    from mathutils import Vector,Matrix,Quaternion
    prep=module('nihang_prep367')
    validate(edit)
    if edit['kind']=='mounted_landing373_contact':return module('nihang_padsolve370').run(bpy,out,phase='landing')
    support=module('nihang_support');motion=module('nihang_motion');scene=support.select_production_scene(bpy)
    if not scene.get('crest372') or scene.get('landing373'):raise ValueError('LANDING373_SOURCE_STATE')
    before=prep.frozen(bpy);prefix_before=prefix_states(bpy);actions_before=prefix_actions(bpy);baseline=support.capture_stance(bpy);hr=bpy.data.objects['horse.rig'];root=bpy.data.objects['mounted leader'];rig=bpy.data.objects['MF coherent Nihang rig'];shaft=bpy.data.objects['LEADER spear world contact owner'];bit=bpy.data.objects['292 bit support']
    # Capture prior source values before authoring, with the original repaired
    # subframe ownership. Replacing an interval removes obsolete interior keys.
    def depth(ob):
        n=0
        while ob.parent is not None:ob=ob.parent;n+=1
        return n
    def key_transform(ob,f):
        rotation='rotation_quaternion' if ob.rotation_mode=='QUATERNION' else 'rotation_axis_angle' if ob.rotation_mode=='AXIS_ANGLE' else 'rotation_euler'
        for path in ('location',rotation,'scale'):ob.keyframe_insert(path,frame=f)
    frames=list(range(334,368));actors=[root]+list(root.children_recursive);actors=sorted(actors,key=depth)
    owned=[o for o in actors if o.type!='LIGHT'];captured={}
    for f in frames:
        t=333;scene.frame_set(int(t),subframe=t-int(t));bpy.context.view_layer.update()
        captured[f]=dict(horse=hr.matrix_world.copy(),rider=root.matrix_world.copy(),objects={o.name:o.matrix_basis.copy() for o in owned},bones={b.name:b.matrix_basis.copy() for b in rig.pose.bones},pole=shaft.matrix_world.copy())
    entry_feet={}
    for t in (332,333):
        scene.frame_set(t);bpy.context.view_layer.update();entry_feet[t]={side:list(hr.matrix_world@hr.pose.bones['DEF-f_hoof.'+side].head) for side in ('L','R')}
    owners=[hr,hr.data,bpy.data.objects['HORSE hind support pivot'],shaft,rig,*owned]
    reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda x:x.name)
    if len(reins)!=2:raise ValueError('PREP367_REINS')
    owners += [o.data for o in reins]
    visited=set()
    #314 can be interpolated from an obsolete315+ key. Pin its ORIGINAL
    # evaluated scalar before deleting/replacing future keys, preserving the
    # accepted endpoint. Existing full-prefix guards detect handle side effects.
    for owner in owners:
        for fc in motion.curves(owner):
            if fc.as_pointer() in visited:continue
            visited.add(fc.as_pointer())
            boundary=float(fc.evaluate(333))
            pin=fc.keyframe_points.insert(333,boundary,options={'FAST'})
            pin.interpolation='LINEAR'
            for key in list(fc.keyframe_points):
                if frames[0]<=key.co.x<=frames[-1]:fc.keyframe_points.remove(key,fast=True)
            fc.update()
    records=[]
    for f in frames:
        row=prep.sample(edit['anchors'],f);row['forelegs']={}
        for side,p in [('L','left'),('R','right')]:
            contact=edit[p+'_contact'];target=hoof_path(entry_feet[333][side],entry_feet[332][side],list(baseline['feet'][side]['f_hoof'].translation),f,contact)
            opened=max(0,1-(f-333)/6)
            row['forelegs'][side]=dict(fold=row[p+'_fold'],back=row[p+'_back'],lift=0,arrival_target=target,curl=(.22 if side=='L' else .36)*opened,toe=.08*opened)
        # Each support moves only during its explicit step, then plants under
        # the body. The old too-far-behind endpoint is not a sacred invariant.
        posed_base={**baseline,'feet':{s:{n:m.copy() for n,m in feet.items()} for s,feet in baseline['feet'].items()}}
        for s,p in [('L','left'),('R','right')]:
            offset=baseline['rotation']@Vector((0,-row[p+'_hind_forward']*baseline['unit'],row[p+'_hind_lift']*baseline['unit']))
            for n in ['hind_foot_fk','r_toe_fk','r_hoof']:posed_base['feet'][s][n].translation+=offset
        try:supports=support.apply_pose(bpy,row,posed_base)
        except Exception:
            (out/'landing373-failure.json').write_text(json.dumps(dict(failed_phase=row,completed=records),indent=2)+'\n');raise
        delta=hr.matrix_world@captured[f]['horse'].inverted()
        root.matrix_world=delta@captured[f]['rider'];key_transform(root,f)
        for b in rig.pose.bones:
            b.matrix_basis=captured[f]['bones'][b.name];key_transform(b,f)
        for ob in owned:
            if ob!=root:ob.matrix_basis=captured[f]['objects'][ob.name];key_transform(ob,f)
        # Read actual pelvis-to-neck body direction. Source-root angle alone
        # missed the consuming coherent rig's compensation and produced a
        # backward learner-like rider. Rotate about the actual seat/pelvis.
        bpy.context.view_layer.update();pelvis=rig.matrix_world@rig.pose.bones['spine05'].head;neck=rig.matrix_world@rig.pose.bones['neck02'].head;v=neck-pelvis
        forward=baseline['rotation']@Vector((0,-1,0));forward.z=0;forward.normalize();angle=math.atan2(v.dot(forward),v.z);axis=baseline['rotation']@Vector((1,0,0));axis.normalize()
        correction=Matrix.Translation(pelvis)@Quaternion(axis,row['rider_lean']-angle).to_matrix().to_4x4()@Matrix.Translation(-pelvis)
        root.matrix_world=correction@root.matrix_world;key_transform(root,f)
        shaft.matrix_world=correction@delta@captured[f]['pole'];key_transform(shaft,f)
        scene.frame_set(f);bpy.context.view_layer.update();grip=rig.matrix_world@((rig.pose.bones['finger3-1.R'].head+rig.pose.bones['finger3-2.R'].head)*.5)
        for sign,ob in zip((-1,1),reins):
            start=bit.matrix_world.translation+hr.matrix_world.to_3x3()@Vector((sign*.07,0,0));inv=ob.matrix_world.inverted()
            for j,p in enumerate(ob.data.splines[0].points):
                u=j/(len(ob.data.splines[0].points)-1);world=start.lerp(grip,u)+Vector((0,0,-.045*math.sin(math.pi*u)));p.co=(*(inv@world),1);p.keyframe_insert('co',frame=f)
        actual_neck=rig.matrix_world@rig.pose.bones['neck02'].head;actual_pelvis=rig.matrix_world@rig.pose.bones['spine05'].head;actual_v=actual_neck-actual_pelvis
        records.append(dict(frame=f,phase=row,support=supports,horse_world=[list(x) for x in hr.matrix_world],grip=list(grip),rider_sagittal=dict(before=angle,desired=row['rider_lean'],actual=math.atan2(actual_v.dot(forward),actual_v.z),pelvis_error=(actual_pelvis-pelvis).length)))
    for owner in owners:
        for fc in motion.curves(owner):
            for k in fc.keyframe_points:
                if frames[0]<=k.co.x<=frames[-1]:k.interpolation='LINEAR'
            fc.update()
    # Keep both accepted caches in their exact old intervals. Live fitted seed
    # is diagnostic only until a new landing-only exterior cache is admitted.
    old=bpy.data.objects['370 contact-solved saddle cloth'];crest=bpy.data.objects['371 apex contact-solved saddle cloth'];pad=bpy.data.objects['fitted saddle blanket292']
    for ob,index,future in [(old,-3,{334:True,367:True,368:True}),(crest,-2,{334:True,367:True,368:True}),(pad,-1,{334:False,367:False,368:True})]:
        for f,value in visibility_keys({f:bool(v[index]) for f,v in prefix_before.items()},future):
            ob.hide_render=value;ob.keyframe_insert('hide_render',frame=f)
        for fc in motion.curves(ob):
            if fc.data_path=='hide_render':
                for key in fc.keyframe_points:key.interpolation='CONSTANT'
    flag=bpy.data.objects.get('MF363 physically solved tied pennant')
    if flag:flag.hide_render=True
    scene['landing373']=1;scene['flag363_requires_resimulation']=True
    after=prep.frozen(bpy)
    if after!=before:raise ValueError('LANDING373_FROZEN_GEOMETRY_CHANGED')
    prefix_after=prefix_states(bpy);errors={str(f):float(np.max(np.abs(prefix_before[f]-prefix_after[f]))) for f in prefix_before}
    action_errors=check_prefix_actions(bpy,actions_before,raise_on_error=False);labels=prefix_layout(bpy);witness=[]
    for f in prefix_before:
        delta=np.abs(prefix_before[f]-prefix_after[f]);index=int(np.argmax(delta))
        if delta[index]>1e-6:witness.append(dict(frame=f,field=labels[index],before=float(prefix_before[f][index]),after=float(prefix_after[f][index]),error=float(delta[index])))
    (out/'landing373-progress.json').write_text(json.dumps(dict(frames=records,prefix_witness=witness,
        maximum_pose_error=max(errors.values()),maximum_action_error=max(action_errors.values(),default=0.),
        worst_action_tracks=sorted(action_errors.items(),key=lambda x:-x[1])[:8],scope='Pre-save diagnostic only; no native/artisticqualification.'),indent=2)+'\n')
    if max(errors.values())>1e-5:raise ValueError('LANDING373_ACCEPTED_PREFIX_CHANGED')
    if max(action_errors.values(),default=0)>1e-6:raise ValueError('LANDING373_PREFIX_TRACK_CHANGED')
    report=dict(frames=records,geometry_unchanged=True,accepted_prefix_errors=errors,
                accepted_prefix_action_error=max(action_errors.values(),default=0.),
                original_mesh_domains=len(before),new_phase=[334,367],
                contact='Accepted370/371caches preservedthrough333; liveoriginal334..367 isdiagnosticuntilnewlandingcache.',
                scope='Landing334..367 only; accepted276..333 unchanged, no mesh/appearance/camera/environment/sound edit. Lateraction/flagcache unqualified.')
    (out/'landing373.json').write_text(json.dumps(report,indent=2)+'\n')
    scene.frame_set(367);return dict(report='landing373.json',frames=len(frames),accepted_prefix_unchanged=True,geometry_unchanged=True)
