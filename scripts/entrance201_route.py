"""Registered rider/palette/dust continuation on the unchanged shared route."""
import json,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance189_groom import read_mdd,write_mdd,attach_cache

def animate(scene,out):
    import bpy
    from mathutils import Matrix,Vector
    from wardrobe185_riding import limb
    from entrance200_pose_control import contact
    from wardrobe_motion178_controls import render_geometry_paused
    data={}
    for key in ('opening','prior','route'):
        with np.load(base.BASE/'entrance201-inspect01'/(key+'.npz')) as z:data[key]={k:z[k] for k in z.files}
    names=list(data['route']['names']);before=data['route']['matrices'];after=[];residuals=[]
    if any(list(d['names'])!=names for d in data.values()):raise ValueError('Bone inventory drift')
    rig=bpy.data.objects['MF_body156_fit_rig'];rig.animation_data.action.use_fake_user=True
    rig.animation_data.action=rig.animation_data.action.copy();rig.animation_data.action.name='201 phase-registered absorption through gather and turn'
    keybones=('pelvis','spine','chest','MF185_neck','MF185_head')
    with render_geometry_paused():
        for i,f in enumerate(range(361,554)):
            scene.frame_set(f)
            for j,name in enumerate(names):rig.pose.bones[name].matrix_basis=Matrix(data['route']['bases'][i,j])
            for name in keybones:
                j=names.index(name);delta=data['opening']['bases'][i,j]@np.linalg.inv(data['prior']['bases'][i,j])
                rig.pose.bones[name].matrix_basis=Matrix(delta@data['route']['bases'][i,j])
            bpy.context.view_layer.update()
            row=[]
            for side in ('L','R'):
                for upper,lower,tip in [('thigh.','shin.','foot.'),('upperarm.','forearm.','hand.')]:
                    end=Matrix(before[i,names.index(tip+side)]);pole=Vector(before[i,names.index(lower+side),:3,3])
                    row.append(limb(rig,upper+side,lower+side,tip+side,end.translation,pole,end))
                contact(rig,side,1)
            for b in rig.pose.bones:
                loc,rot,scale=b.matrix_basis.decompose();b.location=loc;b.rotation_mode='QUATERNION';b.rotation_quaternion=rot;b.scale=scale
                for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(data_path=prop,frame=f)
            bpy.context.view_layer.update();after.append([np.array(b.matrix) for b in rig.pose.bones]);residuals.append(row)
    from worker import action_channels
    for fc in action_channels(rig.animation_data.action):
        for k in fc.keyframe_points:
            if k.co.x>=361:k.interpolation='LINEAR'
    after=np.array(after);np.savez_compressed(out/'rig.npz',names=names,before=before,after=after,world=data['route']['world'])
    return names,before,after,{'max_endpoint_error_native':float(np.max(residuals)),'scope':'Registered200-minus190 gait articulation added to gathered route; original hand/foot endpoints and orientations constrained; source route/root unchanged'}

def cloth(out,names,before,after):
    import bpy
    from entrance201_fit import cover_points
    scene=bpy.context.scene;scene.frame_set(361);records=[]
    for name,filename in [('MF185_moving_shawl','shawl'),('MF185_free_lower_tunic','lower')]:
        ob=bpy.data.objects[name];mod=next(m for m in ob.modifiers if m.type=='MESH_CACHE');src=Path(bpy.path.abspath(mod.filepath));a=read_mdd(src)
        if len(a)!=193 or mod.frame_start!=361:raise ValueError('Route cache clock')
        # At361 the route root is identity; both these caches and the rig
        # use the same actor coordinates. Root motion is applied once later.
        if not np.allclose(np.array(ob.matrix_world),np.eye(4),atol=1e-5):raise ValueError('Unexpected cloth basis')
        def frames():
            for i,p in enumerate(a):
                q=np.array(p,float)
                def move(bone):
                    j=names.index(bone);d=after[i,j]@np.linalg.inv(before[i,j]);return q@d[:3,:3].T+d[:3,3]
                if filename=='lower':q=move('pelvis')
                else:
                    j=names.index('MF185_head');local=q@np.linalg.inv(before[i,j])[:3,:3].T+np.linalg.inv(before[i,j])[:3,3]
                    w=np.clip((local[:,1]+1.2)/1.8,0,1);w=w*w*(3-2*w)
                    q=move('chest')*(1-w[:,None])+move('MF185_head')*w[:,None]
                    q=cover_points(q,after[i,j])
                yield q.astype(np.float32)
        path=out/(filename+'.mdd');write_mdd(path,193,a.shape[1],frames());attach_cache(ob,path,361)
        records.append({'object':name,'source_sha256':base.digest(src),'method':'Small skeletal support transport of193-frame turn simulation; headfall modestly advanced; not a new cloth solve'})
    return records

def pants(out):
    import bpy
    from wardrobe185_lower_cloth import sample
    from wardrobe185_trouser_seat import fixed_surface
    from wardrobe_motion178_controls import render_geometry_paused
    bind=base.BASE/'wardrobe185-trouserseat03/binding.npz'
    if base.digest(bind)!='968014f166312df4b31a3ddc4987173b0f3ba457bb97cfde12071b484f9b73f5':raise ValueError('Pants binding changed')
    with np.load(bind) as z:d={k:z[k] for k in z.files}
    body=bpy.data.objects['MF_studio_adult_body'];ob=bpy.data.objects['MF_fit_trousers_173_visible'];frames=[]
    with render_geometry_paused():
        body.hide_viewport=False
        for f in range(361,554):
            bpy.context.scene.frame_set(f);bpy.context.view_layer.update();p=sample(body)
            q=fixed_surface(p[d['body_triangle_indices']],d['barycentric_weights'],d['clearance'])
            if q.shape!=(len(ob.data.vertices),3):raise ValueError('Pants shape')
            frames.append(q.astype(np.float32))
    path=out/'pants.mdd';write_mdd(path,193,len(ob.data.vertices),iter(frames));attach_cache(ob,path,361)

def tail(out):
    import bpy
    from entrance193_motion import tail_chain,frame_basis
    ob=bpy.data.objects['MF185_gait_Full Bushy Flowing Horse Tail'];m=next(m for m in ob.modifiers if m.type=='MESH_CACHE');a=read_mdd(bpy.path.abspath(m.filepath))
    p=np.array(a[0],float);ids=p[:,1]<6.35;roots=np.array([np.asarray(q)[ids].mean(0) for q in a]);centers=[roots[0]]
    for y in np.linspace(6.7,15.25,17):centers.append(np.median(p[np.argsort(abs(p[:,1]-y))[:700]],axis=0))
    centers=np.array(centers);ys=centers[:,1]
    if np.any(np.diff(ys)<=0):raise ValueError('Tail nonmonotonic')
    u=np.interp(p[:,1],ys,np.arange(len(ys)));lo=np.minimum(u.astype(int),len(ys)-2);w=u-lo
    ref=(1-w[:,None])*centers[lo]+w[:,None]*centers[lo+1];axes=frame_basis(centers);b=(1-w[:,None,None])*axes[lo]+w[:,None,None]*axes[lo+1]
    offset=np.einsum('ni,nij->nj',p-ref,b);chains=tail_chain(centers,roots)
    def frames():
        for i,c in enumerate(chains):
            axes=frame_basis(c);b=(1-w[:,None,None])*axes[lo]+w[:,None,None]*axes[lo+1]
            q=(1-w[:,None])*c[lo]+w[:,None]*c[lo+1]+np.einsum('ni,nji->nj',offset,b)
            blend=np.clip((p[:,1]-6.35)/.65,0,1);blend=blend*blend*(3-2*blend)
            # Retain the existing route's bank/turn shape deviation in addition
            # to flexible root response; attached root vertices remain exact.
            route_delta=np.array(a[i],float)-(p+roots[i]-roots[0]);q+=route_delta*blend[:,None]
            q=(p+roots[i]-roots[0])*(1-blend[:,None])+q*blend[:,None];q[ids]=a[i,ids]
            yield q.astype(np.float32)
    path=out/'tail.mdd';write_mdd(path,193,len(p),frames());attach_cache(ob,path,361)
    return {'method':'Existing turn transport plus193 damped root-driven flexibility; no calibrated aerodynamics','root_error_native':0}

def environment(scene,route):
    import bpy
    from entrance198_terrain import ground,stone,TEXTURE,TEXTURE_SHA
    from entrance190_geography import fields,FLOOR
    if base.digest(TEXTURE)!=TEXTURE_SHA:raise ValueError('Paint changed')
    image=bpy.data.images.load(str(TEXTURE),check_existing=False);image.pack();image.name='201 shared pale earth'
    land=bpy.data.objects['AS_valley_landform'];land.data.materials[0]=land.data.materials[0].copy();ground(land.data.materials[0],image)
    copies={};seen=set()
    for ob in scene.objects:
        if ob.hide_render or not ob.name.startswith(('MF188_bank_stone','MF190_route_dressing','AS_stone','MF189_roadside')) or not hasattr(ob.data,'materials') or ob.data in seen:continue
        seen.add(ob.data)
        for i,m in enumerate(list(ob.data.materials)):
            if not m or not m.use_nodes or not any(n.type=='BSDF_PRINCIPLED' for n in m.node_tree.nodes):continue
            if not any(s in m.name.lower() for s in ('stone','boulder','gravel')):continue
            if m not in copies:copies[m]=m.copy();stone(copies[m],image)
            ob.data.materials[i]=copies[m]
    # Reuse approved irregular scanned rock geometry, not a new asset. Dress
    # the actual fork surface and keep transformed extents outside contacts.
    source=base.BASE/'entrance200-seal17/scene.blend'
    with bpy.data.libraries.load(str(source),link=False) as (data,to):
        candidates=[n for n in data.meshes if n=='196 weathered clustered rock shared']
        if len(candidates)!=1:raise ValueError('Approved rock mesh missing')
        to.meshes=candidates
    mesh=to.meshes[0];rng=np.random.default_rng(201);count=0;root=bpy.data.objects['AS_world_travel'];scene.frame_set(361);bpy.context.view_layer.update();origin=np.array(root.matrix_world.translation)
    rows=[];mesh_points=np.array([v.co[:] for v in mesh.vertices])
    for i in range(1800):
        x,y=rng.uniform(-600,100),rng.uniform(-790,110)
        z,d=fields(np.array([[(x-.0)/8.3,(y-.2)/8.3]]),route)
        if not 3.5<d[0]<32:continue
        s=float(rng.uniform(.18,1.5) if d[0]<7 else rng.uniform(.6,3.5));o=bpy.data.objects.new('MF201_route_stone_'+str(count),mesh);scene.collection.objects.link(o);o.parent=root
        o.scale=(s,s*rng.uniform(.7,1.2),s*.65);o.rotation_euler=(rng.uniform(.7,1.8),rng.uniform(-.5,.5),rng.uniform(0,6.283))
        v=mesh_points*np.array(o.scale);v=v@np.array(o.rotation_euler.to_matrix()).T
        if np.max(np.linalg.norm(v[:,:2],axis=1))>(d[0]-2.7)*8.3:bpy.data.objects.remove(o,do_unlink=True);continue
        o.location=np.array([x,y,FLOOR+z[0]*8.3-v[:,2].min()-.25*np.ptp(v[:,2])])-origin
        rows.append({'name':o.name,'center_route_distance_m':float(d[0]),'radius_native':float(np.max(np.linalg.norm(v[:,:2],axis=1)))});count+=1
    return {'paint_sha256':TEXTURE_SHA,'new_shared_instances':count,'clearance':rows,'terrain_geometry_unchanged':True}

def main():
    import bpy
    from entrance200_build import neck_corrective,materials
    from entrance201_dust import wake
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'route03'}:raise ValueError('Fixed route derivative')
    source=base.BASE/'entrance190-perspective29/scene.blend';out=base.BASE/'entrance201-route03'
    inspection=json.loads((base.BASE/'entrance201-inspect01/result.json').read_text())['route']
    if out.exists() or base.digest(source)!=inspection['source_sha256']:raise ValueError('Source/output')
    for row in inspection['caches']:
        if base.digest(base.BASE/row['path'])!=row['sha256']:raise ValueError('Cache changed')
    with np.load(base.BASE/'entrance190-rider09/route.npz') as z:route={k:z[k] for k in z.files}
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    for name in ('entrance201_dust.py','entrance201_fit.py'):(out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    names,before,after,motion=animate(scene,out);cloth_record=cloth(out,names,before,after);pants(out);tail_record=tail(out)
    body=bpy.data.objects['MF_studio_adult_body'];neck_corrective(body);mat=materials(scene);env=environment(scene,route);dust=wake(scene,range(361,554),route,profile='dense')
    scene.render.use_persistent_data=False;scene.frame_set(361);caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':base.digest(source),'native_sha256':base.digest(out/'scene.blend'),'caches':caches,'motion':motion,'cloth':cloth_record,'tail':tail_record,'materials':mat,'environment':env,'dust':dust,'visual_gate':'NOT_RUN'},indent=2)+'\n')
    base.check_protected()

if __name__=='__main__':main()
