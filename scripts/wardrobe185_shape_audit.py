"""Identify garment components and support gaps before another shape repair.

Read-only native diagnosis. Colors and support markers are temporary; no
appearance pass or selected native is written.
"""
import json
from pathlib import Path
import numpy as np


def run(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE, digest, check_protected
    from wardrobe185_shot import REPAIRED_SHA
    from wardrobe185_gallop import JOINED_TRAJECTORY_SHA
    from wardrobe185_convex import CONTACT_SHA
    from wardrobe_doublewrap185 import color
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-lowerreview07/integration-working.blend'
    trajectory=BASE/'wardrobe185-gallopcloth05/trajectory.npz'
    contacts=BASE/'wardrobe185-convexcontact04/contact.npz'
    for path,sha in ((source,REPAIRED_SHA),(trajectory,JOINED_TRAJECTORY_SHA),(contacts,CONTACT_SHA)):
        if digest(path)!=sha:raise ValueError('Unbound shape audit source')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(trajectory,allow_pickle=False) as data:
        p=data['frames'][168];ids=data['pin_indices'];weights=data['pin_weights'];faces=data['faces']
    with np.load(contacts,allow_pickle=False) as data:
        trees={k:BVHTree.FromPolygons(data[k+'_points'].tolist(),data[k+'_faces'].tolist()) for k in ('torso','armL','armR','head','groom')}
    rows=[]
    for i,w in zip(ids,weights):
        distances={k:float(t.find_nearest(Vector(p[i]))[3])*.12292759120464325 for k,t in trees.items()}
        panel=0 if i<2501 else 1 if i<4853 else 2
        lower=faces[faces[:,0]<(2501 if panel==1 else 4853)] if panel else []
        lower_gap=None
        if len(lower):
            lower_tree=BVHTree.FromPolygons(p.tolist(),lower.tolist())
            lower_gap=float(lower_tree.find_nearest(Vector(p[i]))[3])*.12292759120464325
        rows.append({'index':int(i),'weight':float(w),'point':p[i].tolist(),'surface_distances_m':distances,'underlying_fabric_distance_m':lower_gap})
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.frame_set(169);bpy.context.view_layer.update();check_protected()
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    for ob in scene.objects:
        if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):ob.hide_render=True
    cloth=bpy.data.objects['MF185_moving_shawl'];cloth.data=cloth.data.copy()
    if out.name.endswith('shapeaudit02'):
        cloth.hide_render=True;scene.frame_set(265);bpy.context.view_layer.update()
        body=bpy.data.objects['MF_studio_adult_body'];original=body.data;body.data=original.copy()
        body.data.materials.clear();body.data.materials.append(color('diagnostic skin',(.9,0,.7)))
        for poly in body.data.polygons:poly.material_index=0
        rig=bpy.data.objects['MF_body156_fit_rig'];center=tuple(rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-1.4)))
        for angle,label in ((90,'left'),(270,'right'),(0,'front')):
            fit_render(out,'uncovered-upper-'+label,angle,center,8.,(640,640))
        body.data=original;check_protected()
        (out/'result.json').write_text(json.dumps({'source_sha256':REPAIRED_SHA,'support_distances':rows,'visual_gate':'NOT_RUN','native_saved':False},indent=2)+'\n')
        return
    for index,(name,rgb) in enumerate((('headfall',(.17,.45,.75)),('inner',(.15,.55,.25)),('outer',(.75,.24,.1)))):
        cloth.data.materials[index]=color('diagnostic '+name,rgb)
    for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):
        fit_render(out,'panels-'+label,angle,(0,.15,-1.7),8.,(640,640))
    material=color('diagnostic supports',(.9,.7,.03))
    for i in ids[weights>=.8]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.035,location=p[i])
        bpy.context.object.data.materials.append(material)
    for angle,label in ((90,'left'),(180,'rear')):
        fit_render(out,'supports-'+label,angle,(0,.15,-1.7),8.,(640,640))
    check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':REPAIRED_SHA,'support_distances':rows,
        'scope':'Component and support-location diagnosis, not final appearance','visual_gate':'NOT_RUN','native_saved':False},indent=2)+'\n')
