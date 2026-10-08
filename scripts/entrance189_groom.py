"""Streaming source-bound groom derivatives; keep inherited native caches intact."""
from pathlib import Path
import struct
import numpy as np


def read_mdd(path):
    path=Path(path)
    with path.open('rb') as f:nf,nv=struct.unpack('>ii',f.read(8))
    if not (1<=nf<=400 and 1<=nv<=1000000):raise ValueError('Unexpected MDD dimensions')
    if path.stat().st_size!=8+4*nf+12*nf*nv:raise ValueError('MDD size mismatch')
    return np.memmap(path,dtype='>f4',mode='r',offset=8+4*nf,shape=(nf,nv,3))


def write_mdd(path,nf,nv,frames):
    path=Path(path)
    if path.exists():raise ValueError('Preserve cache')
    count=0
    with path.open('xb') as f:
        f.write(struct.pack('>ii',nf,nv));f.write((np.arange(nf)/24).astype('>f4').tobytes())
        for p in frames:
            if p.shape!=(nv,3) or not np.isfinite(p).all():raise ValueError('Invalid trajectory')
            f.write(p.astype('>f4').tobytes());count+=1
    if count!=nf:raise ValueError('Incomplete trajectory')


def attach_cache(ob,path,start=217):
    import bpy
    previous=[i for i,m in enumerate(ob.modifiers) if m.type=='MESH_CACHE']
    index=previous[0] if previous else 0
    for m in list(ob.modifiers):
        if m.type=='MESH_CACHE':ob.modifiers.remove(m)
    m=ob.modifiers.new('189 source-derived groom trajectory','MESH_CACHE')
    m.cache_format='MDD';m.filepath=str(path);m.deform_mode='OVERWRITE'
    m.forward_axis='POS_Y';m.up_axis='POS_Z';m.frame_start=start;m.frame_scale=1.
    m.play_mode='SCENE';m.time_mode='FRAME'
    # Cache topology belongs before the same downstream subdivision/solidify
    # stages as its source; appending it can silently invalidate all frames.
    bpy.context.view_layer.objects.active=ob
    while list(ob.modifiers).index(m)>index:
        bpy.ops.object.modifier_move_up(modifier=m.name)
    return m


def fuller_tail(scene,out):
    import bpy
    ob=bpy.data.objects['MF185_gait_Full Bushy Flowing Horse Tail']
    mod=next(m for m in ob.modifiers if m.type=='MESH_CACHE')
    a=read_mdd(bpy.path.abspath(mod.filepath));rest=np.asarray(a[0],dtype=float)
    # Stable source-index regions. Root never moves; volume increase grows
    # through the middle, then tapers rather than producing a squared fan.
    t=np.clip((rest[:,1]-6.1)/9.2,0,1);blend=np.sin(np.pi*t)**.8
    bins=np.clip((t*16).astype(int),0,15)
    roots=rest[:,1]<6.35
    rootpath=np.array([np.asarray(row)[roots].mean(0) for row in a])
    def frames():
        for i,row in enumerate(a):
            p=np.asarray(row,dtype=float).copy()
            for b in range(16):
                ids=bins==b
                if not ids.any():continue
                center=p[ids].mean(0)
                p[ids,0]=center[0]+(p[ids,0]-center[0])*(1+.65*blend[ids])
                p[ids,2]=center[2]+(p[ids,2]-center[2])*(1+.25*blend[ids])
            lag=rootpath[max(0,i-3)]-rootpath[i]
            p+=lag[None,:]*t[:,None]**2*.45
            p[:,2]-=.45*t**1.5
            p[:,0]+=.12*np.sin(i/24*4.2+t*4)*t*t
            p[roots]=row[roots]
            yield p.astype(np.float32)
    path=out/'tail.mdd';write_mdd(path,len(a),len(rest),frames());attach_cache(ob,path)
    return {'root_vertices_preserved':int(roots.sum()),'method':'Tapered cross-section volume plus source-root lag; authored not fluid dynamics'}


def mane(scene,out):
    import bpy
    from entrance188_groom import tube_frames
    ob=bpy.data.objects['MF188_flowing_mane'];mod=next(m for m in ob.modifiers if m.type=='MESH_CACHE')
    a=read_mdd(bpy.path.abspath(mod.filepath))
    if a.shape!=(144,113076,3):raise ValueError('Source groom topology changed')
    rng=np.random.default_rng(18903)
    offsets=rng.normal(0,1,(6282,1,3))*.035
    t=np.linspace(0,1,12)[None,:,None]
    def mesh_at(i):
        centers=np.asarray(a[i],dtype=np.float32).reshape(3141,12,3,3).mean(2)
        curves=np.repeat(centers,2,axis=0)
        curves+=offsets*np.sin(np.pi*t)*(.4+.6*t)
        tubes,faces=tube_frames(curves[None])
        v=tubes[0].reshape(6282,12,3,3)
        center=v.mean(2,keepdims=True)
        v=center+(v-center)*.47
        return v.reshape(-1,3),faces
    first,faces=mesh_at(0)
    old=ob.data;mesh=bpy.data.meshes.new('189 fine dense native mane')
    mesh.from_pydata(first.tolist(),[],faces);mesh.update()
    for mat in old.materials:
        m=mat.copy();shader=m.node_tree.nodes.get('Principled BSDF')
        color=shader.inputs['Base Color'].default_value
        shader.inputs['Base Color'].default_value=(color[0]*.72,color[1]*.72,color[2]*.72,1)
        shader.inputs['Roughness'].default_value=.66;shader.inputs['Specular IOR Level'].default_value=.19
        mesh.materials.append(m)
    labels=np.repeat(rng.choice(5,6282,p=[.24,.40,.27,.075,.015]),33)
    mesh.polygons.foreach_set('material_index',labels.astype(np.int32))
    for p in mesh.polygons:p.use_smooth=True
    ob.data=mesh;path=out/'mane.mdd'
    write_mdd(path,144,len(first),(mesh_at(i)[0] for i in range(144)))
    attach_cache(ob,path)
    return {'guides':6282,'individual_radius_ratio':.47,'source_centerline_root_preserved':True,
            'method':'Denser finer fibers on fixed source trajectories; no new per-frame projection'}
