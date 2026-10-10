"""Topology-preserving export of205's newly solved horse/tack articulation."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def main():
    import bpy
    from mathutils import Matrix
    from entrance189_groom import read_mdd,write_mdd
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'export03'}:raise ValueError('Fixed205 export operation')
    src=base.BASE/'entrance205-horse07/horse-route.blend';out=base.BASE/'entrance205-export03'
    r=json.loads((src.parent/'result.json').read_text())
    if out.exists() or base.digest(src)!=r['native_sha256']:raise ValueError('Source/output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);scene=bpy.context.scene
    with np.load(src.parent/'route.npz') as z:route={k:z[k] for k in z.files}
    names=('horse','saddle','saddle.pad','saddle.stirrup','saddle.stirrup.strap','bridle','bridle.body','bit','Torus.002')
    count=len(route['time'][::8]);arrays={}
    for name in names:
        prior=read_mdd(base.BASE/'wardrobe185-horsecache01'/(name+'.mdd'))
        arrays[name]=np.lib.format.open_memmap(out/(name+'.npy'),mode='w+',dtype=np.float32,shape=(count,prior.shape[1],3))
    saddles=[];bits=[]
    registration=Matrix.Translation((0,.20,-6.85))@Matrix.Scale(8.3,4)@Matrix.Translation((0,0,-1.57))
    for f in range(count):
        scene.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        path=bpy.data.objects['horse diagnostic path'].matrix_world@Matrix.Translation((0,2.52,0));transform=registration@path.inverted()
        saddles.append(np.array(transform@bpy.data.objects['saddle'].matrix_world))
        for name in names:
            ev=bpy.data.objects[name].evaluated_get(deps);me=ev.to_mesh()
            try:
                if len(me.vertices)!=arrays[name].shape[1]:raise ValueError('Topology mismatch '+name)
                p=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',p)
                mat=np.array(transform@ev.matrix_world);q=p.reshape(-1,3)@mat[:3,:3].T+mat[:3,3]
                if not np.isfinite(q).all():raise ValueError('Nonfinite export')
                arrays[name][f]=q
                if name=='bit':
                    ends=[]
                    for sign in (1,-1):
                        side=q[q[:,0]*sign>0];ends.append(side[side[:,0]*sign>=np.quantile(side[:,0]*sign,.8)].mean(0))
                    bits.append(ends)
            finally:ev.to_mesh_clear()
        if f%24==0:print('205 EXPORT',f,flush=True)
    for name,a in arrays.items():a.flush();write_mdd(out/(name+'.mdd'),count,a.shape[1],iter(a))
    np.savez_compressed(out/'contacts.npz',saddle_matrices=saddles,bit_points=bits,**route)
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'frames':count,
        'caches':{n:base.digest(out/(n+'.mdd')) for n in names},'contacts_sha256':base.digest(out/'contacts.npz'),
        'visual_gate':'NOT_RUN','coordinate_system':'Actor-local; apply common205 route root exactly once'},indent=2)+'\n')


if __name__=='__main__':main()
