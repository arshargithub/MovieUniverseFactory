"""Metric collision copies follow actual accepted body pose correctives.

Shared protected body data is read-only. Proxy objects/modifiers alone change.
Clothes are bound to the same evaluated body, not linear bone approximations.
"""
def supports(canonical,scale,sample):
    import bpy
    from mathutils import Matrix
    import wardrobe_motion178 as foundation
    import wardrobe_motion178_controls as controls
    source=bpy.data.objects['MF_studio_adult_body']
    target=source.copy();target.name='MF178_support_exact_metric_body_target'
    bpy.context.scene.collection.objects.link(target)
    target.parent=None;target.matrix_world=Matrix.Scale(scale,4)@source.matrix_world
    target.hide_render=True;target.hide_viewport=False
    for mod in target.modifiers:
        if mod.type=='ARMATURE':mod.object=canonical
        if mod.type=='SUBSURF':mod.show_viewport=False;mod.show_render=False
    body=target.copy();body.name='MF178_support_exact_metric_body_collision'
    bpy.context.scene.collection.objects.link(body)
    if len(body.data.polygons)>12000:
        dec=body.modifiers.new('Collision-only pose-evaluated reduction','DECIMATE')
        dec.ratio=12000/len(body.data.polygons)
    body.modifiers.new('Exact pose body collision','COLLISION')
    body.collision.thickness_outer=.0025;body.collision.cloth_friction=8
    result=[body]
    for name in ('MF_fit_tunic_173_visible','MF_171_fitted_sleeve_L_173_visible',
                 'MF_171_fitted_sleeve_R_173_visible','MF_173_tension_harness_-1',
                 'MF_173_tension_harness_1','MF_173_static_groom_clearance','MF_continuous_head_neck'):
        proxy=foundation.solver_support(bpy.data.objects[name],scale)
        bpy.context.view_layer.objects.active=proxy
        for mod in list(proxy.modifiers):
            if mod.type=='DECIMATE':bpy.ops.object.modifier_apply(modifier=mod.name)
        if name in ('MF_173_static_groom_clearance','MF_continuous_head_neck'):
            controls.bind(proxy,canonical,scale=scale,chest_only=True)
        else:controls.bind_render_surface(proxy,target)
        result.append(proxy)
    return result,target

def body_parity(target,scale):
    import bpy
    import numpy as np
    source=bpy.data.objects['MF_studio_adult_body']
    states=[(m,m.show_viewport) for m in source.modifiers if m.type=='SUBSURF']
    hidden=source.hide_viewport
    try:
        source.hide_viewport=False
        for mod,_ in states:mod.show_viewport=False
        bpy.context.view_layer.update()
        def coordinates(ob):
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
            points=np.array([ob.matrix_world@v.co for v in mesh.vertices]);ev.to_mesh_clear()
            return points
        original=coordinates(source);metric=coordinates(target)/scale
        if original.shape!=metric.shape:raise ValueError('Metric body corrective topology mismatch')
        error=float(np.max(np.abs(original-metric)))
        if error>3e-6:raise ValueError('Metric body pose-corrective parity fails: %s'%error)
        return error
    finally:
        for mod,visible in states:mod.show_viewport=visible
        source.hide_viewport=hidden;bpy.context.view_layer.update()
