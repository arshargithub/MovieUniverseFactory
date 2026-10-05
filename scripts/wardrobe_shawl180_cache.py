"""Fixed local MDD transfer of native float32 cloth samples; no payload code."""
import struct
import json
import numpy as np


def cache(ob,frames,path):
    a=np.asarray(frames,dtype=np.float32)
    if a.ndim!=3 or a.shape[2]!=3 or a.shape[1]!=len(ob.data.vertices) or not np.isfinite(a).all():
        raise ValueError('Invalid native mesh samples')
    if path.exists() or path.is_symlink():raise ValueError('Preserve cache evidence')
    with path.open('wb') as stream:
        stream.write(struct.pack('>ii',len(a),a.shape[1]))
        stream.write((np.arange(len(a),dtype=np.float32)/24).astype('>f4').tobytes())
        stream.write(a.astype('>f4').tobytes())
    mod=ob.modifiers.new('Native cloth trajectory','MESH_CACHE')
    mod.cache_format='MDD';mod.filepath=str(path);mod.deform_mode='OVERWRITE'
    mod.forward_axis='POS_Y';mod.up_axis='POS_Z';mod.flip_axis=(False,False,False)
    mod.play_mode='SCENE';mod.time_mode='FRAME';mod.frame_start=1.;mod.frame_scale=1.
    return mod


def unit(out):
    import bpy
    p=np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0]],dtype=np.float32)
    frames=np.array([p+np.array([i*.02,np.sin(i*.1)*.1,i*.01]) for i in range(48)],dtype=np.float32)
    mesh=bpy.data.meshes.new('cache-control');mesh.from_pydata(p.tolist(),[],[(0,1,2,3)]);mesh.update()
    ob=bpy.data.objects.new('cache-control',mesh);bpy.context.scene.collection.objects.link(ob)
    cache(ob,frames,out/'control.mdd');errors={}
    for frame in (1,2,24,48,12):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
        q=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear()
        errors[frame]=float(np.max(abs(q-frames[frame-1])))
    (out/'result.json').write_text(json.dumps({'errors':errors,'max_error':max(errors.values())},indent=2)+'\n')
    if max(errors.values())>2e-6:raise ValueError('Native mesh cache transfer failed')
    print('Native MDD frame transfer',errors,flush=True)
