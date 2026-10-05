"""Native cloth for the fixed approved one-course recipe, not a general runner."""
import json
from pathlib import Path


def simulate(out,rig,mats,groom,points,faces,pins,stitches,wind_off=False,integrated=False):
    import bpy
    import numpy as np
    import wardrobe_studio as studio
    import wardrobe_motion178 as foundation
    import wardrobe_motion178_controls as controls
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_motion178_playback import absolute_cache
    from wardrobe_refinement import neutral
    scale=bpy.context.scene.unit_settings.scale_length
    sample=controls.body_weight_sampler()
    dress_actor(rig)
    if integrated:
        from wardrobe_underarm179_repair import repair
        repair(rig,'repair04')
    controls.animate(rig,neutral_entry=True)
    canonical=controls.canonical_rig(rig,scale)
    original_action=rig.animation_data.action;canonical_action=canonical.animation_data.action
    rig.animation_data.action=None;canonical.animation_data.action=None
    neutral(rig);neutral(canonical);bpy.context.view_layer.update()
    supports=[];exact_body_target=None
    if integrated:
        from wardrobe_shawl179_collision import supports as actual_supports
        supports,exact_body_target=actual_supports(canonical,scale,sample)
    for name in ('MF_studio_adult_body','MF_fit_tunic_173_visible',
                 'MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible',
                 'MF_173_tension_harness_-1','MF_173_tension_harness_1',
                 'MF_173_static_groom_clearance','MF_continuous_head_neck'):
        if integrated:continue
        support=foundation.solver_support(bpy.data.objects[name],scale,
                    faces_limit=12000 if name=='MF_studio_adult_body' else 4500)
        bpy.context.view_layer.objects.active=support
        for mod in list(support.modifiers):
            if mod.type=='DECIMATE':bpy.ops.object.modifier_apply(modifier=mod.name)
        head=name in ('MF_173_static_groom_clearance','MF_continuous_head_neck')
        controls.bind(support,canonical,sample,scale=scale,chest_only=head,
                      allow_fingers=name=='MF_studio_adult_body')
        supports.append(support)
    rig.animation_data.action=original_action;canonical.animation_data.action=canonical_action
    body_errors={}
    if exact_body_target is not None:
        from wardrobe_shawl179_collision import body_parity
        # Validate contacts at revealing poses BEFORE committing to a solve.
        # No cloth cache exists yet; rewind to the real pre-roll afterward.
        with controls.render_geometry_paused():
            for frame in (97,121,145):
                bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
                body_errors[str(frame)]=body_parity(exact_body_target,scale)
            bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    data=bpy.data.meshes.new('MF179_metric_cloth')
    data.from_pydata([tuple(scale*c for c in p) for p in points],stitches,faces);data.update()
    cloth=bpy.data.objects.new('MF178_live_solver179',data)
    bpy.context.scene.collection.objects.link(cloth);cloth.hide_render=True
    controls.bind(cloth,canonical,scale=scale,chest_only=True)
    pin=cloth.vertex_groups.new(name='Actual crown and superior front support')
    for index,weight in pins.items():pin.add([index],weight,'REPLACE')
    mod=cloth.modifiers.new('Native continuous secondary cloth','CLOTH')
    s=mod.settings;s.quality=16;s.mass=.04
    s.tension_stiffness=25;s.compression_stiffness=25;s.shear_stiffness=12;s.bending_stiffness=.015
    s.tension_damping=6;s.compression_damping=6;s.shear_damping=6;s.air_damping=1
    s.vertex_group_mass=pin.name;s.use_sewing_springs=bool(stitches);s.sewing_force_max=1.
    s.use_dynamic_mesh=False
    domain=bpy.data.collections.new('MF179_exclusive_metric_contacts')
    bpy.context.scene.collection.children.link(domain)
    for support in supports:domain.objects.link(support)
    mod.collision_settings.collection=domain
    mod.collision_settings.use_collision=True;mod.collision_settings.distance_min=.003
    mod.collision_settings.use_self_collision=True;mod.collision_settings.self_distance_min=.0015
    mod.point_cache.frame_start=1;mod.point_cache.frame_end=288
    controls.wind(gain=0. if wind_off else .04)
    scene=bpy.context.scene;scene.gravity=(0,0,-9.81);scene.render.fps=24
    frames=[];matrices=[]
    with controls.render_geometry_paused():
        for frame in range(1,289):
            scene.frame_set(frame);bpy.context.view_layer.update()
            ev=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
            coords=np.array([v.co[:] for v in mesh.vertices])/scale;ev.to_mesh_clear()
            if not np.isfinite(coords).all() or np.max(np.abs(coords))>100:
                raise ValueError('Escaped native cloth at frame%s'%frame)
            error=max(float(np.max(np.abs(np.array(b.matrix)-np.array(canonical.pose.bones[b.name].matrix))))
                      for b in rig.pose.bones)
            if error>1e-6:raise ValueError('Canonical actor-local bone mismatch')
            if exact_body_target is not None and frame in (97,121,145):
                from wardrobe_shawl179_collision import body_parity
                body_errors[str(frame)]=body_parity(exact_body_target,scale)
            if frame>=97:frames.append(coords);matrices.append(np.array(studio.torso_matrix(-1.)))
            if frame%24==0:print('179 native cloth frame',frame,flush=True)
    frames=np.array(frames);matrices=np.array(matrices)
    np.savez_compressed(out/'cloth-trajectory.npz',frames=frames,constructed_initial=np.array(points),
                        faces=np.array(faces),chest_matrices=matrices)
    display=studio.panel('MF179_continuous_shawl',points,faces,mats['scarf'],.014,1)
    with controls.render_geometry_paused():absolute_cache(display,frames)
    display['qualification']='Native cached supported/free single-shawl diagnostic; creative acceptance pending'
    scene.frame_start=97;scene.frame_end=288
    if not wind_off:
        from wardrobe_shawl179 import screens
        screens(out,(97,145))
    foundation.check_protected()
    return {'scope':'Native supported/free one-course wardrobe diagnostic',
        'protected_exact':True,'visual_gate':'NOT_RUN','complete_playback':'NOT_RUN','wind_causality':'NOT_RUN',
        'source_sha256':foundation.SOURCE_SHA,'frames':len(frames),'fps':24,'duration_seconds':8.,
        'all_frame_actor_canonical_local_bone_parity':True,'wind_off':wind_off,
        'integrated_underarm_profile':'repair04' if integrated else None,
        'metric_actual_pose_corrective_body_max_errors_native':body_errors,
        'wind_gain':0. if wind_off else .04,'solver_mass_per_vertex':s.mass,
        'settings_scope':'Authored native profile, not measured garment mass or wind calibration',
        'head_pin_scope':'Small crown region, opening edges free',
        'wrap_pin_scope':'Superior front/shoulder border; rear and lower edges free',
        'sewing_edges':stitches,'post_solve_projection':False,
        'cache_sha256':foundation.digest(out/'cloth-trajectory.npz'),
        'handler_sha256':foundation.digest(Path(__file__))}
