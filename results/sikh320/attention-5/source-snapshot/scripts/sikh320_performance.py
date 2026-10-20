"""Shot-owned transform/contact animation; not a general dynamics simulator."""
import math,json
import bpy
import numpy as np
from mathutils import Vector,Matrix,Euler
from mathutils.bvhtree import BVHTree
from sikh257_layout import key,segment
from movie_factory.sikh257_geometry import joint_between
from sikh257_native import mesh
from sikh297_layers import sleeve_points,sleeve_faces
RATE=26/22
def ease(u):
    u=max(0,min(1,u));return u*u*(3-2*u)
def bell(t,a,b,c):return ease((t-a)/(b-a))*(1-ease((t-b)/(c-b)))
def retime(t):
    # Compress the inactive gap between grip and lift. Preserve impact17.10.
    xs=(0,14.28,14.79,15.08,15.42,15.61,15.93,16.14,16.28)
    ys=(0,14.28,14.65,14.84,15.02,15.29,15.70,15.94,16.15)
    if t<=16.28:return float(np.interp(t,xs,ys))
    if t<17.10:
        u=(t-16.28)/.82
        return 16.15+.95*(1-(1-u)**2)
    return t
def curves(owner):
    ad=getattr(owner,'animation_data',None)
    if ad and ad.action:
        for layer in ad.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    yield from bag.fcurves
def warp_rear():
    pivot=bpy.data.objects['HORSE hind support pivot']
    objects={pivot,*pivot.children_recursive}
    spear=bpy.data.objects['LEADER spear world contact owner'];objects.update({spear,*spear.children_recursive})
    objects.update(o for o in bpy.data.objects if o.name.startswith(('leader supported rein292','305 hoof earth puff','305 kicked soil clod')))
    seen=set();count=0
    for ob in objects:
        for owner in (ob,ob.data,getattr(ob.data,'shape_keys',None)):
            if owner is None or owner.as_pointer() in seen:continue
            seen.add(owner.as_pointer())
            ad=getattr(owner,'animation_data',None)
            if not ad or not ad.action:continue
            ad.action=ad.action.copy()
            for fc in curves(owner):
                for p in fc.keyframe_points:
                    for co in (p.co,p.handle_left,p.handle_right):co.x=retime((co.x-1)/24*RATE)/RATE*24+1
                fc.update()
            count+=1
    return count
def upper_owner(root,leader):
    """One pelvis-relative transform for cloth/arms/props, not disconnected sway."""
    existing=next((o for o in root.children if o.name.startswith('320 articulated upper body')),None)
    if existing is not None:return existing,[]
    s=bpy.context.scene;s.frame_set(252);bpy.context.view_layer.update()
    pivot=Vector((0,0,.05 if leader else .88))
    owner=bpy.data.objects.new('320 articulated upper body '+root.name,None);s.collection.objects.link(owner);owner.parent=root;owner.location=pivot
    selected=[]
    for ob in list(root.children):
        if ob==owner:continue
        name=ob.name
        upper=name.startswith(('319 anatomically','319 bound chola','319 chola folded','319 overlapping chola','secondary adult head','secondary facial and crown','297 woven diagonal','297 chola front seam','leader palm','leader upper arm','leader forearm','secondary closed hand','297 crowd sleeve','319 shield rear'))
        if not leader and name.startswith(('spear','300 leaf spearhead','300 round hide shield','300 shield steel boss')):upper=True
        if upper:
            # matrix_parent_inverse offsets the new pivot without rewriting
            # legacy local animation coordinates or mesh cache coordinates.
            ob.parent=owner;ob.matrix_parent_inverse=Matrix.Translation(-pivot);selected.append(ob.name)
    return owner,selected
def add_head_intent(root,owner,leader,index):
    head=next(o for o in owner.children if o.name.startswith('secondary adult head'))
    frame=next(o for o in owner.children if o.name.startswith('secondary facial and crown'))
    # Both skin and all facial/hair/crown parts share the same correction.
    for ob in (head,frame):
        tracks=[]
        for f in range(252,442):
            bpy.context.scene.frame_set(f);tracks.append(ob.rotation_euler.copy())
        for f,rot in zip(range(252,442),tracks):
            t=(f-1)/24*RATE
            if leader:
                rot.z+=.15*bell(t,13.5,14.15,15.2)-.12*bell(t,15.1,16.2,17.65)
                rot.x+=.12*bell(t,13.65,14.35,15.1)+.11*bell(t,17.06,17.22,17.75)
            else:
                side=1 if index%2==0 else -1;start=17.58+(0,.23,.48,.12,.60,.32,.71,.43,.83,.55)[index]
                rot.z+=side*(.36*bell(t,start-.7,start-.25,start+.5)-.28*bell(t,start+.35,start+1,start+2.6))
                rot.x+=.055*bell(t,start-.35,start+.1,start+.8)
            ob.rotation_euler=rot;key(ob,f)
    rebind_neck(head)

def rebind_neck(head):
    # Rebuild the existing lower-neck corrective from changed head ownership.
    neck=next(o for o in head.children if o.name.startswith('319 torso to head neck bridge'))
    bpy.context.scene.frame_set(252);bpy.context.view_layer.update()
    rest=head.matrix_parent_inverse@Matrix.Translation(head.location)@Euler((0,0,head.rotation_euler.z)).to_matrix().to_4x4()@Matrix.Diagonal((*head.scale,1))
    for f in range(252,442):
        bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
        correction=np.array(head.matrix_local.inverted()@rest)-np.eye(4)
        for i in range(3):
            for j in range(4):
                sk=neck.data.shape_keys.key_blocks[f'Anchored neck transform {i}{j}'];sk.value=float(correction[i,j]);sk.keyframe_insert('value',frame=f)
def animate_upper(owner,leader,index):
    for f in range(252,442):
        t=(f-1)/24*RATE
        if leader:
            prep=bell(t,13.5,14.8,15.4);rise=bell(t,15.03,15.98,17.10);land=bell(t,17.08,17.23,17.75)
            owner.rotation_euler=(.055*prep-.105*rise+.16*land,-.04*prep+.03*rise,.07*bell(t,13.5,14.2,15.3))
            owner.location.z=.05-.018*land+.004*math.sin(t*2.1)
        else:
            start=17.58+(0,.23,.48,.12,.60,.32,.71,.43,.83,.55)[index]
            u=(t-start)/2.35;active=math.sin(math.pi*max(0,min(1,u)));side=1 if index%2==0 else -1
            owner.rotation_euler=(.04*active,.025*math.sin(u*math.tau*2+index)*active,side*.15*bell(t,start-.5,start+.2,start+1.3))
            owner.location.z=.88+.006*math.sin(t*1.6+index)*(.2+.8*active)
        key(owner,f)
def crowd(out):
    s=bpy.context.scene;s.frame_set(252);road=bpy.data.objects['irregular packed farm track']
    ground=BVHTree.FromPolygons([road.matrix_world@v.co for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    roots=sorted([o for o in s.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:int(o.name.split()[-1]))
    reports=[]
    for i,r in enumerate(roots):
        s.frame_set(252);origin=r.location.copy();side=1 if i%2==0 else -1
        feet=sorted([o for o in r.children if o.name.startswith('PROXY boot')],key=lambda o:o.name)
        ups=sorted([o for o in r.children if o.name.startswith('PROXY thigh')],key=lambda o:o.name)
        lows=sorted([o for o in r.children if o.name.startswith('PROXY calf')],key=lambda o:o.name)
        starts=[o.matrix_world.translation.copy() for o in feet]
        start=17.58+(0,.23,.48,.12,.60,.32,.71,.43,.83,.55)[i]
        duration=.43+.025*(i%3);stepcount=6;stride=1.7/3
        # People turn to move diagonally BACK toward the verge, rather than
        # remaining face-on while translating sideways. Faces subsequently
        # turn back toward the rider while the body settles half-open.
        heading=-side*1.0;direction=Vector((side*1.7,-.56-.05*(i%3),0))
        histories=[[],[]];footrows=[]
        for f in range(252,442):
            s.frame_set(f);t=(f-1)/24*RATE
            yaw=heading*ease((t-start+.3)/.65)
            yaw+=( -side*.60-heading)*ease((t-start-2.28)/.55)
            targets=[];progress=[];lifts=[]
            for k in range(2):
                order=0 if k==(1 if side>0 else 0) else 1
                steps=0.;lift=0.
                for n in range(order,stepcount,2):
                    u=(t-start-n*(duration*.83))/duration
                    steps+=ease(u)
                    if 0<u<1:lift=.085*math.sin(math.pi*u)**1.4
                frac=steps/3;target=starts[k]+direction*frac
                # Sideways spacing rotates into a narrow walking stance.
                rot=Euler((0,0,yaw)).to_matrix();local=Vector(((-.11 if k==0 else .11),0,0))
                target+=(rot@local-local)*ease(frac*4)
                hit=ground.ray_cast(target+Vector((0,0,5)),Vector((0,0,-1)))[0]
                if hit is None:raise ValueError('320 crowd support missing')
                target.z=hit.z+.055*r.scale.z+lift
                targets.append(target);progress.append(frac);lifts.append(lift)
            center=(targets[0]+targets[1])/2
            r.location=origin+direction*(sum(progress)/2);r.location.z=center.z-.055*r.scale.z-.012*max(lifts)/.085
            r.rotation_euler=(0,side*.025*(lifts[0]-lifts[1])/.085,yaw);key(r,f);bpy.context.view_layer.update()
            inv=r.matrix_world.inverted()
            for k,(up,lo,foot) in enumerate(zip(ups,lows,feet)):
                p=inv@targets[k];hip=Vector((-.11 if k==0 else .11,0,.84))
                if (p-hip).length>.895:
                    r.location.z-=((p-hip).length-.89)*r.scale.z;key(r,f);bpy.context.view_layer.update();inv=r.matrix_world.inverted();p=inv@targets[k]
                knee=Vector(joint_between(hip,p,.45,.45,(0,1,0)))
                segment(up,hip,knee,.074);segment(lo,knee,p,.057);foot.location=p
                foot.rotation_euler=(.20*lifts[k]/.085,0,0)
                for ob in (up,lo,foot):key(ob,f)
                histories[k].append(sleeve_points(hip,knee,p,(.105,.088,.050)))
            footrows.append({'frame':f,'feet':[list(p) for p in targets],'yaw':yaw})
        # Rebuild visible trouser geometry from the new supported limbs.
        old=[o for o in r.children if not o.hide_render and 'trousers' in o.name]
        mat=old[0].data.materials[0]
        for ob in old:ob.hide_render=True;ob.hide_viewport=True
        for poses in histories:
            ob=mesh('320 articulated gathered trousers',poses[0],sleeve_faces(),mat);ob.parent=r;ob.shape_key_add(name='Basis')
            for f,pts in zip(range(252,442),poses):
                sk=ob.shape_key_add(name=f'frame{f}');
                for p,q in zip(sk.data,pts):p.co=q
                for ff,val in ((f-1,0),(f,1),(f+1,0)):sk.value=val;sk.keyframe_insert('value',frame=ff)
        upper,names=upper_owner(r,False);animate_upper(upper,False,i)
        if names:add_head_intent(r,upper,False,i)
        reports.append({'actor':r.name,'reaction_start':start,'upper_owner':upper.name,'children':names,'feet':footrows})
    return reports
def rebuild_reins():
    rig=bpy.data.objects['horse.rig'];bit=bpy.data.objects['292 bit support'];hand=bpy.data.objects['leader palm']
    reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name)
    for f in range(252,442):
        bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
        for sign,ob in zip((-1,1),reins):
            start=bit.matrix_world.translation+rig.matrix_world.to_3x3()@Vector((sign*.07,0,0));end=hand.matrix_world.translation
            for j,p in enumerate(ob.data.splines[0].points):
                u=j/(len(ob.data.splines[0].points)-1);q=start.lerp(end,u)+Vector((0,0,-.075*math.sin(math.pi*u)));p.co=(*q,1);p.keyframe_insert('co',frame=f)
    spear=bpy.data.objects['LEADER spear world contact owner'];hand=bpy.data.objects['leader palm.001']
    for f in range(252,442):
        bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
        spear.rotation_mode='QUATERNION';spear.rotation_quaternion=(hand.matrix_world.translation-spear.location).to_track_quat('Z','Y');key(spear,f)
def build(out):
    warped=warp_rear();r=bpy.data.objects['mounted leader'];upper,names=upper_owner(r,True)
    animate_upper(upper,True,0);add_head_intent(r,upper,True,0);rebuild_reins()
    crowd_report=crowd(out)
    # Linear per-frame samples retain authored trajectories without hidden
    # Bezier handle overshoot at impact, support exchange or partial poses.
    for ob in bpy.data.objects:
        if ob.name.startswith('320'):
            for owner in (ob,ob.data,getattr(ob.data,'shape_keys',None)):
                if owner is None:continue
                for fc in curves(owner):
                    for p in fc.keyframe_points:p.interpolation='LINEAR'
    (out/'crowd-contact-tracks.json').write_text(json.dumps(crowd_report,indent=2))
    return {'retimed_action_owners':warped,'leader_upper':names,'crowd_actors':len(crowd_report),'impact_source_seconds':17.10,'direct_av':False}
