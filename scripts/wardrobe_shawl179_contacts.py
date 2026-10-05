"""Fixed read-only contact-motion audit for the rejected shared-seam solve."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as foundation

def main():
    import bpy
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import wardrobe_motion178_controls as controls
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe_shawl179_collision import supports
    from wardrobe_refinement import neutral
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'audit01'}:raise ValueError('Fixed contact audit only')
    if foundation.digest(foundation.SOURCE)!=foundation.SOURCE_SHA:raise ValueError('Protected source mismatch')
    out=foundation.BASE/'wardrobe179-contact-audit01'
    if out.exists():raise ValueError('Never overwrite evidence')
    out.mkdir();(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(foundation.SOURCE),load_ui=False,use_scripts=False)
    foundation.check_protected();rig,_,_=foundation.clean_foundation();dress_actor(rig);repair(rig,'repair04')
    controls.animate(rig,neutral_entry=True);scale=bpy.context.scene.unit_settings.scale_length
    canonical=controls.canonical_rig(rig,scale)
    actions=(rig.animation_data.action,canonical.animation_data.action)
    rig.animation_data.action=None;canonical.animation_data.action=None
    neutral(rig);neutral(canonical);bpy.context.view_layer.update()
    contacts,_=supports(canonical,scale,controls.body_weight_sampler())
    head=bpy.data.objects['MF_continuous_head_neck'];head_rest=head.matrix_world.copy()
    def mesh(ob,factor=1.):
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());data=ev.to_mesh()
        points=[(ob.matrix_world@v.co)/factor for v in data.vertices]
        faces=[tuple(p.vertices) for p in data.polygons];ev.to_mesh_clear();return points,faces
    groom_rest,groom_faces=mesh(bpy.data.objects['MF_173_static_groom_clearance'])
    rig.animation_data.action=actions[0];canonical.animation_data.action=actions[1]
    rows=[]
    names=('MF_fit_tunic_173_visible','MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible',
           'MF_173_tension_harness_-1','MF_173_tension_harness_1','MF_173_static_groom_clearance','MF_continuous_head_neck')
    for frame in (97,121,145):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        for name,proxy in zip(names,contacts[1:]):
            if name=='MF_173_static_groom_clearance':
                delta=head.matrix_world@head_rest.inverted()
                points=[delta@p for p in groom_rest];faces=groom_faces
            else:points,faces=mesh(bpy.data.objects[name])
            tree=BVHTree.FromPolygons(points,faces,all_triangles=False)
            actual,_=mesh(proxy,scale)
            distances=np.array([tree.find_nearest(p)[3] for p in actual])
            row={'frame':frame,'source':name,'metric_contact':proxy.name,
                 'proxy_to_actual_surface_native_quantiles':np.quantile(distances,[.5,.95,.99,1.]).tolist()}
            rows.append(row);print('179 contact parity',json.dumps(row),flush=True)
    foundation.check_protected()
    (out/'result.json').write_text(json.dumps({'protected_exact':True,'rows':rows,
        'scope':'Contact-to-visible-surface motion comparison, not appearance or cloth acceptance',
        'groom_expected_motion':'Actual accepted head object transform delta from neutral'},indent=2)+'\n')

if __name__=='__main__':main()
