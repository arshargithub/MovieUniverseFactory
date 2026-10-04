"""Fixed internal scarf/hair profile diagnosis, not an appearance pass."""
import json


def run(out):
    import bpy
    import numpy as np
    from wardrobe_studio import neutral,make_materials,pose_wardrobe,SOURCE,SOURCE_SHA
    from wardrobe_riding_fit import fit_render,digest
    neutral(bpy.data.objects['MF_body156_fit_rig']);pose_wardrobe(make_materials())
    bpy.context.scene.cycles.samples=24
    for ob in bpy.context.scene.objects:
        if ob.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus','MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_')):ob.hide_render=True
    fit_render(out,'profile-with-cloth',90,(0,.15,-1.7),7.,(800,850))
    rows={}
    for name in ('MF_natural147_hair_long hair main','MF_natural147_hair_long hair strands'):
        ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        points=np.asarray([tuple(ob.matrix_world@p.position) for p in ev.data.points])
        rows[name]={str(z):np.quantile(points[np.abs(points[:,2]-z)<.15],(0,.01,.5,.99,1),axis=0).tolist()
                    for z in (1.2,.6,0,-.6,-1.2,-1.8,-2.4) if np.any(np.abs(points[:,2]-z)<.15)}
    for ob in bpy.context.scene.objects:
        if ob.name=='MF_173_open_scarf' or ob.name.startswith('MF_173_open_scarf_seam_'):ob.hide_render=True
    fit_render(out,'profile-accepted-hair',90,(0,.15,-1.7),7.,(800,850))
    assert digest(SOURCE)==SOURCE_SHA
    (out/'result.json').write_text(json.dumps({'source_unchanged':True,'hair_slice_quantiles_0_1_50_99_100':rows,'disposition':'Internal profile diagnosis; no visual pass'},indent=2)+'\n')
