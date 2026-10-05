"""Audit visible leather against the actual reduced solver contact surface."""
import json
from pathlib import Path
import numpy as np


def run(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import wardrobe_motion178 as base
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe_doublewrap185_solve import inside
    from wardrobe185_cut import winding_inside
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();rig,_,_=base.clean_foundation();dress_actor(rig);repair(rig,'repair04')
    points=[];faces=[]
    for name in ('MF_173_tension_harness_-1','MF_173_tension_harness_1'):
        ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();offset=len(points)
        points.extend(tuple(ob.matrix_world@v.co) for v in mesh.vertices)
        faces.extend(tuple(offset+i for i in poly.vertices) for poly in mesh.polygons);ev.to_mesh_clear()
    p=np.array(points);f=np.array(faces)
    proxy=base.BASE/'wardrobe185-proxy02/proxy.npz'
    if base.digest(proxy)!='19cce587247a325e2f0b081f49e14eb0a40bf6c3364896a327af4639a6d4f7eb':raise ValueError('Proxy changed')
    with np.load(proxy,allow_pickle=False) as d:cp=d['points'];cf=d['faces']
    scale=.12292759120464325
    mesh=bpy.data.meshes.new('Contact audit');mesh.from_pydata((cp*scale).tolist(),[],cf.tolist());mesh.update()
    ob=bpy.data.objects.new('Contact audit',mesh);bpy.context.scene.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob
    dec=ob.modifiers.new('Actual solver reduction','DECIMATE');dec.ratio=min(1,12000/len(cf));bpy.ops.object.modifier_apply(modifier=dec.name)
    ob.data.calc_loop_triangles();v=np.array([x.co[:] for x in ob.data.vertices]);t=np.array([x.vertices[:] for x in ob.data.loop_triangles])
    tree=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True)
    samples=np.concatenate([p,p[f].mean(1)])
    sample_indices=np.flatnonzero((samples[:,2]>-4)&(samples[:,2]<0))
    results=[]
    for i in sample_indices:
        point=samples[i]*scale;q=Vector(point);h,_,_,dist=tree.find_nearest(q)
        try:within=inside(tree,q)
        except ValueError:within=winding_inside(point,v[t])
        results.append({'index':int(i),'outside':not within,'distance_m':dist,'point':samples[i].tolist()})
    outside=[r for r in results if r['outside']]
    report={'samples':len(results),'outside_count':len(outside),'max_exposure_m':max((r['distance_m'] for r in outside),default=0),
        'worst':sorted(outside,key=lambda r:r['distance_m'],reverse=True)[:20],'protected_exact':True,'visual_gate':'NOT_RUN'}
    np.savez_compressed(out/'visible-harness.npz',points=p,faces=f)
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');base.check_protected();print(json.dumps(report),flush=True)
