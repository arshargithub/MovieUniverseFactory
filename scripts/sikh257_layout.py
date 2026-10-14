"""Fixed, reversible Sikh story-blocking scene. Not final cast/look approval.

Metres; rider forward is local -Y. No asset scripts or external calls.
"""
import math
import json
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector, Matrix
from sikh257_native import material, mesh, sphere, scene_setup, camera_at, male_bust, ROOT
from movie_factory.sikh257_geometry import ease, cloth_strip, end_translation, joint_between

def empty(name,parent=None):
    ob=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(ob);ob.parent=parent;return ob

def attach(ob,parent):
    ob.parent=parent;return ob

def tube(name,points,radius,mat,parent=None):
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=radius;d.bevel_resolution=2
    s=d.splines.new('POLY');s.points.add(len(points)-1)
    for v,p in zip(s.points,points):v.co=(*p,1)
    ob=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(ob);d.materials.append(mat);ob.parent=parent;return ob

def capsule(name,a,b,radius,mat,parent=None):
    ob=sphere(name,(0,0,0),(1,1,1),mat);ob.parent=parent
    segment(ob,a,b,radius);return ob

def segment(ob,a,b,radius):
    a,b=Vector(a),Vector(b);ob.location=(a+b)/2;ob.rotation_mode='QUATERNION';ob.rotation_quaternion=(b-a).to_track_quat('Z','Y');ob.scale=(radius,radius,(b-a).length/2+radius*.25)

def key(ob,f):
    for field in ('location','rotation_quaternion' if ob.rotation_mode=='QUATERNION' else 'rotation_euler','scale'):ob.keyframe_insert(field,frame=f)

def wheel(parent,y,mat,rim):
    root=empty('wheel rolling owner',parent);root.location=(0,y,.34)
    bpy.ops.mesh.primitive_torus_add(major_radius=.285,minor_radius=.055,major_segments=48,minor_segments=12)
    ob=bpy.context.object;ob.name='rubber tire';ob.parent=root;ob.location=(0,0,0);ob.rotation_euler=(0,math.pi/2,0);ob.data.materials.append(mat)
    for off in (-.025,.025):
        tube('rim',[(off,.26*math.sin(i*math.tau/48),.26*math.cos(i*math.tau/48)) for i in range(49)],.012,rim,root)
    for i in range(18):
        a=i*math.tau/18;tube('spoke',[(0,0,0),(0,.26*math.sin(a),.26*math.cos(a))],.0035,rim,root)
    capsule('hub',(-.08,0,0),(.08,0,0),.065,rim,root)
    return root

def motorcycle():
    r=empty('motorcycle travel');paint=material('military charcoal green',(.075,.10,.075));metal=material('worn steel',(.22,.23,.22));rubber=material('rubber',(.018,.021,.025));leather=material('saddle leather',(.10,.053,.027))
    wheels=[wheel(r,y,rubber,metal) for y in (-.70,.70)]
    for sign in (-1,1):
        tube('rigid frame',[(sign*.11,.70,.34),(sign*.11,.15,.39),(sign*.11,-.52,1.01),(sign*.11,.35,.79),(sign*.11,.70,.34)],.028,paint,r)
        tube('girder fork',[(sign*.095,-.70,.34),(sign*.095,-.50,1.06)],.023,metal,r)
        tube('exhaust',[(sign*.16,-.13,.59),(sign*.20,-.30,.31),(sign*.20,.83,.28)],.035,metal,r)
    attach(sphere('fuel tank',(0,-.16,.91),(.19,.32,.16),paint),r)
    attach(sphere('sprung saddle',(0,.32,.83),(.20,.23,.055),leather),r)
    attach(sphere('crankcase',(0,.10,.47),(.15,.19,.15),metal),r)
    for z in np.linspace(.53,.75,7):capsule('single cylinder cooling fin',(-.14,-.10,float(z)),(.14,-.10,float(z)),.035,metal,r)
    tube('low drag bar',[(-.40,-.38,1.09),(-.18,-.38,1.09),(0,-.48,1.08),(.18,-.38,1.09),(.40,-.38,1.09)],.021,metal,r)
    for sign in (-1,1):
        capsule('grip',(sign*.29,-.38,1.09),(sign*.41,-.38,1.09),.028,rubber,r)
        tube('lever',[(sign*.29,-.42,1.09),(sign*.41,-.43,1.08)],.009,metal,r)
        capsule('foot peg',(sign*.13,.08,.25),(sign*.29,.08,.25),.026,metal,r)
    attach(sphere('round headlamp',(0,-.59,1.00),(.10,.07,.10),metal),r)
    bulb=material('lamp lens',(.8,.58,.29));bs=bulb.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.65,.26,1);bs.inputs['Emission Strength'].default_value=3
    attach(sphere('warm lamp',(0,-.652,1.00),(.080,.015,.080),bulb),r)
    return r,wheels

def loft(name,rings,mat,parent=None):
    vs=[];fs=[];n=24
    for x,y,z,rx,ry in rings:
        for j in range(n):
            a=j*math.tau/n;vs.append((x+rx*math.sin(a),y+ry*math.cos(a),z))
    for i in range(len(rings)-1):
        for j in range(n):fs.append((i*n+j,(i+1)*n+j,(i+1)*n+(j+1)%n,i*n+(j+1)%n))
    ob=mesh(name,vs,fs,mat);ob.parent=parent;return ob

def actor(parent,cache):
    r=empty('rider body',parent);cloth=material('rough cast dark tunic',(.075,.085,.11));pants=material('rough cast trousers',(.11,.13,.15));skin=material('rough cast hands',(.35,.18,.095));black=material('beard and boots',(.025,.018,.014));brass=material('cartridges',(.32,.20,.07))
    torso=loft('tunic torso',[(0,.24,.89,.17,.12),(0,.20,1.03,.16,.105),(0,.13,1.25,.21,.13),(0,.10,1.39,.235,.12),(0,.10,1.45,.16,.09)],cloth,r)
    # A tapered connection, not a detached ellipsoid below the donor jaw.
    neck=loft('neck connection',[(0,.10,1.40,.11,.085),(0,.09,1.48,.075,.065),(0,.08,1.57,.065,.060)],skin,r)
    loft('standing tunic collar',[(0,.10,1.43,.13,.09),(0,.09,1.48,.085,.073)],cloth,r)
    before=set(bpy.data.objects);bust,beard=male_bust();head=empty('head performance',r);head.location=(0,.08,.10)
    # Only donor head above jaw; the costume owns the body silhouette in blocking.
    import bmesh
    bm=bmesh.new();bm.from_mesh(bust.data);bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<1.405],context='VERTS');bm.to_mesh(bust.data);bm.free()
    for ob in set(bpy.data.objects)-before:
        if ob not in (head,):
            if ob.type=='MESH':
                for mod in list(ob.modifiers):
                    if mod.type=='COLLISION':ob.modifiers.remove(mod)
            ob.parent=head
    beard.scale=(.83,.78,1.15)
    hairmat=beard.data.materials[0]
    for side in (-1,1):
        tube('moustache',[(0,-.151,1.50),(side*.025,-.151,1.50),(side*.052,-.137,1.49)],.009,hairmat,head)
    clothob=mesh('connected turban and covering',cache['points'][0].tolist(),cache['faces'].tolist(),material('dark indigo turban',(.025,.035,.065)));clothob.parent=head
    base=clothob.shape_key_add(name='Basis')
    # Sparse sampled cache interpolation is an explicit rough-preview reuse.
    for i in range(0,len(cache['points']),4):
        k=clothob.shape_key_add(name='cloth sample '+str(i),from_mix=False)
        k.data.foreach_set('co',cache['points'][i].ravel());k.value=0
    limbs={}
    for side in (-1,1):
        for part in ('upper arm','forearm','thigh','shin'):
            limbs[side,part]=capsule(part,(0,0,0),(0,0,.2),.07,cloth if 'arm' in part else pants,r)
        limbs[side,'palm']=attach(sphere('palm',(0,0,0),(.035,.025,.055),skin),r)
        limbs[side,'boot']=attach(sphere('boot',(0,0,0),(.070,.135,.06),black),r)
    # Equipment is a readable rough shape, not a functioning weapon design.
    strap=tube('cartridge bandolier',[(-.18,.025,1.41),(-.06,-.025,1.25),(.14,.075,1.04)],.025,black,r)
    for i in range(8):
        u=i/7;capsule('cartridge',(-.17+.29*u,-.006+.055*u,1.39-.32*u),(-.14+.29*u,-.006+.055*u,1.34-.32*u),.011,brass,r)
    for x in (.14,.17):tube('double barrel',[(x,.24,1.03),(x+.03,.22,1.75)],.016,black,r)
    capsule('wood stock',(.12,.25,.87),(.15,.24,1.12),.043,material('wood stock',(.18,.08,.025)),r)
    return dict(root=r,head=head,cloth=clothob,limbs=limbs,torso=torso,neck=neck)

def travel(t):
    if t<8:return 50-7*t
    if t<10:
        u=t-8;return -6-7*u+1.75*u*u
    if t<18:return -13.
    if t<21:return -13-1.2*(t-18)
    u=t-21;return -16.6-1.2*u-.9*u*u

def pose_actor(a,t,f):
    hold=ease((t-10)/.8)*(1-ease((t-17.6)/.4));bow=ease((t-13.5)/.6)*(1-ease((t-14.5)/.5))
    a['root'].location.z=.008*math.sin(t*15)*(1-hold);a['head'].rotation_euler.x=-.10*hold+.25*bow+.015*math.sin(t*13)*(1-hold)
    a['head'].rotation_euler.z=(math.atan2(3.3,24+travel(t))-.40)*hold
    key(a['root'],f);key(a['head'],f)
    for side in (-1,1):
        shoulder=(side*.215,.09,1.395);hand=Vector((side*.35,-.38,1.09))
        if side==1:
            reach=ease((t-10.8)/.6)*(1-ease((t-13.1)/.5));u=max(0,min(1,(t-11.4)/1.7))
            end=Vector((.117,-.010,1.610+.130*math.sin(.05)+.015-.030))
            target=end+Vector(end_translation(max(1,(t-11)*48)))+Vector((0,.08,.10));hand=hand.lerp(target,reach)
        greet=ease((t-13.2)/.6)*(1-ease((t-15.1)/.6))
        hand=hand.lerp(Vector((side*.026,-.18,1.40)),greet)
        elbow=joint_between(shoulder,hand,.31,.30,(side,.1,-.5))
        segment(a['limbs'][side,'upper arm'],shoulder,elbow,.075);segment(a['limbs'][side,'forearm'],elbow,hand,.055)
        palm=a['limbs'][side,'palm'];palm.location=hand;palm.rotation_euler=(math.pi/2*(1-greet),0,side*.15*greet)
        foot=Vector((side*.23,.08,.30))
        if side==-1:foot=foot.lerp(Vector((-.32,.28,.07)),hold)
        hip=(side*.135,.25,.96);knee=joint_between(hip,foot,.46,.46,(side*.3,-1,0))
        segment(a['limbs'][side,'thigh'],hip,knee,.095);segment(a['limbs'][side,'shin'],knee,foot,.075)
        a['limbs'][side,'boot'].location=foot
        for part in ('upper arm','forearm','palm','thigh','shin','boot'):key(a['limbs'][side,part],f)
    sample=max(0,min(143,(t-11.0)*48))
    ks=a['cloth'].data.shape_keys.key_blocks
    for k in list(ks)[1:]:
        n=int(k.name.rsplit(' ',1)[1]);k.value=max(0,1-abs(sample-n)/4)
        if sample>=140 and n==140:k.value=1
        k.keyframe_insert('value',frame=f)

def scenery():
    earth=material('moonlit ochre road',(.20,.18,.13));green=material('painted field green',(.09,.15,.12));dark=material('tree silhouettes',(.025,.065,.052));bark=material('tree bark',(.065,.055,.045))
    mesh('ground',[(-80,-110,-.06),(80,-110,-.06),(80,80,-.06),(-80,80,-.06)],[(0,1,2,3)],green)
    mesh('dirt lane',[(-1.8,-100,0),(1.8,-100,0),(1.8,80,0),(-1.8,80,0)],[(0,1,2,3)],earth)
    rng=np.random.default_rng(257)
    for side in (-1,1):
        for y in range(-90,75,12):
            tube('field boundary',[(side*2,y,.03),(side*45,y,.03)],.07,earth)
        for i in range(55):
            x=side*float(rng.uniform(6,65));y=float(rng.uniform(-100,80));h=float(rng.uniform(3,6))
            capsule('tree trunk',(x,y,0),(x,y,h*.7),.14,bark)
            for dx,dy,dz,r in ((0,0,0,1),(-.25,.1,-.10,.72),(.25,-.1,-.07,.78)):
                sphere('broad tree canopy',(x+dx*h,y+dy*h,h*(.76+dz)),(h*.37*r,h*.32*r,h*.28*r),dark)
        # Crop rows give cultivated ground, not the Pashtun's rocky desert.
        vs=[];fs=[]
        for x in np.linspace(2.4,32,45):
            for y in np.linspace(-95,75,200):
                x0=side*float(x)+float(rng.uniform(-.08,.08));y0=float(y)+float(rng.uniform(-.1,.1));h=float(rng.uniform(.18,.32));i=len(vs)
                vs.extend([(x0-.045,y0,0),(x0+.045,y0,0),(x0,y0+.04,h),(x0,y0-.045,0),(x0,y0+.045,0),(x0+.04,y0,h)])
                fs.extend([(i,i+1,i+2),(i+3,i+4,i+5)])
        mesh('cultivated grain blades',vs,fs,green)
    pts=[];fs=[]
    for j in range(21):
        for i in range(21):
            x=-3+6*i/20;y=-4+8*j/20;r=max(abs(x)/2.7,abs(y)/3.6);z=.72*(1-ease((r-.5)/.5));pts.append((3.3+x,-24+y,z-.01))
    for j in range(20):
        for i in range(20):
            a=j*21+i;fs.append((a,a+1,a+22,a+21))
    mound=mesh('low raised earth bank',pts,fs,earth)
    return mound

def dust_pool():
    m=bpy.data.materials.new('moonlit road dust');m.use_nodes=True;n=m.node_tree.nodes;n.clear()
    output=n.new('ShaderNodeOutputMaterial');transparent=n.new('ShaderNodeBsdfTransparent');color=n.new('ShaderNodeEmission');color.inputs[0].default_value=(.25,.28,.30,1);color.inputs[1].default_value=.7
    uv=n.new('ShaderNodeTexCoord');sub=n.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,0)
    length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';ramp=n.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=0;ramp.inputs['From Max'].default_value=.5;ramp.inputs['To Min'].default_value=.65;ramp.inputs['To Max'].default_value=0
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7
    mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mix=n.new('ShaderNodeMixShader');links=m.node_tree.links
    links.new(uv.outputs['UV'],sub.inputs[0]);links.new(sub.outputs[0],length.inputs[0]);links.new(length.outputs['Value'],ramp.inputs['Value']);links.new(uv.outputs['UV'],noise.inputs['Vector']);links.new(ramp.outputs['Result'],mul.inputs[0]);links.new(noise.outputs['Fac'],mul.inputs[1]);links.new(mul.outputs[0],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1]);links.new(color.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],output.inputs['Surface'])
    result=[]
    for i in range(30):
        ob=mesh('rough world-space dust card '+str(i),[(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],[(0,1,2,3)],m)
        layer=ob.data.uv_layers.new()
        for loop,coord in zip(layer.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=coord
        result.append(ob)
    return result

def pose_dust(pool,t,f,cam):
    for i,ob in enumerate(pool):
        age=(t+i*.13)%3.90;born=t-age;velocity=abs(travel(born+.02)-travel(born-.02))/.04
        ob.location=(.28*math.sin(i*3.2)+age*.12,travel(born)+.8,.25+age*.20)
        size=(.35+age*.55)*(1-ease((age-2.7)/1.2))*min(1,velocity/3)
        ob.scale=(max(.001,size),max(.001,size*.60),1);ob.rotation_mode='QUATERNION';ob.rotation_quaternion=(cam.location-ob.location).to_track_quat('Z','Y');key(ob,f)

def crowd():
    blue=material('Nihang indigo',(.035,.065,.19));skin=material('crowd skin',(.28,.15,.07));steel=material('pole steel',(.22,.25,.28));people=[]
    for i in range(12):
        side=-1 if i%2 else 1;x=side*(.40+.40*(i//2));y=-19+(i%3)*.7
        r=empty('Nihang foot warrior '+str(i));r.location=(x,y,0)
        loft('long blue robe',[(0,0,.14,.20,.13),(0,0,.90,.15,.12),(0,0,1.40,.23,.14),(0,0,1.46,.12,.08)],blue,r)
        attach(sphere('crowd face',(0,0,1.59),(.080,.075,.12),skin),r)
        attach(sphere('Nihang turban',(0,.01,1.72),(.12,.12,.16),blue),r)
        foot_objects=[]
        for s in (-1,1):
            capsule('crowd arm',(s*.20,0,1.35),(s*.25,-.05,1.02),.065,blue,r)
            foot_objects.append((attach(sphere('crowd foot',(s*.10,-.03,.06),(.07,.15,.06),steel),r),s))
        tube('upright spear',[(.32,0,.05),(.32,0,2.25)],.012,steel,r)
        people.append((r,side,x,y,foot_objects))
    return people

def horse_leader():
    """Source deform rig; new support proof required, no inherited gallop pass."""
    source=ROOT/'.runtime/assets/demonstrator-01/horse.blend'
    with bpy.data.libraries.load(str(source),link=False) as (_,dest):dest.objects=['horse','horse.rig']
    body,rig=dest.objects
    for ob in (rig,body):
        if ob.name not in bpy.context.scene.objects:bpy.context.scene.collection.objects.link(ob)
    rig.animation_data_clear();body.animation_data_clear()
    for c in list(rig.constraints):rig.constraints.remove(c)
    for pb in rig.pose.bones:
        pb.matrix_basis.identity()
        if 'IK_FK' in pb:pb['IK_FK']=0
    for mod in list(body.modifiers):
        if mod.type not in ('ARMATURE',):body.modifiers.remove(mod)
    if body.data.shape_keys:
        body.data.shape_keys.animation_data_clear()
        for k in body.data.shape_keys.key_blocks:k.value=0
    body.data.materials.clear();body.data.materials.append(material('leader horse gray',(.32,.32,.29)))
    bpy.context.view_layer.update()
    root=empty('leader horse support root');base=rig.matrix_world.copy();rig.parent=root
    # Original rig's rest skeleton has a source scene offset; normalize on root.
    root.location=(3.3,-24,.72);root.rotation_euler.z=math.pi
    rig.location=(0,0,0);rig.rotation_euler=(0,0,0)
    bpy.context.view_layer.update()
    feet={n:(rig.matrix_world@rig.pose.bones[n].matrix).copy() for n in ('hind_foot_ik.L','hind_foot_ik.R','forefoot_ik.L','forefoot_ik.R')}
    rider=empty('mounted leader',root);blue=material('leader blue',(.035,.07,.23));gold=material('leader sash',(.65,.33,.045));skin=material('leader skin',(.28,.16,.085))
    rider.location=(0,.0,1.55)
    loft('leader torso',[(0,0,0,.16,.13),(0,0,.37,.23,.14),(0,0,.52,.12,.09)],blue,rider)
    attach(sphere('leader head',(0,-.01,.65),(.085,.09,.12),skin),rider)
    attach(sphere('leader tall turban',(0,0,.81),(.13,.13,.19),blue),rider)
    for s in (-1,1):
        capsule('leader thigh',(s*.12,0,.02),(s*.32,-.35,-.29),.095,blue,rider)
        capsule('leader shin',(s*.32,-.35,-.29),(s*.34,-.27,-.71),.07,blue,rider)
        capsule('leader arm',(s*.20,0,.42),(s*.23,-.33,.20),.065,blue,rider)
    tube('standard pole',[(.35,0,-.6),(.35,0,2.1)],.022,gold,rider)
    mesh('standard flag',[(.35,0,1.9),(.35,0,1.3),(.35,.65,1.45)],[(0,1,2)],gold).parent=rider
    return root,rig,rider,feet

def build(out,cache_path,stills=False,eevee=False):
    s,cam=scene_setup();s.render.resolution_x=360;s.render.resolution_y=640;s.render.fps=12;s.cycles.samples=12
    import os
    if os.environ.get('CYCLES_METAL_DISABLE_BINARY_ARCHIVES')!='1':raise ValueError('Reviewed Metal workaround required')
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL'
    devices=prefs.get_devices_for_type('METAL')
    if not any(d.type=='METAL' for d in devices):raise ValueError('No Metal device; no silent fallback')
    for d in devices:d.use=d.type=='METAL'
    prefs.metalrt='ON';s.cycles.device='GPU';s.render.use_persistent_data=False
    if eevee:s.render.engine='BLENDER_EEVEE'
    cam.data.type='PERSP';cam.data.lens=42
    for ob in list(s.objects):
        if ob.type=='LIGHT':bpy.data.objects.remove(ob,do_unlink=True)
    s.world.node_tree.nodes['Background'].inputs[0].default_value=(.06,.09,.17,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.55
    wn=s.world.node_tree.nodes;noise=wn.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4;noise.inputs['Detail'].default_value=3;coord=wn.new('ShaderNodeTexCoord');ramp=wn.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.35;ramp.color_ramp.elements[0].color=(.025,.04,.09,1);ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=(.22,.26,.33,1)
    s.world.node_tree.links.new(coord.outputs['Normal'],noise.inputs['Vector']);s.world.node_tree.links.new(noise.outputs['Fac'],ramp.inputs[0]);s.world.node_tree.links.new(ramp.outputs['Color'],wn['Background'].inputs[0])
    sun=bpy.data.lights.new('moon key','SUN');sun.energy=2.5;sun.color=(.57,.69,1);sun.angle=.12
    ob=bpy.data.objects.new('moon key',sun);s.collection.objects.link(ob);ob.rotation_euler=(.40,-.6,-.4)
    fill=bpy.data.lights.new('illustrated moon bounce','SUN');fill.energy=.8;fill.color=(.7,.75,1);o=bpy.data.objects.new('bounce',fill);s.collection.objects.link(o);o.rotation_euler=(.8,.9,2.3)
    scenery();people=crowd();bike,wheels=motorcycle();dust=dust_pool()
    fill=bpy.data.lights.new('rough actor bounce','AREA');fill.energy=180;fill.size=3;fill.color=(.67,.75,1)
    o=bpy.data.objects.new('rough actor bounce',fill);s.collection.objects.link(o);o.parent=bike;o.location=(1.5,-3,3.5);o.rotation_euler=(Vector((0,0,1.3))-o.location).to_track_quat('-Z','Y').to_euler()
    cache=np.load(cache_path,allow_pickle=False);a=actor(bike,cache);horse,rig,leader,feet=horse_leader()
    moonmat=material('moon disc',(.8,.84,.75));b=moonmat.node_tree.nodes.get('Principled BSDF');b.inputs['Emission Color'].default_value=(.7,.8,1,1);b.inputs['Emission Strength'].default_value=1
    sphere('moon',(-20,-95,30),(2,2,2),moonmat)
    phase=[];s.frame_start=1;s.frame_end=312
    for f in range(1,313):
        t=(f-1)/12;s.frame_set(f);bike.location=(0,travel(t),0)
        yaw=.40*ease((t-8.6)/1.0)*(1-ease((t-18.2)/1.0));bike.rotation_euler=(0,0,yaw)
        key(bike,f)
        for i,w in enumerate(wheels):
            w.rotation_euler.x=-travel(t)/.34
            if i==1 and 8.8<t<10:w.rotation_euler.x=-travel(8.8)/.34
            if i==1 and t>=10:w.rotation_euler.x+=(travel(10)-travel(8.8))/.34
            if i==1:w.rotation_euler.x+=2.5*ease((t-21)/.3)
            key(w,f)
        pose_actor(a,t,f)
        for r,side,x,y,foot_objects in people:
            opening=ease((t-16.7)/1.8);r.location=(x+side*2.1*opening,y,.015*math.sin(opening*math.pi*5));r.rotation_euler.z=-side*.22*opening;key(r,f)
            for ob,sign in foot_objects:
                step_phase=opening*math.pi*6+(0 if sign<0 else math.pi);active=math.sin(math.pi*opening)
                ob.location=(sign*.10+side*.14*math.sin(step_phase)*active,-.03,.06+.07*max(0,math.sin(step_phase))*active);key(ob,f)
        rear=ease((t-15)/.75)*(1-ease((t-16.2)/1.2));horse.rotation_euler.x=-.55*rear;key(horse,f)
        bpy.context.view_layer.update()
        for n,m in feet.items():
            target=m.copy()
            if n.startswith('forefoot'):
                target.translation+=Vector((0,-.36*rear,.92*rear))
            rig.pose.bones[n].matrix=rig.matrix_world.inverted()@target
            rig.pose.bones[n].keyframe_insert('location',frame=f);rig.pose.bones[n].keyframe_insert('rotation_quaternion',frame=f)
        leader.rotation_euler.x=.22*rear;key(leader,f)
        p=Vector(bike.location)
        if t<6:
            u=ease((t-2)/4);loc=p+Vector((2.0+6*u,-3.1+4.6*u,.65+4.15*u));target=p+Vector((0,-.1,1.0))
        elif t<8.6:
            loc=p+Vector((.65,1.85,1.90));target=Vector((.1,-20,1.4))
        elif t<15:
            u=ease((t-10.3)/1);loc=p+Vector((3.0-2.1*u,-4.2+2.7*u,1.3+.5*u));target=p+Vector((0,.05,1.10+.33*u))
        elif t<18:
            loc=Vector((.2,-17,2.0));target=Vector((3.3,-24,2.15+.3*rear))
        elif t<22:
            # Track inside the cleared corridor rather than through the people.
            loc=p+Vector((.35,-3.5,1.65));target=p+Vector((0,0,1.10))
        else:
            # Cut only after passage; rear coverage preserves the lane direction.
            u=ease((t-22)/4);loc=p+Vector((.8+2*u,3+2*u,2+1.8*u));target=p+Vector((0,-1,1.05))
        camera_at(cam,loc,target);key(cam,f);pose_dust(dust,t,f,cam)
        if f in (1,37,73,109,133,157,169,181,193,205,217,253,289,312):phase.append({'frame':f,'seconds':t,'bike':list(bike.location),'camera':list(cam.location)})
    # Linear samples prevent unintended Bezier camera cuts between separately authored shots.
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag=strip.channelbag(slot)
                    if bag:
                        for fc in bag.fcurves:
                            for k in fc.keyframe_points:k.interpolation='LINEAR'
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
    (out/'staging.json').write_text(json.dumps({'duration_seconds':26,'fps':12,'stage':'rough blocking, not production pass','frames':phase,'limitations':['Generic male stand-in, not approved Sikh face','Cloth cache is a tested transition candidate, not launch simulation','No soundtrack selected or mapped','Crowd locomotion and horse support require internal review before handoff']},indent=2))
    frames=[p['frame'] for p in phase] if stills else range(1,313)
    (out/'frames').mkdir()
    for f in frames:
        s.frame_set(f);s.render.filepath=str(out/'frames'/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
        print('layout rendered',f,flush=True)
    if stills:
        cam.animation_data_clear()
        for f in (181,193,205):
            s.frame_set(f);camera_at(cam,(9,-23,2.5),(3.3,-24,1.9));s.render.filepath=str(out/f'horse-side-{f}.png');bpy.ops.render.render(write_still=True)
