"""Fixed coordinated wardrobe diagnostic; not certified trailer gallop.

Build a small rig/contact library so native cloth need not evaluate the full
protected groom and character during every solver substep.
"""
import json
from pathlib import Path
import numpy as np

SCALE=.12292759120464325
PROXY_SHA='566257ec73b43170c6ad5414b8936ef537b7373b2d57de967286f13e3f091029'


def schedule(frame):
    from wardrobe_motion178_controls import phase,smooth
    p=phase(frame-72,neutral_entry=True)
    p['legs']=smooth((frame-97)/48)
    return p


def animate(rig):
    import bpy
    from mathutils import Matrix,Quaternion,Vector
    from wardrobe_riding_fit import riding_pose
    from wardrobe_refinement import neutral
    from wardrobe_motion178_controls import render_geometry_paused
    with render_geometry_paused():
        rig.animation_data_clear();riding_pose(rig,1.)
        goals={b.name:b.matrix_basis.decompose() for b in rig.pose.bones}
        neutral(rig);identity=Quaternion((1,0,0,0))
        for frame in list(range(1,361,4))+[360]:
            bpy.context.scene.frame_set(frame);p=schedule(frame)
            for bone in rig.pose.bones:
                t=p['legs'] if bone.name.startswith(('thigh.','shin.','foot.','toe.')) else p['lean']
                loc,rot,scale=goals[bone.name]
                bone.rotation_mode='QUATERNION';bone.location=loc*t
                bone.rotation_quaternion=identity.slerp(rot,t)
                bone.scale=Vector((1,1,1)).lerp(scale,t)
                if bone.name=='pelvis':bone.location.z+=p['bob']
                if bone.name=='chest':bone.rotation_quaternion=Quaternion((0,0,1),p['chest_yaw'])@bone.rotation_quaternion
                for prop in ('location','rotation_quaternion','scale'):bone.keyframe_insert(data_path=prop,frame=frame)
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        for bone in rig.pose.bones:
            if max(abs(bone.matrix_basis[i][j]-Matrix.Identity(4)[i][j]) for i in range(4) for j in range(4))>1e-5:
                raise ValueError('Motion does not start at admitted rest')


def prep(out):
    import bpy
    from mathutils import Matrix
    import wardrobe_motion178 as base
    import wardrobe_motion178_controls as controls
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    path=base.BASE/'wardrobe185-proxy03/proxy.npz'
    if base.digest(path)!=PROXY_SHA:raise ValueError('Contact changed')
    with np.load(path,allow_pickle=False) as d:p=d['points'];f=d['faces']
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();rig,_,_=base.clean_foundation()
    sample=controls.body_weight_sampler()
    animate(rig)
    canonical=controls.canonical_rig(rig,SCALE)
    mesh=bpy.data.meshes.new('185 motion contact');mesh.from_pydata((p*SCALE).tolist(),[],f.tolist());mesh.update()
    contact=bpy.data.objects.new('MF178_support_185_contact',mesh);bpy.context.scene.collection.objects.link(contact)
    def weights(point):
        if point.z>-.8 or (point.z>-2.3 and point.y>.8 and abs(point.x)<1.6):return {'chest':1.}
        return sample(point)
    controls.bind(contact,canonical,weights,scale=SCALE)
    audit={};samples=[]
    with controls.render_geometry_paused():
        for frame in (1,169,193,217,289,360):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
            ev=contact.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
            q=np.array([v.co[:] for v in m.vertices])/SCALE;ev.to_mesh_clear()
            if q.shape!=p.shape or not np.isfinite(q).all():raise ValueError('Invalid posed contact')
            if frame==1 and np.max(abs(q-p))>1e-5:raise ValueError('Initial collider differs from admitted geometry')
            expected=Matrix.Scale(SCALE,4)@rig.matrix_world@rig.pose.bones['chest'].matrix
            actual=canonical.matrix_world@canonical.pose.bones['chest'].matrix
            error=max(abs(expected[i][j]-actual[i][j]) for i in range(4) for j in range(4))
            if error>1e-5:raise ValueError('Canonical rig motion mismatch')
            audit[frame]={'canonical_chest_error':error,'max_contact_displacement_m':float(np.linalg.norm(q-p,axis=1).max()*SCALE)}
            samples.append(q)
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        bpy.data.libraries.write(str(out/'motion-rig.blend'),{canonical,contact},fake_user=True,compress=True)
    base.check_protected()
    np.savez_compressed(out/'contact-poses.npz',frames=np.array(samples),frame_ids=[1,169,193,217,289,360],faces=f)
    (out/'result.json').write_text(json.dumps({'protected_local_data_exact':True,'audit':audit,'visual_gate':'NOT_RUN','actual_gallop':'NOT_RUN','scope':'Coordinated diagnostic rig/contact library; no cloth solve or acceptance','native_sha256':base.digest(out/'motion-rig.blend')},indent=2)+'\n')


def simulate(out):
    from wardrobe185_cut_solve import run
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    run(out,motion=True)
