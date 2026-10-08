"""Production camera: perspective follow, gathering arc, and receding uphill exit."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance190_scene import path_sample

def camera(route,t):
    p=path_sample(route,t)*8.3+np.array([0,.2,-20.931])
    blend=np.clip((t-2)/4,0,1);blend=blend*blend*(3-2*blend)
    dt=max(0,t-6);follow=6+dt-dt**3/4+dt**4/16 if t>6 else t
    origin=path_sample(route,follow)*8.3+np.array([0,.2,-20.931])
    rise=np.clip(dt/2,0,1);rise=rise*rise*(3-2*rise)
    loc=origin+[48-23*blend,18+48*blend,55+10*blend+60*rise]
    return loc,p+[0,0,12]

def project(points,loc,target):
    forward=target-loc;forward/=np.linalg.norm(forward)
    right=np.cross(forward,[0,0,1.]);right/=np.linalg.norm(right);up=np.cross(right,forward)
    q=points-loc;depth=q@forward
    return np.column_stack((.5+(q@right)/(2*depth*(18/32)*(9/16)),.5+(q@up)/(2*depth*(18/32)),depth))

def main():
    import bpy
    from mathutils import Vector
    from entrance190_contacts import world_transform
    from entrance189_groom import read_mdd
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'perspective29'},{'operation':'motion30'},{'operation':'reopen31'}):raise ValueError('Fixed perspective operation required')
    stage='entrance190-ground21' if job['operation']=='perspective29' else 'entrance190-perspective29'
    source=base.BASE/stage/'scene.blend';out=base.BASE/('entrance190-'+job['operation']);r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Unbound source')
    if job['operation']!='perspective29':
        gate=json.loads((source.parent/'internal-review.json').read_text())
        allowed=('PROCEED_TO_REOPEN','PROCEED_TO_COMPLETE_MOTION') if job['operation']=='reopen31' else ('PROCEED_TO_COMPLETE_MOTION',)
        if gate.get('status') not in allowed or gate.get('source_sha256')!=r['native_sha256']:raise ValueError('Perspective review missing')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    with np.load(base.BASE/'entrance190-rider09/route.npz',allow_pickle=False) as z:route={k:z[k] for k in z.files}
    prior=json.loads((base.BASE/'entrance190-integration14/result.json').read_text());checks=[]
    for row in prior['caches']:
        ob=bpy.data.objects[row['object']];mods=[(i,m) for i,m in enumerate(ob.modifiers) if m.type=='MESH_CACHE']
        if len(mods)!=1 or mods[0][0]!=0:raise ValueError('Cache stack changed')
        m=mods[0][1];p=Path(bpy.path.abspath(m.filepath)).resolve()
        if base.digest(p)!=row['sha256'] or not p.is_relative_to(base.BASE.resolve()) or m.frame_start!=361:raise ValueError('Cache changed')
        checks.append({'object':ob.name,'path':str(p.relative_to(base.BASE)),'sha256':row['sha256']})
    cam=scene.camera;camera_rows=[]
    if job['operation']=='perspective29':
        cam.animation_data_clear();cam.data.animation_data_clear();cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=36;cam.data.lens=32;cam.data.clip_start=.1;cam.data.clip_end=12000
        # Conservative complete actor bounds; project actual cached horse and
        # groom extrema plus the retained rider domain, not a center-only fit.
        horse=read_mdd(base.BASE/'entrance190-route-export08/horse.mdd')
        mane=read_mdd(base.BASE/'entrance190-integration14/mane.mdd');tail=read_mdd(base.BASE/'entrance190-integration14/tail.mdd')
        bounds=[]
        for i in range(193):
            a=np.vstack((horse[i]+[0,0,-1.05],mane[i],tail[i],np.array([[-5,-6,-16],[5,7,4]])))
            lo=a.min(0);hi=a.max(0);box=np.array([[x,y,z] for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])])
            m=np.array(world_transform(route,361+i));bounds.append(box@m[:3,:3].T+m[:3,3])
        factor=1.
        for _ in range(30):
            ok=True
            for i,box in enumerate(bounds):
                loc,target=camera(route,i/24);loc=target+(loc-target)*factor;uv=project(box,loc,target)
                if np.any(uv[:,:2]<.07) or np.any(uv[:,:2]>.93) or np.any(uv[:,2]<=0):ok=False;break
            if ok:break
            factor*=1.04
        else:raise ValueError('Whole actor does not fit perspective route')
        for i in range(193):
            loc,target=camera(route,i/24);loc=target+(loc-target)*factor
            cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
            cam.keyframe_insert(data_path='location',frame=361+i);cam.keyframe_insert(data_path='rotation_euler',frame=361+i)
            camera_rows.append({'frame':361+i,'location':loc.tolist(),'target':target.tolist(),'fit_factor':factor,'actor_uv':project(bounds[i],loc,target).tolist()})
        (out/'camera.json').write_text(json.dumps(camera_rows,indent=2)+'\n')
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True;scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
    frames=range(361,553) if job['operation']=='motion30' else (361,385,409,433,457,481,505,529,552) if job['operation']=='perspective29' else (361,457,552)
    rows=[]
    for f in frames:
        scene.frame_set(f);bpy.context.view_layer.update();scene.render.filepath=str(out/('frame-%04d.png'%f))
        reused=False
        if job['operation']=='motion30' and f in (361,385,409,433,457,481,505,529,552):
            import shutil
            parity=json.loads((base.BASE/'entrance190-reopen31/pixel-comparison.json').read_text())
            if parity.get('status')!='PASS' or parity.get('native_sha256')!=r['native_sha256']:raise ValueError('Overview reuse needs actual reopen parity')
            shutil.copy2(source.parent/('frame-%04d.png'%f),scene.render.filepath);reused=True
        else:bpy.ops.render.render(write_still=True)
        rows.append({'frame':f,'camera':list(cam.matrix_world.translation),'reused_from_overview':reused})
    native_sha=None
    if job['operation']=='perspective29':
        scene.frame_start=361;scene.frame_end=552;scene.frame_set(361)
        for ob in scene.objects:
            for m in ob.modifiers:
                if m.type=='MESH_CACHE':m.filepath=bpy.path.abspath(m.filepath)
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);native_sha=base.digest(out/'scene.blend')
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'native_sha256':native_sha,'cache_checks':checks,'frames':rows,'fps':24,'visual_gate':'NOT_RUN','scope':'Perspective route coverage with unchanged integrated performance'},indent=2)+'\n')

if __name__=='__main__':main()
