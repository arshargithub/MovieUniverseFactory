"""Read-only integration checks plus the exact cached wind-off visual control.

Runs on a disposable copy of the pinned working integration. It does not
select the asset or convert numeric collision checks into visual acceptance.
"""
import json
from pathlib import Path
import numpy as np

OFF_SHA='a46ad4fd0b3474a95260164954096d4839096f23cd9c142b6e81d8120603fef5'


def broadphase(points,faces,lower,upper):
    """Conservative triangle AABB clipping, including spanning triangles."""
    q=np.asarray(points);f=np.asarray(faces);lo=np.asarray(lower);hi=np.asarray(upper)
    if q.ndim!=2 or q.shape[1]!=3 or f.ndim!=2 or f.shape[1]!=3 or np.any(lo>hi):raise ValueError('Invalid contact bounds')
    tri=q[f]
    return f[np.all(tri.min(1)<=hi,axis=1)&np.all(tri.max(1)>=lo,axis=1)]


def geometry(ob):
    import bpy
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
    p=np.array([ob.matrix_world@v.co for v in m.vertices]);f=np.array([t.vertices[:] for t in m.loop_triangles])
    labels=np.array([m.polygons[t.polygon_index].material_index for t in m.loop_triangles])
    ev.to_mesh_clear();return p,f,labels


def run(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import WORKING_SHA
    from wardrobe185_gallop import JOINED_TRAJECTORY_SHA
    from wardrobe_shawl180_cache import cache
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-finishreview01/integration-working.blend'
    on=BASE/'wardrobe185-gallopcloth05/trajectory.npz';off=BASE/'wardrobe185-gallopoff05/trajectory.npz'
    for p,h in ((source,WORKING_SHA),(on,JOINED_TRAJECTORY_SHA),(off,OFF_SHA)):
        if h is None or p.is_symlink() or digest(p)!=h:raise ValueError('Unbound integration audit source')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;check_protected();rig=bpy.data.objects['MF_body156_fit_rig']
    cloth=bpy.data.objects['MF185_moving_shawl'];skirt=bpy.data.objects['MF_fit_tunic_173_visible']
    dependencies=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                path=Path(bpy.path.abspath(m.filepath)).resolve()
                if not path.is_relative_to(BASE) or not path.is_file():raise ValueError('Missing/outside native cache')
                dependencies.append({'object':ob.name,'path':str(path.relative_to(BASE)),'sha256':digest(path),'bytes':path.stat().st_size})
    (out/'cache-dependencies.json').write_text(json.dumps(dependencies,indent=2)+'\n')
    # Locate the known neutral-entry intersections, not just their count.
    states=[(m,m.show_viewport) for m in cloth.modifiers if m.type=='SOLIDIFY']
    for m,_ in states:m.show_viewport=False
    scene.frame_set(169);bpy.context.view_layer.update();p,f,labels=geometry(cloth)
    trees=[BVHTree.FromPolygons(p.tolist(),f[labels==i].tolist(),all_triangles=True) for i in range(3)]
    hits=[]
    for a in range(3):
        for b in range(a+1,3):
            fa=f[labels==a];fb=f[labels==b]
            for i,j in trees[a].overlap(trees[b]):
                hits.append({'layers':[a,b],'a':p[fa[i]].tolist(),'b':p[fb[j]].tolist()})
    for m,state in states:m.show_viewport=state
    (out/'entry-contact-locations.json').write_text(json.dumps({'frame':169,'intersections':hits,'visual_gate':'NOT_RUN'},indent=2)+'\n')
    # Lower garment versus actual visible body/pants/horse/saddle surfaces.
    # Counts are tri-tri diagnostics, not proof of visible penetration or ease.
    skirt_states=[(m,m.show_viewport) for m in skirt.modifiers if m.type=='SOLIDIFY']
    for m,_ in skirt_states:m.show_viewport=False
    targets=['MF_fit_trousers_173_visible','MF185_gait_horse','MF185_gait_saddle','MF185_gait_saddle.pad']
    if any(n not in bpy.data.objects for n in targets):raise ValueError('Missing lower garment contact target')
    lower=[];points=[];edges=None
    for frame in range(217,361):
        scene.frame_set(frame);bpy.context.view_layer.update();p,f,_=geometry(skirt)
        if edges is None:edges=np.unique(np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1),axis=0)
        points.append(p);tree=BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True);pairs={}
        for name in targets:
            q,g,_=geometry(bpy.data.objects[name]);g=broadphase(q,g,p.min(0)-.02,p.max(0)+.02)
            if not len(g):pairs[name]={'pairs':0,'skirt_centers':[]};continue
            other=BVHTree.FromPolygons(q.tolist(),g.tolist(),all_triangles=True)
            crossings=tree.overlap(other)
            pairs[name]={'pairs':len(crossings),'skirt_centers':[p[f[i]].mean(0).tolist() for i in sorted({i for i,j in crossings})]}
        lower.append({'frame':frame,'targets':pairs})
        if frame%24==0:print('185 lower contact audit',frame,flush=True)
    for m,state in skirt_states:m.show_viewport=state
    np.savez_compressed(out/'lower-motion.npz',frames=np.array(points),edges=edges)
    (out/'lower-contact.json').write_text(json.dumps({'frames':lower,'visual_gate':'NOT_RUN'},indent=2)+'\n')
    # The filmed range starts after dressing/lean. Inspect the intermediate
    # position separately instead of inheriting an older construction's pass.
    for ob in scene.objects:
        if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):ob.hide_render=True
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    scene.frame_set(193);bpy.context.view_layer.update()
    center=tuple(rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-.6)))
    for angle,label in ((0,'front'),(90,'left'),(180,'rear')):
        fit_render(out,'partial-'+label+'-193',angle,center,8.,(640,640))
    # Wind-off preserves topology, construction, supports and actor action.
    with np.load(off,allow_pickle=False) as data:frames=data['frames']
    for m in list(cloth.modifiers):
        if m.type=='MESH_CACHE':cloth.modifiers.remove(m)
    mod=cache(cloth,frames,out/'wind-off.mdd');bpy.context.view_layer.objects.active=cloth
    while list(cloth.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    for ob in scene.objects:
        if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):ob.hide_render=True
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    for frame in (217,360):
        scene.frame_set(frame);bpy.context.view_layer.update()
        center=tuple(rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-.6)))
        for angle,label in ((0,'front'),(180,'rear')):fit_render(out,'off-'+label+'-%03d'%frame,angle,center,8.,(640,640))
    check_protected()
    # Reuse the settled upper drape in the compatible actual standing rest.
    # Review this derivative before any neutral-master selection.
    from wardrobe185_delivery import neutral_state
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    neutral_record=neutral_state();scene=bpy.context.scene;scene.cycles.device='CPU';scene.cycles.samples=8
    (out/'wardrobe185_delivery.py').write_bytes(Path(__file__).with_name('wardrobe185_delivery.py').read_bytes())
    for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):
        fit_render(out,'neutral-'+label,angle,(0,.15,-1.7),8.,(640,640))
    fit_render(out,'neutral-whole',0,(0,0,-6.4),18.,(576,864))
    (out/'result.json').write_text(json.dumps({'source_sha256':WORKING_SHA,'windoff_sha256':OFF_SHA,
        'protected_exact':True,'native_changed':False,'neutral_staging':neutral_record,
        'visual_gate':'NOT_RUN','selected':False},indent=2)+'\n')
