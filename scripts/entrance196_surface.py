"""Inspect actual rock support and material displacement before more placement edits."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'surface29'}:raise ValueError('Fixed surface audit only')
    source=base.BASE/'entrance196-ground25/scene.blend';out=base.BASE/'entrance196-surface29';record=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=record['native_sha256']:raise ValueError('Unbound source')
    out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(217);bpy.context.view_layer.update()
    land=bpy.data.objects['AS_valley_landform'];ev=land.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();tree=BVHTree.FromPolygons([tuple(v.co) for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear()
    rows=[];matrices=[]
    for ob in scene.objects:
        if not ob.name.startswith('MF196_rock_cluster_'):continue
        p=np.array([v.co[:] for v in ob.data.vertices]);world=np.array(ob.matrix_world);q=p@world[:3,:3].T+world[:3,3]
        point,normal,_,_=tree.ray_cast(Vector((ob.location.x,ob.location.y,1000)),Vector((0,0,-1)))
        ground=point.z-(q[:,0]-point.x)*normal.x/normal.z-(q[:,1]-point.y)*normal.y/normal.z
        gap=q[:,2]-ground
        rows.append({'name':ob.name,'location':list(ob.location),'below_fraction':float((gap<0).mean()),'gap_percentiles':np.percentile(gap,[0,10,25,50,100]).tolist()})
    mat=bpy.data.objects['MF196_rock_cluster_0'].data.materials[0];nodes=[]
    for n in mat.node_tree.nodes:
        nodes.append({'name':n.name,'type':n.type,'inputs':{i.name:(str(i.default_value) if not i.is_linked else 'LINK:'+i.links[0].from_node.name) for i in n.inputs if hasattr(i,'default_value')}})
    r={'support':rows,'material':mat.name,'displacement_method':getattr(mat,'displacement_method','unknown'),'nodes':nodes,'native_modified':False}
    (out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
    print('below fraction percentiles',np.percentile([x['below_fraction'] for x in rows],[0,25,50,75,100]),flush=True)
    print('material displacement',r['displacement_method'],[n for n in nodes if n['type'] in ('DISPLACEMENT','OUTPUT_MATERIAL')],flush=True)

if __name__=='__main__':main()
