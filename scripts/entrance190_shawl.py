"""Continuous double-wrap cloth solve with gathered/turning support motion."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
CONTACT_SHA='2247790d294bc80c986a32b78dad7b18de30db1239f1ba4e58281a2fb850851e'


def transformed(p,m):
    return np.einsum('fij,nj->fni',m[:,:3,:3],p)+m[:,:3,3,None].transpose(0,2,1)


def main():
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe185_redress_motion import inputs,support_selection
    from wardrobe185_convex import rear_support_indices
    from wardrobe185_motion import SCALE
    from wardrobe_doublewrap185 import cloth_settings
    from wardrobe_shawl180_cache import cache
    from wardrobe185_lower_cloth import panel,sample
    from wardrobe185_gallop import apparent_airflow
    from wardrobe185_cut import winding_inside
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'shawl11'}:raise ValueError('Fixed shawl continuation required')
    source=base.BASE/'entrance190-contacts10/contacts.npz';out=base.BASE/'entrance190-shawl11'
    if out.exists() or source.is_symlink() or base.digest(source)!=CONTACT_SHA:raise ValueError('Changed support source or prior output')
    record=json.loads((source.parent/'result.json').read_text())
    if not record['old_envelope_reusable']:raise ValueError('New anatomy not enclosed by colliders')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    with np.load(source,allow_pickle=False) as z:d={k:z[k] for k in z.files}
    p,f,rest,counts,ids,weights,stitches=inputs();ids,weights=support_selection(ids,weights)
    head=np.zeros(len(p),bool);head[:2501]=True;head[rear_support_indices(2501)]=True
    local=transformed(p,d['torso_matrices']);local[:,head]=transformed(p[head],d['head_matrices'])
    world=d['world_inertial'];drive=np.einsum('fij,fnj->fni',world[:,:3,:3],local)+world[:,:3,3,None].transpose(0,2,1)
    # Test actual pin positions against every overlapping regional volume in
    # local actor coordinates. Global rigid motion cannot change clearance.
    violations=[];rows=[]
    for frame in range(553):
        minimum=float('inf')
        for key in ('torso','armL','armR','head','groom'):
            mat=d[key+'_matrices'][frame];q=d[key+'_points']@mat[:3,:3].T+mat[:3,3];faces=d[key+'_faces']
            tree=BVHTree.FromPolygons(q.tolist(),faces.tolist(),all_triangles=True)
            inv=np.linalg.inv(mat);pins=local[frame,ids];neutral=pins@inv[:3,:3].T+inv[:3,3]
            # Hull half-spaces for convex regions, winding for groom.
            if key!='groom':
                from wardrobe185_convex import convex_outside
                inside=~convex_outside(neutral,d[key+'_points'],faces,tolerance=0.)
            else:inside=np.array([winding_inside(v,d[key+'_points'][faces]) for v in neutral])
            distances=np.array([tree.find_nearest(Vector(v))[3]*SCALE for v in pins]);distances[inside]*=-1
            minimum=min(minimum,float(distances.min()))
            for j in np.flatnonzero(distances<.0015):violations.append({'frame':frame+1,'part':key,'vertex':int(ids[j]),'signed_m':float(distances[j])})
        rows.append({'frame':frame+1,'minimum_signed_m':minimum})
    (out/'hold-preflight.json').write_text(json.dumps({'gate':'FAIL' if violations else 'PASS','violations':violations,'rows':rows},indent=2)+'\n')
    if violations:raise ValueError('Held cloth target conflicts with collision support')
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene.render.fps=24;scene.gravity=(0,0,-9.81);scene.unit_settings.scale_length=1.
    mesh=bpy.data.meshes.new('190 double wrap');mesh.from_pydata((p*SCALE).tolist(),stitches.tolist(),f.tolist());mesh.update()
    ob=bpy.data.objects.new('190 continuous double wrap',mesh);scene.collection.objects.link(ob)
    ob.shape_key_add(name='Basis');metric=ob.shape_key_add(name='Unstressed fabric')
    metric.data.foreach_set('co',(rest*SCALE).astype(np.float32).ravel());metric.value=0
    group=ob.vertex_groups.new(name='support')
    for i,w in zip(ids,weights):group.add([int(i)],float(w),'REPLACE')
    cache(ob,drive*SCALE,out/'supports.mdd')
    weld=ob.modifiers.new('Verified rest metric evaluation','WELD');weld.merge_threshold=1e-6
    domain=bpy.data.collections.new('190 exact regional contacts');scene.collection.children.link(domain)
    for key in ('torso','armL','armR','head','groom'):
        mats=np.einsum('fij,fjk->fik',world,d[key+'_matrices']);q=transformed(d[key+'_points'],mats)*SCALE
        co=panel('190 contact '+key,q[0],d[key+'_faces']);domain.objects.link(co)
        cache(co,q,out/(key+'-contact.mdd'));co.modifiers.new('Collision','COLLISION')
        co.collision.thickness_outer=.0015;co.collision.cloth_friction=15
    bpy.ops.object.effector_add(type='WIND');wind=bpy.context.object
    with np.load(base.BASE/'entrance190-rider09/route.npz',allow_pickle=False) as z:route={k:z[k] for k in z.files}
    for frame in range(1,554):
        direction,strength=apparent_airflow(frame)
        if frame>361:
            i=(frame-361)*8;angle=route['heading'][i]
            direction=np.array([-.12*np.cos(angle)-np.sin(angle),-.12*np.sin(angle)+np.cos(angle),.03])
            strength*=float(route['speed'][i]/12)**2
        wind.rotation_euler=Vector(direction).to_track_quat('Z','Y').to_euler();wind.field.strength=strength
        wind.keyframe_insert(data_path='rotation_euler',frame=frame);wind.keyframe_insert(data_path='field.strength',frame=frame)
    scene.frame_set(1);mod=cloth_settings(ob,1,domain);s=mod.settings;s.rest_shape_key=metric;s.use_dynamic_mesh=False
    s.mass=.3;s.air_damping=.2;s.bending_stiffness=.05;s.tension_stiffness=200;s.compression_stiffness=200;s.shear_stiffness=100;s.quality=24
    s.use_sewing_springs=True;s.sewing_force_max=20.;mod.point_cache.frame_end=553
    edges=np.unique(np.sort(np.concatenate([f[:,[i,(i+1)%4]] for i in range(4)]),axis=1),axis=0)
    lengths=np.linalg.norm(rest[edges[:,0]]-rest[edges[:,1]],axis=1)
    frames=[];metrics=[]
    for frame in range(1,554):
        scene.frame_set(frame);bpy.context.view_layer.update();q=sample(ob)/SCALE
        inv=np.linalg.inv(world[frame-1]);q=q@inv[:3,:3].T+inv[:3,3]
        if q.shape!=p.shape or not np.isfinite(q).all() or abs(q).max()>30:raise ValueError('Invalid actor-local cloth bounds at '+str(frame))
        frames.append(q.astype(np.float32));ratio=np.linalg.norm(q[edges[:,0]]-q[edges[:,1]],axis=1)/lengths
        row={'frame':frame,'p99':float(np.quantile(ratio,.99)),'max':float(ratio.max())};metrics.append(row)
        if frame>=169 and row['p99']>2:
            np.savez_compressed(out/'failed-prefix.npz',frames=np.array(frames));raise ValueError('Severe fabric distortion at '+str(frame))
        if frame%24==0:print('190 actual continuous cloth',frame,flush=True)
    np.savez_compressed(out/'trajectory.npz',frames=np.array(frames),faces=f,rest=rest,counts=counts,pin_indices=ids,pin_weights=weights)
    (out/'frame-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    (out/'result.json').write_text(json.dumps({'contact_sha256':CONTACT_SHA,'trajectory_sha256':base.digest(out/'trajectory.npz'),
        'frames':553,'coordinate_frame':'Constant-velocity simulation frame; delivered cache transformed back to actor-local space',
        'wind':'Authored apparent airflow force; not calibrated airspeed','visual_gate':'NOT_RUN'},indent=2)+'\n')


if __name__=='__main__':main()
