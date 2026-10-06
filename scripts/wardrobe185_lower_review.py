"""Integrate and inspect free lower cloth without a premature visual pass."""
import json
from pathlib import Path
import numpy as np

MOUNTED_SHA='f792307a9a22a9ee6fb8039dacf11f2a826855c3bb2820e0a34e8abd6a8feaae'
STANDING_SHA='5e38a63debc3f9e8b0a7466bbd157a1506c33820e93f24ade588439163b35533'


def run(out):
    import bpy
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import WORKING_SHA
    from wardrobe_shawl180_cache import cache
    from wardrobe_riding_fit import fit_render
    from wardrobe185_lower_cloth import panel
    from wardrobe185_lower import fast_geometry
    from mathutils.bvhtree import BVHTree
    source=BASE/'wardrobe185-finishreview01/integration-working.blend'
    mounted=BASE/'wardrobe185-lowercloth01/mounted.npz';standing=mounted.parent/'standing.npz'
    for p,h in ((source,WORKING_SHA),(mounted,MOUNTED_SHA),(standing,STANDING_SHA)):
        if h is None or digest(p)!=h:raise ValueError('Unbound lower review input')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(mounted,allow_pickle=False) as d:
        frames=d['frames'][119:];faces=d['faces'];rest=d['rest'];source_frames=d['source_frame_ids'][119:]
    with np.load(standing,allow_pickle=False) as d:neutral=d['frames'][-1]
    if not np.array_equal(source_frames,np.arange(169,361)):raise ValueError('Incorrect mounted cache time range')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;old=bpy.data.objects['MF_fit_tunic_173_visible'];old.hide_render=True;old.hide_viewport=True
    for ob in scene.objects:
        if ob.name.startswith('MF_173_tunic_toggle_'):ob.hide_render=True;ob.hide_viewport=True
    ob=panel('MF185_free_lower_tunic',frames[0],faces)
    for mat in old.data.materials:ob.data.materials.append(mat)
    attr=ob.data.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT');attr.data.foreach_set('vector',rest.astype(np.float32).ravel())
    for poly in ob.data.polygons:poly.use_smooth=True
    mod=cache(ob,frames,out/'lower-cloth.mdd');mod.frame_start=169
    sub=ob.modifiers.new('Render smooth cloth','SUBSURF');sub.levels=sub.render_levels=2
    solid=ob.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.006
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO';scene.cycles.device='CPU';scene.cycles.samples=8
    scene.render.use_persistent_data=True
    contact_report={};cache_error=0.
    for frame in (169,193,217,223,265,326,360):
        scene.frame_set(frame);bpy.context.view_layer.update();sub.show_viewport=False;solid.show_viewport=False
        p,f=fast_geometry(ob);cache_error=max(cache_error,float(np.max(abs(p-frames[frame-169]))))
        tree=BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True);record={}
        for name in ('MF_fit_trousers_173_visible','MF185_gait_horse','MF185_gait_saddle','MF185_gait_saddle.pad'):
            q,cf=fast_geometry(bpy.data.objects[name]);ct=BVHTree.FromPolygons(q.tolist(),cf.tolist(),all_triangles=True)
            pairs=tree.overlap(ct);record[name]=len(pairs)
        self_pairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not set(f[a])&set(f[b])]
        record['nonadjacent_self_pairs']=len(self_pairs);contact_report[frame]=record
        sub.show_viewport=True;solid.show_viewport=True
        if frame in (169,193,217,360):
            for angle,view in ((90,'left'),(180,'rear'),(270,'right')):
                fit_render(out,'lower-'+view+'-'+str(frame),angle,(0,-.2,-6.5),7.,(640,640))
    if cache_error>2e-5:raise ValueError('Lower cache does not reproduce simulated samples')
    (out/'contact-check.json').write_text(json.dumps(contact_report,indent=2)+'\n')
    # Front is otherwise hidden by the horse; show both actual and unobscured.
    scene.frame_set(217);bpy.context.view_layer.update()
    for item in scene.objects:
        if item.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):item.hide_render=True
    fit_render(out,'lower-front-unoccluded-217',0,(0,-.2,-6.5),7.,(640,640))
    for item in scene.objects:
        if item.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):item.hide_render=False
    scene.frame_start=169;scene.frame_end=360;scene.frame_set(217);bpy.context.view_layer.update();check_protected()
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'integration-working.blend'),check_existing=False)
    native_sha=digest(out/'integration-working.blend')
    from wardrobe185_delivery import neutral_state
    neutral_state()
    ob.modifiers.remove(mod);ob.data=ob.data.copy();ob.data.vertices.foreach_set('co',neutral.astype(np.float32).ravel());ob.data.update()
    for angle,view in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):
        fit_render(out,'neutral-lower-'+view,angle,(0,-.2,-6.5),7.,(640,640))
    check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':WORKING_SHA,'mounted_sha256':MOUNTED_SHA,'standing_sha256':STANDING_SHA,
        'native_sha256':native_sha,'cache_max_error':cache_error,'protected_exact':True,'visual_gate':'NOT_RUN',
        'scope':'Integrated free lower garment diagnostic; not selected or Director approved'},indent=2)+'\n')
