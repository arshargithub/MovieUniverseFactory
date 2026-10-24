"""Bounded primary-motion preparation proof, not a generic horse simulator.

Exact source derivatives, no mesh/material changes. Rejected prep is replaceable;
the outgoing pose/velocity/contact state is evidence for the next rise unit.
"""
import math, json, hashlib, importlib.util
from pathlib import Path
import numpy as np

FIELDS=('pitch','hip_back','hip_drop','neck_pitch','poll_pitch','left_fold','right_fold','left_back','right_back','left_lift','right_lift','actor_time','left_hind_forward','right_hind_forward','left_hind_lift','right_hind_lift','rider_lean')
BOUNDS=((-0.5,.15),(-.12,.25),(0,.25),(-.65,.65),(-.3,1.2),(0,.75),(0,.75),(-.2,.2),(-.2,.2),(0,.22),(0,.22),(276,314),(0,.32),(0,.32),(0,.12),(0,.12),(-.1,.35))

def validate(edit):
    if set(edit)!={'kind','target','anchors'} or edit['kind']!='mounted_prep367' or edit['target']!='mounted leader':raise ValueError('PREP367_FIELDS')
    a=edit['anchors']
    if not isinstance(a,list) or not 4<=len(a)<=20:raise ValueError('PREP367_ANCHORS')
    if a[0].get('frame') not in (276,283) or not 307<=a[-1].get('frame',0)<=320:raise ValueError('PREP367_INTERVAL')
    previous=275
    for row in a:
        if set(row)!=set(FIELDS)|{'frame'} or type(row['frame']) is not int or not previous<row['frame']<=320:raise ValueError('PREP367_ANCHOR_FIELDS')
        previous=row['frame']
        for k,(lo,hi) in zip(FIELDS,BOUNDS):
            if type(row[k]) not in (float,int) or not math.isfinite(row[k]) or not lo<=row[k]<=hi:raise ValueError('PREP367_BOUND:'+k)
    if any(a[j]['actor_time']>a[j+1]['actor_time'] for j in range(len(a)-1)):raise ValueError('PREP367_ACTOR_CLOCK')
    return edit

def sample(a,f):
    if f<=a[0]['frame']:return dict(a[0])
    if f>=a[-1]['frame']:return dict(a[-1])
    i=next(i for i in range(len(a)-1) if a[i]['frame']<=f<a[i+1]['frame']);xs=[x['frame'] for x in a];h=xs[i+1]-xs[i];t=(f-xs[i])/h;out={'frame':f}
    for k in FIELDS:
        ys=[x[k] for x in a];ds=[(ys[j+1]-ys[j])/(xs[j+1]-xs[j]) for j in range(len(a)-1)]
        def slope(j):
            if j==0:return ds[0]
            if j==len(a)-1:return ds[-1]
            if ds[j-1]*ds[j]<=0:return 0.
            x=xs[j]-xs[j-1];y=xs[j+1]-xs[j];w1=2*y+x;w2=y+2*x
            return (w1+w2)/(w1/ds[j-1]+w2/ds[j])
        out[k]=(2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h*slope(i)+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h*slope(i+1)
    return out

def module(name):
    spec=importlib.util.spec_from_file_location('prep367_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def frozen(bpy):
    # Underlying geometry/shape coordinates, not animated deformation. Includes
    # every actor mesh, so an unintended sculpture cannot hide in a motion proof.
    hashes={}
    for ob in bpy.data.objects:
        if ob.type!='MESH':continue
        h=hashlib.sha256();v=np.empty(len(ob.data.vertices)*3,dtype='<f4');ob.data.vertices.foreach_get('co',v);h.update(v.tobytes())
        if ob.data.shape_keys:
            for key in ob.data.shape_keys.key_blocks:
                q=np.empty(len(key.data)*3,dtype='<f4');key.data.foreach_get('co',q);h.update(key.name.encode());h.update(q.tobytes())
        hashes[ob.name]=h.hexdigest()
    return hashes

def audit(bpy,out):
    from mathutils import Vector
    support=module('nihang_support');scene=support.select_production_scene(bpy);hr=bpy.data.objects['horse.rig'];root=bpy.data.objects['mounted leader'];rows=[]
    names=['torso','hips','chest','neck','head','thigh_fk.L','thigh_fk.R','lower_leg_fk.L','lower_leg_fk.R','forefoot_fk.L','forefoot_fk.R','f_hoof.L','f_hoof.R','r_hoof.L','r_hoof.R']
    def ground(x,y,z):
        point=Vector((x,y,z+1));direction=Vector((0,0,-1));dg=bpy.context.evaluated_depsgraph_get()
        for _ in range(32):
            ok,hit,normal,face,ob,matrix=scene.ray_cast(dg,point,direction,distance=50)
            if not ok:return None
            # Large actual terrain surface, not a particle, horse, pole or leaf.
            dims=sorted(float(v) for v in ob.dimensions)
            if ob.type=='MESH' and dims[1]>3 and dims[2]>3 and any(k in ob.name.lower() for k in ['ground','road','hill','terrain','bank','earth','rutted','track','mound','ridge','plateau']):return dict(z=float(hit.z),object=ob.name)
            point=hit+direction*.0005
        return None
    for f in [276,283,287,291,294,298,300,303,306,310,314]:
        scene.frame_set(f);bpy.context.view_layer.update()
        shaft=bpy.data.objects['leader spear shaft'];ev=shaft.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        try:
            points=[ev.matrix_world@v.co for v in mesh.vertices]
            if not points:raise ValueError('PREP367_NO_POLE_SURFACE')
            bottom=min(points,key=lambda p:p.z);surface=ground(*bottom)
        finally:ev.to_mesh_clear()
        rows.append(dict(frame=f,horse_world=[list(x) for x in hr.matrix_world],rider_world=[list(x) for x in root.matrix_world],pole_bottom=list(bottom),pole_ground=surface,pole_gap=None if surface is None else float(bottom.z-surface['z']),bones={n:dict(head=list(hr.matrix_world@hr.pose.bones[n].head),tail=list(hr.matrix_world@hr.pose.bones[n].tail),basis=[list(x) for x in hr.pose.bones[n].matrix_basis]) for n in names}))
    report=dict(samples=rows,geometry=frozen(bpy),actor_tree=[dict(name=o.name,parent=o.parent.name if o.parent else None,parent_type=o.parent_type,parent_bone=o.parent_bone) for o in [root]+list(root.children_recursive)],scope='Read-only current input preparation/control, actual pole/terrain query and frozen underlying geometry; not an artistic pass.')
    (out/'prepaudit367.json').write_text(json.dumps(report,indent=2)+'\n');scene.frame_set(314)
    return {'samples':len(rows),'geometry_meshes':len(report['geometry']),'report':'prepaudit367.json'}

def run(bpy,out,edit):
    from mathutils import Vector,Matrix,Quaternion
    validate(edit);support=module('nihang_support');motion=module('nihang_motion');scene=support.select_production_scene(bpy)
    if scene.get('prep367'):raise ValueError('PREP367_ALREADY_APPLIED')
    before=frozen(bpy);baseline=support.capture_stance(bpy);hr=bpy.data.objects['horse.rig'];root=bpy.data.objects['mounted leader'];rig=bpy.data.objects['MF coherent Nihang rig'];shaft=bpy.data.objects['LEADER spear world contact owner'];bit=bpy.data.objects['292 bit support']
    # Capture prior source values before authoring, with the original repaired
    # subframe ownership. Replacing an interval removes obsolete interior keys.
    def depth(ob):
        n=0
        while ob.parent is not None:ob=ob.parent;n+=1
        return n
    def key_transform(ob,f):
        rotation='rotation_quaternion' if ob.rotation_mode=='QUATERNION' else 'rotation_axis_angle' if ob.rotation_mode=='AXIS_ANGLE' else 'rotation_euler'
        for path in ('location',rotation,'scale'):ob.keyframe_insert(path,frame=f)
    frames=list(range(edit['anchors'][0]['frame'],edit['anchors'][-1]['frame']+1));actors=[root]+list(root.children_recursive);actors=sorted(actors,key=depth)
    owned=[o for o in actors if o.type!='LIGHT'];captured={}
    for f in frames:
        t=sample(edit['anchors'],f)['actor_time'];scene.frame_set(int(t),subframe=t-int(t));bpy.context.view_layer.update()
        captured[f]=dict(horse=hr.matrix_world.copy(),rider=root.matrix_world.copy(),objects={o.name:o.matrix_basis.copy() for o in owned},bones={b.name:b.matrix_basis.copy() for b in rig.pose.bones},pole=shaft.matrix_world.copy())
    owners=[hr,hr.data,bpy.data.objects['HORSE hind support pivot'],shaft,rig,*owned]
    reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda x:x.name)
    if len(reins)!=2:raise ValueError('PREP367_REINS')
    owners += [o.data for o in reins]
    visited=set()
    for owner in owners:
        for fc in motion.curves(owner):
            if fc.as_pointer() in visited:continue
            visited.add(fc.as_pointer())
            for key in list(fc.keyframe_points):
                if frames[0]<=key.co.x<=frames[-1]:fc.keyframe_points.remove(key,fast=True)
            fc.update()
    records=[]
    for f in frames:
        row=sample(edit['anchors'],f);row['forelegs']={s:dict(fold=row[p+'_fold'],back=row[p+'_back'],lift=row[p+'_lift']) for s,p in [('L','left'),('R','right')]}
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
    # Final flag121 is tied to its old pole clock; preserve its source/cache but
    # invalidate visibility for this primary-motion diagnostic, never fake reuse.
    flag=bpy.data.objects.get('MF363 physically solved tied pennant')
    if flag:flag.hide_render=True
    scene['prep367']=1;scene['flag363_requires_resimulation']=True
    after=frozen(bpy)
    if after!=before:raise ValueError('PREP367_FROZEN_GEOMETRY_CHANGED')
    (out/'prep367.json').write_text(json.dumps(dict(frames=records,frozen_geometry=before,geometry_unchanged=True,scope='Preparation through firstlift only; later rear/landing and source chest remain unaccepted. Physical flag cache invalidated/hidden, not a new flag look. Source camera/environment/materials unchanged.'),indent=2)+'\n')
    scene.frame_set(edit['anchors'][-1]['frame']);return {'frames':len(frames),'geometry_unchanged':True,'flag_cache':'INVALIDATED_PRIMARY_MOTION_PROOF','report':'prep367.json'}
