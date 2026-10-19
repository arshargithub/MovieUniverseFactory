"""Reviewed fixed derivative: suspension, coordinated rear, stepping and finish."""
import math,json,shutil
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from movie_factory import sikh317_motion as m
from movie_factory.sikh257_geometry import joint_between
from sikh257_layout import key,segment
from sikh257_native import mesh
from sikh292_assets import surface
from sikh317_run import SOURCE

def suspension(out):
    s=bpy.context.scene;root=bpy.data.objects['BIKE travel owner']
    wheels=[bpy.data.objects['BIKE '+n+' rolling owner'] for n in ('front','rear')]
    rows=[]
    for f in range(1,697):
        s.frame_set(f);rows.append((root.location.copy(),root.rotation_euler.copy(),[o.matrix_world.copy() for o in wheels]))
    z=m.smooth_response([r[0].z for r in rows],6)
    pitch=m.smooth_response([r[1].x for r in rows],6)
    # Lower fork geometry deforms along the same bounded axle excursion. The
    # lamp/handlebar/upper fork remain attached to the chassis, not the wheel.
    steer=bpy.data.objects['BIKE steering owner'];parts=[]
    for o in steer.children:
        if o.type=='MESH' and o.name.startswith('actual donor'):
            o.data=o.data.copy();o.shape_key_add(name='Basis')
            parts.append((o,o.shape_key_add(name='317 lower fork compliance')))
    displacements=[];errors=[]
    for f,(loc,rot,worlds) in enumerate(rows,1):
        s.frame_set(f);w=m.travel_response((f-1)/24*m.RATE)
        root.location=loc;root.location.z+=w*(z[f-1]-loc.z)
        root.rotation_euler=rot;root.rotation_euler.x+=w*(pitch[f-1]-rot.x)
        key(root,f);bpy.context.view_layer.update()
        for o,target in zip(wheels,worlds):
            o.matrix_world=target;o.keyframe_insert('location',frame=f)
            # Restore local wheel orientation as well: tread contact and FX
            # coordinates are unchanged, including slip and contact minima.
            o.keyframe_insert('rotation_quaternion' if o.rotation_mode=='QUATERNION' else 'rotation_euler',frame=f)
        bpy.context.view_layer.update()
        for o,target in zip(wheels,worlds):errors.append(max(abs(o.matrix_world[a][b]-target[a][b]) for a in range(4) for b in range(4)))
        delta=wheels[0].location-Vector((0,-.3548780083656311,-.5970271825790405))
        displacements.append(list(delta))
    # One linear shape basis per axis, with all values keyed. Limited to lower
    # fork/fender near axle; validate the actual axle attachment in renders.
    for o,sk in parts:
        basis=o.data.shape_keys.key_blocks[0]
        for axis in range(3):
            shape=sk if axis==0 else o.shape_key_add(name='317 fork axis '+str(axis))
            for p,base in zip(shape.data,basis.data):
                q=o.matrix_local@base.co;weight=1-m.ease((q.z+.48)/.38)
                d=Vector((0,0,0));d[axis]=weight
                p.co=base.co+o.matrix_local.to_3x3().inverted()@d
            shape.slider_min=-1
            for f,delta in enumerate(displacements,1):shape.value=delta[axis];shape.keyframe_insert('value',frame=f)
    if max(errors)>2e-5:raise ValueError('Wheel world transform changed')
    actual=np.array([r[0].z+m.travel_response((i)/24*m.RATE)*(z[i]-r[0].z) for i,r in enumerate(rows)])
    (out/'suspension.json').write_text(json.dumps({'maximum_wheel_matrix_error':max(errors),'maximum_axle_compliance':np.max(np.abs(displacements),axis=0).tolist(),'opening_original_z_acceleration_rms':float(np.sqrt(np.mean(np.diff([r[0].z for r in rows[:90]],2)**2))),'opening_new_z_acceleration_rms':float(np.sqrt(np.mean(np.diff(actual[:90],2)**2))),'stop_protected_source_interval':[5.3,19.8],'qualification':'shot-authored offline chassis response; not physical suspension solver'},indent=2))

def horse(out):
    import sikh315_scene as prior
    # Old helper carries a shader postlude for its historical material. Keep
    # that compatibility scratch unassigned; preserve current region slots.
    if not bpy.data.materials.get('297 silver dapple coat'):
        legacy=bpy.data.objects['horse'].data.materials[0].copy();legacy.name='297 silver dapple coat'
    before=prior.m;prior.m=m
    try:prior.horse(out)
    finally:prior.m=before
    from sikh305_impacts import build_impacts
    build_impacts(out,event_definitions=[('spear',14.28,None,.20),('grip-left',14.62,'DEF-f_toe.L',.16),('grip-right',14.92,'DEF-f_toe.R',.16),('hind-drive-left',15.02,'DEF-r_toe.L',.35),('hind-drive-right',15.06,'DEF-r_toe.R',.35),('landing-left',17.10,'DEF-f_toe.L',1.),('landing-right',17.14,'DEF-f_toe.R',.85)],follow_terrain=True)

def crowd(out,bake=True):
    from sikh297_layers import baked_limb
    s=bpy.context.scene;s.frame_set(1)
    road=bpy.data.objects['irregular packed farm track'];ground=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    roots=sorted([o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:int(o.name.split()[-1]))
    report=[]
    for i,r in enumerate(roots):
        s.frame_set(1);origin=r.location.copy();side=-1 if i%2 else 1
        uppers=sorted([o for o in r.children if o.name.startswith('PROXY thigh')],key=lambda o:o.name)
        lowers=sorted([o for o in r.children if o.name.startswith('PROXY calf')],key=lambda o:o.name)
        feet=sorted([o for o in r.children if o.name.startswith('PROXY boot')],key=lambda o:o.name)
        head=next(o for o in r.children if o.name.startswith('secondary adult head'))
        crown=next(o for o in r.children if o.name.startswith('secondary facial and crown frame'))
        headrest=head.rotation_euler.copy();crownrest=crown.rotation_euler.copy()
        for f in range(1,697):
            s.frame_set(f);t=(f-1)/24*m.RATE;a=m.crowd_step(t,i,0);b=m.crowd_step(t,i,1);dx=(a[0]+b[0])/2
            start=a[3];anticipation=m.bump(t,start-.55,start-.18,start+.05,start+.5)
            sway=.010*(a[2]-b[2]);travel=m.ease((t-start)/2.3)
            r.location=origin+Vector((side*dx+sway,-.12*travel,-.025*max(a[2],b[2])))
            r.rotation_euler=(.012*max(a[2],b[2]),side*(.045*anticipation+.025*(a[2]-b[2])),side*.18*travel)
            bpy.context.view_layer.update();targets=[]
            for k in range(2):
                st,lf,_,_= (a,b)[k];foot_world=origin+Vector(((-.11 if k==0 else .11)+side*st,-.025-.12*travel,.055+lf))
                # Forward/back position changes only during a foot swing.
                foot_world.y=origin.y-.025-.12*(st/1.7)
                support=ground.ray_cast(foot_world+Vector((0,0,5)),Vector((0,0,-1)))[0]
                if support is None:raise ValueError('Crowd foot lacks support')
                foot_world.z=support.z+(.055+lf)*r.scale.z
                targets.append(foot_world)
            # Solve pelvis height against both planted/swinging feet, including
            # the crossing's real ground. Never stretch a limb to preserve an
            # arbitrary root height over a ditch or rotated torso.
            for _ in range(12):
                bpy.context.view_layer.update();inv=r.matrix_world.inverted()
                excess=max((inv@p-Vector((-.11 if k==0 else .11,0,.84))).length-.885 for k,p in enumerate(targets))
                if excess<=0:break
                r.location.z-=excess*1.3*r.scale.z
            key(r,f);bpy.context.view_layer.update();inv=r.matrix_world.inverted()
            for k,(up,lo,foot) in enumerate(zip(uppers,lowers,feet)):
                p=inv@targets[k];hip=Vector((-.11 if k==0 else .11,0,.84));lf=(a,b)[k][1]
                knee=joint_between(hip,p,.45,.45,(0,-1,0));segment(up,hip,knee,.074);segment(lo,knee,p,.057);foot.location=p
                foot.rotation_euler=(-.18*lf/.085,0,-r.rotation_euler.z)
                for o in (up,lo,foot):key(o,f)
            gaze=side*(.18*m.bump(t,start-.7,start-.2,start+1,start+2.5)-.22*m.ease((t-22.0)/.8))
            head.rotation_euler=headrest;head.rotation_euler.z+=gaze;head.rotation_euler.x+=.025*anticipation;key(head,f)
            crown.rotation_euler=crownrest;crown.rotation_euler.z+=gaze;crown.rotation_euler.x+=.025*anticipation;key(crown,f)
        old=[o for o in r.children if o.name.startswith(('297 continuous crowd trousers','300 supported crowd trousers'))]
        mat=old[0].data.materials[0]
        for o in old:o.hide_render=True;o.hide_viewport=True
        if bake:
            for up,lo in zip(uppers,lowers):baked_limb(r,up,lo,(.074,.057),(.087,.072,.049),mat,'317 planted crowd trousers')
        report.append({'actor':r.name,'start_source_seconds':m.crowd_step(0,i,0)[3],'destination_offset':[side*1.7,-.12,0],'feet':'world-anchored during stance; local IK and rebaked trousers'})
    (out/'crowd.json').write_text(json.dumps(report,indent=2))

def coat(out):
    body=bpy.data.objects['horse'];mat=body.data.materials[0].copy();mat.name='317 silver coat with short nap';body.data.materials[0]=mat
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF']
    b.inputs['Roughness'].default_value=.77;b.inputs['Specular IOR Level'].default_value=.24;b.inputs['Sheen Weight'].default_value=.32;b.inputs['Sheen Roughness'].default_value=.85
    # Restore a natural small-scale coat, not the cloudy stone-like macro noise.
    ramps=[x for x in n if x.type=='VALTORGB']
    for ramp in ramps:
        ramp.color_ramp.elements[0].color=(.235,.225,.20,1);ramp.color_ramp.elements[-1].color=(.32,.31,.28,1)
    rng=np.random.default_rng(317);vs=[];fs=[];weights=[]
    polys=[p for p in body.data.polygons if p.material_index==0]
    groups={g.index:g.name for g in body.vertex_groups}
    # Native short nap shares each sampled vertex's actual armature weights.
    # Exclude material-separated eyes, mouth and hooves; no static floating fur.
    for _ in range(24000):
        p=polys[int(rng.integers(len(polys)))];v=body.data.vertices[p.vertices[int(rng.integers(len(p.vertices)))]]
        normal=v.normal.normalized();tangent=Vector((0,1,-.20));tangent-=normal*tangent.dot(normal)
        if tangent.length<.01:continue
        tangent.normalize();side=normal.cross(tangent);length=float(rng.uniform(.004,.009));base=v.co+normal*.0004;q=len(vs)
        width=float(rng.uniform(.00045,.001));tip=base+tangent*length+normal*length*.23
        vs.extend([base-side*width,base+side*width,tip]);fs.append((q,q+1,q+2));weights.append((q,[(groups[g.group],g.weight) for g in v.groups if g.group in groups]))
    fur=mesh('317 rig-bound short horse nap',vs,fs,mat);fur.parent=body.parent;fur.matrix_parent_inverse=body.matrix_parent_inverse.copy();fur.matrix_basis=body.matrix_basis.copy()
    for g in body.vertex_groups:fur.vertex_groups.new(name=g.name)
    for q,ww in weights:
        for name,w in ww:fur.vertex_groups[name].add([q,q+1,q+2],w,'REPLACE')
    for mod in body.modifiers:
        if mod.type=='ARMATURE':new=fur.modifiers.new('317 shared coat deformation','ARMATURE');new.object=mod.object;new.use_deform_preserve_volume=mod.use_deform_preserve_volume
    (out/'coat.json').write_text(json.dumps({'triangles':len(fs),'length_m':[.004,.009],'rights':'derivative of existing admitted local horse; no external input','weights':'sampled from underlying horse mesh','exclusions':'eyes mouth hooves by material'},indent=2))

def ditch(out,seed=3175,count=2600):
    from sikh315_scene import noise
    road=bpy.data.objects['irregular packed farm track'];ground=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons]);rng=np.random.default_rng(seed)
    mats=[surface('317 drainage growth '+str(i),[a,b],25,rough=.97,bump=.0002) for i,(a,b) in enumerate([((.085,.069,.031),(.24,.19,.09)),((.04,.05,.017),(.10,.13,.035)),((.05,.034,.019),(.14,.095,.04))])]
    vs=[];fs=[];inds=[];roots=0
    for i in range(count):
        y=float(rng.uniform(-170,80));side=-1 if i%2 else 1
        if -30<y<-6 or noise(side*8,y,.19)<-.08:continue
        x=side*float(rng.uniform(2.2,3.9));p=ground.ray_cast(Vector((x,y,9)),Vector((0,0,-1)))[0]
        if p is None or p.z>.25:continue
        roots+=1
        for j in range(int(rng.integers(5,16))):
            a=float(rng.uniform(0,math.tau));h=float(rng.uniform(.07,.29));w=float(rng.uniform(.002,.008));q=len(vs);d=Vector((math.cos(a),math.sin(a),0));across=Vector((-d.y,d.x,0))*w
            base=p+d*float(rng.uniform(0,.08));hit=ground.ray_cast(base+Vector((0,0,2)),Vector((0,0,-1)))[0]
            if hit is None:continue
            base=hit;mid=base+d*h*.4+Vector((0,0,h*.65));tip=base+d*h*.85+Vector((0,0,h*(.5 if j%3 else 1)))
            vs.extend([base-across,base+across,mid+across*.6,mid-across*.6,tip]);fs.extend([(q,q+1,q+2,q+3),(q+3,q+2,q+4)]);inds.extend([i%3,i%3])
    ob=mesh('317 clustered drainage reeds and broken straw',vs,fs,mats[0])
    for mat in mats[1:]:ob.data.materials.append(mat)
    for p,i in zip(ob.data.polygons,inds):p.material_index=i
    (out/'ditch.json').write_text(json.dumps({'grounded_clusters':roots,'faces':len(fs),'lane_geometry_changed':False,'occupied_crossing_excluded':[-30,-6]},indent=2))

def build(out):
    for p in SOURCE.parent.glob('*.json'):
        if p.name not in ('job.json','bindings.json'):shutil.copy2(p,out/p.name)
    crops=[o for o in bpy.data.objects if o.name.startswith(('304 cultivated','305 departure parcel','304 boundary tree'))]
    hidden=[(o,o.hide_viewport) for o in crops]
    for o,_ in hidden:o.hide_viewport=True
    suspension(out);print('317 suspension complete',flush=True)
    horse(out);print('317 horse complete',flush=True)
    crowd(out);print('317 crowd complete',flush=True)
    coat(out);ditch(out)
    for o,value in hidden:o.hide_viewport=value
    # Every newly sampled object/shape trajectory uses the declared samples,
    # not unconstrained Bezier handles between those samples.
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for p in fc.keyframe_points:
                            if 'hide_' not in fc.data_path:p.interpolation='LINEAR'
    bpy.context.scene.frame_set(1)
