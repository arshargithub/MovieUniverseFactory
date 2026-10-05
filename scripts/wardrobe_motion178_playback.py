"""Native solver-to-animation transfer for the reviewed short cloth proof.

Retains full trajectories and creates no visual PASS. Fixed paths/operations
are owned by wardrobe_motion178; this is not a generated-code runner.
"""
import json
from pathlib import Path
import math


def absolute_cache(ob, frames):
    """Store exact per-frame solved cloth positions in editable native keys."""
    ob.shape_key_add(name='Basis')
    keys=ob.data.shape_keys;keys.use_relative=False
    for i,coordinates in enumerate(frames):
        key=ob.shape_key_add(name='Solved frame %03d'%(i+1))
        key.interpolation='KEY_LINEAR'
        key.data.foreach_set('co',coordinates.flatten())
    keys.eval_time=10
    keys.keyframe_insert(data_path='eval_time',frame=97)
    keys.eval_time=10*len(frames)
    keys.keyframe_insert(data_path='eval_time',frame=96+len(frames))
    # Blender defaults keyframe handles to Bezier. Make time itself linear;
    # otherwise a linear cache would be sampled with an unwanted ease.
    action=keys.animation_data.action
    for slot in action.slots:
        for layer in action.layers:
            for strip in layer.strips:
                bag=strip.channelbag(slot)
                if bag:
                    for curve in bag.fcurves:
                        for point in curve.keyframe_points:point.interpolation='LINEAR'


def move(out, recipe, initial):
    import bpy
    import numpy as np
    from mathutils import Vector
    import wardrobe_studio as studio
    import wardrobe_motion178_controls as controls
    from wardrobe_riding_fit import fit_render
    rig,mats,groom=recipe.clean_foundation()
    points,faces,pins,components=recipe.clean_patterns(periodic=True)
    operation_variant=int(out.name.rsplit('move',1)[1])  # main admits a fixed enum only
    major_supported=operation_variant in (44,45,47)
    isolate_collisions=operation_variant in (39,44,45,47)
    variant=38 if isolate_collisions else operation_variant
    relaxed=variant>=17
    contact=variant>=16
    correct_edge=variant>=15
    edge_supported=variant>=14
    supported=variant==12
    coherent=variant>=13
    rest_space=variant>=9
    calibrated=8<=variant<=11
    ribbon=variant>=7
    if ribbon:points,faces,pins,components=recipe.twice_wrapped_patterns(raised_shoulders=edge_supported)
    curved=variant>=5
    integrated=variant>=6
    if curved:
        _,head_faces,head_pins,_=recipe.dressed_head_pattern()
        faces[:len(head_faces)]=head_faces
        pins={i:w for i,w in pins.items() if i>=components[0]}
        pins.update(head_pins)
    if out.name.endswith(('move04','move05','move06')):
        # Closed sewn courses have no exposed rear ends to hold. Free their
        # center back, which otherwise creates an inverted-V shelf.
        for offset in (components[0],components[0]+components[1]):
            for row in (0,1,95):
                for col in (5,6,7):pins.pop(offset+row*13+col,None)
    if initial.shape!=(len(points),3) or not np.isfinite(initial).all():
        raise ValueError('Invalid bounded initial cloth')
    # Coordinates are physically settled staging, not an acceptance target.
    points=[tuple(p) for p in initial]
    if out.name.endswith(('move04','move05','move06')):
        # Initial dressing only: bring the lower course into the same chest
        # assembly rather than a separated second hanging necklace.
        start=components[0]+components[1]
        for index in range(start,len(points)):
            p=list(points[index]);p[2]+=.25*controls.smooth((-p[1]-.2)/1.2)
            points[index]=tuple(p)
    scale=bpy.context.scene.unit_settings.scale_length
    sample=controls.body_weight_sampler()
    print('178 neutral fit/weight support ready',flush=True)
    visible=[]
    for name in ('MF_fit_tunic_173_visible','MF_171_fitted_sleeve_L_173_visible',
                 'MF_171_fitted_sleeve_R_173_visible','MF_173_tension_harness_-1',
                 'MF_173_tension_harness_1','MF_173_waist_belt'):
        ob=bpy.data.objects[name]
        # A belt does not inherit neighbouring thigh skin weights. Its leather
        # band and buckle share pelvis support; shoulder straps retain skinning.
        sampler=(lambda p:{'pelvis':1.}) if curved and name=='MF_173_waist_belt' else sample
        controls.bind(ob,rig,sampler)
        visible.append(ob)
    for name in ('MF_173_belt_buckle','MF_173_buckle_tongue'):
        ob=bpy.data.objects[name]
        if not any(c.type=='CHILD_OF' and c.target==rig for c in ob.constraints):
            constraint=ob.constraints.new('CHILD_OF');constraint.name='MF178 rigid belt fitting'
            constraint.target=rig;constraint.subtarget='pelvis'
            constraint.inverse_matrix=(rig.matrix_world@rig.pose.bones['pelvis'].matrix).inverted()
    # No seams left frozen at a previous pose; refresh them from the dynamic
    # surfaces at final finish, rather than masking a garment displacement.
    for ob in bpy.context.scene.objects:
        if '_seam_' in ob.name or 'harness_welt' in ob.name:ob.hide_render=True
    controls.animate(rig,neutral_entry=edge_supported)
    print('178 coordinated native animation ready',flush=True)
    canonical=controls.canonical_rig(rig,scale)
    supports=[]
    # Capture neutral/rest geometry for skinning, not an already posed mesh.
    # The original rig animation is paused for this construction snapshot.
    animation=rig.animation_data.action;rig.animation_data.action=None
    from wardrobe_refinement import neutral
    neutral(rig)
    canonical_animation=canonical.animation_data.action
    if rest_space:
        canonical.animation_data.action=None;neutral(canonical)
        bpy.context.view_layer.update()
    for name in ('MF_studio_adult_body','MF_fit_tunic_173_visible',
                 'MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible',
                 'MF_173_tension_harness_-1','MF_173_tension_harness_1'):
        ob=recipe.solver_support(bpy.data.objects[name],scale,
              faces_limit=12000 if variant>=25 and name=='MF_studio_adult_body' else 4500)
        # Apply the simplification once so correspondence stays fixed.
        bpy.context.view_layer.objects.active=ob
        for mod in list(ob.modifiers):
            if mod.type=='DECIMATE':bpy.ops.object.modifier_apply(modifier=mod.name)
        controls.bind(ob,canonical,sample,scale,allow_fingers=name=='MF_studio_adult_body')
        supports.append(ob)
    ob=recipe.solver_support(groom,scale)
    controls.bind(ob,canonical,scale=scale,chest_only=True);supports.append(ob)
    if operation_variant==47:
        ob=recipe.solver_support(bpy.data.objects['MF_continuous_head_neck'],scale)
        controls.bind(ob,canonical,scale=scale,chest_only=True);supports.append(ob)
    # Controlled ablation: the convex capped bridge can stand above the real
    # shoulder. Retain actual garment/body/hair collisions; do not change the
    # route, supports, rest shape or animation for this comparison.
    bridge_enabled=variant not in (19,20,32,33,34,35,36,37,38)
    if bridge_enabled:
        bridge=recipe.chest_bridge(supports,scale,upper_z=-2.35 if variant in (21,25,26,27,28,29,30,31) else -1.52,
                                  upper_band=.055 if variant==22 else .23)
        controls.bind(bridge,canonical,sample,scale)
        supports.append(bridge)
    staging=recipe.separated_initial_layout(points,faces,components,supports,scale,curved=True) if curved else None
    if coherent:
        pins={i:w for i,w in pins.items() if i<components[0]}
        pins.update({components[0]+row*13+6:1. for row in (24,72,119,167)})
    pin_staging=seat_shoulder_supports(points,pins,components,supports,scale,top_contact=calibrated or supported or coherent,coherent=coherent) if integrated else None
    contact_dressing=contact_border(points,faces,components,supports,scale) if contact else None
    geometry=geometry_preflight(points,faces)
    if calibrated or supported or coherent:
        for i in pins:
            if i>=components[0]:pins[i]=1.
    if supported or edge_supported:
        # Hybrid authoring: supported top border preserves the wrapped route;
        # lower borders and broad drape remain solved cloth, not rigid shells.
        column=supported_border(points,components) if correct_edge else 0
        for row in range(192):
            if relaxed and points[components[0]+row*13+column][1]>.55:continue
            pins[components[0]+row*13+column]=1.
    if variant>=18:
        for index in list(pins):
            if index>=components[0] and (index-components[0])%13==6:pins.pop(index)
    if variant in (20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37):
        # True collision-only control:19 also changed initial clearance.
        # Restore exact18 dressed points/pins/faces before any physics so
        # bridge removal alone is the independent variable.
        with np.load(recipe.CONTROL_LAYOUT,allow_pickle=False) as controlled:
            points=[tuple(p) for p in controlled['points']]
            faces=[tuple(int(i) for i in f) for f in controlled['faces']]
            pins={int(i):1. for i in controlled['pin_indices']}
        geometry=geometry_preflight(points,faces)
        staging={'controlled_initial_layout_sha256':recipe.CONTROL_LAYOUT_SHA,
                 'scope':'Exact18 starting points/faces/pins; only collision bridge changed'}
        pin_staging=None;contact_dressing=None
    try:
        border_registration=register_actual_border(points,pins,scale,original=initial,
                         coherent=variant>=25,body_envelope=variant>=26) if variant in (24,25,26,27,28) else None
        if variant in (29,30):border_registration=continuous_contact_pattern(points,pins,scale,initial,transport=variant==30)
        if variant in (31,32,33,34,35,36,37):
            with np.load(recipe.CONTINUOUS_LAYOUT,allow_pickle=False) as controlled:
                points=[tuple(p) for p in controlled['points']]
                faces=[tuple(int(i) for i in f) for f in controlled['faces']]
                pins={int(i):1. for i in controlled['pin_indices']}
            pins=sparse_shoulder_attachments(pins)
            border_registration={'continuous_layout_sha256':recipe.CONTINUOUS_LAYOUT_SHA,
                'scope':'Exact30 continuous initial points/faces/rest; shoulder-only attachment control',
                'shoulder_support_rows':[24,72,119,167],'supported_ribbon_points':8,
                'post_solve_projection':False}
            if variant==33:border_registration.update(downward_cross_sections(points,scale,initial))
            if variant in (34,35,36,37):
                with np.load(recipe.DOWNWARD_LAYOUT,allow_pickle=False) as controlled:
                    points=[tuple(p) for p in controlled['points']]
                    faces=[tuple(int(i) for i in f) for f in controlled['faces']]
                    pins={int(i):1. for i in controlled['pin_indices'] if i<1395}
                with np.load(recipe.CONTINUOUS_LAYOUT,allow_pickle=False) as controlled:
                    pins.update({int(i):1. for i in controlled['pin_indices'] if i>=1395})
                border_registration={'downward_layout_sha256':recipe.DOWNWARD_LAYOUT_SHA,
                    'scope':'Exact33 points/faces/rest/mass/wind/colliders; continuous upper-border support replaces sparse shoulder tacks',
                    'supported_ribbon_points':sum(i>=1395 for i in pins),
                    'post_solve_projection':False}
                if variant==35:border_registration['head_rest_override']='Flat measured original cut; not exact34 rest'
                if variant==36:
                    from wardrobe_motion178_cut import recut
                    points,pins,border_registration=recut(points,faces,scale)
                if variant==37:
                    with np.load(recipe.PRE_SHAPED_LAYOUT,allow_pickle=False) as controlled:
                        points=[tuple(p) for p in controlled['points']]
                        faces=[tuple(int(i) for i in f) for f in controlled['faces']]
                        pins={int(i):1. for i in controlled['pin_indices']}
                    border_registration={'pre_shaped_layout_sha256':recipe.PRE_SHAPED_LAYOUT_SHA,
                        'scope':'Exact36 geometry/pins/rest/colliders/body motion; conventional native profile comparison',
                        'post_solve_projection':False}
        if border_registration:
            geometry=geometry_preflight(points,faces)
            staging['scope']=('Exact33 head staging with ordered angular pre-shaped ribbon cut' if variant in (36,37) else
                              '18 starting layout with measured held-border contact repair before physics')
        if variant==38:
            with np.load(recipe.GATHERED_LAYOUT,allow_pickle=False) as controlled:
                points=[tuple(p) for p in controlled['points']]
                faces=[tuple(int(i) for i in f) for f in controlled['faces']]
                pins={int(i):1. for i in controlled['pin_indices']}
            # These former mid-width back tacks formed a projecting shelf;
            # the external rear falls remain free, supported via shoulders.
            for row in (0,191):
                for column in (4,6,8):pins.pop(1395+row*13+column,None)
            geometry=geometry_preflight(points,faces)
            border_registration={'gathered_layout_sha256':recipe.GATHERED_LAYOUT_SHA,
                'scope':'Screened neutral gathered shoulder cut, free rear ends and consistently scaled lightweight diagnostic profile; multifactor, not causal single-parameter test',
                'post_solve_projection':False}
        if major_supported:
            layout=recipe.TUCKED_LAYOUT if operation_variant==47 else recipe.HYBRID_LAYOUT
            with np.load(layout,allow_pickle=False) as controlled:
                points=[tuple(p) for p in controlled['points']]
                faces=[tuple(int(i) for i in f) for f in controlled['faces']]
                pins={int(i):float(w) for i,w in zip(controlled['pin_indices'],controlled['pin_weights'])}
            if operation_variant==45:
                for row in range(3,189):
                    for col in range(1,13):
                        pins[1395+row*13+col]=1. if col>=3 else .8 if col==2 else .3
            geometry=geometry_preflight(points,faces)
            border_registration={'hybrid_layout_sha256':recipe.TUCKED_LAYOUT_SHA if operation_variant==47 else recipe.HYBRID_LAYOUT_SHA,
                'scope':'Explicit major-form chest support; lower loose width and headfall simulated; not universal freely draped cloth',
                'post_solve_projection':False}
    except Exception as error:
        np.savez_compressed(out/'rejected-initial-layout.npz',points=np.array(points),faces=np.array(faces),
                            pin_indices=np.array(sorted(pins)))
        (out/'initial-preflight-failure.json').write_text(json.dumps({'gate':'FAIL','reason':str(error)})+'\n')
        raise
    if variant==32:
        # Reconstruct the prior ghost support for a retained initial-overlap
        # audit only. It is NOT a collider in this ablation.
        ghost=recipe.chest_bridge(supports,scale,upper_z=-2.35)
        from wardrobe_refinement import tree_for
        audit_tree=tree_for(ghost);intrusions=[]
        for index in range(1395,len(points)):
            p=Vector(points[index])*scale;hit,n,_,distance=audit_tree.find_nearest(p)
            signed=(p-hit).dot(n)
            if signed<-.0025:intrusions.append({'index':index,'signed_nearest_m':signed,'distance_m':distance})
        (out/'prior-bridge-overlap-audit.json').write_text(json.dumps({
            'scope':'Local nearest-normal overlap diagnostic on prior closed capped bridge, not visual PASS',
            'negative_below_2_5mm_count':len(intrusions),'points':intrusions,
            'prior_bridge_not_used_in_physics':True},indent=2)+'\n')
        for modifier in list(ghost.modifiers):
            if modifier.type=='COLLISION':ghost.modifiers.remove(modifier)
        ghost.hide_viewport=True
    stitches=([] if variant in (36,37,38) else ribbon_ends(points,components) if ribbon else
              concealed_stitches(points,components,front_overlap=integrated) if curved else [])
    rig.animation_data.action=animation
    data=bpy.data.meshes.new('MF178_live_cloth')
    data.from_pydata([tuple(scale*c for c in p) for p in points],stitches,faces);data.update()
    cloth=bpy.data.objects.new('MF178_live_solver',data)
    bpy.context.scene.collection.objects.link(cloth);cloth.hide_render=True
    controls.bind(cloth,canonical,sample,scale=scale,chest_only=major_supported or not integrated)
    if rest_space:
        canonical.animation_data.action=canonical_animation
        bpy.context.view_layer.update()
    pin=cloth.vertex_groups.new(name='Supported crown and rear overlap')
    for i,w in pins.items():pin.add([i],w,'REPLACE')
    mod=cloth.modifiers.new('Continuous wardrobe cloth','CLOTH')
    flat=None
    if relaxed:
        cloth.shape_key_add(name='Dressed initial assembly')
        flat=cloth.shape_key_add(name='Unrolled fabric rest')
        coordinates=(list(points) if variant in (36,37,38) else flat_ribbon_rest(points,initial,components,matched_guide=variant in (29,30,31,32,33,34,35)))
        if variant in (35,36,37,38) and not major_supported:
            coordinates[:1395]=flat_head_rest(recipe.dressed_head_pattern()[0])
        flat.data.foreach_set('co',(np.array(coordinates)*scale).flatten())
        flat.value=0.;cloth.active_shape_key_index=0;cloth.show_only_shape_key=False
        mod.settings.rest_shape_key=flat;mod.settings.use_dynamic_mesh=False
    profile=cloth_profile(points,faces,scale) if (calibrated or variant==38) and not major_supported else None
    mass_control=cloth_profile(points,faces,scale) if variant in (23,28,29,30,31,32,33,34,35,36) else None
    s=mod.settings;s.quality=16 if calibrated else 8;s.mass=profile['vertex_mass'] if profile else .22
    if mass_control:s.mass=mass_control['vertex_mass']
    s.tension_stiffness=25;s.compression_stiffness=25;s.shear_stiffness=12;s.bending_stiffness=.035
    s.tension_damping=6;s.compression_damping=6;s.shear_damping=6;s.air_damping=3
    if variant==36:
        # Pre-shaped construction plus soft secondary cloth, not another
        # demand that simulation discover the intended wrapping from a flat
        # ribbon. These are authored approximate settings, not measured fabric.
        s.bending_stiffness=mass_control['bending_stiffness']
        s.bending_damping=.5*mass_control['effector_gain']
        s.air_damping=3*mass_control['effector_gain'];s.quality=12
    if (calibrated or variant==38) and not major_supported:
        s.bending_stiffness=profile['bending_stiffness'];s.pin_stiffness=50.
        s.air_damping=3*profile['effector_gain']
        s.bending_damping=.5*profile['effector_gain']
        damping=6*math.sqrt(profile['effector_gain'])
        s.tension_damping=damping;s.compression_damping=damping;s.shear_damping=damping
        if variant==38:s.quality=24
    s.vertex_group_mass=pin.name
    if stitches:s.use_sewing_springs=True;s.sewing_force_max=5.
    if out.name.endswith('move11'):
        # Consistent diagnostic force-to-mass scaling. Changing mass alone
        # left tension/sewing forces several orders of magnitude too large.
        gain=profile['effector_gain']
        s.tension_stiffness=25*gain;s.compression_stiffness=25*gain;s.shear_stiffness=12*gain
        s.tension_damping=6*gain;s.compression_damping=6*gain;s.shear_damping=6*gain
        s.sewing_force_max=5*gain
    if supported:s.pin_stiffness=50.
    mod.collision_settings.use_collision=True;mod.collision_settings.distance_min=.003
    collision_domain=None
    if isolate_collisions:
        collision_domain=bpy.data.collections.new('MF178_exclusive_metric_colliders')
        scene_collection=bpy.context.scene.collection
        scene_collection.children.link(collision_domain)
        for support in supports:collision_domain.objects.link(support)
        mod.collision_settings.collection=collision_domain
        if {o.name for o in mod.collision_settings.collection.all_objects}!={o.name for o in supports}:
            raise ValueError('Collision domain includes an unintended object')
    mod.collision_settings.use_self_collision=True;mod.collision_settings.self_distance_min=.003
    if variant in (36,37):mod.collision_settings.self_distance_min=.0015
    if variant==38:mod.collision_settings.self_distance_min=.001
    if variant==37:s.quality=12
    if major_supported:s.quality=16
    mod.point_cache.frame_start=1;mod.point_cache.frame_end=289
    wind_gain=(.04*mass_control['effector_gain'] if variant in (28,29,30,31,32,33,34,35,36) else
               profile['effector_gain'] if profile else .04 if supported or coherent else 1.)
    if major_supported:wind_gain=1.
    controls.wind(gain=wind_gain)
    np.savez_compressed(out/'constructed-layout.npz',points=np.array(points),faces=np.array(faces),pin_indices=np.array(sorted(pins)))
    (out/'construction.json').write_text(json.dumps({'staging':staging,'pins':pins,'supported_pin_dressing':pin_staging,
        'solver_mass_per_vertex':s.mass,'mass_scope':'Authored solver setting, not measured physical garment mass',
        'operation_variant':operation_variant,
        'major_supported_scope':border_registration if major_supported else None,
        'actual_head_collision_support':operation_variant==47,
        'exclusive_collision_objects':[o.name for o in collision_domain.all_objects] if collision_domain else None,
        'collision_domain_scope':'Explicit metric support collection for new hybrid recipe' if major_supported else 'Exact38 construction/profile/body/wind; only explicit collision membership changed' if isolate_collisions else 'Scene-global collision membership, including retained old colliders',
        'mass_only_control':mass_control,
        'wind_gain':wind_gain,'mass_wind_paired_diagnostic':variant in (28,29,30,31,32,33,34,35,36),
        'solver_profile':'Conventional authored native profile, not measured fabric or mass-only control' if variant==37 else 'Authored diagnostic settings',
        'head_rest_shape':'Prescribed supported major form with free lower cloth' if major_supported else 'Unrolled measured opening arc and longitudinal cut' if variant in (35,36,37,38) else 'Dressed curved geometry',
        'bending_stiffness':s.bending_stiffness,'bending_damping':s.bending_damping,
        'air_damping':s.air_damping,'self_collision_distance_m':mod.collision_settings.self_distance_min,
        'actual_border_registration':border_registration,
        'sewing_edges':stitches,'quality':s.quality,'supported_top_border':supported or edge_supported,'geometry_preflight':geometry,
        'neutral_upper_body_entry':edge_supported,'supported_border_column':12 if correct_edge else 0 if supported or edge_supported else None,
        'contact_border_dressing':contact_dressing,'rear_border_free':relaxed,'middle_holds_removed':variant>=18,
        'convex_chest_collision_bridge':bridge_enabled,
        'bridge_upper_z_native':-2.35 if variant in (21,25,26,27,28,29,30,31) else -1.52 if bridge_enabled else None,
        'body_collision_face_limit':12000 if variant>=25 else 4500,
        'bridge_upper_section_half_width_native':.055 if variant==22 else .23 if bridge_enabled else None,
        'ribbon_rest_shape':'Pre-shaped ordered angular neutral cut' if variant in (36,37,38) else 'Matched continuous held-edge metric with1percent ease' if variant in (29,30,31,32,33,34,35) else 'Unrolled flat fabric with authored8percent length/15percent width ease' if flat else 'Dressed starting geometry'},indent=2)+'\n')
    scene=bpy.context.scene;scene.gravity=(0,0,-9.81);scene.render.fps=24
    frames=[];chest_matrices=[]
    print('178 canonical collision/cloth support ready',flush=True)
    with controls.render_geometry_paused():
        for frame in range(1,289):
            scene.frame_set(frame);bpy.context.view_layer.update()
            ev=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
            coordinates=np.array([v.co[:] for v in mesh.vertices],dtype=float)/scale
            ev.to_mesh_clear()
            if not np.isfinite(coordinates).all() or np.max(np.abs(coordinates))>100:
                raise ValueError('Nonfinite or escaped moving cloth at frame %s max=%s'%(frame,float(np.max(np.abs(coordinates)))))
            if frame>=97:
                frames.append(coordinates.copy())
                chest_matrices.append(np.array(studio.torso_matrix(-1.)))
            if frame%24==0:print('178 live moving cloth',frame,flush=True)
    frames=np.array(frames)
    chest_matrices=np.array(chest_matrices)
    local=np.einsum('fij,fvj->fvi',np.linalg.inv(chest_matrices),
                    np.concatenate([frames,np.ones((*frames.shape[:2],1))],axis=2))[:,:,:3]
    residual=float(np.max(np.linalg.norm(local-local[0],axis=2)))
    rigid=np.einsum('fij,vj->fvi',chest_matrices,
                   np.concatenate([local[0],np.ones((len(local[0]),1))],axis=1))
    rigid_local=np.einsum('fij,fvj->fvi',np.linalg.inv(chest_matrices),rigid)[:,:,:3]
    rigid_residual=float(np.max(np.linalg.norm(rigid_local-rigid_local[0],axis=2)))
    np.savez_compressed(out/'cloth-trajectory.npz',frames=frames,initial=initial,
                       constructed_initial=np.array(points),faces=np.array(faces,dtype=int),
                       chest_matrices=chest_matrices)
    display=studio.panel('MF178_moving_shawl',points,faces,mats['scarf'],.014,1)
    with controls.render_geometry_paused():absolute_cache(display,frames)
    scene.frame_start=97;scene.frame_end=288;scene.cycles.samples=12
    scene.render.use_persistent_data=True
    from wardrobe_motion178_review import preview_gpu
    if variant in (28,29,30,31,32,33,34,35,36,37,38):
        scene.cycles.device='CPU';renderer={'selected':'CPU','reason':'Retained27 Metal pipeline crash'}
    else:renderer=preview_gpu(scene) if curved else {'selected':'CPU'}
    print('178 preview renderer',renderer,flush=True)
    scene.frame_set(97);bpy.context.view_layer.update()
    # Earliest revealing temporal screen before spending on full film frames.
    screen_frames=(97,145) if variant>=18 else (97,145,193,241,288)
    for frame in screen_frames:
        scene.frame_set(frame);bpy.context.view_layer.update()
        target=studio.torso_matrix(-2.7)@Vector((0,.15,-1.7))
        views=(('front',0),('rear',180),('profile',90),('profile-other',270)) if variant>=18 else (('front',0),('rear',180),('profile',90))
        for label,angle in views:
            fit_render(out,'%s-%03d'%(label,frame),angle,tuple(target),8.,(540,600))
    recipe.check_protected()
    (out/'result.json').write_text(json.dumps({'visual_gate':'NOT_RUN','motion_gate':'NOT_RUN',
        'protected_exact':True,'source_sha256':recipe.SOURCE_SHA,'frames':len(frames),
        'moving_start_sha256':None if ribbon else recipe.MOVING_START_SHA,
        'pattern_kind':'continuous_twice_wound_ribbon' if ribbon else 'separate_periodic_courses',
        'staging':staging,'supported_pin_dressing':pin_staging,'cloth_profile':profile,
        'concealed_sewing_edges':stitches,'renderer':renderer,
        'fps':24,'duration_seconds':len(frames)/24,'rendered_screen_frames':screen_frames,
        'maximum_interframe_delta_native':float(np.max(np.linalg.norm(np.diff(frames,axis=0),axis=2))),
        'maximum_chest_relative_motion_native':residual,
        'rigid_reference_negative_control_chest_relative_motion':rigid_residual,
        'rigid_control_kind':'Computed transform-only trajectory; not separately rendered',
        'handler_sha256':recipe.digest(Path(recipe.__file__)),
        'playback_handler_sha256':recipe.digest(Path(__file__))},indent=2)+'\n')


def concealed_stitches(points,components,front_overlap=False):
    """Bounded back-side tacks link all three panels, never world-lock cloth.

    These simulation edges are concealed assembly supports, not visible straps
    or proof of a continuous manufacturable cloth pattern.
    """
    if components!=[1395,1248,1248] or len(points)!=sum(components):
        raise ValueError('Fixed assembly topology required')
    upper=components[0];lower=upper+components[1]
    edges=[];used=set()
    head_candidates=range(22*31,1395)
    for row in (4,8,88,92):
        target=upper+row*13+6
        p=points[target]
        choice=min((i for i in head_candidates if i not in used),
                   key=lambda i:sum((points[i][k]-p[k])**2 for k in range(3)))
        used.add(choice);edges.append((choice,target))
        edges.append((upper+row*13+2,lower+row*13+12))
    if front_overlap:
        # Concealed front overlap is one supported cloth assembly, not two
        # independently hanging necklaces. Offset courses remain visible.
        edges.extend((upper+row*13,lower+row*13+12) for row in range(36,61,2))
    return edges


def seat_shoulder_supports(points,pins,components,supports,scale,top_contact=False,coherent=False):
    """Register only supported starting points to actual shoulder garments.

    No post-solve projection. Free borders retain cloth mechanics. Armature
    support subsequently uses actual body weights, not an all-chest lock.
    """
    from wardrobe_refinement import tree_for
    from mathutils import Vector
    trees=[tree_for(ob) for ob in supports if any(k in ob.name for k in ('adult_body','tunic','harness'))]
    if not trees:raise ValueError('Missing actual shoulder contact support')
    shifts=[]
    for i in pins:
        if i<components[0]:continue
        p=Vector(points[i])*scale
        if top_contact:
            # Register at the actual inner shoulder, not outside the shoulder
            # after radial initial-layer separation pushed the ribbon outward.
            x=math.copysign(min(abs(p.x),1.62*scale),p.x)
            y=max(-.10*scale,min(.20*scale,p.y))
            candidates=[tree.ray_cast(Vector((x,y,3*scale)),Vector((0,0,-1)),10*scale) for tree in trees]
        else:candidates=[tree.find_nearest(p) for tree in trees]
        candidates=[r for r in candidates if r[0] is not None]
        if not candidates:raise ValueError('Missing supported shoulder surface: index=%s point=%s cast=%s scale=%s support=%s'%(i,tuple(p),(x,y) if top_contact else None,scale,[o.name for o in supports]))
        hit,normal,_,_=max(candidates,key=lambda r:r[0].z) if top_contact else min(candidates,key=lambda r:r[3])
        layer=int(i>=components[0]+1248)
        target=hit+normal*(.005+.007*layer if top_contact else .005)
        delta=(target-p)/scale
        shifts.append(delta.length)
        if coherent:
            row=(i-components[0])//13
            # Translate a contiguous patch, retaining cross-sectional width
            # rather than moving a lone vertex by a full native unit.
            for r in range(max(0,row-8),min(192,row+9)):
                weight=(1-abs(r-row)/9)**2
                for column in range(13):
                    j=components[0]+r*13+column
                    points[j]=tuple(Vector(points[j])+delta*weight)
        else:points[i]=tuple(target/scale)
    return {'points':len(shifts),'max_initial_shift_native':max(shifts),'post_solve_projection':False}


def geometry_preflight(points,faces):
    edges={tuple(sorted((a,b))) for face in faces for a,b in zip(face,face[1:]+face[:1])}
    minimum=min(math.sqrt(sum((points[a][k]-points[b][k])**2 for k in range(3))) for a,b in edges)
    if not math.isfinite(minimum) or minimum<1e-4:
        raise ValueError('Collapsed or invalid cloth edge before solver: %s'%minimum)
    return {'edge_count':len(edges),'minimum_edge_native':minimum,'collapsed_edge_gate':'PASS'}


def supported_border(points,components):
    """Check actual front/rear edge elevation rather than assuming v=0 is up."""
    if components!=[1395,2496]:raise ValueError('Fixed supported ribbon required')
    for row in (0,48,96,143,191):
        if points[1395+row*13+12][2]<=points[1395+row*13][2]:
            raise ValueError('Ribbon upper/lower orientation mismatch at row %s'%row)
    return 12


def contact_border(points,faces,components,supports,scale):
    """Dress supported front/back edges on real neutral contact surfaces.

    Whole-row translation preserves cross-section orientation. A final initial
    clearance acts on free vertices only. Never projects a simulated frame.
    """
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_refinement import tree_for
    trees=[tree_for(ob) for ob in supports if any(k in ob.name for k in ('adult_body','tunic','harness','groom')) and 'bridge' not in ob.name]
    trees.append(BVHTree.FromPolygons([Vector(p)*scale for p in points[:1395]],
                 [f for f in faces if max(f)<1395]))
    def outer(p):
        root=Vector((0,.14*scale,p.z));direction=(p-root).normalized();hits=[]
        for tree in trees:
            origin=root.copy()
            for _ in range(8):
                hit,normal,_,_=tree.ray_cast(origin,direction,1.)
                if hit is None:break
                hits.append((float((hit-root).dot(direction)),hit,normal))
                origin=hit+direction*.0003
        if not hits:return None
        return max(hits,key=lambda r:r[0])
    shifts=[]
    for row in range(192):
        index=1395+row*13+12;p=Vector(points[index])*scale
        if abs(p.y/scale)<.55:continue  # superior shoulder already registered
        hit=outer(p)
        if hit is None:raise ValueError('Missing front/back edge contact at row %s'%row)
        _,location,normal=hit
        margin=(.065+.075*int(row>=96))*scale
        delta=(location+normal*margin-p)/scale
        shifts.append(delta.length)
        for column in range(13):
            j=1395+row*13+column;points[j]=tuple(Vector(points[j])+delta)
    free_shifts=[]
    for row in range(192):
        margin=(.065+.075*int(row>=96))*scale
        for column in range(12):
            index=1395+row*13+column;p=Vector(points[index])*scale
            hit=outer(p)
            if hit is None:continue  # free cloth may extend beyond a surface
            distance,location,normal=hit;root=Vector((0,.14*scale,p.z))
            if (p-root).length<distance+margin:
                target=location+normal*margin;free_shifts.append((target-p).length/scale)
                points[index]=tuple(target/scale)
    return {'registered_rows':len(shifts),'maximum_guide_shift_native':max(shifts),
            'free_initial_clearance_vertices':len(free_shifts),'post_solve_projection':False,
            'guide_scope':'Actual body/tunic/harness and staged head covering; not convex bridge'}


def register_actual_border(points,pins,scale,original=None,coherent=False,body_envelope=False):
    """Initial contact registration, never per-pose/post-solve projection.

    The support is the actual held edge, not a different centre-line point.
    Whole cross-sections translate together; free cloth subsequently solves.
    """
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    names=('MF_studio_adult_body','MF_fit_tunic_173_visible',
           'MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible',
           'MF_173_tension_harness_-1','MF_173_tension_harness_1')
    trees=[tree_for(bpy.data.objects[name]) for name in names]
    corrections=[];changed=set();free_corrections=0;row_frames={}
    for index in sorted(pins):
        if index<1395:continue
        p=Vector(points[index]);layer=int(index>=1395+1248);gap=(.005+.007*layer)/scale
        candidates=[tree.find_nearest(p) for tree in trees]
        valid=[r for r in candidates if r[0] is not None]
        hit,normal,_,distance=min(valid,key=lambda r:r[3])
        skin=candidates[0];skin_signed=(p-skin[0]).dot(skin[1])*scale
        signed=(p-hit).dot(normal)*scale
        if distance*scale<=gap*scale+.008 and signed>=.003 and skin_signed>=.003:continue
        target=hit+normal*gap
        if body_envelope:
            # A nearest open leather edge can have an inward/tangent normal.
            # Construct the outer contact along the actual skin normal, not
            # that edge normal. This also gives a coherent fabric tangent.
            normal=skin[1].copy();root=skin[0]-normal*.02;extent=0.
            for tree in trees:
                origin=root.copy();travel=0.
                for _ in range(8):
                    crossing,_,_,ray_distance=tree.ray_cast(origin,normal,.7-travel)
                    if crossing is None:break
                    travel+=ray_distance;extent=max(extent,travel)
                    origin=crossing+normal*1e-5;travel+=1e-5
                    if travel>=.7:break
            target=root+normal*(extent+gap)
        delta=target-p
        if delta.length*scale>.06:raise ValueError('Held border outside bounded measured support')
        row=(index-1395)//13
        corrections.append({'index':int(index),'row':row,'shift_m':delta.length*scale,
                            'before_nearest_m':distance*scale,'before_skin_signed_m':skin_signed})
        for column in range(13):
            i=1395+row*13+column;points[i]=tuple(Vector(points[i])+delta);changed.add(i)
        if coherent:
            width=(Vector(original[1395+row*13])-Vector(original[index])).length
            direction=Vector(points[1395+row*13])-Vector(points[index])
            direction-=normal*direction.dot(normal)
            if direction.length<1e-5:raise ValueError('Missing actual shoulder cloth tangent')
            row_frames[row]=(target,normal.copy(),direction.normalized(),width)
    # Free-point projection collapsed adjacent vertices in24. A coherent
    # tangent cross-section preserves the fabric width and has no point snaps.
    if coherent:
        for row,(top,normal,direction,width) in row_frames.items():
            for bow in (.06,.12,.24,.40):
                free=[]
                for column in range(12):
                    t=(12-column)/12
                    p=top+direction*width*t+normal*bow*t*t
                    free.append(p)
                signs=[]
                for p in free:
                    hit,n,_,_=trees[0].find_nearest(p);signs.append((p-hit).dot(n)*scale)
                if min(signs)>=-1e-6:break
            else:raise ValueError('Coherent initial cross-section still intersects skin at row%s'%row)
            for column,p in enumerate(free):points[1395+row*13+column]=tuple(p)
    for index in (() if coherent else sorted(changed-set(pins))):
        p=Vector(points[index]);gap=(.005+.007*int(index>=1395+1248))/scale
        # Restore only initial clearance lost by the row translation. Source
        # anatomy is read-only; no free vertex is pinned or corrected in motion.
        for tree in trees:
            hit,normal,_,distance=tree.find_nearest(p)
            if hit is not None and distance*scale<.06 and (p-hit).dot(normal)*scale<.0025:
                p=hit+normal*gap;free_corrections+=1
        points[index]=tuple(p)
    errors=[]
    for index in sorted(pins):
        if index<1395:continue
        p=Vector(points[index]);nearest=min((tree.find_nearest(p) for tree in trees),key=lambda r:r[3])
        skin=trees[0].find_nearest(p)
        if (p-skin[0]).dot(skin[1])*scale<.0025:errors.append(int(index))
        if nearest[3]*scale>(.005+.007*int(index>=1395+1248))+.008:errors.append(int(index))
    if errors:raise ValueError('Held-border contact preflight failed: %s'%sorted(set(errors)))
    return {'corrections':corrections,'free_initial_clearance_corrections':free_corrections,
            'coherent_tangent_rows':len(row_frames),
            'actual_skin_normal_envelope':body_envelope,
            'actual_contact_preflight':'PASS','post_solve_projection':False,
            'scope':'Numeric held-contact only, not an integrated visual PASS'}


def downward_cross_sections(points,scale,original):
    """Rebuild only initial free rows in the gravity-projected skin tangent.

    A consistent tangent-cross-normal sign still turned a front row upward
    where its support guide doubled back. Gravity fixes the intended fall.
    """
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    tree=tree_for(bpy.data.objects['MF_studio_adult_body'])
    guides=[Vector(points[1395+r*13+12]) for r in range(192)]
    normals=[tree.find_nearest(p)[1] for p in guides]
    for _ in range(4):
        normals=[n if r in (0,191) else (normals[r-1]*.25+n*.5+normals[r+1]*.25).normalized()
                 for r,n in enumerate(normals)]
    maximum_front_up=-100.;gravity=Vector((0,0,-1))
    for row,(top,n) in enumerate(zip(guides,normals)):
        direction=gravity-n*gravity.dot(n)
        if direction.length<1e-4:direction=Vector((top.x,top.y-.14,0))
        direction.normalize()
        width=(Vector(original[1395+row*13])-Vector(original[1395+row*13+12])).length+.15*(abs(top.x)/2.)**2
        for bow in (.02,.05,.10,.20,.30,.50):
            free=[top+direction*width*((12-c)/12)+n*bow*((12-c)/12)**2 for c in range(12)]
            signs=[]
            for p in free:
                hit,normal,_,_=tree.find_nearest(p);signs.append((p-hit).dot(normal)*scale)
            if min(signs)>=-1e-6:break
        else:raise ValueError('Downward initial section intersects skin at row%s'%row)
        if top.y<-.55:
            maximum_front_up=max(maximum_front_up,free[0].z-top.z)
            if free[0].z>=top.z:raise ValueError('Front cloth lower border rises above support at row%s'%row)
        for column,p in enumerate(free):points[1395+row*13+column]=tuple(p)
    return {'initial_free_sections_follow_projected_gravity':True,
            'front_lower_border_max_up_native':maximum_front_up,
            'scope':'Initial authored fall only; not a visual/physics PASS','post_solve_projection':False}


def sparse_shoulder_attachments(pins):
    result={i:w for i,w in pins.items() if i<1395}
    for row in (24,72,119,167):
        result[1395+row*13+12]=1.
        result[1395+row*13+11]=.7
    return result


def continuous_contact_pattern(points,pins,scale,original,transport=False):
    """Dress a continuous contact guide, then regrow coherent cross-sections.

    This replaces discontinuous independently projected rows. Only initial
    garment authoring is involved; every later free point is native cloth.
    """
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    names=('MF_studio_adult_body','MF_fit_tunic_173_visible',
           'MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible',
           'MF_173_tension_harness_-1','MF_173_tension_harness_1')
    trees=[tree_for(bpy.data.objects[name]) for name in names]
    guides=[Vector(points[1395+r*13+12]) for r in range(192)]
    held={(i-1395)//13 for i in pins if i>=1395}
    def envelope(p,row):
        hit,n,_,_=trees[0].find_nearest(p)
        root=hit-n*.02;extent=.02
        for tree in trees:
            origin=root.copy();travel=0.
            for _ in range(8):
                cross,_,_,distance=tree.ray_cast(origin,n,.7-travel)
                if cross is None:break
                travel+=distance;extent=max(extent,travel)
                origin=cross+n*1e-5;travel+=1e-5
                if travel>=.7:break
        return root+n*(extent+(.012+.007*int(row>=96))/scale),n
    # Smoothing and contact are alternated on the complete route; no isolated
    # vertex jumps are fed into hard attachment weights.
    for _ in range(18):
        guides=[p if r in (0,191) else guides[r-1]*.25+p*.5+guides[r+1]*.25
                for r,p in enumerate(guides)]
        for row in sorted(held):guides[row]=envelope(guides[row],row)[0]
    edges=[(b-a).length for a,b in zip(guides,guides[1:])]
    if max(edges)>.32:raise ValueError('Continuous guide still has a sharp contact jump: %s'%max(edges))
    normals=[trees[0].find_nearest(p)[1] for p in guides]
    for _ in range(4):
        normals=[n if r in (0,191) else (normals[r-1]*.25+n*.5+normals[r+1]*.25).normalized()
                 for r,n in enumerate(normals)]
    previous=None;max_bow=0.
    for row,top in enumerate(guides):points[1395+row*13+12]=tuple(top)
    for row,top in enumerate(guides):
        tangent=guides[min(191,row+1)]-guides[max(0,row-1)]
        direction=tangent.cross(normals[row]).normalized()
        authority=Vector(original[1395+row*13])-Vector(original[1395+row*13+12])
        if transport and previous is not None:
            if direction.dot(previous)<0:direction=-direction
        elif direction.dot(authority)<0:direction=-direction
        if previous is not None and direction.dot(previous)<0:raise ValueError('Continuous cloth direction flips at row%s'%row)
        previous=direction.copy();width=authority.length+.15*(abs(top.x)/2.)**2
        for bow in (.02,.05,.10,.20,.30,.50):
            free=[top+direction*width*((12-c)/12)+normals[row]*bow*((12-c)/12)**2 for c in range(12)]
            signs=[]
            for p in free:
                hit,n,_,_=trees[0].find_nearest(p);signs.append((p-hit).dot(n)*scale)
            if min(signs)>=-1e-6:break
        else:raise ValueError('Continuous initial row intersects skin: %s'%row)
        max_bow=max(max_bow,bow)
        for c,p in enumerate(free+[top]):points[1395+row*13+c]=tuple(p)
    return {'continuous_held_guide':True,'held_rows':len(held),'maximum_guide_edge_native':max(edges),
            'continuous_frame_transport':transport,
            'maximum_initial_bow_native':max_bow,'actual_contact_preflight':'PASS',
            'scope':'Initial guide/skin continuity only; not visual or dynamic contact PASS',
            'post_solve_projection':False}


def flat_ribbon_rest(points,original,components,matched_guide=False):
    """Preserve head rest, unroll one open ribbon with modest authored ease.

    Separate material metric from its posed starting surface. This is an
    authored diagnostic cut pattern, not a textile/garment certification.
    """
    if components!=[1395,2496] or len(points)!=3891 or len(original)!=3891:
        raise ValueError('Fixed flat-ribbon rest topology required')
    result=[tuple(p) for p in points[:1395]];length=0.
    for row in range(192):
        if row:
            source=points if matched_guide else original;column=12 if matched_guide else 6
            a=source[1395+(row-1)*13+column];b=source[1395+row*13+column]
            length+=math.sqrt(sum((a[k]-b[k])**2 for k in range(3)))*(1.01 if matched_guide else 1.08)
        a=original[1395+row*13];b=original[1395+row*13+12]
        width=(sum(math.sqrt(sum((points[1395+row*13+c+1][k]-points[1395+row*13+c][k])**2 for k in range(3))) for c in range(12))*1.01 if matched_guide else
               math.sqrt(sum((a[k]-b[k])**2 for k in range(3)))*1.15)
        result.extend((length,(column/12-.5)*width,0.) for column in range(13))
    return result


def flat_head_rest(source):
    """Unroll the original cut metric rather than preserving a bag-shaped rest.

    Source is the fixed pre-dressed45x31 pattern, not a solved or projected
    headfall. This only changes rest metric; actual supports remain unchanged.
    """
    if len(source)!=1395:raise ValueError('Fixed head cut required')
    across=[0.]
    for column in range(1,31):across.append(across[-1]+math.dist(source[column-1],source[column]))
    result=[];length=0.
    for row in range(45):
        if row:length+=math.dist(source[(row-1)*31+15],source[row*31+15])
        result.extend((distance,length,0.) for distance in across)
    return result


def cloth_profile(points,faces,scale):
    """Mean vertex mass from dressed area, not whole-garment mass per vertex.

    350g/m² is an authored diagnostic material hypothesis, not a measured
    textile specification. Uniform lumping is approximate. Effector gain is
    an authored compensation, not a calibrated meteorological wind speed.
    """
    area=0.
    for face in faces:
        a=points[face[0]]
        for j in range(1,len(face)-1):
            b=tuple((points[face[j]][k]-a[k])*scale for k in range(3))
            c=tuple((points[face[j+1]][k]-a[k])*scale for k in range(3))
            cross=(b[1]*c[2]-b[2]*c[1],b[2]*c[0]-b[0]*c[2],b[0]*c[1]-b[1]*c[0])
            area+=.5*math.sqrt(sum(x*x for x in cross))
    if not 0<area<10 or not math.isfinite(area):raise ValueError('Invalid bounded cloth area')
    density=.35;total=area*density;mass=total/len(points)
    return {'estimated_dressed_area_m2':area,'authored_density_kg_m2':density,
            'estimated_total_mass_kg':total,'vertex_mass':mass,
            'bending_stiffness':max(1e-6,.035*mass/.22),'effector_gain':mass/.22,
            'material_calibration':'Approximate authored diagnostic, not measured fabric or wind'}


def ribbon_ends(points,components):
    """Concealed rear tacks link head panel to the two ends of one ribbon."""
    if components!=[1395,2496] or len(points)!=3891:
        raise ValueError('Fixed ribbon topology required')
    edges=[];used=set()
    for row in (0,191):
        for column in (3,5,7,9):
            target=1395+row*13+column;p=points[target]
            choice=min((i for i in range(24*31,1395) if i not in used),
                       key=lambda i:sum((points[i][k]-p[k])**2 for k in range(3)))
            used.add(choice);edges.append((choice,target))
    return edges
