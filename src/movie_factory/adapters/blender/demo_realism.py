"""Fixed, script-disabled diagnostics for the Director's existing-asset realism repair."""
import json
from pathlib import Path
import bpy
from mathutils import Vector
BASE=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01/free-motion-v2-retry')
SHA='32518f65560d6bdf9c08d200dbc4061e8fd890e4fe768d83d598dfd7b001a174'

def audit(mf,out,job,helper):
    if set(job)!={'mode','output_dir','profile'} or job['mode']!='demo_realism_audit' or job['profile']!={}:raise ValueError('Fixed audit job required')
    out=Path(out).resolve();root=BASE.parent.resolve()
    if root not in out.parents:raise ValueError('Output outside diagnostic runs')
    helper._file(BASE/'scene.blend',SHA)
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'scene.blend'),use_scripts=False,load_ui=False)
    scene=bpy.context.scene;scene.frame_set(59);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    cam=bpy.data.objects['threequarter'];origin=cam.matrix_world.translation
    rays=[]
    for name in ('horse','Man','Helmet','saddle'):
        lo,hi=helper._bbox(bpy.data.objects[name],deps);target=(lo+hi)*.5;delta=target-origin
        hit,location,normal,index,obj,matrix=scene.ray_cast(deps,origin,delta.normalized(),distance=delta.length)
        rays.append({'toward':name,'hit':obj.name if hit else None,'point':list(location) if hit else None,'camera':list(origin)})
    hair=[]
    for obj in scene.objects:
        for ps in obj.particle_systems:
            if ps.name=='horse.tail':
                s=ps.settings;hair.append({'object':obj.name,'system':ps.name,'settings':{n:getattr(s,n) for n in ('count','hair_length','child_type','child_percent','rendered_child_count','root_radius','tip_radius','radius_scale','clump_factor','roughness_1','roughness_2') if hasattr(s,n)}})
    horse=bpy.data.objects['horse.rig'];path=bpy.data.objects['horse diagnostic path']
    for track in horse.animation_data.nla_tracks:
        if track.name.startswith('HoofContactOverlay'):track.mute=True
    path.animation_data.action=None;path.location=(0,0,0)
    samples=[]
    for tick in range(321):
        helper._refresh(scene,mf,tick/32)
        samples.append({'frame':tick/32,'hooves':helper.hoof_surfaces(bpy.context.evaluated_depsgraph_get())})
    mf.write_json(out/'audit.json',{'source_scene_sha256':SHA,'source_samples':samples,'rays_last_frame':rays,'tail':hair,'cycle_frames':10,'fps':24})
    return ['audit.json']

def build(mf,out,job,helper):
    import importlib.util,math,time
    if set(job)!={'mode','output_dir','profile'} or job['mode'] not in ('demo_realism_probe','demo_realism_motion') or job['profile']!={}:raise ValueError('Fixed realism job required')
    out=Path(out).resolve()
    if BASE.parent.resolve() not in out.parents:raise ValueError('Output outside diagnostic runs')
    helper._file(BASE/'scene.blend',SHA);bpy.ops.wm.open_mainfile(filepath=str(BASE/'scene.blend'),use_scripts=False,load_ui=False)
    root=BASE.parents[2];config=json.loads((root/'feasibility/demonstrator-01/realism-config.json').read_text());audit=json.loads((BASE.parent/'realism-audit/audit.json').read_text())
    spec=importlib.util.spec_from_file_location('demo_contact',Path(__file__).with_name('demo_contact.py'));contact=importlib.util.module_from_spec(spec);spec.loader.exec_module(contact)
    scene=bpy.context.scene;horse=bpy.data.objects['horse.rig'];path=bpy.data.objects['horse diagnostic path'];rider=bpy.data.objects['rig'];speed=config['selected_speed_mps'];old_speed=3.454273223876953
    for track in horse.animation_data.nla_tracks:
        if track.name.startswith('HoofContactOverlay'):track.mute=True
    path.animation_data.action=path.animation_data.action.copy()
    for fc in mf.action_channels(path.animation_data.action):
        if fc.data_path=='location' and fc.array_index==1:
            for key in fc.keyframe_points:key.co.y=-speed*key.co.x/24
    helper._refresh(scene,mf,0)
    adjust=bpy.data.objects.new('realism speed compensation',None);scene.collection.objects.link(adjust)
    for name in ('rider normalization','saddle','saddle.pad','saddle.stirrup.strap','saddle.stirrup','Torus.002','repaired rein L','repaired rein R'):
        obj=bpy.data.objects[name]
        if obj.parent is None:
            world=obj.matrix_world.copy();obj.parent=adjust;obj.matrix_world=world
    for frame in (0,60):adjust.location.y=-(speed-old_speed)*frame/24;adjust.keyframe_insert('location',frame=frame)
    for fc in mf.action_channels(adjust.animation_data.action):
        for key in fc.keyframe_points:key.interpolation='LINEAR'
    rider.animation_data.action=rider.animation_data.action.copy()
    head_channels=0
    for fc in mf.action_channels(rider.animation_data.action):
        if fc.data_path=='pose.bones["head"].scale':
            for key in fc.keyframe_points:key.co.y*=config['preview_head_scale'];key.handle_left.y*=config['preview_head_scale'];key.handle_right.y*=config['preview_head_scale']
            head_channels+=1
    if head_channels!=3:raise ValueError('Expected three admitted head scale channels')
    for ps in bpy.data.objects['horse'].particle_systems:
        if ps.name=='horse.tail':
            ps.settings=ps.settings.copy();s=ps.settings;s.rendered_child_count=12;s.child_percent=12;s.clump_factor=.18;s.roughness_1=.018;s.roughness_2=.009;s.root_radius=.035;s.tip_radius=.001;s.radius_scale=.012;ps.use_hair_dynamics=False
    bpy.data.objects['Icosphere.001'].location.x=18
    controls={'DEF-r_hoof.L':'hind_foot_ik.L','DEF-r_hoof.R':'hind_foot_ik.R','DEF-f_hoof.L':'forefoot_ik.L','DEF-f_hoof.R':'forefoot_ik.R'}
    records=[];maximum=0
    samples=audit['source_samples']
    for tick in range(481):
        frame=tick/8;helper._refresh(scene,mf,frame)
        for name,control in controls.items():
            def trajectory(t):
                index=min(int(t*32),319);w=t*32-index;x=samples[index]['hooves'][name]['center'];y=samples[index+1]['hooves'][name]['center'];return tuple(x[i]*(1-w)+y[i]*w for i in range(3))
            delta=contact.offset(frame%10,trajectory,*config['intervals'][name],(0,-speed,0),blend=.5);maximum=max(maximum,Vector(delta).length)
            records.append((frame,control,contact.control_delta(horse,horse.pose.bones[control],delta)))
    contact.bake_overlay(horse,records)
    observations=[];rein_gaps=[]
    for tick in range(321):
        frame=tick/16;helper._refresh(scene,mf,frame);deps=bpy.context.evaluated_depsgraph_get();observations.append({'frame':frame,'hooves':helper.hoof_surfaces(deps)})
        for side in ('L','R'):
            hand=rider.pose.bones['hand_fk.'+side];grip=rider.matrix_world@hand.matrix@Vector((0,hand.length*.55,0));obj=bpy.data.objects['repaired rein '+side];point=obj.matrix_world@Vector(obj.data.splines[0].points[-1].co[:3]);rein_gaps.append((point-grip).length)
    slips=[]
    for name in controls:
        span=[]
        for sample in observations+[None]:
            if sample and sample['hooves'][name]['min_z']<=.04:span.append(sample)
            elif span:
                origin=span[0]['hooves'][name]['center'];slips.append(max(math.hypot(x['hooves'][name]['center'][0]-origin[0],x['hooves'][name]['center'][1]-origin[1]) for x in span));span=[]
    result={'source_scene_sha256':SHA,'config':config,'maximum_correction_m':maximum,'max_stance_excursion_m':max(slips),'max_hoof_penetration_m':max(0,-min(h['min_z'] for x in observations for h in x['hooves'].values())),'max_rein_endpoint_error_m':max(rein_gaps),'sample_step':.0625,'sample_frames':[0,20],'tail_policy':'12 interpolated children, reduced roughness/clump, tapered strands, dynamics disabled','head_scale':config['preview_head_scale'],'render_seconds':{},'limitations':['Source-based contact adaptation, not physical simulation.','Source body vertical motion and cadence unchanged.','Head proportion and groom quality require Director review.']}
    mf.write_json(out/'checks.json',result)
    if result['max_stance_excursion_m']>.05 or result['max_hoof_penetration_m']>.02 or result['max_rein_endpoint_error_m']>.01:raise ValueError('Dense contact screens fail; no render')
    occlusions=[]
    for frame in range(60):
        helper._refresh(scene,mf,frame);deps=bpy.context.evaluated_depsgraph_get()
        for camera in ('lateral','threequarter'):
            origin=bpy.data.objects[camera].matrix_world.translation
            for name in ('horse','Man','Helmet','saddle'):
                lo,hi=helper._bbox(bpy.data.objects[name],deps);delta=(lo+hi)*.5-origin
                hit,point,normal,index,obj,matrix=scene.ray_cast(deps,origin,delta.normalized(),distance=delta.length)
                if hit and (obj.name.startswith('Icosphere') or obj.name=='distant tower'):
                    occlusions.append({'frame':frame,'camera':camera,'target':name,'occluder':obj.name})
    result['scenery_center_ray_occlusions']=occlusions
    mf.write_json(out/'checks.json',result)
    if occlusions:raise ValueError('Diagnostic scenery blocks actor center rays')
    frames=(0,3,59) if job['mode']=='demo_realism_probe' else range(60)
    if job['mode']=='demo_realism_motion':
        helper._refresh(scene,mf,0);bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),check_existing=False)
    for name in ('lateral','threequarter'):
        scene.camera=bpy.data.objects[name];folder=out/'renders'/name;folder.mkdir(parents=True,exist_ok=True);result['render_seconds'][name]=[]
        for frame in frames:
            helper._refresh(scene,mf,frame);scene.render.filepath=str(folder/f'{frame:04d}.png');t=time.perf_counter();bpy.ops.render.render(write_still=True);result['render_seconds'][name].append(time.perf_counter()-t);mf.write_json(out/'checks.json',result)
    return ['checks.json','renders']+(['scene.blend'] if job['mode']=='demo_realism_motion' else [])
