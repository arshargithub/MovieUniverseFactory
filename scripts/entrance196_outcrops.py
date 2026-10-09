"""Compose low embedded outcrops from the existing licensed rock asset."""
import json, os, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    from mathutils import Vector, Matrix
    from mathutils.bvhtree import BVHTree
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'outcrops30'}:raise ValueError('Fixed composition only')
    source=base.BASE/'entrance196-ground25/scene.blend';out=base.BASE/'entrance196-outcrops30'
    record=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=record['native_sha256']:raise ValueError('Unbound source')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.frame_set(217);bpy.context.view_layer.update();base.check_protected()
    land=bpy.data.objects['AS_valley_landform'];ev=land.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
    tree=BVHTree.FromPolygons([tuple(v.co) for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear()
    rows=[];meshes={}
    for ob in scene.objects:
        if not ob.name.startswith(('MF196_rock_cluster_','MF196_scanned_scree_','MF196_path_chip_')):continue
        if ob.data.name not in meshes:meshes[ob.data.name]=np.array([v.co[:] for v in ob.data.vertices])
        p=meshes[ob.data.name];matrix=np.array(ob.matrix_local);linear=matrix[:3,:3].copy()
        # Request world-up compression, not local-axis scaling of randomly
        # oriented stones. Blender decomposes the assigned object matrix;
        # therefore the reopened actual footprint is checked independently
        # by controls31/verify33, not inferred from this desired matrix.
        linear[2]*=.62
        q=p@linear.T;x,y=ob.location.x,ob.location.y
        point,normal,_,_=tree.ray_cast(Vector((x,y,1000)),Vector((0,0,-1)))
        if point is None:raise ValueError('Outside terrain')
        ground=point.z-q[:,0]*normal.x/normal.z-q[:,1]*normal.y/normal.z
        z=-float(np.percentile(q[:,2]-ground,53))
        new=matrix.copy();new[:3,:3]=linear;new[:3,3]=(x,y,z);ob.matrix_local=Matrix(new.tolist())
        rows.append({'name':ob.name,'below_fraction':float((q[:,2]+z<ground).mean()),'inner_edge':float(min(abs(q[:,0]+x)))})
    if min(r['inner_edge'] for r in rows)<4.19:raise ValueError('Corridor regression')
    caches=[]
    for ob in scene.objects:
        for mod in ob.modifiers:
            if mod.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(mod.filepath)).resolve();mod.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':mod.frame_start})
    (out/'support.json').write_text(json.dumps({'rows':rows,'method':'53rd vertex-height percentile against local terrain plane; world-up compression .62; horizontal extents preserved'},indent=2)+'\n')
    base.check_protected();bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':base.digest(source),'native_sha256':base.digest(out/'scene.blend'),'caches':caches,'outcrops':len(rows),'motion_unchanged_from':'entrance196-build02','visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
