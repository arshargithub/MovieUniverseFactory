"""Source-bound gathered rider continuation; coarse contacts before cloth.

Retains the accepted/repaired rig rather than reconstructing its old arm pose.
Not a cloth, groom, geography or final performance qualification.
"""
import json
import math
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance190_actor import SOURCE_SHA


def source_pose_frame(source_frame):
    # Source gait period, not an arbitrary 144-frame looping seam. Use late
    # attention poses, retaining the new actor's existing quaternion motion.
    return 360-((143-float(source_frame))%(24/2.2))


def gathered(time):
    from wardrobe_motion178_controls import smooth
    return smooth(time/2)*(1-.65*smooth((time-5)/2.5))


def build(out):
    import bpy
    from mathutils import Matrix,Quaternion,Vector
    from wardrobe185_riding import limb
    from wardrobe_motion178_controls import render_geometry_paused
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    export=base.BASE/'entrance190-route-export08'
    result=json.loads((export/'result.json').read_text())
    if base.digest(export/'contacts.npz')!=result['contacts_sha256']:raise ValueError('Changed contacts')
    with np.load(export/'contacts.npz',allow_pickle=False) as z:data={k:z[k] for k in z.files}
    with np.load(base.BASE/'wardrobe185-horsecache01/contacts.npz',allow_pickle=False) as z:old_s=z['saddle_matrices'];old_b=z['bit_points']
    names=[b.name for b in rig.pose.bones];poses=[];matrices=[];oldcontacts=[]
    with render_geometry_paused():
        for sf in data['source_frame'][::8]:
            f=source_pose_frame(sf);scene.frame_set(int(f),subframe=f%1);bpy.context.view_layer.update()
            poses.append([np.array(rig.pose.bones[n].matrix_basis) for n in names])
            matrices.append([np.array(rig.pose.bones[n].matrix) for n in names])
            x=f-217;i=int(x);u=x-i
            oldcontacts.append(((1-u)*old_s[i]+u*old_s[min(i+1,143)],(1-u)*old_b[i]+u*old_b[min(i+1,143)]))
        original=rig.animation_data.action
        # Preserve the full neutral-to-riding prefix for subsequent continuous
        # cloth initialization; make an independent action before extending.
        rig.animation_data.action=original.copy();rig.animation_data.action.name='190 gathered continuation'
        records=[]
        for f in range(193):
            frame=361+f;scene.frame_set(frame)
            for n,p in zip(names,poses[f]):rig.pose.bones[n].matrix_basis=Matrix(p)
            bpy.context.view_layer.update()
            before={n:Matrix(p) for n,p in zip(names,matrices[f])}
            ds=Vector(data['saddle_matrices'][f,:3,3]-oldcontacts[f][0][:3,3])
            pelvis=rig.pose.bones['pelvis'];m=pelvis.matrix.copy();m.translation+=ds*.5;pelvis.matrix=m
            g=gathered(f/24)
            for name,angle in (('pelvis',-7),('spine',-5),('chest',-2),('MF185_neck',7),('MF185_head',7)):
                b=rig.pose.bones[name];b.rotation_mode='QUATERNION'
                b.rotation_quaternion=Quaternion((1,0,0),math.radians(angle)*g)@b.rotation_quaternion
            bpy.context.view_layer.update();row={'frame':frame,'gather':g,'residuals':{}}
            for j,side in enumerate(('L','R')):
                foot='foot.'+side;shin='shin.'+side
                target=before[foot].translation+ds;pole=before[shin].translation+ds*.5
                row['residuals']['leg.'+side]=limb(rig,'thigh.'+side,shin,foot,target,pole,before[foot])
                upper='upperarm.'+side;lower='forearm.'+side;hand='hand.'+side
                shoulder_delta=rig.pose.bones[upper].head-before[upper].translation
                db=Vector(data['bit_points'][f,j]-oldcontacts[f][1][j])
                target=before[hand].translation+shoulder_delta+.2*(db-ds)
                pole=before[lower].translation+shoulder_delta
                row['residuals']['arm.'+side]=limb(rig,upper,lower,hand,target,pole,before[hand])
            for bone in rig.pose.bones:
                loc,rot,scale=bone.matrix_basis.decompose();bone.rotation_mode='QUATERNION'
                bone.location=loc;bone.rotation_quaternion=rot;bone.scale=scale
                for prop in ('location','rotation_quaternion','scale'):bone.keyframe_insert(data_path=prop,frame=frame)
            records.append(row)
        for slot in rig.animation_data.action.slots:
            for layer in rig.animation_data.action.layers:
                for strip in layer.strips:
                    bag=strip.channelbag(slot)
                    if bag:
                        for curve in bag.fcurves:
                            for k in curve.keyframe_points:
                                if k.co.x>=360:k.interpolation='LINEAR'
    for name,sha in result['caches'].items():
        path=export/(name+'.mdd')
        if base.digest(path)!=sha:raise ValueError('Changed horse cache')
        ob=bpy.data.objects['MF185_gait_'+name]
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':m.filepath=str(path);m.frame_start=361
    dependencies=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':m.filepath=bpy.path.abspath(m.filepath)
            if m.type=='SURFACE_DEFORM':dependencies.append({'object':ob.name,'target':m.target.name if m.target else None,'bound':m.is_bound})
    (out/'contacts.json').write_text(json.dumps({'records':records,'surface_dependencies':dependencies,'visual_gate':'NOT_RUN'},indent=2)+'\n')
    np.savez_compressed(out/'route.npz',**data)
    return records


def main():
    import bpy
    from wardrobe_riding_fit import fit_render
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'rider09'}:raise ValueError('Fixed rider operation required')
    source=base.BASE/'entrance190-blink03/scene.blend';out=base.BASE/'entrance190-rider09'
    if out.exists() or source.is_symlink() or base.digest(source)!=SOURCE_SHA:raise ValueError('Changed source or prior output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);base.check_protected()
    records=build(out);scene=bpy.context.scene
    # Diagnostic isolates real anatomy and contact. Old cloth caches must not
    # masquerade as a fit for the new maneuver; regenerate after this gate.
    visible={o.name:not o.hide_render for o in scene.objects}
    selected=[]
    for o in scene.objects:
        keep=(o.name=='MF_studio_adult_body' or o.name.startswith(('MF185_gait_','MF_aimable_eye_','MF_natural147_','MF_natural148_','MF_natural149_','MF_natural150_','MF_natural151_','MF_natural152_')))
        if o.type not in ('LIGHT','CAMERA'):o.hide_render=not(keep and visible[o.name])
        if o.name=='MF185_gait_Full Bushy Flowing Horse Tail':o.hide_render=True
        if not o.hide_render:selected.append(o.name)
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    scene.world.color=(.18,.18,.18)
    for f in (361,385,409,433,457,481,505,529,553):
        scene.frame_set(f);bpy.context.view_layer.update()
        for angle,label in ((90,'side'),(35,'quarter')):fit_render(out,label+'-'+str(f),angle,(0,-1.8,-8),32.,(800,650))
    for f in (409,457,505):
        scene.frame_set(f);bpy.context.view_layer.update()
        for angle,label in ((0,'front-body'),(270,'other-body')):fit_render(out,label+'-'+str(f),angle,(0,-2,-5),18.,(720,720))
    # Save original full visibility but mark all old caches unqualified.
    for o in scene.objects:o.hide_render=not visible[o.name]
    scene.frame_start=361;scene.frame_end=553;scene.frame_set(409)
    scene['MF190_status']='COARSE RIDER ONLY; old cloth/groom/effects NOT_RUN'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'rider.blend'),compress=True)
    bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'rider.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'native_sha256':base.digest(out/'rider.blend'),
        'max_limb_residual_native':max(v for r in records for v in r['residuals'].values()),'diagnostic_visible':selected,'visual_gate':'NOT_RUN'},indent=2)+'\n')


if __name__=='__main__':main()
