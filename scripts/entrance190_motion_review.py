"""Fresh-open, dependency-bound full route coverage. No automatic visual PASS."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def geography_camera(scene,t=0.):
    import bpy
    from mathutils import Vector
    from bpy_extras.object_utils import world_to_camera_view
    cam=scene.camera;cam.location=(-45,20-15*t,500);target=Vector((-45,-330-15*t,0))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=400
    landmarks=[Vector(p) for p in [(-24,-373,-10),(24,-373,-10),(0,-190,-20),(-140,-330,-12)]]
    for _ in range(12):
        bpy.context.view_layer.update();uv=[world_to_camera_view(scene,cam,p) for p in landmarks]
        if all(.06<q.x<.94 and .06<q.y<.94 and q.z>0 for q in uv):return [list(q) for q in uv]
        cam.data.ortho_scale*=1.05
    raise ValueError('Geographic landmarks do not fit portrait frustum')

def validate(job):
    if job not in ({'operation':'motion22'},{'operation':'geography23'},{'operation':'coverage24'},{'operation':'coverage25'},{'operation':'coverage26'},{'operation':'coverage27'}):raise ValueError('Fixed complete motion operation required')
    folder=base.BASE/'entrance190-ground21';source=folder/'scene.blend';r=json.loads((folder/'result.json').read_text())
    gate=json.loads((folder/'internal-review.json').read_text())
    if base.digest(source)!=r['native_sha256'] or gate.get('source_sha256')!=r['native_sha256'] or gate.get('status')!='PROCEED_TO_COVERAGE':raise ValueError('Missing source-bound overview admission')
    if job['operation'] not in ('coverage24','coverage25','coverage26','coverage27'):
        coverage=json.loads((base.BASE/('entrance190-coverage27' if job['operation']=='geography23' else 'entrance190-coverage25')/'internal-review.json').read_text())
        if coverage.get('source_sha256')!=r['native_sha256'] or coverage.get('status')!='PROCEED_TO_COMPLETE_MOTION':raise ValueError('Missing corrected-framing admission')
    out=base.BASE/('entrance190-'+job['operation'])
    if out.exists():raise ValueError('Preserve evidence')
    return source,out,r


def main():
    import bpy
    from mathutils import Vector
    from entrance189_groom import read_mdd
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());source,out,r=validate(job)
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    expected=json.loads((base.BASE/'entrance190-integration14/result.json').read_text())['caches'];checks=[]
    for row in expected:
        ob=bpy.data.objects[row['object']];mods=[(i,m) for i,m in enumerate(ob.modifiers) if m.type=='MESH_CACHE']
        if len(mods)!=1 or mods[0][0]!=0:raise ValueError('Cache stack changed')
        m=mods[0][1];p=Path(bpy.path.abspath(m.filepath)).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache dependency changed')
        a=read_mdd(p)
        if a.shape[1]!=len(ob.data.vertices) or len(a)!=193 or m.frame_start!=361:raise ValueError('Incomplete maneuver cache')
        checks.append({'object':ob.name,'path':str(p.relative_to(base.BASE)),'sha256':row['sha256'],'frames':len(a)})
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
    cam=scene.camera;rows=[]
    with np.load(base.BASE/'entrance190-rider09/route.npz',allow_pickle=False) as z:route={k:z[k] for k in z.files}
    from entrance190_composition import pose
    def action_camera(f):
        loc,target,_=pose(route,f)
        # Orthographic origins must remain above the ground across the full
        # portrait frustum. Backing along the same axis preserves projection.
        cam.location=loc+(loc-target).normalized()*180
        cam.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=80
    if job['operation'] in ('coverage24','coverage25','coverage26','coverage27'):
        # Confirm a wider crop before committing all frames, and a detached
        # geographic cutaway before its complete moving-camera render.
        cam.data.animation_data_clear();cam.data.ortho_scale=80
        if job['operation']=='coverage25':cam.animation_data_clear()
        for f in (() if job['operation'] in ('coverage26','coverage27') else (361,457,552)):
            scene.frame_set(f)
            if job['operation']=='coverage25':action_camera(f)
            scene.render.filepath=str(out/('frame-%04d.png'%f));bpy.ops.render.render(write_still=True)
        cam.animation_data_clear();scene.frame_set(361)
        landmarks=geography_camera(scene)
        bpy.context.view_layer.update();scene.render.filepath=str(out/'geography.png');bpy.ops.render.render(write_still=True)
        (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'cache_checks':checks,'landmark_projections':landmarks,'visual_gate':'NOT_RUN'},indent=2)+'\n');return
    if job['operation']=='geography23':
        cam.animation_data_clear();cam.data.animation_data_clear();scene.frame_set(361)
        # Native moving geographic cutaway; actor is outside its forward crop.
        # No frozen rider presented as action and no image zoom substituted.
        for i in range(48):
            t=i/47;landmarks=geography_camera(scene,t)
            bpy.context.view_layer.update();scene.render.filepath=str(out/('frame-%04d.png'%i));bpy.ops.render.render(write_still=True)
            rows.append({'frame':i,'source_time':361,'camera':list(cam.location)})
    else:
        cam.animation_data_clear();cam.data.animation_data_clear();cam.data.ortho_scale=80
        for f in range(361,553):
            scene.frame_set(f);action_camera(f);bpy.context.view_layer.update();scene.render.filepath=str(out/('frame-%04d.png'%f));bpy.ops.render.render(write_still=True)
            rows.append({'frame':f,'camera':list(cam.location)})
    native_sha=None
    if job['operation']=='motion22':
        for f in range(361,553):
            action_camera(f)
            cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)
        scene.frame_start=361;scene.frame_end=552;scene.frame_set(361)
        for ob in scene.objects:
            for m in ob.modifiers:
                if m.type=='MESH_CACHE':m.filepath=bpy.path.abspath(m.filepath)
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
        native_sha=base.digest(out/'scene.blend')
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'native_sha256':native_sha,'cache_checks':checks,'frames':rows,'fps':24,'protected_originals_exact':True,'visual_gate':'NOT_RUN','scope':'Full preview-resolution native coverage; not final-release qualification'},indent=2)+'\n')

if __name__=='__main__':main()
