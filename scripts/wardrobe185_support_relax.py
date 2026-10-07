"""Matched held-pose control: release demonstrably suspended shoulder pins.

The only experimental variable is the shoulder support weight. Retain crown,
rear support, cloth-to-cloth stitches, authored metric and actual contacts.
This is a static construction test, not a replacement moving asset.
"""
import json
from pathlib import Path
import numpy as np


def shoulder_supports(ids):
    ids=np.asarray(ids,dtype=int)
    result=np.zeros(len(ids),dtype=bool)
    for offset in (2501,4853):
        local=ids-offset;rows=local//21
        result|=(local>=0)&(local<2352)&np.isin(rows,[27,28,29,83,84,85])
    return result


def shoulder_stitches(points):
    """Short concealed joins between adjacent fabric panels, not body pins."""
    p=np.asarray(points);pairs=[];used=set()
    if p.shape!=(7205,3) or not np.isfinite(p).all():raise ValueError('Unexpected cloth points')
    for layer,offset in enumerate((2501,4853)):
        for row in (27,28,29,83,84,85):
            index=offset+row*21+12
            candidates=range(2501) if layer==0 else range(2501,4853)
            pool=[j for j in candidates if j not in used and p[j,0]*p[index,0]>0]
            target=min(pool,key=lambda j:np.linalg.norm(p[j]-p[index]))
            if np.linalg.norm(p[target]-p[index])*.12292759120464325>.08:
                raise ValueError('Shoulder join exceeds construction travel')
            pairs.append((index,target));used.add(target)
    return pairs


def run(out):
    import bpy
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_gallop import JOINED_TRAJECTORY_SHA
    from wardrobe185_convex import CONTACT_SHA
    from wardrobe_doublewrap185 import cloth_settings
    from wardrobe_shawl180 import measures
    trajectory=BASE/'wardrobe185-gallopcloth05/trajectory.npz'
    contact_path=BASE/'wardrobe185-convexcontact04/contact.npz'
    if digest(trajectory)!=JOINED_TRAJECTORY_SHA or digest(contact_path)!=CONTACT_SHA:raise ValueError('Unbound support control')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(trajectory,allow_pickle=False) as data:
        p=data['frames'][168];f=data['faces'];rest=data['rest'];ids=data['pin_indices'];weights=data['pin_weights'];counts=data['counts']
    with np.load(contact_path,allow_pickle=False) as data:contacts={k:data[k] for k in data.files if k.endswith(('_points','_faces'))}
    stitches=json.loads((trajectory.parent/'front-tail-seams.json').read_text())['pairs']
    scale=.12292759120464325;released=shoulder_supports(ids)
    if released.sum()!=36:raise ValueError('Unexpected support semantics')
    report={}
    sewn=out.name.endswith('supportrelax03')
    if sewn:
        joins=shoulder_stitches(p);stitches=stitches+joins
        (out/'shoulder-joins.json').write_text(json.dumps({'pairs':joins,'initial_distances_m':[float(np.linalg.norm(p[a]-p[b])*.12292759120464325) for a,b in joins]},indent=2)+'\n')
    for label,release in ((('sewn',True),) if sewn else (('unchanged',False),('released',True))):
        bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
        scene.render.fps=24;scene.gravity=(0,0,-9.81);scene.unit_settings.scale_length=1.
        domain=bpy.data.collections.new('Same regional contacts');scene.collection.children.link(domain)
        for key in ('torso','armL','armR','head','groom'):
            mesh=bpy.data.meshes.new(key);mesh.from_pydata((contacts[key+'_points']*scale).tolist(),[],contacts[key+'_faces'].tolist());mesh.update()
            ob=bpy.data.objects.new(key,mesh);domain.objects.link(ob)
            ob.modifiers.new('Collision','COLLISION');ob.collision.thickness_outer=.0015;ob.collision.cloth_friction=15
        mesh=bpy.data.meshes.new('Same settled cut');mesh.from_pydata((p*scale).tolist(),stitches,f.tolist());mesh.update()
        ob=bpy.data.objects.new('Held scarf',mesh);scene.collection.objects.link(ob)
        group=ob.vertex_groups.new(name='support')
        for index,w,remove in zip(ids,weights,released):
            if not (release and remove):group.add([int(index)],float(w),'REPLACE')
        ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Original fabric metric')
        key.data.foreach_set('co',(rest*scale).astype(np.float32).ravel())
        key.value=0.;ob.active_shape_key_index=0;ob.show_only_shape_key=False
        weld=ob.modifiers.new('Verified rest metric evaluation','WELD');weld.merge_threshold=1e-6
        mod=cloth_settings(ob,1,domain);s=mod.settings;s.rest_shape_key=key;s.use_dynamic_mesh=False
        s.mass=.3;s.air_damping=.2;s.bending_stiffness=.05;s.tension_stiffness=200;s.compression_stiffness=200;s.shear_stiffness=100;s.quality=24
        s.use_sewing_springs=True;s.sewing_force_max=20.;mod.point_cache.frame_end=120
        frames=[]
        for frame in range(1,121):
            scene.frame_set(frame);bpy.context.view_layer.update()
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
            q=np.array([v.co[:] for v in m.vertices])/scale;ev.to_mesh_clear()
            if q.shape!=p.shape or not np.isfinite(q).all() or abs(q).max()>30:
                np.savez_compressed(out/(label+'-failure.npz'),points=q,frames=np.array(frames))
                (out/'failure.json').write_text(json.dumps({'case':label,'frame':frame,'shape':list(q.shape),'max_abs':float(np.nanmax(abs(q))),'active_shape_key':ob.active_shape_key_index})+'\n')
                raise ValueError('Invalid support relaxation')
            frames.append(q)
            if frame%24==0:print('185 support control',label,frame,flush=True)
        np.savez_compressed(out/(label+'.npz'),frames=np.array(frames),faces=f,rest=rest,counts=counts,pin_indices=ids[~released] if release else ids)
        report[label]={'released_count':int(released.sum()) if release else 0,'fabric_metric':measures(rest,f,{120:q},scale),
            'last_step_m':float(np.linalg.norm(frames[-1]-frames[-2],axis=1).max()*scale)}
    (out/'result.json').write_text(json.dumps({'source_sha256':JOINED_TRAJECTORY_SHA,'cases':report,
        'hypothesis':'Shoulder holds suspend courses above actual supporting fabric; removal permits contact-supported drape',
        'visual_gate':'NOT_RUN','moving_gate':'NOT_RUN','actor_loaded':False},indent=2)+'\n')


def screen(out):
    import bpy
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import REPAIRED_SHA
    from wardrobe185_delivery import neutral_state
    from wardrobe185_interface_audit import neutral_lower
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-lowerreview07/integration-working.blend'
    if digest(source)!=REPAIRED_SHA:raise ValueError('Unbound screen actor')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    neutral_state();neutral_lower();scene=bpy.context.scene
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    cloth=bpy.data.objects['MF185_moving_shawl']
    cases=(('wardrobe185-supportrelax03','sewn'),) if out.name.endswith('supportscreen02') else tuple(('wardrobe185-supportrelax02',label) for label in ('unchanged','released'))
    for folder,label in cases:
        with np.load(BASE/folder/(label+'.npz'),allow_pickle=False) as data:p=data['frames'][-1]
        if p.shape!=(len(cloth.data.vertices),3):raise ValueError('Unexpected relaxed topology')
        cloth.data.vertices.foreach_set('co',p.astype(np.float32).ravel());cloth.data.update();bpy.context.view_layer.update()
        for angle,name in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):
            fit_render(out,label+'-'+name,angle,(0,.15,-1.7),8.,(640,640))
    check_protected()
    (out/'result.json').write_text(json.dumps({'visual_gate':'NOT_RUN','native_saved':False})+'\n')
