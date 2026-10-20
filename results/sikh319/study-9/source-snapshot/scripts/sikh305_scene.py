"""Integrated derivative. Native source304 stays immutable."""
import math,json
import bpy
import numpy as np
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
from sikh257_layout import key,segment
from movie_factory.sikh257_geometry import joint_between
from sikh257_native import camera_at
from movie_factory import sikh305_motion as c

def motorcycle(out):
    import sikh304_scene as previous
    import sikh299_scene as mechanics
    s=bpy.context.scene;cam=s.camera
    # Preserve inherited cover/reveal coverage exactly outside changed shots.
    saved={}
    for f in range(1,529):
        s.frame_set(f);saved[f]=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.lens)
    previous.c=c;mechanics.FRAMES=c.FRAMES
    contact_builder=mechanics.contact;mechanics.contact=lambda *args:None
    try:previous.motorcycle(out)
    finally:mechanics.contact=contact_builder
    trace=json.loads((out/'coordinated-motion.json').read_text());projection=[]
    root=bpy.data.objects['BIKE travel owner'];road=bpy.data.objects['irregular packed farm track']
    bvh=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    tires={name:next(o for o in bpy.data.objects['BIKE '+name+' rolling owner'].children if o.type=='MESH' and 'charcoal tire' in o.name) for name in ('front','rear')}
    verts={n:np.asarray([tuple(v.co) for v in o.data.vertices]) for n,o in tires.items()}
    def contact(name):
        m=np.asarray(tires[name].matrix_world);pts=verts[name]@m[:3,:3].T+m[:3,3];p=pts[np.argmin(pts[:,2])]
        hit=bvh.ray_cast(Vector((p[0],p[1],1)),Vector((0,0,-1)))[0]
        if hit is None:raise ValueError('305 tire escaped actual shared ground')
        return float(p[2]-hit.z),p.tolist()
    for row in trace:
        f=row['frame'];t=(f-1)/c.FPS*c.RATE;s.frame_set(f);y=c.travel(t)
        if 21.4<t<23:
            # The lateral breakaway changes ground height under the rear tire.
            # Re-solve both rendered treads after that displacement, before FX.
            front=bpy.data.objects['BIKE front rolling owner'];rear=bpy.data.objects['BIKE rear rolling owner'];steer=bpy.data.objects['BIKE steering owner']
            wheelbase=(steer.matrix_local@front.location).y-rear.location.y
            for _ in range(3):
                bpy.context.view_layer.update();fg,_=contact('front');rg,_=contact('rear')
                q=root.rotation_euler.to_quaternion()@Quaternion((1,0,0),-(fg-rg)/wheelbase)
                root.rotation_euler=q.to_euler();bpy.context.view_layer.update();fg,_=contact('front');root.location.z-=fg-.0008
            key(root,f);bpy.context.view_layer.update()
        for name in ('front','rear'):row[name+'_gap'],row[name+'_tread_contact']=contact(name)
        row['rear']=list(bpy.data.objects['BIKE rear rolling owner'].matrix_world.translation)
        if f<=528:
            cam.location,cam.rotation_euler,cam.data.lens=saved[f]
        if 4.4<=t<5.3:
            # Fixed actor-relative pose and aim throughout OTS. Looking at a
            # fixed distant point rotated the camera as it approached, causing
            # the apparent lunge even with translated camera position.
            camera_at(cam,(.28,y+2.3,1.95),(.12,y-14,1.45));cam.data.lens=32
        elif 5.3<=t<7.5:
            camera_at(cam,(4.3,-7.7,1.55),(-.1,y,1.05));cam.data.lens=42
        elif 13.5<=t<17.5:
            camera_at(cam,(1.0,-25.75,3.65),(7.5,-29,4.8));cam.data.lens=48
        elif 20.5<=t<23.0:
            # Low rear-quarter reveals the driven tire and lateral breakaway.
            # Subject-relative tracking eases into a static departure view.
            u=c.ease((t-22.0)/1.0)
            near=Vector((-2.15,y+3.3,.68));far=Vector((-2.7,-22,2.0))
            camera_at(cam,near.lerp(far,u),(0,y-.20,1.02));cam.data.lens=34
        elif t>=23:
            # Let him recede along the lane; no tracking camera cancelling his
            # departure and no freeze after the old528-frame animation.
            u=c.ease((t-23)/4.0);loc=Vector((-2.7,-22,2.0)).lerp(Vector((-1.5,-25,3.5)),u)
            target=Vector((0,y-.20,1.02)).lerp(Vector((0,-145,1.2)),u)
            camera_at(cam,loc,target);cam.data.lens=34+8*u
        key(cam,f);cam.data.keyframe_insert('lens',frame=f);bpy.context.view_layer.update()
        root=bpy.data.objects['BIKE travel owner'];p=world_to_camera_view(s,cam,root.matrix_world@Vector((0,0,1.25)))
        projection.append({'frame':f,'source_t':t,'subject_screen':list(p),'root':list(root.location),'camera':list(cam.location)})
    (out/'camera-relative.json').write_text(json.dumps(projection,indent=2))
    (out/'coordinated-motion.json').write_text(json.dumps(trace,indent=2))
    contact_builder(out,trace)
    return trace

def dust(trace):
    # Remove only inherited FX in this derivative. Keep tire marks/debris.
    for ob in list(bpy.data.objects):
        if ob.name.startswith(('authored world-space dust','299 tire-contact dust','305 world dust cloud')):bpy.data.objects.remove(ob,do_unlink=True)
    source_mat=bpy.data.materials.get('staging dust volume')
    if source_mat is None:
        # Reopened derivatives purge the unused staging material. Reuse the
        # already-qualified density graph; never multiply object alpha twice.
        mat=bpy.data.materials['305 expanding advected dust']
    else:
        mat=source_mat.copy();mat.name='305 expanding advected dust';mat.node_tree.animation_data_clear()
        n=mat.node_tree.nodes;l=mat.node_tree.links;gain=n['stop clearance'];gain.outputs[0].default_value=1
        info=n.new('ShaderNodeObjectInfo');vol=next(x for x in n if x.bl_idname=='ShaderNodeVolumePrincipled')
        source=vol.inputs['Density'].links[0].from_socket;mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(source,mul.inputs[0]);l.new(info.outputs['Alpha'],mul.inputs[1]);l.new(mul.outputs[0],vol.inputs['Density']);vol.inputs['Emission Strength'].default_value=0
        for link in list(vol.inputs['Emission Strength'].links):l.remove(link)
        vol.inputs['Color'].default_value=(.40,.33,.22,1)
    rng=np.random.default_rng(305);births=[]
    for row in trace:
        t=row['source_t'];f=row['frame']
        if f%6==1 and (t<7.45 or t>18.5):births.append((f,Vector(row['rear_tread_contact']),1.5 if row['slip'] else .65))
    # Established opening trail, not a magically clean first frame.
    for f in range(-47,1,6):
        t=(f-1)/24*c.RATE;births.append((f,Vector((0,c.travel(t)+.7,.03)),.65))
    for index,(birth,p,intensity) in enumerate(births):
        launch=21.35<=(birth-1)/24*c.RATE<=22.6
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);ob=bpy.context.object;ob.name='305 world dust cloud';ob.data.materials.append(mat)
        drift=Vector((float(rng.uniform(.12,.42)),float(rng.uniform(.12,.55)),float(rng.uniform(.18,.34))))
        life=5.8;end=min(c.FRAMES,birth+math.ceil(life*24));ob.color=(1,1,1,0)
        ob.hide_render=True;ob.keyframe_insert('hide_render',frame=max(0,birth-1));ob.hide_render=False;ob.keyframe_insert('hide_render',frame=max(1,birth))
        frames=sorted(set([max(1,birth),end]+list(range(max(1,birth),end+1,3))))
        for f in frames:
            age=(f-birth)/24;size,den=c.dust_state(age,life)
            if launch:size*=1.65;den*=2.4
            ob.location=p+drift*age+Vector((0,0,.12 if launch else 0))
            ob.scale=(size*1.2,size,size*.62);ob.color=(1,1,1,den*intensity);key(ob,f);ob.keyframe_insert('color',frame=f)
        if birth+life*24<=c.FRAMES:
            ob.color=(1,1,1,0);ob.keyframe_insert('color',frame=end);ob.hide_render=True;ob.keyframe_insert('hide_render',frame=end+1)

def bone_x(rig,name,angle,f):
    pb=rig.pose.bones.get(name)
    if pb is None:return
    pb.rotation_mode='QUATERNION';axis=pb.bone.matrix_local.to_3x3().inverted()@Vector((1,0,0));pb.rotation_quaternion=Quaternion(axis,angle);pb.keyframe_insert('rotation_quaternion',frame=f)

def horse(out,rebuild_groom=True):
    s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rig=bpy.data.objects['horse.rig'];pivot=bpy.data.objects['HORSE hind support pivot'];rest=pivot.location.copy()
    fixed={n:(rig.matrix_world@rig.pose.bones[n].matrix).copy() for n in ('hind_foot_ik.L','hind_foot_ik.R')}
    fore_names=('DEF-f_toe.L','DEF-f_toe.R')
    fore_target=min((rig.matrix_world@rig.pose.bones[n].tail).z for n in fore_names)
    rider=next(o for o in pivot.children if o!=rig and any(ch.name.startswith('leader upper arm') for ch in o.children))
    rows=[];grips=[];palms=sorted([o for o in rider.children if o.name.startswith('leader palm')],key=lambda o:o.name);spear=bpy.data.objects['LEADER spear world contact owner'];base_tip=spear.location.copy()
    upper=bpy.data.objects['leader upper arm.001'];lower=bpy.data.objects['leader forearm.001'];sleeve_samples=[]
    from sikh297_layers import sleeve_points
    reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name);bit=bpy.data.objects['292 bit support']
    # Bone-parented groom follows new neck/head. Add delayed tip response in
    # its existing local coordinates, with roots exactly unchanged.
    hair=[]
    for ob in bpy.data.objects:
        if rebuild_groom and ob.type=='CURVE' and ob.name.startswith(('rooted mane locks292','horse tail fullness292')):
            points=ob.data.splines[0].points
            if points:hair.append((ob,[p.co.copy() for p in points]))
    for f in range(1,c.FRAMES+1):
        s.frame_set(f);t=(f-1)/24*c.RATE;a=c.rear(t);g=c.gather(t);land=c.landing(t)
        # Crouch over the hind support while maintaining front-hoof height.
        # The earlier positive preload pitch drove those hooves underground.
        pivot.rotation_euler.x=-.88*a-.075*g-.05*land
        pivot.location=rest+Vector((0,-.28*a,-.13*g-.12*a-.09*land));key(pivot,f)
        # Rider balances forward over the rising saddle, rather than leaning
        # backwards with the animal. His hips still travel with the saddle.
        rider.rotation_euler.x=1.00*a+.10*g+.07*land;key(rider,f)
        for side in ('L','R'):
            fold=c.rear(t-(.035 if side=='R' else 0));asym=.06 if side=='R' else 0;grip=c.fore_grip(t,side)
            for name,angle in (('upper_arm_fk',-.14),('forearm_fk',-1.10+asym),('forefoot_fk',1.70),('f_toe_fk',.12)):
                prep={'upper_arm_fk':-.12,'forearm_fk':-.34,'forefoot_fk':.42,'f_toe_fk':.04}[name]
                bone_x(rig,name+'.'+side,angle*fold+prep*grip,f)
        # Independent neck extension/poll flex: effort leads rise and head
        # follows the landing with a small damped recovery, not rigid transport.
        settle=.06*math.sin(max(0,t-16.05)*11)*math.exp(-max(0,t-16.05)*4) if t>16.05 else 0
        bone_x(rig,'neck',.39*a+.52*g+.08*land+.012*math.sin(t*1.7),f)
        bone_x(rig,'head',.49*c.rear(t-.065)+.55*g+.10*land+settle+.014*math.sin(t*2.1+.7),f)
        bone_x(rig,'jaw',.085*c.bump(t,14.86,15.08,15.56,15.94),f)
        bpy.context.view_layer.update()
        if a<1e-6 and c.rear(t-.035)<1e-6 and (g>0 or land>0 or c.fore_grip(t,'L')>0 or c.fore_grip(t,'R')>0):
            # Solve the supported fore-toe height instead of guessing another
            # crouch offset. The protected plateau is flat under these feet.
            # Mesh silhouettes remain a separate visible-contact check.
            for _ in range(3):
                z=min((rig.matrix_world@rig.pose.bones[n].tail).z for n in fore_names)
                angle=pivot.rotation_euler.x;pivot.rotation_euler.x=angle+.001;bpy.context.view_layer.update()
                z1=min((rig.matrix_world@rig.pose.bones[n].tail).z for n in fore_names)
                derivative=(z1-z)/.001
                if abs(derivative)<.3:raise ValueError('Fore support solve is singular')
                pivot.rotation_euler.x=max(-.18,min(.18,angle-(z-fore_target)/derivative));bpy.context.view_layer.update()
            key(pivot,f)
        for name,world in fixed.items():
            pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=rig.matrix_world.inverted()@world;pb.keyframe_insert('location',frame=f);pb.keyframe_insert('rotation_quaternion',frame=f)
        bpy.context.view_layer.update()
        # Reauthor the actual hand and both connected sleeve segments, not
        # only the pole. The downstroke now cues the horse's preparation.
        lift=c.spear_lift(t);hand=Vector((.35,-.03,.50+.24*lift/.42));shoulder=Vector((.20,0,.42))
        elbow=Vector(joint_between(shoulder,hand,.28,.27,(1,0,-1)));segment(upper,shoulder,elbow,.06);segment(lower,elbow,hand,.045);palms[-1].location=hand
        for ob in (upper,lower,palms[-1]):key(ob,f)
        if f%2==1 or f==c.FRAMES:sleeve_samples.append((f,sleeve_points(shoulder,elbow,hand,(.075,.062,.042))))
        bpy.context.view_layer.update()
        spear.rotation_mode='QUATERNION';spear.rotation_quaternion=(palms[-1].matrix_world.translation-spear.location).to_track_quat('Z','Y');key(spear,f)
        grips.append(palms[-1].matrix_world.translation.copy())
        for sign,ob in zip((-1,1),reins):
            start=bit.matrix_world.translation+rig.matrix_world.to_3x3()@Vector((sign*.07,0,0));end=palms[0].matrix_world.translation
            for j,p in enumerate(ob.data.splines[0].points):
                u=j/(len(ob.data.splines[0].points)-1);q=start.lerp(end,u)+Vector((0,0,-.08*math.sin(math.pi*u)));p.co=(*q,1);p.keyframe_insert('co',frame=f)
        if f%2==1 or f==c.FRAMES:
            lag=c.rear(t-.10)-a
            for index,(ob,base) in enumerate(hair):
                for j,(p,q) in enumerate(zip(ob.data.splines[0].points,base)):
                    u=j/max(1,len(base)-1);v=q.copy();v.x+=u*u*(.08*lag+.008*math.sin(t*3.2+index*.7));v.y+=u*u*.04*lag;p.co=v;p.keyframe_insert('co',frame=f)
        if 13.8<t<17.2:
            rows.append({'frame':f,'source_t':t,'body_pitch':pivot.rotation_euler.x,'head':list(rig.matrix_world@rig.pose.bones['head'].head),'hips':list(rig.matrix_world@rig.pose.bones['hips'].head),'hind_feet':{n:list(rig.matrix_world@rig.pose.bones[n].head) for n in fixed}})
    # Replant below the hand at the apex, not at the former smaller-rear tip.
    # Move the tip only while lifted; hold its new world position after strike.
    stamp=grips[round(14.28/c.RATE*24)];stamp=Vector((stamp.x,stamp.y,base_tip.z))
    for f,grip in enumerate(grips,1):
        t=(f-1)/24*c.RATE;spear.location=base_tip.lerp(stamp,c.ease((t-13.88)/.28))+Vector((0,0,c.spear_lift(t)))
        spear.rotation_quaternion=(grip-spear.location).to_track_quat('Z','Y');key(spear,f)
    (out/'whole-horse-motion.json').write_text(json.dumps(rows,indent=2))
    sleeve=bpy.data.objects['297 continuous leader sleeve.001'];sleeve.shape_key_clear();sleeve.shape_key_add(name='Basis')
    for f,pts in sleeve_samples:
        sk=sleeve.shape_key_add(name=f'cue{f:04d}')
        for p,q in zip(sk.data,pts):p.co=q
        for ff,val in ((max(0,f-2),0),(f,1),(f+2,0)):sk.value=val;sk.keyframe_insert('value',frame=ff)
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for p in fc.keyframe_points:p.interpolation='CONSTANT' if fc.data_path=='hide_render' else 'LINEAR'
    mat=bpy.data.materials['297 silver dapple coat'];n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF'];b.inputs['Roughness'].default_value=.48
    tc=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(65,9,95);l.new(tc.outputs['Generated'],scale.inputs[0])
    fiber=n.new('ShaderNodeTexNoise');fiber.inputs['Scale'].default_value=4;fiber.inputs['Detail'].default_value=2;l.new(scale.outputs[0],fiber.inputs[0]);normal=n.new('ShaderNodeBump');normal.inputs['Strength'].default_value=.22;normal.inputs['Distance'].default_value=.0007;l.new(fiber.outputs['Fac'],normal.inputs['Height']);l.new(normal.outputs[0],b.inputs['Normal'])

def torch():
    s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();center=Vector((8.6,-27.4,0));raised=[]
    for ob in list(s.objects):
        if not any(x in ob.name.lower() for x in ('torch','flame','basket','fire')):continue
        pts=[ob.matrix_world@Vector(p) for p in ob.bound_box] if ob.type in ('MESH','CURVE') else [ob.matrix_world.translation]
        q=sum(pts,Vector())/len(pts)
        if math.hypot(q.x-center.x,q.y-center.y)>1.0:continue
        if 'planted pole' in ob.name:
            # Extend from existing ground anchor, rather than floating pole.
            low=min(p.z for p in pts);high=max(p.z for p in pts)
            if ob.type=='MESH':
                inv=ob.matrix_world.inverted()
                for v in ob.data.vertices:
                    p=ob.matrix_world@v.co;p.z+=3.0*(p.z-low)/max(.01,high-low);v.co=inv@p
        else:
            ob.location.z+=3.0
            if ob.animation_data and ob.animation_data.action:
                for layer in ob.animation_data.action.layers:
                    for strip in layer.strips:
                        for bag in strip.channelbags:
                            for fc in bag.fcurves:
                                if fc.data_path=='location' and fc.array_index==2:
                                    for p in fc.keyframe_points:p.co.y+=3;p.handle_left.y+=3;p.handle_right.y+=3
            if ob.type=='LIGHT' and ob.data.type=='AREA':ob.rotation_euler=(Vector((7.5,-29,5))-ob.location).to_track_quat('-Z','Y').to_euler();ob.data.energy=200
        raised.append(ob.name)
    return raised

def build(out):
    from sikh305_land import build as landscape
    landscape();print('305 terrain and wind built',flush=True)
    crops=[o for o in bpy.data.objects if o.name.startswith(('304 cultivated','305 departure parcel','304 boundary tree'))]
    for o in crops:o.hide_viewport=True
    trace=motorcycle(out);print('305 coupled motorcycle/camera complete',flush=True)
    horse(out);print('305 whole horse complete',flush=True)
    dust(trace);raised=torch()
    for o in crops:o.hide_viewport=False
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for p in fc.keyframe_points:p.interpolation='CONSTANT' if fc.data_path=='hide_render' else 'LINEAR'
    bpy.context.scene.frame_end=c.FRAMES
    (out/'construction.json').write_text(json.dumps({'frames':c.FRAMES,'fps':24,'duration':c.FRAMES/24,'torch_components_raised':raised,'stop_preserved':math.isclose(c.travel(10),-3.6),'review':'NOT_RUN'},indent=2))
