"""Fixed, hash-bound cache presentation; no payload paths/code or visual PASS.

Screening a rejected trajectory is a renderer benchmark, not asset approval.
"""
import json
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as recipe

CACHES={'18':'1e8be001ca770fecb986a719b6d04c299b79a0aba66ca0103c2f5c721f153f77'}
OPERATIONS={'screen18':'18','screen18low':'18','screen18clay':'18'}
CACHES['27']='8be01c0558280dd0c323eda50d4b356b8cd35c2f1e90735b694148d51a8c034d'
OPERATIONS['screen27cpu']='27'
OPERATIONS['audit27']='27'
CACHES['36']='3b9cfbf98b16f0420395127de183ce4fc625425c4bfe591bdcfa549c2d47fd94'
OPERATIONS.update({'initial36':'36','uncovered36':'36','initial36b':'36','uncovered36b':'36'})
OPERATIONS['initial38']='36'
OPERATIONS['initial38b']='36'
CACHES['38']='902326a848f7f4f03d0211febc47597275d133314c27aa283cc4b5a8ea8031be'
OPERATIONS['collision39']='38'
OPERATIONS['rig40audit']='38'
OPERATIONS['donor40']='38'
OPERATIONS['donor40b']='38'
OPERATIONS['donor41']='38'
OPERATIONS['hybrid42']='38'
OPERATIONS['hybrid43']='38'
OPERATIONS['hybrid44']='38'
OPERATIONS['hybrid46']='38'
OPERATIONS['hybrid47']='38'


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or not isinstance(job['operation'],str) or job['operation'] not in OPERATIONS:
        raise ValueError('Fixed cache presentation enum only')
    if recipe.SOURCE.is_symlink() or recipe.digest(recipe.SOURCE)!=recipe.SOURCE_SHA:
        raise ValueError('Pinned native foundation mismatch')
    candidate=OPERATIONS[job['operation']]
    cache=recipe.BASE/('wardrobe178-move'+candidate)/'cloth-trajectory.npz'
    if cache.is_symlink() or not cache.is_file() or recipe.digest(cache)!=CACHES[candidate]:
        raise ValueError('Pinned trajectory mismatch')
    out=recipe.BASE/('wardrobe178-'+job['operation'])
    if out.exists() or out.is_symlink():raise ValueError('Never overwrite retained evidence')
    return out,cache


def dress_actor(rig):
    import bpy
    import wardrobe_motion178_controls as controls
    sample=controls.body_weight_sampler()
    # A bust-only screen can hide static lower garments left by the selected
    # pose authoring. Bind those neutral derivatives before whole-body review;
    # do not alter the accepted actor or recompute the cached shawl trajectory.
    trousers=bpy.data.objects['MF_fit_trousers_173_visible']
    lower_target=controls.render_surface_target()
    controls.bind_render_surface(trousers,lower_target)
    for ob in list(bpy.context.scene.objects):
        if ob.name.startswith('MF_173_trouser_outseam'):
            bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
            bpy.context.view_layer.objects.active=ob
            if ob.type=='CURVE':bpy.ops.object.convert(target='MESH')
            controls.bind_render_surface(bpy.context.view_layer.objects.active,lower_target)
        elif ob.name.startswith(('MF_173_work_boot_','MF_173_boot_')):
            side='L' if '_L' in ob.name else 'R' if '_R' in ob.name else None
            if side is None:raise ValueError('Unknown fixed boot-side attachment')
            if any(c.type=='CHILD_OF' and c.target==rig for c in ob.constraints):
                raise ValueError('Unexpected prior rigid boot attachment')
            c=ob.constraints.new('CHILD_OF');c.target=rig;c.subtarget='foot.'+side
            c.inverse_matrix=(rig.matrix_world@rig.pose.bones[c.subtarget].matrix).inverted()
    for name in ('MF_fit_tunic_173_visible','MF_171_fitted_sleeve_L_173_visible',
                 'MF_171_fitted_sleeve_R_173_visible','MF_173_tension_harness_-1',
                 'MF_173_tension_harness_1','MF_173_waist_belt'):
        sampler=(lambda p:{'pelvis':1.}) if name=='MF_173_waist_belt' else sample
        controls.bind(bpy.data.objects[name],rig,sampler)
    for name in ('MF_173_belt_buckle','MF_173_buckle_tongue'):
        ob=bpy.data.objects[name]
        if not any(c.type=='CHILD_OF' and c.target==rig for c in ob.constraints):
            c=ob.constraints.new('CHILD_OF');c.target=rig;c.subtarget='pelvis'
            c.inverse_matrix=(rig.matrix_world@rig.pose.bones['pelvis'].matrix).inverted()
    for ob in bpy.context.scene.objects:
        if '_seam_' in ob.name or 'harness_welt' in ob.name:ob.hide_render=True


def assembly(record,expected_count=3891):
    import bpy
    import numpy as np
    import wardrobe_studio as studio
    import wardrobe_motion178_controls as controls
    from wardrobe_motion178_playback import absolute_cache
    if expected_count not in (3891,3287):raise ValueError('Fixed admitted cloth topology required')
    points=record['constructed_initial'];frames=record['frames'];faces=record['faces']
    if points.shape!=(expected_count,3) or frames.shape!=(192,expected_count,3) or faces.ndim!=2 or faces.shape[1]!=4:
        raise ValueError('Fixed trajectory topology required')
    if not np.isfinite(frames).all() or np.max(np.abs(frames))>100 or faces.min()<0 or faces.max()>=expected_count:
        raise ValueError('Invalid bounded cloth cache')
    rig,mats,_=recipe.clean_foundation();dress_actor(rig)
    controls.animate(rig,neutral_entry=True)
    display=studio.panel('MF178_moving_shawl',[tuple(p) for p in points],
                        [tuple(int(i) for i in f) for f in faces],mats['scarf'],.014,1)
    with controls.render_geometry_paused():absolute_cache(display,frames)
    scene=bpy.context.scene;scene.frame_start=97;scene.frame_end=288;scene.render.fps=24
    matrices=record['chest_matrices']
    if matrices.shape!=(192,4,4) or not np.isfinite(matrices).all():
        raise ValueError('Invalid original body-motion matrices')
    # Reconstruction must carry the same actual actor motion as the cached
    # cloth solve, not merely the same formula or sampled keyframe count.
    with controls.render_geometry_paused():
        # Invisible objects can stop animation evaluation. Keep the inexpensive
        # cached display active while expensive skin/hair remain paused.
        display.hide_viewport=False
        for frame in range(97,289):
            scene.frame_set(frame);bpy.context.view_layer.update()
            if abs(display.data.shape_keys.eval_time-10*(frame-96))>1e-5:
                raise ValueError('Cache time mapping differs at%s: actual%s expected%s'%(frame,display.data.shape_keys.eval_time,10*(frame-96)))
            error=float(np.max(np.abs(np.array(studio.torso_matrix(-1.))-matrices[frame-97])))
            if error>1e-6:raise ValueError('Actor/cache body-motion mismatch at%s: %s'%(frame,error))
    recipe.check_protected()
    return display


def contact_audit(out,cache):
    """Retain actual rendered-skin contact measures, not a visual PASS.

    Local nearest-normal sign is diagnostic on an open surface, not a global
    inside/outside classifier or automatic quality gate.
    """
    import bpy
    import numpy as np
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    if recipe.digest(recipe.CONTROL_LAYOUT)!=recipe.CONTROL_LAYOUT_SHA:
        raise ValueError('Pinned held-border indices mismatch')
    with np.load(recipe.CONTROL_LAYOUT,allow_pickle=False) as record:
        indices=[int(i) for i in record['pin_indices'] if i>=1395]
    scale=bpy.context.scene.unit_settings.scale_length;rows=[]
    with np.load(cache,allow_pickle=False) as record:
        for frame in (97,121,145,193,241,288):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
            skin=tree_for(bpy.data.objects['MF_studio_adult_body'])
            points=record['frames'][frame-97]
            sample=[]
            for index in indices:
                p=Vector(points[index]);hit,normal,_,distance=skin.find_nearest(p)
                sample.append({'index':index,'row':(index-1395)//13,
                               'skin_nearest_distance_m':distance*scale,
                               'skin_nearest_signed_m':(p-hit).dot(normal)*scale})
            rows.append({'frame':frame,'held_contacts':sample})
            print('178 actual-skin contact audit',frame,flush=True)
    recipe.check_protected()
    (out/'result.json').write_text(json.dumps({'purpose':'Actual rendered skin vs held ribbon edge',
        'cache_sha256':recipe.digest(cache),'indices_source_sha256':recipe.CONTROL_LAYOUT_SHA,
        'protected_exact':True,'visual_gate':'NOT_RUN','full_playback':'NOT_RUN',
        'nearest_normal_sign_is_not_watertight_inside_test':True,'rows':rows},indent=2)+'\n')


def main():
    import bpy
    import numpy as np
    from mathutils import Vector
    import wardrobe_studio as studio
    from wardrobe_riding_fit import fit_render
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());out,cache=validate(job)
    out.mkdir()
    for name in ('wardrobe_motion178.py','wardrobe_motion178_controls.py','wardrobe_motion178_playback.py',
                 'wardrobe_motion178_review.py','wardrobe_motion178_proof.py','wardrobe_motion178_cut.py','wardrobe_motion178_donor.py'):
        (out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(recipe.SOURCE),load_ui=False,use_scripts=False)
    recipe.check_protected()
    if job['operation'] in ('donor40','donor40b','donor41'):
        import wardrobe_motion178_donor as donor
        rig,mats,_=recipe.clean_foundation();ob,record=donor.build(recipe,mats,contact_fit=job['operation']=='donor41')
        scene=bpy.context.scene;scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=True
        for label,angle in (('front',0),('rear',180),('profile',90),('profile-other',270)):
            fit_render(out,label,angle,(0,.15,-1.7),8.,(540,600))
        recipe.check_protected()
        record.update({'protected_exact':True,'visual_gate':'NOT_RUN','motion_gate':'NOT_RUN'})
        (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
        np.savez_compressed(out/'constructed-layout.npz',points=np.array([v.co[:] for v in ob.data.vertices]),
                            triangles=np.array([p.vertices[:] for p in ob.data.polygons],dtype=int))
        return
    if job['operation'] in ('hybrid42','hybrid43','hybrid44','hybrid46','hybrid47'):
        from wardrobe_motion178_cut import recut
        rig,mats,_=recipe.clean_foundation()
        with np.load(recipe.GATHERED_LAYOUT,allow_pickle=False) as record:
            points,pins,cut=recut(record['points'],record['faces'],bpy.context.scene.unit_settings.scale_length,
                                  shoulder_gather=True,supported_major=True,compact_rear=job['operation']!='hybrid42',
                                  diagonal_rear=job['operation'] in ('hybrid44','hybrid46','hybrid47'),
                                  tucked_ends=job['operation'] in ('hybrid46','hybrid47'),
                                  layered_ends=job['operation']=='hybrid47')
            faces=record['faces']
        display=studio.panel('MF178_supported_major_shawl',points,faces,mats['scarf'],.014,1)
        scene=bpy.context.scene;scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=True
        for label,angle in (('front',0),('rear',180),('profile',90),('profile-other',270)):
            fit_render(out,label,angle,(0,.15,-1.7),8.,(540,600))
        recipe.check_protected()
        np.savez_compressed(out/'constructed-layout.npz',points=np.array(points),faces=faces,
            pin_indices=np.array(sorted(pins)),pin_weights=np.array([pins[i] for i in sorted(pins)]))
        (out/'result.json').write_text(json.dumps({'scope':'Initial hybrid construction, no motion pass',
            'cut':cut,'protected_exact':True,'visual_gate':'NOT_RUN','motion_gate':'NOT_RUN'},indent=2)+'\n')
        return
    if job['operation']=='rig40audit':
        import wardrobe_motion178_controls as controls
        from wardrobe_refinement import neutral
        rig,_,_=recipe.clean_foundation();controls.animate(rig,neutral_entry=True)
        proxy=controls.canonical_rig(rig,bpy.context.scene.unit_settings.scale_length)
        actions=[ob.animation_data.action for ob in (rig,proxy)]
        for ob in (rig,proxy):ob.animation_data.action=None;neutral(ob)
        for ob,action in zip((rig,proxy),actions):ob.animation_data.action=action
        rows=[]
        with controls.render_geometry_paused():
            for frame in (1,97,145,193,241,288):
                bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
                errors={b.name:float(np.max(np.abs(np.array(b.matrix)-np.array(proxy.pose.bones[b.name].matrix)))) for b in rig.pose.bones}
                rows.append({'frame':frame,'max_local_bone_matrix_error':max(errors.values()),'errors':errors})
        recipe.check_protected()
        (out/'result.json').write_text(json.dumps({'scope':'Canonical/original local bone-matrix parity after actual action detach/rest/reattach sequence; not rendered-mesh or visual acceptance',
            'rows':rows,'protected_exact':True,'visual_gate':'NOT_RUN',
            'slots':[ob.animation_data.action_slot.identifier if ob.animation_data.action_slot else None for ob in (rig,proxy)]},indent=2)+'\n')
        print('Rig parity',[r['max_local_bone_matrix_error'] for r in rows],flush=True);return
    if job['operation']=='collision39':
        recipe.clean_foundation()
        rows=[{'name':ob.name,'hidden_viewport':ob.hide_viewport,'hidden_render':ob.hide_render,
               'collision_modifiers':[m.name for m in ob.modifiers if m.type=='COLLISION']}
              for ob in bpy.context.scene.objects if any(m.type=='COLLISION' for m in ob.modifiers)]
        recipe.check_protected()
        (out/'result.json').write_text(json.dumps({'scope':'Inherited collider inventory after actual clean foundation, before native proxies',
            'colliders':rows,'protected_exact':True,'collision_collection_api': 'collection' in bpy.types.ClothCollisionSettings.bl_rna.properties.keys(),
            'visual_gate':'NOT_RUN'},indent=2)+'\n')
        print('Inherited colliders',rows,flush=True);return
    with np.load(cache,allow_pickle=False) as record:display=assembly(record)
    if job['operation']=='audit27':
        contact_audit(out,cache);return
    scene=bpy.context.scene;low=job['operation']=='screen18low';clay=job['operation']=='screen18clay'
    initial=job['operation'] in ('initial36','initial36b','initial38','initial38b');uncovered=job['operation'] in ('uncovered36','uncovered36b')
    cpu=job['operation']=='screen27cpu' or initial or uncovered
    if initial:
        display.data.shape_keys.animation_data_clear();display.data.shape_keys.eval_time=0
    if job['operation'] in ('initial38','initial38b'):
        from wardrobe_motion178_cut import recut
        from wardrobe_refinement import neutral
        rig=bpy.data.objects['MF_body156_fit_rig'];action=rig.animation_data.action
        rig.animation_data.action=None;neutral(rig);bpy.context.view_layer.update()
        with np.load(cache,allow_pickle=False) as record:
            points,pins,cut=recut(record['constructed_initial'],record['faces'],scene.unit_settings.scale_length,shoulder_gather=True)
            np.savez_compressed(out/'constructed-layout.npz',points=np.array(points),faces=record['faces'],pin_indices=np.array(sorted(pins)))
        rig.animation_data.action=action
        for item,p in zip(display.data.shape_keys.key_blocks[0].data,points):item.co=p
        (out/'cut.json').write_text(json.dumps(cut,indent=2)+'\n')
    if uncovered:display.hide_render=True
    scene.render.engine='BLENDER_WORKBENCH' if clay else 'CYCLES' if low or cpu else 'BLENDER_EEVEE'
    scene.render.use_persistent_data=True
    renderer=None
    if clay:
        # Motion/contact inspection only. No claim about textured identity or
        # final lighting; those retain matched Cycles stills as authority.
        shading=scene.display.shading;shading.light='STUDIO';shading.color_type='OBJECT'
        shading.show_shadows=True;shading.show_cavity=True
        for ob in scene.objects:
            ob.color=(.24,.34,.52,1) if any(k in ob.name for k in ('tunic','sleeve','shawl','gusset')) else (
                (.22,.12,.06,1) if any(k in ob.name for k in ('harness','belt','buckle')) else (.65,.48,.37,1))
    if low:
        from wardrobe_motion178_review import preview_gpu
        scene.cycles.samples=4;renderer=preview_gpu(scene)
    if cpu:
        scene.cycles.device='CPU';scene.cycles.samples=12
        renderer={'selected':'CPU','reason':'Retained Metal pipeline failure; diagnostic matched lighting'}
    timings=[]
    views=(tuple((frame,label,angle) for frame in ((97,) if initial or uncovered else (97,145)) for label,angle in
                 (('front',0),('profile',90),('rear',180),('profile-other',270))) if cpu else
           ((97,'front',0),(145,'profile',90),(145,'rear',180)))
    for frame,label,angle in views:
        scene.frame_set(frame);bpy.context.view_layer.update()
        target=studio.torso_matrix(-2.7)@Vector((0,.15,-1.7));start=time.monotonic()
        fit_render(out,'%s-%03d'%(label,frame),angle,tuple(target),8.,(360,400) if low or clay else (540,600))
        timings.append({'frame':frame,'angle':angle,'render_seconds':time.monotonic()-start})
    recipe.check_protected()
    (out/'result.json').write_text(json.dumps({'purpose':'Renderer screen only; not whole-look approval',
        'cache_sha256':recipe.digest(cache),'source_sha256':recipe.SOURCE_SHA,
        'protected_exact':True,'cache_time_samples_verified':True,'visual_gate':'NOT_RUN',
        'full_playback':'NOT_RUN','timings':timings,'engine':scene.render.engine,'renderer':renderer,
        'cycles_samples':scene.cycles.samples if low or cpu else None,'resolution':(360,400) if low or clay else (540,600),
        'clay_contact_inspection_only':clay,
        'pre_solve_initial_only':initial,'moving_shawl_hidden_only':uncovered,
        'torso_matrix_parity_all_192_frames':True,
        'handler_sha256':recipe.digest(Path(__file__))},indent=2)+'\n')


if __name__=='__main__':main()
