"""Fixed cached-trajectory playback and renderer screening for wardrobe178.

No job-supplied code/paths, no new physics claims and no visual PASS writer.
Caller validates exact source/cache bytes before opening this assembly.
"""
import time
import json


def preview_gpu(scene):
    """Opt into an available native Metal device in this worker only.

    No preference saving, install or remote rendering. CPU fallback is explicit
    evidence, never a claim that the GPU was used.
    """
    import bpy
    result={'requested':'METAL','selected':'CPU','device_types':[],'error':None}
    try:
        preferences=bpy.context.preferences.addons['cycles'].preferences
        preferences.compute_device_type='METAL'
        preferences.refresh_devices()
        for device in preferences.devices:
            device.use=device.type=='METAL'
            if device.use:result['device_types'].append(device.type)
        if result['device_types']:
            scene.cycles.device='GPU';result['selected']='GPU'
        else:scene.cycles.device='CPU'
    except (TypeError,ValueError,RuntimeError,AttributeError) as error:
        scene.cycles.device='CPU';result['error']=type(error).__name__
    return result


def assembly(recipe,record):
    import bpy
    import numpy as np
    import wardrobe_studio as studio
    import wardrobe_motion178_controls as controls
    from wardrobe_motion178_playback import absolute_cache
    rig,mats,_=recipe.clean_foundation()
    points,faces,_,components=recipe.clean_patterns(periodic=True)
    initial=record['initial'];frames=record['frames']
    if initial.shape!=(len(points),3) or frames.shape!=(192,len(points),3):
        raise ValueError('Fixed moving04 cache topology required')
    if not np.isfinite(frames).all() or np.max(np.abs(frames))>100:
        raise ValueError('Invalid cache bounds')
    # Reproduce the actual moving04 material-coordinate starting layout.
    points=[tuple(p) for p in initial]
    for index in range(components[0]+components[1],len(points)):
        p=list(points[index]);p[2]+=.25*controls.smooth((-p[1]-.2)/1.2)
        points[index]=tuple(p)
    sample=controls.body_weight_sampler()
    for name in ('MF_fit_tunic_173_visible','MF_171_fitted_sleeve_L_173_visible',
                 'MF_171_fitted_sleeve_R_173_visible','MF_173_tension_harness_-1',
                 'MF_173_tension_harness_1','MF_173_waist_belt'):
        controls.bind(bpy.data.objects[name],rig,sample)
    for name in ('MF_173_belt_buckle','MF_173_buckle_tongue'):
        ob=bpy.data.objects[name]
        if not any(c.type=='CHILD_OF' and c.target==rig for c in ob.constraints):
            constraint=ob.constraints.new('CHILD_OF');constraint.name='MF178 rigid belt fitting'
            constraint.target=rig;constraint.subtarget='pelvis'
            constraint.inverse_matrix=(rig.matrix_world@rig.pose.bones['pelvis'].matrix).inverted()
    for ob in bpy.context.scene.objects:
        if '_seam_' in ob.name or 'harness_welt' in ob.name:ob.hide_render=True
    controls.animate(rig)
    display=studio.panel('MF178_moving_shawl',points,faces,mats['scarf'],.014,1)
    absolute_cache(display,frames)
    scene=bpy.context.scene;scene.frame_start=97;scene.frame_end=288;scene.render.fps=24
    scene.frame_set(97);bpy.context.view_layer.update()
    recipe.check_protected()
    return display


def screen(out,recipe,record):
    import bpy
    from mathutils import Vector
    import wardrobe_studio as studio
    from wardrobe_riding_fit import fit_render
    assembly(recipe,record)
    scene=bpy.context.scene;scene.cycles.samples=12
    target=studio.torso_matrix(-2.7)@Vector((0,.15,-1.7))
    fit_render(out,'cycles-frame097',0,tuple(target),8.,(540,600))
    for engine in ('BLENDER_EEVEE','BLENDER_EEVEE_NEXT'):
        try:scene.render.engine=engine;break
        except (TypeError,ValueError):continue
    else:raise ValueError('No native Eevee renderer; do not substitute silently')
    start=time.monotonic()
    fit_render(out,'eevee-frame097',0,tuple(target),8.,(480,540))
    seconds=time.monotonic()-start
    (out/'result.json').write_text(json.dumps({'purpose':'Cache reconstruction and renderer screen',
           'visual_gate':'NOT_RUN','protected_exact':True,'preview_engine':scene.render.engine,
           'eevee_first_frame_seconds':seconds},indent=2)+'\n')
