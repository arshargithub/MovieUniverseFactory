"""Continue the admitted split riding skirt through the new motion."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def main():
    import bpy
    from mathutils import Vector
    from wardrobe185_lower_cloth import panel,profile,sample
    from wardrobe185_lower_drape import support_motion
    from wardrobe185_motion import SCALE
    from wardrobe185_gallop import apparent_airflow
    from wardrobe_shawl180_cache import cache
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'lower13'},{'operation':'lower16'}):raise ValueError('Fixed lower cloth operation required')
    translating=job['operation']=='lower16'
    out=base.BASE/('entrance190-'+job['operation']);folder=base.BASE/'entrance190-fitted12'
    manifest=json.loads((folder/'result.json').read_text());source=folder/'lower-contacts.npz'
    if out.exists() or base.digest(source)!=manifest['lower_contacts_sha256']:raise ValueError('Unbound new contact source')
    paths={
        'cut':('wardrobe185-lowerdress14/initial-layout.npz','0126b7c1a268ee30eef8d94f31927c87cb428b5926ea30b2b4b573d8cdad2d27'),
        'old':('wardrobe185-lowerrecontact02/surfaces.npz','88479a1a2e6dc0e839bf58507b65a462e58da37bebc1529105823bbc8dfde329'),
        'initial':('wardrobe185-lowerhold02/initial-169.npz','b088f7fb5779df6136906a90906110e97cb17f39dcb9c2943d50156592b3605d'),
        'world':('entrance190-contacts10/contacts.npz','2247790d294bc80c986a32b78dad7b18de30db1239f1ba4e58281a2fb850851e')}
    loaded={}
    for name,(path,sha) in paths.items():
        p=base.BASE/path
        if base.digest(p)!=sha:raise ValueError('Changed '+name)
        with np.load(p,allow_pickle=False) as z:loaded[name]={k:z[k] for k in z.files}
    with np.load(source,allow_pickle=False) as z:new={k:z[k] for k in z.files}
    with np.load(base.BASE/'wardrobe185-lowercapture02/moving-source.npz',allow_pickle=False) as z:pelvis=z['pelvis_matrices']
    with np.load(base.BASE/'entrance190-rider09/route.npz',allow_pickle=False) as z:route={k:z[k] for k in z.files}
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    cut,old,initial=loaded['cut'],loaded['old'],loaded['initial'];p=initial['points'];faces=cut['faces'];pins=cut['pin_indices'];weights=cut['pin_weights']
    if not np.array_equal(initial['faces'],faces) or not np.allclose(initial['rest'],cut['rest'],atol=1e-10):raise ValueError('Changed garment cut')
    oldids=np.r_[np.full(120,169),np.arange(170,361)];frames=np.r_[oldids,np.arange(361,554)]
    lookup={int(f):i for i,f in enumerate(old['frame_ids'])};indices=[lookup[int(f)] for f in oldids]
    world=loaded['world']['world_inertial'][frames-1]
    gravity=np.repeat(np.array([[0.,0.,-9.81]]),len(frames),axis=0)
    if translating:
        # Nonrotating coordinates whose origin follows the path: rotations
        # still occur in the solver. Include -a_origin explicitly; do not
        # delete turning/braking inertia along with bulk translation.
        velocity=np.gradient(route['position'],route['time'],axis=0)
        acceleration=np.gradient(velocity,route['time'],axis=0)*8.3*SCALE
        for i,frame in enumerate(frames):
            if frame>361:
                j=(frame-361)*8
                residual=route['position'][j]-np.array([0,-12*route['time'][j],0])
                world[i,:3,3]-=8.3*residual
                gravity[i]-=acceleration[j]
        np.savez_compressed(out/'reference-frame.npz',world=world,gravity=gravity,source_frame_ids=frames)
    drive=np.repeat(p[None],len(frames),axis=0)
    drive[:311,pins]=support_motion(p[pins],cut['guided'][oldids-1][:,pins],pelvis[oldids-1],pelvis[168])
    rel=np.einsum('fij,jk->fik',new['pelvis_matrices'],np.linalg.inv(new['reference_pelvis']))
    drive[311:,pins]=np.einsum('fij,nj->fni',rel[:,:3,:3],drive[310,pins])+rel[:,:3,3,None].transpose(0,2,1)
    drive=np.einsum('fij,fnj->fni',world[:,:3,:3],drive)+world[:,:3,3,None].transpose(0,2,1)
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene.render.fps=24;scene.unit_settings.scale_length=1.;scene.gravity=(0,0,-9.81)
    if translating:
        for i,g in enumerate(gravity):scene.gravity=tuple(g);scene.keyframe_insert(data_path='gravity',frame=i+1)
    ob=panel('190 free riding skirt',p*SCALE,faces);ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Unstressed cut')
    key.data.foreach_set('co',(cut['rest']*SCALE).astype(np.float32).ravel());key.value=0
    group=ob.vertex_groups.new(name='support')
    for i,w in zip(pins,weights):group.add([int(i)],float(w),'REPLACE')
    cache(ob,drive*SCALE,out/'supports.mdd');weld=ob.modifiers.new('Explicit rest evaluation','WELD');weld.merge_threshold=1e-7
    domain=bpy.data.collections.new('190 actual lower contacts');scene.collection.children.link(domain)
    for name in ('pants','horse','saddle','pad','upper'):
        if not np.array_equal(old[name+'_faces'],new[name+'_faces']):raise ValueError('Contact topology changed')
        q=np.concatenate((old[name+'_frames'][indices],new[name+'_frames']))
        q=np.einsum('fij,fnj->fni',world[:,:3,:3],q)+world[:,:3,3,None].transpose(0,2,1)
        co=panel('190 lower contact '+name,q[0]*SCALE,new[name+'_faces']);domain.objects.link(co)
        cache(co,q*SCALE,out/(name+'-contact.mdd'));co.modifiers.new('Actual contact','COLLISION')
        co.collision.thickness_outer=.0015;co.collision.cloth_friction=15
    mod=profile(ob,domain);mod.settings.rest_shape_key=key;mod.settings.quality=48;mod.collision_settings.collision_quality=8;mod.point_cache.frame_end=len(frames)
    bpy.ops.object.effector_add(type='WIND');wind=bpy.context.object
    for i,frame in enumerate(frames):
        direction,strength=apparent_airflow(int(frame))
        if frame>361:
            j=(frame-361)*8;angle=route['heading'][j]
            direction=np.array([-.12*np.cos(angle)-np.sin(angle),-.12*np.sin(angle)+np.cos(angle),.03]);strength*=float(route['speed'][j]/12)**2
        wind.rotation_euler=Vector(direction).to_track_quat('Z','Y').to_euler();wind.field.strength=strength
        wind.keyframe_insert(data_path='rotation_euler',frame=i+1);wind.keyframe_insert(data_path='field.strength',frame=i+1)
    edges=np.unique(np.sort(np.concatenate([faces[:,[i,(i+1)%4]] for i in range(4)]),axis=1),axis=0)
    lengths=np.linalg.norm(cut['rest'][edges[:,0]]-cut['rest'][edges[:,1]],axis=1)
    trajectory=[];metrics=[]
    for i,source_frame in enumerate(frames):
        scene.frame_set(i+1);bpy.context.view_layer.update();q=sample(ob)/SCALE
        inv=np.linalg.inv(world[i]);q=q@inv[:3,:3].T+inv[:3,3]
        if q.shape!=p.shape or not np.isfinite(q).all() or abs(q).max()>30:raise ValueError('Invalid lower cloth bounds')
        trajectory.append(q.astype(np.float32));ratio=np.linalg.norm(q[edges[:,0]]-q[edges[:,1]],axis=1)/lengths
        row={'physics_frame':i+1,'source_frame':int(source_frame),'p99':float(np.quantile(ratio,.99)),'max':float(ratio.max())};metrics.append(row)
        if source_frame>=217 and row['p99']>2:
            np.savez_compressed(out/'failed-prefix.npz',frames=np.array(trajectory));raise ValueError('Severe lower garment distortion')
        if (i+1)%24==0:print('190 free skirt',json.dumps(row),flush=True)
    np.savez_compressed(out/'trajectory.npz',frames=np.array(trajectory),source_frame_ids=frames,faces=faces,rest=cut['rest'],pin_indices=pins)
    (out/'frame-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    (out/'result.json').write_text(json.dumps({'lower_contacts_sha256':manifest['lower_contacts_sha256'],
        'trajectory_sha256':base.digest(out/'trajectory.npz'),'reference_frame':'Translating nonrotating origin with gravity minus path acceleration' if translating else 'Constant-velocity origin',
        'scope':'Free skirt with original settled prefix and new rigid-frame support/contact motion; not a visual or contact pass','visual_gate':'NOT_RUN'},indent=2)+'\n')


if __name__=='__main__':main()
