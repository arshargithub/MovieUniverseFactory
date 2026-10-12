"""Closed source-bound hand/rein diagnostics and reversible shot correction."""
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe_motion178 as base

SOURCES = {
    'opening': ('entrance209-opening03', '0c29e23175dacccdbcbd84e50b94ad279f2b87c0f152bee4d85516148502d204'),
    'route': ('entrance209-route04', '411c1b9916dc4ccd508becb7e95622ea0e42d3367200f359279dec9c29d4deee'),
}
OPS = {'inspect01': 'opening', 'inspect02':'opening','candidate03':'opening','candidate04':'opening',
       'candidate05':'opening','opening06':'opening','route07':'route','opening08':'opening',
       'opening14':'opening','route15':'route','candidate20':'opening'}

def thumb(rig, side, target_local=None):
    import bpy
    from mathutils import Vector
    from entrance200_pose_control import aim
    sign=1 if side=='L' else -1
    hand=rig.pose.bones['hand.'+side]
    chain=[rig.pose.bones[f'MF_fit_finger_4_{j}.{side}'] for j in range(3)]
    # Matrix aiming can leave float32 decomposition residue in location/scale.
    # This is a rotation-only correction: retain the source channels explicitly.
    original=[(b.location.copy(),b.scale.copy()) for b in chain]
    origin=chain[0].head.copy();target=hand.matrix@Vector(target_local if target_local is not None else (sign*.075,.665,-.355))
    lengths=[b.bone.length for b in chain];a=lengths[0];b=sum(lengths[1:])
    delta=target-origin;d=delta.length
    if not abs(a-b)+.001<d<a+b-.001:raise ValueError('Unreachable thumb target')
    # MCP must bow toward the anatomical thumb side, not across the palm and
    # back toward the target. The previous negative-X elbow was hyperextended.
    axis=delta.normalized();bend=hand.matrix.to_3x3()@Vector((sign,0.,-.1))
    bend-=axis*bend.dot(axis);bend.normalize()
    c=(a*a+d*d-b*b)/(2*a*d)
    joint=origin+axis*(a*c)+bend*(a*np.sqrt(1-c*c))
    aim(chain[0],joint);bpy.context.view_layer.update()
    aim(chain[1],target);bpy.context.view_layer.update()
    aim(chain[2],target);bpy.context.view_layer.update()
    for bone,(location,scale) in zip(chain,original):
        q=bone.matrix_basis.to_quaternion().normalized()
        bone.rotation_mode='QUATERNION';bone.rotation_quaternion=q
        bone.location=location;bone.scale=scale
    bpy.context.view_layer.update()

def return_path(start, tangent, middle):
    """Cubic supported loose return; endpoints and tangent are explicit."""
    start=np.asarray(start,float);middle=np.asarray(middle,float)
    tangent=np.asarray(tangent,float)
    if any(v.shape!=(3,) or not np.isfinite(v).all() for v in (start,tangent,middle)) or np.linalg.norm(tangent)<1e-8:
        raise ValueError('Finite nonzero rein exit required')
    tangent=tangent/np.linalg.norm(tangent)
    a=start+tangent*1.0;b=middle+np.array([0.,0.,.5])
    return np.array([(1-t)**3*start+3*(1-t)**2*t*a+3*(1-t)*t*t*b+t**3*middle for t in np.linspace(0,1,18)])

def rein_shape(old, channel, matrix, side):
    from mathutils import Vector
    points=np.array(list(old[:17])+list(channel[1:]))
    sign=1 if side=='L' else -1
    end=points[-1]+np.array(matrix.to_3x3()@Vector((sign*.75,1.0,-1.0)))
    return np.vstack((points,return_path(points[-1],points[-1]-points[-2],end)[1:]))

def leather_profile(scene):
    import bpy
    name='MF214 narrow leather cross section'
    if name in bpy.data.objects:return bpy.data.objects[name]
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='2D';sp=data.splines.new('POLY');sp.points.add(11)
    for i,p in enumerate(sp.points):
        a=2*np.pi*i/12;p.co=(.034*np.cos(a),.009*np.sin(a),0.,1.)
    sp.use_cyclic_u=True
    ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.hide_render=True;ob.hide_viewport=True
    return ob

def reins(scene):
    import bpy
    from mathutils import Vector
    rig=bpy.data.objects['MF_body156_fit_rig'];exits={};channels={};old={}
    from wardrobe185_grip import rein_channel
    for side in ('L','R'):
        ob=bpy.data.objects['MF185_rein_'+side];old[side]=[ob.matrix_world@p.co.to_3d() for p in ob.data.splines[0].points]
        channels[side]=rein_channel(rig,side);exits[side]=np.array(channels[side][-1])
    for side in ('L','R'):
        ob=bpy.data.objects['MF185_rein_'+side];ob.data=ob.data.copy();ob.data.animation_data_clear()
        points=rein_shape(old[side],channels[side],rig.matrix_world,side)
        ob.data.splines.clear();sp=ob.data.splines.new('POLY');sp.points.add(len(points)-1)
        inv=ob.matrix_world.inverted()
        for p,co in zip(sp.points,points):p.co=(*(inv@Vector(co)),1)

def build(scene,out,kind,pose_fn=thumb,changed_digits=(4,),additions=None):
    import bpy
    from mathutils import Vector
    from wardrobe_motion178_controls import render_geometry_paused
    from wardrobe185_grip import rein_channel
    from entrance198_terrain import fingerprint
    from entrance205_actor import save
    from worker import action_channels
    rig=bpy.data.objects['MF_body156_fit_rig'];original_frame=scene.frame_current;before=fingerprint(scene)
    changed=[f'MF_fit_finger_{d}_{j}.{s}' for s in ('L','R') for d in changed_digits for j in range(3)]
    preserved=[b.name for b in rig.pose.bones if b.name not in changed]
    frames=list(range(217,361)) if kind=='opening' else list(range(361,649))
    old=[];world=[];poses=[];cameras=[];lenses=[]
    with render_geometry_paused():
        for side in ('L','R'):bpy.data.objects['MF185_rein_'+side].hide_viewport=False
        for f in frames:
            scene.frame_set(f);bpy.context.view_layer.update()
            old.append([[list(ob.matrix_world@p.co.to_3d()) for p in ob.data.splines[0].points]
                        for ob in [bpy.data.objects['MF185_rein_'+s] for s in ('L','R')]])
            world.append(np.array(rig.matrix_world));poses.append([np.array(rig.matrix_world@rig.pose.bones[n].matrix) for n in preserved])
            cameras.append(np.array(scene.camera.matrix_world));lenses.append(scene.camera.data.lens)
    old=np.array(old);poses=np.array(poses);cameras=np.array(cameras)
    rig.animation_data.action.use_fake_user=True
    rig.animation_data.action=rig.animation_data.action.copy();rig.animation_data.action.name='MF214 thumb contact '+kind
    for fc in action_channels(rig.animation_data.action):
        if any(fc.data_path.startswith('pose.bones["'+n+'"]') for n in changed):fc.keyframe_points.clear()
    for side in ('L','R'):
        ob=bpy.data.objects['MF185_rein_'+side];ob.data.use_fake_user=True
        if ob.data.animation_data and ob.data.animation_data.action:ob.data.animation_data.action.use_fake_user=True
        ob.data=ob.data.copy();ob.data.name='MF214 split rein '+kind+' '+side;ob.data.animation_data_clear()
        ob.data.bevel_mode='OBJECT';ob.data.bevel_object=leather_profile(scene);ob.data.use_fill_caps=True
        ob.data.splines.clear();sp=ob.data.splines.new('POLY');sp.points.add(36)
    after=[];reins_after=[];thumb_bases=[];camera_error=0.
    with render_geometry_paused():
        for side in ('L','R'):bpy.data.objects['MF185_rein_'+side].hide_viewport=False
        for i,f in enumerate(frames):
            scene.frame_set(f);bpy.context.view_layer.update()
            for side in ('L','R'):pose_fn(rig,side)
            for n in changed:
                b=rig.pose.bones[n];q=b.matrix_basis.to_quaternion();b.rotation_mode='QUATERNION';b.rotation_quaternion=q
                b.keyframe_insert('rotation_quaternion',frame=f)
            bpy.context.view_layer.update();row=[]
            for j,side in enumerate(('L','R')):
                ob=bpy.data.objects['MF185_rein_'+side]
                points=rein_shape(old[i,j],rein_channel(rig,side),rig.matrix_world,side);row.append(points)
                inv=ob.matrix_world.inverted()
                if len(points)!=len(ob.data.splines[0].points):raise ValueError('Rein topology')
                for p,co in zip(ob.data.splines[0].points,points):p.co=(*(inv@Vector(co)),1);p.keyframe_insert('co',frame=f)
            # Reopen compares the actual stored float32 curve, not an ideal
            # float64 construction path hundreds of scene units from origin.
            reins_after.append([[list(ob.matrix_world@p.co.to_3d()) for p in ob.data.splines[0].points]
                                 for ob in [bpy.data.objects['MF185_rein_'+s] for s in ('L','R')]])
            thumb_bases.append([np.array(rig.pose.bones[n].matrix_basis) for n in changed])
            after.append([np.array(rig.matrix_world@rig.pose.bones[n].matrix) for n in preserved])
            camera_error=max(camera_error,float(abs(np.array(scene.camera.matrix_world)-cameras[i]).max()),abs(scene.camera.data.lens-lenses[i]))
            if i%48==0:print('214 contact keyed',f,flush=True)
    error=float(abs(np.array(after)-poses).max())
    if error>2e-5 or camera_error>2e-5:raise ValueError('Protected performance changed')
    scene.frame_set(original_frame);bpy.context.view_layer.update();after_fp=fingerprint(scene)
    if before['geometry']!=after_fp['geometry'] or before['camera_light']!=after_fp['camera_light']:
        raise ValueError('Protected geometry or camera/light changed')
    np.savez_compressed(out/'contact.npz',frames=frames,names=preserved,before=poses,after=after,old_reins=old,
                        reins=reins_after,thumb_names=changed,thumb_bases=thumb_bases,cameras=cameras,lenses=lenses)
    if additions:additions(scene)
    final_geometry=fingerprint(scene)['geometry']
    scene.frame_set(360 if kind=='opening' else 427)
    save(scene,out,dict(source_sha256=SOURCES[kind][1],nonthumb_world_max_error=error,camera_max_error=camera_error,
                       protected_geometry_sha256=final_geometry,source_geometry_sha256=before['geometry'],contact_sha256=base.digest(out/'contact.npz'),
                       scope='Declared finger rotations and split reins; optional fitted glove derivative. All other rig motion and original mesh/shape geometry retained',
                       limits='Authored scoped contact, not general equestrian physics; visual review pending'))

def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPS:
        raise ValueError('Closed214 operation required')
    return OPS[job['operation']]

def load(kind):
    import bpy
    folder, sha = SOURCES[kind]
    src = base.BASE / folder
    if base.digest(src / 'scene.blend') != sha:
        raise ValueError('Changed native source')
    record = json.loads((src / 'result.json').read_text())
    for row in record['caches']:
        path = (src / row['path']).resolve()
        if not path.is_relative_to(base.BASE.resolve()) or base.digest(path) != row['sha256']:
            raise ValueError('Changed cache source')
    bpy.ops.wm.open_mainfile(filepath=str(src / 'scene.blend'), load_ui=False, use_scripts=False)
    base.check_protected()
    return bpy.context.scene

def hand_data(scene, out):
    import bpy
    rig = bpy.data.objects['MF_body156_fit_rig']
    body = bpy.data.objects['MF_studio_adult_body']
    rows = {}
    for s in ('L','R'):
        inv = rig.pose.bones['hand.'+s].matrix.inverted()
        bones = {b.name: {'head':list(inv@b.head),'tail':list(inv@b.tail),
                         'basis':np.array(b.matrix_basis).tolist()}
                 for b in rig.pose.bones if b.name.endswith('.'+s) and ('finger' in b.name or b.name.startswith('hand'))}
        ob = bpy.data.objects['MF185_rein_'+s]
        rows[s] = {'bones':bones,'rein':[(inv@rig.matrix_world.inverted()@ob.matrix_world@p.co.to_3d())[:] for p in ob.data.splines[0].points],
                   'radius':ob.data.bevel_depth,'hand_world':np.array(rig.matrix_world@rig.pose.bones['hand.'+s].matrix).tolist()}
    (out/'hands.json').write_text(json.dumps(rows,indent=2)+'\n')
    ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
    np.savez_compressed(out/'body.npz',vertices=np.array([ev.matrix_world@v.co for v in m.vertices]),
                        triangles=np.array([t.vertices[:] for t in m.loop_triangles]))
    ev.to_mesh_clear()

def controls(scene, out):
    import bpy
    from mathutils import Vector
    rig=bpy.data.objects['MF_body156_fit_rig'];cam=scene.camera
    cam.animation_data_clear();cam.data.animation_data_clear();cam.parent=None;cam.constraints.clear();cam.rotation_mode='XYZ';cam.data.type='PERSP';cam.data.lens=55
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12
    scene.render.use_persistent_data=False;scene.render.threads_mode='FIXED';scene.render.threads=8
    scene.render.resolution_x=560;scene.render.resolution_y=560;scene.render.resolution_percentage=100
    for side,sign in (('L',1),('R',-1)):
        target=rig.matrix_world@rig.pose.bones['hand.'+side].head.lerp(rig.pose.bones['hand.'+side].tail,.6)
        for label,delta in [('outside',(sign*2.8,-3.5,1.5)),('palm',(-sign*2.0,-3.,-.4))]:
            cam.location=target+Vector(delta);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
            hidden=[]
            if label=='palm':
                for ob in scene.objects:
                    if ob.type in ('MESH','CURVE','CURVES') and ob.name not in ('MF_studio_adult_body','MF185_rein_L','MF185_rein_R','MF217 fitted leather gloves'):
                        hidden.append((ob,ob.hide_render));ob.hide_render=True
                data=bpy.data.lights.new('214 diagnostic fill','AREA');data.energy=180;data.size=3
                fill=bpy.data.objects.new('214 diagnostic fill',data);scene.collection.objects.link(fill)
                fill.location=cam.location;fill.rotation_euler=cam.rotation_euler
            scene.render.filepath=str(out/f'{side}-{label}.png');bpy.ops.render.render(write_still=True)
            for ob,value in hidden:ob.hide_render=value
            if label=='palm':bpy.data.objects.remove(fill,do_unlink=True);bpy.data.lights.remove(data)

def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());kind=validate(job)
    out=base.BASE/('entrance214-'+job['operation'])
    if out.exists():raise ValueError('Preserve previous output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    scene=load(kind)
    building=job['operation'] in ('opening06','route07','opening08','opening14','route15')
    if building:build(scene,out,kind)
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.frame_set(360 if kind=='opening' else 427);bpy.context.view_layer.update()
    if job['operation'].startswith('candidate'):
        rig=bpy.data.objects['MF_body156_fit_rig'];rig.animation_data.action=None
        for side in ('L','R'):thumb(rig,side)
        reins(scene)
    hand_data(scene,out)
    if building:
        scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
        scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
        for f in ((277,330,360) if kind=='opening' else (390,427,472,550,620)):
            scene.frame_set(f);scene.render.filepath=str(out/f'actual-{f}.png');bpy.ops.render.render(write_still=True)
        scene.frame_set(360 if kind=='opening' else 427)
    controls(scene,out)
    base.check_protected()
    if not building:(out/'result.json').write_text(json.dumps({'source_sha256':SOURCES[kind][1], 'native_modified':False,'visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
