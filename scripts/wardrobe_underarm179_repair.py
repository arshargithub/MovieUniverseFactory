"""Reviewed garment-only elimination of redundant short-sleeve webbing.

Accepted anatomy remains read-only. The fitted mobility panel, rather than an
arm-to-torso stretched sheet, provides underarm coverage during flexion.
"""
def repair(rig):
    import bpy
    import wardrobe_motion178_controls as controls
    tunic=bpy.data.objects['MF_fit_tunic_173_visible']
    rest=tunic.data.attributes['MF_173_material_coords'].data
    group=tunic.vertex_groups.new(name='MF179 torso without redundant short sleeve')
    for vertex,item in zip(tunic.data.vertices,rest):
        x,y,z=item.vector
        # Only the old short-sleeve/upper underarm sector is affected. Retain
        # the neckline, central tailoring, waist and skirt/hip flare.
        remove=abs(x)>1.32 and -4.15<z<-1.35
        if not remove:group.add([vertex.index],1.,'REPLACE')
    mask=tunic.modifiers.new('Remove short-sleeve bridge under fitted sleeve','MASK')
    mask.vertex_group=group.name
    bpy.context.view_layer.objects.active=tunic
    while list(tunic.modifiers).index(mask)>0:bpy.ops.object.modifier_move_up(modifier=mask.name)
    # Use the already retained anatomical pose correctives on a read-only
    # body target. Straight armature weights alone miss shoulder/elbow support.
    target=controls.render_surface_target()
    names=('MF_fit_tunic_173_visible','MF_171_fitted_sleeve_L_173_visible',
           'MF_171_fitted_sleeve_R_173_visible')
    for name in names:
        ob=bpy.data.objects[name]
        for mod in list(ob.modifiers):
            if mod.type=='ARMATURE' and mod.object==rig:ob.modifiers.remove(mod)
        controls.bind_render_surface(ob,target)
    return {'scope':'Garment-only torso mask and surface following; accepted body unchanged',
            'removed_short_sleeve_sector':'abs(rest.x)>1.32 and -4.15<rest.z<-1.35',
            'surface_bound_garments':names,'visual_gate':'NOT_RUN'}
