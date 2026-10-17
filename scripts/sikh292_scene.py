"""292 integrated fixed handler. Reuses291 rig, not its review disposition."""
import math,json
import bpy
import numpy as np
from mathutils import Vector
import sikh291_scene as base
from sikh257_native import ROOT,mesh,material,sphere,camera_at
from sikh257_layout import key,tube,empty
from sikh292_assets import environment,sky,enrich_people,enrich_leader,surface
from movie_factory.sikh292_motion import travel,bike_position,wheel_angle,debris_position,slip,FPS,FRAMES,RATE
BASE=ROOT/'.runtime/art-direction/series01-sikh292'
old_camera=base.camera_pose
old_light=base.lighting
old_people=base.people
old_leader=base.leader

def lighting(s,cam):old_light(s,cam);sky(s)
def people():
    c=old_people();enrich_people(c);return c
def leader(out):
    h=old_leader(out);enrich_leader(h);return h
def camera(cam,t):
    old_camera(cam,t)
    if 5.7<=t<7.8:
        camera_at(cam,(4.3,-7.7,1.55),(-.1,travel(t),1.05));cam.data.lens=42
    elif 7.8<=t<13.5:
        # Stop is6m farther back. Whole shot moves, not just its gaze target.
        cam.location.y+=6
    elif 4.4<=t<5.7:
        camera_at(cam,(.28,travel(t)+2.3,1.95),(1.4,-22.5,2.3));cam.data.lens=32

def add_groom():
    rig=bpy.data.objects['horse.rig'];body=bpy.data.objects['horse'];s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
    # Actual deform-bone positions supply the mane route; positions recorded for review.
    bones=rig.pose.bones
    names=[b.name for b in bones if 'neck' in b.name.lower() and b.name.startswith('DEF')]
    if not names:return
    names.sort()
    hair=surface('292 coarse horse mane',[(.008,.011,.015),(.095,.11,.12)],20,rough=.6,bump=.001)
    def attach_bone(ob,bone):
        bpy.context.view_layer.update();world=ob.matrix_world.copy();ob.parent=rig;ob.parent_type='BONE';ob.parent_bone=bone;bpy.context.view_layer.update();ob.matrix_world=world
    rng=np.random.default_rng(292);inv=body.matrix_world.inverted();rmat=rig.matrix_world
    for name in names:
        b=bones[name]
        for i in range(24):
            p=b.head.lerp(b.tail,(i+.5)/24);start=rmat@(p+Vector((0,.55,0)));direction=rmat.to_3x3()@Vector((0,-1,0))
            hit,point,normal,index=body.ray_cast(inv@start,inv.to_3x3()@direction)
            if not hit:continue
            q=body.matrix_world@point
            # Thin, overlapping side-falling locks. Root is actual skin hit;
            # no geometric chevrons sticking outward from the neck.
            length=float(rng.uniform(.16,.25));dx=float(rng.uniform(.07,.12))
            pts=[q,q+rmat.to_3x3()@Vector((dx*.5,.018,-length*.12)),q+rmat.to_3x3()@Vector((dx,.025,-length*.58)),q+rmat.to_3x3()@Vector((dx*.85,.045,-length))]
            ob=tube('rooted mane locks292',pts,float(rng.uniform(.003,.006)),hair);attach_bone(ob,name)
    # Save support names; unknown general wind motion is not qualified.
    body['292_mane_support_bones']=','.join(names)
    # Forelock rooted at poll and tail volume follow the existing deform rig.
    b=bones['DEF-head']
    for i in range(25):
        q=rmat@(b.head+Vector((float(rng.uniform(-.035,.035)),.015,.13)))
        pts=[q,q+rmat.to_3x3()@Vector((.005,-.07,-.04)),q+rmat.to_3x3()@Vector((.012,-.13,-.13))]
        attach_bone(tube('horse forelock292',pts,.003,hair),'DEF-head')
    tails=[b for b in bones if b.name.startswith('DEF-tail')]
    tails.sort(key=lambda b:b.name)
    if tails:
        for i in range(45):
            dx=float(rng.uniform(-.04,.04));dy=float(rng.uniform(-.025,.025));pts=[rmat@(b.head+Vector((dx,dy,0))) for b in tails]
            pts.append(rmat@(tails[-1].tail+Vector((dx*1.3,dy,.02))))
            attach_bone(tube('horse tail fullness292',pts,.004,hair),tails[0].name)
    # Saddle/pad follow the supported body pivot (unchanged spine in this shot).
    pivot=bpy.data.objects['HORSE hind support pivot'];offset=pivot.location.copy()
    pad=surface('292 woven indigo saddle pad',[(.018,.029,.07),(.10,.15,.25)],20,bump=.002)
    leather=surface('292 worn saddle leather',[(.04,.022,.012),(.16,.085,.035)],15,bump=.003)
    vs=[];fs=[]
    for j in range(9):
        y=-.32+j*.08
        for i in range(13):
            x=-.38+i*.76/12;z=1.51-.36*(abs(x)/.38)**2;vs.append(tuple(Vector((x,y,z))-offset))
        if j:
            for i in range(12):q=j*13+i;fs.append((q-13,q,q+1,q-12))
    ob=mesh('fitted saddle blanket292',vs,fs,pad);ob.parent=pivot
    for sign in (-1,1):
        ob=tube('saddle padded edge292',[Vector((sign*.22,y,1.43))-offset for y in np.linspace(-.30,.31,12)],.035,leather,pivot)
    girth=[]
    center=Vector((0,0,1.34));matrix=pivot.matrix_world
    for a in np.linspace(0,math.tau,97):
        radial=Vector((math.sin(a),0,math.cos(a)));start=matrix@(center+radial*.8-offset)
        direction=matrix.to_3x3()@(-radial)
        hit,point,normal,_=body.ray_cast(inv@start,inv.to_3x3()@direction)
        if hit:girth.append(matrix.inverted()@(body.matrix_world@(point+normal*.012)))
    if len(girth)<80:raise ValueError('Girth contact route incomplete')
    tube('saddle girth292',girth,.014,leather,pivot)
    # Small head-owned bridle and rein endpoints; animated reins are world-space.
    head=bones['DEF-head'];bitlocal=head.tail+Vector((0,-.06,-.045))
    for sign in (-1,1):
        pts=[rmat@(head.head+Vector((sign*.07,.02,.035))),rmat@(head.tail+Vector((sign*.075,-.03,-.005))),rmat@(bitlocal+Vector((sign*.07,0,0)))]
        attach_bone(tube('horse cheek strap292',pts,.009,leather),'DEF-head')
    attach_bone(tube('horse nose band292',[rmat@(head.tail+Vector((x,-.035,.018-.025*abs(x)/.08))) for x in np.linspace(-.08,.08,17)],.009,leather),'DEF-head')
    bit=empty('292 bit support');bit.location=rmat@bitlocal;attach_bone(bit,'DEF-head')
    palm=bpy.data.objects['leader palm']
    reins=[tube('leader supported rein292',[(0,0,0)]*9,.006,leather) for _ in (-1,1)]
    for f in range(1,FRAMES+1):
        s.frame_set(f);bpy.context.view_layer.update()
        for sign,ob in zip((-1,1),reins):
            a=bit.matrix_world.translation+rig.matrix_world.to_3x3()@Vector((sign*.07,0,0));b=palm.matrix_world.translation
            if (a-b).length>2:raise ValueError('Rein support transform escaped the horse/rider assembly')
            for j,p in enumerate(ob.data.splines[0].points):
                u=j/8;v=a.lerp(b,u)+Vector((0,0,-.09*math.sin(math.pi*u)));p.co=(*v,1);p.keyframe_insert('co',frame=f)

def contact_fx():
    s=bpy.context.scene;rng=np.random.default_rng(292);records=[]
    rear=bpy.data.objects['BIKE rear rolling owner']
    for f in range(1,FRAMES+1):
        s.frame_set(f);bpy.context.view_layer.update();p=rear.matrix_world.translation.copy();p.z=.015
        records.append({'frame':f,'source_t':(f-1)/FPS*RATE,'rear_contact':list(p),'slip':slip((f-1)/FPS*RATE)})
    soil=surface('292 fresh scuffed earth',[(.035,.028,.018),(.10,.074,.038)],25,bump=.004)
    gravel=surface('292 thrown earth grains',[(.13,.10,.05),(.35,.27,.15)],7)
    # Growing immutable world-space track segments: no mark before tire contact.
    for i in range(1,len(records)):
        r=records[i];prev=records[i-1]
        if not r['slip']:continue
        a=Vector(prev['rear_contact']);b=Vector(r['rear_contact']);d=b-a
        if d.length<.004:continue
        normal=Vector((-d.y,d.x,0)).normalized();w=.08+.018*math.sin(i*2.7)
        ob=mesh('fresh tire skid292',[a-normal*w,a+normal*w,b+normal*w,b-normal*w],[(0,1,2,3)],soil)
        ob.hide_render=True;ob.keyframe_insert('hide_render',frame=max(1,r['frame']-1));ob.hide_render=False;ob.keyframe_insert('hide_render',frame=r['frame'])
    # Debris born only during actual slip intervals; gravity and ground arrest.
    births=[r for r in records if r['slip'] and r['frame']%2==0]
    for r in births:
        born=(r['frame']-1)/FPS;origin=r['rear_contact'];launch=r['source_t']>20
        for j in range(8):
            vel=(float(rng.uniform(-2.1,2.1)),float(rng.uniform(1.0,4.5 if launch else 2.8)),float(rng.uniform(.55,2.3)))
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=float(rng.uniform(.009,.026)));ob=bpy.context.object;ob.name='contact-born earth chip292';ob.data.materials.append(gravel)
            ob.hide_render=True;ob.keyframe_insert('hide_render',frame=max(1,r['frame']-1));ob.hide_render=False;ob.keyframe_insert('hide_render',frame=r['frame'])
            end=min(FRAMES,r['frame']+36)
            for f in range(r['frame'],end+1,2):
                age=(f-r['frame'])/FPS;ob.location=debris_position(origin,vel,age);ob.rotation_euler=(age*9,age*13+j,age*7);key(ob,f)
            ob.hide_render=True;ob.keyframe_insert('hide_render',frame=end+1)
    # Independent persistent contact puffs. No animated global density clears them early.
    mat=bpy.data.materials['staging dust volume'].copy();mat.name='292 contact dust independent'
    mat.node_tree.animation_data_clear();mat.node_tree.nodes['stop clearance'].outputs[0].default_value=1.3
    for i,r in enumerate(births[::2]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);ob=bpy.context.object;ob.name='wheel-ground slip plume292';ob.data.materials.append(mat)
        birth=r['frame'];p=Vector(r['rear_contact']);drift=Vector((float(rng.uniform(-.4,.4)),.4,.35))
        ob.scale=(.001,.001,.001);key(ob,max(1,birth-1))
        for f in range(birth,min(FRAMES,birth+73)+1,3):
            age=(f-birth)/FPS;size=(.13+age*.64)*(1-base.ease((age-1.8)/1.2));ob.location=p+drift*age
            ob.scale=(max(.001,size*1.5),max(.001,size),max(.001,size*.5));key(ob,f)
        ob.hide_render=True;ob.keyframe_insert('hide_render',frame=min(FRAMES+1,birth+74))
        ob.hide_render=False;ob.keyframe_insert('hide_render',frame=birth)
    return records

def build(out):
    base.travel=travel;base.bike_position=bike_position;base.wheel_angle=wheel_angle
    base.lighting=lighting;base.landscape=environment;base.people=people;base.leader=leader;base.camera_pose=camera
    s,cam=base.build(out);s.frame_set(1);add_groom();records=contact_fx()
    # More samples/pixels for the new fidelity preview, not a final profile claim.
    s.render.resolution_x=576;s.render.resolution_y=1024
    s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
    (out/'contact-fx.json').write_text(json.dumps(records,indent=2))
    return s,cam

def controls(out):
    s,cam=build(out)
    for t in (0,1.8,4.8,6.3,6.8,7.5,8.6,11.8,14.6,15.5,16.6,18.5,21.45,21.8,22.3,24.5):
        s.frame_set(1+round(t/RATE*FPS));s.render.filepath=str(out/f'beat-{t:05.2f}.png');bpy.ops.render.render(write_still=True)
    cam.animation_data_clear();cam.data.animation_data_clear();cam.data.type='ORTHO';cam.data.ortho_scale=20
    s.frame_set(round(8/RATE*FPS)+1);camera_at(cam,(0,-10,28),(0,-10,0));s.render.filepath=str(out/'stop-clearance-top.png');bpy.ops.render.render(write_still=True)

def movie(out):
    s,cam=build(out);(out/'frames').mkdir();s.render.filepath=str(out/'frames/frame-');bpy.ops.render.render(animation=True)

def reopen(out):
    source=BASE/'movie-01/sequence.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);s=bpy.context.scene
    trace=[]
    for f in range(1,FRAMES+1):
        s.frame_set(f);bpy.context.view_layer.update();t=(f-1)/FPS*RATE
        front=bpy.data.objects['BIKE front rolling owner'];rear=bpy.data.objects['BIKE rear rolling owner']
        tip=bpy.data.objects['LEADER spear world contact owner'].matrix_world.translation
        bank=bpy.data.objects['low field bank for leader'];hit,point,normal,index=bank.ray_cast(tip+Vector((0,0,1)),Vector((0,0,-1)))
        if not hit:raise ValueError('Spear missed bank')
        bit=bpy.data.objects['292 bit support'].matrix_world.translation;palm=bpy.data.objects['leader palm'].matrix_world.translation
        crowd_front=max(o.matrix_world.translation.y+.16 for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR '))
        trace.append({'frame':f,'source_t':t,'front_ground_gap':front.matrix_world.translation.z-front['rolling_radius'],
            'rear_ground_gap':rear.matrix_world.translation.z-rear['rolling_radius'],
            'spear_actual_ground_gap':tip.z-point.z,'rein_length':(bit-palm).length,
            'crowd_longitudinal_clearance':front.matrix_world.translation.y-front['rolling_radius']-crowd_front})
    (out/'contact-trace.json').write_text(json.dumps(trace,indent=2))
    for f in (1,99,150,245,315,445):
        s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
    (out/'reopen.json').write_text(json.dumps({'frames':[1,99,150,245,315,445],'fps':s.render.fps,'frame_end':s.frame_end,'source':str(source)}))
