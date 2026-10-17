"""Reviewed staging construction, not final character or cloth qualification."""
import math,json
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector,Matrix
from sikh257_native import ROOT,scene_setup,camera_at,material,mesh,sphere
from sikh257_layout import empty,attach,tube,capsule,segment,key,loft,dust_pool,horse_leader
from movie_factory.sikh257_geometry import joint_between
from movie_factory.sikh291_motion import ease,pulse,travel,yaw,bike_position,wheel_angle,rear_amount,crowd_step,FPS,FRAMES,RATE,launch_amount,uncover_amount,greeting,spear_lift,PARKED,FRONT_FIXED,REAR_FIXED

BASE=ROOT/'.runtime/art-direction/series01-sikh291'

def bike(out):
    source=ROOT/'.runtime/art-direction/series01-sikh289/inspect-03/donor.blend'
    rows=json.loads((ROOT/'.runtime/art-direction/series01-sikh289/inspect-03/components.json').read_text())
    rows={r['name']:r for r in rows}
    with bpy.data.libraries.load(str(source),link=False) as (_,d):d.objects=list(rows)
    for ob in d.objects:bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    root=empty('BIKE travel owner');steer=empty('BIKE steering owner',root)
    front=empty('BIKE front rolling owner',steer);rear=empty('BIKE rear rolling owner',root)
    scale=1.54/(7.844+6.65);rot=Matrix.Rotation(-.017,3,'X')
    def convert(p):return (rot@(Vector(p)-Vector((0,-.597,0))))*scale+Vector((0,0,-.012))
    fc=convert((0,-7.844,3.325));rc=convert((0,6.65,3.735))
    steer.location=convert((0,-4.6,9));steer.rotation_mode='QUATERNION'
    front.location=fc-steer.location;rear.location=rc
    front['rolling_radius']=float(fc.z);rear['rolling_radius']=float(rc.z)
    paint=material('Enfield | muted military olive',(.13,.17,.115))
    steel=material('Enfield | worn steel',(.30,.33,.34));steel.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.72
    dark=material('Enfield | engine dark steel',(.065,.075,.083))
    rubber=material('Enfield | charcoal tire',(.019,.022,.025))
    seat=material('Enfield | brown saddle',(.095,.047,.020))
    groups={};assignment=[]
    for ob in d.objects:
        r=rows[ob.name];lo=np.array(r['min']);hi=np.array(r['max']);c=(lo+hi)/2
        pts=np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices])*10
        # Imported geometry was baked before diagnostic object scale. Assert
        # local source coordinates; never guess from a thumbnail or object name.
        if not np.allclose(pts.min(0),lo,atol=.002):raise ValueError(f'Donor coordinate binding drift {ob.name}: {pts.min(0)} != {lo}; {ob.matrix_world}')
        part=int(ob.name[-3:])
        if lo[2]>10.25 or part in PARKED or part in (92,93,733,734):
            assignment.append({'part':ob.name,'owner':'removed mirror/bar/parked stand or replaced saddle spring'});bpy.data.objects.remove(ob);continue
        radial_f=np.sqrt((pts[:,1]+7.844)**2+(pts[:,2]-3.325)**2)
        radial_r=np.sqrt((pts[:,1]-6.65)**2+(pts[:,2]-3.735)**2)
        owner=root;mat=steel;offset=Vector((0,0,0))
        if part in FRONT_FIXED:
            owner=steer;offset=steer.location.copy();mat=steel
        elif part in REAR_FIXED:owner=root;mat=steel
        elif radial_f.max()<3.38 and max(abs(lo[0]),abs(hi[0]))<1.5:
            owner=front;offset=fc;mat=rubber if radial_f.mean()>2.82 else steel
        elif radial_r.max()<3.56 and max(abs(lo[0]),abs(hi[0]))<1.5:
            owner=rear;offset=rear.location.copy();mat=rubber if radial_r.mean()>2.99 else steel
        elif hi[1]<-3.9 or ob.name in ('donor-part-000','donor-part-001'):
            owner=steer;offset=steer.location.copy();mat=paint if c[2]>4 else steel
        elif ob.name=='donor-part-117':mat=seat
        elif c[2]>6.8:mat=paint
        elif abs(c[0])<1.4:mat=dark
        g=groups.setdefault((owner,mat),[[],[]]);start=len(g[0])
        saddle_shift=Vector((0,.09,-.16)) if part==117 else Vector((0,0,0))
        g[0].extend([tuple(convert(p)-offset+saddle_shift) for p in pts]);g[1].extend([tuple(start+i for i in p.vertices) for p in ob.data.polygons])
        assignment.append({'part':ob.name,'owner':owner.name,'material':mat.name,'vertices':len(pts)})
        bpy.data.objects.remove(ob)
    for (owner,mat),(vs,fs) in groups.items():mesh('actual donor | '+owner.name+' | '+mat.name,vs,fs,mat).parent=owner
    before=set(bpy.data.objects)
    tube('adapted low drag bar',[(-.42,-.14,1.08),(-.19,-.18,1.08),(0,-.31,1.04),(.19,-.18,1.08),(.42,-.14,1.08)],.016,steel,steer)
    for sign in (-1,1):
        capsule('rubber grip',(sign*.31,-.15,1.08),(sign*.43,-.14,1.08),.024,rubber,steer)
        tube('lever',[(sign*.30,-.20,1.08),(sign*.43,-.20,1.045)],.007,steel,steer)
        tube('foot rest',[(sign*.14,-.16,.34),(sign*.31,-.16,.34)],.025,dark,root)
    for sign in (-1,1):
        tube('lower saddle support',[(sign*.10,.40,.62),(sign*.10,.49,.75)],.018,dark,root)
        tube('lower saddle spring',[(sign*.10+.028*math.cos(k*math.tau/12),.49+.028*math.sin(k*math.tau/12),.63+k/72*.11) for k in range(73)],.006,steel,root)
    lamp=material('warm headlamp',(.8,.52,.20));bs=lamp.node_tree.nodes['Principled BSDF'];bs.inputs['Emission Color'].default_value=(1,.62,.25,1);bs.inputs['Emission Strength'].default_value=3
    lamp_center=convert((0,-6.22,9.92))
    tube('headlamp fitted bezel',[tuple(lamp_center+Vector((.098*math.cos(k*math.tau/64),.008,.098*math.sin(k*math.tau/64)))) for k in range(65)],.009,steel,steer)
    attach(sphere('headlamp lens backing',lamp_center+Vector((0,.050,0)),(.096,.040,.096),dark),steer)
    attach(sphere('warm lamp glass',lamp_center,(.091,.009,.091),lamp),steer)
    for ob in set(bpy.data.objects)-before:
        if ob.parent==steer:ob.location-=steer.location
    light=bpy.data.lights.new('headlamp road pool','SPOT');light.energy=60;light.color=(1,.72,.38);light.spot_size=.8;light.spot_blend=.65;light.shadow_soft_size=.08
    ob=bpy.data.objects.new('headlamp beam',light);bpy.context.scene.collection.objects.link(ob);ob.parent=steer;ob.location=lamp_center-steer.location;ob.rotation_euler=(Vector((0,-4,-.8))).to_track_quat('-Z','Y').to_euler()
    (out/'bike-adaptation.json').write_text(json.dumps({'source':'royal_enfield.glb','scale':scale,'source_pitch':-.017,'front_center':list(front.location),'rear_center':list(rear.location),'parts':assignment},indent=2))
    return root,steer,front,rear

def actor(root):
    # Deliberately faceless staging mannequin. It cannot be mistaken for a new
    # likeness candidate; final v03 head/turban admission remains separate.
    tunic=material('PROXY rider tunic',(.13,.17,.19));skin=material('PROXY warm clay',(.40,.27,.17));black=material('PROXY beard boots',(.032,.025,.021));indigo=material('PROXY covering',(.045,.06,.10))
    torso=empty('RIDER torso performance',root);torso.location=(0,.40,.84)
    loft('PROXY tailored torso',[(0,0,0,.16,.12),(0,-.035,.15,.17,.12),(0,-.075,.36,.23,.13),(0,-.08,.47,.225,.12),(0,-.08,.52,.11,.075)],tunic,torso)
    head=empty('RIDER head performance',torso);head.location=(0,-.08,.57)
    attach(sphere('PROXY head no final identity',(0,-.006,.10),(.087,.09,.13),skin),head)
    attach(sphere('PROXY beard volume',(0,-.064,.008),(.081,.062,.11),black),head)
    # Crossed silhouette bands communicate a turban without claiming final tie.
    attach(sphere('PROXY turban silhouette',(0,.006,.215),(.118,.125,.115),indigo),head)
    for i in range(5):
        pts=[]
        for k in range(65):
            a=k*math.tau/64;pts.append((.119*math.sin(a),.006-.126*math.cos(a),.18+i*.019+.035*math.sin(a)))
        tube('PROXY turban winding',pts,.008,indigo,head)
    # One mesh from rear crown around the face. Shape transport communicates
    # un-tuck timing only; no cloth/fit qualification is claimed.
    vs=[];fs=[]
    for i in range(41):
        u=i/40;a=-math.pi/2+u*math.pi
        for j in range(5):vs.append((-.115*math.sin(a),-.010-.106*math.cos(a),.085-(j/4)*.115))
    for i in range(40):
        for j in range(4):q=i*5+j;fs.append((q,q+5,q+6,q+1))
    cover=mesh('PROXY connected face end',vs,fs,indigo);cover.parent=head;cover.shape_key_add(name='Basis');uncover=cover.shape_key_add(name='pulled clear and hanging')
    for i,v in enumerate(uncover.data):
        u=(i//5)/40;j=i%5;v.co=(.115-.22*u,-.02-.08*math.sin(u*math.pi),.085-.43*u-(j/4)*.115)
    # Equipment stays on the body, not floating in world space.
    leather=material('PROXY bandolier',(.11,.068,.032));brass=material('PROXY cartridges',(.43,.29,.10))
    tube('cartridge bandolier',[(-.19,-.15,.48),(-.07,-.18,.29),(.13,-.10,.02)],.028,leather,torso)
    for i in range(9):
        u=i/8;capsule('cartridge',(-.18+.29*u,-.18+.06*u,.46-.40*u),(-.14+.29*u,-.18+.06*u,.43-.40*u),.009,brass,torso)
    # Nonfunctional prop rests diagonally across the back, with an actual sling.
    for dx in (-.017,.017):tube('slung double barrel',[(-.10+dx,.16,.10),(.25+dx,.17,.72)],.014,black,torso)
    capsule('wood stock',(-.23,.16,.02),(-.10,.16,.14),.043,leather,torso)
    tube('gun sling continuous support',[(-.20,.16,.08),(-.23,.08,.20),(-.17,-.15,.26),(.16,-.19,.46),(.22,-.07,.51),(.22,.14,.50),(.20,.17,.60)],.017,leather,torso)
    limbs={}
    for side in (-1,1):
        for part,rad in [('upper arm',.074),('forearm',.054),('thigh',.090),('shin',.064)]:limbs[side,part]=capsule('PROXY '+part,(0,0,0),(0,0,.3),rad,tunic,root)
        limbs[side,'hand']=attach(sphere('PROXY palm',(0,0,0),(.025,.035,.057),skin),root)
        limbs[side,'boot']=attach(sphere('PROXY boot',(0,0,0),(.065,.13,.06),black),root)
    return dict(torso=torso,head=head,cover=cover,uncover=uncover,limbs=limbs)

def actor_pose(a,root,steer,t,f):
    hold=pulse(t,7.35,.45,18.4,.5);bow=pulse(t,12.6,.55,13.6,.55);greet=greeting(t)
    torso=a['torso'];torso.location=(0,.40,.84+.006*math.sin(t*18)*(1-hold));torso.rotation_euler=(.05+.05*bow+.07*launch_amount(t)+.016*math.sin(t*14)*(1-hold),0,-.12*hold)
    a['head'].rotation_euler=(-.05-.23*hold+.25*bow-.03*launch_amount(t)+.018*math.sin(t*14-.4)*(1-hold),0,.16*hold)
    key(torso,f);key(a['head'],f);bpy.context.view_layer.update()
    transform=torso.matrix_local.copy();reach=ease((t-9.0)/.7)*(1-ease((t-17.3)/.6))
    for side in (-1,1):
        shoulder=transform@Vector((side*.22,-.08,.46));hand=steer.matrix_local@(Vector((side*.37,-.145,1.08))-steer.location)
        if side==1:
            # Anatomical right hand crosses to left ear; pull forward before down.
            u=uncover_amount(t);target=transform@Vector((-.115,-.08-.12*math.sin(u*math.pi),.655-.35*u))
            hand=hand.lerp(target,reach)
        hand=hand.lerp(transform@Vector((side*.024,-.30,.39)),greet)
        try:elbow=joint_between(shoulder,hand,.32,.31,(side*.7,.25,-.6))
        except ValueError as exc:raise ValueError(f'arm reach at {t=} {side=}: shoulder={tuple(shoulder)} hand={tuple(hand)} distance={(hand-shoulder).length}') from exc
        segment(a['limbs'][side,'upper arm'],shoulder,elbow,.072);segment(a['limbs'][side,'forearm'],elbow,hand,.054)
        palm=a['limbs'][side,'hand'];palm.location=hand;palm.rotation_euler=(math.pi/2*(1-greet),0,side*.12*greet)
        hip=Vector((side*.13,.40,.85));foot=Vector((side*.27,-.16,.37))
        if side==-1:foot=foot.lerp(Vector((-.40,.24,.065)),hold)
        knee=joint_between(hip,foot,.46,.45,(side*.30,-1,.05))
        segment(a['limbs'][side,'thigh'],hip,knee,.088);segment(a['limbs'][side,'shin'],knee,foot,.064);a['limbs'][side,'boot'].location=foot
        for part in ('upper arm','forearm','hand','thigh','shin','boot'):key(a['limbs'][side,part],f)
    a['uncover'].value=uncover_amount(t);a['uncover'].keyframe_insert('value',frame=f)

def landscape():
    soil=material('Punjab lane warm pale earth',(.29,.26,.19));green=material('Punjab dark fields',(.075,.12,.075));leaf=material('Punjab tree masses',(.045,.085,.064));bark=material('tree bark',(.07,.067,.053))
    s=bpy.context.scene;rng=np.random.default_rng(289)
    mesh('flat cultivated plain',[(-95,-130,-.05),(95,-130,-.05),(95,125,-.05),(-95,125,-.05)],[(0,1,2,3)],green)
    # Lane shoulders are irregular but nowhere imply mountain relief.
    vs=[];fs=[]
    for j in range(128):
        y=-130+j*2
        for x in (-1.9,1.9):vs.append((x+.1*math.sin(y*.18),y,.0))
        if j:fs.append((j*2-2,j*2,j*2+1,j*2-1))
    mesh('unmetalled farm lane',vs,fs,soil)
    # Ground marks are shader detail, not scattered floating rocks.
    m=soil;nodes=m.node_tree.nodes;links=m.node_tree.links
    tc=nodes.new('ShaderNodeTexNoise');tc.inputs['Scale'].default_value=28;tc.inputs['Detail'].default_value=2
    ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.16,.15,.105,1);ramp.color_ramp.elements[1].color=(.37,.33,.24,1);links.new(tc.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],nodes['Principled BSDF'].inputs['Base Color'])
    variants=[material('field crop '+str(i),(.06+.016*i,.10+.02*i,.055+.009*i)) for i in range(4)]
    for side in (-1,1):
        for j,y in enumerate(range(-125,120,13)):
            mat=variants[j%4];mesh('small field plot',[(side*2.2,y,.01),(side*30,y,.01),(side*30,y+12,.01),(side*2.2,y+12,.01)],[(0,1,2,3)],mat)
            tube('field bund',[(side*2.1,y,.04),(side*55,y,.04)],.065,soil)
        vs=[];fs=[]
        for i in range(60000):
            x=side*float(rng.uniform(2.2,45));y=float(rng.uniform(-125,120));h=float(rng.uniform(.22,.55));w=.025;a=float(rng.uniform(0,math.tau));d=Vector((math.cos(a),math.sin(a),0));n=len(vs)
            vs.extend([(x-d.x*w,y-d.y*w,0),(x+d.x*w,y+d.y*w,0),(x+.04,y+.01,h*.6),(x+.03,y,h)])
            fs.extend([(n,n+1,n+2),(n,n+2,n+3)])
        mesh('thin crop leaves',vs,fs,variants[2])
        # Broken cultivated horizons: clustered irregular broadleaf silhouettes.
        for i in range(35):
            x=side*float(rng.uniform(12,85));y=float(rng.uniform(-120,80));h=float(rng.uniform(3,7))
            if 0<x<35 and -45<y<-18:continue  # Clear the leader's sky silhouette.
            capsule('tree trunk',(x,y,0),(x+.12,y,h*.72),.10,bark)
            for k in range(7):
                loc=(x+float(rng.uniform(-.23,.23))*h,y+float(rng.uniform(-.20,.20))*h,h*float(rng.uniform(.63,.93)))
                bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=loc);ob=bpy.context.object;ob.name='irregular broadleaf mass';ob.scale=(h*.25,h*.22,h*.18);ob.data.materials.append(leaf)
                for v in ob.data.vertices:v.co*=float(rng.uniform(.85,1.16))
    # Deliberate broad low bank: top supports all four horse contacts.
    vs=[];fs=[]
    for j in range(31):
        for i in range(31):
            x=-3.1+i*6.2/30;y=-3.7+j*7.4/30;r=max(abs(x)/3,abs(y)/3.6);z=3.2*(1-ease((r-.43)/.57));vs.append((7.5+x*1.65,-29+y*1.65,z-.01))
    for j in range(30):
        for i in range(30):q=j*31+i;fs.append((q,q+1,q+32,q+31))
    mesh('low field bank for leader',vs,fs,soil)

def people():
    blue=material('PROXY Nihang indigo',(.05,.085,.20));skin=material('PROXY crowd clay',(.31,.23,.15));gold=material('PROXY saffron sash',(.55,.29,.06));dark=material('PROXY crowd boots',(.035,.04,.04));people=[]
    for i in range(10):
        side=-1 if i%2 else 1;x=side*(.38+.42*(i//2));y=-18.4+(i%3)*.32
        r=empty('FOOT WARRIOR '+str(i));r.location=(x,y,0)
        loft('PROXY robe',[(0,0,.50,.20,.13),(0,0,.91,.16,.12),(0,0,1.36,.23,.13),(0,0,1.44,.11,.08)],blue,r)
        attach(sphere('PROXY face',(0,-.01,1.56),(.078,.080,.115),skin),r);attach(sphere('PROXY tall turban',(0,0,1.70),(.108,.115,.16),blue),r)
        tube('PROXY sash',[(-.17,-.13,1.36),(.12,-.13,.89)],.025,gold,r)
        legs=[]
        for side2 in (-1,1):
            capsule('PROXY arm',(side2*.215,0,1.34),(side2*.26,-.05,.99),.064,blue,r)
            upper=capsule('PROXY thigh',(0,0,0),(0,0,.3),.075,blue,r);lower=capsule('PROXY calf',(0,0,0),(0,0,.3),.060,blue,r);foot=attach(sphere('PROXY boot',(0,0,0),(.065,.12,.055),dark),r);legs.append((upper,lower,foot,side2))
        tube('spear',[(.30,0,.12),(.30,0,2.15)],.012,dark,r)
        people.append((r,side,x,y,legs))
    return people

def pose_people(crowd,t,f):
    for i,(root,side,x,y,legs) in enumerate(crowd):
        a=crowd_step(t,i,0);b=crowd_step(t,i,1);dx=(a[0]+b[0])/2
        root.location=(x+side*dx,y,0);key(root,f)
        for k,(up,lo,foot,s) in enumerate(legs):
            step,lift=(a,b)[k];p=Vector((s*.11+side*(step-dx),-.025,.055+lift));hip=(s*.11,0,.84)
            knee=joint_between(hip,p,.45,.45,(0,-1,0));segment(up,hip,knee,.074);segment(lo,knee,p,.057);foot.location=p
            for ob in (up,lo,foot):key(ob,f)

def leader(out):
    root,rig,rider,feet=horse_leader();root.location=(7.5,-29,3.2);root.rotation_euler.z=math.pi+.35
    bpy.context.view_layer.update()
    feet={n:(rig.matrix_world@rig.pose.bones[n].matrix).copy() for n in feet}
    # Re-centre rotation at midpoint of planted hind feet. The rig remains
    # unchanged in neutral; rear support is explicit, not a ground-origin tilt.
    hind=(feet['hind_foot_ik.L'].translation+feet['hind_foot_ik.R'].translation)/2
    local=root.matrix_world.inverted()@hind
    pivot=empty('HORSE hind support pivot',root);pivot.location=local
    rig.parent=pivot;rig.location=-local;rider.parent=pivot;rider.location-=local
    rest=rider.location.copy()
    for ob in list(rider.children):
        if ob.name.startswith('leader arm') or ob.name in ('standard pole','standard flag'):bpy.data.objects.remove(ob,do_unlink=True)
    blue=bpy.data.materials['leader blue'];skin=bpy.data.materials['leader skin'];arms=[]
    for side in (-1,1):
        arms.append((side,capsule('leader upper arm',(0,0,0),(0,0,.2),.06,blue,rider),capsule('leader forearm',(0,0,0),(0,0,.2),.045,blue,rider),attach(sphere('leader palm',(0,0,0),(.028,.028,.045),skin),rider)))
    spear=empty('LEADER spear world contact owner')
    gold=bpy.data.materials['leader sash']
    tube('leader spear shaft',[(0,0,0),(0,0,3.65)],.018,gold,spear)
    mesh('leader spear point',[(-.06,0,3.6),(0,0,3.91),(.06,0,3.6),(0,.022,3.62)],[(0,1,3),(1,2,3),(2,0,3)],gold).parent=spear
    mesh('leader standard cloth',[(0,0,3.48),(0,0,2.94),(0,.55,3.12)],[(0,1,2)],gold).parent=spear
    (out/'horse-control.json').write_text(json.dumps({'hind_pivot_local':list(local),'feet_world':{n:list(m.translation) for n,m in feet.items()},'bones':list(rig.pose.bones.keys())},indent=2))
    return root,pivot,rig,rider,feet,rest,arms,spear

def pose_leader(h,t,f):
    root,pivot,rig,rider,feet,rest,arms,spear=h;a=rear_amount(t);pivot.rotation_euler.x=-.46*a;key(pivot,f)
    rider.rotation_euler.x=.22*a;key(rider,f);bpy.context.view_layer.update()
    acknowledgment=pulse(t,14.1,.3,14.6,.3)
    lift=spear_lift(t)
    grip_local=Vector((.35,-.03,.50+.18*lift/.65))
    tip=root.matrix_world@Vector((.75,-.25,-.01+lift))
    grip=rider.matrix_world@grip_local
    spear.location=tip;spear.rotation_mode='QUATERNION';spear.rotation_quaternion=(grip-tip).to_track_quat('Z','Y');key(spear,f)
    for side,upper,lower,palm in arms:
        shoulder=Vector((side*.20,0,.42));hand=grip_local if side==1 else Vector((-.22,-.37,.23)).lerp(Vector((-.24,-.33,.28)),acknowledgment)
        elbow=joint_between(shoulder,hand,.28,.27,(side,0,-1));segment(upper,shoulder,elbow,.06);segment(lower,elbow,hand,.045);palm.location=hand
        for ob in (upper,lower,palm):key(ob,f)
    for n,world in feet.items():
        pb=rig.pose.bones[n];m=world.copy()
        if n.startswith('fore'):
            # Following chest arc plus gathered front feet; feet are not pinned
            # in mid-air at their old world X/Y while the horse rotates.
            local=root.matrix_world.inverted()@world.translation
            p=h[1].location+Matrix.Rotation(-.46*a,3,'X')@(local-h[1].location)
            p+=Vector((0,.10*a,.35*a));m.translation=root.matrix_world@p
        pb.matrix=rig.matrix_world.inverted()@m;pb.keyframe_insert('location',frame=f);pb.keyframe_insert('rotation_quaternion',frame=f)

def lighting(s,cam):
    for ob in list(bpy.data.objects):
        if ob.type=='LIGHT':bpy.data.objects.remove(ob,do_unlink=True)
    s.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.19,.30,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.40
    for name,angle,power,color in [('moon',(.5,-.5,-.5),2.0,(.60,.73,1)),('sky fill',(.8,.3,2.5),.65,(.42,.52,.72))]:
        d=bpy.data.lights.new(name,'SUN');d.energy=power;d.color=color;d.angle=.12;ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.rotation_euler=angle
    s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.1
    # Atmospheric sky backdrop is outside the cultivated geometry; no fake
    # moon hovering over the roadside. Kept camera-independent across cuts.
    sky=material('moon disc',(.55,.59,.63));bs=sky.node_tree.nodes['Principled BSDF'];bs.inputs['Emission Strength'].default_value=.25
    mn=sky.node_tree.nodes;ml=sky.node_tree.links
    mt=mn.new('ShaderNodeTexCoord');maria=mn.new('ShaderNodeTexNoise');maria.inputs['Scale'].default_value=5;maria.inputs['Detail'].default_value=3;maria.inputs['Roughness'].default_value=.7
    mr=mn.new('ShaderNodeValToRGB');mr.color_ramp.elements[0].position=.31;mr.color_ramp.elements[0].color=(.055,.066,.085,1);mr.color_ramp.elements[1].position=.65;mr.color_ramp.elements[1].color=(.65,.69,.75,1)
    ml.new(mt.outputs['Generated'],maria.inputs[0]);ml.new(maria.outputs['Fac'],mr.inputs[0]);ml.new(mr.outputs[0],bs.inputs['Base Color']);ml.new(mr.outputs[0],bs.inputs['Emission Color'])
    cr=mn.new('ShaderNodeTexVoronoi');cr.inputs['Scale'].default_value=33
    bump=mn.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.32;bump.inputs['Distance'].default_value=.025
    ml.new(mt.outputs['Generated'],cr.inputs['Vector']);ml.new(cr.outputs['Distance'],bump.inputs['Height']);ml.new(bump.outputs[0],bs.inputs['Normal'])
    sphere('distant moon',(15,-110,30),(2.0,2.0,2.0),sky)
    # Broad noisy sky values, not solid ellipsoids that read as floating props.
    n=s.world.node_tree.nodes;l=s.world.node_tree.links;coord=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(3,3,7)
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.5;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.7
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.39;ramp.color_ramp.elements[0].color=(.022,.038,.068,1);ramp.color_ramp.elements[1].position=.66;ramp.color_ramp.elements[1].color=(.13,.20,.30,1)
    l.new(coord.outputs['Normal'],scale.inputs[0]);l.new(scale.outputs[0],noise.inputs['Vector']);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],n['Background'].inputs[0])
    broad=n.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=2.0;broad.inputs['Detail'].default_value=1.2
    mask=n.new('ShaderNodeValToRGB');mask.color_ramp.elements[0].position=.42;mask.color_ramp.elements[1].position=.61
    mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.012,.024,.050,1)
    l.new(coord.outputs['Normal'],broad.inputs['Vector']);l.new(broad.outputs['Fac'],mask.inputs[0]);l.new(mask.outputs[0],mix.inputs[0]);l.new(ramp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n['Background'].inputs[0])
    # Director291 follow-up: an actual clear sky opening around the moon.
    # Direction-space aperture stays fixed in the world, not attached to camera.
    axis=n.new('ShaderNodeVectorMath');axis.operation='DOT_PRODUCT';axis.inputs[1].default_value=tuple(Vector((15,-110,30)).normalized())
    absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE'
    aperture=n.new('ShaderNodeValToRGB');aperture.color_ramp.elements[0].position=.955;aperture.color_ramp.elements[1].position=.985;aperture.color_ramp.interpolation='EASE'
    clear=n.new('ShaderNodeMixRGB');clear.inputs[2].default_value=(.012,.024,.050,1)
    l.new(coord.outputs['Normal'],axis.inputs[0]);l.new(axis.outputs['Value'],absolute.inputs[0]);l.new(absolute.outputs[0],aperture.inputs[0]);l.new(aperture.outputs[0],clear.inputs[0]);l.new(mix.outputs[0],clear.inputs[1]);l.new(clear.outputs[0],n['Background'].inputs[0])

def camera_pose(cam,t):
    y=travel(t)
    if t<4.4:
        u=ease((t-1.0)/3.4);loc=Vector((.90,-3.45,.46)).lerp(Vector((9,5,5.8)),u)+Vector((0,y,0));target=(0,y,1.06);lens=40-10*pulse(t,1.5,.4,2.9,.4)
    elif t<5.7:
        loc=(.28,y+2.3,1.95);target=(1.4,-22.5,2.3);lens=32
    elif t<7.8:
        loc=(4.3,-13.7,1.55);target=(-.1,y,1.05);lens=42
    elif t<13.5:
        loc=(2.4,-12.9,1.75);target=(-.08,-9.6,1.25);lens=48
    elif t<17.5:
        loc=(.6,-26.5,3.35);target=(7.5,-29,4.65);lens=38
    elif t<23.0:
        loc=(2.3,-23.8,1.05);target=(0,y,1.0);lens=34-16*pulse(t,21.65,.45,22.6,.4)
    else:
        u=ease((t-23.0)/3);loc=(.6,-23.0-2*(t-23),2.4+u);target=(0,y-1,1.0);lens=42
    camera_at(cam,loc,target);cam.data.lens=lens

def dust_volumes():
    m=bpy.data.materials.new('staging dust volume');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
    out=n.new('ShaderNodeOutputMaterial');v=n.new('ShaderNodeVolumePrincipled');v.inputs['Color'].default_value=(.64,.60,.51,1);v.inputs['Anisotropy'].default_value=.2;v.inputs['Emission Color'].default_value=(.35,.40,.48,1);v.inputs['Emission Strength'].default_value=.25
    tc=n.new('ShaderNodeTexCoord');dist=n.new('ShaderNodeVectorMath');dist.operation='LENGTH'
    fall=n.new('ShaderNodeMapRange');fall.inputs['From Min'].default_value=.25;fall.inputs['From Max'].default_value=.95;fall.inputs['To Min'].default_value=5;fall.inputs['To Max'].default_value=0
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3;noise.inputs['Detail'].default_value=2
    mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(tc.outputs['Object'],dist.inputs[0]);l.new(dist.outputs['Value'],fall.inputs[0]);l.new(tc.outputs['Object'],noise.inputs[0]);l.new(fall.outputs[0],mul.inputs[0]);l.new(noise.outputs['Fac'],mul.inputs[1]);l.new(mul.outputs[0],v.inputs['Density']);l.new(v.outputs[0],out.inputs['Volume'])
    gain=n.new('ShaderNodeValue');gain.name='stop clearance';gain.outputs[0].default_value=1
    density=n.new('ShaderNodeMath');density.operation='MULTIPLY';l.new(mul.outputs[0],density.inputs[0]);l.new(gain.outputs[0],density.inputs[1]);l.new(density.outputs[0],v.inputs['Density'])
    glow=n.new('ShaderNodeMath');glow.operation='MULTIPLY';glow.inputs[1].default_value=.07;l.new(density.outputs[0],glow.inputs[0]);l.new(glow.outputs[0],v.inputs['Emission Strength'])
    result=[]
    for i in range(18):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);ob=bpy.context.object;ob.name='authored world-space dust '+str(i);ob.data.materials.append(m);result.append(ob)
    return result

def build(out):
    s,cam=scene_setup();s.render.engine='BLENDER_EEVEE';s.render.resolution_x=480;s.render.resolution_y=854;s.render.fps=FPS;s.frame_end=FRAMES
    s.render.image_settings.file_format='PNG';s.render.film_transparent=False;cam.data.type='PERSP';cam.data.clip_end=300
    lighting(s,cam);landscape();root,steer,front,rear=bike(out);a=actor(root);crowd=people();h=leader(out);dust=dust_volumes()
    for f in range(1,FRAMES+1):
        t=(f-1)/FPS*RATE;root.location=bike_position(t);root.rotation_euler.z=yaw(t)
        from mathutils import Quaternion
        axis=(-front.location).normalized();steer.rotation_quaternion=Quaternion(axis,-yaw(t)*.85);key(steer,f)
        bpy.context.view_layer.update()
        front_pos=steer.matrix_local@front.location
        root.location.x=-(Matrix.Rotation(yaw(t),3,'Z')@front_pos).x;key(root,f)
        front_start_y=(steer.location+front.location).y
        front_path_y=travel(t)+(Matrix.Rotation(yaw(t),3,'Z')@front_pos).y
        front.rotation_euler.x=(front_path_y-travel(0)-front_start_y)/front['rolling_radius'];rear.rotation_euler.x=wheel_angle(t,True)*.34/rear['rolling_radius'];key(front,f);key(rear,f)
        actor_pose(a,root,steer,t,f);pose_people(crowd,t,f);pose_leader(h,t,f);camera_pose(cam,t);key(cam,f);cam.data.keyframe_insert('lens',frame=f)
        gain=bpy.data.materials['staging dust volume'].node_tree.nodes['stop clearance'].outputs[0];gain.default_value=(1-pulse(t,7.4,.8,18.5,.15))*(1+.65*launch_amount(t));gain.keyframe_insert('default_value',frame=f)
        for i,ob in enumerate(dust):
            age=(t+i*3.9/18)%3.90;born=t-age;speed=abs(travel(born+.02)-travel(born-.02))/.04+12*launch_amount(born)
            ob.location=(.30*math.sin(i*3.2)+age*.15+launch_amount(born)*(.50*math.sin(i*2.1)+age*.8),travel(born)+.8,.16+age*.32)
            size=(.50+age*.70+.65*launch_amount(born))*(1-ease((age-2.7)/1.2))*min(1,speed/3)
            ob.scale=(max(.001,size),max(.001,size*1.2),max(.001,size*.7));key(ob,f)
    # Dense authored samples are linear. Avoid automatic Bezier overshoot
    # across hand contacts, cuts and stopped wheels.
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for point in curve.keyframe_points:point.interpolation='LINEAR'
    s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
    return s,cam

def controls(out):
    s,cam=build(out)
    from bpy_extras.object_utils import world_to_camera_view
    observations=[]
    for t in (0,.15,.3,.5,1,2,4.8,6.7,7.3,8.4,9.0,9.7,10.5,11.4,12.4,13.1,14.8,15.2,15.5,16.5,18.5,21.5,22,22.4,24.5):
        s.frame_set(1+round(t/RATE*FPS));bpy.context.view_layer.update()
        head=bpy.data.objects['PROXY head no final identity'];p=head.matrix_world.translation
        boots=[o for o in bpy.data.objects if o.name.startswith('PROXY boot') and o.parent and o.parent.name=='BIKE travel owner']
        observations.append({'time':t,'head_world':list(p),'head_screen':list(world_to_camera_view(s,cam,p)),
                             'boot_world_bottoms':[[min((o.matrix_world@Vector(v)).z for v in o.bound_box),o.name] for o in boots]})
        s.render.filepath=str(out/f'beat-{t:04.1f}.png');bpy.ops.render.render(write_still=True)
    (out/'screen-controls.json').write_text(json.dumps(observations,indent=2))
    # Separate support/control coverage, not editorial shots.
    cam.animation_data_clear();cam.data.animation_data_clear();cam.data.type='ORTHO';cam.data.ortho_scale=5.5;s.render.resolution_x=800;s.render.resolution_y=600
    for t in (14.6,15.2,15.5,16.2,17.2):
        s.frame_set(1+round(t/RATE*FPS));camera_at(cam,(15,-29,5),(7.5,-29,4.6));s.render.filepath=str(out/f'horse-side-{t:04.1f}.png');bpy.ops.render.render(write_still=True)
    s.frame_set(1+round(12.8/RATE*FPS));cam.data.ortho_scale=3.0;camera_at(cam,(4,-9.6,1.2),(0,-9.6,1));s.render.filepath=str(out/'support-side.png');bpy.ops.render.render(write_still=True)

def diagnose(out):
    s,cam=scene_setup();s.render.engine='BLENDER_EEVEE';lighting(s,cam);root,steer,front,rear=bike(out)
    cam.data.type='ORTHO';cam.data.ortho_scale=3;s.render.resolution_x=900;s.render.resolution_y=650
    for i in range(4):
        front.rotation_euler.x=i*math.pi/2;rear.rotation_euler.x=i*math.pi/2
        camera_at(cam,(3,0,1),(0,0,.6));s.render.filepath=str(out/f'wheel-cycle-{i}.png');bpy.ops.render.render(write_still=True)
    front.rotation_euler.x=0;rear.rotation_euler.x=0;camera_at(cam,(1.1,-3,1.15),(0,-.3,.9));s.render.filepath=str(out/'lamp-front.png');bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'diagnostic.blend'))

def movie(out):
    s,cam=build(out);frames=out/'frames';frames.mkdir();s.render.filepath=str(frames/'frame-');bpy.ops.render.render(animation=True)

def reopen(out):
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'movie-03/sequence.blend'),load_ui=False,use_scripts=False)
    s=bpy.context.scene;observations=[]
    for frame in range(1,FRAMES+1):
        s.frame_set(frame);bpy.context.view_layer.update()
        front=bpy.data.objects['BIKE front rolling owner'];rear=bpy.data.objects['BIKE rear rolling owner'];foot=bpy.data.objects['PROXY boot'];t=(frame-1)/FPS*RATE
        tip=bpy.data.objects['LEADER spear world contact owner'].matrix_world.translation
        bank=bpy.data.objects['low field bank for leader'];hit,point,normal,index=bank.ray_cast(tip+Vector((0,0,1)),Vector((0,0,-1)))
        if not hit:raise ValueError('Spear missed actual bank contact surface')
        observations.append({'frame':frame,'source_t':t,'front_center_x':front.matrix_world.translation.x,
            'front_ground_gap':front.matrix_world.translation.z-front['rolling_radius'],
            'rear_ground_gap':rear.matrix_world.translation.z-rear['rolling_radius'],
            'support_boot_bottom':min((foot.matrix_world@Vector(v)).z for v in foot.bound_box),
            'supported_greeting_interval':12.3<=t<=17.3,
            'spear_tip_z':bpy.data.objects['LEADER spear world contact owner'].matrix_world.translation.z,
            'spear_actual_ground_gap':tip.z-point.z,
            'right_hand_to_bar':(bpy.data.objects['PROXY palm.001'].matrix_world.translation-(bpy.data.objects['BIKE steering owner'].matrix_world@(Vector((.37,-.145,1.08))-bpy.data.objects['BIKE steering owner'].location))).length,
            'cover_amount':bpy.data.objects['PROXY connected face end'].data.shape_keys.key_blocks['pulled clear and hanging'].value})
    (out/'contact-trace.json').write_text(json.dumps(observations,indent=2))
    for frame in (1,41,179,213,315,445,505):
        s.frame_set(frame);s.render.filepath=str(out/f'frame-{frame:04d}.png');bpy.ops.render.render(write_still=True)
    lamp_parent=bpy.data.objects['warm lamp glass'].parent
    lamp_fit=lamp_parent==bpy.data.objects['headlamp lens backing'].parent==bpy.data.objects['headlamp fitted bezel'].parent==bpy.data.objects['headlamp beam'].parent==bpy.data.objects['BIKE steering owner']
    (out/'reopen.json').write_text(json.dumps({'frames':[1,41,179,213,315,445,505],'frame_end':s.frame_end,'fps':s.render.fps,'object_count':len(s.objects),'lamp_common_steering_owner':lamp_fit}))

