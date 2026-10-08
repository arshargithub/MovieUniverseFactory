"""Export the new evaluated horse articulation in the retained actor frame."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SHA='f2bf98d21e3d087a96299f7911a34cd05b57c9d74395036e4265ffec128450eb'

def main():
    import bpy
    from mathutils import Matrix,Vector
    from entrance189_groom import write_mdd,read_mdd
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'export08'}:raise ValueError('Fixed export required')
    source=base.BASE/'entrance190-route-horse04/horse-route.blend';out=base.BASE/'entrance190-route-export08'
    if out.exists() or source.is_symlink() or base.digest(source)!=SHA:raise ValueError('Changed source or prior output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene
    with np.load(source.parent/'route.npz',allow_pickle=False) as z:data={k:z[k] for k in z.files}
    names=('horse','saddle','saddle.pad','saddle.stirrup','saddle.stirrup.strap','bridle','bridle.body','bit','Torus.002')
    source_cache=base.BASE/'wardrobe185-horsecache01'
    arrays={};counts={}
    for name in names:
        prior=read_mdd(source_cache/(name+'.mdd'));counts[name]=prior.shape[1]
        arrays[name]=np.lib.format.open_memmap(out/(name+'.npy'),mode='w+',dtype=np.float32,shape=(193,counts[name],3))
    saddles=[];bits=[];records=[]
    registration=Matrix.Translation((0,.20,-6.85))@Matrix.Scale(8.3,4)@Matrix.Translation((0,0,-1.57))
    for f in range(193):
        scene.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        idx=f*8
        # Actual path matrix includes the original source pivot translation.
        # Undo only world travel/rotation, leaving -2.52 source-centering in
        # place; existing native object registration offsets remain intact.
        path=bpy.data.objects['horse diagnostic path'].matrix_world@Matrix.Translation((0,2.52,0))
        transform=registration@path.inverted()
        saddles.append(np.array(transform@bpy.data.objects['saddle'].matrix_world))
        for name in names:
            ob=bpy.data.objects[name];ev=ob.evaluated_get(deps);me=ev.to_mesh()
            p=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',p)
            if len(me.vertices)!=counts[name]:raise ValueError('Topology mismatch '+name)
            mat=np.array(transform@ev.matrix_world);q=p.reshape(-1,3)@mat[:3,:3].T+mat[:3,3];ev.to_mesh_clear()
            if not np.isfinite(q).all():raise ValueError('Nonfinite cache')
            arrays[name][f]=q
            if name=='bit':
                ends=[]
                for sign in (1,-1):
                    side=q[q[:,0]*sign>0];ends.append(side[side[:,0]*sign>=np.quantile(side[:,0]*sign,.8)].mean(0))
                bits.append(ends)
        if f%24==0:print('190 export frame',f,flush=True)
    for name,a in arrays.items():
        a.flush();write_mdd(out/(name+'.mdd'),193,counts[name],iter(a))
    np.savez_compressed(out/'contacts.npz',saddle_matrices=np.array(saddles),bit_points=np.array(bits),**data)
    (out/'result.json').write_text(json.dumps({'source_sha256':SHA,'frame_start':361,'frames':193,
        'coordinate_system':'Retained actor local frame; new world path is a separate common transform',
        'topology_counts':counts,'caches':{n:base.digest(out/(n+'.mdd')) for n in names},
        'contacts_sha256':base.digest(out/'contacts.npz'),'visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
