"""Source-bound rider correction and coordinated material derivative.

All inputs/operations are fixed reviewed repository code. No runtime code or
arbitrary paths. Neutral originals remain immutable; output is shot-scoped.
"""
import json,math,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance200_inspect import SOURCE,SOURCE_SHA,base
from entrance198_terrain import fingerprint

def response_plan(eulers,names):
    e=np.unwrap(np.asarray(eulers,float),axis=0)
    if e.shape!=(144,len(names),3) or not np.isfinite(e).all():raise ValueError('Fixed finite clock required')
    chest=e[:,names.index('chest'),0];neck=e[:,names.index('MF185_neck'),0];head=e[:,names.index('MF185_head'),0]
    drive=chest-chest.mean();x=float(drive[0]);v=0.;response=[];dt=1/96
    for target in drive:
        for _ in range(4):
            v+=(18**2*(target*.9-x)-2*.72*18*v)*dt;x+=v*dt
        response.append(x)
    response=np.array(response);response-=response.mean()
    desired_head=head.mean()+response
    desired_neck=neck.mean()+.43*drive+.57*response
    neck_delta=desired_neck-neck
    head_delta=desired_head-head-neck_delta
    out=np.column_stack((neck_delta,head_delta))
    if abs(out).max()>np.deg2rad(14):raise ValueError('Unbounded head correction')
    return out

def validate(job):
    if job!={'operation':'candidate10'}:raise ValueError('Fixed integrated derivative only')
    out=base.BASE/'entrance200-candidate10'
    if out.exists() or base.digest(SOURCE)!=SOURCE_SHA:raise ValueError('Source/output mismatch')
    r=json.loads((SOURCE.parent/'result.json').read_text())
    for row in r['caches']:
        p=(SOURCE.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache mismatch')
    return out,r

def thumb_pose(rig,side):
    from entrance200_pose_control import contact
    contact(rig,side,1)

def animate(scene,out):
    import bpy
    from mathutils import Matrix,Quaternion
    from wardrobe_motion178_controls import render_geometry_paused
    from entrance189_groom import read_mdd,write_mdd,attach_cache
    rig=bpy.data.objects['MF_body156_fit_rig']
    with np.load(base.BASE/'entrance200-inspect01/rig.npz') as z:
        names=list(z['names']);before=z['matrices'].copy();basis=z['bases'].copy();offsets=response_plan(z['eulers'],names)
    # Keep the original unassigned action for honest pre-save/reopen inventory
    # parity and reusable provenance; Blender otherwise drops zero-user IDs.
    rig.animation_data.action.use_fake_user=True
    rig.animation_data.action=rig.animation_data.action.copy();rig.animation_data.action.name='200 distributed rider absorption and thumb hold'
    changed=['MF185_neck','MF185_head']+[f'MF_fit_finger_4_{j}.{s}' for s in ('L','R') for j in range(3)];after=[]
    with render_geometry_paused():
        for i,f in enumerate(range(217,361)):
            scene.frame_set(f)
            for name in changed:rig.pose.bones[name].matrix_basis=Matrix(basis[i,names.index(name)])
            for name,angle in zip(changed[:2],offsets[i]):
                b=rig.pose.bones[name];b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion((1,0,0),float(angle))@b.rotation_quaternion
            bpy.context.view_layer.update()
            for s in ('L','R'):thumb_pose(rig,s)
            for name in changed:
                b=rig.pose.bones[name];loc,rot,scale=b.matrix_basis.decompose();b.rotation_mode='QUATERNION';b.rotation_quaternion=rot
                b.keyframe_insert(data_path='rotation_quaternion',frame=f)
            bpy.context.view_layer.update();after.append([np.array(rig.matrix_world@b.matrix) for b in rig.pose.bones])
    after=np.array(after);other=[n for n in names if n not in changed]
    residual=max(float(abs(after[:,names.index(n)]-before[:,names.index(n)]).max()) for n in other)
    if residual>2e-5:raise ValueError('Unrelated bone moved')
    shawl=bpy.data.objects['MF185_moving_shawl'];mod=next(m for m in shawl.modifiers if m.type=='MESH_CACHE');src=Path(bpy.path.abspath(mod.filepath))
    a=read_mdd(src);start=int(mod.frame_start);world=np.array(shawl.matrix_world);inv=np.linalg.inv(world);h=names.index('MF185_head')
    def frames():
        for k,row in enumerate(a):
            p=np.array(row,float);i=k+start-217
            if 0<=i<144:
                q=p@world[:3,:3].T+world[:3,3];w=np.clip((q[:,2]-before[i,h,2,3]+1.2)/1.8,0,1);w=w*w*(3-2*w)
                d=after[i,h]@np.linalg.inv(before[i,h]);moved=q@d[:3,:3].T+d[:3,3];q+=(moved-q)*w[:,None];p=q@inv[:3,:3].T+inv[:3,3]
            yield p.astype(np.float32)
    path=out/'shawl.mdd';write_mdd(path,len(a),a.shape[1],frames());attach_cache(shawl,path,start)
    np.savez_compressed(out/'motion.npz',names=names,before=before,after=after,offsets=offsets)
    return {'unchanged_bone_max_error':residual,'local_correction_ranges_degrees':np.rad2deg(np.ptp(offsets,axis=0)).tolist(),'shawl_source_sha256':base.digest(src),'cloth_method':'Bounded headfall transport of simulated cache; renewed visual contact gate required; not resimulation'}

def neck_corrective(body):
    group=body.vertex_groups.new(name='200 riding neck deformation only')
    for v in body.data.vertices:
        x,y,z=v.co
        w=max(0.,1-abs(x)/1.05)*max(0.,1-abs(z+1.55)/.85)
        if w:group.add([v.index],w,'REPLACE')
    m=body.modifiers.new('200 preserve rest neck under riding extension','CORRECTIVE_SMOOTH')
    m.factor=.7;m.iterations=8;m.vertex_group=group.name;m.use_only_smooth=False;m.rest_source='ORCO'
    # Correct rest-relative pose strain before final subdivision. This is not
    # a smoothing sculpt of the approved neutral anatomy.
    body.modifiers.move(len(body.modifiers)-1,next(i for i,m in enumerate(body.modifiers) if m.type=='SUBSURF'))
    from entrance200_pose_control import neck
    import bpy
    neck(body,bpy.data.objects['MF_body156_fit_rig'])

def multiply(mat,scale,label):
    n,l=mat.node_tree.nodes,mat.node_tree.links;bs=next(n for n in n if n.type=='BSDF_PRINCIPLED');socket=bs.inputs['Base Color']
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.label=label;mix.inputs[0].default_value=1;mix.inputs[2].default_value=(*scale,1)
    if socket.is_linked:l.new(socket.links[0].from_socket,mix.inputs[1])
    else:mix.inputs[1].default_value=socket.default_value
    l.new(mix.outputs[0],socket);return bs

def materials(scene):
    import bpy
    rows=[];copies={}
    targets={'MF185_moving_shawl':('shawl',),'MF_studio_adult_body':('skin',),'MF_173_work_boot_L':('boot',),'MF_173_work_boot_R':('boot',)}
    for name,(kind,) in targets.items():
        ob=bpy.data.objects[name]
        for i,old in enumerate(list(ob.data.materials)):
            if old is None or (kind=='skin' and i not in (0,3,4)) or (kind=='boot' and 'boot' not in old.name):continue
            key=(old,kind)
            if key not in copies:
                mat=old.copy();mat.name='200 '+old.name;copies[key]=mat
                if kind=='shawl':
                    bs=mat.node_tree.nodes.get('Principled BSDF');paint=bs.inputs['Base Color'].links[0].from_node
                    if paint.type!='MIX_RGB':raise ValueError('Unexpected cloth input')
                    paint.inputs[0].default_value=.76
                    bs=multiply(mat,(.42,.55,.72),'200 deeper indigo with retained brush marks')
                    bs.inputs['Specular IOR Level'].default_value=.12;bs.inputs['Roughness'].default_value=.9
                    bs.inputs['Sheen Weight'].default_value=.08
                elif kind=='boot':multiply(mat,(.5,.48,.46),'200 worn umber boot masses')
                else:
                    bs=multiply(mat,(.80,.84,.89),'200 preserve authored skin variation and warmer midtones')
                    bs.inputs['Specular IOR Level'].default_value=.12;bs.inputs['Roughness'].default_value=.78
                    bs.inputs['Subsurface Weight'].default_value=.035;bs.inputs['Subsurface Scale'].default_value=.015
                rows.append({'old':old.name,'new':mat.name,'kind':kind})
            ob.data.materials[i]=copies[key]
    return rows

def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());out,r=validate(job);out.mkdir()
    (out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    body=bpy.data.objects['MF_studio_adult_body'];body.data.use_fake_user=True;body.data=body.data.copy()
    original=fingerprint(scene);motion=animate(scene,out);neck_corrective(body);changes=materials(scene)
    scene.frame_set(217);base.check_protected();result_fp=fingerprint(scene);caches=[]
    for o in scene.objects:
        for m in o.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':o.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'native_sha256':base.digest(out/'scene.blend'),'caches':caches,'motion':motion,'materials':changes,'fingerprint':result_fp,'source_fingerprint':original,'visual_gate':'NOT_RUN','neutral_geometry':'Basis and existing shape deltas unchanged; neck-angle-driven smoothing is zero at neutral; evaluated neutral check pending'},indent=2)+'\n')

if __name__=='__main__':main()
