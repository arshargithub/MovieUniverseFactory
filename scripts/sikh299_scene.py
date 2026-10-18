"""Fixed reviewed299 derivative. Native sources never overwritten."""
import math,json
import bpy
import numpy as np
from mathutils import Vector,Matrix,Quaternion
from sikh257_native import ROOT,mesh,material,camera_at
from sikh257_layout import key,segment
from movie_factory.sikh257_geometry import joint_between
from movie_factory.sikh299_motion import travel,yaw,lean,slip,rear_distance,FPS,FRAMES,RATE
from movie_factory.sikh291_motion import pulse,ease
from movie_factory.sikh297_contract import TORCHES
import sikh291_scene as old
import sikh292_scene as oldfx

def actor_objects():
    limbs={}
    for side,suffix in ((-1,''),(1,'.001')):
        for part in ('upper arm','forearm','thigh','shin','boot'):
            limbs[side,part]=bpy.data.objects['PROXY '+part+suffix]
        limbs[side,'hand']=bpy.data.objects['PROXY palm'+suffix]
    cover=bpy.data.objects['PROXY connected face end']
    return dict(torso=bpy.data.objects['RIDER torso performance'],head=bpy.data.objects['RIDER head performance'],cover=cover,
                uncover=cover.data.shape_keys.key_blocks['pulled clear and hanging'],limbs=limbs)

def greeting_eyeline(out):
    """Preserve leader attention after changing the settled vehicle heading.

    Existing bow pitch/timing remain. The uncover reach follows the changed
    head frame; prayer hands remain torso-owned. This is proxy coordination,
    not final facial performance or cloth qualification.
    """
    s=bpy.context.scene;a=actor_objects();root=bpy.data.objects['BIKE travel owner'];rows=[]
    leader=Vector((7.5,-29,4.8))
    from movie_factory.sikh291_motion import greeting,uncover_amount
    for f in range(1,FRAMES+1):
        s.frame_set(f);t=(f-1)/FPS*RATE;hold=pulse(t,7.35,.45,18.4,.5)
        if not hold:continue
        head=a['head'];torso=a['torso'];bpy.context.view_layer.update()
        before=head.matrix_local.copy();old_world=head.matrix_world.copy()
        direction=torso.matrix_world.inverted().to_3x3()@(leader-head.matrix_world.translation)
        target=math.atan2(direction.x,-direction.y)
        head.rotation_euler.z=(1-hold)*head.rotation_euler.z+hold*target
        key(head,f);bpy.context.view_layer.update()
        delta=head.matrix_local@before.inverted();transform=torso.matrix_local.copy()
        reach=ease((t-9)/.7)*(1-ease((t-17.3)/.6));greet=greeting(t)
        if reach*(1-greet)>0:
            u=uncover_amount(t);original=Vector((-.115,-.08-.12*math.sin(u*math.pi),.655-.35*u))
            correction=transform.to_3x3()@(delta@original-original)
            palm=a['limbs'][1,'hand'];hand=palm.location+correction*reach*(1-greet)
            shoulder=transform@Vector((.22,-.08,.46));elbow=joint_between(shoulder,hand,.32,.31,(.7,.25,-.6))
            segment(a['limbs'][1,'upper arm'],shoulder,elbow,.072);segment(a['limbs'][1,'forearm'],elbow,hand,.054);palm.location=hand
            for part in ('upper arm','forearm','hand'):key(a['limbs'][1,part],f)
        forward=head.matrix_world.to_3x3()@Vector((0,-1,0));old_forward=old_world.to_3x3()@Vector((0,-1,0));d=leader-head.matrix_world.translation
        target_world=math.atan2(d.x,-d.y)
        rows.append({'frame':f,'hold':hold,'before_error_deg':math.degrees(math.atan2(old_forward.x,-old_forward.y)-target_world),'after_error_deg':math.degrees(math.atan2(forward.x,-forward.y)-target_world),'local_head_yaw_deg':math.degrees(head.rotation_euler.z)})
    (out/'greeting-eyeline.json').write_text(json.dumps(rows,indent=2))

def motion(out):
    s=bpy.context.scene;root=bpy.data.objects['BIKE travel owner'];steer=bpy.data.objects['BIKE steering owner']
    front=bpy.data.objects['BIKE front rolling owner'];rear=bpy.data.objects['BIKE rear rolling owner'];actor=actor_objects();trace=[]
    axis=(-front.location).normalized();first_front_y=None
    road=bpy.data.objects['irregular packed farm track']
    tires={owner:next(o for o in owner.children if o.type=='MESH' and 'charcoal tire' in o.name) for owner in (front,rear)}
    tire_points={owner:np.asarray([tuple(v.co) for v in ob.data.vertices]) for owner,ob in tires.items()}
    def contact_point(owner):
        ob=tires[owner];m=np.asarray(ob.matrix_world);pts=tire_points[owner]@m[:3,:3].T+m[:3,3]
        p=pts[np.argmin(pts[:,2])];hit,ground,_,_=road.ray_cast(Vector((p[0],p[1],1)),Vector((0,0,-1)))
        if not hit:raise ValueError('Tire escaped road')
        return float(p[2]-ground.z),p.tolist()
    for f in range(1,FRAMES+1):
        s.frame_set(f);t=(f-1)/FPS*RATE;angle=yaw(t);roll=lean(t)
        steer.rotation_quaternion=Quaternion(axis,-max(-.34,min(.34,angle*.6)));key(steer,f);bpy.context.view_layer.update()
        fp=steer.matrix_local@front.location;rp=rear.location
        # Axle heights have unequal radii: compensate pitch before root elevation.
        pitch=0.
        for _ in range(4):
            rot=Matrix.Rotation(angle,3,'Z')@Matrix.Rotation(roll,3,'Y')@Matrix.Rotation(pitch,3,'X')
            a=rot@fp;b=rot@rp
            delta=(a.z-front['rolling_radius']*math.cos(roll))-(b.z-rear['rolling_radius']*math.cos(roll))
            pitch-=delta/(fp.y-rp.y)
        a=rot@fp;b=rot@rp
        root.rotation_euler=rot.to_euler();root.location=(-a.x,travel(t),front['rolling_radius']*math.cos(roll)-a.z)
        key(root,f);bpy.context.view_layer.update()
        fy=front.matrix_world.translation.y
        if first_front_y is None:first_front_y=fy
        front.rotation_euler.x=(fy-first_front_y)/front['rolling_radius']
        rear.rotation_euler.x=rear_distance(t)/rear['rolling_radius'];key(front,f);key(rear,f)
        # The rendered tire has width and tread. Axle/radius alone is insufficient
        # at lean: solve the actual mesh extrema against the actual uneven road.
        for _ in range(3):
            bpy.context.view_layer.update();fg,_=contact_point(front);rg,_=contact_point(rear)
            pitch-=(fg-rg)/(fp.y-rp.y)
            rot=Matrix.Rotation(angle,3,'Z')@Matrix.Rotation(roll,3,'Y')@Matrix.Rotation(pitch,3,'X')
            root.rotation_euler=rot.to_euler();bpy.context.view_layer.update();fg,_=contact_point(front)
            root.location.z-=fg-.0008
        key(root,f);bpy.context.view_layer.update();fg,fc=contact_point(front);rg,rc=contact_point(rear)
        old.actor_pose(actor,root,steer,t,f)
        # Foot ground ownership during rest is solved after root yaw/lean.
        hold=pulse(t,7.35,.45,18.4,.5)
        if hold:
            foot=actor['limbs'][-1,'boot'];world=root.matrix_world@foot.location
            world.z=.065;target=root.matrix_world.inverted()@world
            foot.location=foot.location.lerp(target,hold)
            hip=Vector((-.13,.40,.85));knee=joint_between(hip,foot.location,.46,.45,(-.30,-1,.05))
            segment(actor['limbs'][-1,'thigh'],hip,knee,.088);segment(actor['limbs'][-1,'shin'],knee,foot.location,.064)
            for part in ('thigh','shin','boot'):key(actor['limbs'][-1,part],f)
        bpy.context.view_layer.update()
        trace.append({'frame':f,'source_t':t,'yaw_deg':math.degrees(angle),'lean_deg':math.degrees(roll),'travel':travel(t),
                      'rear_spin':rear.rotation_euler.x,'front_gap':fg,'rear_gap':rg,'front_tread_contact':fc,'rear_tread_contact':rc,
                      'rear':list(rear.matrix_world.translation),'slip':slip(t)})
    (out/'motion-trace.json').write_text(json.dumps(trace,indent=2))
    return trace

def contact(out,trace):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(('fresh tire skid292','contact-born earth chip292','wheel-ground slip plume292')):bpy.data.objects.remove(ob,do_unlink=True)
    records=[{'frame':r['frame'],'source_t':r['source_t'],'rear_contact':r['rear_tread_contact'],'slip':r['slip']} for r in trace]
    rng=np.random.default_rng(299);births=[r for r in records if r['slip'] and r['frame']%2==0]
    gravel=bpy.data.materials['292 thrown earth grains']
    for r in births:
        for j in range(8):
            velocity=(float(rng.uniform(-2.1,2.1)),float(rng.uniform(1,4.5 if r['source_t']>20 else 2.8)),float(rng.uniform(.55,2.3)))
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=float(rng.uniform(.009,.026)));ob=bpy.context.object;ob.name='299 tire-contact earth chip';ob.data.materials.append(gravel)
            ob.hide_render=True;ob.keyframe_insert('hide_render',frame=max(1,r['frame']-1));ob.hide_render=False;ob.keyframe_insert('hide_render',frame=r['frame'])
            end=min(FRAMES,r['frame']+36)
            for f in range(r['frame'],end+1,2):
                age=(f-r['frame'])/FPS;ob.location=oldfx.debris_position(r['rear_contact'],velocity,age);ob.rotation_euler=(age*9,age*13+j,age*7);key(ob,f)
            ob.hide_render=True;ob.keyframe_insert('hide_render',frame=end+1)
    volume=bpy.data.materials['staging dust volume'].copy();volume.name='299 contact dust';volume.node_tree.animation_data_clear();volume.node_tree.nodes['stop clearance'].outputs[0].default_value=1.3
    for r in births[::2]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);ob=bpy.context.object;ob.name='299 tire-contact dust';ob.data.materials.append(volume)
        birth=r['frame'];p=Vector(r['rear_contact']);drift=Vector((float(rng.uniform(-.4,.4)),.4,.35));ob.scale=(.001,)*3;key(ob,max(1,birth-1))
        for f in range(birth,min(FRAMES,birth+73)+1,3):
            age=(f-birth)/FPS;size=(.13+age*.64)*(1-ease((age-1.8)/1.2));ob.location=p+drift*age;ob.scale=(max(.001,size*1.5),max(.001,size),max(.001,size*.5));key(ob,f)
        ob.hide_render=True;ob.keyframe_insert('hide_render',frame=min(FRAMES+1,birth+74));ob.hide_render=False;ob.keyframe_insert('hide_render',frame=birth)
    mat=bpy.data.objects['irregular packed farm track'].data.materials[0].copy();mat.name='299 scuffed earth blended into lane'
    n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF'];bs.inputs['Roughness'].default_value=.95
    original=bs.inputs['Base Color'].links[0].from_socket
    tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.42,.43,.43,1);l.new(original,tint.inputs[1]);l.new(tint.outputs[0],bs.inputs['Base Color'])
    attr=n.new('ShaderNodeVertexColor');attr.layer_name='edge opacity'
    transparent=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(attr.outputs['Color'],mix.inputs[0]);l.new(transparent.outputs[0],mix.inputs[1]);l.new(bs.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n['Material Output'].inputs['Surface'])
    mat.surface_render_method='DITHERED';mat.use_transparent_shadow=False;road=bpy.data.objects['irregular packed farm track'];rng=np.random.default_rng(299)
    for i,(a,b) in enumerate(zip(records,records[1:])):
        if not b['slip']:continue
        p=Vector(a['rear_contact']);q=Vector(b['rear_contact']);d=q-p
        if d.length<.004:continue
        normal=Vector((-d.y,d.x,0)).normalized();vs=[];fs=[];values=[]
        for row in range(3):
            u=row/2;center=p.lerp(q,u);width=.073+.012*math.sin(i*1.4+u)
            for k in range(7):
                cross=(k-3)/3;v=center+normal*cross*width;hit,point,_,_=road.ray_cast(Vector((v.x,v.y,1)),Vector((0,0,-1)))
                if not hit:raise ValueError('Skid contact outside actual road')
                v.z=point.z+.0007;vs.append(v);values.append((1-abs(cross))**.55*float(rng.uniform(.6,.95)))
            if row:
                for k in range(6):z=row*7+k;fs.append((z-7,z,z+1,z-6))
        ob=mesh('299 ground-integrated tire wear',vs,fs,mat);attr=ob.data.color_attributes.new(name='edge opacity',type='FLOAT_COLOR',domain='POINT')
        for item,value in zip(attr.data,values):item.color=(value,value,value,1)
        ob.hide_render=True;ob.keyframe_insert('hide_render',frame=max(1,b['frame']-1));ob.hide_render=False;ob.keyframe_insert('hide_render',frame=b['frame'])
    (out/'contact-records.json').write_text(json.dumps(records,indent=2))
    # Authored local occlusion: the broad practical lights lacked readable
    # contact despite independently measured tire/road coincidence. This is a
    # soft, ground-projected shadow accent, not a fake geometric-contact test.
    mat=bpy.data.materials.new('299 localized contact occlusion');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links
    color=n.new('ShaderNodeVertexColor');color.layer_name='contact weight';trans=n.new('ShaderNodeBsdfTransparent');dark=n.new('ShaderNodeEmission');dark.inputs[0].default_value=(.008,.006,.004,1);mix=n.new('ShaderNodeMixShader');l.new(color.outputs[0],mix.inputs[0]);l.new(trans.outputs[0],mix.inputs[1]);l.new(dark.outputs[0],mix.inputs[2]);outnode=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],outnode.inputs[0]);mat.surface_render_method='DITHERED';mat.use_transparent_shadow=False
    for which in ('front','rear'):
        vs=[];fs=[];weights=[]
        for j in range(6):
            r=j/5
            for k in range(32):
                a=k*math.tau/32;vs.append((.105*r*math.cos(a),.16*r*math.sin(a),0));weights.append(.76*(1-r)**1.5)
                if j:q=j*32+k;qq=j*32+(k+1)%32;fs.append((q-32,qq-32,qq,q))
        ob=mesh('299 '+which+' tread occlusion',vs,fs,mat);attr=ob.data.color_attributes.new(name='contact weight',type='FLOAT_COLOR',domain='POINT')
        for item,v in zip(attr.data,weights):item.color=(v,v,v,1)
        ob.shape_key_add(name='Basis')
        selected=[r for r in trace if (r['frame']-1)%3==0 or r['frame']==FRAMES]
        for index,r in enumerate(selected):
            p=Vector(r[which+'_tread_contact']);a=math.radians(r['yaw_deg']);rot=Matrix.Rotation(a,3,'Z');points=[]
            for v in vs:
                q=p+rot@Vector(v);hit,g,_,_=road.ray_cast(Vector((q.x,q.y,1)),Vector((0,0,-1)))
                if not hit:raise ValueError('Contact occlusion off road')
                q.z=g.z+.0012;points.append(q)
            shape=ob.shape_key_add(name='contact frame '+str(r['frame']))
            for v,q in zip(shape.data,points):v.co=q
            knots=[]
            if index:knots.append((selected[index-1]['frame'],0))
            knots.append((r['frame'],1))
            if index+1<len(selected):knots.append((selected[index+1]['frame'],0))
            for ff,value in knots:
                shape.value=value;shape.keyframe_insert('value',frame=ff)
        for r in trace:
            ob.hide_render=r[which+'_gap']>.012;ob.keyframe_insert('hide_render',frame=r['frame'])

def moon():
    ob=bpy.data.objects['distant moon'];mat=bpy.data.materials.new('299 NASA LRO lunar albedo');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'.runtime/art-direction/series01-sikh299/moon/lroc_color_2k.jpg'),check_existing=True);tex.image.pack()
    coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value=(0,0,-math.pi/2)
    env=n.new('ShaderNodeTexEnvironment');env.image=tex.image;l.new(coord.outputs['Normal'],mapping.inputs[0]);l.new(mapping.outputs[0],env.inputs[0])
    # Real maria remain visible; no point-sun shading on a near-full lunar disc.
    em=n.new('ShaderNodeEmission');em.inputs[1].default_value=.62;l.new(env.outputs['Color'],em.inputs[0]);out=n.new('ShaderNodeOutputMaterial');l.new(em.outputs[0],out.inputs['Surface'])
    ob.data.materials.clear();ob.data.materials.append(mat)

def contact_shading():
    # Geometry contact is measured separately. Local occlusion restores the
    # missing close-contact shadow beneath tires under broad multi-light fill.
    mat=bpy.data.objects['irregular packed farm track'].data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links
    bs=n['Principled BSDF'];source=bs.inputs['Base Color'].links[0].from_socket
    ao=n.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.18;ao.samples=16
    multiply=n.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1
    l.new(source,multiply.inputs[1]);l.new(ao.outputs['AO'],multiply.inputs[2]);l.new(multiply.outputs[0],bs.inputs['Base Color'])
    bpy.context.scene.eevee.use_raytracing=True

def flames_surface_diagnostic():
    for ob in list(bpy.data.objects):
        if ob.name.startswith('297 flame'):bpy.data.objects.remove(ob,do_unlink=True)
    mat=bpy.data.materials.new('299 living amber combustion');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links
    coord=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=5;noise.inputs['Detail'].default_value=3;l.new(coord.outputs['Generated'],noise.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.elements[0].position=.28;r.elements[0].color=(.65,.025,.001,1);r.elements[1].position=.76;r.elements[1].color=(1,.8,.19,1);e=r.elements.new(.51);e.color=(1,.26,.009,1);l.new(noise.outputs['Fac'],ramp.inputs[0])
    em=n.new('ShaderNodeEmission');em.inputs[1].default_value=3;l.new(ramp.outputs[0],em.inputs[0]);trans=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(noise.outputs['Fac'],mix.inputs[0]);l.new(trans.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs[0]);mat.surface_render_method='BLENDED';mat.use_transparent_shadow=False
    opacity=n.new('ShaderNodeMapRange');opacity.inputs['From Min'].default_value=.32;opacity.inputs['From Max'].default_value=.73;opacity.inputs['To Max'].default_value=.85;opacity.clamp=True;l.new(noise.outputs['Fac'],opacity.inputs[0])
    facing=n.new('ShaderNodeLayerWeight');facing.inputs['Blend'].default_value=.35
    invert=n.new('ShaderNodeMath');invert.operation='SUBTRACT';invert.inputs[0].default_value=1;l.new(facing.outputs['Facing'],invert.inputs[1])
    alpha=n.new('ShaderNodeMath');alpha.operation='MULTIPLY';l.new(invert.outputs[0],alpha.inputs[0]);l.new(opacity.outputs[0],alpha.inputs[1]);l.new(alpha.outputs[0],mix.inputs[0])
    for f in range(1,FRAMES+1,2):noise.inputs['W'].default_value=(f-1)/24*3.2;noise.inputs['W'].keyframe_insert('default_value',frame=f)
    for i,(x,y,z) in enumerate(TORCHES):
        height=1.9 if z==0 else 1.55
        for tongue in range(4):
            vs=[];fs=[];phase=i*1.77+tongue*2.2;length=.42 if tongue==0 else .28+.055*tongue;width=.073 if tongue==0 else .035
            for row in range(17):
                u=row/16;radius=width*math.sin(math.pi*(.10+.90*u))*(1+.12*math.sin(u*17+phase))
                for k in range(12):
                    a=k*math.tau/12;vs.append((radius*math.cos(a)+.035*math.sin(phase)*u+.032*math.sin(u*8+phase)*u, radius*math.sin(a)+.025*math.cos(u*9+phase)*u,length*u))
                if row:
                    for k in range(12):q=row*12+k;r=row*12+(k+1)%12;fs.append((q-12,r-12,r,q))
            ob=mesh('299 rising flame tongue',vs,fs,mat);ob.location=(x+(.035*math.sin(phase) if tongue else 0),y+(.035*math.cos(phase) if tongue else 0),z+height-.015)
            ob.shape_key_add(name='Basis');bend=ob.shape_key_add(name='turbulent buoyancy')
            for p in bend.data:
                u=p.co.z/length;p.co.x+=.085*math.sin(u*6+phase)*u*u;p.co.y+=.06*math.cos(u*9+phase)*u*u
            for f in range(1,FRAMES+1,2):
                t=(f-1)/24;bend.value=.5+.5*math.sin(t*8.3+phase);bend.keyframe_insert('value',frame=f)
                ob.scale=(1+.12*math.sin(t*13+phase),1+.1*math.cos(t*11+phase),1+.22*math.sin(t*9+phase)+.08*math.sin(t*19+phase));ob.keyframe_insert('scale',frame=f)

def flames():
    # Combustion is participating light, not an opaque petal silhouette.
    # A moving tapered turbulent field has a soft boundary from every view.
    bpy.context.scene.eevee.volumetric_tile_size='4'
    bpy.context.scene.eevee.volumetric_samples=96
    for ob in list(bpy.data.objects):
        if ob.name.startswith('297 flame'):bpy.data.objects.remove(ob,do_unlink=True)
    mat=bpy.data.materials.new('299 emissive flame volume');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links
    def mathnode(op,a=None,b=None):
        m=n.new('ShaderNodeMath');m.operation=op
        for i,value in enumerate((a,b)):
            if value is None:continue
            if isinstance(value,(float,int)):m.inputs[i].default_value=value
            else:l.new(value,m.inputs[i])
        return m.outputs[0]
    tc=n.new('ShaderNodeTexCoord');separate=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Generated'],separate.inputs[0]);x,y,z=[separate.outputs[k] for k in ('X','Y','Z')]
    advect=n.new('ShaderNodeVectorMath');advect.operation='ADD';l.new(tc.outputs['Generated'],advect.inputs[0])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4.5;noise.inputs['Detail'].default_value=3;l.new(advect.outputs[0],noise.inputs[0])
    nx=mathnode('SUBTRACT',x,.5);ny=mathnode('SUBTRACT',y,.5)
    radial=mathnode('SQRT',mathnode('ADD',mathnode('MULTIPLY',nx,nx),mathnode('MULTIPLY',ny,ny)))
    width=mathnode('MULTIPLY',mathnode('SUBTRACT',1,z),.43)
    turbulence=mathnode('MULTIPLY',mathnode('SUBTRACT',noise.outputs['Fac'],.5),.36)
    field=mathnode('MAXIMUM',mathnode('SUBTRACT',mathnode('ADD',width,turbulence),radial),0)
    bottom=mathnode('MINIMUM',mathnode('MULTIPLY',z,14),1)
    field=mathnode('MULTIPLY',field,bottom)
    emission=mathnode('MULTIPLY',field,18)
    color=n.new('ShaderNodeValToRGB');color.color_ramp.elements[0].position=.01;color.color_ramp.elements[0].color=(1,.055,.001,1);color.color_ramp.elements[1].position=.29;color.color_ramp.elements[1].color=(1,.72,.13,1);l.new(field,color.inputs[0])
    volume=n.new('ShaderNodeVolumePrincipled');l.new(mathnode('MULTIPLY',field,.08),volume.inputs['Density']);l.new(emission,volume.inputs['Emission Strength']);l.new(color.outputs[0],volume.inputs['Emission Color']);out=n.new('ShaderNodeOutputMaterial');l.new(volume.outputs[0],out.inputs['Volume'])
    for f in range(1,FRAMES+1,2):advect.inputs[1].default_value=(.02*math.sin(f*.2),0,-(f-1)/24*1.8);advect.inputs[1].keyframe_insert('default_value',frame=f)
    for i,(x,y,z) in enumerate(TORCHES):
        height=1.9 if z==0 else 1.55
        bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,z+height+.25));ob=bpy.context.object;ob.name='299 turbulent flame volume';ob.data.materials.append(mat);ob.scale=(.38,.38,.65)
        for f in range(1,FRAMES+1,2):
            t=(f-1)/24;ob.scale=(.38*(1+.12*math.sin(t*9+i)),.38,.65*(1+.16*math.sin(t*11+i)))
            ob.location.z=z+height-.025+ob.scale.z/2;ob.keyframe_insert('scale',frame=f);ob.keyframe_insert('location',frame=f)

def build(out):
    trace=motion(out);contact_shading();contact(out,trace);moon();flames()
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for point in curve.keyframe_points:point.interpolation='LINEAR'
    bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
    return trace
