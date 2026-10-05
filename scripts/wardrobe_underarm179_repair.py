"""Reviewed garment-only elimination of redundant short-sleeve webbing.

Accepted anatomy remains read-only. The fitted mobility panel, rather than an
arm-to-torso stretched sheet, provides underarm coverage during flexion.
"""
def smooth(value):
    value=max(0.,min(1.,value));return value*value*(3-2*value)

def trim_weight(x,z):
    return 1.-smooth((abs(x)-1.20)/.25)*smooth((z+4.40)/.35)*smooth((-1.25-z)/.20)

def repair(rig,profile='repair01'):
    import bpy
    import wardrobe_motion178_controls as controls
    if profile not in ('repair01','repair02','repair03','repair04'):raise ValueError('Fixed garment repair profile only')
    tunic=bpy.data.objects['MF_fit_tunic_173_visible']
    rest=tunic.data.attributes['MF_173_material_coords'].data
    group=tunic.vertex_groups.new(name='MF179 torso without redundant short sleeve')
    for vertex,item in zip(tunic.data.vertices,rest):
        x,y,z=item.vector
        # Only the old short-sleeve/upper underarm sector is affected. Retain
        # the neckline, central tailoring, waist and skirt/hip flare.
        remove=abs(x)>1.32 and -4.15<z<(-2.35 if profile=='repair02' else -1.35)
        weight=trim_weight(x,z) if profile=='repair04' else (0. if remove else 1.)
        if weight:group.add([vertex.index],weight,'REPLACE')
    mask=tunic.modifiers.new('Remove short-sleeve bridge under fitted sleeve','MASK')
    mask.vertex_group=group.name
    if profile=='repair04':mask.use_smooth=True;mask.threshold=.5
    bpy.context.view_layer.objects.active=tunic
    while list(tunic.modifiers).index(mask)>0:bpy.ops.object.modifier_move_up(modifier=mask.name)
    # Use the already retained anatomical pose correctives on a read-only
    # body target. Straight armature weights alone miss shoulder/elbow support.
    target=controls.render_surface_target()
    names=('MF_fit_tunic_173_visible','MF_171_fitted_sleeve_L_173_visible',
           'MF_171_fitted_sleeve_R_173_visible')
    if profile in ('repair02','repair03','repair04'):
        names+=('MF_173_tension_harness_-1','MF_173_tension_harness_1','MF_173_waist_belt',
                'MF_173_belt_buckle','MF_173_buckle_tongue','MF_173_strap_adjuster_1')
    for name in names:
        ob=bpy.data.objects[name]
        if profile in ('repair02','repair03','repair04') and ob.type=='CURVE':
            for constraint in list(ob.constraints):
                if constraint.type=='CHILD_OF' and constraint.target==rig:ob.constraints.remove(constraint)
            bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
            bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
            ob=bpy.context.view_layer.objects.active
        for mod in list(ob.modifiers):
            if mod.type=='ARMATURE' and mod.object==rig:ob.modifiers.remove(mod)
        controls.bind_render_surface(ob,target)
    if profile in ('repair03','repair04'):
        # The whole short-sleeve sector is removed, not left as a jagged cap.
        # Extend only the fitted garment copy to fill the newly exposed join;
        # accepted skin, neckline and the main sleeve data remain unchanged.
        gusset=bpy.data.objects['MF178_render_underarm_gusset']
        coverage=gusset.vertex_groups['MF178 underarm garment coverage']
        for vertex in gusset.data.vertices:
            x,y,z=vertex.co
            if .85<abs(x)<2.75 and -4.20<z<-1.80:
                coverage.add([vertex.index],1.,'REPLACE')
        if profile=='repair04':
            for vertex in gusset.data.vertices:
                x,y,z=vertex.co
                weight=smooth((abs(x)-.80)/.10)*smooth((2.80-abs(x))/.10)*smooth((z+4.30)/.15)*smooth((-1.70-z)/.15)
                coverage.add([vertex.index],weight,'REPLACE')
            panel_mask=gusset.modifiers['Mobility panel only, not full-body clothing']
            panel_mask.use_smooth=True;panel_mask.threshold=.5
        # These lines were authored in the old static mounted pose, not the
        # regenerated neutral trousers. Their bind produces stray wrist-level
        # wires; do not certify them by hiding the defect under a shawl.
        for name in ('MF_173_trouser_outseam_L','MF_173_trouser_outseam_R'):
            bpy.data.objects[name].hide_render=True
    return {'scope':'Garment-only torso mask and surface following; accepted body unchanged',
            'profile':profile,'preserve_shoulder_overlap':profile in ('repair02','repair03','repair04'),
            'surface_bound_garments':names,'visual_gate':'NOT_RUN'}
