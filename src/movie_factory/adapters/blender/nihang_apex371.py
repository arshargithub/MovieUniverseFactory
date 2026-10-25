"""Bounded371 ascent/active-crest authoring, preserving accepted preparation.

Existing evaluated-world support/seat/rein method, no mesh sculpt or landing.
"""
import json,math,hashlib,importlib.util
from pathlib import Path
import numpy as np


def module(name):
    spec=importlib.util.spec_from_file_location('apex371_'+name,Path(__file__).with_name(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def validate(edit):
    fields=module('nihang_prep367').FIELDS
    bounds=dict(zip(fields,[(-1.25,-.35),(-.05,.25),(0,.22),(-1.25,.2),(-.75,1.2),
        (0,1),(0,1),(-.2,.2),(-.2,.2),(0,.22),(0,.22),(314,314),
        (0,.32),(0,.32),(0,.12),(0,.12),(-.1,.35)]))
    if set(edit)!={'kind','target','anchors'} or edit['kind']!='mounted_apex371' or edit['target']!='mounted leader':raise ValueError('APEX371_FIELDS')
    rows=edit['anchors']
    if not isinstance(rows,list) or not 4<=len(rows)<=16 or rows[0].get('frame')!=314 or rows[-1].get('frame')!=333:raise ValueError('APEX371_INTERVAL')
    prior=313
    for row in rows:
        if set(row)!=set(fields)|{'frame'} or type(row['frame']) is not int or not prior<row['frame']<=333:raise ValueError('APEX371_ANCHOR_FIELDS')
        prior=row['frame']
        for k,(lo,hi) in bounds.items():
            if type(row[k]) not in (float,int) or not math.isfinite(row[k]) or not lo<=row[k]<=hi:raise ValueError('APEX371_BOUND:'+k)
    return edit


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
    for name,fc in curves(bpy):result[(name,fc.data_path,fc.array_index)]=np.array([fc.evaluate(f) for f in range(276,315)])
    return result


def check_prefix_actions(bpy,before,raise_on_error=True):
    after=prefix_actions(bpy);errors={}
    for k,values in before.items():
        if k not in after:raise ValueError('APEX371_ORIGINAL_TRACK_REMOVED')
        errors[str(k)]=float(np.max(np.abs(values-after[k])))
    if raise_on_error and max(errors.values(),default=0)>1e-6:raise ValueError('APEX371_PREFIX_TRACK_CHANGED')
    return errors


def visibility_keys(prefix, future):
    if set(prefix)!=set(range(276,315)) or any(type(v) is not bool for v in prefix.values()):raise ValueError('APEX371_VISIBILITY_PREFIX')
    if set(future)-{315,333,334} or any(type(v) is not bool for v in future.values()):raise ValueError('APEX371_VISIBILITY_FUTURE')
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
    labels.extend(['370cloth.hide_render','originalpad.hide_render']);return labels


def prefix_states(bpy):
    scene=module('nihang_support').select_production_scene(bpy);hr=bpy.data.objects['horse.rig'];rig=bpy.data.objects['MF coherent Nihang rig']
    root=bpy.data.objects['mounted leader']
    objects=sorted(set([hr,root,bpy.data.objects['LEADER spear world contact owner']]+list(root.children_recursive)),key=lambda o:o.name)
    pad=bpy.data.objects['370 contact-solved saddle cloth'];original=bpy.data.objects['fitted saddle blanket292'];result={}
    for f in range(276,315):
        scene.frame_set(f);bpy.context.view_layer.update();values=[]
        for ob in objects:values.extend(v for row in ob.matrix_world for v in row)
        for ob in (hr,rig):
            for bone in ob.pose.bones:values.extend(v for row in bone.matrix for v in row)
        for ob in sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name):
            for point in ob.data.splines[0].points:values.extend(point.co)
        values.extend(k.value for k in pad.data.shape_keys.key_blocks);values.extend([float(pad.hide_render),float(original.hide_render)])
        result[f]=np.array(values)
    return result


def run(bpy,out,edit):
    from mathutils import Vector,Matrix,Quaternion
    prep=module('nihang_prep367')
    validate(edit);support=module('nihang_support');motion=module('nihang_motion');scene=support.select_production_scene(bpy)
    if not scene.get('prep367') or scene.get('apex371'):raise ValueError('APEX371_SOURCE_STATE')
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
    frames=list(range(315,334));actors=[root]+list(root.children_recursive);actors=sorted(actors,key=depth)
    owned=[o for o in actors if o.type!='LIGHT'];captured={}
    for f in frames:
        t=prep.sample(edit['anchors'],f)['actor_time'];scene.frame_set(int(t),subframe=t-int(t));bpy.context.view_layer.update()
        captured[f]=dict(horse=hr.matrix_world.copy(),rider=root.matrix_world.copy(),objects={o.name:o.matrix_basis.copy() for o in owned},bones={b.name:b.matrix_basis.copy() for b in rig.pose.bones},pole=shaft.matrix_world.copy())
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
            boundary=float(fc.evaluate(314))
            pin=fc.keyframe_points.insert(314,boundary,options={'FAST'})
            pin.interpolation='LINEAR'
            for key in list(fc.keyframe_points):
                if frames[0]<=key.co.x<=frames[-1]:fc.keyframe_points.remove(key,fast=True)
            fc.update()
    records=[]
    for f in frames:
        row=prep.sample(edit['anchors'],f);row['forelegs']={s:dict(fold=row[p+'_fold'],back=row[p+'_back'],lift=row[p+'_lift']) for s,p in [('L','left'),('R','right')]}
        # Each support moves only during its explicit step, then plants under
        # the body. The old too-far-behind endpoint is not a sacred invariant.
        posed_base={**baseline,'feet':{s:{n:m.copy() for n,m in feet.items()} for s,feet in baseline['feet'].items()}}
        for s,p in [('L','left'),('R','right')]:
            offset=baseline['rotation']@Vector((0,-row[p+'_hind_forward']*baseline['unit'],row[p+'_hind_lift']*baseline['unit']))
            for n in ['hind_foot_fk','r_toe_fk','r_hoof']:posed_base['feet'][s][n].translation+=offset
        supports=support.apply_pose(bpy,row,posed_base);delta=hr.matrix_world@captured[f]['horse'].inverted()
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
    # A cached preparation pad must never pose as valid for a new motion.
    # Preserve it through314; use live original fit only for this primary proof.
    old=bpy.data.objects['370 contact-solved saddle cloth'];pad=bpy.data.objects['fitted saddle blanket292']
    for ob,values in [(old,visibility_keys({f:bool(v[-2]) for f,v in prefix_before.items()},{315:True,334:True})),
                      (pad,visibility_keys({f:bool(v[-1]) for f,v in prefix_before.items()},{315:False,333:False,334:True}))]:
        for f,value in values:ob.hide_render=value;ob.keyframe_insert('hide_render',frame=f)
        for fc in motion.curves(ob):
            if fc.data_path=='hide_render':
                for key in fc.keyframe_points:key.interpolation='CONSTANT'
    flag=bpy.data.objects.get('MF363 physically solved tied pennant')
    if flag:flag.hide_render=True
    scene['apex371']=1;scene['flag363_requires_resimulation']=True
    after=prep.frozen(bpy)
    if after!=before:raise ValueError('APEX371_FROZEN_GEOMETRY_CHANGED')
    prefix_after=prefix_states(bpy);errors={str(f):float(np.max(np.abs(prefix_before[f]-prefix_after[f]))) for f in prefix_before}
    action_errors=check_prefix_actions(bpy,actions_before,raise_on_error=False);labels=prefix_layout(bpy);witness=[]
    for f in prefix_before:
        delta=np.abs(prefix_before[f]-prefix_after[f]);index=int(np.argmax(delta))
        if delta[index]>1e-6:witness.append(dict(frame=f,field=labels[index],before=float(prefix_before[f][index]),after=float(prefix_after[f][index]),error=float(delta[index])))
    (out/'apex371-progress.json').write_text(json.dumps(dict(frames=records,prefix_witness=witness,
        maximum_pose_error=max(errors.values()),maximum_action_error=max(action_errors.values(),default=0.),
        worst_action_tracks=sorted(action_errors.items(),key=lambda x:-x[1])[:8],scope='Pre-save diagnostic only; no native/artisticqualification.'),indent=2)+'\n')
    if max(errors.values())>1e-5:raise ValueError('APEX371_ACCEPTED_PREFIX_CHANGED')
    if max(action_errors.values(),default=0)>1e-6:raise ValueError('APEX371_PREFIX_TRACK_CHANGED')
    report=dict(frames=records,geometry_unchanged=True,accepted_prefix_errors=errors,
                accepted_prefix_action_error=max(action_errors.values(),default=0.),
                original_mesh_domains=len(before),new_phase=[315,333],
                contact='Old66cache preserved/gated through314; liveoriginalpad at315..333 is diagnostic/unqualified until separatefinal-surface bake.',
                scope='Rise/apex/activehold only; no landing, mesh/appearance/camera/environment/sound edit. Lateraction/flagcache invalidated.')
    (out/'apex371.json').write_text(json.dumps(report,indent=2)+'\n')
    scene.frame_set(333);return dict(report='apex371.json',frames=len(frames),accepted_prefix_unchanged=True,geometry_unchanged=True)
