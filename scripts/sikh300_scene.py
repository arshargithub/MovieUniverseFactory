"""Reviewed300 derivative construction; no source overwrites."""
import math,json
import bpy
import numpy as np
from mathutils import Vector,Matrix,Quaternion
from sikh257_native import mesh,material,sphere
from sikh257_layout import key,tube
from movie_factory.sikh300_motion import FPS,FRAMES,RATE
from movie_factory.sikh291_motion import rear_amount,ease

def stop(out):
    import sikh299_scene as prior
    import movie_factory.sikh300_motion as curves
    # Reviewed reuse with explicit curve ownership; no legacy module writes.
    for name in ('travel','yaw','lean','slip','rear_distance'):setattr(prior,name,getattr(curves,name))
    for o in list(bpy.data.objects):
        if o.name.startswith(('299 tire-contact','299 ground-integrated','299 front tread','299 rear tread')):bpy.data.objects.remove(o,do_unlink=True)
    trace=prior.motion(out);prior.greeting_eyeline(out);prior.contact(out,trace)
    return trace

def crowd(out):
    from sikh292_assets import surface
    from sikh297_layers import baked_limb
    from sikh257_layout import segment
    from movie_factory.sikh257_geometry import joint_between
    from movie_factory.sikh300_motion import ground_height
    s=bpy.context.scene;s.frame_set(1);rng=np.random.default_rng(300)
    steel=surface('300 forged crowd steel',[(.035,.041,.046),(.25,.28,.29)],18,rough=.42,bump=.0006);steel.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.72
    leather=surface('300 crowd dark hide',[(.018,.012,.008),(.09,.055,.027)],12,bump=.001)
    roots=sorted([o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:int(o.name.rsplit(' ',1)[1]));rows=[]
    for i,root in enumerate(roots):
        s.frame_set(1);mat=next(o for o in root.children if o.name.startswith('secondary chola')).data.materials[0]
        # Individual proportion variation stays modest and adult; mounted leader untouched.
        head=next(o for o in root.children if o.name.startswith('secondary adult head'))
        crown=next(o for o in root.children if o.name.startswith('secondary facial and crown'))
        sx=.94+.025*(i%5)
        for ob in (head,crown):ob.scale.x*=sx;ob.scale.y*=.98+.018*(i%3)
        # Flat-backed round shields, steel bosses, sheathed side swords and spear heads.
        if i%3!=1:
            ob=sphere('300 round hide shield',(-.27,.14,1.03),(.22,.045,.22),leather);ob.parent=root
            for a in np.linspace(0,math.tau,5)[:-1]:
                ob=sphere('300 shield steel boss',(-.27+.085*math.cos(a),.188,1.03+.085*math.sin(a)),(.022,.012,.022),steel);ob.parent=root
        tube('300 sheathed crowd sword',[(.19,.02,.89),(.25,.04,.62),(.29,.08,.31)],.019,leather,root)
        tube('300 sword crossguard',[(.13,.02,.91),(.25,.02,.91)],.01,steel,root)
        ob=mesh('300 leaf spearhead',[(.30,0,2.12),(.255,0,2.24),(.30,0,2.43),(.345,0,2.24),(.30,.018,2.24)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],steel);ob.parent=root
        # Off-axis quiet cloth finish and sash ends replace featureless repetition.
        trim=surface('300 faded saffron '+str(i),[(.13,.069,.018),(.40,.235,.06)],9,bump=.001)
        vs=[];fs=[]
        for j in range(13):
            u=j/12
            for k in range(7):v=k/6;vs.append((.12+(v-.5)*.085+.025*math.sin(u*3+i),-.17-.012*math.sin(u*5),.89-u*(.37+.03*(i%3))+.014*math.sin(v*math.pi*4)))
            if j:
                for k in range(6):q=j*7+k;fs.append((q-7,q-6,q+1,q))
        ob=mesh('300 loose woven sash end',vs,fs,trim);ob.parent=root
        uppers=sorted([o for o in root.children if o.name.startswith('PROXY thigh')],key=lambda o:o.name);lowers=sorted([o for o in root.children if o.name.startswith('PROXY calf')],key=lambda o:o.name);feet=sorted([o for o in root.children if o.name.startswith('PROXY boot')],key=lambda o:o.name)
        # Crowd crosses the swale. Recompute foot heights and hidden leg controls,
        # then rebake their visible trousers; a new terrain invalidates old support.
        for f in range(1,FRAMES+1):
            s.frame_set(f);bpy.context.view_layer.update();basez=ground_height(root.location.x,root.location.y)
            targets=[]
            for k,foot in enumerate(feet):
                p=foot.location.copy();world=root.matrix_world@p;ground=ground_height(world.x,world.y);side=-1 if k==0 else 1
                horizontal=(p.x-side*.11)**2+p.y*p.y
                # Let the pelvis follow the lower support surface through the
                # swale. Do not stretch a planted leg to retain a flat-ground root.
                vertical=math.sqrt(max(.01,.895**2-horizontal))
                basez=min(basez,ground+root.scale.z*(vertical+p.z-.84))
                targets.append((p,ground))
            root.location.z=basez;key(root,f)
            for k,(up,lo,foot) in enumerate(zip(uppers,lowers,feet)):
                side=-1 if k==0 else 1;p,ground=targets[k]
                p.z+=(ground-basez)/root.scale.z
                hip=Vector((side*.11,0,.84));knee=joint_between(hip,p,.45,.45,(0,-1,0));segment(up,hip,knee,.074);segment(lo,knee,p,.057);foot.location=p
                for ob in (up,lo,foot):key(ob,f)
        for ob in list(root.children):
            if ob.name.startswith('297 continuous crowd trousers'):bpy.data.objects.remove(ob,do_unlink=True)
        for up,lo in zip(uppers,lowers):baked_limb(root,up,lo,(.074,.057),(.087,.072,.049),mat,'300 supported crowd trousers')
        rows.append({'root':root.name,'head_width_factor':sx,'ground_support_rebaked':True})
    (out/'crowd.json').write_text(json.dumps(rows,indent=2));s.frame_set(1)

def build(out):
    from sikh300_scene_land import landscape,bike_materials
    landscape();bike_materials()
    # Crop deformation is unrelated to contact authoring. Keep its millions of
    # surface vertices out of viewport dependency evaluation during 528-frame
    # joint solves; restore before saving/rendering. Render density is unchanged.
    crops=[o for o in bpy.data.objects if o.name.startswith('300 rooted wheat')]
    for o in crops:o.hide_viewport=True
    print('300 surfaces built; authoring contacts',flush=True)
    stop(out);print('300 bike complete',flush=True)
    horse(out);print('300 horse complete',flush=True)
    crowd(out);print('300 crowd complete',flush=True)
    for o in crops:o.hide_viewport=False
    s=bpy.context.scene;s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))

def horse(out):
    s=bpy.context.scene;rig=bpy.data.objects['horse.rig'];pivot=bpy.data.objects['HORSE hind support pivot']
    s.frame_set(1);bpy.context.view_layer.update();rows=[]
    # Existing IK heel chain is already visibly folded in the neutral pose.
    # Forelimb FK bypass is an explicit representation control, not more offsets.
    for side in ('L','R'):
        parent=rig.pose.bones['upper_arm_parent.'+side];parent['IK_FK']=1.;parent.keyframe_insert(data_path='["IK_FK"]',frame=1)
        # Source257 cleared animation_data wholesale, which also deleted Rigify
        # drivers. Merely changing IK_FK therefore does nothing. Explicitly bind
        # the four ORG fore-chain copy constraints to their existing FK targets.
        for name in ('upper_arm','forearm','forefoot','f_toe'):
            pb=rig.pose.bones.get('ORG-'+name+'.'+side)
            if pb:
                for c in pb.constraints:
                    if c.type=='COPY_TRANSFORMS':c.influence=1. if '_fk.' in c.subtarget else 0.
    for f in range(1,FRAMES+1):
        s.frame_set(f);t=(f-1)/FPS*RATE;a=rear_amount(t)
        for side in ('L','R'):
            # Articulation in armature coordinates: shoulder sweeps forward,
            # carpus folds back under the chest, hoof hangs rather than reversing.
            for name,angle in [('upper_arm_fk',-.65*a),('forearm_fk',2.40*a),('forefoot_fk',-.60*a),('f_toe_fk',.12*a)]:
                pb=rig.pose.bones[name+'.'+side];pb.rotation_mode='QUATERNION'
                rest=pb.bone.matrix_local.to_3x3();axis=rest.inverted()@Vector((1,0,0))
                pb.rotation_quaternion=Quaternion(axis,angle);pb.keyframe_insert('rotation_quaternion',frame=f)
        bpy.context.view_layer.update()
        rows.append({'frame':f,'rear':a,'fore_joint_positions':{n:list(rig.matrix_world@rig.pose.bones[n].head) for n in ('DEF-upper_arm.L','DEF-forearm.L','DEF-forefoot.L','DEF-f_toe.L') if n in rig.pose.bones}})
    (out/'horse-trace.json').write_text(json.dumps(rows,indent=2))
    s.frame_set(1)

def hind_support(out):
    """Keep the hoof frame planted, not merely its animated IK translation."""
    s=bpy.context.scene;rig=bpy.data.objects['horse.rig'];s.frame_set(1);bpy.context.view_layer.update()
    targets={name:(rig.matrix_world@rig.pose.bones[name].matrix).copy() for name in ('hind_foot_ik.L','hind_foot_ik.R')}
    for f in range(1,FRAMES+1):
        s.frame_set(f);bpy.context.view_layer.update()
        for name,world in targets.items():
            pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=rig.matrix_world.inverted()@world
            pb.keyframe_insert('location',frame=f);pb.keyframe_insert('rotation_quaternion',frame=f)
    (out/'hind-support.json').write_text(json.dumps({'cause':'Inherited pose handler keyed rotation_quaternion while feet remained XYZ. Explicit quaternion mode preserves the complete world hoof frame through rear.','target_world':{n:list(map(list,m)) for n,m in targets.items()}},indent=2));s.frame_set(1)
