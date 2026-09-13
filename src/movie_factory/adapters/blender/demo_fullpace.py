"""Bounded existing-fixture full-pace diagnostics; no runtime code input."""
from pathlib import Path
import bpy
BASE=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01/realism-motion')
SHA='37594a7ef2d59e5dcc9af42c332f28ab41e86e78f78a60e6bd5ff9e2a7ca961e'

def audit(mf,out,job,helper):
    if set(job)!={'mode','output_dir','profile'} or job['mode']!='demo_fullpace_audit' or job['profile']!={}:raise ValueError('Fixed audit required')
    out=Path(out).resolve()
    if BASE.parent.resolve() not in out.parents:raise ValueError('Output outside diagnostic runs')
    helper._file(BASE/'scene.blend',SHA);bpy.ops.wm.open_mainfile(filepath=str(BASE/'scene.blend'),use_scripts=False,load_ui=False)
    scene=bpy.context.scene;horse=bpy.data.objects['horse.rig'];path=bpy.data.objects['horse diagnostic path'];path.animation_data.action=None;path.location=(0,0,0)
    for tr in horse.animation_data.nla_tracks:
        if tr.name.startswith('HoofContactOverlay'):tr.mute=True
    ik=[{'bone':pb.name,'ik_stretch':pb.ik_stretch,'props':{k:str(pb[k]) for k in pb.keys() if 'stretch' in k.lower()},'constraints':[{'type':c.type,'name':c.name,'use_stretch':getattr(c,'use_stretch',None)} for c in pb.constraints if c.type in ('IK','STRETCH_TO')]} for pb in horse.pose.bones if pb.ik_stretch or any(c.type in ('IK','STRETCH_TO') for c in pb.constraints)]
    poses=[]
    for frame in (0,2,5,8,10):
        helper._refresh(scene,mf,frame)
        names=[p.name for p in horse.pose.bones if any(s in p.name.lower() for s in ('tail','torso','thigh','shin','forefoot','hind_foot','upper_arm','forearm','shoulder','hip'))]
        bones={name:{'head':list(horse.matrix_world@horse.pose.bones[name].head),'tail':list(horse.matrix_world@horse.pose.bones[name].tail),'parent':horse.pose.bones[name].parent.name if horse.pose.bones[name].parent else None,'constraints':[{'type':c.type,'influence':c.influence,'target':getattr(getattr(c,'target',None),'name',None),'subtarget':getattr(c,'subtarget',None)} for c in horse.pose.bones[name].constraints]} for name in names}
        poses.append({'frame':frame,'bones':bones,'hooves':helper.hoof_surfaces(bpy.context.evaluated_depsgraph_get())})
    mf.write_json(out/'audit.json',{'source_sha256':SHA,'horse_matrix':[list(row) for row in horse.matrix_world],'poses':poses,'ik':ik})
    return ['audit.json']

def build(mf,out,job,helper):
    import importlib.util,math,time
    from mathutils import Matrix,Vector
    if set(job)!={'mode','output_dir','profile'} or job['mode'] not in ('demo_fullpace_probe','demo_fullpace_motion') or job['profile']!={}:raise ValueError('Fixed fullpace job required')
    out=Path(out).resolve()
    if BASE.parent.resolve() not in out.parents:raise ValueError('Output outside diagnostic runs')
    helper._file(BASE/'scene.blend',SHA);bpy.ops.wm.open_mainfile(filepath=str(BASE/'scene.blend'),use_scripts=False,load_ui=False)
    spec=importlib.util.spec_from_file_location('fullpace_math',Path(__file__).with_name('fullpace_math.py'));motion=importlib.util.module_from_spec(spec);spec.loader.exec_module(motion)
    scene=bpy.context.scene;horse=bpy.data.objects['horse.rig'];path=bpy.data.objects['horse diagnostic path']
    for tr in horse.animation_data.nla_tracks:
        if tr.name.startswith('HoofContactOverlay'):tr.mute=True
    path.animation_data.action=path.animation_data.action.copy()
    for fc in mf.action_channels(path.animation_data.action):
        if fc.data_path=='location' and fc.array_index==1:
            for k in fc.keyframe_points:k.co.y=-motion.SPEED*k.co.x/24
    helper._refresh(scene,mf,0)
    adjust=bpy.data.objects.new('fullpace body travel',None);scene.collection.objects.link(adjust)
    obj=bpy.data.objects['realism speed compensation'];world=obj.matrix_world.copy();obj.parent=adjust;obj.matrix_world=world
    for pb in horse.pose.bones:
        pb.ik_stretch=0
        for constraint in pb.constraints:
            if constraint.type=='IK':constraint.use_stretch=False
    zkeys=[]
    for tick in range(241):
        f=tick/4;helper._refresh(scene,mf,f);z=(horse.matrix_world@horse.pose.bones['torso'].head).z
        zkeys.append((f,1.32+motion.body_z(f/24)-z))
    for f,z in zkeys:
        path.location.z=z;path.keyframe_insert('location',index=2,frame=f)
        adjust.location=(0,-(motion.SPEED-6.47)*f/24,z);adjust.keyframe_insert('location',frame=f)
    for obj in (path,adjust):
        for fc in mf.action_channels(obj.animation_data.action):
            for key in fc.keyframe_points:
                key.interpolation='LINEAR' if fc.array_index==1 else 'BEZIER';key.handle_left_type=key.handle_right_type='AUTO_CLAMPED'
    controls={'LH':('hind_foot_ik.L','DEF-r_hoof.L',.5),'RH':('hind_foot_ik.R','DEF-r_hoof.R',2.25),'LF':('forefoot_ik.L','DEF-f_hoof.L',4),'RF':('forefoot_ik.R','DEF-f_hoof.R',5.5)}
    rotations={};sole_depth={}
    for leg,(name,group,f) in controls.items():
        helper._refresh(scene,mf,f);rotations[leg]=horse.pose.bones[name].matrix.to_quaternion();h=helper.hoof_surfaces(bpy.context.evaluated_depsgraph_get())[group];sole_depth[leg]=h['center'][2]-h['min_z']+.003
    # Coordinate the additional paw/heel controls with the authored contact clock.
    source_windows={'LH':(9.125,12.46875),'RH':(1.34375,3.375),'LF':(2.4375,5.46875),'RF':(3.5,7.3125)}
    heel_names={leg:name.replace('_ik.','_heel_ik.') for leg,(name,_,_) in controls.items()}
    for name in heel_names.values():
        if name not in horse.pose.bones:raise ValueError('Required existing heel control missing: '+name)
    library={leg:[] for leg in controls}
    for tick in range(81):
        helper._refresh(scene,mf,tick/8)
        for leg,(name,_,_) in controls.items():library[leg].append((horse.pose.bones[name].matrix.to_quaternion().copy(),horse.pose.bones[heel_names[leg]].matrix_basis.copy()))
    def reference(leg,f):
        phase=(f/10-motion.TOUCHDOWN[leg])%1;a,b=source_windows[leg]
        t=(a+(b-a)*phase/motion.DUTY) if phase<=motion.DUTY else (b+(10-(b-a))*(phase-motion.DUTY)/(1-motion.DUTY))
        x=(t%10)*8;i=min(int(x),79);w=x-i
        q0,m0=library[leg][i];q1,m1=library[leg][i+1]
        return q0.slerp(q1,w),m0.lerp(m1,w)
    limb_names=[p.name for p in horse.pose.bones if p.name.startswith(('DEF-thigh','DEF-lower_leg','DEF-hind_foot','DEF-upper_arm','DEF-forearm','DEF-forefoot','DEF-r_hoof','DEF-f_hoof'))]
    records=[];length_ratios=[];errors=[]
    for tick in range(81):
        f=tick/8;helper._refresh(scene,mf,f);baseline={n:(horse.pose.bones[n].tail-horse.pose.bones[n].head).length for n in limb_names}
        targets={}
        for leg,(name,group,_) in controls.items():
            pb=horse.pose.bones[name];rotation,heel=reference(leg,f);hp=horse.pose.bones[heel_names[leg]];hp.rotation_mode='QUATERNION';hp.matrix_basis=heel;pb.rotation_mode='QUATERNION';mat=pb.matrix.copy();mat=Matrix.LocRotScale(mat.translation,rotation,mat.to_scale());pb.matrix=mat
            p,supported=motion.target(f/24,leg);targets[leg]=Vector((p[0],p[1],p[2]+sole_depth[leg]))
        bpy.context.view_layer.update()
        for attempt in range(3):
            hooves=helper.hoof_surfaces(bpy.context.evaluated_depsgraph_get())
            for leg,(name,group,_) in controls.items():
                pb=horse.pose.bones[name];lift,_=motion.target(f/24,leg);targets[leg].z=lift[2]+hooves[group]['center'][2]-hooves[group]['min_z']+.003;delta=targets[leg]-Vector(hooves[group]['center']);mat=pb.matrix.copy();mat.translation+=horse.matrix_world.inverted().to_3x3()@delta;pb.matrix=mat
            bpy.context.view_layer.update()
        hooves=helper.hoof_surfaces(bpy.context.evaluated_depsgraph_get())
        for leg,(name,group,_) in controls.items():
            pb=horse.pose.bones[name];records.append((f,name,tuple(pb.location),tuple(pb.rotation_quaternion)));hp=horse.pose.bones[heel_names[leg]];records.append((f,hp.name,tuple(hp.location),tuple(hp.rotation_quaternion)))
            errors.append({'frame':f,'leg':leg,'error_m':(Vector(hooves[group]['center'])-targets[leg]).length})
        length_ratios.extend({'frame':f,'bone':n,'ratio':(horse.pose.bones[n].tail-horse.pose.bones[n].head).length/baseline[n]} for n in limb_names if baseline[n]>1e-6)
    # Local IK channels repeat with the 10-frame source/reference clock.
    first_cycle=[r for r in records if r[0]<10];records=[(f+10*cycle,n,loc,q) for cycle in range(6) for f,n,loc,q in first_cycle]+[(60,n,loc,q) for f,n,loc,q in first_cycle if f==0]
    mf.write_json(out/'authoring.json',{'records':records,'zkeys':zkeys})
    action=bpy.data.actions.new('authored fullpace gait');slot=action.slots.new(id_type='OBJECT',name=horse.name);layer=action.layers.new('Authored existing IK');bag=layer.strips.new(type='KEYFRAME').channelbag(slot,ensure=True)
    for name in sorted({row[1] for row in records}):
        rows=[r for r in records if r[1]==name]
        prev=None
        for i,(f,n,loc,q) in enumerate(rows):
            if prev and sum(a*b for a,b in zip(prev,q))<0:q=tuple(-x for x in q);rows[i]=(f,n,loc,q)
            prev=q
        for prop,count,col in (('location',3,2),('rotation_quaternion',4,3)):
            for axis in range(count):
                fc=bag.fcurves.new(horse.pose.bones[name].path_from_id(prop),index=axis)
                for row in rows:
                    k=fc.keyframe_points.insert(row[0],row[col][axis]);k.interpolation='BEZIER';k.handle_left_type=k.handle_right_type='AUTO_CLAMPED'
    track=horse.animation_data.nla_tracks.new();track.name='authored fullpace';strip=track.strips.new(action.name,0,action);strip.action_slot=slot;strip.blend_type='REPLACE';strip.extrapolation='NOTHING'
    spans={};slip=0;penetration=0;dense=[]
    for tick in range(257):
        f=10*tick/256;helper._refresh(scene,mf,f);h=helper.hoof_surfaces(bpy.context.evaluated_depsgraph_get());dense.append({'frame':f,'hooves':h})
        for n,p in h.items():
            penetration=max(penetration,-p['min_z'])
            if p['min_z']<=.04:
                spans.setdefault(n,p['center']);start=spans[n];slip=max(slip,math.hypot(p['center'][0]-start[0],p['center'][1]-start[1]))
            else:spans.pop(n,None)
    result={'source_scene_sha256':SHA,'speed_mps':motion.SPEED,'stride_m':motion.SPEED/motion.FREQUENCY,'frequency_hz':motion.FREQUENCY,'authored_gait':True,'max_target_error_m':max(x['error_m'] for x in errors),'worst_target':max(errors,key=lambda x:x['error_m']),'deform_length_ratio_min':min(x['ratio'] for x in length_ratios),'deform_length_ratio_max':max(x['ratio'] for x in length_ratios),'worst_length_ratios':sorted(length_ratios,key=lambda x:abs(x['ratio']-1),reverse=True)[:12],'max_stance_excursion_m':slip,'max_penetration_m':penetration,'dense_samples':dense,'render_seconds':{},'limits':{'target_error_m':.05,'stance_excursion_m':.05,'penetration_m':.02,'length_ratio_min':.97,'length_ratio_max':1.03}}
    result['pass']=result['max_target_error_m']<=.05 and slip<=.05 and penetration<=.02 and result['deform_length_ratio_min']>=.97 and result['deform_length_ratio_max']<=1.03
    mf.write_json(out/'checks.json',result)
    if job['mode']=='demo_fullpace_motion' and not result['pass']:raise ValueError('Authored gait failed preflight; full render blocked')
    scene.render.resolution_x=512;scene.render.resolution_y=288;scene.cycles.samples=6
    # The road must cover the 30m full-pace preview; scenery remains diagnostic.
    bpy.data.objects['diagnostic road'].scale.y=40
    frames=sorted(set((0,3,7,round(result['worst_target']['frame'])))) if job['mode']=='demo_fullpace_probe' else range(60)
    for name in ('lateral','threequarter'):
        scene.camera=bpy.data.objects[name];folder=out/'renders'/name;folder.mkdir(parents=True,exist_ok=True);result['render_seconds'][name]=[]
        for f in frames:
            helper._refresh(scene,mf,f);scene.render.filepath=str(folder/f'{f:04d}.png');t=time.perf_counter();bpy.ops.render.render(write_still=True);result['render_seconds'][name].append(time.perf_counter()-t);mf.write_json(out/'checks.json',result)
    return ['checks.json','renders']
