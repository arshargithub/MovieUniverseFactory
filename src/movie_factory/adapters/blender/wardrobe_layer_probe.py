"""Fixed diagnostic layer isolation; never a Director appearance candidate."""
import json


def run(out):
    import bpy
    from wardrobe_studio import neutral,make_materials,pose_wardrobe,SOURCE,SOURCE_SHA
    from wardrobe_riding_fit import fit_render,digest
    from wardrobe_refinement import tree_for
    neutral(bpy.data.objects['MF_body156_fit_rig']);mats=make_materials();pose_wardrobe(mats)
    bpy.context.scene.cycles.samples=24
    for ob in bpy.context.scene.objects:
        if ob.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus','MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_')):ob.hide_render=True
    def render(label):fit_render(out,label,-40,(0,-.3,-3.2),4.,(750,750))
    render('all-layers')
    head=[o for o in bpy.context.scene.objects if o.name=='MF_173_open_scarf' or o.name.startswith('MF_173_open_scarf_seam_')]
    wrap=bpy.data.objects['MF_173_diagonal_scarf_fall']
    tree=tree_for(wrap);clearances=[]
    for v in bpy.data.objects['MF_173_open_scarf'].data.vertices:
        if v.co.z>-2.5:continue
        hit,n,_,distance=tree.find_nearest(v.co)
        if hit is not None and distance<1.1:clearances.append((v.co-hit).dot(n))
    for ob in head:ob.hide_render=True
    render('head-fall-hidden')
    for ob in head:ob.hide_render=False
    wrap.hide_render=True;bpy.data.objects['MF_173_scarf_bound_edge'].hide_render=True
    render('chest-wrap-hidden')
    assert digest(SOURCE)==SOURCE_SHA
    (out/'result.json').write_text(json.dumps({'source_unchanged':True,'head_fall_raw_to_evaluated_wrap_signed_range':[min(clearances),max(clearances)] if clearances else None,'disposition':'Internal layer-isolation diagnosis; not appearance acceptance'},indent=2)+'\n')
