"""Reviewed reversible action and look correction; separate physical owners."""
import math,json
import bpy
from mathutils import Vector,Quaternion
from sikh257_layout import key,segment
from movie_factory.sikh257_geometry import joint_between
from movie_factory import sikh304_motion as c
from movie_factory.sikh291_motion import rear_amount,pulse,greeting,uncover_amount

def motorcycle(out):
    import sikh299_scene as prior
    import sikh291_scene as actor_module
    original=actor_module.actor_pose
    def balanced(a,root,steer,t,f):
        original(a,root,steer,t,f)
        torso=a['torso'];r=c.lean(t)
        torso.rotation_euler.y=-r*.90
        torso.location.x=-r*.22
        # Controlled forward bracing under deceleration, a small forward
        # anticipation under power. Not an inert upright mannequin.
        torso.rotation_euler.x+=.035*c.bump(t,3.6,4.0,5.9,6.4)+.025*c.bump(t,6.7,6.9,7.1,7.55)
        key(torso,f);bpy.context.view_layer.update();transform=torso.matrix_local.copy()
        for side in (-1,1):
            shoulder=transform@Vector((side*.22,-.08,.46));palm=a['limbs'][side,'hand'];hand=palm.location.copy()
            greet=greeting(t)
            if greet>0:hand=hand.lerp(transform@Vector((side*.024,-.30,.39)),greet)
            elbow=joint_between(shoulder,hand,.32,.31,(side*.7,.25,-.6))
            segment(a['limbs'][side,'upper arm'],shoulder,elbow,.072);segment(a['limbs'][side,'forearm'],elbow,hand,.054);palm.location=hand
            for part in ('upper arm','forearm','hand'):key(a['limbs'][side,part],f)
        # Negative-X boot is the inside support for this authored roll;
        # opposite boot stays on its peg. No documentary control-layout claim.
        # Foot comes down only as the bike settles to rest.
        hold=pulse(t,7.05,.55,18.4,.5);side=-1
        foot=Vector((-.27,-.16,.37));world=root.matrix_world@Vector((-.43,.23,.065));world.z=c.ground_height(world.x,world.y)+.065
        foot=foot.lerp(root.matrix_world.inverted()@world,hold)
        knee=joint_between((-.13,.40,.85),foot,.46,.45,(-.3,-1,.05))
        segment(a['limbs'][side,'thigh'],(-.13,.40,.85),knee,.088);segment(a['limbs'][side,'shin'],knee,foot,.064);a['limbs'][side,'boot'].location=foot
        for part in ('thigh','shin','boot'):key(a['limbs'][side,part],f)
    actor_module.actor_pose=balanced
    for name in ('travel','yaw','lean','slip','rear_distance'):setattr(prior,name,getattr(c,name))
    for o in list(bpy.data.objects):
        if o.name.startswith(('299 tire-contact','299 ground-integrated','299 front tread','299 rear tread')):bpy.data.objects.remove(o,do_unlink=True)
    try:trace=prior.motion(out)
    finally:actor_module.actor_pose=original
    root=bpy.data.objects['BIKE travel owner'];s=bpy.context.scene;cam=s.camera
    tires={name:next(o for o in bpy.data.objects['BIKE '+name+' rolling owner'].children if o.type=='MESH' and 'charcoal tire' in o.name) for name in ('front','rear')}
    road=bpy.data.objects['irregular packed farm track'];actor=prior.actor_objects()
    dust=[o for o in bpy.data.objects if o.name.startswith('authored world-space dust ')]
    for row in trace:
        f=row['frame'];s.frame_set(f);t=(f-1)/c.FPS*c.RATE;dx=c.lateral(t);root.location.x+=dx;key(root,f)
        bpy.context.view_layer.update()
        # Measure again after lateral displacement. Earlier diagnostics were
        # captured before that displacement and were not final-contact proof.
        for name,ob in tires.items():
            p=min((ob.matrix_world@v.co for v in ob.data.vertices),key=lambda p:p.z)
            hit,g,_,_=road.ray_cast(Vector((p.x,p.y,1)),Vector((0,0,-1)))
            if not hit:raise ValueError('Final tread off contact surface')
            row[name+'_gap']=p.z-g.z;row[name+'_tread_contact']=list(p)
        row['rear']=list(bpy.data.objects['BIKE rear rolling owner'].matrix_world.translation)
        hold=pulse(t,7.05,.55,18.4,.5)
        foot=actor['limbs'][-1,'boot']
        if hold:
            world=foot.matrix_world.translation.copy();target=world.copy();target.z=c.ground_height(world.x,world.y)+.061
            foot.location=root.matrix_world.inverted()@world.lerp(target,hold)
            knee=joint_between((-.13,.40,.85),foot.location,.46,.45,(-.30,-1,.05))
            segment(actor['limbs'][-1,'thigh'],(-.13,.40,.85),knee,.088);segment(actor['limbs'][-1,'shin'],knee,foot.location,.064)
            for part in ('thigh','shin','boot'):key(actor['limbs'][-1,part],f)
        bpy.context.view_layer.update();bottom=min((foot.matrix_world@v.co for v in foot.data.vertices),key=lambda p:p.z)
        row['support_boot_gap']=bottom.z-c.ground_height(bottom.x,bottom.y);row['support_hold']=hold
        if t<7.5:
            # Translate the original tracking camera with the earlier braking
            # position. Preserve subject framing, cut/lens and crowd distance.
            cam.location.y+=c.travel(t)-c.old_travel(t);key(cam,f)
        elif t>=21.4:
            # Preserve shot/cut/lens, follow the corrected physical target.
            # Existing camera aim intersects the old rider's Y plane.
            forward=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));dy=c.travel(t)-c.old_travel(t)
            distance=(c.old_travel(t)-cam.location.y)/forward.y if abs(forward.y)>.001 else 4
            target=cam.location+forward*max(.1,distance)+Vector((dx,dy,0))
            from sikh257_native import camera_at
            camera_at(cam,cam.location.copy(),target);key(cam,f)
        for ob in dust:
            i=int(ob.name.rsplit(' ',1)[-1]);age=(t+i*3.9/18)%3.9;born=t-age
            ob.location.y+=c.travel(born)-c.old_travel(born);ob.location.x+=c.lateral(born);key(ob,f)
        row['lateral_slip']=dx;row['rider_counter_roll']=-c.lean(t)*.9
    prior.greeting_eyeline(out);prior.contact(out,trace)
    (out/'coordinated-motion.json').write_text(json.dumps(trace,indent=2))

def horse(out):
    s=bpy.context.scene;s.frame_set(1);rig=bpy.data.objects['horse.rig'];pivot=bpy.data.objects['HORSE hind support pivot'];rest=pivot.location.copy()
    fixed={n:(rig.matrix_world@rig.pose.bones[n].matrix).copy() for n in ('hind_foot_ik.L','hind_foot_ik.R')}
    rows=[]
    for f in range(1,c.FRAMES+1):
        s.frame_set(f);t=(f-1)/c.FPS*c.RATE;a=rear_amount(t)
        # Bring the body back over support and lower the hindquarters. Prior
        # rotation alone carried the pelvis behind the support polygon.
        pivot.location=rest+Vector((0,-.38*a,-.15*a));key(pivot,f)
        for side in ('L','R'):
            delay=.035 if side=='R' else 0;fold=rear_amount(t-delay)
            for name,angle in (('upper_arm_fk',-.62),('forearm_fk',2.05),('forefoot_fk',-.38),('f_toe_fk',.10)):
                pb=rig.pose.bones[name+'.'+side];axis=pb.bone.matrix_local.to_3x3().inverted()@Vector((1,0,0));pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion(axis,angle*fold);pb.keyframe_insert('rotation_quaternion',frame=f)
        # Existing neutral neck stays protected; small poll flex during effort.
        pb=rig.pose.bones.get('head')
        if pb:
            pb.rotation_mode='QUATERNION';axis=pb.bone.matrix_local.to_3x3().inverted()@Vector((1,0,0));pb.rotation_quaternion=Quaternion(axis,.07*a);pb.keyframe_insert('rotation_quaternion',frame=f)
        bpy.context.view_layer.update()
        for name,world in fixed.items():
            pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=rig.matrix_world.inverted()@world;pb.keyframe_insert('location',frame=f);pb.keyframe_insert('rotation_quaternion',frame=f)
        bpy.context.view_layer.update()
        if f in (1,295,310,325,340,355):rows.append({'frame':f,'pivot_offset':list(pivot.location-rest),'hips':list(rig.matrix_world@rig.pose.bones['hips'].head),'hind_support':{n:list(rig.matrix_world@rig.pose.bones[n].head) for n in fixed}})
    # Spear hand must remain connected after body translation; tip stays on
    # its original world contact, not dragged by the horse.
    spear=bpy.data.objects['LEADER spear world contact owner']
    riders=[o for o in pivot.children if o!=rig];rider=next(o for o in riders if any(ch.name.startswith('leader upper arm') for ch in o.children))
    palms=sorted([o for o in rider.children if o.name.startswith('leader palm')],key=lambda o:o.name)
    reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name)
    bit=bpy.data.objects['292 bit support']
    for f in range(1,c.FRAMES+1):
        s.frame_set(f);bpy.context.view_layer.update();grip=palms[-1].matrix_world.translation;spear.rotation_mode='QUATERNION';spear.rotation_quaternion=(grip-spear.location).to_track_quat('Z','Y');key(spear,f)
        for sign,ob in zip((-1,1),reins):
            a=bit.matrix_world.translation+rig.matrix_world.to_3x3()@Vector((sign*.07,0,0));b=palms[0].matrix_world.translation
            for j,p in enumerate(ob.data.splines[0].points):
                u=j/(len(ob.data.splines[0].points)-1);v=a.lerp(b,u)+Vector((0,0,-.08*math.sin(math.pi*u)));p.co=(*v,1);p.keyframe_insert('co',frame=f)
    (out/'horse-support.json').write_text(json.dumps(rows,indent=2))

def bike_finish():
    # Screen-scale wear, not another global layer of very fine noise.
    for mat in list(bpy.data.materials):
        if not mat.name.startswith('300 bike lived material'):continue
        n=mat.node_tree.nodes;l=mat.node_tree.links;b=n.get('Principled BSDF')
        if not b:continue
        old=b.inputs['Base Color'].links[0].from_socket if b.inputs['Base Color'].is_linked else None
        tc=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Generated'],sep.inputs[0])
        noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=22;noise.inputs['Detail'].default_value=2;l.new(tc.outputs['Object'],noise.inputs[0])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.43;ramp.color_ramp.elements[1].position=.64;ramp.color_ramp.elements[0].color=(.28,.28,.28,1);ramp.color_ramp.elements[1].color=(.78,.78,.78,1);l.new(noise.outputs['Fac'],ramp.inputs[0])
        low=n.new('ShaderNodeMapRange');low.inputs['From Min'].default_value=.15;low.inputs['From Max'].default_value=.85;low.inputs['To Min'].default_value=.48;low.inputs['To Max'].default_value=.045;l.new(sep.outputs['Z'],low.inputs[0])
        mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(low.outputs[0],mul.inputs[0]);l.new(ramp.outputs[0],mul.inputs[1])
        mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=b.inputs['Base Color'].default_value;mix.inputs[2].default_value=(.23,.175,.095,1)
        if old:l.new(old,mix.inputs[1])
        l.new(mul.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],b.inputs['Base Color'])
        if 'olive' in mat.name:
            vor=n.new('ShaderNodeTexVoronoi');vor.feature='DISTANCE_TO_EDGE';vor.inputs['Scale'].default_value=72;l.new(tc.outputs['Object'],vor.inputs[0])
            thin=n.new('ShaderNodeMath');thin.operation='LESS_THAN';thin.inputs[1].default_value=.018;l.new(vor.outputs['Distance'],thin.inputs[0]);chip=n.new('ShaderNodeMath');chip.operation='MULTIPLY';l.new(thin.outputs[0],chip.inputs[0]);l.new(mul.outputs[0],chip.inputs[1])
            worn=n.new('ShaderNodeMixRGB');worn.inputs[2].default_value=(.32,.28,.20,1);l.new(chip.outputs[0],worn.inputs[0]);l.new(mix.outputs[0],worn.inputs[1]);l.new(worn.outputs[0],b.inputs['Base Color'])
        if 'steel' in mat.name:b.inputs['Metallic'].default_value=.72

def build(out):
    # Hide expensive crop instances from dependency updates during per-frame
    # actor rebuilding. They remain enabled for the saved renderer.
    from sikh304_land import build as landscape
    from sikh304_finish import finish
    landscape();finish();bpy.context.view_layer.update()
    crops=[o for o in bpy.data.objects if o.name.startswith('304 cultivated parcel canopy')]
    for o in crops:o.hide_viewport=True
    motorcycle(out);horse(out);bike_finish()
    for o in crops:o.hide_viewport=False
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for k in fc.keyframe_points:k.interpolation='LINEAR'
    from sikh304_audit import camera_clearance
    camera_clearance(out)
    # The square ground patches in launch controls were shadow-map aliasing,
    # not extra terrain. Resolve the light sampling instead of repainting dirt.
    settings=[]
    for light in bpy.data.lights:
        if hasattr(light,'shadow_maximum_resolution'):
            light.shadow_maximum_resolution=.0005;light.shadow_filter_radius=2.0;light.use_shadow_jitter=False
            if hasattr(light,'use_absolute_resolution'):light.use_absolute_resolution=True
            settings.append({'name':light.name,'maximum_resolution':light.shadow_maximum_resolution,'filter':light.shadow_filter_radius,'jitter':light.use_shadow_jitter})
    bpy.context.scene.eevee.taa_render_samples=64
    (out/'shadow-settings.json').write_text(json.dumps(settings,indent=2))
