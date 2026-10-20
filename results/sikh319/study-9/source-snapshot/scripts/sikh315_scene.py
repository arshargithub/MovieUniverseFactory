"""Director315 fixed construction: physical support, coupled action, persistent FX."""
import math,json
import bpy
import numpy as np
from mathutils import Vector,Quaternion
from mathutils.noise import noise_vector
from mathutils.bvhtree import BVHTree
from movie_factory import sikh315_motion as m
from sikh257_layout import key
from sikh257_native import camera_at,mesh
from sikh292_assets import surface

def noise(x,y,s):return noise_vector(Vector((x*s,y*s,9.153)))[0]
def terrain(out):
    from sikh305_land import bank_height
    road=bpy.data.objects['irregular packed farm track'];old=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    rig=bpy.data.objects['horse.rig'];supports=[]
    for name in ('DEF-f_toe.L','DEF-f_toe.R','hind_foot_ik.L','hind_foot_ik.R'):
        p=rig.matrix_world@rig.pose.bones[name].tail if name.startswith('DEF') else rig.matrix_world@rig.pose.bones[name].head
        hit=old.ray_cast(Vector((p.x,p.y,8)),Vector((0,0,-1)))[0];supports.append((p.x,p.y,hit.z))
    p=bpy.data.objects['LEADER spear world contact owner'].location;supports.append((p.x,p.y,p.z))
    def height(x,y):
        a=abs(x);n0=noise(x,y,.33);n1=noise(x,y,1.3);n2=noise(x,y,5.5)
        crown=.095*math.exp(-(a/1.45)**2)
        rutcenter=.67+.13*noise(3,y,.3)
        rut=-.067*math.exp(-((a-rutcenter)/.22)**2)
        lane=crown+rut+.045*n0+.025*n1+.012*n2
        center=2.8+.22*noise(2,y,.4)+.11*noise(1,y,1.1)
        d=(a-center)/(.48+.13*noise(4,y,.26))
        ditch=-.39*max(0,1-abs(d)**1.4)
        lip=.12*math.exp(-((d-1.0)/.48)**2)*(1+.5*n1)
        verge=.08*n0+.045*n1+.025*n2+ditch+lip
        w=m.ease((a-1.5)/.65);z=lane*(1-w)+verge*w
        # Short connected wash channels on the embankment, not decorative
        # periodic waves or a mathematically level platform.
        if 1.6<x<24 and -46<y<-12:
            base=bank_height(x,y)
            if base>z+.12:
                relief=.16*noise(x,y,.65)+.095*n1+.045*n2
                channel=-.18*abs(noise(x*.6,y,2))**2
                z=base+relief+channel
                for sx,sy,sz in supports:
                    distance=math.hypot(x-sx,y-sy)
                    wt=1-m.ease((distance-.16)/.40)
                    z=z*(1-wt)+sz*wt
        return z
    xs=sorted(set([-110,-60,-30,-20,-15,-8]+[round(-5+i*.08,3) for i in range(126)]+[round(5+i*.13,3) for i in range(147)]+[30,60,110]))
    ys=sorted(set([-260+j*.5 for j in range(801)]+[round(-60+j*.16,3) for j in range(813)]));nx=len(xs);vs=[];fs=[]
    for j,y in enumerate(ys):
        for x in xs:vs.append((x,y,height(x,y)))
        if j:
            for i in range(nx-1):q=j*nx+i;fs.append((q-nx,q+1-nx,q+1,q))
    mat=surface('315 shaped earth ochre and slate',[(.175,.142,.093),(.245,.204,.134)],8.2,rough=.93,bump=.004)
    data=bpy.data.meshes.new('315 rutted crown eroded banks and irregular hill');data.from_pydata(vs,[],fs);data.materials.append(mat);data.update();road.data=data
    for p in data.polygons:p.use_smooth=True
    colors=data.color_attributes.new(name='315 sediment',type='FLOAT_COLOR',domain='POINT')
    for v,c in zip(data.vertices,colors.data):
        x,y,z=v.co;wet=math.exp(-((abs(x)-2.8)/.4)**2)*max(.15,.6+.5*noise(x,y,.7));shade=1-.62*wet
        c.color=(shade,shade*.96,shade*.86,1)
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF'];src=b.inputs['Base Color'].links[0].from_socket
    attr=n.new('ShaderNodeAttribute');attr.attribute_name='315 sediment';mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.8;l.new(src,mix.inputs[1]);l.new(attr.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],b.inputs['Base Color'])
    moved=0
    for ob in bpy.data.objects:
        if ob.type!='MESH' or not ob.name.startswith(('304 rooted ditch','305 settled ditch','304 cultivated parcel','305 departure parcel','314 clustered drainage vegetation','304 intermittent silt')):continue
        for v in ob.data.vertices:
            x,y=v.co.x+ob.location.x,v.co.y+ob.location.y;hit=old.ray_cast(Vector((x,y,8)),Vector((0,0,-1)))[0]
            if hit:v.co.z+=height(x,y)-hit.z;moved+=1
    # Ground-coupled field rubble: embedded collapsed clay with an irregular
    # flattened silhouette, concentrated at cut banks rather than random road spikes.
    rng=np.random.default_rng(315);verts=[];faces=[]
    for _ in range(1500):
        y=float(rng.uniform(-170,95));x=float(rng.uniform(2.25,3.55))*(-1 if rng.random()<.5 else 1)
        if noise(x,y,.36)<0:continue
        r=float(rng.uniform(.035,.14));z=height(x,y);q=len(verts)
        for ring,h,scale in ((0,-.025,1),(1,r*.44,.75)):
            for k in range(7):
                a=math.tau*k/7;rr=r*scale*float(rng.uniform(.75,1.2));verts.append((x+rr*math.cos(a),y+rr*math.sin(a),z+h))
        faces.append(tuple(q+7+k for k in range(7)))
        for k in range(7):j=(k+1)%7;faces.append((q+k,q+j,q+7+j,q+7+k))
    mesh('315 collapsed clay bank clods',verts,faces,mat)
    (out/'terrain.json').write_text(json.dumps({'vertices':len(vs),'faces':len(fs),'supports':supports,'moved_root_vertices':moved,'lane_peak_to_valley_sample':max(height(x,y) for x in (-1,0,1) for y in range(-40,40))-min(height(x,y) for x in (-1,0,1) for y in range(-40,40))},indent=2))
    return height

def motorcycle(out,height):
    import sikh305_scene as old
    import sikh299_scene as low
    previous=old.c;contact=low.contact;motion=low.motion;old.c=m;low.contact=lambda *args:None
    low.motion=lambda dest:motion(dest,support_height=height)
    m.ground_height=height
    try:trace=old.motorcycle(out)
    finally:old.c=previous;low.contact=contact;low.motion=motion
    # Contact builder needs the inherited volume graph by its original name.
    if not bpy.data.materials.get('staging dust volume'):
        mat=bpy.data.materials['305 expanding advected dust'].copy();mat.name='staging dust volume'
    contact(out,trace)
    from sikh314_scene import debris
    debris(out)
    s=bpy.context.scene;cam=s.camera;rows=[]
    for row in trace:
        t=row['source_t'];f=row['frame']
        if t<18.5:continue
        s.frame_set(f);y=m.travel(t)
        if t<20.5:
            camera_at(cam,(-2.15,y+3.3,.85),(0,y-.20,1.02));cam.data.lens=34
        elif t<23.45:
            u=m.ease((t-22.6)/.85);near=Vector((-2.35,y+3.8,.74));far=Vector((-2.8,m.travel(22.6)+3.8,2.1))
            camera_at(cam,near.lerp(far,u),(m.lateral(t),y-.15,1.05));cam.data.lens=34
        else:
            u=m.ease((t-23.45)/4);loc=Vector((-2.8,m.travel(22.6)+3.8,2.1)).lerp(Vector((-1.5,m.travel(22.6)+1,3.5)),u)
            camera_at(cam,loc,Vector((0,y-.15,1.05)).lerp(Vector((0,-145,1.2)),u));cam.data.lens=34+8*u
        key(cam,f);cam.data.keyframe_insert('lens',frame=f)
        rows.append({'frame':f,'source_t':t,'forward_speed_source':m.speed(t),'yaw':m.yaw(t),'lateral':m.lateral(t),'rear_distance':m.rear_distance(t),'travel':y})
    (out/'launch-phases.json').write_text(json.dumps(rows,indent=2));return trace

def horse(out):
    import sikh305_scene as old
    original_c,original_bone,original_key=old.c,old.bone_x,old.key
    old.c=m;seen=set()
    def rekey(ob,f):
        if ob.name=='HORSE hind support pivot' and f not in seen:
            seen.add(f);t=(f-1)/24*m.RATE;a=m.rear(t)
            ob.rotation_euler.x-=.17*a;ob.location.y-=.045*a;ob.location.z+=.42*a
            ob.rotation_euler.y=.015*a*math.sin((t-15.2)*7)
        elif ob.name=='mounted leader':
            t=(f-1)/24*m.RATE
            ob.rotation_euler.x-=.06*m.rear(t)+.035*m.landing(t)
            ob.rotation_euler.y=-.010*m.rear(t)*math.sin((t-15.2)*7)
        original_key(ob,f)
    def bone(rig,name,angle,f):
        t=(f-1)/24*m.RATE;p=m.pose(t,'R' if name.endswith('.R') else 'L')
        if p['rise']>0:
            for prefix,param in (('upper_arm_fk','shoulder'),('forearm_fk','elbow'),('forefoot_fk','wrist'),('f_toe_fk','toe')):
                if name.startswith(prefix):angle=p[param]
        if name=='neck':
            angle=p['neck']+.012*math.sin(t*1.7)
            # Spine compression/extension changes the shape of the horse,
            # not just its world transform. Small enough to preserve saddle fit.
            original_bone(rig,'chest',p['chest'],f);original_bone(rig,'hips',p['hips'],f)
        elif name=='head':angle=p['head']+.012*math.sin(t*2.1)
        elif name=='jaw':angle=.07*m.bump(t,14.8,15.1,16.5,16.9)
        original_bone(rig,name,angle,f)
    old.key=rekey;old.bone_x=bone
    try:old.horse(out,rebuild_groom=True)
    finally:old.c=original_c;old.bone_x=original_bone;old.key=original_key

def dust(out,trace):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(('authored world-space dust','299 tire-contact dust','305 world dust cloud','315 detached world wake')):bpy.data.objects.remove(ob,do_unlink=True)
    mat=bpy.data.materials['305 expanding advected dust'];rng=np.random.default_rng(315);births=[]
    for row in trace:
        t=row['source_t'];f=row['frame']
        cadence=2 if t>23.2 else 5
        if f%cadence==1 and (t<7.5 or t>18.5):births.append((f,Vector(row['rear_tread_contact']),t,1.5 if row['slip'] else .8))
    for f in range(-47,1,5):
        t=(f-1)/24*m.RATE;births.append((f,Vector((0,m.travel(t)+.7,.07)),t,.8))
    report=[]
    for birth,p,t,intensity in births:
        launch=21.35<t<23.2;life=8.5 if launch else 6.5;end=min(m.FRAMES,birth+math.ceil(life*24))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);ob=bpy.context.object;ob.name='315 detached world wake';ob.data.materials.append(mat)
        drift=Vector((float(rng.uniform(.20,.48)),float(rng.uniform(.12,.38)),float(rng.uniform(.14,.27))))
        ob.hide_render=True;ob.keyframe_insert('hide_render',frame=max(0,birth-1));ob.hide_render=False;ob.keyframe_insert('hide_render',frame=max(1,birth))
        for f in sorted(set([max(1,birth),end]+list(range(max(1,birth),end+1,4)))):
            age=(f-birth)/24;size=(.27+.60*age)*(1.35 if launch else 1)
            den=m.ease(age/.15)*(1-m.ease((age-2.8)/(life-2.8)))/(1+(max(0,age-.5)/1.55)**2)
            ob.location=p+drift*age;ob.location.z+=.16;ob.scale=(size*1.25,size,size*.65);ob.color=(1,1,1,den*intensity*(1.8 if launch else .55));key(ob,f);ob.keyframe_insert('color',frame=f)
        if end<m.FRAMES:ob.hide_render=True;ob.keyframe_insert('hide_render',frame=end+1)
        report.append({'name':ob.name,'birth_frame':birth,'world_birth':list(p),'world_drift_mps':list(drift),'life':life,'launch':launch,'parent':None})
    (out/'dust-ownership.json').write_text(json.dumps(report,indent=2))

def build(out):
    s=bpy.context.scene;s.frame_set(1)
    height=terrain(out);print('315 shaped terrain complete',flush=True)
    crops=[o for o in bpy.data.objects if o.name.startswith(('304 cultivated','305 departure parcel','304 boundary tree'))]
    for ob in crops:ob.hide_viewport=True
    trace=motorcycle(out,height);print('315 coupled launch and contacts complete',flush=True)
    horse(out);print('315 reference phased horse complete',flush=True)
    dust(out,trace)
    from sikh305_impacts import build_impacts
    build_impacts(out,event_definitions=[('spear',14.28,None,.20),('grip-left',14.38,'DEF-f_toe.L',.25),('grip-right',14.56,'DEF-f_toe.R',.25),('hind-drive-left',14.80,'DEF-r_toe.L',.35),('hind-drive-right',14.84,'DEF-r_toe.R',.35),('landing-left',17.10,'DEF-f_toe.L',1.0),('landing-right',17.14,'DEF-f_toe.R',.85)],follow_terrain=True)
    for ob in crops:ob.hide_viewport=False
    s.frame_set(1)
