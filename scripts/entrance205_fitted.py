"""Exchange205 fixed fitted-pants/tack renewal, adapted from validated190 handler."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

BIND_SHA='968014f166312df4b31a3ddc4987173b0f3ba457bb97cfde12071b484f9b73f5'


def main():
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe185_lower import fast_geometry
    from wardrobe185_lower_cloth import sample
    from wardrobe185_lower_drape import triangle_weights
    from wardrobe185_trouser_seat import fixed_surface
    from wardrobe185_grip import rein_channel
    from wardrobe185_mount_fit import rein_points
    from wardrobe_motion178_controls import render_geometry_paused
    from entrance189_groom import attach_cache,write_mdd,read_mdd
    from entrance188_groom import triangle_frames
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'fitted08'},{'operation':'fitted20'},{'operation':'fitted31'},{'operation':'fitted36'}):raise ValueError('Fixed fitted continuation required')
    folders={'fitted08':'rider05','fitted20':'rider19','fitted31':'rider30','fitted36':'rider35'}
    source=base.BASE/('entrance205-'+folders[job['operation']])/'scene.blend';out=base.BASE/('entrance205-'+job['operation'])
    SOURCE_SHA=json.loads((source.parent/'result.json').read_text())['native_sha256']
    binding=base.BASE/'wardrobe185-trouserseat03/binding.npz'
    contact=base.BASE/'wardrobe185-lowerrecontact02/surfaces.npz'
    if out.exists() or base.digest(source)!=SOURCE_SHA or base.digest(binding)!=BIND_SHA or base.digest(contact)!='88479a1a2e6dc0e839bf58507b65a462e58da37bebc1529105823bbc8dfde329':raise ValueError('Unbound fitted inputs')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    with np.load(binding,allow_pickle=False) as z:bind={k:z[k] for k in z.files}
    with np.load(contact,allow_pickle=False) as z:old={k:z[k] for k in z.files}
    with np.load(base.BASE/('entrance205-export29' if job['operation'] in ('fitted31','fitted36') else 'entrance205-export03')/'contacts.npz',allow_pickle=False) as z:contacts={k:z[k] for k in z.files}
    with np.load(base.BASE/'wardrobe185-horsecache01/contacts.npz',allow_pickle=False) as z:saddle_reference=z['saddle_matrices'][0,:3,3].copy()
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);base.check_protected()
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    pants=bpy.data.objects['MF_fit_trousers_173_visible'];stirrup=bpy.data.objects['MF185_gait_saddle.stirrup']
    names={'pants':pants,'upper':bpy.data.objects['MF185_fitted_upper_tunic'],'horse':bpy.data.objects['MF185_gait_horse'],
           'saddle':bpy.data.objects['MF185_gait_saddle'],'pad':bpy.data.objects['MF185_gait_saddle.pad']}
    shells=[(m,m.show_viewport) for ob in names.values() for m in ob.modifiers if m.type=='SOLIDIFY']
    for m,_ in shells:m.show_viewport=False
    flags=[]
    # Bind once against the previous final pose, not against a moving nearest
    # surface every frame. Restore the selected new caches immediately after.
    previous=json.loads((base.BASE/'entrance189-performance14/result.json').read_text())
    for row in previous['caches']:
        if row['object'] not in [o.name for o in names.values()]:continue
        ob=bpy.data.objects[row['object']]
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                path=(base.BASE/'entrance189-performance14'/row['path']).resolve()
                if base.digest(path)!=row['sha256']:raise ValueError('Old bind pose cache changed')
                flags.append((m,m.filepath,m.frame_start));m.filepath=str(path);m.frame_start=1 if ob==pants else 217
    scene.frame_set(360);bpy.context.view_layer.update();maps={};reference={}
    for key,ob in names.items():
        p,f=fast_geometry(ob);q=old[key+'_frames'][-1];tree=BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True)
        ids=[];bary=[];offset=[]
        for point in q:
            hit,_,face,distance=tree.find_nearest(Vector(point));tri=f[face]
            ids.append(tri);bary.append(triangle_weights(hit,p[tri]));offset.append(np.array(point)-np.array(hit))
        ids=np.array(ids);bary=np.array(bary);basis=triangle_frames(p[ids]);offset=np.einsum('ni,nij->nj',offset,basis)
        maps[key]=(ids,bary,offset);reference[key]=p
    pelvis=rig.pose.bones['pelvis'];pm0=np.array(rig.matrix_world@pelvis.matrix@pelvis.bone.matrix_local.inverted())
    for m,path,start in flags:m.filepath=path;m.frame_start=start
    required=set(names.values())|{body,stirrup}
    boots={s:[o for o in scene.objects if o.name.startswith(('MF_173_work_boot_','MF_173_boot_')) and ('_'+s) in o.name and o.type=='MESH'] for s in ('L','R')}
    for v in boots.values():required.update(v)
    for _ in range(8):
        for ob in list(required):
            for m in ob.modifiers:
                for prop in ('target','object'):
                    target=getattr(m,prop,None)
                    if isinstance(target,bpy.types.Object):required.add(target)
    pants_array=np.lib.format.open_memmap(out/'pants.npy',mode='w+',dtype=np.float32,shape=(289,len(pants.data.vertices),3))
    rings=[];straps={s:[] for s in ('L','R')};surfaces={k:[] for k in names};pelvis_mats=[];rows=[]
    for s in ('L','R'):bpy.data.objects['MF185_rein_'+s].data.animation_data_clear()
    with render_geometry_paused():
        for o in required:o.hide_viewport=False
        for i in range(289):
            frame=361+i;scene.frame_set(frame);bpy.context.view_layer.update()
            bp=sample(body)
            if bind['body_triangle_indices'].max()>=len(bp):raise ValueError('Body topology no longer matches fitted trouser binding')
            pq=fixed_surface(bp[bind['body_triangle_indices']],bind['barycentric_weights'],bind['clearance'])
            if len(pq)!=len(pants.data.vertices):raise ValueError('Fitted pants topology changed')
            pants_array[i]=pq
            for key,ob in names.items():
                p=pq if key=='pants' else fast_geometry(ob)[0];ids,bary,offset=maps[key]
                tri=p[ids];q=(tri*bary[:,:,None]).sum(1)+np.einsum('ni,nji->nj',offset,triangle_frames(tri))
                if not np.isfinite(q).all():raise ValueError('Invalid contact transport')
                surfaces[key].append(q.astype(np.float32))
            pelvis_mats.append(np.array(rig.matrix_world@pelvis.matrix@pelvis.bone.matrix_local.inverted()))
            p=fast_geometry(stirrup)[0];row={'frame':frame,'contacts':{}}
            for j,(side,sign) in enumerate((('L',1),('R',-1))):
                foot=rig.pose.bones['foot.'+side];head=rig.matrix_world@foot.head;tail=rig.matrix_world@foot.tail
                target=head+(tail-head).normalized()*.6
                sole=min(float(fast_geometry(o)[0][:,2].min()) for o in boots[side]);target.z=sole+.015
                ids=np.where(p[:,0]*sign>0)[0];a=p[ids];bottom=a[a[:,2]<a[:,2].min()+.15]
                center=(bottom.min(0)+bottom.max(0))*.5;center[2]=a[:,2].min()+.10;p[ids]+=np.array(target)-center
                top=Vector(p[ids][np.argmax(p[ids,2])]);anchor=Vector((sign*2.2,.2,-7.6))+Vector(contacts['saddle_matrices'][i,:3,3]-saddle_reference)
                middle=anchor.lerp(top,.5)+Vector((sign*.1,0,0));v=[]
                for pt in (anchor,middle,top):v.extend([list(pt+Vector((0,-.08,0))),list(pt+Vector((0,.08,0)))])
                straps[side].append(v);channel=rein_channel(rig,side);bit=contacts['bit_points'][i,j]+np.array((0,0,-1.05))
                points=rein_points(bit,channel);ob=bpy.data.objects['MF185_rein_'+side]
                if len(ob.data.splines[0].points)!=len(points):raise ValueError('Unexpected rein topology')
                for point,co in zip(ob.data.splines[0].points,points):point.co=(*co,1);point.keyframe_insert(data_path='co',frame=frame)
                row['contacts'][side]={'sole_z':sole,'stirrup_plate_target':list(target),'grip':list(channel[0]),'bit':bit.tolist()}
            rings.append(p);rows.append(row)
            if i%24==0:print('205 fitted garments and tack',frame,flush=True)
    pants_array.flush();write_mdd(out/'pants.mdd',289,pants_array.shape[1],iter(pants_array));attach_cache(pants,out/'pants.mdd',361)
    write_mdd(out/'stirrups.mdd',289,len(rings[0]),iter(rings));attach_cache(stirrup,out/'stirrups.mdd',361)
    for side,v in straps.items():
        ob=bpy.data.objects['MF185_stirrup_leather_'+side];a=np.array(v,dtype=np.float32)
        write_mdd(out/('leather-'+side+'.mdd'),289,a.shape[1],iter(a));attach_cache(ob,out/('leather-'+side+'.mdd'),361)
    for m,state in shells:m.show_viewport=state
    np.savez_compressed(out/'lower-contacts.npz',frame_ids=np.arange(361,650),pelvis_matrices=np.array(pelvis_mats),reference_pelvis=pm0,
        **{k+'_frames':np.array(v) for k,v in surfaces.items()},**{k+'_faces':old[k+'_faces'] for k in names})
    (out/'tack.json').write_text(json.dumps(rows,indent=2)+'\n')
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':m.filepath=bpy.path.abspath(m.filepath)
    scene.frame_set(409);bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'native_sha256':base.digest(out/'scene.blend'),
        'lower_contacts_sha256':base.digest(out/'lower-contacts.npz'),'pants_binding_sha256':BIND_SHA,'visual_gate':'NOT_RUN'},indent=2)+'\n')


if __name__=='__main__':main()
