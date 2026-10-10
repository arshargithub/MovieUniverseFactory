"""Fixed205 actor derivatives: continuous opening and contact-owned turn rig.

Only closed repository operations, never arbitrary runtime-generated code.
The route source pose is registered by gait phase before new contact solving.
"""
import json,sys,os,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

OPENING=base.BASE/'entrance204-opening06/scene.blend'
OPENING_SHA='82532236cff228acf429c2d7072b161b6f483ddaf3710ef5513b6229d0978d60'


def facial(scene, frames, recognition=False):
    import bpy
    from entrance204_story import face_values
    from wardrobe_motion178_controls import render_geometry_paused
    from worker import action_channels
    body=bpy.data.objects['MF_studio_adult_body'];keys=body.data.shape_keys;controls={}
    for name in face_values(0):
        key=keys.key_blocks[name]
        ds=[d for d in keys.animation_data.drivers if d.data_path==key.path_from_id('value')]
        if len(ds)!=1 or len(ds[0].driver.variables)!=1:raise ValueError('Unrecognized facial driver')
        target=ds[0].driver.variables[0].targets[0]
        if target.id_type!='KEY':raise ValueError('Unrecognized facial source')
        controls[name]=target.id.key_blocks[name]
    for data in set(k.id_data for k in controls.values()):
        data.animation_data.action.use_fake_user=True;data.animation_data.action=data.animation_data.action.copy()
    for k in controls.values():
        for fc in action_channels(k.id_data.animation_data.action):
            if fc.data_path==k.path_from_id('value'):fc.keyframe_points.clear()
    def values(f):
        t=(f-315)/24 if recognition else 2.
        v=face_values(t,True)
        for n in v:
            if n.startswith(('browDown','eyeSquint','mouthPress')):v[n]*=1.2
        return v
    with render_geometry_paused():
        for f in frames:
            for name,v in values(f).items():controls[name].value=v;controls[name].keyframe_insert(data_path='value',frame=f)
        body.hide_viewport=False;errors=[]
        for f in (frames[0],frames[len(frames)//2],frames[-1]):
            scene.frame_set(f);bpy.context.view_layer.update()
            errors.append(max(abs(keys.key_blocks[n].value-v) for n,v in values(f).items()))
    if max(errors)>1e-5:raise ValueError('Facial source/output mismatch')
    return {'maximum_transfer_error':max(errors),'recognition_starts':315 if recognition else None,'muscle_gain_vs204':1.2}


def save(scene,out,record):
    import bpy
    caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve()
                if not p.is_relative_to(base.BASE.resolve()):raise ValueError('Foreign cache')
                m.filepath=str(p);caches.append(dict(object=ob.name,path=os.path.relpath(p,out),sha256=base.digest(p),start=m.frame_start))
    scene.render.use_persistent_data=False
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    record.update(native_sha256=base.digest(out/'scene.blend'),caches=caches,visual_gate='NOT_RUN')
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n');base.check_protected()


def opening(scene,out):
    import bpy
    from mathutils import Vector
    from entrance205_motion import smooth
    from wardrobe_motion178_controls import render_geometry_paused
    cam=scene.camera;rig=bpy.data.objects['MF_body156_fit_rig'];rows=[]
    with render_geometry_paused():
        for f in range(217,361):
            scene.frame_set(f);bpy.context.view_layer.update()
            h=(rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation
            target=h+Vector((0,-.4,-.4));loc=h+Vector((-8,-19.12,2.5))
            desired=(target-loc).to_track_quat('-Z','Y')
            w=float(smooth((f-292)/45))
            pos=cam.matrix_world.translation.lerp(loc,w)
            rot=cam.matrix_world.to_quaternion().slerp(desired,w)
            rows.append((f,pos,rot,cam.data.lens*(1-w)+62*w))
        if cam.animation_data and cam.animation_data.action:cam.animation_data.action.use_fake_user=True
        cam.animation_data_clear();cam.data.animation_data_clear();cam.rotation_mode='QUATERNION'
        for f,pos,rot,lens in rows:
            cam.location=pos;cam.rotation_quaternion=rot;cam.data.lens=lens
            cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_quaternion',frame=f);cam.data.keyframe_insert('lens',frame=f)
    record={'source_sha256':OPENING_SHA,'camera':'Single chronological217..360 move; continuous settle into recognition, no cut or source replay','face':facial(scene,list(range(217,361)),True)}
    np.savez_compressed(out/'camera.npz',frames=[r[0] for r in rows],positions=[r[1][:] for r in rows],quaternions=[r[2][:] for r in rows],lenses=[r[3] for r in rows])
    scene.frame_set(217);save(scene,out,record)


def linear_sample(a,f):
    i=int(np.floor(f));u=f-i
    if i<0 or i>=len(a):raise ValueError('Sample out of range')
    return np.asarray(a[i])*(1-u)+np.asarray(a[min(i+1,len(a)-1)])*u


def rider(scene,out,uphill=False,newhorse=False):
    import bpy
    from mathutils import Matrix,Quaternion,Vector
    from entrance190_rider import source_pose_frame
    from entrance205_motion import smooth
    from entrance205_camera import glance
    from wardrobe185_riding import limb
    from wardrobe_motion178_controls import render_geometry_paused
    from entrance200_pose_control import contact
    from entrance189_groom import attach_cache
    exp=base.BASE/('entrance205-export29' if newhorse else 'entrance205-export03');result=json.loads((exp/'result.json').read_text())
    if base.digest(exp/'contacts.npz')!=result['contacts_sha256']:raise ValueError('Contact source changed')
    with np.load(exp/'contacts.npz') as z:data={k:z[k] for k in z.files}
    # Hands own the rein grip; a neck reach changes rein span, not arm length.
    # Keep the admitted19 hand targets instead of pulling elbows straight.
    hand_bits=data['bit_points']
    if newhorse:
        with np.load(base.BASE/'entrance205-export03/contacts.npz') as z:hand_bits=z['bit_points'].copy()
    with np.load(base.BASE/'wardrobe185-horsecache01/contacts.npz') as z:old_s=z['saddle_matrices'];old_b=z['bit_points']
    frames=list(range(361,361+len(data['saddle_matrices'])))
    phases=[source_pose_frame(s) for s in data['source_frame'][::8]]
    rig=bpy.data.objects['MF_body156_fit_rig'];names=[b.name for b in rig.pose.bones];poses=[];before=[];after=[];residuals=[];world=[]
    with render_geometry_paused():
        for f in phases:
            scene.frame_set(int(f),subframe=f%1);bpy.context.view_layer.update()
            poses.append([np.array(rig.pose.bones[n].matrix_basis) for n in names]);before.append([np.array(rig.pose.bones[n].matrix) for n in names]);world.append(np.array(rig.matrix_world))
        rig.animation_data.action.use_fake_user=True;rig.animation_data.action=rig.animation_data.action.copy();rig.animation_data.action.name='205 phase registered real time turn and steep climb'
        for i,f in enumerate(frames):
            scene.frame_set(f)
            for name,p in zip(names,poses[i]):rig.pose.bones[name].matrix_basis=Matrix(p)
            bpy.context.view_layer.update()
            old={n:Matrix(p) for n,p in zip(names,before[i])}
            old_saddle=linear_sample(old_s,phases[i]-217);old_bit=linear_sample(old_b,phases[i]-217)
            ds=Vector(data['saddle_matrices'][i,:3,3]-old_saddle[:3,3]);t=i/24
            pelvis=rig.pose.bones['pelvis'];m=pelvis.matrix.copy();m.translation+=ds*.5;pelvis.matrix=m
            gather=float(smooth((t-.65)/1.0)*(1-.75*smooth((t-2.2)/1.25)))
            g=glance(t)
            for name,deg in (('pelvis',-7),('spine',-5),('chest',-2),('MF185_neck',7),('MF185_head',7)):
                b=rig.pose.bones[name];b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion((1,0,0),math.radians(deg)*gather)@b.rotation_quaternion
            if uphill:
                # Uphill root pitch is not a rider lean. Counter it through
                # the seat/spine/chest before solving the limbs and contacts.
                climb=float(data['grade'][i*8]/.48)
                for name,deg in (('pelvis',5),('spine',10),('chest',8)):
                    b=rig.pose.bones[name];b.rotation_quaternion=Quaternion((1,0,0),math.radians(deg)*climb)@b.rotation_quaternion
            # Local Y is the chain axis used by the admitted204 head glance;
            # share yaw with neck/chest and add down-look, never detach head.
            for name,yaw,pitch in (('chest',8,0),('MF185_neck',18,4),('MF185_head',65,12)):
                b=rig.pose.bones[name];b.rotation_quaternion=b.rotation_quaternion@Quaternion((0,1,0),math.radians(yaw)*g)@Quaternion((1,0,0),math.radians(pitch)*g)
            bpy.context.view_layer.update();row=[]
            for j,side in enumerate(('L','R')):
                foot='foot.'+side;shin='shin.'+side
                row.append(limb(rig,'thigh.'+side,shin,foot,old[foot].translation+ds,old[shin].translation+ds*.5,old[foot]))
                upper='upperarm.'+side;lower='forearm.'+side;hand='hand.'+side
                shoulder=rig.pose.bones[upper].head-old[upper].translation
                db=Vector(hand_bits[i,j]-old_bit[j])
                row.append(limb(rig,upper,lower,hand,old[hand].translation+shoulder+.2*(db-ds),old[lower].translation+shoulder,old[hand]))
                contact(rig,side,1)
            for b in rig.pose.bones:
                loc,rot,scale=b.matrix_basis.decompose();b.location=loc;b.rotation_mode='QUATERNION';b.rotation_quaternion=rot;b.scale=scale
                for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(data_path=prop,frame=f)
            bpy.context.view_layer.update();after.append([np.array(rig.pose.bones[n].matrix) for n in names]);residuals.append(row)
            if i%24==0:print('205 rider',f,flush=True)
    from worker import action_channels
    for fc in action_channels(rig.animation_data.action):
        for k in fc.keyframe_points:
            if k.co.x>=361:k.interpolation='LINEAR'
    for name,sha in result['caches'].items():
        p=exp/(name+'.mdd')
        if base.digest(p)!=sha:raise ValueError('Horse export changed')
        attach_cache(bpy.data.objects['MF185_gait_'+name],p,361)
    np.savez_compressed(out/'rig.npz',names=names,source_frames=phases,before=before,after=after,world=world)
    np.savez_compressed(out/'route.npz',**data)
    scene.frame_start=361;scene.frame_end=frames[-1];scene.frame_set(361)
    save(scene,out,{'source_sha256':OPENING_SHA,'horse_source':result['source_sha256'],
        'uphill_rider_counterpitch_degrees':23 if uphill else 0,
        'max_limb_error_native':float(np.max(residuals)),'face':facial(scene,frames),
        'limits':'COARSE rider and new horse only; garment/groom/tack caches not yet renewed, no visual pass'})


def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'opening04'},{'operation':'rider05'},{'operation':'rider19'},{'operation':'rider30'},{'operation':'rider35'}):raise ValueError('Fixed205 actor operation')
    out=base.BASE/('entrance205-'+job['operation'])
    if out.exists() or base.digest(OPENING)!=OPENING_SHA:raise ValueError('Source/output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(OPENING),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    if job['operation']=='opening04':opening(scene,out)
    else:rider(scene,out,uphill=job['operation'] in ('rider19','rider30','rider35'),newhorse=job['operation'] in ('rider30','rider35'))


if __name__=='__main__':main()
