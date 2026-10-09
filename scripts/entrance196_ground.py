"""Bind dressing to actual rendered terrain, not a historical analytic proxy."""
import json,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from entrance188_ground import bank_height
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'ground25'}:raise ValueError('Fixed terrain admission required')
    source=base.BASE/'entrance196-seat17/scene.blend';out=base.BASE/'entrance196-ground25'
    if out.exists() or base.digest(source)!='063db28d8384f58c8373b447312622c44bcaa35dc6c2a2ef4d5406fabf3d1dad':raise ValueError('Source changed')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(217);bpy.context.view_layer.update();base.check_protected()
    land=bpy.data.objects['AS_valley_landform'];rows=[]
    if np.max(abs(np.array(land.matrix_local)-np.eye(4)))>1e-5:raise ValueError('Unexpected terrain local transform')
    evaluated=land.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    tree=BVHTree.FromPolygons([tuple(v.co) for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons])
    evaluated.to_mesh_clear()
    for o in scene.objects:
        if not o.name.startswith(('MF196_rock_cluster_','MF196_scanned_scree_','MF196_path_chip_')):continue
        x,y=o.location.x,o.location.y
        point,normal,index,distance=tree.ray_cast(Vector((x,y,1000)),Vector((0,0,-1)))
        if point is None:raise ValueError('Dressing outside actual terrain')
        delta=float(point.z-bank_height(x,y));o.location.z+=delta
        rows.append({'object':o.name,'actual_height':point.z,'analytic_height':bank_height(x,y),'delta':delta})
    (out/'terrain-binding.json').write_text(json.dumps({'rows':rows,'delta_range':np.percentile([r['delta'] for r in rows],[0,25,50,75,100]).tolist()},indent=2)+'\n')
    print('actual terrain placement deltas',np.percentile([r['delta'] for r in rows],[0,25,50,75,100]),flush=True)
    caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    base.check_protected();bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':base.digest(source),'native_sha256':base.digest(out/'scene.blend'),'caches':caches,'actual_terrain_bound_rocks':len(rows),'motion_unchanged_from':'entrance196-build02','visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
