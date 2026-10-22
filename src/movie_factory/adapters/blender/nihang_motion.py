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

    Interior slopes remain continuous. A descending fold reaching grounded zero
    has a finite incoming slope, then a zero grounded slope: impact is a contact
    event, not an airborne ease-to-rest. The body absorbs after contact.
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
        incoming=slope(i+1)
        impact=rows[i]['fold']>0 and rows[i+1]['fold']==0
        if impact and field=='fold':
            # A twice-secant endpoint forced a shallow mid-flight pocket then
            # a last-frame rush. Retain finite arrival without that deceleration.
            incoming=1.25*ds[i]
        if impact and field=='pitch':
            # Body braking belongs after the hoof contact, not in mid-air.
            incoming=ds[i]
        result[field]=(2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h*slope(i)+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h*incoming
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


def contact_frames(records):
    """First grounded frame after the crest, independently for both forelegs."""
    result={}
    for side in ('L','R'):
        airborne=False
        for row in records:
            fold=row['phase']['forelegs'][side]['fold']
            if fold>.5:airborne=True
            if airborne and fold==0:
                result[side]=row['frame'];break
        if side not in result:raise ValueError('MOTION_NO_LANDING:'+side)
    return result


def arrival_position(start, previous, end, elapsed, duration):
    """Final airborne path: matched incoming vertical speed, finite impact.

    Unlike easing a fold channel to zero, this constrains the visible endpoint.
    Duration and elapsed are seconds; samples are 24fps. Ground contact is a
    velocity discontinuity absorbed by the existing post-contact body response.
    """
    if not 0<=elapsed<=duration or duration<=0:raise ValueError('ARRIVAL_TIME')
    v=(start[2]-previous[2])*24
    acceleration=2*(end[2]-start[2]-v*duration)/(duration*duration)
    if v>=0 or acceleration>=0:raise ValueError('ARRIVAL_NOT_ACCELERATING_DOWN')
    u=elapsed/duration;s=u*u*(3-2*u)
    return [start[0]+(end[0]-start[0])*s,start[1]+(end[1]-start[1])*s,
            start[2]+v*elapsed+.5*acceleration*elapsed*elapsed]


def rider_samples(rows):
    """Pelvis-relative counterbalance with a critically damped response.

    Positive upper pitch offsets the root's backward rear inclination. Landing
    absorption starts at contact, never as a pre-impact anticipation of impact.
    No periodic oscillation is introduced.
    """
    result={};x=velocity=0.;omega=18.;dt=1/24
    for f in range(252,442):
        v=sample(rows,f);previous=sample(rows,max(252,f-1))
        root_speed=(v['pitch']-previous['pitch'])*24
        age=max(0,(f-350)/24)
        absorption=(age/.13)*math.exp(1-age/.13) if f>=350 else 0.
        target=.18*v['fold']+max(-.09,min(.12,root_speed*.06))+.10*absorption
        # Exact damped step for held target; position and velocity carry forward.
        error=x-target;aux=velocity+omega*error;decay=math.exp(-omega*dt)
        x=target+(error+aux*dt)*decay
        velocity=(velocity-omega*aux*dt)*decay
        result[f]={'pitch':x,'drop':-.018*absorption,'absorption':absorption}
    return result


def retime_landing_fx(bpy,records):
    """Reuse existing earth response, with birth at actual authored contact.

    Only fixed landing event groups are touched. Keep trajectories, dispersion,
    settled solids and material ownership; preserve the invisible frame1 guard.
    """
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    scene=bpy.context.scene
    road=bpy.data.objects['irregular packed farm track']
    ground=BVHTree.FromPolygons([road.matrix_world@v.co for v in road.data.vertices],
                               [list(p.vertices) for p in road.data.polygons])
    index={r['frame']:r for r in records};events=[]
    for side,frame in contact_frames(records).items():
        label='landing-'+('left' if side=='L' else 'right')
        prefixes=('305 hoof earth puff '+label,'305 kicked soil clod '+label)
        objects=sorted([o for o in bpy.data.objects if o.name.startswith(prefixes)],key=lambda o:o.name)
        if len(objects)<4:raise ValueError('MOTION_MISSING_LANDING_FX:'+label)
        births=[]
        for ob in objects:
            keys=[p for fc in curves(ob) if fc.data_path=='hide_render' for p in fc.keyframe_points if p.co.y<.5]
            if not keys:raise ValueError('MOTION_MISSING_FX_BIRTH:'+ob.name)
            births.append(min(float(p.co.x) for p in keys))
        if max(births)-min(births)>.001:raise ValueError('MOTION_FX_BIRTH_MISMATCH')
        old_birth=births[0];shift=frame-old_birth
        scene.frame_set(round(old_birth));bpy.context.view_layer.update()
        clods=[o for o in objects if o.name.startswith(prefixes[1])]
        source=sum((o.matrix_world.translation for o in clods),Vector())/len(clods)
        endpoint=Vector(index[frame]['hind_support'][0 if side=='L' else 1]['fore_visible_hoof'])
        hit=ground.ray_cast(Vector((endpoint.x,endpoint.y,20)),Vector((0,0,-1)))[0]
        if hit is None:raise ValueError('MOTION_FX_GROUND_MISSING')
        # Clod centres retain their radius offset; original event ground point
        # was8mm above terrain and clod centre has another radius*.6 offset.
        radius_offset=sum(o.scale.z for o in clods)/len(clods)
        target=Vector((endpoint.x,endpoint.y,hit.z+.008+radius_offset))
        offset=target-source
        for ob in objects:
            if ob.parent:raise ValueError('MOTION_FX_UNEXPECTED_PARENT')
            if ob.animation_data.action.users>1:
                ob.animation_data.action=ob.animation_data.action.copy()
            for fc in curves(ob):
                for key in fc.keyframe_points:
                    if key.co.x>1:
                        for point in (key.co,key.handle_left,key.handle_right):point.x+=shift
                    if fc.data_path=='location':
                        for point in (key.co,key.handle_left,key.handle_right):point.y+=offset[fc.array_index]
                    key.interpolation='CONSTANT' if fc.data_path=='hide_render' else 'LINEAR'
                fc.update()
        events.append({'event':label,'old_birth':old_birth,'birth':frame,
                       'objects':len(objects),'translation':list(offset),'ground':list(hit),
                       'persistent_clods':len(clods)})
    return events


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
    records=[];rider_motion=rider_samples(edit['anchors'])
    for frame in range(252,442):
        values=sample(edit['anchors'],frame)
        values['forelegs']=foreleg_phases(edit['anchors'],frame)
        for index,side in enumerate(('L','R')):
            begin=343+index;end_frame=350+index
            if begin<frame<=end_frame:
                start=next(r for r in records if r['frame']==begin)['hind_support'][index]['fore_visible_hoof']
                prior=next(r for r in records if r['frame']==begin-1)['hind_support'][index]['fore_visible_hoof']
                end=list(baseline['feet'][side]['f_hoof'].translation)
                values['forelegs'][side]['arrival_target']=arrival_position(start,prior,end,(frame-begin)/24,(end_frame-begin)/24)
        support_rows=support.apply_pose(bpy,values,baseline)
        m=(Quaternion(axis,values['pitch']*.38).to_matrix()@base_rider).to_4x4()
        m.translation=rig.matrix_world@seat
        rider.rotation_mode='QUATERNION';rider.matrix_world=m
        for path in ('location','rotation_quaternion','scale'):rider.keyframe_insert(path,frame=frame)
        # Upper-body anticipation/absorption is driven by load and torso speed,
        # rather than an independent periodic sway.
        response=rider_motion[frame]
        upper.rotation_euler.x=response['pitch']
        upper.location.z=.05+response['drop']
        upper.keyframe_insert('rotation_euler',frame=frame)
        upper.keyframe_insert('location',frame=frame)
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
        records.append({'frame':frame,'phase':values,'hind_support':support_rows,'rider_response':response,
                        'seat':list(rider.matrix_world.translation),
                        'rein_hand':list(palm.matrix_world.translation),'spear_hand':list(spearhand.matrix_world.translation)})
    # Dense samples are authored curves; no hidden Bezier overshoot at contact.
    for owner in (rig,rig.data,bpy.data.objects['HORSE hind support pivot'],rider,upper,spear,*[o.data for o in reins]):
        for fc in curves(owner):
            for p in fc.keyframe_points:
                if 252<=p.co.x<=441:p.interpolation='LINEAR'
    events=retime_landing_fx(bpy,records)
    return {'scope':'Reference-phase horse and root/upper rider performance with reins/spear rebaked. Rider limb and clothing fit remains visually unqualified.',
            'frames':records,'landing_fx':events}
