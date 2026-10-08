"""Source-bound coordinated absorption and flexible-tail shot derivative.

Not a general biomechanics rig or universal garment simulation. Existing cloth
simulation receives a small verified skeletal-space corrective; retain that
qualification boundary explicitly in the result.
"""
import json
import sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance193_inspect import SOURCE_SHA
from entrance189_groom import read_mdd,write_mdd,attach_cache


def phase_signal(saddles):
    z=np.asarray(saddles)[:,2,3]
    v=np.gradient(z);v=np.convolve(np.pad(v,(2,2),mode='edge'),[1,2,3,2,1],mode='valid')/9
    return v/max(abs(v).max(),1e-8)


def tail_chain(rest,roots,substeps=8):
    """Damped articulated chain, pinned root, fixed segment lengths.

    Authored gravity/air/rest-curvature response, not measured equine hair.
    Root trajectory is the actual cache attachment, not an unrelated clock.
    """
    rest=np.asarray(rest,float);roots=np.asarray(roots,float)
    lengths=np.linalg.norm(np.diff(rest,axis=0),axis=1)
    if len(rest)<3 or lengths.min()<1e-5:raise ValueError('Degenerate tail chain')
    p=rest.copy();velocity=np.zeros_like(p);dt=1/(24*substeps);frames=[]
    for frame,root in enumerate(roots):
        for sub in range(substeps):
            prev=roots[max(0,frame-1)];anchor=prev+(root-prev)*(sub+1)/substeps
            target=rest-rest[0]+anchor
            # Distributed restoring force retains the existing tail silhouette;
            # root-driven inertia supplies lag. Drag prevents a perpetual sine.
            force=95*(target-p)-6.5*velocity
            force[:,2]-=28.;force[:,1]+=8.
            old=p.copy();velocity+=force*dt;p+=velocity*dt
            for _ in range(18):
                p[0]=anchor
                for j,L in enumerate(lengths):
                    d=p[j+1]-p[j];n=np.linalg.norm(d)
                    correction=d*(1-L/max(n,1e-9))
                    if j==0:p[j+1]-=correction
                    else:p[j]+=.5*correction;p[j+1]-=.5*correction
            p[0]=anchor;velocity=(p-old)/dt
        frames.append(p.copy())
    result=np.array(frames)
    if not np.isfinite(result).all():raise ValueError('Invalid tail response')
    return result


def frame_basis(points):
    tangent=np.gradient(points,axis=-2);tangent/=np.linalg.norm(tangent,axis=-1,keepdims=True)
    side=np.cross(tangent,[0,0,1.]);side/=np.linalg.norm(side,axis=-1,keepdims=True)
    up=np.cross(side,tangent)
    return np.stack((side,tangent,up),axis=-1)


def correct_tail(out):
    import bpy
    ob=bpy.data.objects['MF185_gait_Full Bushy Flowing Horse Tail']
    m=next(m for m in ob.modifiers if m.type=='MESH_CACHE');a=read_mdd(bpy.path.abspath(m.filepath))
    p=np.array(a[0],float);root_ids=p[:,1]<6.35
    roots=np.array([np.asarray(q)[root_ids].mean(0) for q in a])
    centers=[roots[0]]
    for y in np.linspace(6.7,15.25,17):
        ids=np.argsort(abs(p[:,1]-y))[:700]
        centers.append(np.median(p[ids],axis=0))
    centers=np.array(centers);ys=centers[:,1]
    if np.any(np.diff(ys)<=0):raise ValueError('Tail parameter is not monotonic')
    u=np.interp(p[:,1],ys,np.arange(len(ys)));lo=np.minimum(u.astype(int),len(ys)-2);w=u-lo
    ref=(1-w[:,None])*centers[lo]+w[:,None]*centers[lo+1]
    axes=frame_basis(centers);b=(1-w[:,None,None])*axes[lo]+w[:,None,None]*axes[lo+1]
    offset=np.einsum('ni,nij->nj',p-ref,b)
    chains=tail_chain(centers,roots);frames=[]
    for i,c in enumerate(chains):
        axes=frame_basis(c);b=(1-w[:,None,None])*axes[lo]+w[:,None,None]*axes[lo+1]
        q=(1-w[:,None])*c[lo]+w[:,None]*c[lo+1]+np.einsum('ni,nji->nj',offset,b)
        # Keep every attached root vertex exact, not merely its average.
        blend=np.clip((p[:,1]-6.35)/.65,0,1);blend=blend*blend*(3-2*blend)
        near=p+roots[i]-roots[0];q=near*(1-blend[:,None])+q*blend[:,None]
        q[root_ids]=a[i,root_ids];frames.append(q.astype(np.float32))
    path=out/'tail.mdd';write_mdd(path,144,len(p),iter(frames));attach_cache(ob,path)
    length_error=np.max(abs(np.linalg.norm(np.diff(chains,axis=1),axis=2)/np.linalg.norm(np.diff(centers,axis=0),axis=1)-1))
    np.savez_compressed(out/'tail-chain.npz',rest=centers,frames=chains,roots=roots)
    return {'root_error':0.,'chain_max_relative_length_error':float(length_error),
            'tip_range_native':np.ptp(chains[:,-1],axis=0).tolist(),
            'method':'Damped length-constrained root-driven chain; retained fuller tail cross section; authored coefficients, not calibrated simulation'}


def animate(out):
    import bpy
    from mathutils import Matrix,Quaternion,Vector
    from wardrobe185_riding import limb
    from wardrobe_motion178_controls import render_geometry_paused
    from wardrobe185_grip import rein_channel
    from wardrobe185_mount_fit import rein_points
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    with np.load(base.BASE/'entrance193-inspect01/rig.npz',allow_pickle=False) as z:
        names=list(z['names']);before=z['matrices'].copy();basis=z['bases'].copy()
    with np.load(base.BASE/'wardrobe185-horsecache01/contacts.npz',allow_pickle=False) as z:
        saddles=z['saddle_matrices'].copy();bits=z['bit_points'].copy()
    phase=phase_signal(saddles);after=[];rows=[]
    rig.animation_data.action=rig.animation_data.action.copy()
    rig.animation_data.action.name='193 coordinated gait absorption'
    for s in ('L','R'):bpy.data.objects['MF185_rein_'+s].data.animation_data_clear()
    with render_geometry_paused():
        for i,f in enumerate(range(217,361)):
            scene.frame_set(f)
            for n,m in zip(names,basis[i]):rig.pose.bones[n].matrix_basis=Matrix(m)
            # Delayed flexion through hip/spine rather than a single rigid torso.
            drive=float(phase[i]);lag=float(phase[max(0,i-1)])
            angles={'pelvis':2.2*drive,'spine':2.3*lag,'chest':1.2*lag,
                    'MF185_neck':-3.7*lag,'MF185_head':-.9*drive}
            for n,angle in angles.items():
                b=rig.pose.bones[n];b.rotation_mode='QUATERNION'
                b.rotation_quaternion=Quaternion((1,0,0),float(np.deg2rad(angle)))@b.rotation_quaternion
            bpy.context.view_layer.update();row={'frame':f,'residuals':{},'angles_degrees':angles}
            for j,s in enumerate(('L','R')):
                for upper,lower,tip in [('thigh.','shin.','foot.'),('upperarm.','forearm.','hand.')]:
                    end=Matrix(before[i,names.index(tip+s)]);pole=Vector(before[i,names.index(lower+s),:3,3])
                    row['residuals'][tip+s]=limb(rig,upper+s,lower+s,tip+s,end.translation,pole,end)
                channel=rein_channel(rig,s);points=rein_points(bits[i,j]+np.array((0,0,-1.05)),channel)
                ob=bpy.data.objects['MF185_rein_'+s]
                if len(ob.data.splines[0].points)!=len(points):raise ValueError('Unexpected reins')
                for point,co in zip(ob.data.splines[0].points,points):
                    point.co=(*co,1);point.keyframe_insert(data_path='co',frame=f)
            for b in rig.pose.bones:
                loc,rot,scale=b.matrix_basis.decompose();b.rotation_mode='QUATERNION'
                b.location=loc;b.rotation_quaternion=rot;b.scale=scale
                for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(data_path=prop,frame=f)
            bpy.context.view_layer.update();after.append([np.array(rig.matrix_world@b.matrix) for b in rig.pose.bones]);rows.append(row)
    sys.path.insert(0,str(ROOT/'src/movie_factory/adapters/blender'))
    from worker import action_channels
    for fc in action_channels(rig.animation_data.action):
        for k in fc.keyframe_points:
            if k.co.x>=217:k.interpolation='LINEAR'
    np.savez_compressed(out/'rig.npz',names=names,before=before,after=after,phase=phase)
    (out/'motion.json').write_text(json.dumps(rows,indent=2)+'\n')
    return names,before,np.array(after)


def cloth_transport(out,names,before,after):
    import bpy
    scene=bpy.context.scene
    def delta(n,i):return after[i,names.index(n)]@np.linalg.inv(before[i,names.index(n)])
    records=[]
    for name,filename in [('MF185_moving_shawl','shawl'),('MF185_free_lower_tunic','lower')]:
        ob=bpy.data.objects[name];m=next(m for m in ob.modifiers if m.type=='MESH_CACHE')
        a=read_mdd(bpy.path.abspath(m.filepath));start=int(m.frame_start);world=np.array(ob.matrix_world);inv=np.linalg.inv(world)
        def frames():
            for k,row in enumerate(a):
                i=k+start-217;p=np.array(row,float)
                if 0<=i<144:
                    q=p@world[:3,:3].T+world[:3,3]
                    if filename=='lower':
                        d=delta('pelvis',i);q=q@d[:3,:3].T+d[:3,3]
                    else:
                        # Blend in the old head's coordinates so the influence
                        # travels with anatomy rather than fixed world height.
                        d=delta('chest',i);moved=q@d[:3,:3].T+d[:3,3]
                        height=q[:,2]-before[i,names.index('MF185_head'),2,3]
                        w=np.clip((height+1.2)/1.8,0,1);w=w*w*(3-2*w)
                        d=delta('MF185_head',i);h=q@d[:3,:3].T+d[:3,3]
                        q=moved*(1-w[:,None])+h*w[:,None]
                    p=q@inv[:3,:3].T+inv[:3,3]
                yield p.astype(np.float32)
        path=out/(filename+'.mdd');write_mdd(path,len(a),a.shape[1],frames());attach_cache(ob,path,start)
        records.append({'object':name,'method':'Small skeletal-space corrective of retained simulation; contact and visual validation required'})
    return records


def pants(out):
    import bpy
    from wardrobe185_lower_cloth import sample
    from wardrobe185_trouser_seat import fixed_surface
    from wardrobe_motion178_controls import render_geometry_paused
    bind=base.BASE/'wardrobe185-trouserseat03/binding.npz'
    if base.digest(bind)!='968014f166312df4b31a3ddc4987173b0f3ba457bb97cfde12071b484f9b73f5':raise ValueError('Changed pants binding')
    with np.load(bind,allow_pickle=False) as z:d={k:z[k] for k in z.files}
    body=bpy.data.objects['MF_studio_adult_body'];ob=bpy.data.objects['MF_fit_trousers_173_visible']
    frames=[]
    with render_geometry_paused():
        body.hide_viewport=False
        for f in range(217,361):
            bpy.context.scene.frame_set(f);bpy.context.view_layer.update();p=sample(body)
            q=fixed_surface(p[d['body_triangle_indices']],d['barycentric_weights'],d['clearance'])
            if q.shape!=(len(ob.data.vertices),3):raise ValueError('Body binding mismatch')
            frames.append(q.astype(np.float32))
            if f%24==0:print('193 refit',f,flush=True)
    path=out/'pants.mdd';write_mdd(path,144,len(ob.data.vertices),iter(frames));attach_cache(ob,path)


def main():
    import bpy
    import os
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'motion02'}:raise ValueError('Fixed motion operation required')
    source=base.BASE/'entrance190-blink03/scene.blend';out=base.BASE/'entrance193-motion02'
    if out.exists() or base.digest(source)!=SOURCE_SHA:raise ValueError('Source changed or evidence exists')
    record=json.loads((base.BASE/'entrance193-inspect01/result.json').read_text())
    if record['source_sha256']!=SOURCE_SHA:raise ValueError('Inspection source mismatch')
    for o in record['objects']:
        for m in o['modifiers']:
            if m['type']=='MESH_CACHE' and base.digest(Path(m['path']))!=m['sha256']:raise ValueError('Changed source cache')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);base.check_protected()
    names,before,after=animate(out);cloth=cloth_transport(out,names,before,after);tail=correct_tail(out);pants(out)
    scene=bpy.context.scene;scene.frame_start=217;scene.frame_end=360;scene.frame_set(217)
    caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve()
                if not p.is_relative_to(base.BASE.resolve()):raise ValueError('External cache')
                caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
                m.filepath=str(p)
    base.check_protected();bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True,check_existing=False)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True,check_existing=False)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'native_sha256':base.digest(out/'scene.blend'),
        'tail':tail,'cloth':cloth,'caches':caches,'visual_gate':'NOT_RUN','contact_gate':'NOT_RUN',
        'scope':'Fixed six-second proof only; new motion not accepted or general simulation qualified'},indent=2)+'\n')


if __name__=='__main__':main()
