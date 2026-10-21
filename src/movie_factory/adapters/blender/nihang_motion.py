"""Bounded reference-phase choreography and contact rebake, not simulation.

All code is trusted repository code. Recipes supply numeric phase anchors only.
No code, filenames, arbitrary targets, asset scripts or provider instructions.
"""
import math

FIELDS=('pitch','hip_back','hip_drop','neck_pitch','poll_pitch','fold')
BOUNDS=((-1.1,.12),(-.2,.4),(0,.45),(-.4,.8),(-.3,1.2),(0,1))


def validate(edit):
    if set(edit) != {'kind','target','anchors'} or edit['target']!='horse.rig':
        raise ValueError('MOTION_FIELDS')
    rows=edit['anchors']
    if not isinstance(rows,list) or not 4<=len(rows)<=20:raise ValueError('MOTION_ANCHORS')
    previous=251
    for row in rows:
        if set(row)!=set(FIELDS)|{'frame'}:raise ValueError('MOTION_ANCHOR_FIELDS')
        if type(row['frame']) is not int or not previous<row['frame']<=441:raise ValueError('MOTION_FRAME_ORDER')
        previous=row['frame']
        for name,(lo,hi) in zip(FIELDS,BOUNDS):
            value=row[name]
            if type(value) not in (int,float) or not math.isfinite(value) or not lo<=value<=hi:
                raise ValueError('MOTION_VALUE:'+name)
    if rows[0]['frame']!=252 or rows[-1]['frame']!=441:raise ValueError('MOTION_HANDLES')
    return edit


def sample(rows,frame):
    """Shape-preserving cubic Hermite: continuous velocity, no curve overshoot.

    Nonzero slope at internal descending anchors prevents artificial pauses
    before contact. Flat crest/ground anchors are deliberately authored.
    """
    if frame<=rows[0]['frame']:return dict(rows[0])
    if frame>=rows[-1]['frame']:return dict(rows[-1])
    i=next(i for i in range(len(rows)-1) if rows[i]['frame']<=frame<rows[i+1]['frame'])
    xs=[r['frame'] for r in rows];h=xs[i+1]-xs[i];t=(frame-xs[i])/h
    result={'frame':frame}
    for field in FIELDS:
        ys=[r[field] for r in rows]
        ds=[(ys[j+1]-ys[j])/(xs[j+1]-xs[j]) for j in range(len(rows)-1)]
        def slope(j):
            if j==0 or j==len(rows)-1:return 0.
            if ds[j-1]*ds[j]<=0:return 0.
            a=xs[j]-xs[j-1];b=xs[j+1]-xs[j]
            w1=2*b+a;w2=b+2*a
            return (w1+w2)/(w1/ds[j-1]+w2/ds[j])
        result[field]=(2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h*slope(i)+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h*slope(i+1)
    return result


def curves(owner):
    ad=getattr(owner,'animation_data',None)
    if ad and ad.action:
        for layer in ad.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    yield from bag.fcurves


def foreleg_phases(rows,frame):
    """Purposeful load preparation, not periodic noise or sliding ground feet.

    Low steps place each forefoot3cm back over0.29s. Translation happens only
    during lift. At release the target blends into the airborne limb path; the
    second leg follows one frame later and lands one frame later.
    """
    result={}
    for side,start,delay in (('L',291,0),('R',298,1)):
        u=max(0,min(1,(frame-start)/7))
        t=u*u*(3-2*u)
        lift=.035*math.sin(math.pi*u)**1.3
        fold=sample(rows,max(252,frame-delay))['fold']
        # Both prepared targets return to original ground placement only while
        # airborne, so the last part of the descent has no hidden ground slide.
        back=.03*t*(1-max(0,min(1,(frame-307)/10)))
        result[side]={'fold':fold,'back':back,'lift':lift}
    return result


def run(bpy,edit,support):
    from mathutils import Matrix,Vector,Quaternion
    validate(edit)
    baseline=support.capture_stance(bpy)
    rig=bpy.data.objects['horse.rig'];rider=bpy.data.objects['mounted leader']
    upper=bpy.data.objects['320 articulated upper body mounted leader']
    palm=bpy.data.objects['leader palm'];spearhand=bpy.data.objects['leader palm.001']
    bit=bpy.data.objects['292 bit support'];spear=bpy.data.objects['LEADER spear world contact owner']
    reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name)
    if len(reins)!=2 or any(o.type!='CURVE' or len(o.data.splines)!=1 for o in reins):
        raise ValueError('MOTION_REIN_TOPOLOGY')
    # Fixed stance offsets. New root performance does not recapture modified
    # frames and does not inherit the rejected rigid pivot compensation.
    seat=baseline['world'].inverted()@baseline['rider'].translation
    axis=baseline['rotation']@Vector((1,0,0))
    base_rider=baseline['rider'].to_3x3()
    records=[]
    for frame in range(252,442):
        values=sample(edit['anchors'],frame)
        values['forelegs']=foreleg_phases(edit['anchors'],frame)
        support_rows=support.apply_pose(bpy,values,baseline)
        m=(Quaternion(axis,values['pitch']*.38).to_matrix()@base_rider).to_4x4()
        m.translation=rig.matrix_world@seat
        rider.rotation_mode='QUATERNION';rider.matrix_world=m
        for path in ('location','rotation_quaternion','scale'):rider.keyframe_insert(path,frame=frame)
        # Upper-body anticipation/absorption is driven by load and torso speed,
        # rather than an independent periodic sway.
        prev=sample(edit['anchors'],max(252,frame-1))
        velocity=(values['pitch']-prev['pitch'])*24
        upper.rotation_euler.x=-.05*values['fold']+max(-.12,min(.12,velocity*.07))
        upper.keyframe_insert('rotation_euler',frame=frame)
        bpy.context.view_layer.update()
        for sign,ob in zip((-1,1),reins):
            start=bit.matrix_world.translation+rig.matrix_world.to_3x3()@Vector((sign*.07,0,0))
            end=palm.matrix_world.translation
            inv=ob.matrix_world.inverted()
            for j,p in enumerate(ob.data.splines[0].points):
                u=j/(len(ob.data.splines[0].points)-1)
                world=start.lerp(end,u)+Vector((0,0,-.045*math.sin(math.pi*u)))
                p.co=(*(inv@world),1);p.keyframe_insert('co',frame=frame)
        origin=spear.matrix_world.translation.copy()
        delta=spearhand.matrix_world.translation-origin
        if delta.length<.2:raise ValueError('MOTION_SPEAR_CONTACT_DEGENERATE')
        mat=delta.to_track_quat('Z','Y').to_matrix().to_4x4()
        scale=spear.matrix_world.to_scale()
        mat=mat@Matrix.Diagonal((*scale,1));mat.translation=origin
        spear.rotation_mode='QUATERNION';spear.matrix_world=mat
        for path in ('location','rotation_quaternion','scale'):spear.keyframe_insert(path,frame=frame)
        records.append({'frame':frame,'phase':values,'hind_support':support_rows,
                        'seat':list(rider.matrix_world.translation),
                        'rein_hand':list(palm.matrix_world.translation),'spear_hand':list(spearhand.matrix_world.translation)})
    # Dense samples are authored curves; no hidden Bezier overshoot at contact.
    for owner in (rig,rig.data,bpy.data.objects['HORSE hind support pivot'],rider,upper,spear,*[o.data for o in reins]):
        for fc in curves(owner):
            for p in fc.keyframe_points:
                if 252<=p.co.x<=441:p.interpolation='LINEAR'
    return {'scope':'Reference-phase horse and root/upper rider performance with reins/spear rebaked. Rider limb and clothing fit remains visually unqualified.',
            'frames':records}
